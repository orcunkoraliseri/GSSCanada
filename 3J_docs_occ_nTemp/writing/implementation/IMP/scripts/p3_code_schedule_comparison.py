#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P3 -- code-schedule (uninjected Default_NECB) vs survey-driven (Y2022, B_central) comparison.

READ-ONLY on the frozen deliverable (V2-G1). Writes only under writing/implementation/IMP/
and writing/figures/ (figure-data CSVs).

Definitions are the SAME as the Step-9 script (3rdJ_09_activityDrivenLoads_4split.py):
  * weekday peak hour = load-weighted circular mean of the weekday (WD), season 'all',
    metric == 'energy_W' diurnal profile in agg_diurnal.csv (Step-9 build_loadshape L330-346);
    argmax of the same profile also reported.
  * whole-building peak hour (published) = agg_peak.csv row channel == '_BUILDING'
    (daytype 'all', energy_W), column peak_hour_circular (Step-8E build_peak L447-451).
  * coincidence factor (published) = agg_peak.csv column coincidence_factor
    = max_t(sum of 6 channel hourly energies) / sum_c max_t(channel c) -- the 6 channels are
    office, retail, hotel, residential, residential_common, service_MEP (8E L66, L452-455).
  * midday/night (published) = mean WD W over hours 11-14 / mean over hours 22-23 and 0-4
    (Step-9 L347-348).
  * day/night (new, stated) = mean WD W over hours 08-17 (08:00-18:00) / mean over the other
    14 hours.
  * EUI = step9_eui_by_channel.csv eui_CFA_kWh_m2 and eui_GFAshare_kWh_m2.

Controls first, then negative controls, then the comparison.
Run: PYTHONIOENCODING=utf-8 py -3 p3_code_schedule_comparison.py [--arm P10R]
  --arm P10R (added 2026-09-25): reads agg_P10R / outputs_step9_P10R / campaign_local_P10R, writes to
  IMP/data/P10R/ and writing/figures/_P10R_figdata/ (never the frozen-arm outputs). Control 2 then
  compares the NEW arm with the PUBLISHED numbers, so it is reported as bucket "published_vs_new"
  (INFO: a difference is the P10R effect, not a reader defect). Negative controls N1-N4 compare with
  the new arm's own correct values, and N4 reads the frozen agg_deliverable as the wrong input.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))          # 3J_docs_occ_nTemp
LEG3 = os.path.join(J3, "Leg3_4-split")
ARM = "P10R" if "--arm" in sys.argv and sys.argv[sys.argv.index("--arm") + 1] == "P10R" else "deliverable"
if ARM == "P10R":
    AGG = os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_P10R")
    AGG_SUPERSEDED = os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_deliverable")  # N4: frozen arm = wrong input
    S9 = os.path.join(LEG3, "Step9_docs", "outputs_step9_P10R")
    CELLS = os.path.join(LEG3, "Step8_docs", "campaign_local_P10R")
    OUT = os.path.join(J3, "writing", "implementation", "IMP", "data", "P10R")
    FIGDATA = os.path.join(J3, "writing", "figures", "_P10R_figdata")
    PUB_BUCKET = "published_vs_new"
else:
    AGG = os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_deliverable")
    AGG_SUPERSEDED = os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg")    # negative control only
    S9 = os.path.join(LEG3, "Step9_docs", "outputs_step9_deliverable")
    CELLS = os.path.join(LEG3, "Step8_docs", "campaign_local_deliverable")
    OUT = os.path.join(J3, "writing", "implementation", "IMP", "data")
    FIGDATA = os.path.join(J3, "writing", "figures")
    PUB_BUCKET = "controls"
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIGDATA, exist_ok=True)
print(f"[arm] {ARM}: AGG={AGG} | S9={S9} | CELLS={CELLS} | OUT={OUT} | FIGDATA={FIGDATA}")

