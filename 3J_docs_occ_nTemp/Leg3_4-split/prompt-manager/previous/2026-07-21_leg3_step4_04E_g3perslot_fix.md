# EMPLOYEE PROMPT — Leg-3 · Step-4 · 04E G3 per-slot co-presence fix (implement + LOCAL smoke ONLY)

**You are the employee. Execute the task below and append a Progress Log entry on completion.** This is a **code edit + LOCAL smoke** task — **NO cluster work of any kind** (no scp, no ssh, no sbatch, no job submission). Windows-local, `py -3 -X utf8` for every Python call. You edit exactly ONE file (`3rdJ_04E_inference_4split.py`), archive its predecessor first, and prove the patch runs correctly at smoke scale. You do NOT touch any production `outputs_step4/sweep/...` dir. Decision-level questions → stop and flag the manager.

---

## Why you exist (context)

Diagnosed 2026-07-21 (W3 entry in `3rdJ_04_augmentationGSS_4split.md`): the G3 co-presence binarization in `3rdJ_04E_inference_4split.py` (lines ~530–561) uses **one GLOBAL quantile threshold per co-presence channel** (all 48 slots × all synthetic rows flattened). This nails the global prevalence (0.0010 pp) but has **zero day-type / slot-shape control** → synthetic `colleagues30` over-generates on weekday afternoons, peaking at 16:30 (SYN 20.19% vs OBS 5.42%), driving validator gate **W3 = 7.19 pp** (gate ≤ 3 pp; W3 is the WD/WE **scalar mean-of-per-slot-means**, `max(|meanSYN−meanOBS|_WD, |·|_WE)`).

**The fix (user chose max-precision, per-slot):** replace the single global threshold with a **per-(day-type × slot)** threshold, so synthetic co-presence prevalence matches observed prevalence *in each (day-type, slot) cell* — this fixes both the W3 scalar (by construction) AND the underlying 16:30 slot shape. A **min-support guard** falls back to a day-type-pooled threshold where the observed cell is too thin to estimate a stable prevalence.

**Determinism (already confirmed):** the sole RNG draw is `torch.multinomial` (line ~195), downstream of `torch.manual_seed(42)` (line ~314); no shuffle/second seed. So re-running 04E on the same checkpoint reproduces act/hom/wrk/ret **byte-identical** — this fix touches **only** the 9 co-presence channels. Your smoke must confirm that invariant.

**Scope boundary:** the checkpoint that generated the production pool is cluster-only (absent locally), so a local smoke uses the **existing local smoke inputs** from the 2026-07-19 04E smoke runs — it proves *code correctness*, not W3 efficacy (efficacy is measured later at the cluster full run). Do not claim W3 is fixed from the smoke.

---

## The change (edit `3rdJ_04E_inference_4split.py` only)

**Archive first:** copy the current file to `Step4_docs/archive/3rdJ_04E_inference_4split.py.20260721_preG3perslot` (create `archive/` if absent). Do not edit anything else.

**Replace the G3-fix loop (the block from the `for cn in COP_COLS:` loop through the `thresholds[cn] = {...}` write, ~lines 534–553; keep the surrounding prints, the `syn_mask`/`obs_mask` defs at 531–532, and the `out_thresh` JSON write at 554–556).** New logic:

