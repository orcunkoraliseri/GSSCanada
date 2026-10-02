# 9p item 5: tiny-flat hold-out list on static_bol5 (Bologna; rule: building held out if ANY flat floor_area_m2 < 15).
# Run from Step9_docs/impl with py. Writes heldout_tinyflats_bol5.csv (same columns as ..._win3.csv; `split` = buildsplit_bol5 split) and prints what moved vs win3.
import csv, collections, io, hashlib
D = "IT-BOL-GALVANI2"
ch = dict(l.rstrip("\r\n").split("\t") for l in open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05/changed_stems.txt"))
def build(flats_dir, split_dir, thr):
    rows = []
    sp = {}
    for s in ("dev", "val", "test"):
        for r in csv.DictReader(open("%s/%s_%s.csv" % (split_dir, D, s), encoding="utf-8")):
            assert r["stem"] not in sp
            sp[r["stem"]] = s
    by = collections.defaultdict(list)
    for r in csv.DictReader(open("%s/flats_%s.csv" % (flats_dir, D), encoding="utf-8")):
        by[r["stem"]].append(float(r["floor_area_m2"]))
    for stem in sorted(by):
        a = by[stem]
        if min(a) < thr:
            assert stem in sp, stem
            rows.append([D, stem, len(a), "%.4f" % min(a), "%.4f" % (sum(a) / len(a)), sp[stem], "flat_under_15m2"])
    return rows
if __name__ == "__main__":
    rows = build("static_bol5", "buildsplit_bol5", 15.0)
    with open("heldout_tinyflats_bol5.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["district", "stem", "n_flats", "min_flat_m2", "mean_flat_m2", "split", "reason"]); w.writerows(rows)
    print("held out bol5:", len(rows), "per split:", dict(collections.Counter(r[5] for r in rows)))
    for r in rows: print("  ", r, "group", ch[r[1]])
    print("md5 heldout_tinyflats_bol5.csv", hashlib.md5(open("heldout_tinyflats_bol5.csv", "rb").read()).hexdigest())
    old = {r["stem"]: r for r in csv.DictReader(open("heldout_tinyflats_win3.csv", encoding="utf-8")) if r["district"] == D}
    new = {r[1]: r for r in rows}
    print("win3 IT held out:", len(old), "per split", dict(collections.Counter(r["split"] for r in old.values())))
    stay = sorted(set(old) & set(new)); out = sorted(set(old) - set(new)); inn = sorted(set(new) - set(old))
    print("stay", len(stay), "| left the list", len(out), "| entered the list", len(inn))
    flats3 = collections.defaultdict(list)
    for r in csv.DictReader(open("static_win3/flats_%s.csv" % D, encoding="utf-8")): flats3[r["stem"]].append(float(r["floor_area_m2"]))
    flats5 = collections.defaultdict(list)
    for r in csv.DictReader(open("static_bol5/flats_%s.csv" % D, encoding="utf-8")): flats5[r["stem"]].append(float(r["floor_area_m2"]))
    def desc(s):
        a3, a5 = flats3.get(s), flats5.get(s)
        return "%s group=%s win3: flats %s min %s | bol5: flats %s min %s" % (s, ch[s], len(a3) if a3 else "-", ("%.2f" % min(a3)) if a3 else "-", len(a5) if a5 else "-", ("%.2f" % min(a5)) if a5 else "-")
    print("ENTERED the list (held out now, not on win3):")
    for s in inn: print("  ", desc(s))
    print("STAY:")
    for s in stay: print("  ", desc(s))
    print("LEFT the list: by group", dict(collections.Counter(ch[s] for s in out)), "| left because the building is no longer usable (not in static_bol5):", sum(1 for s in out if s not in flats5), "| left because its smallest flat is now >= 15 m2:", sum(1 for s in out if s in flats5))
    mins = sorted(min(flats5[s]) for s in out if s in flats5)
    print("  smallest flat of the left-the-list buildings on bol5: min %.2f median %.2f" % (mins[0], mins[len(mins)//2]), "| old minimum flats of these on win3: median %.2f" % sorted(min(flats3[s]) for s in out)[len(out)//2])
    ex = sorted(out, key=lambda s: min(flats3[s]))[:3]
    for s in ex: print("   example:", desc(s))
    print("origin-only stems on the win3 list:", sum(1 for s in old if ch[s] == "origin_shift"), "still held out:", sum(1 for s in stay if ch[s] == "origin_shift"))
    print("PLANT threshold 1.0 holds out:", len(build("static_bol5", "buildsplit_bol5", 1.0)), "buildings; threshold 20 holds out:", len(build("static_bol5", "buildsplit_bol5", 20.0)), "; threshold 100 holds out:", len(build("static_bol5", "buildsplit_bol5", 100.0)), "(rule at 15 holds out", len(rows), ")")
