# -*- coding: utf-8 -*-
"""4J Step 8 item 8.5 --- the gate on the INJECTED campaign.

Two halves, and the second is the one that matters.

HALF C --- structural checks on the artefacts, all re-read from disk.
HALF I --- the injection battery.  A gate that has never been seen refusing is
           not evidence.  Every gate the scorer marks PASS is put in front of a
           defect built to fell it, on a COPY of the campaign, and the run is
           only trusted if the pristine copy scores clean first.

           🔴 Coverage clause (val doc): cross-tab every perturbation against
           the baseline and FAIL the probe if any PASSing gate was never made to
           fall.  This file prints that cross-tab and refuses on a no-op.

🔴 THE COPY IS A SUBSET, AND THAT IS DECLARED
----------------------------------------------
The injected campaign is 88 cells x 5 scenarios x 10 diaries and several hundred
megabytes.  Copying it twice per injection is not a thing that can be done, so
the battery stages a SUBSET --- one cell per fold, every level of `f`, every
diary --- and rewrites the copy's declared counts to match.  Every gate the real
campaign scores is present in the subset, which is what the coverage clause
checks; nothing is scored on the subset that is quoted as a campaign result.
"""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
CELLS = os.path.join(BASE, "cells")
CONTROL = os.path.join(BASE, "control")
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")
SCORER = os.path.join(HERE, "4thJ_gates_step8_injected.py")
PY = sys.executable

CAMPAIGN = os.path.join(BASE, "injected_campaign.json")
RUNS = os.path.join(BASE, "injected_runs.csv")
AGG = os.path.join(BASE, "agg_annual.csv")
MONTHLY = os.path.join(BASE, "injected_monthly.csv")
CACHE = os.path.join(BASE, "injected_cache.json")
BANDS = os.path.join(BASE, "injected_bands.csv")
BOARD = os.path.join(BASE, "injected_gate_board.json")
REFERENCE = os.path.join(BASE, "tabula_reference.csv")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
PREREG = os.path.join(PROJ, "Step6_docs", "outputs_step6", "prereg.md")
PREREG_MD5 = "e4243e07cdd80c9c846b91f40e3e8c45"

ok = 0
bad = []


