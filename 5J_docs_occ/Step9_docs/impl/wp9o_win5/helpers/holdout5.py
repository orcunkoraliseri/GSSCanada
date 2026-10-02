# 9o item 5: tiny-flat hold-out list on static_win5 (Madrid only; rule: building held out if ANY flat floor_area_m2 < 15).
# Run from Step9_docs/impl with py. Writes heldout_tinyflats_win5.csv (same columns as ..._win3.csv; the `split` column is the buildsplit_win5 split) and prints what moved vs win3.
import csv, collections, io
D = "ES-MAD-BERRUGUETE"
ch = dict(l.rstrip("\r\n").split("\t") for l in open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05/changed_stems.txt"))
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
    rows = build("static_win5", "buildsplit_win5", 15.0)
    with open("heldout_tinyflats_win5.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["district", "stem", "n_flats", "min_flat_m2", "mean_flat_m2", "split", "reason"]); w.writerows(rows)
    print("held out win5:", len(rows), "per split:", dict(collections.Counter(r[5] for r in rows)))
    old = {r["stem"]: r for r in csv.DictReader(open("heldout_tinyflats_win3.csv", encoding="utf-8")) if r["district"] == D}
    new = {r[1]: r for r in rows}
    print("win3 ES held out:", len(old))
    stay = sorted(set(old) & set(new)); out = sorted(set(old) - set(new)); inn = sorted(set(new) - set(old))
    print("stay", len(stay), "| left the list", len(out), "| entered the list", len(inn))
    flats3 = collections.defaultdict(list)
    for r in csv.DictReader(open("static_win3/flats_%s.csv" % D, encoding="utf-8")): flats3[r["stem"]].append(float(r["floor_area_m2"]))
    flats5 = collections.defaultdict(list)
    for r in csv.DictReader(open("static_win5/flats_%s.csv" % D, encoding="utf-8")): flats5[r["stem"]].append(float(r["floor_area_m2"]))
    def desc(s):
        a3, a5 = flats3.get(s), flats5.get(s)
        return "%s group=%s win3: flats %s min %s | win5: flats %s min %s" % (s, ch.get(s, "unchanged"),
            len(a3) if a3 else "-", ("%.2f" % min(a3)) if a3 else "-", len(a5) if a5 else "-", ("%.2f" % min(a5)) if a5 else "-")
    print("LEFT the list (win3 held out, not in win5):")
    for s in out: print("  ", desc(s))
    print("ENTERED the list:")
    for s in inn: print("  ", desc(s))
    print("STAY: by group", dict(collections.Counter(ch.get(s, "unchanged") for s in stay)), "; stay with changed min flat (win3 vs win5):", sum(1 for s in stay if abs(min(flats3[s]) - min(flats5[s])) > 1e-3))
    print("unchanged-group stems on the win3 list:", sum(1 for s in old if s not in ch), "still held out:", sum(1 for s in stay if s not in ch))
    # split of the stems: win3 split column vs win5 split column
    chg = [s for s in stay if old[s]["split"] != new[s][5]]
    print("stay with a different split column (win3 split list vs win5 re-derived split):", len(chg))
    print("PLANT threshold 1.0 holds out:", len(build("static_win5", "buildsplit_win5", 1.0)), "buildings; threshold 20 holds out:", len(build("static_win5", "buildsplit_win5", 20.0)), "(rule at 15 holds out", len(rows), ")")
