---
name: wayback
description: >-
  Recover dead or changed pages, inventory a site, and compare versions of a page over time through the Wayback Machine, Common Crawl and Arquivo.pt (queried together) — list distinct captures, fetch one as clean text plus links, and word-diff two versions (or an old capture against a page saved today). Use whenever a link 404s or a page was changed or removed, or the task asks what a job ad, team page, product page, policy, prospectus or company site said before, how it changed, or which pages a site once had — even if the user never says "Wayback" or "archive". Also use when Wayback is down, blocked or has no capture. 中文说法 — "打不开了", "之前是什么内容", "原来的版本", "改版前", "这个页面以前", "历史版本", "存档", "快照", "网页变了". Not for a page that is reachable but refuses you (403, Cloudflare challenge, login wall, paywall: cloudflare skill or a session cookie), nor reddit.com threads, removed ones included (reddit skill).

---
# Wayback Machine (+ Common Crawl, Arquivo.pt)

Script: `${CLAUDE_SKILL_DIR}/scripts/wayback.py` (stdlib only; run with `python3 -I`). Optional: trafilatura in a venv for body extraction (see 正文). No MCP needed.

| Need | Command |
|---|---|
| Distinct captures (dedup by content, HTTP 200 only) | `wayback.py list <url> [--source ia\|cc\|pt\|ia,pt] [--from 2020] [--to 2024] [--limit 20]` |
| Site inventory: one capture per URL for a whole host | `wayback.py list example.com --domain --limit 200` |
| Prefix sweep (all job URLs under a path) | `wayback.py list 'careers.example.com/job/*'` |
| Machine-readable list | `wayback.py list <url> --json` (one JSON object per capture) |
| Find a page by its words when the URL is unknown | `wayback.py find 'collateral management' --site example.com --from 2015` (Arquivo.pt full text) |
| URLs for a host, to feed into `list` | `wayback.py discover example.com [--source otx,urlscan] [--all]` |
| Capture a live page now (JD at application time, a source being cited) | `wayback.py save <url>` → prints `<timestamp>\t<archived URL>` |
| One capture as HTML + text + links | `wayback.py fetch <url> [ref] -o <dir>` (no ref = latest capture) |
| One capture as body text only | `wayback.py fetch <url> --main -o <dir>` (writes `.txt` body + `.raw.txt`) |
| Full change history of one page (consecutive diffs, empty shells skipped) | `wayback.py history <url> [--from 2015] --start '<regex>' --end '<regex>' -o <dir>` |
| Same, but on the whole page including nav and footers | add `--raw` |
| Keep the standing copy in the diff (no template filter) | add `--no-template` |
| What changed between two versions | `wayback.py diff <url> <A> <B> --start '^Job title:' --end '^Apply' -o <dir>` |
| Diff, plus a word-level summary of what was added/removed | add `--stat` (`--stat-words N` for more terms) |
| Only the summary, no diff to read | `--stat-only` |
| "What did this JD start asking for over the years" | `wayback.py history <url> --stat-only --from 2019 -o <dir>` — the `net` block compares the oldest and newest capture |
| Pick the extractor | `--engine auto\|trafilatura\|builtin` |

- `A`/`B` are refs from `list` (`20210909191632` = Wayback, `cc:<ts>` = Common Crawl, `pt:<ts>` = Arquivo.pt) or local `.html`/`.txt`/`.pdf` files, so a page saved today diffs against an old capture and captures from different archives diff against each other.
- `fetch` writes `<name>.html`, `<name>.txt` (visible text) and `<name>.links.txt` (absolute URLs found in the page, with anchor text). Read `.links.txt` to find contact/apply/next pages that the text alone loses. Hostile/odd encodings are handled: the capture's own charset (header, then `<meta charset>`) is used, so 2005-era windows-1252 or Shift_JIS pages do not lose accents. PDF captures go through `pdftotext -layout` when it is installed.
- `list`/`history` query all three archives by default, merge by time and drop captures whose payload digest another archive already has (Wayback ingests part of Common Crawl, so shared captures are common; the Wayback ref is kept). The three are queried in parallel, and listings are cached on disk for 30 min (`--fresh` refetches, `WAYBACK_CACHE_TTL` changes the TTL): the second lookup of the same URL is instant. A default cold run takes ~15–40 s depending on the network, most of it Common Crawl; `--source ia,pt` answers in a few seconds when a quick look is enough. Narrowing `--source` can miss captures: on osttra.com, only Common Crawl had the page after June 2026.
- `diff` prints a word-level `git diff` (`--line` for line-level). `--start`/`--end` are multiline regexes that cut the text down to the body, dropping nav, cookie banners and footers.
- **`history` drops what every capture shares.** A line present in *all* captures cannot be a change, so it is removed from the diff and listed in `<dir>/template.txt` (count, then text) — that file is also the fastest way to write a `--start`/`--end` crop later. Three guardrails: it is off below 3 captures (`template filter off: 2 capture(s), need 3`), it never uses a partial majority (a line that changed once and then stayed is *not* template — a 70% rule was tried and erased exactly those changes), and if every line turns out to be shared it says `nothing changed between them` instead of printing an empty diff. `<dir>/*.txt` holds the filtered view; `.full.txt`/`.main.txt` keep the unfiltered extraction. Measured on osttra.com (36 captures): 244 body lines, 72 dropped as template (30%), leaving one real change in 26 lines of output — the same history in `--raw --no-template` mode prints 624 lines.
- **`history` reads the body, not the page.** Nav menus, cookie banners and footers are most of every capture and therefore most of every diff, so history extracts the main content by default; `--raw` diffs the whole page. Measured on osttra.com (36 captures, Arquivo.pt): raw mode = 624 lines of diff; body mode + template filter = 26 lines and exactly one real change (a homepage copy rewrite). `fetch`/`diff` stay raw unless `--main` is passed, because a `--start`/`--end` regex is written against the raw text; `.full.txt` is always the raw text, so regexes can be tuned on it and reused.
- Save raw captures under the project (e.g. `wayback-raw/`), not the scratchpad, when they back a written note.