def chk(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
        print("  ok    %-50s %s" % (name, detail))
    else:
        bad.append(name)
        print("  FAIL  %-50s %s" % (name, detail))


def load_csv(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def ftag(f):
    return "f%03d" % int(round(float(f) * 100))


def series_values(path):
    return [float(r["heating_j"]) for r in csv.DictReader(io.open(path, encoding="utf-8"))]


# =========================================================================
# HALF C --- the artefacts
# =========================================================================
print("HALF C --- the injected campaign on disk")

for p in (CAMPAIGN, RUNS, AGG, MONTHLY, CACHE, BANDS, BOARD, REFERENCE):
    chk("C0 exists: %s" % os.path.basename(p),
        os.path.exists(p) and os.path.getsize(p) > 0)
if bad:
    sys.exit("artefacts missing -- run the campaign and the scorer first")

header = json.load(io.open(CAMPAIGN, encoding="utf-8"))
runs = load_csv(RUNS)
agg = load_csv(AGG)
brows = load_csv(BANDS)
board = json.load(io.open(BOARD, encoding="utf-8"))
cache = json.load(io.open(CACHE, encoding="utf-8"))
arch = load_csv(IDF_MANIFEST)
wx = {r["fold"]: r for r in load_csv(WX_MANIFEST)}
SWEEP = header["sweep_f"]
NHH = header["households_per_cell"]

# C1 --- the pre-registered grid, and nothing else
chk("C1 sweep == the D-S8-2 (c) pre-registered grid",
    [round(x, 2) for x in SWEEP] == [0.00, 0.15, 0.30, 0.50, 1.00],
    "f = %s" % SWEEP)

# C2 --- one scenario-cell per (archetype, f), and the campaign declares it
chk("C2 one row per (archetype, f)",
    len(agg) == len(arch) * len(SWEEP)
    and len({(r["cell"], r["f"]) for r in agg}) == len(agg),
    "%d rows for %d archetypes x %d levels" % (len(agg), len(arch), len(SWEEP)))
chk("C3 declared == written == table",
    header["declared_scenario_cells"] == board["scenario_cells"] == len(agg)
    and header["declared_runs"] == len(runs),
    "declared %s cells / %s runs" % (header["declared_scenario_cells"],
                                     header["declared_runs"]))

# C4 --- f = 0 is ONE run per cell, every other level is the full ensemble
counts = {}
for r in runs:
    counts.setdefault((r["cell"], r["f"]), 0)
    counts[(r["cell"], r["f"])] += 1
bad_n = [k for k, v in counts.items()
         if v != (1 if float(k[1]) == 0.0 else NHH)]
chk("C4 f = 0 is one run per cell, f > 0 is the full ensemble", not bad_n,
    "%d scenario-cell(s) with the wrong run count" % len(bad_n))

# C5 --- V8.g: the fold field EXISTS in every manifest and is the right one
foldbad, phibad = [], []
for r in agg:
    unit = "%s__%s" % (r["cell"], ftag(r["f"]))
    m = json.load(io.open(os.path.join(CELLS, unit, "manifest.json"), encoding="utf-8"))
    if not m.get("fold") or m["fold"] != r["fold"]:
        foldbad.append(unit)
    if m.get("phi_int_w_m2") != 3.0 or abs(m.get("f", -1) - float(r["f"])) > 1e-9:
        phibad.append(unit)
chk("C5 V8.g explicit fold field in every manifest", not foldbad,
    "%d bad" % len(foldbad))
chk("C6 every manifest declares phi_int = 3.0 and its own f", not phibad,
    "%d bad" % len(phibad))

# C7 --- every cell ran its own fold's D-S8-4 EPW, by md5
wrong = [r["cell"] for r in runs
         if r["epw"] != wx[r["fold"]]["epw"] or r["epw_md5"] != wx[r["fold"]]["epw_md5"]]
chk("C7 every run used its own fold's D-S8-4 EPW", not wrong, "%d wrong" % len(wrong))

# C8 --- 8760 hourly values everywhere a series exists
lens = set()
for r in agg[:6] + agg[-6:]:
    unit = "%s__%s" % (r["cell"], ftag(r["f"]))
    for p in (os.path.join(CELLS, unit, "series_hourly.csv"),
              os.path.join(CELLS, unit, "_rerun", "series_hourly.csv"),
              os.path.join(CELLS, unit, "series_ensemble_mean.csv")):
        lens.add(sum(1 for _ in io.open(p, encoding="utf-8")) - 1)
chk("C8 8760 hourly values in run, re-run and ensemble mean", lens == {8760},
    "lengths %s" % sorted(lens))

# C9 --- 🔴 the pre-registration's OWN claim, re-derived from the CSVs on disk:
# the annual mean of the multiplier is exactly 1.0 at every f, so phi_int's
# annual mean never leaves 3.0 W/m2 and the sweep only REDISTRIBUTES.
SCHEDDIR = os.path.join(BASE, "sched")
seen_paths = {}
for fold in sorted(os.listdir(SCHEDDIR)):
    d = os.path.join(SCHEDDIR, fold)
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".csv"):
            p = os.path.join(d, fn)
            seen_paths[md5(p)] = p
missing = sorted({r["multiplier_md5"] for r in runs} - set(seen_paths))
chk("C9b every multiplier a run used is on disk under sched/", not missing,
    "%d md5(s) with no file" % len(missing))
worst_mean, worst_max = 0.0, 0.0
for md5v, p in seen_paths.items():
    vals = [float(x) for x in io.open(p, encoding="utf-8").read().split("\n")[1:] if x.strip()]
    worst_mean = max(worst_mean, abs(sum(vals) / len(vals) - 1.0))
    worst_max = max(worst_max, max(vals))
# The bound is DERIVED from the precision the campaign declares it wrote at,
# never fitted to the residue that came out.  Half a unit in the last place is
# the most a rounded value can move, so it is the most the mean can move.
DEC = header.get("multiplier_decimals")
BOUND = header.get("multiplier_mean_residue_bound")
chk("C9a the campaign declares the precision it wrote the multiplier at",
    isinstance(DEC, int) and BOUND == 0.5 * 10.0 ** -DEC,
    "%s decimals, residue bound %.1e" % (DEC, BOUND or -1))
chk("C9 every multiplier's annual mean is 1.0 within its own write precision",
    BOUND is not None and worst_mean <= BOUND,
    "%d file(s), worst |mean - 1| = %.3g against %.1e"
    % (len(seen_paths), worst_mean, BOUND or -1))
chk("C10 the multiplier exceeds 1.0 -- ScheduleTypeLimits Frac would have clipped",
    worst_max > 1.0, "max multiplier %.4f, PhiMult upper limit 100.0" % worst_max)

# C11 --- 🔴 f = 0 reproduces the 8.3 uninjected control, value for value.
# `D-S8-2` item 5 (c)'s whole point: the control is an ENDPOINT of the sweep,
# not a second model.  8.4 measured it on one cell; this measures it on 88.
drift, checked = [], 0
for a in arch:
    cell = os.path.splitext(a["idf"])[0]
    p1 = os.path.join(CELLS, "%s__f000" % cell, "series_hourly.csv")
    p2 = os.path.join(CONTROL, cell, "series_hourly.csv")
    if not (os.path.exists(p1) and os.path.exists(p2)):
        continue
    checked += 1
    if series_values(p1) != series_values(p2):
        drift.append(cell)
chk("C11 f = 0 reproduces the 8.3 control on every cell", not drift and checked,
    "%d cell(s) compared, %d drifted" % (checked, len(drift)))

# C12 --- the diaries are the declared ensemble, and no cell borrows another fold's
hh_by_fold = {}
for r in runs:
    if float(r["f"]) > 0.0:
        hh_by_fold.setdefault(r["fold"], set()).add(r["schedule_file"])
decl = {f: set(v) for f, v in header["households"].items()}
chk("C12 every cell used exactly the declared ensemble",
    hh_by_fold == decl,
    "%s" % {f: len(v) for f, v in sorted(hh_by_fold.items())})
cross = []
for f, names in hh_by_fold.items():
    bundle = os.path.join(SCHED7, "leg4_%s_independent_seed1" % f)
    for nme in names:
        if not os.path.exists(os.path.join(bundle, nme)):
            cross.append((f, nme))
chk("C13 every diary lives in its own fold's Step 7 bundle", not cross,
    "%d borrowed" % len(cross))

# C14 --- V8.e: every band row is a hard severity, re-read from the artefact
sev = {r["severity"] for r in brows}
chk("C14 V8.e every band row severity == hard", sev == {"hard"}, "severities %s" % sorted(sev))

# C15 --- V8.c: one bands module, and G8.7 still has no number
bandsrc = io.open(os.path.join(HERE, "4thJ_step8_bands.py"), encoding="utf-8").read()
chk("C15 G8.7 carries no numeric band (D-S8-5 item 1 (a))",
    "G87_TOLERANCE_PCT = None" in bandsrc, "permanent by ruling")

# C16 --- the 88 archetype IDFs are unchanged on disk
adrift = [a["idf"] for a in arch
          if md5(os.path.join(BASE, "archetypes", a["idf"])) != a["idf_md5"]]
chk("C16 the 88 archetype IDFs are unchanged on disk", not adrift,
    "%d drifted" % len(adrift))

# C17 --- the pre-registration was not touched
chk("C17 prereg.md untouched",
    os.path.exists(PREREG) and md5(PREREG) == PREREG_MD5, PREREG_MD5)

# C18 --- the cache has exactly one key per run, all distinct
want = len(runs) + header["declared_reruns"]
chk("C18 one cache key per run, re-runs included",
    len(cache) == want and len({r["cache_key"] for r in runs}) == len(runs),
    "%d keys for %d runs + %d re-runs" % (len(cache), len(runs),
                                          header["declared_reruns"]))

# C19 --- the board's coverage clause
chk("C19 board coverage clause PASS",
    board.get("coverage_clause_verdict") == "PASS",
    ", ".join(k for k, v in board["coverage_clause"].items() if v == "NOT SCORED") or "all scored")

# C20 --- G8.12 and G8.16 are scored here for the FIRST time, and say so
ev = board["evaluable"]
chk("C20 the bands module still declares G8.12/G8.16 not evaluable at the CONTROL",
    ev["G8.12"].startswith("no") and ev["G8.16"].startswith("no"),
    "and this campaign is where they are evaluated")

print("\nHALF C: %d ok, %d FAILED" % (ok, len(bad)))
if bad:
    print("\nrefusing to run the battery on artefacts that already fail")
    for b in bad:
        print("  FAILED: %s" % b)
    sys.exit(1)


# =========================================================================
# HALF I --- the injection battery, on a SUBSET COPY
# =========================================================================
print("\nHALF I --- injections, on a COPY. Baseline must be clean first.")

work = tempfile.mkdtemp(prefix="4j_s85_")
PRIST = os.path.join(work, "pristine")
LIVE = os.path.join(work, "live")

# one cell per fold, so G8.16 has cross-fold material
SUB = []
for fold in ("es", "uk", "it"):
    for a in arch:
        if a["fold"] == fold:
            SUB.append(os.path.splitext(a["idf"])[0])
            break
SUBSET = set(SUB)


def stage():
    for d in (PRIST, LIVE):
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(PRIST)
    shutil.copy(REFERENCE, os.path.join(PRIST, os.path.basename(REFERENCE)))
    shutil.copy(IDF_MANIFEST, os.path.join(PRIST, os.path.basename(IDF_MANIFEST)))
    sruns = [r for r in runs if r["cell"] in SUBSET]
    sagg = [r for r in agg if r["cell"] in SUBSET]
    smon = [r for r in load_csv(MONTHLY) if r["cell"] in SUBSET]
    h = dict(header)
    h["declared_cells"] = len(SUBSET)
    h["declared_scenario_cells"] = len(sagg)
    h["declared_runs"] = len(sruns)
    h["declared_reruns"] = len(SUBSET) * len(SWEEP)
    h["subset_of"] = "the full campaign; staged by the injection battery"
    io.open(os.path.join(PRIST, "injected_campaign.json"), "w",
            encoding="utf-8").write(json.dumps(h, indent=1, sort_keys=True))
    for name, rowset in (("injected_runs.csv", sruns), ("agg_annual.csv", sagg),
                         ("injected_monthly.csv", smon)):
        with io.open(os.path.join(PRIST, name), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rowset[0].keys()))
            w.writeheader()
            for r in rowset:
                w.writerow(r)
    scache = {k: v for k, v in cache.items()
              if any(("cells/%s__" % c) in v["outdir"] for c in SUBSET)}
    io.open(os.path.join(PRIST, "injected_cache.json"), "w",
            encoding="utf-8").write(json.dumps(scache, indent=1, sort_keys=True))
    os.makedirs(os.path.join(PRIST, "cells"))
    for r in sagg:
        unit = "%s__%s" % (r["cell"], ftag(r["f"]))
        shutil.copytree(os.path.join(CELLS, unit), os.path.join(PRIST, "cells", unit))
    shutil.copytree(PRIST, LIVE)
    return len(sruns), len(sagg), len(scache)


