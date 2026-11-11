---
name: diagram
description: Draw structural diagrams with D2 — process lifecycles and sequence/swimlane diagrams (who does what, in what order), flowcharts and decision trees, causal/event networks (what drives what), state machines, layered or market-structure maps, and step-by-step walkthroughs — rendered in the qk palette to light and dark SVG + PNG (plus PDF/GIF) for Typst, HTML, Markdown, slides or standalone use. Use whenever the user wants a 流程图, 时序图, 泳道图, 生命周期图, 拓扑图, 因果图, 传导链, 关系图, state diagram, or asks to "visualize how X works / how A affects B / the steps of X", in any project — even without the word "diagram". Not for data charts (dataviz), mind maps (/mindmap), dated timelines (Typst herodot/timeliney) or a concept drawn as an isometric physical machine (anatomy).
argument-hint: "<what to draw> [-o outdir]"
allowed-tools: Read, Write, Edit, Bash
---

# Diagram (D2)

One `.d2` source per figure, kept next to the deliverable so it stays editable. `scripts/render.sh`
prepends the palette (`theme/light.d2` or `theme/dark.d2`) and the semantic classes
(`theme/classes.d2`), renders with D2, patches the SVG, and rasterises it in headless Chrome.

A diagram makes an argument that prose cannot: what causes what, who acts when, where a thing can
go next. Two tests decide whether it works. With every label deleted, does the shape alone still
say something (a fan-out, a cycle, a hand-off between lanes)? And could the reader learn a concrete
fact from it, or does it only name boxes?

## 1. Decide depth and type

**Depth first.**

- A *sketch* explains a structure the reader already half knows. Use generic labels and keep it
  under about 10 nodes.
- A *teaching diagram* (study notes, a walkthrough, a system explained to someone new) must carry
  concrete content: real numbers from a worked example, real event or field names, the formula
  itself. "Initial margin 4,950, falls to 4,450 < 4,500 maintenance, deposit 500" teaches;
  "margin → call" does not. Take the numbers from the source material, never invent them.

**Then the type.** Pick by the question the figure answers, and start from the matching example:

| The question being answered | Type | Pattern inside it | Start from | Layout |
|---|---|---|---|---|
| Who does what, in what order (parties × time) | sequence / lifecycle | hand-offs between lanes; spans for busy stretches | `examples/sequence-futures-lifecycle.d2` | (fixed) |
| What happens next, with yes/no branches | flow / decision | tree; one end node per branch | `examples/flow-option-exercise.d2` | `elk` |
| What drives what | causal / event network | fan-out from one trigger, convergence onto one outcome | `examples/causal-rate-hike.d2` | `elk` |
| Which states a thing passes through | state machine | chain plus loops | `examples/state-swap-trade.d2` | `tala` |
| Which parts sit in which layer or venue | layers / lanes | side-by-side containers | `examples/layers-market-structure.d2` | `elk` |
| How a chain unfolds, one link at a time | step walkthrough | the same board growing per step | `examples/steps-rate-transmission.d2` | `elk` |

Not here: data charts → `dataviz`; mind maps / topic trees → `/mindmap`; timelines on a real date
axis → Typst herodot/timeliney; a Typst flowchart of 10 nodes or fewer with no crossings →
fletcher (see `typst/references/tool-routing.md`); a mechanism drawn as a real, working object
(isometric, interactive) → `anatomy`.

**Size.** 5–15 nodes reads well. Past 15, split by phase or zoom level, or turn it into a step
walkthrough. Don't shrink the text.

## 2. Write the source

Read the matching example first; it carries the idioms for its type.

Text and boxes:

