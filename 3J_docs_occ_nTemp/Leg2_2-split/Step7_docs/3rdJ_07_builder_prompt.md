# Builder prompt — `3rdJ_07_aug_to_bem_2split.py` (Sonnet employee)

> Paste the block below into a fresh Sonnet session. Manager-authored 2026-06-26.

---

You are the **employee**. Execute the task below and append a Progress Log entry on completion.
Work **locally** (CPU only — no GPU, no `sbatch`). Do not modify any Step-4/5/6 locked files.

## Context (read first)
- Design doc (authoritative): `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split.md`
- Validation plan: `…/Step7_docs/3rdJ_07_bemIntegration_2split_val.md`
- **Port the residential logic from** `2J_docs_occ_nTemp/07_aug_to_bem.py` (read it fully — you
  are reusing `convert()`, `complete_day_types()`, `assemble_2030()`, the `MET` map, the `+4 h`
  diary→clock roll, `dtype_label()`, `PR_LBL`, the atomic write + gates). The office channel is new.

## Goal
Build `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py` that emits TWO
products along the two-channel asymmetry:

**Product 1 — Residential (REPLACE).** Per-`SIM_HH_ID × Day_Type × Hour` schedule, SAME schema/
format as 2J residential (`SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR,
PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate`).

**Product 2 — Office (MODULATE).** Aggregate table per `office_archetype × Day_Type × Hour`
(× `BAND` for 2030) with columns `office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction,
multiplier, n_persons`.

## Inputs
- **2022 stock (both channels):** `Leg2_2-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv`
  — per-person; has `SIM_HH_ID, MATCH_TIER, DDAY_STRATA, WGHT_PER, LFTAG, NOCS`, `act30_001–048`,
  `hom30_001–048`, `wrk30_001–048`, dwelling attrs `HHSIZE/DTYPE/BEDRM/ROOM/CONDO/REPAIR/PR`,
  `office_archetype_ID`, `HH_hom30_001–048`, `N_HH_MEMBERS`. (Note: already `SIM_HH_ID` — no
  `HH_ID→SIM_HH_ID` rename needed, unlike 2J.)
- **2030 forecast (both channels):** `Leg2_2-split/Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell.csv`
  — `act30/hom30/wrk30_001–048`, `CYCLE_YEAR=2030`, `BAND` (conservative/hybrid/fullyhybrid),
  `DDAY_STRATA, LFTAG, NOCS, NAICS, TELEWORK, PR, CMA`. **No dwelling attrs, no SIM_HH_ID, no
  WGHT_PER.** ⚠️ The full file (111,024 rows, 3 bands) lives on the cluster — confirm it is
  synced locally before the 2030 run (see Audit gate); the small local `2030_synthetic_diaries_2split.csv`
  is a stale sample, do not use it.
- **Office lookup:** `0_Occupancy/processed/office_archetype_lookup.csv` — `NOCS → archetype_label,
  is_office` (Office_Knowledge/Office_Public/Office_Sales = is_office True; NonOffice/Unknown_NOCS
  = False).

## Locked design decisions (HARD requirements)
- **OD-7A — Residential occupancy = mean(`hom30`) over HH members** (fraction home ∈ [0,1]).
  Do NOT use `HH_hom30`/max. Metabolic = mean(`MET[act30]`) over members.
- **OD-7B — Office `AT_WORK_fraction` is the primary column** (raw absolute population fraction,
  peak < 1). Also compute `multiplier` = `AT_WORK_fraction / max over weekday hours of that
  archetype's AT_WORK_fraction` (peak-normalized, for flexibility). Do NOT multiply by any
  baseline shape — this is just the GSS fraction.
- **OD-7C — Office denominator = employed `is_office` persons, UNWEIGHTED.** Filter to
  `is_office == True` AND employed (`LFTAG` ∈ employed/self-employed — inspect `LFTAG` distinct
  values, pick the employed codes, and **document which codes you treated as employed** in the
  Progress Log). Plain unweighted mean of `wrk30` over those persons per `(archetype, Day_Type,
  Hour)`. Same denominator rule for 2022 and 2030.
- **OD-7D — No Step-9 loads.** Do NOT add Equipment/Lighting columns.
- **OD-7E — Residential 2030 = three band files**, one per band. Office = one 2030 file with a
  `BAND` column. 2022 = one residential file + one office file (`BAND = "observed"`).
