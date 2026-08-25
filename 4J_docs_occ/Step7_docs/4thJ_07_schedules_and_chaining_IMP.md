# Step 7 — the GPU-free half: schedule emission (7.7) and the chaining rule (7.6)

### 4J HETUS LLM pipeline. Implementation document.
#### Parent implementation: `4thJ_07_constrainedGeneration.md`. Validation: `4thJ_07_constrainedGeneration_val.md`. Handoff: `../Prompts/RESUME.md`
#### Opened **2026-08-22 (night)**, while jobs `1286208` (throughput, 7.2) and `1286209` (Leg 5, Step 4) are PENDING on the A100 `7g.80gb` pool.

---

## WHY THIS DOCUMENT EXISTS

Step 7 has seven work items. **Two of them need no GPU, no Speed and no network**, and both are on
the critical path of the paper's building-side claim:

* **7.7 — emit schedules.** Four gates (`G7.14`–`G7.17`) have never been scored because the artefact
  they score does not exist. Everything they need is on this laptop.
* **7.6 — the chaining rule, open decision 14.** Its definition of done has five items; **items 3 and
  4 are explicitly CPU work** — a pre-screen on assembled 8,760-hour arrays that "costs seconds", and
  an activity-vocabulary check computed on real data.

🔴 **This document does not close either work item.** It closes the parts that do not need a GPU, and
it says in each case exactly which part is left. The distinction is the point: a document that
reports "7.7 done" when what exists is a rehearsal on a 1B pilot model would be the same class of
error as `FINDING 46`, where a gate measured the training corpus and was read as measuring the
output.

---

## 🔴 THE PROVENANCE CEILING ON EVERYTHING BELOW

Every generated diary available offline is from the **Leg-4 rehearsal**:

```
base_repo   allenai/OLMo-2-0425-1B          <- NOT the reported backbone
adapter     runs_ds45/leg4_primary_fold_*   <- the pilot adapters
provenance  "LEG-4 PILOT -- NOT REPORTABLE"
N           600 per fold per arm
```

The reported backbone is `allenai/Olmo-3-1025-7B` and its adapters do not exist yet — that is job
`1286209`. **So every number this document produces about diaries is a rehearsal number and is
labelled `LEG-4 PILOT -- NOT REPORTABLE` in the artefact itself, not merely in prose.** What is being
validated here is the **tooling and the gates**, which is exactly what can be validated before the
model exists, and which is what the campaign will otherwise discover it lacks at the moment the GPU
frees up.

Two things below are **not** subject to this ceiling, because they are computed on the real corpus:

* the activity-vocabulary reference (`RL21` Part D says compute it on the held data, not take it from
  `RL21`), and
* the household composition used by the chaining experiment.

---

## THE TASK LIST, IN EXECUTION ORDER

| | task | needs | closes |
|---|---|---|---|
| **T1** | `tools/4thJ_step7_schedules.py` + selftest — the emitter | nothing | work item 7.7's code |
| **T2** | `tools/4thJ_gates_step7_schedules.py` + the four registered perturbations | T1 | `G7.14` `G7.15` `G7.16` `G7.17`, each **seen failing** |
| **T3** | `tools/4thJ_step7_chaining.py` + selftest — three rules, ≥5 seeds, the pre-screen | T1 | 7.6 DoD items **3 and 4** only |
| **T4** | the activity-vocabulary reference on the **real** corpus | nothing | 7.6 DoD item 4's reference value |
| **T5** | three-artefact closure: this doc, the val doc, `4thJ_07_constrainedGeneration.md`, `../Prompts/RESUME.md` | T1–T4 | the ritual |

**Nothing in this list submits a job, touches Speed, or opens a socket.**

---

## WHAT IS DELIBERATELY NOT ATTEMPTED

* **7.2 throughput** — job `1286208`. Needs the GPU by its own design: the quantity measured is the
  KV cache the engine can allocate.
* **7.3 Leg-5 generation** and **7.4's untuned-base arm** — GPU.
* **7.5 the rejection-sampled control** — sized at ≈22,500 / 8,800 / 15,700 draws and deliberately
  **not** submitted while `1286209` is PENDING on `AssocGrpGRES`, because `gres/gpu` is counted across
  all slice types and three more GPU jobs could delay the reported model.
* **`G7.18`'s verdict** — annual peak electrical power and heating/cooling energy are **Step 8**
  outputs. This document produces the pre-screen that `RL21` calls a screen and the step document
  calls "a screen, not a substitute". **Decision 14 stays OPEN.**

---

## PROGRESS LOG

Append-only.

### 2026-08-22 (night) — 🟢 **T1 AND T2 ARE DONE. WORK ITEM 7.7 HAS AN EMITTER, AND THE FOUR SCHEDULE GATES THAT HAD NEVER BEEN SCORED ARE SCORED, PASS ON ALL THREE FOLDS, AND HAVE EACH BEEN SEEN FALLING. 🔴 IT COST THREE FINDINGS AND TWO NEW PERTURBATIONS THE REGISTERED TABLE DID NOT HAVE.**

#### 🟢 T1 — `tools/4thJ_step7_schedules.py`, selftest **52 ok / 0 FAILED**

`tools/4thJ_step7_schedules_selftest.py` exercises every refusal on fixtures before the module is
pointed at a batch. The refusals are not decoration; each was made to fire:

| refusal | seen firing on |
|---|---|
| a **leap year** | 2012 and 2016, both rejected — 366 days is 8,784 h, and silently dropping 29 February shifts every weekend after it by one day while still looking plausible |
| a timestep that does not divide 1440 | 7 min and 50 min |
| a household with **zero members** | fixture |
| members disagreeing on the number of days | fixture |
| a **day type absent from the pool** | never back-filled with another day type |
| an **empty pool** | a schedule assembled from no days is a constant, which is `FINDING 42`s signature |
| a value count that is not a whole number of hours | 8,759 values at 7 min |
| an unknown chaining rule | `markov` |

🟢 **The three chaining rules are three points on ONE axis, and that is asserted rather than hoped.**
Counting fresh draws over a 365-day year: `independent` = **365**, `static` = **3** (one per day
type), `habit` at `rho = 0` = **365**, `habit` at `rho = 1` = **3**, `habit` at `rho = 0.5` strictly
between. So the habit-coupled rule is not a third implementation that could drift from the other
two — it is the same code with the endpoints reproduced exactly.

