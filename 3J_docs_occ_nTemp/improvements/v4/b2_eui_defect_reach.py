# -*- coding: utf-8 -*-
"""V4-B2 -- measure the reach of the calculate_eui() ReportName defect.

READ-ONLY on Leg2_2-split/. No file under Leg-2 is modified, no simulation is
run, the cluster is not contacted.

The defect (Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py, the End Uses
query): the SQL filters on TableName only. EnergyPlus emits a table named
'End Uses By Subcategory' under BOTH
    AnnualBuildingUtilityPerformanceSummary   -> GJ
    DemandEndUseComponentsSummary             -> W
and the unit branch ends in `else: val_kwh = val` ("unknown unit - assume
kWh"), so every W row is added as if it were a kWh.

What this script measures, per SQL file:
  contaminated = the sum the shipped code produces
  corrected    = the same sum with ReportName pinned to the annual-energy report
  factor       = contaminated / corrected

The pre-registered question is NOT "what is the factor" -- 1.706 was already
measured on one cell. It is whether the factor is UNIFORM, because a single
divisor can only be applied to the published numbers if it is.
"""
import glob, io, json, os, sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LEG2 = os.path.join(ROOT, "Leg2_2-split")

ANNUAL_REPORT = "AnnualBuildingUtilityPerformanceSummary"
DEMAND_REPORT = "DemandEndUseComponentsSummary"


def area(conn):
    q = ("SELECT RowName, Units, Value FROM TabularDataWithStrings "
         "WHERE TableName = 'Building Area'")
    cond = tot = 0.0
    for row_name, units, value in conn.execute(q):
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        if units in ("ft2", "ft²"):
            v *= 0.092903
        if row_name == "Total Building Area":
            tot = v
        elif row_name == "Net Conditioned Building Area":
            cond = v
    return cond or tot


def to_kwh(val, units):
    """The shipped conversion, reproduced EXACTLY -- including the else branch."""
    if units == "GJ":
        return val * 277.778
    if units == "kWh":
        return val
    if units == "J":
        return val / 3600000.0
    if units == "kBtu":
        return val * 0.293071
    if units == "Btu":
        return val * 0.000293071
    if units == "MJ":
        return val * 0.277778
    return val                      # <-- the defect's landing point


def energy(conn, report=None):
    """Total 'energy' the shipped code sums. report=None reproduces the defect."""
    q = ("SELECT ReportName, Units, Value FROM TabularDataWithStrings "
         "WHERE TableName = 'End Uses By Subcategory'")
    n = {}
    total = 0.0
    for rep, units, value in conn.execute(q):
        if "m3" in str(units):
            continue
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        if report is not None and rep != report:
            continue
        kwh = to_kwh(v, units)
        if kwh != 0:
            total += kwh
            n[str(units)] = n.get(str(units), 0) + 1
    return total, n


def main():
    out = []
    for path in sorted(glob.glob(os.path.join(LEG2, "**", "eplusout.sql"), recursive=True)):
        conn = sqlite3.connect(path)
        try:
            a = area(conn)
            bad, units_bad = energy(conn, None)
            good, units_good = energy(conn, ANNUAL_REPORT)
            demand, _ = energy(conn, DEMAND_REPORT)
        finally:
            conn.close()
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        rec = {"cell": rel, "area_m2": round(a, 2),
               "eui_shipped": round(bad / a, 3) if a else None,
               "eui_corrected": round(good / a, 3) if a else None,
               "factor": round(bad / good, 6) if good else None,
               "kwh_legitimate": round(good, 1),
               "watts_read_as_kwh": round(demand, 1),
               "unit_tally_unfiltered": units_bad, "unit_tally_filtered": units_good}
        out.append(rec)
        print("%-88s area %9.1f  shipped %8.2f  corrected %8.2f  factor %.4f"
              % (rel.split("outputs_step8/")[-1], a, rec["eui_shipped"],
                 rec["eui_corrected"], rec["factor"]))

    f = [r["factor"] for r in out if r["factor"]]
    if f:
        print("\nfactors: n=%d  min=%.4f  max=%.4f  spread=%.2f%% of the minimum"
              % (len(f), min(f), max(f), 100 * (max(f) - min(f)) / min(f)))
        print("UNIFORM?  %s" % ("yes, within 0.5%" if (max(f) - min(f)) / min(f) < 0.005
                                else "NO -- a single divisor cannot be applied"))

    here = os.path.dirname(os.path.abspath(__file__))
    with io.open(os.path.join(here, "v4_b2_defect_reach.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"task": "V4-B2", "date": "2026-08-06",
                             "note": "residential smoke cells only; no Leg-2 office SQL exists on this machine",
                             "cells": out}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
