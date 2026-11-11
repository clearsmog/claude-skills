# Visual Tool Routing

## Content-Type Routing

When a Typst document needs a visual, identify what you're visualizing, then pick the tool:

### Diagrams

| Content | Tool |
|---------|------|
| Small flowcharts, decision trees, ER, state diagrams (≤10 nodes, one actor, no forced crossings) | **fletcher** |
| Larger flows, multi-party lifecycles / sequence / swimlane, causal or event networks, busy state machines, layered maps | **`diagram` skill** (D2 → SVG) |
| Simple sequence diagram that must match body font | **chronos** |
| Gantt charts, project schedules | **timeliney** |
| Linear timelines, historical events | **herodot** |

> **Hard rule: no Python or raster diagram tools.** Never use graphviz-from-Python, mermaid or matplotlib for diagrams: they give raster output, mismatched fonts and no editable source. fletcher stays the default for small diagrams because it matches the document font. Past about 10 nodes, with several parties or with crossing edges, hand-placed fletcher coordinates collide, so use the `diagram` skill: it auto-lays out with D2, emits vector SVG, and keeps the `.d2` source beside the `.typ` for version control. The one cost is that the SVG uses its own embedded font, not the body font. Embed with `#figure(image("fig.light.svg", width: 100%), caption: [...])`.

### Charts

| Content | Tool | Notes |
|---------|------|-------|
| Extremely simple chart where lilaq is overkill (rare) | **cetz-plot** | Typst-native, font-matched, use `qk-cycle` colors from `qk-plot.typ` |
| Most charts (line, bar, scatter, box, violin, heatmap, contour, subplots) | **lilaq** | Typst native, font-matched, `as lq` |
| Statistical plots (kde, pair plots) | **matplotlib + seaborn** | `use()` from qk_style, SVG output |
| Grammar-of-graphics / faceted plots | **plotnine** | `theme_qk() + scale_color_qk()`, SVG output |
| Complex charts with Python data pipeline | **matplotlib** | Full API control, SVG output |

### Layout

| Content | Tool |
|---------|------|
| Tables, grids, comparison layouts | **Typst native** |
| Callout boxes, styled layouts | **Typst native** (`rect`, `block`) |

### Images & Illustrations

| Content | Tool |
|---------|------|
| Mind maps, concept maps, topic trees | **`/mindmap`** |
| Company/brand logos | **`/image-search --logo`** |
| Real-world photos | **`/image-search`** |
| Conceptual illustrations, metaphors, cover art | No image generator is wired up. Use a diagram where one fits; if the `anatomy` skill is installed, suggest an isometric figure and wait for a yes (one takes up to an hour); otherwise leave a placeholder `#rect` and tell the user |

### Anatomy figures (isometric machines)

`/anatomy` builds an HTML page; Typst cannot read its SVG directly (it is styled with CSS custom
properties, which Typst ignores, so every shape renders black). Freeze it first:

```sh
node <figure>/build.mjs --light                       # print is light
node ~/.claude/skills/typst/scripts/anatomy-to-typst.mjs <figure>/<name>-light.html images/<name>.svg
# a pose other than rest: --actions pose.json  (drive.mjs actions, e.g. [["key"," "],["wait",2500]])
```

```typst
#figure(image("images/<name>.svg", width: 100%), caption: [...])
```

The script bakes computed paints into SVG attributes, turns CSS `blur()` halos into SVG filters and
stacks the back/front layers. WebGL layers (plume, water, glow) and the card text are not captured:
put the title and readout in the Typst caption. Use it for the one figure that carries the argument,
not for routine visuals (a Figure takes up to an hour).

## Quick Reference

