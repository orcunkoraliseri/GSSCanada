# Deep-Research Prompt dr_L3v2-01A — QUÉBEC (ISQ) MONTHLY HOTEL-OCCUPANCY SERIES EXTRACTION (2005–2022)

> SCOPE GUARD — READ FIRST. This is a **DATA-EXTRACTION / TRANSCRIPTION** task, not a design or
> literature task. Your only job is to retrieve, from the **Institut de la statistique du Québec (ISQ)**
> accommodation-frequentation program, the **monthly, Québec-provincial** hotel **occupancy rate** (and,
> where published, **ADR** and **RevPAR**) for **every month from 2005-01 to 2022-12** — 216 months — and
> transcribe it faithfully into the fixed schema below. Do NOT choose the source (it is fixed: ISQ), do
> NOT design the forecast, do NOT benchmark energy use, do NOT interpolate or smooth. The source was
> already verified in `dr_L3-01_statcan_hotel_data_REPORT.md`; this prompt only harvests the numbers it
> named.

---

## ⚠️ v2.1 HARDENING — LEARN FROM THE FAILED FIRST RUN (read before you start)

A prior run of this prompt set **failed in two ways you must not repeat**:
- One sibling run **fabricated** a full monthly series — it cited an API endpoint that returns HTTP 404
  and an "open-government" source for paywalled years that does not exist. Plausible-looking invented
  numbers are the **worst** possible outcome: they poison published energy results silently.
- The prior QC run returned **100 % GAP** because it could not operate the ISQ Power-BI dashboard and
  gave up without trying the static downloadable alternatives.

You are being run in **Gemini Deep Research (web browsing)**. Therefore:

1. **PROVE REACHABILITY.** For every source you cite, you must have actually opened it in THIS session.
   In Table 2, for each cited source paste a short **verbatim snippet** from the live page/file (a table
   header, a printed figure, one sentence) plus the **exact working URL**. A number whose source you did
   not actually load = blank value + `STATUS = GAP`. **No snippet, no data.**
2. **NEVER invent an endpoint, table ID, or file URL.** If a URL 404s, is blocked, or needs a login,
   say so and GAP the affected months — do NOT substitute a plausible-looking alternative you didn't open.
3. **PAYWALL / LOGIN = GAP.** If data sits behind a paywall or sign-in you cannot pass, you cannot use
   it. Never claim paywalled data is "open."
4. **INTERACTIVE-DASHBOARD REALITY.** The ISQ series lives in a Power-BI dashboard whose export is
   disabled. Do not stop there: hunt for the **static** form — ISQ « Statistiques principales » /
   « Bulletin statistique » Excel/PDF, the ISQ *banque de données statistiques* tables, Tourisme Québec
   annual « performance touristique » reports — and prove you opened whichever carries the monthly taux
   d'occupation. GAP what genuinely remains.
5. **20 verified months beat 216 invented ones.** Honest, well-cited partial coverage is a SUCCESS here;
   a complete-looking uncited series is a FAILED report and will be discarded.

---

## What this document is

A monthly-series harvest brief for the Hotel channel of a 4-channel GSS→BEM occupancy pipeline (Leg 3
of 3). The Hotel channel is the one non-GSS channel: a monthly provincial occupancy series scales a
fixed 48-slot guest-room diurnal shape, and a SARIMA(1,1,1)(1,1,1,12)+COVID forecast projects it to
2030. **Québec is one of the two driving provinces** (Montréal, Zone 6A). This series feeds the
guest-room People schedules, the SARIMA backcast gate (QC 2015–2019 MAE < 0.05), and the hotel EUI
gates — so a fabricated or mis-transcribed month propagates into published energy results. Accuracy and
honest gaps matter more than completeness.

Target file (this prompt fills the QC rows):
```
YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```

## Role

Québec tourism-statistics data-extraction specialist. Work **exclusively** from ISQ / Ministère du
Tourisme du Québec published outputs of the **« Enquête sur la fréquentation des établissements
d'hébergement du Québec »** (the monthly accommodation-frequentation survey, running since 1983,
provincial scope, structurally consistent 2005–2022, **no splice needed**). Portal entry point:
https://www.quebec.ca/tourisme-et-loisirs/services-industrie-touristique/etudes-statistiques and the
ISQ statistics pages / Power-BI dashboards it links to. Browse the actual published tables/dashboards
and transcribe; do not reconstruct from memory.

## Why this matters (so you scope correctly)

