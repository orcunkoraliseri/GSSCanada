# -*- coding: utf-8 -*-
"""Figure 4 (peaks and timing). Columns = the three sealed test lists. Row 1: share of dwelling-days whose daily peak hour of total
electricity is within 1 h of EnergyPlus, per country x class cell, S vs C vs B1 (scores.parquet, G5J.5 rows). Rows 2 and 3: presence-heating
timing lag per country x class, EnergyPlus vs S median lag (h) and share of flats whose S lag is within 1 h of the EnergyPlus lag
(reported_S_<list>.txt, REPORTED thermal_mass_lag lines). No truth or prediction file is read. Speed job only.

Usage: fig04_peaks_timing.py --scores scores.parquet --reported-dir DIR --out DIR
Layout (decision of the employee): the left/right halves of the task text become rows, so that all three lists keep the same x axis.
"""
import argparse, io, re, sys, os
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_common as fc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PEAK_MODELS = ["S", "C", "B1"]
OFF = {"S": -0.26, "C": 0.0, "B1": 0.26}
LAG_RE = re.compile(r"^REPORTED thermal_mass_lag country=(\S+) class=(\S+) flats=(\d+) .*median_lag_ep_h=(\S+) median_lag_s_h=(\S+) share_within_1h=(\S+)$")


def num(s):
    try:
        return float(s)
    except ValueError:
        return float("nan")


