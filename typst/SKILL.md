---
name: typst
description: Syntax guide and ecosystem reference for writing Typst (.typ) files. Use this skill when writing, editing, or debugging Typst documents. Covers core syntax, common errors, packages, and best practices.
license: MIT
---

# Typst Skill

**Current version**: Typst 0.15.x

## Smart Defaults

Defaults, unless the user or the project's existing files say otherwise:

1. Import `@local/qk:2.2.0` — `#import "@local/qk:2.2.0": *`
2. Use the `qk-doc` or `qk-report` preset
3. Use touying for presentations (not raw page dimensions) — see `references/touying-guide.md`
4. `#set figure(placement: auto)` — prevents blank half-pages
5. Add `alt:` to images — `image("path.png", alt: "description")`
6. Escape `$` in content — scan for bare `$` before compiling
7. **Default fonts**: Libertinus Serif (body), Inter (headings), New Computer Modern Math (math), Fira Code (code)
8. **Default compile**: `typst compile --root .. Source/<file>.typ`
9. Template when the request doesn't settle it: Study Guide
10. Visual tool when the content doesn't settle it: diagrams → fletcher; charts → see decision tree (default → lilaq; extremely simple → cetz-plot (rare); statistical kde/pair → matplotlib+seaborn; grammar → plotnine; complex with Python data → matplotlib)
11. Scan the project for existing `.typ` files and match their style (fonts, colors, qk preset)

## New Document Decision Tree

```
User request → scan for keywords:
  "resume/CV/job"           → CV / Résumé template
  "slides/presentation"     → Presentation (touying — metropolis default)
  "lecture/class/academic"   → Academic Lecture (touying — university theme)
  "essay/thesis/paper"      → Essay
  "report/brief/client"     → Business Report
  "research/analysis"       → Research Report
  "study guide/revision"    → Study Guide
  "reference/glossary"                      → Annotated Reference
  "cheatsheet/reference card/formula sheet" → Cheatsheet template
  "exam/problem set/homework"              → Exam template
  "flashcard/Q&A/quiz"                     → Flashcard template
  ambiguous?                → ask purpose + audience → pick template
```

**Steps:**
1. Auto-detect template from keywords above
2. Import `@local/qk:2.2.0` at top
3. Use `qk-doc` or `qk-report` preset when applicable
4. Auto-select template. State choice in Phase 3 summary. User can re-invoke with explicit type override if wrong.
5. Build from `references/templates.md`
6. Custom styles are fine — templates are starting points, not constraints

## Visual Tool Routing (compact)

**Diagrams** (always native Typst — NEVER Python):

| Need | Tool |
|------|------|
| Flowcharts, trees, ER, state diagrams | `fletcher` |
| Sequence diagrams | `chronos` |
| Gantt charts | `timeliney` |
| Linear timelines | `herodot` |

**Charts** (generate SVG, embed with `#figure(image(...))`):

| Need | Tool |
|------|------|
| Extremely simple charts where lilaq is overkill (rare) | **cetz-plot** (Typst native, `qk-cycle` colors) |
| Most charts (line, bar, scatter, violin, heatmap, contour, subplots) | **lilaq** (Typst native, font-matched, `as lq`) |
| Statistical plots (kde, pair plots) | **matplotlib + seaborn** (`use()`, SVG) |
| Grammar-of-graphics / faceted plots | **plotnine** (`theme_qk()`, SVG) |
| Complex charts with Python data pipeline | **matplotlib** (full API, SVG) |

**Images & layout:**

| Need | Tool |
|------|------|
| Tables, boxes, grids | Typst native |
| Mind maps | `/mindmap` (auto-invoke) |
| Conceptual illustrations | No generator: a diagram, or suggest an `anatomy` figure and wait for a yes, or a placeholder `#rect` |
| Key mechanism drawn as a real machine (isometric, exact numbers) | `/anatomy` → `scripts/anatomy-to-typst.mjs` |
| Real photos, logos | `/image-search` (auto-invoke) |

Detail and examples in `references/tool-routing.md`.

## Proactive Behaviors

### Visual Auto-detection

When writing Typst documents, add a visual wherever it makes the content clearer, without waiting to be asked. Route by content type: diagrams → native Typst (fletcher/chronos/timeliney/herodot) up to about 10 nodes, the `diagram` skill (D2) for larger, multi-party or network diagrams; charts → follow the Charts table above (cetz-plot for very simple, lilaq for most, matplotlib/seaborn/plotnine for statistical or grammar-of-graphics) — generate SVG, embed; images → `/image-search` / `/mindmap`.

