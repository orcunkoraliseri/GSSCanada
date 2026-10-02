import json, collections, csv, io
R = json.load(open("win5_check_results.json"))
ch = {}
for ln in open("C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05/changed_stems.txt"):
    s, r = ln.rstrip("\r\n").split("\t"); ch[s] = r
print("n", len(R), "bytes_equal", sum(r["bytes_equal"] for r in R), "any_diff", sum(r["any_diff"] for r in R))
diffset = set(r["stem"] for r in R if not r["bytes_equal"])
print("not byte equal == changed_stems:", diffset == set(ch))
print("any_diff set == not-byte-equal set:", set(r["stem"] for r in R if r["any_diff"]) == diffset)
for g in ("degenerate", "flat_count"):
    G = [r for r in R if ch.get(r["stem"]) == g]
    print("GROUP", g, len(G))
    for k in ("zones_same", "flat_names_same", "cons_same"):
        print("  ", k, sum(r[k] for r in G))
    print("  surf_deleted", sum(r["surf_deleted"] for r in G), "added", sum(r["surf_added"] for r in G), "modified", sum(r["surf_modified"] for r in G),
          "win_deleted", sum(r["win_deleted"] for r in G), "win_added", sum(r["win_added"] for r in G), "win_modified", sum(r["win_modified"] for r in G))
    print("  deleted area", sum(r["surf_deleted_area"] for r in G), "max", max(r["surf_deleted_maxarea"] for r in G), "win_deleted_area", sum(r["win_deleted_area"] for r in G), "win_deleted_host_kept", sum(r["win_deleted_host_kept"] for r in G))
    print("  flats old->new", sum(r["flats_old"] for r in G), sum(r["flats_new"] for r in G), "zones", sum(r["zones_old"] for r in G), sum(r["zones_new"] for r in G))
    print("  surf old->new", sum(r["surf_old"] for r in G), sum(r["surf_new"] for r in G), "area", sum(r["area_old"] for r in G), sum(r["area_new"] for r in G))
    print("  win old->new", sum(r["win_old"] for r in G), sum(r["win_new"] for r in G), "warea", sum(r["warea_old"] for r in G), sum(r["warea_new"] for r in G))
    rk, ak, mc = collections.Counter(), collections.Counter(), collections.Counter()
    for r in G:
        for k, v in r["obj_removed_by_kw"].items(): rk[k] += v
        for k, v in r["obj_added_by_kw"].items(): ak[k] += v
        for k, v in r["surf_modified_cols"].items(): mc[k] += v
    print("  removed by kw", dict(rk)); print("  added by kw", dict(ak)); print("  modified cols", dict(mc))
    print("  kept_zone_or_cons_changed", sum(r["kept_zone_or_cons_changed"] for r in G))
