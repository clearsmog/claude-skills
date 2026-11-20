#!/usr/bin/env python3
"""Web-archive helper: list distinct captures, fetch one as text, diff two versions.

  wayback.py list   <url>... [--source all|ia,cc,pt] [--from YYYY[MMDD]] [--to YYYY[MMDD]]
                    [--limit N] [--domain] [--json] [--fresh]
  wayback.py save   <url>
  wayback.py fetch  <url> [ref] [-o DIR] [--main] [--engine ..]
  wayback.py diff   <url> <A> <B> [--start REGEX] [--end REGEX] [--line] [--stat] [-o DIR]
  wayback.py history <url> [--source ..] [--from ..] [--to ..] [--min-chars 300] [--max N] [--raw] [--engine ..]
                    [--start ..] [--end ..] [--line] [--stat] [-o DIR]

Sources: ia = Internet Archive Wayback Machine, cc = Common Crawl,
pt = Arquivo.pt, gh = ghostarchive, mg = Megalodon and uk = UK Web Archive (mg/uk: listing only);
all by default. A ref is a 14-digit timestamp (Wayback), `cc:<ts>` / `pt:<ts>` / `gh:<id>`,
`live` (the page now), or a local .html/.pdf file or .txt/.md text,
so today's page diffs against any capture.
`--domain` lists one capture per URL for a whole host (site inventory); wildcards (`host/path*`)
work on ia and cc only. `history` diffs every distinct capture against the previous one, skipping
empty shells (text shorter than --min-chars after cropping). Stdlib only; run with `python3 -I`.
"""

import argparse, datetime, email.utils, fnmatch, gzip, hashlib, math, os, html, json, re, shutil, subprocess, sys, tempfile, time
import ssl, urllib.error, urllib.parse, urllib.request, zlib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

# Common Crawl asks for a real, descriptive User-Agent (commoncrawl.org/faq)
UA = "wayback-skill/1.2 (personal web-archive lookup CLI; python-urllib)"
CC_INDEX = "https://index.commoncrawl.org"
CC_DATA = "https://data.commoncrawl.org/"
CC_WORKERS = int(os.environ.get("WAYBACK_CC_WORKERS", 3))  # crawls looked up at once on data.commoncrawl.org
CC_DEFAULT_CRAWLS = 12  # ~1 year of crawls when no --from is given

CACHE = Path.home() / ".cache" / "wayback-skill"
CACHE_TTL = int(os.environ.get("WAYBACK_CACHE_TTL", 1800))  # capture listings, seconds
IA_BLOCK_TTL = int(os.environ.get("WAYBACK_IA_BLOCK_TTL", 900))  # how long to skip a 429-blocked archive.org
FRESH = False  # --fresh: ignore cached listings
MAX_WAIT = 60  # longest back-off; a 503 with Retry-After: 3600 once stalled a command for an hour


def retry_after(headers, default):
    """Seconds to wait per Retry-After (delta-seconds or an HTTP date), capped at MAX_WAIT."""
    v = (headers or {}).get("Retry-After") if headers is not None else None
    try:
        secs = int(v)
    except (TypeError, ValueError):
        try:
            secs = email.utils.parsedate_to_datetime(v).timestamp() - time.time()
        except (TypeError, ValueError, IndexError):
            secs = default
    return int(max(0, min(secs, MAX_WAIT)))


def tls_refused(e):
    """A refused TLS handshake (archive.org does this to some networks) will not get better
    on a retry. A connection cut mid-read is different: arquivo.pt raises SSL
    UNEXPECTED_EOF when four history fetches overlap, and that one retries fine."""
    err = e if isinstance(e, ssl.SSLError) else getattr(e, "reason", None)
    if not isinstance(err, ssl.SSLError):
        return False
    return "EOF" not in f"{getattr(err, 'reason', '')} {err}".upper()


def get(url, tries=5, headers=None, raw=False, with_headers=False, context=None):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, **(headers or {})}
            )
            opened = urllib.request.urlopen(req, timeout=60, context=context) if context else urllib.request.urlopen(req, timeout=60)
            with opened as r:
                data = r.read()
                body = data if raw else decode(data, r.headers.get("Content-Encoding", ""))
                return (body, dict(r.headers)) if with_headers else body
        except urllib.error.HTTPError as e:
            # 429 means "you are being rate-limited right now": one short wait, then give
            # up. Honouring a 120 s Retry-After would stall the whole command.
            if e.code == 429:
                if i >= 1:
                    raise
                wait, why = min(retry_after(e.headers, 5), 5), "HTTP 429"
            elif e.code not in (500, 502, 503, 504) or i == tries - 1:
                raise
            else:
                wait, why = retry_after(e.headers, 5 * 2**i), f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            if i == tries - 1 or tls_refused(e):
                raise
            wait, why = 2 * 2**i, type(e).__name__  # a reset connection needs no long cool-off
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


# ---------- disk caches: listings are re-queried constantly during research, and the
# ---------- archives rate-limit; a short TTL turns the second lookup of a URL into 0 s.


def cache_path(*parts):
    key = hashlib.sha1("\x00".join(str(p) for p in parts).encode()).hexdigest()[:16]
    return CACHE / "cdx" / f"{key}.json"


def cached(key_parts, fn, ttl=CACHE_TTL):
    """ttl=None keeps the entry for good: a finished Common Crawl crawl never changes."""
    p = cache_path(*key_parts)
    if p.exists() and not FRESH and (ttl is None or time.time() - p.stat().st_mtime < ttl):
        try:
            return [tuple(r) if isinstance(r, list) else r for r in json.loads(p.read_text())]
        except (ValueError, OSError):
            pass
    rows = fn()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps([list(r) if isinstance(r, tuple) else r for r in rows]))
        tmp.replace(p)
    except (OSError, TypeError):
        pass
    return rows


def ia_blocked_until():
    p = CACHE / "ia-blocked"
    try:
        return float(p.read_text().strip() or 0)
    except (OSError, ValueError):
        return 0.0


def mark_ia_blocked(why):
    """archive.org answers 429 with a Retry-After we cannot wait out (seen 2026-11-18:
    every CDX and replay URL). Skip ia for a while instead of burning a minute per call."""
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / "ia-blocked").write_text(str(time.time() + IA_BLOCK_TTL))
    except OSError:
        pass
    print(
        f"ia: archive.org is rate-limiting this network ({why}); skipping ia for "
        f"{IA_BLOCK_TTL // 60} min (WAYBACK_IA_BLOCK_TTL=0 disables this)",
        file=sys.stderr,
    )


