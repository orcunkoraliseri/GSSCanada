"""V3 checker. Scores V3b against the PRE-REGISTERED tolerance and summarises V3a spread.

    py -3 v3_check.py selftest [--frozen DIR] [--out DIR]
    py -3 v3_check.py v3b <runs_root>/V3b [--frozen DIR] [--out DIR]
    py -3 v3_check.py v3a <agg_root> [--frozen-agg DIR] [--out DIR]

PRE-REGISTERED TOLERANCE (written 2026-09-22 before any V3 run; IMP/V3_design_and_runs.md sec. 3).
A comparison "A vs B" of two cells PASSES iff, for EVERY column of hourly_meters.csv (15 meters) and
channel_hourly.csv (36 channel x end-use series):
    annual:  |sum A - sum B| / max(|sum B|, 1e-9 * site_J(B))                <= TOL_ANN    = 1e-6
    hourly:  max_t |A_t - B_t| / max(max_t |B_t|, 1e-9 * peak_site_W(B))     <= TOL_HOURLY = 1e-4
and both files have identical shape and column names. site_J = Electricity:Facility +
NaturalGas:Facility annual sum; peak_site = max hourly of that sum (floors keep all-zero columns
from dividing by zero).

V3b verdict, per building-city cell (4 cells):
    noise   U2 vs U  must PASS with margin: both worst metrics <= TOL/10    (else NOT_EVALUABLE)
    control X  vs R  must FAIL                                            (else NOT_EVALUABLE: blind)
    gate    N  vs R  PASS / FAIL
  overall PASS iff every cell's run set is complete, noise ok, control fired, gate PASS in 4/4.
  REPORTED, never gated: U vs R (effect of the injection CONTRACT on code schedules: lights and
  equipment follow the occupancy schedule; apartments on fixed K), N vs U (whole injection-path
  effect), U(Speed) vs frozen local win32 (cross-platform).
Exit code: 0 PASS, 1 FAIL, 2 NOT_EVALUABLE (a run missing/failed, noise too large, or control did
not fire), 3 the checker itself crashed. The summary keeps DID_NOT_RUN / RAN_NOT_FIRED / FIRED
apart for the control, and DID_NOT_RUN / PASS / FAIL for every comparison.
"""
import argparse
import glob
import json
import os
import shutil
import sys
import tempfile
import traceback

import numpy as np
import pandas as pd

TOL_ANN = 1e-6
TOL_HOURLY = 1e-4
NOISE_FRACTION = 0.1
FILES = ("hourly_meters.csv", "channel_hourly.csv")
CELLS = [(b, c) for b in ("Tall", "SuperTall") for c in ("MTL", "CLG")]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FROZEN = os.path.abspath(os.path.join(HERE, *([".."] * 5), "Leg3_4-split", "Step8_docs",
                                              "campaign_local_deliverable"))


def _ok_dir(d):
    if not d or not os.path.isdir(d):
        return False, "missing dir"
    m = os.path.join(d, "manifest.json")
    if os.path.isfile(m):
        try:
            st = json.load(open(m)).get("status")
            if st is not None and st != "ok":
                return False, "manifest status=%s" % st
        except Exception as e:
            return False, "manifest unreadable: %r" % e
    for f in FILES:
        if not os.path.isfile(os.path.join(d, f)):
            return False, "missing %s" % f
    return True, ""


def compare(a, b):
    """-> dict(status in PASS/FAIL/DID_NOT_RUN, worst_ann, worst_hourly, per-column table)."""
    for d in (a, b):
        ok, why = _ok_dir(d)
        if not ok:
            return {"status": "DID_NOT_RUN", "why": "%s: %s" % (d, why)}
    hb = pd.read_csv(os.path.join(b, "hourly_meters.csv"))
    site = hb["Electricity:Facility"] + hb["NaturalGas:Facility"]
    site_J, peak_W = float(site.sum()), float(site.abs().max())
    rows = []
    shape_ok = True
    for f in FILES:
        A = pd.read_csv(os.path.join(a, f))
        B = pd.read_csv(os.path.join(b, f))
        if list(A.columns) != list(B.columns) or A.shape != B.shape:
            shape_ok = False
            rows.append({"file": f, "column": "*SHAPE*", "ann": np.inf, "hourly": np.inf})
            continue
        for col in B.columns:
            xa, xb = A[col].to_numpy(float), B[col].to_numpy(float)
            ann = abs(xa.sum() - xb.sum()) / max(abs(xb.sum()), 1e-9 * site_J)
            hr = np.abs(xa - xb).max() / max(np.abs(xb).max(), 1e-9 * peak_W)
            rows.append({"file": f, "column": col, "ann": float(ann), "hourly": float(hr),
                         "sum_A": float(xa.sum()), "sum_B": float(xb.sum())})
    t = pd.DataFrame(rows)
    wa, wh = float(t["ann"].max()), float(t["hourly"].max())
    passed = shape_ok and wa <= TOL_ANN and wh <= TOL_HOURLY
    ia, ih = t["ann"].idxmax(), t["hourly"].idxmax()
    return {"status": "PASS" if passed else "FAIL", "worst_ann": wa, "worst_hourly": wh,
            "worst_ann_col": "%s:%s" % (t.at[ia, "file"], t.at[ia, "column"]),
            "worst_hourly_col": "%s:%s" % (t.at[ih, "file"], t.at[ih, "column"]),
            "n_cols": len(t), "n_cols_fail": int(((t["ann"] > TOL_ANN) | (t["hourly"] > TOL_HOURLY)).sum()),
            "table": t}


