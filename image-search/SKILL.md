---
name: image-search
description: Search the web for images (photos, logos, graphics) and download them with Typst embedding code. Use when the user needs real-world images, company logos, or existing graphics for documents.
allowed-tools: Bash
argument-hint: <query> [--logo] [--stock] [--url <url>] [--dir images] [-n 1] [--size large|medium|icon] [--type photo|clipart|face|lineart]
---

Parse `$ARGUMENTS` into flags for the bundled script and run it in **one** Bash call. The script handles search, download, filename generation, and Typst code output.

Flags: `query` (positional), `--logo`, `--stock`, `--url <url>`, `-d` dir, `-o` output, `-n` count, `--size`, `--type`, `--width`, `--caption "..."`

Pass `--typst` when generating images for Typst documents (the typical case). If `--output`/`-o` is not given, omit it (script auto-generates from query + dir).

Run exactly one command:

```bash
SERPAPI_KEY="$SERPAPI_KEY" uv run --script ${CLAUDE_SKILL_DIR}/scripts/image_search.py "<query>" --typst [other flags...]
```

If SERPAPI_KEY is empty in this shell, read it directly from fish universal variables (avoids shell greeting pollution): `` `printf '%b' "$(sed -n 's/.*SERPAPI_KEY://p' ~/.config/fish/fish_variables)"` ``. The same goes for `LOGO_DEV_TOKEN` and `UNSPLASH_ACCESS_KEY`: all three are fish universal variables, so a session started before one was set does not have it. Running the command through `fish -c '...'` picks them all up.

For `--stock` mode, also forward Unsplash/Pexels keys if available:
```bash
SERPAPI_KEY="$SERPAPI_KEY" UNSPLASH_ACCESS_KEY="$UNSPLASH_ACCESS_KEY" PEXELS_API_KEY="$PEXELS_API_KEY" uv run --script ${CLAUDE_SKILL_DIR}/scripts/image_search.py "<query>" --stock --typst [other flags...]
```

Print the script's stdout to the user. Done.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| Image search (default) | none | SerpAPI -> DuckDuckGo fallback -> download best match |
| Logo lookup | `--logo` | Logo.dev -> image search fallback. Logo.dev returns a 200 px square icon (the brand mark), not a wide wordmark; for a wordmark use the default mode with "<company> logo" |
| Stock photos | `--stock` | Unsplash -> Pexels -> image search fallback (license-clear) |
| Direct URL | `--url <url>` | Download image directly from URL |

## Environment

Zero API keys required — works via DuckDuckGo by default. Each key unlocks a better tier:

| Key | Purpose |
|-----|---------|
| `SERPAPI_KEY` | Google Images (best quality). Set. Free plan, 250 searches a month, shared with the `reddit` skill's search; one search per default-mode call |
| `UNSPLASH_ACCESS_KEY` | Stock photos via Unsplash. Set (demo app, 50 requests an hour). Unsplash's API terms ask for credit to the photographer and Unsplash; the script does not print the author, so add the credit by hand in anything published |
| `PEXELS_API_KEY` | Stock photos via Pexels. Not set: Pexels had paused issuing new API keys in November 2026 |
| `LOGO_DEV_TOKEN` | `--logo` via Logo.dev (publishable key). Set. Without it `--logo` goes straight to a web image search for "<name> logo", so check the result is the right company's mark |
