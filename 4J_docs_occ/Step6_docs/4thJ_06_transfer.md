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

Train on the other two countries. Generate a population for the held-out country conditioned **only on
its published demographic marginals**, with none of its diaries seen. Score against its published
aggregate tables: `tus_00age`, `tus_00educ`, `tus_00selfstat`, `tus_00hhstatus`, and `tus_00startime`
for the time-of-day curve.

🟢 **THE TABLE LIST ABOVE WAS CORRECTED IN ONE EDIT ON 2026-08-19, UNDER D-S6-2 RULED (a). It
originally read `tus_00hh` and `tus_20startime`.** `tus_00hh` **does not exist** — Eurostat returns
`ERR_NOT_FOUND_4` and it is absent from the catalogue; the intended table is `tus_00hhstatus`.
`tus_20startime` is the HETUS **2020** wave, whose coverage is `AT BG DE EE FI NO RS` and which
contains **none of Spain, Italy or the UK**; the correct table is `tus_00startime` (`{2000, 2010}`,
145 start-time slots = 10-minute resolution, all three countries returning data). **Both are
corrections of fact: the quantity each threshold is written against is published under the corrected
name, and the thresholds are expressed against the quantity, not the string.**

🔴 **THE SAME RULING CARRIES A LIMITATION THIS PARAGRAPH DOES NOT REMOVE.** Eurostat's `2010`
column for **Italy** is the **2008-09** survey, while our Italian microdata is ISTAT **2013-14** — a
wave that appears in **no Eurostat HETUS aggregate table at all**. D-S6-2 ruled **(a)**: the `it` fold
is scored against the 2008-09 tables and the ~5-year gap is declared as a limitation **on that fold
only**. `es` and `uk` are exact-basis. **The LOCO result is therefore not basis-uniform across its
folds; report the folds separately and never average the gap away.** Full entry at the end of this
file, dated 2026-08-19 (evening).

🔴 **N = 3, NOT 4. CORRECTED 2026-08-19.** This paragraph read *"N = 4 after author decision 5, so
training is on three. Italy, Spain, UK, France."* **Author decision 16, taken 2026-08-15, EXCLUDED
FRANCE.** The corpus is **Italy, Spain and the UK**, each fold trains on **two**, and the rotation is
three folds rather than four. That is thinner than the sentence it replaces, it is limitation C4, and
**Track A is the only thing that raises it.** 🔴 **The old sentence's closing clause — "our four waves
are the HETUS 2010 round" — was also wrong on a second count and must not be recycled: D-S6-2
established that Italy's 2013-14 wave is in NO Eurostat HETUS round at all.** Spain's 2009-10 and the
UK's 2014-15 are the 2010 round; Italy's is a national wave sitting between two European rounds.

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
| ✅ **No country is chosen: all four are held out in turn** | **Decision 11, CLOSED by the author 2026-08-14** |
| No forecast, no year token | Author decision 3, `RL16` |
| The privacy audit runs here | `RL10` |

✅ **Decision 11 is CLOSED, 2026-08-14, and it closed by removing the choice rather than by making
it.** The author was asked which country to hold out and answered: **all of them, in turn.** 🔴 **Three
leave-one-country-out folds, three adapters, three reported results, from 2026-08-15** — author
decision 16 excluded France, so the rotation is over Spain, the UK and Italy. *(Was four and four.)*
**Rotation is what closed the decision and rotation is unchanged; only its length moved.**

🔴 **The pre-named fold did NOT move, and that is the part that matters.** It was fixed in advance by
alphabetical ISO code — **ES, FR, GB, IT** — so Spain was first with France in the set and **is still
first without it**. Held-out Spain survives the corpus change by the rule written down before anything
was trained. Had the rule selected France, the honest move would have been to re-run the rule and say
so loudly, never to slide to the next-best fold.

🔴 **And the window closes here, not at Step 4.** If France arrives before **any fold has been
scored**, it can be re-admitted in full and the rotation returns to four. **Once the first fold is
scored, the design is frozen** and France can only ever be an extra held-out country reported
separately as an out-of-design test — never a fourth fold, never averaged into the rotation.

