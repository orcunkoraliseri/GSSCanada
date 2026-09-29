# Validation plan — Step 5 (WP3 baselines and surrogate)

### 5J occupancy-aware surrogate. Main doc: `5thJ_05_surrogateTraining.md`

Written 2026-09-28.

---

## Section 1 — No leakage

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Test reader log: 0 test files opened during Step 5 | 0 | FAIL; a leak cannot be undone, so it is written up and reported in the paper |
| 1.2 | No EnergyPlus output column among model inputs (feature list read from the saved config) | 0 | FAIL |
| 1.3 | No household or building ID in both training and validation batches | 0 | FAIL |
| 1.4 | Leave-one-country-out folds: no field that only one country records; climate ID dropped | yes | FAIL |

## Section 2 — Training sanity

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | Training loss falls; validation loss recorded per epoch | yes | FAIL |
| 2.2 | S beats "predict the training mean" on validation load score | yes | FAIL (the model learned nothing) |
| 2.3 | Output shapes 24 × 3 per window; annual reconstruction = 8,760 hours per run | exact | FAIL |
| 2.4 | Seed spread of S on validation G5J.3 R² reported (three seeds) | reported | INFO |

## Section 3 — Blind control is blind

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | In C's training data, correlation between a run's presence channel and its own electricity is no higher than with a random run's (spot check on 100 runs) | yes | FAIL |
| 3.2 | C and S share configuration and seed (config diff shows only the shuffle flag) | yes | FAIL |

## Section 4 — Pinning

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | Winner rule written before training (file time and md5 earlier than the first training job) | yes | FAIL |
| 4.2 | Winner's code hash, seed and checkpoint md5 recorded and re-computed | equal | FAIL |
| 4.3 | Reloaded checkpoint reproduces the validation score to 4 decimals | yes | FAIL |

## Section 5 — Seen failing

* 1.2: add an EnergyPlus output column to a scratch config; 1.2 must FAIL.
* 1.1: call the test reader once in a scratch run before the freeze file is present; it must refuse and log.
* 3.1: run the check on S's (unshuffled) data; it must FAIL.

## Section 6 — Manager re-derivation

The manager reloads the winner checkpoint for one Spain validation run (not UK) and recomputes its
hourly CV(RMSE) for electricity from the saved prediction file.
