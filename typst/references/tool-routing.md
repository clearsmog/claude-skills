# Visual Tool Routing

## Content-Type Routing

When a Typst document needs a visual, identify what you're visualizing, then pick the tool:

### Diagrams (always native Typst)

| Content | Tool |
|---------|------|
| Flowcharts, decision trees, ER, state diagrams | **fletcher** |
| Sequence diagrams (lifelines, messages) | **chronos** |
| Gantt charts, project schedules | **timeliney** |
| Linear timelines, historical events | **herodot** |

> **Hard rule — no Python for diagrams.** NEVER use graphviz, mermaid, matplotlib, or any Python tool for flowcharts, trees, ER diagrams, or state machines. Always use fletcher. Python diagram tools produce raster images that don't match document fonts, can't be edited in source, and break version control.

### Charts

| Content | Tool | Notes |
|---------|------|-------|
| Simple chart (< 3 series, < 20 pts) | **cetz-plot** | Typst-native, font-matched, use `qk-cycle` colors from `qk-plot.typ` |
| Statistical plots (violin, kde, pair, heatmap) | **matplotlib + seaborn** | `use()` from qk_style, SVG output |
| Grammar-of-graphics / faceted plots | **plotnine** | `theme_qk() + scale_color_qk()`, SVG output |
| Complex charts (4+ series, annotations) | **matplotlib** | Full API control, SVG output |

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
| Conceptual illustrations, metaphors, cover art | **`gemini-generate-image` MCP** |
| Refine/iterate on generated image | **`gemini-start-image-edit` MCP** |
| Verify image content | **`gemini-analyze-image` MCP** |

## Quick Reference

```
What are you visualizing?

LAYOUT       →  Typst native (tables, grids, boxes)
DIAGRAMS     →  fletcher | chronos | timeliney | herodot
               NEVER Python — always native Typst
CHARTS       →  See decision tree below
MIND MAPS    →  /mindmap
IMAGES       →  /image-search (photos/logos) | gemini-generate-image (illustrations)

Chart decision tree:
  < 3 series, < 20 data points, no computation?
    YES → cetz-plot (Typst native, font-matched, qk-cycle colors)
    NO  →
      Statistical plot (violin, kde, pair, heatmap)?
        YES → matplotlib + seaborn (use(), SVG)
      Faceted / layered grammar?
        YES → plotnine (theme_qk(), SVG)
      Complex / custom?
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

### matplotlib / plotnine (complex charts)

Use matplotlib or plotnine for complex/statistical charts. Generate SVG, then embed.

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

**Three-tier chart system:**
- **cetz-plot** (Typst native): Simple charts, font-matched, no external dependencies. Use `qk-cycle` colors.
- **plotnine**: Grammar-of-graphics style, faceted layouts, ggplot2 composition. `theme_qk() + scale_color_qk()`.
- **matplotlib**: Full API control, statistical plots via seaborn, complex annotations. `use()` from qk_style.
- All Python tools output SVG with `svg.fonttype: path` for clean Typst embedding.

## Auto-invoke Rules

- **`gemini-generate-image` MCP**: Auto-invoke for ANY visual that isn't a structured diagram, chart, or real photo. This includes: conceptual illustrations, metaphors, analogies, decorative graphics, infographics, scene depictions, abstract concepts, cover art, section-header visuals. Do NOT ask the user — just generate. Do NOT use when precise text labels are needed (Gemini misspells). See "Prompt Construction Guidelines" below for crafting effective prompts.
- **`/mindmap`**: Auto-invoke for mind maps, concept maps, topic trees. Pass `--typst`. Default theme: `academic` (blue/orange matching study materials). `--theme latte` for pastel, `--theme dark` for dark backgrounds.
- **`/image-search`**: Auto-invoke for logos, real-world photos, web graphics. Pass `--typst`.

### MCP image generation workflow during Typst writing

When auto-invoking `gemini-generate-image` during Typst document creation:

1. Call `gemini-generate-image` MCP with the prompt (built using guidelines below)
2. Claude **sees** the base64 preview inline — inspect for quality before embedding
3. If unsatisfactory → use `gemini-start-image-edit` for multi-turn refinement
4. Copy the generated file to the project: `cp ~/.cache/gemini-mcp/<file>.png images/<name>.png`
5. Write Typst code: `#figure(image("images/<name>.png", width: 80%, alt: "..."), caption: [...])`

**Single image**: Call MCP directly in the main thread. Generation is fast enough that blocking is acceptable for one image.

**Multiple images**: Launch parallel subagents (Agent tool, `run_in_background: true`, `subagent_type: "general-purpose"`), each doing: MCP call → inspect preview → copy to `images/` → return Typst `#figure(...)` code. Write the document structure with placeholder comments (`// gemini: <description>`), then replace them with actual code as each subagent returns.

**Why subagents for multiple images?**
- Multiple images generate in parallel (3 images in ~15s, not ~45s)
- Main context stays clean (generation output goes to subagent)
- Failure is isolated — one failed image doesn't break the document flow

### Prompt Construction Guidelines

When building prompts for `gemini-generate-image`, follow these rules:

1. **Describe scenes, not keywords** — "A three-legged wooden stool on a white background, each leg labeled..." beats "stool, risk parity, three legs"
2. **Specify style explicitly** — Include art style, lighting, and composition (e.g., "flat vector illustration", "isometric 3D render", "watercolor sketch")
3. **Use white backgrounds for documents** — Add "on a clean white background" for images that will be embedded in Typst documents
4. **Describe spatial layout** — "On the left... on the right..." helps Gemini compose multi-element scenes
5. **Don't rely on text labels** — Gemini often misspells text in images; describe the concept visually instead of asking for labeled diagrams

Examples:
```
gemini-generate-image: "A flat vector illustration of a three-legged wooden stool on a clean white background, representing risk parity with three balanced supports"
gemini-generate-image: "Abstract swirling watercolor in blue and gold tones on white background"
gemini-start-image-edit: (for iterating on a generated image — refine composition, adjust style)
/mindmap "Portfolio Theory" --typst --caption "Portfolio Theory Overview"
/image-search --logo "Goldman Sachs" --width 40%
/image-search "electric vehicle charging station" --size large
```

## User Override

If the user explicitly requests a specific tool, use it even if the routing table suggests otherwise. The table is a default, not a constraint.

## Fallback Chains

| If this fails... | Try instead... |
|------------------|----------------|
| `gemini-generate-image` MCP | Placeholder `#rect(width: 100%, height: 4cm, fill: luma(240))[Image placeholder]` |
| `/image-search` | `gemini-generate-image` MCP with descriptive prompt |
| `/mindmap` | `fletcher` tree diagram |
| plotnine | matplotlib (same chart, different API) |
| matplotlib | Check `.venv` exists → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` error | Isolate with `/* ... */`, compile incrementally |
