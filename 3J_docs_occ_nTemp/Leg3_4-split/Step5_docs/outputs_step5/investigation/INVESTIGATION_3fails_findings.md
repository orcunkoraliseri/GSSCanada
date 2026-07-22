# Step-5 (3J Leg-3, 4-split) — Investigation findings: the 3 residual FAILs

**Date:** 2026-07-21 · **Role:** employee · **Chain:** MIN_POOL=15 winner (32P/4W/3F)
**Mode:** diagnostic + options-scoping only. Production matcher, MIN_POOL=15 default, and
all validator gates untouched. No gate relaxed.

**Artifacts produced (all in `outputs_step5/investigation/`):**

| File | What |
|---|---|
| `investigate_3fails.py` → `INVESTIGATION_run.log` | Main diagnostic: slot tables, tier/thin-cell attribution, R1 bootstrap null tests, PR=6 audit |
| `investigate_3fails_probe2.py` → `INVESTIGATION_probe2.log` | Mechanism confirmation: pool cell-conditional prediction (2.2), demographic-reweighting test (R1), composition shift |
| `investigate_3fails_probe3.py` → `INVESTIGATION_probe3.log` | Exact PR=6 donor attribution via deterministic re-match, verified against saved `Matched_Keys` |

**Replication check (all frozen numbers re-derived from the artifacts, exact match):**
2.2-WD syn=6,052 / obs=15,506 / 3.66 pp / 6 slots ✓ · 2.2-WE 2.17 pp / 0 slots ✓ ·
R1 2005-d2 = 4.796 pp ✓ · PR=6 missing from pool ✓ · Frame = 30,273 rows, census deduped
= 30,273 PIDs, excluded = 771 ✓.

> ⚠️ **Supersedes the 2026-07-21 Progress Log entry in `3rdJ_05_censusLinkage_4split_val.md`
> titled "Investigation of the 3 residual FAILs".** That entry referenced this findings file
> before it existed and asserted a thin-cell root cause for Gate 2.2 that the probes below
> **refute**. The numbers and dispositions in THIS file are the verified ones.

---

## FAIL 1 — Gate 2.2 AT_HOME, weekday within-day-type (3.66 pp, 6 slots)

### 1. The 6 failing WD slots (core ask)

All six are **syn < obs** (synthetic-donor rows show *less* home presence). They are NOT the
06:30–09:00 commute window of the stale note — they are mid-morning, lunch, and the
pre-dinner return window:

| Slot | Clock (04:00-origin) | syn % | obs % | Δ (syn−obs) pp |
|---|---|---|---|---|
| 10 | 08:30–09:00 | 34.15 | 37.16 | −3.01 |
| 11 | 09:00–09:30 | 30.63 | 33.98 | −3.35 |
| 12 | 09:30–10:00 | 28.72 | 32.07 | −3.35 |
| 17 | 12:00–12:30 | 25.63 | 28.94 | −3.31 |
| 26 | 16:30–17:00 | 37.57 | 40.68 | −3.11 |
| 27 | 17:00–17:30 | 45.94 | 49.60 | −3.66 |

### 2. Root cause — the thin-cell / early-shift hypothesis is REFUTED

Three independent probes converge on a different mechanism:

1. **The pool aggregate is clean.** Pool WD syn-vs-obs (n_syn=18,423, n_obs=45,638):
   max 1.21 pp, 0 slots > 3 pp. The gap appears only in the matched frame.
2. **The gap is entirely within-cell, not compositional.** Tier-2-cell (AGEGRP×SEX×LFTAG×PR)
   decomposition of the −3.30 pp mean gap over the 6 slots: **within-cell −3.35 pp,
   composition +0.05 pp**. The syn-donor and obs-donor recipients sit in essentially the same
   demographic cells; the *diaries drawn inside those cells* differ.
3. **The pool's own cell-conditional means predict the gap.** Reweighting pool cell-conditional
   syn/obs means by the matched frame's cell weights predicts a **−3.69 pp** gap vs the actual
   **−3.30 pp** (coverage 98.5/99.8%). I.e. the matcher reproduces, faithfully and by
   construction (i.i.d. within-cell draws), a discrepancy that already exists in the Step-4
   pool *conditional on demographics*.

