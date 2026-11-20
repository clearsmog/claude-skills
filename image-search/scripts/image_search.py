#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "serpapi>=0.1.5",
#     "ddgs>=9.0.0",
#     "pillow>=10.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Search the web for images and download them, with optional Typst output.

Channels (keyless unless noted):
    ddgs         DuckDuckGo image index — broad web, good for real-world photos
    commons      Wikimedia Commons — CC-licensed, high-res, factual subjects
    openverse    Openverse — CC pool (Flickr, museums, Wikimedia), attribution built in
    nasa         NASA image library — public domain space/science
    iconify      Iconify icon sets — SVG glyphs for diagrams
    simpleicons  Brand marks — SVG, single-colour
    serpapi      Google/Bing/Yandex/Baidu Images (key)
    brave        Brave Images (key)
    unsplash / pexels / pixabay   stock (key)
    logo_dev / brandfetch         brand marks (key)

Usage:
    uv run image_search.py "golden gate bridge" --typst
    uv run image_search.py "golden gate bridge" --engine commons -n 3
    uv run image_search.py --logo "Alphabet Inc" --typst
    uv run image_search.py --icon "database" --typst
    uv run image_search.py --stock "office meeting" --typst
    uv run image_search.py --url "https://example.com/img.png" "example" --typst
    uv run image_search.py "sfo skyline" --aspect 16:9 --crop --json
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

UA = "image-search/2.0 (document image search; +https://github.com/anthropics/claude-code)"
CACHE_DIR = Path(os.environ.get("IMAGE_SEARCH_CACHE",
                               Path.home() / ".cache" / "image-search"))
CACHE_TTL = 24 * 3600
SECRETS = ("SERPAPI_KEY", "BRAVE_API_KEY", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY",
           "PIXABAY_API_KEY", "LOGO_DEV_TOKEN", "BRANDFETCH_CLIENT_ID")
DOTFILES = ("~/.config/fish/fish_variables", "~/.zshenv", "~/.zshrc",
            "~/.profile", "~/.env")


# ---------------------------------------------------------------- basics

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


def resolve_output(args_output: str | None, args_dir: str,
                   query: str, ext: str = ".png") -> str:
    """Resolve output path: combine -o with -d, ensure extension."""
    if args_output:
        out_p = Path(args_output)
        # If -o is just a filename (no directory), place in --dir
        if out_p.parent == Path("."):
            out_p = Path(args_dir) / out_p
        # Ensure extension
        if not out_p.suffix:
            out_p = out_p.with_suffix(ext)
        return str(out_p)
    return auto_filename(query, args_dir, ext)


def format_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / 1024:.0f} KB"


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"\s+", " ", value).strip()


# ---------------------------------------------------------------- secrets

_secret_cache: dict[str, str] = {}


def _unescape_fish(value: str) -> str:
    """fish stores '--' as '\\x2d' in fish_variables."""
    return re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), value)


def _dotfile_values() -> dict[str, str]:
    """Read KEY=VALUE / KEY:VALUE pairs out of fish universals and shell dotfiles."""
    found: dict[str, str] = {}
    for raw in DOTFILES:
        p = Path(raw).expanduser()
        if not p.exists():
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # fish universal: "SETUVAR --export KEY:value"
            m = re.match(r"^SETUVAR(?:\s+--\w+)*\s+([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
            if m and m.group(1) in SECRETS:
                found.setdefault(m.group(1), _unescape_fish(m.group(2)).strip())
                continue
            # dotenv / shell: "export KEY=value"
            m = re.match(r"^(?:export\s+)?([A-Z][A-Z0-9_]*)\s*[:=]\s*(.+)$", line)
            if m and m.group(1) in SECRETS:
                found.setdefault(m.group(1), _unescape_fish(m.group(2)).strip().strip("'\""))
    return found


def key(name: str) -> str:
    """Env var, else value from fish universals / shell dotfiles. Sanitized."""
    if name in _secret_cache:
        return _secret_cache[name]
    value = os.environ.get(name, "")
    if not value:
        value = _dotfile_values().get(name, "")
    value = re.sub(r"[^A-Za-z0-9_\-.]", "", value)
    _secret_cache[name] = value
    return value


def http_client(timeout: float = 20.0):
    import httpx
    return httpx.Client(headers={"User-Agent": UA}, timeout=timeout,
                        follow_redirects=True)


def get_json(url: str, params: dict | None = None, headers: dict | None = None,
             timeout: float = 20.0, cache_key: str | None = None,
             use_cache: bool = True):
    """GET JSON with an optional on-disk cache (quota protection)."""
    if cache_key and use_cache:
        cached = _cache_read(cache_key)
        if cached is not None:
            return cached
    with http_client(timeout) as c:
        resp = c.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    if cache_key and use_cache:
        _cache_write(cache_key, data)
    return data


def _cache_read(name: str):
    p = CACHE_DIR / "responses" / (hashlib.sha1(name.encode()).hexdigest() + ".json")
    try:
        if p.exists() and time.time() - p.stat().st_mtime < CACHE_TTL:
            return json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    return None


def _cache_write(name: str, data):
    try:
        p = CACHE_DIR / "responses" / (hashlib.sha1(name.encode()).hexdigest() + ".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data)[:4_000_000])
    except OSError:
        pass


def quota_spend(engine: str) -> int:
    """Count paid API calls per calendar month so the shared free plan is visible."""
    p = CACHE_DIR / "usage.json"
    month = datetime.now().strftime("%Y-%m")
    try:
        data = json.loads(p.read_text()) if p.exists() else {}
    except (OSError, ValueError):
        data = {}
    bucket = data.setdefault(month, {})
    bucket[engine] = bucket.get(engine, 0) + 1
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))
    except OSError:
        pass
    return bucket[engine]


