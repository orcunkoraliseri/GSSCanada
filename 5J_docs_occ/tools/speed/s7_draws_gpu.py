# -*- coding: utf-8 -*-
"""5J Step 7 part B code (Speed job; Spain only; never a UK file): the district draw writer.
usage:  s7_draws_gpu.py time            draws 0-9, timed (load / predict / district write separated), N rule  (1 A100 slice)
        s7_draws_gpu.py run             draws of this array task (SLURM_ARRAY_TASK_ID t: draws 50(t-1) .. 50t-1, capped at N)  (1 A100 slice)
        s7_draws_gpu.py hourly          the 20 check draws: per-dwelling HOURLY predictions (pilot writer) into district/pred_check/ (1 slice)
        s7_draws_gpu.py cpu             draw 0 on ONE CPU core (threads 1), district writer, timed; writes under district/draws_cpu/
Per draw the DISTRICT writer saves ONE file draws/d<DDDD>.npz: hourly_all (8760 x 4), hourly_inrange (8760 x 4), annual per dwelling (n x 4),
twin_idx, dwelling, hid; targets = heating, cooling, equipment, total_elec (kWh). Per-dwelling hourly files are NOT written (R7-3 addendum).
Same prediction path as the part A pilot (s7_gpu_pilot.py, unchanged): store of Step 6 part A (s6_store.flat_records), pinned S3 (md5 78271da9...),
bf16 autocast on the GPU, chunks of 2048 windows, clip at 0 kWh, total_elec = equipment + (heating + cooling)/3.0."""
import contextlib, io, json, os, shutil, sys, time
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

WRITER = "s7_draws_gpu v1 2026-10-01"
T = c.TRAIN
TEST_STORE = c.FIVE + "test/store/"
TRAIN_STORE = T + "store/"
PINNED = T + "winner/pinned/"
OUTO = s7.D + "out/"
DRAWS = s7.D + "draws/"
PRED_CHECK = s7.D + "pred_check/"
FAILS = []
PER_TASK = 50
H = c.H


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def sync(dev):
    if dev == "cuda":
        torch.cuda.synchronize()


def draw_path(d, root=DRAWS):
    return "%sd%04d.npz" % (root, d)


def valid_draw_file(path, d, seed):
    if not os.path.exists(path):
        return False
    try:
        z = np.load(path)
        return str(z["writer"]) == WRITER and int(z["draw"]) == d and int(z["seed"]) == seed and z["hourly_all"].shape == (H, 4)
    except Exception:
        return False


def write_draw_file(path, d, seed, ha, hi, ann, tidx, dwl, hidl):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        np.savez(f, writer=np.array(WRITER), draw=np.array(d), seed=np.array(seed, dtype=np.int64), hourly_all=ha, hourly_inrange=hi, annual=ann,
                 twin_idx=np.array(tidx, dtype=np.int16), dwelling=np.array(dwl, dtype=np.int16), hid=np.array(hidl))
    os.replace(tmp, path)


