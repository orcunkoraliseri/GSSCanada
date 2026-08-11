#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3J Leg-3 -- Step 9 : activity-driven end-use loads, four channels.

Reads the Step-8 §8E aggregate tables (no re-simulation -- coupling lives in Steps 7/8) and
produces the four Step-9 tables, the figure set, a gate scorecard and an HTML report.

READ THIS BEFORE TRUSTING ANY EUI IN THE OUTPUT
-----------------------------------------------
Step 9 was blocked on three Step-8 defects found 2026-07-31, all fixed upstream before this
script was written. They are recalled here because each one would have produced a
plausible-looking, badly wrong number rather than an error:

  Defaut 5  53.5 % of site energy (13,884.91 GJ of gas) was reported as zero, because the
            campaign asked for pre-EnergyPlus-9.4 meter names (`Gas:Facility` &c.). Hotel DHW
            alone is 7,726.75 GJ. Every EUI would have been roughly half of the truth, and the
            hotel -- the gas-heaviest channel -- would have been the most wrong.
  Defaut 6  Per-channel series were unmultiplied (Sigma = 25.4 % of the facility meter), and
            because zone multipliers differ BY CHANNEL the error did not cancel in shares.
  Defaut 7  The occupiable shares in the pipeline docs are placeholders (three channels at an
            identical 24.4 %, against a measured 44.65 / 24.91 / 22.40 / 5.53 on the Tall
            tower). The ±2 pp EUI-share gate compares against PARSED shares from agg_meta.csv,
            never against those constants.

§8E refuses to aggregate a cell whose fuel/channel closures do not pass, so if this script
runs at all, the energy it reads accounts for itself.

CONVENTIONS FIXED HERE (Step-9 doc §8, caveat 3)
------------------------------------------------
* Hour-of-day is CIRCULAR. Peak hours use the load-weighted circular mean (a 2J plotting bug
  arithmetic-averaged a bimodal morning/evening population into a meaningless ~14.5 h).
  Both the circular mean and the profile argmax are reported; the tables say which is which.
* EUI is reported on BOTH bases and the basis is a column, never a footnote: CFA (the
  channel's own conditioned floor area -- primary, thermodynamic) and GFA-share (the channel
  plus its area-prorated share of service/MEP and exterior lighting -- the basis SCIEU/CEUD
  stock figures are quoted on).
* As-modelled band = PASS criterion. Empirical/survey band = INFO only, never a FAIL.

USAGE
-----
    py -3 3rdJ_09_activityDrivenLoads_4split.py [--agg-dir ...] [--outdir ...]
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AGG = os.path.abspath(os.path.join(HERE, "..", "Step8_docs", "outputs_step8", "agg"))
DEFAULT_OUT = os.path.join(HERE, "outputs_step9")
# GSSCanada-main/ -- same three-levels-up convention 3rdJ_08D_campaign_cells.py itself uses
# (repo_root/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs -> repo_root).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CAMPAIGN_CELLS_PY = os.path.abspath(
    os.path.join(HERE, "..", "Step8_docs", "3rdJ_08D_campaign_cells.py"))


