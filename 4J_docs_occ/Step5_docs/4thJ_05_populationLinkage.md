# Step 5 — Conditioning and population linkage

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 5. Validation: `4thJ_05_populationLinkage_val.md`

---

## STATUS

**✅ DECIDED by `RL09`. Implementation OPEN.** 🟢 **2026-08-21: work item 5.1 is COMPLETE for all
three folds** — `marginals_{uk,es,it}.csv` and `econ_11plus_{uk,es,it}.csv` exist with full provenance,
so `G6.1`'s raked-donor null is computable on every fold and Italy is off the critical path.

🟢 **2026-08-21 (afternoon): `strat_hh_type` IS NOW ON A PERSON BASIS IN ALL THREE FOLDS** —
`hhtype_person_{es,uk,it}.csv`. `D-S5-6`, `D-S5-7` and `D-S5-8` are all CLOSED, and `D-S5-8` was
dissolved rather than answered: no country needed a conversion factor. 🔴 **`FINDING 60` and the new
`D-S5-9`**: the three offices classify "family plus other people" two different ways, `es`/`uk` on
convention A and `it` on convention B, and the difference is COUNTRY-CORRELATED. All three person
files are on A; `marginals_it.csv`'s HOUSEHOLD rows are still on B and disagree with Italy's own
person file. See the 2026-08-21 (afternoon) Progress Log entry.

🟢 **2026-08-21 (late afternoon): `D-S5-9` RULED (a) AND APPLIED, AND ITEMS 5.2 AND 5.3 ARE
BUILT FOR ALL THREE FOLDS.** `marginals_it.csv`'s household rows are on convention A from the ISTAT
1 % microdata; `population_{es,uk,it}.csv` (100,000 synthetic persons each, no random draw anywhere)
and `prefixes_{es,uk,it}.jsonl` exist, the latter built through the SHARED `tools/encoder.py` with an
exact round trip on all 300,000 rows.

🔴 **The corpus was never the blocker.** It was already on this machine, and it is the
post-`D-S6-1` HOUSEHOLD-split corpus: 73,254 records, 32,205 households, **0 households straddling the
split**, md5 `ca89d2295603c547f2384a40dd1909ba`. It now lives at
`Step3_docs/outputs_step3/4J_step3_corpus.jsonl`.

🔴 **Two new findings, and the second one reaches the headline gate.**

* **`FINDING 61`** --- `D-S5-3` puts every 11-14-year-old in the population into `unknown`, but the
  CORPUS uses a different band in each country: `student` (es, 99.9 %), `other_inactive` (uk, 100 %),
  `unknown` (it, 100 %). So the `es` and `uk` folds have their entire 11-14 band served by ITALIAN
  donors alone, and the `it` fold has no donor for it at all.
* **`FINDING 62`** --- `G6.1` was RUN for the first time, on the real donors and the real marginals.
  It **cannot converge for the `uk` fold** (1.41515 pp against a 0.5 pp tolerance --- the age-15
  `unknown` slice nobody supplies), and the `it` fold converges only by making **68 British diaries**
  carry 4.207 % of an entire country, at an effective sample size of **46 %** of the pool.

🟢 **2026-08-21 (evening): `D-S5-11` RULED (b), `D-S5-10` RULED (a), BOTH APPLIED, AND THE
STEP 5 GATE BATTERY HAS RUN.** All three populations are rebuilt, `G6.1`'s raked-donor null now
**converges on every fold** (it could not be built for `uk` at all before), and 25 of 27 gate-fold
verdicts PASS with the coverage clause clean --- every passing gate was seen falling on every fold.

🔴 **`G5.6` FAILS on `es` (30 of 36 marginal rows) and on `it` (12 of 36), and it is being left
to fail.** Its text bars a marginal "derived from microdata", and `D-S5-4` (b), `D-S5-5` and `D-S5-9`
each ruled exactly that, knowingly. `D-S5-12` is open on whether the gate's text should distinguish
published CENSUS microdata from the held-out country's DIARIES. It is not being relaxed meanwhile.

🔴 **`G5.8` and `G5.9` are BLOCKED, not passing.** Both read artefacts item 5.4 and Step 7 have
not produced. **Item 5.4 remains unbuilt**: it needs a fold checkpoint and a generation pass, which is
`D5.1`'s blocker too. Step 5's Definition of Done is therefore **3 of 5 ticked, item 5 partially**, and
the step is NOT closed.

---

## AIM

Produce the **people** the model will be conditioned on, by a method that is not the model.

```
 census marginals for the place
        |
        v
 (a) synthetic population        <- IPF or combinatorial optimisation
        |                           exact on demographics, literature reviewers already trust
        v
 (b) one diary per synthetic person   <- the fine-tuned LLM (Step 7)
```

---

## WHY TWO STAGES — AND IT IS AN ARGUMENT, NOT TIDINESS

Having the model emit person **and** diary jointly would let it hallucinate demographic proportions,
and it compounds two claims into one a reviewer can reject wholesale. **Separated, a reviewer who
doubts the population synthesis can still accept the diary generation.**

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| Two stages, population first | `RL09` |
| 🔴 **Training loss is UNWEIGHTED** | `RL09` |
| 🔴 **We never rake our own output** | `RL09` |
| No aggressive top-p / top-k at generation | `RL09`; p ≥ 0.98 if used at all (🔴 post-registration erratum, `FINDING 69`, ruled 2026-08-21) |
| Representativeness is enforced in stage (a), where IPF makes it exact | `RL09` |

### The unweighted-loss argument, restated because it is counter-intuitive

Survey statistics says use pseudo-maximum-likelihood with design weights. Deep learning says
importance weighting in an overparameterised network inflates gradient variance without moving the
decision boundary. **`RL09` resolves it rather than picking a side:** because the conditioning prefix
contains the design strata — country, age, sex, household type, economic status, day type, season 🔴 *(`season` DROPPED by `D-S2-19`, 2026-08-20 note: argument unaffected, list stale)* —
the sampling mechanism is **conditionally ignorable** for `P(diary | X)`.

🔴 **It also removes a double-counting bug we would otherwise have shipped.** HETUS diary weights
already carry a weekday-weekend adjustment. Multiplying the loss by them **while** using stratified
batching applies that correction twice.

### The no-raking rule

Raking adjusts univariate margins and cannot reconstruct distorted multi-way interactions. Since
stage (a) already makes demographics exact, raking the diaries afterwards would only paper over a
model that failed.

🔴 **Raking appears in this project in exactly one place: building the null model in Step 6. We do not
get to use the trick we are benchmarked against.**

---

## INPUTS

* Census marginals per target country: Eurostat Census Hub, GEOSTAT 1 km grid, or national small-area
  tables.
* `../Step2_docs/outputs_step2/copresence_availability.md` — the prefix must not claim a flag a
  country never recorded.
* `../Step3_docs/outputs_step3/corpus.jsonl` — for the stratum definitions the prefix uses. 🔴 *(2026-08-20: this path does not exist. The corpus is `4J_step3_corpus.jsonl`, 73,254 records, job `1255620`.)*

---

## WORK ITEMS

### 5.1 — Assemble the marginals, per country, with provenance

For each country and each target geography: household composition, age, sex, employment status.

* Every marginal table carries its source URL, table ID and download date.
* 🔴 **For the held-out country, the marginals must be the PUBLISHED ones and nothing else.** Any
  quantity derived from that country's microdata is contamination, and it is contamination that would
  be invisible in the result.

**Output:** `outputs_step5/marginals_<country>.csv` + `marginals_provenance.md`.

### 5.2 — Synthesise the population

IPF or combinatorial optimisation onto the marginals. Standard method, deliberately: the reviewers
who will doubt this paper's model already trust this literature.

**Output:** `outputs_step5/population_<country>.parquet`, one row per synthetic person carrying
exactly the nine prefix fields Step 3 defined. 🔴 *(2026-08-20: **SIX**, not nine — `D-S2-19` dropped `season`, `D-S3-11` dropped `mode` and `scheme`. The frozen order is `country, strat_age_band, strat_sex, strat_hh_type, strat_econ_status, strat_day_type`, from `../tools/encoder.py`.)*

### 5.3 — Build the conditioning prefixes

Map each synthetic person to a Step 3 prefix string. **The mapping is one function, shared with
Step 3's encoder, not a reimplementation.** A second copy of a field order drifts invisibly from the
first.

**Output:** `outputs_step5/prefixes_<country>.jsonl`.

### 5.4 — Fix the decoding temperature, on a validation split

Paper 1 exposes argmax, probabilistic, and temperature-plus-top-k sampling and reports argmax is too
uniform at neighbourhood scale. The sharper question here: **does a temperature exist at which the
generated population's entropy matches the real population's, and is it the same temperature that
optimises the fidelity metrics?**

🔴 **The tail hazard, in our own terms.** Top-k and top-p truncation systematically delete rare
behaviour, and rare behaviour is where the interesting loads live: the household running laundry at
03:00, the shift worker, the early-morning vehicle charge. **Those are the cases a peak-demand study
exists to capture.** So: validation-set temperature scaling plus the Step 7 grammar mask, and no
aggressive truncation. If top-p is used at all, **p ≥ 0.98**.

🔴 **Post-registration erratum, `FINDING 69`, ruled by the author 2026-08-21.** This clause was registered as *p ≤ 0.98*, and that is the wrong direction. In nucleus sampling a **smaller** p truncates **more**, so as written the gate admitted `p = 0.50` — half the tail deleted — and rejected `p = 1.0`, no truncation at all: the exact opposite of a clause named *no truncation creep*, and incompatible with its own registered perturbation (*set `top_p = 0.9`*, which must FELL the gate and instead satisfied it). The coherent reading **p ≥ 0.98** is adopted; it is the only reading under which the register is self-consistent. ⚪ **Nothing about our configuration changes either way**: `TOP_P = 1.0` is a pre-registered constant in `4thJ_step5_temperature.py`, so top-p is not used at all and the clause is vacuously satisfied under BOTH readings. The checker prints both and takes its verdict on the coherent one.

**Output:** `outputs_step5/temperature_calibration.md` — the entropy-matching curve, the fidelity
curve, and whether they agree. **If they disagree, say so and pick entropy matching**, because
diversity is the property the downstream energy result depends on.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step5/population_<country>.parquet` | Step 7 |
| `outputs_step5/prefixes_<country>.jsonl` | Step 7 |
| `outputs_step5/temperature_calibration.md` | Step 7, Step 6 |
| `outputs_step5/marginals_provenance.md` | Step 6's contamination argument; the methods section |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`. CPU only — IPF needs no GPU.

---

## WHAT BLOCKS THIS STEP

Step 3 (prefix definition). It does **not** block on Step 4: the population can be synthesised while
the model trains, and should be.

**What this step blocks:** Step 7 has nobody to generate for without it. 🔴 **AND, found 2026-08-20: item 5.1 also blocks `G6.1` — Step 6 §5's RAKED-DONOR NULL, the pre-registered BAR, is raked onto "the held-out country's published marginals", i.e. `outputs_step5/marginals_<country>.csv`. Until 5.1 exists the headline gate cannot be computed at all. That puts 5.1 on the critical path of the claim, not merely of Step 7.**

---

## DEFINITION OF DONE

1. Marginals assembled with full provenance, and the held-out country's marginals demonstrably
   published-only.
2. Synthetic populations emitted, matching marginals to the Step 5 gate tolerances.
3. Prefixes built through the **shared** Step 3 encoder function.
4. Temperature calibrated on a validation split, with the entropy and fidelity curves both reported.
5. All Step 5 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 The rule that will be hardest to keep is **no raking of our own output**. When Step 6's margins
  come out slightly wrong, raking them will look like a one-line fix. It is the trick we are
  benchmarked against, and using it makes the headline comparison partly self-referential.

### 2026-08-20 — 🔴 **THIS STEP IS WRITTEN AGAINST A PREFIX THAT NO LONGER EXISTS, AND TWO OF ITS GATES CANNOT PASS AS WRITTEN. `FINDING 40`, `FINDING 41`, `D-S5-1`.**

Opened deliberately as parallel work while Step 4's `it` fold (`1284912`) holds the GPU — this step's
own text says *"it does not block on Step 4: the population can be synthesised while the model trains,
and should be."* Nothing was run. Everything below came from reading this document against
`../tools/encoder.py` and the frozen `../Step6_docs/outputs_step6/prereg.md`.

#### A. Three cross-references that are simply out of date. Corrected inline above.

| where | said | is |
|---|---|---|
| §INPUTS | `../Step3_docs/outputs_step3/corpus.jsonl` | **does not exist.** The corpus is `4J_step3_corpus.jsonl` (73,254 records, built 2026-08-17, job `1255620`) |
| §5.2 | *"exactly the **nine** prefix fields Step 3 defined"* | **SIX.** `D-S2-19` dropped `season`; `D-S3-11` dropped `mode` and `scheme` |
| `_val.md` `G5.5` | `../Step3_docs/outputs_step3/encoder.py` | **`../tools/encoder.py`** — and it is real, importable, and already the corpus's own encoder |

The six frozen fields, in order, from `encoder.py`'s `PREFIX_FIELDS`:
`country, strat_age_band, strat_sex, strat_hh_type, strat_econ_status, strat_day_type`.

**This is good news for `G5.5`.** The gate requires the prefix be **byte-identical** to what the Step 3
encoder emits, *"tested by importing that encoder, never by reimplementing it"*. That encoder exists,
is a pure library with no side effects, and its `encode_prefix(row)` takes exactly the six columns a
synthetic person would carry. `G5.5` is implementable today, with no model and no cluster.

#### 🔴 B. `FINDING 40` — `G5.4` cannot pass for the held-out country. By construction, on every fold.

`G5.4` requires **100 % of synthetic persons map to a prefix whose every field value appears in the
training corpus**, and gives the reason: *"an unseen field value at generation time is out-of-
distribution input, and the model will do something confident with it."*

