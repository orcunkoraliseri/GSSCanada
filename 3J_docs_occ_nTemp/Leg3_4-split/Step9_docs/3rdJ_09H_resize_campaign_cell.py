#!/usr/bin/env python3
"""One cell of the RESIZED campaign: scale the DHW burners by K, re-simulate, re-postprocess.

This is the 56-cell production form of `3rdJ_09H_plant_resize_probe.py`. The probe answered
"does the plant stop mediating the occupancy signal?" and printed tower totals; this script has to
produce a cell directory that the existing §8E aggregator can read as if it were any other arm.

DESIGN DECISION, and the reason it is a post-process of arm H rather than a new injection:
the resize is an edit to the SIMULATION INPUT, not to the occupancy product. Re-running the injector
would re-derive schedules that are already frozen in arm H and risk moving a second variable. So each
cell starts from arm H's own `injected.idf`, changes `Heater Maximum Capacity` and nothing else, and
re-runs. `INJ_HASH` is therefore inherited unchanged, which is the property that makes "resized minus
arm H" a clean one-variable comparison.

WHAT IT REUSES RATHER THAN REIMPLEMENTS:
  * `resize_idf()` from the probe -- so the surgical-edit guard (every declared heater rewritten,
    `Tank Volume` intact) is the same code that has already refused twice in anger.
  * `_do_postprocess()` from the Step-8 probe driver -- so `hourly_meters.csv`, `channel_hourly.csv`,
    `dhw_hourly.csv` and `dhw_volume_hourly.csv` are produced by the campaign's OWN writers, with the
    same channel resolution, the same fuel-closure tripwire and the same unresolved-equipment
    reporting. Writing a second set of extractors here would give the aggregator two sources of truth
    for the quantity the whole exercise is about.

THE MANIFEST is inherited from arm H and then stamped, never invented. `RESIZE_K`, the measured
`PLANT_KW_BASE` / `PLANT_KW_RESIZED` / `PLANT_N_HEATERS`, and `RESIZE_SOURCE_CELL` are added so no
downstream reader can mistake a resized cell for an arm-H cell. `INPUTS_HASH` and `INJ_HASH` are left
exactly as arm H wrote them, because the inputs and the injection genuinely did not change.

`hotel_dT_by_type.csv` (added 2026-08-04) is the per-cell evidence gate `C3'` is scored on. It is
written HERE, in the run, rather than reconstructed later, because the alternative is a second job
re-opening 56 `eplusout.sql` files to recover something the cell already had in memory. The
per-type reduction is IMPORTED from `3rdJ_09H_hotel_dT_decompose.py` (the module H9/H10/H11 were
scored with, job 1172033) instead of retyped, so there is no third copy of the channel-resolution
rules. It carries the same self-check H11 applied: the per-type hotel volume must reproduce the
driver's own `dhwvol_hotel` column to 0.01 %, or the cell REFUSES. A breakdown that does not
reconcile with the driver is not a weaker breakdown, it is a different quantity.

    python 3rdJ_09H_resize_campaign_cell.py <armH_cell_dir> <out_dir> <epw> <K>
"""
import csv
import datetime as _dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.environ.get("REPO", "."))

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from importlib.machinery import SourceFileLoader

RHO_C = 4.184e6
TOL_VOLUME_PCT = 0.01          # same tolerance H11 refused on (job 1172033)


