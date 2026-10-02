# -*- coding: utf-8 -*-
"""Figure 5 (district spread). Columns = heating, cooling, total electricity (equipment is a schedule pass-through and is omitted).
Row 1: distribution of the N surrogate district annual totals (MWh, scope all dwellings), median solid, 5th-95th percentile shaded.
Row 2: the 20 EnergyPlus check draws, S (filled) and EnergyPlus (open), same draw joined by a thin line, on its own x axis
(row 1 has its own x axis around the N draws: the level gap between S and EnergyPlus would squeeze the distribution to a sliver).
Row 3: running median and 90 % interval against the number of draws (log x), from district_spread.csv (scope all, metric annual).
Inputs: fig5_draws.parquet (fig05_data.py), district_spread.csv, district_check_draws.csv. No test-split file. Speed job only.

Usage: fig05_district_spread.py --draws fig5_draws.parquet --spread district_spread.csv --check district_check_draws.csv --out DIR
Read-back check: the drawn medians (read from the figure) equal district_spread.csv (row 3 exactly, row 1 rel 1e-5), one planted change must fire.
"""
import argparse, sys, os
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_common as fc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter, FixedLocator

TG = [("heating", "Heating"), ("cooling", "Cooling"), ("total_elec", "Total electricity")]
COL_S = fc.MODEL_COLOUR["S"]
BAR = "#CBD5E1"


