"""
T94 -- re-plot manuscript Figures 2-8 with plain reader-facing labels (no task IDs, no scenario codes,
no internal status words). Plotting only: every plotted value is read from the already-accepted saved
output of the original figure task (T76, T71, T77, T73); nothing is recomputed except T77's
stock-weighted panels, which reuse T77's own functions (imported from a copy whose only change is the
input/output directory constants) on T77's own accepted input files.

Run locally:  py T94_scripts/t94_clean_figures.py   (from impl/)
Writes:       T94_out/*.png and T94_out/t94_plotted_values.json (every plotted number, for checking)
"""
import importlib.util
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.dirname(HERE)
IN = os.path.join(IMPL, "T94_in")
OUT = os.path.join(IMPL, "T94_out")
os.makedirs(OUT, exist_ok=True)
DPI = 600
FIG_WIDTH_IN = 7.0
VALUES = {}

METER_LABEL = {
    "elec_facility_kWh": "Whole building (total)",
    "lights_kWh": "Interior lighting",
    "equip_kWh": "Interior equipment",
    "fan_kWh": "Fans",
    "heating_ET_kWh": "Heating (energy transfer)",
    "cooling_ET_kWh": "Cooling (energy transfer)",
    "water_ET_kWh": "Water systems (energy transfer)",
    "hvac_dhw_elec_kWh": "HVAC and hot-water electricity\n(remainder)",
}
ANN_COL_ORDER = ["elec_facility_kWh", "lights_kWh", "equip_kWh", "fan_kWh",
                 "heating_ET_kWh", "cooling_ET_kWh", "water_ET_kWh", "hvac_dhw_elec_kWh"]
SCEN_LABEL = {"S-Full": "Main persistence", "S-None": "Full reversion",
              "S-Partial": "Partial persistence", "S-Revert-std": "Standardized reversion"}


def save(fig, name):
    p = os.path.join(OUT, name + ".png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight")
    # vector copy for the journal upload (Applied Energy prefers PDF/EPS for charts)
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print("saved", p)


# ---- Figure 2: at-home fraction by hour (plot code from T76, labels only changed) ----
def fig_athome():
    df = pd.read_csv(os.path.join(IN, "fig01_athome_by_hour.csv"))
    series = [
        ("2022_baseline", "2022", "-", "black"),
        ("2030_main_persist", "2030, main persistence (λ = 1)", "-", "tab:red"),
        ("2030_null", "2030, no-change control", "--", "tab:gray"),
        ("2030_lambda_0.5_partial", "2030, partial persistence (λ = 0.5)", "-.", "tab:orange"),
        ("2030_lambda_0.0_revert", "2030, full reversion (λ = 0)", ":", "tab:blue"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for ax, day_type in zip(axes, ["Weekday", "Weekend"]):
        for key, label, style, color in series:
            sub = df[(df["series"] == key) & (df["day_type"] == day_type)].set_index("hour")
            vals = [float(sub.loc[h, "athome_fraction"]) for h in range(24)]
            VALUES.setdefault("fig2", {})[f"{key}|{day_type}"] = vals
            ax.plot(range(24), vals, style, color=color, label=label, linewidth=1.6)
        ax.set_title(day_type)
        ax.set_xlabel("Hour of day (0-23)")
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlim(0, 23)
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Share of households at home (0-1)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    save(fig, "fig02_athome_by_hour")


# ---- Figure 3: annual energy by end use (plot code from T71 figure_02) ----
def fig_annual():
    df = pd.read_csv(os.path.join(IMPL, "T71_out", "fig02_annual_by_enduse.csv"))
    whole = {y: {} for y in (2022, 2030)}
    perd = {y: {} for y in (2022, 2030)}
    for _, r in df.iterrows():
        whole[int(r["year"])][r["ann_col"]] = float(r["stock_weighted_whole_building_kWh"])
        if r["ann_col"] in ("equip_kWh", "lights_kWh"):
            perd[int(r["year"])][r["ann_col"]] = float(r["stock_weighted_per_dwelling_kWh"])
    VALUES["fig3"] = {"whole": whole, "per_dwelling": perd}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_WIDTH_IN, 8.5))
    x = np.arange(len(ANN_COL_ORDER))
    w = 0.38
    ax1.bar(x - w / 2, [whole[2022][c] for c in ANN_COL_ORDER], width=w, label="2022", color="#4C72B0")
    ax1.bar(x + w / 2, [whole[2030][c] for c in ANN_COL_ORDER], width=w, label="2030", color="#DD8452")
    ax1.set_xticks(x)
    ax1.set_xticklabels([METER_LABEL[c] for c in ANN_COL_ORDER], rotation=30, ha="right")
    ax1.set_ylabel("Annual energy per simulated\nbuilding, stock-weighted (kWh/yr)")
    ax1.set_title("(a) Whole building, all end uses, main scenario")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    cols = ["equip_kWh", "lights_kWh"]
    xp = np.arange(len(cols))
    ax2.bar(xp - w / 2, [perd[2022][c] for c in cols], width=w, label="2022", color="#4C72B0")
    ax2.bar(xp + w / 2, [perd[2030][c] for c in cols], width=w, label="2030", color="#DD8452")
    ax2.set_xticks(xp)
    ax2.set_xticklabels([METER_LABEL[c] for c in cols])
    ax2.set_ylabel("Annual energy per dwelling,\nstock-weighted (kWh/yr)")
    ax2.set_title("(b) Per dwelling, equipment and lighting only")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "fig03_annual_by_enduse")


