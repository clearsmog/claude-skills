---
name: wayback
description: Use the Wayback Machine (web.archive.org), Common Crawl and Arquivo.pt (all three queried together), to recover dead or changed pages and to compare versions of the same page over time — list distinct captures, fetch one as clean text, and word-diff two versions (or an old capture against a page saved today). Use whenever a link 404s or a page was changed or removed, or when the task asks what a job ad, team page, product page, policy, prospectus or company site said before, or how it changed between years — even if the user never says "Wayback" or "archive". Also use when Wayback is down, blocked or has no capture of the page. Not for reddit.com threads, removed ones included (reddit skill).
---
# Wayback Machine (+ Common Crawl, Arquivo.pt)

Script: `${CLAUDE_SKILL_DIR}/scripts/wayback.py` (stdlib only; run with `python3 -I`). No MCP needed.

| Need | Command |
|---|---|
| Distinct captures (dedup by content, HTTP 200 only) | `wayback.py list <url> [--source ia\|cc\|pt\|ia,pt] [--from 2020] [--to 2024] [--limit 20]` |
| Prefix sweep (all job URLs under a path) | `wayback.py list 'careers.example.com/job/*'` |
| Capture a live page now (JD at application time, a source being cited) | `wayback.py save <url>` → prints `<timestamp>\t<archived URL>` |
| One capture as HTML + text | `wayback.py fetch <url> <timestamp> -o <dir>` |
| Full change history of one page (consecutive diffs, empty shells skipped) | `wayback.py history <url> [--from 2015] --start '<regex>' --end '<regex>' -o <dir>` |
| What changed between two versions | `wayback.py diff <url> <A> <B> --start '^Job title:' --end '^Apply' -o <dir>` |

- `A`/`B` are refs from `list` (`20210909191632` = Wayback, `cc:<ts>` = Common Crawl, `pt:<ts>` = Arquivo.pt) or local `.html`/`.txt` files, so a page saved today diffs against an old capture and captures from different archives diff against each other.
- `list`/`history` query all three archives by default, merge by time and drop captures whose payload digest another archive already has (Wayback ingests part of Common Crawl, so shared captures are common; the Wayback ref is kept). The three are queried in parallel; a default run takes about 15 s, most of it Common Crawl, and `--source ia,pt` answers in a few seconds when a quick look is enough. Narrowing `--source` can miss captures: on osttra.com, only Common Crawl had the page after June 2026.
- `diff` prints a word-level `git diff` (`--line` for line-level). `--start`/`--end` are multiline regexes that cut the text down to the body, dropping nav, cookie banners and footers.
- Save raw captures under the project (e.g. `wayback-raw/`), not the scratchpad, when they back a written note.

## Sources

| Source | What it adds | Limits |
|---|---|---|
| `ia` Wayback Machine | densest history; the only one with scripted `save` | sites can opt out; archive.org sometimes refuses TLS from this network (seen 2026-10-31 and 2026-11-11): the script then drops `ia` at once and reports it, and `save` exits telling you to use archive.ph in Chrome |
| `cc` Common Crawl | pages Wayback missed or that excluded archive.org; still answers when archive.org is down | monthly samples, not every page every crawl; robots.txt honoured and many news/corporate sites block CCBot since 2023; a crawler, so no `save` exists |
| `pt` Arquivo.pt | a third independent copy, older pages; covers many non-.pt sites too (osttra.com, nomura.com have captures) | sparser than Wayback; its ArchivePageNow is a web form with a consent checkbox, and captures join the archive later, so no scripted save |

