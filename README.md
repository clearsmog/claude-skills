# Claude Code Skills

Custom skills for [Claude Code](https://claude.com/claude-code), following the [Agent Skills](https://agentskills.io) open standard.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| **typst** | Auto-loaded | Syntax guide, common errors, packages, and best practices for Typst (.typ) files. Auto-loaded when editing `.typ` documents. |
| **nano-banana** | Slash command | Generate images via Google Gemini and get ready-to-paste Typst `#figure(image(...))` code. Invoke with `/nano-banana`. |
| **mindmap** | Slash command | Generate mind map images using mind-elixir. Produces PNG or SVG from plaintext input. Invoke with `/mindmap`. |
| **image-search** | Slash command | Search the web for images (photos, logos, stock photos) and download them with Typst embedding code. Invoke with `/image-search`. |

## Installation

### Method 1: Clone (recommended)

Clone directly into your Claude Code skills directory:

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

All skills are immediately available. The `typst` skill auto-loads when you work with `.typ` files, and `/nano-banana` and `/mindmap` appear in the slash command menu.

### Method 2: Plugin marketplace

Register this repo as a Claude Code plugin:

```
/plugins add https://github.com/clearsmog/claude-skills
```

Skills will be namespaced as `claude-skills:typst`, `claude-skills:nano-banana`, etc.

## Usage

### typst

Automatically loaded when Claude detects `.typ` files. Provides syntax reference, common error fixes, and ecosystem knowledge. No manual invocation needed.

```
# Claude auto-loads the skill when you ask:
"Create a Typst document with a comparison table"
"Fix the compilation error in my .typ file"
```

### nano-banana

Generate AI images with one command and get Typst-ready embedding code.

```bash
# Basic usage
/nano-banana "a conceptual diagram of risk parity"

# With options
/nano-banana "Black-Litterman Bayesian update flowchart" --dir charts --width 90%

# With aspect ratio
/nano-banana "portfolio allocation banner" --aspect-ratio 21:9

# Edit an existing image
/nano-banana "make the background lighter" --edit images/diagram.png

# Multiple outputs at high resolution
/nano-banana "abstract portfolio visualization" --num 3 --resolution 4K
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--dir` | `images` | Output directory |
| `--width` | `80%` | Typst image width |
| `--caption` | auto | Figure caption |
| `--edit` | — | Input image for editing |
| `--resolution` | `1K` | Output resolution (`1K`/`2K`/`4K`) |
| `--num` | `1` | Number of images to generate |
| `--aspect-ratio` | model default | Aspect ratio (`1:1`, `16:9`, `9:16`, `3:4`, `4:3`, `21:9`) |
| `--model` | `gemini-3-pro` | Gemini model ID |

**Output:** The command generates the image and prints Typst code:

```typst
#figure(
  image("charts/2026-02-07-risk-parity-stool.png", width: 80%),
  caption: [Risk Parity: Equal Risk Contribution],
)
```

**Available models:**

| Model | Cost/image | Notes |
|-------|-----------|-------|
| `gemini-3-pro` (default) | ~$0.13 | Best quality, supports 4K resolution |
| `gemini-2.5-flash-image` | ~$0.04 | Fast, good for quick iterations |

### mindmap

Generate mind map images from a topic or structured content.

```bash
# From a topic (Claude expands into branches)
/mindmap "Portfolio Theory"

# With Typst embedding code
/mindmap "CAPM" --typst --caption "CAPM Overview"

# Custom theme and format
/mindmap "Risk Parity" --theme dark --format svg

# Custom direction
/mindmap "Diversification" --direction right
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--dir` | `mindmaps` | Output directory |
| `--format` | `png` | Output format (`png`/`svg`) |
| `--theme` | `academic` | Color theme (`academic`/`latte`/`dark`) |
| `--direction` | `side` | Layout direction (`side`/`right`/`left`) |
| `--typst` | — | Print Typst `#figure(image(...))` code |
| `--caption` | — | Figure caption |

### image-search

Search the web for real-world images, company logos, or stock photos and download them.

```bash
# Search for images (SerpAPI -> DuckDuckGo fallback)
/image-search "golden gate bridge sunset"

# Company logo
/image-search --logo "Stripe"

# Logo with custom width
/image-search --logo "Goldman Sachs" --width 40%

# Stock photos (license-clear, Unsplash/Pexels)
/image-search --stock "sustainable energy" -n 2

# Download from a specific URL
/image-search --url "https://example.com/chart.png" "quarterly chart"

# With size/type filters (SerpAPI only)
/image-search "electric vehicles" --size large --type photo -n 3
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--logo` | off | Logo mode — treat query as company/domain |
| `--stock` | off | Stock photo mode (Unsplash/Pexels) |
| `--url` | — | Direct URL download mode |
| `--dir` | `images` | Output directory |
| `-n` | `1` | Number of images to download |
| `--size` | — | Size filter: `large`/`medium`/`icon` |
| `--type` | — | Type filter: `photo`/`clipart`/`face`/`lineart` |
| `--width` | `80%` | Typst image width |
| `--caption` | auto | Typst figure caption |

### Skill integration

The typst skill knows about both `/nano-banana` and `/mindmap` and will auto-invoke them when appropriate:

```
# Auto-invokes /nano-banana
"Add an illustration of the three-legged stool analogy to my risk parity document"

# Auto-invokes /mindmap
"Add a concept map of CAPM to my week 3 flowchart"

# Auto-invokes /image-search
"Add the Apple logo to my stock pitch"
"Find a photo of the Golden Gate Bridge for the report"
```

Claude uses decision tables to route requests to the right tool:

| Request type | Routed to |
|-------------|-----------|
| Conceptual illustrations, metaphors | `/nano-banana` |
| Photorealistic or decorative images | `/nano-banana` |
| Mind maps, concept maps, topic trees | `/mindmap` |
| Company logos, brand marks | `/image-search --logo` |
| Real-world photos, web graphics | `/image-search` |
| Stock photos (license-clear) | `/image-search --stock` |
| Flowcharts, tables, boxes | Typst native |
| Data-driven charts | matplotlib |

## Setup

### nano-banana requirements

- **uv** — `brew install uv`
- **GEMINI_API_KEY** — get one at https://ai.google.dev/

```bash
# fish
set -Ux GEMINI_API_KEY "your-key"

# bash/zsh
echo 'export GEMINI_API_KEY="your-key"' >> ~/.zshrc
```

Image generation requires a paid Gemini API tier (no free quota for image models).

### image-search requirements

- **uv** — `brew install uv`
- **SERPAPI_KEY** (optional) — get one at https://serpapi.com/

```bash
# fish
set -Ux SERPAPI_KEY "your-key"

# bash/zsh
echo 'export SERPAPI_KEY="your-key"' >> ~/.zshrc
```

Without a key, image search falls back to DuckDuckGo (free, unlimited). For stock photo mode, optionally set `UNSPLASH_ACCESS_KEY` and/or `PEXELS_API_KEY`.

### mindmap requirements

- **Node.js** — `brew install node`
- Dependencies install automatically on first `/mindmap` invocation.

## Structure

```
skills/
├── typst/
│   ├── SKILL.md                   # Typst syntax guide (auto-loaded)
│   └── references/
│       ├── math-pitfalls.md       # Math mode edge cases
│       ├── layout-patterns.md     # Spacing, boxes, colors, curve()
│       ├── common-patterns.md     # Tables, templates, bibliography
│       ├── symbols.md             # sym.* arrows and symbols
│       └── packages.md            # Popular packages
├── nano-banana/
│   ├── SKILL.md                   # Slash command definition
│   └── scripts/
│       └── gemini_imagen.py       # Gemini image generation
├── image-search/
│   ├── SKILL.md                   # Slash command definition
│   └── scripts/
│       └── image_search.py        # Web image search & download
└── mindmap/
    ├── SKILL.md                   # Slash command definition
    ├── references/
    │   └── advanced-syntax.md     # Node colors, arrows, summaries
    └── scripts/
        └── generate_mindmap.mjs   # Mind-elixir rendering
```

Reference files are loaded on-demand (not on every invocation), keeping SKILL.md context lean.

## License

MIT
