#!/usr/bin/env bash
# Render one D2 source with the qk palette.
#
# Usage: render.sh <file.d2> [-o <outdir>] [-l elk|dagre|tala] [--light-only] [--pdf] [--gif]
#   -o            output directory (default: next to the source)
#   -l            layout engine (default elk; sequence diagrams ignore it)
#   --pdf         also write <name>.pdf (light; one page per board)
#   --gif         also write <name>.gif (light; animates steps/layers)
#
# Single-board source: <name>.{light,dark}.{svg,png} (PNG at 2x via headless Chrome).
# Source with steps/layers/scenarios: <name>.pdf plus <name>-<page>.png per board (light only),
# because D2 writes those boards as a directory of SVGs rather than one file.
#
# Exit 0 rendered clean, 1 lint/compile failure or a d2 warning, 2 usage error.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="" outdir="" layout="elk" modes=(light dark) want_pdf=0 want_gif=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o) outdir="${2:?-o needs a directory}"; shift 2 ;;
    -l) layout="${2:?-l needs a layout name}"; shift 2 ;;
    --light-only) modes=(light); shift ;;
    --pdf) want_pdf=1; shift ;;
    --gif) want_gif=1; shift ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *) [[ -z "$src" ]] || { echo "one source file only" >&2; exit 2; }; src="$1"; shift ;;
  esac
done
[[ -n "$src" && -f "$src" ]] || { echo "usage: render.sh <file.d2> [-o dir] [-l layout] [--light-only] [--pdf] [--gif]" >&2; exit 2; }
command -v d2 >/dev/null || { echo "d2 not installed: brew install d2" >&2; exit 1; }
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[[ -x "$chrome" ]] || { echo "Chrome not found; set CHROME=<path to a Chromium binary>" >&2; exit 1; }
# PDF/GIF export fails on CJK text: the system fallback font is a .ttc over D2's 128 MB limit, and
# even one 23 MB TrueType CJK font passed for two faces breaks the 64 MB scene limit. So the export
# gets a subset of a CJK .ttf holding only the characters in the source (needs uv for fonttools).
cjk_ttf="${D2_CJK_TTF:-/System/Library/Fonts/Supplemental/Arial Unicode.ttf}"

name="$(basename "${src%.d2}")"
outdir="${outdir:-$(dirname "$src")}"
mkdir -p "$outdir"

# Lint: colours must come from the palette so the dark render follows; the palette owns d2-config.
fail=0
if grep -nE '#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?\b' "$src" | grep -vE '^[0-9]+:\s*#' ; then
  echo "lint: raw hex colour above; use \${accent}/\${warn}/... or a class (see theme/classes.d2)" >&2; fail=1
fi
if grep -n 'd2-config' "$src"; then
  echo "lint: d2-config belongs to theme/*.d2; pass the layout with -l" >&2; fail=1
fi
if ! d2 fmt --check "$src" >/dev/null 2>&1; then
  echo "lint: $src is not d2-formatted; run: d2 fmt \"$src\"" >&2; fail=1
fi
[[ $fail -eq 0 ]] || exit 1

multi=0
grep -qE '^\s*(steps|layers|scenarios)\s*:' "$src" && multi=1
has_legend=0
grep -q 'd2-legend' "$src" && has_legend=1

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

merge() { # $1 = light|dark; writes the merged source and sets $merged and $offset
  merged="$tmp/$name.$1.d2"
  cat "$here/theme/$1.d2" "$here/theme/classes.d2" "$src" >"$merged"
  offset=$(cat "$here/theme/$1.d2" "$here/theme/classes.d2" | wc -l)
}

run_d2() { # run d2 on $merged with extra args; remap errors to the user's file and line
  local log
  if ! log="$(d2 --layout "$layout" "$@" 2>&1)"; then
    echo "$log" | awk -v f="$merged" -v s="$src" -v o="$offset" '{
      while (match($0, f ":[0-9]+")) {
        n = substr($0, RSTART + length(f) + 1, RLENGTH - length(f) - 1) - o
        $0 = substr($0, 1, RSTART - 1) s ":" n substr($0, RSTART + RLENGTH)
      }
      print }' >&2
    exit 1
  fi
  if grep -qi '^warn' <<<"$log"; then
    grep -i '^warn' <<<"$log" >&2; fail=1
  fi
}

abs() { echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; }

