# Step-4 Improvements — Confirmation Memo (Phase 1)

**Director session · 2026-07-09 · read-only review**
Sources verified: `step4_validation_report_v5.html` (text-stripped, §2/§3/§6/§7/§9, both note boxes, Known Limitations), `05_postlink_rake.py`, `activity_loads.py`, `07_aug_to_bem.py`, `05_census_linkage.py`, `02_harmonizeGSS.py`, `04F_validation.py`, `05_censusLinkageGSS_val.py`, `06_forecast_rake.py`, `step4_Speed_Cluster/04L_joint_rake_test.py`, `_gen_v5_plots.py`.

## Verdicts at a glance

| # | Improvement | Verdict | Priority |
|---|---|---|---|
| 1 | Joint 3-head calibration (act30 + hom30 + cop30) | **ADJUST** (real & sound; two mechanism claims corrected; OD-1..4 resolved) | P2 — after #2 |
| 2 | 2005 `PR` census-linkage gap | **CONFIRM** (Option A; OD-2 resolved YES) | **P1 — do first** |
| 3 | Visualize key findings in the report | **CONFIRM** (all 3 core figures; alongside-tables) | P3 — render last |

## Key-number verification (all checked against report/code)

| Claim (director prompt) | Verified | Where |
|---|---|---|
| 2005: supply 30.0% → Tier-1 expected 0.0% → matched ~9.0% | ✅ exact (57,663 diaries; 11,514 matched; 55.1% of agents fall past Tier-1) | report §9.1 |
| Metabolic gap +1.9% (+2.1 W/person, peak 10.5 W ~22:00) | ✅ | report §"raking all three" |
| Equipment shape mean \|Δ\| 14.9%, peak 32% ~08:30 | ✅ | same |
| Lighting 3.8 pp, peak 10.7 pp ~17:00 | ✅ | same |
| Annual kWh SHEU-fixed, only shape moves | ✅ mechanism confirmed in code | `activity_loads.py:225-254` (`calibrate_schedules` rescales design-W to per-DTYPE SHEU annual target; fractions peak-normalized) |
| Gate 6.2 = 3.27 pp expected-FAIL; activity JS 0.0191 PASS | ✅ | report summary + §6; JS gate `04F_validation.py:118` |
| Spouse marginal 2.23 pp PASS; raw per-cell-slot COP max 19.85 pp; coherence ~1.8–2.1% | ✅ (1.82% 2022 / 2.07% 2030) | report Known Limitations |
| Baseline 21 PASS / 1 WARN / 0 FAIL | ✅ (the 1 WARN = 6.2 expected-FAIL) | report header |

**Minor discrepancies found (flag, not blockers):**
- **286,540 vs 286,537 agents** — notes/`05_census_linkage.py` docstring say 286,540; the §9 reproduction, `05_postlink_rake.py:34` (`EXPECTED_ROWS = 286_537`) and the `Aligned_Census_2022.csv` count say 286,537. Standardize on **286,537** in new docs (285,419 after the 1,118 `_excl` exclusions — internally consistent).
- **LFTAG coding conflict** — `02_harmonizeGSS.py` maps LFTAG to **{1,2,3}**, but `04F_validation.py:470-473` and the report reference **LFTAG=5** (NILF). If the data really is {1,2,3}, the 04F "Employed > NILF" sub-check selects an empty NILF frame (vacuous), and the notes' "LFTAG=1 ≫ LFTAG=5" phrasing is stale HETUS convention. **Must be verified as Step 0 of Improvement 1** — it changes the rake cell count (3×48×3 vs ×5) and fixes a latent validator bug either way.

---

## Improvement 1 — Joint 3-head calibration — **ADJUST**

