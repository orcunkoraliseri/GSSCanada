# -*- coding: utf-8 -*-
"""4J Step 8 WORK ITEM 8.5 --- THE INJECTED CAMPAIGN.  It runs AFTER 8.3 and 8.4.

    "The order of items 8.3 and 8.5 is not a preference.  Reversing it is what
     cost 3J eight campaigns."

WHAT THIS RUNS
---------------
The pre-registered `D-S8-2` item 5 (c) sweep, on every one of the 88 archetype
cells, driven by real Step 7 diaries:

    phi_int(t) = (1 - f) * 3.0  +  f * 3.0 * g(t) / mean_year(g(t))
    f in {0.00, 0.15, 0.30, 0.50, 1.00}

`f = 0` is the control endpoint and its multiplier is identically 1.0, so it does
not depend on which household drives it --- one run per cell.  The four injected
levels do.

🔴 THE FREE PARAMETER THIS CAMPAIGN REFUSES TO CHOOSE
------------------------------------------------------
Nothing anywhere in this project pre-registers WHICH generated household drives
which archetype.  There are 100 diaries per fold and 88 cells, and picking one
diary per cell would put an undeclared free parameter between the schedules and
every number the paper reports --- which is exactly what `FINDING 120` caught on
the weather station, where the choice turned out to be worth 5-11 % of heating
demand.

`FINDING 120`'s precedent is to MEASURE the parameter rather than choose it, so
every cell is driven by a declared ENSEMBLE of `HOUSEHOLDS_PER_CELL` diaries,
taken as the first N by sorted household id from that cell's own fold bundle ---
the same N for every cell in a fold, so a cross-cell comparison holds the diary
set fixed.  What is reported per (cell, f) is the ensemble with its spread, and
the spread IS the measurement of the free parameter.

  * declared campaign size : 88 cells x (1 + 4 x N) runs
  * plus one re-run per (cell, f), on the ensemble's first household, so that
    `G8.1`-`G8.6` have the reference `D-S8-1`(a) requires ON THE INJECTED PATH
    and not only on the control.

WHAT IS MEASURED AT RUN TIME AND NEVER INHERITED
-------------------------------------------------
Same rule as 8.3, and now with a schedule to record: engine version and build
hash out of each run's OWN `eplusout.err`; platform read inside this process;
the executable's md5 in the campaign header; the Step 7 `fold` taken from the
schedule bundle's own `manifest.json` and never from a filename (`G8.16`).

🔴 Timestamps carry microseconds here.  8.3 was serial, so "two cells cannot
have started at the same instant" was a sound inherited-manifest arm; this
campaign is parallel and second-resolution would false-FAIL it.

THE CACHE IS REAL, AND THAT IS THE POINT
-----------------------------------------
`G8.9` was probed in 8.4 against a purpose-built cache.  Here the campaign's own
skip-if-done index is that cache: the key is `4thJ_step8_scenario.cache_key`
over every input that can change the result --- cell, f, household, the Step 7
schedule md5, the multiplier md5, the injected IDF md5, the EPW md5 and the
EnergyPlus executable md5.  Re-invoking this tool re-runs nothing; changing any
one of those inputs re-runs the cells it touches.  The key is deliberately
conservative: a false MISS costs a simulation, a false HIT costs correctness.

WHAT IS DELIBERATELY NOT DONE HERE
-----------------------------------
  * No band is moved, no threshold is defined, and `prereg.md` is not touched.
  * No setback schedule is added.  `F_red_htr` stays the TABULA scalar --- the
    provenance file's §9.5 says that if a real setback and an occupancy-driven
    gains profile are both present the sweep measures two things at once.
  * Nothing under `outputs_step8/control/` or `outputs_step8/probes/` is read
    for its numbers or written to.

Outputs
-------
  sched/<fold>/<hh>__f<NNN>.csv     the multiplier series actually wired in
  cells/<cell>__f<NNN>/             in.idf, eplusout.*, series_hourly.csv,
                                    series_ensemble_mean.csv, manifest.json
  cells/<cell>__f<NNN>/_hh/<hh>/    in.idf + err + end for the other households
  cells/<cell>__f<NNN>/_rerun/      the independent re-run (G8.1-G8.6)
  injected_campaign.json            header + declared counts (V8.a)
  injected_runs.csv                 ONE row per RUN (cell x f x household)
  agg_annual.csv                    ONE row per (cell, f) --- Step 9 consumes it
  injected_monthly.csv              (cell, f) x 12, ensemble mean
"""
import csv
import datetime
import hashlib
import importlib.util as _ilu
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
CELLS = os.path.join(BASE, "cells")
SCHED = os.path.join(BASE, "sched")
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")

IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
CAMPAIGN = os.path.join(BASE, "injected_campaign.json")
RUNS_CSV = os.path.join(BASE, "injected_runs.csv")
AGG_CSV = os.path.join(BASE, "agg_annual.csv")
MONTHLY_CSV = os.path.join(BASE, "injected_monthly.csv")
CACHE_JSON = os.path.join(BASE, "injected_cache.json")

# leg5, not leg4: the Leg-4 records stamp themselves NOT REPORTABLE, and the
# emitter had the leg hard-coded so nothing could reach the Leg-5 pools.
# Emitted on calendar 2017 because the 8.1 IDFs run a Sunday-start RunPeriod ---
# see V8.i, which refuses the pair rather than trusting this comment.
BUNDLE = {"es": "leg5_es_independent_seed1",
          "uk": "leg5_uk_independent_seed1",
          "it": "leg5_it_independent_seed1"}

HOUSEHOLDS_PER_CELL = 10        # the declared ensemble; see the free-parameter note
FLAT_TAG = "flat"               # f = 0 does not depend on a household
# The multiplier is written at 1e-10, not at the module default of 1e-6.  The
# pre-registration says the annual mean of phi_int is EXACTLY 3.0 W/m2 at every
# f; at 1e-6 the file EnergyPlus reads misses that by 4.01e-07 relative, which
# is nothing physically and is still not what the sentence says.  At 1e-10 the
# residue is bounded at 5e-11 by construction.
MULTIPLIER_DECIMALS = 10
J_TO_KWH = 1.0 / 3.6e6

KEEP_FULL = ("in.idf", "eplusout.eio", "eplusout.err", "eplusout.end",
             "eplustbl.csv", "series_hourly.csv", "manifest.json",
             "series_ensemble_mean.csv")
KEEP_LIGHT = ("in.idf", "eplusout.err", "eplusout.end")


def _load(name, mod):
    spec = _ilu.spec_from_file_location(mod, os.path.join(HERE, name))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = _load("4thJ_step8_scenario.py", "step8_scenario")   # 8.4's path, imported not copied
C = _load("4thJ_step8_control.py", "step8_control")     # ONE runner, ONE reader


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def ftag(f):
    return "f%03d" % int(round(f * 100))


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def runperiod_start_day(idf_text):
    """The `Day of Week for Start Day` the IDF itself declares.

    Read from the model, never assumed, because the whole point of `V8.i` is
    that the schedule's calendar and the model's calendar are two different
    things that nothing had ever compared.
    """
    i = idf_text.find("RunPeriod,")
    if i < 0:
        raise ValueError("no RunPeriod object in this IDF")
    blk = idf_text[i:idf_text.find(";", i) + 1]
    fields = []
    for ln in blk.split("\n"):
        for f in ln.split("!")[0].split(","):
            fields.append(f.strip())
    fields = [f for f in fields if f != ""]
    # RunPeriod, Name, bm, bd, by, em, ed, ey, DayOfWeek, ...
    for f in fields:
        if f.capitalize() in ("Sunday", "Monday", "Tuesday", "Wednesday",
                              "Thursday", "Friday", "Saturday"):
            return f.capitalize()
    raise ValueError("RunPeriod names no start day of week")


def assert_calendar_alignment(bman, idf_text, bundle_name):
    """V8.i --- the schedule's weekday pattern must be the model's.

    `FINDING 99` predicted this and nothing was checking it: a bundle emitted on
    a Friday-start year, wired into a Sunday-start RunPeriod, puts every
    synthetic weekend on a Thursday and Friday for fifty-two weeks and leaves no
    trace in the energy.  Both sides are read from artefacts --- the day out of
    the IDF, the year out of the bundle's own manifest.
    """
    year = bman.get("year")
    if not isinstance(year, int):
        raise SystemExit("V8.i: %s declares no schedule year" % bundle_name)
    d0 = datetime.date(year, 1, 1)
    ndays = (datetime.date(year, 12, 31) - d0).days + 1
    want = runperiod_start_day(idf_text)
    got = d0.strftime("%A")
    if ndays != 365:
        raise SystemExit("V8.i: %s was emitted on %d, a %d-day year"
                         % (bundle_name, year, ndays))
    if got != want:
        raise SystemExit(
            "V8.i: %s was emitted on calendar %d, whose 1 January is a %s, and "
            "the IDF's RunPeriod starts on a %s. Every synthetic weekend would "
            "land on the wrong day of the week for the whole year, and the "
            "energy result would look entirely normal (FINDING 99)."
            % (bundle_name, year, got, want))
    return {"schedule_year": year, "runperiod_start_day": want,
            "jan1_weekday": got, "days_in_year": ndays}


