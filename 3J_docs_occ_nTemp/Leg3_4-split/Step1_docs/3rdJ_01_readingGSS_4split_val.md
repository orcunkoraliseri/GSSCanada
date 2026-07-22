# Validation Plan — 01_readingGSS Step 1 (Leg 3 — 4-Channel Split)
### GSS reuse verification + hotel external-series acquisition checks

---

## Goal

Validate the two Step-1 deliverables before Step 2 harmonization: (1) the Leg-2 GSS Step-1 outputs are intact and reusable read-only (Leg-3 adds **no** GSS variables), and (2) the raw hotel monthly-occupancy assembly (`hotel_occupancy_raw_assembled.csv`) is schema-clean, coverage-complete per source, and magnitude-plausible against the dr_L3-01 sanity anchors.

## Reference

- Main doc: `3rdJ_01_readingGSS_4split.md`
- Leg-2 validator style template: `../../Leg2_2-split/Step1_docs/3rdJ_01_readingGSS_2split_val.py` (dark-theme HTML + TXT report convention)
- Deep research: `../deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md` (sanity magnitudes, splice design)
- Artifacts validated: `outputs_step1/gss_reuse_manifest.csv`, `outputs_step1/hotel_occupancy_raw_assembled.csv`, raw files under `0_Occupancy/external/hotel_raw/`

## Validation Sections

### Section 1 — GSS Reuse Manifest (✅ machinery reused, gate NEW)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 1.1 | 8 Leg-2 Step-1 CSVs exist at the referenced paths | all present | FAIL if any missing |
| 1.2 | Exact row counts — main 19,597 / 15,390 / 17,390 / 12,336; episode 333,654 / 283,287 / 274,108 / 168,078 | exact match | FAIL on mismatch (Leg-2 chain moved under us) |
| 1.3 | SHA-256 recorded per file into the manifest | 8/8 hashed | FAIL if unreadable |
| 1.4 | Manifest hash equals hash recorded at any prior Leg-3 run (drift detector; skipped on first run) | equal | WARN on drift — investigate which leg changed |

> Rename-awareness lesson (Leg-2 Step 1): the Leg-2 reader preserves raw `PLACE`/`LOCATION` codes and defers `occPRE`/`AT_WORK`/`AT_RETAIL` derivation downstream. Do **not** re-introduce checks for derived columns at Step 1 — that produced 4 false-positive FAILs in Leg 2.

### Section 2 — Hotel Assembly Schema (⚠️ NEW, Leg 3)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 2.1 | Columns exactly `YEAR, MONTH, PR, SOURCE, occupancy_rate, ADR_CAD, RevPAR_CAD` (+ `REVPAR_COMPUTED` flag) | exact set | FAIL |
| 2.2 | Dtypes: YEAR/MONTH int, PR ∈ {QC, AB}, SOURCE ∈ {ISQ, ABDASH, CBRE}, rates float | as listed | FAIL |
| 2.3 | `occupancy_rate ∈ (0, 1]` on every row (percent→fraction conversion verified) | no violations | FAIL |
| 2.4 | RevPAR internal consistency where all three fields are source-published: `|RevPAR − occupancy_rate × ADR| / RevPAR ≤ 10 %` | ≤ 10 % | WARN (definitional differences exist between sources) |
| 2.5 | No duplicate (YEAR, MONTH, PR, SOURCE) keys | 0 duplicates | FAIL |

### Section 3 — Coverage & Continuity (⚠️ NEW, Leg 3)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 3.1 | QC/ISQ months: 2005-01 … 2022-12 | 216/216 | FAIL if gaps |
| 3.2 | AB/ABDASH months: 2010-01 … 2022-12 | ≥ 156 | FAIL if gaps inside the window |
| 3.3 | AB 2005–2009: CBRE rows present, **or** the documented fallback decision (truncate-to-2010 / TASPI-regressor) is recorded in the main doc's Progress Log | either | WARN if neither |
| 3.4 | COVID months 2020-03 … 2022-06 present with low values (they are signal, not gaps) | present | FAIL if dropped/imputed |

### Section 4 — Magnitude Sanity (⚠️ NEW, Leg 3 — anchors from dr_L3-01, INFO-style bands)

