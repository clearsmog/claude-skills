#import "@local/qk:2.2.0": *
#import "@preview/lilaq:0.6.0" as lq

#show: qk-doc.with(
  title: "Interest Rate Swaps: A Short Primer",
  header-text: "IRS Primer",
  footer-text: "Study notes",
  styled-lists: true,
  styled-captions: true,
  figure-placement: none,
)

#align(center)[
  #text(22pt, weight: "bold", fill: blue.at("900"))[Interest Rate Swaps]\
  #text(12pt, fill: slate.at("500"))[A short primer]
]
#v(6pt)

#metric-row(
  stat-card("2", "legs: fixed and floating", color: blue.at("600")),
  stat-card("PV = 0", "at inception", color: emerald.at("600")),
  stat-card("PV01", "main risk measure", color: violet.at("600")),
)

= What a swap is

A plain-vanilla interest rate swap exchanges a fixed rate for a floating rate on the
same notional. No principal changes hands; only the net coupon is paid on each date.
The payer of fixed gains when rates rise.

#keypoint[*Par swap rate.* 
  The fixed rate is set so the swap is worth zero on the trade date. Any later move in
  the curve gives it a non-zero value, which is what the desk marks to market every day.
]

#formula-box("Value to the fixed payer")[
  $ V = sum_(i=1)^n N tau_i (F_i - K) D(t_i) $
  where $F_i$ is the forward rate, $K$ the fixed rate and $D(t_i)$ the discount factor.
]

= Pricing inputs

#styled-table(
  columns: (1fr, 2fr),
  [*Input*], [*Where it comes from*],
  [Discount curve], [OIS curve bootstrapped from overnight-index swaps],
  [Forward curve], [Same OIS curve under single-curve pricing],
  [Day count], [ACT/365F for SONIA, ACT/360 for SOFR],
  [Fixings], [Published overnight rates, compounded in arrears],
)

#figure(
  lq.diagram(
    width: 12cm,
    height: 5cm,
    xlabel: [Tenor (years)],
    ylabel: [Rate (%)],
    legend: (position: bottom + right),
    lq.plot((1, 2, 3, 5, 7, 10, 20, 30), (4.10, 3.85, 3.72, 3.65, 3.70, 3.82, 4.05, 4.02), label: [Par swap rate], mark: "o"),
    lq.plot((1, 2, 3, 5, 7, 10, 20, 30), (4.05, 3.60, 3.50, 3.55, 3.80, 4.05, 4.40, 3.95), label: [1y forward]),
  ),
  caption: [An illustrative curve. Forwards sit above par where the curve slopes up.],
)

= Lifecycle

#figure(
  image("state-swap-trade.light.svg", width: 42%),
  caption: [Trade states from execution to maturity, drawn with the diagram skill.],
)

#trap[
  PV01 is not the same as duration. PV01 is a money amount per basis point on this
  notional; duration is a percentage sensitivity of a price.
]

#example-box[
  A 5-year payer swap on £100m with PV01 of £45,000 gains about £450,000 if the whole
  curve rises 10 bp.
]