- **Office archetype:** derive from `NOCS` via the lookup for BOTH years (consistent). For 2022,
  cross-check your derived archetype against the stock's `office_archetype_ID` and report any
  mismatch count (do not silently diverge).

## Method (port + extend)
1. **`MET` map / `+4 h` roll / `dtype_label` / `PR_LBL` / `DAYTYPE {1:Weekday,2:Weekend,3:Weekend}`** —
   copy verbatim from 2J `07_aug_to_bem.py`.
2. **Residential `convert(df)`** — port 2J: group by `(SIM_HH_ID, Day_Type)`, mean `hom30` →
   `Occupancy_Schedule`, mean `MET[act30]` → `Metabolic_Rate`, 48→24 (average slot pairs),
   `np.roll(...,4)` on both, relabel DTYPE/PR, emit the 13-col schema. (Drop the 2J Step-9
   Equipment/Lighting block — OD-7D.)
3. **`complete_day_types(df)`** — port 2J donor-draw (`seed=42`) so every HH has Weekday+Weekend.
4. **`assemble_2030(band)`** — port 2J: copy the 2022 stock frame; per stratum `k`, overwrite each
   stock person's `act30+hom30+wrk30` with a `seed=42` stratum-matched draw from that band's 2030
   diary pool; keep stock dwelling/geo/`SIM_HH_ID`. Run once per band.
5. **Office `build_office_multiplier(df, band_label)`** — filter is_office + employed; group
   per-person `wrk30` by `(archetype, Day_Type)`; mean → 24 hourly + `np.roll(...,4)`; compute
   `AT_WORK_fraction`, `multiplier` (peak-normalized), `n_persons`. 2022 sources the stock
   directly (no assemble); 2030 sources each band's slice of the deliverable directly (office does
   NOT need the stock frame).

## Hard gates (assert before write; fail loudly)
Residential: `Day_Type ⊆ {Weekday,Weekend}`; `Hour ∈ [0,23]`; `Occupancy_Schedule ∈ [0,1]`;
`Metabolic_Rate ≥ 0`; every HH has exactly 2 day-types.
Office: `archetype ⊆ {Office_Knowledge,Office_Public,Office_Sales}`; `AT_WORK_fraction ∈ [0,1]`;
complete grid (each archetype × Day_Type has 24 hours, × 3 bands for 2030); weekday peak > night
floor and a visible lunch dip (assert peak hour fraction > 1.3× the 12:00–13:30 min, and >
night-floor); **band monotonicity (2030):** weekday business-hours (Hour 9–17) mean office
presence `conservative > hybrid > fullyhybrid` per archetype. Also report (not assert) the
residential daytime home-occupancy band ordering `conservative < hybrid < fullyhybrid`.

## Outputs (to `Step7_docs/outputs_step7/`, atomic `.tmp`→`os.replace`, gated one-time backup)
- `BEM_Schedules_2split_2022.csv` (residential, `%.3f`)
- `BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv` (residential, `%.3f`)
- `office_presence_multiplier_2022.csv` (`%.4f`)
- `office_presence_multiplier_2030.csv` (3 bands, `BAND` column, `%.4f`)

## CLI
`--audit` (read-only: confirm schemas, 2030 row count == 111,024 & 3 bands, 0 NaN in act30/hom30/
wrk30, office lookup); `--year 2022`; `--year 2030` (all 3 bands). Run-from-anywhere, `seed=42`.

## Verify & report
- Run `--audit`, then `--year 2022` end-to-end (real). For `--year 2030`, run it if the synced
  deliverable is present; otherwise build the code path, note it as PENDING the cluster sync, and
  do a structural dry-run on whatever 2030 sample is available.
- Append a Progress Log entry to `3rdJ_07_bemIntegration_2split.md` with: row counts + unique HH
  per output, 2022 weekday/weekend mean occupancy + metabolic, office weekday peak `AT_WORK_fraction`
  per archetype, the 2030 band ordering (both channels) if run, the `LFTAG` employed codes you used,
  and the 2022 archetype vs `office_archetype_ID` mismatch count. Flag any gate that did not run.

Deps: `pandas`, `numpy` (existing env). No new packages.
