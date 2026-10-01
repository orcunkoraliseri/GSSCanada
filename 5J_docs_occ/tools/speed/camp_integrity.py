# -*- coding: utf-8 -*-
"""5J Step 3 part 2, G5J.1 campaign integrity over every planned run (Speed job only; Spain + Italy only, never a UK file).

EXIT CODE MEANING (read this first): exit 0 ONLY when SUMMARY FAIL=0 and NOT_EVALUABLE=0; exit 1 otherwise.
A check that crashed, or that had nothing to evaluate, is NOT_EVALUABLE, never PASS. A check is FAIL if any run fails it.

Usage:  python -u camp_integrity.py [--ids FILE] [--workers N]
   no --ids : all planned runs of the two frozen tables (9,269), plus the folder-level check C12
   --ids F  : subset mode (one run_id per line), used for the seen-failing tests on scratch trees; C12 is skipped
Environment (as camp_common): CAMP_ROOT (done/ extracted/ runs/ of the tree under test), CAMP_HH (household folders).

Checks (one CHECK line each):
  C01 done.json present, status pass, every recorded check ok, EnergyPlus rc 0
  C02 cache key in done.json equals the key recomputed now from the current inputs (household files, EPW, builder, ...)
  C03 extracted files (csv.gz + dwellings.csv) exist, non-empty, size and md5 equal done.json (truncated-output check)
  C04 every file read: 8,760 rows per dwelling per target, hours 1..8760, finite, dwellings in file = n_dwellings of the plan
  C05 annual heating, cooling, equipment finite and >= 0 for every dwelling
  C06 raw run folder deleted (runs/<run_id>/ absent)
  C07 done/<run_id>.err: Completed Successfully and 0 Severe
  C08 dwellings.csv: n_dwellings rows, hid of dwelling j = household in the plan placement
  C09 per building and climate, no two flats with different households have an identical hourly equipment series
  C10 replicates: dwelling, hour and the 4 target columns equal to the original (whole-file bytes counted, non-target columns reported); max spread per target printed
  C11 B0 runs: every flat has the average household (plan placement and dwellings.csv)
  C12 (full mode) plan = 9,269 unique runs; done/ = json + err of exactly these; extracted/ = exactly these two files each
"""
import gzip, hashlib, io, json, multiprocessing as mp, os, sys, traceback, argparse
import numpy as np
import pandas as pd
import camp_common as cc

CHECKS = [("C01", "done_json_pass"), ("C02", "cache_key_equal"), ("C03", "extracted_size_md5"),
          ("C04", "rows_8760_per_dwelling_per_target"), ("C05", "annual_finite_nonneg"), ("C06", "raw_folder_deleted"),
          ("C07", "err_completed_0_severe"), ("C08", "dwellings_csv_placement"), ("C09", "households_differ_equipment"),
          ("C10", "replicates_equal_original"), ("C11", "b0_average_household"), ("C12", "folder_level_counts")]
NAME = dict(CHECKS)
EXPECTED_TOTAL = 9269


def _short(e):
    return traceback.format_exc().strip().splitlines()[-1][:160]


def read_ext(rid, arr):
    return cc.ROOT + "extracted/%s/%s.csv.gz" % (arr, rid), cc.ROOT + "extracted/%s/%s.dwellings.csv" % (arr, rid)


