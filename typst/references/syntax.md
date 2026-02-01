# Typst Syntax Reference

## Critical Syntax Distinctions

### Data Structures

- **Arrays**: Use `()` parentheses
  ```typst
  #let colors = (red, blue, green)
  #let mixed = (1, "text", true)
  #let singleton = (item,)  // trailing comma for single-element array
  ```

- **Dictionaries**: Use `()` with key-value pairs
  ```typst
  #let config = (name: "value", count: 5)
  #let palette = (primary: red, secondary: blue)
  ```

- **Content blocks**: Use `[]` square brackets
  ```typst
  #let heading = [== My Title]
  #let paragraph = [This is some *bold* text]
  ```

**IMPORTANT**: Typst does NOT have tuples. Only arrays (with parentheses).

### Function Definitions

```typst
// Basic function
#let greet(name) = [Hello, #name!]

// With default parameters
#let box-style(fill: none, stroke: 1pt) = { ... }

// With variadic arguments
#let items(..args) = {
  for item in args.pos() { ... }
}
```

### Conditionals and Loops

```typst
// If-else
#if condition {
  [true branch]
} else {
  [false branch]
}

// For loop
#for item in array {
  [Processing #item]
}
```

### String Interpolation

```typst
#let name = "World"
[Hello #name]  // Content context
#("Hello " + name)  // String concatenation
```

## New in Typst 0.13-0.14

### Curve Function (0.13)

The `curve` function replaces `path` for drawing Bézier curves. It provides a simpler, SVG-inspired interface.

```typst
// Basic curve with line segments
#curve(
  stroke: 2pt + blue,
  curve.move((0pt, 0pt)),
  curve.line((50pt, 0pt)),
  curve.line((50pt, 50pt)),
  curve.close(),
)

// Quadratic Bézier curve
#curve(
  stroke: 2pt + red,
  curve.move((0pt, 50pt)),
  curve.quad((25pt, 0pt), (50pt, 50pt)),  // control point, end point
)

// Cubic Bézier curve
#curve(
  stroke: 2pt + green,
  curve.move((0pt, 25pt)),
  curve.cubic(
    (10pt, 0pt),   // control-start
    (40pt, 50pt),  // control-end
    (50pt, 25pt),  // end point
  ),
)

// Smooth continuation with auto control
#curve(
  stroke: 1pt,
  curve.move((0pt, 0pt)),
  curve.cubic((0pt, 20pt), (30pt, 20pt), (30pt, 0pt)),
  curve.cubic(auto, (60pt, -20pt), (60pt, 0pt)),  // auto mirrors previous control
)
```

**Curve segment types:**
- `curve.move(point)` - Move without drawing
- `curve.line(point)` - Straight line
- `curve.quad(control, end)` - Quadratic Bézier
- `curve.cubic(control-start, control-end, end)` - Cubic Bézier
- `curve.close(mode: "smooth" | "straight")` - Close path

**Fill rules:**
- `"non-zero"` - Uses signed edge crossing sums (default)
- `"even-odd"` - Counts edge crossings as odd/even

### First-Line Indent (0.13)

First-line indent now works on all paragraphs:

```typst
#set par(
  first-line-indent: 1em,
  hanging-indent: 0pt,
)

// Enable for ALL paragraphs (not just consecutive ones)
#show par: set par(first-line-indent: 1em)
```

### Character-Level Justification (0.14)

Fine-tune paragraph justification with character spacing:

```typst
// Enable character-level justification
#set par(
  justify: true,
  justification-limits: (
    min: -0.02em,  // Slightly compress characters
    max: 0.02em,   // Slightly expand characters
  ),
)
```

This improves visual balance in justified text without excessive word spacing.

### Figure Alt Text (0.14)

Add alternative descriptions for accessibility:

```typst
// Image with alt text
#image("chart.png", alt: "Bar chart showing quarterly sales")

// Figure with alt text (for complex composed figures)
#figure(
  stack(dir: ltr, rect[A], sym.arrow, rect[B]),
  alt: "Diagram showing A leads to B",
  caption: [Process Flow],
)
```

**When to use which:**
- `image(alt: ...)` - Describe the image content
- `figure(alt: ...)` - Describe composed figures where image+caption form a unit