# ---- Figure 4: intraday load shape by scenario (plot code from T71 figure_03) ----
def fig_intraday():
    df = pd.read_csv(os.path.join(IMPL, "T71_out", "fig03_intraday_load_shape.csv"))
    colors = {"S-Full": "#4C72B0", "S-None": "#DD8452", "S-Partial": "#55A868", "S-Revert-std": "#C44E52"}
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 4.5))
    for scen in ["S-Full", "S-None", "S-Partial", "S-Revert-std"]:
        sub = df[df["scenario"] == scen].set_index("hour")
        ys = [float(sub.loc[h, "stock_weighted_load_kW"]) for h in range(24)]
        VALUES.setdefault("fig4", {})[scen] = ys
        ax.plot(range(24), ys, marker="o", markersize=3, label=SCEN_LABEL[scen], color=colors[scen])
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Stock-weighted whole-building load (kW)")
    ax.set_xticks(range(0, 24, 2))
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save(fig, "fig04_intraday_load_shape")


# ---- Figure 5: peak, ramp, load factor (plot code from T71 figure_04) ----
def fig_peak():
    df = pd.read_csv(os.path.join(IMPL, "T71_out", "fig04_peak_loadfactor_ramp_ci.csv")).set_index("metric")
    pk, rp, lf = df.loc["peak_kW_annual"], df.loc["evening_ramp_kW_mean"], df.loc["load_factor"]
    VALUES["fig5"] = df.to_dict(orient="index")
    fig, axes = plt.subplots(1, 3, figsize=(FIG_WIDTH_IN, 3.2))

    def bar_no_ci(ax, title, ylab, a, b):
        ax.bar([0, 1], [a, b], color=["#4C72B0", "#DD8452"])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["2022", "2030"])
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=9)

    bar_no_ci(axes[0], "Peak demand", "Stock-weighted\npeak (kW)", pk["value_2022"], pk["value_2030"])
    bar_no_ci(axes[1], "Evening ramp\n(14:00 to 17:00)", "Stock-weighted\nramp (kW)", rp["value_2022"], rp["value_2030"])
    ax = axes[2]
    lf22, lf30 = float(lf["value_2022"]), float(lf["value_2030"])
    d, lo, hi = float(lf["delta_or_point_change"]), float(lf["ci_low"]), float(lf["ci_high"])
    ax.bar([0, 1], [lf22, lf30], color=["#4C72B0", "#DD8452"])
    ax.errorbar([1], [lf30], yerr=[[d - lo], [hi - d]], fmt="none", ecolor="black", capsize=4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["2022", "2030"])
    ax.set_ylabel("Stock-weighted load factor (fraction)")
    ax.set_title("Load factor", fontsize=9)
    fig.tight_layout()
    save(fig, "fig05_peak_loadfactor_ramp")