**Mechanism:** inside employed working-age cells (LFTAG=1, AGEGRP 2–5, Ontario/Quebec
especially), the Step-4 synthetic diaries have 3–9 pp lower AT_HOME at the transition slots
than observed diaries in the *same* cells (e.g. cell 5|2|1|2: pool syn 33.3% vs obs 42.2%,
−8.9 pp). The pool **aggregate** hides this because opposite-signed cells (e.g. Prairies
+ cells: 2|2|1|4 +0.25 pp contribution) cancel, and because the pool is only 53.7% employed.
The census frame is **94.3% employed** — matching to census demographics concentrates weight
exactly on the discrepant cells, surfacing the conditional gap.

**Thin cells are NOT the driver:** 54.7% of WD rows resolve in broadened (<15-donor) cells,
but the top-5 thinnest gap-direction cells contribute ≤0.023 pp each; the top contributors
are *large* cells (pool T2 n = 268–1,276). Thin-cell (broadened) syn rows do sit slightly
lower (32.89% vs 34.88% at failing slots) but this is second-order.

Top contributing Tier-2 cells (signed contribution to the −3.30 pp gap, mean over the 6
failing slots; cell = AGEGRP|SEX|LFTAG|PR):

| Cell | n_syn | n_obs | m_syn % | m_obs % | contrib pp | pool T2 n |
|---|---|---|---|---|---|---|
| 5\|2\|1\|3 | 227 | 619 | 28.9 | 39.1 | −0.479 | 886 |
| 5\|2\|1\|2 | 164 | 473 | 29.5 | 39.6 | −0.410 | 546 |
| 4\|2\|1\|2 | 162 | 467 | 30.5 | 36.4 | −0.280 | 853 |
| 2\|1\|1\|2 | 121 | 363 | 22.6 | 30.6 | −0.264 | 561 |
| 1\|2\|1\|2 | 57 | 227 | 28.4 | 35.5 | −0.252 | 268 |

### 3. Option assessment

- **Option 2 (WD-only MIN_POOL / stratum-targeted broadening): will not work.** Broadening
  changes *which cell* donors come from; the gap is *within-cell* diary content. This is
  consistent with the observed sweep plateau (2.2 never crosses 3.0 at any MIN_POOL). No
  further sweep run — the mechanism evidence makes it moot.
- **Option 3 (shift-composition reweighting of `np.random.choice`): not defensible.** The
  early-riser mix is not the mechanism, and weighting draws by morning-departure behaviour
  would deliberately bias the donor distribution to mask a Step-4 generation artifact —
  exactly the donor-distribution bias the paper must not carry silently.
- **Option 1 (identify slots + cells): done above.**
- **Option 4 (document): RECOMMENDED.** The residual is a Step-4 property (cell-conditional
  syn-vs-obs discrepancy), definitionally out of reach of any Step-5 matcher lever. The real
  fix, if ever wanted, is Step-4-side: conditional calibration of synthetic AT_HOME by
  employment×age cell (a raking-target extension) — retrain-scoped, separate manager decision.

### 4. Proposed caveat text

> Gate 2.2 (AT_HOME within-day-type) retains a weekday residual of 3.66 pp across 6 of 96
> slots (08:30–10:00, 12:00–12:30, 16:30–17:30; weekend clean at 2.17 pp / 0 slots). The
> residual is not a matching artifact: decomposition shows it is a within-cell property of the
> Step-4 augmented pool, whose synthetic diaries carry slightly lower daytime home-presence
> than observed diaries conditional on employed working-age cells; the census frame's higher
> employment share (94% vs 54% in the survey pool) surfaces this conditional discrepancy,
> which cancels in the pool aggregate. The gate threshold was not relaxed; the residual is
> documented and bounded (< 3.7 pp, 6/96 slots).

---

## FAIL 2 — Gate R1 AT_RETAIL matched-vs-pool (4.796 pp, 2005-d2)

### 1. Localization (worst group 2005-d2, n_out=1,455 vs n_pool=19,221)

Deviation is **positive** (matched frame has MORE retail than the pool), concentrated in
Saturday late morning: slots 12–16 (09:30–12:00) all exceed +3 pp, peak **+4.796 pp at slot
14 (10:30–11:00)**; the whole 09:00–16:00 band is +1.4 to +4.8 pp.

**Magnitude-vs-shape verdict: BOTH, dominated by shape/timing.** Daily-mean offset
+1.04 pp (matched 4.08% vs pool 3.04%); after removing the uniform offset a +3.75 pp shape
surplus remains at late morning. Diurnal correlation 0.989 (same curve, amplified and
morning-peaked).

Note the prompt's "weekend-only" framing is incomplete: **6 of 12 groups exceed 3 pp**,
including two large weekday groups (2015-d1 3.024 @ n=5,388; 2022-d1 3.272 @ n=4,058).

