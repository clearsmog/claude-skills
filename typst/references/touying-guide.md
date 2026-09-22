# Touying Presentation Guide

> **Version:** touying 0.7.4 (compiler ≥0.12; verified on Typst 0.15.0)
> **Import:** `#import "@preview/touying:0.7.4": *`
> **CRITICAL:** The 0.6.x/0.7.x API differs completely from 0.3.x/0.4.x. Do NOT use `register()`, `utils.methods()`, or `utils.slides()` — those are the old API. The 0.6→0.7 change is incremental (same `theme.with(...)` system); see Version History for the two minor behavior changes.

---

## Quick Start (Metropolis)

```typst
#import "@preview/touying:0.7.4": *
#import themes.metropolis: *
#import "@local/qk:2.2.0": qk-slides, slide-callout, keypoint, tip

#show: metropolis-theme.with(
  aspect-ratio: "16-9",
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

Content here. Use `#pause` for reveals.

#pause

This appears after clicking.

#slide-callout(keypoint)[This is a key takeaway styled for slides.]

== Another Slide

#focus-slide[Wake up!]
```

---

## Theme Comparison

| Theme | Import | Show Rule | Best For | Slide Types |
|-------|--------|-----------|----------|-------------|
| **metropolis** | `themes.metropolis: *` | `metropolis-theme.with(...)` | Technical talks, seminars | title, focus, new-section |
| **university** | `themes.university: *` | `university-theme.with(...)` | Academic lectures, institution branding | title, focus, matrix |
| **stargazer** | `themes.stargazer: *` | `stargazer-theme.with(...)` | Polished conferences | title, outline, focus |
| **dewdrop** | `themes.dewdrop: *` | `dewdrop-theme.with(...)` | Light aesthetic, navigation bar | title, outline, focus |
| **simple** | `themes.simple: *` | `simple-theme.with(...)` | Minimal, distraction-free | title, centered, focus |
| **aqua** | `themes.aqua: *` | `aqua-theme.with(...)` | Colorful, modern | title, outline, focus |

---

## Config Functions

All themes accept these config functions as arguments to `theme-name.with(...)`:

### `config-info(...)`

Presentation metadata. Always populate at minimum: title, author, date.

```typst
config-info(
  title: [Title],
  subtitle: [Subtitle],
  author: [Author],
  date: datetime.today(),
  institution: [Institution],
  logo: emoji.school,  // or image("logo.png", height: 1.5em)
)
```

### `config-common(...)`

Global behavior settings.

```typst
config-common(
  show-notes-on-second-screen: right,  // Enable speaker notes display
  datetime-format: auto,
)
```

### Theme-specific parameters

Each theme has its own parameters before the config functions:

```typst
#show: metropolis-theme.with(
  aspect-ratio: "16-9",      // "16-9" or "4-3"
  footer: self => self.info.institution,
  config-info(...),
)

#show: stargazer-theme.with(
  aspect-ratio: "16-9",
  progress-bar: true,         // Bottom progress indicator
  config-info(...),
)

#show: dewdrop-theme.with(
  aspect-ratio: "16-9",
  navigation: "mini-slides",  // Top navigation bar
  config-info(...),
)
```

---

## Slide Types

### Standard slides (all themes)

```typst
= Section Title        // Creates a new-section slide automatically
== Slide Title          // Creates a regular slide with title
---                     // Untitled slide (content only)
```

### Special slides

```typst
#title-slide()                    // Title page with config-info metadata
#title-slide(authors: ([A], [B])) // University theme: multiple authors

#focus-slide[Wake up!]            // Full-screen emphasis

#matrix-slide[Left][Right]        // University theme: multi-column
#matrix-slide(columns: 3)[A][B][C]
#matrix-slide(columns: (1fr, 2fr))[Narrow][Wide]

#outline-slide()                  // Table of contents (stargazer, dewdrop)
```

---

## Animation & Reveals

### `#pause`

