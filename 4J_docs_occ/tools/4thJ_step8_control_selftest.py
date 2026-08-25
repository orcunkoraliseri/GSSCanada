# -*- coding: utf-8 -*-
"""4J Step 8 item 8.3 --- the gate on the uninjected control campaign.

Two halves, and the second is the one that matters.

HALF C --- structural checks on the artefacts, all re-read from disk.
HALF I --- the injection battery.  A gate that has never been seen refusing is
           not evidence.  Every check in half C is put in front of a defect
           built to fell it, on a COPY of the campaign, and the run is only
           trusted if the pristine copy scores clean first.

           🔴 Coverage clause (val doc): cross-tab every perturbation against
           the baseline and FAIL the probe if any passing gate was never made to
           fall.  This file prints that cross-tab and refuses on a no-op.
"""
import csv
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
CONTROL = os.path.join(BASE, "control")
SCORER = os.path.join(HERE, "4thJ_gates_step8_control.py")
PY = sys.executable

ANNUAL = os.path.join(BASE, "control_annual.csv")
MONTHLY = os.path.join(BASE, "control_monthly.csv")
CAMPAIGN = os.path.join(BASE, "control_campaign.json")
BANDS = os.path.join(BASE, "control_bands.csv")
BOARD = os.path.join(BASE, "control_gate_board.json")
REFERENCE = os.path.join(BASE, "tabula_reference.csv")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")

ok = 0
bad = []


