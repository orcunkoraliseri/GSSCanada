# T34 — WP10 draft: "Proposed modelling and simulation framework" section with equations

Task doc and implementation state in one file. Written by the manager 2026-09-15 (plan log (as)).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster, no python on Speed.**

## Aim
Draft the new Section 2 of the manuscript (plan §3 WP10 Structure item 2), answering the requests for a
formal definition of every model and metric (plan §2 R1-M2b, R1-D11), a dataset-role table (R1-D8), and a
merged schedule-integration description (R1-D14). **No result numbers.** Output file:
`rejection revision/manuscript/draft_S2_framework.md` (create the folder locally).

## Content, in this order
1. One opening paragraph and a placeholder line for the workflow figure: `[Figure 1: workflow, image prompt to be written in WP11]`.
2. **Table: dataset and its role** — GSS time-use cycles 2005, 2010, 2015, 2022; Census public-use microdata;
   NRCan SHEU end-use reference; weather files; building archetype models; IESO measured hourly data (T02).
   Columns: dataset · years · what it provides · which framework stage uses it.
3. Subsections, each with prose plus numbered equations in LaTeX (`$$ ... $$`), symbols defined once in a
   symbol list at the end of the section:
   - 2.1 Diary harmonisation to 30-minute slots (definition of the slot activity and presence series).
   - 2.2 Generative day-type model: the conditional likelihood the trained model maximises, written from the
     training code, not from the old text.
   - 2.3 Raking (iterative proportional fitting) of slot marginals: the update rule and stopping criterion,
     from `05_postlink_rake.py` and `06_forecast_rake.py`.
   - 2.4 Census to diary matching: the hierarchical key fallback rule and the fixed seed (see task T13 doc).
   - 2.5 Household aggregation and conversion to EnergyPlus schedules (merge archived §3.5 and §4.2 into one
     description; from `07_aug_to_bem.py` and `07_bemIntegrationGSS.md`).
   - 2.6 Activity-driven end-use loads and the end-use calibration scalar f_e (from `activity_loads.py`,
     `09_activityDrivenLoads.md`); call the SHEU agreement "calibration", never "validation".
   - 2.7 2030 scenario construction: the three work-from-home persistence scenarios as a function of the
     persistence share lambda in {1, 0.5, 0} (from `impl/2026-09-15_WP2_scenario_spec.md` and the WP1 step 2
     retargeting spec). Write "scenario-based projection", never "forecast".
   - 2.8 Sampling procedure: how the 50 households per cell are drawn (pool definition, seed), from the T05
     doc and the engine facts in `../../../Prompts/2J_manager_prompt_RESUME_AE_resubmission.md` §0.
   - 2.9 Stock aggregation weights (archetype weights, split equally over cities).
   - 2.10 Load-shape metrics: annual energy, daily peak, circular mean peak hour, circular standard deviation,
     load factor, midday share over [9, 17), morning-leaning share, and a ramp metric if the code has one.
     Definitions from `Step8_docs/08_simulation_plots.py` (resume prompt cites lines 278 to 290, 340, 361, 377,
     385, 387, 914 to 915; re-read them, they may have moved).
   - 2.11 Paired difference and its confidence interval: pooled paired Student-t, from `08_simulation_val.py`
     lines 951 to 1027 (re-read).
   - 2.12 Comparison arms: fixed schedules (T19, T22 docs) and one average survey profile per cell (T30 doc),
     defined in one equation each.
4. A **trace table** at the end of the draft: equation number · code file:line or task doc it was read from ·
   read by you (yes / NOT VERIFIED).

## Rules
- Every equation is read from code or a task doc and carries a trace row. If the code does something
  different from the archived manuscript, follow the code and add a line to "Decisions" below.
- No result numbers (no percentages, kWh, hours measured). Parameters of the method (for example 30 minutes,
  50 households, seed 42, lambda values) are allowed.
