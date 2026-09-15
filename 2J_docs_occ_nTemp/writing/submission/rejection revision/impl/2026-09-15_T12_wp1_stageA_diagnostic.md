# T12 — WP1 stage A diagnostic: where does the 70 % vs 78 % come from — implementation state

Task doc:   this file (section "Task")
Spec:       `2026-09-15_WP1_step2_retargeting_spec.md` (read §1, §4, §5 first)
Status:     DONE (collected by manager 2026-09-15; stage B on hold, spec §5 branch 3)

## Task

**Why.** The manager's reading is that 2030 schedules draw random diaries from a pool raked to
~78 %, while 2022 schedules keep the stock's own diaries at ~70 %. Measure it. **No design, no edits
to pipeline scripts, numbers only.**

**All compute on Speed via `sbatch`** (`-p ps -c 8 --mem=64G -t 7-00:00:00`), python
`/speed-scratch/o_iseri/envs/step4/bin/python`, work dir `/speed-scratch/o_iseri/2J_revision/T12/`.
Login node: only `sbatch squeue sacct scancel scontrol cd ls scp` and single-file `tail head grep wc -l cat`.
**Never `find`, `du`, or python on the login node.** tcsh shell: no `2>&1` or `2>/dev/null` in ssh
strings; `ssh -o BatchMode=yes -o ConnectTimeout=60`, retry once.

**Inputs (local, `GSSCanada-main/`) — scp to `T12/input/`:**
- `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv` (599 MB)
- `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv` (530 MB)
- `0_Occupancy/Outputs_21CEN22GSS/forecast_2030/2030_synthetic_diaries_joint_raked.csv` (11.5 MB)
Record local and remote byte sizes in Verified.

**Script `T12_scripts/t12_diag.py`** (new file; do NOT import `07_aug_to_bem.py`, it imports
`activity_loads`; copy the needed lines and cite them in a comment). Weekday = `DDAY_STRATA==1`,
weekend = 2 or 3. Report weekday and weekend, percent, 3 decimals.

- **M1** stock person-level `hom30` mean (48 slots): unweighted and `WGHT_PER`-weighted; overall and
  by `CYCLE_YEAR × IS_SYNTHETIC` with person counts.
- **M2** `augmented_diaries.csv`, `CYCLE_YEAR==2022 & IS_SYNTHETIC==0`: unweighted and weighted (if a
  weight column exists; name it). Expected unweighted weekday 76.93.
- **M3** joint-raked 2030 pool person-level mean by stratum. Expected weekday 78.44.
- **M4** mean over weekday slots of `8 × pre_slope` — copy `project_to_2030` logic
  (`06_forecast_rake.py:138-165`, `polyfit` on 2005/2010/2015 real respondents from
  `augmented_diaries.csv`; copy how `06_forecast_rake.py` computes `obs_rates`, cite lines). Also the
  clamped target minus obs_2022 mean. Expected ≈ +1.51 pp.
- **M5** household-level hourly schedule means from the **stock as is**: `complete_day_types`
  (`07_aug_to_bem.py:148-180`) then occupancy part of `convert` (`:94-97,103,109`). National and per
  archetype (`dtype_label`, `:36-41`). Must reproduce T01: weekday national 70.239 (±0.01). If not, stop
  and write why.
- **M6** current draw with the 2030 pool: `assemble_2030` logic (`:182-193`, seed 42) → same as M5.
  Must reproduce T01 weekday 78.526 (±0.01).
- **M7** null test: `assemble_2030` logic but pool = `augmented_diaries.csv` 2022 real respondents
  (a zero-change forecast) → same as M5. National and per archetype.
- **M8** composition check: M5 recomputed after per-person random re-draw from the **stock's own**
  weekday/weekend diaries (pool = stock, seed 42) → shows the draw's effect with the anchor held fixed.

Write `T12_out/t12_diagnostic.csv` (columns: measure, day_type, group, weighting, value_pct, n) and the
slurm log. scp both back to `impl/T12_out/`.