**(a) Problem real?** YES. `05_postlink_rake.py` rakes `hom30` only (plus a *dormant* conditional `Spouse30` rake, skipped because 6.3 passes at 2.23 pp ≤ 3 pp — so "hom30-only" is accurate in effect). The act30 marginal error is real: paid-work over-fires 13.3% → 25.6% (+12.3 pp, report). The BEM exposure is exactly as claimed: equipment/lighting **shape only** (SHEU pins levels), metabolic small. One extra supporting fact from code: `activity_loads.compute_48slot_loads` keys every equipment/lighting trigger on `(act30, hom30>0)` **jointly** (`activity_loads.py:144-169`), so coherence errors (home-activity under `hom30=0`) directly *suppress* device triggers — reducing coherence cost has a first-order BEM shape benefit, strengthening the case for a joint (not independent) rake. `Metabolic_Rate` maps act30→W unconditionally (`07_aug_to_bem.py:98`).

**(b) Scope corrections (the ADJUST):**
1. **Gate 6.2 is not LFTAG-conditioned.** `05_censusLinkageGSS_val.py:674-698` defines 6.2 as *top-5 aggregate activity share ≤ ±2 pp* (Work drives the 3.27 pp). Any per-(stratum×slot) act30 marginal rake closes it — LFTAG conditioning is **not required to flip the gate**. Keep LFTAG conditioning as a *fidelity* goal (Section-6 per-group chart; prevents fixing the aggregate while leaving employed/NILF miscalibrated), but decouple the claim in the notes.
2. **A literal 3-way IPF is not well-posed as written.** Co-presence is **9 parallel binary channels** (Alone…colleagues), not one categorical axis — there is no clean (14-act × 2-home × 9-cop) contingency table. 04L's proven design treats COP channels as standalone per-slot binaries. The "joint" aim is correctly achieved by a **conditional factorization** rake: hom30 exact (as now) → act30 raked **within home-status groups** (`act|hom=1` and `act|hom=0` separately) → COP channels minimal-flip standalone (04L machinery). Conditioning act on hom makes coherence reduction *structural* (no home-activity can be assigned under hom=0), satisfying the explicit sub-goal of driving coherence below 1.8–2.1%.
3. New engineering is the **categorical minimal-flip** for 14-way act30 (existing `_rake_binary_slot` is binary-only). Everything else reuses proven parts.
4. Must be **mirrored in the 2030 path** (`06_forecast_rake.py` projects/rakes hom30 only; `07_aug_to_bem.assemble_2030` draws from the raked 2030 diaries). Otherwise 2030 BEM schedules keep uncalibrated act30 and the 2030 coherence cost (2.07%) stays.

**(c) Approach — recommend Option A, implemented as the conditional factorization above** (mathematically a joint scheme; avoids IPF convergence issues in sparse cells; 100% reuse of the boundary-preferred minimal-flip machinery proven in 04L/05/06). Option B (independent sequential + repair pass) rejected: repair pass re-breaks marginals it repairs, no convergence guarantee.

**(d) Priority/dependencies:** P2 — **after Improvement 2**, because the rake computes targets on the *linked* population; re-linking afterwards would force a full re-rake. Independent of Improvement 3.

**(e) Open Decisions — resolved on evidence:**
- **OD-1 → Option A** (conditional-factorization joint rake), per (b)2/(c).
- **OD-2 → keep minimal-flip, boundary-preferred, seed 42** (proven transition-friendly); add a transition-matrix-drift diagnostic (report-only, no gate) to quantify the trade-off instead of guessing it.
- **OD-3 → hold day-type composition**: keep DDAY_STRATA as a conditioning dimension exactly as today — composition is held by construction; the 4.48 pp reporting artefact stays documented, unchanged.
- **OD-4 → YES, add LFTAG to the act30 rake dimension, gated by a sparsity guard**: rake per (stratum × slot × LFTAG) only where the observed cell has ≥30 diaries; below that, fall back to (stratum × slot). Precondition: the Step-0 LFTAG-cardinality check above.
- *(new, resolved by recommendation)* 2030 act30 targets: use **2022 observed marginals** (no trend extrapolation for a 14-way composition; hom30 keeps its OLS projection as today). Conservative, defensible, revisit only if Step-6 gates object.

---

## Improvement 2 — 2005 `PR` census-linkage gap — **CONFIRM**

