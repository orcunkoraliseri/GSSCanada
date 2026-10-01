# -*- coding: utf-8 -*-
"""5J Step 8 part B, figure-data job for Figure 3. Speed job only; Spain + Italy only; never a UK file.

Post-scoring rule (Step 6 spec, 2026-10-01 05:04): reads test truth and the test predictions of S and C for the pairs of the frozen pair
rule, logs every file it opens, writes one table + its md5, writes NO verdict, gate line or score. The numbers it prints that are also
scored numbers (pair counts, above-floor counts, annual sign agreement) are compared with scores.parquet.

Usage: fig03_data.py --out DIR --scores scores.parquet
Output: <out>/fig3_pairs.parquet (long: one row per pair and target), <out>/fig3_pairs.parquet.md5.txt, <out>/openlog_<job>.tsv,
        <out>/fig3_data_<job>.txt (printed lines).
Exit: 0 all checks pass and every planted fault fired; 3 otherwise (outputs are still written); 9 refused (no lock file).
"""
import argparse, csv, hashlib, io, multiprocessing as mp, os, sys, time, traceback
import numpy as np
import pandas as pd

ROOT = "/speed-scratch/o_iseri/5J/"
LOCK = ROOT + "gates_frozen_amend1.md5"
FRZ = ROOT + "freeze/"
CAMP = ROOT + "campaign/"
TRUTH = CAMP + "extracted/"
PREDS = {"S": ROOT + "test/pred/S/", "C": ROOT + "test/pred/C/"}
STORE = ROOT + "test/store/"
TEST_LISTS = ("test_new_households", "test_new_buildings", "test_both_new")
COUNTRIES = ["es", "it"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
COLS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
TNAME = ["heating", "cooling", "equipment", "total_elec"]
H = 8760
RES_KWH = 0.001
ALLOWED = set()


def short_err():
    return traceback.format_exc().strip().splitlines()[-1][:200]


def refuse_path(p):
    for comp in p.replace("\\", "/").split("/"):
        if comp.lower().startswith("uk"):
            raise PermissionError("REFUSED: path component starting with 'uk': " + p)


def read_run(root, climate, rid, nd, log, kind):
    if rid not in ALLOWED:
        raise PermissionError("REFUSED: run %s is not in an allowed test list" % rid)
    p = "%s%s/%s.csv.gz" % (root, climate, rid)
    refuse_path(p)
    log.append((kind, rid, p, os.environ.get("SLURM_JOB_ID", "none")))
    if not os.path.exists(p):
        return None, "missing"
    try:
        df = pd.read_csv(p, comment="#", compression="gzip", usecols=["dwelling", "hour"] + COLS)
    except Exception:
        return None, "unreadable: " + short_err()
    if len(df) != nd * H:
        return None, "rows %d != %d" % (len(df), nd * H)
    df = df.sort_values(["dwelling", "hour"], kind="stable")
    if not (np.array_equal(df["dwelling"].to_numpy(), np.repeat(np.arange(nd), H)) and
            np.array_equal(df["hour"].to_numpy(), np.tile(np.arange(1, H + 1), nd))):
        return None, "dwelling or hour index wrong"
    arr = df[COLS].to_numpy(dtype=float).reshape(nd, H, 4)
    if not np.isfinite(arr).all():
        return None, "non-finite values"
    return arr, "ok"


def work(task):
    rid, cl, nd = task
    log = []
    out = {"rid": rid, "openlog": log}
    try:
        ep, st = read_run(TRUTH, cl, rid, nd, log, "truth")
        if st != "ok":
            raise RuntimeError("truth %s: %s" % (rid, st))
        res = [ep.sum(1)]
        for m in ("S", "C"):
            a, st2 = read_run(PREDS[m], cl, rid, nd, log, "pred_" + m)
            if a is None:
                raise RuntimeError("pred %s %s: %s" % (m, rid, st2))
            res.append(a.sum(1))
        out["sums"] = np.stack(res, 0)            # [3 (EP,S,C), nd, 4]
    except Exception:
        out["error"] = short_err()
    return out


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    global ALLOWED
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if not os.path.exists(LOCK):
        print("REFUSED: %s missing; exit 9" % LOCK, flush=True)
        sys.exit(9)
    jid = os.environ.get("SLURM_JOB_ID", "nojob")
    sys.path.insert(0, FRZ)
    import split_loader as sl
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    lines = []

    def P(s):
        lines.append(s)
        print(s, flush=True)

    P("FIG3_DATA_START %s job=%s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), jid))
    lists = {L: list(sl.load_split(L)) for L in TEST_LISTS}
    for L in TEST_LISTS:
        ALLOWED |= set(lists[L])
    opens = []
    runs = {}
    for cc in COUNTRIES:
        p = CAMP + "in/campaign_runs_%s.csv" % cc
        refuse_path(p)
        opens.append(("driver", "-", p, jid))
        for r in csv.DictReader(io.open(p, encoding="utf-8")):
            runs[r["run_id"]] = (r["country"], r["climate_id"], int(r["n_dwellings"]))
    sc = pd.read_parquet(a.scores)
    opens.append(("scores", "-", a.scores, jid))
    nfail, nplanted_bad = 0, 0
    recs = []
    mine = {}
    for L in TEST_LISTS:
        fp = STORE + "flats_%s.parquet" % L
        opens.append(("driver", "-", fp, jid))
        fl = pd.read_parquet(fp, columns=["run_id", "country", "climate_id", "building_id", "class", "flat", "hid"])
        same = set(fl["run_id"]) == set(lists[L])
        P("CHECK flats_runs_equal_list %s %s flats_runs=%d list_runs=%d" % (L, "PASS" if same else "FAIL", fl["run_id"].nunique(), len(lists[L])))
        nfail += 0 if same else 1
        tasks = [(rid, runs[rid][1], runs[rid][2]) for rid in sorted(lists[L])]
        sums = {}
        errs = []
        with mp.Pool(a.workers) as pool:
            for i, o in enumerate(pool.imap_unordered(work, tasks, chunksize=1)):
                opens += o["openlog"]
                if "error" in o:
                    errs.append((o["rid"], o["error"]))
                else:
                    sums[o["rid"]] = o["sums"]
                if (i + 1) % 200 == 0:
                    print("  %s progress %d/%d %.0fs" % (L, i + 1, len(tasks), time.time() - t0), flush=True)
        P("RUNS %s tasks=%d read=%d crashed_or_unreadable=%d" % (L, len(tasks), len(sums), len(errs)))
        for rid, e in errs[:3]:
            P("RUN_PROBLEM %s %s" % (rid, e))
        if errs:
            P("CHECK all_runs_read %s FAIL %d" % (L, len(errs)))
            nfail += 1
            continue
        fl = fl.sort_values(["run_id", "flat"], kind="stable").reset_index(drop=True)
        ann = np.empty((len(fl), 3, 4))
        for i, (rid, j) in enumerate(zip(fl["run_id"], fl["flat"].astype(int))):
            ann[i] = sums[rid][:, j, :]
        # pair rule (frozen): same climate, building and flat index, two different runs, different households
        ia_l, ib_l = [], []
        for _, idx in fl.groupby(["climate_id", "building_id", "flat"]).indices.items():
            a0, b0 = np.triu_indices(len(idx), 1)
            hid = fl["hid"].to_numpy()[idx]
            keep = hid[a0] != hid[b0]
            ia_l.append(idx[a0[keep]]); ib_l.append(idx[b0[keep]])
        ia = np.concatenate(ia_l) if ia_l else np.array([], int)
        ib = np.concatenate(ib_l) if ib_l else np.array([], int)
        P("PAIRS_TOTAL %s %d" % (L, len(ia)))
        rid_a, rid_b = fl["run_id"].to_numpy()[ia], fl["run_id"].to_numpy()[ib]
        flat = fl["flat"].to_numpy()[ia].astype(int)
        base = pd.DataFrame({"pair_id": [("%s|%s|%d" % (x, y, f)) for x, y, f in zip(rid_a, rid_b, flat)], "list": L,
                             "country": fl["country"].to_numpy()[ia], "class": fl["class"].to_numpy()[ia],
                             "climate": fl["climate_id"].to_numpy()[ia], "building": fl["building_id"].to_numpy()[ia], "flat": flat})
        d = ann[ia] - ann[ib]                     # [pairs, 3, 4]
        for t, tn in enumerate(TNAME):
            x = base.copy()
            x["target"] = tn
            x["dEP"], x["dS"], x["dC"] = d[:, 0, t], d[:, 1, t], d[:, 2, t]
            recs.append(x)
        for c in COUNTRIES:
            for k in CLASSES:
                mine[(L, c, k)] = int(((base["country"] == c) & (base["class"] == k)).sum())
    with io.open(a.out + "/openlog_%s.tsv" % jid, "w", encoding="utf-8") as fh:
        fh.write("kind\trun_id\tpath\tjob\n")
        for k, rid, p, jb in opens:
            fh.write("%s\t%s\t%s\t%s\n" % (k, rid, p, jb))
    # open-log check: truth/pred opens are exactly the runs of the three lists; no run outside them; no path with a 'uk' component
    allrun = set(ALLOWED)
    for kind in ("truth", "pred_S", "pred_C"):
        n_open = len([1 for k, _, _, _ in opens if k == kind])
        got = set(r for k, r, _, _ in opens if k == kind)
        ok = got == allrun and n_open == len(allrun)
        P("CHECK openlog_%s_equals_the_three_lists %s opens=%d unique=%d lists=%d" % (kind, "PASS" if ok else "FAIL", n_open, len(got), len(allrun)))
        nfail += 0 if ok else 1
    bad = [p for _, _, p, _ in opens if any(c.lower().startswith("uk") for c in p.split("/"))]
    P("CHECK openlog_no_uk_path %s" % ("PASS" if not bad else "FAIL %s" % bad[:2]))
    nfail += 0 if not bad else 1
    if len(recs) != 3 * 4:
        P("CHECK all_lists_have_pairs FAIL tables=%d" % len(recs))
        nfail += 1
    df = pd.concat(recs, ignore_index=True)
    outp = a.out + "/fig3_pairs.parquet"
    df.to_parquet(outp, index=False)
    md5 = md5_file(outp)
    with io.open(outp + ".md5.txt", "w", encoding="utf-8") as fh:
        fh.write("%s  fig3_pairs.parquet  rows=%d job=%s\n" % (md5, len(df), jid))
    P("TABLE fig3_pairs.parquet rows=%d md5=%s" % (len(df), md5))
    # ---- check 1: pair count per cell equals scores.parquet (G5J.3 `pairs`, models S and C, all four targets)
    g3 = sc[sc["gate"] == "G5J.3"]
    cnt = {}
    for (L, c, k), n in mine.items():
        for m in ("S", "C"):
            for tn in TNAME:
                r = g3[(g3["model"] == m) & (g3["list"] == L) & (g3["country"] == c) & (g3["class"] == k) & (g3["target"] == tn)]
                if len(r) != 1:
                    P("CHECK pair_count %s %s %s %s %s FAIL scores rows=%d" % (m, L, c, k, tn, len(r)))
                    nfail += 1
                    continue
                ref = r.iloc[0]["pairs"]
                ref = 0 if not np.isfinite(ref) else int(ref)
                cnt[(m, L, c, k, tn)] = (n, ref)
    nbad = [(k, v) for k, v in cnt.items() if v[0] != v[1]]
    P("CHECK pair_count_equals_scores %s cells=%d mismatches=%d %s" % ("PASS" if not nbad else "FAIL", len(cnt), len(nbad), nbad[:3]))
    nfail += 0 if not nbad else 1
    k0 = sorted(cnt)[0]
    pl = dict(cnt)
    pl[k0] = (cnt[k0][0] + 1, cnt[k0][1])
    fired = any(v[0] != v[1] for v in pl.values())
    P("CHECK_PLANTED pair_count_one_off %s" % ("FAIL (expected: the check fires on a count changed by one pair)" if fired else "PASS (UNEXPECTED: the check cannot fire)"))
    nplanted_bad += 0 if fired else 1
    # ---- check 2: above-floor count and annual sign agreement per cell equal scores.parquet (a path the pair-count check cannot reach)
    grp = {kk: vv for kk, vv in df.groupby(["list", "country", "class", "target"])}
    nsign, nsign_bad, shown = 0, [], None
    for m, col in (("S", "dS"), ("C", "dC")):
        for L in TEST_LISTS:
            for c in COUNTRIES:
                for k in CLASSES:
                    for tn in TNAME:
                        r = g3[(g3["model"] == m) & (g3["list"] == L) & (g3["country"] == c) & (g3["class"] == k) & (g3["target"] == tn)]
                        if len(r) != 1 or not np.isfinite(r.iloc[0]["above_floor"]):
                            continue
                        g = grp.get((L, c, k, tn))
                        if g is None:
                            nsign_bad.append((m, L, c, k, tn, "no pairs here"))
                            continue
                        ep, sv = g["dEP"].to_numpy(), g[col].to_numpy()
                        ab = np.abs(ep) > RES_KWH
                        sg = float((np.sign(sv[ab]) == np.sign(ep[ab])).mean()) if ab.any() else float("nan")
                        ok = int(ab.sum()) == int(r.iloc[0]["above_floor"]) and (abs(sg - r.iloc[0]["sign"]) < 6e-5 or (not np.isfinite(sg) and not np.isfinite(r.iloc[0]["sign"])))
                        nsign += 1
                        if not ok:
                            nsign_bad.append((m, L, c, k, tn, int(ab.sum()), int(r.iloc[0]["above_floor"]), round(sg, 4), r.iloc[0]["sign"]))
                        if shown is None and m == "S" and tn == "heating" and ab.sum() > 30:
                            shown = (L, c, k, tn, ep, sv, ab, r.iloc[0]["sign"])
    P("CHECK above_floor_and_sign_equal_scores %s cells=%d mismatches=%d %s" % ("PASS" if not nsign_bad else "FAIL", nsign, len(nsign_bad), nsign_bad[:3]))
    nfail += 0 if not nsign_bad else 1
    if shown is not None:
        L, c, k, tn, ep, sv, ab, ref = shown
        sg_pl = float((np.sign(-sv[ab]) == np.sign(ep[ab])).mean())
        fired = abs(sg_pl - ref) >= 6e-5
        P("CHECK_PLANTED sign_flipped_surrogate %s sign_planted=%.4f scored=%.4f" % ("FAIL (expected: the check fires when the sign of dS is reversed)" if fired else "PASS (UNEXPECTED)", sg_pl, ref))
        nplanted_bad += 0 if fired else 1
    else:
        P("CHECK_PLANTED sign_flipped_surrogate FAIL no cell to plant in")
        nplanted_bad += 1
    P("CHECKS_SUMMARY real_checks_not_passed=%d planted_checks_that_did_not_fire=%d seconds=%.0f" % (nfail, nplanted_bad, time.time() - t0))
    with io.open(a.out + "/fig3_data_%s.txt" % jid, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    P("FIG3_DATA_DONE")
    return 3 if (nfail or nplanted_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
