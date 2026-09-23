#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p10r_local_campaign.py -- local Windows driver for the 56-cell P10R campaign, INSIDE a tight
C: disk budget. (Speed carries the full 56-cell run, `IMP/P10R_fix.md` A5; this is the local
fallback, task doc `IMP/P10R_fix.md` "### B-local".)

For each of the 56 cells `3rdJ_08D_campaign_cells.build_campaign_cells()` returns, runs
`3rdJ_08D_campaign_cell_P10R.py --tag <tag> --outroot campaign_local_P10R`, N at a time
(--workers, default 4). The one cell already built by the P10R agent (A4,
`campaign_local_P10R/B_central__Tall__MTL/`) is kept and only slimmed, not re-run, when its
manifest already says `P10R_STATUS=ok`. As soon as a cell finishes ok, `p10r_slim_sql.py` runs on
it immediately (eplusout.sql never sits at its full ~160 MB for longer than one cell's worth of
time). Before starting ANY cell, waits while C: free space < --min-free-gb (default 3), logging
the wait every 60 s. A cell that fails (non-zero exit or a manifest that does not read back ok)
is retried once; a second failure is recorded as failed and the driver moves on -- it never
aborts the whole campaign for one bad cell. One status line per cell goes to
`campaign_local_P10R/_logs/driver.log` (and stdout). At the end (unless --skip-aggregate) runs the
Step-8E aggregator with an EXPLICIT --outdir into `outputs_step8/agg_P10R/` -- NEVER the default
`outputs_step8/agg/` -- and prints `DRIVER DONE ok=<n> failed=<m>`.

Writes ONLY inside `campaign_local_P10R/`, `outputs_step8/agg_P10R/` and its own log file. Never
touches the frozen arms, `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`,
`eSim_dynamicML_mHead_alignment.py`, or any file outside those two trees.

USAGE (from `Leg3_4-split/Step8_docs/`, Git Bash)
  PYTHONIOENCODING=utf-8 py -3 p10r_local_campaign.py --dry-run
      shows the 56-cell plan (which are already kept) and the current free-space reading; no work.
  PYTHONIOENCODING=utf-8 py -3 p10r_local_campaign.py --limit 2 --workers 1
      smoke test: runs the first 2 not-yet-ok cells only, 1 at a time, then aggregates just those.
  PYTHONIOENCODING=utf-8 py -3 p10r_local_campaign.py
      the real 56-cell run (default --workers 4 --min-free-gb 3).
