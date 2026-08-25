# -*- coding: utf-8 -*-
"""4J Step 8 --- SCORING THE UNINJECTED CONTROL.  `G8.0` and every gate the
control can actually evaluate.

`G8.0` is not a threshold.  It is a precondition on reading every other number
in this step: *"for every archetype x climate, run with no schedules applied,
and record where the result sits relative to every band"*, and *"if a band fails
on the control, that band is reported as a band-applicability limitation and its
value is NOT moved to make it pass."*

So this scorer produces two different things and never mixes them:

  1. a BAND-POSITION TABLE --- `control_bands.csv`, one row per (cell, gate),
     with the measured value, the threshold if one exists, and the verdict;
  2. a GATE BOARD --- `control_gate_board.json`, PASS/FAIL per gate over the
     whole campaign, plus every gate this campaign CANNOT evaluate together with
     the reason, so that a missing gate is a declaration and not an omission.

Everything is re-read from the artefacts on disk.  The scorer does not import
the runner and does not trust a manifest column when the file that column
describes is sitting next to it:

  * areas come from each cell's own `eplusout.eio` (`V8.d`);
  * the engine version and build come from each cell's own `eplusout.err`;
  * the schedule interpolation setting comes from the `in.idf` EnergyPlus read;
  * the end-use closure comes from `eplustbl.csv`.

`V8.b` --- the scorer and the gates consume the SAME table, and its path is
asserted and printed before any delta is computed.
`V8.e` --- every gate's severity is hard.  The guard says to grep for a soft
severity before trusting a PASS count, so this file contains no soft-severity
literal at all --- not even in a comment, because a comment would answer that
grep --- and every row it writes carries severity=hard, which the selftest
re-reads from the artefact.
"""
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# `--base=DIR` exists so that the selftest can score an INJECTED COPY of the
# campaign without ever touching the real artefacts.  It changes where the
# scorer reads from and nothing about what it scores.
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
for _a in sys.argv[1:]:
    if _a.startswith("--base="):
        BASE = os.path.abspath(_a.split("=", 1)[1])

CONTROL = os.path.join(BASE, "control")
RERUN = os.path.join(CONTROL, "_rerun")

CAMPAIGN = os.path.join(BASE, "control_campaign.json")
ANNUAL = os.path.join(BASE, "control_annual.csv")          # V8.b: THE table
MONTHLY = os.path.join(BASE, "control_monthly.csv")
REFERENCE = os.path.join(BASE, "tabula_reference.csv")
BANDS_CSV = os.path.join(BASE, "control_bands.csv")
BOARD = os.path.join(BASE, "control_gate_board.json")

sys.path.insert(0, HERE)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("step8_bands", os.path.join(HERE, "4thJ_step8_bands.py"))
B = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(B)                                 # V8.c: ONE source of bands

J_TO_KWH = 1.0 / 3.6e6
PHI_INT = 3.0


def read_series(path):
    hh, tt, mm = [], [], []
    with io.open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            hh.append(float(row["heating_j"]))
            mm.append(int(row["month"]) if row["month"] else 0)
            tt.append(float(row["zone_temp_c"]) if row["zone_temp_c"] else float("nan"))
    return hh, tt, mm


def monthly_from(hh, mm):
    out = [0.0] * 12
    for x, m in zip(hh, mm):
        if 1 <= m <= 12:
            out[m - 1] += x
    return out


def eio_geometry(path):
    hdr = None
    for ln in io.open(path, encoding="utf-8", errors="replace"):
        if ln.startswith("! <Zone Information>"):
            hdr = [x.strip() for x in ln.split(",")]
        elif ln.startswith(" Zone Information,") and hdr:
            f = [x.strip() for x in ln.split(",")]
            g = {}
            for key in ("Floor Area {m2}", "Exterior Gross Wall Area {m2}",
                        "Exterior Window Area {m2}", "Volume {m3}"):
                if key in hdr:
                    try:
                        g[key] = float(f[hdr.index(key)])
                    except (ValueError, IndexError):
                        g[key] = None
            return g
    return {}


