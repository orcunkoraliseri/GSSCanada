# -*- coding: utf-8 -*-
"""Step 9p item 4: does the static builder depend on absolute coordinates? Run `extract()` of tools/5thJ_modelA_static.py on the 10-03 (UTM) and
10-05 (local origin) text of every origin-only stem (109): flat rows, building dict and aux dict must agree. Floats agree when
|a - b| <= 1e-6 * max(|a|, |b|) + 0.005 (UTM-size products of about 1e12 leave rounding of 1e-4 to 1e-3 m2 in area sums; the local origin is the exact one).
Seen failing: the same comparison with one wall vertex of the 10-05 text raised by 0.5 m (z of vertex 1 of the first outdoor wall) must flag the stem.
Bologna folders only; at most 10 processes."""
import os, sys, io, re
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools"))
sys.path.insert(0, TOOLS)
os.environ["MODELA_VINTAGE"] = "win_2026-10-05"
os.environ["MODELA_COUNTRY"] = "IT"
import importlib
S = importlib.import_module("5thJ_modelA_static")
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
OLD = EU11 + "/IT-BOL-GALVANI2_win_2026-10-03"
NEW = EU11 + "/IT-BOL-GALVANI2_win_2026-10-05"
D = "IT-BOL-GALVANI2"
REL, ABS = 1e-6, 5e-3


def compare(a, b, key, worst):
    """returns True when equal; worst = [max abs float deviation, description]"""
    if isinstance(a, float) and isinstance(b, float):
        if a != a and b != b:
            return True
        dev = abs(a - b)
        if dev > worst[0]:
            worst[0], worst[1] = dev, "%s %r vs %r" % (key, a, b)
        return dev <= REL * max(abs(a), abs(b)) + ABS
    if isinstance(a, dict):
        if not isinstance(b, dict) or a.keys() != b.keys():
            return False
        ok = True
        for k in a:
            ok &= compare(a[k], b[k], str(k), worst)
        return ok
    if isinstance(a, (list, tuple)):
        if len(a) != len(b):
            return False
        ok = True
        for x, y in zip(a, b):
            ok &= compare(x, y, key, worst)
        return ok
    return a == b


def one(args):
    stem, plant = args
    to = io.open(OLD + "/idfs/%s.idf" % stem, encoding="utf-8", newline="").read()
    tn = io.open(NEW + "/idfs/%s.idf" % stem, encoding="utf-8", newline="").read()
    if plant:
        for mm in re.finditer(r"^BUILDINGSURFACE:DETAILED,.*?;", tn, re.S | re.M | re.I):
            seg = mm.group(0)
            if re.search(r"^\s*Wall,", seg, re.I | re.M) and re.search(r"^\s*Outdoors,", seg, re.I | re.M):
                mx = re.search(r"([-0-9.eE+]+)(\s*[,;]\s*!- Vertex 1 Zcoordinate)", seg)
                seg2 = seg[:mx.start(1)] + "%.9f" % (float(mx.group(1)) + 0.5) + seg[mx.end(1):]
                tn = tn.replace(seg, seg2, 1)
                break
    ro, bo, ao = S.extract(to, D, stem)
    rn, bn, an = S.extract(tn, D, stem)
    worst = [0.0, ""]
    ok = bool(compare(ro, rn, "rows", worst) & compare(bo, bn, "bld", worst) & compare(ao, an, "aux", worst))
    return stem, ok, len(ro), ao["normal_viol"], an["normal_viol"], ao["ambiguous"], an["ambiguous"], worst[0], worst[1]


if __name__ == "__main__":
    origin = []
    for ln in io.open(NEW + "/changed_stems.txt", encoding="utf-8"):
        p = ln.rstrip("\r\n").split("\t")
        if len(p) > 1 and p[1] == "origin_shift":
            origin.append(p[0])
    with Pool(10) as pool:
        res = pool.map(one, [(s, False) for s in origin], chunksize=4)
        pl = pool.map(one, [(s, True) for s in origin[:5]], chunksize=1)
    w = max(res, key=lambda r: r[7])
    print("origin-only stems", len(origin), "extract() old (UTM) vs new (local): agree", sum(1 for r in res if r[1]), "of", len(res),
          "| flats read", sum(r[2] for r in res), "| outward-normal violations old/new", sum(r[3] for r in res), sum(r[4] for r in res),
          "| ambiguous old/new", sum(r[5] for r in res), sum(r[6] for r in res))
    print("largest float deviation", w[7], "on", w[0], w[8], "(tolerance 1e-6 relative + 0.005)")
    print("PLANT one wall vertex raised by 0.5 m in the 10-05 text of 5 stems: flagged as different", sum(1 for r in pl if not r[1]), "of", len(pl), "| deviations", [round(r[7], 4) for r in pl])