### PDF Attachments (0.14)

Attach files to PDFs (replaces deprecated `pdf.embed`):

```typst
// Attach a file to the PDF
#pdf.attach(
  "data.xml",
  read("invoice-data.xml", encoding: none),
  mime-type: "application/xml",
  description: "Machine-readable invoice data",
)
```

### Bytes Handling (0.13)

Functions now accept raw bytes directly:

```typst
// Read file as bytes
#let data = read("image.png", encoding: none)

// Use bytes directly with image
#image(data, format: "png")

// Raw pixel data for scientific visualizations
#image(
  bytes((255, 0, 0, 0, 255, 0, 0, 0, 255)),  // RGB pixels
  format: (
    encoding: "rgb",
    width: 3,
    height: 1,
  ),
)
```

### Target Function (0.13)

Conditional rendering for HTML vs PDF export:

```typst
// Check current export target
#context {
  if target() == "html" {
    html.elem("kbd")[Ctrl+C]
  } else {
    box(
      fill: gray.lighten(80%),
      inset: 3pt,
      radius: 2pt,
      [Ctrl+C]
    )
  }
}

// Reusable pattern for templates
#let kbd(body) = context {
  if target() == "html" {
    html.elem("kbd", body)
  } else {
    box(fill: luma(240), inset: (x: 4pt, y: 2pt), radius: 2pt, body)
  }
}
```

**Note:** `target()` is contextual and requires the `html` feature flag.

### Outline Improvements (0.13)

Enhanced table of contents:

```typst
// Auto-indented outline
#outline(
  title: "Contents",
  indent: auto,  // Automatic indentation
)

// Custom indent per level
#outline(
  indent: n => 2em * n,
)

// Custom entry formatting
#show outline.entry: it => {
  if it.level == 1 {
    strong(it)
  } else {
    it
  }
}
```

## Common Patterns

### Custom Styling Functions

```typst
#let highlight(color, body) = {
  box(fill: color.lighten(80%), inset: 3pt, body)
}

#highlight(red)[Important text]
```

### State Management

```typst
#let counter = state("my-counter", 0)

#counter.update(x => x + 1)

#context counter.get()
```

### Layout Helpers

```typst
// Stack (vertical by default)
#stack(
  spacing: 1em,
  [First item],
  [Second item]
)

// Grid
#grid(
  columns: (1fr, 2fr),
  rows: auto,
  gutter: 10pt,
  [Cell 1], [Cell 2]
)

// Box with styling
#box(
  fill: gray.lighten(90%),
  stroke: 1pt,
  inset: 8pt,
  radius: 4pt,
  [Content]
)
```

### Color Manipulation

```typst
#let base = rgb("#3366ff")
#let lighter = base.lighten(40%)
#let darker = base.darken(20%)
#let transparent = base.transparentize(50%)
#let mixed = red.mix(blue, 30%)
```

### Symbol with Grapheme Clusters (0.14)

Create symbols from full grapheme clusters:

```typst
// Single character symbol
#let check = symbol("✓")

// Grapheme cluster (e.g., emoji with modifier)
#let thumbs = symbol("👍🏽")
```

## Common Gotchas

1. **Array access**: Use `.at()` method, not `[]`
   ```typst
   #let arr = (1, 2, 3)
   #arr.at(0)  // Correct
   // arr[0]   // WRONG - [] is for content
   ```

2. **Method chaining on arrays**:
   ```typst
   #items.map(x => x * 2).filter(x => x > 5).join(", ")
   ```

3. **Context blocks**: Required for accessing state and contextual functions
   ```typst
   #context {
     let val = my-state.get()
     [The value is #val]
   }
   ```

4. **Assignment in code blocks**: Use `let`, not `=` alone
   ```typst
   #{
     let x = 5  // Correct
     // x = 5   // WRONG
   }
   ```

5. **Deprecated functions**:
   - ❌ `path` → Use `curve` instead
   - ❌ `pdf.embed` → Use `pdf.attach` instead
   - ❌ `image.decode` → Pass bytes directly to `image`

6. **Math mode strings**: Single-letter strings are now upright
   ```typst
   $"a"$  // Upright "a" (correct in 0.13+)
   $a$    // Italic a (variable)
   ```
