# -*- coding: utf-8 -*-
"""5J Step 9h (and 9j): own counter + old-vs-new comparison for OpenUBEM's fixed base `_win_2026-10-02` (Madrid, Bologna only).
Task: Step9_docs/impl/2026-10-01_wp9h_rebase_fixed_TASK.md.  One process, desktop, no EnergyPlus.
UK licence: only the two districts below can be opened (refused otherwise); no wildcard, no folder-wide search.

Run: py tools/5thJ_modelA_win2_check.py [--old-sample N]      writes Step9_docs/impl/wp9h_win2/*   (default: new = win_2026-10-02, old = win_2026-10-01)
Step 9j (additive): py tools/5thJ_modelA_win2_check.py --new win_2026-10-03   (old = win_2026-10-02) writes Step9_docs/impl/wp9j_win3/win3_check_*;
in that mode the old base is counted on EVERY building and must reproduce 9h's 162 / 209 (probe) and 237 / 327 (winding).
Parsing reused from 5thJ_modelA_idf.py (objects, surface_of, newell, area3, inside copy below).
"""
import argparse
import csv
import hashlib
import importlib
import io
import math
import os
import sys

sys.dont_write_bytecode = True
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
M = importlib.import_module("5thJ_modelA_idf")
EU11 = M.EU11
DISTRICTS = ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2")
OLD, NEW = "win_2026-10-01", "win_2026-10-02"
OUT = os.path.normpath(os.path.join(_HERE, "..", "Step9_docs", "impl", "wp9h_win2"))
OUT3 = os.path.normpath(os.path.join(_HERE, "..", "Step9_docs", "impl", "wp9j_win3"))
FILEPFX = "win2"
# 9j claims (task doc 2026-10-01_wp9j_rebase_win3_TASK.md): only inward counts and totals were claimed; None = no claim made
CLAIM3 = {"ES-MAD-BERRUGUETE": dict(inward=9, outward=None, unclear=None, no_outdoor=11, pairs=25897, opposite=25897, idfs=1172, n_outdoor=36183),
          "IT-BOL-GALVANI2": dict(inward=4, outward=None, unclear=None, no_outdoor=71, pairs=29382, opposite=29382, idfs=1179, n_outdoor=55733)}
REPRO_OLD = {"ES-MAD-BERRUGUETE": dict(wall_out_in=162, edge_in=237), "IT-BOL-GALVANI2": dict(wall_out_in=209, edge_in=327)}   # 9h numbers
CLAIM = {"ES-MAD-BERRUGUETE": dict(inward=0, outward=35720, unclear=463, no_outdoor=11, pairs=25897, opposite=25897, idfs=1172),
         "IT-BOL-GALVANI2": dict(inward=0, outward=55242, unclear=491, no_outdoor=71, pairs=29382, opposite=29382, idfs=1179)}


def folder(d, vint):
    if d not in DISTRICTS:
        raise RuntimeError("district %r not allowed" % d)
    return "%s/%s_%s" % (EU11, d, vint)


def md5file(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i][0], poly[i][1]
        x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def newell(v):
    """Newell normal on coordinates relative to the first vertex (UTM values near 4.4e6 would lose precision)."""
    o = v[0]
    w = [(a[0] - o[0], a[1] - o[1], a[2] - o[2]) for a in v]
    return M.newell(w)


def area3(v):
    sx, sy, sz = newell(v)
    return 0.5 * math.sqrt(sx * sx + sy * sy + sz * sz)


def unit(n):
    l = math.sqrt(sum(c * c for c in n))
    return tuple(c / l for c in n) if l > 0 else (0.0, 0.0, 0.0)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def fen_parse(o):
    f = o["fields"]
    c = f[9:]
    v = [(float(c[i]), float(c[i + 1]), float(c[i + 2])) for i in range(0, len(c) - 2, 3)]
    return {"name": f[0], "head": f[:8], "cons": f[2], "host": f[3], "mult": float(f[7] or 1), "verts": v}


def _k(v):
    return (round(v[0], 2), round(v[1], 2), round(v[2], 2))


