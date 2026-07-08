# EMPLOYEE PROMPT — Step 8 Apartment Cooling-Setpoint Fix + Subset Re-simulation (3J Leg-2)

> Paste-ready. Manager-authored 2026-07-07. Execute top-to-bottom; the session-boundary
> protocol below tells you where to stop and report.

---

**You are the employee. Execute the task below and append a Progress Log entry on completion**
(to BOTH `investigation/step8_coolfix_implementation_plan.md` and
`investigation/step8_resid_heating_cooling_dominance_investigation.md`).

## Context (read these first, in this order)

All paths relative to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\` locally and to
`/speed-scratch/o_iseri/step8_2split/upload/GSSCanada-main-equivalent tree` on the cluster
(the upload tree root is `/speed-scratch/o_iseri/step8_2split/upload/`).

1. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_coolfix_implementation_plan.md`
   — THE runbook. This prompt operationalizes it; if this prompt and the plan disagree, flag it,
   don't guess.
2. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`
   — the confirmed diagnosis (frozen 24.0 °C year-round cooling setpoint in the two ASHRAE-90.1
   apartment prototype IDFs → internal-gain-driven cooling all winter; probe-proven §8.1).

**Scope guard:** Steps 1–7, Step 8A, the office campaign (252 runs), the two house archetypes
(SingleD/OtherDwelling), internal-load densities, and the heating setpoint schedule are ALL
untouched. You change: (a) the cooling-setpoint schedule in COPIES of the 2 apartment IDFs,
(b) one path constant in the 3J `main.py`, (c) one new validator gate. Then you re-simulate
ONLY MidRise+HighRise (4,200 runs) and refresh 8D/8E/Step-9.

## 🔴 Cluster hard rules (account-suspension risk — no exceptions)

- NEVER run python or any compute on the login node (`speed-submit2`). NEVER blocking `srun`.
  Everything computational goes through `sbatch` (fire-and-forget, read the log file later).
- Allowed on login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, mkdir,
  module load`, single-file `tail/head/grep/wc -l/cat`.
- EVERY job requests `-t 7-00:00:00` walltime. Every cluster command is a single line.
- Do NOT poll job status in a loop. Submit, report the job ID, stop. If a check is needed,
  one `sacct` per session, minimum 30 min apart.
- Label every command you show the user as "locally" or "on the cluster".

## Phase-0 decision (RESOLVED 2026-07-07 — encode, don't re-ask)

