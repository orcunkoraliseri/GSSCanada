#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 2b (2026-09-25): value for every P10R marker in chapters_v2, one function on BOTH arms.

Every marker `⟦P10R:<old printed value>⟧` in chapters_v2/00,01,03,04,05,06 is matched to a registry
entry (file, line, k-th marker on the line). Each entry names ONE metric function; the function is run
on the OLD arm (frozen: outputs_step9_deliverable + agg_deliverable + campaign_local_deliverable) and on
the NEW arm (outputs_step9_P10R + agg_P10R + campaign_local_P10R), and both results are formatted in the
printed style of the marker.

CONTROL: a marker may be substituted only if the OLD formatted value equals the printed text (direct
rounding, or 3 dp then print dp: double rounding seen in earlier prints). Claim markers (text) are
substituted only if the claim holds on the old arm AND on the new arm; a claim that no longer holds
stays marked. Direction words (below/above, rise/fall) are substituted and flagged.
NEGATIVE CONTROLS: the same functions with a wrong scenario / channel / hour set / arm must NOT
reproduce the printed value. CODE-COLUMN CONTROLS: the reader must reproduce the Table 3 code-schedule
column (not markers) on both arms.

Read only on both arms. Writes IMP/data/P10R/P10R_marker_table.csv (+ .out via the shell).
With --apply it also replaces substituted markers in the chapter files (backup must exist).
Run: PYTHONIOENCODING=utf-8 py -3 p10r_marker_values.py [--apply]
"""
from __future__ import annotations

import math
import os
from decimal import ROUND_HALF_UP, Decimal
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEG3 = os.path.join(J3, "Leg3_4-split")
CH_DIR = os.path.join(J3, "writing", "chapters_v2")
BACKUP = os.path.join(CH_DIR, "_archive_pre_stage2b_2026-09-25")
OUT = os.path.join(J3, "writing", "implementation", "IMP", "data", "P10R")
ARMS = {
    "old": dict(s9=os.path.join(LEG3, "Step9_docs", "outputs_step9_deliverable"),
                agg=os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_deliverable"),
                cells=os.path.join(LEG3, "Step8_docs", "campaign_local_deliverable")),
    "new": dict(s9=os.path.join(LEG3, "Step9_docs", "outputs_step9_P10R"),
                agg=os.path.join(LEG3, "Step8_docs", "outputs_step8", "agg_P10R"),
                cells=os.path.join(LEG3, "Step8_docs", "campaign_local_P10R")),
}
FILES = ["00_FrontMatter.md", "01_Introduction.md", "03_Results.md", "04_Discussion.md",
         "05_Limitations.md", "06_Conclusion.md"]
TENANT = ["office", "retail", "hotel", "residential"]
CH6 = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]
BC = [("SuperTall", "MTL"), ("SuperTall", "CLG"), ("Tall", "MTL"), ("Tall", "CLG")]
CYCLES = ["Y2005", "Y2010", "Y2015", "Y2022"]
MARK = re.compile(r"⟦P10R:(.*?)⟧")


# ------------------------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------------------------
class Arm:
    def __init__(self, name):
        d = ARMS[name]
        self.name, self.cells = name, d["cells"]
        self.eui = pd.read_csv(os.path.join(d["s9"], "step9_eui_by_channel.csv"))
        self.lon = pd.read_csv(os.path.join(d["s9"], "step9_longitudinal.csv"))
        self.sr = pd.read_csv(os.path.join(d["s9"], "step9_scenario_response.csv"))
        self.diur = pd.read_csv(os.path.join(d["agg"], "agg_diurnal.csv"))
        self.diur = self.diur[(self.diur.season == "all")]
        self.peak = pd.read_csv(os.path.join(d["agg"], "agg_peak.csv"))
        self.meta = pd.read_csv(os.path.join(d["agg"], "agg_meta.csv")).set_index("cell_tag")
        self.annual = pd.read_csv(os.path.join(d["agg"], "agg_annual.csv"))
        self.abc = pd.read_csv(os.path.join(d["agg"], "agg_annual_by_channel.csv"))
        self._prof, self._hourly = {}, {}
        assert int(self.meta["attribution_closed"].sum()) == 56, name

    def prof(self, cell, ch, metric="energy_W", daytype="WD"):
        k = (cell, ch, metric, daytype)
        if k not in self._prof:
            d = self.diur[(self.diur.cell_tag == cell) & (self.diur.channel == ch)
                          & (self.diur.daytype == daytype) & (self.diur.metric == metric)]
            p = d.sort_values("hour")["W"].to_numpy(float)
            assert len(p) == 24, (cell, ch, metric, len(p))
            self._prof[k] = p
        return self._prof[k]

    # hourly per-channel energy reconstruction (same logic as p3_code_schedule_comparison.py,
    # itself verbatim Step-8E aggregate_cell); used for the 4-use coincidence factor and annual peak
    def hourly(self, cell):
        if cell in self._hourly:
            return self._hourly[cell]
        d = os.path.join(self.cells, cell)
        hourly = pd.read_csv(os.path.join(d, "hourly_meters.csv"))
        chan = pd.read_csv(os.path.join(d, "channel_hourly.csv"))
        dhw = pd.read_csv(os.path.join(d, "dhw_hourly.csv"))
        mm = self.meta.loc[cell]
        area = np.array([mm[f"area_{c}_m2"] for c in CH6], float)
        fb = area / area.sum()

        def shares(m):
            m = np.abs(m)
            tot = m.sum(axis=1)
            out = np.zeros_like(m)
            nz = tot > 0
            out[nz] = m[nz] / tot[nz][:, None]
            out[~nz] = fb
            return out
        basis = {
            "cool": shares(chan[[f"{c}_syscool" for c in CH6]].to_numpy(float)),
            "heat": shares(chan[[f"{c}_sysheat" for c in CH6]].to_numpy(float)),
            "hvac": shares(np.column_stack([chan[f"{c}_syscool"].abs() + chan[f"{c}_sysheat"].abs()
                                            for c in CH6])),
            "dhw": shares(dhw[[f"dhw_{c}" for c in CH6]].to_numpy(float)),
        }
        end_uses = [("InteriorLights:Electricity", "direct:lights"),
                    ("InteriorEquipment:Electricity", "direct:equip"),
                    ("InteriorEquipment:NaturalGas", "direct:gasequip"),
                    ("WaterSystems:Electricity", "dhw"), ("WaterSystems:NaturalGas", "dhw"),
                    ("Cooling:Electricity", "cool"), ("Heating:Electricity", "heat"),
                    ("Heating:NaturalGas", "heat"), ("Fans:Electricity", "hvac"),
                    ("Pumps:Electricity", "hvac"), ("HeatRejection:Electricity", "cool"),
                    ("HeatRecovery:Electricity", "hvac")]
        tot = np.zeros((len(hourly), len(CH6)))
        for meter, b in end_uses:
            if meter not in hourly.columns:
                continue
            s = hourly[meter].to_numpy(float)
            if b.startswith("direct:"):
                tot += chan[[f"{c}_{b.split(':')[1]}" for c in CH6]].to_numpy(float)
            else:
                tot += basis[b] * s[:, None]
        self._hourly[cell] = tot / 3600.0
        return self._hourly[cell]


def cells(scen):
    return [f"{scen}__{b}__{c}" for b, c in BC]


def circ(w):
    w = np.asarray(w, float)
    a = 2 * np.pi * np.arange(len(w)) / len(w)
    m = np.arctan2((w * np.sin(a)).sum(), (w * np.cos(a)).sum())
    return float((m % (2 * np.pi)) / (2 * np.pi) * len(w))


def mid_night(p):
    return p[11:15].mean() / np.r_[p[0:5], p[22:24]].mean()


# ------------------------------------------------------------------------------------------------
# Metric functions: f(arm) -> float | list[float] | bool | str.  ONE function for both arms.
# ------------------------------------------------------------------------------------------------
def presence(scen, ch, hours):
    """Weekday occupants per 100 m2 (agg_diurnal metric 'people', season all, WD), mean over `hours`,
    median over the 4 tower-city models."""
    def f(A):
        return float(np.median([100 * A.prof(c, ch, "people")[hours].mean() / A.meta.loc[c, f"area_{ch}_m2"]
                                for c in cells(scen)]))
    return f


def presence_range_over(scens, ch, hours):
    def f(A):
        return [presence(s, ch, hours)(A) for s in scens]
    return f


def occ_peak_hour(scen, ch):
    """Occupant peak hour = median over 4 models of argmax of the WD people profile."""
    def f(A):
        return float(np.median([int(np.argmax(A.prof(c, ch, "people"))) for c in cells(scen)]))
    return f


def lon_eui(scen, ch):
    def f(A):
        return float(A.lon[(A.lon.scenario == scen) & (A.lon.channel == ch)].eui_CFA_kWh_m2.median())
    return f


def lon_pct(scen, ch, agg="median"):
    def f(A):
        v = A.lon[(A.lon.scenario == scen) & (A.lon.channel == ch)].energy_pct_vs_2005
        return float(v.median()) if agg == "median" else v.tolist()
    return f


def share(ch, col):
    """energy_share_pct / area_share_pct, median over the 16 cycle cells (Y2005..Y2022 x 4 models)."""
    def f(A):
        e = A.eui[A.eui.scenario.isin(CYCLES) & (A.eui.channel == ch)]
        return float(e[col].median())
    return f


def energy_peak_hour(scen, ch):
    def f(A):
        return float(np.median([circ(A.prof(c, ch)) for c in cells(scen)]))
    return f


def ratio(scen, ch):
    """Weekday midday (11-14) / night (22-23, 0-4) energy ratio, median over 4 models."""
    def f(A):
        return float(np.median([mid_night(A.prof(c, ch)) for c in cells(scen)]))
    return f


def ratio_building(scen):
    def f(A):
        return float(np.median([mid_night(sum(A.prof(c, ch) for ch in CH6)) for c in cells(scen)]))
    return f


def eui_med(scen, ch):
    def f(A):
        return float(A.eui[(A.eui.scenario == scen) & (A.eui.channel == ch)].eui_CFA_kWh_m2.median())
    return f


def bld_peak(scen, col):
    """agg_peak _BUILDING row: peak_hour_circular (load centroid, all days) or coincidence_factor (6 ch)."""
    def f(A):
        b = A.peak[(A.peak.channel == "_BUILDING") & A.peak.cell_tag.isin(cells(scen))]
        assert len(b) == 4
        return float(b[col].median())
    return f


def bld_peak_cells(scen, col):
    def f(A):
        b = A.peak[(A.peak.channel == "_BUILDING")].set_index("cell_tag")
        return [float(b.loc[c, col]) for c in cells(scen)]
    return f


def cf4(scen):
    def f(A):
        v = []
        for c in cells(scen):
            W = A.hourly(c)[:, :4]
            v.append(W.sum(axis=1).max() / W.max(axis=0).sum())
        return float(np.median(v))
    return f


def delta_vs_code(kind, ch, scen="Y2022"):
    """Per-model change of the survey scenario against Default_NECB (same building-city):
    kind 'eui' = % change of CFA EUI; 'wdpeak' = signed circular shift of the WD energy peak hour (h);
    'centroid' = shift of the building all-days peak_hour_circular (h); 'cf6' = change of the 6-channel CF."""
    def f(A):
        out = []
        for (b, c) in BC:
            s, n = f"{scen}__{b}__{c}", f"Default_NECB__{b}__{c}"
            if kind == "eui":
                g = A.eui.set_index(["cell_tag", "channel"]).eui_CFA_kWh_m2
                out.append(100 * (g[(s, ch)] / g[(n, ch)] - 1))
            elif kind == "wdpeak":
                out.append((circ(A.prof(s, ch)) - circ(A.prof(n, ch)) + 12) % 24 - 12)
            elif kind == "centroid":
                p = A.peak[A.peak.channel == "_BUILDING"].set_index("cell_tag").peak_hour_circular
                out.append((p[s] - p[n] + 12) % 24 - 12)
            elif kind == "cf6":
                p = A.peak[A.peak.channel == "_BUILDING"].set_index("cell_tag").coincidence_factor
                out.append(p[s] - p[n])
        return out
    return f


def union(*fs):
    def f(A):
        v = []
        for g in fs:
            v += list(g(A))
        return v
    return f


def absvals(fn):
    def f(A):
        return [abs(x) for x in fn(A)]
    return f


def maxabs(fn):
    def f(A):
        return max(abs(x) for x in fn(A))
    return f


def max_shift_tenant(scen="Y2022"):
    def f(A):
        return max(abs(x) for ch in TENANT for x in delta_vs_code("wdpeak", ch, scen)(A))
    return f


def count_hotel_night_gt_mid(scen):
    def f(A):
        return int(sum(mid_night(A.prof(c, "hotel")) < 1 for c in cells(scen)))
    return f


def sens(scen, ch):
    """energy_pct_vs_Bcentral per model (step9_scenario_response), the 4 values."""
    def f(A):
        v = A.sr[(A.sr.scenario == scen) & (A.sr.channel == ch)].energy_pct_vs_Bcentral
        assert len(v) == 4
        return v.tolist()
    return f


def t4_range(ch, col):
    def f(A):
        v = A.eui[A.eui.channel == ch][col]
        assert len(v) == 56
        return (float(v.min()), float(v.max()), float(v.median()))
    return f


def t4_inband(ch):
    def f(A):
        return int((A.eui[A.eui.channel == ch].verdict_asmodelled == "PASS").sum())
    return f


def eui56_median(ch):
    def f(A):
        return float(A.eui[A.eui.channel == ch].eui_CFA_kWh_m2.median())
    return f


def count_eui(ch, cond):
    def f(A):
        v = A.eui[A.eui.channel == ch].eui_CFA_kWh_m2
        return int(cond(v).sum())
    return f


def res_info_out(A):
    return int((A.eui[A.eui.channel == "residential"].info_verdict != "IN").sum())


def office_heating_share(scope):
    """Office heating (agg_annual end_use 'heating', all fuels) / office total, %, median over `scope` cells."""
    def f(A):
        o = A.annual[A.annual.channel == "office"]
        t = o.groupby("cell_tag").energy_J.sum()
        h = o[o.end_use == "heating"].groupby("cell_tag").energy_J.sum().reindex(t.index).fillna(0)
        s = 100 * h / t
        if scope != "all56":
            s = s[s.index.str.startswith(scope + "__")]
        return float(s.median())
    return f


def hotel_clusters(A):
    h = A.eui[A.eui.channel == "hotel"]
    st = h[h.building == "SuperTall"].eui_CFA_kWh_m2
    ta = h[h.building == "Tall"].eui_CFA_kWh_m2
    return dict(st=(st.min(), st.max()), ta=(ta.min(), ta.max()))


def hotel_gap(A):
    c = hotel_clusters(A)
    return c["ta"][0] - c["st"][1]


def hotel_gap_pct(A):
    return 100 * hotel_gap(A) / (300.0 - 180.0)


def retail_below_floor_pct(A):
    return 100 * (80.0 - eui56_median("retail")(A)) / 80.0


# ---- claims (bool) ---------------------------------------------------------------------------
def claim_hotel_split(A):
    """Every hotel simulation outside its range is a Tall model above the 300 ceiling, every SuperTall
    model is inside, and the verdict is split (0 < out < 56)."""
    h = A.eui[A.eui.channel == "hotel"]
    out = h[h.verdict_asmodelled != "PASS"]
    return bool(0 < len(out) < 56 and (out.building == "Tall").all() and (out.eui_CFA_kWh_m2 > 300).all()
                and (h[h.building == "SuperTall"].verdict_asmodelled == "PASS").all()
                and (h[h.building == "Tall"].verdict_asmodelled != "PASS").all())


def claim_hotel_gap_contains_ceiling(A):
    c = hotel_clusters(A)
    return bool(claim_hotel_split(A) and c["st"][1] < 300 < c["ta"][0])


def claim_cf_rises_slightly(A):
    """All four per-model changes of the 6-channel CF (Y2022 vs code) are positive and below 0.05."""
    d = delta_vs_code("cf6", None)(A)
    return bool(all(0 < x < 0.05 for x in d))


def claim_peak_0700_january(A):
    """Annual building maximum (6-channel hourly reconstruction) at 07:00 on a January day in every
    Default_NECB and every Y2022 model."""
    for c in cells("Default_NECB") + cells("Y2022"):
        s = A.hourly(c).sum(axis=1)
        i = int(s.argmax())
        if not (i % 24 == 7 and i // 24 < 31):
            return False
    return True


def claim_additive(A):
    """Bundle response within 5 % (relative) of the sum of the three single-lever responses, per model,
    for office, retail and hotel, both bands."""
    worst = 0.0
    for band in ("cons", "opt"):
        for ch in ("office", "retail", "hotel"):
            b = sens(f"B_{band}", ch)(A)
            s = np.array(sens(f"sens_office_{band}", ch)(A)) + np.array(sens(f"sens_retail_{band}", ch)(A)) \
                + np.array(sens(f"sens_hotel_{band}", ch)(A))
            worst = max(worst, float(np.max(np.abs(np.array(b) - s) / np.abs(b))))
    A.additive_worst = worst
    return worst < 0.05


def claim_overstate_and_flatten(A):
    """Code schedules give higher office and retail EUI in all 4 models (overstate) AND a lower weekday
    midday-to-night ratio than the survey channels, median over models (flatten)."""
    over = all(x < 0 for ch in ("office", "retail") for x in delta_vs_code("eui", ch)(A))
    flat = all(ratio("Y2022", ch)(A) > ratio("Default_NECB", ch)(A) for ch in ("office", "retail"))
    A.overstate, A.flatten = over, flat
    return bool(over and flat)


def claim_rebase_lowers(A):
    """Prorating Service/MEP area AND energy onto office by tenant floor-area share lowers office EUI in
    all 56 simulations (V2-B1 mechanism 2)."""
    en = A.abc.pivot_table(index="cell_tag", columns="channel", values="energy_J", aggfunc="sum")
    M = A.meta.loc[en.index]
    at = sum(M[f"area_{c}_m2"] for c in TENANT)
    sh = M["area_office_m2"] / at
    reb = (en["office"] + en["service_MEP"] * sh) / (M["area_office_m2"] + M["area_service_MEP_m2"] * sh)
    cfa = en["office"] / M["area_office_m2"]
    return bool(len(reb) == 56 and (reb < cfa).all())


def claim_retail_not_all_cells(A):
    return t4_inband("retail")(A) < 56


def claim_barely_move(A):
    """Residential and hotel EUI change against code (Y2022, per model) below 2.0 % in absolute value
    (2.0 = the smallest round bound above the largest old printed value, residential 1.9)."""
    v = [abs(x) for ch in ("residential", "hotel") for x in delta_vs_code("eui", ch)(A)]
    A.barely_max = max(v)
    return max(v) < 2.0


# ------------------------------------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------------------------------------
def dps(tok):
    tok = tok.strip()
    return len(tok.split(".")[1]) if "." in tok else 0


def fnum(x, dp, signed=False, rounder="direct"):
    """rounder: 'direct' = Python format of the exact value (used for every NEW value);
    'double' = round to 3 dp, then half-up to the print dp (the double rounding seen in earlier prints);
    'chain1' = half-up to 1 dp, then half-up to 0 dp (a 0-dp print made from a printed 1-dp value)."""
    if rounder == "double" and dp < 3:
        x = float(Decimal(f"{round(float(x), 3):.3f}").quantize(Decimal(1).scaleb(-dp), ROUND_HALF_UP))
    elif rounder == "chain1" and dp == 0:
        x = float(Decimal(f"{float(x):.6f}").quantize(Decimal("0.1"), ROUND_HALF_UP).quantize(Decimal(1), ROUND_HALF_UP))
    s = f"{float(x):.{dp}f}"
    if float(s) == 0:
        return f"{0:.{dp}f}"
    if signed and not s.startswith("-"):
        s = "+" + s
    return s


def ceil_dp(x, dp):
    return math.ceil(x * 10 ** dp - 1e-9) / 10 ** dp


NUMWORD = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four"}


def fmt(spec, val, printed, rounder="direct"):
    kind = spec[0]
    if kind == "num":
        _, signed = spec
        return fnum(val, dps(printed), signed, rounder)
    if kind == "range":
        # spec: ("range", order, signed); per-endpoint decimals from the printed tokens
        _, order, signed = spec
        toks = printed.split(" to ")
        lo, hi = min(val), max(val)
        a, b = (lo, hi)
        if order == "mag":             # smaller magnitude first ("-15.6 to -20.2")
            a, b = sorted([lo, hi], key=abs)
        return f"{fnum(a, dps(toks[0]), signed, rounder)} to {fnum(b, dps(toks[1]), signed, rounder)}"
    if kind == "t4":
        lo, hi, med = val
        m = re.match(r"([\d.]+)-([\d.]+) \(([\d.]+)\)", printed)
        return f"{fnum(lo, dps(m.group(1)), rounder=rounder)}-{fnum(hi, dps(m.group(2)), rounder=rounder)} " \
               f"({fnum(med, dps(m.group(3)), rounder=rounder)})"
    if kind == "of56":
        return f"{val}/56"
    if kind == "int":
        return f"{int(val)}"
    if kind == "hournum":
        return f"{int(val)}" if float(val).is_integer() else f"{val:.1f}"
    if kind == "clock":
        if val == 0:
            return "midnight"
        h, m = int(val), int(round((val - int(val)) * 60))
        return f"{h:02d}:{m:02d}"
    if kind == "lessthan":           # ("lessthan", prefix)
        dp = dps(printed.replace("less than ", ""))
        return f"{spec[1]}{ceil_dp(val, dp):.{dp}f}"
    if kind == "bound":              # printed max, rounded
        return fnum(val, dps(printed))
    if kind == "allword":            # "all four" / "all 56"
        n_all, style = spec[1], spec[2]
        if val == n_all:
            return printed
        return f"{NUMWORD.get(val, val)} of the {NUMWORD.get(n_all, n_all)}" if style == "word" else f"{val} of {n_all}"
    if kind == "claim":
        return printed if val else None
    if kind == "dirword":            # ("dirword", word_if_true, word_if_false)
        return spec[1] if val else spec[2]
    raise ValueError(kind)


# ------------------------------------------------------------------------------------------------
# Registry: (file, line) -> list of (printed, metric_fn, spec, definition) in marker order
# ------------------------------------------------------------------------------------------------
H_NIGHT, H_DAY = list(range(0, 6)), list(range(9, 17))
S_NUM, S_SIG = ("num", False), ("num", True)
OFF_EUI = delta_vs_code("eui", "office")
RET_EUI = delta_vs_code("eui", "retail")
D_EUI = "per-model % change of CFA EUI, Y2022 vs Default_NECB (same tower-city), range over 4 models"
CLAIM = ("claim",)

R = {
    ("00_FrontMatter.md", 13): [
        ("-16 to -20", OFF_EUI, ("range", "mag", True), "office " + D_EUI + ", 0 dp"),
        ("-12 to -15", RET_EUI, ("range", "mag", True), "retail " + D_EUI + ", 0 dp"),
        ("0.3", maxabs(delta_vs_code("centroid", None)), ("lessthan", ""),
         "'less than' bound: max over 4 models of |shift of building load centroid (agg_peak _BUILDING "
         "peak_hour_circular) Y2022 vs code|, rounded UP to 1 dp"),
        ("hotel verdicts split by prototype", claim_hotel_split, CLAIM,
         "claim: all hotel simulations out of range are Tall (above 300), all SuperTall inside"),
    ],
    ("01_Introduction.md", 33): [
        ("the hotel verdict splits by tower prototype", claim_hotel_split, CLAIM, "claim: hotel split (as 00:13)"),
    ],
    ("01_Introduction.md", 35): [
        ("12 to 20", absvals(union(OFF_EUI, RET_EUI)), ("range", "asc", False),
         "|office and retail " + D_EUI + "|, pooled, 0 dp"),
    ],
    ("03_Results.md", 9): [
        ("2.2 to 2.3", presence_range_over(CYCLES, "residential", H_NIGHT), ("range", "asc", False),
         "residential WD presence per 100 m2, hours 00-05, median of 4 models, range over the 4 cycles"),
        ("0.90", presence("Y2005", "residential", H_DAY), S_NUM, "residential WD presence per 100 m2, hours 09-16, Y2005"),
        ("0.71", presence("Y2010", "residential", H_DAY), S_NUM, "same, Y2010"),
        ("0.75", presence("Y2015", "residential", H_DAY), S_NUM, "same, Y2015"),
        ("0.79", presence("Y2022", "residential", H_DAY), S_NUM, "same, Y2022"),
        ("22:00", occ_peak_hour("Y2022", "hotel"), ("clock",), "hotel occupant peak hour (median argmax WD people), Y2022"),
    ],
    ("03_Results.md", 11): [
        ("2.19", presence("Y2005", "office", H_DAY), S_NUM, "office WD presence per 100 m2, hours 09-16, Y2005"),
        ("2.02", presence("Y2010", "office", H_DAY), S_NUM, "same, Y2010"),
        ("2.24", presence("Y2015", "office", H_DAY), S_NUM, "same, Y2015"),
        ("2.13", presence("Y2022", "office", H_DAY), S_NUM, "same, Y2022"),
        ("1.66", presence("B_central", "office", H_DAY), S_NUM, "same, B_central"),
        ("2.45", presence("Y2005", "retail", H_DAY), S_NUM, "retail WD presence per 100 m2, hours 09-16, Y2005"),
        ("2.07", presence("Y2015", "retail", H_DAY), S_NUM, "same, Y2015"),
        ("2.30", presence("Y2022", "retail", H_DAY), S_NUM, "same, Y2022"),
        ("1.87", presence("B_central", "retail", H_DAY), S_NUM, "same, B_central"),
    ],
    ("03_Results.md", 13): [
        ("70.63", lon_eui("Y2005", "office"), S_NUM, "office CFA EUI median, Y2005 (step9_longitudinal)"),
        ("69.78", lon_eui("Y2010", "office"), S_NUM, "office CFA EUI median, Y2010"),
        ("-1.21", lon_pct("Y2010", "office"), S_SIG, "office energy_pct_vs_2005 median, Y2010"),
        ("71.29", lon_eui("Y2015", "office"), S_NUM, "office CFA EUI median, Y2015"),
        ("+0.94", lon_pct("Y2015", "office"), S_SIG, "office energy_pct_vs_2005 median, Y2015"),
        ("70.20", lon_eui("Y2022", "office"), S_NUM, "office CFA EUI median, Y2022"),
        ("-0.67", lon_pct("Y2022", "office"), S_SIG, "office energy_pct_vs_2005 median, Y2022"),
        ("76.36", lon_eui("Y2010", "retail"), S_NUM, "retail CFA EUI median, Y2010"),
        ("-1.42", lon_pct("Y2010", "retail"), S_SIG, "retail energy_pct_vs_2005 median, Y2010"),
        ("75.84", lon_eui("Y2015", "retail"), S_NUM, "retail CFA EUI median, Y2015"),
        ("-2.03", lon_pct("Y2015", "retail"), S_SIG, "retail energy_pct_vs_2005 median, Y2015"),
        ("79.19", lon_eui("Y2022", "retail"), S_NUM, "retail CFA EUI median, Y2022"),
        ("+2.36", lon_pct("Y2022", "retail"), S_SIG, "retail energy_pct_vs_2005 median, Y2022"),
        ("+0.13 to +4.69", lon_pct("Y2022", "retail", "list"), ("range", "asc", True),
         "retail energy_pct_vs_2005, Y2022, range over 4 models"),
        ("118.73", lon_eui("Y2005", "residential"), S_NUM, "residential CFA EUI median, Y2005"),
        ("118.68", lon_eui("Y2022", "residential"), S_NUM, "residential CFA EUI median, Y2022"),
    ],
    ("03_Results.md", 15): [
        ("-0.003", lon_pct("Y2010", "hotel"), S_SIG, "hotel energy_pct_vs_2005 median, Y2010"),
        ("+0.031", lon_pct("Y2015", "hotel"), S_SIG, "hotel energy_pct_vs_2005 median, Y2015"),
        ("+0.09", lon_pct("Y2022", "hotel"), S_SIG, "hotel energy_pct_vs_2005 median, Y2022"),
    ],
    ("03_Results.md", 19): [
        ("44.47", share("hotel", "energy_share_pct"), S_NUM, "hotel energy_share_pct median, 16 cycle cells"),
        ("20.25", share("hotel", "area_share_pct"), S_NUM, "hotel area_share_pct median, 16 cycle cells"),
        ("21.42", share("office", "energy_share_pct"), S_NUM, "office energy share"),
        ("35.14", share("office", "area_share_pct"), S_NUM, "office area share"),
        ("18.27", share("residential", "energy_share_pct"), S_NUM, "residential energy share"),
        ("17.73", share("residential", "area_share_pct"), S_NUM, "residential area share"),
        ("2.56", share("retail", "energy_share_pct"), S_NUM, "retail energy share"),
        ("3.92", share("retail", "area_share_pct"), S_NUM, "retail area share"),
    ],
}
T3 = "Table 3, Y2022, median of 4 models: "
for ln, ch, occ, epk, rat, eui in [(29, "office", "10", "11.69", "11.41", "70.20"),
                                   (33, "retail", "14.5", "13.09", "47.06", "79.19"),
                                   (37, "hotel", "22", "18.90", "0.78", "259.90"),
                                   (41, "residential", "0", "12.03", "3.89", "118.68")]:
    R[("03_Results.md", ln)] = [(occ, occ_peak_hour("Y2022", ch), ("hournum",), T3 + f"{ch} occupant peak hour (median argmax WD people)")]
    R[("03_Results.md", ln + 1)] = [(epk, energy_peak_hour("Y2022", ch), S_NUM, T3 + f"{ch} WD energy peak hour, circular mean")]
    R[("03_Results.md", ln + 2)] = [(rat, ratio("Y2022", ch), S_NUM, T3 + f"{ch} WD midday(11-14)/night(22-04) energy ratio")]
    R[("03_Results.md", ln + 3)] = [(eui, eui_med("Y2022", ch), S_NUM, T3 + f"{ch} CFA EUI")]
R[("03_Results.md", 45)] = [("14.85", bld_peak("Y2022", "peak_hour_circular"), S_NUM, T3 + "building load centroid (agg_peak _BUILDING peak_hour_circular)")]
R[("03_Results.md", 46)] = [("0.940", bld_peak("Y2022", "coincidence_factor"), S_NUM, T3 + "coincidence factor, 6 channels (agg_peak)")]
R[("03_Results.md", 47)] = [("0.969", cf4("Y2022"), S_NUM, T3 + "coincidence factor, 4 tenant uses (hourly reconstruction)")]
R[("03_Results.md", 48)] = [("2.68", ratio_building("Y2022"), S_NUM, T3 + "building (6-channel sum) WD midday/night ratio")]
R.update({
    ("03_Results.md", 52): [
        ("22:00", occ_peak_hour("Y2022", "hotel"), ("clock",), "hotel occupant peak hour, Y2022"),
        ("midnight", occ_peak_hour("Y2022", "residential"), ("clock",), "residential occupant peak hour, Y2022"),
        ("0.8", max_shift_tenant(), ("bound",),
         "max over 4 tenant channels x 4 models of |WD energy peak hour shift, Y2022 vs code|, rounded 1 dp"),
        ("0.1", maxabs(delta_vs_code("wdpeak", "residential")), ("lessthan", ""),
         "'less than' bound: max |residential WD energy peak hour shift|, rounded UP to 1 dp"),
        ("0.16 to 0.29", delta_vs_code("centroid", None), ("range", "asc", False),
         "building load centroid shift Y2022 vs code (h), range over 4 models"),
    ],
    ("03_Results.md", 54): [
        ("0.940", bld_peak("Y2022", "coincidence_factor"), S_NUM, "6-channel CF median, Y2022"),
        ("+0.005 to +0.020", delta_vs_code("cf6", None), ("range", "asc", True), "6-channel CF change Y2022 vs code, range over 4 models"),
        ("and at the same hour with the survey-based channels", claim_peak_0700_january, CLAIM,
         "claim: annual building max at 07:00 on a January day in every Default_NECB and Y2022 model"),
    ],
    ("03_Results.md", 56): [
        ("-15.6 to -20.2", OFF_EUI, ("range", "mag", True), "office " + D_EUI + ", 1 dp"),
        ("-12.2 to -14.5", RET_EUI, ("range", "mag", True), "retail " + D_EUI + ", 1 dp"),
        ("11.4", ratio("Y2022", "office"), S_NUM, "office WD midday/night ratio, Y2022 median, 1 dp"),
        ("47.1", ratio("Y2022", "retail"), S_NUM, "retail WD midday/night ratio, Y2022 median, 1 dp"),
        ("0.78", ratio("Y2022", "hotel"), S_NUM, "hotel WD midday/night ratio, Y2022 median"),
        ("all four", count_hotel_night_gt_mid("Y2022"), ("allword", 4, "word"),
         "count of Y2022 models with hotel midday/night ratio < 1"),
    ],
    ("03_Results.md", 58): [
        ("-1.0 to -1.9", delta_vs_code("eui", "residential"), ("range", "mag", True), "residential " + D_EUI + ", 1 dp"),
        ("3.89", ratio("Y2022", "residential"), S_NUM, "residential WD midday/night ratio, Y2022 median"),
        ("less than 0.6", maxabs(delta_vs_code("eui", "hotel")), ("lessthan", "less than "),
         "'less than' bound: max |hotel " + D_EUI + "|, rounded UP to 1 dp"),
    ],
    ("03_Results.md", 64): [
        ("+1.67 to +2.45", sens("sens_office_cons", "office"), ("range", "asc", True), "office energy_pct_vs_Bcentral, sens_office_cons, range over 4 models"),
        ("-2.19 to -1.46", sens("sens_office_opt", "office"), ("range", "asc", True), "office, sens_office_opt"),
        ("-2.10 to -1.59", sens("sens_retail_cons", "retail"), ("range", "asc", True), "retail, sens_retail_cons"),
        ("+1.88 to +2.50", sens("sens_retail_opt", "retail"), ("range", "asc", True), "retail, sens_retail_opt"),
        ("-0.76 to -0.40", sens("sens_hotel_cons", "hotel"), ("range", "asc", True), "hotel, sens_hotel_cons"),
        ("+0.26 to +0.48", sens("sens_hotel_opt", "hotel"), ("range", "asc", True), "hotel, sens_hotel_opt"),
    ],
    ("03_Results.md", 66): [
        ("-0.08 to +0.02", sens("sens_office_cons", "retail"), ("range", "asc", True), "retail, sens_office_cons"),
        ("+0.004 to +0.03", sens("sens_office_cons", "hotel"), ("range", "asc", True), "hotel, sens_office_cons"),
        ("-0.02 to -0.01", sens("sens_retail_cons", "office"), ("range", "asc", True), "office, sens_retail_cons"),
        ("-0.01 to 0.00", sens("sens_retail_cons", "hotel"), ("range", "asc", True), "hotel, sens_retail_cons"),
        ("-0.27 to -0.18", sens("sens_hotel_cons", "office"), ("range", "asc", True), "office, sens_hotel_cons"),
        ("-0.23 to -0.16", sens("sens_hotel_cons", "retail"), ("range", "asc", True), "retail, sens_hotel_cons"),
        ("+0.06 to +0.29", sens("sens_office_cons", "residential"), ("range", "asc", True),
         "residential, sens_office_cons ONLY (the reproducing definition; with sens_office_opt pooled the old arm gives -0.08 to +0.29)"),
        ("less than 0.10", maxabs(union(*[sens(s, "residential") for s in
                                          ("sens_retail_cons", "sens_retail_opt", "sens_hotel_cons", "sens_hotel_opt")])),
         ("lessthan", "less than "), "'less than' bound: max |residential| under sens_retail_* and sens_hotel_*, rounded UP to 2 dp"),
    ],
    ("03_Results.md", 68): [
        ("-2.05 to +2.20", union(sens("B_cons", "office"), sens("B_opt", "office")), ("range", "asc", True), "office, B_cons and B_opt pooled"),
        ("-2.42 to +2.66", union(sens("B_cons", "retail"), sens("B_opt", "retail")), ("range", "asc", True), "retail, bundles pooled"),
        ("-0.73 to +0.45", union(sens("B_cons", "hotel"), sens("B_opt", "hotel")), ("range", "asc", True), "hotel, bundles pooled"),
        ("These ranges are close to the sums of the single-lever effects, so the levers act nearly additively.",
         claim_additive, CLAIM, "claim: per model, |bundle - sum of 3 single levers| < 5 % of |bundle| (office/retail/hotel, both bands)"),
    ],
    ("03_Results.md", 80): [
        ("61.72-90.21 (71.02)", t4_range("office", "eui_CFA_kWh_m2"), ("t4",), "Table 4 office CFA min-max (median), 56 sims"),
        ("63.27-85.51 (71.53)", t4_range("office", "eui_GFAshare_kWh_m2"), ("t4",), "Table 4 office GFA-share min-max (median)"),
        ("0/56", t4_inband("office"), ("of56",), "office simulations with verdict_asmodelled PASS"),
    ],
    ("03_Results.md", 81): [
        ("63.63-96.84 (75.63)", t4_range("retail", "eui_CFA_kWh_m2"), ("t4",), "Table 4 retail CFA"),
        ("62.88-91.95 (73.27)", t4_range("retail", "eui_GFAshare_kWh_m2"), ("t4",), "Table 4 retail GFA-share"),
        ("12/56", t4_inband("retail"), ("of56",), "retail simulations in range"),
    ],
    ("03_Results.md", 82): [
        ("203.33-318.42 (260.54)", t4_range("hotel", "eui_CFA_kWh_m2"), ("t4",), "Table 4 hotel CFA"),
        ("171.07-261.18 (215.96)", t4_range("hotel", "eui_GFAshare_kWh_m2"), ("t4",), "Table 4 hotel GFA-share"),
        ("28/56", t4_inband("hotel"), ("of56",), "hotel simulations in range"),
    ],
    ("03_Results.md", 83): [
        ("111.57-128.77 (119.10)", t4_range("residential", "eui_CFA_kWh_m2"), ("t4",), "Table 4 residential CFA"),
        ("101.54-115.05 (107.24)", t4_range("residential", "eui_GFAshare_kWh_m2"), ("t4",), "Table 4 residential GFA-share"),
    ],
    ("03_Results.md", 87): [
        ("all 56", count_eui("office", lambda v: v < 100), ("allword", 56, "num"), "office simulations below the 100 floor"),
        ("71.02", eui56_median("office"), S_NUM, "office CFA median, 56 sims"),
        ("17", office_heating_share("all56"), S_NUM,
         "office heating share % (agg_annual end_use heating / office total), median over all 56 sims"),
        ("lowers every value further", claim_rebase_lowers, CLAIM,
         "claim: Service/MEP area+energy prorated onto office by tenant-area share lowers office EUI in 56/56"),
    ],
    ("03_Results.md", 89): [
        ("28", count_eui("hotel", lambda v: v > 300), ("int",), "hotel simulations above the 300 ceiling"),
        ("all are Tall-tower models, while the SuperTall models stay inside in every case", claim_hotel_split, CLAIM,
         "claim: hotel split (as 00:13)"),
        ("203.33 to 218.22", lambda A: list(hotel_clusters(A)["st"]), ("range", "asc", False), "SuperTall hotel CFA cluster min to max"),
        ("302.86 to 318.42", lambda A: list(hotel_clusters(A)["ta"]), ("range", "asc", False), "Tall hotel CFA cluster min to max"),
        ("84.64", hotel_gap, S_NUM, "gap = Tall cluster min - SuperTall cluster max"),
        ("70.5", hotel_gap_pct, S_NUM, "gap / (300 - 180) x 100"),
    ],
    ("03_Results.md", 91): [
        ("75.63", eui56_median("retail"), S_NUM, "retail CFA median, 56 sims"),
        ("5.47", retail_below_floor_pct, S_NUM, "(80 - retail median) / 80 x 100 (positive = below floor)"),
        ("12", t4_inband("retail"), ("int",), "retail simulations in range"),
        ("44", count_eui("retail", lambda v: v < 80), ("int",), "retail simulations below the 80 floor"),
    ],
    ("03_Results.md", 93): [
        ("55", res_info_out, ("int",), "residential simulations outside the SHEU context range (info_verdict != IN)"),
    ],
    ("04_Discussion.md", 5): [
        ("raise it slightly", claim_cf_rises_slightly, CLAIM, "claim: 6-channel CF change Y2022 vs code in (0, 0.05) for all 4 models"),
    ],
    ("04_Discussion.md", 7): [
        ("under both schedule sets", claim_peak_0700_january, CLAIM, "claim: annual max 07:00 January, code and Y2022"),
    ],
    ("04_Discussion.md", 9): [
        ("-16 to -20", OFF_EUI, ("range", "mag", True), "office " + D_EUI + ", 0 dp"),
        ("-12 to -15", RET_EUI, ("range", "mag", True), "retail " + D_EUI + ", 0 dp"),
        ("The code schedules overstate the energy of office and retail tenants and flatten their daily profile.",
         claim_overstate_and_flatten, CLAIM,
         "claim: code EUI > survey EUI in all 4 models (office, retail) AND code midday/night ratio < survey ratio (medians)"),
    ],
    ("04_Discussion.md", 15): [
        ("The hotel verdict follows the tower prototype, because the two prototypes fall on either side of a wide gap that contains the ceiling.",
         claim_hotel_gap_contains_ceiling, CLAIM, "claim: hotel split and SuperTall max < 300 < Tall min"),
        ("below", lambda A: eui56_median("retail")(A) < 80.0, ("dirword", "below", "above"),
         "retail median (56 sims) below (True) or above (False) the 80 floor"),
    ],
    ("05_Limitations.md", 7): [
        ("does not meet its range", claim_retail_not_all_cells, ("dirword", "does not meet its range", "meets its range"),
         "retail in-range count < 56 (all-simulations rule not met)"),
    ],
    ("05_Limitations.md", 11): [
        ("rise", lambda A: lon_pct("Y2022", "retail")(A) > 0, ("dirword", "rise", "fall"),
         "sign of retail energy_pct_vs_2005 median, Y2022"),
    ],
    ("06_Conclusion.md", 5): [
        ("-16 to -20", OFF_EUI, ("range", "mag", True), "office " + D_EUI + ", 0 dp"),
        ("-12 to -15", RET_EUI, ("range", "mag", True), "retail " + D_EUI + ", 0 dp"),
        ("barely move", claim_barely_move, CLAIM, "claim: |residential and hotel EUI change vs code| < 2.0 % in all 4 Y2022 models"),
        ("rises slightly", claim_cf_rises_slightly, CLAIM, "claim: CF change positive and < 0.05 (as 04:5)"),
    ],
    ("06_Conclusion.md", 7): [
        ("the hotel verdict follows the tower prototype", claim_hotel_split, CLAIM, "claim: hotel split (as 00:13)"),
    ],
})

# Table 3 code-schedule column (NOT markers): reader must reproduce it on both arms (positive control)
CODE_COL = [("office occ peak hour", occ_peak_hour("Default_NECB", "office"), ("hournum",), "9"),
            ("office energy peak hour", energy_peak_hour("Default_NECB", "office"), S_NUM, "12.02"),
            ("office ratio", ratio("Default_NECB", "office"), S_NUM, "7.21"),
            ("office EUI", eui_med("Default_NECB", "office"), S_NUM, "85.36"),
            ("retail occ peak hour", occ_peak_hour("Default_NECB", "retail"), ("hournum",), "15"),
            ("retail energy peak hour", energy_peak_hour("Default_NECB", "retail"), S_NUM, "12.46"),
            ("retail ratio", ratio("Default_NECB", "retail"), S_NUM, "9.27"),
            ("retail EUI", eui_med("Default_NECB", "retail"), S_NUM, "91.74"),
            ("hotel occ peak hour", occ_peak_hour("Default_NECB", "hotel"), ("hournum",), "15"),
            ("hotel energy peak hour", energy_peak_hour("Default_NECB", "hotel"), S_NUM, "18.32"),
            ("hotel ratio", ratio("Default_NECB", "hotel"), S_NUM, "1.03"),
            ("hotel EUI", eui_med("Default_NECB", "hotel"), S_NUM, "260.23"),
            ("residential occ peak hour", occ_peak_hour("Default_NECB", "residential"), ("hournum",), "9"),
            ("residential energy peak hour", energy_peak_hour("Default_NECB", "residential"), S_NUM, "11.98"),
            ("residential ratio", ratio("Default_NECB", "residential"), S_NUM, "3.78"),
            ("residential EUI", eui_med("Default_NECB", "residential"), S_NUM, "120.12"),
            ("building centroid", bld_peak("Default_NECB", "peak_hour_circular"), S_NUM, "14.62"),
            ("building CF6", bld_peak("Default_NECB", "coincidence_factor"), S_NUM, "0.930"),
            ("building CF4", cf4("Default_NECB"), S_NUM, "0.963"),
            ("building ratio", ratio_building("Default_NECB"), S_NUM, "2.94"),
            ("office code presence 09-16 (Results:11)", presence("Default_NECB", "office", H_DAY), S_NUM, "3.14"),
            ("hotel night>midday count, code (Results:56 'two of the four')", count_hotel_night_gt_mid("Default_NECB"), ("int",), "2")]

# Negative controls: wrong scenario / channel / hours / definition / arm -> must NOT reproduce the print
NEG = [("office 2022 EUI read from Y2015", lon_eui("Y2015", "office"), S_NUM, "70.20", "old"),
       ("Table 3 office ratio computed on the retail channel", ratio("Y2022", "retail"), S_NUM, "11.41", "old"),
       ("residential night presence over 00-06 instead of 00-05", presence_range_over(CYCLES, "residential", list(range(0, 7))),
        ("range", "asc", False), "2.2 to 2.3", "old"),
       ("office cons single lever read from the B_cons bundle", sens("B_cons", "office"), ("range", "asc", True), "+1.67 to +2.45", "old"),
       ("residential under office variants with cons+opt pooled", union(sens("sens_office_cons", "residential"), sens("sens_office_opt", "residential")),
        ("range", "asc", True), "+0.06 to +0.29", "old"),
       ("hotel energy share read from area_share_pct", share("hotel", "area_share_pct"), S_NUM, "44.47", "old"),
       ("office vs code change on B_central instead of Y2022", delta_vs_code("eui", "office", "B_central"), ("range", "mag", True), "-15.6 to -20.2", "old"),
       ("retail in-range count read from the NEW arm (wrong arm)", t4_inband("retail"), ("of56",), "12/56", "new"),
       ("CF6 median read from B_central instead of Y2022", bld_peak("B_central", "coincidence_factor"), S_NUM, "0.940", "old"),
       ("hotel occupant peak hour from the code schedule", occ_peak_hour("Default_NECB", "hotel"), ("clock",), "22:00", "old"),
       ("abstract retail 0-dp range read from the office channel (all rounders incl. chain1)", OFF_EUI, ("range", "mag", True), "-12 to -15", "old"),
       ("residential vs code 1-dp range read from B_central only", delta_vs_code("eui", "residential", "B_central"), ("range", "mag", True), "-1.0 to -1.9", "old")]

# What was tried for markers that do not reproduce (written into the CSV note column)
TRIED = {
    ("03_Results.md", 58, "-1.0 to -1.9"):
        "tried: Y2022 vs code CFA (-1.0 to -1.6); Y2022 GFA-share (-1.1 to -1.7); B_central vs code (-1.1 to -1.9); "
        "all survey scenarios pooled (-0.9 to -1.9); only Y2022+B_central pooled gives -1.0 to -1.9, but that pooling does NOT "
        "reproduce the office/retail ranges in the same paragraph (office would be -15.6 to -22.7), so it is not the paper's definition",
    ("03_Results.md", 87, "17"):
        "tried: office heating share all 56 sims median 31.7 (old) / 22.0 (new), mean 31.4, pooled 31.8; heating+fans+pumps+heat "
        "recovery 45.2; only the 4 code-schedule (Default_NECB) models give 16.6 -> 17, identical on both arms; the sentence is about "
        "the office channel over the 56 simulations, so the scope is ambiguous; author decision (value from an earlier arm, V2-B1 2026-08-04)",
}


def as_raw(v):
    if isinstance(v, (list, tuple)):
        return "; ".join(f"{float(x):.6f}" for x in v)
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    return f"{float(v):.6f}" if isinstance(v, (float, int, np.floating, np.integer)) else str(v)


def main():
    apply = "--apply" in sys.argv
    A = {"old": Arm("old"), "new": Arm("new")}
    # read markers from the BACKUP copy (stable line numbers, untouched text)
    found = {}
    for f in FILES:
        with open(os.path.join(BACKUP, f), encoding="utf-8", newline="") as fh:
            for i, line in enumerate(fh.read().split("\n"), 1):
                ms = MARK.findall(line)
                if ms:
                    found[(f, i)] = ms
    n_found = sum(len(v) for v in found.values())
    assert set(found) == set(R), (sorted(set(found) ^ set(R)))
    rows = []
    for key in sorted(R, key=lambda k: (FILES.index(k[0]), k[1])):
        assert [e[0] for e in R[key]] == found[key], (key, found[key])
        for idx, (printed, fn, spec, definition) in enumerate(R[key], 1):
            vo, vn = fn(A["old"]), fn(A["new"])
            fo = {r: fmt(spec, vo, printed, rounder=r) for r in ("direct", "double", "chain1")}
            fn_ = fmt(spec, vn, printed)
            match = next((r for r in ("direct", "double", "chain1") if fo[r] == printed), None)
            if spec[0] == "claim":
                repro = "yes" if vo else "no"
                match = "claim"
            else:
                repro = "yes" if match else "no"
            note = ""
            if repro != "yes":
                status, subst = "not_reproduced", "no"
            elif spec[0] == "claim" and not vn:
                status, subst = "claim_no_longer_holds_left_marked", "no"
            else:
                status, subst = "substitute", "yes"
                if spec[0] == "dirword" and fn_ != printed:
                    note = "direction word flips"
            if match == "double":
                note = (note + "; " if note else "") + "old reproduced only with 3dp then half-up double rounding"
            if match == "chain1":
                note = (note + "; " if note else "") + "old reproduced only via the printed 1-dp value rounded half-up to 0 dp"
            if (key[0], key[1], printed) in TRIED:
                note = (note + "; " if note else "") + TRIED[(key[0], key[1], printed)]
            rows.append(dict(row_type="marker", file=key[0], line=key[1], idx=idx, marker_text=printed,
                             metric_definition=definition, old_computed=as_raw(vo), new_computed=as_raw(vn),
                             old_formatted=fo[match] if match in fo else fo["direct"],
                             old_reproduces=repro, new_value=fn_ if fn_ is not None else "",
                             substitute=subst, status=status, note=note))
    # extra diagnostics for claims
    diag = dict(additive_worst_old=getattr(A["old"], "additive_worst", None), additive_worst_new=getattr(A["new"], "additive_worst", None),
                overstate_old=getattr(A["old"], "overstate", None), flatten_old=getattr(A["old"], "flatten", None),
                overstate_new=getattr(A["new"], "overstate", None), flatten_new=getattr(A["new"], "flatten", None),
                barely_max_old=getattr(A["old"], "barely_max", None), barely_max_new=getattr(A["new"], "barely_max", None),
                heating_share_code_control_old=office_heating_share("Default_NECB")(A["old"]),
                heating_share_code_control_new=office_heating_share("Default_NECB")(A["new"]),
                residential_vs_code_Y2022_or_Bcentral_old=fmt(("range", "mag", True), union(delta_vs_code("eui", "residential"), delta_vs_code("eui", "residential", "B_central"))(A["old"]), "-1.0 to -1.9"),
                )
    for name, fn, spec, want in CODE_COL:
        for arm in ("old", "new"):
            v = fn(A[arm])
            got = fmt(spec, v, want)
            rows.append(dict(row_type="control_code_column", file="03_Results.md", line="", idx="", marker_text=want,
                             metric_definition=f"{name} ({arm} arm)", old_computed=as_raw(v) if arm == "old" else "",
                             new_computed=as_raw(v) if arm == "new" else "", old_formatted=got,
                             old_reproduces="yes" if got == want or fmt(spec, v, want, "double") == want else "no",
                             new_value="", substitute="", status="PASS" if (got == want or fmt(spec, v, want, "double") == want) else "FAIL", note=""))
    for name, fn, spec, want, arm in NEG:
        v = fn(A[arm])
        got = fmt(spec, v, want)
        ok = want not in [fmt(spec, v, want, r) for r in ("direct", "double", "chain1")]
        rows.append(dict(row_type="negative_control", file="", line="", idx="", marker_text=want,
                         metric_definition=f"{name} ({arm} arm)", old_computed=as_raw(v), new_computed="",
                         old_formatted=got, old_reproduces="no" if ok else "yes", new_value="", substitute="",
                         status="PASS (does not reproduce, as required)" if ok else "FAIL (wrongly reproduces)", note=""))
    df = pd.DataFrame(rows)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "P10R_marker_table.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 60)
    mk = df[df.row_type == "marker"]
    print(mk[["file", "line", "idx", "marker_text", "old_formatted", "old_reproduces", "new_value", "status", "note"]].to_string(index=False))
    print(f"\nmarkers found in backup: {n_found}; registry rows: {len(mk)}")
    print("status counts:", mk.status.value_counts().to_dict())
    print("per file:", mk.groupby(["file", "status"]).size().to_dict())
    cc = df[df.row_type == "control_code_column"]
    print(f"code-column controls: {(cc.status == 'PASS').sum()}/{len(cc)} PASS",
          cc[cc.status != "PASS"][["metric_definition", "marker_text", "old_formatted"]].to_string(index=False) if (cc.status != "PASS").any() else "")
    ng = df[df.row_type == "negative_control"]
    print(ng[["metric_definition", "marker_text", "old_formatted", "status"]].to_string(index=False))
    print("diagnostics:", diag)

    if apply:
        for f in FILES:
            src = os.path.join(BACKUP, f)
            dst = os.path.join(CH_DIR, f)
            with open(dst, encoding="utf-8", newline="") as fh:
                cur = fh.read()
            with open(src, encoding="utf-8", newline="") as fh:
                assert fh.read() == cur, f"{f} changed since backup; refusing to apply"
            lines = cur.split("\n")
            for (ff, ln), ms in found.items():
                if ff != f:
                    continue
                sub = mk[(mk.file == f) & (mk.line == ln)].sort_values("idx")
                parts = MARK.split(lines[ln - 1])        # text, m1, text, m2, ...
                for j, (_, r) in enumerate(sub.iterrows()):
                    assert parts[2 * j + 1] == r.marker_text
                    parts[2 * j + 1] = r.new_value if r.substitute == "yes" else f"⟦P10R:{r.marker_text}⟧"
                lines[ln - 1] = "".join(parts)
            with open(dst, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(lines))
            print(f"applied: {f}")


if __name__ == "__main__":
    main()