def chk(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
        print("  ok    %-46s %s" % (name, detail))
    else:
        bad.append(name)
        print("  FAIL  %-46s %s" % (name, detail))


def load_csv(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


# =========================================================================
# HALF C --- the artefacts
# =========================================================================
print("HALF C --- the uninjected control campaign on disk")

for p in (ANNUAL, MONTHLY, CAMPAIGN, BANDS, BOARD, REFERENCE):
    chk("C0 exists: %s" % os.path.basename(p), os.path.exists(p) and os.path.getsize(p) > 0)
if bad:
    sys.exit("artefacts missing -- run the campaign and the scorer first")

header = json.load(io.open(CAMPAIGN, encoding="utf-8"))
rows = load_csv(ANNUAL)
mrows = load_csv(MONTHLY)
brows = load_csv(BANDS)
board = json.load(io.open(BOARD, encoding="utf-8"))
arch = load_csv(IDF_MANIFEST)
wx = {r["fold"]: r for r in load_csv(WX_MANIFEST)}
ref = {r["Code_Building"]: r for r in load_csv(REFERENCE)}

# C1 --- every archetype ran, exactly once
chk("C1 one cell per 8.1 archetype",
    len(rows) == len(arch) and len(set(r["cell"] for r in rows)) == len(arch),
    "%d cells for %d IDFs" % (len(rows), len(arch)))

# C2 --- the campaign declares what it wrote (V8.a's own precondition)
chk("C2 declared == written == table",
    header["declared_cells"] == header["cells_written"] == len(rows),
    "declared %s, written %s" % (header["declared_cells"], header["cells_written"]))

# C3 --- no schedule anywhere. This is what makes it the CONTROL.
sched = []
for r in rows:
    m = json.load(io.open(os.path.join(CONTROL, r["cell"], "manifest.json"), encoding="utf-8"))
    if m.get("schedule_file") or m.get("f") != 0.0 or m.get("phi_int_w_m2") != 3.0:
        sched.append(r["cell"])
chk("C3 f = 0, phi_int = 3.0, no schedule file", not sched,
    "%d cell(s) carry a schedule" % len(sched))

# C4 --- V8.g: the fold field EXISTS in every manifest, and is the right one
foldbad = []
for r in rows:
    m = json.load(io.open(os.path.join(CONTROL, r["cell"], "manifest.json"), encoding="utf-8"))
    if not m.get("fold") or m["fold"] != r["fold"]:
        foldbad.append(r["cell"])
chk("C4 V8.g explicit fold field in every manifest", not foldbad,
    "%d bad" % len(foldbad))

# C5 --- one EPW per fold, and it is the D-S8-4 file, checked by md5
wrong = [r["cell"] for r in rows
         if r["epw"] != wx[r["fold"]]["epw"] or r["epw_md5"] != wx[r["fold"]]["epw_md5"]]
chk("C5 every cell ran its own fold's D-S8-4 EPW", not wrong, "%d wrong" % len(wrong))

# C6 --- 8760 hourly values in both the run and the re-run
lens = set()
for r in rows[:8] + rows[-8:]:
    for d in (os.path.join(CONTROL, r["cell"]),
              os.path.join(CONTROL, "_rerun", r["cell"])):
        lens.add(sum(1 for _ in io.open(os.path.join(d, "series_hourly.csv"),
                                        encoding="utf-8")) - 1)
chk("C6 8760 hourly values, run and re-run", lens == {8760}, "lengths %s" % sorted(lens))

# C7 --- the IDF EnergyPlus read is byte-identical to the 8.1 artefact
idfbad = []
for r in rows:
    m = json.load(io.open(os.path.join(CONTROL, r["cell"], "manifest.json"), encoding="utf-8"))
    if m["idf_md5_measured"] != m["idf_md5_manifest"] or m["idf_md5_measured"] != r["idf_md5"]:
        idfbad.append(r["cell"])
chk("C7 in.idf md5 == the 8.1 manifest md5", not idfbad, "%d differ" % len(idfbad))

# C8 --- the engine is one engine, and each manifest measured it itself
vers = set((r["eplus_version"], r["eplus_build"]) for r in rows)
chk("C8 one EnergyPlus version+build across 88 cells", len(vers) == 1, "%s" % sorted(vers))

# C9 --- G8.14's inherited-manifest arm: 176 runs, 176 distinct timestamps is
# too strong (a second is coarse), but two cells must not share a START instant
# AND a wall time AND a result.
sig = {}
dupe = []
for r in rows:
    m = json.load(io.open(os.path.join(CONTROL, r["cell"], "manifest.json"), encoding="utf-8"))
    k = (m["run"]["started_utc"], m["run"]["wall_s"], m["results"]["heating_j"])
    if k in sig:
        dupe.append((r["cell"], sig[k]))
    sig[k] = r["cell"]
chk("C9 no two cells share start+wall+result", not dupe, "%d duplicate signatures" % len(dupe))

# C10 --- V8.d: the area E+ computed, times n_storey, is TABULA's A_C_Ref
adev = []
for r in rows:
    a = float(r["zone_floor_area_eio_m2"]) * float(r["n_storey"])
    d = 100.0 * (a - float(r["a_ref_m2"])) / float(r["a_ref_m2"])
    if abs(d) > 0.1:
        adev.append((r["cell"], d))
chk("C10 V8.d eio floor x n_storey == a_ref", not adev, "%d off by >0.1 %%" % len(adev))

# C11 --- the 8.1 manifest's a_ref is TABULA's A_C_Ref, not a number we invented
mism = []
for r in rows:
    rr = ref.get(r["code"])
    if rr and abs(float(rr["A_C_Ref"]) - float(r["a_ref_m2"])) > 0.01:
        mism.append(r["cell"])
chk("C11 a_ref == TABULA A_C_Ref", not mism, "%d differ" % len(mism))

# C12 --- annual EUI is re-derivable from eplustbl.csv, independently of the
# hourly series the gates use.  Two paths to one number.
eui_bad = []
for r in rows:
    if not r["heating_gj_eplustbl"]:
        eui_bad.append(r["cell"])
        continue
    e2 = float(r["heating_gj_eplustbl"]) * (1000.0 / 3.6) / float(r["a_ref_m2"])
    if abs(e2 - float(r["eui_kwh_m2a"])) > 0.02 * max(1.0, float(r["eui_kwh_m2a"])):
        eui_bad.append(r["cell"])
chk("C12 EUI from eplustbl == EUI from the hourly series", not eui_bad,
    "%d differ by >2 %%" % len(eui_bad))

# C13 --- monthly table is complete and sums to the annual
msum = {}
for r in mrows:
    msum[r["cell"]] = msum.get(r["cell"], 0.0) + float(r["heating_j"])
mbad = [r["cell"] for r in rows
        if abs(msum.get(r["cell"], 0.0) - float(r["heating_j"])) > 1.0]
chk("C13 12 months per cell, summing to the annual",
    len(mrows) == 12 * len(rows) and not mbad, "%d rows, %d mismatched" % (len(mrows), len(mbad)))

# C14 --- zero severe errors anywhere (G8.15)
sev = sum(int(r["severe"]) for r in rows)
chk("C14 zero severe errors over 88 cells", sev == 0, "%d severe" % sev)

# C15 --- the band table covers every cell and every gate carries severity=hard
gates = sorted(set(x["gate"] for x in brows))
soft = [x for x in brows if x["severity"] != "hard"]
chk("C15 V8.e every band row is hard severity", not soft,
    "%d gates, %d rows, %d soft" % (len(gates), len(brows), len(soft)))

# C16 --- G8.7 is INFO and can never be anything else.  D-S8-5 item 1 (a)
# ruled that permanently, so this check also guards the band itself: if anyone
# ever fills G87_TOLERANCE_PCT in, the threshold column stops being empty and
# this fails.  That is the point -- the number would be fitted to an answer
# already in hand.
g87 = [x for x in brows if x["gate"] == "G8.7"]
chk("C16 G8.7 is INFO with no band (D-S8-5 item 1 (a)), never PASS or FAIL",
    g87 and all(x["verdict"] == "INFO" for x in g87)
    and all(x["threshold"] == "" for x in g87)
    and "G87_TOLERANCE_PCT = None" in io.open(
        os.path.join(HERE, "4thJ_step8_bands.py"), encoding="utf-8").read(),
    "%d rows" % len(g87))

# C17 --- the board names every gate it cannot evaluate
chk("C17 board declares the gates it cannot evaluate",
    set(board["not_evaluable_at_the_control"]) >= {"G8.8", "G8.9", "G8.12", "G8.16"},
    ", ".join(sorted(board["not_evaluable_at_the_control"])))

# C18 --- the reproducibility reference actually differs as a FILE while being
# identical as a RESULT.  If the re-run were the same directory re-read, the
# gate would be measuring nothing.
same_dir = [r["cell"] for r in rows
            if os.path.samefile(os.path.join(CONTROL, r["cell"]),
                                os.path.join(CONTROL, "_rerun", r["cell"]))] \
    if os.path.isdir(os.path.join(CONTROL, "_rerun")) else ["_rerun missing"]
chk("C18 the re-run is a different directory", not same_dir, "%d shared" % len(same_dir))

# C19 --- the diagnostics are diagnostics: nothing was applied, and no knob is
# a no-op reported as a measurement.
DIAG = os.path.join(BASE, "control_diagnostics.json")
if os.path.exists(DIAG):
    dg = json.load(io.open(DIAG, encoding="utf-8"))
    flat = [abs(c["dev_pct"]) for k in dg["knobs"].values() for c in k["cells"]]
    chk("C19 every diagnostic knob moved the answer",
        "DIAGNOSTIC ONLY" in dg.get("note", "") and flat and min(flat) > 0.01,
        "%d knobs, smallest |dev| %.3f %%" % (len(dg["knobs"]), min(flat) if flat else -1))
else:
    chk("C19 diagnostics present", False, "control_diagnostics.json missing")

# C20 --- the 8.1 artefacts the diagnostics read are byte-identical to what the
# campaign ran. A diagnostic that quietly edited an IDF would be undetectable.
adrift = []
for r in rows:
    p = os.path.join(BASE, "archetypes", r["cell"] + ".idf")
    h = __import__("hashlib").md5(open(p, "rb").read()).hexdigest()
    if h != r["idf_md5"]:
        adrift.append(r["cell"])
chk("C20 the 88 archetype IDFs are unchanged on disk", not adrift,
    "%d drifted" % len(adrift))

print("\nHALF C: %d ok, %d FAILED" % (ok, len(bad)))


# =========================================================================
# HALF I --- the injection battery
# =========================================================================
print("\nHALF I --- injections, on a COPY. Baseline must be clean first.")

work = tempfile.mkdtemp(prefix="4j_s83_")
PRIST = os.path.join(work, "pristine")
LIVE = os.path.join(work, "live")


def score(base):
    p = subprocess.run([PY, SCORER, "--base=" + base, "--quiet"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    fired = set()
    for ln in out.splitlines():
        m = re.match(r"\s+FAIL (\S+)\s", ln)
        if m:
            fired.add(m.group(1))
    if "V8.a FAIL" in out:
        fired.add("V8.a")
    n = 0
    m = re.search(r"RESULT      : (\d+) gate-cell FAILs", out)
    if m:
        n = int(m.group(1))
    return fired, n, out


def stage():
    for d in (PRIST, LIVE):
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(PRIST)
    for f in ("control_annual.csv", "control_monthly.csv", "control_campaign.json",
              "tabula_reference.csv"):
        shutil.copy(os.path.join(BASE, f), os.path.join(PRIST, f))
    shutil.copytree(CONTROL, os.path.join(PRIST, "control"))
    shutil.copytree(PRIST, LIVE)


def reset():
    shutil.rmtree(LIVE)
    shutil.copytree(PRIST, LIVE)


print("  staging a copy of the campaign ...")
stage()
base_fired, base_n, base_out = score(LIVE)
chk("I0 baseline copy scores clean", base_n == 0 and not base_fired,
    "%d fails %s" % (base_n, sorted(base_fired)))
if base_n:
    print(base_out[-2000:])
    sys.exit("the baseline is not clean; no injection below would mean anything")

CELL = rows[0]["cell"]
CELL2 = rows[1]["cell"]


def cpath(*p):
    return os.path.join(LIVE, "control", *p)


def scale_series(path, k):
    r = list(csv.DictReader(io.open(path, encoding="utf-8")))
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0].keys()))
        w.writeheader()
        for x in r:
            x["heating_j"] = "%.6f" % (float(x["heating_j"]) * k)
            w.writerow(x)


def roll_series(path, k):
    r = list(csv.DictReader(io.open(path, encoding="utf-8")))
    vals = [x["heating_j"] for x in r]
    vals = vals[-k:] + vals[:-k]
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0].keys()))
        w.writeheader()
        for x, v in zip(r, vals):
            x["heating_j"] = v
            w.writerow(x)


