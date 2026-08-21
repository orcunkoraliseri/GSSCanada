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