def reset():
    shutil.rmtree(LIVE)
    shutil.copytree(PRIST, LIVE)


def score(base):
    """Run the real scorer on `base` and read WHICH GATES FELL off its artefact.

    Parsing the printout would make the battery depend on a print format rather
    than on the thing the campaign is judged by.  `injected_bands.csv` is that
    thing, so the battery reads the FAIL rows out of it --- and falls back to the
    printout only for `V8.a`, which aborts before any band row is written.
    """
    p = subprocess.run([PY, SCORER, "--base=" + base, "--quiet"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    fired, n = set(), 0
    bp = os.path.join(base, "injected_bands.csv")
    if os.path.exists(bp):
        for r in load_csv(bp):
            if r["verdict"] == "FAIL":
                fired.add(r["gate"])
                n += 1
    if "V8.a FAIL" in out:
        fired.add("V8.a")
        n += 1
    return fired, n, out


print("  staging a %d-cell copy of the campaign ..." % len(SUBSET))
nr, na, nc = stage()
print("  subset: %d runs, %d scenario-cells, %d cache keys" % (nr, na, nc))
base_fired, base_n, base_out = score(LIVE)
chk("I0 baseline copy scores clean", base_n == 0, "%d fails %s" % (base_n, sorted(base_fired)))
if base_n:
    print(base_out[-3000:])
    shutil.rmtree(work, ignore_errors=True)
    sys.exit("the baseline is not clean; no injection below would mean anything")

CELL = SUB[0]
CELL2 = SUB[1]


def upath(cell, f, *p):
    return os.path.join(LIVE, "cells", "%s__%s" % (cell, ftag(f)), *p)


def edit_csv(path, fn):
    r = list(csv.DictReader(io.open(path, encoding="utf-8")))
    fn(r)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0].keys()))
        w.writeheader()
        for x in r:
            w.writerow(x)