```
What are you visualizing?

LAYOUT       →  Typst native (tables, grids, boxes)
DIAGRAMS     →  fletcher (≤10 nodes) | diagram skill (bigger, multi-party, networks)
               | chronos | timeliney | herodot
               NEVER Python or raster
CHARTS       →  See decision tree below
MIND MAPS    →  /mindmap
IMAGES       →  /image-search (photos/logos) | no AI illustration generator

Chart decision tree:
  Default → lilaq (line, bar, scatter, box, violin, heatmap, contour, subplots, dual axes; font-matched, no Python dependency)
  Exceptions:
      Extremely simple, lilaq overkill (rare)?
        YES → cetz-plot
      Statistical (kde, pair plots)?
        YES → matplotlib + seaborn (use(), SVG)
      Faceted / grammar?
        YES → plotnine (theme_qk(), SVG)
      Data already produced by a Python pipeline, or a chart lilaq can't express?
        YES → matplotlib (plt.style.use('qk'), SVG)
```

## Native Typst Diagram Packages

### fletcher (flowcharts, trees, ER, state diagrams)

**Simple linear flow:**

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#figure(
  diagram(
    node((0, 0), [Start], stroke: 0.5pt, shape: fletcher.shapes.pill),
    edge("-|>"),
    node((1, 0), [Process], stroke: 0.5pt),
    edge("-|>"),
    node((2, 0), [End], stroke: 0.5pt, shape: fletcher.shapes.pill),
  ),
  caption: [Simple flowchart],
)
```

**Decision tree with diamond nodes and Yes/No labels:**

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#figure(
  diagram(
    spacing: (10mm, 12mm),
    node((0, 0), [Start], stroke: 0.5pt, shape: fletcher.shapes.pill),
    edge("-|>"),
    node((1, 0), align(center)[Is the data \ stationary?],
      stroke: 0.5pt, shape: fletcher.shapes.diamond),
    edge("r,d", "-|>", [Yes]),
    node((2, 1), align(center)[Fit ARMA \ model], stroke: 0.5pt),
    edge((1, 0), "l,d", "-|>", [No]),
    node((0, 1), align(center)[Apply \ differencing], stroke: 0.5pt),
    edge("-|>"),
    edge((0, 1), (1, 0), "-|>", bend: -30deg),
  ),
  caption: [Stationarity check decision tree],
)
```

**Text-heavy nodes with width for wrapping:**

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#figure(
  diagram(
    spacing: (15mm, 10mm),
    node-stroke: 0.5pt,
    node((0, 0), width: 28mm,
      align(center)[*Step 1* \ Collect raw data from multiple sources and validate formats]),
    edge("-|>"),
    node((1, 0), width: 28mm,
      align(center)[*Step 2* \ Clean outliers, handle missing values, normalize scales]),
    edge("-|>"),
    node((2, 0), width: 28mm,
      align(center)[*Step 3* \ Run regression analysis and compute confidence intervals]),
  ),
  caption: [Data pipeline with detailed steps],
)
```

**Complex branching (ER-style):**

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#figure(
  diagram(
    spacing: (12mm, 10mm),
    node-stroke: 0.5pt,
    node((0, 0), [*Portfolio*], fill: rgb("#e3f2fd")),
    node((1, -1), [*Asset*], fill: rgb("#e8f5e9")),
    node((1, 1), [*Benchmark*], fill: rgb("#fff3e0")),
    node((2, -1), [*Price History*], fill: rgb("#e8f5e9")),
    edge((0, 0), (1, -1), "-|>", [contains]),
    edge((0, 0), (1, 1), "-|>", [tracks]),
    edge((1, -1), (2, -1), "-|>", [has]),
  ),
  caption: [Portfolio entity relationships],
)
```

