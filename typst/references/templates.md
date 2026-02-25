# Document Templates

> For multi-file projects (500+ lines), extract shared helpers to `lib.typ` and
> use `#import "lib.typ": *` in each content file. Keep a `main.typ` as entry
> point with `#include` for each section.

---

## 1. Research Report
**Use when:** "analysis", "research", "review", "sector", "evaluation" | **Skip when:** <2 pages, slides, CVs

```typst
#import "@local/qk:1.0.0": *

#show: qk-report.with(
  title: "Report Title",
  header-text: "Section Title",
  footer-text: "Confidential",
  heading-numbering: "1.1",
  styled-lists: true,
  styled-captions: true,
)
```

---

## 2. Presentation (touying — Metropolis)
**Use when:** "slides", "presentation", "deck", "pitch" | **Skip when:** text-heavy docs, reports, essays

> Uses touying 0.6.1 theme system. See `references/touying-guide.md` for full API.

```typst
#import "@preview/touying:0.6.1": *
#import themes.metropolis: *
#import "@local/qk:1.0.0": qk-slides, slide-callout, keypoint, tip, trap

#show: metropolis-theme.with(
  aspect-ratio: "16-9",
  footer: self => self.info.institution,
  config-info(
    title: [Presentation Title],
    subtitle: [Subtitle],
    author: [Author Name],
    date: datetime.today(),
    institution: [Institution],
  ),
)
#show: qk-slides.with(title: "Presentation Title")

#title-slide()

= First Section

== Slide Title

Content here.

#pause

Revealed on click.

#slide-callout(keypoint)[Key takeaway for the audience.]
```

## 2b. Academic Lecture (touying — University)
**Use when:** "lecture", "class", "academic talk" | **Skip when:** corporate/pitch decks, short docs

```typst
#import "@preview/touying:0.6.1": *
#import themes.university: *
#import "@local/qk:1.0.0": qk-slides, slide-callout, keypoint, tip, trap

#show: university-theme.with(
  aspect-ratio: "16-9",
  config-info(
    title: [Lecture Title],
    subtitle: [Course Name — Week N],
    author: [Instructor Name],
    date: datetime.today(),
    institution: [University Name],
    logo: emoji.school,
  ),
)
#show: qk-slides.with(title: "Lecture Title")

#title-slide()

= Topic Overview

== Key Concept

Motivation before formalism — always.

#pause

$ E[R_p] = sum_(i=1)^n w_i E[R_i] $

#slide-callout(tip)[Worked example within 2 slides of every definition.]

#focus-slide[Questions?]

#matrix-slide[Left Column][Right Column]
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
#import "@local/qk:1.0.0": *

// Brand overrides on top of qk-report
#let brand-primary = rgb("#0033a0")
#let brand-gold    = rgb("#c5a247")
#let brand-green   = rgb("#1a7a3a")
#let brand-red     = rgb("#c0392b")

#show: qk-report.with(
  title: "Report Title",
  header-text: "Report Title",
  footer-text: "Date",
  body-size: 10pt,
  styled-lists: true,
)

// Brand heading overrides
#show heading.where(level: 1): it => {
  v(10pt)
  block(width: 100%)[
    #block(fill: brand-primary, inset: (x: 12pt, y: 8pt), radius: (top: 4pt),
      width: 100%, text(fill: white, weight: "bold", size: 13pt, it.body))
    #block(fill: brand-primary.lighten(85%), inset: 0pt, width: 100%, height: 2pt)
  ]
  v(6pt)
}
#show heading.where(level: 2): it => {
  v(6pt)
  block[#text(fill: brand-primary, weight: "bold", size: 11pt)[#it.body]
    #v(-2pt) #line(length: 40%, stroke: 1pt + brand-gold)]
  v(4pt)
}
```

---

## 7. Study Guide
**Use when:** "study guide", "revision", "cheatsheet", "exam", "formula sheet" | **Skip when:** formal papers, client docs, slides

```typst
#import "@local/qk:1.0.0": *

#show: qk-doc.with(
  title: "Study Guide Title",
  header-text: "Short Title",
  footer-text: "Course Name",
  styled-lists: true,
  styled-captions: true,
)

// qk-doc already provides: Libertinus Serif body, Inter headings,
// NCM Math, Fira Code, blue accent headings, smart header/footer,
// zebra tables. No need to redefine.
```

---

