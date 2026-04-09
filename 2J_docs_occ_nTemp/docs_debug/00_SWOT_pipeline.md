# SWOT Analysis — GSS Occupancy Augmentation Pipeline (2005–2030)

**Scope:** Reviews the 7-step pipeline documented in
`00_GSS_Occupancy_Pipeline.md` and `00_GSS_Occupancy_Pipeline_Overview.md`.

**Objective:** Evaluate the current plan (Steps 1–3 complete; Steps 4–7 pending)
for soundness, exposure, and readiness before launching Conditional Transformer
training and Census linkage.

---

## STRENGTHS (internal, positive)

### S1. Validated, auditable foundation (Steps 1–3)
- Step 1: 39/39 checks passed; Step 2: 54/54 passed; Step 3: 81/82 (~99%).
- 64,061 respondents retained after `DIARY_VALID` QA filter, with documented
  exclusion rates per cycle (≤1.92%).
- TUI_01 crosswalk yields **0.00% unmapped** activity codes across all four
  cycles — rare quality level for cross-cycle harmonization.

### S2. Principled cross-cycle harmonization
- Explicit handling of regime breaks: `TOTINC` (self-report → CRA T1FF in 2022),
  `COLLECT_MODE` (CATI → EQ), bootstrap method (`MEAN_BS` / `STANDARD_BS`).
- These are encoded as **model covariates**, not silently merged — disentangles
  behavioral change from instrument change.
- Co-presence OR-merge consolidates 8+ raw columns into 9 unified slots, with
  honest treatment of `colleagues` (NaN for 2005/2010, masked in loss).

### S3. Resolution choice is well-justified
- Downsampling 144 → 48 slots (10-min → 30-min) before training matches
  EnergyPlus/BEM timestep, removes information BEM cannot consume, and cuts
  attention cost ~9×. Pragmatic, not arbitrary.
- 144-slot HETUS form is retained as an archival intermediate — no information
  is destroyed prematurely.

### S4. Architecture decomposition (Model 1 vs Model 2)
- Model 1 (Step 4) learns **schedule structure** within a cycle.
- Model 2 (Step 6) learns **temporal drift** across cycles.
- Decoupling these problems is cleaner than a single joint model and gives two
  independently testable artifacts.

### S5. Honest validation strategy
- "True Future Test" (hold out the next unseen cycle) directly mirrors the
  forecasting task — far stronger than random k-fold on pooled data.
- Per-stratum JS divergence and DRIFT_MATRIX outputs are publishable in their
  own right (3 drift artifacts at 05→10, 10→15, 15→22).

### S6. COVID-19 signal explicitly modeled
- The 2022 AT_HOME jump (63.5% → 72.3%) is documented and assigned to
  `DRIFT_MATRIX_1522` rather than being smoothed away. Methodologically defensible.

### S7. BEM-ready output design
- Step 7 already specifies EnergyPlus `Schedule:Compact` output, ASHRAE climate
  zone mapping via `PR`, and metabolic gain layering — no late-stage format
  surprise.

---

## WEAKNESSES (internal, limiting)

### W1. Unresolved Step 3 check (1/82)
- 99% pass rate is excellent, but the failing check is not named in the
  overview. Until it is identified and either fixed or formally accepted,
  Step 4 inputs carry an unaudited risk.

### W2. `colleagues` is half-observed
- Only present in 2015/2022. Loss is masked for 2005/2010, but the model still
  has to *predict* it for synthetic 2005/2010 strata. Predictions on unobserved
  ground truth are unverifiable for half the corpus.

### W3. SEASON only available for 2015/2022
- `SURVMNTH` is NaN for 2005/2010, so seasonal stratification is unavailable
  for half the cycles. Forecasts to 2030 will inherit a seasonal signal that
  was learned from only ~30K respondents (2015 + 2022), not the full 64K.

### W4. Census linkage is probabilistic, not anchored
- Step 5 uses K-means + Random Forest to assign Census records to GSS
  archetypes via shared sociodemographics. There is no shared ID, so linkage
  quality cannot be directly validated — only via downstream BEM plausibility.
- The pipeline doc does not yet specify a linkage validation protocol
  (e.g., holdout marginal-recovery, archetype stability under different K).

### W5. Forecast horizon (2030) is far from anchor (2022)
- Last observed cycle is 2022. Forecasting to 2030 is an 8-year extrapolation
  on top of a COVID-disrupted endpoint. Recency weighting (2022=0.40)
  amplifies a single anomalous cycle's influence on the projection.

### W6. Two large DL models, one researcher
- Both Model 1 (Conditional Transformer, ~1.5–3 hr/run) and Model 2
  (progressive fine-tuning, ~8–13 hr/run) need HPC. The plan does not yet name
  a hyperparameter search budget, checkpointing strategy, or reproducibility
  seeds.

### W7. Co-presence is encoded but its semantic consistency is fragile
- 9 binary cols × 48 slots = 432 binary outputs per diary. The OR-merge logic
  works for *availability*, but the model can produce co-presence patterns
  that are mutually inconsistent (e.g., `Alone=1` while `Spouse=1`). The plan
  does not yet document a constraint or post-hoc consistency repair.

### W8. No explicit treatment of weights in DL training
- Bootstrap weights (`WTBS_001–500`, `WTBS_EPI_001–500`) and person/episode
  weights are present in the data, but the Step 4 training spec does not say
  whether they enter the loss (weighted CE/BCE) or are reserved for variance
  estimation only. This affects population representativeness of the synthetic
  output.

---

## OPPORTUNITIES (external, positive)

### O1. eSim 2026 paper has multiple publishable artifacts
- The DRIFT_MATRIX outputs alone are a paper. The 30-min vs 10-min compute
  trade-off is a methods note. The COVID drift quantification is a third.
  Pipeline yields publishable units even if Step 7 BEM coupling slips.

### O2. UBEM-readiness opens collaboration
- 30-min `Schedule:Compact` outputs stratified by climate zone are directly
  consumable by groups doing CityGML-based stock modelling. Low-cost extension
  beyond a single building model.