## Body extraction (`--main`, on by default for `history`)

| Engine | What it does | When |
|---|---|---|
| `trafilatura` | readability-style DOM pruning: drops nav, cookie banners, footers, related-links boxes | preferred; needs `uv venv ~/.cache/wayback-skill/venv && uv pip install --python ~/.cache/wayback-skill/venv/bin/python trafilatura` once. `python3 -I` ignores pip `--user`, and the venv is usually a different CPython (lxml will not load), so the script runs it as a subprocess; `WAYBACK_MAIN_PYTHON` points at another interpreter |
| `builtin` | stdlib: drops blocks that are mostly link text, and blocks repeated verbatim down the page | fallback when trafilatura is absent; keeps some menu text, so a `--start`/`--end` crop still beats it for a one-off |
| `auto` (default) | trafilatura if available, else builtin, and says which one on stderr (`main: trafilatura extraction`) | always |

`--engine trafilatura` exits with the install command instead of degrading, when what you want is the good extractor. Extraction never fails a command: an empty trafilatura result falls back to the builtin cut with a warning.

## Reading a summary (`--stat`, `--stat-only`)

The summary is a **word-inventory change**, not a diff alignment: `margin -2 / markets +1` means the page stopped saying "margin" twice and started saying "markets" once. Consequences worth knowing:

- A word that only **moved** is not reported (the diff shows the move; the summary stays quiet). This is why the summary does not double-count a reordered paragraph.
- Stopwords and lone punctuation are counted out (they dominate any bag of words); the diff still contains them, because they carry the alignment. `--stat-words 40` widens the list when the top 12 are all template-ish words.
- `history --stat` also prints one `===== net <first> -> <last> (N versions) =====` block, which is the direct answer to "what does the current page say that the 2019 one did not".
- `--stat-only` keeps the same pipeline (body extraction + template filter) and drops just the diff text, so a 36-capture history prints ~20 lines instead of ~600.

## Sources

| Source | What it adds | Limits |
|---|---|---|
| `ia` Wayback Machine | densest history; the only one with scripted `save` and the only one that sweeps a whole host (`--domain`, `matchType=domain`) | sites can opt out; archive.org throttles or refuses (429, or TLS refused, seen 2026-10-31, 2026-11-11, 2026-11-18). A 429 gets one 5 s retry, then `ia` is dropped for 15 min with a one-line notice (`WAYBACK_IA_BLOCK_TTL=0` disables) instead of stalling every command on it. `save` then tells you to use archive.ph in Chrome |
| `cc` Common Crawl | pages Wayback missed or that excluded archive.org; still answers when archive.org is down | monthly samples, not every page every crawl; robots.txt honoured and many news/corporate sites block CCBot since 2023; a crawler, so no `save` exists |
| `pt` Arquivo.pt | a third independent copy, older pages; covers many non-.pt sites too (osttra.com, nomura.com have captures) | sparser than Wayback; matches URLs **exactly** — wildcards and `--domain` are refused with a notice, never silently widened; its ArchivePageNow is a web form with a consent checkbox, and captures join the archive later, so no scripted save |