def effect_table(a, b):
    """Reported effect A vs B per channel end-use (annual relative change, %)."""
    r = compare(a, b)
    if r["status"] == "DID_NOT_RUN":
        return None, r
    t = r["table"]
    t = t[t["column"] != "*SHAPE*"].copy()
    t["rel_change_pct"] = np.where(t["sum_B"].abs() > 0, 100 * (t["sum_A"] - t["sum_B"]) / t["sum_B"].abs(), 0.0)
    return t[["file", "column", "sum_A", "sum_B", "rel_change_pct", "hourly"]], r


def run_dir(root, arm, b, c):
    hits = sorted(glob.glob(os.path.join(root, "%s__Default_NECB__%s__%s__s*" % (arm, b, c))))
    hits = [h for h in hits if "__smoke" not in h]
    return hits[0] if hits else None


def score_v3b(root, frozen, out):
    os.makedirs(out, exist_ok=True)
    cells, lines = {}, []
    overall_missing = overall_noise = overall_blind = False
    n_gate_pass = 0
    effects = []
    for b, c in CELLS:
        d = {arm: run_dir(root, arm, b, c) for arm in ("U", "U2", "R", "N", "X")}
        noise = compare(d["U2"], d["U"])
        ctrl = compare(d["X"], d["R"])
        gate = compare(d["N"], d["R"])
        xplat = compare(d["U"], os.path.join(frozen, "Default_NECB__%s__%s" % (b, c)))
        ctrl_state = {"DID_NOT_RUN": "DID_NOT_RUN", "PASS": "RAN_NOT_FIRED", "FAIL": "FIRED"}[ctrl["status"]]
        noise_ok = (noise["status"] == "PASS" and noise["worst_ann"] <= NOISE_FRACTION * TOL_ANN
                    and noise["worst_hourly"] <= NOISE_FRACTION * TOL_HOURLY)
        missing = "DID_NOT_RUN" in (noise["status"], ctrl["status"], gate["status"])
        if missing:
            v = "NOT_EVALUABLE (did not run)"
            overall_missing = True
        elif not noise_ok:
            v = "NOT_EVALUABLE (noise floor above TOL/10)"
            overall_noise = True
        elif ctrl_state != "FIRED":
            v = "NOT_EVALUABLE (negative control did not fire)"
            overall_blind = True
        else:
            v = gate["status"]
            n_gate_pass += v == "PASS"
        cells["%s_%s" % (b, c)] = {
            "verdict": v, "control": ctrl_state,
            **{k: {kk: vv for kk, vv in r.items() if kk != "table"} for k, r in
               (("noise_U2_vs_U", noise), ("control_X_vs_R", ctrl), ("gate_N_vs_R", gate),
                ("xplatform_U_vs_frozen", xplat))}}
        for name, (A, B) in (("contract_U_vs_R", (d["U"], d["R"])), ("path_N_vs_U", (d["N"], d["U"])),
                             ("xplatform_U_vs_frozen", (d["U"], os.path.join(frozen, "Default_NECB__%s__%s" % (b, c))))):
            t, _ = effect_table(A, B) if A else (None, None)
            if t is not None:
                t.insert(0, "comparison", name)
                t.insert(0, "cell", "%s_%s" % (b, c))
                effects.append(t)
    if overall_missing:
        overall, code = "NOT_EVALUABLE (did not run)", 2
    elif overall_noise:
        overall, code = "NOT_EVALUABLE (noise floor)", 2
    elif overall_blind:
        overall, code = "NOT_EVALUABLE (control did not fire)", 2
    elif n_gate_pass == len(CELLS):
        overall, code = "PASS", 0
    else:
        overall, code = "FAIL", 1
    res = {"TOL_ANN": TOL_ANN, "TOL_HOURLY": TOL_HOURLY, "NOISE_FRACTION": NOISE_FRACTION,
           "overall": overall, "exit_code": code, "cells": cells}
    json.dump(res, open(os.path.join(out, "v3b_scorecard.json"), "w"), indent=2, default=str)
    if effects:
        pd.concat(effects).to_csv(os.path.join(out, "v3b_effects.csv"), index=False)
    lines.append("V3b overall: %s (exit %d)" % (overall, code))
    for k, v in cells.items():
        g, n, x = v["gate_N_vs_R"], v["noise_U2_vs_U"], v["control_X_vs_R"]
        lines.append("  %-14s %-44s gate=%s ann=%s hr=%s | noise=%s | control=%s (ann=%s hr=%s)" % (
            k, v["verdict"], g["status"], _f(g.get("worst_ann")), _f(g.get("worst_hourly")),
            n["status"], v["control"], _f(x.get("worst_ann")), _f(x.get("worst_hourly"))))
    txt = "\n".join(lines)
    open(os.path.join(out, "v3b_summary.txt"), "w").write(txt + "\n")
    print(txt)
    return code