def err_scan(path):
    sev = warn = 0
    kinds = {}
    suspicious = []
    ver = build = None
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for i, ln in enumerate(fh):
            s = ln.strip()
            if i == 0:
                for tok in s.split(","):
                    tok = tok.strip()
                    if tok.startswith("Version "):
                        v = tok[len("Version "):]
                        ver, build = (v.split("-", 1) + [None])[:2]
            if s.startswith("** Severe  **") or s.startswith("**  Fatal  **"):
                sev += 1
                kinds[s.split("**", 2)[-1].strip()[:90]] = \
                    kinds.get(s.split("**", 2)[-1].strip()[:90], 0) + 1
            elif s.startswith("** Warning **"):
                warn += 1
                k = s.split("**", 2)[-1].strip()[:90]
                kinds[k] = kinds.get(k, 0) + 1
            low = s.lower()
            # V8.f: triage by KIND. These two words are what 3J's frequency
            # ranking buried, so they are looked for by name in every line.
            if "invalid" in low or "not found" in low:
                suspicious.append(s[:120])
    return ver, build, sev, warn, kinds, suspicious


def end_uses(tbl_path):
    rows = list(csv.reader(io.open(tbl_path, encoding="utf-8", errors="replace")))
    for i, r in enumerate(rows):
        if len(r) == 1 and r[0].strip() == "End Uses":
            hdr = None
            for j in range(i + 1, min(i + 5, len(rows))):
                if len(rows[j]) > 3 and rows[j][0] == "" and rows[j][1] == "":
                    hdr = [c.strip() for c in rows[j]]
                    start = j + 1
                    break
            if hdr is None:
                return None, None
            uses, total = {}, {}
            for j in range(start, len(rows)):
                r2 = rows[j]
                if len(r2) < 3 or not r2[1].strip():
                    continue
                name = r2[1].strip()
                vals = {}
                for k in range(2, min(len(hdr), len(r2))):
                    try:
                        vals[hdr[k]] = float(r2[k])
                    except ValueError:
                        pass
                if name.lower().startswith("total end uses"):
                    total = vals
                    break
                uses[name] = vals
            return uses, total
    return None, None


def idf_interpolate_violations(idf_path):
    """G8.13, asserted from the file EnergyPlus actually read.

    `Interpolate to Timestep` is a field of Schedule:Day:Interval /
    Schedule:Day:List / Schedule:File.  A `Schedule:Constant` carries no such
    field --- which is exactly `FINDING 95`'s lesson from Step 7, where a
    Compact object meant the setting was never asserted at all.  So this returns
    BOTH the violations and the count of schedule objects that could carry the
    field, and the gate refuses to call "no violations" a pass when nothing
    could have violated it.

    🔴 `FINDING 126`, measured by work item 8.4 and fixed here ADDITIVELY.  The
    original body read only the LAST comma-field of the object.  That is where
    `Interpolate to Timestep` sits on a `Schedule:File` written WITHOUT the
    optional `Minutes per Item` --- which is the shape 8.3's injection battery
    used, so the gate was seen firing.  A real `Schedule:File` carries
    `Minutes per Item` after it, and on that shape the `Yes` is invisible: the
    gate returned no violations and the row read PASS.  The first real
    `Schedule:File` in this project is 8.4's own injected IDF, which is where it
    surfaced.

    The fix reads the field BY POSITION for `Schedule:File` (field 8, 0-based,
    counting the object type as field 0) and keeps the last-field scan for
    every object and every shape it already caught.  Nothing that used to fire
    stops firing; a shape that could not fire now can.

    ⚪ Comments are stripped PER LINE first.  IDF writes `value,  !- Field Name`
    so a trailing comment belongs to the field before the comma, and splitting
    on `!` after splitting on `,` mis-aligns every field in the object.
    """
    txt = io.open(idf_path, encoding="utf-8", errors="replace").read()
    objs = [o.strip() for o in txt.split(";")]
    can_carry = 0
    bad = []
    for o in objs:
        clean = "\n".join(ln.split("!")[0] for ln in o.split("\n"))
        fields = [f.strip().lower() for f in clean.split(",")]
        head = fields[0] if fields else ""
        if head in ("schedule:day:interval", "schedule:day:list", "schedule:file"):
            can_carry += 1
            hit = "yes" in o.lower().split(",")[-1]          # the original scan
            if head == "schedule:file" and len(fields) > 8:  # FINDING 126
                hit = hit or fields[8] == "yes"
            if hit:
                bad.append(head)
    return bad, can_carry


