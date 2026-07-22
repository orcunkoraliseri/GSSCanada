# EMPLOYEE PROMPT — Leg-3 Step 5 · PART 1: BUILD both scripts + run the SMOKE gate

**You are the employee. Execute the task below and append a Progress Log entry on completion.** Runs LOCALLY on Windows (no sbatch). Use `py -3 -X utf8` for every Python invocation. Stop and flag back to the user on any decision-level question — do not decide silently.

This is **Part 1 of 2**. Scope = fork the two scripts, apply the five Leg-3 deltas, and run **only the smoke gate** (`--smoke` on main, then `--smoke` on the validator). **Do NOT run `--full/--aggregate/--bem/--exclusion`** — the manager reviews the smoke result first (the join-key connectivity audit is the checkpoint that catches the Leg-2 silent-truncation class of bug). Report back and stop.

---

## Context you need

- **Runbooks (single source of truth — execute as written, do not redesign):**
  - `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.md`
  - `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.md`
- **Fork bases (the LIVE, non-archived Leg-2 Step-5 files — confirm you are NOT forking an `archive/*_pre*` predecessor):**
  - main: `3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split.py`
  - val:  `3J_docs_occ_nTemp/Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split_val.py`
- **New files to create (fork targets):**
  - `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.py`
  - `3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.py`
- **Inputs (all local, verified present):**
  - Census: `0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv` (~30,273 rows — re-verify at run)
  - Office lookup: `0_Occupancy/processed/office_archetype_lookup.csv`
  - **Diary pool (the Leg-3 LOCKED pool, with `ret30_*`):** `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv` (192,183 rows; `ret30_001..048` present). A separate employee is scp'ing this down now — **before you run anything, confirm this file exists locally and `head -1 | tr ',' '\n' | grep -c '^ret30_'` returns 48.** If it is missing, STOP and tell the user the pool scp is not finished.
- **md5 the pool once** (`md5sum` the local pool) and record it in the Progress Log — pool provenance of record.

The two scripts point at Leg-2 input/output paths. Update the pool path, output dir, and any hardcoded `2split`→`4split` path/name references so Leg-3 writes to its OWN `Step5_docs/outputs_step5/` (NEVER overwrite Leg-2 dirs). Do not otherwise touch the matching machinery — 4-tier fallback match, day-type 5:1:1 (seed 42), authority rules, aggregation stages are all **verbatim Leg-2**.

---

## The five Leg-3 deltas (everything else byte-for-byte Leg 2)

`ret30` is a **per-person population-fraction channel that mirrors `wrk30` in EVERY respect** (carried, never re-derived; **never HH-maxed** — only `hom30` is HH-maxed). The core edit is mechanical: wherever `wrk30` appears as a carried per-person channel, add a parallel `ret30` block. Anchors below are line numbers in the Leg-2 **main** fork base.

### Delta A — channel carry-through (main)
- `expand_slot_schedules` (~L313):
  - docstring (~L320): "Carries BOTH channels (act30, hom30, wrk30)" → "act30, hom30, wrk30, ret30".
  - after the `wrk_cols` definition (~L332) add: `ret_cols = sorted([c for c in df_pool.columns if c.startswith("ret30_")])`.
  - add `set(ret_cols)` into the `_explicit_pool` set (~L344-349).
  - insert `+ ret_cols` into `pool_diary_cols` immediately after `wrk_cols` (~L359).
- `run_smoke`: mirror every `wrk30` presence print/assert with a `ret30` one (Leg-2 anchors ~L525-534, L562, L625, L650). Add `ret_cols = [f"ret30_{i:03d}" for i in range(1,49)]` and assert all 48 present in `df_full`.
- `run_full` (~L682-696): mirror the `wrk30` presence assert (~L690-691) for `ret30`.
- **Do NOT touch the act30 / Rung-I re-rake logic** (~L494-520). `ret30` is inert to raking — it is neither an input to nor an output of any rake. Leave that code exactly as-is; `ret30` simply rides through `expand_slot_schedules`.

### Delta B — aggregation semantics, Sub-step 5E (main, `run_aggregate` ~L722)
- `ret30` **stays per-person — do NOT HH-max it.** Only `hom30` is HH-maxed (the `groupby(...).max()` at ~L737 stays hom30-only — do not add ret30 to it).
- `ret30_*` already flows through `df` into `Full_Aggregated` untouched; add an explicit presence assert that all 48 `ret30_*` survive into `df_agg`.
- Update the NOTE print (~L754) to: `wrk30 AND ret30 stay per-person (no HH aggregation of AT_WORK / AT_RETAIL).`
- Optional (nice-to-have, not required): add a `ret_mean` diurnal line to the validation plot mirroring the `wrk_mean` line (~L768-777).

