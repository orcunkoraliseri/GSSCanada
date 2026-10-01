# -*- coding: utf-8 -*-
"""5J Step 4 scorer (Speed job only; Spain + Italy only, never a UK file, never a test run).

Usage:  5thJ_04_scorer.py --pred DIR --split validation --out DIR --tag NAME [--b1 DIR] [--control DIR]
            [--floors floors.json] [--k 2] [--nboot 2000] [--workers N] [--secondary] [--plant crash] [--selftest 20]
        5thJ_04_scorer.py --mode sources --sources gates_frozen.md        (gates 1.1 and 1.2 only)

DIR = a predictions folder laid out like the campaign extracted/ folder: <climate_id>/<run_id>.csv.gz with columns
dwelling, hour, heating_kwh, cooling_kwh, equipment_kwh, total_elec_kwh (8,760 rows per dwelling).
Truth (EnergyPlus) is always /speed-scratch/o_iseri/5J/campaign/extracted/ (read only).

EXIT CODE MEANING (spec 4C):  0 = every gate computed (PASS or FAIL, nothing NOT_EVALUABLE);
  2 = at least one gate line NOT_EVALUABLE (and no crash);   1 = the scorer crashed somewhere (a crashed section is
  NOT_EVALUABLE in the SUMMARY too, so a crash shows both: NOT_EVALUABLE>0 in the SUMMARY and exit 1). 1 wins over 2.
A gate FAIL does not change the exit code: the verdict is in the lines and in SUMMARY FAIL=.

NO TEST DATA: every file open goes through read_run / read_direct, which refuse a run id that is not in one of
development, validation, b0_dev, b0_val, replicates (lists read through split_loader.load_split only) and which log
every open (kind, run id, path) to <out>/openlog_<tag>.tsv. Gate 2.3 counts opens of ids outside those lists.

Definitions (details and sources in outputs_step4/gates_frozen.md):
  pair  = two households A,B in the SAME flat index of the same building and climate, in two different runs of the
          same split (hid A != hid B); every such pair is used.
  G5J.1 every run of the split has a prediction file with 8,760 finite rows per dwelling (per class and country).
  G5J.2 per run and target hourly CV(RMSE), NMBE over all dwelling-hours of the run; cell passes when the median run
        has CV(RMSE) <= 30 % and median |NMBE| <= 10 %.
  G5J.3 R2 of dS against dEP over the hours of all pairs, sign agreement over pairs above the noise floor, skill over
        B1 = R2(S) - R2(B1) with the two-way cluster bootstrap 95 % interval.
  G5J.4 control C (occupancy blind) must FAIL G5J.3.
  G5J.5 daily peak hour of total electricity within +-1 h (circular, 24 h) on >= 70 % of dwelling-days.
"""
import argparse, csv, hashlib, io, itertools, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np
import pandas as pd

FRZ = "/speed-scratch/o_iseri/5J/freeze/"
CAMP = "/speed-scratch/o_iseri/5J/campaign/"
TRUTH = CAMP + "extracted/"
sys.path.insert(0, FRZ)
import split_loader as sl

