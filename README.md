# Claude Code Skills

A collection of 22 custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — document authoring, quality pipelines, AI image generation, web image search, mind mapping, and more.

Built on the [Agent Skills](https://agentskills.io) open standard.

## Quick Start

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

That's it. Skills are available immediately — the Typst skill auto-loads when you work with `.typ` files, and slash commands (`/create-document`, `/finish`, `/nano-banana`, etc.) appear in your command menu.

> **Already have a `~/.claude/skills` directory?** Clone to a different path and symlink individual skill folders, or use the plugin method: `/plugins add https://github.com/clearsmog/claude-skills`

## Skills Overview

### Document Creation

| Skill | Command | What it does |
|-------|---------|-------------|
| **create-document** | `/create-document [topic]` | One-prompt autonomous pipeline: auto-discovers materials, inherits sibling styles, drafts complete document, compiles, visually verifies, and auto-fixes |
| **compile** | `/compile [file]` | Compile any supported format (`.typ`, `.qmd`, `.py`) |
| **translate** | `/translate [file]` | Multi-format document translation (Typst <-> Quarto) |

### Quality Pipeline

| Skill | Command | What it does |
|-------|---------|-------------|
| **finish** | `/finish [file]` | Master pipeline — compile, visual verify, auto-fix, review, fix, score |
| **review** | `/review [file]` | Launch format-appropriate review agents in parallel |
| **qa** | `/qa [file]` | Adversarial audit loop: critic finds issues, fixer applies fixes (max 5 rounds) |
| **excellence** | `/excellence [file]` | Multi-agent review (visual + pedagogy + proofreading + domain) for milestones |
| **visual-audit** | `/visual-audit [file]` | Check overflow, font consistency, component fatigue, spacing |
| **pedagogy-review** | `/pedagogy-review [file]` | Narrative arc, prerequisites, worked examples, notation, pacing |
| **proofread** | `/proofread [file]` | Grammar, typos, overflow, consistency, academic writing quality |
| **devils-advocate** | `/devils-advocate [file]` | Adversarial content challenge |
| **validate-bib** | `/validate-bib` | Find missing bibliography entries and unused references |

### Visual Tools

| Skill | Command | What it does |
|-------|---------|-------------|
| **nano-banana** | `/nano-banana [prompt]` | Generate images via Google Gemini with Typst embedding code |
| **image-search** | `/image-search [query]` | Find and download real-world images, logos, or stock photos |
| **mindmap** | `/mindmap [topic]` | Generate mind map images from a topic |
| **extract-diagrams** | `/extract-diagrams [file]` | Extract CeTZ diagrams to SVG from Typst files |

### Reference & Utility

| Skill | Command | What it does |
|-------|---------|-------------|
| **typst** | *(auto-loaded)* | Syntax guide, templates, component library, visual routing, packages |
| **google-tasks** | *(auto-loaded)* | Google Tasks management via `gtasks` CLI |
| **learn** | `/learn` | Extract reusable knowledge from the current session into a persistent skill |
| **commit** | `/commit` | Git commit workflow |
| **context-status** | `/context-status` | Check context usage and session health |
| **deploy** | `/deploy` | Deployment workflow |

## How They Work Together

The skills form an integrated pipeline:

```
/create-document "study guide on portfolio theory"
        |
        v
  Phase 0: Auto-discover (scans for PDFs, .typ siblings, images)
  Phase 1: Draft (full document, qk components, auto-visuals)
  Phase 2: Compile + visual verify + auto-fix (max 3 rounds)
  Phase 3: Present summary
        |
        v
  Want deeper review?
        |
   /finish ──> /review + /qa loop ──> auto-fix ──> score
        |
   /excellence ──> 4 parallel agents ──> comprehensive report
```

### Visual Tool Routing

The Typst skill auto-invokes visual tools based on content patterns:

```
Can Typst draw it natively?      ->  Typst (tables, boxes, fletcher flowcharts)
Simple chart (< 3 series)?      ->  cetz-plot (native, font-matching)
Real photo or logo?              ->  /image-search
Mind map or concept tree?        ->  /mindmap
Structured diagram?              ->  Native packages (fletcher, chronos, timeliney)
Complex chart (4+ series)?      ->  matplotlib
Conceptual illustration?         ->  /nano-banana
```

## Slash Command Reference

### `/nano-banana` — AI image generation

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

### `/mindmap` — Mind map generation

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

### `/image-search` — Web image search

```bash
/image-search "golden gate bridge sunset"
/image-search --logo "Stripe"
/image-search --stock "sustainable energy" -n 2
/image-search --url "https://example.com/chart.png" "quarterly chart"
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--logo` | off | Treat query as company name, fetch logo |
| `--stock` | off | Search Unsplash/Pexels (license-clear) |
| `--url` | — | Download from a specific URL |
| `-n` | `1` | Number of images |
| `--size` | — | `large` / `medium` / `icon` |
| `--type` | — | `photo` / `clipart` / `face` / `lineart` |

## Setup

All skills need [uv](https://docs.astral.sh/uv/) (`brew install uv`).

| Skill | Additional requirements |
|-------|----------------------|
| **typst** | [Typst CLI](https://github.com/typst/typst) (`brew install typst`) |
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
├── create-document/SKILL.md         # Autonomous document creation pipeline
├── compile/SKILL.md                 # Format-detecting compilation
├── finish/SKILL.md                  # Master quality pipeline
├── review/SKILL.md                  # Universal file review
├── qa/SKILL.md                      # Adversarial quality audit loop
├── excellence/SKILL.md              # Multi-agent milestone review
├── visual-audit/SKILL.md            # Visual layout auditing
├── pedagogy-review/SKILL.md         # Educational content review
├── proofread/SKILL.md               # Grammar and consistency
├── devils-advocate/SKILL.md         # Adversarial content challenge
├── validate-bib/SKILL.md            # Bibliography validation
├── nano-banana/
│   ├── SKILL.md                     # AI image generation
│   └── scripts/gemini_imagen.py
├── image-search/
│   ├── SKILL.md                     # Web image search & download
│   └── scripts/image_search.py
├── mindmap/
│   ├── SKILL.md                     # Mind map generation
│   ├── references/advanced-syntax.md
│   └── scripts/generate_mindmap.mjs
├── extract-diagrams/SKILL.md        # CeTZ diagram extraction
├── typst/
│   ├── SKILL.md                     # Typst reference (auto-loaded)
│   └── references/
│       ├── quick-ref.md             # Syntax, errors, special characters
│       ├── component-library.md     # @local/qk:1.0.0 API
│       ├── tool-routing.md          # Visual tool routing + examples
│       ├── templates.md             # 10 document preambles
│       ├── common-patterns.md       # Tables, show rules, large documents
│       ├── layout-patterns.md       # Spacing, figures, curve()
│       ├── math-pitfalls.md         # Math mode edge cases
│       ├── packages.md              # Popular packages with imports
│       ├── symbols.md               # sym.* arrows and symbols
│       ├── touying-guide.md         # Presentation framework
│       ├── quality-gates.md         # Rubrics and iteration limits
│       ├── visual-verification.md   # PNG rendering and spot-checks
│       └── data-driven.md           # JSON/CSV generation patterns
├── translate/SKILL.md               # Document format translation
├── learn/SKILL.md                   # Session knowledge extraction
├── commit/SKILL.md                  # Git commit workflow
├── deploy/SKILL.md                  # Deployment workflow
├── context-status/SKILL.md          # Context health monitoring
└── google-tasks/SKILL.md            # Google Tasks CLI reference
```

## License

MIT
