# 2J Occupancy Pipeline — Master Improvement & Bug-Fix Log

**Compiled:** 2026-07-15
**Purpose:** single, one-by-one record of every improvement/bug-fix applied across Steps 4–9 of the 2J (single-channel) GSS occupancy pipeline, with root-cause diagnostics, the fix, before→after numbers, artifacts touched, status, and links to the original source documents. Built for reuse when analyzing these improvements for the **3rd Journal paper** (3J, two-/four-split BEM work) — several of these fixes (region-tier linkage, joint 3-head raking, multi-zone injection bug) are shared code paths that also affect 3J.
**How this was built:** each step's source documents (improvement notes, employee/handoff prompts, fails/investigation docs, validation-report HTML scorecards) were re-read directly (not recalled from memory) by dedicated research passes; every number below was cross-checked against the underlying artifact where possible.
**Root pipeline docs:** [`00_GSS_Occupancy_Pipeline.md`](../00_GSS_Occupancy_Pipeline.md) · [`00_GSS_Occupancy_Pipeline_Overview.md`](../00_GSS_Occupancy_Pipeline_Overview.md)

---

## How to read each entry

Every improvement below follows the same four-part structure:

- **🩺 Diagnostic** — what was actually broken, how it was found, and *why* an improvement was needed (root cause, not just symptom).
- **🔧 Fix applied** — exactly what changed (scripts, logic, flags).
- **📊 Before → After** — quantified impact, taken from the live artifacts.
- **📁 Status / Artifacts / Source** — done/open/deferred, which files were regenerated, and a relative link back to the original document.

---

## Quick index