# --------------------------------------------------------------------------
# one run
# --------------------------------------------------------------------------

def run_injected(idf_text, epw, outdir, cwd=None):
    """Write the injected IDF as the run's own `in.idf` and run EnergyPlus on it.

    The file EnergyPlus reads is the file the gates read back --- there is no
    second copy anywhere for `G8.12`/`G8.13` to disagree with.

    🔴 The working directory is the RUN's own directory, never a shared one.
    `-r` runs ReadVarsESO, which writes `readvars.audit` into the CURRENT
    directory, so a shared cwd makes parallel runs collide on that one file ---
    EnergyPlus reports it as `** Severe ** remove: ... used by another process`
    and terminates, which would have been read as a model failure.
    """
    cwd = outdir if cwd is None else cwd
    # A representative run's directory is the PARENT of its siblings' (`_hh/`,
    # `_rerun/`), so a blanket rmtree+makedirs races: a sibling creating
    # `<sdir>/_hh/<id>` creates `<sdir>` on the way, and the representative then
    # fails with FileExistsError.  Clear FILES only, and create race-safely.
    os.makedirs(outdir, exist_ok=True)
    for _f in os.listdir(outdir):
        _p = os.path.join(outdir, _f)
        if os.path.isfile(_p):
            os.remove(_p)
    dst = os.path.join(outdir, "in.idf")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(idf_text)
    t0 = time.time()
    started = utcnow()
    p = subprocess.run([C.EPLUS, "-w", epw, "-d", outdir, "-r", dst],
                       cwd=outdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"returncode": p.returncode, "wall_s": round(time.time() - t0, 3),
            "started_utc": started, "finished_utc": utcnow(),
            "stdout_tail": p.stdout.decode("utf-8", "replace")[-400:]}


def canonical_series(hourly, months, temps):
    """The result file, in one canonical form, used both for the digest and on disk.

    `G8.8` compares RESULT files.  Building the digest from this string rather
    than from the file on disk means a run whose directory is later thinned is
    still comparable --- the digest is over the numbers, never over a path or a
    timestamp.
    """
    out = [u"hour,month,heating_j,zone_temp_c"]
    for i, x in enumerate(hourly):
        out.append(u"%d,%s,%.6f,%s" % (i, months[i] if i < len(months) else "",
                                       x, ("%.4f" % temps[i]) if i < len(temps) else ""))
    return u"\n".join(out) + u"\n"


