"""New Figure 15 (1J revision): annual end-use deviation from Default, mean of 30 draws with 95 % interval.
Plotted from out/cells_all_enduses.csv (stage5_tables.py). No value is altered."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "..", "..", "figures")
os.makedirs(FIG, exist_ok=True)
c = pd.read_csv(os.path.join(HERE, "out", "cells_all_enduses.csv"), dtype={"year": str})

NUS = ["RC-R", "RC-D", "RC-T", "RC-MR2", "RC-MR3", "RC-HR2"]
YEARS = ["2005", "2010", "2015", "2022", "2025"]
COL = {"2005": "#1b9e77", "2010": "#d95f02", "2015": "#7570b3", "2022": "#e7298a", "2025": "#66a61e"}
PANELS = [("Heating", "(a) Heating"), ("Cooling", "(b) Cooling"),
          ("Electric Equipment", "(c) Electric equipment"), ("Water Systems", "(d) Domestic hot water")]

fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), sharex=True)
x = np.arange(len(NUS))
w = 0.16
for ax, (eu, title) in zip(axes.flat, PANELS):
    s = c[c.end_use == eu]
    for i, yr in enumerate(YEARS):
        r = s[s.year == yr].set_index("nu").loc[NUS]
        err = np.vstack([r.dev_pct - r.dev_lo, r.dev_hi - r.dev_pct])
        ax.bar(x + (i - 2) * w, r.dev_pct, w, color=COL[yr], label=yr, yerr=err, capsize=1.5,
               error_kw=dict(elinewidth=0.7, ecolor="black"))
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(2.5, color="grey", lw=0.6, ls=":")
    ax.set_title(title, fontsize=11, loc="left")
    ax.set_ylabel("Deviation from Default (%)")
    ax.grid(axis="y", lw=0.3, alpha=0.6)
for ax in axes[1]:
    ax.set_xticks(x)
    ax.set_xticklabels(NUS)
axes[0, 0].legend(ncol=5, fontsize=8, frameon=False, loc="upper right")
fig.tight_layout()
out = os.path.join(FIG, "Fig15_annual_deviation_R1.png")
fig.savefig(out, dpi=300)
print("saved", os.path.abspath(out))
