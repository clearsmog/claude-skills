---
name: extract-diagrams
description: Extract CeTZ diagrams to SVG from Typst files. For TikZ extraction, configure at project level.
argument-hint: "[source.typ]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Extract Diagrams to SVG

Extract diagrams from source files and convert to SVG for web use.

## Format Detection

- `.typ` source → CeTZ extraction (Typst native SVG output)
- `.tex` source → TikZ extraction (configure at project level with project-specific TEXINPUTS and paths)

## CeTZ Extraction (Typst)

Typst can output SVG directly — no intermediate PDF needed.

### Step 1: Identify CeTZ diagrams in the `.typ` file
```bash
grep -n '@preview/cetz' $ARGUMENTS
```

### Step 2: For standalone diagram files, compile directly to SVG
```bash
typst compile --format svg diagram.typ diagram.svg
```

### Step 3: For diagrams embedded in documents
- Extract the diagram code to a standalone `.typ` file
- Add necessary imports and page setup
- Compile to SVG: `typst compile --format svg standalone_diagram.typ output.svg`

### Step 4: Verify SVG files
- Read 2-3 SVG files to confirm valid SVG markup
- Confirm file sizes are reasonable

### Step 5: Report results

## Source of Truth

- **CeTZ:** Diagrams are edited in the Typst `.typ` source file
- **TikZ:** Configure extraction at project level (see project's extract-diagrams skill)
