# Pre-registration — 4J, leave-one-country-out transfer of a fine-tuned LLM onto HETUS time-use diaries

## 🔴 STATUS: **FROZEN 2026-08-18. Its md5 lives in the sidecar `prereg.md.md5`, NOT inside this file. `G4.14` IS LIVE.**

**Drafted 2026-08-18. Frozen 2026-08-18, on the author's instruction, before any training job of any
leg had been submitted.** The last open item in it, **D-S6-1**, was ruled **(b)** by the author the
same day and applied by Speed job `1266814` before the freeze — so nothing in this file was left to
be filled in later.

🔴 **From this moment this file is not edited. Not for typos, not for clarifications, not for numbers
that turn out differently.** If it must change, the change is a **new dated document** stating what
changed, why, and which results were computed under which version — and every fold computed under the
old version is re-run or discarded, never mixed with the new.

### 🔴 Why the md5 is not printed inside this file

**A file cannot contain its own hash.** Writing the value in would change the value. The recorded md5
therefore lives in exactly two places, both outside this document:

* **`Step6_docs/outputs_step6/prereg.md.md5`** — the sidecar, one line, the authority;
* the **Progress Log** of `Step6_docs/4thJ_06_transfer.md`, dated, so it is also in an append-only
  record that cannot be quietly re-written.

`G4.14` recomputes the hash **from `prereg.md` on disk** at every run (`V4.g`) and compares it to the
sidecar. **It never reads the value out of the run manifest it is supposed to be checking** — that
circularity is what retired `G1.7b` in Step 1, and it is not being reintroduced here.

**The freeze was in time, and that is the whole point.** §4.2-bis of `4thJ_04_finetuneLLM.md` requires
this file frozen **before the first Leg-5 training job is submitted**. At the moment of freezing,
`outputs_step4/` contained exactly one artefact — `staged_weights.json` from job `1245620`, three
checkpoint revision hashes — and **no training run of any leg existed.** After a model exists, a
pre-registration is a description of it, and the difference does not show up anywhere in the output.

**Why this file could not be written before 2026-08-18.** The blocker was named in
`4thJ_00_HETUS_LLM_Pipeline.md` and it was specific: *"its second hold-out's stratification depends on
a corpus that does not exist."* That corpus now exists — `4J_step3_corpus.jsonl`, 73,254 records,
emitted by Speed job `1257441` and checked by a twenty-gate battery — so §7 is written against
measured counts rather than guessed ones. Nothing else was waiting.

---

## 1. What is being claimed

Train an open-weight LLM on the harmonised time-use diaries of **N−1 countries**. Generate a synthetic
population for the **held-out** country conditioned **only on that country's published demographic
marginals**, with **none of its diaries seen in training**. Score the generated population against the
held-out country's published aggregate tables.

**The claim is transfer**: that the model carries diary structure across a national boundary it was
never shown. Everything below exists to make that claim falsifiable in advance.

---

## 2. The rotation, and the fact that nothing is chosen

**Three leave-one-country-out folds. Three adapters. Three reported results.**

| fold | held out | trained on | diaries held out |
|---|---|---|---|
| 1 | **Spain (`es`)** | UK + Italy | 19,140 |
| 2 | **UK (`uk`)** | Spain + Italy | 15,854 |
| 3 | **Italy (`it`)** | Spain + UK | 38,260 |

Corpus total **73,254 diaries / 2,024,068 episodes**, 0 rows and 0 diaries dropped.

🔴 **No country is chosen, because all of them are held out in turn.** That is author decision 11,
closed 2026-08-14 by removing the choice rather than by making it. The hazard was never *which*
country got picked; it was that a picked country can be picked **late**, after results are visible,
and nothing repairs that afterwards. **Rotation leaves nothing to pick.**

🔴 **LOCO trains on TWO, not three.** Author decision 16 (2026-08-15) excluded France. The rotation
is unchanged in kind and shorter in length; every "trains on the other three" in any older document
is stale and this table is the authority.

**That thinness is a stated limitation, not a hidden one.** Two training countries per fold is thin,
it is limitation C4, and Track A is the only thing that raises it.

---

## 3. The pre-named fold, fixed before anything was trained

**Held-out SPAIN.** Confirmed by the author 2026-08-14, by a rule fixed in advance — **alphabetical
ISO code**, over `ES, FR, GB, IT` — and taken while **no fold had been trained and no result
existed**.

