#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "serpapi>=0.1.5",
#     "ddgs>=7.0.0",
#     "pillow>=10.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Search the web for images and download them, with optional Typst output.

Usage:
    uv run image_search.py "golden gate bridge" --typst
    uv run image_search.py --logo "stripe.com" --typst
    uv run image_search.py --stock "office meeting" --typst
    uv run image_search.py --url "https://example.com/img.png" "example" --typst
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len].rstrip("-")


def auto_filename(query: str, output_dir: str, ext: str = ".png") -> str:
    """Generate timestamped filename from query."""
    date = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(query)
    return str(Path(output_dir) / f"{date}-{slug}{ext}")


def format_size(path: str) -> str:
    size = Path(path).stat().st_size
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / 1024:.0f} KB"


def resolve_domain(company_name: str) -> str:
    """Map a company name to its domain for logo lookup.

    TODO: Implement your preferred resolution strategy.

    Approaches to consider:
    - Simple heuristic: lowercase, strip spaces/punctuation, append .com
      e.g. "Goldman Sachs" -> "goldmansachs.com"
    - Web search: use SerpAPI to find the company's actual domain
      (more accurate but uses API quota)
    - Hybrid: heuristic first, search fallback if logo fetch fails

    Args:
        company_name: Company name like "Goldman Sachs" or "JPMorgan Chase"

    Returns:
        Domain string like "goldmansachs.com"
    """
    # Simple heuristic — replace with your preferred approach
    name = company_name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return f"{name}.com"


def search_images(query: str, num: int = 1, size: str | None = None,
                  type_filter: str | None = None) -> list[str]:
    """Search for images. SerpAPI first, DuckDuckGo fallback."""
    key = os.environ.get("SERPAPI_KEY")
    if key:
        try:
            import serpapi
            params = {
                "engine": "google_images",
                "q": query,
                "num": num * 3,
            }
            if size:
                size_map = {"large": "l", "medium": "m", "icon": "i"}
                params["imgsz"] = size_map.get(size, size)
            if type_filter:
                type_map = {"photo": "photo", "clipart": "clipart",
                            "face": "face", "lineart": "lineart"}
                params["imgtype"] = type_map.get(type_filter, type_filter)

            client = serpapi.Client(api_key=key)
            results = client.search(params)
            urls = [r["original"] for r in results.get("images_results", [])
                    if "original" in r]
            if urls:
                return urls[:num * 3]
        except Exception as e:
            print(f"SerpAPI failed ({e}), falling back to DuckDuckGo...",
                  file=sys.stderr)

    from duckduckgo_search import DDGS
    results = DDGS().images(keywords=query, max_results=num * 3)
    return [r["image"] for r in results if "image" in r]


def search_stock(query: str, num: int = 1) -> list[str]:
    """Search stock photo APIs. Unsplash -> Pexels -> web search fallback."""
    import httpx

    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if unsplash_key:
        try:
            resp = httpx.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": num,
                        "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {unsplash_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                urls = [r["urls"]["regular"]
                        for r in resp.json().get("results", [])]
                if urls:
                    return urls
        except Exception as e:
            print(f"Unsplash failed ({e}), trying Pexels...",
                  file=sys.stderr)

    pexels_key = os.environ.get("PEXELS_API_KEY")
    if pexels_key:
        try:
            resp = httpx.get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": num},
                headers={"Authorization": pexels_key},
                timeout=15,
            )
            if resp.status_code == 200:
                urls = [r["src"]["large"]
                        for r in resp.json().get("photos", [])]
                if urls:
                    return urls
        except Exception as e:
            print(f"Pexels failed ({e}), falling back to web search...",
                  file=sys.stderr)

    print("No stock photo API keys found, falling back to web search...",
          file=sys.stderr)
    return search_images(f"{query} stock photo", num)


def fetch_logo(domain: str, output_path: str) -> str | None:
    """Fetch logo from Logo.dev, fall back to image search."""
    import httpx
    from PIL import Image as PILImage
    from io import BytesIO

    url = f"https://img.logo.dev/{domain}?size=200&format=png"
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 100:
            img = PILImage.open(BytesIO(resp.content))
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            if img.mode == "RGBA":
                rgb = PILImage.new("RGB", img.size, (255, 255, 255))
                rgb.paste(img, mask=img.split()[3])
                rgb.save(str(out), "PNG")
            else:
                img.convert("RGB").save(str(out), "PNG")
            return str(out)
    except Exception as e:
        print(f"Logo.dev failed ({e}), falling back to image search...",
              file=sys.stderr)

    return None


