# T11 — WP1 step 2 fact-finding: why 2022 lands at 70 % and 2030 at 78.5 % — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP1, §10 Wave 2 ("manager writes the WP1 step 2 spec")
Status:     DONE — all 6 questions answered with file:line evidence, reading only, no compute/edits done

## Task

**Why.** T01 confirmed weekday at-home 70.2 % (2022) vs 78.5 % (2030) in the schedules EnergyPlus
read. The 2030 forecast (`2J_docs_occ_nTemp/06_forecast_rake.py:138-183`) sets
`target_2030[stratum, slot] = obs_2022[stratum, slot] + 8 × pre-COVID slope`, where `obs_2022` is the
mean `hom30` of GSS 2022 respondents in `outputs_step4/augmented_diaries.csv` (`IS_SYNTHETIC==0`),
reported as 76.93 %. So the 2030 target is anchored to a 2022 level the 2022 schedules do not have.
The manager must design the fix. This task collects the FACTS only. **No design proposals, no
compute, no Speed, no edits outside this doc.**

**Answer each question with `file:line` evidence. Write NOT FOUND rather than guess.**

Q1. **Chains.** List, in order, every script and intermediate file from `augmented_diaries.csv` to
    `BEM_Schedules_2022.csv`, and from `2030_synthetic_diaries.csv` to `BEM_Schedules_2030.csv`
    (script, input, output, output mtime). Start from `05_postlink_rake.py`, `06_forecast_rake.py`,
    `07_aug_to_bem.py`, `05_censusLinkageGSS.md`, `06_longitudinalForecastingGSS.md`,
    `07_bemIntegrationGSS.md`, and `Step8_docs/08_09_injection_bug_status.md` (entries around
    2026-07-09 and 2026-07-15). Which of the two BEM schedule files was actually used by the Step-8
    campaign (manifest or run script `file:line`)?
Q2. **Asymmetry.** Which steps does 2022 pass through that 2030 does not (or vice versa)? In
    particular: census linkage, the region-tier relink of 2026-07-09, `05_postlink_rake.py`, any
    household aggregation, any `joint_raked` variant (`_JOINT_RAKED_OUT` at `06_forecast_rake.py:51`).
    Which 2030 diary file (`_raked`, `_joint_raked`, unraked) feeds the 2030 schedules?
Q3. **Definitions.** How is "at home" defined at each stage: person-level `hom30` (0/1 per 30-min slot),
    and in `BEM_Schedules_*.csv` (column name, household fraction of members home? any member home?
    occupancy count?). How did T01 compute its 70.2 % / 78.5 % (read
    `impl/2026-09-15_T01_wp1_athome_gap.md`)? Are 76.93 % and 70.2 % the same kind of quantity
    (same weighting, same unit person vs household, same day-type split, same slot window)?
Q4. **Post-link rake.** What targets does `05_postlink_rake.py` rake 2022 to, from which file, and
    what did the 2026-07-09 relink change (tiers, which households matched, at-home level before and
    after if logged)?
Q5. **Recorded numbers.** Every at-home level for 2022 and 2030 already written in the docs above
    (value, stage, date, `file:line`). Mark which were computed from which file.
Q6. **Rerun cost.** What must be rerun, in order, to regenerate `BEM_Schedules_2030.csv` from new rake
    targets (scripts, approximate runtime if logged, whether each ran on Speed or locally), and which
    checks exist (the "28-check" schedule-integration suite: path and how to run it).

Output: answers in Verified below, one subsection per question.

**Employee rules.** Reading only. Never read a multi-MB file into context (`wc -l`, `grep -n`,
`head`). Local python `py -3` only for tiny header reads. If you pass ~150k tokens, write state and
stop with "handoff needed".

## Ledger
(no cluster jobs expected)

## Verified

### Q1. Chains