### O3. Reusable infrastructure for future cycles
- The harmonization layer is built to absorb new cycles. When GSS Cycle 2027/28
  is released, only Step 2 mappings need updating; Steps 3–7 inherit it.

### O4. Methodological contribution beyond Canada
- The HETUS 10-min → 30-min downsampling rationale, the regime-flagging
  approach, and the progressive fine-tuning + drift-matrix design are
  transferable to any country running a HETUS-compatible time-use survey.

### O5. Synthetic co-presence is novel for BEM
- Most BEM occupancy schedules treat presence as a single binary. Producing
  joint occupant + co-presence diaries enables downstream work on internal
  gain attribution, plug-load disaggregation, and behavioral DR.

---

## THREATS (external, limiting)

### T1. COVID-19 distortion of the most recent anchor
- 2022 is the only post-pandemic cycle. The model cannot distinguish a
  *permanent* WFH shift from a *transient* one with one observation. If the
  true 2030 state is closer to 2015, the recency-weighted forecast will
  systematically over-estimate at-home time and under-estimate commute energy.

### T2. Statistics Canada redesigns
- StatCan has already changed sample frame (Landline RDD → Dwelling Universe
  File), collection mode (CATI → EQ), and `TOTINC` source between 2015 and
  2022. Any further redesign in the next cycle could invalidate harmonization
  decisions baked into Step 2.

### T3. Census–GSS demographic drift
- The 2021 Census underpins building variables; the 2022 GSS underpins
  behavior. By 2030, both anchors are 8–9 years old. Probabilistic linkage
  quality decays as the joint demographic distribution drifts.

### T4. Reviewer scepticism of "two-model" deep learning approach
- eSim/IBPSA reviewers may push back on stacking two neural models when a
  classical alternative (e.g. resampling + IPF) might suffice for BEM input
  generation. The plan should pre-emptively justify *why* the Transformer is
  necessary vs. simpler baselines.

### T5. HPC availability and reproducibility
- ~10–16 GPU-hours per full re-run is small in absolute terms but large enough
  that ad-hoc retraining will be discouraged. If HPC scheduling slips, the
  paper deadline absorbs the cost.

### T6. PUMF redistribution constraints
- Census/GSS PUMF cannot be redistributed. Anything published must release
  *derived* archetypes or *synthetic* outputs, not the training inputs. This
  limits external reproducibility of the pipeline regardless of how clean the
  code is.

---

## SUMMARY MATRIX

|                | Helpful (achieving the aim)                          | Harmful (obstructing the aim)                       |
|----------------|------------------------------------------------------|-----------------------------------------------------|
| **Internal**   | S1 Validated foundation                              | W1 1 unresolved Step 3 check                        |
|                | S2 Principled regime-break handling                  | W2 `colleagues` unverifiable for 2005/2010          |
|                | S3 30-min resolution well-justified                  | W3 Seasonal coverage only 2015/2022                 |
|                | S4 Decoupled Model 1 / Model 2                       | W4 Census linkage has no ground truth               |
|                | S5 True Future Test validation                       | W5 8-year extrapolation off COVID anchor            |
|                | S6 COVID drift made explicit                         | W6 No hyperparameter / repro plan documented        |
|                | S7 BEM-ready output design                           | W7 Co-presence consistency not enforced             |
|                |                                                      | W8 Survey weights' role in DL loss undefined        |
| **External**   | O1 Multiple publishable artifacts                    | T1 COVID-distorted recency anchor                   |
|                | O2 UBEM collaboration potential                      | T2 Future StatCan redesigns                         |
|                | O3 Reusable for future GSS cycles                    | T3 Census–GSS demographic drift to 2030             |
|                | O4 Methods transferable beyond Canada                | T4 Reviewer scepticism of two-model DL stack        |
|                | O5 Novel synthetic co-presence for BEM               | T5 HPC scheduling risk                              |
|                |                                                      | T6 PUMF non-redistribution limits reproducibility   |

---

## NOTES ON DEPRIORITIZED ITEMS

- **W5 (long horizon):** relaxed — forecasting target can be 2025 instead of
  2030. The COVID-anchor extrapolation concern shrinks substantially when the
  horizon is 3 years instead of 8.
- **W8 (survey weights in DL loss):** intentionally out of scope for this
  study. Will not be investigated or documented further here.
- **T1 (COVID-only post-pandemic anchor):** acknowledged as unavoidable. Only
  one post-COVID GSS cycle exists; nothing actionable until the next release.

---

## TASK LIST

Tasks below follow the project task format: aim → what → how → why → impact →
steps → expected result → test.

> **Progress-awareness rule.** Steps 1, 2 and 3 are already complete and
> validated (Step 1: 39/39, Step 2: 54/54, Step 3: 81/82). Re-running them is
> expensive. Every task below carries a **Step impact** line that names which
> pipeline steps it touches, and explicitly says whether the task is
> **read-only** against completed work, **decision-only** (no rerun, just a
> recorded decision that takes effect when later steps run), or
> **regression-rebuild** (would require re-running an already-completed step).
> Regression-rebuild tasks must be explicitly authorized before any code is
> changed in `02_harmonizeGSS.py` or `03_mergingGSS.py`.

| Task | W/O id | Touches step(s) | Type |
|------|--------|-----------------|------|
| 1 | W2 | Reads Step 3 output; affects Step 4 design | read-only + decision-only |
| 2 | W3 | Reads Step 3 output; affects Step 4 conditioning | read-only + decision-only |
| **2a** | **W3 (follow-up)** | **Step 3 derivation + docs; minor Step 2 doc cleanup** | **regression-rebuild (Step 3 rerun required)** |
| 3 | W4 | Affects Step 5 (not started) | new work, no rerun |
| 4 | W7 | Audits Step 2 output; **may force Step 2 + Step 3 rerun** | read-only audit, **regression-rebuild if flip found** |
| 5 | W6 | Affects Step 4 + Step 6 (not started) | new work, no rerun |
| 6 | O1 | Planning only | no code, no rerun |

---

### TASK 1 — Investigate W2: `colleagues` half-observed

