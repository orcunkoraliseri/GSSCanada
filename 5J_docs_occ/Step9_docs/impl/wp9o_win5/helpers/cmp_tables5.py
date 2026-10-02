"""Step 9o item 4a: wall table + zone map `_win5` vs `_win3`, Madrid rows only, per stem (md5 of the stem's rows)."""
import csv, io, hashlib, collections, sys
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
NEWD = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05"
D = "ES-MAD-BERRUGUETE"
ch = dict(l.rstrip("\r\n").split("\t") for l in open(NEWD + "/changed_stems.txt"))
def rd(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))
def h(rows): return hashlib.md5(("\n".join(",".join(r) for r in rows)).encode()).hexdigest()
w3, w5 = rd(IMP + "/2026-10-01_wp9c_wall_table_win3.csv"), rd(IMP + "/2026-10-01_wp9c_wall_table_win5.csv")
z3, z5 = rd(IMP + "/2026-10-01_wp9c_zone_map_win3.csv"), rd(IMP + "/2026-10-01_wp9c_zone_map_win5.csv")
print("headers equal: wall", w3[0] == w5[0], "zone", z3[0] == z5[0])
hw = w3[0]; si = hw.index("stem"); di = hw.index("district"); ni = hw.index("n_flats"); ri = hw.index("zone_map_reason")
W3 = {r[si]: r for r in w3[1:] if r[di] == D}; W5 = {r[si]: r for r in w5[1:] if r[di] == D}
print("wall table rows (Madrid): win3", len(W3), "win5", len(W5), "other districts in win5:", sum(1 for r in w5[1:] if r[di] != D))
Z3 = collections.defaultdict(list); Z5 = collections.defaultdict(list)
for r in z3[1:]:
    if r[0] == D: Z3[r[1]].append(r)
for r in z5[1:]:
    if r[0] == D: Z5[r[1]].append(r)
unch = [s for s in W5 if s not in ch]
eq_w = sum(1 for s in unch if W3[s] == W5[s]); eq_z = sum(1 for s in unch if h(Z3[s]) == h(Z5[s]))
print("UNCHANGED stems", len(unch), "wall-table row byte-equal", eq_w, "zone-map rows equal", eq_z)
# which column differs on unchanged stems with unequal wall rows
dc = collections.Counter()
for s in unch:
    if W3[s] != W5[s]:
        for i, (a, b) in enumerate(zip(W3[s], W5[s])):
            if a != b: dc[hw[i]] += 1
print("  columns that differ on unchanged stems:", dict(dc))
for g in ("degenerate", "flat_count"):
    S = [s for s in W5 if ch.get(s) == g]
    eqw = sum(1 for s in S if W3[s] == W5[s]); eqz = sum(1 for s in S if h(Z3[s]) == h(Z5[s]))
    dcols = collections.Counter()
    for s in S:
        for i, (a, b) in enumerate(zip(W3[s], W5[s])):
            if a != b: dcols[hw[i]] += 1
    print("GROUP", g, len(S), "wall rows equal", eqw, "zone-map rows equal", eqz, "columns differing (stems):", dict(dcols))
# usable
u3 = sum(1 for r in W3.values() if not r[ri]); u5 = sum(1 for r in W5.values() if not r[ri])
print("usable (empty zone_map_reason) win3", u3, "win5", u5, "total flats win3", sum(int(r[ni]) for r in W3.values() if not r[ri]), "win5", sum(int(r[ni]) for r in W5.values() if not r[ri]))
bad3 = {s for s, r in W3.items() if r[ri]}; bad5 = {s for s, r in W5.items() if r[ri]}
print("left out win3", len(bad3), "win5", len(bad5), "; left out in win5 not in win3:", sorted(bad5 - bad3), "; back in:", sorted(bad3 - bad5))
for s in sorted(bad5): print("  left out win5:", s, ch.get(s, "unchanged"), W5[s][ri], "n_flats(rows)", W5[s][ni], "| win3:", W3[s][ri] or "usable", W3[s][ni])
print("zone-map total rows win3", sum(len(v) for v in Z3.values()), "win5", sum(len(v) for v in Z5.values()))
# flat counts of the 113, old -> new (usable only), per stem csv
rows = []
for s in sorted(S for S in W5 if ch.get(S) == "flat_count"):
    rows.append([s, W3[s][ni], W5[s][ni], W3[s][ri], W5[s][ri], sum(1 for r in Z3[s]), sum(1 for r in Z5[s])])
with io.open("flatcounts_113_win3_to_win5.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["stem", "n_flats_win3", "n_flats_win5", "reason_win3", "reason_win5", "zone_rows_win3", "zone_rows_win5"]); w.writerows(rows)
print("113 group: sum n_flats (wall table) old", sum(int(r[1]) for r in rows), "new", sum(int(r[2]) for r in rows), "; zone-map rows old", sum(r[5] for r in rows), "new", sum(r[6] for r in rows))
print("total flats (zone map rows) all stems: old", sum(len(v) for v in Z3.values()), "new", sum(len(v) for v in Z5.values()), "| per-stem rows check: n_flats == zone rows for every stem:", all(int(W5[s][ni]) == len(Z5[s]) for s in W5))
