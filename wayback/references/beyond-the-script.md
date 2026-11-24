# Beyond the script

Read by the wayback skill when the script has no capture or the page needs a JavaScript-rendered save.

Checked from this Mac on 2026-10-31 and 2026-11-18; not wired into the script.

| Tool | What it adds | How |
|---|---|---|
| archive.today (archive.ph) | on-demand saves that render JavaScript; many paywalled/news pages | Chrome only: curl gets no connection on archive.ph and on the archive.is/archive.md mirrors alike (2026-11-19), so a mirror does not help. `https://archive.ph/newest/<url>` or the timemap page. ghostarchive (`--source gh`) covers the same niche from the script |
| urlscan.io rendered DOM | the DOM and screenshot of a JS site as someone else's browser saw it | needs a free API key: `https://urlscan.io/api/v1/result/<uuid>/` and `/dom/<uuid>/` answer 403 without one. `discover --source urlscan` uses the keyless search endpoint |
| Google/Bing cache | — | gone |

Memento aggregation: `timetravel.mementoweb.org` no longer resolves and the public MemGator at memgator.cs.odu.edu answers 404; MemGator itself (github.com/oduwsdl/MemGator, last release 1.0-rc9, 2024-05) can be self-hosted, but `list` already merges six archives by payload digest, so it adds nothing here.

`find` and `discover` are wired in (Arquivo.pt full-text search, OTX url_list, urlscan search). `discover` drops tracking pixels, asset URLs and unsubscribe links and collapses URLs that differ only in a long opaque token — OTX is a threat-intel feed, so raw output is mostly one click-tracking URL per recipient. `--all` keeps everything; the output is a URL list to hand to `list`, not an archive.

Not worth using (checked 2026-11-19): Library of Congress web archive and perma.cc (Cloudflare challenge), Archive-It and vefsafn.is (session-verification wall), Stanford SWAP (403), Google/Bing cache (gone).