def setup(dev):
    """Everything built once per job. Sealed inputs are checked first."""
    ctx = {}
    seals = {}
    for ln in io.open(s7.IN + "SEALS.md5", encoding="utf-8"):
        q = ln.split()
        if len(q) == 2:
            seals[q[1]] = q[0]
    ok = all(nm in seals and seals[nm] == s7.md5(s7.IN + nm) for nm in ("sample_buildings.csv", "twins_es.csv", "twins_info_es.csv", "draws.json", "district_runs_es.csv", "district_runs_es_pilot.csv"))
    chk("sealed_inputs_unchanged", ok, "sealed files %s" % sorted(seals))
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    ctx["seeds"], ctx["check"] = dj["seeds"], dj["check_indices"]
    ctx["hids"], ctx["w"], ctx["prow"] = dr.load_pool()
    ctx["twins"] = dr.load_twins()
    chk("pool_md5_equals_the_one_in_draws_json", s7.md5(s7.HH + "pool.csv") == dj["pool_csv_md5"])
    ckp = PINNED + "best.pt"
    h = s7.md5(ckp)
    wj = json.load(open(T + "winner/winner.json"))
    rec_pin = open(PINNED + "best.pt.md5").read().split()[0]
    h3 = s7.md5(T + "ckpt/S/3/best.pt")
    print("CKPT_MD5 md5=%s winner.json=%s best.pt.md5=%s ckpt/S/3=%s" % (h, wj["ckpt_md5"], rec_pin, h3), flush=True)
    chk("S_md5_equals_winner_json_pin_file_and_grid_checkpoint_and_78271da9", h == wj["ckpt_md5"] == rec_pin == h3 and h.startswith("78271da9"))
    chk("S_is_config_S3_seed1", wj["config"]["id"] == "S3" and wj["config"]["seed"] == 1)
    ck = torch.load(ckp, map_location=dev, weights_only=False)
    ctx["ck"], ctx["cfg"], ctx["ss"], ctx["h"] = ck, ck["config"], ck["static_stats"], h
    chk("static_stats_has_zmin_zmax", all(k in ctx["ss"] for k in ("mean", "sd", "zmin", "zmax")))
    clim = c.climates()
    ctx["clim"] = clim
    copies = ["norm.json", "static_cols.json"] + ["weather_%s.npy" % cid for cid in clim] + ["calendar_%s.npy" % cc for cc in c.COUNTRIES]
    bad = [fn for fn in copies if s7.md5(TRAIN_STORE + fn) != s7.md5(s7.STORE + fn)]
    chk("shared_store_files_equal_train_store_md5 (read only, written by part A)", not bad, "files=%d bad=%s" % (len(copies), bad))
    chk("hh_it_equals_test_store", s7.md5(TEST_STORE + "hh_it.npz") == s7.md5(s7.STORE + "hh_it.npz"))
    z = np.load(s7.STORE + "hh_es.npz")
    hl = [str(x) for x in z["hid"]]
    ctx["hh_index"] = {"es": {hh: i for i, hh in enumerate(hl)}}
    print("HH_ES_NPZ md5=%s hids=%d" % (s7.md5(s7.STORE + "hh_es.npz"), len(hl)), flush=True)
    chk("every_pool_household_is_in_hh_es_npz", all(x in ctx["hh_index"]["es"] for x in ctx["hids"]), "pool=%d" % len(ctx["hids"]))
    ctx["sc"] = json.load(open(s7.STORE + "static_cols.json"))
    ctx["range"] = {r["twin_id"]: r["range"] for r in s7.read_csv(OUTO + "twin_range_es.csv")}
    chk("range_file_covers_100_twins", len(ctx["range"]) == 100 and all(t[0] in ctx["range"] for t in ctx["twins"]))
    # builder pieces (as the pilot)
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
            plc = {int(j): t for j, t in (it.split(":", 1) for it in r["placement"].split(";"))}
            rr, fl = s6s.flat_records(r["run_id"], r, plc, bt, arch, acols, clim, geom, ctx["hh_index"])
            for k in fl:
                if fl[k]:
                    flags_bad[k].append(r["run_id"])
            recs.extend(rr)
        return pd.DataFrame(recs)
    ctx["build"], ctx["flags_bad"] = build, flags_bad
    return ctx


def run_rows(ctx, draws):
    rows = []
    for d in draws:
        a = dr.assign(ctx["seeds"][d], ctx["twins"], ctx["hids"], ctx["w"])
        for tid, cls, nd, r in ctx["twins"]:
            rows.append({"run_id": "es_madrid_%s_d%03d" % (tid, d), "country": "es", "climate_id": s7.CLIMATE, "building_id": tid, "class": cls,
                         "k": r["twin_k"], "n_floors": r["twin_floors"], "n_dwellings": str(nd), "draw": d, "placement": dr.placement(a[tid])})
    return rows


def split_rid(rid):
    head, d = rid.rsplit("_d", 1)
    return head[len("es_madrid_"):], int(d)


