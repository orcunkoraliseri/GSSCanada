# 4J — Master Decisions & Rulings Log (All 13 Items Ruled)

**Status:** 🟢 **ALL 13 OPEN DECISIONS RULED (ALL RULED AS OPTION `(a)`)**  
**Date:** 2026-08-20 (night) — Completed and finalized for full downstream pipeline execution.  
**Audience:** For pipeline engineers, autonomous agents, and downstream LLMs executing Steps 1 to 9 of the 4J HETUS LOCO pipeline.

---

## Executive Summary for Downstream LLMs & Agents

> [!IMPORTANT]
> **Directive for any LLM reading this document:**
> Every single open question (Items 1 through 13) has been reviewed, evaluated against the methodological precedents (`Resources/preprocessing_precedents.md`), and **formally ruled as Option (a)**. 
> 
> Downstream execution must follow these principles:
> 1. **Strict Additive Modularity:** Do NOT modify existing raw column values or destroy existing schemas. Add new harmonized/post-stratified columns (e.g., `weight_dia_cal` in Step 2) so all previously validated Step 1/Step 2 gates remain untouched and bit-identical.
> 2. **LOCO Cross-Validation Soundness:** Do not penalize zero-shot transfer for unseen tokens (Item 3, Item 4).
> 3. **Honest Gate Reporting:** If an external standard or benchmark cannot be met by the literature, allow gates to fail transparently and record corpus fidelity rationales rather than relaxing thresholds post-hoc (Item 11).
> 4. **Numeric & Type Integrity:** Use float percentages (`PTP_RT`) instead of parsing `h:mm` duration strings (Item 6), and use string matching for serialized categorical tokens (Item 9).

---

## Master Ruling Summary Table

| # | Item | Step | Ruling | Blocking? | Key Action & Impact |
|---|---|---|---|---|---|
| 1 | Day basis of diary weights (`FINDING 53`) | 2 | **(a)** ✅ | 🔴 Was blocking cross-country numbers | Post-stratify `es` and `it` to calendar week as NEW column `weight_dia_cal`. Leaves `weight_dia` untouched. |
| 2 | Age-15 economic status | 5 | **(a)** ✅ | No | Assign `unknown` to age 15 in `econ_11plus_<c>.csv`. Matches census silence & `D-S5-3`. |
| 3 | `G5.4` field scope (`FINDING 40`) | 5 | **(a)** ✅ | 🔴 Was blocking Step 5 gate | Scope `G5.4` to the 5 non-`country` prefix fields. LOCO unseen `country` token is not a gate defect. |
| 4 | Measure unseen-`country`-token effect | 5 | **(a)** ✅ | No | Add as reported diagnostic metric (not a pass/fail gate) to monitor zero-shot token response. |
| 5 | `G6.7` encoder control-token hook (`FINDING 41`) | 6 | **(a)** ✅ | 🔴 Was blocking `G6.7` | Add test-only hook in `tools/encoder.py` for synthetic country vectors, keeping production whitelist closed. |
| 6 | `MAPE` unit (`D-S6-3` item 2) | 6 | **(a)** ✅ | 🔴 Was blocking Step 6 scoring | Score MAPE exclusively on `PTP_RT` (numeric participation rate). Avoids `h:mm` string truncation & zero-cell noise. |
| 7 | `TOTAL` rows excluded (`D-S6-3` item 3) | 6 | **(a)** ✅ | 🔴 Was blocking Step 6 scoring | Exclude constant 100% `TOTAL` rows from MAPE calculation; declare exclusion in paper. |
| 8 | Per-fold rounding floors reported (`D-S6-3` item 4) | 6 | **(a)** ✅ | No | Print publication rounding floor (UK 1.87%, IT 3.42%) beside each fold's MAPE to avoid biased comparison. |
| 9 | `G7.13` indoor rule (`FINDING 42`) | 7 | **(a)** ✅ | 🔴 Was blocking `G7.13` | Re-point rule to `LOC == "at_home"` (string comparison), fixing the string vs integer `LOC == 11` bug. |
| 10 | `ACT` alphabet = 159 (`FINDING 43`) | 7 | **(a)** ✅ | 🔴 Was blocking `G7.2` / `G7.10` | Declare alphabet as 158 target codes ∪ `{000}` = 159 codes; update `G7.2` validation accordingly. |
| 11 | `G9.11` allowed to fail | 9 | **(a)** ✅ | No | Let `G9.11` FAIL honestly; re-justify 3-digit resolution on corpus fidelity (literature benchmarks lack 3 digits). |
| 12 | `G9.4` citation match rule (`FINDING 47`) | 9 | **(a)** ✅ | No | Require volume, issue, pages, AND first author for citation verification (prevent wrong title-only DOI match). |
| 13 | Trainer edit before next fold (`D-S4-7`) | 4 | **(a)** ✅ | 🔴 Required before re-running fold | Apply `D-S4-7` to `tools/4thJ_step4_train.py`: `G4.7` evaluates generated output, shard check becomes `G4.15`. |

