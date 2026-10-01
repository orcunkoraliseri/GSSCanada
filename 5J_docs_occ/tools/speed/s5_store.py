# -*- coding: utf-8 -*-
"""5J Step 5 part A/B: the feature store (THE CONTRACT for the training tasks). Speed job only; Spain + Italy only.
Writes /speed-scratch/o_iseri/5J/train/store/ :
  hh_<cc>.npz  weather_<climate_id>.npy  calendar_<cc>.npy  flats_<split>.parquet  targets_<split>.npy
  pairs_development.parquet pairs_validation.parquet  norm.json  static_cols.json  README.md
for split in development, validation, b0_dev, b0_val (read ONLY through s5_common.open_run; nothing else is ever opened).
Every check prints one line  CHECK <name> PASS|FAIL ...  ; the R3 check FAIL stops the job (exit 3)."""
import sys, os, io, json, math, time, hashlib, importlib, itertools, datetime, re, multiprocessing as mp
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import s5_common as c

OUT = c.TRAIN + "store/"
H = c.H
RES = []          # (name, ok)


def chk(name, ok, text=""):
    RES.append((name, bool(ok)))
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)


def stamp(s):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), s), flush=True)


# ---- builder (geometry only: derive(); the same module the campaign used, read from the campaign repo copy, no bytecode written)
sys.path.insert(0, c.REPO + "5J_docs_occ/tools")
mz = importlib.import_module("5thJ_idf_mz")
mz._j5.TOOLS_4J = c.REPO + "4J_docs_occ/tools"


def norm_tok(t, cc):
    return t[len(cc) + 1:] if t.startswith(cc + "_") else t