# ---------------------------------------------------------------- candidates

@dataclass
class Candidate:
    url: str
    engine: str
    width: int | None = None
    height: int | None = None
    title: str = ""
    page: str = ""
    license: str = ""
    author: str = ""
    mime: str = ""
    saved_path: str = ""

    def __post_init__(self):
        # Search APIs are inconsistent: widths arrive as int, str or None.
        for attr in ("width", "height"):
            raw = getattr(self, attr)
            try:
                setattr(self, attr, int(raw) if raw not in (None, "") else None)
            except (TypeError, ValueError):
                setattr(self, attr, None)

    @property
    def area(self) -> int:
        return (self.width or 0) * (self.height or 0)

    @property
    def aspect(self) -> float | None:
        if self.width and self.height:
            return self.width / self.height
        return None


class EngineError(RuntimeError):
    pass


def _norm_url(url: str) -> str:
    url = url.split("&amp;")[0].strip()
    return url.split("?")[0] if url.startswith("https://upload.wikimedia") else url


# ---------------------------------------------------------------- engines

def eng_commons(q: str, n: int, opt) -> list[Candidate]:
    """Wikimedia Commons — keyless, CC-licensed, encyclopedic."""
    data = get_json(
        "https://commons.wikimedia.org/w/api.php",
        params={"action": "query", "format": "json", "generator": "search",
                "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6,
                "gsrlimit": min(50, max(n * 4, 8)), "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 2000},
        cache_key=f"commons:{q}:{n}", use_cache=not opt.no_cache)
    pages = data.get("query", {}).get("pages", {})
    out: list[Candidate] = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 1 << 30)):
        info = (p.get("imageinfo") or [{}])[0]
        em = info.get("extmetadata") or {}
        url = info.get("thumburl") or info.get("url")
        if not url:
            continue
        out.append(Candidate(
            url=url, engine="commons", width=info.get("width"),
            height=info.get("height"), mime=info.get("mime", ""),
            title=strip_html(em.get("ObjectName", {}).get("value", "")
                             or p.get("title", "")),
            page=info.get("descriptionurl", ""),
            license=strip_html(em.get("LicenseShortName", {}).get("value", "")),
            author=strip_html(em.get("Artist", {}).get("value", "")),
        ))
    return out


def eng_openverse(q: str, n: int, opt) -> list[Candidate]:
    """Openverse — CC pool, anonymous access ~20 req/min, 200/day."""
    data = get_json("https://api.openverse.org/v1/images/",
                    params={"q": q, "page_size": min(20, max(n * 4, 8))},
                    cache_key=f"openverse:{q}:{n}", use_cache=not opt.no_cache)
    out = []
    for r in data.get("results", []):
        if not r.get("url"):
            continue
        out.append(Candidate(
            url=r["url"], engine="openverse", width=r.get("width"),
            height=r.get("height"), title=r.get("title") or "",
            page=r.get("foreign_landing_url") or "",
            license=(r.get("license") or "").upper()
                    + (f" {r.get('license_version')}" if r.get("license_version") else ""),
            author=r.get("creator") or "",
        ))
    return out


def eng_ddgs(q: str, n: int, opt) -> list[Candidate]:
    """DuckDuckGo image index via the `ddgs` package (formerly duckduckgo_search)."""
    try:
        from ddgs import DDGS
    except ImportError:  # older installs
        from duckduckgo_search import DDGS

    size_map = {"large": "Large", "medium": "Medium", "icon": "Small"}
    type_map = {"photo": "photo", "clipart": "clipart",
                "lineart": "line", "face": "photo"}
    kwargs = {"max_results": max(n * 4, 10), "safesearch": "moderate"}
    if opt.size:
        kwargs["size"] = size_map.get(opt.size, opt.size)
    if opt.type_filter:
        kwargs["type_image"] = type_map.get(opt.type_filter, opt.type_filter)

    last: Exception | None = None
    for attempt in range(3):
        try:
            rows = list(DDGS().images(q, **kwargs))
            out = []
            for r in rows:
                if not r.get("image"):
                    continue
                out.append(Candidate(
                    url=r["image"], engine="ddgs",
                    width=r.get("width"), height=r.get("height"),
                    title=r.get("title") or "", page=r.get("url") or "",
                    license="unknown (web image)"))
            if out:
                return out
            last = EngineError("no rows")
        except Exception as exc:  # ratelimit / 202 / network
            last = exc
        time.sleep(1.2 * (attempt + 1))
    raise EngineError(f"ddgs unavailable ({type(last).__name__}: {last})")