**2022 chain (`BEM_Schedules_2022.csv`):**
1. `02_harmonizeGSS.py` / `03_mergingGSS.py` / `04D_train.py` etc. (Steps 1-4, not re-walked here) → Step-4 output `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv` (192,183 rows, mtime **2026-04-23**, unchanged since — `improvement-planning/2J_improvements_master_log.md:184`, `06_longitudinalForecastingGSS.md:51`).
2. `05_census_linkage.py` (region-tier linkage, **rewritten 2026-07-09**, Task A) → linked/matched population feeding `21CEN22GSS_aug_Full_Schedules.csv` and `21CEN22GSS_aug_Matched_Keys.csv` in `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/` (`05_postlink_rake.py:33-35`). Task-A fix detail and before/after match shares: `improvement-planning/2J_improvements_master_log.md:48-56`.
3. `05_postlink_rake.py` (Phase 8B-5b, `--joint` flag added 2026-07-09, Task B) reads/rewrites `21CEN22GSS_aug_Full_Schedules.csv` in place, raking `IS_SYNTHETIC==1` rows' `hom30`/`act30`/`Spouse30` to the `IS_SYNTHETIC==0` rows already in **that same file** (`05_postlink_rake.py:4-6,31-35`).
4. An aggregation/exclusion step (script not opened — not in this task's named-file list) produces `21CEN22GSS_aug_Full_Aggregated_excl.csv` = "2022 stock — calibrated (post-link-raked, 8B-5b) linked persons, post-exclusion," 285,367 rows, "post Jul-9 Step-5 refresh" (`07_bemIntegrationGSS.md:29`).
5. `07_aug_to_bem.py --year 2022` reads this file directly as `AUG` (`07_aug_to_bem.py:19,184,204`) and writes `BEM_Setup/BEM_Schedules_2022.csv` (`07_aug_to_bem.py:219-223`; run command `07_bemIntegrationGSS.md:194`). Local copy confirmed by T01: 673,929,104 bytes, **mtime 2026-07-09 20:57**, 6,934,320 data rows (`T01 doc Verified item 3`).

**2030 chain (`BEM_Schedules_2030.csv`):**
1. Same `augmented_diaries.csv` (step 1 above) feeds `06_forecast_rake.py` directly as `_AUG_PATH` (`06_forecast_rake.py:44,48`) — **not** the Step-5-linked/relinked file.
2. `06_forecast_rake.py`: loads `augmented_diaries.csv` (`IS_SYNTHETIC==0`), computes per-(CYCLE_YEAR×DDAY_STRATA×slot) mean `hom30` for cycles 2005/2010/2015/2022, OLS-projects to 2030, rakes `2030_synthetic_diaries.csv` (a separate Step-6 model output, `_DIARIES_2030` at `06_forecast_rake.py:49`) to the projected target → writes `2030_synthetic_diaries_raked.csv` (`_RAKED_OUT`, `:50`) and, with `--joint`, `2030_synthetic_diaries_joint_raked.csv` (`_JOINT_RAKED_OUT`, `:51`, write at `:669-675`). Target values: WD 78.44 / Sat 79.15 / Sun 81.48 (`06_longitudinalForecastingGSS.md:549,843-844`).
3. `07_aug_to_bem.py --year 2030 --joint` calls `assemble_2030(joint=True)` (`07_aug_to_bem.py:182-193,204`), which reads `stock=AUG` (same `21CEN22GSS_aug_Full_Aggregated_excl.csv` as the 2022 chain — "frozen 2022 _excl persons," `:184`) for household/dwelling structure, and `d30=D2030_JOINT` (`2030_synthetic_diaries_joint_raked.csv`, `:21,185`) for the occupancy/activity values, stratum-matched draw (`seed=42`) → writes `BEM_Setup/BEM_Schedules_2030.csv`. Local copy confirmed by T01: 673,609,612 bytes, **mtime 2026-07-09 21:06**, 6,934,320 data rows.

**Which file the Step-8 campaign used:** the plain (non-`_BAK`) `BEM_Schedules_2022.csv`/`_2030.csv`, confirmed two ways: (a) `08_simulation.md:167,267` — `08_gen_cycle_schedules.py` generated all five year-files and Step 8 "consumes Step 7 `BEM_Schedules_<year>.csv`"; (b) T01 doc's `D-T01-1` ruling test — 3 panel households' actual EnergyPlus `Schedule:Compact` echo in `in.idf` matched the current `BEM_Schedules_2022/2030.csv` rows exactly, byte-for-byte, 48/48 values each (T01 doc Verified item 6, evidence paths there).

### Q2. Asymmetry

**The central asymmetry, stated directly in the docs:** *"`06_forecast_rake.py`/`06_longitudinalForecasting.py` read `augmented_diaries.csv` (Step-4 J3 output) directly, and only import *code* (not data) from `05_postlink_rake.py`... **Step 5 never actually feeds Step 6** (Step-5's linked population feeds Step 7 only)."* — `improvement-planning/2J_improvements_master_log.md:184`.

Concretely:
- **2022 passes through** census linkage (`05_census_linkage.py`), the 2026-07-09 region-tier relink (Task A, same script), and `05_postlink_rake.py`'s post-link rake (Phase 8B-5b/Task B, `--joint`) before reaching `BEM_Schedules_2022.csv`.
- **2030's forecast target computation** (`06_forecast_rake.py`'s `obs_2022`) reads `augmented_diaries.csv` directly and passes through **none** of those three steps — it is anchored to the pre-linkage, pre-relink, pre-postlink-rake Step-4 output, frozen since 2026-04-23 (`06_longitudinalForecastingGSS.md:51`).
- **2030 does pass through household aggregation** (via `assemble_2030()`'s `stock=AUG`, same `Full_Aggregated_excl.csv` as 2022) for dwelling/geography attributes only — occupancy/activity values come from the diary pool, not the stock file (`07_aug_to_bem.py:182-193`, `07_bemIntegrationGSS.md:32-34`).
- **Which 2030 diary file feeds the schedules:** the **joint-raked** variant, `2030_synthetic_diaries_joint_raked.csv` (`_JOINT_RAKED_OUT`, `06_forecast_rake.py:51`), via the canonical run command `07_aug_to_bem.py --year 2030 --joint` (`07_bemIntegrationGSS.md:195,203-204`). Note `hom30` is identical between the plain-raked and joint-raked files — `--joint` only additionally rakes `act30`; it does not change the AT_HOME numbers (`06_longitudinalForecastingGSS.md:847`).

### Q3. Definitions

- **`hom30`** (person-level, `05_postlink_rake.py:39`, `06_forecast_rake.py:55`): 0/1 hard binary per 30-minute slot, 48 slots/day (`N_SLOTS=48`), calibrated (post-rake) to be hard {0,1} (`07_bemIntegrationGSS.md:43`). This is the unit both the 76.93% and 78.44% figures are computed in, directly, with **no household aggregation and no 30-min→hourly collapse**.
- **`BEM_Schedules_*.csv`'s `Occupancy_Schedule`** column: **household-level fraction of members home**, **hourly** (24 values/day, not 48). Built in `convert()`: `occ48 = df.groupby(["SIM_HH_ID","Day_Type"])[HOM].mean()` (mean of all persons in the household → household fraction-home per 30-min slot, `07_aug_to_bem.py:97`), then `occ24 = occ48.values.reshape(G,24,2).mean(axis=2)` (mean of each adjacent slot-pair → hourly, `:103`), then rolled +4h for GSS-diary-clock-to-wallclock alignment (`:105-110`). Column confirmed as the AT_HOME quantity by its use in Step-8 aggregation (T01 doc Verified item 3, citing `Step8_docs/08_gen_cycle_schedules.py:248` and `08_simulation_plots.py:547-558`).
- **T01's 70.2%/78.5%** = unweighted household-level mean of `Occupancy_Schedule` over all rows (all households × all weekday hours) in the current `BEM_Schedules_2022.csv`/`_2030.csv` — no weight column exists in these files (T01 doc Verified item 3, "No weight column exists").
- **The Step-6 76.93%** = person-level mean of `hom30` over individual `IS_SYNTHETIC==0` rows in `augmented_diaries.csv`, `CYCLE_YEAR==2022`, at native 30-min-slot resolution — `outputs_step6/improvement/step6_improvement_notes.md:837-844` (table, WD=76.93/Sat=77.28/Sun=80.17). A **third**, different-again 2022 baseline also exists in the same doc: `06_longitudinalForecastingGSS_val.py` line 130 defines "observed 2022" **without** the `IS_SYNTHETIC==0` filter (mixes 12,336 observed + 24,672 synthetic rows) → WD AT_HOME **74.23%**, used internally by that validator's §5.6/§4.4 diff checks (`step6_improvement_notes.md:850-855`). This is a distinct quantity from both 76.93% and 70.2%.
- **Are 76.93% and 70.2% the same kind of quantity? No.** They differ on every axis the task asks about:
  - **Unit/level:** 76.93% is a **person**-level indicator average (one `hom30` value per person per slot); 70.2% is a **household**-level fraction-of-members-home average, i.e. already one aggregation step removed.
  - **Time resolution:** 76.93% is native 48×30-min slots; 70.2% is 24 hourly values, each the mean of an adjacent slot pair, plus a +4h clock roll.
  - **Population/file:** 76.93% comes from `augmented_diaries.csv` (192,183 rows, Step-4 output, pre-linkage, pre-relink, pre-postlink-rake, frozen 2026-04-23, `IS_SYNTHETIC==0` subset only = 12,336 real respondent rows per the val-script cross-check at `step6_improvement_notes.md:852`). 70.2% comes from `BEM_Schedules_2022.csv`, built from `21CEN22GSS_aug_Full_Aggregated_excl.csv` (285,367 persons / 144,465 households), which includes synthetic rows, the 2026-07-09 region-tier relink, and the post-link rake — a materially different, larger, and differently-sourced population.
  - **Day-type split:** both define weekday the same way (`DDAY_STRATA==1`), so this axis matches.
  - **Weighting:** confirmed unweighted for the 70.2%/78.5% BEM-file computation (no weight column). Whether `augmented_diaries.csv`'s 76.93% used any survey weight was **not verified** — the file was not opened (see WHAT I DID NOT VERIFY).

### Q4. Post-link rake

- `05_postlink_rake.py` rakes **`IS_SYNTHETIC==1`** ("synthetic"/imputed) rows in `21CEN22GSS_aug_Full_Schedules.csv` so that their per-`(DDAY_STRATA × slot)` `hom30` rate matches the **`IS_SYNTHETIC==0`** ("observed") rows' rate **in that same file** (`05_postlink_rake.py:4-6`). This is a **self-referential** target — it is not raked to a fixed external number like 76.93%, and it does not read `augmented_diaries.csv` at all (confirmed structurally: `05_postlink_rake.py` has no `_AUG_PATH`/`outputs_step4` reference; only `06_forecast_rake.py` reads that file). `05_postlink_rake.py` also runs a floor guard (single-person HH night-slot restore, `:12-14,43-45`) and, if gate 6.3 fails, a `Spouse30` rake (`:15-16`).
- **What the 2026-07-09 relink changed** (in `05_census_linkage.py`, Task A — a *different* script from `05_postlink_rake.py`, though both were touched the same day): fixed a 2005 GSS `PR` coding mismatch (legacy 5-region scheme vs. Census SGC codes) that made every 2005 diary auto-fail Tier-1/Tier-2 linkage matching. First attempt (a Tier-2b fallback tier) was found flawed by independent audit (structurally capped at 0.47% of agents, could never have produced the logged 28.76% jump) and reverted; real fix merged the region-folded key into Tier-2 itself. **Before→after match shares:** 2005 9.03%→15.76% (25,863→45,164 rows), 2010 32.52%→29.93%, 2015 34.80%→32.04%, 2022 23.66%→22.27%; Tier-1 unchanged (128,778 rows) — `improvement-planning/2J_improvements_master_log.md:48-54`.
- **At-home level before/after the relink+rake, as logged:** the Remediation entry (full downstream re-run, Task A + Task B together) reports the **final, verified** population numbers directly: **2022 WD/WE occupancy 0.702/0.743; 2030 WD/WE 0.785/0.804**; 144,465 households, 6,934,320 rows both years; 1,170 HH excluded (0.41%) — `improvement-planning/2J_improvements_master_log.md:79`. A companion table shows the specific v6(stale)→v7(corrected) revision: 2022 Occupancy WD/WE **0.703/0.749 → 0.702/0.743** (`:95`). These 0.702/0.785 figures are the ones the 2026-07-15 log entry (Q1/Q5) later re-quotes as "70.2%/78.5%." No before/after AT_HOME *level* (as opposed to a gate residual) is logged for the relink in isolation (only combined with the Task-B joint rake); the isolated relink-only effect on AT_HOME is not separately recorded in what was read — flagged as NOT FOUND.
- Note: a separate, **gate-residual** "AT_HOME 4.48pp→4.27pp" number also exists (`improvement-planning/2J_improvements_master_log.md:143-144`) but this is a Step-5 validation-gate deviation metric, not a raw at-home percentage — do not conflate it with 70.2%/78.5%/76.93%/78.44%.

### Q5. Recorded numbers

| Value | Stage/quantity | Date | Source `file:line` |
|---|---|---|---|
| 76.93% (WD), 77.28 (Sat), 80.17 (Sun) | 2022 observed, person-level `hom30`, `IS_SYNTHETIC==0`, from `augmented_diaries.csv` | table dated within a 2026-07 entry | `outputs_step6/improvement/step6_improvement_notes.md:841` |
| 78.44% (WD), 79.15 (Sat), 81.48 (Sun) | 2030 base AND joint-raked forecast target, `hom30` | same table | `outputs_step6/improvement/step6_improvement_notes.md:843-844`; also `06_longitudinalForecastingGSS.md:549` |
| +1.51pp (76.93→78.44) | Step-6's own internal calibration check | — | `outputs_step6/improvement/step6_improvement_notes.md:846` |
| 74.23% (WD) | 2022 "observed" per validator L130, **without** `IS_SYNTHETIC==0` filter (12,336 obs + 24,672 synth mixed) | — | `outputs_step6/improvement/step6_improvement_notes.md:850-853` |
| 70.2% (2022) / 78.5% (2030), weekday, population-wide, +8.3pp gap | `BEM_Schedules_2022/2030.csv`, household-level `Occupancy_Schedule` mean | log entry dated **2026-07-15** | `Step8_docs/08_09_injection_bug_status.md:495` |
| 2022 WD/WE 0.702/0.743; 2030 WD/WE 0.785/0.804 | Same quantity as the row above, first appearance (Remediation re-run) | 2026-07-09 | `improvement-planning/2J_improvements_master_log.md:79` |
| 2022 Occupancy WD/WE 0.703/0.749 (stale, v6) → 0.702/0.743 (v7) | v6→v7 report correction, same file lineage | 2026-07-09 | `improvement-planning/2J_improvements_master_log.md:95` |
| 2022 national weekday **70.239%**; 2030 **78.526%** | Independent re-derivation directly from the current `BEM_Schedules_*.csv` files (T01 collector script) | 2026-09-15 | T01 doc, Verified item 5 (`impl/2026-09-15_T01_wp1_athome_gap.md:108-116`) |

All rows above ultimately trace to one of exactly two source files: `augmented_diaries.csv` (76.93/78.44/74.23/+1.51pp) or `BEM_Schedules_{2022,2030}.csv` (70.2/78.5/0.702/0.785/70.239/78.526) — confirming Q3's finding that these are two different quantities, not two measurements of the same thing.

### Q6. Rerun cost

**To regenerate `BEM_Schedules_2030.csv` from new rake targets, in order:**
1. `06_forecast_rake.py` — recompute `obs_2022` (whatever source the fix designates) and re-rake `2030_synthetic_diaries.csv` → `2030_synthetic_diaries_raked.csv` + (with `--joint`) `2030_synthetic_diaries_joint_raked.csv`. Also runs its own validation swap (`06_forecast_rake.py:19` docstring step 5: swaps the raked file in, runs `06_longitudinalForecastingGSS_val.py`, restores). No `sbatch`/job-ID is cited anywhere for this script in the docs read (unlike the Step-6 Transformer training sub-stages A-D, which do cite SLURM job IDs, e.g. `06_longitudinalForecastingGSS.md:640,732,772`) — consistent with it being a lightweight CPU raking script run locally, same class as `05_postlink_rake.py`, but this is inferred from absence of a job ID, not a stated "runs locally" line for this specific script — **flagged as not explicitly confirmed**.
2. `07_aug_to_bem.py --year 2030 --joint` — regenerate `BEM_Schedules_2030.csv`. **Explicitly local, CPU-only, no GPU, no sbatch** (`07_bemIntegrationGSS.md:210`), runtime ~1-3 min (groupby on 285k+ rows, ~6.9M-row write; `07_bemIntegrationGSS.md:213-216`).
3. `07_bemIntegrationGSS_val.py --year 2030` — the "28-check" schedule-integration suite. Path: `2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py`. Run: `py 2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py --year 2030` (or with no `--year` arg to also run 2022's 29-check variant) — `07_bemIntegrationGSS.md:198-199`. Confirmed tally naming: "2022 **29 PASS**/0 WARN/0 FAIL, 2030 **28 PASS**/0 WARN/0 FAIL (2030 has no 3.5 — no observed-future anchor)" — `07_bemIntegrationGSS_val.md:17,199,248`. Produces `outputs_step7/step7_validation_report_2030_v2.html`.
- The 2022 side (`BEM_Schedules_2022.csv`) is **not** affected by a fix to the 2030 rake target and would not need rerunning unless the fix also changes `05_postlink_rake.py`'s target definition.

## Decisions
(none — no design decisions were in scope for this fact-finding task)

## Next
T11 is DONE. All 6 questions answered with file:line evidence above. This unblocks whoever writes the WP1 step 2 re-targeting spec (`00_REVISION_PLAN.md` §3 WP1, §10 Wave 2) — they now have: the exact script/file chain for both years (Q1), the proof that the 2030 forecast target bypasses Step 5 entirely (Q2, `improvement-planning/2J_improvements_master_log.md:184`), confirmation that 76.93%/78.44% and 70.2%/78.5% are not commensurable quantities (Q3), the region-tier relink's own before/after numbers (Q4), a consolidated table of every recorded at-home figure (Q5), and the 3-step rerun order plus the 28-check suite location (Q6).

## WHAT I DID NOT VERIFY
- Did not open `outputs_step4/augmented_diaries.csv` directly to recompute 76.93%/74.23% from raw rows — took `step6_improvement_notes.md`'s numbers as given (same limitation T01 flagged).
- Did not open `21CEN22GSS_aug_Full_Aggregated_excl.csv` directly, and did not identify/open the specific aggregation/exclusion script that turns `21CEN22GSS_aug_Full_Schedules.csv` into `21CEN22GSS_aug_Full_Aggregated_excl.csv` (Q1 step 4, 2022 chain) — its existence and row count are documented in `07_bemIntegrationGSS.md:29`, but the task's named-file list (`05_postlink_rake.py`, `06_forecast_rake.py`, `07_aug_to_bem.py`, plus the three `.md`s and the injection-bug-status log) did not include it, and this task is scoped to those named files plus what they directly cite.
- Did not confirm whether `06_forecast_rake.py` runs on Speed or locally by a direct statement in the docs — inferred "locally" from the absence of any SLURM job ID for it, contrasted with the Transformer sub-stages which do cite job IDs. Flagged, not asserted, in Q6.
- Did not check whether `augmented_diaries.csv` carries a survey weight column that the 76.93% computation might or might not use (Q3's weighting axis) — file not opened.
- Did not verify the isolated (relink-only, pre-Task-B-rake) at-home level — only the combined Task-A+B before/after numbers were found logged (Q4).
- Did not re-derive any number independently in this task (that was T01's job); this task only traced and cross-cited what is already written on disk, per its own "reading only, no compute" instruction.
