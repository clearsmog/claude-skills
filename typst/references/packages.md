# Popular Packages

Install from https://typst.app/universe/ — check for latest versions.

## Drawing & Diagrams

| Package | Purpose | Import |
|---------|---------|--------|
| **cetz** | Core drawing (TikZ-inspired) + cetz-plot for charts. Use `qk-plot.typ` for consistent qk palette colors. | `#import "@preview/cetz:0.4.2"` |
| **fletcher** | Flowcharts, automata, arrows | `#import "@preview/fletcher:0.5.8"` |
| **lilaq** | Data visualization (emerging alternative — usable for basic charts, less mature). Import `as lq`. | `#import "@preview/lilaq:0.5.0" as lq` |
| **chronos** | Sequence diagrams (Feb 2026, requires Typst 0.14.2) | `#import "@preview/chronos:0.3.0"` |

## Scientific & Units

| Package | Purpose | Import |
|---------|---------|--------|
| **physica** | Math constructs for physics/engineering | `#import "@preview/physica:0.9.8"` |
| **unify** | SI units, monetary, binary formatting | `#import "@preview/unify:0.7.1"` |

## Code & Text

| Package | Purpose | Import |
|---------|---------|--------|
| **codly** | Code blocks with line numbers | `#import "@preview/codly:1.3.0"` |
| **zebraw** | Code listings with annotations | `#import "@preview/zebraw:0.6.1"` |
| **lovelace** | Pseudocode / algorithms | `#import "@preview/lovelace:0.3.0"` |
| **gentle-clues** | Callouts, tips, admonitions | `#import "@preview/gentle-clues:1.3.0"` |

## Presentations & Layout

| Package | Purpose | Import |
|---------|---------|--------|
| **touying** | Presentations (Typst 0.14+). **Use 0.6.x API** (`#show: theme.with(...)`), NOT the old 0.3.x `register()` pattern. See `references/touying-guide.md`. | `#import "@preview/touying:0.6.1"` |
| **tablem** | Markdown-like table syntax | `#import "@preview/tablem:0.3.0"` |
| **showybox** | Customizable text boxes | `#import "@preview/showybox:2.0.4"` |

## Timelines & Utility

| Package | Purpose | Import |
|---------|---------|--------|
| **timeliney** | Gantt charts (native Typst) | `#import "@preview/timeliney:0.4.0"` |
| **herodot** | Linear timelines | `#import "@preview/herodot:0.1.0"` |
| **glossarium** | Glossary/terminology management | `#import "@preview/glossarium:0.5.10"` |
| **cmarker** | Render Markdown inside Typst docs | `#import "@preview/cmarker:0.1.0"` |

Note: polylux:0.3.1 is incompatible with 0.14; use `polylux:0.4.0` or `touying` (more active).

## Usage Examples

### gentle-clues (callouts)

```typst
#import "@preview/gentle-clues:1.3.0": tip, warning, example, abstract

#tip[Use shrinkage estimators when T < N.]

#warning[The path function is deprecated in Typst 0.13+. Use curve instead.]

#example[
  A 60/40 portfolio with monthly rebalancing achieved a Sharpe ratio of 0.8
  over 2010-2020.
]
```

### lovelace (pseudocode)

```typst
#import "@preview/lovelace:0.3.0": pseudocode-list

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
#import "@preview/zebraw:0.6.1": *
#show: zebraw.with(
  background-color: luma(250),
  highlight-color: rgb("#e3f2fd"),
)
```

After setup, fenced code blocks automatically get zebra striping and support line highlighting with `// @hl` comments.

### cetz-plot (charts)

cetz-plot is bundled with cetz. Use for simple charts (< 3 series, < 20 data points). Use `qk-plot.typ` from `~/Developer/Typst/MatplotlibStyle/` for consistent qk palette colors. See `references/tool-routing.md` for the chart decision tree.

### lilaq (complex charts)

lilaq is an emerging native Typst data visualization package. For complex charts, prefer matplotlib or plotnine (more mature). See tool-routing.md for the chart decision tree.

```typst
#import "@preview/lilaq:0.5.0" as lq

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
#import "@preview/lilaq:0.5.0" as lq

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
