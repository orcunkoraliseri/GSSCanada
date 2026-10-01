# -*- coding: utf-8 -*-
"""5J Step 6 part B0: the REPORTED (not gated) analyses. Speed job only; Spain + Italy only; never a UK file.

Usage:  s6_reported.py --pred DIR --split validation --out DIR --tag NAME [--pairs-ref score_file.txt] [--test]
  --split validation (default use now) reads the lists validation, b0_dev, b0_val through split_loader.load_split.
  --test  scores a sealed test list (test_new_households, test_new_buildings, test_both_new) and is REFUSED (exit 9)
          unless /speed-scratch/o_iseri/5J/gates_frozen_amend1.md5 exists. The refusal is the first thing the script does.
Truth = /speed-scratch/o_iseri/5J/campaign/extracted/ (as the frozen scorer). Predictions = <pred>/<climate_id>/<run_id>.csv.gz.
Household drivers = <store>/hh_<cc>.npz (people, appl_w) and <store>/flats_<split>.parquet; store = train/store/ for
validation, test/store/ for a test list.
Writes <out>/reported_<tag>.txt, <out>/reported_<tag>.parquet (long form), <out>/reported_<tag>_flats.parquet (one row per
flat), <out>/openlog_<tag>.tsv (kind, run_id, path, job). Every file open of truth or prediction goes through read_run,
which refuses a run id outside the lists loaded here.
Analyses (spec 6A, 6D): 1 thermal-mass lag, 2 mild-climate cooling, 3 level versus timing. All are INFO.
"""
import argparse, csv, io, multiprocessing as mp, os, sys, time, traceback
import numpy as np
import pandas as pd

