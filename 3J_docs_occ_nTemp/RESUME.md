# RESUME — Opus Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Opus session to continue.**
Last updated: 2026-06-29 (Step 8 BUILT + manager-reviewed; corrective cycle pending).
First read CLAUDE.md and memory/MEMORY.md (esp. `project_step8_2split_status.md`,
`project_step7_2split_status.md`), then resume as if no break happened.

---

## 0. Who you are

You are the **MANAGER (Opus)** in a two-agent workflow for the GSSCanada occupancy
modeling research (3rd journal = **"3J"**, Leg-2 = **"2-split"** = two-channel
AT_HOME + AT_WORK joint occupancy model).

- **You plan / debug / judge / write builder prompts. You do NOT execute, submit cluster
  jobs, or run live poll loops.** The employee handles execution + relays results; you act
  only on terminal outcomes.
- **Cheap Haiku/Sonnet "employees" do ALL execution** — scp, sbatch, log peeks, monitoring,
  retrieval. ALWAYS set `model:` on every Agent call (bg agents silently inherit Opus). Use
  one-shot checks, not poll loops; min ~30-min spacing.
- You are "both manager and sometimes employer": if the user hands you a current runbook AND
  confirms, you may execute that one cycle. Default is plan/debug only.
- Communication: casual, ≤100 words unless detail requested. End with the literal command to
  run. Resolve clarifying questions BEFORE printing a builder prompt.

## 1. HARD RULES (never violate — account-suspension risk)

1. **NEVER** run a blocking/interactive `srun` (or any python/computation) on the Speed
   **login node** `speed-submit2`. ALWAYS `sbatch` (fire-and-forget), then read the output
   file. Flagged 3× — one more = suspension = all progress lost.
2. **NO bare `python`/`python3` on the login node — ever** (incl. one-liners). Allowed on
   login node: `sbatch, squeue, sacct, scancel, scontrol, ssh-mkdir, cd, ls, scp, module
   load`, single-file `tail/head/grep/wc -l/cat`. Anything importing pandas/numpy/torch/eppy
   or iterating dirs → `sbatch`.
3. **EVERY job submission MUST request `-t 7-00:00:00`** (1-week min). Speed ps/pg MaxTime =
   7 days. A 1h cap once killed control job 987005 with empty output.
