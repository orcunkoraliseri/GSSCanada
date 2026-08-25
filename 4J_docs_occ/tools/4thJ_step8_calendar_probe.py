# -*- coding: utf-8 -*-
"""4J Step 8 --- WHAT THE SCHEDULE/MODEL CALENDAR MISMATCH WAS WORTH.

`V8.i` now refuses a schedule bundle whose calendar year does not start on the
weekday the 8.1 IDFs' `RunPeriod` declares.  It was written because the bundles
the injected campaign first ran on were emitted on the survey years --- `es` 2010,
whose 1 January is a **Friday** --- and wired into a **Sunday**-start RunPeriod, so
every synthetic Saturday landed on a Thursday for fifty-two weeks.  `FINDING 99`
predicted exactly this and nothing was checking it.

A guard that refuses a defect does not say what the defect was WORTH, and
"negligible" is not a thing anyone gets to assume --- `FINDING 120` is this
project's precedent: the weather station was also "just a file name" until it was
measured at 5-11 % of heating demand.  So this tool MEASURES it, on the same code
path, with the guard deliberately bypassed for the misaligned arm and for no
other purpose.

WHAT IS RUN
------------
One archetype per fold (the fold's first cell by sorted name --- a rule, not a
choice), `f = 1.00` (the sweep's upper endpoint, where the schedule has the most
influence, so this is an UPPER bound), and the campaign's own declared ensemble
of diaries.  Two arms per diary: the bundle emitted on the ALIGNED calendar and
the bundle emitted on the survey year.  Everything else --- pool, seed, households,
IDF, EPW, engine --- is identical.

Output
------
  calendar_probe_step8.json
"""
import csv
import importlib.util as _ilu
import io
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
WORK = os.path.join(BASE, "calendar_probe")
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
OUT_JSON = os.path.join(BASE, "calendar_probe_step8.json")

SURVEY_YEAR = {"es": 2010, "uk": 2014, "it": 2013}
F_LEVEL = 1.00


def _load(name, mod):
    spec = _ilu.spec_from_file_location(mod, os.path.join(HERE, name))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SC = _load("4thJ_step8_scenario.py", "step8_scenario")
INJ = _load("4thJ_step8_injected.py", "step8_injected")
C = _load("4thJ_step8_control.py", "step8_control")

J_TO_KWH = 1.0 / 3.6e6


def reduce_one(outdir, a_ref):
    errp = os.path.join(outdir, "eplusout.err")
    sev, warn, fatal, kinds = C.err_counts(errp)
    hourly, temps, months, mvar, present = C.read_series(
        os.path.join(outdir, "eplusout.csv"))
    return {"eui": sum(hourly) * J_TO_KWH / a_ref,
            "peak_w_m2": (max(hourly) / 3600.0) / a_ref,
            "peak_hour": hourly.index(max(hourly)),
            "severe": sev}


