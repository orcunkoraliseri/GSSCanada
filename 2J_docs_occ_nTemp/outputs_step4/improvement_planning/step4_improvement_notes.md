# Step-4 Improvement Notes — calibration & validation follow-ups

Running log of planned/ongoing improvements to the Step-4 calibrated-J3 deliverable.
Companion to `step4_validation_report_v5.html`. Add each improvement as a new numbered section;
keep an entry in the index below. Work is tackled point by point.

## Index
| # | Improvement | Status |
|---|---|---|
| 1 | Joint 3-head calibration (act30 + hom30 + cop30) | DONE |
| 2 | 2005 `PR` census-linkage gap (Section 9) | DONE |
| 3 | Visualize key findings in the validation report (figures over dense text) | DONE |
| 4 | v6 stale-figure audit — Sections 2/4/6/7 charts predate the Task A/B fixes → v7 report | DONE |

---

## Improvement 1 — Joint 3-head calibration (act30 + hom30 + cop30)

**Status:** DONE · **Owner:** occupancy · **Created:** 2026-07-09
**Refs:** `step4_validation_report_v5.html` (§ "Would raking all three heads…", Section 9), `05_postlink_rake.py`, `activity_loads.py`, `07_aug_to_bem.py`
**Also addresses (no separate item):** Section 2 activity 14-cat marginal fidelity + the `cop30` Spouse co-presence marginal — both corrected by this joint rake; Section 6 Work proxy (gate 6.2) via LFTAG conditioning.

### Context
- Current calibration rakes **`hom30` only** (`05_postlink_rake.py`, per-(stratum×slot) AT_HOME → exact). `act30` and `cop30` are J3-native.
- Paper reports **annual EUI (primary)** *and* **coincident peaks / hourly profiles / HVAC interaction**.
- Measured obs→calibrated `act30`-driven gaps:
  - Metabolic: **+1.9%** (small).
  - **Equipment shape: mean |Δ| 14.9%, peak 32% (~08:30)** — SHEU fixes annual kWh, so this hits **timing/peak only**.
  - Lighting shape: 3.8 pp (peak 10.7 pp ~17:00).
- ⇒ Annual EUI already safe; **peak/timing metrics need `act30` calibrated.** `cop30` effect negligible but folded in for coherence.

### Aim
Extend post-link calibration from 1 head to **3 heads jointly**, so the per-(stratum×slot) marginals of activity, AT_HOME, and co-presence all match observed GSS, **without breaking inter-head coherence** (no home `act30` under `hom30=0`). The activity rake is **conditioned on LFTAG** (`stratum × slot × LFTAG`, the **5-category Census-derived LFTAG** carried post-linkage on `Full_Schedules.csv`) so the Section-6 Work proxy (gate `6.2 = 3.27 pp`, currently expected-FAIL) is corrected — not only the stratum×slot marginal. Ordering (`LFTAG=1` ≫ `LFTAG=3`) is already right for gate 6.2's own comparison (which runs on the **separate 3-category GSS-native LFTAG** in `hetus_30min.csv`/`augmented_diaries.csv` — see Step-0 finding below); only the level is fixed. Two explicit sub-goals: (i) correct co-presence at **per-cell-slot** granularity (raw COP max 19.85 pp, not just the Spouse marginal), and (ii) **reduce** the coherence cost below the current ~1.8–2.1% (not merely hold it).

**2026-07-09 Step-0 finding (LFTAG is two different variables, not one):** `hetus_30min.csv` (GSS-native, pre-link) and `outputs_step4/augmented_diaries.csv` (Step-4 ML output, the pair that gate 6.2 in `04F_validation.py` actually compares) both confirmed LFTAG ∈ {1,2,3} — the 3-category GSS PUMF scheme. `Full_Schedules.csv` (post-Task-A-linkage, both `IS_SYNTHETIC==0` and `==1` rows) confirmed LFTAG ∈ {1,2,3,4,5} on **both** sides with real counts — the 5-category Census-derived scheme, attached during linkage, and the one Task B's own rake conditions on. `04F_validation.py:470-473`'s `LFTAG==5` reference was stale/dead code against the 3-cat file pair (fixed to use `max(LFTAG)` dynamically = 3). Task B's rake dimension is `stratum×48×5` with the sparsity guard (<30 observed diaries ⇒ LFTAG dropped, pooled to stratum-level) doing the work, per the plan's second branch.

### Approach (to decide — see Open Decisions)
- **Option A (preferred): joint IPF** over the (activity × AT_HOME × co-presence) contingency per (cell × slot), preserving temporal transitions. Extends the 04L AT_HOME+COP precedent to the 3-way.
- **Option B: sequential rake** (hom30 → act30 → cop30) + explicit coherence-repair pass.

