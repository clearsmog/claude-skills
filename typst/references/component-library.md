# Component Library (`@local/qk:2.0.0`)

> **Always import `@local/qk:2.0.0` in every new document.**
> Use callout variants by semantic meaning, not color.
> Prefer `qk-doc`/`qk-report` presets over manual setup.

Installed at `~/Library/Application Support/typst/packages/local/qk/2.0.0/`.

```typst
#import "@local/qk:2.0.0": *
```

## Palette Module (NEW in v2)

Tailwind CSS color scales with shades 50–950. Access: `blue.at("600")`, `emerald.at("50")`, etc.

| Hue | Import name |
|-----|-------------|
| Blue, Emerald, Amber, Red, Violet, Teal | `blue`, `emerald`, `amber`, `red`, `violet`, `teal` |
| Slate, Zinc, Orange, Rose, Indigo, Cyan | `slate`, `zinc`, `orange`, `rose`, `indigo`, `cyan` |
| Sky, Lime, Fuchsia, Pink, Stone, Gray, Neutral | `sky`, `lime`, `fuchsia`, `pink`, `stone`, `gray`, `neutral` |

| Component | Usage |
|-----------|-------|
| `colors` | Backward-compat dict mapping v1 names: accent, success, warning, danger, info, surface, etc. |
| `tint(color, amount: 88%)` | Auto-generate light background tint |
| `border-for(fill)` | Compute stroke color from fill |

**Shade access pattern**: `blue.at("600")` (string keys required).

## Theme Engine (NEW in v2)

| Component | Usage |
|-----------|-------|
| `qk-theme(palette:, tokens:, body)` | Configure theme globally via `#show: qk-theme.with(...)` |
| `theme-get(key)` | Read theme token (inside `context`) |
| `callout-theme(variant)` | Get callout colors/icon for a variant (inside `context`) |

Built-in palettes: `"default"`, `"dark"`, `"print"` (disables gradients).

```typst
// Dark mode
#show: qk-theme.with(palette: "dark")

// Custom overrides
#show: qk-theme.with(tokens: (
  tip: (fill: amber.at("50"), accent: amber.at("600"), icon: sym.star.filled),
  use-gradients: false,
))
```

## Callouts (15 variants)

Modern gradient header band + soft body. All read from theme state.

| Component | Color family | Icon |
|-----------|-------------|------|
| `tip` | emerald | diamond.filled |
| `keypoint` | emerald (darker) | star.filled |
| `remember` | emerald (lighter) | checkmark |
| `warning` | red | excl |
| `trap` | rose | triangle.filled.t |
| `note` | blue | circle.stroked |
| `memorize` | blue (darker) | checkmark.heavy |
| `practitioner` | blue (lighter) | circle.filled |
| `caution` | amber | triangle.stroked.t |
| `examtip` | amber (darker) | star.filled |
| `insight` | orange | arrow.r.filled |
| `example-box` | violet | square.filled |
| `whycare` | violet (darker) | interrobang |
| `analogy` | teal | diamond.filled |
| `simple` | teal (lighter) | arrow.r |

All accept `compact: false` parameter for dense guides.

| Component | Usage |
|-----------|-------|
| `callout(title:, icon:, fill:, accent:, compact:, body)` | Base callout (gradient header + body) |

## Academic Module

| Component | Usage |
|-----------|-------|
| `answerbox(correct, why-correct, the-trap, concept, meta: none)` | MCQ answer box with gradient header |
| `qheader(label, qnum)` | Gradient pill question header |
| `question-box(number: 0, body)` | Numbered question container |
| `answer-box(body)` | Emerald answer box |
| `warning-box(body)` | Red warning box |
| `note-box(body)` | Blue note box |
| `exam-pattern(body)` | Teal exam pattern box |
| `data-overview(body)` | Slate dataset summary |
| `freq-badge(level)` | HIGH/MEDIUM/LOW frequency pill (validates input) |
| `formula-box(title, body)` | Blue equation highlight with gradient header |
| `step-box(title, body)` | Violet step procedure with gradient header |
| `comparison-table(headers, ..rows)` | Method comparison table |

## Tables Module

| Component | Usage |
|-----------|-------|
| `zebra-fill(header:, even:, odd:)` | Alternating row fill for `table(fill: ...)` |
| `styled-table(header-color:, ..args)` | Styled table with zebra rows and dark header |

## Cards Module

| Component | Usage |
|-----------|-------|
| `badge(label, color:, filled:)` | Inline pill badge (`filled: true` for solid) |
| `stat-card(value, label, color:, bg:)` | Metric display card with gradient bg |
| `header-card(title, header-bg:, body)` | Two-tone card with gradient header band |

## Layout Module

| Component | Usage |
|-----------|-------|
| `divider(label:, color:)` | Gradient horizontal rule separator |
| `smart-header(title, show-page-num:)` | Running header (hides on page 1) |
| `smart-footer(center-text:, show-page-num:)` | Running footer (hides on page 1) |
| `lecture-divider(num, title, subtitle)` | Modern gradient section divider page |

## Presets Module

| Component | Usage |
|-----------|-------|
| `qk-doc(title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, body)` | Study guide preset (Tailwind blue gradient headings) |
| `qk-report(title:, header-text:, footer-text:, body-size:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, body)` | Research report preset (navy/gold theme) |

## Code & Figures Modules

| Component | Usage |
|-----------|-------|
| `stata-terminal(body)` | Dark Stata terminal show rule (zinc/blue palette) |
| `chart(path, caption-text, alt-text:, width:)` | Figure wrapper for chart images |
| `context-note(body)` | Italic supplementary remark |

## Slides Module

| Component | Usage |
|-----------|-------|
| `qk-slides(title:, date:, author:, body)` | Presentation preset (date resolved at render time) |
| `slide-callout(component, body)` | Scale callout for slide context |

## Preset Usage Examples

```typst
// Study guide with all features
#import "@local/qk:2.0.0": *
#show: qk-doc.with(
  title: "My Document",
  header-text: "Short Title",
  footer-text: "Course Name",
  styled-lists: true,
  styled-captions: true,
  stata-theme: true,
)

// Research report
#import "@local/qk:2.0.0": *
#show: qk-report.with(
  title: "Research Report",
  header-text: "Section Title",
  footer-text: "Confidential",
)

// Dark theme
#import "@local/qk:2.0.0": *
#show: qk-theme.with(palette: "dark")
#show: qk-doc.with(title: "Dark Mode Guide")

// Print mode (no gradients)
#show: qk-theme.with(palette: "print")
```

## v1 → v2 Migration

| v1 Pattern | v2 Equivalent |
|------------|---------------|
| `colors.accent` | `blue.at("600")` (or `colors.accent` via compat dict) |
| `colors.navy` | `blue.at("950")` |
| `rgb("#1565c0")` hardcoded | `blue.at("600")` from palette |
| No theme support | `#show: qk-theme.with(palette: "dark")` |
| Flat callout boxes | Gradient header + body callouts |
| `@local/qk:1.0.0` | `@local/qk:2.0.0` |