- **occupancy_rate** is the driver — this is the non-negotiable column. QC = the **taux d'occupation**
  (occupancy rate) for the province, monthly. Convert every published percent to a **decimal fraction**
  (65.2 % → 0.652).
- **ADR_CAD** = the ISQ **« prix moyen de location »** (average rental price / average daily rate),
  monthly provincial, in CAD.
- **RevPAR_CAD** = the ISQ **« revenu de location par unité disponible » (RUD)** when published; if a
  given month publishes occupancy and ADR but not RUD, you MAY back-compute `RevPAR = occupancy_rate ×
  ADR_CAD` and mark that cell `STATUS = COMPUTED`. Never compute occupancy or ADR — only RevPAR.
- **COVID months are signal, not gaps.** Keep 2020-03 … 2022-06 exactly as published (occupancy will
  crater to very low values in QC/Montréal — that is correct and required for the SARIMA COVID dummy).

---

## REQUIRED OUTPUT — fill every month you can verify; mark the rest GAP

### Table 1 — QC monthly series, 2005-01 … 2022-12 (216 rows)

One row per month. `PR = QC`. `SOURCE = ISQ` (or the exact ISQ product name in PROVENANCE). Leave a
value cell **blank** and set `STATUS = GAP` for any month you cannot verify from the source — **do not
interpolate, do not carry forward, do not estimate.**

| YEAR | MONTH | PR | occupancy_rate | ADR_CAD | RevPAR_CAD | SOURCE | PROVENANCE | STATUS |
|---|---|---|---|---|---|---|---|---|
| 2005 | 1 | QC |  |  |  | ISQ |  |  |
| … | … | … | … | … | … | … | … | … |
| 2022 | 12 | QC |  |  |  | ISQ |  |  |

Then repeat the **identical data** as a fenced CSV block (exact header, no extra columns), so it pastes
straight into the pipeline:

```csv
YEAR,MONTH,PR,occupancy_rate,ADR_CAD,RevPAR_CAD,SOURCE,PROVENANCE,STATUS
2005,1,QC,,,,ISQ,,
...
2022,12,QC,,,,ISQ,,
```

### Table 2 — Per-year source citation (18 rows, one per year 2005–2022)

For each year, name the *specific* ISQ product/page/dashboard extract the 12 months came from, and how
you accessed it. This is the anti-fabrication control — a year with no citable origin must be reported
as fully GAP, not filled.

| Year | ISQ product / dashboard / table (exact name) | Access route (portal page, Power-BI export, PDF) | Months found (of 12) | Notes / breaks / definition changes |
|---|---|---|---|---|
| 2005 |  |  |  |  |
| … |  |  |  |  |
| 2022 |  |  |  |  |

### Table 3 — Reconciliation against the dr_L3-01 sanity magnitudes

Compute the annual averages from YOUR extracted data and compare to the known bands. Flag — do not
adjust — any violation.

| Check | Expected (dr_L3-01) | Your extracted value | Pass / Flag |
|---|---|---|---|
| QC annual-avg occupancy, mean of 2015–2019 | 0.60–0.65 |  |  |
| 2020-04 QC occupancy (COVID trough) | very low (Montréal downtown < 0.04; provincial higher but historically minimal) |  |  |
| Seasonal shape sanity | summer (Jun–Sep) > winter (Jan–Mar) every non-COVID year |  |  |
| Monotonic-recovery sanity | 2021 annual-avg < 2022 annual-avg < 2019 annual-avg |  |  |

---

## Part C — Synthesis (short)

1. **Coverage verdict:** of 216 QC months, how many are `OK`, how many `GAP`, how many RevPAR
   `COMPUTED`. Name the exact ISQ product that carried the bulk of the series.
2. **Definition notes:** does ISQ's occupancy denominator (rooms available) change anywhere in the
   window (e.g., the 2025 census-mode shift is out of window, but flag any in-window redesign)? Does
   "établissements d'hébergement" include non-hotel accommodation that would bias the rate for a
   downtown-hotel use case? State it; do not correct for it.
3. **Least-certain cells:** which years/months are weakest and what specific ISQ export would resolve
   them.

## Output format (follow exactly)

1. **Lead with Table 1 (markdown) immediately followed by the identical CSV block.**
2. Then Table 2 (per-year citations), Table 3 (reconciliation), then Part C.
3. Inline citations throughout; ISQ-catalogue citations kept distinct from any third-party context.
4. **"Confidence and caveats":** the single least-certain stretch and what would resolve it.
5. **Reference list** — full citations with retrieval dates and live URLs (link to the actual ISQ
   data page / dashboard, not a search page).