- Day-types from the existing `aug_df["DDAY_STRATA"]` column (present at this point — emitted by `run_inference`, only the meta-copy was dropped at line 523): **WD = `DDAY_STRATA == 1`**, **WE = `DDAY_STRATA.isin([2, 3])`**.
- Module-level constants near the block (parameterize, don't hard-bury): `G3_MIN_OBS_CELL = 200` (min non-null observed rows in a (daytype,slot) cell), `G3_MIN_POS_CELL = 20` (min observed positives in the cell), `G3_MIN_SYN_CELL = 50` (min non-null synthetic scores in the cell). Below any of these → fall back.
- For each `cn in COP_COLS`, for each day-type `d in {WD, WE}`:
  1. `obs_d` = observed rows of that day-type over the 48 cols; `syn_d` = synthetic rows of that day-type (these hold the **raw continuous scores** at this point).
  2. **Day-type-pooled fallback threshold:** `p_obs_pool = nanmean(obs_d == 1)` (scalar over all cells); `q_pool = clip(1 - p_obs_pool, 0, 1)`; `t_pool = quantile(syn_d_flat_nonnan, q_pool)`.
  3. For each slot `j` in 0..47: `n_obs_j` = non-null obs count, `n_pos_j` = obs positives, `syn_valid` = non-null syn scores in the cell.
     - If `n_obs_j >= G3_MIN_OBS_CELL and n_pos_j >= G3_MIN_POS_CELL and syn_valid.size >= G3_MIN_SYN_CELL`: `p_obs_j = n_pos_j / n_obs_j`; `q_j = clip(1 - p_obs_j, 0, 1)`; `t_j = quantile(syn_valid, q_j)`; binarize this cell's syn scores `>= t_j` → mark **per_slot**.
     - Else: binarize this cell's syn scores `>= t_pool` → mark **fallback_pool**.
  4. Write the binarized synthetic cells back into `aug_df` for `syn_mask & d_mask` (align by index/position — verify no OBS row and no non-`cn` column is written).
- Preserve NaN behavior: `score >= t` yields False for NaN (as the current code does) — do not change how NaNs binarize.
- Record into `thresholds[cn]` a richer summary: per day-type `{obs_prev_pct, syn_prev_pct_after, n_per_slot_cells, n_fallback_cells, max_perslot_abs_gap_pp_after}`. Keep writing `g3_copresence_thresholds.json` (04L merely file-copies it forward as provenance — a richer schema is safe).
- Add a print: per channel, the day-type scalar `|obs−syn|` after, and the per-slot-vs-fallback cell counts.

**Do not** change: the AR generation, ISR pipeline, min-dwell, retail/home/work thresholding, column ordering, `to_csv`, or any CLI arg. Smallest practical change, confined to the G3 block + the 3 new constants.

---

## Verify (LOCAL smoke — correctness gate, not efficacy)

1. `py -3 -X utf8 -m py_compile 3rdJ_04E_inference_4split.py` — clean.
2. Run 04E `--smoke` end-to-end using the **same local smoke inputs (data_dir + checkpoint) that the 2026-07-19 04E smoke used** (documented in this doc's 07-19 Progress Log; reuse `outputs_step4/smoke_test_20260719*` artifacts). Send the output to a **scratch** dir (session scratchpad or `outputs_step4/smoke_g3perslot_20260721/`), NEVER a `sweep/...` production dir.
3. Assert on the smoke output:
   - **(a) only co-presence changed:** compared to a control run of the **pre-fix** archived script on the *same* smoke inputs, `act30_*/hom30_*/wrk30_*/ret30_*` are byte-identical (`np.array_equal`), and OBS (`IS_SYNTHETIC==0`) co-presence rows are unchanged; only synthetic `<cop>30_*` cells differ. (This is the determinism/only-cop invariant.)
   - **(b) it runs, fallback logic fires and is logged:** report, per channel, the per-slot vs fallback cell counts (at smoke scale most cells will fallback — that's expected and fine; the point is the branch executes without error).
   - **(c) construction sanity:** for at least the channels where per-slot cells were used, the per day-type `|obs−syn|` scalar after the fix is ≤ ~1 pp (near-zero by construction). Do NOT over-interpret smoke-scale magnitudes.
4. Relocate/keep smoke artifacts out of production dirs. Leave `outputs_step4/sweep/...` untouched.

---

## Deliverable / report back

Append a Progress Log entry to `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` headed `### 2026-07-21 — 04E G3 per-slot co-presence fix (implemented + local smoke, cluster re-run pending)`, containing: the exact block replaced (line range) + the 3 new constants, the archived-predecessor path, the smoke command used (data_dir + checkpoint), and the three assertions' results (a/b/c) with the only-cop-changed `np.array_equal` outcome and the per-channel per-slot/fallback counts.

Then report back to the manager with a 6–8 line summary: patch landed (block + constants), predecessor archived at `___`, `py_compile` clean, smoke ran on `___` inputs, **only-cop-changed invariant = CONFIRMED/FAILED** (`np.array_equal` on act/hom/wrk/ret), fallback branch fired, construction sanity OK. End with: **"04E patch ready for cluster re-run / NOT ready because ___."** Do NOT do any cluster work — STOP after reporting; the manager authorizes Stage 2 (cluster 04E re-run + rake re-cascade).

## Disciplines (enforce)
1. **One file edited** (`3rdJ_04E_inference_4split.py`); **archive predecessor first**; no other file touched.
2. **No cluster work** — no ssh/scp/sbatch/srun; local `py -3 -X utf8` only.
3. **Never write to `outputs_step4/sweep/...`** — smoke outputs go to a scratch/smoke dir only.
4. **Byte-identity guard** (`np.array_equal`) proving act/hom/wrk/ret unchanged vs the archived pre-fix script on the same smoke inputs.
5. **Verify from the artifact** — every number from the smoke output's own columns, not the log.
6. Decision-level questions → stop and flag the manager.
