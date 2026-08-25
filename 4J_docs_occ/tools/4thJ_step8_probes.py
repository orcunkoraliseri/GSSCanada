# -*- coding: utf-8 -*-
"""4J Step 8 WORK ITEM 8.4 --- THE TWO PROBES.  They run BEFORE the campaign.

    "3J ran 56 cells in which two nominally different scenarios wrote
     byte-identical result files, and a skip-if-done cache handed back a
     directory produced by a schedule that had since been replaced.  Neither
     defect is visible in a scorecard: every value check passes, because the
     values it checks are the stale ones."

`G8.8` (scenario differentiation) and `G8.9` (stale-output guard) are the only
two Step 8 gates that work item 8.3 could not evaluate --- the uninjected
control has exactly one scenario and no cache, so both would have been
vacuously clean.  This tool gives them the two things they need and then does
the part that matters: it runs each of them on a DELIBERATELY BROKEN cell and
requires the gate to fall.  A gate never seen failing is a decoration.

WHAT IS ACTUALLY RUN
---------------------
Six EnergyPlus runs on one archetype, its own fold's EPW, and real Step 7
presence files from the fold that held that country out.

  PROBE A --- G8.8, scenario differentiation
    good arm    f = 0.00 and f = 1.00, injected properly.  The two result
                files MUST differ.  `G8.10` must stay clean in both.
    broken arm  a third scenario is DECLARED at f = 0.50 and wired to the
                f = 1.00 schedule file --- the injector silently not applying
                its own parameter, which is the 3J defect exactly.  The result
                files come out byte-identical and `G8.8` MUST FALL.

  PROBE B --- G8.9, stale-output guard
    good arm    key = every input that can change the result.  Run, re-run
                (must HIT --- a cache that never hits makes the guard vacuous,
                so the hit is asserted before anything else), then CHANGE THE
                SCHEDULE: the key must move and the cell must re-run.
    broken arm  key = the cell name alone.  Change the schedule; the key does
                not move, the stale directory is handed back, and the results
                on disk belong to a schedule that is no longer wired in.
                `G8.9` MUST FALL.

WHAT THE PROBES DO NOT CLAIM
-----------------------------
  * No band is moved and no threshold is defined here.  `G8.8` and `G8.9` are
    boolean wiring gates; the only numeric band used is `G8.10`'s, imported
    from `tools/4thJ_step8_bands.py` (V8.c: one source).
  * `G8.8` is scored ONLY over runs that actually executed.  Under the broken
    cache the second run never happened, so `G8.8` has one result file and no
    pair --- it reports NOT_EVALUATED rather than a pass it did not earn.  That
    is also why the two gates are independent: the stale cache fells `G8.9`
    and leaves `G8.8` silent.
  * Nothing outside `outputs_step8/probes/` is written or deleted.

Outputs
-------
  probes/<arm>/<tag>/     in.idf, eplusout.*, series_hourly.csv
  probes/_sched/          the multiplier files that were actually wired in
  probes_step8.json       every arm, its key, its digest and its verdict
"""
import csv
import datetime
import importlib.util as _ilu
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
CONTROL = os.path.join(BASE, "control")
PROBES = os.path.join(BASE, "probes")
SCHED_DIR = os.path.join(PROBES, "_sched")
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
OUT_JSON = os.path.join(BASE, "probes_step8.json")

DEFAULT_CELL = "es_AB_ES01"
# leg5, not leg4: the Leg-4 records stamp themselves NOT REPORTABLE, and the
# emitter had the leg hard-coded so nothing could reach the Leg-5 pools.
# Emitted on calendar 2017 because the 8.1 IDFs run a Sunday-start RunPeriod ---
# see V8.i, which refuses the pair rather than trusting this comment.
BUNDLE = {"es": "leg5_es_independent_seed1",
          "uk": "leg5_uk_independent_seed1",
          "it": "leg5_it_independent_seed1"}


def _load(name, mod):
    spec = _ilu.spec_from_file_location(mod, os.path.join(HERE, name))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


B = _load("4thJ_step8_bands.py", "step8_bands")        # V8.c: ONE source of bands
S = _load("4thJ_step8_scenario.py", "step8_scenario")  # the path 8.5 will import
C = _load("4thJ_step8_control.py", "step8_control")    # ONE runner, ONE reader
G = _load("4thJ_gates_step8_control.py", "step8_gates")  # ONE G8.13, the scorer's


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# running one cell and reducing it to a RESULT digest
# --------------------------------------------------------------------------

