# Component Library (`@local/qk:2.2.0`)

> **Always import `@local/qk:2.2.0` in every new document.**
> Use callout variants by semantic meaning, not color.
> Prefer `qk-doc`/`qk-report` presets over manual setup.

Installed at `~/Library/Application Support/typst/packages/local/qk/2.2.0/`.

```typst
#import "@local/qk:2.2.0": *
```

> **2.1.0 is kept in sync.** The 2.2.0 fixes are backported into the 2.1.0
> package so existing documents pinned to 2.1.0 get them without edits. Both
> versions behave identically; use 2.2.0 for anything new.

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

## Utils Module

Contrast, elevation, and palette-preview helpers (re-exported from `utils.typ`).

| Component | Usage |
|-----------|-------|
| `fg-for(bg)` | Pick readable foreground (white/black) for a given background |
| `contrast-ratio(fg, bg)` | Compute WCAG contrast ratio between two colors |
| `assert-contrast(fg, bg, level: "AA", label: "")` | Assert contrast meets WCAG AA/AAA; panics only on real failure |
| `elevated(..., level: 1)` | Wrap a block with shadow/elevation |
| `color-swatch(color)` | Render a labelled color swatch (for docs/previews) |
| `palette-grid(palette)` | Render a full Tailwind shade grid for a palette |

## Theme Engine (NEW in v2)

| Component | Usage |
|-----------|-------|
| `qk-theme(palette:, tokens:, body)` | Configure theme globally via `#show: qk-theme.with(...)` |
| `theme-get(key)` | Read theme token (inside `context`) |
| `callout-theme(variant)` | Get callout colors/icon for a variant (inside `context`) |

Built-in palettes: `"default"`, `"dark"`, `"print"`, `"high-contrast"`, `"sepia"`.

| Palette | Effect |
|---------|--------|
| `"default"` | Standard emerald/blue/amber/red/violet colors |
| `"dark"` | Dark backgrounds (950 shades), light accents (400 shades) |
| `"print"` | Disables gradients for clean printing |
| `"high-contrast"` | No gradients, 2pt borders, high-contrast 100/800 shade pairs |
| `"sepia"` | Warm stone tones, no gradients, amber/stone accents |

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

5 visual styles, selectable per-callout or globally via theme. All read from theme state.

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

All variants accept `compact: false`, `style: none`, and `breakable: false` parameters.

| Style | Look | Description |
|-------|------|-------------|
| `"banner"` | Gradient header band + soft body | Default v2 look |
| `"left-bar"` | Left accent bar + tinted body | v1 look, minimal chrome |
| `"outline"` | Full rounded border + circle icon | Clean, professional |
| `"minimal"` | No border, tinted bg + left indent | Notion-like |
| `"card"` | Elevated shadow + circle icon | Card UI |

Set global style via theme: `#show: qk-theme.with(tokens: (callout-style: "left-bar"))`
Or per-callout: `#tip(style: "outline")[...]`

| Component | Usage |
|-----------|-------|
| `callout(title:, icon:, fill:, accent:, compact:, style:, breakable:, body)` | Base callout (gradient header + body) |

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
| `comparison-table(headers, header-color:, ..rows)` | Method comparison table; readable header without a preset |
| `stata-block(body)` | Stata code/output block (context-themed; reads theme state) |
| `answer-reveal(body)` | Collapsible-style answer reveal (context-themed) |
| `exam-question(body)` | Exam question wrapper (callout-based) |
| `context-block(body)` | Context/background callout (callout-based) |

## Tables Module

| Component | Usage |
|-----------|-------|
| `zebra-fill(header:, even:, odd:)` | Alternating row fill for `table(fill: ...)` |
| `styled-table(header-color:, ..args)` | Styled table with zebra rows and dark header |

## Cards Module

| Component | Usage |
|-----------|-------|
| `badge(label, color:, variant:, size:, dot:, icon:)` | Inline pill badge; `variant`: `"soft"` (default), `"solid"`, `"outline"` |
| `stat-card(value, label, color:, bg:, compact:, delta:)` | Metric card; `bg: auto` follows the theme surface |
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
| `qk-doc(title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, palette:, theme-tokens:, body)` | Study guide preset (Tailwind blue gradient headings) |
| `qk-report(body-size:, title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, palette:, theme-tokens:, body)` | Research report preset (navy/gold theme) |
| `qk-minimal(title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, palette:, theme-tokens:, body)` | Clean notes/memos preset (Inter body, no colors, Tufte-inspired, callout-style: minimal) |
| `qk-magazine(accent:, columns:, title:, header-text:, footer-text:, heading-numbering:, margin:, figure-placement:, styled-lists:, styled-captions:, stata-theme:, palette:, theme-tokens:, body)` | Editorial/newsletter preset (Charter body, Georgia headings, configurable accent, callout-style: card) |
| `qk-exam(title:, course:, date:, duration:, total-marks:, header-text:, heading-numbering:, margin:, body)` | Exam papers/problem sets preset (New Computer Modern body, Inter headings, neutral slate, auto header block) |