def scale_series(path, k):
    edit_csv(path, lambda r: [x.__setitem__("heating_j", "%.6f" % (float(x["heating_j"]) * k))
                              for x in r])


def roll_series(path, k):
    def f(r):
        vals = [x["heating_j"] for x in r]
        vals = vals[-k:] + vals[:-k]
        for x, v in zip(r, vals):
            x["heating_j"] = v
    edit_csv(path, f)


def rewrite_schedule_path(idf_path, new_csv):
    """Point the saved IDF's Schedule:File at a different file on disk."""
    txt = io.open(idf_path, encoding="utf-8").read()
    out, done = [], False
    for ln in txt.split("\n"):
        if not done and "!- File Name" in ln:
            out.append("  %s,                    !- File Name" % new_csv)
            done = True
        else:
            out.append(ln)
    io.open(idf_path, "w", encoding="utf-8", newline="").write("\n".join(out))
    return done


INJECTIONS = []


def injection(tag, target, desc):
    def deco(fn):
        INJECTIONS.append((tag, target, desc, fn))
        return fn
    return deco


@injection("I1", "G8.1", "scale the re-run's annual energy by 1.2 (registered perturbation)")
def _i1():
    scale_series(upath(CELL, 1.0, "_rerun", "series_hourly.csv"), 1.2)


