# Deep-Research Prompt dr_L3v2-01A (GEMINI-WEB / Deep Research edition) — QUÉBEC (ISQ) MONTHLY HOTEL-OCCUPANCY SERIES EXTRACTION (2005–2022)

> **Which edition is this?** This is the **Gemini web "Deep Research"** edition: you browse, then return
> ONE finished report **inline in the chat**. There is no file to write, no multi-step agent pipeline —
> just produce the tables + citations described under REQUIRED OUTPUT at the end of your run. (An
> Antigravity edition with an explicit agent pipeline that writes the report file exists as a sibling
> file; ignore it here.)

> SCOPE GUARD — READ FIRST. This is a **DATA-EXTRACTION / TRANSCRIPTION** task, not a design or
> literature task. Your only job: retrieve, from the **Institut de la statistique du Québec (ISQ)**
> accommodation-frequentation program, the **monthly, Québec-provincial** hotel **occupancy rate** (and,
> where published, **ADR** and **RevPAR**) for **every month 2005-01 → 2022-12** (216 months) and
> transcribe it faithfully into the fixed schema below. Do NOT choose the source (it is fixed: ISQ), do
> NOT design the forecast, do NOT interpolate or smooth.

---

## ⚠️ v2.2 HARDENING + ROUTING — READ BEFORE YOU START (updated 2026-07-19)

Two prior runs of this prompt failed the same way: they hit the ISQ **Power-BI dashboard** (export
disabled), gave up, and returned ~100 % GAP (one recovered only 20 summer months from a blog). **Do not
repeat that.** The sibling Alberta task was rescued by abandoning the live dashboard and going to an
**open-data / static / archived** source instead. Apply that same lesson to Québec.

### CONFIRMED DEAD ENDS — do NOT spend browsing budget re-checking these
1. **ISQ Power-BI dashboard** on `statistique.quebec.ca` — the interactive « taux d'occupation »
   dashboard has **data export disabled**; it is not scriptable and not transcribable. Skip it.
2. **Données Québec** (`donneesquebec.ca`, CKAN) — verified 2026-07-19: it hosts only the **SIT Québec
   establishment registries** (Hôtels, Gîtes, Campings, Chalets — coordinates/types, in CSV/JSON/XML).
   It does **NOT** host the monthly taux-d'occupation time series. Do not re-probe it for occupancy.

### PRIORITY ROUTES TO TRY (in this order) — the actual opportunity
1. **Internet Archive / Wayback Machine (`web.archive.org`).** Before ISQ migrated to Power-BI it
   published **static Excel/PDF tables** of « taux d'occupation des établissements hôteliers ». Search
   archived snapshots (~2010–2019) of `statistique.quebec.ca`, the old `stat.gouv.qc.ca`, and
   `bdso.gouv.qc.ca` for those static tables. **This is the single most promising untried route.**
2. **BDSO — Banque de données des statistiques officielles sur le Québec** (`bdso.gouv.qc.ca`). Check
   for a downloadable frequentation / occupation table (HTML table, XLS, or CSV export).
3. **AHQ — Association Hôtellerie du Québec** (`hotelleriequebec.com`). The prior run found Jul/Aug via
   one retrospective post. **Sweep the WHOLE site** (news/blog archive, annual « bilans ») for any other
   months — they re-publish ISQ figures verbatim.
4. **Tourisme Montréal industry portal** (`industrie.mtl.org`) + **Institut du Québec**
   (`institutduquebec.ca`). These carry **Montréal market** monthly occupancy. Montréal ≈ the Zone-6A
   simulated building, so Montréal-market months are useful — but **tag them clearly as market-level, not
   provincial**, in PROVENANCE (do not silently pass a Montréal number as a QC-provincial number).
5. **Tourisme Québec legacy « performance touristique » bulletins** and ISQ « Bulletin statistique
   régional » / « Panorama des régions » — mostly **annual** figures → use for Table-3 reconciliation
   only, never spread into monthly cells.

### Non-negotiable anti-fabrication rules (unchanged from v2.1)
- **PROVE REACHABILITY.** Every non-blank value's source must have been **opened by you in this run**.
  In Table 2, paste a short **verbatim snippet** (a table header, the printed figure, one sentence) +
  the **exact working URL**. **No snippet, no data** → leave the cell blank + `STATUS = GAP`.
- **NEVER invent an endpoint, table ID, or file URL.** 404 / blocked / login → GAP, never a plausible
  substitute. (A prior sibling run was discarded for citing a fabricated API.)
