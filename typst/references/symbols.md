# Symbols Reference

Use `#sym.*` for reliable cross-platform symbols.

## Emoji

Typst exposes some emoji via `emoji.*`, but **coverage is incomplete**. Many emoji names that seem natural (e.g. `emoji.target`, `emoji.fire`) don't exist and cause compilation errors.

**Safe emoji** (confirmed working):
```typst
#emoji.clock        // 🕐
#emoji.pencil       // ✏️
#emoji.checkmark    // ✅ (different from sym.checkmark)
```

**Does NOT exist** (will error):
```typst
#emoji.target       // ❌ "module `emoji` does not contain `target`"
```

**Workaround:** Use `sym.*` equivalents instead — they're always safe:
```typst
#sym.circle.filled  // ● (use instead of emoji.target)
#sym.star.filled    // ★
#sym.diamond.filled // ◆
#sym.triangle.stroked.t // △
```

**Rule of thumb:** Default to `sym.*` unless you've verified the specific emoji exists. The `sym` module is complete; the `emoji` module has gaps.

## Arrows

```typst
#sym.arrow.r       // → right
#sym.arrow.l       // ← left
#sym.arrow.l.r     // ↔ bidirectional
#sym.arrow.t       // ↑ up
#sym.arrow.b       // ↓ down
```

## Common

```typst
#sym.square        // □ checkbox
#sym.checkmark     // ✓ checkmark
#sym.dot           // · middle dot
#sym.bullet        // • bullet
#sym.dash.em       // — em dash
```

## Math/Logic

```typst
#sym.times         // × multiplication
#sym.div           // ÷ division
#sym.lt.eq         // ≤ less or equal
#sym.gt.eq         // ≥ greater or equal
#sym.approx        // ≈ approximately
#sym.percent       // % percent
```
