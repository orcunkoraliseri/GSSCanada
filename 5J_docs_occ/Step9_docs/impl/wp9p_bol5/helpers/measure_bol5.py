# -*- coding: utf-8 -*-
"""Step 9p item 1: re-measure OpenUBEM Bologna `_win_2026-10-05` against `_win_2026-10-03`, per stem, with our own parser
(tools/5thJ_modelA_idf.py: objects, surface_of, area3, zone_map). Opens only the two Bologna district folders by full name (idfs/<stem>.idf and
md5_2026-10-05.txt / changed_stems.txt / dwelling_counts / origin_offset by full file name). No UK path. At most 10 processes.
Iterates the stems of md5_2026-10-05.txt (1,179).
Shift model: new = old - (DX, DY) in x, y; z unchanged. Coordinate-bearing objects covered: BUILDINGSURFACE:DETAILED (fields 11:),
FENESTRATIONSURFACE:DETAILED (9:), SHADING:*:DETAILED (3:), ZONE origin (fields 2,3,4 = x, y, z). Independent scan: ANY numeric field with
abs > 50,000 in the new IDF (any object kind) is counted, so a coordinate-bearing object kind we did not list cannot stay unshifted unseen.
Run: py measure_bol5.py   -> writes ../bol5_check_results.json, ../bol5_check_per_stem.csv, prints the plant tests.
"""
import os, sys, io, csv, json, hashlib, collections, re
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(HERE)
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools"))
sys.path.insert(0, TOOLS)
os.environ["MODELA_VINTAGE"] = "win_2026-10-03"      # import only; paths below are explicit
import importlib
M = importlib.import_module("5thJ_modelA_idf")
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
OLD = EU11 + "/IT-BOL-GALVANI2_win_2026-10-03"
NEW = EU11 + "/IT-BOL-GALVANI2_win_2026-10-05"
DX, DY = 685000.0, 4928000.0
TOLXY = 1e-6
SURF_FIELDS = ["name", "type", "cons", "zone", "space", "bc", "bcobj", "sun", "wind", "vf", "nverts"]


