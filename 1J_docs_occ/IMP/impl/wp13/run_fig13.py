"""Runner for Figure 13 (plot_default_class_v2.py copy). The original script hard-codes panels (c)-(e) and two
annotation percentages from the OLD files; here they are computed from the rebuilt 2025 grid, then the
unchanged plotting code runs. Also writes fig13_summary.csv (every number shown in the figure).
Usage: python run_fig13.py [--grid <csv>] [--figs <dir>]"""
import argparse, os, sys
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--grid")
ap.add_argument("--figs")
a = ap.parse_args()
if a.figs:
    os.environ["WP13_FIGS"] = a.figs
    os.makedirs(a.figs, exist_ok=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot"))
import plot_default_class_v2 as m
if a.grid:
    m.GSS_2025_FILE = a.grid

d = m._defaults()
dvals = np.array(d["occupancy"]["Weekday"], float)
dmet = float(d["activity"])
df = pd.read_csv(m.GSS_2025_FILE, usecols=["Hour", "Day_Type", "Occupancy_Schedule", "Metabolic_Rate"])
prof = {}
met_wd = None
for dt in ["Weekday", "Weekend"]:
    s = df[df["Day_Type"] == dt]
    prof[dt] = s.groupby("Hour")["Occupancy_Schedule"].mean().reindex(range(24)).to_numpy(float)
    if dt == "Weekday":
        met_wd = s.groupby("Hour")["Metabolic_Rate"].mean().reindex(range(24)).to_numpy(float)
        met_pos = float(s.loc[s["Occupancy_Schedule"] > 0, "Metabolic_Rate"].mean())
gss_mean_wd, gss_mean_we = float(prof["Weekday"].mean()), float(prof["Weekend"].mean())
dflt_mean = float(dvals.mean())
day_default = 100 * float(dvals[9:17].mean())
day_gss = 100 * float(prof["Weekday"][9:17].mean())
night_over = 100 * (float(dvals[1:6].mean()) / float(prof["Weekday"][1:6].mean()) - 1)
mid_over = 100 * (dmet / float(met_wd[10:15].mean()) - 1)
gss_met_mean = float(met_wd.mean())
gss_met_peak = float(met_wd.max())

m.SUMMARY = {
    "occ_labels": ["Weekday\nOccupancy", "Weekend\nOccupancy"],
    "occ_default": [round(dflt_mean, 3), round(dflt_mean, 3)],
    "occ_gss": [round(gss_mean_wd, 3), round(gss_mean_we, 3)],
    "day_labels": ["Daytime\nOcc (09-17)"],
    "day_default": [round(day_default, 2)],
    "day_gss": [round(day_gss, 2)],
    "met_labels": ["Mean\nMet. Rate", "Peak\nMet. Rate"],
    "met_default": [dmet, dmet],
    "met_gss": [round(gss_met_mean, 1), round(gss_met_peak, 1)],
}
m.NIGHT_TXT = f"Night {'Overestimate' if night_over > 0 else 'Underestimate'}\n({night_over:+.0f}%)"
m.MID_TXT = f"Midday {'Overestimate' if mid_over > 0 else 'Underestimate'}\n({mid_over:+.0f}%)"

rows = [
    ("default_source", m.DEFAULT_SOURCE), ("default_occupied_hours", float(dvals.sum())),
    ("mean_occ_default", dflt_mean), ("mean_occ_gss_weekday", gss_mean_wd), ("mean_occ_gss_weekend", gss_mean_we),
    ("overest_weekday_pct", 100 * (dflt_mean - gss_mean_wd) / dflt_mean), ("overest_weekend_pct", 100 * (dflt_mean - gss_mean_we) / dflt_mean),
    ("daytime_pct_default", day_default), ("daytime_pct_gss_weekday", day_gss),
    ("night_h1_5_default_over_gss_pct", night_over), ("midday_h10_14_met_default_over_gss_pct", mid_over),
    ("met_mean_gss_weekday_hourly_all_rows", gss_met_mean), ("met_peak_gss_weekday_hourly", gss_met_peak),
    ("met_mean_gss_weekday_occ_pos_rows", met_pos), ("met_default_over_gss_mean_pct", 100 * (dmet - gss_met_mean) / dmet),
    ("met_sleep_h1_5_gss", float(met_wd[1:6].mean())), ("met_midday_h10_14_gss", float(met_wd[10:15].mean())),
]
outdir = os.environ.get("WP13_FIGS", ".")
pd.DataFrame(rows, columns=["quantity", "value"]).to_csv(os.path.join(outdir, "fig13_summary.csv"), index=False)
for k, v in rows:
    print("FIG13", k, v)
m.generate_plot()
print("FIG13 DONE")
