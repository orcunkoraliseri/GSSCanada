# Deep-Research Prompt dr_L3-01 — STATCAN HOTEL-OCCUPANCY DATA (exact tables, coverage, access, breaks)

> SCOPE GUARD — READ FIRST. This is the **data-acquisition** task of the Leg-3 set. Its job is to name
> the exact, currently-published sources for a **MONTHLY hotel-occupancy-rate series by PROVINCE**
> (Quebec + Alberta at minimum) covering **2005–2022**, and precisely how to obtain them. Do NOT derive
> diurnal guest-room shapes (that is `dr_L3-05`), do NOT benchmark hotel energy use (that is
> `dr_L3-03`), and do NOT redesign the forecast — the recipe is already fixed:
> SARIMA(1,1,1)(1,1,1,12) per province with a COVID indicator (2020-03…2022-06). See
> `00_deep_research_prompts_Leg3.md` for the set's shared facts and conventions.

---

## What this document is

A source-verification and acquisition brief. We build a 4-channel occupancy pipeline (Residential /
Office / Retail / Hotel) for Canadian mixed-use tall-building energy models. The Hotel channel cannot
come from time-use surveys (residents are not sampled as guests in their own city's hotels; tourists
are out of frame), so it is driven by an external monthly occupancy-rate series that scales a fixed
diurnal guest-room shape. The target file is:

```
hotel_occupancy_monthly.csv:  YEAR, MONTH, PR, occupancy_rate (0–1), ADR_CAD, RevPAR_CAD
```

Our planning docs reference "Statistics Canada Table 24-10-0048-01 or successor" — that ID was written
from memory and **must be verified, not trusted**. This prompt replaces "or successor" with named,
confirmed tables.

## Role

Canadian official-statistics and tourism-data specialist. Ground every claim in Statistics Canada's own
catalogue (Common Output Data Repository table metadata, survey/program documentation for accommodation
statistics), then in the commercial and destination-marketing sources that fill StatCan's gaps: CBRE
Hotels Canada (National Market Report / Trends), STR (CoStar) Canadian market data, Destination Canada,
Tourisme Québec, Travel Alberta. Distinguish clearly between what StatCan itself publishes and what is
third-party.

## Why this matters (so you scope correctly)

Everything downstream of the hotel channel multiplies this series: the 48-slot guest-room schedules,
the SARIMA 2030 forecast, and the hotel EUI validation gates. Two design decisions hang directly on
your answer: (a) if monthly *provincial* data does not reach back to 2005, the backcast validation gate
(QC+AB 2015–2019, MAE < 0.05) and the training window of the SARIMA change; (b) if occupancy_rate is
only published annually or only nationally for part of the window, we must decide between interpolation
and a fallback source *before* the build starts.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Candidate Statistics Canada tables (verify against the live catalogue)

One row per candidate table, including 24-10-0048-01 (confirm it exists / existed), its predecessors,
successors, and any other accommodation-occupancy tables found.

| Table ID | Exact title | Variables (occupancy rate / ADR / RevPAR / other) | Geography levels | Frequency | Years covered | Status (active / terminated → successor) | Source link |
|---|---|---|---|---|---|---|---|
| 24-10-0048-01 (VERIFY) |  |  |  |  |  |  |  |
| (predecessor, if any) |  |  |  |  |  |  |  |
| (successor / alternative 1) |  |  |  |  |  |  |  |
| (alternative 2) |  |  |  |  |  |  |  |

### Table 2 — QC + AB monthly coverage map, 2005–2022

Which source covers which stretch of our window at monthly × provincial resolution. Mark breaks.

| Source | 2005–2009 | 2010–2014 | 2015–2019 | 2020–2022 | Known breaks / redesigns / COVID collection changes |
|---|---|---|---|---|---|
| StatCan (best table from Table 1) |  |  |  |  |  |
| CBRE Hotels Canada |  |  |  |  |  |
| STR / CoStar |  |  |  |  |  |
| Provincial tourism bodies |  |  |  |  |  |

### Table 3 — Access route and licensing

| Source | Programmatic access (StatCan Web Data Service API / CODR full-table CSV / report PDFs) | Licence / terms for academic use | Required citation format |
|---|---|---|---|
| StatCan |  |  |  |
| CBRE Hotels Canada |  |  |  |
| STR / CoStar |  |  |  |
| Destination Canada / provincial bodies |  |  |  |

### Table 4 — Fallback and complementary sources, ranked

| Source | Geography | Frequency | Years | Cost / access barrier | Fitness for filling StatCan gaps (High/Med/Low) + why |
|---|---|---|---|---|---|
| CBRE Hotels Canada |  |  |  |  |  |
| STR (CoStar) |  |  |  |  |  |
| Tourisme Québec |  |  |  |  |  |
| Travel Alberta |  |  |  |  |  |
| Destination Canada |  |  |  |  |  |

### Table 5 — Sanity magnitudes (for validating whatever we download)

| Quantity | Value | Source |
|---|---|---|
| QC annual-average occupancy, pre-COVID (2015–2019) |  |  |
| AB annual-average occupancy, pre-COVID (2015–2019) |  |  |
| Montreal market occupancy, pre-COVID (if published) |  |  |
| Calgary market occupancy, pre-COVID (if published) |  |  |
| 2020-04 COVID trough (national and/or QC, AB) |  |  |
| 2022 recovery level (vs 2019) |  |  |

---

## Part C — Synthesis (the acquisition recipe)

Give: (1) the **recommended primary + fallback combination** that yields a QC+AB monthly series
2005–2022, with the exact splice points if two sources must be joined; (2) a **data-dictionary verdict**
against our schema — for each column (`occupancy_rate`, `ADR_CAD`, `RevPAR_CAD`), which source fills it
and which cannot; (3) **implications for the SARIMA design** if the usable series starts later than
2005 or contains a break (e.g., shorter training window, level-shift dummy at a splice); (4) any reason
to prefer a *market-level* (Montreal / Calgary) series over the provincial one, given the simulated
buildings sit in those two downtown markets.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations throughout; keep StatCan-catalogue citations distinct from third-party citations.
4. **"Confidence and caveats":** which cell is least certain and what would resolve it.
5. **Reference list** — full citations, dates, URLs/DOIs (StatCan table links must be to the live table
   page, not a search page).

## Hard requirements

- **Verify every table ID against the live StatCan catalogue** — do not repeat "24-10-0048-01" back
  without confirming its existence, exact title, and active/terminated status.
- For each source, state **monthly? provincial? back to 2005?** as three explicit YES/NO answers — no
  hedging by omission.
- **No fabricated precision** (no invented table IDs, no guessed coverage years); flag GAPs explicitly.
- **Stay on topic** — acquisition and coverage only; no diurnal shapes, no EUI, no forecasting method
  comparisons.