TENANT = ["office", "retail", "hotel", "residential"]
CH6 = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]
SCEN = ["Default_NECB", "Y2022", "B_central"]
BLD_CITY = [("SuperTall", "MTL"), ("SuperTall", "CLG"), ("Tall", "MTL"), ("Tall", "CLG")]
DAY_H = list(range(8, 18))                       # 08:00-18:00
NIGHT_H = [h for h in range(24) if h not in DAY_H]

RESULTS = {"controls": [], "negative_controls": [], "published_vs_new": []}


def circ(profile) -> float:
    """Identical to Step-9 circular_mean_hour (L215-221)."""
    w = np.asarray(profile, dtype=float)
    if not np.isfinite(w).any() or w.sum() <= 0:
        return float("nan")
    ang = 2 * np.pi * np.arange(len(w)) / len(w)
    m = np.arctan2(float((w * np.sin(ang)).sum()), float((w * np.cos(ang)).sum()))
    return float((m % (2 * np.pi)) / (2 * np.pi) * len(w))


def resultant(profile) -> float:
    w = np.asarray(profile, dtype=float)
    ang = 2 * np.pi * np.arange(len(w)) / len(w)
    return float(np.hypot((w * np.sin(ang)).sum(), (w * np.cos(ang)).sum()) / w.sum())


def load(agg_dir):
    return {k: pd.read_csv(os.path.join(agg_dir, f"agg_{k}.csv"))
            for k in ("peak", "diurnal", "meta", "annual_by_channel")}


def wd_profile(diur, cell, ch, metric="energy_W", daytype="WD", use_filter=True):
    d = diur[(diur["cell_tag"] == cell) & (diur["channel"] == ch) & (diur["season"] == "all")
             & (diur["daytype"] == daytype)]
    if use_filter:
        d = d[d["metric"] == metric]
    return d.sort_values("hour")["W"].to_numpy()[:24]


def check(bucket, name, got, want, tol):
    ok = bool(np.isfinite(got) and abs(got - want) <= tol)
    RESULTS[bucket].append(dict(check=name, got=round(float(got), 6), want=want, tol=tol,
                                verdict="PASS" if ok else "FAIL"))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {got:.6f} want {want} (tol {tol})")
    return ok


# --------------------------------------------------------------------------------------
# Hourly reconstruction of per-channel energy (Step-8E aggregate_cell L227-259, verbatim logic)
# --------------------------------------------------------------------------------------
END_USES = [
    ("InteriorLights:Electricity", "direct:lights"),
    ("InteriorEquipment:Electricity", "direct:equip"),
    ("InteriorEquipment:NaturalGas", "direct:gasequip"),
    ("WaterSystems:Electricity", "dhw"), ("WaterSystems:NaturalGas", "dhw"),
    ("Cooling:Electricity", "cool"), ("Heating:Electricity", "heat"),
    ("Heating:NaturalGas", "heat"), ("Fans:Electricity", "hvac"),
    ("Pumps:Electricity", "hvac"), ("HeatRejection:Electricity", "cool"),
    ("HeatRecovery:Electricity", "hvac"),
]


def _shares(m, fallback):
    m = np.abs(m)
    tot = m.sum(axis=1)
    out = np.zeros_like(m)
    nz = tot > 0
    out[nz] = m[nz] / tot[nz][:, None]
    out[~nz] = fallback
    return out


