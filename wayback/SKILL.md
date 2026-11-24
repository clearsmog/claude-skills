---
name: wayback
description: >-
  Recover dead or changed pages and compare a page's versions over time across the Wayback Machine, Common Crawl, Arquivo.pt and three more archives: list distinct captures, fetch one as text, word-diff two versions or an old capture against today. Use whenever a link 404s, a page was changed or removed, or the task asks what a job ad, team page, policy or company site said before or which pages a site once had; also when Wayback is down or has no capture. 中文说法 — "打不开了", "之前是什么内容", "改版前", "历史版本", "存档", "快照", "网页变了". Not for a reachable page that refuses you (403, Cloudflare, login wall, paywall: cloudflare skill or a session cookie) or reddit.com threads (reddit skill).

---
# Wayback Machine (+ Common Crawl, Arquivo.pt, ghostarchive, Megalodon, UK Web Archive)

Script: `${CLAUDE_SKILL_DIR}/scripts/wayback.py` (stdlib only; run with `python3 -I`). Optional: trafilatura in a venv for body extraction (see 正文). No MCP needed.

| Need | Command |
|---|---|
| Distinct captures (dedup by content, HTTP 200 only) | `wayback.py list <url> [--source ia\|cc\|pt\|gh\|mg\|uk\|ia,pt] [--from 2020] [--to 2024] [--limit 20]` |
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
| Old capture against the page as it is now | `wayback.py diff <url> <A> live -o <dir>` (`live` works as a ref in `fetch` too) |
| Diff, plus a word-level summary of what was added/removed | add `--stat` (`--stat-words N` for more terms) |
| Only the summary, no diff to read | `--stat-only` |
| "What did this JD start asking for over the years" | `wayback.py history <url> --stat-only --from 2019 -o <dir>` — the `net` block compares the oldest and newest capture |
| Pick the extractor | `--engine auto\|trafilatura\|builtin` |

