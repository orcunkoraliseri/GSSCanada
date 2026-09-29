# Validation plan — Step 7 (WP5 district and speed)

### 5J occupancy-aware surrogate. Main doc: `5thJ_07_speedDistrict.md`

Written 2026-09-28.

---

## Section 1 — Draws

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Draw count written equals draws scored | equal | FAIL |
| 1.2 | Household size distribution over draws matches the weighted survey distribution | within 2 points per size | WARN |
| 1.3 | Two draws with different seeds give different district totals | yes | FAIL (occupancy not reaching the model) |
| 1.4 | Interval stability: the 90 % interval from the first half of draws is within 5 % of the full one | yes | WARN |

## Section 2 — Range

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | Count and share of out-of-range dwellings reported | reported | FAIL if missing |
| 2.2 | Errors in 7C reported separately for in-range and out-of-range | both | FAIL |

## Section 3 — EnergyPlus subsample

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | Every subsample run passes the G5J.1 checks | all | FAIL |
| 3.2 | Subsample draws picked by a recorded seed, before the surrogate was run on them | yes | FAIL |

## Section 4 — Speed

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | Times read from job clock lines on the same node type, the node names recorded | yes | FAIL |
| 4.2 | Surrogate time includes loading inputs and writing outputs, stated | yes | FAIL |

## Section 5 — Before the GPU ends

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 5.1 | Checkpoints copied off Speed, md5s equal on both sides | equal | FAIL |
| 5.2 | UK-trained weights stored only where the licence allows, location written | yes | FAIL |

## Section 6 — Seen failing

* 1.3: run with the same seed twice; the check must FAIL.
* 5.1: compare against a truncated scratch copy of one checkpoint; the check must FAIL.
