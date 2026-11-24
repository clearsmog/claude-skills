# D2 gotchas

Read by the diagram skill before switching layout engines, hand-editing an SVG, exporting
PDF/GIF with CJK, or when a dependency is missing.

## Verified on d2 0.9.0

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