def md5_file(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def coord_start(kw):
    if kw == "BUILDINGSURFACE:DETAILED":
        return 11
    if kw.startswith("FENESTRATIONSURFACE"):
        return 9
    if kw.startswith("SHADING:") and kw.endswith(":DETAILED"):
        return 3
    return None


def fnum(s):
    try:
        return float(s)
    except Exception:
        return None


def vtx(f, start):
    c = f[start:]
    return [(float(c[i]), float(c[i + 1]), float(c[i + 2])) for i in range(0, len(c) - 2, 3)]


def profile_text(text, stem):
    objs = M.objects(text)
    p = {"zones": [], "surf": {}, "fen": {}, "cons": set(), "objs": collections.Counter(), "shade": {}, "big_kinds": collections.Counter(),
         "bld": None, "zone_org": [], "other": []}
    for o in objs:
        kw, f = o["kw"], o["fields"]
        p["objs"][(kw, tuple(f))] += 1
        if kw == "ZONE":
            p["zones"].append(f[0])
            p["zone_org"].append(tuple(f[1:5]))
        elif kw == "CONSTRUCTION":
            p["cons"].add(f[0])
        elif kw == "BUILDING":
            p["bld"] = tuple(f)
        elif kw == "BUILDINGSURFACE:DETAILED":
            s = M.surface_of(o)
            p["surf"][s["name"]] = {"type": s["type"], "cons": s["cons"], "zone": s["zone"], "bc": s["bc"], "bcobj": s["bcobj"],
                                    "verts": s["verts"], "area": M.area3(s["verts"]), "fields": tuple(f)}
        elif kw.startswith("FENESTRATIONSURFACE"):
            v = vtx(f, 9)
            p["fen"][f[0]] = {"cons": f[2], "host": f[3], "verts": v, "area": M.area3(v) * float(f[7] or 1), "fields": tuple(f)}
        elif kw.startswith("SHADING:") and kw.endswith(":DETAILED"):
            p["shade"][f[0]] = {"verts": vtx(f, 3), "fields": tuple(f)}
        # independent scan: any numeric field above 50,000 in absolute value
        for x in f:
            v = fnum(x)
            if v is not None and abs(v) > 50000:
                p["big_kinds"][kw] += 1
                break
    rows, reason, nz, nc = M.zone_map(text, stem, objs)
    p["flats"] = [r["zone"] for r in rows]
    p["floors"] = sorted(set(r["floor_k"] for r in rows))
    p["zone_reason"] = reason
    p["objs_list"] = [(o["kw"], tuple(o["fields"])) for o in objs]
    return p


def shift_cmp(a, b):
    """a = old profile (10-03), b = new (10-05). Returns shift statistics.
    obj_aligned: all objects pairwise (same order, same keyword, same field count). Max deviations are over every coordinate triple that
    belongs to a coordinate-bearing object; non-coordinate fields must be string-equal."""
    d = {}
    la, lb = a["objs_list"], b["objs_list"]
    d["obj_count_old"], d["obj_count_new"] = len(la), len(lb)
    aligned = len(la) == len(lb) and all(x[0] == y[0] and len(x[1]) == len(y[1]) for x, y in zip(la, lb))
    d["obj_aligned"] = int(aligned)
    mx = my = mz = 0.0
    nonc_diff = 0
    nonc_diff_kinds = collections.Counter()
    zorg_diff = 0
    if aligned:
        for (ka, fa), (kb, fb) in zip(la, lb):
            cs = coord_start(ka)
            if ka == "ZONE":
                cs_zone = True
            else:
                cs_zone = False
            for i, (xa, xb) in enumerate(zip(fa, fb)):
                is_coord = cs is not None and i >= cs
                if is_coord:
                    ax, bx = fnum(xa), fnum(xb)
                    k = (i - cs) % 3
                    if k == 0:
                        mx = max(mx, abs((bx - (ax - DX))))
                    elif k == 1:
                        my = max(my, abs((bx - (ax - DY))))
                    else:
                        mz = max(mz, abs(bx - ax))
                elif xa != xb:
                    nonc_diff += 1
                    nonc_diff_kinds[ka] += 1
    d["shift_max_dx"], d["shift_max_dy"], d["shift_max_dz"] = mx, my, mz
    d["noncoord_field_diffs"] = nonc_diff
    d["noncoord_diff_kinds"] = dict(nonc_diff_kinds)
    d["exact_shift_all_vertices"] = int(aligned and mx <= TOLXY and my <= TOLXY and mz <= TOLXY and nonc_diff == 0)
    # shading objects (context): exact shift for every common name, any stem
    sh_common = set(a["shade"]) & set(b["shade"])
    sh_bad = 0
    for n in sh_common:
        va, vb = a["shade"][n]["verts"], b["shade"][n]["verts"]
        if len(va) != len(vb) or any(abs(q[0] - DX - r[0]) > TOLXY or abs(q[1] - DY - r[1]) > TOLXY or abs(q[2] - r[2]) > TOLXY for q, r in zip(va, vb)):
            sh_bad += 1
    d["shade_old"], d["shade_new"] = len(a["shade"]), len(b["shade"])
    d["shade_common"], d["shade_shift_bad"] = len(sh_common), sh_bad
    # building surfaces with the same name: how many keep an exact shift
    sc = set(a["surf"]) & set(b["surf"])
    s_exact = 0
    for n in sc:
        va, vb = a["surf"][n]["verts"], b["surf"][n]["verts"]
        if len(va) == len(vb) and all(abs(q[0] - DX - r[0]) <= TOLXY and abs(q[1] - DY - r[1]) <= TOLXY and abs(q[2] - r[2]) <= TOLXY for q, r in zip(va, vb)):
            s_exact += 1
    d["surf_same_name"], d["surf_same_name_exact_shift"] = len(sc), s_exact
    # bounding boxes of building surfaces (x, y after shift, z)
    def bbox(p):
        xs = [v[0] for s in p["surf"].values() for v in s["verts"]]
        ys = [v[1] for s in p["surf"].values() for v in s["verts"]]
        zs = [v[2] for s in p["surf"].values() for v in s["verts"]]
        return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)) if xs else (0,) * 6
    ba, bb = bbox(a), bbox(b)
    d["bbox_dev_xy"] = max(abs(ba[0] - DX - bb[0]), abs(ba[1] - DX - bb[1]), abs(ba[2] - DY - bb[2]), abs(ba[3] - DY - bb[3]))
    d["bbox_dev_z"] = max(abs(ba[4] - bb[4]), abs(ba[5] - bb[5]))
    d["big_kinds_new"] = dict(b["big_kinds"])
    d["big_kinds_old"] = dict(a["big_kinds"])
    d["bld_same"] = int(a["bld"] == b["bld"])
    d["zone_origin_same"] = int(a["zone_org"] == b["zone_org"][:len(a["zone_org"])] or a["zone_org"] == b["zone_org"]) if a["zone_org"] and b["zone_org"] else 0
    d["zone_origin_all_zero_new"] = int(all(all(fnum(q) == 0.0 for q in zo[1:4]) for zo in b["zone_org"]) if b["zone_org"] else 1)
    d["new_min_x"] = bb[0]; d["new_max_x"] = bb[1]; d["new_min_y"] = bb[2]; d["new_max_y"] = bb[3]
    return d


