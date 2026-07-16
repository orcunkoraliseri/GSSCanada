# -*- coding: utf-8 -*-
"""
apply_04T_to_2030.py -- Step-6 3b gate: apply 04T's conditional act30 rake to the
2030 Calibration-C output, using 2022-OBSERVED conditional targets (2J
06_forecast_rake.py analogue; OD-I4, resolved 2026-07-15).

WHY a wrapper instead of calling 3rdJ_04T_act_rake_2split.py directly:
04T's main() assumes a single input CSV containing BOTH observed (IS_SYNTHETIC==0)
and synthetic (IS_SYNTHETIC==1) rows for the SAME CYCLE_YEAR values (its outer loop
is `for cy in CYCLES: for s in STRATA`, CYCLES=[2005,2010,2015,2022]). The 2030
Calibration-C file has CYCLE_YEAR==2030 uniformly and IS_SYNTHETIC==1 uniformly --
handed to 04T's main() as-is, the (cy,s) grid would never match anything (2030 is
not in CYCLES) and it would silently do nothing (0 moves).

This wrapper builds the same combined-frame shape 04T expects, by relabeling a COPY
of the 2030 rows to CYCLE_YEAR=2022 (so they land in 04T's real 2022 cell grid) and
concatenating with the true 2022-observed rows from R5_raked_mindwell_actv2 (IS_SYNTHETIC==0,
CYCLE_YEAR==2022, n=12,336 -- the canonical, already-clean GSS 2022 diarists; 04T never
mutates obs rows, so these are untouched by Task 1's own rake). It then calls 04T's
OWN tested functions (`_run_act30_conditional_rake`, imported, not re-implemented) to
do the rake, and finally extracts just the (relabeled-back) 2030 rows.

hom30_*/wrk30_* are never touched (04T's own internal invariant); this wrapper adds an
independent, redundant hom/wrk byte-identity check on top of 04T's own guardrail.
"""
from __future__ import annotations

import importlib
import os
import sys

import numpy as np
import pandas as pd

STEP4_DIR = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step4_docs"
sys.path.insert(0, STEP4_DIR)
t04 = importlib.import_module("3rdJ_04T_act_rake_2split")

IN_2030 = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv"
IN_OBS22 = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\outputs_step4\sweep\R5_raked_mindwell_actv2\augmented_diaries.csv"
OUT_2030 = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv"
PRE_RAKE_SNAPSHOT = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.preRake_actv2_20260715.csv"

HOM_COLS, WRK_COLS, ACT_COLS = t04.HOM_COLS, t04.WRK_COLS, t04.ACT_COLS
SEED = 42


