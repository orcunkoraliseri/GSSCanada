"""Step 9o item 6/7: new plan (win5) vs the live plan (copy read by scp, md5 f627f60d...). Row classes, rows to submit, resub manifest (smoke buildings first).
Usage: py cmp_plan5.py [<new plan>] ; writes resub_ES-MAD-BERRUGUETE_win5.csv, plan_compare_rows.csv"""
import csv, io, sys, collections, hashlib
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
W = IMP + "/wp9o_win5"
D = "ES-MAD-BERRUGUETE"
SMOKE = ["394922138a6b5928", "1271cddbf6bd1e8a"]
def rd(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))
KEYS = ["district", "stem", "building_split", "pool", "r", "mode", "n_flats", "seed", "src_idf_md5"]
def classify(old, new, deferred):
    """old, new: dict run_id -> row. Returns dict run_id -> class for every id in either."""
    cls = {}
    for rid in set(old) | set(new):
        o, n = old.get(rid), new.get(rid)
        if o is None: cls[rid] = "added"
        elif n is None: cls[rid] = "dropped"
        else:
            diff = [k for k in KEYS if o[k] != n[k]]
            if not diff: cls[rid] = "identical"
            elif "n_flats" in diff: cls[rid] = "changed_n_flats" + ("+md5" if "src_idf_md5" in diff else "")
            elif diff == ["src_idf_md5"]: cls[rid] = "changed_md5"
            else: cls[rid] = "changed_other:" + ",".join(diff)
    return cls
def summarize(old, new, deferred, label):
    cls = classify(old, new, deferred)
    c = collections.Counter(cls.values())
    print("[%s] live rows %d, new rows %d" % (label, len(old), len(new)))
    print("  rows new/added", c["added"], "| identical", c["identical"], "| changed md5 only", c["changed_md5"], "| changed n_flats (incl. md5)", sum(v for k, v in c.items() if k.startswith("changed_n_flats")), "| dropped", c["dropped"], "| other", {k: v for k, v in c.items() if k.startswith("changed_other")})
    # to submit = new rows that are not identical OR identical but in a deferred stem (never run by the live array)
    sub = [rid for rid in new if cls[rid] != "identical" or new[rid]["stem"] in deferred]
    ident_cov = [rid for rid in new if cls[rid] == "identical" and new[rid]["stem"] not in deferred]
    print("  to submit", len(sub), "| identical and covered by the live array (skip, R1 d)", len(ident_cov), "| identical but deferred (live array did not run them)", sum(1 for rid in new if cls[rid] == "identical" and new[rid]["stem"] in deferred))
    return cls, sub
