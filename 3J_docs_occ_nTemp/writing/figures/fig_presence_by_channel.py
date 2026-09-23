#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_presence_by_channel.py -- weekday occupant presence per channel, by survey cycle.

THIS IS A DATA FIGURE. Plotted from frozen data only; no value is altered.

Data: fig_presence_by_channel_data.csv in this folder, written by
writing/implementation/IMP/scripts/p3_code_schedule_comparison.py from the frozen deliverable
(Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_diurnal.csv, season 'all',
metric 'people', the simulated occupant count per channel; divided by the channel's parsed
conditioned floor area in agg_meta.csv, area_<channel>_m2).

One panel per channel; one line per scenario = median across the four building-city cells of
weekday people per 100 m2. Hotel carries no survey-driven product in 2005, 2010 and 2015 (its
schedule there is the code schedule), so only 2022 and 2030 central are drawn for hotel.

Run:  py -3 writing/figures/fig_presence_by_channel.py
Output: writing/figures/fig_presence_by_channel.pdf / .png (600 dpi)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import SLATE, AMBER, TEAL, GREY, INK, WHITE, save_both  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig_presence_by_channel")
DATA = os.path.join(HERE, "fig_presence_by_channel_data.csv")

SCEN = [("Default_NECB", "Code schedules", GREY, (0, (4, 2)), 1.2),
        ("Y2005", "2005", "#A9BFCB", "solid", 1.0),
        ("Y2010", "2010", "#7F9FB1", "solid", 1.0),
        ("Y2015", "2015", TEAL, "solid", 1.0),
        ("Y2022", "2022", SLATE, "solid", 1.4),
        ("B_central", "2030 central", AMBER, "solid", 1.4)]
PANELS = [("office", "(a) Office"), ("retail", "(b) Retail"), ("hotel", "(c) Hotel"),
          ("residential", "(d) Residential")]


def main():
    d = pd.read_csv(DATA)
    d = d[d.daytype == "WD"]
    if len(d) != 6 * 4 * 4 * 24:
        raise AssertionError(f"weekday rows {len(d)} != 2304 -- BLOCKED, not drawn")
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK, "axes.labelcolor": INK,
                         "xtick.color": INK, "ytick.color": INK, "axes.linewidth": 0.7})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), dpi=100)
    fig.patch.set_facecolor(WHITE)
    hours = np.arange(24)
    for ax, (ch, title) in zip(axes.flat, PANELS):
        for sc, lab, col, ls, lw in SCEN:
            p = d[(d.scenario == sc) & (d.channel == ch)]
            if ch == "hotel" and sc in ("Y2005", "Y2010", "Y2015"):
                continue
            if sc != "Default_NECB" and not p["channel_injected"].all():
                continue
            med = p.pivot_table(index="hour", columns=["building", "city"],
                                values="people_per_100m2").median(axis=1).to_numpy()
            ax.plot(hours, med, color=col, linestyle=ls, linewidth=lw, label=lab)
        ax.set_title(title, loc="left", fontsize=8, color=INK, fontweight="bold")
        ax.set_xlim(0, 23)
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", color="#E6E1D8", linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("Hour of day (weekday)")
        ax.set_ylabel("Occupants per 100 m$^2$")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, frameon=False, fontsize=7.5,
               bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.2, w_pad=1.2)
    save_both(fig, OUT, dpi=600)


if __name__ == "__main__":
    main()