def _f(x):
    return "n/a" if x is None else "%.3g" % x


# ------------------------------------------------------------------------------------------------
# V3a: spread of the published metrics across residential-draw seeds (reported, never gated)
# ------------------------------------------------------------------------------------------------
def summarise_v3a(agg_root, frozen_agg, out):
    os.makedirs(out, exist_ok=True)
    seeds = sorted(d for d in os.listdir(agg_root) if d.startswith("seed"))
    if not seeds:
        print("V3a: no seed*/ aggregate dirs under", agg_root)
        return 2
    eui, peak = [], []
    for s in seeds:
        d = os.path.join(agg_root, s)
        e = pd.read_csv(os.path.join(d, "agg_annual_by_channel.csv"))
        e["seed"] = int(s[4:])
        eui.append(e)
        p = pd.read_csv(os.path.join(d, "agg_peak.csv"))
        p["seed"] = int(s[4:])
        peak.append(p)
    E, P = pd.concat(eui), pd.concat(peak)
    E = E.merge(pd.read_csv(os.path.join(agg_root, seeds[0], "agg_meta.csv"))[["cell_tag", "scenario", "building", "city"]],
                on="cell_tag", how="left")
    g = E.groupby(["scenario", "building", "city", "channel"])["eui_CFA_kWh_m2"]
    se = g.agg(["count", "mean", "std", "min", "max"]).reset_index()
    se["range"] = se["max"] - se["min"]
    se["cv_pct"] = 100 * se["std"] / se["mean"]
    if frozen_agg and os.path.isdir(frozen_agg):
        fz = pd.read_csv(os.path.join(frozen_agg, "agg_annual_by_channel.csv"))
        fz = fz.merge(pd.read_csv(os.path.join(frozen_agg, "agg_meta.csv"))[["cell_tag", "scenario", "building", "city"]],
                      on="cell_tag")
        se = se.merge(fz[["scenario", "building", "city", "channel", "eui_CFA_kWh_m2"]].rename(
            columns={"eui_CFA_kWh_m2": "frozen_eui"}), on=["scenario", "building", "city", "channel"], how="left")
    se.to_csv(os.path.join(out, "v3a_eui_spread.csv"), index=False)
    # scenario delta per seed (same seed pairs), then its spread
    piv = E.pivot_table(index=["building", "city", "channel", "seed"], columns="scenario",
                        values="eui_CFA_kWh_m2").reset_index()
    if {"B_central", "Y2022"} <= set(piv.columns):
        piv["delta_2030_minus_2022"] = piv["B_central"] - piv["Y2022"]
        sd = piv.groupby(["building", "city", "channel"])["delta_2030_minus_2022"].agg(
            ["count", "mean", "std", "min", "max"]).reset_index()
        sd.to_csv(os.path.join(out, "v3a_delta_spread.csv"), index=False)
    P = P.merge(pd.read_csv(os.path.join(agg_root, seeds[0], "agg_meta.csv"))[["cell_tag", "scenario", "building", "city"]],
                on="cell_tag", how="left")
    cols = [c for c in ("peak_hour_circular", "peak_hour_argmax", "coincidence_factor") if c in P.columns]
    sp = P.groupby(["scenario", "building", "city", "channel", "daytype", "metric"])[cols].agg(["mean", "std", "min", "max"])
    sp.columns = ["%s_%s" % c for c in sp.columns]
    sp.reset_index().to_csv(os.path.join(out, "v3a_peak_spread.csv"), index=False)
    print("V3a: %d seeds (%s); wrote v3a_eui_spread.csv, v3a_delta_spread.csv, v3a_peak_spread.csv to %s"
          % (len(seeds), ",".join(seeds), out))
    print(se.sort_values("cv_pct", ascending=False).head(12).to_string(index=False))
    return 0


