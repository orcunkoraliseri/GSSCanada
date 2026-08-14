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
contains the design strata — country, age, sex, household type, economic status, day type, season —
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
* `../Step3_docs/outputs_step3/corpus.jsonl` — for the stratum definitions the prefix uses.

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
exactly the nine prefix fields Step 3 defined.

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

**What this step blocks:** Step 7 has nobody to generate for without it.

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
