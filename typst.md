---
name: typst
description: Syntax guide and ecosystem reference for writing Typst (.typ) files. Use this skill when writing, editing, or debugging Typst documents. Covers core syntax, common errors, packages, and best practices.
license: MIT
---

# Typst Syntax & Ecosystem Guide

Use this skill when writing or editing Typst (.typ) files.

## Documentation

- **Official Reference:** https://typst.app/docs/reference/
- **Package Registry:** https://typst.app/universe/
- **Tutorial:** https://typst.app/docs/tutorial/

## Core Syntax

### Arrays and Dictionaries

Typst uses **parentheses** for both (not square brackets like Python/JS):

```typst
// Arrays - use ()
let colors = (red, green, blue)
let first = colors.at(0)        // NOT colors[0]
let length = colors.len()

// Dictionaries - use () with colons
let person = (name: "Alice", age: 30)
let name = person.name          // or person.at("name")

// WRONG - common mistakes
let arr = [1, 2, 3]             // This is a content block, not array!
let item = arr[0]               // Wrong access syntax
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

## Special Characters

| Character | Problem | Solution |
|-----------|---------|----------|
| `#` | Command prefix | Escape with `\#` in content |
| `_` | Triggers emphasis | Use `......` for blanks, not `_____` |
| `*` | Triggers bold | Escape with `\*` if needed literally |
| `@` | Reference/citation | Escape with `\@` in plain text |
| `$` | Math mode | Escape with `\$` for currency |

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

## Symbols

Use `#sym.*` for reliable cross-platform symbols:

```typst
// Arrows
#sym.arrow.r       // → right
#sym.arrow.l       // ← left
#sym.arrow.l.r     // ↔ bidirectional
#sym.arrow.t       // ↑ up
#sym.arrow.b       // ↓ down

// Common
#sym.square        // □ checkbox
#sym.checkmark     // ✓ checkmark
#sym.dot           // · middle dot
#sym.bullet        // • bullet
#sym.dash.em       // — em dash

// Math/logic
#sym.times         // × multiplication
#sym.div           // ÷ division
#sym.lt.eq         // ≤ less or equal
#sym.gt.eq         // ≥ greater or equal
#sym.approx        // ≈ approximately
#sym.percent       // % percent
```

## Popular Packages

Install from https://typst.app/universe/

| Package | Purpose | Usage |
|---------|---------|-------|
| **cetz** | Diagrams, drawings | `#import "@preview/cetz:0.2.0"` |
| **fletcher** | Flowcharts, arrows | `#import "@preview/fletcher:0.4.0"` |
| **tablex** | Advanced tables | `#import "@preview/tablex:0.0.8"` |
| **polylux** | Presentations/slides | `#import "@preview/polylux:0.3.1"` |
| **lovelace** | Pseudocode | `#import "@preview/lovelace:0.2.0"` |
| **codelst** | Code listings | `#import "@preview/codelst:2.0.0"` |

```typst
// Example: Using a package
#import "@preview/tablex:0.0.8": tablex, rowspanx, colspanx

#tablex(
  columns: 3,
  [A], [B], [C],
  [1], [2], [3],
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

## Common Errors

### "unclosed delimiter"

Special character inside `[brackets]`:

```typst
// ERROR
[Value: ____]

// FIX
[Value: ......]    // Use dots
```

### "duplicate argument"

Same parameter used twice:

```typst
// ERROR
#rect(fill: red, fill: blue)

// FIX
#rect(fill: red)
```

### "unexpected" token

Unescaped special character:

```typst
// ERROR
[Cost: $500]

// FIX
[Cost: \$500]
```

### "unknown variable"

Forgot `#` in markup context:

```typst
// ERROR
let x = 5          // Missing #

// FIX
#let x = 5
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

## Debugging

1. **Compile incrementally** — Don't write 200 lines then compile
2. **Check line numbers** — Errors show exact location
3. **Watch mode** — Auto-recompile on save:
   ```bash
   typst watch file.typ file.pdf
   ```
4. **Isolate problems** — Comment out sections with `/* ... */`
