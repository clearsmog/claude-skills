---
name: google-tasks
description: Manage Google Tasks via the `gtasks` CLI. Use when the user asks to view, add, update, complete, or delete tasks. Supports multiple task lists.
---

# Google Tasks CLI

`gtasks` is globally installed at `~/.local/bin/gtasks`. Use it via Bash to manage the user's Google Tasks.

Source: `~/Developer/Tools/GoogleTasks/`
Reinstall after edits: `uv tool install ~/Developer/Tools/GoogleTasks --force`

## Commands

```
gtasks lists                                          # Show all task lists
gtasks list [LIST_NAME]                               # Show tasks in a list (default if omitted)
gtasks list [LIST_NAME] --all                         # Include completed tasks
gtasks add "TITLE" [-l LIST] [-n NOTES] [-d YYYY-MM-DD]   # Create a task
gtasks update TASK_ID [-l LIST] [-t TITLE] [-n NOTES] [-d YYYY-MM-DD]  # Update a task
gtasks complete TASK_ID [TASK_ID...] [-l LIST]         # Mark task(s) done
gtasks delete TASK_ID [TASK_ID...] [-l LIST] [--yes]   # Delete task(s)
gtasks clear [-l LIST] [--yes]                        # Remove all completed tasks
```

## Task Lists

- `⏰ Urgent`
- `🎯 Important`
- `🎉 Fun`
- `✅ To-Do List`
- `Old Google Keep reminders`

## Usage Notes

- Always run `gtasks list` first to get task IDs before updating/completing/deleting.
- List names with emoji must be quoted: `gtasks list "⏰ Urgent"`
- Multiple task IDs can be passed to `complete` and `delete`.
- Always confirm with the user before deleting tasks.
- The `--yes` flag skips confirmation prompts (use only when user explicitly says to skip).
