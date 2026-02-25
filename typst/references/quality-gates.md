# Quality Gates (Single Source of Truth)

> All quality skills reference this file. Do NOT duplicate these tables elsewhere.

---

## Score Rubric

| Score | Critical | Major | Meaning |
|-------|----------|-------|---------|
| EXCELLENT | 0-2 | 0-5 | Ready to ship |
| GOOD | 3-5 | 6-15 | Minor refinements |
| NEEDS WORK | 6-10 | 16-30 | Significant revision |
| POOR | 11+ | 31+ | Major restructuring |

---

## Commit Threshold

- Score >= 80 AND zero CRITICAL issues → ready to commit
- Score < 80 → report remaining issues, do NOT auto-commit

---

## Iteration Limits

| Loop | Max Rounds |
|------|-----------|
| Main review-fix loop | 5 |
| Critic-fixer sub-loop | 5 |
| Verification retries | 2 |

Never loop indefinitely.

---

## Verdict Criteria

| Verdict | Condition |
|---------|-----------|
| APPROVED | Score EXCELLENT or GOOD, zero CRITICAL |
| NEEDS REVISION | Score NEEDS WORK, or has CRITICAL issues that are fixable |
| REJECTED | Score POOR, or structural issues requiring major rework |

---

## Review Agent Dispatch Table

The ONE authoritative routing table for file-type → agents:

| Extension | Agents (parallel) | Condition |
|-----------|-------------------|-----------|
| `.typ` | typst-reviewer + proofreader + document-auditor | Always |
| `.typ` | + pedagogy-reviewer | If slide format detected |
| `.tex` | proofreader + document-auditor + pedagogy-reviewer | Always |
| `.tex` | + diagram-reviewer | If TikZ found (`\begin{tikzpicture}`) |
| `.qmd` | proofreader + document-auditor | Always |
| `.qmd` | + quality-critic | If `.tex` sibling exists |
| `.py` | python-pro (subagent) | Always |
| `.md` | proofreader | Always |

---

## Severity Definitions

| Severity | Definition | Examples |
|----------|-----------|----------|
| **CRITICAL** | Blocks publication; must fix | Compilation error, missing content, broken references, factual error |
| **MAJOR** | Significant quality issue | Overflow, inconsistent formatting, missing visuals, weak structure |
| **MINOR** | Polish item | Typo, spacing tweak, style inconsistency, optional improvement |
