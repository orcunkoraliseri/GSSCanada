# 3rdJ Step 1 — Data Collection & Column Selection (Leg-3 Four-Channel Split)
### GSS side: nothing to add (reuse Leg-2 verbatim) · Hotel side: NEW external data acquisition (ISQ / CBRE, non-GSS)

---

## Goal

Step 1 of the 4-split leg has **no new GSS work at all** (pipeline doc §1A–1B): the Leg-1 residential column set and the Leg-2 office employment-gating additions are reused unchanged, and the retail presence signal (`occPRE == 5`, `occACT == 4`) is *already carried* on every episode row produced by the Leg-2 Step-1/Step-2 chain. Retail requires no Main-file additions (retail *staff* are deliberately not modelled from GSS — they are AT_WORK).

The only genuine Step-1 build item is **external and non-GSS**: acquire the provincial monthly hotel-occupancy series (ISQ for QC; Alberta Economic Dashboard / CBRE for AB) that drives the Hotel channel, per [dr_L3-01_statcan_hotel_data_REPORT.md](../deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md). **No Statistics Canada table exists for this** (Table 24-10-0048-01 does not exist; verified) — StatCan is bypassed entirely.

Deliverables:
1. **GSS reuse verification** — confirm the Leg-2 Step-1 outputs are present, intact, and row-count-exact, so Leg-3 consumes them read-only (no re-run, no copy).
2. **Hotel raw acquisition** — download the ISQ and Alberta Dashboard series, drop the raw files under `0_Occupancy/external/hotel_raw/`, and assemble a first-pass `hotel_occupancy_raw_assembled.csv` (per-source, un-spliced). Harmonization (splice, canonical schema) is Step 2D.

## Reference

- Pipeline (step-by-step): `../3rdJ_00_4split_Occupancy_Pipeline.md` — STEP 1 (§1A/1B/1C)
- Pipeline (overview): `../3rdJ_00_4split_Occupancy_Pipeline_Overview.md`
- Spec: `../4-channel_split.md` §1 (why hotel is a separate source), §2.5, §8
- Deep research: `../deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md` (sources, licences, splice, sanity magnitudes)
- Leg-2 counterpart (template + the outputs being reused): `../../Leg2_2-split/Step1_docs/3rdJ_01_readingGSS.md` + `3rdJ_01_readingGSS_2split.py`
- Feasibility audit: `../../investigation/00_GSS_split_suitability_audit.md` (§2, §3, §7)

## Data Source Inventory

### A. GSS — ✅ DONE (Leg 2, reused read-only; no re-run)

| Artifact | Path | Expected rows |
|---|---|---|
| `main_2005.csv` | `../../Leg2_2-split/Step1_docs/outputs_step1/` | 19,597 |
| `main_2010.csv` | 〃 | 15,390 |
| `main_2015.csv` | 〃 | 17,390 |
| `main_2022.csv` | 〃 | 12,336 |
| `episode_2005.csv` | 〃 | 333,654 |
| `episode_2010.csv` | 〃 | 283,287 |
| `episode_2015.csv` | 〃 | 274,108 |
| `episode_2022.csv` | 〃 | 168,078 |

> Leg-3 never re-reads the GSS PUMF files and never modifies the Leg-2 outputs. The AT_RETAIL inputs (`occPRE`, `occACT`) live in the **Step-2** harmonized episode CSVs (`../../Leg2_2-split/Step2_docs/outputs_step2/`), which Step 3 consumes directly.

### B. Hotel — ⚠️ PLANNED (Leg 3, non-GSS, external)

| PR | Source | Coverage | Access |
|---|---|---|---|
| QC | ISQ — « Enquête sur la fréquentation des établissements d'hébergement du Québec » | 1983–present, monthly, provincial | Free (Québec Open Government Licence). Portal: https://www.quebec.ca/tourisme-et-loisirs/services-industrie-touristique/etudes-statistiques — CSV/Excel or Power-BI extraction. Structurally consistent 2005–2022, **no splicing needed**. |
| AB | Alberta Economic Dashboard — "Accommodation occupancy rate" (sourced from CBRE) | 2010–2022 direct CSV/XLSX/JSON | Free (Alberta Open Government Licence). Portal: https://economicdashboard.alberta.ca/dashboard/accommodation-occupancy-rate/ — excludes major resorts (Banff, Jasper). |
| AB 2005–2009 gap | CBRE Hotels Canada *National Market Report* archives | 2005–2009 | Proprietary/paywalled; academic use needs a custom agreement. Splice at Jan-2010 (Step 2D). |
| AB fallback (if CBRE archives unobtainable) | (1) truncate AB training window to 2010-01 (156 monthly obs — still sufficient for SARIMA(1,1,1)(1,1,1,12)); or (2) StatCan TASPI Table 18-10-0249-01 as exogenous backcast regressor | — | Decision recorded at acquisition time in the Progress Log. |

> **Market-level preference (dr_L3-01 recommendation).** Where the portals expose **city-market series (Montréal, Calgary)**, acquire them *in addition to* the provincial series — provincial averages smear downtown demand with rural/highway motels, and the event spikes (Stampede July >85 %, Grand Prix/festivals) matter for peak cooling/DHW. The provincial series remains the canonical driver (the pipeline keys on `PR`); market series are kept for validation context.

## Proposed Changes

