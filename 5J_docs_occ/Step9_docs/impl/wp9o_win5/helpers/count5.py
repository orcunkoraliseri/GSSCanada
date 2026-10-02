# -*- coding: utf-8 -*-
"""Step 9o item 2: our own degenerate-surface counter (Step 9k code `wp9k/helpers/degen_lib.py`, tolerance 0.01 m, also 1 mm) on the Madrid
IDFs of `_win_2026-10-05`, and again on `_win_2026-10-03` (reproduction of `wp9k/degenerate_win3.csv`). Iterates stems of md5_2026-10-05.txt
(the 10-05 fleet.lst lists only the 171 changed stems). Madrid only; no UK path.
Writes ../degenerate_win5.csv (stems with >=1 degenerate surface on 10-05) and ../degenerate_win3_rerun.csv (same counter on 10-03).
Planted control: a copy of one clean 10-05 IDF with one 4-vertex wall squeezed to a sliver must be flagged (printed).
"""
import os, sys, io, csv, re
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(HERE)
IMP = os.path.dirname(OUTD)
sys.path.insert(0, os.path.join(IMP, "wp9k", "helpers"))
from degen_lib import read_surfaces, degenerate
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
OLD = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-03"
NEW = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-05"
TOL = 0.01


def count_path(path):
    s = read_surfaces(path)
    hits = [(x[1], x[3] if x[0].startswith("BUILDING") else "window", x[2]) for x in s if degenerate(x[4], TOL, TOL)]
    n1 = sum(degenerate(x[4], 0.001, 0.001) for x in s)
    return hits, n1, len(s)


def work(a):
    ver, stem = a
    root = NEW if ver == "new" else OLD
    hits, n1, ns = count_path(root + "/idfs/%s.idf" % stem)
    return ver, stem, hits, n1, ns


def write(rows, p):
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["district", "stem", "n_degenerate", "names", "boundary_types", "n_degenerate_1mm", "n_surfaces_read"])
        w.writerows(rows)


if __name__ == "__main__":
    stems = [ln.strip().split()[-1][:-4] for ln in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") if ln.strip()]
    jobs = [(v, s) for v in ("old", "new") for s in stems]
    with Pool(10) as p:
        res = p.map(work, jobs, chunksize=8)
    for ver, fn in (("old", "degenerate_win3_rerun.csv"), ("new", "degenerate_win5.csv")):
        rows = [["ES-MAD-BERRUGUETE", st, len(h), ";".join(x[0] for x in h), ";".join(sorted(set(x[1] for x in h))), n1, ns]
                for v, st, h, n1, ns in res if v == ver and h]
        write(rows, os.path.join(OUTD, fn))
        print(ver, "buildings with >=1 degenerate:", len(rows), "surfaces:", sum(r[2] for r in rows), "| at 1 mm: buildings", sum(1 for v, st, h, n1, ns in res if v == ver and n1 > 0),
              "surfaces", sum(n1 for v, st, h, n1, ns in res if v == ver), "| surfaces read", sum(ns for v, st, h, n1, ns in res if v == ver))
    # planted control: clean 10-05 stem, squeeze one 4-vertex wall
    clean = next(st for v, st, h, n1, ns in res if v == "new" and not h and st not in ())
    txt = io.open(NEW + "/idfs/%s.idf" % clean, encoding="utf-8", newline="").read()
    m = re.search(r"^BUILDINGSURFACE:DETAILED,(.*?);", txt, re.S | re.M | re.I)
    body = m.group(0)
    lines = body.split(chr(10))
    vx = {}
    for i, l in enumerate(lines):
        mm = re.search(r"!- Vertex (\d+) ([XYZ])coordinate", l)
        if mm:
            vx[(int(mm.group(1)), mm.group(2))] = i
    vx.setdefault((4, "Z"), len(lines) - 1)      # the match stops at the ';', so the last line has no comment
    print("PLANT stem", clean, "coordinate lines found", len(vx))
    def val(i):
        return float(lines[i].split("!")[0].strip().rstrip(",;"))
    for k in (2, 3, 4):                                    # squeeze vertices 2..4 onto vertex 1 (within 3 mm)
        for ax in "XYZ":
            i = vx[(k, ax)]
            end = ";" if k == 4 and ax == "Z" else ","
            lines[i] = "    %.6f%s  !- Vertex %d %scoordinate" % (val(vx[(1, ax)]) + 0.001 * k, end, k, ax)
    os.makedirs(os.path.join(OUTD, "planted"), exist_ok=True)
    pp = os.path.join(OUTD, "planted", "planted_%s.idf" % clean)
    io.open(pp, "w", encoding="utf-8", newline="").write(txt.replace(body, chr(10).join(lines), 1))
    hits, n1, ns = count_path(pp)
    print("PLANT result: degenerate surfaces flagged", len(hits), "(unplanted 0); named", [h[0] for h in hits][:2])
