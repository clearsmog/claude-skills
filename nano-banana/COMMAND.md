---
allowed-tools: Bash
argument-hint: <prompt> [--dir images] [--width 80%] [--caption "..."] [--edit input.png] [--resolution 1K|2K|4K] [--num 1]
description: Generate images via Gemini and get Typst embedding code
---

Parse `$ARGUMENTS` into flags for `~/.claude/scripts/gemini_imagen.py` and run it in **one** Bash call. The script handles filename generation, API key checks, and Typst code output.

**Argument mapping:**

| User flag | Script flag |
|-----------|-------------|
| `"prompt text"` or `-p` | `-p` |
| `--dir charts` | `-d charts` |
| `--width 85%` | `--width 85%` |
| `--caption "My Caption"` | `--caption "My Caption"` |
| `--edit input.png` | `-i input.png` |
| `--resolution 2K` | `-r 2K` |
| `--num 3` | `-n 3` |
| `--model gemini-2.5-flash-image` | `-m gemini-2.5-flash-image` |

Always pass `--typst`. If `--output`/`-o` is not given, omit it (script auto-generates from prompt + dir).

Run exactly one command:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" uv run --script ~/.claude/scripts/gemini_imagen.py -p "<prompt>" --typst [other flags...]
```

If GEMINI_API_KEY is empty in this shell, read it from fish: ``fish -c 'echo $GEMINI_API_KEY'``.

Print the script's stdout to the user. Done.
