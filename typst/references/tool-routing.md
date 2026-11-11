# Visual Tool Routing

This file is the full routing reference for visuals in Typst documents. The summaries in the typst skill's `SKILL.md` and in `rules/typst.md` are short versions of it; when they and this file differ, this file is right.

## When to Add a Visual

When creating or substantially editing a `.typ` document, add a visual wherever it makes the content clearer, without waiting to be asked.

Do not add one when:

- the edit is small (fewer than about 15 lines changed);
- the document already has a suitable visual for that content;
- the user asked for text only or no images.

If the user names a tool, use it even where the tables below say otherwise. The tables are defaults.

## Routing by Content Type

### Diagrams

| Content | Tool |
|---------|------|
| Small flowcharts, decision trees, ER, state diagrams (up to about 10 nodes, one actor, no forced crossings) | **fletcher** |
| Larger flows, multi-party lifecycles / sequence / swimlane, causal or event networks, state machines with many edges, layered maps | **`diagram` skill** (D2 to SVG) |
| Small sequence diagram that should match the body font | **chronos** |
| Gantt charts, project schedules | **timeliney** |
| Linear timelines, historical events | **herodot** (timeliney if the events have durations) |

Never draw a diagram with Mermaid, Python (graphviz, matplotlib) or any raster tool: the output has mismatched fonts and no source that can be edited beside the document.

fletcher is the default for small diagrams because it sets text in the document font. Past about 10 nodes, with several parties or with crossing edges, hand-placed fletcher coordinates collide, so use the `diagram` skill: D2 lays the diagram out itself, emits vector SVG, and the `.d2` source is kept beside the `.typ`. The cost is that the SVG carries its own font, not the body font. Embed it with `#figure(image("fig.light.svg", width: 100%), caption: [...])`.

### Charts

lilaq is the default: it is native Typst, uses the document font and needs no Python.

| Content | Tool | Notes |
|---------|------|-------|
| Line, bar, scatter, box, violin, heatmap, contour, subplots, dual axes, color bars | **lilaq** | `#import "@preview/lilaq:0.6.0" as lq`, then `#show: qk-lilaq-theme()` and `lq.diagram(...)`; example in `packages.md` |
| A very simple chart where lilaq is more than needed (rare; when unsure, use lilaq) | **cetz-plot** | Native Typst; qk helpers below |
| kde and pair plots | **matplotlib + seaborn** | `use()` from `qk_style`, save SVG |
| Faceted or grammar-of-graphics plots | **plotnine** | `theme_qk() + scale_color_qk()`, save SVG |
| Data that an existing Python pipeline already produces | **matplotlib** | `use()` from `qk_style`, save SVG |

Python is only for the last three rows. Embed its output with `#figure(image("chart.svg", width: 100%), caption: [...])`.

### Layout

| Content | Tool |
|---------|------|
| Tables, grids, comparison layouts | **Typst native** |
| Callout boxes, styled layouts | **Typst native** (`rect`, `block`) |

### Images and Illustrations

| Content | Tool |
|---------|------|
| Mind maps, concept maps, topic trees | **`/mindmap`** |
| Company or brand logos | **`/image-search --logo`** |
| Real-world photos | **`/image-search`** |
| Conceptual illustrations, metaphors, cover art | No image generator is available. Use a diagram where one fits; if the `anatomy` skill is installed, suggest an isometric figure and wait for a yes (one takes up to an hour); otherwise leave a placeholder `#rect` and tell the user |
| The document's central mechanism, where precise parts and true numbers matter | **`/anatomy`**, then `scripts/anatomy-to-typst.mjs` (below). At most one or two per document, and only after the user agrees |

## Content Patterns

Patterns in the text that call for a visual, and what to add:

| Content pattern | Visual | Tool |
|-----------------|--------|------|
| Comparison grids, attribute tables | Styled table | Typst native |
| Callout boxes, styled layouts | `rect()` / `block()` | Typst native |
| Sequential steps, decision logic | Flowchart or decision tree | fletcher |
| Process with inputs and outputs | Workflow diagram | fletcher |
| System architecture, ER diagrams | Block or entity diagram | fletcher |
| Hierarchy or taxonomy | Tree diagram | fletcher or `/mindmap` |
| Topic overview, concept map | Mind map | `/mindmap` |
| Request-response, API flows | Sequence diagram | chronos |
| Project schedule, phases | Gantt chart | timeliney |
| Historical events, evolution | Timeline | herodot or timeliney |
| Numeric series, distributions, comparisons across groups | Chart | Charts table above |
| Company logo, brand mark | Logo image | `/image-search --logo` |
| Real-world subject | Photo | `/image-search` |
| Concept explained by analogy or metaphor | Illustration | Images table above (no generator) |