⚪ One selftest expectation of mine was wrong and the module was right: 2011 has **53** Saturdays and
**260** weekdays, not 52 and 261, because it opens and closes on a Saturday. Corrected in the test.

#### 🟢 The three baseline cells, emitted

`Step7_docs/outputs_step7/schedules/leg4_<fold>_independent_seed1/`, 100 households each, 8,760
hourly values per household, `Schedule:File` + `People` per dwelling.

| fold | calendar year | households | persons | mean household size | mean presence |
|---|---|---|---|---|---|
| `es` | 2010 | 100 | 204 | 2.04 | **0.7285** |
| `uk` | 2014 | 100 | 180 | 1.80 | **0.6450** |
| `it` | 2013 | 100 | 212 | 2.12 | **0.6843** |

🔴 **These three presence numbers are `LEG-4 PILOT -- NOT REPORTABLE` and are stamped so inside every
`manifest.json` and every `.idf` header.** They are not evidence about occupancy; they are evidence
that a signal with plausible structure comes out the far end of the pipe. Fidelity is Steps 4 and 6.

⚪ The calendar year is one per fold — `es` 2010, `uk` 2014, `it` 2013 — the non-leap year of each
survey pair (ES 2009-10, UK 2014-15, IT 2013-14). `D-S8-2` item 6 ruled diary-survey-year actual
weather, and each survey spans **two** calendar years, so which of the two the schedule runs on is a
choice nothing has ruled. It is a CLI parameter with **no default** and leap years are refused, so it
can never be picked by accident; the ruling is owed before Step 8 sizes its weather files.

#### 🔴 The stratum back-off ladder is MEASURED, and at `N = 600` it binds hard

A person is served a day whose stratum matches theirs on as many of the four prefix fields as the
pool can supply; the day type is **never** relaxed. The ladder is counted, per cell:

| fold | depth 4 (exact) | depth 3 | depth 2 | depth 1 | depth 0 | full-depth share |
|---|---|---|---|---|---|---|
| `es` | 43,032 | 25,395 | 5,825 | 208 | 0 | **57.79 %** |
| `uk` | 40,953 | 14,387 | 10,204 | 156 | 0 | **62.33 %** |
| `it` | 49,148 | 21,887 | 6,085 | 260 | 0 | **63.52 %** |

🔴 **So four days in ten are drawn from a stratum coarser than the person own**, and the number is
country-correlated (a 5.7 pp spread) exactly as `FINDING 45` and `FINDING 53` would predict. This is a
consequence of the **600-diary rehearsal pool**, not of the design: the author Leg-5 mandate of
`N >= 5,200` per fold is roughly 8.7 times more days and the ladder must be re-measured then, not
assumed to improve. 🔴 **It is reported because a campaign that quietly served every 13-year-old a day
drawn from "any weekday" would produce a perfectly valid schedule set and a meaningless one, and
nothing downstream would ever see it.** Depth 0 is zero everywhere, so no draw fell back to day type
alone.

#### 🔴 `FINDING 93` — work item 7.6 asks for 100 HOUSEHOLDS and Step 5 cannot supply one

`population_<c>.csv` is a **person** table: `country, strat_age_band, strat_sex, strat_hh_type,
strat_econ_status, strat_day_type`, 100,000 rows, **no household identifier**. `D-S5-9` settled
household TYPE on a person basis (`FINDING 60`, convention A) and never needed to assemble a dwelling,
so nothing in Step 5 says which persons share a roof. Work item 7.6 *100 households* and the whole
co-presence half of `G7.4` therefore have no object to run on in the synthetic population.

**What was done instead, and it is a limitation, not the design:** household composition is taken from
the **real corpus**, which carries `hid` and `pid`. The households are real and their members strata
are real; only the DAYS are generated. That makes the chaining experiment a sample of **surveyed**
households, not a sample of the synthetic population, and those are not the same object.

🔴 **`D-S7-6`, for the author: how do households enter the synthetic population?** Options as far as
they are visible from here: **(a)** leave it — the chaining experiment stays on surveyed composition
and the paper says so; **(b)** add a household identifier to Step 5 by drawing households rather than
persons, which is a **Step 5 basis change** and would re-open a closed step; **(c)** assemble
households post hoc by grouping persons of compatible `strat_hh_type`, which invents a joint
distribution nothing measured. ⚪ Recorded here rather than chosen: (b) re-opens a step that closed on
2026-08-22 and (c) is the class of invention `FINDING 47` is about.

#### 🔴 `FINDING 94` — the two documents disagree about what a schedule carries, and one of them cannot be implemented

| document | what a schedule carries |
|---|---|
| `4thJ_07_constrainedGeneration.md`, DIARIES TO SCHEDULES | *"**Activity-resolved internal gains**, which is the part a presence fraction throws away"* |
| `D-S8-2` item 5, ruled 2026-08-21 | `phi_int(t) = (1-f)*3.0 + f*3.0*g(t)/mean_year(g(t))`, where `g(t)` is *"the generated presence signal from `G7.13`"* |

The second is a **fraction**; the first is a **watt**. Resolving a 3-digit HETUS activity code into a
power needs a mapping, and **there is no admissible one**: `RL25` was commissioned for exactly that
and its Part C figures were **rejected as unsourced** (mechanisms real, numbers not). Inventing one
here would place an invented number between our diaries and every load in the paper.

🟢 **The emitter implements the RULED interface** — presence — and keeps each pool day activity codes
alongside it, so if the author reinstates activity-resolved gains the mapping can be applied to an
artefact that already exists, without a GPU run. ⚪ The methods owe one sentence saying the gains are
occupancy-redistributed and **not** activity-resolved, or `D-S8-2` item 5 own wording will read as
if they were.

#### 🟢 T2 — `tools/4thJ_gates_step7_schedules.py`. **BOARD: 5 PASS / 0 FAIL on all three folds, and all five seen falling.**

Everything is **re-read from disk** — the `.idf` as text, every `.csv` as text — never from the
emitter in-memory objects. That is `G8.12` rule borrowed one step early: *"if it reads the
schedule from the same in-memory object the injector wrote, it is comparing the injector numbers
against the injector."*

