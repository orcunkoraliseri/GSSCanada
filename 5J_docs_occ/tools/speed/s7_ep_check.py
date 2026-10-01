# -*- coding: utf-8 -*-
"""Step 7 part F checks: G5J.1-style integrity (the campaign's camp_integrity.py, subset mode, unchanged) over the pilot runs, then timing.
Expected NOT_EVALUABLE in subset mode: C10 (no replicate runs in a district table) and C11 (no B0 runs); C12 is skipped. Everything else must PASS."""
import io, json, os, statistics, sys
import s7_common as s7
assert os.environ.get("CAMP_ROOT", "").startswith(s7.D), "CAMP_ROOT must be under district/"
cc = s7.install_twins()
table = os.environ.get("S7_TABLE", s7.IN + "district_runs_es_pilot.csv")
ids = os.environ.get("S7_IDS", s7.D + "ep/pilot_ids.txt")
runs = s7.read_csv(table)
cc.load_runs = lambda: runs
import camp_integrity


def timing():
    rows = []
    for r in runs:
        p = cc.done_json(r["run_id"])
        if not os.path.exists(p):
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        rows.append((r, d))
    ok = [(r, d) for r, d in rows if d.get("status") == "pass"]
    print("TIMING runs in table=%d done json=%d pass=%d" % (len(runs), len(rows), len(ok)))
    if not ok:
        return
    wall = [d["wall_seconds_incl_build_extract"] for r, d in ok]
    ep = [d["seconds"] for r, d in ok]
    nd = [int(r["n_dwellings"]) for r, d in ok]
    print("TIMING_PER_RUN wall(build+run+extract) median=%.1f s mean=%.1f s ; EnergyPlus only median=%.1f s ; total wall=%.0f s = %.2f CPU-h" % (statistics.median(wall), sum(wall) / len(wall), statistics.median(ep), sum(wall), sum(wall) / 3600.0))
    print("TIMING_PER_DWELLING_YEAR wall median over runs=%.3f s ; total wall / total dwellings=%.3f s (dwellings=%d)" % (statistics.median([w_ / n for w_, n in zip(wall, nd)]), sum(wall) / sum(nd), sum(nd)))
    for cls in s7.CLASSES:
        sub = [(d["wall_seconds_incl_build_extract"], int(r["n_dwellings"])) for r, d in ok if r["class"] == cls]
        if sub:
            print("TIMING_CLASS %s runs=%d median wall=%.1f s per run ; %.3f s per dwelling" % (cls, len(sub), statistics.median([a for a, _ in sub]), sum(a for a, _ in sub) / sum(n for _, n in sub)))
    print("TIMING_HOSTS %s" % sorted({d.get("host") for r, d in ok}))
    rss = [int(d["max_rss_kb"]) for r, d in ok if d.get("max_rss_kb")]
    if rss:
        print("TIMING_RSS max=%d kB" % max(rss))
    print("TIMING_FAILED %s" % [r["run_id"] for r, d in rows if d.get("status") != "pass"][:10])


if __name__ == "__main__":
    sys.argv = ["camp_integrity.py", "--ids", ids, "--workers", "2"]
    try:
        camp_integrity.main()
    except SystemExit as e:
        print("INTEGRITY_EXIT_CODE", e.code)
    timing()
