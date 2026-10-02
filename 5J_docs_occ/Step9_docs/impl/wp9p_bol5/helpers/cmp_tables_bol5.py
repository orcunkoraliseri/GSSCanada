# -*- coding: utf-8 -*-
"""Step 9p item 4: wall table + zone map + static tables `_bol5` / `static_bol5` vs `_win3` / `static_win3`, Bologna rows only, per stem (md5 of the stem's rows).
Origin-only stems (109): rows equal? if not, how large is the largest numeric difference (UTM-size rounding in the 10-03 numbers)?
Rebuilt stems (1,070): flat counts old -> new per stem into ../flatcounts_1070_win3_to_bol5.csv."""
import csv, io, hashlib, collections, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
NEWD = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
D = "IT-BOL-GALVANI2"
ch = dict(l.rstrip("\r\n").split("\t") for l in io.open(NEWD + "/changed_stems.txt", encoding="utf-8") if l.strip())


def rd(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def h(rows):
    return hashlib.md5(("\n".join(",".join(r) for r in rows)).encode()).hexdigest()


def num(x):
    try:
        return float(x)
    except Exception:
        return None


def maxdiff(ra, rb):
    """largest abs numeric difference over the cells of two row lists (same length) and the columns that differ"""
    m, cols = 0.0, collections.Counter()
    return m, cols


w3, w5 = rd(IMP + "/2026-10-01_wp9c_wall_table_win3.csv"), rd(IMP + "/2026-10-01_wp9c_wall_table_bol5.csv")
z3, z5 = rd(IMP + "/2026-10-01_wp9c_zone_map_win3.csv"), rd(IMP + "/2026-10-01_wp9c_zone_map_bol5.csv")
print("headers equal: wall", w3[0] == w5[0], "zone", z3[0] == z5[0])
hw = w3[0]; si = hw.index("stem"); di = hw.index("district"); ni = hw.index("n_flats"); ri = hw.index("zone_map_reason")
W3 = {r[si]: r for r in w3[1:] if r[di] == D}; W5 = {r[si]: r for r in w5[1:] if r[di] == D}
print("wall table rows (Bologna): win3", len(W3), "bol5", len(W5), "other districts in bol5:", sum(1 for r in w5[1:] if r[di] != D), "| same stem set:", set(W3) == set(W5))
Z3 = collections.defaultdict(list); Z5 = collections.defaultdict(list)
for r in z3[1:]:
    if r[0] == D: Z3[r[1]].append(r)
for r in z5[1:]:
    if r[0] == D: Z5[r[1]].append(r)
unch = [s for s in W5 if ch[s] == "origin_shift"]
eq_w = [s for s in unch if W3[s] == W5[s]]
eq_z = [s for s in unch if h(Z3[s]) == h(Z5[s])]
print("ORIGIN-ONLY stems", len(unch), "| wall-table row byte-equal", len(eq_w), "| zone-map rows (zone names and floor areas) equal", len(eq_z))
dc, mx = collections.Counter(), collections.defaultdict(float)
for s in unch:
    if W3[s] != W5[s]:
        for i, (a, b) in enumerate(zip(W3[s], W5[s])):
            if a != b:
                dc[hw[i]] += 1
                na, nb = num(a), num(b)
                if na is not None and nb is not None:
                    mx[hw[i]] = max(mx[hw[i]], abs(na - nb))
print("  wall-table columns that differ on origin-only stems (stems):", dict(dc), "| largest abs difference per column:", {k: round(v, 5) for k, v in mx.items()})
dz = 0.0; nz = 0
for s in unch:
    if h(Z3[s]) != h(Z5[s]):
        nz += 1
        for a, b in zip(Z3[s], Z5[s]):
            dz = max(dz, abs(float(a[5]) - float(b[5])))
            assert a[:5] == b[:5], (s, a, b)
print("  zone-map: stems whose rows differ", nz, "(zone names equal in all; largest floor-area difference %.5f m2)" % dz)
S = [s for s in W5 if ch[s] != "origin_shift"]
print("REBUILT stems", len(S), "| wall-table rows equal", sum(1 for s in S if W3[s] == W5[s]), "| zone-map rows equal", sum(1 for s in S if h(Z3[s]) == h(Z5[s])))
u3 = sum(1 for r in W3.values() if not r[ri]); u5 = sum(1 for r in W5.values() if not r[ri])
print("usable (empty zone_map_reason) win3", u3, "bol5", u5, "| total flats win3", sum(int(r[ni]) for r in W3.values() if not r[ri]), "bol5", sum(int(r[ni]) for r in W5.values() if not r[ri]))
bad3 = {s for s, r in W3.items() if r[ri]}; bad5 = {s for s, r in W5.items() if r[ri]}
print("left out win3", len(bad3), sorted(bad3), "| bol5", len(bad5), sorted(bad5))
print("  newly left out:", sorted(bad5 - bad3), "| back in:", sorted(bad3 - bad5))
print("zone-map total rows win3", sum(len(v) for v in Z3.values()), "bol5", sum(len(v) for v in Z5.values()), "| per-stem n_flats == zone rows for every stem:", all(int(W5[s][ni]) == len(Z5[s]) for s in W5))
rows = []
for s in sorted(S):
    rows.append([s, ch[s], W3[s][ni], W5[s][ni], W3[s][ri], W5[s][ri], len(Z3[s]), len(Z5[s])])
with io.open(os.path.join(OUTD, "flatcounts_1070_win3_to_bol5.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["stem", "reason", "n_flats_win3", "n_flats_bol5", "reason_win3", "reason_bol5", "zone_rows_win3", "zone_rows_bol5"]); w.writerows(rows)
print("1,070 group: sum n_flats (wall table) old", sum(int(r[2]) for r in rows), "new", sum(int(r[3]) for r in rows))
# static tables
def rows_by_stem(p):
    r = rd(p); d = collections.OrderedDict()
    for x in r[1:]:
        d.setdefault(x[1], []).append(x)
    return r[0], d
for kind in ("flats", "buildings"):
    f = "%s_%s.csv" % (kind, D)
    h3, a = rows_by_stem(IMP + "/static_win3/" + f); h5, b = rows_by_stem(IMP + "/static_bol5/" + f)
    print("==", kind, "header equal", h3 == h5, "stems win3", len(a), "bol5", len(b), "rows win3", sum(len(v) for v in a.values()), "bol5", sum(len(v) for v in b.values()))
    ou = [s for s in b if ch[s] == "origin_shift"]
    eq = [s for s in ou if s in a and h(a[s]) == h(b[s])]
    print("  origin-only stems in bol5 table", len(ou), "| rows md5-equal to win3:", len(eq), "| origin-only stems usable in win3 but not here / missing:", [s for s in ou if s not in a])
    mxd, cols = 0.0, collections.Counter()
    for s in ou:
        if s in a and h(a[s]) != h(b[s]):
            assert len(a[s]) == len(b[s])
            for x, y in zip(a[s], b[s]):
                for i, (u, v) in enumerate(zip(x, y)):
                    if u != v:
                        cols[h3[i]] += 1
                        nu, nv = num(u), num(v)
                        if nu is not None and nv is not None:
                            mxd = max(mxd, abs(nu - nv))
                        else:
                            mxd = max(mxd, 1e9)
    print("  differing stems", len(ou) - len(eq), "| differing cells by column:", dict(cols), "| largest abs numeric difference %.5f" % mxd)
    print("  win3 stems not in bol5:", sorted(set(a) - set(b)), "| bol5 stems not in win3:", sorted(set(b) - set(a)))
h3, a = rows_by_stem(IMP + "/static_win3/flats_%s.csv" % D); h5, b = rows_by_stem(IMP + "/static_bol5/flats_%s.csv" % D)
out = [[s, ch[s], len(a.get(s, [])), len(b.get(s, []))] for s in sorted(set(a) | set(b)) if ch[s] != "origin_shift"]
with io.open(os.path.join(OUTD, "flatcounts_1070_static_win3_to_bol5.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["stem", "reason", "flats_win3", "flats_bol5"]); w.writerows(out)
print("1,070 group in the flats tables: stems present win3/bol5:", sum(1 for r in out if r[2]), sum(1 for r in out if r[3]), "| flats old", sum(r[2] for r in out), "new", sum(r[3] for r in out))
print("total flats win3", sum(len(v) for v in a.values()), "bol5", sum(len(v) for v in b.values()))
print("flat count unchanged for", sum(1 for r in out if r[2] == r[3] and r[2] > 0), "of the stems that are usable in both")
# tiny flats (rule R1 b)
fl3 = rd(IMP + "/static_win3/flats_%s.csv" % D); fl5 = rd(IMP + "/static_bol5/flats_%s.csv" % D)
ai = fl3[0].index("floor_area_m2")
print("flats under 15 m2: win3", sum(1 for r in fl3[1:] if float(r[ai]) < 15), "bol5", sum(1 for r in fl5[1:] if float(r[ai]) < 15), "| minimum flat area win3 %.3f bol5 %.3f" % (min(float(r[ai]) for r in fl3[1:]), min(float(r[ai]) for r in fl5[1:])))