def execute(idf_path, epw, outdir):
    """Run, then reduce the run to the numbers a result file contains.

    The digest is taken over the parsed hourly series written back out in a
    canonical form, never over the inputs and never over anything carrying a
    timestamp or a path.  `control/<cell>/series_hourly.csv` and its
    independent re-run are byte-identical, which is what makes the comparison
    meaningful in the first place.
    """
    r = C.run_cell(idf_path, epw, outdir, PROBES)
    errp = os.path.join(outdir, "eplusout.err")
    if r["returncode"] != 0 or not os.path.exists(errp):
        sys.exit("run failed in %s: rc=%s\n%s"
                 % (outdir, r["returncode"], r["stdout_tail"]))
    sev, warn, fatal, kinds = C.err_counts(errp)
    ver, build = C.engine_from_err(errp)
    ecsv = os.path.join(outdir, "eplusout.csv")
    hourly, temps, months, monthly_var, present = C.read_series(ecsv)
    series = os.path.join(outdir, "series_hourly.csv")
    with io.open(series, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["hour", "month", "heating_j", "zone_temp_c"])
        for i, x in enumerate(hourly):
            w.writerow([i, months[i] if i < len(months) else "", "%.6f" % x,
                        "%.4f" % temps[i] if i < len(temps) else ""])
    uses, total = C.end_uses(os.path.join(outdir, "eplustbl.csv"))
    return {
        "outdir": os.path.relpath(outdir, PROJ).replace("\\", "/"),
        "series_sha256": S.sha256(series),
        "n_hours": len(hourly),
        "heating_j": sum(hourly),
        "peak_w": max(hourly) / 3600.0 if hourly else 0.0,
        "peak_hour": hourly.index(max(hourly)) if hourly else -1,
        "severe": sev, "warnings": warn,
        "eplus_version": ver, "eplus_build": build,
        "end_uses": uses, "end_use_total_gj": total,
        "wall_s": r["wall_s"],
    }


def g810(rec):
    """Sum of end uses against the reported total, PER FUEL --- the scorer's own
    arithmetic and the scorer's own band, so the probe cannot quietly disagree
    with the campaign about what `G8.10` means."""
    total = rec.get("end_use_total_gj")
    uses = rec.get("end_uses")
    if not uses or not total:
        return "FAIL", None, "could not parse the End Uses table"
    worst, worst_fuel, compared = 0.0, "", []
    for fuel, tot in total.items():
        s = sum(u.get(fuel, 0.0) for u in uses.values())
        if tot == 0.0 and s == 0.0:
            continue
        compared.append(fuel)
        d = (100.0 * (s - tot) / tot) if tot else 100.0
        if abs(d) > abs(worst):
            worst, worst_fuel = d, fuel
    if not compared:                                   # FINDING 127
        return "VACUOUS", None, "no fuel carries a non-zero total or sum"
    ok = abs(worst) <= B.G810_METER_CLOSURE_PCT
    return ("PASS" if ok else "FAIL"), worst, (
        "%d fuel(s) compared (%s), worst %.4f %%"
        % (len(compared), ", ".join(compared), worst))


def g813(outdir):
    """Interpolate to Timestep, read back out of the IDF EnergyPlus actually read.

    The control could not evaluate this --- `Schedule:Constant` carries no such
    field, so 8.3 recorded `NOT_EVALUABLE` rather than a vacuous pass.  The
    injected path introduces the project's first real `Schedule:File`, and this
    calls the SCORER's function rather than a second copy of it.  🔴 That is how
    `FINDING 126` surfaced: on a 9-field object the scorer's parser could not
    see a `Yes` at all.
    """
    bad, can_carry = G.idf_interpolate_violations(os.path.join(outdir, "in.idf"))
    if can_carry == 0:
        return "NOT_EVALUABLE", "no object that could carry the field"
    if bad:
        return "FAIL", "violations: %s" % ",".join(bad)
    return "PASS", "%d object(s) could have violated, none did" % can_carry


# --------------------------------------------------------------------------
# the cache, and the broken one
# --------------------------------------------------------------------------

