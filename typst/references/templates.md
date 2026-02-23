# Document Templates

> For multi-file projects (500+ lines), extract shared helpers to `lib.typ` and
> use `#import "lib.typ": *` in each content file. Keep a `main.typ` as entry
> point with `#include` for each section.

---

## 1. Research Report
**Use when:** "analysis", "research", "review", "sector", "evaluation" | **Skip when:** <2 pages, slides, CVs

```typst
#set page(margin: (x: 1.5cm, y: 1.5cm), paper: "a4", numbering: "1 / 1")
#set text(font: "New Computer Modern", size: 9.5pt)
#set par(leading: 0.55em, spacing: 0.65em, justify: true)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(above: 0.6em, below: 0.5em, text(size: 16pt, weight: "bold", fill: rgb("#1a237e"), it.body))
  line(length: 100%, stroke: 0.8pt + rgb("#1a237e"))
  v(0.3em)
}
#show heading.where(level: 2): it => {
  block(above: 0.8em, below: 0.4em, text(size: 12pt, weight: "bold", fill: rgb("#283593"), it.body))
}
#show heading.where(level: 3): it => {
  block(above: 0.6em, below: 0.3em, text(size: 10.5pt, weight: "bold", fill: rgb("#37474f"), it.body))
}
```

---

## 2. Presentation (16:9)
**Use when:** "slides", "presentation", "deck", "pitch" | **Skip when:** text-heavy docs, reports, essays

```typst
#let navy  = rgb("#1B365D")
#let gold  = rgb("#B8860B")
#let teal  = rgb("#2A9D8F")
#let lgray = rgb("#F5F5F5")
#let dtext = rgb("#2C2C2C")

#set page(width: 254mm, height: 142.9mm, margin: (x: 12mm, y: 8mm), fill: lgray, footer: none)
#set text(font: "New Computer Modern", size: 9pt, fill: dtext)
#set par(leading: 0.55em)

#let slide-header(title, slide-num: none) = {
  place(top + left, dx: -12mm, dy: -8mm, rect(width: 254mm, height: 3mm, fill: navy))
  v(2mm)
  text(size: 16pt, weight: "bold", fill: navy, title)
  v(2mm)
  if slide-num != none {
    place(bottom + right, text(size: 6pt, fill: navy.lighten(30%), [Slide #slide-num]))
  }
  place(bottom + left, text(size: 5.5pt, fill: navy.lighten(40%), tracking: 1pt, [CONFIDENTIAL]))
}
#let kv(key, val) = grid(columns: (1fr, 1fr), gutter: 2pt,
  text(weight: "bold", size: 7.5pt, fill: navy, key), text(size: 7.5pt, val))
```

---

## 3. CV / Résumé
**Use when:** "resume", "CV", "job application" | **Skip when:** multi-page docs, reports, essays

```typst
#let cv-primary = rgb("#1a365d")
#let cv-accent  = rgb("#2c5282")
#let cv-light   = rgb("#ebf4ff")

#set page(paper: "a4", margin: (x: 1.4cm, y: 1.2cm), numbering: none)
#set text(font: "New Computer Modern", size: 9pt, fill: rgb("#2d3748"))
#set par(leading: 0.5em, spacing: 0.55em)
#show heading.where(level: 1): it => {
  v(0.4em)
  block(below: 0.3em)[
    #text(size: 11pt, weight: "bold", fill: cv-primary, it.body)
    #v(-2pt)
    #line(length: 100%, stroke: 1pt + cv-accent)
  ]
}
#show heading.where(level: 2): it => {
  block(above: 0.3em, below: 0.2em, text(size: 9.5pt, weight: "bold", fill: cv-accent, it.body))
}
#let cv-entry(title, org, dates, body) = {
  grid(columns: (1fr, auto),
    text(weight: "bold", size: 9pt)[#title],
    text(size: 8pt, fill: rgb("#718096"))[#dates])
  text(size: 8.5pt, style: "italic", fill: cv-accent)[#org]
  v(2pt); set text(size: 8.5pt); body; v(4pt)
}
#let skill-tag(label) = box(fill: cv-light, inset: (x: 5pt, y: 2pt), radius: 3pt,
  text(size: 7.5pt, fill: cv-primary, label))
```

---

## 4. Annotated Reference
**Use when:** "reference", "taxonomy", "glossary", "compliance", "documentation" | **Skip when:** short docs, presentations, CVs

