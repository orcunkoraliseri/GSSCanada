# -*- coding: utf-8 -*-
"""5J Step 5 part D, step D (CPU): parse the 6 score files, apply rules R7.3, write train/winner/winner.json.
Order of the tie-break (R7.3): most G5J.3 PASS cells (of 32); tie -> highest median G5J.3 R2 over the 16 heating + cooling cells;
tie -> most G5J.2 PASS cells; tie -> lowest validation loss. Also: B1 line counts and the R7.5 skill interval of the winner vs B1
(reported either way, never tuned). Seen failing: the same parser on a copy with one verdict flipped."""
import glob, hashlib, json, os, re, statistics, sys
T = "/speed-scratch/o_iseri/5J/train/"
LINE = re.compile(r"^GATE (G5J\.[23]) country=(\S+) class=(\S+) target=(\S+) VERDICT=(\S+)(.*)$")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def parse(text):
    """-> {'G5J.3': {(country, class, target): (verdict, r2, skill, lo, hi)}, 'G5J.2': {cell: verdict}}"""
    out = {"G5J.3": {}, "G5J.2": {}}
    for ln in text.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        g, c, k, t, v, rest = m.groups()
        cell = (c, k, t)
        if g == "G5J.2":
            out[g][cell] = v
        else:
            def num(key):
                mm = re.search(key + r"=(\[?)(-?[0-9.eE+-]+|nan)", rest)
                return float(mm.group(2)) if mm else float("nan")
            ci = re.search(r"ci95=\[(\S+?),(\S+?)\]", rest)
            out[g][cell] = (v, num("r2"), num("skill_over_B1"), float(ci.group(1)) if ci else float("nan"), float(ci.group(2)) if ci else float("nan"))
    return out


def numbers(p):
    g3, g2 = p["G5J.3"], p["G5J.2"]
    p3 = sum(1 for x in g3.values() if x[0] == "PASS")
    hc = [x[1] for cell, x in g3.items() if cell[2] in ("heating", "cooling")]
    hc = [(-1e18 if v != v else v) for v in hc]
    med = statistics.median(hc) if hc else float("nan")
    p2 = sum(1 for v in g2.values() if v == "PASS")
    return {"n_g3_lines": len(g3), "n_g2_lines": len(g2), "g53_pass": p3, "median_r2_heat_cool": med, "n_heat_cool_cells": len(hc), "g52_pass": p2}


sl = json.load(open(T + "winner/shortlist.json"))["shortlist"]
res = []
for r in sl:
    f = T + "score/score_S%d.txt" % r["idx"]
    txt = open(f).read()
    summ = [l for l in txt.splitlines() if l.startswith("SUMMARY PASS")]
    p = parse(txt)
    n = numbers(p)
    if n["n_g3_lines"] != 32 or n["n_heat_cool_cells"] != 16 or "crashed=False" not in " ".join(summ):
        print("WINNER FAIL: score file %s malformed: %s %s" % (f, n, summ))
        sys.exit(1)
    res.append((r, n, p, txt))
    print("S%d (%s w%d %s lam=%g) SUMMARY: %s | %s" % (r["idx"], r["family"], r["width"], r["depth"], r["lam"], summ[0] if summ else "NONE", n))

print("\n--- seen failing: one verdict flipped in a copy of a score table")
txt0 = res[0][3]
lines = txt0.splitlines()
base = numbers(parse(txt0))
flip_from, flip_to = ("VERDICT=PASS", "VERDICT=FAIL")
if not any(l.startswith("GATE G5J.3 ") and flip_from in l for l in lines):
    flip_from, flip_to = flip_to, flip_from
for i, l in enumerate(lines):
    if l.startswith("GATE G5J.3 ") and flip_from in l:
        lines[i] = l.replace(flip_from, flip_to, 1)
        break
