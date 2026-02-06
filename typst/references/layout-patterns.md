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
