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

## Safe Patterns

### Blank Fields

```typst
// CORRECT
[......%]          // Dots for blanks
Answer: ____________   // Underscores outside brackets

// WRONG
[_____%]           // Underscores trigger emphasis inside []
```

### Currency

```typst
// CORRECT
[\$5,000]          // Escaped dollar
£10,000            // Pound OK
EUR 5,000          // Text alternative

// WRONG
[$5,000]           // Starts math mode
```

## Quick Reference

```typst
// Page setup
#set page(margin: 1.5cm, paper: "a4")
#set text(font: "New Computer Modern", size: 10pt)

// Headings
= Level 1
== Level 2
=== Level 3

// Text formatting
*bold*  _italic_  `code`  #underline[underlined]

// Colors
#text(fill: rgb("#ff0000"))[Red text]
#rect(fill: blue.lighten(80%), inset: 10pt)[Box]

// Layout
#grid(columns: (1fr, 1fr), gutter: 1em, [Col 1], [Col 2])
#v(1em)        // Vertical space
#h(1fr)        // Flexible horizontal space (push right)
#pagebreak()   // New page

// Lists
- Bullet item
- Another item
  - Nested

+ Numbered item
+ Another

// Math
$E = m c^2$                    // Inline
$ integral_0^infinity f(x) $   // Display
```
