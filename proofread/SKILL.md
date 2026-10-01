---
name: proofread
description: Run the proofreading protocol on documents. Checks grammar, typos, overflow, consistency, and academic writing quality for .tex, .qmd, .typ, and .md files. Produces a report without editing files.
argument-hint: "[filename or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Proofread Documents

Run the proofreading protocol on documents. Produce a report only; leave source files unedited, because fixes are applied separately after the user reviews the report.

## Steps

1. **Identify files to review:**
   - If `$ARGUMENTS` is a specific filename: review that file only
   - If `$ARGUMENTS` is "all": review every `.tex`, `.qmd`, `.typ`, and `.md` document in the project

2. **For each file, launch the proofreader agent** that checks for:

   **GRAMMAR:** Subject-verb agreement, articles (a/an/the), prepositions, tense consistency
   **TYPOS:** Misspellings, search-and-replace artifacts, duplicated words
   **OVERFLOW:** Overfull hbox (LaTeX), content exceeding slide boundaries (Quarto)
   **CONSISTENCY:** Citation format, notation, terminology
   **ACADEMIC QUALITY:** Informal language, missing words, awkward constructions

3. **Produce a detailed report** for each file listing every finding with:
   - Location (line number or slide title)
   - Current text (what's wrong)
   - Proposed fix (what it should be)
   - Category and severity

4. **Save each report** to `quality_reports/`:
   - For `.tex` files: `quality_reports/FILENAME_report.md`
   - For `.qmd` files: `quality_reports/FILENAME_qmd_report.md`

5. **Present summary** to the user:
   - Total issues found per file
   - Breakdown by category
   - Most critical issues highlighted
