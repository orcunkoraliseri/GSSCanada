# -*- coding: utf-8 -*-
"""
assemble_scenario_2030_4split.py
Sub-step 6B2 (Leg-3) — Scenario Assembly for 2030 Synthetic Population

Port of Leg-2's assemble_scenario_2030_2split.py, verbatim in structure. No
retail-conditioning feature column is added — per the runbook (§8 of the
builder prompt): "no retail conditioning is added to the model" and the
retail lever is entirely post-hoc, applied downstream of this feature file by
a separate script (3rdJ_06_retail_lever_4split.py, not built in this
session). Leg-2 had no analogous column for the office WFH bands either (WFH-
band injection also happens downstream, in 6D2's post-hoc reweight) — so
there is nothing to extend here.

Pipeline:
  1. Load the raw pool augmented_diaries.csv (seed_3_g3fix default; --data override).
  2. Filter to CYCLE_YEAR == 2022 (most recent observed cycle, structural template).
  3. Resample AGEGRP column to M1 2030 Stats Canada targets via weighted resampling.
  4. Keep TELEWORK / TELEWORK_KNOWN columns as-is (WFH-band injection is done in
     6D2's post-hoc reweight, not here).
  5. Tag CYCLE_YEAR = 2030 and SCENARIO = M1_2030.
  6. Write to outputs_step6/scenario_2030_features_4split.csv.

Modes:
  py -3 -X utf8 assemble_scenario_2030_4split.py --verify   # dry-run: print summary, no write
  py -3 -X utf8 assemble_scenario_2030_4split.py            # write mode

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
    _LEG3_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG3_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split"
else:
    _LEG3_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg3_4-split",
    )

STEP4_DATA = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")
STEP6_DIR  = os.path.join(_LEG3_BASE, "Step6_docs")
OUTPUT_DIR = os.path.join(STEP6_DIR, "outputs_step6")

# Same raw-pool resolution order as the main Step-6 script (seed_3_g3fix
# accepted-wholesale per Step-4's 2026-07-21 Progress Log decision).
_RAW_POOL_CANDIDATES = [
    os.path.join(STEP4_DATA, "seed_3_g3fix", "augmented_diaries.csv"),
    os.path.join(STEP4_DATA, "seed_3", "augmented_diaries.csv"),
    os.path.join(STEP4_DATA, "augmented_diaries.csv"),
]


def _default_raw_pool_path() -> str:
    for p in _RAW_POOL_CANDIDATES:
        if os.path.isfile(p):
            return p
    return _RAW_POOL_CANDIDATES[0]


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
    """
    N = len(df)
    rng = np.random.default_rng(rng_seed)

    target_counts = {}
    for ag, share in targets.items():
        target_counts[ag] = int(round(share * N))

    deficit = N - sum(target_counts.values())
    if deficit != 0:
        largest_ag = max(target_counts, key=lambda k: target_counts[k])
        target_counts[largest_ag] += deficit

    assert sum(target_counts.values()) == N, "Target count adjustment failed"

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
    print("assemble_scenario_2030_4split.py — Sub-step 6B2 (Leg-3)")
    print("=" * 60)

    if args.data:
        data_path = args.data
    else:
        data_path = _default_raw_pool_path()

    print(f"  Input: {data_path}")
    if not os.path.isfile(data_path):
        print(f"  ERROR: File not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(data_path, low_memory=False)
    print(f"  Loaded: {len(df):,} rows x {len(df.columns)} cols")

    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    print(f"  Filtered to CYCLE_YEAR=2022: {len(df_2022):,} rows")
    if len(df_2022) == 0:
        print("  ERROR: No CYCLE_YEAR=2022 rows found.", file=sys.stderr)
        sys.exit(1)

    if "AGEGRP" not in df_2022.columns:
        print("  ERROR: AGEGRP column missing.", file=sys.stderr)
        sys.exit(1)

    print("\n  AGEGRP distribution BEFORE resample (2022 cohort):")
    before_summary = agegrp_summary(df_2022)
    print(before_summary.to_string(index=False))

    print("\n  Resampling AGEGRP to M1 2030 Stats Canada targets ...")
    resampled = resample_agegrp(df_2022, AGEGRP_2030_TARGETS, rng_seed=42)

    print("\n  AGEGRP distribution AFTER resample:")
    after_summary = agegrp_summary(resampled)
    print(after_summary.to_string(index=False))

    max_delta = after_summary["delta_pp"].abs().max()
    if max_delta <= 1.0:
        print(f"\n  AGEGRP gate: max_delta={max_delta:.2f}pp  PASS")
    else:
        print(f"\n  AGEGRP gate: max_delta={max_delta:.2f}pp  [WARN] exceeds 1pp tolerance")

    resampled = resampled.copy()
    resampled["CYCLE_YEAR"] = 2030
    resampled["SCENARIO"]   = "M1_2030"
    if "IS_SYNTHETIC" not in resampled.columns:
        resampled["IS_SYNTHETIC"] = 0  # derived from real 2022 respondents, treated as seed

    if "TELEWORK" in resampled.columns:
        tw_rate = resampled["TELEWORK"].fillna(0).mean()
        print(f"\n  TELEWORK column present (rate={tw_rate:.4f}). "
              f"WFH-band injection NOT applied here (done in 6D2).")
    if "TELEWORK_KNOWN" not in resampled.columns:
        resampled["TELEWORK_KNOWN"] = 0

    # Informational only: retail marginal is carried through unmodified (no
    # lever applied here — see module docstring).
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49) if f"ret30_{i:03d}" in resampled.columns]
    if ret_cols:
        ret_rate = resampled[ret_cols].values.astype(float).mean()
        print(f"  ret30 columns carried through unmodified (rate={ret_rate:.4f}). "
              f"No retail-lever feature column added (per §8 — lever is post-hoc, downstream).")

    n_in  = len(df_2022)
    n_out = len(resampled)
    match = "PASS" if n_in == n_out else f"MISMATCH ({n_in} -> {n_out})"
    print(f"\n  Row count: {n_in:,} in -> {n_out:,} out  ({match})")

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

    out_path = os.path.join(OUTPUT_DIR, "scenario_2030_features_4split.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    resampled.to_csv(out_path, index=False)
    print(f"\n  Written: {out_path}  ({len(resampled):,} rows)")
    print("=" * 60)
    print("6B2 COMPLETE")


def parse_args():
    p = argparse.ArgumentParser(description="Step 6B2 (Leg-3) — assemble 2030 scenario features")
    p.add_argument("--data", default=None,
                   help="Path to the raw pool augmented_diaries.csv "
                        "(default: seed_3_g3fix, falls back to seed_3 then flat file)")
    p.add_argument("--verify", action="store_true",
                   help="Dry-run: print summary without writing output file")
    return p.parse_args()


if __name__ == "__main__":
    main(parse_args())
