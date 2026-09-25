#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P9 second numbers pass (2026-09-25): numbers outside chapters 00/01/03/04/05/06.

Scope: chapters_v2/02, 07, 08, 09, SI_additions.md and the table files the SI uses
(writing/tables/Table_04_validation_gates.md = Table S1, Table_07_limitations.md = Table S2,
tables/SI/Table_A1_A2.md = Table S3). The other files in writing/tables/ are old main-text tables
now carried inline by chapters_v2 (Tables 1 to 4, Table A.1, Table S4) and are not used.

Method (same as Stage 2b, p10r_marker_values.py, whose Arm class and metric functions are imported):
  1. every numeric token in scope is extracted; each is either an ARM item (metric function run on
     BOTH arms with the same code) or a constant (band limit, floor area, design input, threshold,
     model-card value, survey statistic, history of an earlier run) with a written reason;
  2. an ARM item is substituted only if the OLD-arm value, formatted like the print, reproduces it;
  3. negative controls (wrong scenario / channel / basis / arm / rule) must NOT reproduce;
  4. text claims whose truth changes between arms are listed (never rewritten here).

Read only on both arms. Writes IMP/data/P10R/P9_second_pass_table.csv (console -> P9_second_pass.out).
--apply edits the in-scope files (refuses unless each equals its _archive_pre_P9_2026-09-25 backup).
Run: PYTHONIOENCODING=utf-8 py -3 p9_second_pass.py [--apply]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p10r_marker_values as M  # noqa: E402  (Arm, metric functions, fnum, fmt)

J3 = M.J3
W = os.path.join(J3, "writing")
OUT = M.OUT
TAG = "_archive_pre_P9_2026-09-25"
S9 = {"old": os.path.join(M.LEG3, "Step9_docs", "outputs_step9_deliverable"),
      "new": os.path.join(M.LEG3, "Step9_docs", "outputs_step9_P10R")}

SCOPE = {  # path relative to writing/ -> default reason for a numeric token that is not an ARM item
    "chapters_v2/02_Framework.md": "design input / method constant (data years, model hyperparameters, thresholds, "
                                   "lever values, NECB densities, floor areas, counts of simulations, dates)",
    "chapters_v2/07_Nomenclature.md": "nomenclature (slot and hour ranges)",
    "chapters_v2/08_AppendixA_Table1.md": "citation years / study count",
    "chapters_v2/09_AppendixB_Equations.md": "equation constant (codes, loss weights, thresholds)",
    "chapters_v2/SI_additions.md": "model-training record or design constant (not a campaign result)",
    "tables/Table_04_validation_gates.md": "threshold or target (project-chosen or ASHRAE G14); not a result",
    "tables/Table_07_limitations.md": "design input, survey statistic or literature reference (see per-line reason)",
    "tables/SI/Table_A1_A2.md": "model card / codebook constant (not a campaign result)",
}
NOT_USED = ["tables/Table_01_gap_matrix.md (now Table A.1 in 08)", "tables/Table_02_channels.md (now Table 1 in 02)",
            "tables/Table_03_sim_domain.md (now Table 2 in 02)", "tables/Table_05_eui_bands.md (now Table 4 in 03)",
            "tables/Table_06_leg2_leg3_delta.md (now Table S4 in SI_additions)",
            "tables/SI/Table_B1_improvement_rounds.md, tables/SI/Appendix_C_corrections.md (assembler excludes them)"]
LINE_REASON = {  # (file, line) -> reason overriding the file default
    ("tables/Table_07_limitations.md", 8): "count of channels by design (3 of 4 survey-driven)",
    ("tables/Table_07_limitations.md", 9): "design statement (0 % staff signal)",
    ("tables/Table_07_limitations.md", 10): "survey statistic (GSS households), not a campaign result",
    ("tables/Table_07_limitations.md", 11): "floor of 100 = band limit",
    ("tables/Table_07_limitations.md", 12): "284.44 / 299.28 = ASHRAE 90.1-2019 prototype references; 300 = band ceiling",
    ("tables/Table_07_limitations.md", 14): "floor of 80 = band limit",
    ("tables/Table_07_limitations.md", 15): "SHEU context range (literature)",
    ("tables/Table_07_limitations.md", 16): "NECB occupant densities (design input)",
    ("tables/Table_07_limitations.md", 17): "equipment power density (model input)",
    ("tables/Table_07_limitations.md", 18): "retail schedule peak and dip (model input)",
    ("tables/Table_07_limitations.md", 19): "pool-size analyst judgement (method constant)",
    ("tables/Table_07_limitations.md", 21): "GSS episode-time shares per cycle (survey statistic)",
    ("tables/Table_07_limitations.md", 23): "global resize factor K = 6 (experiment input)",
    ("chapters_v2/SI_additions.md", 27): "checkpoint-selection record (training, not the campaign)",
    ("chapters_v2/SI_additions.md", 29): "training gate record and thresholds (training, not the campaign)",
    ("chapters_v2/SI_additions.md", 50): "drift tolerance (threshold)",
    ("chapters_v2/SI_additions.md", 54): "counts of simulations (design)",
}
PROVENANCE_FROM = {"tables/Table_04_validation_gates.md": "## Sources", "tables/Table_07_limitations.md": "## Sources"}
NUM = re.compile(r"(?<![A-Za-z0-9_.\-])[-+−]?\d+(?:[.,]\d+)*(?![A-Za-z0-9])")

