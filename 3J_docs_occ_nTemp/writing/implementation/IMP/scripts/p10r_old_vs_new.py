#!/usr/bin/env python3
"""P10R old-vs-new table for P10_2030_level_check.md section 6 (2026-09-25).

Every metric is computed by ONE function on BOTH arms (frozen `outputs_step9_deliverable` +
`agg_deliverable`, and `outputs_step9_P10R` + `agg_P10R`), next to the number the manuscript prints.
Control: the OLD column must reproduce the published number (within the rounding of the print);
a metric whose old column does not reproduce it is flagged OLD!=PUB and must not be used to
substitute a marker until its definition is fixed.

Writes IMP/data/P10R/P10R_old_vs_new.csv and .md. Read-only on both arms.
Run: PYTHONIOENCODING=utf-8 py -3 p10r_old_vs_new.py
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEG3 = os.path.join(J3, "Leg3_4-split")
ARMS = {
    "old": dict(s9=os.path.join(LEG3, "Step9_docs", "outputs_step9_deliverable"),
                agg=os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_deliverable")),
    "new": dict(s9=os.path.join(LEG3, "Step9_docs", "outputs_step9_P10R"),
                agg=os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_P10R")),
}
OUT = os.path.join(J3, "writing", "implementation", "IMP", "data", "P10R")
os.makedirs(OUT, exist_ok=True)
TENANT = ["office", "retail", "hotel", "residential"]


def load(arm):
    d = ARMS[arm]
    r = {k: pd.read_csv(os.path.join(d["s9"], f"step9_{k}.csv"))
         for k in ("eui_by_channel", "longitudinal", "scenario_response", "loadshape_peaks")}
    r["gates"] = json.load(open(os.path.join(d["s9"], "step9_gates.json"), encoding="utf-8"))
    r["peak"] = pd.read_csv(os.path.join(d["agg"], "agg_peak.csv"))
    r["diur"] = pd.read_csv(os.path.join(d["agg"], "agg_diurnal.csv"))
    return r


def circ(w):
    w = np.asarray(w, float)
    a = 2 * np.pi * np.arange(len(w)) / len(w)
    m = np.arctan2((w * np.sin(a)).sum(), (w * np.cos(a)).sum())
    return float((m % (2 * np.pi)) / (2 * np.pi) * len(w))


def wd(diur, cell, ch):
    d = diur[(diur.cell_tag == cell) & (diur.channel == ch) & (diur.season == "all")
             & (diur.daytype == "WD") & (diur.metric == "energy_W")]
    return d.sort_values("hour")["W"].to_numpy()[:24]


def metrics(A):
    m = {}
    e = A["eui_by_channel"]
    # Table 5 / section 5.2: 56-cell EUI (CFA) per channel
    for ch in TENANT:
        v = e[e.channel == ch]
        m[f"T5 {ch} EUI median"] = v.eui_CFA_kWh_m2.median()
        m[f"T5 {ch} EUI min"] = v.eui_CFA_kWh_m2.min()
        m[f"T5 {ch} EUI max"] = v.eui_CFA_kWh_m2.max()
        if ch != "residential":
            m[f"T5 {ch} cells in band (of 56)"] = int((v.verdict_asmodelled == "PASS").sum())
    necb = e[(e.scenario == "Default_NECB") & (e.channel == "office")].eui_CFA_kWh_m2
    m["5.2 Default_NECB office EUI median"] = necb.median()
    # Section 5.1: Y2022 EUI and change vs 2005 (median over the 4 building-city cells)
    lon = A["longitudinal"]
    for ch in TENANT:
        y = lon[(lon.scenario == "Y2022") & (lon.channel == ch)]
        m[f"5.1 {ch} Y2022 EUI median"] = y.eui_CFA_kWh_m2.median()
        m[f"5.1 {ch} Y2022 % vs 2005 median"] = y.energy_pct_vs_2005.median()
        m[f"5.1 {ch} Y2022 % vs 2005 min"] = y.energy_pct_vs_2005.min()
        m[f"5.1 {ch} Y2022 % vs 2005 max"] = y.energy_pct_vs_2005.max()
    # Section 5.1: energy / area shares over the four cycle years (all 16 cells pooled)
    cyc = e[e.scenario.isin(["Y2005", "Y2010", "Y2015", "Y2022"])]
    en = cyc.groupby("channel").energy_GJ.sum()
    ar = cyc.groupby("channel").area_m2.sum()
    allen = cyc.energy_GJ.sum()
    for ch in TENANT:
        m[f"5.1 {ch} energy share % (cycles, tenant-sum)"] = 100 * en[ch] / allen
        m[f"5.1 {ch} area share % (cycles, tenant-sum)"] = 100 * ar[ch] / ar.sum()
        m[f"5.1 {ch} energy_share_pct median (cycles)"] = cyc[cyc.channel == ch].energy_share_pct.median()
        m[f"5.1 {ch} area_share_pct median (cycles)"] = cyc[cyc.channel == ch].area_share_pct.median()
    # Section 5.3: 2030 central (4 cells)
    diur, peak = A["diur"], A["peak"]
    bc = sorted({c for c in e.cell_tag if c.startswith("B_central__")})
    for ch in TENANT:
        hs = [circ(wd(diur, c, ch)) for c in bc]
        m[f"5.3 {ch} WD peak hour median"] = float(np.median(hs))
        m[f"5.3 {ch} WD peak hour min"] = min(hs)
        m[f"5.3 {ch} WD peak hour max"] = max(hs)
        pr = [wd(diur, c, ch) for c in bc]
        m[f"5.3 {ch} WD midday kW median"] = float(np.median([p[11:15].mean() / 1000 for p in pr]))
        m[f"5.3 {ch} WD night kW median"] = float(np.median([np.r_[p[0:5], p[22:24]].mean() / 1000 for p in pr]))
    b = peak[(peak.channel == "_BUILDING") & peak.cell_tag.isin(bc)]
    m["5.3 building peak hour median"] = b.peak_hour_circular.median()
    m["5.3 building peak hour min"] = b.peak_hour_circular.min()
    m["5.3 building peak hour max"] = b.peak_hour_circular.max()
    m["5.3 coincidence factor median"] = b.coincidence_factor.median()
    m["5.3 coincidence factor min"] = b.coincidence_factor.min()
    # Section 5.4: within-2030 band response vs central (range over 4 cells)
    sr = A["scenario_response"]
    for s in ("B_cons", "B_opt"):
        for ch in TENANT:
            v = sr[(sr.scenario == s) & (sr.channel == ch)].energy_pct_vs_Bcentral
            m[f"5.4 {ch} {s} % vs central min"] = v.min()
            m[f"5.4 {ch} {s} % vs central max"] = v.max()
    # Scorecard
    st = pd.Series([g["status"] for g in A["gates"]]).value_counts()
    for k in ("PASS", "WARN", "FAIL", "INFO"):
        m[f"scorecard {k}"] = int(st.get(k, 0))
    for g in A["gates"]:
        if g["gate"].startswith("S9-EUI-") and g["gate"] != "S9-EUI-EXPOSURE":
            m[f"gate {g['gate']}"] = g["status"]
    return m


# Published values (manuscript as printed; source: P10_2030_level_check.md section 6 and P3 controls).
PUB = {
    "T5 office EUI median": 71.02, "T5 office EUI min": 61.72, "T5 office EUI max": 90.21,
    "T5 retail EUI median": 75.63, "T5 retail EUI min": 63.63, "T5 retail EUI max": 96.84,
    "T5 retail cells in band (of 56)": 12,
    "T5 hotel EUI median": 260.54, "T5 hotel EUI min": 203.33, "T5 hotel EUI max": 318.42,
    "T5 hotel cells in band (of 56)": 28,
    "T5 residential EUI median": 119.10, "T5 residential EUI min": 111.57, "T5 residential EUI max": 128.77,
    "5.2 Default_NECB office EUI median": 85.45,
    "5.1 office Y2022 EUI median": 70.20, "5.1 office Y2022 % vs 2005 median": -0.67,
    "5.1 retail Y2022 EUI median": 79.19, "5.1 retail Y2022 % vs 2005 median": 2.36,
    "5.1 retail Y2022 % vs 2005 min": 0.13, "5.1 retail Y2022 % vs 2005 max": 4.69,
    "5.1 residential Y2022 EUI median": 118.68, "5.1 residential Y2022 % vs 2005 median": -0.07,
    "5.1 hotel Y2022 % vs 2005 median": 0.09,
    "5.3 office WD peak hour median": 11.90, "5.3 residential WD peak hour median": 12.04,
    "5.3 retail WD peak hour median": 12.37, "5.3 hotel WD peak hour median": 18.91,
    "5.3 residential WD peak hour min": 12.01, "5.3 residential WD peak hour max": 12.10,
    "5.3 retail WD peak hour min": 12.11, "5.3 retail WD peak hour max": 12.62,
    "5.3 hotel WD peak hour min": 18.84, "5.3 hotel WD peak hour max": 18.94,
    "5.3 building peak hour median": 14.95, "5.3 building peak hour min": 14.11, "5.3 building peak hour max": 15.70,
    "5.3 office WD midday kW median": 569.33, "5.3 office WD night kW median": 48.10,
    "5.3 retail WD midday kW median": 72.03, "5.3 retail WD night kW median": 2.11,
    "5.3 residential WD midday kW median": 347.82, "5.3 residential WD night kW median": 89.53,
    "5.3 hotel WD midday kW median": 335.93, "5.3 hotel WD night kW median": 434.47,
    "5.3 coincidence factor median": 0.941, "5.3 coincidence factor min": 0.851,
    "5.1 hotel energy_share_pct median (cycles)": 44.47, "5.1 hotel area_share_pct median (cycles)": 20.25,
    "5.1 office energy_share_pct median (cycles)": 21.42, "5.1 office area_share_pct median (cycles)": 35.14,
    "5.1 residential energy_share_pct median (cycles)": 18.27, "5.1 residential area_share_pct median (cycles)": 17.73,
    "5.1 retail energy_share_pct median (cycles)": 2.56, "5.1 retail area_share_pct median (cycles)": 3.92,
    # the three OLD!=PUB rows are known (P3_code_schedule_comparison.md controls): 85.45 is a constant
    # hard-coded in the Step-9 band text (median is 85.36); 2.11 and 14.11 are double-rounded prints.
    "scorecard PASS": 17, "scorecard FAIL": 3, "scorecard INFO": 10,
}


def dp(p):
    s = f"{p}"
    return len(s.split(".")[1]) if "." in s else 0


def main():
    old, new = metrics(load("old")), metrics(load("new"))
    rows = []
    for k in old:
        o, n, p = old[k], new.get(k), PUB.get(k)
        row = dict(metric=k, published=p, old=o, new=n)
        if isinstance(o, str):
            row["change"] = "" if o == n else f"{o} -> {n}"
            row["old_reproduces_published"] = ""
        else:
            row["change"] = n - o
            row["change_pct"] = 100 * (n - o) / abs(o) if o else np.nan
            if p is None:
                row["old_reproduces_published"] = "no published value"
            else:
                tol = 0.5 * 10 ** (-dp(p)) + 1e-9
                # printed ranges were sometimes double-rounded (3 dp then 2 dp; P3 control notes)
                ok = abs(o - p) <= tol or abs(round(round(o, 3), dp(p)) - p) <= 1e-9
                row["old_reproduces_published"] = "yes" if ok else "OLD!=PUB"
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "P10R_old_vs_new.csv"), index=False)
    pd.set_option("display.width", 220, "display.max_rows", 400)
    print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    c = df.old_reproduces_published.value_counts()
    print(f"\nCONTROL old column vs published: {dict(c)}")


if __name__ == "__main__":
    main()
