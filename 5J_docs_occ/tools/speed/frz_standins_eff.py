# -*- coding: utf-8 -*-
"""5J Step 4 fix 1: the EFFECT-GOOD stand-in (effgood) and the rows rebuilt on it. Speed job only. Ruled by the manager 2026-09-30 (R2, R3).

DEFINITION of effgood (validation groups = climate x building; flat index j; m = number of runs of the group):
  per target and hour:  mu_j = mean over the m runs of EP_r[j];   D_r,j = EP_r[j] - mu_j
  effgood_r[j] = EP_r[j] + 0.10 * SD_h(mu_j) * z_shared + 0.10 * SD_h(D_r,j) * z_r
  SD_h = standard deviation over the 8,760 hours of that flat (ddof=0), per target.
  z_shared ~ N(0,1), the SAME for every run of the flat (per hour and target);
           seed = int(md5("<climate>|<building>|<j>|effgood_shared|20260930").hexdigest()[:15], 16)
  z_r ~ N(0,1) per run and flat; seed = int(md5("<run_id>|<j>|effgood|20260930").hexdigest()[:15], 16)
  The shared part is the error a surrogate makes on the flat's load level (it cancels inside a pair); the run part is 10 % of the
  occupancy deviation. m = 1: D = 0, so only the shared part. B0 runs (b0_dev, b0_val): only the shared part with mu = EP of that run.
Rows on effgood:
  effbldmean = per flat, the mean of effgood over the m runs of the group (occupancy effect exactly zero)
  effshift2  = effgood rolled by 2 h (wrap-around)
  effdeleted = symlinks to effgood minus the first validation run in sorted order (validation + b0_dev + b0_val)
Output layout: out/standins/<name>/<climate>/<run_id>.csv.gz, written like frz_standins.write_pred ('%.8g')."""
import sys, os, io, gzip, hashlib, importlib, multiprocessing as mp
import numpy as np
import pandas as pd
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
sc = importlib.import_module("5thJ_04_scorer")
sl = sc.sl
OUT = "/speed-scratch/o_iseri/5J/freeze/out/standins/"
BASE = 20260930
FRAC = 0.10
NAMES = ("effgood", "effbldmean", "effshift2", "effdeleted")


def md5seed(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:15], 16)