def download_image(url: str, output_path: str) -> str | None:
    """Download image from URL, validate with PIL, normalize format."""
    import httpx
    from PIL import Image as PILImage
    from io import BytesIO

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return None

        img = PILImage.open(BytesIO(resp.content))
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if img.mode == "RGBA":
            rgb = PILImage.new("RGB", img.size, (255, 255, 255))
            rgb.paste(img, mask=img.split()[3])
            rgb.save(str(out), "PNG")
        else:
            img.convert("RGB").save(str(out), "PNG")

        return str(out)
    except Exception as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
        return None


def print_typst_code(path: str, width: str, caption: str):
    print(f"""#figure(
  image("{path}", width: {width}),
  caption: [{caption}],
)""")


def main():
    parser = argparse.ArgumentParser(
        description="Search the web for images and download them.",
    )
    parser.add_argument("query", help="Search terms or company name")
    parser.add_argument("--logo", action="store_true",
                        help="Logo mode — treat query as company/domain")
    parser.add_argument("--stock", action="store_true",
                        help="Stock photo mode — Unsplash/Pexels (license-clear)")
    parser.add_argument("--url", default=None,
                        help="Direct URL download mode")
    parser.add_argument("--dir", "-d", default="images",
                        help="Output directory (default: images)")
    parser.add_argument("--output", "-o", default=None,
                        help="Explicit output path")
    parser.add_argument("--num", "-n", type=int, default=1,
                        help="Number of images to download (default: 1)")
    parser.add_argument("--size", choices=["large", "medium", "icon"],
                        help="SerpAPI size filter")
    parser.add_argument("--type", dest="type_filter",
                        choices=["photo", "clipart", "face", "lineart"],
                        help="SerpAPI type filter")
    parser.add_argument("--typst", action="store_true",
                        help="Print Typst figure code after download")
    parser.add_argument("--width", default="80%",
                        help="Typst image width (default: 80%%)")
    parser.add_argument("--caption", default=None,
                        help="Typst caption (auto-generated if omitted)")
    args = parser.parse_args()

    saved_paths: list[str] = []

    # --- Direct URL mode ---
    if args.url:
        output_path = args.output or auto_filename(args.query, args.dir)
        result = download_image(args.url, output_path)
        if result:
            saved_paths.append(result)
        else:
            print(f"Error: failed to download {args.url}", file=sys.stderr)
            sys.exit(1)

    # --- Logo mode ---
    elif args.logo:
        domain = args.query
        if "." not in domain:
            domain = resolve_domain(args.query)
            print(f"Resolved '{args.query}' -> {domain}", file=sys.stderr)

        output_path = args.output or auto_filename(
            args.query, args.dir, ext="-logo.png")
        result = fetch_logo(domain, output_path)
        if result:
            saved_paths.append(result)
        else:
            print(f"Logo.dev failed, searching for logo...", file=sys.stderr)
            urls = search_images(f"{args.query} logo transparent", num=1)
            for url in urls:
                result = download_image(url, output_path)
                if result:
                    saved_paths.append(result)
                    break
            if not saved_paths:
                print("Error: could not find logo", file=sys.stderr)
                sys.exit(1)

    # --- Stock photo mode ---
    elif args.stock:
        urls = search_stock(args.query, num=args.num)
        for i, url in enumerate(urls[:args.num]):
            if args.num == 1:
                output_path = args.output or auto_filename(
                    args.query, args.dir)
            else:
                base = args.output or auto_filename(args.query, args.dir)
                stem = Path(base).stem
                output_path = str(
                    Path(base).parent / f"{stem}_{i + 1}.png")
            result = download_image(url, output_path)
            if result:
                saved_paths.append(result)
        if not saved_paths:
            print("Error: no stock images downloaded", file=sys.stderr)
            sys.exit(1)

    # --- Default: image search ---
    else:
        urls = search_images(args.query, num=args.num, size=args.size,
                             type_filter=args.type_filter)
        for i, url in enumerate(urls[:args.num]):
            if args.num == 1:
                output_path = args.output or auto_filename(
                    args.query, args.dir)
            else:
                base = args.output or auto_filename(args.query, args.dir)
                stem = Path(base).stem
                output_path = str(
                    Path(base).parent / f"{stem}_{i + 1}.png")
            result = download_image(url, output_path)
            if result:
                saved_paths.append(result)
            # Try next URL if download failed
        if not saved_paths:
            print("Error: no images downloaded", file=sys.stderr)
            sys.exit(1)

    # --- Output ---
    for p in saved_paths:
        print(f"Saved: {p} ({format_size(p)})")

    if args.typst:
        print("\nTypst:")
        for p in saved_paths:
            caption = args.caption or slugify(
                args.query, 60).replace("-", " ").title()
            print_typst_code(p, args.width, caption)


if __name__ == "__main__":
    main()
