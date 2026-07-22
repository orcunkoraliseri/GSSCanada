# Deep-Research Prompt dr_L3v2-01C — MONTRÉAL + CALGARY MARKET-LEVEL MONTHLY OCCUPANCY (2005–2022) — VALIDATION CONTEXT

> SCOPE GUARD — READ FIRST. This is a **DATA-EXTRACTION** task producing **validation-context only** —
> NOT the canonical driver. The pipeline keys the Hotel channel on the **provincial** series (QC via
> `dr_L3v2-01A`, AB via `dr_L3v2-01B`). This prompt harvests the **city-market** monthly occupancy for
> **Montréal** and **Calgary** (the two downtown markets where the simulated tall buildings actually
> sit) so we can *check* that the provincial driver is not smearing away downtown demand and event
> spikes. Do NOT treat this as the driver, do NOT design the forecast, do NOT interpolate. If market data
> is thin, a partial series with honest gaps is the correct result.

---

## ⚠️ v2.1 HARDENING — LEARN FROM THE FAILED FIRST RUN (read before you start)

A prior run of the sibling Alberta prompt **fabricated** its series (cited an API that 404s and a
non-existent "open" source). Do not repeat that. You are being run in **Gemini Deep Research (web
browsing)**. Therefore:

1. **PROVE REACHABILITY.** Every cited source must have been opened in THIS session — paste a short
   verbatim snippet + working URL in Table 2. No snippet, no data (blank value + `STATUS = GAP`).
2. **NEVER invent an endpoint, table ID, or file URL.** 404/blocked/login → GAP, never a plausible
   substitute.
3. **PAYWALL / LOGIN = GAP.** CBRE / STR market reports are proprietary; if you can't pass, mark GAP —
   never claim paywalled data is open.
4. **This file is BONUS validation context** — sparse honest coverage is completely fine and expected.
   A handful of verified anchors beats an invented monthly grid.

---

## What this document is

A market-level cross-check harvest for the Hotel channel of a 4-channel GSS→BEM occupancy pipeline
(Leg 3 of 3). dr_L3-01 flagged that **provincial averages understate downtown occupancy** (Montréal
~0.73 vs QC ~0.60–0.65 in 2019; Calgary ~0.62 vs AB ~0.54–0.58) and **smooth away event spikes**
(Calgary Stampede July often > 0.85; Montréal Grand Prix / summer-festival June surges). Those peaks
drive summer cooling and DHW peaks in the simulated towers. This series is kept as a side file
(`hotel_occupancy_monthly_markets.csv`) for validation context — it never replaces the provincial
driver.

Target file (market label in place of PR):
```
YEAR, MONTH, MARKET, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```
where `MARKET ∈ {Montreal, Calgary}`.

## Role

Canadian city-market lodging-data extraction specialist. Acceptable sources, in preference order:

- **Montréal:** ISQ « fréquentation » at the **région touristique de Montréal** cut (open-licence,
  monthly); Greater Montréal Hotel Association / Tourisme Montréal releases; CBRE/STR Montréal market
  reports (proprietary).
- **Calgary:** CBRE / STR Calgary market reports (proprietary); Travel Alberta / Calgary tourism
  releases; Alberta Economic Dashboard sub-provincial cuts if published.

Browse actual published figures and transcribe. Where only proprietary sources carry a month, cite the
value + source without redistributing the report.

## Why this matters (so you scope correctly)

- The **occupancy_rate** (0–1) is the column of interest; ADR/RevPAR welcome where published but
  secondary here.
- **Event spikes are the whole point** — capture July (Stampede) for Calgary and June (Grand Prix) for
  Montréal faithfully; these are the months provincial data smooths. Do not clip or average them.
- **COVID months kept as published** (2020-03 …); downtown troughs are extreme (Montréal downtown
  < 0.04) — that is correct.
- Coverage will likely be **patchier than the provincial series** — that is expected. Gaps are fine;
  invented downtown values are not.

---

## REQUIRED OUTPUT

### Table 1 — Montréal + Calgary monthly series, 2005-01 … 2022-12 (as available)

One row per market-month. Blank value + `STATUS = GAP` for anything unverified. **No interpolation.**

| YEAR | MONTH | MARKET | occupancy_rate | ADR_CAD | RevPAR_CAD | SOURCE | PROVENANCE | STATUS |
|---|---|---|---|---|---|---|---|---|
| 2005 | 1 | Montreal |  |  |  |  |  |  |
| … | … | … | … | … | … | … | … | … |
| 2022 | 12 | Calgary |  |  |  |  |  |  |

