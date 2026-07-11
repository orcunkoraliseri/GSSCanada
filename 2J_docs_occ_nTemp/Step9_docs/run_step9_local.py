#!/usr/bin/env python3
"""
run_step9_local.py — parallel LOCAL driver for the full Step 9 campaign (2022 + 2030 only).

Thin wrapper around the SAME validated engine as Step 8 (run_paired_mc.py / run_step8_paired_mc)
run TWICE per cell: once against the 17-col "activity" schedules (default BEM_Setup dir) and once
against the 13-col "baseline" schedules (via --sched-dir pointing at a hardlink dir that exposes
BEM_Schedules_{2022,2030}_baseline.csv under the plain BEM_Schedules_{2022,2030}.csv filename
run_paired_mc.py expects). Because both schedule files share the identical 144,465-HH id set
(verified), a fixed --seed draws the SAME households for baseline and activity, and the SAME
households Step 8's targeted 2022/2030 re-sim used (same seed, same schedule source for the
activity arm) -> Step 8/Step 9 stay paired with no extra bookkeeping.

24 cells x 2 treatments (baseline, activity) x 50 HH x 2 years (2022, 2030) = 4,800 E+ runs total.

No local Step-9 driver existed before this (the cluster path used
step9_cluster/step9_idf_gen_full.py + a Stage-B SLURM array + Singularity). This script covers
IDF generation + E+ execution + hourly-meter extraction in one pass (all already done by
run_step8_paired_mc's engine), then builds step9_manifest.csv in the schema
step9_validate_full.py / step9_loadshape_aggregate.py expect: idx,cell,treatment,hh_id,year,idf_path,epw_path.

Output layout (matches the cluster script's expected glob idfs/<cell>/<arm>/<sample>/<year>/):
  <output-root>/idfs/<cell_label>/<treatment>/sample_XXX_HHnnnn/<year>/Scenario_<year>.idf
  <output-root>/idfs/<cell_label>/<treatment>/sample_XXX_HHnnnn/<year>/hourly_meters.csv
  <output-root>/idfs/<cell_label>/<treatment>/cell_manifest.csv   (written by run_paired_mc.py;
      NOT used to build step9_manifest.csv -- hh_id is read back from the directory name so a
      second treatment's manifest write can never mislabel the other treatment's households)
  <output-root>/step9_manifest.csv

Run (locally):
  cd 2J_docs_occ_nTemp/Step9_docs
  py run_step9_local.py --n 50 --workers 1 --ep-workers 18 --no-resume   # first launch
  py run_step9_local.py --dry-run                                       # resolve + plan only

Exit 0 = all units ok (manifest built); 1 = at least one unit failed (re-launch to resume).
"""
import argparse
import csv
import ctypes
import glob
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE    = os.path.dirname(os.path.abspath(__file__))          # .../Step9_docs
J2_DIR  = os.path.dirname(HERE)                                # .../2J_docs_occ_nTemp
REPO    = os.path.dirname(J2_DIR)                              # .../GSSCanada-main
S8DOCS  = os.path.join(J2_DIR, "Step8_docs")
sys.path.insert(0, S8DOCS)

from eSim_bem_utils_2J.main import BEM_SETUP_DIR                 # noqa: E402
from run_bem import all_cells, resolve_cell                       # noqa: E402

DRIVER = os.path.join(S8DOCS, "run_paired_mc.py")
BASELINE_SCHED_DIR = os.path.join(BEM_SETUP_DIR, "_step9_baseline_sched")
YEARS = ("2022", "2030")
TREATMENTS = ("baseline", "activity")
DEFAULT_ROOT = os.path.join(BEM_SETUP_DIR, "SimResults_Step9", "campaign_N50_2022_2030")

_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)

# --- Memory watchdog: identical pattern to Step 8's run_campaign_local.py ---------------------
_ACTIVE = {}
_ACTIVE_LOCK = threading.Lock()
_ABORT = threading.Event()


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def _committed_pct():
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
                  f"-> KILLING all units and aborting (peak {peak:.1f}%).", flush=True)
            _ABORT.set()
            _kill_active()
            return
        _ABORT.wait(interval)


def _count_hourly(unit_dir):
    n = 0
    for _root, _dirs, files in os.walk(unit_dir):
        n += sum(1 for f in files if f == "hourly_meters.csv")
    return n


