# `D-S6-8` — the level-1 crosswalk, and four things it forces a choice about

**Date:** 2026-08-22 (evening)
**Raised by:** building `G6.4`, which could not be computed because nothing mapped our 158 activity
codes onto Eurostat's `acl00` aggregates.
**Status:** OPEN. Built and calibrated, nothing frozen. `prereg.md` untouched, md5
`e4243e07cdd80c9c846b91f40e3e8c45`.

Evidence: `Step6_docs/4thJ_06_transfer.md`, entry of 2026-08-22 (evening), and
`outputs_step6/g64_corpus_calibration.json`. Code: `tools/4thJ_step6_level1.py`, selftest 48/48.

**The crosswalk works.** The real weighted corpus scores **9 PASS / 0 FAIL** against `tus_00age` 2010
on the three exactly-reproducible age bands, MAPE 1.33 %–4.94 %. The Leg-4 pilot scores **1 PASS /
8 FAIL**. The gate discriminates. What follows is the four places where it rests on a choice.

---

## Item 1 — `AC9A` is taken as the SUM OF ITS CHILDREN, not the published parent

| country | published `AC9A` | its seven children sum to | hole |
|---|---|---|---|
| ES | 70 | 70 | 0 |
| IT | 79 | 79 | 0 |
| **UK** | **129** | **81** | 🔴 **−48** |

Every other UK parent in the table sums to its children exactly. The 48-minute hole matches the UK's
anomalous `AC99NSP` of 49 (against 1 and 1 elsewhere).

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Children sum, all three countries.** | Identical to the parent in ES and IT, so it changes nothing there; in the UK it is the only figure that reconciles. Declared in the methods as a published-table defect |
| **(b)** | Published parent, all three. | Charges the UK model a **58 %** travel error for a defect in Eurostat's table, on the fold the UK is held out of |
| **(c)** | Parent for ES/IT, children for UK. | 🔴 A country-dependent basis, which is the thing `FINDING 53` exists to forbid |

---

## Item 2 — the age base

Our eight frozen bands reproduce **exactly three** Eurostat bands with no boundary straddling:
`Y25-44` = `25-34`+`35-44`, `Y45-64` = `45-54`+`55-64`, `Y_GE65` = `65-74`+`75+`. `Y20-74` cannot be
built (`15-24` straddles 20); `Y65-74` is absent in all three countries (`FINDING 55`).

`TOTAL`'s own population base is **not stated** in the JSON-stat, and our corpus floor is age 11.

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Score the three exact bands; report `TOTAL` as context, never as a verdict.** | Nine scoreable cells per arm. Ages 11–24 are then **not covered by `G6.4` at all**, which must be said plainly — it is the band where the fictional-country control and `G6.8` carry the weight instead |
| **(b)** | Score `TOTAL` as well. | It compares an age-11+ corpus against a base Eurostat does not state. Italy's `TOTAL` `AC1_TR` already reads 16 % off while both its working-age bands read 1–11 % — that gap is age composition, not the model |

---

## Item 3 — the weighting basis for the corpus arm

`weight_dia_cal` moves Italy's employment budget from **113.7** min/day to **155.9** against a
published 162 — a 30 % error becoming a 3.8 % one. This is `FINDING 53` in cash terms and it is
country-correlated.

**Recommendation: `weight_dia_cal` on the corpus arm, UNWEIGHTED on the generated arm.** The synthetic
population the model is prompted from *is* the fitted census marginals, so re-weighting the generated
diaries would apply the raking twice. 🔴 This is an asymmetry between the two arms and it is stated
rather than hidden. **Two UK diaries carry a null `weight_dia_cal`** and are dropped, named, and
counted in the artefact; they are 0.013 % of that fold, and before they were caught they turned every
UK aggregate into `NaN` with no warning.

---

## Item 4 — `MAPE` is unstable at these denominators, again

`AC1_TR` is **5 published minutes** for Spaniards over 65. The pilot puts 106 there, an APE of
**2,020 %**, which drags that band's MAPE to 363 %. The number is arithmetically correct and tells a
reader nothing.

**Recommendation: report `MAE` in minutes/day beside every `MAPE`,** and let `MAE` carry the reading
where the denominator is under ~15 minutes. Already implemented. This is `FINDING 39`'s *"`MAPE > 20 %`
is NOT EVALUABLE AS WRITTEN"* recurring at level-1 granularity — the same conclusion, more evidence,
not a new problem. 🔴 It bears directly on **prereg §6 FAIL criterion 2**, which is `MAPE > 20 %`.

---

## A correction, recorded because it was made

`D-S6-3` item 1's `< 1.0 %` zero-cell tolerance was implemented backwards on the first pass — used to
decide *which published cells count as zero* rather than *what the model may put in a cell the table
publishes as zero*. It classified Italy's published `AC2` of **eleven minutes** as "approximately
zero" and failed the real corpus for putting 14.67 there. Corrected. No level-1 published cell is
zero (the smallest is one minute), so the branch is exercised on a synthetic table in the selftest.
Corpus board moved 8 PASS / 1 FAIL → **9 PASS / 0 FAIL**.
