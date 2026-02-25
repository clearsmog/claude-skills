---
name: compile
description: Compile any supported file type. Detects format (.typ, .qmd, .py) and runs appropriate build command.
argument-hint: "[filename]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile Document

Detect file format and run the appropriate build command.

## Format Detection

Determine file type from extension:
- `.typ` → Typst document
- `.qmd` → Quarto slides
- `.py` → Python script

> **Note:** For `.tex` (LaTeX/Beamer), configure compilation at project level
> with project-specific TEXINPUTS and bibtex paths.

## Compilation Commands

### For `.typ` files (Typst):

```bash
typst compile [--root ..] FILENAME.typ
```

- Use `--root` if the file imports packages from a parent directory
- Check exit code for compilation errors
- Typst compilation is single-pass (no multi-pass needed)

### For `.qmd` files (Quarto):

```bash
quarto render FILENAME.qmd
```

- Or use project-specific deploy script if available

### For `.py` files (Python):

```bash
uv run FILENAME.py
```

- Check exit code
- Verify output files were created (if applicable)

## Post-Compilation Checks

1. **Check for warnings:**
   - `.typ`: Check stderr for warnings
   - `.qmd`: Check for render warnings
   - `.py`: Check for tracebacks or warnings

2. **Verify output exists** and has non-zero file size

3. **Visual spot-check** (`.typ` files only):
   - Render sample pages to PNG: `typst compile FILE.typ /tmp/preview-{0p}.png`
   - For documents (>3 pages): render pages 1, middle, and last
   - For presentations: render all slides
   - Use `Read` tool on PNGs to visually inspect for overflow, blank pages, missing figures
   - See `typst/references/visual-verification.md` for full checklist

4. **Report results:**
   - Compilation success/failure
   - Warning count
   - Output file path and size
   - Visual check: PASS / issues noted