@injection("I2", "G8.6", "shift the re-run profile 2 h later (registered perturbation)")
def _i2():
    roll_series(upath(CELL, 1.0, "_rerun", "series_hourly.csv"), 2)


@injection("I3", "G8.14", "copy another scenario-cell's manifest wholesale")
def _i3():
    shutil.copy(upath(CELL2, 1.0, "manifest.json"), upath(CELL, 1.0, "manifest.json"))


@injection("I4", "G8.14", "delete the fold field -- V8.g's arm")
def _i4():
    p = upath(CELL, 0.5, "manifest.json")
    m = json.load(io.open(p, encoding="utf-8"))
    m["fold"] = ""
    io.open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, sort_keys=True))


@injection("I5", "V8.d", "give one cell a floor area from a different geometry")
def _i5():
    p = upath(CELL, 0.3, "eplusout.eio")
    txt = io.open(p, encoding="utf-8", errors="replace").read().split("\n")
    hdr = None
    for i, ln in enumerate(txt):
        if ln.startswith("! <Zone Information>"):
            hdr = [x.strip() for x in ln.split(",")]
        elif ln.startswith(" Zone Information,") and hdr:
            j = hdr.index("Floor Area {m2}")
            f = ln.split(",")
            f[j] = "%.2f" % (float(f[j].strip()) * 1.5)
            txt[i] = ",".join(f)
            break
    io.open(p, "w", encoding="utf-8", newline="").write("\n".join(txt))


