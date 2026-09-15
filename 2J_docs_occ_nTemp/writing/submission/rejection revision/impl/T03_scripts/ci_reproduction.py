#!/usr/bin/env python3
"""
T03 -- WP8 CI reproduction + cell-stratified cluster bootstrap.

(a) Reproduces the submitted paired-delta t-interval CIs for delta midday_share and
    delta load_factor using the EXACT method found at
    2J_docs_occ_nTemp/08_simulation_val.py:951-1027 (SimulationValidator.validate_shift_effect):
      - inner-join agg_annual.csv rows for year==2022 and year==2030 on the index
        (arch, city, sim_hh_id)  [08_simulation_val.py:957-961]
      - delta = value_2030 - value_2022, per matched household              [:963-967]
      - pool ALL paired households across all 24 (arch,city) cells together, unweighted
        (the join above is one flat table, no stock-weighting, no per-cell average first)
      - one-sample 95% Student-t interval:
          scipy.stats.t.interval(0.95, n-1, loc=delta.mean(), scale=scipy.stats.sem(delta))
                                                                              [:973-975]
    Metric definitions (load_factor, midday_share) are from
    2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py:385-387.

(b) Cell-stratified cluster bootstrap, run beside (a) on the SAME input data:
      - within each of the 24 (arch, city) cells, resample households WITH REPLACEMENT
        (n = number of paired households in that cell, <=50), keeping each household's
        own (2022, 2030) pair intact (never split a household's two years apart)
      - pool the 24 cells' bootstrap draws the same way (a) pools the real data: a flat,
        unweighted concatenation across cells
      - 10,000 replicates, fixed seed, percentile interval (2.5 / 97.5)

Input: agg_annual.csv (expected 6,000 rows = 24 cells x 50 households x 5 years).
NOTE: this input contains the defective 2030 rows (WP1 finding). This script is a
METHOD check only -- outputs are NOT for the paper.

Outputs: ci_reproduction.csv (method, metric, point, low, high, n_paired, unit),
         run_meta.json (input provenance, counts, seed, elapsed time, submitted values).
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
from scipy import stats

METRICS = ["midday_share", "load_factor"]

# Submitted manuscript values (writing/submission/archive/2J_manuscript_submission.md:407),
# for the collector to diff against ci_reproduction.csv -- not used in the computation.
SUBMITTED = {
    "midday_share": {"point_pp": 0.367, "ci_pp": [0.208, 0.526]},  # percentage points
    "load_factor": {"point": 0.0117, "ci": [0.0085, 0.0150]},       # raw units
}


def build_paired(annual: pd.DataFrame) -> pd.DataFrame:
    yr22 = annual[annual["year"] == 2022].set_index(["arch", "city", "sim_hh_id"])
    yr30 = annual[annual["year"] == 2030].set_index(["arch", "city", "sim_hh_id"])
    paired = yr22[METRICS].join(yr30[METRICS], lsuffix="_22", rsuffix="_30", how="inner")
    return paired


def method_a_t_interval(paired: pd.DataFrame, metric: str):
    d = paired[f"{metric}_30"] - paired[f"{metric}_22"]
    mean = float(d.mean())
    lo, hi = stats.t.interval(0.95, len(d) - 1, loc=mean, scale=stats.sem(d))
    return mean, float(lo), float(hi), int(len(d))


def method_b_cluster_bootstrap(paired: pd.DataFrame, metric: str, n_rep: int, seed: int):
    d = (paired[f"{metric}_30"] - paired[f"{metric}_22"]).reset_index()
    d.columns = ["arch", "city", "sim_hh_id", "delta"]
    groups = d.groupby(["arch", "city"]).indices  # dict: (arch,city) -> row positions
    cell_arrays = [d["delta"].to_numpy()[idx] for idx in groups.values() if len(idx) > 0]
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_rep, dtype=float)
    for r in range(n_rep):
        pooled = []
        for arr in cell_arrays:
            n = len(arr)
            draw = rng.integers(0, n, size=n)
            pooled.append(arr[draw])
        boot_means[r] = np.concatenate(pooled).mean()
    mean = float(d["delta"].mean())
    lo, hi = np.percentile(boot_means, [2.5, 97.5])
    return mean, float(lo), float(hi), int(len(d)), len(cell_arrays)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg-annual", required=True, help="path to agg_annual.csv")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--n-rep", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=12345)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    t0 = time.time()

    annual = pd.read_csv(args.agg_annual)
    paired = build_paired(annual)

    rows = []
    n_cells = None
    for metric in METRICS:
        mean_a, lo_a, hi_a, n_a = method_a_t_interval(paired, metric)
        rows.append({
            "method": "a_t_interval_submitted_method", "metric": metric,
            "point": mean_a, "low": lo_a, "high": hi_a,
            "n_paired": n_a, "unit": "raw (fraction/ratio, not pp)",
        })

        mean_b, lo_b, hi_b, n_b, n_cells = method_b_cluster_bootstrap(
            paired, metric, n_rep=args.n_rep, seed=args.seed)
        rows.append({
            "method": "b_cell_stratified_cluster_bootstrap", "metric": metric,
            "point": mean_b, "low": lo_b, "high": hi_b,
            "n_paired": n_b, "unit": "raw (fraction/ratio, not pp)",
        })

    out_csv = os.path.join(args.out_dir, "ci_reproduction.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False)

    meta = {
        "input_file": os.path.abspath(args.agg_annual),
        "input_rows": int(len(annual)),
        "paired_n_total": int(len(paired)),
        "n_cells_with_pairs": int(n_cells) if n_cells is not None else None,
        "n_rep": args.n_rep,
        "seed": args.seed,
        "method_a_source": "2J_docs_occ_nTemp/08_simulation_val.py:951-1027 (validate_shift_effect)",
        "metric_defs_source": "2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py:385-387",
        "submitted_values": SUBMITTED,
        "unit_note": (
            "midday_share column is a fraction (0-1); the manuscript reports it in "
            "percentage points (pp) i.e. fraction * 100. load_factor is reported in raw "
            "units in both this script and the manuscript."
        ),
        "important_caveat": (
            "Input agg_annual.csv contains the defective 2030 rows (WP1 finding). "
            "This run is a METHOD check only -- it proves whether we found the right code "
            "and whether the bootstrap changes interval width. Not for the paper."
        ),
        "elapsed_s": time.time() - t0,
    }
    with open(os.path.join(args.out_dir, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"done: {out_csv}")


if __name__ == "__main__":
    main()
