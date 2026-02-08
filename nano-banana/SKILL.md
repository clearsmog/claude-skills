---
name: nano-banana
description: Generate images via Gemini (Google) and get Typst embedding code. Use when the user needs AI-generated illustrations, conceptual diagrams, or photorealistic images for documents.
allowed-tools: Bash
argument-hint: <prompt> [--dir images] [--width 80%] [--caption "..."] [--edit input.png] [--resolution 1K|2K|4K] [--num 1] [--aspect-ratio 16:9]
---

Parse `$ARGUMENTS` into flags for the bundled script and run it in **one** Bash call. The script handles filename generation, API key checks, and Typst code output.

Flags: `-p` prompt, `-d` dir, `--width`, `--caption "..."`, `-i` edit-image, `-r 1K|2K|4K`, `-n` count, `-m` model, `-a` aspect-ratio

Pass `--typst` when generating images for Typst documents (the typical case). If `--output`/`-o` is not given, omit it (script auto-generates from prompt + dir).

Run exactly one command:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" uv run --script {baseDir}/scripts/gemini_imagen.py -p "<prompt>" --typst [other flags...]
```

If GEMINI_API_KEY is empty in this shell, read it from fish: `` `fish -c 'set fish_greeting; echo $GEMINI_API_KEY'` ``.

Print the script's stdout to the user. Done.

## Prompt construction

When generating the `-p` prompt from the user's description, follow these rules:

1. **Describe scenes, not keywords** — "A three-legged wooden stool on a white background, each leg labeled..." beats "stool, risk parity, three legs"
2. **Specify style explicitly** — Include art style, lighting, and composition (e.g., "flat vector illustration", "isometric 3D render", "watercolor sketch")
3. **Use white backgrounds for documents** — Add "on a clean white background" for images that will be embedded in Typst documents
4. **Describe spatial layout** — "On the left... on the right..." helps Gemini compose multi-element scenes
5. **Don't rely on text labels** — Gemini often misspells text in images; describe the concept visually instead of asking for labeled diagrams

## Options

Aspect ratios (`-a`): `1:1` square, `16:9` landscape, `9:16` portrait, `3:4`, `4:3`, `21:9` banner. Omit for model default.

Models: default = Gemini 3 Pro (quality, 4K). `-m gemini-2.5-flash-image` = fast/cheap drafts.