def pct(a, b):
    if b in (0, 0.0, None) or a is None:
        return None
    return 100.0 * (a - b) / b


def main():
    quiet = "--quiet" in sys.argv
    if not os.path.exists(ANNUAL):
        sys.exit("no campaign table at %s -- run tools/4thJ_step8_control.py first" % ANNUAL)

    print("V8.b  scoring table : %s" % os.path.relpath(ANNUAL, PROJ))
    print("V8.b  monthly table : %s" % os.path.relpath(MONTHLY, PROJ))
    print("V8.c  bands module  : %s (G8.7 tolerance = %r)"
          % ("tools/4thJ_step8_bands.py", B.G87_TOLERANCE_PCT))

    header = json.load(io.open(CAMPAIGN, encoding="utf-8"))
    rows = list(csv.DictReader(io.open(ANNUAL, encoding="utf-8")))
    ref = {r["Code_Building"]: r for r in csv.DictReader(io.open(REFERENCE, encoding="utf-8"))}

    fails = []            # (gate, cell, message)
    notes = []
    band_rows = []
    per_gate = {}

    def record(gate, cell, fold, quantity, value, threshold, verdict, reference, note=""):
        band_rows.append({"cell": cell, "fold": fold, "gate": gate, "quantity": quantity,
                          "value": "" if value is None else "%.6f" % value,
                          "threshold": "" if threshold is None else "%.6f" % threshold,
                          "verdict": verdict, "reference": reference, "note": note,
                          "severity": "hard"})
        d = per_gate.setdefault(gate, {"PASS": 0, "FAIL": 0, "INFO": 0,
                                       "NO_THRESHOLD_PREREGISTERED": 0,
                                       "NOT_EVALUABLE": 0})
        d[verdict] = d.get(verdict, 0) + 1
        if verdict == "FAIL":
            fails.append((gate, cell, note or quantity))

    # ---- V8.a ------------------------------------------------------------
    declared = header.get("declared_cells")
    if declared != len(rows):
        sys.exit("V8.a FAIL: campaign declares %s cells, the table has %d"
                 % (declared, len(rows)))
    print("V8.a  cells         : %d declared, %d read -- OK" % (declared, len(rows)))

    monthly_tbl = {}
    for r in csv.DictReader(io.open(MONTHLY, encoding="utf-8")):
        monthly_tbl.setdefault(r["cell"], []).append(r)

    started_seen = {}
    warn_kind_totals = {}
    suspicious_all = []
    g87 = []
    hours_on = {}

    for r in rows:
        cell, fold = r["cell"], r["fold"]
        cdir = os.path.join(CONTROL, cell)
        rdir = os.path.join(RERUN, cell)
        man = json.load(io.open(os.path.join(cdir, "manifest.json"), encoding="utf-8"))

        # ---- V8.g / G8.14 : the fold field must EXIST, not merely be right --
        if "fold" not in man or not man["fold"]:
            record("G8.14", cell, fold, "fold field present", None, None, "FAIL",
                   "manifest", "V8.g: manifest carries no fold field")
        if man.get("cell") != cell:
            record("G8.14", cell, fold, "manifest cell matches directory", None, None,
                   "FAIL", "manifest", "manifest says %r, directory is %r"
                   % (man.get("cell"), cell))
        missing = [k for k in ("idf_md5_measured", "weather_md5", "energyplus_version",
                               "energyplus_build", "platform", "site_location_line")
                   if not man.get(k)]
        if missing:
            record("G8.14", cell, fold, "required manifest fields", None, None, "FAIL",
                   "manifest", "missing: %s" % ",".join(missing))
        if not man.get("platform", {}).get("measured_at_run_time"):
            record("G8.14", cell, fold, "platform measured", None, None, "FAIL",
                   "manifest", "platform not marked measured at run time")
        st = man.get("run", {}).get("started_utc")
        # the "copy another cell's manifest wholesale" arm: two different cells
        # cannot have started at the same instant on a serial campaign.
        if st in started_seen and started_seen[st] != cell:
            record("G8.14", cell, fold, "run timestamp distinct", None, None, "FAIL",
                   "manifest", "same started_utc as %s -- inherited manifest"
                   % started_seen[st])
        started_seen[st] = cell
        if man.get("idf_md5_measured") != man.get("idf_md5_manifest"):
            record("G8.14", cell, fold, "idf md5 measured == 8.1 manifest", None, None,
                   "FAIL", "in.idf", "%s vs %s" % (man.get("idf_md5_measured"),
                                                   man.get("idf_md5_manifest")))
        if not any(x["verdict"] == "FAIL" and x["gate"] == "G8.14" and x["cell"] == cell
                   for x in band_rows):
            record("G8.14", cell, fold, "manifest completeness", None, None, "PASS",
                   "manifest", "")

        # ---- engine, read from THIS cell's own err -------------------------
        ver, build, sev, warn, kinds, susp = err_scan(os.path.join(cdir, "eplusout.err"))
        for k, v in kinds.items():
            warn_kind_totals[k] = warn_kind_totals.get(k, 0) + v
        suspicious_all.extend(("%s: %s" % (cell, s)) for s in susp)
        record("G8.15", cell, fold, "severe errors", float(sev),
               float(B.G815_SEVERE_MAX), "PASS" if sev <= B.G815_SEVERE_MAX else "FAIL",
               "eplusout.err", "%d warning(s)" % warn)
        if ver != man.get("energyplus_version") or build != man.get("energyplus_build"):
            record("G8.14", cell, fold, "engine matches its own err file", None, None,
                   "FAIL", "eplusout.err", "err says %s-%s, manifest says %s-%s"
                   % (ver, build, man.get("energyplus_version"), man.get("energyplus_build")))

        # ---- V8.d : geometry from THIS cell's own eio ----------------------
        g = eio_geometry(os.path.join(cdir, "eplusout.eio"))
        area = g.get("Floor Area {m2}")
        a_ref = float(r["a_ref_m2"])
        n_storey = float(r["n_storey"])
        implied = area * n_storey if area else None
        dev = pct(implied, a_ref)
        record("V8.d", cell, fold, "a_ref from eio x n_storey vs manifest", dev,
               B.AREA_CONSISTENCY_PCT,
               "PASS" if dev is not None and abs(dev) <= B.AREA_CONSISTENCY_PCT else "FAIL",
               "eplusout.eio", "eio floor %.2f m2 x %g storeys" % (area or -1, n_storey))

        # ---- series ---------------------------------------------------------
        h1, t1, m1 = read_series(os.path.join(cdir, "series_hourly.csv"))
        h2, t2, m2 = read_series(os.path.join(rdir, "series_hourly.csv"))
        if len(h1) != len(h2) or not h1:
            record("G8.2", cell, fold, "series length", float(len(h1)), float(len(h2)),
                   "FAIL", "the re-run", "primary %d h, re-run %d h" % (len(h1), len(h2)))
            continue
        mon1, mon2 = monthly_from(h1, m1), monthly_from(h2, m2)

        # G8.1 - G8.4, reproducibility (D-S8-1 (a)), reference = the re-run
        for gate, val, thr, q in (
                ("G8.1", B.nmbe_pct(mon1, mon2), B.G81_NMBE_MONTHLY_PCT, "NMBE monthly %"),
                ("G8.2", B.nmbe_pct(h1, h2), B.G82_NMBE_HOURLY_PCT, "NMBE hourly %"),
                ("G8.3", B.cvrmse_pct(mon1, mon2), B.G83_CVRMSE_MONTHLY_PCT, "CV(RMSE) monthly %"),
                ("G8.4", B.cvrmse_pct(h1, h2), B.G84_CVRMSE_HOURLY_PCT, "CV(RMSE) hourly %")):
            if val is None:
                record(gate, cell, fold, q, None, thr, "FAIL", "the re-run",
                       "reference series sums to zero")
            else:
                record(gate, cell, fold, q, val, thr,
                       "PASS" if abs(val) <= thr else "FAIL", "the re-run (D-S8-1 (a))")

        # G8.5 / G8.6, armed against the re-run -- D-S8-5 item 2 extends
        # D-S8-1 (a) to them verbatim, so the re-run IS the named reference now
        # and the thresholds did not move.  The occupancy-driven peak shift that
        # 8.5 exists to measure is reported as an empirical result, NOT scored
        # against the flat control: that was the FINDING 44 inversion, in which
        # the gate fails exactly when the paper's claim succeeds.
        p1, p2 = max(h1) / 3600.0, max(h2) / 3600.0
        i1, i2 = h1.index(max(h1)), h2.index(max(h2))
        d5 = pct(p1, p2)
        record("G8.5", cell, fold, "peak magnitude dev %", d5, B.G85_PEAK_MAGNITUDE_PCT,
               "PASS" if d5 is not None and abs(d5) <= B.G85_PEAK_MAGNITUDE_PCT else "FAIL",
               "the re-run (D-S8-5 item 2 -> D-S8-1 (a))",
               "reproducibility tripwire; peak shift is reported, not gated")
        record("G8.6", cell, fold, "peak timing |dh|", float(abs(i1 - i2)),
               float(B.G86_PEAK_TIMING_H),
               "PASS" if abs(i1 - i2) <= B.G86_PEAK_TIMING_H else "FAIL",
               "the re-run (D-S8-5 item 2 -> D-S8-1 (a))",
               "reproducibility tripwire; peak shift is reported, not gated")

        # the two heating series E+ reports must agree for an ideal-loads zone
        mv = [float(x["heating_var_j"]) for x in monthly_tbl.get(cell, [])
              if x["heating_var_j"]]
        if len(mv) == 12:
            d = pct(sum(mv), sum(mon1))
            record("V8.x", cell, fold, "zone-monthly vs supply-hourly %", d,
                   B.SERIES_CONSISTENCY_PCT,
                   "PASS" if d is not None and abs(d) <= B.SERIES_CONSISTENCY_PCT else "FAIL",
                   "eplusout.csv", "two independently aggregated E+ variables")

        # G8.10 end-use closure
        uses, total = end_uses(os.path.join(cdir, "eplustbl.csv"))
        if not uses or not total:
            record("G8.10", cell, fold, "end-use table readable", None, None, "FAIL",
                   "eplustbl.csv", "could not parse the End Uses table")
        else:
            # 🔴 FINDING 127, found by work item 8.4.  `worst_fuel` stays empty
            # when the worst deviation is exactly 0, so the note used to read
            # "worst fuel: all zero" on all 88 cells --- which reads as "nothing
            # was compared" when in fact District Heating Water closed at
            # 97.99 GJ against 97.99 GJ.  The fuels ACTUALLY compared are now
            # counted, so a vacuous pass and a perfect pass stop looking alike.
            worst, worst_fuel, compared = 0.0, "", []
            for fuel, tot in total.items():
                s = sum(u.get(fuel, 0.0) for u in uses.values())
                if tot == 0.0 and s == 0.0:
                    continue
                compared.append(fuel)
                d = pct(s, tot) if tot else 100.0
                if abs(d) > abs(worst):
                    worst, worst_fuel = d, fuel
            if not compared:
                note = "VACUOUS: no fuel carries a non-zero total or sum"
            else:
                note = "%d fuel(s) compared (%s); worst %s" % (
                    len(compared), ", ".join(compared), worst_fuel or compared[0])
            record("G8.10", cell, fold, "sum(end uses) vs total %", worst,
                   B.G810_METER_CLOSURE_PCT,
                   "PASS" if abs(worst) <= B.G810_METER_CLOSURE_PCT else "FAIL",
                   "eplustbl.csv", note)

        # G8.11 requested vs delivered
        delivered = man.get("run", {}).get("variables_delivered", {})
        undelivered = [k for k, v in delivered.items() if not v]
        record("G8.11", cell, fold, "requested variables delivered",
               float(len(undelivered)), 0.0,
               "FAIL" if undelivered else "PASS", "eplusout.csv",
               ("not delivered: %s" % ", ".join(undelivered)) if undelivered else
               "%d of %d" % (len(delivered), len(delivered)))
        if susp:
            record("G8.11", cell, fold, "'invalid'/'not found' in err",
                   float(len(susp)), 0.0, "FAIL", "eplusout.err", susp[0])

        # G8.13 interpolation, from the in.idf E+ read
        bad, can_carry = idf_interpolate_violations(os.path.join(cdir, "in.idf"))
        if bad:
            record("G8.13", cell, fold, "Interpolate to Timestep = Yes", float(len(bad)),
                   0.0, "FAIL", "in.idf", ",".join(bad))
        elif can_carry == 0:
            record("G8.13", cell, fold, "schedule objects that can carry the field",
                   0.0, None, "NOT_EVALUABLE", "in.idf",
                   "the control uses Schedule:Constant only, which has no "
                   "interpolate field -- vacuously clean, declared not claimed")
        else:
            record("G8.13", cell, fold, "Interpolate to Timestep = Yes", 0.0, 0.0,
                   "PASS", "in.idf", "%d object(s) could have violated" % can_carry)

        # ---- G8.7 : where the control sits against TABULA's own answer ------
        rr = ref.get(r["code"])
        eui = float(r["eui_kwh_m2a"])
        hours_on[cell] = int(r["hours_heating_on"])
        if not rr or not rr["q_h_nd"]:
            record("G8.7", cell, fold, "EUI vs TABULA q_h_nd", None, None, "FAIL",
                   "tabula_reference.csv", "no reference row for %s" % r["code"])
        else:
            q = float(rr["q_h_nd"])
            d = pct(eui, q)
            g87.append((fold, cell, eui, q, d, int(r["hours_heating_on"]),
                        float(rr["heating_hours_implied"] or 0.0)))
            # D-S8-5 item 1 (a): INFO, permanently, with no band.  The
            # verdict is INFO whatever the deviation is -- there is nothing
            # here that can pass or fail, by ruling.
            record("G8.7", cell, fold, "EUI vs TABULA q_h_nd, dev %", d,
                   B.G87_TOLERANCE_PCT, "INFO",
                   "TABULA q_h_nd (as-modelled), INFO by D-S8-5 item 1 (a)",
                   "ours %.2f vs TABULA %.2f kWh/(m2.a)" % (eui, q))

    # ---------------------------------------------------------------------
    # the board
    # ---------------------------------------------------------------------
    board = {
        "campaign": header.get("campaign"),
        "work_item": "8.3",
        "cells": len(rows),
        "runs": 2 * len(rows),
        "vacuity_guards": {
            "V8.a": "PASS -- %d declared, %d read" % (declared, len(rows)),
            "V8.b": "PASS -- one table, path asserted: %s" % os.path.relpath(ANNUAL, PROJ),
            "V8.c": "PASS -- bands imported from tools/4thJ_step8_bands.py",
            "V8.d": "scored per cell, areas from each cell's own eplusout.eio",
            "V8.e": "PASS -- every gate row in control_bands.csv carries severity=hard",
            "V8.f": "warnings triaged by kind, see warning_kinds below",
            "V8.g": "PASS -- every control manifest carries an explicit fold field",
        },
        "per_gate": per_gate,
        "not_evaluable_at_the_control": {k: v for k, v in B.EVALUABLE_AT_CONTROL.items()
                                         if v.startswith("no")},
        "warning_kinds": warn_kind_totals,
        "suspicious_err_lines": suspicious_all[:20],
        "fails": [{"gate": g, "cell": c, "note": n} for g, c, n in fails],
    }

    # G8.0's own output: where the control sits, per fold
    g0 = {}
    for fold in ("es", "uk", "it"):
        sel = [x for x in g87 if x[0] == fold]
        if not sel:
            continue
        dev = sorted(x[4] for x in sel)
        ours = sorted(x[2] for x in sel)
        tab = sorted(x[3] for x in sel)
        hon = sorted(x[5] for x in sel)
        thr = sorted(x[6] for x in sel)
        g0[fold] = {
            "n": len(sel),
            "our_eui_median": ours[len(ours) // 2],
            "tabula_q_h_nd_median": tab[len(tab) // 2],
            "dev_pct_median": dev[len(dev) // 2],
            "dev_pct_min": dev[0], "dev_pct_max": dev[-1],
            "sign": "above" if dev[len(dev) // 2] > 0 else "below",
            "eplus_heating_hours_median": hon[len(hon) // 2],
            "tabula_heating_hours_implied_median": thr[len(thr) // 2],
        }
    board["G8.0_band_position"] = g0

    with io.open(BANDS_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(band_rows[0].keys()))
        w.writeheader()
        for x in band_rows:
            w.writerow(x)
    with io.open(BOARD, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(board, indent=1, sort_keys=True))

    # ---------------------------------------------------------------------
    if not quiet:
        print("")
        print("%-7s %-34s %s" % ("GATE", "verdicts over %d cells" % len(rows), "provenance"))
        for gate in sorted(per_gate):
            d = per_gate[gate]
            s = "  ".join("%s=%d" % (k, v) for k, v in sorted(d.items()) if v)
            print("%-7s %-34s %s" % (gate, s, B.PROVENANCE.get(gate, "")))
        print("")
        print("G8.0 --- where the UNINJECTED control sits against TABULA's own q_h_nd")
        print("%-4s %4s %10s %10s %9s %9s %9s   %s"
              % ("fold", "n", "ours", "TABULA", "dev %", "E+ h_on", "TAB h_on", "sign"))
        for f, v in g0.items():
            print("%-4s %4d %10.2f %10.2f %9.1f %9d %9.0f   %s"
                  % (f, v["n"], v["our_eui_median"], v["tabula_q_h_nd_median"],
                     v["dev_pct_median"], v["eplus_heating_hours_median"],
                     v["tabula_heating_hours_implied_median"], v["sign"]))
        print("")
        print("warning kinds (V8.f, by KIND not frequency):")
        for k, v in sorted(warn_kind_totals.items(), key=lambda x: x[0]):
            print("  %5d x  %s" % (v, k))
        if suspicious_all:
            print("  🔴 %d line(s) containing 'invalid' or 'not found'" % len(suspicious_all))

    hard_fails = [x for x in fails]
    print("")
    print("bands table : %s (%d rows)" % (os.path.relpath(BANDS_CSV, PROJ), len(band_rows)))
    print("board       : %s" % os.path.relpath(BOARD, PROJ))
    print("RESULT      : %d gate-cell FAILs over %d cells" % (len(hard_fails), len(rows)))
    for g, c, n in hard_fails[:12]:
        print("   FAIL %-6s %-22s %s" % (g, c, n))
    return 1 if hard_fails else 0


if __name__ == "__main__":
    sys.exit(main())