🔴 **The pre-named fold did not move when France left, and that is the part that matters.** Spain was
first with France in the set and is still first without it. Had the rule selected France, the honest
move was to re-run the rule and say so loudly, never to slide to the next-best fold.

**It is used for exactly two single-fold measurements** — the **ceiling run** (full fine-tune, 8-bit
AdamW) and the **comparison arm** (`Qwen/Qwen2.5-7B`) — and 🔴 **both must be reported as single-fold.
Quoting either as a general result across the corpus would be quoting one fold as three.**

---

## 4. The France re-admission window, and where it closes

**France may be re-admitted in full, restoring a four-fold rotation, up until the moment the FIRST
FOLD IS SCORED.** Not until Step 4, not until training starts — until a score exists.

🔴 **After the first fold is scored, the design is frozen and France can only ever be an extra
held-out country reported separately as an out-of-design test.** Never a fourth fold. Never averaged
into the rotation.

---

## 5. The nulls, and which one is the bar

| null | strength | role |
|---|---|---|
| Pooled all-country average diary | weak | secondary, reported |
| Nearest-neighbouring-country model | moderate | secondary; answers the geographic-proxy objection |
| **Real diaries from the N−1 pool, raked by IPF onto the held-out country's published marginals** | **strongest** | 🔴 **THE PRE-REGISTERED BAR** |

**Why the raked-donor null is the bar.** Every raked donor is an **authentic human day** — perfect
grammar, real transitions, real variance. If a fine-tuned LLM cannot beat a demographically raked pool
of real European donors on the held-out country, **the transfer claim fails.** There is no weaker
reading of that sentence.

🔴 **The bar is stated in the INTRODUCTION as the objective, not disclosed in the evaluation section**
(author decision 4). A bar set in advance and then cleared is worth more than one chosen after the
results are in, and reviewers can tell the difference.

🔴 **This is the only place raking is permitted in this project. It builds the null. It never touches
our output.** A raked *output* would be fitting to the answer.

**Construction, so it cannot be built favourably:** IPF the **real** N−1 diaries onto the held-out
country's published marginals — **the same marginals the model was given, the same geography, the same
strata.** A null built on different marginals from the model's is not a null, it is a handicap.

---

## 6. FAIL criteria — any one of these fails the claim

1. **MAE ≥ the raked-donor null.**
2. **MAPE > 20 %.**
3. **The sign of the country's divergence from the European mean is inverted.**

These are pre-registered as *disqualifying*, not as *discussion points*. A fold that trips any one of
them has failed, and the paper says so.

### 🔴 The outcome that would prove we cheated

The best pre-registration names the result that would convict us, not the one we expect. For this
design there are four, and each has a detector named in advance:

* **A fold scores well and `G4.13` cannot show zero held-out-country records in the shard the trainer
  actually loaded.** Then the score is held-in performance wearing a fold's name. `G4.13` counts from
  the loaded shard, never from the config or the filename, because a filename is not evidence.
* **Generated output tracks a memorised national stereotype rather than the conditioning vector.**
  Detector: the **fictional-country control** — condition on an invented country token with perturbed
  marginals and verify the output follows the vector. If it does not, contamination is the simpler
  explanation than transfer.
* **Marginals are matched and joint structure is not.** Detector: score **joint** quantities that were
  never in the prompt — co-presence cross-tabulations, transition entropy, dwell-time distributions
  conditioned on **pairs** of attributes. Matching what we handed the model is not a result.
* **The reported spread across folds is narrower than the spread actually observed.** That is §8's
  reporting clause being violated, and the only defence against it is that all three folds are named
  here, in advance, including whichever turns out worst.

---

## 7. The second hold-out — **household-level. D-S6-1 ruled (b), 2026-08-18, and applied.**

**What it is.** A random sample of **households** held out from *inside* the training countries, kept
as an ordinary test set. It measures whether the model reproduces data whose country it has **already
seen** — which is what papers 1 to 3 measure.

🔴 **It is a sanity check. It is NEVER reported as transfer, and it never appears in the same table as
the fold results.** It is named here precisely so that it cannot later be presented as evidence of
transfer.

### The definition, frozen