| | `es` | `uk` | `it` |
|---|---|---|---|
| `G7.13` indoor rule, on the EMITTED signal | PASS | PASS | PASS |
| `G7.14` `Schedule:File`, not `Schedule:Compact` | PASS | PASS | PASS |
| `G7.15` `Interpolate to Timestep = No` | PASS | PASS | PASS |
| `G7.16` length and resolution | PASS | PASS | PASS |
| `G7.17` presence range and head-count | PASS | PASS | PASS |

100 `Schedule:File` + 100 `People` objects and 100 CSVs per cell; exclusion list md5
`679518c7f626bd5d408adc96b5a1ff43` on all three, read live from Step 2 shipped path.

#### 🟢 THE GATE CAUGHT A REAL DEFECT ON ITS FIRST RUN, BEFORE ANY PERTURBATION

The first baseline scored **`G7.13` FAIL**: *"the manifest does not record WHICH exclusion list
produced this signal."* It was true — the emitter first manifest recorded the list md5 but not
whether the list used **was** the shipped one, so `V7.c` could not be checked from the artefact.
Fixed additively (two fields), the cells re-emitted, and the gate passes. 🔴 Recorded because it is
the difference between a gate and a formality: the very first thing it did was refuse.

#### 🔴 `FINDING 95` — TWO OF THESE FOUR GATES HAD NO REGISTERED FALSIFIER AT ALL

`4thJ_07_constrainedGeneration_val.md` perturbation table names three perturbations touching these
gates, and **`G7.14` and `G7.17` appear only in the must-stay-clean column**:

```
Set `Interpolate to Timestep = Yes`            -> G7.15   (G7.14 clean)
Emit 8,759 hours                               -> G7.16   (G7.17 clean)
A local copy of OUTDOOR_AT_HOME off by one     -> G7.13   (G7.17 clean)
```

Under the coverage clause — *"FAIL the probe if any passing gate was never made to fall"* — both would
have passed for ever without once being seen to fall, and the board would have read 4 of 4 with two of
them unfalsifiable. **Two falsifiers are added, additively, and named as additions.**

#### The six perturbations, all run

| perturbation | must fall | fell | must stay clean | stayed |
|---|---|---|---|---|
| `Interpolate to Timestep = Yes` | `G7.15` | 🟢 *"100 of 100 Schedule:File objects do not say No"* | `G7.14` | 🟢 |
| emit 8,759 hours | `G7.16` | 🟢 *"a schedule carries 8759 values; 8760 hours at 60 min is 8760"* + *"100 objects declare 8759 hours, not 8760"* | `G7.17` | 🟢 |
| a **local copy** of `OUTDOOR_AT_HOME` missing code `341` | `G7.13` | 🟢 *"derived with a LOCAL COPY … not the shipped list"* | `G7.17` | 🟢 |
| 🔴 **ADDED** — emit `Schedule:Compact` | `G7.14` | 🟢 *"100 Schedule:Compact objects"* | `G7.16` | 🟢 |
| 🔴 **ADDED** — shift every value by `+0.5` | `G7.17` | 🟢 *"presence leaves [0,1]: 100 of 100 schedules, range [0.500000, 1.500000]"* | `G7.14` | 🟢 |
| **null perturbation: change nothing** | nothing | 🟢 nothing fell | everything | 🟢 |

🔴 **One collateral, recorded rather than tidied away.** The `Schedule:Compact` perturbation also fells
`G7.15`, because a Compact object carries no `Interpolate to Timestep` field and `G7.15` reports
*"the setting was never asserted"*. That is the correct reading — if the schedules are Compact, the
interpolation setting genuinely was never asserted — so `G7.16` is named as the clean partner rather
than `G7.15`. A perturbation that fells two gates is not a broken perturbation; a perturbation whose
second casualty is undeclared is.

#### Artefacts

| file | what |
|---|---|
| `tools/4thJ_step7_schedules.py` | the emitter |
| `tools/4thJ_step7_schedules_selftest.py` | 52 ok / 0 FAILED |
| `tools/4thJ_gates_step7_schedules.py` | `G7.13`–`G7.17`, read from disk |
| `outputs_step7/schedules/leg4_{es,uk,it}_independent_seed1/` | three baseline cells |
| `outputs_step7/schedules/perturb_*/` | six perturbation cells |
| `outputs_step7/gates_step7_schedules_baseline.json` | the board |
| `outputs_step7/gates_step7_schedules_perturbations.json` | the six cells, with reasons |

#### 🔴 What T1 and T2 do NOT establish

* **Not** that the schedules are right, only that they are **well formed**. A dwelling occupied by
  someone who sleeps 24 hours a day passes all five gates. Fidelity is Steps 4 and 6.
* **Not** DoD item 7 (schedules emitted with the indoor rule applied) for the REPORTED model. These
  are pilot diaries from a 1B backbone. The emitter is what is done; the campaign is not.
* **Not** anything about EnergyPlus. No IDF has been run, `Schedule:File` has never been resolved by
  the engine, and `G8.12`/`G8.13` are Step 8 and remain unrun.

### 2026-08-22 (night, second entry) — 🟢 **T3 AND T4 ARE DONE, AND THE CHAINING PRE-SCREEN RETURNED THE PRE-REGISTERED NULL RESULT ON EVERY COINCIDENCE METRIC. 🔴 `FINDING 96`: `RL21`'S ACTIVITY-VOCABULARY CRITERION IS NOT COMPUTABLE FROM ANY OF THE THREE SURVEYS, AND THE ONE ANCHOR THAT DOES EXIST IS BLIND TO THE CHAINING RULE.**

`tools/4thJ_step7_chaining.py` + `tools/4thJ_step7_chaining_selftest.py` (**40 ok / 0 FAILED**).
Board: `outputs_step7/chaining_prescreen_leg4.json`. Campaign: **3 folds × 6 rule points × 5 seeds =
90 cells**, 100 households each, 8,760 hourly values per household.

The six rule points are one axis sampled six times, not three unrelated rules — the emitter selftest
proves `rho = 0` **is** `independent` and `rho = 1` **is** `static` by counting fresh draws (365 and
3 respectively):

```
independent   habit rho=0.25   habit rho=0.50   habit rho=0.75   habit rho=0.90   static
```

#### 🟢 T4 — THE ACTIVITY-VOCABULARY REFERENCE, ON THE REAL CORPUS