```typst
#set page(margin: (x: 2.5cm, y: 2.5cm), numbering: "1")
#set text(font: "New Computer Modern", size: 10.5pt)
#set par(leading: 0.7em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  v(0.8em); line(length: 100%, stroke: 1pt + rgb("#1e3a5f")); v(0.3em)
  text(size: 14pt, weight: "bold", fill: rgb("#1e3a5f"))[#it]; v(0.3em)
}
#show heading.where(level: 2): it => {
  v(0.5em); text(size: 12pt, weight: "bold", fill: rgb("#2563eb"))[#it]; v(0.2em)
}
#show heading.where(level: 3): it => {
  v(0.3em); text(size: 10.5pt, weight: "bold")[#it]; v(0.1em)
}
// Callout box factory
#let _box(title, fg, bg, border, body) = block(width: 100%, inset: 10pt, radius: 3pt,
  fill: bg, stroke: 0.5pt + border)[
  #text(size: 9pt, weight: "bold", fill: fg)[#title] #v(0.2em) #text(size: 9pt)[#body]
]
#let concept(term, def) = { text(weight: "bold")[#term] + [ --- ] + def; v(0.15em) }
#let sidebar(title, body)  = _box(title, rgb("#1e3a5f"), rgb("#f0f4ff"), rgb("#2563eb"), body)
#let keyclause(num, title, body) = _box([Section #num: #title], rgb("#1e3a5f"), rgb("#f8f9fa"), rgb("#6b7280"), body)
#let negotiation(body)     = _box("Negotiation Point", rgb("#991b1b"), rgb("#fef2f2"), rgb("#dc2626"), body)
#let takeaway(body)        = _box("Key Takeaways", rgb("#004d40"), rgb("#e0f2f1"), rgb("#00897b"), body)
#let crossref(body)        = _box("Cross-Reference", rgb("#4a148c"), rgb("#f3e5f5"), rgb("#7b1fa2"), body)
```

---

## 5. Essay
**Use when:** "essay", "thesis", "paper", "long-form" | **Skip when:** short docs, slides, data-heavy reports

```typst
#set page(paper: "a4", margin: (x: 2.5cm, y: 3cm),
  header: context {
    if counter(page).get().first() > 2 [
      #set text(9pt, fill: gray.darken(20%))
      #emph[Document Title] #h(1fr) Author Name
      #v(2pt)
      #line(length: 100%, stroke: 0.4pt + gray)
    ]
  },
  footer: context {
    set align(center); set text(9pt, fill: gray.darken(20%))
    counter(page).display("— 1 —")
  },
)
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.7em, first-line-indent: 1.5em)
#set footnote.entry(separator: line(length: 30%, stroke: 0.5pt + gray))
#show heading.where(level: 1): it => {
  set par(first-line-indent: 0em); pagebreak(weak: true); v(1em)
  text(size: 20pt, weight: "bold", fill: rgb("#1a365d"))[#it.body]; v(0.3em)
}
#show heading.where(level: 2): it => {
  set par(first-line-indent: 0em); v(1.2em)
  text(size: 14pt, weight: "bold", fill: rgb("#2c5282"))[#it.body]; v(0.5em)
}
#show heading.where(level: 3): it => {
  set par(first-line-indent: 0em); v(1em)
  text(size: 12pt, weight: "bold", fill: rgb("#4a5568"))[#it.body]; v(0.3em)
}
#let blockquote(body) = {
  set par(first-line-indent: 0em)
  block(inset: (left: 2em, right: 1em, y: 0.8em),
    stroke: (left: 3pt + rgb("#3182ce").lighten(60%)), fill: rgb("#f7fafc"), body)
}
```

---

## 6. Business Report
**Use when:** "report", "brief", "visit prep", "client", "branded" | **Skip when:** academic papers, slides, CVs

```typst
#let brand-primary = rgb("#0033a0")
#let brand-dark    = rgb("#001a4e")
#let brand-light   = rgb("#e8eef8")
#let brand-gold    = rgb("#c5a247")
#let brand-grey    = rgb("#f7f8fa")
#let brand-green   = rgb("#1a7a3a")
#let brand-red     = rgb("#c0392b")

#set page(margin: (x: 1.8cm, y: 2cm), footer: context {
  let pg = counter(page).get().first()
  if pg > 1 {
    line(length: 100%, stroke: 0.3pt + rgb("#ccc")); v(4pt)
    grid(columns: (1fr, auto, 1fr),
      align(left, text(8pt, fill: rgb("#999"))[Report Title]),
      align(center, text(8pt, fill: rgb("#999"))[— #pg —]),
      align(right, text(8pt, fill: rgb("#999"))[Date]))
  }
})
#set text(font: "Georgia", size: 10pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  v(10pt)
  block(width: 100%)[
    #block(fill: brand-primary, inset: (x: 12pt, y: 8pt), radius: (top: 4pt),
      width: 100%, text(fill: white, weight: "bold", size: 13pt, it.body))
    #block(fill: brand-light, inset: 0pt, width: 100%, height: 2pt)
  ]
  v(6pt)
}
#show heading.where(level: 2): it => {
  v(6pt)
  block[#text(fill: brand-primary, weight: "bold", size: 11pt)[#it.body]
    #v(-2pt) #line(length: 40%, stroke: 1pt + brand-gold)]
  v(4pt)
}
#let tip-box(body) = block(fill: rgb("#fff8e1"), stroke: (left: 3pt + brand-gold),
  inset: 10pt, radius: (right: 4pt), width: 100%)[#text(size: 9.5pt)[#body]]
#let insight-box(body) = block(fill: brand-light, stroke: (left: 3pt + brand-primary),
  inset: 10pt, radius: (right: 4pt), width: 100%)[#text(size: 9.5pt)[#body]]
#let warn-box(body) = block(fill: rgb("#fdecea"), stroke: (left: 3pt + brand-red),
  inset: 10pt, radius: (right: 4pt), width: 100%)[#text(size: 9.5pt)[#body]]
#let stat-card(value, label) = block(fill: brand-grey, inset: (x: 10pt, y: 8pt),
  radius: 4pt, width: 100%, align(center)[
    #text(size: 16pt, weight: "bold", fill: brand-primary)[#value]
    #v(2pt) #text(size: 8pt, fill: rgb("#666"))[#label]
  ])
#let styled-table(..args) = {
  set table(
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + brand-primary) }
      else { (bottom: 0.5pt + rgb("#e0e0e0")) },
    inset: 8pt,
    fill: (x, y) => if y == 0 { brand-dark } else if calc.odd(y) { brand-grey } else { white })
  show table.cell.where(y: 0): set text(fill: white, weight: "bold", size: 9pt)
  table(..args)
}
```

