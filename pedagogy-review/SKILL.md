---
name: pedagogy-review
description: Run holistic pedagogical review on academic slides and educational documents. Checks narrative arc, student prerequisites, worked examples, notation clarity, and deck pacing. Supports .tex, .qmd, and .typ slide decks.
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Pedagogical Review of Slides and Educational Documents

Perform a comprehensive pedagogical review. Supports Beamer (.tex), Quarto (.qmd), and Typst (.typ) slide decks.

## Steps

1. **Identify the file** specified in `$ARGUMENTS`
   - If no argument, ask user which lecture to review
   - If just a name, Glob the project for a matching `.tex`, `.qmd`, or `.typ` file

2. **Launch the pedagogy-reviewer agent** with the full file path
   - The agent checks 13 pedagogical patterns
   - Performs deck-level analysis (narrative arc, pacing, visual rhythm, notation)
   - Considers student perspective (prerequisites, objections)

3. **Save the report the agent returns** to:
   `quality_reports/[FILENAME_WITHOUT_EXT]_pedagogy_report.md`

4. **Present summary to user:**
   - Patterns followed vs violated (out of 13)
   - Deck-level assessments
   - Critical recommendations (top 3-5)

## Important Notes

- This is a **read-only review** — no files are edited
- Focuses on **pedagogy** not visual layout (use `/visual-audit` for that)
