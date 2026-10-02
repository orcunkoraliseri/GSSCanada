# -*- coding: utf-8 -*-
"""5J Step 9g: Model A training-data store builder + its test. Speed job only; ES-MAD-BERRUGUETE and IT-BOL-GALVANI2 only.

  python a9_store.py build <manifest.csv> <allowed.json> <zone_map.csv> <static_dir> <out_dir> [tag]
      manifest columns: run_id, split, district, stem, mode, run_dir, placement_csv, epw
         mode O = occupancy run (placement_csv required), D = default-schedule run (placement_csv empty: no household, hh_index -1).
      allowed.json: {"<split>": [run ids]}  -- the ONLY runs the builder may open (RunGuard refuses everything else, logs nothing for it).
      Writes <out_dir>/ (same layout as the pilot store, s5_store.py header):
        hh_<cc>.npz  weather_<district>.npy  calendar_<district>.npy  flats_<split>.parquet  targets_<split>.npy
        pairs_<split>.parquet (development, validation)  norm.json  static_cols.json  README.md  openlog_<tag>.tsv
      Splits are kept apart by name (development, validation, b0_dev, b0_val, default_*, ...); a run is only ever in one.
  python a9_store.py test <base>      the one test job (see test_main).
  Step 9n (additive; the 9g build above is unchanged):
  python a9_store.py campaign <plan.csv> <campaign_root> <zone_map.csv> <static_dir> <epw_dir> <out_dir> [tag] [workers]
      builds / extends the store from what the campaign keeps (results/<rid>.json + .npz, runs/<rid>/placement.csv + series.tar.gz, b0/); only CLEAN
      non-test runs; a test run (pool test or test building) is refused and never opened; incremental (ledger + result md5).
  python a9_store.py campaign-test <smoke_copy_dir> [workers]     the 9n desktop test on the local smoke copy
  python a9_store.py heatrule                                     the heating-column unique-by-position rule on the 9k case and a planted fault
Exit codes: build: 0 = every check PASS, 1 = a check FAILED, 2 = crashed. test: 0 = every evaluated check PASS, 1 = a check FAILED,
2 = crashed or nothing evaluable (the SUMMARY line lists PASS / FAIL / NOT_EVALUABLE counts; a crashed section is NOT_EVALUABLE).
Inputs (E3 to E5): see a9_common.all_input_names(). No EnergyPlus output is an input column (check_features on the full list).
"""
import sys, os, io, re, csv, json, math, time, hashlib
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import a9_common as c
import a9_extract as ex

H = c.H
RES = []


def chk(name, ok, text=""):
    """ok True = PASS, False = FAIL, None = NOT_EVALUABLE. Step 9n: a numpy bool is converted (np.True_ is not `True`, so summary() counted it as nothing)."""
    ok = None if ok is None else bool(ok)
    RES.append((name, ok))
    print("CHECK %s %s %s" % (name, {True: "PASS", False: "FAIL", None: "NOT_EVALUABLE"}[ok], text), flush=True)


def stamp(s):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), s), flush=True)


def write_table(df, path_noext):
    try:
        if os.environ.get("A9_FORCE_CSV") == "1":            # Step 9n test switch: exercises the csv fallback below
            raise RuntimeError("csv forced")
        df.to_parquet(path_noext + ".parquet", index=False)
        return path_noext + ".parquet"
    except Exception:
        df.to_csv(path_noext + ".csv.gz", index=False)
        return path_noext + ".csv.gz"


def read_table(path_noext):
    if os.path.exists(path_noext + ".parquet"):
        return pd.read_parquet(path_noext + ".parquet")
    # Step 9n: id columns stay text (a csv round trip would turn hid '02695' into 2695 and the empty neighbour lists into NaN)
    ids = ["run_id", "split", "district", "country", "stem", "mode", "zone", "hid", "nb_same", "nb_above", "nb_below"]
    return pd.read_csv(path_noext + ".csv.gz", dtype={k: str for k in ids}, keep_default_na=False, na_values=[])


def targets_rows_match(tp, nrows):
    """Step 9k: True when the targets file has exactly nrows rows of shape (8760, 3)."""
    sh = tuple(np.load(tp, mmap_mode="r").shape)
    return sh == (nrows, H, 3)


