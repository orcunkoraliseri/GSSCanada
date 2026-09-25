"""V3a LOCAL driver (2026-09-25): runs the 40 rows of tasks_v3a.csv on this Windows box, at most
MAX_PAR at once, each as `py -3 v3_task.py <tasks.csv> <id> <runs_root>` (one EnergyPlus per task).

    py -3 v3a_local_driver.py <runs_root> [--max-par 10] [--ids 0,1,...]

<runs_root> must contain the text `campaign_local_P10R` so that the RAM guard
(IMP/scripts/p10r_mem_watchdog.ps1) matches this driver, every task and every energyplus.exe.
Logs every start/finish with UTC time to <runs_root>/_logs/driver.log, and every 60 s the RAM in use and
the number of live energyplus.exe (so the peak RAM and the "never more than MAX_PAR" rule can be read
back). A failed task is retried once. Tasks already status=ok are skipped by v3_task.py itself.
Longest tasks (SuperTall) are started first. Exit 0 = all ok, 1 = some task failed after the retry.
"""
import argparse
import csv
import datetime as dt
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(HERE, "tasks_v3a.csv")
LOCK = threading.Lock()
LOG = None
STOP = threading.Event()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(msg):
    line = "%s %s" % (utc(), msg)
    with LOCK:
        print(line, flush=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def ram_and_ep():
    """(RAM used %, number of live energyplus.exe) via wmic-free PowerShell-free calls."""
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    used = 100.0 * (1 - m.ullAvailPhys / m.ullTotalPhys)
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq energyplus.exe", "/NH"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, universal_newlines=True).stdout
    n_ep = sum(1 for l in out.splitlines() if l.lower().startswith("energyplus"))
    return used, n_ep


def sampler():
    peak_ram, peak_ep = 0.0, 0
    while not STOP.is_set():
        try:
            used, n_ep = ram_and_ep()
            peak_ram, peak_ep = max(peak_ram, used), max(peak_ep, n_ep)
            log("[mem] used=%.1f%% energyplus=%d (peak so far used=%.1f%% energyplus=%d)"
                % (used, n_ep, peak_ram, peak_ep))
        except Exception as e:  # never let the sampler kill the driver
            log("[mem] sampler error %r" % e)
        STOP.wait(60)


def run_task(tid, label, runs_root, logs):
    for attempt in (1, 2):
        log("[start] task=%d %s attempt=%d" % (tid, label, attempt))
        t0 = time.time()
        with open(os.path.join(logs, "task_%02d_attempt%d.log" % (tid, attempt)), "w", encoding="utf-8") as fo:
            rc = subprocess.run(["py", "-3", "-u", os.path.join(HERE, "v3_task.py"), TASKS, str(tid), runs_root],
                                stdout=fo, stderr=subprocess.STDOUT, cwd=HERE).returncode
        log("[finish] task=%d %s attempt=%d rc=%d %.0fs" % (tid, label, attempt, rc, time.time() - t0))
        if rc == 0:
            return tid, True, attempt
    return tid, False, 2


def main():
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("runs_root")
    ap.add_argument("--max-par", type=int, default=10)
    ap.add_argument("--ids", default="")
    a = ap.parse_args()
    runs_root = os.path.abspath(a.runs_root)
    if "campaign_local_P10R" not in runs_root or os.path.basename(runs_root) == "campaign_local_P10R":
        raise SystemExit("REFUSING: runs_root must contain campaign_local_P10R (guard match) and must not BE "
                         "the P10R campaign dir: %s" % runs_root)
    if a.max_par > 10:
        raise SystemExit("REFUSING: --max-par %d > 10" % a.max_par)
    logs = os.path.join(runs_root, "_logs")
    os.makedirs(logs, exist_ok=True)
    LOG = os.path.join(logs, "driver.log")
    rows = list(csv.DictReader(open(TASKS)))
    if a.ids:
        keep = {int(x) for x in a.ids.split(",")}
        rows = [r for r in rows if int(r["task_id"]) in keep]
    # task 0 (Tall/MTL, the shortest) first, so a broken chain shows within ~10 min; then SuperTall first
    rows.sort(key=lambda r: (int(r["task_id"]) != 0, r["building"] != "SuperTall", int(r["task_id"])))
    log("[driver] start runs_root=%s tasks=%d max_par=%d tasks_csv=%s" % (runs_root, len(rows), a.max_par, TASKS))
    th = threading.Thread(target=sampler, daemon=True)
    th.start()
    results = []
    with ThreadPoolExecutor(max_workers=a.max_par) as ex:
        futs = [ex.submit(run_task, int(r["task_id"]),
                          "%s__%s__%s__s%s" % (r["scenario"], r["building"], r["city"], r["seed"]), runs_root, logs)
                for r in rows]
        for f in futs:
            results.append(f.result())
    STOP.set()
    ok = [t for t, s, _ in results if s]
    bad = [t for t, s, _ in results if not s]
    retried = [t for t, s, n in results if n == 2]
    log("[driver] done ok=%d failed=%d retried=%s failed_ids=%s" % (len(ok), len(bad), retried, bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
