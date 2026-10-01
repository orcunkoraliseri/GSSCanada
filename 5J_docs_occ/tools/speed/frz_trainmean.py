# -*- coding: utf-8 -*-
"""5J Step 4, Part D helper: 'training mean per hour of year' = mean over all dwelling series of the DEVELOPMENT split,
per climate and dwelling class and target, for each of the 8,760 hours. Speed job only. Writes out/trainmean.npz."""
import sys, importlib, collections, multiprocessing as mp
import numpy as np
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
sc = importlib.import_module("5thJ_04_scorer")
sl = sc.sl


def work(r):
    log = []
    arr, st = sc.read_run(sc.TRUTH, r["climate"], r["run_id"], r["nd"], log, "truth_development")
    if arr is None:
        return r["climate"], r["cls"], None, 0, r["run_id"] + ":" + st, len(log)
    return r["climate"], r["cls"], arr.sum(0), arr.shape[0], "ok", len(log)


def main():
    ids = sl.load_split("development")
    sc._init(set(ids))
    runs = sc.load_runs()
    rows = [runs[i] for i in ids]
    assert all(r["replicate"] == 0 and r["pool"] != "b0" for r in rows)
    S, N, bad, nlog = {}, collections.Counter(), [], 0
    with mp.Pool(8, initializer=sc._init, initargs=(set(ids),)) as p:
        for cl, cls, s, n, st, nl_ in p.imap_unordered(work, rows, chunksize=4):
            nlog += nl_
            if s is None:
                bad.append(st)
                continue
            k = "%s|%s" % (cl, cls)
            S[k] = S.get(k, 0) + s
            N[k] += n
    print("DEVELOPMENT runs %d unreadable %d %s opens %d" % (len(rows), len(bad), bad[:3], nlog))
    out = {k: S[k] / N[k] for k in S}
    np.savez("/speed-scratch/o_iseri/5J/freeze/out/trainmean.npz", **out)
    for k in sorted(out):
        print("TRAINMEAN %s dwelling_series=%d mean_per_target=%s" % (k, N[k], np.round(out[k].mean(0), 4).tolist()))


main()