# ---------- capture listing: each returns rows (ref, timestamp, original, mime, length, digest)


def ia_captures(url, frm=None, to=None, limit=None, domain=False):
    q = {
        "url": url,
        "output": "json",
        "collapse": "urlkey" if domain else "digest",  # domain = site inventory: one per URL
        "filter": "statuscode:200",
        "fl": "timestamp,original,mimetype,length,digest",
    }
    if domain:
        q["matchType"] = "domain"
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


def pt_captures(url, frm=None, to=None, limit=None, domain=False):
    # Arquivo.pt runs pywb and matches `url` exactly: wildcards and matchType are ignored,
    # so a prefix sweep there would silently return the host root. Say so instead.
    if domain or "*" in url:
        print("pt: Arquivo.pt matches URLs exactly (no wildcard/domain sweep); skipped", file=sys.stderr)
        return []
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
CC_CACHE = CACHE / "collinfo.json"


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


def cc_ttl(crawl):
    """A crawl's index is final some weeks after the crawl ends; cache those lookups for good."""
    end = crawl.get("to", "")[:10]
    done = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    return None if end and end < done else CACHE_TTL


def cc_rows(url, frm=None, to=None, domain=False):
    if domain and "*" not in url:
        url = url.rstrip("/") + "/*"

    def one(c):
        def look():
            return zipnum_rows(c["id"], url)

        try:
            return cached(("cc", c["id"], url), look, ttl=cc_ttl(c))
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


def cc_captures(url, frm=None, to=None, limit=None, domain=False):
    out = [
        (
            f"cc:{r['timestamp']}",
            r["timestamp"],
            r["url"],
            r.get("mime", ""),
            r.get("length", ""),
            r.get("digest", ""),
        )
        for r in cc_rows(url, frm, to, domain)
    ]
    return out[-limit:] if limit else out


def _ts_window(frm, to):
    return (frm or "0")[:14].ljust(14, "0"), (to or "9")[:14].ljust(14, "9")


def _url_match(url, query, domain=False):
    """Does a listed URL answer the query? Compared as SURT keys, so scheme, www and a
    trailing slash do not matter; `host/path*` is a prefix, --domain is the whole host."""
    if domain:
        host = urllib.parse.urlsplit(query if "://" in query else "http://" + query).hostname or query
        key = surt(host).split(")")[0]
        got = surt(url).split(")")[0]
        return got == key or got.startswith(key + ",")
    head, star, _ = query.partition("*")
    return surt(url).startswith(surt(head).rstrip("/")) if star else surt(url) == surt(query)


GH_PAGES = int(os.environ.get("WAYBACK_GH_PAGES", 5))  # ~20 hits a page; the search is by substring
GH_ROW = re.compile(
    r'<a href="/archive/(\w+)">([^<]+)</a></td><td>([^<]+?)\s*</td>', re.S
)


def gh_captures(url, frm=None, to=None, limit=None, domain=False):
    """ghostarchive.org: on-demand saves (it renders JavaScript, like archive.ph). Its search
    matches by substring, so hits for sub-pages come back too and are filtered here."""
    # substring search: drop the scheme, or "http://" never finds an "https://" save
    term = re.sub(r"^[a-z]+://", "", url.split("*")[0], flags=re.I)
    if domain:
        term = term.split("/")[0]
    lo, hi = _ts_window(frm, to)
    out, seen = [], set()
    for page in range(GH_PAGES):
        q = {"term": term} | ({"page": page} if page else {})
        body = get("https://ghostarchive.org/search?" + urllib.parse.urlencode(q), tries=2).decode("utf-8", "replace")
        for gid, orig, date in GH_ROW.findall(body):
            orig = html.unescape(orig.strip())
            try:
                ts = email.utils.parsedate_to_datetime(date.strip()).strftime("%Y%m%d%H%M%S")
            except (TypeError, ValueError):
                continue
            if gid in seen or not _url_match(orig, url, domain) or not lo <= ts <= hi:
                continue
            seen.add(gid)
            out.append((f"gh:{gid}", ts, orig, "text/html", "", ""))
        if "Next Page" not in body:
            break
    else:
        print(f"gh: stopped after {GH_PAGES} result pages (WAYBACK_GH_PAGES raises it)", file=sys.stderr)
    out.sort(key=lambda r: r[1])
    return out[-limit:] if limit else out


MG_LINK = re.compile(r'href="(https://megalodon\.jp/(\d{4})-(\d{4})-(\d{4})-(\d{2})/([^"]+))"')


def mg_captures(url, frm=None, to=None, limit=None, domain=False):
    """Megalodon (ウェブ魚拓): strong on Japanese pages. Listing only: its replay answers
    scripts with an "access increase" error page, so a capture opens in Chrome."""
    if domain or "*" in url:
        print("mg: Megalodon lists one exact URL; skipped for wildcard/domain", file=sys.stderr)
        return []
    target = url if "://" in url else "http://" + url
    body = get("https://megalodon.jp/?url=" + urllib.parse.quote(target, safe=""), tries=2).decode("utf-8", "replace")
    lo, hi = _ts_window(frm, to)
    out, seen = [], set()
    for link, y, md, hm, sec, orig in MG_LINK.findall(body):
        ts = y + md + hm + sec
        if link in seen or not _url_match(html.unescape(orig), url) or not lo <= ts <= hi:
            continue
        seen.add(link)
        out.append((f"mg:{ts}", ts, link, "text/html", "", ""))
    out.sort(key=lambda r: r[1])
    return out[-limit:] if limit else out


UKWA = "https://www.webarchive.org.uk/archive/"


def uk_captures(url, frm=None, to=None, limit=None, domain=False):
    """UK Web Archive (British Library): .uk sites since 2004. Listing only in practice:
    legal-deposit captures replay in UK reading rooms, so they prove a page existed on a
    date but give no text here."""
    q = url.rstrip("/") + "/*" if domain and "*" not in url else url
    rows = pywb_rows(UKWA + "cdx", q, frm, to, tries=2)
    out = [
        (f"uk:{r['timestamp']}", r["timestamp"], r["url"], r.get("mime", ""), r.get("length", ""), r.get("digest", ""))
        for r in rows
    ]
    if out and (blocked := sum(r.get("access") == "block" for r in rows)):
        print(f"uk: {blocked} of {len(rows)} captures are reading-room only", file=sys.stderr)
    return out[-limit:] if limit else out