# ---- Figure 6: end use x hour heatmap (plot code from T71 figure_05) ----
def fig_heatmap():
    df = pd.read_csv(os.path.join(IMPL, "T71_out", "fig05_enduse_hour_diff.csv"))
    old_label = {  # T71's own METER_LABEL values, as written in its CSV
        "elec_facility_kWh": "Electricity:Facility (total)", "lights_kWh": "Interior lights",
        "equip_kWh": "Interior equipment", "fan_kWh": "Fan electricity",
        "heating_ET_kWh": "Heating (EnergyTransfer)", "cooling_ET_kWh": "Cooling (EnergyTransfer)",
        "water_ET_kWh": "Water systems (EnergyTransfer)", "hvac_dhw_elec_kWh": "HVAC+DHW electricity (remainder)",
    }
    matrix = np.full((len(ANN_COL_ORDER), 24), np.nan)
    for i, c in enumerate(ANN_COL_ORDER):
        sub = df[df["end_use"] == old_label[c]].set_index("hour")
        assert len(sub) == 24, c
        for h in range(24):
            if sub.loc[h, "status"] == "POINT_ONLY_NO_CI":
                matrix[i, h] = float(sub.loc[h, "pct_change"])
    VALUES["fig6"] = matrix.tolist()
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 4.5))
    vmax = np.nanmax(np.abs(matrix))
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax.set_yticks(range(len(ANN_COL_ORDER)))
    ax.set_yticklabels([METER_LABEL[c].replace("\n", " ") for c in ANN_COL_ORDER], fontsize=8)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Hour of day")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Change in stock-weighted mean load,\n2022 to 2030 (%)")
    fig.tight_layout()
    save(fig, "fig06_enduse_hour_change")


# ---- Figure 7: full model vs average-profile arm (T77 functions, T77 inputs) ----
def fig_avgarm():
    src = open(os.path.join(IN, "t77_fig06_build.py"), encoding="utf-8").read()
    n_sub = 0
    for const, local in (("T68_DIR", os.path.join(IN, "T68")), ("T77_DIR", os.path.join(IN, "T77")),
                         ("LOG_DIR", os.path.join(OUT, "t77_logs_unused"))):
        src, k = re.subn(rf'^{const} = ".*"$', lambda _m, c=const, v=local: f"{c} = {v!r}", src, flags=re.M)
        n_sub += k
    assert n_sub == 3, n_sub
    lib_path = os.path.join(OUT, "_t77_lib_localdirs.py")
    open(lib_path, "w", encoding="utf-8").write(src)
    spec = importlib.util.spec_from_file_location("t77lib", lib_path)
    t77 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t77)

    full_ann, full_grid = t77.load_arm(os.path.join(IN, "T68", "enduse_annual.csv"), os.path.join(IN, "T68", "grid_metrics.csv"))
    avg_ann, avg_grid = t77.load_arm(os.path.join(IN, "T77", "enduse_annual.csv"), os.path.join(IN, "T77", "grid_metrics.csv"))
    assert len(full_ann) == len(full_grid) == len(avg_ann) == len(avg_grid) == 2400
    spread_df = pd.read_csv(os.path.join(IN, "household_peak_spread_both_arms.csv"))
    swp, swci = t77.stock_weighted_point, t77.stock_weighted_paired_ci

    years = (2022, 2030)
    x = np.arange(len(years))
    w = 0.35
    colors = {"full": "#4C72B0", "avg": "#55A868"}
    LBL_F, LBL_A = "Full household model", "Average-profile method"
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.5))
    vals = {}

    def bar_no_ci(ax, key, title, ylab, f, a):
        vals[key] = {"full": f, "avg": a}
        ax.bar(x - w / 2, f, width=w, label=LBL_F, color=colors["full"])
        ax.bar(x + w / 2, a, width=w, label=LBL_A, color=colors["avg"])
        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in years])
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=9)

    def bar_with_ci(ax, key, title, ylab, f, a, cis):
        vals[key] = {"full": f, "avg": a, "ci": cis}
        ax.bar(x - w / 2, f, width=w, label=LBL_F, color=colors["full"])
        ax.bar(x + w / 2, a, width=w, label=LBL_A, color=colors["avg"])
        for i, ci in enumerate(cis):
            if ci is None:
                continue
            point, lo, hi, n = ci
            ax.errorbar([x[i] + w / 2], [a[i]], yerr=[[max(point - lo, 0)], [max(hi - point, 0)]],
                        fmt="none", ecolor="black", capsize=4)
        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in years])
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=9)

    def by_year(dff, dfa, col):
        return ([swp(dff[dff["year"] == y], col) for y in years], [swp(dfa[dfa["year"] == y], col) for y in years])

    f, a = by_year(full_ann, avg_ann, "elec_facility_kWh")
    bar_no_ci(axes[0, 0], "annual", "Annual electricity", "Annual electricity per simulated\nbuilding, stock-weighted (kWh/yr)", f, a)
    f, a = by_year(full_grid, avg_grid, "peak_kW_annual")
    bar_no_ci(axes[0, 1], "peak", "Peak demand", "Stock-weighted\npeak (kW)", f, a)
    for pos, col, title, ylab in ((axes[0, 2], "load_factor", "Load factor", "Stock-weighted\nload factor (fraction)"),
                                  (axes[1, 0], "midday_share", "Midday share (09:00 to 17:00)", "Stock-weighted\nmidday share (fraction)")):
        f, a = by_year(full_grid, avg_grid, col)
        cis = [swci(full_grid[full_grid["year"] == y], avg_grid[avg_grid["year"] == y], col) for y in years]
        bar_with_ci(pos, col, title, ylab, f, a, cis)
    f, a = by_year(full_grid, avg_grid, "evening_ramp_kW_mean")
    bar_no_ci(axes[1, 1], "ramp", "Evening ramp\n(14:00 to 17:00)", "Stock-weighted\nramp (kW)", f, a)
    f = [swp(spread_df[(spread_df["arm"] == "full_model_T21") & (spread_df["year"] == y)], "circular_sd_hours") for y in years]
    a = [swp(spread_df[(spread_df["arm"] == "avg_profile_T30") & (spread_df["year"] == y)], "circular_sd_hours") for y in years]
    bar_no_ci(axes[1, 2], "spread", "Household-to-household spread\nof peak hour (circular SD)", "Stock-weighted\nspread (hours)", f, a)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig07_full_vs_average_profile")
    VALUES["fig7"] = vals