---

## Detailed Rulings & Technical Execution Directives

---

### 1. 🔴 `FINDING 53` — Diary Weight Day Basis Post-Stratification

#### Context & Problem
Step 1 chose the UK's `dia_wt_a` over `dia_wt_b` with an explicit justification: *"Day of week is load-bearing for this paper… a weight with no day-of-week adjustment would carry whatever day-type imbalance the fieldwork left, straight into the thing we are modelling."*  
However, when measured on `harmonised.parquet`, the weighted day distributions across countries are:
* **Calendar week**: 71.43 % weekday, 14.29 % Saturday, 14.29 % Sunday
* **`uk`**: **71.45 % / 14.32 % / 14.24 %** (matches calendar week)
* **`es`**: **50.02 % / 25.00 % / 24.98 %** (50/25/25 exact)
* **`it`**: **33.33 % / 33.33 % / 33.33 %** (one third each exact)

Because Spain and Italy deliberately target non-calendar sampling frames without publishing a calendar weight, raw diary weights distort cross-country occupancy comparisons (+0.95 pp at-home in ES, +1.30 pp in IT, −0.003 pp in UK). In Leave-One-Country-Out (LOCO) evaluation, this moves fold error scores for survey-design reasons unrelated to model performance.

#### Options
* **(a) Post-stratify `es` and `it` to the calendar week, as a NEW column `weight_dia_cal`.**
* (b) Leave the published weights as delivered and declare the asymmetry.
* (c) Put all three on Italy's one-third basis.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Applies the UK calendar-representative standard consistently across all three countries using exact algebraic factors:
  * `es`: Weekday $\times 1.4281$, Saturday $\times 0.5714$, Sunday $\times 0.5718$
  * `it`: Weekday $\times 2.1429$, Saturday $\times 0.4286$, Sunday $\times 0.4286$
  * `uk`: Weekday $\times 0.9998$, Saturday $\times 0.9979$, Sunday $\times 1.0034$ ($\approx 1.000$)
* **Implementation Directive:** Add the post-stratified weight as a new column `weight_dia_cal` in `outputs_step2/harmonised.parquet`. Keep `weight_dia` intact. No past Step 1 or Step 2 gates are broken or invalidated.
* **Note for Step 6:** This resolves the prerequisite for Eurostat table comparisons in Step 6 (Item 6).

---

### 2. Age-15 Economic Status

#### Context & Problem
Decision `D-S5-3` established that `11-14` $\rightarrow$ `unknown` and `75+` $\rightarrow$ `retired`. However, the `15-24` demographic band straddles the standard census economic activity base (ages 16–74). 15-year-olds represent 1.415% of the UK 11+ base and 1.027% of Spain's 11+ base.

#### Options
* **(a) `unknown`, as applied.**
* (b) `student`.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Census tables (e.g., `KS601UK` / INE census microdata) are strictly silent on economic activity for individuals under 16. Mapping age 15 to `unknown` follows the exact logic of `D-S5-3`, avoiding the injection of unmeasured assumptions.
* **Implementation Directive:** Maintain the mapping of age 15 to `unknown` in `outputs_step5/econ_11plus_uk.csv` and `outputs_step5/econ_11plus_es.csv`. Confirmed with partition residual `0.00`.

---

### 3. 🔴 `G5.4` Field Scope (`FINDING 40`)

#### Context & Problem
`G5.4` requires 100% of synthetic person prefixes to match prefix values present in the training set. In LOCO evaluation, the held-out country's `country` token never appears in the training data. Consequently, `G5.4` reads 0% on every fold by construction, penalizing the cross-validation mechanism as if it were a defect.

#### Options
* **(a) Scope `G5.4` to the five non-`country` prefix fields, and say so in the gate text.**
* (b) Leave it and let it fail on every fold.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** `G5.4` is intended to verify that demographic stratum combinations (`strat_age_band`, `strat_sex`, `strat_econ_status`, `strat_hh_type`, `diary_day`) fall within valid training support. Scoping `G5.4` to the 5 demographic fields restores its true validation purpose.
* **Implementation Directive:** Update `4thJ_05_populationLinkage.md` and validator scripts to evaluate `G5.4` over the 5 non-country prefix fields. The zero-shot response to the unseen country token is measured separately under Item 4.

