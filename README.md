# Claude Code Skills

Custom skills for [Claude Code](https://claude.com/claude-code), following the [Agent Skills](https://agentskills.io) open standard.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| **typst** | Auto-loaded | Syntax guide, common errors, packages, and best practices for Typst (.typ) files. Auto-loaded when editing `.typ` documents. |
| **nano-banana** | Slash command | Generate images via Google Gemini and get ready-to-paste Typst `#figure(image(...))` code. Invoke with `/nano-banana`. |

## Installation

### Method 1: Clone (recommended)

Clone directly into your Claude Code skills directory:

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

All skills are immediately available. The `typst` skill auto-loads when you work with `.typ` files, and `/nano-banana` appears in the slash command menu.

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

# Edit an existing image
/nano-banana "make the background lighter" --edit images/diagram.png

# Multiple outputs
/nano-banana "abstract portfolio visualization" --num 3

# Custom resolution (for gemini-3-pro model)
/nano-banana "detailed financial flowchart" --resolution 2K
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
| `--model` | `gemini-3-pro-image-preview` | Gemini model ID |

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
| `gemini-3-pro-image-preview` | ~$0.13 | Best quality, supports resolution control (default) |
| `gemini-2.5-flash-image` | ~$0.04 | Fast, good for quick iterations |

### typst + nano-banana integration

The typst skill knows about `/nano-banana` and will auto-invoke it when you ask for conceptual illustrations that Typst can't draw natively. For example:

```
"Add an illustration of the three-legged stool analogy to my risk parity document"
```

Claude will generate the image via Gemini and embed it in your `.typ` file automatically.

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

## Structure

```
skills/
├── typst/
│   ├── SKILL.md              # Typst syntax guide and reference
│   └── references/
│       ├── math-pitfalls.md
│       ├── layout-patterns.md
│       ├── symbols.md
│       └── packages.md
└── nano-banana/
    ├── SKILL.md              # Slash command definition
    └── scripts/
        └── gemini_imagen.py  # Gemini image generation script
```

## License

MIT
