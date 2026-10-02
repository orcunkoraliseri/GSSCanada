# 9j item 4: tiny-flat hold-out list on static_win3 (rule: building held out if ANY flat floor_area_m2 < 15). Run from Step9_docs/impl with py.
import csv, collections
D = ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2")
def build(flats_dir, split_dir, thr):
    rows = []
    for d in D:
        sp = {}
        for s in ("dev", "val", "test"):
            for r in csv.DictReader(open("%s/%s_%s.csv" % (split_dir, d, s), encoding="utf-8")):
                assert r["stem"] not in sp
                sp[r["stem"]] = s
        by = collections.defaultdict(list)
        for r in csv.DictReader(open("%s/flats_%s.csv" % (flats_dir, d), encoding="utf-8")):
            by[r["stem"]].append(float(r["floor_area_m2"]))
        nf = 0
        for stem in sorted(by):
            a = by[stem]
            if min(a) < thr:
                assert stem in sp, stem
                rows.append([d, stem, len(a), "%.4f" % min(a), "%.4f" % (sum(a) / len(a)), sp[stem], "flat_under_15m2"])
    return rows
rows = build("static_win3", "buildsplit_win3", 15.0)
with open("heldout_tinyflats_win3.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["district", "stem", "n_flats", "min_flat_m2", "mean_flat_m2", "split", "reason"]); w.writerows(rows)
c = collections.Counter(r[0] for r in rows)
print("held out:", dict(c), "per split:", dict(collections.Counter((r[0], r[5]) for r in rows)))
print("old file byte-equal:", open("heldout_tinyflats_win2.csv", "rb").read() == open("heldout_tinyflats_win3.csv", "rb").read())
# seen failing: wrong threshold must change the list
print("PLANT threshold 1.0 holds out:", len(build("static_win3", "buildsplit_win3", 1.0)), "buildings (rule at 15 holds out", len(rows), ")")
print("PLANT threshold 20 holds out:", len(build("static_win3", "buildsplit_win3", 20.0)), "buildings")
