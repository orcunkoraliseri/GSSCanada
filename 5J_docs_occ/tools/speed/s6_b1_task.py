# -*- coding: utf-8 -*-
"""5J Step 6 part C: B1 predictions for the three test lists (Speed CPU job; Spain + Italy only; drivers only, no truth).
  usage: s6_b1_task.py <model>      model in {B1, B1_loco_es, B1_loco_it}
  B1          : the 3 saved models ckpt/B1/{heating,cooling,equipment}.joblib, all runs of the three lists
  B1_loco_es  : trained on Spain only (climate one-hot dropped), predicts the ITALIAN runs
  B1_loco_it  : trained on Italy only, predicts the SPANISH runs
Outputs are clipped at 0 kWh (heating, cooling, equipment) and total_elec = equipment + (heating + cooling)/3.0 (rules AMENDMENT 3), the
number of clipped values is printed per list. No re-implementation of features: s5_b1.Ctx / build / feature_names / write_pred are used
with the module globals pointed at the test store (ST), the predicted country (COUNTRY) and the climate flag (NO_CLIMATE).
Before any test prediction a SELF-CHECK runs the same code on 3 validation runs through the TRAIN store and compares with the Step 5
files (B1 -> pred/B1_clip0, loco -> pred/<model>): the store argument changes nothing (seen failing with a planted shift)."""
import sys, os, io, json, time, hashlib, multiprocessing as mp
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv
sys.argv = [sys.argv[0]]                 # s5_b1 parses its own flags at import; none of ours may reach it
import numpy as np
import pandas as pd
import s6_common as s6
import s5_common as c
import s5_b1 as b
sys.argv = _argv

MODEL = sys.argv[1]
TR = b.TR
SPEC = {"B1": {"ck": TR + "ckpt/B1/", "country": None, "loco": False, "train_cc": None},
        "B1_loco_es": {"ck": TR + "ckpt/B1_loco_es/", "country": "it", "loco": True, "train_cc": "es"},
        "B1_loco_it": {"ck": TR + "ckpt/B1_loco_it/", "country": "es", "loco": True, "train_cc": "it"}}[MODEL]
# Step 5 records of the joblib md5s: B1 from the Step 5 B1 log (job 1404525, MODEL_MD5 lines), B1_loco_es from the log of job 1405049;
# B1_loco_it is read from the log of job 1405050 at run time (the job this task waits for).
REC = {"B1": {"heating": "d42bb3a104b76cb8abaa459f640dbd7d", "cooling": "193d2136710d2d455a2b807c755271d3", "equipment": "620c4d4845f23007b2c25105d32197b1"},
       "B1_loco_es": {"heating": "39e951e7ad358c996caaf9868b402b9a", "cooling": "9aa4b44879decc7cac14868e4e899981", "equipment": "720f81298c9e6ce7e21817adf718f419"}}
OUTDIR = s6.TPRED + MODEL + "/"
VAL_REF = {"B1": TR + "pred/B1_clip0/", "B1_loco_es": TR + "pred/B1_loco_es/", "B1_loco_it": TR + "pred/B1_loco_it/"}[MODEL]
TNAMES = b.TNAMES
H = c.H
fails = []


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        fails.append(name)


def md5(p):
    return b.md5(p)


def md5_ok(h, recorded):
    return recorded is not None and h == recorded


def record_md5():
    if MODEL in REC:
        return REC[MODEL], "Step 5 log line (hard-coded here)"
    out = {}
    for ln in io.open(TR + "logs/s5_cb1_1405050.out", encoding="utf-8"):
        if ln.startswith("MODEL_MD5 "):
            _, t, h = ln.split()
            out[t] = h
    return out, "MODEL_MD5 lines of train/logs/s5_cb1_1405050.out"


