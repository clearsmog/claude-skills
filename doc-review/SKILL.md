---
name: doc-review
description: Universal file review — auto-detects format and launches appropriate review agents in parallel. Use for quality review of any supported file type (.typ, .md, .py, .tex, .qmd).
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
context: fork
background: false
---

# Universal Review

Auto-detect file format and launch the right review agents in parallel. Read-only — no fixes applied.

## Format Detection

Determine file type from extension:
- `.tex` → Beamer LaTeX slides
- `.qmd` → Quarto RevealJS slides
- `.typ` → Typst document (slides, docs, guides, CVs)
- `.py` → Python script
- `.md` → Markdown

For `.typ` files, also detect document type from content:
- Contains `#import "@preview/polylux"` or `#import "@preview/touying"` → Typst slides
- Contains `#import "@local/qk"` → Uses qk component library
- Contains `#set page(width: 16cm, height: 9cm)` or similar → Presentation
- Otherwise → Typst document (guide, essay, CV, etc.)

## Routing Table

| Extension | Agents (parallel) | Condition |
|-----------|-------------------|-----------|
| `.typ` | typst-reviewer + proofreader + writing-style-critic | Always |
| `.typ` | + pedagogy-reviewer | If slide format detected |
| `.typ` | + diagram-reviewer | If CeTZ is imported (`@preview/cetz`) |
| `.md` | proofreader + writing-style-critic | Always |
| `.py` | general-purpose subagent with a Python code-review brief | Always |
| `.tex`, `.qmd` | proofreader + writing-style-critic | Always (prose only: no LaTeX or Quarto toolchain is installed, so nothing is compiled) |
| `.tex` | + pedagogy-reviewer, + diagram-reviewer if TikZ found (`\begin{tikzpicture}`) | If Beamer slides |

## Steps

1. **Parse `$ARGUMENTS`** — resolve file path
2. **Detect format** from extension
3. **For `.typ` files**, read file to detect document subtype
4. **Launch agents in parallel** per routing table
5. **Save each agent's returned report** to `quality_reports/` at the path named in that agent's Output section (read-only agents return their report as text instead of writing it), then collect them
6. **Synthesize** a consolidated summary table

## Output

```markdown
# Review Summary: [Filename]

| Dimension | Agent | Critical | Major | Minor | Verdict |
|-----------|-------|----------|-------|-------|---------|
| [varies] | [agent name] | N | N | N | [status] |

## Overall: [EXCELLENT / GOOD / NEEDS WORK / POOR]

## Critical Issues (if any)
[List top issues requiring immediate attention]

## Reports Generated
- quality_reports/[file]_report.md
- quality_reports/[file]_typst_review.md
- ...
```

## Quality Score Rubric

See `typst/references/quality-gates.md` for the authoritative score rubric and severity definitions.

## Important

- This is a **read-only** review — no fixes applied
- For format-specific deep review, use the individual agents directly
