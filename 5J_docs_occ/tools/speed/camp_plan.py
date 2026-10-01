# -*- coding: utf-8 -*-
"""5J campaign plan (Speed job only: it hashes files). Usage: python -u camp_plan.py
Reads the two frozen run tables, cuts each country x climate array into blocks of about 40 min estimated time (run
positions fixed by table order, replicates last), writes PLAN/<array>/block_<n>.csv, PLAN/plan.csv, PLAN/nblocks.txt.
A run is DONE only if DONE/<run_id>.json has status pass AND its cache_key equals the key recomputed from the current inputs.
Prints: PLAN total=.. done=.. todo=..   (and one PLAN_ARRAY line per array)
"""
import csv, io, os, sys
import camp_common as cc


def main():
    runs = cc.load_runs()
    by = {}
    for r in runs:
        by.setdefault(r["climate_id"], []).append(r)
    os.makedirs(cc.PLAN, exist_ok=True)
    plan_rows = []
    nblocks = []
    tot = done = 0
    cols = list(runs[0].keys())
    for arr in cc.ARRAYS:
        rs = by.get(arr, [])
        if not rs:
            continue
        # replicate runs at the end of the array, table order otherwise (stable sort)
        rs = sorted(rs, key=lambda r: 1 if int(r["replicate"]) > 0 else 0)
        blocks, cur, cum = [], [], 0.0
        for r in rs:
            e = cc.est_seconds(r)
            if cur and cum + e > cc.TARGET_BLOCK_S:
                blocks.append(cur)
                cur, cum = [], 0.0
            cur.append((r, e))
            cum += e
        if cur:
            blocks.append(cur)
        adir = cc.PLAN + arr + "/"
        os.makedirs(adir, exist_ok=True)
        for f in os.listdir(adir):
            if f.startswith("block_") and f.endswith(".csv"):
                os.remove(adir + f)
        a_done = 0
        pos = 0
        for bi, blk in enumerate(blocks, 1):
            with io.open(adir + "block_%d.csv" % bi, "w", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(cols + ["pos", "est_s"])
                for r, e in blk:
                    pos += 1
                    w.writerow([r[c] for c in cols] + [pos, "%.1f" % e])
                    key = cc.cache_key(r)
                    d = 1 if cc.is_done(r["run_id"], key) else 0
                    a_done += d
                    plan_rows.append([r["run_id"], arr, bi, pos, "%.1f" % e, key, d])
        est = sum(e for b in blocks for _r, e in b)
        print("PLAN_ARRAY %s runs=%d blocks=%d est_total_s=%.0f done=%d todo=%d" % (arr, len(rs), len(blocks), est, a_done, len(rs) - a_done))
        nblocks.append((arr, len(blocks)))
        tot += len(rs)
        done += a_done
    with io.open(cc.PLAN + "plan.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["run_id", "array", "block", "pos", "est_s", "cache_key", "done"])
        w.writerows(plan_rows)
    with io.open(cc.PLAN + "nblocks.txt", "w", encoding="utf-8") as fh:
        for a, n in nblocks:
            fh.write("%s %d\n" % (a, n))
    ids = [p[0] for p in plan_rows]
    assert len(ids) == len(set(ids)) == tot, "duplicate run_id in the plan"
    print("PLAN total=%d done=%d todo=%d" % (tot, done, tot - done))
    # the todo list, for the smoke test and the manager
    with io.open(cc.PLAN + "todo_ids.txt", "w", encoding="utf-8") as fh:
        for p in plan_rows:
            if p[6] == 0:
                fh.write(p[0] + "\n")


if __name__ == "__main__":
    main()