def read_lags(path):
    out = {}
    for ln in io.open(path, encoding="utf-8"):
        m = LAG_RE.match(ln.rstrip("\n"))
        if m:
            c, k, n, e, s, w = m.groups()
            out[(c, k)] = (int(n), num(e), num(s), 100.0 * num(w))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--reported-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sc = pd.read_parquet(a.scores)
    g5 = sc[(sc["gate"] == "G5J.5") & (sc["model"].isin(PEAK_MODELS))]
    peak = {(r["model"], r["list"], r["country"], r["class"]): r["share_days_peak_within_1h"] for _, r in g5.iterrows()}
    n_exp = len(PEAK_MODELS) * len(fc.LISTS) * len(fc.CELLS)
    print("CHECK peak_rows_found %s found=%d expected=%d" % ("PASS" if len(peak) == n_exp else "FAIL", len(peak), n_exp), flush=True)
    lag, inputs = {}, [a.scores]
    for L in fc.LISTS:
        p = os.path.join(a.reported_dir, "reported_S_%s.txt" % L)
        lag[L] = read_lags(p)
        inputs.append(p)
        print("CHECK lag_lines_found %s %s cells=%d expected=8" % ("PASS" if len(lag[L]) == 8 else "FAIL", L, len(lag[L])), flush=True)

    fig, axs = plt.subplots(3, 3, figsize=(fc.W2, 168 * fc.MM))
    fig.subplots_adjust(left=0.105, right=0.992, top=0.925, bottom=0.115, hspace=0.12, wspace=0.07)
    drawn = []
    lag_vals = [v for L in fc.LISTS for v in (lag[L][c_k][1] for c_k in fc.CELLS if c_k in lag[L])] + \
               [v for L in fc.LISTS for v in (lag[L][c_k][2] for c_k in fc.CELLS if c_k in lag[L])]
    lag_vals = [v for v in lag_vals if np.isfinite(v)]
    lag_lo, lag_hi = np.floor(min(lag_vals)) - 1, np.ceil(max(lag_vals)) + 1
    for li, L in enumerate(fc.LISTS):
        # row 1: peaks
        ax = axs[0, li]
        for m in PEAK_MODELS:
            ys = np.array([peak.get((m, L, c, k), np.nan) for c, k in fc.CELLS], dtype=float)
            xs = np.array(fc.CELL_X) + OFF[m]
            ok = np.isfinite(ys)
            ln, = ax.plot(xs[ok], ys[ok], ls="none", marker=fc.MODEL_MARKER[m], ms=3.2, mfc=fc.MODEL_COLOUR[m], mec="white", mew=0.3, zorder=3)
            drawn.append((m, L, ln))
        ax.set_ylim(0, 100)
        fc.cell_axis(ax, bottom=False)
        ax.set_title(fc.LIST_NAME[L], fontsize=8, pad=4)
        # row 2: lag, EnergyPlus vs S
        ax = axs[1, li]
        xs = np.array(fc.CELL_X)
        e = np.array([lag[L].get(ck, (0, np.nan, np.nan, np.nan))[1] for ck in fc.CELLS], dtype=float)
        s = np.array([lag[L].get(ck, (0, np.nan, np.nan, np.nan))[2] for ck in fc.CELLS], dtype=float)
        ok = np.isfinite(e)
        ax.plot(xs[ok] - 0.15, e[ok], ls="none", marker="o", ms=4.2, mfc="white", mec="#111111", mew=0.7, zorder=3)
        ok = np.isfinite(s)
        ax.plot(xs[ok] + 0.15, s[ok], ls="none", marker="o", ms=3.0, mfc=fc.MODEL_COLOUR["S"], mec="white", mew=0.3, zorder=4)
        ax.set_ylim(lag_lo, lag_hi)
        fc.cell_axis(ax, bottom=False)
        # row 3: share of flats within 1 h
        ax = axs[2, li]
        w = np.array([lag[L].get(ck, (0, np.nan, np.nan, np.nan))[3] for ck in fc.CELLS], dtype=float)
        ok = np.isfinite(w)
        ax.plot(xs[ok], w[ok], ls="none", marker="o", ms=3.2, mfc=fc.MODEL_COLOUR["S"], mec="white", mew=0.3, zorder=3)
        ax.set_ylim(0, 100)
        fc.cell_axis(ax, bottom=True)
        if li > 0:
            for r in range(3):
                axs[r, li].tick_params(axis="y", labelleft=False)
    axs[0, 0].set_ylabel("Peak hour within 1 h\n(% of dwelling-days)")
    axs[1, 0].set_ylabel("Median lag (h)")
    axs[2, 0].set_ylabel("Flats within 1 h\nof EnergyPlus (%)")
    handles = [Line2D([], [], ls="none", marker=fc.MODEL_MARKER[m], ms=4, mfc=fc.MODEL_COLOUR[m], mec="white", mew=0.3, label=m) for m in PEAK_MODELS]
    handles.append(Line2D([], [], ls="none", marker="o", ms=4.2, mfc="white", mec="#111111", mew=0.7, label="EnergyPlus lag"))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.55, 0.998), handletextpad=0.4, columnspacing=1.6)
    # checks: peak shares drawn = scores.parquet rows (read back from the figure, compared with a pandas filter)
    bad, nchk = [], 0
    for m, L, ln in drawn:
        sub = g5[(g5["model"] == m) & (g5["list"] == L)].set_index(["country", "class"])["share_days_peak_within_1h"]
        want = np.array([sub.loc[(c, k)] for c, k in fc.CELLS], dtype=float)
        want = want[np.isfinite(want)]
        got = np.asarray(ln.get_ydata(), dtype=float)
        nchk += 1
        if len(got) != len(want) or not np.allclose(got, want, rtol=0, atol=0):
            bad.append((m, L))
    print("CHECK drawn_peak_shares_equal_scores_parquet %s series=%d mismatches=%d %s" % ("PASS" if not bad else "FAIL", nchk, len(bad), bad[:3]), flush=True)
    m0, L0, ln0 = drawn[0]
    sub0 = g5[(g5["model"] == m0) & (g5["list"] == L0)].set_index(["country", "class"])["share_days_peak_within_1h"]
    want0 = np.array([sub0.loc[(c, k)] for c, k in fc.CELLS], dtype=float)
    got0 = np.asarray(ln0.get_ydata(), dtype=float).copy()
    got0[0] += 0.5
    print("CHECK_PLANTED drawn_peak_share_changed_by_0.5 %s" % ("FAIL (expected: the comparison fires)" if not np.allclose(got0, want0[np.isfinite(want0)], rtol=0, atol=0) else "PASS (UNEXPECTED: cannot fire)"), flush=True)
    extra = ["INFO lag cells read per list: %s" % {L: len(lag[L]) for L in fc.LISTS},
             "INFO a share of dwelling-days outside the figure: none (axis 0 to 100)"]
    png, pdf = fc.save_figure(fig, "Figure_04_peaks_timing", a.out, inputs, extra)
    print("WROTE", png, pdf, flush=True)


if __name__ == "__main__":
    main()
