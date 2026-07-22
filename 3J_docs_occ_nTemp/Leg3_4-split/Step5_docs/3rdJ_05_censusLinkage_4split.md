# 3J Leg-3 — Step 5: Four-Channel Census–GSS Linkage (MAIN DOC)
### Carry `ret30` through the proven linkage unchanged · Retail = trivial single archetype · Hotel has no respondent-level archetype at all — runs LOCALLY

---

## 1. Aim

Extend the Leg-2 Census–GSS linkage to carry the third GSS channel: every matched diary now brings `act30 + hom30 + wrk30 + ret30 + 9 co-presence` onto its Census person. **The matching machinery is unchanged** — the 4-tier demographic fallback match, day-type assignment (5:1:1, seed 42), authority rules, and aggregation stages are ported verbatim; `ret30` rides through `expand_slot_schedules` exactly as `wrk30` does (channels are carried, never re-derived).

Archetype status per channel (pipeline STEP 5):
- **Residential** — ✅ DONE (Leg 1, unchanged): Census linkage → household assembly.
- **Office** — ✅ DONE (Leg 2, unchanged): NOCS → `office_archetype_lookup.csv`.
- **Retail** — ⚠️ PLANNED (Leg 3): the PNNL prototypes carry a **single "Retail Retail" archetype**, so v1 needs **no lookup**: one population-level `at_retail_fraction(t)` per cycle × DDAY_STRATA drives all retail Spaces. A grocery-vs-merchandise `retail_archetype_ID` is explicitly **deferred** (blocked anyway by the 2015/2022 single shopping bucket — Step 2A).
- **Hotel** — ⚠️ PLANNED (Leg 3, non-GSS): no respondent, no archetype; the multiplier is **province-level** (`PR ∈ {QC, AB}`) — nothing to link here.

## 2. Inputs

| Input | Path | Notes |
|---|---|---|
| Census agents | `0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv` | 30,273 linked rows (Leg-2 figure; re-verify at run) |
| Diary pool | `../Step4_docs/outputs_step4/sweep/<LOCKED_POOL>/augmented_diaries.csv` | the **Leg-3 locked pool** (with `ret30_*`) — never the Leg-2 pool |
| Office archetype lookup | `0_Occupancy/processed/office_archetype_lookup.csv` | reused verbatim |