class Cache(object):
    """Skip-if-done.  `keyfn` decides what the key sees --- which is the whole
    question `G8.9` asks."""

    def __init__(self, root, keyfn):
        self.root = root
        self.keyfn = keyfn
        self.index = {}

    def get_or_run(self, parts, idf_path, epw, tag):
        key = self.keyfn(parts)
        if key in self.index:
            return "HIT", key, self.index[key]
        outdir = os.path.join(self.root, tag)
        rec = execute(idf_path, epw, outdir)
        rec["cached_as"] = key
        self.index[key] = rec
        return "MISS", key, rec


def main():
    cell = DEFAULT_CELL
    for a in sys.argv[1:]:
        if a.startswith("--cell="):
            cell = a.split("=", 1)[1]
    if not os.path.exists(C.EPLUS):
        sys.exit("EnergyPlus not found at %s" % C.EPLUS)

    arch = {os.path.splitext(r["idf"])[0]: r
            for r in csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8"))}
    if cell not in arch:
        sys.exit("cell %s is not in the 8.1 IDF manifest" % cell)
    a = arch[cell]
    fold = a["fold"]
    wx = {r["fold"]: r for r in csv.DictReader(io.open(WX_MANIFEST, encoding="utf-8"))}
    epw = os.path.join(WEATHER, wx[fold]["epw"])
    idf_src = os.path.join(ARCH, a["idf"])
    for p in (epw, idf_src):
        if not os.path.exists(p):
            sys.exit("missing %s" % p)

    # --- the schedules: from the fold that held this country out (G8.16's rule)
    bundle = os.path.join(SCHED7, BUNDLE[fold])
    bman = json.load(io.open(os.path.join(bundle, "manifest.json"), encoding="utf-8"))
    if bman.get("fold") != fold:
        sys.exit("schedule bundle declares fold %r, cell is %r" % (bman.get("fold"), fold))
    presence = sorted(f for f in os.listdir(bundle) if f.startswith("presence_"))
    if len(presence) < 2:
        sys.exit("need two distinct Step 7 schedules, found %d" % len(presence))
    sched_x, sched_y = presence[0], presence[1]

    if os.path.isdir(PROBES):
        shutil.rmtree(PROBES)
    os.makedirs(SCHED_DIR)

    base_idf = io.open(idf_src, encoding="utf-8").read()
    idf_md5 = S.md5(idf_src)
    epw_md5 = S.md5(epw)
    exe_md5 = S.md5(C.EPLUS)

    def build(f, sched_name, tag):
        """Write the multiplier file for (schedule, f) and the IDF that reads it."""
        src = os.path.join(bundle, sched_name)
        g = S.read_presence(src)
        m = S.multiplier_series(g, f)
        mcsv = os.path.join(SCHED_DIR, "%s.csv" % tag)
        S.write_multiplier_csv(mcsv, m, "phi_int_multiplier")
        idf = os.path.join(SCHED_DIR, "%s.idf" % tag)
        io.open(idf, "w", encoding="utf-8", newline="\n").write(
            S.inject(base_idf, mcsv))
        return {"tag": tag, "f": f, "schedule": sched_name,
                "schedule_md5": S.md5(src), "multiplier_csv": mcsv,
                "multiplier_md5": S.md5(mcsv), "idf": idf,
                "injected_idf_md5": S.md5(idf)}

    print("WORK ITEM 8.4 --- THE TWO PROBES")
    print("cell        : %s   fold %s" % (cell, fold))
    print("weather     : %s" % os.path.basename(epw))
    print("schedules   : %s  {%s, %s}" % (BUNDLE[fold], sched_x, sched_y))
    print("bands       : tools/4thJ_step8_bands.py (G8.10 closure = %.2f %%)"
          % B.G810_METER_CLOSURE_PCT)
    print("")

    report = {"work_item": "8.4", "generated_utc": utcnow(), "cell": cell,
              "fold": fold, "epw": os.path.basename(epw), "epw_md5": epw_md5,
              "idf_md5": idf_md5, "eplus_exe_md5": exe_md5,
              "schedule_bundle": BUNDLE[fold],
              "schedules": {"x": sched_x, "y": sched_y},
              "probe_a": {}, "probe_b": {}, "checks": []}
    checks = report["checks"]

    def chk(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        print("  %-4s %-58s %s" % ("ok" if ok else "FAIL", name, detail))
        return bool(ok)

    # ======================================================================
    # PROBE A --- G8.8, scenario differentiation
    # ======================================================================
    print("PROBE A --- G8.8 scenario differentiation")
    s_f000 = build(0.00, sched_x, "A_f000")
    s_f100 = build(1.00, sched_x, "A_f100")
    r_f000 = execute(s_f000["idf"], epw, os.path.join(PROBES, "A_good", "f000"))
    r_f100 = execute(s_f100["idf"], epw, os.path.join(PROBES, "A_good", "f100"))

    differ = r_f000["series_sha256"] != r_f100["series_sha256"]
    a_good = chk("A1 G8.8 good arm: two scenarios, two different result files",
                 differ, "f0.00 %s vs f1.00 %s"
                 % (r_f000["series_sha256"][:12], r_f100["series_sha256"][:12]))
    v0, d0, w0 = g810(r_f000)
    v1, d1, w1 = g810(r_f100)
    # PASS and PASS only --- a VACUOUS closure is not "clean", it is a gate that
    # had nothing to compare, and FINDING 127 is what made the difference visible.
    a_clean = chk("A2 G8.10 stays clean in both scenario runs, non-vacuously",
                  v0 == "PASS" and v1 == "PASS",
                  "%s / %s (%s ; %s)" % (v0, v1, w0, w1))

    # the deliberately broken cell: a scenario DECLARED at f = 0.50 and wired
    # to the f = 1.00 file.  The injector "applied" a parameter that never
    # reached the schedule --- 3J's defect, reproduced on purpose.
    broken_idf = os.path.join(SCHED_DIR, "A_f050_BROKEN.idf")
    io.open(broken_idf, "w", encoding="utf-8", newline="\n").write(
        S.inject(base_idf, s_f100["multiplier_csv"]))
    r_f050 = execute(broken_idf, epw, os.path.join(PROBES, "A_broken", "f050"))
    identical = r_f050["series_sha256"] == r_f100["series_sha256"]
    a_fires = chk("A3 G8.8 SEEN FAILING: declared f=0.50 wired to f=1.00's file",
                  identical, "byte-identical result files: %s"
                  % r_f050["series_sha256"][:12])

    # f = 0 is the control endpoint of the pre-registered sweep, so the injected
    # path at f = 0 must reproduce the 8.3 control.  Reported, not gated.
    ctrl_series = os.path.join(CONTROL, cell, "series_hourly.csv")
    same_as_control = None
    if os.path.exists(ctrl_series):
        same_as_control = S.sha256(ctrl_series) == r_f000["series_sha256"]
        print("  INFO f = 0 reproduces the 8.3 control byte-for-byte: %s"
              % ("yes" if same_as_control else
                 "NO -- injected %.6f GJ vs control series on disk"
                 % (r_f000["heating_j"] / 1e9)))

    v13, d13 = g813(os.path.join(PROBES, "A_good", "f100"))
    a_g813 = chk("A4 G8.13 evaluable for the first time, read from the SAVED IDF",
                 v13 == "PASS", "%s -- %s (FINDING 126 was found here)"
                 % (v13, d13))

    report["probe_a"] = {
        "gate": "G8.8",
        "scenarios": [s_f000, s_f100],
        "good": {"f000": r_f000, "f100": r_f100, "differ": differ,
                 "g810": [v0, v1]},
        "broken": {"declared_f": 0.50, "wired_to": s_f100["tag"],
                   "run": r_f050, "identical_to_f100": identical},
        "f0_reproduces_control": same_as_control,
        "g813_on_injected_idf": [v13, d13],
    }
    print("")

    # ======================================================================
    # PROBE B --- G8.9, stale-output guard
    # ======================================================================
    print("PROBE B --- G8.9 stale-output guard")
    s_x = build(1.00, sched_x, "B_x")
    s_y = build(1.00, sched_y, "B_y")

    def parts_for(s):
        return {"cell": cell, "f": s["f"], "idf_md5": idf_md5,
                "schedule": s["schedule"], "schedule_md5": s["schedule_md5"],
                "multiplier_md5": s["multiplier_md5"],
                "injected_idf_md5": s["injected_idf_md5"],
                "epw_md5": epw_md5, "eplus_exe_md5": exe_md5}

    good = Cache(os.path.join(PROBES, "B_good"), S.cache_key)
    st1, k1, b1 = good.get_or_run(parts_for(s_x), s_x["idf"], epw, "x_first")
    st2, k2, b2 = good.get_or_run(parts_for(s_x), s_x["idf"], epw, "x_again")
    st3, k3, b3 = good.get_or_run(parts_for(s_y), s_y["idf"], epw, "y_after_change")

    b_caches = chk("B1 the cache actually caches (identical inputs -> HIT)",
                   st1 == "MISS" and st2 == "HIT",
                   "%s then %s on key %s" % (st1, st2, k1[:12]))
    b_good = chk("B2 G8.9 good arm: schedule changed -> key moved -> re-run",
                 st3 == "MISS" and k3 != k1,
                 "%s, key %s -> %s" % (st3, k1[:12], k3[:12]))
    b_differ = chk("B3 and the two executed runs differ (G8.8 stays clean here)",
                   b3["series_sha256"] != b1["series_sha256"],
                   "%s vs %s" % (b1["series_sha256"][:12], b3["series_sha256"][:12]))

    # the deliberately broken cell: a key over the cell name alone
    bad = Cache(os.path.join(PROBES, "B_broken"), lambda p: S.naive_cache_key(p["cell"]))
    bt1, bk1, bb1 = bad.get_or_run(parts_for(s_x), s_x["idf"], epw, "x_first")
    bt2, bk2, bb2 = bad.get_or_run(parts_for(s_y), s_y["idf"], epw, "y_after_change")
    stale = (bt2 == "HIT" and bk2 == bk1
             and bb2["series_sha256"] == bb1["series_sha256"])
    b_fires = chk("B4 G8.9 SEEN FAILING: schedule changed, key did not, stale reused",
                  stale, "%s on the same key %s; the result files belong to %s"
                  % (bt2, bk1[:12], sched_x))
    b_g88_silent = chk("B5 G8.8 does NOT fire on the stale arm (one run, no pair)",
                       bt2 == "HIT",
                       "NOT_EVALUATED -- the second run never executed, so there "
                       "is no second result file to compare")

    report["probe_b"] = {
        "gate": "G8.9",
        "scenarios": [s_x, s_y],
        "good": {"x_first": [st1, k1], "x_again": [st2, k2],
                 "y_after_change": [st3, k3],
                 "runs": {"x": b1, "y": b3}},
        "broken": {"key": "naive_cache_key(cell) -- the 3J defect",
                   "x_first": [bt1, bk1], "y_after_change": [bt2, bk2],
                   "stale_reused": stale, "run": bb1},
    }
    print("")

    # ======================================================================
    executed = [r_f000, r_f100, r_f050, b1, b3, bb1]
    sev_total = sum(r["severe"] for r in executed)
    clean = chk("Z1 zero severe errors across every executed run",
                sev_total == 0, "%d run(s), %d severe" % (len(executed), sev_total))

    # What one archetype's occupancy channel is worth, measured here and NOT a
    # campaign claim: 8.5 is what measures that, over 88 archetypes x 5 levels.
    d_ann = 100.0 * (r_f100["heating_j"] - r_f000["heating_j"]) / r_f000["heating_j"]
    d_pk = 100.0 * (r_f100["peak_w"] - r_f000["peak_w"]) / r_f000["peak_w"]
    print("  INFO f = 1.00 vs f = 0.00 on this ONE archetype: annual heating "
          "%+.2f %%, peak %+.2f %%, peak hour %d -> %d. One cell, not a result."
          % (d_ann, d_pk, r_f000["peak_hour"], r_f100["peak_hour"]))
    report["one_cell_sensitivity"] = {
        "annual_pct": d_ann, "peak_pct": d_pk,
        "peak_hour_f000": r_f000["peak_hour"], "peak_hour_f100": r_f100["peak_hour"],
        "note": "one archetype, one household, one fold -- NOT a campaign result",
    }

    ok = all([a_good, a_clean, a_fires, a_g813, b_caches, b_good, b_differ,
              b_fires, b_g88_silent, clean])
    report["verdict"] = "PASS" if ok else "FAIL"
    report["gates_now_evaluable"] = ["G8.8", "G8.9"]
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, indent=2, sort_keys=True))

    print("record      : %s" % os.path.relpath(OUT_JSON, PROJ).replace("\\", "/"))
    print("runs        : %d EnergyPlus runs, %.1f s, %d severe"
          % (len(executed), sum(r["wall_s"] for r in executed), sev_total))
    print("RESULT      : %s --- %d of %d checks ok; G8.8 and G8.9 were each "
          "seen PASSING on a correct cell and FAILING on a broken one"
          % (report["verdict"], sum(1 for c in checks if c["ok"]), len(checks)))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
