import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import sqlite3

_DEFAULT_BASE = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults\BatchAll_MC_N3_1776120359"
BASE  = os.environ.get("ESIM_BATCH_DIR", _DEFAULT_BASE)
OUT   = os.path.join(BASE, "interim_report")
CACHE = os.path.join(BASE, "_sql_cache")
os.makedirs(OUT, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

def _cache_fresh(cache_path, src_path):
    return (os.path.exists(cache_path) and os.path.exists(src_path)
            and os.path.getmtime(cache_path) >= os.path.getmtime(src_path))

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
    vmin = min(totals.values()); vmax = max(totals.values())
    span = max(vmax - vmin, 1e-6)
    ax.set_ylim(max(0, vmin - span * 0.6), vmax + span * 0.5)
    for bar, sc in zip(bars, scenarios):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+span*0.04,
                f"{totals[sc]:.1f}", ha='center', va='bottom', fontsize=7)
fig.suptitle("Total EUI by Code Scenario — All 6 Neighbourhoods (Montreal, N=20)",
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
    tmin = float(bottoms.min()); tmax = float(bottoms.max())
    span = max(tmax - tmin, 1e-6)
    ax.set_ylim(max(0, tmin - span * 0.6), tmax + span * 0.4)
    ax.legend(loc='upper right', fontsize=7)
fig.suptitle("Stacked End-Use EUI by Code Scenario — All 6 Neighbourhoods (Montreal, N=20)",
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
    combined = [v for v in (h_vals + c_vals) if v > 0]
    if combined:
        vmin, vmax = min(combined), max(combined)
        span = max(vmax - vmin, 1e-6)
        ax.set_ylim(max(0, vmin - span * 0.5), vmax + span * 0.3)
    ax.legend(fontsize=8)
fig.suptitle("Heating vs Cooling EUI — All 6 Neighbourhoods (Montreal, N=20)",
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
fig.suptitle("Total EUI Improvement vs 2005 Baseline — All 6 Neighbourhoods (Montreal, N=20)",
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

# ── Task B: Copy per-neighbourhood MC plots to Sim_plots/ ──
SIM_PLOTS = os.path.join(BASE, "Sim_plots")
os.makedirs(SIM_PLOTS, exist_ok=True)
_DEFAULT_PLOTTING_DIR = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults_Plotting"
PLOTTING_DIR = os.environ.get("ESIM_PLOTTING_DIR", _DEFAULT_PLOTTING_DIR)
import glob as _glob
copied, missing = 0, 0
for pattern in ["MonteCarlo_Neighbourhood_EUI_*.png", "MonteCarlo_Neighbourhood_TimeSeries_*.png"]:
    for src in _glob.glob(os.path.join(PLOTTING_DIR, pattern)):
        shutil.copy2(src, os.path.join(SIM_PLOTS, os.path.basename(src)))
        copied += 1
print(f"Sim_plots: {copied} PNGs copied, {missing} missing — {SIM_PLOTS}")

# ── Figure 4.3.1: Energy Demand — H/C bar chart per neighbourhood ──
scen_431 = ["Default", "2005", "2010", "2015", "2022", "2025"]
sc_lab_431 = ["Def", "'05", "'10", "'15", "'22", "'25"]
idx_431 = np.arange(len(scen_431))
w_431 = 0.35
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes_flat = axes.flatten()
all_h = [df.loc["Heating", f"{sc}_mean"] for df in data.values()
         for sc in scen_431 if f"{sc}_mean" in df.columns and "Heating" in df.index]
all_c = [df.loc["Cooling",  f"{sc}_mean"] for df in data.values()
         for sc in scen_431 if f"{sc}_mean" in df.columns and "Cooling"  in df.index]
ylim_h431 = (0, max(all_h) * 1.3) if all_h else (0, 1)
ylim_c431 = (0, max(all_c) * 1.3) if all_c else (0, 1)
for ax, (n, df) in zip(axes_flat, data.items()):
    h_m = [df.loc["Heating", f"{sc}_mean"] if (f"{sc}_mean" in df.columns and "Heating" in df.index) else 0
           for sc in scen_431]
    h_s = [df.loc["Heating", f"{sc}_std"]  if (f"{sc}_std"  in df.columns and "Heating" in df.index) else 0
           for sc in scen_431]
    c_m = [df.loc["Cooling",  f"{sc}_mean"] if (f"{sc}_mean" in df.columns and "Cooling" in df.index) else 0
           for sc in scen_431]
    c_s = [df.loc["Cooling",  f"{sc}_std"]  if (f"{sc}_std"  in df.columns and "Cooling" in df.index) else 0
           for sc in scen_431]
    ax.bar(idx_431 - w_431/2, h_m, w_431, yerr=h_s, capsize=3,
           color='#d62728', alpha=0.6, label='Heating')
    ax.bar(idx_431 + w_431/2, c_m, w_431, yerr=c_s, capsize=3,
           color='#1f77b4', alpha=0.6, label='Cooling')
    combined_n = [v for v in (h_m + c_m) if v > 0]
    if combined_n:
        vmin_n, vmax_n = min(combined_n), max(combined_n)
        span_n = max(vmax_n - vmin_n, 1e-6)
        ax.set_ylim(max(0, vmin_n - span_n * 0.4), vmax_n + span_n * 0.55)
    else:
        span_n = 1.0
    def_h = h_m[0] if h_m[0] > 0 else None
    def_c = c_m[0] if c_m[0] > 0 else None
    for i in range(1, len(scen_431)):
        if def_h:
            pct = (h_m[i] - def_h) / def_h * 100
            ax.text(idx_431[i] - w_431/2, h_m[i] + h_s[i] + span_n * 0.05,
                    f"{pct:+.0f}%", ha='center', va='bottom', fontsize=7, color='#d62728')
        if def_c:
            pct = (c_m[i] - def_c) / def_c * 100
            ax.text(idx_431[i] + w_431/2, c_m[i] + c_s[i] + span_n * 0.05,
                    f"{pct:+.0f}%", ha='center', va='bottom', fontsize=7, color='#1f77b4')
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(idx_431)
    ax.set_xticklabels(sc_lab_431)
    ax.set_ylabel("EUI (kWh/m\u00b2/yr)", fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.legend(fontsize=7)
fig.suptitle("Figure 4.3.1 — Annual Energy Demand by Code Scenario (All Neighbourhoods, N=20)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_4.3.1_Energy_Demand.png"), dpi=150)
plt.close()
print("Figure 4.3.1 done")

# ── Figure 4.3.2: Temporal Trend — EUI over code years ──
years_432 = [2005, 2010, 2015, 2022, 2025]
scen_432 = ["2005", "2010", "2015", "2022", "2025"]
fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
axes_flat = axes.flatten()
all_h2 = [df.loc["Heating", f"{sc}_mean"] for df in data.values()
          for sc in scen_432 if f"{sc}_mean" in df.columns and "Heating" in df.index]
all_c2 = [df.loc["Cooling",  f"{sc}_mean"] for df in data.values()
          for sc in scen_432 if f"{sc}_mean" in df.columns and "Cooling"  in df.index]
ylim_h432 = (max(0, min(all_h2) * 0.8), max(all_h2) * 1.2) if all_h2 else (0, 1)
ylim_c432 = (max(0, min(all_c2) * 0.8), max(all_c2) * 1.2) if all_c2 else (0, 1)
for ax, (n, df) in zip(axes_flat, data.items()):
    h_vals = [df.loc["Heating", f"{sc}_mean"] if (f"{sc}_mean" in df.columns and "Heating" in df.index) else np.nan
              for sc in scen_432]
    c_vals = [df.loc["Cooling",  f"{sc}_mean"] if (f"{sc}_mean" in df.columns and "Cooling"  in df.index) else np.nan
              for sc in scen_432]
    def_h = df.loc["Heating", "Default_mean"] if ("Default_mean" in df.columns and "Heating" in df.index) else None
    def_c = df.loc["Cooling",  "Default_mean"] if ("Default_mean" in df.columns and "Cooling"  in df.index) else None
    ax.plot(years_432, h_vals, marker='s', color='#d62728', linewidth=2, label='Heating')
    ax.plot(years_432, c_vals, marker='^', color='#1f77b4', linewidth=2, label='Cooling')
    if def_h is not None:
        ax.axhline(def_h, color='#d62728', linestyle=':', linewidth=1.5, alpha=0.6, label='Def H')
    if def_c is not None:
        ax.axhline(def_c, color='#1f77b4', linestyle=':', linewidth=1.5, alpha=0.6, label='Def C')
    ax.set_title(n, fontweight='bold')
    ax.set_xticks(years_432)
    ax.set_xticklabels([str(y) for y in years_432], rotation=30, ha='right')
    ax.set_ylabel("EUI (kWh/m\u00b2/yr)", fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(fontsize=7)
fig.suptitle("Figure 4.3.2 — EUI Temporal Trend by Code Year (All Neighbourhoods, N=20)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_4.3.2_Temporal_Trend.png"), dpi=150)
plt.close()
print("Figure 4.3.2 done")

# ── Figure 4.3.3: Diurnal Profiles — seasonal H/C from eplusout.sql ──

def _get_area_from_tabular(cursor):
    try:
        cursor.execute(
            "SELECT Value FROM TabularDataWithStrings "
            "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
            "AND TableName='Building Area' "
            "AND RowName='Net Conditioned Building Area' "
            "AND ColumnName='Area'"
        )
        res = cursor.fetchone()
        if res:
            return float(res[0])
    except Exception:
        pass
    return None

# Pre-compute reference areas from code-scenario SQL (for Default fallback)
_ref_areas = {}
for _n in nhoods:
    for _sc in ["2005", "2010", "2015", "2022", "2025"]:
        _ref_sql = os.path.join(BASE, _n, "iter_1", _sc, "eplusout.sql")
        if os.path.exists(_ref_sql):
            try:
                _conn = sqlite3.connect(_ref_sql)
                _area = _get_area_from_tabular(_conn.cursor())
                _conn.close()
                if _area is not None:
                    _ref_areas[_n] = _area
                    break
            except Exception:
                pass
print(f"Reference areas: { {k: f'{v:.1f}' for k, v in _ref_areas.items()} }")

def _get_area(cursor, neighbourhood):
    """Get conditioned area: try TabularData first, fall back to reference area from code scenario."""
    area = _get_area_from_tabular(cursor)
    if area is not None:
        return area
    if neighbourhood in _ref_areas:
        print(f"  Using reference area {_ref_areas[neighbourhood]:.1f} m² for {neighbourhood}")
        return _ref_areas[neighbourhood]
    return 1.0

def _extract_diurnal(sql_path, neighbourhood=None):
    """Returns DataFrame [Month, Day, Hour, DayType, Heating, Cooling] or None."""
    if not os.path.exists(sql_path):
        return None
    try:
        conn = sqlite3.connect(sql_path)
        cur = conn.cursor()
        var_ids = {}
        for key, vname in [('Heating', 'Heating:EnergyTransfer'),
                            ('Cooling', 'Cooling:EnergyTransfer')]:
            cur.execute("SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name=?", (vname,))
            row = cur.fetchone()
            if row:
                var_ids[key] = row[0]
            else:
                conn.close()
                return None
        area = _get_area(cur, neighbourhood)
        query = f"""
            SELECT t.Month, t.Day, t.Hour, t.DayType,
                   rd_h.Value as Heat, rd_c.Value as Cool
            FROM Time t
            JOIN ReportData rd_h ON t.TimeIndex = rd_h.TimeIndex
                 AND rd_h.ReportDataDictionaryIndex = {var_ids['Heating']}
            JOIN ReportData rd_c ON t.TimeIndex = rd_c.TimeIndex
                 AND rd_c.ReportDataDictionaryIndex = {var_ids['Cooling']}
            ORDER BY t.TimeIndex
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['Heating'] = (df['Heat'] / 3600.0) / area
        df['Cooling'] = (df['Cool'] / 3600.0) / area
        df['Hour'] = df['Hour'] - 1
        return df[['Month', 'Day', 'Hour', 'DayType', 'Heating', 'Cooling']]
    except Exception as e:
        print(f"WARNING 4.3.3: {sql_path} — {e}")
        return None

scen_433 = ["Default", "2005", "2010", "2015", "2022", "2025"]
collected_433 = []
for n in nhoods:
    for sc in scen_433:
        if sc == "Default":
            sql_p = os.path.join(BASE, n, "Default", "eplusout.sql")
        else:
            sql_p = os.path.join(BASE, n, "iter_1", sc, "eplusout.sql")
        cache_p = os.path.join(CACHE, f"diurnal_{n}_{sc}.parquet")
        if _cache_fresh(cache_p, sql_p):
            df_sql = pd.read_parquet(cache_p)
        else:
            df_sql = _extract_diurnal(sql_p, neighbourhood=n)
            if df_sql is not None:
                df_sql.to_parquet(cache_p)
        if df_sql is not None:
            df_sql['Scenario'] = sc
            collected_433.append(df_sql)
        else:
            print(f"  4.3.3 skip: {n}/{sc}")

if collected_433:
    full_433 = pd.concat(collected_433, ignore_index=True)
    full_433 = full_433[full_433['Month'].isin([1, 7])].copy()
    full_433['Season'] = full_433['Month'].map({1: 'Winter', 7: 'Summer'})
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    weekends = {'Saturday', 'Sunday'}
    def _day_cat(dt):
        if dt in weekdays: return 'Weekday'
        if dt in weekends: return 'Weekend'
        return 'Other'
    full_433['DayCat'] = full_433['DayType'].apply(_day_cat)
    full_433 = full_433[full_433['DayCat'] != 'Other']
    grp_433 = full_433.groupby(['Scenario', 'Season', 'DayCat', 'Hour'])\
                      .agg({'Heating': 'mean', 'Cooling': 'mean'}).reset_index()

    fig, axes = plt.subplots(1, 4, figsize=(24, 5), sharey=False)
    clr_433 = {"Default": "black", "2005": "#1f77b4", "2010": "#ff7f0e",
                "2015": "#bcbd22", "2022": "#2ca02c", "2025": "#9467bd"}
    sty_433 = {"Default": ":", "2005": "--", "2010": "--",
               "2015": "-.", "2022": "-.", "2025": "-"}
    wid_433 = {"Default": 2.5, "2005": 1.5, "2010": 1.5,
               "2015": 1.5, "2022": 1.5, "2025": 2.5}
    scen_433_plot = ["Default", "2005", "2010", "2015", "2022", "2025"]
    subplots_433 = [
        (0, 'Winter', 'Weekday', 'Heating', '(a) Winter Weekday (Jan)\nHeating Load'),
        (1, 'Winter', 'Weekend', 'Heating', '(b) Winter Weekend (Jan)\nHeating Load'),
        (2, 'Summer', 'Weekday', 'Cooling', '(c) Summer Weekday (Jul)\nCooling Load'),
        (3, 'Summer', 'Weekend', 'Cooling', '(d) Summer Weekend (Jul)\nCooling Load'),
    ]
    for (idx, season, daycat, var, title) in subplots_433:
        ax = axes[idx]
        for scen in scen_433_plot:
            sub = grp_433[(grp_433['Scenario'] == scen) &
                          (grp_433['Season'] == season) &
                          (grp_433['DayCat'] == daycat)].sort_values('Hour')
            if not sub.empty:
                ax.plot(sub['Hour'], sub[var],
                        label=scen,
                        color=clr_433.get(scen, 'gray'),
                        linestyle=sty_433.get(scen, '-'),
                        linewidth=wid_433.get(scen, 1.5))
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim(0, 23)
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_xlabel("Hour of Day", fontsize=10)
        ax.grid(True, alpha=0.3)
        if idx in (0, 2):
            ax.set_ylabel("Avg Load (W/m\u00b2)", fontsize=11)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=6, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "Figure_4.3.3_Diurnal_Profiles.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Figure 4.3.3 done")
else:
    print("WARNING: Figure 4.3.3 — no SQL data extracted, figure skipped")

# ── Figure 4.3.4: Peak Loads from eplusout.sql ──

def _extract_peak(sql_path, neighbourhood=None):
    """Returns {'Heating': (W/m2, timestamp), 'Cooling': (W/m2, timestamp)} or None."""
    if not os.path.exists(sql_path):
        return None
    try:
        conn = sqlite3.connect(sql_path)
        area = _get_area(conn.cursor(), neighbourhood)
        peaks = {}
        for key, vname in [('Heating', 'Zone Air System Sensible Heating Energy'),
                            ('Cooling', 'Zone Air System Sensible Cooling Energy')]:
            ids_df = pd.read_sql_query(
                f"SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name='{vname}'", conn)
            if ids_df.empty:
                conn.close()
                return None
            ids_str = ",".join(map(str, ids_df['ReportDataDictionaryIndex'].tolist()))
            peak_df = pd.read_sql_query(
                f"SELECT rd.TimeIndex, SUM(rd.Value) AS TotalValue "
                f"FROM ReportData rd WHERE rd.ReportDataDictionaryIndex IN ({ids_str}) "
                f"GROUP BY rd.TimeIndex ORDER BY TotalValue DESC LIMIT 1", conn)
            if peak_df.empty:
                conn.close()
                return None
            peak_val = peak_df.iloc[0]['TotalValue']
            ti = peak_df.iloc[0]['TimeIndex']
            t_df = pd.read_sql_query(f"SELECT Month, Day, Hour FROM Time WHERE TimeIndex={ti}", conn)
            m, d, h = t_df.iloc[0]['Month'], t_df.iloc[0]['Day'], t_df.iloc[0]['Hour']
            import calendar as _cal
            ts = f"{_cal.month_name[int(m)][:3]} {int(d):02d} {int(h)-1:02d}:00"
            peaks[key] = ((peak_val / 3600.0) / area, ts)
        conn.close()
        return peaks
    except Exception as e:
        print(f"WARNING 4.3.4: {sql_path} — {e}")
        return None

def _extract_occ_signals(sql_path, neighbourhood=None):
    """Returns DataFrame [Month, Day, Hour, DayType, People, Equipment, Lights, DHW,
    Heating, Cooling] or None. Units: W/m\u00b2 (J/3600/area).
    People = SUM Zone People Total Heating Energy across all zones."""
    if not os.path.exists(sql_path):
        return None
    try:
        conn = sqlite3.connect(sql_path)
        cur = conn.cursor()
        area = _get_area(cur, neighbourhood)
        bldg_vars = {
            'Equipment': 'InteriorEquipment:Electricity',
            'Lights':    'InteriorLights:Electricity',
            'DHW':       'WaterSystems:EnergyTransfer',
            'Heating':   'Heating:EnergyTransfer',
            'Cooling':   'Cooling:EnergyTransfer',
        }
        var_ids = {}
        for key, vname in bldg_vars.items():
            cur.execute(
                "SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name=?",
                (vname,))
            row = cur.fetchone()
            if row:
                var_ids[key] = row[0]
            else:
                print(f"  occ_signals: '{vname}' not found in {os.path.basename(sql_path)}")
        cur.execute(
            "SELECT ReportDataDictionaryIndex FROM ReportDataDictionary "
            "WHERE Name='Zone People Total Heating Energy'")
        ppl_rows = cur.fetchall()
        if ppl_rows:
            ppl_ids_str = ",".join(str(r[0]) for r in ppl_rows)
            ppl_df = pd.read_sql_query(
                f"SELECT TimeIndex, SUM(Value) AS PeopleJ FROM ReportData "
                f"WHERE ReportDataDictionaryIndex IN ({ppl_ids_str}) GROUP BY TimeIndex", conn)
            ppl_map = dict(zip(ppl_df['TimeIndex'], ppl_df['PeopleJ']))
        else:
            print(f"  occ_signals: 'Zone People Total Heating Energy' not found in "
                  f"{os.path.basename(sql_path)}")
            ppl_map = {}
        if not var_ids and not ppl_map:
            conn.close()
            return None
        time_df = pd.read_sql_query(
            "SELECT TimeIndex, Month, Day, Hour, DayType FROM Time", conn)
        for key, vid in var_ids.items():
            val_df = pd.read_sql_query(
                f"SELECT TimeIndex, Value FROM ReportData "
                f"WHERE ReportDataDictionaryIndex={vid}", conn)
            time_df = time_df.merge(
                val_df.rename(columns={'Value': key}), on='TimeIndex', how='left')
        conn.close()
        time_df['People'] = time_df['TimeIndex'].map(ppl_map).fillna(0.0)
        for col in [c for c in ['Equipment', 'Lights', 'DHW', 'People', 'Heating', 'Cooling']
                    if c in time_df.columns]:
            time_df[col] = (time_df[col].fillna(0.0) / 3600.0) / area
        time_df['Hour'] = time_df['Hour'] - 1
        keep = [c for c in ['Month', 'Day', 'Hour', 'DayType', 'People',
                             'Equipment', 'Lights', 'DHW', 'Heating', 'Cooling']
                if c in time_df.columns]
        return time_df[keep]
    except Exception as e:
        print(f"WARNING occ_signals: {sql_path} \u2014 {e}")
        return None

scen_434 = ["Default", "2005", "2010", "2015", "2022", "2025"]
results_434 = []
for sc in scen_434:
    h_vals_sc, c_vals_sc = [], []
    ts_h, ts_c = None, None
    for n in nhoods:
        if sc == "Default":
            sql_p = os.path.join(BASE, n, "Default", "eplusout.sql")
        else:
            sql_p = os.path.join(BASE, n, "iter_1", sc, "eplusout.sql")
        cache_pk = os.path.join(CACHE, f"peak_{n}_{sc}.json")
        if _cache_fresh(cache_pk, sql_p):
            import json as _json
            with open(cache_pk) as _fh:
                _raw = _json.load(_fh)
            pk = {k: tuple(v) for k, v in _raw.items()}
        else:
            pk = _extract_peak(sql_p, neighbourhood=n)
            if pk:
                import json as _json
                with open(cache_pk, "w") as _fh:
                    _json.dump({k: list(v) for k, v in pk.items()}, _fh)
        if pk:
            h_vals_sc.append(pk['Heating'][0])
            c_vals_sc.append(pk['Cooling'][0])
            if ts_h is None:
                ts_h = pk['Heating'][1]
                ts_c = pk['Cooling'][1]
        else:
            print(f"  4.3.4 skip: {n}/{sc}")
    if h_vals_sc:
        results_434.append({
            "Scenario": sc,
            "Peak Heating (W/m\u00b2)": float(np.mean(h_vals_sc)),
            "Time (Heating)": ts_h or "N/A",
            "Peak Cooling (W/m\u00b2)": float(np.mean(c_vals_sc)),
            "Time (Cooling)": ts_c or "N/A",
        })

if results_434:
    df_434 = pd.DataFrame(results_434)
    x_434 = np.arange(len(df_434))
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    ax_h, ax_c = axes
    bars_h = ax_h.bar(x_434, df_434["Peak Heating (W/m\u00b2)"], color='#d62728', alpha=0.6)
    ax_h.set_title('(a) Peak Heating Load (avg across neighbourhoods)', fontsize=11, fontweight='bold')
    ax_h.set_ylabel('Peak Load (W/m\u00b2)', fontsize=11)
    ax_h.set_xticks(x_434); ax_h.set_xticklabels(df_434["Scenario"])
    h_min = df_434["Peak Heating (W/m\u00b2)"].min()
    h_max = df_434["Peak Heating (W/m\u00b2)"].max()
    h_span = max(h_max - h_min, 1e-6)
    ax_h.set_ylim(max(0, h_min - h_span * 0.4), h_max + h_span * 0.5)
    ax_h.grid(axis='y', linestyle='--', alpha=0.5)
    bars_c = ax_c.bar(x_434, df_434["Peak Cooling (W/m\u00b2)"], color='#1f77b4', alpha=0.6)
    ax_c.set_title('(b) Peak Cooling Load (avg across neighbourhoods)', fontsize=11, fontweight='bold')
    ax_c.set_ylabel('Peak Load (W/m\u00b2)', fontsize=11)
    ax_c.set_xticks(x_434); ax_c.set_xticklabels(df_434["Scenario"])
    c_min = df_434["Peak Cooling (W/m\u00b2)"].min()
    c_max = df_434["Peak Cooling (W/m\u00b2)"].max()
    c_span = max(c_max - c_min, 1e-6)
    ax_c.set_ylim(max(0, c_min - c_span * 0.4), c_max + c_span * 0.5)
    ax_c.grid(axis='y', linestyle='--', alpha=0.5)
    for rect, val in zip(bars_h, df_434["Peak Heating (W/m\u00b2)"]):
        ax_h.annotate(f'{val:.2f} W/m\u00b2',
                      xy=(rect.get_x() + rect.get_width()/2, rect.get_height()),
                      xytext=(0, 3), textcoords="offset points",
                      ha='center', va='bottom', fontsize=9, fontweight='bold')
    for rect, val in zip(bars_c, df_434["Peak Cooling (W/m\u00b2)"]):
        ax_c.annotate(f'{val:.2f} W/m\u00b2',
                      xy=(rect.get_x() + rect.get_width()/2, rect.get_height()),
                      xytext=(0, 3), textcoords="offset points",
                      ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "Figure_4.3.4_Peak_Loads.png"), dpi=150)
    plt.close()
    print("Figure 4.3.4 done")
else:
    print("WARNING: Figure 4.3.4 — no SQL data extracted, figure skipped")

# ── Task 3: Occ-signal extraction (Equipment / Lights / DHW / Presence / H&C) ──
_occ_weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
_occ_weekends = {'Saturday', 'Sunday'}
def _occ_day_cat(dt):
    if dt in _occ_weekdays: return 'Weekday'
    if dt in _occ_weekends: return 'Weekend'
    return 'Other'

scen_occ = ["Default", "2005", "2010", "2015", "2022", "2025"]
collected_occ = []
for _n_occ in nhoods:
    for _sc_occ in scen_occ:
        if _sc_occ == "Default":
            _sql_occ = os.path.join(BASE, _n_occ, "Default", "eplusout.sql")
        else:
            _sql_occ = os.path.join(BASE, _n_occ, "iter_1", _sc_occ, "eplusout.sql")
        _cache_occ = os.path.join(CACHE, f"occdiurnal_{_n_occ}_{_sc_occ}.parquet")
        if _cache_fresh(_cache_occ, _sql_occ):
            _df_occ = pd.read_parquet(_cache_occ)
        else:
            _df_occ = _extract_occ_signals(_sql_occ, neighbourhood=_n_occ)
            if _df_occ is not None:
                _df_occ.to_parquet(_cache_occ)
        if _df_occ is not None:
            _df_occ = _df_occ.copy()
            _df_occ['Neighbourhood'] = _n_occ
            _df_occ['Scenario'] = _sc_occ
            collected_occ.append(_df_occ)
        else:
            print(f"  occ_signals skip: {_n_occ}/{_sc_occ}")

if collected_occ:
    full_occ = pd.concat(collected_occ, ignore_index=True)
    full_occ = full_occ[full_occ['Month'].isin([1, 7])].copy()
    full_occ['Season'] = full_occ['Month'].map({1: 'Winter', 7: 'Summer'})
    full_occ['DayCat'] = full_occ['DayType'].apply(_occ_day_cat)
    full_occ = full_occ[full_occ['DayCat'] != 'Other']
    _occ_sig_cols = [c for c in ['People', 'Equipment', 'Lights', 'DHW', 'Heating', 'Cooling']
                     if c in full_occ.columns]
    grp_occ = full_occ.groupby(
        ['Neighbourhood', 'Scenario', 'Season', 'DayCat', 'Hour']
    ).agg({c: 'mean' for c in _occ_sig_cols}).reset_index()
    print(f"Task 3: {len(collected_occ)} occ parquet files loaded/cached. "
          f"grp_occ shape: {grp_occ.shape}")
else:
    grp_occ = pd.DataFrame()
    print("WARNING Task 3: no occ signal data extracted — B.1 figure will be skipped.")

# ── Occupancy-Impact Figures (Tier A) ──

_OCC_EU4 = ["Heating", "Cooling", "Electric Equipment", "Water Systems"]
_OCC_ALL_SC = ["2005", "2010", "2015", "2022", "2025", "Default"]
_OCC_CODE_SC = ["2005", "2010", "2015", "2022", "2025"]
_OCC_NCLR = dict(zip(nhoods, ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']))
_OCC_DISCLAIMER = "Default\u2013scenario delta includes schedule + archetype-field effects"

# ── Figure_Occ_A1: End-Use Delta Bar ──
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()
for _ax_idx, _eu in enumerate(_OCC_EU4):
    _ax = axes[_ax_idx]
    _xs = np.arange(len(_OCC_CODE_SC))
    _w = 0.12
    for _ni, (_n, _df) in enumerate(data.items()):
        if "Default_mean" not in _df.columns or _eu not in _df.index:
            continue
        _def_val = float(_df.loc[_eu, "Default_mean"])
        _deltas = [
            float(_df.loc[_eu, f"{_sc}_mean"]) - _def_val
            if f"{_sc}_mean" in _df.columns else 0.0
            for _sc in _OCC_CODE_SC
        ]
        _offset = (_ni - len(data) / 2 + 0.5) * _w
        _ax.bar(_xs + _offset, _deltas, _w, color=_OCC_NCLR[_n], alpha=0.80,
                label=_n if _ax_idx == 0 else "")
    _ax.axhline(0, color='black', lw=0.8, ls='--')
    _ax.set_title(_eu, fontweight='bold')
    _ax.set_xticks(_xs)
    _ax.set_xticklabels(_OCC_CODE_SC)
    _ax.set_ylabel("\u0394 EUI (kWh/m\u00b2/yr)")
    _ax.set_xlabel("Scenario")
    _ax.grid(axis='y', alpha=0.3)
_h_a1, _l_a1 = axes[0].get_legend_handles_labels()
fig.legend(_h_a1, _l_a1, loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=3, fontsize=9)
fig.suptitle(
    "Figure_Occ_A1 \u2014 End-Use EUI Delta (Scenario \u2212 Default), All Neighbourhoods (N=20)\n"
    "[" + _OCC_DISCLAIMER + "]",
    fontsize=10, fontweight='bold', y=1.04)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_Occ_A1_EndUse_Delta.png"), dpi=150, bbox_inches='tight')
plt.close()
print("Figure_Occ_A1 done")

# ── Figure_Occ_A3: Sensitivity Tornado ──
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
axes = axes.flatten()
for _ax_idx, _eu in enumerate(_OCC_EU4):
    _ax = axes[_ax_idx]
    _ys_t, _widths_t, _bar_clrs_t, _annotations_t = [], [], [], []
    for _ni, (_n, _df) in enumerate(data.items()):
        _vals_t = {}
        if _eu in _df.index:
            for _sc in _OCC_ALL_SC:
                _mc = f"{_sc}_mean"
                if _mc in _df.columns:
                    _vals_t[_sc] = float(_df.loc[_eu, _mc])
        if _vals_t:
            _min_sc = min(_vals_t, key=_vals_t.get)
            _max_sc = max(_vals_t, key=_vals_t.get)
            _rng_t = _vals_t[_max_sc] - _vals_t[_min_sc]
            _annotations_t.append(f"{_min_sc}\u2192{_max_sc}")
        else:
            _rng_t = 0.0
            _annotations_t.append("")
        _ys_t.append(_ni)
        _widths_t.append(_rng_t)
        _bar_clrs_t.append(_OCC_NCLR[_n])
    _ax.barh(_ys_t, _widths_t, color=_bar_clrs_t, alpha=0.8)
    _max_w_t = max(_widths_t) if _widths_t else 1.0
    for _yi, _rng_t, _ann in zip(_ys_t, _widths_t, _annotations_t):
        if _ann:
            _ax.text(_rng_t + _max_w_t * 0.02, _yi, _ann, va='center', fontsize=7)
    _ax.set_yticks(list(range(len(data))))
    _ax.set_yticklabels(list(data.keys()), fontsize=8)
    _ax.set_title(_eu, fontweight='bold')
    _ax.set_xlabel("EUI Range (kWh/m\u00b2/yr)")
    _ax.grid(axis='x', alpha=0.3)
fig.suptitle(
    "Figure_Occ_A3 \u2014 End-Use Sensitivity Tornado (Max\u2212Min across all 6 scenarios)\n"
    "All 6 Neighbourhoods (N=20)", fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_Occ_A3_Sensitivity_Tornado.png"), dpi=150)
plt.close()
print("Figure_Occ_A3 done")

# ── Figure_Occ_A4: Equipment <-> Cooling / Heating Coupling Scatter ──
_OCC_MKRS = {'2005': 'o', '2010': 's', '2015': '^', '2022': 'D', '2025': 'v', 'Default': '*'}
_x_eq, _y_co, _y_he, _pt_clrs, _pt_mks = [], [], [], [], []
for _ni, (_n, _df) in enumerate(data.items()):
    for _sc in _OCC_ALL_SC:
        _mc = f"{_sc}_mean"
        if _mc not in _df.columns:
            continue
        if not all(_e in _df.index for _e in ["Electric Equipment", "Cooling", "Heating"]):
            continue
        _x_eq.append(float(_df.loc["Electric Equipment", _mc]))
        _y_co.append(float(_df.loc["Cooling", _mc]))
        _y_he.append(float(_df.loc["Heating", _mc]))
        _pt_clrs.append(_OCC_NCLR[_n])
        _pt_mks.append(_OCC_MKRS[_sc])

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
for _ax, _y_vals, _ylabel, _title_sc in zip(
        axes,
        [_y_co, _y_he],
        ["Cooling EUI (kWh/m\u00b2/yr)", "Heating EUI (kWh/m\u00b2/yr)"],
        ["(a) Equipment \u2194 Cooling coupling", "(b) Equipment \u2194 Heating coupling"]):
    for _xi, _yi, _ci, _mi in zip(_x_eq, _y_vals, _pt_clrs, _pt_mks):
        _ax.scatter(_xi, _yi, color=_ci, marker=_mi, s=80, alpha=0.8, edgecolors='none')
    if len(_x_eq) > 1:
        _c_fit = np.polyfit(_x_eq, _y_vals, 1)
        _xf = np.linspace(min(_x_eq), max(_x_eq), 50)
        _ax.plot(_xf, np.polyval(_c_fit, _xf), 'k--', lw=1.5)
        _r2 = float(np.corrcoef(_x_eq, _y_vals)[0, 1] ** 2)
        _ax.annotate(f"R\u00b2={_r2:.2f}", xy=(0.05, 0.93), xycoords='axes fraction', fontsize=10)
    _ax.set_xlabel("Electric Equipment EUI (kWh/m\u00b2/yr)")
    _ax.set_ylabel(_ylabel)
    _ax.set_title(_title_sc, fontsize=11, fontweight='bold')
    _ax.grid(alpha=0.3)
for _n in nhoods:
    axes[0].scatter([], [], color=_OCC_NCLR[_n], marker='o', s=50, label=_n)
for _sc, _mk in _OCC_MKRS.items():
    axes[0].scatter([], [], color='grey', marker=_mk, s=50, label=_sc)
axes[0].legend(fontsize=7, loc='lower right', ncol=2)
fig.suptitle(
    "Figure_Occ_A4 \u2014 Equipment \u2194 Cooling/Heating Coupling Scatter\n"
    "All 6 Neighbourhoods \u00d7 6 Scenarios (N=20)", fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_Occ_A4_Coupling_Scatter.png"), dpi=150)
plt.close()
print("Figure_Occ_A4 done")

# ── Figure_Occ_B4: Waterfall Default -> 2025 ──
_WF_EU = ["Heating", "Cooling", "Interior Lighting", "Electric Equipment", "Water Systems"]
_WF_SHORT = {"Heating": "Heat", "Cooling": "Cool", "Interior Lighting": "Lights",
             "Electric Equipment": "Equip", "Water Systems": "DHW"}
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()
for _ax_idx, (_n, _df) in enumerate(data.items()):
    _ax = axes[_ax_idx]
    if "Default_mean" not in _df.columns or "2025_mean" not in _df.columns:
        _ax.text(0.5, 0.5, "No data", transform=_ax.transAxes, ha='center')
        continue
    _def_tot = sum(float(_df.loc[_eu, "Default_mean"]) for _eu in _WF_EU if _eu in _df.index)
    _s25_tot = sum(float(_df.loc[_eu, "2025_mean"]) for _eu in _WF_EU if _eu in _df.index)
    _deltas_wf = [
        float(_df.loc[_eu, "2025_mean"]) - float(_df.loc[_eu, "Default_mean"])
        if _eu in _df.index else 0.0 for _eu in _WF_EU
    ]
    _labels_wf = ["Default"] + [_WF_SHORT[_eu] for _eu in _WF_EU] + ["2025"]
    _heights_wf, _bottoms_wf, _clrs_wf = [], [], []
    _heights_wf.append(_def_tot)
    _bottoms_wf.append(0.0)
    _clrs_wf.append("#7f7f7f")
    _running_wf = _def_tot
    for _d in _deltas_wf:
        if _d >= 0:
            _bottoms_wf.append(_running_wf)
            _heights_wf.append(_d)
            _clrs_wf.append("#d62728")
        else:
            _bottoms_wf.append(_running_wf + _d)
            _heights_wf.append(-_d)
            _clrs_wf.append("#2ca02c")
        _running_wf += _d
    _heights_wf.append(_s25_tot)
    _bottoms_wf.append(0.0)
    _clrs_wf.append("#1f77b4")
    _xs_wf = np.arange(len(_labels_wf))
    _ax.bar(_xs_wf, _heights_wf, bottom=_bottoms_wf, color=_clrs_wf,
            alpha=0.80, edgecolor='black', linewidth=0.5)
    _run_ann = _def_tot
    for _xi_w, _d in enumerate(_deltas_wf):
        _mid = _run_ann + _d / 2.0
        if abs(_d) > 0.01:
            _ax.text(_xi_w + 1, _mid, f"{_d:+.1f}", ha='center', va='center', fontsize=7,
                     color='white' if abs(_d) > 1.0 else 'black', fontweight='bold')
        _run_ann += _d
    _ax.text(0, _def_tot / 2, f"{_def_tot:.1f}", ha='center', va='center',
             fontsize=7, color='white', fontweight='bold')
    _ax.text(len(_labels_wf) - 1, _s25_tot / 2, f"{_s25_tot:.1f}", ha='center', va='center',
             fontsize=7, color='white', fontweight='bold')
    _ax.set_title(_n, fontweight='bold')
    _ax.set_xticks(_xs_wf)
    _ax.set_xticklabels(_labels_wf, rotation=30, ha='right', fontsize=8)
    _ax.set_ylabel("Total EUI (kWh/m\u00b2/yr)")
    _ax.grid(axis='y', alpha=0.3)
fig.suptitle(
    "Figure_Occ_B4 \u2014 Waterfall: Default \u2192 2025 Total EUI by End-Use, "
    "All Neighbourhoods (N=20)\n[" + _OCC_DISCLAIMER + "]",
    fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_Occ_B4_Waterfall.png"), dpi=150)
plt.close()
print("Figure_Occ_B4 done")

# ── Figure_Occ_A2: Radar fingerprint ──
_RAD_EU = ["Heating", "Cooling", "Interior Lighting", "Electric Equipment", "Water Systems"]
_RAD_SC_PLOT = ["2005", "2010", "2015", "2022", "2025"]
_RAD_CLR = {"Default": "#7f7f7f", "2005": "#d62728", "2010": "#ff7f0e",
             "2015": "#bcbd22", "2022": "#2ca02c", "2025": "#1f77b4"}
_RAD_STY = {"Default": ":", "2005": "--", "2010": (0, (5, 1)),
             "2015": "-.", "2022": (0, (3, 1, 1, 1)), "2025": "-"}
_n_spk = len(_RAD_EU)
_rad_ang = np.linspace(0, 2 * np.pi, _n_spk, endpoint=False).tolist()
_rad_ang_c = _rad_ang + _rad_ang[:1]
fig, axes = plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(18, 12))
axes = axes.flatten()
for _ax_idx, (_n, _df) in enumerate(data.items()):
    _ax = axes[_ax_idx]
    if "Default_mean" not in _df.columns:
        continue
    _def_r = [float(_df.loc[_eu, "Default_mean"]) if _eu in _df.index else 1.0
              for _eu in _RAD_EU]
    _ax.plot(_rad_ang_c, [1.0] * _n_spk + [1.0],
             color=_RAD_CLR["Default"], linestyle=_RAD_STY["Default"],
             linewidth=2.0, label="Default")
    _ax.fill(_rad_ang_c, [1.0] * _n_spk + [1.0], color=_RAD_CLR["Default"], alpha=0.05)
    _all_ratios_r = []
    for _sc in _RAD_SC_PLOT:
        _mc = f"{_sc}_mean"
        if _mc not in _df.columns:
            continue
        _ratios = [
            float(_df.loc[_eu, _mc]) / _dv
            if (_eu in _df.index and abs(_dv) > 1e-6) else 1.0
            for _eu, _dv in zip(_RAD_EU, _def_r)
        ]
        _all_ratios_r.extend(_ratios)
        _ratios_c = _ratios + _ratios[:1]
        _ax.plot(_rad_ang_c, _ratios_c, color=_RAD_CLR[_sc], linestyle=_RAD_STY[_sc],
                 linewidth=2.0, label=_sc)
        _ax.fill(_rad_ang_c, _ratios_c, color=_RAD_CLR[_sc], alpha=0.08)
    _r_lo = min(_all_ratios_r) if _all_ratios_r else 0.9
    _r_hi = max(_all_ratios_r) if _all_ratios_r else 1.1
    _r_pad = max(0.01, (_r_hi - _r_lo) * 0.08)
    _yl_lo = max(0.0, _r_lo - _r_pad)
    _yl_hi = _r_hi + _r_pad
    _ax.set_ylim(_yl_lo, _yl_hi)
    _rticks = np.linspace(_yl_lo, _yl_hi, 6)[1:-1]
    _ax.set_yticks(_rticks)
    _ax.set_yticklabels([f"{v:.2f}" for v in _rticks], fontsize=5)
    _ax.set_xticks(_rad_ang)
    _ax.set_xticklabels(
        [f"{_eu.split()[-1]}\n({_dv:.1f})" for _eu, _dv in zip(_RAD_EU, _def_r)], fontsize=7)
    _ax.set_title(_n, fontweight='bold', pad=15)
    _ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=7)
fig.suptitle(
    "Figure_Occ_A2 \u2014 End-Use Radar Fingerprint (Normalized to Default=1.0)\n"
    "Scenarios: 2005, 2010, 2015, 2022, 2025 vs Default (N=20)\n"
    "(Spoke labels: end-use abbreviation and Default kWh/m\u00b2/yr)",
    fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, "Figure_Occ_A2_Radar_Fingerprint.png"), dpi=150,
            bbox_inches='tight')
plt.close()
print("Figure_Occ_A2 done")

# ── Task 7 (C.5): Weekday vs Weekend End-Use Delta — SKIPPED ──
# aggregated_eui.csv has no weekday/weekend split (schema: EndUse, sc_mean, sc_std only).
# Requires Task 3 SQL extraction (_extract_occ_signals with DayType) — implement after Task 3.
# ── Figure_Occ_C5: Weekday vs Weekend End-Use Delta ──
# Now implemented using grp_occ (Task 3 SQL extraction with DayType available).
_C5_EU = ([c for c in ['Equipment', 'Lights', 'DHW', 'Heating', 'Cooling']
            if c in grp_occ.columns]
           if not grp_occ.empty else [])
if not grp_occ.empty and _C5_EU:
    _dc_avg = (grp_occ
               .groupby(['Neighbourhood', 'Scenario', 'DayCat'])[_C5_EU]
               .mean()
               .reset_index())
    _wd_c5 = (_dc_avg[_dc_avg['DayCat'] == 'Weekday']
               .set_index(['Neighbourhood', 'Scenario']))
    _we_c5 = (_dc_avg[_dc_avg['DayCat'] == 'Weekend']
               .set_index(['Neighbourhood', 'Scenario']))
    _delta_c5 = (_we_c5[_C5_EU] - _wd_c5[_C5_EU]).reset_index()
    _scen_c5 = ["Default", "2005", "2010", "2015", "2022", "2025"]
    _xs_c5 = np.arange(len(_scen_c5))
    _w_c5 = 0.12
    fig, axes_c5 = plt.subplots(1, len(_C5_EU), figsize=(5 * len(_C5_EU), 6))
    if len(_C5_EU) == 1:
        axes_c5 = [axes_c5]
    for _ei5, _eu5 in enumerate(_C5_EU):
        _ax5c = axes_c5[_ei5]
        for _ni5c, _n5c in enumerate(nhoods):
            _sub5c = _delta_c5[_delta_c5['Neighbourhood'] == _n5c]
            _vals5c = []
            for _sc5c in _scen_c5:
                _row5c = _sub5c[_sub5c['Scenario'] == _sc5c]
                _vals5c.append(float(_row5c[_eu5].values[0])
                               if not _row5c.empty else 0.0)
            _off5c = (_ni5c - len(nhoods) / 2 + 0.5) * _w_c5
            _ax5c.bar(_xs_c5 + _off5c, _vals5c, _w_c5,
                      color=_OCC_NCLR[_n5c], alpha=0.80,
                      label=_n5c if _ei5 == 0 else "")
        _ax5c.axhline(0, color='black', lw=0.8, ls='--')
        _ax5c.set_title(_eu5, fontweight='bold')
        _ax5c.set_xticks(_xs_c5)
        _ax5c.set_xticklabels(_scen_c5, rotation=30, ha='right', fontsize=8)
        _ax5c.set_ylabel('\u0394 W/m\u00b2 (Weekend \u2212 Weekday)', fontsize=9)
        _ax5c.grid(axis='y', alpha=0.3)
    _h5c, _l5c = axes_c5[0].get_legend_handles_labels()
    fig.legend(_h5c, _l5c, loc='upper center', bbox_to_anchor=(0.5, 1.03),
               ncol=3, fontsize=8)
    fig.suptitle(
        "Figure_Occ_C5 \u2014 Weekday vs Weekend End-Use \u0394 (Weekend \u2212 Weekday)\n"
        "Averaged over Jan+Jul diurnal profile (N=20)",
        fontsize=11, fontweight='bold', y=1.06)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "Figure_Occ_C5_WeekdayWeekend_Delta.png"),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Figure_Occ_C5 done: Figure_Occ_C5_WeekdayWeekend_Delta.png")
else:
    print("Figure_Occ_C5_WkWe_Delta.png SKIPPED: grp_occ empty or required columns missing.")

# ── Figure_Occ_B1: Diurnal load shape ribbon ──
# Design choice: 6 separate PNGs (one per neighbourhood, 1x4 layout).
# A single 24-subplot grid (6 nhoods x 4 conditions) is too dense for the report.
_B1_PANELS = [
    ('Winter', 'Weekday', '(a) Winter Weekday'),
    ('Winter', 'Weekend', '(b) Winter Weekend'),
    ('Summer', 'Weekday', '(c) Summer Weekday'),
    ('Summer', 'Weekend', '(d) Summer Weekend'),
]
_B1_EQUIP_CLR = '#ff7f0e'
_B1_COOL_CLR  = '#1f77b4'
_B1_FILES = []

if not grp_occ.empty and 'Equipment' in grp_occ.columns and 'Cooling' in grp_occ.columns:
    from matplotlib.patches import Patch as _Patch
    for _n_b1 in nhoods:
        fig, axes = plt.subplots(1, 4, figsize=(22, 5), sharey=False)
        _b1_any = False
        for _pidx, (_season_b1, _daycat_b1, _ptitle_b1) in enumerate(_B1_PANELS):
            _ax_b1 = axes[_pidx]
            _ax2_b1 = _ax_b1.twinx()
            _ax_b1.set_zorder(_ax2_b1.get_zorder() + 1)
            _ax_b1.patch.set_visible(False)
            for _sc_b1, _alpha_b1, _lw_b1, _ls_b1 in [
                    ('Default', 0.25, 1.5, ':'),
                    ('2025',    0.55, 2.0, '-')]:
                _sub_b1 = grp_occ[
                    (grp_occ['Neighbourhood'] == _n_b1) &
                    (grp_occ['Scenario'] == _sc_b1) &
                    (grp_occ['Season'] == _season_b1) &
                    (grp_occ['DayCat'] == _daycat_b1)
                ].sort_values('Hour')
                if _sub_b1.empty:
                    continue
                _b1_any = True
                _hrs_b1 = _sub_b1['Hour'].values
                _eq_b1  = _sub_b1['Equipment'].values
                _co_b1  = _sub_b1['Cooling'].values
                _ax_b1.fill_between(_hrs_b1, 0, _eq_b1,
                                    color=_B1_EQUIP_CLR, alpha=_alpha_b1)
                _ax_b1.fill_between(_hrs_b1, _eq_b1, _eq_b1 + _co_b1,
                                    color=_B1_COOL_CLR, alpha=_alpha_b1)
                if 'People' in _sub_b1.columns:
                    _ppl_b1 = _sub_b1['People'].values
                    _pclr_b1 = '#7f7f7f' if _sc_b1 == 'Default' else 'black'
                    _ax2_b1.plot(_hrs_b1, _ppl_b1,
                                 color=_pclr_b1, linestyle=_ls_b1,
                                 linewidth=_lw_b1, alpha=0.85)
            _ax_b1.set_title(_ptitle_b1, fontsize=10, fontweight='bold')
            _ax_b1.set_xlim(0, 23)
            _ax_b1.set_xticks([0, 6, 12, 18, 23])
            _ax_b1.set_xlabel("Hour of Day", fontsize=9)
            _ax_b1.grid(True, alpha=0.2, zorder=0)
            if _pidx == 0:
                _ax_b1.set_ylabel("Load (W/m\u00b2)", fontsize=9)
            if _pidx == 3:
                _ax2_b1.set_ylabel("People heat gain (W/m\u00b2)", fontsize=8)
            else:
                _ax2_b1.set_yticks([])
        _b1_leg = [
            _Patch(facecolor=_B1_EQUIP_CLR, alpha=0.55, label='Equipment (2025)'),
            _Patch(facecolor=_B1_EQUIP_CLR, alpha=0.25, label='Equipment (Default)'),
            _Patch(facecolor=_B1_COOL_CLR,  alpha=0.55, label='Cooling (2025)'),
            _Patch(facecolor=_B1_COOL_CLR,  alpha=0.25, label='Cooling (Default)'),
            plt.Line2D([0], [0], color='black',   lw=2.0, ls='-',  label='People 2025'),
            plt.Line2D([0], [0], color='#7f7f7f', lw=1.5, ls=':', label='People Default'),
        ]
        fig.legend(handles=_b1_leg, loc='upper center',
                   bbox_to_anchor=(0.5, 1.07), ncol=3, fontsize=8)
        fig.suptitle(
            f"Figure_Occ_B1 \u2014 Diurnal Load Shape Ribbon: Default vs 2025\n"
            f"{_n_b1} (N=20, Jan=Winter / Jul=Summer)",
            fontsize=10, fontweight='bold', y=1.12)
        plt.tight_layout()
        _b1_fname = f"Figure_Occ_B1_Diurnal_Ribbon_{_n_b1}.png"
        plt.savefig(os.path.join(OUT, _b1_fname), dpi=150, bbox_inches='tight')
        plt.close()
        _B1_FILES.append(_b1_fname)
        _status_b1 = "done" if _b1_any else "WARNING: no data"
        print(f"Figure_Occ_B1 {_status_b1}: {_b1_fname}")
else:
    print("Figure_Occ_B1 SKIPPED: grp_occ empty or Equipment/Cooling columns missing.")
    _B1_FILES = []

# ── Task 5: Peak-occ extraction (Equipment + DHW peak hours) → Figure_Occ_B2 ──

def _extract_peak_occ(sql_path, neighbourhood=None):
    """Returns dict {key: {peak_Wm2, peak_hour}} for Heating, Cooling, Equipment, DHW.
    Heating/Cooling: SUM across zones at peak TimeIndex.
    Equipment/DHW: building-level meter, single row per timestep.
    peak_hour is 0-based (0=midnight). Returns None on missing SQL or error."""
    if not os.path.exists(sql_path):
        return None
    try:
        conn = sqlite3.connect(sql_path)
        cur = conn.cursor()
        area = _get_area(cur, neighbourhood)
        result = {}
        for _key_pk, _vname_pk in [
                ('Heating', 'Zone Air System Sensible Heating Energy'),
                ('Cooling', 'Zone Air System Sensible Cooling Energy')]:
            ids_df = pd.read_sql_query(
                "SELECT ReportDataDictionaryIndex FROM ReportDataDictionary "
                f"WHERE Name='{_vname_pk}'", conn)
            if ids_df.empty:
                continue
            ids_str = ",".join(map(str, ids_df['ReportDataDictionaryIndex'].tolist()))
            peak_df = pd.read_sql_query(
                f"SELECT rd.TimeIndex, SUM(rd.Value) AS TotalValue "
                f"FROM ReportData rd "
                f"WHERE rd.ReportDataDictionaryIndex IN ({ids_str}) "
                f"GROUP BY rd.TimeIndex ORDER BY TotalValue DESC LIMIT 1", conn)
            if peak_df.empty:
                continue
            _pv = peak_df.iloc[0]['TotalValue']
            _ti = peak_df.iloc[0]['TimeIndex']
            _t_df = pd.read_sql_query(
                f"SELECT Hour FROM Time WHERE TimeIndex={_ti}", conn)
            _h = int(_t_df.iloc[0]['Hour']) - 1
            result[_key_pk] = {'peak_Wm2': float(_pv / 3600.0 / area), 'peak_hour': _h}
        for _key_pk, _vname_pk in [
                ('Equipment', 'InteriorEquipment:Electricity'),
                ('DHW',       'WaterSystems:EnergyTransfer')]:
            cur.execute(
                "SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name=?",
                (_vname_pk,))
            _row_pk = cur.fetchone()
            if not _row_pk:
                print(f"  peak_occ: '{_vname_pk}' not found in "
                      f"{os.path.basename(sql_path)}")
                continue
            _vid_pk = _row_pk[0]
            peak_df = pd.read_sql_query(
                f"SELECT TimeIndex, Value FROM ReportData "
                f"WHERE ReportDataDictionaryIndex={_vid_pk} "
                f"ORDER BY Value DESC LIMIT 1", conn)
            if peak_df.empty:
                continue
            _pv = peak_df.iloc[0]['Value']
            _ti = peak_df.iloc[0]['TimeIndex']
            _t_df = pd.read_sql_query(
                f"SELECT Hour FROM Time WHERE TimeIndex={_ti}", conn)
            _h = int(_t_df.iloc[0]['Hour']) - 1
            result[_key_pk] = {'peak_Wm2': float(_pv / 3600.0 / area), 'peak_hour': _h}
        conn.close()
        return result if result else None
    except Exception as e:
        print(f"WARNING peak_occ: {sql_path} \u2014 {e}")
        return None

scen_pk5 = ["Default", "2005", "2010", "2015", "2022", "2025"]
pk5_records = []
for _n5 in nhoods:
    for _sc5 in scen_pk5:
        if _sc5 == "Default":
            _sql5 = os.path.join(BASE, _n5, "Default", "eplusout.sql")
        else:
            _sql5 = os.path.join(BASE, _n5, "iter_1", _sc5, "eplusout.sql")
        _cache5 = os.path.join(CACHE, f"peak_occ_{_n5}_{_sc5}.json")
        if _cache_fresh(_cache5, _sql5):
            import json as _json5
            with open(_cache5) as _fh5:
                _pk5 = _json5.load(_fh5)
        else:
            _pk5 = _extract_peak_occ(_sql5, neighbourhood=_n5)
            if _pk5:
                import json as _json5
                with open(_cache5, "w") as _fh5:
                    _json5.dump(_pk5, _fh5)
            else:
                _pk5 = None
        if _pk5:
            _rec5 = {'Neighbourhood': _n5, 'Scenario': _sc5}
            for _k5, _v5 in _pk5.items():
                _rec5[f"{_k5}_hour"] = _v5['peak_hour']
                _rec5[f"{_k5}_Wm2"]  = _v5['peak_Wm2']
            pk5_records.append(_rec5)
        else:
            print(f"  peak_occ skip: {_n5}/{_sc5}")
df_pk5 = pd.DataFrame(pk5_records) if pk5_records else pd.DataFrame()

# ── Figure_Occ_B2: Peak Load Time-Shift ──
if (not df_pk5.empty
        and 'Cooling_hour' in df_pk5.columns
        and 'Equipment_hour' in df_pk5.columns):
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()
    for _ni5, _n5 in enumerate(nhoods):
        _ax5 = axes[_ni5]
        _sub5 = df_pk5[df_pk5['Neighbourhood'] == _n5]
        for _, _row5 in _sub5.iterrows():
            _sc5_r = _row5['Scenario']
            _x5 = _row5.get('Cooling_hour', np.nan)
            _y5 = _row5.get('Equipment_hour', np.nan)
            _sz5 = max(60, float(_row5.get('Cooling_Wm2', 1.0)) * 20)
            _ax5.scatter(_x5, _y5, s=_sz5,
                         color=colors.get(_sc5_r, '#aaaaaa'),
                         edgecolors='k', linewidths=0.5, zorder=3,
                         label=_sc5_r)
        _ax5.plot([0, 23], [0, 23], 'k--', lw=0.8, alpha=0.4)
        _ax5.set_xlim(-0.5, 23.5)
        _ax5.set_ylim(-0.5, 23.5)
        _ax5.set_xlabel("Peak Cooling Hour (0\u201323)", fontsize=9)
        _ax5.set_ylabel("Peak Equipment Hour (0\u201323)", fontsize=9)
        _ax5.set_title(_n5, fontweight='bold')
        _ax5.grid(alpha=0.3)
        if _ni5 == 0:
            _ax5.legend(fontsize=7, loc='upper left',
                        title='Scenario', title_fontsize=7)
    fig.suptitle(
        "Figure_Occ_B2 \u2014 Peak Load Time-Shift: Cooling Hour vs Equipment Hour\n"
        "Marker size \u221d peak Cooling magnitude (W/m\u00b2), N=20",
        fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "Figure_Occ_B2_Peak_TimeShift.png"),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Figure_Occ_B2 done: Figure_Occ_B2_Peak_TimeShift.png")
else:
    print("Figure_Occ_B2 SKIPPED: peak_occ data missing or required columns absent.")

# ── Task 6: Monthly end-use stack (B.3) ──
_EU_CLR_B3 = {
    'Heating':   '#d62728',
    'Cooling':   '#1f77b4',
    'Equipment': '#ff7f0e',
    'Lights':    '#bcbd22',
    'DHW':       '#9467bd',
}
_SC_B3 = ['Default', '2025']
_MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_MONTHS_B3 = list(range(1, 13))

if collected_occ:
    _full_b3 = pd.concat(collected_occ, ignore_index=True)
    _eu_b3 = [c for c in ['Heating', 'Cooling', 'Equipment', 'Lights', 'DHW']
               if c in _full_b3.columns]
    _all_b3 = _eu_b3 + (['People'] if 'People' in _full_b3.columns else [])
    _monthly_b3 = (
        _full_b3.groupby(['Neighbourhood', 'Scenario', 'Month'])[_all_b3]
        .sum()
        .reset_index()
    )
    for _col_b3 in _all_b3:
        _monthly_b3[_col_b3] = _monthly_b3[_col_b3] / 1000.0
    # Impute NUS_RC1 Default Jul–Dec from mean of RC2–RC6 Default, scaled by RC1/others Jan–Jun ratio
    _imputed_b3 = set()
    _rc1_def_m = _monthly_b3[(_monthly_b3['Neighbourhood'] == 'NUS_RC1') & (_monthly_b3['Scenario'] == 'Default')]
    _rc1_present = set(_rc1_def_m['Month'].tolist())
    _missing_m_b3 = [m for m in range(1, 13) if m not in _rc1_present]
    if _missing_m_b3:
        _other_n_b3 = [n for n in nhoods if n != 'NUS_RC1']
        _oth_def_b3 = _monthly_b3[(_monthly_b3['Neighbourhood'].isin(_other_n_b3)) & (_monthly_b3['Scenario'] == 'Default')]
        _shared_m = sorted(_rc1_present)
        _rc1_sh_mn = _rc1_def_m[_rc1_def_m['Month'].isin(_shared_m)][_eu_b3].mean()
        _oth_sh_mn = _oth_def_b3[_oth_def_b3['Month'].isin(_shared_m)][_eu_b3].mean()
        _eu_rat_b3 = (_rc1_sh_mn / _oth_sh_mn.replace(0, np.nan)).fillna(1.0)
        _new_b3_rows = []
        for _mm in _missing_m_b3:
            _oth_mm = _oth_def_b3[_oth_def_b3['Month'] == _mm][_eu_b3].mean()
            _nr = {'Neighbourhood': 'NUS_RC1', 'Scenario': 'Default', 'Month': _mm}
            for _eui in _eu_b3:
                _nr[_eui] = float(_oth_mm[_eui] * _eu_rat_b3[_eui])
            if 'People' in _all_b3:
                _rc1_ppl_sh = float(_rc1_def_m[_rc1_def_m['Month'].isin(_shared_m)]['People'].mean())
                _oth_ppl_sh = float(_oth_def_b3[_oth_def_b3['Month'].isin(_shared_m)]['People'].mean())
                _ppl_r = _rc1_ppl_sh / _oth_ppl_sh if _oth_ppl_sh > 0 else 1.0
                _nr['People'] = float(_oth_def_b3[_oth_def_b3['Month'] == _mm]['People'].mean() * _ppl_r)
            _new_b3_rows.append(_nr)
        _monthly_b3 = pd.concat([_monthly_b3, pd.DataFrame(_new_b3_rows)], ignore_index=True)
        _imputed_b3.add(('NUS_RC1', 'Default'))
        print(f"  B3: imputed NUS_RC1 Default months {_missing_m_b3} from RC2-RC6 Default (scaled)")
    fig, axes_b3 = plt.subplots(3, 4, figsize=(22, 14))
    for _ni6, _n6 in enumerate(nhoods):
        for _sci6, _sc6 in enumerate(_SC_B3):
            _ax6 = axes_b3[_ni6 // 2][(_ni6 % 2) * 2 + _sci6]
            _ax2_6 = _ax6.twinx()
            _sub6 = _monthly_b3[
                (_monthly_b3['Neighbourhood'] == _n6) &
                (_monthly_b3['Scenario'] == _sc6)
            ].sort_values('Month')
            _bot6 = np.zeros(12)
            for _eu6 in _eu_b3:
                _vals6 = []
                for _m6 in _MONTHS_B3:
                    _mask6 = _sub6['Month'] == _m6
                    _vals6.append(
                        float(_sub6.loc[_mask6, _eu6].values[0])
                        if _mask6.any() else 0.0)
                _ax6.bar(_MONTHS_B3, _vals6, bottom=_bot6,
                         color=_EU_CLR_B3.get(_eu6, '#cccccc'), alpha=0.85,
                         label=_eu6 if (_ni6 == 0 and _sci6 == 0) else "")
                _bot6 = _bot6 + np.array(_vals6)
            if 'People' in _sub6.columns:
                _ppl6 = []
                for _m6 in _MONTHS_B3:
                    _mask6 = _sub6['Month'] == _m6
                    _ppl6.append(
                        float(_sub6.loc[_mask6, 'People'].values[0])
                        if _mask6.any() else 0.0)
                _ax2_6.plot(_MONTHS_B3, _ppl6, 'k-o', lw=1.5, ms=4, alpha=0.7)
                if _sci6 == 1:
                    _ax2_6.set_ylabel('People\n(kWh/m\u00b2)', fontsize=7)
                else:
                    _ax2_6.set_yticks([])
            else:
                _ax2_6.set_yticks([])
            _ax6.set_title(f"{_n6} \u2014 {_sc6}", fontsize=9, fontweight='bold')
            _ax6.set_xticks(_MONTHS_B3)
            _ax6.set_xticklabels(_MONTH_LABELS, fontsize=7, rotation=45)
            _ax6.set_ylabel('kWh/m\u00b2', fontsize=8)
            _ax6.grid(axis='y', alpha=0.3)
    for _ni6 in range(len(nhoods)):
        _ri6 = _ni6 // 2
        _ci6_base = (_ni6 % 2) * 2
        _ymax6 = max(axes_b3[_ri6][_ci6_base].get_ylim()[1],
                     axes_b3[_ri6][_ci6_base + 1].get_ylim()[1])
        for _sci6 in range(2):
            axes_b3[_ri6][_ci6_base + _sci6].set_ylim(0, _ymax6)
    # Annotate still-incomplete panels (< 12 months after imputation)
    _mcount_b3 = (_monthly_b3.groupby(['Neighbourhood', 'Scenario'])['Month']
                  .nunique().reset_index(name='n_months'))
    for _, _mr in _mcount_b3.iterrows():
        if _mr['n_months'] >= 12 or _mr['Scenario'] not in _SC_B3:
            continue
        _mni = list(nhoods).index(_mr['Neighbourhood'])
        _msc = _SC_B3.index(_mr['Scenario'])
        _ann_ax = axes_b3[_mni // 2][(_mni % 2) * 2 + _msc]
        _ann_ax.set_facecolor('#fff4ee')
        _ann_ax.text(0.97, 0.97, "Jan\u2013Jun only (incomplete sim.)",
                     transform=_ann_ax.transAxes, ha='right', va='top',
                     fontsize=7, color='#cc4400', style='italic', zorder=5)
    # Annotate imputed panels
    for (_imp_n, _imp_sc) in _imputed_b3:
        if _imp_sc not in _SC_B3:
            continue
        _imp_ni = list(nhoods).index(_imp_n)
        _imp_si = _SC_B3.index(_imp_sc)
        _ann_ax2 = axes_b3[_imp_ni // 2][(_imp_ni % 2) * 2 + _imp_si]
        _ann_ax2.text(0.97, 0.97, "Jul\u2013Dec: imputed from neighbours",
                      transform=_ann_ax2.transAxes, ha='right', va='top',
                      fontsize=7, color='#555555', style='italic', zorder=5)
    _h6, _l6 = axes_b3[0][0].get_legend_handles_labels()
    fig.legend(_h6, _l6, loc='upper center',
               bbox_to_anchor=(0.5, 1.005), ncol=5, fontsize=9)
    fig.suptitle(
        "Figure_Occ_B3 \u2014 Monthly End-Use Stack: Default vs 2025 (N=20)\n"
        "Black line = monthly People heat-gain proxy (right axis, kWh/m\u00b2)",
        fontsize=11, fontweight='bold', y=1.01)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(os.path.join(OUT, "Figure_Occ_B3_Monthly_Stack.png"),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Figure_Occ_B3 done: Figure_Occ_B3_Monthly_Stack.png")
else:
    print("Figure_Occ_B3 SKIPPED: collected_occ empty.")

# ── Text summary ──
_batch_name = os.path.basename(BASE)
lines = [
    f"INTERIM BATCH MC REPORT — {_batch_name}",
    "="*60,
    f"Batch dir: {BASE}",
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

lines.append("\nFigures saved to: " + OUT)
for f in [
    "fig1_total_eui_by_scenario.png", "fig2_stacked_enduse.png",
    "fig3_heating_cooling.png", "fig4_improvement_vs_2005.png", "fig5_heatmap.png",
    "Figure_4.3.1_Energy_Demand.png", "Figure_4.3.2_Temporal_Trend.png",
    "Figure_4.3.3_Diurnal_Profiles.png", "Figure_4.3.4_Peak_Loads.png",
    "Figure_Occ_A1_EndUse_Delta.png", "Figure_Occ_A2_Radar_Fingerprint.png",
    "Figure_Occ_A3_Sensitivity_Tornado.png", "Figure_Occ_A4_Coupling_Scatter.png",
    "Figure_Occ_B4_Waterfall.png",
    "Figure_Occ_B2_Peak_TimeShift.png",
    "Figure_Occ_B3_Monthly_Stack.png",
    "Figure_Occ_C5_WeekdayWeekend_Delta.png",
] + [f"Figure_Occ_B1_Diurnal_Ribbon_{_n}.png" for _n in nhoods]:
    lines.append("  " + f)

summary = "\n".join(lines)
with open(os.path.join(OUT, "interim_summary.txt"), "w") as fh:
    fh.write(summary)
print(summary)
