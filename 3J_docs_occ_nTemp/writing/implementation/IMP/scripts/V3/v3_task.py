"""V3 task runner -- one row of a task table -> one EnergyPlus cell (sbatch array task on Speed).

    python v3_task.py <tasks.csv> <task_id> <runs_root>

Arms (column `arm`):
  U   frozen Default_NECB injected_resized.idf, byte copy                (V3b, uninjected control)
  U2  same as U, second independent run                                  (V3b, same-platform noise floor)
  R   U edited by hand-rule to the injection contract (v3_build_R.py)    (V3b reference)
  N   NECB code schedules sent through the injector chain                (V3b test)
  X   N with the office weekday schedule rolled +3 h                     (V3b negative control)
  S   P10R-arm products of `scenario`, residential draw seed=`seed`, standby floor ON (V3a seed replicate;
      switched from the frozen arm 2026-09-25, backup v3_task.py.pre_P10R_2026-09-25.bak)
Column `smoke_days` > 0 truncates the RunPeriod (smoke only).

Writes <runs_root>/<track>/<label>/ : manifest.json, hourly_meters.csv, channel_hourly.csv,
dhw_hourly.csv, dhw_volume_hourly.csv, static_*.txt, injected_resized.idf, run/eplusout.{sql,err,
end,eio}, run/eplustbl.htm (other E+ outputs deleted after a successful post-process; the SQL is
kept because the Step-8E aggregator reads it). A task whose manifest says status=ok is skipped
(resubmit-safe).
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
import v3_lib as L        # noqa: E402
import v3_static as S     # noqa: E402
import v3_build_R as RB   # noqa: E402

RES_K = 2


def row_for(tasks_csv, tid):
    with open(tasks_csv) as f:
        for r in csv.DictReader(f):
            if int(r["task_id"]) == tid:
                return r
    raise SystemExit("REFUSING: task_id %d not in %s" % (tid, tasks_csv))


def label_of(r):
    return "%s__%s__%s__%s__s%s%s" % (r["arm"], r["scenario"], r["building"], r["city"], r["seed"],
                                     ("__smoke%s" % r["smoke_days"]) if int(r["smoke_days"] or 0) else "")


def main():
    tasks_csv, tid, runs_root = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    r = row_for(tasks_csv, tid)
    arm, scen, b, c = r["arm"], r["scenario"], r["building"], r["city"]
    seed, smoke = int(r["seed"]), int(r["smoke_days"] or 0)
    outdir = os.path.join(runs_root, r["track"], label_of(r))
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
    man = {"task": r, "label": label_of(r), "outdir": outdir, "host": os.uname().nodename if hasattr(os, "uname") else "",
           "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_array": "%s_%s" % (
               os.environ.get("SLURM_ARRAY_JOB_ID"), os.environ.get("SLURM_ARRAY_TASK_ID")),
           "PLATFORM": sys.platform, "python": sys.version.split()[0],
           "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "running",
           "cell_tag": L.cell_tag(scen, b, c), "scenario": scen, "building": b, "city": c,
           "cz": L.CITIES[c]["cz"], "expected_rows": (smoke * 24) if smoke else 8760}
    json.dump(man, open(mpath, "w"), indent=2, default=str)
    T = L.Tools()
    man["code_md5"] = T.code_md5
    man["code_md5"].update({"v3_task.py": L.md5_file(__file__),
                            "v3_static.py": L.md5_file(S.__file__),
                            "v3_build_R.py": L.md5_file(RB.__file__)})
    work = os.path.join(outdir, "build")
    os.makedirs(work, exist_ok=True)
    frozen_u = L.frozen_idf("Default_NECB", b, c)
    try:
        if arm in ("U", "U2"):
            idf = os.path.join(work, "injected_resized.idf")
            shutil.copyfile(frozen_u, idf)
            man["frozen_idf_md5"] = L.md5_file(frozen_u)
            if smoke:
                L.set_runperiod_days(idf, smoke)
        elif arm == "R":
            idf = os.path.join(work, "injected_resized.idf")
            man["build_R"] = RB.build(frozen_u, idf, RES_K)
            if smoke:
                L.set_runperiod_days(idf, smoke)
        elif arm in ("N", "X"):
            chans = L.fixture_channels(c, negative=(arm == "X"))
            man["channels"] = {k: dict(v, csv_md5=L.md5_file(v["csv"])) for k, v in chans.items()}
            idf, info = L.build_injected(T, b, c, chans, "V3%s__%s__%s" % (arm, b, c), work, smoke)
            man["build"] = info
            rref = os.path.join(work, "R_reference.idf")
            man["build_R"] = RB.build(frozen_u, rref, RES_K)
            st = S.compare(idf, rref)
            man["static_vs_R"] = {k: v for k, v in st.items() if k != "report"}
            open(os.path.join(outdir, "static_vs_R.txt"), "w").write(st["report"])
            os.remove(rref)
        elif arm == "S":
            chans = L.product_channels(scen, c, seed)
            man["channels"] = {k: dict(v, csv_md5=L.md5_file(v["csv"])) for k, v in chans.items()}
            # P10R patch (2026-09-25): P10R wiring (standby floor ON) and P10R cell as the static reference
            print("[patch P10R] v3_task arm S: standby_floor=%s, reference=P10R" % L.P10R_STANDBY_FLOOR)
            idf, info = L.build_injected(T, b, c, chans, L.cell_tag(scen, b, c), work, smoke,
                                         standby_floor=L.P10R_STANDBY_FLOOR)
            man["build"] = info
            man["P10R_PATCH"] = {"products_dir": L.S7O, "standby_floor": L.P10R_STANDBY_FLOOR,
                                 "reference_campaign": L.P10R_CAMPAIGN}
            fz = L.p10r_idf(scen, b, c)
            man["reference_idf_md5"] = L.md5_file(fz)
            st = S.compare(idf, fz)
            man["static_vs_P10R"] = {k: v for k, v in st.items() if k != "report"}
            open(os.path.join(outdir, "static_vs_P10R.txt"), "w").write(st["report"])
        else:
            raise SystemExit("REFUSING: unknown arm %r" % arm)
        man["final_idf_md5"] = L.md5_file(idf)
        man["final_idf_static_digest"] = S.digest(idf)
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
            # the final IDF sits beside the CSVs, where the Step-8E aggregator looks for it
            # (--idf-name injected_resized.idf); intermediates are dropped
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