def write_pred(name, climate, rid, arr, note):
    d = "%s%s/%s/" % (OUT, name, climate)
    os.makedirs(d, exist_ok=True)
    p = d + rid + ".csv.gz"
    if os.path.exists(p):
        raise FileExistsError("additive only, exists: " + p)
    nd = arr.shape[0]
    df = pd.DataFrame({"dwelling": np.repeat(np.arange(nd), sc.H), "hour": np.tile(np.arange(1, sc.H + 1), nd)})
    for i, t in enumerate(sc.TARGETS):
        df[t] = arr[:, :, i].reshape(-1)
    with open(p, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            txt = io.TextIOWrapper(gz, encoding="utf-8", newline="")
            txt.write("# 5J Step 4 fix 1 stand-in '%s' for run %s: %s\n" % (name, rid, note))
            df.to_csv(txt, index=False, float_format="%.8g")
            txt.flush()
            txt.detach()


def shared_noise(cl, b, nd, mu):
    """0.10 * SD_h(mu_j) * z_shared, array [nd, H, 4]; also returns the z-free scale for reporting."""
    out = np.empty_like(mu)
    for j in range(mu.shape[0]):
        z = np.random.default_rng(md5seed("%s|%s|%d|effgood_shared|%d" % (cl, b, j, BASE))).standard_normal((sc.H, 4))
        out[j] = FRAC * mu[j].std(0) * z
    return out


def work(task):
    log, rep = [], None
    try:
        rs, cl, kind, b = task["runs"], task["climate"], task["kind"], task["building"]
        eps = []
        for r in rs:
            ep, st = sc.read_run(sc.TRUTH, cl, r["run_id"], r["nd"], log, "truth")
            if ep is None:
                raise RuntimeError("truth %s %s" % (r["run_id"], st))
            eps.append(ep)
        E = np.stack(eps)                       # [m, nd, H, 4]
        mu = E.mean(0)
        sh = shared_noise(cl, b, E.shape[1], mu)
        D = E - mu
        eff = []
        for i, r in enumerate(rs):
            runpart = np.empty_like(mu)
            for j in range(mu.shape[0]):
                z = np.random.default_rng(md5seed("%s|%d|effgood|%d" % (r["run_id"], j, BASE))).standard_normal((sc.H, 4))
                runpart[j] = FRAC * D[i, j].std(0) * z
            g = E[i] + sh + runpart
            eff.append(g)
            write_pred("effgood", cl, r["run_id"], g, "EnergyPlus + 0.10*SD_h(mu_j)*z_shared + 0.10*SD_h(D_rj)*z_r per flat and target (see frz_standins_eff.py)")
            if i < 3 and len(rs) >= 2 and task.get("report"):
                rp = runpart
                sdD = D[i].std(1)               # [nd, 4]
                sdM = mu.std(1)
                tot = (g - E[i]).std(1)
                rep = rep or []
                rep.append("REPORT run %s (group %s %s, m=%d, flats %d): median over flats, per target [heating cooling equipment total]: "
                           "SD(run part)/SD(D)=%s  SD(shared part)/SD(mu)=%s  SD(effgood-EP)/SD(D)=%s" % (
                               r["run_id"], cl, b, len(rs), mu.shape[0],
                               np.round(np.median(rp.std(1) / np.where(sdD > 0, sdD, np.nan), axis=0), 4).tolist(),
                               np.round(np.median(sh.std(1) / np.where(sdM > 0, sdM, np.nan), axis=0), 4).tolist(),
                               np.round(np.median(tot / np.where(sdD > 0, sdD, np.nan), axis=0), 4).tolist()))
        if kind == "main":
            bm = np.mean(eff, axis=0)
            for i, r in enumerate(rs):
                write_pred("effbldmean", cl, r["run_id"], bm, "mean of effgood over the %d runs of this building and climate, per flat" % len(rs))
                write_pred("effshift2", cl, r["run_id"], np.roll(eff[i], 2, axis=1), "effgood shifted by 2 hours (wrap-around)")
        return task["key"], None, len(log), rep
    except Exception:
        return task["key"], sc.short_err(), len(log), rep


def main():
    lists = {n: sl.load_split(n) for n in sc.ALLOWED_SPLITS}
    allowed = set().union(*map(set, lists.values()))
    sc._init(allowed)
    runs = sc.load_runs()
    tasks, grp = [], {}
    for rid in lists["validation"]:
        r = runs[rid]
        grp.setdefault((r["climate"], r["building"]), []).append(r)
    for (cl, b), rs in grp.items():
        tasks.append({"key": "main|%s|%s" % (cl, b), "climate": cl, "building": b, "runs": rs, "kind": "main"})
    for rid in lists["b0_dev"] + lists["b0_val"]:
        r = runs[rid]
        tasks.append({"key": "b0|" + rid, "climate": r["climate"], "building": r["building"], "runs": [r], "kind": "b0"})
    rep_key = sorted(t["key"] for t in tasks if t["kind"] == "main" and len(t["runs"]) >= 2 and t["runs"][0]["nd"] >= 2)[0]
    for t in tasks:
        t["report"] = (t["key"] == rep_key)
    tasks.sort(key=lambda t: -len(t["runs"]) * t["runs"][0]["nd"])
    errs, nlog = [], 0
    with mp.Pool(8, initializer=sc._init, initargs=(allowed,)) as p:
        for i, (k, e, nl_, rep) in enumerate(p.imap_unordered(work, tasks, chunksize=1)):
            nlog += nl_
            if e:
                errs.append((k, e))
            if rep:
                for ln in rep:
                    print(ln, flush=True)
            if (i + 1) % 50 == 0:
                print("  progress %d/%d" % (i + 1, len(tasks)), flush=True)
    print("STANDINS_EFF tasks %d errors %d %s opens %d report_group %s" % (len(tasks), len(errs), errs[:3], nlog, rep_key))
    if errs:
        sys.exit(4)
    drop = sorted(lists["validation"])[0]
    n = 0
    for rid in lists["validation"] + lists["b0_dev"] + lists["b0_val"]:
        if rid == drop:
            continue
        cl = runs[rid]["climate"]
        d = OUT + "effdeleted/" + cl + "/"
        os.makedirs(d, exist_ok=True)
        os.symlink(OUT + "effgood/%s/%s.csv.gz" % (cl, rid), d + rid + ".csv.gz")
        n += 1
    print("EFFDELETED copy: %d symlinks, dropped run %s" % (n, drop))
    for nm in NAMES:
        cnt = {cl: len(os.listdir(OUT + nm + "/" + cl)) for cl in sorted(os.listdir(OUT + nm))}
        print("FOLDER", nm, "climates", len(cnt), "files", sum(cnt.values()))
    print("EXPECTED files: effgood/effdeleted-related: validation %d + b0 %d" % (len(lists["validation"]), len(lists["b0_dev"]) + len(lists["b0_val"])))


main()