**Why that is the stronger closure.** The hazard was never which country got picked. It was that a
picked country can be picked *late*, after results are visible, and nothing repairs that afterwards.
**Rotation leaves nothing to pick.** It also turns the paper's single most fragile number into a
distribution over four folds, which is what separates "transfer works" from "transfer works for Spain".

🔴 **Two conditions are pre-registered in work item 6.1 and are not optional.**

1. **All **three** folds are reported, including the worst *(was four; author decision 16, 2026-08-15, excluded France — the reporting clause itself is unchanged and still forbids dropping or explaining away the worst)*.** Reporting the best fold, or dropping one as
   anomalous, is choosing the held-out country late by a different door. **A fold may be *explained*;
   it may not be *removed*.**
2. **No fold's result may change the design.** Once any fold has been evaluated, architecture, prompt
   format, hyperparameters, gates and thresholds are frozen for the remaining folds. A change made
   after seeing fold 1 contaminates folds 2 to 4, and the contamination is invisible in the output.

**A second hold-out exists and must never be confused with this one.** A random sample of households is
held out from *within* the training countries as an ordinary test set. It measures whether the model
reproduces data whose country it has already seen — which is what papers 1 to 3 measure. 🔴 **It is a
sanity check. It is never reported as transfer, and it never appears in the same table as the fold
results.**

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

🔴 **Two clauses that decision 11 puts here, and the pre-registration is incomplete without them.**

* **Reporting clause.** All **three** folds are reported, including the worst *(was four; author decision 16, 2026-08-15, excluded France — the reporting clause itself is unchanged and still forbids dropping or explaining away the worst)*. A fold may be explained; it
  may not be removed, averaged away, or relegated to an appendix. **Selecting a fold after the fact is
  choosing the held-out country late by a different door**, which is the exact defect rotation was
  adopted to prevent.
* **Freeze clause.** Once **any** fold has been evaluated, the design is frozen for the rest:
  architecture, prompt format, hyperparameters, decoding constraints, gates and thresholds. A change
  made after seeing fold 1 contaminates folds 2 to 4 and **the contamination does not show up anywhere
  in the output.** If a change is unavoidable, every fold is re-run from the new design and the old
  results are discarded, not mixed.

**Also pre-registered here: the second hold-out.** A random household sample inside the training
countries, its size and stratification fixed in advance, kept as an ordinary test set. 🔴 **Named in
the pre-registration precisely so it cannot later be presented as evidence of transfer.**

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

Steps 4, 5 and 7. ✅ **Decision 11 no longer blocks it: closed 2026-08-14, four-fold rotation.**

---

## DEFINITION OF DONE

1. ✅ **DONE 2026-08-18.** Pre-registration frozen and hashed **before** the first fold — md5 `e4243e07cdd80c9c846b91f40e3e8c45`, sidecar `outputs_step6/prereg.md.md5`, and no training run of any leg existed at the time.
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

### 2026-08-14 (second entry) — decision 11 closed, and the step is no longer blocked by it

* ✅ **Four-fold rotation. Every country held out in turn.** The author closed decision 11 by removing
  the choice rather than making it, which is the stronger closure: **a country that is never picked
  cannot be picked late.**
* **Two conditions written into "WHAT IS ALREADY DECIDED" and into work item 6.1**: all four folds are
  reported including the worst, and no fold's result may change the design once any fold has been
  evaluated. 🔴 **Both exist because rotation without them gives back exactly what it bought** — the
  freedom to select is simply moved from before the runs to after them.
* **A second hold-out is now named separately**: a random household sample inside the training
  countries, kept as an ordinary test set. It answers a different question and **never appears in the
  same table as the fold results.** The author proposed it as an alternative to holding out a country;
  it is retained as a companion instead.
* **Cost accepted: four Leg-5 fine-tuning runs instead of one**, four at Leg-4 where the 1B pilot makes
  rotation nearly free. Step 4's output contract already said "one adapter per leave-one-out fold", so
  nothing downstream changes shape.

---

### 2026-08-18 — 🟡 **`prereg.md` is WRITTEN. It is NOT FROZEN, and one open decision is the reason.**

`outputs_step6/prereg.md` now exists. **Work item 6.1 is drafted, not discharged** — the deliverable
is a *frozen* file with a recorded md5, and this one carries the literal string `NOT YET FROZEN` in
its freeze block. 🔴 **`G4.14` must FAIL against it in its present state, and that is correct
behaviour, not an outstanding bug.**

