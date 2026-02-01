# Accessibility in Typst

Starting with Typst 0.14, documents are accessible by default with tagged PDFs. This guide covers best practices for creating universally accessible documents.

## Core Principles

**Universal Access** means designing documents that work for the broadest possible range of people and situations, including:
- People using screen readers
- People with color vision differences
- People with low vision
- People using different devices or preferences

## Tagged PDFs (Default in 0.14+)

Typst automatically produces tagged PDFs, which include rich metadata that assistive technologies use to make documents accessible.

**To disable tagging (NOT recommended):**
```bash
typst compile document.typ --no-pdf-tags
```

## PDF Standards

### PDF/UA-1 (Universal Accessibility)

The strictest accessibility standard. Use for:
- Government documents
- EU compliance (European Accessibility Act)
- US ADA compliance

```bash
typst compile document.typ --pdf-standard ua-1
```

**Requirements for PDF/UA-1:**
- Document must have a title (`#set document(title: ...)`)
- All images and figures must have alt text
- Documents with 21+ pages must have outlined headings
- Math content should have textual alternatives

### PDF/A (Archival with Accessibility)

PDF/A standards include accessibility at certain conformance levels:

```bash
# Level A conformance includes accessibility
typst compile document.typ --pdf-standard a-2a

# Level B is archival-only (less accessibility)
typst compile document.typ --pdf-standard a-2b
```

### Combining Standards

```bash
typst compile document.typ --pdf-standard 1.7,ua-1
```

## Document Metadata

Always set document metadata for accessibility:

```typst
#set document(
  title: "Your Document Title",  // Required for PDF/UA
  author: "Author Name",
  keywords: ("topic1", "topic2"),
)

// Set language for screen readers
#set text(lang: "en")  // ISO 639-1 code

// With regional variant
#set text(lang: "en", region: "GB")  // ISO 3166-1 alpha-2
```

## Alternative Text

### Images

Always provide alt text for images:

```typst
#image("chart.png", alt: "Bar chart showing quarterly revenue increasing from $10M to $15M")
```

**Alt text guidelines:**
- Describe what's visible, not metadata
- Be specific but concise
- Avoid "Image of..." - redundant
- Match effort to visual complexity

**Examples:**

| Bad | Good |
|-----|------|
| "Chart" | "Line graph showing temperature rising from 20°C to 35°C over 24 hours" |
| "Image of a bird" | "Red cardinal perched on oak branch" |
| "Logo" | "Acme Corp logo" (or mark as artifact if purely decorative) |

### Figures

Use `figure.alt` when the figure content and caption form a semantic unit:

```typst
// Simple image in figure - use image alt
#figure(
  image("photo.jpg", alt: "Sunset over mountains"),
  caption: [Mountain vista at dusk],
)

// Complex composed figure - use figure alt
#figure(
  stack(
    dir: ltr,
    spacing: 1em,
    rect(fill: blue)[Input],
    text(2em, sym.arrow),
    rect(fill: green)[Process],
    text(2em, sym.arrow),
    rect(fill: red)[Output],
  ),
  alt: "Flow diagram showing three stages: Input leads to Process leads to Output",
  caption: [Data processing pipeline],
)
```

### Math

Provide spoken descriptions for complex formulas:

```typst
// Simple math - screen readers can often handle
$x^2 + y^2 = r^2$

// Complex formulas - add description in context
The quadratic formula
$ x = (-b plus.minus sqrt(b^2 - 4 a c)) / (2a) $
gives the solutions where $a$ is the coefficient of $x^2$,
$b$ is the coefficient of $x$, and $c$ is the constant.
```

## Semantic Structure

### Use Semantic Elements

Use proper markup instead of visual styling:

```typst
// Good - semantic
= Heading 1
== Heading 2
*emphasis* and *strong*

// Bad - visual only
#text(size: 24pt, weight: "bold")[Heading 1]
```

### Heading Hierarchy

Don't skip heading levels:

```typst
// Good
= Chapter
== Section
=== Subsection

// Bad - skips level 2
= Chapter
=== Subsection
```

### Lists and Tables

Use built-in elements:

```typst
// Good - semantic list
- Item one
- Item two
- Item three

// Bad - fake list
#[• Item one\
• Item two\
• Item three]

// Good - semantic table
#table(
  columns: 2,
  [Name], [Value],
  [Alpha], [1],
  [Beta], [2],
)

// Bad - grid for tabular data
#grid(...)
```

## Reading Order

Content should follow logical reading order in source, regardless of visual layout:

```typst
// Place floating figures where they make sense logically
This is the introduction paragraph.

#figure(
  image("diagram.png", alt: "System architecture"),
  caption: [System Architecture],
  placement: top,  // Floats to top visually
)

The figure above shows...  // Reference comes after figure in source
```

## Decorative Content

Mark purely decorative elements as artifacts:

```typst
// Decorative background - mark as artifact
#pdf.artifact(
  place(
    dx: -1cm, dy: -1cm,
    rect(fill: blue.lighten(95%), width: 100% + 2cm, height: 100% + 2cm)
  )
)

// Page headers/footers are automatically artifacts
#set page(
  header: [Document Title],
  footer: context [Page #counter(page).display()],
)
```

## Color and Contrast

### WCAG Contrast Requirements

| Text Type | AA Level | AAA Level |
|-----------|----------|-----------|
| Large (≥18pt or bold ≥14pt) | 3:1 | 4.5:1 |
| Normal text | 4.5:1 | 7:1 |

### Don't Rely on Color Alone

```typst
// Bad - color only
#text(fill: red)[Error: Invalid input]

// Good - color + text
#text(fill: red)[Error: Invalid input ✗]

// Good - color + pattern in charts
// Use different line styles, markers, or patterns
```

## Links

Use descriptive link text:

```typst
// Good
See the #link("https://typst.app/docs")[Typst documentation] for details.

// Bad
Click #link("https://typst.app/docs")[here] for details.
```

## Testing Accessibility

### Automated Tools

- **veraPDF**: Validates PDF/A and PDF/UA compliance
  ```bash
  verapdf --flavour ua1 document.pdf
  ```

- **PDF Accessibility Checker (PAC)**: Windows tool for PDF/UA and WCAG
- **Adobe Acrobat Pro**: Built-in accessibility checker

### Manual Testing

Test with actual screen readers:

| Platform | Screen Reader | PDF Reader |
|----------|---------------|------------|
| Windows | NVDA | Adobe Acrobat |
| macOS | VoiceOver | Preview or Acrobat |
| Linux | Orca | Evince or Acrobat |

### Testing Checklist

- [ ] Document has title set
- [ ] Language is specified
- [ ] All images have alt text
- [ ] Headings follow proper hierarchy
- [ ] Tables use semantic markup
- [ ] Color contrast meets WCAG AA
- [ ] Links have descriptive text
- [ ] PDF validates against PDF/UA-1

## HTML Export Considerations

When exporting to HTML (experimental), accessibility is often better than PDF:

```bash
TYPST_FEATURES=html typst compile document.typ output.html
```

HTML advantages:
- Native semantic elements
- Better screen reader support
- Responsive to user preferences
- Reflowable text

Consider distributing HTML alongside PDF for maximum accessibility.

## Quick Reference

```typst
// Minimal accessible document setup
#set document(title: "Document Title", author: "Author")
#set text(lang: "en")

// Image with alt
#image("photo.jpg", alt: "Description of image content")

// Figure with alt (for composed content)
#figure(
  ...,
  alt: "Description of figure content",
  caption: [...],
)

// Compile with PDF/UA
// typst compile doc.typ --pdf-standard ua-1
```
