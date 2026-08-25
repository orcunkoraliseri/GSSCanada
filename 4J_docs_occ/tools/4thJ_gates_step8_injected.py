# -*- coding: utf-8 -*-
"""4J Step 8 --- SCORING THE INJECTED CAMPAIGN (work item 8.5).

Every gate `G8.0`'s control campaign could score is scored again here, on the
injected path, plus the four that only an injected campaign can reach:

    G8.8   scenario differentiation   (8.4 probed it; here it runs on 88 cells)
    G8.9   stale-output guard         (8.4 probed it; here the cache is real)
    G8.12  schedule ingestion         FIRST EVALUATION IN THIS PROJECT
    G8.16  fold correctness           FIRST EVALUATION IN THIS PROJECT

🔴 WHERE EACH SIDE OF A COMPARISON COMES FROM
----------------------------------------------
The val doc's own warning about `G8.12`: *"if it reads the schedule from the
same in-memory object the injector wrote, it is comparing the injector's numbers
against the injector's own reading and cannot fail."*  So:

  * the LEFT side is re-opened from the `in.idf` EnergyPlus actually read --- the
    `OtherEquipment E_PHI_INT` block is located by name, its Schedule Name field
    is resolved to a `Schedule:File` object, and that object's File Name field is
    read off disk;
  * the RIGHT side is rebuilt from the Step 7 artefact on disk at the declared
    `f`, through `4thJ_step8_scenario.multiplier_series` --- the same function
    the campaign used, but starting from the published diary rather than from
    anything the campaign wrote down.

Neither side is a number the transform reported about itself.  `G8.12` has an
ASSIGNMENT arm as well as a value arm, because a transform that re-points
`E_PHI_INT` at a different schedule object leaves no before/after pair to
compare --- in 3J that hid a x3.028 change in DHW draw across all 56 cells while
every value check reported zero violations.

`G8.16` does not trust the cell manifest's own `schedule_fold` field either: the
schedule file is located BY CONTENT (name + md5) among the three Step 7 bundles
on disk, and the fold is read out of the bundle's own `manifest.json`.

🔴 VACUITY IS DECLARED, NEVER PASSED
-------------------------------------
`FINDING 95`.  At `f = 0` the multiplier is identically 1.0 and there is no Step
7 file at all, so `G8.12` and `G8.16` report `NOT_EVALUABLE` on those 88
scenario-cells rather than a pass they did not earn --- and the flat series is
separately asserted to be exactly 1.0 so that "no schedule" cannot hide a wrong
one.

Nothing here may be edited to make a gate pass.  Bands come from
`tools/4thJ_step8_bands.py` (`V8.c`), and `G8.0` governs: a band the untreated
control fails is a band-applicability limitation, not a band to move.

Outputs
-------
  injected_bands.csv        one row per (gate, unit) with value, threshold, verdict
  injected_gate_board.json  the board, the coverage clause and the sweep summary
"""
import csv
import hashlib
import importlib.util as _ilu
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# `--base=DIR` exists so that the injection battery can score a COPY of the
# campaign without ever touching the real artefacts.  It changes where the
# scorer reads from and nothing about what it scores.
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
for _a in sys.argv[1:]:
    if _a.startswith("--base="):
        BASE = os.path.abspath(_a.split("=", 1)[1])

CELLS = os.path.join(BASE, "cells")
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")

CAMPAIGN = os.path.join(BASE, "injected_campaign.json")
RUNS_CSV = os.path.join(BASE, "injected_runs.csv")
AGG_CSV = os.path.join(BASE, "agg_annual.csv")
MONTHLY_CSV = os.path.join(BASE, "injected_monthly.csv")
CACHE_JSON = os.path.join(BASE, "injected_cache.json")
REFERENCE = os.path.join(BASE, "tabula_reference.csv")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
BANDS_CSV = os.path.join(BASE, "injected_bands.csv")
BOARD = os.path.join(BASE, "injected_gate_board.json")


def _load(name, mod):
    spec = _ilu.spec_from_file_location(mod, os.path.join(HERE, name))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


B = _load("4thJ_step8_bands.py", "step8_bands")            # V8.c: ONE source of bands
S = _load("4thJ_step8_scenario.py", "step8_scenario")      # the injector's own maths
G = _load("4thJ_gates_step8_control.py", "step8_gates")    # ONE reader per question

MULT_TOL = 1e-6
MARKER = "outputs_step8"


def rundir(rel):
    """A run directory, resolved against the base being scored.

    `injected_runs.csv` records the path relative to the project root.  The
    battery scores a COPY, so the tail after `outputs_step8/` is what is
    portable --- rebasing here is what lets an injected copy be scored without
    the scorer silently reading the real campaign's files instead.
    """
    rel = rel.replace(os.sep, "/")
    tail = rel.split(MARKER + "/", 1)[-1]
    return os.path.join(BASE, *tail.split("/"))


# --------------------------------------------------------------------------
# reading the IDF EnergyPlus actually read --- case preserved, comments stripped
# per LINE (FINDING 126: an IDF comment belongs to the field BEFORE the comma)
# --------------------------------------------------------------------------

def idf_objects(idf_path):
    txt = io.open(idf_path, encoding="utf-8", errors="replace").read()
    out = []
    for o in txt.split(";"):
        clean = "\n".join(ln.split("!")[0] for ln in o.split("\n"))
        fields = [f.strip() for f in clean.split(",")]
        fields = [f for f in fields] if fields else []
        if fields and fields[0]:
            out.append(fields)
    return out