@injection("I6", "G8.10", "zero one end-use row and leave the total")
def _i6():
    p = upath(CELL, 1.0, "eplustbl.csv")
    rows = list(csv.reader(io.open(p, encoding="utf-8", errors="replace")))
    for i, r in enumerate(rows):
        if len(r) > 3 and r[1].strip() == "Heating":
            rows[i] = [r[0], r[1]] + ["0.00"] * (len(r) - 2)
            break
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)


@injection("I7", "G8.11", "an 'invalid'/'not found' line in the error file")
def _i7():
    p = upath(CELL, 0.15, "eplusout.err")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt += "\n   ** Warning ** Output:Variable, invalid Variable Name not found=BOGUS\n"
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I8", "G8.15", "a severe error in the error file")
def _i8():
    p = upath(CELL, 0.15, "eplusout.err")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt += "\n   ** Severe  ** GetSurfaceData: Invalid vertex count on S_WALL_N\n"
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I9", "G8.13", "Interpolate to Timestep = Yes on the REAL Schedule:File")
def _i9():
    p = upath(CELL, 1.0, "in.idf")
    txt = io.open(p, encoding="utf-8").read()
    txt = txt.replace("  No,                    !- Interpolate to Timestep",
                      "  Yes,                   !- Interpolate to Timestep")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I10", "V8.a", "the campaign declares more runs than the table holds")
def _i10():
    p = os.path.join(LIVE, "injected_campaign.json")
    h = json.load(io.open(p, encoding="utf-8"))
    h["declared_runs"] += 1
    io.open(p, "w", encoding="utf-8").write(json.dumps(h, indent=1, sort_keys=True))


@injection("I11", "G8.14", "a manifest that claims an engine its own err file denies")
def _i11():
    p = upath(CELL, 0.3, "manifest.json")
    m = json.load(io.open(p, encoding="utf-8"))
    m["energyplus_build"] = "0000000000"
    io.open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, sort_keys=True))


@injection("I12", "G8.8", "two scenarios that wrote the same result file")
def _i12():
    p = os.path.join(LIVE, "injected_runs.csv")

    def f(r):
        src = [x for x in r if x["cell"] == CELL and float(x["f"]) == 1.0][0]
        for x in r:
            if x["cell"] == CELL and float(x["f"]) == 0.5 \
                    and x["household"] == src["household"]:
                x["series_sha256"] = src["series_sha256"]
    edit_csv(p, f)


@injection("I13", "G8.9", "two runs handed the same cache key")
def _i13():
    p = os.path.join(LIVE, "injected_runs.csv")

    def f(r):
        src = [x for x in r if x["cell"] == CELL and float(x["f"]) == 1.0][0]
        for x in r:
            if x["cell"] == CELL and float(x["f"]) == 0.5 \
                    and x["household"] == src["household"]:
                x["cache_key"] = src["cache_key"]
    edit_csv(p, f)


@injection("I14", "G8.9", "the saved IDF no longer hashes to the key's own input")
def _i14():
    p = upath(CELL, 0.5, "in.idf")
    txt = io.open(p, encoding="utf-8").read()
    io.open(p, "w", encoding="utf-8", newline="").write(txt + "\n!- stale\n")