TARGETS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
TNAME = ["heating", "cooling", "equipment", "total_elec"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
COUNTRIES = ["es", "it"]
ALLOWED_SPLITS = ("development", "validation", "b0_dev", "b0_val", "replicates")
TEST_SPLITS = ("test_new_households", "test_new_buildings", "test_both_new")      # AMENDMENT 1 (--test only)
ALLOWED_SPLITS_TEST = TEST_SPLITS + ("b0_test", "b0_dev")                         # AMENDMENT 1 (--test only)
GATE_LOCK = "/speed-scratch/o_iseri/5J/gates_frozen.md5"
H = 8760
BAND_CV, BAND_NMBE = 0.30, 0.10          # G5J.2 (ASHRAE Guideline 14-2002 clause 5.3.2.4 f, p. 18; a reference)
R2_MIN, SIGN_MIN, PEAK_MIN = 0.5, 0.80, 0.70
MIN_PAIRS, K_DEFAULT, RES_KWH = 30, 2.0, 1e-3
NBOOT, SEED = 2000, 20260930

ALLOWED = set()


def _init(allowed):
    global ALLOWED
    ALLOWED = allowed


def short_err():
    return traceback.format_exc().strip().splitlines()[-1][:200]


# ----------------------------------------------------------------------------------------------- run tables
def load_runs():
    rows = {}
    for cc in COUNTRIES:
        for r in csv.DictReader(io.open(CAMP + "in/campaign_runs_%s.csv" % cc, encoding="utf-8")):
            assert r["country"] == cc and r["run_id"].startswith(cc + "_")
            toks = dict(x.split(":", 1) for x in r["placement"].split(";"))
            nd = int(r["n_dwellings"])
            rows[r["run_id"]] = {"run_id": r["run_id"], "country": cc, "climate": r["climate_id"], "building": r["building_id"],
                                 "cls": r["class"], "nd": nd, "pool": r["pool"], "replicate": int(r["replicate"]),
                                 "tokens": [toks[str(j)] for j in range(nd)]}
    return rows


# ----------------------------------------------------------------------------------------------- readers (every open is logged)
def read_run(root, climate, rid, nd, log, kind):
    """Returns (array [nd, 8760, 4] float64, 'ok') or (None, reason). Refuses a run id outside the allowed lists."""
    if rid not in ALLOWED:
        raise PermissionError("REFUSED: run %s is not in an allowed split list" % rid)
    p = "%s%s/%s.csv.gz" % (root, climate, rid)
    log.append((kind, rid, p))
    if not os.path.exists(p):
        return None, "missing"
    try:
        df = pd.read_csv(p, comment="#", compression="gzip", usecols=["dwelling", "hour"] + TARGETS)
    except Exception:
        return None, "unreadable: " + short_err()
    if len(df) != nd * H:
        return None, "rows %d != %d" % (len(df), nd * H)
    df = df.sort_values(["dwelling", "hour"], kind="stable")
    if not (np.array_equal(df["dwelling"].to_numpy(), np.repeat(np.arange(nd), H)) and
            np.array_equal(df["hour"].to_numpy(), np.tile(np.arange(1, H + 1), nd))):
        return None, "dwelling or hour index wrong"
    arr = df[TARGETS].to_numpy(dtype=float).reshape(nd, H, 4)
    if not np.isfinite(arr).all():
        return None, "non-finite values"
    return arr, "ok"


def read_direct(root, climate, rid, j, tgt, log, kind):
    """Independent (slow) reader for the self-test: one dwelling, one target, filtered by dwelling and sorted by hour."""
    if rid not in ALLOWED:
        raise PermissionError("REFUSED: run %s is not in an allowed split list" % rid)
    p = "%s%s/%s.csv.gz" % (root, climate, rid)
    log.append((kind, rid, p))
    df = pd.read_csv(p, comment="#")
    sub = df[df["dwelling"] == j].sort_values("hour")
    assert len(sub) == H
    return sub[tgt].to_numpy(dtype=float)


# ----------------------------------------------------------------------------------------------- statistics from sums
def r2_from_sums(sEP, sEP2, sse, n=H):
    """R2 = 1 - SSE/SST over all hours of the pairs given. Inputs are per-pair sums (arrays or scalars):
       sEP = sum_t dEP, sEP2 = sum_t dEP^2, sse = sum_t (dEP - dS)^2, n = hours per pair (8,760).
       SST = sum sEP2 - (sum sEP)^2 / (n * number_of_pairs).  Returns nan when SST <= 0."""
    sEP, sEP2, sse = np.atleast_1d(sEP), np.atleast_1d(sEP2), np.atleast_1d(sse)
    N = n * len(sEP)
    sst = sEP2.sum() - sEP.sum() ** 2 / N
    return float(1.0 - sse.sum() / sst) if sst > 0 else float("nan")


def gram_pair_sums(XE, XP, ia, ib):
    """XE, XP: [m, 8760, 4] (same common offset removed from both; differences are unchanged by it).
       Returns dict of [P, 4] arrays for the pairs (ia[k], ib[k]): sEP, sEP2, sP, sP2, sEPP, sse."""
    E = np.ascontiguousarray(XE.transpose(2, 0, 1))
    Pm = np.ascontiguousarray(XP.transpose(2, 0, 1))
    Z = Pm - E
    GEE, GPP, GEP, GZZ = E @ E.transpose(0, 2, 1), Pm @ Pm.transpose(0, 2, 1), E @ Pm.transpose(0, 2, 1), Z @ Z.transpose(0, 2, 1)

    def dsq(G):
        return (G[:, ia, ia] + G[:, ib, ib] - 2 * G[:, ia, ib]).T

    cE, cP = E.sum(2), Pm.sum(2)                     # [4, m]
    return {"sEP": (cE[:, ia] - cE[:, ib]).T, "sEP2": dsq(GEE), "sP": (cP[:, ia] - cP[:, ib]).T, "sP2": dsq(GPP),
            "sEPP": (GEP[:, ia, ia] - GEP[:, ia, ib] - GEP[:, ib, ia] + GEP[:, ib, ib]).T, "sse": dsq(GZZ)}


# ----------------------------------------------------------------------------------------------- bootstrap
def two_way_cluster_bootstrap(bcode, ha, hb, nboot, seed):
    """Two-way cluster bootstrap weights. Resampling units: BUILDINGS (unique values of bcode) and HOUSEHOLDS (unique
    household ids over ha and hb), each drawn with replacement, INDEPENDENTLY of each other (never hours, never runs).
    A pair keeps weight m_building * m_household(A) * m_household(B): it is kept only when its building AND both its
    households were drawn (weight 0 otherwise), drawn more than once it counts more than once.
    Returns W [nboot, P] float64."""
    rng = np.random.default_rng(seed)
    ub, uh = np.unique(bcode), np.unique(np.concatenate([ha, hb]))
    bi, ai, ci = np.searchsorted(ub, bcode), np.searchsorted(uh, ha), np.searchsorted(uh, hb)
    Mb = np.zeros((nboot, len(ub)))
    Mh = np.zeros((nboot, len(uh)))
    for r in range(nboot):
        Mb[r] = np.bincount(rng.integers(0, len(ub), len(ub)), minlength=len(ub))   # buildings resampled
        Mh[r] = np.bincount(rng.integers(0, len(uh), len(uh)), minlength=len(uh))   # households resampled, independent draw
    return Mb[:, bi] * Mh[:, ai] * Mh[:, ci]


def boot_r2(W, sEP, sEP2, sse):
    """R2 for each resample: weights W [nboot,P]. Returns [nboot] (nan where the resample holds no pair)."""
    sw = W.sum(1)
    a, b, c = W @ sEP, W @ sEP2, W @ sse
    with np.errstate(divide="ignore", invalid="ignore"):
        sst = b - a * a / (H * sw)
        return np.where((sw > 0) & (sst > 0), 1.0 - c / sst, np.nan)


def ci95(x):
    x = x[np.isfinite(x)]
    return (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))) if len(x) > 50 else (float("nan"), float("nan"))


