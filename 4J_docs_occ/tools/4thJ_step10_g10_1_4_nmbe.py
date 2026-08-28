# -*- coding: utf-8 -*-
"""`G10.1`-`G10.4` --- NMBE and CV(RMSE), monthly and hourly, on the SIMULATED cells.

!! THE REFERENCE IS AN INDEPENDENT RE-RUN, `D-S8-1`(a) EXTENDED VERBATIM, and this is
!! A REPRODUCIBILITY TRIPWIRE, NOT A MEASURED-ACCURACY CLAIM.  The `FINDING 44`
!! inversion is written on the gate row itself: a tight NMBE here says the two runs
!! agree, and says NOTHING about whether either resembles a real building.

Reference  = the Speed re-run (EnergyPlus 23.1.0, identical IDF bytes).
Measured   = this machine's run.

!! POPULATION, named because `V10.b` requires it: the 40 cells whose LOCAL run tree
!! was retained (4 buildings --- `es` 30 cells, `it` 10, **`uk` 0**).  The other 370
!! local trees were deleted at campaign time; Speed holds all 410, so widening this
!! population needs a LOCAL re-run, which is a decision and not a fix.
"""
import argparse
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
OUT = PROJ / "Step10_docs/outputs_step10/realstock_campaign"
RUNROOT = Path(r"C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/step10_realstock")

J_TO_KWH = 1.0 / 3.6e6
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
BANDS = {"G10.1": 0.05, "G10.2": 0.10, "G10.3": 0.15, "G10.4": 0.30}


def parse_hourly_heating(csv_path):
    """LIFTED VERBATIM from the campaign tool: two definitions would measure the
    definitions, not the platforms."""
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        columns = [c for c in reader.fieldnames or []
                   if "zone ideal loads zone total heating energy" in c.casefold()
                   and "[j]" in c.casefold() and "(hourly)" in c.casefold()]
        if not columns:
            raise ValueError("eplusout.csv lacks the hourly heating variable: %s" % csv_path)
        series = {c: [] for c in columns}
        for row in reader:
            for c in columns:
                series[c].append(float(row[c]))
    n = len(next(iter(series.values())))
    return [sum(series[c][h] for c in columns) * J_TO_KWH for h in range(n)]


def monthly(hourly):
    out, i = [], 0
    for d in DAYS:
        out.append(sum(hourly[i:i + d * 24]))
        i += d * 24
    return out


