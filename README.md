# Claude Code Skills

A collection of custom skills for [Claude Code](https://claude.com/claude-code), Anthropic's official CLI for Claude.

## Skills

| Skill | Description |
|-------|-------------|
| **notebooklm** | Query Google NotebookLM notebooks directly from Claude Code for source-grounded, citation-backed answers. Features browser automation, library management, and persistent auth. |
| **github-to-skills** | Automated factory for converting GitHub repositories into specialized AI skills. Fetches repo details, generates standardized skill structure with metadata for lifecycle management. |
| **skill-manager** | Lifecycle manager for GitHub-based skills. Batch scan skills directory, check for updates on GitHub, and perform guided upgrades. |
| **skill-evolution-manager** | Captures learnings from conversations to evolve skills over time. Extracts successful solutions, fixes, and preferences into persistent skill improvements. |
| **typst** | Syntax guide and ecosystem reference for writing Typst (.typ) files. Covers core syntax, common errors, packages, and best practices. |

## Installation

### From Plugin Marketplace

Add this repository to Claude Code using the marketplace command:

```
/plugin marketplace add clearsmog/claude-skills
```

### Manual Installation

Clone and merge into your existing skills directory:

```bash
# Clone to a temporary location
git clone https://github.com/clearsmog/claude-skills.git /tmp/claude-skills

# Copy desired skills (won't overwrite your existing skills)
cp -r /tmp/claude-skills/notebooklm ~/.claude/skills/
cp -r /tmp/claude-skills/skill-manager ~/.claude/skills/
cp -r /tmp/claude-skills/typst ~/.claude/skills/

# Cleanup
rm -rf /tmp/claude-skills
```

Or if starting fresh:

```bash
git clone https://github.com/clearsmog/claude-skills.git ~/.claude/skills
```

## Usage

Skills are automatically available in Claude Code. Trigger them by:

- Mentioning the skill name (e.g., "query my NotebookLM")
- Using slash commands (e.g., `/skill-manager check`)
- Providing relevant context (e.g., sharing a GitHub URL for `github-to-skills`)

## Structure

```
skills/
├── notebooklm/           # NotebookLM integration
│   ├── SKILL.md          # Main skill definition
│   ├── scripts/          # Automation scripts
│   └── references/       # Extended documentation
├── github-to-skills/     # GitHub repo to skill converter
├── skill-manager/        # Skill lifecycle management
├── skill-evolution-manager/  # Skill learning & evolution
└── typst/                # Typst syntax guide
    └── SKILL.md
```

## Contributing

Contributions welcome! Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests for new skills

## License

MIT