def eng_serpapi(q: str, n: int, opt) -> list[Candidate]:
    """SerpAPI: google_images | bing_images | yandex_images | baidu_images | google_images_light."""
    token = key("SERPAPI_KEY")
    if not token:
        raise EngineError("SERPAPI_KEY not set")
    try:
        import serpapi
    except ImportError as exc:
        raise EngineError(f"serpapi package missing ({exc})") from exc

    backend = getattr(opt, "serpapi_engine", "google_images")
    params = {"engine": backend, "q": q,
              "num" if backend.startswith("google") else "count": max(n * 3, 6)}
    if opt.size and backend.startswith("google"):
        params["imgsz"] = {"large": "l", "medium": "m", "icon": "i"}.get(opt.size, opt.size)
    if opt.type_filter and backend.startswith("google"):
        params["imgtype"] = {"photo": "photo", "clipart": "clipart",
                             "face": "face", "lineart": "lineart"}.get(
                                 opt.type_filter, opt.type_filter)
    try:
        result = serpapi.Client(api_key=token).search(params)
    except Exception as exc:
        text = str(exc)
        if "429" in text or "Too Many" in text:
            raise EngineError("SerpAPI quota exhausted (free plan 250/month, "
                              "shared with the reddit skill)") from exc
        raise EngineError(f"SerpAPI {backend} failed ({text[:120]})") from exc
    quota_spend(f"serpapi:{backend}")

    out = []
    for r in result.get("images_results", []) or result.get("images", []):
        url = r.get("original") or r.get("link") or r.get("imageUrl")
        if not url:
            continue
        out.append(Candidate(
            url=url, engine=f"serpapi:{backend}",
            width=r.get("original_width"), height=r.get("original_height"),
            title=r.get("title") or "", page=r.get("link") or r.get("source") or "",
            license="unknown (web image)"))
    return out


def eng_brave(q: str, n: int, opt) -> list[Candidate]:
    """Brave Search Images API — free tier ~2k queries/month, key required."""
    token = key("BRAVE_API_KEY")
    if not token:
        raise EngineError("BRAVE_API_KEY not set")
    data = get_json("https://api.search.brave.com/res/v1/images/search",
                    params={"q": q, "count": min(100, max(n * 4, 10)),
                            "safesearch": "strict", "country": "us"},
                    headers={"Accept": "application/json",
                             "X-Subscription-Token": token},
                    cache_key=f"brave:{q}:{n}", use_cache=not opt.no_cache)
    quota_spend("brave")
    out = []
    for r in data.get("results", []):
        props = r.get("properties") or {}
        url = props.get("url") or (r.get("thumbnail") or {}).get("src")
        if not url:
            continue
        out.append(Candidate(url=url, engine="brave",
                             width=props.get("width"), height=props.get("height"),
                             title=r.get("title") or "",
                             page=r.get("page_url") or "",
                             license="unknown (web image)"))
    return out


def eng_nasa(q: str, n: int, opt) -> list[Candidate]:
    """NASA image library — public domain."""
    data = get_json("https://images-api.nasa.gov/search",
                    params={"q": q, "media_type": "image"},
                    cache_key=f"nasa:{q}", use_cache=not opt.no_cache)
    out = []
    for item in (data.get("collection", {}).get("items") or [])[:max(n * 4, 8)]:
        links = item.get("links") or [{}]
        url = links[0].get("href")
        if not url:
            continue
        meta = item.get("data", [{}])[0]
        out.append(Candidate(url=url, engine="nasa",
                             title=meta.get("title", ""),
                             page=f"https://images.nasa.gov/details/{meta.get('nasa_id','')}",
                             license="public domain (NASA)"))
    return out


def eng_reverse(url: str, n: int, opt) -> list[Candidate]:
    """Reverse image lookup (Google Lens via SerpAPI): page it came from, similar shots."""
    token = key("SERPAPI_KEY")
    if not token:
        raise EngineError("reverse lookup needs SERPAPI_KEY (Google Lens engine)")
    try:
        import serpapi
        result = serpapi.Client(api_key=token).search(
            {"engine": "google_lens", "url": url})
    except Exception as exc:
        if "429" in str(exc):
            raise EngineError("SerpAPI quota exhausted") from exc
        raise EngineError(f"lens failed ({str(exc)[:100]})") from exc
    quota_spend("serpapi:google_lens")
    out = []
    for r in result.get("visual_matches", [])[:max(n * 4, 8)]:
        if not r.get("thumbnail"):
            continue
        out.append(Candidate(url=r["thumbnail"], engine="lens",
                             title=r.get("title") or "",
                             page=r.get("link") or "", width=r.get("image_width"),
                             height=r.get("image_height"),
                             license="unknown (visual match)"))
    return out


ENGINES = {
    "commons": eng_commons,
    "openverse": eng_openverse,
    "ddgs": eng_ddgs,
    "serpapi": eng_serpapi,
    "brave": eng_brave,
    "nasa": eng_nasa,
}


def ladder(opt) -> list[str]:
    """Engine order for --engine auto: keyed quality tiers first, keyless after."""
    order: list[str] = []
    if opt.engine not in (None, "auto"):
        return [opt.engine]
    if key("BRAVE_API_KEY"):
        order.append("brave")
    if key("SERPAPI_KEY") and not opt.no_serpapi:
        order.append("serpapi")
    order += ["ddgs", "commons", "openverse"]
    return order


def search_images(query: str, num: int | None = None, size: str | None = None,
                  type_filter: str | None = None, opt=None) -> list[str]:
    """Back-compat wrapper: returns candidate URLs across engines."""
    return [c.url for c in search_candidates(query, num or 1, opt)]