def nmbe_cvrmse(meas, ref):
    """NMBE and CV(RMSE) of `meas` against `ref`, normalised on the REFERENCE mean."""
    n = len(ref)
    mean = sum(ref) / n
    if mean == 0:
        return None, None
    nmbe = sum(m - r for m, r in zip(meas, ref)) / (n * mean)
    rmse = math.sqrt(sum((m - r) ** 2 for m, r in zip(meas, ref)) / n)
    return nmbe, rmse / mean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speed-series", required=True)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--runroot", default=str(RUNROOT))
    a = ap.parse_args()

    ref_doc = json.loads(Path(a.speed_series).read_text(encoding="utf-8"))
    refs = ref_doc["cells"]
    runroot = Path(a.runroot)

    rows, skipped = [], []
    for cid in sorted(refs):
        ref = refs[cid]
        if "error" in ref:
            skipped.append({"cell_id": cid, "why": ref["error"]})
            continue
        p = runroot / cid / "eplusout.csv"
        if not p.is_file():
            skipped.append({"cell_id": cid, "why": "no LOCAL eplusout.csv retained"})
            continue
        loc_h = parse_hourly_heating(p)
        ref_h = ref["hourly_kwh"]
        if len(loc_h) != len(ref_h):
            skipped.append({"cell_id": cid, "why": "hour counts differ: %d vs %d"
                                                   % (len(loc_h), len(ref_h))})
            continue
        nm_h, cv_h = nmbe_cvrmse(loc_h, ref_h)
        nm_m, cv_m = nmbe_cvrmse(monthly(loc_h), ref["monthly_kwh"])
        rows.append({"cell_id": cid, "hours": len(loc_h),
                     "nmbe_monthly": nm_m, "cvrmse_monthly": cv_m,
                     "nmbe_hourly": nm_h, "cvrmse_hourly": cv_h})

    def score(gate, key, band):
        vals = [abs(r[key]) for r in rows if r[key] is not None]
        if not vals:
            return {"gate": gate, "verdict": "NOT_EVALUABLE", "cells": 0,
                    "note": "no paired cell survived. NOT a pass."}
        over = sum(1 for v in vals if v > band)
        return {"gate": gate, "verdict": "PASS" if over == 0 else "FAIL",
                "metric": key, "band": band, "cells": len(vals),
                "cells_outside_band": over, "worst_absolute": max(vals),
                "reference": "an INDEPENDENT RE-RUN on Speed (EnergyPlus 23.1.0, "
                             "identical IDF bytes) --- D-S8-1(a) extended verbatim",
                "note": "A REPRODUCIBILITY TRIPWIRE, NOT A MEASURED-ACCURACY CLAIM "
                        "(the FINDING 44 inversion, written on the gate row)."}

    board = {"G10.1": score("G10.1", "nmbe_monthly", BANDS["G10.1"]),
             "G10.2": score("G10.2", "nmbe_hourly", BANDS["G10.2"]),
             "G10.3": score("G10.3", "cvrmse_monthly", BANDS["G10.3"]),
             "G10.4": score("G10.4", "cvrmse_hourly", BANDS["G10.4"])}

    # V10.a --- every gate SEEN FAILING, on the real artefact, not a fixture
    bat = []
    for gate, key, band in (("G10.1", "nmbe_monthly", BANDS["G10.1"]),
                            ("G10.2", "nmbe_hourly", BANDS["G10.2"]),
                            ("G10.3", "cvrmse_monthly", BANDS["G10.3"]),
                            ("G10.4", "cvrmse_hourly", BANDS["G10.4"])):
        mutated = [dict(r) for r in rows]
        mutated[0][key] = band * 2.0
        vals = [abs(r[key]) for r in mutated if r[key] is not None]
        after = "PASS" if sum(1 for v in vals if v > band) == 0 else "FAIL"
        bat.append({"mutation": "one cell's %s pushed to twice the band" % key,
                    "gate": gate, "verdict_clean": board[gate]["verdict"],
                    "verdict_mutated": after, "felled": after == "FAIL"})

    folds = {}
    for r in rows:
        folds[r["cell_id"].split("__")[0]] = folds.get(r["cell_id"].split("__")[0], 0) + 1
    doc = {"tool": "4thJ_step10_g10_1_4_nmbe.py",
           "population": {"paired_cells": len(rows), "by_fold": folds,
                          "skipped": skipped,
                          "why_not_410": "the local run trees were deleted for 370 "
                                         "cells at campaign time; Speed holds all 410. "
                                         "Widening needs a LOCAL re-run --- a decision, "
                                         "not a fix."},
           "board": board, "battery": {"cases": bat,
                                       "verdict": "PASS" if all(c["felled"] for c in bat)
                                                  else "FAIL"},
           "rows": rows}
    p = Path(a.out) / "realstock_g10_1_4_nmbe.json"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for g in ("G10.1", "G10.2", "G10.3", "G10.4"):
        b = board[g]
        print("%-7s %-14s worst |%s| = %.3e  (%d cells, band %.2f)"
              % (g, b["verdict"], b.get("metric", ""), b.get("worst_absolute", float("nan")),
                 b.get("cells", 0), b.get("band", float("nan"))))
    print("battery", doc["battery"]["verdict"], "| population", folds, "| skipped", len(skipped))
    print("->", p)


if __name__ == "__main__":
    main()