def compare(a, b):
    d = {}
    d["zones_old"], d["zones_new"] = len(a["zones"]), len(b["zones"])
    d["zones_same"] = int(a["zones"] == b["zones"])
    d["flats_old"], d["flats_new"] = len(a["flats"]), len(b["flats"])
    d["floors_old"], d["floors_new"] = len(a["floors"]), len(b["floors"])
    d["flat_names_same"] = int(set(a["flats"]) == set(b["flats"]))
    d["surf_old"], d["surf_new"] = len(a["surf"]), len(b["surf"])
    d["area_old"], d["area_new"] = sum(s["area"] for s in a["surf"].values()), sum(s["area"] for s in b["surf"].values())
    d["win_old"], d["win_new"] = len(a["fen"]), len(b["fen"])
    d["warea_old"], d["warea_new"] = sum(s["area"] for s in a["fen"].values()), sum(s["area"] for s in b["fen"].values())
    d["cons_same"] = int(a["cons"] == b["cons"])
    dn = set(a["surf"]) - set(b["surf"])
    an = set(b["surf"]) - set(a["surf"])
    d["surf_deleted"], d["surf_added"] = len(dn), len(an)
    d["surf_deleted_area"] = sum(a["surf"][n]["area"] for n in dn)
    wd = set(a["fen"]) - set(b["fen"])
    wa = set(b["fen"]) - set(a["fen"])
    d["win_deleted"], d["win_added"] = len(wd), len(wa)
    # outdoor wall / roof / floor-to-ground area (envelope), shift-invariant
    def env(p):
        o = {"out_wall": 0.0, "roof": 0.0, "ground": 0.0, "inter_wall": 0.0}
        for s in p["surf"].values():
            if s["type"] == "wall" and s["bc"] == "outdoors":
                o["out_wall"] += s["area"]
            elif s["type"] == "roof" and s["bc"] == "outdoors":
                o["roof"] += s["area"]
            elif s["type"] == "floor" and s["bc"] == "ground":
                o["ground"] += s["area"]
        return o
    ea, eb = env(a), env(b)
    for k in ea:
        d[k + "_old"], d[k + "_new"] = ea[k], eb[k]
    mod = [n for n in a["surf"] if n in b["surf"] and a["surf"][n]["fields"][:11] != b["surf"][n]["fields"][:11]]
    d["surf_head_modified"] = len(mod)      # fields before the coordinates (name,type,cons,zone,...,nverts)
    d["kept_zone_or_cons_changed"] = sum(1 for n in a["surf"] if n in b["surf"] and (a["surf"][n]["zone"] != b["surf"][n]["zone"] or a["surf"][n]["cons"] != b["surf"][n]["cons"] or a["surf"][n]["type"] != b["surf"][n]["type"]))
    # shift-invariant multiset comparison of objects, coordinates ignored: key = (kw, fields before the coordinates)
    def head(p):
        c = collections.Counter()
        for kw, f in p["objs_list"]:
            cs = coord_start(kw)
            c[(kw, f if cs is None else f[:cs])] += 1
        return c
    ha, hb = head(a), head(b)
    rem, add = ha - hb, hb - ha
    rk, ak = collections.Counter(), collections.Counter()
    for (kw, f), n in rem.items():
        rk[kw] += n
    for (kw, f), n in add.items():
        ak[kw] += n
    d["obj_removed_by_kw"], d["obj_added_by_kw"] = dict(rk), dict(ak)
    d["any_diff_noncoord"] = int(bool(rem or add))
    # surface-level area difference by same name (shift invariant)
    ad = [abs(a["surf"][n]["area"] - b["surf"][n]["area"]) for n in a["surf"] if n in b["surf"] and len(a["surf"][n]["verts"]) == len(b["surf"][n]["verts"])]
    d["same_name_area_maxdiff"] = max(ad) if ad else 0.0
    d.update(shift_cmp(a, b))
    return d