def process(ctx, draws, tag, mode, dev, outroot):
    """mode 'district': district writer -> outroot/d<DDDD>.npz ; mode 'hourly': per-dwelling hourly files -> outroot. Returns timing dict."""
    twins, sc, ss, cfg, h, seeds = ctx["twins"], ctx["sc"], ctx["ss"], ctx["cfg"], ctx["h"], ctx["seeds"]
    tmap = {t[0]: i for i, t in enumerate(twins)}
    t0 = time.time()
    ctx["flags_bad"].update({"nf_bad": [], "nd_bad": [], "area_bad": []})
    rows = run_rows(ctx, draws)
    fl = ctx["build"](rows)
    fl.to_parquet(s7.STORE + "flats_%s.parquet" % tag, index=False)
    t_store = time.time() - t0
    chk("[%s] flats_runs_equal_twins_x_draws" % tag, fl["run_id"].nunique() == len(rows) == 100 * len(draws), "runs=%d rows=%d" % (fl["run_id"].nunique(), len(fl)))
    chk("[%s] twin_floors_dwellings_area_equal_TABULA_geometry" % tag, not any(ctx["flags_bad"].values()), "nf=%d nd=%d area=%d" % tuple(len(ctx["flags_bad"][k]) for k in ("nf_bad", "nd_bad", "area_bad")))
    trcols = list(pd.read_parquet(TEST_STORE + "flats_test_both_new.parquet").columns)
    chk("[%s] columns_identical_to_the_test_store_flats" % tag, list(fl.columns) == trcols, "n=%d" % len(trcols))
    ok_f, badn = c.check_features([x for x in fl.columns if x.startswith("s_") or x.startswith("c_")])
    chk("[%s] check_features_static_names" % tag, ok_f, "forbidden=%s" % badn)
    chk("[%s] no_nan_in_flats_static" % tag, int(fl[sc["static"] + sc["climate_onehot"]].isna().sum().sum()) == 0)
    # per-twin range from this table (same arithmetic as s6_data.Data) against the part A range file
    d0 = fl[fl["run_id"].str.endswith("_d%03d" % draws[0])]
    S = d0[sc["static"]].to_numpy(dtype=np.float64)
    outside = (((S - np.array(ss["mean"])) / np.array(ss["sd"])) < np.array(ss["zmin"])) | (((S - np.array(ss["mean"])) / np.array(ss["sd"])) > np.array(ss["zmax"]))
    mine = {}
    for tid, cls, nd, r in twins:
        m = (d0["building_id"] == tid).to_numpy()
        mine[tid] = "out_of_range" if int(outside[m].any(1).sum()) else "in_range"
    chk("[%s] twin_range_equals_part_A_range_file" % tag, mine == ctx["range"], "out_of_range twins %d" % sum(1 for v in mine.values() if v == "out_of_range"))
    inr = {tid: (ctx["range"][tid] == "in_range") for tid in ctx["range"]}
    sync(dev)
    t1 = time.time()
    sd6.TEST_STORE = s7.STORE
    sd6.TEST_LISTS = (tag,)
    dv = sd6.Data(tag, dev, stats=ss, load_targets=False, drop_climate=bool(cfg.get("no_climate", False)), country=None, blind=False, store=s7.STORE)
    model = sm.build_model(cfg, dv.n_dyn, dv.S).to(dev)
    model.load_state_dict(ctx["ck"]["state_dict"])
    model.eval()
    sync(dev)
    t_load = time.time() - t1
    print("DATA_LOADED [%s] rows=%d runs=%d values_clipped=%d seconds=%.1f" % (tag, len(dv.flats), dv.flats["run_id"].nunique(), dv.clip_info["values_clipped"], t_load), flush=True)
    chk("[%s] Data_clipped_value_count_equals_my_count_times_draws" % tag, dv.clip_info["values_clipped"] == int(outside.sum()) * len(draws), "Data %d ; mine %d x %d" % (dv.clip_info["values_clipped"], int(outside.sum()), len(draws)))
    fl2 = dv.flats
    uniq, first, cnt = np.unique(fl2["run_id"].to_numpy(), return_index=True, return_counts=True)
    start, ndr = dict(zip(uniq, first)), dict(zip(uniq, cnt))
    ha = {d: np.zeros((H, 4)) for d in draws}
    hi = {d: np.zeros((H, 4)) for d in draws}
    ann = {}
    t_pred = t_write = 0.0
    nfiles = 0
    if mode == "hourly":
        if os.path.exists(outroot):
            shutil.rmtree(outroot)
    ctxm = (lambda: torch.autocast("cuda", dtype=torch.bfloat16)) if dev == "cuda" else (lambda: contextlib.nullcontext())
    with torch.no_grad():
        for rid in list(uniq):
            s0, nd = int(start[rid]), int(ndr[rid])
            sync(dev)
            ta = time.time()
            rows_t = torch.arange(s0, s0 + nd, device=dev).repeat_interleave(sd6.NDAY)
            days = torch.arange(sd6.NDAY, device=dev).repeat(nd)
            outs = []
            for i in range(0, len(rows_t), 2048):
                x, st, _ = dv.windows(rows_t[i:i + 2048], days[i:i + 2048], with_y=False)
                with ctxm():
                    o = model(x, st)
                o = torch.maximum(o.float(), dv.lo)
                outs.append(o * dv.tsd + dv.tmu)
            o = torch.cat(outs, 0)
            o = torch.clamp(o, min=0.0).reshape(nd, sd6.NDAY * 24, 3).double().cpu().numpy()
            arr = np.concatenate([o, (o[:, :, 2] + (o[:, :, 0] + o[:, :, 1]) / c.COP)[:, :, None]], 2)
            tb = time.time()
            t_pred += tb - ta
            tid, d = split_rid(rid)
            if mode == "hourly":
                sp.write_pred(outroot, fl2["climate_id"].iloc[s0], rid, arr, "Step 7 district check draw, config %s, pinned S3 %s, clipped at 0 kWh" % (cfg.get("id"), h))
                t_write += time.time() - tb
            else:
                # accumulation for the district writer: part of the district-write cost
                s_ = arr.sum(0)
                ha[d] += s_
                if inr[tid]:
                    hi[d] += s_
                ann[(d, tid)] = arr.sum(1)
                t_write += time.time() - tb
            nfiles += 1
            if nfiles % 200 == 0:
                s7.stamp("[%s] predicted %d of %d runs" % (tag, nfiles, len(uniq)))
    t_dwrite = 0.0
    if mode == "district":
        tc = time.time()
        os.makedirs(outroot, exist_ok=True)
        for d in draws:
            a = dr.assign(seeds[d], twins, ctx["hids"], ctx["w"])
            tidx, dwl, hidl, rowsA = [], [], [], []
            for tid, cls, nd, r in twins:
                rowsA.append(ann[(d, tid)])
                tidx += [tmap[tid]] * nd
                dwl += list(range(nd))
                hidl += list(a[tid])
            write_draw_file(draw_path(d, outroot), d, seeds[d], ha[d], hi[d], np.concatenate(rowsA, 0), tidx, dwl, hidl)
        t_dwrite = time.time() - tc
    dwy = len(fl2)
    node = os.uname()[1]
    devname = torch.cuda.get_device_name(0) if dev == "cuda" else "cpu(%d thread)" % torch.get_num_threads()
    chk("[%s] files_or_runs_done_equal_runs" % tag, nfiles == 100 * len(draws), "runs=%d" % nfiles)
    tot = t_load + t_pred + t_write + t_dwrite
    print("SPEED_S mode=%s tag=%s node=%s device=%s dwy=%d store_s=%.2f load_s=%.2f predict_s=%.2f accumulate_or_hourly_write_s=%.2f district_write_s=%.2f total_incl_load_s=%.2f" %
          (mode, tag, node, devname, dwy, t_store, t_load, t_pred, t_write, t_dwrite, tot), flush=True)
    print("SPEED_S_PER_DWY mode=%s tag=%s load=%.5f predict=%.5f accumulate_or_hourly_write=%.5f district_write=%.5f total=%.5f   (store build on CPU %.1f s is NOT in the total)" %
          (mode, tag, t_load / dwy, t_pred / dwy, t_write / dwy, t_dwrite / dwy, tot / dwy, t_store), flush=True)
    return {"dwy": dwy, "load": t_load, "predict": t_pred, "write": t_write, "dwrite": t_dwrite, "store": t_store, "ha": ha, "ann": ann, "fl": fl}