## Gotchas
- **Common Crawl** lookups skip the index server (index.commoncrawl.org, which 503/504s for hours): the script binary-searches each crawl's `cluster.idx` on data.commoncrawl.org with Range reads and gunzips the matching CDX block, about 16 requests / 0.5 MB per crawl, 3 crawls at a time (`WAYBACK_CC_WORKERS`; 3 showed no throttling, 5 was barely faster). Without `--from` it searches the newest 12 of 129 crawls (about a year, ~13 s); `--from 2020` (~70 crawls) takes ~1.5 min. The crawl list (`collinfo.json`) is cached in `~/.cache/wayback-skill/` for a week and used stale when the server is down; with no cache, crawl dates are approximated from the crawl IDs. Prefix sweeps stop after 20 index blocks (~60k index lines) per crawl and warn.
- CC keys are SURTs: `www.`, scheme, fragment, default port and a trailing slash are ignored, case-insensitive, query params sorted. So `https://www.x.com/a/` and `x.com/a` are the same lookup, but `x.com/a?utm=..` is a different page; use `x.com/a*` to catch query variants.
- CC records are cut at 1 MiB (before CC-MAIN-2025-13) or 5 MiB; the script warns `record truncated`. Big PDFs are often incomplete. Crawls 2008–2012 are ARC, not WARC (handled, but less tested). CCBot runs no JavaScript, so SPA captures are shells, as in Wayback.
- CC and Arquivo CDX are pywb: no `collapse=digest`, so dedup is client-side; filters use `filter=status:200` / `filter=!status:200` / `filter=~field:regex`.
- `list`/`history` use CDX with `collapse=digest`, so captures whose bytes did not change are hidden. Captures that differ only in boilerplate (a timestamp, a cookie banner) still show up; `--start`/`--end` cropping makes their diffs empty.
- `archive.org/wayback/available` often returns empty for archived sites; don't trust it, use CDX.
- `id_` in the fetch URL returns the original page without the Wayback toolbar; the script does this.
- Many captures of JS-rendered sites (careers portals, SPAs) are empty shells or "position filled" pages. Check the text length before diffing; try other URL variants (with/without `www`, trailing slash, query string) or an aggregator copy (eFinancialCareers, LinkedIn, Indeed).
- `diff`/`history` fetch 4 captures at a time and cache each uncropped text as `<dir>/<timestamp>.full.txt`. When the script warns `--start not found` / `--end not found`, or skips most captures as short, open a `.full.txt`, fix the regex, and re-run with the same `-o`: no refetch.
- `id_` replays the archived response, sometimes still gzip-encoded; the script decompresses gzip/deflate and warns on anything still binary (brotli). A warned capture's diff is noise.
- Rate limits: 429/5xx are retried with backoff (Retry-After honoured); occasional `retry in 5s` lines are normal.
- Useless for login-gated pages.
- `save` uses unauthenticated Save Page Now: 10–60 s per page, throttled after a burst (429 is retried with backoff). Sites that block the crawler return 520/523; the script then prints the latest existing capture and warns `no new capture was made`, so check that warning before citing the timestamp as "today". Login-gated pages save as a login wall.

## Beyond the script
Checked from this Mac on 2026-10-31; not wired into the script.

| Tool | What it adds | How |
|---|---|---|
| archive.today (archive.ph) | on-demand saves that render JavaScript; many paywalled/news pages | Chrome only: curl times out (bot wall). `https://archive.ph/newest/<url>` or the timemap page |
| Arquivo.pt full-text search | find a page by its words when the URL is unknown | `curl 'https://arquivo.pt/textsearch?q=<words>&maxItems=20&from=2015&to=2020'` (JSON; `siteSearch=<host>` narrows) |
| urlscan.io | recent rendered snapshots (DOM + screenshot) of JS sites, scanned by others | search works keyless: `https://urlscan.io/api/v1/search/?q=domain:<host>`; the DOM/result endpoints need a free API key |
| AlienVault OTX URL list | URL discovery only (old PDF paths, removed pages) to feed into `list` | `https://otx.alienvault.com/api/v1/indicators/domain/<host>/url_list?limit=200` |

Not worth using: Memento TimeTravel (DNS no longer resolves), Library of Congress web archive and perma.cc (Cloudflare challenge), UK Web Archive (no public CDX endpoint at the path tried), Google/Bing cache (gone).
