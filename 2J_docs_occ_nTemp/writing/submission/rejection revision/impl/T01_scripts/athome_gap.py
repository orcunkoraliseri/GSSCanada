#!/usr/bin/env python
"""
T01 (WP1 step 1) -- re-derive the 2022 vs 2030 at-home gap from the BEM schedule
files actually consumed by the Step-8 campaign.

Inputs (must be present in --workdir):
    BEM_Schedules_2022.csv, BEM_Schedules_2030.csv
        columns: SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,
                 MATCH_TIER,Occupancy_Schedule,Metabolic_Rate,Equipment_Fraction,
                 Lighting_Fraction,Equip_Design_W,Light_Design_W
        "at home" column = Occupancy_Schedule (0/0.5/1 fraction of the hour occupied).
        Day_Type in {Weekday, Weekend}; Hour in 0..23; DTYPE in
        {SingleD, MidRise, HighRise, OtherDwelling} (already labelled -- see
        Step8_docs/08_gen_cycle_schedules.py:88-93 for the CONDO/BEDRM -> DTYPE
        mapping used upstream to build this column).
    panel_manifest.csv (optional; produced locally by concatenating each cell's
        cell_manifest.csv.new_2022_2030_20260711 under
        BEM_Setup/SimResults_Step8/campaign_N50/<archetype>__<city>/)
        columns: cell,sample,sim_hh_id,hhsize,dtype,pr

No weight column exists in the schedule files, so only unweighted means are
reported (the task doc says "if a weight column exists" -- it does not; recorded
as NOT VERIFIED / not applicable in the run_meta.json).

Outputs (written to --outdir):
    athome_summary.csv   national + per-archetype (+ panel-only) weekday/weekend
                          at-home mean, per year
    athome_hourly.csv    24-hour at-home profile per year x day-type
                          (+ per archetype, + panel-only)
    run_meta.json         input hashes, row counts, timing
"""
import argparse
import csv
import hashlib
import json
import sys
import time

import pandas as pd

USECOLS = ["SIM_HH_ID", "Day_Type", "Hour", "DTYPE", "Occupancy_Schedule"]
DTYPES = {
    "SIM_HH_ID": "int64",
    "Day_Type": "category",
    "Hour": "int8",
    "DTYPE": "category",
    "Occupancy_Schedule": "float64",
}


def sha256(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(bufsize), b""):
            h.update(chunk)
    return h.hexdigest()


def load_panel_ids(path):
    ids = set()
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ids.add(int(row["sim_hh_id"]))
            except (KeyError, ValueError):
                pass
    return ids


def summarize(df, year, tag=""):
    rows = []
    # national
    g = df.groupby("Day_Type", observed=True)["Occupancy_Schedule"].agg(["mean", "count"])
    for dt, r in g.iterrows():
        rows.append({"year": year, "scope": f"national{tag}", "archetype": "ALL",
                     "day_type": dt, "mean_athome": r["mean"], "n_rows": int(r["count"])})
    # per archetype
    g2 = df.groupby(["DTYPE", "Day_Type"], observed=True)["Occupancy_Schedule"].agg(["mean", "count"])
    for (arch, dt), r in g2.iterrows():
        rows.append({"year": year, "scope": f"per_archetype{tag}", "archetype": arch,
                     "day_type": dt, "mean_athome": r["mean"], "n_rows": int(r["count"])})
    # household-mean-of-means check (should equal row mean exactly: balanced 24h/day-type/hh)
    g3 = (df.groupby(["SIM_HH_ID", "Day_Type"], observed=True)["Occupancy_Schedule"]
          .mean().reset_index()
          .groupby("Day_Type", observed=True)["Occupancy_Schedule"].mean())
    for dt, v in g3.items():
        rows.append({"year": year, "scope": f"national_hh_mean_of_means{tag}", "archetype": "ALL",
                     "day_type": dt, "mean_athome": v, "n_rows": None})
    return rows


def hourly(df, year, tag=""):
    rows = []
    g = df.groupby(["Day_Type", "Hour"], observed=True)["Occupancy_Schedule"].mean()
    for (dt, hr), v in g.items():
        rows.append({"year": year, "scope": f"national{tag}", "archetype": "ALL",
                     "day_type": dt, "hour": int(hr), "mean_athome": v})
    g2 = df.groupby(["DTYPE", "Day_Type", "Hour"], observed=True)["Occupancy_Schedule"].mean()
    for (arch, dt, hr), v in g2.items():
        rows.append({"year": year, "scope": f"per_archetype{tag}", "archetype": arch,
                     "day_type": dt, "hour": int(hr), "mean_athome": v})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--panel-manifest", default=None)
    args = ap.parse_args()

    t0 = time.time()
    meta = {"inputs": {}, "row_counts": {}, "timing_s": {}}

    files = {
        2022: f"{args.workdir}/BEM_Schedules_2022.csv",
        2030: f"{args.workdir}/BEM_Schedules_2030.csv",
    }

    summary_rows = []
    hourly_rows = []

    panel_ids = None
    if args.panel_manifest:
        panel_ids = load_panel_ids(args.panel_manifest)
        meta["panel_manifest"] = args.panel_manifest
        meta["panel_n_households"] = len(panel_ids)

    for year, path in files.items():
        th0 = time.time()
        h = sha256(path)
        meta["inputs"][str(year)] = {"path": path, "sha256": h}

        df = pd.read_csv(path, usecols=USECOLS, dtype=DTYPES)
        meta["row_counts"][str(year)] = int(len(df))
        meta["timing_s"][f"read_{year}"] = round(time.time() - th0, 1)

        summary_rows += summarize(df, year)
        hourly_rows += hourly(df, year)

        if panel_ids:
            dfp = df[df["SIM_HH_ID"].isin(panel_ids)]
            meta.setdefault("panel_rows_matched", {})[str(year)] = int(len(dfp))
            meta.setdefault("panel_hh_matched", {})[str(year)] = int(dfp["SIM_HH_ID"].nunique())
            summary_rows += summarize(dfp, year, tag="_panel")
            hourly_rows += hourly(dfp, year, tag="_panel")

        del df

    pd.DataFrame(summary_rows).to_csv(f"{args.outdir}/athome_summary.csv", index=False)
    pd.DataFrame(hourly_rows).to_csv(f"{args.outdir}/athome_hourly.csv", index=False)

    meta["timing_s"]["total"] = round(time.time() - t0, 1)
    with open(f"{args.outdir}/run_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("DONE", meta["timing_s"])


if __name__ == "__main__":
    main()
