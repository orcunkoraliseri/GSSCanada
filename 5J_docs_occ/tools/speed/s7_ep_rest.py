# -*- coding: utf-8 -*-
"""5J Step 7 part C prep (Speed CPU job): the 1,900 EnergyPlus runs of the other 19 check draws.
district_runs_es.csv (sealed, 2,000 runs) minus district_runs_es_pilot.csv (sealed, 100 runs, run by job 1405248) = district_runs_es_rest.csv (1,900).
Plan: NB blocks balanced by estimated seconds (greedy, longest first; same code as s7_ep_table.py), campaign plan layout under ep/plan_rest/.
Also ep/all_ids.txt = the 2,000 run ids in table order (for the integrity check of all 2,000)."""
import csv, io, os, sys
import s7_common as s7

NB = 15
FAILS = []


def gate(name, ok, text=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def main():
    s7.stamp("s7_ep_rest start")
    seals = {l.split()[1]: l.split()[0] for l in io.open(s7.IN + "SEALS.md5", encoding="utf-8") if len(l.split()) == 2}
    gate("full_table_and_pilot_table_sealed_and_unchanged", all(seals.get(n) == s7.md5(s7.IN + n) for n in ("district_runs_es.csv", "district_runs_es_pilot.csv")))
    allr = s7.read_csv(s7.IN + "district_runs_es.csv")
    pil = s7.read_csv(s7.IN + "district_runs_es_pilot.csv")
    pid = {r["run_id"] for r in pil}
    rest = [r for r in allr if r["run_id"] not in pid]
    gate("2000_all_100_pilot_1900_rest", len(allr) == 2000 and len(pil) == 100 and len(rest) == 1900 and pid <= {r["run_id"] for r in allr}, "all=%d pilot=%d rest=%d" % (len(allr), len(pil), len(rest)))
    gate("rest_rows_identical_to_sealed_table_rows", all(r in allr for r in rest[:50]) and len({r["run_id"] for r in rest}) == 1900)
    cols = list(allr[0].keys())
    p = s7.IN + "district_runs_es_rest.csv"
    s7.write_csv(p, cols, [[r[c_] for c_ in cols] for r in rest])
    print("REST_TABLE md5 %s rows %d (derived from the sealed table, not sealed itself)" % (s7.md5(p), len(rest)))
    io.open(s7.D + "ep/all_ids.txt", "w").write("\n".join(r["run_id"] for r in allr) + "\n")
    cc = s7.install_twins()
    est = {r["run_id"]: cc.est_seconds(r) for r in rest}
    order = sorted(rest, key=lambda r: -est[r["run_id"]])
    blocks = [[] for _ in range(NB)]
    load = [0.0] * NB
    for r in order:
        i = load.index(min(load))
        blocks[i].append(r)
        load[i] += est[r["run_id"]]
    plan = s7.D + "ep/plan_rest/"
    adir = plan + s7.CLIMATE + "/"
    os.makedirs(adir, exist_ok=True)
    prows = []
    pos = 0
    for bi, blk in enumerate(blocks, 1):
        blk.sort(key=lambda r: r["run_id"])
        with io.open(adir + "block_%d.csv" % bi, "w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\n")
            wr.writerow(cols + ["pos", "est_s"])
            for r in blk:
                pos += 1
                wr.writerow([r[c_] for c_ in cols] + [pos, "%.1f" % est[r["run_id"]]])
                prows.append([r["run_id"], s7.CLIMATE, bi, pos, "%.1f" % est[r["run_id"]], cc.cache_key(r), 0])
    with io.open(plan + "plan.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["run_id", "array", "block", "pos", "est_s", "cache_key", "done"])
        wr.writerows(prows)
    io.open(plan + "nblocks.txt", "w").write("%s %d\n" % (s7.CLIMATE, NB))
    io.open(plan + "todo_ids.txt", "w").write("\n".join(p_[0] for p_ in prows) + "\n")
    print("PLAN_REST blocks=%d runs=%d est_seconds per block %s total %.0f" % (NB, len(prows), [round(x) for x in load], sum(load)))
    gate("plan_holds_every_rest_run_once", len(prows) == 1900 and len({p_[0] for p_ in prows}) == 1900)
    # no rest run has a done file yet (the pilot's 100 are the only ones)
    gate("no_done_file_for_a_rest_run_yet", not any(os.path.exists(cc.done_json(r["run_id"])) for r in rest[:200]), "first 200 rest runs checked")
    gate("pilot_runs_all_have_done_json", all(os.path.exists(cc.done_json(i)) for i in pid))
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
