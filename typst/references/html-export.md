# HTML Export in Typst

HTML export is an experimental feature introduced in Typst 0.13. Unlike PDF export which produces visual output, HTML export focuses on semantic structure.

## Enabling HTML Export

HTML export requires a feature flag:

```bash
# Via environment variable
TYPST_FEATURES=html typst compile document.typ output.html

# Via CLI flag
typst compile document.typ output.html --features html

# Watch mode
TYPST_FEATURES=html typst watch document.typ output.html
```

**Note:** HTML export is not yet available in the Typst web app.

## Current Limitations

As of Typst 0.14, HTML export is still experimental:
- Single HTML file output only (multi-file and asset directories planned)
- No automatic CSS stylesheet generation
- Not all built-in elements have semantic HTML mappings
- Incomplete feature set under active development

## The `target()` Function

The `target()` function returns the current export target, enabling conditional rendering:

```typst
#context {
  if target() == "html" {
    // HTML-specific rendering
  } else {
    // PDF/PNG/SVG rendering (paged output)
  }
}
```

**Return values:**
- `"html"` - When exporting to HTML
- `"paged"` - When exporting to PDF, PNG, or SVG

### Why target() is Contextual

The target can change within a single compilation. When using `html.frame` to embed paged content in HTML, the target becomes `"paged"` within that frame:

```typst
// In HTML export
#context target()  // Returns "html"

#html.frame[
  #context target()  // Returns "paged" (inside frame)
]
```

## HTML-Specific Functions

Typst provides functions for generating custom HTML:

### html.elem

Create arbitrary HTML elements:

```typst
// Basic element
#html.elem("kbd")[Ctrl+C]
// Produces: <kbd>Ctrl+C</kbd>

// With attributes
#html.elem("a", attrs: (href: "https://typst.app"))[Typst]
// Produces: <a href="https://typst.app">Typst</a>

// Void elements
#html.elem("br")
// Produces: <br>
```

### html.frame

Embed paged layout content as inline SVG:

```typst
// Complex layout that needs precise positioning
#html.frame[
  #box(
    width: 100pt,
    height: 100pt,
    fill: gradient.radial(red, blue),
  )
]
```

Use `html.frame` for:
- Complex visual layouts
- Precise positioning
- Content that can't be represented semantically

### html.typed (0.14)

Strongly-typed HTML element construction:

```typst
// Using typed interface for better safety
#html.typed.a(href: "https://typst.app")[Typst Website]
```

## Creating Portable Templates

Design templates that work for both PDF and HTML:

```typst
// Portable keyboard shortcut styling
#let kbd(body) = context {
  if target() == "html" {
    html.elem("kbd", body)
  } else {
    box(
      fill: luma(240),
      stroke: luma(180) + 0.5pt,
      inset: (x: 4pt, y: 2pt),
      radius: 2pt,
      text(font: "monospace", body)
    )
  }
}

// Usage - works in both HTML and PDF
Press #kbd[Ctrl] + #kbd[S] to save.
```

### More Examples

```typst
// Callout box
#let callout(title, body, kind: "note") = context {
  if target() == "html" {
    html.elem("aside", attrs: (class: "callout callout-" + kind))[
      #html.elem("strong")[#title]
      #body
    ]
  } else {
    box(
      width: 100%,
      fill: if kind == "warning" { yellow.lighten(80%) } else { blue.lighten(90%) },
      inset: 10pt,
      radius: 4pt,
      [*#title* \ #body]
    )
  }
}

// Code block with language
#let code-block(lang, code) = context {
  if target() == "html" {
    html.elem("pre")[
      #html.elem("code", attrs: (class: "language-" + lang))[#code]
    ]
  } else {
    block(
      fill: luma(245),
      inset: 10pt,
      radius: 4pt,
      width: 100%,
      raw(code, lang: lang)
    )
  }
}
```

## Semantic HTML Mapping

Typst automatically maps some elements to semantic HTML:

| Typst Element | HTML Output |
|---------------|-------------|
| `= Heading` | `<h1>`, `<h2>`, etc. |
| `- List item` | `<ul><li>` |
| `+ Enum item` | `<ol><li>` |
| `*emphasis*` | `<em>` |
| `_strong_` | `<strong>` |
| `#link()` | `<a>` |
| `#figure()` | `<figure>` |
| `#table()` | `<table>` |
| `#raw()` | `<pre><code>` |

## Best Practices

### 1. Test Both Outputs

Always verify your document works in both PDF and HTML:

```bash
# PDF
typst compile document.typ output.pdf

# HTML
TYPST_FEATURES=html typst compile document.typ output.html
```

### 2. Use Semantic Markup

Prefer semantic Typst elements over visual styling:

```typst
// Good - maps to semantic HTML
= Chapter Title
== Section

// Bad - loses semantics in HTML
#text(size: 24pt, weight: "bold")[Chapter Title]
```

### 3. Provide Fallbacks

For complex visual content, provide HTML alternatives:

```typst
#let diagram(..args) = context {
  if target() == "html" {
    // Simplified HTML version or description
    [Diagram: ...]
  } else {
    // Full visual diagram for PDF
    cetz.canvas(...)
  }
}
```

### 4. Consider Accessibility

HTML has better accessibility potential than PDF. Use semantic elements and ARIA attributes:

```typst
#let accessible-nav(items) = context {
  if target() == "html" {
    html.elem("nav", attrs: (role: "navigation", "aria-label": "Main"))[
      #for item in items {
        html.elem("a", attrs: (href: item.href))[#item.label]
      }
    ]
  } else {
    // PDF version
    ...
  }
}
```

## Future Development

HTML export is under active development. Expected improvements:
- Multi-file output with proper asset directories
- Automatic CSS generation
- More complete semantic HTML mappings
- Better integration with web frameworks
- Available in Typst web app

Check the [Typst changelog](https://typst.app/docs/changelog/) for updates.