# ----------------------------------------------------------------------------------------------- per-group worker
def process_group(task):
    log = []
    try:
        out = _process_group(task, log)
    except Exception:
        out = {"error": short_err()}
    out["key"] = task["key"]
    out["openlog"] = log
    return out


def _process_group(task, log):
    runs, cl, preds = task["runs"], task["climate"], task["preds"]
    out = {"country": task["country"], "cls": task["cls"], "g1": [], "g2": [], "g5": [], "sec": None, "pairs": None}
    EP, PR = {}, {nm: {} for nm, _ in preds}
    for r in runs:
        rid = r["run_id"]
        ep, st = read_run(TRUTH, cl, rid, r["nd"], log, "truth")
        if st != "ok":
            raise RuntimeError("truth unreadable %s: %s" % (rid, st))
        EP[rid] = ep
        for nm, root in preds:
            arr, st = read_run(root, cl, rid, r["nd"], log, "pred_" + nm)
            if nm == "S":
                out["g1"].append((rid, st))
            elif arr is None and PR["S"].get(rid) is not None:
                raise RuntimeError("%s prediction unusable for %s: %s" % (nm, rid, st))
            PR[nm][rid] = arr
    U = [r for r in runs if PR["S"][r["run_id"]] is not None]
    for r in U:
        rid, nd = r["run_id"], r["nd"]
        ep, s = EP[rid].reshape(-1, 4), PR["S"][rid].reshape(-1, 4)
        e = s - ep
        mean, sm = ep.mean(0), ep.sum(0)
        rmse = np.sqrt((e ** 2).mean(0))
        cv = np.where(mean > 0, rmse / np.where(mean > 0, mean, 1.0), np.nan)
        nmbe = np.where(sm > 0, e.sum(0) / np.where(sm > 0, sm, 1.0), np.nan)
        out["g2"].append((rid, cv, nmbe))
        pe = EP[rid][:, :, 3].reshape(nd, 365, 24).argmax(2)
        ps = PR["S"][rid][:, :, 3].reshape(nd, 365, 24).argmax(2)
        d = np.abs(pe - ps)
        d = np.minimum(d, 24 - d)
        out["g5"].append((rid, int((d <= 1).sum()), int(d.size)))
    # pairs: same flat index, two different runs, different households
    if len(U) >= 2:
        nd = U[0]["nd"]
        m = len(U)
        ia0, ib0 = np.triu_indices(m, 1)
        acc = {}
        jl, ral, rbl, hal, hbl = [], [], [], [], []
        for j in range(nd):
            toks = np.array([r["tokens"][j] for r in U])
            keep = toks[ia0] != toks[ib0]
            ia, ib = ia0[keep], ib0[keep]
            if len(ia) == 0:
                continue
            XE = np.stack([EP[r["run_id"]][j] for r in U])
            mu = XE.mean(0)
            XE = XE - mu
            for nm, _ in preds:
                XP = np.stack([PR[nm][r["run_id"]][j] for r in U]) - mu
                g = gram_pair_sums(XE, XP, ia, ib)
                if nm == "S":
                    acc.setdefault("sEP", []).append(g["sEP"])
                    acc.setdefault("sEP2", []).append(g["sEP2"])
                for kk in ("sP", "sP2", "sEPP", "sse"):
                    acc.setdefault(nm + "_" + kk, []).append(g[kk])
            jl.append(np.full(len(ia), j)); ral.append(ia); rbl.append(ib)
            hal.append(toks[ia]); hbl.append(toks[ib])
        if jl:
            out["pairs"] = {"stats": {k: np.concatenate(v) for k, v in acc.items()}, "j": np.concatenate(jl),
                            "ra": np.array([U[i]["run_id"] for i in np.concatenate(ral)]),
                            "rb": np.array([U[i]["run_id"] for i in np.concatenate(rbl)]),
                            "ha": np.concatenate(hal), "hb": np.concatenate(hbl)}
    # secondary: each flat against the same flat of its B0 run (average household), reported not gated
    b0 = task.get("b0")
    if b0 is not None:
        e0, st0 = read_run(TRUTH, cl, b0["run_id"], b0["nd"], log, "truth_b0")
        s0, st1 = read_run(preds[0][1], cl, b0["run_id"], b0["nd"], log, "pred_S_b0")
        if e0 is not None and s0 is not None:
            sec = np.zeros((4, 4))
            for r in U:
                DE = EP[r["run_id"]] - e0
                DS = PR["S"][r["run_id"]] - s0
                sec += np.stack([np.full(4, DE.shape[0] * H), DE.sum((0, 1)), (DE ** 2).sum((0, 1)), ((DS - DE) ** 2).sum((0, 1))], 1).T
            out["sec"] = sec
    return out


