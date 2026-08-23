# Step 7 — Constrained generation at scale, and schedule production

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 7. Validation: `4thJ_07_constrainedGeneration_val.md`

---

## STATUS

**OPEN.** Mechanism decided by `RL12`. 🔴 **The words *"Nothing built"* stood here until 2026-08-22
and had been false for eight days** — the progress log below carries fifteen entries of built and run
work. Corrected rather than quietly replaced.

| work item | state as of 2026-08-22 (night) |
|---|---|
| **7.1** compile the grammar | 🟢 **BUILT**, selftest 51/51, `.ebnf` md5 `bb4208dd99794c3b52bdead0608d7fad`, `G7.10` PASS on 10,000 strings under the 34-value `COP` alphabet |
| **7.2** throughput comparison | 🟢 **RUN** — job `1286208` COMPLETED 00:06:55. Diaries/second measured (**OLMo 0.835x Qwen**, not the predicted large penalty). 🔴 `G7.12` STILL FAILS: the KV-memory half is 3.05x the physical card (`FINDING 97`) |
| **7.3** generate | 🟡 Leg-4 rehearsal done on all three folds, both arms. **Leg 5 is job `1286209`, PENDING** |
| **7.4** three-model firing-rate report | 🟡 fine-tuned constrained and unconstrained measured; the **untuned-base arm needs a GPU** |
| **7.5** rejection-sampled control | 🔴 sized (≈22,500 / 8,800 / 15,700 draws) and deliberately **not submitted** while `1286209` is PENDING on `AssocGrpGRES` |
| **7.6** chaining rule (decision 14) | 🟡 DoD items **3 and 4 done** on CPU; items 1, 2, 5 and `G7.18`'s verdict need EnergyPlus. **DECISION 14 IS OPEN** |
| **7.7** emit schedules | 🟢 **EMITTER BUILT** (selftest 52/52) and `G7.13`–`G7.17` scored 5 PASS / 0 FAIL on all three folds, all five seen falling. 🔴 The **campaign** is not run: every diary is `LEG-4 PILOT -- NOT REPORTABLE` |

🔴 **Everything Leg-4 is from `allenai/OLMo-2-0425-1B`, not the reported `Olmo-3-1025-7B`. No Leg-4
number is a result.** Work items 7.6 and 7.7's CPU half is recorded in full in
**`4thJ_07_schedules_and_chaining_IMP.md`**.

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
* 🟢 **Internal gains are OCCUPANCY-REDISTRIBUTED, not activity-resolved.** *(`D-S7-7` ruled **(a)** by the author, 2026-08-22, closing `FINDING 94`. This line previously read
  "activity-resolved internal gains, which is the part a presence fraction throws away", which contradicted the ruled Step 8 interface. That interface is `D-S8-2` item 5:
  `phi_int(t) = (1-f)*3.0 + f*3.0*g(t)/mean_year(g(t))`, with `g(t)` the generated presence signal from `G7.13` — **a fraction, not a watt**. Resolving a 3-digit HETUS code into a power needs a
  mapping and there is no admissible one: `RL25` was commissioned for exactly that and its Part C figures were rejected as unsourced, so writing one here would put an invented number between our
  diaries and every load in the paper. The emitter keeps each pool day's activity codes beside the presence signal, so the mapping can be applied later without a GPU run. 🔴 **The methods owe
  one sentence saying the gains are occupancy-redistributed and NOT activity-resolved.**)*
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