def search_candidates(query: str, num: int, opt) -> list[Candidate]:
    """Walk the engine ladder until enough candidates are collected."""
    need = max(num * 3, 6)
    collected: list[Candidate] = []
    seen: set[str] = set()
    errors: list[str] = []
    tried = 0
    for name in ladder(opt):
        if len(collected) >= need or tried >= 4:
            break
        tried += 1
        try:
            rows = ENGINES[name](query, num, opt)
        except EngineError as exc:
            errors.append(f"{name}: {exc}")
            if not opt.json:
                print(f"  [{name}] {exc}", file=sys.stderr)
            continue
        except Exception as exc:  # network / parse — never fatal
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            if not opt.json:
                print(f"  [{name}] failed: {type(exc).__name__}", file=sys.stderr)
            continue
        fresh = 0
        for c in rows:
            u = _norm_url(c.url)
            if u in seen:
                continue
            seen.add(u)
            collected.append(c)
            fresh += 1
        if not opt.json:
            print(f"  [{name}] {fresh} candidates", file=sys.stderr)
    opt.errors.extend(errors)
    collected.sort(key=lambda c: _rank(c, opt), reverse=True)
    return collected


def _rank(cand: Candidate, opt) -> float:
    """Score candidates: resolution matters, but document layout matters more."""
    import math

    target = getattr(opt, "aspect_value", None) or 1.5   # landscape by default
    megapixels = cand.area / 1_000_000 if cand.area else 0.4   # unknown: assume ~0.4 MP
    ratio = cand.aspect or target
    penalty = 1 / (1 + abs(math.log(max(ratio, 0.1) / target)))
    return (megapixels ** 0.5) * penalty


# ---------------------------------------------------------------- assets (logo / icon)

def wikidata_website(name: str) -> str | None:
    """Official website (P856) for a company/brand — fixes the '<name>.com' guess."""
    try:
        found = get_json("https://www.wikidata.org/w/api.php",
                         params={"action": "wbsearchentities", "format": "json",
                                 "search": name, "language": "en", "limit": 1},
                         cache_key=f"wd-search:{name}")
        hits = found.get("search") or []
        if not hits:
            return None
        qid = hits[0]["id"]
        ent = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
                       cache_key=f"wd-entity:{qid}")
        claims = ent["entities"][qid]["claims"].get("P856") or []
        for c in claims:
            value = (c.get("mainsnak") or {}).get("datavalue", {}).get("value")
            if value:
                return re.sub(r"^https?://(www\.)?", "", value).split("/")[0]
    except Exception:
        return None
    return None


def resolve_domain(company_name: str) -> str:
    """Domain for a brand: Wikidata P856 first, '<name>.com' heuristic after."""
    if "." in company_name and " " not in company_name:
        return company_name
    domain = wikidata_website(company_name)
    if domain:
        return domain
    return re.sub(r"[^a-z0-9]", "", company_name.lower()) + ".com"


def _write_bytes(data: bytes, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(out)
    return str(out)


def fetch_svg(url: str, output_path: str, timeout: float = 20.0) -> str | None:
    """Fetch an SVG mark and store it verbatim (Typst renders SVG natively)."""
    try:
        with http_client(timeout) as c:
            resp = c.get(url)
        if resp.status_code != 200:
            return None
        text = resp.text
        if "<svg" not in text[:2000]:
            return None
        return _write_bytes(text.encode("utf-8"), output_path)
    except Exception:
        return None


def fetch_logo(domain: str, output_path: str, name: str = "",
               timeout: float = 20.0, fmt: str = "png") -> str | None:
    """Brand mark, vector first: Simple Icons -> Brandfetch -> Commons SVG ->
    Logo.dev -> favicon service."""
    stem = Path(output_path).with_suffix("")

    # 1. Simple Icons (monochrome SVG, keyless)
    slug = re.sub(r"[^a-z0-9]", "", (name or domain.split(".")[0]).lower())
    for candidate_slug in {slug, slug.replace("inc", ""), domain.split(".")[0]}:
        if not candidate_slug:
            continue
        got = fetch_svg(f"https://cdn.simpleicons.org/{candidate_slug}",
                        f"{stem}.svg")
        if got:
            return got

    # 2. Brandfetch (client id required)
    bf = key("BRANDFETCH_CLIENT_ID")
    if bf:
        got = fetch_svg(f"https://cdn.brandfetch.io/{domain}/w/512/h/512/logo?c={bf}",
                        f"{stem}.svg")
        if got:
            return got

    # 3. Wikimedia Commons — real wordmarks, still vector
    if name:
        try:
            rows = eng_commons(f"{name} logo filetype:drawing", 4,
                               argparse.Namespace(no_cache=False, size=None,
                                                  type_filter=None))
            for row in rows:
                if row.mime.endswith("svg") or row.url.lower().endswith(".svg"):
                    got = fetch_svg(row.url, f"{stem}.svg")
                    if got:
                        return got
        except Exception:
            pass

    # 4. Logo.dev (200 px PNG icon, needs publishable token)
    token = key("LOGO_DEV_TOKEN")
    if token:
        got = fetch_raster(f"https://img.logo.dev/{domain}?size=256&format=png&token={token}",
                           output_path, keep_alpha=True, white_bg=False, fmt=fmt)
        if got:
            return got

    # 5. Favicon services — last resort, small raster
    for url in (f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
                f"https://icons.duckduckgo.com/ip3/{domain}.ico",
                f"https://unavatar.io/{domain}"):
        got = fetch_raster(url, output_path, keep_alpha=True, white_bg=False,
                           fmt=fmt)
        if got:
            return got
    return None


def search_icon(name: str, n: int, opt) -> list[Candidate]:
    """Iconify search — SVG icons for diagrams and inline glyphs."""
    data = get_json("https://api.iconify.design/search",
                    params={"query": name, "limit": max(n * 4, 8)},
                    cache_key=f"iconify:{name}:{n}", use_cache=not opt.no_cache)
    out = []
    for icon in data.get("icons", []):
        prefix, _, short = icon.partition(":")
        out.append(Candidate(
            url=f"https://api.iconify.design/{prefix}/{short}.svg",
            engine="iconify", title=icon, license="icon-set licence",
            page=f"https://icon-sets.iconify.design/{prefix}/?query={short}"))
    return out


# ---------------------------------------------------------------- download / normalise

def _to_srgb(img):
    """Honour embedded ICC profiles so colours do not shift in print."""
    try:
        from PIL import ImageCms
        icc = img.info.get("icc_profile")
        if icc:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            return ImageCms.profileToProfile(img, src, ImageCms.createProfile("sRGB"))
    except Exception:
        pass
    return img


def _has_alpha(img) -> bool:
    return img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)


