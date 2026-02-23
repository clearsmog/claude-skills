---
name: typst
description: Syntax guide and ecosystem reference for writing Typst (.typ) files. Use this skill when writing, editing, or debugging Typst documents. Covers core syntax, common errors, packages, and best practices.
license: MIT
---

# Typst Skill

**Current version**: Typst 0.14.2 (Dec 2025)

## Smart Defaults

If you know nothing else, follow these rules:

1. **Always** import `@local/qk:1.0.0` — `#import "@local/qk:1.0.0": *`
2. **Always** use `qk-doc` or `qk-report` preset (unless user specifies custom)
3. **Always** `#set figure(placement: auto)` — prevents blank half-pages
4. **Always** add `alt:` to images — `image("path.png", alt: "description")`
5. **Always** escape `$` in content — scan for bare `$` before compiling
6. **Default fonts**: Libertinus Serif (body), Inter (headings), New Computer Modern Math (math), Fira Code (code)
7. **Default compile**: `typst compile --root .. Source/<file>.typ`
8. **When in doubt** about template: Study Guide
9. **When in doubt** about visual tool: Typst native first → cetz-plot → matplotlib

## New Document Decision Tree

```
User request → scan for keywords:
  "resume/CV/job"           → CV / Résumé template
  "slides/presentation"     → Presentation (16:9)
  "essay/thesis/paper"      → Essay
  "report/brief/client"     → Business Report
  "research/analysis"       → Research Report
  "study guide/revision"    → Study Guide
  "reference/glossary"      → Annotated Reference
  ambiguous?                → ask purpose + audience → pick template
```

**Steps:**
1. Auto-detect template from keywords above
2. Import `@local/qk:1.0.0` at top
3. Use `qk-doc` or `qk-report` preset when applicable
4. Confirm briefly: "I'll use the **Study Guide** template — sound good?"
5. Build from `references/templates.md`
6. Custom styles are fine — templates are starting points, not constraints

## Visual Tool Routing (compact)

| Need | Tool |
|------|------|
| Tables, boxes, grids | Typst native |
| Flowcharts, trees, ER, state diagrams | `fletcher` |
| Sequence diagrams | `chronos` |
| Gantt charts | `timeliney` |
| Simple charts (< 3 series) | cetz-plot |
| Complex charts (4+ series) | matplotlib |
| Mind maps | `/mindmap` (auto-invoke) |
| Conceptual illustrations | `/nano-banana` (auto-invoke) |
| Real photos, logos | `/image-search` (auto-invoke) |

Detail and examples in `references/tool-routing.md`.

## Proactive Behaviors

### Visual Auto-detection

When writing Typst documents, automatically identify content that benefits from visuals. Do NOT wait for the user to request them.

| Content pattern | Visual to add | Tool |
|-----------------|---------------|------|
| Sequential steps or phases | Timeline / flowchart | fletcher or timeliney |
| Decision logic (if/then) | Decision tree | fletcher |
| Process with inputs/outputs | Workflow diagram | fletcher |
| Comparison of 2+ approaches | Comparison table | Typst native table |
| Hierarchy or taxonomy | Mind map or tree | `/mindmap` or fletcher |
| Data trends or distributions | Chart | cetz-plot or matplotlib |
| Cause-effect relationships | Flowchart | fletcher |
| Before/after or evolution | Timeline | timeliney or fletcher |
| System architecture or layers | Block diagram | fletcher or Typst boxes |
| Concept with analogy | Illustration | `/nano-banana` |

### Content Structure

- Suggest TOC (`#outline()`) at 4+ sections
- Suggest file split at 40+ pages — see `references/common-patterns.md` "Large Documents"
- Convert prose lists to tables when 3+ items with attributes

### Component Library Auto-use

When writing content, automatically convert matching patterns to `@local/qk:1.0.0` components:

| Content pattern | Use instead |
|-----------------|-------------|
| Warning paragraph | `warning[...]` |
| Key point / takeaway | `keypoint[...]` |
| Tip or best practice | `tip[...]` |
| Common mistake / trap | `trap[...]` |
| Step-by-step procedure | `step-box("Title", [...])` |
| KPI or metric highlight | `stat-card("value", "label")` |

### Cross-referencing

Add `<label>` + `@ref` for recurring concepts across sections.

### Accessibility (Typst 0.14+)

- `alt:` on all figures — `image("path.png", alt: "description")`
- Semantic heading hierarchy — don't skip levels
- `table.header()` for repeating headers — improves PDF/UA accessibility

## Fallback Chains

| If this fails... | Try... |
|------------------|--------|
| `/nano-banana` | Placeholder rect with description text |
| `/image-search` | `/nano-banana` with descriptive prompt |
| `/mindmap` | `fletcher` tree diagram |
| matplotlib | Check `.venv` → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` | Isolate with `/* ... */`, compile incrementally |

## Reference File Index

| When you need... | Read... |
|------------------|---------|
| Syntax, errors, special chars | `references/quick-ref.md` |
| `@local/qk:1.0.0` API | `references/component-library.md` |
| Visual tool details, examples, fallbacks | `references/tool-routing.md` |
| Document preambles | `references/templates.md` |
| Table patterns, show rules, large docs | `references/common-patterns.md` |
| Page layout, spacing, figures, curves | `references/layout-patterns.md` |
| Math mode traps | `references/math-pitfalls.md` |
| Package imports | `references/packages.md` |
| `sym.*` symbols | `references/symbols.md` |

## Version Notes (0.13–0.14)

| Feature | Ver | Description |
|---------|-----|-------------|
| Tagged PDFs, PDF/UA-1 | 0.14 | Accessible PDFs by default |
| `figure.alt` / `image(alt:)` | 0.14 | Alt text for screen readers |
| `pdf.attach` | 0.14 | Attach files (replaces `pdf.embed`) |
| PDF as image format | 0.14 | `image("file.pdf")` |
| Multiple table headers | 0.14 | Hierarchical headers repeat across pages |
| `curve` function | 0.13 | Bezier drawing (replaces `path`) |

**Deprecated**: `path` → `curve` · `pdf.embed` → `pdf.attach` · `image.decode` → pass bytes directly · polylux:0.3.1 → `polylux:0.4.0` or `touying`

## CLI Commands

```bash
typst compile document.typ                     # Compile to PDF
typst compile document.typ --root ..           # Set project root
typst compile document.typ out.pdf --pages 1-5 # Specific pages
typst watch document.typ                       # Watch and recompile
typst fonts                                    # List available fonts
typst query doc.typ "heading.where(level: 1)"  # Query document structure
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

**Variable font warning:** Apple system fonts (New York, SF Pro) are variable → "variable fonts are not currently supported." Install static `.otf`/`.ttf` versions or use alternatives.

**CJK fallback:** `#set text(font: ("New Computer Modern", "Songti SC"))`

## Documentation

- [Official Reference](https://typst.app/docs/reference/)
- [Package Registry](https://typst.app/universe/)
- [Tutorial](https://typst.app/docs/tutorial/)
- [Changelog](https://typst.app/docs/changelog/)
