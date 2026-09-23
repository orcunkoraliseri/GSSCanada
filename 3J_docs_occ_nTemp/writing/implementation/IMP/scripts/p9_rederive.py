#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P9 number-sheet re-derivation script.

Reads ONLY the frozen deliverable paths:
  Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/*.csv
  Leg3_4-split/Step9_docs/outputs_step9_deliverable/*.csv, step9_gates.json

Never the superseded agg/ or outputs_step9/ arms.

Run:  PYTHONIOENCODING=utf-8 py -3 writing/implementation/IMP/scripts/p9_rederive.py
(from the 3J_docs_occ_nTemp directory)
"""
import json
import os
import sys

import pandas as pd
import numpy as np

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
S8 = os.path.join(BASE, "Leg3_4-split", "Step8_docs", "outputs_step8", "agg_deliverable")
S9 = os.path.join(BASE, "Leg3_4-split", "Step9_docs", "outputs_step9_deliverable")

def hr(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

def pct(x):
    return f"{x:.2f}%"

# ---------------------------------------------------------------------------
hr("LOAD FILES")
eui = pd.read_csv(os.path.join(S9, "step9_eui_by_channel.csv"))
long_ = pd.read_csv(os.path.join(S9, "step9_longitudinal.csv"))
peaks = pd.read_csv(os.path.join(S9, "step9_loadshape_peaks.csv"))
scen = pd.read_csv(os.path.join(S9, "step9_scenario_response.csv"))
meta = pd.read_csv(os.path.join(S8, "agg_meta.csv"))
with open(os.path.join(S9, "step9_gates.json"), encoding="utf-8") as f:
    gates = json.load(f)
print("eui_by_channel:", eui.shape)
print("longitudinal:", long_.shape)
print("loadshape_peaks:", peaks.shape)
print("scenario_response:", scen.shape)
print("agg_meta:", meta.shape)
print("gates:", len(gates))

# ---------------------------------------------------------------------------
hr("GATE SCORECARD (step9_gates.json)")
statuses = [g["status"] for g in gates]
from collections import Counter
c = Counter(statuses)
print("Scorecard:", dict(c), "over", len(gates), "gates")

# ---------------------------------------------------------------------------
hr("TABLE 3 / SEC 4.1 -- TOWER AREAS (agg_meta.csv, total_building_area_m2)")
for bld in ["SuperTall", "Tall"]:
    vals = meta.loc[meta["building"] == bld, "total_building_area_m2"].unique()
    print(bld, "unique total_building_area_m2 values:", vals)

# ---------------------------------------------------------------------------
hr("TABLE 5 / ABSTRACT / SEC 5.2 -- PER-CHANNEL EUI BAND VERDICTS (step9_eui_by_channel.csv, 224 rows = 56 cells x 4 channels)")
print("rows:", len(eui), "| unique channels:", sorted(eui['channel'].unique()))
for ch in ["office", "retail", "hotel", "residential"]:
    sub = eui[eui["channel"] == ch]
    cfa = sub["eui_CFA_kWh_m2"]
    gfa = sub["eui_GFAshare_kWh_m2"]
    print(f"\n-- {ch} (n={len(sub)}) --")
    print(f"  CFA basis:  median={cfa.median():.2f}  range=[{cfa.min():.2f}, {cfa.max():.2f}]")
    print(f"  GFA-share:  median={gfa.median():.2f}  range=[{gfa.min():.2f}, {gfa.max():.2f}]")
    if "verdict_asmodelled" in sub.columns and sub["verdict_asmodelled"].notna().any():
        vc = sub["verdict_asmodelled"].value_counts().to_dict()
        print(f"  verdict_asmodelled counts: {vc}")
    if "info_verdict" in sub.columns:
        ivc = sub["info_verdict"].value_counts().to_dict()
        print(f"  info_verdict counts: {ivc}")
    if ch in ("office", "retail", "hotel"):
        lo = sub["band_lo"].iloc[0]
        hi = sub["band_hi"].iloc[0]
        n_in = ((cfa >= lo) & (cfa <= hi)).sum()
        n_below = (cfa < lo).sum()
        n_above = (cfa > hi).sum()
        print(f"  band_lo={lo}, band_hi={hi} | all-cells count: {n_in}/{len(sub)} in band, "
              f"{n_below} below floor, {n_above} above ceiling")
        gap_pct_floor = (lo - cfa.median()) / lo * 100
        print(f"  median-vs-floor gap: (floor {lo} - median {cfa.median():.4f}) / floor = {gap_pct_floor:.4f}%")

# Office control (Default_NECB uninjected scenario) -- check eui_by_channel for that scenario tag
hr("OFFICE UNINJECTED CONTROL (Default_NECB) -- 85.45 kWh/m2/yr claim")
print("scenario values present in step9_eui_by_channel.csv:", sorted(eui['scenario'].unique()))
if "Default_NECB" in eui["scenario"].unique():
    ctrl = eui[(eui["scenario"] == "Default_NECB") & (eui["channel"] == "office")]
    print(ctrl[["cell_tag", "channel", "eui_CFA_kWh_m2"]])
    if len(ctrl):
        print("median:", ctrl["eui_CFA_kWh_m2"].median())
else:
    print("Default_NECB not found as a 'channel' row in step9_eui_by_channel.csv (channel EUI table "
          "only carries injected/office/retail/hotel/residential rows per cell -- control value must be "
          "traced via agg_deliverable/agg_annual_by_channel.csv on the Default_NECB scenario instead).")
    ann_ch = pd.read_csv(os.path.join(S8, "agg_deliverable", "agg_annual_by_channel.csv"))
    print("agg_annual_by_channel scenarios:", sorted(ann_ch['cell_tag'].str.extract(r'^([^_]+(?:_[A-Za-z]+)?)__')[0].dropna().unique())[:20])

# ---------------------------------------------------------------------------
hr("HOTEL BIMODAL GAP -- 84.64 kWh/m2/yr, 70.5% of band width, two clusters")
hotel = eui[eui["channel"] == "hotel"].sort_values("eui_CFA_kWh_m2")
vals = hotel["eui_CFA_kWh_m2"].values
diffs = np.diff(vals)
imax = int(np.argmax(diffs))
gap = diffs[imax]
low_cluster = vals[: imax + 1]
high_cluster = vals[imax + 1 :]
band_lo = hotel["band_lo"].iloc[0]
band_hi = hotel["band_hi"].iloc[0]
band_width = band_hi - band_lo
print(f"n={len(vals)}  low cluster n={len(low_cluster)} range=[{low_cluster.min():.2f},{low_cluster.max():.2f}]"
      f"  high cluster n={len(high_cluster)} range=[{high_cluster.min():.2f},{high_cluster.max():.2f}]")
print(f"largest consecutive gap = {gap:.4f} kWh/m2/yr")
print(f"band width = {band_hi} - {band_lo} = {band_width}")
print(f"gap / band_width = {gap/band_width*100:.2f}%")
print(f"ceiling {band_hi} inside gap? {low_cluster.max() < band_hi < high_cluster.min()}")
n_below_ceiling = (vals <= band_hi).sum()
n_above_ceiling = (vals > band_hi).sum()
print(f"cells <= ceiling: {n_below_ceiling}, cells > ceiling: {n_above_ceiling}")

# Discussion Ch6 clusters: "28 cells at 203.33 to 218.22 kWh/m2/yr" / "28 at 302.86 to 318.42"
print(f"low cluster reported bound check: {low_cluster.min():.2f} to {low_cluster.max():.2f} "
      f"(Discussion claims 203.33 to 218.22)")
print(f"high cluster reported bound check: {high_cluster.min():.2f} to {high_cluster.max():.2f} "
      f"(Discussion claims 302.86 to 318.42)")

# ---------------------------------------------------------------------------
hr("RETAIL MEDIAN-TO-FLOOR GAP -- 5.47% below 80 floor")
retail = eui[eui["channel"] == "retail"]
med = retail["eui_CFA_kWh_m2"].median()
floor = retail["band_lo"].iloc[0]
print(f"median = {med:.4f}, floor = {floor}, gap = (floor-median)/floor = {(floor-med)/floor*100:.4f}%")
n_in = ((retail["eui_CFA_kWh_m2"] >= floor) & (retail["eui_CFA_kWh_m2"] <= retail["band_hi"].iloc[0])).sum()
n_below = (retail["eui_CFA_kWh_m2"] < floor).sum()
print(f"all-cells count: {n_in} in band, {n_below} below floor, out of {len(retail)}")

# ---------------------------------------------------------------------------
hr("SEC 5.1 / TABLE7-L14 CROSS-CHECK -- LONGITUDINAL PER-CHANNEL PER-CYCLE MEDIAN EUI")
print("longitudinal scenario values:", sorted(long_['scenario'].unique()))
print("longitudinal channels:", sorted(long_['channel'].unique()))
cyc_map = {"Y2005": 2005, "Y2010": 2010, "Y2015": 2015, "Y2022": 2022}
for ch in ["office", "retail", "residential", "hotel"]:
    print(f"\n-- {ch} --")
    base_med = None
    for scen_tag, yr in cyc_map.items():
        sub = long_[(long_["scenario"] == scen_tag) & (long_["channel"] == ch)]
        if len(sub) == 0:
            print(f"  {yr}: no rows for scenario={scen_tag}")
            continue
        m = sub["eui_CFA_kWh_m2"].median()
        if base_med is None:
            base_med = m
        pctchg = (m - base_med) / base_med * 100
        rng_pct = None
        if "energy_pct_vs_2005" in sub.columns:
            rng_pct = (sub["energy_pct_vs_2005"].min(), sub["energy_pct_vs_2005"].max())
        print(f"  {yr} (n={len(sub)}): median EUI={m:.4f}  pct_vs_2005(from median)={pctchg:+.4f}%  "
              f"energy_pct_vs_2005 per-cell range={rng_pct}")

# ---------------------------------------------------------------------------
hr("SEC 5.1 -- ENERGY SHARE vs AREA SHARE, AGGREGATED ACROSS ALL 4 CYCLES x 4 CELLS (64 rows total, 16 per channel)")
for ch in ["hotel", "office", "residential", "retail"]:
    sub = long_[long_["channel"] == ch]
    if "energy_share_pct" in sub.columns and "area_share_pct" in sub.columns:
        e_med = sub["energy_share_pct"].median()
        a_med = sub["area_share_pct"].median()
        print(f"{ch}: n={len(sub)}  median energy_share_pct={e_med:.4f}  median area_share_pct={a_med:.4f}  "
              f"delta(energy-area)={e_med-a_med:+.4f} pp")
    else:
        print(f"{ch}: energy_share_pct/area_share_pct columns not found in step9_longitudinal.csv")

# ---------------------------------------------------------------------------
hr("SEC 5.3 -- PEAK HOURS (circular mean, per channel, B_central scenario, per building-city cell)")
bc = peaks[peaks["scenario"] == "B_central"]
print("channels present in B_central rows:", sorted(bc["channel"].dropna().unique()))
for ch in ["office", "residential", "retail", "hotel"]:
    sub = bc[bc["channel"] == ch]
    col = "wd_peak_hour_circular"
    if col in sub.columns and sub[col].notna().any():
        vals = sub[col].dropna()
        print(f"{ch}: n={len(vals)}  median={vals.median():.4f}  range=[{vals.min():.4f}, {vals.max():.4f}]")
    else:
        print(f"{ch}: no {col} data")

print("\nWhole-building peak (_BUILDING rows), peak_hour_circular:")
bld = bc[bc["channel"] == "_BUILDING"]
col = "peak_hour_circular"
vals = bld[col].dropna()
print(f"n={len(vals)}  median={vals.median():.4f}  range=[{vals.min():.4f}, {vals.max():.4f}]")

# ---------------------------------------------------------------------------
hr("SEC 5.3 -- WEEKDAY MIDDAY vs NIGHT DEMAND, PER CHANNEL (B_central)")
for ch in ["retail", "office", "residential", "hotel"]:
    sub = bc[bc["channel"] == ch]
    if "wd_midday_kW" in sub.columns and "wd_night_kW" in sub.columns:
        mid = sub["wd_midday_kW"].median()
        night = sub["wd_night_kW"].median()
        ratio = mid / night if night else float("nan")
        print(f"{ch}: median wd_midday_kW={mid:.2f}  median wd_night_kW={night:.2f}  ratio={ratio:.2f}:1")

# ---------------------------------------------------------------------------
hr("SEC 5.3 / DISCUSSION -- COINCIDENCE FACTOR (whole building, all 4 cells, B_central)")
cf = bld["coincidence_factor"].dropna() if "coincidence_factor" in bld.columns else pd.Series(dtype=float)
print(f"n={len(cf)}  median={cf.median():.4f}  min={cf.min():.4f}")
print(cf.to_string())
# identify which cell has the min (Tall, Calgary claim)
if len(cf):
    idxmin = bld.loc[cf.idxmin(), "cell_tag"]
    print("cell with minimum coincidence factor:", idxmin)

# ---------------------------------------------------------------------------
hr("SEC 5.4 -- SCENARIO SENSITIVITY (step9_scenario_response.csv, energy_pct_vs_Bcentral)")
print("scenario tags present:", sorted(scen["scenario"].unique()))
lever_map = {
    "office": ["sens_office_cons", "sens_office_opt"],
    "retail": ["sens_retail_cons", "sens_retail_opt"],
    "hotel": ["sens_hotel_cons", "sens_hotel_opt"],
}
for ch, sc_tags in lever_map.items():
    print(f"\n-- own-lever effect on {ch} --")
    for tag in sc_tags:
        sub = scen[(scen["scenario"] == tag) & (scen["channel"] == ch)]
        if len(sub):
            v = sub["energy_pct_vs_Bcentral"]
            print(f"  {tag}: n={len(sub)}  range=[{v.min():.4f}%, {v.max():.4f}%]")
        else:
            print(f"  {tag}: NOT FOUND for channel {ch}")

print("\n-- cross-effect on other channels (conservative draws only, matches prose) --")
for driver, tag in [("office", "sens_office_cons"), ("retail", "sens_retail_cons"), ("hotel", "sens_hotel_cons")]:
    for other in ["office", "retail", "hotel", "residential"]:
        if other == driver:
            continue
        sub = scen[(scen["scenario"] == tag) & (scen["channel"] == other)]
        if len(sub):
            v = sub["energy_pct_vs_Bcentral"]
            print(f"  under {tag}: {other} range=[{v.min():.4f}%, {v.max():.4f}%]")

print("\n-- residential under office-coupled scenarios --")
for tag in ["sens_office_cons", "sens_office_opt"]:
    sub = scen[(scen["scenario"] == tag) & (scen["channel"] == "residential")]
    if len(sub):
        v = sub["energy_pct_vs_Bcentral"]
        print(f"  {tag}: residential range=[{v.min():.4f}%, {v.max():.4f}%]")

print("\n-- outer 2030 bundles (B_cons / B_opt) vs B_central --")
for ch in ["office", "retail", "hotel"]:
    for tag in ["B_cons", "B_opt"]:
        sub = scen[(scen["scenario"] == tag) & (scen["channel"] == ch)]
        if len(sub):
            v = sub["energy_pct_vs_Bcentral"]
            print(f"  {ch} {tag}: range=[{v.min():.4f}%, {v.max():.4f}%]")

print("\nDone.")
