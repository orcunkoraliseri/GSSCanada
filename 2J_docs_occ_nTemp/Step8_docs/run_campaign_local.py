#!/usr/bin/env python3
"""
run_campaign_local.py — parallel LOCAL driver for the full Step 8 campaign.

Wraps the validated 1-cell driver (run_paired_mc.py) in a bounded worker pool so
all 24 (archetype x city) cells run concurrently on a multi-core Windows box,
instead of the ~46 h sequential path (run_bem.py option 3). Each cell is one
subprocess = N HH x 5 years of annual EnergyPlus runs; cells are fully isolated
(separate processes, separate output dirs), so this is just safe fan-out over the
exact same engine the 8D-pilot validated.

Key behaviours:
  - Concurrency: --workers (default = CPU cores - 2). Each E+ run is single-threaded,
    so cores-2 keeps every core busy while leaving headroom for the OS.
  - Isolation: writes under SimResults_Step8/campaign_N50/<cell>/ by default, NOT the
    bare SimResults_Step8/<cell>/ dirs the N=3 pilot/smoke used -> no contamination,
    a clean publishable dataset, and a trustworthy resume check.
  - Resume: a cell already holding N x years hourly_meters.csv is SKIPPED, so a
    re-launch after a crash/stop continues where it left off (failed/partial cells
    re-run from scratch; completed cells are skipped).
  - Logging: per-cell stdout/stderr -> <root>/_logs/<cell>.log; one row per cell in
    <root>/campaign_status.csv; a live progress line per finished cell to console.

Run (locally, overnight):
  cd 2J_docs_occ_nTemp/Step8_docs
  py run_campaign_local.py --n 50            # auto workers = cores-2
  py run_campaign_local.py --n 50 --workers 8
  py run_campaign_local.py --dry-run         # resolve + plan only, no E+

Exit 0 = all cells ok; 1 = at least one cell failed (re-launch to resume).
"""
import argparse
import csv
import ctypes
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from eSim_bem_utils_2J.main import STEP8_RESULTS_DIR, COMPARATIVE_YEARS  # noqa: E402
from run_bem import all_cells, resolve_cell  # noqa: E402

DRIVER = os.path.join(HERE, "run_paired_mc.py")

# --- Memory watchdog: hard auto-kill before the box can thrash/freeze --------
# The campaign runs unattended on a machine that can't be rebooted remotely, so a
# background thread polls Windows' commit charge and, if it crosses --mem-abort,
# kills every active cell subprocess (+ its EnergyPlus children) and stops the run.
# With the flip (--workers 1 --ep-workers K) steady state is ~50% commit, so this
# only ever fires on a genuine anomaly -- it's a backstop, not the brake.
_ACTIVE = {}                      # pid -> Popen of a running cell
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
    m = _MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
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


def _count_hourly(cell_dir):
    """Count hourly_meters.csv files anywhere under a cell output dir."""
    n = 0
    for _root, _dirs, files in os.walk(cell_dir):
        n += sum(1 for f in files if f == "hourly_meters.csv")
    return n


def _run_cell(arch, city, n, seed, sim_mode, out_dir, log_dir, ep_workers):
    label = f"{arch}__{city}"
    log_path = os.path.join(log_dir, f"{label}.log")
    t0 = time.time()
    if _ABORT.is_set():
        return {"cell": label, "exit": -1, "status": "ABORTED", "minutes": 0.0, "log": log_path}
    # Inner E+ pool size per cell via ESIM_WORKERS (simulation.py:159-160). Total
    # concurrent E+ == --workers (cells) x --ep-workers (E+ per cell). The flip =
    # --workers 1 --ep-workers K: only ONE cell's schedule CSVs (~3.7 GB) in RAM.
    # Popen (not run) so the watchdog can kill this process tree on a breach.
    child_env = dict(os.environ, ESIM_WORKERS=str(ep_workers))
    with open(log_path, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            [sys.executable, DRIVER,
             "--archetype", arch, "--city", city,
             "--n", str(n), "--seed", str(seed), "--sim-mode", sim_mode,
             "--output-dir", out_dir],
            stdout=lf, stderr=subprocess.STDOUT, cwd=HERE, env=child_env,
        )
        with _ACTIVE_LOCK:
            _ACTIVE[proc.pid] = proc
        try:
            rc = proc.wait()
        finally:
            with _ACTIVE_LOCK:
                _ACTIVE.pop(proc.pid, None)
    status = "ABORTED" if _ABORT.is_set() else ("ok" if rc == 0 else "FAILED")
    return {"cell": label, "exit": rc, "status": status,
            "minutes": round((time.time() - t0) / 60.0, 1), "log": log_path}


