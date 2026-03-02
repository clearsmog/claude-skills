---
paths:
  - "**/*.typ"
---
# Typst

## Diagrams
- Use native Typst packages (fletcher, chronos, timeliney) instead of Mermaid.
- NEVER use Python (graphviz, mermaid, matplotlib) for flowcharts — always fletcher.

## Compile After Editing
- After any `.typ` edit, run `typst compile <file>` to catch errors early.
- Check for text overflow in columns — Typst silently truncates overflowing content.
- PDF output lands in the same directory as the source file by default.

## Package Imports
- Standard pattern: `#import "@preview/package-name:version": *`
- Pin versions per `skills/typst/references/packages.md` (single source of truth) — `@latest` doesn't exist in Typst.

## Figure Paths
- Use paths relative to the `.typ` file location, not the working directory.
- Prefer `image("figures/name.png")` over absolute paths for portability.

## Visual Auto-detection

When creating or substantially editing `.typ` documents, auto-detect content that benefits from visuals. Do NOT wait for the user to request images — invoke tools directly.

**Priority:** Diagrams → native Typst (fletcher/chronos/timeliney/herodot, NEVER Python); Charts → cetz-plot (simple) → lilaq (complex) → matplotlib (last resort); Images → /image-search / /mindmap / `gemini-generate-image` MCP

**Auto-invoke triggers (no user prompt needed):**
- Company/brand logos → invoke `/image-search --logo "Name" --typst`
- Real photographs → invoke `/image-search "query" --typst`
- Conceptual illustrations, metaphors → call `gemini-generate-image` MCP, then copy to `images/` and write Typst `#figure(...)`
- Mind maps, concept maps → invoke `/mindmap "topic" --typst`

**When NOT to auto-invoke:**
- Quick edits (< 15 lines changed) — don't add visuals to minor fixes
- The document already has appropriate visuals for the content
- The user explicitly said no images or text-only

See `skills/typst/references/tool-routing.md` for the full routing table and fallback chains.
