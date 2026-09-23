"""V3c task runner -- one row of tasks_v3c.csv -> one EnergyPlus cell (sbatch array task on Speed).
STANDALONE: does not import or edit v3_task.py, so V3b's still-pending jobs (1342426/1342427) are
never touched. Only arm F (the fairer code-schedule control, v3c_build_F.py).

    python v3c_task.py <tasks_v3c.csv> <task_id> <runs_root>

Writes <runs_root>/V3c/<label>/ : manifest.json, hourly_meters.csv, channel_hourly.csv, dhw*.csv,
injected_resized.idf, build_F.json, run/eplusout.{sql,err,end,eio}, run/eplustbl.htm (other E+
outputs deleted after a successful post-process; sql kept for the Step-8E aggregator). A task whose
manifest says status=ok is skipped (resubmit-safe).
"""
import csv
import datetime as dt
import json
import os
import shutil
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_lib as L          # noqa: E402
import v3c_build_F as FB    # noqa: E402


def row_for(tasks_csv, tid):
    with open(tasks_csv) as f:
        for r in csv.DictReader(f):
            if int(r["task_id"]) == tid:
                return r
    raise SystemExit("REFUSING: task_id %d not in %s" % (tid, tasks_csv))


def label_of(r):
    return "F__%s__%s__%s" % (r["scenario"], r["building"], r["city"])


def main():
    tasks_csv, tid, runs_root = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    r = row_for(tasks_csv, tid)
    if r["arm"] != "F":
        raise SystemExit("REFUSING: v3c_task.py only runs arm F, got %r" % r["arm"])
    scen, b, c = r["scenario"], r["building"], r["city"]
    smoke = int(r["smoke_days"] or 0)
    outdir = os.path.join(runs_root, "V3c", label_of(r))
    mpath = os.path.join(outdir, "manifest.json")
    if os.path.isfile(mpath):
        try:
            if json.load(open(mpath)).get("status") == "ok":
                print("[skip] already ok:", outdir)
                return 0
        except Exception:
            pass
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    man = {"task": r, "label": label_of(r), "outdir": outdir,
           "host": os.uname().nodename if hasattr(os, "uname") else "",
           "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_array": "%s_%s" % (
               os.environ.get("SLURM_ARRAY_JOB_ID"), os.environ.get("SLURM_ARRAY_TASK_ID")),
           "PLATFORM": sys.platform, "python": sys.version.split()[0],
           "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "running",
           "cell_tag": L.cell_tag(scen, b, c), "scenario": scen, "building": b, "city": c,
           "cz": L.CITIES[c]["cz"], "expected_rows": (smoke * 24) if smoke else 8760}
    json.dump(man, open(mpath, "w"), indent=2, default=str)
    T = L.Tools()   # needed only for postprocess()'s tools.probe._do_postprocess
    man["code_md5"] = T.code_md5
    man["code_md5"].update({"v3c_task.py": L.md5_file(__file__), "v3c_build_F.py": L.md5_file(FB.__file__)})
    work = os.path.join(outdir, "build")
    os.makedirs(work, exist_ok=True)
    frozen_u = L.frozen_idf("Default_NECB", b, c)
    try:
        idf = os.path.join(work, "injected_resized.idf")
        man["build_F"] = FB.build(frozen_u, idf)
        man["frozen_idf_md5"] = L.md5_file(frozen_u)
        if smoke:
            L.set_runperiod_days(idf, smoke)
        man["final_idf_md5"] = L.md5_file(idf)
        run_dir = os.path.join(outdir, "run")
        rc, ver = L.run_eplus(idf, L.epw_path(c), run_dir, work)
        man["ep_return_code"], man["energyplus_version_raw"] = rc, ver
        man["epw_md5"] = L.md5_file(L.epw_path(c))
        man["err"] = L.err_summary(run_dir)
        rows_h, rows_c = L.postprocess(T, run_dir, idf, outdir, man)
        ok = (rc == 0 and rows_h == man["expected_rows"] and rows_c == man["expected_rows"]
              and all(v.get("closed", False) for g in ("fuel_closure", "channel_closure")
                      for v in (man.get(g) or {}).values() if isinstance(v, dict)))
        man["status"] = "ok" if ok else "fail"
        if ok:
            man["run_bytes_freed"] = L.cleanup_run(run_dir)
            shutil.move(idf, os.path.join(outdir, "injected_resized.idf"))
            man["final_idf_path"] = os.path.join(outdir, "injected_resized.idf")
            shutil.rmtree(work, ignore_errors=True)
    except SystemExit as e:
        man["status"], man["error"] = "fail", str(e)
        print("[FAIL]", e)
    except Exception as e:
        man["status"], man["error"] = "fail", repr(e)
        man["traceback"] = traceback.format_exc()
        traceback.print_exc()
    man["seconds"] = round(time.time() - t0, 1)
    man["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    json.dump(man, open(mpath, "w"), indent=2, default=str)
    print("[done] %s status=%s %.0fs" % (label_of(r), man["status"], man["seconds"]))
    return 0 if man["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
