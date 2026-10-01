# -*- coding: utf-8 -*-
"""5J Step 6 part C (GPU, one array task): predictions of a sequence-model checkpoint for the three test lists.
  usage: s6_pred_task.py <idx>   0 S, 1 C, 2 S_seed2, 3 S_seed3, 4 S_loco_es, 5 S_loco_it
  S           : pinned winner S3 (train/winner/pinned/best.pt; md5 equal to winner.json, best.pt.md5 and ckpt/S/3/best.pt)
  C           : blind control seed 1 (ckpt/C_seed1): household and neighbour drivers replaced by the donor row (s5_data.blind_donors rule,
                inside the same test list table); donor checks printed (0 same-run, 0 other-country; Data stops otherwise)
  S_seed2/3   : ckpt/S_seed2, ckpt/S_seed3 (reported only)
  S_loco_es   : trained on Spain, predicts the ITALIAN runs ; S_loco_it : trained on Italy, predicts the SPANISH runs
Static vectors: z-scored AND clipped with the checkpoint's own static_stats (mean, sd, zmin, zmax), in s6_data.Data (the s5_data code path);
a checkpoint without zmin/zmax is refused. STATIC_CLIP is printed per list by Data and recorded.
Data(store=test store) refuses everything but the three test lists and refuses targets. No test truth is read (drivers only).
Self-check before any test prediction: the same code with the TRAIN store predicts 2 validation runs and is compared with the Step 5
validation prediction of the same checkpoint (flags-off equality of the store argument), seen failing with a planted shift."""
import hashlib, io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import pandas as pd
import torch
import s6_common as s6
import s5_common as c
import s6_data as sd6          # Data with the store argument
import s5_predict as sp        # predict_runs(..., data=...) is the Step 5 function, unchanged

T = c.TRAIN
IDX = int(sys.argv[1])
NAME = ["S", "C", "S_seed2", "S_seed3", "S_loco_es", "S_loco_it"][IDX]
SPEC = {"S": {"ck": T + "winner/pinned/", "country": None, "train_cc": None, "val_ref": T + "pred/S3/"},
        "C": {"ck": T + "ckpt/C_seed1/", "country": None, "train_cc": None, "val_ref": T + "pred/C_seed1/"},
        "S_seed2": {"ck": T + "ckpt/S_seed2/", "country": None, "train_cc": None, "val_ref": T + "pred/S_seed2/"},
        "S_seed3": {"ck": T + "ckpt/S_seed3/", "country": None, "train_cc": None, "val_ref": T + "pred/S_seed3/"},
        "S_loco_es": {"ck": T + "ckpt/S_loco_es/", "country": "it", "train_cc": "es", "val_ref": None},
        "S_loco_it": {"ck": T + "ckpt/S_loco_it/", "country": "es", "train_cc": "it", "val_ref": None}}[NAME]