planted = numbers(parse("\n".join(lines)))
print("PLANTED a G5J.3 line %s -> %s in S%d copy: g53_pass %d -> %d" % (flip_from, flip_to, res[0][0]["idx"], base["g53_pass"], planted["g53_pass"]))
print("SEEN_FAILING %s" % ("OK (count moved by 1)" if abs(planted["g53_pass"] - base["g53_pass"]) == 1 else "NOT_OK (count did not move)"))
if abs(planted["g53_pass"] - base["g53_pass"]) != 1:
    sys.exit(1)

print("\n--- R7.3 tie-break")
surv = list(res)
steps = [("G5J.3 PASS cells (most)", lambda x: x[1]["g53_pass"], True),
         ("median G5J.3 R2 over 16 heating+cooling cells (highest)", lambda x: round(x[1]["median_r2_heat_cool"], 6), True),
         ("G5J.2 PASS cells (most)", lambda x: x[1]["g52_pass"], True),
         ("validation loss (lowest)", lambda x: x[0]["val_sum"], False)]
for name, key, hi in steps:
    best = max(key(x) for x in surv) if hi else min(key(x) for x in surv)
    print("step '%s': values %s" % (name, {"S%d" % x[0]["idx"]: key(x) for x in surv}))
    surv = [x for x in surv if key(x) == best]
    print("   survivors: %s" % ["S%d" % x[0]["idx"] for x in surv])
    if len(surv) == 1:
        break
if len(surv) > 1:
    surv.sort(key=lambda x: x[0]["idx"])
    print("   still tied after all four steps: lowest index taken")
w, wn, wp, _ = surv[0]
print("WINNER: S%d  %s w%d %s lam=%g  (%s)" % (w["idx"], w["family"], w["width"], w["depth"], w["lam"], wn))

ck = w["ckpt"] + "/best.pt"
cfg = json.load(open(w["ckpt"] + "/config.json"))
code = {os.path.basename(p): md5(p) for p in sorted(glob.glob(T + "s5_*.py")) + [T + "s5_grid.json"]}
info = json.load(open(w["ckpt"] + "/run_info.json"))
same = {k: (code.get(k) == v) for k, v in info["md5"].items()}
print("code md5 now vs run_info of the winner's training:", same)
b1p = parse(open(T + "score/score_B1.txt").read())
b1n = numbers(b1p)
print("B1 (scored with --b1 = B0, so its G5J.3 skill is against B0): %s" % b1n)
g3 = wp["G5J.3"]
lo_pos = [c for c, x in g3.items() if x[3] > 0]
hi_neg = [c for c, x in g3.items() if x[4] < 0]
hc = [c for c in g3 if c[2] in ("heating", "cooling")]
print("R7.5 winner vs B1, G5J.3 skill interval (r2 - r2_B1, ci95): excludes 0 above (lo>0) on %d of 32 cells (%d of 16 heating+cooling); "
      "excludes 0 below (hi<0) on %d of 32; contains 0 on %d" % (len(lo_pos), len([c for c in lo_pos if c in hc]), len(hi_neg), 32 - len(lo_pos) - len(hi_neg)))
out = {"config_index": w["idx"], "family": w["family"], "config": cfg, "ckpt": ck, "ckpt_md5": md5(ck), "code_md5": code,
       "code_md5_same_as_training": same, "seed": cfg["seed"], "validation_loss": w["val_sum"], "val_level": w["val_level"], "val_pair": w["val_pair"],
       "best_epoch": w["best_epoch"], "g53_pass": wn["g53_pass"], "median_r2_heat_cool": wn["median_r2_heat_cool"], "g52_pass": wn["g52_pass"],
       "b1_g53_pass": b1n["g53_pass"], "b1_g52_pass": b1n["g52_pass"],
       "r75_skill_ci_excludes0_above_cells": len(lo_pos), "r75_skill_ci_excludes0_below_cells": len(hi_neg),
       "all6": [{"idx": x[0]["idx"], "val_sum": x[0]["val_sum"], **x[1]} for x in res]}
json.dump(out, open(T + "winner/winner.json", "w"), indent=1)
print("WINNER_JSON written; ckpt md5 %s" % out["ckpt_md5"])
print("WINNER_DONE")
