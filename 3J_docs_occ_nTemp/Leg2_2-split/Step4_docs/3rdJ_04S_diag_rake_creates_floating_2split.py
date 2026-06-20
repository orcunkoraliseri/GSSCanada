#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3rdJ_04S_diag_rake_creates_floating_2split.py
"Security-camera footage" — proves the classic joint rake (04L) manufactures
the ~25% FLOATING anomaly that was nearly absent (~0%) in the model output.

DEFINITIONS (per 30-min slot s, columns 1-indexed 001..048):
  Work-activity slot : act30_s == 1
  Coherent           : wrk30_s == 1  OR  hom30_s == 1
  FLOATING           : act30_s == 1  AND wrk30_s == 0  AND  hom30_s == 0

BUCKET CLASSIFICATION (for every work-activity slot):
  (a) floating BEFORE rake  (model's own residual)
  (b) coherent before AND coherent after  (rake left it fine)
  (c) coherent before → FLOATING AFTER   *** THE SMOKING GUN ***
  (d) floating before → coherent after   (rake fixed one)

Usage (cluster, via sbatch ps):
    python 3rdJ_04S_diag_rake_creates_floating_2split.py [options]
"""
from __future__ import annotations

import argparse
import os
import platform
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Platform-detection path block ────────────────────────────────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
        r"\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = (
        "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main"
        "/3J_docs_occ_nTemp/Leg2_2-split"
    )
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )

_STEP4_SHARED = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")
_R10_PRE      = os.path.join(_STEP4_SHARED, "sweep", "R10_fast",       "augmented_diaries.csv")
_R10_POST     = os.path.join(_STEP4_SHARED, "sweep", "R10_fast_raked", "augmented_diaries.csv")
_OUT_DEFAULT  = os.path.join(_STEP4_SHARED, "diag_rake_creates_floating_R10.txt")

N_SLOTS      = 48
WORK_CAT_CSV = 1   # act30_xxx == 1 means WORK in the CSV (raw 1-indexed category)

ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK_COLS = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]

# 04:00-origin slot grid.  slot i = 04:00 + i*30 min.
def slot_to_clock(i: int) -> str:
    minutes = 4 * 60 + i * 30
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Rake-creates-floating diagnostic (04S)")
    p.add_argument("--pre_csv",  default=None,
                   help="Pre-rake augmented_diaries.csv  (default: R10_fast/...)")
    p.add_argument("--post_csv", default=None,
                   help="Post-rake augmented_diaries.csv (default: R10_fast_raked/...)")
    p.add_argument("--output",   default=None,
                   help="Output report txt path (default: outputs_step4/diag_rake_creates_floating_R10.txt)")
    p.add_argument("--n_examples", type=int, default=5,
                   help="Number of example respondents to show for bucket (c) (default: 5)")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def classify_slots(act: np.ndarray, hom: np.ndarray, wrk: np.ndarray):
    """
    Returns boolean arrays over (n_rows, n_slots):
      is_work     : act == 1
      is_floating : act == 1 AND wrk == 0 AND hom == 0
      is_coherent : act == 1 AND (wrk == 1 OR hom == 1)
    """
    is_work     = (act == WORK_CAT_CSV)
    is_floating = is_work & (wrk == 0) & (hom == 0)
    is_coherent = is_work & ((wrk == 1) | (hom == 1))
    return is_work, is_floating, is_coherent


def pct(num, den, decimals=2):
    if den == 0:
        return float("nan")
    return round(100.0 * num / den, decimals)


# ─────────────────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────────────────

def run(pre_csv: str, post_csv: str, output: str, n_examples: int):
    lines = []

    def pr(msg=""):
        lines.append(msg)
        print(msg)

    pr("=" * 72)
    pr("3rdJ 04S — RAKE-CREATES-FLOATING diagnostic")
    pr("  'Security-camera footage': did the classic 04L rake manufacture")
    pr("   the ~25% FLOATING anomaly from ~0% model output?")
    pr("=" * 72)
    pr(f"  pre_csv  (model output): {pre_csv}")
    pr(f"  post_csv (raked):        {post_csv}")
    pr(f"  output:                  {output}")
    pr()

    # ── 1. Load both CSVs ────────────────────────────────────────────────────
    pr("[1/5] Loading CSVs...")
    pre  = pd.read_csv(pre_csv,  low_memory=False)
    post = pd.read_csv(post_csv, low_memory=False)
    pr(f"  pre  rows : {len(pre):,}")
    pr(f"  post rows : {len(post):,}")

    if len(pre) != len(post):
        pr(f"[ERROR] Row counts differ ({len(pre)} vs {len(post)}). Cannot align. STOPPING.")
        _write(output, lines)
        sys.exit(1)

    pr(f"  Row counts match: {len(pre):,} rows.  Assuming row-aligned.")
    pr()

    # ── 2. Restrict to synthetic rows ────────────────────────────────────────
    pr("[2/5] Restricting to IS_SYNTHETIC == 1...")
    if "IS_SYNTHETIC" in pre.columns:
        mask_syn = (pre["IS_SYNTHETIC"] == 1).values
        pr(f"  IS_SYNTHETIC column found in pre_csv.  Applying filter.")
        pr(f"  Synthetic rows : {mask_syn.sum():,}  "
           f"(obs rows discarded: {(~mask_syn).sum():,})")
        pre_syn  = pre[mask_syn].reset_index(drop=True)
        post_syn = post[mask_syn].reset_index(drop=True)
    else:
        pr("  IS_SYNTHETIC column NOT found — treating ALL rows as synthetic universe.")
        mask_syn = np.ones(len(pre), dtype=bool)
        pre_syn  = pre.reset_index(drop=True)
        post_syn = post.reset_index(drop=True)
    pr()

    N = len(pre_syn)
    pr(f"  Working universe: {N:,} rows")
    pr()

    # ── 3. Build slot arrays ─────────────────────────────────────────────────
    pr("[3/5] Extracting slot matrices...")
    act_pre  = pre_syn[ACT_COLS].to_numpy(dtype=float)
    hom_pre  = pre_syn[HOM_COLS].to_numpy(dtype=float)
    wrk_pre  = pre_syn[WRK_COLS].to_numpy(dtype=float)

    act_post = post_syn[ACT_COLS].to_numpy(dtype=float)
    hom_post = post_syn[HOM_COLS].to_numpy(dtype=float)
    wrk_post = post_syn[WRK_COLS].to_numpy(dtype=float)

    # Verify act columns are identical between pre and post
    act_diff = int(np.sum(act_pre != act_post))
    pr(f"  act30 column differences pre vs post: {act_diff:,} "
       f"({'OK — activity unchanged by rake' if act_diff == 0 else 'WARNING: activity columns differ!'})")
    pr()

    is_work_pre,     is_float_pre,  is_coh_pre  = classify_slots(act_pre,  hom_pre,  wrk_pre)
    _,               is_float_post, is_coh_post = classify_slots(act_post, hom_post, wrk_post)

    # ── 4. Bucket classification ─────────────────────────────────────────────
    pr("[4/5] Classifying buckets...")
    pr()

    # (a) floating BEFORE rake (model residual)
    bucket_a = is_float_pre                           # shape (N, 48)
    # (b) coherent before AND coherent after
    bucket_b = is_coh_pre & is_coh_post
    # (c) coherent before → floating AFTER  *** smoking gun ***
    bucket_c = is_coh_pre & is_float_post
    # (d) floating before → coherent after
    bucket_d = is_float_pre & is_coh_post

    # Global work slot count
    n_work_total = int(is_work_pre.sum())
    n_a = int(bucket_a.sum())
    n_b = int(bucket_b.sum())
    n_c = int(bucket_c.sum())
    n_d = int(bucket_d.sum())

    # Post-rake floating total
    n_float_post_total = int(is_float_post.sum())  # among work slots

    # Safety check: buckets should partition all work slots
    # Note: is_work_pre == (a + b + c)? No — c uses is_coh_pre & is_float_post.
    # More carefully: is_work = (float_pre & float_post) + (float_pre & coh_post)
    #                          + (coh_pre & float_post) + (coh_pre & coh_post)
    #              = (a_residual) + (d) + (c) + (b)   where a_residual = float_pre & float_post
    n_a_residual = int((is_float_pre & is_float_post).sum())  # subset of (a): stayed floating
    n_check = n_a_residual + n_b + n_c + n_d
    pr(f"  Partition check: a_res({n_a_residual}) + b({n_b}) + c({n_c}) + d({n_d}) = {n_check}  "
       f"vs n_work_total({n_work_total})  "
       f"{'OK' if n_check == n_work_total else 'MISMATCH!'}")
    pr()

    pr("=" * 72)
    pr("SECTION A — GLOBAL BUCKET COUNTS")
    pr("=" * 72)
    pr(f"  Total work-activity slots (pre-rake, IS_SYNTHETIC): {n_work_total:,}")
    pr()
    pr(f"  (a) Floating BEFORE rake [model residual]   : {n_a:,}  ({pct(n_a, n_work_total):.2f}% of work slots)")
    pr(f"      of which STAYED floating after rake      : {n_a_residual:,}  ({pct(n_a_residual, n_work_total):.2f}%)")
    pr(f"  (b) Coherent before AND coherent after       : {n_b:,}  ({pct(n_b, n_work_total):.2f}%)")
    pr(f"  (c) Coherent before → FLOATING AFTER [RAKE] : {n_c:,}  ({pct(n_c, n_work_total):.2f}%)")
    pr(f"  (d) Floating before → coherent after [fixed]: {n_d:,}  ({pct(n_d, n_work_total):.2f}%)")
    pr()

    # POST-rake floating breakdown
    pr(f"  POST-rake floating slots (total)             : {n_float_post_total:,}  ({pct(n_float_post_total, n_work_total):.2f}% of work slots)")
    pr(f"    → from bucket (a) stayed-floating          : {n_a_residual:,}  ({pct(n_a_residual, n_float_post_total):.2f}% of post-rake floating)")
    pr(f"    → from bucket (c) rake-created             : {n_c:,}  ({pct(n_c, n_float_post_total):.2f}% of post-rake floating)  *** HEADLINE ***")
    pr()

    headline_pct_c = pct(n_c, n_float_post_total)
    headline_pct_a = pct(n_a_residual, n_float_post_total)
    pr("*** HEADLINE NUMBERS ***")
    pr(f"  {headline_pct_c:.1f}% of the final post-rake floating mass was MANUFACTURED by the rake (bucket c).")
    pr(f"  {headline_pct_a:.1f}% of the final post-rake floating mass was the model's own residual (bucket a).")
    pr()

    # ── 5. Slot-of-day breakdown for bucket (c) ──────────────────────────────
    pr("=" * 72)
    pr("SECTION B — SLOT-OF-DAY BREAKDOWN of bucket (c) [rake-created floating]")
    pr("=" * 72)

    c_per_slot  = bucket_c.sum(axis=0)         # (48,) count of (c) per slot
    work_per_slot = is_work_pre.sum(axis=0)    # (48,) work slots per slot

    pr(f"  {'slot':>4}  {'clock':>5}  {'c_count':>8}  {'c_pct_work':>12}  {'c_pct_all_c':>12}")
    pr("  " + "-" * 52)
    n_c_total_slots = int(c_per_slot.sum())
    for i in range(N_SLOTS):
        if work_per_slot[i] == 0:
            continue
        cc = int(c_per_slot[i])
        if cc == 0:
            continue
        pr(f"  {i:>4}  {slot_to_clock(i):>5}  {cc:>8}  "
           f"{pct(cc, int(work_per_slot[i])):>10.2f}%  "
           f"{pct(cc, n_c if n_c > 0 else 1):>10.2f}%")
    pr()

    # ── 6. Weekday vs weekend breakdown ─────────────────────────────────────
    pr("=" * 72)
    pr("SECTION C — WEEKDAY vs WEEKEND breakdown of bucket (c)")
    pr("=" * 72)

    if "DDAY_STRATA" in pre_syn.columns:
        strata_arr = pre_syn["DDAY_STRATA"].to_numpy(dtype=float)
        for sv, label in [(1, "Weekday (strata=1)"), (2, "Saturday (strata=2)"), (3, "Sunday (strata=3)")]:
            row_mask = (strata_arr == sv)
            n_row = int(row_mask.sum())
            if n_row == 0:
                pr(f"  {label}: 0 rows")
                continue
            nw_s  = int(is_work_pre[row_mask].sum())
            nc_s  = int(bucket_c[row_mask].sum())
            nfp_s = int(is_float_post[row_mask].sum())
            pr(f"  {label}:")
            pr(f"    work_slots={nw_s:,}  post_float={nfp_s:,}  "
               f"rake-created-float(c)={nc_s:,}  "
               f"c_pct_work={pct(nc_s, nw_s):.2f}%  "
               f"c_pct_post_float={pct(nc_s, nfp_s):.2f}%")
    else:
        pr("  DDAY_STRATA column not found — skipping weekday/weekend breakdown.")
    pr()

    # ── 7. Example respondents in bucket (c) ────────────────────────────────
    pr("=" * 72)
    pr(f"SECTION D — {n_examples} EXAMPLE RESPONDENTS in bucket (c) [rake flipped them]")
    pr("=" * 72)

    # Find rows that have at least one bucket(c) slot
    rows_with_c = np.where(bucket_c.any(axis=1))[0]
    pr(f"  Rows (respondent-diaries) with at least 1 bucket(c) slot: {len(rows_with_c):,}")
    pr()

    rng = np.random.default_rng(42)
    sample_rows = rng.choice(rows_with_c, size=min(n_examples, len(rows_with_c)), replace=False)
    sample_rows = np.sort(sample_rows)

    id_cols = [c for c in ["occID", "CYCLE_YEAR", "DDAY_STRATA"] if c in pre_syn.columns]

    for ex_num, row_idx in enumerate(sample_rows, 1):
        id_vals = {c: pre_syn[c].iloc[row_idx] for c in id_cols}
        id_str  = "  ".join(f"{k}={v}" for k, v in id_vals.items())
        c_slots = [i for i in range(N_SLOTS) if bucket_c[row_idx, i]]
        pr(f"  Example {ex_num}: row_idx={row_idx}  {id_str}")
        pr(f"    bucket(c) slots affected: {c_slots} (clock: {[slot_to_clock(i) for i in c_slots]})")
        pr(f"    {'slot':>4}  {'clock':>5}  {'act':>4}  "
           f"{'hom_pre':>8}  {'wrk_pre':>8}  ||  {'hom_post':>9}  {'wrk_post':>9}")
        pr("    " + "-" * 62)
        for i in c_slots:
            ap  = int(act_pre[row_idx, i])
            hp  = int(hom_pre[row_idx, i])
            wp  = int(wrk_pre[row_idx, i])
            hpp = int(hom_post[row_idx, i])
            wpp = int(wrk_post[row_idx, i])
            flag_pre  = "COH" if (hp == 1 or wp == 1) else "FLT"
            flag_post = "FLT" if (hpp == 0 and wpp == 0) else "COH"
            pr(f"    {i:>4}  {slot_to_clock(i):>5}  act={ap}  "
               f"hom={hp}  wrk={wp}  ||  hom={hpp}  wrk={wpp}  "
               f"[{flag_pre}→{flag_post}]")
        pr()

    # ── 8. Final verdict ─────────────────────────────────────────────────────
    pr("=" * 72)
    pr("VERDICT")
    pr("=" * 72)
    if headline_pct_c >= 90:
        verdict = "YES — overwhelmingly confirmed"
    elif headline_pct_c >= 70:
        verdict = "YES — strongly confirmed"
    elif headline_pct_c >= 50:
        verdict = "PARTIAL — majority rake-created"
    else:
        verdict = "PARTIAL/NO — model residual dominates"

    pr(f"  Does the rake CREATE the floating anomaly?  {verdict}")
    pr(f"  {headline_pct_c:.1f}% of post-rake floating was manufactured by the 04L rake.")
    pr(f"  {headline_pct_a:.1f}% was the model's own residual (pre-rake).")
    pr(f"  Bucket (c) count: {n_c:,} coherent→floating flips across {len(rows_with_c):,} respondent-diaries.")
    pr()

    _write(output, lines)
    return lines


def _write(output: str, lines: list):
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n[OK] Report written to {output}")


def main():
    args = parse_args()
    pre_csv  = args.pre_csv  or _R10_PRE
    post_csv = args.post_csv or _R10_POST
    output   = args.output   or _OUT_DEFAULT

    for f, label in [(pre_csv, "pre_csv"), (post_csv, "post_csv")]:
        if not os.path.isfile(f):
            print(f"[ERROR] {label} not found: {f}")
            sys.exit(1)

    run(pre_csv, post_csv, output, args.n_examples)


if __name__ == "__main__":
    main()