| item | value |
|---|---|
| unit | **household**, keyed `(country, hid)` |
| fraction | **0.10** |
| seed | **42** |
| selection | `rng = numpy.random.default_rng(42)`; units in order of first appearance; `permutation(n)[:round(n * 0.10)]` |
| households | **32,205 → 3,220 held out / 28,985 train** |
| diaries | **7,328 held out / 65,926 train**, of 73,254 |
| respondents | 65,334, **none straddling** |
| held-out record fraction | **0.1000** |

| country | diaries train | diaries held out | households train | households held out |
|---|---|---|---|---|
| es | 17,332 | 1,808 | 8,640 | 901 |
| it | 34,366 | 3,894 | 16,532 | 1,903 |
| uk | 14,228 | 1,626 | 3,813 | 416 |

🔴 **The held-out record fraction is 0.1000 by arithmetic, not by adjustment.** The household unit does
not owe us a round number of records and was not nudged toward one. Had it landed at 0.093 it would be
recorded as 0.093.

### What was there before, and the leak that was measured before it was removed

The corpus was originally split by **respondent** `(country, hid, pid)` — 65,334 respondents, 10 %,
seed 42, giving 7,343 held-out records / 65,911 train. **`4thJ_step3_build.py` flagged that at line 20
as an ASSUMPTION rather than a specification**, and that flag is what surfaced this. The disclosure
worked; the reading of it did not.

🔴 **The leak was not marginal, and it is recorded because it justifies the change rather than
decorating it:**

* **4,900 households straddled the old split** — members on both sides — which is **15.22 % of all
  32,205 households and 23.30 % of the 21,031 multi-respondent households**;
* **15,429 records, 21.06 % of the corpus**, lived inside a straddling household;
* per country: es 1,448 · it 2,883 · uk 569.

**Why that mattered.** Household members share a dwelling, a day and most of a routine. A fifth of the
corpus sitting in households with a member on the other side of the split made the in-country test set
**easier than it looked**. That hold-out's entire job is to be an honest in-country baseline against
which the transfer folds are read, and an inflated baseline does not flatter the transfer result — it
makes it look *worse*, which is the direction least likely to be questioned and therefore least likely
to be caught.

### How it was applied — a re-label, and it was proved to be one

Speed job **`1266814`**, `COMPLETED`, exit `0:0`, 00:00:48. `4thJ_resplit_household.py` re-read the
corpus and rewrote **only the `split` field**. The selection procedure was mirrored line for line from
the build so that the **unit** is the only thing that differs — a different shuffle would have
confounded "we changed the unit" with "we changed the draw".

Verified from disk, record for record, against the pre-change backup:

```
records compared      : 73254
records whose TEXT    differs :     0   (must be 0)
records whose KEY     differs :     0   (must be 0)
records whose LABEL   changed : 13149   (the intended change)
households straddling the new split : 0
respondents straddling the new split : 0
```

🔴 **No record text moved, so no Step 3 gate is disturbed and the twenty-gate battery does not need
re-running.** The respondent-split corpus is preserved at
`/speed-scratch/o_iseri/4J_step3_corpus_respondent_split.jsonl`; nothing was overwritten without a
size-matched backup taken first. Full report:
`Step6_docs/outputs_step6/4J_split_report_household.md`.

**Stratification.** The draw is **unstratified by design** — a simple random sample of households
within the training pool. It is not balanced on country, age band, household type or day type. Two
reasons: this hold-out is a sanity check rather than an estimator, so an unstratified draw is the
honest description of what it is; and the per-country counts above are reported so that anyone can see
what the draw actually produced instead of trusting that it was balanced. **The counts are the
report — there is no balancing step whose success would have to be taken on faith.**

---
## 8. The reporting clause — all three folds, including the worst

**All three folds are reported. Including the worst.**

🔴 **A fold may be *explained*. It may not be *removed*, averaged away, or relegated to an appendix.**
Reporting the best fold, or dropping one as anomalous, is **choosing the held-out country late by a
different door** — the exact defect rotation was adopted to prevent.

This clause also states what rotation buys: it turns the paper's single most fragile number into a
**distribution over three folds**, which is what separates *"transfer works"* from *"transfer works
for Spain"*.

---

## 9. The freeze clause — the design closes when the first fold is evaluated

**Once ANY fold has been evaluated, the following are frozen for every remaining fold:** architecture,
prompt format, hyperparameters, decoding constraints, gates, and thresholds.

