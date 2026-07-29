"""3rdJ_08D_campaign_local.py -- Step 8 (3J Leg-3 4-split): LOCAL (Windows) orchestrator for
the 56-cell CAMPAIGN table (2 buildings x 2 cities x 14 scenarios,
3rdJ_08_simulation_4split.md:44).

Strictly additive, same pattern as 3rdJ_08P_probes_local.py (the 7-cell §P probe orchestrator)
-- REUSES (imports, never re-implements) that file's memory watchdog (_committed_pct,
_kill_active, _watchdog, the module-level _ACTIVE/_ACTIVE_LOCK/_ABORT this file's own subprocess
bookkeeping shares), _cell_complete() (resume-skip logic, generic over any outdir + expected
INPUTS_HASH), and _archive_stale() (never-overwrite-in-place convention, "_STALE_<timestamp>").
Loaded via importlib exactly like that file already loads 3rdJ_08P_probe_driver.py as a module.
3rdJ_08P_probes_local.py itself is NOT modified -- proof: `py -3 3rdJ_08P_probes_local.py
--dry-run` is re-run unchanged as part of this task's Progress Log entry.

Drives 3rdJ_08D_campaign_driver.py --cell N --engine local for each requested cell (56 total,
0-55) instead of 3rdJ_08P_probe_driver.py's 7. Cell table comes from
3rdJ_08D_campaign_cells.py::build_campaign_cells() (derived programmatically, never hand-typed).

🔴 Memory guard is NON-NEGOTIABLE (machine cannot be rebooted remotely) -- same watchdog,
same default ceiling (80% committed), same default --workers 6 (deliberately not cores-2: the
user works on this machine during runs).

Run (locally):
  py -3 3rdJ_08D_campaign_local.py --dry-run                        # print all 56 cells, run nothing
  py -3 3rdJ_08D_campaign_local.py --cells 27 --workers 1 --smoke-days 2   # ONE short smoke run
  py -3 3rdJ_08D_campaign_local.py --workers 6                       # full 56-cell campaign
                                                                       # (NOT launched by this task)

2026-07-28 built (employee task: build + dry-run test the campaign driver/runner; do NOT
launch the 56-run campaign -- a single short smoke run only).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DRIVER = os.path.join(HERE, "3rdJ_08D_campaign_driver.py")
PROBES_LOCAL_PY = os.path.join(HERE, "3rdJ_08P_probes_local.py")
CELLS_PY = os.path.join(HERE, "3rdJ_08D_campaign_cells.py")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_OUTROOT = os.path.join(HERE, "campaign_local")
DEFAULT_INJECTOR_PY = os.path.join(REPO_ROOT, "eSim_bem_utils", "commercial_integration.py")


def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Loaded once at import time. _probes_local exposes the watchdog primitives + _cell_complete +
# _archive_stale + _md5_file -- REUSED, not reimplemented (see module docstring). _cells_mod
# exposes build_campaign_cells(). Neither load touches disk beyond parsing these two .py files
# (both modules' top-level code is import-safe -- no eppy/pandas/filesystem access at import
# time, same property 3rdJ_08P_probes_local.py already relies on for its own driver import).
_probes_local = _load_module(PROBES_LOCAL_PY, "_campaign_probes_local_mod")
_cells_mod = _load_module(CELLS_PY, "_campaign_cells_mod")


def _md5_file(path: str) -> str:
    return _probes_local._md5_file(path)


def _run_cell(cell_idx: int, tag: str, outroot: str, log_dir: str, python_exe: str,
              extra_args: list) -> dict:
    """Mirrors 3rdJ_08P_probes_local.py::_run_cell exactly, adapted to invoke
    3rdJ_08D_campaign_driver.py instead of the probe driver, and to share the SAME
    _ACTIVE/_ACTIVE_LOCK/_ABORT globals as the reused watchdog (module-level state lives in
    _probes_local, referenced here rather than duplicated -- one set of "what's currently
    running" bookkeeping, not two)."""
    log_path = os.path.join(log_dir, f"{tag}.log")
    t0 = time.time()
    if _probes_local._ABORT.is_set():
        return {"cell": tag, "exit": -1, "status": "ABORTED", "minutes": 0.0, "log": log_path}
    cmd = [python_exe, CAMPAIGN_DRIVER, "--cell", str(cell_idx), "--engine", "local",
           "--outroot", outroot] + extra_args
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"# cmd: {cmd}\n")
        lf.flush()
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=HERE)
        with _probes_local._ACTIVE_LOCK:
            _probes_local._ACTIVE[proc.pid] = proc
        try:
            rc = proc.wait()
        finally:
            with _probes_local._ACTIVE_LOCK:
                _probes_local._ACTIVE.pop(proc.pid, None)
    status = "ABORTED" if _probes_local._ABORT.is_set() else ("ok" if rc == 0 else "FAILED")
    return {"cell": tag, "exit": rc, "status": status,
            "minutes": round((time.time() - t0) / 60.0, 1), "log": log_path}


