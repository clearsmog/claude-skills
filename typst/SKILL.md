---
name: typst
description: Syntax guide and ecosystem reference for writing Typst (.typ) files. Use this skill when writing, editing, or debugging Typst documents. Covers core syntax, common errors, packages, accessibility, and best practices.
version: 2.0.0
license: MIT
targets:
  - typst: ">=0.14.0"
---

# Typst Syntax & Ecosystem Guide

Use this skill when writing or editing Typst (.typ) files.

**Current Typst version**: 0.14.2 (Dec 2025)

## Documentation

- **Official Reference**: https://typst.app/docs/reference/
- **Changelog**: https://typst.app/docs/changelog/
- **Package Registry**: https://typst.app/universe/
- **Accessibility Guide**: https://typst.app/docs/guides/accessibility/

### Reference Files

- [references/syntax.md](references/syntax.md) - Core syntax patterns and new features
- [references/bibliography.md](references/bibliography.md) - Citations and bibliographies
- [references/accessibility.md](references/accessibility.md) - PDF/UA, alt text, tagged PDFs
- [references/html-export.md](references/html-export.md) - HTML export and `target()` function

## What's New in Typst 0.13-0.14

| Feature | Version | Description |
|---------|---------|-------------|
| Accessibility | 0.14 | Tagged PDFs by default, PDF/UA-1 support |
| `figure.alt` | 0.14 | Alt text for screen readers |
| `pdf.attach` | 0.14 | Attach files to PDFs (replaces `pdf.embed`) |
| Character justification | 0.14 | `par.justification-limits` for microtypography |
| Multithreaded layout | 0.14 | 2-3x speedup for large documents |
| `curve` function | 0.13 | New Bézier curve drawing (replaces `path`) |
| First-line indent | 0.13 | Works on all paragraphs with `all: true` |
| HTML export | 0.13 | Experimental, use `target()` for conditional rendering |

## Core Syntax

### Arrays and Dictionaries

Typst uses **parentheses** for both (not square brackets like Python/JS):

```typst
// Arrays - use ()
#let colors = (red, green, blue)
#let first = colors.at(0)        // NOT colors[0]
#let length = colors.len()
#let singleton = (item,)         // Trailing comma for single-element

// Dictionaries - use () with colons
#let person = (name: "Alice", age: 30)
#let name = person.name          // or person.at("name")

// WRONG - common mistakes
#let arr = [1, 2, 3]             // This is a content block, not array!
#let item = arr[0]               // Wrong access syntax
```

### Content Blocks vs Code Blocks

```typst
// Content blocks [] - for markup/text
[This is *bold* and _italic_ text]

// Code blocks {} - for logic
{
  let x = 5
  if x > 3 { "big" } else { "small" }
}

// In markup mode, use # to switch to code
This is text. #let x = 5 Now x is #x.
```

### The # Prefix

In markup context, `#` switches to code mode:

```typst
// Markup mode (default at start of file)
Hello world.
#let name = "Alice"           // # needed for code
My name is #name.             // # needed to evaluate

// In code block, # not needed
#{
  let x = 5                   // No # needed inside {}
  x + 3
}
```

## CLI Commands

### Basic Commands

```bash
# Compile to PDF
typst compile document.typ

# Watch and recompile on changes
typst watch document.typ

# Compile specific pages
typst compile document.typ output.pdf --pages 1-5

# Query document metadata
typst query document.typ "heading.where(level: 1)" | jq ".[].body.text"

# List available fonts
typst fonts
```

### PDF Standards and Accessibility

```bash
# Enable PDF/UA-1 for accessibility compliance
typst compile document.typ --pdf-standard ua-1

# Use specific PDF version
typst compile document.typ --pdf-standard 2.0

# PDF/A for archival
typst compile document.typ --pdf-standard a-2b

# Combine standards
typst compile document.typ --pdf-standard 1.7,ua-1
```

**Valid PDF standards**: `1.4`, `1.5`, `1.6`, `1.7`, `2.0`, `a-1b`, `a-1a`, `a-2b`, `a-2u`, `a-2a`, `a-3b`, `a-3u`, `a-3a`, `a-4`, `a-4f`, `a-4e`, `ua-1`

### HTML Export (Experimental)

```bash
TYPST_FEATURES=html typst compile document.typ output.html
```

## Accessibility (0.14+)

Typst produces accessible tagged PDFs by default.

