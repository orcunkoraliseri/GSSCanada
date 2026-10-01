# -*- coding: utf-8 -*-
"""5J campaign task: python -u camp_task.py <array> <block>   (one array task = one block of runs)
For each run of PLAN/<array>/block_<n>.csv that is not DONE: build the IDF (build_mz), run EnergyPlus 23.1 in ROOT/runs/<run_id>/
(input named model.idf, never in.idf), extract (same content as mzp_extract.py) into ROOT/extracted/<array>/, check, write
ROOT/done/<run_id>.json; delete the raw run folder ONLY when status is pass.
Ends with: SUMMARY array=.. block=.. planned=.. not_run=.. ran_failed=.. ran_passed=..  skipped_done=..
(planned = not_run + ran_failed + ran_passed; runs already DONE at start are counted in not_run and in skipped_done.)
Exit code: 0 only if ran_failed == 0 and every planned run is either DONE or passed now; 1 otherwise (a crash is never a pass).
"""
import csv, gzip, io, json, os, shutil, subprocess, sys, time, traceback, platform
import pandas as pd
import camp_common as cc


def run_one(run, arr, blk):
    rid = run["run_id"]
    t_start = time.time()
    rd = cc.ROOT + "runs/%s/" % rid
    if os.path.exists(rd):
        shutil.rmtree(rd)
    os.makedirs(rd)
    checks = []
    rec = {"run_id": rid, "array": arr, "block": blk, "status": "fail", "energyplus_version": cc.EP_VERSION,
           "clock_origin": cc.CLOCK_ORIGIN, "host": platform.node(), "start": cc.now()}
    key = cc.cache_key(run)
    rec["cache_key"] = key
    idf, meta, got, bad_area = cc.build_run(run)
    idf_path = rd + "model.idf"
    io.open(idf_path, "w", encoding="utf-8", newline="\n").write(idf)
    json.dump(meta, io.open(rd + "meta.json", "w", encoding="utf-8"), indent=1, default=str)
    rec["idf_md5"] = cc.md5(idf_path)
    epw = cc.epw_path(run["climate_id"])
    rec["epw_md5"] = cc.md5(epw)
    rec["household_md5s"] = cc.hh_md5s(list(cc.parse_placement(run["placement"]).values()), run["country"])
    miss = [p for p in cc.PATCH_NAMES if p not in got]
    checks.append(("patch_lines_present", not miss, "present=%d of %d missing=%s" % (len(got), len(cc.PATCH_NAMES), miss)))
    checks.append(("area_gates", not bad_area, "failures=%s" % bad_area[:3]))
    if rec["epw_md5"] != cc.epw_expected_md5(run["climate_id"]):
        checks.append(("epw_md5", False, "epw md5 %s != climates.csv %s" % (rec["epw_md5"], cc.epw_expected_md5(run["climate_id"]))))
    # ---- EnergyPlus
    out = rd + "eplus_out"
    t0 = time.time()
    use_time = os.path.exists("/usr/bin/time")
    cmd = ([ "/usr/bin/time", "-v", "-o", rd + "time.txt"] if use_time else []) + [cc.EP, "-w", epw, "-d", out, "-x", "-r", idf_path]
    with open(rd + "eplus_stdout.txt", "w") as so:
        rc = subprocess.call(cmd, cwd=rd, stdout=so, stderr=subprocess.STDOUT)
    rec["seconds"] = round(time.time() - t0, 1)
    rec["energyplus_rc"] = rc
    rss = None
    if os.path.exists(rd + "time.txt"):
        for ln in io.open(rd + "time.txt", errors="replace"):
            if "Maximum resident set size" in ln:
                rss = ln.split(":")[-1].strip()
    rec["max_rss_kb"] = rss
    errp = out + "/eplusout.err"
    err_text = io.open(errp, encoding="utf-8", errors="replace").read() if os.path.exists(errp) else ""
    ok_err, why = cc.check_err(err_text) if err_text else (False, ["no eplusout.err"])
    checks.append(("energyplus_completed_and_0_severe", ok_err and rc == 0, "rc=%s %s" % (rc, why)))
    # ---- extract + checks
    ext_dir = cc.ROOT + "extracted/%s/" % arr
    os.makedirs(ext_dir, exist_ok=True)
    gz_tmp = ext_dir + rid + ".csv.gz.tmp"
    dw_tmp = ext_dir + rid + ".dwellings.csv.tmp"
    gz_fin = ext_dir + rid + ".csv.gz"
    dw_fin = ext_dir + rid + ".dwellings.csv"
    csvp = out + "/eplusout.csv"
    if ok_err and os.path.exists(csvp):
        raw = pd.read_csv(csvp)
        cc.extract_run(raw, meta, run, gz_tmp, dw_tmp)
        back = pd.read_csv(gz_tmp, comment="#", compression="gzip")
        s, t = cc.check_rows(back, int(run["n_dwellings"]))
        checks.append(("rows_8760_per_dwelling_per_target", s == "PASS", t))
        tbl = cc.tbl_enduse(out + "/eplustbl.csv")
        s, t = cc.g24_facility(back, tbl)
        checks.append(("facility_annual_eq_hourly_sum", s == "PASS", t))
        s, t = cc.g24_dwelling(back, raw, meta)
        checks.append(("dwelling_annual_eq_zone_columns", s == "PASS", t))
    else:
        checks.append(("extraction", False, "skipped: err file not ok or no eplusout.csv (%s)" % os.path.exists(csvp)))
    ok = all(c[1] for c in checks)
    rec["checks"] = [{"name": n, "ok": bool(o), "detail": d} for n, o, d in checks]
    if ok:
        os.replace(gz_tmp, gz_fin)
        os.replace(dw_tmp, dw_fin)
        rec["extracted"] = {"csv_gz": {"file": arr + "/" + rid + ".csv.gz", "md5": cc.md5(gz_fin), "bytes": os.path.getsize(gz_fin)},
                            "dwellings_csv": {"file": arr + "/" + rid + ".dwellings.csv", "md5": cc.md5(dw_fin), "bytes": os.path.getsize(dw_fin)}}
        os.makedirs(cc.ROOT + "done", exist_ok=True)
        io.open(cc.ROOT + "done/%s.err" % rid, "w", encoding="utf-8").write(err_text)
        rec["status"] = "pass"
    else:
        for p in (gz_tmp, dw_tmp):
            if os.path.exists(p):
                os.remove(p)
        rec["status"] = "fail"
    rec["end"] = cc.now()
    rec["wall_seconds_incl_build_extract"] = round(time.time() - t_start, 1)
    os.makedirs(cc.ROOT + "done", exist_ok=True)
    tmpj = cc.done_json(rid) + ".tmp"
    json.dump(rec, io.open(tmpj, "w", encoding="utf-8"), indent=1)
    os.replace(tmpj, cc.done_json(rid))
    if ok:
        shutil.rmtree(rd)          # raw folder deleted ONLY on pass
    return rec


