# -*- coding: utf-8 -*-
"""5J Step 6 part A/B: the DRIVERS store of the three test lists (Speed job only; Spain + Italy only; never a UK file).
Writes /speed-scratch/o_iseri/5J/test/store/ : flats_<list>.parquet for the three test lists (same columns and same record code as
s5_store.py: see flat_records), hh_<cc>.npz (copy of the train store's rows, unchanged and first, + the households of the test pools
appended), norm.json, static_cols.json, weather_<climate>.npy, calendar_<cc>.npy (all COPIED from the train store, md5 compared).
NO targets file. Every file read goes through s6_common.open_driver (kind 'driver'); the end check on the open log is in s6_checks.py.
The record builder is a function copy of the loop body of s5_store.main; its equality with the train store is CHECKED here on 60
development and 60 validation runs (exact frame equality against flats_development / flats_validation of the train store)."""
import sys, os, io, json, math, time, shutil, hashlib, csv, importlib
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import multiprocessing as mp
import s6_common as s6
import s5_common as c
import s5_store as s5s            # read_hh, norm_tok, mz (the same builder module the campaign used); main() is not called

OUT = s6.TSTORE
RES = []
LOG = []


def chk(name, ok, text=""):
    RES.append((name, bool(ok)))
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)


def stamp(s):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), s), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_hh_guarded(task):
    """s5_store.read_hh on a household folder, after the driver guard on its three files (kind driver)."""
    cc, hid = task
    d = "%s%s_%s/" % (c.HHROOT, cc, hid)
    log = []
    try:
        s6.open_driver(d + "household.json", log)
        j = json.load(io.open(d + "household.json", encoding="utf-8"))
        s6.open_driver(d + j["presence_file"], log)
        s6.open_driver(d + j["elec_file"], log)
    except Exception as e:
        return (cc, hid, None, "guard/json error %s" % str(e)[:120], log)
    r = s5s.read_hh(task)
    return (r[0], r[1], r[2], r[3], log)