def phi_schedule_assignment(objs):
    """The Schedule Name `OtherEquipment E_PHI_INT` actually carries."""
    for f in objs:
        if f[0].lower() == "otherequipment" and len(f) > 4 and f[1] == "E_PHI_INT":
            return f[4]
    return None


def schedule_file_objects(objs):
    """{name: full field list} for every Schedule:File in the file."""
    out = {}
    for f in objs:
        if f[0].lower() == "schedule:file" and len(f) > 3:
            out[f[1]] = f
    return out


# --------------------------------------------------------------------------
# 🔴 G8.17 -- THE CAMPAIGN'S HALF OF THE PHASE CHECK. Added 2026-08-26
# under `D-S9-3`(a).
#
# `FINDING 141`: the schedules this campaign consumed were on the DIARY origin
# (04:00) while `Schedule:File` is read from midnight, so 13,108 EnergyPlus runs
# applied occupancy four hours early and every gate on the board passed.
# `G7.19` scores the emitter. `G8.17` scores the CONSUMER, because a correct
# emitter does not stop a campaign being pointed at an old bundle -- and the
# bundles that were wrong are still on disk under `schedules_bak_prerotation`.
#
# Both arms are computed HERE, from the CSV the saved `in.idf` resolves to. The
# manifest's own declaration is checked as a third, separate arm: an artefact
# that is in phase and does not say so cannot be validated, and one that says so
# and is not is worse.
# --------------------------------------------------------------------------
G8_17_NIGHT_HOUR = 5            # same statistic and same band as `G7.19`
G8_17_NIGHT_RATIO_MIN = 0.90
G8_17_MIN_TROUGH_HOUR = 8


def hour_of_day_profile(values):
    """Mean over the year of each hour-of-day index. Hourly series only."""
    prof = [0.0] * 24
    n = [0] * 24
    for i, v in enumerate(values):
        prof[i % 24] += v
        n[i % 24] += 1
    return [p / c if c else 0.0 for p, c in zip(prof, n)]


def phase_verdict(values):
    """(ok, ratio, trough_hour). The statistic `G7.19` registered."""
    prof = hour_of_day_profile(values)
    pmax = max(prof)
    ratio = prof[G8_17_NIGHT_HOUR] / pmax if pmax > 0 else 0.0
    trough = min(range(24), key=lambda k: prof[k])
    return (ratio >= G8_17_NIGHT_RATIO_MIN
            and trough >= G8_17_MIN_TROUGH_HOUR), ratio, trough


def read_multiplier_csv(path):
    with io.open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() != ""]
    return [float(x) for x in lines[1:]]


# --------------------------------------------------------------------------
# locating a Step 7 schedule BY CONTENT, never by a filename convention
# --------------------------------------------------------------------------

def step7_index():
    """{(filename, md5): (bundle_dir, declared_fold)} over every bundle on disk."""
    idx = {}
    folds = {}
    for b in sorted(os.listdir(SCHED7)):
        d = os.path.join(SCHED7, b)
        mp = os.path.join(d, "manifest.json")
        if not os.path.isdir(d) or not os.path.exists(mp):
            continue
        man = json.load(io.open(mp, encoding="utf-8"))
        fold = man.get("fold")
        folds[b] = fold
        for f in os.listdir(d):
            if f.startswith("presence_") and f.endswith(".csv"):
                idx.setdefault(f, []).append((b, fold, S.md5(os.path.join(d, f))))
    return idx, folds