def main():
    n_hh = 10
    workers = 10
    for x in sys.argv[1:]:
        if x.startswith("--households="):
            n_hh = int(x.split("=", 1)[1])
        elif x.startswith("--workers="):
            workers = int(x.split("=", 1)[1])

    arch = list(csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8")))
    wx = {r["fold"]: r for r in csv.DictReader(io.open(WX_MANIFEST, encoding="utf-8"))}
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)

    report = {"what": "the schedule/model calendar mismatch, measured",
              "f": F_LEVEL, "households_per_arm": n_hh,
              "guard": "V8.i, deliberately bypassed for the misaligned arm",
              "folds": {}}
    t0 = time.time()
    n_runs = 0
    print("WHAT THE CALENDAR MISMATCH WAS WORTH")
    print("%-4s %-20s %11s %11s %9s   %11s %11s %9s"
          % ("fold", "cell", "EUI aligned", "EUI survey", "d %",
             "PK aligned", "PK survey", "d %"))

    for fold in ("es", "uk", "it"):
        cand = sorted((os.path.splitext(r["idf"])[0], r) for r in arch
                      if r["fold"] == fold)
        if not cand:
            continue
        cell, arec = cand[0]
        a_ref = float(arec["a_ref"])
        epw = os.path.join(WEATHER, wx[fold]["epw"])
        base_idf = io.open(os.path.join(ARCH, arec["idf"]), encoding="utf-8").read()
        want_day = INJ.runperiod_start_day(base_idf)

        arms = {}
        for arm, bundle in (("aligned", "leg5_%s_independent_seed1" % fold),
                            ("survey_year", "leg5_%s_independent_seed1_cal%d"
                             % (fold, SURVEY_YEAR[fold]))):
            bdir = os.path.join(SCHED7, bundle)
            if not os.path.isdir(bdir):
                sys.exit("missing bundle %s -- emit it first" % bdir)
            bman = json.load(io.open(os.path.join(bdir, "manifest.json"),
                                     encoding="utf-8"))
            pres = sorted(f for f in os.listdir(bdir) if f.startswith("presence_"))[:n_hh]
            tasks = []
            sdir = os.path.join(WORK, fold, arm, "_sched")
            os.makedirs(sdir)
            for hh in pres:
                g = SC.read_presence(os.path.join(bdir, hh))
                m = SC.multiplier_series(g, F_LEVEL)
                mcsv = os.path.join(sdir, hh)
                SC.write_multiplier_csv(mcsv, m, "phi_int_multiplier",
                                        decimals=INJ.MULTIPLIER_DECIMALS)
                tasks.append({"hh": hh, "idf": SC.inject(base_idf, mcsv),
                              "dir": os.path.join(WORK, fold, arm,
                                                  hh[:-4])})

            def _go(t):
                r = INJ.run_injected(t["idf"], epw, t["dir"])
                if r["returncode"] != 0:
                    raise RuntimeError("%s rc=%s" % (t["dir"], r["returncode"]))
                t["red"] = reduce_one(t["dir"], a_ref)
                return t

            with ThreadPoolExecutor(max_workers=workers) as ex:
                list(ex.map(_go, tasks))
            n_runs += len(tasks)
            euis = [t["red"]["eui"] for t in tasks]
            pks = [t["red"]["peak_w_m2"] for t in tasks]
            arms[arm] = {
                "bundle": bundle, "schedule_year": bman.get("year"),
                "jan1_weekday": bman.get("year") and
                                __import__("datetime").date(bman["year"], 1, 1)
                                .strftime("%A"),
                "runperiod_start_day": want_day,
                "n": len(tasks),
                "eui_mean": sum(euis) / len(euis),
                "peak_w_m2_mean": sum(pks) / len(pks),
                "peak_hour": [t["red"]["peak_hour"] for t in tasks],
                "severe": sum(t["red"]["severe"] for t in tasks),
            }
            for t in tasks:
                shutil.rmtree(t["dir"], ignore_errors=True)

        al, sv = arms["aligned"], arms["survey_year"]
        de = 100.0 * (sv["eui_mean"] - al["eui_mean"]) / al["eui_mean"]
        dp = 100.0 * (sv["peak_w_m2_mean"] - al["peak_w_m2_mean"]) / al["peak_w_m2_mean"]
        arms["delta_survey_minus_aligned_pct"] = {"eui": de, "peak": dp}
        report["folds"][fold] = dict(arms, cell=cell, code=arec["code"])
        print("%-4s %-20s %11.4f %11.4f %+9.4f   %11.4f %11.4f %+9.4f"
              % (fold, cell, al["eui_mean"], sv["eui_mean"], de,
                 al["peak_w_m2_mean"], sv["peak_w_m2_mean"], dp))

    report["runs"] = n_runs
    report["wall_s"] = round(time.time() - t0, 1)
    with io.open(OUT_JSON, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, indent=1, sort_keys=True))
    shutil.rmtree(WORK, ignore_errors=True)
    print("")
    print("%d runs, %.0f s -> %s" % (n_runs, report["wall_s"],
                                     os.path.relpath(OUT_JSON, PROJ)))


if __name__ == "__main__":
    main()
