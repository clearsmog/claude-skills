#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate or edit images using Gemini Image API, with optional Typst output.

Usage:
    uv run gemini_imagen.py -p "description" -o dir/file.png
    uv run gemini_imagen.py -p "description" --dir charts --typst
    uv run gemini_imagen.py -p "edit this" -o out.png -i input.png
    uv run gemini_imagen.py -p "combine" -o out.png -i a.png -i b.png
"""

import argparse
import base64
import os
import re
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

MODELS_WITH_IMAGE_CONFIG = {"gemini-3-pro-image-preview"}


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GENAI_API_KEY")


def slugify(text: str, max_len: int = 40) -> str:
    """Convert prompt text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len].rstrip("-")


def auto_filename(prompt: str, output_dir: str) -> str:
    """Generate timestamped filename from prompt."""
    date = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(prompt)
    return str(Path(output_dir) / f"{date}-{slug}.png")


def generate_image(
    prompt: str,
    output_path: str,
    model: str = "gemini-3-pro-image-preview",
    input_images: list[str] | None = None,
    resolution: str = "1K",
    num_images: int = 1,
    aspect_ratio: str | None = None,
    api_key: str | None = None,
) -> list[str]:
    """Generate image(s) and return list of saved paths."""
    key = get_api_key(api_key)
    if not key:
        print("Error: GEMINI_API_KEY not set.", file=sys.stderr)
        print("  1. Get a key at https://ai.google.dev/", file=sys.stderr)
        print("  2. fish: set -Ux GEMINI_API_KEY 'your-key'", file=sys.stderr)
        print("  3. bash/zsh: export GEMINI_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)

    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    client = genai.Client(api_key=key)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    parts: list = []

    if input_images:
        if len(input_images) > 14:
            raise ValueError(f"Max 14 input images, got {len(input_images)}.")
        max_dim = 0
        for img_path in input_images:
            img = PILImage.open(img_path)
            parts.append(img)
            w, h = img.size
            max_dim = max(max_dim, w, h)
        if resolution == "1K" and max_dim > 0:
            if max_dim >= 3000:
                resolution = "4K"
            elif max_dim >= 1500:
                resolution = "2K"

    parts.append(prompt)
    contents = parts if len(parts) > 1 else prompt

    if model in MODELS_WITH_IMAGE_CONFIG:
        img_cfg_kwargs = {"image_size": resolution}
        if aspect_ratio:
            img_cfg_kwargs["aspect_ratio"] = aspect_ratio
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(**img_cfg_kwargs),
        )
    else:
        img_cfg = types.ImageConfig(aspect_ratio=aspect_ratio) if aspect_ratio else None
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=img_cfg,
        )

    saved_paths: list[str] = []
    base_name = out.stem
    extension = out.suffix or ".png"

    for i in range(num_images):
        mode = "Editing" if input_images else "Generating"
        print(f"{mode} image {i + 1}/{num_images}...", file=sys.stderr)

        response = client.models.generate_content(
            model=model, contents=contents, config=config,
        )

        if not response.candidates:
            raise ValueError("No candidates returned from the API.")
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise ValueError("No content parts in response.")

        img_count = 0
        for part in candidate.content.parts:
            if part.text is not None:
                try:
                    print(f"Model: {part.text}", file=sys.stderr)
                except UnicodeEncodeError:
                    print(f"Model: {part.text.encode('ascii', errors='replace').decode('ascii')}", file=sys.stderr)
            elif part.inline_data is not None:
                data = part.inline_data.data
                if isinstance(data, str):
                    data = base64.b64decode(data)

                image = PILImage.open(BytesIO(data))

                if num_images == 1 and img_count == 0:
                    save_path = str(out)
                else:
                    save_path = str(out.parent / f"{base_name}_{i + 1}_{img_count + 1}{extension}")

                if image.mode == "RGBA":
                    rgb = PILImage.new("RGB", image.size, (255, 255, 255))
                    rgb.paste(image, mask=image.split()[3])
                    rgb.save(save_path, "PNG")
                else:
                    image.convert("RGB").save(save_path, "PNG")

                saved_paths.append(save_path)
                img_count += 1

    return saved_paths


def format_size(path: str) -> str:
    size = Path(path).stat().st_size
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / 1024:.0f} KB"


def main():
    parser = argparse.ArgumentParser(
        description="Generate images via Gemini Image API.",
    )
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--output", "-o", default=None,
                        help="Output path. If omitted, auto-generated from prompt + --dir.")
    parser.add_argument("--dir", "-d", default="images",
                        help="Output directory (used when --output is omitted, default: images)")
    parser.add_argument("--model", "-m", default="gemini-3-pro-image-preview")
    parser.add_argument("--input-image", "-i", action="append", dest="input_images", metavar="IMAGE")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K")
    parser.add_argument("--aspect-ratio", "-a", default=None,
                        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                        help="Output image aspect ratio")
    parser.add_argument("--num-images", "-n", type=int, default=1)
    parser.add_argument("--api-key", "-k")
    # Typst integration flags
    parser.add_argument("--typst", action="store_true",
                        help="Print Typst figure code after generation")
    parser.add_argument("--width", default="80%",
                        help="Typst image width (default: 80%%)")
    parser.add_argument("--caption", default=None,
                        help="Typst figure caption (auto-generated if omitted)")
    args = parser.parse_args()

    # Resolve output path
    if args.output:
        output_path = args.output
    else:
        output_path = auto_filename(args.prompt, args.dir)

    try:
        saved = generate_image(
            prompt=args.prompt,
            output_path=output_path,
            model=args.model,
            input_images=args.input_images,
            resolution=args.resolution,
            num_images=args.num_images,
            aspect_ratio=args.aspect_ratio,
            api_key=args.api_key,
        )

        # Print summary to stdout (this is what Claude reads)
        for p in saved:
            print(f"Saved: {p} ({format_size(p)})")

        # Typst code output
        if args.typst:
            print("\nTypst:")
            for p in saved:
                caption = args.caption or slugify(args.prompt, 60).replace("-", " ").title()
                print(f"""#figure(
  image("{p}", width: {args.width}),
  caption: [{caption}],
)""")

    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stdout)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