def main():
    default_workers = max(1, (os.cpu_count() or 4) - 2)
    p = argparse.ArgumentParser(description="Parallel local Step 8 campaign runner.")
    p.add_argument("--n", type=int, default=50, help="households per cell (default 50).")
    p.add_argument("--seed", type=int, default=42, help="base seed (default 42).")
    p.add_argument("--sim-mode", default="standard", choices=["standard", "weekly"],
                   help="standard = full annual (campaign); weekly = fast smoke.")
    p.add_argument("--workers", type=int, default=default_workers,
                   help=f"concurrent cells (default {default_workers} = cores-2).")
    p.add_argument("--ep-workers", type=int, default=1,
                   help="EnergyPlus processes PER cell (inner pool, via ESIM_WORKERS). Total "
                        "concurrent E+ == workers x ep-workers. Flip = --workers 1 --ep-workers 6.")
    p.add_argument("--mem-abort", type=float, default=80.0,
                   help="HARD watchdog: kill the whole run if committed memory %% reaches this "
                        "(default 80). Prevents an un-rebootable freeze.")
    p.add_argument("--output-root", default=os.path.join(STEP8_RESULTS_DIR, "campaign_N50"),
                   help="campaign root; one subdir per cell.")
    p.add_argument("--cells", default=None,
                   help="comma-separated cell labels (e.g. SingleD__Toronto_5A) to limit "
                        "the run to a subset; default = all 24. Handy for re-running failures.")
    p.add_argument("--no-resume", action="store_true",
                   help="re-run cells even if they already look complete.")
    p.add_argument("--dry-run", action="store_true",
                   help="resolve cells + print plan, run nothing.")
    args = p.parse_args()

    cells = all_cells()
    if args.cells:
        want = {s.strip() for s in args.cells.split(",") if s.strip()}
        cells = [(a, c) for a, c in cells if f"{a}__{c}" in want]
        missing = want - {f"{a}__{c}" for a, c in cells}
        if missing:
            print(f"ERROR: unknown --cells: {', '.join(sorted(missing))}", flush=True)
            sys.exit(2)
    nyr = len(COMPARATIVE_YEARS)
    expected = args.n * nyr
    root = args.output_root
    log_dir = os.path.join(root, "_logs")
    os.makedirs(log_dir, exist_ok=True)

    todo, done, unresolved = [], [], []
    for arch, city in cells:
        label = f"{arch}__{city}"
        if not resolve_cell(arch, city):
            unresolved.append(label)
            continue
        cell_dir = os.path.join(root, label)
        if (not args.no_resume) and os.path.isdir(cell_dir) and _count_hourly(cell_dir) >= expected:
            done.append(label)
            continue
        todo.append((arch, city))

    print(f"=== Step 8 LOCAL campaign | {len(cells)} cells | N={args.n} x {nyr} yr "
          f"= {expected} runs/cell | {len(cells) * expected} total ===")
    print(f"  workers={args.workers}  ep-workers={args.ep_workers}  mem-abort={args.mem_abort}%  mode={args.sim_mode}")
    print(f"  root   ={root}")
    print(f"  to run : {len(todo)} | done (resume-skip): {len(done)} | unresolved: {len(unresolved)}")
    if unresolved:
        print(f"  UNRESOLVED (missing IDF/EPW): {', '.join(unresolved)}")
    if args.dry_run:
        for a, c in todo:
            print(f"  would run: {a}__{c}  -> {os.path.join(root, a + '__' + c)}")
        return

    if not todo:
        print("  Nothing to run (all cells already complete).")
        return

    results = []
    t_start = time.time()
    wd = threading.Thread(target=_watchdog, args=(args.mem_abort,), daemon=True)
    wd.start()
    print(f"  watchdog ARMED at committed >= {args.mem_abort}% (polls every 3s)")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(_run_cell, a, c, args.n, args.seed, args.sim_mode,
                      os.path.join(root, f"{a}__{c}"), log_dir, args.ep_workers): f"{a}__{c}"
            for a, c in todo
        }
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"  [{len(results)}/{len(todo)}] {r['status']:6s} {r['cell']:24s} "
                  f"exit={r['exit']}  {r['minutes']:6.1f} min", flush=True)

    _ABORT.set()  # stop the watchdog thread on normal completion
    status_csv = os.path.join(root, "campaign_status.csv")
    with open(status_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cell", "status", "exit", "minutes", "log"])
        for label in done:
            w.writerow([label, "ok(resume-skip)", 0, "", ""])
        for r in results:
            w.writerow([r["cell"], r["status"], r["exit"], r["minutes"], r["log"]])

    failed = [r["cell"] for r in results if r["status"] != "ok"]
    ok = len(results) - len(failed) + len(done)
    print(f"\n=== Campaign finished in {(time.time() - t_start) / 3600:.2f} h ===")
    print(f"  cells ok: {ok}/{len(cells)}  (newly run: {len(results) - len(failed)}, "
          f"resume-skip: {len(done)})")
    print(f"  status -> {status_csv}")
    if any(r["status"] == "ABORTED" for r in results):
        print("\n!!! ABORTED BY WATCHDOG -- committed-memory ceiling hit. No freeze; run was killed.")
        print("    Lower --ep-workers and re-launch (resume skips completed cells).")
        sys.exit(1)
    if failed:
        print(f"  FAILED ({len(failed)}): {', '.join(failed)}")
        print("  -> re-launch the SAME command: completed cells skip, failed/partial re-run.")
        sys.exit(1)
    print("  All cells ok.")


if __name__ == "__main__":
    main()