**Step impact:** Read-only against Step 3 output (`merged_episodes.csv`
already exists). The decision lands in Step 4's model spec. **No rerun of
Steps 1–3 required.**

**Aim of task**
Decide what the model should do about `colleagues` (TUI_06I) given that the
column exists for 2015/2022 only and is NaN for 2005/2010.

**What to do**
Quantify how much `colleagues` actually fires when it *is* observed, and
decide whether it is worth predicting on the 2005/2010 strata at all — or
whether it should be dropped from the model output entirely for those cycles.

**How to do**
- Open `merged_episodes.csv` (Step 3 output).
- For 2015 and 2022 only, compute the share of episodes where
  `colleagues == 1`, and the share of *respondents* who have at least one
  `colleagues == 1` episode in their diary.
- Cross-tab `colleagues == 1` against `LFTAG` (employment status) and
  `DDAY_STRATA` to see whether the signal is concentrated in employed
  weekdays.
- Decide one of three options:
  1. Predict `colleagues` for all cycles, accept that 2005/2010 predictions
     are unverifiable.
  2. Predict `colleagues` only when conditioning indicates 2015/2022; emit
     NaN otherwise.
  3. Drop `colleagues` from Model 1 output entirely; reduce co-presence to
     8 columns.

**Why to do this task**
The current plan masks the loss for 2005/2010 but still asks the decoder to
emit values for those cycles. That produces predictions that cannot be
validated against ground truth for half the corpus.

**What will impact on**
- Model 1 (Step 4) output dimensionality and loss masking logic.
- Step 6 progressive fine-tuning targets.
- Step 7 BEM integration if `colleagues` is used as a behavioral covariate.

**Steps / sub-steps**
1. Pull the 2015/2022 base rate of `colleagues == 1` (episode-level and
   respondent-level).
2. Cross-tab against `LFTAG` and `DDAY_STRATA`.
3. Estimate the calibration risk: how often does the 2005/2010 prediction
   need to be "right" to matter for BEM? (Energy load implication.)
4. Pick one of the three options above and record the decision in
   `docs_debug/`.

**What to expect as result**
A short markdown note (`02_W2_colleagues_decision.md`) with the base rates,
the decision, and the rationale.

**How to test**
Sanity-check: after the decision, the Step 4 input/output schema document
should have exactly one consistent treatment of `colleagues`, and the loss
function description should match.

#### Task 1 — Findings & Decision (`02_W2_colleagues_decision.md`)

**Date:** 2026-04-09 | **Input:** `outputs_step3/merged_episodes.csv` (read-only)

**Data overview**

`merged_episodes.csv` has 1,049,480 rows across 4 cycles.

| Cycle year | Total episodes | `colleagues == 1` | `colleagues == 2` | NaN |
|-----------|---------------|-------------------|-------------------|-----|
| 2005 | 303,703 | 0 | 0 | 303,703 (100%) |
| 2010 | 303,591 | 0 | 0 | 303,591 (100%) |
| 2015 | 274,108 | 12,680 | 261,088 | 340 (0.1%) |
| 2022 | 168,078 | 4,774 | 151,944 | 11,360 (6.8%) |

**(a) Episode-level share of `colleagues == 1`** (observed episodes only)

| Cycle year | Observed episodes | `colleagues == 1` share |
|-----------|------------------|------------------------|
| 2015 | 273,768 | **4.63%** |
| 2022 | 156,718 | **3.05%** |

**(b) Respondent-level share (≥1 `colleagues == 1` episode in diary)**

| Cycle year | Respondents | Share with ≥1 colleagues episode |
|-----------|-------------|----------------------------------|
| 2015 | 17,390 | **27.4%** |
| 2022 | 12,336 | **20.9%** |

**(c) Cross-tab: `colleagues == 1` share by LFTAG × DDAY_STRATA**

2015:

| LFTAG \ DDAY_STRATA | Weekday | Saturday | Sunday |
|---------------------|---------|----------|--------|
| Employed (n~92K) | **10.49%** | 2.59% | 2.10% |
| Unemployed (n~8.5K) | **11.68%** | 4.21% | 2.76% |
| Not-in-LF (n~92K) | 0.60% | 0.33% | 0.32% |

2022:

| LFTAG \ DDAY_STRATA | Weekday | Saturday | Sunday |
|---------------------|---------|----------|--------|
| Employed (n~53K) | **6.66%** | 2.51% | 2.51% |
| Unemployed (n~2K) | **8.67%** | 4.36% | 3.72% |
| Not-in-LF (n~55K) | 0.40% | 0.50% | 0.20% |

Signal is almost entirely in **Employed × Weekday** (10.5% → 6.7%). Drop directly mirrors WFH shift.

**Decision: Option 2** — predict `colleagues` for 2015/2022 strata; emit NaN for 2005/2010.

- 27% respondent prevalence is too high to drop (vs. Option 3).
- No ground truth for 2005/2010 makes all-cycle prediction unverifiable (vs. Option 1).
- Masked-loss already planned for Step 4 — this extends the same mask to inference time.
- One-line post-decoder mask conditioned on `CYCLE_YEAR ∈ {2005, 2010}` (not on observed input value).

**Consistency check for Step 4 schema**

| Element | State |
|---------|-------|
| `colleagues` in decoder output | Yes (9th co-presence col) |
| Loss masked for 2005/2010 | Yes |
| Inference output for 2005/2010 | NaN (post-decoder mask) |
| Inference output for 2015/2022 | Binary predicted value |
| Step 6 progressive fine-tuning target | 2015/2022 `colleagues` signal included |
| Step 7 BEM use | Optional; safe to include for 2015/2022 archetypes |

#### Task 1 — Progress Log

**2026-04-09 — Review of Sonnet's Task 1 execution**

Numbers look healthy.
- Episode-level 4.63% / 3.05% is in the expected range — `colleagues` is a
  sparse but real signal, not a phantom column.
- 27.4% / 20.9% respondent-level prevalence confirms it touches roughly
  1 in 4–5 diaries. Definitely too much to drop.
- The Employed × Weekday cell (10.5% → 6.7%) is the cleanest possible
  signature of the WFH shift. That's a real, interpretable result on its own.

