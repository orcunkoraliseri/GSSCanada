"""V3a report against the P10R arm (2026-09-25). Reads only; writes into <out>.

    py -3 v3a_report_P10R.py <runs_root> <agg_root> <agg_P10R> <out>

1. Seed-42 reproduction (two levels):
   a. per cell, the hourly captures (hourly_meters.csv, channel_hourly.csv) of V3a seed 42 vs the P10R cell,
      with the V3b checker's own compare() (annual and hourly relative metrics, TOL 1e-6 / 1e-4);
   b. the seed-42 aggregate vs agg_P10R restricted to the 8 cells: max abs and max rel difference over every
      numeric column of agg_annual.csv, agg_annual_by_channel.csv, agg_peak.csv, agg_diurnal.csv, agg_meta.csv.
2. Spread across the 5 seeds, per scenario x cell x channel: EUI (CFA), peak hour (energy_W, all days, argmax
   and circular), coincidence factor; and the 2030-minus-2022 delta within seed for each of these.
   Reading rule (pre-registered, V3_design_and_runs.md section 4): a published difference is "larger than
   draw noise" only if |published delta| > 2 x SD(delta across seeds). Published = the P10R arm (seed 42).
Writes: seed42_repro.json, v3a_P10R_eui_spread.csv, v3a_P10R_delta_eui.csv, v3a_P10R_peak_spread.csv,
v3a_P10R_delta_peak.csv, v3a_P10R_report.txt.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_check as C  # noqa: E402
import v3_lib as L    # noqa: E402

SEEDS = (42, 101, 202, 303, 404)
SCEN = ("Y2022", "B_central")
CELLS = [(b, c) for b in ("Tall", "SuperTall") for c in ("MTL", "CLG")]
CH_EUI = ("office", "retail", "hotel", "residential", "residential_common", "service_MEP")
KEYS = {"agg_annual_by_channel.csv": ["cell_tag", "channel"],
        "agg_peak.csv": ["cell_tag", "channel", "daytype", "metric"], "agg_meta.csv": ["cell_tag"]}


def circ_diff(a, b):
    return (np.asarray(a) - np.asarray(b) + 12.0) % 24.0 - 12.0


def repro(runs_root, agg_root, agg_p10r):
    out = {"cells": {}, "agg": {}}
    for s in SCEN:
        for b, c in CELLS:
            tag = L.cell_tag(s, b, c)
            r = C.compare(os.path.join(runs_root, "V3a", "S__%s__s42" % tag), os.path.join(L.P10R_CAMPAIGN, tag))
            r.pop("table", None)
            out["cells"][tag] = r
    tags = [L.cell_tag(s, b, c) for s in SCEN for b, c in CELLS]
    for f in ("agg_annual.csv", "agg_annual_by_channel.csv", "agg_peak.csv", "agg_diurnal.csv", "agg_meta.csv"):
        A = pd.read_csv(os.path.join(agg_root, "seed42", f))
        B = pd.read_csv(os.path.join(agg_p10r, f))
        B = B[B["cell_tag"].isin(tags)]
        extra_a = sorted(set(A["cell_tag"]) - set(tags))
        A = A[A["cell_tag"].isin(tags)]
        missing_in_a = sorted(set(tags) - set(A["cell_tag"]))   # partial run: compare only cells present
        B = B[B["cell_tag"].isin(set(A["cell_tag"]))]
        key = KEYS.get(f) or [c for c in A.columns if A[c].dtype == object]
        key = [k for k in key if k in A.columns]
        if f == "agg_diurnal.csv":
            key = [c for c in A.columns if A[c].dtype == object or c in ("hour",)]
        m = A.merge(B, on=key, how="outer", suffixes=("_a", "_b"), indicator=True)
        unmatched = int((m["_merge"] != "both").sum())
        num = [c for c in A.columns if c not in key and c in B.columns and pd.api.types.is_numeric_dtype(A[c])
               and pd.api.types.is_numeric_dtype(B[c])]
        skipped = [c for c in A.columns if c not in key and c not in num]
        worst_abs, worst_rel, wcol = 0.0, 0.0, None
        for c in num:
            xa, xb = m[c + "_a"].to_numpy(float), m[c + "_b"].to_numpy(float)
            both_nan = np.isnan(xa) & np.isnan(xb)
            d = np.where(both_nan, 0.0, np.abs(xa - xb))
            d = np.where(np.isnan(d), np.inf, d)
            rel = d / np.maximum(np.abs(xb), 1e-12)
            rel = np.where(d == 0, 0.0, np.where(np.isnan(rel), np.inf, rel))
            if d.size and d.max() > worst_abs:
                worst_abs, wcol = float(d.max()), c
            if rel.size:
                worst_rel = max(worst_rel, float(rel.max()))
        out["agg"][f] = {"rows_a": len(A), "rows_b": len(B), "unmatched_rows": unmatched, "key": key,
                         "cells_in_a_not_expected": extra_a, "cells_missing_in_a": missing_in_a,
                         "non_numeric_cols_not_compared": skipped,
                         "max_abs_diff": worst_abs, "max_abs_col": wcol, "max_rel_diff": worst_rel}
    return out


def main():
    runs_root, agg_root, agg_p10r, out = [os.path.abspath(x) for x in sys.argv[1:5]]
    os.makedirs(out, exist_ok=True)
    R = repro(runs_root, agg_root, agg_p10r)
    json.dump(R, open(os.path.join(out, "seed42_repro.json"), "w"), indent=2, default=str)

    E, P = [], []
    seeds = [s for s in SEEDS if os.path.isdir(os.path.join(agg_root, "seed%d" % s))]
    for s in seeds:
        e = pd.read_csv(os.path.join(agg_root, "seed%d" % s, "agg_annual_by_channel.csv"))
        mt = pd.read_csv(os.path.join(agg_root, "seed%d" % s, "agg_meta.csv"))[["cell_tag", "scenario", "building", "city"]]
        e = e.merge(mt, on="cell_tag")
        e["seed"] = s
        E.append(e)
        p = pd.read_csv(os.path.join(agg_root, "seed%d" % s, "agg_peak.csv")).merge(mt, on="cell_tag")
        p["seed"] = s
        P.append(p)
    E = pd.concat(E)
    E = E[E["channel"].isin(CH_EUI)]
    P = pd.concat(P)
    P = P[(P["daytype"] == "all") & (P["metric"] == "energy_W")]
    idx = ["scenario", "building", "city", "channel"]

    se = E.groupby(idx)["eui_CFA_kWh_m2"].agg(["count", "mean", "std", "min", "max"]).reset_index()
    se["cv_pct"] = 100 * se["std"] / se["mean"]
    pub = E[E["seed"] == 42].set_index(idx)["eui_CFA_kWh_m2"].rename("published_s42")
    se = se.merge(pub.reset_index(), on=idx, how="left")
    se.to_csv(os.path.join(out, "v3a_P10R_eui_spread.csv"), index=False)

    pv = E.pivot_table(index=["building", "city", "channel", "seed"], columns="scenario",
                       values="eui_CFA_kWh_m2").reset_index()
    pv["delta"] = pv["B_central"] - pv["Y2022"]
    de = pv.groupby(["building", "city", "channel"])["delta"].agg(["count", "mean", "std", "min", "max"]).reset_index()
    de = de.merge(pv[pv["seed"] == 42][["building", "city", "channel", "delta"]].rename(columns={"delta": "published_delta"}),
                  on=["building", "city", "channel"], how="left")
    de = de[de["count"] > 0]
    de["ratio_abs_pub_over_sd"] = de["published_delta"].abs() / de["std"]
    de["larger_than_draw_noise"] = de["published_delta"].abs() > 2 * de["std"]
    de["sign_same_all_seeds"] = (np.sign(de["min"]) == np.sign(de["max"])) & (de["min"] != 0)
    de.to_csv(os.path.join(out, "v3a_P10R_delta_eui.csv"), index=False)

    # peak hour (argmax, circular) and coincidence factor; building CF lives on every row of a cell
    ps = []
    for (sc, b, c, ch), g in P.groupby(idx):
        ang = 2 * np.pi * g["peak_hour_circular"].to_numpy(float) / 24.0
        cm = (np.degrees(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())) / 15.0) % 24.0
        cdev = circ_diff(g["peak_hour_circular"], cm)
        ps.append({"scenario": sc, "building": b, "city": c, "channel": ch, "n": len(g),
                   "argmax_values": ",".join(str(int(v)) for v in g.sort_values("seed")["peak_hour_argmax"]),
                   "argmax_n_distinct": g["peak_hour_argmax"].nunique(),
                   "circ_mean_h": cm, "circ_sd_h": float(np.sqrt((cdev ** 2).sum() / (len(g) - 1))) if len(g) > 1 else np.nan,
                   "circ_min_dev_h": float(cdev.min()), "circ_max_dev_h": float(cdev.max()),
                   "cf_mean": g["coincidence_factor"].mean(), "cf_sd": g["coincidence_factor"].std(),
                   "cf_min": g["coincidence_factor"].min(), "cf_max": g["coincidence_factor"].max()})
    ps = pd.DataFrame(ps)
    ps["cf_cv_pct"] = 100 * ps["cf_sd"] / ps["cf_mean"]
    ps.to_csv(os.path.join(out, "v3a_P10R_peak_spread.csv"), index=False)

    pp = P.pivot_table(index=["building", "city", "channel", "seed"], columns="scenario",
                       values=["peak_hour_circular", "coincidence_factor", "peak_hour_argmax"]).reset_index()
    dp = pd.DataFrame({"building": pp["building"], "city": pp["city"], "channel": pp["channel"], "seed": pp["seed"],
                       "d_circ_h": circ_diff(pp[("peak_hour_circular", "B_central")], pp[("peak_hour_circular", "Y2022")]),
                       "d_argmax_h": circ_diff(pp[("peak_hour_argmax", "B_central")], pp[("peak_hour_argmax", "Y2022")]),
                       "d_cf": pp[("coincidence_factor", "B_central")] - pp[("coincidence_factor", "Y2022")]})
    rows = []
    dp = dp.dropna(subset=["d_circ_h", "d_cf"])
    for (b, c, ch), g in dp.groupby(["building", "city", "channel"]):
        if not (g["seed"] == 42).any():
            continue
        g42 = g[g["seed"] == 42].iloc[0]
        r = {"building": b, "city": c, "channel": ch, "n_pairs": len(g)}
        for k in ("d_circ_h", "d_argmax_h", "d_cf"):
            r[k + "_pub"], r[k + "_mean"], r[k + "_sd"] = g42[k], g[k].mean(), g[k].std()
            r[k + "_min"], r[k + "_max"] = g[k].min(), g[k].max()
            r[k + "_larger_than_noise"] = bool(abs(g42[k]) > 2 * g[k].std()) if g[k].std() > 0 else bool(g42[k] != 0)
        rows.append(r)
    dp2 = pd.DataFrame(rows)
    dp2.to_csv(os.path.join(out, "v3a_P10R_delta_peak.csv"), index=False)

    pd.set_option("display.width", 250)
    lines = ["V3a report vs P10R (seed 42 = published P10R cell); seeds present: %s" % seeds, "", "seed-42 reproduction, hourly captures:"]
    for t, r in R["cells"].items():
        lines.append("  %-28s %s worst_ann=%s worst_hourly=%s" % (t, r["status"], r.get("worst_ann"), r.get("worst_hourly")))
    lines.append("seed-42 reproduction, aggregate vs agg_P10R:")
    for f, r in R["agg"].items():
        lines.append("  %-26s rows %d/%d unmatched %d max_abs %.3g (%s) max_rel %.3g" % (
            f, r["rows_a"], r["rows_b"], r["unmatched_rows"], r["max_abs_diff"], r["max_abs_col"], r["max_rel_diff"]))
    lines += ["", "EUI spread (kWh/m2 CFA):", se.to_string(index=False, float_format=lambda x: "%.4g" % x),
              "", "2030-minus-2022 EUI delta within seed:", de.to_string(index=False, float_format=lambda x: "%.4g" % x),
              "", "peak hour / coincidence factor spread (energy_W, all days):",
              ps.to_string(index=False, float_format=lambda x: "%.4g" % x),
              "", "2030-minus-2022 peak-hour / CF delta within seed:",
              dp2.to_string(index=False, float_format=lambda x: "%.4g" % x)]
    open(os.path.join(out, "v3a_P10R_report.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