## Gotchas
- **Common Crawl** lookups skip the index server (index.commoncrawl.org, which 503/504s for hours): the script binary-searches each crawl's `cluster.idx` on data.commoncrawl.org with Range reads and gunzips the matching CDX block, about 16 requests / 0.5 MB per crawl, 3 crawls at a time (`WAYBACK_CC_WORKERS`; 3 showed no throttling, 5 was barely faster). Without `--from` it searches the newest 12 of 129 crawls (about a year, ~13–40 s depending on the network); `--from 2020` (~70 crawls) takes ~1.5 min. The crawl list (`collinfo.json`) is cached in `~/.cache/wayback-skill/` for a week and used stale when the server is down; with no cache, crawl dates are approximated from the crawl IDs. Prefix sweeps stop after 20 index blocks (~60k index lines) per crawl and warn.
- CC is shallow per page but broad per site: a `--domain` sweep returns what CC actually crawled, sometimes a few dozen pages for a whole corporate site, so treat it as a sample, not a sitemap.
- CC keys are SURTs: `www.`, scheme, fragment, default port and a trailing slash are ignored, case-insensitive, query params sorted. So `https://www.x.com/a/` and `x.com/a` are the same lookup, but `x.com/a?utm=..` is a different page; use `x.com/a*` to catch query variants.
- CC records are cut at 1 MiB (before CC-MAIN-2025-13) or 5 MiB; the script warns `record truncated`. Big PDFs are often incomplete. Crawls 2008–2012 are ARC, not WARC (handled, but less tested). CCBot runs no JavaScript, so SPA captures are shells, as in Wayback.
- CC and Arquivo CDX are pywb: no `collapse=digest`, so dedup is client-side; filters use `filter=status:200` / `filter=!status:200` / `filter=~field:regex`.
- `list`/`history` use CDX with `collapse=digest`, so captures whose bytes did not change are hidden. Captures that differ only in boilerplate (a timestamp, a cookie banner) still show up; `--start`/`--end` cropping makes their diffs empty.
- `archive.org/wayback/available` often returns empty for archived sites; don't trust it, use CDX.
- `id_` in the fetch URL returns the original page without the Wayback toolbar; the script does this.
- Text extraction keeps nav, cookie banners and footers in `<name>.txt` (they are also evidence of what the page looked like) and only `--main`, `--raw` or `--start`/`--end` remove them. Because body text is far shorter than the page, `history` skips captures under `--min-chars 300`; raise it when a template change is what you are looking for, lower it for one-paragraph pages. Every capture still has a `.full.txt`, so a wrong crop or a wrong extractor costs a re-run, not a refetch.
- Many captures of JS-rendered sites (careers portals, SPAs) are empty shells or "position filled" pages. Check the text length before diffing; try other URL variants (with/without `www`, trailing slash, query string) or an aggregator copy (eFinancialCareers, LinkedIn, Indeed).
- `diff`/`history` fetch 4 captures at a time and cache each uncropped text as `<dir>/<timestamp>.full.txt`. When the script warns `--start not found` / `--end not found`, or skips most captures as short, open a `.full.txt`, fix the regex, and re-run with the same `-o`: no refetch. `history --max N` limits a page with 100 captures to the newest N.
- `id_` replays the archived response, sometimes still gzip-encoded; the script decompresses gzip/deflate and warns on anything still binary (brotli). A warned capture's diff is noise.
- Retries: 5xx and timeouts back off (Retry-After honoured); 429 gets one 5 s retry, then the source is dropped — `retry in 5s` and `ia: skipped` lines are normal. A connection cut mid-read (Arquivo.pt raises SSL `UNEXPECTED_EOF` when four history fetches overlap) is retried; a refused handshake is not. Before that retry existed, 9 of 36 captures silently went missing from one history run, and a missing capture also changes which lines count as shared — so watch the `N versions` line against `list`'s count.
- Useless for login-gated pages.
- `save` uses unauthenticated Save Page Now: 10–60 s per page, throttled after a burst. Sites that block the crawler return 520/523; the script then prints the latest existing capture and warns `no new capture was made`, so check that warning before citing the timestamp as "today". Login-gated pages save as a login wall.

## Beyond the script
Checked from this Mac on 2026-10-31 and 2026-11-18; not wired into the script.

| Tool | What it adds | How |
|---|---|---|
| archive.today (archive.ph) | on-demand saves that render JavaScript; many paywalled/news pages | Chrome only: curl gets a bot wall or no connection (still true 2026-11-18). `https://archive.ph/newest/<url>` or the timemap page |
| urlscan.io rendered DOM | the DOM and screenshot of a JS site as someone else's browser saw it | needs a free API key: `https://urlscan.io/api/v1/result/<uuid>/` and `/dom/<uuid>/` answer 403 without one. `discover --source urlscan` uses the keyless search endpoint |
| Google/Bing cache | — | gone |

`find` and `discover` are wired in (Arquivo.pt full-text search, OTX url_list, urlscan search). `discover` drops tracking pixels, asset URLs and unsubscribe links and collapses URLs that differ only in a long opaque token — OTX is a threat-intel feed, so raw output is mostly one click-tracking URL per recipient. `--all` keeps everything; the output is a URL list to hand to `list`, not an archive.

Not worth using: Memento TimeTravel (DNS no longer resolves), Library of Congress web archive and perma.cc (Cloudflare challenge), UK Web Archive (no public CDX endpoint at the path tried), Google/Bing cache (gone).