# ------------------------------------------------------------------------------------------------
# selftest: the checker must be SEEN FAILING on real captures before its PASS is trusted
# ------------------------------------------------------------------------------------------------
def selftest(frozen, out):
    tmp = tempfile.mkdtemp(prefix="v3check_")
    try:
        U = os.path.join(frozen, "Default_NECB__Tall__MTL")
        Y = os.path.join(frozen, "Y2022__Tall__MTL")
        res = []

        def mk(name, src, col=None, how=None, k=None):
            d = os.path.join(tmp, name)
            os.makedirs(d)
            for f in FILES:
                shutil.copy(os.path.join(src, f), d)
            if col:
                p = os.path.join(d, "channel_hourly.csv")
                t = pd.read_csv(p)
                if how == "scale":
                    t[col] = t[col] * (1 + k)
                elif how == "spike":
                    t.loc[4000, col] = t.loc[4000, col] + k * t[col].abs().max()
                t.to_csv(p, index=False)
            return d

        cases = [
            ("identical real capture", mk("same", U), "PASS"),
            ("Y2022 cell vs Default cell (wrong input)", mk("y", Y), "FAIL"),
            ("office_lights x(1+2e-6) (annual 2x tol)", mk("s2", U, "office_lights", "scale", 2e-6), "FAIL"),
            ("office_lights x(1+5e-7) (annual 0.5x tol)", mk("s05", U, "office_lights", "scale", 5e-7), "PASS"),
            ("one-hour spike 2e-4 x peak (hourly 2x tol)", mk("h2", U, "office_lights", "spike", 2e-4), "FAIL"),
        ]
        for name, d, exp in cases:
            r = compare(d, U)
            res.append((name, exp, r["status"], r.get("worst_ann"), r.get("worst_hourly")))
        r = compare(os.path.join(tmp, "nope"), U)
        res.append(("missing run dir", "DID_NOT_RUN", r["status"], None, None))
        # verdict logic on synthetic run trees made of real captures
        vt = []
        for scen, arms, exp in [
            ("all arms = Default, X = Y2022", {"U": U, "U2": U, "R": U, "N": U, "X": Y}, "PASS"),
            ("N = Y2022 (gate must fail)", {"U": U, "U2": U, "R": U, "N": Y, "X": Y}, "FAIL"),
            ("X = Default (control cannot fire)", {"U": U, "U2": U, "R": U, "N": U, "X": U}, "NOT_EVALUABLE (control did not fire)"),
            ("U2 missing", {"U": U, "R": U, "N": U, "X": Y}, "NOT_EVALUABLE (did not run)"),
            ("U2 = Y2022 (noise floor too large)", {"U": U, "U2": Y, "R": U, "N": U, "X": Y}, "NOT_EVALUABLE (noise floor)"),
        ]:
            root = os.path.join(tmp, "tree_%d" % len(vt))
            for b, c in CELLS:
                for arm, src in arms.items():
                    d = os.path.join(root, "%s__Default_NECB__%s__%s__s0" % (arm, b, c))
                    os.makedirs(d)
                    for f in FILES:
                        shutil.copy(os.path.join(src, f), d)
            import io
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                code = score_v3b(root, frozen, os.path.join(tmp, "o%d" % len(vt)))
            got = json.load(open(os.path.join(tmp, "o%d" % len(vt), "v3b_scorecard.json")))["overall"]
            vt.append((scen, exp, got, code))
        lines = ["V3 checker selftest (real frozen captures, %s)" % U]
        allok = True
        for name, exp, got, wa, wh in res:
            ok = got == exp
            allok &= ok
            lines.append("  [%s] %-46s expect %-12s got %-12s ann=%s hr=%s" % ("ok" if ok else "XX", name, exp, got, _f(wa), _f(wh)))
        for name, exp, got, code in vt:
            ok = got == exp
            allok &= ok
            lines.append("  [%s] verdict: %-38s expect %-40s got %s (exit %d)" % ("ok" if ok else "XX", name, exp, got, code))
        lines.append("SELFTEST %s" % ("PASS" if allok else "FAIL"))
        txt = "\n".join(lines)
        print(txt)
        if out:
            os.makedirs(out, exist_ok=True)
            open(os.path.join(out, "v3_check_selftest.txt"), "w").write(txt + "\n")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "v3b", "v3a"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--frozen", default=DEFAULT_FROZEN)
    ap.add_argument("--frozen-agg", default=os.path.abspath(os.path.join(DEFAULT_FROZEN, "..", "outputs_step8", "agg_deliverable")))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    try:
        if a.mode == "selftest":
            return selftest(a.frozen, a.out)
        if a.mode == "v3b":
            return score_v3b(a.path, a.frozen, a.out or os.path.join(a.path, "_check"))
        return summarise_v3a(a.path, a.frozen_agg, a.out or os.path.join(a.path, "_check"))
    except Exception:
        traceback.print_exc()
        print("CHECKER CRASHED -> exit 3 (this is NOT a V3 verdict)")
        return 3


if __name__ == "__main__":
    sys.exit(main())