def _run_unit(arch, city, treatment, n, seed, sim_mode, out_dir, log_dir, ep_workers):
    label = f"{arch}__{city}__{treatment}"
    log_path = os.path.join(log_dir, f"{label}.log")
    t0 = time.time()
    if _ABORT.is_set():
        return {"unit": label, "exit": -1, "status": "ABORTED", "minutes": 0.0, "log": log_path}
    child_env = dict(os.environ, ESIM_WORKERS=str(ep_workers))
    cmd = [sys.executable, DRIVER,
           "--archetype", arch, "--city", city,
           "--n", str(n), "--seed", str(seed), "--sim-mode", sim_mode,
           "--years", ",".join(YEARS),
           "--output-dir", out_dir]
    if treatment == "baseline":
        cmd += ["--sched-dir", BASELINE_SCHED_DIR]
    with open(log_path, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=S8DOCS, env=child_env)
        with _ACTIVE_LOCK:
            _ACTIVE[proc.pid] = proc
        try:
            rc = proc.wait()
        finally:
            with _ACTIVE_LOCK:
                _ACTIVE.pop(proc.pid, None)
    status = "ABORTED" if _ABORT.is_set() else ("ok" if rc == 0 else "FAILED")
    return {"unit": label, "exit": rc, "status": status,
            "minutes": round((time.time() - t0) / 60.0, 1), "log": log_path}


def build_manifest(root):
    """Walk <root>/idfs -> step9_manifest.csv (idx,cell,treatment,hh_id,year,idf_path,epw_path).
    hh_id is parsed from the sample_XXX_HHnnnn directory name, NOT from any cell_manifest.csv,
    so a treatment's manifest write can never mislabel the other treatment's households."""
    idfs_root = os.path.join(root, "idfs")
    rows = []
    idx = 0
    for cell_label in sorted(os.listdir(idfs_root)):
        cell_dir = os.path.join(idfs_root, cell_label)
        if not os.path.isdir(cell_dir) or "__" not in cell_label:
            continue
        arch, _, city = cell_label.partition("__")
        cell = resolve_cell(arch, city)
        if not cell:
            continue
        _idf, epw_path, _region, _dtype, _label = cell
        for treatment in TREATMENTS:
            treat_dir = os.path.join(cell_dir, treatment)
            if not os.path.isdir(treat_dir):
                continue
            for samp_name in sorted(os.listdir(treat_dir)):
                m = _RUN_RE.match(samp_name)
                if not m:
                    continue
                hh_id = m.group(2)
                samp_dir = os.path.join(treat_dir, samp_name)
                for year in YEARS:
                    idf_path = os.path.join(samp_dir, year, f"Scenario_{year}.idf")
                    if not os.path.exists(idf_path):
                        continue
                    rows.append({"idx": idx, "cell": cell_label, "treatment": treatment,
                                 "hh_id": hh_id, "year": year, "idf_path": idf_path,
                                 "epw_path": epw_path})
                    idx += 1
    manifest_path = os.path.join(root, "step9_manifest.csv")
    with open(manifest_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "cell", "treatment", "hh_id", "year",
                                          "idf_path", "epw_path"])
        w.writeheader()
        w.writerows(rows)
    print(f"[manifest] wrote {len(rows)} rows -> {manifest_path}")
    return manifest_path, len(rows)