def norm(t):
    t = str(t)
    return t[:-4] if t.endswith("_kwh") else t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", required=True)
    ap.add_argument("--spread", required=True)
    ap.add_argument("--check", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tab = pd.read_parquet(a.draws)
    sp = pd.read_csv(a.spread)
    sp["target"] = sp["target"].map(norm)
    cd = pd.read_csv(a.check)
    cd["target"] = cd["target"].map(norm)
    cd = cd[cd["scope"] == "all"]
    N = int(tab["draw"].nunique())
    chk_draws = sorted(int(d) for d in cd["draw"].unique())
    print("INFO N=%d check draws=%d" % (N, len(chk_draws)), flush=True)

    fig = plt.figure(figsize=(fc.W2, 150 * fc.MM))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.5, 0.75, 1.5], left=0.105, right=0.992, top=0.915, bottom=0.095, hspace=0.62, wspace=0.30)
    med_top, med_run, band_run, strip_pts = {}, {}, {}, {}
    for ci, (t, tname) in enumerate(TG):
        sub = tab[tab["target"] == t].sort_values("draw")
        x = sub["annual_kwh"].to_numpy(dtype=float) / 1000.0
        med, p05, p95 = float(np.median(x)), float(np.percentile(x, 5)), float(np.percentile(x, 95))
        c = cd[cd["target"] == t].sort_values("draw")
        dS = np.array([float(sub.loc[sub["draw"] == int(d), "annual_kwh"].iloc[0]) for d in c["draw"]]) / 1000.0
        dE = c["annual_E_kwh"].to_numpy(dtype=float) / 1000.0
        lo, hi = min(x.min(), dS.min(), dE.min()), max(x.max(), dS.max(), dE.max())
        pad = 0.04 * (hi - lo)
        xlim = (lo - pad, hi + pad)
        # row 1: distribution
        ax1 = fig.add_subplot(gs[0, ci])
        ax1.hist(x, bins=40, range=(x.min(), x.max()), color=BAR, edgecolor="white", linewidth=0.3, zorder=1)
        ax1.axvspan(p05, p95, color=COL_S, alpha=0.12, lw=0, zorder=2)
        ml = ax1.axvline(med, color=COL_S, lw=1.0, zorder=3)
        med_top[t] = ml
        pad1 = 0.04 * (x.max() - x.min())
        ax1.set_xlim(x.min() - pad1, x.max() + pad1)
        ax1.xaxis.set_major_locator(plt.MaxNLocator(4))
        ax1.set_title(tname, fontsize=8, fontweight="bold", pad=4)
        ax1.set_xlabel("District annual total (MWh)")
        if ci == 0:
            ax1.set_ylabel("Draws")
        # row 2: check draws, S vs EnergyPlus
        ax2 = fig.add_subplot(gs[1, ci])
        ax2.set_xlim(*xlim)
        for s_, e_ in zip(dS, dE):
            ax2.plot([s_, e_], [1, 0], color="#94A3B8", lw=0.4, zorder=1)
        ps, = ax2.plot(dS, np.ones_like(dS), ls="none", marker="o", ms=3.2, mfc=COL_S, mec="white", mew=0.3, zorder=3)
        pe, = ax2.plot(dE, np.zeros_like(dE), ls="none", marker="o", ms=3.6, mfc="white", mec="#111111", mew=0.7, zorder=3)
        strip_pts[t] = (ps, pe)
        ax2.set_ylim(-0.6, 1.6)
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(["EnergyPlus", "S"] if ci == 0 else ["", ""])
        ax2.tick_params(axis="y", length=2.5 if ci == 0 else 0)
        ax2.set_xlabel("District annual total (MWh)")
        ax2.spines["left"].set_visible(False)
        ax2.tick_params(axis="y", length=0)
        # row 3: running median and 90 % interval
        ax3 = fig.add_subplot(gs[2, ci])
        r = sp[(sp["scope"] == "all") & (sp["target"] == t) & (sp["metric"] == "annual")].drop_duplicates("n_draws").sort_values("n_draws")
        n = r["n_draws"].to_numpy(dtype=float)
        m_ = r["median_kwh"].to_numpy(dtype=float) / 1000.0
        l_ = r["p05_kwh"].to_numpy(dtype=float) / 1000.0
        u_ = r["p95_kwh"].to_numpy(dtype=float) / 1000.0
        bc = ax3.fill_between(n, l_, u_, color=COL_S, alpha=0.15, lw=0, zorder=2)
        ln, = ax3.plot(n, m_, color=COL_S, lw=1.0, marker="o", ms=2.8, mfc=COL_S, mec="white", mew=0.3, zorder=3)
        med_run[t], band_run[t] = ln, bc
        ax3.set_xscale("log")
        ax3.xaxis.set_major_locator(FixedLocator([10, 100, 1000]))
        ax3.xaxis.set_major_formatter(ScalarFormatter())
        ax3.xaxis.set_minor_formatter(plt.NullFormatter())
        ax3.set_xlim(8, 1.3 * n.max())
        ax3.set_xlabel("Number of draws")
        ax3.grid(axis="y", color=fc.GRID, lw=0.5, zorder=0)
        ax3.set_axisbelow(True)
        if ci == 0:
            ax3.set_ylabel("District annual total (MWh)")
    handles = [Patch(facecolor=BAR, label="Surrogate draws"),
               Line2D([], [], color=COL_S, lw=1.0, label="Median"),
               Patch(facecolor=COL_S, alpha=0.15, label="90 % interval"),
               Line2D([], [], ls="none", marker="o", ms=4, mfc=COL_S, mec="white", mew=0.3, label="S, check draws"),
               Line2D([], [], ls="none", marker="o", ms=4.2, mfc="white", mec="#111111", mew=0.7, label="EnergyPlus, same draws")]
    fig.legend(handles=handles, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.55, 0.998), handletextpad=0.4, columnspacing=1.2)

    # checks: drawn quantities read back from the figure against district_spread.csv (a pandas filter, not the arrays used to draw)
    fig.canvas.draw()
    bad_run, bad_band, bad_top, bad_pts = [], [], [], []
    for t, _ in TG:
        r = sp[(sp["scope"] == "all") & (sp["target"] == t) & (sp["metric"] == "annual")].drop_duplicates("n_draws").sort_values("n_draws")
        want_m = r["median_kwh"].to_numpy(dtype=float) / 1000.0
        got_m = np.asarray(med_run[t].get_ydata(), dtype=float)
        if len(got_m) != len(want_m) or not np.allclose(got_m, want_m, rtol=1e-9, atol=0):
            bad_run.append(t)
        verts = band_run[t].get_paths()[0].vertices[:, 1]
        want_b = set((r["p05_kwh"].to_numpy(dtype=float) / 1000.0).tolist()) | set((r["p95_kwh"].to_numpy(dtype=float) / 1000.0).tolist())
        if set(np.asarray(verts, dtype=float).tolist()) != want_b:
            bad_band.append(t)
        rN = sp[(sp["scope"] == "all") & (sp["target"] == t) & (sp["metric"] == "annual") & (sp["n_draws"] == N)]
        if len(rN) != 1 or not np.isclose(float(med_top[t].get_xdata()[0]) * 1000.0, float(rN["median_kwh"].iloc[0]), rtol=1e-5, atol=0):
            bad_top.append(t)
        ps, pe = strip_pts[t]
        c = cd[cd["target"] == t].sort_values("draw")
        if len(ps.get_xdata()) != len(c) or not np.allclose(np.asarray(pe.get_xdata(), dtype=float) * 1000.0, c["annual_E_kwh"].to_numpy(dtype=float), rtol=1e-9, atol=0):
            bad_pts.append(t)
    print("CHECK drawn_running_median_equals_district_spread_csv %s targets_with_mismatch=%s" % ("PASS" if not bad_run else "FAIL", bad_run), flush=True)
    print("CHECK drawn_running_interval_equals_district_spread_csv %s targets_with_mismatch=%s" % ("PASS" if not bad_band else "FAIL", bad_band), flush=True)
    print("CHECK drawn_distribution_median_equals_district_spread_csv_n%d %s targets_with_mismatch=%s" % (N, "PASS" if not bad_top else "FAIL", bad_top), flush=True)
    print("CHECK drawn_energyplus_check_totals_equal_district_check_draws_csv %s targets_with_mismatch=%s" % ("PASS" if not bad_pts else "FAIL", bad_pts), flush=True)
    # planted: one drawn median changed by 0.1 % must be caught by the same comparisons (counted per quantity, unplanted vs planted)
    t0 = TG[0][0]
    r0 = sp[(sp["scope"] == "all") & (sp["target"] == t0) & (sp["metric"] == "annual")].drop_duplicates("n_draws").sort_values("n_draws")
    want0 = r0["median_kwh"].to_numpy(dtype=float) / 1000.0
    got0 = np.asarray(med_run[t0].get_ydata(), dtype=float).copy()
    got0[3] *= 1.001
    fired_run = not np.allclose(got0, want0, rtol=1e-9, atol=0)
    rN0 = float(sp[(sp["scope"] == "all") & (sp["target"] == t0) & (sp["metric"] == "annual") & (sp["n_draws"] == N)]["median_kwh"].iloc[0])
    fired_top = not np.isclose(float(med_top[t0].get_xdata()[0]) * 1000.0 * 1.001, rN0, rtol=1e-5, atol=0)
    print("CHECK_PLANTED drawn_median_changed_by_0.1pct running=%s distribution=%s" % ("FIRED" if fired_run else "DID NOT FIRE", "FIRED" if fired_top else "DID NOT FIRE"), flush=True)
    inputs = [a.draws, a.spread, a.check]
    png, pdf = fc.save_figure(fig, "Figure_05_district_spread", a.out, inputs,
                              ["INFO N=%d draws, check draws %s, equipment omitted by design" % (N, chk_draws)])
    print("WROTE", png, pdf, flush=True)
    if bad_run or bad_band or bad_top or bad_pts or not (fired_run and fired_top):
        print("EXIT 1", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
