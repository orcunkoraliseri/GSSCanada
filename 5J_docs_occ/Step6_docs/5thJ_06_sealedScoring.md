# Step 6 — WP4: one scoring of the sealed test sets (RQ1 to RQ3)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 6. Validation: `5thJ_06_sealedScoring_val.md`

Written 2026-09-28. Week 4 (19 to 25 Oct 2026).

---

## STATUS

🟢 CLOSED (2026-10-01 04:16 EDT): one scoring done (job 1405205), every verdict as printed in `outputs_step6/RESULTS.md`; manager re-derived (job 1405218). Before: ⬜ NOT STARTED. Needs Step 5 closed (winner and control pinned).

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
| New country | G5J.6 | two leave-one-country-out folds (train ES score IT; train IT score ES; rules R9, note 2026-09-30 21:14) | run and pair, reported |

Every metric states its level (lesson 5).

## 6B. HOW

* One `sbatch` job runs the frozen scorer (md5 checked at start, printed, checked PRESENT) on all models
  and splits and writes `outputs_step6/scores.parquet` and `outputs_step6/SUMMARY.txt` with one line per
  gate, split, class and end use, each PASS, FAIL or NOT_EVALUABLE, plus the exit code as defined in Step 4.
* The job is submitted once. If it crashes, the crashed sections are NOT_EVALUABLE; a rerun of the same
  frozen code on the same inputs is allowed and logged in the ledger with the crash line; any code change
  is a new, dated amendment written before the rerun, with its reason.
* UK results: the SUMMARY is split per country; the UK part is handled as O-7 decides (Step 3, 3E).
  (Manager note 2026-09-30 21:14 EDT: the run campaign is Spain + Italy only, so no UK line is scored here.)

## 6C. AFTER SCORING

* The manager re-derives three numbers from `scores.parquet` (validation doc, section 5).
* Results go into the parent Progress Log as written by the scorer, with no rewording of verdicts.
* A result that contradicts its mechanism (for example, the blind control beating S) is checked for a
  method error first (failure class: sign opposite to the mechanism), and the check is written down;
  the verdict stays as recorded unless a bug is proved.

## 6D. CLAIM RULE AND REPORTING ADDITIONS (manager, 2026-09-30 21:25 EDT, from `date`)

Written before any test prediction, test score or pinned winner exists (Step 5 grid re-running; no test file opened). It
changes no gate, threshold or scorer line; it fixes in advance what the paper may SAY from the gate lines (3J/4J setup review,
`Prompts/manager/2026-09-30_setup_check_3J_4J.md`, issues 1, 2, 3, 5, 7).

* **Claim per end use and test list.** For each target (heating, cooling, equipment, total electricity) and each test list,
  count S's G5J.3 PASS lines over its 8 cells (2 countries x 4 classes). "Holds" = at least 6 of 8 AND at least 3 of 4 in each
  country; "partly" = 3 to 5 of 8 (or 6+ with one country below 3 of 4); "does not hold" = 2 or fewer. A NOT_EVALUABLE cell
  counts as not passed and is listed by name. If G5J.4 prints FLAGGED FOR WITHDRAWAL (the blind control passes) in 2 or more of
  the 8 cells, the claim for that target and list is withdrawn whatever the count.
* **Headline order.** The abstract and conclusion state heating and cooling first, on `test_both_new` (new households in new
  buildings, the case a stock model meets), then `test_new_households` and `test_new_buildings`. Equipment and total
  electricity are reported in their own sentence: their hourly values follow the input schedule, so passing them says little
  about the building physics. Every target x list verdict is tabled, whatever the outcome.
* **Uncertainty units.** Every bootstrap interval is printed with the number of building units and household units of its
  cell; where the cell holds one building, the text says the interval reflects households only.
* **Asymmetries stated in Methods.** B1 is tuned on hourly error only while S also sees a pair term and is chosen on it; the
  country-out configuration was chosen on validation data that include the held-out country.
* **Level versus timing (reported, not gated; Step 6 part C).** Two households differ in size and appliance level as well as
  in timing. Part C reports, per cell, the share of the variance of the EnergyPlus annual pair effect explained by the pair's
  difference in annual mean people-at-home and in annual appliance energy (a regression on the truth), and the same for S's
  annual pair effect. A "timing-only" control (drivers replaced by their annual mean) is NOT added: constant drivers lie far
  outside anything S was trained on, so its score would measure extrapolation, not timing.