def reduce_run(outdir, a_ref):
    """Everything a result is, read back out of what EnergyPlus wrote."""
    errp = os.path.join(outdir, "eplusout.err")
    ver, build = C.engine_from_err(errp)
    sev, warn, fatal, kinds = C.err_counts(errp)
    ecsv = os.path.join(outdir, "eplusout.csv")
    hourly, temps, months, monthly_var, present = C.read_series(ecsv)
    text = canonical_series(hourly, months, temps)
    with io.open(os.path.join(outdir, "series_hourly.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        fh.write(text)
    mon = [0.0] * 12
    for x, m in zip(hourly, months):
        if 1 <= m <= 12:
            mon[m - 1] += x
    heat_j = sum(hourly)
    peak_w = max(hourly) / 3600.0 if hourly else 0.0
    return {
        "series_sha256": sha256_text(text),
        "n_hours": len(hourly),
        "heating_j": heat_j,
        "eui_kwh_m2a": heat_j * J_TO_KWH / a_ref,
        "peak_w": peak_w,
        "peak_w_m2": peak_w / a_ref,
        "peak_hour": hourly.index(max(hourly)) if hourly else -1,
        "hours_heating_on": sum(1 for x in hourly if x > 0.0),
        "severe": sev, "warnings": warn, "fatal": fatal, "warning_kinds": kinds,
        "eplus_version": ver, "eplus_build": build,
        "monthly_j": mon, "monthly_var_j": monthly_var,
        "variables_delivered": present,
        "hourly": hourly,
    }


def thin(outdir, keep):
    for f in os.listdir(outdir):
        p = os.path.join(outdir, f)
        if os.path.isfile(p) and f not in keep:
            os.remove(p)


# --------------------------------------------------------------------------
# the schedules: one multiplier file per (fold, household, f), named
# deterministically, because the cache key contains the injected IDF's md5 and
# the injected IDF contains this path.  A churning name turns the cache off.
# --------------------------------------------------------------------------

def build_schedules(folds, households, sweep, idf_text_for_calendar=None):
    """Write every multiplier file this campaign will wire in, once."""
    out = {}
    out_meta = {}
    for fold in folds:
        bundle = os.path.join(SCHED7, BUNDLE[fold])
        bman = json.load(io.open(os.path.join(bundle, "manifest.json"), encoding="utf-8"))
        if bman.get("fold") != fold:
            sys.exit("G8.16: bundle %s declares fold %r, expected %r"
                     % (BUNDLE[fold], bman.get("fold"), fold))
        prov = str(bman.get("provenance") or "")
        if "NOT REPORTABLE" in prov.upper():
            sys.exit("bundle %s carries provenance %r. A campaign whose diaries "
                     "declare themselves not reportable cannot report anything."
                     % (BUNDLE[fold], prov))
        if idf_text_for_calendar is not None:
            out_meta[fold] = assert_calendar_alignment(bman, idf_text_for_calendar,
                                                       BUNDLE[fold])
            out_meta[fold]["leg"] = bman.get("leg")
            out_meta[fold]["pool"] = (bman.get("pool") or {}).get("pool_file")
            out_meta[fold]["pool_md5"] = (bman.get("pool") or {}).get("pool_md5")
            out_meta[fold]["pool_n_days"] = (bman.get("pool") or {}).get("n_days")
            out_meta[fold]["backoff_full_depth_share"] = \
                bman.get("backoff_full_depth_share")
        d = os.path.join(SCHED, fold)
        if not os.path.isdir(d):
            os.makedirs(d)
        for hh in households[fold]:
            src = os.path.join(bundle, hh)
            g = S.read_presence(src)
            hh_id = hh[len("presence_"):-len(".csv")]
            for f in sweep:
                if f == 0.0:
                    continue
                m = S.multiplier_series(g, f)
                dst = os.path.join(d, "%s__%s.csv" % (hh_id, ftag(f)))
                S.write_multiplier_csv(dst, m, "phi_int_multiplier",
                                       decimals=MULTIPLIER_DECIMALS)
                out[(fold, hh, f)] = {
                    "hh_id": hh_id, "schedule_file": hh,
                    "schedule_md5": S.md5(src), "schedule_fold": bman["fold"],
                    "schedule_bundle": BUNDLE[fold],
                    "multiplier_csv": dst, "multiplier_md5": S.md5(dst),
                    "multiplier_max": max(m), "multiplier_min": min(m),
                }
        # f = 0: m(t) == 1.0 for every household, so it is written once per fold
        flat = [1.0] * S.HOURS
        dst = os.path.join(d, "%s__%s.csv" % (FLAT_TAG, ftag(0.0)))
        S.write_multiplier_csv(dst, flat, "phi_int_multiplier",
                               decimals=MULTIPLIER_DECIMALS)
        out[(fold, FLAT_TAG, 0.0)] = {
            "hh_id": FLAT_TAG, "schedule_file": None,
            "schedule_md5": None, "schedule_fold": bman["fold"],
            "schedule_bundle": BUNDLE[fold],
            "multiplier_csv": dst, "multiplier_md5": S.md5(dst),
            "multiplier_max": 1.0, "multiplier_min": 1.0,
        }
    return out, out_meta


def main():
    limit = None
    n_hh = HOUSEHOLDS_PER_CELL
    workers = 10
    fresh = "--fresh" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a.startswith("--households="):
            n_hh = int(a.split("=", 1)[1])
        elif a.startswith("--workers="):
            workers = int(a.split("=", 1)[1])
    if not os.path.exists(C.EPLUS):
        sys.exit("EnergyPlus not found at %s" % C.EPLUS)

    arch = list(csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8")))
    wx = {r["fold"]: r for r in csv.DictReader(io.open(WX_MANIFEST, encoding="utf-8"))}
    if len(wx) != 3:
        sys.exit("weather manifest declares %d folds, expected 3" % len(wx))
    if limit:
        arch = arch[:limit]
    folds = sorted({a["fold"] for a in arch})

    households = {}
    for fold in folds:
        bundle = os.path.join(SCHED7, BUNDLE[fold])
        pres = sorted(f for f in os.listdir(bundle) if f.startswith("presence_"))
        if len(pres) < n_hh:
            sys.exit("fold %s has %d diaries, need %d" % (fold, len(pres), n_hh))
        households[fold] = pres[:n_hh]           # declared, deterministic, no cherry-pick

    if fresh:
        for d in (CELLS, SCHED):
            if os.path.isdir(d):
                shutil.rmtree(d)
        if os.path.exists(CACHE_JSON):
            os.remove(CACHE_JSON)
    for d in (CELLS, SCHED):
        if not os.path.isdir(d):
            os.makedirs(d)

    sweep = list(S.SWEEP_F)
    # V8.i needs a model to read the RunPeriod out of; every 8.1 IDF carries the
    # same one, and the first archetype is as good a witness as any.
    _first_idf = io.open(os.path.join(ARCH, arch[0]["idf"]), encoding="utf-8").read()
    scheds, calendar_meta = build_schedules(folds, households, sweep, _first_idf)

    cache = {}
    if os.path.exists(CACHE_JSON):
        cache = json.load(io.open(CACHE_JSON, encoding="utf-8"))

    exe_md5 = S.md5(C.EPLUS)
    plat = {"platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "node": platform.node(),
            "python": platform.python_version(), "cpu_count": os.cpu_count(),
            "measured_at_run_time": True}

    n_runs_declared = len(arch) * (1 + (len(sweep) - 1) * n_hh)
    n_rerun_declared = len(arch) * len(sweep)
    header = {
        "campaign": "step8_injected_sweep",
        "work_item": "8.5",
        "decision_basis": [
            "D-S8-2 item 5 (c): f in {0.00,0.15,0.30,0.50,1.00}, annual mean held at 3.0 W/m2",
            "D-S8-1 (a): G8.1-G8.4 reference = a re-run of the same cell",
            "D-S8-5 item 2: G8.5/G8.6 same re-pointing; the peak SHIFT is reported, not gated",
            "D-S8-4: TMYx.2009-2023, one station per fold",
            "decision 11 / G8.16: a cell's schedules come from the fold that held its country out",
        ],
        "sweep_f": sweep,
        "phi_int_mean_w_m2": S.PHI_INT_MEAN_W_M2,
        "multiplier_decimals": MULTIPLIER_DECIMALS,
        "multiplier_mean_residue_bound": 0.5 * 10.0 ** -MULTIPLIER_DECIMALS,
        "households_per_cell": n_hh,
        "household_selection": ("first %d presence files by sorted household id in the "
                                "cell's own fold bundle; the same %d for every cell in a "
                                "fold" % (n_hh, n_hh)),
        "households": {f: households[f] for f in folds},
        "schedule_bundles": {f: BUNDLE[f] for f in folds},
        "schedule_provenance": calendar_meta,
        "declared_cells": len(arch),
        "declared_scenario_cells": len(arch) * len(sweep),
        "declared_runs": n_runs_declared,
        "declared_reruns": n_rerun_declared,
        "energyplus_exe": C.EPLUS,
        "energyplus_exe_md5": exe_md5,
        "platform": plat,
        "cache": {"key": "sha256 over canonical JSON of every input that can change "
                         "the result", "index": os.path.relpath(CACHE_JSON, PROJ)},
        "started_utc": utcnow(),
    }

    print("WORK ITEM 8.5 --- THE INJECTED CAMPAIGN")
    print("cells       : %d   sweep %s   households/cell %d" % (len(arch), sweep, n_hh))
    print("runs        : %d declared (+ %d re-runs), %d workers"
          % (n_runs_declared, n_rerun_declared, workers))
    print("schedules   : %s" % ", ".join("%s=%s" % (f, BUNDLE[f]) for f in folds))
    print("cache       : %d key(s) on disk" % len(cache))
    print("")

    run_rows, agg_rows, monthly_rows = [], [], []
    hits = misses = 0
    t_start = time.time()

    for n, a in enumerate(arch, 1):
        cell = os.path.splitext(a["idf"])[0]
        fold = a["fold"]
        w = wx[fold]
        epw = os.path.join(WEATHER, w["epw"])
        idf_src = os.path.join(ARCH, a["idf"])
        for p in (epw, idf_src):
            if not os.path.exists(p):
                sys.exit("missing %s" % p)
        a_ref = float(a["a_ref"])
        base_idf = io.open(idf_src, encoding="utf-8").read()
        idf_md5 = S.md5(idf_src)

        # ---- build every scenario-run of this cell, and its cache key -------
        tasks = []
        for f in sweep:
            hhs = [FLAT_TAG] if f == 0.0 else households[fold]
            for hh in hhs:
                sc = scheds[(fold, hh, f)]
                idf_text = S.inject(base_idf, sc["multiplier_csv"])
                parts = {"cell": cell, "fold": fold, "f": f,
                         "household": sc["hh_id"],
                         "schedule_file": sc["schedule_file"],
                         "schedule_md5": sc["schedule_md5"],
                         "multiplier_md5": sc["multiplier_md5"],
                         "idf_md5": idf_md5,
                         "injected_idf_sha256": sha256_text(idf_text),
                         "epw": w["epw"], "epw_md5": w["epw_md5"],
                         "eplus_exe_md5": exe_md5}
                key = S.cache_key(parts)
                sdir = os.path.join(CELLS, "%s__%s" % (cell, ftag(f)))
                rep = (hh == hhs[0])
                outdir = sdir if rep else os.path.join(sdir, "_hh", sc["hh_id"])
                tasks.append({"f": f, "hh": hh, "sc": sc, "idf_text": idf_text,
                              "parts": parts, "key": key, "outdir": outdir,
                              "rep": rep, "sdir": sdir})
        # the re-runs: one per (cell, f), on the ensemble's first household
        for f in sweep:
            t0 = next(t for t in tasks if t["f"] == f and t["rep"])
            tasks.append({"f": f, "hh": t0["hh"], "sc": t0["sc"],
                          "idf_text": t0["idf_text"], "parts": dict(t0["parts"], role="rerun"),
                          "key": S.cache_key(dict(t0["parts"], role="rerun")),
                          "outdir": os.path.join(t0["sdir"], "_rerun"),
                          "rep": False, "sdir": t0["sdir"], "rerun": True})

        todo = []
        for t in tasks:
            c = cache.get(t["key"])
            # A HIT must hand back a REDUCTION, not merely a directory name.  A
            # cache that stores only a path forces the next invocation to
            # re-derive from files this one has already thinned, and the tables
            # come out empty --- a silent version of the very defect `G8.9`
            # exists to catch.
            if c and isinstance(c, dict) and os.path.isdir(
                    os.path.join(PROJ, c["outdir"])):
                t["cache"] = "HIT"
                t["red"] = dict(c["red"], hourly=None)
                t["run"] = c["run"]
                hits += 1
            else:
                t["cache"] = "MISS"
                misses += 1
                todo.append(t)

        def _go(t):
            r = run_injected(t["idf_text"], epw, t["outdir"])
            if r["returncode"] != 0 or not os.path.exists(
                    os.path.join(t["outdir"], "eplusout.err")):
                raise RuntimeError("%s f=%s hh=%s failed rc=%s\n%s"
                                   % (cell, t["f"], t["hh"], r["returncode"],
                                      r["stdout_tail"]))
            t["run"] = r
            t["red"] = reduce_run(t["outdir"], a_ref)
            return t

        if todo:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                list(ex.map(_go, todo))
        for t in todo:
            cache[t["key"]] = {
                "outdir": os.path.relpath(t["outdir"], PROJ).replace("\\", "/"),
                "red": {k: v for k, v in t["red"].items() if k != "hourly"},
                "run": t["run"]}

        # ---- reduce this cell, scenario by scenario -------------------------
        by_f = {}
        for t in tasks:
            if t.get("rerun") or "red" not in t:
                continue
            by_f.setdefault(t["f"], []).append(t)
        reruns = {t["f"]: t for t in tasks if t.get("rerun") and "red" in t}

        f0 = None
        for f in sweep:
            group = sorted(by_f.get(f, []), key=lambda t: t["sc"]["hh_id"])
            if not group:
                continue
            rep = next(t for t in group if t["rep"])
            sdir = rep["sdir"]
            euis = [t["red"]["eui_kwh_m2a"] for t in group]
            peaks = [t["red"]["peak_w_m2"] for t in group]
            phours = [t["red"]["peak_hour"] for t in group]
            nh = len(group)
            mean_eui = sum(euis) / nh
            mean_peak = sum(peaks) / nh
            sd = (lambda v, m: (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5
                  if len(v) > 1 else 0.0)
            # The ensemble mean needs every member's hourly array.  A run the
            # cache handed back has a reduction but no series, so the file that
            # is already on disk stands --- and its absence is an error, never a
            # silently skipped output.
            ens_path = os.path.join(sdir, "series_ensemble_mean.csv")
            if all(t["red"].get("hourly") for t in group):
                ens = [0.0] * S.HOURS
                for t in group:
                    for i, x in enumerate(t["red"]["hourly"]):
                        ens[i] += x / nh
                with io.open(ens_path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(u"hour,heating_j_ensemble_mean\n")
                    for i, x in enumerate(ens):
                        fh.write(u"%d,%.6f\n" % (i, x))
            elif not os.path.exists(ens_path):
                sys.exit("%s: every run came from the cache and the ensemble "
                         "mean series is not on disk" % sdir)
            mon = [0.0] * 12
            for t in group:
                for i in range(12):
                    mon[i] += t["red"]["monthly_j"][i] / nh

            rr = reruns.get(f)
            man = {
                "cell": cell, "scenario_cell": "%s__%s" % (cell, ftag(f)),
                "campaign": "step8_injected_sweep", "work_item": "8.5",
                "fold": fold,                              # V8.g / G8.16
                "code": a["code"], "cls": a["cls"], "cell_period": a["cell_period"],
                "f": f,
                "phi_int_w_m2": S.PHI_INT_MEAN_W_M2,
                "injection": ("Schedule:File on OtherEquipment E_PHI_INT; "
                              "m(t) = (1-f) + f*g(t)/mean(g), annual mean exactly 1.0"),
                "schedule_bundle": rep["sc"]["schedule_bundle"],
                "schedule_fold": rep["sc"]["schedule_fold"],   # from the bundle manifest
                "schedule_file": rep["sc"]["schedule_file"],
                "schedule_md5": rep["sc"]["schedule_md5"],
                "multiplier_csv": os.path.relpath(rep["sc"]["multiplier_csv"],
                                                  PROJ).replace("\\", "/"),
                "multiplier_md5": rep["sc"]["multiplier_md5"],
                "multiplier_max": rep["sc"]["multiplier_max"],
                "household": rep["sc"]["hh_id"],
                "households": [t["sc"]["hh_id"] for t in group],
                "household_schedule_md5": {t["sc"]["hh_id"]: t["sc"]["schedule_md5"]
                                           for t in group},
                "idf": a["idf"], "idf_md5_source": idf_md5,
                "idf_md5_measured": S.md5(os.path.join(sdir, "in.idf")),
                "weather_epw": w["epw"], "weather_md5": w["epw_md5"],
                "weather_base_period": w["base_period"], "weather_station": w["station"],
                "weather_wmo": w["wmo"],
                "energyplus_version": rep["red"]["eplus_version"],
                "energyplus_build": rep["red"]["eplus_build"],
                "energyplus_exe_md5": exe_md5,
                "platform": plat,
                "cache_key": rep["key"],
                "run": dict(rep["run"], severe=rep["red"]["severe"],
                            warnings=rep["red"]["warnings"],
                            warning_kinds=rep["red"]["warning_kinds"],
                            variables_delivered=rep["red"]["variables_delivered"],
                            series_sha256=rep["red"]["series_sha256"]),
                "rerun": (dict(rr["run"], severe=rr["red"]["severe"],
                               warnings=rr["red"]["warnings"],
                               series_sha256=rr["red"]["series_sha256"])
                          if rr else None),
                "ensemble": {
                    "n": nh,
                    "eui_kwh_m2a_mean": mean_eui,
                    "eui_kwh_m2a_sd": sd(euis, mean_eui),
                    "eui_kwh_m2a_min": min(euis), "eui_kwh_m2a_max": max(euis),
                    "peak_w_m2_mean": mean_peak,
                    "peak_w_m2_sd": sd(peaks, mean_peak),
                    "peak_w_m2_min": min(peaks), "peak_w_m2_max": max(peaks),
                    "peak_hour_min": min(phours), "peak_hour_max": max(phours),
                    "series_sha256": {t["sc"]["hh_id"]: t["red"]["series_sha256"]
                                      for t in group},
                    "monthly_j_mean": mon,
                },
                "written_utc": utcnow(),
            }
            with io.open(os.path.join(sdir, "manifest.json"), "w", encoding="utf-8") as fh:
                fh.write(json.dumps(man, indent=1, sort_keys=True))

            thin(sdir, KEEP_FULL)
            for t in group:
                if not t["rep"] and t["cache"] == "MISS":
                    thin(t["outdir"], KEEP_LIGHT)
            if rr and rr["cache"] == "MISS":
                thin(rr["outdir"], ("eplusout.err", "eplusout.end", "series_hourly.csv",
                                    "in.idf"))

            for t in group:
                run_rows.append({
                    "cell": cell, "fold": fold, "cls": a["cls"],
                    "cell_period": a["cell_period"], "f": "%.2f" % f,
                    "household": t["sc"]["hh_id"],
                    "schedule_file": t["sc"]["schedule_file"] or "",
                    "schedule_md5": t["sc"]["schedule_md5"] or "",
                    "multiplier_md5": t["sc"]["multiplier_md5"],
                    "multiplier_max": "%.6f" % t["sc"]["multiplier_max"],
                    "a_ref_m2": a_ref,
                    "idf_md5": idf_md5,
                    "epw": w["epw"], "epw_md5": w["epw_md5"],
                    "injected_idf_sha256": t["parts"]["injected_idf_sha256"],
                    "heating_j": "%.6f" % t["red"]["heating_j"],
                    "eui_kwh_m2a": "%.6f" % t["red"]["eui_kwh_m2a"],
                    "peak_w": "%.6f" % t["red"]["peak_w"],
                    "peak_w_m2": "%.6f" % t["red"]["peak_w_m2"],
                    "peak_hour_index": t["red"]["peak_hour"],
                    "hours_heating_on": t["red"]["hours_heating_on"],
                    "severe": t["red"]["severe"], "warnings": t["red"]["warnings"],
                    "series_sha256": t["red"]["series_sha256"],
                    "cache": t["cache"], "cache_key": t["key"],
                    "outdir": os.path.relpath(t["outdir"], PROJ).replace("\\", "/"),
                    "eplus_version": t["red"]["eplus_version"],
                    "eplus_build": t["red"]["eplus_build"],
                })

            row = {
                "cell": cell, "fold": fold, "cls": a["cls"], "code": a["code"],
                "cell_period": a["cell_period"], "a_ref_m2": a_ref,
                "f": "%.2f" % f, "n_households": nh,
                "eui_kwh_m2a_mean": "%.6f" % mean_eui,
                "eui_kwh_m2a_sd": "%.6f" % sd(euis, mean_eui),
                "eui_kwh_m2a_min": "%.6f" % min(euis),
                "eui_kwh_m2a_max": "%.6f" % max(euis),
                "peak_w_m2_mean": "%.6f" % mean_peak,
                "peak_w_m2_sd": "%.6f" % sd(peaks, mean_peak),
                "peak_w_m2_min": "%.6f" % min(peaks),
                "peak_w_m2_max": "%.6f" % max(peaks),
                "peak_hour_median": sorted(phours)[len(phours) // 2],
                "peak_hour_min": min(phours), "peak_hour_max": max(phours),
                "severe": sum(t["red"]["severe"] for t in group),
                "epw": w["epw"],
            }
            if f == 0.0:
                f0 = row
                row["d_eui_pct_vs_f0"] = "0.000000"
                row["d_peak_pct_vs_f0"] = "0.000000"
                row["d_peak_hour_vs_f0"] = 0
            else:
                e0 = float(f0["eui_kwh_m2a_mean"])
                p0 = float(f0["peak_w_m2_mean"])
                row["d_eui_pct_vs_f0"] = "%.6f" % (100.0 * (mean_eui - e0) / e0 if e0 else 0.0)
                row["d_peak_pct_vs_f0"] = "%.6f" % (100.0 * (mean_peak - p0) / p0 if p0 else 0.0)
                row["d_peak_hour_vs_f0"] = (sorted(phours)[len(phours) // 2]
                                            - f0["peak_hour_median"])
            agg_rows.append(row)
            for i in range(12):
                monthly_rows.append({"cell": cell, "fold": fold, "f": "%.2f" % f,
                                     "month": i + 1,
                                     "heating_j_ensemble_mean": "%.6f" % mon[i]})

        if n % 5 == 0 or n == len(arch):
            el = time.time() - t_start
            print("  %3d/%d  %-22s  %d run(s) this cell  %5.1f s elapsed  eta %5.1f s"
                  % (n, len(arch), cell, len(todo), el, el / n * (len(arch) - n)))

    header["finished_utc"] = utcnow()
    header["wall_s"] = round(time.time() - t_start, 1)
    header["runs_executed"] = misses
    header["runs_cache_hit"] = hits
    header["scenario_cells_written"] = len(agg_rows)
    header["rows_written"] = len(run_rows)
    with io.open(CAMPAIGN, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header, indent=1, sort_keys=True))
    with io.open(CACHE_JSON, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(cache, indent=1, sort_keys=True))

    def dump(path, rows):
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)

    dump(RUNS_CSV, run_rows)
    dump(AGG_CSV, agg_rows)
    dump(MONTHLY_CSV, monthly_rows)

    print("\ncells          : %d declared, %d scenario-cells written"
          % (header["declared_cells"], len(agg_rows)))
    print("runs           : %d executed, %d cache HIT, %d declared"
          % (misses, hits, n_runs_declared + n_rerun_declared))
    print("wall           : %.1f s" % header["wall_s"])
    print("severe         : %d over all runs" % sum(int(r["severe"]) for r in run_rows))
    print("")
    print("f      mean dEUI %    mean dPEAK %    median dPEAK hour   ensemble sd(EUI) %")
    for f in sweep:
        sel = [r for r in agg_rows if r["f"] == "%.2f" % f]
        if not sel:
            continue
        de = sum(float(r["d_eui_pct_vs_f0"]) for r in sel) / len(sel)
        dp = sum(float(r["d_peak_pct_vs_f0"]) for r in sel) / len(sel)
        dh = sorted(r["d_peak_hour_vs_f0"] for r in sel)[len(sel) // 2]
        sdp = [100.0 * float(r["eui_kwh_m2a_sd"]) / float(r["eui_kwh_m2a_mean"])
               for r in sel if float(r["eui_kwh_m2a_mean"])]
        print("%.2f   %+9.4f     %+9.4f        %+4d              %7.4f"
              % (f, de, dp, dh, (sum(sdp) / len(sdp)) if sdp else 0.0))


if __name__ == "__main__":
    main()