def _load_campaign_cells_module():
    """Load 3rdJ_08D_campaign_cells.py by file path -- its filename is not a valid Python
    identifier, so a plain `import` is impossible; this is the same importlib.util.
    spec_from_file_location pattern already used by 3rdJ_08D_campaign_driver.py,
    3rdJ_08D_campaign_local.py, 3rdJ_08D_verify_campaign.py and
    3rdJ_08A_gen_historical_products_4split.py. DELIBERATE_CHANNEL_EXCEPTIONS / _expected_channels
    / build_campaign_cells are READ from Step-8's module, never copied -- a second copy of that
    constant would be a second source of truth, the exact defect this project already hit and
    fixed once (see this file's module docstring, Defaut 7 lineage)."""
    spec = importlib.util.spec_from_file_location("_campaign_cells_mod_step9", CAMPAIGN_CELLS_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

TENANT = ["office", "retail", "hotel", "residential"]
ALL_CH = TENANT + ["residential_common", "service_MEP"]

# ---------------------------------------------------------------- benchmarks --
# as-modelled band = PASS criterion; empirical band = INFO. Sources are in the band name and
# must stay there: a number in a table with no provenance becomes a number nobody can defend.
#
# V2-D4 (2026-08-04) -- PROVENANCE ONLY, no band value changed. Every `src=` below now names a path
# that resolves from the repo root. The office `src=` previously read "Step8_docs/deepResearch/...",
# which resolves to NOTHING: `Leg3_4-split/Step8_docs/deepResearch/` does not exist. The document is
# in the FROZEN Leg-2 tree. A provenance string that does not resolve is the same defect as no
# provenance at all -- it just takes longer to discover.
#
# V2-D4 (values half, 2026-08-05) -- WP-B has now decided every band, and the decisions are in
# Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md. *** READ THIS FIRST: **not one threshold moved.**
# WP-B changed WHERE the numbers come from and, for retail, WHICH RULE reads them -- it did not widen
# anything. All three EUI gates were failing before these decisions and all three still fail after
# them. If a future reader finds a band value here that differs from the four listed below, it was
# changed by someone else, not by WP-B.
#
#   office 100/135/200  -- V2-B1: value UNCHANGED, floor recorded CONTESTED AND UNSOURCED (see src).
#   retail  80/110/155  -- V2-B3: values UNCHANGED, decision RULE changed to median-in-band.
#   hotel  180/240/300  -- V2-B2: values UNCHANGED, ceiling RE-CITED to a first-party 90.1-2019 read.
#   residential         -- no as-modelled band, unchanged.
#
# `rule` is per channel and is the criterion the S9-EUI-* gate applies:
#   "all_cells" -- every cell must sit inside [lo, hi] (Leg-3's own rule since this scorer was
#                  written; office and hotel keep it).
#     *** PROVENANCE CORRECTED 2026-08-06 (V3-H3 desk check, no rule changed): "all_cells" is NOT
#     inherited from Leg-2 and was never "the original rule" for the office band. Leg-2 scored the
#     SAME band values on the CHANNEL MEDIAN and graded a miss WARN, in both places it appears:
#       Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:462-470  (G2o, median, WARN)
#       Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py:1420-1431     (4.3-office, median,
#                                                                              WARN, "non-blocking")
#     Leg-3 inherited the band VALUES (135/100/200 -- identical) and then applied a stricter rule AND
#     a stricter severity without recording that it had changed either. Correcting the citation is
#     not a licence to adopt Leg-2's rule: that package is median AND WARN together, and taking half
#     of it is a third rule invented at the moment it would clear a gate. See V3-H3.
#
# THE RULE PRINCIPLE, written down 2026-08-06 (V3-H3, option A -- status quo made explicit).
# Until now `rule` was a per-channel value with no stated criterion for choosing it, which is how a
# "uniform rule" could be proposed as housekeeping when it would in fact clear exactly one FAIL.
#   DEFAULT = "all_cells".
#   "median" applies to a channel ONLY where the channel's across-cell spread is small enough that a
#   re-run's own noise can flip the verdict -- V2-B3's condition, verbatim: "an all-cells rule on a
#   spread smaller than its own uncertainty reports noise as a verdict" (retail: V2-E3 moved the
#   median by -0.05 % and that alone flipped a cell, 55/56 -> 54/56).
#   Measured on the shipped deliverable, across-cell range / band width:
#       office 28.50/100.0 = 0.285 | retail 33.22/75.0 = 0.443 | hotel 115.09/120.0 = 0.959
#   Hotel's cells span 96 % of its own band: they differ genuinely, they are not clustered inside
#   their uncertainty, so an all-cells rule on them reports signal. Hotel is the channel LEAST
#   eligible for median under the principle that put retail there.
#   *** DISCLOSURE: these spreads were measured AFTER it was known which rule clears hotel. That is
#   why no numeric boundary is written here -- a boundary chosen with the answer in hand is not
#   blind. The principle is the condition above; the arithmetic is published so a reader can check
#   that applying it changes NOTHING (office and retail FAIL under both rules; hotel keeps all_cells).
#   A principled rule that changes no status is the one thing gate-shopping cannot produce.
#   REOPENS IF: (T1) the user accepts the precedent-restoration argument above; (T2) any channel's
#   across-cell spread falls below the demonstrated re-run noise of its own median; (T3) the frozen
#   deliverable is reopened for another reason, at which point re-publication costs nothing extra.
#   "median"    -- the channel's CFA median must sit inside [lo, hi] (retail only, V2-B3).
# The gate publishes BOTH readings whatever the rule, precisely so a rule-induced status change is
# visible in the artefact and cannot be mistaken for the model having improved.
BENCH = {
    "office":      dict(central=135.0, lo=100.0, hi=200.0, rule="all_cells",
                        # the em dash in the filename below is the FILE's own byte (U+2014). It is a
                        # path, not prose, so it is reproduced literally -- changing it to "--" to
                        # satisfy the house dash rule would silently break the path again.
                        src="NECB2020/90.1-2019 DOE-PNNL as-modelled band -- 3J_docs_occ_nTemp/"
                            "Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI (NECB 2020, "
                            "ASHRAE 90.1, DOE-PNNL prototypes) — As-Modelled Bands.md, Table 7.1 "
                            "(VALUES repris de Leg-2; the RULE is NOT -- V3-H3, 2026-08-06: Leg-2 "
                            "scored these same values on the channel MEDIAN and graded a miss WARN "
                            "[Leg2 Step9 :462-470, Leg2 Step8 :1420-1431]. Leg-3 chose all_cells + "
                            "FAIL without recording the change. Rule NOT altered by this "
                            "correction). *** FLOOR CONTESTED AND UNSOURCED (V2-B1, decided "
                            "2026-08-05): the source document gives three different floors for it "
                            "(Table 7.1 = 100.0, line 21 = 80-140, Table 2.1 = 85.0-115.0), and the "
                            "UNINJECTED Default_NECB control fails this gate at 85.45 -- a floor no "
                            "untreated control can clear is measuring the band, not the model. The "
                            "value is NOT moved; it is published as contested. Limitation -> V2-G3",
                        info=(230.0, 170.0, 360.0), info_src="SCIEU/CEUD"),
    "retail":      dict(central=110.0, lo=80.0,  hi=155.0, rule="median",
                        src="dr_L3-02 as-modelled (locked 2026-07-02) -- 3J_docs_occ_nTemp/"
                            "Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md. "
                            "RULE = median-in-band (V2-B3, 2026-08-05), replacing 56-of-56: V2-E3 "
                            "moved the median by -0.05 % and that alone flipped a cell, so an "
                            "all-cells rule on a spread smaller than its own uncertainty reports "
                            "noise as a verdict. Band VALUES unchanged",
                        info=(280.0, 150.0, 380.0), info_src="dr_L3-02 empirical"),
    "hotel":       dict(central=240.0, lo=180.0, hi=300.0, rule="all_cells",
                        src="ASHRAE 90.1-2019 Large Hotel prototype, retrieved first-party by V2-F6 "
                            "from the prototype ZIP's own .table.htm: 284.44 kWh/m2/yr at CZ 6A, "
                            "299.28 at CZ 7 (evidence: improvements/v2/f6_prototype_evidence/). "
                            "*** SUPERSEDES dr_L3-03 as the CITATION for these values (V2-B2, "
                            "2026-08-05): V2-F4 chased dr_L3-03's two primaries to the end and "
                            "NEITHER EXISTS (one NOT FOUND; PNNL-28543 resolves to a nuclear-fuel "
                            "report). The band was unsupported, not wrong -- the 300 ceiling rested "
                            "on the 90.1-2004 lineage's 302.21 and the vintage-matched 2019 value "
                            "is 1.0 % from it, so the 'a 2004 band scores a 2019 building' "
                            "objection is dead. Values unchanged; gate still FAILs. Residual "
                            "archetype gap (NECB-2017 MTL/Calgary vs 90.1-2019 Rochester / "
                            "International Falls) is a LIMITATION -> V2-G3, NOT a tolerance",
                        info=(350.0, 220.0, 480.0), info_src="dr_L3-03 empirical"),
    "residential": dict(central=None, lo=None, hi=None, rule=None,
                        src="no as-modelled band (tower apartments)",
                        info=(130.6, 113.9, 147.2), info_src="SHEU-2019 HighRise (context only -- tower != SHEU stock basis)"),
}

BUNDLES = ["B_cons", "B_central", "B_opt"]
ERAS = ["Y2005", "Y2010", "Y2015", "Y2022"]
SENS = {"office": ("sens_office_cons", "B_central", "sens_office_opt"),
        "retail": ("sens_retail_cons", "B_central", "sens_retail_opt"),
        "hotel":  ("sens_hotel_cons",  "B_central", "sens_hotel_opt")}
# The direction each channel's "cons"/"opt" lever moves occupancy, from the Step-6 levers:
# office WFH conservative = MORE people on site (return-to-office), retail 0.90 -> 1.05,
# hotel SARIMA 0.92 -> 1.05. Stated so the monotonicity gate is directional, not hand-waved.
LEVER_ORDER = {"office": ("conservative", "hybrid", "fullyhybrid"),
               "retail": (0.90, 0.97, 1.05), "hotel": (0.92, 1.00, 1.05)}

THEME = {"office": "#d62728", "retail": "#9467bd", "hotel": "#bcbd22",
         "residential": "#1f77b4", "residential_common": "#7f7f7f", "service_MEP": "#c7c7c7"}
J_TO_KWH = 1.0 / 3.6e6


def _log(m):
    print(f"  {m}", flush=True)


def circular_mean_hour(profile) -> float:
    w = np.asarray(profile, dtype=float)
    if not np.isfinite(w).any() or w.sum() <= 0:
        return float("nan")
    ang = 2 * np.pi * np.arange(len(w)) / len(w)
    mean = np.arctan2(float((w * np.sin(ang)).sum()), float((w * np.cos(ang)).sum()))
    return float((mean % (2 * np.pi)) / (2 * np.pi) * len(w))


def circular_resultant(profile) -> float:
    """Resultant length R in [0, 1] -- how concentrated a profile is around its mean hour.

    Caveat 3 says "use the circular mean, not the arithmetic mean". True, but incomplete: a
    circular mean is exactly as meaningless as an arithmetic one when R is small, because the
    direction is then set by noise. Measured on this campaign: retail occupancy R = 0.82 and
    office R = 0.66 -- sharp midday peaks, mean hour meaningful. Residential occupancy R = 0.22
    and hotel R = 0.18 -- near-antipodal shapes (home overnight vs away midday) whose vectors
    almost cancel, which is why the residential mean hour wandered across 0.30-23.62 h over
    cells that are behaviourally identical. Any gate quoting a mean hour must check R first.
    """
    w = np.asarray(profile, dtype=float)
    if not np.isfinite(w).any() or w.sum() <= 0:
        return float("nan")
    ang = 2 * np.pi * np.arange(len(w)) / len(w)
    return float(np.hypot(float((w * np.sin(ang)).sum()),
                          float((w * np.cos(ang)).sum())) / w.sum())


# --------------------------------------------------------------- load agg -----
def load_agg(agg_dir: str) -> dict:
    need = ["agg_annual.csv", "agg_peak.csv", "agg_diurnal.csv", "agg_meta.csv"]
    missing = [f for f in need if not os.path.isfile(os.path.join(agg_dir, f))]
    if missing:
        raise SystemExit(
            f"[FAIL] missing §8E table(s) in {agg_dir}: {missing}\n"
            f"       Run 3rdJ_08E_aggregate_4split.py first. Step 9 reads §8E output and does "
            f"not re-simulate; there is nothing to fall back on.")
    d = {f.split(".")[0].replace("agg_", ""): pd.read_csv(os.path.join(agg_dir, f)) for f in need}
    meta = d["meta"]
    if not meta["attribution_closed"].all():
        bad = list(meta.loc[~meta["attribution_closed"], "cell_tag"])
        raise SystemExit(f"[FAIL] {len(bad)} cell(s) whose attribution does not close against "
                         f"site energy: {bad[:5]}. Fix §8E before reading any EUI.")
    return d


# --------------------------------------------------------- table builders -----
def build_eui(annual: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """§R1 -- EUI per channel x cell, on BOTH bases, with the verdict column.

    CFA basis   : channel energy / channel conditioned floor area.
    GFA-share   : (channel energy + its area-share of service/MEP + exterior lighting)
                  / (channel area + its area-share of service/MEP), i.e. the whole building
                  redistributed onto the tenant channels -- what a stock database reports.
    """
    e = (annual.groupby(["cell_tag", "scenario", "building", "city", "channel"], as_index=False)
         ["energy_J"].sum())
    m = meta.set_index("cell_tag")
    # agg_annual and agg_meta must describe the same set of cells. A cell present in one and not
    # the other means §8E wrote a partial set, and silently dropping it would understate the
    # campaign while every remaining number still looked fine.
    orphans = sorted(set(e["cell_tag"]) - set(m.index))
    if orphans:
        print(f"  [WARN] {len(orphans)} cell(s) in agg_annual.csv with no agg_meta.csv row -- "
              f"excluded from every EUI, and S9-CELLS will register the shortfall: {orphans[:5]}")
        e = e[e["cell_tag"].isin(m.index)]
    rows = []
    for cell, g in e.groupby("cell_tag"):
        mm = m.loc[cell]
        tenant_area = float(sum(mm[f"area_{c}_m2"] for c in TENANT))
        # Everything that is not a tenant channel: service/MEP, residential common, exterior.
        non_tenant_J = float(g.loc[~g["channel"].isin(TENANT), "energy_J"].sum())
        non_tenant_area = float(mm["total_building_area_m2"] - tenant_area)
        for c in TENANT:
            ej = float(g.loc[g["channel"] == c, "energy_J"].sum())
            area = float(mm[f"area_{c}_m2"])
            if area <= 0:
                continue
            share = area / tenant_area if tenant_area > 0 else 0.0
            eui_cfa = ej * J_TO_KWH / area
            eui_gfa = ((ej + non_tenant_J * share) * J_TO_KWH /
                       (area + non_tenant_area * share))
            b = BENCH[c]
            verdict = ("no as-modelled band" if b["lo"] is None else
                       ("PASS" if b["lo"] <= eui_cfa <= b["hi"] else "FAIL"))
            info_lo, info_hi = b["info"][1], b["info"][2]
            rows.append(dict(
                cell_tag=cell, scenario=mm["scenario"], building=mm["building"], city=mm["city"],
                channel=c, area_m2=area, energy_GJ=ej / 1e9,
                eui_CFA_kWh_m2=eui_cfa, eui_GFAshare_kWh_m2=eui_gfa,
                band_central=b["central"], band_lo=b["lo"], band_hi=b["hi"],
                verdict_asmodelled=verdict, band_src=b["src"],
                info_lo=info_lo, info_hi=info_hi,
                info_verdict=("IN" if info_lo <= eui_gfa <= info_hi else "OUT"),
                info_src=b["info_src"],
                energy_share_pct=100.0 * ej / float(g["energy_J"].sum()),
                area_share_pct=100.0 * area / float(mm["total_building_area_m2"]),
            ))
    df = pd.DataFrame(rows)
    # The project-novel ±2 pp gate (dr_L3-10): energy share vs PARSED occupiable share.
    df["share_delta_pp"] = df["energy_share_pct"] - df["area_share_pct"]
    return df


SCEN_OF = {}


def build_loadshape(peak: pd.DataFrame, diur: pd.DataFrame) -> pd.DataFrame:
    """§R2 -- peak magnitude and timing per channel, plus the coincidence story."""
    rows = []
    # `metric` separates the attributed load (energy_W) from the occupant count (people). Under
    # OD-7D the residential channel drives PEOPLE ONLY, so its ENERGY profile carries no evening
    # occupancy peak -- asking "when does residential peak?" of the energy series answers a
    # different question than it does for the three commercial channels. Both are reported, and
    # the gap between them is the measured form of D-20.
    pk_e = peak[(peak["daytype"] == "all") & (peak.get("metric", "energy_W") == "energy_W")]
    di_e = diur[diur.get("metric", "energy_W") == "energy_W"]
    di_p = diur[diur.get("metric", "energy_W") == "people"]
    pk_p = peak[peak.get("metric", "energy_W") == "people"]
    for (cell, ch), g in pk_e.groupby(["cell_tag", "channel"]):
        r = g.iloc[0]
        d = di_e[(di_e["cell_tag"] == cell) & (di_e["channel"] == ch) & (di_e["season"] == "all")]
        wd = d[d["daytype"] == "WD"].sort_values("hour")["W"].to_numpy()
        we = d[d["daytype"] == "WE"].sort_values("hour")["W"].to_numpy()
        dp = di_p[(di_p["cell_tag"] == cell) & (di_p["channel"] == ch) & (di_p["season"] == "all")]
        wdp = dp[dp["daytype"] == "WD"].sort_values("hour")["W"].to_numpy()
        wep = dp[dp["daytype"] == "WE"].sort_values("hour")["W"].to_numpy()
        rows.append(dict(
            cell_tag=cell, channel=ch, scenario=SCEN_OF.get(cell, ""),
            peak_kW=r["peak_W"] / 1000.0, mean_kW=r["mean_W"] / 1000.0,
            peak_hour_circular=r["peak_hour_circular"], peak_hour_argmax=r["peak_hour_argmax"],
            wd_peak_hour_circular=circular_mean_hour(wd) if len(wd) == 24 else np.nan,
            wd_midday_kW=float(wd[11:15].mean()) / 1000.0 if len(wd) == 24 else np.nan,
            wd_night_kW=float(np.concatenate([wd[0:5], wd[22:24]]).mean()) / 1000.0 if len(wd) == 24 else np.nan,
            we_midday_kW=float(we[11:15].mean()) / 1000.0 if len(we) == 24 else np.nan,
            we_mean_kW=float(we.mean()) / 1000.0 if len(we) == 24 else np.nan,
            wd_mean_kW=float(wd.mean()) / 1000.0 if len(wd) == 24 else np.nan,
            coincidence_factor=r["coincidence_factor"],
            # occupancy side
            occ_wd_peak_hour_circular=circular_mean_hour(wdp) if len(wdp) == 24 else np.nan,
            occ_wd_peak_hour_argmax=int(np.argmax(wdp)) if len(wdp) == 24 else -1,
            occ_we_peak_hour_circular=circular_mean_hour(wep) if len(wep) == 24 else np.nan,
            occ_wd_mean=float(wdp.mean()) if len(wdp) == 24 else np.nan,
            occ_we_mean=float(wep.mean()) if len(wep) == 24 else np.nan,
            occ_wd_evening=float(wdp[17:23].mean()) if len(wdp) == 24 else np.nan,
            occ_wd_midday=float(wdp[11:15].mean()) if len(wdp) == 24 else np.nan,
            occ_wd_R=circular_resultant(wdp) if len(wdp) == 24 else np.nan,
            wd_R=circular_resultant(wd) if len(wd) == 24 else np.nan,
        ))
    return pd.DataFrame(rows)


def build_scenario(eui: pd.DataFrame, ann: pd.DataFrame) -> pd.DataFrame:
    """§R3 -- scenario response per channel, and the material for G8o / G8r / G8h."""
    base = eui[eui["scenario"] == "B_central"][["building", "city", "channel", "energy_GJ"]]
    base = base.rename(columns={"energy_GJ": "base_GJ"})
    df = eui.merge(base, on=["building", "city", "channel"], how="left")
    df["energy_pct_vs_Bcentral"] = 100.0 * (df["energy_GJ"] - df["base_GJ"]) / df["base_GJ"]
    y22 = eui[eui["scenario"] == "Y2022"][["building", "city", "channel", "energy_GJ"]]
    y22 = y22.rename(columns={"energy_GJ": "y2022_GJ"})
    df = df.merge(y22, on=["building", "city", "channel"], how="left")
    df["energy_pct_vs_2022"] = 100.0 * (df["energy_GJ"] - df["y2022_GJ"]) / df["y2022_GJ"]
    return df[["cell_tag", "scenario", "building", "city", "channel", "energy_GJ",
               "eui_CFA_kWh_m2", "energy_pct_vs_Bcentral", "energy_pct_vs_2022"]]


def build_longitudinal(eui: pd.DataFrame, ls: pd.DataFrame) -> pd.DataFrame:
    """§R4 -- the 2005 -> 2022 trajectory per channel, energy and timing together."""
    e = eui[eui["scenario"].isin(ERAS)].copy()
    m = ls[["cell_tag", "channel", "wd_peak_hour_circular", "wd_midday_kW", "wd_night_kW"]]
    d = e.merge(m, on=["cell_tag", "channel"], how="left")
    ref = d[d["scenario"] == "Y2005"][["building", "city", "channel", "energy_GJ"]]
    ref = ref.rename(columns={"energy_GJ": "y2005_GJ"})
    d = d.merge(ref, on=["building", "city", "channel"], how="left")
    d["energy_pct_vs_2005"] = 100.0 * (d["energy_GJ"] - d["y2005_GJ"]) / d["y2005_GJ"]
    d["midday_share"] = d["wd_midday_kW"] / (d["wd_midday_kW"] + d["wd_night_kW"])
    return d.sort_values(["channel", "building", "city", "scenario"])


# ------------------------------------------------------------ gate scorecard --
def evaluate_gates(eui, ls, scen, lon, meta, outdir=None) -> list:
    G = []

    def add(gid, name, status, detail):
        G.append(dict(gate=gid, name=name, status=status, detail=detail))

    # -- EUI in band, per channel, as-modelled = PASS criterion --------------------------
    for c in TENANT:
        sub = eui[eui["channel"] == c]
        if BENCH[c]["lo"] is None:
            add(f"S9-EUI-{c}", f"EUI in as-modelled band ({c})", "INFO",
                f"no as-modelled band defined; CFA median {sub['eui_CFA_kWh_m2'].median():.1f} "
                f"kWh/m2/yr, SHEU HighRise context {BENCH[c]['info'][0]} "
                f"[{BENCH[c]['info'][1]}-{BENCH[c]['info'][2]}] on the GFA-share basis "
                f"(median {sub['eui_GFAshare_kWh_m2'].median():.1f})")
            continue
        # V2-D4: the criterion is now per channel (BENCH[c]["rule"]). Both readings are computed
        # and BOTH are printed whatever the rule is in force, for one reason: V2-B3 changed the
        # retail rule while the data stayed put, and a rule that changes a verdict on unchanged
        # data is indistinguishable from a widened band unless the counterfactual is published
        # next to the status. So the gate says what the OTHER rule would have returned, every run.
        lo, hi = BENCH[c]["lo"], BENCH[c]["hi"]
        rule = BENCH[c].get("rule", "all_cells")
        vals = sub["eui_CFA_kWh_m2"]
        n_fail = int((sub["verdict_asmodelled"] == "FAIL").sum())
        n_below = int((vals < lo).sum())
        n_above = int((vals > hi).sum())
        med = float(vals.median())
        st_all = "PASS" if n_fail == 0 else "FAIL"
        st_med = "PASS" if lo <= med <= hi else "FAIL"
        status, other = ((st_med, st_all) if rule == "median" else (st_all, st_med))
        other_name = "all-cells" if rule == "median" else "median-in-band"
        # Which END a channel fails at is not cosmetic: the hotel gate has held the same 28/56
        # count across two arms while every failing cell moved from below the floor to above the
        # ceiling. A gate reporting only a count would have called that "no change".
        ends = (f"{n_below} below the {lo} floor / {n_above} above the {hi} ceiling"
                if (n_below or n_above) else "none outside")
        add(f"S9-EUI-{c}", f"EUI in as-modelled band ({c}, rule = {rule})", status,
            f"RULE IN FORCE = {rule} -> {status}. Median {med:.1f} kWh/m2/yr vs "
            f"[{lo}-{hi}]; {len(sub) - n_fail}/{len(sub)} cells inside, {ends}; range "
            f"{vals.min():.1f}-{vals.max():.1f}. COUNTERFACTUAL: the {other_name} rule would "
            f"return {other} on this same data" +
            ("" if status == other else
             f" -- *** THE TWO RULES DISAGREE HERE, so this gate's status is set by the RULE "
             f"CHOICE and not by the model; read the decision in band_src before quoting it") +
            f". ({BENCH[c]['src']})")

    # -- why a stacked-tower channel may sit below a standalone-prototype band ------------
    # Not a remedy, an explanation, and it changes no threshold. The as-modelled bands were set
    # from STANDALONE prototypes (a Large Office building, a Standalone Retail box). A channel
    # buried mid-tower is a different thermal object: almost its entire envelope is interior
    # partition to other conditioned floors, so it has near-zero roof, ground and (for interior
    # zones) facade load, and it inherits a central plant sized for the whole tower. Lower EUI
    # than a freestanding building of the same use is the expected direction, not a defect.
    # Whether that makes the band inapplicable as a PASS criterion for a stacked tower is a
    # DECISION for the user, not something this script may quietly assume -- so the gate above
    # still FAILS on the band as locked, and this line records the reading.
    tower = eui.groupby("channel")["eui_CFA_kWh_m2"].median()
    below = [c for c in TENANT if BENCH[c]["lo"] is not None and tower.get(c, np.nan) < BENCH[c]["lo"]]
    add("S9-BASIS", "Stacked-tower vs standalone-prototype EUI basis", "INFO",
        (f"channel(s) below their as-modelled floor: {', '.join(below)} "
         f"({'; '.join(f'{c} {tower[c]:.1f} vs floor {BENCH[c]['lo']:.0f}' for c in below)}). "
         if below else "no channel below its as-modelled floor. ") +
        "The locked bands come from STANDALONE prototypes; these channels are floors inside one "
        "tower, where most of the envelope is interior partition to other conditioned space and "
        "the plant is shared and centrally sized. A lower EUI is the physically expected "
        "direction. NO THRESHOLD HAS BEEN CHANGED -- whether the standalone band remains a valid "
        "PASS criterion for a stacked-tower channel is a decision to be taken explicitly. "
        "CORRECTED 2026-07-31 (re-derived from code, not taken on faith): the Leg-2 office "
        "precedent (135 [100-200], job 1054800) is computed on ALL FUELS, not restricted to any "
        "single meter -- _eui_from_sql() "
        "(Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_agg.py:333-345) calls calculate_eui() "
        "(Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py:257-350), which sums the SQL "
        "'End Uses (By Subcategory)' table over ALL fuel columns, excluding only m3 units (water) "
        "-- gas is in it. The Electricity:Facility / office_elec restriction lives on the DIURNAL "
        "path (Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:99-110) and never "
        "feeds the EUI at all (contrast :124-158). The real, larger discrepancy is elsewhere: the "
        "Leg-2 'office' EUI is a TOWER EUI, not a channel EUI -- its `unit` column literally reads "
        "'tower' (Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv, row "
        "office,all,tower,252,172.7), and calculate_eui() returns the energy and area of the "
        "WHOLE model. Leg-2 therefore never validated an office CHANNEL -- Leg-3 produces the "
        "project's first per-channel EUI.")

    # -- S9-EUI-EXPOSURE (INFO, T9-3 result) -- the "stacked channel" story, TESTED not invoked --
    # S9-BASIS above states a mechanism (a channel buried mid-tower has near-zero exterior
    # envelope, so a lower EUI is expected). That is an argument, not a measurement. The
    # falsifiable version: the "stacked channel" explanation predicts that of the three
    # band-carrying channels, the one with the LEAST envelope exposure per m2 of CFA shows the
    # LARGEST negative gap to its as-modelled floor, and the one with the MOST exposure shows the
    # smallest gap (office most buried -> largest gap; hotel least buried -> smallest gap).
    # 3rdJ_09X_envelope_exposure.py measured exposure_ratio = (ext_area_m2 + ground_area_m2) /
    # cfa_m2 per channel per cell from the SQL Surfaces/Zones tables, read-only, independently
    # cross-checked against EnergyPlus's own EnvelopeSummary total. This gate reads that CSV,
    # joins it to the EUI table, and reports the actual ranking -- it does not assume the
    # prediction holds. NOT PASS/FAIL: the prediction was tested by 3rdJ_09X_envelope_exposure.py
    # BEFORE this gate was written and came out FALSIFIED (wrong-signed, wrong order), so scoring
    # it PASS/FAIL here would either manufacture a 4th FAIL nobody asked for or silently launder a
    # rejected hypothesis into a PASS -- both wrong. INFO publishes the numbers and the verdict.
    exposure_csv = os.path.join(outdir, "step9_envelope_exposure.csv") if outdir else None
    if not exposure_csv or not os.path.isfile(exposure_csv):
        add("S9-EUI-EXPOSURE", "Envelope-exposure mechanism test (T9-3) vs band-floor gap", "INFO",
            f"step9_envelope_exposure.csv not found" +
            (f" under {outdir}" if outdir else "") +
            " -- run 3rdJ_09X_envelope_exposure.py first (read-only SQL pass over the 56 campaign "
            "cells). The stacked-channel mechanism test cannot be reported this run.")
    else:
        exp_df = pd.read_csv(exposure_csv)
        banded = [c for c in TENANT if BENCH[c]["lo"] is not None]  # office, retail, hotel
        e2 = eui[eui["channel"].isin(banded)].copy()
        e2["gap_pct"] = (e2["eui_CFA_kWh_m2"] - e2["band_lo"]) / e2["band_lo"] * 100.0
        m = exp_df.merge(
            e2[["cell_tag", "channel", "eui_CFA_kWh_m2", "band_lo", "gap_pct"]],
            on=["cell_tag", "channel"], how="inner")
        med_exp = m.groupby("channel")["exposure_ratio"].median()
        med_gap = m.groupby("channel")["gap_pct"].median()
        rho, pval = spearmanr(m["exposure_ratio"], m["gap_pct"])
        # The falsifiable claim is about direction (does higher exposure predict a SMALLER,
        # i.e. less negative, gap?), not about which channel is "first" by exposure alone --
        # so state the ordering AND whether it matches the office<retail<hotel prediction.
        predicted_seq = ["office", "retail", "hotel"]
        measured_seq = sorted(banded, key=lambda c: med_exp[c])
        matches_prediction = (measured_seq == predicted_seq)
        n_cells = int(exp_df["cell_tag"].nunique())
        order_str = " < ".join(f"{c} ({med_exp[c]:.3f})" for c in measured_seq)
        measured_str = " < ".join(measured_seq)
        gap_str = "; ".join(f"{c} {med_gap[c]:+.1f}%" for c in predicted_seq if c in med_gap.index)
        add("S9-EUI-EXPOSURE", "Envelope-exposure mechanism test (T9-3) vs band-floor gap", "INFO",
            f"median exposure_ratio by channel: {order_str} (n={n_cells} cells). Median gap to "
            f"band floor: {gap_str}. Spearman(exposure_ratio, signed gap-to-floor) pooled over "
            f"the 3 banded channels, rho = {rho:+.3f} (p={pval:.3f}, n={len(m)}). PREDICTED "
            f"office < retail < hotel (least-exposed channel = largest negative gap); MEASURED "
            f"{measured_str} -- " +
            ("the prediction HOLDS" if matches_prediction else
             "the prediction is CONTRADICTED, in 56/56 cells (hotel is the LEAST-exposed of the "
             "three, not the most, and sits CLOSEST to its floor, not furthest) -- the negative "
             "pooled rho is the wrong sign for the 'stacked channel buries the envelope' story. "
             "TESTED AND REFUTED: the 3 EUI FAIL gates above are not explained by this mechanism "
             "and remain unexplained defects.") +
            " LIMIT: geometry varies only between the Tall and SuperTall archetypes in this "
            "campaign, so exposure_ratio takes only 2 distinct values per channel -- the "
            "per-cell rho moves because EUI re-orders across scenarios, not because exposure "
            "does. The inference is therefore over 2 geometries, not 56 independent ones.")

    # -- S9-EUI-TOWER-INFO (INFO) -- the tower-level EUI, on both bases, as context only --------
    # S9-EUI-TOWER (PASS/FAIL against the Leg-2 172.7 [100-200] tower precedent) was considered
    # and NOT created: the Leg-2 reference number is corrupted, not merely uncertain. Leg-2's
    # calculate_eui() (Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py:293-299) filters its
    # SQL query on TableName only, never on ReportName. EnergyPlus writes a table named
    # "End Uses By Subcategory" under TWO distinct ReportNames -- AnnualBuildingUtilityPerformance-
    # Summary (GJ, annual energy) and DemandEndUseComponentsSummary (W, peak demand) -- and
    # calculate_eui() sums both as if they were all kWh. Measured directly on a v24.2.0 SQL file
    # from this campaign (B_central__Tall__MTL): 7,837,731 kWh legitimate + 5,533,372 W miscounted
    # as kWh = 13,371,103 -> inflation factor ~1.706x. Cross-check: 172.7 / 1.706 = 101.2, within
    # ~1% of the ~100.4 measured here on the same tower once the defect is removed. This is
    # read-only context, not a Leg-2 recalculation -- Leg-2 is closed and paper-ready, and
    # reopening it is a user decision, out of scope here (Leg2_2-split/ was not modified).
    energy_kwh = meta["site_energy_GJ"] * 1e9 * J_TO_KWH
    tower_area_gross = meta["total_building_area_m2"]
    tower_area_tenant_cfa = sum(meta[f"area_{c}_m2"] for c in TENANT)
    eui_tower_abups = (energy_kwh / tower_area_gross)
    # "CFA locataires sommee": tenant-channel ENERGY only (not the whole-building energy)
    # divided by the sum of tenant-channel CFA -- the area-weighted average of the four tenant
    # channels' own EUI, i.e. what a stock database quoting "the tower's EUI on a CFA basis"
    # would report if it only ever measured the tenant floors.
    tenant_eui = eui[eui["channel"].isin(TENANT)]
    per_cell = tenant_eui.groupby("cell_tag").apply(
        lambda g: (g["energy_GJ"].sum() * 1e9 * J_TO_KWH) / g["area_m2"].sum(),
        include_groups=False)
    eui_tower_cfa_tenant = per_cell
    add("S9-EUI-TOWER-INFO", "Tower-level EUI, both bases (context, NOT scored PASS/FAIL)", "INFO",
        f"ABUPS gross basis (site_energy_GJ / total_building_area_m2, all {len(meta)} cells): "
        f"median {eui_tower_abups.median():.1f} kWh/m2/yr (range "
        f"{eui_tower_abups.min():.1f}-{eui_tower_abups.max():.1f}). Tenant-CFA-summed basis "
        f"(sum of the 4 tenant channels' own energy / sum of their CFA, {len(per_cell)} cells): "
        f"median {eui_tower_cfa_tenant.median():.1f} kWh/m2/yr (range "
        f"{eui_tower_cfa_tenant.min():.1f}-{eui_tower_cfa_tenant.max():.1f}). The Leg-2 office "
        f"precedent band [100-200] (central 135, from NECB2020/90.1-2019 DOE-PNNL literature) is "
        f"cited here as CONTEXT ONLY, never as a PASS/FAIL criterion. Note the two are different "
        f"objects: the band is literature and is sound; 172.7 is the value Leg-2 MEASURED against "
        f"it, and it is that measured number -- not the band -- that is "
        f"inflated by a factor of ~1.706x by a "
        f"calculate_eui() defect (Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py:293-299 "
        f"filters on TableName without ever filtering ReportName, so the same-named 'End Uses By "
        f"Subcategory' table from the DemandEndUseComponentsSummary report -- which is in WATTS -- "
        f"gets summed in as if it were kWh); 172.7 / 1.706 = 101.2, within ~1% of the ~100 kWh/m2/yr "
        f"measured here on the same tower once that defect is removed. Leg2_2-split/ was read only, "
        f"never modified; correcting the Leg-2 number is a user decision outside this task's scope.")

    # -- energy share vs parsed occupiable share -----------------------------------------
    # The "+/-2 pp EUI-share" gate (dr_L3-10, explicitly project-novel -- ASHRAE 211 suggests the
    # comparison, no code enforces it) CANNOT be a PASS/FAIL criterion here, and saying so is more
    # useful than shipping a gate that must fail. Energy share equals area share only when every
    # channel has the same EUI. This building's own as-modelled bands put hotel at 240 and retail
    # at 110 kWh/m2/yr -- a factor 2.2 -- so a hotel occupying 24.9 % of the area is REQUIRED by
    # arithmetic to exceed 24.9 % of the energy, by far more than 2 pp. Widening the tolerance
    # until it passes is the move this project has banned (never relax a threshold to erase a
    # FAIL); the correct remedy for a criterion that cannot hold is re-specification, not a wider
    # band. So: reported as INFO with the implied EUI ratio, and the falsifiable part of the
    # original intent -- that the parsed areas actually account for the building -- is kept as its
    # own gate below, where it can genuinely fail.
    worst = eui.loc[eui["share_delta_pp"].abs().idxmax()]
    n_out = int((eui["share_delta_pp"].abs() > 2.0).sum())
    ratios = "; ".join(
        f"{c} {eui.loc[eui['channel'] == c, 'energy_share_pct'].median() / eui.loc[eui['channel'] == c, 'area_share_pct'].median():.2f}x"
        for c in TENANT)
    add("S9-SHARE", "Energy share vs parsed occupiable share (dr_L3-10 +/-2 pp)", "INFO",
        f"{len(eui) - n_out}/{len(eui)} channel-cells within +/-2 pp; worst {worst['channel']} on "
        f"{worst['cell_tag']} at {worst['share_delta_pp']:+.2f} pp (energy "
        f"{worst['energy_share_pct']:.2f} % vs area {worst['area_share_pct']:.2f} %). "
        f"NOT scored PASS/FAIL: energy share can equal area share only if all channels share one "
        f"EUI, and the as-modelled bands themselves span 110-240 kWh/m2/yr. Median energy/area "
        f"ratio per channel: {ratios} -- these ARE the relative EUIs, and they are judged against "
        f"their own bands by the S9-EUI-* gates. Shares are PARSED per cell from the IDF + SQL "
        f"(Defaut 7), never the doc constants.")

    # -- the falsifiable half: do the parsed areas actually account for the building? -----
    n_bad = 0
    details = []
    for _, r in meta.iterrows():
        parsed = float(sum(r[f"area_{c}_m2"] for c in ALL_CH)) + float(r["unclassified_area_m2"])
        rel = abs(parsed - float(r["total_building_area_m2"])) / float(r["total_building_area_m2"])
        unc = float(r["unclassified_area_m2"]) / float(r["total_building_area_m2"])
        if rel > 1e-3 or unc > 0.01:
            n_bad += 1
            details.append(f"{r['cell_tag']} (residual {rel * 100:.3f} %, unclassified {unc * 100:.2f} %)")
    add("S9-AREA", "Parsed channel areas account for the whole building",
        "PASS" if n_bad == 0 else "FAIL",
        f"{len(meta) - n_bad}/{len(meta)} cells: Sigma(channel areas) + unclassified == "
        f"ABUPS total building area within 0.1 %, and unclassified < 1 % of gross. "
        f"This fails if the Tag-2 census misses a Space -- the part of the +/-2 pp intent that "
        f"is actually falsifiable. " + ("Offenders: " + "; ".join(details[:3]) if details else ""))

    # -- peak-hour direction, per channel, on the circular mean --------------------------
    # Scored on the OCCUPANCY series. The Step-9 doc's "peak-hour direction" row asks when each
    # channel's occupants peak; for the three commercial channels the energy series answers that
    # too (they modulate People + Lights + Equipment), but for residential it cannot -- OD-7D
    # leaves residential lights and plugs on the flat NECB baseline, so its ENERGY peak is an
    # artefact of the baseline, not of behaviour. Scoring residential on energy would fail a
    # correct model for a documented reason. The energy peak is reported beside it, and the gap
    # is exactly D-20 made measurable.
    # A mean hour is quotable only when the profile HAS a direction (R >= R_MIN). Channels whose
    # occupancy is near-antipodal -- residential (home overnight, away midday) and hotel (guest
    # rooms overnight) -- do not, and are scored on a shape contrast that survives instead.
    R_MIN = 0.30
    WINDOW = {"office": (9, 18), "retail": (10, 20)}
    for c in TENANT:
        sub = ls[ls["channel"] == c]
        h = sub["occ_wd_peak_hour_circular"].dropna()
        he = sub["wd_peak_hour_circular"].dropna()
        R = sub["occ_wd_R"].dropna()
        am = sub["occ_wd_peak_hour_argmax"].dropna()
        if not len(h):
            add(f"S9-PEAK-{c}", f"Weekday occupancy peak-hour direction ({c})", "FAIL",
                "no occupancy series in agg_diurnal.csv -- re-run §8E (it must emit metric=people)")
            continue
        if c in WINDOW:
            lo, hi = WINDOW[c]
            ok = int(((h >= lo) & (h <= hi)).sum())
            weak = int((R < R_MIN).sum())
            add(f"S9-PEAK-{c}", f"Weekday OCCUPANCY peak hour ({c}, {lo}-{hi} h)",
                "PASS" if (ok == len(h) and weak == 0) else "FAIL",
                f"{ok}/{len(h)} cells inside; circular mean {h.mean():.2f} h "
                f"(range {h.min():.2f}-{h.max():.2f}), argmax {am.median():.0f} h, "
                f"concentration R = {R.mean():.3f} (>= {R_MIN} required before a mean hour means "
                f"anything; {weak} cells below). Same channel ENERGY peak: {he.mean():.2f} h.")
            continue
        ratio = (sub["occ_wd_evening"] / sub["occ_wd_midday"])
        ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
        if c == "residential":
            # Default_NECB carries NO injected residential occupancy -- it keeps the code
            # schedule, at the code People/Area count. Scoring it here would ask the baseline
            # to exhibit the behaviour the injection is supposed to create. It is reported as
            # the contrast instead, which is the more informative use of it.
            inj = sub[sub["scenario"] != "Default_NECB"]
            base = sub[sub["scenario"] == "Default_NECB"]
            ratio = (inj["occ_wd_evening"] / inj["occ_wd_midday"])
            ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
            bratio = (base["occ_wd_evening"] / base["occ_wd_midday"]).replace(
                [np.inf, -np.inf], np.nan).dropna()
            ok = int((ratio > 1.0).sum())
            add(f"S9-PEAK-{c}",
                "Weekday residential occupancy: evening (17-22 h) above midday (11-14 h), injected cells",
                "PASS" if ok == len(ratio) else "FAIL",
                f"{ok}/{len(ratio)} injected cells; evening/midday ratio median "
                f"{ratio.median():.2f} (range {ratio.min():.2f}-{ratio.max():.2f}); the "
                f"un-injected NECB baseline sits at {bratio.median():.2f} "
                f"(midday-dominant, argmax 09 h) -- see S9-INJECTION. Deliberately NOT scored on a mean "
                f"hour: AT_HOME occupancy is near-antipodal (maximum overnight while people sleep "
                f"at home, minimum around 10 h), so R = {R.mean():.3f} and the mean hour wanders "
                f"over almost the whole clock across behaviourally identical cells. The doc's "
                f"'resid 15-22 h' describes the evening RISE, and that is what this measures.")
        else:
            add(f"S9-PEAK-{c}", f"Weekday occupancy shape ({c})", "INFO",
                f"hotel guest rooms are occupied overnight by construction (s(t) plateau "
                f"22-06 h), so no daytime window applies; argmax {am.median():.0f} h, "
                f"R = {R.mean():.3f}, evening/midday ratio {ratio.median():.2f}, "
                f"energy peak {he.mean():.2f} h")

    # -- what the residential injection actually does to the occupancy shape --------------
    rr = ls[ls["channel"] == "residential"]
    inj = rr[rr["scenario"] != "Default_NECB"]
    base = rr[rr["scenario"] == "Default_NECB"]
    if len(inj) and len(base):
        ri = (inj["occ_wd_evening"] / inj["occ_wd_midday"]).replace([np.inf, -np.inf], np.nan).dropna()
        rb = (base["occ_wd_evening"] / base["occ_wd_midday"]).replace([np.inf, -np.inf], np.nan).dropna()
        # PASS/FAIL, never a soft INFO. If the injected cells stopped being evening-dominant,
        # or stopped differing from the code baseline, the residential channel would have
        # quietly become a rescaled NECB schedule -- the exact failure this project keeps
        # meeting -- and a gate that can only say PASS or INFO would wave it through.
        # (Caught 2026-07-31 by 3rdJ_09_gate_falsifiability.py, which found this gate unable
        # to fail: removing the shape change left it reporting INFO.)
        evaluable = len(rb) > 0 and len(ri) > 0
        add("S9-INJECTION", "Residential injection changes the occupancy SHAPE, not just its level",
            ("PASS" if (ri.median() > 1.0 > rb.median()) else "FAIL") if evaluable else "INFO",
            f"NECB code baseline: evening/midday occupancy ratio {rb.median():.2f} "
            f"(midday-dominant, argmax {base['occ_wd_peak_hour_argmax'].median():.0f} h). "
            f"GSS-injected cells: {ri.median():.2f} (range {ri.min():.2f}-{ri.max():.2f}, argmax "
            f"{inj['occ_wd_peak_hour_argmax'].median():.0f} h). The injection flips the channel "
            f"from midday-dominant to evening-dominant -- a change of SHAPE, which a level-only "
            f"rescaling of the code schedule could not produce. This is the cleanest sim-side "
            f"evidence that the residential channel carries behaviour and not merely a magnitude, "
            f"and it is exactly the claim the thesis rests on."
            + ("" if evaluable else " NOT EVALUABLE: this campaign carries no Default_NECB "
                                   "baseline cell to contrast against."))

    # -- the finding that the Legs 1-2 headline result cannot be reproduced here ----------
    r = ls[ls["channel"] == "residential"]
    add("S9-RESID-EVENING", "Residential evening ENERGY peak (the Legs 1-2 headline)", "INFO",
        f"NOT REPRODUCIBLE IN LEG 3, by construction. Residential energy peaks at "
        f"{r['wd_peak_hour_circular'].mean():.2f} h (circular mean, R = {r['wd_R'].mean():.3f}), "
        f"not in the evening, because OD-7D leaves residential lights and plug loads on the flat "
        f"NECB baseline -- the very loads that produced the evening peak in Legs 1 and 2. The "
        f"OCCUPANCY still shows the evening rise (see S9-PEAK-residential), so the behavioural "
        f"signal is intact upstream; it simply has no route into energy. This is D-20 at its "
        f"sharpest, and it belongs in the manuscript: any Leg-3 claim about residential evening "
        f"ENERGY demand would be unsupported by this model.")

    # -- D-20 made measurable: how far does energy timing follow occupancy timing? -------
    gaps = []
    for c in TENANT:
        sub = ls[ls["channel"] == c]
        if sub["occ_wd_peak_hour_circular"].notna().any():
            d = (sub["wd_peak_hour_circular"] - sub["occ_wd_peak_hour_circular"]).abs()
            d = np.minimum(d, 24 - d)
            gaps.append(f"{c} {d.mean():.2f} h")
    add("S9-D20", "Energy-vs-occupancy peak lag per channel (D-20 evidence)", "INFO",
        "; ".join(gaps) + ". The three commercial channels modulate People + Lights + Equipment, "
        "so their energy timing tracks their occupancy. Residential modulates People only "
        "(OD-7D), so its energy timing is set by the flat NECB baseline instead. That gap is "
        "the asymmetry D-20 predicted, here as a measured number rather than an argument.")

    # -- weekend structure ---------------------------------------------------------------
    o = ls[ls["channel"] == "office"]
    n_ok = int((o["we_mean_kW"] < o["wd_mean_kW"]).sum())
    add("S9-WE-office", "Weekend structure: office WE < WD",
        "PASS" if n_ok == len(o) else "FAIL",
        f"{n_ok}/{len(o)} cells have weekend mean below weekday mean "
        f"(median ratio {float((o['we_mean_kW'] / o['wd_mean_kW']).median()):.3f})")

    # -- G8o / G8r / G8h: non-degeneracy + damped bound -----------------------------------
    for ch, (lo_tag, mid_tag, hi_tag) in SENS.items():
        gid = {"office": "G8o", "retail": "G8r", "hotel": "G8h"}[ch]
        sub = scen[(scen["channel"] == ch) & (scen["scenario"].isin([lo_tag, mid_tag, hi_tag]))]
        piv = sub.pivot_table(index=["building", "city"], columns="scenario", values="energy_GJ")
        if not {lo_tag, mid_tag, hi_tag}.issubset(piv.columns):
            add(gid, f"{gid} -- {ch} lever non-degenerate", "FAIL",
                f"missing scenario columns: have {sorted(piv.columns)}")
            continue
        spread = (piv[hi_tag] - piv[lo_tag]).abs() / piv[mid_tag] * 100.0
        degenerate = int((spread < 1e-6).sum())
        mono = (((piv[lo_tag] <= piv[mid_tag]) & (piv[mid_tag] <= piv[hi_tag])) |
                ((piv[lo_tag] >= piv[mid_tag]) & (piv[mid_tag] >= piv[hi_tag])))
        add(gid, f"{gid} -- {ch} lever non-degenerate + monotonic",
            "PASS" if (degenerate == 0 and bool(mono.all())) else "FAIL",
            f"spread |opt-cons|/central = {spread.min():.3f}-{spread.max():.3f} % over "
            f"{len(piv)} building-city pairs; monotonic in {int(mono.sum())}/{len(piv)}; "
            f"lever {LEVER_ORDER[ch]}. Degenerate cells: {degenerate}. "
            f"Sim-side evidence, not input-side (caveat 7).")

    # -- coincidence: the stacked peak must be below the sum of channel peaks -------------
    cf = ls["coincidence_factor"].dropna()
    add("S9-COINC", "Coincidence factor < 1 (diversity)",
        "PASS" if bool((cf < 1.0).all()) else "FAIL",
        f"{int((cf < 1.0).sum())}/{len(cf)} cells; median {cf.median():.3f}, "
        f"range {cf.min():.3f}-{cf.max():.3f}. Below 1 means the four channels do not peak "
        f"together -- the mixed-use diversity argument, measured rather than asserted.")

    # -- longitudinal: the era axis must move at all --------------------------------------
    # S9D-6/T9-7: hotel is carved out of the PASS/FAIL loop below. Hotel is NOT injected in
    # Y2005/Y2010/Y2015 (DELIBERATE_CHANNEL_EXCEPTIONS, 3rdJ_08D_campaign_cells.py -- see
    # S9-LONG-UNINJECTED just below), only in Y2022. So the "spread across the four eras" this
    # loop measures for every other channel is, for hotel, NOT a hotel behaviour trajectory: it
    # mixes (a) an injection on/off STEP between Y2015 and Y2022 and (b) whatever thermal
    # coupling the other three channels' genuine era-to-era changes push through shared
    # partitions/plant of the same tower. No hotel behaviour enters it at all. A PASS/FAIL gate
    # that cannot distinguish "hotel behaviour changed" from "injection got switched on
    # elsewhere in the tower" is exactly the failure shape this project has spent three days
    # finding and removing (S9-INJECTION, S9-SHARE) -- so hotel drops to INFO here, and the
    # falsifiable half of the original intent (hotel really is absent pre-2022) becomes its own
    # gate, S9-LONG-UNINJECTED, which CAN fail.
    for c in TENANT:
        sub = lon[lon["channel"] == c]
        if sub.empty:
            continue
        rng = sub.groupby(["building", "city"])["energy_pct_vs_2005"].agg(lambda s: s.max() - s.min())
        if c == "hotel":
            add(f"S9-LONG-{c}", f"Longitudinal 2005->2022 non-degenerate ({c})", "INFO",
                f"energy spread across the four cycles = {rng.min():.3f}-{rng.max():.3f} pp per "
                f"building-city pair -- NOT a hotel-behaviour trajectory: hotel carries no "
                f"era-varying occupancy product before Y2022 (S9D-5, DELIBERATE_CHANNEL_"
                f"EXCEPTIONS). Read this residual as a MEASURE OF INTER-CHANNEL THERMAL COUPLING "
                f"within one tower -- the Y2015->Y2022 injection on/off step plus whatever the "
                f"other three channels' real changes push through shared partitions/plant -- "
                f"not as hotel behaviour. See S9-LONG-UNINJECTED for the falsifiable claim that "
                f"hotel is genuinely absent pre-2022.")
            continue
        add(f"S9-LONG-{c}", f"Longitudinal 2005->2022 non-degenerate ({c})",
            "PASS" if bool((rng > 1e-6).all()) else "FAIL",
            f"energy spread across the four cycles = {rng.min():.3f}-{rng.max():.3f} pp "
            f"per building-city pair")

    # -- S9-LONG-UNINJECTED: hotel really is absent from the three historical eras ---------
    # Two independent checks, per the task spec: (1) the SPEC says hotel is excluded
    # (_expected_channels() / DELIBERATE_CHANNEL_EXCEPTIONS) and (2) the BUILT campaign cells
    # confirm it (no cell's `channels` dict actually carries a hotel key for those scenarios).
    # Checking only (1) would validate the constant against itself; checking only (2) would miss
    # a spec regression. Both must hold. Constant is READ from Step-8's module (see
    # _load_campaign_cells_module docstring), never copied -- an import failure FAILS loudly,
    # it never passes silently.
    HIST_ERAS = ["Y2005", "Y2010", "Y2015"]
    try:
        _cc = _load_campaign_cells_module()
        bad_expected = [e for e in HIST_ERAS if "hotel" in _cc._expected_channels(e)]
        built_cells = _cc.build_campaign_cells(REPO_ROOT)
        hist_cells = [c for c in built_cells if c["scenario"] in HIST_ERAS]
        bad_built = sorted(c["tag"] for c in hist_cells if "hotel" in c["channels"])
        ok = not bad_expected and not bad_built
        add("S9-LONG-UNINJECTED", "Hotel channel absent from Y2005/Y2010/Y2015 (S9D-5)",
            "PASS" if ok else "FAIL",
            (f"_expected_channels() excludes hotel from all three historical eras "
             f"(DELIBERATE_CHANNEL_EXCEPTIONS in 3rdJ_08D_campaign_cells.py) and all "
             f"{len(hist_cells)} built historical-era campaign cells confirm it: 0 carry a "
             f"'hotel' key in their channels dict. "
             if ok else
             f"MISMATCH -- spec still lists hotel as expected for {bad_expected or '[]'}; built "
             f"cells still wiring a hotel channel: {bad_built or '[]'}. ") +
            "This is the assertion S9-LONG-hotel (now INFO) can no longer make on its own.")
    except Exception as exc:
        add("S9-LONG-UNINJECTED", "Hotel channel absent from Y2005/Y2010/Y2015 (S9D-5)", "FAIL",
            f"could not import 3rdJ_08D_campaign_cells.py to check DELIBERATE_CHANNEL_EXCEPTIONS "
            f"/ _expected_channels() / build_campaign_cells() -- refusing to assert "
            f"uninjected-ness silently: {type(exc).__name__}: {exc}")

    # -- provenance / hygiene ------------------------------------------------------------
    add("S9-PLATFORM", "Single platform across compared cells",
        "PASS" if meta["PLATFORM"].nunique() == 1 else "FAIL",
        f"PLATFORM = {sorted(meta['PLATFORM'].unique())}; cross-platform comparison is blocked "
        f"by design (Step-8 C-bis)")
    add("S9-CELLS", "All 56 campaign cells aggregated",
        "PASS" if len(meta) == 56 else "FAIL", f"{len(meta)}/56 cells present in agg_meta.csv")
    add("S9-SCHEMA", "All cells share one output schema",
        "PASS" if meta["OUTPUT_SCHEMA_HASH"].nunique() == 1 else "FAIL",
        f"OUTPUT_SCHEMA_HASH = {sorted(meta['OUTPUT_SCHEMA_HASH'].dropna().unique())}")
    fb = meta[[c for c in meta.columns if c.startswith("fallback_hours_")]].sum()
    add("S9-FALLBACK", "Allocation fallback hours (area share) are rare", "INFO",
        "; ".join(f"{k.replace('fallback_hours_', '')}={int(v)}" for k, v in fb.items()) +
        f" summed over {len(meta)} cells x 8760 h. Non-zero is expected at hours with no coil "
        f"load; it is reported rather than hidden.")
    return G


# ------------------------------------------------------------------ figures ---
def _save(fig, outdir, fname):
    p = os.path.join(outdir, "figures", fname)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_eui(eui, outdir):
    fig, ax = plt.subplots(figsize=(9, 4.6))
    xs = np.arange(len(TENANT))
    for i, c in enumerate(TENANT):
        s = eui[eui["channel"] == c]["eui_CFA_kWh_m2"]
        ax.boxplot(s.dropna(), positions=[i], widths=0.5, patch_artist=True,
                   boxprops=dict(facecolor=THEME[c], alpha=.55), medianprops=dict(color="k"))
        b = BENCH[c]
        if b["lo"] is not None:
            ax.add_patch(plt.Rectangle((i - .32, b["lo"]), .64, b["hi"] - b["lo"],
                                       color="green", alpha=.10, zorder=0))
            ax.hlines(b["central"], i - .32, i + .32, color="green", lw=1.4, zorder=1)
    ax.set_xticks(xs)
    ax.set_xticklabels(TENANT)
    ax.set_ylabel("EUI [kWh/m$^2$/yr], CFA basis")
    ax.set_title("Step 9 §R1 — per-channel EUI vs as-modelled band (green) · CFA basis · all 56 cells")
    ax.grid(alpha=.3, axis="y")
    return _save(fig, outdir, "fig_eui_4ch.png")


def fig_diurnal(diur, outdir, cell=None):
    cell = cell or sorted(diur["cell_tag"].unique())[0]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, season in zip(axes, ("winter", "summer")):
        # 🔴 `metric` MUST be filtered here. agg_diurnal.csv carries two metrics per
        # cell/season/daytype/channel -- `energy_W` and `people` -- so an unfiltered slice returns
        # 48 rows, not 24, and the `len(y) != 24` guard below then skips EVERY channel silently.
        # The figure saved without error and shipped into the manuscript completely empty: axes,
        # grid and an empty legend box, no data. `build_loadshape` already filters this way
        # (see :331); only this figure did not. Fixing it changes no reported number, because every
        # table and gate reads `build_loadshape`, never this function.
        d = diur[(diur["cell_tag"] == cell) & (diur["season"] == season) & (diur["daytype"] == "WD")
                 & (diur.get("metric", "energy_W") == "energy_W")]
        bottom = np.zeros(24)
        for c in ALL_CH:
            y = d[d["channel"] == c].sort_values("hour")["W"].to_numpy() / 1000.0
            if len(y) != 24:
                continue
            ax.fill_between(range(24), bottom, bottom + y, label=c, color=THEME[c], alpha=.85)
            bottom += y
        ax.set_title(f"{season} · weekday"), ax.set_xlabel("hour"), ax.grid(alpha=.3)
        ax.set_xticks(range(0, 24, 3))
    axes[0].set_ylabel("stacked load [kW]")
    axes[1].legend(fontsize=7, loc="upper right", ncol=2)
    fig.suptitle(f"Step 9 §R2 — coincident four-channel diurnal load · {cell}")
    return _save(fig, outdir, "fig_diurnal_4ch.png")


def fig_peakhour(ls, outdir):
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    for i, c in enumerate(TENANT):
        h = ls[ls["channel"] == c]["wd_peak_hour_circular"].dropna()
        ax.scatter(h, np.full(len(h), i) + np.random.default_rng(0).normal(0, .05, len(h)),
                   s=22, color=THEME[c], alpha=.7)
        if len(h):
            ax.scatter([circular_mean_hour(np.ones(1) * 0) if False else h.mean()], [i],
                       marker="|", s=600, color="k", zorder=5)
    ax.set_yticks(range(len(TENANT)))
    ax.set_yticklabels(TENANT)
    ax.set_xlim(0, 24), ax.set_xticks(range(0, 25, 3)), ax.grid(alpha=.3, axis="x")
    ax.set_xlabel("weekday peak hour [h] — load-weighted CIRCULAR mean (caveat 3)")
    ax.set_title("Step 9 §R2 — peak timing per channel, all 56 cells")
    return _save(fig, outdir, "fig_peakhour_4ch.png")


def fig_scenario(scen, outdir):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, (ch, tags) in zip(axes, SENS.items()):
        sub = scen[(scen["channel"] == ch) & (scen["scenario"].isin(tags))]
        piv = sub.pivot_table(index=["building", "city"], columns="scenario",
                              values="energy_pct_vs_Bcentral")
        for tag in tags:
            if tag in piv.columns:
                ax.scatter([tag] * len(piv), piv[tag], s=40, color=THEME[ch], alpha=.8)
        ax.axhline(0, color="k", lw=.8)
        ax.set_title(f"{ch} lever  {LEVER_ORDER[ch]}", fontsize=9)
        ax.tick_params(axis="x", rotation=20, labelsize=7), ax.grid(alpha=.3, axis="y")
    axes[0].set_ylabel("channel energy Δ% vs B_central")
    fig.suptitle("Step 9 §R3 — one-at-a-time scenario response (G8o / G8r / G8h), sim-side evidence")
    return _save(fig, outdir, "fig_scenario_4ch.png")


def fig_longitudinal(lon, outdir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for c in TENANT:
        for ax, col, lab in ((axes[0], "energy_pct_vs_2005", "energy Δ% vs 2005"),
                             (axes[1], "midday_share", "weekday midday share")):
            g = lon[lon["channel"] == c].groupby("scenario")[col].mean().reindex(ERAS)
            ax.plot(ERAS, g.to_numpy(), "-o", color=THEME[c], label=c)
            ax.set_ylabel(lab), ax.grid(alpha=.3)
    axes[1].legend(fontsize=8)
    fig.suptitle("Step 9 §R4 — longitudinal 2005→2022, mean over building × city")
    return _save(fig, outdir, "fig_longitudinal_4ch.png")


# -------------------------------------------------------------------- html ----
def _embed(path) -> str:
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def write_html(outdir, eui, ls, scen, lon, gates, meta, figs, agg_dir):
    n = {k: sum(1 for g in gates if g["status"] == k) for k in ("PASS", "WARN", "FAIL", "INFO")}
    css = """body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#fbfbfd;color:#1a1a1a}
    .w{max-width:1120px;margin:0 auto;padding:28px 22px 70px}h1{font-size:26px;margin:.2em 0}
    h2{margin-top:2em;border-bottom:2px solid #e3e3ea;padding-bottom:.25em}
    table{border-collapse:collapse;width:100%;font-size:13px;margin:.8em 0}
    th,td{border:1px solid #dfdfe6;padding:5px 8px;text-align:right}th{background:#f0f0f5;text-align:left}
    td:first-child,th:first-child{text-align:left}
    .PASS{color:#0a7d28;font-weight:600}.FAIL{color:#c00;font-weight:700}.INFO{color:#666}.WARN{color:#b8860b;font-weight:600}
    .k{display:inline-block;padding:3px 11px;margin-right:7px;border-radius:12px;background:#eee;font-size:13px}
    img{max-width:100%;border:1px solid #e0e0e8;border-radius:6px;margin:.5em 0}
    .note{background:#fff7e6;border-left:4px solid #e0a800;padding:10px 14px;margin:1em 0;font-size:13.5px}
    code{background:#f2f2f7;padding:1px 5px;border-radius:3px;font-size:12.5px}"""

    def tbl(df, cols=None, fmt=2, n_rows=None):
        d = df[cols] if cols else df
        if n_rows:
            d = d.head(n_rows)
        h = "".join(f"<th>{c}</th>" for c in d.columns)
        body = ""
        for _, r in d.iterrows():
            body += "<tr>" + "".join(
                f"<td>{v:.{fmt}f}</td>" if isinstance(v, (int, float, np.floating)) and not isinstance(v, bool)
                else f"<td>{v}</td>" for v in r) + "</tr>"
        return f"<table><tr>{h}</tr>{body}</table>"

    gate_rows = "".join(
        f"<tr><td><code>{g['gate']}</code></td><td>{g['name']}</td>"
        f"<td class='{g['status']}'>{g['status']}</td><td style='text-align:left'>{g['detail']}</td></tr>"
        for g in gates)

    eui_med = (eui.groupby("channel")
               .agg(n=("eui_CFA_kWh_m2", "size"),
                    eui_CFA_median=("eui_CFA_kWh_m2", "median"),
                    eui_CFA_min=("eui_CFA_kWh_m2", "min"),
                    eui_CFA_max=("eui_CFA_kWh_m2", "max"),
                    eui_GFAshare_median=("eui_GFAshare_kWh_m2", "median"),
                    energy_share_pct=("energy_share_pct", "median"),
                    area_share_pct=("area_share_pct", "median"),
                    share_delta_pp=("share_delta_pp", "median"))
               .reset_index())
    ls_med = (ls[ls["channel"].isin(TENANT)].groupby("channel")
              .agg(peak_kW=("peak_kW", "median"),
                   wd_peak_hour=("wd_peak_hour_circular", "mean"),
                   wd_midday_kW=("wd_midday_kW", "median"),
                   wd_night_kW=("wd_night_kW", "median"),
                   we_over_wd=("we_mean_kW", "median")).reset_index())

    figs_html = "".join(
        f"<h3 style='font-size:15px;margin-bottom:.2em'>{t}</h3><img src='{_embed(p)}'>"
        f"<p style='font-size:12.5px;color:#666;margin-top:.1em'>{c}</p>"
        for t, p, c in figs)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>3J Leg-3 — Step 9 : Activity-Driven End-Use Loads (4 channels)</title><style>{css}</style></head><body><div class="w">
<h1>3J Leg-3 — Step 9 · Activity-Driven End-Use Loads</h1>
<p style="color:#666;margin-top:0">Residential + Office + Retail + Hotel in one stacked mixed-use tower ·
generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · source <code>{agg_dir}</code></p>
<p><span class="k">cells {len(meta)}/56</span><span class="k">EnergyPlus {meta['energyplus_version'].iloc[0]}</span>
<span class="k">platform {meta['PLATFORM'].iloc[0]}</span><span class="k">schema {meta['OUTPUT_SCHEMA_HASH'].iloc[0]}</span></p>
<p><span class="k PASS">PASS {n['PASS']}</span><span class="k WARN">WARN {n['WARN']}</span>
<span class="k FAIL">FAIL {n['FAIL']}</span><span class="k INFO">INFO {n['INFO']}</span></p>

<div class="note"><b>Read the basis before the number.</b> EUI is given on two bases and they are not
interchangeable. <b>CFA</b> divides a channel's energy by its own conditioned floor area — the
thermodynamic reading, and the one the as-modelled PASS bands apply to. <b>GFA-share</b> adds the
channel's area-prorated share of service/MEP and exterior lighting and divides by its share of gross
— the basis SCIEU/CEUD stock figures are quoted on, used here for the INFO comparison only.
CFA typically reads higher. Every floor area behind these numbers is parsed per cell from the IDF and
the EnergyPlus SQL, never taken from a documented constant.</div>

<h2>§R1 — EUI per channel</h2>
{tbl(eui_med, fmt=2)}
<p style="font-size:13px;color:#555">Bands: office {BENCH['office']['lo']}–{BENCH['office']['hi']} ·
retail {BENCH['retail']['lo']}–{BENCH['retail']['hi']} · hotel {BENCH['hotel']['lo']}–{BENCH['hotel']['hi']}
kWh/m²/yr (as-modelled, PASS criterion). Residential has no as-modelled band — the SHEU HighRise
figure is context only, because a tower apartment is not the SHEU stock basis.</p>

<h2>§R2 — Load shape, peak timing, coincidence</h2>
{tbl(ls_med, fmt=2)}
<p style="font-size:13px;color:#555">Peak hours are load-weighted <b>circular</b> means. An
arithmetic mean of a bimodal morning/evening distribution returns a number no household experiences —
the 2J lesson behind caveat 3.</p>

<h2>§R3 — Scenario response (G8o / G8r / G8h)</h2>
{tbl(scen[scen['scenario'].isin([t for v in SENS.values() for t in v])].groupby(['channel','scenario'], as_index=False)['energy_pct_vs_Bcentral'].mean(), fmt=3)}

<h2>§R4 — Longitudinal 2005 → 2022</h2>
{tbl(lon.groupby(['channel','scenario'], as_index=False)[['energy_pct_vs_2005','midday_share']].mean(), fmt=3)}

<h2>Figures</h2>
{figs_html}

<h2>Gate scorecard</h2>
<table><tr><th>gate</th><th>check</th><th>status</th><th>detail</th></tr>{gate_rows}</table>

<h2>Caveats carried to the manuscript</h2>
<ol style="font-size:13.5px">
<li><b>Asymmetric pathways to energy (D-20).</b> The three commercial channels modulate People,
Lights and Equipment — three routes from occupancy to energy. Residential drives People only
(OD-7D: the Step-7 residential product has no equipment/lighting columns). Cross-channel comparisons
of occupancy-to-energy sensitivity are therefore structurally biased against residential, which is
the thesis subject. Intra-channel comparisons — bands, cities, eras — are unaffected: the asymmetry
is common mode.</li>
<li><b>Damped scenario response is by design</b>, not a weak result: only People/Lights/Equipment
gains are modulated, while densities and the code baseline are untouched.</li>
<li><b>Dual basis.</b> CFA vs GFA-share differ systematically; never compare one to the other.</li>
<li><b>Retail staff and hotel guests are outside the GSS frame</b> — retail staff are logged as
AT_WORK, hotel guests are not sampled at all. Their loads live in the NECB baseline being modulated.</li>
<li><b>Hotel amenity zones are unmodulated in v1</b> (OD-6).</li>
<li><b>Ground-level EPW on a supertall</b> — no altitudinal temperature or wind gradient.</li>
<li><b>Standalone-prototype EUI bands applied to stacked-tower channels.</b> The as-modelled PASS
bands were derived from freestanding prototypes. A channel occupying floors inside one tower has
almost no roof, ground or (for interior zones) facade load, and shares a centrally sized plant, so
it is expected to read lower. See gate <code>S9-BASIS</code>. No threshold was relaxed; the gate
still fails against the band as locked, and whether that band applies here is an open decision.</li>
<li><b>Residential evening ENERGY peak is not reproducible in Leg 3</b> (gate
<code>S9-RESID-EVENING</code>). The occupancy still rises in the evening — the injection flips the
channel from midday-dominant (NECB code, ratio 0.22) to evening-dominant (GSS, ratio ~2.8, gate
<code>S9-INJECTION</code>) — but under OD-7D that behaviour has no route into energy, because
residential lights and plug loads stay on the flat NECB baseline. Any Leg-3 claim about residential
evening energy demand would be unsupported by this model.</li>
<li><b>Cross-era comparability</b>: each cycle's channel products come from that cycle's GSS pool,
so the longitudinal comparison is population-level, not a paired design.</li>
<li><b>Step-6 era-axis calibration bias (Defaut 4) is still open.</b> The <code>IS_SYNTHETIC</code>
fraction rises 0 % → 44.6 % → 100 % along the very era sequence §R4 compares. Read §R4 as
provisional until that is closed; the band and sensitivity axes are unaffected (common mode).</li>
</ol>
</div></body></html>"""
    p = os.path.join(outdir, "step9_report.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return p


# -------------------------------------------------------------------- main ----
def main():
    ap = argparse.ArgumentParser(description="3J Leg-3 Step 9 -- four-channel activity-driven loads")
    ap.add_argument("--agg-dir", default=DEFAULT_AGG)
    ap.add_argument("--outdir", default=DEFAULT_OUT)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print(f"=== 3J Leg-3 Step 9 | agg = {args.agg_dir} ===")
    d = load_agg(args.agg_dir)
    annual, peak, diur, meta = d["annual"], d["peak"], d["diurnal"], d["meta"]
    _log(f"loaded {len(meta)} cells, {len(annual)} annual rows")

    eui = build_eui(annual, meta)
    SCEN_OF.update(dict(zip(meta["cell_tag"], meta["scenario"])))
    ls = build_loadshape(peak, diur)
    scen = build_scenario(eui, annual)
    lon = build_longitudinal(eui, ls)
    _log(f"tables: eui={len(eui)} loadshape={len(ls)} scenario={len(scen)} longitudinal={len(lon)}")

    eui.to_csv(os.path.join(args.outdir, "step9_eui_by_channel.csv"), index=False)
    ls.to_csv(os.path.join(args.outdir, "step9_loadshape_peaks.csv"), index=False)
    scen.to_csv(os.path.join(args.outdir, "step9_scenario_response.csv"), index=False)
    lon.to_csv(os.path.join(args.outdir, "step9_longitudinal.csv"), index=False)

    figs = [
        ("§R1 — per-channel EUI vs band", fig_eui(eui, args.outdir),
         "Box = the 56 cells. Green band = as-modelled PASS criterion, green line = its central value."),
        ("§R2 — coincident diurnal load", fig_diurnal(diur, args.outdir),
         "Stacked weekday load, winter and summer. The gap between the stacked peak and the sum of "
         "the channel peaks is the tower's diversity."),
        ("§R2 — peak timing", fig_peakhour(ls, args.outdir),
         "Load-weighted circular mean hour per channel, one point per cell."),
        ("§R3 — scenario response", fig_scenario(scen, args.outdir),
         "One-at-a-time levers. A flat column would mean the lever never reached the engine."),
        ("§R4 — longitudinal", fig_longitudinal(lon, args.outdir),
         "Energy and midday share across the four GSS cycles, averaged over building x city."),
    ]

    gates = evaluate_gates(eui, ls, scen, lon, meta, outdir=args.outdir)
    with open(os.path.join(args.outdir, "step9_gates.json"), "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
    html = write_html(args.outdir, eui, ls, scen, lon, gates, meta, figs, args.agg_dir)

    n = {k: sum(1 for g in gates if g["status"] == k) for k in ("PASS", "WARN", "FAIL", "INFO")}
    print(f"\n=== scorecard: {n['PASS']}P / {n['WARN']}W / {n['FAIL']}F / {n['INFO']} INFO ===")
    for g in gates:
        if g["status"] in ("FAIL", "WARN"):
            print(f"  [{g['status']}] {g['gate']} -- {g['name']}: {g['detail']}")
    print(f"\nreport -> {html}")
    sys.exit(0)


if __name__ == "__main__":
    main()