def predict_runs_b1(ctx, models, nfeat, mu, sd, runs_tbl, pool, out_root, max_runs=None, write=True, shift=0.0):
    """Predict every run of ctx (clipped at 0). Returns (list of (run_id, climate, arr float32), values_clipped, values_total)."""
    F = ctx.F
    runs = F["run_id"].to_numpy()
    starts = np.r_[0, np.nonzero(runs[1:] != runs[:-1])[0] + 1, len(runs)]
    spans = [(int(starts[i]), int(starts[i + 1])) for i in range(len(starts) - 1)]
    if max_runs:
        spans = spans[:max_runs]
    kept, pend, nclip, ntot, nrun = [], [], 0, 0, 0
    batch, brows = [], 0

    def flush(batch):
        nonlocal nclip, ntot
        rows = np.concatenate([np.arange(a, bb) for a, bb in batch])
        rr = np.repeat(rows, H)
        hh = np.tile(np.arange(H), len(rows))
        pred = np.empty((len(rr), 3), dtype=np.float64)
        for a in range(0, len(rr), b.CH):
            Xc = b.build(ctx, rr[a:a + b.CH], hh[a:a + b.CH], nfeat)
            for ti, t in enumerate(TNAMES):
                pred[a:a + b.CH, ti] = models[t].predict(Xc).astype(np.float64) * sd[ti] + mu[ti]
        pred = pred.reshape(len(rows), H, 3)
        nclip += int((pred < 0).sum())
        ntot += pred.size
        pred = np.maximum(pred, 0.0) + shift
        o = 0
        for a, bb in batch:
            nd = bb - a
            rid = runs[a]
            assert int(runs_tbl[rid]["n_dwellings"]) == nd and list(F["flat"].iloc[a:bb]) == list(range(nd)), rid
            arr = pred[o:o + nd].astype(np.float32)
            cl = F["climate_id"].iloc[a]
            if write:
                pend.append(pool.apply_async(b.write_pred, ((cl, rid, arr, "HistGradientBoosting (B1), clipped at 0 kWh, total_elec = equipment + (heating + cooling)/3.0"),)))
            else:
                kept.append((rid, cl, arr))
            o += nd
        while len(pend) > 12:
            pend.pop(0).get()

    for a, bb in spans:
        batch.append((a, bb))
        brows += (bb - a)
        if brows * H >= b.CH * 2:
            flush(batch)
            nrun += len(batch)
            batch, brows = [], 0
    if batch:
        flush(batch)
        nrun += len(batch)
    for p in pend:
        p.get()
    return kept, nclip, ntot, nrun


