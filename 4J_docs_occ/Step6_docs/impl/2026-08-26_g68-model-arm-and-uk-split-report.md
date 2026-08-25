# 2026-08-26 — `G6.8`'s MODEL ARM IS RUN, AND `D-S3-14`'s UK-FOLD SPLIT REPORT IS FILED

Two Step-6 obligations were open. Both are now discharged, and neither result is a pass.

* **`G6.8`'s model arm** had "never been run on either leg". It has now been run on all three
  Leg-5 folds, on both weight bases, and it **FAILs both arms in every fold**.
* **`D-S3-14`'s UK-fold split report** was owed since 2026-08-18. It is filed. Its headline is
  that the split it asks for **cannot be produced on the model side**, for a reason worth
  recording, and that everything else it asks for **can** be and has been.

⚪ No threshold moved. No checker edited. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
unchanged. Nothing here re-scores a gate that was already scored.

---

## 1. `G6.8` — the model arm

### What was actually missing

Not a GPU, not a checkpoint, and not the checker. `4thJ_step6_g68_joint.py` and its 17/17
self-test were finished on 2026-08-21, and both registered negative controls had been run and
seen behaving correctly on `it`:

| control | sequence arm | marginal arm |
|---|---|---|
| `REAL vs REAL, split-half null floor` | PASS | PASS |
| `REAL vs CONTROL 'shuffled_across'` | **FAIL** | PASS |

That pair is the proof the two arms are separable — a shuffle destroys sequence and leaves
marginals alone, and the checker sees exactly that. What was missing was one input file: the
script's `--ref/--cand` path calls `load(args.ref)` **without** a `country=` filter, so the
reference has to arrive already filtered, and no country-filtered reference existed on disk.

It is now built, from the corpus:

```
Step6_docs/outputs_step6/g68_refs/real_es.jsonl   19,140 diaries
Step6_docs/outputs_step6/g68_refs/real_uk.jsonl   15,854 diaries
Step6_docs/outputs_step6/g68_refs/real_it.jsonl   38,260 diaries
```

Candidates are the reportable Leg-5 constrained batches, 5,200 diaries per fold.

### Both weight bases, because only one side can carry a weight

`D-S6-4` ruled `weight_dia_cal` the headline basis for Step 6. A **generated** diary has no
`pid`, so the weight table keys nothing on the candidate side: the script reports
`5200 had no pid to key on and were left at 1.0` in every fold. Weighting only the reference
compares a weighted stock to an unweighted sample. Rather than choose, both bases were run —
`none`, which is the basis the two registered negative controls were run on, and
`weight_dia_cal`, which is the ruled headline.

🟢 **The verdicts are identical on both bases in all three folds.** The weighting question does
not reach this result, and that is worth more than picking a side.

### The numbers

Bands, from the Overview's Tier 1 table, unchanged: dwell-time Wasserstein-1 ≤ **10.0** min;
transitions/day absolute error ≤ **1.50**; transition-matrix TVD ≤ **0.050**; diurnal JSD
mean ≤ **0.015** and max ≤ **0.025**; time-budget error ≤ **15.0** min/day per stratum,
≤ **8.0** population.

| fold | basis | dwell W1 max | transitions abs err | TVD | JSD mean / max | budget err max |
|---|---|---|---|---|---|---|
| es | none | **61.46** | 0.32 ✓ | **0.2107** | **0.0694** / **0.1068** | **68.67** |
| es | `weight_dia_cal` | **61.77** | 0.34 ✓ | **0.2120** | **0.0690** / **0.1041** | **57.12** |
| uk | none | **66.56** | **1.80** | **0.1628** | **0.0934** / **0.2151** | **44.02** |
| uk | `weight_dia_cal` | **66.57** | **1.53** | **0.1623** | **0.0927** / **0.2172** | **55.09** |
| it | none | **53.77** | **3.92** | **0.2344** | **0.1189** / **0.2782** | **38.26** |
| it | `weight_dia_cal` | **50.13** | **3.86** | **0.2343** | **0.1168** / **0.2625** | **46.11** |

**SEQUENCE arm: FAIL in all three folds. MARGINAL arm: FAIL in all three folds.**

* The only checker that passes anywhere is **transitions/day on `es`** — 15.04 generated against
  15.36 real, an error of 0.32 against a band of 1.50. On `uk` it is 1.80 (1.53 weighted, still
  over) and on `it` 3.92: the model produces **12.51** transitions a day against a real
  **16.43**, a quarter fewer changes of activity.
* Dwell-time W1 is **5 to 6.7 times** its band everywhere.
* Transition-matrix TVD is **3.3 to 4.7 times** its band.
* Transition **entropy** is *higher* in the generated set than the real one in every fold
  (es 5.36 vs 5.03, uk 5.32 vs 5.11, it 5.05 vs 5.01) while the transition **count** is lower on
  uk and it. The model is not simply flattening; it is redistributing.

⚪ Under `weight_dia_cal` the `uk` reference carries 15,852 diaries, not 15,854: **two UK rows
have a null `weight_dia_cal`** and the loader drops them rather than defaulting them to 1.0. That
is the same pair `4thJ_step6_level1.py` already refuses NaN weights over.

### What this means, stated carefully

`G6.8` exists to answer one objection: *"the model is only echoing the marginals it was prompted
with."* It cannot answer it here, and not because the joints failed while the marginals held —
**the marginal arm fails too**. Time-budget error reaches 38–69 min/day against a band of 8–15,
and diurnal JSD is 4.6–7.9× its mean band. So `G6.8` returns no evidence that the model matches
structure the prompt did not carry, and no evidence that it matches the structure the prompt
*did* carry either.