- Plain words. Do not use these labels: "J3", "True-Future-Test", "frozen frame", "Tier-1/2/3", "FailSafe",
  "COLLECT_MODE", "DDAY_STRATA", "Step-8", "Step-9", "occACT", "gate". Describe what the thing does instead.
- Never edit pipeline code, `archive/`, the plan, or other task docs. Read big files with offset/limit.
- No em dashes and no en dashes. Word budget for the section: about 2,500 words plus equations.
- Append progress to "Ledger" and "Verified" below as you go; end the turn when the draft exists.

## Ledger

Status: DONE. Draft written to `manuscript/draft_S2_framework.md` (created the `manuscript/` folder).
Read CLAUDE.md, this task doc, `impl/2026-09-15_T33_wp10_response_map_and_prep.md`,
`impl/2026-09-15_WP2_scenario_spec.md`, and the resume prompt's engine facts (§0, lines 43-49) for
context. Read code directly: `03_mergingGSS.md` (grep + read), `04D_train.py:60-69,160-380`,
`04B_model.py` (grep only, architecture confirmation), `05_postlink_rake.py:79-150`,
`06_forecast_rake.py:67-99,228-294`, `07_aug_to_bem.py` (full file, 234 lines),
`activity_loads.py:33-90,118-266`, `Step8_docs/08_simulation_plots.py:70-90,114,270-397,905-924`,
`08_simulation_val.py:951-1027`, `08_simulation.md` (grep). Sourced from task docs per the task's own
instruction: `impl/2026-09-15_T13_wp1_rebuild_2022_reading.md` (2.4, census matching),
`impl/2026-09-15_T05_wp4_sample_size.md` (2.8, sampling), `impl/2026-09-15_T19_wp3_static_arm_build_smoke.md`
(2.12, fixed arm), `impl/2026-09-15_T30_wp3_average_profile_arm.md` (2.12, average arm),
`impl/2026-09-15_T02_wp5_ieso_measured_profiles.md` (Table 1, IESO row).

## Verified