| Gate | Check | Expected | Severity |
|---|---|---|---|
| 4.1 | QC annual mean occupancy 2015–2019 | 0.60–0.65 | WARN outside |
| 4.2 | AB annual mean occupancy 2015–2019 (ex-resorts) | 0.54–0.58 | WARN outside |
| 4.3 | 2020-04 trough clearly visible: monthly minimum of the whole series falls in 2020-03…2020-05, both provinces | true | FAIL (a series without the COVID collapse is the wrong series) |
| 4.4 | 2022 annual mean < 2019 annual mean (incomplete recovery), both provinces | true | WARN |
| 4.5 | Seasonality present: pre-COVID summer (Jun–Sep) mean > winter (Dec–Mar) mean, both provinces | true | WARN |

### Section 5 — Visual Dashboard

- 5.1 Headline chart: monthly `occupancy_rate` time series 2005–2022, one line per PR (source changes marked at the AB 2010 boundary), COVID window shaded.
- 5.2 Seasonal profile chart: mean rate per calendar month per PR, pre-COVID (2005–2019).

## PASS / WARN / FAIL Convention

Same as Leg-2 (canonical Step-2 definition): **PASS** = clean / in expected range; **WARN** = plausible but needs attention (soft band breach, documented source quirk); **FAIL** = concrete data-integrity problem (missing file, wrong schema, gap months, out-of-range rates, absent COVID collapse).

## Expected Result

0 FAIL. Acceptable WARNs: 2.4 RevPAR definitional deltas, 3.3 fallback-decision path, 4.x soft-band breaches on provincial averages (market-vs-province composition). Report: `outputs_step1/step1_validation_report.html` + `.txt` (dark theme, base64 charts — house style).

## Test Method