def edge_class(s, fedges, fup):
    """Winding test, exact: the wall's bottom edge (two lowest vertices, consecutive in the ring) against the zone's floor edges.
    The floor points down, so a wall pointing OUT shares the edge in the OPPOSITE direction (closed-surface rule);
    the same direction means the wall points in. 'none' = no floor edge matches (partial edge, split edge)."""
    v = s["verts"]
    zmin = min(a[2] for a in v)
    fe = fedges.get(s["zone"], set())
    for i in range(len(v)):
        a, b = v[i], v[(i + 1) % len(v)]
        if abs(a[2] - zmin) < 1e-6 and abs(b[2] - zmin) < 1e-6:
            same, opp = ("out", "in") if fup.get(s["zone"]) else ("in", "out")   # floor pointing up flips the rule
            if (_k(a), _k(b)) in fe:
                return same
            if (_k(b), _k(a)) in fe:
                return opp
    return "none"


def analyze(text):
    """Geometry counters of one IDF (own code: Newell normal + point-in-floor test)."""
    objs = M.objects(text)
    surf = {}
    floors = {}
    fedges = {}
    fup = {}
    zones = []
    for o in objs:
        if o["kw"] == "ZONE":
            zones.append(o["fields"][0])
        elif o["kw"] == "BUILDINGSURFACE:DETAILED":
            s = M.surface_of(o)
            s["fields"] = o["fields"]
            surf[s["name"]] = s
            if s["type"] == "floor":
                floors.setdefault(s["zone"], []).append(s["verts"])
                vv = s["verts"]
                fup[s["zone"]] = fup.get(s["zone"], 0) or (newell(vv)[2] > 0)
                for i in range(len(vv)):
                    fedges.setdefault(s["zone"], set()).add((_k(vv[i]), _k(vv[(i + 1) % len(vv)])))
    fens = [fen_parse(o) for o in objs if o["kw"].startswith("FENESTRATIONSURFACE")]
    c = dict(wall_out_in=0, wall_out_out=0, wall_out_unclear=0, n_outdoor_walls=0, floor_down=0, floor_up=0,
             ceil_up=0, ceil_down=0, roof_up=0, roof_down=0, win_total=0, win_diff=0, win_nohost=0,
             pairs=0, pairs_opposite=0, pairs_strict=0, pairs_unmatched=0,
             edge_in=0, edge_out=0, edge_none=0)
    for _p in ('in', 'out', 'unc'):
        for _e in ('in', 'out', 'none'):
            c['x_%s_%s' % (_p, _e)] = 0
    for s in surf.values():
        n = newell(s["verts"])
        t = s["type"]
        if t == "wall" and s["bc"] == "outdoors":
            c["n_outdoor_walls"] += 1
            sx, sy = n[0], n[1]
            nn = math.hypot(sx, sy)
            polys = floors.get(s["zone"], [])
            pcls = "unc"
            ecls = edge_class(s, fedges, fup)
            c["edge_" + ecls] += 1
            if nn > 0 and polys:
                wx = sum(v[0] for v in s["verts"]) / len(s["verts"])
                wy = sum(v[1] for v in s["verts"]) / len(s["verts"])
                p_in = any(inside((wx + 0.05 * sx / nn, wy + 0.05 * sy / nn), pl) for pl in polys)
                m_in = any(inside((wx - 0.05 * sx / nn, wy - 0.05 * sy / nn), pl) for pl in polys)
                if p_in and not m_in:
                    c["wall_out_in"] += 1            # normal points into the zone
                    pcls = "in"
                elif m_in and not p_in:
                    c["wall_out_out"] += 1           # normal points out of the zone
                    pcls = "out"
                else:
                    c["wall_out_unclear"] += 1
            else:
                c["wall_out_unclear"] += 1
            c["x_%s_%s" % (pcls, ecls)] += 1
        elif t == "floor":
            c["floor_down" if n[2] < 0 else "floor_up"] += 1
        elif t == "ceiling":
            c["ceil_up" if n[2] > 0 else "ceil_down"] += 1
        elif t == "roof":
            c["roof_up" if n[2] > 0 else "roof_down"] += 1
    for f in fens:
        c["win_total"] += 1
        h = surf.get(f["host"])
        if h is None:
            c["win_nohost"] += 1
            continue
        if dot(unit(newell(f["verts"])), unit(newell(h["verts"]))) <= 0:
            c["win_diff"] += 1
    seen = set()
    for s in surf.values():
        if s["bc"] == "surface" and s["bcobj"]:
            key = tuple(sorted((s["name"], s["bcobj"])))
            if key in seen:
                continue
            seen.add(key)
            o2 = surf.get(s["bcobj"])
            if o2 is None:
                c["pairs_unmatched"] += 1
                continue
            c["pairs"] += 1
            d = dot(unit(newell(s["verts"])), unit(newell(o2["verts"])))
            if d < 0:
                c["pairs_opposite"] += 1
            if d < -0.999:
                c["pairs_strict"] += 1
    c["n_zones"] = len(zones)
    return c