def make_tasks(runs, split_ids, b0_ids, preds, want_b0):
    """One task per (climate, building) group of the main runs (no replicate, no B0) of the split."""
    grp = {}
    for rid in sorted(split_ids):
        r = runs[rid]
        assert r["replicate"] == 0 and r["pool"] != "b0", ("not a main run", rid)
        grp.setdefault((r["climate"], r["building"]), []).append(r)
    b0 = {}
    for rid in b0_ids:
        r = runs[rid]
        b0[(r["climate"], r["building"])] = r
    tasks = []
    for (cl, b), rs in grp.items():
        tasks.append({"key": "%s|%s" % (cl, b), "climate": cl, "country": rs[0]["country"], "cls": rs[0]["cls"], "runs": rs,
                      "preds": preds, "b0": b0.get((cl, b)) if want_b0 else None})
    tasks.sort(key=lambda t: -len(t["runs"]) * t["runs"][0]["nd"])
    return tasks


# ----------------------------------------------------------------------------------------------- gate 3 cell
def g3_cell(st, pref, thr, W, nb_units):
    """st = pair arrays for one cell and one target; pref = 'S' or 'C'. Returns dict."""
    sEP, sEP2 = st["sEP"], st["sEP2"]
    P = len(sEP)
    above = np.abs(sEP) > thr
    r2 = r2_from_sums(sEP, sEP2, st[pref + "_sse"])
    r2b = r2_from_sums(sEP, sEP2, st["B1_sse"])
    sign = float((np.sign(st[pref + "_sP"][above]) == np.sign(sEP[above])).mean()) if above.any() else float("nan")
    bs = boot_r2(W, sEP, sEP2, st[pref + "_sse"]) - boot_r2(W, sEP, sEP2, st["B1_sse"])
    lo, hi = ci95(bs)
    res = {"pairs": P, "above": int(above.sum()), "r2": r2, "r2_b1": r2b, "sign": sign, "skill": r2 - r2b, "lo": lo, "hi": hi,
           "n_b": nb_units[0], "n_h": nb_units[1]}
    if int(above.sum()) < MIN_PAIRS or not np.isfinite(r2):
        res["verdict"] = "NOT_EVALUABLE"
    elif not np.isfinite(lo):
        res["verdict"] = "NOT_EVALUABLE"
    else:
        res["verdict"] = "PASS" if (r2 >= R2_MIN and sign >= SIGN_MIN and lo > 0) else "FAIL"
    return res


