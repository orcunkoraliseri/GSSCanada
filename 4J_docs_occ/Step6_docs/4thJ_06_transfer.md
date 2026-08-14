# Step 6 — Transfer

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 6. Validation: `4thJ_06_transfer_val.md`

---

## STATUS

**OPEN. Null model hardened by `RL06` and adopted as the objective by author decision 4.**
**This is where the paper is won or lost.**

---

## AIM

Answer one sentence, and the paper has to earn it:

> *Can a model that has never seen a country's diaries produce a population for it that is closer to
> the truth than reweighted real diaries from its neighbours?*

---

## THE EXPERIMENT

Train on N-1 countries. Generate a population for the held-out country conditioned **only on its
published demographic marginals**, with none of its diaries seen. Score against its published
aggregate tables: `tus_00age`, `tus_00educ`, `tus_00selfstat`, `tus_00hh`, and `tus_20startime` for
the time-of-day curve.

🔴 **N = 4 after author decision 5, so training is on three.** Italy, Spain, UK, France. That is thin,
it is limitation C4, and **Track A is the only thing that raises it** — to seventeen, with no
harmonisation change, because our four waves are the HETUS 2010 round.

---

## THE NULL, AND IT IS THE OBJECTIVE RATHER THAN AN OBSTACLE

| Null | Strength | Role |
|---|---|---|
| Pooled all-country average diary | weak | secondary, reported |
| Nearest-neighbouring-country model | moderate | secondary; answers the geographic-proxy objection |
| **Real diaries from the N-1 pool, raked by IPF to the held-out country's published marginals** | **strongest** | 🔴 **the pre-registered bar** |

Every raked donor is an **authentic human day** with perfect grammar, real transitions and real
variance. `RL06` states it plainly: if the fine-tuned LLM cannot beat a demographically raked pool of
real European donors on the held-out country, **the transfer claim fails.**

🔴 **Author decision 4: this is stated in the INTRODUCTION as the objective**, not disclosed in the
evaluation section. Two reasons. A bar set in advance and then cleared is worth more than one chosen
after the results are in, and reviewers can tell the difference. And it makes the paper falsifiable in
one sentence, which is the strongest position an empirical claim can be in.

**This is the one place raking is permitted in this project. It builds the null. It never touches our
output.**

---

## THE THREE REVIEWER ATTACKS, EACH WITH ITS COUNTER-MEASURE

Each requires an **experiment**, not a paragraph.

1. **Contamination.** *"The model already read about that country on the web."*
   **Counter:** condition on a **fictional country token with perturbed marginals** and verify the
   output follows the conditioning vector rather than a memorised national stereotype. This is also
   the cleanest test of `RL04`'s cultural-asymmetry confound.
2. **The marginal-matching illusion.** *"It just echoes the marginals you gave it."*
   **Counter:** score **joint** structure that was never in the prompt — co-presence cross-tabulations,
   transition entropy, dwell-time distributions conditioned on **pairs** of attributes.
3. **Geographic proximity.** *"It mapped the held-out country to its neighbour."*
   **Counter:** the nearest-neighbour-country null, reported alongside the headline.

---

## 🔴 THERE IS NO FORECAST IN THIS PAPER

Author decision 3. Not deferred, not attempted and reported as inconclusive. **Absent.** No year
token, no projection, no scenario lever, no 2030.

`RL16` independently concluded the data could not carry a forecast. **The decision and the evidence
agree, but they are not the same thing and the decision is the load-bearing one:** the contribution is
the *method of applying a fine-tuned language model across the HETUS and wider time-use framework*,
and that is a contribution on its own terms.

The Kitagawa-Oaxaca-Blinder decomposition `RL16` recommended is out with it — it was the strongest
available **temporal** formulation and there is no longer a temporal claim.

**The earlier waves** are held-out validation only (parent 1B). Never a trend to extend.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| Leave-one-country-out, rotating | `RL06`, author |
| The raked-donor null is the pre-registered bar | `RL06`, author decision 4 |
| 🔴 **The held-out country must be chosen BEFORE the first training run** | Open decision 11 |
| No forecast, no year token | Author decision 3, `RL16` |
| The privacy audit runs here | `RL10` |

🔴 **Open decision 11 is still open and it is the cheapest thing in this project to get wrong.** A
country chosen after seeing results is not held out, and no amount of later care repairs it. **Rotation
across all four is stronger than picking one**, and with four countries it is affordable.

---

## INPUTS

* `../Step4_docs/outputs_step4/` — one adapter per leave-one-out fold
* `../Step5_docs/outputs_step5/population_<country>.parquet` and `prefixes_<country>.jsonl`
* `../Step7_docs/outputs_step7/generated_<country>.parquet` — Step 7 does the generating
* Published Eurostat aggregate tables for each held-out country

---

## WORK ITEMS

### 6.1 — Pre-register, in writing, before any fold is trained

A file, dated, containing: the held-out rotation, the null definitions, every threshold, and the
**FAIL criteria**. 🔴 **The best pre-registration names the outcome that would prove we cheated**, not
the one we expect.

Pre-registered FAIL criteria, any one of which fails the claim:

* MAE ≥ the raked-donor null; **or**
* MAPE > 20 %; **or**
* the **sign** of the country's divergence from the European mean is inverted.

**Output:** `outputs_step6/prereg.md`, frozen with an md5 before the first fold runs.

### 6.2 — Build the three nulls

The raked-donor null is the one that matters and the one that is easiest to build wrong. IPF the
**real** N-1 diaries onto the held-out country's published marginals. Same marginals the model got,
same geography, same strata.

### 6.3 — Run the folds

One fold per held-out country. Joint training on the other three, country token in the prefix.

### 6.4 — Score

Tier 4 of the parent gate table, plus the joint-structure scores from attack 2, plus the
fictional-country control from attack 1.

### 6.5 — The privacy audit, from `RL10`, before anything is released

| Attack | Fails if |
|---|---|
| Loss-based membership inference | ROC-AUC > 0.65, or TPR at 0.1 % FPR > 5 % |
| Reference-based MIA against the public base model | ROC-AUC > 0.75 |
| Prefix-prompted extraction, greedy and sampled | any exact match on a stratum with fewer than 5 training records |
| Distance to closest record and NNDR on the synthetic release | any DCR = 0; or median DCR to train significantly below median DCR to test; or NNDR < 0.33 in over 0.1 % of records |

With three controls: the **untuned base model** (expect AUC ≈ 0.50), a **random-label-permutation
adapter** setting the floor for pure sequence memorisation, and a train-versus-test perplexity gap
under 5 %.

🔴 **Reference-based MIA is the sharper test, because the base model is public.** That is precisely
why `RL10` forbids releasing the adapter.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step6/prereg.md` (frozen, md5 recorded) | Everything. It is the honesty of the experiment |
| `outputs_step6/fold_<country>_scores.csv` | The results section |
| `outputs_step6/nulls_<country>.parquet` | Step 6 validation |
| `outputs_step6/privacy_audit.md` | The release decision and the Data Availability statement |

---

## WHAT BLOCKS THIS STEP

Steps 4, 5 and 7. **And open decision 11, which must close first.**

---

## DEFINITION OF DONE

1. Pre-registration frozen and hashed **before** the first fold.
2. Three nulls built, the raked-donor null built from real diaries.
3. All folds run, all scored against Tier 4.
4. All three reviewer attacks answered with an experiment.
5. Privacy audit complete with its three controls.
6. All Step 6 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 Open decision 11 blocks this step and is still open. Recorded here as well as in the parent
  because a held-out country chosen late is the one defect in this project that cannot be repaired
  afterwards by any amount of care.
