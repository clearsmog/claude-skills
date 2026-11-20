---
name: image-search
description: Search the web for images (photos, logos, icons, stock) and download them with Typst embedding code. Use when a document needs a real photo, a company logo, an icon, or a licence-clear stock image. 中文说法 — "找张图", "搜图片", "配图", "这个图哪来的", "下载图片".
allowed-tools: Bash, Read
argument-hint: <query> [--logo|--icon|--stock] [--engine <name>] [-n 1] [--aspect 16:9 --crop]
---

Parse `$ARGUMENTS` into flags for the bundled script and run it in **one** Bash call. The script handles search, ranking, dedupe, format normalisation, licence metadata, and Typst code.

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/image_search.py "<query>" --typst [flags...]
```

Keys are discovered automatically — env first, then fish universals (`~/.config/fish/fish_variables`) and `~/.zshenv`. No shell gymnastics needed; `--list-engines` shows which are loaded.

## Workflow

0. **Does the picture exist at all?** This skill only finds what someone already published. For a
   scene, character, product shot or illustration that has to be invented - "a paper boat in a
   neon alley", "our mug on a walnut desk" - search once to be sure, then hand off to
   `/grok-media` (`image`, `edit`, `video`). Generated files carry no licence and need no credit;
   never pass off a generated image as a photograph of a real event or person.
1. **Pick the mode** from the table below. Defaults are fine for photos.
2. **Run once**, read the `Saved:` block (path, size, dimensions, engine, licence).
3. **Verify the pixels**: `Read` the saved file and check it shows the requested subject, is not watermarked, and is not a logo collage or a chart. This is the step that catches wrong-entity logos and unrelated results — the script cannot see images.
   * Wrong or weak? Re-run with `-n 3` and pick, or change `--engine`, or rephrase (see Query craft).
4. **Report** the path and the Typst figure. Keep the licence/credit line when the source is CC, stock, or NASA.

## Modes

| Mode | Flag | Ladder |
|------|------|--------|
| Photo (default) | none | brave → serpapi → ddgs → commons → openverse |
| One channel | `--engine X` | `commons` `openverse` `ddgs` `nasa` `brave` `serpapi` |
| Logo | `--logo` | Simple Icons SVG → Brandfetch → Commons SVG → Logo.dev PNG → favicon |
| Icon | `--icon` | Iconify SVG (diagrams, inline glyphs) |
| Stock | `--stock` | Pixabay → Pexels → Unsplash (licence-clear, download-friendly order) |
| Direct URL | `--url <url>` | fetches and normalises one URL |

**Logo note**: `--logo "Alphabet Inc"` resolves the domain from Wikidata `P856` (not `alphabet.com`, which is a car-leasing firm), then tries vector sources first. A 200 px PNG is the floor, not the goal — for print, prefer a Commons SVG wordmark or `--engine commons` on `"<company> logo"`.

## Query craft

| Source | Query that works | Query that fails |
|--------|------------------|------------------|
| ddgs / serpapi / brave | `golden gate bridge at dusk`, `team meeting whiteboard` | `bridge`, `office` (too generic, returns collages) |
| commons | `Golden Gate Bridge`, `Angela Merkel 2021`, `Blue whale` | abstract concepts, product shots, brand marks |
| openverse | `mountain lake`, `street market` | anything needing a specific real place bearing |
| stock | `business meeting`, `laptop on desk` | famous people, branded products |
| logo | legal name: `Alphabet Inc`, `JPMorgan Chase` | product names, subsidiaries, abbreviations |
| icon | `database`, `shield check` (kebab nouns) | sentences, brand names |

Roughly: concrete nouns and one qualifier beat long natural-language sentences. Add "interior / skyline / close-up / diagram" to steer composition.

## Flags

`--engine`, `--serpapi-engine google_images|bing_images|yandex_images|baidu_images|google_images_light`, `--list-engines`,
`-n/--num`, `-d/--dir` (default `images`), `-o/--output`, `--size large|medium|icon`, `--type photo|clipart|face|lineart`,
`--aspect 16:9`, `--crop`, `--max-width` (1600), `--max-kb` (2500), `--min-width`, `--format auto|jpeg|png`, `--white-bg`,
`--typst`, `--width` (80%), `--fit cover|contain|stretch`, `--caption`, `--json`, `--no-cache`, `--no-serpapi`, `--no-manifest`, `-v`.

Defaults keep documents small: 1600 px wide, JPEG q88, target ≤2.5 MB. Use `--format png` for diagrams with transparency, `--fit cover --crop` for full-bleed figures.

## Budget and failure behaviour

- SerpAPI free plan is 250 searches/month **shared with the `reddit` skill**; each default-mode call spends at most one. Current-month usage prints at the end; a 429 is reported and the ladder moves on instead of failing.
- DuckDuckGo (`ddgs`) is keyless but rate-limits bursts — three retries with backoff, then the next engine.
- Openverse anonymous tier is ~20 req/min, 200/day. Commons and NASA are unmetered (be a good citizen: the script sends a real UA).
- Responses are cached 24 h under `~/.cache/image-search`; `--no-cache` forces fresh results. Cache hits do not spend quota.
- Every engine failure lands in the JSON `errors` array with `--json`, so a failed run is diagnosable without re-running.

## Licence and attribution

`<dir>/.image-search-manifest.json` records engine, source page, image URL, licence, author, and dimensions for each file.

- Commons / Openverse: licence is printed (`CC BY-SA 4.0`, `BY 2.0`, …). CC BY and CC BY-SA need credit + licence name in the document.
- NASA: public domain, no credit required.
- Unsplash: the API terms require hotlinking the returned URL, crediting the photographer and Unsplash, and pinging the download endpoint — the script saves a local copy for convenience, so treat Unsplash output as internal-review-only unless you add the credit line.
- Logo.dev/favicon marks: trademarks of their owners; use for identification, not decoration.
- Web images with `unknown (web image)`: check before publishing anything external.
