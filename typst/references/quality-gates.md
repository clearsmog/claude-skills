# Quality Gates

Severity definitions and verdict rules for document reviews. The `doc-review` skill cites this file; which reviewers run for which file type is in that skill's "Routing Table".

## Severity Definitions

| Severity | Definition | Examples |
|----------|-----------|----------|
| **CRITICAL** | Blocks publication; must fix | Compilation error, missing content, broken references, factual error |
| **MAJOR** | Significant quality issue; fix before the document is called finished | Overflow, inconsistent formatting, missing visuals, weak structure |
| **MINOR** | Polish item; optional | Typo, spacing tweak, style inconsistency |

## Verdict Rules

The verdict follows from the findings, not from a score.

| Verdict | Condition |
|---------|-----------|
| APPROVED | Zero CRITICAL and zero MAJOR. MINOR findings may remain |
| NEEDS REVISION | One or more CRITICAL or MAJOR findings that edits to the existing document can fix |
| REJECTED | The structure itself has to be redone, so fixing findings one by one would not be enough. Say what has to be rebuilt |

- Any CRITICAL finding means the document is not ready to publish or commit, whatever else is true.
- The overall verdict of a multi-reviewer run is the worst single verdict: REJECTED if any reviewer rejects; otherwise NEEDS REVISION if any CRITICAL or MAJOR finding exists across all reviewers; otherwise APPROVED.
- Report the CRITICAL / MAJOR / MINOR counts next to the verdict.
