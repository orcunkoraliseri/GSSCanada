"""
Task 33 — Tier 4 fallback rate per cycle (Task 10 scoped, read-only analysis).

Produces:
  - task33_tier_distribution_<year>.csv  (one per cycle, 5 cols)
  - task33_tier_summary_all_cycles.csv   (8 rows: 4 cycles × WD/WE)
  - task33_cvae_reconstruction_stats.csv (CVAE Confidence/Diff stats, broken out by feature type)
  - task33_2025_cvae_summary.csv         (one-row summary for paper footnote)

Zero pipeline code touched.  Run from project root:
    py -3 eSim_tests/run_task33_tier_analysis.py
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUT_DIR      = SCRIPT_DIR   # write outputs next to this script

BEM_DIR      = PROJECT_ROOT / "BEM_Setup"
OCC_DIR      = PROJECT_ROOT / "0_Occupancy"

CYCLES = [
    ("2005", "06CEN05GSS"),
    ("2010", "11CEN10GSS"),
    ("2015", "16CEN15GSS"),
    ("2022", "21CEN22GSS"),
]

KNOWN_TIERS = ["1_Perfect", "2_Core", "3_Constraints", "4_FailSafe"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tier_distribution(series: pd.Series, label: str) -> dict:
    """
    Return counts and percentages for each known tier.
    Emits a warning (to stdout) for any value outside KNOWN_TIERS.
    """
    vc = series.value_counts(dropna=False)
    unexpected = [v for v in vc.index if v not in KNOWN_TIERS and not pd.isna(v)]
    if unexpected:
        print(f"  WARNING [{label}]: unexpected tier values: {unexpected}")
        for uv in unexpected:
            print(f"    -> '{uv}': count={vc[uv]}")

    # Reindex to known taxonomy; unknown values will be handled separately
    counts = vc.reindex(KNOWN_TIERS, fill_value=0)
    total  = series.notna().sum()
    pcts   = (counts / total * 100).round(2) if total > 0 else counts * 0.0

    result = {}
    for tier in KNOWN_TIERS:
        result[f"count_{tier}"] = int(counts[tier])
        result[f"pct_{tier}"]   = float(pcts[tier])

    # Also capture unexpected values so they appear in the per-cycle CSV
    for uv in unexpected:
        result[f"count_{uv}"] = int(vc[uv])
        result[f"pct_{uv}"]   = round(float(vc[uv] / total * 100), 2) if total > 0 else 0.0

    return result


def escalate(msg: str):
    print(f"\nESCALATION TRIGGER: {msg}")
    sys.exit(2)

# ---------------------------------------------------------------------------
# Step 1 — Tier distribution for tiered cycles
# ---------------------------------------------------------------------------
print("=" * 60)
print("Task 33 — Tier 4 rate analysis")
print("=" * 60)

# NOTE ON TIER LABEL NAMES:
# The spec references taxonomy 1_Exact / 2_Core / 3_Constraints / 4_Fallback.
# The actual labels in the Matched_Keys CSV files are:
#   1_Perfect  (spec: 1_Exact)
#   2_Core     (matches)
#   3_Constraints (matches)
#   4_FailSafe (spec: 4_Fallback)
# These are the same 4 tiers — just named slightly differently.
# They are treated as the canonical labels and reported verbatim.

coverage_rows = []   # for the join-coverage report
summary_rows  = []   # for task33_tier_summary_all_cycles.csv

for year, prefix in CYCLES:
    print(f"\n--- Cycle {year} ({prefix}) ---")

    # BEM Schedules — deduplicate on SIM_HH_ID
    bem_path = BEM_DIR / f"BEM_Schedules_{year}.csv"
    bem_raw  = pd.read_csv(bem_path)
    bem      = bem_raw.drop_duplicates(subset="SIM_HH_ID", keep="first")
    n_bem    = len(bem)
    print(f"  BEM raw rows: {len(bem_raw):,}  ->  deduplicated HHs: {n_bem:,}")

    # Matched Keys — deduplicate on SIM_HH_ID
    mk_path  = OCC_DIR / f"Outputs_{prefix}" / "ProfileMatching" / f"{prefix}_Matched_Keys_sample25pct.csv"
    mk_raw   = pd.read_csv(mk_path)
    mk       = mk_raw.drop_duplicates(subset="SIM_HH_ID", keep="first")
    n_matched = len(mk)
    print(f"  Matched_Keys raw rows: {len(mk_raw):,}  ->  deduplicated HHs: {n_matched:,}")

    # Inner join
    joined   = bem.merge(mk[["SIM_HH_ID", "MATCH_TIER_WD", "MATCH_TIER_WE"]],
                         on="SIM_HH_ID", how="inner")
    n_joined  = len(joined)
    n_dropped = n_bem - n_joined
    join_rate = n_joined / n_bem * 100 if n_bem > 0 else 0.0
    print(f"  Joined: {n_joined:,}  dropped (BEM side): {n_dropped:,}  coverage: {join_rate:.2f}%")

    # Escalate if coverage < 50%
    if join_rate < 50.0:
        escalate(f"Cycle {year}: join coverage {join_rate:.2f}% < 50% — schema/sampling mismatch. "
                 "Do not trust tier percentages. Investigate before proceeding.")

    coverage_rows.append({
        "cycle":     year,
        "n_bem":     n_bem,
        "n_matched": n_matched,
        "n_joined":  n_joined,
        "n_dropped": n_dropped,
        "join_rate_pct": round(join_rate, 2),
    })

    # Tier distributions
    dist_wd = tier_distribution(joined["MATCH_TIER_WD"], f"{year}/WD")
    dist_we = tier_distribution(joined["MATCH_TIER_WE"], f"{year}/WE")

    # Build per-cycle distribution CSV (5 standard columns per spec)
    tier_rows = []
    for tier in KNOWN_TIERS:
        tier_rows.append({
            "tier":     tier,
            "count_wd": dist_wd.get(f"count_{tier}", 0),
            "pct_wd":   dist_wd.get(f"pct_{tier}", 0.0),
            "count_we": dist_we.get(f"count_{tier}", 0),
            "pct_we":   dist_we.get(f"pct_{tier}", 0.0),
        })

    # Add unexpected tiers to per-cycle CSV if any
    extra_keys = set(dist_wd.keys()) | set(dist_we.keys())
    extra_tiers = [
        k.replace("count_", "") for k in extra_keys
        if k.startswith("count_") and k.replace("count_", "") not in KNOWN_TIERS
    ]
    for et in extra_tiers:
        tier_rows.append({
            "tier":     et,
            "count_wd": dist_wd.get(f"count_{et}", 0),
            "pct_wd":   dist_wd.get(f"pct_{et}", 0.0),
            "count_we": dist_we.get(f"count_{et}", 0),
            "pct_we":   dist_we.get(f"pct_{et}", 0.0),
        })

    dist_df = pd.DataFrame(tier_rows)
    out_path = OUT_DIR / f"task33_tier_distribution_{year}.csv"
    dist_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.name}")
    print(dist_df.to_string(index=False))

    # Append to cross-cycle summary
    for day_type, dist in [("WD", dist_wd), ("WE", dist_we)]:
        summary_rows.append({
            "cycle":     year,
            "day_type":  day_type,
            "n_joined":  n_joined,
            "tier1_pct": dist.get("pct_1_Perfect", 0.0),
            "tier2_pct": dist.get("pct_2_Core",    0.0),
            "tier3_pct": dist.get("pct_3_Constraints", 0.0),
            "tier4_pct": dist.get("pct_4_FailSafe", 0.0),
        })

# ---------------------------------------------------------------------------
# Step 3 — Cross-cycle summary table (built alongside Step 1 above)
# ---------------------------------------------------------------------------
summary_df = pd.DataFrame(summary_rows, columns=[
    "cycle", "day_type", "n_joined",
    "tier1_pct", "tier2_pct", "tier3_pct", "tier4_pct"
])
summary_path = OUT_DIR / "task33_tier_summary_all_cycles.csv"
summary_df.to_csv(summary_path, index=False)
print(f"\nSaved cross-cycle summary: {summary_path.name}")
print(summary_df.to_string(index=False))

# Max Tier 4 rate
max_tier4 = summary_df["tier4_pct"].max()
max_tier4_row = summary_df.loc[summary_df["tier4_pct"].idxmax()]
print(f"\nMax Tier 4 rate: {max_tier4:.2f}% in cycle {max_tier4_row['cycle']} ({max_tier4_row['day_type']})")
print(f"CLAUDE.md claim: < 0.5%  ->  {'PASSES' if max_tier4 < 0.5 else 'EXCEEDS -- flag for paper discussion'}")

# ---------------------------------------------------------------------------
# Step 2 — 2025 CVAE reconstruction-error summary
# ---------------------------------------------------------------------------
print("\n--- 2025 CVAE Reconstruction-Error Summary ---")

cvae_path = OCC_DIR / "Outputs_CENSUS" / "Validation_VAE_Reconstruction" / "validation_vae_reconstruction.csv"
cvae_df   = pd.read_csv(cvae_path)

print(f"  CVAE file shape: {cvae_df.shape}")
print(f"  CVAE columns: {cvae_df.columns.tolist()}")

# Escalate if empty
if cvae_df.empty:
    escalate("CVAE validation file is empty.")

# Identify reconstruction-error column.
# Expected keywords: "error", "err", "loss", "mse", "recon"
keywords = ["error", "err", "loss", "mse", "recon"]
numeric_cols = cvae_df.select_dtypes(include="number").columns.tolist()
candidate_cols = [c for c in numeric_cols if any(kw in c.lower() for kw in keywords)]

if candidate_cols:
    chosen_col = candidate_cols[0]
    col_choice_note = (
        f"Chosen column '{chosen_col}' (matched keyword pattern in column name)."
    )
else:
    # No column name matches — pick 'Confidence/Diff' as best available
    # (for continuous features it is |Original − Predicted|, a true reconstruction error;
    #  for categorical features it is the softmax confidence, not an error)
    if "Confidence/Diff" in cvae_df.columns:
        chosen_col = "Confidence/Diff"
        col_choice_note = (
            "WARNING: No column name contains expected keywords ('error', 'err', 'loss', 'mse', 'recon'). "
            "Falling back to 'Confidence/Diff' — the only numeric quality metric in the file. "
            "For Continuous features this equals |Original - Predicted| (true reconstruction error). "
            "For Categorical features it equals the softmax confidence of the correct class "
            "(higher = better; NOT an error metric). "
            "Stats are reported separately for all rows and for Continuous-only rows."
        )
    else:
        escalate(
            "CVAE file does not contain a column identifiable as a reconstruction-error metric. "
            "Columns found: " + str(cvae_df.columns.tolist())
        )

print(f"\n  Column choice: {chosen_col}")
print(f"  Note: {col_choice_note}")

n_samples = cvae_df["Sample_ID"].nunique()
print(f"  Unique Sample_IDs: {n_samples}")

# Compute stats on the full file and on continuous-only rows
rows_stats = []
for subset_label, subset_df in [
    ("all_features",  cvae_df),
    ("continuous_only", cvae_df[cvae_df["Type"] == "Continuous"]),
    ("categorical_only", cvae_df[cvae_df["Type"] == "Categorical"]),
]:
    col_data = subset_df[chosen_col].dropna()
    n = len(col_data)
    if n == 0:
        continue
    rows_stats.append({
        "subset":  subset_label,
        "column":  chosen_col,
        "n":       n,
        "mean":    round(col_data.mean(), 6),
        "median":  round(col_data.median(), 6),
        "std":     round(col_data.std(), 6),
        "p90":     round(col_data.quantile(0.90), 6),
        "p99":     round(col_data.quantile(0.99), 6),
        "max":     round(col_data.max(), 6),
    })

stats_df = pd.DataFrame(rows_stats)
stats_path = OUT_DIR / "task33_cvae_reconstruction_stats.csv"
stats_df.to_csv(stats_path, index=False)
print(f"\n  Saved: {stats_path.name}")
print(stats_df.to_string(index=False))

# One-row summary for paper: use continuous-only stats
cont_row = stats_df[stats_df["subset"] == "continuous_only"].iloc[0]

summary_2025_df = pd.DataFrame([{
    "cycle":   2025,
    "metric":  "cvae_recon_error",
    "n":       int(cont_row["n"]),
    "mean":    cont_row["mean"],
    "median":  cont_row["median"],
    "p90":     cont_row["p90"],
    "p99":     cont_row["p99"],
    "max":     cont_row["max"],
}])
summary_2025_path = OUT_DIR / "task33_2025_cvae_summary.csv"
summary_2025_df.to_csv(summary_2025_path, index=False)
print(f"\n  Saved: {summary_2025_path.name}")
print(summary_2025_df.to_string(index=False))

# Attempt join to BEM_Schedules_2025.csv
print("\n  Checking for SIM_HH_ID in CVAE file for join to BEM_Schedules_2025...")
if "SIM_HH_ID" in cvae_df.columns:
    bem_2025 = pd.read_csv(BEM_DIR / "BEM_Schedules_2025.csv")
    bem_2025_dedup = bem_2025.drop_duplicates(subset="SIM_HH_ID", keep="first")
    n_cvae_ids = cvae_df["SIM_HH_ID"].nunique()
    joined_2025 = cvae_df.drop_duplicates(subset="SIM_HH_ID").merge(
        bem_2025_dedup[["SIM_HH_ID"]], on="SIM_HH_ID", how="inner"
    )
    join_2025_rate = len(joined_2025) / n_cvae_ids * 100 if n_cvae_ids > 0 else 0.0
    print(f"  CVAE unique IDs: {n_cvae_ids}, joined to BEM: {len(joined_2025)}, "
          f"coverage: {join_2025_rate:.2f}%")
    cvae_sim_hh_join_result = (
        f"SIM_HH_ID found in CVAE file; {len(joined_2025)} of {n_cvae_ids} "
        f"CVAE samples joined to BEM_Schedules_2025 ({join_2025_rate:.1f}% coverage)."
    )
else:
    print("  No SIM_HH_ID column in CVAE file — join to BEM_Schedules_2025 not possible.")
    cvae_sim_hh_join_result = (
        "No SIM_HH_ID column found in validation_vae_reconstruction.csv. "
        "This file is a feature-level validation summary (10 sample IDs × 25 features), "
        "not a per-household reconstruction record. "
        "The join to BEM_Schedules_2025.csv is not applicable."
    )

# ---------------------------------------------------------------------------
# Print coverage table
# ---------------------------------------------------------------------------
print("\n--- Join Coverage Table ---")
coverage_df = pd.DataFrame(coverage_rows)
print(coverage_df.to_string(index=False))

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
print("\n--- Analysis complete ---")
print(f"Max Tier 4 (4_FailSafe) rate: {max_tier4:.4f}%")
print(f"Claim check (< 0.5%): {'PASS' if max_tier4 < 0.5 else 'FAIL — exceeds CLAUDE.md claim'}")
print(f"\nStore these values for the report:")
print(f"  cvae_sim_hh_join_result: {cvae_sim_hh_join_result}")
print(f"  col_choice_note: {col_choice_note}")
print(f"  n_samples (CVAE): {n_samples}")
print(f"  cont_row stats: n={int(cont_row['n'])}, mean={cont_row['mean']}, "
      f"median={cont_row['median']}, P90={cont_row['p90']}, "
      f"P99={cont_row['p99']}, max={cont_row['max']}")