cjk_flags=()
cjk_fonts() { # subset the CJK font to the merged source's characters; sets cjk_flags
  python3 -c 'import sys; print("".join(sorted(set(open(sys.argv[1]).read()) - {"\n"})))' "$merged" >"$tmp/chars.txt"
  if uvx --from fonttools pyftsubset "$cjk_ttf" --text-file="$tmp/chars.txt" --output-file="$tmp/cjk.ttf" \
      --name-IDs='*' --name-languages='*' --notdef-outline --layout-features='*' --glyph-names >/dev/null 2>&1; then
    cjk_flags=(--font-bold "$tmp/cjk.ttf" --font-semibold "$tmp/cjk.ttf" --font-italic "$tmp/cjk.ttf")
  else
    echo "note: font subsetting failed (is uv installed?); passing the full CJK font for edge labels only" >&2
    cjk_flags=(--font-italic "$cjk_ttf")
  fi
}

if [[ $multi -eq 1 ]]; then
  merge light
  cjk_fonts
  pdf="$outdir/$name.pdf"
  run_d2 --pad 32 "${cjk_flags[@]}" "$merged" "$pdf"
  rm -f "$outdir/$name"-*.png
  pdftoppm -png -r 110 "$pdf" "$outdir/$name"
  echo "boards: $pdf  pages: $(ls "$outdir/$name"-*.png | wc -l | tr -d ' ') (PNG per page: $outdir/$name-<n>.png)"
else
  for mode in "${modes[@]}"; do
    merge "$mode"
    svg="$outdir/$name.$mode.svg" png="$outdir/$name.$mode.png"
    run_d2 --pad 32 --scale 1 --no-xml-tag "$merged" "$svg"
    # D2 blends groups with `multiply`, which turns them black on a dark background; `screen`
    # lifts them instead. Edge labels use D2's italic face, whose CJK glyphs come out slanted in
    # browsers, so they are pointed at the regular face with a sans fallback.
    blend=multiply; [[ $mode == dark ]] && blend=screen
    sed -i '' -e "s/mix-blend-mode: multiply;/mix-blend-mode: $blend;/" \
      -e 's/^\.blend {/text { font-synthesis: none; }\
.blend {/' -e 's/\(d2-[0-9]*\)-font-italic";$/\1-font-regular", "PingFang SC", "Helvetica Neue", sans-serif;/' "$svg"
    # The legend box ignores the theme: white fill, light-grey rules and black text. Recolour it
    # for dark mode (the stroke swap also hits any other #DEE1EB stroke, which only the legend uses).
    if [[ $mode == dark && $has_legend -eq 1 ]]; then
      sed -i '' -e 's/stroke="#DEE1EB" fill="#F7F7FA"/stroke="#55534E" fill="#30302E"/' \
        -e 's/fill="#ffffff" style="stroke-width: 1px"/fill="#30302E" style="stroke-width: 1px"/' \
        -e 's/stroke="#DEE1EB"/stroke="#55534E"/g' \
        -e 's/^\.blend {/text:not([fill]) { fill: #F5F4ED; }\
.blend {/' "$svg"
    fi
    # Rasterise the patched SVG at 2x in headless Chrome so the PNG matches what a browser shows.
    read -r vw vh < <(grep -oE 'viewBox="[^"]+"' "$svg" | head -1 | tr -d '"' | awk '{printf "%d %d\n", $3+0.5, $4+0.5}')
    "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
      --window-size="$vw,$vh" --screenshot="$(abs "$png")" "file://$(abs "$svg")" >/dev/null 2>&1 \
      || { echo "chrome screenshot failed for $svg" >&2; exit 1; }
    w=$(sips -g pixelWidth "$png" | awk '/pixelWidth/{print $2}')
    h=$(sips -g pixelHeight "$png" | awk '/pixelHeight/{print $2}')
    ratio=$(awk -v w="$w" -v h="$h" 'BEGIN{printf "%.1f", (w>h ? w/h : h/w)}')
    echo "$mode: $outdir/$name.$mode.{svg,png}  ${w}x${h}px  aspect ${ratio}:1"
    awk -v r="$ratio" 'BEGIN{exit !(r > 3.5)}' && echo "  note: aspect over 3.5:1 reads badly on a page; try direction: down or split the diagram"
  done
  if [[ $want_pdf -eq 1 ]]; then
    merge light
    cjk_fonts
    run_d2 --pad 32 "${cjk_flags[@]}" "$merged" "$outdir/$name.pdf"
    echo "pdf: $outdir/$name.pdf"
  fi
fi

if [[ $want_gif -eq 1 ]]; then
  merge light
  cjk_fonts
  run_d2 --pad 32 "${cjk_flags[@]}" --animate-interval 1500 "$merged" "$outdir/$name.gif"
  echo "gif: $outdir/$name.gif"
fi
exit $fail