| | persons | diaries | days per person | distinct `ACT` codes per DAY |
|---|---|---|---|---|
| `es` | 19,140 | 19,140 | **1** for every person | **10.910** |
| `it` | 38,260 | 38,260 | **1** for every person | **11.543** |
| `uk` | 7,934 | 15,854 | **2** for 7,920, 1 for 14 | **12.546** |

#### 🔴 `FINDING 96` — the criterion asks for a quantity the surveys do not contain

`RL21` Part D, as the step document adopted it, says: *"count distinct activity codes per synthetic
individual per **month** … the realistic value is computed on the held **ISTAT** data, not taken from
`RL21`."*

**ISTAT gives every respondent exactly ONE diary day. So does Spain.** Nobody in any of the three
surveys has a month of days, and only the UK has a second day at all. A monthly vocabulary therefore
has **no empirical reference anywhere in this project**, and the sentence that says to compute one on
the held data cannot be carried out as written.

What the corpus *can* anchor, measured rather than assumed:

| the UK two-day sub-sample | |
|---|---|
| persons with exactly two days | **7,920** |
| ... of which the two days share a **day type** | **21** (0.27 %) |
| day-type pairs | `saturday,weekday` 4,001 · `sunday,weekday` 3,896 · `weekday,weekday` 20 · `saturday,sunday` 2 · `saturday,saturday` 1 |
| **NEW** codes the second day adds | **4.907** |
| union over the two days | **17.690** |
| **Jaccard between the two days** | **0.4325** |

🔴 So the only measurement of day-to-day activity-vocabulary accumulation in the entire project rests
on **7,920 British respondents**, and in 99.7 % of those cases it measures the step from a weekday to
a **weekend** day — not from one day to the next of the same kind. Any sentence in the paper that
speaks of "the realistic vocabulary" must carry both facts or it is claiming a reference that does
not exist.

#### 🔴 AND THAT ANCHOR CANNOT TELL THE THREE RULES APART. IT IS FLAT.

The habit rule holds the previous day **of the same day type**, so it cannot touch a
weekday-to-weekend transition — and the measurement confirms it rather than the reasoning asserting
it. Simulated Jaccard between adjacent days **of different day types**, the quantity the UK anchor
measures:

| rule | `es` | `uk` | `it` |
|---|---|---|---|
| `independent` | 0.3451 | 0.3798 | 0.3900 |
| `habit rho=0.25` | 0.3450 | 0.3801 | 0.3897 |
| `habit rho=0.50` | 0.3450 | 0.3795 | 0.3898 |
| `habit rho=0.75` | 0.3447 | 0.3796 | 0.3905 |
| `habit rho=0.90` | 0.3433 | 0.3788 | 0.3904 |
| `static` | 0.3463 | 0.3787 | 0.3883 |
| **spread across all six rules** | **0.0030** | **0.0014** | **0.0022** |
| **the UK real anchor** | — | **0.4325** | — |

🔴 **Six rules spanning the entire persistence axis move this number by 0.003, 0.001 and 0.002.** The
one criterion `RL21` offered as empirically anchorable is, on the axis the data can anchor,
**identical under every chaining rule**. It is a fidelity measurement, not a chaining discriminator,
and using it to choose a rule would be choosing on noise.

⚪ Recorded and NOT used as a fidelity verdict: the pilot's UK cross-day-type Jaccard is 0.379 against
a real 0.4325, i.e. the pilot's people vary a little more between a weekday and a weekend than real
British respondents do. That is a Leg-4 1B-backbone number, it belongs to Step 6, and it is written
here only so nobody re-derives it later and thinks it is new.

#### 🟢 WHERE THE CHAINING RULE **IS** DECISIVE

The two quantities that move are exactly the two the corpus cannot anchor:

| rule | monthly vocabulary `es`/`uk`/`it` | same-day-type adjacent Jaccard `es`/`uk`/`it` |
|---|---|---|
| `independent` | 27.84 / 29.71 / 27.96 | 0.760 / 0.814 / 0.843 |
| `habit rho=0.50` | 26.05 / 27.77 / 26.34 | 0.879 / 0.907 / 0.921 |
| `habit rho=0.90` | 22.25 / 23.85 / 23.37 | 0.976 / 0.981 / 0.984 |
| `static` | 19.91 / 21.45 / 21.55 | 1.000 / 1.000 / 1.000 |

Monotone in `rho`, in the direction `RL21` predicts, on all three folds. A synthetic full-time worker
under independent resampling accumulates **28** distinct activity codes a month against **20** under
static repetition — a 40 % difference — and no survey in this project can say which is right.

#### 🔴 THE PRE-REGISTERED SPREAD TEST: THE COINCIDENCE PRE-SCREEN RETURNS **NOTHING**

The validation document registers the verdict in advance: *"if the spread across seeds within a rule
exceeds the spread between rules, **the experiment has told us nothing about chaining, and the
deliverable is that finding, not a chosen rule**."* Max within-rule seed spread against the spread of
the six rule means, `100` households, `5` seeds:

| metric | `es` | `uk` | `it` |
|---|---|---|---|
| `annual_mean` | 0.28 🔴 | 0.50 🔴 | 0.07 🔴 |
| `peak_aggregate` | ⚪ degenerate (1.0) | 0.66 🔴 | ⚪ degenerate (1.0) |
| `p99_aggregate` | ⚪ degenerate (1.0) | 0.20 🔴 | ⚪ degenerate (1.0) |
| `trough_aggregate` | 1.97 🟢 | 0.87 🔴 | 1.01 🟢 |
| `max_ramp` | 0.79 🔴 | 0.84 🔴 | 1.81 🟢 |
| `mean_pair_corr` | 0.39 🔴 | 0.19 🔴 | 0.19 🔴 |
| `vocab_day_mean` (negative control) | 1.02 | 0.30 | 0.44 |
| `vocab_month_mean` | **18.17** 🟢 | **11.89** 🟢 | **18.36** 🟢 |
| `jaccard_adjacent_same_day_type` | **71.64** 🟢 | **64.50** 🟢 | **63.77** 🟢 |

*(ratio = between-rule spread ÷ within-rule seed spread; 🟢 = rule effect exceeds seed noise, 🔴 =
seed noise dominates and the metric says nothing about chaining.)*