def main():
    quiet = "--quiet" in sys.argv
    for p in (CAMPAIGN, RUNS_CSV, AGG_CSV, MONTHLY_CSV):
        if not os.path.exists(p):
            sys.exit("missing %s -- run tools/4thJ_step8_injected.py first" % p)

    header = json.load(io.open(CAMPAIGN, encoding="utf-8"))
    runs = list(csv.DictReader(io.open(RUNS_CSV, encoding="utf-8")))
    agg = list(csv.DictReader(io.open(AGG_CSV, encoding="utf-8")))
    ref = {r["Code_Building"]: r for r in csv.DictReader(io.open(REFERENCE, encoding="utf-8"))}
    cache = json.load(io.open(CACHE_JSON, encoding="utf-8"))
    s7idx, s7folds = step7_index()
    arch = {os.path.splitext(r["idf"])[0]: r
            for r in csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8"))}

    print("V8.b  scoring tables : %s" % os.path.relpath(AGG_CSV, PROJ))
    print("V8.b  run table      : %s (%d rows)" % (os.path.relpath(RUNS_CSV, PROJ), len(runs)))
    print("V8.c  bands module   : tools/4thJ_step8_bands.py (G8.7 tolerance = %r)"
          % B.G87_TOLERANCE_PCT)

    band_rows = []
    per_gate = {}
    fails = []

    def record(gate, unit, fold, quantity, value, threshold, verdict, reference, note=""):
        band_rows.append({"unit": unit, "fold": fold, "gate": gate, "quantity": quantity,
                          "value": "" if value is None else "%.6f" % value,
                          "threshold": "" if threshold is None else "%.6f" % threshold,
                          "verdict": verdict, "reference": reference, "note": note,
                          "severity": "hard"})
        d = per_gate.setdefault(gate, {})
        d[verdict] = d.get(verdict, 0) + 1
        if verdict == "FAIL":
            fails.append((gate, unit, note or quantity))

    # ---- V8.a : the campaign declares its own size, and it is checked -----
    if header.get("declared_scenario_cells") != len(agg):
        sys.exit("V8.a FAIL: campaign declares %s scenario-cells, agg_annual has %d"
                 % (header.get("declared_scenario_cells"), len(agg)))
    if header.get("declared_runs") != len(runs):
        sys.exit("V8.a FAIL: campaign declares %s runs, injected_runs has %d"
                 % (header.get("declared_runs"), len(runs)))
    print("V8.a  scenario cells : %d declared, %d read -- OK"
          % (header["declared_scenario_cells"], len(agg)))
    print("V8.a  runs           : %d declared, %d read -- OK"
          % (header["declared_runs"], len(runs)))

    _g817_seen = set()
    warn_kind_totals = {}
    suspicious_all = []
    started_seen = {}
    g87 = []

    # ======================================================================
    # per scenario-cell
    # ======================================================================
    for r in agg:
        cell, fold, f = r["cell"], r["fold"], float(r["f"])
        unit = "%s__f%03d" % (cell, int(round(f * 100)))
        sdir = os.path.join(CELLS, unit)
        mp = os.path.join(sdir, "manifest.json")
        if not os.path.exists(mp):
            record("G8.14", unit, fold, "manifest present", None, None, "FAIL",
                   "cells/", "no manifest.json")
            continue
        man = json.load(io.open(mp, encoding="utf-8"))

        # ---- G8.14 manifest completeness, platform measured, not inherited --
        g14_fail = False
        if not man.get("fold"):
            record("G8.14", unit, fold, "fold field present", None, None, "FAIL",
                   "manifest", "V8.g: manifest carries no fold field")
            g14_fail = True
        if man.get("scenario_cell") != unit:
            record("G8.14", unit, fold, "manifest matches directory", None, None,
                   "FAIL", "manifest", "manifest says %r, directory is %r"
                   % (man.get("scenario_cell"), unit))
            g14_fail = True
        missing = [k for k in ("idf_md5_measured", "weather_md5", "energyplus_version",
                               "energyplus_build", "energyplus_exe_md5", "platform",
                               "multiplier_md5", "cache_key")
                   if not man.get(k)]
        if missing:
            record("G8.14", unit, fold, "required manifest fields", None, None, "FAIL",
                   "manifest", "missing: %s" % ",".join(missing))
            g14_fail = True
        if not man.get("platform", {}).get("measured_at_run_time"):
            record("G8.14", unit, fold, "platform measured", None, None, "FAIL",
                   "manifest", "platform not marked measured at run time")
            g14_fail = True
        st = man.get("run", {}).get("started_utc")
        if st in started_seen and started_seen[st] != unit:
            record("G8.14", unit, fold, "run timestamp distinct", None, None, "FAIL",
                   "manifest", "same started_utc as %s -- inherited manifest"
                   % started_seen[st])
            g14_fail = True
        started_seen[st] = unit
        # The injected in.idf carries a Schedule:File the 8.1 archetype does not,
        # so these md5s must DIFFER.  Equal means the injector ran and changed
        # nothing --- the 3J defect, caught on the artefact rather than on a log.
        if man.get("idf_md5_measured") == man.get("idf_md5_source"):
            record("G8.14", unit, fold, "in.idf differs from the source IDF", None, None,
                   "FAIL", "in.idf", "the injected IDF has the same md5 as the "
                                     "un-injected 8.1 archetype: nothing was injected")
            g14_fail = True
        if not g14_fail:
            record("G8.14", unit, fold, "manifest completeness", None, None, "PASS",
                   "manifest", "")

        # ---- engine and warnings, from THIS run's own err --------------------
        errp = os.path.join(sdir, "eplusout.err")
        ver, build, sev, warn, kinds, susp = G.err_scan(errp)
        for k, v in kinds.items():
            warn_kind_totals[k] = warn_kind_totals.get(k, 0) + v
        suspicious_all.extend(("%s: %s" % (unit, s)) for s in susp)
        record("G8.15", unit, fold, "severe errors", float(sev),
               float(B.G815_SEVERE_MAX), "PASS" if sev <= B.G815_SEVERE_MAX else "FAIL",
               "eplusout.err", "%d warning(s)" % warn)
        if ver != man.get("energyplus_version") or build != man.get("energyplus_build"):
            record("G8.14", unit, fold, "engine matches its own err file", None, None,
                   "FAIL", "eplusout.err", "err says %s-%s, manifest says %s-%s"
                   % (ver, build, man.get("energyplus_version"), man.get("energyplus_build")))

        # ---- V8.d geometry from THIS run's own eio --------------------------
        g = G.eio_geometry(os.path.join(sdir, "eplusout.eio"))
        area = g.get("Floor Area {m2}")
        a_ref = float(r["a_ref_m2"])
        n_storey = float(arch[cell]["n_storey"])
        implied = area * n_storey if area else None
        dev = G.pct(implied, a_ref)
        record("V8.d", unit, fold, "a_ref from eio x n_storey vs manifest", dev,
               B.AREA_CONSISTENCY_PCT,
               "PASS" if dev is not None and abs(dev) <= B.AREA_CONSISTENCY_PCT else "FAIL",
               "eplusout.eio", "eio floor %.2f m2 x %g storeys" % (area or -1, n_storey))

        # ---- G8.1 - G8.6 : reproducibility against this cell's own re-run ----
        s1 = os.path.join(sdir, "series_hourly.csv")
        s2 = os.path.join(sdir, "_rerun", "series_hourly.csv")
        if not os.path.exists(s2):
            for gid in ("G8.1", "G8.2", "G8.3", "G8.4", "G8.5", "G8.6"):
                record(gid, unit, fold, "re-run reference", None, None, "NOT_EVALUABLE",
                       "_rerun/", "no independent re-run on disk")
        else:
            h1, t1, m1 = G.read_series(s1)
            h2, t2, m2 = G.read_series(s2)
            if len(h1) != len(h2) or not h1:
                record("G8.2", unit, fold, "series length", float(len(h1)), float(len(h2)),
                       "FAIL", "the re-run", "primary %d h, re-run %d h" % (len(h1), len(h2)))
            else:
                mon1, mon2 = G.monthly_from(h1, m1), G.monthly_from(h2, m2)
                for gid, val, thr, q in (
                        ("G8.1", B.nmbe_pct(mon1, mon2), B.G81_NMBE_MONTHLY_PCT, "NMBE monthly %"),
                        ("G8.2", B.nmbe_pct(h1, h2), B.G82_NMBE_HOURLY_PCT, "NMBE hourly %"),
                        ("G8.3", B.cvrmse_pct(mon1, mon2), B.G83_CVRMSE_MONTHLY_PCT,
                         "CV(RMSE) monthly %"),
                        ("G8.4", B.cvrmse_pct(h1, h2), B.G84_CVRMSE_HOURLY_PCT,
                         "CV(RMSE) hourly %")):
                    ok = val is not None and abs(val) <= thr
                    record(gid, unit, fold, q, val, thr, "PASS" if ok else "FAIL",
                           "independent re-run (D-S8-1 (a))",
                           "reproducibility, not accuracy")
                p1 = max(h1) / 3600.0
                p2 = max(h2) / 3600.0
                d5 = G.pct(p1, p2)
                record("G8.5", unit, fold, "peak magnitude dev %", d5,
                       B.G85_PEAK_MAGNITUDE_PCT,
                       "PASS" if d5 is not None and abs(d5) <= B.G85_PEAK_MAGNITUDE_PCT
                       else "FAIL", "independent re-run (D-S8-5 item 2)",
                       "reproducibility tripwire; the occupancy peak shift is "
                       "REPORTED, not gated")
                i1, i2 = h1.index(max(h1)), h2.index(max(h2))
                record("G8.6", unit, fold, "peak timing |dh|", float(abs(i1 - i2)),
                       float(B.G86_PEAK_TIMING_H),
                       "PASS" if abs(i1 - i2) <= B.G86_PEAK_TIMING_H else "FAIL",
                       "independent re-run (D-S8-5 item 2)",
                       "reproducibility tripwire; the peak SHIFT vs f = 0 is reported")

        # ---- G8.10 end-use closure ------------------------------------------
        uses, total = G.end_uses(os.path.join(sdir, "eplustbl.csv"))
        if uses is None or total is None:
            record("G8.10", unit, fold, "end-use table readable", None, None, "FAIL",
                   "eplustbl.csv", "could not parse the End Uses table")
        else:
            worst, worst_fuel, compared = 0.0, "", []
            for fuel, tot in total.items():
                ssum = sum(u.get(fuel, 0.0) for u in uses.values())
                if tot == 0.0 and ssum == 0.0:
                    continue
                compared.append(fuel)
                d = (100.0 * (ssum - tot) / tot) if tot else 100.0
                if abs(d) > abs(worst):
                    worst, worst_fuel = d, fuel
            if not compared:                                   # FINDING 127
                record("G8.10", unit, fold, "sum(end uses) vs total %", None,
                       B.G810_METER_CLOSURE_PCT, "NOT_EVALUABLE", "eplustbl.csv",
                       "VACUOUS: no fuel carries a non-zero total or sum")
            else:
                record("G8.10", unit, fold, "sum(end uses) vs total %", worst,
                       B.G810_METER_CLOSURE_PCT,
                       "PASS" if abs(worst) <= B.G810_METER_CLOSURE_PCT else "FAIL",
                       "eplustbl.csv", "%d fuel(s) compared (%s); worst %s"
                       % (len(compared), ", ".join(compared), worst_fuel))

        # ---- G8.11 requested vs delivered ------------------------------------
        deliv = man.get("run", {}).get("variables_delivered") or {}
        nmiss = sum(1 for k, v in deliv.items() if not v)
        record("G8.11", unit, fold, "requested variables delivered",
               float(len(deliv) - nmiss), float(len(deliv)),
               "PASS" if deliv and nmiss == 0 else "FAIL", "eplusout.csv header",
               "missing: %s" % (",".join(k for k, v in deliv.items() if not v) or "none"))
        if susp:
            record("G8.11", unit, fold, "'invalid'/'not found' in err", float(len(susp)),
                   0.0, "FAIL", "eplusout.err", susp[0][:110])

        # ---- G8.7 INFO, permanently (D-S8-5 item 1 (a)) ----------------------
        rr = ref.get(r["code"])
        eui = float(r["eui_kwh_m2a_mean"])
        if not rr or not rr["q_h_nd"]:
            record("G8.7", unit, fold, "EUI vs TABULA q_h_nd", None, None, "FAIL",
                   "tabula_reference.csv", "no reference row for %s" % r["code"])
        else:
            q = float(rr["q_h_nd"])
            d = G.pct(eui, q)
            g87.append((fold, unit, f, eui, q, d))
            record("G8.7", unit, fold, "EUI vs TABULA q_h_nd, dev %", d,
                   B.G87_TOLERANCE_PCT, "INFO",
                   "TABULA q_h_nd (as-modelled), INFO by D-S8-5 item 1 (a)",
                   "ours %.2f vs TABULA %.2f kWh/(m2.a) at f = %.2f" % (eui, q, f))

    # ======================================================================
    # per RUN: G8.12, G8.13, G8.16 -- every in.idf on disk, not a sample
    # ======================================================================
    print("")
    print("re-opening every in.idf on disk for G8.12 / G8.13 / G8.16 ...")
    n_idf = 0
    _pres_cache = {}
    _md5_cache = {}

    def presence_of(path):
        if path not in _pres_cache:
            _pres_cache[path] = S.read_presence(path)
            _md5_cache[path] = S.md5(path)
        return _pres_cache[path]
    for row in runs:
        cell, fold, f = row["cell"], row["fold"], float(row["f"])
        unit = "%s__f%03d/%s" % (cell, int(round(f * 100)), row["household"])
        idf = os.path.join(rundir(row["outdir"]), "in.idf")
        if not os.path.exists(idf):
            record("G8.12", unit, fold, "in.idf on disk", None, None, "FAIL",
                   row["outdir"], "the IDF EnergyPlus read is not on disk")
            continue
        n_idf += 1
        objs = idf_objects(idf)

        # ---- G8.13 interpolation, from the file E+ actually read -------------
        bad, can_carry = G.idf_interpolate_violations(idf)
        if can_carry == 0:
            record("G8.13", unit, fold, "objects that can carry Interpolate", 0.0, None,
                   "NOT_EVALUABLE", "in.idf", "no Schedule:File / Day:Interval / Day:List")
        elif bad:
            record("G8.13", unit, fold, "Interpolate to Timestep = Yes", float(len(bad)),
                   0.0, "FAIL", "in.idf", "violations: %s" % ",".join(bad))
        else:
            record("G8.13", unit, fold, "Interpolate to Timestep = Yes", 0.0, 0.0,
                   "PASS", "in.idf", "%d object(s) could have violated, none did"
                   % can_carry)

        # ---- G8.12 ASSIGNMENT arm -------------------------------------------
        assigned = phi_schedule_assignment(objs)
        sfiles = schedule_file_objects(objs)
        if assigned is None:
            record("G8.12", unit, fold, "E_PHI_INT assignment", None, None, "FAIL",
                   "in.idf", "no OtherEquipment named E_PHI_INT")
            continue
        if assigned not in sfiles:
            record("G8.12", unit, fold, "E_PHI_INT points at the injected schedule",
                   None, None, "FAIL", "in.idf",
                   "E_PHI_INT names %r, which is not a Schedule:File in this IDF "
                   "(available: %s)" % (assigned, ",".join(sorted(sfiles)) or "none"))
            continue
        sf = sfiles[assigned]
        csv_path = sf[3]
        if not os.path.exists(csv_path):
            record("G8.12", unit, fold, "schedule file on disk", None, None, "FAIL",
                   "in.idf", "Schedule:File names %r, which does not exist" % csv_path)
            continue
        used = read_multiplier_csv(csv_path)
        if len(used) != S.HOURS:
            record("G8.12", unit, fold, "schedule length", float(len(used)),
                   float(S.HOURS), "FAIL", csv_path, "wrong number of hourly values")
            continue

        # ---- G8.12 VALUE arm, and G8.16, against the Step 7 artefact ---------
        sched_name = row["schedule_file"]
        if f == 0.0 or not sched_name:
            # FINDING 95: declared, not passed.  There IS no Step 7 file at f = 0.
            record("G8.12", unit, fold, "schedule vs the Step 7 artefact", None, None,
                   "NOT_EVALUABLE", "D-S8-2 item 5 (c)",
                   "f = 0 is the control endpoint: the multiplier is identically 1.0 "
                   "and no Step 7 diary is wired in")
            record("G8.16", unit, fold, "fold of the driving schedule", None, None,
                   "NOT_EVALUABLE", "D-S8-2 item 5 (c)",
                   "f = 0 carries no schedule, so there is no fold to mis-drive")
            flat_bad = sum(1 for x in used if abs(x - 1.0) > MULT_TOL)
            record("V8.h", unit, fold, "f = 0 multiplier is exactly 1.0", float(flat_bad),
                   0.0, "PASS" if flat_bad == 0 else "FAIL", csv_path,
                   "the arm that stops 'no schedule' hiding a wrong one")
            continue

        cands = s7idx.get(sched_name, [])
        want_md5 = row["schedule_md5"]
        hit = [(b, fl) for (b, fl, m5) in cands if m5 == want_md5]
        if not hit:
            record("G8.16", unit, fold, "schedule located in a Step 7 bundle", None, None,
                   "FAIL", "Step7_docs/outputs_step7/schedules",
                   "%s with md5 %s is in no bundle on disk" % (sched_name, want_md5[:12]))
            record("G8.12", unit, fold, "schedule vs the Step 7 artefact", None, None,
                   "FAIL", "Step7", "cannot resolve the Step 7 artefact")
            continue
        bundles = sorted({b for b, _fl in hit})
        s7fold = sorted({fl for _b, fl in hit})
        ok16 = len(s7fold) == 1 and s7fold[0] == fold
        record("G8.16", unit, fold, "cells driven by another country's fold",
               0.0 if ok16 else 1.0, 0.0, "PASS" if ok16 else "FAIL",
               "the bundle's own manifest.json, not the filename",
               "bundle(s) %s declare fold %s; the cell is %s"
               % (",".join(bundles), ",".join(s7fold), fold))

        src = os.path.join(SCHED7, bundles[0], sched_name)
        gser = presence_of(src)

        # ---- G8.17: is the schedule this run consumed on the right clock? ----
        bman_path = os.path.join(SCHED7, bundles[0], "manifest.json")
        bman = {}
        if os.path.exists(bman_path):
            bman = json.load(io.open(bman_path, encoding="utf-8"))
        if "rotated_to_midnight" not in bman:
            record("G8.17", unit, fold, "bundle declares its clock", None, None,
                   "FAIL", bman_path,
                   "the Step 7 bundle does not say whether it was rotated to "
                   "midnight. FINDING 141 crossed three steps because no "
                   "artefact recorded which clock it was on.")
        elif not bman.get("rotated_to_midnight"):
            record("G8.17", unit, fold, "bundle declares its clock", None, None,
                   "FAIL", bman_path,
                   "bundle %s declares rotated_to_midnight = false: this run "
                   "applied occupancy on the 04:00 DIARY origin. FINDING 141."
                   % bundles[0])
        else:
            record("G8.17", unit, fold, "bundle declares its clock", None, None,
                   "PASS", bman_path, "rotated_to_midnight = true")
        # 🔴 THE TWO PHASE ARMS ARE SCORED ONCE PER BUNDLE, NOT PER RUN,
        # and that is a specification decision, not a loosened band. Both arms
        # are POPULATION statements: one dwelling that leaves for work together
        # has its occupancy trough at exactly 07:00, and a night-shift dwelling
        # is legitimately empty at 05:00. Each RUN here drives ONE household, so
        # scoring the stock claim per run failed 320 units on CORRECT schedules
        # the first time this gate was executed. `G7.19` had already been
        # corrected for the same error and this module reproduced it -- which is
        # why the counts below are reported and not silently dropped.
        if fold not in _g817_seen:
            _g817_seen.add(fold)
            bdir = os.path.join(SCHED7, bundles[0])
            files = sorted(f for f in os.listdir(bdir)
                           if f.startswith("presence_") and f.endswith(".csv"))
            acc = None
            n_bad_ratio = n_bad_trough = 0
            for fn in files:
                v = presence_of(os.path.join(bdir, fn))
                hp = hour_of_day_profile(v)
                mx = max(hp)
                if mx > 0 and hp[G8_17_NIGHT_HOUR] / mx < G8_17_NIGHT_RATIO_MIN:
                    n_bad_ratio += 1
                if min(range(24), key=lambda k: hp[k]) < G8_17_MIN_TROUGH_HOUR:
                    n_bad_trough += 1
                acc = hp if acc is None else [a + b for a, b in zip(acc, hp)]
            prof = [x / len(files) for x in acc]
            pmax = max(prof)
            ratio17 = prof[G8_17_NIGHT_HOUR] / pmax if pmax > 0 else 0.0
            trough17 = min(range(24), key=lambda k: prof[k])
            note = ("bundle %s, %d dwellings; per-dwelling DIAGNOSTIC, no "
                    "verdict: %d below the night arm, %d below the trough arm"
                    % (bundles[0], len(files), n_bad_ratio, n_bad_trough))
            record("G8.17", "bundle:" + bundles[0], fold,
                   "presence at %02d:00 / daily max" % G8_17_NIGHT_HOUR,
                   ratio17, G8_17_NIGHT_RATIO_MIN,
                   "PASS" if ratio17 >= G8_17_NIGHT_RATIO_MIN else "FAIL", bdir,
                   note)
            record("G8.17", "bundle:" + bundles[0], fold,
                   "hour of the daily occupancy trough",
                   float(trough17), float(G8_17_MIN_TROUGH_HOUR),
                   "PASS" if trough17 >= G8_17_MIN_TROUGH_HOUR else "FAIL", bdir,
                   "a residential trough is the working day, not the small "
                   "hours; measured on the bundle the saved in.idf resolves to")
        want = S.multiplier_series(gser, f)
        worst = max(abs(a - b) for a, b in zip(used, want))
        record("G8.12", unit, fold, "max |m_used - m_rebuilt|", worst, MULT_TOL,
               "PASS" if worst <= MULT_TOL else "FAIL",
               "Step 7 diary on disk, rebuilt through multiplier_series",
               "value arm; %s at f = %.2f" % (sched_name, f))
        record("G8.12", unit, fold, "Step 7 md5 on disk == manifest md5", None, None,
               "PASS" if _md5_cache[src] == want_md5 else "FAIL", src,
               "the val doc's md5 arm")

    print("  %d in.idf re-opened" % n_idf)

    # ======================================================================
    # G8.8 : scenario differentiation, over the whole campaign
    # ======================================================================
    print("")
    by_cell = {}
    for row in runs:
        by_cell.setdefault(row["cell"], []).append(row)
    for cell, rows_c in sorted(by_cell.items()):
        fold = rows_c[0]["fold"]
        f0 = [x for x in rows_c if float(x["f"]) == 0.0]
        d0 = f0[0]["series_sha256"] if f0 else None
        # arm 1: for one household, the five levels of f must all differ
        hhs = sorted({x["household"] for x in rows_c if float(x["f"]) > 0.0})
        for hh in hhs:
            digs = [d0] + [x["series_sha256"] for x in rows_c
                           if x["household"] == hh and float(x["f"]) > 0.0]
            digs = [d for d in digs if d]
            n_uni = len(set(digs))
            record("G8.8", "%s/%s" % (cell, hh), fold, "distinct result digests over f",
                   float(n_uni), float(len(digs)),
                   "PASS" if n_uni == len(digs) else "FAIL", "series_hourly.csv",
                   "%d scenario(s), %d distinct result file(s)" % (len(digs), n_uni))
        # arm 2: at one level of f, two different diaries must not agree either
        for fv in sorted({float(x["f"]) for x in rows_c if float(x["f"]) > 0.0}):
            digs = [x["series_sha256"] for x in rows_c if float(x["f"]) == fv]
            n_uni = len(set(digs))
            record("G8.8", "%s/f%03d" % (cell, int(round(fv * 100))), fold,
                   "distinct result digests over households", float(n_uni),
                   float(len(digs)), "PASS" if n_uni == len(digs) else "FAIL",
                   "series_hourly.csv",
                   "%d diaries, %d distinct result file(s)" % (len(digs), n_uni))

    # ======================================================================
    # G8.9 : the cache key is a function of every input that can change the
    # result -- re-derived from the artefacts on disk, not from the runner
    # ======================================================================
    seen_keys = {}
    n_rederived = 0
    for row in runs:
        unit = "%s/f%s/%s" % (row["cell"], row["f"], row["household"])
        key = row["cache_key"]
        if key in seen_keys and seen_keys[key] != row["outdir"]:
            record("G8.9", unit, row["fold"], "cache key collision", 1.0, 0.0, "FAIL",
                   "injected_runs.csv", "same key as %s" % seen_keys[key])
        seen_keys[key] = row["outdir"]
        idf = os.path.join(rundir(row["outdir"]), "in.idf")
        if not os.path.exists(idf):
            continue
        # ARM 1 --- the IDF the run actually read still hashes to what the key
        # was built from.  If it does not, the directory on disk was produced by
        # a different IDF than the key claims, which is the stale-output defect
        # in its purest form.
        txt = io.open(idf, encoding="utf-8").read()
        got = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        record("G8.9", unit, row["fold"], "in.idf hashes to the key's own input",
               None, None, "PASS" if got == row["injected_idf_sha256"] else "FAIL",
               row["outdir"], "recorded %s, on disk %s"
               % (row["injected_idf_sha256"][:12], got[:12]))

        # ARM 2 --- the key MOVES when any recorded input moves.  A key that
        # ignores an input is what handed 3J a directory produced by a schedule
        # that had since been replaced.
        parts = {"cell": row["cell"], "fold": row["fold"], "f": float(row["f"]),
                 "household": row["household"],
                 "schedule_file": row["schedule_file"] or None,
                 "schedule_md5": row["schedule_md5"] or None,
                 "multiplier_md5": row["multiplier_md5"],
                 "idf_md5": row["idf_md5"],
                 "injected_idf_sha256": row["injected_idf_sha256"],
                 "epw": row["epw"], "epw_md5": row["epw_md5"],
                 "eplus_exe_md5": header["energyplus_exe_md5"]}
        # The dict is passed WHOLE, nulls included, exactly as the runner built
        # it --- dropping a null key would change the canonical JSON and the
        # re-derivation below would fail on every f = 0 row for a reason that has
        # nothing to do with the gate.
        base = S.cache_key(parts)
        watched = [k for k in ("cell", "f", "household", "schedule_md5",
                               "multiplier_md5", "idf_md5", "injected_idf_sha256",
                               "epw_md5", "eplus_exe_md5") if k in parts]
        moved = 0
        for k in watched:
            mut = dict(parts)
            mut[k] = (mut[k] + 0.01) if isinstance(mut[k], float) else "MUTATED"
            if S.cache_key(mut) != base:
                moved += 1
        record("G8.9", unit, row["fold"], "recorded inputs that move the cache key",
               float(moved), float(len(watched)),
               "PASS" if moved == len(watched) else "FAIL",
               "4thJ_step8_scenario.cache_key",
               "watched: %s" % ",".join(watched))
        if base != row["cache_key"]:
            record("G8.9", unit, row["fold"], "key re-derives from the recorded inputs",
                   None, None, "FAIL", "injected_runs.csv",
                   "stored %s, re-derived %s" % (row["cache_key"][:12], base[:12]))
        n_rederived += 1

    n_cached = len(cache)
    record("G8.9", "campaign", "-", "cache index entries vs runs", float(n_cached),
           float(len(runs) + header["declared_reruns"]),
           "PASS" if n_cached == len(runs) + header["declared_reruns"] else "FAIL",
           "injected_cache.json",
           "one key per executed run, re-runs included")

    # ======================================================================
    # the board
    # ======================================================================
    board = {
        "work_item": "8.5",
        "campaign": header["campaign"],
        "scenario_cells": len(agg),
        "runs": len(runs),
        "runs_executed": header.get("runs_executed"),
        "sweep_f": header["sweep_f"],
        "households_per_cell": header["households_per_cell"],
        "household_selection": header["household_selection"],
        "bands_module": "tools/4thJ_step8_bands.py",
        "per_gate": per_gate,
        "fails": [{"gate": g, "unit": c, "note": n} for g, c, n in fails],
        "warning_kinds": warn_kind_totals,
        "suspicious_lines": suspicious_all[:40],
        "n_suspicious": len(suspicious_all),
        "evaluable": dict(B.EVALUABLE_AT_CONTROL),
        "provenance": dict(B.PROVENANCE),
    }

    # ---- the sweep result, which is what this campaign is FOR -------------
    sweep = {}
    for fv in header["sweep_f"]:
        sel = [r for r in agg if abs(float(r["f"]) - fv) < 1e-9]
        by_fold = {}
        for fold in ("es", "uk", "it"):
            s = [r for r in sel if r["fold"] == fold]
            if not s:
                continue
            de = sorted(float(x["d_eui_pct_vs_f0"]) for x in s)
            dp = sorted(float(x["d_peak_pct_vs_f0"]) for x in s)
            dh = sorted(int(x["d_peak_hour_vs_f0"]) for x in s)
            sd = [100.0 * float(x["eui_kwh_m2a_sd"]) / float(x["eui_kwh_m2a_mean"])
                  for x in s if float(x["eui_kwh_m2a_mean"])]
            sdp = [100.0 * float(x["peak_w_m2_sd"]) / float(x["peak_w_m2_mean"])
                   for x in s if float(x["peak_w_m2_mean"])]
            by_fold[fold] = {
                "n_cells": len(s),
                "d_eui_pct_median": de[len(de) // 2],
                "d_eui_pct_min": de[0], "d_eui_pct_max": de[-1],
                "d_peak_pct_median": dp[len(dp) // 2],
                "d_peak_pct_min": dp[0], "d_peak_pct_max": dp[-1],
                "d_peak_hour_median": dh[len(dh) // 2],
                "d_peak_hour_min": dh[0], "d_peak_hour_max": dh[-1],
                "household_sd_eui_pct_mean": (sum(sd) / len(sd)) if sd else None,
                "household_sd_peak_pct_mean": (sum(sdp) / len(sdp)) if sdp else None,
            }
        sweep["f=%.2f" % fv] = by_fold
    board["sweep"] = sweep

    g87s = {}
    for fold in ("es", "uk", "it"):
        for fv in header["sweep_f"]:
            s = sorted(d for (fl, u, ff, e, q, d) in g87
                       if fl == fold and abs(ff - fv) < 1e-9 and d is not None)
            if s:
                g87s.setdefault(fold, {})["f=%.2f" % fv] = {
                    "n": len(s), "median_dev_pct": s[len(s) // 2],
                    "min": s[0], "max": s[-1]}
    board["G8.7_vs_tabula"] = g87s

    # ---- the coverage clause ----------------------------------------------
    ALL_GATES = ["G8.1", "G8.2", "G8.3", "G8.4", "G8.5", "G8.6", "G8.7", "G8.8",
                 "G8.9", "G8.10", "G8.11", "G8.12", "G8.13", "G8.14", "G8.15",
                 "G8.16", "G8.17"]
    cov = {}
    for gid in ALL_GATES:
        d = per_gate.get(gid)
        if not d:
            cov[gid] = "NOT SCORED"
        elif set(d) == {"NOT_EVALUABLE"}:
            cov[gid] = "DECLARED NOT_EVALUABLE on every unit"
        else:
            cov[gid] = "scored: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(d.items()))
    board["coverage_clause"] = cov
    board["coverage_clause_verdict"] = ("PASS" if not any(v == "NOT SCORED"
                                                          for v in cov.values())
                                        else "FAIL")

    with io.open(BANDS_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(band_rows[0].keys()))
        w.writeheader()
        for r in band_rows:
            w.writerow(r)
    with io.open(BOARD, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(board, indent=1, sort_keys=True))

    # ---- print -------------------------------------------------------------
    print("")
    print("%-7s %s" % ("gate", "verdicts"))
    for gid in ALL_GATES:
        d = per_gate.get(gid, {})
        print("%-7s %s" % (gid, ", ".join("%s=%d" % (k, v)
                                          for k, v in sorted(d.items())) or "NOT SCORED"))
    print("%-7s %s" % ("V8.d", ", ".join("%s=%d" % (k, v)
                                         for k, v in sorted(per_gate.get("V8.d", {}).items()))))
    print("%-7s %s" % ("V8.h", ", ".join("%s=%d" % (k, v)
                                         for k, v in sorted(per_gate.get("V8.h", {}).items()))))
    print("")
    print("THE SWEEP --- median over cells, ensemble mean per cell")
    print("%-7s %-4s  %8s %8s   %8s %8s   %6s  %7s"
          % ("f", "fold", "dEUI%", "[min,max]", "dPEAK%", "[min,max]", "dPkH", "hh sd%"))
    for fv in header["sweep_f"]:
        for fold in ("es", "uk", "it"):
            s = sweep["f=%.2f" % fv].get(fold)
            if not s:
                continue
            print("%-7.2f %-4s  %+8.3f [%+.2f,%+.2f]  %+8.3f [%+.2f,%+.2f]  %+6d  %7.3f"
                  % (fv, fold, s["d_eui_pct_median"], s["d_eui_pct_min"], s["d_eui_pct_max"],
                     s["d_peak_pct_median"], s["d_peak_pct_min"], s["d_peak_pct_max"],
                     s["d_peak_hour_median"], s["household_sd_eui_pct_mean"] or 0.0))
    print("")
    print("coverage clause : %s" % board["coverage_clause_verdict"])
    print("bands           : %d rows -> %s" % (len(band_rows),
                                               os.path.relpath(BANDS_CSV, PROJ)))
    if fails:
        print("")
        print("RESULT: %d gate-unit FAILs" % len(fails))
        for g, c, n in fails[:25]:
            print("  %-6s %-30s %s" % (g, c, n))
        sys.exit(1)
    print("")
    print("RESULT: 0 gate-unit FAILs over %d scenario-cells / %d runs"
          % (len(agg), len(runs)))


if __name__ == "__main__":
    main()
