"""
assemble_scenario_2030.py
Step 6 — Sub-step 6B2: Assemble scenario_2030_features.csv

Produces the per-person conditioning file for Sub-stage D Phase ii (2030 forward
forecast). The output has ~37,008 rows — one per synthetic 2030 person — with all
demographic columns the model uses as conditioning input, plus the 2022 observed
diary slots (act30 / hom30) that serve as the encoder seed in Phase ii inference.

Source:  augmented_diaries.csv (Step 4 output), CYCLE_YEAR=2022 rows (~37,008)
Output:  0_Occupancy/Inputs_Step6/scenario_2030_features.csv

Demographic shift applied:
  AGEGRP distribution is resampled to match the Stats Canada 2030 projected
  population structure (medium scenario M1, Table 17-10-0057-01, population 15+).
  All other columns (SEX, MARSTH, HHSIZE, PR, etc.) are carried over as-is from
  the 2022 respondents; the LFTAG / HRSWRK distributions shift naturally as a
  byproduct of AGEGRP resampling (older respondents tend toward retirement / part-time).

Usage (locally):
    py assemble_scenario_2030.py
    py assemble_scenario_2030.py --verify   # print distribution report only, no write
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths (mirrors 06_longitudinalForecasting.py conventions) ─────────────────
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
MODEL_SRC    = PROJECT_ROOT / "2J_docs_occ_nTemp"

AUG_PATH   = MODEL_SRC / "outputs_step4" / "augmented_diaries.csv"
INPUTS_DIR = PROJECT_ROOT / "0_Occupancy" / "Inputs_Step6"
OUT_PATH   = INPUTS_DIR / "scenario_2030_features.csv"

# ── Stats Canada 2030 AGEGRP target distribution ──────────────────────────────
# Source: Statistics Canada Table 17-10-0057-01
#   "Projected population, by projection scenario and age group as of July 1"
#   Medium-growth scenario M1, ~2030, population aged 15 and over, Canada total.
#
# AGEGRP coding (GSS AGEGR10 / unified pipeline):
#   1 = 15–24   2 = 25–34   3 = 35–44   4 = 45–54
#   5 = 55–64   6 = 65–74   7 = 75 and over
#
# Key shift vs. 2022: AGEGRP 6 and 7 grow as baby boomers fully enter retirement;
# AGEGRP 1 and 2 shrink as a share of the 15+ population.
AGEGRP_TARGET_2030: dict[int, float] = {
    1: 0.135,   # 15–24  ↓ from ~17%
    2: 0.165,   # 25–34  ↓ slightly
    3: 0.175,   # 35–44  roughly stable
    4: 0.155,   # 45–54  ↓ slightly
    5: 0.148,   # 55–64  roughly stable
    6: 0.130,   # 65–74  ↑ from ~10%  (boomer cohort)
    7: 0.092,   # 75+    ↑ from ~6%
}
assert abs(sum(AGEGRP_TARGET_2030.values()) - 1.0) < 1e-6, "AGEGRP weights must sum to 1.0"


def resample_to_agegrp(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Resample 2022 rows so that AGEGRP distribution matches AGEGRP_TARGET_2030.

    For each AGEGRP category, draws (with replacement if needed) from the pool
    of 2022 respondents in that category. Final row count equals len(df).
    Row order is shuffled before return.
    """
    rng = np.random.default_rng(seed)
    n_total = len(df)
    cats = sorted(AGEGRP_TARGET_2030.keys())

    # Compute integer target counts; adjust largest bucket for rounding residual
    target_counts: dict[int, int] = {}
    for c in cats:
        target_counts[c] = int(round(AGEGRP_TARGET_2030[c] * n_total))
    residual = n_total - sum(target_counts.values())
    largest = max(target_counts, key=target_counts.get)
    target_counts[largest] += residual

    parts = []
    for cat in cats:
        pool = df[df["AGEGRP"] == cat]
        n_needed = target_counts[cat]
        if n_needed == 0:
            continue
        if len(pool) == 0:
            raise ValueError(
                f"AGEGRP={cat} has 0 rows in 2022 data — cannot resample. "
                f"Check augmented_diaries.csv."
            )
        replace = n_needed > len(pool)
        idx = rng.choice(len(pool), size=n_needed, replace=replace)
        parts.append(pool.iloc[idx])

    result = pd.concat(parts, ignore_index=True)
    # Shuffle so strata aren't block-ordered
    result = result.sample(frac=1, random_state=seed).reset_index(drop=True)
    return result


def print_distribution_report(df22: pd.DataFrame, df30: pd.DataFrame) -> None:
    print("\n── AGEGRP distribution ────────────────────────────────────────────")
    print(f"  {'AGEGRP':<8} {'2022 obs':>10} {'2030 target':>12} {'2030 actual':>12}")
    for cat in sorted(AGEGRP_TARGET_2030):
        obs    = (df22["AGEGRP"] == cat).mean()
        target = AGEGRP_TARGET_2030[cat]
        actual = (df30["AGEGRP"] == cat).mean()
        print(f"  {cat:<8} {obs:>10.3f} {target:>12.3f} {actual:>12.3f}")

    print("\n── LFTAG distribution (natural shift from AGEGRP resampling) ──────")
    for col in ("LFTAG", "HRSWRK"):
        print(f"\n  {col}:")
        obs_d  = df22[col].value_counts(normalize=True).sort_index()
        act_d  = df30[col].value_counts(normalize=True).sort_index()
        for k in sorted(set(obs_d.index) | set(act_d.index)):
            print(f"    {str(k):<6}  2022={obs_d.get(k, 0):.3f}  2030={act_d.get(k, 0):.3f}")

    print(f"\n── Row counts ─────────────────────────────────────────────────────")
    print(f"  2022 base rows : {len(df22):,}")
    print(f"  2030 output rows: {len(df30):,}")
    print(f"  DDAY_STRATA counts: {df30['DDAY_STRATA'].value_counts().sort_index().to_dict()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true",
                        help="Print distribution report only; do not write output file.")
    args = parser.parse_args()

    print(f"Loading {AUG_PATH} ...")
    df = pd.read_csv(AUG_PATH)
    print(f"  Total rows: {len(df):,} | Columns: {df.shape[1]}")

    df22 = df[df["CYCLE_YEAR"] == 2022].copy()
    print(f"  2022 rows  : {len(df22):,}")

    if len(df22) == 0:
        raise RuntimeError("No CYCLE_YEAR=2022 rows found in augmented_diaries.csv.")

    print("Resampling AGEGRP to 2030 target distribution ...")
    df30 = resample_to_agegrp(df22)

    # Tag as 2030 scenario
    df30["CYCLE_YEAR"] = 2030
    df30["SCENARIO"]   = "M1_2030"

    print_distribution_report(df22, df30)

    if args.verify:
        print("\n[verify mode] No file written.")
        return

    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    df30.to_csv(OUT_PATH, index=False)
    print(f"\nSaved: {OUT_PATH}  ({len(df30):,} rows × {df30.shape[1]} columns)")
    print("Ready for Sub-stage D Phase ii inference.")


if __name__ == "__main__":
    main()