Insert pause points. Content after `#pause` appears on the next click.

```typst
== Key Concepts

First point is always visible.

#pause

Second point appears on click.

#pause

Third point appears on next click.
```

### `#meanwhile`

Show content synchronously on a different subslide.

```typst
Left column content.

#pause

More left content.

#meanwhile

Right column content (appears with "Left column content").
```

### Progressive list reveal

For lists that reveal item by item, put `#pause` between items (robust across themes):

```typst
- First item
#pause
- Second item
#pause
- Third item
```

> **0.7.x note:** `components.progressive-show` (the old 0.6.x helper) was removed. The compact equivalent is now `utils.item-by-item`, but it needs the slide's `self` and must be wrapped (`touying-fn-wrapper(self => utils.item-by-item(self: self)[...])`). For everyday decks the `#pause`-between-items form above is simpler and always works.

**Usage guideline:** Use `#pause` sparingly — 2-3 per slide maximum. Overuse makes presentations feel sluggish.

---

## Speaker Notes

```typst
== Slide Title

Visible content here.

#speaker-note[
  - Talking points for the presenter
  - These are hidden in normal view
  - Visible with `config-common(show-notes-on-second-screen: right)`
]
```

To enable speaker notes display:

```typst
#show: theme-name.with(
  config-common(show-notes-on-second-screen: right),
  config-info(...),
)
```

**0.7.3 change:** `#speaker-note[]` now always attaches to the slide *above* it, and `receive-body-for-new-*-slide-fn` defaults to `false`. If you relied on prose written directly under a `= Section` heading being absorbed into the section slide, set `receive-body-for-new-section-slide-fn: true` in `config-common(...)`.

---

## Appendix

Slides after `#show: appendix` don't count in the total slide number and don't appear in outlines.

```typst
#show: appendix

= Backup Slides

== Extra Detail

This slide has a separate numbering.
```

---

## Integration with qk Components

Use `slide-callout` to render qk callout boxes at slide-appropriate sizing:

```typst
#import "@local/qk:2.2.0": slide-callout, keypoint, tip, trap

== Important Concepts

#slide-callout(keypoint)[Portfolio diversification reduces unsystematic risk.]

#slide-callout(tip)[Use Sharpe ratio for risk-adjusted comparison.]

#slide-callout(trap)[Don't confuse correlation with causation in returns.]
```

**Max 2 callout boxes per slide** — more causes component fatigue.

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Using 0.3.x/0.4.x API | `register()`, `utils.methods()` don't exist in 0.6.x/0.7.x | Use `#show: theme-name.with(...)` |
| Missing theme import | `themes.metropolis` not found | Add `#import themes.metropolis: *` after touying import |
| Empty title slide | No metadata shown | Populate `config-info(...)` |
| Too many pauses | Presentation feels sluggish | Max 2-3 `#pause` per slide |
| Font mismatch | Theme fonts don't match qk style | Apply `#show: qk-slides.with(...)` after theme show rule |
| Polylux import | Incompatible with touying | Use touying only — don't mix packages |

---

## Version History

| Version | Breaking Changes |
|---------|-----------------|
| 0.7.4 | `lazy-layout` defaults to `false` for `cols` |
| 0.7.3 | `#speaker-note[]` always attaches to previous slide; `receive-body-for-new-*-slide-fn` defaults to `false` (see Speaker Notes) |
| 0.7.x | Same API as 0.6.x (`#show: theme.with(...)`, `config-info`, `config-common`) — incremental, no theme-system rewrite |
| 0.6.x | Established API: `#show: theme.with(...)`, `config-info`, `config-common` |
| 0.5.x | Transitional: introduced `theme.with()` pattern |
| 0.4.x | Old API: `register()` + `utils.methods()` |
| 0.3.x | Original API: `register()` + `utils.slides()` |

**Use 0.7.4** — current release, verified compatible with Typst 0.15.0. The 0.6.x API patterns in this guide all carry over unchanged.
