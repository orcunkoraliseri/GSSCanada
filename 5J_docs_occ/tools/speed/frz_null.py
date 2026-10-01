# -*- coding: utf-8 -*-
"""5J Step 4, Part E (val 3.2): bootstrap null. S and B1 are two INDEPENDENT copies of the good stand-in construction
(EnergyPlus + N(0,(0.10 x run hourly SD)^2) per target), so the true skill R2(S) - R2(B1) is 0. For each of REPS repetitions
(new noise each) and each cell (country x class x target) the 95 % interval of the skill from the scorer's
two_way_cluster_bootstrap is computed; we count the intervals that cover 0. Validation split, truth files only. Speed job only."""
import sys, os, io, math, hashlib, importlib, time, multiprocessing as mp
import numpy as np
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
sc = importlib.import_module("5thJ_04_scorer")
sl = sc.sl
REPS = int(os.environ.get("NULL_REPS", "200"))
BLOCK = 10
FRAC = 0.10


def gseed(key):
    return int(hashlib.md5(("null|%s|%d" % (key, sc.SEED)).encode()).hexdigest()[:15], 16)


def work(task):
    nlog = 0
    try:
        runs, cl, key = task["runs"], task["climate"], task["key"]
        log = []
        EP = []
        for r in runs:
            ep, st = sc.read_run(sc.TRUTH, cl, r["run_id"], r["nd"], log, "truth")
            if ep is None:
                raise RuntimeError("truth %s %s" % (r["run_id"], st))
            EP.append(ep)
        nlog = len(log)
        m, nd = len(runs), runs[0]["nd"]
        sig = np.stack([e.reshape(-1, 4).std(0) for e in EP]) * FRAC        # [m, 4] noise SD per run and target
        ia0, ib0 = np.triu_indices(m, 1)
        rng = np.random.default_rng(gseed(key))
        res = {"sEP": [], "sEP2": [], "sseS": [], "sseB": [], "ha": [], "hb": [], "j": []}
        for j in range(nd):
            toks = np.array([r["tokens"][j] for r in runs])
            keep = toks[ia0] != toks[ib0]
            ia, ib = ia0[keep], ib0[keep]
            if len(ia) == 0:
                continue
            XE = np.stack([e[j] for e in EP])
            XE = XE - XE.mean(0)
            g = sc.gram_pair_sums(XE, XE, ia, ib)
            res["sEP"].append(g["sEP"])
            res["sEP2"].append(g["sEP2"])
            ss = np.zeros((len(ia), 4, REPS), dtype=np.float32)
            sb = np.zeros_like(ss)
            for b0 in range(0, REPS, BLOCK):
                nb = min(BLOCK, REPS - b0)
                for arr in (ss, sb):
                    Z = rng.standard_normal((nb, 4, m, sc.H)) * sig.T[None, :, :, None]     # [nb, 4, m, H]
                    G = Z @ Z.transpose(0, 1, 3, 2)                                          # [nb,4,m,m]
                    d = G[:, :, ia, ia] + G[:, :, ib, ib] - 2 * G[:, :, ia, ib]            # [nb,4,P]
                    arr[:, :, b0:b0 + nb] = d.transpose(2, 1, 0).astype(np.float32)
            res["sseS"].append(ss)
            res["sseB"].append(sb)
            res["ha"].append(toks[ia])
            res["hb"].append(toks[ib])
            res["j"].append(np.full(len(ia), j))
        if not res["j"]:
            return key, task["country"], task["cls"], None, nlog
        out = {k: np.concatenate(v) for k, v in res.items()}
        return key, task["country"], task["cls"], out, nlog
    except Exception:
        return key, None, None, sc.short_err(), nlog


def main():
    t0 = time.time()
    lists = {n: sl.load_split(n) for n in sc.ALLOWED_SPLITS}
    allowed = set().union(*map(set, lists.values()))
    sc._init(allowed)
    runs = sc.load_runs()
    tasks = sc.make_tasks(runs, lists["validation"], [], [], False)
    res, errs, nlog = [], [], 0
    with mp.Pool(int(os.environ.get("NULL_WORKERS", "8")), initializer=sc._init, initargs=(allowed,)) as p:
        for i, (key, c, k, out, nl_) in enumerate(p.imap_unordered(work, tasks, chunksize=1)):
            nlog += nl_
            if c is None:
                errs.append((key, out))
            elif out is not None:
                res.append((key, c, k, out))
            if (i + 1) % 20 == 0:
                print("  progress %d/%d %.0fs" % (i + 1, len(tasks), time.time() - t0), flush=True)
    print("NULL groups %d errors %d %s opens %d reps %d" % (len(tasks), len(errs), errs[:3], nlog, REPS))
    cov_all, rows = [], []
    for ci, c in enumerate(sc.COUNTRIES):
        for ki, k in enumerate(sc.CLASSES):
            rs = [r for r in res if r[1] == c and r[2] == k]
            if not rs:
                continue
            bc = np.concatenate([np.full(len(r[3]["j"]), r[0].split("|", 1)[1]) for r in rs])
            ha = np.concatenate([r[3]["ha"] for r in rs])
            hb = np.concatenate([r[3]["hb"] for r in rs])
            sEP = np.concatenate([r[3]["sEP"] for r in rs])
            sEP2 = np.concatenate([r[3]["sEP2"] for r in rs])
            sS = np.concatenate([r[3]["sseS"] for r in rs])
            sB = np.concatenate([r[3]["sseB"] for r in rs])
            W = sc.two_way_cluster_bootstrap(bc, ha, hb, sc.NBOOT, sc.SEED + 1000 * ci + 100 * ki)
            sw = W.sum(1)
            for t in range(4):
                a_, b_ = W @ sEP[:, t], W @ sEP2[:, t]
                with np.errstate(divide="ignore", invalid="ignore"):
                    sst = b_ - a_ * a_ / (sc.H * sw)
                    cS, cB = W @ sS[:, t, :].astype(np.float64), W @ sB[:, t, :].astype(np.float64)
                    skill = (cB - cS) / sst[:, None]
                    skill[~((sw > 0) & (sst > 0))] = np.nan
                lo, hi = np.nanpercentile(skill, 2.5, axis=0), np.nanpercentile(skill, 97.5, axis=0)
                sstp = sEP2[:, t].sum() - sEP[:, t].sum() ** 2 / (sc.H * len(sEP))
                pt = (sB[:, t, :].sum(0) - sS[:, t, :].sum(0)) / sstp
                cover = (lo <= 0) & (hi >= 0)
                cov_all.append(cover)
                rows.append((c, k, sc.TNAME[t], float(cover.mean())))
                print("NULLCELL country=%s class=%s target=%s coverage=%.1f%% reps=%d pairs=%d mean_point_skill=%.5f sd_point_skill_over_reps=%.5f mean_ci_width=%.5f" %
                      (c, k, sc.TNAME[t], 100 * cover.mean(), REPS, len(sEP), pt.mean(), pt.std(ddof=1), np.mean(hi - lo)), flush=True)
    allc = np.concatenate(cov_all)
    n93 = sum(1 for r in rows if r[3] < 0.93)
    print("NULL_POOLED coverage=%.2f%% over %d cells x %d reps = %d intervals; cells below 93%%: %d of %d; min cell coverage %.1f%%" %
          (100 * allc.mean(), len(rows), REPS, len(allc), n93, len(rows), 100 * min(r[3] for r in rows)))
    print("GATE 3.2 bootstrap null: intervals covering 0 >= 93%% -> %s" % ("PASS" if allc.mean() >= 0.93 else "FAIL"))
    print("seconds %.0f" % (time.time() - t0))


main()