> **⚠️ Frame discipline (Leg-2 lesson, memory-flagged).** Do **not** assume the Leg-2 frame constants (23,150 HH / 29,538 stock / 735 excluded) carry over — the Leg-3 pool is a different Step-4 artifact. **Re-derive every frame count from this run's own `Full_Aggregated` output** and record them in the Progress Log; verify the aggregate was regenerated from the same run's `Full_Schedules` (the internal-staleness bug: Leg-2's June aggregate disagreed with its own schedules on 43.7 % of rows). And when comparing frames across runs, **compare household-ID sets, never counts — a matching count is not a matching set** (the Leg-2 re-matching scare arose exactly from reading count-agreement as set-agreement); after every stage that touches only one channel, assert the other channels' columns byte-identical (`np.array_equal`), the Leg-2 04T guard pattern.

## 3. Method (Leg-3 deltas only — everything else verbatim Leg 2)

- **Delta A — channel carry-through:** add `ret30_001..048` to the carried column set in `expand_slot_schedules` and every schema list downstream (Full_Schedules ~248 → ~296 cols).
- **Delta B — aggregation semantics (5E):** `ret30` is a **per-person population-fraction channel — never HH-maxed** (same rule as `wrk30`; `hom30` alone is HH-max). The Step-7 retail product consumes the population-level weighted mean, not household aggregates.
- **Delta C — exclusion stage (5H):** unchanged (AT_HOME < 0.30 drop) — retail plays no role in exclusion.
- **Delta D — join-key connectivity audit (the PR-remap lesson):** before the full run, verify the domain overlap of **every** match key between census and the new pool (the Leg-2 PR coding mismatch silently confined matching to ~30 % of the pool while tier rates looked healthy). One diagnostic function, run in `--smoke`.
- **Delta E — validator:** new Section 3r (AT_RETAIL consistency, R1–R3) — see val doc.

Script: `3rdJ_05_censusLinkage_4split.py` with the Leg-2 CLI stages: `--smoke`, `--full`, `--aggregate`, `--bem`, `--exclusion`, `--regression`. Runs **LOCALLY** (no sbatch).

## 4. Expected result / test method

- **Expected:** all Leg-2 outputs regenerated under `outputs_step5/` with `ret30` columns present end-to-end (`3rdJ_25CEN_aug_Full_Schedules.csv`, `_Full_Aggregated.csv`, `_BEM_Schedules.csv`, `_excl` variants, `excluded_pids.csv`); inherited residential/office gates at Leg-2-comparable levels; new R-gates PASS (per-slot retail deviation small — retail is ~2 %-positive, so absolute deviations should be tiny).
- **Test:** `py -3 -X utf8` the stage chain (smoke → full → aggregate → bem → exclusion → validator, exact CLI in the val doc); target 0 new FAILs beyond the documented inherited ones; record the re-derived frame counts.

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description> (role)`; before/after tables; frame counts of record)*

### 2026-07-20 — Part 1: fork build + smoke gate — BLOCKED on Delta-D CMA finding (employee)

**Scope executed:** forked both Step-5 scripts from the LIVE Leg-2 base (confirmed
NOT an `archive/*_pre*` predecessor), applied Deltas A-E, ran `--smoke` on the main
script only. Validator `--smoke` could NOT run (see below). Did not touch
`--full/--aggregate/--bem/--exclusion`, per scope.

**Files created:**
- `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.py` (forked
  from `Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split.py`, 1200→~1345 lines)
- `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.py`
  (forked from `Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split_val.py`,
  923→~1195 lines)

**Pool provenance of record:**
- Path: `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv`
- Rows: 192,183 (192,184 lines incl. header) — matches spec exactly
- md5: `ebb1dfe8d678744415ce0852dc77147f` — matches spec exactly
- `ret30_001..048`: confirmed 48/48 present before any run

**Deltas applied (functions/lines touched, in the Leg-3 fork):**
- **Delta A** (`expand_slot_schedules`, `run_linkage_smoke`, `run_linkage_full`):
  added `ret_cols` alongside `wrk_cols` in column selection, `_explicit_pool` set,
  and `pool_diary_cols`; mirrored every wrk30 presence print/assert with a ret30
  one in smoke schema checks, AT_RETAIL spot-check print, 5-agent spot-check
  (`ret[0:10]`), and the final DONE print; added a hard `assert not missing_ret`
  gate in smoke (stricter than the informational-only checks used for
  act/hom/wrk); mirrored the `wrk_cols[:3]` presence assert in `run_linkage_full`.
  Did NOT touch any act30/Rung-I logic (none found at the cited anchor in this
  script — that logic lives upstream in `3rdJ_04T_act_rake_2split.py`; ret30 was
  left to simply ride through `expand_slot_schedules` as specified).
- **Delta B** (`run_aggregate`): added a `ret30_*` 48-col presence assert on
  `df_agg`; updated the NOTE print to "wrk30 AND ret30 stay per-person (no HH
  aggregation of AT_WORK / AT_RETAIL)"; did NOT add ret30 to the `hom_cols`-only
  `groupby(...).max()`; added the optional `ret_mean` diurnal plot line.
- **Delta C** (`run_exclusion`): logic unchanged; added `ret30_*` 48-col presence
  asserts on both `sched_excl` and `agg_excl`.
- **Delta D** (NEW `audit_join_key_connectivity`, called inside `run_linkage_smoke`
  right after `_assign_dday` and before `run_slot_match`): per-key census⊆pool
  domain check for all 8 Tier-1 keys (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA,
  DDAY_STRATA) + Tier-1/Tier-2 pool-reachability share, using the module-level
  `_T1_KEYS`/`_T2_KEYS` and the (now module-level, moved out of
  `load_augmented_pool`) `_PROVINCE_TO_REGION` dict — no second hand-coded copy
  of the remap or key lists. Raises loudly on any <100% overlap, per spec.
- **Delta E** (validator fork): class renamed `CensusLinkageValidator4CH`;
  Sections 1,2,4,5,6 + Section 3 (W1-W4) kept verbatim; added `RET_COLS` to the
  `_sw`/`_aw`/`_bw` loader `usecols` sets (mechanical — no gate-logic change to
  the ported sections); added NEW Section 0 (`validate_join_key_connectivity`,
  reuses `MATCH_KEYS/_T1_KEYS/_T2_KEYS/_PROVINCE_TO_REGION` via a dynamic
  `importlib` load of the main script — one source of truth, no second remap
  copy) and NEW Section 3r (`validate_at_retail_consistency`, gates R1-R4);
  Section 0's table is surfaced as its own prominent HTML block (with a PASS/FAIL
  banner) directly under the scorecard, ahead of the pass/warn/fail badge lists.

**⚠️ Delta-D connectivity audit result — LOAD-BEARING FINDING, smoke run BLOCKED:**

```
KEY         census_n  pool_n  overlap%  census⊆pool
---------------------------------------------------
AGEGRP             7       7   100.00%  YES
SEX                2       2   100.00%  YES
MARSTH             3       6   100.00%  YES
HHSIZE             5       5   100.00%  YES
LFTAG              2       3   100.00%  YES
PR                 5       5   100.00%  YES
CMA                6       3     0.00%  NO  <-- missing [462, 535, 825, 835, 933, 999]
DDAY_STRATA        3       3   100.00%  YES

Pool rows reachable under Tier-1 (8-key) combos present in census: 0.00%  (n=0/192183)
Pool rows reachable under Tier-2 (5-key) combos present in census: 35.58%  (n=68385/192183)
```

7/8 keys are clean 100% overlap. **CMA is a hard domain mismatch, not a coding
quirk**: census `CMA` carries raw 3-digit StatCan CMA/CA codes (462=Montréal,
535=Toronto, 825=Calgary, 835=Edmonton, 933=Vancouver, 999=outside CMA/CA — from
`Aligned_Census_2025.csv`), while the GSS pool's `CMA` column is actually a
renamed `LUC_RST` urban/rural-size proxy (1=CMA pop 500k+, 2=CA 10k-100k,
3=Rural — confirmed via `eSim_dynamicML_mHead_alignment.py` and the
`16CEN15GSS_alignment.py` docstring). These are two different variables sharing
a column name — domain overlap is structurally 0%, not fixable by a simple
remap dict the way PR was.

Per the audit's own design ("FAIL loudly... this is exactly the Leg-2 bug class"),
`run_linkage_smoke()` raised `ValueError` immediately after printing the table,
before writing any output file (`outputs_step5/smoke/` confirmed empty). The
validator's `--smoke` therefore could NOT be run (no `Full_Schedules_smoke.csv`/
`Matched_Keys_smoke.csv` to read).

**This is not a new Leg-3 bug — it was already present and silently masked in
Leg-2.** Leg-2's own full-run match report
(`Leg2_2-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Validation_match.txt`)
shows **0% `1_Perfect` (Tier-1) matches**: 99.74% fell to `2_Core` (Tier-2, which
drops CMA from its key set) and 0.26% to `3_Constraints`. Tier rates looked
"healthy" (0% FailSafe) precisely because Tier-2's fallback silently absorbed
100% of the traffic that Tier-1 could never serve — the exact failure mode Delta
D was built to catch, just on CMA instead of PR, and 100% (not ~30%) unreachable.

A legacy `harmonize_cma()` exists in the pre-3J per-census-year scripts
(`eSim_occ_utils/21CEN22GSS/21CEN22GSS_alignment.py` ~L488-510, spec in
`eSim_occ_utils/docs_pipelines/21CEN22GSS_tasks.md` task C10) that collapses
census CMA `{462,535,825,835,933}→1, 999→2` against GSS `LUC_RST∈{1,2}` — but it
was never wired into the ML-era alignment (`eSim_dynamicML_mHead_alignment.py`
has `harmonize_pr()` only, no `harmonize_cma()`) or into either 3J census-linkage
script. Adopting it, changing the Tier-1/Tier-2 key definitions, or leaving CMA
out of the match keys entirely are all real options — this is a modeling decision
outside Part 1 scope, not something to silently pick.

**Status: Part 1 BLOCKED at the smoke gate, exactly at the checkpoint it was
designed to enforce.** Not proceeding to Part 2 or to any fix without a manager
decision on the CMA key. Reported back to the user per task instructions
("STOP and report back rather than deciding silently").

### 2026-07-20 — Part 1 re-run: CMA harmonization fix (binary metro/non-metro) — smoke gate GREEN (employee)

**Manager decision implemented exactly (binary, not 3-class):** both sides
harmonized to a **metro(1) / non-metro(2)** key via a new `harmonize_cma(df, side)`
helper, mirroring how `harmonize_pr()` / `_PROVINCE_TO_REGION` is wired.
- Census (`Aligned_Census_2025.csv`, raw StatCan 3-digit CMA/CA code):
  `{462 Montreal, 535 Toronto, 825 Calgary, 835 Edmonton, 933 Vancouver} → 1`;
  `999 (outside CMA/CA) → 2`. Any OTHER census CMA value observed at full-run
  scale is logged and mapped `→ 2` — does **not** raise (per spec).
- Pool (`CMA` = `LUC_RST` renamed, codes 1/2/3): `1 → 1`; `{2, 3} → 2`. Any
  value outside `{1,2,3}` DOES raise (pool's LUC_RST domain is fixed/known —
  an unmapped value there is real corruption, not an edge case). No pool rows
  dropped; rural (`LUC_RST=3`) folds into non-metro, full 192,183-row locked
  pool stays usable.
- `CMA_raw` (pre-harmonization value) preserved on both sides in-memory;
  carried through to `Full_Schedules` on the census side via `cen_extra` in
  `expand_slot_schedules` (nice-to-have, for the audit record).

**Root cause (unchanged from the blocking finding):** census `CMA` is the raw
StatCan code; the GSS pool's `CMA` column is `LUC_RST` (urban/rural size class)
renamed — two different variables sharing a column name, 0% domain overlap.
Not a Leg-3-introduced bug: it was already present and silently masked in
Leg-2 (Tier-2's key set drops CMA, so 100% of matches silently fell through to
Tier-2/3 while tier rates looked "healthy").

**Files touched:**
- `3rdJ_05_censusLinkage_4split.py` — added `_CMA_CENSUS_METRO_CODES`,
  `_CMA_POOL_TO_METRO`, `harmonize_cma()`; wired into `load_augmented_pool()`
  (pool side, before the WD/WE split), `run_linkage_smoke()` and
  `run_linkage_full()` (census side, right after dedup, before DDAY assignment
  and before the Delta-D audit); `CMA_raw` added to `expand_slot_schedules()`'s
  `cen_extra` carry list. `audit_join_key_connectivity()` docstring updated to
  note CMA now arrives pre-harmonized — no logic change needed there (it's
  generic over the key-domain sets it's given).
- `3rdJ_05_censusLinkage_4split_val.py` — imports `harmonize_cma` from the
  main script (`_main_mod`, same one-source-of-truth pattern as
  `_PROVINCE_TO_REGION`); applied to `cen_base` (census) and `df_pool_keys`
  (pool) inside `validate_join_key_connectivity()` (Section 0), before the
  per-key overlap table and Tier-1/Tier-2 reachability calc. Pool-side
  `ValueError` from `harmonize_cma` is caught and recorded as a validator
  `FAIL` (`0.1`) rather than crashing the report.
- Archived predecessors (both, since both were edited):
  `archive/3rdJ_05_censusLinkage_4split.2026-07-20_preCMAharmonize.py`,
  `archive/3rdJ_05_censusLinkage_4split_val.2026-07-20_preCMAharmonize.py`.

**Delta-D audit — NEW result (smoke, 303-agent 1% census sample vs 192,183-row pool):**

```
KEY         census_n  pool_n  overlap%  census⊆pool
---------------------------------------------------
AGEGRP             7       7   100.00%  YES
SEX                2       2   100.00%  YES
MARSTH             3       6   100.00%  YES
HHSIZE             5       5   100.00%  YES
LFTAG              2       3   100.00%  YES
PR                 5       5   100.00%  YES
CMA                2       2   100.00%  YES   <-- was 0.00% (6 vs 3, structural mismatch)
DDAY_STRATA        3       3   100.00%  YES

Pool rows reachable under Tier-1 (8-key exact) combos present in census: 2.31%  (n=4433/192183)
Pool rows reachable under Tier-2 (5-key) combos present in census: 35.58%  (n=68385/192183)
```

All 8 keys now clean (census ⊆ pool). **Tier-1 reachable: 0.00% → 2.31%**
(was mathematically impossible before — CMA domains never intersected, so
no Tier-1 8-key combo could ever match). Tier-2 reachable unchanged at
35.58% (expected: `_T2_KEYS` never included CMA, so the Tier-2 key set was
never affected by the CMA bug or its fix — Tier-2's value was always a
mask over the Tier-1 failure, not a result of Tier-1 domain state).

**Smoke match-tier distribution (main script, 303 sampled census agents):**
`1_Perfect: 253 (83.50%)`, `2_Core: 50 (16.50%)`, WD/WE FailSafe both 0.00%.
(For comparison: Leg-2's full-run report showed 0% Tier-1 / 99.74% Tier-2 —
CMA's 0% overlap meant Tier-1 could never fire at all. Post-fix, the smoke
sample resolves the large majority of agents at the tightest tier.)

**ret30 carry-through re-confirmed:** `ret30` cols 48/48 present in
`Full_Schedules_smoke.csv`, observed values `{0.0, 1.0}`, per-person (never
HH-maxed — `run_aggregate()`/Delta B untouched by this fix). Mean AT_RETAIL
1.16% across all smoke slots.

**Smoke-validator scorecard:** `22 PASS / 11 WARN / 1 FAIL`
(`3rdJ_step5_validation_report_smoke.html`). Section 0 (Join-Key Connectivity):
8/8 keys PASS (CMA now PASS, was blocking the whole run before). Tier-1/Tier-2
reachable share still flagged WARN (2.31%/35.58% < 95% gate) — expected at
smoke scale (1% census sample) and **not** a regression from this fix; the
95% gate is a full-run target, not a smoke-scale one. The 1 FAIL is
`R1 | AT_RETAIL per-slot max deviation (matched vs pool, by cycle x stratum):
24.299pp` — pre-existing Section 3r retail gate, unrelated to CMA/Delta-D
(this is the first time the validator has run to completion far enough to
surface it, since Delta-D previously blocked before any output existed to
validate). Not in scope for this fix; flagged for manager triage separately.

**Status: Part 1 re-run complete after CMA harmonization, awaiting manager
review before the full chain.** Not proceeding to `--full/--aggregate/--bem/
--exclusion`.

### 2026-07-20 — Full chain run (`--full`→`--aggregate`→`--bem`→`--exclusion`→validator) — BLOCKED on 2 new findings (employee)

**Scope executed:** all 5 stages run in order, locally, no errors/asserts raised at any stage. Full traceable log files: `run_full_main_2026-07-20.log`, `run_full_aggregate_2026-07-20.log`, `run_full_bem_2026-07-20.log`, `run_full_exclusion_2026-07-20.log`, `run_full_val_2026-07-20.log` (all in this dir).

**Output timestamps (regeneration-order check, all within one run window 19:47:31–19:48:21):** `Matched_Keys` → `Full_Schedules` → `Full_Aggregated` → `BEM_Schedules` → `excluded_pids` → `*_excl` variants, strictly increasing — no staleness.

**Frame counts of record — RE-DERIVED from this run's own output CSVs (not logged numbers):**
- Total matched persons (pre-exclusion, `Full_Schedules`/`Full_Aggregated`/`BEM_Schedules`): **30,273** (all three agree)
- Unique `SIM_HH_ID` pre-exclusion: **23,882**
- `excluded_pids.csv`: **648** persons excluded
- Post-exclusion rows (`*_excl`, all three): **29,625** — reconciles exactly (30,273 − 648 = 29,625)
- Unique `SIM_HH_ID` post-exclusion: **23,238**
- Set check: `set(PID_all) − set(PID_excluded) == set(PID_retained)` → **True** (exact set equality, not count-only)
- HH fully emptied by exclusion (0 members retained): **644** HH (of the 648 excluded persons, 4 belonged to multi-person HH whose other members survived — so 644, not 648, HH vanish entirely)
- These are **Leg-3-of-record counts** — do **not** reuse Leg-2's 23,150/29,538/735 constants; this is a different Step-4 artifact/pool.

**Byte-identity guard (04T pattern), verified directly from CSVs, not logs:**
- `wrk30`/`act30`/`ret30` (48 cols each): byte-identical (`np.array_equal`) between `Full_Schedules` and `Full_Aggregated` — confirms Delta B did not touch per-person channels.
- `hom30`: byte-identical between `Full_Schedules` and `Full_Aggregated` too (HH-max aggregation is a no-op at the byte level for this pool — not a bug, `[5E]` log confirms HH-max logic ran; every HH's members already agree on hom30 pre-aggregation).
- `hom30`/`wrk30`/`act30`: byte-identical between `Full_Schedules` and `BEM_Schedules` (Delta confirms 5F is a pure passthrough + schema check).
- `ret30`: present 48/48 in all of `Full_Schedules`/`Full_Aggregated`/`BEM_Schedules`, values ∈ {0,1}, per-person (never HH-maxed). Per-person mean **0.014953** identical in `Full_Schedules` and `Full_Aggregated` (diff = 0.00e+00) — matches validator gate R3 exactly.

**CMA-harmonization note:** binary metro(1)/non-metro(2) harmonization (from the prior smoke-gate fix) carried cleanly into the full run — census 30,273 rows split metro=12,295/non-metro=17,978; pool 192,183 rows split metro=146,397/non-metro=45,786. Section 0.1 CMA key: 100% overlap, PASS, as at smoke.

**Validator scorecard: 29 PASS / 4 WARN / 6 FAIL** (`3rdJ_step5_validation_report.html`, full-scale N=30,273).

**⚠️ BLOCKING — 2 new findings, not proceeding to declare Step 5 done, per task's explicit stop conditions:**

1. **R1 (AT_RETAIL) FAILs materially at full scale — the exact "not smoke noise" trigger.** Full-scale max deviation **5.548pp** (gate ≤3pp), driven by **cycle=2005, dday=2: n_out=1,407 / n_pool=19,221** — a well-populated cell, not the 4-person smoke artifact. (Smoke's FAIL was 24.299pp driven by a 4-person cell — genuinely noise; this is not that.) Other cells are close to or under gate (e.g. 2022/dday=3 at 1.355pp) but 5 of 12 cycle×dday cells exceed 3pp at full scale (2005/dday2=5.548, 2010/dday1=3.822, 2010/dday3=3.946, 2015/dday2=4.463, 2015/dday1=3.331). This indicates a real carry-through/aggregation issue in the retail channel, not sampling noise — needs manager triage before Step 5 is accepted.

2. **Section 0 join-key overlap: 2 new FAILs invisible at smoke scale.** `LFTAG` (66.7% overlap, census has value 99 the pool never carries) and `PR` (83.3% overlap, census has value 6/Territories the pool never carries) — both PASSED at smoke (303-row census subsample happened not to include either edge value). Root-caused (read-only lookup, not fixed):
   - `LFTAG=99` = census's literal "not-stated" sentinel; the pool's harmonization (`recode_lftag`) converts the equivalent per-cycle NS/RF/DK sentinels to `NaN` rather than a coded 99 — a **coding-convention mismatch**, not a missing population. Affects 10/30,273 census rows (0.03%).
   - `PR=6` = Territories (YT/NT/NU) region code; GSS has **zero territorial respondents in any cycle** (a genuine sample-frame gap, not a remap-dict defect — `_PROVINCE_TO_REGION` does map raw 60/61/62→6, the pool just never has those raw codes). Affects 24/30,273 census rows (0.08%).
   - Combined: 34/30,273 (0.11%) census rows structurally unmatchable on these keys — tiny in magnitude, but new-vs-smoke and same audit class as the CMA finding; flagging per Delta-D's own design rather than silently absorbing it.

3. **Section 2/3 residential+office gates: materially worse than the Leg-2 canonical full-run baseline (2026-07-15, `Leg2_2-split` `3rdJ_step5_validation_report.html`), not just "inherited at comparable magnitude":**
   | Gate | Leg-2 canonical full-run (2-split) | Leg-3 full-run (4-split, this run) | Δ |
   |---|---|---|---|
   | 2.2 AT_HOME per-slot max diff | 3.72pp / 5 slots — **FAIL** (documented sole FAIL) | 7.38pp / 21 slots — **FAIL** | ~2x worse |
   | W1 AT_WORK per-slot max diff | 2.74pp / 0 slots — **PASS** | 5.33pp / 19 slots — **FAIL** | PASS→FAIL, new |
   | W3 Colleagues co-presence | 2.675pp — **PASS** | 11.378pp — **FAIL** | PASS→FAIL, new, ~4x |

   Per the task's own instruction ("a materially worse value than the Leg-2 record is a new WARN, flag it") — W1 and W3 cross from PASS in Leg-2 to FAIL in Leg-3, and 2.2 nearly doubles. These are **not** the expected "inherited Step-4 FAIL at Leg-2-comparable magnitude" case; flagged as new, not declared done.

**Not blocking (acceptance-consistent):**
- Section 0 (7/8 keys, CMA): PASS as designed.
- R3 (ret30 per-person semantics, exact match) and R4 (retail_archetype absent): PASS.
- R2b (night retail rate): PASS. R2a (WD midday retail rate 0.0211 vs 0.06-0.10 band): WARN, same class as Leg-2 (not new).
- Sections 4, 5.1/5.3/5.4, 6: all PASS. 5.2 (mean N_HH_MEMBERS 1.500 vs Census ref ~2.80): WARN, pre-existing/expected shape (per-person retained schema — not a new regression).

**Status: full chain executed cleanly end-to-end (no crashes/asserts), all outputs regenerated and internally reconciled (byte-identity + set-equality guards all pass) — but Step 5 acceptance is BLOCKED pending manager decision on findings 1–3 above.** Not declaring Step 5 done. Reported to user per task instructions.

### 2026-07-20 — Diagnostic: root-cause of the 6 Step-5 FAILs (read-only, employee)

**Scope: read-only verification only.** No script, threshold, or output was modified.
All numbers below are re-derived directly from the artifacts' own columns (never
from a log). `py -3 -X utf8` used throughout, scratch scripts run locally against
`Full_Schedules` (30,273 rows), `Matched_Keys` (30,273 rows), the Leg-3 locked pool
(`seed_3_raked3_mindwell_actv/augmented_diaries.csv`, 192,183 rows), and
`Aligned_Census_2025.csv` (30,273 rows).

#### Cluster A+C — tier-regime hypothesis (CMA now live in Tier-1)

**Test A1 — full-scale tier distribution** (`Matched_Keys.csv`, N=30,273, cross-checked
identical against `Full_Schedules`):

| Tier | n | % |
|---|---|---|
| 1_Perfect (8-key, incl. CMA) | 24,905 | 82.27% |
| 2_Core (5-key, excl. CMA) | 5,288 | 17.47% |
| 3_Constraints (3-key) | 80 | 0.26% |
| 4_FailSafe | 0 | 0.00% |

Confirms full-scale echoes the 83.5%/16.5% smoke split — Tier-1 now fires for the
large majority, as expected post-CMA-fix.

**Test A2 — tier-split marginal deviation, TWO statistics computed:**

(a) Literal "matched-output-tier-subgroup mean vs full raw-pool mean," max abs diff
over 48 slots (the statistic the task specified; **not** the literal validator
formula for 2.2/W1/W3 — see caveat below):

| Channel | Tier-1 max-dev | non-Tier-1 max-dev | ALL max-dev |
|---|---|---|---|
| AT_HOME (hom30) | 22.900pp | 17.165pp | 21.883pp |
| AT_WORK (wrk30) | 28.164pp | 24.510pp | 27.466pp |
| AT_RETAIL (ret30) | 2.544pp | 2.504pp | 2.460pp |
| Colleagues co-presence | 9.908pp | 8.355pp | 9.603pp |

(b) **Corrected — the validator's ACTUAL gate statistic** for 2.2/W1/W3 is a
within-day-type SYN-origin-vs-OBS-origin split *of the matched output itself*
(`IS_SYNTHETIC` flag), **not** a matched-output-vs-pool comparison. Re-derived
formula per-channel and cross-checked exactly against the report before trusting
it: computed 7.384/5.329/11.378pp vs report's 7.38/5.33/11.38pp — exact match,
methodology confirmed correct. Tier-split using this TRUE gate statistic:

| Gate | Tier-1 (1_Perfect) | non-Tier-1 (2_Core+3_Constraints) | Gate threshold |
|---|---|---|---|
| 2.2 AT_HOME | 8.115pp | 6.649pp | ≤3pp |
| W1 AT_WORK | 6.570pp | 5.333pp | ≤3pp |
| W3 Colleagues | 11.480pp | 10.782pp | ≤3pp |

**These three gates REFUTE the tier-regime hypothesis.** non-Tier-1 persons — whose
match (Tier-2, 5-key) has **never** included CMA, in Leg-2 or Leg-3 alike — already
show deviations almost as large as Tier-1 (gap of only ~0.7–1.5pp between the two
subgroups), and BOTH subgroups individually blow through the 3pp gate on their own.
If CMA-driven stratification were the primary driver, non-Tier-1 should look close
to the Leg-2 record (2.2: 3.72pp / W1: 2.74pp PASS / W3: 2.675pp PASS) — it does not.
The evidence points to a SYN-vs-OBS composition gap that is a property of the Leg-3
pool itself (`seed_3_raked3_mindwell_actv`), independent of which match tier a
census person lands on.

**R1 (AT_RETAIL) is the exception — CONFIRMS the hypothesis.** R1's real gate
statistic (matched-output mean vs pool mean, grouped by cycle×stratum, max over 48
slots) is genuinely a matched-vs-pool comparison, unlike 2.2/W1/W3. See Test A4.

**Test A3 — carry-through fidelity.** `occID` exists in both `Matched_Keys` and
`Full_Schedules`, but is **not a unique diary-row pointer** — it is a many-to-one
base-GSS-respondent key: 192,183 pool rows share only 27,389 unique `occID` values
(avg 7.02 augmented variants per base respondent). The matcher's true unique row
selector (`_pool_idx`) is dropped before any output is written
(`df_matched.drop(columns=["_pool_idx"])`), so single-row byte-identity cannot be
re-derived from the output files alone. Corrected test: for 200 randomly sampled
matched persons, does their carried `wrk30`/`hom30`/`ret30` 48-vector match **any**
row within their `occID` group in the pool (the strongest carry-through check the
available columns support)? **Result: 200/200 (100%) matched exactly**
(`np.array_equal` on all three channels) — no scrambling detected. (A naive
first-row-of-group rejoin without this correction falsely showed only 29.5% —
an artifact of `occID` non-uniqueness, not a real defect; documented here so it
isn't misread later.)

**Test A4 — R1 driver cell under the tier lens** (cycle=2005, dday_strata=2,
n_out=1,407, n_pool=19,221):

| Subset | n | Retail max-dev |
|---|---|---|
| ALL persons in cell | 1,407 | 5.548pp (matches validator report exactly) |
| Tier-1 subset | 1,140 (81.0%) | 6.692pp |
| non-Tier-1 subset | 267 (19.0%) | 1.957pp |

Confirms the hypothesis cleanly for retail: restricting to non-Tier-1 persons in
the worst driver cell drops the deviation from FAIL territory (5.548pp/6.692pp)
to well under the 3pp gate (1.957pp) — the R1 FAIL is concentrated in the newly-live
Tier-1 (CMA-stratified) subset.

#### Cluster B — join-key gaps (PR=6, LFTAG=99)

**Test B1 — pre-existence in the same census input** (`Aligned_Census_2025.csv`,
raw, pre-harmonize, read directly — no Step-5 processing applied):

| Key/value | Count | 
|---|---|
| PR==6 | 24 |
| LFTAG==99 | 10 |

Exact match to the numbers in the prior full-chain finding. **Since Leg-2 used this
identical file** (`0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv`, unchanged),
these 24+10 rows existed in Leg-2's census input too — Leg-2 simply had no
Section-0-equivalent gate to measure/report them. This is a **newly-measured,
pre-existing condition**, not a Leg-3-introduced regression.

**Test B2 — resolved tier (graceful degradation check):**

| Group | n | Found in Matched_Keys | Found in Full_Schedules | Resolved tier |
|---|---|---|---|---|
| PR=6 persons | 24 | 24/24 | 24/24 | 100% → `3_Constraints` |
| LFTAG=99 persons | 10 | 10/10 | 10/10 | 100% → `3_Constraints` |

Zero silent drops (set-membership check, not count-only). Mechanism confirmed via
the key-tier definitions in `3rdJ_05_censusLinkage_4split.py`: `_T1_KEYS` (8-key)
and `_T2_KEYS` (`["AGEGRP","SEX","LFTAG","PR",DDAY_COL]`, line 86) both include
PR and/or LFTAG, so both groups fail Tier-1 and Tier-2 lookups; `_T3_KEYS`
(`["AGEGRP","SEX",DDAY_COL]`, line 87) excludes both PR and LFTAG, so they resolve
there — exactly the graceful-degradation path by design, not a bug.

**Test B3 — LFTAG harmonization asymmetry (the fixable part):**

Pool-side `recode_lftag()` (`Leg2_2-split/Step2_docs/3rdJ_02_harmonizeGSS_2split.py`
lines 103–144, reused verbatim by the Leg-3 Step-2/4 chain) maps every cycle's
not-stated/refusal/don't-know sentinel to `pd.NA`, never to a literal 99:

```python
if cycle in (2005, 2010):
    df["LFTAG"] = df["LFTAG"].replace({8: pd.NA, 9: pd.NA})
    ...
elif cycle == 2015:
    df["LFTAG"] = df["LFTAG"].replace({97: pd.NA, 98: pd.NA, 99: pd.NA})
    ...
elif cycle == 2022:
    df["LFTAG"] = df["LFTAG"].replace({9: pd.NA})
    ...
```

Census (`Aligned_Census_2025.csv`) instead keeps a **literal 99** for its
not-stated sentinel (confirmed directly: 10 rows, Test B1). This is a
coding-convention mismatch, not a missing population. Because
`audit_join_key_connectivity()` builds `cen_dom` via
`set(df_census[k].dropna().unique()...)` (script line 613), a one-line census-side
harmonization (`LFTAG 99 → NaN`, mirroring the pool's own convention) would make
those 10 rows drop out of `cen_dom` automatically — closing the Section-0 LFTAG
FAIL without changing any matching outcome (they already gracefully resolve to
`3_Constraints` either way, per Test B2). **This is the one Cluster-B item that is
a genuine one-line fix candidate**, not a frame limitation.

**PR=6 is different — not fixable the same way.** Census PR=6 (Territories:
YT/NT/NU) has **zero GSS respondents in any cycle, in either pool** — a real
sample-frame gap (`_PROVINCE_TO_REGION` at module scope does map raw StatCan
60/61/62→6 correctly; the pool simply never contains rows with those raw codes
because GSS never surveyed the territories). No remap or harmonization closes
this — the only options are to accept the Section-0 WARN/FAIL as a documented,
permanent frame-coverage caveat, or to explicitly carve PR=6 out of the Section-0
100%-subset requirement.

#### Manager-facing verdict

- **Cluster A+C: PARTIALLY CONFIRMED, channel-dependent — not a blanket "precision
  improvement, not a bug" story.**
  - **R1 (AT_RETAIL): CONFIRMED.** The FAIL is concentrated in the Tier-1
    (CMA-stratified) subset — restricting the worst driver cell to non-Tier-1
    persons drops the deviation from 6.69pp to 1.96pp (under the 3pp gate). The
    live CMA key is the direct cause here.
  - **2.2 (AT_HOME), W1 (AT_WORK), W3 (Colleagues): REFUTED.** Using the
    validator's actual gate statistic (SYN-vs-OBS split within the matched
    output, cross-checked to match the report exactly), non-Tier-1 persons —
    whose match key set has never included CMA — show deviations almost as large
    as Tier-1 (within ~1.5pp of each other), and both subgroups independently
    fail the 3pp gate. CMA/tier is not the explanation for these three; the
    evidence points to a SYN-vs-OBS composition property of the Leg-3 pool
    itself, which needs separate investigation (out of this diagnostic's scope).
  - Carry-through/assignment fidelity is clean: 200/200 sampled persons'
    wrk30/hom30/ret30 vectors byte-match their source pool diary exactly — no
    scrambling bug anywhere in the pipeline.
- **Cluster B: both PR=6 and LFTAG=99 are confirmed pre-existing in the SAME
  census input Leg-2 used** (newly measured by Section 0, not newly created).
  Both gracefully degrade to `3_Constraints` with zero silent drops. **LFTAG=99
  is fixable** (one-line census-side `99→NaN` harmonization, mirroring the pool's
  own `recode_lftag` convention, closes the Section-0 FAIL with no matching-outcome
  change). **PR=6 is a genuine frame gap** (GSS never sampled the Territories) —
  not fixable by remapping, only acceptable-and-documented or explicitly excluded
  from the Section-0 subset check.

### 2026-07-20 — Diagnostic 2: localizing the 2.2/W1/W3 SYN-vs-OBS divergence (read-only, employee)

**Scope: read-only verification only.** No script, threshold, or output was modified,
no pipeline stage was re-run. `py -3 -X utf8` used throughout; a scratch script
(`diag2_step5_localize.py`, run outside the repo) computed the validator's exact
within-day-type combined-max statistic (2.2/W1: per-slot |SYN mean − OBS mean|,
combined over WD-48 + WE-48 = 96 values, max/mean/count>3pp; W3: the validator's
own scalar mean-of-means-over-slots diff, WD vs WE, max of the two) against three
populations, plus a genuine per-slot breakdown for the colleagues channel (which
the validator itself never computes per-slot — see caveat below).

**P1 reproduction check** — computed max_diff = 7.384 / 5.329 / 11.378pp vs the
report's 7.38 / 5.33 / 11.38pp — exact match, statistic confirmed correct before
using it on P2/P3.

#### Results table

| Channel | P1 max | P1 daily-mean | P1 #slots>3pp (of 96) | P1 worst-slot | P2 max | P2 daily-mean | P3 max (Leg-2) |
|---|---|---|---|---|---|---|---|
| AT_HOME (hom30) | 7.38pp | 1.97pp | 21 | WE slot 10 → 08:30 | 1.21pp | 0.35pp | 3.72pp |
| AT_WORK (wrk30) | 5.33pp | 1.73pp | 19 | WE slot 8 → 07:30 | 0.69pp | 0.13pp | 2.74pp |
| Colleagues co-presence | 11.38pp¹ | 6.36pp² | 47² | WD slot 26 → 16:30² | 7.19pp¹ | 4.08pp² | 2.675pp |

¹ Colleagues' *official* gate stat (W3) is not a per-slot max — it's already a
scalar mean-of-means **across all 48 slots**, computed separately for WD/WE, then
maxed. So 11.38pp (P1) / 7.19pp (P2) are themselves daily-integrated averages, not
peak values. ² These columns are a genuine per-slot |SYN−OBS| array I computed
in addition (the validator never produces one for W3) — shown for comparability
with the 2.2/W1 tail analysis; not the official gate number.

P3 numbers independently re-derived from `Leg2_2-split/Step5_docs/outputs_step5/
3rdJ_25CEN_aug_Full_Schedules.csv` (not trusted from the existing
`run_val_20260715.log` alone): got 3.718 / 2.737 / 2.675pp — exact match to the
canonical log and to the number already in `3rdJ_05_censusLinkage_2split_val.md`.

**SYN/OBS shares:**

| Population | N | SYN (IS_SYNTHETIC=1) | OBS (IS_SYNTHETIC=0) |
|---|---|---|---|
| P1 Leg-3 matched frame | 30,273 | 13,729 (45.35%) | 16,544 (54.65%) |
| P2 Leg-3 raw pool | 192,183 | 128,122 (66.67%) | 64,061 (33.33%) |
| P3 Leg-2 matched frame | 30,273 | 13,571 (44.83%) | 16,702 (55.17%) |

Overall SYN/OBS share is similar Leg-2 vs Leg-3 (~45/55 either way) — the ratio
by itself is not the driver. The driver is the **within-day-type split**, which
diverges sharply between raw pool and matched frame:

| Group | Raw pool (P2) n | Matched frame (P1) n | Selection rate |
|---|---|---|---|
| OBS, Weekday (DDAY=1) | 45,638 | 15,233 | 33.4% |
| OBS, Weekend (DDAY∈{2,3}) | 18,423 | 1,311 | 7.1% |
| SYN, Weekday (DDAY=1) | 18,423 | 6,325 | 34.3% |
| SYN, Weekend (DDAY∈{2,3}) | 109,699 | 7,404 | 6.7% |

WD/WE selection rates are nearly identical between SYN and OBS (33.4% vs 34.3%;
7.1% vs 6.7%) — Step-5 matching is not differentially over/under-sampling SYN
vs OBS *within* a day-type. But the raw pool's OBS-weekend stratum is already
thin (18,423, only 28.8% of all 64,061 OBS rows, vs SYN-weekend at 109,699/
128,122 = 85.6%), so applying a similar ~7% selection rate to both crushes
OBS-weekend down to just **1,311** matched persons against **7,404** matched
SYN-weekend persons (5.6:1) — a demographically-conditioned draw from a thin
pool, not a uniform random subsample, so its mean is not guaranteed to track
the full 18,423-row pool mean.

#### Verdict

**AT_HOME (2.2) and AT_WORK (W1): cause (ii), frame-composition/reweighting
effect — not diary-fidelity.** P2 (raw pool, unweighted, no Step-5 matching
applied) is small and clean: 1.21pp / 0.69pp max, 0.35pp / 0.13pp daily-mean,
**0 slots >3pp for both channels** — SYN and OBS diaries are essentially
fidelity-matched before Step-5 ever touches them. P1 (matched frame) then jumps
5–8× to 7.38pp / 5.33pp. That jump is created entirely inside Step-5, and traces
to the thin/skewed OBS-weekend stratum documented above (1,311 matched persons,
demographically-conditioned selection from an already-thin 18,423-row raw pool).
This is a Step-5 frame property, not a Step-4 diary-fidelity problem.

**Colleagues (W3): a MIX, majority cause (iii) with cause (ii) on top.** P2's
own official-style scalar diff is already 7.19pp — well over the 3pp gate — with
*zero* Step-5 matching involved, so ~63% of P1's 11.38pp gap is a genuine,
pre-existing Step-4 diary-shape divergence between synthetic and observed
colleague co-presence (a real joint-rake trade-off on this channel). Step-5
matching adds the remaining ~4.2pp (same thin-OBS-weekend mechanism as above).
Strong corroboration that this is a real signal, not composition noise: the
worst slot is the **identical** slot/day-type in both P1 and P2 — WD slot 26
(16:30), a genuine weekday mid-afternoon hour, not a low-signal artifact slot.

**Cause (i) tail-artifact: a minor, entangled contributor for AT_HOME/AT_WORK
only, not applicable to Colleagues.** P1's daily-mean sits comfortably under
gate (1.97pp / 1.73pp vs the 3pp threshold) even though the max is 5.33–7.38pp,
so the "typical" slot is fine — but 19–21 of 96 slots (~20%) exceed 3pp, not
just 1–2 outliers, and that cluster is concentrated in the same thin
OBS-weekend stratum, so tail-inflation and frame-composition are intertwined
rather than separable causes here. Colleagues' *official* gate stat is already
a full-48-slot average (not a max), so cause (i) doesn't apply to it at all —
11.38pp is a real level shift, not a peak-slot spike.

**Benign for aggregate-daily BEM energy?** Likely yes for AT_HOME/AT_WORK — the
daily-mean deviations are modest (~2pp) and the gate-failing peaks sit in a
demographically thin weekend-observed stratum (n=1,311) at moderate-occupancy
transition hours (07:30/08:30), not the true daily occupancy peak, so
daily-integrated occupied-hours (what drives aggregate HVAC/plug loads) should
track much closer than the peak-slot statistic implies; Colleagues is less
clearly benign since ~63% of its gap is a real behavioral divergence at 16:30,
a genuine weekday afternoon occupancy hour, though its BEM impact is likely
secondary to AT_HOME/AT_WORK unless the pipeline explicitly modulates internal
gains by colleague co-presence.

### 2026-07-21 — g3fix-pool re-run + LFTAG 99->NaN fix (employee)

**Scope executed:** manager pre-applied two fixes (no script edits made by
employee): (1) pool repoint `seed_3_raked3_mindwell_actv` (md5 `ebb1dfe8...`)
→ `seed_3_g3fix_raked3_mindwell_actv` (md5 `47705ce8ee67f01296e96791a9ba008a`,
verified locally, 192,183 rows, 418,622,542 bytes) in the main script's
`POOL_PATH`; (2) new `harmonize_lftag_census()` (census `LFTAG 99 → NaN`,
mirrors pool's own `recode_lftag` not-stated convention) wired into both
`run_linkage_full`/`run_linkage_smoke` (main) and Section 0 (validator).
Both scripts `py_compile`-clean before running. Prior canonical report backed
up to `outputs_step5/3rdJ_step5_validation_report_preG3fix.html` (no prior
`.txt` existed). Ran the full 7-stage chain locally in exact order (smoke main
→ smoke val → full → aggregate → bem → exclusion → full val); **no stage
raised or asserted**; logs at `run_g3fix_<stage>_2026-07-21.log`.

**Harmonization log lines confirmed present** in both smoke and full runs:
`[harmonize_cma/census]`, `[harmonize_cma/pool]`,
`[harmonize_lftag_census] LFTAG 99 -> NaN on 10 census row(s)...`.
Smoke Delta-D audit: CMA 100% overlap, did not raise (all 8 keys 100% at
smoke scale, incl. LFTAG/PR — edge values not in the 303-row subsample).

**⚠️ Finding (read-only, not fixed, not a raise):** the **validator's own
`POOL_FILE` constant (line 50-53) was never repointed** — it still reads the
OLD pre-fix pool (`seed_3_raked3_mindwell_actv`, md5 `ebb1dfe8...`), used only
by Section 0 (connectivity audit) and Section 3r R1/R2 (matched-vs-pool
retail comparison), while the main script correctly used the g3fix pool
(md5 `47705ce8...`) for all of `--full/--aggregate/--bem/--exclusion`. This
does **not** appear to affect the numbers reported below — the g3fix delta
between the two pool files is 2 bytes, consistent with touching only
colleague-co-presence-related columns, not CMA/PR/LFTAG/retail — but it is a
provenance discrepancy flagged for the manager's review (W1/W3/2.2 gates are
computed from `Full_Schedules` alone via the `IS_SYNTHETIC` split, not from
`POOL_FILE`, so they are unaffected by this; R1/R2/Section-0 domain checks DO
read `POOL_FILE` directly and would be reading the wrong pool if it mattered).

**Frame counts — re-derived from this run's own output CSVs (`np.array_equal`/
set-based checks, not logs):**
- Total matched persons pre-exclusion: **30,273** — agree across
  `Full_Schedules`/`Full_Aggregated`/`BEM_Schedules` (all three: 30,273 rows,
  30,273 unique PID)
- Unique `SIM_HH_ID` pre-exclusion: **23,882** (all three agree)
- `excluded_pids.csv`: **648** persons
- Post-exclusion rows (`*_excl`, all three): **29,625** (30,273 − 648 = 29,625, reconciles)
- Unique `SIM_HH_ID` post-exclusion: **23,238**
- Set check: `set(PID_all) − set(PID_excluded) == set(PID_retained)` → **True**
- HH fully emptied by exclusion: **644**
- **Identical to the prior (pre-g3fix) full-run frame counts** — expected,
  since the g3fix pool change only touches colleague-co-presence generation,
  not household composition or match keys.
- Regeneration order (mtimes, strictly increasing): `Matched_Keys` (14:38:32)
  → `Full_Schedules` (14:38:37) → `Full_Aggregated` (14:38:48) →
  `BEM_Schedules` (14:39:03) → `excluded_pids` (14:39:09) → `*_excl` variants
  (14:39:14 → 14:39:26) — confirmed, no staleness.

**Byte-identity guards (all confirmed `True` via `np.array_equal`):**
- `wrk30`/`act30`/`ret30` (48 cols each): byte-identical `Full_Schedules` vs
  `Full_Aggregated`.
- `hom30`/`wrk30`/`act30`: byte-identical `Full_Schedules` vs `BEM_Schedules`.
- `ret30`: present 48/48 in all three, values `{0,1}` only, per-person mean
  identical `Full_Schedules`=`Full_Aggregated`=0.014953 (diff = 0.00e+00).

**Match-tier distribution (`Matched_Keys`, N=30,273):**
`1_Perfect 24,905 (82.27%) / 2_Core 5,288 (17.47%) / 3_Constraints 80 (0.26%) /
4_FailSafe 0` — identical to the pre-g3fix full run (matching unaffected).

**LFTAG=99 / PR=6 graceful-degradation re-check (set-membership, not count):**
Census `LFTAG==99`: 10 rows, **10/10 found in Matched_Keys, all → `3_Constraints`**.
Census `PR==6`: 24 rows, **24/24 found in Matched_Keys, all → `3_Constraints`**.
Zero silent drops — degradation path preserved post-fix.

**Validator scorecards:**
- Smoke: **23 PASS / 10 WARN / 1 FAIL**. W3 (Colleagues) **PASS at 2.730pp**
  (smoke, within-day-type max) — was the blocking 11.38pp-class FAIL pre-fix.
  R1 (retail) still FAIL at smoke scale (24.299pp, 4-person driver cell — same
  documented noise artifact as before, unrelated to this fix).
- Full: **31 PASS / 4 WARN / 4 FAIL**. Full breakdown below.

**W3/2.2/W1/R1 comparison table:**

| Gate | (a) prior un-fixed-pool Leg-3 run | (b) this g3fix run | (c) Leg-2 canonical | Cross PASS↔FAIL? |
|---|---|---|---|---|
| W3 (colleagues co-presence) | 11.38pp — **FAIL** | **0.208pp — PASS** | 2.675pp — PASS | **FAIL→PASS vs (a); still PASS vs (c), and better** |
| 2.2 (AT_HOME per-slot max) | 7.38pp — FAIL | 7.38pp — **FAIL (unchanged)** | 3.72pp — FAIL | No change either direction |
| W1 (AT_WORK per-slot max) | 5.33pp — FAIL | 5.33pp — **FAIL (unchanged)** | 2.74pp — PASS | No change vs (a); was already PASS→FAIL vs (c) pre-fix, unaffected by this fix |
| R1 (AT_RETAIL per-slot max, worst cell cycle=2005/dday=2, n_out=1407/n_pool=19,221) | 5.548pp — FAIL | 5.548pp — **FAIL (unchanged)** | N/A (no retail channel in Leg-2) | No change |

**Only W3 changed — exactly the target of this fix.** 2.2/W1/R1 are byte-for-byte
unchanged from the pre-g3fix run (expected: the g3fix pool only touched
colleague co-presence, and W1/2.2/R1's driver mechanisms — SYN-vs-OBS frame
composition for 2.2/W1, CMA-stratified Tier-1 subset for R1 — are untouched
by this fix, per the 2026-07-20 diagnostics).

**Section 0 (join-key connectivity) — full scale:**
`AGEGRP/SEX/MARSTH/HHSIZE/CMA/DDAY_STRATA` all 100% PASS (unchanged).
**LFTAG: 100% overlap — PASS** (was FAIL at 66.7% pre-fix — the fix's other
target, resolved). **PR: 83.3% overlap — FAIL, missing=[6]** (unchanged,
genuine frame gap — GSS never sampled the Territories, not fixable by
harmonization). Tier-1/Tier-2 pool-reachable share (0.2): 27.89%/56.77%, both
still WARN (<95% gate) — unaffected by either fix.

**Status: g3fix pool re-run + LFTAG fix COMPLETE, both applied fixes verified
working exactly as intended (W3 FAIL→PASS, LFTAG Section-0 FAIL→PASS), no new
regressions in any other gate, all frame/byte-identity/set-equality guards
hold. 2.2/W1/R1/PR remain FAIL/WARN at unchanged (pre-existing, documented)
magnitudes — not reclassified, per instruction. One provenance discrepancy
flagged (validator `POOL_FILE` not repointed) for manager review — did not
appear to change any reported number, but is a real staleness in the script
that the manager may want addressed. Not editing any script; reporting
factually.**

### 2026-07-21 — POOL_FILE staleness fix (manager)

Fixed the validator's hand-coded `POOL_FILE` (was still the pre-W3-fix
`seed_3_raked3_mindwell_actv`) to `_main_mod.FULL_POOL` (single source of
truth). Re-validated against g3fix: **31 PASS / 4 WARN / 4 FAIL, unchanged** —
staleness confirmed numerically inert (g3fix touched only `colleagues30`; no
POOL_FILE-reading gate depends on it). W3 0.208pp PASS, LFTAG 100% PASS, R1
5.548pp, PR 83.3% (missing=[6]). Remaining 4 FAILs (PR frame gap, 2.2/W1
frame-composition, R1 CMA-precision) held for manager/user disposition — none
reclassified. See val.md for detail.

### 2026-07-21 — Diagnostic 3: localizing the 2.2/W1 fixable lever (employee)

**Scope: read-only diagnostic.** No script, threshold, or production output modified.
`py -3 -X utf8` used throughout; all scratch work under
`AppData/Local/Temp/claude/.../scratchpad/diag3_step*.py` (outside the repo). Builds
directly on Diagnostic 2's finding ("Step-5 frame property, not Step-4 diary-fidelity")
by pinning down the *specific* Step-5 mechanism and testing counterfactual fixes.

**Reproduction check (must-pass before trusting anything downstream):** recomputed the
validator's exact within-day-type combined-max stat from production
`Full_Schedules.csv` → **AT_HOME 7.38pp / AT_WORK 5.33pp, 21/19 slots>3pp — exact match**
to the reported gate values.

**Clock-time correction:** diary slots are **04:00-origin** (`_val.py` line 81-83:
"Unrotated 04:00-origin diary: slots 1-8 = 04:00-08:00"), i.e. slot *i* → clock
`(04:00 + (i-1)×30min) mod 24h`, NOT the 00:00-origin convention `run_aggregate()`'s
plot labels use for cosmetic x-axis ticks. Under the correct convention the worst
slots are **06:30-09:00 (AT_HOME) / 07:00-09:30 (AT_WORK)**, matching Diagnostic 2's
already-established "WE slot 10 → 08:30 / WE slot 8 → 07:30" — a plausible early-shift
transition window, not overnight sleep hours.

#### A. Diary-reuse (matcher re-run for `_pool_idx`, 100% verified byte-identical to
production `Matched_Keys.csv` on occID/MATCH_TIER/DDAY_STRATA — see method note below)

| group | n_persons | n_distinct_diaries | reuse_max | reuse_mean | reuse_median |
|---|---|---|---|---|---|
| OBS-WD | 15,233 | 6,159 | 118 | 2.47 | 1.0 |
| SYN-WD | 6,325 | 2,538 | 79 | 2.49 | 1.0 |
| OBS-WE | 1,311 | 891 | 19 | **1.47** | 1.0 |
| SYN-WE | 7,404 | 5,027 | 30 | **1.47** | 1.0 |

**No smoking gun here** — OBS-WE's reuse ratio (1.47) is statistically indistinguishable
from SYN-WE's (1.47); top-10-reused-diary concentration is 8.8% (OBS-WE) vs 2.9%
(SYN-WE), elevated but not extreme. Aggregate reuse intensity is not the driver.

*Method:* the production module (`3rdJ_05_censusLinkage_4split.py`) was **imported
unmodified** via `importlib.util` and its own `load_augmented_pool()`/`run_slot_match()`
(seed 42, deterministic) re-run against the same locked pool + census to recover
`_pool_idx` (dropped before production writes `Matched_Keys.csv`). Verified
occID/MATCH_TIER/DDAY_STRATA match production **100.0000%** on all 30,273 rows before
using the rerun for anything. `build_office_archetype_lookup()` (the only function that
writes a production file) was deliberately never called.

#### B. Demographic coverage/skew (Tier-1 = 7 MATCH_KEYS, Tier-2 = AGEGRP/SEX/LFTAG/PR)

| Population (n) | Tier-1 top-5 share | Tier-1 top-10 share | Tier-2 top-5 share | Tier-2 top-10 share |
|---|---|---|---|---|
| OBS-WE matched (1,311) | 6.4% | 10.5% | 20.0% | 35.7% |
| SYN-WE matched (7,404) | 3.6% | 6.2% | 19.1% | 34.8% |
| Census-WE demand (8,715) | 3.5% | 6.0% | 18.7% | 34.3% |

**Mild, not extreme, concentration** — OBS-WE is ~2× more concentrated than SYN-WE/census
at Tier-1 (549 distinct cells over 1,311 persons — expected sparsity at n=1,311 over
7 keys), but at Tier-2 (the tier that actually governs most of the thin-cell fallback
behavior) OBS-WE/SYN-WE/census are **nearly identical** (18.7-20.0% top-5). Demographic-
cell skew alone does not explain a 5-8pp gap.

#### C. Per-slot localization (WD-48/WE-48 separate; worst 5 each; 04:00-origin clock)

| Channel/day-type | slot(clock) | slot(clock) | slot(clock) | slot(clock) | slot(clock) |
|---|---|---|---|---|---|
| AT_HOME-WD (max 4.68pp, 5>3pp) | 28(17:30) 4.68 | 29(18:00) 4.19 | 32(19:30) 4.18 | 33(20:00) 4.18 | 31(19:00) 4.06 |
| AT_HOME-WE (max **7.38pp**, 16>3pp) | 10(08:30) 7.38 | 9(08:00) 7.03 | 8(07:30) 5.96 | 7(07:00) 5.88 | 6(06:30) 5.14 |
| AT_WORK-WD (max 3.26pp, 4>3pp) | 28(17:30) 3.26 | 32(19:30) 3.22 | 33(20:00) 3.21 | 29(18:00) 3.15 | 34(20:30) 2.91 |
| AT_WORK-WE (max **5.33pp**, 15>3pp) | 8(07:30) 5.33 | 10(08:30) 5.11 | 7(07:00) 4.83 | 11(09:00) 4.69 | 12(09:30) 4.68 |

Confirmed **weekend-concentrated**: the combined-max driver is always a WE slot, and WE
supplies the large majority of failing slots (16/21 AT_HOME, 15/19 AT_WORK). A smaller,
mechanistically-distinct WD tail also exists (afternoon 17:30-20:30, both channels,
~3-4.7pp) — flagged as a secondary, out-of-scope residual (see verdict).

#### D. Counterfactuals

**D1 — post-stratify OBS-WE to census-WE Tier-2 distribution:** AT_HOME 7.38→6.26pp
(16→13 slots>3pp); AT_WORK 5.33→4.70pp (15→10 slots>3pp). **Helps, doesn't close the
gate** — consistent with B's finding that demographic skew is a minor contributor.

**D2 — bootstrap, is 7.38/5.33pp within OBS-WE(n=1,311) sampling noise?** Bootstrap
(B=2,000, resampling OBS-WE with replacement) 95% CI half-width at the worst slot is
only ~2.5pp (AT_HOME slot 10) / ~1.7pp (AT_WORK slot 8) — the SYN-WE reference mean
(n=7,404, treated as stable) falls **outside** the OBS-WE 95% CI at the worst slot, and
outside it for **52% of AT_HOME slots / 83% of AT_WORK slots** across the full 48.
Reverse check (randomly subsampling SYN-WE down to n=1,311, B=2,000): max deviation from
the full SYN-WE mean at the worst slots is only 4.29pp (AT_HOME)/1.97pp (AT_WORK), p95 =
2.23pp/1.13pp — well under the observed 7.38/5.33pp gaps. **Verdict: this is a real level
shift, not thin-sample noise.**

#### Follow-up: is the level shift a Step-4 (pool) or Step-5 (matcher) property?

Split the **raw pool itself** (pre-matching) by IS_SYNTHETIC × DDAY_STRATA, WE-only:
**AT_HOME 1.08pp / AT_WORK 0.40pp max diff, 0 slots>3pp** (n: OBS-WE=18,423,
SYN-WE=109,699) — reconciles exactly with Diagnostic 2's P2=1.21/0.69pp (which is the
WD/WE combined-max; my WD component independently reproduces 1.21/0.69pp too). **The
raw pool, split cleanly by day-type, is clean on WE alone** — the divergence does not
pre-exist in Step-4's pool composition.

Tested the specific mechanism: flagged raw-pool WE rows as "shift-like" (away from home
≥4 of 7 overnight/early slots, 02:30-05:30). Raw-pool OBS-WE shift-like base rate =
**18.59%**. In the **matched** OBS-WE frame: distinct-diary-level rate = **24.47%**,
person-weighted (reuse-inclusive) rate = **28.53%** — a real, ~10pp **enrichment**
of shift-like diaries created by Step-5's matching, on top of the raw pool's own rate.
Reweighting matched OBS-WE to correct only this one factor (shift-like share →
18.59%): **AT_WORK max diff 5.33→2.28pp, slots>3pp 15→0 (full PASS)**; **AT_HOME max
diff 7.38→4.80pp, slots>3pp 16→6** (residual — plausibly the separate WD-afternoon
mechanism noted in C, not covered by this flag). Root cause: per-Tier-2-cell OBS-WE
candidate pools are thin (median 7 candidates/cell; 131/340 cells ≤3 candidates) versus
much deeper SYN-WE candidate pools (109,699 raw rows, ~6:1 vs OBS-WE) — thin per-cell
candidate sets, combined with `np.random.choice`-with-replacement draws to satisfy
census weekend demand, mechanically amplify whatever composition (e.g. shift-worker
share) those few candidates happen to carry.

#### E. Lever verdict

**Primary lever: Step-5 matcher (not Step-4 pool composition, not a pure gate-design
artifact).** Evidence: (1) raw pool WE-only is clean (1.08pp/0.40pp, 0 slots>3pp) — Step-4
is not the source; (2) bootstrap rules out pure sampling noise (real level shift outside
the 95% CI on the majority of slots) — not a gate-design artifact; (3) a single,
mechanistically-identified selection-bias correction (shift-like enrichment, driven by
thin per-cell OBS-WE candidate pools) **fully resolves W1** (0 slots>3pp) and
substantially shrinks 2.2 (16→6 slots>3pp) — this is squarely inside Step-5's control
(the draw mechanism), not something only a bigger Step-4 pool could fix.

**Most-promising Phase-2 intervention:** in `run_slot_match()`, for OBS-origin
weekend-stratum cells where the demand:candidate ratio is high relative to a thin
candidate pool (e.g. Tier-2 cells with ≤10 raw OBS-WE candidates), either (a) cap
per-diary reuse (sample-without-replacement-then-cycle instead of unbounded
`np.random.choice`-with-replacement) or (b) broaden the OBS-side candidate pool for
those specific thin cells (e.g. relax PR/CMA within Tier-1/Tier-2 for OBS-only draws) so
within-cell composition variance shrinks toward the raw pool's true 18.6% shift-like
rate. Test by re-running the matcher with a reuse cap (e.g. max 3) applied only to
OBS-WE candidates and re-checking 2.2/W1; expect W1 → PASS and 2.2 to drop toward its
~4.8pp residual (driven by the separate WD-afternoon mechanism, still open).

### 2026-07-21 — Balanced round-robin matcher fix (2.2/W1) [employee]

**Scope executed:** implemented option (a) from Diagnostic 3's Phase-2 lever exactly
as specified — replaced `run_slot_match()`'s per-agent `np.random.choice(...)`
(i.i.d.-with-replacement) with a **balanced round-robin draw**: each cell's candidate
array is shuffled once (seeded, deterministic) inside `_build_index()`, then a new
`_draw()` helper cycles through it via a per-`(tier, key)` cursor (`arr[c % len(arr)]`,
`c` incremented each call) instead of drawing independently each time. This caps
per-donor reuse to `ceil(n_agents/n_candidates)` — the mathematical minimum forced by
pool thinness — for all four match tiers. 3 hunks in `run_slot_match()`; nothing else
in the file touched; `np.random.seed(42)` at function entry left as-is.
`py_compile` clean before running.

**Predecessor archived:** `archive/3rdJ_05_censusLinkage_4split.2026-07-21_preBalancedMatch.py`
(md5-confirmed byte-identical to the live script pre-edit).

**Full local chain re-run** (`--smoke` → val`--smoke` → `--full` → `--aggregate` →
`--bem` → `--exclusion` → val full), all 7 stages exit 0, no errors/asserts. Logs:
`run_balancedmatch_{smoke,smokeval,full,aggregate,bem,exclusion,val}_2026-07-21.log`.
`Full_Schedules.csv` regenerated at 30,273 rows (unchanged, matches spec).
`excluded_pids.csv`: 645 (was 648 pre-fix, −3 — expected: a few borderline
AT_HOME-exclusion outcomes shifted because different donor diaries are now assigned
to some agents).

**⚠️ Result: the fix did NOT resolve 2.2 or W1 — net full-scale scorecard is
UNCHANGED (31 PASS / 4 WARN / 4 FAIL, both before and after), and the two targeted
gates moved in different directions, neither crossing FAIL→PASS/WARN:**

| Gate | Before (g3fix run) | After (balanced round-robin) | Verdict |
|---|---|---|---|
| Full scorecard | 31P / 4W / 4F | 31P / 4W / 4F | **Unchanged tally** |
| 2.2 AT_HOME max diff (slots>3pp) | 7.38pp (21) — WD 4.68pp/5, WE 7.38pp/16 | 8.87pp (29) — WD 4.32pp/6, WE 8.87pp/23 | **FAIL, worse** |
| W1 AT_WORK max diff (slots>3pp) | 5.33pp (19) | 5.18pp (14) — WD 3.33pp/2, WE 5.18pp/12 | FAIL, marginally better, still FAIL |
| W3 Colleagues (must stay PASS) | 0.208pp — PASS | 0.470pp — PASS | Unaffected, still comfortably PASS |
| R1 AT_RETAIL (must be unchanged) | 5.548pp — FAIL | 6.133pp — FAIL | **Unexpectedly shifted** (see below) |
| PR (Section 0.1, must be unchanged) | 83.3% overlap, missing=[6] — FAIL | 83.3% overlap, missing=[6] — FAIL | Exactly unchanged, as required |

**Anomaly — R1 shifted despite being off-limits.** R1 (AT_RETAIL) is not touched by
this edit's logic, but its gate statistic is computed from the SAME `run_slot_match()`
donor draws (the matched-output-vs-pool comparison reads whichever row got drawn for
each agent, and `ret30` rides through on that same row). Changing the draw mechanism
for every tier therefore mechanically perturbs R1's composition too, even though no
retail-specific code was edited. R1 remains FAIL both before and after (no
reclassification), so the scorecard tally is unaffected, but the exact pp value is not
byte-identical to the pre-fix run — flagged since the task assumed R1 would be
untouched and that assumption does not hold structurally.

**Interpretation:** Diagnostic 3's counterfactual (reweighting matched OBS-WE to the
raw pool's true 18.59% shift-like rate) predicted W1 → 0 slots>3pp and 2.2 → 6
slots>3pp by correcting the *shift-like composition bias* directly. Balanced
round-robin instead enforces uniform per-candidate reuse within each cell — a
different correction (variance reduction under an assumed-uniform target), not a
targeted debias toward the pool's true shift-like rate. The full-scale result shows
this substitution is not equivalent: W1 improved only marginally (still FAIL) and 2.2
got worse. The two are not interchangeable fixes; round-robin uniformity does not
reproduce the shift-like-reweighting counterfactual's predicted effect.

**Determinism:** confirmed deterministic by construction — `np.random.seed(42)` fixes
the shuffle in `_build_index()`, `df_pool`/`df_census` row order is fixed per run, and
the round-robin cursor (`_cursors` dict, incremented per call) has no other source of
randomness. Re-running would reproduce byte-identical output; not re-run twice per
task instructions.

**Publishable-results note:** every donor assignment may differ from the pre-fix
matched output — this is expected, since the draw mechanism changed for all four
tiers, not just the thin weekend cells originally diagnosed.

**Status: fix applied exactly as specified, ran clean end-to-end, but did not achieve
the intended 2.2/W1 improvement at full scale — reported honestly per task
instructions. No gate relaxed, no script beyond the specified 3 hunks touched. Not
advancing to Step 6. Awaiting manager review of the R1 side-effect and the
non-improvement before further action.**

### 2026-07-21 — Thin-cell broadening matcher fix (2.2/W1 tier-asymmetry) [employee]

**Discarded:** the balanced round-robin matcher above (2.2 got worse, W1 only
marginally better) is REJECTED and archived as
`archive/3rdJ_05_censusLinkage_4split.2026-07-21_roundRobinRejected.py`. Reverted
the live script to the g3fix i.i.d. baseline
(`archive/3rdJ_05_censusLinkage_4split.2026-07-21_preBalancedMatch.py`, verified
by grep: `run_slot_match()` restored to four `np.random.choice(...)` calls, no
`_draw(`/`_cursors`/`np.random.shuffle`).

**New hypothesis (tier-asymmetry / thin-cell composition):** thin resolved cells
(few candidate donors) are intrinsically shift-heavy in the observed pool, so
census weekend agents mapped onto them over-represent early-shift diaries.
Fix: for a resolved cell with `< MIN_POOL` (=10) candidates, dilute it by
unioning in the next-coarser tier's candidate array (`np.unique(concatenate(...))`)
before the i.i.d. `np.random.choice` draw. Reported `MATCH_TIER` stays the
originally-resolved tier — only the candidate pool is broadened, not the tier
label. `np.random.seed(42)` at function entry unchanged. Implemented as a
`_candidates()` helper + edit inside `run_slot_match()`, applied to tiers
1/2/3 (tier 4 fail-safe has no coarser fallback).

Full local chain re-run (`--smoke` → val`--smoke` → `--full` → `--aggregate` →
`--bem` → `--exclusion` → val full), all 7 stages exit 0, no errors. Used
`py -3 -X utf8` (plain `py` hits a `UnicodeEncodeError` on the Delta-D
connectivity audit's `⊆` glyph under the Windows cp1252 console — same fix
noted in the val doc's 2026-07-20 entry). Logs:
`run_broaden_{smoke,smokeval,full,aggregate,bem,exclusion,val}_2026-07-21.log`.
`Full_Schedules.csv` regenerated at 30,273 rows (matches spec).

**Scorecard: 31 PASS / 4 WARN / 4 FAIL — same tally as the g3fix baseline.**
Both targeted gates improved substantially in both pp and failing-slot count,
but neither crossed FAIL→WARN/PASS:

| Gate | Before (g3fix baseline) | After (thin-cell broadening) | Disposition |
|---|---|---|---|
| Full scorecard | 31P / 4W / 4F | 31P / 4W / 4F | Unchanged tally |
| 2.2 AT_HOME max diff (slots>3pp) | 7.38pp (21) | 6.10pp (4) | **FAIL, but much improved** (−1.28pp, −17 slots) |
| W1 AT_WORK max diff (slots>3pp) | 5.33pp (19) | 3.13pp (1) | **FAIL, but much improved** (−2.20pp, −18 slots; now only 0.13pp over the 3pp gate) |
| W3 Colleagues (must stay PASS) | 0.208pp — PASS | 0.870pp — PASS | Held PASS, no regression |
| R1 AT_RETAIL (untouched, expect FAIL) | 5.548pp — FAIL | 4.402pp — FAIL | Still FAIL as expected (mild side-effect improvement, same mechanism as round-robin: shares `run_slot_match()` draws) |
| PR (Section 0.1, untouched, expect FAIL) | 83.3% overlap, missing=[6] — FAIL | 83.3% overlap, missing=[6] — FAIL | Exactly unchanged, as required |
| Delta-D Tier-1/Tier-2 reachability (0.2, WARN) | 27.89% / 56.77% | 27.89% / 56.77% | Exactly unchanged |

**Row counts:** `Full_Schedules.csv` 30,273 rows (matches spec, unchanged).
`excluded_pids.csv` 738 rows (was 648 pre-fix, +90) — donor assignments differ
under the broadened pool, shifting which agents land in the AT_HOME-exclusion
band; flagged, not treated as an error.

**Publishable results change: donor assignments differ from the g3fix
baseline** — expected, since candidate pools for thin cells (tiers 1–3) are now
broadened before the draw.

**Verdict — lever partially confirmed, not fully resolving:** per the task's
interpretation rule (judge by the validator; success = 2.2/W1 improve toward
PASS/WARN without regressing W3/other gates), this run is a **success on that
narrower bar** — both 2.2 and W1 moved substantially toward their gates (2.2's
failing-slot count fell 21→4; W1 is now only 0.13pp from passing) and W3 held
PASS with no other gate regressing. However, on the stricter bar of actually
flipping a FAIL to WARN/PASS, **neither gate crossed** — the full scorecard
tally is unchanged (31P/4W/4F) and 2.2/W1 remain FAIL. Exactly one swing taken
per instructions; MIN_POOL not tuned further. Not advancing to Step 6. Awaiting
manager review to decide whether "improved-but-still-FAIL" is accepted as this
task's resolution or whether a different lever is needed for full PASS/WARN.

### 2026-07-21 — MIN_POOL sweep + finalize (W1 crossing) [employee]

**Goal:** find the smallest `MIN_POOL` (thin-cell broadening threshold, see
2026-07-21 entry above) that flips W1 FAIL→PASS without regressing W3 or
introducing a genuine new FAIL, starting from the MIN_POOL=10 baseline
(31P/4W/4F; W1=3.13pp/1 slot, only 0.13pp over the 3.0pp gate).

**Setup:** archived the live MIN_POOL=10 script as
`archive/3rdJ_05_censusLinkage_4split.2026-07-21_broaden_minpool10.py`. Added
`import os` and parametrized the threshold:
`MIN_POOL = int(os.environ.get("STEP5_MIN_POOL", "10"))` so the sweep needed no
per-iteration code edit. Nothing else changed.

**Sweep (`--full` + val only, per instructions — aggregate/bem/exclusion skipped
to save time since they don't affect 2.2/W1/W3/R1):**

| MIN_POOL | 2.2 AT_HOME (pp / slots>3pp) | W1 AT_WORK (pp / slots) | W3 Colleagues (pp) | R1 AT_RETAIL (pp) |
|---|---|---|---|---|
| 10 (baseline) | 6.10 / 4 | 3.13 / 1 — **FAIL** | 0.870 — PASS | 4.402 — FAIL |
| **11** | 6.29 / 12 | **2.97 / 0 — PASS** | 0.751 — PASS | 5.511 — FAIL |
| 12 | 4.37 / 9 | 2.47 / 0 — PASS | 0.714 — PASS | 5.292 — FAIL |
| 15 | 3.66 / 6 | 2.05 / 0 — PASS | 0.888 — PASS | 4.796 — FAIL |
| 20 | 4.86 / 3 | 2.98 / 0 — PASS | 0.200 — PASS | 4.815 — FAIL |
| 30 | 5.78 / 9 | **3.81 / 1 — FAIL** | (not extracted) | 6.161 — FAIL |

Non-monotonic: W1 crosses to PASS at 11 and holds through 20, then relapses to
FAIL at 30 (over-broadening dilutes the pool too far). 12/15/20/30 tested per
the instructed order; since 12 was the smallest passing value in that list,
also tested 11 per the tie-down rule — 11 passes (2.97pp, the exact crossing
point) and W3 holds, so 11 is the winner (smallest passing integer).

**Sweep-only artifact (not a MIN_POOL regression):** every sweep val run shows
gate `R3` (`ret30` exact-match, Full_Schedules vs Full_Aggregated) as FAIL —
this is because `--aggregate` was intentionally skipped during the sweep
(Full_Aggregated.csv stays frozen at its MIN_POOL=10 content while
Full_Schedules.csv changes each iteration). Confirmed this is not a real
regression: R3 returns to PASS (0.00e+00 diff) in the Step-3 final run below
once `--aggregate` is rerun. Section 0.1 PR (FAIL, untouched) and Section 0.2
Delta-D Tier-1/Tier-2 reachability (27.89%/56.77% WARN) are unchanged across
every MIN_POOL tested — no other gate regressed.

**Winner: MIN_POOL = 11.** Hardcoded as the new default (env override
mechanism kept): `MIN_POOL = int(os.environ.get("STEP5_MIN_POOL", "11"))`.
`STEP5_MIN_POOL` cleared from the shell before the final run.

**Final run — complete 7-stage chain, MIN_POOL=11 default, env var unset:**
smoke -> val(smoke) -> full -> aggregate -> bem -> exclusion -> val(full), all
7 stages exit 0. Used `py -3 -X utf8` throughout (plain `py` hits
`UnicodeEncodeError` on the Delta-D `⊆` glyph under Windows cp1252). Logs:
`run_final_minpool11_{smoke,valsmoke,full,aggregate,bem,exclusion,valfull}_2026-07-21.log`.

**Final scorecard: 32 PASS / 4 WARN / 3 FAIL** (was 31P/4W/4F at the MIN_POOL=10
baseline — net +1 PASS / −1 FAIL, W1 crossed):
- 2.2 AT_HOME: 6.29pp, 12 slots>3pp — FAIL (pre-existing FAIL category, not new)
- **W1 AT_WORK: 2.97pp, 0 slots>3pp — PASS** (crossed FAIL→PASS)
- W3 Colleagues: 0.751pp — PASS (held, no regression)
- R1 AT_RETAIL: 5.511pp — FAIL (pre-existing FAIL category, untouched per instructions)
- R3 ret30 exact-match: PASS, diff=0.00e+00 (confirms sweep-time FAIL was staleness only)
- PR (Section 0.1): 83.3% overlap, missing=[6] — FAIL (left untouched, as instructed)
- Delta-D 0.2: Tier-1 27.89% / Tier-2 56.77% — WARN (unchanged)

**Row counts:** `Full_Schedules.csv` 30,273 rows (matches spec). `excluded_pids.csv`
766 rows (was 738 at the MIN_POOL=10 broadening baseline, +28 — donor
reassignment under the wider pool shifts which agents land in the
AT_HOME-exclusion band).

**Archived predecessor:**
`archive/3rdJ_05_censusLinkage_4split.2026-07-21_broaden_minpool10.py`.

**Publishable results change: donor assignments differ from the MIN_POOL=10
version** — expected, since MIN_POOL=11's broadened candidate pools change
which donor diary each census agent draws.

Not advancing to Step 6 per instructions.

### 2026-07-21 — Winner switched to MIN_POOL=15 (better 2.2) [employee]

**Rationale (15 vs 11 tradeoff):** the sweep table above (same date, MIN_POOL=11
entry) shows 11 wins on "smallest passing integer" but leaves 2.2 (AT_HOME)
badly regressed — 6.29pp/12 slots, worse than even the MIN_POOL=10 baseline's
6.10pp/4 slots. Manager decision: re-examine the sweep table's MIN_POOL=15 row,
which gives **W1 still PASS at 2.05pp** (comfortably under the 3.0pp gate) AND
**2.2 far better at 3.66pp/6 slots** (vs 11's 6.29pp/12 slots — roughly half the
deviation, half the slot count) while **W3 holds PASS at 0.888pp** (no
regression). 15 dominates 11 on 2.2 without giving up the W1 crossing, so 15 is
the new winner.

**Setup:** archived the MIN_POOL=11 live script as
`archive/3rdJ_05_censusLinkage_4split.2026-07-21_minpool11.py`. Changed the
`run_slot_match()` default: `MIN_POOL = int(os.environ.get("STEP5_MIN_POOL", "15"))`.
Nothing else changed. Confirmed `STEP5_MIN_POOL` unset in-shell before running
(default 15 takes effect).

**Full 7-stage chain re-run, MIN_POOL=15 default, env var unset:** smoke ->
val(smoke) -> full -> aggregate -> bem -> exclusion -> val(full), all 7 stages
exit 0. `py -3 -X utf8` used throughout. Logs:
`run_final_minpool15_{smoke,valsmoke,full,aggregate,bem,exclusion,valfull}_2026-07-21.log`.

**Final scorecard: 32 PASS / 4 WARN / 3 FAIL** (identical PASS/WARN/FAIL tally
to MIN_POOL=11, but 2.2 materially improved):
- 2.2 AT_HOME: 3.66pp, 6 slots>3pp — FAIL (still FAIL as a category, but much
  closer to the 3pp gate than MIN_POOL=11's 6.29pp/12 slots)
- W1 AT_WORK: 2.05pp, 0 slots>3pp — PASS (held, more margin than 11's 2.97pp)
- W3 Colleagues: 0.888pp — PASS (held, no regression)
- R1 AT_RETAIL: 4.796pp — FAIL (pre-existing FAIL category, untouched)
- R3 ret30 exact-match: PASS, diff=0.00e+00 (full chain regenerates
  Full_Aggregated.csv, so this is the real reading — R3 only spuriously FAILs
  in abbreviated sweeps where `--aggregate` is skipped)
- PR (Section 0.1): 83.3% overlap, missing=[6] — FAIL (left untouched)
- Delta-D 0.2: Tier-1 27.89% / Tier-2 56.77% — WARN (unchanged)

**Row counts:** `Full_Schedules.csv` 30,273 rows (matches spec, unchanged).
`excluded_pids.csv` 771 rows (was 766 at MIN_POOL=11 — donor reassignment
under the wider MIN_POOL=15 pool shifts which agents land in the
AT_HOME-exclusion band).

**Archived predecessor:**
`archive/3rdJ_05_censusLinkage_4split.2026-07-21_minpool11.py`.

**Publishable results change: donor assignments differ from the MIN_POOL=11
version** — expected, since MIN_POOL=15's more-broadened candidate pools change
which donor diary each census agent draws.

Not advancing to Step 6 per instructions.
