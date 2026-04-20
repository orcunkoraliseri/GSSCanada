"""
Task 30 Step 1 — SSE distribution dump for the Worker target profile.

Loads BEM_Schedules_2022.csv (SingleD), finds the best-match household under
the default TARGET_WORKING_PROFILE (Worker), exports the full SSE distance CSV,
plots a histogram, and prints summary statistics.

Usage:
    py -3 eSim_tests/task30_dump_sse.py
"""
import os
import sys
import csv as csv_mod

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import eSim_bem_utils.integration as integration

TESTS_DIR = os.path.dirname(__file__)
CSV_2022  = os.path.join(PROJECT_ROOT, "BEM_Setup", "BEM_Schedules_2022.csv")
SSE_CSV   = os.path.join(TESTS_DIR, "task30_sse_distances_2022.csv")
HIST_PNG  = os.path.join(TESTS_DIR, "task30_sse_histogram_2022.png")


def main():
    print("=" * 60)
    print("Task 30 Step 1 — SSE distribution dump (Worker profile)")
    print("=" * 60)

    # 1. Load schedules
    schedules = integration.load_schedules(CSV_2022, dwelling_type="SingleD", region=None)
    print(f"Loaded {len(schedules)} households after sanity filter.")

    # 2. Find best-match household under default Worker profile
    best_hh = integration.find_best_match_household(schedules)
    print(f"Best-match HH (Worker): {best_hh}")

    # 3. Export full SSE distances CSV
    integration.export_sse_distances_csv(schedules, SSE_CSV, included_ids=[best_hh])

    # 4. Read CSV back for stats and plot
    rows = []
    with open(SSE_CSV, newline="", encoding="utf-8") as f:
        for r in csv_mod.DictReader(f):
            rows.append({
                "HH_ID":        r["HH_ID"],
                "SSE":          float(r["SSE_to_target"]),
                "included":     int(r["included"]),
                "hhsize":       r["hhsize"],
                "match_tier":   r["match_tier"],
            })

    sses      = [r["SSE"] for r in rows]
    best_sse  = next(r["SSE"] for r in rows if r["included"] == 1)
    n         = len(sses)
    sses_sorted = sorted(sses)
    p10 = sses_sorted[int(n * 0.10)]
    p50 = sses_sorted[int(n * 0.50)]
    p90 = sses_sorted[int(n * 0.90)]
    rank = sum(1 for s in sses if s <= best_sse)
    pct_rank = rank / n * 100

    print(f"\nSSE summary ({n} households):")
    print(f"  P10:              {p10:.4f}")
    print(f"  Median (P50):     {p50:.4f}")
    print(f"  P90:              {p90:.4f}")
    print(f"  Best-HH SSE:      {best_sse:.4f}")
    print(f"  Best-HH rank:     {rank}/{n}  ({pct_rank:.1f} percentile)")

    # 5. Demographic breakdown of top-100 by SSE
    top100 = sorted(rows, key=lambda r: r["SSE"])[:100]
    sizes  = {}
    tiers  = {}
    for r in top100:
        sizes[r["hhsize"]] = sizes.get(r["hhsize"], 0) + 1
        tiers[r["match_tier"]] = tiers.get(r["match_tier"], 0) + 1
    print("\nTop-100 household-size distribution:")
    for k, v in sorted(sizes.items(), key=lambda x: -x[1]):
        print(f"  hhsize={k}: {v}")
    print("Top-100 match-tier distribution:")
    for k, v in sorted(tiers.items(), key=lambda x: -x[1]):
        print(f"  tier={k}: {v}")

    # Full cohort for comparison
    all_sizes = {}
    all_tiers = {}
    for r in rows:
        all_sizes[r["hhsize"]] = all_sizes.get(r["hhsize"], 0) + 1
        all_tiers[r["match_tier"]] = all_tiers.get(r["match_tier"], 0) + 1
    print("\nFull cohort household-size distribution:")
    for k, v in sorted(all_sizes.items(), key=lambda x: -x[1]):
        print(f"  hhsize={k}: {v}")
    print("Full cohort match-tier distribution:")
    for k, v in sorted(all_tiers.items(), key=lambda x: -x[1]):
        print(f"  tier={k}: {v}")

    # 6. Plot histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(sses, bins=100, color="steelblue", edgecolor="none", alpha=0.8)
    ax.axvline(best_sse, color="red", linewidth=1.5,
               label=f"Best-HH SSE={best_sse:.3f} (p{pct_rank:.0f})")
    ax.set_xlabel("SSE to TARGET_WORKING_PROFILE")
    ax.set_ylabel("Count")
    ax.set_title("SSE Distance Distribution — BEM_Schedules_2022 (SingleD, Worker profile)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HIST_PNG, dpi=120)
    print(f"\nHistogram saved: {os.path.basename(HIST_PNG)}")

    return {
        "best_hh": best_hh,
        "best_sse": best_sse,
        "pct_rank": pct_rank,
        "n": n,
        "p10": p10, "p50": p50, "p90": p90,
        "top100_sizes": sizes,
        "top100_tiers": tiers,
        "all_sizes": all_sizes,
        "all_tiers": all_tiers,
    }


if __name__ == "__main__":
    stats = main()
    print("\nStep 1 complete.")
    sys.exit(0)