# ----------------------------------------------------------------------------------------------- main
class Out:
    def __init__(self):
        self.lines = []
        self.verdicts = []          # (gate, verdict)
        self.crashed = False

    def gate(self, gate, country, cls, target, verdict, text=""):
        self.verdicts.append((gate, verdict))
        ln = "GATE %s country=%s class=%s target=%s VERDICT=%s %s" % (gate, country, cls, target, verdict, text)
        self.lines.append(ln)
        print(ln, flush=True)

    def info(self, s):
        self.lines.append(s)
        print(s, flush=True)


def section(out, name, fn):
    """Run a section; a crash prints one NOT_EVALUABLE line for the whole section and marks the scorer as crashed."""
    try:
        fn()
    except Exception:
        out.crashed = True
        out.gate(name, "ALL", "ALL", "ALL", "NOT_EVALUABLE", "SECTION_CRASHED: " + short_err())


def sources_check(path):
    txt = io.open(path, encoding="utf-8").read().splitlines()
    pending = [l for l in txt if "SOURCE PAGE PENDING" in l]
    print("GATE 1.1 ASHRAE Guideline 14 band: source opened, page cited in gates_frozen.md: %s" %
          ("FAIL (marker 'SOURCE PAGE PENDING (author)' still in the file: %d line(s); expected until the author gives the page)" % len(pending)
           if pending else "PASS"))
    th = [l for l in txt if l.startswith("THRESHOLD ")]
    bad = [l for l in th if "| source:" not in l]
    print("GATE 1.2 every numeric threshold names its source or who chose it on which date: %s (%d THRESHOLD lines, %d without source)" %
          ("PASS" if th and not bad else "FAIL", len(th), len(bad)))
    for l in bad:
        print("  missing source:", l[:120])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="score")
    ap.add_argument("--sources")
    ap.add_argument("--pred"); ap.add_argument("--b1"); ap.add_argument("--control")
    ap.add_argument("--split", default="validation")
    ap.add_argument("--out", default=FRZ + "out/"); ap.add_argument("--tag", default="run")
    ap.add_argument("--floors", default=FRZ + "out/floors.json")
    ap.add_argument("--k", type=float, default=K_DEFAULT)
    ap.add_argument("--nboot", type=int, default=NBOOT)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--secondary", action="store_true")
    ap.add_argument("--plant", default="none")
    ap.add_argument("--selftest", type=int, default=0)
    ap.add_argument("--test", action="store_true")                                  # AMENDMENT 1
    a = ap.parse_args()
    if a.mode == "sources":
        sources_check(a.sources)
        return 0
    if a.test:                                                                       # AMENDMENT 1
        assert os.path.exists(GATE_LOCK), "REFUSED: --test needs %s (the gates are not frozen)" % GATE_LOCK
        assert a.split in TEST_SPLITS, "--test scores one of the three test lists only"
    else:
        assert a.split in ("development", "validation"), "scorer runs on development or validation only"
    t0 = time.time()
    O = Out()
    O.info("SCORER start %s tag=%s split=%s pred=%s b1=%s control=%s k=%s nboot=%d workers=%d" % (time.strftime("%Y-%m-%dT%H:%M:%S"), a.tag, a.split, a.pred, a.b1, a.control, a.k, a.nboot, a.workers))
    os.makedirs(a.out, exist_ok=True)
    allowed = set()
    lists = {}
    for nm in (ALLOWED_SPLITS_TEST if a.test else ALLOWED_SPLITS):                   # AMENDMENT 1
        lists[nm] = sl.load_split(nm)
        allowed |= set(lists[nm])
    runs = load_runs()
    split_ids = lists[a.split]
    b0_ids = lists["b0_dev"] + (lists["b0_test"] if a.test else lists["b0_val"])    # AMENDMENT 1
    floors = json.load(io.open(a.floors, encoding="utf-8"))["floor"] if os.path.exists(a.floors) else None
    if floors is None:
        O.info("WARNING no floors file %s: floor taken as 0 for every class and target" % a.floors)
        floors = {c: {t: 0.0 for t in TNAME} for c in CLASSES}
    preds = [("S", a.pred + "/")]
    if a.b1:
        preds.append(("B1", a.b1 + "/"))
    if a.control:
        preds.append(("C", a.control + "/"))
    _init(allowed)
    tasks = make_tasks(runs, split_ids, b0_ids, preds, a.secondary)
    O.info("TASKS %d groups, %d runs of split %s" % (len(tasks), len(split_ids), a.split))
    results, errs = [], []
    with mp.Pool(a.workers, initializer=_init, initargs=(allowed,)) as pool:
        for i, r in enumerate(pool.imap_unordered(process_group, tasks, chunksize=1)):
            (errs if r.get("error") else results).append(r)
            if (i + 1) % 40 == 0:
                print("  progress %d/%d groups %.0fs" % (i + 1, len(tasks), time.time() - t0), flush=True)
    if errs:
        O.crashed = True
        for e in errs[:5]:
            O.info("GROUP_ERROR %s: %s" % (e["key"], e["error"]))
            O.gate("GROUPS", e["key"], "ALL", "ALL", "NOT_EVALUABLE", "group crashed: " + e["error"][:80])
    openlog = [x for r in results + errs for x in r["openlog"]]
    with io.open(a.out + "openlog_%s.tsv" % a.tag, "w", encoding="utf-8") as fh:
        fh.write("kind\trun_id\tpath\n")
        for k, rid, p in openlog:
            fh.write("%s\t%s\t%s\n" % (k, rid, p))
    cells = [(c, k) for c in COUNTRIES for k in CLASSES]

    def cell_runs(c, k):
        return [r for r in results if r["country"] == c and r["cls"] == k]

    # ---- pair counts
    cellpairs = {}
    for c, k in cells:
        rs = cell_runs(c, k)
        nruns = sum(len(r["g1"]) for r in rs)
        npair = sum(len(r["pairs"]["j"]) for r in rs if r["pairs"])
        O.info("PAIRS country=%s class=%s runs=%d groups=%d pairs=%d" % (c, k, nruns, len(rs), npair))
        cellpairs[(c, k)] = npair
    O.info("PAIRS_TOTAL %d" % sum(cellpairs.values()))

    # ---- G5J.1
    def s_g1():
        for c, k in cells:
            g1 = [x for r in cell_runs(c, k) for x in r["g1"]]
            bad = [x for x in g1 if x[1] != "ok"]
            if not g1:
                O.gate("G5J.1", c, k, "ALL", "NOT_EVALUABLE", "no runs")
            else:
                O.gate("G5J.1", c, k, "ALL", "FAIL" if bad else "PASS",
                       "runs=%d ok=%d bad=%d %s" % (len(g1), len(g1) - len(bad), len(bad), "; ".join("%s:%s" % (x[0], x[1]) for x in bad[:3])))
    section(O, "G5J.1", s_g1)

    # ---- G5J.2
    def s_g2():
        for c, k in cells:
            g2 = [x for r in cell_runs(c, k) for x in r["g2"]]
            for t in range(4):
                cv = np.array([x[1][t] for x in g2]); nm = np.array([x[2][t] for x in g2])
                ok = np.isfinite(cv) & np.isfinite(nm)
                if ok.sum() == 0:
                    O.gate("G5J.2", c, k, TNAME[t], "NOT_EVALUABLE", "no run with a nonzero mean"); continue
                mcv, mnm = float(np.median(cv[ok])), float(np.median(np.abs(nm[ok])))
                share = float(((cv[ok] <= BAND_CV) & (np.abs(nm[ok]) <= BAND_NMBE)).mean())
                O.gate("G5J.2", c, k, TNAME[t], "PASS" if (mcv <= BAND_CV and mnm <= BAND_NMBE) else "FAIL",
                       "median_cvrmse=%.1f%% median_abs_nmbe=%.2f%% share_runs_in_band=%.1f%% runs=%d" % (100 * mcv, 100 * mnm, 100 * share, int(ok.sum())))
    section(O, "G5J.2", s_g2)

    # ---- G5J.3 and G5J.4
    g3res = {}

    def s_g3():
        for c, k in cells:
            rs = [r for r in cell_runs(c, k) if r["pairs"]]
            if not rs:
                for t in range(4):
                    O.gate("G5J.3", c, k, TNAME[t], "NOT_EVALUABLE", "no pairs")
                    O.gate("G5J.4", c, k, TNAME[t], "NOT_EVALUABLE", "no pairs")
                continue
            bc = np.concatenate([np.full(len(r["pairs"]["j"]), r["key"].split("|", 1)[1]) for r in rs])
            ha = np.concatenate([r["pairs"]["ha"] for r in rs]); hb = np.concatenate([r["pairs"]["hb"] for r in rs])
            st_all = {kk: np.concatenate([r["pairs"]["stats"][kk] for r in rs]) for kk in rs[0]["pairs"]["stats"]}
            seed = SEED + 1000 * COUNTRIES.index(c) + 100 * CLASSES.index(k)
            W = two_way_cluster_bootstrap(bc, ha, hb, a.nboot, seed)
            nbu = (len(np.unique(bc)), len(np.unique(np.concatenate([ha, hb]))))
            for t in range(4):
                st = {kk: v[:, t] for kk, v in st_all.items()}
                if "B1_sse" not in st:
                    O.gate("G5J.3", c, k, TNAME[t], "NOT_EVALUABLE", "no B1 predictions given"); continue
                thr = max(a.k * math.sqrt(2) * floors[k][TNAME[t]], RES_KWH)
                res = g3_cell(st, "S", thr, W, nbu)
                g3res[(c, k, t)] = res
                O.gate("G5J.3", c, k, TNAME[t], res["verdict"],
                       "r2=%.4f sign=%.4f skill_over_B1=%.4f ci95=[%.4f,%.4f] r2_B1=%.4f pairs=%d above_floor=%d thr_kwh=%.3g buildings=%d households=%d"
                       % (res["r2"], res["sign"], res["skill"], res["lo"], res["hi"], res["r2_b1"], res["pairs"], res["above"], thr, nbu[0], nbu[1]))
                if "C_sse" in st:
                    rc = g3_cell(st, "C", thr, W, nbu)
                    if res["verdict"] == "NOT_EVALUABLE" or rc["verdict"] == "NOT_EVALUABLE":
                        v4 = "NOT_EVALUABLE"; msg = "control G5J.3 verdict=%s, model G5J.3 verdict=%s" % (rc["verdict"], res["verdict"])
                    elif rc["verdict"] == "FAIL":
                        v4 = "PASS"; msg = "control fails G5J.3 (r2=%.4f sign=%.4f skill_ci_lo=%.4f)" % (rc["r2"], rc["sign"], rc["lo"])
                    else:
                        v4 = "FAIL"; msg = "control passes G5J.3 (r2=%.4f sign=%.4f skill_ci_lo=%.4f): G5J.3 FLAGGED FOR WITHDRAWAL" % (rc["r2"], rc["sign"], rc["lo"])
                    O.gate("G5J.4", c, k, TNAME[t], v4, msg)
                else:
                    O.gate("G5J.4", c, k, TNAME[t], "NOT_EVALUABLE", "no control predictions given")
    section(O, "G5J.3", s_g3)

    # ---- G5J.5
    def s_g5():
        if a.plant == "crash":
            raise RuntimeError("planted crash in section G5J.5")
        for c, k in cells:
            g5 = [x for r in cell_runs(c, k) for x in r["g5"]]
            if not g5:
                O.gate("G5J.5", c, k, "total_elec", "NOT_EVALUABLE", "no runs"); continue
            hits, days = sum(x[1] for x in g5), sum(x[2] for x in g5)
            O.gate("G5J.5", c, k, "total_elec", "PASS" if hits / days >= PEAK_MIN else "FAIL",
                   "share_days_peak_within_1h=%.1f%% dwelling_days=%d" % (100 * hits / days, days))
    section(O, "G5J.5", s_g5)

    # ---- secondary (reported, not gated)
    if a.secondary:
        def s_sec():
            for c, k in cells:
                ss = [r["sec"] for r in cell_runs(c, k) if r["sec"] is not None]
                if not ss:
                    O.info("SECONDARY country=%s class=%s no B0 pairing" % (c, k)); continue
                tot = np.sum(ss, axis=0)
                for t in range(4):
                    N, a1, a2, e2 = tot[0, t], tot[1, t], tot[2, t], tot[3, t]
                    sst = a2 - a1 ** 2 / N
                    O.info("SECONDARY country=%s class=%s target=%s r2_vs_own_B0=%.4f flats_hours=%d (reported, not gated)" % (c, k, TNAME[t], 1 - e2 / sst if sst > 0 else float("nan"), int(N)))
        try:
            s_sec()
        except Exception:
            O.info("SECONDARY section crashed: " + short_err()); O.crashed = True

    # ---- self-test of the R2 sums on 20 pairs
    if a.selftest:
        def s_self():
            rng = np.random.default_rng(SEED)
            allp = [(r, i) for r in results if r["pairs"] for i in range(len(r["pairs"]["j"]))]
            pick = [allp[i] for i in rng.choice(len(allp), a.selftest, replace=False)]
            mx, dl = 0.0, []
            pools = {t: ([], [], []) for t in range(4)}
            for r, i in pick:
                p = r["pairs"]; cl = r["key"].split("|")[0]
                for t in range(4):
                    ea = read_direct(TRUTH, cl, p["ra"][i], int(p["j"][i]), TARGETS[t], dl, "selftest_truth")
                    eb = read_direct(TRUTH, cl, p["rb"][i], int(p["j"][i]), TARGETS[t], dl, "selftest_truth")
                    sa = read_direct(a.pred + "/", cl, p["ra"][i], int(p["j"][i]), TARGETS[t], dl, "selftest_pred")
                    sb = read_direct(a.pred + "/", cl, p["rb"][i], int(p["j"][i]), TARGETS[t], dl, "selftest_pred")
                    dE, dS = ea - eb, sa - sb
                    pools[t][0].append(dE); pools[t][1].append(dS)
                    sst = ((dE - dE.mean()) ** 2).sum()
                    if sst > 0:
                        direct = 1 - ((dE - dS) ** 2).sum() / sst
                        form = r2_from_sums(p["stats"]["sEP"][i, t], p["stats"]["sEP2"][i, t], p["stats"]["S_sse"][i, t])
                        mx = max(mx, abs(direct - form))
                    pools[t][2].append((p["stats"]["sEP"][i, t], p["stats"]["sEP2"][i, t], p["stats"]["S_sse"][i, t]))
            mp_ = 0.0
            for t in range(4):
                dE = np.concatenate(pools[t][0]); dS = np.concatenate(pools[t][1])
                sst = ((dE - dE.mean()) ** 2).sum()
                if sst > 0:
                    direct = 1 - ((dE - dS) ** 2).sum() / sst
                    arr = np.array(pools[t][2])
                    mp_ = max(mp_, abs(direct - r2_from_sums(arr[:, 0], arr[:, 1], arr[:, 2])))
            openlog.extend(dl)
            with io.open(a.out + "openlog_%s.tsv" % a.tag, "a", encoding="utf-8") as fh:
                for k_, rid, p_ in dl:
                    fh.write("%s\t%s\t%s\n" % (k_, rid, p_))
            O.info("SELFTEST R2 from sums vs direct on %d pairs x 4 targets: max abs diff per pair %.3e, pooled over the 20 pairs %.3e -> %s" %
                   (a.selftest, mx, mp_, "PASS" if max(mx, mp_) <= 1e-9 else "FAIL"))
        section(O, "SELFTEST", s_self)

    # ---- gate 2.3 and G5J.6 / G5J.7
    n_out = sum(1 for k_, rid, p_ in openlog if rid not in allowed)
    O.info("CHECK 2.3 file opens logged=%d distinct_runs=%d opens_outside_the_5_allowed_lists=%d -> %s (log: %sopenlog_%s.tsv)" %
           (len(openlog), len(set(x[1] for x in openlog)), n_out, "PASS" if n_out == 0 else "FAIL", a.out, a.tag))
    O.info("INFO G5J.6 (new country) and G5J.7 (speed): reported, not gated, not computed by this step")
    cnt = {v: sum(1 for g, x in O.verdicts if x == v) for v in ("PASS", "FAIL", "NOT_EVALUABLE")}
    for g in sorted(set(g for g, _ in O.verdicts)):
        O.info("SUMMARY_GATE %s PASS=%d FAIL=%d NOT_EVALUABLE=%d" % (g, *[sum(1 for gg, x in O.verdicts if gg == g and x == v) for v in ("PASS", "FAIL", "NOT_EVALUABLE")]))
    O.info("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d crashed=%s seconds=%.0f" % (cnt["PASS"], cnt["FAIL"], cnt["NOT_EVALUABLE"], O.crashed, time.time() - t0))
    code = 1 if O.crashed else (2 if cnt["NOT_EVALUABLE"] else 0)
    O.info("SCORER_EXIT %d (0 = all computed, 2 = some NOT_EVALUABLE, 1 = crashed)" % code)
    return code


if __name__ == "__main__":
    sys.exit(main())
