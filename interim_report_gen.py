import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import sys

# ── Run section 4.3 plotting scripts ──
script_dir = os.path.dirname(os.path.abspath(__file__))
plotting_dir = os.path.join(script_dir, "eSim_occ_utils", "plotting")
if plotting_dir not in sys.path:
    sys.path.insert(0, plotting_dir)

import importlib.util
for mod_name in ["plot_figure_4.3.1", "plot_figure_4.3.2", "plot_figure_4.3.3", "plot_figure_4.3.4"]:
    try:
        fpath = os.path.join(plotting_dir, f"{mod_name}.py")
        spec = importlib.util.spec_from_file_location(mod_name, fpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
        print(f"{mod_name} done")
    except Exception as e:
        print(f"WARNING: {mod_name} failed — {e}")

BASE = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults\BatchAll_MC_N3_1776120359"
OUT  = os.path.join(BASE, "interim_report")
os.makedirs(OUT, exist_ok=True)

nhoods = ["NUS_RC1", "NUS_RC2", "NUS_RC3", "NUS_RC4", "NUS_RC5", "NUS_RC6"]
data = {}
for n in nhoods:
    p = os.path.join(BASE, n, "aggregated_eui.csv")
    if os.path.exists(p):
        data[n] = pd.read_csv(p, index_col="EndUse")

N = len(data)
scenarios = ["2005", "2010", "2015", "2022", "2025", "Default"]
colors = {"2005":"#d62728","2010":"#ff7f0e","2015":"#bcbd22","2022":"#2ca02c","2025":"#1f77b4","Default":"#7f7f7f"}
end_uses = ["Heating","Cooling","Interior Lighting","Electric Equipment","Water Systems"]
eu_colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd"]

# ── Figure 1: Total EUI by scenario per neighbourhood ──
fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharey=False)
axes = axes.flatten()
for ax, (n, df) in zip(axes, data.items()):
    totals = {}
    stds = {}
    for sc in scenarios:
        mc = f"{sc}_mean"
        sc2 = f"{sc}_std"
        totals[sc] = df[mc].sum() if mc in df.columns else 0
        stds[sc]   = float(np.sqrt((df[sc2]**2).sum())) if sc2 in df.columns else 0
    xs = np.arange(len(scenarios))
    bars = ax.bar(xs, [totals[s] for s in scenarios], 0.6,
                  color=[colors[s] for s in scenarios],
                  yerr=[stds[s] for s in scenarios], capsize=4, ecolor='black', alpha=0.85)
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels(scenarios, rotation=30, ha='right')
    ax.set_ylabel("Total EUI (kWh/m\u00b2/yr)")
    ax.set_xlabel("Code Scenario")
    for bar, sc in zip(bars, scenarios):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                f"{totals[sc]:.1f}", ha='center', va='bottom', fontsize=7)
fig.suptitle("Total EUI by Code Scenario — All 6 Neighbourhoods (Montreal, N=3)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig1_total_eui_by_scenario.png"), dpi=150)
plt.close()
print("fig1 done")

# ── Figure 2: Stacked end-use ──
fig, axes = plt.subplots(2, 3, figsize=(20, 10), sharey=False)
axes = axes.flatten()
for ax, (n, df) in zip(axes, data.items()):
    xs = np.arange(len(scenarios))
    bottoms = np.zeros(len(scenarios))
    for eu, col in zip(end_uses, eu_colors):
        vals = []
        for sc in scenarios:
            mc = f"{sc}_mean"
            vals.append(df.loc[eu, mc] if (mc in df.columns and eu in df.index) else 0)
        ax.bar(xs, vals, 0.6, bottom=bottoms, color=col, label=eu, alpha=0.85)
        bottoms += np.array(vals)
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels(scenarios, rotation=30, ha='right')
    ax.set_ylabel("EUI (kWh/m\u00b2/yr)")
    ax.set_xlabel("Code Scenario")
    ax.legend(loc='upper right', fontsize=7)
fig.suptitle("Stacked End-Use EUI by Code Scenario — All 6 Neighbourhoods (Montreal, N=3)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig2_stacked_enduse.png"), dpi=150)
plt.close()
print("fig2 done")

# ── Figure 3: Heating vs Cooling ──
fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharey=False)
axes = axes.flatten()
for ax, (n, df) in zip(axes, data.items()):
    xs = np.arange(len(scenarios))
    w = 0.35
    h_vals = [df.loc["Heating", f"{sc}_mean"] if f"{sc}_mean" in df.columns else 0 for sc in scenarios]
    c_vals = [df.loc["Cooling", f"{sc}_mean"] if f"{sc}_mean" in df.columns else 0 for sc in scenarios]
    h_err  = [df.loc["Heating", f"{sc}_std"]  if f"{sc}_std"  in df.columns else 0 for sc in scenarios]
    c_err  = [df.loc["Cooling", f"{sc}_std"]  if f"{sc}_std"  in df.columns else 0 for sc in scenarios]
    ax.bar(xs - w/2, h_vals, w, yerr=h_err, capsize=3, color='#1f77b4', label='Heating', alpha=0.85)
    ax.bar(xs + w/2, c_vals, w, yerr=c_err, capsize=3, color='#ff7f0e', label='Cooling',  alpha=0.85)
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels(scenarios, rotation=30, ha='right')
    ax.set_ylabel("EUI (kWh/m\u00b2/yr)")
    ax.set_xlabel("Code Scenario")
    ax.legend(fontsize=8)