4. Speed login shell is **tcsh**: no `2>&1` (use `>` only; SLURM captures stderr to
   `--output`); one short line per command, no `\` continuation.
5. **Label every command "locally" or "on the cluster."**
6. **Bundle uploads** — one upload cycle; never file-by-file across cycles. Never upload the
   whole `GSSCanada-main/` dir; only named files/dirs.
7. Before any `sbatch` handoff, scan script imports — ensure eppy/pandas/numpy/torch/etc.
   exist in the cluster env (`envs/step4`); add a precheck line if unsure.
8. **Step 4 is LOCKED.** Archive predecessor (`cp` to `archive/`) before any edit. Update
   progress logs **live/incrementally**, not batched.
9. **Full audit, no patches**: when one cluster cycle reveals a bug, audit the whole chain and
   ship ONE fix bundle.

## 2. Cluster facts (Speed @ Concordia)

- host: `o_iseri@speed.encs.concordia.ca`; login node = submission only; GPU partition = `pg`,
  CPU = `ps`.
- python: `/speed-scratch/o_iseri/envs/step4/bin/python`
- EnergyPlus 24.2 SIF: `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`
- Step-8 scratch dir: `/speed-scratch/o_iseri/step8_2split/` (upload tree under `upload/`,
  logs under `logs/`).
- Step-4 base ckpt (LOCKED): `…/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt`

---

## 3. WHERE WE ARE — Steps 1–7 DONE; Step 8 BUILT + REVIEWED (corrective cycle pending)

**Steps 5/6/7 closed** (see memory `project_step{5,6,7}_2split_status`). Step-7 deliverables in
`Leg2_2-split/Step7_docs/outputs_step7/`: residential `BEM_Schedules_2split_{2022,2030_conservative,
2030_hybrid,2030_fullyhybrid}.csv` (REPLACE) + office `office_presence_multiplier_{2022,2030}.csv`
(MODULATE). Validator: 2022 = 32/0/0, 2030 = 43/0/0.

**Step 8 = two-channel EnergyPlus simulation.** Docs written + employee BUILT it (2026-06-29).
All in `Leg2_2-split/Step8_docs/`:
- `3rdJ_08_simulation_2split.md` (design, §0 locked decisions), `…_val.md` (validation),
  `3rdJ_08_builder_prompt.md` (original build prompt), `3rdJ_08_corrective_prompt.md`
  (**current — the fix→upload→submit handoff, awaiting employee execution; user delivers it**).
- Scripts: `3rdJ_08A_gen_historical_schedules.py`, `3rdJ_08B_run_paired_mc.py`,
  `office_integration.py`, `office_runner.py`, `eSim_bem_utils_3J/` (engine, `main.py`),
  `3rdJ_08C0_idf_transition.sh`, `run_residential_array.sh`, `run_office_array.sh`,
  `3rdJ_08_simulation_2split_val.py`.

**Locked scope:** 7 scenarios both channels (2005/2010/2015/2022/2030-cons/hybrid/fullyhybrid).
Full coupling People+Lights+Equipment (office Lights `L=max(Lmin,ηOD)` Lmin=0.15; Equip
`P=Pbase+(1−Pbase)O` Pbase=0.20); HVAC/DHW code baseline; peak densities never modified. Office
= 3 archetypes × 2 envelopes (Tall/SuperTall) × 6 CZ × 7 scen = **252 deterministic**. Residential
= 4 arch × 6 CZ × 7 scen × N=50 paired = **8,400**. New gating sub-step **8A** generates the
historical (2005/2010/2015) schedules (don't exist yet). Office IDFs need v22.1→v24.2 transition
(sub-step 8C.0).

**Employee pre-campaign scorecard:** 6 PASS / 0 WARN / 18 INFO / 3 FAIL (3 FAILs = the missing
2005/2010/2015 CSVs — expected; 8A generates them).

## 4. MANAGER REVIEW (2026-06-29) — 3 blockers + 4 minor, captured in the corrective prompt

The scripts are individually sound but had integration bugs. The corrective prompt
(`3rdJ_08_corrective_prompt.md`) tells the employee to fix, re-smoke-test, then **own the upload
AND submission** (user approved this delegation):

- **Blocker 1 — upload layout + missing inputs.** Scripts derive paths via `__file__` walk-up
  (`main.py:39` `BASE_DIR` = 5 levels up); the array `.sh` already `cd` to nested
  `upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs`. Upload must MIRROR the repo tree (not flat)
  and include the inputs that were omitted: Step5 aug CSV, Step6 2030 diaries, ALL Step7
  `BEM_Schedules_2split_*`+`office_presence_multiplier_*`, `0_Occupancy/processed/
  office_archetype_lookup.csv`, `BEM_Setup/{Buildings/CAN_CLG,CAN_MTL,WeatherFile}`,
  `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242`.
- **Blocker 2 — 8C.0 output dir.** `3rdJ_08C0_idf_transition.sh` writes v242 IDFs to
  `$SCRATCH/office_idfs_v242` but `office_runner.py:104` reads `Step8_docs/outputs_step8/
  office_idfs_v242/<CAN_CLG|CAN_MTL>`. Repoint 8C.0 output (subdir tokens already match CZ_MAP).
- **Blocker 3 — GPU misuse.** `run_residential_array.sh` requests `-p pg --gres=gpu:1` but 8B is
  EnergyPlus CPU-only → change to `-p ps`.
- **Minor:** office_runner `"Tall"` substr also matches `"SuperTall"` (anchor it); add module
  precheck line; comment that `get_region_from_epw` still returns "Alberta" (harmless — 8B passes
  `city["region"]`="Prairies" directly). **VERIFIED CORRECT:** Calgary_6B→"Prairies" (3J `PR` has
  no Alberta), all 8 IDFs exist, 7-day walltime + sbatch-only honored.

**Submission = Option A (safe pause, user-chosen, NOT auto-chain):** employee submits 8C.0 + 8A →
reports job IDs and pauses → runs val **§0** → **only on §0 PASS** submits the residential + office
arrays. We deliberately rejected `--dependency=afterok` (afterok = "didn't crash" ≠ "schedules
correct"; a wrong-but-clean 8A would fire 8,652 wasted sims).

## 5. WHAT'S NEXT — what you (manager) wait on

The user is delivering `3rdJ_08_corrective_prompt.md` to a fresh employee (Sonnet) session. Next,
the employee reports back: **fixes applied + local re-smoke result + upload verification + Phase A
(8C.0 + 8A) job IDs.** You review those. When 8C.0 + 8A finish and val §0 runs, you review the §0
result; on **§0 PASS**, confirm the residential + office arrays were submitted; later review the
full **§1–§8** validation after the arrays complete (separate cycle). Debug any blocker the
employee flags (missing input, §0 FAIL, transition error, dep missing).

**Suggested opening line to the user:** "Step 8 is built and I've reviewed it — 3 blockers + a few
minor items are in the corrective prompt, with upload + submit delegated to the employee and the
safe §0 pause before the arrays. Has the employee reported back yet (fix result / Phase A job IDs)?"