def read_series(p):
    """One value per line after a one-line name, exactly 8,760 (as s5_store.py:41-47)."""
    with io.open(p, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    v = np.array(lines[1:], dtype=np.float64)
    if len(v) != H:
        raise RuntimeError("%s has %d values" % (p, len(v)))
    return v


def read_epw(path):
    df = pd.read_csv(path, skiprows=8, header=None)
    if len(df) != H or int(df.iloc[0, 1]) != 1 or int(df.iloc[0, 2]) != 1 or int(df.iloc[0, 3]) != 1 or \
            int(df.iloc[-1, 1]) != 12 or int(df.iloc[-1, 2]) != 31 or int(df.iloc[-1, 3]) != 24:
        raise RuntimeError("EPW %s: shape or first / last row wrong" % path)
    return df.iloc[:, c.EPW_COLS].to_numpy(dtype=np.float64).astype(np.float32)


# ================================================================================================ build
def build_store(rows, allowed, zmap_path, static_dir, out_dir, tag="store"):
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    guard = c.RunGuard(allowed)
    zm = c.zone_map(zmap_path)
    flat_tab, bld_tab, bands = c.static_tables(static_dir)
    names_all = c.all_input_names(bands)
    rows = sorted(rows, key=lambda r: r["run_id"])
    for r in rows:
        if r["district"] not in c.DISTRICTS:
            raise ValueError("district %r is not a Model A district" % r["district"])
    # ---- 1. which rows may be opened (the guard decides; a refused row is recorded and never touched again)
    use, refused = [], []
    for r in rows:
        try:
            guard.open_run(r["run_id"], "probe", r["run_dir"])
        except PermissionError:
            refused.append(r["run_id"])
            continue
        if guard.split_of(r["run_id"]) != r["split"]:
            raise RuntimeError("manifest split %s differs from the allowed list %s for %s" % (r["split"], guard.split_of(r["run_id"]), r["run_id"]))
        use.append(r)
    guard.log = []                                   # the probe is not an open
    stamp("manifest rows %d, allowed %d, refused %d %s" % (len(rows), len(use), len(refused), refused[:3]))
    chk("refused_rows_listed", True, "refused=%d %s" % (len(refused), refused[:5]))
    splits = sorted({r["split"] for r in use})
    nfl = {s: 0 for s in splits}
    for r in use:
        key = (r["district"], r["stem"])
        if key not in zm:
            raise RuntimeError("stem %s not in the zone map" % r["stem"])
        nfl[r["split"]] += len(zm[key])
    # ---- 2. households (placements of the allowed O runs only)
    plc, hh_need = {}, {cc: {} for cc in c.COUNTRIES}
    for r in use:
        if r["mode"] != "O":
            continue
        cc = c.DISTRICTS[r["district"]]["cc"]
        zones = [z["zone"] for z in zm[(r["district"], r["stem"])]]
        p = {}
        for pr in c.read_csv_rows(r["placement_csv"]):
            if pr["dwelling_zone"] in p:
                raise RuntimeError("%s: zone %s placed twice" % (r["run_id"], pr["dwelling_zone"]))
            p[pr["dwelling_zone"]] = pr
            spec = (pr["presence_csv"], pr["appliance_csv"], float(pr["n_members"]), float(pr["appliance_peak_w"]))
            old = hh_need[cc].setdefault(pr["hid"], spec)
            if old != spec:
                raise RuntimeError("household %s (%s) has two different specs" % (pr["hid"], cc))
        if sorted(p) != sorted(zones):
            raise RuntimeError("%s: placement zones differ from the zone map (%d vs %d)" % (r["run_id"], len(p), len(zones)))
        plc[r["run_id"]] = p
    hh_index, HHA, nan_hh = {}, {}, 0
    for cc in c.COUNTRIES:
        hl = sorted(hh_need[cc])
        hh_index[cc] = {h: i for i, h in enumerate(hl)}
        if not hl:
            continue
        pres = np.stack([read_series(hh_need[cc][h][0]).astype(np.float32) for h in hl])
        frac = np.stack([read_series(hh_need[cc][h][1]).astype(np.float32) for h in hl])
        mem = np.array([hh_need[cc][h][2] for h in hl], dtype=np.float32)
        dw = np.array([hh_need[cc][h][3] for h in hl], dtype=np.float32)
        people = (mem[:, None] * pres).astype(np.float32)
        applw = (dw[:, None] * frac).astype(np.float32)
        nan_hh += sum(int((~np.isfinite(x)).sum()) for x in (pres, frac, mem, dw))
        np.savez(os.path.join(out_dir, "hh_%s.npz" % cc), hid=np.array(hl), presence=pres, appl_frac=frac, people=people, appl_w=applw, members=mem, design_w=dw)
        HHA[cc] = {"presence": pres, "appl_frac": frac, "people": people, "appl_w": applw}
        print("INFO hh_%s.npz n_hh=%d presence[min,max]=[%.3f,%.3f] appl_frac[min,max]=[%.4f,%.4f] members[%.2f,%.2f] design_w[%.1f,%.1f]"
              % (cc, len(hl), pres.min(), pres.max(), frac.min(), frac.max(), mem.min(), mem.max(), dw.min(), dw.max()), flush=True)
    # ---- 3. weather + calendar per district
    wmat, cal, epw_info = {}, {}, {}
    for r in use:
        d = r["district"]
        if d in wmat:
            if epw_info[d] != r["epw"]:
                raise RuntimeError("district %s has two EPW files in the manifest" % d)
            continue
        wmat[d] = read_epw(r["epw"])
        epw_info[d] = r["epw"]
        np.save(os.path.join(out_dir, "weather_%s.npy" % d), wmat[d])
        cal[d] = c.calendar_array(c.DISTRICTS[d]["year"])
        np.save(os.path.join(out_dir, "calendar_%s.npy" % d), cal[d])
        print("INFO weather_%s.npy from %s md5 %s ; calendar year %d" % (d, os.path.basename(r["epw"]), hashlib.md5(open(r["epw"], "rb").read()).hexdigest(),
                                                                         c.DISTRICTS[d]["year"]), flush=True)
    nan_w = sum(int((~np.isfinite(w)).sum()) for w in wmat.values())
    # ---- 4. runs: targets (memmap per split) and flat rows
    mm = {s: np.lib.format.open_memmap(os.path.join(out_dir, "targets_%s.npy" % s), mode="w+", dtype=np.float32, shape=(nfl[s], H, 3)) for s in splits}
    off = {s: 0 for s in splits}
    recs = {s: [] for s in splits}
    failed, nan_t, meta_all = [], 0, {}
    for r in use:
        rid, s, d = r["run_id"], r["split"], r["district"]
        cc = c.DISTRICTS[d]["cc"]
        zr = zm[(d, r["stem"])]
        try:
            run_dir = guard.open_run(rid, "truth", r["run_dir"])
            res, meta = ex.extract_run(run_dir, zr)
        except Exception as e:
            failed.append((rid, str(e)[:200]))
            continue
        meta_all[rid] = meta
        assert res["zones"] == [z["zone"] for z in zr]
        n = len(zr)
        arr = np.stack([res[k] for k in c.TARGET_NAMES], -1).astype(np.float32)
        nan_t += int((~np.isfinite(arr)).sum())
        mm[s][off[s]:off[s] + n] = arr
        off[s] += n
        fk = [int(z["floor_k"]) for z in zr]
        hids = [plc[rid][z["zone"]]["hid"] for z in zr] if r["mode"] == "O" else [None] * n
        hidx = [hh_index[cc][h] if h is not None else -1 for h in hids]
        bl = bld_tab[(d, r["stem"])]
        for j, z in enumerate(zr):
            fr = flat_tab[(d, z["zone"])]
            rec = {"run_id": rid, "split": s, "district": d, "country": cc, "stem": r["stem"], "mode": r["mode"], "zone": z["zone"], "floor": fk[j],
                   "hid": hids[j] if hids[j] is not None else "", "hh_index": hidx[j]}
            for nm, lo in (("nb_same", [g for g in range(n) if fk[g] == fk[j] and g != j]), ("nb_above", [g for g in range(n) if fk[g] == fk[j] + 1]),
                           ("nb_below", [g for g in range(n) if fk[g] == fk[j] - 1])):
                rec[nm] = ";".join(str(hidx[g]) for g in lo) if r["mode"] == "O" else ""
            for k_ in c.COUNTRIES:
                rec["s_ctry_" + k_] = 1.0 if cc == k_ else 0.0
            for k_ in c.CLASSES:
                rec["s_cls_" + k_] = 1.0 if bl["class"] == k_ else 0.0
            for b in bands:
                rec["s_age_" + b.replace(".", "_")] = 1.0 if bl["age_band_prepared"] == b else 0.0
            for src, nm in c.BLD_NUMERIC + c.BLD_FLAGS:
                rec[nm] = float(bl[src])
            for src, nm in c.FLAT_NUMERIC + c.FLAT_FLAGS:
                rec[nm] = float(fr[src])
            recs[s].append(rec)
    for s in splits:
        mm[s].flush()
        if off[s] != nfl[s]:
            print("INFO split %s: %d flat rows written of %d announced (failed runs)" % (s, off[s], nfl[s]), flush=True)
    # Step 9k item 3 (2): the memmap was sized from the zone map; a failed run leaves trailing zero rows. Truncate to the rows written
    # (switch A9_TRUNCATE_TARGETS=0 restores the old behaviour, which the rows check below then reports as FAIL).
    if os.environ.get("A9_TRUNCATE_TARGETS", "1") == "1":
        for s in splits:
            if off[s] != nfl[s]:
                tp = os.path.join(out_dir, "targets_%s.npy" % s)
                del mm[s]
                src = np.load(tp, mmap_mode="r")
                tmp = tp + ".tmp.npy"
                dst = np.lib.format.open_memmap(tmp, mode="w+", dtype=np.float32, shape=(off[s], H, 3))
                for a0 in range(0, off[s], 256):
                    dst[a0:a0 + 256] = src[a0:min(a0 + 256, off[s])]
                dst.flush()
                del dst, src
                os.replace(tmp, tp)
                print("INFO split %s: targets_%s.npy truncated from %d to %d rows" % (s, s, nfl[s], off[s]), flush=True)
    chk("all_allowed_runs_extracted", not failed, "failed=%d %s" % (len(failed), failed[:3]))
    # ---- 5. flats tables, static z-score on development, clipped to the development range
    flats = {s: pd.DataFrame(recs[s]) for s in splits}
    zcols = c.zscored_names()
    static_norm = {}
    if "development" in flats and len(flats["development"]):
        dev = flats["development"]
        for nm in zcols:
            v = dev[nm].to_numpy(dtype=np.float64)
            sd = float(v.std())
            static_norm[nm] = {"mean": float(v.mean()), "sd": sd if sd > 0 else 1.0, "lo": float(v.min()), "hi": float(v.max())}
        for s in splits:
            for nm in zcols:
                st = static_norm[nm]
                flats[s][nm] = ((flats[s][nm].clip(st["lo"], st["hi"]) - st["mean"]) / st["sd"]).astype(np.float64)
    else:
        chk("static_norm_from_development", False, "no development flats: static columns cannot be z-scored")
    for s in splits:
        flats[s] = flats[s].reset_index(drop=True)
        pth = write_table(flats[s], os.path.join(out_dir, "flats_%s" % s))
        stamp("%s rows %d runs %d" % (os.path.basename(pth), len(flats[s]), flats[s]["run_id"].nunique() if len(flats[s]) else 0))
        chk("targets_rows_equal_flats_rows_%s" % s, targets_rows_match(os.path.join(out_dir, "targets_%s.npy" % s), len(flats[s])),
            "targets shape %s, flats rows %d" % (tuple(np.load(os.path.join(out_dir, "targets_%s.npy" % s), mmap_mode="r").shape), len(flats[s])))
    # ---- 6. leakage guard on the full input list, list equals spec
    some = next((flats[s] for s in splits if len(flats[s])), None)
    cols = list(some.columns) if some is not None else []
    present = c.HH_CHANNELS + c.NB_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS + [x for x in cols if x.startswith("s_")]
    chk("input_list_equals_spec", sorted(present) == sorted(names_all), "n_inputs=%d n_spec=%d" % (len(present), len(names_all)))
    ok, bad = c.check_features(present)
    chk("check_features_full_input_list", ok, "n=%d forbidden_hits=%s" % (len(present), bad))
    nan_static = sum(int(flats[s][[x for x in cols if x.startswith("s_")]].isna().sum().sum()) for s in splits if len(flats[s]))
    json.dump({"static": [x for x in cols if x.startswith("s_")], "zscored_clipped_on_development": zcols, "age_bands": bands,
               "id_columns_never_inputs": ["run_id", "split", "district", "country", "stem", "mode", "zone", "floor", "hid", "hh_index", "nb_same", "nb_above", "nb_below"],
               "feature_forbidden": c.FEATURE_FORBIDDEN}, open(os.path.join(out_dir, "static_cols.json"), "w"), indent=1)
    # ---- 7. pairs (same flat in two runs of one split, different household)
    for s in ("development", "validation"):
        if s not in flats:
            continue
        df = flats[s]
        grp = df[df["mode"] == "O"].groupby(["district", "stem", "zone"]).indices if len(df) else {}
        sub = df[df["mode"] == "O"]
        hid_code = pd.factorize(sub["country"] + "|" + sub["hid"])[0]
        ridx = sub.index.to_numpy()
        A, B, alt = [], [], 0
        for key, idx in grp.items():
            m = len(idx)
            if m < 2:
                continue
            ia, ib = np.triu_indices(m, 1)
            keep = hid_code[idx[ia]] != hid_code[idx[ib]]
            A.append(ridx[idx[ia][keep]]); B.append(ridx[idx[ib][keep]])
            cnt = np.bincount(hid_code[idx])
            alt += m * (m - 1) // 2 - int((cnt * (cnt - 1) // 2).sum())
        ra = np.concatenate(A) if A else np.zeros(0, dtype=np.int64)
        rb = np.concatenate(B) if B else np.zeros(0, dtype=np.int64)
        write_table(pd.DataFrame({"row_a": ra.astype(np.int64), "row_b": rb.astype(np.int64)}), os.path.join(out_dir, "pairs_%s" % s))
        chk("pairs_%s_two_methods_agree" % s, len(ra) == alt, "pairs=%d second_method=%d" % (len(ra), alt))
    # ---- 8. norm.json (development flat-hours), as s5_store.py:338-371 plus the static block
    norm = {"source": None, "targets": {}, "channels": {}, "static": static_norm}
    if "development" in flats and len(flats["development"]):
        dev = flats["development"]
        nf = len(dev)
        N = float(nf) * H
        norm["source"] = "development flat-hours (%d flats x %d h)" % (nf, H)
        T = np.load(os.path.join(out_dir, "targets_development.npy"), mmap_mode="r")
        s1, s2 = np.zeros(3), np.zeros(3)
        for a0 in range(0, nf, 256):
            x = np.asarray(T[a0:a0 + 256]).astype(np.float64)
            s1 += x.sum((0, 1)); s2 += (x ** 2).sum((0, 1))
        for i, nm in enumerate(("heating", "cooling", "equipment")):
            mu = s1[i] / N
            norm["targets"][nm] = {"mean": mu, "sd": math.sqrt(max(s2[i] / N - mu * mu, 0.0))}
        acc = {nm: [0.0, 0.0] for nm in c.HH_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS}
        for cc in c.COUNTRIES:
            sub = dev[(dev["country"] == cc) & (dev["hh_index"] >= 0)]
            if len(sub) and cc in HHA:
                cnt = np.bincount(sub["hh_index"].to_numpy(), minlength=len(hh_index[cc]))
                for nm, arr in HHA[cc].items():
                    a64 = arr.astype(np.float64)
                    acc[nm][0] += float((cnt * a64.sum(1)).sum()); acc[nm][1] += float((cnt * (a64 ** 2).sum(1)).sum())
        for d in wmat:
            n_d = int((dev["district"] == d).sum())
            w = wmat[d].astype(np.float64)
            for k_, nm in enumerate(c.WEATHER_CHANNELS):
                acc[nm][0] += n_d * float(w[:, k_].sum()); acc[nm][1] += n_d * float((w[:, k_] ** 2).sum())
            for k_, nm in enumerate(c.CALENDAR_CHANNELS):
                col = cal[d][:, k_].astype(np.float64)
                acc[nm][0] += n_d * float(col.sum()); acc[nm][1] += n_d * float((col ** 2).sum())
        for nm, (a1, a2) in acc.items():
            mu = a1 / N
            norm["channels"][nm] = {"mean": mu, "sd": math.sqrt(max(a2 / N - mu * mu, 0.0))}
    norm["note"] = ("neighbour channels nb_*_people and nb_*_appl_w use the people and appl_w statistics; flags are not standardised; hh channels "
                    "are weighted over development flats that have a household; static block: z = (clip(x, lo, hi) - mean) / sd per development flat, "
                    "already applied in flats_<split>; one-hots and flags are raw")
    json.dump(norm, open(os.path.join(out_dir, "norm.json"), "w"), indent=1)
    # ---- 9. remaining checks
    chk("no_nan", (nan_hh + nan_w + nan_static + nan_t) == 0, "hh=%d weather=%d static=%d targets=%d calendar=%d" %
        (nan_hh, nan_w, nan_static, nan_t, sum(int((~np.isfinite(v)).sum()) for v in cal.values())))
    olp = os.path.join(out_dir, "openlog_%s.tsv" % tag)
    if os.path.exists(olp):
        os.remove(olp)
    guard.flush(olp)
    n_open, bad_open, ids_open = 0, 0, set()
    allowed_all = set().union(*[set(v) for v in allowed.values()]) if allowed else set()
    for ln in io.open(olp, encoding="utf-8").read().splitlines()[1:]:
        k_, rid, p = ln.split("\t")
        n_open += 1; ids_open.add(rid); bad_open += 0 if rid in allowed_all else 1
    chk("openlog_outside_allowed_zero", bad_open == 0 and not (set(refused) & ids_open),
        "log lines=%d distinct_runs=%d outside=%d refused_ids_in_log=%d" % (n_open, len(ids_open), bad_open, len(set(refused) & ids_open)))
    readme = [
        "# 5J Model A store (written %s by a9_store.py)" % time.strftime("%Y-%m-%d %H:%M"),
        "hh_<cc>.npz : hid, presence, appl_frac, people (= members x presence), appl_w (= design_w x appl_frac) n_hh x 8760 float32; members, design_w",
        "weather_<district>.npy : 8760 x 7 float32 = EPW columns (0-based) 6 dry bulb C, 7 dew point C, 8 RH %, 13 GHI, 14 DNI, 15 DHI (Wh/m2), 21 wind m/s",
        "calendar_<district>.npy : 8760 x 5 float32 = hour sin, hour cos, day-of-year sin, day-of-year cos (period 365), day of week (Monday = 0); Madrid year 2010, Bologna 2014",
        "flats_<split> (.parquet or .csv.gz) : one row per (run, flat = zone); id columns (never inputs) + nb_same/nb_above/nb_below = ';'-joined hh_index of the flats on the same storey (flat itself excluded) / storey above / storey below by floor_k; s_* static inputs (numeric ones z-scored on development, clipped to the development range)",
        "targets_<split>.npy : float32 n_rows x 8760 x 3 (heating, cooling, equipment kWh per hour per flat), same row order as flats_<split>; total_elec = equipment + (heating + cooling) / 3.0",
        "pairs_<split> : row_a, row_b into flats_<split> (same district, building, flat; different runs; different household); O runs only",
        "norm.json : development mean and SD of targets and dynamic channels, plus the static block; static_cols.json : input names and id columns",
        "neighbour channels (assembled by Store.assemble_row): mean over the listed neighbour flats of people / appl_w; flag = 1 when the list is not empty (value 0 then)",
    ]
    io.open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8").write("\n".join(readme) + "\n")
    nfail = sum(1 for _, ok in RES if ok is False)
    print("STORE_DONE checks=%d fail=%d seconds=%.0f" % (len(RES), nfail, time.time() - t0), flush=True)
    return {"refused": refused, "failed": failed, "meta": meta_all, "n_flats": {s: len(flats[s]) for s in splits}, "nfail": nfail,
            "names": names_all, "bands": bands}


# ================================================================================================ read side (what a training task uses)
class Store(object):
    def __init__(self, out_dir):
        self.d = out_dir
        self.norm = json.load(open(os.path.join(out_dir, "norm.json")))
        self._flats, self._hh, self._w, self._cal = {}, {}, {}, {}

    def flats(self, split):
        if split not in self._flats:
            self._flats[split] = read_table(os.path.join(self.d, "flats_%s" % split))
        return self._flats[split]

    def targets(self, split):
        return np.load(os.path.join(self.d, "targets_%s.npy" % split), mmap_mode="r")

    def hh(self, cc):
        if cc not in self._hh:
            z = np.load(os.path.join(self.d, "hh_%s.npz" % cc))
            self._hh[cc] = {k: z[k] for k in z.files}
        return self._hh[cc]

    def weather(self, d):
        if d not in self._w:
            self._w[d] = np.load(os.path.join(self.d, "weather_%s.npy" % d))
        return self._w[d]

    def calendar(self, d):
        if d not in self._cal:
            self._cal[d] = np.load(os.path.join(self.d, "calendar_%s.npy" % d))
        return self._cal[d]

    def assemble_row(self, split, i, t):
        """{input name: value} of flat row i at hour t (0-based, raw units; static z-scored as stored). Household channels are 0 when hh_index = -1."""
        df = self.flats(split)
        r = df.iloc[i]
        cc, d = r["country"], r["district"]
        out = {}
        hi = int(r["hh_index"])
        if hi >= 0:
            hh = self.hh(cc)
            for nm in c.HH_CHANNELS:
                out[nm] = float(hh[nm][hi, t])
        else:
            for nm in c.HH_CHANNELS:
                out[nm] = 0.0
        for grp in ("same", "above", "below"):
            lst = [int(x) for x in str(r["nb_" + grp]).split(";") if x != "" and x != "nan"] if hi >= 0 else []
            if lst:
                hh = self.hh(cc)
                out["nb_%s_people" % grp] = float(np.mean([hh["people"][g, t] for g in lst]))
                out["nb_%s_appl_w" % grp] = float(np.mean([hh["appl_w"][g, t] for g in lst]))
                out["nb_%s_flag" % grp] = 1.0
            else:
                out["nb_%s_people" % grp] = 0.0
                out["nb_%s_appl_w" % grp] = 0.0
                out["nb_%s_flag" % grp] = 0.0
        w = self.weather(d)[t]
        for k_, nm in enumerate(c.WEATHER_CHANNELS):
            out[nm] = float(w[k_])
        cl = self.calendar(d)[t]
        for k_, nm in enumerate(c.CALENDAR_CHANNELS):
            out[nm] = float(cl[k_])
        for col in df.columns:
            if col.startswith("s_"):
                out[col] = float(r[col])
        return out


def dir_bytes(d):
    return sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))


