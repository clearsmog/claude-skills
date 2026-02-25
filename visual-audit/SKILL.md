---
name: visual-audit
description: Adversarial visual layout audit of documents and slides. Checks overflow, font consistency, component fatigue, and spacing. Supports .tex, .qmd, and .typ files.
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Visual Audit

Perform a thorough visual layout audit of any supported document. Routes to the `document-auditor` agent.

## Steps

1. **Read the file** specified in `$ARGUMENTS`

2. **For Quarto (.qmd) files:**
   - Render with `quarto render Quarto/$ARGUMENTS`
   - Open in browser to inspect each slide

3. **For Beamer (.tex) files:**
   - Compile and check for overfull hbox warnings

4. **For Typst (.typ) files:**
   - Compile with `typst compile FILENAME.typ`
   - Check for content overflow, component fatigue, typography consistency

5. **Audit every slide/page for:**

   **OVERFLOW:** Content exceeding boundaries
   **FONT CONSISTENCY:** Inline font-size overrides, inconsistent sizes
   **COMPONENT FATIGUE:** 2+ colored boxes/callouts on one slide/page, wrong types
   **SPACING:** Missing margins, missing alignment
   **LAYOUT:** Missing transitions, missing framing sentences, semantic colors

6. **Produce a report** organized by slide/page with severity and recommendations

7. **Follow the spacing-first principle:**
   1. Reduce vertical spacing with negative margins
   2. Consolidate lists
   3. Move displayed equations inline
   4. Reduce image/SVG size
   5. Last resort: font size reduction (never below 0.85em)