SOURCES = {"ia": ia_captures, "cc": cc_captures, "pt": pt_captures,
           "gh": gh_captures, "mg": mg_captures, "uk": uk_captures}
LIST_ONLY = {"mg", "uk"}  # captures are listed, but their text cannot be fetched by a script


def fetchable(names):
    return [n for n in names if n not in LIST_ONLY]


def captures(url, frm=None, to=None, limit=None, sources=tuple(SOURCES), domain=False):
    """Distinct captures across sources, oldest first. Wayback, CC and Arquivo.pt use the base32
    SHA-1 of the payload as digest, so the same bytes captured by two archives collapse."""
    if domain and url.startswith(("http://", "https://")):
        url = urllib.parse.urlsplit(url).hostname or url

    def one(s):
        if s == "ia" and (until := ia_blocked_until()) > time.time():
            print(
                f"ia: skipped, rate-limited until {time.strftime('%H:%M', time.localtime(until))} "
                "(WAYBACK_IA_BLOCK_TTL=0 disables this)",
                file=sys.stderr,
            )
            return []
        try:
            def look():
                return SOURCES[s](url, frm, to, limit, domain)

            return cached((s, url, frm, to, limit, domain), look)
        except urllib.error.HTTPError as e:
            if s == "ia" and e.code in (429, 403) and IA_BLOCK_TTL:
                mark_ia_blocked(f"HTTP {e.code}")
            if len(sources) == 1:
                sys.exit(
                    f"{s}: {e}; retry later, or take the other archives with --source cc / --source pt"
                )
            print(f"{s}: failed ({e}); continuing with the other sources", file=sys.stderr)
            return []
        except Exception as e:
            if s == "ia" and IA_BLOCK_TTL and isinstance(e, urllib.error.URLError) and tls_refused(e):
                mark_ia_blocked("TLS handshake refused")
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


# ---------- URL discovery and full-text search: the two archives' own search APIs,
# ---------- plus the two free URL feeds. These answer "I do not know the URL" and
# ---------- "what did this host ever have", which a CDX lookup cannot.


def arquivo_find(query, site=None, frm=None, to=None, limit=20):
    """Arquivo.pt full-text search. Rows: (timestamp, mime, original URL, archive URL)."""
    q = {"q": query, "maxItems": min(limit, 50)}
    if site:
        q["siteSearch"] = site
    if frm:
        q["from"] = frm
    if to:
        q["to"] = to
    url = "https://arquivo.pt/textsearch?" + urllib.parse.urlencode(q)
    rows, seen = [], set()
    while url and len(rows) < limit:
        data = json.loads(get(url))
        for it in data.get("response_items", []):
            key = (it.get("originalURL"), it.get("tstamp"))
            if key in seen or not it.get("originalURL"):
                continue
            seen.add(key)
            rows.append(
                (
                    it.get("tstamp", ""),
                    it.get("mimeType", ""),
                    it.get("originalURL", ""),
                    it.get("linkToArchive") or f"https://arquivo.pt/wayback/{it.get('tstamp', '')}/{it.get('originalURL', '')}",
                )
            )
        nxt = data.get("next_page")
        url = nxt if isinstance(nxt, str) and len(rows) < limit else None
    return rows[:limit]


def otx_urls(host, limit=200):
    """AlienVault OTX url_list: URLs seen against a domain, including long-dead ones."""
    body = get(
        "https://otx.alienvault.com/api/v1/indicators/domain/"
        f"{urllib.parse.quote(host)}/url_list?limit={min(limit, 500)}"
    )
    return [it["url"] for it in json.loads(body).get("url_list", []) if it.get("url")]


def urlscan_urls(host, limit=100):
    """urlscan.io search: keyless, metadata only (the rendered DOM needs a free API key)."""
    body = get(
        "https://urlscan.io/api/v1/search/?q="
        + urllib.parse.quote(f"domain:{host}")
        + f"&size={min(limit, 100)}"
    )
    out = []
    for r in json.loads(body).get("results", []):
        url = (r.get("page") or {}).get("url") or (r.get("task") or {}).get("url")
        if url:
            out.append(url)
    return out


# email-tracking and asset URLs dominate URL feeds (OTX is a threat-intel list) and are
# useless as archive targets: one click-tracking pixel per recipient
JUNK_URL = re.compile(
    r"/(unsubscribe|emailpreference|listunsubscribeheader|track|tracking|click|optout|opt-out)"
    r"[a-z]*(/|\?|$)|[?&](utm_[a-z]+|gclid|fbclid)=|\.(gif|png|jpe?g|svg|css|js|woff2?)$",
    re.I,
)


def _url_shape(url):
    """Host + path with long opaque tokens blanked, so 500 tracking links collapse to one."""
    u = urllib.parse.urlsplit(url)
    return (u.netloc.lower(), re.sub(r"[A-Za-z0-9_\-]{16,}", "*", u.path))


def discover(host, sources, limit, everything=False):
    """URLs for a host from the free feeds, deduped, as (url, source)."""
    out, seen = [], set()
    for name in sources:
        fn = {"otx": otx_urls, "urlscan": urlscan_urls}[name]
        try:
            urls = cached(("discover", name, host, limit), lambda: [(u,) for u in fn(host, limit)])
        except Exception as e:
            print(f"{name}: failed ({e}); continuing", file=sys.stderr)
            continue
        shapes = set()
        for (u,) in urls:
            if u in seen or (not everything and JUNK_URL.search(u)):
                continue
            shape = _url_shape(u)
            if shape in shapes:
                continue
            seen.add(u)
            shapes.add(shape)
            out.append((u, name))
    # clean, shallow, query-free URLs first: a product page beats a SAML callback
    out.sort(key=lambda r: (bool(urllib.parse.urlsplit(r[0]).query),
                            urllib.parse.urlsplit(r[0]).path.count("/"), r[0]))
    return out[:limit]


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
    ctype = re.search(rb"(?im)^content-type:\s*([^\r\n]+)", http_head)
    body = decode(body, enc.group(1).decode() if enc else "")
    return body, (ctype.group(1).decode() if ctype else "")