@injection("I15", "G8.12", "the schedule on disk is not the Step 7 diary at this f")
def _i15():
    src = upath(CELL, 1.0, "in.idf")
    bogus = os.path.join(LIVE, "bogus_multiplier.csv")
    with io.open(bogus, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("phi_int_multiplier\n")
        for i in range(8760):
            fh.write("%.6f\n" % (1.0 + 0.5 * ((i // 24) % 2)))
    rewrite_schedule_path(src, bogus)


@injection("I16", "G8.12", "E_PHI_INT re-pointed back at the flat schedule "
                           "-- the ASSIGNMENT arm, which has no value pair")
def _i16():
    # by LINE, because the injector reuses the source IDF's own column
    # spacing and an exact-string replace would silently do nothing.
    p = upath(CELL, 1.0, "in.idf")
    out, done = [], False
    for ln in io.open(p, encoding="utf-8").read().split("\n"):
        if not done and "!- Schedule Name" in ln and "SCH_PHI_INT" in ln:
            ln = ln.replace("SCH_PHI_INT", "SCH_ALWAYS_ON")
            done = True
        out.append(ln)
    if not done:
        raise AssertionError("I16 found no Schedule Name field to re-point")
    io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))


@injection("I17", "G8.16", "drive one country's cell with another country's fold")
def _i17():
    p = os.path.join(LIVE, "injected_runs.csv")
    other = "it" if CELL.startswith("es") else "es"
    onme = sorted(header["households"][other])[0]
    omd5 = md5(os.path.join(SCHED7, "leg4_%s_independent_seed1" % other, onme))

    def f(r):
        for x in r:
            if x["cell"] == CELL and float(x["f"]) == 1.0:
                x["schedule_file"] = onme
                x["schedule_md5"] = omd5
                break
    edit_csv(p, f)


@injection("I18", "V8.h", "the f = 0 multiplier is not identically 1.0")
def _i18():
    src = upath(CELL, 0.0, "in.idf")
    bogus = os.path.join(LIVE, "bogus_flat.csv")
    with io.open(bogus, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("phi_int_multiplier\n")
        for i in range(8760):
            fh.write("%.6f\n" % (1.0 if i else 0.5))
    rewrite_schedule_path(src, bogus)


print("")
hits, noops = 0, []
crosstab = []
for tag, target, desc, fn in INJECTIONS:
    reset()
    fn()
    fired, n, out = score(LIVE)
    hit = target in fired
    extra = sorted(fired - {target})
    crosstab.append((tag, target, hit, n, extra))
    if hit:
        hits += 1
        print("  HIT   %-4s -> %-6s  %-52s  also: %s"
              % (tag, target, desc[:52], ",".join(extra) if extra else "-"))
    else:
        noops.append(tag)
        print("  NO-OP %-4s -> %-6s  %-52s  fired: %s"
              % (tag, target, desc[:52], ",".join(sorted(fired)) or "NOTHING"))

shutil.rmtree(work, ignore_errors=True)

# ---- the coverage clause -------------------------------------------------
scored = set(x["gate"] for x in brows if x["verdict"] in ("PASS", "FAIL"))
falsified = set(t for _, t, h, _, _ in crosstab if h) | \
    set(e for _, _, _, _, ex in crosstab for e in ex)
unfalsified = sorted(scored - falsified)

print("")
chk("I-all every injection felled its target", not noops, "no-ops: %s" % (noops or "none"))
chk("coverage clause: every PASSing gate was made to fall", not unfalsified,
    "never falsified: %s" % (unfalsified or "none"))

print("\nHALF I: %d of %d injections HIT" % (hits, len(INJECTIONS)))
print("\nTOTAL: %d ok, %d FAILED" % (ok, len(bad)))
for b in bad:
    print("  FAILED: %s" % b)
sys.exit(1 if bad else 0)