def main():
    default_workers = max(1, (os.cpu_count() or 4) - 2)
    p = argparse.ArgumentParser(description="Parallel local Step 9 campaign runner (2022+2030).")
    p.add_argument("--n", type=int, default=50, help="households per cell (default 50).")
    p.add_argument("--seed", type=int, default=42, help="base seed (default 42, matches Step 8).")
    p.add_argument("--sim-mode", default="standard", choices=["standard", "weekly"])
    p.add_argument("--workers", type=int, default=default_workers,
                   help=f"concurrent (cell,treatment) units (default {default_workers} = cores-2). "
                        "Use --workers 1 --ep-workers K to keep only one unit's schedule set "
                        "(~1.5GB for 2 years) in RAM at a time -- see Step 8's memory-watchdog note.")
    p.add_argument("--ep-workers", type=int, default=1,
                   help="EnergyPlus processes PER unit (inner pool, via ESIM_WORKERS).")
    p.add_argument("--mem-abort", type=float, default=80.0)
    p.add_argument("--output-root", default=DEFAULT_ROOT)
    p.add_argument("--cells", default=None,
                   help="comma-separated cell labels (e.g. SingleD__Toronto_5A) to limit the run.")
    p.add_argument("--treatments", default=None,
                   help="comma-separated subset of {baseline,activity}; default = both.")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--manifest-only", action="store_true",
                   help="skip simulation; just (re)build step9_manifest.csv from existing outputs.")
    args = p.parse_args()

    if not os.path.isdir(BASELINE_SCHED_DIR) or not all(
            os.path.exists(os.path.join(BASELINE_SCHED_DIR, f"BEM_Schedules_{y}.csv")) for y in YEARS):
        print(f"ERROR: baseline hardlink dir missing/incomplete: {BASELINE_SCHED_DIR}\n"
              f"  Expected BEM_Schedules_{{2022,2030}}.csv hardlinked to the _baseline.csv originals.")
        sys.exit(2)

    root = args.output_root
    if args.manifest_only:
        build_manifest(root)
        return

    cells = all_cells()
    if args.cells:
        want = {s.strip() for s in args.cells.split(",") if s.strip()}
        cells = [(a, c) for a, c in cells if f"{a}__{c}" in want]
        missing = want - {f"{a}__{c}" for a, c in cells}
        if missing:
            print(f"ERROR: unknown --cells: {', '.join(sorted(missing))}", flush=True)
            sys.exit(2)
    treatments = TREATMENTS
    if args.treatments:
        treatments = tuple(s.strip() for s in args.treatments.split(",") if s.strip())
        bad = set(treatments) - set(TREATMENTS)
        if bad:
            print(f"ERROR: unknown --treatments: {bad}", flush=True)
            sys.exit(2)

    expected = args.n * len(YEARS)
    idfs_root = os.path.join(root, "idfs")
    log_dir = os.path.join(root, "_logs")
    os.makedirs(log_dir, exist_ok=True)

    units, todo, done, unresolved = [], [], [], []
    for arch, city in cells:
        if not resolve_cell(arch, city):
            unresolved.append(f"{arch}__{city}")
            continue
        for treatment in treatments:
            units.append((arch, city, treatment))

    for arch, city, treatment in units:
        cell_label = f"{arch}__{city}"
        label = f"{cell_label}__{treatment}"
        unit_dir = os.path.join(idfs_root, cell_label, treatment)
        if (not args.no_resume) and os.path.isdir(unit_dir) and _count_hourly(unit_dir) >= expected:
            done.append(label)
            continue
        todo.append((arch, city, treatment))

    print(f"=== Step 9 LOCAL campaign | {len(units)} units ({len(cells)} cells x {len(treatments)} "
          f"treatment(s)) | N={args.n} x {len(YEARS)} yr = {expected} runs/unit | "
          f"{len(units) * expected} total ===")
    print(f"  workers={args.workers}  ep-workers={args.ep_workers}  mem-abort={args.mem_abort}%  "
          f"mode={args.sim_mode}  years={YEARS}")
    print(f"  root   ={root}")
    print(f"  to run : {len(todo)} | done (resume-skip): {len(done)} | unresolved cells: {len(unresolved)}")
    if unresolved:
        print(f"  UNRESOLVED (missing IDF/EPW): {', '.join(unresolved)}")
    if args.dry_run:
        for a, c, t in todo:
            print(f"  would run: {a}__{c}__{t} -> {os.path.join(idfs_root, a + '__' + c, t)}")
        return
    if not todo:
        print("  Nothing to run (all units already complete).")
        build_manifest(root)
        return

    results = []
    t_start = time.time()
    wd = threading.Thread(target=_watchdog, args=(args.mem_abort,), daemon=True)
    wd.start()
    print(f"  watchdog ARMED at committed >= {args.mem_abort}% (polls every 3s)")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(_run_unit, a, c, t, args.n, args.seed, args.sim_mode,
                      os.path.join(idfs_root, f"{a}__{c}", t), log_dir, args.ep_workers):
                f"{a}__{c}__{t}"
            for a, c, t in todo
        }
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"  [{len(results)}/{len(todo)}] {r['status']:6s} {r['unit']:36s} "
                  f"exit={r['exit']}  {r['minutes']:6.1f} min", flush=True)

    _ABORT.set()
    status_csv = os.path.join(root, "campaign_status.csv")
    with open(status_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unit", "status", "exit", "minutes", "log"])
        for label in done:
            w.writerow([label, "ok(resume-skip)", 0, "", ""])
        for r in results:
            w.writerow([r["unit"], r["status"], r["exit"], r["minutes"], r["log"]])

    failed = [r["unit"] for r in results if r["status"] != "ok"]
    ok = len(results) - len(failed) + len(done)
    print(f"\n=== Campaign finished in {(time.time() - t_start) / 3600:.2f} h ===")
    print(f"  units ok: {ok}/{len(units)}  (newly run: {len(results) - len(failed)}, "
          f"resume-skip: {len(done)})")
    print(f"  status -> {status_csv}")
    if any(r["status"] == "ABORTED" for r in results):
        print("\n!!! ABORTED BY WATCHDOG -- committed-memory ceiling hit.")
        print("    Lower --ep-workers and re-launch (resume skips completed units).")
        sys.exit(1)
    if failed:
        print(f"  FAILED ({len(failed)}): {', '.join(failed)}")
        print("  -> re-launch the SAME command: completed units skip, failed/partial re-run.")
        sys.exit(1)
    print("  All units ok.")
    build_manifest(root)


if __name__ == "__main__":
    main()
