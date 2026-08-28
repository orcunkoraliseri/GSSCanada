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
5. ✅ **DONE 2026-08-25.** Privacy audit complete with its three controls — `outputs_step6/privacy_audit.md`. 🔴 It closes as a **REFUSAL**: `G6.10` 0.6645 against a registered ≤ 0.65 and the perplexity-gap control 0.0570 against ≤ 0.05 both FAIL on the governing run `1286976`. Complete does not mean passed; never write it as 4 of 4.
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

#### 🟢 2026-08-20 — BOTH CROSS-REFERENCES HAVE SINCE BEEN CORRECTED FORWARD. THE "left in place" SENTENCE ABOVE DESCRIBES 2026-08-18 AND NO LONGER HOLDS.

The two bullets above are a record of what was true when they were written, and they are kept. **What
changed after them:** on **2026-08-19** both passages were amended **in their own files, by the route
this project allows** — a forward correction that quotes the wording it replaces, rather than a silent
harmonisation.

| passage | state on 2026-08-18 | state now |
|---|---|---|
| `4thJ_04_finetuneLLM.md` §4.3 | *"Primary, four runs … the other three countries"* | **"Primary, three runs … the other two"**, carrying the note *"🔴 CORRECTED 2026-08-19. This read 'four runs … the other three countries', which was true before author decision 16 EXCLUDED FRANCE on 2026-08-15."* |
| this file's EXPERIMENT section | *"N = 4 … Italy, Spain, UK, France"* | **"🔴 N = 3, NOT 4. CORRECTED 2026-08-19."**, quoting the replaced sentence in full |

🔴 **No evidence was destroyed, and that is the whole test the bullets above were protecting.** Each
correction carries the sentence it replaced inside itself, so the record that the two documents once
disagreed survives in the documents themselves — which is strictly better than the record surviving
only in a third file's progress log. **The rule is unchanged: amend forward, quote what you replace,
never retro-fit.** What is now retired is only the *decision* to leave the two sentences standing;
the reason for that decision was satisfied by a different route.

**One further correction rode along with the §4.3 amendment and is recorded here because it is a
separate claim:** §4.3's closing line *"Quoting either as a general result across the corpus would be
quoting one fold as three"* previously read **"as four"**. The ceiling run and the comparison arm are
still single-fold measurements; only the count they are contrasted against moved.

🔴 **The bullets above must not be deleted.** A future session reading only the corrected files would
otherwise have no way to learn that the two specs were inconsistent for four days, which is the fact
that justifies checking the others.

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

---

### 2026-08-20 — 🔴 **THE §6 THRESHOLDS WERE CHECKED AGAINST THE REAL PUBLISHED NUMBERS. `MAPE > 20 %` IS NOT EVALUABLE AS WRITTEN, AND ITS MECHANICAL FLOOR IS NOT THE SAME IN ALL THREE FOLDS.** New: **FINDING 39**, and **D-S6-3** for the author.

**Why this was done now, and what it closes.** The D-S6-2 ruling of 2026-08-19 (evening) ends with a
declared owed item: *"no §6 threshold has been re-checked for achievability against the real published
numbers … it is unblocked, and it is still owed."* Step 4's `it` fold (job `1284912`) occupies the GPU
and this check needs none, so it was taken in that window — the same reasoning that produced D-S6-2 in
the `uk` window. 🔴 **It found defects again.** The pattern is now twice-confirmed: *the declared
omissions in this project have not been harmless, and each one that has actually been opened has
contained a real defect.* The remaining declared omissions should be read in that light.

**The tables were pulled from Eurostat's dissemination API with the CORRECTED names ruled in D-S6-2** —
`tus_00startime` (145 start-time slots, 9 activity groups, 3 sexes, `time=2010`) for ES, UK and IT, and
`tus_00age` for IT as a contrast case. Everything below is computed from those payloads, not from a
description of them.

#### 🔴 DEFECT 4 — `MAPE` IS UNDEFINED ON CELLS EUROSTAT PUBLISHES AS `0.0`, AND `prereg.md` NAMES NO RULE FOR THEM

`tus_00startime` publishes a participation rate for every one of its 3,480 non-`TOTAL` cells per
country — nothing is missing — but a large number of them are **exactly `0.0`**:

| | ES | UK | IT |
|---|---|---|---|
| non-`TOTAL` cells | 3,480 | 3,480 | 3,480 |
| missing | 0 | 0 | 0 |
| **published exactly `0.0`** | **139 (4.0 %)** | **13 (0.4 %)** | **176 (5.1 %)** |

An absolute percentage error divides by the reference value. On these cells the reference is zero and
**`MAPE` has no value at all** — not a large value, no value. §6 says `MAPE > 20 %` and stops.
🔴 **Every available repair is a basis choice, and they do not agree with each other:** dropping the
zero cells removes between 0.4 % and 5.1 % of the evidence *and removes a different amount per fold*;
flooring the denominator at ε makes the score a function of ε; switching to sMAPE or to a
weighted MAPE changes the quantity being thresholded. **By this project's own rule a basis is
registered before the run that reports under it**, which is exactly the rule D-S6-2 was decided under.

#### 🔴 DEFECT 5 — THE THRESHOLD'S MECHANICAL FLOOR IS COUNTRY-DEPENDENT, AND IT IS WORST ON `it`

Eurostat publishes these rates on a **0.1 percentage-point grid**. A cell printed as `0.2` is some
true value in `[0.15, 0.25)`. **A model that reproduced the underlying population perfectly would
still score a non-zero APE on that cell**, purely from the publication rounding. Taking the true value
as uniform inside the printed cell, the expected irreducible APE is `0.025 / v`:

| | ES | UK | IT |
|---|---|---|---|
| **expected `MAPE` floor from publication rounding alone** | **2.98 %** | **1.87 %** | **3.42 %** |
| cells where rounding alone can exceed 20 % APE | 282 (8.1 %) | 148 (4.3 %) | 360 (10.3 %) |

🔴 **The 20 % threshold therefore does not mean the same thing in the three folds.** A perfect model
starts at `1.87 %` on `uk` and at `3.42 %` on `it` — the floor on `it` is **1.83×** the floor on `uk`,
so `it` is scored with roughly `1.5` percentage points less headroom than `uk` before it has generated
anything. **This is not fatal: the floors are single-digit against a 20 % bar, so the threshold is
achievable in all three folds and does not need to move.** What it is, is a second respect in which
**the LOCO result is not basis-uniform across its folds — and it falls on the same fold as the first
one.** D-S6-2 already ruled that `it` carries a ~5-year wave gap; `it` also carries the loosest
publication grid relative to its own cell values. **Report them together or the reader sees neither.**

#### 🔴 DEFECT 6 — 12.5 % OF `tus_00age` IS SIMPLY ABSENT, SO THE DENOMINATOR OF ANY SCORE OVER IT IS A CHOICE

Unlike `tus_00startime`, the demographic tables are **not** complete. `tus_00age` for Italy declares
`3 units × 3 sexes × 8 age groups × 56 activity categories = 4,032` cells and returns **3,528**:

| unit | present | missing | published as zero | expected floor |
|---|---|---|---|---|
| `TIME_SP` (time spent) | 1,176 / 1,344 | **168 (12.5 %)** | 125 (10.6 %) | 5.79 % |
| `PTP_TIME` (participation time) | 1,176 / 1,344 | **168 (12.5 %)** | 31 (2.6 %) | 0.37 % |
| `PTP_RT` (participation rate) | 1,176 / 1,344 | **168 (12.5 %)** | 16 (1.4 %) | 1.06 % |

**`TIME_SP` is the bad one**: 10.6 % of its cells are `0:00`, and its expected rounding floor is
**5.79 %** because it is published on a **whole-minute** grid where many cells are only a few minutes
long. A `MAPE` computed over `TIME_SP` is close to a quarter unusable before the model is involved.
🔴 **§6 does not say which unit it scores.** `tus_00age` publishes three, they behave completely
differently under `MAPE`, and picking one after seeing the results is precisely the move D-S4-5 exists
to forbid elsewhere in this project.

#### 🔴 DEFECT 7 — `TOTAL` IS ALWAYS EXACTLY `100`, AND IT IS ONE NINTH OF THE TIME-OF-DAY TABLE

`tus_00startime` carries an `acl00 = TOTAL` row for every (sex, slot) pair — **435 cells per country,
11.1 % of the table — and it is `100` in every single one of them, verified for all three countries.**
Any generated population whose activity shares sum to one matches those cells exactly and for free.
🔴 **Including them would cut the reported `MAPE` by about a ninth and would be indistinguishable, in
the printed number, from the model being a ninth better.** They must be excluded, and the exclusion
must be stated rather than assumed — a reader cannot tell from a `MAPE` figure which cells went into
it.

#### 🔴 A TRAP THAT CAUGHT THIS SESSION'S OWN FIRST PASS, RECORDED SO THE SCORING CODE DOES NOT REPEAT IT

In `tus_00age`, **`PTP_RT` is a JSON number and `TIME_SP` / `PTP_TIME` are JSON *strings* in `h:mm`
form** — `"3:24"`, `"0:51"`, `"0:00"`. The first pass of this check parsed all three as floats. It did
not crash and it did not return anything obviously wrong; it returned a **complete, plausible,
entirely false table** in which `TIME_SP` appeared to be 79.9 % zeros and to top out at 24. The error
was only caught by printing the raw payload. 🔴 **Scoring code that reads these tables with a float
cast will silently truncate every duration to whole hours and will still produce a `MAPE`.** This is
a `Step 6` implementation requirement, not a note: the parse must assert the unit and reject a value
whose form does not match it. Recorded under this project's standing rule that a check nobody has
seen fail is not evidence.

#### 🔴 D-S6-3 — FOR THE AUTHOR. `prereg.md` IS FROZEN AND HAS **NOT** BEEN EDITED.

md5 **`e4243e07cdd80c9c846b91f40e3e8c45`** is intact, `outputs_step6/prereg.md.md5` is untouched, and
`G4.14` is unaffected — the `it` fold on the GPU is not disturbed by this entry. **As with D-S6-2,
these corrections exist only as declared post-hoc errata, here, and are never applied by editing the
frozen file.** Four things need a ruling, and **none is taken here**:

1. **Zero-reference cells.** (a) Exclude them and report the excluded count per fold — simple, but
   the excluded fraction differs 12-fold between `uk` and `it`; (b) report **sMAPE** alongside, which
   is defined at zero; (c) keep `MAPE` for non-zero cells and report the zero cells as a separate
   **hit/miss rate** — did the model also put ~0 there? 🔴 **Recommend (c):** it discards nothing, it
   is defined everywhere, and "the model correctly generates *no* night-time employment" is a real
   result rather than a discarded cell.
2. **Which unit `MAPE` is computed on** where a table publishes several. Recommend **`PTP_RT`
   only** — it is the one unit common to all five tables, it is the least rounding-damaged, and it is
   the quantity the occupancy claim is actually about.
3. **`TOTAL` rows excluded**, and the exclusion stated in the paper. Recommend accepting; there is no
   argument for keeping a constant.
4. **Whether the per-fold rounding floors are reported** next to the per-fold `MAPE`. Recommend yes,
   as one line — a reader cannot otherwise tell that `1.87 %` and `3.42 %` of the three numbers were
   never available to the model.

**What this check did NOT do.** It did not compare the tables' *contents* against anything we hold —
no diary, no generated population, no null. It establishes what the metric can and cannot mean; it
says nothing yet about whether we will clear the bar. **The raked-donor null of §5 has still never
been constructed, and it, not `MAPE`, is the pre-registered bar.**

---

### 2026-08-20 (evening) — 🟢 **THE RAKED-DONOR NULL EXISTS. `G6.1`'s PRE-REGISTERED BAR IS NO LONGER "NEVER BUILT" — 23/23 GREEN, EVERY GUARD SEEN FIRING. 🔴 AND BUILDING IT EXPOSED A DEPENDENCY THAT IS IN NEITHER DOCUMENT: THE BAR IS BLOCKED ON STEP 5.1.**

Built locally in the `it` GPU window. **No cluster compute, no model, no corpus file, nothing
submitted.** `prereg.md` not touched — md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified against its
sidecar while this entry was written.

| file | lines | md5 |
|---|---:|---|
| `../tools/4thJ_step6_rakeddonor.py` | 173 | `f1d18ba70c506011eb2440a4eda21019` |
| `../tools/4thJ_step6_rakeddonor_selftest.py` | 133 | `f3fdf5e9ca5175e593ae674917e6ba03` |

**Why this one first, ahead of anything else still open in Step 6.** §5 of the frozen pre-registration
names it in bold as **THE BAR**, and every progress entry since has recorded it as never built. `G6.4`'s
MAPE — the thing `FINDING 39` spent this morning on — is explicitly *not* the claim; §5 is.

#### 🔴 The dependency nobody wrote down

`rake()` needs **the held-out country's published marginals**: `prereg.md` §5 requires *"the same
marginals the model was given, the same geography, the same strata"*. Those are Step 5 work item 5.1's
deliverable, `outputs_step5/marginals_<country>.csv` + `marginals_provenance.md`.

**`outputs_step5/` is empty. Work item 5.1 has never been started.**

So **`G6.1`'s pre-registered bar cannot be computed until Step 5.1 exists**, and neither
`4thJ_05_populationLinkage.md` nor this document says so — Step 5's own "what this step blocks" line
names only Step 7. **This is not a code gap and no amount of Step 6 work closes it.** It also raises
the priority of 5.1 well above "populate the people for Step 7": it is on the critical path of the
headline gate.

#### 🟢 The prereg perturbation is now DEMONSTRATED, before any fold is scored

The Step 6 validation table's first perturbation reads:

> Score the **raked-donor null against itself** as if it were the model → **`G6.1` must report exactly
> zero margin** — and a `<= 0` comparison would pass it. 🔴 The comparison must be strict `>`.

That is now a passing test rather than a plan. The self-test scores the null against itself, asserts
the margin is **exactly `0.0`**, asserts `G6.1` returns **FAIL**, and then asserts that the `>=`
reading **would have returned PASS** — so `V6.c` is shown to be load-bearing rather than merely
stated. 🔴 **A perturbation demonstrated before the runs is worth more than the same perturbation
demonstrated after them**, and this one cost no GPU at all.

#### The three ways this null could have been built favourably, each refused in code

`prereg.md` §5 says *"Construction, so it cannot be built favourably"* and then gives one sentence of
construction. These are the three ways that sentence can be violated, each now a hard failure:

