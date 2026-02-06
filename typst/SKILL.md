---
name: typst
description: Syntax guide and ecosystem reference for writing Typst (.typ) files. Use this skill when writing, editing, or debugging Typst documents. Covers core syntax, common errors, packages, and best practices.
license: MIT
---

# Typst Syntax & Ecosystem Guide

Use this skill when writing or editing Typst (.typ) files.

**Current Typst version**: 0.14.x (Dec 2025)

## Documentation

- **Official Reference:** https://typst.app/docs/reference/
- **Package Registry:** https://typst.app/universe/
- **Tutorial:** https://typst.app/docs/tutorial/
- **Changelog:** https://typst.app/docs/changelog/

### Reference Files

- [references/math-pitfalls.md](references/math-pitfalls.md) - Currency in math, adjacent letters, commas, angle brackets
- [references/layout-patterns.md](references/layout-patterns.md) - Compact setup, spacing, nested boxes, color themes
- [references/symbols.md](references/symbols.md) - `sym.*` arrows, common symbols, math/logic
- [references/packages.md](references/packages.md) - Popular packages with import syntax

## What's New in 0.13-0.14

| Feature | Ver | Description |
|---------|-----|-------------|
| Tagged PDFs by default | 0.14 | Accessible PDFs out of the box, PDF/UA-1 support |
| `figure.alt` / `image(alt:)` | 0.14 | Alt text for screen readers |
| `pdf.attach` | 0.14 | Attach files to PDFs (replaces deprecated `pdf.embed`) |
| Character justification | 0.14 | `par.justification-limits` for microtypography |
| Multithreaded layout | 0.14 | 2-3x speedup for large documents |
| `curve` function | 0.13 | Bezier curve drawing (replaces deprecated `path`) |
| First-line indent | 0.13 | `#set par(first-line-indent: 1em)` with `all: true` |

### Deprecated Functions

- `path` -> use `curve` instead (Bezier curves)
- `pdf.embed` -> use `pdf.attach` instead
- `image.decode` -> pass bytes directly to `image`
- `polylux:0.3.1` is **incompatible** with Typst 0.14 -> use `touying` instead

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
| `$` | Math mode delimiter | Escape with `\$` for currency; NEVER use inside `$ $` |
| `<>` | Label reference | Use words ("below", "above") or escape with `\<` `\>` |
| `£` `€` | Unknown in math mode | Keep currency symbols OUTSIDE math expressions |

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

## Common Errors

### "unclosed delimiter"

Special character inside `[brackets]` or currency in math:

```typst
// ERROR - underscore in brackets
[Value: ____]

// FIX
[Value: ......]    // Use dots

// ERROR - $ in math mode
$ P = $500 $

// FIX
$ P = 500 $
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

Forgot `#` in markup context, or adjacent letters in math mode:

```typst
// ERROR - missing #
let x = 5

// FIX
#let x = 5

// ERROR - adjacent letters parsed as one variable
$NPV = 0$          // "unknown variable: NPV"

// FIX - separate with spaces or quote as string
$"NPV" = 0$
```

See [references/math-pitfalls.md](references/math-pitfalls.md) for full math mode pitfalls.

### "can only be used when context is known"

Counter/state access in headers needs `context`:

```typst
// ERROR
#set page(header: [Page #counter(page).display()])

// FIX
#set page(header: context [Page #counter(page).display()])
```

### "only element functions can be used as selectors"

Package incompatible with Typst 0.14+. Check package version requirements or use alternatives (e.g. `polylux` -> `touying`).

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

## CLI Commands

```bash
typst compile document.typ                     # Compile to PDF
typst watch document.typ                       # Watch and recompile
typst compile document.typ out.pdf --pages 1-5 # Specific pages
typst query document.typ "heading.where(level: 1)"  # Query metadata
typst fonts                                    # List available fonts
typst compile --timings document.typ           # Profile compilation
```

## Debugging

1. **Compile incrementally** — Don't write 200 lines then compile
2. **Check line numbers** — Errors show exact location
3. **Watch mode** — Auto-recompile on save:
   ```bash
   typst watch file.typ file.pdf
   ```
4. **Isolate problems** — Comment out sections with `/* ... */`
