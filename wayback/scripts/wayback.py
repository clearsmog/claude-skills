#!/usr/bin/env python3
"""Web-archive helper: list distinct captures, fetch one as text, diff two versions.

  wayback.py list  <url> [--source all|ia,cc,pt] [--from YYYY[MMDD]] [--to YYYY[MMDD]] [--limit N]
  wayback.py save  <url>
  wayback.py fetch <url> <ref> [-o DIR]
  wayback.py diff  <url> <A> <B> [--start REGEX] [--end REGEX] [--line] [-o DIR]
  wayback.py history <url> [--source ..] [--from ..] [--to ..] [--min-chars 500] [--start ..] [--end ..] [--line] [-o DIR]

Sources: ia = Internet Archive Wayback Machine, cc = Common Crawl,
pt = Arquivo.pt; all three by default. A ref is a 14-digit timestamp (Wayback), `cc:<ts>` / `pt:<ts>`,
or a local .html/.txt file, so a page saved today diffs against any capture.
`history` diffs every distinct capture against the previous one, skipping empty
shells (text shorter than --min-chars after cropping). Stdlib only; run with `python3 -I`.
"""

import argparse, datetime, fnmatch, gzip, os, html, json, re, shutil, subprocess, sys, tempfile, time
import ssl, urllib.error, urllib.parse, urllib.request, zlib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

# Common Crawl asks for a real, descriptive User-Agent (commoncrawl.org/faq)
UA = "wayback-skill/1.1 (personal web-archive lookup CLI; python-urllib)"
CC_INDEX = "https://index.commoncrawl.org"
CC_DATA = "https://data.commoncrawl.org/"
CC_WORKERS = int(os.environ.get("WAYBACK_CC_WORKERS", 3))  # crawls looked up at once on data.commoncrawl.org
CC_DEFAULT_CRAWLS = 12  # ~1 year of crawls when no --from is given


def tls_refused(e):
    """A refused TLS handshake (archive.org does this to some networks) will not get
    better on a retry, unlike a timeout or a dropped connection."""
    return isinstance(e, ssl.SSLError) or isinstance(getattr(e, "reason", None), ssl.SSLError)


def get(url, tries=5, headers=None, raw=False):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, **(headers or {})}
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return (
                    data if raw else decode(data, r.headers.get("Content-Encoding", ""))
                )
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or i == tries - 1:
                raise
            wait, why = int(e.headers.get("Retry-After") or 5 * 2**i), f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            if i == tries - 1 or tls_refused(e):
                raise
            wait, why = 5 * 2**i, type(e).__name__
        print(f"{why}, retry in {wait}s ...", file=sys.stderr)
        time.sleep(wait)


def decode(data, encoding):
    # archived responses may still carry the original site's gzip/deflate encoding
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    if "deflate" in encoding:
        try:
            return zlib.decompress(data)
        except zlib.error:
            return zlib.decompress(data, -zlib.MAX_WBITS)
    return data


# ---------- capture listing: each returns rows (ref, timestamp, original, mime, length, digest)


