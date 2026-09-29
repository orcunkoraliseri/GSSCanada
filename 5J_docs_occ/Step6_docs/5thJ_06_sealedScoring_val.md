# Validation plan — Step 6 (WP4 one scoring)

### 5J occupancy-aware surrogate. Main doc: `5thJ_06_sealedScoring.md`

Written 2026-09-28.

---

## Section 1 — The scoring is the frozen one

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Scorer md5 printed at start equals the Step 4 md5 | equal | FAIL |
| 1.2 | Model checkpoint md5s printed equal the Step 5 pins | equal | FAIL |
| 1.3 | Split md5s printed equal the Step 3 seals | equal | FAIL |
| 1.4 | Number of scoring jobs in the ledger = 1, or each extra one has its crash line and amendment | yes | FAIL |

## Section 2 — Completeness of the SUMMARY

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | One line per gate × split × class × end use, none missing | all | FAIL |
| 2.2 | Every line reads PASS, FAIL or NOT_EVALUABLE; exit code consistent with the lines | yes | FAIL |
| 2.3 | NOT_EVALUABLE lines give their reason (below noise floor, fewer than 30 pairs, crashed) | all | FAIL |

## Section 3 — Plausibility

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | B0's G5J.3 R² is about 0 (it predicts no occupancy effect) | |R²| < 0.05 | FAIL (scorer suspect) |
| 3.2 | C's G5J.3 is lower than S's | reported | INFO; if not, method checked first (6C) |
| 3.3 | Bootstrap intervals widen for smaller classes | yes | WARN |

## Section 4 — Seen failing (before the real run, on validation, with the frozen scorer)

These were already seen in Step 4. Here only 1.1 to 1.3 are seen failing: run the start-up checks
against a scratch copy with one md5 changed; the job must stop before scoring.

## Section 5 — Manager re-derivation (Spain or Italy only)

* One run's hourly CV(RMSE) for electricity recomputed from the saved predictions and the EnergyPlus file.
* One pair's annual difference sign for S and for EnergyPlus recomputed.
* One class's G5J.3 R² recomputed from `scores.parquet` rows.
