"""Step 9o item 4b: static tables `static_win5` vs `static_win3` (Madrid): md5 of each stem's rows; flat counts of the 113 old -> new."""
import csv, io, hashlib, collections
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
ch = dict(l.rstrip("\r\n").split("\t") for l in open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05/changed_stems.txt"))
def rows_by_stem(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        r = list(csv.reader(fh))
    d = collections.OrderedDict()
    for x in r[1:]:
        d.setdefault(x[1], []).append(x)
    return r[0], d
def h(rows): return hashlib.md5(("\n".join(",".join(r) for r in rows)).encode()).hexdigest()
for kind in ("flats", "buildings"):
    f = "%s_ES-MAD-BERRUGUETE.csv" % kind
    h3, a = rows_by_stem(IMP + "/static_win3/" + f); h5, b = rows_by_stem(IMP + "/static_win5/" + f)
    print("==", kind, "header equal", h3 == h5, "stems win3", len(a), "win5", len(b), "rows win3", sum(len(v) for v in a.values()), "win5", sum(len(v) for v in b.values()))
    unch = [s for s in b if s not in ch]
    print("  unchanged stems in win5 table", len(unch), "rows md5-equal to win3:", sum(1 for s in unch if s in a and h(a[s]) == h(b[s])), "; unchanged stems missing in win3:", [s for s in unch if s not in a])
    print("  win3 stems not in win5:", sorted(set(a) - set(b)), "; win5 not in win3:", sorted(set(b) - set(a)))
    for g in ("degenerate", "flat_count"):
        S = [s for s in b if ch.get(s) == g and s in a]
        print("  group", g, "stems in both", len(S), "rows equal", sum(1 for s in S if h(a[s]) == h(b[s])))
        if kind == "flats":
            cols = collections.Counter()
            for s in S:
                if len(a[s]) == len(b[s]):
                    for x, y in zip(a[s], b[s]):
                        for i, (u, v) in enumerate(zip(x, y)):
                            if u != v: cols[h3[i]] += 1
            print("    differing columns (cell count, same-row-count stems only):", dict(cols))
if True:
    h3, a = rows_by_stem(IMP + "/static_win3/flats_ES-MAD-BERRUGUETE.csv"); h5, b = rows_by_stem(IMP + "/static_win5/flats_ES-MAD-BERRUGUETE.csv")
    out = []
    for s in sorted(set(a) | set(b)):
        if ch.get(s) == "flat_count":
            out.append([s, len(a.get(s, [])), len(b.get(s, []))])
    print("113 group in the flats tables: stems present in win3/win5:", sum(1 for r in out if r[1]), sum(1 for r in out if r[2]), "flats old", sum(r[1] for r in out), "new", sum(r[2] for r in out))
    print("total flats win3", sum(len(v) for v in a.values()), "win5", sum(len(v) for v in b.values()))
    with io.open("../wp9o_win5/flatcounts_113_static_win3_to_win5.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["stem", "flats_win3", "flats_win5"]); w.writerows(out)
    print("flat count unchanged for", sum(1 for r in out if r[1] == r[2] and r[1] > 0), "of the 113 (should be 0)")