if __name__ == "__main__":
    newp = sys.argv[1] if len(sys.argv) > 1 else W + "/plan_ES-MAD-BERRUGUETE_win5.csv"
    old = {r["run_id"]: r for r in rd(W + "/plan_live_copy.csv")}
    new_rows = rd(newp); new = {r["run_id"]: r for r in new_rows}
    assert len(new) == len(new_rows), "duplicate run_id in new plan"
    deg = [r for r in rd(IMP + "/wp9k/degenerate_win3.csv") if r["district"] == D]
    held3 = {r["stem"] for r in rd(IMP + "/heldout_tinyflats_win3.csv") if r["district"] == D}
    deferred = {r["stem"] for r in deg if r["stem"] not in held3}
    live_stems = {r["stem"] for r in old.values()}
    live_array = [rid for rid, r in old.items() if r["stem"] not in deferred]
    print("deferred degenerate stems (win3 list, ES, not held out):", len(deferred), "| all in live plan:", deferred <= live_stems, "| their runs", sum(1 for r in old.values() if r["stem"] in deferred), "| live array runs (plan minus deferred)", len(live_array), "(log: 8,616 + 585 = 9,201)")
    cls, sub = summarize(old, new, deferred, "win5 vs live")
    # breakdown of rows to submit
    by = collections.Counter()
    for rid in sub:
        s = new[rid]["stem"]
        by[("deferred" if s in deferred else "not deferred") + " / " + cls[rid]] += 1
    for k, v in sorted(by.items()): print("    ", k, v)
    # per-stem view
    st = collections.defaultdict(set)
    for rid, r in new.items(): st[r["stem"]].add(cls[rid])
    print("  stems: all rows identical", sum(1 for s, v in st.items() if v == {"identical"}), "| any row not identical", sum(1 for s, v in st.items() if v != {"identical"}), "| stems in live not in new:", len({r["stem"] for r in old.values()} - set(st)), "| stems in new not in live:", len(set(st) - {r["stem"] for r in old.values()}))
    gone = sorted({r["stem"] for r in old.values()} - set(st)); print("  stems that left the plan:", gone)
    addst = sorted(set(st) - live_stems); print("  stems new in the plan (joined from the 10-03 hold-out):", len(addst))
    # does anything differ besides src_idf path? all src_idf paths differ by the folder name only
    print("  src_idf path differs in", sum(1 for rid in new if rid in old and old[rid]["src_idf"] != new[rid]["src_idf"]), "rows (folder _win_2026-10-03 -> _win_2026-10-05, expected for all)")
    print("  seed equal in all shared rows:", all(old[r]["seed"] == new[r]["seed"] for r in new if r in old))
    # resub manifest: smoke buildings first, then the rest in plan order
    order = {rid: i for i, rid in enumerate(new)}
    sub_sorted = sorted(sub, key=lambda rid: (0 if new[rid]["stem"] in SMOKE else 1, SMOKE.index(new[rid]["stem"]) if new[rid]["stem"] in SMOKE else 0, order[rid]))
    cols = list(new_rows[0].keys())
    with io.open(W + "/resub_ES-MAD-BERRUGUETE_win5.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows([new[rid] for rid in sub_sorted])
    print("RESUB manifest rows", len(sub_sorted), "first 3:", sub_sorted[:3], "smoke rows first:", all(new[r]["stem"] in SMOKE for r in sub_sorted[:len([r for r in sub_sorted if new[r]["stem"] in SMOKE])]), "smoke rows", sum(1 for r in sub_sorted if new[r]["stem"] in SMOKE))
    print("RESUB md5", hashlib.md5(open(W + "/resub_ES-MAD-BERRUGUETE_win5.csv", "rb").read()).hexdigest())
    # equivalent index ranges on the full plan (1-based data row numbers)
    idx = sorted(order[rid] + 1 for rid in sub)
    rng = []; a = b = idx[0]
    for x in idx[1:]:
        if x == b + 1: b = x
        else: rng.append((a, b)); a = b = x
    rng.append((a, b))
    print("ranges on the FULL new plan (1-based):", len(rng), "ranges;", ",".join("%d-%d" % r if r[0] != r[1] else "%d" % r[0] for r in rng)[:400], "...")
    io.open(W + "/plan_compare_rows.csv", "w", encoding="utf-8", newline="").write("run_id,class,stem_deferred\n" + "".join("%s,%s,%d\n" % (rid, cls[rid], int(rid in new and new[rid]["stem"] in deferred or (rid in old and old[rid]["stem"] in deferred))) for rid in sorted(cls)))
    # smoke buildings
    for s in SMOKE:
        print("  smoke", s, "rows in new plan", sum(1 for r in new.values() if r["stem"] == s), "classes", dict(collections.Counter(cls[rid] for rid, r in new.items() if r["stem"] == s)), "in live plan", sum(1 for r in old.values() if r["stem"] == s))
    # ---- seen failing: planted changes on a copy of the new plan
    pl = {k: dict(v) for k, v in new.items()}
    unch = [rid for rid in new if cls[rid] == "identical" and new[rid]["stem"] not in deferred]
    v1 = unch[0]; pl[v1]["src_idf_md5"] = "0" * 32
    v2 = unch[40]; pl[v2]["n_flats"] = str(int(pl[v2]["n_flats"]) + 1)
    cls2, sub2 = summarize(old, pl, deferred, "PLANTED copy: md5 of %s zeroed, n_flats of %s +1" % (v1, v2))
    print("  PLANT result: planted md5 row in re-run set:", v1 in sub2, cls2[v1], "| planted n_flats row in re-run set:", v2 in sub2, cls2[v2], "| re-run set grew by", len(sub2) - len(sub))
