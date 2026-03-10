---
paths:
  - "**/charts/**/*.py"
  - "**/*chart*.py"
  - "**/*plot*.py"
  - "**/*fig*.py"
  - "**/figures/**/*.py"
  - "**/generate_*.py"
---
# Matplotlib Chart Quality

## qk Style (MANDATORY for all plots)
- Always apply before plotting: `plt.style.use('qk')` or `from qk_style import use; use()`
- Style source: ~/Developer/Typst/MatplotlibStyle/ (v2.2.0, Tailwind CSS palette)
- Named colors: `from qk_style import QK_COLORS, CYCLE` — use `CYCLE[:n]` for explicit bar/histogram colors
- Save as SVG for Typst: `fig.savefig("name.svg")`
- Embed in Typst: `#image("name.svg", width: 100%)`
- Place plot scripts next to the .typ file, or in a `figures/` subdirectory

## Context Presets
- `use()` or `use("paper")` — 10.5pt base, 8×5 figsize (default, Typst docs)
- `use("talk")` — 14pt base, 12×7.5 figsize (slides, presentations)
- `use("poster")` — 18pt base, 16×10 figsize (A0/A1 posters)
- All sizes scale proportionally from the paper baseline

## Seaborn Convenience Functions
- `heatmap_kws(**overrides)` — returns dict: cmap="qk_diverging", linewidths, linecolor, annot_kws
- `violin_kws(**overrides)` — returns dict: inner="quart", linewidth=0.8, saturation=0.85
- `strip_kws(**overrides)` — returns dict: jitter=0.3, edgecolor="white", linewidth=0.5
- Usage: `sns.heatmap(data, **heatmap_kws())` or `sns.heatmap(data, **heatmap_kws(annot=True))`
- `qk_cmap()` — registers + returns "qk_diverging" colormap (blue-white-red). Auto-called by `use()`.

## plotnine (Grammar of Graphics)
- `from qk_plotnine import theme_qk, scale_color_qk, scale_fill_qk`
- Usage: `ggplot(df, aes(...)) + geom_point() + theme_qk() + scale_color_qk()`
- Produces SVG output with `svg.fonttype = "path"` (set automatically)
- Use plotnine when: faceted plots, layered grammar, ggplot2-style composition

## When to Use What (Charts)
- **cetz-plot** (Typst native): < 3 series, < 20 data points, no computation needed
- **plotnine**: faceted plots, layered grammar, ggplot2-style composition
- **matplotlib + seaborn**: statistical plots (violin, kde, pair, heatmap), complex charts
- **matplotlib raw**: full API control, 4+ series, heavy annotations, custom layouts

## SVG Font Rendering for Typst
- `qk.mplstyle` v2.2.0 sets `svg.fonttype: path` by default — text becomes vector paths
- Without this, Typst cannot render SVG text when fonts (e.g. Inter) are missing from its cache
- This is the #1 cause of broken chart text in Typst documents
- Trade-off: text becomes non-editable vectors, but renders identically everywhere

## Font Cache
- After installing new fonts, rebuild matplotlib cache: `matplotlib.font_manager._load_fontmanager(try_read_cache=False)`
- Inter font often "installed but not found" — always include fallback: `plt.rcParams["font.sans-serif"] = ["Inter", "Helvetica Neue", "DejaVu Sans"]`

## Minimum Font Sizes for Print
- Chart labels/annotations: minimum 8pt (7pt and below are unreadable in print)
- Axis tick labels: minimum 9pt
- Flowchart box text: minimum 8pt for body, 9pt for titles
- Use weight="medium" for body text in flow diagrams (default "regular" too thin)

## Text Contrast on Colored Patches
- Text color must be based on FILL color brightness, never edge color.
- Safe pattern for box/diamond helpers:
  ```python
  dark_fills = {DARK_BLUE, BLUE, GREEN, RED, ORANGE}
  text_color = "white" if fc in dark_fills else ec  # or "#1a1a1a"
  ```
- Never use `color=ec` for text sitting on a filled patch — ec can equal fc, making text invisible.
- Light fill variants (LIGHT_BLUE=#e3f2fd, LIGHT_GREEN=#e8f5e9, LIGHT_RED=#ffebee) need dark text, not white.

## Figure Margins and Clipping
- ALWAYS use `pad_inches >= 0.3` in savefig() — prevents edge clipping of labels/arrows
- For diagrams with `ax.axis("off")`: use `fig.subplots_adjust(left=0.02, right=0.98)` instead of tight_layout()
- `tight_layout()` + `bbox_inches="tight"` clips arrows and annotations near figure edges
- Expand axis limits 0.5 units beyond outermost elements to prevent label truncation
- After saving, verify no elements are clipped at figure edges

## Flowchart Layout
- Side branches (decision sub-flows) need their own vertical space — 2-3 y-units per branching level. Never squeeze into the main spine's y-range.
- Set axis limits with 0.5-unit margin beyond the outermost elements.

## Z-Ordering
- Box/diamond patches: `zorder=3`
- Text labels: `zorder=4`
- Arrows/connectors: default (~2) or explicit `zorder=2`
- This ensures text is always readable above patches and arrows.

## After Generating Charts
- Visually verify ALL text is readable in the output — especially boxes with colored fills.
- Check no elements are clipped at figure edges.
