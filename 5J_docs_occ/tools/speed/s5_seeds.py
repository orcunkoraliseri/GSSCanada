# -*- coding: utf-8 -*-
"""5J Step 5 part E, step E (CPU, 1 core): seeds and the blind control, from the FROZEN scorer's score files (no model is run).
Parses `GATE G5J.3` / `GATE G5J.4` / `GATE G5J.2` lines. All score files below use B1 clipped at 0 kWh (`--b1 pred/B1_clip0`, AMENDMENT 3).
  S seeds 1-3 : score_S3_vsC.txt (pinned winner, seed 1, also carries the G5J.4 lines of C seed 1 as control), score_S_seed2.txt, score_S_seed3.txt
  C seeds 1-3 : score_C_seed1.txt ... score_C_seed3.txt   (C as the model: its own G5J.3 lines)
  INFO        : score_S3.txt (the winner against UNCLIPPED B1, R7 as run), kept for comparison, never overwritten.
Reports per file: G5J.3 PASS cells (of 32), median G5J.3 R2 over the 16 heating + cooling cells, G5J.2 PASS cells; the spread (min, max)
of the median R2 over the 3 seeds for S and for C (INFO, val 2.4); G5J.4 = C seed 1 FAILS G5J.3 (cells where C passes are printed;
"C passes" is a result to report, never tuned away). Seen failing: a flipped verdict moves the count by 1; the G5J.4 evaluator applied
to the winner's own score file (as if it were C) reports "C passes". Writes train/winner/seeds.json."""
import json, os, re, statistics, sys
T = "/speed-scratch/o_iseri/5J/train/"
LINE = re.compile(r"^GATE (G5J\.[234]) country=(\S+) class=(\S+) target=(\S+) VERDICT=(\S+)(.*)$")


def parse(text):
    out = {"G5J.3": {}, "G5J.2": {}, "G5J.4": {}}
    for ln in text.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        g, c, k, t, v, rest = m.groups()
        cell = (c, k, t)
        if g == "G5J.3":
            mm = re.search(r"r2=(-?[0-9.eE+-]+|nan)", rest)
            out[g][cell] = (v, float(mm.group(1)) if mm else float("nan"))
        else:
            out[g][cell] = v
    return out


def numbers(p):
    g3 = p["G5J.3"]
    p3 = sum(1 for x in g3.values() if x[0] == "PASS")
    hc = [(-1e18 if x[1] != x[1] else x[1]) for cell, x in g3.items() if cell[2] in ("heating", "cooling")]
    return {"n_g3_lines": len(g3), "g53_pass": p3, "n_hc_cells": len(hc), "median_r2_heat_cool": statistics.median(hc) if hc else float("nan"),
            "g52_pass": sum(1 for v in p["G5J.2"].values() if v == "PASS"), "n_g2_lines": len(p["G5J.2"])}


def g54_from_g53(p):
    """G5J.4 for a control file: PASS iff the control FAILS G5J.3 on every one of the 32 cells; returns (verdict, cells where it passes)."""
    cells = sorted(cell for cell, x in p["G5J.3"].items() if x[0] == "PASS")
    return ("PASS" if not cells and len(p["G5J.3"]) == 32 else "FAIL"), cells


def load(name):
    f = T + "score/score_%s.txt" % name
    txt = open(f).read()
    summ = [l for l in txt.splitlines() if l.startswith("SUMMARY PASS")]
    p = parse(txt)
    n = numbers(p)
    if n["n_g3_lines"] != 32 or n["n_hc_cells"] != 16 or n["n_g2_lines"] != 32 or "crashed=False" not in " ".join(summ):
        print("SEEDS FAIL: score file %s malformed: %s %s" % (f, n, summ))
        sys.exit(1)
    print("%-12s %s | %s" % (name, summ[0], n), flush=True)
    return p, n, txt


FILES = {"S1": "S3_vsC", "S2": "S_seed2", "S3": "S_seed3", "C1": "C_seed1", "C2": "C_seed2", "C3": "C_seed3"}
data = {k: load(v) for k, v in FILES.items()}
s3_unclipped = load("S3")

print("\n--- seen failing (1): one verdict flipped in a copy of the S seed 1 score file")
lines = data["S1"][2].splitlines()
base = numbers(parse("\n".join(lines)))
ff, ft = ("VERDICT=PASS", "VERDICT=FAIL")
if not any(l.startswith("GATE G5J.3 ") and ff in l for l in lines):
    ff, ft = ft, ff
for i, l in enumerate(lines):
    if l.startswith("GATE G5J.3 ") and ff in l:
        lines[i] = l.replace(ff, ft, 1)
        break