---

### 4. Unseen `country` Token Diagnostic (`FINDING 40`)

#### Context & Problem
The LOCO transfer claim relies on the generative model receiving a prompt with a `country` token not seen during fine-tuning. The behavioral effect of this unseen token on embedding space and output entropy should be measured.

#### Options
* **(a) Add it as a reported diagnostic, not a gate.**
* (b) Do not measure it.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Quantifying model steering under out-of-distribution conditioning is critical for scientific transparency, but it should be reported as a diagnostic characterization rather than a binary pass/fail gate.
* **Implementation Directive:** Implement a lightweight diagnostic generation pass over existing checkpoints logging token prediction entropy and output divergence when conditioned on the held-out country token.

---

### 5. 🔴 `G6.7` Encoder Control-Token Hook (`FINDING 41`)

#### Context & Problem
`G6.7` tests whether the model's output follows conditioning vectors by steering generation with an invented fictional country token. However, `enc_country()` in `tools/encoder.py` employs a strict whitelist (`{"es", "uk", "it"}`), which causes the encoder to reject fictional tokens and blocks `G6.7`.

#### Options
* **(a) Add an explicit test-only control-token hook to the encoder, used by `G6.7` alone.**
* (b) Drop `G6.7`.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Preserves strict input sanitization in production pipelines while enabling synthetic verification tests to execute cleanly.
* **Implementation Directive:** Add an optional parameter `allow_synthetic_controls=False` to `enc_country()` in `tools/encoder.py`. When enabled solely during `G6.7` testing, synthetic control tokens can be encoded without loosening standard validation.

---

### 6. 🔴 `MAPE` Unit Selection (`D-S6-3` Item 2)

#### Context & Problem
Eurostat publishes time-use summary tables in multiple units:
* `PTP_RT` (participation rate, numeric percentage, available across all 5 tables, 1.06% zero floor).
* `TIME_SP` / `PTP_TIME` (time spent, formatted as `h:mm` strings; float casting silently truncates minutes to whole hours, and 10.6% of cells are zero).

#### Options
* **(a) `PTP_RT` only.**
* (b) All units.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** `PTP_RT` provides a uniform, natively numeric percentage representation across all five Eurostat validation tables (`tus_00age`, etc.), eliminating string parsing bugs and minimizing zero-cell singularities.
* **Implementation Directive:** Standardize Step 6 MAPE evaluation to compute exclusively on `PTP_RT`. Note: Apply Item 1 (`weight_dia_cal`) prior to running Step 6 scoring.

---

### 7. 🔴 Exclusion of `TOTAL` Rows in `MAPE` (`D-S6-3` Item 3)

#### Context & Problem
`TOTAL` rows in Eurostat tables represent constant 100.0% values (comprising 11.1% of cells). Including these constant marginals artificially introduces guaranteed zero-error comparisons, artificially deflating overall MAPE.

#### Options
* **(a) Exclude, and state the exclusion in the paper.**
* (b) Include.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Removing trivial 100% constant totals ensures the error metric measures actual predictive accuracy across substantive activity categories rather than being masked by fixed sums.
* **Implementation Directive:** Filter out `TOTAL` rows in Step 6 scoring routines and explicitly document this filtering in the manuscript methodology section.

---

### 8. Reporting Per-Fold Publication Rounding Floors (`D-S6-3` Item 4)

#### Context & Problem
Eurostat publication rounding limits vary by country: the theoretical minimum rounding floor on `PTP_RT` is **1.87% for the UK** versus **3.42% for Italy**. Without disclosing these baselines, cross-fold performance differences could be misattributed to model error rather than data source granularity.

#### Options
* **(a) Print the floor next to each fold's `MAPE`.**
* (b) Do not.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Scientific rigor requires contextualizing empirical errors against the intrinsic precision limit of the ground-truth data.
* **Implementation Directive:** Display the national rounding floor alongside each fold's MAPE in all Step 6 result tables and figures.

---

### 9. 🔴 `G7.13` Indoor Rule Definition (`FINDING 42`)

#### Context & Problem
`G7.13` was written as `LOC == 11`. However, the serialized location token in the corpus is a string (`"at_home"`). Evaluating `"at_home" == 11` returns `False` across all records, incorrectly reporting 0% indoor presence for every simulated occupant.

#### Options
* **(a) Re-point it to `LOC == "at_home"`.**
* (b) Leave it.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Resolves a type mismatch between integer code legacy definitions and string-serialized pipeline tokens.
* **Implementation Directive:** Update `G7.13` in `4thJ_07_constrainedGeneration.md` and associated validator scripts to test for `LOC == "at_home"`.