fig.suptitle("Heating vs Cooling EUI — All 6 Neighbourhoods (Montreal, N=3)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig3_heating_cooling.png"), dpi=150)
plt.close()
print("fig3 done")

# ── Figure 4: % improvement vs 2005 ──
fig, axes = plt.subplots(2, 3, figsize=(18, 10), sharey=False)
axes = axes.flatten()
compare_scen = ["2010","2015","2022","2025","Default"]
for ax, (n, df) in zip(axes, data.items()):
    base = df["2005_mean"].sum()
    impr = []
    for sc in compare_scen:
        mc = f"{sc}_mean"
        tot = df[mc].sum() if mc in df.columns else base
        impr.append((base - tot)/base*100)
    bar_colors = ['#2ca02c' if v >= 0 else '#d62728' for v in impr]
    xs = np.arange(len(compare_scen))
    ax.bar(xs, impr, 0.6, color=bar_colors, alpha=0.75)
    ax.axhline(0, color='black', lw=0.8, ls='--')
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels(compare_scen, rotation=30, ha='right')
    ax.set_ylabel("EUI reduction vs 2005 (%)")
    ax.set_xlabel("Code Scenario")
    for x, v in zip(xs, impr):
        ax.text(x, v + (0.1 if v >= 0 else -0.5), f"{v:.1f}%", ha='center', va='bottom', fontsize=8)
fig.suptitle("Total EUI Improvement vs 2005 Baseline — All 6 Neighbourhoods (Montreal, N=3)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig4_improvement_vs_2005.png"), dpi=150)
plt.close()
print("fig4 done")

# ── Figure 5: Heatmap ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for ax, metric in zip(axes, ["Heating", "Cooling"]):
    mat = []
    for n, df in data.items():
        row = [df.loc[metric, f"{sc}_mean"] if (f"{sc}_mean" in df.columns and metric in df.index) else np.nan
               for sc in scenarios]
        mat.append(row)
    mat = np.array(mat)
    im = ax.imshow(mat, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, rotation=30, ha='right')
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(list(data.keys()))
    ax.set_title(f"{metric} EUI Heatmap (kWh/m\u00b2/yr)", fontweight='bold')
    plt.colorbar(im, ax=ax)
    for i in range(len(data)):
        for j in range(len(scenarios)):
            ax.text(j, i, f"{mat[i,j]:.1f}", ha='center', va='center', fontsize=8, color='black')
fig.suptitle("Neighbourhood x Scenario Heatmap — Heating & Cooling (All 6)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig5_heatmap.png"), dpi=150)
plt.close()
print("fig5 done")

# ── Text summary ──
lines = [
    "INTERIM BATCH MC REPORT — BatchAll_MC_N3_1776120359",
    "="*60,
    "Run: N=3 iterations, Fast Mode (24 TMY weeks), Montreal EPW",
    "Status: All 6 neighbourhoods complete (RC1 Default patched 2026-04-16)",
    "",
    "All Neighbourhoods Summary",
    "-"*40,
]
for n, df in data.items():
    lines.append(f"\n{n}:")
    for sc in scenarios:
        mc = f"{sc}_mean"
        if mc in df.columns:
            tot = df[mc].sum()
            lines.append(f"  {sc:8s}: Total EUI = {tot:6.1f} kWh/m2/yr")
# ── Copy section 4.3 figures into interim_report ──
fig43_files = [
    "Figure_4.3.1_Energy_Demand.png",
    "Figure_4.3.2_Temporal_Trend.png",
    "Figure_4.3.3_Diurnal_Profiles.png",
    "Figure_4.3.4_Peak_Loads.png",
]
for fname in fig43_files:
    src = os.path.join(plotting_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(OUT, fname))
        print(f"copied {fname}")
    else:
        print(f"MISSING (skipped): {fname}")

lines.append("\nFigures saved to: " + OUT)
for f in ["fig1_total_eui_by_scenario.png","fig2_stacked_enduse.png",
          "fig3_heating_cooling.png","fig4_improvement_vs_2005.png","fig5_heatmap.png"] + fig43_files:
    lines.append("  " + f)

summary = "\n".join(lines)
with open(os.path.join(OUT, "interim_summary.txt"), "w") as fh:
    fh.write(summary)
print(summary)