**Why it could be written at all today.** The blocker was named precisely in
`4thJ_00_HETUS_LLM_Pipeline.md` — *"its second hold-out's stratification depends on a corpus that does
not exist"* — and that corpus now exists: `4J_step3_corpus.jsonl`, 73,254 records, emitted by Speed
job `1257441` and checked by a twenty-gate battery. Nothing else was waiting on anything.

**Why it was not frozen.** Two reasons, and neither is caution for its own sake:

* **The deadline is not now.** §4.2-bis of `4thJ_04_finetuneLLM.md` freezes this file **before the
  first Leg-5 training job**, not before Step 6 scores anything. No training job has been submitted.
  **Freezing early buys nothing. Freezing late is fatal** — after a model exists, a pre-registration
  is a description of it.
* 🔴 **One item in it is genuinely open — D-S6-1 — and a pre-registration frozen with an open item is
  a pre-registration that will be edited.** That is the precise defect `G4.14` was added to catch, so
  freezing over it would have been the document defeating its own gate.

### 🔴 D-S6-1 — the second hold-out is specified in HOUSEHOLDS and was built in RESPONDENTS

**The finding.** This document specifies the second hold-out as *"a random sample of **households**"*.
The corpus was split by **respondent**, keyed `(country, hid, pid)` — 65,334 respondents, 10 %, seed
42, giving **6,533 held out / 58,801 train** with `SPLIT INTEGRITY: intersection = 0`.

🔴 **The build script flagged this itself and was not read.** `4thJ_step3_build.py` line 20 records
the respondent split as *"ASSUMPTION, not"* decided. It declared its own uncertainty in the right
place instead of presenting a choice as a specification — **the disclosure worked and the reading of
it did not.** That is the useful half of this finding.

**Why it is not cosmetic.** Household members share a dwelling, a day and most of a routine. A
respondent-level split puts one member in train and another in test, so **the in-country test set is
easier than it looks**. This hold-out's entire job is to be an honest in-country baseline against
which the transfer folds are read. An inflated baseline does not flatter the transfer result — it
makes it look *worse*, which is the direction least likely to be questioned and therefore least
likely to be caught.

**Both options are live today and neither rebuilds `harmonised.parquet`.** `hid` is a column of the
D-S2-12 record contract **and is written onto every corpus record**, so a household split is
recomputable from `4J_step3_corpus.jsonl` alone.

* **(a)** keep the respondent split, and record the leak as a stated limitation with the
  household-level figure measured and reported beside it;
* **(b)** re-split by `(country, hid)`, 10 %, seed 42, re-emitting **the `split` label only**.

🔴 **Recommended: (b).** It is what this document already says; it is the stricter of the two; the
change is a **re-label, not a rebuild**, so no record text moves and the Step 3 twenty-gate battery
does not need re-running; and it is being made **before any model exists**, which is the only moment
at which changing a hold-out definition costs nothing and means anything.

**§7 of `prereg.md` freezes the moment D-S6-1 is ruled**, with the measured per-country counts written
in from the split's own output. They are deliberately absent now: **a pre-registration containing an
unmeasured number is worse than one containing an open question.**

### Two stale cross-references found while drafting, recorded and not silently fixed

* 🔴 **`4thJ_04_finetuneLLM.md` §4.3 still reads "Primary, four runs … Each trains on the other three
  countries."** Decision 16 made that **three runs, each training on the other two**. §4.2 of the same
  document was updated for decision 16 and §4.3 was not, so the file disagrees with itself two
  sections apart. `prereg.md` §2 carries the correct table and says explicitly that it is the
  authority over any older wording.
* **This document's own EXPERIMENT section still opens "N = 4 … Italy, Spain, UK, France."** It is
  corrected further down the same file, so the document is self-inconsistent in the same direction.
  **Both are left in place** — a spec is amended by its author, and a session that quietly harmonises
  two documents to each other destroys the evidence that they ever disagreed. The correct reading is
  recorded here and in `prereg.md` §2 instead.

**What this step now owes, and it is new:** 🔴 **a split report for the UK fold** — its scores for
`strat_hh_type = unknown` versus the rest — created by **D-S3-14** on 2026-08-18. 551 UK diaries carry
a value neither training country emits. If the split cannot be produced, it is reported as
un-quantified **and said to be so**, never omitted.

