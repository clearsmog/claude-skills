---
name: qa
description: Adversarial quality audit loop. Critic finds issues, fixer applies fixes, loops until APPROVED (max 5 rounds). Works with any document format.
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Adversarial Quality Audit Workflow

Iterative critic/fixer loop for any supported document format.

## Format Detection

Determine file type from extension:
- `.tex` → Beamer LaTeX slides
- `.qmd` → Quarto RevealJS slides (compare vs `.tex` benchmark if it exists)
- `.typ` → Typst document (audit against quality standards)

## Workflow

```
Phase 0: Pre-flight → Phase 1: Critic audit → Phase 2: Fixer → Phase 3: Re-audit → Loop until APPROVED (max 5 rounds)
```

## Hard Gates (Non-Negotiable, Universal)

| Gate | .tex | .qmd | .typ |
|------|------|------|------|
| **Overflow** | No overfull hbox > 10pt | No content cut off | No content exceeds page |
| **Content Quality** | No undefined citations | Interactive >= static plots | All imports resolve |
| **Typography** | Consistent formatting | Notation fidelity | Font consistency |

## Phase 0: Pre-flight

### For `.qmd` files:
1. Locate Beamer (.tex/.pdf) and Quarto (.qmd/.html) files
2. Check freshness (re-render if QMD newer than HTML)
3. Verify TikZ SVGs if applicable

### For `.typ` files:
1. Locate the file, check it compiles
2. Detect document type (slides, CV, guide, essay, report)

### For `.tex` files:
1. Locate the file, verify it compiles
2. Check for auxiliary files (.aux, .bbl)

## Phase 1: Initial Audit

Launch the `quality-critic` agent to audit the document. Report saved to `quality_reports/[FILENAME]_qa_critic_round1.md`.

## Phase 2: Fix Cycle

If not APPROVED, launch `quality-fixer` agent to apply fixes (Critical → Major → Minor), re-compile, and verify.

## Phase 3: Re-Audit

Re-launch critic to verify fixes. Loop back to Phase 2 if needed.

## Iteration Limits

Max 5 fix rounds. After that, escalate to user with remaining issues.

## Final Report

Save to `quality_reports/[FILENAME]_qa_final.md` with:
- Hard gate status
- Iteration summary (rounds, issues fixed per round)
- Remaining issues (if any)
- Final verdict

## Quality Gates

See `typst/references/quality-gates.md` for score rubric, commit thresholds, and severity definitions.