🔴 **On every coincidence metric — the ones a peak-demand pre-screen is made of — seed noise wins on
at least two folds of three, and on `mean_pair_corr` it wins on all three.** `trough_aggregate` and
`max_ramp` scrape past 1.0 on one or two folds, which is not an effect, it is a coin landing on its
edge. So the honest statement is the pre-registered one: **on the occupancy side, this experiment has
told us nothing about chaining.** The rule is invisible in coincident occupancy and decisive in
activity vocabulary, and those are two different claims about two different quantities.

⚪ **`peak_aggregate` and `p99_aggregate` are DEGENERATE on `es` and `it`** — pinned at exactly 1.000
in all 30 cells, because with 100 households there is some hour of the year when everyone is home.
The module labels this rather than scoring it: both spreads are zero, the ratio is 0/0, and reporting
that as "seed noise dominates" would put a verdict on a constant. 🔴 It also means an aggregate-peak
coincidence metric **saturates at this household count** and Step 8 must size its ensemble with that
in mind.

🟢 **`vocab_day_mean` is a negative control and it behaves like one.** The chaining rule cannot change
how many activities are in a single drawn diary, only which diaries repeat — so a correctly built
metric must land near ratio 1. It reads 1.02 / 0.30 / 0.44. Nothing in the harness is manufacturing
rule effects.

#### 🔴 WHAT T3 DOES NOT DO — OPEN DECISION 14 STAYS OPEN

* **`G7.18` IS NOT EVALUATED.** Its escalation trigger is *"if peak demand differs by more than 25 %
  between rules"*, and `RL21`'s second metric is annual heating and cooling **energy**. Both are
  EnergyPlus outputs. **Nothing above is a watt**, and no number in this entry may be substituted for
  the trigger.
* DoD items 1, 2 and 5 of work item 7.6 are untouched. What is closed is **item 3** (the pre-screen)
  and **item 4** (the vocabulary check), and item 4 is closed with the finding that its reference
  value does not exist rather than with the value.
* The step document already warns that the pre-screen is *"a **screen, not a substitute** — `RL21`
  claims a shift in it 'guarantees' a shift in simulated peak, which is an unsupported causal claim
  with an invented threshold."* This run makes that warning concrete from the other side: **the
  screen does not shift at all**, so it cannot guarantee anything, and whether peak demand shifts is
  still entirely unmeasured.
* All 90 cells are `LEG-4 PILOT -- NOT REPORTABLE`, drawn from 600-diary pools whose back-off ladder
  serves four days in ten from a coarser stratum. 🔴 **The rank ordering is monotone and huge on the
  vocabulary axis and would survive a bigger pool; the seed-noise verdicts are the ones a larger pool
  could move, and they must be re-run at Leg-5's `N >= 5,200` before any of them is written into the
  paper.**

### 2026-08-22 (night, third entry) — 🟢 **T5: THE THREE-ARTEFACT CLOSURE IS DISCHARGED, AND TWO STATUS LINES THAT HAD BEEN FALSE FOR EIGHT DAYS ARE CORRECTED.**

| artefact | was | now |
|---|---|---|
| `4thJ_07_constrainedGeneration.md` STATUS | *"OPEN. Mechanism decided by `RL12`. **Nothing built.**"* | a seven-row work-item table with the true state of each, plus a new progress entry |
| `4thJ_07_constrainedGeneration_val.md` STATUS | *"OPEN. **Nothing built.** All thresholds pre-registered."* | what is built, what is genuinely unbuilt, and why every Leg-4 number is not a result; plus a new progress entry |
| `4thJ_07_constrainedGeneration_val.md` perturbation table | three rows touching the schedule gates | five — the two `FINDING 95` falsifiers added and marked as additions |
| `../Prompts/RESUME.md` | — | updated after **each** task, four times |

🔴 **Both STATUS lines said "Nothing built" while the progress log beneath them carried fifteen
entries of built and run work.** Corrected in place and the correction is stated rather than quietly
applied: a status line nobody maintains is how a reader concludes an entire step is untouched, and
this one would have been read that way by the next cold agent, by a co-author, and eventually by us.

Backups before the edits: `4thJ_07_constrainedGeneration.md.bak_20260822night2` and
`4thJ_07_constrainedGeneration_val.md.bak_20260822night2`.

---

## STATUS OF THIS DOCUMENT

**T1–T5 COMPLETE.** Every task on the list at the top of this document ran to the end. Nothing in it
was submitted to Speed, and no GPU was used.

| | task | result |
|---|---|---|
| `T1` | the emitter | 🟢 built, selftest 52/52 |
| `T2` | `G7.14`–`G7.17` + perturbations | 🟢 5 PASS / 0 FAIL × 3 folds, all five seen falling, six perturbations run |
| `T3` | the chaining pre-screen | 🟢 90 cells, selftest 40/40, the pre-registered null returned |
| `T4` | the vocabulary reference on the real corpus | 🟢 computed — and `FINDING 96` is that the criterion has no reference |
| `T5` | three-artefact closure | 🟢 discharged |

### 🔴 WHAT IS OWED, AND TO WHOM

**To the author, needing a ruling and nothing else:**

* **`D-S7-6`** — how households enter the synthetic population (`FINDING 93`). Nothing downstream can
  claim a household-level result until this is answered, because right now the households are
  surveyed ones wearing generated days.
* **`FINDING 94`** — presence versus activity-resolved gains. One sentence either way; the emitter
  already carries both artefacts.
* **the schedule calendar year** — one of the two years of each survey pair. `es` 2010 / `uk` 2014 /
  `it` 2013 were used and are recorded, not ruled.

**To the GPU queue, needing nothing from anybody:**

* work item **7.2** (job `1286208`) → `G7.12`
* the **Leg-5** campaign (job `1286209`) → every reportable diary in the paper
* the **untuned-base** firing-rate arm → `G7.7` control 1
* the **rejection-sampled control** at ≈22,500 / 8,800 / 15,700 draws → `G7.9`, DoD item 5
* **`G7.18`** — EnergyPlus, Step 8. **Open decision 14 stays OPEN.**

### 🔴 THE ONE THING THAT MUST BE RE-RUN, NOT INHERITED

Every number in this document is measured on **600-diary Leg-4 pools from a 1B backbone**, whose
back-off ladder serves four days in ten from a coarser stratum. The **vocabulary ordering** is
monotone across six rule points on three folds and would survive a bigger pool. The **seed-noise
verdicts would not necessarily**: a larger pool narrows the within-rule spread and could turn a
coincidence metric from "tells us nothing" into a real effect. 🔴 **The pre-screen must be re-run at
Leg-5's `N >= 5,200` before any of its verdicts is written into the paper**, and the back-off ladder
re-measured at the same time rather than assumed to have improved.