All 18 equations (numbered 1-18 in the draft) carry a file:line or task-doc trace, listed in the
draft's own "Trace table" section; full detail not repeated here. Confirmed by direct code read:
act30/hom30 construction (`03_mergingGSS.md:424-460`); the model's default loss weights and 3-head
structure (`04D_train.py:60-69,166-380`); the raking mechanism is single-pass exact-count flips, not
iterative (`05_postlink_rake.py:79-99`, `06_forecast_rake.py:228-294`); household aggregation and the
4h clock roll (`07_aug_to_bem.py:93-146`); the equipment power build-up and calibration scalar f_e,
named as such in the code's own docstring (`activity_loads.py:33-90,118-266`); all load-shape metric
definitions at the resume prompt's cited lines (`Step8_docs/08_simulation_plots.py:74-77,114,278-297,
340,361,377,385,387,914-915,300-321`); the paired-difference / pooled paired Student-t CI
(`08_simulation_val.py:951-1027`); the full lambda-scenario equation and its standardised-jump
addendum (`impl/2026-09-15_WP2_scenario_spec.md:8-73`). No ramp metric exists in
`Step8_docs/08_simulation_plots.py` (grepped the whole file for "ramp", no match) - reported as
absent in section 2.10, not invented.

## Decisions

- Followed the code over the archived manuscript for section 2.3: the raking is a single
  deterministic pass of exact-count record flips, not classical iterative proportional fitting
  (no loop, no tolerance parameter in either raking file). Recorded explicitly in the draft.
- Kept appliance wattages, the co-occupancy lookup values, SHEU kWh targets and the archetype
  stock-share weights symbolic in the equations (not quoted as literals), to keep the draft free of
  anything that could read as a measured/reported result; all cited by file:line for the literal
  values.
- `05_census_linkage.py` (cited by the T13 task doc for section 2.4) was not found locally under
  `2J_docs_occ_nTemp/` (search returned nothing) so it was not re-read directly; section 2.4 traces
  to the T13 task doc's own verified reading, per the task doc's instruction to source 2.4 from T13.
  Same treatment for `main.py`, `run_paired_mc.py`, `integration.py`, `idf_optimizer.py` in sections
  2.8 and 2.12, sourced from the T05/T19/T22/T30 task docs as instructed.

## Next

Draft complete, approximately 2,400 prose words (excluding equations/tables/this state file).
Nothing further planned by this task. A later task should decide whether to have an employee locate
and directly re-read `05_census_linkage.py`, `main.py`, `run_paired_mc.py`, `integration.py` and
`idf_optimizer.py` (possibly Speed-side only) before final submission, since this draft's sections
2.4, 2.8 and 2.12 currently trace to task docs rather than to those scripts directly.

## WHAT I DID NOT VERIFY

- `05_census_linkage.py`, `main.py`, `run_paired_mc.py`, `integration.py`, `idf_optimizer.py`: not
  read directly this session (not found locally, or out of scope per the task's own doc-sourcing
  instruction for 2.4/2.8/2.12); their citations in the draft are copied from prior task docs'
  verified readings.
- `07_bemIntegrationGSS.md` and `09_activityDrivenLoads.md` prose docs were not checked line-by-line
  against the code for disagreement; the draft's equations come from the code directly
  (`07_aug_to_bem.py`, `activity_loads.py`), which is authoritative over prose docs per the rules.
- `04B_model.py` was only grepped for architecture confirmation, not read in full; the loss/objective
  equation comes entirely from `04D_train.py`.
- IESO dataset vintage year and licence terms not independently confirmed beyond the T02 task doc's
  opening lines.

## Manager review (plan log (au))
Every trace row re-read by the manager at its cited lines. Confirmed as drafted: Eq. 1 and 2
(`03_mergingGSS.md:424-460`), Eq. 3 weights (`04D_train.py:60-69`), Eq. 4 and 5 single-pass flip rake
(`05_postlink_rake.py:79-99`), Eq. 8 and 9 (`activity_loads.py:33-59,118-182,197-265`), Eq. 10
(`WP2_scenario_spec.md:8-37`), Eq. 12 to 14 and the load factor, midday and morning shares
(`Step8_docs/08_simulation_plots.py:74-77,114,278-321,336-390,905-924`), Eq. 15 and 16
(`08_simulation_val.py:951-975`), Eq. 11 (T05 doc 52-74), Eq. 17 (T19 doc 6-22), Eq. 18 (T30 doc 9-26).
Corrections applied to `manuscript/draft_S2_framework.md` (original kept in the manager scratchpad):
1. Section 2.4 described the published build, not the rebuilt 2022 set. First level no longer uses
   metropolitan area (T18b doc line 18), and the 2022 donor pool is 2022 diaries only (plan decision,
   T18 Nb-f). The sentence "the donor pool pools every survey cycle" was wrong for the new paper; replaced.
2. Section 2.5: `07_aug_to_bem.py:97-100` averages over all member diary-day rows (Saturday and Sunday
   both map to weekend, line 34), and the metabolic lookup applies to every row with a 100 W default,
   not only to present members. Text and symbol list fixed.
3. Eq. 8: the dishwasher term is also multiplied by the co-occupancy factor (`activity_loads.py:173`).
4. Section 2.8: the pool is IDs present in all years simulated together (T21 doc line 15), not every
   cycle-year's file.
5. Section 2.11: added that the interval treats households as independent (reviewer 3 point 6; T03).
6. Section 2.12: named the reference profile (mid-rise standard residential, T19 doc).
7. Section 2.1: three-way ties resolved separately (`03_mergingGSS.md:440-447`).
8. Table 1: Census PUMF year 2021 (archived manuscript line 49).
9. Removed internal state sections (Decisions, Ledger, Verified, Next, not-verified) from the draft
   file and the "decision point against the archived manuscript" wording; they live in this doc.
Open for WP10: `05_census_linkage.py` and `main.py` lines are traced through task docs only; the
clustering check promised in 2.11 must be delivered by WP6 or the sentence is removed.
**Status: T34 DONE (accepted with 9 manager corrections).**
