"""3rdJ_08P_probes_local.py -- Step 8 (3J Leg-3 4-split): LOCAL (Windows) orchestrator
for the §P probe cell table.

Purpose: this repo's `3rdJ_08P_probes.sh` is a SLURM array launcher (#SBATCH directives)
and is unusable on Windows. This script is its local replacement, calling
`3rdJ_08P_probe_driver.py --cell N --engine local` for each requested cell in a bounded
worker pool instead of one SLURM array task per cell.

Scope: this drives the EXISTING 7-cell §P probe table only (cells 0-6, one-at-a-time
office/retail/hotel variation on the SuperTall tower). It is NOT the 56/64-run campaign --
that stays BLOCKED pending A/B/C in
3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md. Running
this script exercises the injection -> EnergyPlus -> SQL-extraction chain end-to-end on
Windows so the campaign driver (whenever built) can reuse the same proven path.

Memory watchdog -- PORTED (pattern, not reinvented) from
2J_docs_occ_nTemp/Step8_docs/run_campaign_local.py:13,51-75,144. Same rationale verbatim:
"the campaign runs unattended on a machine that can't be rebooted remotely, so a
background thread polls Windows' commit charge and, if it crosses --mem-abort, kills every
active cell subprocess ... and stops the run." The ctypes MEMORYSTATUSEX struct,
_committed_pct(), _kill_active(), and the watchdog polling loop below are the same
implementation as that file, adapted to this script's per-cell subprocess bookkeeping.

Resume + no-silent-overwrite (2026-07-28 LOCAL PORT, Contrainte n2): a cell whose outdir
already holds a COMPLETE, valid manifest.json (ep_return_code==0 or postprocess_only,
no *_exception keys) + 8760-row hourly_meters.csv + 8760-row channel_hourly.csv is
SKIPPED. An outdir that exists but is incomplete/stale is ARCHIVED (renamed with a
timestamp suffix) before the cell is (re)run -- this script never overwrites an existing
outdir in place. This is the exact failure mode flagged as "Defaut 3 -- trou d'empreinte"
in the reference doc for the raw per-cell driver (os.makedirs(..., exist_ok=True) +
idf.saveas() + EnergyPlus -d run_dir all silently overwrite).

2026-07-28 Defaut-3 fix: "complete" alone is no longer sufficient for resume-skip. A cell
outdir can be perfectly complete (rc==0, 8760 rows both CSVs) yet built from STALE Step-7
products if the products changed after that cell was simulated -- this is precisely how
the retail-multiplier bug's re-simulation would have silently overwritten valid-looking
output. _cell_complete() now also takes the INPUTS_HASH this cell's CURRENT products hash
to (computed via the driver's own _compute_inputs_hash(), loaded from
3rdJ_08P_probe_driver.py so the exact same recipe is used) and returns False on a
mismatch -- which routes the outdir through the EXISTING _archive_stale() call below
(same "_STALE_<timestamp>" convention, not a second one) instead of a false resume-skip.
The driver's own --allow-stale-inputs guard (3rdJ_08P_probe_driver.py) remains as a
defense-in-depth backstop for direct/cluster invocations that don't go through this
orchestrator's pre-check.

Run (locally):
  py -3 3rdJ_08P_probes_local.py --dry-run
  py -3 3rdJ_08P_probes_local.py --cells 0,1,2,3,4,5,6 --workers 6
  py -3 3rdJ_08P_probes_local.py --cells 0 --workers 1     # single short-day smoke test

2026-07-28 built (LOCAL PORT task, additive -- does not touch 3rdJ_08P_probes.sh,
3rdJ_08P_gates.sh, or 3rdJ_08P_postprocess.sh, which remain the cluster path).
"""
from __future__ import annotations

import argparse
import csv
import ctypes
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
DRIVER = os.path.join(HERE, "3rdJ_08P_probe_driver.py")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_OUTROOT = os.path.join(HERE, "probes_local")
DEFAULT_INJECTOR_PY = os.path.join(REPO_ROOT, "eSim_bem_utils", "commercial_integration.py")


