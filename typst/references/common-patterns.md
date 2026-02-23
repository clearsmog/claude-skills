# Common Patterns

## Tables

### Single Fill Parameter

Only ONE `fill:` parameter per table:

```typst
// CORRECT - single fill with conditions
#table(
  fill: (x, y) => if y == 0 { rgb("#263238") } else if calc.odd(y) { rgb("#f5f5f5") },
  columns: (auto, 1fr),
  [*Header*], [*Value*],
  [Row 1], [Data],
  [Row 2], [Data],
)

// WRONG - duplicate argument error
#table(
  fill: (x, y) => if y == 0 { gray },
  fill: (x, y) => if y == 1 { blue },  // ERROR!
  ...
)
```

### Table Options

```typst
#table(
  columns: (auto, 1fr, 2fr),      // Column widths
  align: (left, center, right),   // Per-column alignment
  inset: 8pt,                     // Cell padding
  stroke: 0.5pt,                  // Border thickness
  gutter: 1em,                    // Space between cells
  ...
)
```

### Repeating Table Headers (Typst 0.14+)

Headers automatically repeat on each page when using `table.header`:

```typst
#table(
  columns: 3,
  table.header(
    [Name], [Role], [Department],
  ),
  [Alice], [Engineer], [Platform],
  [Bob], [Designer], [Product],
  // ... many rows spanning pages
)
```

For hierarchical (multi-row) headers:

```typst
#table(
  columns: 4,
  table.header(
    table.cell(colspan: 2)[Revenue], table.cell(colspan: 2)[Costs],
    [Q1], [Q2], [Q1], [Q2],
  ),
  [100], [120], [80], [85],
)
```

## Templates

Apply document-wide styling with `#show:`:

```typst
// Use a template
#import "@preview/charged-ieee:0.1.0": ieee
#show: ieee.with(
  title: "My Paper",
  authors: ("Alice", "Bob"),
)

// Custom show rules
#show heading.where(level: 1): it => {
  set text(size: 16pt, weight: "bold")
  block(above: 1em, below: 0.5em, it.body)
}
```

## Bibliography

Typst supports BibTeX (.bib) and Hayagriva (.yml) formats:

```typst
// In your document
This is a citation @einstein1905.

// At the end
#bibliography("references.bib")
```

## Large Documents (500+ lines)

### File Organization

Split into multiple files when a document exceeds ~500 lines:

```
project/
├── main.typ          # Entry point: #include for each section
├── lib.typ           # Shared helpers, colors, functions
├── sections/
│   ├── 01-intro.typ
│   ├── 02-analysis.typ
│   └── 03-conclusion.typ
└── images/
```

```typst
// main.typ
#import "lib.typ": *
#include "sections/01-intro.typ"
#include "sections/02-analysis.typ"
#include "sections/03-conclusion.typ"
```

Compile with: `typst compile main.typ --root .`

### Reusable Helper Pattern

Define helpers as functions returning content — the pattern used across
all templates in [templates.md](templates.md):

```typst
// Callout box factory — one function, many variants
#let _box(title, fg, bg, border, body) = block(
  width: 100%, inset: 10pt, radius: 3pt, fill: bg, stroke: 0.5pt + border,
)[#text(size: 9pt, weight: "bold", fill: fg)[#title] #v(0.2em) #text(size: 9pt)[#body]]

// One-liner wrappers for each variant
#let warning(body) = _box("Warning", rgb("#991b1b"), rgb("#fef2f2"), rgb("#dc2626"), body)
#let tip(body)     = _box("Tip", rgb("#004d40"), rgb("#e0f2f1"), rgb("#00897b"), body)
```

