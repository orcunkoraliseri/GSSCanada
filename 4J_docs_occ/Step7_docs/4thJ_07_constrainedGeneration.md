# Step 7 — Constrained generation at scale, and schedule production

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 7. Validation: `4thJ_07_constrainedGeneration_val.md`

---

## STATUS

**OPEN. Mechanism decided by `RL12`. Nothing built.**

---

## AIM

Turn a synthetic population into 10⁵ to 10⁶ **structurally valid** diaries, and then into EnergyPlus
schedules.

---

## THE EPISODES-VERSUS-SLOTS CONFLICT, AND WHY EPISODES WIN

`RL12` argued for fixed 48 or 144 slots because a grammar cannot enforce an unbounded arithmetic sum,
and `sum(DUR) == 1440` looks like exactly that. `RL07` argued for episodes on a measured four-fold
token saving.

**Episodes win, and `RL12` supplies the reason in its own text.** The sum is neither unbounded nor
continuous: durations are multiples of 10 minutes and the total is fixed at 1440, so the running total
takes **145 distinct values**. A 145-state tally automaton is finite, therefore the constraint is
regular, therefore it is enforceable by the same FSM machinery. **We keep the token saving and the
hard guarantee.**

Written down because it is the kind of resolution that looks obvious afterwards and is expensive to
rediscover.

---

## STRUCTURE IS GUARANTEED, NOT ENCOURAGED

One percent malformed at one million records is ten thousand broken records, and 🔴 **silently
discarding them biases the population toward whatever the model finds easy** — the same class of error
as choosing a threshold that makes a gate pass.

* **Engine: vLLM with XGrammar**, under about 8 % latency overhead. Not a naive `LogitsProcessor` and
  not early Outlines, which `RL12` puts at 50 to 200 %. A hand-written processor is kept as a
  **unit-test oracle only**.
* 🔴 **The backbone must have a native vLLM kernel, and this became a selection criterion.** Read from
  `vllm/model_executor/models/registry.py` on 2026-08-14: `Olmo3ForCausalLM`, `Qwen2ForCausalLM` and
  `Qwen3ForCausalLM` map to native implementations; `Olmo2ForCausalLM` and `OlmoForCausalLM` map to
  `("transformers", "TransformersForCausalLM")`, the generic fallback. **This is the single reason the
  backbone is OLMo 3 rather than the OLMo 2 checkpoint that first looked best.**
* **XGrammar imposes no constraint on model choice.** It detects vocabulary type (`RAW`,
  `BYTE_FALLBACK`, `BYTE_LEVEL`) from the vocabulary itself. Checked in
  `python/xgrammar/tokenizer_info.py`, not assumed.

**Constraints encoded:**

1. the **duration tally** (145 states);
2. vocabulary membership for `ACT` and `LOC`;
3. **transition legality** — no workplace-to-home without an intervening travel episode;
4. **household-consistent co-presence**, via a small set of pre-compiled grammar variants indexed by
   household type, so nothing is compiled per sample.

---

## 🔴 REPORT THE CONSTRAINT-FIRING RATE, PER STRATUM

**100 % validity after masking is a property of the DECODER, not of the model.** The metric that
measures the model is how often the mask had to intervene.

* Reported for **three** models: untuned base (expect a high rate, over 35 %, or the constraint is not
  doing anything), fine-tuned unconstrained, fine-tuned constrained.
* 🔴 **Broken down by demographic stratum.** A firing rate concentrated in minority strata means the
  mask is doing the most work exactly where the model is weakest, and that **biases those strata**.
* Alongside it, the **unconstrained well-formedness rate**, which is the honest model-quality number.

Masking renormalises probability over the allowed set, which is **not neutral**. Audited by generating
an unconstrained rejection-sampled control batch and confirming the constrained batch's marginals have
not moved.

---

## DIARIES TO SCHEDULES

