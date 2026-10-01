---
name: create-document
description: Create new documents in any format — Beamer slides, Typst documents, or Quarto slides. Autonomous pipeline from prompt to publication-quality output.
disable-model-invocation: true
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task", "mcp__gemini__gemini-generate-image", "mcp__gemini__gemini-start-image-edit", "mcp__gemini__gemini-continue-image-edit", "mcp__gemini__gemini-end-image-edit"]
context: fork
background: false
---

# Document Creation Workflow

One prompt → one publication-quality document. Internal quality loop runs automatically.

---

## Format Selection

- User specifies format explicitly → use that
- User doesn't specify → detect from project context:
  - Has `Slides/` directory → Beamer LaTeX
  - Has `Source/` or mainly `.typ` files → Typst
  - Has `Quarto/` directory → Quarto
- Default for new projects → Typst (preferred modern format)

## Format Detection (for `.typ`)

Detect document type from user request keywords:
- resume, CV → CV template
- slides, presentation, lecture → touying slides (see `typst/references/touying-guide.md`)
- essay, paper → essay template
- guide, study guide, reference → study guide
- report, business → business report
- reference card, cheat sheet → dense reference layout

---

## Constraints

All formats: verify every citation against the bibliography.

Teaching material (lectures, slides, study guides): first read the project's knowledge base in `.claude/rules/` (notation registry, narrative arc) and check each new symbol against it; motivation before formalism; a worked example within 2 slides/pages of each definition; transition slides at major conceptual pivots.

---

## WHEN TO PAUSE (the ONLY case)

Request is genuinely ambiguous AND no project context to disambiguate:
- No sibling `.typ` files, no PDFs, no clear topic in the prompt
- Example: user says "make something" with zero context

In this case: ONE `AskUserQuestion` (topic + type), then proceed autonomously.

For everything else — proceed without asking. Template auto-selection is correct 90%+ of the time; user can re-invoke with explicit overrides if wrong.

---

## PIPELINE

### Phase 0: Auto-Discover

Run these before drafting, without stopping to confirm:

1. **Scan project for related materials**
   - Glob for `*.pdf`, `*.md`, `*.typ`, `images/` in the project directory
   - If PDFs found → check for `.parsed.md` next to each; read if exists
   - If no `.parsed.md` → parse using PDF handling rules (background for large files)
2. **Detect document type** from keywords + project context (see Format Detection above)
3. **Auto-select template** — no confirmation needed
4. **Style inheritance**: if sibling `.typ` files exist in the project:
   - Read first 30 lines of the most recent sibling
   - Match fonts, colors, qk preset
   - Only inherit from files that use `@local/qk` presets; ignore raw inline styles
5. **Build context**: materials found, template chosen, style detected

### Phase 1: Draft (autonomous — full document at once)

#### For Typst Documents (.typ):
- Always import `@local/qk:2.2.0` and set smart defaults
- Apply qk components per the typst skill's component auto-use table:
  - Warning paragraph → `#warning[...]`
  - Key takeaway → `#keypoint[...]`
  - Actionable advice → `#tip[...]`
  - Common mistake → `#trap[...]`
  - Memory aid → `#memorize[...]`
- **Visuals**: add them as content is drafted, routed per the typst skill's "Visual Tool Routing (compact)" section and its "Visual Auto-detection" table (single source; details in `typst/references/tool-routing.md`).
- Always add `alt:` text on all images
- Always `#set figure(placement: auto)`
- Write COMPLETE `.typ` file — not batches
- For large docs (>30 pages): write in sections but don't pause between them

#### For Beamer Slides (.tex):
- Check notation, apply creation patterns
- No `\pause` or overlay commands (check project rules)
- Write complete slide deck at once

#### For Quarto Slides (.qmd):
- Standard RevealJS YAML with theme, bibliography
- Environment parity with CSS classes
- Plotly for Python-generated plots

### Phase 2: Verify + Auto-Fix (autonomous — max 3 rounds)

1. **Compile**: `typst compile FILE.typ` (or format-appropriate command)
   - Hard gate: exit code must be 0
2. **Render sample PNGs**:
   - Documents <=3 pages → all pages
   - Documents >3 pages → page 1, middle page, last page
   - Presentations <30 slides → all slides
   - Presentations 30+ → first 3, middle 3, last 3
   - Command: `typst compile FILE.typ /tmp/create-preview-{0p}.png --pages [SAMPLE]`
3. **Visual inspection** — Read each PNG and check:
   - Content overflow / cut off?
   - Blank half-pages?
   - Font fallback squares (missing font)?
   - Missing images / broken references?
   - Cramped text / unbalanced layout?
4. **Structural query**: `typst query` for heading count, figure count
5. **If issues found** → fix → re-compile → re-render → re-check
6. Cap at 3 lightweight fix rounds

### Phase 3: Present (final output to user)

Deliver a summary:

```
## Created: [filename]

| Metric | Value |
|--------|-------|
| Pages | [N] |
| Sections | [N] |
| Visuals | [N figures, N diagrams] |
| Compile | PASS |
| Visual check | PASS / [issues noted] |
| Template | [template used] |
| Style inherited from | [sibling file or "none"] |
| Materials discovered | [list or "none"] |

**What could break:** [list risks]

**Next steps:** `/doc-review` for deep audit · `/finish` for full pipeline · `/excellence` for milestone
```

---

## Figures & Code

- Python scripts for data-driven content (plotly for Quarto only; Typst charts use lilaq by default, matplotlib/plotnine only for kde, pair or faceted plots)
- Diagrams: TikZ in Beamer source, fletcher/chronos/timeliney in Typst (NEVER Python), SVG for Quarto
- Save outputs as `.svg` for Typst embedding (preferred), `.png` for raster, `.parquet` for data persistence

---

## Post-Creation Checklist

```
[ ] Document compiles without errors
[ ] No overflow issues (verified via PNG)
[ ] All citations resolve
[ ] Every definition has motivation + worked example
[ ] 2-3 Socratic questions embedded (for slides)
[ ] Transition slides between sections (for slides)
[ ] Visual aids present where content benefits from them
[ ] New notation added to knowledge base
```

---

## Format-Specific Notes

### Typst Pedagogical Constraints (for slides)
- Motivation before formalism
- Worked example within 2 slides of definition
- Fragment reveals with `#pause` (touying) — max 2-3 per slide
- Speaker notes with `#speaker-note[...]` for presenter context
- Use touying themes via qk-slides (see `typst/references/touying-guide.md`)

### Beamer Pedagogical Constraints
- Same as Typst but using LaTeX environments
- No `\pause` or overlay commands

### Devil's Advocate for Non-Slide Documents
- For guides: "Is this section ordering optimal for the reader?"
- For CVs: "Is this ATS-compatible? Is the hierarchy clear?"
- For pitch decks: "Does the narrative build to a clear ask?"
- For essays: "Is the argument structure compelling?"
