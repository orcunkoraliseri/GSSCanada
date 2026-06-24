# -*- coding: utf-8 -*-
"""
assemble_scenario_2030_2split.py
Sub-step 6B2 — Scenario Assembly for 2030 Synthetic Population

Builds scenario_2030_features_2split.csv for use as conditioning features in
Sub-stage D Phase ii (2030 forward forecast, three WFH bands).

Pipeline:
  1. Load R5_lr1e4 augmented_diaries.csv (or --data override).
  2. Filter to CYCLE_YEAR == 2022 (most recent observed cycle, structural template).
  3. Resample AGEGRP column to M1 2030 Stats Canada targets via weighted resampling.
  4. Keep TELEWORK / TELEWORK_KNOWN columns as-is (WFH-band injection is done in 6D2,
     not here — per OD-4 deferred resolution: scenario assembly does NOT inject bands).
  5. Tag CYCLE_YEAR = 2030 and SCENARIO = M1_2030.
  6. Write to outputs_step6/scenario_2030_features_2split.csv.

Modes:
  python assemble_scenario_2030_2split.py --verify   # dry-run: print summary, no write
  python assemble_scenario_2030_2split.py            # write mode

AGEGRP 2030 M1 targets (Stats Canada projection):
  1 -> 13.5%   (15-24)
  2 -> 16.5%   (25-34)
  3 -> 17.5%   (35-44)
  4 -> 15.5%   (45-54)
  5 -> 14.8%   (55-64)
  6 -> 13.0%   (65-74)
  7 ->  9.2%   (75+)
"""

from __future__ import annotations

import argparse
import os
import platform
import sys

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Path resolution ────────────────────────────────────────────────────────────

_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )

STEP4_DATA = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")
STEP6_DIR  = os.path.join(_LEG2_BASE, "Step6_docs")
OUTPUT_DIR = os.path.join(STEP6_DIR, "outputs_step6")

# ── AGEGRP 2030 M1 targets ─────────────────────────────────────────────────────

AGEGRP_2030_TARGETS = {
    1: 0.135,
    2: 0.165,
    3: 0.175,
    4: 0.155,
    5: 0.148,
    6: 0.130,
    7: 0.092,
}


def resample_agegrp(df: pd.DataFrame, targets: dict, rng_seed: int = 42) -> pd.DataFrame:
    """
    Resample df so the AGEGRP distribution matches targets via stratified resampling.
    The output has the same total N as input (no upsample/downsample beyond per-group
    proportional sampling-with-replacement).

    Strategy:
      - Compute target counts as round(target_share * N) per group.
      - Round-adjust smallest group to hit exact N.
      - Sample each group with replacement to the target count.
    """
    N = len(df)
    rng = np.random.default_rng(rng_seed)

    # Compute target counts (integer)
    target_counts = {}
    for ag, share in targets.items():
        target_counts[ag] = int(round(share * N))

    # Adjust for rounding error: add/subtract from the largest group
    deficit = N - sum(target_counts.values())
    if deficit != 0:
        largest_ag = max(target_counts, key=lambda k: target_counts[k])
        target_counts[largest_ag] += deficit

    assert sum(target_counts.values()) == N, "Target count adjustment failed"

    # Sample per group
    parts = []
    present_groups = set(df["AGEGRP"].dropna().astype(int).unique())

    for ag, n_target in target_counts.items():
        if n_target == 0:
            continue
        sub = df[df["AGEGRP"] == ag]
        n_avail = len(sub)
        if n_avail == 0:
            print(f"  [WARN] AGEGRP {ag}: no observations in 2022 cohort "
                  f"(target {n_target}); skipping group.")
            continue
        replace = n_target > n_avail
        idx = rng.choice(n_avail, size=n_target, replace=replace)
        parts.append(sub.iloc[idx].reset_index(drop=True))

    resampled = pd.concat(parts, ignore_index=True)
    # Shuffle to avoid all-group-1 at start
    resampled = resampled.sample(frac=1, random_state=rng_seed).reset_index(drop=True)
    return resampled


