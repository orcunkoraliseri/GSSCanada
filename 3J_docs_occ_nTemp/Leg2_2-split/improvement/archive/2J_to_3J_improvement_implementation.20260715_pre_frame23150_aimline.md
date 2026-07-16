# Implementation plan: porting the 2J fixes into 3J Leg-2 (2-split)

**Compiled:** 2026-07-15 (manager session)
**Source audit:** [`../investigation/2J_to_3J_audit_reference.md`](../investigation/2J_to_3J_audit_reference.md) (2026-07-15)
**2J-side provenance:** [`2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md`](../../../2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md)
**Status:** PLANNED — no code changed by this document. Each task below is a self-contained employee work package (aim / steps / expected result / test method) to be executed one at a time, in the order given.

---

## Introduction — read this first (background for the executing employee)

You are the **employee**: you execute one task at a time from this document, exactly as written, and append a Progress Log entry at the bottom when done. You do not redesign, reorder, or expand scope; if something blocks you, stop and report the blocker. This chapter gives you all the context you need — you should not have to read the 2J master log or the audit end-to-end to start working.

### What these pipelines are
- **2J** ("2nd journal") is a single-channel occupancy pipeline: it builds synthetic 30-minute residential occupancy diaries from Canadian GSS time-use data + Census, converts them to EnergyPlus schedules, and simulates a residential building stock. Its code lives under `2J_docs_occ_nTemp/`. It went through a long bug-fix campaign in July 2026, recorded in its master log.
- **3J Leg-2** ("3rd journal", the pipeline you are working on) is a **two-channel fork** of the same idea: each synthetic person now carries **two binary occupancy channels** — `hom30_*` (AT_HOME, 48 half-hour slots) and `wrk30_*` (AT_WORK) — plus a 14-category activity channel `act30_*` (code 1 = Work, others = sleep, leisure, etc.). This enables modeling **telework/WFH**: a person can do work activity while at home. The pipeline runs Steps 1→9: diary generation and calibration (Step 4), census linkage (Step 5), 2030 forecasting (Step 6), BEM schedule conversion (Step 7), EnergyPlus simulation of a residential + office building stock (Step 8), and activity-driven load analysis (Step 9). All code lives under `3J_docs_occ_nTemp/Leg2_2-split/Step*_docs/`.
- 3J Leg-2 does **not** share code files with 2J — every script was forked at some point and evolved separately. An audit (`../investigation/2J_to_3J_audit_reference.md`) checked which 2J bugs still exist in the 3J forks. Two do. This document is the plan to fix them.

### The two bugs you are fixing, in plain language
1. **Task 1 — the activity channel was never calibrated.** Step 4's script `3rdJ_04L_joint_rake_2split.py` "rakes" (statistically adjusts) the two binary channels hom30/wrk30 so their population rates match observed GSS rates, slot by slot. But it moves people in and out of the AT_WORK state **without touching their activity codes**. Result: many synthetic person-slots now say "activity = Work" while the person is marked neither at home nor at work. That state — work activity with `hom30=0 & wrk30=0` — is called **FLOATING** and is physically impossible. (Work activity with `hom30=1` is **TELEWORK** and is legitimate — it is the very signal this paper studies, so it must be preserved, never "fixed" away.) The repair: a new script that re-rakes `act30` *conditionally on* the final (hom30, wrk30) state, so activity composition matches occupancy state, using 2J's proven categorical-rake functions as the template.
2. **Task 2 — multi-zone buildings lose most of their equipment/lighting energy.** In Step 8, before simulating, `integration.py` injects household-specific equipment and lighting loads into each building IDF: it first zeroes out ("neutralizes") the legacy ElectricEquipment/Lights objects in **every zone** of the building, then creates one new "carrier" object — but only in **one zone**. For single-zone houses that's fine; for apartment archetypes with N zones (MidRise, HighRise, OtherDwelling), the whole building ends up with ~1/N of its true equipment/lighting electricity. 2J measured 37–99× undercounts and fixed it by creating one carrier per neutralized zone. The 3J file is byte-identical to 2J's pre-fix version, so the fix is a near-direct copy from 2J's fixed file.

### Vocabulary you will meet below
- **Raking**: iterative reweighting/reassignment so synthetic marginal rates match observed targets per cell (cell = year × day-type stratum × time slot, sometimes × labour-force tag LFTAG).
- **Observed vs synthetic rows**: the augmented-diaries CSVs mix real GSS respondents (`IS_SYNTHETIC==0`, the calibration targets) and generated people (`IS_SYNTHETIC==1`, the ones being adjusted).
- **04L → 04M → 04T chain**: 04L = joint binary rake; 04M = "mindwell" minimum-dwell smoother on hom30/wrk30 (removes 1-slot flickers); 04T = the new activity rake you will build, which must run **after** 04M (04M edits the binary channels; if activity were conditioned on them first, 04M would break the conditioning).
- **Gate A / Gate B / S8**: checks inside `3rdJ_04_augmentationGSS_2split_val.py`. Gate A = FLOATING-rate excess (PASS if synthetic ≤ observed + 2pp). Gate B = transition-flicker (median hom30 transitions/day ≤ 1.25× observed). S8 = logged semantic metrics ("Work activity but AT_WORK=0" etc.). Gate A is Task 1's success criterion.
- **Carrier / neutralization / zone**: EnergyPlus terms in Task 2 — a "carrier" is the new ElectricEquipment or Lights object holding the household's SHEU-calibrated wattage; "neutralization" is zeroing the IDF's original objects; a "zone" is one thermal zone of the building model.
- **Campaign / cells / agg tables**: Step 8 runs a SLURM array — residential 4 archetypes × 6 climate zones × 7 scenarios × 50 Monte-Carlo households = 8,400 EnergyPlus runs, office 252 runs — then `3rdJ_08_simulation_2split_agg.py` collapses them into `outputs_step8/agg/agg_*.csv`, which the validator and Step 9 read.

### Working rules (binding)
- **Archive the predecessor** of any file you modify (copy to `<name>.<YYYYMMDD>_pre<Fix>.py` beside it or in the local `archive/`) before editing. Never overwrite pipeline output directories — new outputs go to new dirs (e.g. `R5_raked_mindwell_actv2/`).
- **Tasks 1–3 are strictly local** — no cluster access needed or allowed. Only Task 4 touches the Speed cluster, under the sbatch-only rules restated in its section (no bare `python`/blocking `srun` on the login node, minimum walltime `-t 7-00:00:00`, single-line commands).
- Heavy local runs: this machine cannot be rebooted remotely — if a run risks exhausting RAM, add a hard memory guard or split the work.
- Make the smallest change that satisfies the task; match the surrounding code style; cite exact `file:line` references in your Progress Log entry, and paste the metric tables each task's *Test method* asks for.
- The **OPEN DECISIONS** at the bottom were all resolved by the user on 2026-07-15 (each with the plan's recommended option) — nothing blocks execution. If a NEW decision-level question surfaces mid-task, stop and report it; do not decide it yourself.

---

## 0. Scope resolved by this planning pass (what changed vs. the audit)

The audit left three open questions; the pre-implementation scan (3 employee reports, 2026-07-15) resolved them:

1. **Audit Item 6 (frame size) — RESOLVED, not a bug.** The 3J Leg-2 stock is **23,211 HH** (from 23,882 linked HH pre-exclusion / 30,273 agents; 29,660 after exclusion), consistently stated in Step-7 val reports (`step7_validation_report_2022.html` "N_HH=23,211", same for 2030) and Step-8 docs (`3rdJ_08_simulation_2split_SCOPING.md:63`: "the 3J stock has 23,211 HH (not 144,507)"). The 2J numbers 144,507/144,465 never applied to 3J and no mid-pipeline shrinkage event exists. **Residual: documentation debt only** — stale 2J-inherited comments claiming "144,507 SIM_HH_IDs frozen frame" at `Step8_docs/eSim_bem_utils_3J/main.py:74-75` and `Step8_docs/eSim_bem_utils_3J/integration.py:17`. Folded into Task 2 (we touch `integration.py` anyway).
   > **[MANAGER CORRECTION — 2026-07-15 verification pass]:** the `integration.py:17` citation in this bullet is erroneous — no such comment ever existed in `integration.py`. Line 17 there is the `TARGET_WORKING_PROFILE = [` statement; the file's only match for `SIM_HH_ID`-family strings is legitimate code at `:373` (`row['SIM_HH_ID']`). The stale comment existed only in `main.py:74-75` (still visible in `archive/main.20260629.py:74-75`) and was correctly fixed there (see Task 2's Progress Log entry, which independently confirmed the same thing). Do not re-hunt `integration.py` for this comment.
2. **Office channel is NOT exposed to the multi-zone injection bug.** `Step8_docs/office_integration.py` (415 lines) uses a per-zone in-place `Schedule_Name` override on every existing PEOPLE/LIGHTS/ELECTRICEQUIPMENT object (lines 274–305, `_zone_tag` classifier at 72–84) — nothing is neutralized, no single-zone carrier is created. The injection fix (Task 2) is residential-only.
3. **The 61.12% discordance number overstates the physical problem.** `Step4_docs/3rdJ_04P_work_wrk30_discordance.py` (already in-repo) decomposes "work activity while `wrk30=0`" into **TELEWORK** (`hom30=1` — legitimate, and in fact the paper's core signal) and **FLOATING** (`hom30=0 & wrk30=0` — the only impossible state). This kills the dr_S4-02 "hard-lock `act30==Work → wrk30=1`" option: it would force all work activity into the workplace and destroy the telework signal. Task 1's design goes the other direction — **adapt act30 to the raked binary channels** (the 2J approach, extended from 2 to 3 conditioning states).
   **[MANAGER CORRECTION — 2026-07-15 verification pass]:** the 61.12% figure cited here is itself stale/non-representative — see the full correction at §Task 1 "Current state" (line ~71) below. The conclusion in this bullet (TELEWORK/FLOATING decomposition kills the hard-lock option) is unaffected and still holds under the corrected 50.24% pre-04T baseline.

### Execution order (binding — do not reorder)

An act30 change in Step 4 invalidates **everything** downstream (Step 5 re-link → Step 6 re-forecast → Step 7 re-integrate → Step 8 re-sim → Step 9). An `integration.py` change alone invalidates only Step 8 → agg → Step 9. Therefore: **implement Task 1 and Task 2 first, run the full downstream cascade exactly once** (Task 4), with the fixed `integration.py` already in place. Never re-simulate between the two fixes — that would double the 8,400-run residential campaign.

```
Task 1 (Step-4 act30 conditional rake, local dev + smoke)
Task 2 (integration.py multi-zone port + stale-comment cleanup, local)
Task 3 (verification-only spot-checks, local, can run in parallel with 1-2)
Task 4 (single re-run cascade: 04T → 05 → 06 → 07 → 08 resid+office → agg → val → 09)
```

Cluster note: Speed was unavailable as of ~2026-07-08 (est. ~2 weeks). Tasks 1–3 are fully local. Task 4's Step-8 campaign is the only cluster-bound stage; everything before it can be completed and validated locally while waiting.

---

## Task 1 — act30 conditional re-rake (audit Item 2) 🔴 HIGH, design + build

### Aim
Eliminate the semantic-consistency break introduced by the 04L joint binary rake — synthetic slots whose activity says "Work" while the person is neither at home nor at work (FLOATING), and more generally an activity channel whose composition no longer matches its occupancy state — by raking `act30_*` **conditionally on the final raked (hom30, wrk30) state**, without touching the binary channels themselves. Target metric is the FLOATING rate (Gate A definition), not the raw 61.12% figure (which includes legitimate telework).

### Current state (established by scan)
- `Step4_docs/3rdJ_04L_joint_rake_2split.py` (741 lines): jointly rakes hom30+wrk30 with structural mutual exclusion via `_joint_rake_slot` (lines 314–409, greedy 2N-action transportation matcher) per `(CYCLE_YEAR × DDAY_STRATA × slot)` cell; header lines 21–23 state act30/COP are carried forward untouched. Input `outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv`, output `outputs_step4/sweep/R5_raked/`.
- `Step4_docs/3rdJ_04M_mindwell_2split.py`: min-dwell smoother on hom30/wrk30 **only** (act30 untouched), writes `outputs_step4/sweep/R5_raked_mindwell/augmented_diaries.csv` = Step-5 `FULL_POOL` (`3rdJ_05_censusLinkage_2split.py:44-47`).
- Measured discordance (`Step4_docs/deepResearch/dr_S4-02_posthoc_calibration_raking_REPORT.md`, lines 62–71): raked synthetic "work-act but AT_WORK=0" = **61.12%** vs observed 16.36%; sleep-but-not-home 4.23% vs 3.50%. Transition inflation also documented (§2 of that report).
  > **[MANAGER CORRECTION — 2026-07-15 verification pass]:** the 61.12% figure was measured on `outputs_step4/raked_sample/augmented_diaries_SAMPLE.csv` — a **2,560-synthetic-row diagnostic sample dated 2026-06-18, of lineage disjoint from the 128,122-syn-row R5 sweep** the pipeline actually uses. `dr_S4-02_posthoc_calibration_raking_REPORT.md:55` itself states the figure came from "the local sample run (augmented_diaries_SAMPLE.csv before and after raking)". The `R5_raked/` directory named as this figure's source elsewhere in this doc (a no-mindwell 04L output) **does not exist in the repo at all**. **This 61.12% figure is stale/non-representative and must NOT be cited in the paper or downstream docs as the pre-fix baseline.** The correct pre-04T baseline, measured on the actual pool (`R5_raked_mindwell/`), is **50.24%** (= 26.30% TELEWORK + 23.94% FLOATING) — independently re-derived and consistent with the Task-1 Progress Log's own SYN pre-04T row below (26.30% + 23.94% = 50.24%).
- 2J's proven fix to port from: `2J_docs_occ_nTemp/05_postlink_rake.py` — `_rake_categorical_slot()` (147–207, 14-way minimal-move categorical rake with boundary preference to extend existing runs), `_rake_act_group()` (210–274, splits each slot into hom30=1/0 subsets and rakes each against the matching hom-conditioned observed target), `_run_act30_conditional_rake()` (277–319+, conditions on DDAY_STRATA × slot × LFTAG with a `MIN_OBS_FOR_LFTAG` sparsity gate pooling thin cells). 2J result: weekday paid-work gap +12.3pp → **3.78pp** (`2J_docs_occ_nTemp/outputs_step4/improvement_planning/step4_improvements_implementation.md:97`); synthetic unit test 19/19 PASS.

### Design (recommended — decide before building, see OPEN DECISIONS)
1. **New script `Step4_docs/3rdJ_04T_act_rake_2split.py`** (next free letter; A–S taken). Port `_rake_categorical_slot` / `_run_act30_conditional_rake` from `2J_docs_occ_nTemp/05_postlink_rake.py`, extending 2J's 2-way hom30 conditioning to the 3-way occupancy state: **`wrk30=1` / `hom30=1` / neither**, per `(CYCLE_YEAR × DDAY_STRATA × slot × LFTAG-or-pooled)` cell. Targets = observed (`IS_SYNTHETIC==0`) 14-category activity counts within the matching state cell (unweighted, mirroring 04L's target convention at its lines 594–596), largest-remainder rounding (`_round_to_sum`, 2J 118–144).
2. **Run position: AFTER 04M**, not between 04L and 04M. 04M edits hom30/wrk30; raking act30 before 04M would let the smoother re-break the conditioning. 04T reads `R5_raked_mindwell/augmented_diaries.csv`, writes **`R5_raked_mindwell_actv2/augmented_diaries.csv`** (new dir — never overwrite the predecessor; keep `R5_raked_mindwell` as-is for provenance) + a rake-provenance JSON (mirror `g2ow1_rake_provenance.json` conventions).
3. **Semantic guardrails inside the rake** (this is where 3J goes beyond a blind categorical rake):
   - Slots with `wrk30=1`: work-activity codes are valid; rake to the observed at-work activity mix.
   - Slots with `hom30=1, wrk30=0`: work activity is **legitimate telework** — rake to the observed at-home mix (which contains 16.36%-level work share), do NOT zero it.
   - Slots with `hom30=0 & wrk30=0`: work activity is impossible → the conditional targets (observed neither-state mix) naturally drive it to the observed floating-work rate (~0). This is the mechanism that closes Gate A, without any hard lock.
   - Keep 2J's boundary preference (extend adjacent same-state runs; gate it on the neighbour sharing the same 3-way state, generalizing 2J's hom-status gate at its lines 251–267) to avoid re-inflating transition counts.