# ---- households ----------------------------------------------------------------------------------------------------
def read_series(p):
    with io.open(p, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    v = np.array(lines[1:], dtype=np.float64)          # line 1 = a name
    if len(v) != H:
        raise RuntimeError("%s has %d values" % (p, len(v)))
    return v


def read_hh(task):
    cc, hid = task
    d = "%s%s_%s/" % (c.HHROOT, cc, hid)
    if not os.path.isdir(d):
        return (cc, hid, None, "folder missing")
    try:
        j = json.load(io.open(d + "household.json", encoding="utf-8"))
        if str(j["hid"]) != hid or j["country"] != cc:
            return (cc, hid, None, "json hid/country mismatch %s %s" % (j["hid"], j["country"]))
        pres = read_series(d + j["presence_file"])
        elec = read_series(d + j["elec_file"])
        return (cc, hid, (pres.astype(np.float32), elec.astype(np.float32), float(j["n_members"]), float(j["appliance_peak_w"])), "ok")
    except Exception as e:
        return (cc, hid, None, "error %s" % str(e)[:150])


# ---- truth worker --------------------------------------------------------------------------------------------------
def work_truth(task):
    rid, nd = task
    log = []
    a = c.read_truth(rid, nd, log, "truth")
    return rid, a[:, :, :3].astype(np.float32), log


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    olp = c.TRAIN + "openlog_store.tsv"
    if os.path.exists(olp):
        os.remove(olp)                                  # own file of an earlier attempt
    allowed = c.allowed_ids()
    L = c.lists()
    stamp("allowed ids %d  %s" % (len(allowed), {k: len(v) for k, v in L.items()}))
    R = c.runs()
    bt = {r["building_id"]: r for r in __import__("csv").DictReader(io.open(c.CAMP + "in/buildings_es_it.csv", encoding="utf-8"))}
    arch = {}
    for cc in c.COUNTRIES:
        arch[cc] = {r["Code_Building"]: r for r in mz._s8.load_rows(c.CAMP + "in/", cc)[0]}
    acols, askipped = c.archetype_numeric_columns()
    print("INFO archetype numeric columns used %d; skipped %s" % (len(acols), askipped), flush=True)
    clim = c.climates()
    stat_names = c.static_names()
    names_all = c.all_input_names()

    # ------------------------------------------------------------------ R3 check on 3 development runs (stops the job on FAIL)
    dev_sorted = sorted(L["development"])
    log = []
    worst, ratio = 0.0, 0.0
    for rid in (dev_sorted[0], dev_sorted[len(dev_sorted) // 2], dev_sorted[-1]):
        a = c.read_truth(rid, int(R[rid]["n_dwellings"]), log, "r3check")
        calc = a[:, :, 2] + (a[:, :, 0] + a[:, :, 1]) / c.COP
        diff = np.abs(a[:, :, 3] - calc)
        tol = 2e-7 * (np.abs(a[:, :, 2]) + np.abs(a[:, :, 0]) / c.COP + np.abs(a[:, :, 1]) / c.COP) + 1e-9
        worst = max(worst, float(diff.max()))
        ratio = max(ratio, float((diff / tol).max()))
    c.flush_log(log, "store")
    chk("R3_total_elec_rule", ratio <= 1.0, "runs=3 max_abs_diff_kwh=%.3e max_diff_over_file_precision_tolerance=%.3f (<=1 means equal to file precision %%.8g)" % (worst, ratio))
    if ratio > 1.0:
        print("STOP: R3 total-electricity rule does not hold; job stops", flush=True)
        sys.exit(3)

    # ------------------------------------------------------------------ households
    hids = {cc: set() for cc in c.COUNTRIES}
    split_hids = {s: {cc: set() for cc in c.COUNTRIES} for s in c.SPLITS}
    for s in c.SPLITS:
        for rid in L[s]:
            cc = R[rid]["country"]
            for t in c.placement(rid).values():
                h = norm_tok(t, cc)
                hids[cc].add(h)
                split_hids[s][cc].add(h)
    stamp("households named by placements: %s" % {cc: len(v) for cc, v in hids.items()})
    tasks = [(cc, h) for cc in c.COUNTRIES for h in sorted(hids[cc])]
    got = {}
    missing = []
    with mp.Pool(8) as pool:
        for cc, h, val, st in pool.imap_unordered(read_hh, tasks, chunksize=16):
            if val is None:
                missing.append((cc, h, st))
            else:
                got[(cc, h)] = val
    chk("hid_found", not missing, "households_needed=%d found=%d missing=%d %s" % (len(tasks), len(got), len(missing), missing[:3]))
    if missing:
        sys.exit(4)
    hh_index = {}
    nan_hh = 0
    for cc in c.COUNTRIES:
        hl = sorted(hids[cc])
        hh_index[cc] = {h: i for i, h in enumerate(hl)}
        pres = np.stack([got[(cc, h)][0] for h in hl])
        frac = np.stack([got[(cc, h)][1] for h in hl])
        mem = np.array([got[(cc, h)][2] for h in hl], dtype=np.float32)
        dw = np.array([got[(cc, h)][3] for h in hl], dtype=np.float32)
        people = (mem[:, None] * pres).astype(np.float32)
        applw = (dw[:, None] * frac).astype(np.float32)
        nan_hh += sum(int((~np.isfinite(x)).sum()) for x in (pres, frac, mem, dw))
        np.savez(OUT + "hh_%s.npz" % cc, hid=np.array(hl), presence=pres, appl_frac=frac, people=people, appl_w=applw, members=mem, design_w=dw)
        print("INFO hh_%s.npz n_hh=%d presence[min,max]=[%.3f,%.3f] appl_frac[min,max]=[%.4f,%.4f] members[min,max]=[%.2f,%.2f] design_w[min,max]=[%.1f,%.1f]"
              % (cc, len(hl), pres.min(), pres.max(), frac.min(), frac.max(), mem.min(), mem.max(), dw.min(), dw.max()), flush=True)
        hh_arrays = {"presence": pres, "appl_frac": frac, "people": people, "appl_w": applw}
        globals().setdefault("HHA", {})[cc] = hh_arrays

    # ------------------------------------------------------------------ weather + calendar
    wmat = {}
    epw_bad = []
    for r in __import__("csv").DictReader(io.open(c.CAMP + "in/climates_es_it.csv", encoding="utf-8")):
        cid = r["climate_id"]
        p = c.CAMP + "epw/" + re.split(r"[\\/]", r["path"])[-1]
        md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
        if md5 != r["md5"]:
            epw_bad.append((cid, "md5"))
        df = pd.read_csv(p, skiprows=8, header=None)
        if len(df) != H or int(df.iloc[0, 1]) != 1 or int(df.iloc[0, 2]) != 1 or int(df.iloc[0, 3]) != 1 or \
                int(df.iloc[-1, 1]) != 12 or int(df.iloc[-1, 2]) != 31 or int(df.iloc[-1, 3]) != 24:
            epw_bad.append((cid, "shape or first/last row"))
            continue
        w = df.iloc[:, c.EPW_COLS].to_numpy(dtype=np.float64)
        wmat[cid] = w.astype(np.float32)
        np.save(OUT + "weather_%s.npy" % cid, wmat[cid])
    chk("weather_epw_md5_and_shape", not epw_bad and len(wmat) == len(clim), "climates=%d bad=%s" % (len(wmat), epw_bad))
    nan_w = sum(int((~np.isfinite(w)).sum()) for w in wmat.values())
    cal = {}
    for cc in c.COUNTRIES:
        i = np.arange(H)
        hod, doy = i % 24, i // 24
        dow = (datetime.date(c.CAL_YEAR[cc], 1, 1).weekday() + doy) % 7          # Monday = 0 (same calendar as 4thJ_step7 year_day_types)
        cal[cc] = np.stack([np.sin(2 * np.pi * hod / 24), np.cos(2 * np.pi * hod / 24), np.sin(2 * np.pi * doy / 365),
                            np.cos(2 * np.pi * doy / 365), dow], 1).astype(np.float32)
        np.save(OUT + "calendar_%s.npy" % cc, cal[cc])
        print("INFO calendar_%s year %d: 1 January is weekday %d (Mon=0); row 0 = 00:00-01:00 of 1 January; dow of row 0 = %d, row 24 = %d, row %d = %d"
              % (cc, c.CAL_YEAR[cc], datetime.date(c.CAL_YEAR[cc], 1, 1).weekday(), cal[cc][0, 4], cal[cc][24, 4], H - 1, cal[cc][H - 1, 4]), flush=True)

    # ------------------------------------------------------------------ flats tables
    geom_cache = {}

    def geom(row):
        code = row["Code_Building"]
        if code not in geom_cache:
            d = mz.derive(row)
            geom_cache[code] = (d["width"], d["depth"], d["n_storey"], d["a_ref"])
        return geom_cache[code]

    flats = {}
    area_bad, nf_bad, nd_bad = [], [], []
    for s in c.SPLITS:
        recs = []
        for rid in sorted(L[s]):
            r = R[rid]
            cc, cls = r["country"], r["class"]
            nd, k, F = int(r["n_dwellings"]), int(r["k"]), int(r["n_floors"])
            plc = c.placement(rid)
            b = bt[r["building_id"]]
            row = arch[cc][b["archetype_code"]]
            W, D, nst, aref = geom(row)
            spans = cls in ("SFH", "TH")
            if abs(nst - F) > 1e-9:
                nf_bad.append(rid)
            if (spans and nd != 1) or ((not spans) and nd != F * k):
                nd_bad.append(rid)
            area = W * D * nst if spans else W * D / k
            if abs(area * nd - aref) > 1e-6 * aref:
                area_bad.append(rid)
            aval = {}
            for col in acols:
                v = row[col].strip()
                aval["s_" + col.lower()] = float(v) if v != "" else 0.0
            nrad = math.radians(float(b["north_axis_deg"]))
            floor_of = [0 if spans else j // k for j in range(nd)]
            for j in range(nd):
                f = floor_of[j]
                same = [g for g in range(nd) if floor_of[g] == f and g != j] if not spans else []
                above = [g for g in range(nd) if floor_of[g] == f + 1] if not spans else []
                below = [g for g in range(nd) if floor_of[g] == f - 1] if not spans else []
                hid = norm_tok(plc[j], cc)
                rec = {"run_id": rid, "country": cc, "climate_id": r["climate_id"], "building_id": r["building_id"], "class": cls,
                       "flat": j, "floor": f, "hid": hid, "hh_index": hh_index[cc][hid]}
                for nm, lst in (("nb_same", same), ("nb_above", above), ("nb_below", below)):
                    rec[nm] = ";".join(str(hh_index[cc][norm_tok(plc[g], cc)]) for g in lst)
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
        df = pd.DataFrame(recs)
        flats[s] = df
        df.to_parquet(OUT + "flats_%s.parquet" % s, index=False)
        stamp("flats_%s.parquet rows %d runs %d" % (s, len(df), len(L[s])))
    chk("flats_rows_validation_7617", len(flats["validation"]) == 7617, "development=%d validation=%d b0_dev=%d b0_val=%d" %
        (len(flats["development"]), len(flats["validation"]), len(flats["b0_dev"]), len(flats["b0_val"])))
    chk("run_n_floors_eq_archetype_n_storey_and_dwelling_counts", not nf_bad and not nd_bad, "n_floors_mismatch=%d n_dwellings_mismatch=%d" % (len(nf_bad), len(nd_bad)))
    chk("flat_areas_sum_to_A_C_Ref", not area_bad, "runs_with_area_sum != A_C_Ref (rel 1e-6): %d %s" % (len(area_bad), area_bad[:3]))
    # inputs actually present in the table = the spec list; leakage guard on the FULL list
    cols = list(flats["development"].columns)
    present = c.HH_CHANNELS + c.NB_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS + [x for x in cols if x.startswith(("s_", "c_"))]
    chk("input_list_equals_spec", sorted(present) == sorted(names_all), "n_inputs=%d n_spec=%d" % (len(present), len(names_all)))
    ok, bad = c.check_features(present)
    chk("check_features_full_input_list", ok, "n=%d forbidden_hits=%s" % (len(present), bad))
    nan_static = sum(int(flats[s][[x for x in cols if x.startswith(("s_", "c_"))]].isna().sum().sum()) for s in c.SPLITS)
    json.dump({"static": [x for x in cols if x.startswith("s_")], "climate_onehot": [x for x in cols if x.startswith("c_")],
               "dropped_text_or_id_archetype_columns": askipped, "dropped_building_columns": ["building_id", "country", "class", "archetype_code", "period", "pilot"],
               "feature_forbidden": c.FEATURE_FORBIDDEN}, open(OUT + "static_cols.json", "w"), indent=1)

    # ------------------------------------------------------------------ households and buildings overlap
    ov = {cc: split_hids["development"][cc] & split_hids["validation"][cc] for cc in c.COUNTRIES}
    chk("households_dev_cap_val_zero", all(len(v) == 0 for v in ov.values()),
        "overlap es=%d it=%d (dev households es=%d it=%d; val es=%d it=%d)" % (len(ov["es"]), len(ov["it"]), len(split_hids["development"]["es"]),
        len(split_hids["development"]["it"]), len(split_hids["validation"]["es"]), len(split_hids["validation"]["it"])))
    bd = set(flats["development"]["building_id"]); bv = set(flats["validation"]["building_id"])
    gd = set(zip(flats["development"]["climate_id"], flats["development"]["building_id"]))
    gv = set(zip(flats["validation"]["climate_id"], flats["validation"]["building_id"]))
    print("INFO building overlap dev/val: buildings dev=%d val=%d both=%d; (climate,building) groups dev=%d val=%d both=%d (shared by design, R10)"
          % (len(bd), len(bv), len(bd & bv), len(gd), len(gv), len(gd & gv)), flush=True)

    # ------------------------------------------------------------------ targets (read through open_run only)
    openlog = []
    for s in c.SPLITS:
        df = flats[s]
        ids = sorted(L[s])
        nds = [int(R[rid]["n_dwellings"]) for rid in ids]
        off = {}
        o = 0
        for rid, nd in zip(ids, nds):
            off[rid] = o
            o += nd
        assert o == len(df), (s, o, len(df))
        assert (df["run_id"].to_numpy()[[off[r] for r in ids]] == np.array(ids)).all()
        mm = np.lib.format.open_memmap(OUT + "targets_%s.npy" % s, mode="w+", dtype=np.float32, shape=(len(df), H, 3))
        n_done = 0
        with mp.Pool(8) as pool:
            for rid, arr, lg in pool.imap_unordered(work_truth, list(zip(ids, nds)), chunksize=1):
                mm[off[rid]:off[rid] + arr.shape[0]] = arr
                openlog.extend(lg)
                n_done += 1
                if n_done % 500 == 0:
                    stamp("targets_%s %d/%d runs" % (s, n_done, len(ids)))
        mm.flush()
        del mm
        stamp("targets_%s.npy done rows %d" % (s, len(df)))
    c.flush_log(openlog, "store")

    # round trip: 3 random rows per split against a fresh read of the file
    rng = np.random.default_rng(20260930)
    log2 = []
    worst_rt = 0.0
    nan_t = 0
    for s in c.SPLITS:
        T = np.load(OUT + "targets_%s.npy" % s, mmap_mode="r")
        df = flats[s]
        for i in rng.choice(len(df), 3, replace=False):
            rid, j = df["run_id"].iat[i], int(df["flat"].iat[i])
            a = c.read_truth(rid, int(R[rid]["n_dwellings"]), log2, "roundtrip")
            worst_rt = max(worst_rt, float(np.abs(np.asarray(T[i]) - a[j, :, :3]).max()))
        for a0 in range(0, len(df), 512):
            nan_t += int((~np.isfinite(np.asarray(T[a0:a0 + 512]))).sum())
    c.flush_log(log2, "store")
    chk("targets_roundtrip", worst_rt < 1e-4, "9+ random rows re-read from the csv.gz; max abs diff %.3e kWh (float32 storage)" % worst_rt)

    # ------------------------------------------------------------------ pairs
    pair_counts = {}
    for s in ("development", "validation"):
        df = flats[s]
        grp = df.groupby(["climate_id", "building_id", "flat"]).indices
        hid_code = pd.factorize(df["country"] + "|" + df["hid"])[0]
        A, B = [], []
        alt = 0
        for key, idx in grp.items():
            m = len(idx)
            if m < 2:
                continue
            ia, ib = np.triu_indices(m, 1)
            keep = hid_code[idx[ia]] != hid_code[idx[ib]]
            A.append(idx[ia][keep]); B.append(idx[ib][keep])
            cnt = np.bincount(hid_code[idx])
            alt += m * (m - 1) // 2 - int((cnt * (cnt - 1) // 2).sum())          # second method: all pairs minus same-household pairs
        ra = np.concatenate(A) if A else np.zeros(0, dtype=np.int64)
        rb = np.concatenate(B) if B else np.zeros(0, dtype=np.int64)
        pd.DataFrame({"row_a": ra.astype(np.int64), "row_b": rb.astype(np.int64)}).to_parquet(OUT + "pairs_%s.parquet" % s, index=False)
        pair_counts[s] = (len(ra), alt)
        print("INFO pairs_%s rows %d (second counting method %d)" % (s, len(ra), alt), flush=True)
    chk("pairs_validation_33474", pair_counts["validation"][0] == 33474 and pair_counts["validation"][1] == 33474,
        "pairs=%d second_method=%d scorer=33474" % pair_counts["validation"])
    chk("pairs_development_two_methods_agree", pair_counts["development"][0] == pair_counts["development"][1], "pairs=%d second_method=%d" % pair_counts["development"])

    # ------------------------------------------------------------------ norm.json (development flat-hours)
    dev = flats["development"]
    nfl = len(dev)
    N = float(nfl) * H
    norm = {"source": "development flat-hours (%d flats x %d h)" % (nfl, H), "targets": {}, "channels": {}}
    T = np.load(OUT + "targets_development.npy", mmap_mode="r")
    s1 = np.zeros(3); s2 = np.zeros(3)
    for a0 in range(0, nfl, 256):
        x = np.asarray(T[a0:a0 + 256]).astype(np.float64)
        s1 += x.sum((0, 1)); s2 += (x ** 2).sum((0, 1))
    for i, nm in enumerate(("heating", "cooling", "equipment")):
        mu = s1[i] / N
        norm["targets"][nm] = {"mean": mu, "sd": math.sqrt(max(s2[i] / N - mu * mu, 0.0))}
    acc = {nm: [0.0, 0.0] for nm in c.HH_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS}
    for cc in c.COUNTRIES:
        sub = dev[dev["country"] == cc]
        cnt = np.bincount(sub["hh_index"].to_numpy(), minlength=len(hh_index[cc]))
        for nm, arr in globals()["HHA"][cc].items():
            a64 = arr.astype(np.float64)
            acc[nm][0] += float((cnt * a64.sum(1)).sum()); acc[nm][1] += float((cnt * (a64 ** 2).sum(1)).sum())
        for k_, nm in enumerate(c.CALENDAR_CHANNELS):
            col = cal[cc][:, k_].astype(np.float64)
            acc[nm][0] += len(sub) * float(col.sum()); acc[nm][1] += len(sub) * float((col ** 2).sum())
    for cid in clim:
        n_c = int((dev["climate_id"] == cid).sum())
        w = wmat[cid].astype(np.float64)
        for k_, nm in enumerate(c.WEATHER_CHANNELS):
            acc[nm][0] += n_c * float(w[:, k_].sum()); acc[nm][1] += n_c * float((w[:, k_] ** 2).sum())
    for nm, (a1, a2) in acc.items():
        mu = a1 / N
        norm["channels"][nm] = {"mean": mu, "sd": math.sqrt(max(a2 / N - mu * mu, 0.0))}
    norm["note"] = "neighbour channels nb_*_people and nb_*_appl_w use the people and appl_w statistics; flags are not standardised; static columns are not in this file"
    json.dump(norm, open(OUT + "norm.json", "w"), indent=1)
    print("INFO norm.json targets %s" % {k: (round(v["mean"], 5), round(v["sd"], 5)) for k, v in norm["targets"].items()}, flush=True)

    # ------------------------------------------------------------------ remaining checks
    chk("no_nan", (nan_hh + nan_w + nan_static + nan_t) == 0,
        "hh=%d weather=%d static=%d targets=%d calendar=%d" % (nan_hh, nan_w, nan_static, nan_t, sum(int((~np.isfinite(v)).sum()) for v in cal.values())))
    n_bad_open, n_open, runs_open = 0, 0, set()
    for ln in io.open(olp, encoding="utf-8").read().splitlines()[1:]:
        kind, rid, p = ln.split("\t")
        n_open += 1
        runs_open.add(rid)
        n_bad_open += 0 if rid in allowed else 1
    chk("openlog_outside_allowed_zero", n_bad_open == 0, "log lines=%d distinct_runs=%d outside_the_four_lists=%d log=%s" % (n_open, len(runs_open), n_bad_open, olp))

    readme = [
        "# 5J Step 5 feature store (written %s by s5_store.py; contract for the training tasks)" % time.strftime("%Y-%m-%d %H:%M"),
        "hh_<cc>.npz : hid (str, incl. avg), presence, appl_frac, people (=members x presence), appl_w (=design_w x appl_frac) as n_hh x 8760 float32; members, design_w (n_hh)",
        "weather_<climate_id>.npy : 8760 x 7 float32 = EPW columns (0-based) 6 dry bulb C, 7 dew point C, 8 RH %, 13 GHI, 14 DNI, 15 DHI (Wh/m2), 21 wind speed m/s",
        "calendar_<cc>.npy : 8760 x 5 float32 = hour sin, hour cos, day-of-year sin, day-of-year cos (period 365), day of week 0-6 (Monday=0); row 0 = 00:00-01:00 of 1 January of the diary year (es 2010, it 2014; the 4J schedule calendar)",
        "flats_<split>.parquet : one row per (run, flat), sorted by run_id then flat; ids, hid, hh_index (row in hh_<cc>), nb_same/nb_above/nb_below (';'-joined hh_index of the flats on the same floor excluding itself / the floor above / the floor below), s_* static, c_* climate one-hot",
        "targets_<split>.npy : float32 n_rows x 8760 x 3 (heating, cooling, equipment kWh per hour per flat), same row order as flats_<split>.parquet; total_elec = equipment + (heating + cooling)/3.0",
        "pairs_development.parquet, pairs_validation.parquet : row_a, row_b indices into flats_<split> (same building, climate and flat index; different runs; different hid)",
        "norm.json : mean and SD (population, ddof 0) from development for the 3 targets and each dynamic channel; static_cols.json : the s_* and c_* column names and what was dropped",
        "split names: development, validation, b0_dev, b0_val only. Open log: /speed-scratch/o_iseri/5J/train/openlog_store.tsv",
    ]
    io.open(OUT + "README.md", "w", encoding="utf-8").write("\n".join(readme) + "\n")
    nfail = sum(1 for _, ok in RES if not ok)
    print("STORE_DONE checks=%d fail=%d seconds=%.0f" % (len(RES), nfail, time.time() - t0), flush=True)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