The fletcher and chronos rows hold only within the size limits in the Diagrams table; past them the tool is the `diagram` skill.

## Anatomy Figures (isometric machines)

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
not for routine visuals.

## qk Plot Style

The chart styling that matches the qk palette lives in `~/Developer/Typst-PDF/MatplotlibStyle/`. It is not part of the `@local/qk` package, so neither side is available in a project until you do one of the steps below.

### Typst side: `qk-plot.typ`

`qk-plot.typ` defines `qk-lilaq-theme`, `qk-cycle`, `qk-marks` and the cetz-plot helpers. Copy it next to the `.typ` file that imports it:

```sh
cp ~/Developer/Typst-PDF/MatplotlibStyle/qk-plot.typ "<directory of the .typ file>/"
```

```typst
#import "@preview/lilaq:0.6.0" as lq
#import "qk-plot.typ": *
#show: qk-lilaq-theme()                  // colorblind palette: qk-lilaq-theme(colorblind: true)
```

The import path is relative to the importing file, so a document in another directory needs its own relative path (or `/qk-plot.typ` with `--root`). The copy does not follow later changes to the source; copy it again after the source changes. Without the file, lilaq and cetz-plot still work with their own default styling.

cetz-plot with the qk helpers: `set-style(content: qk-cetz-content)` in the canvas, `x-format` and `y-format: qk-tick-format` (plain-text ticks, not the math font), `plot-style: qk-plot-style`, `mark-style: qk-plot-style`, and `mark: qk-marks.at(i)` per series. Colors come from `qk-cycle`.

### Python side: `qk_style` and `qk_plotnine`

`qk_style.py` and `qk_plotnine.py` are plain modules in the same directory, not an installed package, so `from qk_style import use` fails in a project venv unless that directory is on the path:

```sh
PYTHONPATH="$HOME/Developer/Typst-PDF/MatplotlibStyle" uv run --with matplotlib --with seaborn --with plotnine python fig_returns.py
```

Drop the `--with` flags when the project venv already has those packages. `uv run --with-editable ~/Developer/Typst-PDF/MatplotlibStyle` does not work: the directory has several top-level modules and no package layout, so the build fails.

`plt.style.use("qk")` works in any environment that has matplotlib, because `qk.mplstyle` is also installed in `~/.matplotlib/stylelib/`. It applies the rcParams only (no `use("talk")` contexts, colormaps or seaborn helpers), and that installed copy is separate from the source file.

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

## Python Charts (the exceptions to lilaq)

Use matplotlib, seaborn or plotnine only for the cases in the Charts table. Save SVG and embed it. The qk style keeps `svg.fonttype: path`, so the text becomes outlines and renders in Typst whether or not the font is installed. See "qk plot style" above for how the `qk_style` import resolves.

```python
# matplotlib
from qk_style import use
use()  # or use("talk") for slides; plt.style.use("qk") also works, without the helpers
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

## Auto-invoke Rules

- **`/mindmap`**: invoke for mind maps, concept maps and topic trees. Pass `--typst`. Default theme: `academic` (blue/orange, matching study materials). `--theme latte` for pastel, `--theme dark` for dark backgrounds.
- **`/image-search`**: invoke for logos, real-world photos and web graphics. Pass `--typst`.

Examples:
```
/mindmap "Portfolio Theory" --typst --caption "Portfolio Theory Overview"
/image-search --logo "Goldman Sachs" --typst --width 40%
/image-search "electric vehicle charging station" --typst --size large
```

## Fallback Chains

| If this fails... | Try instead... |
|------------------|----------------|
| `/image-search` | Placeholder `#rect(width: 100%, height: 4cm, fill: luma(240))[Image placeholder]` |
| `/mindmap` | `fletcher` tree diagram |
| plotnine | matplotlib (same chart, different API) |
| matplotlib | Check `.venv` exists; if not, `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` error | Isolate with `/* ... */`, compile incrementally |
