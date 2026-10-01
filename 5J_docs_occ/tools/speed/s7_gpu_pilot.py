# -*- coding: utf-8 -*-
"""5J Step 7 part E (Speed GPU job, one A100 slice): district store for draws 0-9 + pinned S3 predictions + timing.
Store code path = Step 6 part A (s6_store.flat_records, the SAME function; s6_data.Data with a store-dir argument, NO targets).
Reads only: sealed in/ files, hh/pool/ (household folders), campaign in/ tables (drivers), the train/test stores (drivers; copied files),
the pinned checkpoint. No truth file of any run is read (not even a development one); the reproduction check compares flats built by
this script with the Step 5 flats_development.parquet drivers (a drivers table, no targets).
Writes only under district/ (store/, pilot/, out/)."""
import hashlib, io, json, multiprocessing as mp, os, shutil, sys, time
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import numpy as np
import pandas as pd
import torch
import s7_common as s7
import s7_draws as dr
import s5_common as c
import s5_store as s5s
import s6_store as s6s
import s6_data as sd6
import s5_predict as sp
import s5_models as sm

T = c.TRAIN
TEST_STORE = c.FIVE + "test/store/"
TRAIN_STORE = T + "store/"
PINNED = T + "winner/pinned/"
OUTP = s7.D + "pilot/"
OUTO = s7.D + "out/"
FAILS = []
D0, D1 = 0, 9
SPLIT = "district_d%03d_d%03d" % (D0, D1)


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def sync():
    torch.cuda.synchronize()


def run_rows(draws, twins, seeds, hids, w):
    """campaign-style run rows for the given draws: one run = one twin in one draw."""
    rows = []
    for d in draws:
        a = dr.assign(seeds[d], twins, hids, w)
        for tid, cls, nd, r in twins:
            rows.append({"run_id": "es_madrid_%s_d%03d" % (tid, d), "country": "es", "climate_id": s7.CLIMATE, "building_id": tid, "class": cls,
                         "k": r["twin_k"], "n_floors": r["twin_floors"], "n_dwellings": str(nd), "draw": d, "placement": dr.placement(a[tid])})
    return rows


