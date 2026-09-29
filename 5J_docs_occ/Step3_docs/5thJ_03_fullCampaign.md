# Step 3 — WP2: full campaign on Speed (CPU)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 3. Validation: `5thJ_03_fullCampaign_val.md`

Written 2026-09-28. Week 2 (5 to 11 Oct 2026).

---

## STATUS

⬜ NOT STARTED. Needs Step 2 closed: design frozen, pilot passed, size set, CPU share agreed.

## AIM

Run every planned EnergyPlus run of `../Step2_docs/outputs_step2/campaign_design.md`, check each one,
extract the hourly targets, and seal the splits so no model can see a test run before the gates are
frozen (Step 4).

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| `sbatch` only, 7-day walltime, `--exclude=antenna1` | CLAUDE.md, lesson 11 |
| Run count = plan count from Step 2; any shortfall is repaired, never ignored | G5J.1 |
| Households and buildings never cross splits | Parent Step 3 |
| No model sees a test file before Step 4 is ticked | Parent Step 3 |

## 3A. SUBMISSION

* One array per country and climate (9 arrays), throttled so the running CPUs stay under the agreed
  share. Task = a block of runs (block size from the pilot so a task lasts 1 to 4 hours).
* Before each array: disk preflight job prints free space; the array starts only if free space covers
  the plan (Step 2, 2C). The preflight line is printed and checked PRESENT (failure class 58).
* Each task: builds the IDF and schedules for its runs (cached by input hash, lesson 7), runs
  EnergyPlus in its own `run_dir` (lesson 8), extracts the hourly targets, checks them, deletes the raw
  folder only after the check passes, and appends one line per run to the task's manifest.
* 🔴 UK arrays: the job builds UK schedules from the diaries itself. The assistant writes and submits the
  code but never opens UK schedules, IDFs, outputs or per-run manifests (UK rule, Step 1 doc).

## 3B. LEDGER (append-only, `impl/<date>_wp2_campaign.md`)

One line per job: JobID · array · what · state · exit · output path. A failed task stays in the ledger
with the line of the task that replaced it.

## 3C. CHECKS DURING THE CAMPAIGN

* G5J.1 per task (by the job, printed as one SUMMARY line with three outcomes: did not run / ran and
  failed / ran and passed): run present, "Completed Successfully", 0 severe, 8,760 rows per target, annual
  = hourly sum, outputs differ from the previous household on the same building.
* Resume check (failure class 61): move one finished task's outputs away; the plan tool must count those
  runs as missing and the plan count must drop by exactly that number; move them back.
* Truncated output check (1J lesson, antenna1): size and md5 of every extracted file recorded.

## 3D. SPLITS AND SEAL

After G5J.1 passes on all arrays:
* Write the split files (`development`, `validation`, `test_new_households`, `test_new_buildings`,
  `test_both_new`, and the three leave-one-country-out folds) as lists of `run_id`, from the Step 2 split
  tables.
* Make them read-only (`chmod a-w` on Speed), write each md5 in the parent checklist Step 3 box, and copy
  the md5 list into this doc's Progress Log.
* The training code reads a test file only through a function that refuses unless the file
  `gates_frozen.md5` from Step 4 exists (the refusal is seen failing in Step 4).

## 3E. OPEN ITEM (UK aggregate results, O-7)

The assistant must never open UK-derived files. The gate SUMMARY lines of UK arrays are UK-derived too.
Until the author rules, the UK SUMMARY lines are read by the author (one `grep SUMMARY` line given to
them) and pasted back as pass/fail and counts only. The simplest clean route is written permission from
UKDS for the assistant to see aggregate gate results; that is the author's call.

## OUTPUTS

| Where | What |
|---|---|
| `/speed-scratch/o_iseri/5J/campaign/extracted/` | Hourly targets, one parquet per task |
| `/speed-scratch/o_iseri/5J/campaign/manifests/` | Run manifests (inputs by hash) |
| `/speed-scratch/o_iseri/5J/splits/` | Sealed split files |
| `impl/<date>_wp2_campaign.md` | Ledger and state |

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 2.