* **Weekday of the run year (review issue 7c, checked 21:26).** Every campaign IDF says `Sunday` as the start weekday
  (`tools/5thJ_idf_mz.py:435-437`), while 1 January is a Friday in 2010 (Spain) and a Wednesday in 2014 (Italy). It changes no
  result: every schedule is either an 8,760-hour file built on the diary calendar or a constant (`:410-413, 443, 455-456`),
  weather-file holidays are off, and nothing in the IDF reads the weekday. The surrogate gets the true diary weekday
  (rules R2). The paper says this in one Methods sentence.
* **What "new household" means (review issue 6, answered 21:26, `Prompts/manager/2026-09-30_household_day_overlap.md`).**
  A 5J household keeps its real HETUS composition, but every person-day is drawn with replacement from ONE pool of 5,200
  generated days per country (4J model output), shared by all splits. So a test household is a new composition and a new
  sequence of days, not new day content: training households used many of the same generated days. This is not a leak of the
  scored truth (the schedule is an input to both EnergyPlus and S; the target is the EnergyPlus response on that building,
  weather and calendar), but it limits the claim: S is shown to generalise to new households drawn from the same day
  distribution, not to unseen behaviour. The paper says this in Methods and Limitations. Part C reports, per country, the share
  of test person-days whose pool day was also used by a development household (replay of the draws; check the replay
  reproduces 3 shipped presence files by md5 first).
* **Seed spread on test (added 2026-10-01 02:05 EDT, before any test prediction or score).** On validation the pinned S3
  (seed 1) passes G5J.3 in 30/32 cells, but the same configuration retrained with seed 2 / seed 3 passes 22 / 13 (median
  heating+cooling R² 0.82 / 0.73 / 0.67; seeds 2 and 3 early-stopped at epochs 4 and 2; job 1405056). Part of the winner's
  validation margin is therefore seed luck plus selection on the same validation set. So S_seed2 and S_seed3 are ALSO
  predicted and scored on the three test lists, REPORTED next to S3 (same scorer, same B1 and C), never gated and never used
  to change the claim, which stays on the pinned S3 (6D claim rule). The paper reports the three-seed range for every
  claim cell and says the configuration's result depends on the seed.
* **Test-open record.** Part B's collect job counts, from the scorer's `openlog_<tag>.tsv` files, every test-truth file
  opened and by which job; the count must equal the runs of the scored lists, all from the ONE scoring job.

## OUTPUTS

`outputs_step6/scores.parquet`, `SUMMARY.txt`, `bootstrap_intervals.csv`, `impl/<date>_wp4_scoring.md`.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 5.
- 2026-10-01 04:16 EDT (manager): Step 6 CLOSED. Scorer test mode = gates_frozen §8 amendment (locked 02:16, before any test
  prediction); reported analyses locked (v2) before scoring; ONE scoring job 1405205. S (pinned S3): G5J.3 31/32 new households,
  31/32 new buildings, 26/28 both new (+4 NOT_EVALUABLE); G5J.2 21 / 14 / 14 of 32; G5J.5 8/8 each; C fails G5J.3 everywhere
  (G5J.4 PASS). 6D claims hold in 11 of 12 target x list cases (heating on both-new: partly). Seeds 2/3 of the same
  configuration do much worse (G5J.3 11-23 cells), so the claim belongs to the pinned model. New country: Spain -> Italy fails
  (G5J.3 0-3 of 16), Italy -> Spain partly (9-10 of 16). Full record: `outputs_step6/RESULTS.md`. Next: Step 7.
- 2026-10-01 05:04 EDT (manager): post-scoring rule for Step 8 figures. The verdicts are recorded (04:16) and nothing is trained,
  tuned or re-scored after them. Figure-data jobs may now read test truth and test predictions to draw the frozen results
  (e.g. annual pair effects of S, C and EnergyPlus for the key figure), each in a Speed job that logs every file it opens and
  writes the md5 of its output table; no figure-data job may write a verdict, a gate line or a score, and any number it shows
  that is also a scored number must equal `outputs_step6/scores.parquet`.