**The first prefix field is `country`.** Under LOCO the `it` fold trains on ES and UK only — `G4.13`
exists precisely to assert that **zero** held-out-country records reached the loaded shard, and it is
scored from the shard, not the filename. So on the `it` fold the token `it` appears in the training
corpus **exactly zero times**, and then Step 7 generates every Italian diary with a prefix that opens
`it,...`.

**So 100 % of the held-out country's synthetic persons carry a field value absent from training, on
all three folds. `G5.4` reads 0 % where it demands 100 %.**

🔴 **This is not a bug to be fixed away — it is the experiment.** LOCO's whole claim is that the model
generalises to a country it never saw, and the country token is how the conditioning names that
country. But `G5.4`'s own rationale is then **describing the design's central mechanism as a defect**,
and it is right to be nervous: the model *will* do something confident with an unseen token, and
nothing in Steps 4–7 currently measures **what**. The parent's §4D chose a country token over
per-country adapters for forgetting reasons; the out-of-distribution consequence at generation time is
recorded nowhere in the project — a grep over every `.md` for *"unseen token"*, *"country token"*,
*"out-of-distribution"* returns discussion of an unrelated `<YEAR_2030>` case and nothing else.

**What it does NOT threaten:** `G4.13` is unaffected — an unseen token at generation is the opposite
of leakage. `G5.1`, `G5.2`, `G5.3`, `G5.6` and `G5.7` are unaffected; they never touch `country`.

#### 🔴 C. `FINDING 41` — `G6.7`'s fictional country cannot be encoded at all. The gate is blocked by the encoder.

`prereg.md` is **FROZEN** and its line 151 names the fictional-country control as one of four
named-in-advance detectors: *"condition on an **invented country token** with perturbed marginals and
verify the output follows the vector."* `G6.7` quantifies it at slope ≥ 0.8.

`../tools/encoder.py`, `enc_country()`:

```python
if s not in ("es", "uk", "it"):
    raise EncodeError("country %r lowercased to %r, not one of es/uk/it" % (v, s))
```

**The whitelist is closed and the failure is loud.** An invented token cannot be encoded, so `G6.7` —
a detector in a frozen pre-registration — cannot be executed through the shared encoder. There are
only two ways out and they are not equivalent:

* **hand-build the fictional prefix outside the encoder**, which is the reimplementation `G5.5` and
  `V5.d` both exist to forbid, and which would let the control's prefix drift from the real one
  invisibly — in a control whose entire job is to be identical except for the token; or
* **give `encoder.py` an explicit, declared escape hatch** for control tokens.

🔴 **The second is the only safe one, and it is an additive change to a file the corpus was built
with.** `4J_step3_corpus.jsonl` and every Step 4 fold were produced by the current encoder. Any edit
must therefore be **provably a no-op on the real three countries** — the same standard `D-S6-1`'s
household re-split met when it proved 0 texts differed. It also must not be taken by this step alone.

#### `D-S5-1` — for the author. Three rulings, none of which Step 5 may take on its own.

| | question | recommendation |
|---|---|---|
| **(a)** 🟢 **RULED 2026-08-20 (a), APPLIED** | `G5.4` scope | 🔴 **Exclude `country` from `G5.4`'s membership test and say why in the gate's own text**, keeping the other five fields at 100 %. An unseen `country` is the design; an unseen `strat_hh_type` is a bug, and today one gate cannot tell them apart. **Do not weaken the threshold** — narrow the field set, and name the narrowing. |
| **(b)** | the unmeasured half of (a) | 🔴 **Add a measurement, not a waiver.** Nothing currently reports what the model does with the unseen country token. Cheapest honest version: at Step 7, generate one held-out batch with the country token **and** one with it replaced by each held-in token, and report whether the output moves. If it does not move, the token is inert and the conditioning is carried entirely by the other five fields — which would be a **major** result about how transfer is actually working, and it is invisible to every gate now written. |
| **(c)** | `G6.7`'s encoder path | Add a declared control-token hook to `encoder.py` (e.g. an explicit opt-in argument, default off, refusing silently-unknown values as it does now), **and prove it a no-op** by re-encoding the corpus and asserting byte-identity on all 73,254 records. 🔴 **`prereg.md` is NOT edited** — it is correct; the encoder is what cannot serve it. |

🔴 **`prereg.md` was not touched.** md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified against its sidecar
while this entry was written.

#### What was NOT done here

No marginals were downloaded, no population was synthesised, no IPF was run, no gate was implemented
and nothing was submitted to Speed. **This entry is a reading of the specification against the
artefacts that now exist, and its whole content is three stale cross-references and two gates that
cannot pass.** Work items 5.1–5.4 remain untouched and `outputs_step5/` remains empty.

### 2026-08-20 — 🟢 **`RL24` VETTED. THE MARGINALS ROUTE IS DECIDED BY THE EVIDENCE, NOT BY PREFERENCE: ROUTE 3, THE NATIONAL OFFICES. AND THE ANSWER TO "CAN ONE TABLE DO IT" IS ZERO, THREE TIMES.**

The `A / B / C` question this step was holding open — Eurostat national, Eurostat NUTS-2, or the
national statistical offices — is now answered against checked sources rather than by choosing the
tidiest option. **Route 1 is eliminated on two independent grounds, and neither is negotiable.**

#### What was verified here, by query, not by reading the report

| claim | check run in this session | verdict |
|---|---|---|
| Nomis carries UK-wide `KS102UK` (age), `KS105UK` (household composition), `KS601UK` (economic activity) | Nomis API `def.sdmx.json?search=name-*KS102*` etc. → `NM_159_1`, `NM_1502_1`, `NM_1511_1`, all UK-wide | ✅ |
| `KS601UK` separates `homemaker` from `other_inactive` | cell codelist read from the API: **`Economically inactive: Looking after home or family`** is its own cell, distinct from `Long-term sick or disabled` and `Other` | ✅ |
| Eurostat `CensusHub2` is reachable | HTTP 200, page title `CensusHub`, no decommission notice | ✅ (reachable; contents not audited) |

🔴 **My first Nomis query returned `keyfamilies: null` for all three tables and I nearly recorded them
as non-existent. The query syntax was mine and it was wrong.** Re-run with the correct wildcard form,
all three appeared immediately. **Recorded because a falsifier whose reference is my own expectation
returns the same verdict for "the report is wrong" and "I asked the wrong question".**

#### 🔴 The finding `RL24` reports and that decides the route

**Zero. For every country.** No single published table cross-tabulates our four demographic fields at
our category boundaries — not in Spain, not in the UK, not in Italy. So **multi-table IPF is not a
design choice, it is the only option**, and this step's §5.2 must say so.

**Route 1 (Eurostat) fails on two counts:**

1. 🔴 **`CAS.L`, the mandatory census activity-status classification, merges homemakers with "others"**
   into a single category `2.4`. Splitting it was made **optional** for Member States. **Our
   `strat_econ_status` has `homemaker` and `other_inactive` as separate values**, so Eurostat cannot
   supply our strata while the national LFS tables can — `KS601UK` demonstrably does, verified above.
2. 🔴 **The United Kingdom is in the Eurostat 2011 round and ABSENT from the 2021 round**, post-Brexit.
   And the UK 2021 census was not one exercise: ONS (England and Wales) and NISRA (Northern Ireland)
   in 2021, NRS (Scotland) delayed to **2022**. There is no single UK-wide 2021 table.

**Route 2 (NUTS-2) is not rejected, it is deferred.** It inherits both Route 1 defects and adds
suppressed cells, and 🔴 **a suppressed cell is not a nuisance here — `4thJ_step6_rakeddonor.py` FAILS
hard when a target category has no donor, by design.** Geography is a later extension if the energy
story needs it, and it is not needed for the transfer claim.

#### 🔴 The age floor, answered plainly, and it is worse than "the bands do not line up"

* Published 5-year bands are `0-4, 5-9, **10-14**, 15-19, …`. **No aggregate table isolates `11-14`.**
  It must be built from single-year-of-age population registers (INE Padrón, ISTAT Bilancio
  Demografico, ONS Mid-Year Estimates) or by subtracting age 10.
* **Economic status is not published below 15 (Eurostat, ISTAT) or 16 (Spain, UK) anywhere.** So for
  our entire `11-14` band there is **no** economic-status marginal, and its value must be *assigned*,
  not fitted. `RL24` proposes assigning `student` on the national legal definition; that is defensible
  and it is **an assumption to declare, not a marginal**.
* 🔴 **A gap `RL24` understated, found here in the `KS601UK` codelist: the table is
  `All usual residents aged 16 to 74`.** There is an **upper** cap too. **Our `75+` band has no
  economic-status marginal either.** `RL24`'s negative control 4 mentions "16-74 or 16+" without
  drawing the consequence. So **two of our eight age bands sit outside every economic-status table**,
  at both ends, and both must be assigned rather than fitted.

#### The temporal mismatch, and what it costs `G6.1`

Diary waves 2009-10 (ES), 2013-14 (IT), 2014-15 (UK); census rounds 2011 and 2021. **No census year
matches any wave.** `RL24` names annual alternatives covering the actual wave years — INE Padrón + EPA,
ISTAT Bilancio + RCFL, ONS MYE + APS — all open, all with an API.

🔴 **This is a `prereg.md` §5 problem, not only a Step 5 problem.** The raked-donor null must use *"the
same marginals the model was given"*. So whichever basis is chosen, **it must be one basis, used for
both the population synthesis and the null**, and frozen before the first fold is scored. Mixing —
census for the population, annual series for the null — would be the handicap §5 explicitly forbids.

#### 🔴 The one thing in `RL24` that is NOT evidence: every number in its Part C

`RL24`'s answer to *"the question we may not have thought to ask"* is the **household-level versus
person-level denominator mismatch**, and **the mechanism is real, important, and not one of the three
candidates the prompt excluded.** Household-type marginals are counts of *households*; age, sex and
economic status are counts of *persons*. Fitting them together treats one as the other. It is a genuine
defect and this step must handle it.

**But every quantity attached to it is unsourced and must not be carried forward:**

* *"~30-35 % of households are one-person but only ~14-17 % of persons live alone"* — **no citation**.
* *"a severe 2x distortion"* — arithmetic on the two unsourced ranges. **Circular.**
* *"`m_A(11-14)` ≈ 4 %"*, *"`m_E(retired)` ≈ 22 %"*, *"exactly ~880 synthetic persons will be
  12-year-old retirees"* — **no citation**, and 🔴 **the worked example commits the very error it is
  diagnosing**: `m_E(retired)` is defined over the 15+ or 16+ population while `m_A(11-14)` is over the
  whole population, so the product is a person-base mismatch. It also assumes IPF returns the
  independence product, which it does not for a non-uniform seed.
* It is tabled as `B19`, **`Inference`, source "Mathematical analysis", Tier 1, confidence H.** An
  inference with no document is not Tier 1.

**Salvage the route, not the table:** adopt the household-to-person conversion and the structural-zero
mask; measure the actual shares from the published tables ourselves; quote none of `RL24`'s numbers.

🟢 **And note what the mechanism confirms:** `G5.2` (joint plausibility, zero persons in structurally
impossible cells) and `V5.a` (the impossibility table must be non-empty and must actually bind) were
written for exactly this, before `RL24` existed. **An outside reader independently rediscovered why
those gates are in the list**, which is the best evidence we have that they are the right gates.

#### `D-S5-1` update

* **(a) `G5.4` field scope** — unchanged and still open; `FINDING 40` is untouched by `RL24`.
* **(b) measure the unseen-token effect** — unchanged and still open.
* **(c) encoder control-token hook for `G6.7`** — unchanged and still open.
* **NEW, and it belongs with them: the marginals basis.** Census 2011 as the frozen primary, with the
  annual series as a declared sensitivity, is `RL24`'s recommendation. **It is a `prereg.md` §5 basis
  decision and must be taken before the first fold is scored.**

---

### 2026-08-20 (evening) — 🟢 **THE MARGINALS BASIS IS RULED: THE CENSUS ROUND IS THE FROZEN PRIMARY, THE ANNUAL SERIES IS A DECLARED SENSITIVITY. THIS IS A `prereg.md` §5 BASIS DECISION AND IT IS NOW TAKEN.**

**Ruled by the author 2026-08-20.** Combined with the route decided by `RL24` above, the basis is now
fully specified and **nothing in Step 5 is waiting on a source question any more**:

| | ruled |
|---|---|
| **route** | **Route 3 — the national statistical offices.** Decided by evidence, not preference: Eurostat merges homemaker with other-inactive (`CAS.L` category `2.4`, splitting it optional) and drops the UK from the 2021 round entirely. |
| **basis** | **The census round is the FROZEN PRIMARY.** INE / Nomis / ISTAT census tables supply the marginals. |
| **the annual series** | **A DECLARED SENSITIVITY, not a second basis.** INE Padrón + EPA, ISTAT Bilancio + RCFL, ONS MYE + APS are run as a robustness check and reported as one, never mixed into the primary. |

#### 🔴 What this ruling binds, and it binds harder than a Step 5 choice normally would

`prereg.md` §5 requires the raked-donor null to use **the same marginals the model was given**. So this
is **one basis serving two consumers** — the population synthesis and `G6.1`'s null — and it must be
frozen **before the first fold is scored**. It now is. **Mixing bases — census for the population,
annual series for the null — is the handicap §5 explicitly forbids, and the ruling forecloses it.**

`4thJ_step6_rakeddonor.py` already **refuses** the mixed case in code: `score_margin()` raises
`RakeError` when `model_source` and `null_source` differ as strings. 🟢 **The guard was written before
the ruling existed and the ruling is exactly what it was guarding.** That is the shape we want — the
code refuses the favourable construction, and the decision then agrees with it.

#### 🔴 The cost the ruling accepts, stated plainly so it is never discovered later

