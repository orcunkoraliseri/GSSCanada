# -*- coding: utf-8 -*-
"""5J Step 9f: Model A static-vector reader. Reads EnergyPlus INPUT text only (windowed IDFs), never any output.

Task: Step9_docs/impl/2026-10-01_wp9f_static_vector_TASK.md
Districts: ES-MAD-BERRUGUETE and IT-BOL-GALVANI2 only (UK licence: nothing else may be named here).
Run:  py tools/5thJ_modelA_static.py          (one process; writes Step9_docs/impl/static/*)
Parsing is reused from 5thJ_modelA_idf.py (objects, surface_of, area3, newell, classify_wall, zone_map, read_text, idf_path).
"""
import csv
import hashlib
import io
import math
import os
import statistics
import sys
import time

# Base switch (additive, old behaviour is the default): MODELA_VINTAGE=win_2026-10-02 = OpenUBEM's fixed base (outward walls),
# outputs go to impl/static_win2/ and read the `_win2` wall table / zone map. Must be set before the import below.
_VINTAGE = os.environ.get("MODELA_VINTAGE") or "win_2026-10-01"
_SUFFIX = {"win_2026-10-01": "win", "win_2026-10-02": "win2", "win_2026-10-03": "win3", "win_2026-10-05": "win5"}   # step 9j: win_2026-10-03 -> `_win3` names; step 9o: win_2026-10-05 -> `_win5` (Madrid only)
if _VINTAGE not in _SUFFIX:
    raise SystemExit("MODELA_VINTAGE must be win_2026-10-01, win_2026-10-02, win_2026-10-03 or win_2026-10-05, got %r" % _VINTAGE)
os.environ["MODELA_VINTAGE"] = _VINTAGE
WIN2 = _VINTAGE in ("win_2026-10-02", "win_2026-10-03", "win_2026-10-05")   # fixed bases: the "outward" check replaces the "inverted" check
# step 9p (additive): MODELA_COUNTRY=IT with win_2026-10-05 = Bologna only, own names `_bol5` (cannot collide with the Madrid `_win5` files); unset = unchanged
_COUNTRY = os.environ.get("MODELA_COUNTRY", "")
if _COUNTRY not in ("", "IT") or (_COUNTRY and _VINTAGE != "win_2026-10-05"):
    raise SystemExit("MODELA_COUNTRY must be empty or IT, and IT only with win_2026-10-05, got %r with %r" % (_COUNTRY, _VINTAGE))
_BOL5 = (_COUNTRY == "IT")
sys.dont_write_bytecode = True
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import importlib
M = importlib.import_module("5thJ_modelA_idf")
assert M.VINTAGE == _VINTAGE

IMPL = os.path.normpath(os.path.join(_HERE, "..", "Step9_docs", "impl"))
OUT = os.path.join(IMPL, {"win": "static", "win2": "static_win2", "win3": "static_win3", "win5": "static_win5"}[_SUFFIX[_VINTAGE]])
if _BOL5:
    OUT = os.path.join(IMPL, "static_bol5")
# step 9o: `_win_2026-10-05` is delivered for Madrid only; the other values keep both districts
_DISTRICTS = ("ES-MAD-BERRUGUETE",) if _VINTAGE == "win_2026-10-05" else None
WALLS_CSV = os.path.join(IMPL, "2026-10-01_wp9c_wall_table_%s.csv" % _SUFFIX[_VINTAGE])
ZONES_CSV = os.path.join(IMPL, "2026-10-01_wp9c_zone_map_%s.csv" % _SUFFIX[_VINTAGE])
if _BOL5:
    _DISTRICTS = ("IT-BOL-GALVANI2",)
    WALLS_CSV = os.path.join(IMPL, "2026-10-01_wp9c_wall_table_bol5.csv")
    ZONES_CSV = os.path.join(IMPL, "2026-10-01_wp9c_zone_map_bol5.csv")
BINS = ["N", "E", "S", "W"]
# film resistances (m2K/W), ISO 6946 style; ground floor: inside film only, ground resistance NOT added (stated limit)
FILM = {"wall": (0.13, 0.04), "roof": (0.10, 0.04), "floor": (0.17, 0.0)}


def az_bin(az):
    a = az % 360.0
    if a >= 315.0 or a < 45.0:
        return "N"
    if a < 135.0:
        return "E"
    if a < 225.0:
        return "S"
    return "W"


