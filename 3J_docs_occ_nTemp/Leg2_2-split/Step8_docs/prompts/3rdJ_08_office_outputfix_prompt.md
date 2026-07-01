# Employee Prompt — Step 8C Office Output-Fix: Re-upload, Smoke, Resubmit, Drain

**You are the employee. Execute the tasks below in order and append a Progress Log entry to `3rdJ_08_simulation_2split.md` on completion.**

---

## Context — what broke and what was fixed

The office array (**job 1032839**, 252 tasks) was failing. Two tasks completed but both produced `status=fail`:

- EnergyPlus ran fine and finished a full annual simulation (~9–10 min, *not* the ~38 s we first estimated — a 10-min office run is NORMAL, not hung).
- But `eplusout.sql` had an **empty `ReportData` table** → `hourly_meters.csv` was never written → `status=fail`.

**Root cause (confirmed):** the residential path runs every IDF through `idf_optimizer.optimize_idf(meter_frequency='Hourly', enable_hourly_detail=True)`, which injects `Output:SQLite` + hourly `Output:Meter` objects. The **office path never did this.** PNNL Tall/SuperTall prototypes ship with `Output:SQLite` + tabular reports but **no time-series `Output:Meter`/`Output:Variable`**, so the SQL has nothing to report.

**The fix (already applied locally by the manager):** `office_integration.py` now injects hourly outputs into every office IDF just before save — a new `_ensure_output_objects()` call adds `Output:SQLite` (idempotent) + 6 hourly `Output:Meter` (InteriorLights, InteriorEquipment, Heating/Cooling/WaterSystems:EnergyTransfer, Electricity:Facility) + 3 hourly `Output:Variable` (Zone Lights/Equipment Electricity Energy, Zone People Occupant Count). It does **not** touch office physics (no Timestep/Solar/density changes).

**Only ONE file changed: `office_integration.py`.** The array script `run_office_array.sh` is unchanged and already correct (`-t 7-00:00:00`, `-p ps`, array 0-251).

---

## Your Tasks

### Task A — Cancel the broken office job

**On the cluster:**
```
scancel 1032839
```
Confirm it's gone: `squeue -u o_iseri | grep 3J_8C` (should return nothing). Cancelling also frees the account CPU reservation, so the smoke test below schedules sooner.

> Leave the two stale failed cell dirs as-is — they have no `hourly_meters.csv`, so the resubmit's `skip_done` will correctly re-run them. No cleanup needed.

### Task B — Re-upload the one fixed file

**Locally (Windows):**
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step8_docs\office_integration.py" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/office_integration.py
```
Do **not** upload anything else. Do **not** touch `run_office_array.sh`.

### Task C — Smoke test ONE cell (validate the fix before burning 252 tasks)

Run just cell index 0 (= `Office_Knowledge / Tall / 5A / 2005` — one of the exact cells that failed before). The CLI `--array` overrides the script's `0-251`:

**On the cluster:**
```
sbatch --array=0-0 /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_array.sh
```
Record the job ID. It may PEND behind the NYC campaign jobs (account `AssocGrpCpuLimit`) — that's expected. **Do not poll in a loop.** Check at most once every ≥30 min until it completes (~10 min once it starts).

When it finishes, verify the fix worked — **on the cluster, single-file commands only:**
```
wc -l /speed-scratch/o_iseri/step8_2split/office/Office_Knowledge__Tall__5A/2005/hourly_meters.csv
head -2 /speed-scratch/o_iseri/step8_2split/office/Office_Knowledge__Tall__5A/2005/hourly_meters.csv
```
**PASS criteria:** `wc -l` ≈ **8761** (8760 hours + header), the header row has `Hour` + several meter/variable columns, and the first data row has non-zero values.

- ✅ If PASS → proceed to Task D.
- ❌ If still header-only, zero rows, or missing → **STOP and flag to the manager.** Do not launch the full array. Quote the tail of `/speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_0.out` and any `eplusout.err` severe errors.

### Task D — Launch the full office array

Only after Task C PASSES:

**On the cluster:**
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_array.sh
```
Record the job ID. This submits all 252 tasks (0-251); cell 0 already has `hourly_meters.csv` from the smoke, so `skip_done` skips it (251 effective). Expect pending behind NYC jobs. No poll loops — ≥30-min spacing.

### Task E — Drain and report (the bundle)

When the full office job disappears from `squeue -u o_iseri`, collect and report as a single bundle:

1. **Office:** total tasks (252), count `status=ok`, count `status=fail`. Extract from the logs, e.g.:
   ```
   grep -h "Result:" /speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_*.out | grep -c "'status': 'ok'"
   grep -h "Result:" /speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_*.out | grep -c "'status': 'fail'"
   ```
2. **The smoke cell stats** from Task C (`wc -l` count + header columns).
3. **Any failure pattern** — if multiple tasks fail with the same error substring, quote the first example and its cell label.

This bundle is the gate for the §1–§8 validation review. **Do not run the validation scorecard yourself** — just deliver the counts.

---

## Guardrails

- **NEVER** run blocking `srun` or bare `python`/`python3` on the login node (`speed-submit2`). Use `sbatch` only. Allowed on login: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `scp`, `ls`, single-file `cat`/`tail`/`head`/`grep`/`wc -l`.
- All job submissions use `-t 7-00:00:00` (already in the script — do not modify).
- Only one file is uploaded: `office_integration.py`. Do not upload anything else.
- Append a Progress Log entry to `3rdJ_08_simulation_2split.md` (locally), then `scp` it to `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/` once Task E is complete.

---

## Key Paths

| Item | Path |
|---|---|
| Changed file (local) | `…\Leg2_2-split\Step8_docs\office_integration.py` |
| Changed file (cluster) | `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/office_integration.py` |
| Array script (cluster, unchanged) | `…/Step8_docs/run_office_array.sh` |
| Cluster python | `/speed-scratch/o_iseri/envs/step4/bin/python` |
| SIF | `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` |
| Office logs | `/speed-scratch/o_iseri/step8_2split/logs/8C_office_<jobid>_*.out` |
| Office output | `/speed-scratch/o_iseri/step8_2split/office/` |
| Smoke cell output | `/speed-scratch/o_iseri/step8_2split/office/Office_Knowledge__Tall__5A/2005/hourly_meters.csv` |
| Progress doc (local) | `…/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split.md` |

---

## Job ID Log (fill in as you go)

- Cancelled: `1032839`
- Smoke (cell 0): `__________`
- Full array (0-251): `__________`
