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
- [references/layout-patterns.md](references/layout-patterns.md) - Compact setup, spacing, nested boxes, color themes, `curve` function
- [references/symbols.md](references/symbols.md) - `sym.*` arrows, common symbols, math/logic
- [references/packages.md](references/packages.md) - Popular packages with import syntax
- [references/common-patterns.md](references/common-patterns.md) - Tables, templates, bibliography, safe patterns, quick reference

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

- `path` -> use `curve` instead (see [layout-patterns.md](references/layout-patterns.md#curve-function-replaces-path))
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

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "unclosed delimiter" | `_` or `$` in `[]` | Escape: `\$`, use `......` not `____` |
| "duplicate argument" | Same param twice | Remove duplicate |
| "unexpected token" | Unescaped special char | Escape: `\$`, `\#`, `\@` |
| "unknown variable" | Missing `#` or `$NPV$` | Add `#`, or `$"NPV"$` |
| "context is known" | Counter in header | Wrap in `context [...]` |
| "element functions" | Old package | Update package or use `touying` |

See [references/math-pitfalls.md](references/math-pitfalls.md) for full math mode pitfalls.

## CLI Commands

```bash
typst compile document.typ                     # Compile to PDF
typst watch document.typ                       # Watch and recompile
typst compile document.typ out.pdf --pages 1-5 # Specific pages
typst fonts                                    # List available fonts
```

## Image Generation (`/nano-banana`)

When a Typst document needs images, choose the right tool:

| Need | Tool | Why |
|------|------|-----|
| Callout boxes, styled `rect()` layouts | **Typst native** | Matches fonts, editable in source |
| Simple flowcharts (< 10 nodes) | **Typst native** (`fletcher` or `cetz` package) | Precise labels, version-friendly |
| Tables, grids, comparison layouts | **Typst native** | Perfect fit |
| Data-driven charts (bar, scatter, line) | **matplotlib/Python** | Numerical precision |
| Conceptual illustrations or metaphors | **`/nano-banana`** | Artistic visuals Typst can't draw |
| Photorealistic or decorative images | **`/nano-banana`** | Only AI generation can do this |
| Complex diagrams where label accuracy doesn't matter | **`/nano-banana`** | Faster than 100+ lines of Typst |

**Auto-invoke rule:** When the user requests a conceptual diagram, illustration, or visual that cannot be reasonably drawn with Typst native tools or packages, automatically run `/nano-banana` to generate it via Gemini. Pass `--typst` to get ready-to-paste `#figure(image(...))` code. Do NOT ask the user whether to use `/nano-banana` — just use it.

**Do NOT use `/nano-banana`** when the image needs precise text labels (Gemini often misspells), or when the visual is a structured layout that Typst handles natively (boxes, tables, grids).

Example:
```bash
/nano-banana "three-legged stool analogy for risk parity" --dir images --width 80%
```

## Mind Map Generation (`/mindmap`)

When a Typst document needs a mind map or concept overview:

| Need | Tool | Why |
|------|------|-----|
| Hierarchical topic overview (3+ branches) | **`/mindmap`** | Organic layout, curved connectors, color-coded |
| Simple 2-level list | **Typst native** | Overkill to launch Puppeteer for a flat list |
| Flowchart with directional logic | **Typst native** (`fletcher`) | Mind maps show hierarchy, not flow |

**Auto-invoke rule:** When the user requests a mind map, concept map, topic tree, or overview diagram for a Typst document, automatically run `/mindmap` to generate it. Pass `--typst --format svg` for vector output (crisp text at any zoom). Do NOT ask the user whether to use `/mindmap` — just use it.

Example:
```bash
/mindmap "Portfolio Theory" --typst --format svg --caption "Portfolio Theory Overview"
```

Default theme (`academic`) uses blue/orange colors matching the Typst study materials palette. Use `--theme latte` for a pastel alternative or `--theme dark` for dark backgrounds.

## Debugging

1. **Compile incrementally** — Don't write 200 lines then compile
2. **Check line numbers** — Errors show exact location
3. **Watch mode** — Auto-recompile on save:
   ```bash
   typst watch file.typ file.pdf
   ```
4. **Isolate problems** — Comment out sections with `/* ... */`