## 8. Cheatsheet / Reference Card
**Use when:** "cheatsheet", "reference card", "formula sheet", "quick reference" | **Skip when:** >2 pages, narrative docs, slides

> Dense, information-rich layout. A4 landscape, small text, minimal margins, colored section bars.

```typst
#import "@local/qk:1.0.0": *

#set page(paper: "a4", flipped: true, margin: (x: 1cm, y: 1cm))
#set text(font: "New Computer Modern", size: 8pt)
#set par(leading: 0.45em, spacing: 0.5em, justify: true)
#set heading(numbering: none)

// Compact colored section headers
#show heading.where(level: 1): it => {
  block(fill: colors.navy, inset: (x: 6pt, y: 4pt), radius: 2pt, width: 100%,
    text(fill: white, weight: "bold", size: 9pt, it.body))
  v(2pt)
}
#show heading.where(level: 2): it => {
  block(above: 0.4em, below: 0.2em,
    text(weight: "bold", size: 8.5pt, fill: colors.accent, it.body))
}

#columns(3, gutter: 8pt)[
  // Content here — use short paragraphs, tables, formula-box
]
```

---

## 9. Exam / Problem Set
**Use when:** "exam", "problem set", "homework", "quiz", "assignment" | **Skip when:** study guides, slides, reports

> Uses qk academic components. Numbered questions with answer space. Optional answer key toggle.

```typst
#import "@local/qk:1.0.0": *

#let show-answers = false  // Toggle to true for answer key version

#show: qk-doc.with(
  title: "Exam Title",
  header-text: "Course — Exam",
  footer-text: "Page",
  heading-numbering: none,
)

// Exam header
#align(center)[
  #text(size: 16pt, weight: "bold")[Course Name — Final Exam]
  #v(4pt)
  #text(size: 10pt)[Date: #datetime.today().display() #h(2em) Time: 2 hours #h(2em) Total: 100 marks]
]
#v(1em)
#line(length: 100%, stroke: 1pt)
#grid(columns: (1fr, 1fr), gutter: 12pt,
  [Name: #box(width: 100%, stroke: (bottom: 0.5pt))[]],
  [Student ID: #box(width: 100%, stroke: (bottom: 0.5pt))[]],
)
#v(1em)

// Questions using qk components
#question-box(number: 1)[
  Define portfolio diversification and explain its effect on risk. *(10 marks)*
]
#if show-answers {
  answer-box[
    Portfolio diversification is the practice of...
  ]
} else {
  v(5cm)  // Answer space
}

#question-box(number: 2)[
  Calculate the expected return given the following data. *(15 marks)*
]
#formula-box("Expected Return")[
  $ E[R_p] = sum_(i=1)^n w_i E[R_i] $
]
```

---

## 10. Flashcard / Q&A
**Use when:** "flashcard", "Q&A cards", "revision cards", "study cards" | **Skip when:** continuous text, exams, slides

> Alternating question/answer cards on half-pages. Suitable for print-and-cut.

```typst
#import "@local/qk:1.0.0": *

#set page(paper: "a4", margin: (x: 1.5cm, y: 1.5cm))
#set text(font: "New Computer Modern", size: 11pt)

#let flashcard(question, answer) = {
  block(width: 100%, inset: 16pt, radius: 6pt, above: 1em, below: 0em,
    fill: rgb("#f0f4ff"), stroke: 1.5pt + colors.accent)[
    #text(weight: "bold", size: 10pt, fill: colors.accent)[Q:]
    #v(4pt)
    #text(size: 11pt)[#question]
  ]
  block(width: 100%, inset: 16pt, radius: 6pt, above: 0em, below: 1em,
    fill: rgb("#f0faf0"), stroke: 1.5pt + colors.success)[
    #text(weight: "bold", size: 10pt, fill: colors.success)[A:]
    #v(4pt)
    #text(size: 10pt)[#answer]
  ]
  line(length: 100%, stroke: (dash: "dashed", paint: luma(200), thickness: 0.5pt))
}

#align(center, text(size: 18pt, weight: "bold")[Revision Flashcards — Topic Name])
#v(1em)

#flashcard(
  [What is the Capital Asset Pricing Model?],
  [CAPM: $E[R_i] = R_f + beta_i (E[R_m] - R_f)$. It relates expected return to systematic risk (beta).]
)

#flashcard(
  [What does beta measure?],
  [Beta measures the sensitivity of an asset's returns to market returns. Beta > 1 means more volatile than market.]
)
```
