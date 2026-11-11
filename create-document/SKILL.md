---
name: create-document
description: Create a new Typst document from one prompt - report, study guide, essay, CV, slides or reference card. Finds source material in the project, copies the style of sibling files, drafts the whole document, compiles it, checks the rendered pages and fixes what it finds.
disable-model-invocation: true
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Skill"]
---

# Document Creation Workflow

One prompt → one publication-quality document. Internal quality loop runs automatically.

---

## Format

This skill writes Typst and loads the `typst` skill for syntax, components and visual
routing. If the user asks for LaTeX/Beamer or Quarto, say this skill doesn't build those
and stop, rather than produce a file nothing here can compile or check.

## Document type

Detect document type from user request keywords:
- resume, CV → CV template
- slides, presentation, lecture → touying slides (see the `typst` skill's `references/touying-guide.md`)
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
2. **Detect document type** from keywords + project context (see Document type above)
3. **Auto-select template** — no confirmation needed
4. **Style inheritance**: if sibling `.typ` files exist in the project:
   - Read first 30 lines of the most recent sibling
   - Match fonts, colors, qk preset
   - Only inherit from files that use `@local/qk` presets; ignore raw inline styles
5. **Build context**: materials found, template chosen, style detected

### Phase 1: Draft (autonomous — full document at once)

- Always import `@local/qk:2.2.0` and set smart defaults
- Apply qk components per the typst skill's component auto-use table:
  - Warning paragraph → `#warning[...]`
  - Key takeaway → `#keypoint[...]`
  - Actionable advice → `#tip[...]`
  - Common mistake → `#trap[...]`
  - Memory aid → `#memorize[...]`
- **Visuals**: add them as content is drafted, routed per the typst skill's `references/tool-routing.md` (the single source: routing tables, content patterns, and when not to add one; the skill's "Visual Tool Routing" section is the short version).
- Always add `alt:` text on all images
- Always `#set figure(placement: auto)`
- Write COMPLETE `.typ` file — not batches
- For large docs (>30 pages): write in sections but don't pause between them

### Phase 2: Verify + Auto-Fix (autonomous — max 3 rounds)

1. **Compile**: `typst compile FILE.typ`
   - Hard gate: exit code must be 0
2. **Render sample PNGs**:
   - Documents <=3 pages → all pages
   - Documents >3 pages → page 1, middle page, last page
   - Presentations <30 slides → all slides
   - Presentations 30+ → first 3, middle 3, last 3
   - Command: `typst compile FILE.typ "$(mktemp -d)/p-{0p}.png" --pages [SAMPLE]`
3. **Visual inspection** — Read each PNG and check:
   - Content overflow / cut off?
   - Blank half-pages?
   - Font fallback squares (missing font)?
   - Missing images / broken references?
   - Cramped text / unbalanced layout?
4. **Structural query**: `typst eval --in <file> 'query(heading).len()'` (and `query(figure)`) for heading count, figure count
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

**Next steps:** `/doc-review` for deep audit
```

---

## Figures & Code

- Charts use lilaq by default; a Python script (matplotlib/plotnine) only for kde, pair or faceted plots, or an existing data pipeline
- Diagrams: fletcher/chronos/timeliney for small ones, the `diagram` skill (D2) for larger, multi-party or network diagrams; never Python
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
- Use touying themes via qk-slides (see the `typst` skill's `references/touying-guide.md`)

### Questions to put to a non-slide document before presenting it
- For guides: "Is this section ordering optimal for the reader?"
- For CVs: "Is this ATS-compatible? Is the hierarchy clear?"
- For pitch decks: "Does the narrative build to a clear ask?"
- For essays: "Is the argument structure compelling?"