### 2. Small-sample check: the FAIL is NOT sampling noise

- **Null test** (matched group as a random n_out draw from its pool group, B=1,000 per
  group): P(max|dev| ≥ 3.0) ≤ 0.012 in every group; for 2005-d2, null p50 = 1.27 pp,
  p95 = 2.09 pp, P(≥ 4.796) = 0.000.
- **Matched-side bootstrap** (B=2,000): worst-slot matched mean 14.02% with 95% CI
  [12.30, 15.88] — pool 9.22% far outside; the group max|dev| statistic has 95% CI
  [3.35, 6.79] pp, entirely above patterns explainable at the 3.0 line by chance.
  Donor reuse is mild (1,324 unique donors, effective n ≈ 1,216 of 1,455).

### 3. What it actually is: the census demographic reweighting itself

Reweighting each pool group's retail diurnal by the matched frame's Tier-2 cell weights
collapses the deviation in **every** group (cell coverage 98–99%):

| Group | raw max\|dev\| | after demographic reweighting |
|---|---|---|
| 2005-d2 | 4.796 | **2.268** |
| 2010-d2 | 4.020 | 1.293 |
| 2010-d3 | 3.529 | 1.419 |
| 2015-d1 | 3.024 | 0.620 |
| 2015-d2 | 3.213 | 1.236 |
| 2022-d1 | 3.272 | 0.559 |

All 12 groups fall below 3.0 (max 2.27) once the pool reference carries the matched frame's
demographic mix. The driver is the employment/age shift (matched 94% employed / 0.5% AGEGRP-7
vs pool 54% / 10.3%): employed working-age people shop more Saturday late-morning and less
weekday-midday. **R1 compares a census-weighted output against the raw survey-pool marginal,
so it structurally penalizes the very reweighting the matcher exists to perform.** The
conditional (per-cell) retail behaviour is transferred faithfully.

### 4. R2a under-representation (0.0251 vs band 0.06–0.10): two stacked causes

- **The pool itself is below band**: pool WD 12:00–14:00 AT_RETAIL = **0.0465** (obs-GSS
  0.0469, synthetic 0.0453). No matcher can exceed what the donors carry — even a perfect
  pool-marginal match would sit at 0.047, still WARN.
- Census reweighting (worker-heavy frame, at work at midday) lowers it further to 0.0251.

### 5. Retail v2 (multi-archetype) — scope only

A respondent-level retail archetype (mirroring the office NOC archetype; signal would come
from NOCS 6 sales occupations + NAICS retail industry of donors) would add *heterogeneity*
(who staffs vs who visits retail) but would **not** move R1 (demographic-reweighting effect,
archetype-orthogonal) and would **not** lift R2a magnitude (pool-level ceiling 0.047). An R2a
fix requires an external magnitude calibration target (e.g. retail-footfall/dwell data) at
Step-4 or as a BEM-side multiplier. Effort: medium (new lookup + carry-through + gates);
benefit for these two gates: near zero. Separate decision; do not build for this.

### 6. Recommendation

**Option 4 — document as a v1 limitation, with the reweighting evidence attached.** Not
option 2's "noise" disposition (bootstrap refutes it). Optionally (manager decision, NOT
taken here): redefine R1's reference as the demographically-reweighted pool — that is a gate
*redefinition*, distinct from relaxing the 3.0 threshold, and is exactly what the reweighting
column above would formalize. Flagged, not implemented.

### 7. Proposed caveat text

> Gate R1 (AT_RETAIL matched-vs-pool by cycle×stratum) reads 4.80 pp at worst (2005 Saturday,
> late morning). Bootstrap analysis rules out small-sample noise; instead, the deviation is
> the census demographic reweighting itself: re-referencing each pool group to the matched
> frame's demographic mix reduces every group below 3 pp (worst 2.27 pp). The retail channel's
> conditional behaviour is transferred faithfully; the marginal deviation reflects the
> census frame's higher employment share versus the survey pool. Relatedly, midday weekday
> retail presence (R2a, 0.025 vs. empirical band 0.06–0.10) is bounded above by the GSS-diary
> pool itself (0.047) — a single-archetype retail-v1 magnitude limitation, not a matching
> loss. No gate threshold was changed.

---

## FAIL 3 — Gate 0.1 PR census⊆pool (PR=6 Territories, 83.3% overlap)

### 1. Exposure quantified (exact, verified)

