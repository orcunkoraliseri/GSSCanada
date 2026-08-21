# Step 5 — Conditioning and population linkage

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 5. Validation: `4thJ_05_populationLinkage_val.md`

---

## STATUS

**✅ DECIDED by `RL09`. Implementation OPEN, nothing built.**

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
| No aggressive top-p / top-k at generation | `RL09`; p ≤ 0.98 if used at all |
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
aggressive truncation. If top-p is used at all, **p ≤ 0.98**.

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
| **(a)** | `G5.4` scope | 🔴 **Exclude `country` from `G5.4`'s membership test and say why in the gate's own text**, keeping the other five fields at 100 %. An unseen `country` is the design; an unseen `strat_hh_type` is a bug, and today one gate cannot tell them apart. **Do not weaken the threshold** — narrow the field set, and name the narrowing. |
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
| **`D-S5-3`** | `strat_econ_status` for `11-14` and `75+`, which no census publishes at either end. Assign one convention to all folds, or assign each fold its own observed convention? | 🔴 **Neither as stated, and `FINDING 48` is why.** One convention imports Spain's coding into the UK and Italy; per-fold conventions require reading the held-out country's microdata, which is contamination. **Recommend a THIRD option: assign `unknown` to `11-14` in all three folds**, since `unknown` is a declared value of the field in the crosswalk for all three countries, it is the value Italy actually uses, and it is the only choice that asserts nothing the source does not say. `75+` is a separate and easier case, but state its weak fold: `retired` is the corpus modal value in all three, at `uk` 1,232 of 1,292 (95.4 %), `it` 3,420 of 4,753 (71.9 %) and `es` 1,138 of 1,933 — **only 58.9 %, because Spain also records 251 `homemaker` and 539 `other_inactive` at 75+**. So `retired` is defensible as a single convention and is NOT clean in Spain, and the Spanish figure must be quoted alongside it. |

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