- Labels are `中文 English` (or the user's language plus the standard term). Node labels are at
  most 2 lines; edge labels are at most about 12 characters. The mechanism goes on the edge, the
  state on the node.
- Box only things that carry meaning. Titles and annotations are `shape: text`, and a root-level
  title can take `near: top-center`. `near` with a position constant only works on root-level shapes.
- Formulas are LaTeX: `|latex F_0 = S_0(1+r)^T|`. Keep CJK outside the LaTeX (it turns serif). For
  a labelled formula, nest it: `fwd: 远期价格 ↑ { style.font-size: 16; f: |latex ...| {shape: text} }`.

Colour and grouping:

- Colour comes only through classes, never raw hex. The render lints for hex, because hex doesn't
  follow dark mode.
  - Node classes: `accent` for the trigger or focus (one per figure), `warn`, `good`, `muted` for
    the inactive path, and `lane` for containers.
  - Edge classes: `pos` (raises / leads to), `neg` (lowers / blocks), `alert` (the exception
    path), `weak` (optional).
  - Raw tokens such as `${accent}` and `${soft}` work in `style` when no class fits.
- Globs save repetition. `*: {&leaf: false; class: lane}` turns every container into a lane.
  `*: {&shape: diamond; ...}` styles every decision.
- When a figure uses colour or dash to encode meaning (causal signs, exception paths), add a
  legend under `vars.d2-legend` (see the causal example). Its title stays "Legend".

Content:

- In a sequence, `actor.span -> other` draws an activation bar for a busy stretch, such as the
  CCP during mark-to-market. An unconnected child (`long.check: "..."`) is a note.
- Steps: `steps: { 1: {...}; 2: {...} }`. Each step inherits the one before, so add only the new
  link in each.

Rules the render enforces or depends on:

- No `vars.d2-config` in the source: the palette owns it. Pass the layout with `-l`.
- Run `d2 fmt` on the file. The render refuses unformatted sources.
- Avoid forced crossings by structure, not by tweaking. Give branches their own end nodes, and
  order lane children in the direction their edges leave.
- Grid layouts (`grid-columns`) draw edges straight through nodes in between. Use them only when
  every edge joins neighbouring cells.

Sources:

- Every causal edge and lifecycle step must come from the user's material or a checked source.
  Cite it in a comment at the top (a CFA LO, a document section).
- For per-edge provenance in HTML, put it in `tooltip:`; it shows on hover and survives into the SVG.
- Mark anything unchecked `[unverified]` in its label.

## 3. Render

```bash
${CLAUDE_SKILL_DIR}/scripts/render.sh path/to/fig.d2 [-o outdir] [-l elk|dagre|tala] [--light-only] [--pdf] [--gif]
```

Output names and locations:

- Single-board figures get `fig.{light,dark}.{svg,png}` (PNG at 2x).
- A source with `steps`/`layers`/`scenarios` gets `fig.pdf` (one page per board) plus
  `fig-<n>.png` per page, light only.
- `--gif` animates the boards (1.5 s each); `--pdf` adds a PDF for single-board figures.
- Default output location: inside a git repo, `./diagrams/<slug>.d2` (kebab-case subject, at most
  40 characters), so the source gets committed; otherwise next to the deliverable.

Exit 1 means one of: a lint failure (hex, d2-config, unformatted), a compile error (reported at
the line in your file), or a D2 warning.

## 4. Look, in two passes, then fix

Read the PNGs (light and dark, or every page) and judge them in this order.

**Pass 1: does it make the argument?**
- [ ] With labels ignored, the structure shows the intended pattern (fan-out, hand-off, loop, branch)
- [ ] The eye lands on the `accent` node first and then follows the flow direction
- [ ] A teaching diagram shows its concrete numbers or names, readable at the rendered size
- [ ] Nothing on the page is decoration: each box, colour and dash means something (the legend says what)

**Pass 2: defects**
- [ ] No label overlaps a node, an arrowhead or another label
- [ ] No edge passes through a non-endpoint node; crossings appear only where unavoidable
- [ ] Spacing is even, with no cramped cluster beside a large void
- [ ] The dark version has no black or white blocks, and every label is readable
- [ ] Aspect ratio is at most 3.5:1 (the script notes it); otherwise switch `direction` or split

Fix the source and re-render. Expect 2–4 rounds. Stop when both passes are clean and you would show
it without caveats. Don't hand over a figure you have not looked at. When delivering, show the
light PNG and list the paths.

## 5. Embed

| Target | Snippet |
|---|---|
| Typst | `#figure(image("fig.light.svg", width: 100%), caption: [...])` (print is light) |
| HTML / Artifact | `<picture><source srcset="fig.dark.svg" media="(prefers-color-scheme: dark)"><img src="fig.light.svg" alt="..."></picture>`. For a page with its own theme toggle, inline both SVGs (they carry no XML declaration) and show one per theme with CSS; tooltips work only inline |
| Markdown / GitHub | the same `<picture>` block, or `![...](fig.light.png)` |
| Slides | the PNG, or `--pdf` / `--gif` for a step walkthrough |

The SVG embeds its own fonts (Source Sans plus a CJK fallback), so it does not match a Typst
document's body font. When that matters for a small diagram, use fletcher.

## Gotchas (verified on d2 0.9.0)

- `d2 validate` passes files that fail to compile (for example, a theme code such as `AA4` used
  as a style value). Trust `render.sh`.
- `render.sh` applies these SVG patches; keep them if you hand-edit an SVG:
  - Sequence groups are drawn with `mix-blend-mode: multiply`, which turns them black on dark. The
    dark SVG switches it to `screen`.
  - The italic face used for edge labels slants CJK in browsers. Labels are pointed at the regular
    face with a sans fallback.
  - The legend box is hard-coded white/black. The dark SVG recolours it.
- On ELK and dagre, `label.near` on an edge is accepted but does nothing, and self-loop labels
  overlap the loop. Use `-l tala`. TALA ignores `direction` on containers, so keep lanes on ELK.
- PDF/GIF export dies on CJK with the system fallback font (a .ttc over D2's 128 MB limit), and one
  23 MB CJK `.ttf` passed for two faces breaks the 64 MB scene limit. `render.sh` handles this by
  subsetting `Arial Unicode.ttf` to the source's characters (about 50 KB) with fonttools via `uvx`.
  The cost: PDF/GIF lose bold, since that font has one weight; the SVG/PNG keep it. Override the
  font with `D2_CJK_TTF=<path to a .ttf>` (`.otf` is rejected).
- Needs `d2` (`brew install d2`) and Google Chrome (or `CHROME=<path>`). PDF/GIF and step boards
  also need `uv` and `pdftoppm` (poppler).
