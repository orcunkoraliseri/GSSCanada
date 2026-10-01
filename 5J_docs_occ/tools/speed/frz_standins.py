# -*- coding: utf-8 -*-
"""5J Step 4, Part D: write the stand-in predictor folders for the VALIDATION split (and the B0 runs) from EnergyPlus. Speed job only.
  good      = EnergyPlus + N(0, (0.10 x run hourly SD)^2) per target, independent noise per target (seed = md5(run_id|good|base))
  weakb1    = EnergyPlus + N(0, (0.30 x run hourly SD)^2)   (the 'B1' reference for the skill score; chosen by the employee, see gates_frozen.md)
  bldmean   = per flat index, the mean of the GOOD predictions over all runs of the same building and climate in the split
              (household effect removed, load level kept)
  trainmean = mean over the DEVELOPMENT split per climate, class, hour of year (out/trainmean.npz)
  shift2    = GOOD shifted by 2 hours (np.roll, wrap-around)
  deleted   = symlink copy of good without one run
'run hourly SD' = standard deviation over all dwelling-hours of the run, per target (ddof=0)."""
import sys, os, io, gzip, hashlib, importlib, multiprocessing as mp
import numpy as np
import pandas as pd
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
sc = importlib.import_module("5thJ_04_scorer")
sl = sc.sl
OUT = "/speed-scratch/o_iseri/5J/freeze/out/standins/"
BASE = 20260930
FRAC = {"good": 0.10, "weakb1": 0.30}
TRAIN = None


def seed(rid, label):
    return int(hashlib.md5(("%s|%s|%d" % (rid, label, BASE)).encode()).hexdigest()[:15], 16)


def write_pred(name, climate, rid, arr, note):
    d = "%s%s/%s/" % (OUT, name, climate)
    os.makedirs(d, exist_ok=True)
    nd = arr.shape[0]
    df = pd.DataFrame({"dwelling": np.repeat(np.arange(nd), sc.H), "hour": np.tile(np.arange(1, sc.H + 1), nd)})
    for i, t in enumerate(sc.TARGETS):
        df[t] = arr[:, :, i].reshape(-1)
    with open(d + rid + ".csv.gz", "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            txt = io.TextIOWrapper(gz, encoding="utf-8", newline="")
            txt.write("# 5J Step 4 stand-in '%s' for run %s: %s\n" % (name, rid, note))
            df.to_csv(txt, index=False, float_format="%.8g")
            txt.flush()
            txt.detach()


def noisy(ep, rid, label):
    sd = ep.reshape(-1, 4).std(0)
    z = np.random.default_rng(seed(rid, label)).standard_normal(ep.shape)
    return ep + FRAC[label] * sd * z


def work(task):
    log = []
    try:
        rs, cl, kind = task["runs"], task["climate"], task["kind"]
        goods = []
        for r in rs:
            ep, st = sc.read_run(sc.TRUTH, cl, r["run_id"], r["nd"], log, "truth")
            if ep is None:
                raise RuntimeError("truth %s %s" % (r["run_id"], st))
            g = noisy(ep, r["run_id"], "good")
            write_pred("good", cl, r["run_id"], g, "EnergyPlus + N(0,(0.10*run hourly SD)^2) per target")
            goods.append(g)
            if kind == "main":
                write_pred("weakb1", cl, r["run_id"], noisy(ep, r["run_id"], "weakb1"), "EnergyPlus + N(0,(0.30*run hourly SD)^2) per target")
                write_pred("shift2", cl, r["run_id"], np.roll(g, 2, axis=1), "good shifted by 2 hours (wrap-around)")
                tm = TRAIN["%s|%s" % (cl, r["cls"])]
                write_pred("trainmean", cl, r["run_id"], np.broadcast_to(tm, g.shape), "development mean per climate, class, hour of year")
        if kind == "main":
            bm = np.mean(goods, axis=0)
            for r in rs:
                write_pred("bldmean", cl, r["run_id"], bm, "mean of the good predictions over the %d runs of this building and climate, per flat" % len(rs))
        return task["key"], None, len(log)
    except Exception:
        return task["key"], sc.short_err(), len(log)


def main():
    global TRAIN
    TRAIN = dict(np.load("/speed-scratch/o_iseri/5J/freeze/out/trainmean.npz"))
    lists = {n: sl.load_split(n) for n in sc.ALLOWED_SPLITS}
    allowed = set().union(*map(set, lists.values()))
    sc._init(allowed)
    runs = sc.load_runs()
    tasks = []
    grp = {}
    for rid in lists["validation"]:
        r = runs[rid]
        grp.setdefault((r["climate"], r["building"]), []).append(r)
    for (cl, b), rs in grp.items():
        tasks.append({"key": "main|%s|%s" % (cl, b), "climate": cl, "runs": rs, "kind": "main"})
    for rid in lists["b0_dev"] + lists["b0_val"]:
        r = runs[rid]
        tasks.append({"key": "b0|" + rid, "climate": r["climate"], "runs": [r], "kind": "b0"})
    tasks.sort(key=lambda t: -len(t["runs"]) * t["runs"][0]["nd"])
    errs, nlog = [], 0
    with mp.Pool(8, initializer=sc._init, initargs=(allowed,)) as p:
        for i, (k, e, nl_) in enumerate(p.imap_unordered(work, tasks, chunksize=1)):
            nlog += nl_
            if e:
                errs.append((k, e))
            if (i + 1) % 50 == 0:
                print("  progress %d/%d" % (i + 1, len(tasks)), flush=True)
    print("STANDINS tasks %d errors %d %s opens %d" % (len(tasks), len(errs), errs[:3], nlog))
    drop = sorted(lists["validation"])[0]
    n = 0
    for rid in lists["validation"] + lists["b0_dev"] + lists["b0_val"]:
        if rid == drop:
            continue
        cl = runs[rid]["climate"]
        d = OUT + "deleted/" + cl + "/"
        os.makedirs(d, exist_ok=True)
        os.symlink(OUT + "good/%s/%s.csv.gz" % (cl, rid), d + rid + ".csv.gz")
        n += 1
    print("DELETED copy: %d symlinks, dropped run %s" % (n, drop))
    for nm in ("good", "weakb1", "bldmean", "trainmean", "shift2", "deleted"):
        print("FOLDER", nm, "climates", sorted(os.listdir(OUT + nm)))


main()
