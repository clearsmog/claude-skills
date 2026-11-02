---
paths:
  - "**/*.typ"
---
# Typst

## Diagrams
- Use native Typst packages (fletcher, chronos, timeliney) instead of Mermaid.
- Never draw diagrams with Python or raster tools (graphviz via Python, mermaid, matplotlib).
- Flowcharts with at most 10 nodes, one actor and no forced crossings: fletcher. Anything larger, multi-party (sequence, swimlane, lifecycle), causal/event networks or state machines with many edges: the `diagram` skill (D2 to SVG, `.d2` source kept beside the `.typ`, embedded with `image("fig.light.svg")`).

## Charts
- **Default choice**: Lilaq with `qk-lilaq-theme()` — handles line, bar, scatter, box, violin, heatmap, contour, subplots, dual axes natively in Typst
- **Fall back to Python SVG** only when: kde plots, pair plots, faceted grammar (plotnine), or Python data pipeline already exists
- **cetz-plot**: only for extremely simple charts where Lilaq would be overkill (rare — Lilaq is almost always better)
- Lilaq + qk style: `#import "qk-plot.typ": *` then `#show: qk-lilaq-theme()`. Colorblind variant: `qk-lilaq-theme(colorblind: true)`.
- cetz-plot + qk style: `set-style(content: qk-cetz-content)` in the canvas, `x-format`/`y-format: qk-tick-format` (Inter ticks instead of math font), `mark-style: qk-plot-style` + `mark: qk-marks.at(i)` per series
- SVG embedding: `#figure(image("chart.svg", width: 100%), caption: [...])`

## Compile After Editing
- After any `.typ` edit, run `typst compile <file>` to catch errors early.
- Check for text overflow in columns — Typst silently truncates overflowing content.
- PDF output lands in the same directory as the source file by default.

## Package Imports
- Standard pattern: `#import "@preview/package-name:version": *`
- Pin versions per `skills/typst/references/packages.md` (single source of truth) — `@latest` doesn't exist in Typst.

## Figure Paths
- Use paths relative to the `.typ` file location, not the working directory.
- Prefer `image("figures/name.png")` over absolute paths for portability.

## Visual Auto-detection

When creating or substantially editing `.typ` documents, add visuals where the content would clearly benefit, without waiting to be asked.

**Priority:** Diagrams → native Typst (fletcher/chronos/timeliney/herodot, NEVER Python); Charts → Lilaq (default) / Python SVG for kde, pair or faceted plots — embed with `#figure(image(...))`; Images → /image-search / /mindmap / `gemini-generate-image` MCP

**Triggers:**
- Company/brand logos → invoke `/image-search --logo "Name" --typst`
- Real photographs → invoke `/image-search "query" --typst`
- Conceptual illustrations, metaphors → call `gemini-generate-image` MCP, then copy to `images/` and write Typst `#figure(...)`
- Mind maps, concept maps → invoke `/mindmap "topic" --typst`

**When NOT to auto-invoke:**
- Quick edits (< 15 lines changed) — don't add visuals to minor fixes
- The document already has appropriate visuals for the content
- The user explicitly said no images or text-only

See `skills/typst/references/tool-routing.md` for the full routing table and fallback chains.

## qk Component Library
- Local package: `#import "@local/qk:2.2.0": *`
- Source: ~/Library/Application Support/typst/packages/local/qk/2.2.0/ — the `qk/` dir is a git repo (local only); commit after changing qk, and regression-compile dependent docs (70+ in ~/Documents) before committing
- Components: callouts (15 variants, 5 styles), cards, tables, academic boxes, layout, presets
- When creating Typst documents for the user, prefer qk components over raw Typst blocks
- Presets: qk-doc (study guides), qk-report (corporate), qk-minimal (notes), qk-magazine (editorial), qk-exam (exams)
- All five presets share the same core options, so swapping between them is safe: `title`, `header-text`, `footer-text`, `heading-numbering`, `margin`, `figure-placement`, `styled-lists`, `styled-captions`, `stata-theme`, `code-theme`, `palette`, `theme-tokens`
- Colors: Tailwind scales (`blue.at("600")`) or semantic aliases (`colors.navy`)
- Theming: pass `palette:` to the **preset** — `#show: qk-doc.with(title: "…", palette: "dark")`. Palettes: default, dark, print, high-contrast, sepia
- A standalone `#show: qk-theme.with(palette: ...)` written after a preset only reaches components, not page fill or heading colors — `set page(fill:)` needs the value before state resolves. Use `resolve-theme(palette:, tokens:)` for a color at `set`-time
- `theme-get()` must be called inside `context { ... }`
- `chart()` takes `path("f.png")`, image bytes, or content — not a plain string (a string inside a package resolves against the package dir)
- Code blocks: presets style language-tagged fences (```` ```python ````) with codly 2.0 by default (`code-theme: true`): frame, line numbers, language badge, dark-palette syntax colors. Stata and unlabelled fences (program output) are left alone. Standalone: `#show: qk-code.with(resolve-theme())`
- `styled-table(columns: n, ...)` wraps the first n cells in `table.header` automatically (repeats across page breaks); pass your own `table.header(...)` to override

## Display Pitfalls (Prevent Before They Happen)

### Image Width
- Default to `width: 100%` for full-width charts
- Images with height/width ratio > 0.6 MUST use width >= 95% — tall images at lower % become tiny
- Never use width < 80% for data charts — excessive whitespace around small charts

### Font Sizes for Print Readability
- Minimum body text in custom layouts: 8pt (7.5pt and below fails in print)
- Labels in diagrams/zones: match surrounding text size, minimum 8.5pt
- When overriding font sizes for space, never go below 7pt

### Content Overflow Prevention
- Typst SILENTLY truncates overflowing content — no warnings, no errors
- After compiling, always check that all text is visible, especially in:
  - Multi-column layouts with `grid(columns: ...)`
  - Constrained `block()` elements
  - Table cells with long content
- Prefer `table()` over `grid()` for data — tables handle overflow better

### Angle Brackets and Equals Signs
- `<` and `>` in content are parsed as LABEL REFERENCES — "unclosed label" errors
- `=` at start of content block is parsed as HEADING — renders as huge text
- Fix: escape (\<, \>), use fullwidth characters, or use words (below, above)
- Pre-compile check: `grep -n '[^\\]<\|[^\\]>' file.typ`

### Logo/Image Clipping at Margins
- Full-bleed layouts with `outset` cause edge clipping
- Wrap edge-adjacent images in `box(inset: (right: 4pt))` for breathing room
- Reduce oversized logos by 2pt height as additional clearance
