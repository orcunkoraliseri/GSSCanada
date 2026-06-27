# RESUME — Opus Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Opus session to continue.**
Last updated: 2026-06-26 (Step 7 closed). First read CLAUDE.md and memory/MEMORY.md
(esp. `project_step7_2split_status.md`, `project_step6_2split_status.md`), then resume as
if no break happened.

---

## 0. Who you are

You are the **MANAGER (Opus)** in a two-agent workflow for the GSSCanada residential
occupancy modeling research (3rd journal paper = **"3J"**, Leg-2 = **"2-split"** =
two-channel AT_HOME + AT_WORK joint occupancy model).

- **You plan / debug / judge / write builder prompts.** You do NOT execute.
- **Cheap Haiku/Sonnet "employees" do ALL execution** — scp, sbatch, log peeks,
  monitoring, retrieval. ALWAYS set `model:` on every Agent call (bg agents silently
  inherit Opus otherwise). Use one-shot checks, not poll loops; min ~30-min spacing.
- You are "both manager and sometimes employer": if the user hands you a current
  runbook AND confirms, you may execute that one cycle. Default is plan/debug only.
- Monitoring/polling (ssh/sacct/squeue/wakeup loops) is NOT your duty — the
  employee/user relays the numbers back to you.

## 1. HARD RULES (never violate — account-suspension risk)

1. **NEVER** run a blocking/interactive `srun` (or any python/computation) on the
   Speed **login node**. ALWAYS `sbatch` (fire-and-forget), then read the output file.