# ================================================================================================ the test
def _raw_col(csv_path, label):
    """One column of an eplusout.csv by exact label, csv module only (the manager-style re-read)."""
    with io.open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        p = head.index(label)
        return np.array([float(r[p]) for r in rd])


def _raw_series(p):
    return np.loadtxt(p, skiprows=1)


def _close(a, b, tol=1e-6):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return bool((np.abs(a - b) <= tol * np.maximum(1.0, np.abs(b))).all())


def heating_candidates(head, zone):
    """Step 9n: header positions of the zone's SUPPLY-AIR total heating column, by the exact label. The 9k rule (startswith zone + 'Total Heating Energy'
    in h) also matched 'Zone Ideal Loads Zone Total Heating Energy' and so found two columns for every zone."""
    want = "%s IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](Hourly)" % zone.upper()
    return [k for k, h in enumerate(head) if h.strip() == want]


def heating_rule_selftest():
    """Step 9n item 3: the unique-column rule passes on the 9k case (both Supply Air and Zone Total Heating columns present for the zone) and is seen
    failing on a planted header list with two exact supply-air columns. Returns True when both behave."""
    z = "05E17B2BF818153B_F0_DWELLING_0"
    pre = z + " IDEAL LOADS AIR SYSTEM:Zone Ideal Loads "
    case_9k = ["Date/Time", pre + "Supply Air Total Heating Energy [J](Hourly)", pre + "Supply Air Total Cooling Energy [J](Hourly)",
               pre + "Zone Total Heating Energy [J](Hourly)", pre + "Zone Total Cooling Energy [J](Hourly)", pre + "Supply Air Sensible Heating Energy [J](Hourly)"]
    old_rule = [k for k, h in enumerate(case_9k) if h.startswith(z + " IDEAL LOADS AIR SYSTEM") and "Total Heating Energy" in h and h.endswith("(Hourly)")]
    new_rule = heating_candidates(case_9k, z)
    planted = case_9k + [pre + "Supply Air Total Heating Energy [J](Hourly)"]
    planted_new = heating_candidates(planted, z)
    chk("heating_column_unique_by_position_on_9k_case", len(new_rule) == 1, "exact supply-air rule finds %s (the old substring rule found %s = the 9k defect)" % (new_rule, old_rule))
    chk("heating_column_unique_by_position_seen_failing_planted_two_exact_columns", len(planted_new) == 2,
        "planted header list with two exact supply-air columns: candidates %s, the unique check would say FAIL (len != 1)" % planted_new)
    return len(new_rule) == 1 and len(planted_new) == 2 and len(old_rule) == 2


def _raw_col_pos(csv_path, pos):
    """Step 9k: one column of an eplusout.csv by header POSITION; returns (header text at that position, values)."""
    with io.open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        return head[pos], np.array([float(r[pos]) for r in rd])