INJECTIONS = []


def injection(tag, target, desc):
    def deco(fn):
        INJECTIONS.append((tag, target, desc, fn))
        return fn
    return deco


@injection("I1", "G8.1", "scale the re-run's annual energy by 1.2 (registered perturbation)")
def _i1():
    scale_series(cpath("_rerun", CELL, "series_hourly.csv"), 1.2)


@injection("I2", "G8.6", "shift the re-run profile 2 h later (registered perturbation)")
def _i2():
    roll_series(cpath("_rerun", CELL, "series_hourly.csv"), 2)


@injection("I3", "G8.14", "copy another cell's manifest wholesale (registered perturbation)")
def _i3():
    shutil.copy(cpath(CELL2, "manifest.json"), cpath(CELL, "manifest.json"))


@injection("I4", "G8.14", "delete the fold field -- V8.g's arm")
def _i4():
    p = cpath(CELL, "manifest.json")
    m = json.load(io.open(p, encoding="utf-8"))
    m["fold"] = ""
    io.open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, sort_keys=True))


@injection("I5", "V8.d", "give one cell a floor area from a different geometry")
def _i5():
    p = cpath(CELL, "eplusout.eio")
    out = []
    for ln in io.open(p, encoding="utf-8", errors="replace"):
        if ln.startswith(" Zone Information,"):
            f = ln.rstrip("\n").split(",")
            f[22] = "%.2f" % (float(f[22]) * 1.5)
            ln = ",".join(f) + "\n"
        out.append(ln)
    io.open(p, "w", encoding="utf-8", newline="").write("".join(out))


