#!/usr/bin/env python3
"""Arm H -- run the pre-registered DHW-volume gates over ALL campaign cells, in-job.

Cluster-side companion to 3rdJ_09H_dhwvol_verify.py (which checks ONE downloaded cell). Same gates,
same thresholds -- they were pre-registered on 2026-08-03 before any cell finished and are NOT
re-tuned here. Python 3.10 on the cluster: no PEP 701 multi-line f-strings.

    python 3rdJ_09H_dhwvol_sweep.py <campaign_dir> <out_csv>

Also carries the pre-registered HOTEL SATURATION test. Cell Y2022 showed the hotel's implied
delta-T collapsing from ~52 K at low draw to 18.3 K at peak draw, against water heaters that are
hard-sized literals (5 x 87921.32 W + 1 x 7999.96 W = 447.6 kW for the whole tower) while the hotel
peak decile alone needs 526.0 kW to reach target. Prediction recorded before B_opt finished:

    cells that scale hotel volume UP (r_hotel > 1) must show a LOWER annual implied hotel delta-T
    than cells with r_hotel == 1, because the plant cannot follow the draw.

If instead delta-T is flat in r_hotel, the capacity explanation is wrong and must be re-opened.
This script only MEASURES; it does not decide. A miss is recorded, not repaired.
"""
import os
import sys
import json
import glob
import re

import numpy as np
import pandas as pd

RHO = 1000.0     # kg/m3
CP = 4186.0      # J/(kg.K)
DT_LO, DT_HI = 20.0, 80.0
EXPECTED_ROWS = 8760
CHANNELS = ["office", "retail", "hotel", "residential",
            "residential_common", "service_MEP", "unassigned"]


def _r_for_channel(prov_path, channel):
    """Volume ratio R the injector actually applied to `channel`, from the provenance file.

    Returns None when the channel is absent from this cell (e.g. hotel before 2019 under the
    documented era exclusion) -- absent must NOT be read as 1.0.
    """
    if not os.path.isfile(prov_path):
        return None
    pat = re.compile(r"^t9_13\s+" + re.escape(channel) + r"\s+.*?R=([0-9.]+)")
    vals = []
    with open(prov_path, errors="ignore") as fh:
        for ln in fh:
            m = pat.match(ln)
            if m:
                vals.append(float(m.group(1)))
    if not vals:
        return None
    return float(np.mean(vals))