| Content pattern | Visual to add | Tool |
|-----------------|---------------|------|
| Comparison grids, attribute tables | Styled table | Typst native |
| Callout boxes, styled layouts | `rect()` / `block()` | Typst native |
| Sequential steps, decision logic | Flowchart / decision tree | `fletcher` |
| Process with inputs/outputs | Workflow diagram | `fletcher` |
| System architecture, ER diagrams | Block / entity diagram | `fletcher` |
| Hierarchy or taxonomy | Tree diagram | `fletcher` or `/mindmap` |
| Topic overview, concept map | Mind map | `/mindmap` |
| Request-response, API flows | Sequence diagram | `chronos` |
| Project schedule, phases | Gantt chart | `timeliney` |
| Historical events, evolution | Timeline | `herodot` or `timeliney` |
| Extremely simple chart where lilaq is overkill (rare) | Line/bar/scatter chart | cetz-plot (Typst native) |
| Most charts (multi-series, subplots, violin, heatmap, contour) | Data visualization | lilaq (Typst native, font-matched) |
| Statistical chart (kde, pair plots) | Statistical plot | matplotlib+seaborn (SVG) |
| Faceted / grammar chart | Layered plot | plotnine (SVG) |
| Company logo, brand mark | Logo image | `/image-search --logo` |
| Real-world photograph | Photo | `/image-search` |
| Concept with analogy, metaphor | Illustration | `/anatomy` or a diagram; no AI image generator is available |
| The document's central mechanism, where precise parts and true numbers matter (at most one or two per document; each takes up to an hour) | Isometric machine figure | `/anatomy`, then `scripts/anatomy-to-typst.mjs` |

See `references/tool-routing.md` for full examples, fallback chains, and auto-invoke rules.

### Content Structure

- Suggest TOC (`#outline()`) at 4+ sections
- Suggest file split at 40+ pages — see `references/common-patterns.md` "Large Documents"
- Convert prose lists to tables when 3+ items with attributes

### Component Library Auto-use

When writing content, automatically convert matching patterns to `@local/qk:2.2.0` components:

| Content pattern | Use instead |
|-----------------|-------------|
| Warning paragraph | `warning[...]` |
| Key point / takeaway | `keypoint[...]` |
| Tip or best practice | `tip[...]` |
| Common mistake / trap | `trap[...]` |
| Step-by-step procedure | `step-box("Title", [...])` |
| Key equation / formula | `formula-box("Title", [...])` |
| KPI or metric highlight | `stat-card("value", "label")` |
| Frequency indicator | `freq-badge("HIGH")` / `freq-badge("MEDIUM")` / `freq-badge("LOW")` |
| MCQ answer explanation | `answerbox("A", "why", "trap", "concept")` |
| Analogy / intuition | `analogy[...]` |
| "Why this matters" | `whycare[...]` |

### Cross-referencing

Add `<label>` + `@ref` for recurring concepts across sections.

### Accessibility (Typst 0.14+)

- `alt:` on all figures — `image("path.png", alt: "description")`
- Semantic heading hierarchy — don't skip levels
- `table.header()` for repeating headers — improves PDF/UA accessibility

## Fallback Chains