**No census year matches any diary wave.** Waves are ES 2009-10, IT 2013-14, UK 2014-15; rounds are
2011 and 2021. The primary basis is therefore **1 to 4 years off in every fold, and off by a different
amount in each**:

| fold | diary wave | census primary | gap |
|---|---|---|---|
| `es` | 2009-10 | 2011 | ~1-2 years |
| `it` | 2013-14 | 2011 | ~2-3 years |
| `uk` | 2014-15 | 2011 | ~3-4 years |

**This is a third per-fold asymmetry**, alongside D-S6-2's Eurostat wave gap and `FINDING 39`'s
country-dependent MAPE rounding floor. 🔴 **It must be reported per fold and never averaged**, and it
is the reason the annual-series sensitivity is not optional decoration: it is the only thing that will
tell a reader whether the gap moved anything.

#### What is still open in `D-S5-1` — three items, unchanged by this ruling

**(a) `G5.4` field scope**, **(b) measuring what the model does with the unseen `country` token**, and
**(c) the `G6.7` encoder control-token hook** are **all still open**. `FINDING 40` and `FINDING 41` are
untouched. Only the basis item is closed here.

#### The two age bands that no marginal covers, and what the ruling does NOT solve

The ruling does not touch the gap found above: **`11-14` and `75+` sit outside every economic-status
table**, at both ends (`KS601UK` is *aged 16 to 74*; Eurostat and ISTAT publish nothing below 15, Spain
and the UK nothing below 16). **Two of eight age bands must be ASSIGNED, not fitted**, under any basis.
That is an assumption to declare in `G5.3`'s provenance column, and it is not made smaller by choosing
the census.

**Nothing was downloaded and no IPF was run in this entry.** `outputs_step5/` remains empty; work items
5.1-5.4 remain untouched. 🔴 **Step 5.1 is on the critical path of the CLAIM** — `G6.1`'s bar rakes onto
the held-out country's published marginals — and it is now unblocked on every question except the three
`D-S5-1` items above, none of which block the download. **`prereg.md` not touched**, md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar.

---

### 2026-08-20 (night) — 🟢 **`outputs_step5/` IS NO LONGER EMPTY. THE UNITED KINGDOM MARGINALS ARE BUILT AND VERIFIED, ONE FOLD OF THREE. AND 🔴 `FINDING 48`: OUR THREE CORPORA GIVE THE `11-14` BAND THREE DIFFERENT ECONOMIC STATUSES, DETERMINISTICALLY, WHICH IS A COUNTRY FINGERPRINT IN A LEAVE-ONE-COUNTRY-OUT DESIGN.**

The ruling of the previous entry unblocked the download and the download was done. **Nothing was
estimated, nothing was re-typed**: four Nomis tables were retrieved, stored verbatim under
`outputs_step5/raw/` with their md5s, and every figure below is a summation of those files.

`outputs_step5/marginals_uk.csv` — 25 category rows, md5 `1a7cb9d749b565ec6d8aaadba4567430`.
`outputs_step5/marginals_provenance.md` — the full derivation, cell by cell.

🔴 **Item 5.1 is NOT complete.** One country of three. **`G6.1` can now be computed for the `uk` fold
and for no other.**

#### What was retrieved, and the one thing that nearly stopped it

| field | table | Nomis id | base |
|---|---|---|---|
| age | `QS103UK` age by **single year**, UK-wide | `NM_1531_1` | 55,053,949 persons aged 11+ |
| sex | `KS101UK` usual resident population | `NM_158_1` | 63,182,178 persons, **all ages** |
| household type | `KS105UK` household composition | `NM_1502_1` | 26,442,096 **households** |
| economic status | `KS601UK` economic activity | `NM_1511_1` | 46,410,490 persons aged **16 to 74** |

🔴 **A silent-failure trap, recorded because it is the same shape as one we already carry.** The Nomis
range syntax `cell=0...9999999` returns **HTTP 200 with a zero-byte body**. Four downloads reported
success and produced four empty files. That is the tcsh `2>/dev/null` failure mode in a different
costume: **a status code that says yes and a payload that says nothing.** Omitting the filter returns
the full codelist. **Any script that checks only the HTTP code here will report a marginals file it did
not build.**

#### 🟢 The `11-14` band is solved for the UK, exactly, and it retires an unsourced number

`QS103UK` publishes single years of age UK-wide, so `11-14` is **summed, not subtracted and not
estimated**. The 101 single-year cells sum to **63,182,178**, the table's own published total,
**difference 0**.

`RL24` asserted `m_A(11-14) ≈ 4 %` with no citation and it was rejected on that ground. The measured
value is **4.703 % of all ages, 5.398 % of the 11-plus base**. 🔴 **Quote the measured figure with its
base. Never `RL24`'s.**

#### 🟢 The route decision is confirmed in the numbers, not just in a codelist

Our six economic-status bands partition `KS601UK` with **residual exactly 0**: 28,607,397 + 2,054,146 +
4,296,273 + 6,443,875 + 1,981,470 + 3,027,329 = **46,410,490**, the published base.

Two nesting checks were run first, because a category that is a *subset* rather than *disjoint* would
have double-counted and the sum would still have looked plausible:

* In employment + Unemployed + active full-time student = 32,268,535 = *Economically active*. So the
  active-student cell is **disjoint** and safe to add to the inactive-student cell.
* Employee part-time + full-time + self-employed = 28,607,397 = *In employment*.

**`RL24`'s central claim about the route is now confirmed against the file itself:** the national table
separates *Looking after home or family* (1,981,470) from *Long-term sick or disabled* and from
*Other*. Eurostat's `CAS.L` merges them. **The route rests on a real distinction and we have seen it.**

#### 🔴 `FINDING 48` — the `11-14` band carries a different economic status in each of our three countries, with no overlap at all

Measured on the fetched corpus, cross-tabulating `strat_age_band` against `strat_econ_status`:

| fold | `11-14` diaries | economic status assigned | determinism |
|---|---|---|---|
| `es` | 711 | **`student`** (710) plus one `employed` | 99.86 % |
| `uk` | 896 | **`other_inactive`** (896) | **100 %** |
| `it` | 1,644 | **`unknown`** (1,644) | **100 %** |

🔴 **Italy's entire `strat_econ_status = unknown` mass IS the `11-14` band — 1,644 of 1,644, exactly.**
Not approximately: the count of Italian `unknown` records and the count of Italian `11-14` records are
the same number, and the cross-tab shows no Italian `unknown` outside that band. So what Step 2
reported as an Italian non-response asymmetry (`it` 4.243 % versus `uk` 0.519 %) is **not non-response
at all in Italy's case. It is an age rule**, and it is the same age rule `RL24` found in the published
tables: economic status is not defined below 15.

The UK's 68 `unknown` records are a different thing entirely — they are scattered across six adult
bands (`15-24` 24, `25-34` 12, `35-44` 8, `45-54` 12, `55-64` 8, `65-74` 2, `75+` 2) and are genuine
item non-response. **Two countries, one label, two mechanisms.** The Step 2 escalation was right to
fire and its stated reason was incomplete.

**Why this is a leave-one-country-out problem and not a data-cleaning note.** The pair
`(11-14, econ_status)` is a **country fingerprint**. When `it` is held out, the training data contains
`es,11-14,...,student` and `uk,11-14,...,other_inactive` and nothing else; the true Italian convention,
`unknown`, is absent from training by construction. Whatever we put in the synthetic Italian prefix, we
are choosing between a value the model has seen paired with the wrong country and a value it has never
seen paired with any. 🔴 **This is `FINDING 40`'s unseen-token problem again, arriving through the
population synthesis instead of through the `country` token, and `D-S5-1(b)` — "measure what the model
does with an unseen prefix value" — now has a second, sharper instance to measure.**

**It also disposes of `RL24`'s proposal by measurement.** `RL24` recommended assigning `student` to the
`11-14` band on the national legal definition. That matches Spain, **contradicts the UK outright**, and
**contradicts Italy outright**. It is not a neutral convention; it is Spain's convention. **Assigning it
to all three folds would silently impose one country's coding on the other two**, in the one design
where that is the specific thing we must not do.

#### 🔴 A household category that does not map, and it is 8.06 % of the UK

`KS105UK` publishes **"One family only: All aged 65 and over" = 2,131,191 households, 8.060 %**, as a
category *outside* the married / cohabiting / lone-parent breakdown. Disjointness confirmed by
arithmetic: 2,131,191 + 8,785,131 + 2,554,054 + 2,851,354 = 16,321,730 = *One family household*.

It is a one-family household so it is not `one_person`; the table says nothing more. **It is written
into the CSV as its own row with `status = AMBIGUOUS_needs_author_ruling` and is NOT folded into
`couple_no_children`**, which is what it mostly is and which is exactly the quiet assumption this
project's gates exist to catch. Our five bands otherwise account for 24,310,905 of 26,442,096, or
91.94 %.

#### 🔴 No UK-wide census table of sex by age exists, so the sex marginal is an approximation

`QS103UK` has no sex dimension. `DC1117EW` and `LC1117EW` have sex by single year but are **England and
Wales only**. The UK sex rows therefore carry the **all-ages** split (male 49.109 %, female 50.891 %)
and `status = APPROXIMATION_ALL_AGES`.

The error is small in aggregate and **concentrated in `75+`**, where the sex ratio actually diverges.
🔴 **That is also the band with no economic-status marginal. Two weaknesses coincide in one stratum**,
and the limitations section must say so rather than list them separately.

#### 🟢 `RL24`'s denominator mechanism is confirmed, with both sides measured and neither taken from it

`RL24` named the household-versus-person denominator mismatch and attached **no citation to a single
number**, so its figures were rejected. Both sides are now real:

| | source | UK |
|---|---|---|
| one-person **households** | `KS105UK`, census | **30.584 %** |
| diarists who **live alone** | our corpus, 2,290 of 15,854 | **14.444 %** |
| ratio | | **2.12x** |

**The distortion is a factor of 2.1 and it is now derived from one published table plus our own corpus.**
Fitting a household margin against person margins without conversion puts roughly twice as many
synthetic people in one-person dwellings as belong there. Per fold the person-side share is `es`
8.955 %, `uk` 14.444 %, `it` 15.564 % — **not transferable between countries**, so the conversion is
per fold.

#### Spain and Italy: nothing downloaded, and why

* **Spain.** `servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES` is live and usable, but the
  **2011 Censos de Poblacion y Viviendas is not in the operations list**. What is there — Padron, EPA,
  Cifras de Poblacion — is the **annual** basis, which this project's ruling makes a sensitivity and
  not the primary.
* **Italy.** `dati-censimentopopolazione.istat.it` returned **HTTP 302**. `esploradati.istat.it` serves
  a 10 MB dataflow list in which **no dataflow is named for the census in English or Italian**; the
  population dataflows present are `Popolazione residente ricostruita` and the projections, again the
  annual basis.

**No Spanish or Italian number appears in any file.** Both were handed to a new deep-research round,
**`L26_es_it_census_marginals.md`**, written today. `L26` is unusual in the series in one respect:
**it carries the finished UK numbers as a calibration target** and makes "did you reproduce them"
a mandatory negative control, on the reasoning that a report which cannot reproduce a figure we have
already verified should not be believed on the two countries we cannot check.

#### Two author decisions this entry opens

| | question | recommendation |
|---|---|---|
| **`D-S5-2`** | The 8.06 % `One family only: All aged 65 and over` block. Fold into `couple_no_children`, split it pro rata between `couple_no_children` and `single_parent_with_children`, or hold it out until `L26` D2 reports whether ONS publishes a split? | 🔴 **Hold, pending `L26` D2.** It is 8 % of the household base and pro-rata splitting invents a composition the source declines to state. |
| **`D-S5-3`** (🟢 RULED 2026-08-20: `unknown` for `11-14` all folds, `75+` = `retired`; applied in `econ_11plus_<c>.csv`, see the late-night entry) | `strat_econ_status` for `11-14` and `75+`, which no census publishes at either end. Assign one convention to all folds, or assign each fold its own observed convention? | 🔴 **Neither as stated, and `FINDING 48` is why.** One convention imports Spain's coding into the UK and Italy; per-fold conventions require reading the held-out country's microdata, which is contamination. **Recommend a THIRD option: assign `unknown` to `11-14` in all three folds**, since `unknown` is a declared value of the field in the crosswalk for all three countries, it is the value Italy actually uses, and it is the only choice that asserts nothing the source does not say. `75+` is a separate and easier case, but state its weak fold: `retired` is the corpus modal value in all three, at `uk` 1,232 of 1,292 (95.4 %), `it` 3,420 of 4,753 (71.9 %) and `es` 1,138 of 1,933 — **only 58.9 %, because Spain also records 251 `homemaker` and 539 `other_inactive` at 75+**. So `retired` is defensible as a single convention and is NOT clean in Spain, and the Spanish figure must be quoted alongside it. |

**`prereg.md` not touched**, md5 verified against its sidecar. **No gate was run and no verdict was
changed by this entry.**

---

### 2026-08-20 (late) — `RL26` VETTED BY RE-DERIVATION. 🟢 **SPAIN IS BUILT FOR THREE OF FOUR FIELDS AND `D-S5-2` IS ANSWERED.** 🔴 **TWO NEW FINDINGS: SPAIN PUBLISHES NO ECONOMIC-ACTIVITY CENSUS TABLE, AND OUR MARGINALS ARE ON THE WRONG UNIVERSE.**

`RL26` returned. It was vetted the way `RL24` and `RL25` were: **by opening the sources and
recomputing, not by reading the report.** Fourteen of its claims were tested. The route survives; the
Spanish arithmetic does not.

#### 🟢 What survived, and it unblocked Spain the same evening

