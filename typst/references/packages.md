# Popular Packages

Install from https://typst.app/universe/ — check for latest versions.

## Drawing & Diagrams

| Package | Purpose | Import |
|---------|---------|--------|
| **cetz** | Core drawing (TikZ-inspired). Use `qk-plot.typ` for consistent qk palette colors. | `#import "@preview/cetz:0.5.2"` |
| **cetz-plot** | Charts on top of cetz (separate package, pair with cetz 0.5.x). | `#import "@preview/cetz-plot:0.1.4"` |
| **fletcher** | Flowcharts, automata, arrows | `#import "@preview/fletcher:0.5.8"` |
| **lilaq** | Native Typst data visualization — line, scatter, bar, box, violin, heatmap, contour, subplots, dual axes, color bars, themes, datetime. Import `as lq`. | `#import "@preview/lilaq:0.6.0" as lq` |
| **chronos** | Sequence diagrams (Feb 2026, requires Typst 0.14.2) | `#import "@preview/chronos:0.3.0"` |

## Scientific & Units

| Package | Purpose | Import |
|---------|---------|--------|
| **physica** | Math constructs for physics/engineering | `#import "@preview/physica:0.9.8"` |
| **unify** | SI units, monetary, binary formatting | `#import "@preview/unify:0.8.1"` |

## Code & Text

| Package | Purpose | Import |
|---------|---------|--------|
| **codly** | Code blocks with line numbers | `#import "@preview/codly:1.3.0"` |
| **zebraw** | Code listings with annotations | `#import "@preview/zebraw:0.6.3"` |
| **lovelace** | Pseudocode / algorithms (supports `title-inset` parameter) | `#import "@preview/lovelace:0.3.1"` |
| **gentle-clues** | Callouts, tips, admonitions | `#import "@preview/gentle-clues:1.3.1"` |

## Presentations & Layout

| Package | Purpose | Import |
|---------|---------|--------|
| **touying** | Presentations. **Use 0.6.x/0.7.x API** (`#show: theme.with(...)`), NOT the old 0.3.x `register()` pattern. See `references/touying-guide.md`. | `#import "@preview/touying:0.7.4"` |
| **tablem** | Markdown-like table syntax | `#import "@preview/tablem:0.3.0"` |
| **showybox** | Customizable text boxes | `#import "@preview/showybox:2.0.4"` |

## Timelines & Utility

| Package | Purpose | Import |
|---------|---------|--------|
| **timeliney** | Gantt charts (native Typst) | `#import "@preview/timeliney:0.4.0"` |
| **herodot** | Linear timelines (v1.0: `spanheight` moved to `eventspan()`, new params: `event-rotation`, `span-rotation`, `event-display`, `month-locale`, `event.offset`) | `#import "@preview/herodot:1.0.0"` |
| **glossarium** | Glossary/terminology management | `#import "@preview/glossarium:0.5.10"` |
| **cmarker** | Render Markdown inside Typst docs (supports math via mitex, tables, footnotes, HTML handling, inline SVG, frontmatter parsing; `heading-label-case` renamed to `heading-labels` with values `"github"`/`"jupyter"`; new `render-with-metadata()`; requires Typst 0.15.0+ as of 0.1.9) | `#import "@preview/cmarker:0.1.9"` |

Note: polylux:0.3.1 is incompatible with 0.14; use `polylux:0.4.0` or `touying` (more active).

## Usage Examples

### gentle-clues (callouts)

```typst
#import "@preview/gentle-clues:1.3.1": tip, warning, example, abstract

#tip[Use shrinkage estimators when T < N.]

#warning[The path function was removed in Typst 0.15. Use curve instead.]

#example[
  A 60/40 portfolio with monthly rebalancing achieved a Sharpe ratio of 0.8
  over 2010-2020.
]
```

### lovelace (pseudocode)

```typst
#import "@preview/lovelace:0.3.1": pseudocode-list

#pseudocode-list[
  + *Input:* views vector $q$, uncertainty $tau$
  + Compute equilibrium returns: $Pi = delta Sigma w_"mkt"$
  + Blend views with prior:
    + $M = (tau Sigma)^(-1) + P^top Omega^(-1) P$
    + $mu = M^(-1)((tau Sigma)^(-1) Pi + P^top Omega^(-1) q)$
  + *Output:* posterior expected returns $mu$
]
```

### zebraw (annotated code blocks)

```typst
#import "@preview/zebraw:0.6.3": *
#show: zebraw.with(
  background-color: luma(250),
  highlight-color: rgb("#e3f2fd"),
)
```

After setup, fenced code blocks automatically get zebra striping and support line highlighting with `// @hl` comments.

### cetz-plot (charts)

cetz-plot is a separate package (`@preview/cetz-plot:0.1.4`, pair with `cetz:0.5.2`). Use for simple charts (< 3 series, < 20 data points). Use `qk-plot.typ` from `~/Developer/Typst-PDF/MatplotlibStyle/` for consistent qk palette colors (its `qk-plot-style`/`qk-bar-style` helpers are version-agnostic style dicts). See `references/tool-routing.md` for the chart decision tree.

### lilaq (native Typst charts)

lilaq (0.6.0) is a native Typst data visualization package supporting line, scatter, bar, box, violin, heatmap, contour, and quiver plots with subplots via `lq.diagram` grids, dual axes, color bars, themes, and datetime support. See tool-routing.md for the chart decision tree.

```typst
#import "@preview/lilaq:0.6.0" as lq

// Multi-series line chart
#figure(
  lq.diagram(
    width: 10cm, height: 6cm,
    xlabel: [Year], ylabel: [Return (%)],
    lq.plot((2020, 2021, 2022, 2023), (8.2, 12.1, -5.3, 15.7), label: [Fund A]),
    lq.plot((2020, 2021, 2022, 2023), (6.1, 9.8, -2.1, 11.3), label: [Fund B]),
    lq.plot((2020, 2021, 2022, 2023), (4.5, 7.2, -8.9, 18.2), label: [Fund C]),
  ),
  caption: [Three-fund performance comparison],
)
```

```typst
// Bar chart with labels
#import "@preview/lilaq:0.6.0" as lq

#figure(
  lq.diagram(
    width: 10cm, height: 5cm,
    xlabel: [Category], ylabel: [Allocation (%)],
    lq.bar((0, 1, 2, 3), (40, 25, 20, 15), width: 0.6),
    xaxis: (subticks: none),  // custom tick labels via lq.tick-label ([Equities], [Bonds], [Real Estate], [Alternatives]),
  ),
  caption: [Portfolio allocation],
)
```

See `references/tool-routing.md` for full routing guidance on when to use lilaq vs cetz-plot vs matplotlib.