# --------------------------------------------------------------------------------------------
# Metric functions (the Stage 2b ones where they exist; new ones take an Arm and use only its tables)
# --------------------------------------------------------------------------------------------
_GATES = {}


def gates(A):
    if A.name not in _GATES:
        with open(os.path.join(S9[A.name], "step9_gates.json"), encoding="utf-8") as fh:
            _GATES[A.name] = {g["gate"]: g["status"] for g in json.load(fh)}
    return _GATES[A.name]


def n_scored_fail(chs=("office", "retail", "hotel")):
    def f(A):
        return int(sum(gates(A)[f"S9-EUI-{c}"] == "FAIL" for c in chs))
    return f


def n_scored_notpass(A):   # negative control: every S9-EUI-* gate that is not PASS (INFO counted)
    return int(sum(v != "PASS" for k, v in gates(A).items() if k.startswith("S9-EUI")))


def hotel_range(basis="eui_CFA_kWh_m2", building=None, scen=None):
    def f(A):
        h = A.eui[A.eui.channel == "hotel"]
        if building:
            h = h[h.building == building]
        if scen:
            h = h[h.scenario == scen]
        return (float(h[basis].min()), float(h[basis].max()))
    return f


def count_hotel_over(building=None):
    def f(A):
        h = A.eui[A.eui.channel == "hotel"]
        if building:
            h = h[h.building == building]
        return int((h.eui_CFA_kWh_m2 > 300).sum())
    return f


def retail_median(basis="eui_CFA_kWh_m2", scen=None):
    def f(A):
        r = A.eui[A.eui.channel == "retail"]
        if scen:
            r = r[r.scenario == scen]
        return float(r[basis].median())
    return f


def retail_below(floor=80.0):
    def f(A):
        return int((A.eui[A.eui.channel == "retail"].eui_CFA_kWh_m2 < floor).sum())
    return f


def pct_below(floor):
    def f(A):
        return 100 * (floor - retail_median()(A)) / floor
    return f


def office_code(stat, basis="eui_CFA_kWh_m2"):
    def f(A):
        o = A.eui[(A.eui.channel == "office") & (A.eui.scenario == "Default_NECB")][basis]
        return float(getattr(o, stat)())
    return f


def retail_min_margin(A):
    r = A.eui[A.eui.channel == "retail"].eui_CFA_kWh_m2
    return float(((r - 80).abs() / 80 * 100).min())


def claim_retail_not_met_either_rule(A):
    """Retail does not meet its range under the median rule (gate FAIL) nor the all-simulations rule."""
    return bool(gates(A)["S9-EUI-retail"] == "FAIL" and M.t4_inband("retail")(A) < 56)


def claim_hotel_over_all_tall(A):
    return M.claim_hotel_split(A)


def claim_code_below_floor(A):
    return office_code("median")(A) < 100.0


WORD = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four"}


def fmt_local(kind, val, printed, rounder="direct"):
    if kind == "word":
        return WORD.get(int(val), str(int(val)))
    if kind == "int":
        return str(int(val))
    if kind == "dash":            # "203.33-318.42"
        a, b = printed.split("-")
        return f"{M.fnum(val[0], M.dps(a), rounder=rounder)}-{M.fnum(val[1], M.dps(b), rounder=rounder)}"
    if kind == "num":
        return M.fnum(val, M.dps(printed), rounder=rounder)
    if kind == "claim":
        return printed if val else None
    raise ValueError(kind)


