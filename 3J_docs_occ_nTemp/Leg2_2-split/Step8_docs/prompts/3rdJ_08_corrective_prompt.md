# 3rd Journal — Step 8 — EMPLOYEE CORRECTIVE PROMPT (fix → upload → submit)

> Manager-authored, 2026-06-29. Follows the pre-campaign build (scorecard 6 PASS / 0 WARN / 18 INFO / 3 FAIL — the 3 FAILs are the missing 2005/2010/2015 CSVs, expected; 8A generates them). A manager review of the build found **3 campaign-blocking integration bugs** plus a few correctness/robustness items. This cycle: apply the fixes, re-smoke-test locally, then **you own the upload and the submission** (the user delegated both). Paste everything below the line.

---

**You are the employee. Execute the tasks below and append a `Progress Log` entry to `3rdJ_08_simulation_2split.md` on completion.** Stay in scope; flag any blocker to the user (who relays to the manager). Do not re-litigate the locked Step-8 scope.

---

## ⚠️ CYCLE-2 UPDATE (2026-06-29) — START HERE. Parts 1–3 below are already DONE; only 8C.0 verification + the §0 gate + the campaign launch remain.

**What already happened (do NOT redo):**
- Part 1 Fixes 1–7 applied; predecessors archived. Part 2 mirrored-tree upload complete; all inputs verified present on the cluster (8A's clean run proves the bundle is intact).
- **8A historical schedules — job `1016771` COMPLETE** (6 CSVs written, all gates PASS). **Do not rerun 8A.**
- **8C.0 office IDF transition failed twice, now refixed (v3):**
  - `1016770` (v1) FAILED — the EnergyPlus **SIF has no IDFVersionUpdater/Transition binaries**; it emitted v22.1 IDFs mislabeled `_v242`.
  - `1016775` (v2) FAILED — switched to the host-side `ep_install` Transition chain, but every step died at `V22-1=>V22-2`: `Energy+.idd missing. Fullname=V22-1-0-Energy+.idd`. Root cause: the `Transition-Vxx` binaries read their version IDD from the **current working directory**, and the script `cd`s into an empty temp dir. (The "Done" list then showed stale 09:13 v1 files, so the failure masqueraded as success.)
  - **v3 fix (manager-applied, predecessor archived `archive/3rdJ_08C0_idf_transition.20260629c.sh`, already re-uploaded):** stage every `V*-Energy+.idd` into the temp dir before the chain; purge stale outputs at start; tighten the version verify to the Version object. **Resubmitted as job `1016780` — currently RUNNING. Let it finish; do NOT kill it.**

**Your job this cycle — resume from verification:**

**Step 1 — verify 8C.0 (`1016780`) when it completes** (one-shot checks, ≥30 min apart or wait for the user to relay):
```
sacct -j 1016780 --format=JobID,State,ExitCode,Elapsed
tail -40 /speed-scratch/o_iseri/step8_2split/logs/8C0_transition_1016780.out
ls -la /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_CLG /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL
```
PASS requires: the log shows **4 lines** `-> *_v242.idf (version: …24.2)` with **no** `ERROR` / `transition chain failed`, AND each output dir holds **2 `_v242.idf` files dated after the 1016780 submit** (NOT the stale 09:13 files). If 1016780 FAILED or any version isn't 24.2 → **flag the manager; do not improvise a 4th transition approach.**

**Step 2 — val §0**, then **Step 3 — Phase B arrays** on §0 PASS: follow **Part 3 → Phase B** below exactly (commands unchanged). Phase A is already done — skip it.

Append the Progress Log when done.

---

## Why this cycle exists

The scripts are individually correct, but the upload layout, the cross-script paths, and the SLURM partition don't line up, and the upload bundle omits inputs every script reads. As proposed, **8A, 8B, and the office campaign all fail.** Fix, then launch.

Read first: `3rdJ_08_simulation_2split.md` (design, §0 locked decisions) and `3rdJ_08_simulation_2split_val.md` (validation). This prompt is the execution layer; the design doc is the source of truth.

**Guardrail (every edit):** before editing any script, `cp` it to `archive/<name>.<date>.py|.sh` in the same change. Smallest practical change; preserve naming/workflow. Update the Progress Log incrementally, not at the end.

---

## PART 1 — Fixes (apply all, then re-smoke-test)

### Fix 1 — Upload must mirror the repo tree, and include the missing inputs (THE blocker)
Every script derives its paths by walking up from `__file__` assuming the repo tree is intact (`main.py:39` `BASE_DIR` = 5 levels up; `3rdJ_08A_…py:48-58`; `office_runner.py:118,129`). The array `.sh` files already `cd` to the **nested** path `…/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs` (`run_residential_array.sh:25`, `run_office_array.sh:22`). So the upload MUST recreate that tree under `upload/` — **not** the flat `upload/Step8_docs`. No script path edits are needed once the tree is correct; the only change here is how you upload (Part 2).

The bundle must also carry the inputs the scripts read (none were in the earlier proposal):
- `3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv` (8A:53-54)
- `3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell.csv` (8A:55-56)
- `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/outputs_step7/` → **all** `BEM_Schedules_2split_*.csv` and **all** `office_presence_multiplier_*.csv` (`main.py:90-98`, `office_runner.py:127-134`) — **8B cannot start without these**
- `0_Occupancy/processed/office_archetype_lookup.csv` (8A:57)
- `BEM_Setup/Buildings/CAN_CLG`, `BEM_Setup/Buildings/CAN_MTL`, `BEM_Setup/WeatherFile`
- `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242` (4 residential IDFs)

Before uploading, open those constants and `ls` the local source dirs to confirm exact filenames (e.g. whether Step-7 multipliers are a single `office_presence_multiplier_2030.csv` or per-band files) — upload whatever actually exists, don't assume.

### Fix 2 — 8C.0 must write where office_runner reads
`3rdJ_08C0_idf_transition.sh:29-30` writes to `$SCRATCH/office_idfs_v242/{CAN_CLG,CAN_MTL}/`, but `office_runner.py:104` reads from `Step8_docs/outputs_step8/office_idfs_v242/<env_family>/`. The `<env_family>` token is `CAN_CLG` / `CAN_MTL` (`office_runner.py:62-68` `CZ_MAP`), so **only the parent dir is wrong**. Repoint the transition output:
```
STEP8_DOCS=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs
OUT_CLG=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_CLG
OUT_MTL=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_MTL
```
The `_v242.idf` names already contain `TallBuilding` / `SuperTallBuilding`, matching `ENVELOPE_IDF_SUBSTR` (`office_runner.py:71-74`). Leave the input read path (`$SRC_BASE/BEM_Setup/Buildings/…`) alone — it is correct under the mirrored tree.

### Fix 3 — Residential array uses a GPU it never touches
`run_residential_array.sh:13-14` requests `-p pg --gres=gpu:1` for 168 tasks. 8B only runs EnergyPlus (CPU-only) over pre-generated schedule CSVs — no torch/CUDA anywhere in the path. Change to CPU (drop the GPU line entirely), matching the office array:
```
#SBATCH -p ps
#SBATCH --cpus-per-task=8
```
(As written it would reserve 168 GPUs and stall the whole campaign in the GPU queue.)

### Fix 4 — Submit/8A commands must use the nested path
The earlier run commands pointed at the flat `upload/Step8_docs/…`. With the mirrored tree they must be `upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/…` (exact commands in Part 3).

### Fix 5 — Module precheck in each wrapper
Add a precheck line at the top of each `.sh` run body (and the 8A `--wrap`), so a missing dep fails fast instead of mid-array:
```
/speed-scratch/o_iseri/envs/step4/bin/python -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
```

### Fix 6 — `"Tall"` substring also matches `"SuperTall"` (correctness)
`office_runner.py:72` matches the `Tall` envelope by substring `"TallBuilding"`, but `"SuperTallBuilding"` **contains** `"TallBuilding"`. Depending on `_find_one`'s ordering this can silently run SuperTall geometry for the 126 `Tall` cells. Anchor it: match the basename that **starts with** `TallBuilding` (or exclude names containing `Super`) for the `Tall` envelope. Add a 1-line smoke assertion that `Tall`≠`SuperTall` resolves to different files.

### Fix 7 — leave a guard comment (low priority)
`get_region_from_epw()` (`main.py:168`) still returns `"Alberta"` for Calgary. It's harmless today only because 8B passes `city["region"]` (`"Prairies"`, `main.py:117`) straight into `run_step8_paired_mc` (`3rdJ_08B_…py:192`). Add a one-line comment at `main.py:168` warning not to route the Step-8 pool filter through `get_region_from_epw`, so nobody reintroduces the empty-pool bug. (The Calgary→Prairies fix itself is correct — the 3J stock `PR` has no "Alberta"; AB folds into "Prairies", `3rdJ_08A_…py:88-91`.)

### Re-smoke-test (gate before upload)
After the fixes, re-run the tiny local smoke (1 office archetype × 1 envelope × 1 CZ × 1 scenario; 1 resid arch × 1 CZ × 2 scen × N=2) and confirm: office_runner finds the v242 IDF in the new dir and picks the right Tall/SuperTall file; residential still produces a valid 8760-row `hourly_meters.csv`. Only upload once this passes.

---

## PART 2 — Upload (you run this; one cycle, mirrored tree)

All `mkdir`/`scp`/`ssh` here are login-node-safe. **Cluster — create the target tree first** (one line):
```
ssh o_iseri@speed.encs.concordia.ca "mkdir -p /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/outputs_step5 /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/outputs_step6 /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/outputs_step7 /speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/Buildings /speed-scratch/o_iseri/step8_2split/upload/2J_docs_occ_nTemp/BEM_setup /speed-scratch/o_iseri/step8_2split/upload/0_Occupancy/processed /speed-scratch/o_iseri/step8_2split/logs"
```
**Locally — Step8_docs (with the fixed scripts) into the nested slot:**
```
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step8_docs" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/
```
**Locally — the single-file inputs (one target each):**
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Aggregated_excl.csv" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/outputs_step5/
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell.csv" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/outputs_step6/
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\0_Occupancy\processed\office_archetype_lookup.csv" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/0_Occupancy/processed/
```
**Locally — all Step-7 schedule + multiplier CSVs** (`ls` the dir first; adjust the name list to what exists — ForEach pattern, no brace expansion):
```
"BEM_Schedules_2split_2022","BEM_Schedules_2split_2030_conservative","BEM_Schedules_2split_2030_hybrid","BEM_Schedules_2split_2030_fullyhybrid","office_presence_multiplier_2022","office_presence_multiplier_2030" | ForEach-Object { scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step7_docs\outputs_step7\$_.csv" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/outputs_step7/ }
```
**Locally — BEM_Setup + residential IDFs (recursive, one target each):**
```
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\Buildings\CAN_CLG" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/Buildings/
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\Buildings\CAN_MTL" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/Buildings/
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\WeatherFile" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\BEM_setup\Buildings_MTL_v242" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/2J_docs_occ_nTemp/BEM_setup/
```
**Verify (cluster, single `ls`):** confirm each input landed at its mirrored path before submitting. If any `scp` line errors on Windows path quoting, fall back to the per-file ForEach form for that line.

---

## PART 3 — Submit (you run this; sbatch only, two phases)

### Phase A — gating jobs (independent, run in parallel)
> **⛔ CYCLE-2: Phase A is ALREADY DONE. Do NOT run these.** 8A = `1016771` COMPLETE; 8C.0 = `1016780` RUNNING (refixed v3). Re-running these would duplicate-submit 8C.0 and overwrite 8A. Go to Phase B. The two commands below are kept for the record only.
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08C0_idf_transition.sh
```
```
sbatch -p ps --mem=32G -t 7-00:00:00 --output=/speed-scratch/o_iseri/step8_2split/logs/8A_%j.out --wrap "cd /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs && /speed-scratch/o_iseri/envs/step4/bin/python 3rdJ_08A_gen_historical_schedules.py --year all > /speed-scratch/o_iseri/step8_2split/logs/8A_gen.out"
```
Record both job IDs, **report them to the user, and pause.** Do not poll in a loop — when both complete (check no sooner than 30 min apart, or wait for the user to relay), proceed.

### Phase B — validation gate, then the campaigns
1. Confirm 8C.0 produced 4 `_v242.idf` files under `…/Step8_docs/outputs_step8/office_idfs_v242/{CAN_CLG,CAN_MTL}/` (single `ls`), and that the 8A log reports 6 CSVs written with 0 transition errors.
2. Run val **§0** on the 8A output **via sbatch** (no bare python on the login node) — schema, row counts, calibration provenance, longitudinal continuity (no `2015≈2022` leakage), no NaN. Example:
```
sbatch -p ps --mem=16G -t 7-00:00:00 --output=/speed-scratch/o_iseri/step8_2split/logs/8A_val_%j.out --wrap "cd /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs && /speed-scratch/o_iseri/envs/step4/bin/python 3rdJ_08_simulation_2split_val.py --section 0 > /speed-scratch/o_iseri/step8_2split/logs/8A_val.out"
```
(If the validator has no `--section` flag, add a §0-only entry point or a small standalone schema/continuity check — don't skip the gate.)
3. **Only if §0 PASSes**, launch both campaigns (independent of each other; both already have their gating inputs):
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_residential_array.sh
```
```
sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_array.sh
```
Record the array job IDs, report to the user, and stop. The full §1–§8 validation runs after the arrays finish (separate cycle).

---

## Cluster hard rules (account-suspension risk — NON-NEGOTIABLE)
1. **`sbatch` ONLY.** No `srun`, no bare `python`/`python3` on the login node `speed-submit2` — not even one-liners (flagged 3×; one more = suspension = all progress lost). `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `ssh`-`mkdir`, `cd`, `ls`, `scp`, single-file `tail`/`cat` are the only login-node actions.
2. Every job `-t 7-00:00:00` (7-day) minimum walltime — already set in all `.sh`; keep it in the `--wrap` jobs too.
3. Login shell is `tcsh`: single-line commands, no `\` continuation, no `2>&1` (use `>` only; SLURM captures stderr to `--output`).
4. **No tight polling.** Submit, report job IDs, wait ≥30 min between checks — prefer letting the user relay completion. SLURM finishing does not need watching.

## Deliverables checklist
- [x] Fixes 1–7 applied; predecessors archived; local smoke re-passes (office Tall≠SuperTall confirmed)
- [x] Mirrored-tree upload complete; every input verified present on the cluster
- [x] Phase A submitted; 8A `1016771` COMPLETE; 8C.0 refixed (v3) and resubmitted as `1016780`
- [x] **8C.0 `1016780` verified — 4 fresh `_v242.idf`, all Version 24.2, no transition errors** (Cycle-2 Step 1)
- [x] Val §0 PASS confirmed — Job `1016796`, 13 PASS / 0 WARN / 2 INFO / 0 FAIL
- [x] Phase B submitted — residential `1016804` (168 tasks, ps), office `1016809` (252 tasks, ps)
- [x] `Progress Log` entry appended to `3rdJ_08_simulation_2split.md` (Cycle-2 session, §0 scorecard, Phase B job IDs)

Flag any blocker (missing input file, §0 FAIL, transition error, dep missing, ambiguous zone tag) to the user before proceeding past it.
