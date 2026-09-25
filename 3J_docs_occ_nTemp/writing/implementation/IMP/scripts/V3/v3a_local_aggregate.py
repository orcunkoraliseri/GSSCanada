"""V3a LOCAL aggregation (2026-09-25): the Windows equivalent of v3a_aggregate.sh.

    py -3 v3a_local_aggregate.py <runs_root> <agg_root> [--slim]

For each seed k in {42,101,202,303,404}: builds <runs_root>/agg_in/seed<k>/<cell_tag> as directory
JUNCTIONS (no copy, no admin rights) to <runs_root>/V3a/S__<cell_tag>__s<k>, then runs the Step-8E
aggregator exactly as v3a_aggregate.sh does:
    3rdJ_08E_aggregate_4split.py --campaign-dir agg_in/seed<k> --outdir <agg_root>/seed<k>
                                 --eplus-idd <IDD> --idf-name injected_resized.idf
with PYTHONPATH=<repo>/eSim. Refuses if a seed has fewer than 8 status=ok cells.
--allow-partial: aggregate each seed over whatever cells are status=ok (for an interrupted run; the output
must be reported as PARTIAL). Never combined with --slim in practice.
--slim: AFTER all five aggregations exit 0, shrinks every run/eplusout.sql with IMP/scripts/p10r_slim_sql.py
(keeps only what the aggregator reads; the P10R arm's own agg_P10R was built from slimmed SQLs).
Exit 0 = all five aggregations ok.
"""
import _winapi
import datetime as dt
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_lib as L  # noqa: E402

SEEDS = (42, 101, 202, 303, 404)
AGG = os.path.join(L.S8, "3rdJ_08E_aggregate_4split.py")
SLIM = os.path.join(HERE, "..", "p10r_slim_sql.py")


def log(msg):
    print("%s %s" % (dt.datetime.now(dt.timezone.utc).isoformat(), msg), flush=True)


def main():
    runs_root, agg_root = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    slim = "--slim" in sys.argv[3:]
    partial = "--allow-partial" in sys.argv[3:]   # PARTIAL mode: aggregate whatever cells are ok (reported as partial)
    for bad in ("agg_P10R", "agg_deliverable", "campaign_local_deliverable"):
        if bad in agg_root.split(os.sep) or os.path.basename(agg_root) == bad:
            raise SystemExit("REFUSING: agg_root is a frozen/P10R tree: %s" % agg_root)
    env = dict(os.environ, PYTHONPATH=L.INJ_ROOT)
    for s in SEEDS:
        src = sorted(glob.glob(os.path.join(runs_root, "V3a", "S__*__s%d" % s)))
        ok = [d for d in src if json.load(open(os.path.join(d, "manifest.json"))).get("status") == "ok"]
        log("[agg] seed %d: %d run dirs, %d status=ok" % (s, len(src), len(ok)))
        if partial and not ok:
            log("[agg] seed %d: no ok cell, skipped (partial mode)" % s)
            continue
        if len(ok) != 8 and not partial:
            raise SystemExit("REFUSING: seed %d has %d ok cells, expected 8" % (s, len(ok)))
        inp = os.path.join(runs_root, "agg_in", "seed%d" % s)
        os.makedirs(inp, exist_ok=True)
        for d in ok:
            tag = json.load(open(os.path.join(d, "manifest.json")))["cell_tag"]
            j = os.path.join(inp, tag)
            if not os.path.exists(j):
                _winapi.CreateJunction(d, j)
            if os.path.realpath(j) != os.path.realpath(d):
                raise SystemExit("REFUSING: junction %s -> %s, expected %s" % (j, os.path.realpath(j), d))
        out = os.path.join(agg_root, "seed%d" % s)
        cmd = ["py", "-3", "-u", AGG, "--campaign-dir", inp, "--outdir", out, "--eplus-idd", L.IDD,
               "--idf-name", "injected_resized.idf"]
        log("[agg] " + " ".join(cmd))
        rc = subprocess.run(cmd, env=env).returncode
        log("[agg] seed %d exit=%d" % (s, rc))
        if rc != 0:
            return 1
    if slim:
        for s in SEEDS:
            for d in sorted(glob.glob(os.path.join(runs_root, "V3a", "S__*__s%d" % s))):
                rc = subprocess.run(["py", "-3", SLIM, d]).returncode
                log("[slim] %s exit=%d" % (os.path.basename(d), rc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