def strip_surfaces(text):
    objs = M.objects(text)
    spans = [(o["start"], o["end"]) for o in objs if o["kw"] in ("BUILDINGSURFACE:DETAILED",) or o["kw"].startswith("FENESTRATIONSURFACE")]
    return M.remove_objects(text, spans)


def rnd(v):
    return tuple(round(x, 6) for x in v)


def compare(told, tnew, tol=1e-6):
    """Everything except vertex order. Returns (list of problems, counters)."""
    probs = []
    cnt = dict(surf_same_seq=0, surf_reversed=0, surf_other_order=0, surf_set_diff=0, cons_diff=0, field_diff=0, changed_S=0, changed_W=0)
    oo, on = M.objects(told), M.objects(tnew)
    zo = [o["fields"][0] for o in oo if o["kw"] == "ZONE"]
    zn = [o["fields"][0] for o in on if o["kw"] == "ZONE"]
    if zo != zn:
        probs.append("zone names/count differ (%d vs %d)" % (len(zo), len(zn)))
    so = {}
    sn = {}
    for o in oo:
        if o["kw"] == "BUILDINGSURFACE:DETAILED":
            so[o["fields"][0]] = ("S", o["fields"][:11], M.surface_of(o)["verts"])
        elif o["kw"].startswith("FENESTRATIONSURFACE"):
            f = fen_parse(o)
            so[f["name"]] = ("W", f["head"], f["verts"])
    for o in on:
        if o["kw"] == "BUILDINGSURFACE:DETAILED":
            sn[o["fields"][0]] = ("S", o["fields"][:11], M.surface_of(o)["verts"])
        elif o["kw"].startswith("FENESTRATIONSURFACE"):
            f = fen_parse(o)
            sn[f["name"]] = ("W", f["head"], f["verts"])
    if set(so) != set(sn) or len(so) != len(sn):
        probs.append("surface names/count differ (%d vs %d)" % (len(so), len(sn)))
    ao = an = wo = wn = 0.0
    nwo = nwn = 0
    for name in so:
        if name not in sn:
            continue
        ko, ho, vo = so[name]
        kn, hn, vn = sn[name]
        if ko == "W":
            nwo += 1
            nwn += 1
        fo = [x for i, x in enumerate(ho)] if ko == "S" else ho
        # BUILDINGSURFACE head: name,type,cons,zone,space,bc,bcobj,sun,wind,vf,nverts(field 10 = vertex count text)
        if ko == "S":
            if ho[:10] != hn[:10]:
                cnt["field_diff"] += 1
                probs.append("fields differ on %s" % name)
            if ho[2] != hn[2]:
                cnt["cons_diff"] += 1
        else:
            if ho != hn:
                cnt["field_diff"] += 1
                probs.append("window fields differ on %s" % name)
            if ho[2] != hn[2]:
                cnt["cons_diff"] += 1
        a1, a2 = area3(vo), area3(vn)
        if abs(a1 - a2) > tol * max(a1, 1e-12):
            probs.append("area differs on %s (%.9f vs %.9f)" % (name, a1, a2))
        mult = 1.0
        if ko == "W":
            mult = float(ho[7] or 1)
            wo += a1 * mult
            wn += a2 * mult
        ao += a1
        an += a2
        ro, rn = [rnd(v) for v in vo], [rnd(v) for v in vn]
        if ro != rn:
            cnt["changed_" + ko] = cnt.get("changed_" + ko, 0) + 1
        if ro == rn:
            cnt["surf_same_seq"] += 1
        elif sorted(ro) != sorted(rn):
            cnt["surf_set_diff"] += 1
            probs.append("vertex set differs on %s" % name)
        else:
            # reversed up to rotation?
            r = list(reversed(rn))
            rot = any(r[i:] + r[:i] == ro for i in range(len(r)))
            cnt["surf_reversed" if rot else "surf_other_order"] += 1
    if abs(ao - an) > tol * max(ao, 1e-12):
        probs.append("building area sum differs (%.9f vs %.9f)" % (ao, an))
    if abs(wo - wn) > tol * max(wo, 1e-12) and (wo or wn):
        probs.append("window area sum differs (%.9f vs %.9f)" % (wo, wn))
    # constructions and everything that is not a surface: byte-equal text outside surface objects
    co = sorted(o["fields"][0] for o in oo if o["kw"] == "CONSTRUCTION")
    cn = sorted(o["fields"][0] for o in on if o["kw"] == "CONSTRUCTION")
    if co != cn:
        probs.append("construction names differ")
    if strip_surfaces(told) != strip_surfaces(tnew):
        probs.append("text outside surface objects differs")
    cnt.update(n_surf=len(so), n_win=nwo, area=ao, warea=wo)
    return probs, cnt