- **24 census agents** carry PR=6 (Territories) — **0.079%** of the 30,273-row frame.
  0 of them are in `excluded_pids.csv`. Day-types: d1=16, d2=4, d3=4.
- **All 24 resolve at Tier-3 `3_Constraints`** (AGEGRP×SEX×DDAY — the first tier that drops
  PR). None reach FailSafe; connectivity-audit FAIL only, matching succeeds.
- **Donor attribution is exact, not sampled:** the production match was reproduced
  in-memory (seed 42, MIN_POOL=15) and verified **30,273/30,273 identical** to the saved
  `Matched_Keys.csv` (occID, tier, DDAY all equal; `probe3` log). The 24 donors, read off
  `_pool_idx`:

| Donor region | n | share |
|---|---|---|
| Ontario | 7 | 29.2% |
| Prairies | 7 | 29.2% |
| Quebec | 5 | 20.8% |
| BC | 3 | 12.5% |
| Atlantic | 2 | 8.3% |

  24 unique donors (no reuse); 11 observed-GSS / 13 synthetic; cycles 2005×6, 2010×7,
  2015×4, 2022×7. (An earlier `occID`-join attribution in `INVESTIGATION_run.log` §3.3 is
  unreliable — occIDs are non-unique across pool rows — and is superseded by this table.)

### 2. Is the substitution defensible?

Yes. Because Tier-3 keys exclude PR entirely, PR=6 agents draw from the **national pool
within their age×sex×day-type cell** — the fallback silently substitutes a
population-proportional national mix (table above ≈ national region shares), not an
arbitrary single province. At n=24 this is the least-assumption behaviour available.

### 3. Option assessment

- **Option 2 (explicit nearest-province proxy):** over-engineering for 24 rows; would
  *replace* a national-mix draw with a hand-picked province (which one is "nearest" to
  Yukon vs Nunavut differs), adding a modeling assumption for no measurable gain.
- **Option 3 (exclude PR=6):** removes 24 rows → `Full_Schedules` 30,273 → **30,249**,
  `excluded_pids` 771 → 795, and every downstream paper count changes for a 0.08% purity
  gain. Not worth destabilizing the cited frame number.
- **Option 4 (accept + document): RECOMMENDED** — Leg-2 precedent; this is the only FAIL of
  the three that is definitionally unfixable by matching (GSS has no Territories diaries).
  Gate 0.1 will continue to FAIL by construction; it stays as an honest connectivity audit.

### 4. Proposed caveat text

> The GSS time-use frame does not sample the Territories, so the Section-0 connectivity
> audit reports an unavoidable PR domain gap (census⊆pool 83.3%). Exactly 24 census agents
> (0.08% of 30,273) are affected; all resolve at the demographic fallback tier that omits
> province, drawing donors population-proportionally from the national pool (verified donor
> audit: 7 Ontario, 7 Prairies, 5 Quebec, 3 BC, 2 Atlantic). Territories-specific schedule
> behaviour is therefore not represented; at 0.08% of the frame this does not affect any
> reported aggregate. The audit gate was intentionally left failing rather than masked.

---

## Summary

| FAIL | Recommended disposition | One-line rationale |
|---|---|---|
| 2.2 AT_HOME WD (3.66 pp, 6 slots) | **Document as residual** (Step-4-side fix = separate retrain decision) | Gap is the pool's own cell-conditional syn-vs-obs discrepancy in employed working-age cells, reproduced faithfully by the matcher; no Step-5 lever (broadening/reweighting) touches a within-cell property |
| R1 AT_RETAIL (4.796 pp, 2005-d2) | **Document as v1 limitation**; optional R1 reference redefinition = manager decision | Not noise (null p ≤ 0.001); deviation is the intended census demographic reweighting — reweighted pool reference puts all 12 groups < 3 pp (worst 2.27) |
| 0.1 PR=6 Territories (83.3%) | **Accept + document frame gap** (Leg-2 precedent) | 24 agents (0.08%), all Tier-3, national population-proportional donors (verified exactly); definitionally unfixable — GSS never sampled Territories |

**Guardrails:** matcher + validator untouched; MIN_POOL=15 live default untouched; no gate
threshold changed; all load-bearing numbers re-derived from `Full_Schedules.csv`,
`Matched_Keys.csv`, `excluded_pids.csv`, the locked pool, and `Aligned_Census_2025.csv`
(not from logs). Big-file reads stayed inside the analysis scripts; only aggregate tables
returned. Step 6 not advanced.