**Key fletcher patterns:**
- `width: 28mm` on nodes to wrap long text
- `align(center)[...]` for centered multi-line content
- `\` for line breaks within node content
- `shape: fletcher.shapes.diamond` for decision nodes
- `shape: fletcher.shapes.pill` for start/end terminals
- `edge("r,d", ...)` for routing edges via compass directions
- `fill:` on nodes for color-coding
- `bend: 30deg` for curved feedback edges

### chronos (sequence diagrams)

```typst
#import "@preview/chronos:0.3.0"
#figure(
  chronos.diagram({
    import chronos: *
    _par("Client")
    _par("Server")
    _seq("Client", "Server", comment: "Request")
    _seq("Server", "Client", comment: "Response", dashed: true)
  }),
  caption: [Client-server interaction],
)
```

### timeliney (Gantt charts)

```typst
#import "@preview/timeliney:0.4.0"
#figure(
  timeliney.timeline(
    show-grid: true,
    {
      import timeliney: *
      headerline(group(([Q1], 3)), group(([Q2], 3)))
      taskgroup(title: [Phase 1], {
        task("Research", (0, 2), style: (stroke: 2pt + blue))
        task("Design", (1, 4), style: (stroke: 2pt + green))
      })
    },
  ),
  caption: [Project timeline],
)
```

### matplotlib / plotnine (exceptions to lilaq)

Use matplotlib or plotnine only for kde/pair plots, faceted grammar-of-graphics plots, data from an existing Python pipeline, or charts lilaq can't express. Generate SVG, then embed.

```python
# matplotlib
from qk_style import use
use()  # or use("talk") for slides
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot([2020, 2021, 2022, 2023, 2024], [8.2, 12.1, -5.3, 15.7, 9.4], label="Fund A")
ax.plot([2020, 2021, 2022, 2023, 2024], [6.1, 9.8, -2.1, 11.3, 7.6], label="Fund B")
ax.set_xlabel("Year")
ax.set_ylabel("Return (%)")
ax.legend()
fig.savefig("charts/performance.svg")
```

```python
# plotnine (grammar of graphics)
from qk_plotnine import theme_qk, scale_color_qk
from plotnine import ggplot, aes, geom_line, labs

p = (ggplot(df, aes("year", "return_pct", color="fund"))
     + geom_line() + theme_qk() + scale_color_qk()
     + labs(title="Fund Performance"))
p.save("charts/performance.svg", width=8, height=5)
```

```typst
#figure(
  image("charts/performance.svg", width: 90%),
  caption: [Fund performance comparison],
)
```

**Four-tier chart system:**
- **cetz-plot** (Typst native): Only extremely simple charts where lilaq is overkill (rare). Use `qk-cycle` colors.
- **lilaq** (Typst native, the default): Most charts — line, bar, scatter, box, violin, heatmap, contour, subplots, dual axes, color bars. Font-matched, no Python dependency.
- **plotnine**: Grammar-of-graphics style, faceted layouts, ggplot2 composition. `theme_qk() + scale_color_qk()`.
- **matplotlib**: Full API control, statistical plots (kde, pair) via seaborn, complex annotations. `use()` from qk_style.
- All Python tools output SVG with `svg.fonttype: path` for clean Typst embedding.

## Auto-invoke Rules

- **`/mindmap`**: Auto-invoke for mind maps, concept maps, topic trees. Pass `--typst`. Default theme: `academic` (blue/orange matching study materials). `--theme latte` for pastel, `--theme dark` for dark backgrounds.
- **`/image-search`**: Auto-invoke for logos, real-world photos, web graphics. Pass `--typst`.

Examples:
```
/mindmap "Portfolio Theory" --typst --caption "Portfolio Theory Overview"
/image-search --logo "Goldman Sachs" --width 40%
/image-search "electric vehicle charging station" --size large
```

## User Override

If the user explicitly requests a specific tool, use it even if the routing table suggests otherwise. The table is a default, not a constraint.

## Fallback Chains

| If this fails... | Try instead... |
|------------------|----------------|
| `/image-search` | Placeholder `#rect(width: 100%, height: 4cm, fill: luma(240))[Image placeholder]` |
| `/mindmap` | `fletcher` tree diagram |
| plotnine | matplotlib (same chart, different API) |
| matplotlib | Check `.venv` exists → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` error | Isolate with `/* ... */`, compile incrementally |