2. **NO bare `python`/`python3` on the login node — ever** (incl. one-liners). Allowed
   on login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, module load`,
   and single-file `tail/head/grep/wc -l/cat`. Anything importing pandas/numpy/torch
   or iterating dirs → `sbatch`.
3. **EVERY job submission MUST request `-t 7-00:00:00`** (1-week min). Speed ps/pg
   MaxTime = 7 days. A 1h cap once killed control job 987005 with empty output.
4. Speed login shell is **tcsh**: no `2>&1` (use `>&` or omit); one short line per
   command, no backslash continuation.
5. **Label every command "locally" or "on the cluster."**
6. **Bundle uploads** — one recursive scp per cycle; never file-by-file mid-cycle.
   Never upload the whole `GSSCanada-main/` dir; only named individual files.
7. Before any Speed `sbatch` handoff, scan script imports — ensure
   yaml/eppy/joblib/numpy/pandas/torch etc. exist in the cluster env (`envs/step4`).
8. **Step 4 is LOCKED.** Archive predecessor (`cp` to `archive/`) before any
   architecture edit. Update progress logs **live/incrementally**, not batched.
9. **Full audit, no patches**: when one cluster cycle reveals a bug, audit the whole
   chain and ship ONE fix bundle — not one patch per failure.
10. Communication: casual, ≤100 words unless detail requested. End with the literal
    command to run (not "when X finishes, do Y").

## 2. Cluster facts (Speed @ Concordia)

- host: `o_iseri@speed.encs.concordia.ca`; login node = submission only; GPU = `pg`.
- python: `/speed-scratch/o_iseri/envs/step4/bin/python`
- Step-6 module: `…/Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split.py`
- data (augmented diaries): `…/Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv`
- Step-4 base ckpt (LOCKED): `…/R5_lr1e4/checkpoints/best_model.pt`
- 04M min-dwell: `…/Step4_docs/3rdJ_04M_mindwell_2split.py`
- Step-6 outputs: `…/Leg2_2-split/Step6_docs/outputs_step6/`
- Cluster dir prefix on Speed: `/nfs/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/…`

---

## 3. WHERE WE ARE — Step 6 is **DONE** (2026-06-26)

**Step 6 = Model 2: Longitudinal Forecasting to 2030** (office/WFH leg, two-channel
AT_HOME+AT_WORK, 3 WFH bands: conservative 17.5% / hybrid 30% / fullyhybrid 40%).
First Leg-2 HPC step. **Fully closed, validated honestly (not rubber-stamped).**

**FINAL DELIVERABLE (for Step 7):**
`…/Leg2_2-split/Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell.csv`
(111,024 rows = 3 bands × 37,008; one CSV, `BAND` column). Calibrated + min-dwell —
use THIS, not the un-calibrated `2030_synthetic_diaries_2split.csv`.

**The journey (compressed):**
1. **Degeneracy bug → FIXED.** `Step6Dataset` self-paired each diary → 04B translator
   collapsed to identity copier (all 3 bands identical, backcast JS=−0.0000). Fix
   bundle **job 987039** (pg GPU, 30.5h, clean): (A) cross-day KNN pairing
   `build_cycle_pairs()`; (B) `_posthoc_reweight()` → 3 WFH bands diverge correctly
   (WFH-day share 0.170/0.292/0.388, Gate 4 PASS); (C) anti-copy gates.
2. **Backcast diagnostic was self-handicapped — both fixed.** (i) Gate computed
   `js_divergence` on RAW FLATTENED BINARY → element-wise memorization metric
   saturating near ln2 (weekend JS_work 0.45 despite dWork≈0.0005). Fixed to
   **marginal per-slot profile JS + per-slot MAD** (PASS keys on
   `mad_h<0.10 and mad_w<0.10`); verified by job 1005383. (ii) Backcast ran
   `temperature=0.0` (greedy) → AR work head latched "at work all night". Fixed
   backcast **temp 0.0→0.8** (job 1006500). After both: shape excellent, weekends
   PASS, anti-copy PASS.
3. **Weekday work-hot bias — diagnosed, source-split, calibrated.** Backcast on the
   LOCKED Step-4 base (job 1006516, read-only via new `--backcast_ckpt` abs-path flag)
   split it: **HOME under-prediction is INHERITED from locked Step-4** (base MADhome
   0.177, worse than Step-6's 0.141) → a retrain ("C") canNOT fix it; **WORK
   over-prediction is ADDED by Step-6 fine-tuning** (base MADwork 0.085 PASSES;
   Step-6 0.169), rooted in `work_pos_weight=7.873` + `cw[WORK]*=5.0` boost (locked
   Step-4 machinery). Mutex check (job 1006514) refuted head-overlap (0.52% conflicts).
   **C ruled out** (can't fix inherited BEM-critical home channel, 1.5-day gamble).
4. **Calibration B (`calibrate_weekday_work_2split.py`) — DONE.** Post-hoc, no-retrain.
   Caps weekday-employed WORK at observed-2022 per-slot profile by trimming work-block
   tails→home; flipped slots get time-appropriate home activity (Sleep night / Passive
   day). **KEY: trims NON-business-hours slots only** (skip BIZ_SET = 0-idx 10-25 =
   1-idx slots 11-26) → preserves band WFH shares EXACTLY (a v1 capping biz-hours
   inflated conservative share 0.174→0.222; the WFH-day classifier is biz-hours-based).
   Result: night work 0.13→0.035 (obs ~0.02–0.03), bands differentiated (0.174/0.302/
   0.380). Then 04M min-dwell (job 1006522, only 136 work + 5,241 home slots changed).
   Final verify (job 1006523): deliverable weekday VERDICT **HEALTHY**
   (night-end WORK 0.037 / HOME 0.916).

**Documented residual (accepted, NOT a blocker):** weekday BUSINESS-HOURS home is
modestly under-counted — inherited from the locked Step-4 base, scenario-appropriate
(conservative = low telework = more people at the office during the day). Cannot fix
without retraining the LOCKED Step-4 model.

**Archives** (`Step6_docs/archive/`): `.preCrossDayPairing.py`, `.preAMPfix.py`,
`.preBackcastMetricFix.py`, `.preBackcastTempFix.py`, `.preBackcastCkptParam.py`.
**New B-scripts** (`Step6_docs/`): `verify_backcast_metric_2split.py`,
`profile_forecast_weekday_2split.py`, `mutex_check_backcast_2split.py`,
`characterize_bias_2split.py`, `calibrate_weekday_work_2split.py`. Module gained
`--backcast_ckpt` flag + profile-based backcast gate + temp=0.8 backcast.

Progress logs current: `3rdJ_06_longitudinalForecasting_2split.md` (main) +
`…_val.md` (validation). Memory `project_step6_2split_status.md` = DONE.

---

## 4. STEP 7 (BEM wiring) — **DONE** (2026-06-26)

Two-channel BEM wiring built, run LOCALLY, validated honestly, then a fix bundle cleared
every validator FAIL. **Producer:** `Step7_docs/3rdJ_07_aug_to_bem_2split.py`.
**Validator:** `Step7_docs/3rdJ_07_bemIntegration_2split_val.py` (ported from the 2J
residential validator + office sections). Both docs (`…_2split.md` main, `…_2split_val.md`
plan+gate table) current.

**Final validator scorecard:** 2022 = **32 PASS / 0 WARN / 0 FAIL**; 2030 = **43 PASS /
0 WARN / 0 FAIL**.

**DELIVERABLES (for Step 8), in `Step7_docs/outputs_step7/`:**
- Residential: `BEM_Schedules_2split_2022.csv`; `BEM_Schedules_2split_2030_{conservative,
  hybrid,fullyhybrid}.csv` (REPLACE; per-HH × day-type × hour occupancy + metabolic).
- Office: `office_presence_multiplier_{2022,2030}.csv` (MODULATE; AT_WORK_fraction per
  `office_archetype × day_type × hour (× BAND)`).
- Reports: `step7_validation_report_{2022,2030}.html`.
- **2030 source is now the `_C` file:** `…/Step6_docs/outputs_step6/2030_synthetic_diaries_
  2split_calibrated_mindwell_C.csv` (calibration-C, regenerated by the fix bundle). NOT the
  pre-C `_calibrated_mindwell.csv`.

**Design (OD-7A…E LOCKED):** residential occupancy = **mean(`hom30`)**; office = **raw
absolute `AT_WORK_fraction`** as the schedule (peak-normalized `multiplier` also emitted but
not the default consumer input — keeps the WFH level effect, peak ~0.5→0.4 across bands);
office denominator = employed `is_office` persons unweighted; Step-9 equip/light kept
separate; residential 2030 = 3 band files, office = one file + `BAND`.

**Fix bundle A/B/C (2026-06-26, surfaced by the validator — full-audit, one bundle):**
- **A — province labels:** producer's `PR_LBL` used old census codes; Step 5 had already
  collapsed provinces to 6 region codes via `_PROVINCE_TO_REGION` in
  `3rdJ_05_censusLinkage_2split.py`. Reused that authoritative map (1=Atlantic, 2=Quebec,
  3=Ontario, 4=Prairies, 5=BC, 6=Northern Canada); `PR` now exits as region names; validator
  `PR_VALID` updated.
- **B — donor-draw drift:** `complete_day_types()` now overwrites household-level attrs with
  the recipient HH's own values (only `Occupancy_Schedule`+`Metabolic_Rate` come from the
  donor) + a `groupby(SIM_HH_ID).first()` STAT canonicalization in `convert()`. Within-HH
  DTYPE/PR drift 2,086 HH → **0**.
- **C — weekend office work:** calibration-C gained a **Stage 0 weekend work cap** (strata 2&3,
  trim-only 1→0, seed=42, target = observed-2022 weekend per-slot `wrk30`). WE work 18.6% →
  6.6% (obs Sat 7.1% / Sun 6.1%); office WD > WE now holds for all 9 archetype×band combos.
  Weekday `wrk30` untouched. **NOTE (publishable):** C now consciously modifies *weekend*
  `wrk30` — the old "wrk30 never modified" note applied to weekday only.
- **Regression guard held:** sleep 35.4%, WD metabolic ~110 W, WE daytime home 0.51–0.56,
  residential band order cons<hyb<fully, office biz-hours order cons>hyb>fully — all PASS.

**Archives:** `Step7_docs/archive/3rdJ_07_aug_to_bem_2split.preFixBundle_2026-06-26.py`;
`Step6_docs/archive/3rdJ_06_calibrate_C_activity_weekend_2split.preWeekendWork_2026-06-26.py`;
all output CSVs + `_C` deliverable backed up to dated `.preFixBundle` copies.

## 5. WHAT'S NEXT — Step 8 (EnergyPlus simulation / office integration)

Step 8 consumes the Step-7 deliverables above. The 2J analogs: residential schedules ride the
existing EnergyPlus consumer unchanged; the NEW office path needs an `office_integration.py`
that takes `office_presence_multiplier_*.csv` and replaces the NECB/ASHRAE office temporal
shape (OD-7B: use the raw `AT_WORK_fraction` directly, keep the density). Not yet started —
confirm scope with the user before building. (2J reference: `project_step8_simulation`,
`project_step9_activity_loads` in memory.)

**Suggested opening line to the user:** "Step 7 is closed (validator 32/0/0 for 2022, 43/0/0
for 2030; fix bundle A/B/C cleared all FAILs). Step 8 = EnergyPlus + the new office_integration
path. Want to scope Step 8?"