def warc_page(data, url):
    """(body, content type) of the page's own response record in an uncompressed WARC;
    falls back to the first HTML response (ghostarchive saves the page plus its assets)."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    want, first, pos = surt(url), None, 0
    while (start := data.find(b"WARC/1.", pos)) != -1:
        head_end = data.find(b"\r\n\r\n", start)
        if head_end == -1:
            break
        head = data[start:head_end].decode("latin-1")
        m = re.search(r"(?im)^content-length:\s*(\d+)", head)
        n = int(m.group(1)) if m else 0
        block = data[head_end + 4 : head_end + 4 + n]
        pos = head_end + 4 + n
        if not re.search(r"(?im)^warc-type:\s*response", head):
            continue
        http_head, _, body = block.partition(b"\r\n\r\n")
        ct = re.search(rb"(?im)^content-type:\s*([^\r\n]+)", http_head)
        ctype = ct.group(1).decode("latin-1") if ct else ""
        enc = re.search(rb"(?im)^content-encoding:\s*(\S+)", http_head)
        body = decode(body, enc.group(1).decode() if enc else "")
        uri = re.search(r"(?im)^warc-target-uri:\s*<?([^\r\n>]+)", head)
        if uri and surt(uri.group(1)) == want:
            return body, ctype
        if first is None and "html" in ctype.lower():
            first = (body, ctype)
    if first:
        return first
    sys.exit("gh: no HTML response in the archive's WARC")


def gh_fetch(url, gid):
    page = get(f"https://ghostarchive.org/archive/{gid}", tries=2).decode("utf-8", "replace")
    m = re.search(r'<replay-web-page[^>]*\ssource="([^"]+\.warc(?:\.gz)?)"', page)
    if not m:  # older saves replay through an iframe that does not answer scripts
        sys.exit(f"gh:{gid} is an older ghostarchive save without a WARC; open https://ghostarchive.org/archive/{gid} in Chrome")
    return warc_page(get(urllib.parse.urljoin("https://ghostarchive.org/", m.group(1)), raw=True), url)


def load(url, ref, engine=None):
    """Return (name, raw bytes, full text, main text or None, links) for a capture ref
    or a local file."""
    if Path(ref).exists():
        raw = Path(ref).read_bytes()
        if Path(ref).suffix.lower() in TEXT_SUFFIXES:
            # already text (`cf text` output, a pasted JD): parsing it as HTML joined every
            # line into one and ate anything in angle brackets
            text = _decode(raw, "utf-8")
            text = text if text.endswith("\n") or not text else text + "\n"
            return Path(ref).stem, raw, text, (text if engine else None), []
        return Path(ref).stem, raw, *_as_text(raw, url, "", engine)
    if ref == "live":
        return live_page(url, engine)
    src, _, ts = ref.rpartition(":")
    ctype = ""
    if src == "cc":
        raw, ctype = cc_fetch(url, ts)
    elif src == "pt":
        raw, hdrs = get(f"https://arquivo.pt/wayback/{ts}id_/{url}", with_headers=True)
        ctype = hdrs.get("Content-Type", "")
    elif src == "gh":
        raw, ctype = gh_fetch(url, ts)
    elif src == "mg":
        sys.exit(
            f"mg: Megalodon serves its copies to browsers only; open it in Chrome: "
            f"https://megalodon.jp/?url={urllib.parse.quote(url if '://' in url else 'http://' + url, safe='')}"
        )
    elif src == "uk":
        page = f"https://www.webarchive.org.uk/wayback/archive/{ts}/{url}"
        try:
            raw, hdrs = get(f"{UKWA}{ts}id_/{url}", tries=2, with_headers=True)
            ctype = hdrs.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code not in (451, 403):
                raise
            sys.exit(
                f"uk: capture {ts} is legal deposit (HTTP {e.code}): it can only be read in a UK "
                f"legal deposit library reading room. It does show the page existed then: {page}"
            )
    elif src in ("", "ia"):
        raw, hdrs = get(f"https://web.archive.org/web/{ts}id_/{url}", with_headers=True)
        ctype = hdrs.get("Content-Type", "")
    else:
        sys.exit(f"bad ref {ref!r}: use <ts>, cc:/pt:/uk:/mg:<ts>, gh:<id>, live, or a local file")
    name = ts if src in ("", "ia") else f"{src}-{ts}"  # no ':' in file names
    return name, raw, *_as_text(raw, url, ctype, engine)


TEXT_SUFFIXES = {".txt", ".md", ".text"}
CHALLENGE = re.compile(rb"_cf_chl_opt|challenge-platform|<title>\s*Just a moment|cf-browser-verification", re.I)


def keychain_context():
    """macOS: /etc/ssl/cert.pem, which Python reads, lags the system roots (example.com's
    SSL.com 2022 root was missing on 2026-11-19 while curl, on the Keychain, was fine)."""
    if not shutil.which("security"):
        return None
    out = subprocess.run(
        ["security", "find-certificate", "-a", "-p",
         "/System/Library/Keychains/SystemRootCertificates.keychain"],
        capture_output=True, text=True,
    )
    if out.returncode or "BEGIN CERTIFICATE" not in out.stdout:
        return None
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cadata=out.stdout)
    return ctx


def live_page(url, engine=None):
    """The page as it is now, so `diff <url> <old> live` needs no manual save first."""
    target = url if "://" in url else "https://" + url
    hint = (
        f"live: {target} refuses scripted requests ({{}}). Get it with the cloudflare skill "
        f"(`cf text {target} > today.txt`) and pass today.txt as the ref."
    )
    try:
        try:
            raw, hdrs = get(target, tries=2, with_headers=True)
        except urllib.error.URLError as e:
            if not isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError) or not (ctx := keychain_context()):
                raise
            raw, hdrs = get(target, tries=2, with_headers=True, context=ctx)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503):
            sys.exit(hint.format(f"HTTP {e.code}"))
        raise
    if CHALLENGE.search(raw[:200000]):
        sys.exit(hint.format("bot challenge"))
    name = "live-" + time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return name, raw, *_as_text(raw, target, hdrs.get("Content-Type", ""), engine)


# ---------- HTML -> text


SKIP = {"script", "style", "noscript", "svg", "template", "head", "title"}


class _Text(HTMLParser):
    BLOCK = {
        "p", "li", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th",
        "section", "article", "header", "footer", "main", "nav", "table", "ul", "ol",
        "blockquote", "pre", "dd", "dt", "figure", "figcaption",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []  # (text, link_chars)
        self.links = []  # (href, anchor text), in document order
        self.skip = 0
        self._buf, self._linkchars = [], 0
        self._href = None
        self._htext = []

    def _flush(self):
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        if text:
            self.blocks.append((text, self._linkchars))
        self._buf, self._linkchars = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag == "a":
            self._href, self._htext = dict(attrs).get("href"), []
        if tag == "base":
            self.links.append(("", dict(attrs).get("href") or ""))
        if tag in self.BLOCK:
            self._flush()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        if tag == "a" and self._href is not None:
            self.links.append((self._href, "".join(self._htext)))
            self._href = None

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        if tag == "a" and self._href is not None:
            self.links.append((self._href, re.sub(r"\s+", " ", "".join(self._htext)).strip()))
            self._href = None
        if tag in self.BLOCK:
            self._flush()

    def handle_data(self, d):
        if not self.skip:
            self._buf.append(d)
            if self._href is not None:
                self._htext.append(d)
                self._linkchars += len(d)


def sniff_charset(raw, ctype=""):
    """Archived pages keep their original encoding: 2005-era corporate sites are often
    windows-1252 or Shift_JIS, and decoding those as UTF-8 drops every accent."""
    if m := re.search(r"charset=[\"']?([\w.:-]+)", ctype or "", re.I):
        return m.group(1)
    head = raw[:4096].decode("latin-1", "ignore")
    if m := re.search(r"(?i)<meta[^>]+charset=[\"']?([\w.:-]+)", head):
        return m.group(1)
    if m := re.search(r"(?i)<\?xml[^>]+encoding=[\"']([\w.:-]+)", head):
        return m.group(1)
    return "utf-8"


def _decode(raw, charset):
    """Try the declared charset, then utf-8, then cp1252, and keep the cleanest result:
    a wrong guess must never drop characters the way `errors="ignore"` did."""
    best = ""
    for cs in dict.fromkeys([charset, "utf-8", "cp1252"]):
        try:
            s = raw.decode(cs, "replace")
        except LookupError:
            continue
        if s.count("\ufffd") == 0:
            return s
        if best == "" or s.count("\ufffd") < best.count("\ufffd"):
            best = s
    return best if best != "" else raw.decode("cp1252", "replace")



def pdf_text(raw):
    """Captured PDFs (prospectuses, policies) are common; pdftotext beats a binary warning."""
    if not (tool := shutil.which("pdftotext")):
        print("warn: capture is a PDF and pdftotext is not installed; text unavailable", file=sys.stderr)
        return ""
    out = subprocess.run([tool, "-layout", "-q", "-", "-"], input=raw, capture_output=True)
    if out.returncode != 0:
        print(f"warn: pdftotext failed ({out.stderr[:120].decode(errors='replace')})", file=sys.stderr)
        return ""
    return re.sub(r"\n{3,}", "\n\n", out.stdout.decode("utf-8", "replace"))


# ---------- main-content extraction: nav, cookie banners and footers are the bulk of a
# ---------- capture and the bulk of every diff, so history reads the body by default.

NAV_MAX = 120  # a block shorter than this that is mostly link text is navigation
# A line in *every* capture cannot be a change. 0.7 was tried and rejected: a line that
# changed once and then stayed would sit in 35 of 36 captures, be called template, and
# erase that old change from the history.
TEMPLATE_RATIO = 1.0
TEMPLATE_MIN = 3  # with fewer captures "every capture" says nothing (2 of 2 is everything)
_TRAFILATURA = "unset"
_ENGINE_NOTED = None


def trafilatura_module():
    """Optional dependency: trafilatura does real boilerplate removal (readability-style
    DOM pruning), the builtin cut only drops link farms and repeated blocks. `-I` ignores
    PYTHONPATH, so a venv is added to sys.path here instead."""
    global _TRAFILATURA
    if _TRAFILATURA != "unset":
        return _TRAFILATURA
    _TRAFILATURA = None
    try:
        import trafilatura  # noqa: PLC0415

        _TRAFILATURA = trafilatura
        return trafilatura
    except ImportError:
        pass
    roots = [os.environ.get("WAYBACK_TRAFILATURA_PATH"), str(CACHE / "venv")]
    for root in filter(None, roots):
        for sp in sorted(Path(root).glob("lib/python3*/site-packages")):
            sys.path.insert(0, str(sp))
            try:
                import trafilatura  # noqa: PLC0415

                _TRAFILATURA = trafilatura
                return trafilatura
            except ImportError:
                sys.path.pop(0)
    return None


TRAFILATURA_PY = os.environ.get("WAYBACK_MAIN_PYTHON") or str(CACHE / "venv" / "bin" / "python")
TR_SNIPPET = (
    "import sys, trafilatura\n"
    "doc = sys.stdin.buffer.read().decode('utf-8', 'replace')\n"
    "out = trafilatura.extract(doc, url=sys.argv[1] or None, include_links=False,\n"
    "                          include_comments=False, favor_precision=True)\n"
    "sys.stdout.write(out or '')\n"
)


def trafilatura_ready():
    """True when trafilatura can run: in-process, or through a venv's interpreter.
    A venv is usually a different CPython (compiled deps like lxml will not import into
    this one), so the fallback is a subprocess rather than a sys.path hack."""
    return bool(trafilatura_module()) or Path(TRAFILATURA_PY).exists()


def trafilatura_extract(doc, page_url):
    if mod := trafilatura_module():
        return (
            mod.extract(
                doc, url=page_url or None, include_links=False, include_comments=False,
                favor_precision=True,
            )
            or ""
        ).strip()
    try:
        p = subprocess.run(
            [TRAFILATURA_PY, "-c", TR_SNIPPET, page_url or ""],
            input=doc.encode("utf-8", "replace"),
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as e:
        print(f"warn: trafilatura subprocess failed ({e})", file=sys.stderr)
        return ""
    if p.returncode != 0:
        print(
            f"warn: trafilatura subprocess failed ({p.stderr[:160].decode(errors='replace')})",
            file=sys.stderr,
        )
        return ""
    return p.stdout.decode("utf-8", "replace").strip()


def resolve_engine(name="auto"):
    if name == "builtin":
        return "builtin"
    if trafilatura_ready():
        return "trafilatura"
    if name == "trafilatura":
        sys.exit(
            f"trafilatura is not available (looked in-process and at {TRAFILATURA_PY}).\n"
            "  uv venv ~/.cache/wayback-skill/venv && "
            "uv pip install --python ~/.cache/wayback-skill/venv/bin/python trafilatura\n"
            "  (or set WAYBACK_MAIN_PYTHON to an interpreter that has it)\n"
            "  or run with --engine builtin for the stdlib cut."
        )
    return "builtin"


def note_engine(engine):
    global _ENGINE_NOTED
    if _ENGINE_NOTED == engine:
        return
    _ENGINE_NOTED = engine
    extra = (
        "  (trafilatura unavailable: only link farms and repeated blocks are dropped; "
        "see --engine)"
        if engine == "builtin"
        else "  (trafilatura)"
    )
    print(f"main: {engine} extraction{extra}", file=sys.stderr)


def lite_main(blocks):
    """Stdlib boilerplate cut over (text, link_chars) blocks: menus are mostly link text,
    and a block repeated verbatim further down the page is a footer, not content. The first
    occurrence is kept, so a repeated row costs one duplicate rather than the text."""
    keep, seen = [], set()
    for text, links in blocks:
        if len(text) < NAV_MAX and links / max(len(text), 1) >= 0.5:
            continue  # a menu item, not a sentence
        key = text.lower()
        if len(text) < 200 and key in seen:
            continue
        seen.add(key)
        keep.append(text)
    return "\n".join(keep) + "\n" if keep else ""


def template_lines(texts):
    """{lowercase line: (capture count, first original spelling)} for lines every capture
    shares: nav, cookie banners, footers, the standing copy. They are what a history diff
    is made of, not what changed."""
    if len(texts) < TEMPLATE_MIN:
        return {}
    counts, spelling = {}, {}
    for text in texts:
        for line in {l.strip().lower() for l in text.splitlines() if l.strip()}:
            counts[line] = counts.get(line, 0) + 1
        for line in text.splitlines():
            if line.strip():
                spelling.setdefault(line.strip().lower(), line.strip())
    need = max(TEMPLATE_MIN, math.ceil(TEMPLATE_RATIO * len(texts)))
    return {line: (n, spelling[line]) for line, n in counts.items() if n >= need}


def drop_template(text, template):
    """(text without template lines, lines dropped, lines seen)."""
    lines = text.splitlines()
    kept = [l for l in lines if l.strip().lower() not in template]
    return ("\n".join(kept) + "\n" if kept else ""), len(lines) - len(kept), len(lines)


def extract_main(doc, page_url, blocks, engine="auto"):
    engine = resolve_engine(engine)
    note_engine(engine)
    if engine == "trafilatura":
        if out := trafilatura_extract(doc, page_url):
            return out + "\n"
        print("warn: trafilatura found no main content; falling back to the builtin cut", file=sys.stderr)
    return lite_main(blocks)


def _as_text(raw, page_url="", ctype="", engine=None):
    """(full text, main text or None, links) for a raw payload."""
    if raw[:4] == b"%PDF" or "pdf" in (ctype or "").lower():
        text = pdf_text(raw)
        return text, None, []
    doc = _decode(raw, sniff_charset(raw, ctype))
    p = _Text()
    try:
        p.feed(doc)
    except Exception as e:  # malformed markup: keep whatever parsed
        print(f"warn: HTML parse stopped early ({e})", file=sys.stderr)
    p._flush()
    text = "\n".join(t for t, _ in p.blocks)
    links = _abs_links(p.links, page_url)
    if raw.count(b"\x00"):
        print("warn: capture looks binary/compressed (brotli?), text is unusable", file=sys.stderr)
    full = text + "\n" if text else ""
    main = extract_main(doc, page_url, p.blocks, engine) if (engine and full) else None
    return full, main, links


def _abs_links(pairs, page_url):
    base = next((b for h, b in pairs if h == ""), "") or page_url  # <base href> wins
    seen, out = set(), []
    for href, label in pairs:
        if not href:
            continue
        href = href.strip()
        if href.startswith(("javascript:", "data:", "#")) or not href:
            continue
        full = urllib.parse.urljoin(base, href)
        if full in seen or full.split("://")[0] not in ("http", "https", ""):
            continue
        seen.add(full)
        out.append(f"{full}\t{label}" if label else full)
    return out


def to_text(raw, engine=None):
    """Back-compat: text only (main text when an engine is given)."""
    full, main, _ = _as_text(raw, "", "", engine)
    return main if (engine and main) else full


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
            wait = retry_after(e.headers, 20 * 2**i)
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
        except (urllib.error.URLError, TimeoutError, urllib.error.HTTPError) as e:
            sys.exit(
                f"archive.org is unreachable from this network ({type(e).__name__}): nothing "
                "was saved. Save the page with archive.ph in Chrome instead."
            )
        if not rows:
            sys.exit("no capture exists and Save Page Now did not create one")
        ts = rows[-1][1]
    return ts, f"https://web.archive.org/web/{ts}/{url}", ts >= started[:12]


def cut_template(cropped, out, disabled=False):
    """Replace each kept .txt with its template-free view, under three guardrails: enough
    captures for "every capture" to mean something, a refusal to filter when every line is
    shared (that is "nothing changed", not "delete the page"), and a printed count so a
    suspiciously empty diff is explained. The unfiltered extraction stays in .full.txt /
    .main-<engine>.txt, so nothing is lost."""
    if disabled or len(cropped) < TEMPLATE_MIN:
        if not disabled:
            print(
                f"template filter off: {len(cropped)} capture(s), need {TEMPLATE_MIN}",
                file=sys.stderr,
            )
        return cropped, [p for p, _ in cropped]
    template = template_lines([t for _, t in cropped])
    if not template:
        print("template: no line is shared by enough captures; nothing dropped", file=sys.stderr)
        return cropped, [p for p, _ in cropped]
    cut, total = [], 0
    for p, text in cropped:
        stable, dropped, _ = drop_template(text, template)
        cut.append((p, stable))
        total += dropped
    lines = sum(len(t.splitlines()) for _, t in cropped)
    frac = total / max(lines, 1)
    if not any(text.strip() for _, text in cut):
        print(
            f"template: all {lines} lines are shared by every capture, so nothing changed "
            f"between them; the {out}/*.txt files keep the text, --no-template diffs it",
            file=sys.stderr,
        )
        return cropped, [p for p, _ in cropped]
    for (p, stable), (_, text) in zip(cut, cropped):
        p.write_text(stable)
    (out / "template.txt").write_text(
        "\n".join(f"{n}\t{text}" for n, text in sorted(template.values(), key=lambda v: -v[0])) + "\n"
    )
    print(
        f"template: dropped {total}/{lines} lines ({frac:.0%}) shared by >="
        f"{TEMPLATE_RATIO:.0%} of {len(cropped)} captures; they are listed in {out / 'template.txt'}",
        file=sys.stderr,
    )
    return cut, [p for p, _ in cut]


# the summary is for "what did this page start saying", so stopwords and punctuation stay
# in the diff (they carry the alignment) and are only counted out of the summary
STOPWORDS = set(
    """a an and are as at be been but by for from had has have if in into is it its of on
    or that the their them there these they this to was were what when which will with
    would you your we our us not no""".split()
)


def _counted(words):
    return [w for w in words if w not in STOPWORDS and not re.fullmatch(r"\W+", w)]


def _words(path):
    try:
        return re.findall(r"\w+|[^\w\s]", path.read_text().lower())
    except OSError:
        return []


def word_stat(a, b, limit=12, label=""):
    """Net word-inventory change between two texts: what the page stopped saying and started
    saying. Counted as bags of words, not by diff alignment — a word that merely moved is not
    a change, and "margin -2 / markets +1" is the answer a "what did this JD add" question
    wants. Empty string when the two share every counted word."""
    from collections import Counter

    minus = Counter(_counted(_words(a))) - Counter(_counted(_words(b)))
    plus = Counter(_counted(_words(b))) - Counter(_counted(_words(a)))
    if not minus and not plus:
        return ""
    ranked = lambda d: sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))  # ties alphabetical
    out = [f"-{n} {w}" for w, n in ranked(minus)[:limit]]
    out += [f"+{n} {w}" for w, n in ranked(plus)[:limit]]
    head = f"{label}\n" if label else ""
    return head + "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list")
    l.add_argument("url", nargs="+")
    l.add_argument("--limit", type=int)
    l.add_argument("--domain", action="store_true", help="inventory a whole host, one capture per URL")
    l.add_argument("--json", action="store_true", help="one JSON object per capture")
    fd = sub.add_parser("find")
    fd.add_argument("query", nargs="+", help="words to look for in the archived text")
    fd.add_argument("--site", help="restrict to one host (siteSearch)")
    fd.add_argument("--limit", type=int, default=20)
    fd.add_argument("--json", action="store_true")
    dc = sub.add_parser("discover")
    dc.add_argument("host")
    dc.add_argument("--source", default="otx,urlscan", help="otx, urlscan, or a comma list")
    dc.add_argument("--limit", type=int, default=200)
    dc.add_argument("--json", action="store_true")
    dc.add_argument("--all", action="store_true", help="keep tracking pixels and asset URLs")
    s = sub.add_parser("save")
    s.add_argument("url")
    f = sub.add_parser("fetch")
    f.add_argument("url")
    f.add_argument("ts", nargs="?", help="ref from `list`; omit for the latest capture")
    f.add_argument("-o", default=".")
    f.add_argument("--main", action="store_true", help="write the main content instead of the full text")
    f.add_argument("--engine", default="auto", choices=("auto", "trafilatura", "builtin"))
    d = sub.add_parser("diff")
    d.add_argument("url")
    d.add_argument("a")
    d.add_argument("b")
    h = sub.add_parser("history")
    h.add_argument("url")
    h.add_argument("--min-chars", type=int, default=300)  # body text is shorter than the page
    h.add_argument("--max", type=int, help="diff only the newest N captures")
    for x in (l, h, fd):
        x.add_argument("--from", dest="frm")
        x.add_argument("--to")
    for x in (l, h):
        x.add_argument("--source", default="all", help="all (default), or ia, cc, pt, gh, mg, uk, or a comma list")
        x.add_argument("--fresh", action="store_true", help="ignore the on-disk listing cache")
    for x in (d, h):
        x.add_argument("--start")
        x.add_argument("--end")
        x.add_argument("--line", action="store_true")
        x.add_argument("--stat", action="store_true",
                       help="add a word-level change summary after each diff; history also gets a net first->last summary")
        x.add_argument("--stat-only", action="store_true", help="word-level summary without the diff")
        x.add_argument("--stat-words", type=int, default=12, help="terms per side in the summary (default 12)")
        x.add_argument("--engine", default="auto", choices=("auto", "trafilatura", "builtin"))
        x.add_argument("-o")
    d.add_argument("--main", action="store_true", help="diff the main content instead of the full text")
    h.add_argument("--raw", action="store_true", help="diff the full text, nav and footers included")
    h.add_argument("--no-template", action="store_true",
                   help="keep lines shared by every capture in the diff")
    a = ap.parse_args()
    global FRESH
    FRESH = getattr(a, "fresh", False)
    if a.cmd == "history" and "*" in a.url:
        ap.error("history takes one page URL; use `list` for a prefix sweep")
    # history reads the body by default (nav and footers are most of a diff); fetch and
    # diff stay raw unless asked, because a crop regex is written against the raw text
    want_main = (a.cmd == "history" and not getattr(a, "raw", False)) or (
        a.cmd in ("fetch", "diff") and a.main
    )
    engine = resolve_engine(a.engine) if want_main else None

    if a.cmd == "list":
        total = 0
        for url in a.url:
            rows = captures(url, a.frm, a.to, a.limit, parse_sources(a.source), a.domain)
            for ref, ts, orig, mime, length, _ in rows:
                if a.json:
                    src = ref.split(":")[0] if ":" in ref else "ia"
                    print(json.dumps({"ref": ref, "source": src, "timestamp": ts, "url": orig,
                                      "mime": mime, "length": length}))
                else:
                    print(ref, mime, length, orig, sep="\t")
            total += len(rows)
        print(f"{total} distinct 200 captures", file=sys.stderr)
    elif a.cmd == "find":
        try:
            rows = cached(
                ("find", " ".join(a.query), a.site, a.frm, a.to, a.limit),
                lambda: arquivo_find(" ".join(a.query), a.site, a.frm, a.to, a.limit),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            sys.exit(f"find failed: {type(e).__name__} {e}; arquivo.pt may be down, try again")
        for ts, mime, orig, arch in rows:
            if a.json:
                print(json.dumps({"timestamp": ts, "mime": mime, "url": orig, "archive": arch}))
            else:
                print(ts, mime, orig, arch, sep="\t")
        print(f"{len(rows)} hits in arquivo.pt full-text search", file=sys.stderr)
    elif a.cmd == "discover":
        names = [n for n in a.source.split(",") if n]
        if bad := [n for n in names if n not in ("otx", "urlscan")]:
            sys.exit(f"unknown source {bad}; choose otx, urlscan, or both")
        rows = discover(a.host, names, a.limit, a.all)
        for url, src in rows:
            print(json.dumps({"url": url, "source": src}) if a.json else url)
        print(f"{len(rows)} URLs for {a.host}; feed them to `list`", file=sys.stderr)
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
        ref = a.ts
        if not ref:
            rows = captures(a.url, limit=1, sources=fetchable(list(SOURCES)))
            if not rows:
                sys.exit(f"no captures for {a.url}; try `save {a.url}`")
            ref = rows[-1][0]
        try:
            name, raw, full, main, links = load(a.url, ref, engine)
        except urllib.error.HTTPError as e:
            why = "archive.org is rate-limiting this network" if e.code == 429 else str(e)
            sys.exit(f"{ref}: {why}; retry later, or use --source cc / --source pt")
        except (urllib.error.URLError, TimeoutError) as e:
            sys.exit(f"{ref}: {type(e).__name__} ({e}); retry later")
        (out / f"{name}.html").write_bytes(raw)
        (out / f"{name}.txt").write_text(main or full)
        if main and full != main:
            (out / f"{name}.raw.txt").write_text(full)
        if links:
            (out / f"{name}.links.txt").write_text("\n".join(links) + "\n")
        print(out / f"{name}.txt")
        if links:
            print(f"{len(links)} links in {out / f'{name}.links.txt'}", file=sys.stderr)
    else:
        out = Path(a.o) if a.o else Path(tempfile.mkdtemp(prefix="wayback-"))
        out.mkdir(parents=True, exist_ok=True)
        if a.cmd == "diff":
            refs = [a.a, a.b]
        else:
            names = parse_sources(a.source)
            if dropped := [n for n in names if n in LIST_ONLY]:
                if a.source != "all":
                    print(f"{','.join(dropped)}: listing only, their text cannot be fetched; left out of history", file=sys.stderr)
                names = fetchable(names)
            seen_refs = [r[0] for r in captures(a.url, a.frm, a.to, sources=names)]
            refs = seen_refs[-a.max :] if a.max else seen_refs

        def grab(ref):
            # texts are cached in the output dir, so re-running with a fixed --start/--end
            # (or switching --raw/--main) costs no fetch
            stem = ref.replace(":", "-")
            full_cache = out / f"{stem}.full.txt"
            main_cache = out / main_cache_name(stem, engine) if engine else None
            # the cache must cover the mode asked for: a --raw run leaves no .main-<engine>.txt,
            # and answering a --main run with the raw text would quietly keep the nav
            if ref != "live" and not Path(ref).exists() and full_cache.exists() and (not engine or main_cache.exists()):
                main = main_cache.read_text() if engine else None
                return stem, full_cache.read_text(), main
            try:
                name, raw, full, main, links = load(a.url, ref, engine)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                # one dead capture must not sink the whole history: skip it and say so
                print(f"warn {ref}: {type(e).__name__} {e}; skipped", file=sys.stderr)
                return stem, "", None
            (out / f"{name}.full.txt").write_text(full)
            if main:
                (out / main_cache_name(name, engine)).write_text(main)
            if links and a.cmd == "history":
                (out / f"{name}.links.txt").write_text("\n".join(links) + "\n")
            return name, full, main

        with ThreadPoolExecutor(max_workers=4) as pool:
            texts = list(pool.map(grab, refs))
        if any(not full.strip() for _, full, _ in texts):
            if a.cmd == "diff":
                sys.exit("one side of the diff could not be fetched; see the warnings above")
            texts = [t for t in texts if t[1].strip()]
        kept, cropped, misses = [], [], 0
        for name, full, main in texts:
            text, warn = crop(main if main else full, a.start, a.end)
            if warn:
                misses += 1
                print(f"warn {name}: {warn}", file=sys.stderr)
            if a.cmd == "history" and len(text) < a.min_chars:
                print(f"skip {name}: {len(text)} chars (empty shell?)", file=sys.stderr)
                continue
            p = out / f"{name}.txt"
            p.write_text(text)
            kept.append(p)
            cropped.append((p, text))
        if a.cmd == "history":
            cropped, kept = cut_template(cropped, out, a.no_template)
        if misses or (a.cmd == "history" and len(kept) < len(texts) // 2):
            print(
                f"check --start/--end against the uncropped {out}/*.full.txt "
                "(--raw diffs the same text); re-running reuses them",
                file=sys.stderr,
            )
        stat = a.stat or a.stat_only
        same = changed = 0
        for old, new in zip(kept, kept[1:]):
            summary = word_stat(old, new, limit=a.stat_words) if stat else ""
            d = "" if a.stat_only else diff_text(old, new, a.line)
            if not d and not summary:
                same += 1
                continue
            changed += 1
            if a.cmd == "history":
                print(f"\n===== {old.stem} -> {new.stem} =====")
            if d:
                sys.stdout.write(d if d.endswith("\n") else d + "\n")
            if summary:
                print("-- word change --")
                print(summary)
        if a.cmd == "history" and stat and len(kept) > 1:
            print(f"\n===== net {kept[0].stem} -> {kept[-1].stem} ({len(kept)} versions) =====")
            print(word_stat(kept[0], kept[-1], limit=a.stat_words) or "(first and last share every word)")
        if a.cmd == "history":
            span = f"{kept[0].stem} .. {kept[-1].stem}" if kept else "none"
            print(
                f"{len(kept)} versions, {changed} change(s), {same} identical pair(s) ({span})",
                file=sys.stderr,
            )
        elif same:
            print(f"{same} consecutive pair(s) identical after cropping", file=sys.stderr)
        print(f"{len(kept)} texts saved in {out}", file=sys.stderr)


def main_cache_name(stem, engine):
    """Body text depends on the extractor, so each engine keeps its own cache file."""
    return f"{stem}.main-{engine}.txt"


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
