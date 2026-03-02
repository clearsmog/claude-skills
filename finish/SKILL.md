---
name: finish
description: Master pipeline — compile, review, fix, and finalize any document. Auto-detects format and runs the full quality loop.
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Finish Document

Master pipeline that compiles, reviews, fixes, and finalizes any supported document type.

## Format Detection

Determine file type from extension:
- `.typ` → Typst document (slides, docs, guides, CVs)
- `.qmd` → Quarto RevealJS slides
- `.py` → Python script

> **Note:** For `.tex` (LaTeX/Beamer), configure the finish pipeline at project level.

For `.typ` files, also detect document type from content:
- Contains `#import "@preview/polylux"` or `#import "@preview/touying"` → Typst slides
- Contains `#import "@local/qk"` → Uses qk component library
- Otherwise → Typst document

## Pipeline Phases

### Phase 0: Detect File Type
- Parse `$ARGUMENTS`, resolve file path
- Detect format from extension and content

### Phase 1: Compile + Visual Spot-Check

**Step 1 — Compile:**
- Route to `/compile` with the detected format
- **Hard gate:** exit code must be 0. Do not proceed until compilation succeeds.

**Step 2 — Determine sample pages:**
- Documents <=3 pages → all pages
- Documents >3 pages → page 1, middle page, last page
- Presentations <30 slides → all slides
- Presentations 30+ → first 3, middle 3, last 3

**Step 3 — Render PNGs:**
```
typst compile FILE.typ /tmp/finish-preview-{0p}.png --pages [SAMPLE]
```

**Step 4 — Visual inspection:**
- Read each PNG with the Read tool
- Apply the full visual checklist from `typst/references/visual-verification.md`:
  - Content overflow / cut off?
  - Blank half-pages?
  - Font fallback squares (missing font)?
  - Missing images / broken references?
  - Cramped text / unbalanced layout?
  - Heading hierarchy consistent?
  - Table headers repeating across pages?

**Step 5 — Record issues** for Phase 1.5 or Phase 3 fix list.

### Phase 1.5: Quick Auto-Fix Before Review

If the visual spot-check caught simple issues, fix them now so review agents start from a clean baseline.

**Scope:** Only fix issues that are:
- Clearly identified in the PNG inspection
- Fixable without design decisions (overflow, missing alt text, font fallback)

**Steps:**
1. Apply fixes:
   - Overflow → split content, adjust spacing, or reduce font size
   - Missing alt text → add generic alt descriptions
   - Font fallback → switch to documented font stack (see typst skill)
   - Blank half-pages → adjust `figure(placement: auto)` or page breaks
2. Re-compile: `typst compile FILE.typ`
3. Re-render affected sample pages to PNG
4. Visually verify fixes resolved the issue AND didn't introduce new ones
5. Max 2 mini-rounds, then proceed to Phase 2 regardless

### Phase 2: Parallel Review
- Route to `/review` with the file
- Collect all agent reports

### Phase 3: Fix Critical Issues (max 5 rounds)

**For each fix round:**

1. **Apply fixes** — priority order: Critical → Major → Minor
2. **Re-compile:** `typst compile FILE.typ`
3. **Re-render** affected pages to PNG:
   ```
   typst compile FILE.typ /tmp/finish-fix-{0p}.png --pages [AFFECTED]
   ```
4. **Visually verify** that:
   - Fixes resolved the flagged issue
   - No new visual issues were introduced
5. **If new visual issues** → add to fix list for next round

**Format-specific notes:**

**For `.qmd` files:**
- Launch quality-fixer agent with critic report
- Re-render after fixes

**For `.typ` files:**
- Apply fixes directly via Edit tool
- If typst-reviewer flags "content would benefit from visuals":
  - Call `gemini-generate-image` MCP for conceptual illustrations
  - Invoke `/image-search` for real photos/logos

**For `.py` files:**
- Apply fixes directly via Edit tool
- Re-run to verify output

### Phase 4: Commit Decision
- If score >= 80 AND zero CRITICAL issues → ready to commit
- If score < 80 → report remaining issues, do NOT auto-commit

### Phase 5: Summary Report

```markdown
# Finish Report: [Filename]

## Pipeline Summary
| Phase | Status | Details |
|-------|--------|---------|
| Compile | PASS/FAIL | [output file, warnings] |
| Visual Spot-Check | PASS/[N issues] | [issues found and auto-fixed] |
| Review | [score] | [agent count, issue count] |
| Fix | [rounds] | [issues fixed / remaining] |
| Final Score | [score] | [EXCELLENT/GOOD/NEEDS WORK/POOR] |

## Score Progression
- Initial: [score] ([N] critical, [M] major)
- After auto-fix: [score] ([N] critical, [M] major)
- Final: [score] ([N] critical, [M] major)
- Rounds: [N]

## Fixes Applied
[List of changes made]

## Remaining Issues (if any)
[List issues that could not be auto-fixed]
```

## Iteration Limits

See `typst/references/quality-gates.md` for authoritative limits.

- **Fix rounds:** max 5
- **Auto-fix mini-rounds (Phase 1.5):** max 2
- **Verification retries:** max 2 per round
- Never loop indefinitely

## Important

- For `.typ` files, visual tool invocation (`gemini-generate-image` MCP, `/image-search`) only happens when the reviewer explicitly flags missing visuals
- Always re-compile after fixes to verify they don't break anything
- Always re-render affected pages to PNG after fixes to confirm visual correctness
