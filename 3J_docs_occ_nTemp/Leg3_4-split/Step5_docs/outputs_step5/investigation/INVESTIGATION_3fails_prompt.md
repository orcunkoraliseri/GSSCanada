# Step-5 (3J Leg-3, 4-split) — Investigation prompt: the 3 residual FAILs

**Role:** You are the employee. Execute the investigation below and append a Progress Log entry
(to `3rdJ_05_censusLinkage_4split_val.md`) on completion. This is a **diagnostic + options-scoping**
task — do NOT change the production matcher or relax any gate without an explicit follow-up manager
instruction. Where a lever is worth testing, test it on a **copy / env-var sweep** and report numbers;
do not overwrite the live winner (MIN_POOL=15).

**Runs LOCALLY on Windows** (no cluster, no sbatch). Invoke Python with `py -3 -X utf8 <script>`
(the Delta-D audit prints a `⊆` glyph that crashes under cp1252).

---

## 0. Current state (frozen reference — do not re-run to establish this)

Final chain: MIN_POOL=15, scorecard **32 PASS / 4 WARN / 3 FAIL**. `Full_Schedules.csv` = 30,273 rows,
`excluded_pids.csv` = 771 rows. Live script:
`3J_docs_occ_nTemp\Leg3_4-split\Step5_docs\3rdJ_05_censusLinkage_4split.py`, `run_slot_match()`,
`MIN_POOL = int(os.environ.get("STEP5_MIN_POOL", "15"))` (line ~411). Validator:
`3rdJ_05_censusLinkage_4split_val.py`. **Never relax a gate to clear a FAIL.**

The 3 FAILs, verbatim from `run_final_minpool15_valfull_2026-07-21.log`:

| # | Gate | Section | Observed | Threshold | Status |
|---|------|---------|----------|-----------|--------|
| 1 | 2.2 AT_HOME per-slot max diff (within-day-type) | §2 | **3.66 pp, 6 slots >±3pp** | 0 slots >±3pp | FAIL |
| 2 | R1 AT_RETAIL per-slot max dev (matched vs pool, by cycle×stratum) | §3r | **4.796 pp** | ≤3.0 (WARN 1–3) | FAIL |
| 3 | 0.1 PR census⊆pool overlap | §0 | **83.3%, missing=[6]** | 100% (subset) | FAIL |

---

## FAIL 1 — Gate 2.2 AT_HOME (residential channel)

### Definition (exact)
Validator `validate_at_home_consistency()`, lines ~441–470. For each day-type group
(**WD** = `DDAY_STRATA==1`, **WE** = `DDAY_STRATA∈{2,3}`), compute per-slot
`|mean(syn AT_HOME) − mean(obs AT_HOME)| × 100` over the 48 `hom30` slots, where
`syn = IS_SYNTHETIC==1`, `obs = IS_SYNTHETIC==0`. Concatenate WD+WE slot diffs;
gate = **0 slots may exceed ±3pp** (max also reported). Non-smoke → FAIL if any slot >3pp.

### Current breakdown (KEY — supersedes the stale "weekend artifact" note)
```
[2.2-WD] syn=6052,  obs=15506, max_diff=3.66pp, slots>3pp=6   ← the residual lives HERE
[2.2-WE] syn=7448,  obs=1267,  max_diff=2.17pp, slots>3pp=0   ← CLEAN after broadening
```
The MIN_POOL=15 broadening **cleaned the weekend** (was the worst offender pre-fix) and the residual
is now **6 weekday slots**. Note the sample asymmetry: obs WD is large (15,506) but obs WE is tiny
(1,267); syn is weekend-heavy (7,448 WE). Complementary check: **W1 AT_WORK WD is clean (2.05pp / 0
slots)** — so the failing AT_HOME weekday slots are NOT mirrored by AT_WORK; the "missing-from-home"
mass sits in some other state (transit / other activity), consistent with the morning
commute/get-ready window (worst slots historically 06:30–09:00 on the 04:00-origin clock).

