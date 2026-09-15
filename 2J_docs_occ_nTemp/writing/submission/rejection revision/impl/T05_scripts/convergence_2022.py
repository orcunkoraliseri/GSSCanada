#!/usr/bin/env python3
"""
T05 step 3 -- subsample convergence, 2022 only, from the existing N=50 paired-MC campaign.

Input: agg_annual_2022.csv (2022 slice of Step 8's agg_annual.csv, one row per
(archetype, city, sample, sim_hh_id) household -- already carries the paper's own
per-household metrics, computed in 2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py:
  - elec_facility_kWh : annual electricity (line ~361, meter=Electricity:Facility)
  - load_factor       : mean(hourly facility kW) / max(hourly facility kW)      (line 385)
  - midday_share      : facility kWh in hours [9,17) / total facility kWh       (line 387, MIDDAY at line 114)
  - mean_peak_hour    : circular mean of the 365 daily-peak hours (line 372/378/388),
                        via _circular_mean_hour (08_simulation_plots.py:278-285)

For each of the 24 (archetype x city) cells, and for the stock-weighted total, draw
N in {10,20,30,40} households WITHOUT replacement from the 50 (2,000 draws, fixed
seed), and record the across-draw mean + 95% range (2.5/97.5 percentile) of each
metric, plus the N=50 (full-cell) value.

Stock weighting reproduces 08_simulation_plots.py:74-77 (STOCK_WEIGHTS, archetype-only,
renormalized over the 4 modelled archetypes) and 300-321 (_stock_weighted_circular_mean:
each archetype's weight split EQUALLY across its cities, i.e. weight/6 per cell here since
all 4 archetypes have exactly 6 cities in this campaign). Non-circular metrics (kWh,
midday_share, load_factor) use a plain per-cell-weight average; mean_peak_hour uses the
same sin/cos circular-mean construction as the source (08_simulation_plots.py:278-285),
applied to the (already circular-mean) per-household mean_peak_hour values.

Output: convergence_2022.csv, one row per (cell_or_STOCK, metric, N).
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IN_CSV = os.path.join(HERE, "agg_annual_2022.csv")
OUT_CSV = os.path.join(HERE, "..", "T05_out", "convergence_2022.csv")

SEED = 42
N_DRAWS = 2000
SUB_NS = [10, 20, 30, 40]
FULL_N = 50

METRICS = ["elec_facility_kWh", "midday_share", "load_factor"]  # linear metrics
PEAK_COL = "mean_peak_hour"                                     # circular metric

# STOCK_WEIGHTS: 08_simulation_plots.py:75 (raw), :76-77 (renormalized over 4 archetypes)
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}


def circular_mean_hour(hours):
    """Reproduces 08_simulation_plots.py:278-285 _circular_mean_hour."""
    if len(hours) == 0:
        return np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    return float((np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0)


def subsample_stats(values_by_metric, peak_hours, n_hh, n_draws, rng):
    """values_by_metric: dict metric -> np.array (len=50). peak_hours: np.array (len=50).
    Returns dict metric -> (mean_of_draws, lo95, hi95) for the linear metrics + peak hour."""
    idx_full = np.arange(FULL_N)
    draw_idx = np.array([rng.choice(idx_full, size=n_hh, replace=False) for _ in range(n_draws)])
    out = {}
    for m, vals in values_by_metric.items():
        draw_means = vals[draw_idx].mean(axis=1)
        out[m] = (float(draw_means.mean()), float(np.percentile(draw_means, 2.5)),
                   float(np.percentile(draw_means, 97.5)))
    # circular metric: per-draw circular mean of the sampled households' mean_peak_hour
    draw_peak = np.array([circular_mean_hour(peak_hours[d]) for d in draw_idx])
    # circular mean/95% range done on the sin/cos representation to respect the 23->0 wrap
    ang = 2 * np.pi * draw_peak / 24.0
    s_bar, c_bar = np.sin(ang).mean(), np.cos(ang).mean()
    mean_peak = (np.arctan2(s_bar, c_bar) * 24.0 / (2 * np.pi)) % 24.0
    # report percentile range on the unwrapped draw values around the mean (linear
    # percentile on hour-of-day is adequate here: no cell/stock draw distribution in this
    # campaign straddles the 23->0 wrap at its 2.5/97.5 tails -- checked below at runtime).
    lo, hi = np.percentile(draw_peak, 2.5), np.percentile(draw_peak, 97.5)
    out[PEAK_COL] = (float(mean_peak), float(lo), float(hi))
    return out


def main():
    df = pd.read_csv(IN_CSV)
    assert (df["year"].astype(str) == "2022").all(), "expected 2022-only input"

    cells = df.groupby(["arch", "city"])
    cell_keys = sorted(cells.groups.keys())
    assert len(cell_keys) == 24, f"expected 24 cells, got {len(cell_keys)}"

    rows = []
    rng_master = np.random.default_rng(SEED)

    # per-cell data, and full-N=50 value
    cell_data = {}
    for (arch, city), g in cells:
        g = g.sort_values("sample")
        assert len(g) == FULL_N, f"{arch}__{city}: expected {FULL_N} rows, got {len(g)}"
        vals = {m: g[m].to_numpy(dtype=float) for m in METRICS}
        peak = g[PEAK_COL].to_numpy(dtype=float)
        cell_data[(arch, city)] = (vals, peak)
        cell_label = f"{arch}__{city}"

        # N=50 (full cell) row
        for m in METRICS:
            rows.append({"cell": cell_label, "metric": m, "N": FULL_N,
                         "mean": float(vals[m].mean()), "lo95": "", "hi95": ""})
        rows.append({"cell": cell_label, "metric": PEAK_COL, "N": FULL_N,
                     "mean": circular_mean_hour(peak), "lo95": "", "hi95": ""})

        for n_hh in SUB_NS:
            rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
            stats = subsample_stats(vals, peak, n_hh, N_DRAWS, rng)
            for m, (mean_v, lo, hi) in stats.items():
                rows.append({"cell": cell_label, "metric": m, "N": n_hh,
                             "mean": mean_v, "lo95": lo, "hi95": hi})

    # ---- stock-weighted total ----
    # weight per cell = STOCK_WEIGHTS[arch] / n_cities_for_that_arch (08_simulation_plots.py:300-321)
    n_cities_per_arch = df.groupby("arch")["city"].nunique().to_dict()
    cell_weight = {(a, c): STOCK_WEIGHTS[a] / n_cities_per_arch[a] for (a, c) in cell_keys}
    w_sum = sum(cell_weight.values())
    assert abs(w_sum - 1.0) < 1e-9, f"cell weights do not sum to 1: {w_sum}"

    # N=50 stock-weighted value: weighted average of each cell's full-N mean
    for m in METRICS:
        v = sum(cell_weight[k] * cell_data[k][0][m].mean() for k in cell_keys)
        rows.append({"cell": "STOCK", "metric": m, "N": FULL_N, "mean": float(v), "lo95": "", "hi95": ""})
    # circular: weight-average sin/cos of each cell's full-N circular mean
    s_acc = c_acc = 0.0
    for k in cell_keys:
        cm = circular_mean_hour(cell_data[k][1])
        ang = 2 * np.pi * cm / 24.0
        s_acc += cell_weight[k] * np.sin(ang)
        c_acc += cell_weight[k] * np.cos(ang)
    mean_peak_stock = float((np.arctan2(s_acc, c_acc) * 24.0 / (2 * np.pi)) % 24.0)
    rows.append({"cell": "STOCK", "metric": PEAK_COL, "N": FULL_N,
                 "mean": mean_peak_stock, "lo95": "", "hi95": ""})

    # subsampled stock-weighted total: independent draw per cell per iteration, combined by weight
    for n_hh in SUB_NS:
        rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
        idx_full = np.arange(FULL_N)
        # draw_idx[cell] shape (N_DRAWS, n_hh)
        draws = {k: np.array([rng.choice(idx_full, size=n_hh, replace=False) for _ in range(N_DRAWS)])
                 for k in cell_keys}
        for m in METRICS:
            per_cell_draw_means = np.column_stack(
                [cell_data[k][0][m][draws[k]].mean(axis=1) for k in cell_keys])
            w = np.array([cell_weight[k] for k in cell_keys])
            stock_draw = (per_cell_draw_means * w).sum(axis=1)
            rows.append({"cell": "STOCK", "metric": m, "N": n_hh,
                         "mean": float(stock_draw.mean()),
                         "lo95": float(np.percentile(stock_draw, 2.5)),
                         "hi95": float(np.percentile(stock_draw, 97.5))})
        # circular
        per_cell_draw_peak = np.column_stack(
            [np.array([circular_mean_hour(cell_data[k][1][d]) for d in draws[k]]) for k in cell_keys])
        w = np.array([cell_weight[k] for k in cell_keys])
        ang = 2 * np.pi * per_cell_draw_peak / 24.0
        s_draw = (np.sin(ang) * w).sum(axis=1)
        c_draw = (np.cos(ang) * w).sum(axis=1)
        stock_peak_draw = (np.arctan2(s_draw, c_draw) * 24.0 / (2 * np.pi)) % 24.0
        s_bar, c_bar = s_draw.mean(), c_draw.mean()
        mean_peak = (np.arctan2(s_bar, c_bar) * 24.0 / (2 * np.pi)) % 24.0
        rows.append({"cell": "STOCK", "metric": PEAK_COL, "N": n_hh,
                     "mean": float(mean_peak),
                     "lo95": float(np.percentile(stock_peak_draw, 2.5)),
                     "hi95": float(np.percentile(stock_peak_draw, 97.5))})

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False)
    print(f"DONE: wrote {len(out)} rows -> {OUT_CSV}", flush=True)


if __name__ == "__main__":
    main()