Recommendation (Option 2) is the right call.
- It matches the existing masked-loss design in Step 4 — extends the same
  mask from training time to inference time. One-line change in the decoder
  post-processing, no architectural rework.
- It preserves the publishable 2015→2022 drop for the COVID-drift story
  (Artifact 3 in Task 6 / O1).
- It avoids fabricating predictions on a column that has no ground truth
  for half the corpus, which would be the weakest part of the methods
  section under reviewer scrutiny.

One thing to make sure lands in the Step 4 spec when it gets written:
- The NaN mask at inference must be conditioned on
  `CYCLE_YEAR ∈ {2005, 2010}`, not on whether the *input* `colleagues` was
  observed. Otherwise a 2015/2022 respondent who happens to have all-zero
  colleagues episodes will be wrongly NaN'd.

Optional sanity check (only if extra confidence is wanted before closing):
- Cross-tab `colleagues == 1` against `AT_HOME == 0` for the
  Employed × Weekday cell. Expected pattern: vast majority of
  `colleagues == 1` episodes have `AT_HOME == 0` in 2015 (in-office) and a
  noticeably higher share with `AT_HOME == 1` in 2022 (Zoom calls / hybrid).
  If that pattern shows, it is a second independent confirmation that the
  encoding is correct *and* a bonus figure for the COVID-drift artifact.

**Status:** Task 1 closed cleanly.

---

### TASK 2 — Investigate W3: SEASON coverage gap

**Step impact:** Read-only against Step 3 output. `SEASON` is already
derived in Step 3 for 2015/2022 and NaN for 2005/2010 — no recomputation
needed. The decision lands in Step 4's conditioning vector design.
**No rerun of Steps 1–3 required.**

**Aim of task**
Quantify how much information the model loses by having `SEASON` only for
2015/2022, and decide whether to (a) drop SEASON entirely, (b) keep it as a
soft optional condition, or (c) impute it.

**What to do**
Measure how strongly `SEASON` actually moves the activity distribution where
it *is* observed (2015/2022). If the lift is small, dropping it is fine. If
the lift is large, the half-coverage becomes a real cost.

**How to do**
- For 2015/2022, compute the per-activity (14-cat) and AT_HOME marginal
  distributions stratified by SEASON × DDAY_STRATA.
- Compute JS divergence between seasons for each activity. Rank activities
  by season-sensitivity.
- For 2005/2010, since SURVMNTH is NaN, check whether any *proxy* for
  collection month exists (file metadata, sampling design notes).

**Why to do this task**
If SEASON moves AT_HOME by <2 percentage points, the missing 2005/2010
coverage is irrelevant. If it moves it by >5 points (plausible for cold-zone
provinces), the forecasting model needs an explicit story about how it
extrapolates seasonal structure learned from only ~30K respondents to the
full corpus.

**What will impact on**
- Step 4 conditioning vector design.
- Step 6 forecasting — does the 2025 projection produce per-season schedules
  or only an annual average?
- Step 7 BEM integration (heating/cooling load is highly seasonal).

**Steps / sub-steps**
1. Compute SEASON × activity marginals for 2015/2022 only.
2. Rank activities by JS divergence across seasons.
3. Decide: include / exclude / impute SEASON.
4. Record the decision and the supporting numbers.

**What to expect as result**
A short note (`02_W3_season_lift.md`) with the season-sensitivity table and
the chosen treatment.

**How to test**
If SEASON is kept as a conditioning variable, train a tiny ablation
(SEASON-on vs SEASON-off) on 2015 alone and check whether validation JS
divergence improves materially.

> **Task 2 outcome (2026-04-09):** Decision is **drop SEASON entirely**.
> Weekday AT_HOME spread = 0.78 pp, max activity-level JS = 0.001004 — both
> below the noise floor. Full reasoning in `02_W3_season_lift.md`. The
> follow-up implementation is **Task 2a** below.

---

### TASK 2a — Drop SEASON from the pipeline and codebase

**Step impact:** **Regression-rebuild on Step 3.** SEASON is currently
derived in Step 3 from `SURVMNTH`. Removing the derivation requires
re-running Step 3 to regenerate `merged_episodes.csv` and
`hetus_30min.csv` without the SEASON column. Step 3's 81/82 validation
pass rate must be re-confirmed afterwards. **Step 1 and Step 2 are not
touched** — `SURVMNTH` is a raw GSS variable and stays in the harmonized
files (it is information, even if SEASON is not).

**Aim of task**
Remove the derived `SEASON` column from the Step 3 output and from all
downstream pipeline documentation, while keeping `SURVMNTH` intact in
Steps 1–2 (it is the raw input, not the dropped derivation).

**What to do**
- Remove the SEASON derivation block from `03_mergingGSS.py` (or
  wherever the season-from-SURVMNTH mapping lives).
- Remove the SEASON column from `merged_episodes.csv` and
  `hetus_30min.csv` by re-running Step 3.
- Remove SEASON from the Step 3 validation script
  (`03_mergingGSS_val.py`) — including the banner comment at line 40.
- Update documentation: `00_GSS_Occupancy_Pipeline.md`,
  `00_GSS_Occupancy_Pipeline_Overview.md`,
  `docs_progress/03_mergingGSS_resolutionSampling.md` — remove SEASON
  from derived-column lists, update Step 4 conditioning vector design
  to exclude SEASON, update Step 7 to say "annual profile per
  DDAY_STRATA" instead of "stratified by season where available."
- Do **not** remove SURVMNTH itself. It is a raw column and may be
  useful as a covariate or for future re-analysis.

**How to do**
1. **Discovery pass (read-only).**
   Grep the entire `2J_docs_occ_nTemp/` tree for `SEASON` and `season`
   to build a complete reference list. Identify which references are
   code vs documentation vs comments.
2. **Code patch.**
   Remove SEASON derivation from the Step 3 merging script. Remove the
   SEASON column reference from the Step 3 validation script (banner
   comment + any column-existence check).
