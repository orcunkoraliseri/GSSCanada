# -*- coding: utf-8 -*-
"""5J Step 7 part F (Speed CPU job): the EnergyPlus-check run table and the 1-draw pilot plan.
district_runs_es.csv = the 20 check draws (draws.json check_indices) x the 100 twins = 2,000 runs, campaign layout
(run_id,country,climate_id,building_id,class,k,n_floors,n_dwellings,pool,building_split,replicate,seed,placement); placement = the draw's
households by the rule in s7_draws.py; pool = building_split = district; replicate 0; seed = the draw's seed.
district_runs_es_pilot.csv = the 100 runs of the FIRST check draw. Both are sealed. Then the pilot plan: 4 blocks balanced by estimated
seconds (greedy, longest first) under ep/plan_pilot/ in the campaign plan layout (block_<n>.csv, plan.csv, nblocks.txt, todo_ids.txt)."""
import csv, io, json, os, sys
import s7_common as s7
import s7_draws as dr

FAILS = []
NB = 4


def gate(name, ok, text=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def main():
    s7.stamp("s7_ep_table start")
    seals = {l.split()[1]: l.split()[0] for l in io.open(s7.IN + "SEALS.md5", encoding="utf-8") if len(l.split()) == 2}
    gate("draws_json_sealed_and_unchanged", seals.get("draws.json") == s7.md5(s7.IN + "draws.json"))
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    seeds, chk = dj["seeds"], dj["check_indices"]
    hids, w, prow = dr.load_pool()
    twins = dr.load_twins()
    hdr = ["run_id", "country", "climate_id", "building_id", "class", "k", "n_floors", "n_dwellings", "pool", "building_split", "replicate", "seed", "placement"]
    rows = []
    for d in chk:
        a = dr.assign(seeds[d], twins, hids, w)
        for tid, cls, nd, r in twins:
            rows.append(["es_madrid_%s_d%03d" % (tid, d), "es", s7.CLIMATE, tid, cls, r["twin_k"], r["twin_floors"], nd, "district", "district", 0, seeds[d], dr.placement(a[tid])])
    gate("2000_runs_unique_ids", len(rows) == 2000 and len({r[0] for r in rows}) == 2000, "rows=%d" % len(rows))
    toks = set()
    for r in rows:
        for x in r[12].split(";"):
            toks.add(x.split(":")[1])
    gate("n_dwellings_equals_placement_items", all(len(r[12].split(";")) == r[7] for r in rows))
    gate("every_placed_household_has_a_folder_with_household_json", all(os.path.exists(s7.POOL + "es_%s/household.json" % t) for t in toks), "distinct households used %d" % len(toks))
    chk0 = chk[0]
    a0 = dr.assign(seeds[chk0], twins, hids, w)
    rule = {tid: dr.placement(a0[tid]) for tid, _c, _n, _r in twins}
    got = {r[3]: r[12] for r in rows if r[0].endswith("_d%03d" % chk0)}
    gate("table_placement_equals_the_assignment_rule_for_the_first_check_draw", got == rule, "twins=%d" % len(got))
    bad = dict(got)
    t0 = sorted(bad)[0]
    first = bad[t0].split(";")[0].split(":")[1]
    bad[t0] = bad[t0].replace(":" + first, ":99999", 1)
    gate("planted_changed_household_CAUGHT (seen failing)", bad != rule)
    p = s7.IN + "district_runs_es.csv"
    p1 = s7.IN + "district_runs_es_pilot.csv"
    s7.write_csv(p, hdr, rows)
    pil = [r for r in rows if r[0].endswith("_d%03d" % chk0)]
    gate("pilot_is_100_runs_of_check_draw_%d" % chk0, len(pil) == 100)
    s7.write_csv(p1, hdr, pil)
    s7.seal(p)
    s7.seal(p1)
    print("EP_TABLE check draws %s ; pilot draw %d ; dwellings per draw %d" % (chk, chk0, sum(r[7] for r in pil)))
    # ---- pilot plan (camp_plan layout), balanced into NB blocks
    cc = s7.install_twins()
    runs = s7.read_csv(p1)
    est = {r["run_id"]: cc.est_seconds(r) for r in runs}
    order = sorted(runs, key=lambda r: -est[r["run_id"]])
    blocks = [[] for _ in range(NB)]
    load = [0.0] * NB
    for r in order:
        i = load.index(min(load))
        blocks[i].append(r)
        load[i] += est[r["run_id"]]
    plan = s7.D + "ep/plan_pilot/"
    adir = plan + s7.CLIMATE + "/"
    os.makedirs(adir, exist_ok=True)
    cols = list(runs[0].keys())
    prows = []
    pos = 0
    for bi, blk in enumerate(blocks, 1):
        blk.sort(key=lambda r: r["run_id"])
        with io.open(adir + "block_%d.csv" % bi, "w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\n")
            wr.writerow(cols + ["pos", "est_s"])
            for r in blk:
                pos += 1
                wr.writerow([r[c] for c in cols] + [pos, "%.1f" % est[r["run_id"]]])
                prows.append([r["run_id"], s7.CLIMATE, bi, pos, "%.1f" % est[r["run_id"]], cc.cache_key(r), 0])
    with io.open(plan + "plan.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["run_id", "array", "block", "pos", "est_s", "cache_key", "done"])
        wr.writerows(prows)
    io.open(plan + "nblocks.txt", "w").write("%s %d\n" % (s7.CLIMATE, NB))
    io.open(plan + "todo_ids.txt", "w").write("\n".join(p_[0] for p_ in prows) + "\n")
    io.open(s7.D + "ep/pilot_ids.txt", "w").write("\n".join(p_[0] for p_ in prows) + "\n")
    print("PLAN_PILOT blocks=%d runs=%d est_seconds per block %s total %.0f" % (NB, len(prows), [round(x) for x in load], sum(load)))
    gate("plan_holds_every_pilot_run_once", len(prows) == 100 and len({p_[0] for p_ in prows}) == 100)
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
