"""
Figures 7 and 9 redrawn to show the 2022 to 2030 CHANGE (main scenario) instead of side-by-side levels,
which looked identical at full scale (author request 2026-09-28). Plotting only; nothing is recomputed.

Sources (both already accepted, plan log (ds)):
  impl/T79_in/t68_enduse_change_2022_2030.csv   stock-weighted rows: percent change and 95 % CI per meter,
                                                 absolute-fraction change and CI for load factor, midday share
  impl/T71_out/fig02_annual_by_enduse.csv        stock-weighted 2022 whole-building levels (row labels)
  impl/T71_out/fig04_peak_loadfactor_ramp_ci.csv peak and evening-ramp levels (point estimates, no CI)

Writes (same names the manuscript embeds): T94_out/fig03_annual_by_enduse.{png,pdf} (Figure 7) and
T94_out/fig05_peak_loadfactor_ramp.{png,pdf} (Figure 9), plus T94_out/t94_fig7_fig9_values.json.
Run from impl/:  py T94_scripts/t94_fig7_fig9_change.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.dirname(HERE)
OUT = os.path.join(IMPL, "T94_out")
DPI = 600
W_IN = 7.0
UP, DOWN, FLAT = "#DD8452", "#4C72B0", "#8C8C8C"
VALUES = {}

LABEL = {
    "elec_facility_kWh": "Whole building (total)",
    "lights_kWh": "Interior lighting",
    "equip_kWh": "Interior equipment",
    "fan_kWh": "Fans",
    "heating_ET_kWh": "Heating (energy transfer)",
    "cooling_ET_kWh": "Cooling (energy transfer)",
    "water_ET_kWh": "Water systems (energy transfer)",
    "hvac_dhw_elec_kWh": "HVAC and hot-water electricity",
}
ORDER = ["elec_facility_kWh", "lights_kWh", "equip_kWh", "fan_kWh",
         "heating_ET_kWh", "cooling_ET_kWh", "water_ET_kWh", "hvac_dhw_elec_kWh"]


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=DPI, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def colour(v, lo, hi):
    if lo > 0:
        return UP
    if hi < 0:
        return DOWN
    return FLAT


chg = pd.read_csv(os.path.join(IMPL, "T79_in", "t68_enduse_change_2022_2030.csv"))
sw = chg[chg["level"] == "stock_weighted"].set_index("metric_ann_col")
assert len(sw) == 10, len(sw)


# ---- Figure 7: percent change by end use, 95 % CI ----
def fig7():
    lev = pd.read_csv(os.path.join(IMPL, "T71_out", "fig02_annual_by_enduse.csv"))
    lev22 = {r["ann_col"]: float(r["stock_weighted_whole_building_kWh"])
             for _, r in lev.iterrows() if int(r["year"]) == 2022}
    rows = []
    for c in ORDER:
        r = sw.loc[c]
        assert r["change_type"] == "percent", c
        rows.append((c, float(r["point_change_pct"]), float(r["ci_low_pct"]), float(r["ci_high_pct"]), lev22[c]))
    VALUES["fig7"] = [{"meter": c, "change_pct": v, "ci_low_pct": lo, "ci_high_pct": hi, "level_2022_kWh": l}
                      for c, v, lo, hi, l in rows]

    fig, ax = plt.subplots(figsize=(W_IN, 4.6))
    ys = list(range(len(rows)))[::-1]
    ys = [y + (0.6 if i == 0 else 0) for i, y in enumerate(ys)]  # small gap under the total
    for (c, v, lo, hi, l), y in zip(rows, ys):
        col = colour(v, lo, hi)
        ax.barh(y, v, height=0.62, color=col, alpha=0.9 if c != "elec_facility_kWh" else 1.0,
                edgecolor="black" if c == "elec_facility_kWh" else "none", linewidth=0.8)
        ax.errorbar(v, y, xerr=[[v - lo], [hi - v]], fmt="none", ecolor="black", elinewidth=0.9, capsize=3)
        txt = "{:+.2f} %".format(v)
        x_txt = hi + 0.03 if v >= 0 else lo - 0.03
        ax.text(x_txt, y, txt, va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
    ax.set_yticks(ys)
    ax.set_yticklabels(["{}\n{:,.0f} kWh in 2022".format(LABEL[c], l) for c, _, _, _, l in rows], fontsize=8.5)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlim(-0.75, 1.0)
    ax.set_xlabel("Change in annual energy, 2022 to 2030 (%),\nwith 95 % confidence interval")
    ax.grid(axis="x", alpha=0.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "fig03_annual_by_enduse")


# ---- Figure 9: size of demand (peak, ramp) and shape of demand (load factor, midday share) ----
def fig9():
    pk = pd.read_csv(os.path.join(IMPL, "T71_out", "fig04_peak_loadfactor_ramp_ci.csv")).set_index("metric")
    size = []
    for key, name in (("peak_kW_annual", "Peak demand"), ("evening_ramp_kW_mean", "Evening ramp\n(14:00 to 17:00)")):
        a, b = float(pk.loc[key, "value_2022"]), float(pk.loc[key, "value_2030"])
        size.append((name, a, b, 100.0 * (b - a) / a))
    shape = []
    for key, name in (("load_factor", "Load factor"), ("midday_share", "Midday share\n(09:00 to 17:00)")):
        r = sw.loc[key]
        assert r["change_type"] == "absolute_fraction", key
        shape.append((name, 100 * float(r["point_change_pct"]), 100 * float(r["ci_low_pct"]),
                      100 * float(r["ci_high_pct"])))
    VALUES["fig9"] = {"size": [{"metric": n, "value_2022_kW": a, "value_2030_kW": b, "change_pct": p}
                               for n, a, b, p in size],
                      "shape": [{"metric": n, "change_pp": v, "ci_low_pp": lo, "ci_high_pp": hi}
                                for n, v, lo, hi in shape]}

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W_IN, 2.9), gridspec_kw={"wspace": 0.95})
    ys = [1, 0]
    for (n, a, b, p), y in zip(size, ys):
        a1.barh(y, p, height=0.55, color=DOWN if p < 0 else UP)
        a1.text(p - 0.06 if p < 0 else p + 0.06, y, "{:+.2f} %".format(p), va="center",
                ha="right" if p < 0 else "left", fontsize=8.5)
    a1.set_yticks(ys)
    a1.set_yticklabels(["{}\n{:.2f} to {:.2f} kW".format(n, a, b) for n, a, b, _ in size], fontsize=8.5)
    a1.axvline(0, color="black", linewidth=0.8)
    a1.set_xlim(-3.0, 0.5)
    a1.set_xlabel("Change, 2022 to 2030 (%)", fontsize=8.5)
    a1.set_title("(a) Size of demand", fontsize=9.5)
    for (n, v, lo, hi), y in zip(shape, ys):
        a2.barh(y, v, height=0.55, color=UP if lo > 0 else (DOWN if hi < 0 else FLAT))
        a2.errorbar(v, y, xerr=[[v - lo], [hi - v]], fmt="none", ecolor="black", elinewidth=0.9, capsize=3)
        a2.text(hi + 0.04, y, "{:+.2f}".format(v), va="center", ha="left", fontsize=8.5)
    a2.set_yticks(ys)
    a2.set_yticklabels([n for n, _, _, _ in shape], fontsize=8.5)
    a2.axvline(0, color="black", linewidth=0.8)
    a2.set_xlim(-0.1, 1.15)
    a2.set_xlabel("Change, 2022 to 2030\n(percentage points), with\n95 % confidence interval", fontsize=8.5)
    a2.set_title("(b) Shape of demand", fontsize=9.5)
    for ax in (a1, a2):
        ax.grid(axis="x", alpha=0.3)
        ax.tick_params(axis="x", labelsize=8)
        ax.set_ylim(-0.6, 1.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    save(fig, "fig05_peak_loadfactor_ramp")


if __name__ == "__main__":
    fig7()
    fig9()
    with open(os.path.join(OUT, "t94_fig7_fig9_values.json"), "w") as fh:
        json.dump(VALUES, fh, indent=1)
    print(json.dumps(VALUES, indent=1))