OUT = s6.TPRED + NAME
H = c.H
fails = []


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        fails.append(name)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    t0 = time.time()
    dev = "cuda"
    print("PREDICT name=%s ckpt=%s predicted_country=%s out=%s torch=%s gpu=%s" % (NAME, SPEC["ck"], SPEC["country"] or "es+it", OUT, torch.__version__, torch.cuda.get_device_name(0)), flush=True)
    if os.path.exists(OUT) and os.listdir(OUT):
        print("REFUSED: %s already holds files" % OUT)
        sys.exit(4)
    # ---- checkpoint md5s
    p = SPEC["ck"] + "best.pt"
    h = md5(p)
    snap = {}
    spath = s6.TEST + "ckpt_md5_snapshot.tsv"
    for ln in io.open(spath, encoding="utf-8"):
        q = ln.rstrip("\n").split("\t")
        if len(q) >= 2:
            snap[q[0]] = q[1]
    if NAME == "S":
        wj = json.load(open(T + "winner/winner.json"))
        rec_pin = open(T + "winner/pinned/best.pt.md5").read().split()[0]
        h3 = md5(T + "ckpt/S/3/best.pt")
        print("CKPT_MD5 name=S md5=%s winner.json=%s best.pt.md5=%s ckpt/S/3=%s" % (h, wj["ckpt_md5"], rec_pin, h3), flush=True)
        chk("S_md5_equals_winner_json_and_pin_file_and_grid_checkpoint", h == wj["ckpt_md5"] == rec_pin == h3)
        chk("S_is_config_S3_seed1", wj["config"]["id"] == "S3" and wj["config"]["seed"] == 1)
    else:
        print("CKPT_MD5 name=%s md5=%s (no Step 5 record of this md5 exists; compared with the snapshot taken before any prediction: %s)" % (NAME, h, snap.get(p, "none")), flush=True)
    chk("ckpt_md5_equals_snapshot_taken_before_prediction_%s" % NAME, snap.get(p) == h, "snapshot=%s" % snap.get(p))
    ck = torch.load(p, map_location=dev, weights_only=False)
    cfg = ck["config"]
    ss = ck["static_stats"]
    print("CONFIG name=%s id=%s family=%s width=%s depth=%s lam=%s seed=%s blind=%s country=%s no_climate=%s ; static_stats keys=%s" % (
        NAME, cfg.get("id"), cfg.get("family"), cfg.get("width"), cfg.get("depth"), cfg.get("lam"), cfg.get("seed"), cfg.get("blind"), cfg.get("country"), cfg.get("no_climate"), sorted(ss.keys())), flush=True)
    chk("static_stats_has_zmin_zmax", "zmin" in ss and "zmax" in ss and "mean" in ss and "sd" in ss)
    chk("config_matches_role", cfg.get("country") == SPEC["train_cc"] and bool(cfg.get("blind", False)) == (NAME == "C") and bool(cfg.get("no_climate", False)) == (SPEC["train_cc"] is not None),
        "country=%s blind=%s no_climate=%s" % (cfg.get("country"), cfg.get("blind"), cfg.get("no_climate")))
    if fails:
        print("STOP: %s" % fails, flush=True)
        sys.exit(1)
    # ---- self-check: train store, 2 validation runs, same checkpoint
    if SPEC["val_ref"] and os.path.isdir(SPEC["val_ref"]):
        dv = sd6.Data("validation", dev, stats=ss, load_targets=False, drop_climate=bool(cfg.get("no_climate", False)), country=cfg.get("country"), blind=bool(cfg.get("blind", False)))
        runs2 = sorted(set(dv.flats["run_id"]))[:2]
        tmp = s6.TEST + "check/selfcheck_%s/" % NAME
        sp.predict_runs(SPEC["ck"], tmp, run_ids=runs2, device=dev, data=dv)
        worst, worst_pl = 0.0, 0.0
        for rid in runs2:
            cl = dv.flats["climate_id"][dv.flats["run_id"] == rid].iloc[0]
            cols = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
            a = pd.read_csv("%s%s/%s.csv.gz" % (tmp, cl, rid), comment="#", compression="gzip")[cols].to_numpy(dtype=np.float64)
            r = pd.read_csv("%s%s/%s.csv.gz" % (SPEC["val_ref"], cl, rid), comment="#", compression="gzip")[cols].to_numpy(dtype=np.float64)
            worst = max(worst, float(np.abs(a - r).max()))
            worst_pl = max(worst_pl, float(np.abs(a + 1e-2 - r).max()))
        chk("train_store_path_reproduces_step5_validation_predictions", worst <= 2e-3, "runs=%s ref=%s max abs diff %.3e kWh (bf16 GPU run, tolerance 2e-3)" % (runs2, SPEC["val_ref"], worst))
        chk("selfcheck_planted_shift_1e-2_CAUGHT (seen failing)", worst_pl > 2e-3, "max abs diff with a planted +1e-2 shift %.3e" % worst_pl)
        del dv
    else:
        print("INFO no Step 5 validation prediction of %s to compare with (self-check skipped; data-class equality is proved in s6_dcheck)" % NAME, flush=True)
    if fails:
        print("STOP: %s" % fails, flush=True)
        sys.exit(1)
    # ---- test lists
    tot = 0
    for nm in s6.TEST_LISTS:
        dv = sd6.Data(nm, dev, stats=ss, load_targets=False, drop_climate=bool(cfg.get("no_climate", False)), country=SPEC["country"], blind=bool(cfg.get("blind", False)), store=sd6.TEST_STORE)
        print("TEST_LIST name=%s list=%s rows=%d runs=%d STATIC_CLIP_RECORD values_clipped=%d columns=%s" % (
            NAME, nm, len(dv.flats), dv.flats["run_id"].nunique(), dv.clip_info["values_clipped"], dv.clip_info["columns_clipped"]), flush=True)
        if SPEC["country"]:
            chk("only_%s_runs_in_%s" % (SPEC["country"], nm), set(dv.flats["country"]) == {SPEC["country"]})
        if cfg.get("blind"):
            bi = dv.blind_info
            chk("blind_donor_checks_%s" % nm, bi["donor_same_run"] == 0 and bi["donor_other_country"] == 0, "same_run=%d other_country=%d INFO own_hid_share=%.5f rows=%d" % (bi["donor_same_run"], bi["donor_other_country"], bi["share_donor_hid_equals_own_hid"], bi["n_rows"]))
        t1 = time.time()
        info = sp.predict_runs(SPEC["ck"], OUT, device=dev, data=dv)
        tot += len(info)
        print("COUNT model=%s list=%s runs_written=%d rows_written=%d window_shapes=%s seconds=%.0f" % (
            NAME, nm, len(info), sum(i["rows_written"] for i in info), sorted(set(str(i["window_shape"]) for i in info)), time.time() - t1), flush=True)
        del dv
        torch.cuda.empty_cache()
    print("PRED_TASK_DONE name=%s %s runs=%d seconds=%.0f" % (NAME, "OK" if not fails else "FAILED %s" % fails, tot, time.time() - t0), flush=True)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