def verify_cell(cell_dir):
    name = os.path.basename(cell_dir.rstrip("/"))
    row = {"cell": name}
    vol_p = os.path.join(cell_dir, "dhw_volume_hourly.csv")
    eng_p = os.path.join(cell_dir, "dhw_hourly.csv")
    man_p = os.path.join(cell_dir, "manifest.json")
    prov_p = os.path.join(cell_dir, "injected.idf.provenance.txt")

    man = {}
    if os.path.isfile(man_p):
        try:
            man = json.load(open(man_p))
        except Exception as e:
            row["manifest_error"] = str(e)

    # G1
    row["G1"] = os.path.isfile(vol_p)
    if not row["G1"]:
        row["exception"] = man.get("dhw_volume_hourly_exception", "file absent")
        for g in ["G2", "G3", "G4", "G5", "G6", "G7"]:
            row[g] = False
        return row

    vol = pd.read_csv(vol_p)
    want = ["dhwvol_" + c for c in CHANNELS]
    have = [c for c in want if c in vol.columns]

    row["G2"] = (len(vol) == EXPECTED_ROWS)
    row["rows"] = len(vol)
    row["G3"] = (len(have) == len(want))
    row["missing_cols"] = ",".join([c for c in want if c not in vol.columns])

    tot = float(np.nansum(vol[have].to_numpy())) if have else 0.0
    allnan = bool(vol[have].isna().all().all()) if have else True
    row["G4"] = bool(tot > 0 and np.isfinite(tot) and not allnan)
    row["total_volume_m3"] = tot

    exc = man.get("dhw_volume_hourly_exception")
    claimed = (man.get("dhw_volume_hourly_csv") or {}).get("rows")
    row["G5"] = (exc is None and claimed == len(vol))
    row["exception"] = exc
    unres = man.get("dhw_volume_unresolved_equipment")
    row["G6"] = (not unres)
    row["unresolved"] = unres if unres else 0

    # G7 + the saturation measurement
    if not os.path.isfile(eng_p):
        row["G7"] = False
        return row
    eng = pd.read_csv(eng_p)
    ok_all = True
    for ch in CHANNELS:
        vc, ec = "dhwvol_" + ch, "dhw_" + ch
        if vc not in vol.columns or ec not in eng.columns:
            continue
        V = float(np.nansum(vol[vc].to_numpy()))
        E = float(np.nansum(eng[ec].to_numpy()))
        if V <= 0:
            if E > 0:
                ok_all = False
                row["dT_" + ch] = np.inf   # energy without water
            continue
        dT = E / (RHO * CP * V)
        row["dT_" + ch] = dT
        row["V_" + ch] = V
        if not (DT_LO <= dT <= DT_HI):
            ok_all = False
    row["G7"] = ok_all

    # hotel saturation: annual dT, peak-decile dT, and the r actually applied
    hv, he = "dhwvol_hotel", "dhw_hotel"
    if hv in vol.columns and he in eng.columns:
        V = vol[hv].to_numpy()
        E = eng[he].to_numpy()
        m = V > 0
        if m.sum() > 20:
            dTh = E[m] / (RHO * CP * V[m])
            Vm = V[m]
            order = np.argsort(Vm)
            top = order[-max(1, len(order) // 10):]
            low = order[:max(1, len(order) // 10)]
            row["hotel_dT_peakdecile"] = float(dTh[top].mean())
            row["hotel_dT_lowdecile"] = float(dTh[low].mean())
            row["hotel_V_peakdecile"] = float(Vm[top].mean())
    row["r_hotel"] = _r_for_channel(prov_p, "hotel")
    row["r_office"] = _r_for_channel(prov_p, "office")
    row["r_retail"] = _r_for_channel(prov_p, "retail")
    return row


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    camp, out_csv = sys.argv[1], sys.argv[2]
    cells = sorted([d for d in glob.glob(os.path.join(camp, "*")) if os.path.isdir(d)])
    print("cells found: %d" % len(cells))
    rows = [verify_cell(c) for c in cells]
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print("wrote %s" % out_csv)

    gates = ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]
    print("\n=== gate pass counts (of %d cells) ===" % len(df))
    for g in gates:
        if g in df.columns:
            n = int(df[g].sum())
            print("  %-3s %3d / %3d %s" % (g, n, len(df), "" if n == len(df) else "  <-- FAIL"))
    bad = df[~df[gates].all(axis=1)] if all(g in df.columns for g in gates) else df.iloc[0:0]
    if len(bad):
        print("\ncells failing at least one gate:")
        cols = ["cell"] + gates + ["rows", "total_volume_m3", "unresolved", "exception"]
        print(bad[[c for c in cols if c in bad.columns]].to_string(index=False))

    print("\n=== PRE-REGISTERED hotel saturation test ===")
    print("prediction: cells with r_hotel > 1 show LOWER annual hotel dT than cells with r_hotel==1")
    if "r_hotel" in df.columns and "dT_hotel" in df.columns:
        h = df[df["r_hotel"].notna() & df["dT_hotel"].notna()].copy()
        if len(h) == 0:
            print("  no cell carries both an r_hotel and a hotel draw -- NOT TESTABLE here")
        else:
            h["r_bin"] = np.where(h["r_hotel"] > 1.001, "r>1",
                                  np.where(h["r_hotel"] < 0.999, "r<1", "r==1"))
            g = h.groupby("r_bin").agg(
                n=("cell", "size"),
                dT_hotel_mean=("dT_hotel", "mean"),
                dT_peakdec_mean=("hotel_dT_peakdecile", "mean"),
                r_mean=("r_hotel", "mean"))
            print(g.to_string())
            if {"r>1", "r==1"}.issubset(set(g.index)):
                d = g.loc["r>1", "dT_hotel_mean"] - g.loc["r==1", "dT_hotel_mean"]
                print("\n  delta(r>1 minus r==1) = %+.3f K" % d)
                print("  VERDICT: %s" % ("CONFIRMED (lower, as predicted)" if d < 0
                                         else "REFUTED -- capacity explanation must be re-opened"))
            else:
                print("\n  bins present: %s -- comparison not available, NOT TESTABLE"
                      % list(g.index))
        if len(h):
            cc = h[["r_hotel", "dT_hotel"]].corr().iloc[0, 1]
            print("  corr(r_hotel, dT_hotel) = %.4f  (predict NEGATIVE)" % cc)
    else:
        print("  columns absent -- NOT TESTABLE")


if __name__ == "__main__":
    main()
