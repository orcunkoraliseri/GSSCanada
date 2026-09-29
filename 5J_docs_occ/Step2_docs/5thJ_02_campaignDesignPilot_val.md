# Validation plan — Step 2 (WP1 campaign design and pilot)

### 5J occupancy-aware surrogate. Main doc: `5thJ_02_campaignDesignPilot.md`

Written 2026-09-28. Every check prints its own line; a check that did not run prints NOT_EVALUABLE.

---

## Section 1 — Design tables

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Every building parameter inside the TABULA range for its country and class | 0 outside | FAIL |
| 1.2 | Every dwelling class present in every split (development, validation, test) per country | all | FAIL |
| 1.3 | Household table: same household IDs listed for every building of a country | exact | FAIL |
| 1.4 | Weighted household draw: size distribution of the 60 against the weighted survey distribution | reported | INFO |
| 1.5 | Each climate has an EPW whose year matches the diary year used in 4J | all | FAIL |
| 1.6 | md5 of each table written in `campaign_design.md` and re-computed | equal | FAIL |

## Section 2 — Pilot integrity (50 runs)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | 50 of 50 run folders or extracted rows present | 50 | FAIL |
| 2.2 | "EnergyPlus Completed Successfully" and 0 severe in every `eplusout.err` | 50 | FAIL |
| 2.3 | 8,760 hourly rows per target per run | all | FAIL |
| 2.4 | Annual sum equals hourly sum, per target | abs diff < 0.1 % | FAIL |
| 2.5 | Run manifest has every field of 2A, clock origin = midnight | all | FAIL |

## Section 3 — Occupancy actually reaches the model (lesson 6)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | On each building, hourly electricity differs between any two different households | all pairs differ | FAIL |
| 3.2 | Same for heating (or cooling where heating is zero) | reported per class | WARN if identical |
| 3.3 | Two repeats of one input: difference per target reported (noise floor first look) | reported | INFO |
| 3.4 | Schedule md5 differs between households and is identical between repeats | exact | FAIL |

## Section 4 — Physics plausibility (lesson 9)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | Annual heating per m² per class, in the range 4J reported for the same archetype and weather | inside or explained | WARN |
| 4.2 | Cooling is zero where the system has no cooling; no cooling in heating-only months from heat recovery | as expected | FAIL |
| 4.3 | Electricity mean over hours of presence > mean over hours of absence, per household | ≥ 90 % of households | WARN |

## Section 5 — Size arithmetic

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 5.1 | CPU-hours and wall time computed from the measured median, written with the formula | present | FAIL |
| 5.2 | Disk plan below free space read by the disk preflight at submit time | yes | FAIL |
| 5.3 | Finish date at the agreed CPU share on or before 11 Oct 2026, or the cut order of 2E applied | yes | FAIL |

## Section 6 — Seen failing

* 3.1: re-run the check with one household's schedule copied onto another; it must FAIL.
* 2.2: point the check at a copy of one `eplusout.err` with a planted "** Severe **" line; it must FAIL.
* 2.4: scale one hourly series by 1.01 in a scratch copy; it must FAIL.
* 1.1: plant one value outside the range in a scratch copy of `buildings.csv`; it must FAIL.

## Section 7 — Manager re-derivation

One run's hourly electricity read from the extracted file and its annual sum computed by the manager;
one building row checked against the TABULA table by hand; the median time per run re-computed from the
job log times.