def main():
    t_start = time.time()
    dev = "cuda"
    os.makedirs(s7.STORE, exist_ok=True)
    os.makedirs(OUTP, exist_ok=True)
    os.makedirs(OUTO, exist_ok=True)
    print("GPU_PILOT host=%s gpu=%s torch=%s start=%s" % (os.uname()[1], torch.cuda.get_device_name(0), torch.__version__, time.strftime("%Y-%m-%dT%H:%M:%S")), flush=True)
    # ---- seals: every input sealed and unchanged, draws.json sealed BEFORE this job started (validation 3.2)
    seals = {}
    for ln in io.open(s7.IN + "SEALS.md5", encoding="utf-8"):
        q = ln.split()
        if len(q) == 2:
            seals[q[1]] = q[0]
    ok = all(nm in seals and seals[nm] == s7.md5(s7.IN + nm) for nm in ("sample_buildings.csv", "twins_es.csv", "twins_info_es.csv", "draws.json"))
    chk("sealed_inputs_unchanged", ok, "sealed files %s" % sorted(seals))
    chk("draws_json_written_before_this_job_started", os.path.getmtime(s7.IN + "draws.json") < t_start and seals.get("draws.json") == s7.md5(s7.IN + "draws.json"),
        "draws.json mtime %s, job start %s" % (time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(s7.IN + "draws.json"))), time.strftime("%H:%M:%S", time.localtime(t_start))))
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    seeds = dj["seeds"]
    hids, w, prow = dr.load_pool()
    twins = dr.load_twins()
    chk("pool_md5_equals_the_one_in_draws_json", s7.md5(s7.HH + "pool.csv") == dj["pool_csv_md5"])
    # ---- checkpoint (pinned S3), md5 as s6_pred_task
    ckp = PINNED + "best.pt"
    h = s7.md5(ckp)
    wj = json.load(open(T + "winner/winner.json"))
    rec_pin = open(PINNED + "best.pt.md5").read().split()[0]
    h3 = s7.md5(T + "ckpt/S/3/best.pt")
    print("CKPT_MD5 md5=%s winner.json=%s best.pt.md5=%s ckpt/S/3=%s" % (h, wj["ckpt_md5"], rec_pin, h3), flush=True)
    chk("S_md5_equals_winner_json_pin_file_and_grid_checkpoint_and_78271da9", h == wj["ckpt_md5"] == rec_pin == h3 and h.startswith("78271da9"))
    chk("S_is_config_S3_seed1", wj["config"]["id"] == "S3" and wj["config"]["seed"] == 1)
    ck = torch.load(ckp, map_location=dev, weights_only=False)
    cfg, ss = ck["config"], ck["static_stats"]
    chk("static_stats_has_zmin_zmax", all(k in ss for k in ("mean", "sd", "zmin", "zmax")))
    # ---- store files copied from the train store (md5 compared), as s6_store
    t0 = time.time()
    clim = c.climates()
    copies = ["norm.json", "static_cols.json"] + ["weather_%s.npy" % cid for cid in clim] + ["calendar_%s.npy" % cc for cc in c.COUNTRIES]
    bad = []
    for fn in copies:
        shutil.copyfile(TRAIN_STORE + fn, s7.STORE + fn)
        if s7.md5(TRAIN_STORE + fn) != s7.md5(s7.STORE + fn):
            bad.append(fn)
    chk("copies_equal_train_store_md5", not bad, "files=%d bad=%s" % (len(copies), bad))
    shutil.copyfile(TEST_STORE + "hh_it.npz", s7.STORE + "hh_it.npz")
    sc = json.load(open(s7.STORE + "static_cols.json"))
    # ---- households: the test store's Spanish rows first and unchanged, new pool households appended
    c.HHROOT = s7.POOL                                   # s5_store.read_hh / s6_store.read_hh_guarded read c.HHROOT at call time
    z = np.load(TEST_STORE + "hh_es.npz")
    base = {k: z[k] for k in z.files}
    hl = [str(x) for x in base["hid"]]
    hh_index = {"es": {hh: i for i, hh in enumerate(hl)}}
    new = sorted(hh for hh in hids if hh not in hh_index["es"])
    print("HOUSEHOLDS pool=%d already in the test store=%d new=%d" % (len(hids), len(hids) - len(new), len(new)), flush=True)
    got, missing = {}, []
    with mp.Pool(3) as pool:
        for cc, hid, val, st, lg in pool.imap_unordered(s6s.read_hh_guarded, [("es", x) for x in new], chunksize=16):
            if val is None:
                missing.append((hid, st))
            else:
                got[hid] = val
    chk("every_new_household_read", not missing, "new=%d read=%d missing=%s" % (len(new), len(got), missing[:3]))
    if missing:
        sys.exit(4)
    add = sorted(got)
    pres = np.stack([got[x][0] for x in add])
    frac = np.stack([got[x][1] for x in add])
    mem = np.array([got[x][2] for x in add], dtype=np.float32)
    dw = np.array([got[x][3] for x in add], dtype=np.float32)
    out = {"hid": np.concatenate([base["hid"], np.array(add)]), "presence": np.concatenate([base["presence"], pres]),
           "appl_frac": np.concatenate([base["appl_frac"], frac]), "people": np.concatenate([base["people"], (mem[:, None] * pres).astype(np.float32)]),
           "appl_w": np.concatenate([base["appl_w"], (dw[:, None] * frac).astype(np.float32)]), "members": np.concatenate([base["members"], mem]),
           "design_w": np.concatenate([base["design_w"], dw])}
    np.savez(s7.STORE + "hh_es.npz", **out)
    z2 = np.load(s7.STORE + "hh_es.npz")
    n0 = len(base["hid"])
    chk("hh_es_test_store_rows_unchanged_and_first", all(np.array_equal(z2[k][:n0], base[k]) for k in base) and len(z2["hid"]) == n0 + len(add), "base %d + new %d = %d" % (n0, len(add), len(z2["hid"])))
    for i, x in enumerate(add):
        hh_index["es"][x] = n0 + i
    nanc = sum(int((~np.isfinite(z2[k])).sum()) for k in ("presence", "appl_frac", "people", "appl_w", "members", "design_w"))
    chk("no_nan_in_households", nanc == 0, "nan=%d ; new presence range [%.3f, %.3f]" % (nanc, float(pres.min()), float(pres.max())))
    # the 60 campaign hids: the new reader reproduces the stored rows
    cam = [r["hid"] for r in prow if r["source"] == "campaign"][:3]
    same = True
    for x in cam:
        r_ = s5s.read_hh(("es", x))
        same = same and r_[2] is not None and np.array_equal(r_[2][0], z2["presence"][hh_index["es"][x]])
    chk("reader_reproduces_stored_rows_of_3_campaign_households", same)
    # ---- run rows and flats
    bt = {r["building_id"]: r for r in s7.read_csv(s7.CAMP_IN + "buildings_es_it.csv")}
    for r in s7.read_csv(s7.TWINS_CSV):
        bt[r["building_id"]] = r
    arch = {"es": {r["Code_Building"]: r for r in s5s.mz._s8.load_rows(c.CAMP + "in/", "es")[0]}}
    acols, _sk = c.archetype_numeric_columns()
    geom_cache = {}

    def geom(row):
        code = row["Code_Building"]
        if code not in geom_cache:
            d = s5s.mz.derive(row)
            geom_cache[code] = (d["width"], d["depth"], d["n_storey"], d["a_ref"])
        return geom_cache[code]
    flags_bad = {"nf_bad": [], "nd_bad": [], "area_bad": []}

    def build(rows):
        recs = []
        for r in sorted(rows, key=lambda x: x["run_id"]):
            rr, fl = s6s.flat_records(r["run_id"], r, dr_plc(r), bt, arch, acols, clim, geom, hh_index)
            for k in fl:
                if fl[k]:
                    flags_bad[k].append(r["run_id"])
            recs.extend(rr)
        return pd.DataFrame(recs)

    def dr_plc(r):
        return {int(j): t for j, t in (it.split(":", 1) for it in r["placement"].split(";"))}
    # reproduction: this builder against the Step 5 drivers of 3 development runs (exact), seen failing with a planted hh_index change
    trf = pd.read_parquet(TRAIN_STORE + "flats_development.parquet")
    camp = {r["run_id"]: r for r in s7.read_csv(s7.CAMP_IN + "campaign_runs_es.csv")}
    pick = []
    for cls in ("SFH", "MFH", "AB"):
        ids = sorted(trf[(trf["country"] == "es") & (trf["class"] == cls)]["run_id"].unique())
        pick.append(ids[len(ids) // 2])
    mine = build([camp[x] for x in pick])
    ref = trf[trf["run_id"].isin(pick)].sort_values("run_id", kind="stable").reset_index(drop=True)
    try:
        pd.testing.assert_frame_equal(mine.reset_index(drop=True), ref, check_exact=True, check_dtype=False)
        eq = True
    except AssertionError as e:
        eq = False
        print("DIFF", str(e)[:300])
    chk("builder_reproduces_Step5_development_drivers_for_3_runs_exactly", eq, "runs %s rows %d" % (pick, len(ref)))
    mb = mine.copy()
    mb.loc[0, "hh_index"] = int(mb.loc[0, "hh_index"]) + 1
    try:
        pd.testing.assert_frame_equal(mb.reset_index(drop=True), ref, check_exact=True, check_dtype=False)
        caught = False
    except AssertionError:
        caught = True
    chk("planted_hh_index_change_CAUGHT (seen failing)", caught)
    flags_bad = {"nf_bad": [], "nd_bad": [], "area_bad": []}
    draws = list(range(D0, D1 + 1))
    rows = run_rows(draws, twins, seeds, hids, w)
    fl = build(rows)
    t_store = time.time() - t0
    fl.to_parquet(s7.STORE + "flats_%s.parquet" % SPLIT, index=False)
    chk("flats_runs_equal_twins_x_draws", fl["run_id"].nunique() == len(rows) == 100 * len(draws), "runs=%d rows=%d" % (fl["run_id"].nunique(), len(fl)))
    chk("twin_floors_dwellings_area_equal_TABULA_geometry", not any(flags_bad.values()), "nf=%d nd=%d area=%d" % tuple(len(flags_bad[k]) for k in ("nf_bad", "nd_bad", "area_bad")))
    trcols = list(pd.read_parquet(TEST_STORE + "flats_test_both_new.parquet").columns)
    chk("columns_identical_to_the_test_store_flats", list(fl.columns) == trcols, "n=%d" % len(trcols))
    chk("static_columns_identical_to_static_cols_json", [x for x in fl.columns if x.startswith("s_")] == sc["static"] and [x for x in fl.columns if x.startswith("c_")] == sc["climate_onehot"])
    ok_f, badn = c.check_features([x for x in fl.columns if x.startswith("s_") or x.startswith("c_")])
    chk("check_features_static_names", ok_f, "forbidden=%s" % badn)
    chk("no_nan_in_flats_static", int(fl[sc["static"] + sc["climate_onehot"]].isna().sum().sum()) == 0)
    chk("no_targets_file_in_district_store", not any(fn.startswith("targets") for fn in os.listdir(s7.STORE)), "files=%s" % sorted(os.listdir(s7.STORE)))
    dwy = len(fl)
    print("STORE_BUILT rows=%d dwelling-years=%d seconds=%.1f (copies + households + flats, CPU)" % (dwy, dwy, t_store), flush=True)
    # ---- per-twin range (same arithmetic as s6_data.Data)
    d0 = fl[fl["run_id"].str.endswith("_d%03d" % D0)]
    S = d0[sc["static"]].to_numpy(dtype=np.float64)
    zz = (S - np.array(ss["mean"])) / np.array(ss["sd"])
    outside = (zz < np.array(ss["zmin"])) | (zz > np.array(ss["zmax"]))
    rng_rows = []
    for tid, cls, nd, r in twins:
        m = (d0["building_id"] == tid).to_numpy()
        o = outside[m]
        cols = [sc["static"][i] for i in range(len(sc["static"])) if o[:, i].any()]
        n_out = int(o.any(1).sum())
        print("STATIC_CLIP_TWIN %s class=%s code=%s dwellings=%d clipped_dwellings=%d columns=%s" % (tid, cls, r["code"], int(m.sum()), n_out, ",".join(cols) or "-"))
        rng_rows.append([tid, cls, r["code"], r["code_seen_in_dev_buildings"], int(m.sum()), n_out, "out_of_range" if n_out else "in_range", ";".join(cols)])
    s7.write_csv(OUTO + "twin_range_es.csv", ["twin_id", "class", "code", "code_seen_in_dev_buildings", "dwellings", "clipped_dwellings", "range", "columns_clipped"], rng_rows)
    n_oor = sum(1 for r in rng_rows if r[6] == "out_of_range")
    print("RANGE twins in_range=%d out_of_range=%d ; out-of-range twins: %s" % (len(rng_rows) - n_oor, n_oor, [r[0] for r in rng_rows if r[6] == "out_of_range"]), flush=True)
    print("RANGE dwellings clipped in draw %d: %d of %d" % (D0, int(outside.any(1).sum()), len(outside)), flush=True)
    # ---- load (timed): Data + model
    sync()
    t1 = time.time()
    sd6.TEST_STORE = s7.STORE
    sd6.TEST_LISTS = (SPLIT,)
    dv = sd6.Data(SPLIT, dev, stats=ss, load_targets=False, drop_climate=bool(cfg.get("no_climate", False)), country=None, blind=False, store=s7.STORE)
    model = sm.build_model(cfg, dv.n_dyn, dv.S).to(dev)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    sync()
    t_load = time.time() - t1
    print("DATA_LOADED rows=%d runs=%d STATIC_CLIP_RECORD values_clipped=%d columns=%s seconds=%.1f" % (len(dv.flats), dv.flats["run_id"].nunique(), dv.clip_info["values_clipped"], dv.clip_info["columns_clipped"], t_load), flush=True)
    chk("data_class_clipped_value_count_equals_my_per_twin_count_times_draws", dv.clip_info["values_clipped"] == int(outside.sum()) * len(draws),
        "Data %d ; mine %d x %d draws (static vectors do not depend on the household)" % (dv.clip_info["values_clipped"], int(outside.sum()), len(draws)))
    # ---- predict (timed) and write (timed), as s5_predict.predict_runs
    fl2 = dv.flats
    rid_col = fl2["run_id"].to_numpy()
    uniq, first, cnt = np.unique(rid_col, return_index=True, return_counts=True)
    start, ndr = dict(zip(uniq, first)), dict(zip(uniq, cnt))
    outdir = OUTP + "pred_S3"
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    sums = {d: np.zeros((c.H, 4)) for d in draws}
    ann_dw = []
    t_pred = t_write = 0.0
    nfiles = 0
    with torch.no_grad():
        for rid in list(uniq):
            s0, nd = int(start[rid]), int(ndr[rid])
            sync()
            ta = time.time()
            rows_t = torch.arange(s0, s0 + nd, device=dev).repeat_interleave(sd6.NDAY)
            days = torch.arange(sd6.NDAY, device=dev).repeat(nd)
            outs = []
            for i in range(0, len(rows_t), 2048):
                x, st, _ = dv.windows(rows_t[i:i + 2048], days[i:i + 2048], with_y=False)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    o = model(x, st)
                o = torch.maximum(o.float(), dv.lo)
                outs.append(o * dv.tsd + dv.tmu)
            o = torch.cat(outs, 0)
            o = torch.clamp(o, min=0.0).reshape(nd, sd6.NDAY * 24, 3).double().cpu().numpy()
            arr = np.concatenate([o, (o[:, :, 2] + (o[:, :, 0] + o[:, :, 1]) / c.COP)[:, :, None]], 2)
            sync()
            tb = time.time()
            t_pred += tb - ta
            sp.write_pred(outdir, fl2["climate_id"].iloc[s0], rid, arr, "Step 7 district pilot, config %s, pinned S3 %s, clipped at 0 kWh" % (cfg.get("id"), h))
            t_write += time.time() - tb
            nfiles += 1
            d = int(str(rid).rsplit("_d", 1)[1])
            sums[d] += arr.sum(0)
            ann_dw.append((rid, arr.sum(1)))
            if nfiles % 100 == 0:
                s7.stamp("predicted %d of %d runs" % (nfiles, len(uniq)))
    dwyr = len(fl2)
    t_tot = t_load + t_pred + t_write
    print("TIMING node=%s gpu=%s dwelling_years=%d" % (os.uname()[1], torch.cuda.get_device_name(0), dwyr))
    print("TIMING_S_PER_DWELLING_YEAR load=%.5f predict=%.5f write=%.5f total=%.5f   (seconds: load %.1f predict %.1f write %.1f ; store build on CPU %.1f s, not in the total)" %
          (t_load / dwyr, t_pred / dwyr, t_write / dwyr, t_tot / dwyr, t_load, t_pred, t_write, t_store), flush=True)
    chk("files_written_one_per_run", nfiles == 100 * len(draws), "files=%d" % nfiles)
    # ---- output checks and district sums
    ar = np.concatenate([a for _r, a in ann_dw], 0)
    chk("predictions_finite_nonneg_annual", bool(np.isfinite(ar).all() and (ar >= 0).all()), "dwelling-years=%d annual kWh mean heat/cool/equip/total = %s" % (len(ar), np.round(ar.mean(0), 1).tolist()))
    one = pd.read_csv("%s/%s/%s.csv.gz" % (outdir, s7.CLIMATE, uniq[0]), comment="#", compression="gzip")
    chk("one_written_file_has_8760_rows_per_dwelling", len(one) == 8760 * int(ndr[uniq[0]]) and np.isfinite(one[c.TARGETS].to_numpy()).all(), "%s rows=%d" % (uniq[0], len(one)))
    tot = np.stack([sums[d] for d in draws])
    np.savez(OUTP + "district_sums_d%03d_d%03d.npz" % (D0, D1), draws=np.array(draws), hourly=tot)
    ann = tot.sum(1)
    pk = tot.max(1)
    for i, d in enumerate(draws):
        print("DISTRICT draw %d annual kWh heat=%.0f cool=%.0f equip=%.0f total=%.0f ; peak-hour kWh heat=%.1f cool=%.1f equip=%.1f total=%.1f" % (d, *ann[i], *pk[i]))
    chk("two_draws_with_different_seeds_give_different_district_totals (validation 1.3)", abs(ann[0, 2] - ann[1, 2]) > 1e-6 and len(set(np.round(ann[:, 3], 3))) == len(draws), "equipment annual draw0=%.1f draw1=%.1f" % (ann[0, 2], ann[1, 2]))
    # ---- N by R7-3
    dw_draw = sum(t[2] for t in twins)
    tpd = t_tot / dwyr
    tpd_np = (t_load + t_pred) / dwyr
    lines = []
    chosen = None
    for n in (1000, 500, 200):
        sh = n * dw_draw * tpd / 3600.0
        sh2 = n * dw_draw * tpd_np / 3600.0
        fits = sh <= 24.0
        lines.append("N=%d slice_hours(load+predict+write)=%.2f  (without per-dwelling write %.2f)  fits_24_slice_hours=%s  wall_on_4_slices_h=%.2f" % (n, sh, sh2, fits, sh / 4.0))
        if fits and chosen is None:
            chosen = n
    for ln in lines:
        print("N_RULE " + ln)
    if chosen is None:
        chosen = 200
        print("N_RULE none of 1000/500/200 fits 24 slice-hours with per-dwelling write; N=200 taken (smallest)")
    print("N_CHOSEN %d (district dwellings per draw %d ; strict reading: 24 GPU slice-hours in total)" % (chosen, dw_draw))
    io.open(OUTP + "n_chosen.txt", "w").write("%d\n" % chosen)
    print("SUMMARY fails=%d %s total_seconds=%.0f" % (len(FAILS), FAILS, time.time() - t_start))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