def check_run(run):
    """Per-run checks C01-C08 and C11. Returns (run_id, {check: (status, detail)}, group_data)."""
    rid, cty = run["run_id"], run["country"]
    n_dw = int(run["n_dwellings"])
    res, gd = {}, {"bld": (run["building_id"], run["climate_id"]), "flats": None}
    plc = cc.parse_placement(run["placement"])
    rec = None
    # C06
    try:
        res["C06"] = ("FAIL", "runs/%s still exists" % rid) if os.path.exists(cc.ROOT + "runs/" + rid) else ("PASS", "")
    except Exception as e:
        res["C06"] = ("NOT_EVALUABLE", _short(e))
    # C01
    try:
        p = cc.done_json(rid)
        if not os.path.exists(p):
            res["C01"] = ("FAIL", "no done.json")
        else:
            rec = json.load(io.open(p, encoding="utf-8"))
            bad = []
            if rec.get("status") != "pass":
                bad.append("status=%s" % rec.get("status"))
            if not rec.get("checks") or not all(c["ok"] for c in rec["checks"]):
                bad.append("a recorded check is not ok")
            if rec.get("energyplus_rc") != 0:
                bad.append("rc=%s" % rec.get("energyplus_rc"))
            if rec.get("run_id") != rid:
                bad.append("run_id mismatch")
            res["C01"] = ("FAIL", "; ".join(bad)) if bad else ("PASS", "")
    except Exception as e:
        res["C01"] = ("NOT_EVALUABLE", _short(e))
    ne = ("NOT_EVALUABLE", "no readable done.json")
    # C02
    try:
        if rec is None or "cache_key" not in rec:
            res["C02"] = ne
        else:
            k = cc.cache_key(run)
            res["C02"] = ("PASS", "") if k == rec["cache_key"] else ("FAIL", "done.json key %s != recomputed %s" % (rec["cache_key"][:8], k[:8]))
    except Exception as e:
        res["C02"] = ("NOT_EVALUABLE", _short(e))
    # C03
    gz, dw = read_ext(rid, run["climate_id"])
    try:
        if rec is None or "extracted" not in rec:
            res["C03"] = ne
        else:
            bad = []
            for key, path in (("csv_gz", gz), ("dwellings_csv", dw)):
                ex = rec["extracted"][key]
                if not ex["file"].startswith(run["climate_id"] + "/"):
                    bad.append("%s recorded under another array" % key)
                if not os.path.exists(path):
                    bad.append("%s missing" % key)
                    continue
                sz = os.path.getsize(path)
                if sz == 0:
                    bad.append("%s empty" % key)
                if sz != ex["bytes"]:
                    bad.append("%s size %d != %d" % (key, sz, ex["bytes"]))
                if cc.md5(path) != ex["md5"]:
                    bad.append("%s md5 differs" % key)
            res["C03"] = ("FAIL", "; ".join(bad)) if bad else ("PASS", "")
    except Exception as e:
        res["C03"] = ("NOT_EVALUABLE", _short(e))
    # C04, C05 (read every file)
    try:
        if not os.path.exists(gz):
            res["C04"] = res["C05"] = ("NOT_EVALUABLE", "extracted file missing (see C03)")
        else:
            try:
                df = pd.read_csv(gz, comment="#", compression="gzip")
            except Exception as e:
                res["C04"] = ("FAIL", "unreadable: %s" % _short(e))
                res["C05"] = ("NOT_EVALUABLE", "file unreadable")
                df = None
            if df is not None:
                s, t = cc.check_rows(df, n_dw)
                res["C04"] = (s, t if s != "PASS" else "")
                bad = []
                flats = []
                for j in sorted(df["dwelling"].unique()):
                    sub = df[df["dwelling"] == j]
                    ann = {}
                    for tg in ("heating_kwh", "cooling_kwh", "equipment_kwh"):
                        a = float(sub[tg].sum())
                        ann[tg] = a
                        if not (np.isfinite(a) and a >= 0):
                            bad.append("dw%d %s annual=%s" % (j, tg, a))
                    eq = sub["equipment_kwh"].to_numpy(dtype=float)
                    flats.append((int(j), hashlib.md5(eq.tobytes()).hexdigest(), ann))
                res["C05"] = ("FAIL", "; ".join(bad[:3])) if bad else ("PASS", "")
                gd["flats"] = flats
    except Exception as e:
        res["C04"] = res.get("C04", ("NOT_EVALUABLE", _short(e)))
        res["C05"] = res.get("C05", ("NOT_EVALUABLE", _short(e)))
    # C07
    try:
        ep = cc.ROOT + "done/%s.err" % rid
        if not os.path.exists(ep):
            res["C07"] = ("FAIL", "no done/%s.err" % rid)
        else:
            ok, why = cc.check_err(io.open(ep, encoding="utf-8", errors="replace").read())
            res["C07"] = ("PASS", "") if ok else ("FAIL", "; ".join(why))
    except Exception as e:
        res["C07"] = ("NOT_EVALUABLE", _short(e))
    # C08 and C11
    try:
        if not os.path.exists(dw):
            res["C08"] = ("NOT_EVALUABLE", "dwellings.csv missing (see C03)")
            dwdf = None
        else:
            dwdf = pd.read_csv(dw, dtype={"hid": str})
            bad = []
            if len(dwdf) != n_dw:
                bad.append("rows=%d expected %d" % (len(dwdf), n_dw))
            if sorted(dwdf["dwelling"].tolist()) != list(range(n_dw)):
                bad.append("dwelling numbers not 0..%d" % (n_dw - 1))
            for _, r in dwdf.iterrows():
                if plc.get(int(r["dwelling"])) != str(r["hid"]):
                    bad.append("dw%d hid %s != placement %s" % (r["dwelling"], r["hid"], plc.get(int(r["dwelling"]))))
            res["C08"] = ("FAIL", "; ".join(bad[:3])) if bad else ("PASS", "")
        if run["pool"] == "b0":
            avg = cty + "_avg"
            bad = [j for j, t in plc.items() if t != avg]
            if dwdf is not None:
                bad += ["dwfile%s" % r["dwelling"] for _, r in dwdf.iterrows() if str(r["hid"]) != avg]
            res["C11"] = ("PASS", "") if not bad and len(plc) == n_dw else ("FAIL", "not all flats %s: %s" % (avg, bad[:3]))
    except Exception as e:
        res["C08"] = res.get("C08", ("NOT_EVALUABLE", _short(e)))
        if run["pool"] == "b0":
            res["C11"] = ("NOT_EVALUABLE", _short(e))
    gd["placement"] = plc
    return rid, res, gd