```typst
// Always set document metadata
#set document(title: "Document Title", author: "Author Name")
#set text(lang: "en")

// Add alt text to images
#image("chart.png", alt: "Bar chart showing sales growth")

// Alt text for complex figures
#figure(
  stack(dir: ltr, rect[A], sym.arrow, rect[B]),
  alt: "Flow diagram showing A leads to B",
  caption: [Process Flow],
)
```

See [references/accessibility.md](references/accessibility.md) for detailed guidelines.

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
)

// WRONG - duplicate argument error
#table(
  fill: (x, y) => if y == 0 { gray },
  fill: (x, y) => if y == 1 { blue },  // ERROR!
  ...
)
```

## New Features

### Curve Function (0.13)

Replaces `path` for Bézier curves:

```typst
#curve(
  stroke: 2pt + blue,
  curve.move((0pt, 0pt)),
  curve.line((50pt, 0pt)),
  curve.quad((25pt, -20pt), (50pt, 0pt)),  // Quadratic
  curve.cubic((10pt, 0pt), (40pt, 50pt), (50pt, 25pt)),  // Cubic
  curve.close(),
)
```

### Character-Level Justification (0.14)

```typst
#set par(
  justify: true,
  justification-limits: (min: -0.02em, max: 0.02em),
)
```

### PDF Attachments (0.14)

```typst
#pdf.attach(
  "data.xml",
  read("invoice-data.xml", encoding: none),
  mime-type: "application/xml",
)
```

See [references/syntax.md](references/syntax.md) for more new features.

## Popular Packages (2025)

| Package | Purpose | Version |
|---------|---------|---------|
| **cetz** | Diagrams, drawings | 0.4.2 |
| **fletcher** | Flowcharts, arrows | 0.5.9 |
| **codly** | Code blocks | latest |
| **polylux** | Presentations | latest |
| **touying** | Modern slides | latest |
| **pinit** | Arrows/pointers | latest |
| **tiaoma** | QR codes/barcodes | 0.3.0 |
| **gentle-clues** | Callouts | latest |

```typst
#import "@preview/cetz:0.4.2"
#import "@preview/fletcher:0.5.9"
```

## Templates

```typst
#import "@preview/charged-ieee:0.1.4": *

#show: ieee.with(
  title: "My Paper",
  authors: (
    (name: "Author One", email: "author@example.com"),
  ),
  abstract: [Your abstract...],
  bibliography: bibliography("refs.bib"),
)

= Introduction
...
```

## Bibliography

```typst
// Cite in text
This is a citation @einstein1905.
With page: @smith2023[p. 42]

// At the end
#bibliography("references.bib", style: "ieee")
```

See [references/bibliography.md](references/bibliography.md) for complete guide.

## Common Mistakes to Avoid

- ❌ Using `[]` for arrays (use `()` instead)
- ❌ Accessing array elements with `arr[0]` (use `arr.at(0)`)
- ❌ Forgetting `#` prefix for code in markup context
- ❌ Using `pdf.embed` (deprecated - use `pdf.attach`)
- ❌ Using `path` for curves (use `curve` instead)
- ❌ Forgetting alt text on figures (accessibility)

## Special Characters

| Character | Problem | Solution |
|-----------|---------|----------|
| `#` | Command prefix | Escape with `\#` |
| `_` | Triggers emphasis | Escape with `\_` |
| `*` | Triggers bold | Escape with `\*` |
| `@` | Reference/citation | Escape with `\@` |
| `$` | Math mode | Escape with `\$` |

## Quick Reference

```typst
// Page setup
#set page(margin: 1.5cm, paper: "a4")
#set text(font: "New Computer Modern", size: 11pt, lang: "en")
#set document(title: "Title", author: "Author")

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
#h(1fr)        // Flexible horizontal space
#pagebreak()   // New page

// Lists
- Bullet item
  - Nested

+ Numbered item

// Math
$E = m c^2$                    // Inline
$ integral_0^infinity f(x) $   // Display

// Figure with alt text
#figure(
  image("img.png", alt: "Description"),
  caption: [Caption text],
)
```

## Debugging

1. **Watch mode** — Auto-recompile: `typst watch file.typ`
2. **Check line numbers** — Errors show exact location
3. **Profile** — `typst compile --timings file.typ`
4. **Isolate problems** — Comment out sections with `/* ... */`
