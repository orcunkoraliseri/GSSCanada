# -*- coding: utf-8 -*-
"""5J Step 4, Part C: noise floor from the Step 3 replicates (split 'replicates' only). Speed job only.
Floor per target and class = RMS over (input, dwelling) of the standard deviation (ddof=1) of the annual total over the
repeats of one input. Writes out/floors.json and prints the table (val 5.1)."""
import sys, re, json, io, importlib, collections, multiprocessing as mp
import numpy as np
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
sc = importlib.import_module("5thJ_04_scorer")
sl = sc.sl


def work(r):
    log = []
    arr, st = sc.read_run(sc.TRUTH, r["climate"], r["run_id"], r["nd"], log, "truth_replicate")
    return r["run_id"], (arr.sum(1) if arr is not None else None), st, log


def main():
    ids = sl.load_split("replicates")
    sc._init(set(ids))
    runs = sc.load_runs()
    rows = [runs[i] for i in ids]
    with mp.Pool(4, initializer=sc._init, initargs=(set(ids),)) as p:
        res = p.map(work, rows, chunksize=4)
    log = [x for r in res for x in r[3]]
    bad = [(r[0], r[2]) for r in res if r[1] is None]
    print("REPLICATE_RUNS %d unreadable %d %s" % (len(res), len(bad), bad[:3]))
    grp = collections.defaultdict(list)
    for rid, ann, st, _ in res:
        grp[re.sub(r"_rep\d+$", "", rid)].append((rid, ann))
    print("INPUTS %d ; repeats per input: %s" % (len(grp), sorted(collections.Counter(len(v) for v in grp.values()).items())))
    print("example run ids of one input:", [x[0] for x in list(grp.values())[0]][:4])
    acc = {c: {t: [] for t in sc.TNAME} for c in sc.CLASSES}
    maxsp = {c: {t: 0.0 for t in sc.TNAME} for c in sc.CLASSES}
    nin = collections.Counter()
    nrep = collections.defaultdict(set)
    for key, v in sorted(grp.items()):
        cls = runs[v[0][0]]["cls"]
        A = np.stack([x[1] for x in v])                # [repeats, nd, 4]
        sd = A.std(axis=0, ddof=1)                     # [nd, 4]
        rng_ = A.max(0) - A.min(0)
        nin[cls] += 1
        nrep[cls].add(len(v))
        for t, tn in enumerate(sc.TNAME):
            acc[cls][tn].extend(sd[:, t].tolist())
            maxsp[cls][tn] = max(maxsp[cls][tn], float(rng_[:, t].max()))
    floor = {c: {} for c in sc.CLASSES}
    print("NOISE_FLOOR table: SD of the annual total (kWh) over the repeats of one input; file resolution %.8g")
    for c in sc.CLASSES:
        for tn in sc.TNAME:
            x = np.array(acc[c][tn])
            floor[c][tn] = float(np.sqrt((x ** 2).mean())) if len(x) else float("nan")
            print("FLOOR class=%s inputs=%d repeats=%s target=%s n_series=%d rms_sd=%.6g max_sd=%.6g max_spread=%.6g" %
                  (c, nin[c], sorted(nrep[c]), tn, len(x), floor[c][tn], x.max() if len(x) else float("nan"), maxsp[c][tn]))
    for c in sc.CLASSES:
        for tn in sc.TNAME:
            if not acc[c][tn]:
                floor[c][tn] = max(floor[o][tn] for o in sc.CLASSES if acc[o][tn])
                print("ASSUMPTION class=%s target=%s: no replicate input of this class exists (the 20 replicate inputs are SFH 10, MFH 4, AB 6); floor taken as the largest of the other classes = %.6g" % (c, tn, floor[c][tn]))
    json.dump({"floor": floor, "unit": "kWh per year", "rule": "RMS over inputs and dwellings of the SD over repeats; file resolution %.8g",
               "source": "split replicates, Step 3 campaign, %d runs" % len(res)}, io.open("/speed-scratch/o_iseri/5J/freeze/out/floors.json", "w"), indent=1)
    print("FLOORS_WRITTEN /speed-scratch/o_iseri/5J/freeze/out/floors.json")
    print("OPENS %d all in split replicates: %s" % (len(log), all(x[1] in set(ids) for x in log)))


main()
