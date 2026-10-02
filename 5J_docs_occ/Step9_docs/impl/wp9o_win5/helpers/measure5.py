# -*- coding: utf-8 -*-
"""Step 9o item 1: re-measure OpenUBEM `_win_2026-10-05` (Madrid only) against `_win_2026-10-03`, per stem, with our own parser
(tools/5thJ_modelA_idf.py: objects, surface_of, area3). Iterates the stems of md5_2026-10-05.txt (NOT fleet.lst: the 10-05 fleet.lst
lists only the 171 changed stems). Opens only the two Madrid folders by full name. No UK path.
Run: py measure5.py   -> writes ../win5_check_results.json and prints a plant test
"""
import os, sys, io, csv, json, hashlib, collections
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
OLD = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-03"
NEW = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-05"
SURF_FIELDS = ["name", "type", "cons", "zone", "space", "bc", "bcobj", "sun", "wind", "vf", "nverts"]


def md5_file(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def profile_text(text, stem):
    objs = M.objects(text)
    p = {"zones": [], "cond": set(), "surf": {}, "fen": {}, "cons": set(), "objs": collections.Counter()}
    for o in objs:
        kw, f = o["kw"], o["fields"]
        p["objs"][(kw, tuple(f))] += 1
        if kw == "ZONE":
            p["zones"].append(f[0])
        elif kw == "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM":
            p["cond"].add(f[0])
        elif kw == "CONSTRUCTION":
            p["cons"].add(f[0])
        elif kw == "BUILDINGSURFACE:DETAILED":
            s = M.surface_of(o)
            p["surf"][s["name"]] = {"type": s["type"], "cons": s["cons"], "zone": s["zone"], "bc": s["bc"], "bcobj": s["bcobj"],
                                    "area": M.area3(s["verts"]), "fields": tuple(f)}
        elif kw.startswith("FENESTRATIONSURFACE"):
            c = f[9:]
            v = [(float(c[i]), float(c[i + 1]), float(c[i + 2])) for i in range(0, len(c) - 2, 3)]
            p["fen"][f[0]] = {"cons": f[2], "host": f[3], "area": M.area3(v) * float(f[7] or 1), "fields": tuple(f)}
    rows, reason, nz, nc = M.zone_map(text, stem, objs)
    p["flats"] = [r["zone"] for r in rows]
    p["floors"] = sorted(set(r["floor_k"] for r in rows))
    p["zone_reason"] = reason
    return p


def compare(a, b):
    """a = old profile, b = new profile. Returns dict of differences (own counters)."""
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
    d["surf_deleted_maxarea"] = max([a["surf"][n]["area"] for n in dn] or [0.0])
    wd = set(a["fen"]) - set(b["fen"])
    wa = set(b["fen"]) - set(a["fen"])
    d["win_deleted"], d["win_added"] = len(wd), len(wa)
    d["win_deleted_area"] = sum(a["fen"][n]["area"] for n in wd)
    d["win_deleted_host_kept"] = sum(1 for n in wd if a["fen"][n]["host"] in b["surf"])
    mod = [n for n in a["surf"] if n in b["surf"] and a["surf"][n]["fields"] != b["surf"][n]["fields"]]
    d["surf_modified"] = len(mod)
    cols = collections.Counter()
    for n in mod:
        fa, fb = a["surf"][n]["fields"], b["surf"][n]["fields"]
        if len(fa) != len(fb):
            cols["nfields"] += 1
        for i in range(min(len(fa), len(fb))):
            if fa[i] != fb[i]:
                cols[SURF_FIELDS[i] if i < len(SURF_FIELDS) else "coord"] += 1
    d["surf_modified_cols"] = dict(cols)
    modw = [n for n in a["fen"] if n in b["fen"] and a["fen"][n]["fields"] != b["fen"][n]["fields"]]
    d["win_modified"] = len(modw)
    d["kept_zone_or_cons_changed"] = sum(1 for n in a["surf"] if n in b["surf"] and (a["surf"][n]["zone"] != b["surf"][n]["zone"] or a["surf"][n]["cons"] != b["surf"][n]["cons"] or a["surf"][n]["type"] != b["surf"][n]["type"]))
    rem = a["objs"] - b["objs"]
    add = b["objs"] - a["objs"]
    rk, ak = collections.Counter(), collections.Counter()
    for (kw, f), n in rem.items():
        rk[kw] += n
    for (kw, f), n in add.items():
        ak[kw] += n
    d["obj_removed_by_kw"] = dict(rk)
    d["obj_added_by_kw"] = dict(ak)
    d["any_diff"] = int(bool(rem or add))
    return d


def work(stem):
    po, pn = OLD + "/idfs/%s.idf" % stem, NEW + "/idfs/%s.idf" % stem
    mo, mn = md5_file(po), md5_file(pn)
    to, tn = M.read_text(po), M.read_text(pn)
    a, b = profile_text(to, stem), profile_text(tn, stem)
    d = compare(a, b)
    d["stem"], d["md5_old"], d["md5_new"] = stem, mo, mn
    d["bytes_equal"] = int(mo == mn)
    d["zones_removed"] = sorted(set(a["zones"]) - set(b["zones"]))[:6]
    d["zones_added"] = sorted(set(b["zones"]) - set(a["zones"]))[:6]
    d["flats_list_old"] = a["flats"]
    d["flats_list_new"] = b["flats"]
    return d


def plant_test(stem):
    """Seen failing: copy of one 10-03 IDF with one surface (and one with one window, one with a renamed zone) must be flagged."""
    to = M.read_text(OLD + "/idfs/%s.idf" % stem)
    objs = M.objects(to)
    a = profile_text(to, stem)
    res = {}
    clean = compare(a, profile_text(to, stem))
    res["unplanted_any_diff"] = clean["any_diff"]
    victim = next(o for o in objs if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "wall")
    t2 = to[:victim["start"]] + to[victim["end"]:]
    d2 = compare(a, profile_text(t2, stem))
    res["planted_surface"] = {"victim": victim["fields"][0], "any_diff": d2["any_diff"], "surf_deleted": d2["surf_deleted"],
                              "surf_old": d2["surf_old"], "surf_new": d2["surf_new"], "area_changed": int(abs(d2["area_old"] - d2["area_new"]) > 1e-9)}
    wv = next((o for o in objs if o["kw"].startswith("FENESTRATIONSURFACE")), None)
    if wv is not None:
        t3 = to[:wv["start"]] + to[wv["end"]:]
        d3 = compare(a, profile_text(t3, stem))
        res["planted_window"] = {"victim": wv["fields"][0], "any_diff": d3["any_diff"], "win_deleted": d3["win_deleted"],
                                 "warea_changed": int(abs(d3["warea_old"] - d3["warea_new"]) > 1e-9)}
    zo = next(o for o in objs if o["kw"] == "ZONE")
    t4 = to.replace(zo["fields"][0], zo["fields"][0] + "X")
    d4 = compare(a, profile_text(t4, stem))
    res["planted_zone_rename"] = {"zones_same": d4["zones_same"], "any_diff": d4["any_diff"]}
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
    with io.open(os.path.join(OUTD, "win5_check_results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh)
    print("done", len(res))
    print("PLANT", json.dumps(plant_test(stems[0]), indent=1))
