# Step 4 — Freeze the gates (before any test row is scored)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 4. Validation: `5thJ_04_freezeGates_val.md`

Written 2026-09-28. Runs at the end of week 2, before any training result is looked at on a test split.

---

## STATUS

⬜ NOT STARTED. Needs Step 3 closed (campaign complete, splits sealed, noise floor written).

## AIM

Turn every DRAFT threshold of the Overview into a frozen rule, written once, checksummed, and seen
failing, so no threshold is chosen after a result is known.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| Gates G5J.1 to G5J.7 and their meaning | Overview, validation gates |
| A gate counts only after it has been seen failing | Parent, validation plan |
| A band is used only after its source is opened (lesson 16) | Parent, lessons |
| Three outcomes kept apart in the SUMMARY and the exit code (lesson 16) | Parent, lessons |
| Occupancy effect scored per end use and per dwelling class, never pooled (lessons 3, 4) | Parent, lessons |

## 4A. DEFINITIONS (written into `outputs_step4/gates_frozen.md`)

* **Load score (G5J.2).** Per run and target: hourly CV(RMSE) and NMBE of the surrogate against
  EnergyPlus; reported as the median and the share of runs inside the band, per split and per class.
  DRAFT band: CV(RMSE) ≤ 30 % and |NMBE| ≤ 10 % (ASHRAE Guideline 14, hourly calibration). 🔴 The
  guideline text (or a peer-reviewed paper quoting it with page) is opened and the page cited in this doc
  before the band is frozen; it is labelled "a reference", since G14 is for measured data.
* **Occupancy effect (G5J.3).** For a pair (households A, B; one building; one weather):
  ΔEP(t) = EP_A(t) − EP_B(t), ΔS(t) = S_A(t) − S_B(t). Scores: R² of ΔS against ΔEP over the hours of
  all pairs of a class; annual sign agreement (sign of ΣΔS = sign of ΣΔEP) over pairs above the noise
  floor; skill over B1 = R²(S) − R²(B1) with a cluster-bootstrap 95 % interval.
  DRAFT pass: R² ≥ 0.5, sign agreement ≥ 80 %, interval of the skill over B1 excludes 0.
* **Noise floor.** From the Step 3 replicates: per target and class, the standard deviation of the annual
  total over repeats of one input. A pair is "above the floor" when |ΣΔEP| > k × √2 × floor, DRAFT k = 2.
  A class and end use with fewer than 30 pairs above the floor is NOT_EVALUABLE for G5J.3.
* **Blind control (G5J.4).** Control C = model S retrained with each run's occupancy channels replaced
  by those of a random other run of the same country (the building and weather stay; the link is
  broken). Pass for the paper = C **fails** G5J.3. If C passes, G5J.3 is withdrawn and the paper says so.
* **Peaks (G5J.5).** Daily electricity peak hour of S within ±1 h of EnergyPlus on ≥ 70 % of days (DRAFT).
* **New country (G5J.6)** and **speed (G5J.7)**: reported, not gated.
* **Bootstrap.** Two-way cluster bootstrap: buildings and households resampled independently, pairs kept
  where both members were drawn; 2,000 resamples; seed fixed. Never by hour or run (lesson 15). The null
  is simulated under the same design once, to check the interval covers 0 when S = B1.

## 4B. PERTURBATION TABLE (`outputs_step4/perturbations.md`)

One named perturbation breaks exactly one gate, run on the **validation** split only. No trained model
exists yet, so the stand-in predictors are built from EnergyPlus itself: "good" = the EnergyPlus output
plus small noise (drawn at the size of the noise floor), which must pass every gate.

| Perturbation of the "good" stand-in | Must break |
|---|---|
| Delete one run's output from a scratch copy | G5J.1 |
| Prediction replaced by the training mean per hour of year | G5J.2 |
| Prediction for every household = the hourly mean of all households on that building (occupancy effect set to zero, load level kept) | G5J.3 (whether G5J.2 still passes is reported, not required) |
| Prediction shifted by 2 hours | G5J.5 |
| G5J.4 given the "good" stand-in as its control | G5J.4 reads "control passes", so G5J.3 is flagged for withdrawal |

The G5J.3 row is the important one. Whether this occupancy-blind stand-in still passes the load band is
the paper's premise ("a surrogate can match the load while ignoring occupancy"), measured here on
validation data before any model exists; it is written down either way.

Each row: the gate verdict before and after, and the line that printed it.

## 4C. FREEZE

* Frozen file `outputs_step4/gates_frozen.md` and the scorer code; md5 of both written in the parent
  checklist Step 4 box and in `gates_frozen.md5`.
* The test-split reader refuses to open a test file unless `gates_frozen.md5` exists and matches; the
  refusal is seen once (run before the freeze, it must refuse).
* SUMMARY and exit code meaning written: 0 = all gates computed (pass or fail), 2 = at least one gate
  NOT_EVALUABLE, 1 = the scorer crashed (a crashed section is NOT_EVALUABLE in the SUMMARY too).

## OUTPUTS

`outputs_step4/gates_frozen.md`, `gates_frozen.md5`, `perturbations.md`, the scorer
`5thJ_04_scorer.py` (written in this step, run on validation only), `impl/<date>_freeze.md`.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 3.
