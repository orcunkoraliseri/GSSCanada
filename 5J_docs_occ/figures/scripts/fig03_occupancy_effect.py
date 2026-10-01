# -*- coding: utf-8 -*-
"""Figure 3 (occupancy effect): per pair, the annual difference of the surrogate S (left) and of the blind control C (right) against the
EnergyPlus annual difference, for heating (top) and cooling (bottom), the three test lists pooled in one panel and coloured by list, with
the 1:1 line. Data = figures/data/fig3_pairs.parquet (written by fig03_data.py). No other file is read. Speed job only.

Usage: fig03_occupancy_effect.py --pairs fig3_pairs.parquet --out DIR
Axis limits: symmetric, from the 99.9th percentile of |EnergyPlus difference| and |S difference| of the target (same limits on both axes of
all panels of a row, so the 1:1 line is the diagonal). Pairs outside the limits are counted in the sidecar, none is altered.
"""
import argparse, sys, os
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_common as fc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

ORDER = ["test_new_buildings", "test_new_households", "test_both_new"]       # the large list first, so the small ones stay visible
ROWS = [("heating", "Heating"), ("cooling", "Cooling")]
COLS = [("dS", "S", "Surrogate S"), ("dC", "C", "Blind control C")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    df = pd.read_parquet(a.pairs)
    fig, axs = plt.subplots(2, 2, figsize=(fc.W2, 176 * fc.MM))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.915, bottom=0.095, hspace=0.30, wspace=0.26)
    outside = {}
    counts = {}
    for ri, (t, tl) in enumerate(ROWS):
        d = df[df["target"] == t]
        lim = float(np.percentile(np.concatenate([np.abs(d["dEP"].to_numpy()), np.abs(d["dS"].to_numpy())]), 99.9)) * 1.05
        for ci, (col, mk, title) in enumerate(COLS):
            ax = axs[ri, ci]
            for L in ORDER:
                x = d[d["list"] == L]
                sca = ax.scatter(x["dEP"], x[col], s=2.2, color=fc.LIST_COLOUR[L], alpha=0.45, linewidths=0, rasterized=True, zorder=3)
                counts[(t, mk, L)] = len(sca.get_offsets())        # read back from the drawn collection
            ax.plot([-lim, lim], [-lim, lim], color=fc.BAND, lw=0.7, zorder=4)
            ax.axhline(0, color=fc.GRID, lw=0.5, zorder=1)
            ax.axvline(0, color=fc.GRID, lw=0.5, zorder=1)
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.set_aspect("equal", adjustable="box")
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.yaxis.set_major_locator(MaxNLocator(5))
            out = int(((d["dEP"].abs() > lim) | (d[col].abs() > lim)).sum())
            outside[(t, mk)] = out
            if ri == 0:
                ax.set_title(title, fontsize=8, pad=5)
            if ri == 1:
                ax.set_xlabel("EnergyPlus annual difference (kWh)")
            ax.set_ylabel("%s\n%s annual difference (kWh)" % (tl, "surrogate" if ci == 0 else "control"))
    handles = [Line2D([], [], ls="none", marker="o", ms=4, mfc=fc.LIST_COLOUR[L], mec="none", label=fc.LIST_NAME[L]) for L in fc.LISTS]
    handles.append(Line2D([], [], color=fc.BAND, lw=0.7, label="1:1"))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.55, 0.995), handletextpad=0.4, columnspacing=1.6)
    pairs_per_list = {L: int((df[(df["target"] == "heating") & (df["list"] == L)]).shape[0]) for L in fc.LISTS}
    extra = ["INFO pairs per list (heating rows): %s" % pairs_per_list,
             "INFO pairs outside the drawn axis range (not altered, only not visible): %s" % {"%s_%s" % k: v for k, v in outside.items()}]
    for ln in extra:
        print(ln, flush=True)
    # check: each panel draws as many points as the table has rows for that target and list
    bad = [(k, v) for k, v in counts.items() if v != int(((df["target"] == k[0]) & (df["list"] == k[2])).sum())]
    print("CHECK points_per_panel_equal_table_rows %s mismatches=%d" % ("PASS" if not bad else "FAIL", len(bad)), flush=True)
    png, pdf = fc.save_figure(fig, "Figure_03_occupancy_effect", a.out, [a.pairs], extra)
    print("WROTE", png, pdf, flush=True)


if __name__ == "__main__":
    main()
