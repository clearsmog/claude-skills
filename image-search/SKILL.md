---
name: image-search
description: Search the web for images (photos, logos, graphics) and download them with Typst embedding code. Use when the user needs real-world images, company logos, or existing graphics for documents.
allowed-tools: Bash
argument-hint: <query> [--logo] [--stock] [--url <url>] [--dir images] [-n 1] [--size large|medium|icon] [--type photo|clipart|face|lineart]
---

Parse `$ARGUMENTS` into flags for the bundled script and run it in **one** Bash call. The script handles search, download, filename generation, and Typst code output.

Flags: `query` (positional), `--logo`, `--stock`, `--url <url>`, `-d` dir, `-o` output, `-n` count, `--size`, `--type`, `--width`, `--caption "..."`

Always pass `--typst`. If `--output`/`-o` is not given, omit it (script auto-generates from query + dir).

Run exactly one command:

```bash
SERPAPI_KEY="$SERPAPI_KEY" uv run --script {baseDir}/scripts/image_search.py "<query>" --typst [other flags...]
```

If SERPAPI_KEY is empty in this shell, read it from fish: `` `fish -c 'set fish_greeting; echo $SERPAPI_KEY'` `` (suppress greeting to avoid ANSI pollution).

For `--stock` mode, also forward Unsplash/Pexels keys if available:
```bash
SERPAPI_KEY="$SERPAPI_KEY" UNSPLASH_ACCESS_KEY="$UNSPLASH_ACCESS_KEY" PEXELS_API_KEY="$PEXELS_API_KEY" uv run --script {baseDir}/scripts/image_search.py "<query>" --stock --typst [other flags...]
```

Print the script's stdout to the user. Done.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| Image search (default) | none | SerpAPI -> DuckDuckGo fallback -> download best match |
| Logo lookup | `--logo` | Logo.dev -> image search fallback |
| Stock photos | `--stock` | Unsplash -> Pexels -> image search fallback (license-clear) |
| Direct URL | `--url <url>` | Download image directly from URL |

## Environment

Zero API keys required — works via DuckDuckGo by default. Each key unlocks a better tier:

| Key | Purpose |
|-----|---------|
| `SERPAPI_KEY` | Google Images (best quality) |
| `UNSPLASH_ACCESS_KEY` | Stock photos via Unsplash |
| `PEXELS_API_KEY` | Stock photos via Pexels |
