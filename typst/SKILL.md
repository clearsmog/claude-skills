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
7. **Default fonts** (qk presets): Libertinus Serif (body), Inter (headings), New Computer Modern Math (math), Fira Code (code). Typst's own defaults, with no preset, are Libertinus Serif, New Computer Modern Math and DejaVu Sans Mono
8. **Default compile**: `typst compile <file>.typ`. Add `--root <project root>` only when the file uses root-relative paths (leading `/`) or reaches into a parent directory (`../`); see "CLI Commands"
9. Template when the request doesn't settle it: Study Guide
10. Visual tool when the content doesn't settle it: see "Visual Tool Routing" below
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
4. Auto-select template. User can re-invoke with explicit type override if wrong.
5. Build from `references/templates.md`
6. Custom styles are fine — templates are starting points, not constraints

## Visual Tool Routing

Add a visual wherever it makes the content clearer, without waiting to be asked. Read `references/tool-routing.md` before adding any visual: it has the size limits, the content-pattern table, examples, and the cases where no visual should be added.

Priority order:

- Diagrams: native Typst (fletcher, chronos, timeliney, herodot) up to about 10 nodes and one actor; the `diagram` skill (D2) for larger, multi-party or network diagrams. Never Mermaid, Python or raster tools.
- Charts: lilaq by default; cetz-plot only for very simple ones; Python SVG (matplotlib/seaborn/plotnine) only for kde, pair or faceted plots, or an existing Python pipeline.
- Photos and logos: `/image-search`. Mind maps: `/mindmap`.
- Conceptual illustrations: there is no image generator. Use a diagram, or suggest an `anatomy` figure and wait for a yes, or leave a placeholder `#rect`.

## Proactive Behaviors

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

## Reference File Index

| When you need... | Read... |
|------------------|---------|
| Syntax, errors, special chars | `references/quick-ref.md` |
| `@local/qk:2.2.0` API | `references/component-library.md` |
| Visual tool routing, examples, qk plot style setup, fallbacks | `references/tool-routing.md` |
| Document preambles | `references/templates.md` |
| Table patterns, show rules, large docs | `references/common-patterns.md` |
| Page layout, spacing, figures, curves | `references/layout-patterns.md` |
| Math mode traps | `references/math-pitfalls.md` |
| Package imports | `references/packages.md` |
| Touying presentations (themes, slides, speaker notes) | `references/touying-guide.md` |
| Visual verification (PNG rendering, spot-checks) | `references/visual-verification.md` |
| Severity definitions and review verdict rules | `references/quality-gates.md` |
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
**touying 0.8.0**: themes use `#show: theme.with(...)` (the API since touying 0.6), not the old `register()` pattern

## CLI Commands

```bash
typst compile document.typ                     # Compile to PDF
typst compile --root . Source/document.typ     # From the project root, for "/..." or "../" paths
typst compile document.typ out.pdf --pages 1-5 # Specific pages
typst watch document.typ                       # Watch and recompile
typst fonts                                    # List available fonts
typst eval --in doc.typ 'query(heading.where(level: 1)).len()'   # Introspect structure
typst query doc.typ "heading.where(level: 1)"  # Deprecated form — still runs, with a warning
```

**`--root` flag:** The root defaults to the directory of the input file, which is enough when every import and image path stays inside that directory. A path with a leading `/` resolves against the root, and a `../` path that leaves the root fails with "would escape the project root". In both cases pass `--root <project root>` (the directory that contains everything the file reaches), not its parent.

**When a compile fails:** isolate the failing part with `/* ... */` and compile incrementally.

**Batch compile:** `for f in *.typ; do typst compile "$f"; done`

## Conventions

- Source files in `Source/`, compiled PDFs in `PDFs/`
- From the project root, compile with `typst compile --root . Source/<file>.typ` when a file in `Source/` uses `/...` or `../` paths; otherwise plain `typst compile Source/<file>.typ`
- For multi-file projects: `main.typ` + `#include` sections + shared `lib.typ`
- File naming: lowercase-kebab-case (e.g., `portfolio-theory-guide.typ`)

## Fonts

| Font | Style | Notes |
|------|-------|-------|
| Libertinus Serif | Text serif | Typst's default body font; bundled with Typst |
| New Computer Modern | Academic serif | Bundled with Typst; its Math companion is the default math font |
| Georgia | Readable serif | Safe on macOS |
| Helvetica Neue | Clean sans-serif | macOS only |

**Variable fonts (supported since 0.15):** Apple variable fonts and others now load directly — no need to install static `.otf`/`.ttf` versions. Select an axis with `#set text(font: "New York", variations: (wght: 600))`. The "Variable"/"Var"/"VF" suffix in a font's name is trimmed automatically, so reference the base family name. Note Apple's *exposed* family names differ from marketing names: San Francisco is `SF NS` (not "SF Pro"), and the serif is `New York` — run `typst fonts` to confirm. (On Typst ≤ 0.14 these failed with "variable fonts are not currently supported" — only relevant if pinned to an old binary.)

**CJK fallback:** `#set text(font: ("Libertinus Serif", "Songti SC"))`

## Documentation

- [Official Reference](https://typst.app/docs/reference/)
- [Package Registry](https://typst.app/universe/)
- [Tutorial](https://typst.app/docs/tutorial/)
- [Changelog](https://typst.app/docs/changelog/)