🔴 This is **consistent with, and not independent of**, `G6.1` failing 9 of 9 and `G6.4` going
0 PASS / 9 FAIL. It is one more reading of the same failure, taken on quantities the prompt does
not contain. It must not be written up as a separate confirmation, and it must never be written
up as "G6.8 was run" without "and it failed".

⚪ Artefacts: `Step6_docs/outputs_step6/g68_model_leg5_{es,uk,it}_{none,weight_dia_cal}.json`,
six files.

---

## 2. `D-S3-14` — the UK-fold split report

### What was owed

> "🔴 **Step 6 must report the UK fold's scores split by this cell** — `strat_hh_type = unknown`
> versus the rest — so the limitation is quantified against outcomes rather than asserted. If
> that split cannot be produced, the limitation is reported as un-quantified and said to be so."

Ruled 2026-08-18, option (a): the `unknown` cell **stays**, no row imputed, no row dropped, and
`G3.9` stays red on `uk` by ruling.

### The cell, reproduced

551 UK diaries of 15,854 — **3.48 %** — across **107 households** of 4,229. Source:
a blank `dhhtype` in the UKDA extract, carried through
`Step2_docs/outputs_step2/crosswalk_strata.csv` as the literal value `unknown`. Under the
`D-S6-1(b)` household re-split they fall **481 train / 70 held-out**. No record was refused by
the decoder.

### 🔴 The model side of the split does not exist, and that is the finding

| batch | n | diaries at `strat_hh_type = unknown` |
|---|---|---|
| leg 4 constrained | 600 | **0** |
| leg 4 nogrammar | 600 | **0** |
| leg 5 constrained | 5,200 | **0** |
| leg 5 nogrammar | 5,200 | **0** |

`generation_config_uk.json` does not contain the string `unknown` anywhere.

The reason is structural, not accidental. Generation prompts are drawn from the Step 5 **synthetic
population**, which is built from census marginals, and a census margin has no "household type
unknown" category — the cell exists only as an artefact of a missing field in one national survey.
So the model was **never asked** to produce a diary in this cell, on either leg, and there are no
model scores to split.

🔴 Therefore the split `D-S3-14` names — model scores, `unknown` versus the rest — **cannot be
produced, and is hereby reported as un-quantified**, exactly as that decision's own fallback
clause requires. It is not un-quantified because the work was skipped; it is un-quantified because
one side of the comparison was never generated, and generating it would mean prompting from a
stratum the target population does not have.

### What CAN be quantified against outcomes, and is

The 551 still reach the result by two routes that do not need a model score: they trained the
model (481 diaries, with a corrupted conditioning token), and they sit in the real UK corpus the
reference statistics are taken from. Both are measurable.

**(a) The cell is not a random slice of the fold.** Largest departures, in percentage points:

| variable | value | unknown % | rest % | diff |
|---|---|---|---|---|
| age band | 15-24 | 32.12 | 11.96 | **+20.16** |
| age band | 65-74 | 3.63 | 13.36 | **−9.73** |
| age band | 55-64 | 6.17 | 14.80 | **−8.63** |
| age band | 11-14 | 11.25 | 5.45 | +5.80 |
| econ status | retired | 5.81 | 22.87 | **−17.06** |
| econ status | other_inactive | 23.05 | 11.46 | **+11.59** |
| econ status | student | 13.07 | 4.25 | **+8.81** |
| sex | female | 63.34 | 53.70 | **+9.64** |
| day type | every level | — | — | ≤ 3.1, i.e. flat |

A blank `dhhtype` is concentrated in the **young, the student, the economically inactive and
women**, and is almost absent among the retired. This is a missing-not-at-random field, and the
write-up must say so rather than call it 3.5 % of rows.

**(b) It behaves differently on the very quantity Step 6 scores.** Level-1 time budget,
min/day, against the published Eurostat UK column (`tus_00age`, TOTAL, 2010):

| | MAE min/day | MAPE |
|---|---|---|
| the `unknown` cell (551) | **29.087** | **34.332 %** |
| the rest of the fold (15,303) | 17.187 | 9.945 % |
| the whole UK fold (15,854) | 17.345 | 10.647 % |

The cell fits the published column **3.5 times worse in MAPE** than the rest of its own fold.
Per aggregate it is out by **+30.9** min/day on `AC0` (personal care and sleep), **+28.6** on
`AC2` (household and family care) and **−30.8** on `AC3` (unpaid work and volunteering) relative
to the rest — consistent with a young, student-heavy, inactive-heavy cell.

**(c) Its effect on the fold's reported number is nevertheless small,** because it is 3.48 % of
the fold: dropping it moves whole-fold MAE by **+0.158 min/day** (17.345 → 17.187) and MAPE from
10.647 % to 9.945 %. The worst single aggregate moves **+1.07 min/day** (`AC0`).

### The sentence the limitations section can now carry

The `strat_hh_type = unknown` cell is 3.48 % of the UK fold, is missing-not-at-random — over-
representing 15-24-year-olds by 20 pp and students by 9 pp, under-representing the retired by
17 pp — and fits the published UK time budget 3.5× worse than the rest of the fold (MAPE 34.3 %
vs 9.9 %). Because the synthetic population has no such stratum, **no diary was ever generated in
this cell**, so the model's own scores cannot be split on it and that half of `D-S3-14` is
reported un-quantified. Its influence on the fold-level number is bounded and measured:
**0.158 min/day of MAE**, 0.7 pp of MAPE.

⚪ Artefacts: `Step6_docs/outputs_step6/uk_fold_split_report_D-S3-14.txt` (md5
`a9502f55910257fcc2248cab5cf522b9`), produced by `tools/4thJ_step6_uk_split_report.py` (md5
`f8cd4a8adb261fa4a8bfc60604e59187`).
