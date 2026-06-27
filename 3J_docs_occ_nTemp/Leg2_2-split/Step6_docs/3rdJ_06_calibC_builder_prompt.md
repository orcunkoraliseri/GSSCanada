# Builder prompt — calibration-C (activity + weekend home) + Step-7 2030 re-run

> Paste into a fresh Sonnet session. Manager-authored 2026-06-26.

---

You are the **employee**. Build a calibration script, run it, re-run Step 7 for 2030, verify, and append Progress Log entries. Work **locally** only (no cluster). `pandas`+`numpy` only. `seed=42`, reproducible, atomic writes. Do NOT modify any locked Step-4/5/6 *model* files; you MAY edit the Step-7 script (`3rdJ_07_aug_to_bem_2split.py`, ours).

## Read first
- Design (authoritative): the **"POST-HOC CALIBRATION-C"** section in `…\Leg2_2-split\Step7_docs\3rdJ_07_bemIntegration_2split.md`.
- Reuse references: `…\Step4_docs\3rdJ_04M_mindwell_2split.py` (min-dwell function/param), `…\Step6_docs\calibrate_weekday_work_2split.py` (calibration-B style/atomic-write idiom).

## Goal & I/O
Build `…\Step6_docs\3rdJ_06_calibrate_C_activity_weekend_2split.py`.
- **Input A (to calibrate):** `…\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell.csv` (111,024 rows; cols incl. `act30_001-048`, `hom30_001-048`, `wrk30_001-048`, `DDAY_STRATA`, `BAND`).
- **Input B (target source, real 2022):** `…\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Aggregated_excl.csv` (has matching `act30/hom30/wrk30` + `DDAY_STRATA`).
- **Output:** `…\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (same schema as Input A).

## Core principle
Forecast = WHERE people are (home/work/out), which is calibrated → keep it. WHAT they do given location = take from real 2022, conditional on state. `wrk30` is NEVER modified (office channel must stay identical).

## Stage 1 — weekend home restore (`hom30`, DDAY_STRATA ∈ {2,3} only)
- Build target = observed per-slot `hom30` mean from Input B, **per weekend stratum** (stock stratum 2 → deliverable stratum 2; stock 3 → deliverable 3), for each of the 48 slots.
- For each weekend stratum & slot: if target rate p_obs > current 2030 rate p30, flip `round((p_obs−p30)*n)` person-slots from 0→1, chosen `seed=42` **only among rows that are currently OUT** at that slot (`hom30=0 AND wrk30=0`). If p_obs < p30, flip 1→0 symmetrically (choose among `hom30=1 AND wrk30=0`). Never touch a slot where `wrk30=1`.
- After all weekend slots: apply the **04M min-dwell** smoother to the modified weekend `hom30` rows only (read 04M for the min-dwell length + function; reuse it).
- **Weekday (stratum 1) `hom30` is untouched.** `wrk30` untouched everywhere.

## Stage 2 — activity restore (`act30`, ALL strata, conditional on state)
- Define state per (row, slot) **after Stage 1**: `WORK` if `wrk30=1`; elif `HOME` if `hom30=1`; else `OUT`.
- From Input B build pools: `pool[slot, state]` = array of observed 2022 `act30` values at that slot for rows in that state.
- For every 2030 (row, slot): replace `act30` by a `seed=42` draw from `pool[slot, state]`. **Vectorize per (slot×state) cell** (group the 2030 indices in each of the 48×3 cells, assign with one `np.random.choice` per cell — do NOT loop per row). If a cell has < 20 observed samples, fall back to `pool[any-slot, state]`.

## Write + re-run Step 7
- Atomic-write the `_C` deliverable.
- Add an optional `--deliverable <path>` flag to `3rdJ_07_aug_to_bem_2split.py` (default = the original path, so existing behavior is unchanged), so 2030 can read the `_C` file.
- Re-run: `py 3rdJ_07_aug_to_bem_2split.py --year 2030 --deliverable <_C file>` → overwrites the 3 residential band files + office multiplier in `Step7_docs\outputs_step7\`. (Back up the pre-calibration band files first.)

## Verification (report all; flag any miss)
1. Sleep (act30 code 5) share: 22.8% → **~34–35%** (target: matches 2022 stock 34.6%).
2. Residential WD mean Metabolic: ~125–127 → **~108–112 W** per band.
3. Weekend daytime (slots 11–26, 09–17h) home occupancy: ~0.43 → **~0.52–0.56** (matches 2022 Sat/Sun ~0.52/0.56).
4. **WFH weekday gain PRESERVED:** WD daytime home conservative ~0.38 < hybrid ~0.43 < fullyhybrid ~0.46 (≈ unchanged from pre-calibration).
5. **Office unaffected:** `office_presence_multiplier_2030.csv` stats identical pre/post (since `wrk30` untouched) — confirm, and confirm office band-monotonicity still PASS.
6. All Step-7 hard gates still PASS on the re-run.

## Progress Log
Append a dated row to the Progress Log in `Step7_docs\3rdJ_07_bemIntegration_2split.md` recording the before→after for each of the 6 checks, the script path, the `_C` output path, and the `--deliverable` flag addition. Add a one-line note to the Step-6 main doc Progress Log (`Step6_docs\3rdJ_06_longitudinalForecasting_2split.md`) that calibration-C was added (triggered by the Step-7 diagnostic). Be honest about any check that missed target.

## Return
Concise report: the 6 before→after numbers, files written, and any issue or judgment call.