def _encode(img, path: Path, fmt: str, max_kb: int) -> None:
    if fmt == "jpeg":
        img.convert("RGB").save(str(path), "JPEG", quality=88, optimize=True,
                                progressive=True)
    else:
        img.save(str(path), "PNG", optimize=True)
    # Soft size budget: step quality/scale down until it fits
    if max_kb <= 0:
        return
    for _ in range(6):
        if path.stat().st_size <= max_kb * 1024:
            return
        if fmt == "jpeg":
            for q in (80, 72, 64, 56):
                img.convert("RGB").save(str(path), "JPEG", quality=q, optimize=True,
                                        progressive=True)
                if path.stat().st_size <= max_kb * 1024:
                    return
        width, height = img.size
        img = img.resize((max(320, int(width * 0.8)), max(320, int(height * 0.8))))
        _encode(img, path, fmt, max_kb)
        return


def fetch_raster(url: str, output_path: str, *, page: str = "",
                 fmt: str = "auto", max_width: int = 1600, max_kb: int = 2500,
                 aspect: float | None = None, crop: bool = False,
                 keep_alpha: bool = False, white_bg: bool = False,
                 min_width: int = 0, timeout: float = 30.0) -> str | None:
    """Download one image, validate it, normalise size/format, write atomically."""
    from PIL import Image as PILImage

    try:
        with http_client(timeout) as c:
            headers = {"Referer": page} if page else {}
            resp = c.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} for {url[:90]}", file=sys.stderr)
            return None
        ctype = (resp.headers.get("content-type") or "").lower()
        if "svg" in ctype or resp.content[:200].lstrip().lower().startswith(b"<svg"):
            return fetch_svg(url, str(Path(output_path).with_suffix(".svg")))
        if ctype and not ctype.startswith("image/"):
            return None
        if len(resp.content) < 2_500:            # tracking pixel / error page
            return None

        img = PILImage.open(io.BytesIO(resp.content))
        if img.width < 200 or img.height < 200:
            print(f"  too small ({img.width}x{img.height}), skipping", file=sys.stderr)
            return None
        if min_width and img.width < min_width:
            print(f"  under min width ({img.width} < {min_width}), skipping",
                  file=sys.stderr)
            return None

        img = _to_srgb(img)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, max(1, round(img.height * ratio))),
                             PILImage.LANCZOS)

        if aspect and crop:
            target = aspect
            current = img.width / img.height
            if current > target:
                new_w = round(img.height * target)
                left = (img.width - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.height))
            elif current < target:
                new_h = round(img.width / target)
                top = (img.height - new_h) // 2
                img = img.crop((0, top, img.width, top + new_h))

        out = Path(output_path)
        if fmt == "auto":
            fmt = "png" if (_has_alpha(img) and keep_alpha) else "jpeg"
        out = out.with_suffix(".png" if fmt == "png" else ".jpg")

        if fmt == "png":
            if white_bg or not keep_alpha:
                if _has_alpha(img):
                    canvas = PILImage.new("RGB", img.size, (255, 255, 255))
                    canvas.paste(img, mask=img.convert("RGBA").split()[3])
                    img = canvas
                else:
                    img = img.convert("RGB")
            else:
                img = img.convert("RGBA")
        else:
            if _has_alpha(img):
                canvas = PILImage.new("RGB", img.size, (255, 255, 255))
                canvas.paste(img, mask=img.convert("RGBA").split()[3])
                img = canvas
            else:
                img = img.convert("RGB")

        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(out.suffix + ".part")
        _encode(img, tmp, fmt, max_kb)
        tmp.replace(out)
        return str(out)
    except Exception as exc:
        print(f"  download failed ({type(exc).__name__}: {exc}) {url[:80]}",
              file=sys.stderr)
        return None


def download_image(url: str, output_path: str, **kwargs) -> str | None:
    """Back-compat name for fetch_raster."""
    return fetch_raster(url, output_path, **kwargs)


def _dhash(path: str, size: int = 8) -> int | None:
    """Perceptual hash for near-duplicate detection."""
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            im = im.convert("L").resize((size + 1, size), PILImage.LANCZOS)
            px = im.tobytes()  # 8-bit grayscale, one byte per pixel
        bits = 0
        for row in range(size):
            for col in range(size):
                bits <<= 1
                left = px[row * (size + 1) + col]
                right = px[row * (size + 1) + col + 1]
                bits |= 1 if left > right else 0
        return bits
    except Exception:
        return None


def _near_dup(hash_a: int | None, hash_b: int | None,
              threshold: int = 6) -> bool:
    if hash_a is None or hash_b is None:
        return False
    return bin(hash_a ^ hash_b).count("1") <= threshold


