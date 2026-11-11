---
name: verify
description: Verify that changed work actually runs and renders before a commit or before calling a task done. Compiles .typ/.qmd/.py/.R, runs the project's tests and build, and click-tests frontend changes in Chrome. Use before committing, when asked to verify or check work, or when finishing any change to compilable or visual files.
allowed-tools: ["Read", "Bash", "Glob", "Grep", "Skill"]
---

# Verify

Prove the change works. A passing type-check is not proof.

## 1. Find what changed

In a git repo: `git diff --name-only HEAD` plus `git diff --name-only --cached`, plus untracked files from `git status --porcelain`. Outside git, verify the files touched in this session.

## 2. Check each file type

| Changed | Check |
|---|---|
| `.typ` | `typst compile` the entry file with the project's flags (`--root`, `--font-path`); any warning counts. Then render to PNG in a temp directory, `typst compile --format png --ppi 110 <file> "$(mktemp -d)/p-{0p}.png"`, and Read the pages touched (slides: every slide; long documents: also the first and last page) for overflow, blank pages and missing figures. Full checklist: the `typst` skill's `references/visual-verification.md` |
| `.qmd` | `quarto render` the file |
| `.py` | `uv run python -I -m py_compile <file>`; when the script writes output files, confirm they exist and are not empty; run `uv run pytest` if the project has tests; run the script itself if it is an entry point and safe to run |
| `.R` | `Rscript <file>` when it is a standalone script |
| `.html`, `.tsx`, `.jsx`, `.css`, `.vue` | `bun run build` and `bun run test` if defined (`biome check` when `biome.json` exists); then open the page with Claude in Chrome (load the `claude-in-chrome` skill) and click through the changed flow, checking the console for errors |
| `.md` with images or diagrams | render it in the target viewer and confirm the images load |
| `.xlsx` | recalculate and scan for `#REF!`, `#DIV/0!`, `#VALUE!` |

Use the project's own commands when it defines them (`package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`), in preference to the defaults above.

## 3. Report

One line per check: what ran and whether it passed. On a failure, show the relevant output and do not commit. Fix it, or stop and say what is broken. Never report a check as passed when it was skipped; say it was skipped and why.