**What was NOT verified while drafting this.** The published Eurostat aggregate tables named in the
EXPERIMENT section (`tus_00age`, `tus_00educ`, `tus_00selfstat`, `tus_00hh`, `tus_20startime`) were
**not opened, not downloaded and not checked to exist** for the three countries at the waves we hold.
`prereg.md` names them because this document names them. 🔴 **Every threshold in §6 is expressed
against tables nobody in this project has yet confirmed we can obtain** — that is a real dependency,
it is not a Step 3 or Step 4 problem, and it will be one here if it is left until scoring time.

---

### 2026-08-18 (later) — 🟢 **D-S6-1 RULED (b) BY THE AUTHOR, APPLIED, AND `prereg.md` IS FROZEN. Work item 6.1 is DONE.**

**md5 `e4243e07cdd80c9c846b91f40e3e8c45`**, recorded in `outputs_step6/prereg.md.md5` and here, in an
append-only log, on **2026-08-18**. At the moment of freezing `outputs_step4/` held exactly one
artefact — `staged_weights.json` from job `1245620` — and **no training run of any leg existed**, so
the §4.2-bis deadline was met with room rather than met narrowly.

🔴 **The md5 is deliberately NOT printed inside `prereg.md`: a file cannot contain its own hash.**
Writing the value in changes the value. It lives in the sidecar and in this entry, and `G4.14`
recomputes it **from the file on disk** (`V4.g`) and compares. Reading the value out of the manifest
being checked is the circularity that retired `G1.7b` in Step 1, and it has not been reintroduced.

### The re-split: Speed job `1266814`, `COMPLETED`, `0:0`, 00:00:48

`tools/4thJ_resplit_household.py` moved the second hold-out from respondent `(country, hid, pid)` to
household `(country, hid)`, keeping seed 42 and fraction 0.10 and **mirroring the build's selection
procedure line for line** — a different shuffle would have confounded *"we changed the unit"* with
*"we changed the draw"*.

| | before (respondent) | after (household) |
|---|---|---|
| units | 65,334 respondents | **32,205 households → 3,220 / 28,985** |
| diaries held out / train | 7,343 / 65,911 | **7,328 / 65,926** |
| held-out record fraction | 0.1002 | **0.1000** |

Per country after the change — es 17,332 / 1,808 diaries (8,640 / 901 households), it 34,366 / 3,894
(16,532 / 1,903), uk 14,228 / 1,626 (3,813 / 416).

### 🔴 The leak was far larger than the argument for fixing it assumed

It was measured **before** it was removed, which is the only order in which the number means anything:

* **4,900 households straddled the old split** — members on both sides — **15.22 % of all households
  and 23.30 % of the 21,031 multi-respondent households**;
* **15,429 records, 21.06 % of the corpus**, sat inside a straddling household;
* per country: es 1,448 · it 2,883 · uk 569.

**A fifth of the corpus.** The case for (b) was argued from principle — household members share a
dwelling, a day and most of a routine — and the measurement came back an order of magnitude more
serious than "a technicality worth tidying". 🔴 **And the direction is the one that hides:** an
inflated in-country baseline does not flatter the transfer result, it makes transfer look *worse*, so
nobody reading the output would have had a reason to question it.

### It was a re-label, and that was proved rather than asserted

Verified from disk against a size-matched backup taken before the write, record for record:

```
records compared              : 73254
records whose TEXT differs    :     0
records whose KEY  differs    :     0
records whose LABEL changed   : 13149   (the intended change)
households straddling the new split : 0
respondents straddling the new split : 0   (65334 respondents)
```

🔴 **No record text moved, so no Step 3 gate is disturbed and the twenty-gate battery does not need
re-running.** The respondent-split corpus is preserved at
`/speed-scratch/o_iseri/4J_step3_corpus_respondent_split.jsonl`; the script refuses to run at all if
that backup already exists or fails its size check. Report:
`outputs_step6/4J_split_report_household.md`.

**Stratification: unstratified by design**, and said so in `prereg.md` §7. This hold-out is a sanity
check, not an estimator, so a simple random draw of households is the honest description of it — and
the per-country counts are reported so the draw can be *seen* rather than a balancing step being
trusted.

