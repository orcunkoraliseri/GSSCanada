# Validation plan — Step 3 (WP2 full campaign)

### 5J occupancy-aware surrogate. Main doc: `5thJ_03_fullCampaign.md`

Written 2026-09-28.

---

## Section 1 — G5J.1 campaign integrity (gate)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Runs present = plan count, per country, climate and building | equal | FAIL |
| 1.2 | "EnergyPlus Completed Successfully" in every run's error file (checked by the job before deleting raw) | all | FAIL |
| 1.3 | 0 severe errors | all | FAIL |
| 1.4 | 8,760 rows per target per run | all | FAIL |
| 1.5 | A run that exited 0 but wrote nothing is caught (row count or file size 0) | caught | FAIL |
| 1.6 | Every task printed its SUMMARY line; a missing line is NOT_EVALUABLE for that task, never PASS | all present | FAIL |

## Section 2 — Occupancy differences survive (lesson 6)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | Per building, hourly electricity of any two different households differs | all | FAIL |
| 2.2 | Schedule md5 per household constant across buildings of a country (same households everywhere) | exact | FAIL |
| 2.3 | Replicates: repeat spread per target written; this is the noise floor handed to Step 4 | written | FAIL if missing |

## Section 3 — Resume and cache

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | Outputs moved away → plan count drops by exactly the moved number → moved back → count restored | exact | FAIL |
| 3.2 | Cache: one input changed → key changes → MISS; unchanged → HIT | both seen | FAIL |

## Section 4 — Splits sealed

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | No household ID and no building ID appears in two of development, validation, test | 0 | FAIL |
| 4.2 | Every run in exactly one split (per fold for leave-one-country-out) | exact | FAIL |
| 4.3 | Split files read-only; md5 written in the parent checklist | yes | FAIL |
| 4.4 | Both members of every scoring pair are in the same split | all | FAIL |

## Section 5 — Seen failing

* 1.1: remove one run's output from a scratch copy of the index; count must drop and 1.1 FAIL.
* 1.5: an empty extracted file planted in a scratch folder; 1.5 must FAIL.
* 4.1: one household ID copied into the test list of a scratch copy; 4.1 must FAIL.
* 1.6: one SUMMARY line deleted from a scratch copy of a log; the task must read NOT_EVALUABLE.

## Section 6 — Manager re-derivation

For Spain and Italy only (UK rule): one run per country re-read from the extracted parquet (row count,
annual sum); one split file md5 re-computed; the ledger count of COMPLETED tasks against `sacct`.
