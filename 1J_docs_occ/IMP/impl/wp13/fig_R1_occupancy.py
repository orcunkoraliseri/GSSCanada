"""R1 figures from WP13 outputs (no value altered): metabolic profiles by cycle; Default vs 2025 schedules."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FIG = os.path.normpath(os.path.join(HERE, "..", "..", "..", "figures"))
DEF = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.85, 0.39, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.30, 0.52, 0.87, 0.87, 0.87, 1.0, 1.0, 1.0]
assert abs(sum(DEF) - 16.42) < 1e-9
COL = {"2005": "#1b9e77", "2010": "#d95f02", "2015": "#7570b3", "2022": "#e7298a", "2025": "#66a61e"}
met = pd.read_csv(os.path.join(OUT, "figs", "metabolic_hourly_by_year.csv"))
fig, ax = plt.subplots(figsize=(7, 4))
for y in ["2005", "2010", "2015", "2022", "2025"]:
    ax.plot(met.hour, met[y], color=COL[y], lw=1.8, label=y)
ax.axhline(95, color="black", ls="--", lw=1.2, label="Default (95 W)")
ax.set_xlabel("Hour of day"); ax.set_ylabel("Metabolic rate per person at home (W)")
ax.set_xticks(range(0, 25, 3)); ax.set_xlim(0, 23); ax.grid(lw=0.3, alpha=0.6); ax.legend(ncol=3, fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "Fig8_metabolic_R1.png"), dpi=300); plt.close(fig)

pr = pd.read_csv(os.path.join(OUT, "profiles_by_year_region.csv"), dtype={"year": str})
pr = pr[(pr.region == "Canada")]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, dt in zip(axes, ["Weekday", "Weekend"]):
    ax.step(range(24), DEF, where="post", color="black", ls="--", lw=1.3, label="Default")
    for y in ["2005", "2010", "2015", "2022", "2025"]:
        s = pr[(pr.year == y) & (pr.day_type == dt)].sort_values("hour")
        ax.plot(s.hour, s.mean_occupancy, color=COL[y], lw=1.6, label=y)
    ax.set_title(f"({'a' if dt == 'Weekday' else 'b'}) {dt}", loc="left", fontsize=11)
    ax.set_xlabel("Hour of day"); ax.set_xticks(range(0, 25, 3)); ax.set_xlim(0, 23); ax.set_ylim(0, 1.05); ax.grid(lw=0.3, alpha=0.6)
axes[0].set_ylabel("Occupancy fraction"); axes[1].legend(ncol=2, fontsize=8, frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "Fig9_default_vs_cycles_R1.png"), dpi=300); plt.close(fig)
print("ok")