| If this fails... | Try... |
|------------------|--------|
| `/image-search` | Placeholder `#rect(width: 100%, height: 4cm, fill: luma(240))[Image placeholder]` |
| `/mindmap` | `fletcher` tree diagram |
| matplotlib | Check `.venv` → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` | Isolate with `/* ... */`, compile incrementally |

## Reference File Index

| When you need... | Read... |
|------------------|---------|
| Syntax, errors, special chars | `references/quick-ref.md` |
| `@local/qk:2.2.0` API | `references/component-library.md` |
| Visual tool details, examples, fallbacks | `references/tool-routing.md` |
| Document preambles | `references/templates.md` |
| Table patterns, show rules, large docs | `references/common-patterns.md` |
| Page layout, spacing, figures, curves | `references/layout-patterns.md` |
| Math mode traps | `references/math-pitfalls.md` |
| Package imports | `references/packages.md` |
| Touying presentations (themes, slides, speaker notes) | `references/touying-guide.md` |
| Visual verification (PNG rendering, spot-checks) | `references/visual-verification.md` |
| Quality gates, rubrics, dispatch table | `references/quality-gates.md` |
| Data-driven generation (JSON, CSV, batch, variants) | `references/data-driven.md` |
| `sym.*` symbols | `references/symbols.md` |

## Offline API and Package Search

Look up the exact signature before writing an unfamiliar function or parameter; don't guess from memory. Index covers Typst 0.15.1 (the installed version).

```bash
python3 -I ${CLAUDE_SKILL_DIR}/scripts/search-api.py --name text            # exact: text, str.position, table.cell
python3 -I ${CLAUDE_SKILL_DIR}/scripts/search-api.py "rotate content angle" --top 5
python3 -I ${CLAUDE_SKILL_DIR}/scripts/search-packages.py "gantt chart" -n 5   # Typst Universe, filtered to installed compiler
python3 -I ${CLAUDE_SKILL_DIR}/scripts/search-packages.py --category cv -n 5
```

Scripts and `data/` come from [lucifer1004/claude-skill-typst](https://github.com/lucifer1004/claude-skill-typst) (MIT). After a Typst upgrade, or to refresh the package index, copy `skills/typst/data/{api,api-bm25,packages,packages-bm25}.json` from that repo into `${CLAUDE_SKILL_DIR}/data/`.

**Text-level check without rendering:** `typst compile doc.typ /dev/stdout -f html --features html 2>/dev/null` dumps headings, paragraphs and tables as HTML — cheaper than PNG when only content or structure needs checking.

## Version Notes (0.13–0.15)

| Feature | Ver | Description |
|---------|-----|-------------|
| Variable fonts | 0.15 | Supported at last — axis selection via `text(variations: (...))`; Apple variable fonts (`New York`, `SF NS`) now load |
| `within` selector | 0.15 | Match elements inside a container — simplifies introspection |
| `divider` element | 0.15 | Thematic break (templates can customize) |
| Multiple bibliographies | 0.15 | Independent bibliographies via `bibliography(target:, group:)` |
| MathML HTML export | 0.15 | Equations export to web (was a hard limitation before) |
| `typst eval` | 0.15 | General CLI introspection — supersedes `typst query` |
| Tagged PDFs, PDF/UA-1 | 0.14 | Accessible PDFs by default |
| `figure.alt` / `image(alt:)` | 0.14 | Alt text for screen readers |
| `pdf.attach` | 0.14 | Attach files (replaces `pdf.embed`) |
| PDF as image format | 0.14 | `image("file.pdf")` |
| Multiple table headers | 0.14 | Hierarchical headers repeat across pages |
| `curve` function | 0.13 | Bezier drawing (replaces `path`) |

**Removed in 0.15** (were deprecated, now gone): `path` element → use `curve` · `pdf.embed` → `pdf.attach` · `image.decode` / scoped decode fns → pass bytes directly · `pattern` type → `tiling`
**Other migrations**: polylux:0.3.1 → `polylux:0.4.0` or `touying`
**Breaking (0.15)**: file paths must use forward slashes only (no backslashes)

| touying 0.8.0 | 0.6+ | Presentation framework — `#show: theme.with(...)` API (not the old `register()` pattern) |

## CLI Commands

```bash
typst compile document.typ                     # Compile to PDF
typst compile document.typ --root ..           # Set project root
typst compile document.typ out.pdf --pages 1-5 # Specific pages
typst watch document.typ                       # Watch and recompile
typst fonts                                    # List available fonts
typst eval --in doc.typ 'query(heading.where(level: 1)).len()'   # Introspect structure
typst query doc.typ "heading.where(level: 1)"  # Deprecated form — still runs, with a warning
```

**`--root` flag:** When a `.typ` file uses `#import` or `#image()` with paths outside its directory, set `--root` to the project root.

**Batch compile:** `for f in *.typ; do typst compile "$f"; done`

## Conventions

- Source files in `Source/`, compiled PDFs in `PDFs/`
- Compile with `--root ..` when `.typ` references parent directory assets
- For multi-file projects: `main.typ` + `#include` sections + shared `lib.typ`
- File naming: lowercase-kebab-case (e.g., `portfolio-theory-guide.typ`)

## Fonts

| Font | Style | Notes |
|------|-------|-------|
| New Computer Modern | Academic serif | Default; bundled with Typst |
| Georgia | Readable serif | Safe on macOS |
| Helvetica Neue | Clean sans-serif | macOS only |

**Variable fonts (supported since 0.15):** Apple variable fonts and others now load directly — no need to install static `.otf`/`.ttf` versions. Select an axis with `#set text(font: "New York", variations: (wght: 600))`. The "Variable"/"Var"/"VF" suffix in a font's name is trimmed automatically, so reference the base family name. Note Apple's *exposed* family names differ from marketing names: San Francisco is `SF NS` (not "SF Pro"), and the serif is `New York` — run `typst fonts` to confirm. (On Typst ≤ 0.14 these failed with "variable fonts are not currently supported" — only relevant if pinned to an old binary.)

**CJK fallback:** `#set text(font: ("New Computer Modern", "Songti SC"))`

## Documentation

- [Official Reference](https://typst.app/docs/reference/)
- [Package Registry](https://typst.app/universe/)
- [Tutorial](https://typst.app/docs/tutorial/)
- [Changelog](https://typst.app/docs/changelog/)
