#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_codeschedule_vs_survey.py -- weekday load shape under code schedules vs survey-driven channels.

THIS IS A DATA FIGURE. Plotted from frozen data only; no value is altered.

Data: fig_codeschedule_vs_survey_profiles.csv and fig_codeschedule_vs_survey_metrics.csv in
this folder, written by
writing/implementation/IMP/scripts/p3_code_schedule_comparison.py from the frozen deliverable
(Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_diurnal.csv, season 'all',
daytype 'WD', metric 'energy_W'; agg_peak.csv column coincidence_factor). The whole-building
curve is the sum of the six attributed channels (the four tenant channels plus residential
common space and service/MEP), i.e. the same total the coincidence factor is computed on.

Panels (a)-(e): weekday mean hourly energy, normalised by its own daily mean, median across the
four building-city cells (line) with the four-cell range (band, survey 2022 only); the marker on
the top edge is the load-weighted circular mean hour (Step-9 definition), median across cells.
Panel (f): coincidence factor per building-city cell.

Run:  py -3 writing/figures/fig_codeschedule_vs_survey.py [--arm P10R|deliverable]
      --arm P10R (default since the P9 second pass, 2026-09-25) reads _P10R_figdata/ (written by
      p3_code_schedule_comparison.py --arm P10R); --arm deliverable reads the frozen-arm CSVs in this folder.
Output: writing/figures/fig_codeschedule_vs_survey.pdf / .png (600 dpi)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import SLATE, AMBER, GREY, INK, WHITE, save_both  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig_codeschedule_vs_survey")
ARM = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "P10R"
assert ARM in ("P10R", "deliverable"), ARM
_D = os.path.join(HERE, "_P10R_figdata") if ARM == "P10R" else HERE
PROF = os.path.join(_D, "fig_codeschedule_vs_survey_profiles.csv")
MET = os.path.join(_D, "fig_codeschedule_vs_survey_metrics.csv")

SCEN = [("Default_NECB", "Code schedules", GREY, (0, (4, 2))),
        ("Y2022", "Survey-driven, 2022", SLATE, "solid"),
        ("B_central", "Survey-driven, 2030 central", AMBER, "solid")]
PANELS = [("office", "(a) Office"), ("retail", "(b) Retail"), ("hotel", "(c) Hotel"),
          ("residential", "(d) Residential"), ("_BUILDING", "(e) Whole building")]
CELLS = [("SuperTall", "MTL", "SuperTall\nMontreal"), ("SuperTall", "CLG", "SuperTall\nCalgary"),
         ("Tall", "MTL", "Tall\nMontreal"), ("Tall", "CLG", "Tall\nCalgary")]


def circ(profile):
    w = np.asarray(profile, float)
    ang = 2 * np.pi * np.arange(24) / 24
    m = np.arctan2((w * np.sin(ang)).sum(), (w * np.cos(ang)).sum())
    return (m % (2 * np.pi)) / (2 * np.pi) * 24


def main():
    print(f"[arm] {ARM}: {PROF}")
    prof = pd.read_csv(PROF)
    met = pd.read_csv(MET)
    # integrity guard: 3 scenarios x 4 cells x 5 series x 24 h
    if len(prof) != 3 * 4 * 5 * 24:
        raise AssertionError(f"profile rows {len(prof)} != 1440 -- BLOCKED, not drawn")
    prof["norm"] = prof["wd_kW"] / prof.groupby(["scenario", "building", "city", "channel"])["wd_kW"].transform("mean")

    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK, "axes.labelcolor": INK,
                         "xtick.color": INK, "ytick.color": INK, "axes.linewidth": 0.7})
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.9), dpi=100)
    fig.patch.set_facecolor(WHITE)
    hours = np.arange(24)
    for ax, (ch, title) in zip(axes.flat[:5], PANELS):
        top = 0.0
        for sc, lab, col, ls in SCEN:
            p = prof[(prof.scenario == sc) & (prof.channel == ch)]
            piv = p.pivot_table(index="hour", columns=["building", "city"], values="norm")
            med = piv.median(axis=1).to_numpy()
            if sc == "Y2022":
                ax.fill_between(hours, piv.min(axis=1), piv.max(axis=1), color=col, alpha=0.15,
                                linewidth=0)
            ax.plot(hours, med, color=col, linestyle=ls, linewidth=1.3, label=lab)
            top = max(top, float(piv.max(axis=1).max()))
            h = np.median([circ(piv[c].to_numpy()) for c in piv.columns])
            ax.plot([h], [1.0], marker="v", color=col, markersize=5, transform=ax.get_xaxis_transform(),
                    clip_on=False, zorder=5)
        ax.set_title(title, loc="left", fontsize=8, color=INK, fontweight="bold")
        ax.set_xlim(0, 23)
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_ylim(0, top * 1.08)
        ax.grid(axis="y", color="#E6E1D8", linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("Hour of day (weekday)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Load / daily mean load")

    # (f) coincidence factor per cell
    ax = axes.flat[5]
    b = met[met.channel == "_BUILDING"]
    x = np.arange(len(CELLS))
    wbar = 0.26
    for k, (sc, lab, col, ls) in enumerate(SCEN):
        v = [float(b[(b.scenario == sc) & (b.building == bl) & (b.city == ci)]
                   ["coincidence_factor_published_6ch"].iloc[0]) for bl, ci, _ in CELLS]
        ax.bar(x + (k - 1) * wbar, v, width=wbar, color=col, edgecolor=WHITE, linewidth=0.4,
               hatch="////" if sc == "Default_NECB" else None, alpha=0.9 if sc != "Default_NECB" else 0.55)
    ax.set_xticks(x)
    ax.set_xticklabels([c[2] for c in CELLS], fontsize=5.6)
    ax.set_ylim(0.80, 1.0)
    ax.set_ylabel("Coincidence factor")
    ax.set_title("(f) Coincidence factor", loc="left", fontsize=8, color=INK, fontweight="bold")
    ax.grid(axis="y", color="#E6E1D8", linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=7.5,
               bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.2, w_pad=1.0)
    save_both(fig, OUT, dpi=600)


if __name__ == "__main__":
    main()
