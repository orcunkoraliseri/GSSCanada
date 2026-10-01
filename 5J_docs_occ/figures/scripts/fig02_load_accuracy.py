# -*- coding: utf-8 -*-
"""Figure 2 (load accuracy): median hourly CV(RMSE) and median |NMBE| per target and class-country cell for S, B1, B0 and C on the
three sealed test lists, against the ASHRAE Guideline 14 hourly bands (30 % and 10 %). Data = scores.parquet (G5J.2 rows) only; no truth
or prediction file is read. Speed job only.

Usage: fig02_load_accuracy.py --scores scores.parquet --out DIR
Layout (decision of the employee): columns = the three test lists; for each target (block of rows) the upper row is CV(RMSE) and the lower
row is |NMBE|, because the two quantities have different bands; log y axis (values span two orders of magnitude).
"""
import argparse, sys, os
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_common as fc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

MODELS = ["S", "B1", "B0", "C"]
OFF = {"S": -0.30, "B1": -0.10, "B0": 0.10, "C": 0.30}
METRICS = [("median_cvrmse", "CV(RMSE) (%)", 30.0), ("median_abs_nmbe", "|NMBE| (%)", 10.0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sc = pd.read_parquet(a.scores)
    g = sc[(sc["gate"] == "G5J.2") & (sc["model"].isin(MODELS))].copy()
    # value lookup by a loop over rows (independent of the plotting arrays below)
    look = {(r["model"], r["list"], r["country"], r["class"], r["target"]): (r["median_cvrmse"], r["median_abs_nmbe"]) for _, r in g.iterrows()}
    n_expected = len(MODELS) * len(fc.LISTS) * len(fc.TARGETS) * len(fc.CELLS)
    print("CHECK rows_found %s found=%d expected=%d" % ("PASS" if len(look) == n_expected else "FAIL", len(look), n_expected), flush=True)
    nan_cells = [k for k, v in look.items() if not (np.isfinite(v[0]) and np.isfinite(v[1]))]
    print("INFO cells_not_finite=%d %s" % (len(nan_cells), nan_cells[:4]), flush=True)
    nonpos = [k for k, v in look.items() if (np.isfinite(v[1]) and v[1] <= 0) or (np.isfinite(v[0]) and v[0] <= 0)]
    print("INFO cells_with_zero_median=%d (not drawable on a log axis) %s" % (len(nonpos), nonpos[:4]), flush=True)

    nT = len(fc.TARGETS)
    ratios = []
    for i in range(nT):
        ratios += [1, 1] + ([0.38] if i < nT - 1 else [])
    fig = plt.figure(figsize=(fc.W2, 228 * fc.MM))
    gs = fig.add_gridspec(len(ratios), 3, height_ratios=ratios, left=0.125, right=0.995, top=0.945, bottom=0.095, hspace=0.12, wspace=0.07)
    # y limits per (target, metric) row, shared over the three lists
    axes = {}
    plotted = {}
    drawn = {}
    for ti, t in enumerate(fc.TARGETS):
        for mi, (mkey, mlabel, band) in enumerate(METRICS):
            row = ti * 3 + mi
            vals = [look[(m, L, c, k, t)][mi] for m in MODELS for L in fc.LISTS for c, k in fc.CELLS]
            vals = np.array([v for v in vals if np.isfinite(v) and v > 0] + [band])
            lo, hi = vals.min() / 1.6, vals.max() * 1.6
            for li, L in enumerate(fc.LISTS):
                ax = fig.add_subplot(gs[row, li])
                axes[(ti, mi, li)] = ax
                for m in MODELS:
                    ys = np.array([look[(m, L, c, k, t)][mi] for c, k in fc.CELLS], dtype=float)
                    xs = np.array(fc.CELL_X) + OFF[m]
                    ok = np.isfinite(ys) & (ys > 0)
                    ln, = ax.plot(xs[ok], ys[ok], ls="none", marker=fc.MODEL_MARKER[m], ms=3.0, mfc=fc.MODEL_COLOUR[m], mec="white", mew=0.3,
                                  zorder=3)
                    plotted[(t, mkey, L, m)] = int(ok.sum())
                    drawn[(t, mkey, L, m)] = ln
                ax.axhline(band, color=fc.BAND, lw=0.7, ls=(0, (4, 2)), zorder=2)
                ax.set_yscale("log")
                ax.set_ylim(lo, hi)
                fc.cell_axis(ax, bottom=(ti == nT - 1 and mi == 1))
                if li == 0:
                    ax.set_ylabel(mlabel)
                else:
                    ax.tick_params(axis="y", labelleft=False)
                    ax.tick_params(axis="y", which="minor", labelleft=False)
                if ti == 0 and mi == 0:
                    ax.set_title(fc.LIST_NAME[L], fontsize=8, pad=4)
    fig.canvas.draw()
    for ti, t in enumerate(fc.TARGETS):
        p1 = axes[(ti, 0, 0)].get_position()
        p2 = axes[(ti, 1, 0)].get_position()
        fig.text(0.012, (p1.y1 + p2.y0) / 2, fc.TARGET_NAME[t], rotation=90, ha="left", va="center", fontsize=8, fontweight="bold")
    handles = [Line2D([], [], ls="none", marker=fc.MODEL_MARKER[m], ms=4, mfc=fc.MODEL_COLOUR[m], mec="white", mew=0.3, label=lab)
               for m, lab in (("S", "S"), ("B1", "B1"), ("B0", "B0"), ("C", "C"))]
    handles.append(Line2D([], [], color=fc.BAND, lw=0.7, ls=(0, (4, 2)), label="ASHRAE band"))
    fig.legend(handles=handles, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.56, 0.998), handletextpad=0.4, columnspacing=1.6)
    # check: every panel shows 8 points per model unless a cell is not finite
    short = {k: v for k, v in plotted.items() if v != 8}
    print("CHECK points_per_panel_model %s panels_with_fewer_than_8=%d %s" % ("PASS" if not short else "REVIEW", len(short), list(short.items())[:4]), flush=True)
    # check: the numbers on the drawn markers (read back from the figure) equal the scored rows (a pandas filter, not the lookup used to draw)
    bad, nchk = [], 0
    for (t, mkey, L, m), ln in drawn.items():
        sub = g[(g["model"] == m) & (g["list"] == L) & (g["target"] == t)]
        sub = sub.set_index(["country", "class"])
        want = np.array([sub.loc[(c, k), mkey] for c, k in fc.CELLS], dtype=float)
        want = want[np.isfinite(want) & (want > 0)]
        got = np.asarray(ln.get_ydata(), dtype=float)
        nchk += 1
        if len(got) != len(want) or not np.allclose(got, want, rtol=0, atol=0):
            bad.append((t, mkey, L, m))
    print("CHECK drawn_values_equal_scores_parquet %s series=%d mismatches=%d %s" % ("PASS" if not bad else "FAIL", nchk, len(bad), bad[:3]), flush=True)
    # planted fault: one drawn value changed by 1 % must be caught by the same comparison
    k0 = sorted(drawn)[0]
    sub0 = g[(g["model"] == k0[3]) & (g["list"] == k0[2]) & (g["target"] == k0[0])].set_index(["country", "class"])
    want0 = np.array([sub0.loc[(c, k), k0[1]] for c, k in fc.CELLS], dtype=float)
    want0 = want0[np.isfinite(want0) & (want0 > 0)]
    got0 = np.asarray(drawn[k0].get_ydata(), dtype=float).copy()
    got0[0] *= 1.01
    print("CHECK_PLANTED drawn_value_changed_by_1pct %s" % ("FAIL (expected: the comparison fires)" if not np.allclose(got0, want0, rtol=0, atol=0) else "PASS (UNEXPECTED: cannot fire)"), flush=True)
    inputs = [a.scores]
    png, pdf = fc.save_figure(fig, "Figure_02_load_accuracy", a.out, inputs,
                              ["INFO markers drawn=%d of %d possible (a log axis needs a positive finite median)" % (sum(plotted.values()), 2 * n_expected)])
    print("WROTE", png, pdf, flush=True)


if __name__ == "__main__":
    main()