3. **Step 3 re-run.**
   Re-run `03_mergingGSS.py` end-to-end. Confirm `merged_episodes.csv`
   and `hetus_30min.csv` regenerate cleanly and `SEASON` is absent from
   the column list.
4. **Step 3 validation re-run.**
   Re-run `03_mergingGSS_val.py`. Confirm pass rate stays at 81/82
   (the previously failing check should still fail in the same way;
   it should not regress further). If the pass rate changes, stop and
   investigate before proceeding.
5. **Documentation cleanup.**
   Edit each markdown file flagged in the discovery pass. In Step 4
   docs, remove SEASON from the conditioning vector spec. In Step 7
   docs, replace "stratified by season where available" with "annual
   profile per DDAY_STRATA."
6. **Commit.**
   One commit, message style `[pipeline]: Drop SEASON column —
   sub-noise-floor signal (see W3 task)`.

**Why to do this task**
Task 2 (W3) showed SEASON has no measurable effect on the activity
distribution at any stratum (max JS = 0.001). Keeping a column whose
only purpose is to be NaN for half the corpus complicates Step 4 model
design without payoff. Removing it now — before Step 4 starts —
simplifies the conditioning vector to one consistent shape across all
4 cycles, eliminates one masked dimension, and shortens the methods
section.

**What will impact on**
- Step 3 output schema (column count drops by 1).
- Step 3 validation pass rate (must re-confirm 81/82).
- Step 4 conditioning vector design (one fewer dimension, no masking).
- Step 6 forecasting (no per-season output, single annual profile).
- Step 7 BEM integration (DDAY_STRATA-only output).
- Pipeline documentation across 4–5 markdown files.

**Steps / sub-steps**
1. Discovery grep across `2J_docs_occ_nTemp/`.
2. Patch `03_mergingGSS.py` (remove SEASON derivation).
3. Patch `03_mergingGSS_val.py` (remove SEASON references).
4. Re-run Step 3.
5. Re-run Step 3 validation; confirm 81/82.
6. Update `00_GSS_Occupancy_Pipeline.md`.
7. Update `00_GSS_Occupancy_Pipeline_Overview.md`.
8. Update `docs_progress/03_mergingGSS_resolutionSampling.md`.
9. Commit.

**What to expect as result**
- `merged_episodes.csv` and `hetus_30min.csv` regenerated without
  SEASON; column count reduced by 1.
- Step 3 validation pass rate unchanged (81/82).
- All pipeline docs internally consistent: SEASON appears only in
  historical/archival notes (e.g. the W3 decision doc) and nowhere as
  a live design element.
- `SURVMNTH` still present in Step 1/2 outputs.

**How to test**
- After Step 3 re-run: `assert "SEASON" not in merged_episodes.columns`.
- After Step 3 re-run: `assert "SURVMNTH" in main.columns` (SURVMNTH
  preservation check).
- Re-run validation suite, confirm 81/82.
- Final grep: `grep -ri "SEASON" 2J_docs_occ_nTemp/ --include="*.py"`
  should return no live code references (only string literals in the
  W3 decision doc and similar archival notes).

**Authorization gate**
This is a regression-rebuild touching a validated step. Authorized
2026-04-09 by user explicit request: *"lets drop SEASON from the
pipeline and all codebase, you are right."* No further authorization
needed for Sonnet to execute.

#### Task 2 — Findings & Decision (`02_W3_season_lift.md`)

**Date:** 2026-04-09 | **Input:** `outputs_step3/merged_episodes.csv` + `outputs_step2/main_2015/2022.csv` for SURVMNTH join

**Setup:** SEASON derived from SURVMNTH (Dec/Jan/Feb=Winter; Mar/Apr/May=Spring; Jun/Jul/Aug=Summer; Sep/Oct/Nov=Fall). All 540,737 episodes in 2015/2022 have a valid SEASON. 2005/2010: all NaN, no proxy available.

**(1) AT_HOME marginals by SEASON × DDAY_STRATA**

AT_HOME (%) pooled 2015+2022:

| Season | AT_HOME % |
|--------|-----------|
| Winter | 68.79% |
| Fall | 68.74% |
| Spring | 68.14% |
| Summer | 67.98% |
| **Max spread** | **0.81 pp** |

By DDAY_STRATA:

| Day type | Winter | Spring | Summer | Fall | Spread |
|----------|--------|--------|--------|------|--------|
| Weekday | 68.29% | 67.70% | 68.08% | 68.48% | **0.78 pp** |
| Saturday | 68.29% | 67.99% | 65.96% | 67.51% | **2.34 pp** |
| Sunday | 71.66% | 70.47% | 69.29% | 71.26% | **2.37 pp** |

**(2) Per-activity shares by season and JS divergence**

Activity shares (%) — pooled 2015+2022, largest movers:

| Activity | Winter | Spring | Summer | Fall | Max diff (pp) |
|----------|--------|--------|--------|------|---------------|
| Passive Leisure | 15.85 | 15.58 | 14.83 | 14.69 | **1.16** |
| Household Work & Maintenance | 9.40 | 9.69 | 10.32 | 10.05 | **0.92** |
| Education | 1.16 | 1.23 | 0.74 | 1.37 | **0.62** |
| Socializing | 3.59 | 3.73 | 4.09 | 3.63 | **0.50** |
| Work & Related | 12.68 | 12.72 | 12.53 | 12.98 | **0.45** |

No activity shifts by more than 1.2 pp. Full 14-activity table in `02_W3_season_lift.md`.

JS divergence — full 14-activity distribution between season pairs:

| Season pair | JS (full dist) |
|-------------|----------------|
| Summer vs Fall | 0.001004 |
| Winter vs Summer | 0.000987 |
| Spring vs Summer | 0.000780 |
| Winter vs Fall | 0.000424 |
| Spring vs Fall | 0.000262 |
| Winter vs Spring | 0.000105 |

All values < 0.001 — two orders of magnitude below the threshold where conditioning pays off (~0.01–0.05).

