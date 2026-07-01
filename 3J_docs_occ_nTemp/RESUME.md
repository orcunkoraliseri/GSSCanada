# RESUME — Opus Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Opus session to continue.**
Last updated: 2026-06-30 (Step 8 corrective cycle DONE; residential array drained CLEAN
168/168; office array handed off — waiting on it to drain).
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

## 3. WHERE WE ARE — Steps 1–7 DONE; Step 8 corrective cycle DONE; residential CLEAN; office draining

**Steps 5/6/7 closed** (see memory `project_step{5,6,7}_2split_status`). Step-7 deliverables in
`Leg2_2-split/Step7_docs/outputs_step7/`: residential `BEM_Schedules_2split_{2022,2030_conservative,
2030_hybrid,2030_fullyhybrid}.csv` (REPLACE) + office `office_presence_multiplier_{2022,2030}.csv`
(MODULATE). Validator: 2022 = 32/0/0, 2030 = 43/0/0.

**Step 8 = two-channel EnergyPlus simulation.** Built + corrective cycle applied + Phase A (8C.0 +
8A) ran + val §0 PASSED + arrays launched. All in `Leg2_2-split/Step8_docs/`:
- `3rdJ_08_simulation_2split.md` (design + live Progress Log — canonical doc, uploaded to cluster),
  `…_val.md` (validation spec), `3rdJ_08_builder_prompt.md`, `3rdJ_08_corrective_prompt.md` (DONE).
- **Active handoff:** `Step8_docs/extra/3rdJ_08_office_submit_prompt.md` — the office submit +
  spot-check + drain-report prompt (A → A0 → B → C; details in §5).
- Scripts: `3rdJ_08A_gen_historical_schedules.py`, `3rdJ_08B_run_paired_mc.py`,
  `office_integration.py`, `office_runner.py`, `eSim_bem_utils_3J/` (engine, `main.py`),
  `3rdJ_08C0_idf_transition.sh`, `run_residential_array.sh`, `run_office_array.sh`,
  `3rdJ_08_simulation_2split_val.py`.

**Locked scope:** 7 scenarios both channels (2005/2010/2015/2022/2030-cons/hybrid/fullyhybrid).
Full coupling People+Lights+Equipment (office Lights `L=max(Lmin,ηOD)` Lmin=0.15; Equip
`P=Pbase+(1−Pbase)O` Pbase=0.20); HVAC/DHW code baseline; peak densities never modified. Office
= 3 archetypes × 2 envelopes (Tall/SuperTall) × 6 CZ × 7 scen = **252 deterministic** (1 EP run/task,
~38s each, array = 252 tasks). Residential = 4 arch × 6 CZ × 7 scen × N=50 paired = **8,400** (array
= **168 tasks**, 0-167). Step-8 scratch: `/speed-scratch/o_iseri/step8_2split/` (upload tree under
`upload/`, logs `logs/`, residential output `campaign/`, office output `office/`).

## 4. WHAT'S DONE THIS CYCLE (corrective + Phase A + residential array)

The corrective cycle (3 blockers + minors: upload-tree mirror + missing inputs; 8C.0 output dir
repoint; `pg`→`ps`; anchor `"Tall"` vs `"SuperTall"`; module precheck) was applied and the employee
owned upload + submission (Option A safe pause). Phase A ran, val §0 PASSED, arrays launched.

- **Residential array (job 1029756): FULLY DRAINED, CLEAN.** 168/168 tasks `status=ok`, 0 errors.
  All 8,400 cells ran without a single failure. (sacct shows 304 records — sub-step overcount;
  collapses to 168/168 COMPLETED.) **Spot-check (Task A0) still pending** — we want one 2005 + one
  2030 cell proven to have a non-zero `hourly_meters.csv`/`eplusout.sql` before we trust the `ok`
  flag (lesson: a status flag ≠ proven real output).
- **Symlink/bind bug — RESOLVED.** `/speed-scratch`→`/nfs/speed-scratch` symlink + Python
  `realpath` meant EP got `/nfs/...` paths the singularity wrapper didn't bind → rc=1. Fix:
  `--bind /nfs/speed-scratch` added to the energyplus + ExpandObjects wrappers in
  `run_residential_array.sh`. Office is safe by construction (`office_runner.py` uses `abspath`,
  binds `dir:dir`).

## 5. WHAT'S NEXT — office array draining; one bundle to review

The office array was NOT yet in the queue at the last drain report, so the active handoff
(`Step8_docs/extra/3rdJ_08_office_submit_prompt.md`) does it. That prompt =
**A** submit office (`sbatch …/Step8_docs/run_office_array.sh`, 252 tasks) →
**A0** residential output spot-check (2 cells, one 2005 + one 2030, prove non-zero output file) →
**B** confirm one office task's real output (`eplusout.eso`/`.sql`/`hourly_meters.csv`) →
**C** drain both, report residential ok/error + office completed/failed as ONE bundle, append a
Progress Log to `3rdJ_08_simulation_2split.md` (do NOT run the §1–§8 scorecard yet).

**You (manager) wait on the Task C bundle.** When it lands: if A0 is clean (both files non-zero) and
office drained with no failure pattern, that's the gate to the full **§1–§8 validation review** of
the two-channel campaign (separate cycle — that's where the val scorecard runs). Debug any blocker
the employee flags (zero-byte output, office failures, transition/bind error).

**Suggested opening line to the user:** "Residential is drained clean (168/168) and office is handed
off via the submit prompt (A→A0→B→C). Has the employee relayed the Task C bundle yet — office
completed/failed counts and the two residential spot-check file sizes?"
