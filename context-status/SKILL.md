---
name: context-status
description: |
  Show current context status and session health.
  Use to check how much context has been used, whether auto-compact is
  approaching, and what state will be preserved.
author: Claude Code Academic Workflow
version: 1.0.0
---

# /context-status — Check Session Health

Show the current session status including context usage estimate, active plan,
and preservation state.

## What This Skill Shows

1. **Context usage estimate** — Approximate % of context window used
2. **Active plan** — Current plan file and status
3. **Session log** — Most recent session log
4. **Preservation state** — What will survive compaction

## Workflow

### Step 1: Check Context Monitor Cache

Read the context monitor cache to get the current estimate:

```bash
cat ~/.claude/sessions/*/context-monitor-cache.json 2>/dev/null | head -20
```

### Step 2: Find Active Plan

Search common plan locations:

```bash
ls -lt quality_reports/plans/*.md .planning/*.md plans/*.md 2>/dev/null | head -3
```

### Step 3: Find Session Log

```bash
ls -lt quality_reports/session_logs/*.md .planning/logs/*.md session_logs/*.md 2>/dev/null | head -1
```

### Step 4: Report Status

Format the output:

```
Session Status
-----------------------------------
Context Usage:  ~XX% (estimated)
Auto-compact:   [approaching | not imminent]

Active Plan
File:   [plan path]
Status: [draft | approved | in_progress | completed]
Task:   [current unchecked task or "none"]

Session Log
File:   [log path]

Preservation Check
  - Pre-compact hook: [configured | missing]
  - Post-compact restore: [configured | missing]
  - Session state will be saved before compaction
```

## Notes

- Context % is an estimate based on tool call count
- Actual compaction is triggered by Claude Code automatically
- All important state is saved to disk (plans, logs, MEMORY.md)