`RL26`'s central mechanical claim is **true and was confirmed by retrieval**: the Censo 2011 is not in
the Tempus3 JSON API because INE runs two dissemination architectures, and the census lives as static
PC-Axis files under `https://www.ine.es/jaxi/files/_px/es/px/t20/e244/`. Four `.px` files were
downloaded on that pattern, all HTTP 200.

`outputs_step5/marginals_es.csv` — **22 rows, md5 `eff025b704ca993d35ba2ca2de5c335e`**, built by
`tools/4thJ_step5_build_es.sh` from the two files now stored verbatim in `raw/`. **Not one value came
from the report.**

* **Age.** `03001.px` is single year of age **by sex**, so the `11-14` band is summed exactly as for
  the UK: **1,746,617.18 of an 11-plus base of 41,493,161.67 = 4.209 %**. Partition residual `0.0000`.
* 🟢 **Sex is EXACT for Spain, where it is an approximation for the UK.** Because `03001.px` carries
  both dimensions, the Spanish sex marginal is computed **on the 11-plus base** (male 49.075 %, female
  50.925 %) instead of the all-ages split the UK is stuck with. **The `75+` stratum has two weaknesses
  in the UK and one in Spain**, and the limitations text must not describe them as symmetric.
* **Household type partitions EXACTLY into our five bands**, residual `-0.0003` against 18,083,692.31
  households, and a **nesting check on a second axis** confirms the mapping: the four one-person
  *structure* cells sum to `4,193,319.34`, which is precisely the `1 persona` *size* column,
  **residual 0.0000**.
* 🟢 **Spain has no analogue of the UK's 8.06 % unallocated block** — its age-defined household
  categories are one-person cells and map without ambiguity. **`D-S5-2` is a UK-only problem.**

#### 🔴 A structural property of the Spanish census that changes how a marginal is checked

`03001.px` reads `DATA=4.6815916442321E7 ...`. **The Censo 2011 is sample-based and grossed up, so
every published cell is a float** — the national total is `46,815,916.44`. **The `residual == 0` test
that the UK tables pass exactly cannot be applied to Spain.** The builder reports a float residual
instead; both partitions close to better than 0.001 persons.

This is also the mechanism behind the report's errors: `RL26` rounded each band before summing, so its
eight band counts are off by 1 to 4, and **its own 11-plus base is internally inconsistent by 5**
(`41,493,158` stated against `41,493,163` implied by total minus under-11). Caught by arithmetic on
the report before any file was opened; confirmed against the file afterwards.

#### 🔴 `FINDING 49` — Spain publishes NO economic-activity census table for the general population

`RL26` names matrix `03007.px` as the Spanish economic-activity source in four separate places. **The
file was downloaded and its own `TITLE` field reads *"Poblacion en establecimientos COLECTIVOS por
sexo, nivel de estudios completados y relacion con la actividad economica"*** — the institutional
population, roughly 0.27 M persons. It is the wrong universe by two orders of magnitude. **This is the
`FINDING 47` class again: a citation that resolves to a different object than the one claimed**, and
it was invisible from the report because the URL is real and returns HTTP 200.

**The absence was then established directly rather than inferred from one wrong citation.** INE's own
results index lists every published Censo 2011 tree — `avance`, `hogares`, `nucleos`, `colectivos`,
`vinculada`, `edificios`, `viviendas`. **None is about economic activity.** The national population
tree holds exactly eight matrices (`03001`-`03008`), all on nationality, birthplace or foreign
population; `03009` and above return HTTP 204.

So the Spanish `strat_econ_status` marginal **cannot be had from a static published census table on
the frozen basis.** It is written into the CSV as `NOT_AVAILABLE`, status
`NO_STATIC_CENSUS_TABLE_see_provenance` — **a blank, not a zero and not a guess.**

#### 🔴 `FINDING 50` — our marginals are fitted on the wrong universe, and the evidence was already on disk

`RL26`'s Part E raises the one thing neither we nor `RL24` had asked: census marginals enumerate **all
usual residents**, while HETUS samples **private households only**. The UK numbers are in `KS101UK`,
in `raw/`, in cells we had downloaded and not read:

| `KS101UK` cell | count |
|---|---|
| All usual residents | 63,182,178 |
| **Lives in a household** | **62,055,838** |
| Lives in a communal establishment | **1,126,340** |

**1,126,340 persons, 1.78 %, and they are not distributed evenly** — communal residents concentrate in
`75+` (care homes) and `15-24` (halls of residence, barracks). Our `marginals_uk.csv` age and sex rows
are on the 63.18 M base; the household-type rows are on private households by construction. **Fitting
one against the other pushes institutional residents into private dwellings, and the modal destination
is `one_person`** — which is already the band the denominator mismatch inflates. **Two independent
errors pushing the same stratum the same way.**

🔴 **The uncomfortable part is that this was found in a file we already had.** The Nomis response
carried the two cells all along and the build read only the first three.

#### 🔴 What did NOT survive the vetting

| `RL26` claim | verdict |
|---|---|
| Spain age band counts | **off by 1 to 4**, base internally inconsistent by 5 |
| `03007.px` is the Spanish economic-activity table | **FALSE** — collective establishments |
| "no upper age ceiling on Spanish economic activity" | **UNSUPPORTED** — no static table exists to have a ceiling |
| "3,509,545 ... proves over 98.4 % are pensioner couples" | **NON SEQUITUR.** `QS111UK` was downloaded: that cell is *HRP aged 65+, 2+ person, no dependent children*, a superset of the block in question. The 98.4 % does not follow from the two cells cited |
| "8 of 8 country-field combinations have retrieved numbers" | **FALSE — 3 of 8.** Spain has no economic-status numbers and Italy has no numbers at all |
| "No unverified counts. Every figure directly parsed" | **FALSE**, per the two rows above |
| Italy: six `DF_DCSS_*` dataflows and all Italian numbers | **UNVERIFIED.** On re-check `esploradati.istat.it` returned `HTTP 000` after a ~21 s connect failure on seven requests, while `www.istat.it` returned 200 from the same machine. The host answered earlier the same day, so this is an outage and **not** evidence against the report — but nothing was confirmed and **no Italian number is in any file** |
| "Did you recommend Eurostat or an annual series?" | 🟢 **NO.** The frozen basis was respected throughout — the guard clause worked |

#### 🟢 `D-S5-2` is answered, and by the stronger of the two arguments

`QS112UK` (`NM_1537_1`) was downloaded and parsed. The category *"One family only: All aged 65 and
over"* holds **4,263,276 persons**, exactly as reported, against the **2,131,191 households** we
already had from `KS105UK`. Disjointness holds on the person base too:
`4,263,276 + 27,677,022 + 75,188 + 7,162,262 + 7,409,415 = 46,587,163` = *One family only: Total*,
**exactly**.

Mean size = **2.00042 persons per household**. A one-family household holds at least two people, so
the excess over `2 x 2,131,191` is **894 persons** — **at most 894 of 2,131,191 households, 0.042 %,
contain more than two people.** That is a far tighter bound than `RL26`'s 98.4 %, and unlike it, it
follows from the cited numbers.

| | ruling | note |
|---|---|---|
| **`D-S5-2`** | 🔴 **Recommended: map the block to `couple_no_children` with a stated caveat.** | 99.958 % of it is a two-person one-family household. The residue the table genuinely cannot resolve is the two-person **lone parent with a 65+ non-dependent child**, which requires a parent aged ~85+ and is demographically rare. State that the block was assigned, state the 2.00042, and state that the couple-versus-elderly-parent-and-child split is not published. **This supersedes the earlier HOLD**, which was correct while the evidence was missing. |

#### Two new decisions this entry opens

| | question | recommendation |
|---|---|---|
| **`D-S5-4`** | Spain has no static census table for economic status. Take it from the INE *Resultados detallados* on-demand query tool, take it from the Censo 2011 person microdata (`RELAC`), or declare the field unavailable for the `es` fold? | 🔴 **Recommended: the INE query tool, and only if it returns a citable table identifier.** Microdata means **we** tabulate the marginal, which is a different basis from "published aggregate" and would make `es` the only fold whose econ marginal we computed ourselves — an asymmetry inside a LOCO design, which is the specific thing this design cannot absorb. If the query tool yields nothing citable, **declare the field unavailable for `es` and fit without it**, which is honest and symmetric with the `11-14`/`75+` gaps we already declare. |
| **`D-S5-5`** | Fit the marginals on all usual residents, or restrict them to residents of private households to match the HETUS frame? | 🔴 **Recommended: restrict to private households.** The mismatch is 1.78 % in the UK and concentrated in exactly the two bands we are weakest in. The correction is a division by a published cell that is already in `raw/`, so it costs nothing and removes an error we would otherwise have to declare. It requires rebuilding `marginals_uk.csv` on the 62,055,838 base and finding the equivalent Spanish cell (the `colectivos` tree). |

**`prereg.md` not touched**, md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar. **No
gate was run and no verdict was changed by this entry.**

---

### 2026-08-20 (night) — **ALL THREE OPEN `D-S5-*` DECISIONS RULED AND APPLIED.** 🟢 **BOTH BUILT FOLDS ARE NOW ON THE PRIVATE-HOUSEHOLD FRAME, AND SPAIN IS COMPLETE IN ALL FOUR FIELDS.** 🔴 **`FINDING 51`: THE SPANISH CENSUS HAS NO `homemaker` CATEGORY. ITALY IS STILL UNREACHABLE AND IS NOW THE WHOLE OF WHAT STEP 5.1 HAS LEFT.**

The author ruled `D-S5-2` (a), `D-S5-4` (b) — **against my recommendation** — and `D-S5-5` for the
option carrying the most precision. All three are applied. Full derivations, tables and hashes are in
`outputs_step5/marginals_provenance.md`, which is now in two parts: sections 1-6 describe the files as
first built, **Part II (sections 7-11) supersedes them.**

| file | before | after |
|---|---|---|
| `marginals_uk.csv` | md5 `1a7cb9d749b565ec6d8aaadba4567430`, 25 rows, all usual residents | **md5 `5bd9d6c7feadcc2382e573a76d2f7b7e`**, 23 rows, **private households** |
| `marginals_es.csv` | md5 `eff025b704ca993d35ba2ca2de5c335e`, 3 of 4 fields | **md5 `32e1d97d0c107ee8d2eb7034abd18a8a`**, **4 of 4**, private households |
| `marginals_provenance.md` | 351 lines | **663 lines** |

#### 🟢 `D-S5-2` ruled (a) — the 8.06 % block folded, and the partition now closes exactly

`QS112UK` was downloaded and stored: the *One family only: All aged 65 and over* block is
**4,263,276 persons in 2,131,191 households = 2.00042**, and disjointness holds on the person base to
the unit. The excess over two per household is **894 persons**, so **at most 894 households — 0.042 %
— hold more than two people.** Folded into `couple_no_children`, which becomes **6,755,763
(25.5493 %)**; `hh_partition_sum = 26,442,096` against a published base of `26,442,096`, **residual 0**,
where before it was short by exactly the block. The limitation to declare is that the
couple-versus-elderly-parent-and-adult-child split is **not published**; the residue the assignment
cannot be right about needs a parent aged ~85+.

#### 🟢 `D-S5-5` ruled — and it is not a cosmetic correction

**UK.** `QS419UK` gives the communal population as **1,126,340**, equal to `KS101UK`'s
63,182,178 − 62,055,838 to the person. 🔴 **No UK-wide table crosses residence type with age** — the
78-table UK-suffixed catalogue was enumerated on Nomis and every such table (`DC1104EW`, `LC1104EW`,
`LC1105EW`, `DC1602EWla`) is England-and-Wales only, with Scotland and NI not on Nomis and
`scotlandscensus.gov.uk` serving a JavaScript shell. So the **E&W band profile is scaled to the UK
total**, `k = 1,126,340 / 1,004,799 = 1.12096051`, and E&W is 88.8 % of the UK, so only the residual
11.2 % is borrowed. **What it moved: `75+` −6.79 %, `15-24` −5.61 %, `student` −9.56 %,
`other_inactive` −5.16 %.** Age and econ partitions both close at **residual 0.00**. 🔴 **Two thirds of
the whole correction lands on the two bands this study is already weakest in** — care homes and halls
of residence — and without it IPF would have been fitting 332,474 care-home residents into private
dwellings. The economic vector came from `DC1602EWla`, whose `65+` band is split to `65-74` by
**40,838 / 337,435 = 0.121025**, a ratio *measured* against `DC1104EW` — the two tables agree on the
65+ communal total to the person. **The sex row is unchanged in kind: still `APPROXIMATION_ALL_AGES`,
so `75+` still has two weaknesses in the UK and one in Spain.**

**Spain.** INE's microdata universe is stated on line 2 of its own record layout — *"persona residente
en viviendas principales"* — so no subtraction is needed. 🟢 **The claim was verified arithmetically:**
published total **46,815,916.44** minus the **241,186.87** people *usually resident* in collective
establishments (`colectivos/01002.px`) is 46,574,729.57, against a microdata weighted total of
**46,574,725.58** — **a gap of 3.99 persons on 46.8 million.** 🔴 **This is also why `RL26`'s Spanish
collectives figure is unusable:** the collectives table's own total is **444,100.79**, but over 45 % of
those people are registered as usually resident elsewhere and the census already counts them in their
family dwelling. `RL26` quoted 271,760, which matches neither number (the nearest published figure is
`Residencias de personas mayores`, 270,285.89, one type of five).

🔴 **The most useful single comparison this produced.** The UK `15-24` band loses **5.61 %** to
communal establishments; the Spanish `15-24` band loses **0.034 %** — **a factor of 165.** British
students live in halls, Spanish students live at home. It is invisible in any all-resident marginal, it
lands squarely on `strat_age_band × strat_hh_type`, and **any LOCO result on `uk` or `es` involving
young adults has to be read with it in view.**

#### 🔴 `D-S5-4` ruled (b) — microdata — and it delivered five of our six bands

