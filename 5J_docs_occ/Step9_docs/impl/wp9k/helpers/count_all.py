"""Step 9k item 1: count degenerate surfaces over every building of the two districts on _win_2026-10-03.
Rule: remove coincident vertices (< 0.01 m) and collinear vertices (distance to line of neighbours < 0.01 m), repeat; < 3 left = degenerate.
Also prints the count with 0.001 m (EnergyPlus Engineering Reference says 1 mm) for comparison."""
import sys, csv, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from degen_lib import read_surfaces, degenerate
from multiprocessing import Pool
ROOT = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/%s_win_2026-10-03"
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
DISTS = ["ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"]
TOL = 0.01

def work(a):
    dist, stem = a
    s = read_surfaces(ROOT % dist + "/idfs/%s.idf" % stem)
    hits = [(x[1], x[3] if x[0].startswith("BUILDING") else "window", x[2]) for x in s if degenerate(x[4], TOL, TOL)]
    n1 = sum(degenerate(x[4], 0.001, 0.001) for x in s)
    return dist, stem, hits, n1, len(s)

if __name__ == "__main__":
    jobs = []
    for d in DISTS:
        for ln in open(ROOT % d + "/fleet.lst"):
            if ln.strip():
                jobs.append((d, ln.strip()))
    print("buildings to read:", len(jobs))
    with Pool(8) as p:
        res = p.map(work, jobs, chunksize=8)
    split = {}
    for d in DISTS:
        for sp in ("dev", "val", "test"):
            for r in csv.DictReader(open("%s/buildsplit_win3/%s_%s.csv" % (IMP, d, sp))):
                split[(d, r["stem"])] = sp
    held = {(r["district"], r["stem"]) for r in csv.DictReader(open(IMP + "/heldout_tinyflats_win3.csv"))}
    rows = []
    for dist, stem, hits, n1, ns in res:
        if hits:
            rows.append([dist, stem, len(hits), ";".join(h[0] for h in hits), ";".join(sorted(set(h[1] for h in hits))),
                         split.get((dist, stem), "not_modelA"), 1 if (dist, stem) in held else 0])
    with open(IMP + "/wp9k/degenerate_win3.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["district", "stem", "n_degenerate", "names", "boundary_types", "split", "heldout_tiny"])
        w.writerows(rows)
    print("surfaces read:", sum(r[4] for r in res))
    for d in DISTS:
        rr = [r for r in rows if r[0] == d]
        nb = sum(1 for r in res if r[0] == d)
        print(d, "buildings", nb, "with >=1 degenerate:", len(rr), "total degenerate surfaces:", sum(r[2] for r in rr),
              "| ModelA:", sum(1 for r in rr if r[5] != "not_modelA"),
              "| in heldout_tiny:", sum(r[6] for r in rr),
              "| split dev/val/test/not_modelA:", [sum(1 for r in rr if r[5] == k) for k in ("dev", "val", "test", "not_modelA")],
              "| ModelA and not heldout:", sum(1 for r in rr if r[5] != "not_modelA" and not r[6]),
              "| at 1 mm tol: buildings", sum(1 for r in res if r[0] == d and r[3] > 0), "surfaces", sum(r[3] for r in res if r[0] == d))
    bt = {}
    for r in rows:
        for t in r[4].split(";"): bt[t] = bt.get(t, 0) + 1
    print("buildings by boundary type (a building counted once per type):", bt)
    # calibration lines
    cal = ["1271cddbf6bd1e8a", "919761afea1827b3", "0275c53572b2ff9f", "7307694dddf93fb6", "504fa19567bbc2b7", "1ef46361a8060ff9", "13c60875a803e164", "b3f8d90890ff6314"]
    for dist, stem, hits, n1, ns in res:
        if stem in cal:
            print("CAL", stem, "n_degenerate", len(hits), "n_1mm", n1)