### What the freeze now binds

**`G4.14` is live.** Every run manifest carries this md5, all manifests carry the same value, and it
is recomputed from disk at every run. 🔴 **If `prereg.md` is ever edited, `G4.14` fails every run in
the project simultaneously, including runs that had already passed.** That is intended — a
pre-registration whose breach fails only future runs is not a pre-registration.

**What was NOT verified, unchanged from the drafting entry and now carried past a freeze:** the
Eurostat aggregate tables every FAIL threshold is expressed against — `tus_00age`, `tus_00educ`,
`tus_00selfstat`, `tus_00hh`, `tus_20startime` — have still **not been opened, downloaded or confirmed
to exist** for these three countries at our waves. 🔴 **Freezing the thresholds did not make the
tables exist.** This is Step 6's dependency and it is now recorded on both sides of the freeze.

---

### 2026-08-19 — 🔴 **THE EUROSTAT SCORING TABLES WERE FINALLY OPENED. TWO OF THE FIVE NAMES ARE WRONG, AND ONE OF THE THREE COUNTRIES HAS A WAVE MISMATCH.** New: **FINDING 31**, and **D-S6-2** for the author.

**Why this was done now.** Both this file and `prereg.md` carry the same declared omission on both
sides of the freeze — the five tables *"have not been opened, downloaded or confirmed to exist"* —
and this file added the warning *"it will be one here if it is left until scoring time."* Step 4's
`uk` fold (job `1274964`) occupies the GPU for roughly five hours and this check needs no GPU, so it
was taken in that window. 🔴 **It was left until now, and it should not have been: the check took
under an hour and it found real defects in a FROZEN pre-registration.**

**Every claim below was verified against Eurostat's own dissemination API and its own catalogue, not
against a summary and not against DBnomics.** DBnomics was tried first and **is not admissible for
absence**: it reported `tus_00startime` as non-existent when Eurostat's official table-of-contents
lists it, and it answered HTTP `200` for `tus_00hh` with an empty `num_found: 0` payload. Both traps
are recorded because the wrong reading of either would have produced the opposite conclusion.

#### What is correct, and stays

| table | exists | ES | IT | UK | `time` |
|---|---|---|---|---|---|
| `tus_00age` | ✅ | ✅ | ✅ | ✅ | `{2000, 2010}` |
| `tus_00educ` | ✅ | ✅ | ✅ | ✅ | `{2000, 2010}` |
| `tus_00selfstat` | ✅ | ✅ | ✅ | ✅ | `{2000, 2010}` |

Three of the five names are right, exist, and cover all three countries at the `2010` reference year.
Titles as published: *"Time spent, participation time and participation rate in the main activity by
sex and age group / educational attainment level / self-declared labour status."*

#### 🔴 DEFECT 1 — `tus_00hh` DOES NOT EXIST

Eurostat's dissemination API returns a hard 404 for it, for all three countries:

```
ERR_NOT_FOUND_4: TUS_00HH (DATA_FLOW:ALL,1.0) is not available for dissemination
```

It is **absent from Eurostat's official catalogue** (`/api/dissemination/catalogue/toc/txt`), which
lists 20 `tus_00*` codes and 23 `tus_20*` codes and no `tus_00hh` among them. **The intended table
exists under a different code: `tus_00hhstatus`** — *"…by sex and household composition"* — which
does cover ES, IT and UK at `2010`. This is a naming error, not a missing dependency: the quantity
the threshold is expressed against is published, under a name this project never used.

#### 🔴 DEFECT 2 — `tus_20startime` IS THE WRONG WAVE AND COVERS NONE OF OUR COUNTRIES

`tus_20startime` exists, but the `tus_20` prefix is the **HETUS 2020** round. Its coverage is:

```
geo = AT, BG, DE, EE, FI, NO, RS      time = {2020}
```

🔴 **Spain, Italy and the United Kingdom are all absent from it — the string `ES`/`IT`/`UK` does not
occur anywhere in the dataset descriptor.** The whole 2020 wave excludes our three countries
(`tus_20age` geo = BG, DE, EE, HR, HU, NL, AT, PL, FI, NO, RS). **The time-of-day curve is the single
most load-bearing table for an occupancy paper, and the code named for it in a frozen
pre-registration returns nothing for any country we hold.**