1. 🔴 **Raking onto different marginals from the model's** — *"not a null, it is a handicap"*.
   `rake()` requires a non-empty `marginals_source` provenance label and `score_margin()` **refuses to
   compare** two values whose labels differ. A blank label is refused too: a provenance field nobody
   fills is not provenance (`V5.b`'s reasoning).
2. 🔴 **Leaving the held-out country in the donor pool.** `rake()` FAILS if any donor carries it. A
   self-donor would make the null unbeatable *for the right reason* and the claim unfalsifiable — and
   nothing in the resulting number would look wrong.
3. 🔴 **A non-strict comparison.** `V6.c`, above.

**Two more guards that exist because the failure would otherwise be silent:**

* **A target category no donor can supply is a hard FAIL, never a silent drop.** IPF cannot create a
  category from nothing; dropping it would quietly rake onto *different* marginals than the model
  received — violation 1 arriving through the back door. This is the real one to watch when the
  marginals finally land, because the UK's `strat_hh_type = unknown` (D-S3-14) is exactly the kind of
  category a published census table will not have.
* **Non-convergence is reported as a failure, never as a result.** Demonstrated on a structurally
  infeasible pool where sex and day type are perfectly correlated: IPF oscillates, the worst margin
  stays **22 pp** against a 0.5 pp tolerance, and `rake()` raises instead of returning the last
  iterate. 🔴 A raking routine that returns its final iterate regardless is the single easiest way to
  ship a null that was never actually raked.

The tolerance is **±0.5 pp, reused from `G5.1` deliberately** — a raked margin is a fitted margin and
is held to the same bar the synthetic population is held to, rather than to a looser one chosen here.

#### What this does NOT close

* **The null has never been run on real data**, because it cannot be (see the dependency above).
  Twenty-three unit tests on synthetic pools are not a null.
* **`score_margin()` does not choose the metric.** It applies `V6.c` to two values someone else
  computed. Which quantity `G6.1` compares is still `G6.1`'s business and is unresolved — and
  `FINDING 39`/`D-S6-3` are open on exactly that question for `G6.4`.
* **`V6.b` is not satisfied by this module.** Asserting that the scorer and the gate read the *same
  table* needs both of them to exist; only one does.
* The other two nulls — pooled all-country average (`G6.3`) and nearest-neighbour country (`G6.2`) —
  are **not** built. They are secondary by `RL08`/author decision, but they are still owed.

---

### 2026-08-20 (evening) — 🟢 **`D-S6-3` ITEM 1 RULED (c): `MAPE` ON NON-ZERO CELLS, AND THE ZERO CELLS BECOME THEIR OWN HIT/MISS RESULT. 🔴 THAT CREATES A NEW TOLERANCE WHICH MUST BE FIXED NOW, BEFORE ANY NUMBER IS SEEN.**

**Ruled by the author 2026-08-20.** The zero-reference cells — `4.0 % (ES) / 0.4 % (UK) / 5.1 % (IT)`
of time-of-day cells, where Eurostat publishes a literal `0.0` and `MAPE` has no value — are **not
excluded and not patched**. They are scored separately:

* **`MAPE` is computed over cells with a non-zero published reference.** Unchanged threshold, unchanged
  arm, and no ε-floor or sMAPE substitution — every one of those is a basis choice and they disagree.
* **The zero cells become a hit/miss rate:** did the model also put approximately zero there? 🟢 *"The
  model correctly generates no night-time employment"* **is a result**, and (a) would have thrown it in
  the bin while reporting a `12-fold` difference in what each fold binned.

#### 🔴 The ruling's cost, and it must be paid before results exist

**"Approximately zero" is a tolerance, and it does not exist yet.** Setting it after the model's
night-time employment rates are visible would be exactly the defect this project refuses everywhere
else — a threshold chosen while looking at the number it judges. **It must be pre-registered now.**

**Proposed, for the author to confirm or replace, and either way to fix before any run:**

| | proposal | why this and not something else |
|---|---|---|
| **hit definition** | a zero cell is a **HIT** when the model's rate for it is `< 0.5 %` of the population in that cell's stratum-hour | It is the publication rounding grain, not an invented number: Eurostat's own floor is already `1.87 % (UK)` to `3.42 % (IT)` on `PTP_RT`, so `0.5 %` is comfortably inside what the source could not have resolved anyway. |
| **reporting** | **per fold, as a fraction — `hits / zero-cells` — with the denominator printed** | The denominators are `4.0 / 0.4 / 5.1 %`, a `12-fold` spread. A bare percentage across folds would be dominated by `it` and `es` and would say almost nothing about `uk`. 🔴 **Never average the three.** |
| **gate or not** | **REPORTED, NOT THRESHOLDED**, on its first appearance | No prior exists for what this rate should be. Thresholding it now would be inventing a bar; reporting it makes the bar available to whoever comes next, which is what `G4.10` already does in Step 4. |

#### What is still open in `D-S6-3` — items 2, 3 and 4

Only item 1 was put to the author and only item 1 is ruled. **Still open:**

2. **Which unit `MAPE` is computed on** where a table publishes several. Recommendation stands:
   **`PTP_RT` only** — the one unit common to all five tables, the least rounding-damaged, and the
   quantity the occupancy claim is actually about. 🔴 **Note the trap attached to it:** two of the three
   units are `h:mm` **strings**, and a float cast truncates to whole hours **while still printing a
   number**. It caught this session's own first pass.
3. **`TOTAL` rows excluded** and the exclusion stated. Recommendation stands: accept — `TOTAL` is a
   constant `100` across `11.1 %` of the startime table and would flatter any `MAPE` that included it.
4. **Per-fold rounding floors reported** next to the per-fold `MAPE`. Recommendation stands: yes, one
   line — otherwise no reader can tell that `1.87 %` and `3.42 %` of those numbers were never available
   to the model in the first place.

**`prereg.md` IS FROZEN AND WAS NOT EDITED.** md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified against
`outputs_step6/prereg.md.md5` while this entry was written. As with `D-S6-2`, this ruling exists **only
as a declared post-hoc erratum, here** — the frozen file is never touched and `G4.14` is unaffected.

🔴 **And the standing caveat, unchanged by any of this:** `MAPE` is **not** the pre-registered bar. The
raked-donor null of §5 is, its implementation is green at `23/23`, and it is **blocked on Step 5.1**.

---

### 2026-08-20 (execution pass) — 🟢 **`D-S6-3` ITEMS 2, 3 AND 4 RULED (a) AND APPLIED. THE FIVE SCORING TABLES ARE NOW ON DISK AND WERE MEASURED, NOT QUOTED — WHICH CONFIRMED `FINDING 39` AND PRODUCED `FINDING 54` AND `FINDING 55`.**

All five tables were fetched verbatim for all three countries (15 files, HTTP 200, in
`outputs_step6/eurostat_raw/`) and every number below is re-derived from them.

#### 🟢 Item 6 = `D-S6-3` item 2 — `MAPE` is computed on `PTP_RT` only

**Applied.** Confirmed at the source, and it is not a preference:

* `TIME_SP` and `PTP_TIME` are **JSON strings** — the first cell of `tus_00age_ES` reads
  `'24:00'`, not `24.0`. 🔴 A float cast does not raise; it truncates to whole hours **and still
  prints a number.**
* `tus_00startime` — **the time-of-day table, the one the occupancy claim is actually about —
  publishes `PTP_RT` and nothing else.** For the table that matters most the ruling is not a
  choice, it is the only unit there is.
* `PTP_RT` is the one unit common to all five tables.

#### 🟢 Item 7 = `D-S6-3` item 3 — `TOTAL` rows are excluded, and the exclusion is stated

**Applied, and the premise re-derived:** in `tus_00startime`, `435` of `3,915` cells are `TOTAL`
rows carrying exactly `100.0` — **`11.11 %`**, which is the logged figure to the digit. Any `MAPE`
including them is diluted by an eleventh of guaranteed-zero error. The exclusion is a **declared
methods sentence**, not a silent filter.

#### 🟢 Item 8 = `D-S6-3` item 4 — the per-fold rounding floor is printed beside each fold's `MAPE`

**Applied, and the floors are now derived rather than quoted.** The published grain is `0.1 pp`
(the smallest non-zero `PTP_RT` in every table and every country is exactly `0.10`), so a cell
carries an expected rounding error of `0.025 pp`, and `mean(0.025 / value)` over the non-zero
scorable cells is the `MAPE` **a perfect model cannot beat**:

| table | ES | UK | IT |
|---|---|---|---|
| `tus_00startime` | **3.01 %** | **1.87 %** | **3.38 %** |
| `tus_00selfstat` | 1.13 % | 0.47 % | 0.96 % |
| `tus_00age` | 1.01 % | 0.57 % | 0.89 % |

🟢 **`FINDING 39`'s floors are CONFIRMED and their basis is now written down instead of inferred:**
expected, not worst-case, rounding error on the time-of-day table. **`uk` reproduces exactly at
`1.87 %`**; `es` reads `3.01` against the logged `2.98` and `it` `3.38` against `3.42`, a gap of
`0.04 pp` that is the cell filter (this pass scores `sex = T` only), not a disagreement.
🔴 **`it`'s floor is `1.8x` the UK's**, so an identical model scores worse on the `it` fold for a
reason that is entirely the publisher's rounding.

🟢 **`FINDING 39`'s zero-cell shares are CONFIRMED too, and their filter identified:** `ES 4.02 %`,
`UK 0.38 %`, `IT 5.09 %` of time-of-day cells — the logged `4.0 / 0.4 / 5.1 %` — measured over
**all sexes with `TOTAL` rows removed**. (Restricted to `sex = T` they are `3.73 / 0.09 / 4.77 %`;
the filter has to be stated or the numbers do not reproduce.)

#### 🔴 `FINDING 54` — **not one of the five tables has a day-type dimension.**

`tus_00age`, `tus_00educ`, `tus_00selfstat`, `tus_00hhstatus` and `tus_00startime` all carry
exactly `['freq', 'unit', 'sex', <one stratifier>, 'acl00', 'geo', 'time']`. **There is no
weekday/weekend split to select.** Every published figure is an average day on whatever basis the
national institute used, and we cannot ask for a different one.

🔴 **This lands directly on `FINDING 53` and it is now a decision that must be made before scoring.**
Item 1 put all three folds on a calendar week (`weight_dia_cal`); the published tables are on an
undeclared national basis. Scoring calendar-weighted output against a table built on Spain's
`50/25/25` would re-introduce, in the comparison, exactly the bias item 1 removed from the corpus.
**Which weight Step 6 scores on is therefore a new open decision, `D-S6-4`** — it is not settled by
item 1 and it is not settled by item 6.

* **Recommended: score on `weight_dia_cal` and report the `weight_dia` figure beside it as a
  declared sensitivity, never mixed.** The HETUS convention for an "average day" is a
  calendar-representative day, all three folds are then mutually comparable, and the gap is
  bounded and already measured (`es +0.947`, `it +1.300`, `uk −0.003 pp` on at-home time).
* 🔴 **What would settle it properly and has not been done:** confirm from the HETUS guidelines
  what basis the national institutes were required to tabulate on. That is a literature question,
  and literature questions leave this project as a prompt.

#### 🔴 `FINDING 55` — the scoring tables do not carry our strata, and one of the five cannot be used at all

Measured, per table:

| table | usable against our prefix? | why |
|---|---|---|
| `tus_00startime` | 🟢 **yes** | `sex` x `time of day` x 9 broad activity groups; `PTP_RT` only |
| `tus_00selfstat` | 🟢 **yes** | `wstatus` = `EMP_FT`/`EMP_PT`/`LEAV`/`UNE`/`EDUC`/`HOME`/`RET`/`OTH` collapses **1:1** onto our six `strat_econ_status` bands once the three employed classes are merged |
| `tus_00age` | 🟡 **partly** | see below |
| `tus_00hhstatus` | 🟡 **partly** | 12 published categories (`CPL_CH6`, `CPL45-64_NCH`, `P25_NCH`, …) against our five; needs a declared regrouping and will not be exact |
| `tus_00educ` | 🔴 **NO** | it is stratified by `isced97` **educational attainment**, and the corpus carries no education column at all. It cannot be scored against our strata under any mapping |

🔴 **`tus_00age` has two separate defects.**

1. **`Y65-74` is entirely absent — `0` of `168` cells present, in ES, UK and IT alike.** That is
   the `12.5 %` absence logged in `FINDING 39`, now localised: it is not scattered missingness, it
   is **one whole age band, and it is one of ours** (`65-74`), missing in every fold.
   🔴 **CORRECTED by `FINDING 73` (2026-08-21 night): this is true of the `2010` column only,
   and the cause is not missingness.** Split by the `time` dimension, `Y65-74` is populated in `504`
   of `504` cells in the **2000** wave and `0` in **2010**, identically in all three countries —
   Eurostat replaced it with `Y_GE65`, which is itself absent in 2000. The band we cannot use is
   still unusable, but the sentence "Eurostat does not publish 65–74" is FALSE and must not be
   written. See the `D-S6-5` residue below for the full table.
2. **The age dimension is not a partition.** Published: `TOTAL, Y15-20, Y20-24, Y20-74, Y25-44,
   Y45-64, Y65-74, Y_GE65`. `Y20-74` contains `Y25-44` and `Y45-64`; `Y_GE65` contains `Y65-74`.
   A `MAPE` computed over all of them double-counts the same people. **And nothing below 15 is
   published at all, so our `11-14` band has no counterpart in any fold** — which is the same
   `11-14` that `FINDING 48` showed is a country fingerprint.

**Consequence, recorded not decided:** the scoring set is realistically `tus_00startime` +
`tus_00selfstat`, with `tus_00age` on a declared non-overlapping subset and `tus_00hhstatus` on a
declared regrouping. **`D-S6-5`: confirm dropping `tus_00educ` from the scoring set and declaring
it, rather than inventing an education proxy.** Recommended: drop and declare.

#### ⚪ Still owed from `D-S6-3` item 1

The **"approximately zero" tolerance** proposed at `< 0.5 %` was written into the ruling's cost
section and has **not been confirmed**. It must be fixed before any zero-cell hit rate is computed.
🟢 The proposal survives contact with the data: the publication grain is `0.1 pp`, so `0.5 %` is
five grains — comfortably below what the source could resolve, and not a number chosen by looking
at a model output.

#### ⚪ Provenance

`outputs_step6/eurostat_raw/<table>_<GEO>.json`, 15 files, fetched
`2026-08-20` from `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<table>?format=JSON&lang=EN&geo=<GEO>`,
all HTTP 200. 🔴 **The `2010` column is the wave, not the year: for `it` it is the 2008-09 survey
while our microdata is ISTAT 2013-14 — `D-S6-2`'s declared asymmetry, unchanged by anything here.**
`prereg.md` **not touched**; md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar
while this entry was written.

---

### 2026-08-21 — 🟢 **`D-S6-4`, `D-S6-5` AND THE OUTSTANDING `D-S6-3` ITEM 1 TOLERANCE ARE ALL RULED BY THE AUTHOR.** 🔴 **THE ZERO-CELL TOLERANCE IS `< 1.0 %`, NOT THE `< 0.5 %` THAT WAS RECOMMENDED.**

Three decisions closed. No file was rebuilt and no gate was run; `prereg.md` **not touched**, md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar at both ends of the session.

#### 🟢 `D-S6-4` — RULED as recommended: score on `weight_dia_cal`

Step 6 scores on **`weight_dia_cal`**, the calendar-week weight that item 1 put all three folds on.
The `weight_dia` figure is **reported beside it as a declared sensitivity and never mixed into the
headline**.

This keeps the comparison on one basis across the three folds and prevents `FINDING 53`'s
country-correlated day-mix (`uk` 71.45/14.32/14.24, `es` 50/25/25, `it` 33/33/33) from re-entering
through the scoring tables after item 1 removed it from the corpus. The gap it leaves is bounded and
already measured: at-home time `es +0.947`, `it +1.300`, `uk −0.003` pp.

🔴 **Unchanged and still owed:** confirming from the HETUS guidelines what basis the national
institutes were *required* to tabulate on. That is a literature question and leaves this project as a
prompt, not as a search.

#### 🟢 `D-S6-5` — RULED as recommended: drop `tus_00educ` and declare it

`tus_00educ` is stratified by `isced97` **educational attainment** and the corpus carries no
education column at all, so no mapping exists. It is **dropped from the scoring set and declared**,
rather than back-filled with an invented education proxy.

The scoring set is therefore `tus_00startime` + `tus_00selfstat` as the two clean tables, with
`tus_00age` on a declared non-overlapping subset (🔴 **now specified below** — and `FINDING 73` corrects the reason: `Y65-74` is not absent from the source, it is the 2000 wave's top band and does not exist in the 2010 wave we score against) and `tus_00hhstatus` on a declared regrouping.

#### 🟢 `D-S6-5` RESIDUE — RULED (a) 2026-08-21 night: the `tus_00age` subset, written down BEFORE any fold is scored

The ruling above drops `tus_00educ` and leaves `tus_00age` "on a declared non-overlapping subset".
That subset had never been written down. The author ruled **(a) — fix it in writing now**, on the
ground that a subset chosen while looking at a transfer result is selection on the outcome.

**The ruled subset, on the Eurostat side:** the five published bands
`Y15-20`, `Y20-24`, `Y25-44`, `Y45-64`, `Y_GE65`, with `TOTAL` excluded as a redundant aggregate and
`Y20-74` excluded as a composite that overlaps `Y25-44`, `Y45-64` and part of `Y_GE65`.

Two things were then **checked against the downloaded tables rather than assumed**, and both change
what may be written.

##### 🔴 `FINDING 73` (i) — `Y65-74` is NOT absent. It is the 2000 wave's top band, and the age dimension is WAVE-DEPENDENT

`FINDING 55`'s second half said `Y65-74` was absent in `0 of 168` cells across ES, UK and IT. Counting
the populated cells in `tus_00age_{ES,UK,IT}.json` **split by the `time` dimension** gives a different
and much more specific picture — identical in all three countries:

| band | cells in the **2000** wave | cells in the **2010** wave |
|---|---|---|
| `TOTAL` | 504 | 504 |
| `Y15-20` | **0** | 504 |
| `Y20-24` | 504 | 504 |
| `Y20-74` | **0** | 504 |
| `Y25-44` | 504 | 504 |
| `Y45-64` | 504 | 504 |
| `Y65-74` | 504 | **0** |
| `Y_GE65` | **0** | 504 |

So Eurostat **did not stop publishing 65–74**; it changed the classification between waves. `Y65-74`
is the 2000 wave's top band and `Y_GE65` replaced it in 2010, exactly as `Y15-20` and `Y20-74` appear
only in 2010. ⚪ The ruled subset is therefore precisely *the 2010 wave's own band set, minus `TOTAL`
and minus the composite* — which is the right subset for us, because `D-S6-2` scores every fold
against the **2010** column. But the reason must be written as "the band does not exist in the wave we
score against", never as "Eurostat does not publish it": the second is false and is checkable in one
line by any reviewer.

##### 🔴 `FINDING 73` (ii) — two of the five ruled bands cannot be scored against OUR corpus at all

The finest age resolution anything in this project ever sees is the **eight-band prefix scheme**
(`11-14`, `15-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75+`). It is what the corpus carries,
what the Step 5 population prefixes carry, and therefore the only age information a **generated** diary
can ever be resolved to. Mapping it onto the ruled Eurostat subset:

| Eurostat band | our bands | mapping |
|---|---|---|
| `Y25-44` | `25-34` + `35-44` | 🟢 **exact** |
| `Y45-64` | `45-54` + `55-64` | 🟢 **exact** |
| `Y_GE65` | `65-74` + `75+` | 🟢 **exact** |
| `Y15-20` | — | 🔴 **not separable**: our finest class in this range is `15-24` |
| `Y20-24` | — | 🔴 **not separable**: same |
| (none) | `11-14` | 🔴 **no counterpart**: Eurostat's table starts at 15 |

🔴 **The split cannot be repaired from either side.** We cannot split our `15-24` because the band is
what the model is conditioned on; and we cannot merge Eurostat's `Y15-20` and `Y20-24` into a single
15–24 figure either, because the published units are participation **rates** and mean **times**, not
counts, and the table carries no band population with which to weight the two into a union.

**Consequence, stated with the size:** `tus_00age` is scorable on **three** bands, not five, and those
three cover **84.7 %** of the corpus (`62,076` of `73,254` diaries). The two unscorable slices are
`15-24` at **10.8 %** (`7,927`) and `11-14` at **4.4 %** (`3,251`); the second was never in scope, since
the Eurostat table begins at 15. ⚪ This is a **coverage limitation of the reference table**, not a
result — it is fixed before any fold is scored and must be reported as such, with the percentages,
in the same breath as any `tus_00age` number.

##### ⚪ One boundary that the published metadata cannot settle

Eurostat labels the two bands *"From 15 to 20 years"* and *"From 20 to 24 years"*, which read as
overlapping at age 20. Under the standard HETUS five-year classes they are 15–19 and 20–24 and
partition 15–24 cleanly, and that is the reading adopted here. It is recorded rather than resolved
because the metadata does not settle it — and it is **harmless for us**, since neither band is
scorable on our side anyway. It would become load-bearing only if a future age scheme split `15-24`.

##### The specification, as it must be applied

> `tus_00age` is scored on `Y25-44`, `Y45-64` and `Y_GE65`, against the **2010** column, mapping our
> eight prefix bands two-to-one onto each. `TOTAL` (redundant aggregate) and `Y20-74` (composite) are
> excluded as non-partition members. `Y65-74` is excluded because it does not exist in the 2010 wave.
> `Y15-20` and `Y20-24` are excluded because our corpus cannot separate them and the published table
> cannot merge them. The excluded population — `15-24` (10.8 %) and `11-14` (4.4 %) — is declared with
> every `tus_00age` result.

⚪ Nothing here touches `prereg.md`, whose md5 is unchanged; `tus_00age` is a scoring-table detail that
the prereg does not name at band level.

#### 🔴 `D-S6-3` item 1 — the "approximately zero" tolerance is `< 1.0 %`

**The author chose the LOOSER of the two options.** The recommendation was `< 0.5 %`; the ruling is
**`< 1.0 %`**, and `< 1.0 %` is what must be written everywhere the zero-cell hit/miss rule appears.

⚪ Recorded so the number is not silently reverted to the recommendation later: the publication grain
is `0.1 pp`, so `1.0 %` is **ten** grains rather than five. It is further below what the source can
resolve, which makes the "approximately zero" test easier to pass and therefore **more conservative
about claiming a miss** — a zero-cell has to be more clearly non-zero before it counts against us.
The direction of the looseness is toward the model, so it must be stated in the paper as the
pre-registered value and not defended as if it were the tight one.

🔴 This tolerance is now **fixed** and any zero-cell hit rate computed against a different value is
invalid.

#### What this does NOT close

* `FINDING 39`'s other defects stand: `TOTAL` is a constant 100 in 11.1 % of cells, and two of three
  units are `h:mm` **strings** that a float cast silently truncates.
* `D-S6-2`'s wave asymmetry is unchanged — the Eurostat `2010` column is the 2008-09 survey for `it`
  while our microdata is ISTAT 2013-14.
* `G6.1`'s raked-donor null is computable on all three folds as of 2026-08-21, but has **not been
  run**, because the donors are the Step 3 corpus and it lives on Speed.


---

### 2026-08-21 (late afternoon) --- 🔴 **`G6.1` WAS RUN FOR THE FIRST TIME. IT CANNOT CONVERGE ON THE `uk` FOLD, AND WHERE IT DOES CONVERGE IT RESTS ON FAR FEWER DIARIES THAN THE POOL SIZE SUGGESTS. `FINDING 62`.**

Step 5.1 unblocked `G6.1` in principle on 2026-08-20 and Step 5.2 was built today, so the null was
run: the REAL donors from `Step3_docs/outputs_step3/4J_step3_corpus.jsonl`, raked onto the REAL
published marginals in `outputs_step5/`, through the REAL `tools/4thJ_step6_rakeddonor.rake()`. No
substitute for any of the three. Full numbers in
`../Step5_docs/outputs_step5/marginals_provenance.md` section 25.

#### 🔴 First attempt: all three folds REFUSED, and both guards were right

```
es, it   551 donors carry strat_hh_type 'unknown' that the target never names.
uk       IPF did not converge: worst margin off by 1.41515 pp, tolerance 0.5 pp.
```

The first is `FINDING 52`'s orphan guard firing exactly as designed on `D-S3-14`'s UK-only household
band. The second is something else entirely.

#### Second attempt, with `collapse={strat_hh_type: {unknown: other_complex}}`

| fold | verdict | iterations | `max_dev_pp` |
|---|---|---:|---:|
| `es` | converged | 7 | 0.4506 |
| `uk` | 🔴 **CANNOT CONVERGE** | 200 | **1.41515** |
| `it` | converged | 3 | 0.4121 |

🔴 **`G6.1` is the pre-registered BAR for the entire claim, and it cannot be computed for
one of the three folds.** The 1.41515 pp is exactly the age-15 `unknown` slice of `FINDING 61`: the
`D-S5-3` convention puts those people in an economic band that **no donor diary carries**, so no
reweighting of any donor pool can produce them. **This is not a tolerance to be loosened. It is a
missing category**, and it is `D-S5-11`'s to resolve.

#### 🔴 And the two folds that DO converge are thinner than the pool size suggests

Effective sample size, `(sum w)^2 / sum w^2`, which no gate currently looks at:

| fold | ESS | as % of pool | largest single donor weight | the `unknown` band is carried by |
|---|---:|---:|---:|---|
| `es` | 36,977 | 68.3 % | 0.0206 % | 1,712 donors |
| `it` | **16,101** | **46.0 %** | **0.1136 %** | 🔴 **68 donors** |

The Italian fold's null hits its economic margin by making **68 British diaries** stand for **4.207 %
of an entire country**, roughly 62 synthetic persons per donor diary, with a largest-donor weight
**5.5x** the Spanish fold's. It converges and it is arithmetically correct. A bar resting on 68
diaries is not much of a bar, and `G6.1` for `it` may not be quoted without this alongside it.

#### 🔴 Two collapses are now known to be REQUIRED, and neither is pre-registered

* `strat_hh_type: unknown -> ?` --- without it the rake refuses on two folds. The `other_complex`
  target used above was chosen to expose the next failure, **not decided**.
* `strat_econ_status: homemaker -> other_inactive` for `es` --- already required by `FINDING 52` and
  `FINDING 51`.

`prereg.md` is frozen and cannot be edited, so both collapses have to be declared in the paper as
what they are: post-registration operational choices, stated with their effect.

#### 🟢 What was closed on the writing side

`D-S6-4` still owed one item: confirmation from the HETUS guidelines of what weight basis the national
institutes were REQUIRED to tabulate on. That is a literature question, so the deliverable is a
prompt, and it is now written:
`DeepResearchPrompts/L27_hetus_weights_amy_weather_tabula_licence.md`, **Part A**. It carries the
measured day-base table (`uk` 71.45/14.32/14.24, `es` 50/25/25, `it` 33/33/33) as the thing the
guidelines have to explain, and it asks whether the 2008 and 2018 editions differ, because that alone
would account for it.

#### What did NOT happen

No `G6.*` gate was scored, no fold was compared, and `prereg.md` was not touched --- md5
`e4243e07cdd80c9c846b91f40e3e8c45`, verified against its sidecar at both ends of the session. The
numbers above are measurements of whether the null is COMPUTABLE, not a null result.


---

### 2026-08-21 (evening) --- 🟢 **`G6.1`'s RAKED-DONOR NULL NOW BUILDS ON ALL THREE FOLDS. `FINDING 62` IS RETIRED.**

Runner: `tools/4thJ_step6_g61_rake_folds.py`, new. It does NOT score anything --- there is no model
output yet --- it answers the question that comes first: **can the null be constructed for this fold?**

`FINDING 62` had said no for `uk` (1.41515 pp against a 0.5 pp tolerance, the age-15 `unknown` slice no
donor carries) and had said yes-but-thin for `it` (68 British diaries carrying 4.207 % of the country,
effective sample size 46.0 %). `D-S5-11` (b), ruled and applied the same evening, removes both.

| fold | iterations | worst margin | effective sample size | heaviest single diary |
|---|---:|---:|---|---:|
| `es` | 3 | 0.24602 pp | 26,769 of 54,114 (49.5 %) | 0.0164 % of the target |
| `uk` | 5 | 0.41662 pp | 34,107 of 57,400 (59.4 %) | 0.0118 % |
| `it` | 4 | 0.24487 pp | 26,881 of 34,994 (**76.8 %**) | 0.0098 % |

🔴 **The null is raked onto the FITTED population, not onto `marginals_<c>.csv`.** That is
`score_margin`'s Guard 1 applied honestly: the model is prompted with prefixes drawn from
`population_<c>.csv`, so a null raked onto anything else would be answering a different population and
the difference would be reported as transfer.

🔴 **Two collapses are required for the null to exist and NEITHER IS PRE-REGISTERED.**
`strat_hh_type: unknown -> other_complex` (the 551 UK diaries of `D-S3-14`; `es` and `it` folds) and
`strat_econ_status: homemaker -> other_inactive` (`es` only, `FINDING 51`). `prereg.md` is frozen and
mentions neither. Both are stamped into `marginals_source`, so a collapsed run can never compare equal
to an uncollapsed one --- but they are owed to the author.

Seen failing, on demand rather than from memory: with the collapses dropped, `es` and `it` REFUSE on
the orphan guard; and rebuilding `uk` under the superseded `D-S5-3` minor convention refuses at
**1.414 pp**, reproducing `FINDING 62` to four figures.

⚪ Still true: `G6.1` cannot be SCORED until a fold has generated. What changed is that the bar now
exists on every fold.


---

### 2026-08-22 — 🟢 **WORK ITEM 6.2: THE POOLED ALL-COUNTRY NULL (`G6.3`) IS BUILT ON ALL THREE FOLDS.** 🔴 **`G6.2` REFUSES TO BE BUILT AND `D-S6-6` IS WHY. NEW `FINDING 77`.**

`tools/4thJ_step6_secondary_nulls.py` + `_selftest.py` (**30 of 30 green, every guard seen firing**),
report at `outputs_step6/secondary_nulls.json` md5 `bc9f53bb04e0a911649fdb6c552399ca`. Full record:
`Step6_docs/impl/2026-08-22_secondary-nulls.md`. No cluster job; nothing is scored.

`G6.1` fixed the shape of a null here — **a weighting over the real N−1 donor diaries**. The raked
null solves for weights that reproduce the held-out country's strata; these two solve for nothing,
which is what makes them weaker on purpose. 🔴 **Neither is raked, and that is a rule, not an
omission:** a raked pooled null is the raked-donor null under another name, and `prereg.md` permits
raking in exactly one place. Weight basis `weight_dia_cal` (`D-S6-4`); `FINDING 53` is why that
matters here more than anywhere — an unweighted pooled null would be a null about weekends, and
unequally so per fold.

#### `G6.3` builds, and for the first time we know HOW WEAK it is

| fold | donors | ESS | ESS % | worst strata gap vs the target population |
|---|---:|---:|---:|---:|
| `es` | 54,112 of 54,114 | 14,868 | 27.5 % | 🔴 **14.7629 pp** |
| `uk` | 57,400 of 57,400 | 25,436 | 44.3 % | 🔴 **10.1901 pp** |
| `it` | 34,992 of 34,994 | 11,110 | 31.7 % | 🔴 **9.6242 pp** |

🔴 **`G6.1` is ≤ 0.5000 pp on every variable BY CONSTRUCTION, so the pooled null sits 19x to 30x
further from the population it is a null for.** Beating `G6.3` is a much smaller claim than beating
`G6.1`, and the two must never share a sentence in the paper without this number.

#### 🔴 `FINDING 77` — the `es` fold's widest gap is a category the target population does not contain

`strat_econ_status = homemaker` is **14.76 %** of the `es` donor pool and **0.00 %** of
`population_es.csv`. `FINDING 51`: the Spanish census `RELA` has no *Labores del hogar*, so
`D-S5-4`(b) fitted Spain on **five** economic bands. The raked null met this as an orphan and it is
why registered collapse **B** exists. 🔴 **The pooled null is not raked, so nothing refuses — the
mismatch is simply carried, and must be DECLARED rather than repaired.** Collapsing it here would
make `G6.3` a partly-raked null, which is the one thing it may not be. ⚪ On all three folds the
widest gap is an economic-status column, not age or sex.

#### ⚪ A counterintuitive measurement, recorded so it is not misread later

Effective sample size, pooled vs raked, on the same pools: `es` 27.5 % vs 49.5 %, `uk` 44.3 % vs
59.4 %, `it` 31.7 % vs **76.8 %**. **Raking INCREASED effective sample size on every fold** — the raw
survey weights are more dispersed than the factors that reproduce a target from them, so the stronger
null also rests on more diaries. `FINDING 62` pointed the other way; neither number may be quoted as
though low ESS made a null weak on its own.

#### 🔴 `D-S6-6` — OPEN, FOR THE AUTHOR: which country is the "nearest neighbour"?

`prereg.md` §5 names a **"nearest-neighbouring-country model"** and **registers no rule for choosing
the neighbour.** It did not need one: the design then had **four** countries including **France**,
which borders both Spain and Italy. **Author decision 16 (2026-08-15) excluded France.** The pool per
fold is now two countries, and for the `uk` fold neither Spain nor Italy is anybody's idea of a
nearest neighbour.

🔴 **Choosing one now — after the corpus, the folds and the populations are all built — is choosing
a null's strength after the fact**, the same defect `G6.2` exists to answer. So the registry ships
**empty**, `G6.2` **refuses on all three folds**, and the refusal names this decision. Seen refusing
in the selftest and in the live run.

**The ruling must supply a RULE, not three country codes.** Candidate bases, none chosen here: shared
land border (fails for `uk` outright); great-circle distance between population centroids; a
published regional grouping; or **drop `G6.2` and declare it undeliverable under a three-country
design** — defensible, because the objection it answers is weaker when no fold *has* a neighbour.
⚪ Whatever is ruled goes in a dated sidecar, `outputs_step6/prereg_addendum_02.md`;
`prereg.md` is frozen and cannot carry it.

#### Where this leaves Step 6

**DoD item 2 is two nulls of three**: raked-donor (`G6.1`) and pooled (`G6.3`) built, neighbour
(`G6.2`) blocked on `D-S6-6`. 🔴 **Everything else in Step 6 — items 6.3 (run the folds), 6.4
(score) and 6.5 (privacy audit) — waits on GENERATED DIARIES, which is Step 7's deliverable.** That,
not Step 6, is the critical path.

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified at both ends. Nothing is
running on Speed.


---

### 2026-08-22 (evening) — 🟢 **`D-S6-6` RULED (a) AND APPLIED: `G6.2` IS BUILT, SIX NULLS, TWO PER FOLD. WORK ITEM 6.2 IS COMPLETE.** 🔴 **AND THE REBUILD EXPOSED `FINDING 78` — NEW `D-S6-7`.**

The author ruled **(a)**: build the single-donor-country null for **every** country in the fold's
pool, report them all, **drop the word "nearest"**. Registered in
`outputs_step6/prereg_addendum_02.md` (md5 `db450b89abbaf8f5480eb2479d50ae2d`, sidecar written,
`md5sum -c` OK). ⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` **unchanged**. Full record:
`Step6_docs/impl/2026-08-22_secondary-nulls.md`. No cluster job; nothing scored.

Why (a) and not a geographic rule: the rule was **computed, not assumed**, and it does not survive.
The `es` fold's neighbour **flips** — `uk` under capital cities, `it` under centroids — and the
basis is itself unregistered; the three capitals span 1263/1364/1434 km so "nearest" wins by 5–13 %;
and **no fold has a land-border neighbour** in its pool, France having been the country that made
that rule work (decision 16). (a) removes the degree of freedom instead of registering one, and it is
the logic `G6.9` already uses: compare against all, nominate none.

#### The six nulls, and why reporting both matters

| fold | donor | donors | ESS % | worst strata gap vs the target |
|---|---|---:|---:|---:|
| `es` | `it` | 38,260 | 38.9 % | 14.7639 pp |
| `es` | `uk` | 15,852 | 70.5 % | 🔴 **30.7305 pp** |
| `uk` | `es` | 19,140 | 58.0 % | 9.7688 pp |
| `uk` | `it` | 38,260 | 38.9 % | 12.1025 pp |
| `it` | `es` | 19,140 | 58.0 % | 9.6249 pp |
| `it` | `uk` | 15,852 | 70.5 % | 🔴 **31.0235 pp** |

🔴 **The two nulls of one fold differ by up to 3.2x** (`it` fold: 9.62 vs 31.02 pp). Under any
single-nomination rule, one of those two numbers would have been the whole of `G6.2` and the other
invisible.

#### 🔴 `FINDING 78` — the three surveys' weights are not on one scale, and `G6.3` is 99.99 % one country on two folds

Σ `weight_dia_cal`: `ES` **162,500,706**, `IT` **162,800,375**, `UK` 🔴 **15,920** (mean
1.0043). Population-grossing versus scale-free, ~10,000:1, identical in every weight column — a
property of the **source microdata**. So the pooled null carries `it` **99.9902 %** on the `es` fold
and `es` **99.9902 %** on the `it` fold; only `uk` (49.95/50.05) is a real mixture, and only because
ES and IT gross to nearly the same total. On `es`, `G6.3` (14.7629 pp) and the `it`-only null
(14.7639 pp) agree to four decimals: **the same object under two names**, so two folds ship **two**
independent nulls, not three.

🟢 **Checked, not assumed:** `G6.1` starts from a uniform seed
(`4thJ_step6_rakeddonor.py:169`, `D-S5-10` (a)) and never reads a survey weight — **the
pre-registered bar and `prereg_addendum_01.md` are untouched**. All six `G6.2` nulls are
single-country, so the scale factor cancels on renormalisation. `G6.9` reads published tables. Steps
1–5 use weights within one country only. 🔴 **What moves: `G6.3` `es` 14.7629 pp and `it`
9.6242 pp must not be quoted as "pooled" until ruled;** `uk` 10.1901 pp is sound.

🔴 **Not repaired — the pooling basis is a BASIS CHOICE.** Put to the author as `D-S6-7`
(`IMP/docs/2026-08-22_D-S6-7_pooled-null-weight-scale.md`, recommendation **(a) equal country
mass**). What was added is diagnostic only: `country_mass()` and a dominance flag printed on every
run and stored in the JSON. ⚪ It was found only **because** (a) put the single-country nulls
beside the pooled one — a single nomination had an even chance of hiding it, and `G6.3`'s own
summary statistics (ESS 27.5 %, heaviest diary 0.0297 %) all looked ordinary. Second time a null has
looked healthy while being wrong; `FINDING 52` was the first.

#### Where this leaves Step 6

**DoD item 2 is three nulls of three built** — `G6.1` raked-donor, `G6.2` six per-donor-country,
`G6.3` pooled with its basis open. 🔴 **Items 6.3 (run the folds), 6.4 (score) and 6.5 (privacy
audit) still wait on GENERATED DIARIES — Step 7's deliverable. That is the critical path.**

⚪ Artefacts: `secondary_nulls.json` md5 `5bb023e51a3e5c4eb1a7e97b6d79ed66`, module
`0e2df0ca8d0fd4a02145b356a9be53bb`, selftest `1e8a5a3880250af68762368e99f78b11` (**42 of 42 green**,
was 30). Nothing is running on Speed.

---

### 2026-08-22 (night) — `D-S6-7` RULED (a) AND APPLIED: the pooled null `G6.3` now pools at EQUAL COUNTRY MASS. **Work item 6.2 is closed with THREE independent nulls per fold.**

🟢 **The ruling.** Each donor country's `weight_dia_cal` is renormalised to sum to **1.0**
before the pool is formed, so every donor country contributes the same total mass while, **within** a
country, the survey weights keep their exact relative values — which is what `D-S6-4` chose and
what `FINDING 53` requires, since `weight_dia_cal` is the column that corrects the three different day
bases. Registered in `Step6_docs/outputs_step6/prereg_addendum_02.md` **§5b**; the file was
re-frozen at md5 `fa1e4524f52c36ec82f02f825d6ff149` (its `D-S6-6`-only version was
`db450b89abbaf8f5480eb2479d50ae2d`) and §1–§5 are unchanged. 🔴 `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` **UNTOUCHED**; all three sidecars `md5sum -c` **OK**.

🔴 **It is a BASIS CHANGE and it is not raking.** Nothing is solved for, no held-out marginal
is read, no diary's weight is fitted to a target: one arbitrary factor is removed — the national
statistical office's choice to gross to the population or not — and nothing else. `prereg.md`
still permits raking in exactly one place, `G6.1`. The declared cost is that a Spanish diary now
counts ~1.21x a UK diary inside the pooled null, because 15,852 UK and 19,140 Spanish diaries share
the mass equally.

**What moved** (`secondary_nulls.json`, rebuilt, md5 `d4ce5e2f8345bc147d8d297f8f9606d7`):

| fold | `G6.3` worst strata gap | ESS | donor mass after |
|---|---|---|---|
| `es` | 14.7629 → **14.1839 pp** | 14,868 → 25,514 | `it` 50.0000 %, `uk` 50.0000 % |
| `uk` | 10.1901 → **10.1883 pp** | 25,436 → 25,429 | `es` 50.0000 %, `it` 50.0000 % |
| `it` | 9.6242 → **14.8304 pp** | 11,110 → 22,280 | `es` 50.0000 %, `uk` 50.0000 % |

🟢 **`G6.3` is no longer a duplicate of a `G6.2`.** On `es` it is 14.1839 pp against the
`it`-only null's 14.7639; on `it` it is 14.8304 pp against the `es`-only null's 9.6249. Before the
ruling those pairs agreed to **four decimal places**. `pool_dominated_by` is `null` on every fold.
**Step 6 ships three independent nulls per fold, not two.**

🟢 **Two predictions were CHECKED against the rebuild rather than assumed.** All six `G6.2`
nulls came back byte-identical (14.7639 / 30.7305 / 9.7688 / 12.1025 / 9.6249 / 31.0235 pp, every ESS
unchanged) because each is single-country and a constant scale factor cancels exactly on
renormalisation. And `uk` moved by **0.0018 pp**, which is the check on the whole story: that fold was
already a real mixture, because ES and IT gross to almost the same national total. `G6.1` was
re-checked at `tools/4thJ_step6_rakeddonor.py:169` — `weights = [1.0] * len(donors)`, a uniform
seed — so it never reads a survey weight and `prereg_addendum_01.md` stands.

**Guards, all seen firing** (`tools/4thJ_step6_secondary_nulls_selftest.py`, **55 ok / 0 FAILED**, was
42): the equalisation refuses a donor country with zero total mass instead of dividing by it
(`FINDING 52`'s failure mode); it is applied **unconditionally**, proved by reading the module's own
source, because a basis that switches itself on when the numbers look bad is a basis chosen after the
fact; the `FINDING 78` flag is re-pointed to mean *"the ruling was not applied — do not quote this
null"*; and the source label carries `EQUAL COUNTRY MASS (D-S6-7 (a))`, which `score_margin`'s Guard 1
uses to refuse any comparison against a pre-ruling number.

🔴 **One expectation broke and was left failing first.** The selftest's §6 case — a
donor whose source weight is NULL is excluded — read `0.2 / 0.8` on the raw survey weights and now
reads `0.5 / 0.5`, because after the exclusion the pool is one UK diary and one Italian diary. The
check was run and watched failing before the expectation was rewritten, and the old value is recorded
beside the new one.

🟢 **STEP 6 WORK ITEM 6.2 IS CLOSED.** Three nulls of three built: `G6.1` the raked-donor bar,
`G6.2` six single-donor-country nulls, `G6.3` the pooled all-country null at equal country mass.
Nothing in item 6.2 is waiting on anyone. 🔴 **Items 6.3 (run the folds), 6.4 (score) and 6.5
(privacy audit) still wait on GENERATED DIARIES — Step 7's deliverable. That is the critical
path.**

⚪ Artefacts: module `e79918f62e64c836ac6479a4d265da2e`, selftest
`6a2737f8883ab00d9baea23955565998`, `secondary_nulls.json` `d4ce5e2f8345bc147d8d297f8f9606d7`,
`prereg_addendum_02.md` `fa1e4524f52c36ec82f02f825d6ff149`. Record:
`Step6_docs/impl/2026-08-22_secondary-nulls.md`. Nothing is running on Speed, and nothing is scored.


---

### 2026-08-22 (evening) — 🟢 **`G6.4` IS BUILT, CALIBRATED ON THE REAL CORPUS AT 9 PASS / 0 FAIL, AND RUN ON THE LEG-4 BATCHES AT 1 PASS / 8 FAIL. 🔴 GETTING THERE TOOK FOUR CORRECTIONS TO THE CROSSWALK, THREE OF WHICH WOULD HAVE BIASED EVERY FOLD. `FINDING 84`, `D-S6-8`.**

`G6.4` reads *"Level-1 time budgets vs published tables, MAPE ≤ 15.0 %"*, and `G6.1`'s `MAE` is the
same quantity. Neither could be computed, because **nothing in this project mapped our 158 activity
codes onto Eurostat's `acl00` aggregates.** `tools/4thJ_step6_level1.py` now does, `_selftest.py` is
**48/48 green**, and `tools/4thJ_step6_g64_run.py` runs it on either arm.

#### 🔴 `FINDING 84` — the obvious crosswalk is wrong four times, and every error is one-directional

The obvious mapping is the leading digit: `0`→`AC0`, `1`→`AC1_TR`, … `9`→`AC9A`. Four corrections,
each established by arithmetic against the published table, never by reading a label.

**1. `995`–`999` are unspecified time, not travel.** They carry leading digit `9`. Eurostat puts them
under `AC99NSP`. In the corpus they are **26.09 min/day in the UK** against 0.02 in `es` and 0.00 in
`it` — and Eurostat's own `AC99NSP` is **49 min for the UK** against 1 and 1. Left in the travel
bucket they would have inflated one country's travel budget by a third, on the fold that country is
held out of.

**2. `998` (unspecified free time) is `AC4-8NSP`, inside `AC4-8`**, not unspecified time.

**3. 🔴 `910` (travel to/from work) STAYS IN `AC9A`. This was got wrong first.** `AC1_TR` reads
*"Employment, related activities and travel as part of/during main and second job"* and `AC9A` reads
*"Travel except travel related to jobs"*, which together read as though commuting belongs with
employment. It does not. **`AC9A`'s seven children sum to the published `AC9A` exactly — ES 70 = 70,
IT 79 = 79 — and `AC913` "Travel to/from work" is one of the seven.** Moving `910` across cost
15 min/day in *each* direction and took the travel category from a 5 % error to a 31 % one. The label
was misleading; the column total was not.

**4. 🔴 `AC9A`'s PUBLISHED PARENT IS UNUSABLE FOR THE UK.** Every other UK parent in `tus_00age` sums
to its children exactly. `AC9A` does not:

| country | `AC9A` parent | children sum | hole |
|---|---|---|---|
| ES | 70 | 70 | 0 |
| IT | 79 | 79 | 0 |
| **UK** | **129** | **81** | 🔴 **−48** |

The 48-minute hole matches the UK's anomalous `AC99NSP` of 49 almost exactly. The module therefore
takes `AC9A` as **the sum of its seven children** in every country — identical to the parent in ES and
IT, and the only defensible figure in the UK. Using the published parent charges the UK model a 58 %
travel error for a defect in the published table.

#### 🔴 Two more basis facts, both measured

**Weighting is not optional.** Unweighted, Italy's employment budget reads **113.7 min/day** against a
published 162 — a 30 % shortfall. Weighted by `weight_dia_cal` it reads **155.9**, a 3.8 % error.
`FINDING 53` said the three countries' diary weights hit three different day bases; this is what that
costs when it is ignored, and it is country-correlated.

**The age base is a choice.** Eurostat offers `TOTAL, Y15-20, Y20-24, Y20-74, Y25-44, Y45-64, Y65-74,
Y_GE65`. Our eight frozen bands reproduce **exactly three** with no straddling — `Y25-44`, `Y45-64`,
`Y_GE65`. `Y20-74` cannot be built (`15-24` straddles 20) and `Y65-74` is absent everywhere
(`FINDING 55`). `TOTAL`'s own population base is not stated in the JSON-stat and our floor is age 11,
so **`TOTAL` compares two different populations** and is reported as context, never scored.

#### 🟢 The calibration arm, which is what makes this a gate rather than a number

**The real harmonised corpus, weighted, against `tus_00age` 2010: 9 PASS / 0 FAIL.**

| fold | `Y25-44` | `Y45-64` | `Y_GE65` |
|---|---|---|---|
| `es` | 2.79 % | **1.49 %** | 2.57 % |
| `uk` | 3.43 % | 4.94 % | 2.70 % |
| `it` | 4.38 % | **1.33 %** | 2.24 % |

Every one inside the 15 % band, most inside 5 %. 🔴 **A gate whose own ground truth cannot pass it is
not measuring the model**, and until this arm was run the gate reported a 31 % travel error that
belonged entirely to the crosswalk. `outputs_step6/g64_corpus_calibration.json`.

#### 🔴 The Leg-4 generated arm: 1 PASS / 8 FAIL, and the failure has a legible signature

🔴 **`LEG-4 PILOT — NOT REPORTABLE.** `outputs_step6/g64_leg4_generated.json`.

| fold | `Y25-44` | `Y45-64` | `Y_GE65` |
|---|---|---|---|
| `es` | FAIL 42.6 % | **PASS 12.2 %** | FAIL 363.4 % |
| `uk` | FAIL 56.0 % | FAIL 13.8 % (MAE 22.9) | FAIL 215.1 % |
| `it` | FAIL 39.8 % | FAIL 74.7 % | FAIL 176.9 % |

The signature is one category. **`AC1_TR`, employment:** the pilot gives **106 min/day of work to
Spaniards over 65** (published 5), **144 to Britons over 65** (published 20), and only **65 to
working-age Italians** (published 263). It emits a roughly flat employment budget regardless of the
prefix. That is not a calibration error — **it is the model not conditioning on age or economic
status**, which is exactly the question `G6.7`'s fictional-country control exists to ask, answered
here by accident on a 1.48 B rehearsal model.

#### 🔴 A correction inside this entry, because it was made and it matters

The zero-cell rule of `D-S6-3` item 1 was implemented backwards on the first pass: the `< 1.0 %`
tolerance was used to decide **which published cells count as zero**, which classified Italy's
published `AC2` of **eleven minutes** (0.76 % of the day) as "approximately zero" and then failed the
real corpus for putting 14.67 minutes there. The tolerance governs **the model's value when the
published cell is zero**. Corrected; no level-1 published cell is zero (the smallest is one minute),
so the branch is now exercised on a synthetic table in the selftest rather than pretended into
existence. The corpus board moved 8 PASS / 1 FAIL → **9 PASS / 0 FAIL**.

#### 🔴 MAPE at these denominators, again

`AC1_TR` is 5 published minutes at `Y_GE65`. A model putting 106 there scores an APE of **2,020 %**,
which drags the band MAPE to 363 % and tells a reader nothing they could act on. **MAE is reported
beside every MAPE for this reason** (42.13 min/day for that same cell). This is `FINDING 39`'s
*"`MAPE > 20 %` is NOT EVALUABLE AS WRITTEN"* showing up again at level-1 granularity, and it is more
evidence for the same conclusion rather than a new problem.

#### `D-S6-8` — for the author

Four items, all recorded in `IMP/docs/2026-08-22_D-S6-8_level1-crosswalk.md`. Nothing is frozen and
`prereg.md` is untouched (md5 `e4243e07cdd80c9c846b91f40e3e8c45`).

#### What is NOT established

* `G6.1` still has no `model_value` **for the null side** — `tools/4thJ_step6_rakeddonor.py` has
  `score_margin` and the nulls are built, but the raked-donor null has never been expressed as a
  level-1 budget. That is the next piece and it is small now that the metric exists.
* `G6.5`, `G6.6`, `G6.7`, `G6.9` and the four privacy gates are untouched.
* The generated batches' **day-type mix** has not been checked against the calendar. `FINDING 53`
  applies to synthetic populations too and nobody has looked.

---

### 2026-08-22 (evening, second entry) — 🟢 **`G6.1` IS SCORED. THE PRE-REGISTERED BAR NOW HAS A NUMBER ON BOTH SIDES OF IT, FOR THE FIRST TIME.**

`tools/4thJ_step6_g61_rake_folds.py` said it in capitals in its own docstring: **"IT DOES NOT SCORE
ANYTHING."** It answered whether the null could be *built*. `tools/4thJ_step6_g61_score.py` scores it.

#### The quantity, and why it is this one

prereg §6 FAIL criterion 1 is *"MAE ≥ the raked-donor null"*. `G6.4` fixes what the error is measured
on — the level-1 time budget against the held-out country's published Eurostat table. So both sides
produce a level-1 budget in minutes/day, both are scored against **the same published column**, and
the margin is `null_MAE − model_MAE`, strictly positive or the claim fails. `V6.c` is enforced by
`score_margin`, which returns `passes=False` for a margin of exactly 0.0.

🔴 **The age-band restriction happens AFTER raking.** The null is raked onto the whole synthetic
population, exactly as the model was prompted from the whole synthetic population; the `Y25-44` slice
is taken from each afterwards. Raking separately per band would build three different nulls and make
each one easier.

#### 🟢 The bar itself — the number Leg 5 has to beat

| fold | donors | raked | ESS-bearing | null MAE `Y25-44` | `Y45-64` | `Y_GE65` |
|---|---|---|---|---|---|---|
| `es` | uk+it | 54,114 | 3 iterations, 0.24602 pp | **9.94** | **8.82** | **11.81** |
| `uk` | es+it | 57,400 | 5 iterations, 0.41662 pp | **21.79** | **19.21** | **18.54** |
| `it` | es+uk | 34,994 | 4 iterations, 0.24487 pp | **19.51** | **13.85** | **15.51** |

🔴 **The bar is not the same height in the three folds.** Spain's null is roughly twice as good as
Britain's — 8.8–11.8 min/day against 18.5–21.8. Whatever the model does, **`es` is the hard fold and
`uk` is the easy one**, and a cross-fold comparison that does not say so is comparing three different
difficulties. This is a property of the donors, not of the model, and it was not visible before today.

A sanity check the same run buys: `es`'s own real corpus scores **MAE 1.86–2.00** against the same
published table (the `G6.4` calibration arm). Its raked-foreigner null scores 8.8–11.8. So the null is
about five times worse than the country's own data — which is exactly what a demographically raked
pool of real *foreign* days should look like. A null scoring like the real thing would have meant the
rake was leaking the held-out country in.

#### 🔴 The Leg-4 pilot loses every cell, 0 of 9

🔴 **`LEG-4 PILOT — NOT REPORTABLE.** `outputs_step6/g61_leg4_scored.json`.

| fold | `Y25-44` | `Y45-64` | `Y_GE65` |
|---|---|---|---|
| `es` | −59.57 | −21.03 | −30.32 |
| `uk` | **−2.25** | **−3.72** | −17.83 |
| `it` | −58.25 | −40.83 | −5.70 |

Expected, and it is the reason `D-S7-3` (a) made Leg 4 a rehearsal — but the shape is worth keeping.
The pilot comes closest on `uk` at working age (−2.25, −3.72 min/day) and is furthest away on `es` and
`it` at `Y25-44` (−59, −58). That is the same signature `G6.4` found: **the model is not conditioning
on age or economic status**, so it does best exactly where the population is most homogeneous and
worst where the prefix carries the most information.

#### What this makes runnable that was not

`G6.1` was the last Tier-4 gate with no implementation path. It now has one, the null is built from
real diaries with all three registered collapses **imported from the runner rather than restated**,
and `score_margin`'s Guard 1 is satisfied by construction — both sides carry
`population_<c>.csv|D-S5-11b` as their marginals source.

#### Still not established

* `G6.3`'s pooled null and `G6.2`'s six single-donor nulls exist as *convergence* results
  (`prereg_addendum_02.md`) but have **not** been expressed as level-1 budgets, so their margins are
  not computed. Same shape as this work, one function call each.
* `G6.5`, `G6.6`, `G6.7`, `G6.9` untouched. The four privacy gates untouched.
* Nothing here is a model result.

---

### 2026-08-22 (evening, third entry) — 🔴 **`G6.2` AND `G6.3` ARE SCORED TOO, AND THE THREE NULLS TOGETHER SAY SOMETHING THE PRE-REGISTRATION DID NOT EXPECT: THE RAKED-DONOR NULL IS NOT THE STRONGEST ONE. `FINDING 85`, `D-S6-9`.**

`tools/4thJ_step6_secondary_score.py` turns `build_pooled` and `build_all_neighbours` into level-1
budgets on the same metric, against the same published column, so `G6.1`, `G6.2` and `G6.3` are three
readings of one comparison. Both nulls are **imported**, never rebuilt: `D-S6-7` (a)'s equal-country-
mass renormalisation and `D-S6-6` (a)'s refusal to nominate a neighbour stay in the module that owns
them. `outputs_step6/g62_g63_leg4_scored.json`.

#### 🔴 `FINDING 85` — the pre-registered bar is the weakest of the three in 6 of 9 cells

**NULL MAE, minutes/day against the published table. Lower = a stronger null = a harder bar.**

| fold | band | `G6.1` raked | `G6.3` pooled | `G6.2` per donor |
|---|---|---|---|---|
| `es` | `Y25-44` | 9.93 | **5.81** | `it` **5.01**  ·  `uk` 10.91 |
| `es` | `Y45-64` | **8.82** | 9.79 | `it` 11.23  ·  `uk` 15.26 |
| `es` | `Y_GE65` | 11.81 | 15.71 | `it` **11.27**  ·  `uk` 20.84 |
| `uk` | `Y25-44` | 21.79 | 11.69 | `es` 12.41  ·  `it` **10.80** |
| `uk` | `Y45-64` | 19.21 | 17.62 | `es` **17.18**  ·  `it` 19.25 |
| `uk` | `Y_GE65` | 18.54 | **18.43** | `es` 24.98  ·  `it` 18.99 |
| `it` | `Y25-44` | 19.51 | 13.81 | `es` **13.26**  ·  `uk` 15.27 |
| `it` | `Y45-64` | **13.85** | 14.07 | `es` 14.40  ·  `uk` 19.37 |
| `it` | `Y_GE65` | 15.51 | **14.54** | `es` 16.82  ·  `uk` 18.31 |

prereg §5 registers the raked-donor null as **"the strongest"** and calls the pooled all-country
average **"weak"**; `D-S6-7` demoted `G6.3` to *"Reported, **secondary**"*. On the level-1 time budget
the ordering is the other way round in **six of nine cells**, and on the `uk` fold at working age the
gap is a factor of two — 21.79 against 10.80.

**Two candidate mechanisms, neither asserted.** The rake starts from a **uniform seed** (`D-S5-10` (a))
and therefore **discards the survey weights**, while `G6.3` and `G6.2` carry `weight_dia_cal`; and a
raked null can converge on a small effective sample, which `FINDING 62` already showed for the `uk`
fold. Both are checkable and neither has been checked. It is **not** the day mix: the synthetic
populations are 71.43 / 14.29 / 14.29, the calendar week to two decimals, in all three folds.

#### 🔴 `D-S6-9` — what the bar is, now that the ordering is known to be wrong

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. `G6.1` stays exactly as pre-registered — the raked-donor null is the bar — and `FINDING 85` is declared as a result.** | The pre-registration is honoured to the letter, which is the entire value of having frozen it. The paper reports that the null we called strongest was not, and says so with the table |
| **(b)** | Take the minimum null MAE across all three as the operative bar. | Strictly harder, and therefore tempting — but it is **choosing the bar after seeing the numbers**, which is what prereg §6 exists to prevent. It would also make the bar's identity vary by cell |
| **(c)** | Re-seed the rake from `weight_dia_cal` instead of uniform and re-measure. | 🔴 A basis change to `D-S5-10` (a), which was ruled. It might well fix the ordering, and it must be the author's call, not a repair applied because the result was surprising |

🟢 **Found on a Leg-4 rehearsal, before any reportable model existed.** That is the only time this
could have been found without it looking like a reaction to a result.

#### The Leg-4 margins, for completeness

🔴 **`LEG-4 PILOT — NOT REPORTABLE.** The pilot loses to every null in every cell — 9 of 9 against
`G6.1`, and the same against all six `G6.2` nulls and `G6.3`. Its worst cells are `it Y25-44`
(−63.9 against the pooled null) and `es Y25-44` (−59.6 against the raked one); its best is
`uk Y45-64` (−3.7). No margin is positive anywhere.

#### 🔴 `G6.2` is six nulls and the module refuses to reduce them

`D-S6-6` (a) dropped the word *nearest*, so every donor country in a fold's pool is built and none is
nominated. The scorer prints both members of each pair and emits no aggregate. On `es Y_GE65` the two
differ by a factor of 1.85 — `it` 11.27 against `uk` 20.84 — which is exactly how large the
gate-shopping opportunity would have been.

#### Still not established

* `G6.5`, `G6.6`, `G6.7`, `G6.9` and the four privacy gates are untouched.
* No Step 6 gate has been **seen failing** under a registered perturbation yet. The nulls discriminate
  (the pilot loses, the real corpus passes `G6.4` 9 of 9) but the perturbation battery of the
  validation document has not been run.

---

### 2026-08-22 (evening, fourth entry) — 🟢 **STEP 6.5 IS STARTED. `G6.13` IS BUILT, PASSES 3/3, AND EACH OF ITS THREE CLAUSES HAS BEEN SEEN FAILING. 🔴 GETTING THERE COST TWO CORRECTIONS, AND THE SECOND ONE IS THE INTERESTING ONE: THE RAW GATE FAILED ALL THREE FOLDS AT `p < 1e-9` FOR A REASON THAT HAS NOTHING TO DO WITH PRIVACY. `FINDING 86`.**

`tools/4thJ_step6_g613_dcr.py`, artefact `outputs_step6/g613_leg4_dcr.json`. It is the one privacy
gate that needs no GPU: it reads the release and the corpus and nothing else.

#### The distance, because a diary is a sequence and tabular DCR does not apply

**Normalised Hamming over 144 ten-minute activity slots.** 144 is exact, not a resampling — every
duration in all 73,254 corpus diaries is a positive multiple of 10 and they sum to 1440, which is the
premise the tally automaton is built on and which was counted rather than assumed. It makes `DCR = 0`
mean what the gate needs it to mean: **the synthetic day is the same activity sequence, slot for slot,
as a real person's day.**

🔴 `LOC`, `ACT2` and `COP` are **not** in the distance. That is the **optimistic** reading — two days
identical in activity but differing in location score 0 here and are flagged. Declared, not defaulted.

#### 🔴 Correction 1 — the `test` reference set did not exist, and the gate said PASS anyway

Clause 2 compares median DCR to **train** against median DCR to **test**. Written as
`split == "test"`, it matched **nothing**: the corpus `split` column has exactly two values, `train`
and `heldout`, and `heldout` is `D-S6-1`'s second hold-out — the 10 % household split inside each
country — not the LOCO country hold-out. The first run built no `test` set, **skipped clause 2
entirely, and printed PASS on all three folds.**

A privacy gate that quietly drops one of its own comparisons is worse than one that does not run. The
module now **REFUSES** if any reference set is empty, and the three sets are named:

| set | what it is | role |
|---|---|---|
| `train` | the donor countries' `split == "train"` | what the model saw |
| `test` | the donor countries' `split == "heldout"` | same distribution, never seen |
| `country` | every diary of the LOCO held-out country | unseen **and** a different country — reported, **not** part of the verdict |

#### 🔴 `FINDING 86` — the raw train-versus-test comparison is a pool-size artefact, and it is enormous

With `test` in place, the gate FAILED **all three folds**:

| fold | median DCR train | test | difference | Mann-Whitney |
|---|---|---|---|---|
| `es` | 0.4028 | 0.4514 | −7.00 slots | z = −6.068, **p = 1.3e-9** |
| `uk` | 0.3611 | 0.4028 | −6.00 slots | z = −6.301, **p = 3.0e-10** |
| `it` | 0.4236 | 0.4583 | −5.00 slots | z = −8.097, **p = 5.7e-16** |

**None of it is evidence of anything.** `train` is **8.80× / 9.07× / 9.19×** the size of `test`,
because the second hold-out is a 10 % split. A nearest neighbour drawn from a nine-times-larger pool
is mechanically closer, memorisation or not.

🟢 **Size-matched, the signal vanishes completely.** `train` is subsampled without replacement to
`|test|`, 200 draws, seed 20260822:

| fold | matched train median [95 %] | test median | verdict |
|---|---|---|---|
| `es` | 0.4514 [0.4375, 0.4583] | **0.4514** | inside |
| `uk` | 0.4028 [0.3889, 0.4097] | **0.4028** | inside |
| `it` | 0.4583 [0.4514, 0.4653] | **0.4583** | inside |

The test median lands **exactly on** the matched train median in all three folds. The whole
`p < 1e-9` signal was pool size. This is the discipline the Overview already mandates for `G6.8` —
*"a sample-size-matched bootstrap … That last comparison is the honest one"* — arriving in a second
gate for a second reason. 🔴 **The raw comparison is still printed and still labelled `NOT THE
VERDICT`**: deleting it would hide the size effect, using it would be a false alarm.

#### 🟢 The other two clauses, at baseline

**Zero exact matches** against any reference set, in any fold. **Zero records** with NNDR < 0.33,
against any reference set, in any fold. Minimum DCR is 0.0972 (`es`) — about 14 of 144 slots — so the
closest the pilot ever comes to a real day is still fourteen ten-minute blocks away.

#### 🟢 Every clause seen failing, and the null perturbation moves nothing

| perturbation | what it injects | what fell |
|---|---|---|
| `null` | nothing | nothing — PASS |
| `verbatim` | one real TRAIN diary copied into the release | clause 1 (**1 exact match**) and clause 3 (NNDR < 0.33 in 0.167 %) |
| `nearcopy` | one real TRAIN diary with two slots changed | clause 3 only — DCR 0.0139, **no exact match**, which is the distinction the gate exists to draw |
| `leak_all` | all 600 records replaced by real TRAIN diaries | all three: 600 exact matches, NNDR < 0.33 in **99.5 %**, and the **size-matched** clause 2 finally fires (test 0.4236 above the matched interval [0.3958, 0.4132]) |

🔴 `leak_all` is the one that matters for clause 2: it shows the size-matched test **can** fire, so
its PASS at baseline is a measurement and not a gate that never fires.

#### What Step 6.5 still owes

* **`G6.10` loss-based MIA** and **`G6.11` reference-based MIA** need per-record losses from the
  adapter and from the untuned base — a GPU job, not written.
* **`G6.12` prefix-prompted extraction**, greedy and sampled, on strata with fewer than five training
  records — a GPU job, not written.
* The **three controls**: untuned base model, random-label-permutation adapter, and the train-versus-
  test perplexity gap under 5 %. None exists.
* 🔴 So `privacy_audit.md` cannot be written and **no release decision can be made**.

---

### 2026-08-22 (night) — 🟢 **THE AUTHOR RULED ALL FIVE DOCKET DECISIONS AND ALL FIVE ARE APPLIED. `G6.5` AND `G6.9` ARE BUILT AND BOTH ARMS ARE SCORED. 🔴 AND `G6.9` FAILS 9 OF 9 ON THE REAL WEIGHTED CORPUS — `FINDING 88`: ITS MARGIN CLAUSE CANNOT BE MET BY A PERFECT MODEL.**

Ruling archived at `IMP/docs/DONE/2026-08-22_rehearsal-docket_findings-and-decisions.md`. New decision:
`IMP/docs/2026-08-22_D-S6-10_g69-margin-and-the-european-mean.md`. Code:
`tools/4thJ_step6_g65_g69.py`. Artefacts: `outputs_step6/g65_g69_corpus_calibration.json` and
`g65_g69_leg4.json`.

#### What the rulings changed, honestly: almost nothing, and that is the point

| ruling | option | what had to change |
|---|---|---|
| `D-S6-8` item 1 — `AC9A` | (a) children sum | **nothing.** `4thJ_step6_level1.py` already summed the seven children in all three countries, with the UK's −48 min parent hole named in the code |
| `D-S6-8` item 2 — age base | (a) three exact bands | **nothing.** `4thJ_step6_g64_run.py` already excludes `ALL` from the board and prints *"context only"* beside it |
| `D-S6-8` items 3 & 4 | confirmed | **nothing.** Weight asymmetry and `MAE`-beside-`MAPE` were already implemented |
| `D-S6-9` — the bar | (a) honour the pre-registration | **nothing.** `G6.1`'s bar is the raked-donor null and `FINDING 85` is reported, not acted on |

🟢 That four of five rulings required no code change is the strongest evidence the recommendations were
not written to justify work already done. The one that did require change was `D-S7-5`, in Step 7.

#### `G6.5` — an AND over three frozen criteria, two of them READ BY FILE

`prereg.md` freezes `G6.5` as: the claim fails if **any** of (1) MAE ≥ the raked-donor null, (2) MAPE
> 20 %, (3) the sign of the country's divergence from the European mean is inverted.

🔴 Criteria 1 and 2 are read out of `g61_*.json` and `g64_*.json` **by file, never recomputed.** Two
modules recomputing the same bar can disagree about it, and the one a reader believes is whichever
printed last. Only the **sign arm** is new code — which is what the val doc's own perturbation table
demands, since a 25 % category shift must move `G6.4` and the MAPE arm while an inverted divergence
must move the sign arm and *not* `G6.4`.

| arm | `G6.5` board |
|---|---|
| **real corpus**, weighted | 🟢 **7 PASS / 2 FAIL** |
| **Leg-4 pilot**, unweighted | 0 PASS / 9 FAIL |

Both corpus failures are the **sign arm alone**: `es Y45-64` on `AC3` and `it Y25-44` on `AC1_TR`.

#### 🔴 The European mean is not published. It had to be built, and that is `D-S6-10` item 2.

Probed 2026-08-22: `tus_00age`'s `geo` dimension carries **22 countries and no EU aggregate at all** —
AT BE BG DE EE EL ES FI FR HU IT LT LU LV NL NO PL RO RS SI TR UK. Implemented as the **unweighted
mean over every HETUS country with a complete profile in the band**, fold country included, from
`tus_00age_ALLGEO_2010_TIME_SP_T.json` (md5 `86eeb1b290519d25ab134731e3a813d2`). Not
population-weighted — that would make "European" mean Germany and Turkey. An aggregate is scored only
where the **published** divergence exceeds 2.0 min/day; below that the `h:mm` rounding swamps the sign,
and those aggregates are reported `not_scored`, which is not a pass.

#### 🔴 `FINDING 88` — `G6.9`'s margin clause is unsatisfiable by ground truth

Operationalised literally — margin = MAE(runner-up) − MAE(own), bar = the **mean** pairwise MAE between
the three published profiles — a model reproducing the held-out country's published table **exactly**
still fails, because its margin is one pairwise distance and the bar is the mean of three. The nearest
pair is below the mean by construction.

| band | pairwise MAE | mean spread | perfect `es` | perfect `uk` | perfect `it` |
|---|---|---|---|---|---|
| `Y25-44` | 11.83 · 13.17 · 15.67 | 13.56 | 11.83 ❌ | 13.17 ❌ | 11.83 ❌ |
| `Y45-64` | 12.67 · 16.83 · 20.50 | 16.67 | 12.67 ❌ | 16.83 ✔ | 12.67 ❌ |
| `Y_GE65` | 15.17 · 23.33 · 20.17 | 19.56 | 15.17 ❌ | 20.17 ✔ | 15.17 ❌ |

**A perfect model fails 7 of 9.** The real corpus fails 9 of 9.

🟢 The discrimination itself works: the nearest published profile is the country's own in **8 of 9**
corpus cells, at 2–7 min/day against 11–18 for the runner-up. Under `D-S6-10` item 1's recommended
scale-free margin — `(MAE_runner − MAE_own) / MAE(own_pub, runner_pub) > 0.5` — the corpus scores
**5 of 9** and the pilot **2 of 9**, and `es` reads 0.79 / 0.98 / 0.99.

#### 🔴 `FINDING 89` — the Italian corpus is nearer SPAIN'S published table than Italy's own

On `Y25-44`, real weighted `it` scores MAE **5.01 against `es`** and **10.40 against `it`**. Not an
artefact: `D-S6-2` established that Eurostat's `2010` column for Italy is the **2008-09** survey while
our microdata is **ISTAT 2013-14**, which appears in no Eurostat table at all. `G6.9` on the `it` fold
therefore compares a 2013-14 corpus against a 2008-09 table, and working age is where five years show.
Second basis asymmetry on that fold, after `D-S6-3`'s.

#### Seen failing — `G6.5` yes, `G6.9` not yet, and the clause says so

Run on the **corpus** arm, because a gate already failing at baseline cannot be seen to fall:

| perturbation | fells |
|---|---|
| `null` | nothing |
| `shift25` (+25 % on `AC3`, mass back to `AC0`) | `G6.5` in 6 cells, **all 6 by the sign arm alone** |
| `invert_sign` (reflect the model through the European mean) | `G6.5` in 7 cells, **all 7 by the sign arm alone** — and `G6.4` not at all, a rigid motion about the mean |
| `neighbour_tables` | 🔴 **nothing.** It cannot fell a gate already failing every cell. It goes live the moment `D-S6-10` item 1 is ruled |

🔴 **Coverage clause: FAIL**, reported as such. `G6.5` has been seen failing; `G6.9` has not.

---

### 2026-08-22 (night) — 🟢 **STEP 6.5 MIA IS COMPLETE ON ALL THREE FOLDS. `G6.10`, `G6.11` AND `G6.12` PASS EVERYWHERE, BOTH RUNNING CONTROLS PASS, AND THE COVERAGE CLAUSE PASSES ON EVERY FOLD WITH ZERO NO-OP PERTURBATIONS. 🔴 GETTING THERE COST `FINDING 87`, WHICH WOULD HAVE MADE A PRIVACY GATE PASS FOR THE WRONG REASON.**

`tools/4thJ_step6_privacy_mia.py`, 366 to 508 lines. Jobs **1286235** (`es`), **1286236** (`uk`),
**1286237** (`it`); one `nvidia_a100_2g.20gb` slice each, 22 to 25 minutes. Artefacts
`outputs_step6/privacy_mia_leg4_{es,uk,it}.json`. 🔴 **LEG-4 PILOT — NOT REPORTABLE**, and the string
`"LEG-4 PILOT -- NOT REPORTABLE"` is written into every artefact's `provenance` field so a later
reader cannot mistake it.

#### 🔴 `FINDING 87` — one tokeniser attribute, two incompatible requirements, and a privacy gate that would have passed on garbage

The module does two different things with the same tokeniser. `G6.10` and `G6.11` score **per-record
losses**, which needs **RIGHT** padding, because the keep-mask that selects real tokens is built by
indexing from the left. `G6.12` **generates** from a prefix, which needs **LEFT** padding, because a
decoder-only model attends to whatever sits immediately before the first generated token; with right
padding that is a run of PAD.

The first version set `padding_side = "right"` once, at load, and never changed it. `G6.12` would then
have generated from a batch of pad-terminated prompts, produced continuations of nothing, matched
nothing, and reported **`PASS` — zero extraction**. 🔴 **That is a false negative in a privacy gate:
the failure mode is silence, and silence is exactly what the gate reads as success.** The fix is one
line, set at the top of the generation block and commented with the reason:

```python
# `FINDING 87`: the loss pass needs RIGHT padding (the keep-mask indexes from
# the left) and `generate` needs LEFT padding ... a FALSE NEGATIVE in a privacy gate.
tok.padding_side = "left"
```

The `transformers` warning *"right-padding was detected"* still appears in the logs — it is emitted by
the **loss** pass, where right padding is correct — so its presence is not evidence the bug is back.

#### 🟢 The baseline board, all three folds

| | `es` | `uk` | `it` | bar |
|---|---|---|---|---|
| `G6.10` loss MIA, AUC | **0.5481** | **0.5336** | **0.5539** | < 0.65 |
| `G6.10` TPR at FPR 0.001 | 0.0005 | 0.0000 | 0.0005 | < 0.05 |
| control, **untuned base** AUC | 0.4914 | 0.5012 | 0.4874 | approx 0.50 |
| `G6.11` reference MIA, AUC | **0.5204** | **0.5074** | **0.5274** | < 0.75 |
| control, train/test **ppl gap** | 0.0143 | 0.0097 | 0.0182 | < 0.05 |
| `G6.12` exact matches, greedy / sampled | 0 / 0 | 0 / 0 | 0 / 0 | 0 |

**9 of 9 scored gates PASS, both running controls PASS on all three folds.** `n = 2000` per class,
seed 20260822.

🔴 **The untuned-base control is what makes the tuned numbers readable.** All three sit within 0.013
of chance, so the member and non-member splits do not differ for any reason other than membership —
without it an AUC of 0.55 could be a distribution artefact rather than a memorisation floor.

#### 🔴 `G6.12`'s attack surface is not the same size in the three folds

| fold | rare strata (< 5 training records) | records in them |
|---|---|---|
| `es` | 33 | 91 |
| `uk` | **14** | **40** |
| `it` | 39 | 103 |

`it` offers the extraction attack **2.6x** as many targets as `uk`. The gate is the same and the
verdict is the same, but **a `PASS` on `uk` is a weaker statement than a `PASS` on `it`**, and the
three must never be quoted as one number. This is the demographic tail of the LOCO split showing up in
a privacy gate: `uk` is the fold whose donor pool is `es` + `it`, the two largest shards.

#### 🟢 Six injections, and every gate seen falling on every fold

Baseline and perturbation traverse **identical code**: the verdicts were factored out into
`score_g610`, `score_g611`, `score_pplgap` and `g612_match`, and a nested `board(tm, tn, bm, bn, dec)`
closure is called once for the baseline and once per injection. A gate cannot pass at baseline and be
scored by a different rule under attack.

| injection | what it does | fell (`es` / `uk` / `it`, identical) |
|---|---|---|
| `null` | nothing | **nothing** — the board is stable |
| `g610_memorise` | member losses down 0.5 nats | `G6.10` + `G6.11`, AUC to **0.9999 / 0.9999 / 0.9997** |
| `g610_tail` | the top **8 %** of members down 5.0 nats | **`G6.10` only** |
| `g611_reference` | base-model member losses **up** 1.0 nat | **`G6.11` only**, AUC to 0.9858 / 0.9928 / 0.9867 |
| `pplgap_widen` | non-member losses times 1.15 | `G6.10` + the ppl-gap control |
| `g612_verbatim` | one real training diary pasted into the greedy decode | **`G6.12` only**, 1 exact match |

🔴 **Coverage clause: PASS on all three folds, and `no_op_perturbations` is EMPTY in all three
artefacts.** Every injection moved something; none was decorative.

**`g610_tail` is the one that earns its place.** `G6.10` has two clauses — AUC, and TPR at
FPR = 0.001 — and an attack that lifts every member equally only ever exercises the first. Driving the
worst-off 8 % of members down 5 nats leaves the AUC essentially where it was (`es` 0.5481 to 0.5510)
and takes **TPR from 0.0005 to 0.0800** against a bar of 0.05. 🔴 **The second clause has now been seen
failing on its own, which is the only way to know it is not decorative.** The first draft of this
injection was a no-op — it moved TPR to 0.0100, under the bar — and was strengthened until it fired.

**`g611_reference` had to be confined by hand.** Written the obvious way it shifted the *tuned* member
losses, which both gates read, and felled `G6.10` as collateral. Shifting only the **base** model's
member losses reaches `G6.11`'s likelihood ratio and nothing else. 🔴 **`pplgap_widen` is NOT
confinable** — the perplexity gap and `G6.10` are computed from the same two loss vectors, so any
injection that widens one moves the other. That is recorded in the module, not worked around.

#### 🔴 What Step 6.5 still owes, unchanged

The **third registered control — the random-label-permutation adapter — is still NOT RUN.** It needs
its own training run and sets the floor for pure sequence memorisation. Every artefact carries the
refusal text in `control_random_label_permutation`, and every job prints it:

> 🔴 CONTROL NOT RUN: random-label-permutation adapter. Two of three registered controls are present.
> No release decision can rest on this.

🔴 **`privacy_audit.md` therefore still cannot be written, and no release decision can be made** — on
Leg 4 or on Leg 5. Four of the five Step 6.5 gates now exist and pass (`G6.10`, `G6.11`, `G6.12`,
`G6.13`); what is missing is not a gate but a control.

---

### 2026-08-22 (late night) — 🟢 **`D-S6-10` AND `D-S6-11` RULED AND APPLIED. THE `G6.9` MARGIN CLAUSE IS NOW SATISFIABLE, AND ON THE REAL CORPUS IT GOES FROM 0 OF 9 TO 5 OF 9 WITH THE COVERAGE CLAUSE PASSING FOR THE FIRST TIME.**

Both documents are in `IMP/docs/DONE/`. Four items ruled, **one code change**.

#### 🟢 `D-S6-10` item 1 — option (a), the dimensionless relative margin

`FINDING 88` showed the original clause was **unsatisfiable by a perfect model**: the numerator was
ONE pairwise distance and the bar was the MEAN of three, so a model sitting exactly on its own
published table failed 7 of 9 corpus cells. The ruled replacement, in
`tools/4thJ_step6_g65_g69.py`, `G69_REL_MARGIN_MIN = 0.5`:

> **(MAE_runner − MAE_own) / MAE(own_pub, runner_pub) > 0.5**

Perfect model → 1.0. Equidistant → 0.0. The bar is the midpoint. The denominator is the published
distance **for the pair actually in contention**, not the three-country average, because the question
is whether the model separates the two candidates it could plausibly be confused between.

🔴 One defect fixed while implementing it, and it is not cosmetic: the runner-up was read as
`order[1]`. When the model lands on the **wrong** country, `order[1]` is the SECOND wrong country, and
the gate would have reported a healthy margin for a model that had just misidentified itself. The
runner-up is now the nearest country **that is not `own`**, whatever the model did. `it Y25-44` is
exactly that case and would have been mis-scored.

🔴 `between_country_spread` is still computed and still written to the artefact, labelled
`REPORTED ONLY`. Deleting it would make every reading before 2026-08-22 unreproducible.

#### 🟢 The calibration, and it is the thing that shows the new bar works

| fold | band | **rel. margin** | MAE own | MAE runner | published pair distance | nearest |
|---|---|---|---|---|---|---|
| `es` | Y25-44 | **0.7907** | 2.00 | 12.41 | 13.17 | `es` |
| `es` | Y45-64 | **0.9844** | 1.94 | 14.40 | 12.67 | `es` |
| `es` | Y_GE65 | **0.9862** | 1.86 | 16.82 | 15.17 | `es` |
| `it` | Y45-64 | **0.7255** | 2.04 | 11.23 | 12.67 | `it` |
| `uk` | Y_GE65 | **0.6974** | 4.24 | 18.31 | 20.17 | `uk` |
| `it` | Y_GE65 | 0.4752 | 4.06 | 11.27 | 15.17 | `it` |
| `uk` | Y45-64 | 0.4922 | 6.97 | 15.26 | 16.83 | `uk` |
| `uk` | Y25-44 | 0.4400 | 5.12 | 10.91 | 13.17 | `uk` |
| `it` | Y25-44 | **−0.4555** | 10.40 | **5.01** | 11.83 | 🔴 `es` |

🟢 **The bar separates exactly what it should.** Spain's corpus sits on Spain's published tables
(MAE 1.86–2.00) and scores 0.79–0.99. Every cell below the bar is a cell where **the real corpus is
far from its own published table** — `uk Y25-44` 5.12, `uk Y45-64` 6.97, `it Y_GE65` 4.06 — and the
one negative is `FINDING 89`, where Italy's own diaries are nearer **Spain's** table (5.01) than
Italy's (10.40) because Eurostat's IT 2010 column is the 2008-09 survey and our microdata is ISTAT
2013-14. 🔴 **The four remaining failures are a data problem, not a gate-design problem**, and none of
them is a near-miss caused by an arbitrary threshold.

#### 🟢 The coverage clause passes on the corpus arm for the first time

| injection | `G6.5` fell | `G6.9` fell |
|---|---|---|
| `null` | 0 | 0 |
| `shift25` | 6 (all 6 by the SIGN ARM ALONE) | 4 |
| `invert_sign` | 7 (all 7 by the SIGN ARM ALONE) | 5 |
| `neighbour_tables` | 0 | **5** |

🔴 **`neighbour_tables` was a no-op before this ruling** — it cannot fell a gate that already fails
every cell. It now fells `G6.9` in five of nine, which is the whole reason the coverage clause moved
from FAIL to **PASS**. Board on the corpus arm: `G6.5` **7 PASS / 2 FAIL**, `G6.9` **5 PASS / 4 FAIL**.

On the Leg-4 pilot arm `G6.9` goes 0/9 → **2/9**; `G6.5` stays 0/9 and its coverage clause stays FAIL
there, correctly — a gate already failing at baseline cannot be *seen* to fall. 🔴 **LEG-4 PILOT,
NOT REPORTABLE.**

#### 🟢 `D-S6-10` item 2 — confirmed, and it was already built this way

The European mean is the **unweighted** mean over every HETUS country with a complete profile in the
band, **the fold's own country included**, with `SIGN_FLOOR_MIN = 2.0` min/day below which a published
divergence is treated as rounding noise. Equal vote per country; no crowding-out by the large
populations. No code change — the constant is now annotated with the ruling so the next reader does
not have to re-derive that it was deliberate.

#### 🟢 `D-S6-11` — all three items confirmed, no code change

1. **Perturbation axis and amplitude guard.** Exponential tilt on age rank, λ ∈ [−0.6, +0.6] over five
   levels, amplitude guard ≥ 30 min/day — Spain measures **79.3**. This is what replaced
   `FINDING 90`'s first attempt, a distribution reversal worth **0.8 min/day** end to end.
2. **Prefix pricing — option (a).** The fixed five-rung backoff ladder, with the share priced at each
   rung reported per λ level. **0 % of prefixes dropped**, so no selection bias correlated with λ.
   The first build dropped 24.6 % of the population as unpriced.
3. **Anti-stereotype clause.** `MAE(gen, EXP(λ)) < MAE(gen, profile_c)` for **every** real country
   `c`, against the corpus-**weighted** real national budgets — not the published tables.

Items 1–3 were already implemented as ruled; all three modules now carry the ruling stamp.

---

### 2026-08-22 (late night, second entry) — 🟢 **`G6.6` IS BUILT. IT WAS THE LAST UNBUILT STEP 6 GATE, IT HAD NO NUMERIC BAR ANYWHERE, AND ITS CALIBRATION ARM IS GREEN 3/3 WITH THE COVERAGE CLAUSE PASSING. 🔴 ITS REGISTERED PERTURBATION IS A NAMED GAP THAT NO RE-SCORE CAN CLOSE.**

`tools/4thJ_step6_g66_heldin.py`, artefact `outputs_step6/g66_corpus_calibration.json`.

#### 🔴 The gate had no threshold. Anywhere.

The val doc's row reads *"Bounded; small by construction under joint training"* and cites `RL05`. The
**frozen prereg does not mention `G6.6` at all**, and neither addendum does. A gate whose requirement
is an adjective cannot be seen failing, so the first job was to give it a measurable form without
inventing a band — bands belong to the author.

#### What it scores, and why it costs no new design

Each country is a **donor in exactly two folds and held out in one**. That asymmetry is free evidence:

| fold | generates at | |
|---|---|---|
| `es` | `uk` prefixes, `it` prefixes | the two countries it trained on |
| `uk` | `es` prefixes, `it` prefixes | |
| `it` | `es` prefixes, `uk` prefixes | |

Six (fold, donor) batches, each scored with **`G6.4`'s own machinery** — level-1 budget against the
donor's published tables — so held-in and held-out numbers are commensurable **by construction**, not
by assertion. The Step 5 prefix files already exist; nothing new is designed.

**Clause 1, absolute:** the donor's worst scoreable-band MAPE must clear `G6.4`'s bar, **15.0 %**,
reused verbatim rather than chosen a second time. A model that cannot reproduce a country it was
*trained on* has no standing on a country it was not.

**Clause 2, paired — the forgetting clause:** `MAPE(F, D)` with `D` held **in**, against `MAPE(D, D)`
with `D` held **out**, the latter read **by file** from the `G6.4` artefact. Held-in is the easier
task. 🔴 **Held-in scoring worse than held-out is the alarm**, and the *direction* is what carries the
meaning. The tolerance is `--tolerance-pp`, default **0.0** — the strict reading — and widening it is
a band, so it is left to the author rather than assumed.

#### 🟢 The calibration arm, on the real corpus

| country | n | worst band MAPE | clause 1 |
|---|---|---|---|
| `es` | 19,140 | **4.64 %** | PASS |
| `uk` | 15,852 (2 dropped for a null weight) | **5.96 %** | PASS |
| `it` | 38,260 | **11.50 %** | PASS |

Weighted by `weight_dia_cal` (`FINDING 53`). The three numbers reproduce `G6.4`'s corpus calibration
exactly, which is the cross-check that the two modules share a scorer.

🔴 **Clause 2 is NOT SCORED on the corpus arm and says so.** A real corpus does not belong to a fold,
so there is no held-in / held-out pair. It would have been trivial to compare a country with itself
and print PASS; that is precisely the failure `FINDING 86` caught in `G6.13`, where a reference set
that did not exist was silently skipped and the gate reported PASS anyway.

#### 🟢 Coverage clause: PASS

| injection | what fell |
|---|---|
| `null` | **nothing** |
| `wrong_tables` (score the donor against a country whose token was never used) | all three |
| `flatten_to_ac0` (a model that forgot everything and sleeps all day) | all three |
| `degrade_donor` (40 % of paid work and study moved into personal care) | all three |

#### 🔴 The registered perturbation is a NAMED GAP

The val doc registers *"train country-by-country sequentially → `G6.6`"*. That lever exists —
`4thJ_step4_train.py --perturbation sequential_countries`, added under `FINDING 6` because the
coverage clause would otherwise have reported a gate with no lever at all — but it is a **training**
run, not a re-score. This module refuses to pretend otherwise: it prints `NOT RUNNABLE HERE`, writes
`runnable: false` into the artefact, and the coverage clause names the gap explicitly.

#### 🟢 The loss-side answer is already on disk, at zero compute

`G4.9` — per-country held-in probe loss, final checkpoint within +5 % of its own best — reads **PASS
6 of 6** from the existing Leg-4 detectors, with `regression` exactly **0.0** in every pair:

| fold | donor | epoch 0 | epoch 1 | Δ |
|---|---|---|---|---|
| `es` | `it` | 0.85516 | 0.84424 | **−0.01092** |
| `es` | `uk` | 0.97482 | 0.96130 | −0.01352 |
| `uk` | `es` | 0.88149 | 0.86660 | −0.01489 |
| `uk` | `it` | 0.85185 | 0.83502 | −0.01682 |
| `it` | `es` | 0.89832 | 0.86979 | **−0.02853** |
| `it` | `uk` | 0.98466 | 0.96976 | −0.01490 |

Every donor improves monotonically; nothing is forgotten under joint training, which is what `RL05`'s
prohibition on sequential training is for. 🔴 **But `regression = 0.0` in all six is guaranteed by the
shape of the run, not earned**: Leg 4 has two epochs and both are monotone, so the final epoch IS the
best epoch and the gate cannot report anything else. **Leg 5 has three epochs and is the first run
where `G4.9` can say something.** Do not quote 6/6 as evidence of resistance to forgetting.

#### What `G6.6` still owes

Six generation batches — the fold's adapter, the donor's Step 5 prefixes, `--tag g66<donor>`. Until
they exist the generated arm exits **2** and prints the six missing filenames. 🔴 **NOT SCORED is not
a pass**, and the module will not print a board without them.

---

### 2026-08-22 (late afternoon) — 🟢 **`G6.6`'s GENERATED ARM IS RUN — SIX BATCHES, 3,600 DIARIES, 600/600 VALID AND 600/600 TERMINATED IN EVERY ONE. 🔴 IT FAILS 6 OF 6 ON CLAUSE 1, AND IN CHASING WHY, THE PRIMARY TRANSFER GATE `G6.4` TURNED OUT TO BE MEASURING SOMETHING OTHER THAN FIT. `FINDING 90`, `D-S6-12`.**

Jobs 1286254–1286259, one per `(fold, donor)` ordered pair, each the fold's Leg-4 adapter driven by
the **donor country's** 100,000-prefix pool. Artefact `outputs_step6/g66_leg4_generated.json`.

#### The board

| pair | worst band MAPE | held-out ref (`G6.4`) | delta | clause 1 | clause 2 |
|---|---|---|---|---|---|
| `es`/`it` | 206.19 % | 176.87 % | **+29.32 pp** | FAIL | **FAIL** |
| `es`/`uk` | 85.14 % | 215.13 % | −129.99 pp | FAIL | PASS |
| `it`/`es` | 122.19 % | 363.44 % | −241.25 pp | FAIL | PASS |
| `it`/`uk` | 105.64 % | 215.13 % | −109.48 pp | FAIL | PASS |
| `uk`/`es` | 249.88 % | 363.44 % | −113.56 pp | FAIL | PASS |
| `uk`/`it` | 145.96 % | 176.87 % | −30.91 pp | FAIL | PASS |

Clause 1 (MAPE ≤ 15 %, `G6.4`'s bar reused) fails everywhere, which for a 1.48 B two-epoch pilot
scored at 363/215/177 % **held out** is the expected reading and not news.

🔴 **Clause 2 is the finding, and its one failure is instructive.** Held-in beats held-out in five
pairs of six. The exception is `es`/`it`: the `es`-fold model, which had **Italy in its training
data**, matches Italy's published tables *worse* (206.19 %) than the `it`-fold model that never saw
Italy (176.87 %). And the two models that both hold Italy in disagree with each other by **60 pp**
(206.19 vs 145.96). 🔴 **The pair-to-pair spread is larger than the held-in advantage**, so at pilot
scale clause 2 is not resolving membership. It is a `PASS 5/6` that must never be quoted as one.

#### 🔴 The perturbation battery on this arm is vacuous, and is recorded as such

All four runnable injections "fell" all six pairs — but the gate was **already failing at baseline**,
so nothing was demonstrated. This is the identical situation to `G6.5`'s pilot arm. The `null`
perturbation moving the verdict is the tell. **The demonstration of record for `G6.6` remains the
corpus arm**, where baseline is 3/3 PASS and the three real injections each felled it. The coverage
clause is FAIL here for the separate, honest reason that `sequential_countries` needs its own
training run — a **NAMED GAP**, not an omission.

#### 🔴 `FINDING 90` — the worst-band rule selects the smallest denominator, and it reaches `G6.4`

Every one of the six worst-band verdicts above is driven by a cell whose **published** value is
between **1 and 15 minutes per day**. Pulling the same view on `G6.4`, the reported gate:

| fold | reported | band | that band's **MAE** | driving cell |
|---|---|---|---|---|
| `es` | 363.44 % | `Y_GE65` | 42.13 min | `AC1_TR` pub **5**, model 106.1 |
| `uk` | 215.13 % | `Y_GE65` | 36.37 min | `AC2` pub **1**, model 7.3 |
| `it` | 176.87 % | `Y_GE65` | 21.21 min | `AC2` pub **1**, model 6.3 |

**`Y_GE65` is not the worst-fitting band; in minutes it is among the best.** Italy's `Y_GE65` MAE of
21.21 min is the **second-lowest of the twelve rows in the artefact**, while its `Y25-44` — MAE
77.75, nearly 4× larger — is reported at 39.76 %. Selecting on MAE instead flips the answer in two
folds of three. Over the eighteen `(pair, band)` cells here the two metrics are **negatively
rank-correlated, Spearman −0.5604.**

The cause is not the model. Eurostat publishes ~1 min/day of employment for the over-65s because
retired people do not work; that is the right number to publish and a useless denominator.
`D-S6-3` item 1 ruled MAPE on **non-zero** cells — these are non-zero, so the rule sends them to the
MAPE arm. It anticipated zero, not **near-zero**, and all three headlines live in near-zero.

Compounded with `FINDING 39`'s country-dependent rounding floor, a cell printed `1` is truly in
`[0.5, 1.5]`, so its APE is **not identified**: `uk`'s 630 % spans **387–1360 %** on the rounding
convention alone; `it`'s 530 % spans 320–1160 %.

🟢 **Not all three are artefacts and this must not be written as if they were.** `es`'s cell spans
1829–2258 % — 106 minutes of daily travel against a published 5 is a genuine ~20× error that
survives any rounding assumption. The `uk` and `it` cells do not survive it.

🔴 **`D-S6-12` is open and blocks quoting any `G6.4` or `G6.6` headline.** It is a band question,
so nothing was changed: no checker edited, `G6.4`'s artefact as it was, `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` intact. It does **not** reach `G6.9` (dimensionless MAE ratio
since `D-S6-10`) nor `G6.1`/`G6.2`/`G6.3` (in pp).

---

### 2026-08-22 (evening) — 🟢 **`G6.7` IS RUN ON ALL THREE FOLDS — FIFTEEN BATCHES, 9,000 DIARIES, THE AMPLITUDE GUARD HELD EVERYWHERE AND 0 % OF PREFIXES WERE DROPPED. 🔴 IT FAILS 3/3 ON CLAUSE 1, AND THE PER-AGGREGATE VIEW SAYS THE OPPOSITE OF THE HEADLINE: THE MODEL RECEIVES THE CONDITIONING VECTOR AND ATTENUATES IT. `FINDING 91`, `D-S6-13`.**

Jobs 1286260–1286274, five λ levels per fold under the fictional token `x_zz`. Artefacts
`outputs_step6/g67_leg4_{es,uk,it}.json`.

| fold | pooled slope | bar | clause 2 recites at |
|---|---|---|---|
| `es` | 0.0358 (R² 0.0018) | ≥ 0.80 | levels 0, 1, 2 (`uk`, `uk`, `uk`) |
| `uk` | 0.2437 (R² 0.1012) | ≥ 0.80 | levels 0, 1, 2 (`es`, `uk`, `es`) |
| `it` | 0.1899 (R² 0.1008) | ≥ 0.80 | levels 0, 1 (`es`, `es`) |

#### 🟢 Clause 2 works, and reads cleanly

The anti-stereotype clause fires at **low |λ|** and clears at **high |λ|** in every fold: MAE against
the conditioning vector falls monotonically across the levels (`it`: 47.52 → 43.41 → 27.20 → 15.97 →
**9.16**) while MAE against the national profiles stays flat at 31–49. **The weaker the conditioning
signal, the more the model falls back on a national pattern** — which is exactly the behaviour the
clause was written to detect, arriving as a graded result rather than a binary one.

#### 🔴 `FINDING 91` — the pooled slope cannot separate attenuation from indifference

`AC2` (employment), the channel the λ tilt principally moves:

| fold | `AC2` **R²** | slope | requested | delivered | **gain** |
|---|---|---|---|---|---|
| `es` | 0.845 | +0.166 | 79.3 min | 14.3 min | **18 %** |
| `uk` | **0.981** | +0.596 | 83.7 min | 47.7 min | **57 %** |
| `it` | **0.984** | +0.120 | 72.5 min | 9.2 min | **13 %** |

`AC2` is the **highest-R² aggregate of the six in two folds of three**. An R² of 0.98 over five
levels is not indifference — the model orders the levels almost perfectly and then delivers an
eighth to a half of the amplitude. `AC3` agrees: +0.822 / +0.504 / +0.863 at R² 0.90–0.96.

🔴 **The statistic is blind to this.** `ignore_prefix`, which destroys all conditioning by
construction, scores pooled **0.0000**; baseline `it` scores **0.1899**. Two behaviours as different
as "tracks at R² 0.984" and "cannot track at all" are 0.19 apart on the gate's own number.

**Why: budget closure.** The six level-1 aggregates were measured to sum to **1439.2–1439.6 min** of
the 1440-minute day at every level in every fold, so their deviations must sum to ≈ 0. A model that
under-delivers on five aggregates is *forced* to over-deliver on the sixth, and `AC4-8` (leisure) is
that residual bucket — slope **−1.259** (`es`, R² 0.843) and **−1.023** (`uk`, R² 0.732), absorbing
almost one-for-one what the other channels failed to deliver. Pooling averages the attenuated
positives against the forced negative and lands near zero. 🔴 **So a model of uniform gain `g < 1`
does not score pooled ≈ `g`; it scores well below it, by an amount set by which bucket absorbs the
residual. The 0.80 bar is not "80 % of the requested amplitude".**

🟢 **This is the diagnosis that matters for Leg 5:** an amplitude/gain deficit is the kind of thing
a 7 B model at three epochs can plausibly close. A comprehension failure is not. The pilot's number
would have suggested the latter; the per-aggregate view shows the former.

#### 🔴 The perturbation battery on this arm is vacuous, and is recorded as such

All four injections "fell" all three folds, but baseline was already FAILing — the same vacuity as
`G6.6`'s generated arm and `G6.5`'s pilot arm, and again the tell is that `null` moves the verdict.
**`G6.7` has never been seen failing from a passing baseline and cannot be until a model passes it.**

#### 🟢 Cross-gate corroboration, at zero extra compute

`G6.4` independently found the `es`-fold adapter producing `AC2` = 4.0 min against a published 15.0
for `Y25-44`. `G6.7` finds the same adapter unable to move `AC2` past 17 min at any λ. Two gates,
different tables, same channel.

🔴 `D-S6-13` is open on the verdict statistic. Nothing was changed: no checker edited, artefacts as
produced, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` intact.

---

## `D-S6-12` RULED AND APPLIED — the APE floor, 2026-08-22

Ruled **(a) + MAE** on question 1 and **(a)** on question 2. Both applied the same day. Backups
`tools/4thJ_step6_level1.py.bak_ds612`, `tools/4thJ_step6_g66_heldin.py.bak_ds612`.

**What changed.** `gate_g6_4` now picks a cell's basis from the **published side only**, on a
three-rung ladder, and the rung is chosen before the model's value is looked at:

| published value | basis | bar |
|---|---|---|
| `< 0.5` min/day | zero cell, hit/miss (`D-S6-3` item 1 (c), unchanged) | model `< 1.0 %` of the day |
| `< 10.0` min/day | **floor cell, absolute** (new) | abs(model − published) `< 15.0` min/day |
| otherwise | APE, and the MAPE is the mean of these | `MAPE <= 15.0 %`, unchanged |

`PUBLISHED_FLOOR_MIN = 10.0` and `FLOOR_MAE_MAX = 15.0` are pre-registered in
`tools/4thJ_step6_level1.py` and neither was tuned to an observed result. **`MAPE_MAX` did not
move**: the 15 % bar stays binding, unchanged, on every cell of 10 min/day or more. Clause 2's
tolerance stays at **0.0 pp** per question 2 (a) — a strict non-inferiority test, to be described in
the methods as a **directional** guard rather than a calibrated band.

`tools/4thJ_step6_level1_selftest.py` went 47 → **56 green**, and the one assertion that broke was
the right one: *"Y_GE65 scores all six on APE"* is exactly what `FINDING 90` says must stop being
true. Nine new checks cover the floor rung, including that a floor cell moves the verdict **without
moving the MAPE** in both directions.

**Blast radius, measured not assumed.** `grep` over `tools/` confirms `gate_g6_4` has exactly two
callers, `4thJ_step6_g64_run.py` and `4thJ_step6_g66_heldin.py`. `G6.1`, `G6.5`, `G6.9` and the
secondary scorer use `L1.mae`, which is untouched. That matches the decision doc's §3 scope claim.

### 🟢 The calibration arm confirms the defect on the ground truth itself

The real corpus is a perfect model of itself, and it was being charged up to **7.35 pp** for
denominators it cannot be blamed for:

| fold | band | MAPE before | MAPE after | delta pp |
|---|---|---|---|---|
| `es` | `Y45-64` | 3.22 | 1.49 | −1.73 |
| `es` | `Y_GE65` | 4.64 | 2.57 | −2.07 |
| `uk` | `Y45-64` | 4.92 | **4.94** | **+0.03** |
| `uk` | `Y_GE65` | 5.96 | 2.70 | −3.27 |
| `it` | `Y45-64` | 5.98 | 1.33 | −4.65 |
| `it` | `Y_GE65` | 11.50 | 4.15 | −7.35 |

`Y25-44` is unmoved in all three folds — it has no cell below 10 min/day. Corpus board stays **9/9
PASS**, so the gate still clears its own ground truth. 🔴 `uk`/`Y45-64` went **up** by 0.03 pp: a
removed cell was below the band's mean APE, so dropping it raises the mean. Not a defect, and worth
stating because a floor that could only ever lower a number would be a floor worth distrusting.

### 🟢 The generated arm: the same error, now caught in minutes instead of in a percentage

`es`/`Y_GE65`, the fold that produced `FINDING 90`'s headline **363.44 %**, now reads **MAPE
14.65 %** — and still **FAILs**, on this line:

> floor-cell `AC1_TR`: published 5.00 min/day is below the 10.0 min/day APE floor, model 106.10 min,
> absolute error 101.10 min/day exceeds the pre-registered 15.0 min/day tolerance

That is the whole point of the ruling. A 101-minute error on a 5-minute published cell is real and
must fail; **2 029 %** was never the size of it, and under `FINDING 39`'s rounding that percentage
was not identified. The generated board moves **8 FAIL / 1 PASS → 7 FAIL / 2 PASS**.

🔴 **The single band that flipped, `es`/`Y45-64` (20.95 → 12.21 %), was audited cell by cell before
being accepted.** The cell that left the MAPE is `AC2`, published 5.00, model 1.77 — an error of
**3.23 minutes** that was contributing a 64.6 % APE. Removing it is correct. But the band now
PASSes while carrying `AC3` at **+53.05** and `AC0` at **−67.22** min/day (MAE 29.86). That is a
property of a mean-of-percentages bar and not something this ruling introduced — and it is exactly
why item 1 point 3 requires the minutes to be printed beside the percentage. **`G6.4` PASS at
MAPE <= 15 % does not mean small absolute error, and no write-up may imply that it does.**

### 🔴 The cost of the ruling, measured: `wrong_tables` lost two of its three kills

The registered `wrong_tables` injection scores a country's real diaries against **another country's**
published tables. On the corpus arm it felled 3 of 3 donors before and fells **1 of 3** now:

| donor | worst MAPE before | after | bar 15.0 % |
|---|---|---|---|
| `es` | 35.01 % | **25.37 %** | FELL → FELL |
| `uk` | 67.82 % | **11.77 %** | FELL → **held** |
| `it` | 33.41 % | **8.06 %** | FELL → **held** |

⚪ **Provenance of that table.** The `fell` transition 3/3 → 1/3 is in the artefacts on both
sides (`g66_corpus_calibration.json`, `perturbations.wrong_tables.fell`). The six MAPE values are
NOT — the perturbation record stores only which pairs fell. They were obtained by calling
`score_pair(..., "wrong_tables", ...)` twice per donor over the same corpus, once with
`L1.PUBLISHED_FLOOR_MIN` monkeypatched back to 0.5 to reproduce the pre-ruling basis exactly. Stated
here so the numbers are not hunted for in a file that does not contain them.

The reason is structural: what most distinguishes these three countries *in proportion* lives in the
near-zero cells (over-65 `AC2` is 1 vs 2 vs 5 min/day), and in **minutes** those differences are a
few units. The floor removes them from the percentage, so cross-scoring two countries is no longer
visible to a 15 % bar in two of three cases. 🔴 **This is a real loss of discriminating power and it
is not hidden.** The coverage clause still reads **PASS** — every injection still fells at least one
pair and there is no no-op — and `es` still fells with a 10-point margin, so the gate remains
demonstrated. But the trade the ruling makes is sensitivity on small cells in exchange for
identifiability on them, and this table is the price.

### 🔴 `FINDING 93` — `G6.6` clause 2 was 5/6 for the wrong reason. It is 2/6.

The last session recorded clause 2 at **5 of 6 PASS** and flagged that it must never be quoted as a
clean result. It was worse than flagged. Three of those five passes were bought by the denominator
artefact **on the held-out side of the comparison**:

| pair | worst MAPE | held-out ref | delta pp | clause 2 |
|---|---|---|---|---|
| `es`/`it` | 206.19 → 227.43 | 176.87 → 106.70 | +29.32 → **+120.73** | FAIL → FAIL |
| `es`/`uk` | 85.14 → 58.37 | 215.13 → 132.54 | −129.99 → −74.17 | PASS → PASS |
| `it`/`es` | 122.19 → 69.69 | **363.44 → 42.57** | −241.25 → **+27.13** | **PASS → FAIL** |
| `it`/`uk` | 105.64 → 45.30 | 215.13 → 132.54 | −109.48 → −87.23 | PASS → PASS |
| `uk`/`es` | 249.88 → 54.87 | **363.44 → 42.57** | −113.56 → **+12.31** | **PASS → FAIL** |
| `uk`/`it` | 145.96 → 155.15 | 176.87 → 106.70 | −30.91 → **+48.45** | **PASS → FAIL** |

`es`'s held-out reference was **363.44 %** — that number *was* `FINDING 90`, a 1-minute published
cell. Any held-in score at all beat it, so clause 2 passed by default in every pair that referenced
Spain. Under the floor the reference is **42.57 %** and the comparison becomes real.

🔴 **Clause 2 is 2 of 6, not 5 of 6, and the corrected reading is the alarm this gate exists to
raise**: the pilot reproduces a country it *trained on* **worse** than the model that never saw it,
in 4 of 6 pairs. With `--tolerance-pp` ruled to stay at 0.0, nothing softens that. `G6.6`'s
generated board is **6/6 FAIL** on clause 1 either way — expected of a 1.48 B two-epoch pilot — and
its perturbation battery remains **vacuous** (baseline already FAILs; `null` moves the verdict).
The demonstration of record stays the **corpus** arm, still 3/3 PASS, coverage clause PASS.

⚪ The `worst by MAPE` / `worst by MAE` disagreement flag now prints on every pair, and it fires on
exactly the two pairs whose worst-by-MAPE band is still `Y_GE65` (`es`/`it`, `uk`/`it`).

---

## `D-S6-13` RULED AND APPLIED — `AC4-8` out of the fit, steering in, 2026-08-22

Ruled **(c) + (d)**, applied the same day. Backup `tools/4thJ_step6_g67_score.py.bak_ds613`.
Clause 1 is now two parts and a batch must clear both:

1. **STEERING** — on `AC2`, the channel the lambda tilt targets: **R² >= 0.80 and slope > 0**.
2. **AMPLITUDE** — pooled slope **>= 0.80** over the five independent channels `AC0`, `AC1_TR`,
   `AC2`, `AC3`, `AC9A`. `AC4-8` is excluded **by name**, on the stated ground that budget closure
   makes it a dependent quantity; it is still measured and still printed.

`SLOPE_MIN` is unchanged at 0.80 and `STEER_R2_MIN` reuses the same 0.80 rather than inventing a
second project number. The six-aggregate fit is retained in the artefact as
`pooled_slope_all_six` so the correction can be **shown** rather than asserted.

| fold | pooled slope, six | pooled slope, five active | `AC2` R² | steering | amplitude |
|---|---|---|---|---|---|
| `es` | 0.0358 | **0.2666** | 0.8455 | **PASS** | FAIL |
| `uk` | 0.2437 | **0.4612** | 0.9808 | **PASS** | FAIL |
| `it` | 0.1899 | **0.3785** | 0.9836 | **PASS** | FAIL |

🟢 **The correction does what the ruling predicted, and the 7.4x on `es` is the measure of how much
of the old number was closure rather than model.** More importantly the new clause **separates the
two behaviours the old one could not**: baseline steering PASSes in all three folds at R² 0.85–0.98,
while `ignore_prefix` — which destroys all conditioning by construction — returns `AC2` R² **NaN**
(zero variance in the generated series) and slope 0.0, and FAILs steering outright. That is the
discrimination `FINDING 91` said the single pooled statistic lacked, now demonstrated on the
artefact rather than argued.

🔴 **The verdict is unchanged: `G6.7` FAILs in all three folds**, on amplitude and on clause 2 (the
model recites a country at levels 0/1/2 in `es` and `uk`, 0/1 in `it`). The ruling did not rescue
the pilot and was not meant to. What it changes is what the failure *means*: the corrected board
says the model **tracks the conditioning vector and under-delivers its magnitude**, which is a
deficit a 7 B model at three epochs can plausibly close.

🔴 The perturbation battery stays **vacuous** on this arm — baseline already FAILs, so all four
injections "felling" the gate demonstrates nothing, and the coverage clause correctly reads FAIL.
**`G6.7` has still never been seen failing from a passing baseline.**

⚪ One stale cross-reference fixed in passing: `ols()`'s zero-variance message cited "FINDING 90" for
the amplitude guard, a number since assigned to the near-zero-denominator finding. Message text
only; no verdict, threshold or count depends on it.

🔴 All numbers on this page are **LEG-4 PILOT and not reportable**. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` intact; no checker threshold was moved that the author did not
rule; nothing was run on Speed.

---

## `D-S6-14` RULED AND BUILT — the memorisation ceiling, 2026-08-22

Ruled **(a)** on question 1 and **(ii) + (iii)** on question 2, with three directives. The
construction was built and demonstrated the same day; the four training runs are **held**, by the
author's own scheduling directive, until Leg 5 is actually running.

| # | question | ruling |
|---|---|---|
| 1 | what is permuted | **(a)** prefix-to-body pairing, at shard-build time, with a printed seed |
| 2 | which leg, how many folds | **(ii) + (iii)** — one Leg-5 run on the pre-named `it` fold, plus three Leg-4 runs on `es`, `uk`, `it` |
| 3 | thresholds | **unchanged** — `G6.10 <= 0.65`, `G6.11 <= 0.75`; the ceiling is reported beside them, never substituted for them |

Plus: permuted shards marked `POISONED_CONTROL`, kept out of the production shard directory, and
submitted only once job 1286209 is running so the control cannot compete with the critical path for
`AssocGrpGRES`.

### What was built

`4thJ_step4_shards.py --permute-labels [--permutation-seed N]`, seed **614614**. Default mode is
untouched: with no flag the script writes exactly what it wrote before, to exactly where it wrote it.

🔴 **The permutation is within `(country, split)`, not global, and the first reason is not
negotiable.** A global shuffle would put an Italian body behind a Spanish prefix, which in the `it`
fold is the held-out country's data entering training wearing a donor's prefix — and `G4.13` would
still read **0**, because it counts the `country` field. The leak would be invisible to the one gate
built to see leaks. The second reason is that `4thJ_step6_privacy_mia.py` draws members from
`split == "train"` and non-members from `split == "heldout"` of the same countries; permuting only
the member side would let the attack separate the two sets on *pairing style* rather than on
membership and report an inflated AUC that is not memorisation at all. **Both splits are permuted,
independently.**

⚪ **Declared limitation, and it follows directly from that first reason.** `P(body | country)`
survives the permutation. The control de-associates five of the six prefix fields — age band, sex,
household type, economic status, day type — and cannot touch the sixth without destroying the LOCO
design. The ceiling it measures is therefore the ceiling for a model that may still condition on
country. No write-up may call it a fully unconditional control.

🔴 **The permutation is a derangement.** A uniform permutation of `n` items has one fixed point in
expectation *regardless of n*, and a fixed point is a genuine `(prefix, body)` pair surviving inside
a control whose whole claim is that no genuine pair survives. Drawn by rejection — redraw the group
until it has none — which is a uniform derangement exactly, at an expected 2.72 draws.

### The build, job 1286302, and its five measured invariants

| group | n | draws | fixed points | identical-body collisions |
|---|---|---|---|---|
| `es`/heldout | 1,808 | 1 | 0 | 0 |
| `es`/train | 17,332 | 1 | 0 | 0 |
| `it`/heldout | 3,894 | 3 | 0 | 0 |
| `it`/train | 34,366 | 1 | 0 | 0 |
| `uk`/heldout | 1,626 | 4 | 0 | 0 |
| `uk`/train | 14,228 | 2 | 0 | 0 |

1. body character multiset **identical** (42,744,954 characters)
2. prefix multiset **identical** (2,520 distinct prefixes)
3. total body length **identical**
4. prefix country `==` record country for **all 73,254** records — so `G4.13` still counts what it
   thinks it counts
5. records whose full text survived: **0** (0.0000 %)

Fold shards come out with counts **identical to production** — train 48,594 / 51,698 / 31,560, strata
at `N >= 100` of 150 / 151 / 97 — because the prefixes never moved and every stratum is keyed off the
prefix. `G6.12`'s rare-stratum counts and the MIA's stratum keys are therefore unchanged by
construction, which is what makes the ceiling comparable to the run it is a ceiling for.

`corpus_permuted_control.jsonl` md5 `533a07e0417c8c05259c9e5e9ba72c4e`. The production
`shard_manifest.json` and `shards/` still carry their 2026-08-18 10:50 timestamps: **nothing was
written into the production tree.**

### 🟢 The interlock was seen failing, in both directions — job 1286303

The trainer refuses a poisoned shard for a production run-type and a clean shard for the control:

> **A.** `--run-type primary` against the poisoned manifest →
> *"this manifest is marked POISONED_CONTROL (permutation seed 614614) and the run-type is
> 'primary'. A permuted-label shard may only be trained as the control."*
>
> **B.** `--run-type permuted` against the clean manifest →
> *"the memorisation-ceiling control trained on the real corpus is not a ceiling, it is a duplicate
> of the reported run."*

Both refusals cost 45 seconds of CPU, on purpose: they read a json key and exit before a model
loads. The two interlocks inside `4thJ_step6_privacy_mia.py` were hoisted to the same position for
the same reason — a guard that can only fire after a full 7 B scoring pass is a guard nobody ever
sees fail.

### What the ceiling is for

`4thJ_step6_privacy_mia.py` grows `--permuted-adapter` and `--permuted-corpus`. Given both, it scores
the control through **the same functions the baseline went through**, over the permuted corpus at the
same `n` and the same seed, and records `ceiling_G6_10_auc`, `ceiling_G6_11_auc` and the headroom to
the measured values. Without them it prints the named gap exactly as before.

The audit had a **floor** — the untuned base model, AUC ~0.50 — and no top. A measured 0.55 against a
0.65 bar could not be called low, because low compared to what. The permuted adapter has nothing to
generalise by construction, so what it scores is what rote memorisation looks like at this size, on
this corpus, at this schedule.

🔴 **One reading would invalidate the reported run and the artefact says so in words:** if the
reported adapter's AUC is at or above the ceiling, then a model that could *only* memorise did not
leak more than the model that could also generalise. Either the reported run memorised or the control
did not train, and neither permits a release. That clause is written now, before any number exists.

### 🔴 Two things found while building it

**The `it` fold is the SMALLEST training pool, not the largest.** The ruling's rationale gives
31,560 records — the right number — and calls it the largest; it is the smallest of the three
(48,594 / 51,698 / 31,560). The other half of the rationale is right: 97 strata at `N >= 100` is the
**fewest**, i.e. the highest fragmentation. The choice of `it` as the pre-named 7 B anchor is
unaffected and stands; it is recorded here so the descriptor is not quoted from the docket into a
paper.

🔴 **The cluster's `4thJ_step4_train.py` was stale — it predated `D-S4-7`.** The re-point ruled on
2026-08-20 (`G4.7` moved to the generated sample, the corpus reading became `G4.15`) existed only in
the local tree. Job 1286209 is the **reported** Leg-5 fold and would have run without it, producing a
result missing a ruled gate and costing a full re-run to notice. `4thJ_step4_g47_coverage.py`, the
standalone generated-side lever, was **absent from the cluster entirely**. Both were pushed and
verified by md5 while 1286209 was still queued; the old trainer is kept at
`4thJ_step4_train.py.bak_pre_ds47_ds614`. `diagnostics`, `genperturb`, `thresholds`, `perturbtable`
and `stratum_probe` were compared the same way and were already identical.

⚪ Everything else in this section is construction, not result. No adapter has been trained on these
shards yet, so there is no ceiling number to quote — and until there is, `privacy_audit.md` still has
two of three controls.

⚪ **Addendum, same day: the three audit-side guards were seen failing too** (jobs 1286305, 1286311).
`--permuted-adapter` without `--permuted-corpus` is refused — *"the control adapter must be scored on
the corpus it trained on"*; the real corpus passed as the control corpus is refused — *"not marked
POISONED_CONTROL ... a ceiling measured on the real corpus is not a ceiling, it would simply read low
and be believed"*; and a control adapter that has not been trained yet is refused rather than
silently omitted from the artefact. 🔴 The first attempt at this demonstration FAILED TO FAIL: the
`.py` had been pushed to Speed before the interlocks were hoisted, so the clean-corpus run sailed past
the guard and began loading models. Caught, cancelled, re-pushed, re-run. **Five refusals are now on
the record — two in the trainer, three in the audit — and every one of them was watched happening.**

---

### 2026-08-24 — 🔴 **STEP 6.3 IS UNBLOCKED BY STEP 4 AND STILL CANNOT BE SUBMITTED. `--leg 5` DOES NOT SELECT THE LEG-5 MODEL. `FINDING 102`, `D-S6-15`.** 🟢 **THE TWO "UNREAD" STEP 6.5 JOBS ARE READ AND THE RECORD WAS ALREADY RIGHT.**

Step 4 closed the same day (`D-S4-16`, both items `(a)`), so item 6.3 became the critical path and
the launcher was already built and already rehearsed. Nothing has been submitted, and nothing in
this entry changes a threshold: `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched.

#### 🟢 First, the smaller thing: jobs `1286305` and `1286311` are read

The handoff carried them as **unread**, with an explicit warning not to trust `1286311`'s exit code
because it completed in 1 m 21 s and `1286631`-`33` had exited `0:0` in ~48 s having done nothing.
Both `.out` files were fetched and read in full:

* `1286305` — `GUARD-A-REFUSED-GOOD`, then `GUARD-B` **sailed past** and began loading the base
  model (`loading the PUBLIC base model ...`, `Fetching 2 files`) before being cancelled at
  `00:02:52`. This is the *failed to fail* attempt.
* `1286311` — `GUARD-B-REFUSED-GOOD` and `GUARD-C-REFUSED-GOOD`, 6 lines, **no model loaded**. The
  short elapsed is the guards working, not a no-op: a refusal that costs 81 seconds is the design.

⚪ **The §2696 addendum above was already correct in every particular.** Nothing is revised; the
handoff's "unread" flag is retired, having cost one `scp` to clear. 🔴 Checking it was still right:
the cost of reading two files is 81 seconds, and the cost of *assuming* a 1 m 21 s COMPLETED job did
its work is the whole privacy audit.

#### 🔴 `FINDING 102` — `--leg 5` changes the filename and the provenance stamp, not the model

`tools/4thJ_step7_generate.py` resolves both the adapter and the backbone from
`generation_config_<fold>.json` — lines 137, 146, 203 all read `cfg["adapter"]` — and **never from
`--leg`**. The three configs on Speed still read `runs_ds45/leg4_primary_fold_<c>/adapter` and
`allenai/OLMo-2-0425-1B`, frozen by Step 5 and correct for Leg 4.

What `--leg 5` actually does, all three cosmetic or protective: renames the output
`generated_leg5_*` (line 214); **strips** `"provenance": "LEG-4 PILOT -- NOT REPORTABLE"` from every
record and from the summary (142-144, 236-237, 274-275); and enforces `N >= 5200` in the launcher.

🔴 **A `LEG=5` submission today would generate from the 1.48 B Leg-4 adapter, name the file
`generated_leg5_*`, remove the not-reportable stamp, and hand it to every Step 6 and Step 7 gate as
the paper result.** The `N >= 5200` guard would pass — it counts prompts, not parameters. This is
`FINDING 56`'s shape exactly: a default covering for a selector that was never wired, invisible to
every downstream check. It is caught for the same reason it was caught there — the guard was read
before the number was wanted.

⚪ The three Leg-5 adapters exist and are complete at
`4J_step4/runs_leg5/leg5_primary_fold_{es,uk,it}/adapter`.

#### 🔴 And the decision under it: the temperature is a 1 B measurement

`temperature` 1.30 / 1.10 / 1.20 was chosen by **entropy matching**, and each config says so:
`"temperature_basis": "entropy matching"`. `H_real` is the corpus's; the temperature that reproduces
it is the **model's**, and it was measured against `OLMo-2-0425-1B` while Leg 5 is
`Olmo-3-1025-7B` — 4.7× the parameters.

🔴 **There is no ruling to apply because the question was never asked.** Step 5's two documents do
not contain the word "leg" at all, and `D-S7-3` (a) directive 4 says only *"train Leg-5 … and execute
paper campaign"*. Carrying the number forward is a choice; re-measuring it is a choice; neither is
the status quo. Already on the record and weakening the number *on its own model*:
`temperature_curves_agree: false` on all three folds (`es` entropy argmin 1.30 vs fidelity argmin
0.70), 14.8 % of `es` diaries never terminate at `T = 0.70`, and `G5.8` ships FAILING on `es` + `uk`
with fidelity as a band.

⚪ **Not evidence, and recorded so it is not mistaken for evidence:** every Leg-5 generation that
exists — the `G4.7` / `G4.16` sets — ran at a hard-coded `temperature=1.0`
(`4thJ_step4_train.py:811`, `4thJ_step4_diagnostics.py:413`), a diagnostic default. There is no
measurement of the 7 B adapter at 1.30 / 1.10 / 1.20.

#### 🟢 What was checked and is clean — the `D-S4-8` defect has no third copy here

`4thJ_step4_train.py` and `4thJ_step4_diagnostics.py` both carried the missing-`eos_token_id` defect.
The Step 7 generation path does **not**: it is vLLM with `stop=[grammar.EOR]` and
`include_stop_str_in_output=True` (lines 182-183), and vLLM terminates each sequence independently
under continuous batching — it never needs `eos_token_id` to pad a finished row, which is the exact
mechanism that failed in HF `transformers`. 🔴 Worth checking rather than assuming, because Leg 4 ran
on `OLMo-2-0425-1B`, which **does** ship an `eos_token_id`: the defect would have been invisible
throughout the rehearsal and would have appeared for the first time in the paper campaign.

#### The campaign this gates, and one guard aimed at the wrong batches

| purpose | batches | Leg-4 precedent |
|---|---:|---|
| primary per fold, constrained + unconstrained | 6 | `1286195`-`1286200`, N = 600 |
| `G6.6` held-in, one per ordered `(fold, donor)` pair | 6 | `1286254`-`1286259`, N = 600 |
| `G6.7` fictional-country levels, 3 folds × 5 | 15 | `1286260`-`1286274`, N = 600 |

**27 batches.** The launcher's refusal is written `if [ "$LEG" = "5" ] && [ "$N" -lt 5200 ]` —
unconditional on the batch's purpose. Its stated justification is `V7.a`, a **Step 7** vacuity guard,
and `grep -ln "V7\.a" tools/4thJ_step6_{g66_heldin,g67_score,level1}.py` returns nothing. As written
it would force the 21 auxiliary batches to 8.7× their rehearsal size for a reason that does not
apply to them, and would move `G6.6`/`G6.7` off the single basis their own comparisons rest on.

#### `D-S6-15` — three items, for the author

`IMP/docs/2026-08-24_D-S6-15_the_leg5_generation_config.md`.

1. **The selector.** (a) recommended — `--leg 5` resolves `runs_leg5/…` + `Olmo-3-1025-7B` additively
   and **refuses** rather than falling back; the Leg-4 path stays byte-identical so nothing scored
   from the rehearsal is disturbed. (b) separate `_leg5.json` configs. (c) rejected — by hand, 27
   times, which is the failure mode itself.
2. **The temperature.** (a) carry 1.30/1.10/1.20 forward and declare the transfer; (b) re-run the
   Step 5 entropy sweep on the Leg-5 adapters — defensible, but re-opens a CLOSED step and costs a
   7 B sweep before the campaign; (c) generate at `T = 1.0`, the only setting the 7 B adapter has
   been observed at, and declare the departure. 🔴 Under every option the basis must reach the
   methods: each config asserts *"nothing here is a fresh choice"*, and that is true only of Leg 4.
3. **The `N >= 5200` refusal.** (a) recommended — narrow it to the primary batches. (b) apply it to
   all 27.

#### 🔴 Unchanged, and not touched by any option above

Step 6.5's **third registered control — the random-label-permutation adapter — is still not
trained.** `4J_step4/runs/leg4_permuted_fold_it/` exists and is **empty**. `privacy_audit.md` cannot
be written and no release decision can be made, on either leg. Four of five Step 6.5 gates exist and
pass; what is missing is a control, not a gate.

---

### 2026-08-24 (evening) — 🟢 **`D-S6-15` RULED ALL THREE ITEMS `(a)`, APPLIED, AND THE SELECTOR WAS SEEN WORKING BEFORE A SINGLE DIARY WAS GENERATED (job `1286834`, 6/6, the control fired). 🟢 STEP 6.3 IS RUNNING: ALL TWENTY-SEVEN LEG-5 BATCHES ARE ON THE QUEUE, `1286835`–`1286861`, AND THEY ARE THE FIRST GENERATION THIS PROJECT HAS EVER RUN ON THE 7 B MODEL.**

The author ruled the day the decision was written. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` untouched, no threshold moved, and the frozen Step 5 configs were
**not edited** — the leg overrides three fields in memory and prints the Leg-4 values it displaced.

#### What was applied

| item | ruling | file | change |
|---|---|---|---|
| 1 | `(a)` | `tools/4thJ_step7_generate.py` | `resolve_leg()` — leg 5 resolves `runs_leg5/leg5_primary_fold_<fold>/adapter` + `Olmo-3-1025-7B` @ `a81bae42…`, hard `SystemExit(3)` if absent, **never a fallback**; `--leg` now `choices=(4, 5)` |
| 2 | `(a)` | same | temperatures 1.30 / 1.10 / 1.20 **carried unchanged**; `TEMPERATURE_PROVENANCE_LEG5` written into every leg-5 record **and** summary |
| 3 | `(a)` | `tools/4thJ_step7_generate.sh` | `N >= 5200` narrowed to the six PRIMARY batches; the 21 auxiliaries stay at `N = 600` |

Backups verified non-empty and **byte-identical to what was staged on Speed** before the push:
`.py` `2ea98c3690fba099caf42cbe11483b92` → `9840897345905bcf7e808ee484965530`;
`.sh` `4bafdb2cd839c15d76e1919bd3547945` → `adbd34ebefa38eb94444d7853078976a`.

#### 🟢 The fix-check — `1286834`, 46 s, CPU only, **6 / 6 PASS**, and check 0 is a CONTROL

🔴 `FINDING 56` is why this job exists: Leg 4's `600/600` was a model-repo default covering for a
broken harness, so a guard that has not been seen refusing is not a guard. The control ran **first**
and the run was declared VOID if it did not fire.

| # | check | result |
|---|---|---|
| 1 | `py_compile` the patched generator | PASS |
| **0** | **CONTROL — the leg-5 adapter root pointed at a missing directory** | **PASS — `SystemExit` 3, "Nothing was generated."** |
| 2 | `--leg 4` returns the config **identical** (`==`): still `runs_ds45` + `OLMo-2-0425-1B` | PASS |
| 3 | `--leg 5` resolves the leg-5 adapter + `Olmo-3-1025-7B` @ `a81bae42` | PASS |
| 4 | temperature, `top_p`, `top_k`, seed unchanged; provenance string present | PASS |
| 5 | three leg-5 adapters on disk, `adapter_config.json` readable, `r = 32` each | PASS |

The refusal exits **3**, deliberately not `NotRun`'s **2**: `2` is a legitimate "NOT RUN" the launcher
reports, and a missing Leg-5 adapter must never be readable as an ordinary outcome.

Item 3's classifier was tested against **the file's own bytes** — the guard block extracted with
`sed` and evaluated, not reimplemented: `LEG=5 es 600` REFUSED exit 1; `LEG=5 es 5200` allowed;
`g66it` and `g67_es_t00` both classified auxiliary and allowed at 600; `LEG=4 es 600` untouched.
`IS_PRIMARY` is **derived** from the invocation (own prefixes **and** no tag), never hand-labelled,
so a typo in a submission line cannot promote an auxiliary batch into a primary one.

#### 🟢 The campaign — 27 batches, `1286835`–`1286861`

| batches | jobs | N |
|---|---|---:|
| primary, 3 folds × {constrained, `--no-grammar`} | `1286835`–`1286840` | 5,200 |
| `G6.6` held-in, six ordered `(fold, donor)` pairs | `1286841`–`1286846` | 600 |
| `G6.7` fictional-country levels, 3 folds × 5 | `1286847`–`1286861` | 600 |

`1286835` (`es`, constrained) was submitted **alone and read before the other 26 went out** — the
selector is proved by a fix-check, but that the 7 B model actually loads on the rehearsal's
`2g.20gb` slice is a separate claim. Its header reads
`base : allenai/Olmo-3-1025-7B @ a81bae42…` and
`adapter : …/runs_leg5/leg5_primary_fold_es/adapter`, engine up in **39.6 s**, LoRA rank 32,
`5200 drawn from a pool of 100000`, EBNF 114,806 chars / ACT 159.

⚪ **The KV cache is the tight resource and it is worth recording**: `GPU KV cache size: 5,901
tokens` on the 20 GB slice, against `max_new_tokens = 1200`. It nevertheless sustains **3.4
diaries/s, 932 output tok/s**, so a 5,200-diary primary batch is ~25 minutes of generation, not the
hours a naive read of that cache size suggests. Four jobs run at once (`AssocGrpGRES`, my own
concurrent-GPU ceiling); the remaining 23 are `PD` behind them.

#### 🔴 What this does NOT settle

* The temperature is **transferred, not measured**. `H_real` is a property of the corpus; the
  temperature that reproduces it is a property of the **model**, and 1.30 / 1.10 / 1.20 were fitted
  on a 1.48 B backbone. Under `D-S6-15` item 2 `(a)` this is carried **and declared** — in the
  methods, and in every generated record via `temperature_provenance`. It is not a re-measurement and
  must never be written up as one.
* **Nothing is scored yet.** These are batches, not gates. `D-S6-2` still binds Step 6.4: `it` is
  scored against 2008-09 with the gap declared, and that must be settled **before** the `it` fold is
  scored.
* Step 6.5's **third registered control — the random-label-permutation adapter — is still not
  trained**, `4J_step4/runs/leg4_permuted_fold_it/` is empty, and no release decision can be made on
  either leg until it is.

### 2026-08-24 (night) — 🟢 **STEP 6.3 IS CLOSED: ALL 27 LEG-5 BATCHES `COMPLETED` EXIT `0:0`. 🔴 STEP 6.4 IS SCORED AND THE PRE-REGISTERED TRANSFER CLAIM FAILS — `G6.1` FAILS 9 OF 9, AND SCALING THE BACKBONE 4.7x BOUGHT NOTHING: MEAN MODEL MAE `42.05` -> `43.14`.**

#### Step 6.3 — the campaign, read out of the job logs

Jobs `1286835`-`1286861`, all `COMPLETED`, exit `0:0`. Every batch header carries
`base : allenai/Olmo-3-1025-7B @ a81bae42db3975be1671e27b9c9a56da1a9f980f` and
`adapter : …/runs_leg5/leg5_primary_fold_<c>/adapter` — `FINDING 102` is repaired in the artefact
itself, not only in the script. 27 of 27 output files on disk and fetched to
`Step7_docs/outputs_step7/`.

| batches | jobs | N | oracle-valid | terminated |
|---|---|---:|---|---|
| primary, constrained, 3 folds | `1286835`/`1286837`/`1286839` | 5,200 | **5200/5200 each** | 5200/5200 |
| primary, `--no-grammar`, 3 folds | `1286836`/`1286838`/`1286840` | 5,200 | es `358` (6.88 %), uk `1610` (30.96 %), it `554` (10.65 %) | uk+it 5200/5200, **es 5190/5200** |
| `G6.6` held-in, 6 ordered pairs | `1286841`-`1286846` | 600 | 600/600 each | 600/600 |
| `G6.7` fictional-country, 15 levels | `1286847`-`1286861` | 600 | 600/600 each | 600/600 |

⚪ **The grammar is load-bearing and the free-arm spread is country-correlated.** Unconstrained
validity runs 6.88 % / 30.96 % / 10.65 % — `uk` is `4.5x` `es`. That is a LOCO-relevant pattern, not
a nuisance, and it is recorded before anyone reads a fidelity number from a constrained batch.
⚪ `es --no-grammar` is the only batch in the campaign that did not terminate everywhere: **10 of
5,200 diaries carry no `<eor>`**. Post-`D-S4-8` that is exactly the count `G4.16` exists to see.

#### Step 6.4 — the board, Leg 5

All scored locally from the fetched batches, `--leg 5`, `--wave 2010`. 🔴 **`D-S6-2` is honoured and
restated here rather than assumed: `it` is scored against the Eurostat `2010` column, which is the
**2008-09** survey, while the Italian microdata is ISTAT 2013-14. The gap is declared, the
asymmetry with `es`/`uk` is real, and no `it` number below may be quoted without it.**

| gate | what it asks | Leg-5 verdict | artefact |
|---|---|---|---|
| **`G6.1`** | model MAE **<** raked-donor null, per band | 🔴 **FAIL 9 / 9** | `g61_leg5_scored.json` |
| `G6.4` | level-1 budget vs published, MAPE ≤ 15 % | 🔴 **FAIL 9 / 9** exact bands | `g64_leg5_generated.json` |
| `G6.5` | AND over three frozen FAIL criteria | 🔴 **FAIL 9 / 9** | `g65_g69_leg5.json` |
| `G6.9` | nearest published profile is the held-out country | 🔴 **FAIL 9 / 9** | `g65_g69_leg5.json` |
| `G6.6` | held-in donor prefixes clear `G6.4`'s bar | 🔴 **FAIL 6 / 6** | `g66_leg5_generated.json` |
| `G6.7` | follows a fictional conditioning vector, slope ≥ 0.80 | 🔴 **FAIL 3 / 3** | `g67_leg5_{es,uk,it}.json` |
| `G6.2` / `G6.3` | secondary nulls, **reported not thresholded** | all margins negative | `g62_g63_leg5_scored.json` |
| `G6.13` | distance to closest record | ⚪ **PASS 2 / FAIL 1** — `uk` fails the size-matched arm | `g613_leg5_dcr.json` |

#### 🔴 The headline. `G6.1` is the pre-registered bar and it is not close.

`prereg.md` §5: *"If a fine-tuned LLM cannot beat a demographically raked pool of real European
donors on the held-out country, the transfer claim fails. There is no weaker reading of that
sentence."*

| fold | band | model MAE | null MAE | margin |
|---|---|---:|---:|---:|
| `es` | Y25-44 / Y45-64 / Y_GE65 | 36.81 / 34.52 / 44.32 | 9.94 / 8.82 / 11.81 | **−26.9 / −25.7 / −32.5** |
| `uk` | Y25-44 / Y45-64 / Y_GE65 | 58.91 / 60.44 / 21.24 | 21.79 / 19.21 / 18.54 | **−37.1 / −41.2 / −2.7** |
| `it` | Y25-44 / Y45-64 / Y_GE65 | 62.24 / 33.95 / 35.84 | 19.51 / 13.85 / 15.51 | **−42.7 / −20.1 / −20.3** |

The closest the model ever comes is `uk Y_GE65` at **−2.70 MAE**, and it is still behind. 🔴 **This is
not a threshold that could be argued about. A raked pool of real diaries from the other two
countries reproduces the held-out country's time budget between two and six times better than the
fine-tuned model does, on every band of every fold.**

#### 🔴 4.7x the parameters bought nothing on the headline gate

Same nulls, same bands, same scorer — only the backbone changed (`OLMo-2-0425-1B`, 1.48 B ->
`Olmo-3-1025-7B`, 7 B):

| fold / band | Leg-4 model MAE | Leg-5 model MAE | |
|---|---:|---:|---|
| `es` Y25-44 | 69.50 | **36.81** | better |
| `es` Y45-64 | 29.86 | 34.52 | worse |
| `es` Y_GE65 | 42.13 | 44.32 | worse |
| `uk` Y25-44 | 24.04 | 58.91 | **much worse** |
| `uk` Y45-64 | 22.93 | 60.44 | **much worse** |
| `uk` Y_GE65 | 36.37 | **21.24** | better |
| `it` Y25-44 | 77.75 | **62.24** | better |
| `it` Y45-64 | 54.68 | **33.95** | better |
| `it` Y_GE65 | 21.21 | 35.84 | worse |
| **mean** | **42.05** | **43.14** | **4 cells better, 5 worse** |

`G6.4` tells the same story from the other side: Leg 4 scored **1 PASS / 8 FAIL** over the exact age
bands; Leg 5 scores **0 PASS / 9 FAIL**. The one Leg-4 PASS (`uk` Y45-64, MAPE 9.69 %) went to
36.57 % at 7 B.

🔴 **What this does and does not license.** It licenses: *within this design, at this corpus size,
scaling the backbone from 1.48 B to 7 B does not improve cross-country transfer of time-use
structure, and the per-cell movement is not even consistent in sign.* It does **not** license any
claim about scaling in general — two points is not a curve, one LoRA configuration is not a training
regime, and `D-S4-11` is open on whether `G4.1` was even read on its registered basis.

#### ⚪ `G6.7` is the one place the model demonstrably responds

`G6.7` FAILs, but not by being inert. The distance to the fictional conditioning vector falls
monotonically as the vector is pushed:

| fold | level 0 | 1 | 2 | 3 | 4 | slope (need ≥ 0.80) |
|---|---:|---:|---:|---:|---:|---:|
| `es` | 60.71 | 59.15 | 49.04 | 34.19 | **16.64** | 0.4153 |
| `uk` | 35.76 | 34.06 | 24.38 | 18.77 | **15.39** | 0.5329 |
| `it` | 36.49 | 28.55 | 15.89 | **12.42** | 19.02 | 0.4049 |

The model **does** move with the prefix — at roughly **half** the demanded amplitude — and at the low
levels a real country's published profile still explains the output better than the vector does
(`es` at levels 0/1/2, `uk` at 0/1/2/3, `it` at 0/1/4). Read with `G4.3`'s base-model baseline from
the same day (§10.1 of the Step-4 investigation: untrained `0.0001`-`0.0011` vs fine-tuned
`0.068`-`0.106`), the two agree: **conditioning is real and under-powered**, on both the CE metric
and the behavioural one.

#### 🔴 Coverage: the Leg-5 perturbations felled nothing, and the reason matters

`G6.5` / `G6.9`: all four levers (`null`, `shift25`, `invert_sign`, `neighbour_tables`) fell in **0**
cells and the coverage clause reads FAIL. 🔴 **That is not a new defect and it must not be reported
as one: every cell is already FAIL at baseline, and a gate that is already down cannot be seen
falling.** The seen-falling credit for `G6.5`/`G6.9` comes from the **Leg-4** run and from the corpus
calibration arm, where the baseline passes. The same reading applies to `G6.6`, whose four runnable
levers all felled all six pairs — and whose fifth, `sequential_countries`, remains a **NAMED GAP**
that needs its own training run.

#### What Step 6.4 does NOT settle

* ⚪ **`G6.13` finished after the table was drafted and is now in it: PASS `es`, PASS `it`, FAIL `uk`.** Zero exact matches and zero `NNDR < 0.33` on all three folds, so the crude memorisation arms are clean. `uk` fails the **size-matched** arm: median DCR to TEST `0.4236` lies **above** the 95 % interval of the median DCR to a same-size train subsample, `[0.4028, 0.4167]` over 200 draws — the model sits closer to what it was trained on than to unseen diaries of the same distribution. 🔴 The RAW train-vs-test comparison is **not** the verdict on any fold (pool ratios `8.8x`-`9.2x`) and must not be quoted as one; the checker says so itself.
* **`G6.8`'s model arm has never been run on either leg.** Only the `it` controls exist
  (`g68_it_splithalf.json`, `g68_it_shuffled_across.json`). Scoring the generated set against the
  real held-out country needs a country-filtered reference file that does not exist; recorded as
  owed, not improvised.
* 🔴 **Step 6.5's third registered control — the random-label-permutation adapter — is still NOT
  TRAINED.** `4J_step4/runs/leg4_permuted_fold_it/` is empty, `privacy_audit.md` cannot be written,
  and **no release decision can be made on either leg.**
* The `UK-fold split report` owed by `D-S3-14` (551 UK diaries at `strat_hh_type = unknown`) is
  still owed.
* 🔴 `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` — **untouched**. No threshold moved, no
  checker edited, no band re-argued. Every FAIL above is reported as the result.

---

## 2026-08-24 (evening) — STEP 6.5: THE THIRD REGISTERED CONTROL IS TRAINING, AND ITS INTERLOCK HAS BEEN SEEN REFUSING

`D-S6-14` was ruled on 2026-08-22 — **(a)** permute the prefix-to-body pairing at shard-build time,
**(ii)+(iii)** one Leg-5 run on the pre-named `it` fold plus three Leg-4 runs — and the tooling was
built the same day. It then sat unsubmitted, because the ruling's own §6 directive said to hold every
permuted job until the reported model's training was off the queue. That condition is now met: the
queue is empty of reported work, all 27 Step 6.3 batches having finished.

### Submitted 2026-08-24

| job | leg | fold | backbone | what it is |
|---|---|---|---|---|
| `1286896` | 5 | `it` | `Olmo-3-1025-7B` | 🔴 the **governing** memorisation ceiling, fold pre-named ex ante |
| `1286897` | 4 | `es` | `OLMo-2-0425-1B` | cross-fold spread at pilot scale |
| `1286898` | 4 | `uk` | `OLMo-2-0425-1B` | cross-fold spread at pilot scale |
| `1286899` | 4 | `it` | `OLMo-2-0425-1B` | cross-fold spread at pilot scale, the Leg-4/Leg-5 hinge |

The three Leg-4 runs started immediately on `speed-43`/`speed-39`. `1286896` is `PENDING (Resources)`
for the full `nvidia_a100_7g.80gb` instance with an estimated start of **2026-08-25T07:35**.

The shards were **not** rebuilt for this — they were deranged on 2026-08-22 and were sitting ready:
`shards_permuted_control/`, manifest `shard_manifest_permuted_control.json`, **permutation seed
`614614`**, **73,254 records re-paired, 0 fixed points** (a strict derangement — no record keeps its
own body), every record marked `POISONED_CONTROL`. Each run reprints all of it in its own log, so the
seed is in the artefact and not only in the builder.

### 🔴 The interlock, seen refusing in both directions — job `1286901`

The four control jobs show the `POISONED_CONTROL` interlock **accepting**. That is not evidence that
it works. `FINDING 56` is this project's own case of a guard that passed for the wrong reason — a
600/600 that turned out to be a model-repo default covering for a broken harness — and the standing
rule is that a guard not seen refusing is not a guard. So both refusals were put to it directly, on a
**CPU-only** job so as not to take a GPU from the Leg-5 control already queued behind `Resources`:

| arm | command | expected | observed |
|---|---|---|---|
| 1 | `--run-type primary` on the **poisoned** manifest | refuse | 🟢 `FAIL: this manifest is marked POISONED_CONTROL (permutation seed 614614) and the run-type is 'primary'` — exit 1 |
| 2 | `--run-type permuted` on the **clean** manifest | refuse | 🟢 `FAIL: --run-type permuted was given but the manifest … is NOT marked POISONED_CONTROL` — exit 1 |

Both arms died before any weight was loaded, and `G4.14` printed PASS in both — the prereg md5 is
checked before the interlock, so a refusal is not a way to skip it.

⚪ **An observation the probe's own guard caught, and it retires a line this document has been
carrying.** The probe asserted that no run directory should exist afterwards, and one did:
`--out/<run_name>/` is created *before* the manifest is read, so a refused run still leaves an empty
directory behind. That is exactly what `4J_step4/runs/leg4_permuted_fold_it/` is — empty, timestamped
`2026-08-22 15:13`, the same minute the shards were built. This document and the board have both been
citing that empty directory as evidence the control was never trained. The conclusion was right and
the reasoning was wrong: **an empty run directory is the residue of a refusal, not of a half-finished
run**, and it would look identical either way. The probe's two directories were removed; the Aug-22
one is left where it is, as the record.

### What this does not yet settle

* **Nothing is scored.** The adapters do not exist yet. `privacy_audit.md` stays unwritten and **no
  release decision can be made on either leg.**
* The scoring path is already wired and needs no new code: `4thJ_step6_privacy_mia.sh <fold> <leg>
  <n> control` passes `--permuted-adapter` and `--permuted-corpus` together, and the module refuses
  one without the other — the control must be scored on the corpus it trained on, or it measures a
  model reading text it never saw.
* 🔴 **The Leg-5 audit will not fit `4thJ_step6_privacy_mia.sh` as written.** Its GRES is a
  `2g.20gb` slice, and a Leg-5 control run loads *two* 7 B bases (the reported one and a fresh one
  for the control). The script says so in its own comments. That submission is owed.
* 🔴 The bars do not move. `G6.10` ≤ 0.65 and `G6.11` ≤ 0.75 are pre-registered, and the ceiling is
  read **beside** the measured AUCs, never substituted for the bar. `prereg.md` md5
  `e4243e07cdd80c9c846b91f40e3e8c45`, verified live inside every one of these jobs by `G4.14`.

---

## 2026-08-24 (night) — 🔴 THE FIRST MEMORISATION CEILING IS SCORED AND IT ALARMED. THE MEASUREMENT SAYS THE CEILING IS NOT A CEILING. `FINDING 112`, `FINDING 113`, `D-S6-16`.

Job `1286941`, fold `it`, Leg 4, `4thJ_step6_privacy_mia.sh it 4 2000 control` — **COMPLETED
`0:0` in 00:39:48**. It is the first `D-S6-14` control this project has ever scored. Artefacts
fetched: `outputs_step6/privacy_mia_leg4_it.json` (4,922 B, against 3,227/3,228 B for the
control-less `es`/`uk` audits of 2026-08-22) and `outputs_step6/4J_step6_mia_1286941.out`.

### What was measured

| | reported adapter | ceiling (permuted) | headroom | pre-registered bar |
|---|---|---|---|---|
| `G6.10` loss MIA AUC | **0.5539** | **0.5488** | **−0.0051** | ≤ 0.65 — **PASS** |
| `G6.11` reference MIA AUC | **0.5274** | **0.5147** | **−0.0127** | ≤ 0.75 — **PASS** |
| perplexity gap | 0.0182 | 0.0168 | −0.0014 | ≤ 0.05 — **PASS** |
| `G6.12` verbatim | 0 greedy / 0 sampled of 103 rare records | — | — | **PASS** |
| untuned-base floor | 0.4874 | — | — | ≈ 0.50, as expected |

The perturbation battery ran and the **coverage clause is PASS**: `G6_10` fell to `g610_memorise`
(AUC 0.9997), `g610_tail` and `pplgap_widen`; `G6_11` to `g610_memorise` (0.8706) and
`g611_reference` (0.9867); `G6_12` to `g612_verbatim` (exact 1). Every gate has been seen falling.

🔴 **The module printed the alarm it was built to print**, on both attacks:

> A model that could only memorise did not leak more than the reported one. Either the reported run
> memorised, or the control did not train. Neither reading permits a release.

### 🔴 `FINDING 112` — the control DID train, and it reached the SAME loss as the reported model. That is exactly what makes it not a ceiling.

The alarm offered two readings. Three independent measurements support a **third** one it did not
offer.

**(i) Training loss.** Mean of the last 20 logged steps of epoch 2, read from the job logs:

| run | job | start | last-20 mean | sd |
|---|---|---|---|---|
| reported `it` | `1281612` | 1.7323 | **0.5565** | 0.0386 |
| permuted `it` | `1286899` | 1.7134 | **0.5536** | 0.0733 |

🔴 **The model whose prefix-to-body pairing was destroyed ended 0.0029 *below* the
correctly-paired one.** It trained (1.71 → 0.55) and it trained to the same place.

**(ii) Perplexity, measured inside the audit itself on held-in text.** Reported model train
`1.7189`; ceiling model train `1.7353`. **0.95 % apart.**

**(iii) The conditioning gates on the permuted adapters.** `G4.3` / `G4.4` / `G4.12` **all FAIL** on
both permuted runs read so far — `1286899` (`it`, `G4.12` CE rise 0.0023 against a required 0.15,
MI drop −0.070 against 0.10) and `1286898` (`uk`, `G4.4` evening ratio 0.305 / morning 0.134, both
FAIL). The permutation did precisely what it was built to do: it destroyed conditioning on age, sex,
household type, economic status and day type.

Put (iii) beside (i) and (ii): **conditioning on the prefix contributes almost nothing to the
training loss.** A model that has lost it entirely reaches the same likelihood as one that has it.

The consequence for `D-S6-14` is structural, not arithmetic. The ruling's premise was that destroying
the pairing leaves nothing generalisable to learn, so the control is *forced* to memorise. **That
premise is false for this corpus.** The permutation shuffles which prefix sits in front of which
body; the builder itself asserts the body multiset is unchanged. Every body in the permuted corpus is
still a real, well-formed diary, so the control has a large generalisable thing left to learn —
**the diary language** — and it learns that instead of memorising. Its MIA AUC is near chance
because it never needed to memorise, **not** because memorisation is impossible at this capacity.

🔴 **A control that is not forced to memorise does not bound memorisation. `0.5488` is not a
ceiling; it is another model's near-chance MIA score.**

⚪ Same class as `FINDING 56` — a guard returning a number for a reason other than the one it was
built to test — and caught the same way, by measuring rather than re-reading the design.

### 🔴 `FINDING 113` — the comparison has no tolerance, and this alarm fires on noise

`D-S6-14` pre-registered the direction of the comparison and no margin. The module implements a
strict test, so any negative headroom alarms. At `n = 2000` per class the Hanley–McNeil standard
error of one AUC near 0.55 is **0.0091**:

| | observed gap | SE of the difference | z |
|---|---|---|---|
| `G6.10` | 0.0051 | 0.0128 | **0.40** |
| `G6.11` | 0.0127 | 0.0129 | **0.99** |

🔴 **Neither difference is distinguishable from zero.** Even if `FINDING 112` were wrong and
the control were a valid ceiling, this alarm would not be evidence that the reported model leaks
more — it would be two tied numbers ordered by noise. `FINDING 86` already forced size-matching on
this attack for a related reason; the tolerance was never added.

### `D-S6-16` — for the author

**What does an alarmed `D-S6-14` control mean for the release decision?** Four options, brief at
`IMP/docs/2026-08-24_D-S6-16_the-ceiling-alarmed-and-may-not-be-a-ceiling.md`.

🟢 **Recommendation (a):** read the alarm as informative about the **control**, not about the
reported model; report the ceiling as **INCONCLUSIVE AS A CEILING** with the three measurements
printed beside it; rest the release on the four controls that pass — the two pre-registered bars,
the untuned-base floor, the perplexity gap and `G6.12`. It changes no threshold, discards no control
and repairs no number after the fact. ⚪ If (a), the same reading must apply to `uk`, `es` and the
governing Leg-5 `it` control **whatever they return**, and that has to be said now, before they are
read, or (a) becomes a rule invented per result.

⚪ (b) adds the missing tolerance but sets it after seeing the number it would decide — admissible
only as a pre-registration for future folds, never as a repair of this one. (c) builds a control that
really is forced to memorise (randomise the **bodies**, not the pairing) and costs a full retrain per
fold, on Leg 5 the 7 B model. (d) refuses the release on the strength of an instrument whose premise
has just been shown false, at 0.4 sigma.

### Queue, as of 23:05

| job | leg | fold | state |
|---|---|---|---|
| `1286899` | 4 | `it` permuted | 🟢 COMPLETED 03:33:29 — audit `1286941` 🟢 COMPLETED, read above |
| `1286898` | 4 | `uk` permuted | 🟢 COMPLETED 04:46:37, `0:0` — audit submitted as **`1286945`** |
| `1286897` | 4 | `es` permuted | RUNNING 04:47 — audit follows the same way |
| `1286896` | 5 | `it` permuted | RUNNING 03:39 — 🔴 the **governing** control; its audit still needs a separate submission at `--gres=gpu:nvidia_a100_7g.80gb:1` and `--mem=192G` |

🔴 **The bars did not move.** `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified live
by `G4.14` inside every job above. Nothing in this entry asks for a threshold to change.

🔴 **`privacy_audit.md` is still unwritten and no release decision has been made on either
leg.** It waits on `D-S6-16` and on the Leg-5 control.

---

## 2026-08-24 (night, later) — 🔴 THE SECOND CEILING LANDED AND IT DID **NOT** ALARM. THE TWO CEILINGS ARE 0.0004 APART. `FINDING 114`.

Job `1286945`, fold `uk`, Leg 4 — **COMPLETED**. Artefacts fetched:
`outputs_step6/privacy_mia_leg4_uk.json`, `outputs_step6/4J_step6_mia_1286945.out`.

| | reported adapter | ceiling (permuted) | headroom | bar |
|---|---|---|---|---|
| `G6.10` | 0.5336 | 0.5484 | **+0.0148** | ≤ 0.65 — PASS |
| `G6.11` | 0.5074 | 0.5116 | **+0.0041** | ≤ 0.75 — PASS |
| perplexity gap | 0.0097 | 0.0132 | +0.0035 | ≤ 0.05 — PASS |
| `G6.12` | 0 greedy / 0 sampled of 40 rare records | — | — | PASS |
| untuned-base floor | 0.5012 | — | — | ≈ 0.50 |

> `no alarm: the reported adapter sits below the memorisation ceiling on both attacks.`

Taken alone this reads as the control working. Put beside `it` it is the clearest evidence yet that
it is not.

### 🔴 `FINDING 114` — the ceiling does not move between folds. It is a constant, and it silently imposes a bar tighter than the registered one.

| fold | reported AUC `G6.10` | ceiling AUC `G6.10` | headroom | alarm? |
|---|---|---|---|---|
| `it` | **0.5539** | **0.5488** | −0.0051 | 🔴 YES |
| `uk` | **0.5336** | **0.5484** | +0.0148 | no |

🔴 **The two ceilings are 0.0004 apart.** Two independently trained adapters, two different
folds, two different training corpora, two different held-out countries — and the quantity that is
supposed to measure *how much this model could memorise if it had to* comes out at 0.5484 and 0.5488.
The Hanley–McNeil SE of either is **0.0091**, so the spread is **1/23 of one standard error**. The
reported AUCs, over the same two folds, are **0.0203** apart.

A ceiling that is constant to four decimal places while the thing it is supposed to bound varies by
fifty times as much is not measuring memorisation capacity. It is measuring a fixed property of the
setup — exactly what `FINDING 112` predicts, since the permuted model learns the diary language and
never memorises, and the diary language is the same in every fold.

🔴 **The consequence is that `D-S6-14` has been acting as an unregistered bar at ≈ 0.548.**
`it` alarmed and `uk` did not, and neither ceiling moved — the *reported* AUC moved. So in practice
the control replaces the pre-registered `G6.10 ≤ 0.65` with a hidden `≤ 0.5484`, an 82 % tighter
threshold, set by an artefact, discovered after the fact and never registered. That is a stronger
reason to rule `D-S6-16` (a) than the `it` alarm on its own.

### `FINDING 112` reproduces on `uk`

| run | job | last-20 mean loss | sd |
|---|---|---|---|
| reported `uk` | `1274964` | 0.5005 | 0.0779 |
| permuted `uk` | `1286898` | 0.5195 | 0.0543 |

Permuted is **0.0190** higher, against an SE of the difference of about **0.021** — under one sigma,
the same verdict as `it` (where the permuted run came out 0.0029 *lower*). Held-in perplexity:
reported `1.6572`, ceiling `1.6701` — **0.78 % apart**, against `it`'s 0.95 %. **Destroying the
prefix-to-body pairing costs the training loss nothing on either fold.**

### Queue

| job | leg | fold | state |
|---|---|---|---|
| `1286941` | 4 | `it` audit | 🟢 COMPLETED — 🔴 ALARMED |
| `1286945` | 4 | `uk` audit | 🟢 COMPLETED — no alarm |
| `1286897` | 4 | `es` permuted | 🟢 COMPLETED — audit submitted as **`1286955`** |
| `1286896` | 5 | `it` permuted | RUNNING — 🔴 the **governing** control; its audit still needs a separate submission at `--gres=gpu:nvidia_a100_7g.80gb:1` and `--mem=192G` |

⚪ `D-S6-16` recommendation (a) required that its reading be declared to apply to `uk`, `es` and the
Leg-5 control **before they were read**. `uk` was read before the ruling came back, so that
undertaking is now partly spent: the recommendation was on the record, in writing, before `1286945`
was opened, and this entry records that `uk` did **not** alarm — which is the direction that would
have made it convenient to drop the recommendation. It stands unchanged.

🔴 **The bars did not move.** `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`. All four
registered controls pass on both folds read so far. `privacy_audit.md` remains unwritten and **no
release decision has been made on either leg.**

---

## 2026-08-25 (early) — 🔴 ALL THREE LEG-4 CEILINGS ARE IN. TWO OF THREE ALARM, AND THE THREE CEILINGS HAVE A STANDARD DEVIATION OF **0.00117**. `FINDING 114` CONFIRMED.

Job `1286955`, fold `es`, Leg 4 — **COMPLETED**, and it **ALARMED**, by the smallest margin yet.
Artefacts fetched: `outputs_step6/privacy_mia_leg4_es.json`,
`outputs_step6/4J_step6_mia_1286955.out`.

| `es` | reported | ceiling | headroom | bar |
|---|---|---|---|---|
| `G6.10` | 0.5481 | 0.5466 | **−0.0015** | ≤ 0.65 — PASS |
| `G6.11` | 0.5204 | 0.5183 | **−0.0021** | ≤ 0.75 — PASS |
| perplexity gap | 0.0143 | 0.0147 | +0.0004 | ≤ 0.05 — PASS |
| `G6.12` | 0 greedy / 0 sampled of 91 rare records | — | — | PASS |
| untuned-base floor | 0.4914 | — | — | ≈ 0.50 |

### The complete Leg-4 board — and what it shows

| fold | job | reported `G6.10` | ceiling `G6.10` | headroom | z | alarm? |
|---|---|---|---|---|---|---|
| `it` | `1286941` | 0.5539 | **0.5488** | −0.0051 | 0.40 | 🔴 YES |
| `uk` | `1286945` | 0.5336 | **0.5484** | +0.0148 | 1.16 | no |
| `es` | `1286955` | 0.5481 | **0.5466** | −0.0015 | **0.12** | 🔴 YES |

🔴 **`FINDING 114` is confirmed on three folds, and it is stronger than it looked on two.**

| quantity, over the three folds | mean | sd | range |
|---|---|---|---|
| **ceiling** `G6.10` | 0.5479 | **0.00117** | **0.0022** |
| **reported** `G6.10` | 0.5452 | 0.01046 | **0.0203** |

The between-fold standard deviation of the ceiling is **0.00117** — **one eighth of the
Hanley–McNeil standard error of a single one of these AUCs (0.0091)**. Three independently trained
adapters, three different training corpora, three different held-out countries, and the number that
is supposed to say *how much this model could memorise if it had to* comes out at 0.5488, 0.5484,
0.5466. The quantity it is supposed to bound ranges **9.2 times** more widely. `G6.11` says the same:
ceiling range 0.0067 against a reported range of 0.0200.

🔴 **The ceiling is not a property of the fold. It is a constant of the setup**, and
`D-S6-14` has been imposing it as an **unregistered bar at 0.5479 ± 0.001** — **82 % tighter** than
the pre-registered `G6.10 ≤ 0.65`, never registered, and discovered only after it fired.

⚪ **Which folds alarm is therefore decided by noise on the reported side alone.** The three
headrooms are z = 0.40, 1.16 and **0.12**; `es` alarms on a gap of **0.0015** against a difference SE
of 0.0128. Two of three folds alarming is not a signal about two of three models — it is three
reported AUCs scattering by ±0.01 around a constant that sits in the middle of them.

### `FINDING 112` reproduces on all three folds

| fold | reported last-20 mean loss | permuted | difference | z | held-in perplexity gap |
|---|---|---|---|---|---|
| `it` | 0.5565 | 0.5536 | **−0.0029** | −0.15 | 1.7189 → 1.7353 = **0.95 %** |
| `uk` | 0.5005 | 0.5195 | +0.0190 | 0.90 | 1.6572 → 1.6701 = **0.78 %** |
| `es` | 0.5353 | 0.5517 | +0.0165 | 1.07 | 1.6852 → 1.7001 = **0.88 %** |

**Destroying the prefix-to-body pairing costs the training loss nothing, on every fold, in both
directions.** No difference reaches 1.1 sigma, and the held-in perplexity penalty is under **1 %**
everywhere. Meanwhile `G4.3` / `G4.4` / `G4.12` FAIL on every permuted adapter — conditioning really
was destroyed. A model that has lost the pairing entirely fits the data as well as one that has it,
so it never has to memorise, so its MIA AUC is near chance for a reason that has nothing to do with
memorisation capacity.

### What this does and does not change

* 🔴 **All four registered controls PASS on all three folds.** Reported `G6.10` 0.5539 /
  0.5336 / 0.5481 against 0.65; `G6.11` 0.5274 / 0.5074 / 0.5204 against 0.75; perplexity gap 0.0182
  / 0.0097 / 0.0143 against 0.05; `G6.12` **zero exact matches, greedy and sampled, on all three**
  (103 / 40 / 91 rare records). Untuned-base floors 0.4874 / 0.5012 / 0.4914, all within 0.013 of
  0.50 — the splits do not differ for a reason that is not membership.
* `D-S6-16` is unchanged and now rests on three folds instead of one. 🟢 Recommendation
  **(a)** — report the ceiling as **INCONCLUSIVE AS A CEILING**, rest the release on the four
  controls that pass. The brief's §7 carries the three-fold table.
* 🔴 **This is Leg 4, the pilot, and the module prints `NOT REPORTABLE` on every one of these
  runs.** The governing control is the Leg-5 `it` run, `1286896`, still training.
* 🔴 `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`. No threshold moved, no checker
  edited, every alarm reported as it fired. `privacy_audit.md` stays unwritten and **no release
  decision has been made on either leg.**

---

## 2026-08-25 (early) — 🟢 THE GOVERNING LEG-5 CONTROL IS TRAINED AND ITS AUDIT IS SUBMITTED. `FINDING 112` SURVIVES THE 7 B BACKBONE.

`1286896` — **COMPLETED `0:0` in 07:33:23**, three epochs, loss 1.7811 → ≈ 0.52. This is the
`D-S6-14` control the ruling pre-named ex ante: Leg 5, `Olmo-3-1025-7B`, fold `it`. 600 diaries
generated; `G4.3` / `G4.4` / `G4.12` **all FAIL** (`G4.12` CE rise −0.0054 against a required 0.15,
MI drop 0.093 against 0.10), as they do on every permuted adapter.

⚪ **The adapter is at `runs_leg5_permuted_control/leg5_permuted_fold_it/adapter`**, not
`runs_permuted_control/` — the Leg-5 launcher writes to its own tree, and
`4thJ_step6_privacy_mia.sh` already branches on `$LEG` for exactly this. Its `--out` refusal was
checked live before submitting: the script exits 1 rather than run a control that is silently absent.

**Audit submitted: `1286976`**, with the two overrides the script's own comment demands —
`--gres=gpu:nvidia_a100_7g.80gb:1` and `--mem=192G`, since a Leg-5 control loads *two* 7 B bases and
the header's `2g.20gb` slice would OOM after the first. `FINDING 9` discipline: the GRES is named on
the submission, not assumed.

### 🔴 `FINDING 112` is not a small-model artefact — it reproduces on the 7 B backbone

| leg | fold | reported last-20 mean loss | permuted | difference | z |
|---|---|---|---|---|---|
| 4 | `it` | 0.5565 | 0.5536 | −0.0029 | −0.15 |
| 4 | `uk` | 0.5005 | 0.5195 | +0.0190 | 0.90 |
| 4 | `es` | 0.5353 | 0.5517 | +0.0165 | 1.07 |
| **5** | **`it`** | **0.5223** (`1286548`) | **0.5267** (`1286896`) | **+0.0045** | **0.23** |

🔴 **Scaling 1.48 B → 7 B did not make the prefix-to-body pairing matter.** On the reported
leg, on the fold the ruling pre-named, a model that has lost the pairing entirely trains to within
**0.0045** of one that has it — **0.23 sigma**, the smallest difference of the four. The mechanism
behind `FINDING 112` is a property of this corpus, not of the pilot's capacity, and the four
measurements now span both backbones.

⚪ This says nothing yet about what `1286976` will return. The ceiling AUC has not been measured on
Leg 5; the three Leg-4 ceilings sat at 0.5488 / 0.5484 / 0.5466 (`FINDING 114`). Whatever it returns,
`D-S6-16` (a) applies — that undertaking was written before any of the four controls was read, and
it is on the record above.

🔴 `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`, printed by the job itself.
`privacy_audit.md` stays unwritten; **no release decision on either leg.**

---

## 2026-08-25 (early) — 🔴🔴 THE GOVERNING AUDIT IS READ AND **`G6.10` FAILS ITS PRE-REGISTERED BAR**. `FINDING 115`. TWO EARLIER READINGS OF MINE ARE CORRECTED HERE.

Job `1286976`, fold `it`, **Leg 5**, `Olmo-3-1025-7B`, adapter
`runs_leg5/leg5_primary_fold_it/adapter` — **COMPLETED `0:0` in 00:49:01**. This is the run the whole
of Step 6.5 was waiting for. Artefacts: `outputs_step6/privacy_mia_leg5_it.json`,
`outputs_step6/4J_step6_mia_1286976.out`.

### 🔴 `FINDING 115` — the reported model exceeds a pre-registered privacy bar on the reported leg

| | measured | bar | verdict |
|---|---|---|---|
| `G6.10` loss MIA AUC | **0.6645** | ≤ **0.65** | 🔴 **FAIL** |
| `G6.11` reference MIA AUC | 0.5594 | ≤ 0.75 | PASS |
| perplexity-gap control | **0.0570** | ≤ **0.05** | 🔴 **FAIL** |
| `G6.12` verbatim | 0 greedy / 0 sampled of 103 rare records | 0 | PASS |
| untuned-base floor | **0.4886** | ≈ 0.50 | clean |

🔴 **Two of the four registered controls FAIL, and the floor is clean.** 0.4886 is within 0.012
of chance, so the two splits do **not** differ for a reason that is not membership — which is exactly
what makes the 0.6645 readable as membership signal rather than as an artefact of the split. The bar
is exceeded by 0.0145 against a Hanley–McNeil SE of 0.0085: **z = 1.70**, and `TPR@FPR=0.001` is
0.0010 against a 0.05 allowance.

The perplexity gap tells the same story from the other side: train `1.6397` vs test `1.7331`, a gap
of **0.0570** against a registered 0.05. The reported model fits its training members measurably
better than its non-members.

🔴 **Under the prereg's own terms this is a refusal.** `G6.10` is a registered gate, it was
scored on the reported leg with the reported model, and it failed. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45`, printed by the job. No threshold moved and none may.
⚪ It does not overturn the standing project position that the weights cannot be released — it
supplies the measurement that position had been asserted without.

### 🔴 CORRECTION 1 — `FINDING 114` was stated too broadly, and I stated it

The 2026-08-25 entry above says the ceiling *“is not a property of the fold — it is a constant of
the setup”*. **The Leg-5 ceiling is 0.6496.** The three Leg-4 ceilings were 0.5488 / 0.5484 / 0.5466.

| | ceiling `G6.10` | ceiling `G6.11` | ceiling ppl gap |
|---|---|---|---|
| Leg 4 (1.48 B), three folds | 0.5479 ± 0.00117 | 0.5149 ± 0.0034 | ≈ 0.0149 |
| **Leg 5 (7 B), `it`** | **0.6496** | **0.5441** | **0.0511** |

🔴 **The ceiling moves +0.102 with capacity — 87 times its between-fold sd.** So the correct
statement is narrower than the one on the record: **the ceiling is constant across FOLDS at fixed
capacity, and it responds strongly to capacity.** `D-S6-14` does track memorisation capacity across
backbones; what it does not do is discriminate between folds. The “unregistered bar at ≈ 0.548”
reading holds **within Leg 4 only** — on Leg 5 that implicit bar is 0.6496, which sits *above* the
registered 0.65 rather than 82 % below it. `FINDING 114` stands as a Leg-4 result and is corrected
here, not deleted.

### 🔴 CORRECTION 2 — `FINDING 112`'s measurement reproduces; its inference does not, at 7 B

The measurement is unchanged and now spans both backbones: permuted minus reported last-20 mean loss
−0.0029 / +0.0190 / +0.0165 (Leg 4) and **+0.0045, z = 0.23** (Leg 5). Destroying the pairing still
costs the training loss nothing.

But `FINDING 112` went on to infer *“so the control never needed to memorise, so its AUC is near
chance”*. **At 7 B the control's AUC is 0.6496, not near chance.** So the permuted model at 7 B
**does** memorise substantially, while its aggregate training loss stays indistinguishable from the
reported model's. The two facts are compatible — memorisation of 31,560 records moves an aggregate
loss very little — but the inference as written was too strong and is withdrawn for Leg 5. It
survives for Leg 4, where the ceiling really is near chance.

⚪ What both corrections have in common: they were caught by running the governing arm rather than
generalising from the pilot. `FINDING 105` and `FINDING 106` were the same lesson at Step 7.

### What this does to `D-S6-16`

🔴 **Option (a)'s premise is now false on Leg 5.** It read *“rest the release on the four
controls that pass”*; on the governing run **two of them fail**. The ceiling question has not
disappeared — it still governs how the control is written up in the methods — but it is **no longer
what decides the release**. The registered bar decides it, and the registered bar fails.

⚪ The alarm fired here too (headroom −0.0149 and −0.0153, z = 1.23 and 1.19), and on this run the
alarm and the bar agree for once. That agreement is not evidence for the ceiling: a ceiling that sits
0.0149 below a reported AUC which itself sits 0.0145 above the registered bar is simply tracking the
same thing the bar caught.

### Where Step 6.5 now stands

* All four permuted controls are trained and all four audits are read: `1286941` `it`4,
  `1286945` `uk`4, `1286955` `es`4, **`1286976` `it`5**.
* 🔴 `privacy_audit.md` is still unwritten — but it now has a result to write, and it is a
  **FAIL on `G6.10` and on the perplexity-gap control**, with a clean floor and `G6.12` at zero.
* 🔴 Leg 4 remains the pilot and remains `NOT REPORTABLE`. Every Leg-4 number above is context
  for the Leg-5 result, never a substitute for it.
* `D-S6-16` still needs an answer for the **methods write-up**; it no longer gates the release.

---

### 2026-08-25 — 🟢 **`privacy_audit.md` IS WRITTEN. WORK ITEM 6.5 IS CLOSED, AND IT CLOSES AS A REFUSAL.**

`outputs_step6/privacy_audit.md`, written from the four scored artefacts on disk, not from any
summary. Every number in it was re-derived from the JSON; three re-derivations differ from what the
record carried and are recorded as corrections below rather than silently adopted.

#### The decision

🔴 **The fine-tuned adapter weights are NOT released.** `G6.10` — a registered gate with a
registered bar — was scored on the reported leg with the reported model and returned **0.6645
against ≤ 0.65**. Under the pre-registration's own terms that is a refusal. It is not a judgement
call, and the standing position that the weights cannot be released is no longer asserted: it is
measured.

⚪ The Data Availability statement is drafted in §8 of the audit, ready for the paper. It withholds
the weights, ships the `es` and `it` synthetic sets, and **withholds the `uk` synthetic set** with
them, because `G6.13` clause 2 fails on `uk`.

#### The four registered attacks, governing run `1286976`

| # | attack | fails if | measured | verdict |
|---|---|---|---|---|
| 1 | loss-based MIA `G6.10` | AUC > 0.65 | **0.6645** | 🔴 **FAIL** |
| 1b | same gate, clause 2 | TPR@FPR 0.001 > 5 % | 0.0010 | PASS |
| 2 | reference-based MIA `G6.11` | AUC > 0.75 | 0.5594 | PASS |
| 3 | extraction `G6.12` | any exact match, rare strata | 0 of 103 in 39 strata | PASS |
| 4 | DCR / NNDR `G6.13`, Leg 5 | see spec | `es` PASS, `it` PASS, **`uk` FAIL** | 2 / 1 |

Controls: untuned base **0.4886** (clean), perplexity gap **0.0570** against ≤ 0.05 (🔴 FAIL),
permutation ceiling 0.6496 / 0.5441 (alarms, headroom −0.0149 / −0.0153).
**Three of three registered controls are present for the first time.**

#### 🔴 Three corrections, from re-deriving instead of quoting

1. **The `z` on `G6.10` is 1.70 and the SE is 0.00852, not 0.0128.** The 0.0128 on the record is the
   SE of an AUC *difference* at AUC ≈ 0.55 (`FINDING 113`); the bar comparison needs the
   Hanley–McNeil SE of a single AUC at 0.6645, with n = 2,000 per class. Re-derived:
   `Q1 = A/(2−A) = 0.49757`, `Q2 = 2A²/(1+A) = 0.53057`, **SE = 0.008516**, so
   `(0.6645 − 0.65)/SE = 1.699`. The published 1.70 is right; the SE it was attributed to was not.
2. **The Leg-4 ceiling sd is 0.001137, not 0.00117, and the Leg-5 gap is 89× it, not 87×.** The
   brief computed the sd from the 4-decimal values (0.5466 / 0.5484 / 0.5488). At full precision
   (0.5466445 / 0.54838775 / 0.54877925) the mean is 0.547937 and the sample sd 0.0011365, so the
   Leg-5 ceiling's +0.10161 is **89.4×**. Changes nothing — it makes the point marginally stronger —
   and is recorded because the audit quotes the number.
3. **The `G6.13` minimum-DCR claim was mis-stated at first draft and fixed before the file was
   saved.** "Minimum DCR 0.132–0.174" is the range over the `uk` reference sets only; over all nine
   (fold × reference set) combinations the smallest single distance is **0.0694** (`es`, country
   set). The clause that matters — no DCR of zero — holds on all nine.

#### 🔴 `FINDING 116` — the perplexity-gap control fails for the PERMUTED adapter too

The permuted control's own train/test perplexity gap is **0.0511**, over the same 0.05 bar. A model
trained on randomly re-paired prefixes and bodies, **0 fixed points**, still breaches the gap. So on
this corpus at three epochs the gap is measuring train/test overfit of the diary *language*, not
membership of the pairing.

⚪ **It does not rescue the reported failure** — 0.0570 is over the registered bar and ships as a
failure. What it does is forbid reading the gap as a second, independent confirmation of `G6.10`.
The two registered failures are one measurement plus one much weaker one, not two.

#### 🔴 The Leg-5 coverage clause reads FAIL and must never be quoted bare

`coverage_clause: FAIL`, `G6_10 <- NEVER SEEN FAILING`, no-ops `g610_tail` and `pplgap_widen`.

This is the **vacuity condition**, not a new defect. The harness credits a perturbation with felling
a gate only when it moves that gate PASS → FAIL. `G6.10` is already FAIL at baseline here, so the
two injections aimed at it cannot be credited — even though they land exactly as designed
(`g610_tail` → 0.6659, `pplgap_widen` → 0.8367). The same two injections **do** fell `G6.10` on all
three Leg-4 folds, where the baseline passes and the coverage clause is PASS with zero no-ops.
`G6.10` is a demonstrated gate. Same class as the Step 6.4 generated-arm batteries.

#### What this closes and what it leaves

* 🟢 **DoD item 5 — "Privacy audit complete with its three controls" — is met.** All three controls
  present, all four attacks scored, the decision written down with the artefacts that produced it.
* 🔴 The audit **ships two registered FAILs and one partial**, and the write-up must say so. Never
  "the privacy audit passed"; never "4 of 4".
* `D-S6-16` stays open on the **methods write-up only**, recommendation **(a′)**. The release does
  not rest on it.
* ⚪ Nothing on Speed. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` intact; no threshold moved,
  no checker edited.

---

### 2026-08-26 — `G6.8`'s MODEL ARM IS RUN AND FAILS, AND `D-S3-14`'s SPLIT REPORT IS FILED

Both of Step 6's remaining obligations are discharged. Full record:
`Step6_docs/impl/2026-08-26_g68-model-arm-and-uk-split-report.md`.

**`G6.8` — the model arm, which "has never been run on either leg", has now been run on all
three Leg-5 folds.** It was never blocked on a GPU, a checkpoint or the checker: the checker and
its 17/17 self-test were finished on 2026-08-21 and both registered negative controls had been
seen behaving correctly (split-half PASS/PASS, `shuffled_across` FAIL/PASS). It was blocked on one
missing input — the `--ref/--cand` path calls `load(args.ref)` with no `country=` filter, so the
reference must arrive already filtered, and no country-filtered reference existed. Three were
built from the corpus (`outputs_step6/g68_refs/real_{es,uk,it}.jsonl`, 19,140 / 15,854 / 38,260).

🔴 **SEQUENCE arm FAIL and MARGINAL arm FAIL, in all three folds, on both weight bases.** Dwell-time
W1 5–6.7× its 10-min band (50.13–66.57); transition-matrix TVD 3.3–4.7× its 0.050 band
(0.1623–0.2344); diurnal JSD mean 4.6–7.9× its 0.015 band (0.0690–0.1189); time-budget error
38.26–68.67 min/day against 8–15. The one checker that passes anywhere is transitions/day on `es`
(0.32 against a band of 1.50); `uk` reads 1.80 and `it` **3.92** — 12.51 generated transitions a
day against a real 16.43.

⚪ **The verdicts are IDENTICAL under `weight_dia_cal` and unweighted.** `D-S6-4` ruled
`weight_dia_cal` the headline, but a generated diary has no `pid`, so all 5,200 candidates key
nothing and sit at 1.0 while the reference is weighted; rather than weight one side only, both
bases were run and both agree. Under weighting the `uk` reference is 15,852, not 15,854 — two UK
rows carry a null `weight_dia_cal` and are dropped rather than defaulted.

🔴 **This is not independent evidence.** It is the same failure `G6.1` (9 of 9) and `G6.4`
(0 PASS / 9 FAIL) already report, read on quantities the prompt does not carry. Never write
"G6.8 was run" without "and it failed", and never present it as a second confirmation.

**`D-S3-14` — the UK-fold split report is filed, and half of it is reported UN-QUANTIFIED, which
is that decision's own fallback and not an omission.** The 551 UK diaries at
`strat_hh_type = unknown` are 3.48 % of the fold across 107 households (481 train / 70 held-out
under `D-S6-1(b)`). 🔴 **Not one generated UK diary carries that value on either leg** — 0 of 600,
0 of 600, 0 of 5,200, 0 of 5,200 — because generation prompts are drawn from the Step 5 synthetic
population, built from census marginals, and a census margin has no "household type unknown"
category. The model was never asked for this cell, so its scores cannot be split on it.

What IS quantified: the cell is **missing-not-at-random** — 15-24-year-olds +20.16 pp, students
+8.81 pp, other-inactive +11.59 pp, women +9.64 pp, retired **−17.06 pp**, day type flat — and it
fits the published UK level-1 budget **3.5× worse** than the rest of its own fold (MAE 29.087 vs
17.187 min/day; MAPE **34.332 %** vs 9.945 %). Its influence on the fold-level number is bounded
and measured: dropping it moves whole-fold MAE by **+0.158 min/day** and MAPE from 10.647 % to
9.945 %, worst single aggregate **+1.07 min/day** (`AC0`).

⚪ No threshold moved, no checker edited, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
unchanged.

---

### 2026-08-27 (night) — `D-S6-16`'s METHODS WRITE-UP IS DRAFTED. THE DECISION IS STILL OPEN AND THAT IS SAID IN THE TEXT.

🟢 **The one thing `D-S6-16` still governed — how the `D-S6-14` ceiling is reported — now has
drafted text.** `writing/4thJ_writeup_notes.md` **§8** (375 → **478** lines; backup
`.bak_pre_ds616`, `[ -s ]`-verified before the append): `8.1` Methods (the control and what it turned
out to measure), `8.2` Results and limitations (what actually decided the release), `8.3` the
`FINDING 112` sentence and why it may not be generalised, `8.4` scope.

🔴 **The decision is NOT ruled by this.** The passages are drafted under **(a′)**, the standing
recommendation, and say so in their first paragraph; **(c′)** — additionally building the
body-randomised ceiling, a full 7 B retrain — remains the author's call and one line closes it. Under
(c′) the drafted text survives unchanged and gains a paragraph, which is why drafting it now costs
nothing.

🔴 **What the text carries, because these are the sentences easiest to lose.** The ceiling is
reported as **constant across folds at fixed capacity** (Leg 4: 0.5488 / 0.5484 / 0.5466, sd
**0.001137**) and **strongly responsive to capacity** (Leg 5: **0.6496**, +0.102 = **89.4×** that
sd), so it discriminates **backbones, not folds**; its alarms are quoted with their z-values
(**0.40 / 1.16 / 0.12** against an AUC-difference SE of 0.0128) **to explain them, never to re-score
them** — adding the tolerance and re-scoring is option (b), declined because it sets a threshold
after seeing the number it would decide. The control is **not removed**: it was built, run and found
not to do what it was designed to do, and deleting a control after seeing its result is the move this
project refuses everywhere else.

🔴 **Three sentences the write-up must not lose**, all already on this page and now in the drafted
text: never *"the privacy audit passed"* or *"4 of 4"* (it ships **two registered FAILs and one
partial**); the perplexity gap is **not** independent confirmation (`FINDING 116`, 0.0511 on the
permuted adapter); and the Leg-5 coverage clause FAILs for **vacuity**, the same two injections
felling `G6.10` on all three Leg-4 folds.

🔴 **`FINDING 112`'s inference is written as withdrawn for Leg 5 and standing for Leg 4**, with the
generalisable half stated in the methods rather than only in the decision record: *an aggregate loss
that matches is not evidence that a model did not memorise* — at 7 B the control reaches 0.6496 while
its last-20-step loss sits +0.0045 (z = 0.23) from the reported model's. The Leg-4-only
*"unregistered bar at ≈ 0.548"* reading is quoted as Leg-4-only or not at all.

⚪ **Nothing moved.** No band, threshold, verdict or count changed; no gate was scored; no run was
submitted; the release position is unchanged and still rests on `G6.10`'s registered FAIL.
`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.
