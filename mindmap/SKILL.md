---
name: mindmap
description: Generate mind map images using mind-elixir. Produces PNG or SVG files from plaintext input. Use when the user needs a mind map, concept map, or topic overview diagram.
allowed-tools: Bash, Write, Read
argument-hint: <topic or "plaintext content"> [--dir mindmaps] [--format png|svg] [--theme academic|latte|dark] [--direction side|right|left] [--typst] [--caption "..."]
---

Generate a mind map image from a topic or plaintext mind map content.

## Setup (first run only)

If `{baseDir}/scripts/node_modules` does not exist, run:

```bash
cd {baseDir}/scripts && npm install
```

## Workflow

1. **Generate plaintext mind map content** from `$ARGUMENTS`. If the user provides a short topic, expand it into a full mind map tree (3-4 branches, 3-5 leaves each). If the user provides plaintext content, use it directly.

2. **Write the plaintext** to a temp file at `/tmp/mindmap-input.txt`.

3. **Run the script** to render the mind map:

```bash
node {baseDir}/scripts/generate_mindmap.mjs -i /tmp/mindmap-input.txt -o "<output-path>" [flags...]
```

4. **Print the script's stdout** to the user. Open the output file with `open <path>`.

## Plaintext format

Use mind-elixir plaintext: a markdown-style indented list. Two-space indentation per level.

```
- Root Topic
  - Branch 1
    - Leaf 1a
    - Leaf 1b
    - Leaf 1c
  - Branch 2
    - Leaf 2a
    - Leaf 2b
  - Branch 3
    - Leaf 3a
    - Leaf 3b
    - Leaf 3c
```

Keep topics **short** (2-5 words per node). Aim for 3-5 branches, 3-5 leaves per branch, max 3 levels deep.

For node colors, arrows, and summaries, see [references/advanced-syntax.md](references/advanced-syntax.md).

## Flags

`-i` input, `-o` output, `-f png|svg`, `-t academic|latte|dark`, `-d side|right|left`, `-s` scale (default 3), `--typst`, `--caption "..."`, `--typst-width 90%`

Defaults: `--dir mindmaps/`, auto-generates filename from topic.

## Example invocation

For `/mindmap "Portfolio Theory"`:

```bash
node {baseDir}/scripts/generate_mindmap.mjs \
  -i /tmp/mindmap-input.txt \
  -o "mindmaps/portfolio-theory.png"
```