`Microdatos_personas_nacional.zip` (155,860,498 bytes, md5 `0c8f9b44b70b079b25f2f20fdbd2e83f`) expands
to a 1.16 GB fixed-width file of **4,107,465 person records**, tabulated in one streaming pass by
`tools/4thJ_step5_build_es_micro.sh`. On the 16-74 base that matches `KS601UK`: employed 49.8007 %,
unemployed **20.9115 %**, student 5.5092 %, retired 14.9912 %, other_inactive 8.7874 %, **partition
residual 0.0000** on 35,026,085.07.

🔴 **`FINDING 51` — the Spanish census never asked the question.** `RELA` has **six** values and
neither *Labores del hogar* nor *Estudiante* is among them. `student` is recoverable by crossing
`RELA = 6` with a non-blank `ESCUR1`; **`homemaker` is not recoverable at all.** `RL26` states twice
that `RELA` "explicitly distinguishes Category 6 *Labores del hogar* from Category 7 and Category 8" —
**false for the public microdata file, and it was one of the two grounds on which it recommended this
route.**

🔴 **The size of it, and it is not small.** The Spanish corpus has **11.140 % of diarists in
`homemaker`**. The census's entire residual inactive band, homemakers included, is **8.787 %**. *The
category that must contain every homemaker is smaller than the homemaker band alone.* The two
instruments do not classify Spanish inactivity the same way and IPF cannot repair it. **Fit `es` on a
five-band collapsed econ vector and declare it; do not fit six bands for Spain.**

🔴 **The asymmetry `D-S5-4` was ruled against my recommendation to avoid is now real and must be
declared, not discovered.** The UK econ marginal is a published aggregate with six bands; the Spanish
one is a table **we tabulated ourselves** with five. In a LOCO design the held-out country's marginal
carries the whole of the null's information, so the folds are not scored against sources of equal
standing. ⚪ One thing the ruling bought that was not anticipated: because the microdata universe *is*
private households, `D-S5-4` and `D-S5-5` are satisfied by the same file, with the 3.99-person
reconciliation as proof.

⚪ **Spain's `unemployed` at 20.91 % against the UK's 4.46 %** is not an error — it is Spain in 2011,
and it is the largest cross-country difference in any marginal we hold. It will dominate the raked
donor null for the `es` fold.

#### 🔴 One consequence the author has not been asked about

`D-S5-1` froze the basis as **published census aggregates**. INE publishes no private-household age or
sex distribution — the collectives tables carry **no age dimension at all** (type × sex, type ×
registration, type × municipality size, and that is the entire tree). The only source that has it is
the microdata already admitted for economic status, so **Spain's `strat_age_band` and `strat_sex` are
now microdata-based too**, flagged `PRIVATE_HH_FROM_MICRODATA_D-S5-5`, with the published all-resident
counts kept as `#` reference lines and the per-band differences printed beside them. **This follows
from combining two of the author's own rulings but was not itself ruled on. It is a basis change for
two fields and is the first item owed.**

#### ⚪ Italy — diagnosed, not merely retried

`esploradati.istat.it` **resolves** (`193.204.90.13`, alias `01a-filtro.istat.it`) and then **times out
on TCP 443** — identically under forced IPv4, a browser user-agent, and a direct-to-IP request, at
~21 s each time. `dati.istat.it` now redirects to a notices page and
`dati-censimentopopolazione.istat.it` redirects into `esploradati` itself. **This is an outage or a
block, not a wrong URL**, and Eurostat is not an admissible substitute under `D-S5-1`. `RL26`'s
`DF_DCSS_*` identifiers remain the starting point and remain **unverified**. **No Italian number is in
any file.**

**`prereg.md` not touched**, md5 `e4243e07cdd80c9c846b91f40e3e8c45` re-verified against its sidecar.
**No gate was run and no verdict was changed by this entry.** 🔴 **Step 5.1 is now Italy plus one
yes/no.**

---

### 2026-08-20 (late night) — **THE SECOND ROUND OF RULINGS.** 🟢 **`D-S5-3` IS CLOSED, `FINDING 51` IS APPLIED, AND SPAIN'S MICRODATA BASIS IS NOW RULED RATHER THAN MERELY RECORDED.** 🔴 **APPLYING THE FIVE-BAND FIT SURFACED `FINDING 52`: THE RAKING ENGINE DELETES A DONOR CATEGORY THE TARGET NEVER NAMES, AND REPORTS A PERFECT FIT WHILE DOING IT.** 🔴 **ITALY IS NOW THE WHOLE OF THE CRITICAL PATH.**

The author ruled all three open items, each as recommended. Full derivations and hashes are in
`outputs_step5/marginals_provenance.md`, **Part III (sections 12-15)**, which supersedes Part II's
list of what 5.1 owes.

| item | ruling | effect on disk |
|---|---|---|
| §9.2 — Spain's age and sex basis | **keep the microdata basis** | none; `marginals_es.csv` unchanged, md5 `32e1d97d0c107ee8d2eb7034abd18a8a` |
| `FINDING 51` — the Spanish econ fit | **`es` on five bands, `uk` on six** | `tools/4thJ_step6_rakeddonor.py` 173 → 227 lines; selftest 133 → 194 lines, **23 → 34 checks** |
| `D-S5-3` — econ status outside 16-74 | **`unknown` for `11-14` all folds; `75+` = `retired`** | 🟢 **NEW** `econ_11plus_uk.csv` md5 `b4b3935816bf238c2f3c3248e578412f`, `econ_11plus_es.csv` md5 `24e3b6f3625f8dc2a3dff9ba38db9a73` |

#### 🔴 `FINDING 52` — a null that was about to be built on a pool that had been silently cut by a sixth

Handing `rake()` Spain's **five**-band target against a donor pool carrying **six** is not a
no-op. `rake()` builds its IPF factors only from the categories the target names, so a donor whose
category is absent hits `factor.get(..., 0.0)` and is multiplied by **zero** — not merged, not
flagged, not counted. **Deleted.**

Measured on a 120-donor `uk + it` pool against Spain's five published bands: **20 of 20 `homemaker`
donors given weight exactly `0.0`, 16.67 % of the pool gone, `max_dev_pp` reported as 5.6e-15, and
no error raised.** 🔴 **The diagnostic reports a flawless fit precisely because it converged on the
categories that survived** — the sixth had been annihilated before the deviation was measured, and
nothing in the return value shows it. Implemented naively, the `es` null would have looked *better*
for having lost a sixth of its donors.

⚪ **The engine already guarded the mirror image and it does not catch this.** `rake()` refuses a
target naming a category **no donor has** ("IPF cannot create them"). The dangerous direction — a
donor carrying a category **the target never names** — was open. A check that passes for the wrong
reason is indistinguishable from a check that passes.

**Fix, additive.** A new optional `collapse={variable: {donor_category: target_category}}` applied to
a *copy* of the donors before raking, with its own two guards; and **Guard 5**, which raises on any
orphan donor category, naming the count and the categories. 🟢 **A collapse is stamped onto the
provenance label** — `…marginals_es.csv@2026-08-20|collapse=strat_econ_status:homemaker>other_inactive`
— which buys a third protection free: `score_margin()`'s existing handicap guard **now refuses to
compare a five-band null against a six-band model** without a line being written for it.

**Seen failing, then seen passing.** Guard 5 fires on the uncollapsed pool; the collapsed run
converges at 3.89e-14 pp keeping **120 of 120** donors; collapsing into an unnamed category and
collapsing a variable nobody rakes on are both refused; callers that never needed a collapse come
back `collapse=None` with the label untouched. 🟢 **The 23 pre-existing checks were re-run green
BEFORE the new ones were added**, so the change is *shown* additive, not asserted — the Leg-3
bit-identity precedent, now indexed at `Resources/preprocessing_precedents.md` §4.

🔴 **Step 5.2 must rake `es` with `collapse={"strat_econ_status": {"homemaker": "other_inactive"}}`.**
Not by dropping donors, and not by leaving `rake()` to work it out — as of Guard 5 it will refuse.

#### 🟢 `D-S5-3` applied — and the age bands do not align with the econ base

The censuses publish economic activity for **16-74**; the synthetic population starts at **11**.
`11-14` → `unknown`, `75+` → `retired`, both as ruled. 🔴 **But `15-24` straddles the econ base, so a
third slice falls out that `D-S5-3` did not cover: the 15-year-olds.** They are **1.415 %** of the
UK's 11+ base and **1.027 %** of Spain's. Assigned `unknown` by the ruling's own argument — the
census is equally silent at 15 — and flagged as **a one-line confirmation owed**. Reading it off the
corpus was rejected for the two reasons that already killed `RL24`'s proposal: it would either
import one country's convention as universal, or require reading the held-out country's own data.

The slice is never counted directly. It is the **residual** of the four bases already in
`marginals_<c>.csv`, so it cannot drift from them:
`age15 = base(11+) − band(11-14) − base(16-74) − band(75+)`.
🟢 **Independently checked for the UK**, where `QS103UK` publishes single years: 774,892 minus the
scaled `DC1104EW` communal count (11,571.87) gives 763,320.13 against a residual of 763,320.32 —
**the two agree to 0.19 persons.**

| | `uk` | `es` |
|---|---|---|
| `unknown` (= `11-14` + age 15) | **3,712,013.70 (6.882 %)** | **2,170,562.74 (5.261 %)** |
| `retired` (= published + `75+`) | **10,964,343.30 (20.327 %)** | **9,308,468.47 (22.564 %)** |
| `homemaker` | 1,979,621.62 (3.670 %) | **blank — `FINDING 51`** |
| partition residual vs base | **−0.00** | **0.00** |

🔴 **`retired` roughly doubles and becomes the second-largest band** — UK 14.02 % → **20.33 %**,
Spain 14.99 % → **22.56 %**. Any statement about retired-person occupancy must name its base. **The
two files are not interchangeable:** `marginals_<c>.csv` carries published fields on published bases,
`econ_11plus_<c>.csv` carries a *convention* applied on top. Step 5.2 rakes on the latter; anything
citing a census figure quotes the former.

⚪ And `75+` = `retired` is **not clean in Spain**: corpus-modal at `uk` 95.4 % and `it` 71.9 % but
**`es` only 58.9 %**, because Spain also records 251 `homemaker` and 539 `other_inactive` at 75+.
Quote that figure wherever this marginal is used.

⚪ `unknown` now carries real mass (6.9 % uk, 5.3 % es) where in `marginals_<c>.csv` it is a `0` row
flagged `NOT_PUBLISHED`. Donors can carry it: it is a declared crosswalk value in all three
countries, and in Italy it **is** the `11-14` band (`FINDING 48`).

#### 🔴 The LOCO asymmetry is now ruled, not merely recorded

Keeping Spain's age and sex on the microdata basis was the right call against the alternative —
mixing two universes inside one file — but it means **three of Spain's four marginal fields are
tables we tabulated ourselves against three of four published aggregates for the UK.** In LOCO the
held-out country's marginal carries the whole of the null's information, so **the folds are not
scored against sources of equal standing.** A declared property of the design, to be stated wherever
a cross-fold comparison of `G6.1` margins appears.

#### New and changed artefacts

`outputs_step5/econ_11plus_uk.csv`, `outputs_step5/econ_11plus_es.csv`,
`tools/4thJ_step5_econ11plus.sh` (regenerates both from `marginals_<c>.csv` alone),
`tools/4thJ_step6_rakeddonor.py` (+54 lines), `tools/4thJ_step6_rakeddonor_selftest.py` (+61 lines,
34/34 green), `marginals_provenance.md` 663 → 889 lines with **Part III**. 🟢 Also written at the
author's instruction: **`4J_docs_occ/Resources/preprocessing_precedents.md`**, an index of the 2J and
3J preprocessing precedents to consult *before* any future preprocessing decision.

**`prereg.md` NOT touched**, md5 `e4243e07cdd80c9c846b91f40e3e8c45` re-verified against its sidecar.
**No gate was run and no verdict was changed.**

🔴 **STEP 5.1 IS NOW ITALY, PLUS ONE LINE ON THE 15-YEAR-OLDS.**

---

### 2026-08-20 (execution pass) — decision items 3 and 4 applied: `G5.4` narrowed, `D5.1` registered

🟢 **Item 3 (a).** `G5.4` now scores the **five non-`country` prefix fields** —
`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`, `strat_day_type`. **The
threshold did not move**: it is still 100 %, on every one of those five. What moved is the field
set, and the gate's own row now says so, which was `D-S5-1 (a)`'s whole condition.

