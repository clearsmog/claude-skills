# Popular Packages

Install from https://typst.app/universe/ — check for latest versions.

## Drawing & Diagrams

| Package | Purpose | Import |
|---------|---------|--------|
| **cetz** | Core drawing (TikZ-inspired) + cetz-plot for charts | `#import "@preview/cetz:0.4.2"` |
| **fletcher** | Flowcharts, automata, arrows | `#import "@preview/fletcher:0.5.8"` |
| **lilaq** | Data visualization, plots | `#import "@preview/lilaq:0.5.0"` |
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
| **touying** | Presentations (Typst 0.14+) | `#import "@preview/touying:0.6.1"` |
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

cetz-plot is bundled with cetz. Use for distribution plots, simple line/area charts, and font-matching resolution-independent output. See `references/tool-routing.md` for detailed examples.
