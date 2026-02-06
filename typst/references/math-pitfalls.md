# Math Mode Pitfalls

## Currency Symbols in Math Mode

Currency symbols (£, $, €) cause errors inside math mode. Keep them outside:

```typst
// WRONG - causes "unclosed delimiter" or "unknown variable"
$ P = 548.33 $           // $ inside math breaks delimiter
$ V_0 = £80.00 $            // £ is unknown variable in math

// CORRECT - numbers only in math, currency outside
$ P = 548.33 $
The price is \$548.33.

$ V_0 = 80.00 $
The value is £80.00.
```

## Angle Brackets as Labels

`<text>` is interpreted as a label reference in Typst:

```typst
// WRONG - "unclosed label" error
[Discount (<100)]
[Premium (>100)]

// CORRECT - use words instead
[Discount (below 100)]
[Premium (above 100)]

// Or escape them
[Discount (\<100)]
```

## Numbers with Currency in Math

Never mix currency symbols with numbers inside `$ $`:

```typst
// WRONG
$ "FV" = $13,254,608 $     // Inner $ breaks math mode
$ "Coupon" = $3,500 $

// CORRECT
$ "FV" = 13,254,608 $
$ "Coupon" = 3,500 $
```

## Adjacent Letters / Multi-Letter Abbreviations

Typst parses adjacent letters as a single variable name:

```typst
// WRONG - "unknown variable: NPV"
$NPV = 0$
$V_L = V_U + tD$

// CORRECT
$"NPV" = 0$              // quoted string (upright)
$V_L = V_U + t D$        // spaces between letters
$V_L = V_U + t times D$  // explicit multiplication

// Same issue with: IRR, WACC, FCFF, FCFE, EPS, ROE, DDM, CAPM, etc.
```

## Commas in Numbers

Thousand separators cause line breaks in math mode:

```typst
// WRONG - displays as "1, 471, 429" with breaks
$ "PV" = 1,471,429 / 1.6105 $

// CORRECT - no thousand separators inside $ $
$ "PV" = 1471429 / 1.6105 $

// For formatted display, use text mode:
The PV is £1,471,429.
```

## Asterisk in Content Blocks

`*` starts bold text, causing "unclosed delimiter":

```typst
// ERROR
[The value is \$1,859,375*]

// FIX
[The value is \$1,859,375\*]
```
