"""Step 9p item 5: the three Bologna lists of buildsplit_bol5 vs buildsplit_win3 (IT lists). Reports; decides nothing."""
import csv, io, collections, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
D = "IT-BOL-GALVANI2"
ch = dict(l.rstrip("\r\n").split("\t") for l in io.open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05/changed_stems.txt", encoding="utf-8") if l.strip())
def load(folder):
    m = {}
    for sp in ("dev", "val", "test"):
        for r in csv.DictReader(io.open("%s/%s/%s_%s.csv" % (IMP, folder, D, sp), encoding="utf-8", newline="")):
            assert r["stem"] not in m, ("stem in two lists", folder, r["stem"])
            m[r["stem"]] = dict(r, split=sp)
    return m
a, b = load("buildsplit_win3"), load("buildsplit_bol5")
print("win3", len(a), "bol5", len(b))
for sp in ("dev", "val", "test"):
    print(" ", sp, "win3", sum(1 for r in a.values() if r["split"] == sp), "bol5", sum(1 for r in b.values() if r["split"] == sp))
out3 = sorted(set(a) - set(b)); in5 = sorted(set(b) - set(a))
print("in win3 lists, not in bol5:", [(s, a[s]["split"], a[s]["class"], a[s]["band"], a[s]["n_flats"]) for s in out3])
print("in bol5 lists, not in win3:", [(s, b[s]["split"], b[s]["class"], b[s]["band"], b[s]["n_flats"]) for s in in5])
both = sorted(set(a) & set(b))
moved = [s for s in both if a[s]["split"] != b[s]["split"]]
bandchg = [s for s in both if a[s]["band"] != b[s]["band"]]
classchg = [s for s in both if a[s]["class"] != b[s]["class"]]
nchg = [s for s in both if a[s]["n_flats"] != b[s]["n_flats"]]
print("in both:", len(both), "| split differs:", len(moved), "| flat band differs:", len(bandchg), "| class differs:", len(classchg), "| flat count differs:", len(nchg))
def strata(m):
    d = collections.defaultdict(set)
    for s, r in m.items(): d[(r["class"], r["band"])].add(s)
    return d
sa, sb = strata(a), strata(b)
changed_strata = {k for k in set(sa) | set(sb) if sa.get(k, set()) != sb.get(k, set())}
print("strata total", len(set(sa) | set(sb)), "with changed membership", len(changed_strata))
inch = [s for s in both if (b[s]["class"], b[s]["band"]) in changed_strata]
print("stems in both whose bol5 stratum has changed membership:", len(inch), "; of them moved split:", sum(1 for s in inch if a[s]["split"] != b[s]["split"]))
print("stems in both in strata with UNCHANGED membership:", len(both) - len(inch), "; of them moved split:", sum(1 for s in both if s not in inch and a[s]["split"] != b[s]["split"]))
print("moved stems by OpenUBEM group:", collections.Counter(ch[s] for s in moved), "| origin-only stems that moved:", sum(1 for s in moved if ch[s] == "origin_shift"), "of", sum(1 for s in both if ch[s] == "origin_shift"))
print("moves (win3 -> bol5):", dict(collections.Counter((a[s]["split"], b[s]["split"]) for s in moved)))
print("flat band changes:", dict(collections.Counter((a[s]["band"], b[s]["band"]) for s in bandchg)))
print("strata with changed membership:")
for k in sorted(changed_strata):
    print("  ", k, "win3", len(sa.get(k, ())), "bol5", len(sb.get(k, ())), "added", len(sb.get(k, set()) - sa.get(k, set())), "removed", len(sa.get(k, set()) - sb.get(k, set())))
with io.open(os.path.join(OUTD, "split_win3_vs_bol5.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["stem", "group", "split_win3", "split_bol5", "class_win3", "class_bol5", "band_win3", "band_bol5", "n_flats_win3", "n_flats_bol5", "in_win3", "in_bol5"])
    for s in sorted(set(a) | set(b)):
        x, y = a.get(s), b.get(s)
        w.writerow([s, ch[s], x["split"] if x else "", y["split"] if y else "", x["class"] if x else "", y["class"] if y else "", x["band"] if x else "", y["band"] if y else "", x["n_flats"] if x else "", y["n_flats"] if y else "", int(bool(x)), int(bool(y))])
print("flat-count changers in lists:", len(nchg), "| all in the 1,070 rebuilt group:", all(ch[s] != "origin_shift" for s in nchg))
# independent check on the written bol5 files: no stem in two lists, plus a planted copy
def cnt(m): return sum(1 for _ in m)
b_by = collections.Counter()
for sp in ("dev", "val", "test"):
    for r in csv.DictReader(io.open("%s/buildsplit_bol5/%s_%s.csv" % (IMP, D, sp), encoding="utf-8", newline="")):
        b_by[r["stem"]] += 1
print("INDEPENDENT overlap check on the written bol5 files: stems in more than one list:", sum(1 for v in b_by.values() if v > 1), "| stems", len(b_by))
planted = collections.Counter(b_by); planted[sorted(b_by)[0]] += 1
print("PLANTED (one stem counted in a second list): stems in more than one list:", sum(1 for v in planted.values() if v > 1), "named", [k for k, v in planted.items() if v > 1])
# md5 of each bol5 file
for sp in ("dev", "val", "test"):
    p = "%s/buildsplit_bol5/%s_%s.csv" % (IMP, D, sp)
    print("MD5", os.path.basename(p), hashlib.md5(io.open(p, "rb").read()).hexdigest())
p = "%s/buildsplit_bol5/strata.csv" % IMP
print("MD5 strata.csv", hashlib.md5(io.open(p, "rb").read()).hexdigest())
# win3 sealed md5 for reference
for sp in ("dev", "val", "test"):
    p = "%s/buildsplit_win3/%s_%s.csv" % (IMP, D, sp)
    print("MD5 win3", os.path.basename(p), hashlib.md5(io.open(p, "rb").read()).hexdigest())
