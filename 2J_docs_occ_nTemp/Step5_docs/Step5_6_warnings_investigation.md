# Step 5 & 6 — Non-PASS Gate Investigation (post-calibration, journal-prep)

*Generated: 2026-06-01. Scope: every non-PASS line (FAIL + WARN) in the **calibrated-J3** Step-5 and Step-6 validators, for the journal submission. Each item is traced to root cause with fresh quantitative evidence, classified, and given a paper recommendation + Step-7 blocker verdict.*

> **Relationship to `outputs_step5/step5_fails.md`:** that report (2026-05-12) analysed the **pre-calibration** J3 linkage (AT_HOME deficit up to **6.73 pp**, 1,248-HH floor breach). Phase-8B raking (8B-5b) has since been applied, which **changes the diagnosis** of two items: the AT_HOME gate (2.2/6.1) is no longer a model deficit but a day-type **composition artefact** (proven below), and the floor exclusion dropped 1,248 → **1,118**. This document is the authoritative post-calibration view; where it conflicts with `step5_fails.md`, this one governs. Items 6.2 (Work) and 3.3 (night-sleep) are unchanged because `act30` is deliberately not raked.

Verification script: `Step5_docs/_verify_warnings.py` (deterministic, reads the live `_excl` canonical). Numbers below are from its 2026-06-01 run.

---

## 1. Inventory — every non-PASS line

**Step 5 validator (`05_censusLinkageGSS_val.py`):** normal **29 PASS / 0 WARN / 5 FAIL**; `--excl` **25 PASS / 0 WARN / 9 FAIL**.
**Step 6 validator (`06_longitudinalForecastingGSS_val.py`):** all hard gates **PASS**, **3 WARN**.

| # | Step | Check | Value | Gate | Class | Step-7 blocker? |
|---|---|---|---|---|---|:--:|
| 1 | 5 | 2.2 / 6.1 AT_HOME per-slot max diff | 4.48 pp (norm) / 4.37 pp (excl) | ≤3 pp | **A — composition artefact** | No |
| 2 | 5 | 6.2 Top-5 activity (Work) | 3.27 / 3.29 pp | ≤2 pp | **B — un-raked act30 (by design)** | No |
| 3 | 5 | 3.3 night-slot sleep dominance | 67.46 / 67.49 % | ≥70 % | **B — un-raked act30 (by design)** | No |
| 4 | 5 | 1.1 / 4.5 / 5.6 row count (`--excl` only) | 285,419 | =286,537 | **C — validator baseline bug** | No |
| 5 | 5 | 5.4 / 6.4 DTYPE vs Census (`--excl` only) | 0.1063 % | exact | **C — exclusion perturbation** | No |
| 6 | 6 | 3.2 / 3.4 / 3.6 DRIFT WD activities >0.001 | 1 / 2 / 1 | ≥3 | **D — superseded metric** | No |

**None of the six blocks Step 7.** Groups A/D are not defects (artefact / wrong metric); group B is the documented un-raked-`act30` limitation; group C is two fixable validator issues. Detail + evidence below.

---

## 2. Group A — AT_HOME per-slot diff (2.2 / 6.1): a composition artefact, not a model error

### What the gate computes
`05_censusLinkageGSS_val.py` compares **all matched rows** vs the **IS_SYNTHETIC=0 (observed)** subset, per 30-min slot: `max_s |mean_all[s] − mean_obs[s]|`. Result **4.37 pp** (`--excl`, 9 slots > ±3 pp) / 4.48 pp (normal, 11 slots).

### Root cause — the two pools have different day-type mixes
The observed subset is overwhelmingly weekday; the full population is the 3-strata expansion:

| DDAY_STRATA | IS_SYNTHETIC=0 (baseline) | full population (all) | IS_SYNTHETIC=1 |
|---|--:|--:|--:|
| 1 Weekday | **92.61 %** | 71.34 % | 45.30 % |
| 2 Saturday | 3.61 % | 14.33 % | 27.44 % |
| 3 Sunday | 3.77 % | 14.33 % | 27.26 % |

Weekday AT_HOME differs from weekend AT_HOME, so an aggregate that averages a 92.6 %-WD pool against a 71.3 %-WD pool differs **even if every within-stratum marginal is identical**. That mix gap — not any model deficit — drives the 4.37 pp.