Variant **1a** (user delegated the choice to the manager; recommendation ratified — see the
plan's Progress Log): cooling setpoint `Through: 4/30` → **28.0**, `Through: 9/30` → **24.0**
(unchanged cooling season), `Through: 12/31` → **28.0**. Variant **1b** (winter blocks at
40.0 = lockout) is PRE-AUTHORIZED as fallback — apply it WITHOUT asking the user, but ONLY if
the Phase-4 smoke gate fails (rule below), and only once.

---

## Phase 1 — patched IDF set (locally)

1. Create `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/Buildings_MTL_v242_3Jfix/` and copy into
   it all 4 residential IDFs from `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`
   (`ASHRAE901_ApartmentHighRise_...v242.idf`, `ASHRAE901_ApartmentMidRise_...v242.idf`,
   `AttachedHouse+...v242.idf`, `DetachedHouse+...v242.idf`).
2. Write `Step8_docs/investigation/patch_apartment_cooling_setpoint.py`:
   - Text-level (NOT eppy): locate the single `Schedule:Compact,` object whose name field is
     `NECB-G-Thermostat Setpoint-Cooling` (object spans header → terminating `;`), in each of
     the two `ASHRAE901_Apartment*` files in the NEW dir only.
   - Replace it with the 1a seasonal version: three `Through:` blocks (4/30, 9/30, 12/31);
     within each block reproduce the SAME `For:` day-type structure as the original object;
     all hourly values 28.0 / 24.0 / 28.0 respectively.
   - **Exception:** if the original object contains `SummerDesignDay` or `WinterDesignDay`
     day-types, keep those day-types at 24.0 in ALL three blocks so HVAC autosizing is
     unchanged.
   - Print a unified diff of what changed per file.
3. Verify, all three of:
   - `grep -A5 "NECB-G-Thermostat Setpoint-Cooling"` on both patched files shows the seasonal
     blocks (investigation §6 spot-check);
   - the diff touches ONLY that one schedule object per apartment file;
   - the two house IDFs in the new dir are hash-identical (`Get-FileHash`) to the 2J originals.

## Phase 2 — config switch (locally)

4. Archive predecessor: copy `Step8_docs/eSim_bem_utils_3J/main.py` →
   `Step8_docs/archive/main.20260707_preCoolfix.py`.
5. Edit `main.py` line ~82: `STEP8_BUILDINGS_DIR` → the new `Buildings_MTL_v242_3Jfix` dir
   (keep it an absolute join off the repo base like the current line; add a one-line comment
   citing `investigation/step8_coolfix_implementation_plan.md`). Do NOT touch 2J's `main.py`.

## Phase 3 — validator dominance gate (locally)

6. Archive predecessor: copy `Step8_docs/3rdJ_08_simulation_2split_val.py` →
   `Step8_docs/archive/3rdJ_08_simulation_2split_val.20260707_preCoolfixGate.py`.
7. In `_gate_enduse_split()` (near gates 4.6/4.7, ~line 1422) add **gate 4.9-heat-dominance**:
   from `agg_annual` (resid, scenario 2022), per archetype × CZ in {6A, 6B, 7A} compute
   `ratio = cooling_ET_kWh_sum / heating_ET_kWh_sum`. Status: **FAIL** if any archetype has
   ratio > 2.0 in CZ 7A; **WARN** if any archetype has ratio > 1.25 in any of 6A/6B/7A;
   else PASS. Message must list the per-archetype 7A ratios. This gate MUST be able to FAIL —
   that is its purpose (4.6/4.7 are PASS/WARN-only by construction).
8. `py -m py_compile 3rdJ_08_simulation_2split_val.py` must pass. Do NOT regenerate the report
   HTML locally (local tree lacks campaign outputs; a local run would regress the scorecard —
   this happened before, see the improvements doc Progress Log).

## Phase 4 — smoke test (cluster; STOP-AND-REPORT after submitting)

9. Write `Step8_docs/run_coolfix_smoke.sh` locally: copy `run_residential_array.sh`, remove the
   `--array` directive, keep ALL the E+ SIF-wrapper scaffolding (the `EPWRAP` block — the sims
   fail without it), and replace the python invocation with two sequential calls:
   `--arch MidRise --city Winnipeg_7A --scenario 2022 --n 2 --seed 42 --mode standard
   --out-dir "$SCRATCH/campaign_smoke"` then the same with `--arch HighRise`.
   Job name `3J_coolfix_smoke`, `-t 7-00:00:00`.
10. Upload (locally): scp the new IDF dir (recursive), edited `main.py`, edited val script, and
    `run_coolfix_smoke.sh` into the matching paths under
    `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/`.
11. Submit (on the cluster): `sbatch .../Step8_docs/run_coolfix_smoke.sh`.
12. **STOP. Report the job ID + everything done so far.** No polling.

## Phase 4b — smoke evaluation (next session, once user relays the job finished)

13. scp the 4 smoke `hourly_meters.csv` files local
    (`campaign_smoke/<cell>/sample_*/2022/hourly_meters.csv`) into a local mirror dir, run
    `investigation/probe_winter_cooling.py` locally with `STEP8_CAMP_DIR` pointed at the mirror.
14. **Smoke gate:** DJF cooling per archetype < 10% of pre-fix values (pre-fix: MidRise
    16,474 kWh, HighRise 34,126 kWh DJF) AND annual heating clearly up. Also check the SLURM
    log for E+ severe/fatal errors (a malformed Schedule:Compact fatals out — if so, fix the
    patch, re-verify Phase 1, resubmit smoke).
    - PASS → Phase 5. FAIL (material DJF cooling remains) → apply variant 1b (winter blocks
      40.0), redo Phase 1 verify + re-upload + resubmit smoke ONCE. If 1b also fails, STOP and
      report — that falsifies the mechanism and the manager must re-diagnose.

## Phase 5 — full subset re-sim (cluster; STOP-AND-REPORT after submitting)

15. Preserve pre-fix outputs (on the cluster, single line):
    `mkdir -p /speed-scratch/o_iseri/step8_2split/campaign_precoolfix && mv /speed-scratch/o_iseri/step8_2split/campaign/MidRise__* /speed-scratch/o_iseri/step8_2split/campaign/HighRise__* /speed-scratch/o_iseri/step8_2split/campaign_precoolfix/`
16. Write + upload `run_residential_array_coolfix.sh`: copy of `run_residential_array.sh` with
    `#SBATCH --array=84-167` (MidRise = 84–125, HighRise = 126–167 per the cell-idx decode
    `arch_idx = idx // 42`) and job name `3J_8B_coolfix`. NOTHING else changes (seed 42
    preserves the paired HH sampling).
17. Submit (on the cluster): `sbatch .../run_residential_array_coolfix.sh`.
18. **STOP. Report the array job ID.** 84 tasks × 50 sims; the queue is saturated
    (`AssocGrpCpuLimit`) — expect days. No polling.

## Phase 6 — downstream refresh (next session, once user relays the array finished)

19. Sanity first (on the cluster): `sacct -j <arrayjob> --format=JobID,State,ExitCode | grep -cv COMPLETED`
    — investigate any non-COMPLETED tasks before aggregating (resubmit failed indices only).
20. Submit in sequence (each fire-and-forget, wait for user relay between them):
    `run_aggregation.sh` (confirm it does a full rebuild of `agg_*.csv` — if it has a
    `--rebuild`/env flag, set it), then `run_validation.sh` (8E), then the Step-9 report job
    (same submission pattern as job 1058662 — see `project_step9_2split_status` /
    `Step9_docs`).
21. After each: scp outputs local (agg CSVs, `outputs_step8/step8_validation_report.html`,
    Step-9 report). Archive predecessor HTMLs per repo convention before overwriting.
22. Campaign-scale probe: scp 5 fresh CZ7A `hourly_meters.csv` per apartment archetype from the
    NEW campaign, run `probe_winter_cooling.py` locally, confirm the smoke-gate numbers hold at
    scale.

## Phase 7 — documentation (locally)

23. Acceptance checks to report against (all must hold, else STOP-and-report, don't paper over):
    - CZ7A cooling/heating ratio per apartment archetype now O(1) (pre-fix 5.3× / 9.8×);
    - gate 4.9 PASS; 4.6/4.7 PASS; **0 FAIL** scorecard overall;
    - office gates and house-archetype results unchanged;
    - if any §4 SHEU/EUI band gate newly FAILs → STOP and report (new information, not a doc
      task).
24. Append dated Progress Log entries: implementation plan (per-phase, job IDs, before/after
    ratio table), investigation doc (option 1+3 APPLIED), `project`-level status docs the user
    maintains for Step 8/Step 9, and an addendum note in
    `Leg2_2-split/investigation/2split_results_acceptance_review.md` (its PAPER-READY verdict
    predates this fix — re-affirm with the new numbers or amend).
25. Do NOT git-commit anything — leave the working tree for the user's review (repo rule: user
    owns git).

## Session-boundary protocol

Natural stop points = steps 12, 18, and after each submission in 20. At each stop: report what
was done, every job ID, and the exact resume point in this prompt. The user relays job
completion; the next employee session resumes from the stated step. Never idle-wait or poll for
a running job within a session.

## Blockers

Anything ambiguous, any FAIL outside the rules above, any file that doesn't match what this
prompt says it contains (e.g. the Schedule:Compact object differs from the investigation's
description) → stop and flag to the user for the manager. Do not improvise around a mismatch.
