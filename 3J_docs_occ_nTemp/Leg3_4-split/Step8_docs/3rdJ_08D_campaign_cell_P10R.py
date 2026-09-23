"""3rdJ_08D_campaign_cell_P10R.py -- ONE cell of the P10R sibling arm (2026-09-22).

Why a new runner rather than 3rdJ_08D_campaign_driver.py + 3rdJ_09H_resize_campaign_cell.py:
  * the frozen deliverable chain was  driver (inject -> ensure outputs -> EnergyPlus run #1 ->
    post-process)  ->  V2-D9 retail NECB-C converter  ->  V2-D10 per-object resize + EnergyPlus run #2
    (improvements/v2/V2-E5_PREREGISTRATION.md "Method"). Run #1's outputs are never used: the resize
    step reads only arm H's `injected.idf` + `manifest.json`. So the deliverable needs ONE useful
    EnergyPlus run per cell, on `injected_resized.idf`.
  * the driver cannot run unmodified in today's tree: it expects `<repo>/eSim_bem_utils/`, which moved
    to `<repo>/eSim/eSim_bem_utils/`, and it does not take a Step-7 product dir.
This file calls the SAME functions in the same order, and nothing else:
  cells      3rdJ_08D_campaign_cells.build_campaign_cells(REPO, step7_out=outputs_step7_P10R)
  inject     eSim_bem_utils.commercial_integration.inject_mixed_use(..., preserve_load_standby_floor=
             True [P10R scope change, manager 2026-09-22: T9-9 fix ON], lighting_model=None, dhw_model=None)
  outputs    3rdJ_08P_probe_driver._ensure_output_objects
  D9         Step9_docs/3rdJ_09J_retail_necb_c.convert + verify
  D10        Step9_docs/3rdJ_09H_resize_campaign_cell.resolve_equip_spec + 3rdJ_09H_plant_resize_probe.resize_idf
             (K = 1.0, "Laundry Service Water Use 30.6gpm 180F=8.5", V2-G1)
  E+         C:/EnergyPlusV24-2-0/energyplus.exe (24.2.0, build 94a887817b -- the frozen arm's build)
  post       3rdJ_08P_probe_driver._do_postprocess + 3rdJ_09H_resize_campaign_cell._write_hotel_dT_by_type
  manifest   driver fields (INPUTS_HASH via _compute_inputs_hash, INPUTS_HASH_DETAIL, channels_requested,
             arm, EnergyPlus provenance) + the resize stamps + P10R_* fields.
`--no-standby-floor` reproduces the frozen wiring (used ONLY for the static reproduction control).
`--build-only` stops after the IDF is written (no EnergyPlus).

    py -3 3rdJ_08D_campaign_cell_P10R.py --tag B_central__Tall__MTL [--outroot DIR] [--keep-run]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))                   # Step8_docs
LEG3 = os.path.dirname(HERE)
J3 = os.path.dirname(LEG3)
REPO = os.path.dirname(J3)                                           # GSSCanada-main
INJ_ROOT = os.path.join(REPO, "eSim")
S9 = os.path.join(LEG3, "Step9_docs")
STEP7_P10R = os.path.join(LEG3, "Step7_docs", "outputs_step7_P10R")
DEFAULT_OUTROOT = os.path.join(HERE, "campaign_local_P10R")
FROZEN_DIRS = [os.path.join(HERE, d) for d in ("campaign_local_deliverable", "campaign_local_v2", "campaign_local")]
IS_WIN = sys.platform == "win32"
# Windows: the frozen arm's local binary. Linux (Speed): the SIF V3 proved is the same build 24.2.0-94a887817b
# (writing/implementation/IMP/V3_design_and_runs.md); the IDD is the uploaded copy of the Windows one.
EPLUS_EXE = os.environ.get("EPLUS_EXE") or (r"C:\EnergyPlusV24-2-0\energyplus.exe" if IS_WIN else "")
EPLUS_IDD = os.environ.get("EPLUS_IDD") or (r"C:\EnergyPlusV24-2-0\Energy+.idd" if IS_WIN else os.path.join(REPO, "Energy+.idd"))
SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"


def _eplus_cmd(outdir):
    if EPLUS_EXE:
        return [EPLUS_EXE]
    wrap = os.path.join(outdir, "energyplus_sif.sh")
    with open(wrap, "w") as f:
        f.write("#!/bin/bash\nexec singularity exec --bind /speed-scratch --bind /nfs/speed-scratch %s %s \"$@\"\n"
                % (SIF, SIF_EXE))
    os.chmod(wrap, 0o755)
    return [wrap]
RESIZE_K = 1.0
RESIZE_SPEC = "Laundry Service Water Use 30.6gpm 180F=8.5"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cell", type=int)
    g.add_argument("--tag")
    ap.add_argument("--outroot", default=DEFAULT_OUTROOT)
    ap.add_argument("--step7-out", default=STEP7_P10R)
    ap.add_argument("--no-standby-floor", action="store_true", help="CONTROL ONLY: frozen wiring")
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--keep-run", action="store_true", help="keep all of run/ (eplusout.*, ~300 MB)")
    ap.add_argument("--drop-sql", action="store_true", help="also delete run/eplusout.sql (aggregator needs it!)")
    a = ap.parse_args()
    t0 = time.time()

    outroot = os.path.abspath(a.outroot)
    for fd in FROZEN_DIRS:
        if os.path.normcase(outroot) == os.path.normcase(fd) or os.path.normcase(outroot).startswith(os.path.normcase(fd) + os.sep):
            raise SystemExit("REFUSING: --outroot %s is a frozen campaign tree" % outroot)
    os.environ["EPLUS_IDD"] = EPLUS_IDD
    os.environ["REPO"] = REPO

    probe = _load(os.path.join(HERE, "3rdJ_08P_probe_driver.py"), "p10r_probe_driver")
    cells_mod = _load(os.path.join(HERE, "3rdJ_08D_campaign_cells.py"), "p10r_cells")
    # injector resolution guard (same as 3rdJ_08D_campaign_driver.py:153-176, repo layout of today)
    while INJ_ROOT in sys.path:
        sys.path.remove(INJ_ROOT)
    sys.path.insert(0, INJ_ROOT)
    for m in [m for m in list(sys.modules) if m == "eSim_bem_utils" or m.startswith("eSim_bem_utils.")]:
        del sys.modules[m]
    import eSim_bem_utils.commercial_integration as ci
    if os.path.realpath(INJ_ROOT) not in os.path.realpath(ci.__file__):
        raise SystemExit("REFUSING: injector resolved outside %s: %s" % (INJ_ROOT, ci.__file__))
    d9 = _load(os.path.join(S9, "3rdJ_09J_retail_necb_c.py"), "p10r_d9")
    rprobe = _load(os.path.join(S9, "3rdJ_09H_plant_resize_probe.py"), "p10r_resize_probe")
    topo = _load(os.path.join(S9, "3rdJ_09H_dhw_plant_topology.py"), "p10r_topo")
    rcell = _load(os.path.join(S9, "3rdJ_09H_resize_campaign_cell.py"), "p10r_resize_cell")
    dec = _load(os.path.join(S9, "3rdJ_09H_hotel_dT_decompose.py"), "p10r_hotel_dT")

    cells = cells_mod.build_campaign_cells(REPO, step7_out=os.path.abspath(a.step7_out))
    if a.tag:
        hit = [c for c in cells if c["tag"] == a.tag]
        if len(hit) != 1:
            raise SystemExit("REFUSING: tag %r matched %d cells" % (a.tag, len(hit)))
        cell = hit[0]
    else:
        cell = cells[a.cell]
    tag = cell["tag"]
    if cell["missing_inputs"]:
        raise SystemExit("REFUSING: %s missing inputs %s" % (tag, cell["missing_inputs"]))
    outdir = os.path.join(outroot, tag)
    standby = not a.no_standby_floor

    inputs_hash, inputs_detail = probe._compute_inputs_hash(cell["channels"])
    code_md5 = {k: probe.md5_file(p) for k, p in (
        ("commercial_integration.py", ci.__file__),
        ("3rdJ_08P_probe_driver.py", os.path.join(HERE, "3rdJ_08P_probe_driver.py")),
        ("3rdJ_08D_campaign_cells.py", os.path.join(HERE, "3rdJ_08D_campaign_cells.py")),
        ("3rdJ_08D_campaign_cell_P10R.py", os.path.abspath(__file__)),
        ("3rdJ_09J_retail_necb_c.py", os.path.join(S9, "3rdJ_09J_retail_necb_c.py")),
        ("3rdJ_09H_plant_resize_probe.py", os.path.join(S9, "3rdJ_09H_plant_resize_probe.py")),
        ("3rdJ_09H_resize_campaign_cell.py", os.path.join(S9, "3rdJ_09H_resize_campaign_cell.py")),
        ("3rdJ_09H_dhw_plant_topology.py", os.path.join(S9, "3rdJ_09H_dhw_plant_topology.py")))}
    inj_hash = code_md5["commercial_integration.py"][:8]

    man_path = os.path.join(outdir, "manifest.json")
    if os.path.isfile(man_path) and not a.build_only:
        old = json.load(open(man_path, encoding="utf-8"))
        if old.get("P10R_STATUS") == "ok" and old.get("INPUTS_HASH") == inputs_hash \
                and old.get("arm", {}).get("preserve_load_standby_floor") == standby:
            print("[resume-skip] %s already complete (INPUTS_HASH %s)" % (tag, inputs_hash))
            sys.exit(0)
        stale = outdir + "_STALE_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        os.rename(outdir, stale)
        print("[archive] incomplete/stale %s -> %s" % (outdir, stale))
    os.makedirs(outdir, exist_ok=True)

    print("[P10R] cell=%d tag=%s scenario=%s INJ_HASH=%s INPUTS_HASH=%s" % (
        cell["cell_index"], tag, cell["scenario"], inj_hash, inputs_hash))
    print("[arm] preserve_load_standby_floor=%s lighting_model=None dhw_model=None  (P10R cell %s)" % (standby, tag))
    for ch, cfg in sorted(cell["channels"].items()):
        print("[channel] %-11s %s" % (ch, cfg.get("csv")))

    # ---- 1. inject ------------------------------------------------------------------------------
    pre = os.path.join(outdir, "injected.idf")
    meta = {"building": cell["building"], "city": cell["city"], "cz": cell["cz"], "purpose": "campaign_P10R",
            "cell_index": cell["cell_index"], "scenario_label": tag}
    inj_result = ci.inject_mixed_use(cell["idf"], pre, cell["channels"], meta, verbose=True,
                                     preserve_load_standby_floor=standby, lighting_model=None, dhw_model=None)
    fallback = sorted(set(inj_result.get("fallback", [])))
    for ch in fallback:
        print("!!! FALLBACK: %s reverted to NECB baseline !!!" % ch)
    from eppy.modeleditor import IDF
    IDF.setiddname(EPLUS_IDD)
    idf = IDF(pre)
    probe._ensure_output_objects(idf, verbose=True)
    idf.saveas(pre)
    pre_md5 = probe.md5_file(pre)

    # ---- 2. V2-D9 retail NECB-C -------------------------------------------------------------------
    d9_idf = os.path.join(outdir, "injected_d9.idf")
    rep, n_swap = d9.convert(pre, d9_idf, True, True)
    if not d9.verify(pre, d9_idf, True, True, n_swap):
        raise SystemExit("REFUSING: V2-D9 verify failed for %s" % tag)
    print("[D9] retail NECB-C: %d schedule swap(s), verify OK" % n_swap)

    # ---- 3. V2-D10 per-object DHW resize ----------------------------------------------------------
    final = os.path.join(outdir, "injected_resized.idf")
    per_object, spec_report = rcell.resolve_equip_spec(RESIZE_SPEC, d9_idf, topo)
    seen, base_kW, new_kW = rprobe.resize_idf(d9_idf, final, RESIZE_K, per_object or None)
    print("[D10] plant %.1f kW -> %.1f kW (%d heaters)" % (base_kW, new_kW, len(seen)))
    build_s = time.time() - t0

    manifest = {
        "cell_index": cell["cell_index"], "cell_tag": tag, "scenario_label": tag, "scenario": cell["scenario"],
        "building": cell["building"], "city": cell["city"], "cz": cell["cz"],
        "INJ_HASH": inj_hash, "INPUTS_HASH": inputs_hash, "INPUTS_HASH_DETAIL": inputs_detail,
        "campaign_driver": "3rdJ_08D_campaign_cell_P10R.py", "outdir": outdir,
        "channels_requested": {ch: {"csv_path": cfg.get("csv"), "csv_md5": probe.md5_file(cfg["csv"]),
                                    "exists": True, **{k: v for k, v in cfg.items() if k != "csv"}}
                               for ch, cfg in cell["channels"].items()},
        "smoke_days": None, "expected_rows": 8760,
        "arm": {"preserve_load_standby_floor": standby, "lighting_model": None, "dhw_model": None},
        "inject_mixed_use_result": inj_result, "FALLBACK_LOUD": fallback, "injected_idf_md5": pre_md5,
        "D9_schedule_swaps": n_swap,
        "RESIZE_K": RESIZE_K, "PLANT_KW_BASE": base_kW, "PLANT_KW_RESIZED": new_kW, "PLANT_N_HEATERS": len(seen),
        "RESIZE_MODE": "per_object" if per_object else "scalar", "RESIZE_EQUIP_SPEC": RESIZE_SPEC,
        "RESIZE_PER_OBJECT": per_object,
        "RESIZE_SPEC_RESOLUTION": [{"equipment": e, "loop": l, "heaters": h, "factor": f} for e, l, h, f in spec_report],
        "injected_resized_idf_md5": probe.md5_file(final),
        "P10R_CODE_MD5": code_md5, "P10R_STEP7_OUT": os.path.abspath(a.step7_out),
        "P10R_NOTE": "P10R sibling arm (writing/implementation/IMP/P10R_fix.md): frame-fixed products + T9-9 "
                     "standby floor; chain = inject -> ensure outputs -> D9 -> D10 -> ONE EnergyPlus run.",
    }
    if "hotel_deliberately_absent" in cell:
        manifest["hotel_deliberately_absent"] = cell["hotel_deliberately_absent"]
    for p in (pre, d9_idf):
        pass
    if a.build_only:
        manifest["P10R_STATUS"] = "build_only"
        probe._write_manifest(outdir, manifest)
        print("[build-only] %s -> %s (%.0f s)" % (tag, final, build_s))
        sys.exit(0)

    # ---- 4. EnergyPlus (one run) ------------------------------------------------------------------
    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    manifest.update(probe._energyplus_provenance("local"))
    cmd = _eplus_cmd(outdir)
    ver = subprocess.run(cmd + ["--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True).stdout.strip()
    manifest["PLATFORM"] = sys.platform
    manifest["energyplus_exe_used"] = cmd[0]
    manifest["energyplus_version_raw"] = ver.splitlines()[-1] if ver else ""
    print("[sim] %s | %s" % (cmd[0], manifest["energyplus_version_raw"]))
    t_ep = time.time()
    rc = subprocess.run(cmd + ["-w", cell["epw"], "-d", run_dir, final], stdout=subprocess.DEVNULL).returncode
    ep_s = time.time() - t_ep
    manifest["ep_return_code"] = rc
    print("[sim] EnergyPlus exit=%d (%.0f s)" % (rc, ep_s))
    sql = os.path.join(run_dir, "eplusout.sql")
    if rc != 0 or not os.path.isfile(sql):
        manifest["P10R_STATUS"] = "FAILED_EPLUS"
        probe._write_manifest(outdir, manifest)
        raise SystemExit("REFUSING: EnergyPlus failed for %s" % tag)

    # ---- 5. post-process (campaign's own writers) -------------------------------------------------
    rows_h, rows_c = probe._do_postprocess(sql, final, EPLUS_IDD, outdir, manifest)
    # every frozen deliverable cell carries hotel_dT_by_type.csv (the resize step wrote it unconditionally)
    n_types, hotel_V, hotel_dT = rcell._write_hotel_dT_by_type(dec, probe, final, sql, EPLUS_IDD, outdir)
    manifest["HOTEL_DT_BY_TYPE"] = {"n_types": n_types, "hotel_volume_m3": hotel_V, "hotel_dT_K": hotel_dT}
    status, why = "ok", []
    if rows_h != 8760 or rows_c != 8760:
        status, why = "FAILED_ROWS", why + ["rows hourly=%d channel=%d" % (rows_h, rows_c)]
    for gate in ("fuel_closure", "channel_closure"):
        for key, r in (manifest.get(gate) or {}).items():
            if isinstance(r, dict) and not r.get("closed", False):
                status, why = "FAILED_CLOSURE", why + ["%s[%s]" % (gate, key)]
    manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["sql_extraction_method"] = probe.SQL_EXTRACTION_METHOD
    manifest["P10R_TIMING_S"] = {"build": round(build_s, 1), "energyplus": round(ep_s, 1),
                                 "total": round(time.time() - t0, 1)}
    manifest["P10R_STATUS"] = status
    if why:
        manifest["P10R_FAIL_REASONS"] = why
    probe._write_manifest(outdir, manifest)
    # keep what the frozen deliverable keeps; drop the intermediates and (unless asked) run/
    for p in (pre, d9_idf):
        if os.path.isfile(p):
            os.remove(p)
    # the Step-8E aggregator reads run/eplusout.sql, so it is KEPT (with eplusout.err); the rest of run/
    # (eso, mtr, csv, ...) is dropped unless --keep-run. --drop-sql removes the sql too (only after aggregation).
    if not a.keep_run and status == "ok":
        for fn in os.listdir(run_dir):
            if fn in ("eplusout.sql", "eplusout.err") and not a.drop_sql:
                continue
            fp = os.path.join(run_dir, fn)
            if os.path.isfile(fp):
                os.remove(fp)
            else:
                shutil.rmtree(fp, ignore_errors=True)
    print("[done] %s status=%s total %.0f s (build %.0f, EnergyPlus %.0f)" % (tag, status, time.time() - t0, build_s, ep_s))
    sys.exit(0 if status == "ok" else 1)


if __name__ == "__main__":
    main()