def main():
    arr, blk = sys.argv[1], int(sys.argv[2])
    print("python", sys.version.split()[0], "pandas", pd.__version__, "host", platform.node(), "start", cc.now())
    print("ROOT", cc.ROOT, "TABLES", cc.TABLES, "HH", cc.HHROOT)
    bp = cc.PLAN + "%s/block_%d.csv" % (arr, blk)
    rows = cc.read_csv(bp)
    planned = len(rows)
    skipped = failed = passed = 0
    os.makedirs(cc.ROOT + "failed", exist_ok=True)
    os.makedirs(cc.ROOT + "done", exist_ok=True)
    for run in rows:
        rid = run["run_id"]
        try:
            assert run["country"] in ("es", "it"), "not a Spain/Italy run"
            key = cc.cache_key(run)
            if cc.is_done(rid, key):
                skipped += 1
                print("RUN %s SKIP already done (pass, same cache key)" % rid)
                continue
            rec = run_one(run, arr, blk)
            if rec["status"] == "pass":
                passed += 1
                print("RUN %s PASS seconds=%s rss_kb=%s" % (rid, rec["seconds"], rec["max_rss_kb"]))
            else:
                failed += 1
                print("RUN %s FAIL %s" % (rid, [c for c in rec["checks"] if not c["ok"]]))
        except Exception:
            failed += 1
            tb = traceback.format_exc()
            io.open(cc.ROOT + "failed/%s.txt" % rid, "w", encoding="utf-8").write(tb)
            rec = {"run_id": rid, "array": arr, "block": blk, "status": "fail", "crash": tb[-2000:], "end": cc.now()}
            try:
                json.dump(rec, io.open(cc.done_json(rid), "w", encoding="utf-8"), indent=1)
            except Exception:
                pass
            print("RUN %s CRASH (counted ran_failed, traceback in failed/%s.txt): %s" % (rid, rid, tb.strip().splitlines()[-1]))
        sys.stdout.flush()
    not_run = planned - failed - passed
    print("SUMMARY array=%s block=%d planned=%d not_run=%d ran_failed=%d ran_passed=%d skipped_done=%d"
          % (arr, blk, planned, not_run, failed, passed, skipped))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
