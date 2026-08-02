"""3rdJ_08D_campaign_driver.py -- Step 8 (3J Leg-3 4-split): CAMPAIGN cell runner (56 runs).

Runs ONE campaign cell out of the 56-cell table (3rdJ_08D_campaign_cells.py::build_campaign_cells,
2 buildings x 2 cities x 14 scenarios, 3rdJ_08_simulation_4split.md:44). Strictly additive:
3rdJ_08P_probe_driver.py (the 7-cell §P probe harness) is NOT modified by this file -- its
inject -> ensure-outputs -> simulate -> postprocess -> manifest mechanics are REUSED by loading
it as a module (importlib, same trick 3rdJ_08P_probes_local.py already uses for
_build_cells/_compute_inputs_hash -- the filename starts with a digit so `import` doesn't work),
never duplicated. This is the concrete proof the campaign is additive: `py -3
3rdJ_08P_probes_local.py --dry-run` still runs unchanged (see Progress Log).

Reused verbatim from the probe driver module: md5_file, _compute_inputs_hash,
_check_inputs_hash_guard, _archive_stale_dir, _ensure_output_objects, _do_postprocess,
_energyplus_provenance, _write_manifest, SQL_EXTRACTION_METHOD, REQUIRED_METERS,
REQUIRED_VARIABLES. NOT reused (campaign-specific): the cell table (7-cell CELLS vs. the 56-cell
build_campaign_cells), and the IDF/EPW paths (probe driver hardcodes SuperTall/MTL only; the
campaign varies building AND city).

Residential (OD-8R-L3, `channels["residential"]`) is now IN for cells whose scenario has a
residential product (2026-07-28 fix -- see 3rdJ_08D_campaign_cells.py module docstring "2026-07-28
FIX" note): this file builds no channel config itself, it merely passes `cell["channels"]`
straight through to `inject_mixed_use()` (below), so the residential channel arrives automatically
once `3rdJ_08D_campaign_cells.py::build_campaign_cells()` wires it in -- this file needed no
change for that. The probe harness (3rdJ_08P_probe_driver.py, 7 cells, reused here for its
inject/simulate/postprocess mechanics only) is untouched and still residential-OUT; that scope
boundary applies to the probe harness, not to the campaign driver.

--smoke-days N (NEW, campaign-driver-only): truncates the injected IDF's RunPeriod to the first
N days of the year (instead of the full year _ensure_output_objects() would otherwise force),
for a short end-to-end smoke test. Expected row count becomes N*24 instead of 8760 -- the row-
count gate below adapts accordingly. Never used for a real campaign cell (the campaign is
deterministic full-year, 1 run per cell, per the runbook).

2026-07-28 built (employee task: build + dry-run test the campaign driver; do NOT launch the
56-run campaign -- a single short smoke run only, --smoke-days).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PROBE_DRIVER_PY = os.path.join(HERE, "3rdJ_08P_probe_driver.py")
CELLS_PY = os.path.join(HERE, "3rdJ_08D_campaign_cells.py")

DEFAULT_OUTROOT = os.path.join(HERE, "campaign_local")


def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Loaded once at import time -- pure module-level code in both (no filesystem/eppy/pandas
# access at import), same rationale 3rdJ_08P_probes_local.py already documents for doing this.
_probe = _load_module(PROBE_DRIVER_PY, "_campaign_probe_driver_mod")
_cells_mod = _load_module(CELLS_PY, "_campaign_cells_mod")


def _set_smoke_runperiod(idf, smoke_days: int, verbose: bool = True) -> None:
    """Overrides the RunPeriod _ensure_output_objects() just forced to full-year, truncating it
    to the first `smoke_days` days of January. Called AFTER _ensure_output_objects() (which
    creates the RunPeriod object if none existed) so there is always exactly one RunPeriod to
    mutate here."""
    rps = idf.idfobjects.get("RUNPERIOD", [])
    for rp in rps:
        rp.Begin_Month = 1
        rp.Begin_Day_of_Month = 1
        rp.End_Month = 1
        rp.End_Day_of_Month = smoke_days
        if verbose:
            print(f"  [smoke] RunPeriod truncated to Jan 1-{smoke_days} "
                  f"({smoke_days} day(s), expect {smoke_days * 24} hourly rows)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run one 3J Leg-3 Step-8 CAMPAIGN cell "
                                              "(56-cell table, 2 buildings x 2 cities x 14 scenarios).")
    ap.add_argument("--cell", type=int, required=True, help="index into the 56-cell table (0-55)")
    ap.add_argument("--engine", choices=["auto", "cluster", "local"], default="auto",
                     help="auto (default) = platform-detected: Windows -> local, else cluster. "
                          "cluster path is UNIMPLEMENTED in this file (campaign has not been "
                          "ported to cluster paths -- local-only per this task's scope).")
    ap.add_argument("--outroot", type=str, default=None,
                     help="campaign output root (default: <Step8_docs>/campaign_local).")
    ap.add_argument("--repo-root", type=str, default=REPO_ROOT,
                     help="override the repo checkout root used to derive IDF/EPW/product paths "
                          "(default: auto-derived from this script's own location).")
    ap.add_argument("--postprocess-only", action="store_true",
                     help="Skip injection + EnergyPlus; re-derive both CSVs + manifest from an "
                          "already-existing <outdir>/run/eplusout.sql. Mirrors the probe driver's "
                          "--postprocess-only exactly (reuses _do_postprocess()).")
    ap.add_argument("--allow-stale-inputs", action="store_true",
                     help="Defaut-3 guard override -- see 3rdJ_08P_probe_driver.py's "
                          "--allow-stale-inputs for the full semantics (reused verbatim here via "
                          "_check_inputs_hash_guard()).")
    ap.add_argument("--smoke-days", type=int, default=None,
                     help="SMOKE-TEST ONLY: truncate the RunPeriod to the first N days instead "
                          "of the full year, and adjust the expected row count to N*24. Never "
                          "pass this for a real campaign cell.")
    # ---- T9-9 / T9-10 arm selection (2026-07-31) ----
    ap.add_argument("--no-standby-floor", action="store_true",
                     help="T9-9 OFF: reproduce the pre-fix defect S9D-8 exactly (one occupancy "
                          "schedule written to PEOPLE + LIGHTS + ELECTRICEQUIPMENT). Only for "
                          "regenerating the closed campaign_cf69d508 artefacts.")
    ap.add_argument("--lighting-model", type=str, default="none",
                     help="T9-10 LIGHTS-only diversity model. 'none' (default) = T9-9 behaviour, "
                          "lighting stays floor+(1-floor)*occ. 'calibrated' = office_n=3 (fitted "
                          "to the NECB prototype on 2022 observed occupancy), hotel_n=1, retail "
                          "driven by the open/closed staff_shoulder_flag -- WITHDRAWN, retail "
                          "lighting comes out frozen across every scenario; kept only to "
                          "reproduce arm B. 'calibrated_v2' = THE ONE TO USE: same office_n=3 "
                          "and hotel_n=1, retail on the T9-12 open-hours mix (k=0.60). 'nK' "
                          "(e.g. n8) = office_n=K with the withdrawn retail form. See "
                          "commercial_integration.py's T9-10 / T9-12 blocks.")
    ap.add_argument("--dhw-model", type=str, default="none",
                     help="T9-11 occupancy-driven service hot water. 'none' (default) = "
                          "WaterUse:Equipment keeps its prototype flow-fraction schedule and DHW "
                          "stays occupancy-invariant (26.8 %% of tower site energy frozen). "
                          "'per_capita' = T9-11, floor+(peak-floor)*occ on office/retail/hotel/"
                          "residential, hotel laundry excluded as a batch process -- REFUTED "
                          "(residential DHW +40.78 %%, night share 8.34->32.86 %%, peak draw hour "
                          "06:00->04:00); kept only to reproduce arm D. 'volume_scaled' = THE ONE "
                          "TO USE: T9-13, daily VOLUME scaled by r(d)=mean(occ_d)/mean(occ_ref_d) "
                          "with the prototype's intra-day shape carried through untouched, so "
                          "night share and peak hour are preserved by construction. Laundry no "
                          "longer excluded. See commercial_integration.py's T9-11/T9-13 blocks.")
    ap.add_argument("--dry-run", action="store_true",
                     help="print the resolved cell (paths, channels, missing inputs) and exit; "
                          "runs nothing, touches no filesystem beyond os.path.isfile checks "
                          "already done by build_campaign_cells().")
    args = ap.parse_args()

    engine = args.engine
    if engine == "auto":
        engine = "local" if sys.platform == "win32" else "cluster"
    if engine != "local":
        print(f"[FAIL] engine={engine!r} not implemented in the campaign driver -- local-only "
              f"per this task's scope (LOCAL Windows execution, campaign not ported to cluster).")
        sys.exit(1)

    repo_root = args.repo_root
    outroot = args.outroot if args.outroot else DEFAULT_OUTROOT

    # --repo-root must actually win. 3rdJ_08P_probe_driver.py:94 does
    # `sys.path.insert(0, UPLOAD)` at MODULE-IMPORT time as a cluster fallback, and this file
    # loads that module at import time (_load_module above) -- so on the cluster the probe
    # harness's own /speed-scratch/.../step8_4split/upload tree shadowed both PYTHONPATH and
    # --repo-root, and `import eSim_bem_utils` silently resolved to a STALE injector.
    # Caught 2026-07-31 by the pre-campaign validation job (ImportError: cannot import name
    # LIGHTING_MODEL_ZONE ... from .../upload/eSim_bem_utils/commercial_integration.py) --
    # i.e. it failed loudly only because the new code added a new name. Had T9-9/T9-10 changed
    # only BEHAVIOUR and not the module's API, all 56 cells would have run to completion
    # against the old injector and reported success. Re-assert repo_root at the front here, and
    # drop any eSim_bem_utils already bound, so the resolved path is the one the caller asked
    # for. The probe driver itself is NOT modified (closed, validated artefact).
    while repo_root in sys.path:
        sys.path.remove(repo_root)
    sys.path.insert(0, repo_root)
    for _m in [m for m in list(sys.modules) if m == "eSim_bem_utils"
               or m.startswith("eSim_bem_utils.")]:
        del sys.modules[_m]
    import eSim_bem_utils.commercial_integration as _ci_check
    print(f"[setup] eSim_bem_utils resolved from: {_ci_check.__file__}")
    if os.path.realpath(repo_root) not in os.path.realpath(_ci_check.__file__):
        print(f"[FAIL] injector resolved OUTSIDE --repo-root {repo_root}: "
              f"{_ci_check.__file__} -- refusing to run against an unknown copy of the injector")
        sys.exit(1)

    cells = _cells_mod.build_campaign_cells(repo_root)
    if not (0 <= args.cell < len(cells)):
        print(f"[FAIL] --cell {args.cell} out of range 0..{len(cells) - 1}")
        sys.exit(1)
    cell = cells[args.cell]
    tag = cell["tag"]

    if args.dry_run:
        print(f"[dry-run] cell={args.cell} tag={tag} building={cell['building']} "
              f"city={cell['city']} cz={cell['cz']} scenario={cell['scenario']}")
        print(f"[dry-run]   idf={cell['idf']}")
        print(f"[dry-run]   epw={cell['epw']}")
        for ch, cfg in cell["channels"].items():
            print(f"[dry-run]   channel {ch}: {cfg}")
        if "hotel_deliberately_absent" in cell:
            print(f"[dry-run]   hotel_deliberately_absent: {cell['hotel_deliberately_absent']}")
        if cell["missing_inputs"]:
            print(f"[dry-run]   MISSING: {cell['missing_inputs']}")
        else:
            print("[dry-run]   all inputs resolve")
        return

    if cell["missing_inputs"]:
        print(f"[FAIL] cell {args.cell} ({tag}) has missing required inputs (IDF/EPW): "
              f"{cell['missing_inputs']} -- refusing to run silently against absent files "
              f"(fail loudly per task instruction). Channel CSVs alone missing would instead "
              f"go through inject_mixed_use()'s own loud FALLBACK path; IDF/EPW absence is a "
              f"harder stop.")
        # NOTE: only IDF/EPW absence is a hard stop here; a channel csv absence is allowed
        # through deliberately (identical fallback semantics as the probe driver's cell 6 /
        # this campaign's Y2005/Y2010/Y2015 hotel-absent cells) -- re-filter missing_inputs to
        # decide which case this is.
        hard_missing = [m for m in cell["missing_inputs"] if m.startswith("idf:") or m.startswith("epw:")]
        if hard_missing:
            sys.exit(1)
        print("[setup] missing input(s) above are channel CSV(s) only -- proceeding, "
              "inject_mixed_use() will FALLBACK_LOUD that channel to NECB baseline.")

    # INJ_HASH: same fingerprint recipe as the probe driver (md5 of commercial_integration.py),
    # so a wiring-code change invalidates campaign output paths exactly the same way it does
    # for probes -- one injector, one hashing scheme, reused, not reinvented.
    injector_py = os.path.join(repo_root, "eSim_bem_utils", "commercial_integration.py")
    if not os.path.isfile(injector_py):
        print(f"[FAIL] injector not found at {injector_py}")
        sys.exit(1)
    inj_hash = _probe.md5_file(injector_py)[:8]
    driver_md5 = _probe.md5_file(os.path.abspath(__file__))
    outdir = os.path.join(outroot, f"campaign_{inj_hash}", tag)

    # ---- STALE-INPUTS GUARD (Defaut-3 fix, reused verbatim from the probe driver) ----
    inputs_hash, inputs_detail = _probe._compute_inputs_hash(cell["channels"])
    _probe._check_inputs_hash_guard(outdir, inputs_hash, inputs_detail,
                                     args.allow_stale_inputs, args.postprocess_only)

    os.makedirs(outdir, exist_ok=True)
    print(f"[setup] cell={args.cell} tag={tag} INJ_HASH={inj_hash} INPUTS_HASH={inputs_hash}")
    print(f"[setup] outdir={outdir}")
    print(f"[setup] idf={cell['idf']}  epw={cell['epw']}")

    eplus_idd = os.environ.get("EPLUS_IDD", "")
    if not eplus_idd or not os.path.isfile(eplus_idd):
        try:
            from eSim_bem_utils.config import resolve_idd_path
        except ImportError:
            sys.path.insert(0, repo_root)
            from eSim_bem_utils.config import resolve_idd_path
        try:
            eplus_idd = resolve_idd_path()
            print(f"[setup] EPLUS_IDD not set; resolved locally via config.py -> {eplus_idd}")
        except Exception as e:
            print(f"[FAIL] local IDD resolution via config.py failed: {e}")
            sys.exit(1)
    os.environ["EPLUS_IDD"] = eplus_idd

    # ---- --postprocess-only: reuse _do_postprocess() verbatim ----
    if args.postprocess_only:
        injected_idf_path = os.path.join(outdir, "injected.idf")
        run_dir = os.path.join(outdir, "run")
        sql_path = os.path.join(run_dir, "eplusout.sql")
        if not os.path.isfile(sql_path):
            print(f"[FAIL] --postprocess-only: eplusout.sql not found at {sql_path}")
            sys.exit(1)
        if not os.path.isfile(injected_idf_path):
            print(f"[FAIL] --postprocess-only: injected.idf not found at {injected_idf_path}")
            sys.exit(1)
        manifest_path = os.path.join(outdir, "manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        else:
            manifest = {"cell_index": args.cell, "cell_tag": tag, "scenario_label": tag,
                        "INJ_HASH": inj_hash, "outdir": outdir, "channels_requested": {}}
        manifest["driver_md5"] = driver_md5
        manifest["campaign_driver"] = True
        manifest["postprocess_only"] = True
        manifest["INPUTS_HASH"] = inputs_hash
        manifest["INPUTS_HASH_DETAIL"] = inputs_detail
        manifest.update(_probe._energyplus_provenance(engine))
        rows_hourly, rows_channel = _probe._do_postprocess(
            sql_path, injected_idf_path, eplus_idd, outdir, manifest)
        manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["sql_extraction_method"] = _probe.SQL_EXTRACTION_METHOD
        _probe._write_manifest(outdir, manifest)
        expected_rows = manifest.get("expected_rows", 8760)
        exit_rc = 0 if (rows_hourly == expected_rows and rows_channel == expected_rows) else 1
        print(f"[done] cell={args.cell} tag={tag} postprocess-only exit={exit_rc}")
        sys.exit(exit_rc)

    try:
        from eppy.modeleditor import IDF
    except ImportError as e:
        print(f"[FAIL] eppy not importable: {e}")
        sys.exit(1)
    try:
        from eSim_bem_utils.commercial_integration import inject_mixed_use
    except ImportError:
        sys.path.insert(0, repo_root)
        from eSim_bem_utils.commercial_integration import inject_mixed_use

    IDF.setiddname(eplus_idd)

    expected_rows = (args.smoke_days * 24) if args.smoke_days else 8760

    manifest = {
        "cell_index": args.cell,
        "cell_tag": tag,
        "scenario_label": tag,
        "scenario": cell["scenario"],
        "building": cell["building"],
        "city": cell["city"],
        "cz": cell["cz"],
        "INJ_HASH": inj_hash,
        "INPUTS_HASH": inputs_hash,
        "INPUTS_HASH_DETAIL": inputs_detail,
        "driver_md5": driver_md5,
        "campaign_driver": True,
        "outdir": outdir,
        "channels_requested": {},
        "smoke_days": args.smoke_days,
        "expected_rows": expected_rows,
    }
    if "hotel_deliberately_absent" in cell:
        manifest["hotel_deliberately_absent"] = cell["hotel_deliberately_absent"]
    manifest.update(_probe._energyplus_provenance(engine))
    for ch, cfg in cell["channels"].items():
        csv_path = cfg.get("csv", "")
        exists = bool(csv_path) and os.path.isfile(csv_path)
        manifest["channels_requested"][ch] = {
            "csv_path": csv_path,
            "csv_md5": _probe.md5_file(csv_path) if exists else None,
            "exists": exists,
            **{k: v for k, v in cfg.items() if k != "csv"},
        }

    # ---- Inject (reuse inject_mixed_use() -- the actual injector, untouched) ----
    injected_idf_path = os.path.join(outdir, "injected.idf")
    building_meta = {
        "building": cell["building"], "city": cell["city"], "cz": cell["cz"],
        "purpose": "campaign", "cell_index": args.cell, "scenario_label": tag,
    }
    # T9-9 / T9-10 arm -- resolved here, recorded in the manifest, passed straight through.
    from eSim_bem_utils.commercial_integration import (LIGHTING_MODEL_ZONE,
                                                        LIGHTING_MODEL_CALIBRATED_V2)
    _lm_arg = str(args.lighting_model).strip().lower()
    if _lm_arg in ("", "none", "off"):
        lighting_model = None
    elif _lm_arg == "calibrated":
        # WITHDRAWN retail form (frozen lighting) -- kept ONLY to reproduce arm B. See T9-12.
        lighting_model = dict(LIGHTING_MODEL_ZONE, office_n=3)
    elif _lm_arg in ("calibrated_v2", "v2"):
        lighting_model = dict(LIGHTING_MODEL_CALIBRATED_V2)
    elif _lm_arg.startswith("n") and _lm_arg[1:].isdigit():
        lighting_model = dict(LIGHTING_MODEL_ZONE, office_n=int(_lm_arg[1:]))
    else:
        print(f"[FAIL] --lighting-model {args.lighting_model!r} not understood "
              f"(expected 'none', 'calibrated', 'calibrated_v2', or 'nK')")
        sys.exit(1)
    # T9-11 arm -- same discipline: resolved here, recorded, never inferred downstream.
    from eSim_bem_utils.commercial_integration import (DHW_MODEL_PER_CAPITA,
                                                        DHW_MODEL_VOLUME_SCALED)
    _dhw_arg = str(args.dhw_model).strip().lower()
    if _dhw_arg in ("", "none", "off"):
        dhw_model = None
    elif _dhw_arg in ("per_capita", "percapita", "linear"):
        dhw_model = dict(DHW_MODEL_PER_CAPITA)
    elif _dhw_arg in ("volume_scaled", "volumescaled", "t9_13", "t913"):
        # T9-13 (arm E). Fail LOUD and EARLY if the baseline reference is not filled in: an empty
        # `reference_occ_mean` makes every WaterUse:Equipment object report `dhw_unresolved` and the
        # whole arm becomes a silent no-op that still produces 56 plausible-looking result dirs.
        dhw_model = dict(DHW_MODEL_VOLUME_SCALED)
        _ref = dhw_model.get("reference_occ_mean") or {}
        _missing = [c for c in dhw_model.get("channels", ()) if c not in _ref]
        if _missing:
            print(f"[FAIL] --dhw-model volume_scaled needs a baseline reference for every declared "
                  f"channel; missing {_missing}. Fill DHW_MODEL_VOLUME_SCALED['reference_occ_mean'] "
                  f"in commercial_integration.py -- see the T9-13 block and FINDING 4.")
            sys.exit(1)
        _flat = [c for c, v in _ref.items() if not isinstance(v, dict)]
        if _flat:
            print(f"[WARN] --dhw-model volume_scaled: channels {_flat} carry a FLAT scalar "
                  f"reference. That applies our series' weekday/weekend asymmetry on top of the "
                  f"prototype's (FINDING 4). Intended only for an IDF where flat is genuinely "
                  f"right; the campaign reference is per-day-type.")
    else:
        print(f"[FAIL] --dhw-model {args.dhw_model!r} not understood "
              f"(expected 'none', 'per_capita' or 'volume_scaled')")
        sys.exit(1)
    manifest["arm"] = {"preserve_load_standby_floor": not args.no_standby_floor,
                        "lighting_model_arg": args.lighting_model,
                        "lighting_model": lighting_model,
                        "dhw_model_arg": args.dhw_model,
                        "dhw_model": dhw_model}
    print(f"[arm] preserve_load_standby_floor={not args.no_standby_floor} "
          f"lighting_model={lighting_model} dhw_model={dhw_model}")
    try:
        inj_result = inject_mixed_use(cell["idf"], injected_idf_path, cell["channels"],
                                       building_meta, verbose=True,
                                       preserve_load_standby_floor=not args.no_standby_floor,
                                       lighting_model=lighting_model,
                                       dhw_model=dhw_model)
    except Exception as e:
        print(f"[FAIL] inject_mixed_use raised: {e}")
        manifest["inject_exception"] = str(e)
        _probe._write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["inject_mixed_use_result"] = inj_result
    fallback = sorted(set(inj_result.get("fallback", [])))
    banner_lines = []
    if fallback:
        manifest["FALLBACK_LOUD"] = fallback
        for ch in fallback:
            line = f"!!! FALLBACK: {ch} reverted to NECB baseline !!!"
            print(line)
            banner_lines.append(line)
    manifest["banner_lines"] = banner_lines

    # ---- Ensure outputs (reuse _ensure_output_objects() verbatim -- forces full year) ----
    try:
        idf = IDF(injected_idf_path)
        _probe._ensure_output_objects(idf, verbose=True)
        if args.smoke_days:
            _set_smoke_runperiod(idf, args.smoke_days, verbose=True)
        idf.saveas(injected_idf_path)
    except Exception as e:
        print(f"[FAIL] ensure-outputs step raised: {e}")
        manifest["ensure_outputs_exception"] = str(e)
        _probe._write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["injected_idf_md5"] = _probe.md5_file(injected_idf_path)

    # ---- Simulate (local engine only -- direct EnergyPlus.exe, no Singularity) ----
    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    from eSim_bem_utils.config import ENERGYPLUS_EXE
    if not os.path.isfile(ENERGYPLUS_EXE):
        print(f"[FAIL] local EnergyPlus executable not found: {ENERGYPLUS_EXE}")
        _probe._write_manifest(outdir, manifest)
        sys.exit(1)
    ep_cmd = [ENERGYPLUS_EXE, "-w", cell["epw"], "-d", run_dir, injected_idf_path]
    print(f"[sim] launching EnergyPlus directly: exe={ENERGYPLUS_EXE}")
    print(f"[sim] args: -w {cell['epw']} -d {run_dir} {injected_idf_path}")
    proc = subprocess.run(ep_cmd)
    ep_rc = proc.returncode
    manifest["ep_return_code"] = ep_rc
    print(f"[sim] EnergyPlus return code = {ep_rc}")

    # ---- Post-process (reuse _do_postprocess() verbatim) ----
    sql_path = os.path.join(run_dir, "eplusout.sql")
    rows_hourly, rows_channel = _probe._do_postprocess(sql_path, injected_idf_path, eplus_idd,
                                                         outdir, manifest)
    manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["sql_extraction_method"] = _probe.SQL_EXTRACTION_METHOD
    _probe._write_manifest(outdir, manifest)

    exit_rc = 0
    if ep_rc != 0:
        print(f"[FAIL] EnergyPlus exited nonzero ({ep_rc})")
        exit_rc = 1
    if rows_hourly != expected_rows:
        print(f"[FAIL] hourly_meters.csv row count = {rows_hourly}, expected {expected_rows}")
        exit_rc = 1
    if rows_channel != expected_rows:
        print(f"[FAIL] channel_hourly.csv row count = {rows_channel}, expected {expected_rows}")
        exit_rc = 1
    # 2026-07-31 (Defaut 5/6). A cell that simulated cleanly but cannot account for its own
    # energy is not a usable cell: Defaut 5 shipped precisely because "ep_return_code == 0 and
    # 8760 rows" was the whole definition of success. Closure failures now fail the CELL, so
    # they surface in campaign_status.csv instead of waiting to be noticed at Step 9.
    for gate in ("fuel_closure", "channel_closure"):
        for key, rep in (manifest.get(gate) or {}).items():
            if isinstance(rep, dict) and not rep.get("closed", False):
                print(f"[FAIL] {gate}[{key}] did not close "
                      f"(residual {rep.get('residual_rel', float('nan')) * 100:.4f} %)")
                exit_rc = 1

    print(f"[done] cell={args.cell} tag={tag} exit={exit_rc}")
    sys.exit(exit_rc)


if __name__ == "__main__":
    main()
