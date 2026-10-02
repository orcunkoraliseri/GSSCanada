# -*- coding: utf-8 -*-
"""Step 9p item 2: our own degenerate-surface counter (Step 9k code `wp9k/helpers/degen_lib.py`, tolerance 0.01 m, also 1 mm) on the Bologna IDFs of
`_win_2026-10-05` and, again, on `_win_2026-10-03` (reproduction of the 20 Bologna rows of `wp9k/degenerate_win3.csv`). Iterates stems of md5_2026-10-05.txt.
Bologna only; no UK path. At most 10 processes.
Writes ../degenerate_bol5.csv (stems with >=1 degenerate surface on 10-05), ../degenerate_bol3_rerun.csv (same counter on 10-03).
Controls (seen failing / seen firing):
  (a) the 10-03 files of the 20 old-list stems fire (counts equal to the 9k list);
  (b) coordinate-size test: the SAME 10-03 files with every x, y vertex field shifted by (-685000, -4928000) in the text give the same hits per stem;
      and the reverse (a 10-05 file shifted back by +685000, +4928000) gives the same hits;
  (c) a clean 10-05 IDF with one wall squeezed to a sliver (all vertices within 3 mm) is flagged, the unplanted file gives 0.
"""
import os, sys, io, csv, re, tempfile
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(HERE)
IMP = os.path.dirname(OUTD)
sys.path.insert(0, os.path.join(IMP, "wp9k", "helpers"))
from degen_lib import read_surfaces, degenerate
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
OLD = EU11 + "/IT-BOL-GALVANI2_win_2026-10-03"
NEW = EU11 + "/IT-BOL-GALVANI2_win_2026-10-05"
DX, DY = 685000.0, 4928000.0
TOL = 0.01
SCR = os.environ.get("P9_SCRATCH") or tempfile.gettempdir()


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


RX = re.compile(r"^(\s*)([-+0-9.eE]+)(\s*[,;]\s*!- Vertex \d+ ([XY])coordinate)", re.M)


def shift_text(txt, sign):
    """sign=-1: new = old - offset (to local origin); +1: back to UTM. x, y fields of every `!- Vertex n X/Ycoordinate` line."""
    def f(m):
        d = DX if m.group(4) == "X" else DY
        return "%s%.9f%s" % (m.group(1), float(m.group(2)) + sign * d, m.group(3))
    return RX.sub(f, txt)


def shifted_hits(path, sign):
    txt = io.open(path, encoding="utf-8", newline="").read()
    t2 = shift_text(txt, sign)
    nlines = len(RX.findall(txt))
    p = os.path.join(SCR, "shifted_%s_%s" % ("local" if sign < 0 else "utm", os.path.basename(path)))
    io.open(p, "w", encoding="utf-8", newline="").write(t2)
    h, n1, ns = count_path(p)
    os.remove(p)
    return h, n1, ns, nlines