T7, SI = "tables/Table_07_limitations.md", "chapters_v2/SI_additions.md"
# ARM items: (file, line, anchor (exact substring on the line), token inside anchor, fn, kind, definition)
ARM = [
    (T7, 12, "FAIL on 28 of 56 cells", "28", count_hotel_over(), "int", "hotel simulations above the 300 ceiling (CFA), 56 sims"),
    (T7, 12, "range 203.33-318.42", "203.33-318.42", hotel_range(), "dash", "hotel CFA EUI min-max over 56 sims"),
    (T7, 14, "Median 75.63 against", "75.63", retail_median(), "num", "retail CFA EUI median, 56 sims"),
    (T7, 14, "5.47 % below", "5.47", pct_below(80.0), "num", "(80 - retail median) / 80 x 100"),
    (T7, 14, "44 of 56 cells under", "44", retail_below(80.0), "int", "retail simulations below the 80 floor"),
    (SI, 55, "Four-channel checks, three reported outside", "three", n_scored_fail(), "word",
     "count of scored uses (office, retail, hotel) whose Step-9 gate S9-EUI-<use> is FAIL"),
]
# numbers that look like campaign results but do not reproduce on the old arm: (file, line, token, why + tried)
NOT_REPRO = [
    (T7, 11, "85.45", office_code("median"),
     "uninjected control office EUI. tried: Default_NECB office CFA median 85.36 (old) / 85.36 (new), mean 85.65, "
     "GFA-share median 82.09, the four values 81.65/82.29/88.43/90.21; source says V2-B1 (earlier arm). "
     "The SI merge note already asks for 85.36, which is the value on BOTH arms (code control injects nothing)"),
    (T7, 13, "56", None, "stacked-channel test (L6). S9-EUI-EXPOSURE is INFO on both arms with 'step9_envelope_exposure.csv "
     "not found': the test was not run on either arm; the SI merge note deletes this measured claim"),
    (T7, 13, "2", None, "L6 'exposure takes 2 values': not an output of either arm (same gate, not run); merge note deletes it"),
    (T7, 23, "-0.98", None, "L16 DHW slope from the V2-B4 diagnostic (per-heater regression); no per-heater series in agg_* or step9_*"),
    (T7, 23, "26.7", None, "L16 LAUNDRY share of hotel DHW, V2-B4 diagnostic; not in the arm tables"),
    (T7, 23, "65.4", None, "L16 share after the global K = 6 resize, V2-B4 diagnostic run; not in the arm tables"),
    (SI, 39, "0.15", retail_min_margin,
     "decision margin of the retired all-cells rule (V2-B3, earlier run). tried: smallest |retail - 80| / 80 over 56 sims "
     "= 0.82 % (old) / 0.37 % (new); no reproduction"),
    (SI, 39, "-0.05", None, "median shift between two earlier runs (V2-E3); history, not an output of either arm"),
]
# text claims in scope whose truth is tested on both arms (never rewritten here)
CLAIMS = [
    ("chapters_v2/02_Framework.md", 93, "Retail does not meet its range under either rule.", claim_retail_not_met_either_rule),
    (SI, 39, "Retail does not meet its range under both rules.", claim_retail_not_met_either_rule),
    (T7, 12, "all Tall, all over the 300 ceiling", claim_hotel_over_all_tall),
    (T7, 11, "The uninjected control scores 85.45 against a floor of 100", claim_code_below_floor),
    (T7, 14, "Median 75.63 against a floor of 80, 5.47 % below", lambda A: M.eui56_median("retail")(A) < 80.0),
    (T7, 4, "No verdict is paraphrased and every number is the source's own.", lambda A: A.name == "old"),
]
# negative controls: (name, fn, kind, printed, arm) -> must NOT reproduce
NEG = [
    ("hotel range on the GFA-share basis", hotel_range("eui_GFAshare_kWh_m2"), "dash", "203.33-318.42", "old"),
    ("hotel range over Tall models only", hotel_range(building="Tall"), "dash", "203.33-318.42", "old"),
    ("hotel range over one scenario (B_central) instead of all 56", hotel_range(scen="B_central"), "dash", "203.33-318.42", "old"),
    ("hotel count above 300 on SuperTall only (wrong prototype)", count_hotel_over("SuperTall"), "int", "28", "old"),
    ("retail median on the GFA-share basis", retail_median("eui_GFAshare_kWh_m2"), "num", "75.63", "old"),
    ("retail median over the 2022 cycle only (wrong scenario)", retail_median(scen="Y2022"), "num", "75.63", "old"),
    ("retail median read from the NEW arm as if old", retail_median(), "num", "75.63", "new"),
    ("retail cells under the floor read from the NEW arm", retail_below(80.0), "int", "44", "new"),
    ("retail cells under the office floor of 100 (wrong band)", retail_below(100.0), "int", "44", "old"),
    ("retail % below computed against the 155 ceiling (wrong limit)", pct_below(155.0), "num", "5.47", "old"),
    ("scored FAIL count read from the NEW arm", n_scored_fail(), "word", "three", "new"),
    ("EUI gates not PASS incl. INFO gates (wrong gate set)", n_scored_notpass, "word", "three", "old"),
    ("scored FAIL count over office and hotel only (wrong channels)", n_scored_fail(("office", "hotel")), "word", "three", "old"),
]
# positive cross-file control: the same functions on the NEW arm reproduce 03_Results Table 4 (already P10R)
POS_NEW = [("Table 4 hotel CFA range 204.83-322.18", hotel_range(), "dash", "204.83-322.18"),
           ("Table 4 retail CFA median 84.85", retail_median(), "num", "84.85"),
           ("Table 4 retail 37/56 in range -> 19 below the floor (56 - 37, none above 155)", retail_below(80.0), "int", "19"),
           ("Table 4 hotel 28/56 in range -> 28 above the ceiling", count_hotel_over(), "int", "28"),
           ("scorecard 18/2/10 -> 2 scored FAIL (office, hotel)", n_scored_fail(), "word", "two")]