def main():
    t0 = time.time()
    import joblib
    b.OUT = OUTDIR                                  # BEFORE the fork: the writer workers read this module constant
    assert b.OUT.startswith(s6.TPRED) and "/train/" not in b.OUT, b.OUT
    pool = mp.get_context("fork").Pool(3)           # forked before any OpenMP use (as s5_b1)
    LOG = []
    R = s6.runs(LOG)
    cn = json.load(open(s6.TSTORE + "static_cols.json"))
    cn["climates"] = c.climates()
    b.NO_CLIMATE = SPEC["loco"]
    names = b.feature_names(cn)
    ok, bad = c.check_features(names)
    chk("check_features", ok, "n=%d bad=%s" % (len(names), bad))
    cfgj = json.load(open(SPEC["ck"] + "b1_config.json"))
    chk("feature_list_equals_the_one_saved_with_the_models", cfgj["features"] == names, "n=%d" % len(names))
    nfeat = len(names)
    norm = json.load(open(s6.TSTORE + "norm.json"))["targets"]
    trn = json.load(open(s6.TRAIN_STORE + "norm.json"))["targets"]
    chk("norm_json_in_test_store_equals_train_store", norm == trn)
    mu = np.array([norm[t]["mean"] for t in TNAMES], dtype=np.float64)
    sd = np.array([norm[t]["sd"] for t in TNAMES], dtype=np.float64)
    # ---- checkpoints: md5 against the Step 5 record and against the snapshot taken before any prediction
    rec, rec_src = record_md5()
    models, allok = {}, True
    snap = {}
    sp = s6.TEST + "ckpt_md5_snapshot.tsv"
    if os.path.exists(sp):
        for ln in io.open(sp, encoding="utf-8"):
            p_ = ln.rstrip("\n").split("\t")
            if len(p_) >= 2:
                snap[p_[0]] = p_[1]
    for t in TNAMES:
        p = SPEC["ck"] + "%s.joblib" % t
        h = md5(p)
        same = md5_ok(h, rec.get(t))
        allok &= same
        print("CKPT_MD5 model=%s target=%s md5=%s record=%s (%s) equal=%s snapshot=%s" % (MODEL, t, h, rec.get(t), rec_src, same, snap.get(p, "none")), flush=True)
        chk("ckpt_md5_equals_step5_record_%s_%s" % (MODEL, t), same)
        if p in snap:
            chk("ckpt_md5_equals_snapshot_%s_%s" % (MODEL, t), snap[p] == h)
        models[t] = joblib.load(p)
        assert models[t].n_features_in_ == nfeat, (t, models[t].n_features_in_, nfeat)
    chk("md5_comparison_planted_wrong_value_CAUGHT (seen failing)", (not md5_ok("0" * 32, rec.get("heating"))) and md5_ok(rec.get("heating"), rec.get("heating")))
    # ---- self-check on validation through the TRAIN store (the store argument changes nothing)
    b.ST = s6.TRAIN_STORE
    b.COUNTRY = SPEC["train_cc"]
    vctx = b.Ctx("validation", cn)
    outv, nc, nt, nr = predict_runs_b1(vctx, models, nfeat, mu, sd, R, pool, None, max_runs=3, write=False)
    worst, worst_pl = 0.0, 0.0
    for rid, cl, arr in outv:
        ref = pd.read_csv("%s%s/%s.csv.gz" % (VAL_REF, cl, rid), comment="#", compression="gzip")
        nd = arr.shape[0]
        full = np.empty((nd, H, 4), dtype=np.float64)
        full[:, :, :3] = arr
        full[:, :, 3] = arr[:, :, 2] + (arr[:, :, 0] + arr[:, :, 1]) / c.COP
        mine = full.reshape(-1, 4)
        refv = ref[["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]].to_numpy(dtype=np.float64)
        worst = max(worst, float(np.abs(mine - refv).max()))
        worst_pl = max(worst_pl, float(np.abs(mine + 1e-3 - refv).max()))
    chk("train_store_path_reproduces_step5_validation_predictions", len(outv) == 3 and worst <= 1e-5, "runs=%d ref=%s max abs diff %.3e kWh (file precision 8 digits)" % (len(outv), VAL_REF, worst))
    chk("selfcheck_planted_shift_1e-3_CAUGHT (seen failing)", worst_pl > 1e-5, "max abs diff with a planted +1e-3 shift %.3e" % worst_pl)
    del vctx
    # ---- test predictions
    if os.path.exists(OUTDIR) and os.listdir(OUTDIR):
        print("REFUSED: %s already holds files" % OUTDIR)
        sys.exit(4)
    b.ST = s6.TSTORE
    b.COUNTRY = SPEC["country"]
    assert b.OUT == OUTDIR
    if fails:
        print("STOP: a check before the test predictions failed: %s" % fails, flush=True)
        sys.exit(1)
    os.makedirs(OUTDIR, exist_ok=True)
    L = s6.lists()
    tot_runs = 0
    for nm in s6.TEST_LISTS:
        ctx = b.Ctx(nm, cn)
        assert set(ctx.F["run_id"]) <= set(L[nm])
        if SPEC["country"]:
            assert set(ctx.F["country"]) == {SPEC["country"]}
        _, nc, nt, nr = predict_runs_b1(ctx, models, nfeat, mu, sd, R, pool, OUTDIR, write=True)
        tot_runs += nr
        print("CLIPPED_AT_0 model=%s list=%s values_clipped=%d of %d (%.4f%%) (heating, cooling, equipment; total recomputed)" % (MODEL, nm, nc, nt, 100.0 * nc / max(1, nt)), flush=True)
        print("COUNT model=%s list=%s runs_written=%d flats=%d country=%s" % (MODEL, nm, nr, len(ctx.F), SPEC["country"] or "es+it"), flush=True)
        del ctx
    pool.close()
    pool.join()
    s6.flush_log(LOG, "b1_" + MODEL)
    badl = s6.check_lines(s6.read_log_file(s6.TEST + "openlog_b1_%s.tsv" % MODEL), s6.b0_ids())
    chk("openlog_driver_only", not badl, "offending=%d" % len(badl))
    print("B1_TASK_DONE model=%s %s runs=%d seconds=%.0f" % (MODEL, "OK" if not fails else "FAILED %s" % fails, tot_runs, time.time() - t0), flush=True)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
