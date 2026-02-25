# Visual Verification for Typst Documents

> Compilation success (exit code 0) does NOT guarantee visual quality.
> Always spot-check rendered output after compilation.

---

## Approach

Typst compiles directly to PNG — no external tools needed:

```bash
# Single page
typst compile doc.typ /tmp/preview.png --pages 1

# All pages as numbered PNGs
typst compile doc.typ /tmp/preview-{0p}.png

# Specific page range
typst compile doc.typ /tmp/preview-{0p}.png --pages 3-5
```

Use the `Read` tool on PNG files to visually inspect rendered pages. Claude is multimodal and can detect layout issues by looking at the rendered output.

---

## Sampling Strategy

Not every page needs checking. Sample based on document type:

| Document Type | Pages to Check | Rationale |
|---------------|---------------|-----------|
| Documents (>3 pages) | Page 1, middle page, last page | Title page, body content, ending |
| Documents (<=3 pages) | All pages | Small enough to check everything |
| Presentations (<30 slides) | All slides | Each slide is a distinct layout |
| Presentations (30+ slides) | First 3, middle 3, last 3, + any flagged | Representative sample |

---

## Visual Checklist

When inspecting rendered PNGs, check for:

### Layout Issues
- [ ] **Content overflow** — text or figures cut off at page edges
- [ ] **Blank half-pages** — unintentional whitespace (usually from `pagebreak()` or large figures)
- [ ] **Cramped text** — content that needs more breathing room
- [ ] **Unbalanced columns** — one column much longer than the other

### Typography
- [ ] **Font rendering** — correct fonts loaded (check for fallback squares)
- [ ] **Heading hierarchy** — visual distinction between heading levels
- [ ] **Text size consistency** — no unexpected tiny or huge text

### Figures & Tables
- [ ] **Missing images** — blank spaces where images should be
- [ ] **Table alignment** — columns properly aligned, not overflowing
- [ ] **Figure placement** — figures near their references, not floating to odd locations
- [ ] **Chart readability** — labels and legends visible

### Presentation-Specific
- [ ] **Slide content density** — not too much text per slide
- [ ] **Callout box count** — max 2 per slide
- [ ] **Title consistency** — uniform title styling across slides
- [ ] **Footer/header presence** — institutional info visible where expected

---

## Structural Validation

For deeper structural checks, use `typst query`:

```bash
# Count headings
typst query doc.typ "heading"

# Count figures
typst query doc.typ "figure"

# Check page count
typst query doc.typ "page" --field "body"
```

---

## Integration Points

- **`/compile` skill:** After successful compilation, render sample pages to PNG and spot-check
- **Verifier agent:** Add visual verification step after compilation pass
- **`/finish` skill:** Re-render affected pages after each fix round
- **typst-reviewer agent:** Can request visual verification for flagged sections