def azimuth(verts, north_axis):
    sx, sy, sz = M.newell(verts)
    return (math.degrees(math.atan2(sx, sy)) + north_axis) % 360.0   # outward normal, clockwise from +Y, + North Axis


def inside(pt, poly):
    """2-D point-in-polygon (even-odd) on x, y."""
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i][0], poly[i][1]
        x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def read_csv(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def material_R(objs):
    mats = {}
    for o in objs:
        f = o["fields"]
        if o["kw"] == "MATERIAL":
            mats[f[0]] = float(f[2]) / float(f[3])             # thickness / conductivity
        elif o["kw"] == "MATERIAL:NOMASS":
            mats[f[0]] = float(f[2])
        elif o["kw"] == "MATERIAL:AIRGAP":
            mats[f[0]] = float(f[1])
    cons = {}
    for o in objs:
        if o["kw"] == "CONSTRUCTION":
            cons[o["fields"][0]] = [x for x in o["fields"][1:] if x]
    glaz = {}
    for o in objs:
        if o["kw"] == "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM":
            glaz[o["fields"][0]] = (float(o["fields"][1]), float(o["fields"][2]))
    return mats, cons, glaz


def u_of(cons_name, kind, mats, cons):
    r = sum(mats[l] for l in cons[cons_name])
    rsi, rse = FILM[kind]
    return 1.0 / (r + rsi + rse)


def extract(text, district, stem, north_override=None, wrow=None):
    """Return (flat rows, building dict, aux) for one IDF text."""
    objs = M.objects(text)
    mats, cons, glaz = material_R(objs)
    north = 0.0
    nshade = 0
    zone_rot = 0
    zone_mult = {}
    for o in objs:
        if o["kw"] == "BUILDING":
            north = float(o["fields"][1] or 0)
        elif o["kw"].startswith("SHADING:"):
            nshade += 1
        elif o["kw"] == "ZONE":
            f = o["fields"]
            if any(float(f[i] or 0) != 0 for i in (1, 2, 3, 4)):
                zone_rot += 1
            zone_mult[f[0]] = float(f[6] or 1)
    if north_override is not None:
        north = north_override
    zrows, reason, _, _ = M.zone_map(text, stem, objs)
    flats = {z["zone"]: {"district": district, "stem": stem, "zone": z["zone"], "floor_k": z["floor_k"],
                         "storeys_spanned": int(zone_mult.get(z["zone"], 1)), "floor_area_m2": 0.0,
                         **{"wall_" + b + "_m2": 0.0 for b in BINS}, **{"win_" + b + "_m2": 0.0 for b in BINS},
                         "adiabatic_wall_m2": 0.0, "roof_m2": 0.0, "ground_floor_m2": 0.0} for z in zrows}
    surf_zone = {}
    uw = {"wall": [0.0, 0.0], "roof": [0.0, 0.0], "floor": [0.0, 0.0]}   # area, area*U
    gr = [0.0, 0.0]
    elig_area = 0.0
    n_out_walls = 0
    out_wall_area = 0.0
    normal_viol = 0
    ambiguous = 0
    n_floor = n_roof = 0
    surf_normal = {}
    floor_dir_viol = 0
    roof_dir_viol = 0
    kinds = {"eligible_rectangle": 0, "too_small": 0, "triangle": 0, "other_shape": 0}
    # zone floor centroids (for the outward-normal check)
    zc = {}
    surfs = []
    for o in objs:
        if o["kw"] == "BUILDINGSURFACE:DETAILED":
            s = M.surface_of(o)
            surfs.append(s)
            surf_zone[s["name"]] = s["zone"]
            if s["type"] == "floor":
                a = M.area3(s["verts"])
                zc.setdefault(s["zone"], []).append(s["verts"])
    for s in surfs:
        z = flats.get(s["zone"])
        a = M.area3(s["verts"])
        surf_normal[s["name"]] = M.newell(s["verts"])
        if s["type"] == "floor":
            n_floor += 1
            if z is not None:
                z["floor_area_m2"] += a
            sx, sy, sz = M.newell(s["verts"])
            if sz >= 0:
                floor_dir_viol += 1
            if s["bc"] == "ground":
                if z is not None:
                    z["ground_floor_m2"] += a
                gu = u_of(s["cons"], "floor", mats, cons)
                gr[0] += a
                gr[1] += a * gu
                uw["floor"][0] += a
                uw["floor"][1] += a * gu
        elif s["type"] == "roof" and s["bc"] == "outdoors":
            n_roof += 1
            if z is not None:
                z["roof_m2"] += a
            sx, sy, sz = M.newell(s["verts"])
            if sz <= 0:
                roof_dir_viol += 1
            ru = u_of(s["cons"], "roof", mats, cons)
            uw["roof"][0] += a
            uw["roof"][1] += a * ru
        elif s["type"] == "wall":
            if s["bc"] == "adiabatic":
                if z is not None:
                    z["adiabatic_wall_m2"] += a
            elif s["bc"] == "outdoors":
                n_out_walls += 1
                out_wall_area += a
                k = M.classify_wall(s["verts"])
                kinds[k] += 1
                if k == "eligible_rectangle":
                    elig_area += a
                b = az_bin(azimuth(s["verts"], north))
                if z is not None:
                    z["wall_" + b + "_m2"] += a
                wu = u_of(s["cons"], "wall", mats, cons)
                uw["wall"][0] += a
                uw["wall"][1] += a * wu
                # outward-normal check: wall centroid minus zone floor centroid should lie on the normal's side
                sx, sy, sz = M.newell(s["verts"])
                wx = sum(v[0] for v in s["verts"]) / len(s["verts"])
                wy = sum(v[1] for v in s["verts"]) / len(s["verts"])
                polys = zc.get(s["zone"], [])
                nn_ = math.hypot(sx, sy)
                if polys and nn_ > 0:
                    px, py_ = wx + 0.05 * sx / nn_, wy + 0.05 * sy / nn_
                    mx, my = wx - 0.05 * sx / nn_, wy - 0.05 * sy / nn_
                    plus_in = any(inside((px, py_), pl) for pl in polys)
                    minus_in = any(inside((mx, my), pl) for pl in polys)
                    if plus_in and not minus_in:
                        normal_viol += 1
                    elif not plus_in and not minus_in or (plus_in and minus_in):
                        ambiguous += 1
    # windows
    win_area = 0.0
    wu_sum = [0.0, 0.0, 0.0]   # area, area*U, area*SHGC
    n_win = 0
    win_wall_disagree = 0
    for o in objs:
        if o["kw"].startswith("FENESTRATIONSURFACE"):
            f = o["fields"]
            c = f[9:]
            v = [(float(c[i]), float(c[i + 1]), float(c[i + 2])) for i in range(0, len(c) - 2, 3)]
            a = M.area3(v) * float(f[7] or 1)
            zname = surf_zone.get(f[3])
            bn = surf_normal.get(f[3])
            wn_ = M.newell(v)
            if bn is not None and bn[0] * wn_[0] + bn[1] * wn_[1] + bn[2] * wn_[2] <= 0:
                win_wall_disagree += 1
            b = az_bin(azimuth(v, north))
            if zname in flats:
                flats[zname]["win_" + b + "_m2"] += a
            win_area += a
            n_win += 1
            lay = cons[f[2]][0]
            u, sh = glaz[lay]
            wu_sum[0] += a
            wu_sum[1] += a * u
            wu_sum[2] += a * sh
    rows = [flats[z["zone"]] for z in zrows]
    # roof U fallback: building has no outdoor roof surface -> the IDF's own roof construction (name kept in 'u_roof_src')
    roof_src = "surfaces"
    if uw["roof"][0] > 0:
        u_roof = uw["roof"][1] / uw["roof"][0]
    else:
        rn = [n for n in cons if "roof" in n.lower()]
        u_roof = u_of(rn[0], "roof", mats, cons) if rn else float("nan")
        roof_src = "construction_only" if rn else "none"
    floor_src = "ground_surfaces"
    if uw["floor"][0] > 0:
        u_floor = uw["floor"][1] / uw["floor"][0]
    else:
        fn = [n for n in cons if "floor" in n.lower() and "mass" not in n.lower()]
        u_floor = u_of(fn[0], "floor", mats, cons) if fn else float("nan")
        floor_src = "construction_only" if fn else "none"
    if uw["wall"][0] > 0:
        u_wall = uw["wall"][1] / uw["wall"][0]
        wall_src = "surfaces"
    else:
        wn = [n for n in cons if "wall" in n.lower()]
        u_wall = u_of(wn[0], "wall", mats, cons) if wn else float("nan")
        wall_src = "construction_only" if wn else "none"
    if wu_sum[0] > 0:
        u_win, shgc = wu_sum[1] / wu_sum[0], wu_sum[2] / wu_sum[0]
        win_src = "surfaces"
    else:
        g = list(glaz.values())
        if g:
            u_win, shgc = g[0]
            win_src = "glazing_only"
        elif wrow is not None:
            u_win, shgc = float(wrow["u"]), float(wrow["shgc"])    # no window object in the IDF (no outdoor wall): windows.csv value that would be inserted
            win_src = "windows_csv"
        else:
            u_win, shgc, win_src = float("nan"), float("nan"), "none"
    bld = {"district": district, "stem": stem, "storeys": len({r["floor_k"] for r in rows}), "flats": len(rows),
           "conditioned_area_m2": sum(r["floor_area_m2"] for r in rows),
           "u_wall": u_wall, "u_roof": u_roof, "u_floor": u_floor, "u_window": u_win, "shgc_window": shgc,
           "window_share": (win_area / out_wall_area) if out_wall_area > 0 else 0.0,
           "n_shading": nshade, "no_outdoor_wall": int(n_out_walls == 0),
           "u_src": "wall:%s;roof:%s;floor:%s;window:%s" % (wall_src, roof_src, floor_src, win_src)}
    aux = {"north": north, "zone_rot": zone_rot, "n_out_walls": n_out_walls, "out_wall_area": out_wall_area,
           "elig_area": elig_area, "kinds": kinds, "win_area": win_area, "n_win": n_win,
           "normal_viol": normal_viol, "ambiguous": ambiguous, "n_floor": n_floor, "n_roof": n_roof, "win_wall_disagree": win_wall_disagree, "floor_dir_viol": floor_dir_viol, "roof_dir_viol": roof_dir_viol,
           "reason": reason, "n_zone_rows": len(zrows), "u_win": u_win, "shgc": shgc}
    return rows, bld, aux


FLAT_COLS = ["district", "stem", "zone", "floor_k", "storeys_spanned", "floor_area_m2",
             "wall_N_m2", "wall_E_m2", "wall_S_m2", "wall_W_m2", "win_N_m2", "win_E_m2", "win_S_m2", "win_W_m2",
             "adiabatic_wall_m2", "roof_m2", "ground_floor_m2", "top_flag", "ground_flag"]
BLD_COLS = ["district", "stem", "building_id", "class", "age_band", "age_band_prepared", "storeys", "flats",
            "conditioned_area_m2", "u_wall", "u_roof", "u_floor", "u_window", "shgc_window", "window_share",
            "n_shading", "no_outdoor_wall", "u_src"]


def fmt(v):
    if isinstance(v, float):
        return "%.6g" % v if abs(v) < 1e-3 and v != 0 else "%.4f" % v
    return v


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    walls = read_csv(WALLS_CSV)
    zones = read_csv(ZONES_CSV)
    log = []

    def say(s):
        print(s)
        log.append(s)
        sys.stdout.flush()

    zmap = {}
    for r in zones:
        zmap.setdefault((r["district"], r["stem"]), {})[r["zone"]] = r
    results = {}
    outfiles = []
    for d in (_DISTRICTS or M.DISTRICTS):
        wrows = [w for w in walls if w["district"] == d and not w["zone_map_reason"]]
        wcsv = M.read_windows_csv(d)
        prep = {r["stem"]: r for r in M.read_prepared(d)}
        fl_rows, b_rows = [], []
        chk = {"flat_rows": 0, "zone_rows_expected": 0, "win_bad": [], "wall_bad": [], "cnt_bad": [], "u_bad": [], "shgc_bad": [],
               "area_bad": [], "zone_name_bad": 0, "normal_viol": 0, "floor_viol": 0, "roof_viol": 0, "n_wall": 0, "ambig": 0, "n_floor": 0, "n_roof": 0, "ww_dis": 0, "north_nonzero": [],
               "zone_rot": 0, "age_mismatch": [], "src_fallback": {}}
        per_b = []
        for i, w in enumerate(wrows):
            stem = w["stem"]
            text = M.read_text(M.idf_path(d, stem))
            rows, bld, aux = extract(text, d, stem, wrow=wcsv[stem])
            pr = prep[stem]
            parts = pr["archetype_id"].split(".")
            bld["building_id"] = pr["building_id"]
            bld["class"] = pr["building_type"]
            bld["age_band"] = parts[3]
            bld["age_band_prepared"] = pr["age_band"]
            if pr["age_band"].split(".")[-1] != parts[3]:
                chk["age_mismatch"].append(stem)
            for r in rows:
                r["top_flag"] = int(r["roof_m2"] > 0)
                r["ground_flag"] = int(r["ground_floor_m2"] > 0)
            fl_rows += rows
            b_rows.append(bld)
            per_b.append((stem, rows, bld, aux))
            chk["flat_rows"] += len(rows)
            exp = zmap.get((d, stem), {})
            chk["zone_rows_expected"] += len(exp)
            if {r["zone"] for r in rows} != set(exp):
                chk["zone_name_bad"] += 1
            for r in rows:
                e = exp.get(r["zone"])
                if e and abs(r["floor_area_m2"] - float(e["floor_area_m2"])) > 1e-3:
                    chk["area_bad"].append(r["zone"])
            wa = sum(r["win_" + b + "_m2"] for r in rows for b in BINS)
            if abs(wa - float(w["window_area_m2_idf"])) > 0.01:
                chk["win_bad"].append((stem, wa, w["window_area_m2_idf"]))
            ncount = int(w["outdoor_eligible_rectangle"]) + int(w["outdoor_too_small"]) + int(w["outdoor_triangle"]) + int(w["outdoor_other_shape"])
            if ncount != aux["n_out_walls"]:
                chk["cnt_bad"].append((stem, ncount, aux["n_out_walls"]))
            if abs(aux["elig_area"] - float(w["eligible_wall_area_m2"])) > 0.01:
                chk["wall_bad"].append((stem, aux["elig_area"], w["eligible_wall_area_m2"]))
            binsum = sum(r["wall_" + b + "_m2"] for r in rows for b in BINS)
            if abs(binsum - aux["out_wall_area"]) > 0.01:
                chk["wall_bad"].append((stem, "binsum", binsum, aux["out_wall_area"]))
            wc = wcsv[stem]
            if abs(aux["u_win"] - float(wc["u"])) > 0.01:
                chk["u_bad"].append(stem)
            if abs(aux["shgc"] - float(wc["shgc"])) > 0.01:
                chk["shgc_bad"].append(stem)
            chk["normal_viol"] += aux["normal_viol"]
            chk["n_wall"] += aux["n_out_walls"]
            chk["ambig"] += aux["ambiguous"]
            chk["n_floor"] += aux["n_floor"]
            chk["n_roof"] += aux["n_roof"]
            chk["ww_dis"] += aux["win_wall_disagree"]
            chk["floor_viol"] += aux["floor_dir_viol"]
            chk["roof_viol"] += aux["roof_dir_viol"]
            chk["zone_rot"] += aux["zone_rot"]
            if aux["north"] != 0:
                chk["north_nonzero"].append(stem)
            for k in bld["u_src"].split(";"):
                if not k.endswith(":surfaces") and not k.endswith(":ground_surfaces"):
                    chk["src_fallback"][k] = chk["src_fallback"].get(k, 0) + 1
            if (i + 1) % 100 == 0:
                say("%s %d/%d buildings, %.0f s" % (d, i + 1, len(wrows), time.time() - t0))
        results[d] = (fl_rows, b_rows, chk, per_b, wrows, wcsv)
        pf = os.path.join(OUT, "flats_%s.csv" % d)
        pb = os.path.join(OUT, "buildings_%s.csv" % d)
        with io.open(pf, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(FLAT_COLS)
            for r in fl_rows:
                w.writerow([fmt(r[c]) for c in FLAT_COLS])
        with io.open(pb, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(BLD_COLS)
            for r in b_rows:
                w.writerow([fmt(r[c]) for c in BLD_COLS])
        outfiles += [pf, pb]

    # ------------------------------------------------------------------ checks
    verdicts = []

    def verdict(name, ok, detail):
        verdicts.append((name, ok))
        say("CHECK %s: %s | %s" % (name, "PASS" if ok else "FAIL", detail))

    for d, (fl_rows, b_rows, chk, per_b, wrows, wcsv) in results.items():
        verdict("rows %s" % d, chk["flat_rows"] == chk["zone_rows_expected"] and chk["zone_name_bad"] == 0 and len(b_rows) == len(wrows),
                "flat rows %d vs zone map usable rows %d; buildings %d vs usable %d; zone-name mismatches %d"
                % (chk["flat_rows"], chk["zone_rows_expected"], len(b_rows), len(wrows), chk["zone_name_bad"]))
        verdict("floor area vs zone map %s" % d, not chk["area_bad"], "%d flats differ by >0.001 m2 from the zone map" % len(chk["area_bad"]))
        verdict("window area vs wall table %s" % d, not chk["win_bad"], "%d of %d buildings differ by >0.01 m2 %s" % (len(chk["win_bad"]), len(b_rows), chk["win_bad"][:3]))
        verdict("outdoor wall count and eligible area %s" % d, not chk["cnt_bad"] and not chk["wall_bad"],
                "compared: outdoor wall surface count vs eligible+too_small+triangle+other counts (%d mismatches); area of eligible-class walls vs eligible_wall_area_m2 within 0.01 and bin sum vs total outdoor wall area (%d mismatches)"
                % (len(chk["cnt_bad"]), len(chk["wall_bad"])))
        verdict("window U vs windows.csv %s" % d, not chk["u_bad"], "%d of %d buildings differ by >0.01" % (len(chk["u_bad"]), len(b_rows)))
        verdict("window SHGC vs windows.csv %s" % d, not chk["shgc_bad"], "%d of %d buildings differ by >0.01" % (len(chk["shgc_bad"]), len(b_rows)))
        tw, tf, tr = chk["n_wall"], chk["n_floor"], chk["n_roof"]
        verdict("outward normals (right-hand rule, geometric outward) %s" % d, chk["normal_viol"] == 0 and chk["floor_viol"] == 0 and chk["roof_viol"] == 0,
                "outdoor walls whose vertex-order normal points into the zone floor polygon: %d of %d (ambiguous %d); floors with upward normal: %d of %d; roofs with downward normal: %d of %d"
                % (chk["normal_viol"], tw, chk["ambig"], chk["floor_viol"], tf, chk["roof_viol"], tr))
        share = [chk["normal_viol"] / max(tw, 1), chk["floor_viol"] / max(tf, 1), chk["roof_viol"] / max(tr, 1)]
        out_share = [(tw - chk["normal_viol"] - chk["ambig"]) / max(tw, 1), (tf - chk["floor_viol"]) / max(tf, 1), (tr - chk["roof_viol"]) / max(tr, 1)]
        if WIN2:
            # fixed base: the vertex order must now be uniformly OUTWARD (walls: inward share <= 1 %, floors and roofs: none inverted)
            verdict("vertex order uniformly outward (walls inward share <= 1%%, floors and roofs inverted none) %s" % d,
                    share[0] <= 0.01 and share[1] == 0 and share[2] == 0,
                    "inward share: walls %.4f (%d walls, ambiguous %d), floors %.4f, roofs %.4f; EnergyPlus-read orientation = vertex-order normal = geometric outward on the fixed base (no rotation of bins)"
                    % (share[0], chk["normal_viol"], chk["ambig"], share[1], share[2]))
        else:
          verdict("vertex order uniformly inverted (outward share <= 0.1%% for walls, floors, roofs) %s" % d,
                all(x <= 0.001 for x in out_share) and all(x >= 0.99 for x in share),
                "inverted share: walls %.4f (ambiguous %d), floors %.4f, roofs %.4f; outward share: walls %.4f, floors %.4f, roofs %.4f; EnergyPlus-read orientation = vertex-order normal, geometric outward = rotate bins by 180 deg (N<->S, E<->W)"
                % (share[0], chk["ambig"], share[1], share[2], out_share[0], out_share[1], out_share[2]))
        verdict("window normal agrees with its wall normal %s" % d, chk["ww_dis"] == 0, "%d windows disagree with their base wall" % chk["ww_dis"])
        say("INFO %s: buildings with non-zero North axis: %d; zones with non-zero origin / relative north: %d; age_band mismatches vs prepared: %d; U fallbacks (not from surfaces): %s"
            % (d, len(chk["north_nonzero"]), chk["zone_rot"], len(chk["age_mismatch"]), chk["src_fallback"]))
        top = sorted(per_b, key=lambda x: -sum(r["win_" + b + "_m2"] for r in x[1] for b in BINS))[:3]
        for stem, rows, bld, aux in top:
            say("ORIENT %s %s window m2 per bin: %s (total %.2f), wall m2 per bin: %s"
                % (d, stem, {b: round(sum(r["win_" + b + "_m2"] for r in rows), 2) for b in BINS},
                   aux["win_area"], {b: round(sum(r["wall_" + b + "_m2"] for r in rows), 2) for b in BINS}))
        # north-axis demonstration (in memory): first top building, North axis 0 vs planted 90
        stem = top[0][0]
        text = M.read_text(M.idf_path(d, stem))
        r0, _, a0 = extract(text, d, stem)
        r90, _, a90 = extract(text, d, stem, north_override=90.0)
        s0 = {b: round(sum(r["win_" + b + "_m2"] for r in r0), 2) for b in BINS}
        s90 = {b: round(sum(r["win_" + b + "_m2"] for r in r90), 2) for b in BINS}
        rotated_ok = all(abs(s0[b] - s90[BINS[(BINS.index(b) + 1) % 4]]) < 0.02 for b in BINS) and s0 != s90
        say("NORTHAXIS %s %s: %s non-zero in IDFs; planted in memory 0 vs 90 deg: %s vs %s (each bin moves one step clockwise: %s)"
            % (d, stem, "none" if not chk["north_nonzero"] else "some", s0, s90, rotated_ok))
        verdict("north axis applied %s" % d, rotated_ok, "bins rotate one step when North axis is planted at 90")

    # planted fault: swap one building's window U in memory, run the U check, must fail on exactly that building
    d = "IT-BOL-GALVANI2" if _BOL5 else "ES-MAD-BERRUGUETE"   # step 9p: the planted window-U fault runs on the district that is built
    fl_rows, b_rows, chk, per_b, wrows, wcsv = results[d]
    victim = per_b[5][0]
    bad = []
    for stem, rows, bld, aux in per_b[:40]:
        text = M.read_text(M.idf_path(d, stem))
        if stem == victim:
            i = text.index("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM")
            j = text.index("!- UFactor", i)
            ls = text.rfind(chr(10), 0, j) + 1
            text = text[:ls] + "    9.9,                      " + text[j:]
        _, _, a = extract(text, d, stem)
        if abs(a["u_win"] - float(wcsv[stem]["u"])) > 0.01:
            bad.append(stem)
    verdict("planted window U fault", bad == [victim], "swapped U to 9.9 on %s; U check failed on %s (40 buildings checked)" % (victim, bad))

    # ranges
    for d, (fl_rows, b_rows, chk, per_b, wrows, wcsv) in results.items():
        miss = 0
        for r in fl_rows:
            miss += sum(1 for c in FLAT_COLS if r[c] is None or r[c] == "" or (isinstance(r[c], float) and r[c] != r[c]))
        for r in b_rows:
            miss += sum(1 for c in BLD_COLS if r[c] is None or r[c] == "" or (isinstance(r[c], float) and r[c] != r[c]))
        verdict("no missing values %s" % d, miss == 0, "%d missing cells over %d flat rows and %d building rows" % (miss, len(fl_rows), len(b_rows)))
        for nm, rows, cols in (("flats", fl_rows, FLAT_COLS), ("buildings", b_rows, BLD_COLS)):
            for c in cols:
                vals = [r[c] for r in rows]
                if isinstance(vals[0], (int, float)):
                    say("RANGE %s %s %s min %.4g median %.4g max %.4g" % (d, nm, c, min(vals), statistics.median(vals), max(vals)))
                elif c in ("class", "age_band", "age_band_prepared"):
                    cnt = {}
                    for v in vals:
                        cnt[v] = cnt.get(v, 0) + 1
                    say("RANGE %s %s %s values %s" % (d, nm, c, dict(sorted(cnt.items()))))
        ex = []
        for r in b_rows[:3]:
            pr = [p for p in M.read_prepared(d) if p["stem"] == r["stem"]][0]
            ex.append((pr["archetype_id"], r["age_band"]))
        say("AGEPARSE %s examples (archetype_id -> age_band): %s" % (d, ex))
    say("TIME %.0f s" % (time.time() - t0))
    for p in outfiles:
        say("MD5 %s %s %d bytes" % (md5(p), os.path.basename(p), os.path.getsize(p)))
    say("ALL CHECKS PASS" if all(ok for _, ok in verdicts) else "SOME CHECK FAILED: %s" % [n for n, ok in verdicts if not ok])
    with io.open(os.path.join(OUT, "checks_log.txt"), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