@injection("I6", "G8.10", "zero one end-use row and leave the total (registered perturbation)")
def _i6():
    p = cpath(CELL, "eplustbl.csv")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt = txt.replace(",Heating,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,",
                      ",Heating,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,X",
                      1)
    m = re.search(r"\n,Heating,([^\n]*)\n", txt)
    if m:
        f = m.group(1).split(",")
        f = ["0.00"] * len(f)
        txt = txt[:m.start()] + "\n,Heating," + ",".join(f) + "\n" + txt[m.end():]
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I7", "G8.11", "an 'invalid'/'not found' line in the error file")
def _i7():
    p = cpath(CELL, "eplusout.err")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt = txt.replace("   ************* Beginning Simulation",
                      "   ** Warning ** Output:Variable, request variable=\"Boiler NG Rate\" "
                      "not found.\n   ************* Beginning Simulation", 1)
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I8", "G8.15", "a severe error in the error file")
def _i8():
    p = cpath(CELL, "eplusout.err")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt = txt.replace("   ************* Beginning Simulation",
                      "   ** Severe  ** GetSurfaceData: Duplicate surface name.\n"
                      "   ************* Beginning Simulation", 1)
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I9", "G8.13", "a Schedule:File with Interpolate to Timestep = Yes")
def _i9():
    p = cpath(CELL, "in.idf")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt += ("\nSchedule:File,\n  S_INJECT,\n  Frac,\n  x.csv,\n  1,\n  0,\n  8760,\n"
            "  Comma,\n  Yes;\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


@injection("I10", "V8.a", "the campaign declares more cells than the table holds")
def _i10():
    p = os.path.join(LIVE, "control_campaign.json")
    h = json.load(io.open(p, encoding="utf-8"))
    h["declared_cells"] = h["declared_cells"] + 1
    io.open(p, "w", encoding="utf-8").write(json.dumps(h, indent=1, sort_keys=True))


@injection("I11", "G8.14", "a manifest that claims an engine its own err file denies")
def _i11():
    p = cpath(CELL, "manifest.json")
    m = json.load(io.open(p, encoding="utf-8"))
    m["energyplus_build"] = "deadbeef99"
    io.open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, sort_keys=True))