# ---- Figure 8: measured vs simulated, Toronto (plot code from T73, labels only changed) ----
def fig_measured():
    df = pd.read_csv(os.path.join(IMPL, "T73_out", "sim_vs_measured_toronto_2022_shape_rebuilt.csv"))
    sub = df[(df["calendar"] == "eplus") & (df["series"] == "facility") & (df["measured_scope"] == "Toronto")]
    periods = ["shoulder", "winter", "summer", "full_year"]
    daytypes = ["weekday", "weekend", "holiday"]
    combos = [(p, d) for p in periods for d in daytypes]
    pname = {"shoulder": "Shoulder", "winter": "Winter", "summer": "Summer", "full_year": "Full year"}
    labels = [f"{pname[p]}, {d}" for p, d in combos]
    metrics = [
        ("load_factor", "Load factor\n(mean / peak load, 0-1)", "Load factor", False),
        ("peak_to_avg", "Peak-to-average ratio", "Peak-to-average ratio", False),
        ("midday_share", "Share of daily energy,\n09:00 to 17:00 (0-1)", "Midday share", False),
        ("mean_peak_hour", "Mean hour of daily peak\n(hour ending, 1-24)", "Mean peak hour", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(FIG_WIDTH_IN * 1.2, 6.8))
    af = axes.flatten()
    x = np.arange(len(combos))
    w = 0.38
    vals = {}
    for i, (m, ylab, title, _) in enumerate(metrics):
        ms = sub[sub["metric"] == m]
        sims, meas = [], []
        for p, d in combos:
            r = ms[(ms["period"] == p) & (ms["daytype"] == d)]
            assert len(r) == 1, (m, p, d, len(r))
            sims.append(float(r.iloc[0]["sim"]))
            meas.append(float(r.iloc[0]["measured"]))
        vals[m] = {"sim": sims, "measured": meas}
        ax = af[i]
        ax.bar(x - w / 2, meas, width=w, label="Measured (IESO, Toronto)", color="#4C72B0")
        ax.bar(x + w / 2, sims, width=w, label="Simulated", color="#DD8452")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=6, rotation=60, ha="right")
        ax.set_ylabel(ylab, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    h, l = af[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    save(fig, "fig08_measured_vs_simulated")
    VALUES["fig8"] = vals


if __name__ == "__main__":
    fig_athome()
    fig_annual()
    fig_intraday()
    fig_peak()
    fig_heatmap()
    fig_avgarm()
    fig_measured()
    with open(os.path.join(OUT, "t94_plotted_values.json"), "w") as fh:
        json.dump(VALUES, fh, indent=1, default=str)
    print("done")