def _energyplus_version_raw(exe):
    """Ask the executable that ACTUALLY ran what it is. Returns '' if it cannot be asked.

    Deliberately non-fatal: a missing version banner must not kill a cell whose simulation already
    succeeded. But it must also never silently leave arm H's build hash in place pretending to be
    this run's -- the caller only overwrites the version fields when this returns something.
    """
    try:
        out = subprocess.run([exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=60).stdout.decode("utf-8", "replace")
    except Exception:
        return ""
    for line in out.splitlines():
        if "EnergyPlus" in line and "Version" in line:
            return line.strip()
    return ""
_DESIGN_F_RE = re.compile(r"([0-9.]+)\s*F\s*$")


def _design_F(target_sched):
    """Design delivery temperature in F, read off the Target Temperature Schedule NAME.

    The schedules are literally named 'Mixed Water At Faucet Temp - 140F' / '- 180F', and the
    target schedule is the causal input that sets the rise -- so it is the right source, not the
    equipment name (which also carries an F token but is a label, not an input). Objects whose
    schedule carries no readable F are reported as None and itemised by the scorer; they are NOT
    defaulted to 140, because 140 is a legitimate measured value and a default that collides with
    a real value is the defect recorded as vacuous-gate #12.
    """
    m = _DESIGN_F_RE.search(str(target_sched or "").strip())
    return float(m.group(1)) if m else None


def _write_hotel_dT_by_type(dec, drv, idf_path, sql_path, idd, outdir):
    """Per-type hotel volume / energy / delivered rise -> hotel_dT_by_type.csv. Evidence for C3'.

    Refuses if the totals do not reconcile with the driver's own hotel volume column.
    """
    hotel, meta = dec.hotel_equipment(idf_path, idd, drv)
    vol = dec.per_object(sql_path, drv.DHW_VOLUME_VARIABLE)
    eng = dec.per_object(sql_path, drv.DHW_VARIABLE)

    rows, skipped = {}, []
    for key in hotel:
        V, E = vol.get(key, 0.0), eng.get(key, 0.0)
        if V <= 0:
            skipped.append(key)
            continue
        t = dec._type_of(key)
        f = _design_F(meta[key]["target"])
        r = rows.setdefault(t, dict(V=0.0, E=0.0, n=0, target=meta[key]["target"], design_F=f))
        if r["design_F"] != f:
            r["design_F"] = "MIXED"     # scorer FAILs on this rather than picking one
        r["V"] += V
        r["E"] += E
        r["n"] += 1
    if not rows:
        raise SystemExit("REFUSING: no hotel WaterUse:Equipment carried volume in %s" % sql_path)

    # H11, per cell. The reference is the driver's own dhwvol_hotel column, written minutes ago by
    # `_do_postprocess` from the same SQL -- an artefact of the run, not a constant I believe.
    ref_csv = os.path.join(outdir, "dhw_volume_hourly.csv")
    if not os.path.isfile(ref_csv):
        raise SystemExit("REFUSING: %s absent -- the per-type breakdown has nothing to reconcile "
                         "against and must not be written unchecked" % ref_csv)
    import pandas as pd
    ref = float(pd.read_csv(ref_csv)["dhwvol_hotel"].sum())
    mine = sum(r["V"] for r in rows.values())
    d = 100.0 * abs(mine - ref) / ref if ref else float("inf")
    if not (d <= TOL_VOLUME_PCT):
        raise SystemExit("REFUSING: per-type hotel volume %.4f m3 disagrees with the driver's "
                         "dhwvol_hotel %.4f m3 by %.5f %% (tol %.2f %%)" % (mine, ref, d,
                                                                            TOL_VOLUME_PCT))

    out_csv = os.path.join(outdir, "hotel_dT_by_type.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["type", "n_objects", "design_F", "volume_m3", "energy_J", "dT_K",
                    "target_schedule"])
        for t, r in sorted(rows.items(), key=lambda kv: -kv[1]["V"]):
            w.writerow([t, r["n"], "" if r["design_F"] is None else r["design_F"],
                        "%.6f" % r["V"], "%.6f" % r["E"],
                        "%.6f" % ((r["E"] / r["V"]) / RHO_C), r["target"]])
    agg = sum(r["E"] for r in rows.values()) / mine / RHO_C
    print("  [OK] hotel_dT_by_type.csv: %d types, V = %.1f m3 (driver %.1f, |d| = %.5f %%), "
          "aggregate dT = %.2f K" % (len(rows), mine, ref, d, agg))
    if skipped:
        print("      %d hotel objects carried zero volume and are not in the table: %s"
              % (len(skipped), skipped[:5]))
    return len(rows), mine, agg