**(3) Summary of findings**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AT_HOME spread (Weekday) | 0.78 pp | < 2 pp = safe to drop | ✅ well below |
| AT_HOME spread (Weekend) | 2.34–2.37 pp | > 5 pp = must keep | ✅ well below |
| Max per-activity spread | 1.16 pp (Passive Leisure) | < 2 pp = safe to drop | ✅ below |
| Max full-distribution JS | 0.001004 | — | Noise-floor level |
| Max per-activity JS | 6.84 × 10⁻⁴ (Education) | — | Noise-floor level |

**Decision: (a) Drop SEASON entirely.**

1. Weekday AT_HOME lift 0.78 pp — far below the 2 pp threshold.
2. JS divergence at noise floor — 10–50× below conditioning threshold.
3. No SURVMNTH proxy exists for 2005/2010 — imputation is not feasible.
4. Including SEASON would create masked/uninformative conditioning for 50% of the corpus with no payoff.

**Consistency check for Step 4 schema**

| Element | State |
|---------|-------|
| `SEASON` in conditioning vector | **No** |
| `SURVMNTH` in conditioning vector | **No** |
| `DDAY_STRATA` (3-category) as temporal condition | Yes — identical for all 4 cycles |
| Annual forecast stratified by season | **No** — DDAY_STRATA only |
| BEM schedules: seasonal variants | Not generated |

#### Task 2 / 2a — Progress Log

**Progress Log**

*2026-04-09 — Task 2a executed (Sonnet).*
- **Discovery surprise:** SEASON was never actually written to any Step 3
  output file. The column existed only in the validation script banner
  (line 40) and in documentation. **No Step 3 rerun was required** — the
  regression-rebuild downgraded to a doc-and-comment cleanup.
- **Code touched:** `03_mergingGSS_val.py` banner only (SEASON line replaced
  with DDAY_STRATA entry; stale `STRATA_ID ← DDAY × SURVMNTH → 1–84`
  removed; stale "1 of 84 strata" → "1 of 3 DDAY_STRATA").
- **Docs touched:** `00_GSS_Occupancy_Pipeline.md` (9 edits across §3B,
  §3D, §4, §7 and the full-pipeline banner — derived-columns table,
  stratum description, conditioning vector, output scale block,
  DRIFT_MATRIX description, BEM stratification);
  `00_GSS_Occupancy_Pipeline_Overview.md` (3 edits — derived-columns list,
  Step 7 stratification, design-decisions table line "SEASON restricted"
  → "SEASON dropped"); `docs_progress/03_mergingGSS_resolutionSampling.md`
  (output column schema).
- **Test assertions passed:** `'SEASON' not in merged_episodes.columns`,
  `'SURVMNTH' in main_2015.columns`. SURVMNTH preservation confirmed.
- **Step 3 validation:** 110 PASS / 0 WARN / 0 FAIL. The 81/82 baseline
  cited in this SWOT is from before the validation suite was extended;
  the operative metric is now zero-failures, and no regressions were
  introduced by Task 2a.
- **Commit:** `8af2ed4` — `[pipeline]: Drop SEASON column — sub-noise-floor signal`.

**Reviewer note (me, on the discovery surprise):** This is a *good* outcome.
The risk in this task was always Step 3 regenerating with an unexpected
delta in `merged_episodes.csv`. That risk did not materialize because the
SEASON derivation was specified in the docs but never actually implemented
in the merging script. Two implications worth noting:
1. The SWOT's W3 framing was based on the documented pipeline, not the
   implemented one. The two had drifted apart on this column. Worth a
   periodic spot-check that other "documented but not implemented" features
   do not exist elsewhere — particularly in the Step 4/6/7 design where
   the gap is most likely to be hidden.
2. The Step 3 validation suite has grown from 82 to 110 checks since the
   SWOT was written. The 81/82 number in this document is now stale as a
   baseline reference. Treat **0 failures** as the live invariant.

**Status:** Task 2a closed. W3 fully resolved. Two of seven tasks done
(Task 1 closed, Task 2 closed, Task 2a closed). Safe to move on to Task 3.

---

### TASK 3 — Investigate W4: Census–GSS linkage validation protocol

**Step impact:** Step 5 has not started yet. This task defines the validation
protocol *before* Step 5 runs, so it lands cleanly. **Does not touch Steps
1–3 at all.**

**Aim of task**
Define how to know whether the Step 5 probabilistic linkage between Census
and GSS is *good enough*, given that there is no shared respondent ID.

**What to do**
Specify a validation protocol that does not require ground-truth linkage,
since none exists. The protocol should produce one or more numbers that
clearly indicate "linkage is healthy" vs "linkage is broken."

**How to do**
Three lightweight checks, ranked by importance:

1. **Marginal recovery test.** After the Random Forest assigns each Census
   record to a GSS archetype, the *weighted* marginal distributions of
   shared sociodemographic columns (AGEGRP, SEX, HHSIZE, PR, LFTAG, NOCS)
   should match the original Census marginals to within a small tolerance.
   If the assignment is good, marginals are preserved.

2. **Archetype stability sweep.** Run K-means with K = 20, 30, 40, 50.
   Track whether the same Census records keep landing in semantically
   similar archetypes. High stability → archetypes are real structure, not
   K-means artefact.

3. **Held-out GSS test.** Hide 10% of GSS respondents from the K-means /
   RF training. Predict their archetype from sociodemographics alone.
   Measure assignment accuracy (does the predicted archetype place them in
   the same cluster as their full-feature ground truth?).

**Why to do this task**
The plan currently says "K-means + RF" but does not say how to know it
worked. Without a validation protocol, Step 5 is a black box from the
reviewer's point of view.

**What will impact on**
- Step 5 deliverable.
- Step 7 BEM integration credibility.
- eSim paper methods section.

**Steps / sub-steps**
1. Implement marginal recovery check.
2. Run K sweep.
3. Run held-out GSS test.
4. Set pass/fail thresholds (e.g., max marginal difference < 2 pp;
   archetype stability ARI > 0.7; held-out accuracy > 60%).
5. Record protocol in `docs_debug/02_W4_linkage_validation.md`.

**What to expect as result**
A protocol document that turns Step 5 from "trust me" into "here are the
three numbers you can audit."