def test_main(base, win="/speed-scratch/o_iseri/5J/step9c/win/", epwd="/speed-scratch/o_iseri/5J/step9c/epw/", runs_dir=None, kinds="D,O", small_stem="7307694dddf93fb6"):
    """Step 9k: runs_dir (read-only run folders <stem>_<run>), kinds (e.g. D,O,DF,OF) and small_stem extend the 9g test; with runs_dir set the 9k checks are added
    (keep_csv present, heating by header position, targets rows = flats rows incl. a planted extra row, triangle refusal, SIZE with and without fast runs).
    Defaults reproduce the 9g test exactly."""
    v3 = runs_dir is not None
    kinds = tuple(kinds.split(","))
    base = base.rstrip("/") + "/"
    W = win.rstrip("/") + "/"
    EPWD = epwd.rstrip("/") + "/"
    zmap_path, static_dir = base + "in/zone_map.csv", base + "in/static"
    zm = c.zone_map(zmap_path)
    man = [r for r in c.read_csv_rows(W + "manifest.csv") if r["run"] in kinds]
    rows = []
    for r in man:
        rid = "%s_%s" % (r["stem"], r["run"])
        rows.append({"run_id": rid, "split": "development", "district": r["district"], "stem": r["stem"], "mode": r["run"][0],
                     "run_dir": ((runs_dir.rstrip("/") + "/") if v3 else base + "runs/") + rid,
                     "placement_csv": (W + "%s/placement_%s.csv" % (r["district"], r["stem"])) if r["run"][0] == "O" else "",
                     "epw": EPWD + r["epw"], "n_flats": r["n_flats"], "fast": r["run"] in ("DF", "OF")})
    if v3:
        for r in rows:        # item 3 (4): the hourly csv must still be in the run folder (nothing deleted it before the extraction)
            chk("keep_csv_present_" + r["run_id"], os.path.isfile(r["run_dir"] + "/eplusout.csv") and os.path.getsize(r["run_dir"] + "/eplusout.csv") > 0,
                r["run_dir"] + "/eplusout.csv")
    # ---------------- 1. extraction of every D and O run (the extractor's own checks per run)
    os.makedirs(base + "extracted", exist_ok=True)
    mf = base + "extract_manifest.csv"
    with io.open(mf, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["run_id", "district", "stem", "mode", "run_dir"])
        for r in rows:
            w.writerow([r["run_id"], r["district"], r["stem"], r["mode"], r["run_dir"]])
    ex.main(["x", mf, zmap_path, base + "extracted"])
    okrun, bad_run = {}, {}
    for r in rows:
        m = json.load(open(base + "extracted/%s.json" % r["run_id"]))
        if m["status"] == "OK":
            okrun[r["run_id"]] = m
            tvx = m["table_vs_extracted_rel"]
            chk("extract_" + r["run_id"], m["zone_count_ok"] if "zone_count_ok" in m else m["n_zones"] == int(r["n_flats"]),
                "zones=%d (manifest flats %s) rows=%d status=%s severe=%s annual_vs_sum_hourly_max_rel=%.2e equipment_source=%s table_vs_extracted_rel(INFO)=%s extras=%d" %
                (m["n_zones"], r["n_flats"], m["rows"], m["completed"], m["severe"], m["annual_vs_sum_hourly_max_rel"], m["equipment_source"][:24],
                 {k: round(v, 5) for k, v in tvx.items()}, len(m["extras_present"])))
        else:
            bad_run[r["run_id"]] = m["reason"]
            chk("extract_" + r["run_id"], None, "run could not be extracted: %s" % m["reason"])
    o_ok = [r for r in rows if r["mode"] == "O" and not r["fast"] and r["run_id"] in okrun]
    if v3:        # triangle building: refused by the clean-status rule is the RIGHT behaviour; everything else must extract
        tri = [r["run_id"] for r in rows if r["stem"] == "1271cddbf6bd1e8a"]
        other_bad = [rid for rid in bad_run if rid not in tri]
        chk("triangle_runs_refused_by_clean_rule_others_extracted", all(rid in bad_run and "evere" in bad_run[rid] for rid in tri) and not other_bad,
            "triangle runs refused %d of %d (reasons: %s); other runs not extracted: %s" % (sum(1 for rid in tri if rid in bad_run), len(tri), sorted({bad_run[rid][:60] for rid in tri if rid in bad_run}), other_bad))
    if not o_ok:
        chk("store_build", None, "no O run could be extracted: store test NOT_EVALUABLE")
        return summary()
    # ---------------- 2. test store from the O runs (made-up allowed list: all O runs = development, no validation)
    allowed = {"development": [r["run_id"] for r in rows if r["mode"] == "O" and not r["fast"]], "validation": []}
    json.dump(allowed, open(base + "allowed_test.json", "w"), indent=1)
    sdir = base + "store/"
    info = build_store([r for r in rows if r["mode"] == "O" and not r["fast"]], allowed, zmap_path, static_dir, sdir, "test")
    S = Store(sdir)
    fl = S.flats("development")
    T = S.targets("development")
    # ---------------- 3. G-c3 style: hourly equipment = design level x placement series within 0.5 % (own code)
    worst_all, nflat_c3 = 0.0, 0
    for r in o_ok:
        sub = fl[fl["run_id"] == r["run_id"]]
        for pr in c.read_csv_rows(r["placement_csv"]):
            i = int(sub.index[sub["zone"] == pr["dwelling_zone"]][0])
            exp = float(pr["appliance_peak_w"]) * _raw_series(pr["appliance_csv"]) / 1000.0
            got = np.asarray(T[i, :, 2], dtype=np.float64)
            pos = exp > 1e-9
            worst_all = max(worst_all, float((np.abs(got[pos] - exp[pos]) / exp[pos]).max()))
            nflat_c3 += 1
    chk("gc3_equipment_equals_design_x_series_0p5pct", worst_all <= 0.005, "flats=%d max_rel_dev=%.3e (tolerance 5e-3)" % (nflat_c3, worst_all))
    # ---------------- 4. manager-style re-derivation: one O flat, heating straight from eplusout.csv, one hour of inputs straight from files
    pick = next((r for r in o_ok if r["stem"] == "919761afea1827b3"), o_ok[0])
    sub = fl[fl["run_id"] == pick["run_id"]]
    fks = sorted(sub["floor"].unique())
    mid = fks[len(fks) // 2]
    i = int(sub.index[sub["floor"] == mid][0])
    zone = fl["zone"].iat[i]
    lab = "%s IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](Hourly)" % zone.upper()
    if v3:        # item 3 (3): by header POSITION found by substring rules (not the built label), then the header at that position must equal the heating name
        with io.open(pick["run_dir"] + "/eplusout.csv", newline="", encoding="utf-8", errors="replace") as fh:
            head0 = next(csv.reader(fh))
        cand = heating_candidates(head0, zone)          # Step 9n: exact supply-air label (the 9k substring rule matched two columns)
        chk("heating_column_unique_by_position", len(cand) == 1, "candidates at header positions %s" % cand)
        hpos, raw_h = _raw_col_pos(pick["run_dir"] + "/eplusout.csv", cand[0])
        chk("heating_header_at_position_is_the_heating_name", hpos == lab, "position %d header %r expected %r" % (cand[0], hpos, lab))
        raw_h = raw_h / 3.6e6
    else:
        raw_h = _raw_col(pick["run_dir"] + "/eplusout.csv", lab) / 3.6e6
    chk("rederive_heating_one_flat", _close(np.asarray(T[i, :, 0], dtype=float), raw_h, 1e-6),
        "run=%s zone=%s annual_raw=%.3f annual_store=%.3f max_abs_diff=%.2e" % (pick["run_id"], zone, raw_h.sum(), float(np.asarray(T[i, :, 0], dtype=float).sum()),
                                                                                 float(np.abs(np.asarray(T[i, :, 0], dtype=float) - raw_h).max())))
    pr = [p for p in c.read_csv_rows(pick["placement_csv"]) if p["dwelling_zone"] == zone][0]
    t = 4000
    pres, frac = _raw_series(pr["presence_csv"]), _raw_series(pr["appliance_csv"])
    epw_lines = io.open(pick["epw"], encoding="latin-1").read().splitlines()[8:]
    ev = [float(epw_lines[t].split(",")[k]) for k in c.EPW_COLS]
    got = S.assemble_row("development", i, t)
    exp = {"presence": pres[t], "appl_frac": frac[t], "people": float(pr["n_members"]) * pres[t], "appl_w": float(pr["appliance_peak_w"]) * frac[t]}
    for k_, nm in enumerate(c.WEATHER_CHANNELS):
        exp[nm] = ev[k_]
    exp["hour_sin"] = math.sin(2 * math.pi * (t % 24) / 24); exp["hour_cos"] = math.cos(2 * math.pi * (t % 24) / 24)
    exp["doy_sin"] = math.sin(2 * math.pi * (t // 24) / 365); exp["doy_cos"] = math.cos(2 * math.pi * (t // 24) / 365)
    import datetime
    exp["dow"] = (datetime.date(c.DISTRICTS[pick["district"]]["year"], 1, 1).weekday() + t // 24) % 7
    diffs = {k: abs(got[k] - v) / max(1.0, abs(v)) for k, v in exp.items()}
    chk("rederive_inputs_one_hour", max(diffs.values()) <= 1e-6, "zone=%s hour=%d channels=%d max_rel_diff=%.2e (worst %s)" %
        (zone, t, len(exp), max(diffs.values()), max(diffs, key=diffs.get)))
    # static: a z-scored value re-derived from the static table and norm.json
    ftab, btab, _b = c.static_tables(static_dir)
    fr_ = ftab[(pick["district"], zone)]
    st = S.norm["static"]["s_floor_area"]
    expz = (min(max(float(fr_["floor_area_m2"]), st["lo"]), st["hi"]) - st["mean"]) / st["sd"]
    chk("rederive_static_one_value", abs(got["s_floor_area"] - expz) <= 1e-9, "s_floor_area stored %.6f re-derived %.6f (raw %.4f m2, dev mean %.3f sd %.3f)" %
        (got["s_floor_area"], expz, float(fr_["floor_area_m2"]), st["mean"], st["sd"]))
    # ---------------- 5. neighbour channels on a store with DISTINCT households (the test series are identical for every flat, so they cannot show a wrong index)
    small = [r for r in o_ok if r["stem"] == small_stem]
    if not small:
        chk("neighbour_channels_by_hand", None, "ES small O run not extracted")
    else:
        sm = small[0]
        zr = zm[(sm["district"], sm["stem"])]
        sdir2 = base + "synth/"
        os.makedirs(sdir2, exist_ok=True)
        base_p, base_a = _raw_series(c.read_csv_rows(sm["placement_csv"])[0]["presence_csv"]), _raw_series(c.read_csv_rows(sm["placement_csv"])[0]["appliance_csv"])
        spec = {}
        with io.open(sdir2 + "placement_synth.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["dwelling_zone", "hid", "presence_csv", "appliance_csv", "n_members", "appliance_peak_w"])
            for j, z in enumerate(zr):
                pp, ap = sdir2 + "pres_%d.csv" % j, sdir2 + "appl_%d.csv" % j
                np.savetxt(pp, np.clip(base_p * (0.1 + 0.07 * j), 0, 1), header="presence", comments="", fmt="%.6f")
                np.savetxt(ap, np.clip(base_a * (0.2 + 0.05 * j), 0, 1), header="appliance", comments="", fmt="%.6f")
                mem, pk = 1 + j % 4, 100.0 + 50.0 * j
                w.writerow([z["zone"], "S%d" % j, pp, ap, mem, pk])
                spec[z["zone"]] = (pp, ap, mem, pk)
        srow = dict(sm); srow["run_id"] = "SYNTH_" + sm["run_id"]; srow["placement_csv"] = sdir2 + "placement_synth.csv"
        info2 = build_store([srow], {"development": [srow["run_id"]]}, zmap_path, static_dir, base + "store_synth/", "synth")
        S2 = Store(base + "store_synth/")
        ser = [(_raw_series(spec[z["zone"]][0]), _raw_series(spec[z["zone"]][1])) for z in zr]       # the files as written, read by the test itself
        f2 = S2.flats("development")
        bad_n, n_nonempty, checked = 0, 0, 0
        for rule_shift, label in ((0, "right"), (2, "planted_wrong_storey_rule")):
            bad_n = 0
            for j, z in enumerate(zr):
                fk = int(z["floor_k"])
                lists = {"same": [g for g, z2 in enumerate(zr) if int(z2["floor_k"]) == fk + (rule_shift if rule_shift else 0) and g != j],
                         "above": [g for g, z2 in enumerate(zr) if int(z2["floor_k"]) == fk + 1 + rule_shift],
                         "below": [g for g, z2 in enumerate(zr) if int(z2["floor_k"]) == fk - 1 - rule_shift]}
                for t in (100, 4000, 8000):
                    gi = S2.assemble_row("development", int(f2.index[f2["zone"] == z["zone"]][0]), t)
                    for grp, lst in lists.items():
                        ppl = [spec[zr[g]["zone"]][2] * ser[g][0][t] for g in lst]
                        apw = [spec[zr[g]["zone"]][3] * ser[g][1][t] for g in lst]
                        e_p, e_a, e_f = (float(np.mean(ppl)), float(np.mean(apw)), 1.0) if lst else (0.0, 0.0, 0.0)
                        if rule_shift == 0 and lst:
                            n_nonempty += 1
                        checked += 1
                        if not (abs(gi["nb_%s_people" % grp] - e_p) <= 1e-6 * max(1, abs(e_p)) and abs(gi["nb_%s_appl_w" % grp] - e_a) <= 1e-6 * max(1, abs(e_a)) and gi["nb_%s_flag" % grp] == e_f):
                            bad_n += 1
            if rule_shift == 0:
                chk("neighbour_channels_by_hand", bad_n == 0 and n_nonempty > 0, "flats=%d hours=3 groups_checked=%d non_empty_groups=%d mismatches=%d (households differ per flat, distinct values)" % (len(zr), checked, n_nonempty, bad_n))
            else:
                chk("neighbour_check_fails_on_planted_wrong_rule", bad_n > 0, "same check with the storey rule shifted by 2: mismatches=%d (must be > 0 to count as seen failing)" % bad_n)
    # ---------------- 6. check_features on the real list, and seen failing with a target name added
    names = c.all_input_names(info["bands"])
    ok1, bad1 = c.check_features(names)
    ok2, bad2 = c.check_features(names + ["heating_kwh_lag24"])
    chk("check_features_real_list_passes", ok1, "n=%d bad=%s" % (len(names), bad1))
    chk("check_features_fails_with_heating_kwh_lag24", (not ok2) and bad2 == ["heating_kwh_lag24"], "ok=%s bad=%s" % (ok2, bad2))
    # ---------------- 7. the guard refuses an id that is not in the list and logs nothing for it (and the builder skips such a row)
    g = c.RunGuard({"development": [o["run_id"] for o in o_ok][:1]})
    raised, nlog = False, len(g.log)
    try:
        g.open_run("NOT_A_LISTED_RUN_O", "truth", base + "runs/NOT_A_LISTED_RUN_O")
    except PermissionError:
        raised = True
    gl = base + "guard_log_test.tsv"
    if os.path.exists(gl):
        os.remove(gl)
    g.flush(gl)
    chk("guard_refuses_unlisted_id_and_logs_nothing", raised and len(g.log) == 0 and nlog == 0 and "NOT_A_LISTED_RUN_O" not in io.open(gl).read() and g.refused == ["NOT_A_LISTED_RUN_O"],
        "raised=%s log_lines_for_it=%d refused_list=%s" % (raised, int("NOT_A_LISTED_RUN_O" in io.open(gl).read()), g.refused))
    if len(o_ok) >= 2:
        two = [r for r in rows if r["run_id"] == o_ok[0]["run_id"] or r["run_id"] == o_ok[1]["run_id"]]
        n0 = len(RES)
        info3 = build_store(two, {"development": [o_ok[0]["run_id"]]}, zmap_path, static_dir, base + "store_refuse/", "refuse")
        logtxt = io.open(base + "store_refuse/openlog_refuse.tsv").read()
        fl3 = Store(base + "store_refuse/").flats("development")
        chk("builder_skips_run_not_in_allowed_list", info3["refused"] == [o_ok[1]["run_id"]] and o_ok[1]["run_id"] not in logtxt and o_ok[1]["run_id"] not in set(fl3["run_id"]),
            "refused=%s in_open_log=%s in_store=%s" % (info3["refused"], o_ok[1]["run_id"] in logtxt, o_ok[1]["run_id"] in set(fl3["run_id"])))
    # ---------------- 8. no NaN in the whole test store, size per flat-year
    nan_total = 0
    for a0 in range(0, len(fl), 64):
        nan_total += int((~np.isfinite(np.asarray(T[a0:a0 + 64]))).sum())
    nan_total += sum(int((~np.isfinite(fl[x].to_numpy(dtype=float))).sum()) for x in fl.columns if x.startswith("s_"))
    chk("no_nan_in_test_store", nan_total == 0, "non-finite cells in targets and static: %d" % nan_total)
    nb = dir_bytes(sdir)
    tb = os.path.getsize(sdir + "targets_development.npy")
    fb = sum(os.path.getsize(sdir + f) for f in os.listdir(sdir) if f.startswith("flats_development"))
    print("SIZE flats=%d store_total_bytes=%d MB_per_flat_year_total=%.4f targets_only_MB_per_flat_year=%.4f flats_table_MB_per_flat_year=%.5f hh_files_MB_total=%.3f"
          % (len(fl), nb, nb / len(fl) / 1e6, tb / len(fl) / 1e6, fb / len(fl) / 1e6, sum(os.path.getsize(sdir + f) for f in os.listdir(sdir) if f.startswith("hh_")) / 1e6), flush=True)
    if v3:
        # item 3 (2): rows of targets = rows of flats on the real store, and the check seen failing on a planted extra row
        tp = sdir + "targets_development.npy"
        chk("targets_rows_equal_flats_rows_real", targets_rows_match(tp, len(fl)), "targets shape %s flats %d" % (tuple(np.load(tp, mmap_mode="r").shape), len(fl)))
        pl = base + "planted_extra_row_targets.npy"
        src = np.load(tp, mmap_mode="r")
        dst = np.lib.format.open_memmap(pl, mode="w+", dtype=np.float32, shape=(len(fl) + 1, H, 3))
        dst[:len(fl)] = src[:]
        dst.flush()
        del dst
        chk("targets_rows_check_fails_on_planted_extra_row", not targets_rows_match(pl, len(fl)), "planted file has %d rows, flats %d: the rows check must say False" % (len(fl) + 1, len(fl)))
        os.remove(pl)
        # SIZE with the fast runs: a second store from the O runs and the OF runs
        f_rows = [r for r in rows if r["mode"] == "O"]
        allowed_f = {"development": [r["run_id"] for r in f_rows], "validation": []}
        build_store(f_rows, allowed_f, zmap_path, static_dir, base + "store_fast/", "withfast")
        sf = base + "store_fast/"
        flf = Store(sf).flats("development")
        nbf = dir_bytes(sf)
        print("SIZE_WITH_FAST_RUNS flats=%d store_total_bytes=%d MB_per_flat_year_total=%.4f targets_only_MB_per_flat_year=%.4f (O and OF runs; WITHOUT fast runs see the SIZE line above)"
              % (len(flf), nbf, nbf / len(flf) / 1e6, os.path.getsize(sf + "targets_development.npy") / len(flf) / 1e6), flush=True)
    return summary()


# ================================================================================================ Step 9n: campaign mode
# The store is built from what the campaign KEEPS (a9_campaign_task.py:49 KEEP, :433 npz): results/<rid>.json + results/<rid>.npz (hourly targets),
# runs/<rid>/placement.csv + series.tar.gz (household series), b0/<cc>/ files, EPW, zone map, static tables. No EnergyPlus csv is read.
# The 9g build_store above is untouched (old behaviour reachable: `a9_store.py build ...`).
CAMPAIGN_EPW = {"ES-MAD-BERRUGUETE": "es_madrid_2009_2010_y2010.epw", "IT-BOL-GALVANI2": "it_bologna_2013_2014_y2014.epw"}
HHCH = ["presence", "appl_frac", "people", "appl_w"]


def is_test_row(r):
    """R1: a run is a TEST run when its household pool is test or its building is a test building. Decided from the plan row alone."""
    return r["pool"] == "test" or r["building_split"] == "test"


def store_split(bs, pool):
    """Store split name of a non-test run: development = dev building x dev households; validation = val building x val households;
    the two mixed cases are kept apart (never training or early stopping); b0 and default runs by building split; test -> None (refused)."""
    if pool == "test" or bs == "test":
        return None
    if pool == "b0":
        return "b0_" + bs
    if pool == "def":
        return "default_" + bs
    if bs == "dev" and pool == "dev":
        return "development"
    if bs == "val" and pool == "val":
        return "validation"
    return "x%s_h%s" % (bs, pool)


class CampaignGuard(c.RunGuard):
    """RunGuard plus a forbidden set (the test runs, from the plan): a forbidden id is refused even if some list contains it, and logs nothing."""

    def __init__(self, allowed, forbidden):
        c.RunGuard.__init__(self, allowed)
        self.forbidden = set(forbidden)

    def open_run(self, run_id, kind, run_dir):
        if run_id in self.forbidden:
            self.refused.append(run_id)
            raise PermissionError("REFUSED: run %s is a test run (R1: read only by the one scoring job)" % run_id)
        return c.RunGuard.open_run(self, run_id, kind, run_dir)


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def md5_file(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def parse_series_bytes(b, name):
    """One value per line after a one-line name, exactly 8,760 (read_series, from bytes)."""
    lines = [ln.strip() for ln in b.decode("utf-8").splitlines() if ln.strip()]
    v = np.array(lines[1:], dtype=np.float64)
    if len(v) != H:
        raise RuntimeError("%s has %d values" % (name, len(v)))
    return v


def load_campaign_run(task):
    """Worker (top level so a pool can pickle it). Reads ONLY the kept files of one non-test CLEAN run. Returns arrays + household instances."""
    rid, zones, mode = task["run_id"], task["zones"], task["mode"]
    z = np.load(task["npz"])
    got_zones = [str(x) for x in z["zones"]]
    if got_zones != zones:
        raise RuntimeError("npz zone order differs from the zone map (%s ...)" % got_zones[:2])
    arr = np.stack([z[k[:-4]] for k in c.TARGET_NAMES], -1).astype(np.float32)       # npz keys: heating, cooling, equipment (a9_campaign_task.py:433)
    if arr.shape != (len(zones), H, 3):
        raise RuntimeError("targets shape %s, expected %s" % (arr.shape, (len(zones), H, 3)))
    out = {"run_id": rid, "targets": arr, "inst": [None] * len(zones), "series": {}, "hid": [None] * len(zones)}
    if mode != "O":
        return out
    plc = {}
    for pr in c.read_csv_rows(task["placement"]):
        if pr["dwelling_zone"] in plc:
            raise RuntimeError("%s: zone %s placed twice" % (rid, pr["dwelling_zone"]))
        plc[pr["dwelling_zone"]] = pr
    if sorted(plc) != sorted(zones):
        raise RuntimeError("%s: placement zones differ from the zone map (%d vs %d)" % (rid, len(plc), len(zones)))
    import tarfile
    tf, cache = None, {}

    def get_bytes(path):
        nonlocal tf
        if path in cache:
            return cache[path]
        pth = path.replace("\\", "/")
        if "/series/" in pth:
            if tf is None:
                tf = tarfile.open(task["series_tar"], "r:gz")
            b = tf.extractfile(os.path.basename(pth)).read()
        else:
            cand = path
            if not os.path.exists(cand):
                i = pth.find("/b0/")
                if i < 0:
                    raise RuntimeError("cannot resolve series path %s" % path)
                cand = task["camp_root"].rstrip("/") + pth[i:]
            with io.open(cand, "rb") as fh:
                b = fh.read()
        cache[path] = b
        return b
    cc = task["cc"]
    for j, zn in enumerate(zones):
        pr = plc[zn]
        bp, ba = get_bytes(pr["presence_csv"]), get_bytes(pr["appliance_csv"])
        key = (cc, pr["hid"], md5_bytes(bp), md5_bytes(ba), repr(float(pr["n_members"])), repr(float(pr["appliance_peak_w"])))
        out["inst"][j] = key
        out["hid"][j] = pr["hid"]
        if key not in out["series"]:
            out["series"][key] = (parse_series_bytes(bp, pr["presence_csv"]).astype(np.float32), parse_series_bytes(ba, pr["appliance_csv"]).astype(np.float32))
    if tf is not None:
        tf.close()
    return out


def classify_campaign(rows, results_dir, guard):
    """Plan rows -> {test, missing, not_clean, src_md5, gate, ok}. A test row is never looked at (not even its status json). Every status json
    read of a non-test row goes through the guard (logged as kind `status`)."""
    o = {"test": [], "missing": [], "not_clean": [], "src_md5": [], "gate": [], "ok": [], "json_md5": {}}
    for r in rows:
        rid = r["run_id"]
        if is_test_row(r):
            o["test"].append(rid)
            continue
        p = os.path.join(results_dir, rid + ".json")
        guard.open_run(rid, "status", p)
        if not os.path.exists(p):
            o["missing"].append(rid)
            continue
        raw = io.open(p, "rb").read()
        j = json.loads(raw.decode("utf-8"))
        if not j.get("complete") or j.get("status") != "CLEAN":
            o["not_clean"].append((rid, str(j.get("status")), str(j.get("not_clean_reason") or j.get("extract_reason") or j.get("error") or "")[:120]))
        elif j.get("src_idf_md5") != r["src_idf_md5"]:
            o["src_md5"].append(rid)
        elif j.get("gc3_fail") is True or int(j.get("purity_violations") or 0) > 0:
            o["gate"].append(rid)
        else:
            o["ok"].append(r)
            o["json_md5"][rid] = md5_bytes(raw)
    return o


def write_npz_stream(path, items):
    """items: list of (name, ndarray) or (name, (shape, dtype, generator of ndarray chunks along axis 0)). Same file format as np.savez (one .npy per name)."""
    import zipfile
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
        for name, it in items:
            with zf.open(name + ".npy", "w", force_zip64=True) as f:
                if isinstance(it, np.ndarray):
                    np.lib.format.write_array(f, it, allow_pickle=False)
                else:
                    shape, dt, gen = it
                    np.lib.format.write_array_header_1_0(f, {"descr": np.lib.format.dtype_to_descr(np.dtype(dt)), "fortran_order": False, "shape": tuple(shape)})
                    for ch in gen:
                        f.write(np.ascontiguousarray(ch, dtype=dt).tobytes())


def _gc():
    import gc
    gc.collect()


def combine_rows(final_path, old_path, keep_idx, new_bin, n_new, tail_shape, dtype=np.float32):
    """final = old rows keep_idx (in order) + n_new rows of the raw binary new_bin; written to a tmp file, then moved over final_path."""
    n_keep = 0 if keep_idx is None else len(keep_idx)
    tmp = final_path + ".tmp.npy"
    dst = np.lib.format.open_memmap(tmp, mode="w+", dtype=dtype, shape=(n_keep + n_new,) + tuple(tail_shape))
    if n_keep:
        src = np.load(old_path, mmap_mode="r")
        for a0 in range(0, n_keep, 256):
            blk = keep_idx[a0:a0 + 256]
            dst[a0:a0 + len(blk)] = src[blk]
        del src
    if n_new:
        nb = np.memmap(new_bin, dtype=dtype, mode="r", shape=(n_new,) + tuple(tail_shape))
        for a0 in range(0, n_new, 256):
            blk = nb[a0:a0 + 256]
            dst[n_keep + a0:n_keep + a0 + len(blk)] = blk
        del nb
    dst.flush()
    del dst
    _gc()
    os.replace(tmp, final_path)


def gc3_rows(T, fl, HH, tol=0.005):
    """G-c3 inside the STORE: equipment target of every flat that has a household = design level x appliance series / 1000 (hours with expected > 0).
    T = targets memmap, fl = flats frame, HH = {cc: (appl_frac, design_w)}. Returns (ok, worst relative deviation, flats checked)."""
    worst, n = 0.0, 0
    for cc, (frac, dw) in HH.items():
        sub = fl[(fl["country"] == cc) & (fl["hh_index"] >= 0)]
        ri, hi = sub.index.to_numpy(), sub["hh_index"].to_numpy()
        for a0 in range(0, len(ri), 256):
            r_, h_ = ri[a0:a0 + 256], hi[a0:a0 + 256]
            exp = dw[h_][:, None].astype(np.float64) * frac[h_].astype(np.float64) / 1000.0
            got = np.asarray(T[r_, :, 2], dtype=np.float64)
            pos = exp > 1e-9
            if pos.any():
                worst = max(worst, float((np.abs(got[pos] - exp[pos]) / exp[pos]).max()))
            n += len(r_)
    return (worst <= tol and n > 0), worst, n


def rederive_heating(store_row, npz_heating, npz_equip, npz_cool, npz_total, json_annual_heat, run_heat_sum, tol_annual=1e-5):
    """One flat re-derived from the KEPT arrays (results/<rid>.npz read by this check itself): store heating row equals the npz row; total_elec of the
    npz equals equipment + (heating + cooling) / 3 (E6); the run's annual heating in the result json (extractor, float64) equals the sum over its flats."""
    a = bool(np.array_equal(np.asarray(store_row, dtype=np.float32), np.asarray(npz_heating, dtype=np.float32)))
    b = bool(np.allclose(np.asarray(npz_total, dtype=np.float64), np.asarray(npz_equip, dtype=np.float64) + (np.asarray(npz_heating, dtype=np.float64) + np.asarray(npz_cool, dtype=np.float64)) / c.COP, rtol=1e-5, atol=1e-6))
    d = abs(run_heat_sum - json_annual_heat) <= tol_annual * max(1.0, abs(json_annual_heat))
    return a and b and d, (a, b, d)


def openlog_ok(log_lines, forbidden, bad_data_ids):
    """True when no log line names a forbidden (test) run and no data file (kind npz / placement / series) of a not-clean / missing run was opened."""
    ids_kinds = [(ln.split("\t")[0], ln.split("\t")[1]) for ln in log_lines]
    hit_test = [i for k, i in ids_kinds if i in forbidden]
    hit_bad = [i for k, i in ids_kinds if k in ("npz", "placement", "series", "recheck") and i in bad_data_ids]
    return (not hit_test and not hit_bad), hit_test, hit_bad


def build_campaign(plan_csv, camp_root, zmap_path, static_dir, epw_dir, out_dir, tag="campaign", workers=1):
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(out_dir, "work")
    os.makedirs(work, exist_ok=True)
    camp_root = camp_root.rstrip("/\\")
    results_dir, runs_dir = camp_root + "/results", camp_root + "/runs"
    rows = c.read_csv_rows(plan_csv)
    for r in rows:
        if r["district"] not in c.DISTRICTS:
            raise ValueError("district %r is not a Model A district" % r["district"])
    rows = sorted(rows, key=lambda r: r["run_id"])
    zm = c.zone_map(zmap_path)
    flat_tab, bld_tab, bands = c.static_tables(static_dir)
    names_all = c.all_input_names(bands)
    test_ids = [r["run_id"] for r in rows if is_test_row(r)]
    nontest = [r for r in rows if not is_test_row(r)]
    guard = CampaignGuard({"status_stage": [r["run_id"] for r in nontest]}, test_ids)
    # ---- 1. classify (a test row is never opened; a not-clean row is listed by name and never opened for data)
    cl = classify_campaign(rows, results_dir, guard)
    nc = [x[0] for x in cl["not_clean"]]
    refused_by_name = [(i, "TEST") for i in cl["test"]] + [(x[0], "STATUS_%s %s" % (x[1], x[2])) for x in cl["not_clean"]] + \
                      [(i, "MISSING_RESULT") for i in cl["missing"]] + [(i, "SRC_IDF_MD5_MISMATCH") for i in cl["src_md5"]] + [(i, "GATE_FAIL_G-c3_or_purity") for i in cl["gate"]]
    with io.open(os.path.join(out_dir, "refused_%s.tsv" % tag), "w", encoding="utf-8") as fh:
        fh.write("run_id\treason\n")
        for i, why in refused_by_name:
            fh.write("%s\t%s\n" % (i, why))
    stamp("plan rows %d: test %d (refused, never opened), not clean %d, missing %d, src md5 mismatch %d, gate fail %d, CLEAN to store %d" %
          (len(rows), len(cl["test"]), len(cl["not_clean"]), len(cl["missing"]), len(cl["src_md5"]), len(cl["gate"]), len(cl["ok"])))
    for i, why in refused_by_name[:40]:
        print("REFUSED %s %s" % (i, why), flush=True)
    chk("refused_rows_listed_by_name", True, "refused=%d (file refused_%s.tsv) test=%d not_clean=%d missing=%d src_md5=%d gate=%d" %
        (len(refused_by_name), tag, len(cl["test"]), len(cl["not_clean"]), len(cl["missing"]), len(cl["src_md5"]), len(cl["gate"])))
    ok_rows = cl["ok"]
    # ---- 2. what is stored already (ledger) and what changes
    lp = os.path.join(out_dir, "ledger.tsv")
    ledger = {}
    if os.path.exists(lp):
        for ln in io.open(lp, encoding="utf-8").read().splitlines()[1:]:
            rid, sp, md, nf = ln.split("\t")
            ledger[rid] = {"split": sp, "md5": md, "n": int(nf)}
    splits_all = sorted({store_split(r["building_split"], r["pool"]) for r in ok_rows} | {v["split"] for v in ledger.values()})
    old_df = {}
    for s in splits_all:
        pth = os.path.join(work, "flats_raw_%s" % s)
        if os.path.exists(pth + ".parquet") or os.path.exists(pth + ".csv.gz"):
            old_df[s] = read_table(pth)
    keep_ids = set()
    counts = {s_: df["run_id"].value_counts().to_dict() for s_, df in old_df.items()}
    for r in ok_rows:
        rid = r["run_id"]
        e = ledger.get(rid)
        s = store_split(r["building_split"], r["pool"])
        if e and e["md5"] == cl["json_md5"][rid] and e["split"] == s and counts.get(s, {}).get(rid, 0) == e["n"]:
            keep_ids.add(rid)
    to_add = [r for r in ok_rows if r["run_id"] not in keep_ids]
    removed = [rid for rid in ledger if rid not in keep_ids]
    ledger = dict((k, v) for k, v in ledger.items() if k in keep_ids)           # everything else is re-added below or gone
    orphan_rows = {s: sorted(set(df["run_id"]) - keep_ids) for s, df in old_df.items()}
    stamp("ledger %d runs; kept %d; to add %d; to remove %d (changed md5 or no longer clean: counted in remove; stored rows of runs not kept, incl. rows without a ledger line, per split: %s)" %
          (len(ledger), len(keep_ids), len(to_add), len(removed), {s: len(v) for s, v in orphan_rows.items() if v}))
    # ---- 3. read the new runs (only through the guard)
    inst = {}
    for cc in c.COUNTRIES:
        ip = os.path.join(work, "hh_%s_inst.tsv" % cc)
        inst[cc] = {}
        if os.path.exists(ip):
            for ln in io.open(ip, encoding="utf-8").read().splitlines()[1:]:
                i_, hid, mem, pk, mp, ma = ln.split("\t")
                inst[cc][(cc, hid, mp, ma, mem, pk)] = int(i_)
    n_old_inst = {cc: len(inst[cc]) for cc in c.COUNTRIES}
    tasks, zr_of = [], {}
    for r in to_add:
        d, rid = r["district"], r["run_id"]
        zr = zm[(d, r["stem"])]
        zr_of[rid] = zr
        mode = "O" if r["mode"] == "occupancy" else "D"
        for kind, pth in (("npz", "%s/%s.npz" % (results_dir, rid)),) + ((("placement", "%s/%s/placement.csv" % (runs_dir, rid)), ("series", "%s/%s/series.tar.gz" % (runs_dir, rid))) if mode == "O" else ()):
            guard.open_run(rid, kind, pth)
        tasks.append({"run_id": rid, "zones": [z["zone"] for z in zr], "mode": mode, "cc": c.DISTRICTS[d]["cc"], "npz": "%s/%s.npz" % (results_dir, rid),
                      "placement": "%s/%s/placement.csv" % (runs_dir, rid), "series_tar": "%s/%s/series.tar.gz" % (runs_dir, rid), "camp_root": camp_root})
    newbin = {}
    new_n = {s: 0 for s in splits_all}
    new_recs = {s: [] for s in splits_all}
    new_hh_n = {cc: 0 for cc in c.COUNTRIES}
    new_inst_rows = {cc: [] for cc in c.COUNTRIES}
    failed, nan_t, nan_hh = [], 0, 0
    fh_t = {s: open(os.path.join(work, "new_targets_%s.bin" % s), "wb") for s in splits_all}
    fh_p = {cc: open(os.path.join(work, "new_hh_%s_pres.bin" % cc), "wb") for cc in c.COUNTRIES}
    fh_f = {cc: open(os.path.join(work, "new_hh_%s_frac.bin" % cc), "wb") for cc in c.COUNTRIES}
    meta_by_rid = {r["run_id"]: r for r in to_add}
    if workers > 1 and len(tasks) > 1:
        import multiprocessing as mp
        pool = mp.Pool(workers)
        it = pool.imap(_safe_load, tasks, chunksize=1)
    else:
        pool, it = None, (_safe_load(t) for t in tasks)
    for res in it:
        rid = res["run_id"]
        if "error" in res:
            failed.append((rid, res["error"][:200]))
            continue
        r = meta_by_rid[rid]
        d, s = r["district"], store_split(r["building_split"], r["pool"])
        cc = c.DISTRICTS[d]["cc"]
        zr = zr_of[rid]
        n = len(zr)
        arr = res["targets"]
        nan_t += int((~np.isfinite(arr)).sum())
        fh_t[s].write(np.ascontiguousarray(arr, dtype=np.float32).tobytes())
        mode = "O" if r["mode"] == "occupancy" else "D"
        hidx = []
        for j in range(n):
            key = res["inst"][j]
            if key is None:
                hidx.append(-1)
                continue
            if key not in inst[cc]:
                k_ = n_old_inst[cc] + new_hh_n[cc]
                inst[cc][key] = k_
                new_hh_n[cc] += 1
                pres, frac = res["series"][key]
                nan_hh += int((~np.isfinite(pres)).sum() + (~np.isfinite(frac)).sum())
                fh_p[cc].write(pres.tobytes())
                fh_f[cc].write(frac.tobytes())
                new_inst_rows[cc].append((k_, key[1], key[4], key[5], key[2], key[3]))
            hidx.append(inst[cc][key])
        fk = [int(z["floor_k"]) for z in zr]
        bl = bld_tab[(d, r["stem"])]
        for j, z in enumerate(zr):
            fr = flat_tab[(d, z["zone"])]
            rec = {"run_id": rid, "split": s, "district": d, "country": cc, "stem": r["stem"], "mode": mode, "zone": z["zone"], "floor": fk[j],
                   "hid": res["hid"][j] if res["hid"][j] is not None else "", "hh_index": hidx[j]}
            for nm, lo in (("nb_same", [g for g in range(n) if fk[g] == fk[j] and g != j]), ("nb_above", [g for g in range(n) if fk[g] == fk[j] + 1]),
                           ("nb_below", [g for g in range(n) if fk[g] == fk[j] - 1])):
                rec[nm] = ";".join(str(hidx[g]) for g in lo) if mode == "O" else ""
            for k_ in c.COUNTRIES:
                rec["s_ctry_" + k_] = 1.0 if cc == k_ else 0.0
            for k_ in c.CLASSES:
                rec["s_cls_" + k_] = 1.0 if bl["class"] == k_ else 0.0
            for b in bands:
                rec["s_age_" + b.replace(".", "_")] = 1.0 if bl["age_band_prepared"] == b else 0.0
            for src, nm in c.BLD_NUMERIC + c.BLD_FLAGS:
                rec[nm] = float(bl[src])
            for src, nm in c.FLAT_NUMERIC + c.FLAT_FLAGS:
                rec[nm] = float(fr[src])
            new_recs[s].append(rec)
        new_n[s] += n
        ledger[rid] = {"split": s, "md5": cl["json_md5"][rid], "n": n}
    if pool is not None:
        pool.close()
        pool.join()
    for f_ in list(fh_t.values()) + list(fh_p.values()) + list(fh_f.values()):
        f_.close()
    for rid, _e in failed:
        ledger.pop(rid, None)
    chk("all_candidate_runs_loaded", not failed, "to_add=%d failed=%d %s" % (len(to_add), len(failed), failed[:3]))
    # ---- 4. rewrite the splits that changed (old kept rows + new rows), hh arrays append-only
    flats_raw = {}
    for s in splits_all:
        df_old = old_df.get(s)
        if df_old is not None and len(df_old):
            msk = df_old["run_id"].isin(keep_ids).to_numpy()
        else:
            msk = np.zeros(0, dtype=bool)
        n_keep = int(msk.sum())
        tpath = os.path.join(out_dir, "targets_%s.npy" % s)
        if df_old is not None and msk.all() and new_n[s] == 0 and os.path.exists(tpath):
            flats_raw[s] = df_old.reset_index(drop=True)
        elif n_keep + new_n[s] == 0:
            flats_raw[s] = None
            for f_ in (tpath, os.path.join(work, "flats_raw_%s.parquet" % s), os.path.join(work, "flats_raw_%s.csv.gz" % s)):
                if os.path.exists(f_):
                    os.remove(f_)
        else:
            keep_idx = np.flatnonzero(msk) if n_keep else None
            combine_rows(tpath, tpath, keep_idx, os.path.join(work, "new_targets_%s.bin" % s), new_n[s], (H, 3))
            parts = ([df_old[msk]] if n_keep else []) + ([pd.DataFrame(new_recs[s])] if new_n[s] else [])
            flats_raw[s] = pd.concat(parts, ignore_index=True)
            write_table(flats_raw[s], os.path.join(work, "flats_raw_%s" % s))
        nbp = os.path.join(work, "new_targets_%s.bin" % s)
        if os.path.exists(nbp):
            os.remove(nbp)
    HHA = {}
    for cc in c.COUNTRIES:
        pp, fp = os.path.join(work, "hh_%s_pres.npy" % cc), os.path.join(work, "hh_%s_frac.npy" % cc)
        if new_hh_n[cc]:
            for nm_, path_ in (("pres", pp), ("frac", fp)):
                keep = np.arange(n_old_inst[cc]) if n_old_inst[cc] else None
                combine_rows(path_, path_, keep, os.path.join(work, "new_hh_%s_%s.bin" % (cc, nm_)), new_hh_n[cc], (H,))
            allrows = []
            ip = os.path.join(work, "hh_%s_inst.tsv" % cc)
            if os.path.exists(ip):
                allrows = io.open(ip, encoding="utf-8").read().splitlines()[1:]
            with io.open(ip, "w", encoding="utf-8") as fh:
                fh.write("idx\thid\tmembers\tdesign_w\tmd5_presence\tmd5_appl\n")
                for ln in allrows:
                    fh.write(ln + "\n")
                for x in new_inst_rows[cc]:
                    fh.write("\t".join(str(v) for v in x) + "\n")
        for nm_ in ("pres", "frac"):
            b_ = os.path.join(work, "new_hh_%s_%s.bin" % (cc, nm_))
            if os.path.exists(b_):
                os.remove(b_)
        ip = os.path.join(work, "hh_%s_inst.tsv" % cc)
        if os.path.exists(ip):
            lines = io.open(ip, encoding="utf-8").read().splitlines()[1:]
            hl = np.array([ln.split("\t")[1] for ln in lines])
            mem = np.array([float(ln.split("\t")[2]) for ln in lines], dtype=np.float32)
            dw = np.array([float(ln.split("\t")[3]) for ln in lines], dtype=np.float32)
            pres_m, frac_m = np.load(pp, mmap_mode="r"), np.load(fp, mmap_mode="r")
            n_i = len(hl)

            def gen(kind, pres_m=pres_m, frac_m=frac_m, mem=mem, dw=dw, n_i=n_i):
                for a0 in range(0, n_i, 2048):
                    p_, f_ = np.asarray(pres_m[a0:a0 + 2048]), np.asarray(frac_m[a0:a0 + 2048])
                    yield {"presence": p_, "appl_frac": f_, "people": (mem[a0:a0 + 2048, None] * p_).astype(np.float32),
                           "appl_w": (dw[a0:a0 + 2048, None] * f_).astype(np.float32)}[kind]
            npzp = os.path.join(out_dir, "hh_%s.npz" % cc)
            if new_hh_n[cc] or not os.path.exists(npzp):
                write_npz_stream(npzp, [("hid", hl)] + [(k, ((n_i, H), np.float32, gen(k))) for k in HHCH] + [("members", mem), ("design_w", dw)])
            HHA[cc] = (frac_m, dw, pres_m, mem)
            print("INFO hh_%s.npz n_hh=%d household instances (one per household x run draw; identical series files share one; new this build %d)" % (cc, n_i, new_hh_n[cc]), flush=True)
    # ---- 5. weather + calendar per district present
    wmat, cal, nan_w = {}, {}, 0
    for d in sorted({r["district"] for r in ok_rows} | set().union(*[set(fr_["district"]) for fr_ in flats_raw.values() if fr_ is not None and len(fr_)])):
        epwp = os.path.join(epw_dir, CAMPAIGN_EPW[d])
        wmat[d] = read_epw(epwp)
        np.save(os.path.join(out_dir, "weather_%s.npy" % d), wmat[d])
        cal[d] = c.calendar_array(c.DISTRICTS[d]["year"])
        np.save(os.path.join(out_dir, "calendar_%s.npy" % d), cal[d])
        nan_w += int((~np.isfinite(wmat[d])).sum())
        print("INFO weather_%s.npy from %s md5 %s ; calendar year %d" % (d, CAMPAIGN_EPW[d], md5_file(epwp), c.DISTRICTS[d]["year"]), flush=True)
    # ---- 6. final flats tables (z-score on development), checks
    live = [s for s in splits_all if flats_raw.get(s) is not None]
    flats = {s: flats_raw[s].copy() for s in live}
    zcols = c.zscored_names()
    static_norm = {}
    if "development" in flats and len(flats["development"]):
        dev = flats["development"]
        for nm in zcols:
            v = dev[nm].to_numpy(dtype=np.float64)
            sd = float(v.std())
            static_norm[nm] = {"mean": float(v.mean()), "sd": sd if sd > 0 else 1.0, "lo": float(v.min()), "hi": float(v.max())}
        for s in live:
            for nm in zcols:
                st = static_norm[nm]
                flats[s][nm] = ((flats[s][nm].clip(st["lo"], st["hi"]) - st["mean"]) / st["sd"]).astype(np.float64)
    else:
        chk("static_norm_from_development", None, "no development flats in the store yet: static columns not z-scored (NOT_EVALUABLE)")
    for s in live:
        pth = write_table(flats[s], os.path.join(out_dir, "flats_%s" % s))
        stamp("%s rows %d runs %d" % (os.path.basename(pth), len(flats[s]), flats[s]["run_id"].nunique() if len(flats[s]) else 0))
        sh_ = tuple(np.load(os.path.join(out_dir, "targets_%s.npy" % s), mmap_mode="r").shape)
        chk("targets_rows_equal_flats_rows_%s" % s, targets_rows_match(os.path.join(out_dir, "targets_%s.npy" % s), len(flats[s])), "targets shape %s, flats rows %d" % (sh_, len(flats[s])))
    some = next((flats[s] for s in live if len(flats[s])), None)
    if some is not None:
        cols = list(some.columns)
        present = c.HH_CHANNELS + c.NB_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS + [x for x in cols if x.startswith("s_")]
        chk("input_list_equals_spec", sorted(present) == sorted(names_all), "n_inputs=%d n_spec=%d" % (len(present), len(names_all)))
        ok_, bad = c.check_features(present)
        chk("check_features_full_input_list", ok_, "n=%d forbidden_hits=%s" % (len(present), bad))
        nan_static = sum(int(flats[s][[x for x in cols if x.startswith("s_")]].isna().sum().sum()) for s in live)
        json.dump({"static": [x for x in cols if x.startswith("s_")], "zscored_clipped_on_development": zcols, "age_bands": bands,
                   "id_columns_never_inputs": ["run_id", "split", "district", "country", "stem", "mode", "zone", "floor", "hid", "hh_index", "nb_same", "nb_above", "nb_below"],
                   "feature_forbidden": c.FEATURE_FORBIDDEN}, open(os.path.join(out_dir, "static_cols.json"), "w"), indent=1)
    else:
        nan_static = 0
    # ---- 7. pairs
    for s in ("development", "validation"):
        if s not in flats:
            continue
        df = flats[s]
        sub = df[df["mode"] == "O"]
        grp = sub.groupby(["district", "stem", "zone"]).indices if len(sub) else {}
        hid_code = pd.factorize(sub["country"] + "|" + sub["hid"])[0]
        ridx = sub.index.to_numpy()
        A, B, alt = [], [], 0
        for key, idx in grp.items():
            m = len(idx)
            if m < 2:
                continue
            ia, ib = np.triu_indices(m, 1)
            keep = hid_code[idx[ia]] != hid_code[idx[ib]]
            A.append(ridx[idx[ia][keep]]); B.append(ridx[idx[ib][keep]])
            cnt = np.bincount(hid_code[idx])
            alt += m * (m - 1) // 2 - int((cnt * (cnt - 1) // 2).sum())
        ra = np.concatenate(A) if A else np.zeros(0, dtype=np.int64)
        rb = np.concatenate(B) if B else np.zeros(0, dtype=np.int64)
        write_table(pd.DataFrame({"row_a": ra.astype(np.int64), "row_b": rb.astype(np.int64)}), os.path.join(out_dir, "pairs_%s" % s))
        chk("pairs_%s_two_methods_agree" % s, len(ra) == alt, "pairs=%d second_method=%d" % (len(ra), alt))
    # ---- 8. norm.json (development flat-hours)
    norm = {"source": None, "targets": {}, "channels": {}, "static": static_norm}
    if "development" in flats and len(flats["development"]):
        dev = flats["development"]
        nf = len(dev)
        N_ = float(nf) * H
        norm["source"] = "development flat-hours (%d flats x %d h)" % (nf, H)
        T = np.load(os.path.join(out_dir, "targets_development.npy"), mmap_mode="r")
        s1, s2 = np.zeros(3), np.zeros(3)
        for a0 in range(0, nf, 256):
            x = np.asarray(T[a0:a0 + 256]).astype(np.float64)
            s1 += x.sum((0, 1)); s2 += (x ** 2).sum((0, 1))
        for i, nm in enumerate(("heating", "cooling", "equipment")):
            mu = s1[i] / N_
            norm["targets"][nm] = {"mean": mu, "sd": math.sqrt(max(s2[i] / N_ - mu * mu, 0.0))}
        acc = {nm: [0.0, 0.0] for nm in c.HH_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS}
        for cc in c.COUNTRIES:
            sub = dev[(dev["country"] == cc) & (dev["hh_index"] >= 0)]
            if len(sub) and cc in HHA:
                frac_m, dw_, pres_m, mem_ = HHA[cc]
                cnt = np.bincount(sub["hh_index"].to_numpy(), minlength=len(dw_))
                for a0 in range(0, len(dw_), 2048):
                    p_ = np.asarray(pres_m[a0:a0 + 2048]).astype(np.float64)
                    f_ = np.asarray(frac_m[a0:a0 + 2048]).astype(np.float64)
                    cb = cnt[a0:a0 + 2048]
                    arrs = {"presence": p_, "appl_frac": f_, "people": mem_[a0:a0 + 2048, None].astype(np.float64) * p_, "appl_w": dw_[a0:a0 + 2048, None].astype(np.float64) * f_}
                    for nm, a64 in arrs.items():
                        acc[nm][0] += float((cb * a64.sum(1)).sum()); acc[nm][1] += float((cb * (a64 ** 2).sum(1)).sum())
        for d in wmat:
            n_d = int((dev["district"] == d).sum())
            w = wmat[d].astype(np.float64)
            for k_, nm in enumerate(c.WEATHER_CHANNELS):
                acc[nm][0] += n_d * float(w[:, k_].sum()); acc[nm][1] += n_d * float((w[:, k_] ** 2).sum())
            for k_, nm in enumerate(c.CALENDAR_CHANNELS):
                col = cal[d][:, k_].astype(np.float64)
                acc[nm][0] += n_d * float(col.sum()); acc[nm][1] += n_d * float((col ** 2).sum())
        for nm, (a1, a2) in acc.items():
            mu = a1 / N_
            norm["channels"][nm] = {"mean": mu, "sd": math.sqrt(max(a2 / N_ - mu * mu, 0.0))}
    norm["note"] = ("neighbour channels nb_*_people and nb_*_appl_w use the people and appl_w statistics; flags are not standardised; hh channels "
                    "are weighted over development flats that have a household; static block: z = (clip(x, lo, hi) - mean) / sd per development flat, "
                    "already applied in flats_<split>; one-hots and flags are raw")
    json.dump(norm, open(os.path.join(out_dir, "norm.json"), "w"), indent=1)
    # ---- 9. G-c3 in the store, one heating flat re-derived from the kept arrays (own read of the npz), seen failing on planted changes
    HHg = {cc: (HHA[cc][0], HHA[cc][1]) for cc in HHA}
    n_g, worst_g, ok_g = 0, None, None
    for s in live:
        if not len(flats[s]) or not (flats[s]["hh_index"] >= 0).any():
            continue
        T = np.load(os.path.join(out_dir, "targets_%s.npy" % s), mmap_mode="r")
        o_, w_, n_ = gc3_rows(T, flats[s], HHg)
        ok_g = (ok_g is not False) and o_
        worst_g = w_ if worst_g is None else max(worst_g, w_)
        n_g += n_
    chk("gc3_in_store_equipment_equals_design_x_series_0p5pct", ok_g, "flats=%s max_rel_dev=%s (tolerance 5e-3)" % (n_g, "n/a" if worst_g is None else "%.3e" % worst_g))
    first = next((s for s in live if len(flats[s]) and (flats[s]["hh_index"] >= 0).any()), None)
    if first is not None:
        T = np.load(os.path.join(out_dir, "targets_%s.npy" % first), mmap_mode="r")
        fdf = flats[first]
        pick = fdf[fdf["hh_index"] >= 0].iloc[len(fdf[fdf["hh_index"] >= 0]) // 2]
        rid_p = pick["run_id"]
        guard.open_run(rid_p, "recheck", "%s/%s.npz" % (results_dir, rid_p))
        zz = np.load("%s/%s.npz" % (results_dir, rid_p))
        zl = [str(x) for x in zz["zones"]]
        jj = zl.index(pick["zone"])
        in_run = fdf.index[fdf["run_id"] == rid_p].to_numpy()
        jd = json.load(io.open("%s/%s.json" % (results_dir, rid_p), encoding="utf-8"))
        ri = int(fdf.index[(fdf["run_id"] == rid_p) & (fdf["zone"] == pick["zone"])][0])
        run_heat = float(np.asarray(T[in_run, :, 0], dtype=np.float64).sum())
        ok_r, parts = rederive_heating(T[ri, :, 0], zz["heating"][jj], zz["equipment"][jj], zz["cooling"][jj], zz["total_elec"][jj], jd["annual_kwh"]["heating_kwh"], run_heat)
        chk("rederive_heating_one_flat_from_kept_arrays", ok_r, "run=%s zone=%s store==npz row %s, total_elec identity %s, run annual heating store %.3f vs result json %.3f %s" %
            (rid_p, pick["zone"], parts[0], parts[1], run_heat, jd["annual_kwh"]["heating_kwh"], parts[2]))
        bad_row = np.asarray(T[ri, :, 0], dtype=np.float64) * 1.01
        ok_p, parts_p = rederive_heating(bad_row, zz["heating"][jj], zz["equipment"][jj], zz["cooling"][jj], zz["total_elec"][jj], jd["annual_kwh"]["heating_kwh"], run_heat * 1.01)
        chk("rederive_heating_seen_failing_planted_plus_1pct", not ok_p, "planted +1 %% on the stored row: parts %s (must contain False)" % (parts_p,))
        T_pl = np.array(T[in_run], dtype=np.float32)
        T_pl[:, :, 2] *= 1.02
        o_p, w_p, _n = gc3_rows(T_pl, fdf.loc[in_run].reset_index(drop=True), HHg)
        chk("gc3_in_store_seen_failing_planted_equipment_x1.02", not o_p, "planted x1.02 on equipment rows: worst rel dev %.3e (must exceed 5e-3)" % w_p)
    else:
        chk("rederive_heating_one_flat_from_kept_arrays", None, "no stored flat with a household")
    # ---- 10. open log, NaN, ledger, README, size
    with io.open(lp, "w", encoding="utf-8") as fh:
        fh.write("run_id\tsplit\tresult_md5\tn_flats\n")
        for rid in sorted(ledger):
            fh.write("%s\t%s\t%s\t%d\n" % (rid, ledger[rid]["split"], ledger[rid]["md5"], ledger[rid]["n"]))
    chk("no_nan", (nan_hh + nan_w + nan_static + nan_t) == 0, "hh=%d weather=%d static=%d targets=%d" % (nan_hh, nan_w, nan_static, nan_t))
    olp = os.path.join(out_dir, "openlog_%s.tsv" % tag)
    if os.path.exists(olp):
        os.remove(olp)
    guard.flush(olp)
    lines = io.open(olp, encoding="utf-8").read().splitlines()[1:]
    bad_data = set(nc) | set(cl["missing"]) | set(cl["src_md5"]) | set(cl["gate"])
    ok_l, hit_t, hit_b = openlog_ok(lines, set(test_ids), bad_data)
    chk("openlog_no_test_run_and_no_data_of_a_refused_run", ok_l, "log lines=%d test ids in log=%d (%s) data files of refused runs opened=%d (%s); guard refusals=%d" %
        (len(lines), len(hit_t), hit_t[:3], len(hit_b), hit_b[:3], len(guard.refused)))
    pl_lines = lines + (["status\t%s\tplanted" % test_ids[0]] if test_ids else [])
    if test_ids:
        ok_pl, _a, _b = openlog_ok(pl_lines, set(test_ids), bad_data)
        chk("openlog_check_seen_failing_planted_test_id_in_log", not ok_pl, "planted log line naming test run %s: the check says %s (must be False)" % (test_ids[0], ok_pl))
    readme = [
        "# 5J Model A store, campaign mode (written %s by a9_store.py campaign, Step 9n)" % time.strftime("%Y-%m-%d %H:%M"),
        "Same layout as the 9g store (hh_<cc>.npz, weather_<district>.npy, calendar_<district>.npy, flats_<split>, targets_<split>.npy, pairs_<split>, norm.json, static_cols.json, openlog_<tag>.tsv).",
        "Built only from what the campaign keeps: results/<rid>.json (status CLEAN), results/<rid>.npz (hourly heating, cooling, equipment per flat, float32), runs/<rid>/placement.csv + series.tar.gz, b0 files, EPW, zone map, static tables.",
        "Split names: development = dev building x dev households; validation = val building x val households; xdev_hval / xval_hdev = the mixed cases (kept apart); b0_<bs>, default_<bs>. Test runs (pool test or test building) are never opened.",
        "hh_<cc>.npz index = household INSTANCE (one per household x run draw; identical series files share one instance). Instances are append-only; ones whose runs were removed stay as unused rows.",
        "ledger.tsv = stored runs with the md5 of their result json; work/ = raw (un-z-scored) flats tables and hh arrays used for incremental builds; refused_<tag>.tsv = every refused run with its reason.",
        "Row order inside a split = order of insertion (kept rows first, then new runs sorted by run_id); the key of a row is (run_id, zone).",
        "targets_<split>.npy : float32 n_rows x 8760 x 3 (heating, cooling, equipment kWh per hour per flat); total_elec = equipment + (heating + cooling) / 3.0",
    ]
    io.open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8").write("\n".join(readme) + "\n")
    tot = sum(len(flats[s]) for s in live)
    top = sum(os.path.getsize(os.path.join(out_dir, f)) for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f)))
    wk = sum(os.path.getsize(os.path.join(work, f)) for f in os.listdir(work) if os.path.isfile(os.path.join(work, f)))
    tb = sum(os.path.getsize(os.path.join(out_dir, "targets_%s.npy" % s)) for s in live)
    hb = sum(os.path.getsize(os.path.join(out_dir, "hh_%s.npz" % cc)) for cc in c.COUNTRIES if os.path.exists(os.path.join(out_dir, "hh_%s.npz" % cc)))
    print("SIZE flats=%d store_total_bytes=%d MB_per_flat_year_total=%.4f targets_only_MB_per_flat_year=%.4f hh_files_MB_per_flat_year=%.4f work_folder_MB=%.2f (R9 measured 0.229 MB per flat-year)" %
          (tot, top, top / max(tot, 1) / 1e6, tb / max(tot, 1) / 1e6, hb / max(tot, 1) / 1e6, wk / 1e6), flush=True)
    added = len(to_add) - len(failed)
    nfail = sum(1 for _, ok in RES if ok is False)
    print("CAMPAIGN_INCREMENT added=%d removed=%d kept=%d stored_total=%d failed=%d" % (added, len(removed), len(keep_ids), len(ledger), len(failed)), flush=True)
    print("STORE_DONE checks=%d fail=%d seconds=%.0f" % (len(RES), nfail, time.time() - t0), flush=True)
    return {"added": added, "removed": len(removed), "kept": len(keep_ids), "stored": sorted(ledger), "refused": refused_by_name, "classify": cl, "failed": failed, "nfail": nfail,
            "test_ids": test_ids, "n_flats": {s: len(flats[s]) for s in live}, "guard": guard, "openlog": olp}


def _safe_load(task):
    try:
        return load_campaign_run(task)
    except Exception as e:                      # a failed run is a result, written down
        return {"run_id": task["run_id"], "error": repr(e)}


def campaign_main(argv):
    plan, camp, zmap, static_dir, epw_dir, out_dir = argv[0:6]
    tag = argv[6] if len(argv) > 6 else "campaign"
    workers = int(argv[7]) if len(argv) > 7 else 1
    info = build_campaign(plan, camp, zmap, static_dir, epw_dir, out_dir, tag, workers)
    return 1 if info["nfail"] else 0


def campaign_test(base, workers=4):
    """Step 9n test on the local smoke copy: <base>/smoke_ES-MAD-BERRUGUETE.csv, results/, runs/, b0/, inputs/zone_map_win3.csv, inputs/static, epw/."""
    base = base.rstrip("/\\")
    plan, zmap, static_dir, epw_dir, out = base + "/smoke_ES-MAD-BERRUGUETE.csv", base + "/inputs/zone_map_win3.csv", base + "/inputs/static", base + "/epw", base + "/store"
    import shutil
    shutil.rmtree(out, ignore_errors=True)
    rows = c.read_csv_rows(plan)
    # ---- independent expectation (own code: plan columns + the raw result json text)
    exp_test = sorted(r["run_id"] for r in rows if r["pool"] == "test" or r["building_split"] == "test")
    exp_clean, exp_notclean = [], []
    for r in rows:
        if r["run_id"] in exp_test:
            continue
        txt = io.open("%s/results/%s.json" % (base, r["run_id"]), encoding="utf-8").read()
        (exp_clean if '"status": "CLEAN"' in txt else exp_notclean).append(r["run_id"])
    exp_clean, exp_notclean = sorted(exp_clean), sorted(exp_notclean)
    print("EXPECTED from the plan and the result jsons: smoke rows %d, test runs %d, non-test clean %d, non-test not clean %d" % (len(rows), len(exp_test), len(exp_clean), len(exp_notclean)), flush=True)
    chk("expected_counts_nonzero", len(exp_clean) > 0 and len(exp_notclean) > 0 and len(exp_test) > 0, "clean=%d not_clean=%d test=%d" % (len(exp_clean), len(exp_notclean), len(exp_test)))
    # ---- refusal branches seen firing on planted result jsons (a scratch results folder with four tweaked copies of real results)
    pl_dir = base + "/planted_results"
    shutil.rmtree(pl_dir, ignore_errors=True)
    os.makedirs(pl_dir)
    clean_rows = [r for r in rows if r["run_id"] in exp_clean]
    nc_rows = [r for r in rows if r["run_id"] in exp_notclean]
    pr_ = {"src": clean_rows[0], "gate": clean_rows[1], "notclean": nc_rows[0], "missing": clean_rows[2], "good": clean_rows[3]}
    for k_, r_ in pr_.items():
        if k_ == "missing":
            continue
        j_ = json.load(io.open("%s/results/%s.json" % (base, r_["run_id"]), encoding="utf-8"))
        if k_ == "src":
            j_["src_idf_md5"] = "0" * 32
        if k_ == "gate":
            j_["gc3_fail"] = True
        json.dump(j_, io.open("%s/%s.json" % (pl_dir, r_["run_id"]), "w", encoding="utf-8"))
    gp = CampaignGuard({"s": [r_["run_id"] for r_ in pr_.values()]}, [])
    cp = classify_campaign(list(pr_.values()), pl_dir, gp)
    chk("classifier_seen_refusing_planted_src_md5_gate_not_clean_missing", cp["src_md5"] == [pr_["src"]["run_id"]] and cp["gate"] == [pr_["gate"]["run_id"]] and
        [x[0] for x in cp["not_clean"]] == [pr_["notclean"]["run_id"]] and cp["missing"] == [pr_["missing"]["run_id"]] and [r_["run_id"] for r_ in cp["ok"]] == [pr_["good"]["run_id"]],
        "planted: src md5 changed -> refused %d, G-c3 flag -> refused %d, NOT_CLEAN -> refused %d, missing -> %d, untouched copy -> accepted %d" %
        (len(cp["src_md5"]), len(cp["gate"]), len(cp["not_clean"]), len(cp["missing"]), len(cp["ok"])))
    shutil.rmtree(pl_dir, ignore_errors=True)
    # ---- build 1 (fresh)
    info = build_campaign(plan, base, zmap, static_dir, epw_dir, out, "build1", workers)
    chk("stored_runs_equal_clean_non_test_smoke_runs", info["stored"] == exp_clean and info["added"] == len(exp_clean), "stored %d, expected %d, added %d" % (len(info["stored"]), len(exp_clean), info["added"]))
    got_nc = sorted(i for i, why in info["refused"] if why.startswith("STATUS_"))
    chk("not_clean_runs_refused_by_name", got_nc == exp_notclean, "refused not-clean %d, expected %d; first names %s" % (len(got_nc), len(exp_notclean), got_nc[:3]))
    got_t = sorted(i for i, why in info["refused"] if why == "TEST")
    chk("every_test_pool_and_test_building_run_refused", got_t == exp_test and all(any(i == t for t in got_t) for i in exp_test), "refused test runs %d expected %d (test building 4a1eb42e7c488fc0 runs: %d)" %
        (len(got_t), len(exp_test), sum(1 for i in got_t if "4a1eb42e7c488fc0" in i)))
    lines = io.open(info["openlog"], encoding="utf-8").read().splitlines()[1:]
    in_log = {ln.split("\t")[1] for ln in lines}
    chk("test_runs_absent_from_open_log", not (in_log & set(exp_test)), "open log distinct runs %d, test runs in log %d" % (len(in_log), len(in_log & set(exp_test))))
    # planted call that asks for a test id
    g = CampaignGuard({"x": exp_clean + exp_test}, exp_test)          # even a list that wrongly contains the test ids cannot open them
    raised, n0 = False, len(g.log)
    try:
        g.open_run(exp_test[0], "npz", "%s/results/%s.npz" % (base, exp_test[0]))
    except PermissionError:
        raised = True
    gl = base + "/guard_log_9n.tsv"
    if os.path.exists(gl):
        os.remove(gl)
    g.flush(gl)
    chk("planted_call_for_a_test_id_refused_and_not_logged", raised and len(g.log) == 0 and n0 == 0 and exp_test[0] not in io.open(gl).read() and g.refused == [exp_test[0]],
        "raised=%s log_lines_for_it=%d" % (raised, int(exp_test[0] in io.open(gl).read())))
    # the plain RunGuard (9g) with a wrongly allowed test id would open it: shows why the forbidden set exists (seen failing of the old door)
    g0 = c.RunGuard({"x": exp_test})
    try:
        g0.open_run(exp_test[0], "npz", "p")
        opened_old = True
    except PermissionError:
        opened_old = False
    chk("old_guard_seen_opening_a_wrongly_allowed_test_id_new_guard_not", opened_old and raised, "9g RunGuard with the test id in its list opened it: %s; CampaignGuard refused it: %s" % (opened_old, raised))
    # ---- store content: row counts per split from the ledger
    S = Store(out)
    nfl = {s: len(S.flats(s)) for s in info["n_flats"]}
    print("INFO store splits (flats): %s" % nfl, flush=True)
    st_runs = set()
    for s in nfl:
        st_runs |= set(S.flats(s)["run_id"])
    chk("store_flats_runs_equal_ledger_runs", sorted(st_runs) == exp_clean, "runs in flats tables %d, expected %d" % (len(st_runs), len(exp_clean)))
    tpl = out + "/targets_development.npy"
    pl = out + "/planted_extra_row_targets.npy"
    src_ = np.load(tpl, mmap_mode="r")
    dst_ = np.lib.format.open_memmap(pl, mode="w+", dtype=np.float32, shape=(src_.shape[0] + 1, H, 3))
    dst_[:src_.shape[0]] = src_[:]
    dst_.flush()
    del dst_, src_
    chk("targets_rows_check_seen_failing_planted_extra_row", (not targets_rows_match(pl, nfl["development"])) and targets_rows_match(tpl, nfl["development"]), "planted file has one extra row: False; real file: True")
    _gc()
    os.remove(pl)
    # ---- incremental
    md0 = {f: md5_file(out + "/" + f) for f in sorted(os.listdir(out)) if os.path.isfile(out + "/" + f) and f.startswith(("targets_", "flats_"))}
    info2 = build_campaign(plan, base, zmap, static_dir, epw_dir, out, "build2", workers)
    md1 = {f: md5_file(out + "/" + f) for f in sorted(os.listdir(out)) if os.path.isfile(out + "/" + f) and f.startswith(("targets_", "flats_"))}
    chk("incremental_second_build_adds_0_runs", info2["added"] == 0 and info2["removed"] == 0 and info2["kept"] == len(exp_clean), "added=%d removed=%d kept=%d" % (info2["added"], info2["removed"], info2["kept"]))
    chk("incremental_second_build_leaves_targets_and_flats_files_byte_equal", md0 == md1, "files compared %d, differing %s" % (len(md0), [f for f in md0 if md0.get(f) != md1.get(f)][:3]))
    # (a) delete one stored run: its ledger line removed (rows still in the tables) -> exactly 1 added, rows not duplicated
    victim = next(r for r in exp_clean if "_dev_" in r)
    led = io.open(out + "/ledger.tsv", encoding="utf-8").read().splitlines()
    io.open(out + "/ledger.tsv", "w", encoding="utf-8").write("\n".join(l for l in led if not l.startswith(victim + "\t")) + "\n")
    n_rows_before = sum(nfl.values())
    info3 = build_campaign(plan, base, zmap, static_dir, epw_dir, out, "build3", workers)
    S3 = Store(out)
    n_rows_after = sum(len(S3.flats(s)) for s in info3["n_flats"])
    chk("incremental_after_deleting_one_stored_run_adds_exactly_1", info3["added"] == 1 and n_rows_after == n_rows_before and (S3.flats("development")["run_id"] == victim).sum() == len(zone_rows_of(base, victim)),
        "deleted %s; added=%d; rows %d -> %d; rows of that run in development %d" % (victim, info3["added"], n_rows_before, n_rows_after, (S3.flats("development")["run_id"] == victim).sum()))
    # (b) a changed result md5 re-adds that run (the skip rule is on the md5): ledger md5 altered
    led = io.open(out + "/ledger.tsv", encoding="utf-8").read().splitlines()
    led2 = [(l.split("\t")[0] + "\t" + l.split("\t")[1] + "\t" + "0" * 32 + "\t" + l.split("\t")[3]) if l.startswith(victim + "\t") else l for l in led]
    io.open(out + "/ledger.tsv", "w", encoding="utf-8").write("\n".join(led2) + "\n")
    info4 = build_campaign(plan, base, zmap, static_dir, epw_dir, out, "build4", workers)
    chk("incremental_changed_result_md5_readds_exactly_that_run", info4["added"] == 1 and info4["removed"] == 1, "ledger md5 of %s altered: added=%d removed=%d" % (victim, info4["added"], info4["removed"]))
    # (c) the same-md5 skip seen failing is (b); a store whose rows are intact after all three rebuilds still checks out
    info5 = build_campaign(plan, base, zmap, static_dir, epw_dir, out, "build5", workers)
    chk("incremental_final_build_adds_0", info5["added"] == 0 and info5["stored"] == exp_clean, "added=%d stored=%d" % (info5["added"], len(info5["stored"])))
    return summary()


def zone_rows_of(base, rid):
    d, stem = rid.split("_")[0], rid.split("_")[1]
    return c.zone_map(base + "/inputs/zone_map_win3.csv")[(d, stem)]


def summary():
    npass = sum(1 for _, o in RES if o is True)
    nfail = sum(1 for _, o in RES if o is False)
    nne = sum(1 for _, o in RES if o is None)
    print("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d  (exit 0 = no FAIL and something evaluated, 1 = a FAIL, 2 = crashed or nothing evaluable)" % (npass, nfail, nne), flush=True)
    for nm, o in RES:
        if o is not True:
            print("SUMMARY_NOT_PASS %s %s" % (nm, {False: "FAIL", None: "NOT_EVALUABLE"}[o]), flush=True)
    return 1 if nfail else (0 if npass else 2)


def build_main(argv):
    man, allowed_json, zmap, static_dir, out_dir = argv[0:5]
    tag = argv[5] if len(argv) > 5 else "store"
    rows = c.read_csv_rows(man)
    allowed = json.load(open(allowed_json))
    info = build_store(rows, allowed, zmap, static_dir, out_dir, tag)
    return 1 if info["nfail"] else 0


if __name__ == "__main__":
    try:
        if sys.argv[1] == "build":
            code = build_main(sys.argv[2:])
        elif sys.argv[1] == "test":
            code = test_main(*sys.argv[2:8])
        elif sys.argv[1] == "campaign":
            code = campaign_main(sys.argv[2:])
        elif sys.argv[1] == "campaign-test":
            code = campaign_test(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
        elif sys.argv[1] == "heatrule":
            heating_rule_selftest()
            code = summary()
        else:
            raise SystemExit("usage: a9_store.py build|test ...")
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        chk("crashed", None, "the section that raised is NOT_EVALUABLE")
        summary()
        code = 2
    sys.exit(code)
