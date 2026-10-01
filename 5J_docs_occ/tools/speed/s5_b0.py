# -*- coding: utf-8 -*-
"""5J Step 5 part C: B0 predictions (rules R4). Speed job only; Spain + Italy only.
For each validation run, write /speed-scratch/o_iseri/5J/train/pred/B0/<climate>/<run_id>.csv.gz (scorer layout, copied from
frz_standins.write_pred) = the average-household EnergyPlus run (pool b0) of the SAME building and climate, flat by flat:
heating, cooling, equipment copied; total_elec = equipment + (heating + cooling)/3.0 (R3). The B0 run's own total_elec column is
compared and the max difference printed. b0_val is used first; a building whose b0 run is in b0_dev falls back to b0_dev (printed).
Every file open goes through s5_common.open_run (allowed lists only); open log: train/openlog_b0.tsv."""
import sys, os, io, gzip, time, multiprocessing as mp
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import s5_common as c

OUT = c.TRAIN + "pred/B0/"
H = c.H


def write_pred(climate, rid, arr, note):
    d = "%s%s/" % (OUT, climate)
    os.makedirs(d, exist_ok=True)
    nd = arr.shape[0]
    df = pd.DataFrame({"dwelling": np.repeat(np.arange(nd), H), "hour": np.tile(np.arange(1, H + 1), nd)})
    for i, t in enumerate(c.TARGETS):
        df[t] = arr[:, :, i].reshape(-1)
    with open(d + rid + ".csv.gz", "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            txt = io.TextIOWrapper(gz, encoding="utf-8", newline="")
            txt.write("# 5J Step 5 baseline 'B0' for run %s: %s\n" % (rid, note))
            df.to_csv(txt, index=False, float_format="%.8g")
            txt.flush()
            txt.detach()


def work(task):
    log = []
    try:
        cl, b, b0id, rids, nd = task["climate"], task["building"], task["b0"], task["runs"], task["nd"]
        e = c.read_truth(b0id, nd, log, "b0_truth")
        pred = e.copy()
        pred[:, :, 3] = e[:, :, 2] + (e[:, :, 0] + e[:, :, 1]) / c.COP
        dtot = float(np.abs(pred[:, :, 3] - e[:, :, 3]).max())
        for rid in rids:
            write_pred(cl, rid, pred, "copy of the b0 run %s (same building and climate), total_elec = equipment + (heating + cooling)/3.0" % b0id)
        return task["key"], None, log, dtot, len(rids)
    except Exception as ex:
        return task["key"], str(ex)[:200], log, 0.0, 0


def main():
    t0 = time.time()
    olp = c.TRAIN + "openlog_b0.tsv"
    if os.path.exists(olp):
        os.remove(olp)
    allowed = c.allowed_ids()
    L = c.lists()
    R = c.runs()
    b0 = {}
    src = {"b0_val": 0, "b0_dev": 0}
    for lst in ("b0_dev", "b0_val"):                    # b0_val overwrites b0_dev when both exist
        for rid in L[lst]:
            r = R[rid]
            assert r["pool"] == "b0", (rid, r["pool"])
            b0[(r["climate_id"], r["building_id"])] = (rid, lst)
    groups = {}
    for rid in L["validation"]:
        r = R[rid]
        groups.setdefault((r["climate_id"], r["building_id"]), []).append(rid)
    tasks, nomatch = [], []
    for (cl, b), rids in groups.items():
        if (cl, b) not in b0:
            nomatch.append((cl, b))
            continue
        b0id, lst = b0[(cl, b)]
        src[lst] += len(rids)
        nds = {int(R[x]["n_dwellings"]) for x in rids + [b0id]}
        if len(nds) != 1:
            nomatch.append((cl, b, "dwelling counts differ"))
            continue
        tasks.append({"key": "%s|%s" % (cl, b), "climate": cl, "building": b, "b0": b0id, "runs": sorted(rids), "nd": nds.pop()})
    print("B0 groups: validation (climate,building) groups=%d with a b0 run=%d without=%d %s" % (len(groups), len(tasks), len(nomatch), nomatch[:3]), flush=True)
    print("B0 source list by validation runs: %s" % src, flush=True)
    if nomatch:
        print("CHECK b0_every_group_has_a_b0_run FAIL", nomatch[:5])
        sys.exit(3)
    print("CHECK b0_every_group_has_a_b0_run PASS groups=%d (b0_val runs used for %d validation runs, b0_dev fallback for %d)" % (len(tasks), src["b0_val"], src["b0_dev"]), flush=True)
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
    c.flush_log(nlog, "b0")
    out_ids = {x[1] for x in nlog}
    bad = sum(1 for x in nlog if x[1] not in allowed)
    print("B0 written: runs=%d groups=%d errors=%d %s" % (nrun, len(tasks), len(errs), errs[:3]), flush=True)
    print("CHECK b0_run_count_1980 %s written=%d expected=%d" % ("PASS" if nrun == len(L["validation"]) == 1980 else "FAIL", nrun, len(L["validation"])), flush=True)
    print("CHECK b0_total_elec_formula_vs_b0_own_total INFO max abs diff between equipment+(heating+cooling)/3.0 and the b0 run's own total_elec column = %.3e kWh (formula used)" % worst, flush=True)
    print("CHECK b0_openlog_outside_allowed_zero %s log_lines=%d distinct_b0_runs=%d outside=%d log=%s" % ("PASS" if bad == 0 else "FAIL", len(nlog), len(out_ids), bad, olp), flush=True)
    ok = (not errs) and nrun == 1980 and bad == 0
    print("B0_DONE", "OK" if ok else "FAILED", "seconds=%.0f" % (time.time() - t0), flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
