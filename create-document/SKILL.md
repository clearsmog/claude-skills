---
name: create-document
description: Create new documents in any format — Beamer slides, Typst documents, or Quarto slides. Autonomous pipeline from prompt to publication-quality output.
disable-model-invocation: true
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task", "mcp__gemini__gemini-generate-image", "mcp__gemini__gemini-start-image-edit", "mcp__gemini__gemini-continue-image-edit", "mcp__gemini__gemini-end-image-edit"]
context: fork
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

## CONSTRAINTS (Non-Negotiable, All Formats)

1. **Read the knowledge base FIRST** — notation registry, narrative arc, applications database
2. Every new symbol MUST be checked against the notation registry
3. Motivation before formalism — no exceptions
4. Worked example within 2 slides/pages of every definition
5. Max 2 colored boxes/callouts per slide or page
6. Transition slides at major conceptual pivots (for slide decks)
7. All citations verified against the bibliography

---

## WHEN TO PAUSE (the ONLY case)

Request is genuinely ambiguous AND no project context to disambiguate:
- No sibling `.typ` files, no PDFs, no clear topic in the prompt
- Example: user says "make something" with zero context

In this case: ONE `AskUserQuestion` (topic + type), then proceed autonomously.

For everything else — proceed without asking. Template auto-selection is correct 90%+ of the time; user can re-invoke with explicit overrides if wrong.

---

## PIPELINE

### Phase 0: Auto-Discover (silent — no pause)

Run all of these silently before drafting:

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
- Always import `@local/qk:2.0.0` and set smart defaults
- Apply qk components per the typst skill's component auto-use table:
  - Warning paragraph → `#warning[...]`
  - Key takeaway → `#keypoint[...]`
  - Actionable advice → `#tip[...]`
  - Common mistake → `#trap[...]`
  - Memory aid → `#memorize[...]`
- **Visual auto-detection** (proactive): as content is drafted, match patterns to the best tool. Route by content type: diagrams → native Typst (fletcher/chronos/timeliney/herodot, NEVER Python); charts → cetz-plot (simple, < 3 series) / plotnine (faceted/grammar) / matplotlib+seaborn (statistical/complex) — generate SVG, embed; images → `/image-search` / `/mindmap` / `gemini-generate-image` MCP.

  | Content pattern | Visual | Tool |
  |-----------------|--------|------|
  | Comparison of 2+ items, attribute grids | Table or grid | Typst native |
  | Callout boxes, styled layouts | `rect()`, `block()` | Typst native |
  | Sequential process, decision logic | Flowchart / decision tree | `fletcher` |
  | System architecture, ER diagrams | Block / entity diagram | `fletcher` |
  | Hierarchy or taxonomy | Tree diagram | `fletcher` or `/mindmap` |
  | Topic overview, concept map | Mind map | `/mindmap` |
  | Request-response, API flows | Sequence diagram | `chronos` |
  | Project schedule, phases | Gantt chart | `timeliney` |
  | Historical events, evolution | Timeline | `herodot` |
  | Simple data chart (< 3 series, < 20 pts) | Line/bar/scatter chart | `cetz-plot` (Typst native, `qk-cycle`) |
  | Statistical chart (violin, kde, heatmap) | Statistical plot | matplotlib+seaborn (`use()`, SVG) |
  | Faceted / grammar-of-graphics chart | Layered plot | plotnine (`theme_qk()`, SVG) |
  | Complex chart (4+ series, annotations) | Publication chart | matplotlib (full API, SVG) |
  | Company logo, brand mark | Logo | `/image-search --logo` |
  | Real-world photo | Photo | `/image-search` |
  | Conceptual illustration, metaphor | AI-generated image | `gemini-generate-image` MCP |

  See `typst/references/tool-routing.md` for full details, examples, and fallback chains.
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

**Next steps:** `/review` for deep audit · `/finish` for full pipeline · `/excellence` for milestone
```

---

## Figures & Code

- Python scripts for data-driven content (plotly for Quarto only; matplotlib/plotnine for Typst charts)
- Diagrams: TikZ in Beamer source, fletcher/chronos/timeliney in Typst (NEVER Python), SVG for Quarto
- Save outputs as `.svg` for Typst embedding (preferred), `.png` for raster, `.parquet` for data persistence

---

## Post-Creation Checklist

```
[ ] Document compiles without errors
[ ] No overflow issues (verified via PNG)
[ ] All citations resolve
[ ] Every definition has motivation + worked example
[ ] Max 2 colored boxes/callouts per slide/page
[ ] 2-3 Socratic questions embedded (for slides)
[ ] Transition slides between sections (for slides)
[ ] Visual aids present where content benefits from them
[ ] New notation added to knowledge base
```

---

## Format-Specific Notes

### Typst Pedagogical Constraints (for slides)
- Motivation before formalism
- Max 2 boxes/slide
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
