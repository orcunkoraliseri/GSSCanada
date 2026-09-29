# Step 6 — WP4: one scoring of the sealed test sets (RQ1 to RQ3)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 6. Validation: `5thJ_06_sealedScoring_val.md`

Written 2026-09-28. Week 4 (19 to 25 Oct 2026).

---

## STATUS

⬜ NOT STARTED. Needs Step 5 closed (winner and control pinned).

## AIM

Score B0, B1, the pinned S and control C **once** on the sealed test splits with the frozen scorer, and
report every verdict as it comes out. Nothing is re-trained or re-tuned after this step starts.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| Frozen scorer and thresholds (md5 in the parent Step 4 box) | Step 4 |
| One scoring; a gate verdict stays as recorded | Parent, validation plan |
| Occupancy effect per end use and per dwelling class; bootstrap by building and household | Step 4, lessons 3, 4, 15 |
| If C passes G5J.3, G5J.3 is withdrawn and the paper says so | G5J.4 |

## 6A. WHAT IS SCORED

| Question | Gate | Splits | Level |
|---|---|---|---|
| RQ1 load accuracy | G5J.2 | new households, new buildings, both new | run, per target, per class |
| RQ2 occupancy effect | G5J.3 | pairs inside each test split | pair, per end use, per class |
| RQ2 blind control | G5J.4 | same as G5J.3, for C | pair |
| RQ3 peaks | G5J.5 | new households, new buildings | day |
| RQ3 thermal-mass lag | reported | new buildings | run: lag of the peak cross-correlation of presence and heating, S against EnergyPlus |
| RQ3 mild-climate cooling | reported | per climate | run |
| New country | G5J.6 | three leave-one-country-out folds | run and pair, reported |

Every metric states its level (lesson 5).

## 6B. HOW

* One `sbatch` job runs the frozen scorer (md5 checked at start, printed, checked PRESENT) on all models
  and splits and writes `outputs_step6/scores.parquet` and `outputs_step6/SUMMARY.txt` with one line per
  gate, split, class and end use, each PASS, FAIL or NOT_EVALUABLE, plus the exit code as defined in Step 4.
* The job is submitted once. If it crashes, the crashed sections are NOT_EVALUABLE; a rerun of the same
  frozen code on the same inputs is allowed and logged in the ledger with the crash line; any code change
  is a new, dated amendment written before the rerun, with its reason.
* UK results: the SUMMARY is split per country; the UK part is handled as O-7 decides (Step 3, 3E).

## 6C. AFTER SCORING

* The manager re-derives three numbers from `scores.parquet` (validation doc, section 5).
* Results go into the parent Progress Log as written by the scorer, with no rewording of verdicts.
* A result that contradicts its mechanism (for example, the blind control beating S) is checked for a
  method error first (failure class: sign opposite to the mechanism), and the check is written down;
  the verdict stays as recorded unless a bug is proved.

## OUTPUTS

`outputs_step6/scores.parquet`, `SUMMARY.txt`, `bootstrap_intervals.csv`, `impl/<date>_wp4_scoring.md`.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 5.