ROOT = "/speed-scratch/o_iseri/5J/"
LOCK = ROOT + "gates_frozen_amend1.md5"
FRZ = "/speed-scratch/o_iseri/5J/freeze/"
CAMP = "/speed-scratch/o_iseri/5J/campaign/"
TRUTH = CAMP + "extracted/"
TARGETS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
TNAME = ["heating", "cooling", "equipment", "total_elec"]
COUNTRIES = ["es", "it"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
H = 8760
MAXLAG = 24
MIN_HEAT_HOURS = 500
EP_COOL_MIN = 1e-3                      # kWh per year; flats with less EP cooling are left out of the relative error
SHIFT_H = 6
TEST_LISTS = ("test_new_households", "test_new_buildings", "test_both_new")

ALLOWED = set()
PEOPLE = {}
PRED = ""


def short_err():
    return traceback.format_exc().strip().splitlines()[-1][:200]


# ------------------------------------------------------------------------------------------ run table and readers
def load_runs():
    rows = {}
    for cc in COUNTRIES:
        for r in csv.DictReader(io.open(CAMP + "in/campaign_runs_%s.csv" % cc, encoding="utf-8")):
            assert r["country"] == cc and r["run_id"].startswith(cc + "_")
            rows[r["run_id"]] = {"run_id": r["run_id"], "country": cc, "climate": r["climate_id"], "building": r["building_id"],
                                 "cls": r["class"], "nd": int(r["n_dwellings"])}
    return rows


def read_run(root, climate, rid, nd, log, kind):
    """(array [nd, 8760, 4] float64, 'ok') or (None, reason). Refuses a run id outside the allowed lists; logs every open."""
    if rid not in ALLOWED:
        raise PermissionError("REFUSED: run %s is not in an allowed split list" % rid)
    p = "%s%s/%s.csv.gz" % (root, climate, rid)
    log.append((kind, rid, p, os.environ.get("SLURM_JOB_ID", "none")))
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


# ------------------------------------------------------------------------------------------ analysis 1: lag
def lag_peak(p, h, mask):
    """Lag (0..24 h) of the peak Pearson correlation between presence p(t) and heating h(t+L), over the hours t+L inside mask."""
    cors = np.full(MAXLAG + 1, np.nan)
    for L in range(MAXLAG + 1):
        idx = np.flatnonzero(mask[L:]) + L
        if idx.size < 3:
            continue
        x = p[idx - L]
        y = h[idx]
        x = x - x.mean()
        y = y - y.mean()
        d = np.sqrt((x * x).sum() * (y * y).sum())
        if d > 0:
            cors[L] = (x * y).sum() / d
    if np.all(np.isnan(cors)):
        return float("nan")
    return float(np.nanargmax(cors))


def flat_lags(p, heat_ep, heat_s):
    mask = heat_ep > 0
    n = int(mask.sum())
    if n < MIN_HEAT_HOURS:
        return n, float("nan"), float("nan")
    return n, lag_peak(p, heat_ep, mask), lag_peak(p, heat_s, mask)


def work(task):
    rid, cl, nd, flats, cc, selfcheck = task
    log = []
    out = {"rid": rid, "openlog": log}
    try:
        ep, st = read_run(TRUTH, cl, rid, nd, log, "truth")
        if st != "ok":
            raise RuntimeError("truth unreadable %s: %s" % (rid, st))
        s, st2 = read_run(PRED, cl, rid, nd, log, "pred_S")
        if s is None:
            out["skipped"] = st2
            return out
        if len(flats) != nd:
            raise RuntimeError("run %s: %d flats in the store but %d dwellings" % (rid, len(flats), nd))
        rows = []
        for j, hi in flats:
            p = PEOPLE[cc][hi].astype(float)
            n, le, ls = flat_lags(p, ep[j, :, 0], s[j, :, 0])
            row = [j, n, le, ls] + list(ep[j].sum(0)) + list(s[j].sum(0))
            if selfcheck:
                h2 = np.roll(ep[j, :, 0], SHIFT_H)                       # EP heating arrives SHIFT_H hours later
                n2, l2, _ = flat_lags(p, h2, h2)
                n3, l3, _ = flat_lags(p, ep[j, :, 0], ep[j, :, 0])      # planted defect: the shift is lost, the series is the unshifted one
                row += [l2, l3]
            rows.append(row)
        out["rows"] = rows
    except Exception:
        out["error"] = short_err()
    return out


# ------------------------------------------------------------------------------------------ statistics
def r2_annual(y, yh):
    y, yh = np.asarray(y, float), np.asarray(yh, float)
    if len(y) < 2:
        return float("nan")
    sst = ((y - y.mean()) ** 2).sum()
    return float(1 - ((y - yh) ** 2).sum() / sst) if sst > 0 else float("nan")


def ols_r2(X, y):
    if len(y) < 4:
        return float("nan")
    A = np.column_stack([np.ones(len(y)), X])
    beta = np.linalg.lstsq(A, y, rcond=None)[0]
    sst = ((y - y.mean()) ** 2).sum()
    return float(1 - ((y - A @ beta) ** 2).sum() / sst) if sst > 0 else float("nan")


def cooling_cells(fl, pairs, s_cool):
    """{(climate, class): (pairs, R2 of annual pair effect of cooling)} with s_cool = the S annual cooling per flat."""
    out = {}
    ep = fl["ep_cooling"].to_numpy()
    for (cl, k), g in pairs.groupby(["climate", "cls"]):
        ia, ib = g["ia"].to_numpy(), g["ib"].to_numpy()
        out[(cl, k)] = (len(g), r2_annual(ep[ia] - ep[ib], s_cool[ia] - s_cool[ib]))
    return out


def check_cooling_constant(cells):
    """Rule: a constant S cooling gives R2 <= 0 in every cell where R2 is defined (and at least one cell is defined)."""
    v = [r for (_, r) in cells.values() if np.isfinite(r)]
    return bool(v) and all(r <= 1e-9 for r in v), len(v), (max(v) if v else float("nan"))


def check_pair_count(mine, ref):
    bad = [(k, mine.get(k), ref.get(k)) for k in sorted(set(mine) | set(ref)) if mine.get(k) != ref.get(k)]
    return not bad, bad


def parse_pairs_ref(path):
    ref = {}
    for ln in io.open(path, encoding="utf-8"):
        if ln.startswith("PAIRS country="):
            d = dict(x.split("=", 1) for x in ln.split()[1:])
            ref[(d["country"], d["class"])] = int(d["pairs"])
    return ref


def fmt(x, nd=4):
    return "nan" if x is None or (isinstance(x, float) and not np.isfinite(x)) else ("%.*f" % (nd, x))


# ------------------------------------------------------------------------------------------ main
def main():
    global ALLOWED, PEOPLE, PRED
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pairs-ref")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    # ---- refusals first, before any list or file is read
    if a.test:
        if not os.path.exists(LOCK):
            print("REFUSED: --test needs %s (the amended gates are not frozen); exit 9" % LOCK, flush=True)
            sys.exit(9)
        if a.split not in TEST_LISTS:
            print("REFUSED: --test needs one of %s; exit 9" % (TEST_LISTS,), flush=True)
            sys.exit(9)
        store = ROOT + "test/store/"
    else:
        if a.split != "validation":
            print("REFUSED: without --test only the list 'validation' is allowed; exit 9", flush=True)
            sys.exit(9)
        store = ROOT + "train/store/"
    sys.path.insert(0, FRZ)
    import split_loader as sl
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    lines = []

    def P(s):
        lines.append(s)
        print(s, flush=True)

    P("REPORTED_START %s tag=%s split=%s pred=%s store=%s test=%s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), a.tag, a.split, a.pred, store, a.test))
    allowed = set(sl.load_split(a.split))
    if not a.test:
        for nm in ("b0_dev", "b0_val"):
            allowed |= set(sl.load_split(nm))
    split_ids = sl.load_split(a.split)
    ALLOWED = allowed
    PRED = a.pred.rstrip("/") + "/"
    runs = load_runs()
    flats = pd.read_parquet(store + "flats_%s.parquet" % a.split, columns=["run_id", "country", "climate_id", "building_id", "class", "flat", "hid", "hh_index"])
    ck_fail, ck_planted_bad = 0, 0
    same = set(flats["run_id"]) == set(split_ids)
    P("CHECK flats_runs_equal_list %s flats_runs=%d list_runs=%d" % ("PASS" if same else "FAIL", flats["run_id"].nunique(), len(split_ids)))
    ck_fail += 0 if same else 1
    ann = {}
    for cc in COUNTRIES:
        z = np.load(store + "hh_%s.npz" % cc)
        PEOPLE[cc] = z["people"]
        ann[cc] = (PEOPLE[cc].astype(np.float64).sum(1), z["appl_w"].astype(np.float64).sum(1) / 1000.0)
    # ---- one task per run
    flats = flats.sort_values(["run_id", "flat"], kind="stable").reset_index(drop=True)
    first = sorted(set(flats["run_id"]))[0]
    tasks = []
    for rid, g in flats.groupby("run_id", sort=True):
        r = runs[rid]
        tasks.append((rid, r["climate"], r["nd"], list(zip(g["flat"].astype(int), g["hh_index"].astype(int))), r["country"], rid == first))
    recs, log, skipped, errs = [], [], [], []
    with mp.Pool(a.workers) as pool:
        for i, o in enumerate(pool.imap_unordered(work, tasks, chunksize=1)):
            log += o["openlog"]
            if "error" in o:
                errs.append((o["rid"], o["error"]))
            elif "skipped" in o:
                skipped.append((o["rid"], o["skipped"]))
            else:
                for row in o["rows"]:
                    recs.append([o["rid"]] + row)
            if (i + 1) % 200 == 0:
                print("  progress %d/%d runs %.0fs" % (i + 1, len(tasks), time.time() - t0), flush=True)
    with io.open(a.out + "/openlog_%s.tsv" % a.tag, "w", encoding="utf-8") as fh:
        fh.write("kind\trun_id\tpath\tjob\n")
        for k, rid, p, jb in log:
            fh.write("%s\t%s\t%s\t%s\n" % (k, rid, p, jb))
    P("RUNS tasks=%d flats_read=%d runs_without_usable_prediction=%d runs_crashed=%d" % (len(tasks), len(recs), len(skipped), len(errs)))
    for rid, e in (skipped[:3] + errs[:3]):
        P("RUN_PROBLEM %s %s" % (rid, e))
    if errs:
        P("CHECK all_runs_read FAIL %d crashed" % len(errs))
        ck_fail += 1
    cols = ["run_id", "flat", "n_heat_hours", "lag_ep", "lag_s"] + ["ep_" + t for t in TNAME] + ["s_" + t for t in TNAME] + ["lag_ep_shifted", "lag_ep_blind"]
    df = pd.DataFrame([r + [np.nan] * (len(cols) - len(r)) for r in recs], columns=cols)
    fl = flats.merge(df, on=["run_id", "flat"], how="inner").reset_index(drop=True)
    fl = fl.rename(columns={"class": "cls", "climate_id": "climate", "building_id": "building"})
    fl["people_hours"] = [ann[c][0][h] for c, h in zip(fl["country"], fl["hh_index"])]
    fl["appl_kwh"] = [ann[c][1][h] for c, h in zip(fl["country"], fl["hh_index"])]
    # ---- pairs: same climate, building and flat index, two different runs, different households
    ia_l, ib_l = [], []
    for _, idx in fl.groupby(["climate", "building", "flat"]).indices.items():
        a0, b0 = np.triu_indices(len(idx), 1)
        hid = fl["hid"].to_numpy()[idx]
        keep = hid[a0] != hid[b0]
        ia_l.append(idx[a0[keep]]); ib_l.append(idx[b0[keep]])
    ia = np.concatenate(ia_l) if ia_l else np.array([], int)
    ib = np.concatenate(ib_l) if ib_l else np.array([], int)
    pairs = pd.DataFrame({"ia": ia, "ib": ib, "country": fl["country"].to_numpy()[ia], "cls": fl["cls"].to_numpy()[ia], "climate": fl["climate"].to_numpy()[ia]})
    mine = {(c, k): int(((pairs["country"] == c) & (pairs["cls"] == k)).sum()) for c in COUNTRIES for k in CLASSES}
    P("PAIRS_TOTAL %d" % len(pairs))
    long_rows = []

    # ---- CHECK 1: pair count equals the frozen scorer's
    if a.pairs_ref:
        ref = parse_pairs_ref(a.pairs_ref)
        ok, bad = check_pair_count(mine, ref)
        P("CHECK pair_count_equals_scorer %s cells=%d ref=%s %s" % ("PASS" if ok else "FAIL", len(ref), a.pairs_ref, "" if ok else "differences=%s" % bad[:4]))
        ck_fail += 0 if ok else 1
        ref2 = dict(ref)
        k0 = sorted(ref2)[0]
        ref2[k0] += 1
        ok2, _ = check_pair_count(mine, ref2)
        P("CHECK_PLANTED pair_count_one_off %s" % ("FAIL (expected: the check fires on a reference changed by one pair)" if not ok2 else "PASS (UNEXPECTED: the check cannot fire)"))
        ck_planted_bad += 1 if ok2 else 0

    # ---- CHECK 2: planted +6 h shift of one EP heating series moves the EP lag by 6 h
    sc = fl[(fl["run_id"] == first) & np.isfinite(fl["lag_ep"]) & np.isfinite(fl["lag_ep_shifted"])]
    sc = sc[sc["lag_ep"] + SHIFT_H <= MAXLAG]
    if len(sc):
        r0 = sc.iloc[0]
        d_real = float(r0["lag_ep_shifted"] - r0["lag_ep"])
        ok = d_real == SHIFT_H
        P("CHECK lag_shift_plus6h %s run=%s flat=%d lag_ep=%d lag_ep_shifted=%d delta=%d (flats with a usable lag in this run: %d)" %
          ("PASS" if ok else "FAIL", first, int(r0["flat"]), r0["lag_ep"], r0["lag_ep_shifted"], d_real, len(sc)))
        ck_fail += 0 if ok else 1
        d_blind = float(r0["lag_ep_blind"] - r0["lag_ep"])      # planted defect: the shift is lost before the lag code
        P("CHECK_PLANTED lag_shift_plus6h_blind %s delta=%d" % ("FAIL (expected: the check fires when the shift is lost)" if d_blind != SHIFT_H else "PASS (UNEXPECTED)", d_blind))
        ck_planted_bad += 1 if d_blind == SHIFT_H else 0
    else:
        P("CHECK lag_shift_plus6h FAIL no flat of run %s has a usable lag with room for +%d h" % (first, SHIFT_H))
        ck_fail += 1

    # ---- analysis 1
    for c in COUNTRIES:
        for k in CLASSES:
            g = fl[(fl["country"] == c) & (fl["cls"] == k)]
            if g.empty:
                continue
            u = g[np.isfinite(g["lag_ep"]) & np.isfinite(g["lag_s"])]
            few = int((g["n_heat_hours"] < MIN_HEAT_HOURS).sum())
            w = float((np.abs(u["lag_s"] - u["lag_ep"]) <= 1).mean()) if len(u) else float("nan")
            me, ms = (float(u["lag_ep"].median()), float(u["lag_s"].median())) if len(u) else (float("nan"), float("nan"))
            P("REPORTED thermal_mass_lag country=%s class=%s flats=%d flats_skipped_under_%d_heating_hours=%d median_lag_ep_h=%s median_lag_s_h=%s share_within_1h=%s" %
              (c, k, len(u), MIN_HEAT_HOURS, few, fmt(me, 1), fmt(ms, 1), fmt(w)))
            for mname, v in (("flats", len(u)), ("flats_skipped", few), ("median_lag_ep_h", me), ("median_lag_s_h", ms), ("share_within_1h", w)):
                long_rows.append(("thermal_mass_lag", c, k, "", "heating", mname, float(v)))

    # ---- analysis 2
    s_cool = fl["s_cooling"].to_numpy()
    cells = cooling_cells(fl, pairs, s_cool)
    for cl in sorted(fl["climate"].unique()):
        for k in CLASSES:
            g = fl[(fl["climate"] == cl) & (fl["cls"] == k)]
            if g.empty:
                continue
            pos = g[g["ep_cooling"] > EP_COOL_MIN]
            rel = ((pos["s_cooling"] - pos["ep_cooling"]) / pos["ep_cooling"]).to_numpy()
            mre = float(np.median(rel)) if len(rel) else float("nan")
            mae = float(np.median(np.abs(rel))) if len(rel) else float("nan")
            npair, r2 = cells.get((cl, k), (0, float("nan")))
            P("REPORTED mild_climate_cooling climate=%s class=%s flats=%d flats_with_ep_cooling=%d median_rel_error=%s median_abs_rel_error=%s pairs=%d r2_annual_pair_effect=%s" %
              (cl, k, len(g), len(pos), fmt(mre), fmt(mae), npair, fmt(r2)))
            for mname, v in (("flats", len(g)), ("flats_with_ep_cooling", len(pos)), ("median_rel_error", mre), ("median_abs_rel_error", mae), ("pairs", npair), ("r2_annual_pair_effect", r2)):
                long_rows.append(("mild_climate_cooling", cl[:2], k, cl, "cooling", mname, float(v)))

    # ---- CHECK 3: constant S cooling gives R2 <= 0
    ok, ncell, mx = check_cooling_constant(cooling_cells(fl, pairs, np.full(len(fl), 1.0)))
    P("CHECK cooling_constant_S_r2_not_positive %s cells_defined=%d max_r2=%s" % ("PASS" if ok else "FAIL", ncell, fmt(mx, 6)))
    ck_fail += 0 if ok else 1
    ok2, ncell2, mx2 = check_cooling_constant(cooling_cells(fl, pairs, fl["ep_cooling"].to_numpy()))
    P("CHECK_PLANTED cooling_constant_rule_on_S_equals_EP %s cells_defined=%d max_r2=%s" %
      ("FAIL (expected: the check fires when S is EnergyPlus itself)" if not ok2 else "PASS (UNEXPECTED: the check cannot fire)", ncell2, fmt(mx2, 6)))
    ck_planted_bad += 1 if ok2 else 0

    # ---- analysis 3
    x1_all = fl["people_hours"].to_numpy()
    x2_all = fl["appl_kwh"].to_numpy()
    for c in COUNTRIES:
        for k in CLASSES:
            g = pairs[(pairs["country"] == c) & (pairs["cls"] == k)]
            if g.empty:
                continue
            A, B = g["ia"].to_numpy(), g["ib"].to_numpy()
            X = np.column_stack([x1_all[A] - x1_all[B], x2_all[A] - x2_all[B]])
            for tn in ("heating", "cooling"):
                ye = fl["ep_" + tn].to_numpy()[A] - fl["ep_" + tn].to_numpy()[B]
                ys = fl["s_" + tn].to_numpy()[A] - fl["s_" + tn].to_numpy()[B]
                re, rs = ols_r2(X, ye), ols_r2(X, ys)
                P("REPORTED level_vs_timing country=%s class=%s target=%s pairs=%d share_explained_by_level_ep=%s share_explained_by_level_s=%s" % (c, k, tn, len(g), fmt(re), fmt(rs)))
                for mname, v in (("pairs", len(g)), ("share_explained_by_level_ep", re), ("share_explained_by_level_s", rs)):
                    long_rows.append(("level_vs_timing", c, k, "", tn, mname, float(v)))

    P("CHECKS_SUMMARY real_checks_not_passed=%d planted_checks_that_did_not_fire=%d seconds=%.0f" % (ck_fail, ck_planted_bad, time.time() - t0))
    with io.open(a.out + "/reported_%s.txt" % a.tag, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    pd.DataFrame(long_rows, columns=["analysis", "country", "cls", "climate", "target", "metric", "value"]).to_parquet(a.out + "/reported_%s.parquet" % a.tag, index=False)
    fl.drop(columns=["hh_index"]).to_parquet(a.out + "/reported_%s_flats.parquet" % a.tag, index=False)
    P("REPORTED_DONE")
    return 3 if (ck_fail or ck_planted_bad or errs) else 0


if __name__ == "__main__":
    sys.exit(main())
