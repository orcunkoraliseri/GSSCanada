# -*- coding: utf-8 -*-
"""5J Step 7 parts A + B (Speed CPU job): the 100-building sample of the Madrid stock and its 100 archetype twins.
  A. eligible buildings = the 1,151 buildings of the 4J Step 10 Madrid campaign (building ids of cells/ and cells_failed/ of
     /speed-scratch/o_iseri/4J_step10_nocore/out/ES-MAD-BERRUGUETE/, checked against preflight_report.json: eligible 1,151, dwellings 11,976).
     class, archetype_id, dwellings_total, storeys are read from each payload (layouts/{relation,way}/<id>.json). Sample 100, stratified by
     class in proportion (largest remainder), at least 5 per class, seed 20261001. Written to in/sample_buildings.csv.
  B. one 5J building row per sampled building (in/twins_es.csv, columns of campaign/in/buildings_es_it.csv, ids es_T001..es_T100),
     infiltration and north by the campaign's own rule (Latin hypercube, 5thJ_design_tables.lhs, ranges 0.3-1.0 and 0-360, seed 20261002),
     the IDF of each twin built once with the 5J builder (camp_common.build_run), size recorded next to the real one (in/twins_info_es.csv).
Seals (md5, append only): in/SEALS.md5."""
import collections, io, json, os, random, re, sys, contextlib, math
import s7_common as s7

PREF = "/speed-scratch/o_iseri/4J_step10_nocore/out/ES-MAD-BERRUGUETE/"
LAY = "/speed-scratch/o_iseri/4J_step10_nocore/tree/openubem/outputs/3D/eu_ES-MAD-BERRUGUETE_data/layouts/"
CELLRE = re.compile(r"^es__(relation|way)-(\d+)__case")
FAILS = []


