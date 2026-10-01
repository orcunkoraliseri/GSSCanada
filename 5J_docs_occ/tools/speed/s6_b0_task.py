# -*- coding: utf-8 -*-
"""5J Step 6 part C: B0 predictions for every run of the three test lists (Speed job only; Spain + Italy only).
B0 of a run = the b0 run (average household, pool b0) of the SAME building and climate, flat by flat: b0_dev for development buildings,
b0_test for test buildings (the building key decides: every (climate, building) group must have exactly one b0 run in b0_dev U b0_test).
heating, cooling, equipment copied; total_elec = equipment + (heating + cooling)/3.0 (R3), written with s5_b0.write_pred (same layout).
The b0 runs' own extracted files are read (B0 INPUTS, log kind 'b0'); no other truth file is opened (s6_common.read_b0_truth refuses).
Output: /speed-scratch/o_iseri/5J/test/pred/B0/<climate>/<run_id>.csv.gz ; open log: test/openlog_b0.tsv."""
import sys, os, time, multiprocessing as mp
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import s6_common as s6
import s5_common as c
import s5_b0 as b0mod

OUT = s6.TPRED + "B0/"
b0mod.OUT = OUT              # s5_b0.write_pred writes into this folder (module constant)


def work(task):
    log = []
    try:
        cl, b0id, rids, nd = task["climate"], task["b0"], task["runs"], task["nd"]
        e = s6.read_b0_truth(b0id, nd, log)
        pred = e.copy()
        pred[:, :, 3] = e[:, :, 2] + (e[:, :, 0] + e[:, :, 1]) / c.COP
        dtot = float(np.abs(pred[:, :, 3] - e[:, :, 3]).max())
        for rid in rids:
            b0mod.write_pred(cl, rid, pred, "copy of the b0 run %s (same building and climate), total_elec = equipment + (heating + cooling)/3.0" % b0id)
        return task["key"], None, log, dtot, len(rids)
    except Exception as ex:
        return task["key"], str(ex)[:200], log, 0.0, 0


def main():
    t0 = time.time()
    olp = s6.TEST + "openlog_b0.tsv"
    if os.path.exists(olp):
        os.remove(olp)
    if os.path.exists(OUT) and os.listdir(OUT):
        print("REFUSED: %s already holds files" % OUT)
        sys.exit(4)
    L = s6.lists()
    mainlog = []
    R = s6.runs(mainlog)
    b0 = {}
    dup = []
    for lst in s6.B0_LISTS:
        for rid in L[lst]:
            r = R[rid]
            assert r["pool"] == "b0", (rid, r["pool"])
            key = (r["climate_id"], r["building_id"])
            if key in b0:
                dup.append((key, b0[key][0], rid))
            b0[key] = (rid, lst)
    print("CHECK b0_no_building_in_both_b0_dev_and_b0_test %s duplicates=%d %s" % ("PASS" if not dup else "FAIL", len(dup), dup[:3]), flush=True)
    if dup:
        sys.exit(3)
    groups, byl = {}, {}
    for nm in s6.TEST_LISTS:
        for rid in L[nm]:
            r = R[rid]
            groups.setdefault((r["climate_id"], r["building_id"]), []).append(rid)
            byl[rid] = nm
    tasks, nomatch, used = [], [], {"b0_dev": 0, "b0_test": 0}
    cross = {}
    for (cl, b), rids in groups.items():
        if (cl, b) not in b0:
            nomatch.append((cl, b))
            continue
        b0id, lst = b0[(cl, b)]
        used[lst] += len(rids)
        for x in rids:
            k = (R[x].get("building_split", "?"), lst)
            cross[k] = cross.get(k, 0) + 1
        nds = {int(R[x]["n_dwellings"]) for x in rids + [b0id]}
        if len(nds) != 1:
            nomatch.append((cl, b, "dwelling counts differ"))
            continue
        tasks.append({"key": "%s|%s" % (cl, b), "climate": cl, "building": b, "b0": b0id, "runs": sorted(rids), "nd": nds.pop()})
    print("INFO B0 groups: test (climate,building) groups=%d with a b0 run=%d without=%d %s" % (len(groups), len(tasks), len(nomatch), nomatch[:3]), flush=True)
    print("INFO B0 source list by test runs: %s ; building_split (run table) x b0 list used: %s" % (used, sorted(cross.items())), flush=True)
    if nomatch:
        print("CHECK b0_every_group_has_a_b0_run FAIL", nomatch[:5], flush=True)
        sys.exit(3)
    print("CHECK b0_every_group_has_a_b0_run PASS groups=%d" % len(tasks), flush=True)
    tasks.sort(key=lambda t: -len(t["runs"]) * t["nd"])
    errs, nlog, nrun, worst = [], [], 0, 0.0
    with mp.Pool(int(os.environ.get("SLURM_CPUS_PER_TASK", "4"))) as pool:
        for i, (k, e, lg, dt, n) in enumerate(pool.imap_unordered(work, tasks, chunksize=1)):
            nlog.extend(lg)
            nrun += n
            worst = max(worst, dt)
            if e:
                errs.append((k, e))
            if (i + 1) % 50 == 0:
                print("  progress %d/%d groups" % (i + 1, len(tasks)), flush=True)
    s6.flush_log(mainlog + nlog, "b0")
    badl = s6.check_lines(s6.read_log_file(olp), s6.b0_ids())
    n_expected = sum(len(L[nm]) for nm in s6.TEST_LISTS)
    print("B0 written: runs=%d groups=%d errors=%d %s" % (nrun, len(tasks), len(errs), errs[:3]), flush=True)
    for nm in s6.TEST_LISTS:
        print("COUNT model=B0 list=%s runs_expected=%d" % (nm, len(L[nm])), flush=True)
    print("CHECK b0_run_count %s written=%d expected=%d" % ("PASS" if nrun == n_expected else "FAIL", nrun, n_expected), flush=True)
    print("INFO b0 max abs diff between equipment+(heating+cooling)/3.0 and the b0 run's own total_elec = %.3e kWh (formula used)" % worst, flush=True)
    kinds = sorted({k for k, _, _ in s6.read_log_file(olp)})
    print("CHECK b0_openlog_kinds_driver_or_b0_and_only_b0_runs_under_extracted %s log_lines=%d kinds=%s distinct_b0_runs_read=%d offending=%d" % (
        "PASS" if not badl else "FAIL", len(s6.read_log_file(olp)), kinds, len({x[1] for x in nlog}), len(badl)), flush=True)
    ok = (not errs) and nrun == n_expected and not badl
    print("B0_DONE", "OK" if ok else "FAILED", "seconds=%.0f" % (time.time() - t0), flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