**Employee rules.** One job. Submit, write JobID in Ledger, **end the turn** ("job N submitted, state
written to <this doc>"). No waiting, no polling, no sleep. A later agent collects. Never read multi-MB
files into context. If past ~150k tokens, write state and stop with "handoff needed".

**Collector (a later, fresh agent).** `sacct` state/exit, scp outputs, check M5 and M6 reproduce T01,
fill Verified with every M value, apply nothing from spec §5 (manager decides).

## Ledger
- **1328275** · `t12_diag.py` (M1-M8, occupancy-only reconstruction of `07_aug_to_bem.py`, no
  activity_loads import) · `sbatch -p ps -c 8 --mem=64G -t 7-00:00:00` · state: SUBMITTED (not yet
  polled) · output: `/speed-scratch/o_iseri/2J_revision/T12/T12_out/t12_diagnostic.csv`, slurm log
  `/speed-scratch/o_iseri/2J_revision/T12/T12_out/slurm_1328275.out`.
  **Manager, 2026-09-15: FAILED exit 1:0 after 15 s.** M1-M4 completed and flushed; M5 raised
  `KeyError: "['DTYPE', 'BEDRM'] not in index"` (`t12_diag.py:289`) because M1's `usecols` (`:88`) did not
  load them. Partial output kept as `T12_out/t12_diagnostic_partial_1328275.csv` on Speed.
- **1328277** · same script, manager fix: `DTYPE`, `BEDRM` added to M1 `usecols` (compiled, scp'd) ·
  `sbatch -p ps -c 8 --mem=64G -t 7-00:00:00 -o T12_out/slurm_%j.out --wrap '... t12_diag.py'` · SUBMITTED ·
  supersedes 1328275 · outputs `T12_out/t12_diagnostic.csv`, `T12_out/slurm_1328277.out`.

## Verified
- Script `T12_scripts/t12_diag.py` compiles (`py -3 -m py_compile`, local, OK). Not run locally on the
  big files.
- Byte sizes, local vs Speed (`/speed-scratch/o_iseri/2J_revision/T12/input/`), all three match exactly:
  - `21CEN22GSS_aug_Full_Aggregated_excl.csv`: local 598,812,455 = remote 598,812,455
  - `augmented_diaries.csv`: local 530,141,993 = remote 530,141,993
  - `2030_synthetic_diaries_joint_raked.csv`: local 11,546,248 = remote 11,546,248
- Header check (local, `head -1` + `grep -n`, not full-file reads) confirmed the columns the script
  relies on exist: stock file has `WGHT_PER` (col 7), `HHSIZE`(545)/`PR`(547)/`DTYPE`(549)/`BEDRM`(550);
  `augmented_diaries.csv` has `WGHT_PER` (col 15) and `IS_SYNTHETIC` (col 545); the 2030 joint-raked
  pool has only `occID,CYCLE_YEAR,DDAY_STRATA,act30_*,hom30_*` (no weight column), matching
  `06_forecast_rake.py`'s own documented 99-column note.
- Sample data row (stock file, row 2): `HH_ID=1, CYCLE_YEAR=2010, IS_SYNTHETIC=1, WGHT_PER=780.23,
  DTYPE=2, BEDRM=1` — confirms `DTYPE`/`CYCLE_YEAR`/`IS_SYNTHETIC` are populated as expected by M1's
  by-cycle breakdown, and that `DTYPE` is the raw numeric code `dtype_label()` expects (not
  pre-mapped).

**M1-M4 from job 1328275 (read by manager with `cat` on Speed, 50 rows; M2/M3/M4 check lines matched):**
- M1 stock person-level weekday: 69.799 % unweighted, 67.464 % weighted (203,635 persons); weekend
  74.187 / 70.602 (81,732).
- M1 by diary cycle, weekday unweighted (n): 2005 real 70.837 (22,871), 2005 synth 75.112 (9,253),
  2010 real 67.486 (44,310), 2010 synth 67.767 (16,863), 2015 real 68.365 (45,435), 2015 synth 67.807
  (19,684), 2022 real 74.618 (32,592), 2022 synth 70.686 (12,627).
- **Diary-cycle share of the stock: 2022 diaries = 45,219 of 203,635 weekday persons (22.2 %) and
  18,310 of 81,732 weekend (22.4 %); 77.7 % of all stock persons carry a 2005/2010/2015 diary.**
- M2 2022 real respondents (augmented_diaries): weekday 76.931 unweighted (n 8,894), 74.926 `WGHT_PER`;
  weekend 78.811 / 77.005 (3,442).
- M3 2030 pool: weekday 78.437 (12,231), weekend 80.318 (24,777), no weight column.
- M4 weekday mean 8 x pre_slope = +1.507 pp (= clamped target − obs_2022); Sat +1.878, Sun +1.309,
  weekend pooled +1.553.

**Manager reading against spec §5 (pre-registered):** branch 1 condition holds (stock weekday 69.8 %,
inside 69–72 %) but **branch 3 also fires: the stock is mostly non-2022 diaries (77.7 %)**. Branch 3
says stop and tell the author before stage B. Stage B (T13) is NOT briefed. M5-M8 still to come from
job 1328277 (they are diagnostic only and do not depend on the branch).

**Job 1328277 collected by manager (COMPLETED 0:0, 52 s; outputs scp'd to `impl/T12_out/`, csv 99 lines).**
M1-M4 identical to 1328275. Household schedule means, 144,465 households, unweighted:
- M5 stock as is: weekday 70.239 (T01 check delta 0.000), weekend 74.331. Per archetype weekday
  HighRise 70.598, MidRise 70.392, OtherDwelling 69.577, SingleD 70.252.
- M6 current 2030 draw: weekday 78.526 (T01 check delta 0.000), weekend 80.367.
- **M7 null test (current draw, pool = 2022 real respondents, zero forecast change): weekday 76.933,
  weekend 78.714 → +6.69 / +4.38 pp over M5. The current machinery FAILS N0** (seen failing, as spec §4 asks).
- M8 current draw, pool = stock's own diaries: weekday 69.785, weekend 74.226 → −0.45 / −0.11 pp vs M5.
- A 43-household group labelled `8` appears (raw `DTYPE` 8 not mapped by the copied `dtype_label`); not
  root-caused, numbers 72.4 / 76.6 weekday / weekend.

**Decomposition of the +8.29 pp weekday 2022→2030 gap:** anchor (2022 respondents vs mixed-cycle stock)
M7 − M5 = +6.69; forecast M6 − M7 = +1.59 (M4 says +1.51); draw on the stock's own diaries M8 − M5 = −0.45.
The forecast is about one fifth of the gap; the anchor population is four fifths.

## Decisions
- Did not import `07_aug_to_bem.py` (per task doc); copied `dtype_label` (:36-41),
  `complete_day_types` (:148-180, restricted to `hom30_*` cols only — `act30_*` not loaded since this
  diagnostic is occupancy-only and the random-draw indices are unaffected by which columns are
  copied), the occupancy part of `convert` (:94-97,103,109), and `assemble_2030` (:182-193). Copied
  `compute_observed_marginals`/`project_to_2030` from `06_forecast_rake.py:100-165` for M4.
- M4 also reports a "weekend pooled" (Sat+Sun combined) row in addition to the pipeline's native
  per-stratum weekday/Sat/Sun split, to match this diagnostic's weekday/weekend reporting convention;
  this is additive reporting only, not a change to `06_forecast_rake.py`.
- M5-M8 use only `HOM` (occupancy) columns from the stock/pool files, not `ACT` — no metabolic/
  equipment/lighting fractions are computed (would require `activity_loads`, excluded per task doc).

## Next
**Superseded job id: use 1328277.** Collector (fresh agent): poll job 1328277 via `sacct`, scp `T12_out/t12_diagnostic.csv` and the slurm
log back to `impl/T12_out/`, check M5 and M6 reproduce T01 (weekday national 70.239 / 78.526, ±0.01 —
script prints an explicit check line for both), fill Verified with every M value, apply nothing from
spec §5 (manager decides).

## WHAT I DID NOT VERIFY
- Did not run the script on Speed or read any output — job is submitted only, not polled, per the
  no-parking rule.
- Did not verify row counts of the inputs post-transfer (byte size match only); row-count check is
  left to the collector via the job's own prints.