def hourly_channels(cell, meta, break_fallback=False, swap_basis=False):
    d = os.path.join(CELLS, cell)
    hourly = pd.read_csv(os.path.join(d, "hourly_meters.csv"))
    chan = pd.read_csv(os.path.join(d, "channel_hourly.csv"))
    dhw = pd.read_csv(os.path.join(d, "dhw_hourly.csv"))
    mm = meta.set_index("cell_tag").loc[cell]
    area = np.array([mm[f"area_{c}_m2"] for c in CH6], float)
    fb = area / area.sum()
    if break_fallback:                      # negative control: wrong fallback basis
        fb = np.full(len(CH6), 1.0 / len(CH6))
    basis = {
        "cool": _shares(chan[[f"{c}_syscool" for c in CH6]].to_numpy(float), fb),
        "heat": _shares(chan[[f"{c}_sysheat" for c in CH6]].to_numpy(float), fb),
        "hvac": _shares(np.column_stack([chan[f"{c}_syscool"].abs() + chan[f"{c}_sysheat"].abs()
                                         for c in CH6]), fb),
        "dhw": _shares(dhw[[f"dhw_{c}" for c in CH6]].to_numpy(float), fb),
    }
    if swap_basis:                          # negative control: cooling on heating shares
        basis["cool"], basis["heat"] = basis["heat"], basis["cool"]
    tot = np.zeros((len(hourly), len(CH6)))
    for meter, b in END_USES:
        if meter not in hourly.columns:
            continue
        s = hourly[meter].to_numpy(float)
        if b.startswith("direct:"):
            tot += chan[[f"{c}_{b.split(':')[1]}" for c in CH6]].to_numpy(float)
        else:
            tot += basis[b] * s[:, None]
    return tot / 3600.0                      # W (hourly J / 3600 s)


def cf_from_hourly(W, idx):
    sub = W[:, idx]
    stacked = sub.sum(axis=1)
    return float(stacked.max() / sub.max(axis=0).sum()), float(stacked.max()), int(stacked.argmax())