### Root-cause hypothesis
Thin demographic×day-type candidate cells are shift-/early-riser-heavy in the observed pool; census
weekday agents drawn i.i.d. from those cells over-represent early-departure diaries, depressing
morning AT_HOME. Broadening (union next-coarser tier when cell < MIN_POOL) diluted this enough to
fix WE and cut WD from ~7pp to 3.66pp, but it plateaus above 3.0 (2.2 never crosses 3.0 at any
MIN_POOL — chasing it further = overfitting stochastic noise).

### Options to scope (report feasibility + a quick numeric probe where cheap)
1. **Identify the 6 failing WD slots + their driver cells.** Which `hom30` slot indices fail, what
   clock time (04:00-origin), and which Tier-2/Tier-3 cells contribute the census agents landing on
   the shift-heavy diaries. Deliverable: a 6-row table (slot, clock, syn%, obs%, Δpp) + the top-5
   thinnest contributing cells. **This is the core ask — do this first.**
2. **Stratum-targeted broadening.** Broaden only WD-thin cells (or raise MIN_POOL for WD only) instead
   of uniform MIN_POOL — WE is already clean, so uniform pressure may be wasted / re-perturbing.
   Probe: sweep a WD-only MIN_POOL variant, report 2.2 WD max_diff + W1 (must stay PASS).
3. **Shift-composition reweighting.** Within a resolved cell, weight `np.random.choice` by the
   observed early-shift vs day-shift mix (or down-weight diaries whose morning departure is extreme)
   rather than i.i.d. Assess whether this is defensible (does it bias the donor distribution the paper
   relies on?) before proposing.
4. **Accept as documented residual.** If 1–3 show the residual is an intrinsic thin-cell / small-obs-WE
   frame property (not a matcher bug), the honest disposition is: document 2.2 as a **weekday-morning
   thin-cell residual (3.66pp, 6 slots, WE clean), not gate-relaxed**. Provide the one-paragraph
   caveat text.

---

## FAIL 2 — Gate R1 AT_RETAIL (retail channel)

### Definition (exact)
Validator `validate_at_retail_consistency()`, lines ~709–740. For each `(CYCLE_YEAR, DDAY_STRATA)`
group present in BOTH matched output and pool, compute per-slot
`|mean(matched ret30) − mean(pool ret30)| × 100` over the 48 `ret30` slots; take the max per group;
gate metric = **max over all groups**. Thresholds: **≤1.0 PASS, 1–3 WARN, >3 FAIL**.

### Current breakdown (all 12 cycle×stratum groups)
```
2005 d1: 2.453   2005 d2: 4.796 ←max   2005 d3: 2.399
2010 d1: 2.926   2010 d2: 4.020        2010 d3: 3.529
2015 d1: 3.024   2015 d2: 3.213        2015 d3: 1.797
2022 d1: 3.272   2022 d2: 2.357        2022 d3: 2.440
```
Pattern: the FAILs cluster on **weekend strata (d2 = Saturday especially)** where the matched-output
n is small (n_out ≈ 800–1,455) against a large pool (n_pool ≈ 12k–19k). Also **R2a is WARN**: weekday
12:00–14:00 AT_RETAIL rate = **0.0251** vs expected band **0.06–0.10** → retail is materially
UNDER-represented in the matched frame overall (magnitude issue, not just shape).

### Root-cause hypothesis
Retail v1 has **no respondent-level archetype** (single "Retail Retail" population multiplier — see
§3r header comment, R4 guard confirms `retail_archetype` column absent by design). Combined with small
matched retail counts in weekend strata, the matched frame diverges from the pool's retail diurnal on
exactly the thin (weekend) groups, and sits low overall (R2a).

### Options to scope
1. **Localize the 4.796pp.** For 2005-d2 (and the other >3 groups), which `ret30` slots drive the max
   deviation, and is it a magnitude offset (matched retail uniformly lower) or a shape/timing mismatch?
   Deliverable: per-slot Δ curve for the worst group + a one-line "magnitude vs shape" verdict.