def ia_captures(url, frm=None, to=None, limit=None):
    q = {
        "url": url,
        "output": "json",
        "collapse": "digest",
        "filter": "statuscode:200",
        "fl": "timestamp,original,mimetype,length,digest",
    }
    if frm:
        q["from"] = frm
    if to:
        q["to"] = to
    if limit:
        q["limit"] = f"-{limit}"
    rows = json.loads(
        get("https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(q))
        or b"[]"
    )
    return [(r[0], *r) for r in rows[1:]]


def pywb_rows(endpoint, url, frm=None, to=None, limit=None, tries=5):
    """CDX query against a pywb-style server (Common Crawl, Arquivo.pt): JSON lines."""
    q = {"url": url, "output": "json", "filter": "status:200"}
    if frm:
        q["from"] = frm
    if to:
        q["to"] = to
    if limit:
        q["limit"] = limit
    try:
        body = get(endpoint + "?" + urllib.parse.urlencode(q), tries=tries)
    except urllib.error.HTTPError as e:
        if e.code == 404:  # pywb answers 404 when there are no captures
            return []
        raise
    return [json.loads(l) for l in body.decode().splitlines() if l.strip()]


def pt_captures(url, frm=None, to=None, limit=None):
    rows = pywb_rows("https://arquivo.pt/wayback/cdx", url, frm, to)
    out = [
        (
            f"pt:{r['timestamp']}",
            r["timestamp"],
            r["url"],
            r.get("mime", ""),
            r.get("length", ""),
            r.get("digest", ""),
        )
        for r in rows
    ]
    return out[-limit:] if limit else out


_crawls = None
CC_CACHE = Path.home() / ".cache" / "wayback-skill" / "collinfo.json"


def _crawl_list():
    """collinfo.json lives on the index server, which goes down for hours: keep a disk copy
    (refreshed weekly, used stale on failure); with no copy, derive crawls from data.commoncrawl.org."""
    fresh = CC_CACHE.exists() and time.time() - CC_CACHE.stat().st_mtime < 7 * 86400
    if not fresh:
        try:
            data = get(CC_INDEX + "/collinfo.json", tries=2)
            json.loads(data)
            CC_CACHE.parent.mkdir(parents=True, exist_ok=True)
            CC_CACHE.write_bytes(data)
        except Exception as e:
            print(f"cc: collinfo.json unavailable ({e}); using fallback crawl list", file=sys.stderr)
    if CC_CACHE.exists():
        return json.loads(CC_CACHE.read_text())
    page = get(CC_DATA + "crawl-data/index.html").decode()
    out = []
    for cid in sorted(set(re.findall(r"CC-MAIN-(\d{4})-(\d{2})\b", page)), reverse=True):
        # the id names the ISO week the crawl ends in; crawls run about two weeks
        end = datetime.date.fromisocalendar(int(cid[0]), int(cid[1]), 7)
        out.append({"id": f"CC-MAIN-{cid[0]}-{cid[1]}", "from": str(end - datetime.timedelta(days=27)), "to": str(end)})
    return out


def cc_crawls(frm=None, to=None):
    """Crawls (newest first) whose date window overlaps [frm, to]."""
    global _crawls
    if _crawls is None:
        _crawls = _crawl_list()
    lo = (frm or "")[:8].ljust(8, "0")
    hi = (to or "9")[:8].ljust(8, "9")
    hits = [c for c in _crawls if c["to"][:10].replace("-", "") >= lo and c["from"][:10].replace("-", "") <= hi]
    if not frm:
        if len(hits) > CC_DEFAULT_CRAWLS:
            print(f"cc: searching the newest {CC_DEFAULT_CRAWLS} of {len(hits)} crawls; pass --from to go further back", file=sys.stderr)
        hits = hits[:CC_DEFAULT_CRAWLS]
    return hits


def surt(url):
    """SURT key as Common Crawl's index builds it (rules of the `surt` package, which is AGPL,
    so ported here): no scheme/fragment, host reversed without www, default port dropped,
    everything lowercased, trailing slash dropped except on the root, query params sorted."""
    u = urllib.parse.urlsplit(url if "://" in url else "http://" + url)
    host = re.sub(r"^www\d*\.", "", (u.hostname or "").rstrip("."))
    key = ",".join(reversed(host.split(".")))
    if u.port and u.port not in (80, 443):
        key += f":{u.port}"
    path = u.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    query = "&".join(sorted(u.query.split("&"))) if u.query else ""
    return (key + ")" + path + ("?" + query if query else "")).lower()


def _range(url, start, end):
    return get(url, headers={"Range": f"bytes={start}-{end}"}, raw=True)


def zipnum_rows(crawl, url):
    """Look a URL up in one crawl's ZipNum CDX on data.commoncrawl.org, without the index server:
    binary-search cluster.idx (sorted, ~100 MB) with Range reads, then gunzip the matching
    ~200 KB block(s). About 16 requests / 0.5 MB per crawl. `url/*` sweeps a prefix."""
    # the index only supports prefix lookups: search up to the first `*`, then filter the
    # rest of the pattern (e.g. `careers.x.com/job/*Risk*`) against each capture's URL
    head, star, tail = url.partition("*")
    prefix = bool(star)
    key = surt(head or "/")
    if prefix and head.endswith("/") and not key.endswith("/"):
        key += "/"
    pattern = "*" + tail.lower() if tail.strip("*") else None
    base = f"{CC_DATA}cc-index/collections/{crawl}/indexes/"
    idx = base + "cluster.idx"
    req = urllib.request.Request(idx, method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        size = int(r.headers["Content-Length"])
    lo, hi, win = 0, size, 16384
    while hi - lo > win:  # invariant: the first full line after lo has key < target
        mid = (lo + hi) // 2
        chunk = _range(idx, mid, mid + 4095)
        line = chunk.split(b"\n")[1] if chunk.count(b"\n") >= 2 else b""
        if line and line.split(b" ")[0].decode() < key:
            lo = mid
        else:
            hi = mid
    lines = _range(idx, lo, min(size, hi + win) - 1).decode(errors="replace").split("\n")
    lines = [l for l in (lines if lo == 0 else lines[1:]) if "\t" in l]
    start = max([i for i, l in enumerate(lines) if l.split(" ")[0] < key] or [0])

    def hit(k):
        return k.startswith(key) if prefix else k == key

    rows, blocks = [], 0
    for l in lines[start:]:
        _, fname, off, ln, _ = l.split("\t")
        if blocks and l.split(" ")[0] > key and not hit(l.split(" ")[0]):
            break  # the next block starts past our key
        blocks += 1
        if blocks > 20:
            print(f"cc: {crawl}: prefix spans >20 index blocks; truncated, narrow the prefix", file=sys.stderr)
            break
        text = gzip.decompress(_range(base + fname, int(off), int(off) + int(ln) - 1)).decode(errors="replace")
        for cdx in text.splitlines():
            k, ts, js = cdx.split(" ", 2)
            if hit(k):
                row = {"urlkey": k, "timestamp": ts, **json.loads(js)}
                if not pattern or fnmatch.fnmatch(row.get("url", "").lower(), pattern):
                    rows.append(row)
    return rows


_cc_seen = {}


def cc_rows(url, frm=None, to=None):
    def one(c):
        try:
            return zipnum_rows(c["id"], url)
        except Exception as e:  # one failing crawl should not sink the sweep
            print(f"cc: {c['id']} failed ({e}); skipped", file=sys.stderr)
            return []

    with ThreadPoolExecutor(max_workers=CC_WORKERS) as pool:
        rows = [r for rs in pool.map(one, cc_crawls(frm, to)) for r in rs]
    lo, hi = (frm or "0")[:14].ljust(14, "0"), (to or "9")[:14].ljust(14, "9")
    rows = [r for r in rows if r.get("status") == "200" and lo <= r["timestamp"] <= hi]
    rows = sorted(rows, key=lambda r: r["timestamp"])
    _cc_seen.update((r["timestamp"], r) for r in rows)  # lets `history` fetch without a second lookup
    return rows


def cc_captures(url, frm=None, to=None, limit=None):
    out = [
        (
            f"cc:{r['timestamp']}",
            r["timestamp"],
            r["url"],
            r.get("mime", ""),
            r.get("length", ""),
            r.get("digest", ""),
        )
        for r in cc_rows(url, frm, to)
    ]
    return out[-limit:] if limit else out


SOURCES = {"ia": ia_captures, "cc": cc_captures, "pt": pt_captures}


def captures(url, frm=None, to=None, limit=None, sources=tuple(SOURCES)):
    """Distinct captures across sources, oldest first. All three archives use the base32
    SHA-1 of the payload as digest, so the same bytes captured by two archives collapse."""
    def one(s):
        try:
            return SOURCES[s](url, frm, to, limit)
        except Exception as e:
            if len(sources) == 1:
                raise
            print(f"{s}: failed ({e}); continuing with the other sources", file=sys.stderr)
            return []

    # different hosts, so query them at once: a down archive.org retrying for minutes
    # no longer delays the others. map() keeps source order, so ties keep the Wayback ref
    with ThreadPoolExecutor(max_workers=len(sources)) as pool:
        rows = [r for rs in pool.map(one, sources) for r in rs]
    rows.sort(key=lambda r: r[1])
    seen, out = set(), []
    for r in rows:
        if r[5] and r[5] in seen:
            continue
        seen.add(r[5])
        out.append(r)
    return out[-limit:] if limit else out


def parse_sources(s):
    names = list(SOURCES) if s == "all" else s.split(",")
    if bad := [n for n in names if n not in SOURCES]:
        sys.exit(f"unknown source {bad}; choose from {','.join(SOURCES)} or all")
    return names


# ---------- fetching one capture


def cc_fetch(url, ts):
    """Find the record in the crawl(s) covering ts, then range-read it from the WARC."""
    rows = [_cc_seen[ts]] if ts in _cc_seen else [r for r in cc_rows(url, ts[:8], ts[:8]) if r["timestamp"] == ts]
    if not rows:
        sys.exit(f"cc: no 200 record for {url} at {ts}; take refs from `list --source cc`")
    r = rows[0]
    start, n = int(r["offset"]), int(r["length"])
    rec = gzip.decompress(
        get(
            CC_DATA + r["filename"],
            headers={"Range": f"bytes={start}-{start + n - 1}"},
            raw=True,
        )
    )
    if rec.startswith(b"WARC/"):
        warc_head, _, rest = rec.partition(b"\r\n\r\n")
    else:  # crawls 2008-2012 are ARC: a one-line header, then the HTTP response
        warc_head, _, rest = rec.partition(b"\n")
    http_head, _, body = rest.partition(b"\r\n\r\n")
    # cap is 1 MiB before CC-MAIN-2025-13, 5 MiB after; the WARC header was unreliable until 2019-30
    if b"WARC-Truncated" in warc_head or r.get("truncated") or len(body) == 1048576:
        print(
            f"warn cc:{ts}: record truncated by the crawler (size cap); text is incomplete",
            file=sys.stderr,
        )
    enc = re.search(rb"(?im)^content-encoding:\s*(\S+)", http_head)
    return decode(body, enc.group(1).decode() if enc else "")


def load(url, ref):
    if Path(ref).exists():
        raw = Path(ref).read_bytes()
        return (
            Path(ref).stem,
            raw,
            (raw.decode("utf-8", "ignore") if ref.endswith(".txt") else to_text(raw)),
        )
    src, _, ts = ref.rpartition(":")
    if src == "cc":
        raw = cc_fetch(url, ts)
    elif src == "pt":
        raw = get(f"https://arquivo.pt/wayback/{ts}id_/{url}")
    elif src in ("", "ia"):
        raw = get(f"https://web.archive.org/web/{ts}id_/{url}")
    else:
        sys.exit(f"bad ref {ref!r}: use <ts>, cc:<ts>, pt:<ts> or a local file")
    name = ts if src in ("", "ia") else f"{src}-{ts}"  # no ':' in file names
    return name, raw, to_text(raw)


class _Text(HTMLParser):
    BLOCK = {
        "p",
        "li",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "tr",
        "section",
        "article",
        "ul",
        "ol",
    }

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def to_text(raw):
    p = _Text()
    p.feed(raw.decode("utf-8", errors="ignore"))
    if raw.count(b"\x00") or raw[:200].decode("utf-8", "replace").count("�") > 20:
        print(
            "warn: capture looks binary/compressed (brotli?), text is unusable",
            file=sys.stderr,
        )
    lines = (
        re.sub(r"\s+", " ", l).strip()
        for l in html.unescape("".join(p.out)).splitlines()
    )
    return "\n".join(l for l in lines if l) + "\n"


def crop(text, start, end):
    """Cut text to the body between two regexes; say which one did not match."""
    warn = []
    if start:
        if m := re.search(start, text, re.M):
            text = text[m.start() :]
        else:
            warn.append("--start not found, kept from top")
    if end:
        if m := re.search(end, text, re.M):
            text = text[: m.start()]
        else:
            warn.append("--end not found, kept to bottom")
    return text, "; ".join(warn)


def save(url, tries=3):
    """Ask Save Page Now for a fresh capture; return (timestamp, archived_url, fresh)."""
    started, final = time.strftime("%Y%m%d%H%M%S", time.gmtime()), ""
    for i in range(tries):
        try:
            req = urllib.request.Request(
                "https://web.archive.org/save/" + url, headers={"User-Agent": UA}
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                final = r.headers.get("Content-Location") or r.geturl()
            break
        except urllib.error.HTTPError as e:
            # SPN answers 520/523 when the target refuses the crawler; 429 when we are throttled
            if e.code not in (429, 500, 502, 503, 504) or i == tries - 1:
                print(
                    f"save failed: HTTP {e.code}; falling back to the latest existing capture",
                    file=sys.stderr,
                )
                final = ""
                break
            wait = int(e.headers.get("Retry-After") or 20 * 2**i)
        except (urllib.error.URLError, TimeoutError) as e:
            if i == tries - 1 or tls_refused(e):
                print(
                    f"save failed: {type(e).__name__}; falling back to the latest existing capture",
                    file=sys.stderr,
                )
                final = ""
                break
            wait = 20 * 2**i
        print(f"retry save in {wait}s ...", file=sys.stderr)
        time.sleep(wait)
    if m := re.search(r"/web/(\d{14})", final):
        ts = m.group(1)
    else:
        try:
            rows = ia_captures(url, limit=1)
        except (urllib.error.URLError, TimeoutError) as e:
            sys.exit(
                f"archive.org is unreachable from this network ({type(e).__name__}): nothing "
                "was saved. Save the page with archive.ph in Chrome instead."
            )
        if not rows:
            sys.exit("no capture exists and Save Page Now did not create one")
        ts = rows[-1][1]
    return ts, f"https://web.archive.org/web/{ts}/{url}", ts >= started[:12]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list")
    l.add_argument("url")
    l.add_argument("--limit", type=int)
    s = sub.add_parser("save")
    s.add_argument("url")
    f = sub.add_parser("fetch")
    f.add_argument("url")
    f.add_argument("ts")
    f.add_argument("-o", default=".")
    d = sub.add_parser("diff")
    d.add_argument("url")
    d.add_argument("a")
    d.add_argument("b")
    h = sub.add_parser("history")
    h.add_argument("url")
    h.add_argument("--min-chars", type=int, default=500)
    for x in (l, h):
        x.add_argument("--source", default="all", help="all (default), or ia, cc, pt, or a comma list")
        x.add_argument("--from", dest="frm")
        x.add_argument("--to")
    for x in (d, h):
        x.add_argument("--start")
        x.add_argument("--end")
        x.add_argument("--line", action="store_true")
        x.add_argument("-o")
    a = ap.parse_args()
    if a.cmd == "history" and "*" in a.url:
        ap.error("history takes one page URL; use `list` for a prefix sweep")

    if a.cmd == "list":
        rows = captures(a.url, a.frm, a.to, a.limit, parse_sources(a.source))
        for ref, ts, orig, mime, length, _ in rows:
            print(ref, mime, length, orig, sep="\t")
        print(f"{len(rows)} distinct 200 captures", file=sys.stderr)
    elif a.cmd == "save":
        ts, archived, fresh = save(a.url)
        print(ts, archived, sep="\t")
        if not fresh:
            print(
                f"warn: no new capture was made; {ts} is the latest existing one",
                file=sys.stderr,
            )
    elif a.cmd == "fetch":
        out = Path(a.o)
        out.mkdir(parents=True, exist_ok=True)
        name, raw, text = load(a.url, a.ts)
        (out / f"{name}.html").write_bytes(raw)
        (out / f"{name}.txt").write_text(text)
        print(out / f"{name}.txt")
    else:
        out = Path(a.o) if a.o else Path(tempfile.mkdtemp(prefix="wayback-"))
        out.mkdir(parents=True, exist_ok=True)
        refs = (
            [a.a, a.b]
            if a.cmd == "diff"
            else [
                r[0]
                for r in captures(a.url, a.frm, a.to, sources=parse_sources(a.source))
            ]
        )

        def grab(ref):
            # full text is cached in the output dir, so re-running with a fixed --start/--end costs no fetch
            cache = out / f"{ref.replace(':', '-')}.full.txt"
            if not Path(ref).exists() and cache.exists():
                return cache.name.removesuffix(".full.txt"), cache.read_text()
            name, raw, text = load(a.url, ref)
            (out / f"{name}.full.txt").write_text(text)
            return name, text

        with ThreadPoolExecutor(max_workers=4) as pool:
            texts = list(pool.map(grab, refs))
        kept, misses = [], 0
        for name, full in texts:
            text, warn = crop(full, a.start, a.end)
            if warn:
                misses += 1
                print(f"warn {name}: {warn}", file=sys.stderr)
            if a.cmd == "history" and len(text) < a.min_chars:
                print(f"skip {name}: {len(text)} chars (empty shell?)", file=sys.stderr)
                continue
            p = out / f"{name}.txt"
            p.write_text(text)
            kept.append(p)
        if misses or (a.cmd == "history" and len(kept) < len(texts) // 2):
            print(
                f"check --start/--end against the uncropped {out}/*.full.txt; re-running reuses them",
                file=sys.stderr,
            )
        same = 0
        for old, new in zip(kept, kept[1:]):
            d = diff_text(old, new, a.line)
            if not d:
                same += 1
                continue
            if a.cmd == "history":
                print(f"\n===== {old.stem} -> {new.stem} =====")
            sys.stdout.write(d)
        if same:
            print(
                f"{same} consecutive pair(s) identical after cropping", file=sys.stderr
            )
        print(f"{len(kept)} texts saved in {out}", file=sys.stderr)


def diff_text(old, new, line):
    if old.read_text() == new.read_text():
        return ""
    if shutil.which("git"):
        args = ["git", "--no-pager", "diff", "--no-index", "--no-color"] + (
            [] if line else ["--word-diff=plain"]
        )
        return subprocess.run(
            args + [str(old), str(new)], capture_output=True, text=True
        ).stdout
    import difflib

    return "".join(
        difflib.unified_diff(
            old.read_text().splitlines(True),
            new.read_text().splitlines(True),
            str(old),
            str(new),
        )
    )


if __name__ == "__main__":
    main()