def work(stem):
    po, pn = OLD + "/idfs/%s.idf" % stem, NEW + "/idfs/%s.idf" % stem
    mo, mn = md5_file(po), md5_file(pn)
    a, b = profile_text(M.read_text(po), stem), profile_text(M.read_text(pn), stem)
    d = compare(a, b)
    d["stem"], d["md5_old"], d["md5_new"] = stem, mo, mn
    d["bytes_equal"] = int(mo == mn)
    d["zone_reason_old"], d["zone_reason_new"] = a["zone_reason"], b["zone_reason"]
    d["flats_list_old"], d["flats_list_new"] = a["flats"], b["flats"]
    return d


def plant_tests(stem):
    """Seen failing. (1) 10-03 copy with one surface deleted vs the unplanted 10-03: the counters (surfaces, area, any_diff_noncoord) flag it.
    (2) the real 10-05 copy of an origin-only stem with one vertex moved 0.1 m (x, then z): the shift check flags it; the unplanted pair is clean.
    (3) the real 10-05 copy with a window deleted, (4) with a zone renamed."""
    res = {}
    to = M.read_text(OLD + "/idfs/%s.idf" % stem)
    tn = M.read_text(NEW + "/idfs/%s.idf" % stem)
    a, b = profile_text(to, stem), profile_text(tn, stem)
    c0 = compare(a, b)
    res["unplanted"] = {"exact_shift_all_vertices": c0["exact_shift_all_vertices"], "any_diff_noncoord": c0["any_diff_noncoord"], "surf_deleted": c0["surf_deleted"]}
    objs = M.objects(to)
    victim = next(o for o in objs if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "wall")
    t2 = to[:victim["start"]] + to[victim["end"]:]
    d2 = compare(a, profile_text(t2, stem))        # old vs planted-old (no shift expected: only compare the non-shift counters)
    res["planted_10_03_surface_deleted"] = {"victim": victim["fields"][0], "surf_deleted": d2["surf_deleted"], "any_diff_noncoord": d2["any_diff_noncoord"],
                                             "area_changed": int(abs(d2["area_old"] - d2["area_new"]) > 1e-9), "surf_old": d2["surf_old"], "surf_new": d2["surf_new"]}
    # (2) one vertex moved 0.1 m in the 10-05 copy (first BUILDINGSURFACE vertex, x field)
    nobjs = M.objects(tn)
    sv = next(o for o in nobjs if o["kw"] == "BUILDINGSURFACE:DETAILED")
    seg = tn[sv["start"]:sv["end"]]
    m = list(re.finditer(r"([-0-9.eE+]+)(\s*[,;]\s*!- Vertex 1 Xcoordinate)", seg))[0]
    newv = "%.10f" % (float(m.group(1)) + 0.1)
    seg2 = seg[:m.start(1)] + newv + seg[m.end(1):]
    tn2 = tn[:sv["start"]] + seg2 + tn[sv["end"]:]
    d3 = compare(a, profile_text(tn2, stem))
    res["planted_10_05_vertex_x_plus_0.1"] = {"exact_shift_all_vertices": d3["exact_shift_all_vertices"], "shift_max_dx": d3["shift_max_dx"], "surf_same_name_exact_shift": d3["surf_same_name_exact_shift"],
                                                "surf_same_name": d3["surf_same_name"]}
    m = list(re.finditer(r"([-0-9.eE+]+)(\s*[,;]\s*!- Vertex 1 Zcoordinate)", seg))[0]
    seg3 = seg[:m.start(1)] + "%.10f" % (float(m.group(1)) + 0.1) + seg[m.end(1):]
    tn3 = tn[:sv["start"]] + seg3 + tn[sv["end"]:]
    d4 = compare(a, profile_text(tn3, stem))
    res["planted_10_05_vertex_z_plus_0.1"] = {"exact_shift_all_vertices": d4["exact_shift_all_vertices"], "shift_max_dz": d4["shift_max_dz"]}
    # unshifted copy: the 10-03 text itself used as "new" must fail the shift check on every vertex
    d5 = compare(a, profile_text(to, stem))
    res["planted_unshifted_copy_as_new"] = {"exact_shift_all_vertices": d5["exact_shift_all_vertices"], "shift_max_dx": d5["shift_max_dx"], "big_kinds_new": d5["big_kinds_new"]}
    # window deleted in the 10-05 copy
    wv = next((o for o in nobjs if o["kw"].startswith("FENESTRATIONSURFACE")), None)
    if wv is not None:
        t6 = tn[:wv["start"]] + tn[wv["end"]:]
        d6 = compare(a, profile_text(t6, stem))
        res["planted_10_05_window_deleted"] = {"win_deleted": d6["win_deleted"], "any_diff_noncoord": d6["any_diff_noncoord"], "exact_shift_all_vertices": d6["exact_shift_all_vertices"]}
    zo = next(o for o in nobjs if o["kw"] == "ZONE")
    t7 = tn.replace(zo["fields"][0], zo["fields"][0] + "X")
    d7 = compare(a, profile_text(t7, stem))
    res["planted_10_05_zone_renamed"] = {"zones_same": d7["zones_same"], "any_diff_noncoord": d7["any_diff_noncoord"]}
    return res


if __name__ == "__main__":
    stems = []
    with io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                stems.append(ln.split()[-1][:-4])
    print("stems in md5 file:", len(stems), "unique:", len(set(stems)))
    with Pool(10) as pool:
        res = pool.map(work, stems, chunksize=4)
    with io.open(os.path.join(OUTD, "bol5_check_results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh)
    print("done", len(res))
    origin_only = []
    with io.open(NEW + "/changed_stems.txt", encoding="utf-8") as fh:
        for ln in fh:
            p = ln.rstrip("\r\n").split("\t")
            if len(p) > 1 and p[1] == "origin_shift":
                origin_only.append(p[0])
    print("PLANT stem", origin_only[0])
    print("PLANT", json.dumps(plant_tests(origin_only[0]), indent=1))