### Delta C — exclusion, Sub-step 5H (main, `run_exclusion` ~L898) — UNCHANGED
- Logic stays exactly Leg-2 (AT_HOME < 0.30 drop; retail plays no role). `ret30_*` rides through automatically because exclusion operates on whole rows. Add one assert that `ret30_*` columns are present in both `_excl` outputs.

### Delta D — join-key connectivity audit (main, NEW; run in `--smoke`) — the PR-remap lesson
Write one diagnostic function, e.g. `audit_join_key_connectivity(df_census, df_pool)`, called inside `run_smoke` **after** the census remaps are applied and **before** matching. For every match key — **AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA, DDAY** — print a small table of: census value domain, pool value domain, and whether `census_domain ⊆ pool_domain` (after the same remaps the matcher applies). Also print the share of pool rows reachable under the Tier-1 and Tier-2 key sets.
- **FAIL loudly (raise / non-zero) if any census value for any key is absent from the pool domain** — that is the exact Leg-2 bug where a silent PR coding mismatch confined matching to ~30% of the pool while tier rates still looked healthy.
- Use the matcher's own key list / remap helpers so the audit reflects reality — do not hand-code a second copy of the remap.

### Delta E — validator (val script): Section 0 + Section 3r (per `..._4split_val.md`)
Fork `3rdJ_05_censusLinkage_2split_val.py` → `3rdJ_05_censusLinkage_4split_val.py`. Keep Sections 1,2,4,5,6 verbatim (Section 3 AT_WORK W1–W4 too — inherited Step-4 FAILs are expected; only a *materially worse* value than the Leg-2 record is a new WARN). Rename the class to `CensusLinkageValidator4CH` and update output path to `outputs_step5/3rdJ_step5_validation_report.html`. Update column-count checks for the added `ret30` (Full_Schedules ~248 → ~296; BEM/6.x counts accordingly). Then ADD:

- **Section 0 — join-key connectivity:**
  - 0.1: for each match key (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA, DDAY) census domain ⊆ pool domain after remaps → **FAIL** if <100% overlap.
  - 0.2: share of pool reachable under Tier-1/Tier-2 keys ≥ 95% → **WARN** if below.
- **Section 3r — AT_RETAIL consistency:**
  - R1: AT_RETAIL per-slot max deviation, matched-output vs pool, per (cycle × stratum) ≤ 3.0 pp → **FAIL** > 3, **WARN** 1–3 (expect ≪ — ~2%-positive channel).
  - R2: population-level retail sanity on the matched frame: weekday 12–14h rate 0.06–0.10 · night 0.000–0.003 → **WARN** outside band.
  - R3: aggregation semantics — `ret30` never HH-maxed: per-person mean of matched persons == the 5E aggregate within float tolerance → **FAIL** if not exact.
  - R4: assert **no** `retail_archetype` column exists (deferred-decision guard) → **WARN** if present.

---

## Non-negotiable disciplines (enforce; Leg-2 lessons)
1. **Frame discipline — re-derive, never assume.** Do NOT hardcode or carry the Leg-2 frame constants (23,150 HH / 29,538 stock / 735 excluded). Any frame count must come from THIS run's own outputs. (Smoke won't produce the final frame — just don't bake Leg-2 numbers into the code.)
2. **Byte-identity guard.** `ret30` edits must not perturb the other channels. Where a stage touches only one channel, assert the others are byte-identical with `np.array_equal`.
3. **Pool provenance:** use the Leg-3 locked pool only (with `ret30_*`), NEVER the Leg-2 pool. Record its md5.
4. **Archive before edit is N/A** here (these are NEW files, not edits to existing pipeline files) — but do NOT overwrite any Leg-2 file or output dir.
5. **Verify from the artifact, not the log** — re-derive any number you report from the file's own columns.

---

## Run the SMOKE gate (and ONLY the smoke gate)

```
py -3 -X utf8 3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.py --smoke
py -3 -X utf8 3J_docs_occ_nTemp/Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.py --smoke
```

**Do not run `--full`, `--aggregate`, `--bem`, or `--exclusion`.** Those are Part 2, after the manager reviews smoke.

## Deliverable / report back
Append a **Progress Log** entry to `3rdJ_05_censusLinkage_4split.md` covering: files created, the five deltas applied (with the exact functions/lines touched), pool md5 + row count, and the **join-key connectivity audit table** (Delta D output — this is the load-bearing result). Then report back to the user with:
- confirmation both scripts fork-built and import/run clean under `--smoke`;
- the Section 0 connectivity verdict (per-key ⊆ overlap %, and Tier-1/2 reachable share) — **flag immediately if any key is <100% overlap**;
- ret30 carry-through confirmed in the smoke `Full_Schedules_smoke.csv` (48 cols present, values in {0,1});
- the smoke-validator scorecard (P/W/F counts) and any FAIL;
- STOP after smoke — state "Part 1 complete, awaiting manager review before the full chain."