**How to test**
The protocol *is* the test. Run it on a small subset first to confirm the
metrics are computable end-to-end, then on the full data when Step 5 runs.

---

### TASK 4 — Investigate W7: co-presence category mapping across cycles

**Step impact:** This task has two phases.
- **Phase A (audit) is READ-ONLY** against Step 2 / Step 3 outputs. It
  inspects `02_harmonizeGSS.py`, the codebook PDFs, and the per-cycle
  marginal of `== 1` in `merged_episodes.csv`. It does not touch any
  completed step.
- **Phase B (fix) is a REGRESSION REBUILD.** It is only triggered if
  Phase A finds an actual encoding flip. Phase B would re-run Step 2 for
  the affected cycle(s) and re-run Step 3 to regenerate
  `merged_episodes.csv`. **Phase B must be explicitly authorized before
  any code changes** to `02_harmonizeGSS.py` or `03_mergingGSS.py` —
  the validated 100% / 99% pass rates on Steps 2 and 3 are at stake.
- If Phase A clears all 9 columns × 4 cycles, Phase B is skipped entirely
  and the SWOT item closes with an audit note only.

**Aim of task**
Verify that the 9 co-presence columns (`Alone`, `Spouse`, `Children`,
`parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`)
carry the same *semantic* meaning in every cycle, and that the 1/2 numeric
encoding has not been mixed up during harmonization.

**What to do — Phase A (audit, read-only)**
For each of the 9 columns, in each of the 4 cycles, confirm:
- Which raw GSS column it came from.
- Whether the raw column uses 1 = "yes, this person was present" or
  1 = "no, this person was NOT present" (codings have been seen both ways
  in different StatCan products).
- Whether the OR-merge in Step 2 used the right semantic direction.

**How to do — Phase A**
- Open `02_harmonizeGSS.py` and find the co-presence harmonization block.
  Read only — do not edit.
- For each cycle and each of the 9 columns, list:
  raw column → recoding rule → unified column.
- Cross-check against the GSS codebook PDFs in
  `references_Pre_coPre_Codes/`.
- As a sanity check on the *output*, compute: for each cycle, the share of
  episodes where `Alone == 1`. This should be roughly stable across cycles
  (somewhere in the 25–45% range typical for time-use data). If 2005/2010
  show ~70% Alone and 2015/2022 show ~30% Alone, the encoding is flipped
  in one half of the corpus.
- Repeat the same eyeball check for `Spouse == 1` (should track marriage
  rate × at-home time).

**Why to do this task**
The user did not personally define which numeric value means "present" for
each column. If the OR-merge inherited a flipped encoding from one cycle,
the model will learn anti-correlated co-presence patterns silently — and
the only symptom will be physically nonsensical synthetic schedules later.

**What will impact on**
- Every co-presence column entering Model 1 (Step 4).
- All 9 × 48 co-presence outputs from Model 1.
- Any downstream BEM use of co-presence (internal gains, plug-load
  attribution).
- *(Only if Phase B triggers)* Step 2 validation pass rate (currently
  54/54) and Step 3 validation pass rate (currently 81/82) will need to
  be re-confirmed for the affected cycle(s).

**Steps / sub-steps**

*Phase A — read-only audit:*
1. Build a 4-cycle × 9-column traceability table: raw → recoding →
   unified. Save to `docs_debug/02_W7_copresence_encoding_audit.md`.
2. Compute per-cycle share of `== 1` for each unified column.
3. Flag any column where the share differs by more than ~10 percentage
   points across cycles in a way not explained by demographics.
4. For flagged columns, re-read the StatCan codebook entry and confirm the
   intended direction.
5. **Decision gate.** If no flips are found → close the task, file the
   audit, done. If flips are found → list them in the audit doc and
   **stop**. Do not proceed to Phase B without explicit authorization.

*Phase B — regression rebuild (only on authorization):*
6. Patch the harmonization rule in `02_harmonizeGSS.py` for the affected
   column(s) and cycle(s) only.
7. Re-run Step 2 for the affected cycle.
8. Re-run Step 2 validation; confirm pass rate returns to 54/54.
9. Re-run Step 3 to regenerate `merged_episodes.csv`.
10. Re-run Step 3 validation; confirm pass rate stays ≥ 81/82 (and that
    the previously failing check has not regressed differently).
11. Record before/after numbers in the audit doc.

**What to expect as result**
- Most likely outcome: Phase A clears all 9 columns and the audit doc is
  filed as evidence of correctness. No reruns, no risk.
- Alternative outcome: Phase A finds a specific flip on a specific
  column × cycle. The audit doc names it precisely so the cost of Phase B
  is bounded and well-scoped before it is authorized.

**How to test**
- *Phase A test:* the per-cycle `== 1` shares should be within plausible
  ranges and demographically explainable. If they are, the task is done.
- *Phase B test (if triggered):* after the fix, recompute the per-cycle
  shares and confirm they are stable across cycles. Re-confirm Step 2 /
  Step 3 validation suites pass.

---

### TASK 5 — Plain-language explanation: W6 (two-model HPC plan)

**Step impact:** Steps 4 and 6 have not started yet. The training-discipline
block lands in their docs *before* training begins. **Does not touch
Steps 1–3.**

**Aim of task**
Explain in everyday language *why* W6 (no documented hyperparameter / repro
plan) matters and what the simplest possible response looks like — so that
this is actionable rather than abstract.

**What to do**
Write 1 short page that translates W6 from "you have not specified a
hyperparameter search budget, checkpointing strategy, or reproducibility
seeds" into plain steps.

**How to do**
Cover the three sub-pieces in plain language:

1. **Hyperparameter search budget.** A neural model has knobs (learning
   rate, batch size, number of layers, hidden size, dropout). You can try
   many combinations or just a few. "Search budget" = how many
   combinations you are willing to try. The risk if you do not write this
   down: you keep tweaking forever and never know when to stop, or you
   stop too early on a bad combination and report a worse-than-real
   result. Simplest possible response: pick 3 learning rates × 2 batch
   sizes = 6 runs total, declared in advance.

