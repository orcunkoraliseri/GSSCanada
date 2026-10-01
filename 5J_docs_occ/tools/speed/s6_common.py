# -*- coding: utf-8 -*-
"""5J Step 6 part A shared code (Speed job only; Spain + Italy only; never a UK file).

TEST TRUTH IS NEVER READ in this part. What may be opened:
  * DRIVERS of the test runs (run table, building table, archetype tables, climates table, household folders, the copied store
    files): through open_driver(), which refuses any path under campaign/extracted/ and any path with a component starting with
    'uk', and logs (kind 'driver', run_id or '-', path).
  * B0 runs (the average-household runs of b0_dev and b0_test, which are MODEL INPUTS of the B0 prediction): through
    read_b0_truth(), which refuses any run id that is not in b0_dev or b0_test, and logs (kind 'b0', run_id, path).
Open logs live in /speed-scratch/o_iseri/5J/test/openlog_<tag>.tsv. check_openlogs() is the end check: a line fails if its kind is
not 'driver' or 'b0', if a 'driver' line points under campaign/extracted/, if a 'b0' line is not a b0_dev / b0_test run, or if
any line (any kind) points under campaign/extracted/ for a run outside b0_dev U b0_test.
Lists are read only through split_loader.load_split and only by these names: the three test lists, b0_dev, b0_test (and, for the
store builder's equality check against the Step 5 store, development, validation). Never `unused`, never loco_es / loco_it.
"""
import csv, io, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
import pandas as pd
import s5_common as c            # constants only; its allowed_ids() / open_run() are never used here (they refuse test runs)
import split_loader as sl

FIVE = c.FIVE
TEST = FIVE + "test/"
TSTORE = TEST + "store/"
TPRED = TEST + "pred/"
TRAIN_STORE = c.TRAIN + "store/"
EXTRACTED = c.CAMP + "extracted/"
TEST_LISTS = ("test_new_households", "test_new_buildings", "test_both_new")
B0_LISTS = ("b0_dev", "b0_test")
TRAIN_LISTS = ("development", "validation")          # only for the store builder's equality check against the Step 5 store
H = c.H
COUNTRIES = c.COUNTRIES
TARGETS = c.TARGETS
COP = c.COP

_L = {}
_RUNS = None


def lists():
    """The three test lists + b0_dev + b0_test, each through load_split (the lock file exists since the Step 4 freeze)."""
    if not _L:
        for nm in TEST_LISTS + B0_LISTS:
            _L[nm] = sl.load_split(nm)
    return _L


def train_lists():
    return {nm: sl.load_split(nm) for nm in TRAIN_LISTS}


def test_ids():
    L = lists()
    return [rid for nm in TEST_LISTS for rid in L[nm]]


def b0_ids():
    L = lists()
    return set(L["b0_dev"]) | set(L["b0_test"])


# ------------------------------------------------------------------------------------------------ guarded readers
def refuse_path(p):
    pl = p.replace("\\", "/")
    if pl.startswith(EXTRACTED) or "/campaign/extracted/" in pl:
        raise PermissionError("REFUSED: %s is under campaign/extracted/ (test truth is never read here)" % p)
    for comp in pl.split("/"):
        if comp.lower().startswith("uk"):
            raise PermissionError("REFUSED: %s has a component starting with 'uk' (UK licence)" % p)


def open_driver(path, log, run_id=None):
    """Returns `path` after the guard; logs (driver, run_id, path). The caller opens the file."""
    refuse_path(path)
    log.append(("driver", run_id or "-", path))
    return path


def runs(log):
    """Raw rows of the two run tables, run_id -> dict (a DRIVER file: run table of the campaign)."""
    global _RUNS
    if _RUNS is None:
        _RUNS = {}
        for cc in COUNTRIES:
            p = open_driver(c.CAMP + "in/campaign_runs_%s.csv" % cc, log)
            for r in csv.DictReader(io.open(p, encoding="utf-8")):
                assert r["country"] == cc and r["run_id"].startswith(cc + "_"), r["run_id"]
                _RUNS[r["run_id"]] = r
    return _RUNS


def placement(r):
    d = {}
    for item in r["placement"].split(";"):
        j, t = item.split(":", 1)
        d[int(j)] = t
    return d


def read_b0_truth(run_id, nd, log):
    """[nd, 8760, 4] float64 of ONE b0 run (b0_dev or b0_test only), checked like the scorer's reader. Logged kind 'b0'."""
    if run_id not in b0_ids():
        raise PermissionError("REFUSED: %s is not a b0_dev / b0_test run (only B0 runs may be read from campaign/extracted/)" % run_id)
    r = _RUNS[run_id]
    p = "%s%s/%s.csv.gz" % (EXTRACTED, r["climate_id"], run_id)
    log.append(("b0", run_id, p))
    df = pd.read_csv(p, comment="#", compression="gzip", usecols=["dwelling", "hour"] + TARGETS)
    if len(df) != nd * H:
        raise RuntimeError("%s: rows %d != %d" % (run_id, len(df), nd * H))
    df = df.sort_values(["dwelling", "hour"], kind="stable")
    if not (np.array_equal(df["dwelling"].to_numpy(), np.repeat(np.arange(nd), H)) and
            np.array_equal(df["hour"].to_numpy(), np.tile(np.arange(1, H + 1), nd))):
        raise RuntimeError("%s: dwelling or hour index wrong" % run_id)
    arr = df[TARGETS].to_numpy(dtype=float).reshape(nd, H, 4)
    if not np.isfinite(arr).all():
        raise RuntimeError("%s: non-finite values" % run_id)
    return arr


def flush_log(log, tag):
    p = TEST + "openlog_%s.tsv" % tag
    new = not os.path.exists(p)
    with io.open(p, "a", encoding="utf-8") as fh:
        if new:
            fh.write("kind\trun_id\tpath\n")
        for k, rid, pth in log:
            fh.write("%s\t%s\t%s\n" % (k, rid, pth))


# ------------------------------------------------------------------------------------------------ the end check on open logs
def check_lines(lines, b0set):
    """lines: iterable of (kind, run_id, path). Returns the list of offending lines with the reason."""
    bad = []
    for kind, rid, p in lines:
        pl = p.replace("\\", "/")
        under = pl.startswith(EXTRACTED) or "/campaign/extracted/" in pl
        if kind not in ("driver", "b0"):
            bad.append((kind, rid, p, "kind is neither driver nor b0"))
        elif kind == "driver" and under:
            bad.append((kind, rid, p, "driver line points under campaign/extracted/"))
        elif kind == "b0" and rid not in b0set:
            bad.append((kind, rid, p, "b0 line for a run outside b0_dev / b0_test"))
        elif under and rid not in b0set:
            bad.append((kind, rid, p, "extracted/ file of a run outside b0_dev / b0_test"))
        if any(comp.lower().startswith("uk") for comp in pl.split("/")):
            bad.append((kind, rid, p, "UK path"))
    return bad


def read_log_file(p):
    out = []
    for ln in io.open(p, encoding="utf-8").read().splitlines()[1:]:
        if ln.strip():
            k, rid, pth = ln.split("\t")
            out.append((k, rid, pth))
    return out