---

## 7. Study Guide
**Use when:** "study guide", "revision", "cheatsheet", "exam", "formula sheet" | **Skip when:** formal papers, client docs, slides

```typst
#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(font: "Inter", size: 8.5pt, fill: rgb("#78909c"))
      Study Guide Title #h(1fr) #counter(page).display()
      #v(4pt) #line(length: 100%, stroke: 0.4pt + rgb("#b0bec5"))
    ]
  },
  footer: context {
    if counter(page).get().first() > 1 [
      #line(length: 100%, stroke: 0.4pt + rgb("#b0bec5"))
      #v(4pt) #set text(size: 8pt, fill: rgb("#b0bec5"))
      #align(center)[Course Name]
    ]
  },
)
#set text(font: ("Libertinus Serif", "Charter", "Georgia"), size: 11pt)
#set heading(numbering: "1.1")
#set par(justify: true, leading: 0.7em, spacing: 0.85em)
#show math.equation: set text(font: "New Computer Modern Math")
#show raw: set text(font: "Fira Code", size: 9.5pt)
#set list(marker: (
  text(fill: rgb("#1565c0"), size: 7pt, "●"),
  text(fill: rgb("#78909c"), size: 6pt, "●"),
  text(fill: rgb("#b0bec5"), size: 5pt, "●"),
), spacing: 0.65em)
#show heading.where(level: 1): it => {
  set text(font: "Inter", size: 18pt, weight: "bold", fill: rgb("#0d47a1"))
  block(above: 2em, below: 0.8em)[
    #block(width: 100%, inset: (bottom: 8pt), stroke: (bottom: 2.5pt + rgb("#1565c0")))[#it]]
}
#show heading.where(level: 2): it => {
  set text(font: "Inter", size: 14pt, weight: "bold", fill: rgb("#1565c0"))
  block(above: 1.5em, below: 0.8em, inset: (left: 10pt), stroke: (left: 3pt + rgb("#1565c0")))[#it]
}
#show heading.where(level: 3): it => {
  set text(font: "Inter", size: 12pt, weight: "semibold", fill: rgb("#1976d2"))
  block(above: 1.2em, below: 0.6em)[#it]
}
#set table(stroke: 0.5pt + rgb("#cfd8dc"))
#show table.cell.where(y: 0): set text(fill: white, weight: "bold", size: 10pt)

#let infobox(title: "", icon: none, color: rgb("#e3f2fd"), accent: none, body) = {
  let c = if accent != none { accent } else { color.darken(40%) }
  block(width: 100%, inset: (x: 14pt, y: 12pt), radius: 6pt, fill: color,
    stroke: (left: 4pt + c, rest: 0.5pt + color.darken(15%)), above: 1em, below: 1em)[
    #if title != "" [
      #text(font: "Inter", weight: "bold", size: 10.5pt, fill: c)[
        #if icon != none [#icon ] #upper(title)] #v(0.4em)]
    #set text(size: 10.5pt); #body]
}
#let keypoint(body) = infobox(title: "Key Point", icon: sym.diamond.filled, color: rgb("#e8f5e9"), accent: rgb("#2e7d32"), body)
#let warning(body)  = infobox(title: "Warning", icon: sym.excl, color: rgb("#ffebee"), accent: rgb("#c62828"), body)
#let examtip(body)  = infobox(title: "Exam Tip", icon: sym.star.filled, color: rgb("#fff3e0"), accent: rgb("#e65100"), body)
#let example(body)  = infobox(title: "Example", icon: sym.square.filled, color: rgb("#f3e5f5"), accent: rgb("#6a1b9a"), body)
#let trap(body)     = infobox(title: "Common Trap", icon: sym.triangle.stroked.t, color: rgb("#ffebee"), accent: rgb("#c62828"), body)
#let memorize(body) = infobox(title: "Must Memorize", icon: sym.checkmark.heavy, color: rgb("#e3f2fd"), accent: rgb("#1565c0"), body)
```