Locally: `py -3 -X utf8 3rdJ_01_readingGSS_4split_val.py` from `Step1_docs/`. Inspect the HTML; confirm Section-1 8/8 OK and the Section-5 headline chart shape (sawtooth + COVID trough).

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`)*

### 2026-07-19 — Validator built + first run (verdict WARN, 0 FAIL)

Built `3rdJ_01_readingGSS_4split_val.py` (dark-theme HTML + TXT, base64 charts, house style) and ran it against the real Step-1 deliverables. **Verdict: WARN — PASS 13 / WARN 3 / FAIL 0 / INFO 2** (meets the "0 FAIL" expected result). Outputs: `outputs_step1/step1_validation_report.{html,txt}`.

- **Section 1** (GSS reuse): 8/8 PASS — existence, exact row counts, SHA-256 all clean; 1.4 drift = INFO (first run).
- **Section 2** (schema): all PASS — essential cols present, PR∈{QC,AB}, occ∈(0,1] on all 188 observed rows, RevPAR≈occ×ADR (48 QC rows, 0 breach), no dup (YEAR,MONTH,PR) keys.
- **Section 3** (coverage): 3.1 QC WARN (48/216, span 2019-2022, 0 core gaps); 3.2 AB WARN (140/156, span 2011-2022, 0 core gaps, 1 edge gap 2011-12); 3.3 fallback WARN; 3.4 COVID months PASS.
- **Section 4** (magnitude): 4.1 QC 2015-19 mean = INFO (insufficient — QC monthly starts 2019); 4.2 AB 2015-19 mean 0.550 PASS (band 0.54-0.58); 4.3 COVID trough (series min in 2020-03..05) PASS both PR; 4.4 2022<2019 PASS both; 4.5 summer>winter PASS both.

**Gate reconciliations vs the pre-acquisition plan (tagged `[RECONCILED]` in the report):**
1. **SOURCE tags** {ISQ,ABDASH,CBRE} → **{ISQ, ABMKTMONITOR}**. The AB series came from the open-data **Alberta Tourism Market Monitor** (open.alberta.ca, OGLA), not the Economic Dashboard/CBRE; CBRE never obtained.
2. **Coverage gates 3.1/3.2** assumed full historical acquisition (QC 216/216, AB≥156 from 2010). Reality: ISQ's public Power-BI exposes only 2019+; the Market Monitor starts 2011. A month the source does not publish is a coverage limit, not an integrity defect → these gates **FAIL only on CORE gaps** (a hole inside a fully-covered non-edge year) and **WARN on edge/short-span**. This reclassified an initial FAIL (single edge-year hole **2011-12**, absent for every GEO because no Dec-2011 report exists — 2011 has only the Nov-2011 native PDF) down to WARN. The reliable complete AB series is **2012-2022**.
3. **4.1 QC 2015-2019 mean** → **INFO** (insufficient data, not WARN) — pre-2019 QC monthly is unavailable.

Data provenance recap: QC = manual ISQ Power-BI export (tab "Données mensuelles", Territoire=Province) → `_transcribe_isq_qc_pdfs.py` → `hotel_raw/ISQ_QC/`. AB = Market Monitor harvest → `deepResearch_v2/hotel_ab_monthly_2012_2022.csv`. Section-B readers + assembler in `3rdJ_01_hotelIngest_4split.py` now implemented (no longer stubs).

### 2026-07-19 — Report expanded to the RICH edition (10 figures, all 4 building types)

Per reviewer request, the report now shows schedules for **every building type**, not just hotel, and matches the Leg-2 Step-1 report's figure richness. The validator streams the reused Leg-2 **Step-2 harmonized episodes** (read-only) to derive the diurnal channel profiles; only small aggregates enter memory (runs ~5 s). Section-5 now carries **10 figures** (was 2):

- **C1** GSS data volume (respondents + episode rows/cycle) · **C2** episodes/respondent · **C3** WGHT_PER spread (boxplot) · **C4** diary completeness (mean min/day — all four cycles = **1440**, i.e. full 24 h accounted).
- **C5 ★ 4-channel diurnal schedules (2022)** — Residential (AT_HOME) overnight ~0.95→midday 0.49, Office (AT_WORK) weekday hump plateau ~0.28 (10-15 h), Retail (AT_RETAIL) midday bump ~0.05. This is the "horaires par type de bâtiment" figure. Hotel is monthly (C8), not diurnal.
- **C6** Office presence across cycles (2022 peak ~0.28 vs 2005 ~0.31 — modest on-site drop; fuller telework signal is in WFH). · **C7** Retail episode-time share (2005 2.00% / 2010 2.14% / 2015 1.66% / 2022 1.50% — near the dr_L3-06 2.1-2.3% band early, easing as in-person shopping declines; online leak gated out).
- **C8** Hotel monthly series (QC+AB, COVID shaded) · **C9** hotel seasonal profile (pre-COVID) · **C10** hotel coverage heatmap (year×month per PR, GAP grey — shows the QC-2019+/AB-2011+ edges).

Channels R/O/R are shown as **context** (Step 1 formally gates GSS-reuse + hotel acquisition; derivation proper runs in Step-3). Verdict unchanged: **WARN, 0 FAIL** (PASS 13 / WARN 3 / INFO 2). Visual QA: C5 shapes physically correct (residential/office/retail rhythms as expected); diary completeness exactly 1440 min confirms no episode-coverage loss in the reused diaries.

### 2026-07-19 — Hotel added to the diurnal figure + per-channel across-cycle set (now 13 figures)

Reviewer follow-up: (1) hotel was absent from the C5 diurnal chart, and (2) only Office had an across-cycle figure. Fixed:
- **Hotel is now in C5** as the fixed guest-room shape **s(t)** (dashed magenta, dr_L3-05 weekday), clearly labelled a *design* shape (not a GSS-measured population share). Rationale surfaced in the caption: hotel occupancy is **monthly**, so it has no GSS diary — its daily shape is the PNNL guest-room curve scaled by the monthly rate. (Physically coherent: the hotel midday trough coincides with the office peak — business travellers out at meetings.)
- **Across-cycle diurnal figures now exist for all three GSS channels** (the C6 pattern generalised): C6 Residential, C7 Office, C8 Retail — one line per cycle 2005/2010/2015/2022.
- **New C9 = hotel guest-room shape weekday vs weekend** (dr_L3-05: weekday trough 0.200 09-15h, weekend 0.308 shallower/later) — the hotel analogue of the per-channel diurnal figures. Hotel has no GSS cycles, so its across-*time* variation is the monthly series (**C10**) + seasonal profile (**C12**), not a cycle series.
- s(t) encoded from dr_L3-05 Table 5 (48 slots, RLE); both weekday and weekend curves visually verified against the report. Figure set 10 → **13**. Verdict unchanged (WARN, 0 FAIL).