**The correct table is `tus_00startime`**, and it is a good fit — better than the one it replaces:

```
label : "Participation rate in the main activity (wide groups) by sex and time of the day (2000 and 2010)"
id    : [freq, unit, sex, startime, acl00, geo, time]
size  : [1, 1, 1, 145, 9, 1, 2]          time = {2000, 2010}
```

ES, IT and UK all return data. **145 start-time slots** is 10-minute resolution across the day, which
is the same grid the corpus is built on — the tally automaton's "multiples of 10" constraint was
already chosen to be compatible with it, by accident rather than by design.

#### 🔴 DEFECT 3 — ITALY'S AGGREGATE TABLES DESCRIBE A DIFFERENT SURVEY FROM ITALY'S MICRODATA

This one is not a naming error and cannot be repaired by renaming. Eurostat's ESMS metadata for the
`tus_00` collection gives the fieldwork years behind the `2010` column, per country:

| country | our microdata (decision 6) | Eurostat `2010` column | verdict |
|---|---|---|---|
| Spain | INE **2009-10** | **2009-2010** | ✅ same survey |
| United Kingdom | ONS **2014-15** | **2014-2015** | ✅ same survey |
| **Italy** | ISTAT **2013-14** | **2008-2009** | 🔴 **different survey, ~5 years apart** |