## Components Module

| Component | Usage |
|-----------|-------|
| `dl(accent:, ..pairs)` | Definition list -- bold term + indented definition with left accent bar. Pairs as positional `(term, definition)` args |
| `pull-quote(body, attribution:, accent:)` | Large decorative pull-quote with oversized quotation marks |
| `checklist(accent:, ..items)` | Visual checkboxes. Items: `(true, [text])` for checked, just `[text]` for unchecked |
| `alert-banner(text-content, color:, icon:)` | Full-width colored status banner strip (uppercase text) |
| `pros-cons(pros, cons)` | Two-column green/red comparison with PROS/CONS headers |
| `metric-row(gutter:, ..cards)` | Auto-sizing grid wrapper for stat-cards |
| `timeline(events, accent:)` | Vertical timeline with dots and connecting lines. Events: array of `(label, description)` pairs |
| `progress-bar(value, max:, label:, color:, height:)` | Horizontal progress bar with percentage label |
| `comparison-grid(features, products, checks)` | Feature comparison table with checkmarks/crosses. `checks`: 2D boolean array |
| `margin-note(body, side:)` | Tufte-style margin note (`side: "right"` or `"left"`) |
| `sidenote(body, number)` | Numbered sidenote with inline superscript marker and margin content |

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
#import "@local/qk:2.2.0": *
#show: qk-doc.with(
  title: "My Document",
  header-text: "Short Title",
  footer-text: "Course Name",
  styled-lists: true,
  styled-captions: true,
  stata-theme: true,
)

// Research report
#import "@local/qk:2.2.0": *
#show: qk-report.with(
  title: "Research Report",
  header-text: "Section Title",
  footer-text: "Confidential",
)

// Dark theme
#import "@local/qk:2.2.0": *
#show: qk-theme.with(palette: "dark")
#show: qk-doc.with(title: "Dark Mode Guide")

// Print mode (no gradients)
#show: qk-theme.with(palette: "print")
```

## v2.2.0 API Changes

Behaviour that changed. Do not emit the old forms.

| Area | Old (broken / absent) | New |
|------|----------------------|-----|
| `chart` | `chart("figs/p.png", "Cap")` — a path inside a package resolves against the *package* dir, so this never worked | `chart(read("figs/p.png", encoding: none), "Cap")` or `chart(image("figs/p.png"), "Cap")` |
| `assert-contrast` | errored on **every** call, pass or fail | works; panics only on genuine failure |
| `margin-note` / `sidenote` | ran off the paper edge; `side: "left"` was invisible | sized to the real page margin; `gutter:` and `width:` params added |
| `comparison-table` | header text unreadable outside a preset | picks its own contrast; new `header-color:` param |
| `styled-lists`, `styled-captions`, `stata-theme` | silently did nothing (a `set`/`show:` inside `if` only scopes to that block) | actually apply |
| `qk-slides` | discarded `title`/`subtitle`/`author`/`institution`/`logo` | renders a title slide; `title-slide: false` to opt out |
| `stat-card` | `bg: slate.at("50")` | `bg: auto` follows the theme surface |
| Boxed components | `set block(spacing: 0pt)` leaked into your content and collapsed paragraph/list gaps | seam scoped to the component's own bands |

### Theming now reaches the page

Presets take `palette:` and `theme-tokens:` directly. Pass the palette to the
**preset** — `#show: qk-theme.with(palette: ...)` written after a preset cannot
affect page fill or heading colors, because `set page(fill:)` needs the value
before state resolves.

```typst
// correct — page fill, body text, headings all follow the palette
#show: qk-doc.with(title: "Notes", palette: "dark")

// also fine: per-token overrides
#show: qk-doc.with(title: "Notes", theme-tokens: (callout-style: "outline"))
```

Palettes: `default`, `dark`, `print`, `high-contrast`, `sepia`.

All five presets share the same core options, so swapping between them is safe:
`title`, `header-text`, `footer-text`, `heading-numbering`, `margin`,
`figure-placement`, `styled-lists`, `styled-captions`, `stata-theme`,
`palette`, `theme-tokens`.

### New exports

| Export | Purpose |
|--------|---------|
| `resolve-theme(palette:, tokens:)` | Resolve a palette to a plain dict with no state — use when you need a color at `set`-time |
| `is-dark(color)` | True when white text reads better on that color |

## v1 → v2 Migration

| v1 Pattern | v2 Equivalent |
|------------|---------------|
| `colors.accent` | `blue.at("600")` (or `colors.accent` via compat dict) |
| `colors.navy` | `blue.at("950")` |
| `rgb("#1565c0")` hardcoded | `blue.at("600")` from palette |
| No theme support | `#show: qk-theme.with(palette: "dark")` |
| Flat callout boxes | Gradient header + body callouts |
| `@local/qk:1.0.0` | `@local/qk:2.0.0` |
| `@local/qk:2.0.0` | `@local/qk:2.1.0` |
| `@local/qk:2.1.0` | `@local/qk:2.2.0` |