def flat_records(rid, r, plc, bt, arch, acols, clim, geom, hh_index):
    """Function copy of the per-run loop body of s5_store.main (same arithmetic, same column order). Returns (records, flags)."""
    cc, cls = r["country"], r["class"]
    nd, k, F = int(r["n_dwellings"]), int(r["k"]), int(r["n_floors"])
    b = bt[r["building_id"]]
    row = arch[cc][b["archetype_code"]]
    W, D, nst, aref = geom(row)
    spans = cls in ("SFH", "TH")
    flags = {"nf_bad": abs(nst - F) > 1e-9, "nd_bad": (spans and nd != 1) or ((not spans) and nd != F * k)}
    area = W * D * nst if spans else W * D / k
    flags["area_bad"] = abs(area * nd - aref) > 1e-6 * aref
    aval = {}
    for col in acols:
        v = row[col].strip()
        aval["s_" + col.lower()] = float(v) if v != "" else 0.0
    nrad = math.radians(float(b["north_axis_deg"]))
    floor_of = [0 if spans else j // k for j in range(nd)]
    recs = []
    for j in range(nd):
        f = floor_of[j]
        same = [g for g in range(nd) if floor_of[g] == f and g != j] if not spans else []
        above = [g for g in range(nd) if floor_of[g] == f + 1] if not spans else []
        below = [g for g in range(nd) if floor_of[g] == f - 1] if not spans else []
        hid = s5s.norm_tok(plc[j], cc)
        rec = {"run_id": rid, "country": cc, "climate_id": r["climate_id"], "building_id": r["building_id"], "class": cls,
               "flat": j, "floor": f, "hid": hid, "hh_index": hh_index[cc][hid]}
        for nm, lst in (("nb_same", same), ("nb_above", above), ("nb_below", below)):
            rec[nm] = ";".join(str(hh_index[cc][s5s.norm_tok(plc[g], cc)]) for g in lst)
        for cl_ in c.CLASSES:
            rec["s_cls_" + cl_] = 1.0 if cls == cl_ else 0.0
        rec.update({"s_infil_ach": float(b["infiltration_ach"]), "s_north_sin": math.sin(nrad), "s_north_cos": math.cos(nrad),
                    "s_n_floors": float(F), "s_k": float(k), "s_n_dwellings": float(nd), "s_floor_idx": float(f),
                    "s_is_top": 1.0 if (spans or f == F - 1) else 0.0, "s_is_ground": 1.0 if (spans or f == 0) else 0.0,
                    "s_area_m2": float(area)})
        rec.update(aval)
        for cid in clim:
            rec["c_" + cid] = 1.0 if r["climate_id"] == cid else 0.0
        recs.append(rec)
    return recs, flags


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    olp = s6.TEST + "openlog_drivers.tsv"
    if os.path.exists(olp):
        os.remove(olp)
    L = s6.lists()
    TL = s6.train_lists()
    R = s6.runs(LOG)
    for nm in s6.TEST_LISTS:
        print("INFO list %s runs %d" % (nm, len(L[nm])), flush=True)
    # ------------------------------------------------------------------ building / archetype / climate tables (driver files)
    bt = {r["building_id"]: r for r in csv.DictReader(io.open(s6.open_driver(c.CAMP + "in/buildings_es_it.csv", LOG), encoding="utf-8"))}
    arch = {}
    for cc in c.COUNTRIES:
        s6.open_driver(c.CAMP + "in/archetype_parameters_%s.csv" % cc, LOG)
        arch[cc] = {r["Code_Building"]: r for r in s5s.mz._s8.load_rows(c.CAMP + "in/", cc)[0]}
    acols, askipped = c.archetype_numeric_columns()          # reads the two archetype tables (already logged above)
    s6.open_driver(c.CAMP + "in/climates_es_it.csv", LOG)
    clim = c.climates()
    names_all = c.all_input_names()

    # ------------------------------------------------------------------ copies from the train store (never recomputed)
    copies = ["norm.json", "static_cols.json"] + ["weather_%s.npy" % cid for cid in clim] + ["calendar_%s.npy" % cc for cc in c.COUNTRIES]
    bad = []
    for fn in copies:
        src = s6.TRAIN_STORE + fn
        s6.open_driver(src, LOG)
        shutil.copyfile(src, OUT + fn)
        if md5(src) != md5(OUT + fn):
            bad.append(fn)
    chk("copies_equal_train_store_md5", not bad, "files=%d bad=%s norm.json md5=%s static_cols.json md5=%s" % (len(copies), bad, md5(OUT + "norm.json"), md5(OUT + "static_cols.json")))
    sc = json.load(open(OUT + "static_cols.json"))

    # ------------------------------------------------------------------ households: train rows first and unchanged, test-pool households appended
    need = {cc: set() for cc in c.COUNTRIES}
    for nm in s6.TEST_LISTS:
        for rid in L[nm]:
            cc = R[rid]["country"]
            for t in s6.placement(R[rid]).values():
                need[cc].add(s5s.norm_tok(t, cc))
    # households named by the equality-check runs are inside the train store by construction (checked below)
    hh_index, trainhh, new_tasks = {}, {}, []
    for cc in c.COUNTRIES:
        z = np.load(s6.open_driver(s6.TRAIN_STORE + "hh_%s.npz" % cc, LOG))
        trainhh[cc] = {k: z[k] for k in z.files}
        hl = [str(x) for x in trainhh[cc]["hid"]]
        hh_index[cc] = {h: i for i, h in enumerate(hl)}
        assert len(hh_index[cc]) == len(hl)
        for h in sorted(need[cc]):
            if h not in hh_index[cc]:
                new_tasks.append((cc, h))
    stamp("households named by test placements: %s ; already in the train store: %s ; new: %d" % (
        {cc: len(v) for cc, v in need.items()}, {cc: len(need[cc] & set(hh_index[cc])) for cc in c.COUNTRIES}, len(new_tasks)))
    got, missing = {}, []
    with mp.Pool(8) as pool:
        for cc, h, val, st, lg in pool.imap_unordered(read_hh_guarded, new_tasks, chunksize=16):
            LOG.extend(lg)
            if val is None:
                missing.append((cc, h, st))
            else:
                got[(cc, h)] = val
    chk("hid_found", not missing, "households_needed_new=%d found=%d missing=%d %s" % (len(new_tasks), len(got), len(missing), missing[:3]))
    if missing:
        sys.exit(4)
    nan_hh = 0
    new_by_cc = {}
    for cc in c.COUNTRIES:
        add = sorted(h for (c2, h) in got if c2 == cc)
        new_by_cc[cc] = len(add)
        t = trainhh[cc]
        if add:
            pres = np.stack([got[(cc, h)][0] for h in add])
            frac = np.stack([got[(cc, h)][1] for h in add])
            mem = np.array([got[(cc, h)][2] for h in add], dtype=np.float32)
            dw = np.array([got[(cc, h)][3] for h in add], dtype=np.float32)
            people = (mem[:, None] * pres).astype(np.float32)
            applw = (dw[:, None] * frac).astype(np.float32)
            nan_hh += sum(int((~np.isfinite(x)).sum()) for x in (pres, frac, mem, dw))
            out = {"hid": np.concatenate([t["hid"], np.array(add)]), "presence": np.concatenate([t["presence"], pres]),
                   "appl_frac": np.concatenate([t["appl_frac"], frac]), "people": np.concatenate([t["people"], people]),
                   "appl_w": np.concatenate([t["appl_w"], applw]), "members": np.concatenate([t["members"], mem]),
                   "design_w": np.concatenate([t["design_w"], dw])}
        else:
            out = dict(t)
        np.savez(OUT + "hh_%s.npz" % cc, **out)
        base = len(hh_index[cc])
        for i, h in enumerate(add):
            hh_index[cc][h] = base + i
        z2 = np.load(OUT + "hh_%s.npz" % cc)
        same_prefix = all(np.array_equal(z2[k][:len(t["hid"])], t[k]) for k in t)
        n_hh = len(z2["hid"])
        chk("hh_%s_train_rows_unchanged_and_first" % cc, same_prefix and n_hh == len(t["hid"]) + len(add), "train rows %d + new %d = %d" % (len(t["hid"]), len(add), n_hh))
        print("INFO hh_%s.npz n_hh=%d new presence[min,max]=[%.3f,%.3f]" % (cc, n_hh, float(out["presence"][len(t["hid"]):].min()) if add else float("nan"), float(out["presence"][len(t["hid"]):].max()) if add else float("nan")), flush=True)
        nan_hh += sum(int((~np.isfinite(z2[k])).sum()) for k in ("presence", "appl_frac", "people", "appl_w", "members", "design_w"))

    # ------------------------------------------------------------------ flats tables
    geom_cache = {}

    def geom(row):
        code = row["Code_Building"]
        if code not in geom_cache:
            d = s5s.mz.derive(row)
            geom_cache[code] = (d["width"], d["depth"], d["n_storey"], d["a_ref"])
        return geom_cache[code]

    flags_bad = {"nf_bad": [], "nd_bad": [], "area_bad": []}

    def build(ids):
        recs = []
        for rid in sorted(ids):
            r = R[rid]
            rr, fl = flat_records(rid, r, s6.placement(r), bt, arch, acols, clim, geom, hh_index)
            for k in fl:
                if fl[k]:
                    flags_bad[k].append(rid)
            recs.extend(rr)
        return pd.DataFrame(recs)

    # equality of the copied record code with the train store (exact), on 60 development + 60 validation runs
    rng = np.random.default_rng(20260930)
    eq_ok, eq_txt = True, []
    for nm in s6.TRAIN_LISTS:
        ids = sorted(TL[nm])
        by_cls = {}
        for rid in ids:
            by_cls.setdefault(R[rid]["class"], []).append(rid)
        pick = {v[0] for v in by_cls.values()} | set(rng.choice(ids, 60, replace=False).tolist())
        mine = build(pick)
        tr = pd.read_parquet(s6.open_driver(s6.TRAIN_STORE + "flats_%s.parquet" % nm, LOG))
        tr = tr[tr["run_id"].isin(pick)].reset_index(drop=True)
        try:
            pd.testing.assert_frame_equal(mine.reset_index(drop=True), tr, check_exact=True, check_dtype=False)
            eq_txt.append("%s: %d runs %d rows equal" % (nm, len(pick), len(tr)))
        except AssertionError as e:
            eq_ok = False
            eq_txt.append("%s: DIFFER %s" % (nm, str(e)[:200]))
    chk("record_code_equals_train_store_on_dev_and_val_runs", eq_ok, "; ".join(eq_txt))
    # seen failing: a planted wrong hh_index must be caught by the same comparison
    mine_bad = mine.copy()
    mine_bad.loc[0, "hh_index"] = int(mine_bad.loc[0, "hh_index"]) + 1
    try:
        pd.testing.assert_frame_equal(mine_bad.reset_index(drop=True), tr, check_exact=True, check_dtype=False)
        planted_caught = False
    except AssertionError:
        planted_caught = True
    chk("record_equality_planted_hh_index_change_CAUGHT (seen failing)", planted_caught)
    flags_bad = {"nf_bad": [], "nd_bad": [], "area_bad": []}          # the equality-check runs are not part of the test checks below

    flats = {}
    for nm in s6.TEST_LISTS:
        df = build(L[nm])
        flats[nm] = df
        df.to_parquet(OUT + "flats_%s.parquet" % nm, index=False)
        stamp("flats_%s.parquet rows %d runs %d (list has %d runs)" % (nm, len(df), df["run_id"].nunique(), len(L[nm])))
        chk("rows_%s" % nm, df["run_id"].nunique() == len(L[nm]) and set(df["run_id"]) == set(L[nm]),
            "runs=%d (list %d) flat rows=%d es_rows=%d it_rows=%d" % (df["run_id"].nunique(), len(L[nm]), len(df), int((df["country"] == "es").sum()), int((df["country"] == "it").sum())))
    chk("run_n_floors_eq_archetype_n_storey_and_dwelling_counts_and_area_sums", not any(flags_bad.values()),
        "nf=%d nd=%d area=%d" % tuple(len(flags_bad[k]) for k in ("nf_bad", "nd_bad", "area_bad")))
    # ------------------------------------------------------------------ checks on the tables
    allcols = [list(f.columns) for f in flats.values()]
    chk("columns_identical_across_lists", all(x == allcols[0] for x in allcols))
    scols = [x for x in allcols[0] if x.startswith("s_")]
    ccols = [x for x in allcols[0] if x.startswith("c_")]
    chk("static_columns_identical_to_static_cols_json", scols == sc["static"] and ccols == sc["climate_onehot"], "n_static=%d n_climate=%d" % (len(scols), len(ccols)))
    trcols = list(pd.read_parquet(s6.TRAIN_STORE + "flats_validation.parquet").columns)
    chk("columns_identical_to_train_flats", allcols[0] == trcols, "n=%d" % len(trcols))
    present = c.HH_CHANNELS + c.NB_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS + scols + ccols
    chk("input_list_equals_spec", sorted(present) == sorted(names_all), "n_inputs=%d n_spec=%d" % (len(present), len(names_all)))
    ok, badn = c.check_features(present)
    chk("check_features_full_input_list", ok, "n=%d forbidden_hits=%s" % (len(present), badn))
    nan_static = sum(int(f[scols + ccols].isna().sum().sum()) for f in flats.values())
    nan_other = sum(int(f[["hh_index"]].isna().sum().sum()) for f in flats.values())
    wnan = sum(int((~np.isfinite(np.load(OUT + "weather_%s.npy" % cid))).sum()) for cid in clim) + sum(int((~np.isfinite(np.load(OUT + "calendar_%s.npy" % cc))).sum()) for cc in c.COUNTRIES)
    chk("no_nan", (nan_hh + nan_static + nan_other + wnan) == 0, "hh=%d static=%d hh_index=%d weather_calendar=%d" % (nan_hh, nan_static, nan_other, wnan))
    # every hid of a placement is inside the (extended) household table
    nh = {cc: len(np.load(OUT + "hh_%s.npz" % cc)["hid"]) for cc in c.COUNTRIES}
    hmax = {}
    for f in flats.values():
        for cc in c.COUNTRIES:
            sub = f[f["country"] == cc]
            if len(sub):
                nbmax = max([int(x) for s in pd.concat([sub["nb_same"], sub["nb_above"], sub["nb_below"]]) if s for x in s.split(";")] or [0])
                hmax[cc] = max(hmax.get(cc, -1), int(sub["hh_index"].max()), nbmax)
    chk("every_hh_index_inside_household_table", all(hmax.get(cc, -1) < nh[cc] for cc in c.COUNTRIES), "max index %s, rows %s" % (hmax, nh))
    # the test-list households: how many are new vs already in the train store
    chk("no_targets_file_in_test_store", not any(fn.startswith("targets") for fn in os.listdir(OUT)), "files=%s" % sorted(os.listdir(OUT)))
    # open log (driver reads only)
    s6.flush_log(LOG, "drivers")
    lines = s6.read_log_file(olp)
    badl = s6.check_lines(lines, s6.b0_ids())
    chk("openlog_drivers_kind_driver_only_and_nothing_under_extracted", not badl and all(k == "driver" for k, _, _ in lines),
        "lines=%d kinds=%s offending=%d %s" % (len(lines), sorted({k for k, _, _ in lines}), len(badl), badl[:2]))
    # seen failing: a planted extracted/ line and a planted 'truth' kind are caught by the same check
    pl1 = s6.check_lines([("driver", "es_B00_x", s6.EXTRACTED + "x/es_B00_x.csv.gz")], s6.b0_ids())
    pl2 = s6.check_lines([("truth", "es_B00_x", "/tmp/x")], s6.b0_ids())
    pl3 = s6.check_lines([("b0", L["test_both_new"][0], s6.EXTRACTED + "x/" + L["test_both_new"][0] + ".csv.gz")], s6.b0_ids())
    chk("openlog_check_planted_lines_CAUGHT (seen failing)", bool(pl1) and bool(pl2) and bool(pl3), "extracted-driver=%d truth-kind=%d b0-of-a-test-run=%d" % (len(pl1), len(pl2), len(pl3)))
    # guard seen failing: the reader refuses an extracted path and a UK-looking path
    r1 = r2 = False
    try:
        s6.open_driver(s6.EXTRACTED + "x/y.csv.gz", [])
    except PermissionError:
        r1 = True
    try:
        s6.open_driver(c.HHROOT + "uk_1/household.json", [])
    except PermissionError:
        r2 = True
    chk("guard_refuses_extracted_and_uk_paths (seen failing)", r1 and r2)
    readme = [
        "# 5J Step 6 DRIVERS store of the three test lists (written %s by s6_store.py)" % time.strftime("%Y-%m-%d %H:%M"),
        "flats_<test list>.parquet : same columns as the Step 5 store (checked equal); NO targets file exists here (test truth is read only by the frozen scorer)",
        "hh_<cc>.npz : the train store's rows first and unchanged, then the households of the test pools (new: %s)" % new_by_cc,
        "norm.json, static_cols.json, weather_<climate>.npy, calendar_<cc>.npy : COPIES of the train store (md5 compared)",
        "Open log: /speed-scratch/o_iseri/5J/test/openlog_drivers.tsv (kind driver only)",
    ]
    io.open(OUT + "README.md", "w", encoding="utf-8").write("\n".join(readme) + "\n")
    nfail = sum(1 for _, ok_ in RES if not ok_)
    print("TEST_STORE_DONE checks=%d fail=%d seconds=%.0f" % (len(RES), nfail, time.time() - t0), flush=True)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
