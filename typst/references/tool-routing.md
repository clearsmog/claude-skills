# Visual Tool Routing

## Priority Order

When a Typst document needs a visual, follow this priority:

1. **Typst native** — Can Typst draw it? (table, grid, box, flowchart via `fletcher`)
2. **cetz-plot** — Simple chart (line, area, scatter, < 3 series)? Font-matching, resolution-independent
3. **`/image-search`** — Real photograph, logo, or existing graphic?
4. **`/mindmap`** — Mind map or hierarchical overview?
5. **Native Typst packages** — Structured diagram (sequence, Gantt, timeline)?
6. **matplotlib/Python** — Complex chart (grouped bars, annotations, many series)?
7. **`/nano-banana`** — Conceptual illustration, metaphor, artistic visual?

## Routing Table

| Need | Tool | Why |
|------|------|-----|
| Callout boxes, styled `rect()` layouts | **Typst native** | Matches fonts, editable in source |
| Flowcharts (any size) | **`fletcher`** | Precise labels, version-friendly, no external tool |
| Sequence diagrams | **`chronos`** | Native Typst package for lifelines and messages |
| Gantt charts | **`timeliney`** | Native Typst timeline layout with dependencies |
| Linear timelines | **`herodot`** | Native Typst historical/event timelines |
| ER diagrams, state diagrams | **`fletcher`** (styled) | Entities as nodes, relationships as edges |
| Tables, grids, comparison layouts | **Typst native** | Perfect fit |
| Simple charts (line, area, scatter) | **cetz-plot** | Native, font-matching, resolution-independent |
| Complex charts (grouped bars, 4+ series) | **matplotlib/Python** | Full control over axes, legends, annotations |
| Mind map, concept map, topic tree | **`/mindmap`** | Organic layout, curved connectors, color-coded |
| Conceptual illustrations | **`/nano-banana`** | Artistic visuals Typst can't draw |
| Photorealistic or decorative | **`/nano-banana`** | Only AI generation can do this |
| Company/brand logos | **`/image-search --logo`** | Exact logo from Logo.dev |
| Real-world photos | **`/image-search`** | Google Images via SerpAPI |
| Stock photos (license-clear) | **`/image-search --stock`** | Unsplash/Pexels APIs |
| Existing graphic from URL | **`/image-search --url`** | Direct download |

## Native Typst Diagram Packages

### fletcher (flowcharts, trees, ER, state diagrams)

```typst
#import "@preview/fletcher:0.5.8": diagram, node, edge
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
    cplot.plot(size: (7, 4), x-label: [Return], y-label: [Density], {
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

## Auto-invoke Rules

- **`/nano-banana`**: Auto-invoke for conceptual diagrams or illustrations that can't be drawn natively. Pass `--typst` for ready-to-paste code. Do NOT ask the user — just use it. Do NOT use when precise text labels are needed (Gemini misspells).
- **`/mindmap`**: Auto-invoke for mind maps, concept maps, topic trees. Pass `--typst`. Default theme: `academic` (blue/orange matching study materials). `--theme latte` for pastel, `--theme dark` for dark backgrounds.
- **`/image-search`**: Auto-invoke for logos, real-world photos, web graphics. Pass `--typst`.

Examples:
```bash
/nano-banana "three-legged stool analogy for risk parity" --dir images --width 80%
/mindmap "Portfolio Theory" --typst --caption "Portfolio Theory Overview"
/image-search --logo "Goldman Sachs" --width 40%
/image-search "electric vehicle charging station" --size large
/image-search --stock "sustainable energy" -n 2
```

## User Override

If the user explicitly requests a specific tool, use it even if the routing table suggests otherwise. The table is a default, not a constraint.

## Fallback Chains

| If this fails... | Try instead... |
|------------------|----------------|
| `/nano-banana` | Placeholder `#rect(width: 100%, height: 4cm, fill: luma(240))[Image placeholder]` |
| `/image-search` | `/nano-banana` with descriptive prompt |
| `/mindmap` | `fletcher` tree diagram |
| matplotlib | Check `.venv` exists → `uv venv .venv.nosync && ln -s .venv.nosync .venv` |
| `typst compile` error | Isolate with `/* ... */`, compile incrementally |