### Proof (verification run, `_verify_warnings.py`)
- **Within-stratum** synthetic-vs-observed per-slot AT_HOME max |diff|: **WD 0.50 pp · Sat 0.89 pp · Sun 1.09 pp.** The raking made the marginal the downstream actually scores essentially exact; the <1.1 pp residual is post-exclusion drift (1,118 synthetic single-person HHs removed after the rake).
- **Composition-held** (re-weight the full population to the observed 92.6 %-WD mix): per-slot max diff collapses **4.37 pp → 0.19 pp**. (Daily-mean composition-held residual ≈ 0.004 pp per the OP1 record.)

So **~96 % of the 4.37 pp is pure day-type composition**; the genuine within-stratum residual is ≤0.19 pp per slot.

### Contrast with pre-calibration
`step5_fails.md` (pre-rake) attributed the then-6.73 pp to Work→AT_HOME=0 depletion in weekday synthetic diaries. Calibration (8B-5b) raked the per-(stratum×slot) `hom30` to the observed rate, eliminating that deficit. What remains is the benign mix effect — a **different and much smaller** phenomenon.

### Paper recommendation
Report the **composition-held / within-stratum** figure (≤0.19 pp) as the authoritative AT_HOME fidelity metric, and present the raw 4.37 pp explicitly as a day-type-composition effect (the validator's aggregate baseline mixes strata). This is honest and strengthens the calibration claim. **Do not** simply relax the ±3 pp threshold — decompose it instead. Not a Step-7 blocker (BEM keys off the calibrated `hom30`; night AT_HOME 2.4 passes at 85.6 %).

---

## 3. Group B — un-raked `act30` limitations (6.2 Work, 3.3 night-sleep)

These are **Step-4 J3 activity-channel properties**, unchanged by calibration because raking touches `hom30` only (deliberate: the downstream BEM occupancy keys off `hom30`, not `act30`). They are genuine, documented model limitations — appropriate for §4.2, not blockers.

### 6.2 — Work over-fire (+3.27 / 3.29 pp)
J3 over-represents Work & Related vs observed GSS (≈21.6 % vs 18.3 % aggregate; ≈+7 pp in the IS_SYNTHETIC=1 component). The activity CE loss plateaued at Step-4 training; JS divergence (0.0191, gate-passing) is too coarse to penalise a marginal shift in one large class. **Verdict:** real, bounded, documented. Within ASHRAE-90.1-class occupancy uncertainty for BEM. Document §4.2.

### 3.3 — night-slot sleep dominance 67.49 % (< 70 %)
Night slots 1–8 = 04:00–08:00. Activity breakdown across those slots (verification run):

| act30 | label | share of slots 1–8 |
|---|---|--:|
| 5 | Sleep & Naps | **67.49 %** |
| 1 | Work & Related | 10.40 % |
| 7 | Personal Care | 6.38 % |
| 13 | Travel | 3.77 % |
| 6 | Eating | 3.07 % |
| 2 | HH Work | 2.87 % |

The non-sleep 32.5 % is a plausible early-morning routine (personal care, eating, commute), but the **10.4 % Work** is elevated for 04:00–08:00 — the same Work over-fire as 6.2 bleeding into the early-morning window, abetted by J3's high activity-transition rate (Step-4 §4.2 ratio ≈158× observed). It is **borderline** (2.5 pp under gate). **Critically, AT_HOME for the same slots passes at 85.6 %** (gate 2.4 ≥85 %) — occupants are home and generating metabolic load regardless of the activity label, so EnergyPlus occupancy is intact. **Verdict:** real model limitation, BEM-harmless. Document §4.2; flag a transition-rate regulariser for any future J3 retrain.

---

## 4. Group C — `--excl`-only validator issues (fixable)

The `--excl` run shows **4 extra FAILs vs the normal run** (9 vs 5). All four are validator-side, not data-side:

### 1.1 / 4.5 / 5.6 — row count 285,419 vs hardcoded 286,537
The validator's expected row count is the **pre-exclusion** count (286,537). Under `--excl` the file is correctly 285,419 (286,537 − 1,118 excluded HHs). These three FAILs are **spurious** — the exclusion is intentional and documented.
**Recommendation (FIX):** make the expected count exclusion-aware under `--excl` (`expected = 286_537 − n_excluded`, read from `…_excluded_ppids.csv`). This is a comparison-baseline correction, **not** a threshold relaxation — it removes 3 false FAILs that would otherwise misrepresent the pipeline in the paper.

### 5.4 / 6.4 — DTYPE vs Census 0.1063 % (gate: exact)
Excluding 1,118 single-person HHs slightly shifts the matched DTYPE distribution away from the Census reference (single-person dwellings skew toward apartments). 0.1063 % is negligible, but the gate demands an **exact** match, which is unattainable once any HH is excluded.
**Recommendation (FIX or document):** under `--excl`, relax 5.4/6.4 to a small tolerance (e.g. ≤0.5 pp) or compare against the **post-exclusion** Census subset. Either is defensible; document the choice.

> These two fixes are the only **code** changes recommended. They correct the validator's handling of the (intended) exclusion; they do not touch any model output or loosen any scientific gate. After them, the `--excl` sheet reads **30 PASS / 0 WARN / 4 FAIL** (measured 2026-06-01) — *cleaner* than the normal run (whose 4.4 still FAILs pre-exclusion), with only the Group-A/B documented items remaining. See the Progress Log below.

---

## 5. Group D — Step-6 DRIFT WARNs (superseded metric)

The 3 WARNs (3.2 / 3.4 / 3.6: count of weekday activities with per-activity drift > 0.001 is 1 / 2 / 1, gate ≥3) are on a metric the Step-6 team already **retired**. The COVID AT_HOME shift is a *joint aggregate* across `hom30` slots, not visible in any single per-activity marginal JS — so "count of WD activities that drifted" is the wrong instrument (documented in `06_longitudinalForecastingGSS.md`, 2026-05-14 post-hoc analysis). The **replacement** gate **3.7 (COVID AT_HOME aggregate residual ≤5 pp) PASSES at 0.2 pp**, and weekend drift is rich (9–10 activities). Weekday routines are simply more stable across cycles than weekends, so WD drift concentrates in few activities — expected, not a defect.

**Recommendation:** in the validator, downgrade 3.2/3.4/3.6 to informational (or raise to ≥1) so the authoritative §3.7 gate is the one reported; document that the marginal-JS count was superseded by the aggregate-residual gate. The Step-6 hard gates (backcast JS WD 0.063 / Sat 0.164 / Sun 0.162; §5.1–5.6; §6 BEM-readiness) all pass.

---

## 6. Step-7 readiness verdict

**GO.** No item blocks the EnergyPlus simulations:
- The calibrated channel (`hom30`) that BEM consumes is exact within-stratum (≤0.19 pp composition-held); night AT_HOME 85.6 %.
- Group A is a composition artefact; Group D is a retired metric; Group C is two validator-baseline fixes that don't touch data.
- Group B (Work over-fire, night-sleep) lives in `act30`, which BEM does not key occupancy off — documented limitation, harmless to the energy simulation (OP5: ~1.8 % (2022) / ~2.1 % (2030) act/hom coherence cost, BEM-safe).

**Recommended actions before submission:**
1. **(code)** Make `05_censusLinkageGSS_val.py` exclusion-aware for row-count (1.1/4.5/5.6) and DTYPE tolerance (5.4/6.4) under `--excl`.
2. **(code, optional)** Downgrade Step-6 3.2/3.4/3.6 to informational; surface §3.7 as the COVID gate.
3. **(paper)** Use the §4.2 text below; report AT_HOME fidelity as the composition-held / within-stratum residual.
4. **(none)** No model retrain required for Step 7; transition-rate regulariser is future work only.

---

## 7. Paper §4.2 text (post-calibration, supersedes the `step5_fails.md` paragraph)

> **Downstream validation of the calibrated diaries (Steps 5–6).** Post-hoc raking (Phase 8B) aligns the synthetic per-(stratum×slot) at-home marginal to the observed rate in the exact population the linkage validator scores: within-stratum, synthetic and observed at-home rates agree to ≤1.1 pp per slot, and ≤0.19 pp once day-type composition is held constant. The residual 4.4 pp aggregate per-slot difference reported by the linkage validator is a day-type **composition** effect — the observed comparison subset is 92.6 % weekday whereas the full Census-matched population is 71.3 % weekday — not a model error. Two activity-channel limitations persist by design, as raking adjusts location (at-home) but not activity: Work & Related is over-represented by ≈3.3 pp relative to observed GSS, and pre-dawn (04:00–08:00) sleep dominance is 67.5 % against a 70 % heuristic, the shortfall being early-morning Work and personal-care coding; the at-home rate for those slots nonetheless exceeds 85 %, so building-occupancy schedules for the energy model are unaffected (the energy model keys occupancy on location, not activity). The 2030 forecast passes all plausibility gates (at-home 79.7 %, weekday < weekend, night-sleep 89.0 %, weekday continuity 4.2 pp) and backcasts 2022 with weekday Jensen–Shannon divergence 0.063. Households whose calibrated mean at-home fell below a 0.30 physical floor (1,118 of 145,589; 0.8 %) were excluded prior to energy simulation. The official-language key (KOL) was omitted from the 7-key demographic match (absent from the augmented pool; low cardinality, expected negligible effect).

---

## 8. Provenance

- Validator runs: `05_censusLinkageGSS_val.py` {normal, `--excl`}, `06_longitudinalForecastingGSS_val.py` — 2026-06-01 reproducibility pass (see `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md`, Progress Log 2026-06-01).
- Evidence: `Step5_docs/_verify_warnings.py` on `aug_pipeline/21CEN22GSS_aug_Full_Schedules_excl.csv` (285,419 rows; 157,103 obs / 128,316 syn).
- Supersedes the AT_HOME (2.2/6.1) and floor (4.4) sections of `outputs_step5/step5_fails.md` for the post-calibration model.

---

## 9. Progress Log

### 2026-06-01 — Validator fixes applied + re-run (Groups C & D)

Applied the two recommended fixes (Group C: row-count + DTYPE under `--excl`; Group D: Step-6 DRIFT WARNs). **No model output or data file was touched, and no scientific gate was loosened.** The Group-A (AT_HOME composition, 2.2/6.1) and Group-B (`act30`: 6.2 Work, 3.3 night-sleep) items were intentionally left as documented FAILs per §2–§3.

**Code changes**

- `2J_docs_occ_nTemp/05_censusLinkageGSS_val.py`
  - Added `self.expected_rows` in `__init__`: under `--excl` it reads `…_aug_excluded_ppids.csv` and sets `expected = 286,537 − n_excluded` (= 285,419). Row-count gates **1.1 / 4.5 / 5.6** now compare against the correct post-exclusion baseline — still an *exact* check, just the right number.
  - DTYPE gates **5.4 / 6.4**: under `--excl`, the Census comparison is restricted to the **retained PP_IDs** (`census[census.PP_ID.isin(bem.PP_ID)]`). DTYPE is a per-PP_ID Census attribute, so this is the correct like-for-like exact-match test — **not** a tolerance relaxation.
- `eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecastingGSS_val.py`
  - DRIFT WD-activity checks **3.2 / 3.4 / 3.6** changed from a `≥3` gate to **informational** (always reported, never WARN/FAIL), labelled `[info]` with a pointer to the authoritative gate **3.7**. The marginal-JS WD count is a superseded metric (the COVID shift is a joint aggregate; Bundle 3.11). Weekend gates (3.2b/3.4b/3.6b) and 3.7 remain real gates and pass.

**Re-run results (2026-06-01)**

| Sheet | Before | After | Change |
|---|---|---|---|
| Step 5 normal | 29 PASS / 0 WARN / 5 FAIL | 29 / 0 / 5 | unchanged — no regression ✓ |
| Step 5 `--excl` | 25 PASS / 0 WARN / 9 FAIL | **30 / 0 / 4** | 5 spurious FAILs removed ✓ |
| Step 6 | gates PASS / 3 WARN | gates PASS / **0 WARN** | DRIFT WARNs → informational ✓ |

- **Step-5 `--excl` FAILs removed:** 1.1 / 4.5 / 5.6 (row count → PASS at 285,419), 5.4 / 6.4 (DTYPE → **0.0003 %**, was 0.1063 %). 4.4 PASSES post-exclusion (below=0), so `--excl` is now *cleaner* than the normal sheet (normal still shows 4.4 FAIL = 1,118 pre-exclusion HHs).
- **Step-5 remaining 4 FAILs** are exactly the documented items: 2.2 / 6.1 AT_HOME composition artefact (4.37 pp; Group A) and 3.3 night-sleep (67.49 %) + 6.2 Work (3.29 pp) un-raked `act30` (Group B).
- **Step-6:** 3.2/3.4/3.6 now `[PASS] … (informational — superseded by gate 3.7)`; gate 3.7 PASS at 0.2 pp residual; all hard gates green.

**Reports regenerated:** `outputs_step5/step5_validation_report{,_excl}.html`, `outputs_step6/step6_validation_report.html`.

**Net for the manuscript:** the only non-PASS lines remaining anywhere in Steps 5–6 are the documented Group-A (composition artefact) and Group-B (`act30`, by-design un-raked) items, both fully explained above and in the §7 paper text. No Step-7 blocker.