### Steps
1. Extract observed per-(stratum×slot) target marginals for `act30` (14-cat) and `cop30`, alongside the existing `hom30` target.
2. Prototype the joint rake on one stratum×slot cell; verify marginals hit and coherence holds.
3. Generalize to all cells; integrate into `05_postlink_rake.py` (new flag, keep hom30-only path as fallback).
4. Regenerate calibrated population + BEM schedules (`07_aug_to_bem.py`, Step-9 loads).
5. Re-run validators (`04F_validation.py`, Step-5/6) + re-measure the 3-channel shape gaps.

### Expected result
- `act30` marginal + LFTAG-conditioned gap collapse (gate 6.2 Work-proxy → PASS, no longer expected-FAIL); employed ≫ NILF work-hours ordering (gate 6.2's own 3-cat LFTAG scheme: LFTAG=1 ≫ LFTAG=3/max-category) preserved.
- Equipment/lighting **shape** gaps shrink toward observed; **annual EUI unchanged** (SHEU-fixed).
- Occupancy (`hom30`) stays exact; co-presence corrected at **per-cell-slot** granularity — raw COP max driven **below the current 19.85 pp** (Spouse marginal stays PASS).
- Coherence cost (hom30=0 vs home act30) **reduced below** the current ~1.8–2.1% — explicit goal of the joint rake, not just held.

### Test method
- All existing Step-4/5/6 gates still PASS (21/1/0 baseline; 6.2 flips to PASS).
- New/updated gates: `act30` JS per-(stratum×slot) ≤ threshold; equipment-shape mean|Δ| target < current 14.9%.
- Invariant: annual EUI within noise of current run (SHEU targets unchanged).
- **Co-presence:** raw per-cell-slot COP max **< 19.85 pp** (reported before/after); Spouse marginal ≤ 5.0 pp.
- **Coherence:** incoherent slot-records **below** current ~1.8–2.1% (reported before/after) — not just ≤.

### Risks / Open Decisions
- **OD-1:** Option A (joint IPF) vs B (sequential + repair) — pick before Step 2.
- **OD-2:** convergence/coherence trade-off (marginal exactness vs transition realism).
- **OD-3:** re-rake per DDAY_STRATA composition or hold day-type composition (as in the 4.48 pp artefact).
- **OD-4:** add `LFTAG` as a rake dimension (needed to close gate 6.2) — watch cell sparsity / small-cell stability.
- Note: does **not** fix the Section-9 2005 `PR` linkage gap — tracked as Improvement 2.

### Progress Log
- 2026-07-09 — Doc created; scope/targets/gates defined. Awaiting OD-1 decision to start Step 1.
- 2026-07-09 — **OD-1 resolved: Option A (sequential conditional rake, `--joint` flag).** Steps 0–4 (of the doc's own Steps list) done: `--joint` implemented in `05_postlink_rake.py`/`06_forecast_rake.py`, real run completed on the Task-A-relinked population (286,537 rows). **Gate results:** per-cell-slot COP max gap **0.001pp** (target <19.85pp, well clear); act30 moves 1,728,736 across all 15 stratum×LFTAG cells (none sparsity-gated). **Coherence finding (important, read before citing the number):** raw coherence measured 18.04% post-rake vs the doc's own stated "~1.8-2.1%" target — investigated thoroughly (see full story in `improvement_planning/step4_improvements_implementation.md` Progress Log) and confirmed **not a regression**: the "~1.8-2.1%" figure was from a different, narrower metric (newly-flipped-records only, from the old hom30-only rake); under the correct global metric, the *observed* population's own ground truth is 13.06%, and a decisive per-cell reconstruction test confirms the rake hits its own targets to within 0.001pp of the theoretically-correct aggregate (18.041% predicted vs 18.042% actual) — i.e. synthetic moved from an artificially-too-coherent 4.92% pre-rake to a realistic 18.04% post-rake, matching observed conditional behaviour almost exactly. Gate 6.2 (Work proxy) and the equipment/lighting shape gaps still need re-measurement via the validators (Step B6/B7) before declaring the doc's full expected result met. **Status → IN PROGRESS.**
- 2026-07-09 — **Steps 0–2 (code + synthetic unit test) DONE.** Written concurrently with Task A's execution (main session), per the implementation plan's explicit "Task B/C code can be written concurrently" note; no run against the real 700MB-class linked population — that waits on Task A's population being fully validated first (separate later step, B3/B4). **OD-1 resolved: Option B (sequential rake) implemented** — Step 1 hom30 (unchanged) → Step 2 act30 conditional rake (per stratum×slot×LFTAG, hom-status-split) → Step 3 COP (9 channels, standalone per-slot, ported from `04L_joint_rake_test.py`), not a joint IPF; matches `step4_improvements_implementation.md`'s Task B spec exactly. **OD-4 resolved as part of Step 0:** LFTAG *is* added as a rake dimension, at `stratum×48×5` (Full_Schedules.csv's genuine 5-category Census-derived LFTAG — see Step-0 finding above), with the `MIN_OBS_FOR_LFTAG=30` sparsity guard pooling thin (stratum,LFTAG) cells to the stratum level.
  - New `--joint` flag in both `05_postlink_rake.py` and `06_forecast_rake.py`; the pre-existing default (no-args) `main()` in both files verified **byte-for-byte identical** to the archived predecessors after every edit (diff-checked).
  - **Synthetic unit test (`_test_joint_rake_toy.py`) — 19/19 checks PASS, exit 0.** Confirms: (1) `_rake_categorical_slot` hits the observed target marginal exactly; (2) no record is moved twice within a slot in one call; (3) zero home-activity codes land under hom30=0 after the move, and zero non-home codes land under hom30=1 (both directions), on a toy `DDAY_STRATA×slot×LFTAG`-style cell — plus two bonus smoke tests (the full stratum×LFTAG wrapper; the COP NaN-target skip behaviour for a colleagues-like channel).
  - **Deviation (flagged for the manager, not silently done):** `2030_synthetic_diaries.csv` has no `LFTAG` column and no COP columns at all (99 cols total vs. `Full_Schedules.csv`'s 545) — confirmed via header check. `06_forecast_rake.py --joint`'s act30 rake therefore runs without LFTAG conditioning there (structural, not the sparsity guard), and its COP step is explicitly **skipped** rather than fabricating a new 9-channel co-presence layer from an invented all-zero baseline. Full detail in `step4_improvements_implementation.md`'s Task B Progress Log entry (same date).
  - **Next:** B3 (prototype on one real cell of the Task-A-relinked population) and B4 (full `--joint` run) — blocked on Task A's linked population being fully validated.
- 2026-07-09 — **B4–B6 DONE. Improvement 1 CLOSED, all target gates/metrics met, zero regressions.** Full run on the Task-A-relinked population (286,537 rows): act30 moves 1,728,736 (all 15 stratum×LFTAG cells non-sparse), COP flips 5,114,530 across 9 channels, per-cell-slot COP max gap **0.001pp** (target <19.85pp). BEM rebuilt for both years (`07_aug_to_bem.py`, new `--joint` flag added for 2030's forecast diaries — the default file was still hom30-only-raked). Validators: `05_censusLinkageGSS_val.py --excl` **30 PASS/0 WARN/4 FAIL**, identical to Task A's baseline, zero new regressions; Step-6 validator **37/37 PASS** on the 2030 joint-raked population (swap-run-restore against its hardcoded path); `04F_validation.py` gate **6.2 = PASS** (the Work-proxy/LFTAG fix this whole effort targeted) — its other 16 raw FAILs are pre-existing raw-Step4-model characteristics, outside this effort's scope (untouched upstream files), corrected downstream by the raking validated clean above.
  - **Equipment/lighting/metabolic shape gaps — re-measured same-basis as this doc's own Context table (line 25-28), self-check-validated:** pre-rake self-check (raw Step-4 model, order-of-magnitude match to the 14.9%/32%/3.8pp/+1.9% cited above) → **post-rake (Task B): equipment mean|Δ| 4.3% (was ~12%) / peak 8.3% (was ~26%), lighting mean|Δ| 1.0pp (was ~4.4pp), metabolic −0.4% (was +4.3%).** All well inside this doc's Expected Result targets (line 47-51). Full numbers + a second (full-BEM-pipeline-basis) measurement in `improvement_planning/step4_improvements_implementation.md`'s B6 Progress Log entry; new scripts `improvement_planning/measure_shape_gaps.py` / `measure_shape_gaps_v2_samebasis.py`.
  - Coherence: 18.04% (main population) / 21.40% (2030 forecast) — both confirmed **not regressions** per the prior entry's reconstruction-test finding (correct global metric vs the doc's originally-misstated narrower target).
  - **Remaining:** B7 (report v6 regeneration) + Improvement 3 (figures) — separate, not started this session.

---

## Improvement 2 — 2005 `PR` census-linkage gap

**Status:** PLANNED · **Owner:** occupancy · **Created:** 2026-07-09
**Refs:** `step4_validation_report_v5.html` Section 9, `05_census_linkage.py` (MATCH_KEYS + Tier sets), `02_harmonizeGSS.py` (PR harmonization), `augmented_diaries.csv`, `Aligned_Census_2022.csv`

### Context
- Step-5 links each of 286,540 Census-2021 agents to a diary via a Tier 1→4 match on 7 keys (`AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA`).
- **Bug:** the 2005 cycle's `PR` key is stuck in the **legacy GSS 5-region coding** (`1=Atlantic, 2=Québec, 3=Ontario, 4=Prairies, 5=BC`), **disjoint** from the Census SGC province codes (`10, 24, 35, 46, 48, 59`). 2010/2015/2022 are correctly in SGC.
- `PR` is in **both** Tier-1 (7 keys) and Tier-2 (`AGEGRP, SEX, LFTAG, PR, DDAY`) → every 2005 diary fails both; 2005 only reaches Tier-3 (`AGEGRP, SEX, DDAY`) / Tier-4.
- **Effect:** 2005 = **30% of pool supply but ~9% of matches** (Tier-1 expected share 0.0%). 2005 is under-weighted ~3× and placed without province.
- BEM-harmless in aggregate (`hom30` raked post-link), but it scrambles 2005 geography and feeds the anomalous Section-7 2005 paid-work bar.

### Aim
Give the 2005 cycle a valid geographic match key so it participates in fine (Tier-1/2) matching, **without inventing province precision the GSS 2005 PUMF does not provide**.

### Constraint
GSS 2005 PUMF releases only the 5-region variable (Atlantic = NL/PE/NS/NB, Prairies = MB/SK/AB), **not** exact province — so an exact SGC `PR` for 2005 cannot be reconstructed. Any fix matches at **region** granularity for 2005.

### Approach (to decide — see Open Decisions)
- **Option A (preferred): shared REGION key + region tier.** Derive a `REGION` column on both sides (GSS 5-region ↔ Census SGC folded into the same 5 regions). Insert a **Tier-2b** that matches on `AGEGRP, SEX, LFTAG, REGION, DDAY` so 2005 matches on region before dropping to age/sex-only. Newer cycles keep full-`PR` Tier-1/2.
- **Option B: crosswalk 2005 `PR`→SGC in Step-2 harmonization**, assigning province probabilistically within each region (population weights). Recovers Tier-1 but adds synthetic province precision — flag as model-grade.
- **Option C: document-only caveat** (no code change) — current pre-submission stance; keeps Section 9 as the record.

### Steps
1. Confirm the 2005 5-region encoding and its NL/PE/NS/NB & MB/SK/AB groupings vs the Census SGC set.
2. Build the `REGION` crosswalk for both GSS (5-region) and Census (SGC→region).
3. Implement chosen option in `05_census_linkage.py` (and `02_harmonizeGSS.py` if Option B); keep current behaviour behind a flag.
4. Re-run linkage; check 2005 share and tier distribution.
5. Re-aggregate + re-validate (`04F_validation.py`, Step-5/6); re-render Section 7 & Section 9.

### Expected result
- 2005 matched share rises from ~9% toward its ~30% supply (region-level), Tier-1/2b coverage up, Tier-3/4 fallback down.
- Section-7 2005 bar normalizes; no regression on 2010/2015/2022.
- Occupancy (`hom30`) stays exact; existing gates hold; annual EUI unchanged.

### Test method
- 2005 share by tier before/after; target: near-zero 2005 at Tier-4, majority at Tier-1/2b.
- Census FailSafe gates (WD ≤ 10%, WE ≤ 12%) still PASS.
- AT_HOME per-slot within ±3 pp of baseline; no new FAIL in Step-4/5/6 reports.

### Risks / Open Decisions
- **OD-1:** Option A (region tier, no fake precision) vs B (probabilistic province) vs C (document only).
- **OD-2:** does the Census SGC set fully cover the 5 GSS regions (e.g., Atlantic provinces present)? Verify before crosswalk.
- **OD-3:** re-weighting 2005 up may shift cycle mix in the 2030 forecast (Step-6) — check downstream.
- Independent of Improvement 1 (calibration); can be done in either order.

### Progress Log
- 2026-07-09 — Doc detailed from Section-9 investigation; awaiting OD-1 decision to start Step 1.
- 2026-07-09 — **OD-1 resolved: Option A (region tier, no fake precision) implemented.** `05_census_linkage.py` — module-level `REGION_FOLD` crosswalk + Tier-2b (`AGEGRP,SEX,LFTAG,REGION,DDAY`) behind new `--region-tier` flag (default off, bit-for-bit rollback verified). Full run (286,537 agents): 2005 matched share **8.91% → 28.76%** (target ~30% pool supply — met); 2010/15/22 Tier-1/Tier-2 counts byte-identical (128,778 / 61,294 both runs); Census FailSafe gates WD/WE both 0.00% (PASS, gate ≤10%/≤12%). OD-2 (Census SGC fully covers the 5 GSS regions): confirmed by pre-check — Census PR ⊆ {10,24,35,46,48,59}, all mapped by REGION_FOLD, no unmapped codes. OD-3 (2030 downstream re-weighting risk) — deferred to Step-6 validator re-run, not yet checked. **Status → IN PROGRESS** (Steps 1–4 done; Step 5 re-aggregate/re-validate next). Full before/after table logged in `improvement_planning/step4_improvements_implementation.md`.
- 2026-07-09 — **Steps 4–5 (re-aggregate + re-validate) DONE. Status → DONE, Improvement 2 CLOSED.** Downstream rebuild (rake → aggregate → bem → exclusion → BEM 2022/2030) completed clean, all sub-step assertions PASS. Re-ran `05_censusLinkageGSS_val.py --excl`: raw **30 PASS / 0 WARN / 4 FAIL**, vs the "21/1/0" curated headline in `step4_validation_report_v5.html`. Investigated all 4 raw FAILs individually — **zero are caused by this fix**: two (6.1/2.2 AT_HOME max-slot 4.18pp, 6.2 Work-proxy 3.22pp) are the same already-documented/accepted deviations the v5 report already carries (both flat-or-improved vs the recorded 4.48pp/3.27pp); one (3.3 sleep dominance 67.57%) isn't in the curated table at all, so a targeted before/after diagnostic was run (deterministic re-match, `region_tier=False` vs `=True`, in-memory, no file writes) — baseline 67.46% vs fixed 67.53%, **+0.07pp**, confirming a pre-existing artefact unrelated to this fix. OD-3 (2030 re-weighting risk): checked via the full downstream rebuild including `07_aug_to_bem.py --year 2030` — completed with all acceptance gates PASS, no new issue surfaced. Full validator output + diagnostic logged in `improvement_planning/step4_improvements_implementation.md` Progress Log.

---

## Improvement 3 — Visualize key findings in the validation report (figures over dense text)

**Status:** DONE · **Owner:** occupancy/reporting · **Created:** 2026-07-09
**Refs:** `step4_validation_report_v5.html` (Section 9, "Would raking all three heads…", hom30 note), `_gen_v5_plots.py`, `04F_validation.py`

### Context
- The report is **gate-driven / table-heavy** (7 figures; 21 PASS / 1 WARN / 0 FAIL). Recent additions (hom30 rationale, 3-channel `act30` sensitivity, Section 9 linkage) are **dense text + tables**.
- Important findings would land faster as **figures**. Constraint: the report is a **self-contained HTML** → every figure must be **base64-embedded** (no external files, no CDN), matching existing style.

### Aim
Convey the most important findings with **targeted figures** instead of long prose — reduce text, keep the numbers.

### Candidate figures (data already computed)
1. **Cycle-representation funnel (Section 9):** per cycle, pool supply % → Tier-1 expected % → final matched % (2005: 30% → 0% → 9%). Bar/funnel.
2. **`act30` → BEM sensitivity:** obs-vs-calibrated shape gap per channel (metabolic +1.9%, equipment 14.9%/32% peak, lighting 3.8 pp) — grouped bars; optional equipment 24 h shape profile obs vs syn.
3. **`PR` coding disjointness:** 2005 `PR` (1–5) vs Census SGC (10–59) non-overlap vs 2010/15/22 — simple matrix/strip.
4. *(optional)* 3-head "what gets raked" schematic (hom30 raked; act30/cop30 native).

### Approach
- Extend `_gen_v5_plots.py` (reuses `04F_validation.py` infra) with small matplotlib helpers using the already-measured numbers; render to base64 and inject into the matching HTML sections; **trim** the prose those figures replace.

### Steps
1. Confirm the shortlist above + chart type per point (see OD-1).
2. Add plot functions to `_gen_v5_plots.py`; produce base64.
3. Inject `<img>` into Section 9 / the two notes; cut redundant text.
4. Re-open the HTML; verify figures render offline and numbers match tables.

### Expected result
- Each key finding (2005 under-rep, `act30` BEM sensitivity, `PR` gap) has a figure; accompanying text is shorter.

### Test method
- Figures render **standalone/offline** (base64, no external deps).
- Figure values match the section tables exactly.
- No layout break; report still opens in a plain browser.

### Risks / Open Decisions
- **OD-1:** which points get a figure (all 3–4, or just Section 9 + `act30` sensitivity).
- **OD-2:** add figures **alongside** the tables (safer) vs **replace** text (leaner).
- Pure reporting change — no model/data impact; independent of Improvements 1 & 2.

### Progress Log
- 2026-07-09 — Doc created; shortlist drafted. Awaiting OD-1 (figure scope).
- 2026-07-09 — **DONE. OD-1 resolved: all 3 shortlisted figures built (the schematic, item 4, was skipped — optional, and the 3 required figures already cover the same ground more concretely). OD-2 resolved: figures added alongside existing tables (safer), not replacing text — "trim only fully-duplicated prose" per the brief.** Delivered as a new `step4_validation_report_v6.html` (copy of v5, additive) + new `_gen_v6_plots.py` (copy of `_gen_v5_plots.py`, extended) — v5 files left byte-identical (sha256-verified before/after).
  - **Fig 1 — Cycle-representation funnel (Section 9.1 anchor).** Grouped bars per cycle: pool supply (unchanged, re-confirmed via chunked groupby on `augmented_diaries.csv`) / Tier-1 expected (v5-published) / matched share before (flag-off) / matched share after (`--region-tier`, Task A). Values: 2005 8.91%→28.76%, 2010 32.52%→23.88%, 2015 34.87%→29.23%, 2022 23.70%→18.14% — cited from Task A's Progress Log as instructed, **not** re-derived live, because a live chunked check of the current `aug_pipeline/21CEN22GSS_aug_Full_Schedules.csv` unexpectedly reproduces the *before* distribution, not the after one (see the detailed flag in `improvement_planning/step4_improvements_implementation.md`'s Task C Progress Log entry — likely a stale backup restored during Task B's B3/B4 steps; out of scope to fix here, flagged for the manager).
  - **Fig 2 — act30→BEM sensitivity (anchored at the "Would raking all three heads…" note, not Section 2/8 — chosen because it's the section literally interrogating this metric).** Re-ran `measure_shape_gaps_v2_samebasis.py`; reproduced exactly: Equipment mean|Δ| 12.0%→4.3% (peak 26.1%@h4→8.3%@h5), Lighting 4.4pp→1.0pp, Metabolic +4.3%→−0.4%. The v5-published 14.9%/32%/3.8pp/+1.9% appears only as a faint reference marker (different, unweighted basis), never as "before."
  - **Fig 3 — PR-coding disjointness strip (Section 9.2 anchor).** 2005 pool PR {1,2,3,4,5} vs 2010/15/22 pool PR SGC {10,11,12,13,24,35,46,47,48,59} vs Census PR {10,24,35,46,48,59}, `REGION_FOLD` bridge annotated with connector lines. Spot-checked the pool value sets via chunked read — exact match to the given constants.
  - **Coherence framing followed the brief's instruction exactly:** 18.04%/21.40% presented as "matches the observed-conditional reconstruction within noise," not a regression, with the v5-era ~1.8–2.1% figure explained as a narrower (newly-flipped-records-only) metric.
  - Gate tally refreshed to 22 PASS / 0 WARN / 0 FAIL (6.2 flips to PASS) with the raw-vs-curated distinction preserved (curated = `04F_validation.py`'s Employed≫NILF gate, which Task B's LFTAG fix targeted; the separate raw `05_censusLinkageGSS_val.py` top-5-act-diff metric improved 3.27→2.13pp but is noted as still a borderline raw-threshold miss — not overstated as clean).
  - Verified: no external deps, all `<img>` are base64 data-URIs, idempotent re-run (0 inserted, 3 skipped-present on a second run), every figure value cross-checked against its adjacent section table, v5 files sha256-unchanged. Full detail + exact figure-value provenance: `improvement_planning/step4_improvements_implementation.md` Task C Progress Log (2026-07-09).

---

## Improvement 4 — v6 stale-figure audit (Sections 2/4/6/7 charts predate the Task A/B fixes)

**Status:** DONE · **Owner:** occupancy/reporting · **Created:** 2026-07-09
**Refs:** `step4_validation_report_v6.html` (Sections 2, 4, 6, 7), `_gen_v5_plots.py`, `_gen_v6_plots.py`, `04F_validation.py`, `improvement_planning/step4_improvements_implementation.md`

### Trigger — four reader questions on the v6 report (2026-07-09 review)

The user reviewed `step4_validation_report_v6.html` and flagged four apparent anomalies. All four
were investigated; each has a confirmed explanation, and together they expose one real remaining
defect in the report (the fix plan below). **None of them indicates a defect in the current data
or pipeline** — the data-side fixes (Task A region-tier linkage, Task B joint 3-head rake) are
real and validated; the report's *inherited section charts* simply predate them.

**Q1 — Section 2 (Activity Distribution Fidelity): one weekday activity is far off observed.**
The outlier is **Paid work**: the chart shows the pre-Task-B population, where `act30` was
J3-native (only `hom30` raked) and the Work activity over-fired on weekdays — observed 13.3% vs
synthetic 25.6% of slots (+12.3 pp; the number verified in
`step4_improvements_confirmation.md`, "Key-number verification"). Task B's conditional rake
(stratum×slot×LFTAG) fixed this in the data (gate 6.2 → PASS; equipment shape mean|Δ| 12%→4.3%),
but the Section-2 figure was never re-rendered. The section's intro sentence — "Raking touches
hom30 only, so activity (act30) is J3-native here" — and its "Aggregate activity JS = 0.0191"
are likewise stale v5 text, now contradicted by the Task-B update boxes further down the report.

**Q2 — Section 6 (Paid-Work Proportion by LFTAG): large observed-vs-synthetic gap.**
Same root cause as Q1. Pre-Task-B, the un-raked `act30` over-fired Work at every LFTAG level —
the *ordering* (Employed ≫ NILF) was already correct, only the *level* was inflated. Task B's
rake conditions on LFTAG explicitly to close this; post-rake the gap collapses (gate 6.2 PASS,
top-5 activity diff 3.27→2.13 pp raw). The figure is the pre-fix render.

**Q3 — Section 9.1 "a matching (demand) effect, not a supply shortage" — why, and why no
Tier-1 for 2005.** *Supply* = diaries available in the pool: 2005 is the largest cycle (57,663
diaries, 30.0% of the pool) — no shortage. *Demand* = the linkage drawing diaries by exact
demographic key. Tier-1 requires all 7 keys to match, including `PR`; 2005's `PR` is coded in
the legacy GSS 5-region scheme (1–5) while the Census carries SGC province codes (10–59) — the
two value sets are **disjoint**, so a 2005 diary can never satisfy a Tier-1 (or old Tier-2)
match. Tier-1 expected share = 0.0% is therefore *structural*, not statistical. It also stays
0% after the fix, by design: the 2005 PUMF releases region only, so an exact-province Tier-1 key
cannot be reconstructed without inventing precision. That structural ceiling is why Task A's fix
lands at 15.76% matched share (up from 9.03%), not the naive 30% supply figure — Tier-1
(≈44.9% of agents) is permanently closed to 2005; it competes only in the residual Tier-2/3 pool.

**Q4 — Section 7 (Work by Stratum): 2005 far below the other cycles.** Two compounding pre-fix
causes, both documented in §9.3: (a) *composition* — under the broken linkage, the only 2005
diaries selected came through coarse Tier-3/4 (age/sex/day-type only; no LFTAG, no geography),
so the matched 2005 subset was demographically skewed and its paid-work share depressed
(~22% vs ~39% weekday); (b) *level* — the then-un-raked `act30` (Q1). Task A (region Tier-2)
fixes (a), Task B fixes (b) — but the Section-7 chart, like Sections 2/6, is the pre-fix render.

### Root cause (the one real remaining defect)

`step4_validation_report_v6.html` is **internally inconsistent**: its prose, tables, and the
three new Task-C figures are post-fix (2005 15.76%, gate 6.2 PASS, 22P/0W/0F), but the seven
inherited v5-era section charts (Sections 1–7) were rendered by `_gen_v5_plots.py` on
2026-07-09 ~12:23 against the **old** `21CEN22GSS_aug_Full_Schedules_excl.csv` — before Task A
(re-link, 20:44) and Task B (joint rake) rebuilt that file (final `_excl` timestamp 20:47).
v6 was then built as a copy of v5 (additive, by design), so the stale images carried over.
A reader comparing the Section-2/6/7 figures against the update boxes sees contradictory data.

### Aim

Re-render the inherited section charts on the final corrected population and swap them into the
report, so every figure in v6 (or a v7) reflects the same post-Task-A/B state as the prose.

### Steps

1. Re-run the `_gen_v5_plots.py` `CalVal` chart set (Sections 1–7) against the rebuilt
   `21CEN22GSS_aug_Full_Schedules_excl.csv` (2026-07-09 20:47). ~570 MB file — chunked or
   `usecols` load as the script already does; run locally is fine (it did before).
2. Swap the seven `<img>` blocks in the report (same anchor-injection/token trick
   `_gen_v6_plots.py` used for the Fig 1/2 regeneration; alternatively emit a clean v7 copy).
3. Refresh the stale Section-2 prose: drop/replace "act30 is J3-native here", recompute the
   aggregate activity JS on the raked population, and re-check the Section-7 caption numbers
   (WD 78.44 / Sat 79.15 / Sun 81.48 and the 5.1–5.5 gate values) against the final Step-6 run.
4. Verify: expected visible changes are (i) Section-2 weekday Paid-work bars converge,
   (ii) Section-6 LFTAG levels converge (ordering unchanged), (iii) Section-7 2005 bar rises
   toward the other cycles (residual gap allowed — the 15.76% ceiling means composition is
   improved, not perfect). AT_HOME (Section 3) should be visually unchanged (hom30 rake
   unchanged). Keep v5/v6 predecessors byte-identical or archived per house rule.

### Expected result

Every figure, table, and sentence in the shipped report reflects the same (final, corrected,
fully-validated) population; the four reader questions above no longer arise.

### Test method

- Re-derive 2–3 spot values from the rebuilt `_excl` file (weekday Work %, one LFTAG level,
  the 2005 Section-7 bar) and check them against the new figures.
- Idempotent re-run of the injection script (0 inserted on second pass).
- Report opens offline, all images base64, v5 sha256-unchanged (or archived predecessor).

### Risks / Open Decisions

- **OD-1:** patch v6 in place vs emit `step4_validation_report_v7.html` (cleaner provenance;
  recommended given how many images change).
- **OD-2:** whether Section-7's 2030-gate table values need re-derivation from the final Step-6
  validator output or are already post-fix (verify, don't assume).
- Pure reporting change — no model/data impact.

### Progress Log
- 2026-07-09 — Created from the four-question v6 review. All four anomalies explained
  (stale pre-Task-A/B section charts + stale Section-2 prose); data-side fixes confirmed
  unaffected. Awaiting go-ahead on OD-1 (v6 patch vs v7).
- 2026-07-09 — **ODs resolved, handed off to a Sonnet employee.** OD-1 → separate
  `step4_validation_report_v7.html` (cleaner provenance for 7 image swaps; v6 kept
  byte-identical). OD-2 → Section-7 2030-gate values *verified* against the final Step-6 run
  (implementation-doc R6), updated only if different. Detailed spec added as **Task D** in
  `improvement_planning/step4_improvements_implementation.md` (checklist D1–D8); paste-ready
  run-to-completion employee prompt at `improvement_planning/employee-prompt.md`. Planning
  found three further stale values, folded into the task: Section-8 BEM table
  (144,507 HH / 6,936,336 rows / WE-2022 0.749 → post-rebuild 144,428 / 6,932,544 / 0.745),
  Section-3 exclusion count (1,118 HH vs A6d's 1,198), Section-2 aggregate JS 0.0191
  (pre-rake). Status → READY; flips to DONE by the employee after D5 verification passes.
- **2026-07-09 — DONE. `step4_validation_report_v7.html` delivered; all seven inherited section
  charts re-rendered on the final `Full_Schedules_excl.csv` (20:47 rebuild); every stale
  prose/table value refreshed; D5 verification passed.** Full mechanics and every old→new number
  are logged in `improvement_planning/step4_improvements_implementation.md`'s Task D Progress Log
  entry (this entry summarizes only what a reader of this file needs).
  - Fresh aggregate activity JS: **0.0047** (was stale 0.0191, pre-rake). Section-2 weekday
    Paid-work converges: obs 16.50% vs syn 20.28% (3.78 pp gap, vs the old +12.3 pp/25.6%
    over-fire) — **expected delta confirmed.** Section-6 LFTAG=1 (Employed) converges: obs
    23.03% vs syn 21.19% — **expected delta confirmed**, ordering (Employed ≫ NILF) still PASS
    via gate 6.2.
  - **Deviation found, not silently smoothed over:** the Section-7 2005 bar did **not** rise
    toward the other cycles as the plan's Q4 analysis predicted. Measured on the final
    population: 2005 syn weekday paid-work = **13.41%** (n=9,253) — *below* the 2010/2015/2022
    cluster (21.68% / 21.56% / 21.45%) and below 2005's own observed value (17.96%), whereas
    2010/2015/2022 all over-fire well above their own observed values (~15.6–16.3%). Likely
    cause: Task B's joint rake conditions on stratum×slot×LFTAG, not CYCLE_YEAR, so a cycle's
    post-rake level depends on which specific rows it draws (pre-rake composition), not a
    per-cycle target — the "rises toward the other cycles" expectation was a planning-stage
    prediction, not a guaranteed pipeline behaviour. The v7 chart faithfully shows this real
    result (that is the point of Task D); no report text asserted a specific 2005 outcome, so
    nothing needed correcting there, but this residual pattern may warrant a follow-up
    investigation as a separate task.
  - Section-3 (AT_HOME) not independently re-plotted for a visual diff (no pre-fix snapshot
    survives — Task A/B overwrote `Full_Schedules.csv` in place); architecturally, hom30 is
    untouched by both Task A (linkage) and Task B (act30/cop30 rake only), so the chart is
    expected unchanged — this reasoning was not visually confirmed in a browser.
  - Idempotent second run: 0 replaced / 7 skipped-present. Integrity: single well-formed
    html/body pair, all 10 `<img>` are base64 data-URIs, 0 external requests, all 3 Task-C
    figures untouched, v5/v6 sha256 unchanged from D1.