pl = numbers(parse("\n".join(lines)))
print("PLANTED G5J.3 %s -> %s: g53_pass %d -> %d ; SEEN_FAILING %s" % (ff, ft, base["g53_pass"], pl["g53_pass"], "OK" if abs(pl["g53_pass"] - base["g53_pass"]) == 1 else "NOT_OK"))
if abs(pl["g53_pass"] - base["g53_pass"]) != 1:
    sys.exit(1)
print("--- seen failing (2): the G5J.4 evaluator on the winner's own score file (as if it were C)")
vplant, cplant = g54_from_g53(data["S1"][0])
print("G5J.4 evaluator on S seed 1 file as 'C': %s, %d cells pass G5J.3 ; SEEN_FAILING %s" % (vplant, len(cplant), "OK (reports C passes)" if vplant == "FAIL" and cplant else "NOT_OK"))
if not (vplant == "FAIL" and cplant):
    sys.exit(1)

print("\n--- G5J.4: C seed 1 vs G5J.3 (C scored as the model; 32 cells)")
v4, cells4 = g54_from_g53(data["C1"][0])
print("G5J.4 (from C seed 1 own G5J.3 lines) = %s ; cells where C seed 1 PASSES G5J.3: %d %s" % (v4, len(cells4), cells4))
g4_lines = data["S1"][0]["G5J.4"]
cnt4 = {v: sum(1 for x in g4_lines.values() if x == v) for v in ("PASS", "FAIL", "NOT_EVALUABLE")}
print("G5J.4 lines in score_S3_vsC (C seed 1 as the control of the pinned winner): %s (32 expected; PASS = control fails G5J.3)" % cnt4)
fail4 = sorted(cell for cell, x in g4_lines.items() if x != "PASS")
print("G5J.4 cells not PASS in score_S3_vsC: %s" % fail4)
for cell in cells4:
    print("   C seed 1 passes G5J.3 at %s: %s" % (cell, data["C1"][0]["G5J.3"][cell]))
agree = (sorted(cells4) == fail4)
print("C seed 1 own G5J.3 PASS cells equal the not-PASS G5J.4 cells of score_S3_vsC: %s" % agree)

print("\n--- seeds (G5J.3 PASS cells of 32, median G5J.3 R2 over 16 heating + cooling cells)")
res = {}
for grp in ("S", "C"):
    rows = []
    for s in (1, 2, 3):
        n = data["%s%d" % (grp, s)][1]
        rows.append({"seed": s, "g53_pass": n["g53_pass"], "median_r2_heat_cool": n["median_r2_heat_cool"], "g52_pass": n["g52_pass"]})
        print("%s seed %d: G5J.3 PASS %d/32, median R2 heat+cool %.4f, G5J.2 PASS %d/32" % (grp, s, n["g53_pass"], n["median_r2_heat_cool"], n["g52_pass"]))
    med = [r["median_r2_heat_cool"] for r in rows]
    pas = [r["g53_pass"] for r in rows]
    res[grp] = {"seeds": rows, "median_r2_min": min(med), "median_r2_max": max(med), "median_r2_spread": max(med) - min(med),
                "g53_pass_min": min(pas), "g53_pass_max": max(pas)}
    print("%s spread over the 3 seeds (INFO): median R2 min %.4f max %.4f (range %.4f); G5J.3 PASS min %d max %d" %
          (grp, min(med), max(med), max(med) - min(med), min(pas), max(pas)))
n0 = s3_unclipped[1]
print("INFO winner vs UNCLIPPED B1 (score_S3.txt, R7 as run): G5J.3 PASS %d/32, median R2 %.4f" % (n0["g53_pass"], n0["median_r2_heat_cool"]))
out = {"files": {k: "score/score_%s.txt" % v for k, v in FILES.items()}, "b1": "pred/B1_clip0 (clipped at 0 kWh)", "S": res["S"], "C": res["C"],
       "g54_C_seed1": {"verdict": v4, "cells_where_C_passes_g53": [list(c) for c in cells4], "lines_in_score_S3_vsC": cnt4,
                       "cells_not_pass_in_S3_vsC": [list(c) for c in fail4], "agree": agree},
       "winner_vs_unclipped_b1": {"g53_pass": n0["g53_pass"], "median_r2_heat_cool": n0["median_r2_heat_cool"]}}
json.dump(out, open(T + "winner/seeds.json", "w"), indent=1)
print("SEEDS_JSON written %s" % (T + "winner/seeds.json"))
print("SEEDS_DONE G5J.4=%s" % v4)