def _load_driver_module():
    """Load 3rdJ_08P_probe_driver.py as a module (its filename starts with a digit,
    so it can't be `import`ed normally) so this orchestrator can reuse the driver's
    OWN _build_cells()/_compute_inputs_hash() -- the exact same recipe, not a
    reimplementation -- to pre-check INPUTS_HASH before deciding resume-skip vs.
    archive (Defaut-3 fix, see module docstring). Safe to import: module-level code
    in the driver only does os.path.join()s (CELLS = _build_cells(STEP7_OUT)), no
    filesystem access, so this doesn't touch disk or require the cluster paths to
    exist."""
    spec = importlib.util.spec_from_file_location("_probe_driver_mod", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

CELL_TAGS = {
    0: "baseline_necb", 1: "B_central", 2: "var_office", 3: "var_retail",
    4: "var_hotel", 5: "cycle_2022", 6: "fallback_retail",
}

# ---------------------------------------------------------------------------
# Memory watchdog -- ported (pattern) from
# 2J_docs_occ_nTemp/Step8_docs/run_campaign_local.py:60-98. Kept as close to the
# original as this script's per-cell (not per-archetype-city) process bookkeeping allows.
# ---------------------------------------------------------------------------
_ACTIVE = {}                      # pid -> Popen of a running cell subprocess
_ACTIVE_LOCK = threading.Lock()
_ABORT = threading.Event()


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def _committed_pct():
    """Windows commit charge in use as % of the commit limit (== Task Manager
    'Committed' / perfmon '% Committed Bytes In Use') -- the metric that predicts
    the freeze (commit-limit exhaustion -> thrash)."""
    m = _MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    if not m.ullTotalPageFile:
        return float(m.dwMemoryLoad)
    return (1.0 - m.ullAvailPageFile / m.ullTotalPageFile) * 100.0


def _kill_active():
    with _ACTIVE_LOCK:
        pids = list(_ACTIVE)
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
        except Exception:
            pass


def _watchdog(ceiling, interval=3.0):
    peak = 0.0
    while not _ABORT.is_set():
        pct = _committed_pct()
        if pct > peak:
            peak = pct
        if pct >= ceiling:
            print(f"\n!!! WATCHDOG: committed memory {pct:.1f}% >= {ceiling}% "
                  f"-> KILLING all cells and aborting (peak {peak:.1f}%).", flush=True)
            _ABORT.set()
            _kill_active()
            return
        _ABORT.wait(interval)
# ---------------------------------------------------------------------------


def _md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _cell_complete(outdir: str, expected_inputs_hash: str = None) -> bool:
    """A cell outdir is COMPLETE iff manifest.json parses, records success (either
    ep_return_code == 0, or postprocess_only == True), carries no *_exception key,
    both CSVs are present with the manifest-recorded row count == 8760, AND (Defaut-3
    fix, 2026-07-28) -- when expected_inputs_hash is given -- the manifest's own
    INPUTS_HASH matches it. A manifest with no INPUTS_HASH at all (legacy/pre-fix) or
    a mismatched one is treated as NOT complete, which routes it through the existing
    _archive_stale() call in main() instead of a false resume-skip: "complete" is not
    the same question as "built from today's Step-7 products", and conflating them is
    exactly the silent-overwrite failure mode this fix closes."""
    manifest_path = os.path.join(outdir, "manifest.json")
    if not os.path.isfile(manifest_path):
        return False
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = json.load(f)
    except Exception:
        return False
    if any(k.endswith("_exception") for k in m):
        return False
    if not m.get("postprocess_only") and m.get("ep_return_code") != 0:
        return False
    for key in ("hourly_meters_csv", "channel_hourly_csv"):
        info = m.get(key, {})
        rows = info.get("rows")
        csv_path = info.get("path")
        if rows != 8760 or not csv_path or not os.path.isfile(csv_path):
            return False
    if expected_inputs_hash is not None and m.get("INPUTS_HASH") != expected_inputs_hash:
        return False
    return True


def _archive_stale(outdir: str) -> None:
    """Never silently overwrite an existing (incomplete/stale) outdir -- rename it aside
    with a timestamp suffix instead. See module docstring / reference doc 'Defaut 3'."""
    if not os.path.isdir(outdir):
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = outdir.rstrip("\\/") + f"_STALE_{ts}"
    os.rename(outdir, dest)
    print(f"  [archive] incomplete/stale outdir found -> archived to {dest} (never overwritten in place)")


def _run_cell(cell_idx: int, outroot: str, log_dir: str, python_exe: str,
              extra_args: list) -> dict:
    tag = CELL_TAGS[cell_idx]
    log_path = os.path.join(log_dir, f"{tag}.log")
    t0 = time.time()
    if _ABORT.is_set():
        return {"cell": tag, "exit": -1, "status": "ABORTED", "minutes": 0.0, "log": log_path}
    cmd = [python_exe, DRIVER, "--cell", str(cell_idx), "--engine", "local",
           "--outroot", outroot] + extra_args
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"# cmd: {cmd}\n")
        lf.flush()
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=HERE)
        with _ACTIVE_LOCK:
            _ACTIVE[proc.pid] = proc
        try:
            rc = proc.wait()
        finally:
            with _ACTIVE_LOCK:
                _ACTIVE.pop(proc.pid, None)
    status = "ABORTED" if _ABORT.is_set() else ("ok" if rc == 0 else "FAILED")
    return {"cell": tag, "exit": rc, "status": status,
            "minutes": round((time.time() - t0) / 60.0, 1), "log": log_path}


