---
paths:
  - "**/*.typ"
---
# Typst

## Diagrams
- Use native Typst packages (fletcher, chronos, timeliney) instead of Mermaid.
- NEVER use Python (graphviz, mermaid, matplotlib) for flowcharts — always fletcher.

## Charts
- Simple charts (< 3 series, < 20 data points, no computation): **cetz-plot** with `qk-cycle` colors from `qk-plot.typ`
- Statistical/complex charts: **matplotlib** with `plt.style.use('qk')` or **plotnine** with `theme_qk()` — generate SVG, embed with `#figure(image(...))`
- Lilaq: emerging alternative, usable for basic multi-series charts but less mature than the above

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

When creating or substantially editing `.typ` documents, auto-detect content that benefits from visuals. Do NOT wait for the user to request images — invoke tools directly.

**Priority:** Diagrams → native Typst (fletcher/chronos/timeliney/herodot, NEVER Python); Charts → cetz-plot (simple) / matplotlib or plotnine (complex) — generate SVG, embed with `#figure(image(...))`; Images → /image-search / /mindmap / `gemini-generate-image` MCP

**Auto-invoke triggers (no user prompt needed):**
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
- Local package: `#import "@local/qk:2.1.0": *`
- Source: ~/Library/Application Support/typst/packages/local/qk/2.1.0/
- Components: callouts (15 variants, 5 styles), cards, tables, academic boxes, layout, presets
- When creating Typst documents for the user, prefer qk components over raw Typst blocks
- Presets: qk-doc (study guides), qk-report (corporate), qk-minimal (notes), qk-magazine (editorial), qk-exam (exams)
- Colors: Tailwind scales (`blue.at("600")`) or semantic aliases (`colors.navy`)
- Theming: `#show: qk-theme.with(palette: "dark")` — palettes: default, dark, print, high-contrast, sepia
- `theme-get()` must be called inside `context { ... }`

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