def n_rule(ctx, tm):
    dw_draw = sum(t[2] for t in ctx["twins"])
    tpd = (tm["load"] + tm["predict"] + tm["write"] + tm["dwrite"]) / tm["dwy"]
    chosen = None
    for n in (1000, 500, 200):
        sh = n * dw_draw * tpd / 3600.0
        fits = sh <= 24.0
        print("N_RULE N=%d slice_hours(load+predict+district write)=%.2f fits_24_slice_hours=%s wall_on_4_slices_h=%.2f" % (n, sh, fits, sh / 4.0))
        if fits and chosen is None:
            chosen = n
    if chosen is None:
        chosen = 200
        print("N_RULE none of 1000/500/200 fits 24 slice-hours; N=200 taken (smallest)")
    print("N_CHOSEN %d (district dwellings per draw %d ; %.5f s per dwelling-year ; strict reading: 24 GPU slice-hours in total)" % (chosen, dw_draw, tpd))
    return chosen


def main():
    mode = sys.argv[1]
    dev = "cpu" if mode == "cpu" else "cuda"
    if mode == "cpu":
        torch.set_num_threads(1)
    t_start = time.time()
    print("DRAWS_GPU mode=%s host=%s device=%s torch=%s threads=%d start=%s writer=%s" % (mode, os.uname()[1], torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", torch.__version__, torch.get_num_threads(), time.strftime("%Y-%m-%dT%H:%M:%S"), WRITER), flush=True)
    os.makedirs(OUTO, exist_ok=True)
    ctx = setup(dev)
    if FAILS:
        print("SUMMARY fails=%d %s (setup)" % (len(FAILS), FAILS))
        sys.exit(1)
    if mode == "time":
        draws = list(range(0, 10))
        tm = process(ctx, draws, "t_d000_d009", "district", dev, DRAWS)
        # draws 0-9 against part A: flats identical to the pilot store file; district hourly totals equal to the pilot's in-memory sums
        a = pd.read_parquet(s7.STORE + "flats_t_d000_d009.parquet").reset_index(drop=True)
        b = pd.read_parquet(s7.STORE + "flats_district_d000_d009.parquet").reset_index(drop=True)
        try:
            pd.testing.assert_frame_equal(a, b, check_exact=True)
            eq = True
        except AssertionError as e:
            eq = False
            print("DIFF", str(e)[:300])
        chk("flats_of_draws_0_9_equal_part_A_flats_exactly", eq, "rows %d" % len(a))
        pz = np.load(s7.D + "pilot/district_sums_d000_d009.npz")
        mx = 0.0
        for i, d in enumerate(draws):
            z = np.load(draw_path(d))
            ref = pz["hourly"][list(pz["draws"]).index(d)]
            mx = max(mx, float((np.abs(z["hourly_all"] - ref).sum(0) / np.abs(ref).sum(0)).max()))
        chk("district_hourly_totals_draws_0_9_equal_pilot_in_memory_sums_rel_1e-6", mx <= 1e-6, "max relative annual-sum difference %.2e" % mx)
        ann = np.stack([np.load(draw_path(d))["hourly_all"].sum(0) for d in draws])
        for i, d in enumerate(draws):
            z = np.load(draw_path(d))
            print("DISTRICT draw %d annual kWh heat=%.0f cool=%.0f equip=%.0f total=%.0f ; peak-hour kWh heat=%.1f cool=%.1f equip=%.1f total=%.1f ; annual rows %d" % (d, *ann[i], *z["hourly_all"].max(0), len(z["annual"])))
        chk("draw_annual_equals_sum_of_per_dwelling_annual", all(np.allclose(np.load(draw_path(d))["annual"].sum(0), np.load(draw_path(d))["hourly_all"].sum(0), rtol=1e-9) for d in draws))
        chk("two_draws_with_different_seeds_give_different_district_totals (validation 1.3)", len(set(np.round(ann[:, 3], 3))) == len(draws))
        n = n_rule(ctx, tm)
        io.open(OUTO + "n_chosen_B.txt", "w").write("%d\n" % n)
    elif mode == "run":
        t = int(os.environ["SLURM_ARRAY_TASK_ID"])
        N = int(io.open(OUTO + "n_chosen_B.txt").read().split()[0])
        lo, hi = PER_TASK * (t - 1), min(PER_TASK * t, N)
        print("TASK t=%d N=%d draws %d..%d" % (t, N, lo, hi - 1), flush=True)
        todo = [d for d in range(lo, hi) if not valid_draw_file(draw_path(d), d, ctx["seeds"][d])]
        print("TASK draws already written by this writer (skipped): %s" % [d for d in range(lo, hi) if d not in todo], flush=True)
        if todo:
            process(ctx, todo, "w_d%04d_d%04d" % (todo[0], todo[-1]), "district", dev, DRAWS)
        chk("all_draws_of_this_task_written_and_valid", all(valid_draw_file(draw_path(d), d, ctx["seeds"][d]) for d in range(lo, hi)), "draws %d..%d" % (lo, hi - 1))
    elif mode == "hourly":
        draws = list(ctx["check"])
        process(ctx, draws, "h_check20", "hourly", dev, PRED_CHECK)
        n = sum(1 for _ in os.listdir(PRED_CHECK + s7.CLIMATE))
        chk("hourly_files_written_2000", n == 2000, "files=%d" % n)
    elif mode == "cpu":
        draws = [0]
        process(ctx, draws, "c_d000", "district", dev, s7.D + "draws_cpu/")
    print("SUMMARY fails=%d %s total_seconds=%.0f" % (len(FAILS), FAILS, time.time() - t_start))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