🔴 **A change made after seeing fold 1 contaminates folds 2 and 3, and the contamination does not show
up anywhere in the output.** No metric moves. No gate fires. The numbers look exactly as they would
have looked.

**If a change is genuinely unavoidable, every fold is re-run from the new design and the old results
are discarded — not mixed, not compared, not reported alongside.** A table containing folds from two
designs is a table with no interpretation.

---

## 10. 🔴 The freeze record

**FROZEN — 2026-08-18.**

| field | value |
|---|---|
| md5 of this file | in **`Step6_docs/outputs_step6/prereg.md.md5`** — see §STATUS for why it is not printed here |
| frozen on | **2026-08-18** |
| authorised by | the author, in writing: *"option b et apres continuer avec step 4, jusqu'a la fin"* — ruling D-S6-1 as (b) and instructing that Step 4 proceed, which is the roadmap step immediately after this freeze |
| what existed at freeze time | `outputs_step4/staged_weights.json` (job `1245620`, three checkpoint revision hashes) and **no training run of any leg** |
| command | `md5sum Step6_docs/outputs_step6/prereg.md` |

**`G4.14` is now live.** Every run manifest carries this md5; all manifests carry the **same** value;
the value is recomputed **from the file on disk** at every run (`V4.g`) and compared against the
sidecar. Missing field, mismatched field, or a changed file: **FAIL**.

🔴 **If this file is ever edited, `G4.14` fails every run in the project simultaneously — including
runs that had already passed.** That is intended. A pre-registration whose breach fails only future
runs is not a pre-registration.

---

## 11. Provenance of every number in this file

| figure | source | status |
|---|---|---|
| 73,254 diaries; 2,024,068 episodes; 0 dropped | Speed job `1257441` `.out`, loader accounting | measured |
| per-fold diary counts 19,140 / 15,854 / 38,260 | same, per-country loader accounting | measured |
| 32,205 households → 3,220 / 28,985; 7,328 / 65,926 diaries; per-country table | Speed job `1266814` `.out` and `4J_split_report_household.md` | measured |
| 4,900 straddling households, 15.22 % / 23.30 %, 15,429 records, 21.06 % | same | measured |
| 65,334 respondents, none straddling | jobs `1257441` and `1266814`, agreeing | measured |
| the three FAIL criteria | `4thJ_06_transfer.md` §6.1 | specification |
| the three nulls and which is the bar | `4thJ_06_transfer.md`, `RL06`, author decision 4 | specification |
| rotation over three countries, LOCO trains on two | author decision 16, 2026-08-15 | decision |
| pre-named fold = Spain | author, 2026-08-14, alphabetical ISO rule | decision |
| second hold-out = household, 10 %, seed 42 | **author, D-S6-1 (b), 2026-08-18** | decision, applied and verified |

🔴 **Nothing in this file is a placeholder dressed as a value, and there is no longer anything in it
marked open.** That is the condition it had to reach before it could be frozen.

### What this pre-registration does NOT cover, stated so the omission is not read as coverage

* **The Eurostat aggregate tables that §6's thresholds are expressed against** — `tus_00age`,
  `tus_00educ`, `tus_00selfstat`, `tus_00hh`, `tus_20startime` — have **not been opened, downloaded,
  or confirmed to exist** for these three countries at the waves we hold. 🔴 **Every threshold here is
  written against tables nobody in this project has yet confirmed we can obtain.** That is a real
  dependency of Step 6 and it is recorded here rather than discovered at scoring time.
* **The privacy audit** (work item 6.5, from `RL10`) is specified in `4thJ_06_transfer.md` and is not
  restated here. This file governs the experiment's design, not its release conditions.
* **`strat_hh_type = unknown`** — 551 UK diaries, 3.5 % of the UK fold, a value neither training
  country emits. Ruled by **D-S3-14 (a)** on 2026-08-18: it stays, as a declared limitation. 🔴 **Step
  6 owes a split report** — the UK fold's scores for that cell versus the rest — and if the split
  cannot be produced it is reported as un-quantified **and said to be so**. Note the failure mode
  precisely: the token `unknown` also occurs in `strat_econ_status`, which Italy emits, so under
  UK-held-out the model has seen the symbol inside the same prefix. **What is novel at test time is
  the field position, not the symbol.**