**(a) Problem real?** YES, unambiguous. `02_harmonizeGSS.py:98-100` — `recode_pr` is a deliberate no-op: *"No remap needed. 2005 stays as REGION (1-5), others as PRV (10-59)"* (the comment is wrong about "no remap needed"; it's the root cause). `05_census_linkage.py:57-64`: `PR` sits in both `_T1_KEYS` and `_T2_KEYS`, so every 2005 diary fails both tiers — codes 1–5 can never equal SGC 10–59. Report §9 numbers reproduced 2026-07-09 (30.0% → 0.0% → ~9.0%). Effect (~3× under-weighting + province-scrambled placement + the anomalous §7 2005 bar) confirmed.

**(b) Scope:** correct and complete. No overlap with Improvement 1 (the notes correctly state joint calibration does not fix this). One addition: the fix touches only the *linkage* key; the harmonization no-op (`recode_pr`) should gain the REGION derivation but must NOT fake SGC codes for 2005.

**(c) Approach — recommend Option A (shared REGION key + Tier-2b)**, exactly as the notes prefer: honest granularity (GSS 2005 PUMF has region only — confirmed in report §9.3 "Not fully recoverable"), smallest surface, current behaviour kept behind a flag. Option B (probabilistic province) rejected — synthetic precision in a *match key* contaminates Tier-1 semantics and is paper-awkward. Option C (document-only) is superseded by the decision to fix.
**Implementation trap flagged:** do **not** reuse `_PR_MAP` / `PR_LBL` (`05_census_linkage.py:50-54`, `07_aug_to_bem.py:31-32`) as the crosswalk — they split Alberta (48) from "Prairies", whereas the GSS-2005 region 4 = MB/SK/AB. The REGION fold must be: {10,11,12,13}→1 Atlantic; 24→2 Québec; 35→3 Ontario; **{46,47,48}→4 Prairies**; 59→5 BC.

**(d) Priority/dependencies:** **P1 — first.** Upstream of calibration (Improvement 1 targets are computed on the linked file). Re-linking is the heavy step (full 286,537-agent run + downstream rebuild) — do it once, before the rake.

**(e) Open Decisions:**
- **OD-1 → Option A** (region Tier-2b inserted between Tier-2 and Tier-3: `AGEGRP, SEX, LFTAG, REGION, DDAY_STRATA`). Newer cycles also become 2b-eligible when they fail exact-PR Tier-2 — acceptable, strictly better than falling to Tier-3.
- **OD-2 → resolved: YES, coverage is complete.** Census PR values present = {10, 24, 35, 46, 48, 59} (report §9.2) → folds to all 5 GSS regions (Atlantic via 10; Prairies via 46+48). Pool 2010/15/22 additionally has 11,12,13,47 — all fold cleanly.
- **OD-3 → cannot be resolved read-only; contained by gates.** Note: `06_forecast_rake.py` projects hom30 from *observed* diaries per cycle (not from the matched mix), so the 2030 hom30 targets are untouched; the cycle-mix shift enters only through the synthetic population composition, which the rake then corrects. Risk is bounded — verify via the existing Step-6 gates (5.1–5.5) after re-linking; no user decision needed.

---

## Improvement 3 — Visualize key findings — **CONFIRM**

**(a/b) Real and correctly scoped.** Report is table/prose-heavy exactly where it matters (§9 addendum, the two note boxes are pure text); all candidate-figure numbers already exist in the report tables — no new computation. Pure reporting change, zero model/data impact.
**One mechanical correction:** `_gen_v5_plots.py` works by `{{CHART_*}}` placeholder substitution, and the placeholders were **consumed in place** on the last run (replaced by `<img>` tags in the current HTML). New figures therefore need **section-anchor injection** (insert after the known heading strings) or re-inserted placeholders — not the existing PLACE loop as-is.

**(c) Approach:** confirmed — extend `_gen_v5_plots.py` with three small matplotlib helpers fed by the already-measured constants; base64-embed; keep self-contained-HTML constraint.

**(d) Priority:** P3 — **render last.** Improvements 1–2 change the very numbers these figures show (2005 funnel, act30 sensitivity, possibly a v6 report). Figure *code* can be written any time in parallel; final render happens after the post-fix validation pass.

**(e) Open Decisions:**
- **OD-1 → the 3 core figures** (cycle-representation funnel; act30→BEM sensitivity bars + optional 24h equipment shape overlay; PR coding-disjointness strip). Skip the "what gets raked" schematic — after Improvement 1 lands it would be stale (all heads raked) and it carries the least information per pixel.
- **OD-2 → alongside the tables** (safer), trimming only prose that the figure fully duplicates. Numbers stay greppable for the paper.

---

## Blocking questions for the user
None. All ODs resolved on evidence or by recommendation above (per instruction to proceed without questions). The only *verify-before-build* items are internal: the LFTAG-cardinality check (Improvement 1, Step 0) and the standard before/after tier-share counts (Improvement 2).

### Progress Log
- **2026-07-09** — Phase-1 confirmation completed (director session, read-only). Verdicts: #1 ADJUST (gate-6.2 mechanism corrected — aggregate top-5 gate; joint rake respecified as conditional factorization hom→act|hom→cop; 2030 mirroring added; OD-1..4 resolved), #2 CONFIRM (Option A region Tier-2b; OD-2 coverage resolved YES; _PR_MAP-reuse trap flagged), #3 CONFIRM (3 core figures, alongside tables, render last; placeholder-consumption issue flagged). Execution order fixed: 2 → 1 → 3. All key numbers verified; two doc discrepancies flagged (286,537 vs 286,540; LFTAG {1,2,3} vs =5).

---

## Addendum (2026-07-09, post-execution review) — Improvement 4: v6 stale-figure audit — **CONFIRM**

**(a) Problem real?** YES, confirmed by timestamp evidence. A four-question user review of
`step4_validation_report_v6.html` (Section-2 weekday Paid-work outlier; Section-6 Paid-Work-by-LFTAG
level gap; §9.1 demand-vs-supply reading; Section-7 anomalous 2005 bar) traced all four to a single
reporting defect: the seven section charts inherited from v5 were rendered ~12:23 on the
pre-Task-A/B population, but Tasks A/B rebuilt `21CEN22GSS_aug_Full_Schedules_excl.csv` at 20:47 —
v6's prose/tables/Task-C figures are post-fix while its inherited section charts are pre-fix.
Data-side work is unaffected: Tasks A/B stay CLOSED and validated; this is Improvement-3-class
(pure reporting).

**(b/c) Scope & approach.** New **Task D** in `step4_improvements_implementation.md`: emit
`step4_validation_report_v7.html` (v6 kept byte-identical) with the 7 charts re-rendered on the
final population via a new `_gen_v7_plots.py` (CalVal reuse, alt-keyed swap, idempotency token) +
stale-number refresh (Section-2 intro/JS, Section-3 exclusion count, Section-7 gate values vs the
final Step-6 run, Section-8 BEM stats vs the R5 rebuild). Full analysis:
`step4_improvement_notes.md` Improvement 4.

**(d) Priority.** P1 — the report is the shipped deliverable and currently self-contradictory;
nothing else depends on it, so it can run immediately.

**(e) Open Decisions — resolved:** OD-1 → separate v7 (provenance; 7 image swaps is not a patch);
OD-2 → Section-7 2030-gate values verified against R6, updated only if different.

### Progress Log (addendum)
- **2026-07-09** — Improvement 4 confirmed (manager session). Task D spec + D1–D8 checklist added to
  the implementation plan; paste-ready Sonnet employee prompt authored at
  `improvement_planning/employee-prompt.md` (run-to-completion; deviations logged, not asked).
- **2026-07-09** — Task D executed by the employee session. `step4_validation_report_v7.html`
  delivered — all 7 inherited charts re-rendered on the final population, all D5 checks passed
  (idempotent, integrity clean, v5/v6 sha256 unchanged); one deviation flagged (Section-7 2005 bar
  did not rise toward the other cycles as predicted — see `step4_improvement_notes.md` Improvement 4
  and the implementation doc's Task D Progress Log for the full finding). Verdict: CLOSED.