def download_first(urls: list[str], num: int, base: str, *,
                   candidates: list[Candidate] | None = None,
                   opt=None) -> list[str]:
    """Download until `num` distinct images are saved, skipping failures and dups."""
    saved: list[str] = []
    hashes: list[int | None] = []
    bp = Path(base)
    pool = candidates or [Candidate(url=u, engine="direct") for u in urls]
    opts = dict(
        fmt=getattr(opt, "fmt", "auto"), max_width=getattr(opt, "max_width", 1600),
        max_kb=getattr(opt, "max_kb", 2500),
        aspect=getattr(opt, "aspect_value", None), crop=getattr(opt, "crop", False),
        keep_alpha=getattr(opt, "keep_alpha", False),
        white_bg=getattr(opt, "white_bg", False),
        min_width=getattr(opt, "min_width", 0),
        timeout=getattr(opt, "timeout", 30.0),
    )
    for cand in pool:
        if len(saved) == num:
            break
        if not cand.url or cand.url.startswith("data:"):
            continue
        target = base if num == 1 else str(
            bp.parent / f"{bp.stem}_{len(saved) + 1}{bp.suffix}")
        result = fetch_raster(cand.url, target, page=cand.page, **opts)
        if not result:
            continue
        digest = _dhash(result)
        if any(_near_dup(digest, h) for h in hashes):
            print(f"  near-duplicate of an earlier hit, skipping {result}",
                  file=sys.stderr)
            Path(result).unlink(missing_ok=True)
            continue
        hashes.append(digest)
        saved.append(result)
        if len(saved) < num and opt is not None and opt.verbose:
            print(f"  picked {cand.engine}: {cand.url[:90]}", file=sys.stderr)
        cand.saved_path = result
    return saved


# ---------------------------------------------------------------- stock

def search_stock(query: str, num: int = 1, opt=None) -> list[Candidate]:
    """Stock photos, download-friendly services first (Unsplash requires hotlinking)."""
    out: list[Candidate] = []

    pix = key("PIXABAY_API_KEY")
    if pix:
        try:
            data = get_json("https://pixabay.com/api/",
                            params={"key": pix, "q": query, "image_type": "photo",
                                    "per_page": min(20, max(num * 3, 5)),
                                    "orientation": "horizontal", "safesize": "true"},
                            cache_key=f"pixabay:{query}:{num}")
            for r in data.get("hits", []):
                out.append(Candidate(url=r.get("largeImageURL") or r.get("webformatURL"),
                                     engine="pixabay",
                                     width=r.get("imageWidth"), height=r.get("imageHeight"),
                                     title=r.get("tags", ""), page=r.get("pageURL", ""),
                                     license="Pixabay Content Licence",
                                     author=r.get("user", "")))
        except Exception as exc:
            print(f"  [pixabay] {exc}", file=sys.stderr)

    pex = key("PEXELS_API_KEY")
    if pex and not out:
        try:
            data = get_json("https://api.pexels.com/v1/search",
                            params={"query": query, "per_page": min(20, max(num * 3, 5)),
                                    "orientation": "landscape"},
                            headers={"Authorization": pex},
                            cache_key=f"pexels:{query}:{num}")
            for r in data.get("photos", []):
                out.append(Candidate(url=r["src"]["original"], engine="pexels",
                                     width=r.get("width"), height=r.get("height"),
                                     title=r.get("alt", ""), page=r.get("url", ""),
                                     license="Pexels Licence",
                                     author=r.get("photographer", "")))
        except Exception as exc:
            print(f"  [pexels] {exc}", file=sys.stderr)

    uns = key("UNSPLASH_ACCESS_KEY")
    if uns and not out:
        try:
            data = get_json("https://api.unsplash.com/search/photos",
                            params={"query": query,
                                    "per_page": min(20, max(num * 3, 5)),
                                    "orientation": "landscape"},
                            headers={"Authorization": f"Client-ID {uns}"},
                            cache_key=f"unsplash:{query}:{num}")
            for r in data.get("results", []):
                out.append(Candidate(url=r["urls"]["full"], engine="unsplash",
                                     width=r.get("width"), height=r.get("height"),
                                     title=r.get("alt_description") or "",
                                     page=r.get("links", {}).get("html", ""),
                                     license="Unsplash Licence",
                                     author=r.get("user", {}).get("name", "")))
        except Exception as exc:
            print(f"  [unsplash] {exc}", file=sys.stderr)

    if not out:
        print("  no stock API key answered, falling back to web search",
              file=sys.stderr)
        fallback = argparse.Namespace(**{**vars(opt), "engine": "ddgs"}) if opt else \
            argparse.Namespace(no_cache=False, size=None, type_filter=None,
                               engine="ddgs", no_serpapi=True, json=True, errors=[])
        return search_candidates(f"{query} stock photo", num, fallback)
    return out


# ---------------------------------------------------------------- output