---

### 2026-08-22 (night, fourth entry) — 🟢 **JOB `1286208` RETURNED: WORK ITEM 7.2 IS MEASURED. 🔴 `G7.12` STAYS FAIL, AND IT IS RIGHT TO — THE REPORT'S KV-MEMORY HALF IS 3.05x THE PHYSICAL CARD (`FINDING 97`).**

Job `1286208` COMPLETED in **00:06:55** on node `speed-40` and wrote
`outputs_step7/throughput_comparison.{md,json}`. Both fetched (md5 `51b94ccface7e02747e8826cb28a6280`
and `c4cb5e9be3564c4734ef9ace70387a09`); the re-derivation below ran **on the laptop**, needed no GPU,
and is reproducible from `outputs_step7/throughput_evidence/` (`recheck.py`, `recheck.json`, and the
model's own `olmo3_7b_config.json`, md5 `b122791d9a8cdc622d16dca564eaecd4`).

#### 🟢 The measured half, which is what the campaign is sized from

`N = 200` prompts from the Step 5 `es` pool, constrained (completion root), `T = 1.3`, seed 42,
`max_model_len` 2048, both backbones **base, no adapter, eager mode** — so every rate is a floor, and
the comparison is like-for-like because both were measured the same way in the same job.

| | `allenai/Olmo-3-1025-7B` | `Qwen/Qwen2.5-7B` | OLMo / Qwen |
|---|---|---|---|
| **diaries / second** | 22.5331 | 26.9839 | **0.835** |
| output tokens / diary | 100.73 | 140.62 | 0.716 |
| max concurrency @ 2048 | 227.14 | 508.80 | 0.446 |
| engine load (s) | 171.98 | 204.62 | |

🔴 **The headline, and it is a paper sentence:** the step document's KV-cache argument predicts a large
throughput penalty for OLMo. **Measured, there is almost none — 0.835x.** The reason is visible in the
same table: OLMo spends **0.716x** as many output tokens per diary, so the per-token cost is very
nearly cancelled by needing fewer tokens. The backbone choice does not have to be defended on
throughput.

#### 🔴 `FINDING 97` — the KV-memory rows are not a measurement, and one of them is impossible

`throughput_comparison.md` reports OLMo's KV pool as **227.141 GiB**. The named GRES is one
`nvidia_a100_7g.80gb`: **74.506 GiB of physical memory**. The reported figure is **3.049x the entire
card**, so it cannot be describing anything the engine allocated.

The cause is in the emitter's derivation, not in the engine. `kv_bytes_per_token` is computed as
`2 x num_hidden_layers x num_kv_heads x head_dim x 2`, which assumes **all 32 layers are
full-attention**. OLMo 3's own config says otherwise:

```
"layer_types": 24 x sliding_attention + 8 x full_attention,  "sliding_window": 4096
```

Accounting only the **8 full-attention** layers gives `131,072` bytes/token and an implied pool of
**56.785 GiB** — within **1.135 GiB of Qwen's 55.650**, which is the independent check: two ~7B bf16
models on the same card at the same `gpu_memory_utilization = 0.9` must land within about a gigabyte
of each other, and corrected they do. The reported figure is **exactly 4.0x** the corrected one, which
is `32 / 8`.

| | reported | corrected | |
|---|---|---|---|
| OLMo KV bytes / token | 524,288 | **131,072** | 4.0x overstated |
| OLMo KV pool | 227.141 GiB | **56.785 GiB** | vs Qwen 55.650 |
| **OLMo / Qwen bytes per token** | **9.14x** | **2.29x** | the step document's *"about nine times larger"* |

🔴 **The step document's "no GQA, so about nine times larger per token" is confirmed nowhere.** It is
true of the *config field* `num_key_value_heads` and false of the *cache the engine builds*, because
three quarters of OLMo 3's layers never cache more than a 4,096-token window. The correct multiplier
at our sequence lengths is **2.29x**, and the two models end up allocating **the same pool to within
2 %**. Nothing about the campaign sizing changes — `max_concurrency` and `kv_cache_tokens` come
straight from `num_gpu_blocks x block_size` and are untouched — but the *sentence* must not be
written as it stands.

#### 🔴 And there is no peak-memory measurement at all

`torch_peak_allocated_gib` is **0.0 in both rows**. vLLM v1 runs the model in a worker process; the
parent's allocator never sees it, so the field is structurally null rather than small. Between an
impossible pool figure and an identically-zero peak, the report has **no valid peak-memory value**.

#### 🔴 Therefore `G7.12` does NOT move to PASS

`G7.12` requires `throughput_comparison.md` to exist, cover **both** backbones, and report
**diaries/second AND peak KV memory**. Three of four clauses are satisfied on this artefact. The
fourth is not, on the artefact's own numbers. **`G7.12` stays FAIL on all three folds**, and this is
the gate behaving exactly as a gate should: it was pointed at a quantity, the quantity arrived wrong,
and the gate is what noticed. It moves when the emitter's KV derivation reads `layer_types` and a real
peak is read from the worker (`vllm` reports it in the engine log) — **a re-run, but a 7-minute one.**

#### 🟢 The fix is written and DEMONSTRATED, offline, and staged — but NOT submitted

`tools/4thJ_step7_throughput.py` patched **additively** (backup `.bak_f97`, staged on Speed at
md5 `75ff9842fa6a22f993c940c9fe711e2d`):

| change | why |
|---|---|
| `layer_types` and `sliding_window` read from the config | the fact the derivation was missing |
| `kv_bytes_per_token` now counts **full-attention layers only** | 131,072 for OLMo, unchanged 57,344 for Qwen |
| `kv_bytes_per_token_all_layers_assumption` kept beside it | the old number stays readable, named for what it assumes |
| `device_total_gib` / `device_used_gib` from `torch.cuda.mem_get_info()` | a real device measurement, which is what `G7.12` was actually asking for |
| `torch_peak_allocated_gib` → **`None`** when zero, plus `torch_peak_is_null_in_parent_process` | a structurally null field must not print as a measured `0.0` |
| 🔴 **`kv_cache_gib_exceeds_device`** — refuses aloud if the derived pool is larger than the card | the guard whose absence is the whole of `FINDING 97` |

`tools/4thJ_step7_throughput_selftest.py` — **24 ok / 0 FAILED**, on a laptop, with the engine faked
from the two models' real shipped shapes. It checks the hybrid is counted (24 + 8), that the old
figure is **exactly 4.0x** the new one, that Qwen is **untouched** by the fix, that the two corrected
pools land **1.135 GiB apart** as two 7B bf16 models on one card must, that the guard **fires on
227.141 and is silent on 56.785**, and — section 6 — that the shipped artefact still contains the
numbers this test was written from, so the regression cannot quietly detach from its evidence.

🔴 **NOT SUBMITTED, deliberately.** The only `nvidia_a100_7g.80gb` on the node is running job
`1286209`, the Leg-5 `es` fold, which is the critical path for every reportable diary in the paper. A
7-minute throughput re-run is not worth contending for it. Submit `sbatch 4thJ_step7_throughput.sh 200`
once `1286209` is done; `G7.12` moves on that run and on nothing else.

---

### 2026-08-22 (night, fifth entry) — 🟢 **THE FOUR AUTHOR ITEMS ARE ON ONE DOCKET, AND MEASURING ONE OF THEM PRODUCED `FINDING 98`.**

`IMP/docs/2026-08-22_step7-four-items_D-S7-6_D-S7-7_D-S7-8_decision-14.md`. It carries the complete
set of things Step 7 waits on a **person** for; everything else Step 7 owes is owed to the GPU queue.
Two decision ids are opened by it: **`D-S7-7`** (presence vs activity-resolved gains, i.e. `FINDING
94` given a number so it can be ruled and closed) and **`D-S7-8`** (the schedule calendar year, which
had been recorded and never assigned an id). `D-S7-6` and open decision 14 are restated with the
evidence that now exists. **Nothing was changed on disk to write it** — no gate re-scored, no tool
edited, no cell re-emitted, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

#### 🔴 `FINDING 98` — the `hid` fallback of `FINDING 93` is weaker than "surveyed households" sounds

Measured on `harmonised.parquet` by grouping `(country, hid)`. **A `hid` group is the set of household
members who kept a diary, not the household.**

| | `es` | `uk` | `it` |
|---|---|---|---|
| `hid` groups | 9,541 | 4,229 | 18,435 |
| mean diarists per group | 2.006 | 1.876 | 2.075 |
| exactly one diarist | 31.46 % | 39.44 % | 35.28 % |
| 🔴 ... members NOT labelled `one_person` | **13.50 %** | **12.37 %** | **2.98 %** |
| `couple_with_children` groups on one diarist | **10.50 %** | **11.96 %** | **1.58 %** |
| ... mean diarists in them | 2.46 | 2.25 | 3.03 |

🔴 **Between 3 % and 13.5 % of the "households" the chaining experiment runs on are multi-person
households represented by a single person, country-correlated with a 4.5× spread.** The co-presence
half of `G7.4` sees partners and children who have no day at all and will read that absence as
structure. ⚪ Zero groups mix household types, so the label is internally consistent; what is missing
is people. This changes nothing that was run — it changes what `D-S7-6` option (a) may claim: not
"surveyed households" but **"the diarist members of surveyed households"**, quoted per fold.

#### 🔴 The recorded rationale for the schedule year selects nothing, and the choice is inert today

`es` 2010 / `uk` 2014 / `it` 2013 were recorded as "the non-leap year of each survey pair". Checked:
**none of the six candidate years (2009, 2010, 2013, 2014, 2015) is a leap year**, so the stated rule
does not discriminate in any fold. And all six are identical in composition — **365 days, 261
weekdays, 52 Saturdays, 52 Sundays** — so the year cannot move a mean presence or any annual
aggregate. What it moves is the **ordering**: which date is a Saturday. That is irrelevant while the
schedules stand alone and becomes a basis choice the moment `D-S8-2` item 6's actual-meteorological
year is attached, which is why `D-S7-8` recommends ruling the *rule* (first year of the fixed
twelve-month window) rather than the three years.

#### 🔴 And `D-S8-2` item 6's proposed window rule is not computable from what we hold

`harmonised.parquet` carries **no diary date and no diary year** — only `wave` and
`strat_season_raw`, which is a different object per country: `es` `TRIM` calendar quarters with **no
month field anywhere in the delivery** (`F-ES-9`), `it` `meseri` banded **Nov-Jan / Feb-Apr / May-Jul
/ Aug-Oct** and not readable finer (`F-IT-2`), `uk` `dmonth` at month resolution. Diary shares are
`es` 25.60/26.19/25.11/23.10 %, `it` 26.56/25.44/24.12/23.89 %, `uk` 5.42 % (Dec) to 12.12 % (Oct).
**Two consequences:** fieldwork covers the whole annual cycle in all three countries, so neither year
of a pair is "the" survey year; and Italy's Nov-Jan band straddles the calendar boundary by
construction, so about a quarter of Italian diaries cannot be placed in a calendar year **even in
principle** from our data. Fixing the window is a documentation task — the published fieldwork
calendars — exactly as item 6 already says of its own items (1)–(3).

⚪ Recorded, not a finding: the emitter's day types are `weekday / saturday / sunday`, so **public
holidays simulate as ordinary weekdays** in every country. That is a property of `strat_day_type`, not
something introduced here, and no year choice repairs it.


---

## 2026-08-22 (night, sixth entry) — 🟢 **THE AUTHOR RULED ALL FOUR DOCKET ITEMS, ALL FOUR (a), AND ALL FOUR ARE APPLIED. 🔴 APPLYING `D-S7-8` PRODUCED `FINDING 99`.**

The docket written in the fifth entry came back ruled the same night. It has moved to
`IMP/docs/DONE/2026-08-22_step7-four-items_D-S7-6_D-S7-7_D-S7-8_decision-14.md` and carries the
author's rulings and rationale verbatim, under the options they were ruled against.

⚪ **Nothing was re-scored, re-emitted or re-run to apply them.** `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` is untouched — none of the four is a pre-registered quantity.
The only executable touched is `tools/4thJ_step7_schedules.py`, and only its module docstring;
`4thJ_step7_schedules_selftest.py` re-run after the edit: **52 ok, 0 FAILED**.

### What each ruling moved

| item | ruled | applied where |
|---|---|---|
| `D-S7-6` household basis | **(a)** surveyed composition, declared per fold | `4thJ_07_constrainedGeneration.md` §7.6 — declaration + `FINDING 98`'s per-fold numbers |
| `D-S7-7` internal gains | **(a)** presence signal (`D-S8-2` item 5) | same doc: DIARIES TO SCHEDULES bullet rewritten, §7.7 corrected, emitter docstring corrected |
| `D-S7-8` calendar year | **(a)** first calendar year of the `D-S8-2` item 6 window | same doc §7.7; the "non-leap" rationale struck |
| decision 14 | **(a)** closes in Step 8 on `G7.18` | same doc §7.6 (sizing + interim `independent`), DoD item 6 marked discharged in Step 8 |

🔴 **The contradiction `FINDING 94` named is gone.** Two lines in the step document claimed
activity-resolved gains against a ruled interface that is a **fraction**. Both now state the ruled
interface and name why no other is available: `RL25` was commissioned for an activity→power mapping
and its Part C figures were rejected as unsourced. Reinstating activity-resolved gains later needs a
**source**, not a GPU run — the emitter already keeps each pool day's activity codes beside the
presence signal.

### 🔴 `FINDING 99` — the ruled year rule is sufficient only for a January-start window

`D-S7-8` (a) says the schedule runs on **the first calendar year of the twelve-month weather window**
`D-S8-2` item 6 fixes. Checked against what the emitter can actually do:

| condition | consequence |
|---|---|
| window is January–December | 🟢 exact weekend coincidence for all 8,760 hours, which is what the ruling wants |
| window straddles two calendar years (e.g. Jul 2013 – Jun 2014) | 🔴 the schedule aligns for the first six months and is off by one or two weekdays for the rest |
| straddling window containing 29 February | 🔴 8,784 hours — `year_day_types()` refuses it outright, and no `Schedule:File` in this project accepts it |
| any straddling window | 🔴 the emitter takes `--year` and has **no window-start parameter**; honouring one needs an additive change to `tools/4thJ_step7_schedules.py` |

⚪ **It needs no ruling.** It is a constraint handed to `D-S8-2` item 6: prefer a calendar-year
window, or accept a partial weekday alignment and declare it. Recorded in §7.7 of the step document
and in the Step 8 document, not fixed — there is no window to fix it against yet.

### 🔴 What the rulings do not close

* `D-S7-6` (a) is a constraint on **claims**: household-level quantities (`mean_pair_corr`,
  `trough_aggregate`, co-presence) are measured on **the diarist members of surveyed households** —
  `FINDING 98`, 13.50 / 12.37 / 2.98 % single-diarist multi-person groups, a 4.5× country-correlated
  spread — and are read **per fold or not at all**. One row is owed in the paper's asymmetry table.
* Decision 14 (a) rules **order**, not readiness. `G7.18` is blocked behind an IDF that does not exist
  and five open §6 geometry/zoning decisions. Step 7's DoD item 6 therefore cannot close inside
  Step 7; it is discharged in Step 8.
* The CPU pre-screen's seed-noise verdicts stand on 600-diary Leg-4 pools on a 1B backbone. **They
  must be re-derived at Leg-5's `N >= 5,200`, with the back-off ladder re-measured rather than
  assumed to have improved, before any of them is written into the paper.** CPU-only, minutes.

### State

Job `1286209` (Leg-5 `es`) still owns the only A100 `7g.80gb` slice; `G7.12`'s 7-minute re-run stays
staged behind it. **No decision in this project is now waiting on a person.**

### 2026-08-26 (early) — 🔴 **THE EMITTER NOW PUTS THE SERIES ON THE CLOCK ENERGYPLUS READS IT ON, AND EVERY BUNDLE ON DISK IS RE-EMITTED. `D-S9-3`(a).**

`FINDING 141`, found by Step 9 and ruled by the author the same day: `D-S2-5` harmonised every diary
onto a **04:00** day origin, `write_schedule_csv` put minute 0 into a `Schedule:File`, and EnergyPlus
reads a `Schedule:File` from **midnight**.

🟢 **The change is `rotate_to_midnight()` and one call, and it is declared in three places at
once**: `DIARY_ORIGIN_HOUR = 4` in the module, `"rotated_to_midnight": true` and
`"diary_origin_hour": 4` in every manifest, and a line in the emitter's own stdout.

🔴 **The rotation is cyclic over the YEAR, not within each day.** A diary day covers 04:00 of
day *D* to 04:00 of day *D+1*, so its last four hours belong to the **next** calendar day; rotating
each day inside itself would move them backwards by twenty hours instead of forwards by four. The
selftest distinguishes the two on a two-day fixture rather than asserting the intent in a comment.

🟢 **The change is exactly the rotation and nothing else, and that is checked rather than
claimed.** `--no-rotate` reproduces the shipped pre-rotation bundle **byte-for-byte, 100 of 100
presence files and the `.idf`**. And the rotated emission agrees with
`tools/4thJ_step9_trigger.py`'s **independent** implementation on all 100 x 8,760 values — two
implementations, written a day apart, compared at six decimals.

🟢 **Step 9's byte-for-byte guard now carries that comparison permanently.**
`_assert_same_dwellings` rotates its own rebuilt series with Step 9's function before comparing it to
Step 7's file on disk, so the check that proves Step 9 is modelling Step 8's dwellings **also** proves
the two rotations agree. **300 of 300 across the three folds**, and **seen failing** when pointed at
the pre-rotation bundle (`household 02202 ... first difference at line 4`).

⚪ **Sixteen bundles re-emitted**: `leg5_{es,uk,it}_independent_seed1` (the campaign's, calendar
2017), the three `_cal20XX` calendar-probe bundles, the three `leg4` pilots, the six perturbation
cells, and the new `perturb_norotate`. The pre-rotation tree is kept at
`Step7_docs/outputs_step7/schedules_bak_prerotation/` — it is `G8.17`'s falsifier and it is also the
artefact Step 8's 13,108 runs actually consumed.

⚪ Selftest **61 ok / 0 FAILED** (was 52; nine new checks, all on the rotation). Backups
`.bak_prerotation` on the emitter, its selftest, the schedule gates, the Step 8 injected gates and the
Step 9 trigger.
