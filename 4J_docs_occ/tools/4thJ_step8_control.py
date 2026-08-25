# -*- coding: utf-8 -*-
"""4J Step 8 WORK ITEM 8.3 --- THE UNINJECTED CONTROL CAMPAIGN.  It runs FIRST.

    "The single most expensive lesson of 3J.  The office EUI gate failed, and
     eight simulation campaigns were spent before it was traced out of the
     occupancy model entirely: the uninjected control run, with no schedules
     applied at all, already sat below the band floor --- 85.45 against a floor
     of 100.  A gate that no untreated control can pass is measuring the band,
     not the model."

WHAT "UNINJECTED" MEANS HERE, EXACTLY
-------------------------------------
It is NOT a separately built model.  `D-S8-2` item 5 (ruled (c), pre-registered)
put the control INSIDE the sweep:

    phi_int(t) = (1 - f) * 3.0  +  f * 3.0 * g(t) / mean_year(g(t))

and `f = 0` is the control --- a flat 3.0 W/m2, which is exactly what TABULA's
`EU.SUH`/`EU.MUH` boundary condition specifies and exactly what the 8.1 IDFs
already contain (`OtherEquipment E_PHI_INT` on `SCH_ALWAYS_ON`).  So the control
is the 88 archetype IDFs as built, run on their fold's EPW, with no Step 7
schedule anywhere.  That removes the "the control was constructed differently"
objection outright, and it is why this tool writes no IDF: writing one would
re-introduce the objection it was designed out of.

TWO RUNS PER CELL, AND THE SECOND ONE IS NOT A WASTE
-----------------------------------------------------
`D-S8-1` was ruled (a): `G8.1`-`G8.4` are REPRODUCIBILITY gates, reference = a
re-run of the same cell, thresholds unmoved.  A reference that does not exist
cannot be scored, so this tool MAKES it exist: every cell is run twice, the
second time

  * from a fresh process,
  * into a different output directory,
  * with a different working directory,
  * from a freshly copied IDF,

so that the comparison can catch stale-output reuse and path-dependent
behaviour, which is the defect class `D-S8-1`(a) named.  🔴 A clean re-run is
expected to read EXACTLY zero on all four gates.  That is not a hidden failure
of the gate --- it is what a deterministic engine does, and it is stated in the
scorer's own output so that nobody reads "NMBE = 0.000 %" as an accuracy claim.
The gates earn their keep by being SEEN FAILING, which is the selftest's job.

WHAT IS MEASURED AT RUN TIME AND NEVER INHERITED
-------------------------------------------------
`G8.14` and the 3J precedent behind it ("an inherited PLATFORM field was
accidentally correct on the only platform ever run, and 112 manifests claimed a
value nothing had measured"):

  * the EnergyPlus version AND build hash are parsed out of each cell's OWN
    `eplusout.err` first line, per cell, never copied from a sibling;
  * the platform is read from `platform`/`os` inside this process;
  * the md5 of the EnergyPlus executable itself is recorded once, in the
    campaign header, so a silently upgraded engine is visible;
  * `fold` is written explicitly into every manifest (`V8.g`) even though no
    schedule exists yet, so that 8.5's `G8.16` has a field to check and cannot
    find "zero violations" over a field that is absent.

WHAT IS DELIBERATELY NOT DONE HERE
-----------------------------------
  * No band is moved.  Where the control lands relative to a band is an OUTPUT
    of this campaign, and `G8.0` says a band the control fails is reported as a
    band-applicability limitation.
  * No schedule, no `f > 0`, no scenario --- that is 8.5, and 8.4's two probes
    come between.
  * Nothing is deleted from `outputs_step8`; the campaign writes only under
    `outputs_step8/control/`.

Outputs
-------
  control/<cell>/            in.idf, eplustbl.csv, eplusout.{eio,err,end},
                             series_hourly.csv, manifest.json
  control/_rerun/<cell>/     series_hourly.csv, eplusout.{err,end}
  control_campaign.json      the campaign header + the declared cell count (V8.a)
  control_annual.csv         ONE row per cell --- the single table the scorer and
                             the gates both consume (V8.b)
  control_monthly.csv        88 x 12 rows
"""
import csv
import datetime
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
CONTROL = os.path.join(BASE, "control")
RERUN = os.path.join(CONTROL, "_rerun")
EPLUS = r"C:\EnergyPlusV24-2-0\energyplus.exe"

IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
CAMPAIGN = os.path.join(BASE, "control_campaign.json")
ANNUAL = os.path.join(BASE, "control_annual.csv")
MONTHLY = os.path.join(BASE, "control_monthly.csv")

GJ_TO_KWH = 1000.0 / 3.6            # 1 GJ = 277.7778 kWh
J_TO_KWH = 1.0 / 3.6e6

KEEP = ("eplustbl.csv", "eplusout.eio", "eplusout.err", "eplusout.end")
KEEP_RERUN = ("eplusout.err", "eplusout.end")

HOURLY_VAR = "Zone Ideal Loads Supply Air Total Heating Energy"
MONTHLY_VAR = "Zone Ideal Loads Zone Total Heating Energy"
TEMP_VAR = "Zone Mean Air Temperature"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# reading what EnergyPlus wrote, never what we told it to write
# --------------------------------------------------------------------------

def engine_from_err(err_path):
    """Version and build hash out of the run's OWN error file.

    First line is e.g.
        Program Version,EnergyPlus, Version 24.2.0-94a887817b, YMD=...
    """
    with io.open(err_path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
    ver = build = None
    for tok in first.split(","):
        tok = tok.strip()
        if tok.startswith("Version "):
            v = tok[len("Version "):].strip()
            if "-" in v:
                ver, build = v.split("-", 1)
            else:
                ver = v
    return ver, build


def err_counts(err_path):
    """Severe/warning counts and the warning KINDS (V8.f: by kind, not frequency)."""
    sev = warn = 0
    kinds = {}
    fatal = False
    with io.open(err_path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            s = ln.strip()
            if s.startswith("** Severe  **") or s.startswith("**  Fatal  **"):
                sev += 1
                if s.startswith("**  Fatal  **"):
                    fatal = True
                k = s.split("**", 2)[-1].strip()[:90]
                kinds[k] = kinds.get(k, 0) + 1
            elif s.startswith("** Warning **"):
                warn += 1
                k = s.split("**", 2)[-1].strip()[:90]
                kinds[k] = kinds.get(k, 0) + 1
    return sev, warn, fatal, kinds


def zone_floor_area(eio_path):
    """Floor area E+ ITSELF computed from the geometry (V8.d).

    Read from this cell's own eplusout.eio, never carried across geometries and
    never taken from the manifest column that claims it.
    """
    hdr = None
    for ln in io.open(eio_path, encoding="utf-8", errors="replace"):
        if ln.startswith("! <Zone Information>"):
            hdr = [x.strip() for x in ln.split(",")]
        elif ln.startswith(" Zone Information,") and hdr:
            f = [x.strip() for x in ln.split(",")]
            try:
                j = hdr.index("Floor Area {m2}")
            except ValueError:
                return None, None, None
            try:
                k = hdr.index("Exterior Gross Wall Area {m2}")
                m = hdr.index("Exterior Window Area {m2}")
                return float(f[j]), float(f[k]), float(f[m])
            except (ValueError, IndexError):
                return float(f[j]), None, None
    return None, None, None


def site_location(eio_path):
    for ln in io.open(eio_path, encoding="utf-8", errors="replace"):
        if ln.startswith("Site:Location,"):
            return ln.strip()
    return None


def end_uses(tbl_path):
    """The End Uses table: {fuel: {end use: GJ}} plus the reported total row."""
    rows = list(csv.reader(io.open(tbl_path, encoding="utf-8", errors="replace")))
    for i, r in enumerate(rows):
        if len(r) == 1 and r[0].strip() == "End Uses":
            hdr = None
            for j in range(i + 1, min(i + 5, len(rows))):
                if len(rows[j]) > 3 and rows[j][0] == "" and rows[j][1] == "":
                    hdr = [c.strip() for c in rows[j]]
                    break
            if hdr is None:
                return None, None
            uses, total = {}, {}
            start = None
            for j in range(i + 1, min(i + 6, len(rows))):
                if [c.strip() for c in rows[j]] == hdr:
                    start = j + 1
                    break
            if start is None:
                return None, None
            for j in range(start, len(rows)):
                r2 = rows[j]
                if len(r2) < 3 or not r2[1].strip():
                    # blank spacer row sits between the end uses and the total;
                    # skipping it rather than breaking is the difference between
                    # reading the total row and silently returning {}
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


def read_series(csv_path):
    """Hourly heating [J], hourly zone temperature [C], and E+'s OWN monthly column.

    Returns (hourly_j, temps, monthly_var_j, requested_ok) where requested_ok
    lists which of the three requested variables actually appear as columns ---
    G8.11's real question, asked of the output rather than of the input.
    """
    fh = io.open(csv_path, encoding="utf-8", errors="replace")
    rdr = csv.reader(fh)
    hdr = next(rdr)
    ci_h = ci_t = ci_m = None
    for i, c in enumerate(hdr):
        if HOURLY_VAR in c and "(Hourly)" in c:
            ci_h = i
        elif TEMP_VAR in c and "(Hourly)" in c:
            ci_t = i
        elif MONTHLY_VAR in c and "(Monthly)" in c:
            ci_m = i
    present = {HOURLY_VAR: ci_h is not None, TEMP_VAR: ci_t is not None,
               MONTHLY_VAR: ci_m is not None}
    hourly, temps, months, monthly_var = [], [], [], []
    for row in rdr:
        if not row or not row[0].strip():
            continue
        stamp = row[0].strip()
        if ci_h is not None and ci_h < len(row) and row[ci_h].strip():
            try:
                hourly.append(float(row[ci_h]))
            except ValueError:
                continue
            try:
                months.append(int(stamp.split("/")[0]))
            except ValueError:
                months.append(0)
            if ci_t is not None and ci_t < len(row):
                try:
                    temps.append(float(row[ci_t]))
                except ValueError:
                    temps.append(float("nan"))
        if ci_m is not None and ci_m < len(row) and row[ci_m].strip():
            try:
                monthly_var.append(float(row[ci_m]))
            except ValueError:
                pass
    fh.close()
    return hourly, temps, months, monthly_var, present


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------

def run_cell(idf_src, epw, outdir, cwd):
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    dst = os.path.join(outdir, "in.idf")
    shutil.copy(idf_src, dst)
    t0 = time.time()
    started = utcnow()
    p = subprocess.run([EPLUS, "-w", epw, "-d", outdir, "-r", dst],
                       cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    return {"returncode": p.returncode, "wall_s": round(wall, 3),
            "started_utc": started, "finished_utc": utcnow(),
            "stdout_tail": p.stdout.decode("utf-8", "replace")[-400:]}


def main():
    limit = None
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
    if not os.path.exists(EPLUS):
        sys.exit("EnergyPlus not found at %s" % EPLUS)

    arch = list(csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8")))
    wx = {r["fold"]: r for r in csv.DictReader(io.open(WX_MANIFEST, encoding="utf-8"))}
    if len(wx) != 3:
        sys.exit("weather manifest declares %d folds, expected 3" % len(wx))
    if limit:
        arch = arch[:limit]

    for d in (CONTROL, RERUN):
        if not os.path.isdir(d):
            os.makedirs(d)

    plat = {"platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "node": platform.node(),
            "python": platform.python_version(), "cpu_count": os.cpu_count(),
            "measured_at_run_time": True}
    header = {
        "campaign": "step8_control_uninjected",
        "work_item": "8.3",
        "gate": "G8.0",
        "decision_basis": ["D-S8-2 item 5 (c): f = 0 is an endpoint of the pre-registered sweep",
                           "D-S8-1 (a): G8.1-G8.4 reference = a re-run of the same cell",
                           "D-S8-4: TMYx.2009-2023, one station per fold"],
        "f": 0.0,
        "phi_int_w_m2": 3.0,
        "schedules_applied": False,
        "declared_cells": len(arch),
        "runs_per_cell": 2,
        "energyplus_exe": EPLUS,
        "energyplus_exe_md5": md5(EPLUS),
        "platform": plat,
        "started_utc": utcnow(),
    }

    annual_rows, monthly_rows = [], []
    t_start = time.time()
    for n, a in enumerate(arch, 1):
        cell = os.path.splitext(a["idf"])[0]
        fold = a["fold"]
        w = wx[fold]
        epw = os.path.join(WEATHER, w["epw"])
        idf_src = os.path.join(ARCH, a["idf"])
        if not os.path.exists(idf_src):
            sys.exit("missing IDF %s" % idf_src)
        if not os.path.exists(epw):
            sys.exit("missing EPW %s" % epw)

        # --- primary run -------------------------------------------------
        outdir = os.path.join(CONTROL, cell)
        r1 = run_cell(idf_src, epw, outdir, CONTROL)
        errp = os.path.join(outdir, "eplusout.err")
        if r1["returncode"] != 0 or not os.path.exists(errp):
            sys.exit("cell %s failed: rc=%s\n%s" % (cell, r1["returncode"], r1["stdout_tail"]))
        ver, build = engine_from_err(errp)
        sev, warn, fatal, kinds = err_counts(errp)
        area, wall_area, win_area = zone_floor_area(os.path.join(outdir, "eplusout.eio"))
        loc = site_location(os.path.join(outdir, "eplusout.eio"))
        uses, total = end_uses(os.path.join(outdir, "eplustbl.csv"))
        eplus_csv = os.path.join(outdir, "eplusout.csv")
        hourly, temps, months, monthly_var, present = read_series(eplus_csv)
        raw_csv_md5 = md5(eplus_csv)

        # --- reproducibility re-run: fresh process, different dirs -------
        rrdir = os.path.join(RERUN, cell)
        r2 = run_cell(idf_src, epw, rrdir, RERUN)
        errp2 = os.path.join(rrdir, "eplusout.err")
        if r2["returncode"] != 0 or not os.path.exists(errp2):
            sys.exit("cell %s RE-RUN failed: rc=%s" % (cell, r2["returncode"]))
        ver2, build2 = engine_from_err(errp2)
        sev2, warn2, _f2, _k2 = err_counts(errp2)
        h2, t2, m2, mv2, present2 = read_series(os.path.join(rrdir, "eplusout.csv"))
        raw_csv_md5_rerun = md5(os.path.join(rrdir, "eplusout.csv"))

        # --- derived, on the reference area TABULA divides by ------------
        a_ref = float(a["a_ref"])
        n_storey = float(a["n_storey"])
        heat_j = sum(hourly)
        eui = heat_j * J_TO_KWH / a_ref
        heat_gj_tbl = None
        if uses:
            for fuel, v in (uses.get("Heating") or {}).items():
                if v:
                    heat_gj_tbl = (heat_gj_tbl or 0.0) + v
        peak_w = max(hourly) / 3600.0 if hourly else 0.0
        peak_i = hourly.index(max(hourly)) if hourly else -1
        hours_on = sum(1 for x in hourly if x > 0.0)
        mon = [0.0] * 12
        for x, m in zip(hourly, months):
            if 1 <= m <= 12:
                mon[m - 1] += x
        mon2 = [0.0] * 12
        for x, m in zip(h2, m2):
            if 1 <= m <= 12:
                mon2[m - 1] += x

        def write_series(path, hh, tt):
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                wtr = csv.writer(fh)
                wtr.writerow(["hour", "month", "heating_j", "zone_temp_c"])
                for i, x in enumerate(hh):
                    wtr.writerow([i, months[i] if i < len(months) else "",
                                  "%.6f" % x,
                                  "%.4f" % tt[i] if i < len(tt) else ""])
        write_series(os.path.join(outdir, "series_hourly.csv"), hourly, temps)
        write_series(os.path.join(rrdir, "series_hourly.csv"), h2, t2)

        man = {
            "cell": cell,
            "campaign": "step8_control_uninjected",
            "work_item": "8.3",
            "fold": fold,                       # V8.g
            "code": a["code"],
            "cls": a["cls"],
            "cell_period": a["cell_period"],
            "schedule_file": None,              # the control HAS no Step 7 schedule
            "schedule_md5": None,
            "schedule_fold": None,
            "f": 0.0,
            "phi_int_w_m2": 3.0,
            "injection": "none (f = 0, TABULA phi_int held flat and constant)",
            "idf": a["idf"],
            "idf_md5_manifest": a["idf_md5"],
            "idf_md5_measured": md5(os.path.join(outdir, "in.idf")),
            "weather_epw": w["epw"],
            "weather_md5": w["epw_md5"],
            "weather_base_period": w["base_period"],
            "weather_station": w["station"],
            "weather_wmo": w["wmo"],
            "energyplus_version": ver,
            "energyplus_build": build,
            "energyplus_exe_md5": header["energyplus_exe_md5"],
            "platform": plat,
            "site_location_line": loc,
            "run": dict(r1, severe=sev, warnings=warn, fatal=fatal,
                        warning_kinds=kinds, eplusout_csv_md5=raw_csv_md5,
                        variables_delivered=present),
            "rerun": dict(r2, severe=sev2, warnings=warn2,
                          energyplus_version=ver2, energyplus_build=build2,
                          eplusout_csv_md5=raw_csv_md5_rerun,
                          variables_delivered=present2),
            "geometry_measured_from_eio": {
                "zone_floor_area_m2": area,
                "exterior_gross_wall_area_m2": wall_area,
                "exterior_window_area_m2": win_area,
                "n_storey_manifest": n_storey,
                "a_ref_implied": (area * n_storey) if area else None,
                "a_ref_manifest": a_ref,
            },
            "results": {
                "heating_j": heat_j,
                "heating_gj_eplustbl": heat_gj_tbl,
                "eui_kwh_m2a": eui,
                "peak_heating_w": peak_w,
                "peak_hour_index": peak_i,
                "hours_heating_on": hours_on,
                "monthly_j": mon,
                "monthly_var_j": monthly_var,
                "end_uses_total_gj": total,
            },
            "rerun_results": {
                "heating_j": sum(h2),
                "peak_heating_w": (max(h2) / 3600.0) if h2 else 0.0,
                "peak_hour_index": h2.index(max(h2)) if h2 else -1,
                "monthly_j": mon2,
                "monthly_var_j": mv2,
            },
            "written_utc": utcnow(),
        }
        with io.open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(man, indent=1, sort_keys=True))

        for f in os.listdir(outdir):
            if f not in KEEP and f not in ("in.idf", "series_hourly.csv", "manifest.json"):
                os.remove(os.path.join(outdir, f))
        for f in os.listdir(rrdir):
            if f not in KEEP_RERUN and f not in ("series_hourly.csv",):
                os.remove(os.path.join(rrdir, f))

        annual_rows.append({
            "cell": cell, "fold": fold, "code": a["code"], "cls": a["cls"],
            "cell_period": a["cell_period"],
            "a_ref_m2": a_ref, "n_storey": a["n_storey"],
            "zone_floor_area_eio_m2": area,
            "heating_j": "%.6f" % heat_j,
            "heating_gj_eplustbl": "" if heat_gj_tbl is None else "%.4f" % heat_gj_tbl,
            "eui_kwh_m2a": "%.6f" % eui,
            "peak_heating_w": "%.6f" % peak_w,
            "peak_w_m2": "%.6f" % (peak_w / a_ref),
            "peak_hour_index": peak_i,
            "hours_heating_on": hours_on,
            "severe": sev, "warnings": warn,
            "rerun_heating_j": "%.6f" % sum(h2),
            "rerun_peak_heating_w": "%.6f" % ((max(h2) / 3600.0) if h2 else 0.0),
            "rerun_peak_hour_index": h2.index(max(h2)) if h2 else -1,
            "epw": w["epw"], "epw_md5": w["epw_md5"],
            "idf_md5": a["idf_md5"],
            "eplus_version": ver, "eplus_build": build,
        })
        for i in range(12):
            monthly_rows.append({"cell": cell, "fold": fold, "month": i + 1,
                                 "heating_j": "%.6f" % mon[i],
                                 "rerun_heating_j": "%.6f" % mon2[i],
                                 "heating_var_j": ("%.6f" % monthly_var[i]
                                                   if i < len(monthly_var) else "")})

        if n % 10 == 0 or n == len(arch):
            print("  %3d/%d  %-22s eui %8.2f kWh/(m2.a)  peak %7.2f W/m2  %s"
                  % (n, len(arch), cell, eui, peak_w / a_ref,
                     "severe=%d" % sev if sev else "clean"))

    header["finished_utc"] = utcnow()
    header["wall_s"] = round(time.time() - t_start, 1)
    header["cells_written"] = len(annual_rows)
    with io.open(CAMPAIGN, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header, indent=1, sort_keys=True))

    with io.open(ANNUAL, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(annual_rows[0].keys()))
        w.writeheader()
        for r in annual_rows:
            w.writerow(r)
    with io.open(MONTHLY, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(monthly_rows[0].keys()))
        w.writeheader()
        for r in monthly_rows:
            w.writerow(r)

    print("\ncells        : %d declared, %d written" % (header["declared_cells"], len(annual_rows)))
    print("runs         : %d (2 per cell: primary + independent re-run)" % (2 * len(annual_rows)))
    print("wall         : %.1f s" % header["wall_s"])
    print("engine       : EnergyPlus %s build %s  exe md5 %s"
          % (annual_rows[0]["eplus_version"], annual_rows[0]["eplus_build"],
             header["energyplus_exe_md5"][:12]))
    for f in ("es", "uk", "it"):
        sel = [float(r["eui_kwh_m2a"]) for r in annual_rows if r["fold"] == f]
        if sel:
            sel.sort()
            print("  %-3s n=%2d  EUI kWh/(m2.a)  min %7.2f  median %7.2f  max %7.2f"
                  % (f, len(sel), sel[0], sel[len(sel) // 2], sel[-1]))


if __name__ == "__main__":
    main()