if __name__ == "__main__":
    stems = [ln.strip().split()[-1][:-4] for ln in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") if ln.strip()]
    jobs = [(v, s) for v in ("old", "new") for s in stems]
    with Pool(10) as p:
        res = p.map(work, jobs, chunksize=8)
    for ver, fn in (("old", "degenerate_bol3_rerun.csv"), ("new", "degenerate_bol5.csv")):
        rows = [["IT-BOL-GALVANI2", st, len(h), ";".join(x[0] for x in h), ";".join(sorted(set(x[1] for x in h))), n1, ns]
                for v, st, h, n1, ns in res if v == ver and h]
        write(rows, os.path.join(OUTD, fn))
        print(ver, "buildings with >=1 degenerate:", len(rows), "surfaces:", sum(r[2] for r in rows), "| at 1 mm: buildings", sum(1 for v, st, h, n1, ns in res if v == ver and n1 > 0),
              "surfaces", sum(n1 for v, st, h, n1, ns in res if v == ver), "| surfaces read", sum(ns for v, st, h, n1, ns in res if v == ver))
    # (a) reproduction of the 9k list (Bologna rows)
    ref = {}
    for r in csv.DictReader(io.open(os.path.join(IMP, "wp9k", "degenerate_win3.csv"), encoding="utf-8", newline="")):
        if r["district"] == "IT-BOL-GALVANI2":
            ref[r["stem"]] = int(r["n_degenerate"])
    mine = {st: len(h) for v, st, h, n1, ns in res if v == "old" and h}
    print("REPRO 9k Bologna list: stems", len(ref), "mine on 10-03:", len(mine), "same stem set:", set(ref) == set(mine), "same counts per stem:", ref == mine, "surfaces", sum(ref.values()), sum(mine.values()))
    # (b) coordinate-size test on the 20 old-list stems (10-03 UTM files -> local copy in text) and on the 10-05 flagged stems (local -> UTM)
    bad = 0
    for st in sorted(ref):
        h0, n10, ns0 = count_path(OLD + "/idfs/%s.idf" % st)
        h1, n11, ns1, nl = shifted_hits(OLD + "/idfs/%s.idf" % st, -1)
        ok = ([x[0] for x in h0] == [x[0] for x in h1]) and n10 == n11 and ns0 == ns1 and nl > 0
        bad += (not ok)
    print("COORD-SIZE TEST 1: 20 old-list stems, 10-03 file vs the same file shifted to the local origin in text: stems whose hits differ:", bad, "of", len(ref))
    newhit = sorted(st for v, st, h, n1, ns in res if v == "new" and h)
    for st in newhit[:5]:
        h0, n10, ns0 = count_path(NEW + "/idfs/%s.idf" % st)
        h1, n11, ns1, nl = shifted_hits(NEW + "/idfs/%s.idf" % st, +1)
        print("COORD-SIZE TEST 2: 10-05 hit stem", st, "hits local", len(h0), "hits after shifting back to UTM", len(h1), "same names", [x[0] for x in h0] == [x[0] for x in h1])
    # clean 10-05 stems shifted back to UTM must stay clean (5 stems)
    clean = [st for v, st, h, n1, ns in res if v == "new" and not h][:5]
    print("COORD-SIZE TEST 3: 5 clean 10-05 stems shifted back to UTM:", [len(shifted_hits(NEW + "/idfs/%s.idf" % st, +1)[0]) for st in clean], "hits (expect all 0)")
    # (c) planted sliver on a clean 10-05 stem
    clean = next(st for v, st, h, n1, ns in res if v == "new" and not h)
    txt = io.open(NEW + "/idfs/%s.idf" % clean, encoding="utf-8", newline="").read()
    m = re.search(r"^BUILDINGSURFACE:DETAILED,(.*?);", txt, re.S | re.M | re.I)
    body = m.group(0)
    lines = body.split(chr(10))
    vx = {}
    for i, l in enumerate(lines):
        mm = re.search(r"!- Vertex (\d+) ([XYZ])coordinate", l)
        if mm:
            vx[(int(mm.group(1)), mm.group(2))] = i
    print("PLANT stem", clean, "coordinate lines found", len(vx), "nverts", len(vx) // 3)
    nv = len(vx) // 3

    def val(i):
        return float(lines[i].split("!")[0].strip().rstrip(",;"))
    for k in range(2, nv + 1):
        for ax in "XYZ":
            i = vx[(k, ax)]
            end = ";" if (k == nv and ax == "Z") else ","
            lines[i] = "    %.6f%s  !- Vertex %d %scoordinate" % (val(vx[(1, ax)]) + 0.001 * k, end, k, ax)
    os.makedirs(os.path.join(OUTD, "planted"), exist_ok=True)
    pp = os.path.join(OUTD, "planted", "planted_%s.idf" % clean)
    io.open(pp, "w", encoding="utf-8", newline="").write(txt.replace(body, chr(10).join(lines), 1))
    hits, n1, ns = count_path(pp)
    print("PLANT result: degenerate surfaces flagged", len(hits), "(unplanted 0); named", [h[0] for h in hits][:2])
    # which of the 20 old stems are in the 109 origin-only / 1,070 rebuilt groups
    reason = {}
    for ln in io.open(NEW + "/changed_stems.txt", encoding="utf-8"):
        p = ln.rstrip("\r\n").split("\t")
        reason[p[0]] = p[1]
    newcount = {st: len(h) for v, st, h, n1, ns in res if v == "new" and h}
    rows = []
    for st in sorted(ref):
        rows.append((st, ref[st], reason.get(st, "?"), newcount.get(st, 0)))
    io.open(os.path.join(OUTD, "deferred_bol5_status.csv"), "w", encoding="utf-8", newline="").write("stem,n_degenerate_10_03,group_10_05,n_degenerate_10_05_ours\n" + "\n".join("%s,%d,%s,%d" % r for r in rows) + "\n")
    import collections
    print("OLD LIST by group:", collections.Counter(r[2] for r in rows), "still degenerate on 10-05:", sum(1 for r in rows if r[3] > 0), "; stems NOT in old list but degenerate on 10-05:", sorted(set(newcount) - set(ref)))
