# Employee Prompt — Step 8E Validation Scorecard: Upload, Submit, Report

**You are the employee. Execute the tasks below in order and append a Progress Log entry to `3rdJ_08_simulation_2split.md` on completion.**

---

## Context — both campaigns are done; this is the acceptance test

Both EnergyPlus arrays have drained clean:
- **Residential** (job 1029756): 168/168 tasks ok → 8,400 cells under `/speed-scratch/o_iseri/step8_2split/campaign/`.
- **Office** (job 1048238 + smoke 1048226): 252/252 cells under `/speed-scratch/o_iseri/step8_2split/office/`.

Now we run the **§1–§8 validation scorecard** (`3rdJ_08_simulation_2split_val.py`) — it reads every cell's `hourly_meters.csv`, checks run integrity, schedule-injection fidelity, MC convergence, and scenario/band ordering, and writes an HTML scorecard.

**Manager fix applied (why two files are re-uploaded):** the validator's default output paths (`outputs_step8/campaign_N50`, `outputs_step8/office`) did **not** match where the arrays actually wrote (`$SCRATCH/campaign`, `$SCRATCH/office`). Left unfixed, §1 would falsely report "0/8400, 0/252 not run." Fix = the validator now reads `STEP8_CAMP_DIR` / `STEP8_OFFICE_DIR` env vars (defaults unchanged), and a new `run_validation.sh` exports the real scratch dirs. **Two files changed: `3rdJ_08_simulation_2split_val.py` + `run_validation.sh`.** Nothing else.

This validator imports pandas/numpy and rglobs ~8,600 CSVs, so it **must run via `sbatch`**, never on the login node.

---

## Your Tasks

### Task A — Upload the two files (one bundle)

**Locally (Windows):**
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step8_docs\3rdJ_08_simulation_2split_val.py" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py
```
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step8_docs\run_validation.sh" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_validation.sh
```
Upload **only** these two. Do not touch any other file.

### Task B — Submit the validation job

**On the cluster:**
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_validation.sh
```
Record the job ID. It may PEND behind the NYC campaign jobs (`AssocGrpCpuLimit`) — expected. Once it starts it runs single-node; the §3 MC-convergence gate reads all 8,400 residential CSVs, so allow **~10–30 min** of runtime. **No poll loops** — check at most once every ≥30 min.

### Task C — Collect and report the scorecard

When the job disappears from `squeue -u o_iseri`, do all three — **single-file commands only on the cluster:**

1. Dump the scorecard tally + the §1 run counts:
   ```
   grep -E "Scorecard:|\] .1.1|FAIL" /speed-scratch/o_iseri/step8_2split/logs/8E_val_<jobid>.out
   ```
   (Captures the final `Scorecard: X PASS / Y WARN / Z INFO / W FAIL` line, both §1.1 run-count lines, and every FAIL line.)

2. Pull the HTML report back **locally (Windows):**
   ```
   scp o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/step8_validation_report.html "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step8_docs\outputs_step8\step8_validation_report.html"
   ```

3. **Report as one bundle to the manager:**
   - The `Scorecard:` line (PASS / WARN / INFO / FAIL counts).
   - The two §1.1 lines (residential `n/8400`, office `n/252` — these MUST now show real counts, not 0).
   - **Every blocking FAIL** — any FAIL line in §0, §1, or §2 (quote it verbatim). If there are none, say "no blocking FAILs."
   - Confirm the HTML landed locally (byte size).

**Do NOT interpret or judge the scorecard** — the manager reviews it. If §1.1 still shows `0/8400` or `0/252`, STOP and flag it (means the env-var path fix didn't take) and quote the two `CAMP=`/`OFFICE=` lines the wrapper echoed at the top of the log.

---

## Guardrails

- **NEVER** run blocking `srun` or bare `python`/`python3` on the login node (`speed-submit2`). Use `sbatch` only. Allowed on login: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `scp`, `ls`, single-file `cat`/`tail`/`head`/`grep`/`wc -l`.
- Walltime is `-t 7-00:00:00` (already in `run_validation.sh` — do not modify).
- Only two files are uploaded: `3rdJ_08_simulation_2split_val.py` + `run_validation.sh`.
- Append a Progress Log entry to `3rdJ_08_simulation_2split.md` (locally), then `scp` it to `…/Step8_docs/` once Task C is complete.

---

## Key Paths

| Item | Path |
|---|---|
| Fixed validator (local) | `…\Leg2_2-split\Step8_docs\3rdJ_08_simulation_2split_val.py` |
| New wrapper (local) | `…\Leg2_2-split\Step8_docs\run_validation.sh` |
| Upload dir (cluster) | `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/` |
| Validation log (cluster) | `/speed-scratch/o_iseri/step8_2split/logs/8E_val_<jobid>.out` |
| HTML report (cluster) | `…/Step8_docs/outputs_step8/step8_validation_report.html` |
| Residential output | `/speed-scratch/o_iseri/step8_2split/campaign/` |
| Office output | `/speed-scratch/o_iseri/step8_2split/office/` |
| Cluster python | `/speed-scratch/o_iseri/envs/step4/bin/python` |
| Progress doc (local) | `…\Leg2_2-split\Step8_docs\3rdJ_08_simulation_2split.md` |

---

## Job ID Log (fill in as you go)

- Validation (8E): `__________`
