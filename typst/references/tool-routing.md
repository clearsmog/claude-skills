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
| Simple charts (line, area, scatter, < 3 series) | **cetz-plot** | Native, font-matching, resolution-independent |
| Complex charts (4+ series, grouped bars, annotations) | **lilaq** | Native Typst data visualization package |
| Extreme charts (3D, 10+ series, exotic plot types) | **matplotlib** | Last resort — only when native tools genuinely can't handle it |

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
CHARTS       →  cetz-plot (simple) → lilaq (complex) → matplotlib (extreme, last resort)
MIND MAPS    →  /mindmap
IMAGES       →  /image-search (photos/logos) | gemini-generate-image (illustrations)
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

### cetz-plot (charts)

cetz-plot is bundled with cetz. Use for distribution plots, simple line/area charts, and anywhere you want resolution-independent, font-matching output.

```typst
#import "@preview/cetz:0.4.2": canvas
#import "@preview/cetz:0.4.2": plot as cplot

#figure(
  canvas(length: 1cm, {
    import draw: *
    cplot.plot(size: (7, 4), xlabel: [Return], ylabel: [Density], {
      cplot.add(domain: (-4, 4), samples: 80, fill: true,
        style: (stroke: rgb("#1565c0") + 1.5pt, fill: rgb("#1565c0").lighten(80%)),
        x => 0.399 * calc.exp(-0.5 * x * x))
    })
  }),
  caption: [Normal distribution with filled area],
)
```

**Key patterns:**
- `fill: true` on `cplot.add` fills from curve to x-axis
- Split domains to color regions differently
- `cplot.add-vline` / `cplot.add-hline` for reference lines
- For custom bar/waterfall charts, use `draw.rect` + `draw.content` in plain `canvas`

### lilaq (complex charts)

lilaq is a native Typst data visualization package for charts that exceed cetz-plot's capabilities — multi-series, grouped bars, annotations, and publication-quality formatting.

```typst
#import "@preview/lilaq:0.5.0" as lq

// Multi-series line chart
#figure(
  lq.diagram(
    width: 10cm, height: 6cm,
    xlabel: [Year], ylabel: [Return (%)],
    lq.plot(
      (2020, 2021, 2022, 2023, 2024),
      (8.2, 12.1, -5.3, 15.7, 9.4),
      label: [Fund A],
    ),
    lq.plot(
      (2020, 2021, 2022, 2023, 2024),
      (6.1, 9.8, -2.1, 11.3, 7.6),
      label: [Fund B],
    ),
    lq.plot(
      (2020, 2021, 2022, 2023, 2024),
      (4.5, 7.2, -8.9, 18.2, 5.1),
      label: [Fund C],
    ),
    lq.plot(
      (2020, 2021, 2022, 2023, 2024),
      (5.0, 8.0, -3.5, 12.0, 8.0),
      label: [Benchmark],
      stroke: (dash: "dashed"),
    ),
  ),
  caption: [Four-series fund performance comparison],
)
```

```typst
// Bar chart
#import "@preview/lilaq:0.5.0" as lq

#figure(
  lq.diagram(
    width: 10cm, height: 5cm,
    xlabel: [Asset Class], ylabel: [Allocation (%)],
    lq.bar(
      (0, 1, 2, 3),
      (40, 25, 20, 15),
      width: 0.6,
    ),
    xaxis: (subticks: none),  // custom tick labels via lq.tick-label ([Equities], [Bonds], [Real Estate], [Alternatives]),
  ),
  caption: [Portfolio allocation by asset class],
)
```

**When to use lilaq vs cetz-plot:**
- cetz-plot: < 3 series, simple line/area/scatter, distribution curves
- lilaq: 4+ series, grouped bars, bar charts with labels, publication-quality multi-panel
- matplotlib: only as last resort for 3D plots, 10+ series, or exotic types lilaq can't handle

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
| lilaq | cetz canvas primitives (`draw.rect`, `draw.content`) for manual chart building |
| matplotlib | Last resort for extreme chart complexity only. Check `.venv` exists → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` error | Isolate with `/* ... */`, compile incrementally |
