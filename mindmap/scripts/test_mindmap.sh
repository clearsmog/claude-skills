#!/usr/bin/env bash
# Tests for generate_mindmap.mjs. Run: bash scripts/test_mindmap.sh
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
cd "$T"
IN="$T/in.txt"; printf -- '- Root\n  - A\n    - a1\n  - B\n    - b1\n' > "$IN"
G="$HERE/generate_mindmap.mjs"
fail=0
check() { if eval "$2"; then echo "ok $1"; else echo "FAIL $1"; fail=1; fi; }

out="$(node "$G" -i "$IN" -o "new dir/sub/map.png" --typst 2>&1)"; rc=$?
check "creates a missing output directory" '[ $rc -eq 0 ] && file "new dir/sub/map.png" | grep -q "PNG image"'
check "--typst prints the path as given" 'printf "%s" "$out" | grep -qF "image(\"new dir/sub/map.png\""'
check "leaves no temp file in the skill" '[ ! -e "$HERE/.tmp-mindmap.html" ]'

node "$G" -i "$IN" -o "map.svg" >/dev/null 2>&1; rc=$?
check ".svg output is an SVG file" '[ $rc -eq 0 ] && head -c 4 map.svg | grep -q "<svg"'

node "$G" -i "$IN" -o "bad.svg" -f png >/dev/null 2>&1; rc=$?
check "format/extension mismatch is refused" '[ $rc -ne 0 ] && [ ! -e bad.svg ]'

node "$G" -i "$IN" -o "t.png" -t nosuchtheme >/dev/null 2>&1; rc=$?
check "unknown theme is refused" '[ $rc -ne 0 ] && [ ! -e t.png ]'
exit $fail
