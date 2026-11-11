---
name: doc-review
description: Universal file review — auto-detects format and launches appropriate review agents in parallel. Use for quality review of any supported file type (.typ, .md, .py, .tex, .qmd, .d2).
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
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
- `.d2` → D2 diagram source (the `diagram` skill)

For `.typ` files, also detect document type from content:
- Contains `#import "@preview/polylux"` or `#import "@preview/touying"` → Typst slides
- Contains `#import "@local/qk"` → Uses qk component library
- Contains `#set page(width: 16cm, height: 9cm)` or similar → Presentation
- Otherwise → Typst document (guide, essay, CV, etc.)

Then detect two things from content, for every prose format:

- **Diagrams.** Any of: `@preview/fletcher`, `@preview/chronos`, `@preview/timeliney`,
  `@preview/cetz`; an embedded image whose file has a sibling `.d2` source
  (`image("diagrams/x.light.svg")` beside `diagrams/x.d2`, or `![](x.svg)` in Markdown);
  `\begin{tikzpicture}` in `.tex`.
- **Substance.** The file makes claims a specialist could get wrong: formulas, numbers
  with a source or derivation, defined terms, worked examples, legal or regulatory
  statements. A CV, cover letter, README, changelog or meeting note does not count.

## Routing Table

| Extension | Agents (parallel) | Condition |
|-----------|-------------------|-----------|
| `.typ` | typst-reviewer + proofreader + writing-style-critic | Always |
| `.typ` | + pedagogy-reviewer | If slide format detected |
| `.md` | proofreader + writing-style-critic | Always |
| `.tex`, `.qmd` | proofreader + writing-style-critic | Always (prose only: no LaTeX or Quarto toolchain is installed, so nothing is compiled) |
| `.tex` | + pedagogy-reviewer | If Beamer slides |
| `.typ`, `.md`, `.tex`, `.qmd` | + domain-reviewer | If substance detected |
| `.typ`, `.md`, `.tex` | + diagram-reviewer | If diagrams detected |
| `.d2` | diagram-reviewer | Always |
| `.py` | general-purpose subagent with a Python code-review brief | Always |

Each agent's report is saved under `quality_reports/`, where `<name>` is the file name
without its extension:

| Agent | Report file |
|---|---|
| typst-reviewer | `<name>_typst_review.md` |
| proofreader | `<name>_report.md` (`<name>_qmd_report.md` for `.qmd`) |
| writing-style-critic | `<name>_tropes_review.md` |
| pedagogy-reviewer | `<name>_pedagogy_report.md` |
| domain-reviewer | `<name>_substance_review.md` |
| diagram-reviewer | `<name>_diagram_review.md` |
| general-purpose (`.py`) | `<name>_code_review.md` |

## Rendering for the diagram reviewer

fletcher, chronos, timeliney and D2 lay diagrams out themselves, so the source does not
say where anything landed. The diagram-reviewer has no Bash: render first and hand it
the pictures.

- `.typ`: compile the pages to PNG in a temp directory, with the same `--root` and
  `--font-path` flags the project compiles with:
  `typst compile --format png --ppi 110 <file>.typ "$(mktemp -d)/p-{0p}.png"`.
  Give the reviewer the PNG paths, the `.typ` path, and the line numbers of each
  diagram. For an embedded D2 image, add its `.d2` source path.
- `.d2`: pass the source and the `<name>.light.png` beside it. If there is none, or it is
  older than the source, render one with the `diagram` skill:
  `${CLAUDE_SKILL_DIR}/../diagram/scripts/render.sh <file>.d2 -o "$(mktemp -d)" --light-only`
  (a temp directory, never over the project's files).
- `.md`: pass the `.d2` source and its PNG as above.
- `.tex` (TikZ): nothing can be rendered here; say so in the brief, and the reviewer
  works from coordinates.
- If a render fails, still launch the reviewer, tell it there is no render, and put the
  compile error in the summary.

## Steps

1. **Parse `$ARGUMENTS`** — resolve file path
2. **Detect format** from extension
3. **Read the file** to detect the `.typ` subtype, diagrams and substance
4. **Render** for the diagram reviewer if diagrams were detected (section above)
5. **Launch agents in parallel** per routing table, in one message, using the Agent tool with the agent name as `subagent_type`. Each brief gives the absolute file path; the diagram brief adds the renders and line numbers
6. **Save each agent's returned report** to its file in the table above (the agents are read-only and return the report as text), then collect them
7. **Synthesize** a consolidated summary table, and list which agents were skipped and why (no diagrams, no substance)

## Output

```markdown
# Review Summary: [Filename]

| Dimension | Agent | Critical | Major | Minor | Verdict |
|-----------|-------|----------|-------|-------|---------|
| [varies] | [agent name] | N | N | N | [status] |

## Overall: [APPROVED / NEEDS REVISION / REJECTED]

## Critical Issues (if any)
[List top issues requiring immediate attention]

## Reports Generated
- quality_reports/[name]_report.md
- quality_reports/[name]_typst_review.md
- ... (one per agent launched)

## Not Run
- [agent]: [reason, e.g. "no diagrams detected"]
```

## Severity and Verdicts

Use the severity definitions and verdict rules in `${CLAUDE_SKILL_DIR}/../typst/references/quality-gates.md`. The overall verdict is the worst one: any CRITICAL or MAJOR finding from any agent makes it NEEDS REVISION; APPROVED needs zero of both. Where an agent reports in its own scale, apply the rules to its Critical / Major / Minor counts.

## Important

- This is a **read-only** review — no fixes applied. The only files written are the reports and temp renders
- For format-specific deep review, use the individual agents directly
