# Quick Reference

## Top 5 Errors (by frequency)

| Error | Cause | Fix |
|-------|-------|-----|
| Unescaped `$` in content | `$5,000` starts math mode | `\$5,000` — scan all `$` before compiling |
| "unclosed delimiter" | `_` or `$` inside `[]` content | Escape: `\$`, use `......` not `____` for blanks |
| "unknown variable" | Missing `#` prefix, or `$NPV$` | Add `#`, or quote multi-letter: `$"NPV"$` |
| "unknown variable: True/None" | Expression chaining: `#func()(` parsed as call | Insert `~` after `#func()` — breaks greedy parsing |
| `<text>` parsed as label | Angle brackets in content (including CJK) | Escape `\<` `\>`, use words, or fullwidth `＜＞` |

Additional errors:

| Error | Cause | Fix |
|-------|-------|-----|
| "duplicate argument" | Same param twice | Remove duplicate |
| "unexpected token" | Unescaped special char | Escape: `\$`, `\#`, `\@` |
| "context is known" | Counter in header | Wrap in `context [...]` |
| "element functions" | Old package | Update package or use `touying` |
| "module `emoji` does not contain" | Not all emoji exist | Use `sym.*` instead |

## Special Characters

| Character | Problem | Solution |
|-----------|---------|----------|
| `#` | Command prefix | `\#` in content |
| `_` | Triggers emphasis | `......` for blanks, not `_____` |
| `*` | Triggers bold (even in captions!) | `\*` or rephrase; use `times` in math |
| `@` | Reference/citation | `\@` in plain text |
| `$` | Math mode delimiter | `\$` for currency; NEVER inside `$ $` |
| `<>` | Label reference in ALL content | `\<` `\>`, use words, or fullwidth `＜＞` |
| `£` `€` | Unknown in math mode | Keep currency OUTSIDE math expressions |

## Core Syntax

### Data Structures

```typst
// Arrays — parentheses, NOT []
#let colors = (red, green, blue)
#let first = colors.at(0)           // NOT colors[0]
#let length = colors.len()

// Dictionaries — parentheses with colons
#let person = (name: "Alice", age: 30)
#let name = person.name             // or person.at("name")

// Content blocks — [] for markup
[This is *bold* and _italic_ text]

// Code blocks — {} for logic
{ let x = 5; if x > 3 { "big" } else { "small" } }

// WRONG — common mistakes
#let arr = [1, 2, 3]               // This is content, not array!
#let item = arr[0]                  // Wrong access syntax
```

### The `#` Prefix

In markup mode, `#` switches to code: `#let x = 5`, `#x`, `#{...}`.
Inside `{}` code blocks, `#` is not needed.

### Variadic Arguments

```typst
#let items(..args) = {
  for item in args.pos() { [- #item] }
}
```

### State Management

```typst
#let counter = state("my-counter", 0)
#counter.update(x => x + 1)
#context counter.get()
```

### Color Manipulation

```typst
#let base = rgb("#3366ff")
base.lighten(40%)   base.darken(20%)
base.transparentize(50%)   red.mix(blue, 30%)
```

### Method Chaining

```typst
#items.map(x => x * 2).filter(x => x > 5).join(", ")
```

## Safe Patterns

### Blank Fields

```typst
// CORRECT                         // WRONG
[......%]                          [_____%]  // underscores trigger emphasis
Answer: ____________
```

### Currency

```typst
[\$5,000]          // escaped dollar
£10,000            // pound OK
EUR 5,000          // text alternative
// WRONG: [$5,000] — starts math mode
```

### Expression Chaining

After `#expr`, Typst greedily checks for `(`, `[`, `.` to chain. When followed by literal `(` that should be text, insert `~`:

```typst
// WRONG — Typst parses ( as calling h(1em)
#h(1em)("eps_revision_net", True),   // error: unknown variable: True

// CORRECT — ~ breaks the chain
#h(1em)~("eps_revision_net", True),  // works

// CORRECT — raw() is a separate #expr
#h(1em)#raw("(\"key\", True),")
```

**Rule:** When `#func()` is followed by literal `(` or `[` that should be text, insert `~` between them.

## Quick Syntax Cheatsheet

```typst
#set page(margin: 1.5cm, paper: "a4")
#set text(font: "New Computer Modern", size: 10pt)

= Level 1                         // Headings
== Level 2
=== Level 3

*bold*  _italic_  `code`  #underline[underlined]

#text(fill: rgb("#ff0000"))[Red text]
#rect(fill: blue.lighten(80%), inset: 10pt)[Box]

#grid(columns: (1fr, 1fr), gutter: 1em, [Col 1], [Col 2])
#v(1em)        // Vertical space
#h(1fr)        // Flexible horizontal space (push right)
#pagebreak()   // New page

- Bullet item              + Numbered item
  - Nested                 + Another

$E = m c^2$                       // Inline math
$ integral_0^infinity f(x) $      // Display math
```
