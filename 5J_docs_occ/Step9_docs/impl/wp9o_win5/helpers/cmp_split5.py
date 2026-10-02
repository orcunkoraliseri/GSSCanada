"""Step 9o item 5: the six lists (Madrid: three) of buildsplit_win5 vs buildsplit_win3. Reports; decides nothing."""
import csv, io, collections, hashlib
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
D = "ES-MAD-BERRUGUETE"
ch = dict(l.rstrip("\r\n").split("\t") for l in open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05/changed_stems.txt"))
def load(folder):
    m = {}
    for sp in ("dev", "val", "test"):
        for r in csv.DictReader(io.open("%s/%s/%s_%s.csv" % (IMP, folder, D, sp), encoding="utf-8", newline="")):
            m[r["stem"]] = dict(r, split=sp)
    return m
a, b = load("buildsplit_win3"), load("buildsplit_win5")
print("win3", len(a), "win5", len(b))
for sp in ("dev", "val", "test"):
    print(" ", sp, "win3", sum(1 for r in a.values() if r["split"] == sp), "win5", sum(1 for r in b.values() if r["split"] == sp))
out3 = sorted(set(a) - set(b)); in5 = sorted(set(b) - set(a))
print("in win3 lists, not in win5:", [(s, a[s]["split"], a[s]["class"], a[s]["band"], a[s]["n_flats"]) for s in out3])
print("in win5 lists, not in win3:", [(s, b[s]["split"], b[s]["class"], b[s]["band"], b[s]["n_flats"]) for s in in5])
both = sorted(set(a) & set(b))
moved = [s for s in both if a[s]["split"] != b[s]["split"]]
bandchg = [s for s in both if a[s]["band"] != b[s]["band"]]
classchg = [s for s in both if a[s]["class"] != b[s]["class"]]
nchg = [s for s in both if a[s]["n_flats"] != b[s]["n_flats"]]
print("in both:", len(both), "| split differs:", len(moved), "| flat band differs:", len(bandchg), "| class differs:", len(classchg), "| flat count differs:", len(nchg))
# strata membership
def strata(m):
    d = collections.defaultdict(set)
    for s, r in m.items(): d[(r["class"], r["band"])].add(s)
    return d
sa, sb = strata(a), strata(b)
changed_strata = {k for k in set(sa) | set(sb) if sa.get(k, set()) != sb.get(k, set())}
print("strata total", len(set(sa) | set(sb)), "with changed membership", len(changed_strata))
inch = [s for s in both if (b[s]["class"], b[s]["band"]) in changed_strata]
print("stems in both whose win5 stratum has changed membership:", len(inch), "; of them moved split:", sum(1 for s in inch if a[s]["split"] != b[s]["split"]))
print("stems in both in strata with UNCHANGED membership:", len(both) - len(inch), "; of them moved split:", sum(1 for s in both if s not in inch and a[s]["split"] != b[s]["split"]))
print("moved stems by their OpenUBEM group:", collections.Counter(ch.get(s, "unchanged") for s in moved))
print("unchanged-group stems that moved split:", sum(1 for s in moved if ch.get(s) is None), "of", sum(1 for s in both if ch.get(s) is None))
mv = collections.Counter((a[s]["split"], b[s]["split"]) for s in moved)
print("moves (from win3 -> win5):", dict(mv))
print("strata with changed membership:")
for k in sorted(changed_strata):
    print("  ", k, "win3", len(sa.get(k, ())), "win5", len(sb.get(k, ())), "added", len(sb.get(k, set()) - sa.get(k, set())), "removed", len(sa.get(k, set()) - sb.get(k, set())))
# per stem csv
with io.open("split_win3_vs_win5.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["stem", "group", "split_win3", "split_win5", "class_win3", "class_win5", "band_win3", "band_win5", "n_flats_win3", "n_flats_win5", "in_win3", "in_win5"])
    for s in sorted(set(a) | set(b)):
        x, y = a.get(s), b.get(s)
        w.writerow([s, ch.get(s, "unchanged"), x["split"] if x else "", y["split"] if y else "", x["class"] if x else "", y["class"] if y else "", x["band"] if x else "", y["band"] if y else "", x["n_flats"] if x else "", y["n_flats"] if y else "", int(bool(x)), int(bool(y))])
# a numeric check that the flat-count changers (113) are exactly the stems with changed n_flats
print("flat-count changers in lists:", len(nchg), "all in flat_count group:", all(ch.get(s) == "flat_count" for s in nchg))
print("band changers by direction:", collections.Counter((a[s]["band"], b[s]["band"]) for s in bandchg))
# strata.csv comparison for Madrid rows
def sc(folder):
    return [r for r in csv.reader(io.open("%s/%s/strata.csv" % (IMP, folder), encoding="utf-8", newline="")) if r and (r[0] == D or r[0] == "district")]
s3, s5 = sc("buildsplit_win3"), sc("buildsplit_win5")
print("strata.csv Madrid rows: win3", len(s3), "win5", len(s5), "equal", s3 == s5)