Then the identical data as a fenced CSV block:

```csv
YEAR,MONTH,MARKET,occupancy_rate,ADR_CAD,RevPAR_CAD,SOURCE,PROVENANCE,STATUS
2005,1,Montreal,,,,,,
...
2022,12,Calgary,,,,,,
```

### Table 2 — Per-market, per-year citation

| Market | Year(s) | Source product (exact) | Access route | Months found | Notes |
|---|---|---|---|---|---|
| Montreal |  |  |  |  |  |
| Calgary |  |  |  |  |  |

### Table 3 — Event-spike & reconciliation check (the reason this file exists)

| Check | Expected (dr_L3-01) | Your extracted value | Pass / Flag |
|---|---|---|---|
| Montréal 2019 annual-avg | ~0.73 |  |  |
| Calgary 2019 annual-avg | ~0.62 |  |  |
| Calgary July (Stampede) vs Calgary annual-avg, a typical pre-COVID year | July markedly higher (often > 0.85 peak) |  |  |
| Montréal June (Grand Prix/festivals) vs annual-avg, pre-COVID | June elevated |  |  |
| Market minus provincial, 2019 | Montréal > QC by ~8–13 pp; Calgary > AB by ~4–8 pp |  |  |
| 2020-04 downtown trough | Montréal downtown < 0.04; Calgary 0.03–0.08 |  |  |

---

## Part C — Synthesis (short)

1. **Coverage verdict** per market (months OK / GAP), and which source carried each stretch.
2. **Downtown-vs-provincial gap:** quantify the 2019 offset you found for each city — this is the
   evidence for whether the provincial driver needs a downtown-context caveat in the paper.
3. **Event-spike fidelity:** did you capture the Stampede/Grand-Prix months, or are they in the gaps?

## Output format (follow exactly)

1. **Table 1 (markdown) + identical CSV block first.**
2. Then Tables 2–3, then Part C.
3. Inline citations; keep open-licence (ISQ regional) distinct from proprietary (CBRE/STR).
4. **"Confidence and caveats."**
5. **Reference list** — full citations, retrieval dates, live URLs. No proprietary PDF redistribution.

## Hard requirements

- **Validation context only** — clearly labelled; never presented as the canonical driver.
- **No fabricated values**; unverified = blank + `GAP`; per-year citation mandatory.
- **No interpolation / smoothing / carry-forward.** Capture event-spike months verbatim.
- **occupancy_rate as 0–1 fraction**; all COVID months kept.
- **Two markets only** (Montréal, Calgary); provincial series live in `dr_L3v2-01A/01B`.
- **Reachability-proof rule (v2.1):** every non-blank value's source was opened this session and carries
  a pasted snippet + working URL in Table 2 — otherwise the value is blank + `GAP`.

## Progress Log

### 2026-07-18 — 01C executed by cheap agent under token cap

Executed under the cost-discipline cap (~13 web actions, close to the 8–12 budget). Report written to
`dr_L3v2-01C_market_montreal_calgary_REPORT.md`. **Coverage: Montreal 1 month OK (2020-04 COVID trough,
~3%); Calgary 0 months OK.** All other 430 of 432 market-months are `GAP` — true monthly series are
paywalled (CBRE/STR, Calgary) or trapped behind a non-scriptable ISQ Power BI dashboard (Montréal; same
blocker `dr_L3v2-01A` hit for QC). Recovered 4 annual/quarterly headline figures instead (Montréal 2019
73.1% / 2022 60.7%; Calgary 2019 61–62% / 2022 58–52%), reported only in Table 3 (reconciliation), not
forced into Table 1 monthly rows. Table 3 reconciliation: Montréal 2019 annual-avg PASS (0.731 vs
expected ~0.73); Calgary 2019 annual-avg PASS (0.61–0.62 vs expected ~0.62); market-minus-provincial gap
PASS for both cities (caveated); 2020-04 downtown trough PASS for Montréal, FLAG/no-data for Calgary;
**Stampede (July) and Grand Prix (June) event-spike checks are FLAG — no in-window (2005–2022) numeric
point was freely recoverable for either, only qualitative/out-of-window corroboration.** Validation-context
only; never to be treated as the canonical Hotel-channel driver (that remains the provincial series in
01A/01B). Report also flags that `01B`'s (AB) suspiciously complete zero-GAP monthly series is
unaudited and should not be taken at face value for downstream reconciliation.