def content_bytes(gzpath):
    """Decompressed file content without the '#' header lines."""
    with gzip.open(gzpath, "rb") as fh:
        return b"".join(ln for ln in fh.read().splitlines(True) if not ln.startswith(b"#"))


def replicate_check(runs_by_id):
    """C10. Returns (status, detail, spread_lines)."""
    reps = [r for r in runs_by_id.values() if int(r["replicate"]) > 0]
    if not reps:
        return "NOT_EVALUABLE", "no replicate runs in this set", []
    bad, ne = [], []
    groups = {}
    for r in reps:
        base = r["run_id"].rsplit("_rep", 1)[0]
        groups.setdefault(base, []).append(r)
    spread = {t: [0.0, 0.0] for t in cc.TARGETS}   # [max abs hourly diff, max annual spread across the group]
    other = {}                                     # non-target column -> [max abs diff, max value]  (informational)
    n_ok = 0
    n_bytes_equal = 0
    for base, lst in sorted(groups.items()):
        try:
            if base not in runs_by_id:
                ne.append("%s original not in the run set" % base)
                continue
            org = runs_by_id[base]
            op = read_ext(base, org["climate_id"])[0]
            ocont = content_bytes(op)
            odf = pd.read_csv(op, comment="#", compression="gzip")
            annual = {t: [float(odf[t].sum())] for t in cc.TARGETS}
            for r in lst:
                rp = read_ext(r["run_id"], r["climate_id"])[0]
                rcont = content_bytes(rp)
                rdf = pd.read_csv(rp, comment="#", compression="gzip")
                if rcont == ocont:
                    n_bytes_equal += 1
                # PATCH c10_targets_exact: the gate is the dwelling, hour and the 4 TARGET columns equal to the last digit;
                # the other (diagnostic) columns differ at machine-noise level between hosts (seen 2026-09-30: 1e-16 kWh, rh 3e-6 %),
                # they are reported, not gated.
                same_keys = (list(rdf.columns) == list(odf.columns) and len(rdf) == len(odf)
                             and np.array_equal(rdf["dwelling"].to_numpy(), odf["dwelling"].to_numpy())
                             and np.array_equal(rdf["hour"].to_numpy(), odf["hour"].to_numpy()))
                if not same_keys:
                    bad.append("%s columns, rows, dwelling or hour differ from %s" % (r["run_id"], base))
                    continue
                for t in cc.TARGETS:
                    if not np.array_equal(rdf[t].to_numpy(), odf[t].to_numpy()):
                        bad.append("%s target %s differs from %s" % (r["run_id"], t, base))
                for c in odf.columns:
                    if c in cc.TARGETS or c in ("dwelling", "hour"):
                        continue
                    d = float(np.abs(rdf[c].to_numpy(dtype=float) - odf[c].to_numpy(dtype=float)).max())
                    o = other.setdefault(c, [0.0, 0.0])
                    o[0] = max(o[0], d)
                    o[1] = max(o[1], float(np.abs(odf[c].to_numpy(dtype=float)).max()))
                for t in cc.TARGETS:
                    spread[t][0] = max(spread[t][0], float(np.abs(rdf[t].to_numpy() - odf[t].to_numpy()).max()))
                    annual[t].append(float(rdf[t].sum()))
                n_ok += 1
            for t in cc.TARGETS:
                spread[t][1] = max(spread[t][1], max(annual[t]) - min(annual[t]))
        except Exception as e:
            ne.append("%s: %s" % (base, _short(e)))
    lines = ["REPLICATE_SPREAD %s max_abs_hourly_diff=%.6g kWh max_annual_spread_in_group=%.6g kWh (over %d replicate runs, %d inputs)"
             % (t, spread[t][0], spread[t][1], n_ok, len(groups)) for t in cc.TARGETS]
    lines.append("REPLICATE_FILE_CONTENT whole file (without # lines) byte-equal to the original in %d of %d replicate runs" % (n_bytes_equal, n_ok))
    for c, (d, m) in sorted(other.items()):
        if d > 0:
            lines.append("REPLICATE_NONTARGET_DIFF column=%s max_abs_diff=%.3g (column max %.4g)" % (c, d, m))
    if bad:
        return "FAIL", "; ".join(bad[:3]) + " (%d differ)" % len(bad), lines
    if ne:
        return "NOT_EVALUABLE", "; ".join(ne[:3]), lines
    return "PASS", "%d replicate runs in %d groups, dwelling/hour/4 target columns equal to their original; whole-file bytes equal in %d" % (n_ok, len(groups), n_bytes_equal), lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    print("camp_integrity start", cc.now(), "ROOT", cc.ROOT, "HH", cc.HHROOT, "workers", a.workers)
    print("PATCH c10_targets_exact OK (replicate gate = dwelling, hour and 4 target columns; backup camp_integrity.py.v1_2026-09-30)")
    allruns = cc.load_runs()
    full = a.ids is None
    if full:
        runs = allruns
    else:
        want = [ln.strip() for ln in io.open(a.ids, encoding="utf-8") if ln.strip()]
        ix = {r["run_id"]: r for r in allruns}
        runs = [ix[w] for w in want]
    runs_by_id = {r["run_id"]: r for r in runs}
    print("RUNS_IN_SCOPE", len(runs), "full_mode", full)
    results = {c: {} for c, _ in CHECKS}    # check -> run_id -> (status, detail)
    gdata = {}
    if a.workers > 1:
        with mp.Pool(a.workers) as pool:
            it = pool.imap_unordered(check_run, runs, chunksize=8)
            for n, (rid, res, gd) in enumerate(it, 1):
                for c, v in res.items():
                    results[c][rid] = v
                gdata[rid] = gd
                if n % 1000 == 0:
                    print("PROGRESS %d/%d %s" % (n, len(runs), cc.now()), flush=True)
    else:
        for n, run in enumerate(runs, 1):
            rid, res, gd = check_run(run)
            for c, v in res.items():
                results[c][rid] = v
            gdata[rid] = gd
            if n % 1000 == 0:
                print("PROGRESS %d/%d %s" % (n, len(runs), cc.now()), flush=True)
    # ---- C09 group check
    try:
        groups = {}
        missing = []
        for rid, gd in gdata.items():
            if gd["flats"] is None:
                missing.append(rid)
                continue
            plc = gd["placement"]
            for j, sha, _ann in gd["flats"]:
                groups.setdefault(gd["bld"], {}).setdefault(sha, {}).setdefault(plc[j], []).append("%s/dw%d" % (rid, j))
        clash = []
        nflat = 0
        for bld, shas in groups.items():
            for sha, byhid in shas.items():
                nflat += sum(len(v) for v in byhid.values())
                if len(byhid) > 1:
                    clash.append("%s %s households %s" % (bld[0], bld[1], sorted(byhid)))
        print("C09_INFO building-climate groups=%d flats hashed=%d runs without data=%d" % (len(groups), nflat, len(missing)))
        if clash:
            c09 = ("FAIL", "%d identical-series pairs with different households, first: %s" % (len(clash), clash[0]))
        elif missing:
            c09 = ("NOT_EVALUABLE", "%d runs without a readable series" % len(missing))
        else:
            c09 = ("PASS", "%d groups, %d flats, no series shared by two households" % (len(groups), nflat))
    except Exception as e:
        c09 = ("NOT_EVALUABLE", _short(e))
    # ---- C10
    try:
        s10, d10, lines10 = replicate_check(runs_by_id)
        for ln in lines10:
            print(ln)
    except Exception as e:
        s10, d10 = "NOT_EVALUABLE", _short(e)
    # ---- C12
    c12 = None
    if full:
        try:
            bad = []
            ids = [r["run_id"] for r in runs]
            if len(ids) != EXPECTED_TOTAL or len(set(ids)) != EXPECTED_TOTAL:
                bad.append("plan has %d runs (%d unique), expected %d" % (len(ids), len(set(ids)), EXPECTED_TOTAL))
            want_done = set(i + ".json" for i in ids) | set(i + ".err" for i in ids)
            have_done = set(os.listdir(cc.ROOT + "done"))
            if have_done != want_done:
                bad.append("done/ differs: missing %d extra %d (e.g. %s)" % (len(want_done - have_done), len(have_done - want_done), sorted(have_done - want_done)[:2]))
            want_ext = {}
            for r in runs:
                want_ext.setdefault(r["climate_id"], set()).update([r["run_id"] + ".csv.gz", r["run_id"] + ".dwellings.csv"])
            for arr in cc.ARRAYS:
                have = set(os.listdir(cc.ROOT + "extracted/" + arr))
                w = want_ext.get(arr, set())
                if have != w:
                    bad.append("extracted/%s missing %d extra %d (e.g. %s)" % (arr, len(w - have), len(have - w), sorted(have - w)[:2]))
            left = os.listdir(cc.ROOT + "runs")
            if left:
                bad.append("runs/ holds %d folders" % len(left))
            nfail = len(os.listdir(cc.ROOT + "failed"))
            print("C12_INFO failed/ files=%d (tracebacks of crashed runs, informational)" % nfail)
            c12 = ("FAIL", "; ".join(bad)) if bad else ("PASS", "planned=%d done json+err=%d extracted files=%d" % (len(ids), len(have_done), 2 * len(ids)))
        except Exception as e:
            c12 = ("NOT_EVALUABLE", _short(e))
    # ---- report: one line per check
    n_pass = n_fail = n_ne = 0
    for code, name in CHECKS:
        if code == "C09":
            st, det, ev = c09[0], c09[1], len(gdata)
            fails = []
        elif code == "C10":
            st, det, ev = s10, d10, len([r for r in runs if int(r["replicate"]) > 0])
            fails = []
        elif code == "C12":
            if c12 is None:
                print("CHECK C12 %s SKIPPED (subset mode)" % name)
                continue
            st, det, ev = c12[0], c12[1], 1
            fails = []
        else:
            d = results[code]
            ev = len(d)
            fails = [(r, v[1]) for r, v in d.items() if v[0] == "FAIL"]
            nes = [(r, v[1]) for r, v in d.items() if v[0] == "NOT_EVALUABLE"]
            ok = sum(1 for v in d.values() if v[0] == "PASS")
            if ev == 0:
                st, det = "NOT_EVALUABLE", "no run evaluated"
            elif fails:
                st = "FAIL"
                det = "pass=%d fail=%d ne=%d; first: %s %s" % (ok, len(fails), len(nes), fails[0][0], fails[0][1][:200])
            elif nes:
                st = "NOT_EVALUABLE"
                det = "pass=%d fail=0 ne=%d; first: %s %s" % (ok, len(nes), nes[0][0], nes[0][1][:200])
            else:
                st, det = "PASS", "evaluated=%d pass=%d fail=0 ne=0" % (ev, ok)
        print("CHECK %s %s %s %s" % (code, name, st, det))
        if st == "PASS":
            n_pass += 1
        elif st == "FAIL":
            n_fail += 1
        else:
            n_ne += 1
    print("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d" % (n_pass, n_fail, n_ne))
    print("camp_integrity end", cc.now())
    sys.exit(0 if (n_fail == 0 and n_ne == 0) else 1)


if __name__ == "__main__":
    main()
