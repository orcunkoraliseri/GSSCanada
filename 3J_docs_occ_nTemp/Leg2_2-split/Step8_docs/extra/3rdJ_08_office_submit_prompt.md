# Employee Prompt — Step 8C Office Array Submit + Drain Report

**You are the employee. Execute the tasks below and append a Progress Log entry to `3rdJ_08_simulation_2split.md` on completion.**

---

## Context

You are executing Step 8 (EnergyPlus simulation) for 3J Leg-2 (two-channel residential + office campaign). The residential array is already running:

- **Job 1029756** (`run_residential_array.sh`, 168 tasks, ps partition, `/speed-scratch/o_iseri/step8_2split/logs/8B_resid_1029756_*.out`)

The residential Singularity wrappers were patched with `--bind /nfs/speed-scratch` (fix for the `/speed-scratch` → `/nfs/speed-scratch` symlink issue). Tasks 0–3 confirmed 50/50.

The **office array has not yet been submitted.** The office script (`run_office_array.sh`) uses a different EP invocation (`office_runner.py → run_energyplus_via_sif()`) that self-binds each resolved path directly — it already handles the symlink correctly and does **not** need the same patch.

---

## Your Tasks

### Task A — Submit the office array

**On the cluster:**
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_array.sh
```

Record the job ID.

The office array is 252 tasks (3 arch × 2 envelope × 6 CZ × 7 scenarios), deterministic (1 EP run per task, not N=50). Logs go to `/speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_<task>.out`. Output cells go to `/speed-scratch/o_iseri/step8_2split/office/`.

### Task B — Confirm one office task produces real output

Wait for at least one office task to finish (each run takes ~38 s EP + overhead, so ~5 min total per task). Then confirm a task's output directory contains `eplusout.eso` or `eplusout.sql` or `hourly_meters.csv`.

Report: the cell label (arch × envelope × city × scenario), the EP return code from the log, and whether the expected output file exists and is non-zero bytes.

### Task C — Wait for both arrays to drain, then report

When both job 1029756 (residential) and the office job finish (all tasks in `squeue -u o_iseri` disappear for both), collect the following and report as a single bundle:

1. **Residential:** total tasks, count with `status=ok`, count with `status=error`. Extract from:
   ```
   grep "DONE cell" /speed-scratch/o_iseri/step8_2split/logs/8B_resid_1029756_*.out
   ```
2. **Office:** total tasks, count completed OK (look for `DONE cell.*status=ok` or equivalent in `8C_office` logs), count failed.
3. **Any unexpected failure patterns** — if multiple tasks fail with the same error substring, quote the first example.

This report is the gate for §1–§8 validation review. Do **not** run the validation scorecard yourself — just deliver the counts.

---

## Guardrails

- **NEVER** run blocking `srun` or bare `python` on the login node (`speed-submit2`). Use `sbatch` only. Allowed on login: `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`grep`.
- All job submissions must use `-t 7-00:00:00` (already in the scripts — do not modify).
- Do not upload any files unless you identify a bug that requires a fix.
- Append a Progress Log entry to `3rdJ_08_simulation_2split.md` (locally, then `scp` it to `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/`) once Task C is complete.

---

## Key Paths

| Item | Path |
|---|---|
| Cluster python | `/speed-scratch/o_iseri/envs/step4/bin/python` |
| SIF | `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` |
| Upload root | `/speed-scratch/o_iseri/step8_2split/upload/` |
| Residential logs | `/speed-scratch/o_iseri/step8_2split/logs/8B_resid_1029756_*.out` |
| Office logs | `/speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_*.out` |
| Residential output | `/speed-scratch/o_iseri/step8_2split/campaign/` |
| Office output | `/speed-scratch/o_iseri/step8_2split/office/` |
| Progress doc (local) | `GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split.md` |