def raw(v):
    if isinstance(v, (tuple, list)):
        return "; ".join(f"{float(x):.6f}" for x in v)
    if isinstance(v, bool):
        return str(v)
    return f"{float(v):.6f}" if v is not None else ""


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_lines(rel):
    with open(os.path.join(W, rel), encoding="utf-8", newline="") as fh:
        return fh.read().split("\n")


def main():
    apply = "--apply" in sys.argv
    A = {"old": M.Arm("old"), "new": M.Arm("new")}
    rows = []
    arm_tokens = {(f, ln, tok) for f, ln, _, tok, *_ in ARM} | {(f, ln, tok) for f, ln, tok, *_ in NOT_REPRO}

    # ---- ARM items -------------------------------------------------------------------------
    for f, ln, anchor, tok, fn, kind, definition in ARM:
        line = read_lines(f)[ln - 1]
        assert line.count(anchor) == 1 and anchor.count(tok) == 1, (f, ln, anchor)
        vo, vn = fn(A["old"]), fn(A["new"])
        fo = {r: fmt_local(kind, vo, tok, r) for r in ("direct", "double")}
        match = next((r for r in ("direct", "double") if fo[r] == tok), None)
        new = fmt_local(kind, vn, tok)
        rows.append(dict(row_type="arm", file=f, line=ln, token=tok, anchor=anchor, definition=definition,
                         old_computed=raw(vo), new_computed=raw(vn), old_formatted=fo[match or "direct"],
                         old_reproduces="yes" if match else "no", new_value=new,
                         status="substitute" if match else "not_reproduced",
                         note=("same value on both arms" if new == tok else "value changes") if match else ""))
    for f, ln, tok, fn, why in NOT_REPRO:
        line = read_lines(f)[ln - 1]
        assert tok in line, (f, ln, tok)
        vo = fn(A["old"]) if fn else None
        vn = fn(A["new"]) if fn else None
        rows.append(dict(row_type="arm", file=f, line=ln, token=tok, anchor="", definition=why,
                         old_computed=raw(vo), new_computed=raw(vn),
                         old_formatted=M.fnum(vo, M.dps(tok)) if vo is not None else "not computable",
                         old_reproduces="no", new_value="", status="not_reproduced", note="left as printed"))
    # ---- claims ----------------------------------------------------------------------------
    for f, ln, text, fn in CLAIMS:
        assert text in read_lines(f)[ln - 1], (f, ln, text)
        co, cn = bool(fn(A["old"])), bool(fn(A["new"]))
        rows.append(dict(row_type="claim", file=f, line=ln, token=text, anchor="", definition=fn.__doc__ or "",
                         old_computed=str(co), new_computed=str(cn), old_formatted="", old_reproduces="yes" if co else "no",
                         new_value="", status="holds on both" if co and cn else ("MEANING CHANGED (left, not rewritten)"
                                                                                 if co and not cn else "does not hold on old"),
                         note=""))
    # ---- constants (every other numeric token in scope) ----------------------------------------
    for f, default in SCOPE.items():
        lines = read_lines(f)
        stop = next((i for i, l in enumerate(lines, 1) if PROVENANCE_FROM.get(f) and l.startswith(PROVENANCE_FROM[f])), None)
        in_comment = False
        for i, l in enumerate(lines, 1):
            if "<!--" in l:
                in_comment = True
            toks = [t for t in NUM.findall(l) if (f, i, t) not in arm_tokens]
            reason = LINE_REASON.get((f, i), default)
            if stop and i >= stop:
                reason = "provenance notes below the table (not printed in the SI); history of the frozen arm, left"
            elif in_comment:
                reason = "inside an HTML comment (not printed)"
            if "-->" in l:
                in_comment = False
            if toks:
                rows.append(dict(row_type="constant", file=f, line=i, token=" | ".join(toks), anchor="", definition=reason,
                                 old_computed="", new_computed="", old_formatted="", old_reproduces="", new_value="",
                                 status="constant, not arm", note=f"{len(toks)} token(s)"))
    # ---- controls ----------------------------------------------------------------------------
    for name, fn, kind, printed, arm in NEG:
        v = fn(A[arm])
        got = {fmt_local(kind, v, printed, r) for r in ("direct", "double")}
        ok = printed not in got
        rows.append(dict(row_type="negative_control", file="", line="", token=printed, anchor="", definition=f"{name} ({arm} arm)",
                         old_computed=raw(v), new_computed="", old_formatted=" / ".join(sorted(got)),
                         old_reproduces="yes" if not ok else "no", new_value="",
                         status="PASS (does not reproduce, as required)" if ok else "FAIL (wrongly reproduces)", note=""))
    for name, fn, kind, printed in POS_NEW:
        v = fn(A["new"])
        got = fmt_local(kind, v, printed)
        rows.append(dict(row_type="positive_control_new_vs_03", file="chapters_v2/03_Results.md", line="", token=printed, anchor="",
                         definition=name, old_computed="", new_computed=raw(v), old_formatted=got,
                         old_reproduces="", new_value="", status="PASS" if got == printed else "FAIL", note=""))

    df = pd.DataFrame(rows)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "P9_second_pass_table.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 70)
    print("tables used by the SI (in scope): Table_04_validation_gates.md (S1), Table_07_limitations.md (S2), "
          "SI/Table_A1_A2.md (S3)")
    print("table files NOT used by the manuscript/SI (not edited):")
    for t in NOT_USED:
        print("   ", t)
    a = df[df.row_type == "arm"]
    print("\nARM items")
    print(a[["file", "line", "token", "old_formatted", "old_reproduces", "new_value", "status", "note"]].to_string(index=False))
    c = df[df.row_type == "claim"]
    print("\nCLAIMS")
    print(c[["file", "line", "token", "old_computed", "new_computed", "status"]].to_string(index=False))
    k = df[df.row_type == "constant"]
    print(f"\nCONSTANTS: {len(k)} lines, {int(k.note.str.split().str[0].astype(int).sum())} numeric tokens "
          f"(per file: {k.groupby('file').size().to_dict()})")
    n = df[df.row_type == "negative_control"]
    print("\nNEGATIVE CONTROLS")
    print(n[["definition", "token", "old_formatted", "status"]].to_string(index=False))
    p = df[df.row_type == "positive_control_new_vs_03"]
    print("\nPOSITIVE CONTROLS (new arm vs 03_Results, already P10R)")
    print(p[["definition", "token", "old_formatted", "status"]].to_string(index=False))
    sub = a[a.status == "substitute"]
    print(f"\nSUMMARY: arm items {len(a)}; substitute {len(sub)} (value changes {int((sub.note == 'value changes').sum())}, "
          f"same value {int((sub.note != 'value changes').sum())}); not reproduced {int((a.status == 'not_reproduced').sum())}; "
          f"negative controls {int(n.status.str.startswith('PASS').sum())}/{len(n)} PASS; "
          f"positive controls {int((p.status == 'PASS').sum())}/{len(p)} PASS; "
          f"claims with meaning changed {int(c.status.str.startswith('MEANING').sum())}")
    if not n.status.str.startswith("PASS").all() or not (p.status == "PASS").all():
        print("CONTROL FAILURE: not applying")
        return 1

    if apply:
        for f in sorted(set(sub.file)):
            src = os.path.join(W, f)
            bak = os.path.join(os.path.dirname(src), TAG, os.path.basename(src))
            assert os.path.getsize(bak) > 0 and md5(bak) == md5(src), f"{f}: backup missing or differs; refusing"
            lines = read_lines(f)
            for _, r in sub[sub.file == f].iterrows():
                if r.new_value == r.token:
                    continue
                ln = int(r.line)
                assert lines[ln - 1].count(r.anchor) == 1
                lines[ln - 1] = lines[ln - 1].replace(r.anchor, r.anchor.replace(r.token, r.new_value))
                print(f"applied {f}:{ln}: '{r.anchor}' -> '{r.anchor.replace(r.token, r.new_value)}'")
            with open(src, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
