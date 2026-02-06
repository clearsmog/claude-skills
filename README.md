# Claude Code Skills

Custom skills for [Claude Code](https://claude.com/claude-code).

## Skills

| Skill | Description |
|-------|-------------|
| **typst** | Syntax guide and ecosystem reference for writing Typst (.typ) files. Covers core syntax, common errors, packages, and best practices. |

## Installation

Clone into your skills directory:

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

Or copy a specific skill:

```bash
git clone https://github.com/clearsmog/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/typst ~/.claude/skills/
rm -rf /tmp/claude-skills
```

## Structure

```
skills/
└── typst/
    ├── SKILL.md              # Core syntax, errors, quick reference
    └── references/
        ├── math-pitfalls.md  # Currency, adjacent letters, commas in math
        ├── layout-patterns.md # Compact setup, nested boxes, color themes
        ├── symbols.md        # sym.* reference
        └── packages.md       # Popular packages with imports
```

## License

MIT
