---
name: excellence
description: Multi-agent document review (visual, pedagogy, proofreading, domain). Use for comprehensive quality check before milestones. Works with any supported file type.
argument-hint: "[filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
context: fork
---

# Excellence Review

Run a comprehensive multi-dimensional review. Multiple agents analyze the file independently, then results are synthesized.

## Format Detection

Determine file type from extension:
- `.tex` → Beamer LaTeX slides
- `.qmd` → Quarto RevealJS slides
- `.typ` → Typst document (slides, docs, guides, CVs)
- `.py` → Python script

For `.typ` files, also detect document type from content.

## Agent Dispatch by File Type

### For `.tex` files:
| Agent | What It Checks | Report |
|-------|---------------|--------|
| document-auditor | Overflow, font consistency, spacing, images | `[FILE]_visual_audit.md` |
| pedagogy-reviewer | 13 patterns, narrative, pacing, notation | `[FILE]_pedagogy_report.md` |
| proofreader | Grammar, typos, consistency, academic quality | `[FILE]_report.md` |
| diagram-reviewer | Label overlaps, geometric accuracy (only if TikZ present) | `[FILE]_tikz_review.md` |
| domain-reviewer | Field-specific substance (optional) | `[FILE]_substance_review.md` |

### For `.qmd` files:
| Agent | What It Checks | Report |
|-------|---------------|--------|
| document-auditor | Overflow, font consistency, spacing, images | `[FILE]_visual_audit.md` |
| pedagogy-reviewer | 13 patterns, narrative, pacing | `[FILE]_pedagogy_report.md` |
| proofreader | Grammar, typos, consistency | `[FILE]_report.md` |
| quality-critic | Adversarial comparison vs .tex (only if sibling exists) | `[FILE]_parity_report.md` |

### For `.typ` files:
| Agent | What It Checks | Report |
|-------|---------------|--------|
| typst-reviewer | Compilation, smart defaults, component usage, visual routing | `[FILE]_typst_review.md` |
| document-auditor | Overflow, typography, component fatigue, spacing | `[FILE]_visual_audit.md` |
| proofreader | Grammar, typos, consistency | `[FILE]_report.md` |
| pedagogy-reviewer | Narrative, pacing, notation (only if slides detected) | `[FILE]_pedagogy_report.md` |

### For `.py` files:
| Agent | What It Checks | Report |
|-------|---------------|--------|
| python-pro (subagent) | Code quality, style, type safety, patterns | `[FILE]_python_review.md` |
| domain-reviewer | Field-specific correctness (optional) | `[FILE]_substance_review.md` |

## Steps

1. **Parse `$ARGUMENTS`** for the filename, resolve path
2. **Detect format** from extension
3. **Launch all applicable agents in parallel** per dispatch table
4. **Collect all reports** from `quality_reports/`
5. **Synthesize combined summary**

## Combined Summary Format

```markdown
# Excellence Review: [Filename]

## Overall Quality Score: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Agent | Critical | Major | Minor |
|-----------|-------|----------|-------|-------|
| Visual/Layout | [auditor] | N | N | N |
| Content Quality | [reviewer] | N | N | N |
| Proofreading | proofreader | N | N | N |
| [Additional] | [agent] | N | N | N |

### Critical Issues (Immediate Action Required)
### Major Issues (Next Revision)
### Recommended Next Steps
```

## Quality Score Rubric

See `typst/references/quality-gates.md` for the authoritative score rubric and severity definitions.