def gate(name, ok, text=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def alloc_min(total, counts, minimum):
    """Largest-remainder allocation proportional to counts, then every class gets at least min(minimum, its size)."""
    n = float(sum(counts.values()))
    base, rem = {}, []
    for k in sorted(counts):
        q = total * counts[k] / n
        base[k] = int(q)
        rem.append((q - int(q), k))
    left = total - sum(base.values())
    for _, k in sorted(rem, reverse=True)[:left]:
        base[k] += 1
    for k in sorted(base):
        need = min(minimum, counts[k]) - base[k]
        while need > 0:
            donor = max((c for c in base if base[c] > min(minimum, counts[c])), key=lambda c: base[c])
            base[donor] -= 1
            base[k] += 1
            need -= 1
    assert sum(base.values()) == total and all(base[k] <= counts[k] for k in base)
    return base


def lhs(rng, n, lo, hi, nd):
    """Copy of 5thJ_design_tables.lhs (the campaign's own rule)."""
    perm = list(range(n))
    rng.shuffle(perm)
    return [round(lo + (perm[i] + rng.random()) / n * (hi - lo), nd) for i in range(n)]


def main():
    s7.stamp("s7_sample start host=%s" % os.uname()[1])
    # self-test of the allocation rule: plain proportional gives 2 to the small class; the rule must lift it to 5 and keep the total
    t = alloc_min(100, {"A": 20, "B": 970, "C": 8, "D": 2}, 5)
    gate("selftest_alloc_min_lifts_small_classes_and_keeps_total", t["A"] >= 5 and t["C"] >= 5 and t["D"] == 2 and sum(t.values()) == 100, str(t))
    bad = alloc_min(100, {"A": 20, "B": 970, "C": 8, "D": 2}, 0)
    gate("selftest_without_the_minimum_the_small_class_is_below_5 (seen failing)", bad["C"] < 5, str(bad))
    pre = json.load(io.open(PREF + "preflight_report.json", encoding="utf-8"))
    ids = set()
    n_files = {}
    for sub in ("cells", "cells_failed"):
        names = os.listdir(PREF + sub)
        n_files[sub] = len(names)
        for nm in names:
            m = CELLRE.match(nm)
            if m:
                ids.add((m.group(1), m.group(2)))
    print("CELL_FILES cells=%d cells_failed=%d distinct buildings=%d" % (n_files["cells"], n_files["cells_failed"], len(ids)))
    gate("eligible_count_equals_preflight_report", len(ids) == pre["eligible"] == 1151, "from cells=%d preflight eligible=%s" % (len(ids), pre["eligible"]))
    # ---- read payloads
    recs = []
    for kind, i in sorted(ids, key=lambda t: (t[0], int(t[1]))):
        j = json.load(io.open(LAY + "%s/%s.json" % (kind, i), encoding="utf-8"))
        aid = j.get("archetype_id")
        recs.append({"real_id": "%s-%s" % (kind, i), "building_type": j.get("building_type"), "archetype_id": aid,
                     "dwellings": j.get("dwellings_total"), "storeys": j.get("storeys"),
                     "cond_area": j.get("conditioned_floor_area_m2"), "provenance": j.get("dwelling_count_provenance")})
    nodw = [r["real_id"] for r in recs if r["dwellings"] is None]
    tot = sum(int(r["dwellings"]) for r in recs if r["dwellings"] is not None)
    print("PAYLOADS read=%d dwellings_total None=%d sum dwellings_total=%d (preflight dwellings_registered %s)" % (len(recs), len(nodw), tot, pre["dwellings_registered"]))
    gate("sum_dwellings_total_equals_preflight_11976", tot == pre["dwellings_registered"] and not nodw, "sum=%d none=%d" % (tot, len(nodw)))
    for r in recs:
        a = r["archetype_id"]
        assert a and a.endswith(".001") and len(a.split(".")) == 8, ("archetype_id form", r)
        r["code"] = a[:-4]
        r["cls"] = a.split(".")[2]
    cross = collections.Counter((r["building_type"], r["cls"]) for r in recs)
    print("CROSSTAB payload building_type x class of the archetype code:", dict(cross))
    gate("classes_are_the_four", set(r["cls"] for r in recs) <= set(s7.CLASSES), str(sorted(set(r["cls"] for r in recs))))
    cnt_all = collections.Counter(r["cls"] for r in recs)
    print("CLASS_COUNTS_1151 %s total=%d" % (dict((c, cnt_all[c]) for c in s7.CLASSES), sum(cnt_all.values())))
    # ---- A: sample
    take = alloc_min(s7.N_SAMPLE, dict(cnt_all), s7.MIN_PER_CLASS)
    rng = random.Random("%d|sample|es" % s7.SEED_SAMPLE)
    chosen = []
    for c in s7.CLASSES:
        pool = [r for r in recs if r["cls"] == c]        # already sorted by (kind, id)
        chosen += rng.sample(pool, take[c])
    cnt_s = collections.Counter(r["cls"] for r in chosen)
    print("CLASS_COUNTS_100 %s total=%d allocation=%s" % (dict((c, cnt_s[c]) for c in s7.CLASSES), len(chosen), take))
    gate("sample_is_100_and_each_class_at_least_5", len(chosen) == 100 and len(set(r["real_id"] for r in chosen)) == 100 and all(cnt_s[c] >= min(5, cnt_all[c]) for c in s7.CLASSES))
    os.makedirs(s7.IN, exist_ok=True)
    sp = s7.IN + "sample_buildings.csv"
    if os.path.exists(sp):
        os.rename(sp, sp + ".prev_%d" % int(__import__("time").time()))
    s7.write_csv(sp, ["twin_id", "real_id", "class", "code", "archetype_id", "real_dwellings", "real_storeys", "real_conditioned_area_m2", "dwelling_count_provenance"],
                 [["es_T%03d" % (n + 1), r["real_id"], r["cls"], r["code"], r["archetype_id"], r["dwellings"], r["storeys"], r["cond_area"], r["provenance"]] for n, r in enumerate(chosen)])
    # ---- B: twins
    bt = {r["archetype_code"]: r for r in s7.read_csv(s7.CAMP_IN + "buildings_es_it.csv") if r["country"] == "es"}
    rng2 = random.Random("%d|twins|es" % s7.SEED_TWIN)
    infil = lhs(rng2, len(chosen), 0.3, 1.0, 4)
    north = lhs(rng2, len(chosen), 0.0, 360.0, 2)
    trows = []
    for n, r in enumerate(chosen):
        per = bt[r["code"]]["period"] if r["code"] in bt else "ES.%s" % r["code"].split(".")[3]
        trows.append({"building_id": "es_T%03d" % (n + 1), "country": "es", "class": r["cls"], "archetype_code": r["code"], "period": per,
                      "infiltration_ach": "%.4f" % infil[n], "north_axis_deg": "%.2f" % north[n], "pilot": 0})
    hdr = ["building_id", "country", "class", "archetype_code", "period", "infiltration_ach", "north_axis_deg", "pilot"]
    camp_hdr = list(s7.read_csv(s7.CAMP_IN + "buildings_es_it.csv")[0].keys())
    gate("twin_columns_equal_campaign_building_table", hdr == camp_hdr, "%s vs %s" % (hdr, camp_hdr))
    tp = s7.TWINS_CSV
    if os.path.exists(tp):
        os.rename(tp, tp + ".prev_%d" % int(__import__("time").time()))
    s7.write_csv(tp, hdr, [[t[k] for k in hdr] for t in trows])
    cc = s7.install_twins()
    mz = cc.mzmod()
    codes_in_tab = {r["Code_Building"] for r in cc._tabula_rows("es")}
    miss = sorted({t["archetype_code"] for t in trows} - codes_in_tab)
    gate("all_twin_codes_in_the_TABULA_table", not miss, "missing %s; distinct codes %d" % (miss, len({t["archetype_code"] for t in trows})))
    hh60 = [r["hid"] for r in s7.read_csv(s7.IN + "ref/households.csv") if r["country"] == "es"]
    assert len(hh60) == 60, len(hh60)
    dev = {r["building_id"] for r in s7.read_csv(s7.IN + "ref/splits_buildings.csv") if r["country"] == "es" and r["split"] == "dev"}
    dev_codes = {bt2["archetype_code"] for bid, bt2 in ((r["building_id"], r) for r in s7.read_csv(s7.CAMP_IN + "buildings_es_it.csv")) if bid in dev}
    info = []
    for n, t in enumerate(trows):
        code = t["archetype_code"]
        row = {r["Code_Building"]: r for r in cc._tabula_rows("es")}[code]
        d = mz.derive(row)
        F = int(round(d["n_storey"]))
        k, _n_apt, _ln = mz.k_from_tabula(s7.CAMP_IN + "dwelling_count_es.csv", code, d["n_storey"])
        nd = 1 if t["class"] in ("SFH", "TH") else F * k
        plc = ";".join("%d:%s" % (j, hh60[j % 60]) for j in range(nd))
        run = {"country": "es", "building_id": t["building_id"], "n_floors": str(F), "k": str(k), "placement": plc, "climate_id": s7.CLIMATE, "class": t["class"]}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            idf, meta, got, bad_area = cc.build_run(run)
        okb = (not bad_area) and all(p in got for p in cc.PATCH_NAMES)
        area = sum(meta["zone_floor_areas"].values())
        ch = chosen[n]
        info.append([t["building_id"], ch["real_id"], t["class"], code, t["period"], "seen" if code in dev_codes else "new",
                     ch["dwellings"], nd, k, ch["storeys"], F, ch["cond_area"], "%.1f" % area, len(meta["zones"]), "1" if okb else "0", len(idf)])
        if not okb:
            FAILS.append("build_%s" % t["building_id"])
            print("BUILD_PROBLEM %s bad_area=%s patches=%d" % (t["building_id"], bad_area[:2], len(got)))
        if (n + 1) % 20 == 0:
            s7.stamp("built %d of %d twin IDFs" % (n + 1, len(trows)))
    ip = s7.IN + "twins_info_es.csv"
    if os.path.exists(ip):
        os.rename(ip, ip + ".prev_%d" % int(__import__("time").time()))
    s7.write_csv(ip, ["twin_id", "real_id", "class", "code", "period", "code_seen_in_dev_buildings", "real_dwellings", "twin_dwellings", "twin_k", "real_storeys", "twin_floors",
                      "real_conditioned_area_m2", "twin_floor_area_m2", "twin_zones", "idf_build_ok", "idf_chars"], info)
    gate("every_twin_idf_built_with_all_9_patch_lines_and_area_gates", all(r[14] == "1" for r in info), "built %d of %d" % (sum(1 for r in info if r[14] == "1"), len(info)))
    gate("twin_zones_equal_floors_times_k", all(r[13] == r[10] * r[8] for r in info), "zones = floors x k")
    rd = sum(int(r[6]) for r in info)
    td = sum(int(r[7]) for r in info)
    print("SIZE real dwellings of the 100 = %d ; twin dwellings = %d ; ratio %.3f" % (rd, td, td / float(rd)))
    byc = collections.defaultdict(lambda: [0, 0, 0])
    for r in info:
        byc[r[2]][0] += 1
        byc[r[2]][1] += int(r[6])
        byc[r[2]][2] += int(r[7])
    for c in s7.CLASSES:
        print("SIZE_CLASS %s buildings=%d real_dwellings=%d twin_dwellings=%d" % (c, byc[c][0], byc[c][1], byc[c][2]))
    exact = sum(1 for r in info if int(r[6]) == int(r[7]))
    print("SIZE_MATCH twins with twin dwellings == real dwellings: %d of 100; seen codes %d new codes %d" % (exact, sum(1 for r in info if r[5] == "seen"), sum(1 for r in info if r[5] == "new")))
    for r in info:
        if int(r[6]) != int(r[7]):
            print("SIZE_GAP %s real=%s twin=%s class=%s code=%s" % (r[0], r[6], r[7], r[2], r[3]))
    # ---- seals
    for p in (sp, tp, ip):
        s7.seal(p)
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