2. **Small-sample check.** Is the weekend-stratum FAIL a sampling-variance artifact of n_out≈800–1,455?
   Probe: bootstrap the matched weekend group's per-slot mean CI; if the 3.0 line is inside the CI,
   the FAIL is noise, not bias.
3. **Retail v2 (multi-archetype) — SCOPE ONLY, do not build.** Would a respondent-level retail
   archetype (mirroring the office NOC archetype) plausibly close R1 + lift R2a into band? Estimate
   effort and where the archetype signal would come from. Flag as a separate decision, not this task.
4. **Accept as documented v1 limitation.** If (2) shows it is largely small-sample weekend variance on
   a single-archetype channel, disposition: R1 = **retail-v1 CMA/single-archetype limitation, weekend
   small-n**, not gate-relaxed; provide caveat text + note R2a under-representation.

---

## FAIL 3 — Gate 0.1 PR census⊆pool (join-key connectivity)

### Definition (exact)
Validator `_validate_join_key_connectivity()` / Section 0, lines ~286–306. For each Tier-1 match key,
require `census_domain ⊆ pool_domain` (0 missing values). PR result:
`census_n=6, pool_n=5, missing=[6], overlap=83.3%` → FAIL because PR=**6 (Territories)** exists in the
Census frame but the GSS pool never sampled it.

### Root-cause
**Genuine frame gap, not a matcher bug.** GSS (all cycles) does not sample the Territories (PR=6);
the Census does contain PR=6 agents. This is structurally identical to the Leg-2 deferred FAIL. The
matcher already resolves these agents (they fall through to coarser tiers that drop PR), so it is a
*connectivity-audit* FAIL, not a matching failure — Section 1 shows 0 FailSafe, 99.74% Tier1+2.

### Options to scope
1. **Quantify the exposure.** How many census PID rows have PR=6? What tier do they currently match at,
   and what province do their donor diaries come from (i.e., what does the fallback silently substitute)?
   Deliverable: count + tier + donor-PR distribution for PR=6 agents. **Do this — it decides whether
   the substitution is defensible.**
2. **Explicit nearest-province fallback.** Instead of letting PR=6 fall through tiers to an arbitrary
   province, define a deliberate proxy (e.g., nearest sampled province / national pool) and document it.
   Modeling decision — scope only, flag for manager.
3. **Exclude PR=6 from the frame.** Drop Territories agents into `excluded_pids.csv` with reason
   "GSS frame gap (Territories never sampled)" and document coverage. Report how many rows that removes
   and whether any downstream count (30,273) the paper cites would change.
4. **Accept + document as frame gap** (Leg-2 precedent). Provide caveat text. Note this is the only
   one of the 3 that is *definitionally unfixable by matching* — GSS has no Territories diaries to match.

---

## Deliverables

Write findings to `outputs_step5\investigation\INVESTIGATION_3fails_findings.md`:
1. FAIL-1: 6-slot table + top thin cells + verdict (fixable-further vs documented residual) + which
   option you recommend.
2. FAIL-2: worst-group per-slot Δ + magnitude-vs-shape verdict + small-sample/bootstrap result +
   recommendation.
3. FAIL-3: PR=6 row count + tier + donor-PR distribution + recommendation.
4. A 3-row summary table: FAIL / recommended disposition (fix-lever to test | document-as-residual |
   defer to v2/decision) / one-line rationale.

Then append a short Progress Log entry to `3rdJ_05_censusLinkage_4split_val.md`.

## Guardrails
- Diagnostic only. **Do not modify** `3rdJ_05_censusLinkage_4split.py` production behaviour or the
  validator gates. Lever probes go through the `STEP5_MIN_POOL` env var or a scratch copy — never
  overwrite the MIN_POOL=15 live default.
- **Never relax a gate threshold to clear a FAIL.** Documenting an honest residual is allowed;
  changing `>3` to `>4` is not.
- Verify load-bearing numbers from the artifacts' own columns, not from logs.
- Big-file reads (the 418 MB / augmented pool) stay inside your own script's aggregation — return only
  small result tables.
- Report at the end; do NOT advance to Step 6.