Confirmed independently of the ESMS page: Italy's contribution to the European 2010 wave is the
*Indagine Multiscopo sulle Famiglie — Uso del Tempo 2008-2009* edition, conducted February 2008 to
January 2009. **The ISTAT 2013-14 wave we hold appears in no Eurostat HETUS aggregate table at
all** — it is not in the 2010 round (which took 2008-09 from Italy) and not in the 2020 round (which
has no `IT` at all; Italy's 2020-round wave is 2022-23). Italy's 2013-14 is a national wave that sits
between two European rounds.

**What this does and does not break.** It does **not** touch Steps 1–4: the corpus, the gates and the
`it` training shard are unaffected, and nothing already run needs re-running. It breaks exactly one
thing, and only for one fold: **when Italy is the held-out country, "score against its published
aggregate tables" scores 2013-14 diaries against 2008-09 published marginals.** For `es` and `uk` the
basis is exact. 🔴 **This is a basis question, not a band question, and by this project's own rule a
basis is registered before the run that reports under it — so it must be ruled before the `it` fold
is scored, not after.**

#### 🔴 D-S6-2 — FOR THE AUTHOR. `prereg.md` IS FROZEN AND HAS **NOT** BEEN EDITED.

`prereg.md` §"What this pre-registration does NOT cover" names all five tables, `tus_00hh` and
`tus_20startime` among them. **It has not been touched and must not be** — its md5
`e4243e07cdd80c9c846b91f40e3e8c45` is what `G4.14` checks on every run in the project, and editing it
would fail every run at once, including the `uk` fold currently on the GPU. **The corrections above
are therefore recorded here, post-hoc and declared as post-hoc, exactly as a basis change is required
to be.** They are not presented as though the pre-registration had them right.

Three things need an author ruling:

1. **The two renames** — `tus_00hh` → `tus_00hhstatus`, `tus_20startime` → `tus_00startime`. These
   are corrections of fact: the intended quantity is published under the corrected name in both
   cases, and the thresholds are expressed against the quantity, not against the string. Recommend
   accepting both as **declared errata against a frozen file**, recorded here and never by editing
   `prereg.md`.
2. **Italy's basis**, and this is the real decision. (a) Score the `it` fold against the
   **2008-09** tables and declare the five-year gap as a named limitation on that fold only;
   (b) drop the published-marginal scoring for `it` and report it as un-quantified **and say so**,
   the way D-S3-14 handled `strat_hh_type = unknown`; (c) re-open decision 6 and swap Italy's
   microdata to the **2008-09** wave so the basis is exact for all three — 🔴 **listed for
   completeness and flagged against itself: it invalidates the entire corpus, every Step 1–4 gate
   result, and the frozen pre-registration. It is not recommended.** No option is taken here.
3. **Whether `es`/`uk` may be reported as exact-basis while `it` is not.** They can, and the
   asymmetry should be stated rather than averaged away — but it means the LOCO result is not
   basis-uniform across its three folds, and a reviewer will find that if we do not say it.

**One thing this check did not settle.** The tables were confirmed to **exist, be reachable, and
cover our countries**; their *contents* were not compared against anything we hold, and no threshold
in §6 has been re-checked for whether it is achievable against the real published numbers. **That is
still open, it is a smaller question than the one just closed, and it is now unblocked.**

---

### 2026-08-19 (evening) — 🟢 **D-S6-2 RULED (a) BY THE AUTHOR. BOTH RENAMES ACCEPTED; ITALY IS SCORED AGAINST 2008-09 WITH THE GAP DECLARED.**

Ruled while fold `it` (job `1281612`) was still training. 🔴 **Training `it` is not scoring `it`** —
this ruling governs the Step 6 scoring of that fold, and it is now in place **before** the fold is
scored, which is the order a basis question requires.

**Ruling, against the three questions raised in the entry above:**

1. **Both renames ACCEPTED as declared errata.** `tus_00hh` → **`tus_00hhstatus`**;
   `tus_20startime` → **`tus_00startime`**.
2. **Italy's basis: option (a).** The `it` fold is scored against Italy's published **2008-09**
   Eurostat marginals, and the ~5-year gap is declared as a named limitation **on that fold only**.
   Option (c) stays rejected as flagged.
3. **`es` and `uk` are reported exact-basis, `it` is not, and the asymmetry is stated.**

#### What changed in this file, and it was one edit

The EXPERIMENT paragraph's table list now reads `tus_00age`, `tus_00educ`, `tus_00selfstat`,
**`tus_00hhstatus`**, **`tus_00startime`**. The warning block beneath it, which had said the list was
"deliberately left unchanged", has been replaced by the correction and by the limitation the ruling
does **not** remove. 🔴 **Two other passages in this file still print the old names and were left
alone on purpose:** the *"What was NOT verified while drafting this"* paragraph and the D-S6-2
investigation entry itself. Both are **historical records of what was believed at the time**, and
harmonising them would destroy the evidence that the project ever held the wrong names. The rule is
the same one applied to the two self-inconsistent §-spec sentences recorded earlier in this file: a
document is amended forward, not retro-fitted.

#### 🔴 `prereg.md` IS UNTOUCHED AND STAYS UNTOUCHED

md5 **`e4243e07cdd80c9c846b91f40e3e8c45`**, held in `outputs_step6/prereg.md.md5`. Its
§"What this pre-registration does NOT cover" still names `tus_00hh` and `tus_20startime`, and it will
continue to. **These corrections exist only as declared post-hoc errata, here.** Editing the frozen
file would fail `G4.14` on every run in the project at once, including every run that has already
passed it.

#### 🔴 THE LIMITATION, IN THE WORDS IT IS TO BE WRITTEN IN

Eurostat's ESMS gives the fieldwork behind the `2010` column per country: **Spain 2009-2010**
(= our microdata ✅), **UK 2014-2015** (= our microdata ✅), **Italy 2008-2009** — but our Italian
microdata is ISTAT **2013-14**. Italy's contribution to the European 2010 wave is the *Uso del Tempo
2008-2009* edition, confirmed independently; **ISTAT 2013-14 appears in no Eurostat HETUS aggregate
table at all**, the 2020 wave having no `IT`. It is a national wave sitting between two European
rounds. **When Italy is held out, "score against its published aggregate tables" therefore scores
2013-14 diaries against 2008-09 marginals, and every `it` transfer number carries a ~5-year basis
gap.**

🔴 **THE LOCO RESULT IS NOT BASIS-UNIFORM ACROSS ITS FOLDS.** A three-fold mean hides the one thing a
reader needs to know about the third. **Report the folds separately, with `it` carrying the gap in
the same sentence as its number.** This is a limitation of the same class as D-S3-14's UK-only
`strat_hh_type = unknown`: declared, not repaired, and never omitted.

#### What this ruling does not close

The tables were confirmed to **exist, be reachable and cover our countries**. Their **contents** have
still not been compared against anything we hold, and **no §6 threshold has been re-checked for
achievability against the real published numbers.** That question is smaller than the one just
closed, it is unblocked, and it is still owed. Also still owed, and unblocked since the `uk` adapter
exists: **the D-S3-14 UK-fold split report** for `strat_hh_type = unknown`.