4. **Step-5 pointer update:** `3rdJ_05_censusLinkage_2split.py` `FULL_POOL` (lines 44–47) → `R5_raked_mindwell_actv2/augmented_diaries.csv`.
5. **2030 path:** Step 6 (`3rdJ_06_longitudinalForecasting_2split.py`) reads the augmented diaries and its `mutual_exclusion_resolve()` (2116–2139) arbitrates hom/wrk conflicts using `act30==Work` — after Task 1 this arbitration input is calibrated, which is a free improvement. Whether the 2030 synthetic diaries need their **own** 04T pass (2J's analogue: `06_forecast_rake.py` reusing the same functions, its line 511) must be checked during Task 4: if the Step-6 output's FLOATING rate (via `3rdJ_04P` probe) exceeds Gate-A bounds, apply 04T's rake to the 2030 file with 2022-observed conditional targets, exactly as 2J did.

### Steps (employee)
1. Read 2J's `05_postlink_rake.py:118-319` and 3J's `3rdJ_04L_joint_rake_2split.py`, `3rdJ_04M_mindwell_2split.py`, `3rdJ_04P_work_wrk30_discordance.py` in full before writing code.
2. Build `3rdJ_04T_act_rake_2split.py` per the design above (CLI: `--in_csv`, `--out_dir`, `--seed`, `--smoke` for a stratified subsample).
3. Synthetic unit test first (mirror 2J's 19-case test): construct a toy frame with known state-conditional activity marginals, verify exact target attainment, mutual state respect (no act code moved across a (hom,wrk) state boundary), determinism under fixed seed, and no record touched twice per slot-call.
4. Run 04T on `R5_raked_mindwell/augmented_diaries.csv` (local; the file is Step-4-sized, not the 500 MB 2J monster, but still delegate the run + metric extraction to a cheap session if it strains memory — see the local-run guard rule).
5. Before/after metrics with `3rdJ_04P_work_wrk30_discordance.py` (run it on both the input and the output CSV) + the Section-8/Gate-A/Gate-B blocks of `3rdJ_04_augmentationGSS_2split_val.py` (lines 845–940).
6. Update the Step-5 `FULL_POOL` pointer (do not run Step 5 yet — that is Task 4).
7. Document in `3rdJ_04_augmentationGSS.md` (append; note 04T in the step-4 script inventory) and append a Progress Log entry.

### Expected result
- `R5_raked_mindwell_actv2/augmented_diaries.csv` with identical row count/schema to its input, hom30/wrk30 **byte-identical** to input, act30 re-raked.
- FLOATING share of work-activity slots (04P decomposition): from current level down to ≤ observed + 2.0pp (Gate A PASS band, `GATE_A_PASS_PP` in the validator).
- "Work-act but AT_WORK=0" (S8 metric): from 61.12% to the neighbourhood of the observed 16.36% + retained telework share — report the exact number; do not tune to it, tune to Gate A.
  > **[MANAGER CORRECTION — 2026-07-15]:** the 61.12% starting point named here is stale/non-representative — the real pre-04T baseline on the actual pool (`R5_raked_mindwell/`) is **50.24%**. See the full correction at §Task 1 "Current state" above. Does not change the target (Gate A / observed 16.36%+telework), only the "from" figure.
- 14-category activity KL(obs‖syn) (validator lines 890–894) improved or unchanged; Gate B (transition flicker, ≤1.25× obs median) not degraded vs. the pre-04T value.

### Test method
- Synthetic unit test suite PASS (all cases).
- `3rdJ_04P` before/after table pasted into the Progress Log (OBS / SYN-pre / SYN-post × AT-WORK/TELEWORK/FLOATING).
- Full `3rdJ_04_augmentationGSS_2split_val.py` run on the 04T output: Section 4 (G4), Section 8, Gate A, Gate B all at PASS/WARN, zero new FAIL vs. the current baseline report.
- Spot-check 20 random synthetic person-days by eye: no work activity in (0,0) slots, telework episodes preserved, no 1-slot activity flickers introduced.

### Paste-ready employee prompt
> You are the employee. Execute Task 1 of `3J_docs_occ_nTemp/Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md` (act30 conditional re-rake, new script `3rdJ_04T_act_rake_2split.py`). Follow the design, steps, and test method exactly as written there; the 2J reference implementation is `2J_docs_occ_nTemp/05_postlink_rake.py:118-319`. Everything is local — no cluster. Do not modify 04L/04M outputs; write to a new `R5_raked_mindwell_actv2/` dir. Append a Progress Log entry to the implementation doc on completion, including the 04P before/after decomposition table and the validator gate lines.

---

## Task 2 — multi-zone equipment/lighting injection port (audit Item 4) 🔴 HIGH, mechanical

### Aim
Port 2J's already-validated fix into `Step8_docs/eSim_bem_utils_3J/integration.py`: replicate the Step-9 SHEU carrier objects across **every zone that had a legacy object neutralized** (fallback: occupancy zone only if the set is empty), removing the ~1/N_units whole-building equipment/lighting undercount on multi-zone residential archetypes (MidRise, HighRise, OtherDwelling; SingleD single-zone unaffected; office channel not exposed — see §0.2).

### Current state (established by scan)
- 3J file: `Step8_docs/eSim_bem_utils_3J/integration.py` (2506 lines). Neutralization loops: equipment **1552–1586**, lights **1649–1657** (all zones, no zone-set collection). Single-zone carrier injections: equipment **1605–1614**, fridge fallback **1629–1638**, lights **1683–1692** (all `_s9_set_zone(..., _s9_occ_zone)`).
- 2J fixed reference: `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py` — `_s9_equip_zones` collection at 1551–1596, replication loop 1615–1625, fridge replication 1627–1653; `_s9_light_zones` at 1663–1679, replication 1705–1715.
- Diff between the two files confirms the Step-9 block is **byte-identical pre-fix code** (same `_s9_get_zone`/`_s9_set_zone`/`_s9_occ_zone`/`hh_id` names); 3J's only structural additions (`step8_occ_couple` param + its block at ~1706–1707/1964–1991) sit outside the patch region. The in-place `step8_occ_couple` and `load_targets` paths (1973–1991, 1721–1727) are per-existing-object and NOT affected — do not touch them.
- Expected impact reference (2J measured): ~37–99× undercount depending on archetype; post-fix MidRise peak corrected to 16.72h, HighRise 50/50 validation batch circular mean 17.32h, OtherDwelling magnitude restored exactly 7.00× (= its zone count).

### Steps (employee)
1. Read both files' Step-9 blocks side by side (3J 1540–1720; 2J fixed 1540–1720).
2. Apply the 2J pattern to 3J: collect `_s9_equip_zones` during the equipment neutralization loop (add `_z = _s9_get_zone(_eo); if _z: _s9_equip_zones.add(_z)`), fall back to `{_s9_occ_zone}` if empty, replace the single `newidfobject("ElectricEquipment")` with the sorted-zone replication loop (per-zone names `STEP9_Equip_{hh_id}_{zi}`); same for the fridge fallback loop and for lights (`_s9_light_zones`, `STEP9_Lights_{hh_id}_{zi}`). Keep per-zone design levels identical to 2J's convention (2J divides nothing — the carrier watts are per-zone replicas; confirm against 2J lines 1615–1625 and copy exactly).
3. Same-file cleanup: correct the stale frame comment at `integration.py:17` (and `main.py:74-75`) from "144,507 SIM_HH_IDs" to "23,211 SIM_HH_IDs (3J Leg-2 stock; see 3rdJ_08_simulation_2split_SCOPING.md §OD-8F)".
   > **[MANAGER CORRECTION — 2026-07-15]:** `integration.py:17` was an erroneous citation in this plan — no such comment ever existed there (confirmed by the employee's Task 2 entry below, which found zero matches). Only `main.py:74-75` needed the fix, and that was correctly done.
4. Archive the predecessor: copy the pre-fix file to `Step8_docs/eSim_bem_utils_3J/` archive convention (e.g. `integration.20260715_preMultizoneFix.py`) before editing, matching how 2J and prior 3J fixes preserved predecessors.
5. Local smoke test (NO cluster): eppy-load one MidRise and one HighRise IDF from `Buildings_MTL_v242_3Jfix/` (or the canonical v24.2 set Step 8 actually uses — confirm from `3rdJ_08B_run_paired_mc.py`), run the injection path for 2–3 households, then assert on the resulting IDF objects: (a) count of STEP9_Equip/STEP9_Lights objects == count of zones that had a neutralized legacy object, (b) every neutralized zone is covered, (c) SingleD still gets exactly 1 carrier, (d) total injected Design_Level across zones ≈ N_zones × per-zone level (magnitude restoration ratio == zone count, mirroring 2J's 7.00× OtherDwelling check).
6. Append a Progress Log entry with the smoke-test object tables.

### Expected result
Patched `integration.py` whose Step-9 block matches 2J's fixed logic line-for-line (modulo module-name imports); smoke test shows carrier replication across all neutralized zones on multi-zone archetypes and unchanged single-zone behaviour. No re-simulation yet (Task 4).

### Test method
Smoke-test assertions (a)–(d) above, plus a `diff` of the patched 3J Step-9 block against 2J's fixed block showing only the expected import/encoding deltas. Full energetic validation happens in Task 4 (agg tables + gate 4.9 family + Step-9 G8o re-checks).

### Paste-ready employee prompt
> You are the employee. Execute Task 2 of `3J_docs_occ_nTemp/Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md` (multi-zone injection port into `Step8_docs/eSim_bem_utils_3J/integration.py`). The fixed reference is `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py` (equip 1551–1653, lights 1663–1715). Archive the predecessor file first. Local eppy smoke test only — do NOT launch any simulation campaign or touch the cluster. Append a Progress Log entry on completion.

---

## Task 3 — verification-only spot-checks (audit Items 1, 3, 5) 🟢 LOW, local, parallelizable

### Aim
Close the three "already fixed" audit items with logged evidence instead of by-analogy claims.

### Steps / expected / test (one bundle)
1. **Item 1 (2005 region linkage):** no 3J-specific 2005 matched-share number was ever logged (2J's ~15.76% is cited by analogy only). Write a ~30-line probe that loads `outputs_step5` matched-keys output (`3rdJ_25CEN_aug_Matched_Keys.csv` or equivalent), computes per-cycle matched share, and confirms 2005 is in family with 2010/2015/2022 (not collapsed to ~9%-style failure). Expected: 2005 share within ~0.5× of the other cycles. Record the number in the Progress Log — it becomes 3J's own reference figure.
2. **Item 3 (+4h roll):** already confirmed at `3rdJ_07_aug_to_bem_2split.py:156-157` (occ/met) and `:307` (office wrk). Nothing to run; cite these lines in the Progress Log as closed.
3. **Item 5 (ERV / gate 4.9):** confirmed v3 executed (WARN not FAIL, 2026-07-08; §12.4 of `Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`). One decision to record: a merged report `outputs_step8/step8_validation_report_v3_merged.html` (50P/2W/17I/0F) already combines the job-1069196 full report with the corrected §4 — decide whether this supersedes the "regen canonical HTML once cluster returns" item. **Recommendation: it does NOT fully supersede** — Task 4's re-simulation regenerates the whole report anyway, which retires this item for free. Mark Item 5's residual as "absorbed by Task 4".

### Paste-ready employee prompt
> You are the employee. Execute Task 3 of `3J_docs_occ_nTemp/Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md` (three verification spot-checks, all local, read-only except the one small probe script). Deliverable: the 2005 per-cycle matched-share table + the two citation closures, appended as a Progress Log entry.

---

## Task 4 — single downstream re-run cascade 🔴 gate to PAPER-READY, cluster-bound at Step 8

### Aim
Propagate Task 1's recalibrated act30 and Task 2's fixed injection through the pipeline in **one** pass, restoring end-to-end validated status (current baselines to beat/match: Step 5 val 20P/1W post-fix; Step 7 val 2022 34/0/0 & 2030 33/0/0 style; Step 8 46P/1W/13I/0F; Step 9 10P/1W/0F with G8o PASS).

### Preconditions
Tasks 1–2 merged and smoke-tested; Speed cluster reachable again; Task 3 item-1 probe done (so the Step-5 re-run has a 2005 reference to compare against).

### Cascade (scripts and artifacts, in order)
| # | Step | Run | Input → Output | Where |
|---|---|---|---|---|
| 1 | 4T | `3rdJ_04T_act_rake_2split.py` (done in Task 1; re-run only if 04L/04M re-ran) | `R5_raked_mindwell/` → `R5_raked_mindwell_actv2/` | local |
| 2 | 5 | `3rdJ_05_censusLinkage_2split.py` + val | actv2 pool + `Aligned_Census_2025.csv` → `3rdJ_25CEN_aug_*` (+ `_excl`) | local |
| 3 | 6 | `3rdJ_06_longitudinalForecasting_2split.py` + calibrate + telework control | 2022 stock + drift matrices → `2030_synthetic_diaries_2split_calibrated_mindwell.csv` (`_C`) | local |
| 3b | 6-gate | `3rdJ_04P` probe on the 2030 output; if FLOATING > Gate-A band, apply 04T with 2022-observed targets (2J `06_forecast_rake.py` analogue) | — | local |
| 4 | 7 | `3rdJ_07_aug_to_bem_2split.py` + val | Step-5 `_excl` + Step-6 `_C` → `BEM_Schedules_2split_*.csv`, `office_presence_multiplier_*.csv` | local |
| 5 | 8 | `run_residential_array.sh` (168 tasks × 50 MC = 8,400 runs) + `run_office_array.sh` (252 runs) — **both channels**, because Step-7 outputs changed for both | Step-7 outputs + IDFs → `campaign/` + `office/` trees | **cluster, sbatch only, `-t 7-00:00:00`** |
| 6 | 8-agg | `3rdJ_08_simulation_2split_agg.py` then `3rdJ_08_simulation_2split_val.py` | run trees → `outputs_step8/agg/agg_{annual,peak,diurnal,meta,enduse_annual}.csv` + HTML report | cluster (sbatch) |
| 7 | 9 | `3rdJ_09_activityDrivenLoads_2split.py` | agg tables → `step9_report.html` | cluster (sbatch) |

Note Step 9 in 3J reads only the Step-8 agg tables (no local campaign of its own, no direct act30 use) — the 2J caution about "Step 9's own campaign exposure" has no 3J analogue beyond re-running step 7 above.

### Expected result / test method
- Every validator re-run at 0 FAIL; specifically watch: Step-4 val Gate A/B + S8 on the final pool; Step-5 §1.4 tier proportions + the new 2005 share; Step-6 C4 WFH gate; Step-7 N_HH=23,211 + Metabolic_Rate shape sanity (act30 now feeds `MET` mapping at `3rdJ_07_aug_to_bem_2split.py:79,138` — expect visible daytime metabolic changes, that is the point); Step-8 gate 4.9 (WARN acceptable per ERV v3), the multi-zone magnitude checks (MidRise/HighRise/OtherDwelling equipment electricity up by ~zone-count factor vs. the pre-fix campaign — compare `agg_enduse_annual.csv` old vs new and log the ratios); Step-9 G8o (WFH modulation signal) and office EUI band gate.
- Since **both** fixes land in one campaign, attribute magnitude deltas carefully in the Progress Log: equipment/lighting level shifts on multi-zone archetypes ⇒ Task 2; activity-shape / metabolic / telework-signal shifts ⇒ Task 1. Keep the old `outputs_step8/agg/` tables archived pre-overwrite for this comparison.
- Paper-facing deliverable: an updated acceptance note appended to `../investigation/2split_results_acceptance_review.md` recording the new scorecards and superseding the 2026-07-02 PAPER-READY verdict.

### Cluster etiquette (hard rules, restated for the employee)
- `sbatch` only; NEVER blocking `srun`/bare `python` on `speed-submit2`; single-line commands; `-t 7-00:00:00` minimum walltime on every job including probes; read outputs later via single-file `tail`/`cat`; no polling loops (report job IDs back and stop).

---

## OPEN DECISIONS — ✅ ALL RESOLVED by the user, 2026-07-15 (nothing here blocks execution)

1. **OD-I1 — act30 rake design: ✅ RESOLVED — 3-way state-conditional categorical rake (2J port).** The dr_S4-02 hard-lock is rejected (it would suppress the telework signal, §0.3). Build Task 1 exactly as designed; no comparative smoke needed.
2. **OD-I2 — LFTAG conditioning: ✅ RESOLVED — keep LFTAG with 2J's `MIN_OBS_FOR_LFTAG` sparsity pool-up.** Report the pooling rate in the Task-1 Progress Log; if >50% of cells pool up, flag it to the manager (do not switch design unilaterally).
3. **OD-I3 — re-sim scope: ✅ RESOLVED — full campaign** (residential 168 array tasks / 8,400 runs + office 252 runs, both channels), since Task 1 changes BEM schedules for all archetypes.
4. **OD-I4 — 2030 second rake (step 3b): ✅ RESOLVED — conditional on the 04P probe.** Apply 04T to the Step-6 2030 output (with 2022-observed conditional targets) only if its FLOATING rate exceeds the Gate-A band (observed + 2.0pp).

---

## Progress Log

*(employees append below — one dated entry per task, include the metric tables specified in each task's test method)*

### 2026-07-15 — Task 3 (verification-only spot-checks, audit Items 1, 3, 5) — DONE, all local

**Item 1 (2005 region linkage) — 3J-specific reference number now logged.**
Wrote `Step5_docs/_2005_matchshare_probe.py` (read-only, matches the surrounding `_gap_analysis_tmp.py`/`_q1234_analysis.py` style — raw-string paths, `usecols`-scoped `pd.read_csv`, flat printout). It compares each GSS `CYCLE_YEAR`'s share of the Step-5 donor pool (`Step4_docs/outputs_step4/sweep/R5_raked_mindwell/augmented_diaries.csv`, 192,183 rows) against its share of the matched output (`Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Schedules.csv`, 30,273 rows — used in place of `3rdJ_25CEN_aug_Matched_Keys.csv` because the latter drops `CYCLE_YEAR`; `Full_Schedules.csv` carries the same matched rows plus `CYCLE_YEAR` joined in via `expand_slot_schedules()`, confirmed row-count-consistent).

| CYCLE_YEAR | pool_share_% | matched_share_% | ratio (matched/pool) |
|---|---|---|---|
| 2005 | 30.00 | 32.55 | 1.08 |
| 2010 | 23.59 | 23.66 | 1.00 |
| 2015 | 27.15 | 25.65 | 0.95 |
| 2022 | 19.26 | 18.13 | 0.94 |

**2005 matched share = 32.55%**, ratio 1.08 vs. its own pool share — squarely in family with 2010/2015/2022 (ratios 0.94–1.08, all within the expected ~0.5×–1.5× band around 1.0). No collapse toward a ~9%-style linkage failure. This is 3J's own reference figure going forward (2J's ~15.76% no longer needs to be cited by analogy for this item). Script left in place at `3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/_2005_matchshare_probe.py`.

> **[MANAGER CORRECTION — 2026-07-15 verification pass]:** the numbers in the table above are all exactly correct, but **32.55% needs a precision caveat**: it is a **per-cycle row-composition share** (each cycle's share of the matched output; the four `matched_share_%` values sum to 100%), **not a matched-rate** (fraction of a given cycle's own records that got matched). It is therefore **not comparable to 2J's ~15.76% matched-rate figure** — do not cite 32.55% against 2J's 15.76% in the paper or elsewhere. The actual evidence against a 2005 linkage collapse is the **ratio column** (2005 = 1.08 vs 0.94–1.00 for the other cycles), which remains valid as stated above.

**Item 3 (+4h diary→clock roll) — CLOSED, citations verified.**
Read the live file; both roll sites confirmed exactly as claimed:
- `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py:156-157` — residential occ/met: `occ24 = np.roll(occ24, 4, axis=1)` / `met24 = np.roll(met24, 4, axis=1)`, under the `# FIX 2026-06-08 (4h diary->clock offset, ported from 2J)` comment (lines 153-155).
- `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py:307` — office wrk channel: `wrk24 = np.roll(wrk24, 4)`, same convention (comment at line 306).

Both still point at live roll logic, unchanged since the audit. No action needed.

**Item 5 (ERV / gate 4.9) — residual marked absorbed by Task 4.**
Confirmed `Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md` §12.4 (line 567 header, table row at line 637): fix v3 executed and re-verified locally 2026-07-08, gate 4.9 = WARN not FAIL (CZ7A ratios all <1×: SingleD 0.20, MidRise 0.67, OtherDwelling 0.33, HighRise 0.71). Confirmed `Step8_docs/outputs_step8/step8_validation_report_v3_merged.html` exists (1.4 MB, dated 2026-07-13). Per the plan's recommendation: the merged report does **not** fully supersede the "regen canonical HTML" item — Task 4's re-simulation cascade regenerates the whole report anyway. **Item 5's residual status: absorbed by Task 4.** No standalone regen scheduled.

**Blockers:** none. All three items closed/logged as scoped; no scope expansion.

---

### 2026-07-15 — Task 2 (multi-zone equipment/lighting injection port) — DONE

**Predecessor archived first:** `Step8_docs/eSim_bem_utils_3J/archive/integration.20260715_preMultizoneFix.py` (byte copy of the pre-fix file, matches the local archive convention already used for `integration.20260603.py` / `integration.20260604.py` / `integration.20260708_*.py`).

**Files changed:**
- `Step8_docs/eSim_bem_utils_3J/integration.py` — Step-9 equipment/lighting consolidation block patched to 2J's per-zone replication pattern:
  - Equipment neutralization loop `integration.py:1552-1594` — added `_s9_equip_zones = set()` (1552) and per-object zone collection `_z = _s9_get_zone(_eo); if _z: _s9_equip_zones.add(_z)` (1592-1594), fallback `if not _s9_equip_zones: _s9_equip_zones = {_s9_occ_zone}` (1596-1597).
  - Equipment carrier injection `integration.py:1616-1626` — single `newidfobject` call replaced with `for _zi, _zname in enumerate(sorted(_s9_equip_zones)):` loop, per-zone names `STEP9_Equip_{hh_id}_{_zi}`.
  - Fridge fallback loop `integration.py:1628-1654` — same sorted-zone loop, names `STEP9_Fridge_{hh_id}_{_zi}`.
  - Lights neutralization loop `integration.py:1662-1680` — `_s9_light_zones` collection + fallback, mirroring equipment.
  - Lights carrier injection `integration.py:1706-1719` — sorted-zone loop, names `STEP9_Lights_{hh_id}_{_zi}`.
  - Log lines updated to report `len(_s9_equip_zones)` / `len(_s9_light_zones)` (e.g. `integration.py:1658-1659`, `:1718-1719`).
  - `step8_occ_couple` block (`:1729-1732`) and the `load_targets` loop guards immediately following it — **not touched**, confirmed by direct read after patching.
- `Step8_docs/eSim_bem_utils_3J/main.py:74-77` — stale frame comment fixed: "144,507 SIM_HH_IDs (frozen frame, verified)" → "23,211 SIM_HH_IDs (3J Leg-2 stock; see 3rdJ_08_simulation_2split_SCOPING.md §OD-8F) (frozen frame, verified)".
- `Step8_docs/eSim_bem_utils_3J/integration.py:17` — **discrepancy, not fixed, none needed:** grepped the live file (and the newly-archived pre-fix copy) for `144,507` / `144507` / `SIM_HH_IDs` / `frozen frame` — zero matches anywhere in `integration.py`, at line 17 or otherwise. Line 17 is actually the `TARGET_WORKING_PROFILE` comment, unrelated to frame size. The stale-comment claim in this doc's §Task 2 "Current state" for `integration.py:17` does not hold against the current file; only `main.py:74-77` had the real instance, which is fixed above. Flagging as a doc-accuracy note, not a blocker.

**Office channel:** `Step8_docs/office_integration.py` not opened or modified, per scope (§0.2 confirmed not exposed to this bug).

**Canonical IDF set confirmed from `3rdJ_08B_run_paired_mc.py:35-44`:** `STEP8_BUILDINGS_DIR` (imported from `eSim_bem_utils_3J.main`) resolves to `Buildings_MTL_v242_3Jfix/` (`main.py:84`), matched by archetype-name substring (`main.py:106-111`): SingleD→`DetachedHouse`, OtherDwelling→`AttachedHouse`, MidRise→`ApartmentMidRise`, HighRise→`ApartmentHighRise`. Used exactly these 4 files for the smoke test.

**Local eppy smoke test** (script: `task2_smoke_test.py`, run via `py -3`, no cluster, no simulation — eppy load → `integration.inject_schedules()` → eppy re-load of the saved output IDF only):

| hh_id | archetype | IDF | ref zones (equip) | STEP9_Equip carriers | equip zones covered | STEP9_Fridge carriers | ref zones (lights) | STEP9_Lights carriers | light zones covered | equip carrier total/each ratio | light carrier total/each ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SMOKE_MR_001 | MidRise | ASHRAE901_ApartmentMidRise...v242.idf | 25 | 25 | True | 25 (no named fridge) | 27 | 27 | True | 8750.0/350.0 = 25.0 | 3240.0/120.0 = 27.0 |
| SMOKE_MR_002 | MidRise | (same) | 25 | 25 | True | 25 (no named fridge) | 27 | 27 | True | 25.0 | 27.0 |
| SMOKE_HR_001 | HighRise | ASHRAE901_ApartmentHighRise...v242.idf | 25 | 25 | True | 25 (no named fridge) | 27 | 27 | True | 25.0 | 27.0 |
| SMOKE_SD_001 | SingleD | DetachedHouse+CZ6A+IECC+2024...v242.idf | 1 | 1 | True | 0 (named fridge found, calibrated in-place) | 1 | 1 | True | 350.0/350.0 = 1.0 | 120.0/120.0 = 1.0 |

"ref zones" = independently recomputed (fresh eppy load of the **original, pre-injection** IDF, not reusing any patched code) count of unique zones referenced by non-fridge legacy ELECTRICEQUIPMENT/LIGHTS objects — the ground truth for assertions (a)/(b).

**Assertions (per Task 2 test method):**
- (a) carrier count == neutralized-zone count: PASS all 4 cases (25=25, 25=25, 25=25, 1=1 for both equip and lights).
- (b) every neutralized zone covered: PASS all 4 cases (`equip_carrier_zones_n`/`light_carrier_zones_n` set-equal to the independently-recomputed reference zone sets).
- (c) SingleD gets exactly 1 carrier: PASS (SMOKE_SD_001: 1 equip carrier, 1 light carrier; note the raw DetachedHouse IDF has 8 ELECTRICEQUIPMENT objects but all target the same `living_unit1` zone, so the zone-set correctly collapses to 1 — confirmed at `Buildings_MTL_v242_3Jfix/DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf:3100-3195`).
- (d) magnitude restoration ratio == zone count: PASS all 4 cases (MidRise/HighRise 25.0×/27.0× exactly matching their equip/light zone counts; SingleD 1.0×/1.0×), mirroring 2J's OtherDwelling 7.00× check.

MidRise/HighRise raw building files: 92/69 `ZONE` objects total, 26 `ELECTRICEQUIPMENT` / 50 `LIGHTS` objects each (multiple legacy objects per zone in some cases, e.g. duplicate equipment rows), collapsing to 25 unique equip zones / 27 unique light zones (one of which is a shared `Office` zone and a `Corridor` zone that also carry ElectricEquipment/Lights objects in the DOE prototype — included in the neutralization+replication set exactly as 2J's pattern does, since the fix targets *every* zone that had a legacy object, not only residential-unit zones).

**Diff vs. 2J's fixed block** (`2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py:1539-1718` vs patched `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/eSim_bem_utils_3J/integration.py:1540-1719`, unified diff, ~~4 hunks / 56 diff lines total~~):
> **[MANAGER CORRECTION — 2026-07-15 verification pass]:** the hunk/line bookkeeping above was wrong. The actual diff is **5 hunks / 20 changed lines (10 removed, 10 added), 7 distinct change locations at zero context** — of which **5 are mojibake em-dash artifacts** (`—` vs `â€"`) in comments/print text, and **2 are intentional narrative/date comment rewrites**. The load-bearing part of the claim below is correct and independently re-confirmed: **zero diffs touch any executable line.**
- ~~3 hunks~~ **5 of the 7 change locations** are pure encoding artifacts: 3J's file already carried mojibake em-dashes (`â€"` instead of `—`) in these exact comment/print lines *before* this fix (confirmed identical in the archived predecessor copy) — a pre-existing UTF-8/cp1252 round-trip issue in 3J's file history, not introduced by this patch, and left as-is (out of scope to fix file-wide encoding).
- ~~1 hunk~~ **2 of the 7 change locations are** an intentional narrative difference: the neutralization-loop comment cites 3J's own fix context ("the root cause of the equipment/lighting undercount ported from 2J (2026-07-15)") instead of 2J's own discovery narrative ("2022/2030 phantom-peak defect found during manuscript QA (2026-07-13)") — correct, since 3J's defect was found via this audit, not via 2J's manuscript QA. Same for the lights-loop date tag (07-15 vs 07-13).
- All executable code lines (loop structure, variable names, carrier-naming convention `STEP9_{Equip,Lights,Fridge}_{hh_id}_{zi}`, `Design_Level`/`Lighting_Level` handling, fallback logic) are byte-identical between the two files. No import-line deltas appear in this block (module imports live outside the excerpted range; `eSim_bem_utils_3J` vs `eSim_bem_utils_2J` package-name differences are pre-existing and untouched).

**Expected result:** met — patched `integration.py` Step-9 block matches 2J's fixed logic line-for-line modulo the encoding/narrative deltas above; smoke test confirms carrier replication across all neutralized zones on both multi-zone archetypes tested (MidRise, HighRise) and unchanged single-carrier behaviour on SingleD. No re-simulation run (correctly deferred to Task 4).

**Blockers:** none. Local-only, eppy smoke test only, no cluster/sbatch/ssh touched, office_integration.py not modified, step8_occ_couple/load_targets paths verified untouched.

---

### 2026-07-15 — Task 1 DONE: act30 conditional re-rake built, Gate A CLOSED (employee: Claude Sonnet 5)

**Read first, per Introduction:** `2J_docs_occ_nTemp/05_postlink_rake.py:118-319` in full
(`_round_to_sum` 118-144, `_rake_categorical_slot` 147-207, `_rake_act_group` 210-274,
`_run_act30_conditional_rake` 277-331), plus `Step4_docs/3rdJ_04L_joint_rake_2split.py`,
`3rdJ_04M_mindwell_2split.py`, `3rdJ_04P_work_wrk30_discordance.py` end-to-end before writing code.

**Built:**
1. `Step4_docs/3rdJ_04T_act_rake_2split.py` (new file — next free letter after S). CLI
   `--in_csv --out_dir --seed --smoke [--smoke_frac]`, as specified. Ports 2J's four functions
   verbatim (`_round_to_sum`, `_rake_categorical_slot`) or with the 3-way extension
   (`_rake_act_group`, `_run_act30_conditional_rake`), replacing 2J's 2-way `hom30==1/0` split with
   a 3-way occupancy state derived from the FINAL raked (hom30, wrk30): `STATE_WORK` (wrk30==1),
   `STATE_HOME` (hom30==1 & wrk30==0, includes legitimate TELEWORK), `STATE_NEITHER` (hom30==0 &
   wrk30==0, the FLOATING state when act30==Work). Cell = `(CYCLE_YEAR × DDAY_STRATA × slot ×
   LFTAG-or-pooled)`, `MIN_OBS_FOR_LFTAG=30` kept unchanged (`3rdJ_04T_act_rake_2split.py:83`).
   Boundary preference (extends same-state runs) is gated on the neighbour sharing the SAME 3-way
   state — generalizes 2J's hom-status gate (`_rake_act_group`, in-file comment at the boundary
   block). hom30_*/wrk30_* are read-only throughout; only act30_* is ever written back
   (`df.loc[syn_g_idx, act_p] = act_arr`, never touches `hom_p`/`wrk_p`) — verified byte-identical
   pre/post via `np.array_equal` on every run, with a hard `RuntimeError` abort-before-write if it
   ever isn't.
   **3J-specific extension (flagged, not a silent deviation):** ~2.2% of syn rows carry
   `LFTAG==NaN` (2J's source data never has this). Rather than leaving them completely unraked
   (2J's literal group-membership logic would silently skip them), folded them into the same
   "pooled" (cy,s)-level group as sparsity-thin LFTAG values
   (`3rdJ_04T_act_rake_2split.py`, `_run_act30_conditional_rake`,
   `pooled_syn_mask = syn_cs_mask & (df["LFTAG"].isin(thin) | df["LFTAG"].isna())`). This is a
   data-completeness fix (closes a gap 2J's design didn't need to handle), not a redesign of the
   pooling logic itself.
2. `Step4_docs/3rdJ_04T_act_rake_2split_test.py` — synthetic unit test suite (27 cases, exceeds
   2J's 19). Categories: `_round_to_sum` (4), `_rake_categorical_slot` exact-attainment /
   no-op / boundary-preference / determinism / no-double-touch (6), 3-way state + mutual-state
   respect + TELEWORK preservation + FLOATING suppression (7), full-run integration incl. LFTAG
   pooling + determinism + no cross-slot contamination (5), end-to-end schema/scope preservation
   (5). **Result: 27/27 PASS** (`py -3 3rdJ_04T_act_rake_2split_test.py`, exit 0).
3. `3rdJ_05_censusLinkage_2split.py:44-47` `FULL_POOL` repointed from `R5_raked_mindwell/` to
   `R5_raked_mindwell_actv2/` (Step 5 itself NOT run — that is Task 4, per binding execution
   order). Predecessor archived
   `Step5_docs/3rdJ_05_censusLinkage_2split.20260715_preFULLPOOLactv2.py` before editing (diffed
   afterward to confirm only the `FULL_POOL` block changed).
4. `3rdJ_04_augmentationGSS.md` — new dated entry appended (script inventory note + full
   before/after tables), mirroring the existing 04L/04M entry format.

**Real run:** `outputs_step4/sweep/R5_raked_mindwell/augmented_diaries.csv` (192,183 rows, 544.8 MB)
→ `outputs_step4/sweep/R5_raked_mindwell_actv2/augmented_diaries.csv`, `seed=42`. 1,123,623 act30
moves. Row count/schema preserved exactly; hom30/wrk30 confirmed byte-identical
(`hom30_byte_identical: True`, `wrk30_byte_identical: True` in
`act30_rake_provenance.json`). Runtime ~1 min on this machine (68 GB RAM available; no memory
guard needed — full in-memory run was safe, confirmed before running by checking
`Get-CimInstance Win32_ComputerSystem` first).

**LFTAG pooling rate:** **2.8% of (CYCLE_YEAR, DDAY_STRATA, LFTAG) cells** pooled (1 of 36 —
2022×Sunday's LFTAG=2 cell, <30 obs diaries), and **2.2% of syn rows** (2,795/128,122, includes
the NaN-LFTAG extension) routed into a pooled group. Both well under the 50% manager-escalation
threshold (OD-I2) — no flag raised, design unchanged.

**04P before/after decomposition** (`3rdJ_04P_work_wrk30_discordance.py`, run once on each CSV —
work-activity slots, act30==1, OBS / SYN-pre / SYN-post):

| | AT-WORK (wrk=1) | TELEWORK (wrk=0,hom=1) | FLOATING (wrk=0,hom=0) | n_work |
|---|---|---|---|---|
| OBS | 82.58% | 14.46% | **2.96%** | 409,388 |
| SYN pre-04T (`R5_raked_mindwell`) | 49.76% | 26.30% | **23.94%** | 726,991 |
| SYN post-04T (`R5_raked_mindwell_actv2`) | 79.26% | 16.65% | **4.08%** | 432,746 |

TELEWORK is preserved (not zeroed) at a share close to observed (16.65% vs obs 14.46%); FLOATING
collapses from 23.94% to 4.08%, close to observed 2.96%.

**Full validator run** (`3rdJ_04_augmentationGSS_2split_val.py --step4_dir <dir>`, production
thresholds, run once against each of `R5_raked_mindwell` [baseline] and `R5_raked_mindwell_actv2`
[04T output] since no pre-existing baseline report existed to compare against):

| Gate | Pre-04T | Post-04T |
|---|---|---|
| **GA** FLOATING excess (Task-1 target) | **+20.98 pp FAIL** | **+1.12 pp PASS** |
| **GB** Transition-flicker | 1.000× PASS | 1.000× PASS (unchanged, not degraded) |
| G4 Transition-rate dev | 11.2% PASS | 8.4% PASS |
| G4 Night sleep-slot delta | 6.25 pp FAIL | 0.34 pp PASS |
| G4 Work peak-slot delta | 6.38 pp FAIL | 14.85 pp FAIL (pre-existing FAIL, see note below) |
| OW5 Day-type ordering | 61.4% FAIL (pre-existing, unrelated) | 61.4% FAIL (unchanged) |
| S8 KL(obs‖syn) 14-cat | 0.0370 | 0.0290 (improved, per Expected Result) |
| S8 Work-act-but-AT_WORK=0 | obs 17.4% / syn 50.2% | obs 17.4% / syn 20.7% |
| **Scorecard** | 64 PASS / 3 WARN / 4 FAIL | **66 PASS / 3 WARN / 2 FAIL** |

**Zero new FAIL, confirmed set-wise:** post-04T FAIL set `{G4 Work-peak, OW5}` ⊂ pre-04T FAIL set
`{GA, G4 Night, G4 Work-peak, OW5}`. GA (this task's target gate) and G4-Night both close; OW5 is
untouched (already documented pre-existing, act30-independent per `3rdJ_04_augmentationGSS.md`'s
"FAIL 2" entry). All Expected-Result bullets met: byte-identical hom/wrk, FLOATING ≤ obs+2.0pp
(Gate A PASS band, not just WARN), Work-act-but-AT_WORK=0 lands near observed+telework as specified,
KL improved, GB not degraded.

**Honest flag — G4 Work-peak-slot delta got numerically worse (6.38→14.85 pp), same FAIL status
both runs, root-caused, not a 04T defect:** `validate_temporal`'s `WORK_PEAK_SLOTS` check
(`3rdJ_04_augmentationGSS_2split_val.py:538-541`) pools ALL `CYCLE_YEAR` × ALL `DDAY_STRATA`
together UNCONDITIONALLY — unlike G2/OW1, which stratify. Measured directly: obs rows are 71%
weekday-weighted (45,638/64,061 stratum-1); syn rows are 86% weekend-weighted (109,699/128,122
strata 2+3) — a structural consequence of each respondent's 2 synthetic strata being the day-types
they were NOT diaried on (most GSS respondents are diaried on a weekday). Pre-04T, the FLOATING bug
inflated syn's raw Work-category share broadly (including on weekends), which *coincidentally*
offset this population-weighting mismatch (peak-slot work%: obs 28.72% vs syn 22.34%, gap 6.38pp).
04T correctly drives weekend Work-activity share down toward its true near-zero observed level
(syn peak-slot work% 22.34%→13.87%, obs unchanged 28.72%), which removes that accidental offset and
exposes the pre-existing DDAY-unconditional pooling confound in the gate's own definition (gap now
14.85pp). This is a gate-definition issue, not a 04T defect — flagged for the manager; Task 1 does
not alter validator gate definitions (out of scope).

**Spot-check** (20 random synthetic person-days, `random_state=99`, on `R5_raked_mindwell_actv2`):
4 FLOATING slots / 960 total (~0.4%, consistent with the probabilistic — not hard-locked — 4.08%
population rate), 1 TELEWORK slot observed directly (signal preserved), 16 isolated 1-slot act30
flickers vs **17** on the same 20 rows pre-04T (essentially unchanged, confirms the boundary
preference isn't introducing new chatter).

**Files:** `Step4_docs/3rdJ_04T_act_rake_2split.py`, `Step4_docs/3rdJ_04T_act_rake_2split_test.py`,
`Step4_docs/outputs_step4/sweep/R5_raked_mindwell_actv2/{augmented_diaries.csv,
act30_rake_provenance.json, step4_validation_report.{html,txt}}`,
`Step5_docs/3rdJ_05_censusLinkage_2split.py:44-47` (edited),
`Step5_docs/3rdJ_05_censusLinkage_2split.20260715_preFULLPOOLactv2.py` (archived predecessor),
`Step4_docs/3rdJ_04_augmentationGSS.md` (dated entry appended).

**Blockers:** none. `R5_raked_mindwell/` was never overwritten (new `_actv2` output dir throughout).
Step 5/6/7/8/9 re-run correctly deferred to Task 4 per the binding execution order.

---

### 2026-07-15 — Manager verification pass

Independently re-verified Tasks 1–3 against their underlying artifacts (documentation-accuracy pass; no pipeline code or data touched). Engineering in all three tasks is sound. Re-derived checks:

- `hom30_*` / `wrk30_*` byte-identical pre/post 04T — confirmed.
- 04P before/after table (line ~339 above) — exact to <0.03pp against independent re-derivation.
- Gate A: **+20.98pp FAIL → +1.12pp PASS** — confirmed.
- Scorecard: **64P/3W/4F → 66P/3W/2F**, with the post-04T FAIL set a strict subset of the pre-04T FAIL set — confirmed.
- Unit tests: **27/27** — confirmed.
- LFTAG pooling: **2.78% of cells** (1/36) **/ 2.18% of syn rows** (2,795/128,122) — confirmed (matches the employee's reported "2.8%"/"2.2%" to the underlying exact fractions).
- Task 2's executable code (loop structure, variable names, carrier-naming convention, fallback logic) — **byte-identical to 2J's fixed block** — confirmed.
- Task 2's zone-count restoration ratios — **MidRise 25×, HighRise 27×, DetachedHouse 1.0×** — confirmed directly against the actual IDF zone structures (independent zone counts, not reused from the employee's script).

Four documentation-accuracy corrections applied in place above (not re-investigated further here; see each correction note for detail):
1. The 61.12% pre-04T discordance figure (§0.3, §Task-1 "Current state", §Task-1 "Expected result") is stale/non-representative — measured on a disjoint 2,560-row Jun-18 diagnostic sample, not the 128,122-syn-row R5 sweep the pipeline uses; `R5_raked/` does not exist in the repo. Correct pre-04T baseline on the real pool (`R5_raked_mindwell/`) is **50.24%** (26.30% TELEWORK + 23.94% FLOATING) — consistent with the Task-1 Progress Log's own SYN pre-04T row.
2. Task 2's diff bookkeeping ("4 hunks / 56 diff lines") corrected to **5 hunks / 20 changed lines (10 removed, 10 added), 7 distinct change locations at zero context — 5 mojibake em-dash artifacts, 2 intentional narrative rewrites.** The load-bearing conclusion (zero diffs touch executable lines) was already correct and stands.
3. The plan's own Task-2 step 3 and §0.1 wrongly cited a stale "144,507 SIM_HH_IDs" comment at `integration.py:17` — no such comment ever existed there (line 17 is `TARGET_WORKING_PROFILE = [`); the real stale comment was only in `main.py:74-75`, correctly fixed. Annotated in place so nobody hunts for it again.
4. Task 3's 32.55% 2005 figure is a **per-cycle row-composition share** (the four cycle shares sum to 100%), not a matched-rate — **not comparable to 2J's ~15.76% matched-rate figure.** The valid evidence against a 2005 linkage collapse is the ratio column (2005 = 1.08 vs 0.94–1.00 for other cycles), which stands unchanged.

**Two additional findings for the manager/paper record, out of scope for this plan:**

- **G4 "Work peak-slot delta" is a pre-existing validator-gate defect, not a 04T regression.** `Step4_docs/3rdJ_04_augmentationGSS_2split_val.py:538-541` (`WORK_PEAK_SLOTS` check) uses `self.obs`/`self.syn` pooled across **all** `DDAY_STRATA` (pooling set up at `:258-262`), with no stratification — unlike `G2`/`OW1`, which do stratify. SYN row composition is 14.4% weekday / 85.6% weekend vs OBS 71.2% / 28.8% weekday/weekend. Per-stratum, 04T *improves* the fit sharply (weekday 14.5pp→0.3pp, Saturday 8.0pp→0.02pp, Sunday 7.0pp→0.00pp), and the argmax peak slot is identical pre/post in every stratum (14/15/20), matching observed exactly. The **pooled** delta worsens (6.38pp→14.85pp) purely from composition-weighting — a Simpson's-paradox artifact of the gate's own unconditional pooling, not a defect introduced by 04T (consistent with the "Honest flag" already logged in the Task-1 entry above). Recommend logging this as a separate validator-gate fix candidate. **Explicitly out of scope for this plan** — Task 1 correctly did not alter validator gate definitions.
- The `R5_raked/` directory referenced in the plan's Task-1 design (§Current state, line ~69) does not exist in the repo; the 04L output is not persisted separately from the 04M-smoothed pool (`R5_raked_mindwell/` is the earliest persisted stage). This is consistent with, and is part of the evidence for, correction 1 above.

**Files touched by this pass:** only this document (`3J_docs_occ_nTemp/Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md`) — annotated in place at the four locations above plus this closing entry. No pipeline code, no pipeline data, no other doc modified.

---

### 2026-07-15 — Task 4 step 2 (Step 5 re-run)

**Scope:** Step 5 census linkage re-run on the actv2 pool + its validator only. Steps 6/7/8/9 explicitly NOT run (out of scope). All local — no cluster.

**Archive (mandatory, done first):** `Step5_docs/outputs_step5/` (19 files, 392 MB) copied to `Step5_docs/outputs_step5.20260715_pre_actv2/` before running anything. Verified: 19 files both sides, identical file list, byte-identical per-file sizes (`stat -c "%n %s"` diff empty). Disk had 23 GB free (of 1.9 TB) — ample headroom, no space blocker.

**Run:** `Step5_docs/3rdJ_05_censusLinkage_2split.py` — confirmed `FULL_POOL` already repointed to `R5_raked_mindwell_actv2/augmented_diaries.csv` (`3rdJ_05_censusLinkage_2split.py:44-47`, done by Task 1) and `CENSUS_FILE` = `0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv` exists (3.9 MB, unchanged). Memory guard: this run is the same 192,183-row/545 MB pool size as the predecessor `R5_raked_mindwell/` (Task 1 confirmed only `act30_*` differs, `hom30`/`wrk30` byte-identical) — i.e. identical memory footprint to a run that already succeeded without incident. Machine has 63.5 GB RAM, 32.2 GB free at launch — no chunking/guard needed. Ran all 5 substeps in the documented order (`3rdJ_05_censusLinkage_2split.md:108`) via a background PowerShell wrapper (`run_step5_full_20260715.ps1`, log `run_step5_full_20260715.log`): `--full → --aggregate → --bem → --exclusion → --regression`, all exit=0. **Elapsed: ~75 seconds total** (19:34:16.88 → 19:35:31.63), well under any timeout concern.

**Validator:** `Step5_docs/3rdJ_05_censusLinkage_2split_val.py` (no `--excl`, matching the only historically-produced report format, `3rdJ_step5_validation_report.html`) — exit 0, log `run_val_20260715.log`.

**Scorecard: 22 PASS / 1 WARN / 1 FAIL.**

This exactly reproduces the memory-logged "RESOLVED 2026-06-23 (22/1/1)" baseline (`project_step5_2split_status.md`). Note the task brief's stated baseline "20P/1W, zero FAIL required" (drawn from `3rdJ_05_censusLinkage_2split_val.md:377`, "20 PASS/1 WARN/3 FAIL") does **not** match either the memory-logged resolved status or this run's result — flagging this discrepancy for the manager rather than deciding which historical figure is authoritative. The 1 FAIL present here is **Section 2.2** (AT_HOME per-slot max deviation, within-day-type: 3.72pp, gate ±3pp, 5 slots over), which the validator's own INFO-level annotations mark as driven by day-type composition, not act30/hom30 content — it is unrelated to Task 1's act30 rake (hom30/wrk30 confirmed byte-identical through the entire linkage, see below) and is not a new regression.

Full section-by-section (`run_val_20260715.log:15-76`):
| Section | Result |
|---|---|
| 1 Match Tier Distribution | 6/6 PASS (incl. §1.4 below) |
| 2 AT_HOME Consistency | 5 PASS, 1 FAIL (2.2, 3.72pp) |
| 3 AT_WORK Consistency | 4/4 PASS |
| 4 Schedule Shape Plausibility | 3/3 PASS |
| 5 HH Aggregation Integrity | 3 PASS, 1 WARN (5.2, mean N_HH_MEMBERS 1.500 vs Census ref ~2.80) |
| 6 BEM Output Format | 3/3 PASS |

**§1.4 tier proportions** (`Step5_docs/outputs_step5/3rdJ_25CEN_aug_Matched_Keys.csv`, 30,273 rows):
| Tier | n | % |
|---|---|---|
| 1_Perfect | 0 | 0.00% |
| 2_Core | 30,193 | 99.74% |
| 3_Constraints | 80 | 0.26% |
| 4_FailSafe | 0 | 0.00% |

Gate (`>=60%` Tier1+2) → PASS at 99.74%. Identical to the archived pre-actv2 `Matched_Keys.csv` tier breakdown (re-checked directly, same counts) — expected, since `MATCH_KEYS`/`DDAY_COL` never include `act30`.

**Per-cycle matched share, including 2005** (probe `Step5_docs/_2005_matchshare_probe_actv2.py`, same definition as Task 3's `_2005_matchshare_probe.py` — row-composition share, sums to 100% across cycles, not a matched-rate):
| CYCLE_YEAR | pool_share_% (actv2 pool) | matched_share_% | ratio |
|---|---|---|---|
| 2005 | 30.00 | 32.55 | 1.08 |
| 2010 | 23.59 | 23.66 | 1.00 |
| 2015 | 27.15 | 25.65 | 0.95 |
| 2022 | 19.26 | 18.13 | 0.94 |

**Identical to Task 3's reference table to 2 decimal places, including the 2005 ratio (1.08).** Expected: `CYCLE_YEAR` is a non-`act30` column, so pool composition and match assignment are unaffected by Task 1's rake.

**Row counts vs. archived pre-actv2 (`outputs_step5.20260715_pre_actv2/`):**
| File | Archived (pre-actv2) | New (actv2) | Δ |
|---|---|---|---|
| `3rdJ_25CEN_aug_Full_Schedules.csv` | 30,273 rows | 30,273 rows | 0 |
| `3rdJ_25CEN_aug_Matched_Keys.csv` | 30,273 rows | 30,273 rows | 0 |
| `3rdJ_25CEN_aug_BEM_Schedules.csv` | 30,273 rows | 30,273 rows | 0 |
| `3rdJ_25CEN_aug_Full_Aggregated.csv` | 30,273 rows | 30,273 rows | 0 |
| `3rdJ_25CEN_aug_excluded_pids.csv` | 674 rows | 735 rows | **+61** |
| `3rdJ_25CEN_aug_Full_Schedules_excl.csv` | 29,599 rows | 29,538 rows | **−61** |
| `3rdJ_25CEN_aug_Full_Aggregated_excl.csv` | 29,599 rows | 29,538 rows | **−61** |
| `3rdJ_25CEN_aug_BEM_Schedules_excl.csv` | 29,599 rows | 29,538 rows | **−61** |

The core linkage frame (30,273 agents, 23,882 unique `SIM_HH_ID`) is **exactly stable** — confirmed the census-agent (`PID`) set and household (`SIM_HH_ID`) set are set-identical between old and new `Full_Aggregated.csv`, and every individual per-agent `hom30_*`/`wrk30_*` value in `Full_Schedules.csv` (the pre-aggregation linkage output) is byte-identical between old and new runs (0/30,273 differ on either channel), with identical `occID`/`DDAY_STRATA` per `PID` too. **No red flag on the linkage frame itself.**

The `_excl` row-count delta (+61 excluded / −61 remaining, 0.2% of 30,273) was investigated to ground truth rather than left unexplained, because it initially looked like it might indicate an `act30`-driven side effect on the AT_HOME vacancy-exclusion gate (`run_exclusion`, `3rdJ_05_censusLinkage_2split.py:891-944`, threshold on `HH_hom30_*` mean < 0.30 — a `hom30`-only computation that should be untouched by `act30`). Root-caused as follows:
- The **archived** `outputs_step5.20260715_pre_actv2/3rdJ_25CEN_aug_Full_Aggregated.csv` is **internally inconsistent with its own** `3rdJ_25CEN_aug_Full_Schedules.csv` in that same archived snapshot: comparing individual `hom30_*` between the two archived files (joined on `PID`) shows **13,233/30,273 rows (43.7%) disagree** — i.e. the archived `Full_Aggregated.csv` was not regenerated from the archived `Full_Schedules.csv` currently sitting beside it (consistent with the multiple partial `run_full_2026-06-23*.log`/`run_full_2026-06-23_colmask.log` variants on disk, suggesting `--full` was re-run at some point after `--aggregate`/`--exclusion` without re-running the downstream sub-steps).
- Recomputing the HH-level aggregate correctly (`groupby('SIM_HH_ID')[hom_cols].max()`) directly from the **archived** `Full_Schedules.csv` (which IS confirmed byte-identical to today's new `Full_Schedules.csv`) gives an exclusion count of **735** — exactly matching today's fresh run, not the archived (stale) 674.
- Today's fresh run has zero such inconsistency: `Full_Schedules.csv` vs `Full_Aggregated.csv` `hom30_*` agree on 30,273/30,273 rows (checked the same way).
- **Conclusion: the true, correctly-computed exclusion count (735) is unchanged by the `act30` rake — it is fully determined by `hom30`, which is byte-identical pre/post. The −61/+61 `_excl` delta is an artifact of a stale archived reference file, not a regression from today's work.** Flagging this because the archived directory (`outputs_step5.20260715_pre_actv2/`) should not be treated as a reliable ground truth for `_excl`-file row counts in any future comparison — its `Full_Aggregated*`/`*_excl` files predate a `Full_Schedules.csv` refresh that was never propagated through the rest of the pipeline on 2026-06-23.

**Files:** `Step5_docs/outputs_step5.20260715_pre_actv2/` (archive, 19 files/392MB), `Step5_docs/outputs_step5/*` (fresh Task-4 outputs), `Step5_docs/run_step5_full_20260715.ps1` + `run_step5_full_20260715.log` (run wrapper/log), `Step5_docs/run_val_20260715.log` (validator log), `Step5_docs/_2005_matchshare_probe_actv2.py` (new read-only probe, mirrors Task 3's script).

**Blockers:** none — run completed cleanly, frame stable, zero net regression from Task 1's act30 change at the Step-5 linkage level. **Flagged for manager attention (not decided unilaterally):** (1) the task's stated "20P/1W, 0 FAIL" baseline does not match either the memory-logged 22/1/1 resolved status or this run's reproduced 22/1/1 result — which figure is authoritative should be reconciled; (2) the archived `outputs_step5.20260715_pre_actv2/` directory has a pre-existing internal staleness (Full_Aggregated vs Full_Schedules mismatch, unrelated to today's work) that should be kept in mind if it's ever used as a reference again. Per task scope, Steps 6/7/8/9 were NOT run.

---

### 2026-07-15 — Task 4 step 3 + step 3b (Step 6 re-run + FLOATING gate) — DONE, all local

**Scope:** Step 6 (forecast calibration only) + the step-3b 2030 FLOATING gate. Steps 7/8/9 explicitly NOT run. All local — no cluster, no sbatch.

**Read first:** `Step6_docs/3rdJ_06_longitudinalForecasting_2split.py` (full), `Step6_docs/3rdJ_06_longitudinalForecasting_2split.md`, `Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py` (full), `Step6_docs/calibrate_weekday_work_2split.py`, `Step6_docs/3rdJ_06_control_telework_2split.py`.

**Pipeline-shape finding (governs what was and wasn't re-run):** Step 6's model training/forecast stages (A/B/C/D1/D2 in `3rdJ_06_longitudinalForecasting_2split.py`) read **only** `Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv` (the RAW, pre-04L/04M/04T pool — OD-1, `.md:45-50`, confirmed live at `.py:2177-2183`), never `R5_raked_mindwell` or `R5_raked_mindwell_actv2`. Calibration-B (`calibrate_weekday_work_2split.py`) likewise reads only the raw R5_lr1e4 pool + the model's own deliverable. **Task 1's act30 rake therefore does not touch the base forecast or Calibration-B at all** — confirmed on disk: `2030_synthetic_diaries_2split.csv`, the three per-band raw/mindwell files, `DRIFT_MATRIX_*`, `reconstructed_2022_diaries_2split.csv`, and `2030_synthetic_diaries_2split_calibrated_mindwell.csv` (Calibration-B's mindwell output = Calibration-C's Input A) all carry their original **Jun 24 / Jun 26 17:21** timestamps, untouched today — verified, not re-run, because nothing upstream of them changed.
The **only** Step-6 stage whose input changed is **Calibration-C** (`3rdJ_06_calibrate_C_activity_weekend_2split.py`), whose **Input B is `Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv`** — the file the prior Progress Log entry (Task 4 step 2) just regenerated on the actv2 lineage. This is the one link between today's upstream fixes and Step 6's deliverable.

**Archive (mandatory, done first):** `Step6_docs/outputs_step6/` (17 files, 267 MB) copied to `Step6_docs/outputs_step6.20260715_pre_actv2/` before running anything. Verified: identical file list + identical per-file sizes (`ls -la` diff on name+size, empty). Disk had 22 GB free (of 1.9 TB) before and after — no space blocker.

**Run 1 — Calibration-C, fresh (`Step6_docs/run_calibC_20260715.log`):** `py -3 3rdJ_06_calibrate_C_activity_weekend_2split.py` (no args; paths are script-relative constants). Input A unchanged (`2030_synthetic_diaries_2split_calibrated_mindwell.csv`, 111,024 rows). Input B = fresh `Full_Aggregated_excl.csv` (29,538 rows, matches Task-4-step-2's reported count exactly). Stage 0 (weekend wrk30 cap), Stage 1 (weekend hom30 restore + 04M smoother), Stage 2 (act30 conditional donor-resample, 144/144 cells, 0 fallback) all ran clean; wrk30 integrity assert passed after Stage 1 and Stage 2 (`[OK] wrk30 untouched`). Wrote `outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv`, 111,024 rows (script's own atomic-write backup: `..._C_BAK_2026-07-15.csv`, 70,541,063 bytes — matches the pre-run file's size exactly, confirming the auto-backup is faithful).

**Root-caused the one WARN status-flip (Check [1], Sleep share) against the archived predecessor, per instructions — proved, not asserted:**
Reran Calibration-C a second time with Input B swapped to the archived pre-actv2 Step-5 file (`Step5_docs/outputs_step5.20260715_pre_actv2/3rdJ_25CEN_aug_Full_Aggregated_excl.csv`, 29,599 rows) via a scratch replay copy of the script (output redirected to a scratch path, `outputs_step6/` untouched by this replay run) — log `Step6_docs/_replay_calibC_preactv2_20260715.log`. Direct comparison:

| Check | pre-actv2 replay (old Input B, 29,599 rows) | today's fresh run (new Input B, 29,538 rows) | status |
|---|---|---|---|
| [1] Sleep (code 5) share | 0.2278 → **0.3540** `[PASS]` (band 0.33–0.36) | 0.2278 → **0.3660** `[WARN]` | **NEW — flipped PASS→WARN** |
| [2] WD Metabolic proxy (3 bands) | 127.3/126.8/126.9 → 109.9/109.9/109.9 `[PASS]`×3 | 127.3/126.8/126.9 → 108.9/109.0/109.0 `[PASS]`×3 | unchanged, both PASS |
| [3] WE daytime (11–26) hom30 | 0.4358 → **0.5148** `[WARN]` (band 0.52–0.57, target obs Sat=0.5239/Sun=0.5588) | 0.4358 → **0.4884** `[WARN]` (target obs Sat=0.4912/Sun=0.5301) | **pre-existing — WARN both times** |
| [4] WD hom30 ordering (C4 gate — see below) | 0.3844 < 0.4314 < 0.4576 `[PASS]`, delta=0 for all bands both runs | identical (weekday hom30 is untouched by Calibration-C, both runs) | unchanged, both PASS |

Root cause of the [1] flip, independently re-derived (not from the log — direct column computation on both `Full_Aggregated_excl.csv` files): sleep-code(5) share of Input B itself moved from **34.64%** (old, pre-actv2) to **35.71%** (new, actv2) and work-code(1) share dropped **23.96%→21.45%** — i.e. the 2022-observed donor pool that Stage 2 resamples act30 from is itself less "Work"-inflated post-04T (consistent with Task 1's own FLOATING-rate fix: less spurious Work-activity coding survives into the census-linked pool), which pulls Stage 2's 2030 draws toward more Sleep and less Work. **This is the expected downstream shape-shift from Task 1's act30 fix (the plan's own "activity-shape shifts ⇒ Task 1" attribution rule), not a new defect.** It is a genuine WARN (36.60% vs the 33–36% band, 0.6pp over the upper edge) — flagged honestly rather than waved off, but out of this task's scope to correct (Step 6 + 3b gate only; not decided unilaterally).

**Step-6 reconstructed scorecard** (Step 6 has **no** standalone validator `.py` — `3rdJ_06_longitudinalForecasting_2split_val.py` referenced in the doc's checklist at `.md:32` does not exist on disk, checklist item unticked; the "validator" is the set of embedded PASS/WARN/GATE-FAIL checks inside the pipeline scripts themselves, reconstructed here):

| Check | Value | Status | Pre-existing? |
|---|---|---|---|
| Calibration-C [1] Sleep share | 36.60% (band 33–36%) | WARN | **NO — new, root-caused above** |
| Calibration-C [2] Metabolic proxy ×3 bands | 108.9/109.0/109.0 W (band 108–112) | PASS ×3 | — |
| Calibration-C [3] WE daytime hom30 | 0.4884 (band 0.52–0.57) | WARN | YES — confirmed via replay, WARN under old Input B too |
| **Calibration-C [4] = C4 WFH gate** | conservative 0.3844 < hybrid 0.4314 < fullyhybrid 0.4576 | **PASS** | unchanged (hom30 untouched by both Calib-C and 04T) |
| Step-3b Gate A (FLOATING), before 04T | see below | exceeds PASS band | new measurement (2030 is a new file) |
| Step-3b Gate A (FLOATING), after 04T | see below | **PASS** | new measurement |
| wrk30/hom30 integrity asserts (Calib-C Stage 1/2) | — | PASS | — |
| Row-count integrity (111,024 in/out) | — | PASS | — |

**Scorecard tally: 5 PASS / 2 WARN / 0 FAIL.** Zero FAIL. Both WARNs are on Calibration-C's own internal checks, not on the gates this task was asked to watch (C4 / Gate A), which are both PASS.

**C4 WFH gate (the one this task specifically asked to watch): PASS.** `conservative=0.3844 < hybrid=0.4314 < fullyhybrid=0.4576`, monotone ordering holds, delta=+0.0000 for all three bands relative to Input A (expected — Calibration-C's Stages 0–2 never touch weekday hom30, only weekend hom30/wrk30 and all-strata act30). Re-verified directly on the FINAL (post-04T) file below — identical values, since 04T also never touches hom30.

---

**Step-3b gate — mandatory, run as directed:**

`3rdJ_04P_work_wrk30_discordance.py` run directly on the fresh 2030 `_C` file (log `Step6_docs/_04P_2030_C_20260715.log`): the file has `IS_SYNTHETIC==1` uniformly (all 111,024 rows) and `CYCLE_YEAR==2030` uniformly (no 2005–2022 rows), so 04P's own `[OBS]` panel is empty (`n=0 no work slots`) by construction — a 2030 forecast has no observed 2030 anchor. **SYN (2030, pre-04T):** AT-WORK 66.66%, TELEWORK 28.37%, **FLOATING 4.97%** (n_work=738,698).

For the "obs" side of Gate A, computed the 2022-observed decomposition three ways directly from the fresh `Full_Aggregated_excl.csv` (root-caused, not guessed) to bound the answer regardless of which "observed" reference is deemed authoritative:

| obs definition | n_work | AT-WORK | TELEWORK | FLOATING | Gate-A excess (syn 4.97% − this) |
|---|---|---|---|---|---|
| strict 2022 (IS_SYNTHETIC==0, CYCLE_YEAR==2022), n=2,946 | 35,976 | 69.15% | 29.76% | 1.08% | **+3.89pp** |
| Calibration-C's own "obs22" pool (ALL rows/cycles, as literally coded in the script), n=29,538 | 304,179 | 82.63% | 15.01% | 2.35% | **+2.62pp** |
| Task-1's established pooled-cycle obs (R5_raked_mindwell_actv2, IS_SYNTHETIC==0, all cycles 2005–2022), n=192,183-pool | — | 82.58% | 14.46% | 2.96% | **+2.01pp** |

**Every candidate obs definition puts the excess above the `GATE_A_PASS_PP=2.0` PASS band** (range +2.01pp to +3.89pp; none reach the +5.0pp WARN→FAIL line). Per OD-I4 ("apply 04T... only if FLOATING exceeds the [PASS] band"): **04T was applied.**

**04T could not be run directly on the 2030 file** (`3rdJ_04T_act_rake_2split.py`'s `main()` assumes obs+syn coexist in one CSV for the same `CYCLE_YEAR`; its outer loop is `for cy in CYCLES` with `CYCLES=[2005,2010,2015,2022]` — a 2030-only, all-`IS_SYNTHETIC==1` file would match zero cells and silently move 0 rows). Built a wrapper, `Step6_docs/3rdJ_06_forecast_rake_2split.py` (analogue of 2J's `06_forecast_rake.py`), that **imports 04T's own tested functions unmodified** (`_run_act30_conditional_rake`, `_measure_work_state`) rather than re-implementing them: it relabels a copy of the 2030 rows to `CYCLE_YEAR=2022` (so they land in 04T's real 2022 cell grid), concatenates with the canonical 2022-observed rows (`Step4_docs/outputs_step4/sweep/R5_raked_mindwell_actv2/augmented_diaries.csv`, `IS_SYNTHETIC==0 & CYCLE_YEAR==2022`, n=12,336 — the same GSS-2022-diarist pool Task 1 itself validated against; 04T never mutates obs rows so these are the untouched originals), runs 04T's rake, then extracts the (relabeled-back) 2030 rows. Log: `Step6_docs/run_forecast_rake_20260715.log`.

**Before/after (04P-style decomposition, from the wrapper's own log, cross-checked by re-running `3rdJ_04P_work_wrk30_discordance.py` directly on the written output — `Step6_docs/_04P_2030_C_post04T_20260715.log` — both agree exactly):**

| | AT-WORK | TELEWORK | FLOATING | n_work |
|---|---|---|---|---|
| OBS (2022, R5_raked_mindwell_actv2, n=12,336) | 72.78% | 25.79% | **1.44%** | 77,219 |
| SYN 2030, before 04T | 66.66% | 28.37% | **4.97%** | 738,698 |
| SYN 2030, after 04T | 82.84% | 15.16% | **2.00%** | 586,471 |

**Gate-A excess: before = 4.97 − 1.44 = +3.53pp (exceeds the 2.0pp PASS band) → after = 2.00 − 1.44 = +0.56pp (PASS, ≤2.0pp).** LFTAG pooling: 11.1% of cells (1/9 — the 2022×Sunday×LFTAG=2 cell, same thin cell Task 1 found), 4.6% of syn rows (5,052/111,024) — both well under the 50% OD-I2 escalation threshold, no flag raised. Total act30 moves: 662,604 (of 5,329,152 2030 act30 cells, 12.4%).

**hom30/wrk30 not mutated — verified three independent ways, all PASS:** (1) 04T's own internal guardrail inside `_run_act30_conditional_rake`'s caller in the wrapper: `np.array_equal` on the full combined (obs+2030) frame's hom30/wrk30 before vs after — `True`/`True`. (2) A second, row-count-preserving check restricted to just the 2030 slice (before-rake copy vs after-rake extracted rows) — `True`/`True`. (3) Direct recomputation of the C4 WFH-ordering values on the FINAL post-04T file (`conservative=0.3844, hybrid=0.4314, fullyhybrid=0.4576`) — bit-for-bit identical to Calibration-C's own pre-04T-rake values, which is only possible if weekday hom30 (which drives that check) was untouched.

**Sleep-share [1] WARN after 04T:** re-measured on the FINAL file directly — 36.618% vs 36.599% before the rake (negligible +0.02pp shift; 04T only touches the ~12% of 2030 act30 cells involved in a FLOATING/TELEWORK/AT-WORK state realignment, most of which are not sleep-adjacent). Still WARN, same root cause as above (Calibration-C's Stage-2 donor pool, not 04T) — not re-investigated further, out of scope.

**Row counts / population size, `_C` output vs archived predecessor:**

| | Archived (`outputs_step6.20260715_pre_actv2/..._C.csv`) | Final (today, post-Calib-C + post-04T) | Δ |
|---|---|---|---|
| Rows | 111,024 | 111,024 | 0 |
| BAND breakdown | 37,008 × 3 | 37,008 × 3 | 0 |
| DDAY_STRATA breakdown | 37,008 × 3 (strata 1/2/3) | 37,008 × 3 | 0 |
| CYCLE_YEAR | {2030} only | {2030} only | — |

**No `SIM_HH_ID`/`PID`/agent-ID column exists in the 2030 diary file** (confirmed by full column-name scan, 156 cols, zero ID-shaped names) — the Step-6 2030 deliverable is a flat synthetic-diary population with no persistent household/person identity (that linkage is a Step-7/8 concept, not present pre-Step-7); row count (one row = one synthetic person-diary) is the only population-size metric available at this stage, and it is exactly preserved.

**Files:**
- `Step6_docs/outputs_step6.20260715_pre_actv2/` (archive, 17 files/267MB, verified).
- `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` — **final deliverable** (post-Calibration-C, post-04T-forecast-rake), 111,024 rows, 70,682,794 bytes.
- `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.preRake_actv2_20260715.csv` — intermediate snapshot (post-Calibration-C, pre-04T), kept for traceability of the two-stage change.
- `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C_BAK_2026-07-15.csv` — Calibration-C's own auto-backup of the original Jun-26 file (script-native behaviour, redundant with but consistent with the mandatory archive above).
- `Step6_docs/3rdJ_06_forecast_rake_2split.py` — new wrapper script (2030 forecast-year 04T application; imports and reuses 04T's own functions, does not duplicate their logic).
- `Step6_docs/run_calibC_20260715.log`, `Step6_docs/_replay_calibC_preactv2_20260715.log`, `Step6_docs/run_forecast_rake_20260715.log`, `Step6_docs/_04P_2030_C_20260715.log`, `Step6_docs/_04P_2030_C_post04T_20260715.log`.

**Blockers:** none. Local only — no cluster, no sbatch, `torch`/GPU stages not touched (Step 6's trained checkpoints and raw-pool base forecast are unaffected by today's upstream changes and were correctly NOT re-run). **Flagged for manager attention (not decided unilaterally, informational only):** Calibration-C's Check [1] (Sleep share) moved from PASS (35.40%) to WARN (36.60%, 0.6pp over the upper band edge) as a direct, root-caused, expected consequence of Task 1's act30 fix propagating through the Step-5 refresh — real signal, not a bug, but worth watching in Step 7/8's downstream validators since it changes the 2030 activity-code composition slightly. Per task scope, Steps 7/8/9 were NOT run.

---

### 2026-07-15 — Task 4 step 4 (Step 7 re-run: BEM integration, both years) — DONE, all local

**Scope:** Step 7 (residential REPLACE + office MODULATE conversion) for 2022 and 2030, on today's freshly-regenerated Step-5 (`_excl`, 29,538 rows / 23,150 HH) and Step-6 (`_C` deliverable, post-Calibration-C + post-04T-forecast-rake) outputs. Step 8/9 explicitly NOT run.

**Read first:** `Step7_docs/3rdJ_07_bemIntegration_2split.md` (full), `Step7_docs/3rdJ_07_aug_to_bem_2split.py` (full), `Step7_docs/3rdJ_07_bemIntegration_2split_val.md`.

**Archive (mandatory, done first):** `Step7_docs/outputs_step7/` (23 files, 795 MB) copied to `Step7_docs/outputs_step7.20260715_pre_actv2/`. Verified via `diff` on `ls -la` name+size listing of both dirs — empty diff, confirmed identical.

**Deliverable-path decision (not a new decision, just recording it):** the producer script's default `D2030` constant points at the Jun-26 `2030_synthetic_diaries_2split_calibrated_mindwell.csv` (pre-Calibration-C/pre-04T). Per the cascade table (row 4: "Step-6 `_C` → BEM_Schedules") and per the prior Progress Log entry's own final deliverable, ran `--year 2030` with `--deliverable ../Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (the post-Calibration-C + post-04T-forecast-rake file, 111,024 rows, confirmed via `--audit` first: `[2] 2030 deliverable` schema check ran against the *default* path only — audit is schema-only and tolerant of the override, the real run used `--deliverable` explicitly).

**Runs (in order):** `py -3 3rdJ_07_aug_to_bem_2split.py --audit` (log `run_audit_20260715.log`) → `--year 2022` (log `run_year2022_20260715.log`) → `--year 2030 --deliverable <...>_C.csv` (log `run_year2030_20260715.log`) → `py -3 3rdJ_07_bemIntegration_2split_val.py` (log `run_val_20260715.log`). RAM checked before running (34 GB free of 66 GB total) — no memory guard needed, all runs completed in-memory without incident. Disk: 21 GB free of 1.9 TB before and after (99% full but stable; no space blocker, verified `df -h` post-run).

**Audit confirmed the frame note is live in the actual input:** 2022 stock = **29,538 rows / 23,150 unique `SIM_HH_ID`** (matches Step-5's reported `_excl` count exactly, not 23,211/29,599). act30/hom30/wrk30: 0 NaN, 48 cols each, present. 2030 deliverable (default path, schema check only): 111,024 rows, 3 bands, wrk30 present, 0 NaN.

**Validator scorecards (both zero FAIL, re-derived from the printed section tables, not just the summary line):**

| Year | PASS | WARN | FAIL |
|---|---|---|---|
| 2022 | 32 | 0 | 0 |
| 2030 | 43 | 0 | 0 |

**Baseline-figure discrepancy — flagged, not resolved unilaterally (same pattern as the Step-5/Step-6 entries above):** this task's Aim line (governing doc, "current baselines to beat/match") states *"Step 7 val 2022 34/0/0 & 2030 33/0/0 style"*. The actual documented baseline inside `3rdJ_07_bemIntegration_2split.md`'s own Progress Log (2026-06-26, "Fix bundle A/B/C" entry) and the `_val.md` companion doc's own Progress Log both say **2022 = 32 PASS / 0 WARN / 0 FAIL; 2030 = 43 PASS / 0 WARN / 0 FAIL** — which is exactly what today's fresh run reproduced. Verified by counting the printed `[PASS]` lines per section directly in `run_val_20260715.log` (not the validator's own summary line): **2022** — A=9, B=3, C=4, D=4, E=5, F=2, G=5 → sum **32**; **2030** — A=9, B=3, C=11, D=4, E=8, F=3, G=5 → sum **43**. Both match the validator's own printed "Validation complete: N PASS" totals exactly, and both match the June-26 documented baseline gate-for-gate (same section letters, same per-section counts). The "34/33" figure in the governing doc does not match either the memory-logged status or this run's independently re-counted result. **Not deciding which figure is authoritative — flagging for the manager**, exactly as the prior Task-4-step-2 employee did for Step 5's analogous "20P/1W" vs "22/1/1" mismatch. **Zero FAIL either way — the task's actual pass/fail gate is met regardless of which PASS-count baseline is correct.**

**Row count + `SIM_HH_ID` nunique, every output CSV vs its archived predecessor (independently re-derived via a standalone pandas script, not read from the validator's own printout):**

| File | Archived (pre-actv2) rows | Archived nunique HH | New (actv2) rows | New nunique HH | Row Δ | HH Δ |
|---|---|---|---|---|---|---|
| `BEM_Schedules_2split_2022.csv` | 1,114,128 | 23,211 | 1,111,200 | 23,150 | −2,928 | **−61** |
| `BEM_Schedules_2split_2030_conservative.csv` | 1,114,128 | 23,211 | 1,111,200 | 23,150 | −2,928 | −61 |
| `BEM_Schedules_2split_2030_hybrid.csv` | 1,114,128 | 23,211 | 1,111,200 | 23,150 | −2,928 | −61 |
| `BEM_Schedules_2split_2030_fullyhybrid.csv` | 1,114,128 | 23,211 | 1,111,200 | 23,150 | −2,928 | −61 |
| `office_presence_multiplier_2022.csv` | 144 | n/a (aggregate table) | 144 | n/a | 0 | — |
| `office_presence_multiplier_2030.csv` | 432 | n/a (aggregate table) | 432 | n/a | 0 | — |

**All four residential files: exactly 23,150 × 2 day-types × 24 h = 1,111,200 rows, matching the task brief's expected arithmetic exactly (not 23,211).** This is the **CORRECT, expected** figure per the task brief's frame note — the June `outputs_step7` (and its `outputs_step7.20260715_pre_actv2` archive copy) inherited the 23,211/29,599 figure from Step 5's own pre-actv2 staleness (documented in the Task-4-step-2 Progress Log entry above: June's `Full_Aggregated.csv` was internally inconsistent with its own `Full_Schedules.csv`, so 61 households that should have been excluded were not). **Did not "fix" 23,150 back to 23,211 — confirmed this is the true count by cross-checking against Step-5's fresh `_excl` row count (29,538) and Step-6's `_C` assemble_2030() log line ("stock 29,538 rows"), both of which agree with today's Step-7 input read exactly.** Office multiplier files are population-aggregate tables (no `SIM_HH_ID` column, one row per archetype×band×day-type×hour cell) — their row counts (144 for 2022's single band, 432 for 2030's 3 bands) are structurally independent of N_HH and correctly unchanged.

**Column count/schema vs predecessor:** all 4 residential files stayed **13 columns**, byte-identical column list and order to the archived predecessor (`SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate`) — confirmed via direct `list(df.columns)` comparison, `same_columns=True` for every file. Both office files stayed **7 columns**, also unchanged (`office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction, multiplier, n_persons`). **Note on the task brief's "should stay 17-col unless the doc says otherwise" instruction:** checked the doc — `3rdJ_07_bemIntegration_2split.md`'s own `OUT_COLS` (script `:69-73`) and its "Output Format / Product 1" table (`.md:181-193`) both specify a **13-column** residential schema by design, explicitly *excluding* the Step-9 equipment/lighting columns (`OD-7D — Step-9 activity loads kept SEPARATE. LOCKED (default)`, `.md:335-337`) that were folded into 2J's own step-7 output at some later point (the "17-col" figure appears to be a 2J-lineage number, not applicable here — 3J Leg-2's Step 7 was never designed to carry those columns). 13-col is therefore the doc-correct, unchanged schema; not a regression or a deviation.

**MET / Metabolic_Rate shape characterisation (act30 now feeds `MET` at `3rdJ_07_aug_to_bem_2split.py:79,138` — visible changes expected, characterised not treated as a regression):**

2022 residential, Weekday, hourly mean `Metabolic_Rate`, new (actv2) vs archived (pre-actv2), independently recomputed by grouping the raw CSVs on `Hour`:

| Hour (post +4h roll, real clock) | NEW (W) | OLD (W) | Δ |
|---|---|---|---|
| h04–h07 (early-morning wake transition) | 76.0 / 85.9 / 107.6 / 123.1 | 77.8 / 89.1 / 111.6 / 125.1 | **−1.8 / −3.2 / −4.1 / −2.1** (largest single move: h06, −4.09 W) |
| h09–h14 (mid-morning through early afternoon) | 126.3–130.2 | 125.8–127.3 | **+0.3 to +1.2** (consistently positive) |
| h17–h20 (evening) | 103.6–134.8 | 103.6–135.5 | −0.2 to −0.9 (small, mixed) |
| Overall WD mean | 109.22 | 109.76 | −0.54 |
| Overall WE mean | 108.33 | 109.72 | **−1.40** |
| Night (0–5h) mean | 75.60 | 76.83 | −1.23 |
| Daytime (9–17h) mean | 129.45 | 129.02 | +0.43 |

**Direction check:** the shift is a coherent, small (sub-2-W on the whole-day mean) reshaping — early-morning "wake transition" hours (h04–h07) get *lower* mean MET (people staying in low-activity/sleep-adjacent codes slightly longer before the sharp morning ramp) while core daytime hours (h09–h14) get *slightly higher* MET. This is directionally consistent with the act30 fix: 04T re-raked activity conditional on the corrected (hom30,wrk30) state, so slots that used to carry spuriously "active" codes during the FLOATING artifact (state = neither home nor work, which peaked pre-fix) are now conditioned on their real state, which for early-morning slots skews toward the observed sleep/personal-care mix and for core daytime hours skews toward the observed work/active mix. **No 2022 person's hom30/wrk30 changed — only which activity code within the (already-correct) state was assigned, and by how the underlying census-linked pool composition shifted** (Step 5's `_excl` pool itself changed by −61 HH for reasons unrelated to act30, per the frame note). This is a plausible, small, non-alarming shift — not a regression.

2030 fullyhybrid band shows a **larger** version of the same pattern (as expected — 2030's donor pool for Calibration-C's Stage 2 shifted more, per the prior Progress Log entry's [1] Sleep-share WARN root-cause): WD mean diff **+0.632 W**, with h06 moving **−6.72 W** (early-morning) and h11–h17 moving **+1.9 to +3.8 W** (core daytime/early-evening) — same direction, larger magnitude, consistent with the Sleep-share WARN (36.60% vs 33–36% band) already flagged upstream as a real, root-caused, expected consequence of Task 1's fix, not a new Step-7 defect. All values stay well inside the validator's hard gate `[70, 245]` W and the INFO sleep-trough/diurnal-variation checks (D.1–D.4, all PASS both years).

**Office multiplier files — confirmed regenerated, row counts stated above (144 / 432), values traced:** office 2022 weekday peak `AT_WORK_fraction` moved negligibly (Office_Knowledge 0.6022→0.6015, Office_Public 0.6078→0.6054, Office_Sales 0.5915→0.6003 vs the June baseline) — expected, since `wrk30` (which drives the office channel) is untouched by both Task 1's act30 rake and Calibration-C. **2030 office band-monotonicity values are bit-identical to the June 26 baseline** (Office_Knowledge cons=0.5883/hyb=0.5022/fully=0.4623; Office_Public 0.5910/0.5142/0.4450; Office_Sales 0.6059/0.5368/0.5075) — confirms, independently, that the office channel is fully insulated from today's upstream changes (both `04T` and Calibration-C only ever touch `act30`/`hom30`, never `wrk30`), exactly as the design doc's Stage-2 note promises ("`wrk30` is never modified, so the office channel is unaffected").

**Files:**
- `Step7_docs/outputs_step7.20260715_pre_actv2/` (archive, 23 files/795 MB, verified via `ls -la` name+size diff).
- `Step7_docs/outputs_step7/*` — regenerated: `BEM_Schedules_2split_2022.csv`, `BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv`, `office_presence_multiplier_{2022,2030}.csv`, `step7_validation_report_{2022,2030}.html`, plus the script's own native `*_BAK_2026-07-15.csv` backups (redundant with but consistent with the mandatory archive above).
- `Step7_docs/run_audit_20260715.log`, `run_year2022_20260715.log`, `run_year2030_20260715.log`, `run_val_20260715.log` — full run logs.
- `Step7_docs/_verify_step7_rowcols.log`, `Step7_docs/_met_characterization.log` — independent verification scripts' output (row/HH/schema cross-check and MET hourly-profile diff), run from standalone one-off scripts (not committed as pipeline code) to re-derive every number in this entry directly from the CSVs rather than trust the validator's own printed summary.

**Blockers:** none. Local only — no cluster, no sbatch. Per task scope, Step 8/9 were NOT run. **Flagged for manager attention (not decided unilaterally):** the governing doc's Task-4 Aim line cites a "34/0/0 & 33/0/0" Step-7 baseline that does not match either `3rdJ_07_bemIntegration_2split.md`'s own logged 32/0/0-and-43/0/0 baseline or today's reproduced 32/0/0-and-43/0/0 result — same category of pre-existing doc/baseline drift already flagged for Step 5 and (by omission) Step 6 upstream; recommend reconciling all three in one pass when the doc-propagation pass mentioned in the task brief happens. Task 4's step 5 (Step 8 cluster campaign) is next and is out of this task's scope.