### [NEW] `Step1_docs/3rdJ_01_hotelIngest_4split.py` ⚠️ PLANNED (Leg 3)

Small local script (no cluster needed; runs in seconds):

- **Section A — GSS reuse verification.** For each of the 8 Leg-2 Step-1 CSVs: assert existence, assert exact row counts (table above), record file size + SHA-256 into `outputs_step1/gss_reuse_manifest.csv`. Any mismatch is a loud FAIL — it would mean the Leg-2 chain moved under us (cf. the Leg-2 stale-artifact lessons).
- **Section B — hotel raw ingest.** Read the manually-downloaded raw files from `0_Occupancy/external/hotel_raw/` (one sub-dir per source: `ISQ_QC/`, `ABdash_AB/`, `CBRE_AB_archive/`), normalize month parsing and percent→fraction units, and emit `outputs_step1/hotel_occupancy_raw_assembled.csv` with columns:
  `YEAR, MONTH, PR, SOURCE, occupancy_rate (0–1), ADR_CAD, RevPAR_CAD`
  (one row per source-month; **no splicing, no gap-filling here** — Step 2D owns that). COVID-collapse months (2020-03 onward) are kept as-is: they are signal for the Step-6 SARIMA COVID indicator, not gaps.
- RevPAR: QC = ISQ « revenu de location par unité disponible » (RUD) when published, else computed `occupancy_rate × ADR_CAD` and flagged in a `REVPAR_COMPUTED` column; AB = dashboard RevPAR directly.

### Manual acquisition step (user-executed, documented here)

Downloads are manual (portal navigation / possible Power-BI extraction). The runbook step is: download QC monthly 2005-01…2022-12 and AB monthly 2010-01…2022-12 (+ CBRE 2005–2009 if obtainable), drop under `0_Occupancy/external/hotel_raw/<SOURCE>/` untouched, record filenames + retrieval dates in the Progress Log. Licences: ISQ and Alberta files are open-licence; CBRE material must not be redistributed in the repo (keep values, cite source, no raw PDF commit).

## Module Structure Summary

```
3rdJ_01_hotelIngest_4split.py
├── verify_gss_reuse()          (NEW — Section A: 8-file manifest, row counts, hashes)
├── read_isq_qc()               (NEW — Section B)
├── read_abdash_ab()            (NEW — Section B)
├── read_cbre_ab_archive()      (NEW — Section B, optional/fallback-aware)
├── assemble_raw_monthly()      (NEW — unit normalization, RevPAR completion flag)
└── __main__                    (platform-detect paths; py -3 -X utf8)
```

## Expected Result

- `outputs_step1/gss_reuse_manifest.csv` — 8 rows, all `status = OK`.
- `outputs_step1/hotel_occupancy_raw_assembled.csv` — QC: 216 source-months (2005-01…2022-12); AB: ≥156 source-months (2010-01…2022-12), plus 60 CBRE months if the archive path succeeded; all `occupancy_rate ∈ (0, 1]`.
- Raw files preserved untouched under `0_Occupancy/external/hotel_raw/`.

## Test Method

1. Locally: `py -3 -X utf8 3rdJ_01_hotelIngest_4split.py` from `Step1_docs/`.
2. Confirm the two output CSVs exist and the manifest shows 8/8 OK.
3. Run the validator: `py -3 -X utf8 3rdJ_01_readingGSS_4split_val.py` → target **0 FAIL** (see `3rdJ_01_readingGSS_4split_val.md`).
4. Inspect the HTML report's monthly time-series chart: seasonal sawtooth visible, COVID 2020-04 collapse present (QC/AB troughs — see sanity table in the val doc), no gap months inside each source's window.

## Progress Log

*(append entries below as work completes — format: `### YYYY-MM-DD — <short description>`, with job IDs where cluster runs are involved)*

### 2026-07-18 — Section A (GSS reuse verification) implemented and passing

Created `Step1_docs/3rdJ_01_hotelIngest_4split.py` with a working `verify_gss_reuse()` and a `__main__` that runs it. Only **Section A** is implemented in this pass; the Section B hotel-reader functions (`read_isq_qc`, `read_abdash_ab`, `read_cbre_ab_archive`, `assemble_raw_monthly`) exist only as `# PLANNED (Leg 3, Section B) — not yet implemented` stubs that raise `NotImplementedError` — they are blocked on the manual ISQ/Alberta/CBRE downloads and out of scope here.

Ran locally from `Step1_docs/`: `py -3 -X utf8 3rdJ_01_hotelIngest_4split.py` → **8/8 OK**, exit code 0. Wrote `outputs_step1/gss_reuse_manifest.csv` (8 rows, all `status=OK`), confirming the Leg-2 Step-1 outputs are present and row-count-exact:

| file | expected rows | actual rows |
|---|---|---|
| main_2005.csv | 19,597 | 19,597 |
| main_2010.csv | 15,390 | 15,390 |
| main_2015.csv | 17,390 | 17,390 |
| main_2022.csv | 12,336 | 12,336 |
| episode_2005.csv | 333,654 | 333,654 |
| episode_2010.csv | 283,287 | 283,287 |
| episode_2015.csv | 274,108 | 274,108 |
| episode_2022.csv | 168,078 | 168,078 |

Row counts were streamed via newline counting (no pandas/full-file load); SHA-256 hashes streamed in 1 MiB chunks (all 64 hex chars, verified). No Leg-2 source file was modified or copied.