def main() -> None:
    ap = argparse.ArgumentParser(description="LOCAL (Windows) orchestrator for the Step-8 "
                                              "§P probe cells.")
    ap.add_argument("--cells", default="0,1,2,3,4,5,6",
                     help="comma-separated cell indices, 0-6 (default: all 7).")
    ap.add_argument("--workers", type=int, default=6,
                     help="concurrent cells (default 6 -- deliberately NOT cores-2: the user "
                          "works on this machine while runs are in flight, see reference doc "
                          "Contrainte n2).")
    ap.add_argument("--mem-abort", type=float, default=80.0,
                     help="HARD watchdog: kill the whole run if committed memory %% reaches "
                          "this (default 80, ported from run_campaign_local.py --mem-abort).")
    ap.add_argument("--outroot", default=DEFAULT_OUTROOT,
                     help="probes root dir, passed through to the driver's --outroot "
                          "(default: <this dir>/probes_local).")
    ap.add_argument("--repo-root", default=None,
                     help="passed through to the driver's --repo-root (non-default checkout).")
    ap.add_argument("--no-resume", action="store_true",
                     help="re-run requested cells even if they already look complete "
                          "(existing outdir is still archived, never overwritten in place).")
    ap.add_argument("--postprocess-only", action="store_true",
                     help="mirrors 3rdJ_08P_postprocess.sh's recovery array: re-derive both "
                          "CSVs + manifest.json from each requested cell's EXISTING "
                          "<outdir>/run/eplusout.sql, no re-simulation. Resume/archive logic "
                          "is bypassed in this mode (the whole point is to reuse the existing "
                          "outdir, not archive it away) -- the driver's own --postprocess-only "
                          "guard errors clearly per-cell if that sql file is absent.")
    ap.add_argument("--allow-stale-inputs", action="store_true",
                     help="passed through to the driver (Defaut-3 fix): explicit override for "
                          "the per-cell STALE-INPUTS GUARD. Rarely needed when going through "
                          "this orchestrator -- the resume/archive logic below already archives "
                          "an INPUTS_HASH-mismatched outdir before invoking the driver, so the "
                          "driver's own guard sees a fresh (nonexistent) outdir in the normal "
                          "case. Kept for parity with direct driver invocation and "
                          "--postprocess-only (which bypasses the pre-check below).")
    ap.add_argument("--dry-run", action="store_true",
                     help="resolve + print the plan, run nothing.")
    args = ap.parse_args()

    if not args.dry_run:
        try:
            import eppy, pandas, numpy  # noqa: F401
        except ImportError as e:
            print(f"ERROR: missing dependency ({e}) -- fail fast before spawning any cell "
                  f"(mirrors the dep precheck in 3rdJ_08P_probes.sh/_postprocess.sh).")
            sys.exit(2)

    python_exe = sys.executable
    try:
        cells = [int(c.strip()) for c in args.cells.split(",") if c.strip() != ""]
    except ValueError:
        print(f"ERROR: --cells must be comma-separated integers, got '{args.cells}'")
        sys.exit(2)
    unknown = [c for c in cells if c not in CELL_TAGS]
    if unknown:
        print(f"ERROR: unknown cell index/indices {unknown} (valid: 0-6)")
        sys.exit(2)

    log_dir = os.path.join(args.outroot, "_logs")
    os.makedirs(log_dir, exist_ok=True)

    injector_py = (os.path.join(args.repo_root, "eSim_bem_utils", "commercial_integration.py")
                   if args.repo_root else DEFAULT_INJECTOR_PY)
    if not os.path.isfile(injector_py):
        print(f"ERROR: injector not found at {injector_py}")
        sys.exit(2)
    inj_hash = _md5_file(injector_py)[:8]
    campaign_dir = os.path.join(args.outroot, f"campaign_{inj_hash}")

    extra_args = []
    if args.repo_root:
        extra_args += ["--repo-root", args.repo_root]
    if args.postprocess_only:
        extra_args += ["--postprocess-only"]
    if args.allow_stale_inputs:
        extra_args += ["--allow-stale-inputs"]

    todo, done = [], []
    if args.postprocess_only:
        # Mirrors 3rdJ_08P_postprocess.sh: every requested cell is re-run through
        # --postprocess-only, which reuses (never touches) the existing outdir/run/
        # eplusout.sql. Resume-skip / archive-stale do NOT apply here -- archiving would
        # destroy the exact eplusout.sql this mode exists to recover from. INPUTS_HASH
        # consistency for this mode is enforced by the driver itself (--postprocess-only
        # never archives on a genuine mismatch, only on a legacy manifest + explicit
        # --allow-stale-inputs -- see 3rdJ_08P_probe_driver.py::_check_inputs_hash_guard).
        todo = list(cells)
    else:
        # Defaut-3 fix: resume-skip requires the outdir's manifest INPUTS_HASH to match
        # what THIS cell's CURRENT Step-7 products hash to -- not just "looks complete".
        # Uses the driver's own _build_cells()/_compute_inputs_hash() (loaded once) so the
        # exact same recipe decides both here and inside the driver's own guard.
        driver_mod = _load_driver_module()
        step7_out = (
            os.path.join(args.repo_root, "3J_docs_occ_nTemp", "Leg3_4-split", "Step7_docs",
                         "outputs_step7")
            if args.repo_root else driver_mod.LOCAL_STEP7_OUT)
        cells_table = driver_mod._build_cells(step7_out)
        for c in cells:
            tag = CELL_TAGS[c]
            outdir = os.path.join(campaign_dir, tag)
            expected_hash, _detail = driver_mod._compute_inputs_hash(cells_table[c]["channels"])
            if os.path.isdir(outdir):
                if (not args.no_resume) and _cell_complete(outdir, expected_hash):
                    done.append(tag)
                    continue
                _archive_stale(outdir)
            todo.append(c)

    print(f"=== §P PROBE LOCAL | {len(cells)} cell(s) requested | INJ_HASH={inj_hash} | "
          f"campaign dir = {campaign_dir} | postprocess-only={args.postprocess_only} ===")
    print(f"  workers={args.workers}  mem-abort={args.mem_abort}%")
    print(f"  to run : {len(todo)} | done (resume-skip): {len(done)}")
    if args.dry_run:
        for c in todo:
            print(f"  would run: cell {c} ({CELL_TAGS[c]})")
        for tag in done:
            print(f"  would skip (already complete): {tag}")
        return
    if not todo:
        print("  Nothing to run (all requested cells already complete).")
        return

    results = []
    t_start = time.time()
    wd = threading.Thread(target=_watchdog, args=(args.mem_abort,), daemon=True)
    wd.start()
    print(f"  watchdog ARMED at committed >= {args.mem_abort}% (polls every 3s)")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(_run_cell, c, args.outroot, log_dir, python_exe, extra_args): c
            for c in todo
        }
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"  [{len(results)}/{len(todo)}] {r['status']:6s} {r['cell']:20s} "
                  f"exit={r['exit']}  {r['minutes']:6.1f} min", flush=True)

    _ABORT.set()  # stop the watchdog thread on normal completion
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
    print(f"\n=== Local probe run finished in {(time.time() - t_start) / 60.0:.1f} min ===")
    print(f"  cells ok: {ok}/{len(cells)}  (newly run: {len(results) - len(failed)}, "
          f"resume-skip: {len(done)})")
    print(f"  status -> {status_csv}")
    if any(r["status"] == "ABORTED" for r in results):
        print("\n!!! ABORTED BY WATCHDOG -- committed-memory ceiling hit. No freeze; run was killed.")
        print("    Lower --workers and re-launch (resume skips completed cells).")
        sys.exit(1)
    if failed:
        print(f"  FAILED ({len(failed)}): {', '.join(failed)}")
        print("  -> re-launch the SAME command: completed cells skip, failed/partial re-run "
              "(their outdir is archived first, never overwritten in place).")
        sys.exit(1)
    print("  All cells ok.")


if __name__ == "__main__":
    main()
