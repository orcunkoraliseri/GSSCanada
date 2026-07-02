#!/usr/bin/env python3
"""step9_probe.py — READ-ONLY schema/signal probe for the Step-9 office refinement.

Answers three questions before we edit build_scenario/build_longitudinal:
  (1) Does agg_peak office peak_kW_annual / mean_peak_hour vary across the 7 scenarios?
  (2) What is the exact office occupancy meter name in agg_diurnal, and does its
      weekday mid-day value vary across scenarios? (the office WFH signal)
  (3) Sanity: confirm agg_annual office energy/occ really are flat.

Prints small tables only. No writes. Reads the same AGG_DIR as the analysis script.
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

HERE    = Path(__file__).resolve().parent
AGG_DIR = Path(os.environ.get("STEP9_AGG_DIR", HERE.parent / "Step8_docs" / "outputs_step8" / "agg"))
SCEN_ORDER = ["2005", "2010", "2015", "2022",
              "2030-conservative", "2030-hybrid", "2030-fullyhybrid"]


def num(s):
    return pd.to_numeric(s, errors="coerce")


def hdr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78, flush=True)


def main():
    print(f"AGG_DIR = {AGG_DIR}", flush=True)

    # ---- agg_peak -----------------------------------------------------------
    hdr("(1) agg_peak — office peak_kW_annual / mean_peak_hour by scenario")
    p = pd.read_csv(AGG_DIR / "agg_peak.csv", low_memory=False)
    print("columns:", list(p.columns), flush=True)
    print("channels:", sorted(p["channel"].dropna().unique()), flush=True)
    po = p[p["channel"] == "office"].copy()
    for c in ("peak_kW_annual", "mean_daily_peak_kW", "mean_peak_hour"):
        if c in po:
            po[c] = num(po[c])
    if not po.empty:
        g = (po.groupby("scenario")
               .agg(n=("scenario", "size"),
                    peak_kW_annual=("peak_kW_annual", "mean"),
                    mean_daily_peak_kW=("mean_daily_peak_kW", "mean"),
                    mean_peak_hour=("mean_peak_hour", "mean"))
               .reindex(SCEN_ORDER))
        print(g.round(3).to_string(), flush=True)
    else:
        print("!! no office rows in agg_peak", flush=True)

    # ---- agg_annual ---------------------------------------------------------
    hdr("(2) agg_annual — office energy/occ by scenario (expect ~flat)")
    a = pd.read_csv(AGG_DIR / "agg_annual.csv", low_memory=False)
    print("columns:", list(a.columns), flush=True)
    ao = a[a["channel"] == "office"].copy()
    occ_cols = [c for c in ("occ_mean_persons", "occ_midday_persons",
                            "midday_share", "total_energy_kWh", "eui_kWh_m2") if c in ao]
    for c in occ_cols:
        ao[c] = num(ao[c])
    if not ao.empty:
        g = ao.groupby("scenario")[occ_cols].mean().reindex(SCEN_ORDER)
        print(g.round(4).to_string(), flush=True)

    # ---- agg_diurnal --------------------------------------------------------
    hdr("(3) agg_diurnal — ALL unique meters + office occupancy signal by scenario")
    meters, chans = set(), set()
    office_occ_parts = []
    for chunk in pd.read_csv(AGG_DIR / "agg_diurnal.csv", chunksize=250_000, low_memory=False):
        if "meter" in chunk:
            meters.update(chunk["meter"].dropna().unique().tolist())
        if "channel" in chunk:
            chans.update(chunk["channel"].dropna().unique().tolist())
        # keep office weekday rows for later per-meter/per-scenario mid-day summary
        if "channel" in chunk and "daytype" in chunk:
            m = (chunk["channel"] == "office") & (chunk["daytype"] == "weekday")
            if "season" in chunk:
                m = m & (chunk["season"] == "all")
            sub = chunk.loc[m, [c for c in ("scenario", "meter", "hour", "value") if c in chunk]].copy()
            if len(sub):
                office_occ_parts.append(sub)
    print("columns seen: (per chunk)  channels:", sorted(map(str, chans)), flush=True)
    print("ALL unique meters:", sorted(map(str, meters)), flush=True)

    if office_occ_parts:
        od = pd.concat(office_occ_parts, ignore_index=True)
        od["hour"] = num(od["hour"]); od["value"] = num(od["value"])
        od = od.dropna(subset=["hour", "value"])
        od["hour"] = od["hour"].astype(int)
        print("\noffice meters present in diurnal:",
              sorted(od["meter"].astype(str).unique()), flush=True)
        # mid-day (9..17) weekday mean per meter per scenario — spot the varying one
        mid = od[od["hour"].between(9, 17)]
        for mtr in sorted(mid["meter"].astype(str).unique()):
            sub = mid[mid["meter"].astype(str) == mtr]
            g = sub.groupby("scenario")["value"].mean().reindex(SCEN_ORDER)
            print(f"\n[office meter='{mtr}'] weekday mid-day(9-17) mean value by scenario:", flush=True)
            print(g.round(4).to_string(), flush=True)

    print("\nPROBE DONE.", flush=True)


if __name__ == "__main__":
    main()
