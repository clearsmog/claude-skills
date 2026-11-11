---
paths:
  - "**/*.typ"
---
# Typst

## Visuals

When creating or substantially editing a `.typ` document, add visuals where the content clearly benefits, without waiting to be asked. Skip this for quick edits (fewer than 15 lines changed), when the document already has suitable visuals, or when the user asked for text only.

- **Diagrams**: flowcharts, trees, ER and state diagrams with at most about 10 nodes, one actor and no forced crossings: fletcher. Small sequence diagrams: chronos. Gantt: timeliney. Timelines: herodot. Anything larger, multi-party (sequence, swimlane, lifecycle), causal/event networks or state machines with many edges: the `diagram` skill (D2 to SVG, `.d2` source kept beside the `.typ`, embedded with `image("fig.light.svg")`). NEVER Mermaid, Python (graphviz, matplotlib) or raster tools for diagrams.
- **Charts**: Lilaq by default (line, bar, scatter, box, violin, heatmap, contour, subplots, dual axes, all native Typst). cetz-plot only for a very simple chart where Lilaq is more than needed (rare). Python SVG only for kde plots, pair plots, faceted grammar (plotnine), or when a Python data pipeline already exists. For a chart in a Typst document the qk style below (Lilaq with `qk-lilaq-theme`, `qk_style` on the Python side) overrides the `dataviz` skill's palette and fonts; use `dataviz` only for its advice on chart form, labelling and accessibility.
- **Photos and logos**: invoke `/image-search "query" --typst` (add `--logo` for a company or brand mark).
- **Mind maps, concept maps**: invoke `/mindmap "topic" --typst`.
- **Conceptual illustrations, metaphors**: no image generator is available. Use a diagram where one fits; if the `anatomy` skill is installed, suggest an isometric figure and wait for a yes (one takes up to an hour); otherwise leave a placeholder `#rect` and tell the user.
- Embed any SVG with `#figure(image("chart.svg", width: 100%), caption: [...])`.
- qk chart style: `#import "qk-plot.typ": *` then `#show: qk-lilaq-theme()` (colorblind: `qk-lilaq-theme(colorblind: true)`); for cetz-plot, `set-style(content: qk-cetz-content)`, `x-format`/`y-format: qk-tick-format`, `mark-style: qk-plot-style`, `mark: qk-marks.at(i)`. `qk-plot.typ` is not in the `@local/qk` package and has to be copied into the project first.

The detailed source is the typst skill's `references/tool-routing.md` (`skills/typst/references/tool-routing.md`): full tables, content patterns, examples, fallbacks, and how to get `qk-plot.typ` and `qk_style`. Read it before adding a visual when the skill is installed.

## Compile After Editing
- After any `.typ` edit the file must compile. Where the auto-compile hook is installed (`~/.claude/hooks/auto-compile-typst.sh`, PostToolUse on Edit/Write) it does this and reports a failure back to you, finding `--root` from a `typst.toml` above the file or the git top level; then compile by hand only for what it skips: partials (`_*.typ`, `*.body.typ`), files changed through Bash, or a project with its own flags. Without the hook, run `typst compile <file>` yourself.
- Check for text overflow in columns — Typst silently truncates overflowing content.
- PDF output lands in the same directory as the source file by default.

## Package Imports
- Standard pattern: `#import "@preview/package-name:version": *`
- Pin versions per `skills/typst/references/packages.md` (single source of truth) — `@latest` doesn't exist in Typst.

## Figure Paths
- Use paths relative to the `.typ` file location, not the working directory.
- Prefer `image("figures/name.png")` over absolute paths for portability.

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
