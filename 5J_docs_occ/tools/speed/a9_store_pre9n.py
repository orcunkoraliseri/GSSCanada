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
    """ok True = PASS, False = FAIL, None = NOT_EVALUABLE"""
    RES.append((name, ok))
    print("CHECK %s %s %s" % (name, {True: "PASS", False: "FAIL", None: "NOT_EVALUABLE"}[ok], text), flush=True)


def stamp(s):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), s), flush=True)


def write_table(df, path_noext):
    try:
        df.to_parquet(path_noext + ".parquet", index=False)
        return path_noext + ".parquet"
    except Exception:
        df.to_csv(path_noext + ".csv.gz", index=False)
        return path_noext + ".csv.gz"


def read_table(path_noext):
    if os.path.exists(path_noext + ".parquet"):
        return pd.read_parquet(path_noext + ".parquet")
    return pd.read_csv(path_noext + ".csv.gz")


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
        cand = [k for k, h in enumerate(head0) if h.startswith(zone.upper() + " IDEAL LOADS AIR SYSTEM") and "Total Heating Energy" in h and h.endswith("(Hourly)")]
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
