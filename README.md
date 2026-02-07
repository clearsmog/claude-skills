# Claude Code Skills

Custom skills for [Claude Code](https://claude.com/claude-code).

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| **typst** | Auto-loaded | Syntax guide and ecosystem reference for writing Typst (.typ) files. Covers core syntax, common errors, packages, and best practices. |
| **nano-banana** | Slash command | Generate images via Gemini (Google) and get Typst `#figure(image(...))` embedding code. |

## Installation

Clone into your skills directory:

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

### nano-banana setup

The nano-banana skill requires additional setup since it's a slash command with a Python script:

```bash
# 1. Copy the command definition
cp ~/.claude/skills/nano-banana/COMMAND.md ~/.claude/commands/nano-banana.md

# 2. Copy the script
cp ~/.claude/skills/nano-banana/scripts/gemini_imagen.py ~/.claude/scripts/gemini_imagen.py

# 3. Set your Gemini API key (get one at https://ai.google.dev/)
# fish:
set -Ux GEMINI_API_KEY "your-key"
# bash/zsh:
echo 'export GEMINI_API_KEY="your-key"' >> ~/.zshrc
```

Then use it: `/nano-banana "a conceptual diagram of risk parity" --dir images --width 80%`

### Requirements

- `uv` (Python package manager) — `brew install uv`
- `GEMINI_API_KEY` environment variable
- Gemini API paid tier recommended (image generation has no free quota)

## Structure

```
skills/
├── typst/
│   ├── SKILL.md              # Core syntax, errors, quick reference
│   └── references/
│       ├── math-pitfalls.md
│       ├── layout-patterns.md
│       ├── symbols.md
│       └── packages.md
└── nano-banana/
    ├── COMMAND.md             # Slash command definition (/nano-banana)
    └── scripts/
        └── gemini_imagen.py   # Gemini image generation script
```

## License

MIT