🟢 **RULED 2026-08-22 — open decision 14 closes in STEP 8, on `G7.18`.** The author ruled option **(a)**: the CPU pre-screen is a screen and not the decision. It returned this document's own
pre-registered null on every coincidence metric a peak-demand screen is made of (seed noise dominates `mean_pair_corr` on all three folds; `peak_aggregate` and `p99_aggregate` are degenerate at 1.000 on
`es` and `it`), and the one axis on which the rules separate decisively — activity vocabulary, ratios 18.17 / 11.89 / 18.36, and same-day-type Jaccard 71.64 / 64.50 / 63.77 — is the one axis with
**no empirical reference anywhere in this project** (`FINDING 96`: ISTAT and Spain give one diary day per respondent; the UK's second day is a weekend day in 99.7 % of cases). Decision 14 therefore
closes on the quantity its trigger is defined on, which is a **watt**. Sizing, fixed here as arithmetic from `G7.18`'s own registration: **one archetype per fold, one `f` level, 3 rules × 5
seeds × 100 dwellings = 1,500 dwelling-years per fold**, 4,500 across three — **independent of** the 510-archetype `f`-sweep, since one archetype and one `f` are held fixed.

⚪ **Interim convention until then: `independent`, seed 1** — the rule the three baseline schedule cells on disk already use. It is a **placeholder, not an adopted rule**, and nothing downstream has
committed to it.

🔴 **Owed before any pre-screen verdict reaches the paper, and it needs no ruling:** every number in the pre-screen comes from 600-diary Leg-4 pools on a 1B backbone, whose back-off ladder
serves four days in ten from a stratum coarser than the person's own (`es` 57.79 / `uk` 62.33 / `it` 63.52 % full depth). The vocabulary ordering would survive a bigger pool; **the seed-noise
verdicts might not**, because a larger pool narrows the within-rule spread and could turn a coincidence metric from "tells us nothing" into a real effect. **Re-run the pre-screen at Leg-5's
`N >= 5,200` and re-measure the back-off ladder rather than assuming it improved.** CPU-only, minutes.

🟢 **RULED 2026-08-22 — `D-S7-6`, the household basis: option (a), surveyed composition, declared per fold.** The 100 households this item runs on come from the **real corpus** (`hid`/`pid`),
because `population_<c>.csv` is a 100,000-row **person** table with no household identifier (`FINDING 93`) and `D-S5-9` settled household type on a person basis without ever assembling a
dwelling. Re-opening Step 5 to draw households (option b) would invalidate `population_*`, `prefixes_*` and every `G6.1` null raked onto them; grouping synthetic persons post hoc (option c)
would manufacture a joint distribution nothing measured. 🔴 **The declaration is specific, and it is not "surveyed households":** `FINDING 98` measured that a `hid` group is the household members
who **kept a diary**, not the household — **13.50 % (`es`) / 12.37 % (`uk`) / 2.98 % (`it`)** of groups are multi-person households represented by a single diarist, a **4.5× country-correlated
spread**, and `couple_with_children` runs on one diarist in **10.50 / 11.96 / 1.58 %** of cases. So the co-presence half of `G7.4` sees partners and children who have no day at all, and every
household-level quantity (`mean_pair_corr`, `trough_aggregate`, co-presence) is measured on **the diarist members of surveyed households** and is read **per fold or not at all**. That row joins
the paper's asymmetry table beside `FINDING 53`, `D-S6-2`, `FINDING 51` and `FINDING 60`.

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

`Schedule:File`, `Interpolate to Timestep = No`, indoor rule applied, **the presence signal carried** — occupancy-redistributed gains per `D-S8-2` item 5, **not** activity-resolved (`D-S7-7` (a), 2026-08-22).

🟢 **The schedule calendar year** (`D-S7-8`, ruled **(a)** by the author, 2026-08-22): **a schedule runs on the first calendar year of whatever twelve-month weather window `D-S8-2`
item 6 fixes**, and the schedules are re-emitted (CPU-seconds) once that window is known. The rule previously recorded — *"the non-leap year of each survey pair"* — is **struck**: none of the
six candidate years (2009, 2010, 2013, 2014, 2015) is a leap year, so it discriminated nothing, and all six are identical in composition (365 d / 261 weekdays / 52 Saturdays / 52 Sundays). What the year changes is the **ordering** — which calendar date is a Saturday — which is inert while
the schedules stand alone and becomes a basis choice the moment an actual-meteorological-year file is attached: the schedule's weekends must land on the weather's weekends, or the campaign pairs a
synthetic Sunday with a real Tuesday for fifty-two weeks. The cells currently on disk (`es` 2010, `uk` 2014, `it` 2013) are **pilot cells emitted before the rule existed** and are superseded by it.

🔴 **`FINDING 99` — the ruled alignment holds exactly when the window is a CALENDAR year, and nothing yet says it will be.** `D-S8-2` item 6 fixes *twelve consecutive months*, not necessarily
January–December. If the window straddles two calendar years (say July 2013 – June 2014), a schedule emitted on calendar 2013 aligns with the weather for its first six months and is off by one
or two weekdays for the rest — so "the first calendar year of the window" delivers the intended weekend coincidence only for a January-start window. Two further consequences of a straddling window:
a twelve-month span containing 29 February is **8,784 hours**, which `year_day_types()` refuses outright and which no `Schedule:File` in this project accepts; and the emitter takes a `--year`
parameter but has **no window-start parameter**, so a straddling window would need an additive change to `tools/4thJ_step7_schedules.py` before it could be honoured at all. ⚪ This needs no ruling now —
it is a **constraint on `D-S8-2` item 6**: prefer a calendar-year window, or accept that the schedule/weather weekday alignment is partial and say so.

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
6. Open decision 14 closed with a written reason. ⚪ **Discharged in STEP 8** by `G7.18`, per the author's ruling of 2026-08-22 (option (a)) — this item cannot close inside Step 7.
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

---

### 2026-08-22 — 🟢 **`G7.10` IS RUN AND PASSES. THE GRAMMAR SIDE OF THE GATE DID NOT EXIST BEFORE TODAY; ONLY THE HAND-WRITTEN ORACLE DID, AND A GATE CANNOT COMPARE A THING TO ITSELF.**

Executed under `D-S7-3` (a), directives 1 and 2. Job `1286176`, partition `ps`, **no GPU** — XGrammar
compiles and matches on the CPU and neither recogniser involves a model, which is why `G7.10` is the
one Step 7 gate settleable before a single diary is generated.

#### What was missing

`G7.10` reads *"an independently written recogniser for the same language accepts and rejects
identically."* Work item 7.1 shipped one recogniser: `4thJ_step7_grammar.py`, the hand-written oracle,
44/44 green on 2026-08-20. The second recogniser was never written. Until today the gate had nothing
to compare against, and the note above recorded it honestly as **"no XGrammar back-end."**

#### The environment, first

`/speed-scratch/o_iseri/envs/step7` built by `tools/4thJ_step7_env_build.sh` (md5
`dd8a1bb568e6e699720d6668e9513442`), job `1286173`, from `envs/step4`'s interpreter. Nothing pinned.
Approved by the author as the sub-question of `D-S7-3`. **`envs/step4` is untouched and was verified
so afterwards** — its torch still reports `2.5.1+cu121`.

#### The two new artefacts

| file | md5 | what it is |
|---|---|---|
| `tools/4thJ_step7_ebnf.py` | `164ca6dae8a66da70bfa0306f0efbce4` | emits the EBNF; **never imports the oracle** |
| `tools/4thJ_step7_ebnf_selftest.py` | `fe29725a404d70512e92019b4b528d04` | 43 checks, **43 ok / 0 FAILED** |
| `tools/4thJ_step7_g710.py` | `351c446ca5869a63c454fe8e4ec46431` | the gate runner |
| `outputs_step7/step7_grammar.ebnf` | `65aae7cb4f48ebb495f449ae91bcfd50` | 115,046 chars, 296 rules |
| `outputs_step7/g710_oracle_agreement.json` | `7d345798faa29b0f5f2ff95841c4eb69` | the verdict |

#### The 145-state claim is now COUNTED, not asserted

The self-test walks the emitted text rather than trusting the generator: **144 duration rules
`E1`..`E144`**, `E1` spelling `10` and `E144` spelling `1440`; **144 tally states `S0`..`S143`**, with
`S144` never defined anywhere in the file because a day that has reached 1440 ends on a bare `E`, not
on a state; every alternative checked to advance the tally by exactly its own duration; and
**10,440 transitions** in total. Alphabets are read live off the crosswalks, not hardcoded: ACT 159
(158 shipped + `000`), ACT2 43, LOC 5, COP 65.

#### The verdict

**PASS — 0 disagreements on 10,000 strings**, 5,000 accepted by both and 5,000 rejected by both,
matched in 576.9 s. XGrammar 0.2.3; entry point `xgrammar.testing._is_grammar_accept_string`; policy
`permissive` per `D-S7-2` (a). Nineteen mutator classes plus `valid`, each ~263 strings, **every one
of them zero-disagreement and none of them vacuously accepted**: `bad_act`, `bad_act2`, `bad_loc`,
`cop_leading_zero`, `cop_range`, `day_long`, `day_short`, `dur_leading_zero`, `dur_not_mult10`,
`episode_long`, `episode_short`, `no_bar`, `no_eor`, `no_terminal_semi`, `prefix_empty`,
`prefix_long`, `prefix_short`, `whitespace`, `zero_episodes`.

🔴 The negative codes are **computed, not guessed**. `_out_of_alphabet()` searches the alphabet for a
code that is provably absent and **raises** if none exists — a full alphabet cannot silently yield a
"bad" code that is actually legal. `999` is not assumed to be free.

#### 🔴 The perturbation that mattered, and the two checks that were wrong before it

Five perturbations were run against the module. **P3 — make the grammar import the oracle — SURVIVED
at 42 ok / 0 FAILED.** The independence check read `"validate_record(" not in body`, so a perturbation
that *bound* the oracle without calling it (`validate_record = _grammar.validate_record`) walked
straight past. That is precisely the `V5.d` / `V6.b` self-comparison failure the gate exists to
prevent, and it was invisible. The substring fix then failed on the **unperturbed** module, because a
comment in `build_ebnf` names the function.

The check now parses the **syntax tree** (`ast.walk`) and requires two things: no identifier named
`validate_record` or `tally_step` anywhere in the module, and — the positive form — every attribute
pulled off `_grammar` must be in a constant allowlist. `build_alphabets` is shared deliberately, since
it is the constraint definition both sides compile from, but it is called by the caller and never
reached through the grammar module. With that, **5 of 5 perturbations fell, each hitting only its own
target.**

⚪ A smaller one worth recording: the harness restored the module with CRLF line endings and silently
changed its md5. It now writes back in binary.

#### 🔴 What `G7.10` does NOT establish

It compares two recognisers **on strings**. It says nothing about whether vLLM's decoder actually
honours the mask at generation time — that is items 7.3 and 7.5, on generated text, and it is still
owed.

---

### 2026-08-22 (afternoon) — 🟡 **THE `envs/step7` INFERENCE STACK TOOK THREE FIXES TO COME UP, AND THE FIRST TWO ARE THE SAME BUG WITH TWO DIFFERENT GUARDS. `FINDING 79`.**

`G7.10` needed no GPU and no model, so it passed on a stack that had never actually served a token.
The first generation run is what exercised vLLM's engine, and it failed three times before the engine
reached the sampler. All three fixes are **additive and confined to `envs/step7`**; `envs/step4` was
re-checked after each and still reports torch `2.5.1+cu121`.

#### 🔴 `FINDING 79` — `flashinfer` cannot be imported on Python 3.10, and vLLM reaches it two ways

`envs/step7` was created from `envs/step4`'s interpreter, so it is **Python 3.10.20**.
`flashinfer/comm/fd_exchange.py:55` annotates a return type as `tuple[tuple[int, int, array.array[int]]]`,
and `array.array` only became subscriptable in Python **3.12**. The annotation is evaluated at module
scope, so the import dies with `TypeError: 'type' object is not subscriptable` — not at call time, at
import time, unconditionally.

| Attempt | Job | What it did | How it failed |
|---|---|---|---|
| 1 | `1286177` | nothing — first run | `TypeError: 'type' object is not subscriptable`, via `allreduce_rms_fusion.py:90` |
| 2 | `1286185` / `1286186` | `pip uninstall -y flashinfer-python` | `ModuleNotFoundError: No module named 'flashinfer'`, via `topk_topp_sampler.py:51` |
| 3 | `1286187` | `export VLLM_USE_FLASHINFER_SAMPLER=0` | got past the sampler; died later in dynamo |
| 4 | `1286189` | `enforce_eager=True` | engine up in 76.8 s |

🔴 **The uninstall was necessary and not sufficient, and the reason is worth writing down.** vLLM
reaches flashinfer through **two** different code paths with **two different guard styles**:

- `vllm/compilation/passes/fusion/allreduce_rms_fusion.py` asks `find_spec("flashinfer.comm")` and
  skips the pass when the module is absent. That path is **guarded**, so removing the package fixes it.
- `vllm/v1/sample/ops/topk_topp_sampler.py:flashinfer_sampler_supported()` does a **bare**
  `from vllm.v1.attention.backends.flashinfer import FlashInferBackend` with no guard at all. Its
  docstring says so in as many words: *"Assumes flashinfer is installed, as guaranteed by
  `requirements/cuda.txt`."* Removing the package therefore converts one crash into another.

The function does return `False` **before** that import when `VLLM_USE_FLASHINFER_SAMPLER` is `0`, so
the wrapper now exports it. Nothing is installed, nothing is pinned, and the log carries the proof:
`INFO topk_topp_sampler.py:46] FlashInfer top-p/top-k sampling disabled via VLLM_USE_FLASHINFER_SAMPLER=0.`

#### 🟡 `torch.compile` is OFF, and the reason is the same shared-interpreter arrangement

With the sampler settled, the fourth failure was `AssertionError: Source mismatch for collections.abc
(line 828-835)` inside `torch/_dynamo/package.py`. The venv's **site-packages** are under
`envs/step7` but its **stdlib** is under `envs/step4/lib/python3.10` — visible in the traceback itself,
which walks through `/speed-scratch/o_iseri/envs/step4/lib/python3.10/contextlib.py`. Dynamo hashes
the source of the stdlib modules it traces and refused the mismatch.

`4thJ_step7_generate.py` now passes `enforce_eager=not a.compile`, default eager, with `--compile` kept
as an opt-in. ⚪ **This is a speed setting, not a sampling one** — eager and compiled graphs draw from
the same distribution with the same seed, so no rehearsal or campaign number depends on it. It is
recorded here anyway, because item 7.2 is a **throughput** comparison and any timing measured in this
environment is an eager-mode timing and must be labelled as such.

#### What the failed runs established before they died

Two facts the smoke test existed to check were already visible in the logs of runs that crashed later:

- `structured : structured_outputs=StructuredOutputsParams(grammar=...)` — this build takes the
  grammar through `StructuredOutputsParams`, not the older `GuidedDecodingParams`.
- `INFO model.py:645] Resolved architecture: Olmo2ForCausalLM` — 🔴 **and this corrects something this
  session had repeated.** `Step4_docs/4thJ_04_finetuneLLM.md:96` is read as saying vLLM has no OLMo
  support; it has. `ModelRegistry.get_supported_archs()` on this build returns eight OLMo
  architectures including `Olmo2ForCausalLM` and `Olmo3ForCausalLM`. The `D-S7-3` ruling does not
  depend on this — it rests on the downstream gates never having run on generated text — but the
  throughput half of the argument was weaker than it was presented.

---

### 2026-08-22 (afternoon, second entry) — 🔴 **THE FIRST CONSTRAINED BATCH CAME BACK 0 OF 16 VALID, AND THE CAUSE IS THE ONE THING `G7.10` WAS WRITTEN TO SAY IT COULD NOT SEE. `FINDING 80`.**

Job `1286189`, 16 diaries, fold `es`, Leg-4 adapter, mask on. The engine came up, the LoRA loaded
(`Loading LoRA weights trained with rsLoRA`), 16 diaries were generated in 47.0 s — and **not one was
valid**. Every rejection carried the same reason, `does not end with <eor>`, `n_terminated 0 / 16`,
and every record's `finish_reason` was `length` at exactly `1200` tokens.

The script's own guard fired, in the words it was written in:

> 🔴 THE MASK WAS ON AND 16 RECORD(S) ARE STILL INVALID. Either the grammar does not say what the
> oracle says, or vLLM did not apply it. Do not score this batch.

#### 🔴 `FINDING 80` — the mask was applied, correctly, to the wrong root

Neither of the guard's two hypotheses is what happened, and the third possibility is worse than both
because it is silent. Counting delimiters in the 16 generated bodies settles it:

| | measured |
|---|---|
| commas in the generated body | **exactly 5**, in all 16 |
| `\|` in the generated body | **0**, in all 16 |
| `;` in the generated body | 0 |

That is not unconstrained text. A free-running model trained on this corpus emits hundreds of commas
and semicolons. **The mask was on and it was obeyed exactly.** It was simply matching a different
production from the one intended.

`root ::= PF "," PF "," PF "," PF "," PF "," PF "|" S0 "<eor>"` describes the **whole record**. But
vLLM constrains the **completion**, and at generation time the six prefix fields and the `|` are
already in the *prompt*. So the matcher was started at the top of `root` and handed the first
generated character. It therefore read the episodes as **prefix fields** — and

```
PF     ::= PFCHAR | PFCHAR PF
PFCHAR ::= [0-9a-zA-Z_+-]
```

accepts any non-empty run of letters, digits, `_`, `+` and `-`. `180`, `011`, `82`, `at_home` are all
legal `PF`. So are `6-faced` and `733etrueAnnotationalledat_home_bounds_g1`. The model consumed its
five commas, entered the **sixth and last** `PF` — which is unbounded — and stayed there for the
remaining ~1,100 tokens, never reaching the `|` that would have let the day begin.

🔴 **A grammar that constrains nothing looks exactly like a grammar that was ignored.** The only
reason this was caught in fifteen minutes rather than after the campaign is that the batch was piped
through the independent oracle immediately and the script refuses to file an invalid constrained batch
quietly.

#### What this says about `G7.10`, and it is not that `G7.10` was wrong

The previous entry closed with the sentence *"It compares two recognisers on strings. It says nothing
about whether vLLM's decoder actually honours the mask at generation time — that is items 7.3 and 7.5,
on generated text, and it is still owed."* That was written before this run and it is exactly what
happened. `G7.10` compared the two recognisers **on whole records**, where both are right; the defect
lives in the *seam* between the grammar and the decoder, which no string-level gate can reach.

⚪ **`G7.10`'s verdict is untouched.** The gate is not re-run and its artefact is not rebuilt.

#### The fix, and it is additive

`build_ebnf(alphabets, whole_record=True)` gains a parameter. `True` — the default — emits the
whole-record root, byte for byte what it emitted before: the regenerated text still hashes to
**`65aae7cb4f48ebb495f449ae91bcfd50`**, the md5 of the `step7_grammar.ebnf` that `G7.10` scored, and
`4thJ_step7_ebnf_selftest.py` is still **43 ok, 0 FAILED**. `False` emits

```
# ROOT: COMPLETION ONLY. The prefix and its "|" are in the prompt.
root ::= S0 "<eor>"
```

and omits `PF` and `PFCHAR` entirely, so the failure mode cannot reappear by accident: with no `PF` in
the grammar there is nothing permissive for a mis-rooted matcher to fall into. `4thJ_step7_generate.py`
now asks for `whole_record=False`; **the oracle and `G7.10` keep the whole-record root**, because the
record they validate really does include the prefix.

⚪ The two roots are now a thing the paper has to be honest about: the language is defined on whole
records, and what the decoder is masked with is its suffix. They are the same language given the
prompt, and the oracle checks the whole record afterwards, which is what makes the claim checkable.

---

### 2026-08-22 (evening) — 🟢 **THE FIX HOLDS, ALL THREE FOLDS ARE GENERATED BOTH WAYS, AND THE STEP 7 GATE BATTERY EXISTS AND HAS BEEN RUN ON GENERATED TEXT FOR THE FIRST TIME. 🔴 IT RETURNED `FINDING 81`, `FINDING 82` AND `D-S7-4`.**

The previous entry ended with a fix and no evidence. This one has the evidence, and then it has the
three things the evidence exposed.

#### 🟢 `FINDING 80` is closed by demonstration, not by argument

Job **1286191**, the same 16-prompt smoke test that returned 0 of 16, returned **16 of 16 valid and
16 of 16 `<eor>`-terminated** against the completion-rooted grammar. Nothing else changed.

#### 🟢 The Leg-4 rehearsal campaign, six jobs, `N = 600` per fold per arm

| fold | arm | job | diaries/s | valid by the oracle | `<eor>` |
|---|---|---|---|---|---|
| `es` | constrained | 1286195 | 15.76 | **600 / 600 (100.00 %)** | 600 / 600 |
| `es` | `--no-grammar` | 1286196 | 23.03 | **16 / 600 (2.67 %)** | 600 / 600 |
| `uk` | constrained | 1286197 | 13.50 | **600 / 600 (100.00 %)** | 600 / 600 |
| `uk` | `--no-grammar` | 1286198 | 19.49 | **44 / 600 (7.33 %)** | 600 / 600 |
| `it` | constrained | 1286199 | 12.87 | **600 / 600 (100.00 %)** | 600 / 600 |
| `it` | `--no-grammar` | 1286200 | 13.80 | **24 / 600 (4.00 %)** | 600 / 600 |

🔴 **`LEG-4 PILOT -- NOT REPORTABLE`**, stamped inside every record by the generator itself. Eager
mode throughout (`FINDING 79`), on a `nvidia_a100_2g.20gb` slice, so the diaries/s figures are floors.

Two readings, and only one of them is comfortable.

🟢 **The model has learned to stop.** `600 / 600` terminated with `<eor>` in **every arm, including
unconstrained**. That is not a masking artefact — with the mask off nothing forces termination — and
it is the clearest single piece of evidence in Step 7 so far that the fine-tune took.

🔴 **`G7.5` FAILS on all three folds, and by a very long way.** Unconstrained well-formedness is
**2.67 % / 7.33 % / 4.00 %** against a pre-registered **≥ 99.90 %**. This is the one Tier-3 gate that
measures the model rather than the harness, and on the 1.48 B pilot it says the model cannot produce a
valid diary on its own. The failure modes are arithmetic, not vocabulary — `durations sum to 1310
minutes, not 1440`, `duration 270 is not a positive multiple of 10`, `episode 9 has 6 fields` — which
is exactly the class of error the tally automaton exists to remove. **This is a pilot number and it is
the reason `D-S7-3` (a) made Leg 4 a rehearsal**, but it is also the first honest measurement of the
backbone and it must be re-taken on Leg 5 before anything is said about it in the paper.

#### 🟢 `tools/4thJ_gates_step7.py` — the battery, and it reads generated text

`G7.1`–`G7.13`, all three folds, artefacts `outputs_step7/gates_step7_leg4_baseline.json` and
`outputs_step7/gates_step7_leg4_perturbations.json`. Board over **SCORED** gates only:
**12 PASS / 15 FAIL** across three folds.

| gate | `es` | `uk` | `it` | reading |
|---|---|---|---|---|
| `G7.1` tally | PASS | PASS | PASS | 🔴 ENFORCEMENT CONFIRMATION, excluded from any tally |
| `G7.2` alphabet | PASS | PASS | PASS | 🔴 ENFORCEMENT CONFIRMATION, excluded |
| `G7.3` direct return home | 45.00 % | 46.00 % | 57.17 % | REPORTED RATE (`D-S7-2` (a)); corpus 43.18 / 24.64 / 23.63 |
| `G7.4` co-presence | **FAIL** | **FAIL** | **FAIL** | `FINDING 81` |
| `G7.5` unconstrained | **FAIL** | **FAIL** | **FAIL** | 2.67 / 7.33 / 4.00 % |
| `G7.6` round-trip | PASS | PASS | PASS | `FINDING 82` — a third confirmation, not a measurement |
| `G7.7`/`G7.8` firing rate | **FAIL** | **FAIL** | **FAIL** | `V7.a` unsatisfiable at `N = 600` |
| `G7.9` renormalisation | **FAIL** | **FAIL** | **FAIL** | the control is 16 / 44 / 24 diaries |
| `G7.10` oracle agreement | PASS | PASS | PASS | read from its own job's artefact, not re-scored |
| `G7.11` no silent discard | PASS | PASS | PASS | 600 requested, 600 on disk |
| `G7.12` throughput recorded | **FAIL** | **FAIL** | **FAIL** | 🔴 job 1286208 RETURNED and the gate STILL fails — no valid peak-KV value exists (`FINDING 97`) |
| `G7.13` indoor rule | PASS | PASS | PASS | 🔴 first run ever on GENERATED records |

🟢 **`G7.13` on generated text at last.** The 2026-08-21 entry closed with *"it has still never been
run against a GENERATED batch, which is the case that matters"*. It now has. Presence share
**73.11 % / 67.43 % / 69.35 %** of the day, the shipped exclusion list (md5
`679518c7f626bd5d408adc96b5a1ff43`) imported not copied, and the `FINDING 42` vacuity signature —
constant presence — refused in both directions. `it` is the only fold whose generated batch contains
`000` at home at all (9 episodes), counted PRESENT by the `D-S7-1` (c) declaration.

#### 🔴 `FINDING 81` — `G7.4` is not an enforcement confirmation in this build, and it FAILS

Work item 7.1 asks for *"household-indexed co-presence variants"* and the validation document lists
`G7.4` among the four gates that *"cannot fail while the mask is on"*. **Both assume a grammar that
does not exist.** `4thJ_step7_ebnf.py` compiles **one** grammar whose `COP` alphabet is the full
`0..64`, so nothing prevents the model asserting a household member the household does not contain.

Scored on the 600-diary batches — the rule is **membership**, never behaviour, and
`cop_other_persons` (people from outside the household) is never constrained:

| fold | episodes checked | diaries violating | largest single violation |
|---|---|---|---|
| `es` | 12,385 | **84** | `cop_parent` in `one_person`, 54 |
| `uk` | 14,582 | **41** | `cop_parent` in `one_person`, 120 |
| `it` | 13,548 | **124** | `cop_parent` in `one_person`, 169 |

The same shape in all three folds: a person recorded as living alone, co-present with a parent. There
are also `cop_alone` episodes that simultaneously assert company — 39 / 23 / 59 — which is
self-contradiction inside a single episode and needs no household knowledge to reject.

🔴 **This is a gap against the specification, not a model result.** It could be closed by compiling
six `COP` sub-alphabets and selecting one per prompt, which is what item 7.1 already asks for; it is
not done, and until it is, `G7.4` measures rather than confirms. **It is left FAILING** — the gate is
telling the truth about the build.

#### 🔴 `FINDING 82` — `G7.6` cannot fall unless `G7.2` already has

The shipped `tools/decoder.py` and `tools/4thJ_step7_grammar.py` were checked field by field: duration
canonical form, `ACT` three-digit membership, `ACT2` empty-or-member, `LOC` five classes, `COP` range
`0..64`. **They accept the same language.** So `G7.6` is a *third* enforcement confirmation and not,
as the gate table implies, an independent check. It is demonstrated rather than asserted: the
`g76_break_decoder` perturbation fells `G7.6` and `G7.2` together and nothing else.

This is worth having — an encoder/decoder pair that drifted from the grammar would show up here — but
it must not be counted as a passing measurement.

#### 🔴 `D-S7-4` — how the constraint-firing rate is defined. For the author.

`G7.7` asks *"how often the mask had to intervene"*, per stratum, and expects **> 35 %** untuned and
**< 2 %** tuned. **vLLM exposes no count of mask interventions**, and the obvious substitute — the
share of decoding positions at which the mask removed at least one candidate token — is ~100 % for
every batch ever generated and therefore carries no information.

| option | reading | note |
|---|---|---|
| **(a)** | 🔴 **Recommended. Per DIARY: the share of diaries the model gets structurally wrong with the mask OFF.** | It is the quantity the document's own expectations are sized for, it is already measured (it is `1 − G7.5` pooled, and `G7.7` is it per stratum), and it needs no instrumentation the back-end does not provide. It makes `G7.5` and `G7.7` two granularities of one measurement, which should be said in the methods rather than hidden |
| **(b)** | Per TOKEN, instrumented with a custom `LogitsProcessor` that counts positions where the sampled token would have been masked out | Honest and much more expensive: it needs a second decode of every diary, it cannot be done inside vLLM's structured-output path, and the resulting number has no pre-registered band |

**Implemented as (a)** in `tools/4thJ_gates_step7.py`, printed as a declaration at the top of the
module rather than left in the operator's head. 🔴 If the author rules (b), the gate is rebuilt and
this entry is superseded; nothing downstream depends on it yet.

#### 🔴 `V7.a` cannot be satisfied at `N = 600`, and that sizes the campaign

`V7.a` FAILs `G7.7`/`G7.8` unless **10 strata carry ≥ 100 records**. 600 records cannot fill more than
six. Computed from the real 100,000-person prefix pools — **228 strata per fold** — the tenth-largest
stratum has share 0.0196 / 0.0192 / 0.0206, so the minimum viable batch is:

| fold | strata | 10th-largest share | 🔴 `N` for `V7.a` |
|---|---|---|---|
| `es` | 228 | 1.96 % | **5,115** |
| `uk` | 228 | 1.92 % | **5,203** |
| `it` | 228 | 2.06 % | **4,850** |

`G7.9` is harder still. Its control is the **rejection-sampled** subset of the unconstrained batch, and
at the pilot's yield matching 600 constrained diaries needs ~22,500 unconstrained draws on `es`,
~8,200 on `uk`, ~15,000 on `it`. **At Leg-4 yields the rejection control is not affordable**; it
becomes affordable exactly to the extent Leg 5 raises `G7.5`. That is the number to watch first when
the 7 B fold is generated.

#### 🟢 Every gate that can move has been made to move

`outputs_step7/gates_step7_leg4_perturbations.json`, eleven runs on the `es` fold.

| perturbation | felled |
|---|---|
| `g71_break_tally` | `G7.1`, and `G7.13` with it (the indoor module refuses a day that does not sum, rather than padding it) |
| `g72_out_of_list_act` | `G7.2` |
| `g76_break_decoder` | `G7.6` and `G7.2` together — `FINDING 82` |
| `g711_drop` | `G7.11` |
| `g713_local_copy` | `G7.13` |
| **rose from FAIL** | |
| `g74_clean_cop` | `G7.4` → PASS |
| `g75_control_is_valid` | `G7.5` → PASS, and `G7.9` → PASS |
| `null` | nothing moved |

🔴 **The coverage clause earned its keep immediately.** The first version of `g72_out_of_list_act` set
an `ACT` to **`999`** — which **is** one of the 159 codes. The perturbation was a no-op, `G7.2` stayed
green, and only the cross-tab showed it. The battery now asserts its out-of-list code against the live
alphabet at start-up and refuses to run if it is a member.

`G7.10` did not move here and is not supposed to: it was seen failing in **its own** job under the
off-by-one oracle perturbation, and the battery reads its artefact rather than re-scoring it.
`G7.12` did **not** move when work item 7.2 wrote `throughput_comparison.md` on 2026-08-22. The
artefact exists and covers both backbones, and diaries/second is measured and sound, but the gate
also demands **peak KV memory** and the report carries no valid value for it: the derived pool is
**227.141 GiB against a 74.506 GiB card** and `torch_peak_allocated_gib` is **0.0 in both rows**.
See `FINDING 97`. It moves when the KV derivation reads OLMo 3's `layer_types` — a 7-minute re-run.

#### What is NOT established

* **Nothing here is a model result.** Leg 4 is 1.48 B and a rehearsal.
* `G7.4` is failing for a build reason, and the six household-indexed `COP` variants are owed.
* `G7.7`/`G7.8` have never been scored, only refused by `V7.a`. They need `N ≈ 5,100`.
* `G7.9` has never been scored against an adequate control.
* Work items 7.4, 7.6 and 7.7 are untouched. The three-model firing-rate report needs the untuned base
  arm, which has not been generated.

---

### 2026-08-22 (evening, second entry) — 🔴 **`FINDING 81` WAS MEASURED AGAINST THE REAL CORPUS BEFORE ANYONE PROPOSED ENFORCING IT, AND IT SPLITS IN TWO. `FINDING 83`, `D-S7-5`.**

`FINDING 81` closed with *"it could be closed by compiling six `COP` sub-alphabets"*. Before writing
one, the rule was run against all **73,254 real diaries** — because `FINDING 45` is what happens when
a constraint is encoded first and measured afterwards, and it cost 28.95 % of the corpus.

#### 🔴 `FINDING 83` — the household-membership half would reject 1.49 % of the REAL corpus, unevenly

| fold | diaries | violating | share |
|---|---|---|---|
| `es` | 19,140 | 226 | 1.18 % |
| `it` | 38,260 | 124 | **0.32 %** |
| `uk` | 15,854 | 744 | **4.69 %** |
| **all** | **73,254** | **1,094** | **1.49 %** |

**A 14.7× spread between `uk` and `it`.** Country-correlated, therefore read per fold or not at all
(`FINDING 53`'s standing rule), and therefore capable of moving a LOCO result on its own.

| violation | episodes in the corpus |
|---|---|
| `cop_children` in `couple_no_children` | 2,358 |
| `cop_other_hh` in `one_person` | 2,132 |
| `cop_partner` in `one_person` | 1,355 |
| `cop_partner` in `single_parent_with_children` | 1,151 |
| `cop_parent` in `one_person` | 449 |
| `cop_children` in `one_person` | 384 |

These are not our defect. They are the harmonised source data disagreeing with itself: a respondent
whose household type came from one survey field reporting company from another. `D-S2-19` already
forbids repairing this class on a prevalence basis.

#### 🟢 The self-contradiction half is CLEAN on real data, and the model breaks it

`cop_alone` asserted **together with** any other co-presence flag, in the same episode. It needs no
household knowledge — it is one episode contradicting itself.

* **Real corpus: 0 episodes in 73,254 diaries.** Not rare. Zero.
* **Generated, Leg-4 pilot: 39 (`es`) / 23 (`uk`) / 59 (`it`) episodes.**

🔴 **That is a model-side defect with a clean reference**, and it is the first thing in Step 7 that
separates "the corpus is like this" from "the model invented this".

#### 🔴 `D-S7-5` — what `G7.4` enforces. For the author.

| | option | consequence |
|---|---|---|
| **1** | 🟢 **Recommended. Enforce ONLY the self-contradiction rule** in the grammar: an episode asserting `cop_alone` may assert nothing else. | **Costs zero real diaries** — the corpus contains none — so it is additive, not a basis change. It removes a defect the model demonstrably has. One `COP` sub-alphabet, not six: the 32 patterns with bit 0 set and any other bit are simply absent from the alphabet |
| **2** | Enforce household membership as well, via the six household-indexed variants item 7.1 asks for. | 🔴 **A BASIS CHANGE.** It rejects 1.49 % of real diaries, 14.7× more often in `uk` than in `it`, and would have to be declared as a modelling intervention in the methods rather than as structural validity — exactly what `D-S7-2` (a) decided not to do for `G7.3` |
| **3** | Enforce neither; report both rates alongside `G7.3`. | Consistent with `D-S7-2` (a) and cheapest. But it leaves the model free to emit a self-contradicting episode that no human day contains, and Step 8 reads `COP` |

🔴 **Nothing is enforced pending the ruling** and `G7.4` is left FAILING in the battery, reporting
both halves separately. `4thJ_step7_ebnf.py` is untouched; the grammar md5 is unchanged.

---

### 2026-08-22 (night) — 🟢 **`D-S7-4` AND `D-S7-5` RULED BY THE AUTHOR AND BOTH APPLIED. THE GRAMMAR HAS CHANGED FOR THE FIRST TIME SINCE IT WAS BUILT: `COP` GOES 65 → 34 AND THE `.ebnf` md5 GOES `65aae7cb…` → `bb4208dd…`. 🔴 THE RULING SAID 32 IMPOSSIBLE PATTERNS. IT IS 31, AND THE MODULE REFUSES TO RUN IF IT IS EVER ANYTHING ELSE.**

Ruling document, with the author's directives, archived at
`IMP/docs/DONE/2026-08-22_rehearsal-docket_findings-and-decisions.md`.

#### `D-S7-5` option (1) — enforce self-contradiction, never household membership

`COP` is a six-bit flag set with `cop_alone` at **bit 0** (read live from
`crosswalk_copresence.csv`, not hard-coded). The excluded set is every value with bit 0 set **and**
any other bit set:

| | count | why |
|---|---|---|
| values with the `cop_alone` bit set | 32 | |
| of those, `cop_alone` **alone** — legal, kept | 1 | a person who is alone |
| 🔴 **excluded** | **31** | alone *and* with company, in the same episode |
| the sentinel `64` = *not collected* | kept | it is not a flag set at all |

🔴 **The ruling and the earlier docket both said 32.** The count is 31; the off-by-one is the legal
`cop_alone`-alone pattern. It is recorded here rather than silently corrected because the number
appears in an author ruling, and `build_alphabets()` now **raises** if the exclusion is ever a
different size — a COP width change or a bit-position change would otherwise slide past.

**Verified before enforcing, which is the discipline `FINDING 45` cost 28.95 % of the corpus to
learn:** across **73,254 diaries / 2,024,068 episodes**, **ZERO** carry an excluded pattern. The rule
is additive. It is not a basis change and it rejects nothing real.

| artefact | before | after |
|---|---|---|
| `COP` alphabet | 65 | **34** |
| `step7_grammar.ebnf` md5 | `65aae7cb4f48ebb495f449ae91bcfd50` | **`bb4208dd99794c3b52bdead0608d7fad`** |
| header line | `ACT 159 \| ACT2 43 \| LOC 5 \| COP 65` | `… \| COP 34` |
| `4thJ_step7_grammar_selftest.py` | 44 checks | **51 passed, 0 FAILED** |

The seven new checks are not decoration: they pin the count at 31, keep `64`, keep `0`, keep
`cop_alone`-alone, kill `3`, assert that every excluded value really does carry the alone bit plus
another, and confirm the **oracle itself** rejects an excluded pattern — so the hand-written
recogniser and the grammar cannot drift apart on this rule.

🔴 **`G7.10` must be re-run** — the language changed, so a 2026-08-22-morning agreement between the
oracle and XGrammar says nothing about the language of 2026-08-22 night. Submitted as job 1286241, which died in 5 s (`ModuleNotFoundError: encoder`, the grammar now imports `load_bit_positions`); resubmitted as **job 1286244**;
until it returns, the `G7.10` PASS printed by the battery is a **stale artefact** and is labelled so.

#### `G7.4` is now two gates wearing one name, and only one of them is the verdict

| half | status | on the Leg-4 batches |
|---|---|---|
| **self-contradiction** (`cop_alone` + company) | 🟢 **ENFORCEMENT CONFIRMATION** — the grammar cannot emit one | 🔴 still FAILS: 39 / 23 / **59** episodes. Those batches were generated **before** the ruling. That is the defect the ruling removes, not a gate failing |
| **household membership** | REPORTED, **never enforced**, **not in the verdict** | rates reported per fold beside `G7.3`, as the ruling directs |

Board unchanged at **12 PASS / 15 FAIL** over scored gates, and `G7.4`'s FAIL is now traceable to a
single named cause that Leg 5 cannot reproduce.

#### `D-S7-4` option (a) — per diary, and the campaign is sized

Confirmed as already implemented. The methods owe one sentence: **`G7.5` and `G7.7` are the same
measurement at two granularities**, pooled and per stratum, and must never be presented as
independent evidence. The author **mandated `N ≥ 5,200` per fold** for Leg 5, which is what `V7.a`'s
ten-strata-of-100 rule costs against the real 228-stratum prefix pools.

---

### 2026-08-22 (late night) — 🟢 **`G7.10` RE-RUN UNDER THE 34-VALUE COP ALPHABET: PASS, 0 DISAGREEMENTS ON 10,000 STRINGS. THE STALE ARTEFACT IS RETIRED. 🔴 AND IT CAUGHT A SECOND SELF-TEST NOBODY HAD UPDATED.**

Job **1286244**, 23 min 15 s, `envs/step7`, XGrammar **0.2.3**. Artefact
`outputs_step7/g710_oracle_agreement.json`, md5 `631ad64ba344de9e1195e0029214652c`; grammar
`step7_grammar.ebnf` md5 `bb4208dd99794c3b52bdead0608d7fad`, 114,833 chars, 296 rules.

| | |
|---|---|
| alphabets | ACT **159** (158 shipped + `000`), ACT2 43, LOC 5, **COP 34** |
| policy | `permissive` (`D-S7-2` (a)) |
| entry point | `xgrammar.testing._is_grammar_accept_string` |
| compile | 0.281 s |
| match | 1,113.15 s for 10,000 strings (9 strings/s) |
| **disagreements** | **0** |
| oracle | accepted **5,000**, rejected **5,000** |

🔴 **The 5,000 / 5,000 split is what makes the zero meaningful.** Two recognisers that both reject
everything also agree perfectly. Here 5,000 valid strings are accepted by BOTH and each of the
nineteen mutator classes is rejected by BOTH — `cop_range`, `cop_leading_zero`, `bad_act`,
`dur_not_mult10`, `day_long`/`day_short`, `no_eor`, `zero_episodes`, `whitespace` and the rest, 263
or 264 strings each. No mutator class is entirely accepted, which is `V7.e`'s vacuity clause.

**The earlier PASS is now retired.** It was measured on the 65-value COP language of
2026-08-22 morning and was labelled a stale artefact the moment `D-S7-5` (1) changed the alphabet.
This one is measured on the language that will actually be used.

#### 🔴 The re-run exposed a self-test that had been left behind

`4thJ_step7_ebnf_selftest.py` still asserted `COP is 0..64 = 65` and reported **42 ok, 1 FAILED** — in
the same job whose grammar self-test reported 51 of 51 green. Two self-tests, one alphabet, and only
one of them had been updated. The EBNF self-test now carries **six** checks in place of the one:
34 values, exactly 31 excluded, `64` still present as the not-collected sentinel, `0` still present,
`3` (alone + partner) gone, and `COP_MIN`/`COP_MAX` **unchanged at 0..64** — because the range
constants describe the encoding, not the admissible set, and conflating the two is how this kind of
edit goes wrong. **48 ok, 0 FAILED.**

🔴 The job that shipped this ran with the failure in it. `G7.10` itself was unaffected — it reads the
alphabet from `build_alphabets()`, not from the self-test — but a red self-test in a green job is
exactly the state in which a real regression hides, and it is recorded here rather than quietly fixed.

#### 🟢 What `G7.10`'s PASS does and does not cover, settled by diff rather than by argument

The generation jobs print a **114,806**-char grammar; `G7.10` verified **114,833**. The 27 characters
are not a discrepancy — they are the prefix, and the difference was checked rule by rule rather than
assumed:

| present only in the WHOLE-RECORD grammar (`G7.10`) | present only in the COMPLETION grammar (generation) |
|---|---|
| `root ::= PF "," PF "," PF "," PF "," PF "," PF "|" S0 "<eor>"` | `root ::= S0 "<eor>"` |
| `PF ::= PFCHAR | PFCHAR PF` | |
| `PFCHAR ::= [0-9a-zA-Z_+-]` | |

**Every other rule is byte-identical** — all 293 of them, including the 145-state duration tally and
the ACT / ACT2 / LOC / COP alphabets. So `G7.10`'s zero disagreements over 10,000 strings covers the
whole of the episode language that constrained generation actually uses; what falls outside its scope
is the six prefix fields and the `|`, and those are **supplied in the prompt and never generated**.

🔴 Stated because a reviewer would otherwise be right to ask: a gate that verifies one language while
the run uses another proves nothing. Here the second language is the first with the prompt-side rule
removed, and that is a diff anyone can re-run.

---

### 2026-08-22 (evening) — 🟢 **`D-S7-5` (1) IS NOW VERIFIED ON GENERATED TEXT, NOT ASSERTED FROM THE ALPHABET. TWENTY-ONE POST-RULING BATCHES, 301,713 EPISODES, **ZERO** SELF-CONTRADICTORY `COP`. AND THE COMPARISON EXPOSES WHAT THE OLD GRAMMAR WAS ACTUALLY DOING: `FINDING 92`.**

The 21 batches generated for `G6.6` and `G6.7` (jobs 1286254–1286274) are the first Leg-4 output
produced **after** the `COP` alphabet was cut from 65 values to 34. That makes them the first
opportunity to check the ruling against text rather than against the grammar file.

A `COP` value is self-contradictory when `cop_alone` is set alongside any company bit. The bit
positions are read live from `crosswalk_copresence.csv`; the `64` "not collected" sentinel is
excluded, as it is everywhere else.

| batch set | `COP` alphabet | files | episodes | self-contradictory |
|---|---|---|---|---|
| **post-ruling** (`g66*`, `g67*`) | **34** | 21 | **301,713** | **0** |
| pre-ruling `constrained` | 65 | 3 | 40,720 | 121 (**0.2972 %**) |
| `nogrammar` control | none | 3 | 35,626 | 120 (**0.3368 %**) |

#### 🔴 `FINDING 92` — the COP-65 grammar had no purchase on this axis at all

The pre-ruling **constrained** batch produced self-contradictions at **0.2972 %**, and the batch
generated with **no grammar whatsoever** produced them at **0.3368 %**. The constrained rate is
**88 % of the unconstrained rate.** Within the noise of three batches, *the mask was removing
nothing here*: it admitted all 65 encodings, so the 31 impossible flag sets were legal tokens and
the model emitted them at essentially the rate it would have unmasked.

🔴 This is the concrete cost of the defect `D-S7-5` (1) removed, and it reframes what `G7.4`'s
self-contradiction half was measuring before the ruling. It was **not** reporting a residual failure
of a constraint that was mostly working. It was reporting a constraint that, on this axis, was not
operating — while sitting inside a batch labelled `constrained`. A gate reading 0.30 % looks like a
small leak; it was in fact the full unconstrained rate.

🟢 After the ruling the quantity is not small — it is **structurally zero, across 301,713 episodes**,
because the 31 encodings are no longer in the alphabet and the grammar cannot express them. That is
the difference between a measurement and an enforcement confirmation, and it is why the battery
docstring now labels it the latter.

#### What this does and does not settle

* It confirms the ruling on **generated** text at scale. The absence was previously established only
  on the 2,024,068 **real** episodes, which is what justified the cut but says nothing about what a
  model would emit.
* 🔴 It does **not** retire the pre-ruling batches' `G7.4` readings. Those batches remain what they
  are; they are simply no longer the current alphabet, and any Leg-4 `G7.4` number quoted from
  `generated_leg4_*_constrained.jsonl` must carry the COP-65 label.
* The household-membership half of `G7.4` is untouched by all of this and remains **reported and
  never enforced**, per the same ruling.

#### 🔴 One reporting defect fixed while checking the above — `G7.2` was describing the wrong rejection

Re-scoring the battery surfaced `G7.2` reporting **`episode 1 COP 5 outside 0..64`**. `5` is inside
`0..64`. The *test* was correct — `int(cop_s) not in alphabets["cop"]` — but after `D-S7-5` (1) cut
the alphabet to 34 values, two different rejections wear that one test, and the message only ever
described the rarer one. The common case is now a value that **is** in the encoding range and is
simply not an admissible flag set.

The two are separated in `4thJ_step7_grammar.py` (backup `.bak_g72msg`), message-only:

```python
if int(cop_s) < COP_MIN or int(cop_s) > COP_MAX:
    return False, "episode %d COP %s outside the %d..%d encoding range" % (...)
return False, ("episode %d COP %s is in 0..%d but is not one of the %d "
               "admissible flag sets (D-S7-5 (1))" % (...))
```

🟢 **Nothing about acceptance changed and it was verified rather than assumed**: every gate verdict
and every count in `gates_step7_leg4_baseline.json` is identical across the two runs (board
`15 FAIL / 12 PASS` both sides), the twenty-one differing leaves are message strings and relative
paths, and both self-tests stay green — `4thJ_step7_grammar_selftest.py` **51/51**,
`4thJ_step7_ebnf_selftest.py` **48/48**. `G7.10`'s oracle-agreement result is therefore untouched:
the string is returned only on rejection and the boolean is unaffected.

🔴 It also puts a number on something previously unquantified. `G7.5`'s `top_reasons` shows **24 of
the `es` unconstrained rejections** are this COP reason — so the reduced alphabet accounts for about
4 % of the mask's work on that fold, not the bulk of it. The bulk remains the tally automaton.

🔴 Corrected in passing, and **the pre-COP-34 `constrained` batches were already scored under the
34-value alphabet** — the earlier baseline artefact was produced after the ruling, so the firing
rates did **not** move: `G7.5` stays 2.67 % (`es`) / 6.83 % (`uk`) / 3.83 % (`it`) valid without the
mask, i.e. a per-diary firing rate of **97.33 / 93.17 / 96.17 %**.

#### 🔴 DoD item 5 is NOT met, and `G7.9` computed the reason itself

*"Rejection-sampled control generated and marginals compared."* The control exists but is far too
small to support the comparison. `G7.9` says so in its own output rather than passing quietly:

> *the control carries 23 valid diaries against 600 constrained ones. A marginal estimated from 23
> diaries cannot resolve 5.0 min/day, so this verdict is about the CONTROL, not about the mask.*

Sized from the measured unconstrained validity rates, matching 600 constrained diaries needs:

| fold | valid without the mask | draws needed for 600 valid |
|---|---|---|
| `es` | 16/600 = **2.67 %** | **≈ 22,500** |
| `uk` | 41/600 = **6.83 %** | **≈ 8,800** |
| `it` | 23/600 = **3.83 %** | **≈ 15,700** |

The `es`/`uk` ratio is **2.6×**: the rejection control is not equally affordable across folds, which
is itself a country-correlated property and belongs in the write-up beside `FINDING 45`'s
country-correlated `G7.3` rejection.

🔴 **These three jobs are sized and ready but deliberately NOT submitted.** Job 1286209 (Leg 5, the
critical path) is PENDING on **`AssocGrpGRES`** with *zero* running jobs of mine, i.e. the cap is a
group-level TRES rather than my own concurrency, and `gres/gpu` is counted across all slice types.
Submitting three more GPU jobs could therefore push the reported model's training later. Item 7.5
runs once Leg 5 is RUNNING, not before. Recorded here rather than left as a plan in someone's head.

---

### 2026-08-22 (night, third entry) — 🟢 **WORK ITEM 7.7 HAS AN EMITTER AND WORK ITEM 7.6 HAS ITS CPU HALF. FOUR GATES THAT HAD NEVER BEEN SCORED ARE SCORED. 🔴 FOUR FINDINGS AND ONE NEW DECISION CAME OUT OF IT, AND ONE OF THEM SAYS THIS DOCUMENT AND `D-S8-2` DISAGREE ABOUT WHAT A SCHEDULE CARRIES.**

Everything in this entry ran on the author's laptop while jobs `1286208` and `1286209` sat PENDING on
the A100 `7g.80gb` pool. **No job was submitted, nothing touched Speed, no socket was opened.** Full
record, with every number and every refusal: **`4thJ_07_schedules_and_chaining_IMP.md`**.

#### What was built

| file | what | state |
|---|---|---|
| `tools/4thJ_step7_schedules.py` | work item 7.7 — diary → presence → `Schedule:File` | selftest **52 ok / 0 FAILED** |
| `tools/4thJ_step7_schedules_selftest.py` | every refusal made to fire on fixtures | |
| `tools/4thJ_gates_step7_schedules.py` | `G7.13`–`G7.17`, everything re-read **from disk** | |
| `tools/4thJ_step7_chaining.py` | work item 7.6, DoD items 3 and 4 | selftest **40 ok / 0 FAILED** |
| `tools/4thJ_step7_chaining_selftest.py` | metrics checked against series whose answer is known | |

Artefacts under `outputs_step7/`: `schedules/leg4_{es,uk,it}_independent_seed1/`, `schedules/perturb_*/`,
`gates_step7_schedules_baseline.json`, `gates_step7_schedules_perturbations.json`,
`chaining_prescreen_leg4.json`, `chaining_prescreen_leg4_stdout.txt`.

#### 🟢 `G7.13`–`G7.17`: 5 PASS / 0 FAIL on all three folds, all five seen falling

100 `Schedule:File` + 100 `People` objects and 100 CSVs of 8,760 hourly values per fold; mean presence
`es` 0.7285 / `uk` 0.6450 / `it` 0.6843; exclusion list md5 `679518c7f626bd5d408adc96b5a1ff43` read
live from Step 2's shipped path. The board's **first** run was a `G7.13` FAIL and it was right: the
emitter's manifest recorded the list's md5 but not whether the list used **was** the shipped one, so
`V7.c` was uncheckable from the artefact. Fixed additively, re-emitted, PASS.

#### 🔴 `FINDING 93` — this document asks for 100 HOUSEHOLDS and Step 5 cannot supply one

`population_<c>.csv` is a 100,000-row **person** table with **no household identifier** — `D-S5-9`
settled household type on a person basis and never needed to assemble a dwelling. Work item 7.6's
*"100 households"*, and the co-presence half of `G7.4`, have no object to run on in the synthetic
population. Composition was therefore taken from the **real corpus** (`hid`/`pid`): real households,
generated days — **a sample of surveyed households, not of the synthetic population.** → **`D-S7-6`,
open**: (a) leave it and say so, (b) give Step 5 a household id, which re-opens a step that closed on
2026-08-22, or (c) group persons post hoc, which invents a joint distribution nothing measured.

#### 🔴 `FINDING 94` — this document and `D-S8-2` disagree, and one of them cannot be implemented

**"DIARIES TO SCHEDULES"** above says schedules carry *"activity-resolved internal gains, which is the
part a presence fraction throws away"*. **`D-S8-2` item 5**, ruled 2026-08-21, fixes the Step 8
interface as `phi_int(t) = (1-f)*3.0 + f*3.0*g(t)/mean_year(g(t))` with `g(t)` *"the generated
presence signal from `G7.13`"*. **A fraction is not a watt.** Resolving a 3-digit HETUS code into a
power needs a mapping and there is no admissible one: `RL25` was commissioned for exactly that and its
Part C figures were rejected as unsourced. The emitter implements the **ruled** interface and keeps
each pool day's activity codes beside it, so the mapping can be applied later without a GPU run. ⚪ The
methods owe one sentence saying the gains are occupancy-redistributed and **not** activity-resolved.

#### 🔴 `FINDING 95` — `G7.14` and `G7.17` had no registered falsifier

The validation document's perturbation table listed both only in the "must stay clean" column, so the
coverage clause would have read four of four with two unfalsifiable gates. Two perturbations added
there, marked as additions; all six run; each felled its gate with the intended message; the null
perturbation felled nothing.

#### 🔴 `FINDING 96` — `RL21`'s vocabulary criterion has no reference, and the reference it does have is flat

*"The realistic value is computed on the held ISTAT data"*: **ISTAT gives every respondent exactly one
diary day, and so does Spain.** Only the UK has a second (7,920 persons), and in 99.7 % of those the
two days are a weekday and a **weekend** day — 21 pairs share a day type. A monthly vocabulary has no
empirical reference anywhere in this project. And the quantity the UK anchor does measure — Jaccard
between adjacent days of different day types — moves by **0.003 / 0.001 / 0.002** across all six
chaining rules, because the habit rule holds the previous day *of the same day type* and cannot touch
a weekday→weekend step. **The one empirically anchorable criterion cannot tell the rules apart.**

#### 🔴 The chaining pre-screen returned the validation document's own pre-registered null

90 cells (3 folds × 6 rule points × 5 seeds, 100 households). On the coincidence metrics a peak-demand
pre-screen is made of, **seed noise dominates**: `mean_pair_corr` on all three folds, `annual_mean` on
all three, `max_ramp` on two; `peak_aggregate` and `p99_aggregate` are **degenerate**, pinned at 1.000
in all 30 cells on `es` and `it`. The rule effect is large only on monthly vocabulary (ratios 18.17 /
11.89 / 18.36) and same-day-type Jaccard (71.64 / 64.50 / 63.77). 🔴 **`G7.18` is NOT evaluated** — its
trigger is on peak DEMAND and `RL21`'s second metric on annual heating/cooling ENERGY, both
EnergyPlus outputs. **Open decision 14 stays OPEN.**

#### ⚪ Recorded, not decided

The schedule calendar year is one per fold — `es` 2010, `uk` 2014, `it` 2013, the non-leap year of
each survey pair. `D-S8-2` item 6 ruled diary-survey-year weather and each survey spans **two**
calendar years, so which of the two a schedule runs on is unruled. The emitter refuses leap years and
the parameter has no default, so it cannot be chosen by accident.

#### 🔴 What is still owed on this step

DoD items **2, 3, 4, 5 and 6** and the reported-model half of item **7**, all of which need the GPU:
work item 7.2 (job `1286208`), the Leg-5 campaign (job `1286209`), the untuned-base firing-rate arm,
the rejection-sampled control at the size `G7.9` needs, and `G7.18`'s verdict. **Item 8 — "all Step 7
gates PASS and each has been seen failing" — is now true for `G7.13`–`G7.17` and for nothing else:
the generated-text board still reads 12 PASS / 15 FAIL.**

---

### 2026-08-22 (night, fourth entry) — 🟢 **WORK ITEM 7.2 IS MEASURED (job `1286208`, 00:06:55). 🔴 `G7.12` STAYS FAIL AND `FINDING 97` SAYS THE KV-CACHE ARGUMENT IN THIS DOCUMENT IS OVERSTATED FOURFOLD.**

Full record and the re-derivation: **`4thJ_07_schedules_and_chaining_IMP.md`** (fourth entry).
Artefacts: `outputs_step7/throughput_comparison.{md,json}` plus `outputs_step7/throughput_evidence/`.

🟢 **The measured half.** `N = 200`, both backbones base, eager, same job, same prompts, same grammar:
**22.5331 vs 26.9839 diaries/second — OLMo is 0.835x Qwen, not the large penalty this document's KV
argument predicts**, because it spends only **0.716x** as many output tokens per diary. 🔴 **The
backbone does not need defending on throughput, and the paper should say so in those terms.**

🔴 **`FINDING 97`.** The report's OLMo KV pool reads **227.141 GiB** against a **74.506 GiB** card —
**3.05x the whole GPU**, so it measures nothing. The emitter derives bytes/token from
`num_hidden_layers`, but OLMo 3 is hybrid: `layer_types` = **24 `sliding_attention` (window 4096) +
8 `full_attention`**. On the 8 full layers the pool is **56.785 GiB**, within **1.135 GiB of Qwen's
55.650** — which is the check, since two ~7B bf16 models on one card at `utilization = 0.9` must land
about there. 🔴 **The claim *"no GQA, so about nine times larger per token"* above is true of the
config field and false of the cache: the engine's ratio is 2.29x, not 9.14x.** `kv_cache_tokens` and
`max_concurrency` come straight from `num_gpu_blocks x block_size` and are unaffected, so **no
campaign sizing changes** — only the sentence does.

🔴 **`G7.12` does not move.** It demands diaries/second **and** peak KV memory. The pool figure is
impossible and `torch_peak_allocated_gib` is **0.0 in both rows** (vLLM v1 runs the model in a worker;
the parent allocator never sees it). No valid peak exists, so the gate fails on its own artefact —
which is the gate doing its job. It moves on a **7-minute re-run** once the derivation reads
`layer_types` and the peak is read from the engine log.


---

### 2026-08-22 (night, fifth entry) — 🟢 **ALL FOUR ITEMS THAT NEEDED A PERSON ARE RULED, ALL FOUR (a), AND ALL FOUR APPLIED. `D-S7-6`, `D-S7-7`, `D-S7-8` CLOSED; OPEN DECISION 14 CLOSES IN STEP 8. 🔴 APPLYING `D-S7-8` PRODUCED `FINDING 99`.**

Docket: `IMP/docs/DONE/2026-08-22_step7-four-items_D-S7-6_D-S7-7_D-S7-8_decision-14.md`, carrying the
author's rulings verbatim. Full record: `4thJ_07_schedules_and_chaining_IMP.md` (sixth entry).
⚪ **No gate was re-scored, no schedule re-emitted, no tool behaviour changed.** `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` untouched — none of the four is a pre-registered quantity.

| item | ruled | what moved in this document |
|---|---|---|
| `D-S7-6` — household basis | **(a)** surveyed composition, declared per fold | §7.6 carries the declaration and `FINDING 98`'s per-fold numbers |
| `D-S7-7` — internal gains (`FINDING 94`) | **(a)** presence signal, `D-S8-2` item 5 | DIARIES TO SCHEDULES bullet **rewritten**; §7.7 corrected |
| `D-S7-8` — schedule calendar year | **(a)** first calendar year of the `D-S8-2` item 6 window | §7.7 carries the rule; the "non-leap" rationale is struck |
| open decision 14 | **(a)** closes in Step 8 on `G7.18` | §7.6 carries the sizing; DoD item 6 marked discharged in Step 8 |

🔴 **The one contradiction in this document is gone.** DIARIES TO SCHEDULES said schedules carry
*"activity-resolved internal gains, which is the part a presence fraction throws away"* and §7.7 said
*"activity-resolved gains carried"*, while the ruled Step 8 interface (`D-S8-2` item 5) is a
**fraction**. Both lines now state the ruled interface and name the reason no other one is available:
`RL25` was commissioned for an activity→power mapping and its Part C figures were rejected as
unsourced. ⚪ The emitter already implemented the ruled interface and keeps each pool day's activity
codes beside the presence signal, so reinstating activity-resolved gains later needs a **source**, not
a GPU run.

🔴 **`FINDING 99` — applying `D-S7-8` exposed a condition the ruling itself cannot satisfy alone.**
"The first calendar year of the twelve-month window" delivers the intended weekend coincidence **only
if that window is January–December**. A window straddling two calendar years (July 2013 – June 2014,
say) aligns for its first six months and is off by one or two weekdays for the rest; a straddling span
containing 29 February is **8,784 hours**, which `year_day_types()` refuses outright; and the emitter
has a `--year` parameter but **no window-start parameter**, so a straddling window could not be
honoured without an additive change to `tools/4thJ_step7_schedules.py`. ⚪ Needs no ruling — it is a
**constraint on `D-S8-2` item 6**, recorded in §7.7 and in the Step 8 document.

🔴 **What the rulings do NOT close.** `D-S7-6` (a) constrains what may be claimed, so household
metrics are **per fold or not at all** and the asymmetry table gains a row. Decision 14 (a) is a
ruling about **order**, not a green light: `G7.18` is blocked behind an IDF that does not exist and
five open §6 geometry/zoning decisions, and the CPU pre-screen must be **re-run at Leg-5's
`N >= 5,200`** before any of its verdicts is written into the paper. DoD item 6 therefore cannot close
inside Step 7.