| Step | Topic | # Improvements | Span | Status |
|---|---|---|---|---|
| [Step 4](#step-4--j3-model-augmentation) | J3 two-channel augmentation model | 4 tasks + 1 remediation chain | 2026-07-09 | ✅ Closed |
| [Step 5](#step-5--census-linkage-validator) | Census-GSS linkage / raking validator | 7 entries | 2026-05-12 → 2026-07-10 | ✅ Closed |
| [Step 6](#step-6--2030-forecast-validator) | 2030 longitudinal forecast validator | 4 improvements | 2026-07-10 | ✅ Closed |
| [Step 7](#step-7--bem-integration-validator) | BEM schedule integration validator | 4 improvements + follow-up round | 2026-07-10 | ✅ Closed (1 deferred item propagated to Step 8/9) |
| [Step 8](#step-8--bem-simulation-campaign) | BEM simulation campaign (EnergyPlus) | 5 items | 2026-07-07 → 2026-07-15 | ✅ Closed (Bug-A decision gate fully closed 2026-07-15) |
| [Step 9](#step-9--activity-driven-loads-validation) | Activity-driven end-use load validation | 5 items (Thread A) + 3 items (Thread B, 3J) | 2026-06-08 → 2026-07-15 | ⚠️ Mostly closed — **1 open exposure gap flagged** |

**Cross-cutting:** [Cross-step dependency map](#cross-step-dependency-map) · [Master open/deferred list](#master-open--deferred-items-list) · [Chronological timeline](#chronological-timeline-all-steps)

---

## Step 4 — J3 model augmentation

Working docs: [`outputs_step4/improvement_planning/`](../outputs_step4/improvement_planning/) · Report: [`step4_validation_report_v7.html`](../outputs_step4/step4_validation_report_v7.html) · Notes: [`step4_improvement_notes.md`](../outputs_step4/improvement_planning/step4_improvement_notes.md) · Implementation log: [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md) · Confirmation review: [`step4_improvements_confirmation.md`](../outputs_step4/improvement_planning/step4_improvements_confirmation.md) · Handoff: [`employee-prompt.md`](../outputs_step4/improvement_planning/employee-prompt.md)

All dated **2026-07-09**, executed in order 2 → 1 → 3, with a mid-stream **Remediation** (independent audit) inserted between Task A and its final close-out, then a same-day **Task D** follow-up.

### Phase 0 — Confirmation review

🩺 **Diagnostic:** before any code was touched, a director-level pass verified the three candidate improvements against source (`05_postlink_rake.py`, `05_census_linkage.py`, `02_harmonizeGSS.py`, `04F_validation.py`, `05_censusLinkageGSS_val.py`, `06_forecast_rake.py`, `04L_joint_rake_test.py`) to make sure the plan matched what the code actually did. Two doc/code discrepancies were caught here that would otherwise have silently biased later numbers: agent count documented as 286,540 in places vs. the code's real 286,537; and a stale `LFTAG==5` reference in `04F_validation.py` conflicting with the `{1,2,3}` coding actually in use.
🔧 **Fix:** none yet — this set execution order (2→1→3) and flagged the two discrepancies for Step-0 verification inside Task B.
📁 **Status:** DONE. **Source:** [`step4_improvements_confirmation.md`](../outputs_step4/improvement_planning/step4_improvements_confirmation.md)

### Task A (Improvement 2) — 2005 `PR` census-linkage gap

🩺 **Diagnostic:** `02_harmonizeGSS.py`'s `recode_pr()` left 2005 GSS diaries in a legacy 5-region scheme, disjoint from the Census SGC province codes used by 2010/2015/2022. Because `PR` was the key for both Tier-1 and Tier-2 census-linkage matching, **every 2005 diary failed both tiers automatically**: 2005 supplied 30.0% of the diary pool but won only ~9% of matches, scrambling 2005's geography and depressing its Section-7 paid-work bar. This needed fixing because it silently degraded the oldest survey cycle's representativeness in every downstream table.
🔧 **Fix applied (first attempt, later found flawed):** added a `REGION_FOLD` crosswalk and a new **Tier-2b** fallback tier, gated behind `--region-tier`. Logged result: 2005 matched share 8.91%→28.76%.
🩺 **Diagnostic (self-correction / independent audit):** re-reading `run_slot_match()` showed Tier-2b only fires *after* Tier-1 and Tier-2 both fail on raw `PR` — so it was structurally capped at **0.47% of agents (1,352 of 286,537)** and could never have produced a ~3× jump. A fresh re-derivation from the actual on-disk `Full_Schedules.csv` reproduced the **pre-fix** 9.03% — proof that the logged "28.76%" was never actually produced by a real run. This is why the fix had to be redone: shipping the false number would have overstated the 2005 fix by roughly 2× in the paper.
🔧 **Real fix:** merged the region-folded key **into Tier-2 itself** (not a separate fallback tier); Tier-1 left untouched.
📊 **Before → After:** 2005 matched share **9.03% → 15.76%** (25,863 → 45,164 rows) — a genuine near-doubling. 2010 32.52%→29.93%, 2015 34.80%→32.04%, 2022 23.66%→22.27%. Tier-1 byte-identical (128,778 rows) across all runs. A structural ceiling was documented: Tier-1 (44.94% of the population) is permanently closed to 2005 by data design, so the naive ~30% supply target is unreachable.
📁 **Artifacts:** `archive/05_census_linkage.20260709.py` (original) and `archive/05_census_linkage.20260709_preTier2Merge.py` (flawed version) both preserved. Full downstream rebuild run (`--aggregate`→`--bem`→`--exclusion`→BEM 2022/2030). `05_censusLinkageGSS_val.py --excl`: **30 PASS / 0 WARN / 4 FAIL** (0 new regressions).
**Status:** DONE/CLOSED. **Source:** [`step4_improvement_notes.md`](../outputs_step4/improvement_planning/step4_improvement_notes.md) (Improvement 2), [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md) (Task A + Remediation R1–R2)

### Task B (Improvement 1) — Joint 3-head calibration (act30 + hom30 + cop30)

🩺 **Diagnostic:** `05_postlink_rake.py` raked only `hom30` (AT_HOME) to observed marginals; `act30` (14-category activity) and `cop30` (co-presence) were left J3-native and un-calibrated. Measured gap: weekday paid-work **over-fired** by +12.3 pp (obs 13.3% vs syn 25.6%); equipment shape mean|Δ| 14.9% (peak 32%); lighting 3.8 pp; metabolic +1.9%. This drove validation gate 6.2 to an accepted-but-unresolved FAIL. The fix was needed because BEM end-use shapes (equipment/lighting/metabolic) are driven directly by `act30`, so leaving it un-raked meant every downstream simulated load shape inherited this bias.
🔧 **Fix applied:** new `_rake_categorical_slot()` (14-way minimal-move rake) applied to `act30` **within** `hom30`=1/0 subsets per stratum×slot×LFTAG (sparsity-gated); 9 `cop30` channels raked standalone per-slot. New `--joint` flag added to both `05_postlink_rake.py` and `06_forecast_rake.py`; the no-flag path verified byte-identical to predecessors.
🩺 **Diagnostic (mid-implementation gap, B3):** `main_joint()` initially lacked `main()`'s single-person-household 0.30-floor guard — would have regressed gate 4.4 if shipped. Ported as a new Step 1b.
🩺 **Diagnostic (false-alarm investigated, not just accepted):** raw coherence appeared to move the *wrong* direction (11.79%→18.04% vs. a "~1.8–2.1%" target). Root-caused to a metric-definition mismatch (the old target used a narrower "newly-flipped-records-only" metric); under the correct, broader metric the **observed population's own ground truth is 13.06%**, and the rake's own per-cell reconstruction matched its target almost exactly (18.041% predicted vs 18.042% actual) — i.e. a genuine realism gain, not a regression. Recording this here because a naive "before/after" comparison would have wrongly flagged the fix as broken.
📊 **Before → After (first run, later fully re-run — see Remediation):** Gate 6.2 → **PASS**. Shape gaps: Equipment mean|Δ| **12.0%→4.3%**; Lighting **4.4pp→1.0pp**; Metabolic **+4.3%→−0.4%**. act30 moves: 1,728,736; COP flips 5,114,530 across 9 channels, per-cell-slot max gap 0.001 pp.
📁 **Deviation flagged (not silently absorbed):** `2030_synthetic_diaries.csv` has only 99 columns (no LFTAG/COP), so the 2030 rake runs without LFTAG conditioning and the COP step is explicitly skipped (not fabricated) for 2030.
**Status:** DONE, then fully re-run on the Remediation-corrected population (see below). **Source:** [`step4_improvement_notes.md`](../outputs_step4/improvement_planning/step4_improvement_notes.md) (Improvement 1), [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md) (Task B)

### Task C (Improvement 3) — Validation-report figures (v5 → v6)

🩺 **Diagnostic:** the v5 report's Task-A/B findings existed only as prose/tables, making it hard to visually audit magnitude and direction of the fixes.
🔧 **Fix:** added 3 base64-embedded figures (cycle-representation funnel, act30→BEM sensitivity before/after bars, PR-coding disjointness strip) into a new `step4_validation_report_v6.html`, alongside existing tables; v5 kept byte-identical.
🩺 **Diagnostic (real finding that triggered the Remediation below):** while building Fig 1, re-measuring pool composition against the *on-disk* `Full_Schedules.csv` reproduced the pre-fix CYCLE_YEAR distribution, not the logged post-fix numbers — while the companion `Matched_Keys.csv` correctly showed post-fix counts. This discrepancy, flagged rather than silently fixed in-place, is exactly what proved Task A's first-attempt number was false and triggered the independent audit.
📁 **Status:** DONE (report-only); this task's own discrepancy flag is what needed the improvement below. **Source:** [`step4_improvement_notes.md`](../outputs_step4/improvement_planning/step4_improvement_notes.md) (Improvement 3), [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md) (Task C)

### Remediation — Independent audit + full re-run chain

🩺 **Diagnostic:** Task C's discrepancy flag needed resolving before anything could ship. An independent audit rejected the "stale snapshot" hypothesis and instead proved, from `run_slot_match()`'s own logic, that Tier-2b (a fallback reached only after Tier-1/2 both fail) was mathematically capped at 0.47% of agents and could never have produced the originally logged 28.76%/82,407-row result — **no artifact ever supported that number**. This mattered because every Task-B measurement downstream had been computed on the flawed, never-actually-real population.
🔧 **Fix:** merged Tier-2b into Tier-2 (the real Task-A fix, above); re-ran the entire downstream chain twice — once on the Task-A-only corrected population, then again with Task B's joint rake applied on top.
📊 **Before → After (final, verified population):** **6,934,320 rows / 144,465 households** both years; 2022 WD/WE occupancy 0.702/0.743; 2030 WD/WE 0.785/0.804; 1,170 HH excluded (0.41%), 285,367 rows. Full validator sweep: `05_censusLinkageGSS_val.py --excl` **30/0/4** (zero new regressions); Step-6 validator 0 WARN/0 FAIL across all 7 sections. Final shape gaps: Equipment mean|Δ| **4.9%** (was 12.0%), Lighting **1.1pp** (was 4.4pp), Metabolic **−0.5%** (was +4.3%) — plan targets still met with wide margin using the *real*, verified numbers. The v6 report's Fig 1/Fig 2 and every dependent prose value were corrected; language changed from "Resolved"/"gap closed" to **"Improved, not eliminated"** with the structural-ceiling explanation added.
📁 **Status:** CLOSED. **Source:** [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md), Remediation checklist R1–R7

### Task D (Improvement 4) — v6 stale-figure audit → v7 report

🩺 **Diagnostic:** a user review of v6 raised four apparent anomalies. All four traced to **one root defect**: v6's prose/tables were post-fix, but its 7 inherited section charts (Training Curves, Activity Distribution by Stratum, JS Heatmap, AT_HOME Daily Rhythm, Activity Heatmap, Work Proportion by LFTAG, Work by Stratum) were still rendered from v5's pre-fix population — because v6 was built as an additive copy of v5, the stale images carried over unnoticed. This is a classic "report says X, picture still shows old X" bug, dangerous because it's invisible unless someone checks image-generation timestamps against data-rebuild timestamps.
🔧 **Fix:** new `_gen_v7_plots.py` (alt-keyed `<img>` replacement on the 7 exact stale titles, idempotency token `data-regen="v7-20260709"`) regenerated exactly those 7 charts against the final, fully-corrected population, in a new `step4_validation_report_v7.html` (v6 kept byte-identical).
📊 **Before → After (confirmed live in v7):**

| Item | Old (v6, stale) | New (v7) |
|---|---|---|
| Aggregate activity JS (§2) | 0.0191 | **0.0047** |
| Calibrated synthetic rows | 128,918 | **128,741** |
| Linked population (_excl) | 285,419 | **285,367** |
| BEM rows (both years) | 6,936,336 | **6,934,320** |
| BEM households (both years) | 144,507 | **144,465** |
| 2022 Occupancy WD/WE | 0.703/0.749 | **0.702/0.743** |
| §4.4 exclusion count | 1,413→1,118 HH | 1,413→**1,170 HH** |
| §2 weekday Paid-work | obs 13.3% vs syn 25.6% (+12.3pp) | **obs 16.50% vs syn 20.28% (3.78pp)** |

Gate tally unchanged: **22 PASS / 0 WARN / 0 FAIL** (Task D touched reporting only, no gate computation).
🩺 **Deviation flagged, not silently absorbed:** the Section-7 2005 bar did **not** rise toward the other cycles as expected — final 2005 synthetic weekday paid-work = 13.41%, *below* 2010/2015/2022 (21.68/21.56/21.45%) and below 2005's own observed value (17.96%). Likely cause: the rake conditions on stratum×slot×LFTAG, not CYCLE_YEAR. Flagged as a possible follow-up, not resolved here.
📁 **Status:** DONE/CLOSED. **Source:** [`step4_improvement_notes.md`](../outputs_step4/improvement_planning/step4_improvement_notes.md) (Improvement 4), [`step4_improvements_implementation.md`](../outputs_step4/improvement_planning/step4_improvements_implementation.md) (Task D), [`employee-prompt.md`](../outputs_step4/improvement_planning/employee-prompt.md)

### Step 4 — open/deferred items
- Section-7 2005 bar residual pattern (Task D deviation) — flagged for follow-up, not resolved.
- Section-3 (AT_HOME) visual re-check — reasoned-but-not-visually-confirmed (no browser rendering in that session).
- `measure_shape_gaps.py` (v1) explicitly **not valid** for direct before/after-Task-B comparison — kept only as a standalone BEM-fidelity diagnostic; `measure_shape_gaps_v2_samebasis.py` is the one used for all official claims.
- Both shape-gap scripts remain **report-only diagnostics**, not yet promoted to hard pass/fail gates.

---

## Step 5 — Census linkage validator

Working docs: [`outputs_step5/step5_improvement_notes.md`](../outputs_step5/step5_improvement_notes.md) · [`outputs_step5/step5_fails.md`](../outputs_step5/step5_fails.md) · [`Step5_docs/Step5_6_warnings_investigation.md`](../Step5_docs/Step5_6_warnings_investigation.md) · [`Step5_docs/_verify_warnings.py`](../Step5_docs/_verify_warnings.py) · Report: [`step5_validation_report.html`](../outputs_step5/step5_validation_report.html) (canonical) · Archived predecessors: [`outputs_step5/previous/`](../outputs_step5/previous/)

### Entry 1 — Initial FAIL investigation (baseline diagnostic)

🩺 **Diagnostic:** first systematic diagnosis of the pre-calibration population (286,537 rows). Found: **2.2/6.1** AT_HOME per-slot max diff 6.73 pp (gate ≤3pp), 9 breaching slots at morning-departure/evening-return; **6.2** Work time-share Δ+3.27pp (gate ≤2pp); **3.3** night-sleep dominance 67.46% (gate ≥70%); **4.4** 1,248 households (0.86%) with implausible mean AT_HOME <0.30. Root causes traced to the Step-4 J3 model: a post-hoc `Work→AT_HOME=0` rule amplifying the activity bias into an AT_HOME deficit, plus J3 temporal over-fragmentation. This diagnostic set the baseline every later fix is measured against.
📁 **Status:** superseded by Entry 3 for the AT_HOME/floor items once calibration landed; the 6.2/3.3 (`act30`) analysis remains valid since `act30` is never raked by the hom30-only rake. **Source:** [`step5_fails.md`](../outputs_step5/step5_fails.md), 2026-05-12.

### Entry 2 — Phase-8B hom30 raking (calibration input)

🩺 **Diagnostic:** synthetic per-(stratum×slot) `hom30` marginals diverged from observed rates by up to 6.73pp (Entry 1).
🔧 **Fix:** raked synthetic `hom30` to the observed rate per stratum×slot — deliberately touching `hom30` only (BEM occupancy keys off it), not `act30`.
📊 **Before → After:** within-stratum AT_HOME max|diff| collapsed to **WD 0.50pp / Sat 0.89pp / Sun 1.09pp**; floor-breach households **1,248 → 1,118**.
📁 **Status:** DONE (upstream input to Entry 3+). **Source:** referenced in [`Step5_6_warnings_investigation.md`](../Step5_docs/Step5_6_warnings_investigation.md) §2/§9.

### Entry 3 — Post-calibration warnings investigation + validator fixes

🩺 **Diagnostic (4 groups classified, not all "bugs"):**
- **Group A** — AT_HOME max diff still 4.48pp post-raking, but re-diagnosed as a **day-type composition artefact**: the observed baseline is 92.61% weekday vs 71.34% weekday in the full population — not a modeling error.
- **Group B** — Work (3.27/3.29pp) and night-sleep (67.46/67.49%) unchanged — genuine, by-design `act30` limitations (raking only touches `hom30`).
- **Group C** — the `--excl` validator run showed **4 spurious extra FAILs** (9 vs 5): row-count gates compared post-exclusion counts against a hardcoded pre-exclusion expectation (a **real validator bug**), and DTYPE gates demanded an unattainable exact match once households were excluded.
- **Group D** — Step-6 DRIFT WARNs flagged a superseded metric (per-activity drift instead of the joint AT_HOME aggregate, which already passes).
This diagnostic mattered because it separated *real validator bugs* (Group C, needed fixing) from *documented model residuals* (Groups A/B, needed labeling not fixing) — conflating them would have led to either wasted fix effort or unexplained FAILs in the paper.
🔧 **Fix (Group C & D only):** `05_censusLinkageGSS_val.py` — added `expected_rows` under `--excl` (reads the excluded-PPIDs file, sets expected = 286,537 − n_excluded); DTYPE gates restricted to retained PP_IDs (like-for-like fix, not a tolerance relaxation). `06_longitudinalForecastingGSS_val.py` — DRIFT checks changed from hard gate to informational `[info]`.
📊 **Before → After:** Step-5 normal 29P/0W/5F (unchanged, no regression); Step-5 `--excl` **25P/0W/9F → 30P/0W/4F**; Step-6 gates PASS/3 WARN → PASS/**0 WARN**; DTYPE diff 0.1063%→**0.0003%**.
🔧 **Verification tooling added:** [`_verify_warnings.py`](../Step5_docs/_verify_warnings.py) — deterministic, read-only re-derivation proving the 4.37pp composition-held aggregate collapses to ~0.19pp once day-type mix is held constant.
🩺 **Deferred, explicitly rejected:** recalibrating gate thresholds (±7pp AT_HOME/≥65% sleep) was considered and **rejected as goalpost-moving**; the composition-held decomposition was reported instead.
📁 **Status:** DONE. Explicit Step-7 readiness verdict: **GO**. **Source:** [`Step5_6_warnings_investigation.md`](../Step5_docs/Step5_6_warnings_investigation.md), 2026-06-01.

### Entry 4 — Task A (region-tier linkage) + Task B (joint rake) land in Step 5's population

🩺 **Diagnostic:** context carry-over from Step 4's Task A/B (these fixes physically live in Step-5-adjacent code — `05_census_linkage.py`/`05_postlink_rake.py`). Pre-fix state: 29P/0W/5F, AT_HOME 4.48pp, sleep 67.46%, Work 3.27pp, §4.4 FAIL at 1,118 HH.
📊 **Before → After:** **29P/0W/5F → 30P/0W/4F**; AT_HOME 4.48→**4.27pp**; sleep 67.46→**69.05%**; Work 3.27→**2.15pp**; §4.4 FAIL→PASS (via the 5H exclusion of Entry 5).
📁 **Status:** DONE. **Source:** context section of [`step5_improvement_notes.md`](../outputs_step5/step5_improvement_notes.md).

### Entry 5 (Improvement 1) — 5H exclusion + report reconciliation

🩺 **Diagnostic:** two live report files disagreed with neither labelled authoritative (Jun-11 pre-fix 29P/0W/5F vs Jul-9 post-fix 30P/0W/4F); three different exclusion counts were in circulation (1,118 HH, 1,170 rows, 1,248 HH) from three different pipeline states. Needed reconciling before the report could be cited in the paper.
🔧 **Fix:** re-derived the exclusion count live on the current rebuild → **1,170 rows (0.41%)** declared authoritative; promoted `step5_validation_report_v2.html` to the canonical `step5_validation_report.html`; archived the Jun-11 original to `previous/step5_validation_report_pre_taskAB_20260611.html`.
📊 **Before → After:** 29P/0W/5F → **30P/0W/4F**; exclusion pinned at 1,170 rows.
📁 **Status:** DONE. **Source:** [`step5_improvement_notes.md`](../outputs_step5/step5_improvement_notes.md) (Improvement 1), 2026-07-10.

### Entry 6 (Improvement 2) — Five new figures added

🩺 **Diagnostic:** the report was gate-and-table heavy (6 figures for 34 checks); several decision-relevant quantities existed only as scalars, making the Task A/B trajectory hard to see at a glance.
🔧 **Fix:** new [`_gen_step5_v2_plots.py`](../outputs_step5/step5_improvement_notes.md) added 5 figures: F1 (per-slot AT_HOME residual, max 4.27pp), F2 (before→after trajectory on 3 gates, kept amber/"still just-failing" — no green-washing), F4 (14-activity share, Work the lone >2pp outlier), F5 (per-HH AT_HOME histogram with exclusion tail shaded), F6 (3 surviving FAILs as "distance past gate": 1.27/0.95/0.15pp).
📊 **Before → After:** figure count 6 → 11.
📁 **Deferred, with reasons:** **F3** (cycle-representation funnel) deferred — needs a flag-off "before" run the already-fixed population can't provide. **F7** (completeness bars) deferred — "all-100% filler," low value.
**Status:** DONE. **Source:** [`step5_improvement_notes.md`](../outputs_step5/step5_improvement_notes.md) (Improvement 2), 2026-07-10.

### Entry 7 (Improvement 3) — Reframe the three borderline gates

🩺 **Diagnostic:** three FAILs (AT_HOME 4.27pp, sleep 69.05%, Work 2.15pp) stood as unexplained red FAILs despite all being within ~1pp of passing and all being documented J3 residuals — a reviewer could easily misread these as unresolved bugs rather than known, bounded model limitations.
🔧 **Fix (Option B — relabel + document, chosen over recalibrating gates or deferring to a retrain):** added a "Post-Task-A/B update & reading guide" panel stating the disposition explicitly, citing Fig F2 (trajectory) and Fig F6 (severity map) as evidence. **Gate thresholds themselves left unchanged** — no goalpost-moving.
📁 **Deferred:** **Option A** (recalibrate to ≈±7pp/≥65%) kept documented as available but not implemented. **Option C** (Step-4 J3 retrain with an `L_trans` transition-rate penalty) tracked as a separate future model-iteration task.
**Status:** DONE (reporting side). **Source:** [`step5_improvement_notes.md`](../outputs_step5/step5_improvement_notes.md) (Improvement 3), 2026-07-10.

### Step 5 — open/deferred items
- Option A (gate recalibration) and Option C (J3 retrain with transition-rate penalty) — both documented, neither implemented.
- F3/F7 figures — deferred.
- A file-organization discrepancy was found in `outputs_step5/previous/`: the notes doc implies `step5_validation_report_excl.html` stays in the root as the figure-less generator source, but on disk all three predecessor files (`_excl`, `_v2`, pre-Task-A/B original) currently sit in `previous/`. Worth a quick check before citing "the canonical generator source" in the paper.

---

## Step 6 — 2030 forecast validator

Working docs: [`outputs_step6/improvement/step6_improvement_notes.md`](../outputs_step6/improvement/step6_improvement_notes.md) · Scripts: [`_validate_joint_raked_2030.py`](../outputs_step6/improvement/_validate_joint_raked_2030.py), [`_gen_step6_plots.py`](../outputs_step6/improvement/_gen_step6_plots.py), [`_gen_step6_names.py`](../outputs_step6/improvement/_gen_step6_names.py), [`_gen_step6_panel.py`](../outputs_step6/improvement/_gen_step6_panel.py) · Report: [`step6_validation_report.html`](../outputs_step6/step6_validation_report.html) · Archived predecessors: [`outputs_step6/previous/`](../outputs_step6/previous/)

All 4 improvements ("Option A" bundle) dated **2026-07-10**.

### Improvement 1 — Lineage check (does Step 6 need rebuilding?)

🩺 **Diagnostic:** after Steps 4/5 were refreshed, it needed verifying whether Step 6's forecast data was now stale. Traced code dependencies: `06_forecast_rake.py`/`06_longitudinalForecasting.py` read `augmented_diaries.csv` (Step-4 J3 output) directly, and only import *code* (not data) from `05_postlink_rake.py`; confirmed no J3 retrain since ~May 23 and `augmented_diaries.csv` unchanged (Apr 23, 192,183 rows). Step 5 never actually feeds Step 6 (Step-5's linked population feeds Step 7 only).
🔧 **Fix:** none needed — **Option A confirmed**: Step-6 forecast data is current. Standing rule set: only rebuild on a future Step-4 J3 retrain (Option B).
📁 **Status:** DONE (pure analysis, no data changed). **Open item:** OD-2 — an unexplained provenance timestamp on `2030_synthetic_diaries.csv` (Jul 9 21:07 vs Apr-23 training source), left non-blocking. **Source:** [`step6_improvement_notes.md`](../outputs_step6/improvement/step6_improvement_notes.md) (Improvement 1).

### Improvement 2 — Reconcile the canonical report with the actual 2030 population

🩺 **Diagnostic:** the shipped report (35/35 PASS) validated the **base** (un-act30-raked) 2030 diary, while a calibrated `2030_synthetic_diaries_joint_raked.csv` existed on disk but was never validated/shipped — meaning the "canonical" report described the wrong population. A separate 35-vs-37-check discrepancy (an earlier log claimed "37/37 PASS" on the joint-raked file) also needed settling before either number could be trusted, plus a doc path bug (`aug_pipeline/` vs the real `outputs_step4/`) and a missing §5.5 WFH check that the validation plan called for but the shipped validator never implemented.
🔧 **Fix:** built [`_validate_joint_raked_2030.py`](../outputs_step6/improvement/_validate_joint_raked_2030.py) (archive→swap→run→restore driver); confirmed §5.5 was genuinely never wired (grep of validator source, zero matches) — not hidden, just never built.
📊 **Before → After:** 35-vs-37 settled as **35/35 PASS, 0 WARN, 0 FAIL** (the "37/37" log claim does not reproduce and is treated as stale/unverified). §5 calibrated: AT_HOME 79.6959% (∈[55,90]); WD 78.4%<WE 80.3%; night-sleep 75.7948% (≥70%); max activity share 38.0003% (<60%); WD continuity Δ4.2099pp (≤15pp). Row count 37,008.
🩺 **Important caveat surfaced (why this needed a careful diagnostic, not just a swap):** the *archived* "base" report had actually already shown joint-raked-equivalent act30 values, a byproduct of `06_forecast_rake.py`'s own internal swap-run-restore leaving a stale report in place — meaning nobody has yet shipped a validated report of the *true* current base (un-raked) forecast. Flagged for the paper, out of scope to fix here.
📁 **Status:** DONE. Predecessor archived: [`previous/step6_validation_report_base_20260709.html`](../outputs_step6/previous/step6_validation_report_base_20260709.html). **Source:** [`step6_improvement_notes.md`](../outputs_step6/improvement/step6_improvement_notes.md) (Improvement 2).

### Improvement 3 — Figures over prose; re-derive progress-log-sourced sections

🩺 **Diagnostic:** report had 6 uncaptioned figures and no chart at all for §6 (BEM readiness); §1/§2 were transcribed from the progress log rather than re-derived from data — violating the project's own "verify claims from the artifact, not the log" rule ([[feedback_verify_progress_log_claims]]).
🔧 **Fix:** [`_gen_step6_plots.py`](../outputs_step6/improvement/_gen_step6_plots.py) captioned all 6 existing figures and added 4 new ones (F_S2 corrected per-stratum gate lines — the original wrongly drew only one gate line; F_S3 WD per-activity JS; F_S5 compact §5 panel; F_S6 §6's first-ever chart). §1/§2 explicitly labeled "log-sourced, not re-derived per-epoch" rather than faked, since no per-epoch training CSV was ever persisted.
🩺 **Load-bearing finding surfaced while building F_S3:** the validator computes `covid_signal_pp` internally but **never uses it in any printed check** — the shipped "0.2pp" (check 3.7) is actually a separate hardcoded constant, not derived from the drift matrices. Live re-derivation from the matrices gives a *different*, smaller COVID-window delta (−0.0168pp) — explicitly distinguished from the report's 0.2pp rather than conflated with it. This is a validator-hygiene gap that should be fixed before the number is cited as "derived."
🔧 **Addendum (same day) — activity-name relabeling:** [`_gen_step6_names.py`](../outputs_step6/improvement/_gen_step6_names.py) added a 14-row code↔name legend and relabeled 3 figures (S3, S7, F_S3) from bare `act30` codes to activity names — values unchanged, labels only.
📊 **Before → After:** figures 6 (0 captions) → 10 (10 captions), then held at 11 through the naming addendum.
📁 **Status:** DONE. Predecessors archived: [`previous/step6_validation_report_jointraked_prefig_20260710.html`](../outputs_step6/previous/step6_validation_report_jointraked_prefig_20260710.html), [`previous/step6_validation_report_prenames_20260710.html`](../outputs_step6/previous/step6_validation_report_prenames_20260710.html). **Source:** [`step6_improvement_notes.md`](../outputs_step6/improvement/step6_improvement_notes.md) (Improvement 3).

### Improvement 4 — One coherent, paper-ready disposition for the three documented deviations

🩺 **Diagnostic:** three existing deviations (§2 TFT Saturday JS 0.2040 vs 0.20 gate; §3 COVID gate redefinition; §4 weekend backcast re-baseline) had each been re-based separately with no unifying evidence trail — risking a "goalpost-moving" read from a reviewer if left as scattered, individually-justified exceptions.
🔧 **Fix (Option A — relabel + document, no re-thresholding):** [`_gen_step6_panel.py`](../outputs_step6/improvement/_gen_step6_panel.py) injected a disposition panel with a basis for each of the 3 deviations, plus a new **diagnostic (INFO, not a gate)** WFH figure in §5.
📊 **WFH numbers surfaced:** 2030 calibrated WD WFH rate = **4.2815%**; 2022 backcast = **4.7106%** (Δ=−0.4292pp).
🩺 **Follow-up verification (same day, read-only) — this is the key finding for the paper's WFH narrative:** AT_HOME occupancy (`hom30`) rise **confirmed** as the true telework carrier: WD mean AT_HOME rises **2022 observed 76.93% → 2030 calibrated 78.44% (+1.51pp)**. Meanwhile calibrated WFH-*activity* (`act30`) sits at/below the 2022 backcast — **not** because telework isn't growing, but because the `act30` joint-rake calibrates activity mix back to 2022-observed marginals while `hom30` is raked to the 2030 projection. **Design consequence for the paper: `hom30` keeps the 2030 drift; `act30` loses it — the 2030 telework story must be told through AT_HOME occupancy, not paid-work-at-home activity.** A related validator-hygiene issue was also found (not fixed here): §5.6/§4.4's reported deltas use a mixed observed+synthetic 2022 baseline rather than an `IS_SYNTHETIC==0`-filtered one; the gate still passes and the direction of the finding holds under either baseline, but the true observed→2030 rise is the smaller +1.51pp, not the report's stated 4.21pp.
📁 **Status:** DONE (reporting side). **Deferred:** Bundle 3.18 "Path A" (redefine the §4 weekend gate on observed-only rows) — explicitly gated on a future Step-4 J3 retrain. **Source:** [`step6_improvement_notes.md`](../outputs_step6/improvement/step6_improvement_notes.md) (Improvement 4).

### Step 6 — open/deferred items
- OD-2: unexplained base-forecast provenance timestamp.
- WFH hard gate: currently only a diagnostic/INFO figure, not promoted to a validator gate.
- Validator hygiene: wire `covid_signal_pp` into an actual check; fix §5.6/§4.4 to use an `IS_SYNTHETIC==0`-filtered 2022 baseline.
- Bundle 3.18 "Path A" — deferred to a future Step-4 J3 retrain.
- F1 true per-epoch training curve — blocked on persisting Model-2 training logs (currently cluster-only).
- Open design question (unresolved, worth flagging to the paper's methods discussion): should `act30`'s rake target be 2030-projected rather than 2022-observed marginals? This is the root cause of the WFH-in-activity vs WFH-in-occupancy split above.

---

## Step 7 — BEM integration validator

Working docs: [`outputs_step7/improvement/step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) · Handoffs: [`outputs_step7/prompt/step7_handoff_prompt.md`](../outputs_step7/prompt/step7_handoff_prompt.md), [`outputs_step7/prompt/step8_9_targeted_resim_LOCAL_prompt.md`](../outputs_step7/prompt/step8_9_targeted_resim_LOCAL_prompt.md) · Reports: [`step7_validation_report_2022_v2.html`](../outputs_step7/step7_validation_report_2022_v2.html), [`step7_validation_report_2030_v2.html`](../outputs_step7/step7_validation_report_2030_v2.html) · Archived predecessors: [`outputs_step7/previous/`](../outputs_step7/previous/)

All dated **2026-07-10**, triggered by the same Steps-4/5/6-refresh review as Step 6.

### Improvement 1 — Lineage / staleness check

🩺 **Diagnostic:** the two existing reports (internally dated 2026-06-01) described the pre-Step-9, 13-column BEM schema and referenced the base (non-joint) 2030 diary, while the actual `BEM_Schedules_{2022,2030}.csv` files had already been rebuilt (Jul-9) as 17-column, 2030 built with `--joint` — i.e. the *data* was current but the *validator/report* were ~5 weeks stale. Proved via the weekend metabolic channel: the live 2030 file (109.59 W) matched the joint-raked diary (109.49 W, gap 0.10 W), not the base diary (99.90 W, gap 9.69 W) — the occupancy channel alone couldn't have caught this since `hom30` is byte-identical between base/joint.
🔧 **Fix:** decision made to un-stale the validator + regenerate reports (no BEM recompute needed — data was already correct).
📁 **Status:** DONE. **Source:** [`step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) (Improvement 1).

### Improvement 2 — Un-stale the validator + regenerate both reports (core fix)

🩺 **Diagnostic:** three concrete validator bugs: (1) hardcoded 13-entry `OUT_COLS` against a live 17-col file → guaranteed hard-FAIL on check 1.1; (2) 2030 reference pointed at the base diary instead of `joint_raked`; (3) hardcoded `N_HH = 144,507`.
🩺 **Diagnostic — the frame-size discovery (the single most consequential Step-7 finding):** un-staling the validator first surfaced **5 new count-gate FAILs** (checks 1.2/1.3/5.2/5.4/5.5). Rather than assuming a validator bug, a targeted read of the actual `21CEN22GSS_aug_Full_Aggregated_excl.csv` confirmed **144,465 unique households / 285,367 persons**, down from 144,507/285,419 — a real, legitimate **−42 HH / −52 person** shrinkage from the Step-5 region-tier relink + joint rake + 5H exclusion refresh, *not* a validator defect. This distinction mattered because treating it as "just fix the validator's number" without confirming the population had genuinely shrunk could have masked a real upstream regression.
🔧 **Fix:** schema check updated 13→17 cols; 2030 reference switched to `2030_synthetic_diaries_joint_raked.csv`; `N_HH` corrected 144,507→**144,465** (and two other hardcoded strings); §6.2 re-based to a 13-col baseline file so the live 17-col file wouldn't spuriously FAIL there.
📊 **Before → After:** pass counts **2022: 29/0/0 → 34/0/0**; **2030: 28/0/0 → 33/0/0**. §3.3/§3.4 occupancy deltas 2022 Δ0.44/Δ0.144pp; 2030 (vs joint reference) Δ0.089/Δ0.049pp. §4 metabolic WE gap corrected from a spurious ~9.7 W (wrong reference) to ≈0.1 W (joint_raked reference).
📁 **Artifacts:** new reports written as [`step7_validation_report_2022_v2.html`](../outputs_step7/step7_validation_report_2022_v2.html) / [`step7_validation_report_2030_v2.html`](../outputs_step7/step7_validation_report_2030_v2.html); the two Jun-11 originals preserved in place (not overwritten), dated copies also archived to `previous/`. **Status:** DONE. **Source:** [`step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) (Improvement 2).

### Improvement 3 — Validate the Step-9 internal-gain channels (new Section 4b)

🩺 **Diagnostic:** four EnergyPlus-facing columns (`Equipment_Fraction`, `Lighting_Fraction`, `Equip_Design_W`, `Light_Design_W`) existed in the 17-col file and were asserted inline in `07_aug_to_bem.py`, but were **validated nowhere in the report** — a silent coverage gap for exactly the channels Step 9 depends on.
🔧 **Fix:** new §4b with 5 gates (fraction bounds, design-W ≥0, lighting evening-peak plausibility, equipment diurnal amplitude, design-W variance by dwelling type) + a 24h overlay figure.
📊 **Result:** all-PASS/INFO in both years' `_v2` reports (net-new coverage, not a re-threshold).
📁 **Status:** DONE. **Source:** [`step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) (Improvement 3).

### Improvement 4 — Figures + paper-ready deviation disposition

🩺 **Diagnostic:** figures lacked captions; five documented deviations (metabolic/activity un-calibrated, Sat/Sun pooled→Weekend, 70 W/MET basis, MATCH_TIER within-HH drift, classic-frame regression) were scattered across risk-register lines rather than one citable disposition.
🔧 **Fix:** caption dict added for all 7 figures; a "Documented deviations — disposition" panel with a one-line BEM-impact note per deviation, gate status kept visible.
📁 **Deferred:** optional metabolic conversion-factor sensitivity (×1.19/×1.5) — flagged as Methods-stage, not a validation gate. **Status:** DONE. **Source:** [`step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) (Improvement 4).

### Follow-up round — "00h peak" / `_clock` label bug fix

🩺 **Diagnostic:** §4b's lighting-peak gate reported the peak at 00h, implausible for an evening-lighting channel. Root cause: since a 2026-06-08 pipeline change already rolled BEM `Hour` values +4h into clock time, the validator still applied a now-stale `_clock(h) = (4+h) % 24` helper — **double-shifting** the true 20h peak down to 0h, and mislabeling §3/§4/§4b x-axes by +4h. This is a labeling-only bug (no gate ever flipped), but worth recording precisely because it's easy to mistake for a real physical anomaly.
🔧 **Fix:** removed the stale `_clock()` helper entirely; all three x-axes now read true clock hours.
📊 **Before → After:** §4b now reads "Lighting peak at 20h — PASS" in both years; total pass counts **unchanged** (2022 34/0/0, 2030 33/0/0) — cosmetic only.
📁 **Also in this round:** frame-propagation audit confirmed no live Step-8/9 code hardcodes the 144,465 HH count (all use `.nunique()`), so no false-FAIL risk from the frame shrinkage — but flagged that `BEM_Schedules_{2005,2010,2015}.csv` still sit on the old 144,507 frame while 2022/2030 are now on 144,465, an invariant break deferred to next-campaign prep and handed off via [`step8_9_targeted_resim_LOCAL_prompt.md`](../outputs_step7/prompt/step8_9_targeted_resim_LOCAL_prompt.md). `07_bemIntegrationGSS.md` doc updated to the new frame numbers; the two Jun-11 report originals restored to the root; [`step7_handoff_prompt.md`](../outputs_step7/prompt/step7_handoff_prompt.md) written for the next session.
**Status:** DONE (clock fix, doc alignment, handoff); frame-propagation itself remains open (picked up directly by Step 8, below). **Source:** [`step7_improvement_notes.md`](../outputs_step7/improvement/step7_improvement_notes.md) (Progress Log, "follow-up round" entry).

### Step 7 — open/deferred items (as of hand-off)
1. Regenerate `BEM_Schedules_{2005,2010,2015}.csv` on the 144,465 frame before any new EnergyPlus campaign.
2. Decide/execute Step-8/9 re-sim for 2022/2030 — **addressed by Step 8, Item 3 below.**
3. Doc-hygiene sweep of remaining 144,507 prose across the manuscript and pipeline docs.
4. Decision on promoting `_v2` reports to canonical filenames — left to the user, not auto-executed.
5. Optional metabolic ×1.19/×1.5 sensitivity — Methods-stage, non-blocking.
6. Step 7's own "metabolic un-calibrated" deviation-panel language needs correcting now that `act30` is confirmed joint-raked (surfaced later, in the Step 8/9 resim prompt's Task 0).

---

## Step 8 — BEM simulation campaign

Working docs: [`outputs_step8/investigation/`](../outputs_step8/investigation/) · [`outputs_step8/implementation-improvement/step8_2022_2030_resim_implementation.md`](../outputs_step8/implementation-improvement/step8_2022_2030_resim_implementation.md) · Canonical status doc (injection bug): [`Step8_docs/08_09_injection_bug_status.md`](../Step8_docs/08_09_injection_bug_status.md) · Fig review: [`Step8_docs/08-09_injection_bug/fig6_fig5_regen_review.md`](../Step8_docs/08-09_injection_bug/fig6_fig5_regen_review.md) · Reports: [`step8_validation_report_v3_section4_local.html`](../outputs_step8/step8_validation_report_v3_section4_local.html), [`step8_validation_report_v3_merged.html`](../outputs_step8/step8_validation_report_v3_merged.html)

### Item 1 — Residential heating/cooling dominance investigation

🩺 **Diagnostic:** §4's physical-plausibility report showed apartment (MidRise/HighRise) cooling energy rivaling or exceeding heating in cold Canadian climate zones (CZ 7A Winnipeg 2022: MidRise cooling/heating **3.36×**, HighRise **1.86×**) — physically implausible, and stable across all 5 campaign years, pointing to a static-input artifact rather than an occupancy effect. Existing gates 4.2/4.3 structurally **could not** catch this (4.2 only checks heating rises cold→warm; 4.3 only checks cooling >0.05) — a coverage gap that let it ship undetected.
🩺 **Diagnostic (hypothesis revised, not just patched):** initial hypothesis (frozen 24.0°C cooling setpoint in NECB apartment templates) was **experimentally falsified** by a sibling investigation (raising the setpoint 24→28→40°C left winter cooling energy unchanged). True root cause: `Cooling:EnergyTransfer` sums *any* air-system sensible cooling, and every apartment zone has a thermostat-independent ERV (heat-recovery ventilator) whose post-recovery supply air reads below room temperature in winter — metered as "cooling" at **zero electricity**. Houses have no per-zone ventilation air system, which is why they looked clean by comparison.
🔧 **Consequence:** the planned 3,000-run 2J re-simulation was **cancelled** — all 6,000 existing runs remain valid; the setpoint hypothesis retired; the single-envelope-per-climate-zone limitation kept only as a paper caveat.
📁 **Status:** DONE/closed — feeds directly into Item 2. **Source:** [`step8_resid_heating_cooling_dominance_investigation.md`](../outputs_step8/investigation/step8_resid_heating_cooling_dominance_investigation.md), 2026-07-07→08.

### Item 2 — End-use metric re-base (validator gates 4.9/4.10)

🩺 **Diagnostic:** because §4's heating/cooling split was read off the `:EnergyTransfer` meter (the ERV-ventilation artifact from Item 1), the report's dominance signal was misleading and no gate could ever FAIL a true dominance problem — this needed fixing so the paper's end-use claims rest on the right meter, not an artifact.
🔧 **Fix:** ported 3J's end-use extractors; pulled a 600-file 2022 subset from cluster scratch (zero sbatch, login-node file transfer only, since cluster compute was blocked ~2 weeks); added **gate 4.9** (cooling-elec/heating-fuel dominance, FAIL >2.0× in 7A / WARN >1.25× in 6A/6B/7A — now *can* actually FAIL); **gate 4.10** (INFO end-use table); relabeled (not removed) the ET-based gates/chart as "air-system delivered sensible energy (incl. ventilation air)."
📊 **Before → After:** every archetype×climate-zone cell measured **≤0.40×** cooling/heating — well under both thresholds. Scorecard moved **24→25 PASS, 3→4 INFO, 0 WARN/0 FAIL** (verified: 25 Checks Passed / 0 Warnings / 4 Info / 0 Failures / 100%).
📁 **Artifacts:** canonical `step8_validation_report.html` **deliberately never overwritten** (md5-verified unchanged); new `step8_validation_report_v3_section4_local.html` (§4-only) and `step8_validation_report_v3_merged.html` (full) instead. Two follow-on UX-only fixes same day (caption clarity distinguishing the artifact chart from the "cite this one" chart; palette recolor to avoid clashing with the heating=red/cooling=blue convention) — neither changed the scorecard.
**Status:** DONE/CLOSED. Only the full-campaign canonical regen (all 6,000 runs) remains deferred until cluster compute returns. **Source:** [`step8_enduse_rebase_implementation_plan.md`](../outputs_step8/investigation/step8_enduse_rebase_implementation_plan.md), [`step8_enduse_rebase_employee_prompt.md`](../outputs_step8/investigation/step8_enduse_rebase_employee_prompt.md), 2026-07-08.

### Item 3 — Step-8 2022/2030 targeted local re-simulation

🩺 **Diagnostic:** the Step-7 frame-size fix (144,507→144,465 HH, 1.2% household-ID churn) made the existing Step-8 campaign (job 953111, 24/24 PASS) **stale for 2022/2030 only** — 2005/2010/2015 untouched. This is the direct downstream consequence of Step 7's open item #2.
🩺 **Diagnostic (3 real bugs found while re-running, not just "click re-run"):**
1. **Manifest-clobbering risk** — a fresh 2022/2030 sampling run would overwrite the shared `cell_manifest.csv`, mislabeling old 2005/2010/2015 sample folders.
2. **Resume-skip false-positive** — no `--years` flag existed, so restricting to 2022/2030 would misdetect all cells as "already done."
3. **Concurrent-cell memory blowup** — default `--workers 18` loaded 18× ~3.7GB schedule sets simultaneously, tripping an 80% memory watchdog within ~3 minutes (attempt 1: 0/24 cells completed).
🔧 **Fix:** archived (not deleted) `cell_manifest.csv` per cell before aggregation; added `--years` CLI passthrough with recomputed expected-count logic; relaunched with `--workers 1 --ep-workers 18` (one cell's schedules in RAM at a time).
📊 **Before → After:** attempt 1: 0/24 cells, killed at 80.4% committed memory (~3 min). Attempt 2: **24/24 cells ok, 0 failures across 2,400 EnergyPlus runs**, ≈20.96h wall-clock.
📁 **Status:** Step-8 re-sim DONE; Step-9 full re-sim campaign launched same round (see Step 9 below); re-aggregate/re-validate and doc-frame-propagation **not started** at the time this doc was written (later completed — see Item 4/5 and Step 9). **Source:** [`step8_2022_2030_resim_implementation.md`](../outputs_step8/implementation-improvement/step8_2022_2030_resim_implementation.md), 2026-07-10→11.

### Item 4 — Multi-zone equipment/lighting injection bug ("Bug A") + HighRise investigation ("Bug B")

🩺 **Diagnostic (Bug A):** discovered while updating manuscript figures — Figure S8 showed an implausible ~13h stock-weighted peak hour vs. the manuscript's claimed stable ~17.5–17.7h. Root cause in `Step8_docs/eSim_bem_utils_2J/integration.py`: for multi-zone apartment archetypes (MidRise, HighRise, OtherDwelling), the Step-9 SHEU-calibrated equipment/lighting "carrier" was injected into **only the occupancy zone**, while legacy objects were neutralized across **all** zones — collapsing whole-building equipment/lighting electricity to roughly 1/N_units of its true value (measured ~37–99×, depending on archetype). SingleD (single-zone) was unaffected. This is a serious bug because it silently under-counts electricity for exactly the archetypes with the most units, i.e. the ones that matter most for aggregate/stock-level claims.
🔧 **Fix:** replicated the SHEU carrier across every zone that had a legacy object neutralized, falling back to the occupancy zone only if that set is empty (preserves SingleD behavior). Verified on a 5-household test batch: MidRise circular-mean peak hour corrected to 16.72h (matches the 17.5–17.7h band).
🩺 **Diagnostic ("Bug B" — investigated and resolved as NOT a bug):** HighRise still showed 11.72h post-fix, looking like a second defect. Traced the suspect 94.70 GJ/yr electric-heating component to a legitimate Water-Loop Heat Pump design (gas boiler + electric backup) — physically normal, and it didn't track the morning-skew window at all. The true driver was that the *specific sampled household* genuinely has a morning-leaning schedule from Step 4/7 — the fix correctly replicated that household's real schedule. A second household in the same cell showed a normal 16.78h peak, confirming ordinary Monte Carlo sampling variance rather than a systemic defect. This distinction (real household-level variance vs. a systemic bug) had to be established with a full 50-household test before it could be trusted, not just asserted.
📊 **Full validation:** 50-household HighRise×Calgary_6B, 2022-only — 50/50 runs completed, 0 failed; stock-level circular mean **17.32h** (within the 17.5–17.7h claimed band). OtherDwelling spot-check also passed (magnitude restored exactly 7.00× matching its 7-zone count).
🔧 **Full re-sim executed:** 18 cells (MidRise+HighRise+OtherDwelling × 6 cities) × 2 years = 36 cell-years, 1,800 EnergyPlus jobs. A backup was taken first (128.98 GB). One verification run hit an operational incident (an accidental duplicate process launch from a false external "finished" status, corrupting 12/100 files) — fully diagnosed and repaired (12/12 re-run, 0/0 errors) before the full campaign proceeded.
📊 **Result:** **18/18 cells, 1,800/1,800 EnergyPlus jobs ok, re-aggregation 6,000/6,000 runs ok, 0 missing/short.**
🔧 **Downstream reconciliation (all DONE):** Table 5 re-derived, Figure S8 (dual-metric fix) + Figure S9 refreshed, `readySubmission.docx` regenerated via pandoc (0 warnings, both runs exit 0), manuscript §5.2/Table 5/§5.3 updated (peak-hour claim corrected to 17.0–17.7h band), a new WFH/AT_HOME calibration-provenance caveat added to §7 Limitations.
📁 **Status: RESOLVED / DECISION GATE FULLY CLOSED (2026-07-15).** Every checklist item in the canonical status doc's §6 is checked, ending "The Bug-A closeout investigation is complete." **This corrects the prior memory note** that said "HighRise still broken, under investigation" — that is now stale; both MidRise and HighRise are fixed and validated. **Source:** [`Step8_docs/08_09_injection_bug_status.md`](../Step8_docs/08_09_injection_bug_status.md) (canonical, 496 lines), 2026-07-13→15.

### Item 5 — Figure 6 / Figure 5 regeneration review ("Task #21")

🩺 **Diagnostic:** needed to check whether Figures 5/6 (which had been reverted to pre-fix versions on 2026-07-13 as a blanket precaution against Bug A) actually needed rebuilding from the corrected campaign. Found Figure 5's source sits entirely upstream of Bug A (never actually wrong, reverted only out of caution) — but rebuilding Figure 6 surfaced a **real style regression**: the corrected campaign's source PNGs now carry a bold baked-in title header the old published figure doesn't have, which a naive mechanical rebuild would have silently shipped as visual clutter.
🔧 **Fix:** flagged via a side-by-side preview (3 resolution options) rather than silently shipping the regression; user chose "strip titles"; applied via a monkeypatch script (scratchpad-only, not committed to production plotting code) that no-ops the title call only for the 3 relevant plot calls.
📁 **Status:** DONE, applied 2026-07-15. **Source:** [`Step8_docs/08-09_injection_bug/fig6_fig5_regen_review.md`](../Step8_docs/08-09_injection_bug/fig6_fig5_regen_review.md).

### Step 8 — open/deferred items
- Full-campaign canonical §4 end-use regen (all 6,000 runs, Item 2) — deferred until cluster compute returns; still not started as of the source docs.
- Single-envelope-per-climate-zone limitation (Item 1, "Mechanism B") — kept as a paper caveat only, not fixed.

---

## Step 9 — Activity-driven loads validation

⚠️ **Two distinct Step-9 pipelines exist and both matter for the paper — do not conflate their numbers:**
- **Thread A — 2J single-channel Step 9** ([`Step9_docs/`](../Step9_docs/), report: [`outputs_step9/step9_validation_report.html`](../outputs_step9/step9_validation_report.html)) — residential-only, current scorecard 6P/1W/3I/0F.
- **Thread B — 3J Leg-2 bi-channel Step 9** (`3J_docs_occ_nTemp/Leg2_2-split/Step9_docs/`, report `step9_report.html`) — residential + office/WFH, this is where **G8o**, the office EUI 172.6 vs bands 135(PNNL)/230(SCIEU), and the +0.54%/−0.01%/−0.33% energy deltas actually live; current scorecard 10P/1W/0F.

### Thread A1 — Initial WARN/INFO investigation (diagnostic only)

🩺 **Diagnostic:** a user review of the report questioned the WARN/INFO gate lines, a "default vs Step-9" magnitude gap, and the lighting mechanism. Investigation found: **G3 sleep-floor WARN** root-caused to the GSS diary starting at 04:00 — simulation hours labelled "sleep" by the validator actually correspond to real clock 06:00–09:59 (breakfast + dishwasher), not true sleep; **the "h14 peak" headline** decomposed to dishwasher-queue (38%) + cooking (25%) dominating, not the dryer (9.7%) — diary h14 = real clock 18:00 (dinner), matching literature, not "early afternoon" as the SI implied; **lighting** confirmed as a binary "someone home & awake" flag with no daylight gate, contradicting the SI's claimed daylight-gate mechanism.
📁 **Recommendation explicitly NOT taken here:** applying the −4h offset correction directly (OC3) was **recommended against** in this pass — flagged as high-risk (would require re-simulating ~4,800 runs) pending explicit go-ahead. **Status:** OPEN at close of this entry. **Source:** [`Step9_docs/investigation/step9_investigation.md`](../Step9_docs/investigation/step9_investigation.md), 2026-06-08.

### Thread A2 — Manager escalation: the offset is a REAL injection bug, not a labeling issue

🩺 **Diagnostic (supersedes A1's initial "benign" read):** `07_aug_to_bem.py` reshaped the 48-slot diary **positionally** instead of resampling by real clock hour. Since diary slot 1 = 04:00, this dropped the +4h rotation entirely — occupancy, metabolic rate, equipment, and lighting were all injected **4 real clock hours early relative to the EPW weather clock**, verified via [`offset_check.py`](../Step9_docs/investigation/offset_check.py) (clean +4h circular shift, SSE 0.04305→0.00744 at roll+4). Annual EUI/SHEU totals are phase-invariant (why prior sanity checks had passed) but **all timing claims were corrupted**, including the report's own −4h peak-shift headline and the G3 "sleep-hour" WARN (which was really morning activity). [`year_clock_check.py`](../Step9_docs/investigation/year_clock_check.py) found all 5 census years affected, including 2005/2010/2015 which don't even go through `07_aug_to_bem.py` — independently stale by the same +4h.
🔧 **Fix:** `07_aug_to_bem.py` rolled the injected arrays +4h (predecessor archived as `archive/07_aug_to_bem.BUGGY_20260608.py`); [`fix_old_years_clock.py`](../Step9_docs/investigation/fix_old_years_clock.py) relabeled `Hour` on the three older-year BEM files (data unchanged, label corrected only). Full re-simulation approved for Step 8 (~6,000 runs) + Step 9 (~4,800 runs).
📁 **Status:** DONE — this explicitly supersedes A1's earlier "benign, document only" verdict. **Source:** memory `project_step9_injection_offset_bug.md`; scripts above, 2026-06-08.

### Thread A3 — Corrected re-run

🩺 **Diagnostic:** needed a full corrected campaign to replace the buggy one, plus verification the fix actually worked and didn't regress anything else.
🔧 **Fix:** archived the buggy run (`step9_run_BUGGY_20260608`), regenerated corrected `BEM_Schedules_{2022,2030}.csv` + 9,600 IDFs, re-ran the full 4,800-run Step-9 array.
📊 **Before → After:** peak shift **−4h (all cells/years) → 0±1h** building-level; SHEU gate held **48/48 PASS** both before and after (phase-invariant); sleep-floor WARN improved (buggy ~600–790 Wh → corrected 426–505 Wh building-total, WARN persists but lower, consistent with now sampling true sleep hours). Zone-level equip_zone_shift (−17h HighRise/MidRise) confirmed **unchanged** — a known, non-fixable fridge-dominance artifact at the zone-meter level, unrelated to the clock bug.
📁 **Status:** "Step 9 corrected campaign: COMPLETE" (2026-06-10). Not independently confirmed: whether `si_appendix_step9.md`'s prose was updated to match — see verification below. **Source:** `Step9_docs/cluster_run.md`.

**✅ Verification (added during this changelog compilation):** [`Step9_docs/si_appendix_step9.md`](../Step9_docs/si_appendix_step9.md) (last modified 2026-06-11) was checked directly — all four redline recommendations (R1 lighting mechanism, R2 sleep-floor WARN reframed as "expected multi-unit refrigerator sum, NOT a calibration error," R3 h14→real-clock-18h/evening-peak reframing, R4 gross/net energy clarification) **are correctly reflected** in the current SI text. No stale claims remain.

### Thread A4 — Targeted 2022/2030 local re-sim (frame-size propagation)

🩺 **Diagnostic:** the Step-7 frame-size fix (144,507→144,465 HH) required Step 9's 2022/2030 outputs to be re-simulated against the corrected household frame — a direct, confirmed cross-step dependency.
🔧 **Fix:** built a **local** Step-9 driver from scratch (previously cluster/Singularity-only); ran 4,800/4,800 jobs locally; re-aggregated and re-validated. Fixed a paired-sampling gotcha: 2022/2030 drew an independent 50-HH/cell sample (not the same households as 2005-2015), causing HH-ID collisions — fixed by keying the aggregator by the **(sample, hh_id) tuple** instead of hh_id alone.
📊 **Result:** all gates PASS; this run **is** the data behind the current published report — scorecard **PASS 6 / WARN 1 / INFO 3 / FAIL 0**, G2a max|pct_equip|=0.51%, G2b max|pct_light|=1.10%.
📁 **Status:** DONE 2026-07-13. HTML re-rendered cosmetically 2026-07-15 but built from the 2026-07-13 CSVs. **Source:** memory `project_2j_step89_resim.md`; `Step9_docs/{cluster_run_results,loadshape_profiles,peak_hours,peak_shift_summary}.csv`.

### Thread A5 — ⚠️ OPEN exposure gap: does Step 9's own campaign carry the multi-zone injection bug ("Bug A")?

🩺 **Diagnostic:** Bug A (Step 8, Item 4 above) was found in `Step8_docs/eSim_bem_utils_2J/integration.py` on 2026-07-13, the same day as Thread A4's re-sim. Both Step 8's 24-cell campaign and Step 9's separate local 4,800-run campaign build IDFs for the same multi-zone archetypes — so it needed checking whether Step 9's own campaign shares the defective code path.
**✅ Verification (added during this changelog compilation):** the canonical [`Step8_docs/08_09_injection_bug_status.md`](../Step8_docs/08_09_injection_bug_status.md) was read in full. It states explicitly (Progress Log, Task #20): **`step9_loadshape_aggregate.py`/`step9_validate_full.py` were found NOT runnable against the corrected campaign** — the only directory matching their expected layout (`BEM_Setup/SimResults_Step9/campaign_N50_2022_2030/idfs/`) is dated **2026-07-12 05:44**, which **predates Bug A's discovery (07-13) and the Phase-5 corrected re-sim entirely**. The doc's scope throughout is explicitly limited to the Step-8 24-cell campaign; **Step 9's separate local campaign was never re-simulated as part of the Bug-A closeout** and remains structurally incompatible with the Step-8 re-sim workflow.
🚩 **This means: the currently published `outputs_step9/step9_validation_report.html` (Thread A4, dated 2026-07-13 — the same day Bug A was found) has NOT been confirmed clean of Bug A.** Circumstantial evidence is reassuring (SHEU gate deviations are tiny, 0.51%/1.10%, which would likely be grossly violated by a ~37–99× magnitude collapse) but this is inference, not direct verification.
📁 **Status: OPEN — recommend explicitly checking Step 9's own IDF-generation code (`step9_idf_gen_full.py` / `Step9_docs/eSim_bem_utils_2J` if it has its own copy vs. sharing Step 8's `integration.py`) before citing the current Step-9 report as Bug-A-clean in the paper.** This is the one unresolved item in the whole Step 4–9 changelog. **Source:** [`Step8_docs/08_09_injection_bug_status.md`](../Step8_docs/08_09_injection_bug_status.md).

### Thread B1 — 3J bi-channel Step 9 initial build

🩺 **Diagnostic:** built to give the office channel parity with the deep residential model; found the office channel was **annual-degenerate** — `occ_mean_persons` was the NECB design density (not simulated), and annual energy was identical across all 7 WFH scenarios. Root cause traced to the office WFH People-schedule never actually being wired into the IDFs (a Step-8 bug).
📁 **Status:** diagnostic → feeds directly into B2. **Source:** memory `project_step9_2split_status.md`, 2026-07-01.

### Thread B2 — Office WFH-bug fix + office EUI gate + G8o build

🩺 **Diagnostic:** confirmed fix needed by checking that re-simmed IDFs now produce 7 distinct output checksums (they didn't before) with a monotone occupant-hour spread across WFH scenarios.
🔧 **Fix:** office re-sim fixed and re-run (job 1058490); added `evaluate_gates()` with 11 bi-channel gates including **G8o** ("office 2030 bands DIFFER" — the fixed-bug gate); job 1054800 defined `OFFICE_EUI_BAND=(135,100,200)` (NECB/PNNL, pass criterion) and `OFFICE_EUI_EMPIRICAL=(230,170,360)` (SCIEU, INFO context).
📊 **Result (job 1058662):** scorecard **PASS 10 / WARN 1 / INFO 0 / FAIL 0**. Office EUI = **172.6** kWh/m² vs bands 135/230. Energy-response deltas across 2030 WFH scenarios: **+0.54% / −0.01% / −0.33%** (damped, HVAC/plug-baseload dominated) — the real WFH signal lives in occupancy/peak-shape (office occupancy +5.41%/+2.55%/+0.65%), not annual energy.
📁 **Status:** DONE. **Source:** memory `project_step8_office_wfh_bug.md`, `project_step9_2split_status.md`, 2026-07-02.

### Thread B3 — Report clarity/parity improvement round (13 tasks)

🩺 **Diagnostic (Task 12):** residential lights/equipment archetype panels were empty — root-caused to the Step-8 aggregator only ever persisting hourly-shape rows for `Electricity:Facility`, never per-end-use meters (a deliberate original scoping decision, never revisited until this task asked for the split).
🔧 **Fix:** added a loop over `(M_LIGHTS, M_EQUIP)`; re-agg job 1067688, Step-8 validator re-confirmed 46P/1W/13I/0F (no regression); Step-9 regen job 1067730, scorecard unchanged 10P/1W/0F, G8o still PASS.
🩺 **Diagnostic (Task 13):** residential `occ_mean`/`occ_pct_vs_2022` were NaN for every row — no occupant-count E+ output variable had ever been requested for residential runs.
🔧 **Fix (user-chosen "Option 1"):** derive 2022/2030 occupancy from input schedules × HHSIZE; leave 2005/2010/2015 explicitly NaN rather than report a partial-survivor mean (only 11.7% of historical households had matched schedules — treated as a data-integrity issue, not just a gap). Verified via job 1068096, Step-8 scorecard still 46P/1W/13I/0F.
📁 **Status:** all 13 tasks CLOSED, scorecard held steady at 10P/1W/0F throughout, zero regressions across every job in this round. **Source:** `3J_docs_occ_nTemp/Leg2_2-split/Step9_docs/outputs_step9/step9_report_improvements_TASKS.md`, 2026-07-05→06.

### Step 9 — open/deferred items
- **🚩 Highest-priority open item across the whole log:** confirm whether Step 9's own local IDF-generation pipeline shares Bug A (Thread A5) — not yet verified either way.
- 2005/2010/2015 `BEM_Schedules` files still on the old 144,507 frame (shared with Step 7/8's open item).

---

## Cross-step dependency map

| Root cause | Where found | Steps affected | Resolution status |
|---|---|---|---|
| 2005 `PR` census-linkage disjointness | Step 4 (Task A) | 4, 5, 6, 7, 8, 9 (population-wide) | ✅ Closed 2026-07-09 |
| Un-raked `act30`/`cop30` (activity/co-presence) | Step 4 (Task B) | 4, 5, 6 (act30 rake target design question still open) | ✅ Closed 2026-07-09; open design question in Step 6 |
| Region-tier relink + joint rake + 5H exclusion → frame shrinkage (144,507→144,465 HH) | Step 7 (Improvement 2) | 7 (found), 8 (re-sim'd), 9 (re-sim'd) | ✅ Closed for 2022/2030; 2005/2010/2015 files still on old frame (open) |
| 4-hour diary/clock injection offset | Step 9 (Thread A2) | 8 (5 census years), 9 | ✅ Resolved/closed 2026-06-10 |
| Multi-zone equipment/lighting injection bug ("Bug A") | Step 8 (Item 4) | 8 (confirmed fixed), 9 (Thread A — **unconfirmed**) | ⚠️ Closed for Step 8; **open exposure question for Step 9** |
| Office WFH People-schedule never wired | 3J Step 8/9 (Thread B) | 3J Step 8, 3J Step 9 (G8o) | ✅ Resolved 2026-07-02 |
| `_clock()` label bug (+4h double-shift) | Step 7 (follow-up round) | 7 only (cosmetic, no gate change) | ✅ Fixed 2026-07-10 |

---

## Master open / deferred items list

1. **[Step 9 — HIGH PRIORITY]** Confirm whether Step 9's own local campaign shares Bug A (the multi-zone injection bug); the current published report has not been directly verified clean.
2. **[Step 7/8]** Regenerate `BEM_Schedules_{2005,2010,2015}.csv` on the 144,465 frame before any new EnergyPlus campaign that mixes historical + 2022/2030 years.
3. **[Manuscript]** Doc-hygiene sweep of remaining 144,507→144,465 prose across `writing/2J_full_manuscript.md`, `readySubmission.md`, `2nd_Occ_Journal_Skeleton.md`, and pipeline docs.
4. **[Step 6]** Promote the WFH diagnostic figure to a hard validator gate (currently INFO-only); resolve whether `act30`'s rake target should be 2030-projected rather than 2022-observed marginals.
5. **[Step 6]** Wire `covid_signal_pp` into an actual printed check; fix §5.6/§4.4 to use an `IS_SYNTHETIC==0`-filtered 2022 baseline.
6. **[Step 6]** Bundle 3.18 "Path A" (redefine the §4 weekend backcast gate on observed-only rows) — gated on a future Step-4 J3 retrain.
7. **[Step 5]** Option A (recalibrate gate thresholds) and Option C (J3 retrain with an `L_trans` transition-rate penalty) — both documented alternatives, neither implemented.
8. **[Step 5]** F3/F7 figures deferred; a `previous/` folder file-location discrepancy noted for a quick check.
9. **[Step 4]** Section-7 2005 bar's residual under-performance (13.41% vs. the other cycles' 21%+ cluster) — flagged as a possible follow-up investigation.
10. **[Step 8]** Full-campaign canonical §4 end-use regen (all 6,000 runs) — deferred until cluster compute returns.
11. **[Step 7]** Optional metabolic ×1.19/×1.5 conversion-factor sensitivity — Methods-stage, non-blocking.

---

## Chronological timeline (all steps)

- **2026-05-12** — Step 5 baseline FAIL diagnosis (`step5_fails.md`).
- **2026-06-01** — Step 5 warnings investigation + validator fixes (Groups A–D).
- **2026-06-08** — Step 9 Thread A1 (initial WARN/INFO investigation) → Thread A2 (4-hour injection bug found and fixed) same day.
- **2026-06-10** — Step 9 corrected campaign complete (Thread A3).
- **2026-07-01 → 2026-07-02** — 3J Step 9 bi-channel build + office WFH-bug fix (Thread B1/B2).
- **2026-07-05 → 2026-07-06** — 3J Step 9 report improvement round, 13 tasks (Thread B3).
- **2026-07-07 → 2026-07-08** — Step 8 heating/cooling dominance investigation + end-use metric re-base (Items 1–2).
- **2026-07-09** — Step 4 Tasks A/B/C/D + Remediation (region-tier linkage, joint rake, report figures, stale-chart fix) — the single busiest day in this log.
- **2026-07-10** — Step 5 Improvements 1–3 (report reconciliation, figures, gate reframing); Step 6 Improvements 1–4; Step 7 Improvements 1–4 + follow-up clock-bug round; Step 8 Item 3 begins (targeted re-sim).
- **2026-07-11** — Step 8 Item 3 re-sim completes (~13:10); Step 9 local campaign launched.
- **2026-07-13** — Step 9 Thread A4 (targeted 2022/2030 re-sim) completes; Bug A (multi-zone injection bug) discovered same day.
- **2026-07-14 → 2026-07-15** — Bug A full 18-cell re-sim, downstream reconciliation, `readySubmission.docx` regen, Figure 5/6 review — decision gate fully closed 2026-07-15.

---

*This document is additive: when a new improvement round lands on any step, append a new entry under that step's section (don't rewrite prior entries) and add one row to the Quick index / timeline / open-items list as needed.*
