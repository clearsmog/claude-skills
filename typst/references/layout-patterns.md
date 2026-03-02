# Layout Patterns

## Compact Document Setup

For dense reference guides, cheatsheets, or documentation:

```typst
// Compact page setup
#set page(margin: (x: 1.2cm, y: 1.2cm), paper: "a4")
#set text(font: "New Computer Modern", size: 8.5pt)
#set par(leading: 0.5em, spacing: 0.6em, justify: true)
#show heading: set block(above: 0.8em, below: 0.4em)
```

**Parameter guide:**
- `leading`: Line spacing within paragraphs (0.5em = compact, 0.65em = normal)
- `spacing`: Space between paragraphs (0.6em = tight, 1em = normal)
- `justify: true`: Fill line width for denser text

## Spacing Hierarchy

Use consistent vertical spacing between elements:

```typst
#v(0.3em)   // Between major sections/boxes
#v(0.25em)  // Between subsections
#v(0.2em)   // Between tightly related items
```

## Nested Box Pattern

For step-by-step guides with instructions inside containers:

```typst
// Outer container (10pt inset)
#rect(fill: rgb("#e3f2fd"), radius: 5pt, width: 100%, inset: 10pt)[
  #text(weight: "bold", size: 12pt)[Step Title]
  #v(0.3em)

  // Inner instruction box (6pt inset)
  #rect(fill: rgb("#bbdefb"), radius: 3pt, inset: 6pt)[
    #text(size: 8pt)[
      1. First instruction\
      2. Second instruction
    ]
  ]
]
```

**Inset sizing rule:**
| Element | Inset |
|---------|-------|
| Outer containers | 10pt |
| Nested/inner boxes | 6pt |
| Tables | 3pt |

## Color-Coded Sections

Consistent color pairs (outer, inner) for multi-section documents:

```typst
// Blue theme
#rect(fill: rgb("#e3f2fd"), ...)[  // outer
  #rect(fill: rgb("#bbdefb"), ...)  // inner
]

// Green theme
#rect(fill: rgb("#e8f5e9"), ...)[  // outer
  #rect(fill: rgb("#c8e6c9"), ...)  // inner
]

// Orange theme
#rect(fill: rgb("#fff3e0"), ...)[  // outer
  #rect(fill: rgb("#ffe0b2"), ...)  // inner
]

// Purple theme
#rect(fill: rgb("#f3e5f5"), ...)[  // outer
  #rect(fill: rgb("#e1bee7"), ...)  // inner
]
```

## Slide / Presentation Layout

For 16:9 slide decks without external packages (no polylux/touying):

```typst
#set page(width: 254mm, height: 142.9mm, margin: (x: 12mm, y: 8mm))

// Slide separator — each pagebreak starts a new slide
#let slide(title, body) = {
  pagebreak(weak: true)
  // Header bar
  place(top + left, dx: -12mm, dy: -8mm,
    rect(width: 254mm, height: 3mm, fill: rgb("#1B365D")))
  v(2mm)
  text(size: 16pt, weight: "bold", fill: rgb("#1B365D"), title)
  v(4mm)
  body
}
```

**Key dimensions:**
| Aspect | 16:9 | 4:3 |
|--------|------|-----|
| Width | 254mm | 254mm |
| Height | 142.9mm | 190.5mm |
| Margins | 12mm x 8mm | 15mm x 12mm |

**Tips:**
- Use `place()` for absolute positioning on slides
- `grid(columns: (1fr, 1fr))` for two-column layouts
- Keep font at 9pt body / 16pt titles for readability
- Use `#set page(footer: none)` — slides don't need page numbers

## Figures and Images

### Figure Floating

By default, Typst figures are placed inline. If a figure doesn't fit on the remaining page, it pushes to the next page — leaving a blank gap. Fix with:

```typst
// Enable globally (recommended for multi-page documents)
#set figure(placement: auto)

// Or per-figure
#figure(placement: top, image("chart.png", width: 90%),
  caption: [My chart],
)
```

- `auto`: Typst chooses top or bottom of nearest page
- `top` / `bottom`: Force specific position
- Figures float independently — text flows around their anchor point

### Image Sizing by Aspect Ratio

Check aspect ratio (height / width) to choose width%:

| Aspect Ratio | Shape | Recommended Width |
|-------------|-------|-------------------|
| < 0.4 | Wide/panoramic | 100% |
| 0.4–0.6 | Moderate | 90–100% |
| > 0.6 | Tall/square | 95% (never below 80%) |

Tall images at low width% make embedded text unreadable. When in doubt, use 95%.

Check dimensions on macOS: `sips -g pixelWidth -g pixelHeight image.png`

### When to Replace PNG with Native Typst

Replace an image with a Typst table/block when:
- The image is a **table or grid** (comparison charts, matrices, sign tables)
- The image has **nested cells with small text** that becomes unreadable when scaled
- The content is **structured data**, not a spatial diagram with arrows

Keep as PNG when:
- The image has **arrows, flow paths, or spatial layout** (flowcharts, causal diagrams)
- The chart needs **grouped bars, complex annotations, or precise axis formatting** — lilaq can handle grouped bars natively

Use **cetz-plot or lilaq** (not external tools) when:
- The chart is a **filled-area distribution plot** — `cplot.add(fill: true, ...)` handles shaded regions cleanly
- The chart is a **simple line/scatter/area plot** with < 3 series
- You want the chart to match document fonts and be resolution-independent
- cetz canvas primitives (`draw.rect`, `draw.line`, `draw.content`) work well for **waterfall charts** and custom bar charts

For flowcharts you must keep as PNG, use 95% width for readability.

### Replacing a figure with native content

Typst `#figure()` accepts any content, not just images:

```typst
#figure(
  table(
    columns: (1fr, 1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#0d47a1") }
      else if x == y { rgb("#c8e6c9") }
      else { rgb("#ffcdd2") },
    // ... table content
  ),
  caption: [My native table figure],
)
```

This keeps figure numbering consistent while using crisp native rendering.

### Page Break Pitfalls

- `#pagebreak()` before a section that starts with a figure creates a blank page — the figure floats away, leaving the forced break with nothing after it
- Do NOT add `#v()` spacers around `#figure()` — they compound page-break gaps
- With `placement: auto` enabled, Typst handles spacing automatically

## `curve` Function (replaces `path`)

```typst
// Line segments
#curve(
  curve.move((0pt, 0pt)),
  curve.line((30pt, 0pt)),
  curve.line((30pt, 30pt)),
  curve.close(),
  fill: blue.lighten(80%),
  stroke: blue,
)

// Cubic Bezier curves
#curve(
  curve.move((0pt, 50pt)),
  curve.cubic((20pt, 0pt), (40pt, 0pt), (60pt, 50pt)),
  stroke: 2pt + red,
)

// Close path for filled shapes
#curve(
  curve.move((0pt, 0pt)),
  curve.line((40pt, 0pt)),
  curve.cubic((40pt, 20pt), (0pt, 20pt), (0pt, 40pt)),
  curve.close(),
  fill: gradient.linear(blue, purple),
)
```

Key: `curve.move` sets start, `curve.line` draws straight, `curve.cubic(ctrl1, ctrl2, end)` draws Bezier, `curve.close()` connects back to start.