@injection("I12", "V8.x", "the two E+ heating series disagree by 5 %")
def _i12():
    p = os.path.join(LIVE, "control_monthly.csv")
    r = list(csv.DictReader(io.open(p, encoding="utf-8")))
    for x in r:
        if x["cell"] == CELL and x["heating_var_j"]:
            x["heating_var_j"] = "%.6f" % (float(x["heating_var_j"]) * 1.05)
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0].keys()))
        w.writeheader()
        for x in r:
            w.writerow(x)


@injection("I13", "G8.13", "a REAL 9-field Schedule:File with Interpolate = Yes "
                           "(FINDING 126 -- I9's shape omits Minutes per Item)")
def _i13():
    # I9 appends an 8-field Schedule:File, which puts `Yes` in the LAST comma
    # field.  The real injector (tools/4thJ_step8_scenario.py, work item 8.4)
    # writes `Minutes per Item` after it, and on that shape the original parser
    # could not see the Yes at all -- the gate read PASS.  This injection uses
    # the shape the campaign will actually produce, so the fix is what is being
    # tested rather than the fix's own convenience case.
    p = cpath(CELL, "in.idf")
    txt = io.open(p, encoding="utf-8", errors="replace").read()
    txt += ("\nSchedule:File,\n"
            "  S_INJECT9,             !- Name\n"
            "  Frac,                  !- Schedule Type Limits Name\n"
            "  x.csv,                 !- File Name\n"
            "  1,                     !- Column Number\n"
            "  1,                     !- Rows to Skip at Top\n"
            "  8760,                  !- Number of Hours of Data\n"
            "  Comma,                 !- Column Separator\n"
            "  Yes,                   !- Interpolate to Timestep\n"
            "  60;                    !- Minutes per Item\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


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
        print("  HIT   %-4s -> %-6s  %-58s  also: %s"
              % (tag, target, desc[:58], ",".join(extra) if extra else "-"))
    else:
        noops.append(tag)
        print("  NO-OP %-4s -> %-6s  %-58s  fired: %s"
              % (tag, target, desc[:58], ",".join(sorted(fired)) or "NOTHING"))

shutil.rmtree(work, ignore_errors=True)

# ---- coverage clause ----------------------------------------------------
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