## Hard requirements

- **No fabricated values.** Every non-blank `occupancy_rate`/`ADR_CAD` cell must be traceable to the
  `PROVENANCE` you cite for it (or its year's Table-2 row). A month you cannot verify = blank value +
  `STATUS = GAP`. **A plausible-looking full series with no per-year citation is a failed report.**
- **No interpolation, smoothing, seasonal-adjustment, or carry-forward** to fill gaps. Report the holes.
- **occupancy_rate as a 0–1 fraction**, three decimals where the source allows; state the source's
  native precision if coarser.
- **Keep all COVID months** (2020-03 …) as published — never drop or normalize them.
- **RevPAR** may be `COMPUTED` (flagged) only as `occupancy × ADR`; occupancy and ADR are never derived.
- **Stay on QC only** — Alberta is a separate prompt (`dr_L3v2-01B`); do not mix provinces.
- **No StatCan occupancy table** exists — do not cite one (dr_L3-01 confirmed this).
- **Reachability-proof rule (v2.1):** every non-blank value's source was opened in this session and
  carries a pasted verbatim snippet + working URL in Table 2 — otherwise the value is blank + `GAP`.
  A citation you did not actually load does not count.

## Progress Log

### 2026-07-19 — Split into two tool-specific v2.2 editions (this base file is now superseded for running)

This base prompt is kept for provenance; **run one of the two new editions instead**, both in this folder:
- `dr_L3v2-01A_isq_qc_monthly_extraction_prompt_GEMINIWEB.md` — Gemini web Deep Research; returns the
  report **inline** (no file pipeline).
- `dr_L3v2-01A_isq_qc_monthly_extraction_prompt_ANTIGRAVITY.md` — Gemini Antigravity; runs a 5-stage
  **agent pipeline** (RECON → FETCH+PROVE → TRANSCRIBE → RECONCILE → WRITE REPORT) that ends by writing
  `dr_L3v2-01A_isq_qc_monthly_extraction_REPORT.md` + a self-audit.

Both editions add **v2.2 routing** learned from the Alberta win (open-data beats the live dashboard):
- **CONFIRMED DEAD ENDS (do not re-probe):** (1) ISQ Power-BI dashboard (export disabled); (2) **Données
  Québec CKAN — verified 2026-07-19 to host only SIT Québec establishment registries, NOT the monthly
  taux-d'occupation series.**
- **New priority routes:** Wayback Machine snapshots of pre-migration ISQ static Excel/PDF occupancy
  tables (top lead); BDSO (`bdso.gouv.qc.ca`); exhaustive AHQ site sweep; Tourisme Montréal `industrie.mtl.org`
  + Institut du Québec (market-level, tag as such); Tourisme Québec legacy annual bulletins (Table-3 only).

### 2026-07-18 — Retry via non-Power-BI routes (token-capped)

Prior run 100%-GAP'd on the ISQ Power-BI dashboard (needs browser automation). This retry searched ~10
alternative static/secondary routes under a ~12-16 web-call budget instead of retrying Power BI.

**Result: 20 of 216 QC months OK (9.3%), 196 GAP, 0 RevPAR COMPUTED.** The 20 OK cells are July + August
of each year 2013–2022, transcribed from an Association Hôtellerie du Québec (AHQ) blog re-publication of
ISQ *Enquête sur la fréquentation des établissements d'hébergement du Québec* results
(hotelleriequebec.com) — a secondary/once-removed source, not a raw ISQ table, flagged as such. No ADR or
RevPAR was recovered anywhere, so RevPAR remains fully GAP (nothing to COMPUTE from).

Confirmed (re-derived independently): the quebec.ca ISQ results page still states data export is not
currently possible — Power BI remains the only route on that domain, matching the prior run's root cause.
Two other leads (`observat.qc.ca` QC-wide comparison table, `tourisme.gouv.qc.ca` legacy bulletin page)
were found but blocked (HTTP 403 / TLS cert error respectively) — logged as unresolved next steps, not
worked around. An independent 2019 annual figure (HRImag/TourismExpress, ~60% occupancy) was used only for
Table-3 reconciliation (falls inside the dr_L3-01 0.60–0.65 band) — not spread into monthly cells per the
anti-fabrication rule.

Full report: `dr_L3v2-01A_isq_qc_monthly_extraction_REPORT.md` (overwritten, same filename).