def edit_vertices(text, obj, how):
    """In-memory planted edits of one surface object: 'reverse' = vertex triples in reverse order (terminators stay in place),
    'shift' = first vertex x + 0.1 m."""
    seg = text[obj["start"]:obj["end"]]
    lines = seg.splitlines(True)
    vidx = [i for i, ln in enumerate(lines) if "!- Vertex" in ln]
    vals, tails = [], []
    for i in vidx:
        ln = lines[i]
        k = min(x for x in (ln.find(","), ln.find(";")) if x >= 0)
        vals.append(ln[:k])
        tails.append(ln[k:])
    if how == "reverse":
        tri = [vals[i:i + 3] for i in range(0, len(vals), 3)]
        vals = [x for t in reversed(tri) for x in t]
    else:
        vals[0] = "    %.6f" % (float(vals[0]) + 0.1)
    for j, i in enumerate(vidx):
        lines[i] = vals[j] + tails[j]
    return text[:obj["start"]] + "".join(lines) + text[obj["end"]:]


def read_rows(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-sample", type=int, default=20)
    ap.add_argument("--new", default="win_2026-10-02", choices=["win_2026-10-02", "win_2026-10-03"])
    args = ap.parse_args()
    global OLD, NEW, OUT, CLAIM, FILEPFX
    MODE3 = args.new == "win_2026-10-03"
    if MODE3:
        OLD, NEW, OUT, CLAIM, FILEPFX = "win_2026-10-02", "win_2026-10-03", OUT3, CLAIM3, "win3"
    os.makedirs(OUT, exist_ok=True)
    log = []

    def say(s):
        print(s)
        sys.stdout.flush()
        log.append(s)

    verdicts = []

    def verdict(name, ok, msg):
        verdicts.append((name, ok))
        say("CHECK %s: %s | %s" % (name, "PASS" if ok else "FAIL", msg))

    stems = {}
    for d in DISTRICTS:
        pn, po = folder(d, NEW) + "/prepared_buildings.csv", folder(d, OLD) + "/prepared_buildings.csv"
        mn, mo = md5file(pn), md5file(po)
        say("MD5 prepared_buildings.csv %s new %s old %s" % (d, mn, mo))
        verdict("prepared_buildings.csv equal %s" % d, mn == mo, "md5 new %s old %s" % (mn, mo))
        stems[d] = [r["stem"] for r in read_rows(pn)]
        for fn in ("windows.csv",):
            a, b = md5file(folder(d, NEW) + "/" + fn), md5file(folder(d, OLD) + "/" + fn)
            verdict("%s equal %s" % (fn, d), a == b, "md5 new %s old %s" % (a, b))
        ids = sorted(os.listdir(folder(d, NEW) + "/idfs"))
        verdict("idf count %s" % d, len(ids) == CLAIM[d]["idfs"] == len(stems[d]) and set(i[:-4] for i in ids) == set(stems[d]),
                "idfs/ holds %d files, prepared_buildings %d rows, claim %d" % (len(ids), len(stems[d]), CLAIM[d]["idfs"]))
        # weather (single folder) and fleet.lst
        wn_ = sorted(os.listdir(folder(d, NEW) + "/weather"))
        wo_ = sorted(os.listdir(folder(d, OLD) + "/weather"))
        eq = wn_ == wo_ and all(md5file(folder(d, NEW) + "/weather/" + f) == md5file(folder(d, OLD) + "/weather/" + f) for f in wn_)
        verdict("weather files byte-equal %s" % d, eq, "files read (both bases): %s" % wn_)
        oc = md5file(folder(d, NEW) + "/orientation.csv"), md5file(folder(d, OLD) + "/orientation.csv")
        say("INFO orientation.csv md5 %s new %s old %s (equal: %s; this file describes the fix, a change is expected)" % (d, oc[0], oc[1], oc[0] == oc[1]))
        ml = md5file(folder(d, NEW) + "/fleet.lst"), md5file(folder(d, OLD) + "/fleet.lst")
        say("INFO fleet.lst md5 %s new %s old %s (equal: %s)" % (d, ml[0], ml[1], ml[0] == ml[1]))

    # schedules: one stem folder at a time (no recursion)
    for d in DISTRICTS:
        names, bad, nfiles, missing = {}, [], 0, []
        for stem in stems[d]:
            fn_, fo_ = folder(d, NEW) + "/schedules/" + stem, folder(d, OLD) + "/schedules/" + stem
            if not (os.path.isdir(fn_) and os.path.isdir(fo_)):
                missing.append(stem)
                continue
            ln, lo = sorted(os.listdir(fn_)), sorted(os.listdir(fo_))
            if ln != lo:
                bad.append((stem, "listing"))
                continue
            for f in ln:
                nfiles += 1
                names[f] = names.get(f, 0) + 1
                if md5file(fn_ + "/" + f) != md5file(fo_ + "/" + f):
                    bad.append((stem, f))
        verdict("schedules byte-equal %s" % d, not bad and not missing,
                "%d stem folders compared, %d files (file names read: %s), different %d, folder missing in one base %d %s"
                % (len(stems[d]) - len(missing), nfiles, dict(sorted(names.items())), len(bad), len(missing), (bad[:3], missing[:3])))

    # own counter on new base (every building), old-vs-new comparison (every building)
    tot_new = {}
    cmp_tot = {}
    rows_out = []
    orient = {}
    old_tot = {d: {} for d in DISTRICTS}
    for d in DISTRICTS:
        orient[d] = read_rows(folder(d, NEW) + "/orientation.csv")
    for d in DISTRICTS:
        tn = {}
        ct = {}
        nprob = 0
        probs_first = []
        no_outdoor = 0
        for i, stem in enumerate(stems[d]):
            tnew = M.read_text(folder(d, NEW) + "/idfs/" + stem + ".idf")
            told = M.read_text(folder(d, OLD) + "/idfs/" + stem + ".idf")
            c = analyze(tnew)
            pr, cc = compare(told, tnew)
            if MODE3:
                co_ = analyze(told)
                for k in ("wall_out_in", "edge_in", "wall_out_out", "wall_out_unclear", "n_outdoor_walls"):
                    old_tot[d][k] = old_tot[d].get(k, 0) + co_[k]
            if c["n_outdoor_walls"] == 0:
                no_outdoor += 1
            for k, v in c.items():
                tn[k] = tn.get(k, 0) + v
            for k, v in cc.items():
                ct[k] = ct.get(k, 0) + v
            if pr:
                nprob += 1
                if len(probs_first) < 5:
                    probs_first.append((stem, pr[:2]))
            rows_out.append([d, stem] + [c[k] for k in sorted(c)] + [len(pr)] + ([cc["changed_S"], cc["changed_W"], co_["wall_out_in"], co_["edge_in"]] if MODE3 else []))
            if (i + 1) % 300 == 0:
                say("%s %d/%d buildings" % (d, i + 1, len(stems[d])))
        tot_new[d] = tn
        cmp_tot[d] = (ct, nprob, probs_first)
        cl = CLAIM[d]
        say("NEWBASE %s own counts: %s" % (d, {k: tn[k] for k in sorted(tn)}))
        verdict("claim outdoor walls inward %s" % d, tn["wall_out_in"] == cl["inward"], "own %d, claim %d" % (tn["wall_out_in"], cl["inward"]))
        if cl["outward"] is not None:
            verdict("claim outdoor walls outward %s" % d, tn["wall_out_out"] == cl["outward"], "own %d, claim %d" % (tn["wall_out_out"], cl["outward"]))
            verdict("claim outdoor walls unclear %s" % d, tn["wall_out_unclear"] == cl["unclear"], "own %d, claim %d" % (tn["wall_out_unclear"], cl["unclear"]))
        else:
            say("INFO %s no claim for outward / unclear counts; own: outward %d unclear %d" % (d, tn["wall_out_out"], tn["wall_out_unclear"]))
        if MODE3:
            verdict("claim total outdoor walls %s" % d, tn["n_outdoor_walls"] == cl["n_outdoor"], "own %d, claim %d" % (tn["n_outdoor_walls"], cl["n_outdoor"]))
            ot = old_tot[d]
            rp = REPRO_OLD[d]
            say("OLDBASE-FULL %s (every building of %s): outdoor walls %d, probe inward %d outward %d unclear %d, winding inward %d" % (d, OLD, ot["n_outdoor_walls"], ot["wall_out_in"], ot["wall_out_out"], ot["wall_out_unclear"], ot["edge_in"]))
            verdict("reproduces 9h on the old base (probe inward, winding inward) %s" % d, ot["wall_out_in"] == rp["wall_out_in"] and ot["edge_in"] == rp["edge_in"],
                    "own probe %d (9h %d), own winding %d (9h %d)" % (ot["wall_out_in"], rp["wall_out_in"], ot["edge_in"], rp["edge_in"]))
        say("EDGETEST %s outdoor walls by exact winding test (bottom edge vs floor edge): in %d out %d none %d; cross-tab point-test x edge-test: %s"
            % (d, tn["edge_in"], tn["edge_out"], tn["edge_none"], {k[2:]: tn[k] for k in sorted(tn) if k.startswith("x_") and tn[k]}))
        verdict("claim homes without outdoor wall %s" % d, no_outdoor == cl["no_outdoor"], "own %d, claim %d" % (no_outdoor, cl["no_outdoor"]))
        verdict("claim interzone pairs and opposite %s" % d, tn["pairs"] == cl["pairs"] and tn["pairs_opposite"] == cl["opposite"],
                "own pairs %d opposite %d (strict < -0.999: %d, unmatched %d), claim %d / %d" % (tn["pairs"], tn["pairs_opposite"], tn["pairs_strict"], tn["pairs_unmatched"], cl["pairs"], cl["opposite"]))
        verdict("floors down, ceilings up, roofs up %s" % d, tn["floor_up"] == 0 and tn["ceil_down"] == 0 and tn["roof_down"] == 0,
                "floors down %d up %d; ceilings up %d down %d; roofs up %d down %d" % (tn["floor_down"], tn["floor_up"], tn["ceil_up"], tn["ceil_down"], tn["roof_up"], tn["roof_down"]))
        verdict("window normal = host wall normal %s" % d, tn["win_diff"] == 0 and tn["win_nohost"] == 0,
                "windows %d, normal differs from host wall %d, host not found %d" % (tn["win_total"], tn["win_diff"], tn["win_nohost"]))
        ow = sum(int(r["wall_inward"] or 0) for r in orient[d]), sum(int(r["wall_outward"] or 0) for r in orient[d]), sum(int(r["wall_unclear"] or 0) for r in orient[d])
        say("INFO orientation.csv column sums %s: wall_inward %d wall_outward %d wall_unclear %d; wall_reversed %d wall_kept %d windows_reversed %d windows_kept %d"
            % (d, ow[0], ow[1], ow[2], sum(int(r["wall_reversed"] or 0) for r in orient[d]), sum(int(r["wall_kept"] or 0) for r in orient[d]),
               sum(int(r["windows_reversed"] or 0) for r in orient[d]), sum(int(r["windows_kept"] or 0) for r in orient[d])))
        ct, nprob, pf = cmp_tot[d]
        verdict("nothing but vertex order changed %s" % d, nprob == 0,
                "buildings with any problem %d of %d %s; totals: %s" % (nprob, len(stems[d]), pf, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ct.items()}))

    # seen failing 1: same counter on the OLD base
    for d in ([] if MODE3 else DISTRICTS):
        sample = stems[d][::max(1, len(stems[d]) // args.old_sample)][:args.old_sample]
        agg = {}
        for stem in sample:
            c = analyze(M.read_text(folder(d, OLD) + "/idfs/" + stem + ".idf"))
            for k, v in c.items():
                agg[k] = agg.get(k, 0) + v
        say("OLDBASE %s sample of %d buildings (every %dth stem of prepared_buildings): outdoor walls %d inward %d outward %d unclear %d; floors up %d down %d; roofs up %d down %d; windows differing from host %d of %d; pairs opposite %d of %d"
            % (d, len(sample), max(1, len(stems[d]) // args.old_sample), agg["n_outdoor_walls"], agg["wall_out_in"], agg["wall_out_out"], agg["wall_out_unclear"], agg["floor_up"], agg["floor_down"],
               agg["roof_up"], agg["roof_down"], agg["win_diff"], agg["win_total"], agg["pairs_opposite"], agg["pairs"]))
        say("OLDBASE %s edge test: in %d out %d none %d" % (d, agg["edge_in"], agg["edge_out"], agg["edge_none"]))
        verdict("counter sees the old base failing %s" % d, agg["wall_out_in"] > 10 * max(agg["wall_out_out"], 1),
                "inward %d vs outward %d on the old base (the counter is able to report inward walls)" % (agg["wall_out_in"], agg["wall_out_out"]))

    # seen failing 2: planted faults in memory on one new-base building
    d = DISTRICTS[0]
    stem = "0275c53572b2ff9f"
    tnew = M.read_text(folder(d, NEW) + "/idfs/" + stem + ".idf")
    told = M.read_text(folder(d, OLD) + "/idfs/" + stem + ".idf")
    base_pr, _ = compare(told, tnew)
    base_c = analyze(tnew)
    # (a) flip one outdoor wall's vertex order: analyze must report one more inward wall
    objs = M.objects(tnew)
    victim = None
    for o in objs:
        if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "wall" and o["fields"][5].lower() == "outdoors":
            victim = o
            break
    flipped = edit_vertices(tnew, victim, "reverse")
    cf = analyze(flipped)
    say("PLANT flip one outdoor wall (%s): inward %d -> %d, outward %d -> %d" % (victim["fields"][0], base_c["wall_out_in"], cf["wall_out_in"], base_c["wall_out_out"], cf["wall_out_out"]))
    verdict("planted wall flip seen by counter", cf["wall_out_in"] == base_c["wall_out_in"] + 1 and cf["wall_out_out"] == base_c["wall_out_out"] - 1, "one wall moved from outward to inward")
    # (b) comparison must catch a changed vertex coordinate (area) and a renamed zone
    zname = [o["fields"][0] for o in objs if o["kw"] == "ZONE"][0]
    t_ren = tnew.replace(zname + ",", zname + "_x,", 1)
    pr_ren, _ = compare(told, t_ren)
    t_mv = edit_vertices(tnew, victim, "shift")
    pr_mv, _ = compare(told, t_mv)
    say("PLANT unplanted comparison problems: %d; renamed zone: %s; moved one vertex 0.1 m: %s" % (len(base_pr), pr_ren[:2], pr_mv[:2]))
    verdict("planted zone rename and moved vertex seen by comparison", len(base_pr) == 0 and len(pr_ren) > 0 and len(pr_mv) > 0, "unplanted 0 problems; renamed %d; moved %d" % (len(pr_ren), len(pr_mv)))

    if MODE3:
        # (c) the reproduction comparison must fail when ONE old-base wall is flipped: plant it on the old building and recount
        cfo = analyze(edit_vertices(told, [o for o in M.objects(told) if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "wall" and o["fields"][5].lower() == "outdoors"][0], "reverse"))
        cbo = analyze(told)
        es_in = old_tot[DISTRICTS[0]]["wall_out_in"]
        planted_in = es_in - cbo["wall_out_in"] + cfo["wall_out_in"]
        rp0 = REPRO_OLD[DISTRICTS[0]]
        say("PLANT old base: one outdoor wall flipped in memory, Madrid probe inward total %d -> %d (9h value %d); reproduction test would read: %s"
            % (es_in, planted_in, rp0["wall_out_in"], "PASS" if planted_in == rp0["wall_out_in"] else "FAIL"))
        verdict("planted flip on the old base makes the reproduction test fail", planted_in != rp0["wall_out_in"] and es_in == rp0["wall_out_in"], "unplanted total equals 9h, planted total does not")
    with io.open(os.path.join(OUT, FILEPFX + "_check_per_building.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["district", "stem"] + sorted(analyze(tnew).keys()) + ["n_problems_vs_old"] + (["changed_walls_vs_old", "changed_windows_vs_old", "old_wall_out_in", "old_edge_in"] if MODE3 else []))
        w.writerows(rows_out)
    say("ALL CHECKS PASS" if all(ok for _, ok in verdicts) else "SOME CHECK FAILED: %s" % [n for n, ok in verdicts if not ok])
    with io.open(os.path.join(OUT, FILEPFX + "_check_log.txt"), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