def agegrp_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Print and return a summary of AGEGRP distribution."""
    counts = df["AGEGRP"].value_counts().sort_index()
    total  = len(df)
    rows   = []
    for ag in sorted(AGEGRP_2030_TARGETS):
        n   = int(counts.get(ag, 0))
        pct = n / total if total > 0 else 0.0
        tgt = AGEGRP_2030_TARGETS.get(ag, 0.0)
        rows.append({
            "AGEGRP":      ag,
            "n":           n,
            "actual_%":    round(pct * 100, 2),
            "target_%":    round(tgt * 100, 2),
            "delta_pp":    round((pct - tgt) * 100, 2),
        })
    return pd.DataFrame(rows)


def main(args) -> None:
    print("\n" + "=" * 60)
    print("assemble_scenario_2030_2split.py — Sub-step 6B2")
    print("=" * 60)

    # Resolve data path
    if args.data:
        data_path = args.data
    else:
        # Per OD-1: use R5_lr1e4 raw
        data_path = os.path.join(STEP4_DATA, "sweep", "R5_lr1e4", "augmented_diaries.csv")
        if not os.path.isfile(data_path):
            data_path = os.path.join(STEP4_DATA, "augmented_diaries.csv")

    print(f"  Input: {data_path}")
    if not os.path.isfile(data_path):
        print(f"  ERROR: File not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    # Load
    df = pd.read_csv(data_path, low_memory=False)
    print(f"  Loaded: {len(df):,} rows x {len(df.columns)} cols")

    # Filter to CYCLE_YEAR == 2022
    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    print(f"  Filtered to CYCLE_YEAR=2022: {len(df_2022):,} rows")
    if len(df_2022) == 0:
        print("  ERROR: No CYCLE_YEAR=2022 rows found.", file=sys.stderr)
        sys.exit(1)

    # Check AGEGRP column
    if "AGEGRP" not in df_2022.columns:
        print("  ERROR: AGEGRP column missing.", file=sys.stderr)
        sys.exit(1)

    # Before summary
    print("\n  AGEGRP distribution BEFORE resample (2022 cohort):")
    before_summary = agegrp_summary(df_2022)
    print(before_summary.to_string(index=False))

    # Resample AGEGRP
    print("\n  Resampling AGEGRP to M1 2030 Stats Canada targets ...")
    resampled = resample_agegrp(df_2022, AGEGRP_2030_TARGETS, rng_seed=42)

    # After summary
    print("\n  AGEGRP distribution AFTER resample:")
    after_summary = agegrp_summary(resampled)
    print(after_summary.to_string(index=False))

    # Gate: all groups within ±1pp of target
    max_delta = after_summary["delta_pp"].abs().max()
    if max_delta <= 1.0:
        print(f"\n  AGEGRP gate: max_delta={max_delta:.2f}pp  PASS")
    else:
        print(f"\n  AGEGRP gate: max_delta={max_delta:.2f}pp  [WARN] exceeds 1pp tolerance")

    # Tag metadata
    resampled = resampled.copy()
    resampled["CYCLE_YEAR"] = 2030
    resampled["SCENARIO"]   = "M1_2030"
    if "IS_SYNTHETIC" not in resampled.columns:
        resampled["IS_SYNTHETIC"] = 0  # derived from real 2022 respondents, treated as seed

    # TELEWORK check
    if "TELEWORK" in resampled.columns:
        tw_rate = resampled["TELEWORK"].fillna(0).mean()
        print(f"\n  TELEWORK column present (rate={tw_rate:.4f}). "
              f"WFH-band injection NOT applied here (done in 6D2).")
    if "TELEWORK_KNOWN" not in resampled.columns:
        resampled["TELEWORK_KNOWN"] = 0

    # Row count match
    n_in  = len(df_2022)
    n_out = len(resampled)
    match = "PASS" if n_in == n_out else f"MISMATCH ({n_in} -> {n_out})"
    print(f"\n  Row count: {n_in:,} in -> {n_out:,} out  ({match})")

    # Schema
    print(f"  Columns in output: {len(resampled.columns)}")
    key_cols = ["CYCLE_YEAR", "SCENARIO", "AGEGRP", "SEX", "LFTAG",
                "TELEWORK", "TELEWORK_KNOWN", "DDAY_STRATA"]
    present = [c for c in key_cols if c in resampled.columns]
    missing = [c for c in key_cols if c not in resampled.columns]
    print(f"  Key cols present: {present}")
    if missing:
        print(f"  [WARN] Key cols missing: {missing}")

    if args.verify:
        print("\n  [DRY RUN] --verify mode: no file written.")
        return

    # Write
    out_path = os.path.join(OUTPUT_DIR, "scenario_2030_features_2split.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    resampled.to_csv(out_path, index=False)
    print(f"\n  Written: {out_path}  ({len(resampled):,} rows)")
    print("=" * 60)
    print("6B2 COMPLETE")


def parse_args():
    p = argparse.ArgumentParser(description="Step 6B2 — assemble 2030 scenario features")
    p.add_argument("--data", default=None,
                   help="Path to augmented_diaries.csv (default: R5_lr1e4 per OD-1)")
    p.add_argument("--verify", action="store_true",
                   help="Dry-run: print summary without writing output file")
    return p.parse_args()


if __name__ == "__main__":
    main(parse_args())