def _load(name, relpath):
    path = os.path.join(os.environ.get("REPO", "."), relpath)
    if not os.path.isfile(path):
        raise SystemExit("REFUSING: cannot find %s at %s" % (name, path))
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: %s <armH_cell_dir> <out_dir> <epw> <K>" % sys.argv[0])
    cell, outdir, epw, K = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    idd = os.environ["EPLUS_IDD"]
    name = os.path.basename(cell.rstrip("/"))
    os.makedirs(outdir, exist_ok=True)

    probe = _load("resize_probe",
                  "3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_plant_resize_probe.py")
    drv = _load("probe_driver",
                "3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_probe_driver.py")
    dec = _load("hotel_dT_decompose",
                "3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_hotel_dT_decompose.py")

    print("=" * 88)
    print("RESIZED CAMPAIGN CELL  %s  K=%.4f" % (name, K))
    print("=" * 88)

    src_idf = os.path.join(cell, "injected.idf")
    src_manifest = os.path.join(cell, "manifest.json")
    for p in (src_idf, src_manifest):
        if not os.path.isfile(p):
            raise SystemExit("REFUSING: arm-H artefact missing: %s" % p)

    # --- 1. surgical resize -------------------------------------------------------------------
    dst_idf = os.path.join(outdir, "injected_resized.idf")
    seen, base_kW, new_kW = probe.resize_idf(src_idf, dst_idf, K)
    n_heaters = len(seen)

    prov = os.path.join(cell, "injected.idf.provenance.txt")
    if os.path.isfile(prov):
        shutil.copy2(prov, os.path.join(outdir, "injected.idf.provenance.txt"))
    else:
        # The elasticity reader establishes `r` from this file and REFUSES without it (the
        # silent-default defect of job 1171812). Losing it here would move that refusal downstream
        # into a script that has no idea why the file is missing.
        raise SystemExit("REFUSING: no provenance beside %s -- r would be unrecoverable" % src_idf)

    # --- 2. re-simulate -----------------------------------------------------------------------
    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    # LOCAL-RUN PORT (2026-08-04, V2-B4). `EPLUS_EXE` names an EnergyPlus binary to call directly,
    # for running this campaign off-cluster. It is DEFAULT-OFF: with the variable unset the
    # singularity branch below is byte-identical to the one arms H and R ran under, so every earlier
    # cell reproduces unchanged. The local binary must be 24.2.0 -- the same version as the SIF --
    # or the resized cells are not comparable to the arm-H cells they are differenced against.
    #
    # A SET-BUT-MISSING `EPLUS_EXE` REFUSES rather than falling back to singularity. A silent
    # fallback would let a mistyped path run the wrong engine (or, off-cluster, fail 56 times with
    # "singularity: not found") and report it as a campaign result. That silent-default shape is the
    # defect recorded at job 1171812 and it is not being reintroduced here.
    local_exe = os.environ.get("EPLUS_EXE", "").strip()
    if local_exe:
        if not os.path.isfile(local_exe):
            raise SystemExit("REFUSING: EPLUS_EXE set but not a file: %s" % local_exe)
        cmd = [local_exe]
        print("  EnergyPlus: local binary %s" % local_exe)
    else:
        wrap = os.path.join(outdir, "energyplus")
        with open(wrap, "w") as f:
            f.write("#!/bin/bash\nsingularity exec --bind /speed-scratch --bind /nfs/speed-scratch "
                    "%s %s \"$@\"\n" % (probe.SIF, probe.SIF_EXE))
        os.chmod(wrap, 0o755)
        cmd = [wrap]
    print("  running EnergyPlus ...")
    rc = subprocess.run(cmd + ["-w", epw, "-d", run_dir, dst_idf],
                        stdout=subprocess.DEVNULL).returncode
    print("  EnergyPlus exit=%d" % rc)
    sql = os.path.join(run_dir, "eplusout.sql")
    if rc != 0 or not os.path.isfile(sql):
        err = os.path.join(run_dir, "eplusout.err")
        if os.path.isfile(err):
            print("".join(open(err, errors="replace").readlines()[-25:]))
        raise SystemExit("REFUSING: EnergyPlus failed for %s -- no cell written" % name)

    # --- 3. post-process with the campaign's OWN writers ---------------------------------------
    with open(src_manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    rows_hourly, rows_channel = drv._do_postprocess(sql, dst_idf, idd, outdir, manifest)
    if rows_hourly <= 0 or rows_channel <= 0:
        raise SystemExit("REFUSING: post-process produced empty CSVs (hourly=%d channel=%d) for %s"
                         % (rows_hourly, rows_channel, name))

    # --- 3b. C3' evidence -----------------------------------------------------------------------
    n_types, hotel_V, hotel_dT = _write_hotel_dT_by_type(dec, drv, dst_idf, sql, idd, outdir)

    # --- 4. stamp provenance so a resized cell can never be read as an arm-H cell ---------------
    manifest["HOTEL_DT_BY_TYPE"] = {"path": os.path.join(outdir, "hotel_dT_by_type.csv"),
                                    "n_types": n_types, "hotel_volume_m3": hotel_V,
                                    "hotel_dT_K": hotel_dT,
                                    "reconciled_against": "dhw_volume_hourly.csv:dhwvol_hotel"}
    manifest["RESIZE_K"] = K
    manifest["PLANT_KW_BASE"] = base_kW
    manifest["PLANT_KW_RESIZED"] = new_kW
    manifest["PLANT_N_HEATERS"] = n_heaters
    manifest["RESIZE_SOURCE_CELL"] = os.path.abspath(cell)
    manifest["RESIZE_NOTE"] = ("Heater Maximum Capacity x K on every WaterHeater:Mixed; tank volume, "
                               "parasitics and loss coefficients untouched. INJ_HASH/INPUTS_HASH "
                               "inherited from arm H because the injection did not change.")

    # --- 4b. RE-STAMP the fields that describe THIS run, not arm H's ----------------------------
    # Defect found 2026-08-04 by the local (win32) port and fixed here. The manifest is inherited
    # wholesale from arm H, which is right for INJ_HASH / INPUTS_HASH (the injection genuinely did
    # not change) but WRONG for anything describing the execution: this script re-runs EnergyPlus,
    # so PLATFORM, the executable, the timestamp and the output directory are properties of the
    # resize run and must be measured, not copied.
    #
    # 🔴 Why it went unseen for eight arms: on Speed the inherited value was `linux` and the actual
    # value was `linux`, so the field was ACCIDENTALLY CORRECT and no gate could distinguish a
    # measured stamp from a copied one. The PLATFORM comparability guard
    # (`Step8_docs/3rdJ_08P_probe_gates.py:202`) reads this field to refuse cross-platform diffs --
    # so before this fix that guard was comparing a value inherited FROM the arm it audits, and
    # could not fail. Running the same code on win32 is what made a copied stamp visibly wrong.
    # This is the catalogue's "gate whose reference comes from the same source it audits" class.
    #
    # Arm H's values are preserved under ARMH_* rather than discarded, so the inheritance is still
    # auditable and nothing that was true of the source run is lost.
    for _k in ("PLATFORM", "engine", "energyplus_exe_used", "energyplus_version",
               "energyplus_version_raw", "energyplus_build", "timestamp_utc", "outdir",
               "ep_return_code"):
        if _k in manifest:
            manifest["ARMH_" + _k] = manifest[_k]
    manifest["PLATFORM"] = sys.platform
    manifest["engine"] = "local"
    manifest["energyplus_exe_used"] = os.path.abspath(cmd[0])
    manifest["outdir"] = os.path.abspath(outdir)
    manifest["timestamp_utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    manifest["ep_return_code"] = rc
    _ver_raw = _energyplus_version_raw(cmd[0])
    if _ver_raw:
        manifest["energyplus_version_raw"] = _ver_raw
        _m = re.search(r"Version\s+([0-9.]+)-([0-9a-f]+)", _ver_raw)
        if _m:
            manifest["energyplus_version"], manifest["energyplus_build"] = _m.group(1), _m.group(2)
    manifest["RESIZE_PROVENANCE_NOTE"] = (
        "PLATFORM/engine/exe/version/timestamp/outdir/ep_return_code describe THIS resize run and "
        "are measured here. The arm-H values they replaced are kept verbatim under ARMH_*. Cells "
        "written before 2026-08-04 carry arm H's execution stamp for all of these fields and must "
        "not be read as evidence of the platform they actually ran on.")
    drv._write_manifest(outdir, manifest)

    print("  [OK] %s : base %.1f kW -> %.1f kW, hourly=%d rows, channel=%d rows"
          % (name, base_kW, new_kW, rows_hourly, rows_channel))
    sys.exit(0)


if __name__ == "__main__":
    main()
