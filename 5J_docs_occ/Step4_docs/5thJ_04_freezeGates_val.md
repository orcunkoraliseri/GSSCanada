# Validation plan — Step 4 (freeze the gates)

### 5J occupancy-aware surrogate. Main doc: `5thJ_04_freezeGates.md`

Written 2026-09-28.

---

## Section 1 — Sources opened

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | ASHRAE Guideline 14 hourly band: source opened, page cited in `gates_frozen.md` | cited | FAIL (band not frozen without it) |
| 1.2 | Every other numeric threshold says where it comes from (source, or "chosen by the author on <date>") | all | FAIL |

## Section 2 — Perturbation table

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.0 | The unperturbed "good" stand-in passes every gate | all | FAIL (a gate the good stand-in fails is too strict or wrong) |
| 2.1 | Each perturbation breaks its gate; the other gates are unchanged except G5J.2 under the G5J.3 row | 5/5 | FAIL |
| 2.1b | Under the G5J.3 perturbation, the G5J.2 verdict is written per target and class (the premise, measured) | written | INFO |
| 2.2 | Each row shows the printed verdict line before and after | all | FAIL |
| 2.3 | All perturbations ran on the validation split; the test reader log shows no test file opened | 0 test opens | FAIL |

## Section 3 — Bootstrap

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | Resampling unit is building and household (code read, line cited) | yes | FAIL |
| 3.2 | Simulated null (S = B1): interval covers 0 in ≥ 93 % of 200 null runs | ≥ 93 % | FAIL |
| 3.3 | Function name matches what it does (failure class: "cluster_bootstrap" that was stratified) | yes | FAIL |

## Section 4 — Freeze

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | md5 of `gates_frozen.md` and scorer written in the parent checklist and re-computed | equal | FAIL |
| 4.2 | Test reader refused before the freeze (log line) and opens after | both seen | FAIL |
| 4.3 | Exit code meaning written; a planted crash in one section gives NOT_EVALUABLE in the SUMMARY and exit 1 | seen | FAIL |

## Section 5 — Noise floor

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 5.1 | Floor per target and class computed from Step 3 replicates, number of repeats stated | present | FAIL |
| 5.2 | A class with fewer than 30 pairs above the floor prints NOT_EVALUABLE for G5J.3 (planted with a high k) | seen | FAIL |