---

### 10. 🔴 `ACT` Alphabet Declaration = 159 (`FINDING 43`)

#### Context & Problem
`G7.2` requires 100% of activity codes to match `activity_target_list.csv` (which lists 158 codes). However, the corpus includes code `000` (the pre-registered null activity code ruled under `D-S3-4`). Without including `000`, `G7.2` fails on valid corpus files.

#### Options
* **(a) Declare the alphabet as the 158 target codes ∪ `{000}` = 159, and amend `G7.2` to say so.**
* (b) Leave it.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Formally recognizes the valid 158 substantive HETUS activities plus the explicit null activity state `{000}`.
* **Implementation Directive:** Update the official vocabulary size to 159 in `4thJ_07_constrainedGeneration.md`, `G7.2`, `G7.10`, and the grammar construction scripts.

---

### 11. Handling of `G9.11` Benchmark Comparison

#### Context & Problem
Literature survey `RL25` established that 0 of 4 benchmark end-use models (CREST, Widén, LPG, RAMP) resolve activity profiles at 3 digits.

#### Options
* **(a) Let `G9.11` FAIL, and re-justify the 3-digit decision on corpus fidelity instead.**
* (b) Relax the band.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Modifying gate criteria post-hoc when a benchmark fails violates pre-registration protocols. Allowing `G9.11` to record an honest fail while justifying 3-digit resolution based on raw HETUS microdata granularity maintains methodological integrity.
* **Implementation Directive:** Record `G9.11` as FAIL in Step 9 logs and document the justification based on primary microdata fidelity.

---

### 12. `G9.4` Citation Compound Verification Rule (`FINDING 47`)

#### Context & Problem
`G9.4` previously used title-only CrossRef matching, which allowed a citation to match an incorrect paper (passive cooling in Brazil) that shared ambiguous title keywords.

#### Options
* **(a) Amend `G9.4` to match volume, issue, pages AND first author — not the title alone.**
* (b) Leave it.

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Prevents false-positive bibliography resolution through multi-field validation.
* **Implementation Directive:** Update `G9.4` validation logic in Step 9 tools to enforce matching across volume, issue, page range, and first author surname.

---

### 13. 🔴 Trainer Updates: `G4.7` on Generated Output, Shard Check $\rightarrow$ `G4.15` (`D-S4-7`)

#### Context & Problem
Decision `D-S4-7` was previously ruled (a) to ensure `G4.7` checks generated diary termination (which identified the IT epoch 1 defect of `599/600` completed diaries), while moving the training shard verification to new gate `G4.15`. This update needs to be applied to `tools/4thJ_step4_train.py` and Step 4 documentation before re-running folds.

#### Options
* **(a) Apply it now, before any fold re-runs.**

#### 🟢 RULING: (a) APPROVED
* **Methodological Rationale:** Ensures training monitoring accurately reports generation termination integrity (`G4.7`) and training data integrity (`G4.15`).
* **Implementation Directive:** Update `tools/4thJ_step4_train.py` and `4thJ_04_train.md` to reflect `G4.7` (generated sample termination) and `G4.15` (shard check) prior to launching any subsequent LOCO training jobs.

---

## Operational Roadmap & Outstanding Work Items

The following items are active operational tasks to be carried out:

1. **Step 5.1 (Italy Marginal Acquisition):**
   * `esploradati.istat.it` (193.204.90.13) connection timeouts must be monitored. If ISTAT SDMX endpoints remain unreachable due to external network blocks, check local cache or alternative direct national census dumps. Eurostat remains non-admissible under `D-S5-1`.
2. **Step 5.2 (Iterative Proportional Fitting & Raking):**
   * Execute household-to-person conversion.
   * Rake `es` using `collapse={"strat_econ_status": {"homemaker": "other_inactive"}}` on `outputs_step5/econ_11plus_es.csv` (five-band collapsed vector) as required by `FINDING 51` and `FINDING 52`.
   * Rake `uk` on `outputs_step5/econ_11plus_uk.csv` (six-band vector).
3. **Step 8.1 (TABULA Building Energy Archetypes):**
   * TABULA `tabula-values.xlsx` (65 sheets, 22 construction bands) is verified.
   * Note geographic scope: TABULA `GB` represents Great Britain (England, Wales, Scotland; excluding Northern Ireland).
4. **Step 7 (`G7.4` Grammar Engine):**
   * Complete co-presence grammar variant implementation supporting the 159-code vocabulary.
5. **Execution of Standalone Scripts:**
   * Run `4thJ_step4_g41_seedfloor.sh` and `4thJ_step4_g47_coverage.sh`.