- `A`/`B` are refs from `list` (`20210909191632` = Wayback, `cc:<ts>` = Common Crawl, `pt:<ts>` = Arquivo.pt, `gh:<id>` = ghostarchive), `live` (the page fetched now, saved as `live-<UTC ts>`), or local `.html`/`.pdf` files and `.txt`/`.md` text, which is read line for line rather than parsed as HTML. So captures from different archives diff against each other and against today's page.
- `live` exits with a pointer to the cloudflare skill when the site answers 403/429/503 or serves a bot challenge: run `cf text <url> > today.txt` and pass `today.txt` as the ref. A certificate error on macOS retries once with the system Keychain roots, because the `/etc/ssl/cert.pem` Python reads lags them (example.com failed that way on 2026-11-19).
- `fetch` writes `<name>.html`, `<name>.txt` (visible text) and `<name>.links.txt` (absolute URLs found in the page, with anchor text). Read `.links.txt` to find contact/apply/next pages that the text alone loses. Hostile/odd encodings are handled: the capture's own charset (header, then `<meta charset>`) is used, so 2005-era windows-1252 or Shift_JIS pages do not lose accents. PDF captures go through `pdftotext -layout` when it is installed.
- `mg:<ts>` (Megalodon) and `uk:<ts>` (UK Web Archive) refs are **listing only**: `fetch` on one prints the browser link (Megalodon) or explains the legal-deposit block (UKWA) instead of text, and `history` leaves both sources out. Their captures still answer "did this page exist on that date".
- `list`/`history` query all archives by default (history: the four whose text can be fetched), merge by time and drop captures whose payload digest another archive already has (Wayback ingests part of Common Crawl, so shared captures are common; the Wayback ref is kept). The three are queried in parallel, and listings are cached on disk for 30 min (`--fresh` refetches, `WAYBACK_CACHE_TTL` changes the TTL): the second lookup of the same URL is instant. Common Crawl lookups in a crawl that ended over 30 days ago are cached for good, since that index no longer changes: a `--from 2025` rerun went from 23 s to 0.1 s. A default cold run takes ~15–40 s depending on the network, most of it Common Crawl; `--source ia,pt` answers in a few seconds when a quick look is enough. Narrowing `--source` can miss captures: on osttra.com, only Common Crawl had the page after June 2026.
- `diff` prints a word-level `git diff` (`--line` for line-level). `--start`/`--end` are multiline regexes that cut the text down to the body, dropping nav, cookie banners and footers.
- **`history` drops what every capture shares.** A line present in *all* captures cannot be a change, so it is removed from the diff and listed in `<dir>/template.txt` (count, then text) — that file is also the fastest way to write a `--start`/`--end` crop later. Three guardrails: it is off below 3 captures (`template filter off: 2 capture(s), need 3`), it never uses a partial majority (a line that changed once and then stayed is *not* template — a 70% rule was tried and erased exactly those changes), and if every line turns out to be shared it says `nothing changed between them` instead of printing an empty diff. `<dir>/*.txt` holds the filtered view; `.full.txt`/`.main-<engine>.txt` keep the unfiltered extraction (one body cache per extractor, so installing trafilatura never reuses a builtin cut). On osttra.com (36 captures) it dropped 72 of 244 body lines (30%) as template.
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
| `ia` Wayback Machine | densest history; the only one with scripted `save` and the only one that sweeps a whole host (`--domain`, `matchType=domain`) | sites can opt out; archive.org throttles or refuses (429, or TLS refused, seen 2026-10-31, 2026-11-11, 2026-11-18). A 429 or a refused TLS handshake gets `ia` dropped for 15 min (a 429 first gets one 5 s retry) with a one-line notice (`WAYBACK_IA_BLOCK_TTL=0` disables) instead of stalling every command on it. `save` then tells you to use archive.ph in Chrome |
| `cc` Common Crawl | pages Wayback missed or that excluded archive.org; still answers when archive.org is down | monthly samples, not every page every crawl; robots.txt honoured and many news/corporate sites block CCBot since 2023; a crawler, so no `save` exists |
| `pt` Arquivo.pt | a third independent copy, older pages; covers many non-.pt sites too (osttra.com, nomura.com have captures) | sparser than Wayback; matches URLs **exactly** — wildcards and `--domain` are refused with a notice, never silently widened; its ArchivePageNow is a web form with a consent checkbox, and captures join the archive later, so no scripted save |
| `gh` ghostarchive.org | on-demand saves that render JavaScript (the archive.ph niche): news, social posts, pages people cited. Text comes from the save's WARC, parsed by the script | search is by substring and paginated (~20 hits a page, `WAYBACK_GH_PAGES`, default 5): results are filtered to the asked URL, so a popular host's root can sit beyond page 5. Older saves have no WARC and open in Chrome only. Saving needs a browser |
| `mg` Megalodon (ウェブ魚拓) | Japanese pages, some captures back to 2008 | exact URL only; **listing only**: its replay answers scripts with an "アクセス増加" error page (checked 2026-11-19 with browser headers and cookies), so open the printed link in Chrome |
| `uk` UK Web Archive (British Library) | .uk sites since 2004, prefix and `--domain` sweeps | **listing only**: almost every capture is legal deposit (`access: block`, replay HTTP 451) and readable only in a UK reading room. Proof that a page existed on a date, not its text |

## Before trusting a result

- Many captures of JS-rendered sites (careers portals, SPAs) are empty shells or "position filled" pages. Check the text length before diffing; try other URL variants (with/without `www`, trailing slash, query string) or an aggregator copy (eFinancialCareers, LinkedIn, Indeed).
- When the script warns `--start not found` / `--end not found`, or skips most captures as short, open a `.full.txt`, fix the regex, and re-run with the same `-o`: no refetch. `history --max N` limits a page with 100 captures to the newest N.
- Watch the `N versions` line against `list`'s count: a capture lost to a network error also changes which lines count as shared.
- `save` on a site that blocks the crawler prints the latest existing capture and warns `no new capture was made`: check that warning before citing the timestamp as "today". Login-gated pages save as a login wall, and the archives are useless for them.

Archive internals (Common Crawl index reads, SURT keys, truncation, dedup, gzip, retries, Save Page Now limits): `references/archive-internals.md`. Tools beyond the script (archive.ph, urlscan DOM, Memento, sources checked and rejected): `references/beyond-the-script.md`.