def main():
    print("=" * 70)
    print("apply_04T_to_2030.py -- Step-6 3b gate 04T forecast-rake")
    print(f"  2030 input (post Calibration-C actv2): {IN_2030}")
    print(f"  2022-observed reference (R5_raked_mindwell_actv2): {IN_OBS22}")
    print("=" * 70)

    df2030 = pd.read_csv(IN_2030, low_memory=False)
    print(f"\n2030 rows: {len(df2030):,}  cols: {len(df2030.columns)}")
    assert (df2030["CYCLE_YEAR"] == 2030).all()
    assert (df2030["IS_SYNTHETIC"] == 1).all()

    # Snapshot a pristine copy of the pre-rake 2030 file (traceability of the
    # intermediate, post-Calibration-C/pre-04T state) before any mutation.
    df2030.to_csv(PRE_RAKE_SNAPSHOT, index=False)
    print(f"  Wrote pre-rake snapshot -> {PRE_RAKE_SNAPSHOT}")

    needed_obs_cols = list(dict.fromkeys(HOM_COLS + WRK_COLS + ACT_COLS +
                                          ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC", "LFTAG"]))
    obs_all = pd.read_csv(IN_OBS22, low_memory=False, usecols=needed_obs_cols)
    obs22 = obs_all[(obs_all["CYCLE_YEAR"] == 2022) & (obs_all["IS_SYNTHETIC"] == 0)].copy()
    print(f"2022-observed reference rows: {len(obs22):,}")

    # ---- Build the combined frame 04T expects ----
    fc = df2030.copy()
    fc["_FORECAST_2030_MARKER"] = 1
    fc["CYCLE_YEAR"] = 2022          # relabel so it lands in 04T's real 2022 (cy,s) grid
    # IS_SYNTHETIC already == 1

    obs22["_FORECAST_2030_MARKER"] = 0
    # obs22 IS_SYNTHETIC already == 0, CYCLE_YEAR already == 2022

    combined = pd.concat([obs22, fc], ignore_index=True, sort=False)
    print(f"Combined frame rows: {len(combined):,}  "
          f"(obs22={len(obs22):,} + 2030-as-2022={len(fc):,})")

    hom_before = combined[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = combined[WRK_COLS].to_numpy(dtype=float, copy=True)

    obs_mask = combined["IS_SYNTHETIC"] == 0
    syn_mask = combined["IS_SYNTHETIC"] == 1
    print(f"obs_mask rows: {int(obs_mask.sum()):,}  syn_mask rows (2030-as-2022): {int(syn_mask.sum()):,}")

    print("\n--- Before (04P-style decomposition, forecast rows only) ---")
    before_syn = t04._measure_work_state(combined.loc[syn_mask])
    print(f"  SYN(2030) : n_work={before_syn.get('n_work', 0):,}  "
          f"AT-WORK={before_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_syn.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={before_syn.get('floating_pct', float('nan')):.2f}%")
    before_obs = t04._measure_work_state(combined.loc[obs_mask])
    print(f"  OBS(2022) : n_work={before_obs.get('n_work', 0):,}  "
          f"AT-WORK={before_obs.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_obs.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={before_obs.get('floating_pct', float('nan')):.2f}%")

    print("\n--- Running 04T's conditional rake (imported, unmodified) ---", flush=True)
    rng = np.random.default_rng(SEED)
    total_moves, diag = t04._run_act30_conditional_rake(
        combined, ACT_COLS, HOM_COLS, WRK_COLS, obs_mask, syn_mask, rng
    )

    print("\n--- After ---")
    after_syn = t04._measure_work_state(combined.loc[syn_mask])
    print(f"  SYN(2030) : n_work={after_syn.get('n_work', 0):,}  "
          f"AT-WORK={after_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={after_syn.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={after_syn.get('floating_pct', float('nan')):.2f}%")

    # ---- Guardrail: hom30/wrk30 byte-identical across the WHOLE combined frame ----
    hom_after = combined[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_after = combined[WRK_COLS].to_numpy(dtype=float, copy=True)
    hom_identical = np.array_equal(hom_before, hom_after)
    wrk_identical = np.array_equal(wrk_before, wrk_after)
    print(f"\n  hom30 byte-identical (combined frame): {hom_identical}")
    print(f"  wrk30 byte-identical (combined frame): {wrk_identical}")
    if not (hom_identical and wrk_identical):
        raise RuntimeError("INVARIANT VIOLATION: hom30/wrk30 changed. Aborting write.")

    # ---- Extract the (relabeled) 2030 rows back out, restore CYCLE_YEAR=2030 ----
    out2030 = combined.loc[combined["_FORECAST_2030_MARKER"] == 1].copy()
    out2030["CYCLE_YEAR"] = 2030
    out2030 = out2030.drop(columns=["_FORECAST_2030_MARKER"])
    # Restore original 2030 column order/schema exactly (drop any obs22-only cols
    # that leaked in via the outer join, e.g. LFTAG is shared so nothing extra
    # should appear, but enforce anyway for a clean, schema-stable deliverable).
    out2030 = out2030[[c for c in df2030.columns]]

    assert len(out2030) == len(df2030), f"row count mismatch: {len(out2030)} vs {len(df2030)}"
    assert (out2030["CYCLE_YEAR"] == 2030).all()
    assert (out2030["IS_SYNTHETIC"] == 1).all()

    # Row-count-preserving hom/wrk identity check for the 2030 slice specifically
    hom_2030_before = df2030[HOM_COLS].to_numpy(dtype=float)
    wrk_2030_before = df2030[WRK_COLS].to_numpy(dtype=float)
    hom_2030_after = out2030[HOM_COLS].to_numpy(dtype=float)
    wrk_2030_after = out2030[WRK_COLS].to_numpy(dtype=float)
    print(f"\n  2030-slice hom30 byte-identical to pre-rake: {np.array_equal(hom_2030_before, hom_2030_after)}")
    print(f"  2030-slice wrk30 byte-identical to pre-rake: {np.array_equal(wrk_2030_before, wrk_2030_after)}")

    act_2030_before = df2030[ACT_COLS].to_numpy(dtype=float)
    act_2030_after = out2030[ACT_COLS].to_numpy(dtype=float)
    n_act_moved_2030 = int((act_2030_before != act_2030_after).sum())
    print(f"  2030-slice act30 cells changed: {n_act_moved_2030:,} "
          f"(of {act_2030_before.size:,})")

    out2030.to_csv(OUT_2030, index=False)
    print(f"\nWrote raked 2030 deliverable -> {OUT_2030}  rows={len(out2030):,}")

    print(f"\nTotal act30 moves in combined rake: {total_moves:,}")
    print("LFTAG pooling:", diag["pooling_rate_cells_pct"], "% cells,",
          diag["pooling_rate_rows_pct"], "% syn rows")
    print("=" * 70)
    print("DONE")


if __name__ == "__main__":
    main()
