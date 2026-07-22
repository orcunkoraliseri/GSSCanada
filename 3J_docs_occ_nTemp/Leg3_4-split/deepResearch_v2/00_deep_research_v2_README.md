# Deep-Research Prompt Set — Leg 3 **v2 (DATA EXTRACTION, not design)**

### README — roster, shared facts, and run conventions for the `dr_L3v2-*` extraction prompts

**Purpose.** The v1 set (`../deepResearch/dr_L3-*`) closed *design* gaps (which tables exist, EUI
bands, diurnal shapes, forecast recipe). This **v2 set closes the one remaining acquisition gap it
left open: the actual monthly hotel-occupancy numbers.** dr_L3-01 confirmed *where* the data lives
(ISQ for QC, Alberta Economic Dashboard / CBRE for AB) and that **no StatCan table publishes it**; it
did **not** return the series itself. These v2 prompts are run in a browsing deep-research tool
(**Gemini Antigravity**) to retrieve and transcribe that series **in place of the manual portal
downloads** — so the Step-1 hotel ingest (`3rdJ_01_hotelIngest_4split.py`, Section B) can consume a
ready CSV instead of hand-downloaded files.

> **This is transcription-with-provenance, not synthesis.** The single greatest failure mode here is a
> model *inventing* plausible month-by-month occupancy values it did not actually read from the source.
> Every prompt below is built to make fabrication impossible-to-hide: per-value provenance, an explicit
> GAP status for anything not found, a hard no-interpolation rule, and a reconciliation check against
> the dr_L3-01 sanity magnitudes. **A report that returns a full 216-month series with no per-year
> source citations is to be rejected outright.**

> ### ⚠️ v2.1 update (2026-07-18) — a first run FAILED; prompts hardened
> The first pass proved the failure mode is real, not hypothetical:
> - **01B (Alberta) fabricated its whole series** — it cited an API endpoint (`api.economicdata.alberta.ca`)
>   that returns HTTP 404 and an "open" 2005–2009 source that does not exist. **That report is discarded.**
> - **01A (Québec) returned 100 % GAP** (ISQ Power-BI export disabled) on the first try; a retry via
>   secondary routes recovered only ~20 real months (Jul/Aug 2013–2022) — honest but too thin to drive
>   the SARIMA.
> - **01C (markets)** returned only annual anchors (validation context only — acceptable).
>
> **Lesson:** the real hotel data sits behind interactive Power-BI dashboards (ISQ) and export controls
> (Alberta) that agents cannot reliably drive; when they can't reach it, they either GAP (good) or
> fabricate (fatal). All three prompts now carry a **v2.1 HARDENING** block and a **reachability-proof
> rule**: every non-blank value must be backed by a source the tool actually opened in-session, with a
> pasted verbatim snippet + working URL in Table 2 — no snippet, no data. Run these in **Gemini Deep
> Research (web browsing)**. **If deep research still can't reach the series, the fallback is a manual
> portal download by the user** (Step-1 §B) — an honest GAP is always preferred over an invented value.

---

## Roster

| # | Prompt file | Extracts | Feeds | Priority |
|---|---|---|---|---|
| dr_L3v2-01A | `dr_L3v2-01A_isq_qc_monthly_extraction_prompt.md` | QC provincial monthly occupancy + ADR + RevPAR, 2005-01…2022-12 (ISQ) | Step-1 Section B → `hotel_occupancy_raw_assembled.csv` (QC rows) | **REQUIRED** |
| dr_L3v2-01B | `dr_L3v2-01B_alberta_ab_monthly_extraction_prompt.md` | AB provincial monthly occupancy + ADR + RevPAR, 2010-01…2022-12 (Alberta Dashboard) + 2005-01…2009-12 (CBRE archive, *if obtainable*) | Step-1 Section B → QC/AB rows; Step-2D splice | **REQUIRED** (2010–2022) + *optional* (2005–2009) |
| dr_L3v2-01C | `dr_L3v2-01C_market_montreal_calgary_extraction_prompt.md` | Montréal + Calgary **market-level** monthly series, 2005–2022 as available | Validation context only (`hotel_occupancy_monthly_markets.csv`); NOT the canonical driver | *Bonus* |

Run order: **01A and 01B first** (they populate the canonical driver); **01C** any time (validation
context). 01A and 01B are independent — run in parallel.

---

## The one target schema (all three prompts emit exactly this)

