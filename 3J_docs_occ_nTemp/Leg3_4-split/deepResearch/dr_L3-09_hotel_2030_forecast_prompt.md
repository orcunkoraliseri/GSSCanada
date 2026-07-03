# Deep-Research Prompt dr_L3-09 — HOTEL OCCUPANCY TO 2030: forecast-method pressure-test + scenario bands

> SCOPE GUARD — READ FIRST. This is the **hotel-forecast** task of the Leg-3 set. Its two jobs: (a)
> pressure-test our planned forecasting recipe — SARIMA(1,1,1)(1,1,1,12) per province with a COVID
> indicator (2020-03…2022-06) — against best practice for monthly tourism series with a structural
> break, and (b) give the hotel channel its **2030 scenario bands** (the analogue of the office WFH
> bands and the retail in-store bands), grounded in post-COVID travel-demand evidence. Do NOT hunt for
> the data tables (that is `dr_L3-01`), do NOT derive diurnal shapes (`dr_L3-05`), and do NOT produce
> EUI benchmarks (`dr_L3-03`). See `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A method-and-scenarios brief. The hotel channel multiplies a fixed diurnal shape by a monthly
provincial occupancy rate; 2030 needs 12 monthly values per province (QC, AB). The planning docs fix
SARIMA(1,1,1)(1,1,1,12) + COVID dummy as the recipe — chosen for being classical, cheap, and
defensible, but the specification was set by convention, not evidence. Separately, the other two
commercial channels each carry a named scenario lever for their dominant 2030 uncertainty (office: WFH
rate; retail: in-store share); the hotel channel currently has only the extrapolated trend, which
leaves its dominant uncertainty — **whether business travel structurally recovers** — implicit inside
one SARIMA path. This prompt closes both gaps.

## Role

Tourism-demand forecasting researcher. Ground the method side in the tourism/hospitality forecasting
literature (SARIMA vs ETS vs structural / BSTS on monthly occupancy or arrivals series; intervention
analysis for shocks — pulse vs level-shift vs transfer function; the post-COVID tourism-forecasting
papers specifically). Ground the scenario side in published outlooks for Canadian (or comparable)
hotel demand: business-travel recovery projections, Destination Canada / CBRE / STR outlooks, and the
remote-work→business-travel link. Keep method evidence and outlook evidence separate.

## Why this matters (so you scope correctly)

The 2030 hotel multiplier feeds every hotel-floor simulation scenario. Two specific traps: (1) a COVID
**pulse** dummy assumes full mean-reversion — if post-2022 demand settled to a new level (structurally
lower business travel), a pulse specification silently forecasts the *old* normal for 2030; (2) with
the series ending at 2022 (our GSS-parallel window), the model must extrapolate 8 years — the
literature on how far a seasonal ARIMA can credibly extrapolate, and how to report its widening
uncertainty, decides whether we present one path or bands. The office channel's WFH bands defused
exactly this class of reviewer challenge; the hotel channel needs the same armour.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Method comparison for monthly occupancy series with a structural break

| Method | Handling of seasonality | Handling of the COVID break | Long-horizon (8-yr) behaviour | Precedent on hotel/tourism series | Citation |
|---|---|---|---|---|---|
| SARIMA + intervention dummy (our plan) |  |  |  |  |  |
| ETS / state-space exponential smoothing |  |  |  |  |  |
| Structural time-series / BSTS |  |  |  |  |  |
| Regression with ARMA errors + exogenous drivers |  |  |  |  |  |

### Table 2 — COVID intervention specification (the pulse-vs-level question)

| Specification | What it assumes about 2030 | Evidence from post-COVID tourism series (did occupancy mean-revert or re-level?) | Citation |
|---|---|---|---|
| Pulse dummy 2020-03…2022-06 (our plan) |  |  |  |
| Level shift from 2020-03 |  |  |  |
| Pulse + permanent level component |  |  |  |
| Transfer-function / decay intervention |  |  |  |

### Table 3 — Post-COVID travel-demand outlooks (the scenario evidence)

| Source + year | Scope (Canada / North America; business vs leisure split if given) | Numeric outlook (occupancy, room-nights, or business-travel volume vs 2019) | Horizon | Citation |
|---|---|---|---|---|
| Destination Canada outlook |  |  |  |  |
| CBRE Hotels Canada outlook |  |  |  |  |
| STR / CoStar projections |  |  |  |  |
| Business-travel-specific studies (GBTA or academic) |  |  |  |  |
| Remote-work → business-travel link studies |  |  |  |  |

### Table 4 — Sanity anchors

| Quantity | Value | Citation |
|---|---|---|
| QC + AB occupancy 2019 (pre-COVID reference) |  |  |
| QC + AB occupancy 2022 (end of our series) |  |  |
| Latest available (2023–2025) — how much further recovery happened after our window closes |  |  |

### Table 5 — THE DELIVERABLE: three named 2030 hotel scenarios

Multipliers apply to the SARIMA central path (or directly to 2019/2022 monthly levels — state which).

| Scenario name | 2030 monthly-occupancy level vs 2019 (%) | One-paragraph justification (below table) | Key sources |
|---|---|---|---|
| (e.g., Full Recovery) |  |  |  |
| (e.g., Structural Business-Travel Loss) |  |  |  |
| (e.g., Leisure-Led Growth) |  |  |  |

---

## Part C — Synthesis (recipe + bands)

Give: (1) a verdict on our planned specification — keep SARIMA(1,1,1)(1,1,1,12) + pulse dummy, or
change the intervention type / add a level component / switch method — with the deciding citation;
(2) how to *select* the final orders defensibly (information criteria on the pre-COVID segment,
auto-ARIMA, or fixed by convention) so the paper can answer "why (1,1,1)(1,1,1,12)?"; (3) the
uncertainty-reporting recommendation for an 8-year extrapolation (prediction intervals vs scenario
bands vs both); (4) the three named scenarios restated, with the central one identified as the default
and an explicit statement of how they interact with the SARIMA path (replace it / bracket it);
(5) whether QC and AB warrant different scenario tilts (Alberta's oil-business exposure vs Montreal's
leisure/events mix), one paragraph.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations; method literature vs industry outlooks kept distinct.
4. **"Confidence and caveats":** which scenario bound and which method claim are least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **The pulse-vs-level question must be answered with post-COVID evidence** — it is the single biggest
  lever on the 2030 number.
- **Three numeric scenarios are mandatory** — a trend-only answer does not close this prompt.
- **No fabricated precision;** flag GAPs (industry outlooks are often paywalled — cite what is public
  and mark the rest GAP).
- **Stay on topic** — forecasting method and 2030 levels only; no data acquisition, no diurnal shape,
  no EUI.