def typst_path(path: str) -> str:
    """Typst resolves a leading '/' against --root, not the filesystem root, so
    emit a path relative to the current directory whenever possible."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        print(f"  warning: {resolved} is outside the compile root; "
              f"pass --root {resolved.parent} to typst", file=sys.stderr)
        return str(resolved)


def print_typst_code(path: str, width: str, caption: str, fit: str | None = None):
    extra = f', fit: "{fit}"' if fit else ""
    print(f"""#figure(
  image("{typst_path(path)}", width: {width}{extra}),
  caption: [{caption}],
)""")


def report(saved: list[Candidate], opt) -> None:
    """Human-readable result block, including the credit/licence line."""
    records = []
    for c in saved:
        path = Path(c.saved_path)
        entry = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "engine": c.engine,
            "source": c.page or c.url,
            "image_url": c.url,
            "license": c.license,
            "author": c.author,
            "title": c.title,
        }
        if path.suffix.lower() == ".svg":
            entry["format"] = "svg"
            try:
                head = path.read_text(errors="ignore")[:800]
                box = re.search(r'viewBox="([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)"', head)
                if box:
                    entry["width"], entry["height"] = round(float(box.group(3))), \
                        round(float(box.group(4)))
            except OSError:
                pass
        else:
            try:
                from PIL import Image as PILImage
                with PILImage.open(path) as im:
                    entry["width"], entry["height"] = im.size
                    entry["format"] = im.format.lower()
            except Exception:
                pass
        records.append(entry)

    if opt.json:
        print(json.dumps({"ok": bool(records), "saved": records,
                          "errors": getattr(opt, "errors", [])}, indent=2,
                         ensure_ascii=False))
        return

    for e in records:
        dims = (f"{e.get('width')}x{e.get('height')}" if e.get("width")
                else "vector" if e.get("format") == "svg" else "?")
        print(f"Saved: {e['path']} ({format_size(e['bytes'])}, {dims}, "
              f"{e.get('format','?')}, {e['engine']})")
        bits = [b for b in (e["license"], f"by {e['author']}" if e["author"] else "",
                            e["source"]) if b]
        if bits:
            print("  " + " · ".join(bits))

    if records:
        manifest = Path(opt.dir) / ".image-search-manifest.json"
        if not opt.no_manifest:
            try:
                manifest.parent.mkdir(parents=True, exist_ok=True)
                previous = []
                if manifest.exists():
                    try:
                        previous = [r for r in json.loads(manifest.read_text())
                                    if isinstance(r, dict) and r.get("path")
                                    and Path(r["path"]).exists()
                                    and r["path"] not in {x["path"] for x in records}]
                    except (OSError, ValueError):
                        previous = []
                manifest.write_text(json.dumps(previous + records, indent=2,
                                               ensure_ascii=False))
            except OSError:
                pass

    if opt.typst:
        print("\nTypst:")
        for e in records:
            caption = opt.caption or slugify(opt.query, 60).replace("-", " ").title()
            print_typst_code(e["path"], opt.width, caption, opt.fit)

    used = []
    if key("SERPAPI_KEY"):
        try:
            used = json.loads((CACHE_DIR / "usage.json").read_text()
                              ).get(datetime.now().strftime("%Y-%m"), {})
        except (OSError, ValueError):
            used = {}
    if used:
        print("\n  quota this month: " + ", ".join(f"{k}={v}" for k, v in used.items()),
              file=sys.stderr)


# ---------------------------------------------------------------- cli

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Search the web for images and download them.")
    p.add_argument("query", nargs="?", default="",
                   help="Search terms, company name, or icon name")
    p.add_argument("--logo", action="store_true",
                   help="Logo mode — treat query as company/domain, prefer SVG")
    p.add_argument("--icon", action="store_true",
                   help="Icon mode — Iconify SVG glyph for diagrams")
    p.add_argument("--stock", action="store_true",
                   help="Stock photo mode — Pixabay/Pexels/Unsplash")
    p.add_argument("--url", default=None, help="Direct URL download mode")
    p.add_argument("--reverse", default=None, metavar="URL",
                   help="Reverse image lookup (Google Lens via SerpAPI)")
    p.add_argument("--engine", default=None,
                   help="Force one engine: " + ", ".join(sorted(ENGINES))
                   + " | auto (default)")
    p.add_argument("--serpapi-engine", default="google_images",
                   help="SerpAPI backend: google_images|bing_images|yandex_images|"
                        "baidu_images|google_images_light")
    p.add_argument("--list-engines", action="store_true", help="Show channels and keys")
    p.add_argument("--dir", "-d", default="images", help="Output directory (default: images)")
    p.add_argument("--output", "-o", default=None, help="Explicit output path")
    p.add_argument("--num", "-n", type=int, default=1, help="Number of images (default: 1)")
    p.add_argument("--size", choices=["large", "medium", "icon"], help="Size filter")
    p.add_argument("--type", dest="type_filter",
                   choices=["photo", "clipart", "face", "lineart"], help="Type filter")
    p.add_argument("--typst", action="store_true", help="Print Typst figure code")
    p.add_argument("--width", default="80%", help="Typst image width (default: 80%%)")
    p.add_argument("--fit", default=None, choices=["cover", "contain", "stretch"],
                   help="Typst fit mode (use cover with --crop)")
    p.add_argument("--caption", default=None, help="Typst caption")
    p.add_argument("--max-width", type=int, default=1600,
                   help="Downscale to this width (default: 1600)")
    p.add_argument("--max-kb", type=int, default=2500,
                   help="Soft file-size budget in KB (default: 2500, 0 = off)")
    p.add_argument("--min-width", type=int, default=0, help="Reject narrower images")
    p.add_argument("--aspect", default=None, help="Crop to ratio, e.g. 16:9")
    p.add_argument("--crop", action="store_true", help="Centre-crop to --aspect")
    p.add_argument("--format", dest="fmt", default="auto",
                   choices=["auto", "jpeg", "png"], help="Output format (default: auto)")
    p.add_argument("--white-bg", action="store_true",
                   help="Flatten transparency onto white (default for photos)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    p.add_argument("--no-cache", action="store_true", help="Bypass the response cache")
    p.add_argument("--no-serpapi", action="store_true", help="Skip SerpAPI in auto ladder")
    p.add_argument("--no-manifest", action="store_true", help="Skip manifest sidecar")
    p.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout")
    p.add_argument("--verbose", "-v", action="store_true")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.errors = []
    args.keep_alpha = args.logo or args.icon or args.fmt == "png"
    if args.fmt == "auto" and (args.logo or args.icon):
        args.fmt = "png"  # brand marks and icons are line art: no JPEG ringing
    args.aspect_value = None
    if args.aspect:
        try:
            w, h = args.aspect.replace("x", ":").split(":")
            args.aspect_value = float(w) / float(h)
        except (ValueError, ZeroDivisionError):
            print("--aspect must look like 16:9", file=sys.stderr)
            sys.exit(2)

    if args.list_engines:
        for name in sorted(ENGINES):
            print(f"{name:10} {ENGINES[name].__doc__.strip().splitlines()[0]}")
        print("\nkeys: " + ", ".join(f"{k}={'set' if key(k) else 'missing'}"
                                     for k in SECRETS))
        return
    if not args.query and not (args.url or args.reverse):
        parser.error("query is required (or use --url / --list-engines)")

    saved: list[Candidate] = []

    # --- Reverse lookup mode ---
    if args.reverse:
        try:
            cards = eng_reverse(args.reverse, args.num, args)
        except EngineError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        for c in cards:
            print(f"{c.title or '(no title)'}\n  {c.page or c.url}")
        if not cards:
            print("Error: no visual matches", file=sys.stderr)
            sys.exit(1)
        if args.num:
            saved = _download_cards(cards, args, resolve_output(
                args.output, args.dir, args.query or "reverse-match"))
            report(saved, args)
        return

    # --- Direct URL mode ---
    if args.url:
        base = resolve_output(args.output, args.dir, args.query)
        result = fetch_raster(args.url, base, max_width=args.max_width,
                              max_kb=args.max_kb, aspect=args.aspect_value,
                              crop=args.crop, keep_alpha=args.keep_alpha,
                              white_bg=args.white_bg, min_width=args.min_width,
                              timeout=args.timeout, fmt=args.fmt)
        if not result:
            print(f"Error: failed to download {args.url}", file=sys.stderr)
            sys.exit(1)
        saved.append(Candidate(url=args.url, engine="direct", saved_path=result))

    # --- Logo mode ---
    elif args.logo:
        domain = resolve_domain(args.query)
        output = str(Path(resolve_output(args.output, args.dir, args.query,
                                         ext=".png")).with_suffix(""))
        if args.verbose:
            print(f"  domain: {domain}", file=sys.stderr)
        got = fetch_logo(domain, output + ".png", name=args.query,
                         timeout=args.timeout, fmt=args.fmt)
        if got:
            saved.append(Candidate(url=f"brand mark for {domain}", engine="logo",
                                   page=f"https://{domain}",
                                   license="trademark of the brand owner",
                                   saved_path=got))
        else:
            print("  no brand-mark source answered, searching the web",
                  file=sys.stderr)
            cards = search_candidates(f"{args.query} logo transparent png",
                                      args.num, args)
            saved = _download_cards(cards, args, resolve_output(
                args.output, args.dir, args.query))
            if not saved:
                print("Error: could not find logo", file=sys.stderr)
                sys.exit(1)

    # --- Icon mode ---
    elif args.icon:
        cards = search_icon(args.query, args.num, args)
        if not cards:
            print(f"Error: no icons matched '{args.query}'", file=sys.stderr)
            sys.exit(1)
        for card in cards[:args.num]:
            stem = Path(resolve_output(args.output, args.dir, args.query)).with_suffix("")
            target = str(stem) + ("" if args.num == 1 else f"_{len(saved) + 1}") + ".svg"
            got = fetch_svg(card.url, target)
            if got:
                saved.append(Candidate(url=card.url, engine="iconify",
                                       title=card.title, page=card.page,
                                       license=card.license, saved_path=got))
        if not saved:
            print("Error: icon download failed", file=sys.stderr)
            sys.exit(1)

    # --- Stock photo mode ---
    elif args.stock:
        cards = search_stock(args.query, args.num, args)
        saved = _download_cards(cards, args, resolve_output(
            args.output, args.dir, args.query))
        if not saved:
            print("Error: no stock images downloaded", file=sys.stderr)
            sys.exit(1)

    # --- Default: image search ---
    else:
        cards = search_candidates(args.query, args.num, args)
        if not cards:
            print(f"Error: no candidates for '{args.query}' "
                  f"({'; '.join(args.errors) or 'no engines answered'})",
                  file=sys.stderr)
            sys.exit(1)
        saved = _download_cards(cards, args, resolve_output(
            args.output, args.dir, args.query))
        if not saved:
            print(f"Error: no images downloaded ({len(cards)} candidates tried)",
                  file=sys.stderr)
            sys.exit(1)

    report(saved, args)


def _download_cards(cards: list[Candidate], args, base: str) -> list[Candidate]:
    """Download candidates and return the ones that were saved."""
    saved_paths = download_first([c.url for c in cards], args.num, base,
                                 candidates=cards, opt=args)
    keep = [c for c in cards if getattr(c, "saved_path", None) in saved_paths]
    return keep


if __name__ == "__main__":
    main()