# ======================================================================================
def main():
    A = load(AGG)
    peak, diur, meta = A["peak"], A["diurnal"], A["meta"]
    ls = pd.read_csv(os.path.join(S9, "step9_loadshape_peaks.csv"))
    eui = pd.read_csv(os.path.join(S9, "step9_eui_by_channel.csv"))
    assert int(meta["attribution_closed"].sum()) == 56, "agg_meta must carry 56 closed cells"

    # ---------------- CONTROL 1: my reader == Step-9's own table, per cell, exactly -------
    print("\nCONTROL 1 -- reader vs step9_loadshape_peaks.csv (all 56 cells x 4 channels)")
    worst = 0.0
    for _, r in ls[ls["channel"].isin(TENANT)].iterrows():
        h = circ(wd_profile(diur, r["cell_tag"], r["channel"]))
        worst = max(worst, abs(h - r["wd_peak_hour_circular"]))
    check("controls", "max |reader - step9 wd_peak_hour_circular| over 224 rows", worst, 0.0, 1e-9)

    # ---------------- CONTROL 2: published B_central numbers (manuscript 5.3) ------------
    print("\nCONTROL 2 -- published 2030-central values, manuscript section 5.3")
    bc = ls[ls["scenario"] == "B_central"]
    pub_hours = {"office": (11.90, 11.82, 11.93), "residential": (12.04, 12.01, 12.10),
                 "retail": (12.37, 12.11, 12.62), "hotel": (18.91, 18.84, 18.94)}
    for ch, (med, lo, hi) in pub_hours.items():
        v = np.array([circ(wd_profile(diur, c, ch)) for c in bc[bc.channel == ch]["cell_tag"]])
        check(PUB_BUCKET, f"B_central {ch} WD peak hour median", np.median(v), med, 0.005)
        check(PUB_BUCKET, f"B_central {ch} WD peak hour min", v.min(), lo, 0.005)
        check(PUB_BUCKET, f"B_central {ch} WD peak hour max", v.max(), hi, 0.005)
    b = peak[(peak.channel == "_BUILDING") & peak.cell_tag.str.startswith("B_central__")]
    check(PUB_BUCKET, "B_central building peak hour median", b.peak_hour_circular.median(), 14.95, 0.005)
    check(PUB_BUCKET, "B_central building peak hour min", b.peak_hour_circular.min(), 14.11, 0.005)
    check(PUB_BUCKET, "B_central building peak hour max", b.peak_hour_circular.max(), 15.70, 0.005)
    pub_mn = {"retail": (72.03, 2.11), "office": (569.33, 48.10),
              "residential": (347.82, 89.53), "hotel": (335.93, 434.47)}
    for ch, (mid, nig) in pub_mn.items():
        pr = [wd_profile(diur, c, ch) for c in bc[bc.channel == ch]["cell_tag"]]
        mids = [p[11:15].mean() / 1000 for p in pr]
        nigs = [np.concatenate([p[0:5], p[22:24]]).mean() / 1000 for p in pr]
        check(PUB_BUCKET, f"B_central {ch} WD midday kW median", np.median(mids), mid, 0.005)
        check(PUB_BUCKET, f"B_central {ch} WD night kW median", np.median(nigs), nig, 0.005)
    # coincidence factor: which scope reproduces 0.941 / 0.851?
    cfb = peak[peak.channel == "_BUILDING"].set_index("cell_tag")["coincidence_factor"]
    cf_bc = cfb[cfb.index.str.startswith("B_central__")]
    print(f"    CF scope probe: B_central-4 median {cf_bc.median():.4f} min {cf_bc.min():.4f} "
          f"({cf_bc.idxmin()}); all-56 median {cfb.median():.4f} min {cfb.min():.4f} ({cfb.idxmin()})")
    RESULTS["cf_scope_probe"] = dict(bcentral_median=cf_bc.median(), bcentral_min=cf_bc.min(),
                                     bcentral_argmin=cf_bc.idxmin(), all56_median=cfb.median(),
                                     all56_min=cfb.min(), all56_argmin=cfb.idxmin())
    check(PUB_BUCKET, "CF median (B_central, 4 cells -- the scope of manuscript 5.3)", cf_bc.median(), 0.941, 0.0005)
    check(PUB_BUCKET, "CF min (B_central, Tall CLG)", cf_bc.min(), 0.851, 0.0005)
    # Published ranges that fail at +-0.005: test the double-rounding explanation (value first
    # rounded to 3 dp in an intermediate table, then to 2 dp in the prose).
    dr = lambda x: round(round(float(x), 3), 2)
    for name, x, want in (("building peak hour min", b.peak_hour_circular.min(), 14.11),
                          ("building peak hour max", b.peak_hour_circular.max(), 15.70)):
        check(PUB_BUCKET, f"B_central {name}, double-rounded 3dp->2dp", dr(x), want, 1e-9)
    rn = [np.concatenate([p[0:5], p[22:24]]).mean() / 1000 for p in
          [wd_profile(diur, c, "retail") for c in bc[bc.channel == "retail"]["cell_tag"]]]
    check(PUB_BUCKET, "B_central retail WD night kW median, double-rounded", dr(np.median(rn)), 2.11, 1e-9)
    # Office range low end 11.82: the all-days column (agg_peak peak_hour_circular), not weekday
    ao = peak[(peak.channel == "office") & (peak.daytype == "all") & (peak.metric == "energy_W")
              & peak.cell_tag.str.startswith("B_central__")]["peak_hour_circular"]
    check(PUB_BUCKET, "B_central office ALL-DAYS peak hour min (explains published 11.82)", ao.min(), 11.82, 0.005)
    # EUI Table 5 (56 cells)
    pub_eui = {"office": (61.72, 90.21, 71.02), "retail": (63.63, 96.84, 75.63),
               "hotel": (203.33, 318.42, 260.54), "residential": (111.57, 128.77, 119.10)}
    for ch, (lo, hi, med) in pub_eui.items():
        v = eui[eui.channel == ch]["eui_CFA_kWh_m2"]
        check(PUB_BUCKET, f"Table 5 {ch} CFA median (56 cells)", v.median(), med, 0.005)
        check(PUB_BUCKET, f"Table 5 {ch} CFA min", v.min(), lo, 0.005)
        check(PUB_BUCKET, f"Table 5 {ch} CFA max", v.max(), hi, 0.005)
    # Section 5.2 office uninjected control 85.45
    necb_off = eui[(eui.scenario == "Default_NECB") & (eui.channel == "office")]["eui_CFA_kWh_m2"]
    print(f"    Default_NECB office CFA per cell: {necb_off.round(2).tolist()}")
    check(PUB_BUCKET, "Default_NECB office CFA median (published 85.45)", necb_off.median(), 85.45, 0.005)
    # Reconstruct hourly channel energy from cell files; must reproduce agg_peak CF exactly.
    print("\nCONTROL 3 -- hourly reconstruction from cell files reproduces agg_peak CF + building peak")
    Wcache, worst_cf, worst_pk = {}, 0.0, 0.0
    for s in SCEN:
        for bld, city in BLD_CITY:
            cell = f"{s}__{bld}__{city}"
            W = hourly_channels(cell, meta)
            Wcache[cell] = W
            cf6, pk6, _ = cf_from_hourly(W, list(range(6)))
            row = peak[(peak.cell_tag == cell) & (peak.channel == "_BUILDING")].iloc[0]
            worst_cf = max(worst_cf, abs(cf6 - row.coincidence_factor))
            worst_pk = max(worst_pk, abs(pk6 - row.peak_W) / row.peak_W)
    check("controls", "max |CF6 reconstructed - agg_peak| (12 cells)", worst_cf, 0.0, 1e-9)
    check("controls", "max rel |building peak reconstructed - agg_peak| (12 cells)", worst_pk, 0.0, 1e-9)

    # ---------------- NEGATIVE CONTROLS: the reader must FAIL on wrong input -------------
    print("\nNEGATIVE CONTROLS -- each MUST print FAIL")
    if ARM == "P10R":   # the arm's own correct values (the published ones belong to the frozen arm)
        _m = lambda ch: float(np.median([circ(wd_profile(diur, c, ch)) for c in bc[bc.channel == ch]["cell_tag"]]))
        TRUTH = dict(office_h=_m("office"), hotel_h=_m("hotel"), retail_h=_m("retail"), cf=float(cf_bc.median()))
    else:
        TRUTH = dict(office_h=11.90, hotel_h=18.91, retail_h=12.37, cf=0.941)
    RESULTS["negative_control_truth"] = TRUTH
    print(f"    truth used: {TRUTH}")
    # N1: drop the metric filter (people rows come first? take whichever 24 rows sort first)
    v = []
    for c in bc[bc.channel == "office"]["cell_tag"]:
        d = diur[(diur.cell_tag == c) & (diur.channel == "office") & (diur.season == "all")
                 & (diur.daytype == "WD")]
        v.append(circ(d[d.metric == "people"].sort_values("hour")["W"].to_numpy()))
    check("negative_controls", "N1 office peak hour read from metric=='people' (filter wrong)",
          np.median(v), TRUTH["office_h"], 0.005)
    # N2: wrong scenario (Y2022 read as if it were B_central)
    y = ls[(ls.scenario == "Y2022") & (ls.channel == "hotel")]
    v = [circ(wd_profile(diur, c, "hotel")) for c in y["cell_tag"]]
    check("negative_controls", "N2 hotel peak hour from Y2022 rows instead of B_central",
          np.median(v), TRUTH["hotel_h"], 0.005)
    # N3: profile rotated by 3 h
    v = [circ(np.roll(wd_profile(diur, c, "retail"), 3)) for c in bc[bc.channel == "retail"]["cell_tag"]]
    check("negative_controls", "N3 retail profile rotated +3 h", np.median(v), TRUTH["retail_h"], 0.005)
    # N4: superseded aggregate directory
    if os.path.isdir(AGG_SUPERSEDED):
        P = pd.read_csv(os.path.join(AGG_SUPERSEDED, "agg_peak.csv"))
        cfo = P[P.channel == "_BUILDING"]["coincidence_factor"]
        check("negative_controls", f"N4 CF median from wrong aggregate {os.path.basename(AGG_SUPERSEDED)}",
              cfo.median(), TRUTH["cf"], 0.0005)
        Do = pd.read_csv(os.path.join(AGG_SUPERSEDED, "agg_diurnal.csv"))
        v = [circ(wd_profile(Do, c, "retail")) for c in bc[bc.channel == "retail"]["cell_tag"]]
        check("negative_controls", f"N4b retail B_central WD peak hour from wrong aggregate {os.path.basename(AGG_SUPERSEDED)}",
              np.median(v), TRUTH["retail_h"], 0.005)
    # N5: hourly reconstruction with cooling allocated on HEATING shares must NOT reproduce CF
    cell = "Default_NECB__Tall__CLG"
    cfw, _, _ = cf_from_hourly(hourly_channels(cell, meta, swap_basis=True), list(range(6)))
    cfo = peak[(peak.cell_tag == cell) & (peak.channel == "_BUILDING")].coincidence_factor.iloc[0]
    check("negative_controls", "N5 |CF - published| with cool/heat allocation bases swapped, Default_NECB Tall CLG",
          abs(cfw - cfo), 0.0, 1e-9)
    # N5b (recorded, not a gate): the fallback basis alone does not move CF (fallback hours are
    # zero-load hours, never the peak) -- a wrong fallback is invisible to this reader.
    cfz, _, _ = cf_from_hourly(hourly_channels(cell, meta, break_fallback=True), list(range(6)))
    RESULTS["N5b_fallback_insensitive_absdiff"] = abs(cfz - cfo)
    print(f"    N5b (info): equal-share fallback moves CF by {abs(cfz - cfo):.2e} -- not detectable")
    # N6: 4-channel CF computed on 6-channel columns mislabelled -> differs from published 6-ch CF
    #     (shows the CF is sensitive to which channels are summed)
    cf4, _, _ = cf_from_hourly(Wcache["B_central__Tall__CLG"], [0, 1, 2, 3])
    cf6 = peak[(peak.cell_tag == "B_central__Tall__CLG") & (peak.channel == "_BUILDING")].coincidence_factor.iloc[0]
    check("negative_controls", "N6 4-tenant-channel CF vs published 6-channel CF, B_central Tall CLG",
          cf4, round(cf6, 3), 0.0005)

    # ---------------- COMPARISON ------------------------------------------------------
    print("\nCOMPARISON")
    rows = []
    for s in SCEN:
        for bld, city in BLD_CITY:
            cell = f"{s}__{bld}__{city}"
            W = Wcache[cell]
            prk = peak[(peak.cell_tag == cell)]
            brow = prk[prk.channel == "_BUILDING"].iloc[0]
            cf4, pk4, i4 = cf_from_hourly(W, [0, 1, 2, 3])
            cf6, pk6, i6 = cf_from_hourly(W, list(range(6)))
            wd_b6 = sum(wd_profile(diur, cell, c) for c in CH6)
            wd_b4 = sum(wd_profile(diur, cell, c) for c in TENANT)
            base = dict(cell_tag=cell, scenario=s, building=bld, city=city)
            rows.append({**base, "channel": "_BUILDING",
                         "wd_peak_hour_circular": circ(wd_b6), "wd_peak_hour_argmax": int(np.argmax(wd_b6)),
                         "wd_R": resultant(wd_b6),
                         "all_peak_hour_circular_published": brow.peak_hour_circular,
                         "wd_peak_hour_circular_4tenant": circ(wd_b4),
                         "wd_peak_hour_argmax_4tenant": int(np.argmax(wd_b4)),
                         "annual_peak_hour_of_day_6ch": i6 % 24, "annual_peak_day_of_year_6ch": i6 // 24 + 1,
                         "annual_peak_hour_of_day_4tenant": i4 % 24,
                         "annual_peak_day_of_year_4tenant": i4 // 24 + 1,
                         "peak_kW": brow.peak_W / 1000, "sum_of_channel_peaks_kW_6ch": brow.sum_of_channel_peaks_W / 1000,
                         "coincidence_factor_published_6ch": brow.coincidence_factor,
                         "coincidence_factor_4tenant": cf4,
                         "day_night_ratio_08_18": wd_b6[DAY_H].mean() / wd_b6[NIGHT_H].mean(),
                         "midday_night_ratio_published_def": wd_b6[11:15].mean() / np.concatenate([wd_b6[0:5], wd_b6[22:24]]).mean(),
                         })
            for ch in TENANT:
                p = wd_profile(diur, cell, ch)
                pp = wd_profile(diur, cell, ch, metric="people")
                e = eui[(eui.cell_tag == cell) & (eui.channel == ch)].iloc[0]
                ap = prk[(prk.channel == ch) & (prk.daytype == "all") & (prk.metric == "energy_W")].iloc[0]
                rows.append({**base, "channel": ch,
                             "wd_peak_hour_circular": circ(p), "wd_peak_hour_argmax": int(np.argmax(p)),
                             "wd_R": resultant(p),
                             "all_peak_hour_circular_published": ap.peak_hour_circular,
                             "occ_wd_peak_hour_circular": circ(pp), "occ_wd_peak_hour_argmax": int(np.argmax(pp)),
                             "occ_wd_R": resultant(pp),
                             "peak_kW": ap.peak_W / 1000,
                             "wd_midday_kW": p[11:15].mean() / 1000,
                             "wd_night_kW": np.concatenate([p[0:5], p[22:24]]).mean() / 1000,
                             "midday_night_ratio_published_def": p[11:15].mean() / np.concatenate([p[0:5], p[22:24]]).mean(),
                             "day_night_ratio_08_18": p[DAY_H].mean() / p[NIGHT_H].mean(),
                             "eui_CFA_kWh_m2": e.eui_CFA_kWh_m2, "eui_GFAshare_kWh_m2": e.eui_GFAshare_kWh_m2})
    comp = pd.DataFrame(rows)
    comp.to_csv(os.path.join(OUT, "P3_comparison_long.csv"), index=False)

    # Summary: median over the 4 building-city cells, per scenario x channel
    num = [c for c in comp.columns if c not in ("cell_tag", "scenario", "building", "city", "channel")]
    summ = comp.groupby(["channel", "scenario"])[num].agg(["median", "min", "max"])
    summ.columns = [f"{a}__{b}" for a, b in summ.columns]
    summ = summ.reset_index()
    summ.to_csv(os.path.join(OUT, "P3_comparison_summary.csv"), index=False)

    # Deltas survey - code per cell
    key = ["building", "city", "channel"]
    nb = comp[comp.scenario == "Default_NECB"].set_index(key)
    dl = []
    for s in ("Y2022", "B_central"):
        sb = comp[comp.scenario == s].set_index(key)
        d = pd.DataFrame(index=sb.index)
        for c in ("wd_peak_hour_circular", "all_peak_hour_circular_published", "occ_wd_peak_hour_circular"):
            if c in sb:
                x = (sb[c] - nb[c] + 12) % 24 - 12          # signed circular difference, hours
                d[f"d_{c}_h"] = x
        for c in ("coincidence_factor_published_6ch", "coincidence_factor_4tenant"):
            d[f"d_{c}"] = sb[c] - nb[c]
        for c in ("day_night_ratio_08_18", "midday_night_ratio_published_def", "eui_CFA_kWh_m2",
                  "eui_GFAshare_kWh_m2", "peak_kW"):
            d[f"rel_{c}_pct"] = 100 * (sb[c] / nb[c] - 1)
        d["scenario"] = s
        dl.append(d.reset_index())
    delta = pd.concat(dl, ignore_index=True)
    delta.to_csv(os.path.join(OUT, "P3_delta_vs_code.csv"), index=False)

    # Figure data A: weekday energy profiles (kW) per cell x scenario x channel (+ building 6ch)
    fa = []
    for s in SCEN:
        for bld, city in BLD_CITY:
            cell = f"{s}__{bld}__{city}"
            for ch in TENANT + ["_BUILDING"]:
                p = (sum(wd_profile(diur, cell, c) for c in CH6) if ch == "_BUILDING"
                     else wd_profile(diur, cell, ch))
                for h in range(24):
                    fa.append(dict(scenario=s, building=bld, city=city, channel=ch, hour=h,
                                   wd_kW=p[h] / 1000))
    pd.DataFrame(fa).to_csv(os.path.join(FIGDATA, "fig_codeschedule_vs_survey_profiles.csv"), index=False)
    comp.to_csv(os.path.join(FIGDATA, "fig_codeschedule_vs_survey_metrics.csv"), index=False)

    # Figure data B: weekday presence (people) per channel, by hour, per cycle + 2030 central + code
    fb_rows = []
    for s in ("Default_NECB", "Y2005", "Y2010", "Y2015", "Y2022", "B_central"):
        for bld, city in BLD_CITY:
            cell = f"{s}__{bld}__{city}"
            mm = meta.set_index("cell_tag").loc[cell]
            man = json.load(open(os.path.join(CELLS, cell, "manifest.json"), encoding="utf-8"))
            injected = {d["channel"] for d in man.get("INPUTS_HASH_DETAIL", [])}
            for ch in TENANT:
                for dt in ("WD", "WE"):
                    pp = wd_profile(diur, cell, ch, metric="people", daytype=dt)
                    for h in range(24):
                        fb_rows.append(dict(scenario=s, building=bld, city=city, channel=ch, daytype=dt,
                                            hour=h, people=pp[h], area_m2=mm[f"area_{ch}_m2"],
                                            people_per_100m2=100 * pp[h] / mm[f"area_{ch}_m2"],
                                            channel_injected=ch in injected))
    pd.DataFrame(fb_rows).to_csv(os.path.join(FIGDATA, "fig_presence_by_channel_data.csv"), index=False)

    # Console summary
    pd.set_option("display.width", 250, "display.max_columns", 40)
    show = ["wd_peak_hour_circular__median", "wd_peak_hour_argmax__median",
            "all_peak_hour_circular_published__median", "occ_wd_peak_hour_circular__median",
            "occ_wd_peak_hour_argmax__median",
            "coincidence_factor_published_6ch__median", "coincidence_factor_4tenant__median",
            "day_night_ratio_08_18__median", "midday_night_ratio_published_def__median",
            "eui_CFA_kWh_m2__median", "eui_GFAshare_kWh_m2__median"]
    print(summ[["channel", "scenario"] + [c for c in show if c in summ]].round(3).to_string())
    print("\nPER-CELL (key metrics)")
    print(comp[["cell_tag", "channel", "wd_peak_hour_circular", "wd_peak_hour_argmax",
                "all_peak_hour_circular_published", "occ_wd_peak_hour_circular", "occ_wd_peak_hour_argmax",
                "coincidence_factor_published_6ch", "coincidence_factor_4tenant",
                "day_night_ratio_08_18", "eui_CFA_kWh_m2", "eui_GFAshare_kWh_m2", "wd_R"]].round(3).to_string())
    print("\nDELTAS vs code")
    print(delta.round(3).to_string())

    with open(os.path.join(OUT, "P3_controls.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=1, default=float)
    nc = RESULTS["controls"]
    nn = RESULTS["negative_controls"]
    pv = RESULTS["published_vs_new"]
    if pv:
        print(f"PUBLISHED vs NEW ARM (info, not a control): {sum(r['verdict'] == 'PASS' for r in pv)}/{len(pv)} "
              f"published numbers still reproduced within their tolerance")
    print(f"\nCONTROLS PASS {sum(r['verdict'] == 'PASS' for r in nc)}/{len(nc)}; "
          f"NEGATIVE CONTROLS FAILING AS REQUIRED {sum(r['verdict'] == 'FAIL' for r in nn)}/{len(nn)}")


if __name__ == "__main__":
    main()
