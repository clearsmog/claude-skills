---
name: deploy
description: Render and deploy documents to output directory for hosting. Supports Quarto slides and Typst PDFs.
disable-model-invocation: true
argument-hint: "[target or 'all']"
allowed-tools: ["Read", "Bash"]
---

# Deploy Documents

Render and deploy documents to output directory for GitHub Pages or other hosting.

## Steps

### For Quarto Slides (.qmd)

1. **Render:**
   - `quarto render FILENAME.qmd`
   - Or use project-specific deploy script if available

2. **Verify deployment:**
   - Check that HTML files exist in output directory
   - Check that `_files/` directories were copied (RevealJS assets)
   - Check that referenced figures/images are accessible

3. **Verify interactive charts** (if applicable):
   - Grep rendered HTML for interactive widget count

4. **Open in browser** for visual verification

### For Typst Documents (.typ)

1. **Compile to PDF:** `typst compile file.typ`
2. **Copy PDF to output directory:** `cp file.pdf docs/` or project-specific output path
3. **For HTML output** (if using typst-preview or conversion): follow project-specific pipeline
4. **Verify PDF** was generated with non-zero file size

### For LaTeX (.tex)

> Configure at project level — compilation requires project-specific TEXINPUTS and paths.

6. **Report results** to the user