"""
from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

THIS_DIR = os.path.dirname(os.path.abspath(__file__))         # writing/implementation/IMP/scripts
J3 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(THIS_DIR))))  # 3J_docs_occ_nTemp
REPO = os.path.dirname(J3)                                     # GSSCanada-main
LEG3 = os.path.join(J3, "Leg3_4-split")
STEP8 = os.path.join(LEG3, "Step8_docs")                       # where the campaign + aggregator live

OUTROOT = os.path.join(STEP8, "campaign_local_P10R")
AGG_OUT = os.path.join(STEP8, "outputs_step8", "agg_P10R")
LOG_DIR = os.path.join(OUTROOT, "_logs")
LOG_FILE = os.path.join(LOG_DIR, "driver.log")

RUNNER = os.path.join(STEP8, "3rdJ_08D_campaign_cell_P10R.py")
SLIMMER = os.path.join(THIS_DIR, "p10r_slim_sql.py")
AGGREGATOR = os.path.join(STEP8, "3rdJ_08E_aggregate_4split.py")
CELLS_SCRIPT = os.path.join(STEP8, "3rdJ_08D_campaign_cells.py")
STEP7_P10R = os.path.join(LEG3, "Step7_docs", "outputs_step7_P10R")
PY = ["py", "-3"]  # project convention: never bare `python`

_LOG_LOCK = threading.Lock()


def _load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    with _LOG_LOCK:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    print(line, flush=True)


def free_gb(path: str = "C:\\") -> float:
    free = ctypes.c_ulonglong(0)
    ok = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(path), None, None, ctypes.pointer(free))
    if not ok:
        raise OSError("GetDiskFreeSpaceExW failed")
    return free.value / 1e9


def wait_for_disk(min_free_gb: float) -> None:
    while True:
        f = free_gb()
        if f >= min_free_gb:
            return
        log(f"[disk] {f:.2f} GB free < {min_free_gb:.2f} GB minimum -- waiting 60 s")
        time.sleep(60)


def cell_ok(cell_dir: str) -> bool:
    mpath = os.path.join(cell_dir, "manifest.json")
    if not os.path.isfile(mpath):
        return False
    try:
        with open(mpath, "r", encoding="utf-8") as f:
            man = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    if man.get("P10R_STATUS") != "ok":
        return False
    for name in ("channel_hourly.csv", "hourly_meters.csv", "injected_resized.idf"):
        if not os.path.isfile(os.path.join(cell_dir, name)):
            return False
    return True


def slim(cell_dir: str) -> None:
    sql = os.path.join(cell_dir, "run", "eplusout.sql")
    tag = os.path.basename(cell_dir.rstrip("\\/"))
    if not os.path.isfile(sql):
        log(f"[slim] {tag}: no run/eplusout.sql (already slim or cell has none)")
        return
    r = subprocess.run(PY + [SLIMMER, cell_dir], capture_output=True, text=True,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode == 0:
        log(f"[slim] {tag}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'done'}")
    else:
        log(f"[slim] {tag}: FAILED rc={r.returncode} {(r.stderr or r.stdout).strip()[-400:]}")


def run_one_cell(tag: str, min_free_gb: float) -> tuple:
    cell_dir = os.path.join(OUTROOT, tag)
    if cell_ok(cell_dir):
        log(f"[skip] {tag}: existing manifest P10R_STATUS=ok, kept")
        slim(cell_dir)
        return tag, "ok"
    for attempt in (1, 2):
        wait_for_disk(min_free_gb)
        log(f"[{'run' if attempt == 1 else 'retry'}] {tag} attempt={attempt}")
        r = subprocess.run(PY + [RUNNER, "--tag", tag, "--outroot", OUTROOT],
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if r.returncode == 0 and cell_ok(cell_dir):
            log(f"[ok] {tag} attempt={attempt}")
            slim(cell_dir)
            return tag, "ok"
        log(f"[fail] {tag} attempt={attempt} exit={r.returncode}")
    log(f"[failed] {tag}: both attempts failed")
    return tag, "failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--min-free-gb", type=float, default=3.0)
    ap.add_argument("--limit", type=int, default=None,
                     help="run only the first N not-yet-ok cells; 0 = plan only (= --dry-run)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-aggregate", action="store_true")
    a = ap.parse_args()

    cells_mod = _load(CELLS_SCRIPT, "p10r_cells_driver")
    cells = cells_mod.build_campaign_cells(REPO, step7_out=STEP7_P10R)
    tags = [c["tag"] for c in cells]
    assert len(tags) == 56, f"expected 56 cells from build_campaign_cells(), got {len(tags)}"

    existing_ok = [t for t in tags if cell_ok(os.path.join(OUTROOT, t))]
    todo = [t for t in tags if t not in existing_ok]

    print(f"[plan] outroot={OUTROOT}")
    print(f"[plan] 56 cells total; {len(existing_ok)} already ok (kept, only re-slimmed): "
          f"{existing_ok}")
    print(f"[plan] {len(todo)} still to run; workers={a.workers} min_free_gb={a.min_free_gb} "
          f"skip_aggregate={a.skip_aggregate}")
    print(f"[plan] current C: free space: {free_gb():.2f} GB")

    dry = a.dry_run or a.limit == 0
    if dry:
        for i, t in enumerate(tags):
            tag_status = "KEEP(ok)" if t in existing_ok else "run"
            print(f"  [{i:2d}] {t}  -- {tag_status}")
        print(f"[plan] aggregate target: {AGG_OUT}")
        print(f"[plan] log file: {LOG_FILE}")
        print("[dry-run] no work done")
        return

    run_tags = todo[: a.limit] if a.limit else todo
    kept_tags = [t for t in existing_ok if t not in run_tags]

    os.makedirs(LOG_DIR, exist_ok=True)
    log(f"[start] {len(run_tags)} cells to run + {len(kept_tags)} kept, workers={a.workers}, "
        f"min_free_gb={a.min_free_gb}")

    ok_n = failed_n = 0
    for t in kept_tags:
        tag, status = run_one_cell(t, a.min_free_gb)  # cell_ok short-circuits to skip+slim
        ok_n += status == "ok"
        failed_n += status != "ok"

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        futs = {ex.submit(run_one_cell, t, a.min_free_gb): t for t in run_tags}
        for fut in as_completed(futs):
            tag, status = fut.result()
            ok_n += status == "ok"
            failed_n += status != "ok"

    log(f"[campaign] ok={ok_n} failed={failed_n}")

    if a.skip_aggregate:
        print(f"DRIVER DONE ok={ok_n} failed={failed_n} (aggregate skipped)")
        return

    os.makedirs(AGG_OUT, exist_ok=True)
    agg_cmd = PY + [AGGREGATOR, "--campaign-dir", OUTROOT, "--outdir", AGG_OUT,
                     "--idf-name", "injected_resized.idf"]
    log(f"[aggregate] {' '.join(agg_cmd)}")
    r = subprocess.run(agg_cmd, env={**os.environ, "PYTHONIOENCODING": "utf-8",
                                      "PYTHONPATH": os.path.join(REPO, "eSim")})
    log(f"[aggregate] exit={r.returncode}")
    print(f"DRIVER DONE ok={ok_n} failed={failed_n}")


if __name__ == "__main__":
    main()