* Presence fraction per slot per dwelling, from location codes **with the code-11 indoor rule from
  Step 2B applied**. 🔴 *(2026-08-20 `FINDING 42`: the record carries `LOC` as a STRING; the rule is `LOC == "at_home"`, which also picks up Italy's merged code 12 that a literal `11` would drop.)*
* **Activity-resolved internal gains**, which is the part a presence fraction throws away.
* 🔴 **`Schedule:File`, not `Schedule:Compact`.** At urban scale, compact blocks bloat the IDF past
  twenty thousand lines per schedule.
* 🔴 **`Interpolate to Timestep = No`.** A step-wise presence signal interpolated linearly is no longer
  the signal we generated: it invents fractional occupants and smears appliance peaks. Inherited from
  3J and confirmed independently by `RL13`.
* Occupant count from household size via the `People` object, modulated by a 0-1 presence schedule.
* Residential **replaces** the baseline schedule, per the papers 2 and 3 convention.

---

## 🔴 THE GAP `RL17` PART D FOUND: HOW 365 DAYS BECOME ONE YEAR

**Nothing in this plan says how a household's 8,760 hours are assembled from generated days**, and the
two obvious rules are wrong in opposite directions.

* **Independent daily resampling** assumes an occupant with no habits. It washes out individual
  variance and **damps** coincident peaks.
* **Static repetition** of one generated weekday introduces no day-to-day entropy at all and
  **exaggerates** them.

Real people wake at 06:45 most weekdays, not at a fresh random time each morning.

**The experiment, before the Step 8 campaign is designed:** 100 households, one archetype, three
chaining rules — independent daily resampling, static repetition, and Markovian habit-coupled
resampling — compared on annual peak electrical power and on heating and cooling ramp rates.

🔴 **If peak demand moves by more than about 25 % between rules, the chaining method dominates the
downstream result regardless of transfer quality**, and Step 8 would be measuring our convention
rather than the model. **This is open decision 14, and it is the only decision in the project still
open.**

### What `RL21` settled on 2026-08-14, and what it did not

`L21` asked the literature this exact question. **The answer is that the literature does not have one.**

* 🔴 **Zero published studies** compare two or more chaining rules on the same building, same weather,
  same archetype, with the daily generator held fixed. Studies comparing *static versus stochastic*
  schedules all conflate within-day stochasticity with cross-day assembly. **So this experiment cannot
  be replaced by a citation.**
* **No standard defines a protocol.** No ASHRAE, ISO or IBPSA document, and **IEA EBC Annex 66 and
  Annex 79 are silent** — they treat schedule generation as an upstream boundary condition. Practice
  splits between static repetition in compliance modelling and Markov chains with midnight state
  carryover in academic work, and is almost never justified in methods sections.
* 🔴 **The 25 % threshold above has no basis in the literature and is permanently labelled
  project-chosen.** `RL21` searched ASHRAE Guideline 14, IPMVP and FEMP and found nothing defining when
  a modelling convention dominates a result. Guideline 14's tolerances are model-versus-measurement, a
  different quantity, and may be quoted as context but never as our bar.
* 🔴 **Every percentage in `RL21` is rejected**, including its headline claim that peak moves 15 to 35 %
  between rules. That number is labelled a measured fact while the same report says nobody has measured
  it, and it appears elsewhere in the same report as 15 to 40 % and as 10 to 25 %. **Do not carry any
  `RL21` number into this document or into the manuscript.** See parent V13.

### 🔴 The one `RL21` finding that changes the experiment

**A two-day survey of one weekday plus one weekend day cannot identify consecutive-day transition
probabilities.** The two observed days are not adjacent and they straddle a day-type regime change.
This is arithmetic rather than literature, so it is accepted on its face.

**Consequence: rule 3 cannot be fitted from our own corpus.** Its persistence parameter would be chosen
by us, and comparing a rule we parameterised against two rules we did not is comparing our bookkeeping
against itself — the exact failure this decision exists to detect.

**So rule 3 is run as a sweep over the persistence parameter and reported as a sensitivity band**, not
as a single fitted rule. What a two-day design *can* identify is individual baseline propensity and
weekday-to-weekend covariance, and those are used for household archetype assignment instead.

**Also measure annual energy in the same campaign.** `RL21` infers it moves under 3 % while peak moves
far more. If true, it is the reason peak is the discriminating metric and annual energy would give a
falsely reassuring answer. **It costs nothing to record both, and measuring is what settled open
decision 3.**

---

## WORK ITEMS

### 7.1 — Compile the grammar

The 145-state tally automaton, the vocabulary sets, the transition table, and the household-indexed
co-presence variants. **Pre-compiled, never per sample.**

### 7.2 — The throughput comparison, before the campaign is sized

🔴 `Olmo-3-1025-7B` has **no grouped-query attention** — 32 KV heads against Qwen's 4 — so its KV
cache is about **nine times** larger per token, against which the 34 % token saving buys back only
part. KV cache is what limits vLLM's concurrent batch.

Run `Olmo-3-1025-7B` against `Qwen/Qwen2.5-7B`: same grammar, same batch, diaries per second, peak KV
memory. **Record it.** The training-side argument for OLMo 3 is settled; the generation-side argument
is not, and if throughput dominates, the comparison arm and the primary can swap **without any of the
serialisation work being wasted**, because the tokenizer decision is what the corpus depends on.

### 7.3 — Generate

Per country, per fold. Constrained, at the Step 5 temperature, `p ≤ 0.98` if top-p is used at all.

### 7.4 — The three-model firing-rate report

Untuned base, fine-tuned unconstrained, fine-tuned constrained. Per stratum.

### 7.5 — The unconstrained rejection-sampled control batch

Generate without the mask, reject invalid records, compare marginals against the constrained batch.
**This is what makes the renormalisation claim checkable rather than asserted.**

### 7.6 — Decide the chaining rule (open decision 14)

Run the three-rule experiment above. Record the peak-demand spread. **Decide, and write down why.**

**Definition of done, sharpened after `RL21`:**

1. Three rules run: independent daily resampling, static repetition, and habit-coupled resampling
   **swept over its persistence parameter** rather than fitted.
2. **Both** metrics recorded per rule: aggregate coincident peak power and ramp rates, **and** annual
   heating and cooling energy. The second is what tests `RL21`'s inference that annual energy is
   insensitive, and it is free.
3. **A cheap pre-screen before the full campaign:** compute schedule-level aggregate coincidence and
   mean pairwise cross-correlation on the assembled 8,760-hour arrays. It costs seconds. 🔴 It is a
   **screen, not a substitute** — `RL21` claims a shift in it "guarantees" a shift in simulated peak,
   which is an unsupported causal claim with an invented threshold.
4. **The activity-vocabulary check**, from `RL21` Part D and the one genuinely new thing it returned:
   count distinct activity codes per synthetic individual per month, and check household role coherence
   across consecutive days. Under independent resampling a synthetic full-time worker walks the whole
   conditional distribution and accumulates an implausible activity vocabulary; a household can have a
   spouse commuting on Tuesday and not on Wednesday for no reason. 🔴 **The realistic value is computed
   on the held ISTAT data, not taken from `RL21`**, whose criterion is project-chosen like everything
   else in it.
5. The threshold used is stated as **project-chosen**, with ASHRAE Guideline 14 named as context and
   explicitly not as the bar.

### 7.7 — Emit schedules

`Schedule:File`, `Interpolate to Timestep = No`, indoor rule applied, activity-resolved gains carried.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step7/generated_<country>.parquet` | Step 6 scoring |
| `outputs_step7/firing_rate_by_stratum.csv` | Step 7 validation; the results section |
| `outputs_step7/rejection_control.parquet` | Step 7 validation |
| `outputs_step7/throughput_comparison.md` | Campaign sizing |
| `outputs_step7/chaining_experiment.md` | Open decision 14; Step 8 |
| `outputs_step7/schedules/*.csv` | Step 8 |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`, one MIG instance per job. **No distributed generation across MIG
slices** — there is no peer-to-peer path between slices of one physical GPU.

---

## WHAT BLOCKS THIS STEP

Steps 3 (grammar is defined against the record format), 4 (the adapter) and 5 (the people).

**What this step blocks:** Steps 6, 8 and 9.

---

## DEFINITION OF DONE

1. Grammar compiled, all four constraint classes encoded, oracle agreement demonstrated.
2. Throughput comparison run and recorded **before** the campaign is sized.
3. Generation complete for every fold.
4. Firing rate reported for three models, per stratum.
5. Rejection-sampled control generated and marginals compared.
6. Open decision 14 closed with a written reason.
7. Schedules emitted with the indoor rule applied.
8. All Step 7 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 Item 7.2 is the one that could still reverse a settled decision. The KV-cache figure is
  arithmetic from measured config values, **not a benchmark**, and it is the only number in the
  backbone argument that has not been run.

### 2026-08-14 (second entry) — `RL21` returned; decision 14 stays open but changes shape

* ✅ **The commissioning question came back zero.** No published study compares chaining rules on the
  same building with the daily generator held fixed; no standard defines a protocol; Annex 66 and
  Annex 79 are silent; no citable threshold exists for convention dominance. **Item 7.6 can no longer
  be replaced by a citation — it is the only way this decision closes.**
* 🔴 **The 25 % threshold in section 7E is now permanently labelled project-chosen.** `RL21` searched
  ASHRAE Guideline 14, IPMVP and FEMP and found nothing. Guideline 14 is model-versus-measurement, a
  different quantity, and is context only.
* 🔴 **No `RL21` percentage may enter this document.** Its headline 15-35 % peak divergence is labelled
  a measured fact in a report whose own `B1` says the measurement has never been made, and the same
  quantity appears elsewhere in it as 15-40 % and as 10-25 %. Parent V13 has the full list.
* 🔴 **Rule 3 changed from fitted to swept.** A two-day design of 1 weekday + 1 weekend cannot identify
  consecutive-day transitions, so its persistence parameter cannot come from our corpus. Fitting it
  ourselves and then comparing it against two rules we did not fit would compare our bookkeeping
  against itself.
* **Item 7.6 gained four clauses:** record annual energy alongside peak so `RL21`'s insensitivity claim
  is measured rather than believed; a seconds-cheap coincidence pre-screen that is a screen and not a
  substitute; the activity-vocabulary and household-role-coherence check from `RL21` Part D, with its
  realistic value computed on held ISTAT data rather than taken from the report; and an explicit
  project-chosen label on whatever threshold is used.
* **`RL21` Part D is the one genuinely new failure mode in the round** and it belongs to this step:
  independent resampling inflates a synthetic individual's activity vocabulary and breaks household
  role coherence between days. It also links to open decision 12, since role coherence is a
  household-level property.

### 2026-08-20 — 🔴 **TWO GATES IN THIS STEP READ FIELDS THE RECORD FORMAT DOES NOT CONTAIN. `FINDING 42`, `FINDING 43`, `D-S7-1`.**

Written as parallel work while Step 4's `it` fold holds the GPU. Nothing here was run — Step 7 has
never been run, `outputs_step7/` is empty, and no grammar has been compiled. Everything below comes
from reading this step against the **frozen record format** in `../tools/encoder.py` and the shipped
Step 2 crosswalks.

#### 🔴 `FINDING 42` — `G7.13`'s indoor rule tests `LOC == 11`. The serialised `LOC` is a **string**, and `11` is not one of its values.

`G7.13` requires presence be derived via **`(LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)`**, and the
implementation doc's *"DIARIES TO SCHEDULES"* section repeats it as *"location codes with the code-11
indoor rule from Step 2B applied"*.

`encoder.py` serialises `LOC` as **one of five lowercase strings** — `at_home`, `other_place`,
`private_transport`, `public_transport`, `unknown` (`D-S3-4`). The raw national code `11` is consumed
by Step 2's crosswalk and **never reaches the record**.

🔴 **`"at_home" == 11` is `False`, and it does not raise.** A schedule builder written literally to
`G7.13` produces **presence identically zero for every occupant of every dwelling**, in every country,
and the gate that is supposed to catch a wrong indoor rule is the same expression, so it agrees. This
is the failure mode Step 9's own `G9.14` names in its threshold column — *"a trigger reading an absent
column does not raise, it silently never fires"* — arriving one step earlier and in the load-bearing
direction.

**The correct rule, and it is strictly better than the code-based one:**

```
presence = (LOC == "at_home") AND (ACT not in OUTDOOR_AT_HOME)
```

`crosswalk_location.csv` row `es,11,Casa,at_home` confirms `at_home` is exactly what source code 11
maps to. **And the string is more correct than `11` ever was:** `D-S2-4` merges Italy's codes **11 and
12** into `at_home`, so a literal `LOC == 11` would silently drop part of Italian at-home time while
looking right for Spain. The class absorbs that; the code does not. `OUTDOOR_AT_HOME` is the shipped
`../Step2_docs/outputs_step2/outdoor_at_home.csv` — **four codes**, `322`, `341`, `342`, `344` — which
`G7.13` already correctly requires be read from the file *"not a copy"*.

#### 🔴 `FINDING 43` — `G7.2` demands 100 % of codes be *"inside the coding list"*. The corpus contains a code that is not in it.

`D-S3-9` emits the literal `ACT` value **`000`** for a null activity — *"the diary entry here was not a
usable activity"* — **8,709 episodes** (ES 3,786 / IT 333 / UK 4,590), from eight source codes Step 2
declined to map on purpose. `encoder.py` hard-codes it as `ACT_NULL_CODE = "000"`.

`../Step2_docs/outputs_step2/activity_target_list.csv` holds **158 target codes and `000` is not one
of them** (checked: no row matches).

**Two things follow, and the second is the damaging one.**

1. `G7.2` as written FAILs at baseline on any batch containing `000`, for a code the corpus format
   defines. That is merely wrong.
2. 🔴 **If the grammar's `ACT` vocabulary is built from `activity_target_list.csv` — the obvious
   source, and what work item 7.1 says — then the mask FORBIDS `000`.** The model was trained on a
   corpus where `000` is legal and carries real duration; at generation the mask would push every one
   of those attempts onto some *real* activity code instead. **Unusable diary time would be silently
   converted into real activity**, inflating whatever activity absorbs it, and no structural gate can see
   it: the output is perfectly well-formed. It would surface only as an unexplained lift in `G7.7`'s
   firing rate, which is *"reported, not thresholded"*.

**The grammar's `ACT` alphabet must therefore be the 158 target codes ∪ `{000}` — 159 values — and
`G7.2` must say so.** This is a declaration, not a widening: `000` is already in the frozen record
format, and refusing it at generation would make the decoder and the mask disagree about the same
corpus.

#### Path corrections, same class as Step 5's

| where | said | is |
|---|---|---|
| `G7.6`, and `../Step3_docs/4thJ_03_serialisation.md:333` | `outputs_step3/encoder.py` + `decoder.py` | **`../tools/encoder.py`** and **`../tools/decoder.py`** — both exist and are importable |

#### `D-S7-1` — for the author

| | question | recommendation |
|---|---|---|
| **(a)** 🟢 **RULED 2026-08-20 (a), APPLIED** | `G7.13`'s indoor test | 🔴 **Re-point to `LOC == "at_home"`.** Additive, no threshold moves, and it *fixes* the silent Italy 11/12 loss the code form would have caused. The gate's own "read the shipped list, not a copy" clause is unaffected. |
| **(b)** | `000` in the grammar | 🔴 **Declare the `ACT` alphabet as 158 ∪ `{000}` = 159 in work item 7.1, and amend `G7.2` to match**, before any grammar is compiled. Deciding this *after* a batch exists means deciding it while looking at a firing rate. |
| **(c)** | whether `000` episodes should reach the schedule builder at all | Genuinely open, and **separate from (b)**. `000` has a duration but no activity, so it has no internal gain and no appliance trigger. Treating it as at-home-idle, as away, or as a gap are three different annual energies. **Recommend: carry it explicitly as its own state and report how much time it is** (0.43 % of episodes) rather than folding it into any existing class. |

#### What was NOT done

No grammar compiled, no throughput comparison, no generation, nothing submitted. `outputs_step7/`
remains empty and every work item 7.1–7.7 is untouched. **`prereg.md` not touched** — md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar.

### 2026-08-20 (later) — 🟢 **WORK ITEM 7.1 IS BUILT AND ITS SELF-TEST IS GREEN, 44/44, EVERY REJECTION BRANCH SEEN FIRING. 🔴 AND IT SURFACED `FINDING 45`, WHICH IS THE LARGEST OF THE DAY: `G7.3` AS WRITTEN WOULD REJECT 28.95 % OF THE REAL CORPUS, UNEVENLY BY COUNTRY.**

Built locally — **no cluster compute, no GPU, no model.** The only cluster access was **retrieval**:
`grep` and `wc -l` over the single shipped file `/speed-scratch/o_iseri/4J_step3_corpus.jsonl`, which
is inside the login node's allowed command set. **Nothing was submitted and no generation was run.**

#### 🔴 `FINDING 45` — the transition constraint would mask nearly a third of the training distribution

`G7.3` requires **transition legality — "no workplace-to-home with no travel episode" — at 100 %,
encoded as an FSM transition table.** Two separate things are wrong with it, and the second is
measured.

**(i) The rule cannot be expressed in the record format.** `crosswalk_location.csv` maps every
non-home, non-transport place — workplace, second home, shop, restaurant, another person's house —
onto the **single class `other_place`**. **There is no "workplace" in the serialised `LOC`.** The
nearest implementable rule, `other_place -> at_home` requires an intervening transport episode, is
therefore **strictly broader** than the rule that was specified: it also forbids coming home from a
shop, from a restaurant, or from a friend's flat.

**(ii) That broader rule contradicts the data.** Measured by grep over the corpus, counting **diaries
containing at least one occurrence** (what a line-oriented grep can honestly report — it is a count of
diaries, not of transitions, and is therefore a **lower bound** on how often the mask would fire):

| | diaries with a direct `other_place → at_home`, no travel | total | share |
|---|---:|---:|---:|
| **all** | **21,210** | 73,254 | **28.95 %** |
| `es` | 8,264 | 19,140 | **43.18 %** |
| `uk` | 3,907 | 15,854 | 24.64 % |
| `it` | 9,039 | 38,260 | 23.63 % |

For scale, the *legal* form — a transport episode immediately before `at_home` — appears in 54,626
diaries (74.57 %), and the mirror transition `at_home → other_place` with no travel appears in 21,106
(28.81 %). **Both forms coexist throughout the corpus.** The direct transition is not an artefact of
one country's instrument; it is ordinary under-reporting of short trips, and every HETUS wave has it.

🔴 **What enforcing `G7.3` at 100 % would actually do.** The mask would fire on at least 28.95 % of
generated diaries and **insert travel episodes the respondents never recorded** — inventing travel
time, and in Step 9 inventing transport energy and the appliance-off period that goes with it. It
would do so **1.83× more often on Spanish diaries than on Italian ones** (43.18 / 23.63). `G7.8`
exists to catch exactly this — *"the mask propping up minority strata"*, ratio < 3.0 — **but `G7.8` is
stratified by demographic stratum, not by country, so this particular unevenness is invisible to it.**
And under LOCO, when Spain is the held-out country, that country-specific mask load lands directly on
the transfer result.

**This is the `FINDING 43` shape again, one gate over:** a constraint compiled from a source that
disagrees with the corpus, enforced at 100 %, producing perfectly well-formed output that no
structural gate can question.

#### `D-S7-2` — for the author

| | ruling | consequence |
|---|---|---|
| **(a)** | 🔴 **Recommended. Drop the travel requirement from the grammar** and keep `G7.3` as a *reported* rate rather than an enforced constraint. The corpus is the ground truth for what a plausible diary looks like, and it says this transition is normal. **Costs nothing real:** the constraint was never protecting a downstream consumer — no schedule, gain or appliance model reads the travel episode as a precondition for being home. |
| **(b)** | Enforce it, and **report the firing rate per country** alongside `G7.8`'s per-stratum rate. | Honest but expensive: it changes 29 % of diaries, the change is country-dependent, and it must then be declared as a modelling intervention in the methods rather than as "structural validity". |
| **(c)** | Enforce it only where the source data supports it. | 🔴 **Rejected.** It does not: the rate is 24–43 % in *all three* countries. There is no country where the rule holds. |

Until it is ruled, the module below **refuses to run** in the enforcing mode without an explicit
acknowledgement argument, and prints the measured rejection rates in the exception text.

#### 🟢 What was actually built

| file | lines | md5 | checked |
|---|---:|---|---|
| `../tools/4thJ_step7_grammar.py` | 286 | `53996757a17a5b2648302de3baaa0a83` | imports and runs; alphabets read live from the shipped crosswalks |
| `../tools/4thJ_step7_grammar_selftest.py` | 146 | `6b9ba5168e1f18e486007b43ff6bb644` | **44 passed, 0 failed**, run locally on Python 3.13.5 |

**Two functions that must never be the same code**, which is the whole point of `G7.10`:
`build_alphabets()` is the constraint *definition* a grammar back-end compiles from;
`validate_record()` is an independently written recogniser for the same language. `G7.10` compares
them on 10,000 strings — **if the oracle imported the grammar's own accept function, the gate would
compare a thing to itself**, the `V5.d` / `V6.b` failure class.

**Verified, not asserted:**

* **The 145-state tally automaton is returned as an explicit table** — 145 states, one accepting
  state, 10,440 transitions — so `RL12`'s regularity objection is answered by something anyone can
  count rather than by a paragraph.
* 🔴 **The multiple-of-10 premise the automaton rests on was CHECKED against the real corpus, not
  assumed.** A grep for any duration whose final digit is non-zero returned **zero diaries across all
  73,254 records** — including the UK and Italy, which ship native episodes with explicit
  start/end minutes rather than reconstructed 10-minute slots, and which were the obvious place for
  the premise to break.
* **The ACT alphabet is 158 ∪ {`000`} = 159**, per `FINDING 43`, declared in one place with its
  reason. `build_alphabets()` **raises** if `000` ever appears in `activity_target_list.csv`, so the
  union cannot silently become a duplication.
* **Every rejection branch is exercised by a case built to fire it** — 20 malformed records covering
  whitespace, a missing `<eor>`, a missing separator, 5- and 7-field prefixes, an empty prefix field,
  zero episodes, a missing terminal semicolon, 4- and 6-field episodes, a non-multiple-of-10 duration,
  a leading zero, an under- and an over-long day, an out-of-alphabet `ACT`, `ACT2` and `LOC`, an
  out-of-range and a leading-zero `COP`, and a non-string input.

🔴 **An honest note about the first run of that self-test, because it is the point of the discipline.**
It came back **6 failed**, and two of the failures were that my "invalid" test codes were **valid**:
`999` is a real target code and `99` is a real `ACT2` code. **Those two negative cases were vacuous —
they would have passed a weaker test harness while proving nothing**, exactly the `V4.f` vacuity class.
They were replaced with codes confirmed absent from the shipped lists (`120`, `10`), and only then did
the branches fire.

#### What this does NOT close

* **`G7.1`–`G7.4` still cannot fail while the mask is on.** This module makes the language explicit; it
  does not make those gates measurements. That warning stands unchanged.
* **No XGrammar grammar has been compiled and no back-end has been run**, so `G7.10`'s actual
  comparison — oracle versus XGrammar on 10,000 strings — has **not** been performed. Half of the pair
  exists.
* **The co-presence grammar variants indexed by household type (constraint class 4) are NOT built.**
  `G7.4` is untouched by this work.
* Nothing was generated, `outputs_step7/` is still empty, and no work item other than 7.1 was started.
* **`../Step6_docs/outputs_step6/prereg.md` not touched** — md5 `e4243e07cdd80c9c846b91f40e3e8c45`,
  verified against its sidecar.

### 2026-08-20 — 🟢 **`D-S7-2` RULED (a) BY THE AUTHOR: THE TRAVEL REQUIREMENT IS DROPPED FROM THE GRAMMAR.**

Ruled on the measured evidence in `FINDING 45`, the same day it was measured and **before any diary
was generated** — so no result was seen when the rule was chosen.

**The ruling.** `G7.3`'s travel requirement is **not enforced by the grammar.** `G7.3` becomes a
**reported rate**, not a 100 % structural constraint. The mask never inserts a travel episode.

**Why (a) and not (b).** (b) — enforce and declare — was the author's first inclination and is
defensible, but it accepts that ~28.95 % of generated diaries would carry travel the model did not
produce, unevenly by country (ES 43.18 % vs IT 23.63 %, `1.83×`). Under LOCO that intervention lands
hardest on exactly the fold whose transfer result is being measured. **(a) costs nothing real:** no
downstream consumer reads the travel episode as a precondition for being home — not the presence
schedule, not the internal gains, not the appliance trigger. The corpus is the ground truth for what a
plausible European diary looks like, and it says coming home without a recorded trip is ordinary.

**What still gets reported.** The rate itself, per country, as a model-quality number alongside
`G7.7`'s firing rate — because *how often the model produces a direct return home* is a real property
of the model and is now measurable against the corpus baselines (ES 43.18 %, UK 24.64 %, IT 23.63 %,
all 28.95 %).

**Consequences already handled in code.** `../tools/4thJ_step7_grammar.py` was written with
`TransitionPolicy` explicit and undefaulted for exactly this decision. Under the ruling the operative
value is **`PERMISSIVE`**; `REQUIRE_TRAVEL` stays in the module as the falsifier the self-test uses to
prove the constraint has teeth, and keeps its `acknowledge_finding_45` guard so it can never become
the operative mode by accident.

🔴 **What (a) does NOT do.** It does not claim the diaries are complete. Short trips *are* under-
reported in HETUS, that under-reporting is now inherited by the generated diaries, and it belongs in
the limitations next to the transport-energy caveat in Step 9 — **the model will under-produce travel
because the corpus does.** Enforcing the rule would have hidden that behind a mask rather than fixed
it.

---

### 2026-08-20 (evening) — 🟢 **`D-S7-1(c)` RULED: `000` IS CARRIED AS ITS OWN STATE. 🔴 AND MEASURING IT BEFORE WRITING THE RULING DOWN CHANGED WHAT IT COSTS — TWICE. THE DOCUMENT'S OWN `0.43 %` IS THE WRONG DENOMINATOR, AND `000` IS NOT "WHEREABOUTS UNKNOWN".**

**Ruled by the author 2026-08-20:** `000` reaches the schedule builder as an **explicit, distinct
state**. It is not folded into at-home-idle and not folded into away — those were the two alternatives
and each would have silently moved annual energy in a known direction. The rate is **reported**.

The corpus was then measured rather than quoted. `4J_step3_corpus.jsonl` was fetched by `scp`
(retrieval only, no cluster compute) and scored locally: **73,254 diaries, 2,024,068 episodes,
0 malformed, and every diary's durations sum to exactly 1440 — `105,485,760 = 73,254 × 1440`.**

#### 🔴 Correction 1 — the number this step has been quoting is on the wrong axis, and it is 3x too big

This document says `000` is *"0.43 % of episodes"*. That is right, and it is **not the quantity the
ruling is about**. Energy is driven by **time**, and `000` episodes are short:

| basis | value |
|---|---|
| episodes | `8,709 / 2,024,068` = **0.4303 %** |
| 🔴 **time** | `149,510 / 105,485,760` min = **0.1417 %** |
| mean duration | **`17.17` min**, against `52.12` min for the corpus as a whole |

**The state the ruling creates covers one part in 700 of modelled time, not one part in 230.** Quote
the time share; the episode share overstates the exposure by a factor of `3.04`.

🔴 **And it is strongly country-dependent, which is the axis this paper is scored on:**

| fold | `000` share of episodes | `000` share of **time** |
|---|---|---|
| `es` | 0.848 % | **0.304 %** |
| `uk` | 0.809 % | **0.245 %** |
| `it` | 0.033 % | **0.018 %** |

**`es` carries 17x more `000` time than `it`.** This is a **per-fold** quantity and pooling it would
hide the entire effect. It joins the standing list of per-fold asymmetries — the D-S6-2 wave gap,
`FINDING 39`'s rounding floor, and the census-basis gap ruled today in Step 5. 🔴 **Never report a
single pooled `000` rate.**

#### 🟢 Correction 2 — `000` means "activity unknown", NOT "whereabouts unknown". `LOC` survives.

This is the part that makes the ruling cheap, and it was not obvious from the specification. **`000`
episodes carry a real `LOC`**, and mostly a known one:

| `LOC` on `000` episodes | minutes | share of `000` time |
|---|---|---|
| `private_transport` | 64,320 | **43.02 %** |
| `at_home` | 32,320 | **21.62 %** |
| `unknown` | 29,220 | 19.54 % |
| `other_place` | 20,660 | 13.82 % |
| `public_transport` | 2,990 | 2.00 % |

🟢 **80.46 % of `000` time has a determined location.** So for four fifths of it **the occupancy
schedule is not in doubt at all** — the dwelling is known to be occupied or not. What is undefined is
narrower than the specification implied: **the internal-gain level and the appliance trigger, not the
occupancy state.**

🔴 **The genuinely irreducible residue is `0.1417 % x 19.54 % = 0.0277 % of modelled time`** — about
**one minute in 3,600** where neither the activity nor the location is known. **That, and only that,
is what a declared limitation needs to cover.** The rest is an internal-gain question with a known
occupancy answer.

🔴 **A consequence that must not be missed: the modal `000` location is `private_transport`, at 43 %.**
An implementation that reflexively treats a null activity as at-home-idle would put **43 % of `000`
time inside the dwelling while the diary says the person is in a car.** Option (b), rejected today,
would have done exactly that. **The ruling avoids a real error, not a hypothetical one.**

#### What work item 7.1 must now carry

`tools/4thJ_step7_grammar.py` already declares the `ACT` alphabet as `158 ∪ {000} = 159` and **raises**
if `000` ever appears in `activity_target_list.csv`. That is unchanged and correct. **What is added by
this ruling is downstream, in the schedule builder, not in the grammar:** a fourth state, its time
share reported **per fold** on the time basis, and the `0.0277 %` residue named as the limitation.

#### 🟢 A bonus check the same pass bought, which belongs to Step 8 and is recorded there too

**1,320 diaries — 1.802 % — have ZERO at-home minutes**: `uk` 2.927 %, `es` 1.641 %, `it` 1.417 %, a
2.1x spread. Those are dwellings with nobody home for a full modelled day. Legitimate, and it must be
a deliberate branch in the schedule builder rather than an accident. Mean at-home time is `1,028.8`
min/day, **71.4 %** of the corpus-wide time budget.

#### Still open in `D-S7-1`: items (a) and (b)

**(a) re-point `G7.13` to `LOC == "at_home"`** and **(b) declare the `ACT` alphabet as 159 and amend
`G7.2`** were recommendations with no counter-option and **neither has been ruled.** 🟢 **(a) is now
supported by measurement rather than by argument: `at_home` is `71.441 %` of corpus time**, so the
re-pointed test is abundant and non-vacuous — unlike `LOC == 11`, whose presence is identically zero
because `LOC` is a string. **`prereg.md` not touched**, md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified
against its sidecar.

---

### 2026-08-20 (execution pass) — items 9 and 10 ruled `(a)` and applied

🟢 **Item 9 — `G7.13` now reads `(LOC == "at_home") AND (ACT not in OUTDOOR_AT_HOME)`.** The old
form compared a string against the integer `11`, which is `False` for every episode ever written,
so the gate reported **presence identically zero for every occupant of every dwelling** and would
have done so while printing a clean verdict (`FINDING 42`).

🟢 **Checked against the corpus rather than assumed.** `loc_class` has exactly four values —
`at_home`, `other_place`, `private_transport`, `public_transport` — and the re-pointed rule
reproduces the shipped `indoor_presence` column on all **2,022,141** episodes that carry an
activity: `1,352,977` indoor, with `10,436` at-home-but-not-indoor episodes that are exactly the
four `OUTDOOR_AT_HOME` codes `322`, `341`, `342`, `344`. The gate's "read the shipped list, not a
copy" clause is untouched, and so is its threshold.

🔴 **And the check found something the ruling does not mention: the rule is not defined for the
null activity.** `1,927` at-home episodes carry a NULL `act` (ES 290 / IT 105 / UK 1,532). The
shipped `indoor_presence` is `NA` for exactly those, while `ACT not in OUTDOOR_AT_HOME` is
vacuously true and returns **PRESENT**. In generated text the case arrives as `000`, which
`D-S7-1 (c)` ruled is a state in its own right, and a person at home doing an unrecorded activity
**is** present — so PRESENT is the right answer. 🟢 **But it is an answer, not an accident of the
`not in` operator, and it is now written into the gate's own row.** ⚪ The affected share is
country-skewed (`uk` carries `79 %` of them), which is why it is recorded rather than waved past.

🟢 **Item 10 — the `ACT` alphabet is declared as 159.** Re-derived from the shipped file:
`activity_target_list.csv` holds **158 rows, 158 distinct `target_code`s, and `000` is not one of
them**. `000` is the pre-registered null activity (`D-S3-9`, 8,709 episodes), so a grammar built
from that file alone would forbid a code the corpus itself defines. The alphabet is
`158 ∪ {000} = 159` in `G7.2`, `G7.10` and the grammar construction.

⚪ **This ruling records what the code already does.** `tools/4thJ_step7_grammar.py` declares the
union in the module itself, at the point of construction, and its selftest is green at 44/44. The
documents were the things out of step, and they are now in step.

🔴 **Neither gate has been RUN.** `G7.13` has no implementation yet — it is specified, not built —
and `G7.10` still has no XGrammar back-end. Nothing here is a verdict about the model.

---

### 2026-08-21 — 🟢 **`G7.13` IS BUILT. IT WAS THE ONE GATE IN THIS STEP THAT WAS SPECIFIED AND NOT IMPLEMENTED, AND `FINDING 42` IS NOW A REGRESSION TEST RATHER THAN A MEMORY.**

`tools/4thJ_step7_indoor.py` + `tools/4thJ_step7_indoor_selftest.py`. **36 of 36 green.** Local, no
cluster, no model, no generated batch.

The 2026-08-20 entry closed with *"`G7.13` has no implementation yet — it is specified, not built"*.
It is built.

#### What it implements, exactly as `D-S7-1` item 9 (a) ruled it

    presence  <=>  (LOC == "at_home")  AND  (ACT not in OUTDOOR_AT_HOME)

reading the exclusion list **live** from `Step2_docs/outputs_step2/outdoor_at_home.csv` — the four
`D-S2-4` garden codes `322`, `341`, `342`, `344`, md5 `679518c7f626bd5d408adc96b5a1ff43`. The module
carries **no literal copy of a code**, and the selftest asserts that by grepping its own source.

#### 🔴 The three guards, each exercised rather than asserted

* **`V7.c` — the pre-registered perturbation lands.** The gate re-reads the shipped file itself and
  FAILs if the caller's set differs by so much as one code. Tested in both directions: one code
  removed, one code added. A missing shipped file **raises** rather than falling back to a copy,
  because there is deliberately no copy to fall back to.
* 🔴 **`FINDING 42`'s signature is refused by construction.** A presence signal that is CONSTANT —
  all-absent or all-present — FAILs. That is the exact shape the old `LOC == 11` produced: a string
  compared against an integer, silently `False` for every episode ever written, **presence identically
  zero for every occupant of every dwelling**. A building with nobody in it never fails a schedule
  gate; it fails the paper. The selftest reproduces the old form and shows it matching **0 of 9**
  episodes of a normal batch while the new form matches a non-zero number of the same episodes.
* **An empty batch FAILs rather than skipping** (`V5.b`'s argument), as does a batch in which no
  episode is `at_home`, because then the activity half of the rule was never reached.

#### The two readings written down rather than left to an operator

1. **`000` at home is PRESENT.** `D-S3-9`'s null activity, made its own state by `D-S7-1 (c)`. A person
   at home doing an unrecorded activity is inside the conditioned volume. It is counted **separately**
   in the gate's report so the reading is visible in every run, not inferred from a `not in`.
2. **`LOC` unknown is NOT at home.** The decoder returns `None`; an unknown location is not evidence of
   presence, and reading it as one would inflate every schedule in the direction that flatters the
   paper.

⚪ A record whose durations do not sum to 1,440 is **refused, never padded** — a short diary padded to
a day is an occupancy dip nobody would ever trace back to here.

#### 🔴 What has NOT been shown

**`G7.13` has never been run against real records.** The 36 selftest cases are hand-built dicts. The
corpus-level agreement quoted in the module docstring — reproducing the shipped `indoor_presence`
column on all 2,022,141 episodes carrying an activity, differing on 1,927 at-home `NULL`-act episodes
— is **the validation document's measurement of 2026-08-20, quoted and attributed, not re-derived
here**; the corpus is on Speed and was not fetched. Running it over the corpus, and then over a
generated batch, is owed.

⚪ `G7.10` still has no XGrammar back-end, unchanged.


---

### 2026-08-21 (late afternoon) --- 🟢 **`G7.13` HAS NOW BEEN RUN AGAINST THE REAL CORPUS, AND SEEN FAILING TWICE. IT WAS 36/36 GREEN ON FIXTURES ONLY UNTIL TODAY.**

`tools/4thJ_step7_g713_corpus.py`. All 73,254 Step 3 records decoded through the SHIPPED
`tools/decoder.py` and put through the SHIPPED `tools/4thJ_step7_indoor.gate_g7_13()`. **No rule is
implemented in the new module**; it only supplies data and perturbations.

```
73,254 records decoded, 0 refused
exclusion list  ['322', '341', '342', '344']  md5 679518c7f626bd5d408adc96b5a1ff43  SHIPPED
episodes        2,024,068
minutes present 74,826,850 / 105,485,760
presence share  70.9355 %
at_home eps     1,365,340   excluded 10,436  {341: 7125, 342: 1657, 322: 1147, 344: 507}
null act (000)  1,927  counted PRESENT by declaration
verdict         PASS
```

🟢 **The 1,927 figure the Step 7 validation document quoted on 2026-08-20 is now
RE-DERIVED rather than repeated, and it matches to the diary: ES 290 / IT 105 / UK 1,532.** That
number had been carried as a quotation with a note saying the module had never seen a corpus. It has
now.

#### Per country, because `FINDING 53` says anything country-correlated is read per fold or not at all

| fold | records | presence | at_home episodes | excluded | null act at home |
|---|---:|---:|---:|---:|---:|
| `es` | 19,140 | 69.5667 % | 304,849 | 1,704 | 290 |
| `uk` | 15,854 | 69.6524 % | 384,614 | 3,883 | 1,532 |
| `it` | 38,260 | 72.1519 % | 675,877 | 4,849 | 105 |

⚪ A 2.59 pp spread in presence across the three folds, with Italy highest. Read alongside
`FINDING 53`: the day bases differ per country too, and both effects move at-home time in the same
direction for `it`.

#### 🔴 Both perturbations FAILED, which is the only part of this that proves anything

* **`V7.c`, the pre-registered one.** The same corpus re-run with an exclusion list differing by
  exactly one code (`322` removed from the caller's copy): **FAIL**, naming the missing code. A gate
  that passed here would be validating against a copy of the list instead of the shipped one.
* **The vacuity guard.** A batch of 50 all-day at-home records: **FAIL**, "presence is identically
  PRESENT across every record". That is `FINDING 42`'s signature refused by construction.

`G7.13` is therefore seen passing on real data and seen failing for two different reasons. 🔴 It has still never been run against a GENERATED batch, which is the case that matters
for the paper and which needs a fold checkpoint.

#### ⚪ Unchanged

`G7.10` has no XGrammar back-end. `FINDING 45` stands: enforcing `G7.3` would reject 28.95 % of the
corpus, and `LOC` has no workplace class. The ACT alphabet is 159.
