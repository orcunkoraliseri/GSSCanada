# -*- coding: utf-8 -*-
"""5J Step 9l: Model A campaign runner (Speed only, one array task = one run = 1 CPU). ES-MAD-BERRUGUETE / IT-BOL-GALVANI2 only.

Sub-commands (Step 9m: skip key = md5 of the LOADED code chain; env A9_CAMP overrides the campaign folder; `codekeytest` = staged-copy test)
  run <manifest.csv> <N>          one run = row N (1-based, data rows) of the manifest. Skip rule R1(d): skipped only if results/<run_id>.json
                                  exists, is complete, status CLEAN or NOT_CLEAN, and its stored src_idf_md5, writer_md5, hh_md5 and
                                  placement_md5 equal the CURRENT ones (otherwise re-run).
  prep <manifest.csv>             once per campaign: B0 average households (DEV households only, per country), light-vs-full placement
                                  equality, skip-rule self test on a synthetic result. Writes campaign/b0/<cc>/.
  check <manifest.csv> [--skiptest]   the check job (a9_campaign_check): rows done / missing / not clean (by name) / purity violations /
                                  G-c3 failures / src md5 mismatches, CPU seconds per district, bytes kept. EXIT CODE: 0 = every section ran
                                  (the verdicts are the text); 4 = written, but at least one section crashed (that section is NOT_EVALUABLE,
                                  never PASS); any other nonzero = the check itself crashed = EVERYTHING is NOT_EVALUABLE.
                                  --skiptest: also tests the skip rule on a COPY of a real result (one md5 changed at a time must RERUN).

Per run (task `run`): households (own split, no-repeat rule recomputed from the plan) -> series + placement + draws on disk -> writer
(`5thJ_modelA_idf.py write`, MODELA_VINTAGE=win_2026-10-03, no --fast, OpenUBEM settings) -> schedcheck -> EnergyPlus 23.1 in the run's OWN
folder -> status read from the err file (G-c5: Severe == 0 and no invalid / not found) -> extraction (a9_extract.extract_run) BEFORE anything
is deleted -> purity read back from the written draw file -> G-c3 per flat (design x series) -> delete the big EnergyPlus files, keep err,
eplustbl.csv, IDF (gz), series (tar.gz), placement, draws (gz), summary -> result json written LAST.
Status: CLEAN | NOT_CLEAN (EnergyPlus ran, not clean: kept and reported by name) | EXTRACT_FAILED | TASK_ERROR.
UK licence: nothing UK is named, opened or passed; the households builder's corpus guard and assert_not_uk stay on.
"""
import csv, gzip, hashlib, importlib.util, io, json, math, os, shutil, subprocess, sys, tarfile, time, traceback

sys.dont_write_bytecode = True
# Step 9o COPY (staged in campaign_win5, never the live campaign): data root, base vintage and zone map point at the 10-05 delivery.
LIVE_CAMP = "/speed-scratch/o_iseri/5J/modelA/campaign_win5"
CAMP = os.environ.get("A9_CAMP", LIVE_CAMP)      # Step 9m: env override, so a staged copy can be tested (default = live)
CODE = CAMP + "/root/5J_docs_occ/tools"     # writer imports 4J_docs_occ/tools relative to its own root: CAMP/root/4J_docs_occ/tools
RES = os.environ.get("A9_RESULTS", CAMP + "/results")
RUNS = CAMP + "/runs"
PY = "/speed-scratch/o_iseri/envs/step4/bin/python"
EP = "/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus"
FLEET = "/speed-scratch/o_iseri/fleets"
VINT = "win_2026-10-05"
EPWDIR = "/speed-scratch/o_iseri/5J/step9c/epw"
EPW = {"ES-MAD-BERRUGUETE": EPWDIR + "/es_madrid_2009_2010_y2010.epw", "IT-BOL-GALVANI2": EPWDIR + "/it_bologna_2013_2014_y2014.epw"}
CC = {"ES-MAD-BERRUGUETE": "es", "IT-BOL-GALVANI2": "it"}
ZMAP = CAMP + "/inputs/zone_map_win5.csv"
ZMAP_MD5 = "93d97d50477842196e1021f5152b1bcb"
HHDIR = "/speed-scratch/o_iseri/5J/modelA/households"
SPLIT_MD5 = {"es": {"dev": "915952abb6b7060ccab6334616f6e33a", "val": "599f2acdbde37f92d80ed5189e2c7dfa", "test": "e0a9706c981c8e0442cc043f69f24136",
                    "respondents": "7063296a99876343bf6ed201ec0b8aff"},
             "it": {"dev": "92a729299090e84a9747e71def939ddf", "val": "f7dead7152420dae4ade3e77c7504ad6", "test": "59bd62e8ac85a07b0ef89c767e7f1b65",
                    "respondents": "daff79642b924ba9cfbe8819bf9ad50f"}}
SEED_B0 = 9106                      # new constant of this step (the households builder uses 9101, 9103, 9104, 9105)
N_B0 = 60                           # as the pilot's average household (60 households)
N = 8760
KEEP = ("eplusout.err", "eplusout.end", "eplustbl.csv", "eplus_stdout.txt", "writer_stdout.txt", "placement.csv", "draws.csv.gz",
        "series.tar.gz", "summary.json")
_BAD_UK = ("uk", "gb", "ldn", "london", "stdunstans")