🔴 **One correction made in execution, not silently.** The rulings document lists the five fields
as ending in `diary_day`. That is wrong twice over: `tools/encoder.py:86` `PREFIX_FIELDS` names
`strat_day_type` as the sixth prefix field, and `diary_day` is not a prefix field at all — it is
the raw column `FINDING 53` showed carries **three different meanings** across the three countries
(`es` 1-7 day of week, `it` 1-3 day *type*, `uk` 1-2 *which of the respondent's two diaries*).
Scoring membership on it would have compared values that are not the same kind of thing across
folds. The gate is scoped to `PREFIX_FIELDS` **minus `country`**, read from the encoder.

🟢 **`G5.11` added, because the narrowing needs a guard.** A field list is only safe while it is
read from the encoder. `G5.11` fails if the `G5.4` checker restates the five names as a literal;
its perturbation is to restate them and then add a seventh prefix field, at which point `G5.4`
keeps passing on a prefix that no longer exists. That is the failure the narrowing could otherwise
create, so it gets its own gate rather than a comment.

🟢 **A perturbation `G5.4` did not have: run the design as specified.** Generating the held-out
fold with its own `country` token must now fell **nothing**. Before this ruling that was the
experiment felling its own gate on all three folds; it is now the check that the ruling was
actually applied.

🟢 **Item 4 (a) — `D5.1`, reported, never a gate.** Entropy at the first body position and the
first-episode `ACT` total-variation distance, held-out token against each seen token, same prefixes.
🔴 **No band is pre-registered for it, on purpose** — no published number says what an
out-of-distribution conditioning token should do, and a band written here would be a threshold
chosen after seeing the design. 🔴 **It cannot be run yet**: it needs a fold checkpoint and a
generation pass, so it is owed at Step 7 and named here so it cannot be forgotten.

⚪ **Nothing executable changed.** No Step 5 gate runner exists yet; when it is written, `G5.4`
takes its field list from `tools/encoder.py`.

---

### 2026-08-21 — 🟢 **ITALY IS BUILT. STEP 5.1 IS 3 OF 3 AND `G6.1` IS COMPUTABLE ON EVERY FOLD.** 🔴 **`FINDING 56`: ISTAT'S OWN VARIABLE LABEL FOR `P139` IS WRONG, AND ONLY ARITHMETIC CATCHES IT. `D-S5-6` AND `D-S5-7` OPEN.**

Full provenance in `outputs_step5/marginals_provenance.md` **Part IV, §16-§22**. Builder:
`tools/4thJ_step5_build_it.py`. Nothing on the cluster; national aggregation of 366,863 census tracts
runs locally in ~40 s and touches no GPU.

#### What was actually retrieved, after the warehouse was retried a fourth time

`esploradati.istat.it` is still dead — `193.204.90.13`, TCP 443 connect timeout, `000` after 15 s;
`dati.istat.it` 302s to `avvisi.istat.it/IdotStat/`; `sdmx.istat.it` and
`dati-censimentopopolazione.istat.it` both 302 into `esploradati`. **Four attempts across three days.
It is treated as dead, not as a wrong URL.**

Two live routes replaced it:

* 🟢 **ISTAT's own STATIC census-tract release**, on `www.istat.it`, which is up:
  `dati-cpa_2011.zip`, 52,442,848 bytes, md5 `bab8d744088761397c09ef8c70ca53d4` — 366,863 tracts x
  140 variables, all 20 regions. **This is the national statistical office, i.e. `D-S5-1`'s route 3**,
  and it is where the private-household base and **all six economic bands** come from.
* 🟢 **Eurostat's 2011 Census Hub** via the dissemination API — single-year age, sex-by-age, the
  collective-quarters profile, and **household type**.

#### 🟢 The two routes were cross-checked before either was used, and fifteen shared quantities are identical **to the person**

Total population, males, females, each of the eight age bands, labour force, employed, unemployed and
inactive: **residual 0 on all fifteen.** The builder raises `BuildError` and writes nothing if any one
of them disagrees, so this is a gate rather than a remark. It is also the evidence that the Eurostat
cube is ISTAT's own transmitted tabulation and not a second-best substitute.

#### 🟢 Italy is the BEST-conditioned fold on two fields, which is itself an asymmetry to declare

* **Six economic bands.** ISTAT publishes `casalinghe` (`P130`), so `it` is fitted on **six** bands
  where `es` has five (`FINDING 51` — the Spanish census has no `homemaker` category at all).
* **Sex is EXACT on the 11+ base**, because `cens_11ag_r3` is sex x single-year. The UK's sex marginal
  is an all-ages `APPROXIMATION` — no UK-wide sex-by-age table exists.
* **`11-14` is EXACT**, from single-year age, with no fifths assumption.

🔴 **Being better-conditioned is not neutral in a LOCO design.** Three folds fitted at three different
resolutions is a third basis asymmetry, alongside `D-S5-1`'s per-fold census-year gap and `FINDING 39`'s
country-dependent MAPE floor. It goes in the same table as those, and it is never averaged away.

#### 🔴 `FINDING 56` — ISTAT's published label for `P139` contradicts the variable's own population

The tracciato reads `P139;Popolazione residente - totale di 15 anni e più percettori di reddito da
lavoro o capitale` — income from **work** or capital. But `P139` lives inside `P128`, the population
**outside the labour force**, which cannot be drawing income from work. The label is self-contradictory
and reading it would have mapped the band wrongly or dropped it.

Arithmetic settles it, exactly:

```
P130 (casalinghe) + P131 (studenti) + P135 (altra condizione) + P139  =  25,122,406
P128 (non appartenente alle forze di lavoro)                          =  25,122,406
                                                             residual =           0
```

`P139` is the fourth non-labour-force band — **pension** or capital income — and the wording is a typo.
It is mapped to `retired` **on the identity, never on the label**.

🔴 **This is `FINDING 47`'s class, one level deeper: there the conflation was ours, here the defective
label is in the national statistical office's own published documentation.** The general rule stands
and now has a second instance: a plausible label is not a verified one, and the check that catches it
is an identity the source asserts about itself.

#### 🟢 `D-S5-5` applied, and Italy's communal population is Spain-like, not UK-like

`PF2 = 59,132,045` persons in famiglie against `P1 = 59,433,744` gives convivenze `301,699`, **0.5076 %
of the population** — Spain is 0.515 %, the UK 1.78 %. **The UK is the outlier and stays the outlier.**
Age and sex are corrected by the Eurostat CLQ profile scaled to ISTAT's convivenze total,
`k = 0.858126` — the same construction the UK used with `DC1104EW` at `k = 1.12096051`. The 11+
private-household base is `53,043,789.10`.

#### 🔴 The build REFUSED itself once, and the refusal was right — a `FINDING 50`-class base mixture

The first run produced an `econ_11plus_it` partition missing its base by **295,531.65 persons**. That
residual is not a rounding: it is **exactly the collective population aged 15+**, because the six
economic bands are `ALL RESIDENTS 15+` while the base is `PRIVATE HOUSEHOLD 11+`. Two universes in one
partition — the same error `FINDING 50` found in the Spanish marginals, caught this time by a check
that was written before the number existed.

It is closed by carrying the composition onto the private-household 15+ total, and two independent
derivations of that total now agree to `-0.0000` persons:

```
base_11plus - band(11-14)       = 53,043,789.10 - 2,231,619.75 = 50,812,169.35
base_15plus - collective_15plus = 51,107,701.00 -   295,531.65 = 50,812,169.35
```

🔴 **The assumption cannot move `G6.1`**: `rake()` consumes SHARES and a proportional rescaling leaves
every share bit-identical. It changes the base only.

#### 🔴 `D-S5-3` mostly does NOT apply to Italy, so `unknown` and `retired` now mean three different things

Italy publishes economic activity for **15+**, not 16-74. So on the `it` fold **age 15 is published**,
**`75+` is published**, and **`unknown` holds the `11-14` band alone**:

| fold | `unknown` | what is in it | `retired` | basis |
|---|---|---|---|---|
| `uk` | 6.88 % | 11-14 + age 15 | 20.33 % | published 16-74 **+ imputed 75+** |
| `es` | 5.26 % | 11-14 + age 15 | 22.56 % | published 16-74 **+ imputed 75+** (only 58.9 % clean) |
| `it` | **4.21 %** | **11-14 only** | **23.76 %** | **published throughout** |

🔴 **This is `FINDING 48`'s species — a category whose content is a country fingerprint — and it now
affects two categories, not one.** Any `it`-fold economic result is read with this table beside it.

#### 🔴 Two decisions this entry opens, both for the author

**`D-S5-6` — is Eurostat admissible for `strat_hh_type`, and for age/sex/CLQ?**
`D-S5-1` ruled route 3, the national offices, and `marginals_provenance.md` §15 records "Eurostat is
not admissible". **The ruling's two stated grounds do not reach these tables**: ground 1 was that
Eurostat merges `homemaker` into `other_inactive` — economic status, which is taken from ISTAT here and
has all six bands; ground 2 was that Eurostat drops the UK from the 2021 round — this is Italy, 2011.
And the fifteen-quantity cross-check is exact. **But the letter of the ruling says national offices,
and this is the author's basis call, not Step 5's.**
🔴 **The cost if the answer is no:** ISTAT's tract file publishes households by SIZE and **never by
TYPE**, so `strat_hh_type` is not derivable from the national office at all. Italy would have **three
of four fields and no household-type marginal**, and `G6.1` would rake `it` on three variables where
`uk` and `es` rake on four. Age and sex would fall back to 5-year bands and an all-ages sex
approximation — recoverable, but a precision loss.
**Recommendation: (a) admit it, narrowly** — for these four tables, on the ground that both stated
objections are inapplicable and the agreement is exact — and record the narrowness so it cannot be
read as reopening Eurostat for economic status or for the UK.

**`D-S5-7` — accept the Italian economic marginal on ALL RESIDENTS 15+?**
No published Italian table crosses residence type with economic status; the UK had `DC1602EW` and there
is no equivalent. **The bound is measured**: if every one of the 295,531.65 collective residents aged
15+ were `retired`, the worst band moves **0.44 pp** (`retired` 24.8051 % → 24.3678 %). For comparison
`D-S5-5` moved the UK's `student` band by 9.56 pp.
**Recommendation: (a) accept and declare**, quoting the 0.44 pp bound wherever the `it` econ marginal
is used.

#### What was NOT done here

* **No IPF, no synthesis, no gate run.** This is item 5.1 only. Step 5.2 is unblocked for all three
  folds and has not been started in this entry.
* **`prereg.md` NOT touched** — md5 `e4243e07cdd80c9c846b91f40e3e8c45` re-verified against its sidecar
  before and after.
* 🔴 **The three folds' `strat_hh_type` marginals are still on a HOUSEHOLD base while donors are
  PERSONS.** That conversion is Step 5.2's first job in every fold, not just Italy's.
* 🔴 **`marginals_<c>.csv` `share` columns are written to 6 dp and `econ_11plus_uk.csv` sums to
  `0.999999`.** `rake()` refuses a target marginal whose shares miss 1.0 by more than `1e-6`, so the
  Step 5.2 driver must build its targets from the `count` column and normalise — never from `share`.
  Found by reading the files back, not by a gate; no gate covers it yet.

---

### 2026-08-21 (afternoon) — 🟢 **`D-S5-6`, `D-S5-7` AND `D-S5-8` ALL CLOSED. `strat_hh_type` IS ON A PERSON BASIS IN ALL THREE FOLDS, AND NO COUNTRY NEEDED A CONVERSION FACTOR.** 🔴 **`FINDING 59` (a fourth published-label defect) AND `FINDING 60` + `D-S5-9` (the three offices use two different household classifications, and the difference is country-correlated).**

Full provenance: `outputs_step5/marginals_provenance.md` **Part V** (§15–§20). Builders:
`tools/4thJ_step5_build_it_microdata.py`, `tools/4thJ_step5_hhtype_person_es_uk.py`. Outputs:
`hhtype_person_{es,uk,it}.csv`, `econ_basis_check_it.csv`. Local, no cluster.

#### What arrived

The author supplied **ISTAT's 2011 census 1 % public-use microdata sample**
(`Datasets/CensPop2011_1%_2011_IT-…`, 594,247 person records, md5
`9f3ae2f2f9022e7e73ccd3107c0aa7a9`). It is a national-office release, so it is inside `D-S5-1` route
3 and Eurostat is not involved in anything derived from it.

Two more sources were pulled in alongside it: the **INE Censo 2011 person microdata** (re-fetched;
the copy left in an earlier session's scratchpad turned out to be a **truncated partial download** —
145,035,264 bytes, not a valid zip — and the real file, md5 `0c8f9b44b70b079b25f2f20fdbd2e83f`,
matches the hash recorded on 2026-08-20 byte for byte), and **ONS `QS112UK`**, which had been sitting
in `raw/` since 2026-08-20 **unused**.

#### 🟢 `D-S5-8` DISSOLVED — the person basis was published or tabulable in every country

The decision asked how to convert a household marginal onto a person basis for Italy and offered a
mean-household-size assumption as the fallback. **No conversion is needed anywhere:** `QS112UK`
counts *people*, `ESTHOG` sits on every Spanish person record, `TIPOLOGIA_FAM` sits on every Italian
person record. Zero conversion factors, zero new assumptions, three folds.

🔴 **What it was worth.** Raking a person file onto a household marginal would have driven
one-person households to **31.0 %** of UK *people*. They are **13.0 %** of people and 31.0 % of
*households* — a factor of **2.4** on the largest single stratum, in the direction that makes the
null model look like a country of people living alone.

#### 🔴 `FINDING 59` — `TIPOLOGIA_FAM`'s classification page is offset from its own codes

The page reads as a hierarchy. The data do not. Cross-tabulated against `NROCOMPO` and against the
presence of a spouse/partner and of children: `tf` **1, 2 and 3** all have **exactly one component**,
no couple, no children, and together they are **76,391 households = exactly the count of
`NROCOMPO == 1`**. `tf` **5** is exactly **2.00** persons per household. **Same class as
`FINDING 47`, `FINDING 56` and TABULA's `F_red_htr` unit** — that is four published-label defects in
three official sources, all caught by reading values instead of labels. The mapping is keyed on
verified code behaviour and the verification re-runs as a refusal on every execution.

Two candidate readings were scored against the Eurostat full count: nucleus code **1.49 %** worst
deviation, composition (`REL_PAR`) **71.90 %**. The nucleus reading is adopted, and its agreement
independently validates the Eurostat household mapping built on 2026-08-21 morning.

#### 🔴 `FINDING 60` — two conventions, and the check that caught it was a RATIO

A household holding a nucleus **plus other resident people** goes to `other_complex` under
**convention A** (ONS, INE) or keeps its nucleus type under **convention B** (Eurostat, hence
`marginals_it.csv`). `es` and `uk` were on A, `it` on B, in shipped files, and nothing had compared
them.

The first version of the Spanish builder deliberately used **B**, to match Italy. The
mean-household-size check then read **`es other_complex` = 1.6495 persons per household** — 🔴
**impossible**, since every household in that class holds at least two people. Neither file is wrong
on its own and neither would fail any check applied to it alone; **only the ratio between the two
bases could show it.** The guard band was 1.5–6.0 and let it through: it is now **1.95**–6.0.

**Convention A is adopted, and it is forced rather than preferred.** `QS112UK` publishes *Other
household types* as one **indivisible** class, so the UK cannot be put on B by any means. The
corroboration, which was not arranged: under A, `couple_no_children` has a mean size of **2.0000** in
Spain, **2.0000** in Italy and **2.0022** in the UK — and the UK's figure is the same **2.00042**
that `D-S5-2` measured for a different reason. Under B, Italy reads 2.0794.

Cost: **7.222 % of Italian persons** and 4.446 % of Italian households move; `other_complex` goes
5.62 % → **12.84 %** of persons. Printed on every run, not buried.

#### 🔴 `D-S5-9` — OPEN, and it is the only new decision

`marginals_it.csv`'s **household**-basis `strat_hh_type` rows are still on convention B and now
contradict Italy's own person file. Only the ISTAT microdata can reconcile them, and that edits a
shipped file.

* **(a) Recommended** — rewrite those five rows from the ISTAT microdata under convention A. Cost:
  they stop being a full count and become a 1 % sample (deviation ≤1.49 %).
* (b) Leave them on B; the published table then contradicts the raked one.

⚪ **This does not block Step 5.2** — the rake consumes the person files, and all three are on A.

#### 🟢 Spain reproduces its own published household table to under one household

`ESTHOG` and `NMIEM` sit on the same record, so summing `weight / NMIEM` reconstructs households.
Against the PC-Axis table already in `marginals_es.csv`: **five categories, five differences of
−0.00.** The two bases are provably the same classification and the PC-Axis table is independently
confirmed.

#### 🟢 `D-S5-7` — the 0.44 pp bound becomes a 0.178 pp MEASUREMENT, and the ruling stands

Both universes tabulated from the same ISTAT records: **max basis effect 0.178 pp**, signed —
employed **+0.178**, retired **−0.177**, other-inactive **−0.127**, the expected direction for a
collective sector that is overwhelmingly care homes.

🔴 **But the same records on the same universe as the published tract table deviate from it by up to
0.207 pp** (1 % sampling error plus ISTAT's disclosure control), which is **larger than the effect it
would correct**. Rewriting `econ_11plus_it.csv` from the sample would trade a known signed 0.178 pp
bias for an unsigned random 0.207 pp error. 🟢 **So it is not rewritten**; `D-S5-7` stands as ruled,
with a measured effect and a direction replacing the bound. Recorded in `econ_basis_check_it.csv`.

#### 🟢 `D-S5-6` — answered, and narrower than expected

Eurostat was admitted narrowly for Italy. In the event the microdata supplies household type
outright, so Eurostat's remaining role in `marginals_it.csv` is single-year age, the sex split and
the collective-quarters profile only.

#### ⚪ The 6-dp rounding trap, closed at the source

At six decimals the five shares sum to **0.999999** and `rake()` refuses a target that misses 1.0 by
1e-6 — the exact hazard flagged on 2026-08-20 for `econ_11plus_uk.csv`. The writers now emit **nine**
decimals and, more to the point, **re-read the file they just wrote** and refuse if the shares *as
written* miss 1.0 by more than 1e-7. Checking the intent would not have caught it. ⚪ The first
tolerance chosen was 1e-9 and it **refused a correct file** on the UK's 0.999999999; the band was
moved to 1e-7, still an order of magnitude inside what `rake()` requires.

#### 🔴 What was NOT done

* **`ETA_CLASSI` bottoms out at "0-14", so the `11-14` band cannot be recovered from the Italian
  microdata at any price.** `marginals_it.csv` keeps its published-table derivation, and the builder
  **refuses to emit an age marginal at all** rather than emit a 15+ one that looks like the whole
  thing.
* **Step 5.2 is still not built.** Its only remaining blocker is that the raking donors are the Step 3
  corpus, which lives on Speed and is not on this machine.
* No Step 5 gate has been run. Items 5.3 and 5.4 untouched.


---

### 2026-08-21 (late afternoon) --- 🟢 **`D-S5-9` APPLIED; ITEMS 5.2 AND 5.3 BUILT FOR ALL THREE FOLDS; 🔴 `FINDING 61` AND `FINDING 62`, THE SECOND OF WHICH STOPS `G6.1` ON THE `uk` FOLD**

Full text and every number: `outputs_step5/marginals_provenance.md` **PART VI**, sections 21-27
(backup `.bak5`). Nothing ran on the cluster. `prereg.md` untouched, md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar at both ends of the session.

#### 🟢 `D-S5-9` ruled (a) and applied

`marginals_it.csv`'s five household-basis `strat_hh_type` rows are rebuilt from the ISTAT 1 %
microdata on **convention A**. `other_complex` moves **+4.502 pp**; the other four move between
-0.041 and -2.014. The rows stop being a full count, and what bounds their accuracy is not a guess:
the same sample on convention B reproduces the Eurostat full count to **1.49 %** worst-category, and
the builder refuses above 3 %.

New: `tools/4thJ_step5_apply_ds59.py`, the only module in Step 5 allowed to mutate a shipped
marginal. It re-reads the file it wrote, diffs it line by line against its own backup, and refuses
unless **exactly six lines changed and every other line is byte-identical**.

⚪ On a household basis `other_complex` now reads es 11.45 / uk 7.69 / it 8.58 %. Italy's old 4.08 %
was an artefact of the classification, not of Italian households.

#### 🟢 Item 5.2 --- three synthetic populations, deterministic end to end

`tools/4thJ_step5_synthesise.py`. IPF onto `age x sex x hh_type x econ`, then largest-remainder
expansion to `N = 100,000`. **No random draw and no seed to record**; every marginal is reproduced to
under **0.014 pp**, a seventh of the 0.1 pp publication grain.

🔴 `strat_hh_type` is taken from `hhtype_person_<c>.csv` and `strat_econ_status` from
`econ_11plus_<c>.csv` --- **not** from `marginals_<c>.csv` in either case. The first is `D-S5-8`; the
second is `D-S5-3`.

Three structural zeros for `G5.2`, none of them a plausibility judgement: two are forced by `D-S5-3`,
and the third is **proved** by the measured mean household sizes of exactly 1.0000 and 2.0000 persons
under convention A.

⚪ `strat_day_type` is exogenous at the calendar week (5/7, 1/7, 1/7), because `FINDING 54` says no
source publishes it. Independence is an assumption and is declared as one.

#### 🟢 Item 5.3 --- prefixes through the shared encoder

`tools/4thJ_step5_prefixes.py` imports `encoder.encode_prefix()` and holds no mapping of its own.
Round trip exact on 300,000 rows; distinct prefixes == distinct strata in all three folds.

🔴 The coverage diagnostic is printed twice on purpose. On the whole prefix string it is
**identically 100 % unseen in every fold** --- the country token is held out, so it cannot be
anything else, and that is the same mechanism that made `G5.4` read 0 %. With the country stripped:
**14.38 % (es) / 17.01 % (uk) / 24.39 % (it)** of synthetic PERSONS sit on a stratum the fold's
training corpus never contained.

#### 🔴 `FINDING 61` --- the population and the corpus disagree about minors

`D-S5-3` says `11-14 -> unknown`. The corpus says `student` in Spain (711 diaries, 99.9 %),
`other_inactive` in the UK (896 of 896) and `unknown` in Italy (1,644 of 1,644). Three countries,
three deterministic and DIFFERENT answers --- `FINDING 48` re-derived from the corpus, with a
consequence `FINDING 48` did not state:

* `es` and `uk` folds: the whole 11-14 band is served by **Italian donors alone**, a country
  fingerprint entering through the back door;
* `it` fold: **no donor supplies it at all**.

Caught by machine, not by inspection: `--seed donor` was added to the synthesiser and **refused on
two of three folds**, quoting the exact deviations.

#### 🔴 `FINDING 62` --- `G6.1` run for the first time, and it is thinner than it looks

Real donors, real published marginals, the real `rake()`.

* First attempt: **all three folds REFUSED.** The UK's 551 `strat_hh_type = unknown` donors
  (`D-S3-14`) have no target category in the `es` and `it` folds --- `FINDING 52`'s orphan guard
  firing correctly. The `uk` fold failed differently, on convergence.
* With `collapse={strat_hh_type: {unknown: other_complex}}`: `es` converges (7 iters, 0.4506 pp),
  `it` converges (3 iters, 0.4121 pp), 🔴 **`uk` CANNOT** --- 1.41515 pp against a 0.5 pp
  tolerance, which is exactly the age-15 `unknown` slice of `FINDING 61`. **This is not a tolerance
  to loosen. It is a missing category.**
* 🔴 And the two that converge are thin. Effective sample size, which no gate looks at:
  `es` 36,977 (68.3 % of pool); **`it` 16,101 (46.0 %)**, where 4.207 % of the country is carried by
  **68 British diaries** at ~62 synthetic persons each, and the largest single donor weight is
  **5.5x** the Spanish fold's.

⚪ Two collapses are now known to be **required** for `G6.1` to run at all and **neither is
pre-registered**. The `unknown -> other_complex` used above was chosen to expose the next failure, not
decided.

#### 🔴 What is now open

* **`D-S5-10`** --- uniform (independence) or donor IPF seed. Recommendation **(a) uniform, declared**,
  because (b) is better but is blocked behind `D-S5-11` and builds for only one fold today.
* **`D-S5-11`** --- what economic band a minor gets in the synthetic population. Recommendation
  **(b) take it from the donor pool per fold**: the only option that makes `G6.1` computable on all
  three folds without touching the frozen corpus, without contradicting `D-S2-17`'s confirmed age
  floor, and without inventing a value. It is a **basis change** and must not be applied without a
  ruling.

#### What did NOT happen

No Step 5 gate was run and none has been seen failing; the numbers above are measurements, not gate
verdicts. Item 5.4 is untouched. `population_<c>.parquet` is written alongside the CSV and verified
on read-back.


---

### 2026-08-21 (evening) --- 🟢 **`D-S5-11` RULED (b) AND `D-S5-10` RULED (a), BOTH APPLIED. `G6.1`'s NULL NOW BUILDS ON ALL THREE FOLDS. THE STEP 5 GATE BATTERY HAS RUN: 25 OF 27 PASS, COVERAGE CLAUSE CLEAN.** 🔴 **`FINDING 63` AND `D-S5-12`.**

Nothing ran on the cluster. `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. No shipped
marginal was modified --- `marginals_{es,uk,it}.csv` keep the md5s they had this morning, and the
battery re-checks the populations' own md5s at both ends of its run.

#### 🟢 `D-S5-11` ruled (b): the minor's economic band comes from the DONOR POOL, per fold

`D-S5-3` had put the whole 11-14 band, plus in `es` and `uk` the age-15 slice, into a single `unknown`
economic band. That band is not a census category; it is a construct, invented because no national
economic-activity table reaches below 16. Under (b) that mass is split back over real bands using the
N-1 pool's own econ mix at the ages the mass comes from.

🔴 **It is not, and cannot be, a rewrite of `econ_11plus_<c>.csv`.** The answer depends on WHICH
TWO COUNTRIES ARE THE DONORS, so `es` under the `es` fold and `es` as a donor elsewhere would need
different files. The rule therefore lives in the synthesiser, at fit time, and what it produced is
written out beside the population as `minor_econ_split_<c>.csv`.

The split is checked against the marginal file's own footer before it is applied: `band_11-14` plus
`age_15_residual` must equal the `unknown` count to within half a person, and it does in all three.

| fold | `unknown` re-labelled | `w11` / `w15` | where it went |
|---|---:|---|---|
| `es` | 2,170,563 (5.2614 %) | 0.804762 / 0.195238 | `unknown` .5216, `other_inactive` .3036, `student` .1000, `employed` .0491, `unemployed` .0256, `retired` .0001 |
| `uk` | 3,712,014 (6.8818 %) | 0.794365 / 0.205635 | `unknown` .5545, `student` .3663, `employed` .0382, `unemployed` .0302, `other_inactive` .0054, `homemaker` .0053 |
| `it` | 2,231,620 (4.2071 %) | 1.000000 / 0.000000 | `other_inactive` .5576, `student` .4418, `employed` .0006 --- **`unknown` is now EMPTY** |

🔴 **What it costs, stated plainly.** `FINDING 61`/`FINDING 48`: each country labels its own
minors differently and deterministically. Under leave-one-country-out we are forbidden the held-out
country's own convention, so a Spanish synthetic 13-year-old is labelled from the British and Italian
habit instead. **The token is wrong for that country in a way no amount of data fixes**, and every run
prints the mix it used. Spain additionally loses 10,753 donor minors' `homemaker` to `other_inactive`,
which is `FINDING 51` reaching into the minor band as well.

#### 🔴 `FINDING 63` --- the re-label fixed the MARGINAL and left the JOINT wrong

Caught by reading the first output, not by a check: the `it` fold's largest unseen strata came back as
`it,11-14,*,couple_with_children,employed`, 1,512 synthetic 13-year-olds in work out of about 4,207 ---
**a third of Italy's minors**, off ONE Spanish donor diary.

The cause is not the rule, it is where the rule was applied. IPF fits marginals; it takes the shape
INSIDE a row from the seed. With a uniform seed the 11-14 row was spread across its admissible bands
in proportion to the whole population's econ marginal, where `employed` is 43 %. The re-label had put
the right TOTAL on each band and said nothing about who held it.

Fixed by seeding the 11-14 row with the donor mix --- which is what (b) ruled, applied where it binds.
`employed` at 11-14 falls to 0.2764 % (`uk`) and 0.4351 % (`it`). IPF still moves the row, because it
must satisfy the marginals, and how far it moves is now printed on every run:

| fold | worst departure of the fitted minor profile from the donor mix |
|---|---:|
| `es` | 11.6949 pp of the minor band |
| `it` | 4.9713 pp |
| `uk` | 0.2339 pp |

⚪ Spain's 11.69 pp is the largest because its minor band is admissible on only TWO econ categories, so
the econ marginal has nowhere else to push. It is a measurement, it is reported, and it is not tuned.

#### 🟢 `D-S5-10` ruled (a): `uniform` is the frozen primary, `donor` is a declared sensitivity

`population_<c>.csv` is the population every downstream step consumes; `population_<c>_donorseed.csv`
is built beside it and never mixed into a headline. The reason is the one already recorded: under the
donor seed the out-of-distribution share falls to zero BY CONSTRUCTION, so it stops being evidence, and
the primary population must be one that can still be surprised.

⚪ Both variants now build on all three folds. Before `D-S5-11`, `--seed donor` REFUSED on two of the
three --- which is how `FINDING 61` was caught in the first place.

Out-of-distribution exposure, country token stripped, on the frozen primary: **`es` 14.339 %,
`uk` 16.277 %, `it` 20.093 %** of synthetic persons sit on a stratum the fold's training corpus never
contained. Strata: `es` 1,116, `uk` 1,306, `it` 1,306.

#### 🟢 `G6.1`'s null now BUILDS ON EVERY FOLD, and `FINDING 62` is retired

`tools/4thJ_step6_g61_rake_folds.py`, new. It rakes the real N-1 diary pool onto the target the model
is actually prompted with --- the fitted population, not the raw marginal file, which is `score_margin`
Guard 1: a null raked onto a different population from the model's is not a null, it is a handicap.

| fold | before (`D-S5-3`) | now | effective sample size | heaviest single diary |
|---|---|---|---:|---:|
| `es` | converged 0.4506 pp | **3 iters, 0.24602 pp** | 26,769 of 54,114 (49.5 %) | 0.0164 % of the target |
| `uk` | 🔴 **COULD NOT CONVERGE**, 1.41515 pp | **5 iters, 0.41662 pp** | 34,107 of 57,400 (59.4 %) | 0.0118 % |
| `it` | converged 0.4121 pp | **4 iters, 0.24487 pp** | 26,881 of 34,994 (**76.8 %**) | 0.0098 % |

🔴 **Italy's null no longer rests on 68 British diaries.** That was `FINDING 62`'s second half:
4.207 % of an entire country was being carried by the 68 `uk` diaries coded `econ = unknown`. With
`unknown` empty in the `it` fold there is nothing for them to carry, and the effective sample size rises
from 46.0 % to 76.8 %.

Two perturbations, both run:

* **drop the collapses** --- `es` and `it` REFUSE on the 551 `strat_hh_type = unknown` donors of
  `D-S3-14` (`FINDING 52`'s orphan guard). `uk` still converges, correctly: those donors are its own
  and are held out.
* **rebuild `uk` under the superseded `D-S5-3` convention** --- refuses at **1.414 pp**, which is the
  1.4151 % age-15 slice to four figures. The failure is reproduced on demand, not remembered.

🔴 ~~**Both collapses are still NOT PRE-REGISTERED** and `prereg.md` is frozen. Declared, owed.~~

🟢 **CLOSED 2026-08-21 (night): registered in `Step6_docs/outputs_step6/prereg_addendum_01.md`**
(md5 `531d064176070e89371e86acbba68dd1`), a dated sidecar addendum --- the author's ruling, and the
route `prereg.md`'s own STATUS section prescribes. `prereg.md` is byte-untouched at
`e4243e07cdd80c9c846b91f40e3e8c45` and `G4.14` is unaffected.

🔴 **AND THERE ARE THREE COLLAPSES, NOT TWO.** This sentence, and every other note in the project,
said "both". The third is `strat_econ_status: unknown -> other_inactive` on fold `it`: `D-S5-11` (b)
emptied Italy's `unknown` economic band entirely, which orphaned the 68 UK donor diaries carrying
`econ = unknown` --- **the same 68 British diaries `FINDING 62` was about**. It is built by a loop in
`tools/4thJ_step6_g61_rake_folds.py` rather than written literally, which is why nobody had counted
it; it was found by reading the script's own `collapses (...)` line, not the note. Counts, costs and
per-fold bindings are in the addendum. The registry is now **enforced**: the rake refuses on any
collapse the addendum does not name, and that refusal is demonstrated by
`tools/4thJ_step6_collapse_registry_selftest.py`.

#### 🟢 The Step 5 gate battery --- `tools/4thJ_gates_step5.py`, run on all three folds

**25 of 27 gate-fold verdicts PASS. Coverage clause CLEAN: no gate passed at baseline without being
made to fall.** Eleven perturbations per fold, each felling exactly the gate the validation doc names.

🔴 **`G5.6` FAILS on `es` (30 of 36 rows) and `it` (12 of 36).** Run as written and left to
fail. See `D-S5-12` below.

🔴 **`G5.8` and `G5.9` are BLOCKED, a third verdict, not PASS.** There is no temperature sweep
and no generation config to read. A gate whose input does not exist has not passed.

⚪ Two things the battery found about itself, both kept as comments in the code because they are facts
about the data:

* Dropping the FIRST 5 % of rows fells `G5.1` as well as `G5.3`, because the population file is ordered
  by stratum and a head slice deletes whole categories. The validation doc asks specifically whether
  the margins survive a PROPORTIONAL loss, so the perturbation drops every 20th row instead --- and
  then `G5.1` survives, as the doc predicted it would.
* **`it` survives "stop IPF after 2 sweeps" and needs one.** Not a weak perturbation: Italy's four
  marginals are close enough to independent that two sweeps already land inside 0.5 pp. Worth knowing
  before anyone reads `G5.1` as evidence that the Italian fit was hard. The escalation is printed.

#### 🔴 `D-S5-12` --- open, and it is a gate-text decision, not a data one

`G5.6` reads "count of marginals with no published source, **or derived from microdata**: 0". Since it
was written, three rulings put census microdata into the marginals on purpose: `D-S5-4` (b) (Spanish
economic bands), `D-S5-5` (private-household frame) and `D-S5-9` (Italian household rows).

The measured split matters: **zero rows in any fold fail for "no published source".** Every failing row
has a URL and a table id; all 42 fail only the microdata clause. And the microdata in question is the
INE Censo 2011 and ISTAT CPA 2011 **public-use census files** --- not the HETUS diaries, which are what
the contamination argument is actually about.

**Recommendation (a): split `G5.6` into two conditions** --- (i) zero marginals derived from the
held-out country's TIME-USE DIARIES, which is the contamination gate and which passes today, and
(ii) zero marginals without a published source with URL and table id, which also passes today. Each
would then have to be seen failing separately.

🟢 **RULED (a) BY THE AUTHOR, 2026-08-21 (night), AND APPLIED.** `G5.6` is now `G5.6i` and
`G5.6ii`; both PASS on all three folds; each was seen falling separately, on every fold; the battery
is 30 of 30 with the coverage clause still clean. 🔴 **The gate as written is NOT deleted** --- it
runs at every baseline as `G5.6-as-written`, INFORMATIONAL and never scored, and still FAILS `es`
30/36 and `it` 12/36. See the 2026-08-21 (night) Progress Log entry.

#### What did NOT happen

Item 5.4 is untouched --- no checkpoint, no generation, so no temperature sweep. `D5.1` likewise. The
Definition of Done is 3 of 5, with item 5 partial. **Step 5 is not closed and is not being written up
as closed.**

---

## 2026-08-21 (night) --- 🟢 `D-S5-12` RULED (a) AND APPLIED, THE COLLAPSES ARE REGISTERED, AND THERE ARE THREE OF THEM

### Say this first

**Two things were owed and both are closed. Neither closed the way the note said it would.**

1. `D-S5-12` ruled **(a)**: `G5.6` is split into `G5.6i` (contamination --- zero marginals from the
   held-out country's TIME-USE DIARIES) and `G5.6ii` (published source --- URL and table id). Both
   PASS on all three folds. Each was **seen failing separately**, on every fold. The battery is now
   **30 gate-fold verdicts, 30 PASS**, coverage clause still CLEAN, `G5.8`/`G5.9` still BLOCKED.
2. The unregistered collapses are registered in a dated sidecar addendum,
   `Step6_docs/outputs_step6/prereg_addendum_01.md` --- and writing it turned up a **third collapse
   nobody had counted**.

### 🔴 The gate as written is still run, and still fails

`G5.6-as-written` executes at every baseline and prints
`[INFORMATIONAL -- superseded by D-S5-12 (a), not counted]`. It still reads **FAIL 30 of 36** on
`es` and **FAIL 12 of 36** on `it`. It is kept deliberately: its failure is the evidence for the
split, and deleting the failing version of a gate one has just relaxed destroys the audit trail that
made the relaxation defensible in the first place.

The perturbation *substitute a held-out marginal computed from CENSUS microdata* is also kept, with
its expectation changed to **fell nothing**. That is the ruling's own test --- `D-S5-4` (b),
`D-S5-5` and `D-S5-9` deliberately admit published-census microdata, so a split that still fells a
scored gate there has not split anything. It does still fell `G5.6-as-written`.

Two new perturbations, both green on all three folds:

* *recount a held-out marginal from the held-out diaries* → fells **`G5.6i`** alone. The injected row
  is published, sourced, and fits the margins; only the contamination condition sees it.
* *add a marginal with no URL and no table id* → fells **`G5.6ii`** alone.

🔴 `G5.6i`'s marker list is deliberately **wide**: `hetus`, `diary`, `diaries`, `time-use`,
`time use`, `time_use`, `tus_`, `step3_corpus`, `harmonised.parquet`. `tus_` matches published
Eurostat *time-use* aggregate tables, which are not diaries. Zero Step 5 marginal rows match any
marker today, so the width costs nothing now and makes the gate fail towards caution later.

### 🔴 FINDING 64 --- there are THREE collapses, not two, and the third moves the 68 diaries of `FINDING 62`

Every note in this project --- this document, `4thJ_06_transfer.md`, `Prompts/RESUME.md` --- says
"both collapses" and names two. It was wrong. Running `tools/4thJ_step6_g61_rake_folds.py` and
reading the `collapses (...)` line it prints for each fold gives:

| fold | collapses actually passed |
|---|---|
| `es` | `strat_hh_type: unknown→other_complex` **+** `strat_econ_status: homemaker→other_inactive` |
| `uk` | `strat_hh_type: unknown→other_complex` (binds on nothing --- the 551 are held out) |
| `it` | `strat_hh_type: unknown→other_complex` **+** 🔴 `strat_econ_status: unknown→other_inactive` |

The third is generated by the "a donor band the target lost entirely must go somewhere" loop, not
written literally, which is why it was never counted. Its cause is `D-S5-11` (b): splitting the
constructed `unknown` band back over real bands **emptied Italy's `unknown` economic band
completely**, so the 68 UK donor diaries carrying `econ = unknown` became orphans on that fold.

🔴 **Those are the same 68 British diaries `FINDING 62` was about.** Italy's null used to rest on
them at ESS 46 %; it now runs at 76.8 %, and this collapse is part of the reason --- they are
weighted as `other_inactive` instead of being orphaned. The cost is stated in the addendum: a UK
respondent whose economic status the UKDA left blank is *asserted* to be economically inactive when
the UK donates into `it`. 68 of 73,254 diaries.

Counts for the other two, measured from the corpus rather than remembered: **A** moves 551 diaries
(all UK, binds on `es` and `it`); **B** moves 5,584 (uk 710 + it 4,874, binds on `es` only).

### The registry is enforced, not asserted

`REGISTERED_COLLAPSES` in `tools/4thJ_step6_g61_rake_folds.py` holds the three triples with the
ruling each follows from. The rake **REFUSES** and names the pair if the dict it built contains
anything else. Demonstrated by `tools/4thJ_step6_collapse_registry_selftest.py`: the three real
per-fold dicts pass; a fourth collapse (`student→employed`) is refused; and a **registered
variable and source with a new target** (`strat_hh_type: unknown→one_person`) is also refused, which
is the case a coarser check would have missed.

🟢 **The guard is additive: the three nulls are byte-for-byte what they were.** `es` 3 iters
0.24602 pp, `uk` 5 iters 0.41662 pp, `it` 4 iters 0.24487 pp.

### Artefacts

| file | md5 |
|---|---|
| `tools/4thJ_gates_step5.py` | `0988f1abfb4b9534798271748d1db5fa` |
| `tools/4thJ_step6_g61_rake_folds.py` | `d692ba56455cd7ab0c4cb69b40fd1d10` |
| `tools/4thJ_step6_collapse_registry_selftest.py` | `8875678c7916d8056ffc9c605ec9181c` |
| `Step6_docs/outputs_step6/prereg_addendum_01.md` | `531d064176070e89371e86acbba68dd1` |
| `Step6_docs/outputs_step6/prereg.md` | `e4243e07cdd80c9c846b91f40e3e8c45` --- 🟢 **UNCHANGED, verified at both ends** |

`.bak_ds512` and `.bak_addendum` copies of both patched tools are on disk. No population, marginal or
prefix file was touched; the battery md5s `population_*.csv` before and after and reports them equal.

### What did NOT happen

**Item 5.4 is still untouched** --- no fold checkpoint, no generation pass, so no temperature sweep
and no generation config. `G5.8`, `G5.9` and `D5.1` remain BLOCKED on it, and nothing here changes
that.

**The Definition of Done is STILL 3 of 5.** Items 1, 2 and 3 are done. Item 4 (temperature
calibrated, both curves reported) is item 5.4 and is untouched. 🔴 **Item 5 --- "all Step 5 gates
PASS and each has been seen failing" --- is CLOSER but NOT MET: the two gates that split both pass
and both were seen failing, but `G5.8` and `G5.9` are BLOCKED, and a gate whose input does not exist
has not passed.** Nine of eleven gates now satisfy item 5 completely. **Step 5 is not closed.**