def main() -> None:
    ap = argparse.ArgumentParser(description="LOCAL (Windows) orchestrator for the Step-8 "
                                              "56-cell CAMPAIGN table.")
    ap.add_argument("--cells", default=",".join(str(i) for i in range(56)),
                     help="comma-separated cell indices, 0-55 (default: all 56).")
    ap.add_argument("--workers", type=int, default=6,
                     help="concurrent cells (default 6 -- deliberately NOT cores-2: the user "
                          "works on this machine while runs are in flight).")
    ap.add_argument("--mem-abort", type=float, default=80.0,
                     help="HARD watchdog: kill the whole run if committed memory %% reaches "
                          "this (default 80, reused from 3rdJ_08P_probes_local.py).")
    ap.add_argument("--outroot", default=DEFAULT_OUTROOT,
                     help="campaign root dir, passed through to the driver's --outroot "
                          "(default: <this dir>/campaign_local -- a FRESH tree, distinct from "
                          "the probe harness's probes_local/, so no INPUTS_HASH guard collision "
                          "with pre-existing probe outputs is possible).")
    ap.add_argument("--repo-root", default=REPO_ROOT,
                     help="passed through to the driver's --repo-root (non-default checkout).")
    ap.add_argument("--no-resume", action="store_true",
                     help="re-run requested cells even if they already look complete "
                          "(existing outdir is still archived, never overwritten in place).")
    ap.add_argument("--postprocess-only", action="store_true",
                     help="re-derive both CSVs + manifest.json from each requested cell's "
                          "EXISTING <outdir>/run/eplusout.sql, no re-simulation. Resume/archive "
                          "logic is bypassed (mirrors 3rdJ_08P_probes_local.py's own "
                          "--postprocess-only semantics).")
    ap.add_argument("--allow-stale-inputs", action="store_true",
                     help="passed through to the driver -- see 3rdJ_08P_probe_driver.py's flag "
                          "of the same name for the full semantics.")
    ap.add_argument("--smoke-days", type=int, default=None,
                     help="SMOKE-TEST ONLY: passed through to the driver, truncates each run's "
                          "RunPeriod to N days instead of the full year. Never pass this for a "
                          "real campaign launch.")
    ap.add_argument("--dry-run", action="store_true",
                     help="resolve + print the plan (all requested cells, resolved paths, "
                          "missing inputs) and exit; runs nothing.")
    args = ap.parse_args()

    if not args.dry_run:
        try:
            import eppy, pandas, numpy  # noqa: F401
        except ImportError as e:
            print(f"ERROR: missing dependency ({e}) -- fail fast before spawning any cell.")
            sys.exit(2)

    python_exe = sys.executable
    try:
        requested = [int(c.strip()) for c in args.cells.split(",") if c.strip() != ""]
    except ValueError:
        print(f"ERROR: --cells must be comma-separated integers, got '{args.cells}'")
        sys.exit(2)

    all_cells = _cells_mod.build_campaign_cells(args.repo_root)
    if len(all_cells) != 56:
        print(f"ERROR: build_campaign_cells() returned {len(all_cells)} cells, expected 56")
        sys.exit(2)
    cells_by_idx = {c["cell_index"]: c for c in all_cells}
    unknown = [c for c in requested if c not in cells_by_idx]
    if unknown:
        print(f"ERROR: unknown cell index/indices {unknown} (valid: 0-55)")
        sys.exit(2)

    log_dir = os.path.join(args.outroot, "_logs")
    os.makedirs(log_dir, exist_ok=True)

    injector_py = os.path.join(args.repo_root, "eSim_bem_utils", "commercial_integration.py")
    if not os.path.isfile(injector_py):
        print(f"ERROR: injector not found at {injector_py}")
        sys.exit(2)
    inj_hash = _md5_file(injector_py)[:8]
    campaign_dir = os.path.join(args.outroot, f"campaign_{inj_hash}")

    extra_args = ["--repo-root", args.repo_root]
    if args.postprocess_only:
        extra_args += ["--postprocess-only"]
    if args.allow_stale_inputs:
        extra_args += ["--allow-stale-inputs"]
    if args.smoke_days:
        extra_args += ["--smoke-days", str(args.smoke_days)]

    # _compute_inputs_hash() is the probe driver's (reused verbatim, same recipe the campaign
    # driver itself uses via its own load of 3rdJ_08P_probe_driver.py) -- loaded once here, not
    # once per cell, unlike the inline placeholder this replaced.
    _inputs_hash_mod = _load_module(os.path.join(HERE, "3rdJ_08P_probe_driver.py"),
                                     "_campaign_inputs_hash_mod")

    todo, done, dry_rows = [], [], []
    if args.postprocess_only:
        todo = list(requested)
    else:
        for c in requested:
            cell = cells_by_idx[c]
            tag = cell["tag"]
            outdir = os.path.join(campaign_dir, tag)
            expected_hash, _detail = _inputs_hash_mod._compute_inputs_hash(cell["channels"])
            if os.path.isdir(outdir):
                if (not args.no_resume) and _probes_local._cell_complete(outdir, expected_hash):
                    done.append(tag)
                    continue
                _probes_local._archive_stale(outdir)
            todo.append(c)

    print(f"=== 3J Leg-3 Step-8 CAMPAIGN LOCAL | {len(requested)} cell(s) requested (of 56) | "
          f"INJ_HASH={inj_hash} | campaign dir = {campaign_dir} | "
          f"postprocess-only={args.postprocess_only} | smoke-days={args.smoke_days} ===")
    print(f"  workers={args.workers}  mem-abort={args.mem_abort}%")
    print(f"  to run : {len(todo)} | done (resume-skip): {len(done)}")

    if args.dry_run:
        for c in sorted(requested):
            cell = cells_by_idx[c]
            miss = f"  MISSING={cell['missing_inputs']}" if cell["missing_inputs"] else ""
            hotel_note = ""
            if "hotel_deliberately_absent" in cell:
                hotel_note = "  [hotel deliberately absent -- see cell table docstring]"
            print(f"  cell {c:2d}  {cell['tag']:35s}  building={cell['building']:9s} "
                  f"city={cell['city']:3s}  scenario={cell['scenario']:16s}{miss}{hotel_note}")
            print(f"           idf={cell['idf']}")
            print(f"           epw={cell['epw']}")
            for ch, cfg in cell["channels"].items():
                print(f"           channel {ch}: {cfg}")
        n_missing = sum(1 for c in requested if cells_by_idx[c]["missing_inputs"])
        print(f"\n  {len(requested)} cell(s) printed, {n_missing} with a missing input.")
        return

    if not todo:
        print("  Nothing to run (all requested cells already complete).")
        return

    results = []
    t_start = time.time()
    _probes_local._ABORT.clear()
    wd = threading.Thread(target=_probes_local._watchdog, args=(args.mem_abort,), daemon=True)
    wd.start()
    print(f"  watchdog ARMED at committed >= {args.mem_abort}% (polls every 3s, reused from "
          f"3rdJ_08P_probes_local.py)")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(_run_cell, c, cells_by_idx[c]["tag"], args.outroot, log_dir, python_exe,
                      extra_args): c
            for c in todo
        }
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"  [{len(results)}/{len(todo)}] {r['status']:6s} {r['cell']:35s} "
                  f"exit={r['exit']}  {r['minutes']:6.1f} min", flush=True)

    _probes_local._ABORT.set()
    status_csv = os.path.join(args.outroot, "campaign_status.csv")
    with open(status_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cell", "status", "exit", "minutes", "log"])
        for tag in done:
            w.writerow([tag, "ok(resume-skip)", 0, "", ""])
        for r in results:
            w.writerow([r["cell"], r["status"], r["exit"], r["minutes"], r["log"]])

    failed = [r["cell"] for r in results if r["status"] != "ok"]
    ok = len(results) - len(failed) + len(done)
    print(f"\n=== Campaign run finished in {(time.time() - t_start) / 60.0:.1f} min ===")
    print(f"  cells ok: {ok}/{len(requested)}  (newly run: {len(results) - len(failed)}, "
          f"resume-skip: {len(done)})")
    print(f"  status -> {status_csv}")
    if any(r["status"] == "ABORTED" for r in results):
        print("\n!!! ABORTED BY WATCHDOG -- committed-memory ceiling hit. No freeze; run was killed.")
        print("    Lower --workers and re-launch (resume skips completed cells).")
        sys.exit(1)
    if failed:
        print(f"  FAILED ({len(failed)}): {', '.join(failed)}")
        sys.exit(1)
    print("  All requested cells ok.")


if __name__ == "__main__":
    main()
