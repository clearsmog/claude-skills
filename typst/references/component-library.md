# Component Library (`@local/qk:1.0.0`)

> **Always import `@local/qk:1.0.0` in every new document.**
> Use callout variants by semantic meaning, not color.
> Prefer `qk-doc`/`qk-report` presets over manual setup.

Installed at `~/Library/Application Support/typst/packages/local/qk/1.0.0/`.

```typst
#import "@local/qk:1.0.0": *
```

## Colors Module

| Component | Usage |
|-----------|-------|
| `colors` | Semantic palette dict: accent, success, warning, danger, info, surface, light, muted, slate, navy, gold, teal, purple, header, dark, caption, footer, border |
| `tint(color, amount: 88%)` | Auto-generate light background tint |
| `border-for(fill)` | Compute stroke color from fill |

## Callouts (15 variants)

| Component | Usage |
|-----------|-------|
| `callout(title:, icon:, fill:, accent:, body)` | Base callout box (left-bordered) |
| `tip`, `warning`, `note`, `caution`, `example-box` | Original callout variants |
| `examtip`, `memorize`, `trap` | Study guide variants |
| `keypoint`, `insight`, `practitioner`, `analogy`, `whycare`, `simple`, `remember` | v1.0.0 variants |

## Academic Module

| Component | Usage |
|-----------|-------|
| `answerbox(correct, why-correct, the-trap, concept, meta: none)` | MCQ answer breakdown |
| `qheader(label, qnum)` | Question header banner |
| `question-box(number: 0, body)` | Numbered question container |
| `answer-box(body)` | Green answer box |
| `warning-box(body)` | Red warning box |
| `note-box(body)` | Blue note box |
| `exam-pattern(body)` | Teal exam pattern box |
| `data-overview(body)` | Gray dataset summary |
| `freq-badge(level)` | HIGH/MEDIUM frequency pill |
| `formula-box(title, body)` | Blue equation highlight |
| `step-box(title, body)` | Purple step procedure |
| `comparison-table(headers, ..rows)` | Method comparison table |

## Tables Module

| Component | Usage |
|-----------|-------|
| `zebra-fill(header:, even:, odd:)` | Alternating row fill for `table(fill: ...)` |
| `styled-table(header-color:, ..args)` | Styled table with zebra rows and colored header |

## Cards Module

| Component | Usage |
|-----------|-------|
| `badge(label, color:, filled:)` | Inline pill badge (`filled: true` for solid) |
| `stat-card(value, label, color:, bg:)` | Metric display card for KPI grids |
| `header-card(title, header-bg:, body)` | Two-tone card (dark header + light body) |

## Layout Module

| Component | Usage |
|-----------|-------|
| `divider(label:, color:)` | Horizontal rule separator |
| `smart-header(title, show-page-num:)` | Running header (hides on page 1) |
| `smart-footer(center-text:, show-page-num:)` | Running footer (hides on page 1) |
| `lecture-divider(num, title, subtitle)` | Section divider page |

## Presets Module

| Component | Usage |
|-----------|-------|
| `qk-doc(title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, body)` | Study guide preset |
| `qk-report(title:, header-text:, footer-text:, body-size:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, body)` | Research report preset |

## Code & Figures Modules

| Component | Usage |
|-----------|-------|
| `stata-terminal(body)` | Dark Stata terminal show rule |
| `chart(path, caption-text, alt-text:, width:)` | Figure wrapper for chart images |
| `context-note(body)` | Italic supplementary remark |

## Preset Usage Examples

```typst
// Study guide with all features
#import "@local/qk:1.0.0": *
#show: qk-doc.with(
  title: "My Document",
  header-text: "Short Title",
  footer-text: "Course Name",
  styled-lists: true,
  styled-captions: true,
  stata-theme: true,
)

// Research report
#import "@local/qk:1.0.0": *
#show: qk-report.with(
  title: "Research Report",
  header-text: "Section Title",
  footer-text: "Confidential",
)
```

## Migrating from Custom Styles

Common inline patterns and their qk equivalents:

| Inline Pattern | qk Equivalent |
|----------------|---------------|
| Manual `#set page(...)` + `#set text(...)` + heading show rules | `#show: qk-doc.with(...)` or `#show: qk-report.with(...)` |
| Custom `#let infobox(...)` callout factory | `#callout(title:, icon:, fill:, accent:, body)` or specific variants |
| `#let styled-table(...)` with zebra rows | `#styled-table(header-color:, ..args)` from qk tables module |
| `#let stat-card(value, label)` inline | `#stat-card(value, label, color:, bg:)` from qk cards module |
| Custom header/footer with `context` | `qk-doc` / `qk-report` presets handle this automatically |
| `#set list(marker: ...)` with blue bullets | `qk-doc.with(styled-lists: true)` |
| Custom figure caption styling | `qk-doc.with(styled-captions: true)` |

**When to keep custom styles:** Essay (unique first-line-indent + author header), CV (specialized layout), Annotated Reference (domain-specific callout factory).