def stamp(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def md5f(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def md5s(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def read_csv(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def assert_not_uk(*things):
    import re
    for t in things:
        if re.search(r"(^|[^a-z])(uk|gb|ldn)([^a-z]|$)|london|stdunstans", str(t), re.I):
            sys.exit("STOP: argument or path names the UK: %r" % (t,))


# ---------------------------------------------------------------------------------------------- modules
_HH = {}


def load_hh():
    if "m" not in _HH:
        sys.path.insert(0, CODE)
        spec = importlib.util.spec_from_file_location("hh9", CODE + "/5thJ_modelA_households.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _HH["m"] = m
    return _HH["m"]


_CHAIN = {}


def _is_code_file(f):
    return bool(f) and f.startswith("/speed-scratch/o_iseri/") and "site-packages" not in f and "/lib/python" not in f


def _closure(roots):
    """Every loaded code file reachable from the root modules: sys.modules alone is not enough (the households chain is loaded with
    spec_from_file_location and is never registered there), so follow module-valued globals and the home module of every function / class
    held as a global (covers `from encoder import f`). Stops at files outside the scratch code tree (stdlib, site-packages)."""
    import types
    seen, files, todo = set(), set(), list(roots)
    while todo:
        m = todo.pop()
        if m is None or id(m) in seen:
            continue
        seen.add(id(m))
        f = getattr(m, "__file__", None)
        if not _is_code_file(f):
            continue
        files.add(os.path.abspath(f))
        for v in list(vars(m).values()):
            if isinstance(v, types.ModuleType):
                todo.append(v)
            elif isinstance(v, (types.FunctionType, type)) and getattr(v, "__module__", None) in sys.modules:
                todo.append(sys.modules[v.__module__])
    return sorted(files)


def code_chain():
    """Step 9m: the code files actually LOADED. writer = closure of the writer module 5thJ_modelA_idf (-> idf_mz -> 5thJ_idf, 4thJ_step8_idf);
    households = closure of the household builder, its design tables, the trigger module and the Step 7 chain (set up by setup_modules).
    File lists are fixed once per process (a lazy import later cannot change the key); md5s are read fresh at every call."""
    if "w" not in _CHAIN:
        hh = load_hh()
        if hh.trig is None:
            hh.setup_modules()
        import importlib
        wmod = importlib.import_module("5thJ_modelA_idf")
        _CHAIN["w"] = _closure([wmod])
        _CHAIN["h"] = _closure([hh, hh.dt, hh.trig, hh.s7])
    return _CHAIN["w"], _CHAIN["h"]


def chain_md5(files, override=None):
    """md5 of the sorted (path, file md5) list; override = {path: md5} only for the weak test."""
    ov = override or {}
    pairs = sorted((f, ov.get(f) or md5f(f)) for f in files)
    return md5s("\n".join("%s %s" % x for x in pairs)), pairs


def hashes_static(override=None):
    """code md5s that go into every result (R1 d): writer_md5 / hh_md5 = md5 of the sorted (path, file md5) lists of the LOADED chain."""
    wf, hf = code_chain()
    return chain_md5(wf, override)[0], chain_md5(hf, override)[0]


def code_lists():
    wf, hf = code_chain()
    return chain_md5(wf)[1], chain_md5(hf)[1]


_ZM = {}


def zone_rows(district, stem):
    if "m" not in _ZM:
        if md5f(ZMAP) != ZMAP_MD5:
            raise RuntimeError("zone map md5 differs from the sealed one")
        sys.path.insert(0, CODE)
        import a9_common as c
        _ZM["m"] = c.zone_map(ZMAP)
    return _ZM["m"][(district, stem)]


class Light(object):
    pass


_LIGHT = {}


def light_ctx(c):
    """Weights + split lists only (no pools): enough for assign_flats. Split list md5s are checked against R1."""
    if c in _LIGHT:
        return _LIGHT[c]
    hh = load_hh()
    ctx = Light()
    ctx.weights = hh.dt.read_household_weights(hh.PARQ[c], "weight_ind")
    ctx.hids_by_split = {}
    for sp in hh.SPLITS:
        p = "%s/splits/hids_%s_%s.csv" % (HHDIR, c, sp)
        if md5f(p) != SPLIT_MD5[c][sp]:
            raise RuntimeError("household split list %s differs from the sealed md5" % p)
        ctx.hids_by_split[sp] = [r["hid"] for r in read_csv(p)]
    _LIGHT[c] = ctx
    return ctx


def b0_dir(c):
    return "%s/b0/%s" % (CAMP, c)


def b0_files(c):
    d = b0_dir(c)
    return d + "/presence_HH_%s_avg.csv" % c, d + "/elec_HH_%s_avg.csv" % c, d + "/household.json"


def placement_for(row, ctx=None):
    """Deterministic placement from the plan: list of (zone, hid) for pools dev/val/test (the no-repeat rule re-computes the earlier
    runs r' < r of the same building and pool); b0: every flat gets 'avg'; def: none."""
    hh = load_hh()
    d, stem, pool, r = row["district"], row["stem"], row["pool"], int(row["r"])
    zones = [z["zone"] for z in zone_rows(d, stem)]
    if len(zones) != int(row["n_flats"]):
        raise RuntimeError("zone map has %d zones for %s, the plan says n_flats=%s" % (len(zones), stem, row["n_flats"]))
    if pool == "def":
        return zones, []
    if pool == "b0":
        return zones, [(z, "avg") for z in zones]
    ctx = ctx or light_ctx(CC[d])
    prev = {}
    out = None
    for rr in range(1, r + 1):
        rid = "%s_%s_%s_%d" % (d, stem, pool, rr)
        out = hh.assign_flats(ctx, pool, rid, zones, exclude=prev)
        for z, h in out:
            prev.setdefault(z, set()).add(h)
    return zones, out


def placement_md5(row, placement):
    if row["pool"] == "def":
        return md5s("def|no household")
    txt = "\n".join("%s,%s" % (z, h) for z, h in placement)
    if row["pool"] == "b0":
        p, a, j = b0_files(CC[row["district"]])
        txt += "\nb0files=%s,%s,%s" % (md5f(p), md5f(a), md5f(j))
    return md5s(txt)


def current_hashes(row, ctx=None):
    w, h = hashes_static()
    zones, pl = placement_for(row, ctx)
    return {"src_idf_md5": md5f(row["src_idf"]), "writer_md5": w, "hh_md5": h, "placement_md5": placement_md5(row, pl)}


def decide(row, results_dir=None, cur=None):
    """('SKIP', why) or ('RERUN', reason). Rule R1(d)."""
    rd = results_dir or RES
    p = "%s/%s.json" % (rd, row["run_id"])
    if not os.path.exists(p):
        return "RERUN", "no result"
    try:
        j = json.load(io.open(p, encoding="utf-8"))
    except Exception as e:
        return "RERUN", "result unreadable: %r" % (e,)
    if not j.get("complete") or j.get("status") not in ("CLEAN", "NOT_CLEAN"):
        return "RERUN", "result not complete or status %s" % j.get("status")
    cur = cur or current_hashes(row)
    for k in ("src_idf_md5", "writer_md5", "hh_md5", "placement_md5"):
        if j.get(k) != cur[k]:
            return "RERUN", "%s differs (stored %s, current %s)" % (k, j.get(k), cur[k])
    return "SKIP", "all four md5 equal"


# ---------------------------------------------------------------------------------------------- households (full ctx)
def full_ctx(c):
    hh = load_hh()
    if hh.trig is None:
        hh.setup_modules()
    rows = hh.read_corpus(hh.CORPUS)
    step2 = hh.ROOT4 + "/Step2_docs/outputs_step2"
    bitpos = hh.s7.load_bit_positions(step2 + "/crosswalk_copresence.csv")
    outdoor, _m = hh.s7.indoor.load_outdoor_at_home(step2)
    ctx = hh.build_ctx(c, rows[c], bitpos, outdoor)
    ctx.members_pid_hid = dict((pid, hid) for pid, hid, _t in rows[c])
    md = {}
    for sp in hh.SPLITS:
        md[sp] = md5f("%s/splits/hids_%s_%s.csv" % (HHDIR, c, sp))
    md["respondents"] = md5f("%s/splits/respondents_%s.csv" % (HHDIR, c))
    if md != SPLIT_MD5[c]:
        raise RuntimeError("split md5 differs from the sealed ones: %s" % md)
    ctx.split_md5 = md
    # the campaign never re-calibrates: a cache miss would call calibrate_all, which is made to raise
    def _no_recal(*a, **k):
        raise RuntimeError("calibration cache key mismatch: the campaign must not re-calibrate")
    hh.trig.calibrate_all = _no_recal
    hh.calibrate(ctx)
    return ctx


# ---------------------------------------------------------------------------------------------- one run
def read_series(p):
    with io.open(p, encoding="utf-8") as fh:
        ls = [l.strip() for l in fh.read().splitlines() if l.strip()]
    return [float(x) for x in ls[1:]]


def sh(cmd, cwd, env, out_path, tag):
    e = dict(os.environ)
    e.update(env)
    with io.open(out_path, "a", encoding="utf-8") as fh:
        fh.write("### %s\n" % tag)
        fh.flush()
        rc = subprocess.call(cmd, cwd=cwd, env=e, stdout=fh, stderr=subprocess.STDOUT)
    return rc


def err_status(run):
    p = run + "/eplusout.err"
    ls = io.open(p, encoding="utf-8", errors="replace").read().splitlines() if os.path.exists(p) else []
    sev, sev_text = 0, []
    for i, l in enumerate(ls):
        if "** Severe" in l:
            sev += 1
            sev_text.append(l.strip()[:220])
            for l2 in ls[i + 1:i + 6]:
                if "~~~" in l2:
                    sev_text.append(l2.strip()[:220])
                else:
                    break
    import re
    bad = [l.strip()[:200] for l in ls if re.search(r"invalid|not found", l, re.I)]
    return {"completed": any("EnergyPlus Completed Successfully" in l for l in ls), "severe": sev, "severe_text": sev_text[:12],
            "fatal": sum(1 for l in ls if "** Fatal" in l), "warnings": sum(1 for l in ls if "** Warning" in l),
            "invalid_or_not_found": len(bad), "invalid_first": bad[:3], "err_present": os.path.exists(p)}


def do_run(row, t_start):
    d, stem, pool, r, rid = row["district"], row["stem"], row["pool"], int(row["r"]), row["run_id"]
    c = CC[d]
    res = {"run_id": rid, "district": d, "stem": stem, "pool": pool, "r": r, "mode": row["mode"], "building_split": row["building_split"],
           "n_flats": int(row["n_flats"]), "seed": int(row["seed"]), "complete": False, "status": "TASK_ERROR"}
    w5, h5 = hashes_static()
    res["writer_md5"], res["hh_md5"] = w5, h5
    res["code_files_writer"], res["code_files_hh"] = code_lists()
    res["src_idf_md5"] = md5f(row["src_idf"])
    if res["src_idf_md5"] != row["src_idf_md5"]:
        res["src_md5_mismatch_vs_plan"] = row["src_idf_md5"]
    run = "%s/%s" % (RUNS, rid)
    if os.path.exists(run):
        shutil.rmtree(run)
    os.makedirs(run)
    os.makedirs(CAMP + "/schedules", exist_ok=True)
    # schedules of the stem: ../../schedules/<stem>/... from the run folder (campaign/schedules/<stem> -> the fleet copy)
    link = "%s/schedules/%s" % (CAMP, stem)
    if not os.path.exists(link):
        try:
            os.symlink("%s/EU11_%s_%s/schedules/%s" % (FLEET, d, VINT, stem), link)
        except FileExistsError:
            pass
    wlog = run + "/writer_stdout.txt"
    hh = load_hh()
    ctx = None
    placement = []
    zones = [z["zone"] for z in zone_rows(d, stem)]
    res["zones"] = len(zones)
    # ---- households
    if pool in ("dev", "val", "test"):
        stamp("full context for %s" % c)
        ctx = full_ctx(c)
        res["hh_context_s"] = round(time.time() - t_start, 1)
        _z, pl = zones, None
        light = light_ctx(c)
        _z, pl = placement_for(row, light)
        assert _z == zones
        sdir = run + "/series"
        os.makedirs(sdir)
        draws, place_rows = [], []
        bad_series = []
        for z, h in pl:
            hy = hh.household_year(ctx, pool, h, int(row["seed"]))
            pp, ap = hh.write_household(sdir, c, h, hy)
            draws.extend(hy["records"])
            place_rows.append([z, h, pp, ap, hy["n_members"], "%.4f" % hy["peak_w"]])
            bs = hh.check_series(pp, ap, int(hy["n_members"]))
            if bs:
                bad_series.append((h, bs))
        res["series_bad"] = len(bad_series)
        if bad_series:
            raise RuntimeError("series check failed: %s" % bad_series[:2])
        dpath = run + "/draws.csv"
        hh.write_draws(dpath, draws)
        viol, nrec = hh.purity(dpath, pool, hh.read_resp_table(c))
        res["purity_records"], res["purity_violations"] = nrec, len(viol)
        res["purity_first"] = [list(v) for v in viol[:3]]
        placement = pl
        hh.write_csv(run + "/placement.csv", ["dwelling_zone", "hid", "presence_csv", "appliance_csv", "n_members", "appliance_peak_w"], place_rows)
        res["placement_md5"] = placement_md5(row, pl)
    elif pool == "b0":
        pp, ap, jj = b0_files(c)
        meta = json.load(io.open(jj, encoding="utf-8"))
        placement = [(z, "avg") for z in zones]
        place_rows = [[z, "avg", pp, ap, repr(float(meta["n_members"])), "%.4f" % float(meta["appliance_peak_w"])] for z in zones]
        hh.write_csv(run + "/placement.csv", ["dwelling_zone", "hid", "presence_csv", "appliance_csv", "n_members", "appliance_peak_w"], place_rows)
        res["placement_md5"] = placement_md5(row, placement)
        res["purity_records"], res["purity_violations"] = 0, 0
        res["purity_note"] = "b0 = average of %d DEV households; source-draw purity gate is in the prep job" % N_B0
    else:
        place_rows = []
        res["placement_md5"] = placement_md5(row, [])
        res["purity_records"], res["purity_violations"] = 0, 0
        res["purity_note"] = "default run: no household"
    stamp("households done (%d flats)" % len(place_rows))
    # ---- writer
    idf = "%s/%s.idf" % (run, rid)
    env = {"MODELA_VINTAGE": VINT, "MODELA_FLEET_ROOT": FLEET}
    cmd = [PY, CODE + "/5thJ_modelA_idf.py", "write", "--district", d, "--stem", stem, "--mode", row["mode"], "--out", idf]
    if row["mode"] == "occupancy":
        cmd += ["--placement", run + "/placement.csv"]
    rc = sh(cmd, run, env, wlog, "write")
    if rc != 0 or not os.path.exists(idf):
        raise RuntimeError("writer failed rc=%s (see writer_stdout.txt)" % rc)
    rc = sh([PY, CODE + "/5thJ_modelA_idf.py", "schedcheck", "--idf", idf], run, env, wlog, "schedcheck")
    if rc != 0:
        raise RuntimeError("schedcheck failed rc=%s (see writer_stdout.txt)" % rc)
    # ---- EnergyPlus in the run's own folder
    t0 = time.time()
    with io.open(run + "/eplus_stdout.txt", "w", encoding="utf-8") as fh:
        rc = subprocess.call([EP, "-w", EPW[d], "-d", run, "-x", "-r", idf], cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    res["ep_rc"], res["ep_wall_s"] = rc, round(time.time() - t0, 1)
    st = err_status(run)
    res.update(st)
    clean = (rc == 0 and st["completed"] and st["severe"] == 0 and st["invalid_or_not_found"] == 0 and st["err_present"]
             and os.path.exists(run + "/eplustbl.csv"))
    res["clean"] = bool(clean)
    # ---- extraction BEFORE anything is deleted
    npz = "%s/%s.npz" % (RES, rid)
    if clean:
        try:
            import numpy as np
            import a9_extract as ex
            arr, meta = ex.extract_run(run, zone_rows(d, stem))
            if arr["zones"] != zones:
                raise RuntimeError("extracted zone order differs from the zone map")
            np.savez_compressed(npz, heating=arr["heating_kwh"].astype("float32"), cooling=arr["cooling_kwh"].astype("float32"),
                                equipment=arr["equipment_kwh"].astype("float32"), total_elec=arr["total_elec_kwh"].astype("float32"),
                                zones=np.array(arr["zones"]))
            res["annual_kwh"] = meta["annual_kwh"]
            res["equipment_source"] = meta["equipment_source"]
            res["extract_rows"], res["extract_zones"] = meta["rows"], meta["n_zones"]
            res["annual_vs_sum_hourly_max_rel"] = meta["annual_vs_sum_hourly_max_rel"]
            res["status"] = "CLEAN"
            # ---- G-c3: equipment = design x series, every flat, hours with expected > 0 (0.5 %)
            if row["mode"] == "occupancy":
                worst, nbad, nchk = 0.0, 0, 0
                zi = dict((z, i) for i, z in enumerate(arr["zones"]))
                cache = {}
                for z, h, pp, ap, nm, pk in place_rows:
                    if ap not in cache:
                        cache[ap] = read_series(ap)
                    series = cache[ap]
                    lvl = float(pk)
                    got = arr["equipment_kwh"][zi[z]]
                    for hr in range(N):
                        exp = lvl * series[hr] / 1000.0
                        if exp > 0:
                            rel = abs(got[hr] - exp) / exp
                            nchk += 1
                            if rel > worst:
                                worst = rel
                            if rel > 0.005:
                                nbad += 1
                res["gc3_max_rel"], res["gc3_hours_checked"], res["gc3_hours_bad"] = worst, nchk, nbad
                res["gc3_fail"] = bool(nbad > 0 or nchk == 0)
            else:
                res["gc3_fail"] = None
                res["gc3_note"] = "default run: no ElectricEquipment series"
        except Exception as e:
            res["status"] = "EXTRACT_FAILED"
            res["extract_reason"] = (repr(e) + " | " + traceback.format_exc()[-400:])[:900]
    else:
        res["status"] = "NOT_CLEAN"
        res["not_clean_reason"] = "rc=%s completed=%s severe=%s invalid_or_not_found=%s" % (rc, st["completed"], st["severe"], st["invalid_or_not_found"])
    # ---- keep list, delete the rest
    stamp("cleanup")
    if os.path.isdir(run + "/series"):
        with tarfile.open(run + "/series.tar.gz", "w:gz") as tf:
            for fn in sorted(os.listdir(run + "/series")):
                tf.add(run + "/series/" + fn, arcname=fn)
    if os.path.exists(run + "/draws.csv"):
        with io.open(run + "/draws.csv", "rb") as fi, gzip.open(run + "/draws.csv.gz", "wb") as fo:
            shutil.copyfileobj(fi, fo)
    with io.open(idf, "rb") as fi, gzip.open(idf + ".gz", "wb") as fo:
        shutil.copyfileobj(fi, fo)
    json.dump(res, io.open(run + "/summary.json", "w", encoding="utf-8"), indent=1, default=str)
    for fn in os.listdir(run):
        if fn in KEEP or fn == rid + ".idf.gz":
            continue
        p = run + "/" + fn
        if os.path.isdir(p) and not os.path.islink(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
    kept = sum(os.path.getsize(run + "/" + fn) for fn in os.listdir(run))
    kept += os.path.getsize(npz) if os.path.exists(npz) else 0
    res["bytes_kept"] = kept
    res["bytes_kept_note"] = "run folder + extracted npz (json of the result not counted)"
    return res


def cmd_run(argv):
    manifest, n = argv[0], int(argv[1])
    assert_not_uk(manifest)
    rows = read_csv(manifest)
    row = rows[n - 1]
    if row["district"] not in CC:
        sys.exit("STOP: district %r is not a Model A district" % row["district"])
    os.makedirs(RES, exist_ok=True)
    os.makedirs(RUNS, exist_ok=True)
    t0 = time.time()
    stamp("task %d run_id=%s pool=%s mode=%s flats=%s host=%s" % (n, row["run_id"], row["pool"], row["mode"], row["n_flats"], os.uname()[1]))
    try:
        verdict, why = decide(row)
    except Exception as e:
        verdict, why = "RERUN", "decide crashed: %r" % (e,)
    print("DECIDE %s %s %s" % (row["run_id"], verdict, why), flush=True)
    if verdict == "SKIP":
        print("SKIPPED %s" % row["run_id"], flush=True)
        return 0
    try:
        res = do_run(row, t0)
        res["complete"] = True
    except Exception as e:
        res = {"run_id": row["run_id"], "district": row["district"], "stem": row["stem"], "pool": row["pool"], "status": "TASK_ERROR",
               "complete": True, "error": (repr(e) + " | " + traceback.format_exc()[-1200:])[:1500]}
    res["task_wall_s"] = round(time.time() - t0, 1)
    tmp = "%s/%s.json.tmp" % (RES, row["run_id"])
    json.dump(res, io.open(tmp, "w", encoding="utf-8"), indent=1, default=str)
    os.replace(tmp, "%s/%s.json" % (RES, row["run_id"]))
    print("RESULT %s status=%s wall=%.1f" % (row["run_id"], res["status"], res["task_wall_s"]), flush=True)
    return 1 if res["status"] == "TASK_ERROR" else 0


# ---------------------------------------------------------------------------------------------- prep
def gate(name, ok, msg=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", msg), flush=True)
    return bool(ok)


def selftest_decide(row):
    """Synthetic result with the CURRENT hashes: SKIP; one md5 at a time changed: RERUN."""
    ok = True
    d = CAMP + "/skiptest_synth"
    os.makedirs(d, exist_ok=True)
    cur = current_hashes(row)
    base = {"run_id": row["run_id"], "status": "CLEAN", "complete": True}
    base.update(cur)
    p = "%s/%s.json" % (d, row["run_id"])
    json.dump(base, io.open(p, "w", encoding="utf-8"))
    v, _ = decide(row, d, cur)
    ok &= gate("skip_rule_synthetic_equal_md5_skips", v == "SKIP", v)
    for k in ("src_idf_md5", "writer_md5", "hh_md5", "placement_md5"):
        j = dict(base)
        j[k] = "0" * 32
        json.dump(j, io.open(p, "w", encoding="utf-8"))
        v, why = decide(row, d, cur)
        ok &= gate("skip_rule_synthetic_changed_%s_reruns (seen failing)" % k, v == "RERUN", why[:60])
    j = dict(base)
    j["status"] = "TASK_ERROR"
    json.dump(j, io.open(p, "w", encoding="utf-8"))
    ok &= gate("skip_rule_synthetic_task_error_reruns", decide(row, d, cur)[0] == "RERUN")
    return ok


def cmd_prep(argv):
    manifest = argv[0]
    assert_not_uk(manifest)
    hh = load_hh()
    ok = True
    for sub in ("logs", "results", "runs", "schedules", "manifests", "inputs", "b0", "skiptest"):
        os.makedirs("%s/%s" % (CAMP, sub), exist_ok=True)
    ok &= gate("zone_map_md5", md5f(ZMAP) == ZMAP_MD5, md5f(ZMAP))
    rows = read_csv(manifest)
    for c in ("es", "it"):
        if c == "it":
            continue                                   # Bologna waits for _win_2026-10-04; its B0 is built when it is run
        stamp("prep country %s" % c)
        ctx = full_ctx(c)
        # light vs full: same placements
        light = light_ctx(c)
        ok &= gate("%s_light_ctx_equals_full_ctx_lists" % c, all(ctx.hids_by_split[s] == light.hids_by_split[s] for s in hh.SPLITS) and ctx.weights == light.weights)
        # B0: 60 DEV households by survey weight (key log(1-u)/w), no replacement
        rng = hh.dt.rng_for(SEED_B0, "b0", c)
        keyed = sorted(((math.log(1.0 - rng.random()) / ctx.weights[h], h) for h in ctx.hids_by_split["dev"]), reverse=True)
        chosen = [h for _, h in keyed[:N_B0]]
        ok &= gate("%s_b0_households_are_dev_only" % c, all(ctx.split_of_hid[h] == "dev" for h in chosen) and len(set(chosen)) == N_B0, "n=%d" % len(chosen))
        seed = hh.run_seed_of("%s_b0avg" % c)
        sdir = "%s/src" % b0_dir(c)
        os.makedirs(sdir, exist_ok=True)
        loaded, recs = [], []
        for h in chosen:
            hy = hh.household_year(ctx, "dev", h, seed)
            pp, ap = hh.write_household(sdir, c, h, hy)
            recs.extend(hy["records"])
            loaded.append({"presence": hy["presence"], "frac": hy["appliance_frac"], "peak": hy["peak_w"], "n_members": hy["n_members"]})
        dpath = b0_dir(c) + "/draws_b0avg.csv"
        hh.write_draws(dpath, recs)
        viol, nrec = hh.purity(dpath, "dev", hh.read_resp_table(c))
        ok &= gate("%s_b0_source_draws_purity_dev" % c, not viol and nrec > 0, "records=%d violations=%d" % (nrec, len(viol)))
        # average (rule of the pilot's `<cc>_avg`, hh_build.average_series)
        def average(ld):
            n = float(len(ld))
            pres = [sum(x["presence"][t] for x in ld) / n for t in range(N)]
            watts = [sum(x["frac"][t] * x["peak"] for x in ld) / n for t in range(N)]
            peak = max(watts)
            return {"presence": pres, "frac": [w / peak for w in watts], "peak": peak, "n_members": sum(x["n_members"] for x in ld) / n}
        av = average(loaded)
        pn, an, jn = b0_files(c)
        with io.open(pn, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(u"HH_%s_avg_Presence\n" % c)
            for v in av["presence"]:
                fh.write(u"%.12f\n" % v)
        with io.open(an, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(u"HH_%s_avg_ApplianceFraction\n" % c)
            for v in av["frac"]:
                fh.write(u"%.12f\n" % v)
        meta = {"hid": "avg", "country": c, "n_members": av["n_members"], "appliance_peak_w": av["peak"], "average_of": N_B0, "hids": chosen,
                "split": "dev only", "weighting": "UNWEIGHTED mean of %d dev households drawn by survey weight (key log(1-u)/w, seed %d)" % (N_B0, SEED_B0),
                "run_seed": seed, "presence_md5": md5f(pn), "elec_md5": md5f(an)}
        json.dump(meta, io.open(jn, "w", encoding="utf-8"), indent=1)

        def kwh_of(path, peak):
            return sum(read_series(path)) * peak / 1000.0
        mean60 = sum(sum(x["frac"]) * x["peak"] for x in loaded) / 1000.0 / N_B0
        kavg = kwh_of(an, av["peak"])
        ok &= gate("%s_b0_avg_kwh_equals_mean_of_60" % c, abs(kavg - mean60) / mean60 < 1e-9, "avg=%.6f mean60=%.6f" % (kavg, mean60))
        bad = [dict(x) for x in loaded]
        bad[0]["frac"] = [v * 1.01 for v in bad[0]["frac"]]
        bav = average(bad)
        ok &= gate("%s_b0_kwh_gate_seen_failing_one_household_x1.01" % c, abs(sum(bav["frac"]) * bav["peak"] / 1000.0 - mean60) / mean60 > 1e-9)
        ok &= gate("%s_b0_series_8760_in_range" % c, len(read_series(pn)) == N and len(read_series(an)) == N and min(read_series(pn)) >= 0 and max(read_series(pn)) <= 1.0 and min(read_series(an)) >= 0)
        print("B0 %s n_members=%.4f appliance_peak_w=%.4f annual_kwh=%.4f presence_md5=%s elec_md5=%s" % (c, av["n_members"], av["peak"], kavg, meta["presence_md5"], meta["elec_md5"]), flush=True)
        # placement: light == full
        r0 = [r for r in rows if r["pool"] == "dev" and CC[r["district"]] == c][0]
        ok &= gate("%s_placement_light_equals_full" % c, placement_for(r0, light) == placement_for(r0, ctx), r0["run_id"])
    ok &= selftest_decide([r for r in rows if r["pool"] == "dev"][0])
    print("PREP_SUMMARY %s" % ("ALL PASS" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


# ---------------------------------------------------------------------------------------------- check
def check_core(rows, rd):
    """Return counters + lists from the manifest rows and the results dir rd."""
    out = {"rows": len(rows), "done": 0, "missing": [], "not_clean": [], "extract_failed": [], "task_error": [], "purity_viol": [],
           "gc3_fail": [], "src_md5_mismatch": [], "cpu_s": {}, "bytes": {}, "clean": 0, "incomplete": []}
    for r in rows:
        p = "%s/%s.json" % (rd, r["run_id"])
        if not os.path.exists(p):
            out["missing"].append(r["run_id"])
            continue
        j = json.load(io.open(p, encoding="utf-8"))
        if not j.get("complete"):
            out["incomplete"].append(r["run_id"])
            continue
        out["done"] += 1
        d = r["district"]
        out["cpu_s"][d] = out["cpu_s"].get(d, 0.0) + float(j.get("task_wall_s") or 0.0)
        out["bytes"][d] = out["bytes"].get(d, 0) + int(j.get("bytes_kept") or 0)
        st = j.get("status")
        if st == "CLEAN":
            out["clean"] += 1
        elif st == "NOT_CLEAN":
            out["not_clean"].append((r["run_id"], j.get("not_clean_reason"), (j.get("severe_text") or [""])[:1]))
        elif st == "EXTRACT_FAILED":
            out["extract_failed"].append((r["run_id"], (j.get("extract_reason") or "")[:200]))
        else:
            out["task_error"].append((r["run_id"], (j.get("error") or "")[:200]))
        if int(j.get("purity_violations") or 0) > 0:
            out["purity_viol"].append((r["run_id"], j.get("purity_violations")))
        if j.get("gc3_fail") is True:
            out["gc3_fail"].append((r["run_id"], j.get("gc3_max_rel"), j.get("gc3_hours_bad")))
        if j.get("src_idf_md5") != r["src_idf_md5"]:
            out["src_md5_mismatch"].append((r["run_id"], j.get("src_idf_md5"), r["src_idf_md5"]))
    return out


def cmd_check(argv):
    manifest = argv[0]
    assert_not_uk(manifest)
    rows = read_csv(manifest)
    crashed = []
    try:
        cw, ch = code_lists()
        print("CODE_FILES_WRITER %d writer_md5=%s" % (len(cw), hashes_static()[0]), flush=True)
        for f, m in cw:
            print("  %s %s" % (m, f), flush=True)
        print("CODE_FILES_HH %d hh_md5=%s" % (len(ch), hashes_static()[1]), flush=True)
        for f, m in ch:
            print("  %s %s" % (m, f), flush=True)
    except Exception as e:
        crashed.append("code_files")
        print("SECTION code_files NOT_EVALUABLE %r %s" % (e, traceback.format_exc()[-300:]), flush=True)
    print("CHECK a9_campaign_check manifest=%s rows=%d results=%s" % (manifest, len(rows), RES), flush=True)

    # ---- control: the check must SEE planted faults (synthetic results in a scratch folder, not the real ones)
    try:
        d = CAMP + "/checktest_synth"
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        fake = [dict(run_id="f%d" % i, district="ES-MAD-BERRUGUETE", src_idf_md5="aa") for i in range(7)]
        base = {"complete": True, "status": "CLEAN", "purity_violations": 0, "gc3_fail": False, "src_idf_md5": "aa", "task_wall_s": 10, "bytes_kept": 100}
        plants = {0: {}, 1: {"status": "NOT_CLEAN", "not_clean_reason": "planted"}, 2: {"purity_violations": 3}, 3: {"gc3_fail": True, "gc3_max_rel": 0.1},
                  4: {"src_idf_md5": "bb"}, 5: {"status": "EXTRACT_FAILED", "extract_reason": "planted"}}   # 6 = missing
        for i, ch in plants.items():
            j = dict(base)
            j.update(ch)
            json.dump(j, io.open("%s/f%d.json" % (d, i), "w", encoding="utf-8"))
        o = check_core(fake, d)
        fired = (len(o["not_clean"]) == 1 and len(o["purity_viol"]) == 1 and len(o["gc3_fail"]) == 1 and len(o["src_md5_mismatch"]) == 1
                 and len(o["extract_failed"]) == 1 and len(o["missing"]) == 1 and o["clean"] == 4)   # f0, f2, f3, f4 keep status CLEAN (purity, G-c3 and src md5 faults do not change the EnergyPlus status); fixed 20:17 after the smoke check printed DID_NOT_FIRE with every count right
        print("CONTROL planted_faults (1 not clean, 1 purity, 1 G-c3, 1 src md5, 1 extract failed, 1 missing) %s: not_clean=%d purity=%d gc3=%d src=%d extract=%d missing=%d clean=%d"
              % ("FIRED" if fired else "DID_NOT_FIRE", len(o["not_clean"]), len(o["purity_viol"]), len(o["gc3_fail"]), len(o["src_md5_mismatch"]),
                 len(o["extract_failed"]), len(o["missing"]), o["clean"]), flush=True)
    except Exception as e:
        crashed.append("control")
        print("SECTION control NOT_EVALUABLE %r" % (e,), flush=True)

    # ---- main section
    try:
        o = check_core(rows, RES)
        print("ROWS total=%d done=%d clean=%d missing=%d incomplete=%d" % (o["rows"], o["done"], o["clean"], len(o["missing"]), len(o["incomplete"])), flush=True)
        print("NOT_CLEAN %d" % len(o["not_clean"]), flush=True)
        for x in o["not_clean"]:
            print("  NOT_CLEAN %s | %s | %s" % x, flush=True)
        print("EXTRACT_FAILED %d" % len(o["extract_failed"]), flush=True)
        for x in o["extract_failed"]:
            print("  EXTRACT_FAILED %s | %s" % x, flush=True)
        print("TASK_ERROR %d" % len(o["task_error"]), flush=True)
        for x in o["task_error"]:
            print("  TASK_ERROR %s | %s" % x, flush=True)
        print("PURITY_VIOLATIONS %d %s" % (len(o["purity_viol"]), o["purity_viol"][:5]), flush=True)
        print("GC3_FAILURES %d %s" % (len(o["gc3_fail"]), o["gc3_fail"][:5]), flush=True)
        print("SRC_MD5_MISMATCH %d %s" % (len(o["src_md5_mismatch"]), o["src_md5_mismatch"][:5]), flush=True)
        for d_ in sorted(o["cpu_s"]):
            print("CPU_SECONDS %s %.1f (= %.2f CPU-h) BYTES_KEPT %d (= %.3f GB)" % (d_, o["cpu_s"][d_], o["cpu_s"][d_] / 3600.0, o["bytes"][d_], o["bytes"][d_] / 1e9), flush=True)
        if o["missing"]:
            print("MISSING first 10: %s" % o["missing"][:10], flush=True)
    except Exception as e:
        crashed.append("main")
        print("SECTION main NOT_EVALUABLE %r %s" % (e, traceback.format_exc()[-300:]), flush=True)

    # ---- skip rule on a COPY of a real result
    if "--skiptest" in argv:
        try:
            done = [r for r in rows if os.path.exists("%s/%s.json" % (RES, r["run_id"]))
                    and json.load(io.open("%s/%s.json" % (RES, r["run_id"]), encoding="utf-8")).get("status") == "CLEAN"]
            if not done:
                raise RuntimeError("no CLEAN real result to copy")
            r = done[0]
            d = CAMP + "/skiptest"
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            cur = current_hashes(r)
            shutil.copyfile("%s/%s.json" % (RES, r["run_id"]), "%s/%s.json" % (d, r["run_id"]))
            v0, why0 = decide(r, d, cur)
            ok = (v0 == "SKIP")
            print("SKIPTEST copy of real result %s unchanged -> %s (%s)" % (r["run_id"], v0, why0), flush=True)
            for k in ("src_idf_md5", "writer_md5", "hh_md5", "placement_md5"):
                j = json.load(io.open("%s/%s.json" % (d, r["run_id"]), encoding="utf-8"))
                j[k] = "0" * 32
                json.dump(j, io.open("%s/%s.json" % (d, r["run_id"]), "w", encoding="utf-8"))
                v, why = decide(r, d, cur)
                ok &= (v == "RERUN")
                print("SKIPTEST copy with %s changed -> %s (%s)" % (k, v, why[:70]), flush=True)
                shutil.copyfile("%s/%s.json" % (RES, r["run_id"]), "%s/%s.json" % (d, r["run_id"]))
            print("CONTROL skip_rule_on_real_copy %s" % ("FIRED" if ok else "DID_NOT_FIRE"), flush=True)
        except Exception as e:
            crashed.append("skiptest")
            print("SECTION skiptest NOT_EVALUABLE %r %s" % (e, traceback.format_exc()[-300:]), flush=True)
    print("CHECK_SUMMARY sections_crashed=%s %s" % (crashed, "ALL SECTIONS RAN" if not crashed else "NOT_EVALUABLE: " + ",".join(crashed)), flush=True)
    return 4 if crashed else 0


# ---------------------------------------------------------------------------------------------- Step 9m test (staged copy only)
def cmd_codekeytest(argv):
    """codekeytest <manifest.csv> <run_id>: needs A9_CAMP = a staged copy (never the live campaign). Expects results/<run_id>.json (a finished
    result with OLD keys) in the stage. Never runs EnergyPlus; edits only files under the stage and restores them."""
    manifest, rid = argv[0], argv[1]
    assert_not_uk(manifest, rid)
    if CAMP == LIVE_CAMP or not os.environ.get("A9_CAMP"):
        sys.exit("STOP: codekeytest only runs on a staged copy (A9_CAMP)")
    row = [r for r in read_csv(manifest) if r["run_id"] == rid][0]
    ok = True
    wl, hl = code_lists()
    print("CODE_FILES_WRITER %d" % len(wl))
    for f, m in wl:
        print("  %s %s" % (m, f))
    print("CODE_FILES_HH %d" % len(hl))
    for f, m in hl:
        print("  %s %s" % (m, f))
    ok &= gate("(a) writer list incl. 4thJ_step8_idf, 5thJ_idf, 5thJ_idf_mz, 5thJ_modelA_idf",
               all(any(f.endswith("/" + n) for f, _ in wl) for n in ("4thJ_step8_idf.py", "5thJ_idf.py", "5thJ_idf_mz.py", "5thJ_modelA_idf.py")), str(len(wl)))
    ok &= gate("(a) hh list incl. households, design_tables, trigger_act2, step7_schedules, step7_indoor",
               all(any(f.endswith("/" + n) for f, _ in hl) for n in ("5thJ_modelA_households.py", "5thJ_design_tables.py", "5thJ_step9_trigger_act2.py",
                                                                      "4thJ_step7_schedules.py", "4thJ_step7_indoor.py")), str(len(hl)))
    ok &= gate("(a) every listed file is a .py under the stage or the households repo",
               all((f.startswith(CAMP + "/") or f.startswith("/speed-scratch/o_iseri/5J/households/repo/")) and f.endswith(".py") for f, _ in wl + hl))
    p = "%s/%s.json" % (RES, rid)
    j = json.load(io.open(p, encoding="utf-8"))
    print("stored keys before re-key: writer=%s hh=%s" % (j.get("writer_md5"), j.get("hh_md5")))
    v, why = decide(row)
    ok &= gate("(b0) result with OLD keys -> RERUN", v == "RERUN", why[:90])
    cur = current_hashes(row)
    j.update(cur)
    json.dump(j, io.open(p, "w", encoding="utf-8"))
    v, why = decide(row)
    ok &= gate("(b) result re-keyed with NEW hashes -> SKIP", v == "SKIP", why)

    def edit_test(tag, path, key):
        raw = io.open(path, "rb").read()
        m0 = md5f(path)
        try:
            with io.open(path, "ab") as fh:
                fh.write(b"\n# 9m test comment line\n")
            v1, why1 = decide(row)
            ok1 = (v1 == "RERUN" and key in why1)
        finally:
            with io.open(path, "wb") as fh:
                fh.write(raw)
        v2, why2 = decide(row)
        a = gate("%s edit of %s -> RERUN on %s" % (tag, os.path.basename(path), key), ok1, why1[:90])
        b = gate("%s restored (md5 %s equal: %s) -> SKIP" % (tag, m0, md5f(path) == m0), v2 == "SKIP" and md5f(path) == m0, why2)
        return a and b
    wpath = [f for f, _ in wl if f.endswith("/4thJ_step8_idf.py")][0]
    assert wpath.startswith(CAMP + "/"), wpath
    ok &= edit_test("(c)", wpath, "writer_md5")
    hpath = [f for f, _ in hl if f.endswith("/5thJ_design_tables.py")][0]
    assert hpath.startswith(CAMP + "/"), hpath
    ok &= edit_test("(d)", hpath, "hh_md5")
    # (d2) WEAK test: household-chain files outside the stage (households/repo) are never edited; one md5 altered in the list only
    for f in [f for f, _ in hl if not f.startswith(CAMP + "/")]:
        a = hashes_static()[1]
        b = hashes_static({f: "0" * 32})[1]
        ok &= gate("(d2) WEAK test (md5 altered in the list, file not edited): %s" % os.path.basename(f), a != b)
    print("CODEKEYTEST_SUMMARY %s" % ("ALL PASS" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


def main(argv):
    cmd = argv[1]
    if cmd == "run":
        return cmd_run(argv[2:])
    if cmd == "prep":
        return cmd_prep(argv[2:])
    if cmd == "codekeytest":
        return cmd_codekeytest(argv[2:])
    if cmd == "check":
        return cmd_check(argv[2:])
    sys.exit("unknown command %r" % cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
