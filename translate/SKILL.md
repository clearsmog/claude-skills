---
name: translate
description: Multi-format document translation. Supports Typst ↔ Quarto. For Beamer translations, configure at project level.
argument-hint: "[source_file] [target_format]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Multi-Format Translation Workflow

Translate documents between supported formats.

**CRITICAL: The source file is the SINGLE SOURCE OF TRUTH.**

---

## Supported Translations

| From | To | Method |
|------|----|--------|
| `.typ` (Typst) | `.qmd` (Quarto) | Component mapping |
| `.qmd` (Quarto) | `.typ` (Typst) | CSS classes to components |

> **Note:** For Beamer (`.tex`) translations, configure at project level.
> Projects with Beamer support should have their own translate skill
> with environment mapping tables.

## Format Detection

Parse `$ARGUMENTS`:
- First argument: source file path
- Second argument (optional): target format (`.qmd`, `.typ`)
- If no target specified, infer from project context

---

## Typst → Quarto

### Component Mapping

| Typst (qk) | Quarto CSS |
|-------------|-----------|
| `#keypoint[...]` | `::: {.keybox}\n...\n:::` |
| `#insight[...]` | `::: {.highlightbox}\n...\n:::` |
| `#tip[...]` | `::: {.methodbox}\n...\n:::` |
| `#note[...]` | `::: {.softbox}\n...\n:::` |
| `#warning[...]` | `::: {.keybox}\n**Warning:** ...\n:::` |
| `#trap[...]` | `::: {.keybox}\n**Common mistake:** ...\n:::` |

### Citation Mapping
- `@key` → `@key` (same in Quarto)

### Math Mapping
- `$...$` (Typst inline) → `$...$` (Quarto inline)
- `$ ... $` (Typst display) → `$$...$$` (Quarto display)

---

## Quarto → Typst

### Component Mapping

| Quarto CSS | Typst (qk) |
|-----------|-------------|
| `::: {.keybox}` | `#keypoint[...]` |
| `::: {.highlightbox}` | `#insight[...]` |
| `::: {.methodbox}` | `#tip[...]` |
| `::: {.resultbox}` | `#keypoint[...]` |
| `::: {.quotebox}` | `#quote(attribution: "...")[...]` |
| `::: {.softbox}` | `#note[...]` |

### Math Mapping
- `$...$` → `$...$`
- `$$...$$` → `$ ... $` (display)

---

## Quality Standards (All Translations)

1. **Content parity** — every idea from source must appear in target
2. **Environment parity** — every box/callout must use the corresponding target element
3. **Notation consistency** — same symbols as source
4. **No content loss** — never summarize or condense
5. **All citations verified** — every reference resolves
6. **All images referenced** — every figure path valid
7. **Compile successfully** — target must build without errors

## Post-Translation

Run `/qa` on the translated file to verify quality.