```
YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```

- `YEAR` 2005–2022 · `MONTH` 1–12 · `PR` ∈ {QC, AB} (01A/01B) or market label (01C).
- `occupancy_rate` = **decimal fraction 0–1** (convert any published percent: 65.2 % → 0.652).
- `ADR_CAD`, `RevPAR_CAD` = Canadian dollars; blank if the source does not publish it.
- `SOURCE` = short tag (`ISQ`, `ABDASH`, `CBRE`, `STR`).
- `PROVENANCE` = the *specific* origin of THIS cell's value (report title + period + table/page, or the
  exact dashboard export + retrieval note) — enough for a human to re-find it.
- `STATUS` ∈ {`OK`, `GAP`, `COMPUTED`}. `GAP` = value not found in the source (cell left blank, **never
  guessed**). `COMPUTED` = RevPAR back-computed as `occupancy_rate × ADR_CAD` (allowed only for RevPAR,
  must be flagged).

Deliver the table **twice**: once as a readable markdown table, once as a fenced ```csv block with the
exact header above, so it pastes straight into the pipeline.

---

## Shared facts every v2 prompt assumes (embedded inline in each, repeated here for the record)

- **Project.** GSS-derived 4-channel occupancy pipeline (Leg 3 of 3). The Hotel channel is the one
  non-GSS channel: a monthly provincial occupancy-rate series (QC + AB) scales a fixed 48-slot
  guest-room diurnal shape, and a SARIMA(1,1,1)(1,1,1,12) + COVID-indicator forecast projects it to
  2030. Buildings: PNNL Tall / SuperTall mixed-use prototypes, Montréal Z6 + Calgary Z7A.
- **Window.** 2005-01 … 2022-12 (216 months per province). **All COVID months (2020-03 onward) are
  kept as-is — they are signal for the SARIMA COVID indicator, never a gap to fill.**
- **Sources (fixed by dr_L3-01; do not re-litigate).** QC = Institut de la statistique du Québec (ISQ)
  « Enquête sur la fréquentation des établissements d'hébergement du Québec » (monthly, provincial,
  1983–present, structurally consistent, **no splice**). AB = Alberta Economic Dashboard
  "Accommodation occupancy rate" (CBRE-sourced, monthly, **2010–present**, excludes major resorts
  Banff/Jasper); the 2005–2009 AB gap can only be filled from CBRE Hotels Canada *National Market
  Report* archives (paywalled — optional, splice at Jan-2010). **StatCan publishes no occupancy table
  — do not cite one.**
- **Sanity magnitudes (dr_L3-01 Table 5 — use these to self-check, and flag any year that violates
  them; do NOT force values to fit):**
  - QC annual-average occupancy, 2015–2019: **0.60–0.65**.
  - AB annual-average occupancy, 2015–2019 (excl. resorts): **0.54–0.58**.
  - Montréal market, 2019: **~0.73**; Calgary market, 2019: **~0.62**.
  - 2020-04 COVID trough: national **~0.19**; Montréal downtown **< 0.04**; Calgary **0.03–0.08**.
  - 2022 recovery: Montréal **~0.61** (vs 0.73 in 2019); Calgary **~0.58–0.60**.

## Run conventions

1. Paste the **entire** `_prompt.md` file into Gemini Antigravity (browsing enabled). The SCOPE GUARD
   and anchors are part of the prompt.
2. Every report must return **the dual table (markdown + CSV) + a per-year source-citation table + a
   reconciliation-vs-sanity check + a full reference list**. Reject any report missing per-year
   citations or the CSV block.
3. Save each report as **`dr_L3v2-0N_<shortname>_REPORT.md`** in this folder, next to its prompt.
4. Hand the returned CSV blocks to the Step-1 employee, who drops them under
   `0_Occupancy/external/hotel_raw/<SOURCE>/` (as if downloaded) and re-points Section B's reader at
   them. The Step-2D harmonizer then does the AB Jan-2010 splice and writes the canonical
   `hotel_occupancy_monthly.csv`. **The GAP/COMPUTED flags and PROVENANCE column survive into the
   Progress Log so the paper's data-availability statement is honest.**

> **Verify before trusting (project rule).** Whatever comes back is re-derived and range-checked by the
> Step-1/Step-2 validators against these same sanity bands before any number is quoted — an extracted
> series is treated exactly like a downloaded one, not more.