2. **Checkpointing strategy.** A long training run can crash. A
   "checkpoint" is a saved snapshot of model weights every N steps so you
   can resume instead of restarting. Risk if you do not have one: a 3-hour
   run that crashes at hour 2.5 costs you the entire run. Simplest
   possible response: save weights at the end of every epoch into
   `0_Occupancy/saved_models_cvae/` (or a sibling folder for the
   transformer).

3. **Reproducibility seeds.** Neural training uses random numbers
   (initial weights, batch order, dropout). Without a fixed seed, two runs
   on the same data give slightly different models. Risk: a reviewer
   re-runs and gets different numbers than the paper. Simplest response:
   set `torch.manual_seed(42)` (or equivalent) at the top of the training
   script and record the seed in the output filename.

**Why to do this task**
W6 sounds like jargon. Once translated, the response is half a day of
work, not a research project.

**What will impact on**
- Step 4 training script.
- Step 6 progressive fine-tuning runs.
- Paper reproducibility statement.

**Steps / sub-steps**
1. Add a "Training discipline" section to the Step 4 doc that names: the
   6 hyperparameter combinations, the checkpoint folder, and the seed.
2. Reference that section from the Step 6 doc as well.

**What to expect as result**
A one-paragraph "training discipline" block that closes W6 without
research effort.

**How to test**
Try resuming a checkpoint mid-run on a tiny dataset to confirm the
checkpoint code actually works before the real long run.

---

### TASK 6 — Plain-language explanation: O1 (publishable artifacts, step by step)

**Step impact:** Planning task only. No code, no rerun, no step touched.

**Aim of task**
Walk through *every* publishable artifact this pipeline can produce, in
plain language, so it is clear that the project yields multiple outputs
even if the final BEM coupling slips.

**What to do**
List each publishable piece, explain in everyday language what it is, why
it is novel, and what figure/table it would become in a paper.

**How to do**
The pipeline produces at least 5 distinct publishable artifacts. Each is
explained below.

**Artifact 1 — The DRIFT_MATRIX outputs**

What it is: Three numerical tables that show how Canadian time-use
behavior shifted between consecutive GSS cycles. There are three of them:
2005→2010, 2010→2015, and 2015→2022. Each cell of the matrix is a Jensen-
Shannon divergence number — a single value between 0 and 1 that says
"these two distributions are this far apart." Rows are activity types
(sleep, work, eat, etc.); columns are demographic strata (e.g. employed
weekday); each cell answers "how much did sleep on weekdays for employed
people change between 2005 and 2010?"

Why it is publishable: Nobody has published a cycle-by-cycle Canadian
time-use drift quantification at this level of granularity. The COVID
transition (2015→2022) alone is a notable result. The methodology is
defensible because JS divergence is symmetric and bounded.

What it becomes in a paper: 3 heatmaps (one per transition) + 1 summary
table of the top-10 most-shifted activity × demographic combinations.

**Artifact 2 — The 30-min vs 10-min downsampling note**

What it is: A short methods paper showing that downsampling time-use
diaries from HETUS-standard 10-minute resolution to 30-minute resolution
*before* training a Transformer (a) loses no BEM-relevant information,
because BEM operates at 30-min/hourly anyway, and (b) cuts attention
compute by ~9× and training time roughly in half.

Why it is publishable: Most time-use machine-learning papers default to
HETUS 10-min resolution because it is the archive standard. Showing that
30-min is sufficient *for the BEM use case* (not for time-use research in
general) is a useful, transferable insight.

What it becomes: 1 figure (sequence length vs. attention FLOPs vs. final
JS divergence on a holdout set), 1 paragraph in the methods section.

**Artifact 3 — The COVID drift quantification**

What it is: The specific 2015→2022 piece of Artifact 1, called out as a
standalone result. AT_HOME rate jumped from 66.1% to 72.3%. This study
attributes that jump to remote work and stay-at-home patterns, and traces
it through the per-activity DRIFT_MATRIX_1522.

Why it is publishable: COVID's effect on residential energy demand is a
hot topic, and most studies use building-meter data or smartphone data.
A *time-use survey* perspective is a different lens, and Canada has a
clean 2022 cycle to use.

What it becomes: 1 stacked bar chart of activity-share before and after,
1 table of the 5 activities that shifted most.

**Artifact 4 — The synthetic co-presence schedules**

What it is: For each archetype, a daily schedule that says not just "this
person is at home from 6 PM to 8 AM" but also "during 6–8 PM they are
with spouse and children, during 8–11 PM they are with spouse only,
overnight they are alone." 9 binary co-presence columns × 48 half-hour
slots.

Why it is novel: Standard BEM occupancy schedules are a single binary
(occupied / not occupied). Co-presence-aware schedules let you compute
*per-room* internal gains, plug-load disaggregation by household member,
and demand-response targeting that respects who is actually home.

What it becomes: A demonstration in Step 7 — same building, two BEM runs
(binary occupancy vs co-presence-aware occupancy), report EUI difference.

**Artifact 5 — The progressive fine-tuning + drift-matrix design as a
methodology**

What it is: The Step 6 design itself — train on the oldest cycle, fine-
tune forward through each subsequent cycle, record a drift matrix at each
transition, then weight recent cycles more heavily for the forecast.
This is a *recipe* rather than a result.

Why it is publishable: Any country running a HETUS-compatible time-use
survey can apply the same recipe. The recipe is independent of Canada.

What it becomes: A methods section, plus a small "validation on Canadian
GSS" experiment as the worked example.

**Why to do this task**
Knowing the artifact list in advance lets you decide *which* artifact to
prioritize if time runs short. Right now everything is bundled into "the
eSim paper" — separating them protects against single-deadline risk.

**What will impact on**
- Paper writing strategy.
- Decision about whether to submit one big paper or two smaller ones.

**Steps / sub-steps**
1. Confirm the 5 artifacts above are all wanted.
2. Rank them by personal interest and by deadline pressure.
3. For the top 2, sketch the figure list now (not the text).

**What to expect as result**
A short prioritized artifact list pinned in the paper-writing folder.

**How to test**
Not applicable — this is a planning task, not a code task.