- **PAYWALL / LOGIN = GAP.** CBRE/STR and any sign-in-gated data = GAP.
- **20 verified months beat 216 invented ones.** Honest partial coverage is a SUCCESS; a complete-looking
  uncited series is a FAILED report and will be discarded.

---

## What this document is

A monthly-series harvest brief for the **Hotel channel** of a 4-channel GSS→BEM occupancy pipeline (Leg 3
of 3). The Hotel channel is the one non-GSS channel: a monthly provincial occupancy series scales a fixed
48-slot guest-room diurnal shape, and a SARIMA(1,1,1)(1,1,1,12)+COVID forecast projects it to 2030.
**Québec is one of the two driving provinces** (Montréal, Zone 6A). This series feeds the guest-room
People schedules, the SARIMA backcast gate (QC 2015–2019 MAE < 0.05), and the hotel EUI gates — a
fabricated or mis-transcribed month propagates into published energy results.

Target schema (this prompt fills the QC rows):
```
YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```

- **occupancy_rate** — the non-negotiable column. QC = the provincial **taux d'occupation**, monthly.
  Convert every published percent to a **decimal fraction** (65.2 % → 0.652).
- **ADR_CAD** = ISQ « prix moyen de location » (average daily rate), CAD. **RevPAR_CAD** = ISQ « revenu
  de location par unité disponible » (RUD) when published; if a month has occupancy + ADR but no RUD you
  MAY back-compute `RevPAR = occupancy × ADR` and set `STATUS = COMPUTED`. Never compute occupancy/ADR.
- **COVID months are signal, not gaps.** Keep 2020-03 … 2022-06 exactly as published.
- `SOURCE` short tag (`ISQ`, `ISQ via AHQ`, `BDSO`, `TourismeMontreal`, `Wayback/ISQ` …).
- `STATUS` ∈ {`OK`, `GAP`, `COMPUTED`}.

---

## REQUIRED OUTPUT (return all of this INLINE, in order)

### Table 1 — QC monthly series, 2005-01 … 2022-12 (216 rows)

One row per month, `PR = QC`. Blank value + `STATUS = GAP` for any month you cannot verify — no
interpolation, no carry-forward, no estimate.

| YEAR | MONTH | PR | occupancy_rate | ADR_CAD | RevPAR_CAD | SOURCE | PROVENANCE | STATUS |
|---|---|---|---|---|---|---|---|---|
| 2005 | 1 | QC |  |  |  | ISQ |  | GAP |
| … | … | … | … | … | … | … | … | … |
| 2022 | 12 | QC |  |  |  | ISQ |  | GAP |

Then the **identical data as a fenced ```csv block** with the exact header, so it pastes straight into the
pipeline.

### Table 2 — Per-year source citation WITH reachability proof (18 rows, 2005–2022)

For each year: the specific product/page you opened, the access route, months found, and a **pasted
verbatim snippet + working URL** for at least one value that year. A year with no citable, opened origin
must be reported as fully GAP — not filled.

| Year | Product / page (exact) | Access route | Months found (of 12) | Verbatim snippet + URL | Notes |
|---|---|---|---|---|---|

### Table 3 — Reconciliation against dr_L3-01 sanity magnitudes (flag, do not adjust)

| Check | Expected | Your value | Pass / Flag |
|---|---|---|---|
| QC annual-avg occupancy, mean 2015–2019 | 0.60–0.65 |  |  |
| 2020-04 QC occupancy (COVID trough) | very low |  |  |
| Seasonal shape | summer (Jun–Sep) > winter (Jan–Mar), non-COVID | |  |
| Monotonic recovery | 2021 < 2022 < 2019 annual-avg |  |  |

### Part C — Synthesis (short)
1. Coverage verdict: of 216 months, how many OK / GAP / COMPUTED; which route carried the bulk.
2. Which of the PRIORITY ROUTES paid off and which were dead; the single most-productive source.
3. Least-certain cells and the exact export that would resolve them.

Then: **"Confidence and caveats"** + a **Reference list** (full citations, retrieval dates, live URLs —
the actual data page, not a search page). Keep ISQ/open-licence citations distinct from market-level ones.

## Hard requirements (recap)
- No fabricated values; unverified = blank + `GAP`; every non-blank cell traces to a Table-2 snippet+URL.
- No interpolation / smoothing / seasonal-adjustment / carry-forward.
- occupancy_rate as 0–1 fraction; keep all COVID months; RevPAR may be `COMPUTED` (flagged) only.
- Stay on **QC** (Alberta is a separate task); no StatCan occupancy table exists — do not cite one.
- Montréal-market months allowed but **must be tagged market-level in PROVENANCE**, never passed as QC-provincial.
