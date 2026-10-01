# -*- coding: utf-8 -*-
"""5J Step 7 part B: the district writer equals the sums of per-dwelling hourly files (Speed CPU job; Spain only).
usage: s7_wcheck.py a   draws 0-9 of draws/ against part A's per-dwelling hourly files pilot/pred_S3/ (relative 1e-6)
       s7_wcheck.py b   the 20 check draws of draws/ against the per-dwelling hourly files pred_check/ (written by s7_draws_gpu.py hourly)
For every draw: district hourly (all, in-range twins) and per-dwelling annual from the file sums vs the draw file.
Metrics: annual relative error per target (district, in-range, and the worst single dwelling), and the largest hourly absolute difference
divided by the file's peak-hour total. PASS when all <= 1e-6. Seen failing: the same comparison on a copy of the file sums with 1e-5 of the
annual total added to ONE hour of ONE dwelling must FAIL (planted quantity itself, not a multiplied factor)."""
import io, json, multiprocessing as mp, os, sys, time
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import s7_common as s7
import s7_draws as dr
import s5_common as c

TOL = 1e-6
H = c.H


def read_run(path, nd):
    df = pd.read_csv(path, comment="#", compression="gzip", usecols=["dwelling", "hour"] + c.TARGETS)
    assert len(df) == nd * H, (path, len(df), nd)
    assert (df["dwelling"].to_numpy() == np.repeat(np.arange(nd), H)).all() and (df["hour"].to_numpy() == np.tile(np.arange(1, H + 1), nd)).all(), path
    return df[c.TARGETS].to_numpy(dtype=np.float64).reshape(nd, H, 4)


def file_sums(args):
    root, d, twins_nd, inr = args
    tids = [t[0] for t in twins_nd]
    ha = np.zeros((H, 4))
    hi = np.zeros((H, 4))
    ann = []
    for tid, cls, nd, _r in twins_nd:
        a = read_run("%s/%s/es_madrid_%s_d%03d.csv.gz" % (root.rstrip("/"), s7.CLIMATE, tid, d), nd)
        s = a.sum(0)
        ha += s
        if inr[tid]:
            hi += s
        ann.append(a.sum(1))
    return d, ha, hi, np.concatenate(ann, 0)


def compare(ha_f, hi_f, ann_f, z):
    out = {}
    for nm, f, g in (("all", ha_f, z["hourly_all"]), ("inrange", hi_f, z["hourly_inrange"])):
        fa, ga = f.sum(0), g.sum(0)
        out["annual_rel_%s" % nm] = float((np.abs(fa - ga) / np.where(fa > 0, fa, 1.0)).max())
        pk = f.sum(1).max()
        out["hourly_abs_over_peak_%s" % nm] = float(np.abs(f - g).max() / max(pk, 1e-12))
    an = z["annual"]
    out["dwelling_annual_rel_worst"] = float((np.abs(ann_f - an) / np.where(ann_f > 1e-9, ann_f, 1.0)).max())
    return out


def main():
    mode = sys.argv[1]
    s7.stamp("s7_wcheck %s start" % mode)
    fails = []
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    twins = dr.load_twins()
    rng = {r["twin_id"]: r["range"] == "in_range" for r in s7.read_csv(s7.D + "out/twin_range_es.csv")}
    if mode == "a":
        draws, root = list(range(10)), s7.D + "pilot/pred_S3"
    else:
        draws, root = list(dj["check_indices"]), s7.D + "pred_check"
    z = {d: np.load(s7.D + "draws/d%04d.npz" % d) for d in draws}
    t0 = time.time()
    with mp.Pool(2) as pool:
        res = pool.map(file_sums, [(root, d, twins, rng) for d in draws], chunksize=1)
    print("READ_FILES draws=%d files=%d seconds=%.0f" % (len(draws), 100 * len(draws), time.time() - t0), flush=True)
    worst = {}
    for d, ha, hi, ann in res:
        m = compare(ha, hi, ann, z[d])
        ok = all(v <= TOL for v in m.values())
        print("WCHECK draw %d %s %s" % (d, "PASS" if ok else "FAIL", " ".join("%s=%.2e" % (k, v) for k, v in m.items())), flush=True)
        if not ok:
            fails.append(d)
        for k, v in m.items():
            worst[k] = max(worst.get(k, 0.0), v)
    print("WCHECK worst over %d draws: %s" % (len(draws), " ".join("%s=%.2e" % (k, v) for k, v in worst.items())))
    # seen failing: plant 1e-5 of the annual total into one hour of one dwelling
    d, ha, hi, ann = res[0]
    ann2 = ann.copy()
    ann2[0, 0] += 1e-5 * ann[:, 0].sum()
    ha2 = ha.copy()
    ha2[4000, 0] += 1e-5 * ha[:, 0].sum()
    hi2 = hi.copy()
    m2 = compare(ha2, hi2, ann2, z[d])
    caught = not all(v <= TOL for v in m2.values())
    print("PLANTED %s CAUGHT=%s (%s)" % (d, caught, " ".join("%s=%.2e" % (k, v) for k, v in m2.items())))
    if not caught:
        fails.append("planted_not_caught")
    print("SUMMARY fails=%d %s" % (len(fails), fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
