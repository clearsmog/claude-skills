# Claude Code Skills

A collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that add Typst document authoring, AI image generation, web image search, mind mapping, and Google Tasks management.

Built on the [Agent Skills](https://agentskills.io) open standard.

## Quick Start

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

That's it. Skills are available immediately — the Typst skill auto-loads when you work with `.typ` files, and the slash commands (`/nano-banana`, `/mindmap`, `/image-search`) appear in your command menu.

> **Already have a `~/.claude/skills` directory?** Clone to a different path and symlink individual skill folders, or use the plugin method: `/plugins add https://github.com/clearsmog/claude-skills`

## What's Included

### Typst — Auto-loaded reference guide

Automatically activates when Claude detects `.typ` files. Provides syntax reference, common error fixes, template library, visual tool routing, and package ecosystem knowledge.

```
"Create a study guide about portfolio theory"
"Fix the compilation error in my .typ file"
"Add a comparison table to my research report"
```

Includes a component library (`@local/qk:1.0.0`) with 15 callout variants, styled tables, stat cards, badges, and document presets. Reference files for math pitfalls, layout patterns, packages, and symbols are loaded on-demand — not every invocation — keeping context lean.

---

### `/nano-banana` — AI image generation

Generate images with Google Gemini and get Typst-ready `#figure(image(...))` code.

```bash
/nano-banana "a conceptual diagram of risk parity"
/nano-banana "portfolio allocation banner" --aspect-ratio 21:9
/nano-banana "make the background lighter" --edit images/diagram.png
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--dir` | `images` | Where to save |
| `--width` | `80%` | Typst image width |
| `--edit` | — | Edit an existing image instead of creating one |
| `--resolution` | `1K` | `1K` / `2K` / `4K` |
| `--num` | `1` | Generate multiple variants |
| `--aspect-ratio` | auto | `1:1`, `16:9`, `9:16`, `3:4`, `4:3`, `21:9` |

**Models:** `gemini-3-pro` (default, best quality, ~$0.13/image) or `gemini-2.5-flash-image` (fast, ~$0.04/image).

**Requires:** `uv` + `GEMINI_API_KEY` from [Google AI Studio](https://ai.google.dev/) (paid tier).

---

### `/mindmap` — Mind map generation

Generate mind map images from a topic. Claude expands your topic into branches automatically.

```bash
/mindmap "Portfolio Theory"
/mindmap "CAPM" --typst --caption "CAPM Overview"
/mindmap "Risk Parity" --theme dark --format svg
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--dir` | `mindmaps` | Where to save |
| `--format` | `png` | `png` or `svg` |
| `--theme` | `academic` | `academic` (blue/orange), `latte` (pastel), `dark` |
| `--direction` | `side` | `side`, `right`, or `left` |
| `--typst` | — | Print Typst embedding code |

**Requires:** Node.js (`brew install node`). Dependencies auto-install on first run.

---

### `/image-search` — Web image search

Find and download real-world images, company logos, or stock photos.

```bash
/image-search "golden gate bridge sunset"
/image-search --logo "Stripe"
/image-search --stock "sustainable energy" -n 2
/image-search --url "https://example.com/chart.png" "quarterly chart"
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--logo` | off | Treat query as company name → fetch logo |
| `--stock` | off | Search Unsplash/Pexels (license-clear) |
| `--url` | — | Download from a specific URL |
| `-n` | `1` | Number of images |
| `--size` | — | `large` / `medium` / `icon` |
| `--type` | — | `photo` / `clipart` / `face` / `lineart` |

**Requires:** `uv`. Optionally set `SERPAPI_KEY` for Google Images; without it, falls back to DuckDuckGo (free, unlimited).

---

### Google Tasks — Task management

Auto-loads when you ask about tasks, to-dos, or reminders. Uses the `gtasks` CLI.

```
"Show my urgent tasks"
"Add a task to review the quarterly report by Friday"
"Mark task 3 as done"
```

**Requires:** `gtasks` CLI installed separately (not included in this repo).

## How the Skills Work Together

The Typst skill knows about the other tools and auto-invokes them when appropriate:

```
"Add an illustration of the three-legged stool analogy"   →  /nano-banana
"Add a concept map of CAPM to my study guide"             →  /mindmap
"Add the Apple logo to my stock pitch"                    →  /image-search --logo
```

The routing priority:

```
Can Typst draw it natively?      →  Typst (tables, boxes, fletcher flowcharts)
Simple chart (< 3 series)?      →  cetz-plot (native, font-matching)
Real photo or logo?              →  /image-search
Mind map or concept tree?        →  /mindmap
Structured diagram?              →  Native packages (fletcher, chronos, timeliney)
Complex chart (4+ series)?      →  matplotlib
Conceptual illustration?         →  /nano-banana
```

## Setup

All skills need [uv](https://docs.astral.sh/uv/) (`brew install uv`).

| Skill | Additional requirements |
|-------|----------------------|
| **typst** | None — works out of the box |
| **nano-banana** | `GEMINI_API_KEY` ([get one](https://ai.google.dev/), paid tier required) |
| **image-search** | `SERPAPI_KEY` optional ([get one](https://serpapi.com/)); DuckDuckGo fallback is free |
| **mindmap** | Node.js (`brew install node`) |
| **google-tasks** | `gtasks` CLI installed separately |

**Setting API keys:**

```bash
# fish
set -Ux GEMINI_API_KEY "your-key"
set -Ux SERPAPI_KEY "your-key"

# bash / zsh
export GEMINI_API_KEY="your-key"  # add to ~/.zshrc
export SERPAPI_KEY="your-key"
```

## Repository Structure

```
skills/
├── typst/
│   ├── SKILL.md                      # Behavioral core (auto-loaded)
│   └── references/
│       ├── quick-ref.md              # Syntax, errors, special characters
│       ├── component-library.md      # @local/qk:1.0.0 API reference
│       ├── tool-routing.md           # Visual tool routing + examples
│       ├── templates.md              # 7 document preambles
│       ├── common-patterns.md        # Tables, show rules, large documents
│       ├── layout-patterns.md        # Spacing, figures, curve()
│       ├── math-pitfalls.md          # Math mode edge cases
│       ├── packages.md              # Popular packages with imports
│       └── symbols.md               # sym.* arrows and symbols
├── nano-banana/
│   ├── SKILL.md                      # Slash command definition
│   └── scripts/gemini_imagen.py      # Gemini image generation
├── image-search/
│   ├── SKILL.md                      # Slash command definition
│   └── scripts/image_search.py       # Web image search & download
├── mindmap/
│   ├── SKILL.md                      # Slash command definition
│   ├── references/advanced-syntax.md # Node colors, arrows, summaries
│   └── scripts/generate_mindmap.mjs  # Mind-elixir rendering
└── google-tasks/
    └── SKILL.md                      # Google Tasks CLI reference
```

## License

MIT
