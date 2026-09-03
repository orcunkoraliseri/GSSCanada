"""4thJ_imp_nocore_void_census.py -- two read-only censuses over the retained Step 10 run trees.

Written 2026-09-03 for IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md.

(1) VOID CENSUS. For every unique building (first cell found, case A, f = 0.00) parse the
    EnergyPlus IDF, take every BuildingSurface:Detailed of type `floor`, group by storey
    (zone name `_F<n>_`) and report, per storey, the sum of zone floor areas against the
    census footprint area carried in the cell manifest (`footprint_area_m2`).  The
    `void_share` is 1 - sum(zone floor areas) / footprint_area.  Under D-EU-80 (no empty
    space per floor) this must be ~0.  A convex-hull reference is reported beside it and
    is NOT the verdict: it was seen NOT failing on an edge-dwelling removal (blind spot).

(2) NO-CORE PROJECTION. For the same buildings, read `observed_dwellings` and
    `observed_storeys` from the manifest and apply the no-core storey rule
    k = max(1, round(dwellings / storeys)) (OpenUBEM PLAN_eu21-district-viewer-2026-09-03.md
    `load_universe`), so N_u(no-core) = k x storeys.  Compare with `zone_count_built`.
    This is ARITHMETIC ON THE CENSUS, never a result: no plate was cut, nothing was run.

Usage:
  python 4thJ_imp_nocore_void_census.py --runs <dir of <fold>__<building>__case<A|B>__f<NNN>/>
        --manifests <dir of *.json> --out-void <csv> --out-projection <csv>
"""
import argparse
import csv
import json
import os
import re
import statistics
from collections import defaultdict

from shapely.geometry import Polygon
from shapely.ops import unary_union

CELL_RE = re.compile(r"^(es|it|uk)__(.+)__case([AB])__f(\d{3})$")


def parse_floor_surfaces(idf_path):
    txt = open(idf_path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"!-[^\n]*", "", txt)
    txt = re.sub(r"^\s*!.*$", "", txt, flags=re.M)
    out = []
    for obj in txt.split(";"):
        f = [x.strip() for x in obj.split(",")]
        if not f or f[0].upper() != "BUILDINGSURFACE:DETAILED":
            continue
        if f[2].lower() != "floor":
            continue
        zone = f[4]
        nums = []
        for c in f[11:]:
            if c == "":
                continue
            try:
                nums.append(float(c))
            except ValueError:
                pass  # the 'autocalculate' number-of-vertices field
        pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - len(nums) % 3, 3)]
        if len(pts) >= 3:
            out.append((zone, Polygon(pts).buffer(0)))
    return out


def storey_of(zone_name):
    m = re.search(r"_F(\d+)_", zone_name)
    return int(m.group(1)) if m else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--manifests", required=True)
    ap.add_argument("--out-void", required=True)
    ap.add_argument("--out-projection", required=True)
    a = ap.parse_args()

    manifests = {}
    for fn in os.listdir(a.manifests):
        if fn.endswith("__caseA__f000.json"):
            d = json.load(open(os.path.join(a.manifests, fn), encoding="utf-8"))
            manifests[d["building_id"]] = d

    void_rows, proj_rows, seen = [], [], set()
    for d in sorted(os.listdir(a.runs)):
        m = CELL_RE.match(d)
        if not m:
            continue
        fold, bid, case, f = m.groups()
        if bid in seen:
            continue
        idf = os.path.join(a.runs, d, d + ".idf")
        if not os.path.exists(idf):
            continue
        seen.add(bid)
        man = manifests.get(bid)
        fp_area = float(man["footprint_area_m2"]) if man else float("nan")
        floors = parse_floor_surfaces(idf)
        by_st = defaultdict(list)
        for z, p in floors:
            by_st[storey_of(z)].append((z, p))
        arm_geom = "whole" if any(z.endswith("_whole") for z, _ in floors) else "dwelling"
        st_rows = []
        for st, zp in sorted(by_st.items()):
            polys = [p for _, p in zp]
            s = sum(p.area for p in polys)
            hull = unary_union(polys).convex_hull.area
            st_rows.append((st, len(zp), s, hull))
        void_fp = [1 - r[2] / fp_area for r in st_rows] if fp_area == fp_area else [float("nan")]
        void_hull = [1 - r[2] / r[3] for r in st_rows if r[3] > 0]
        void_rows.append(dict(
            building=bid, fold=fold, arm_geometry=arm_geom, arm_manifest=(man or {}).get("arm", ""),
            storeys=len(st_rows), zones_total=sum(r[1] for r in st_rows),
            zones_per_storey_median=statistics.median(r[1] for r in st_rows),
            footprint_area_m2=round(fp_area, 3),
            sum_floor_area_F0_m2=round(st_rows[0][2], 3),
            void_share_vs_footprint_max=round(max(void_fp), 5),
            void_share_vs_footprint_mean=round(statistics.mean(void_fp), 5),
            void_share_vs_hull_max=round(max(void_hull), 5) if void_hull else "",
        ))
        if man:
            dw = float(man["observed_dwellings"])
            st = int(round(float(man["observed_storeys"])))
            k = max(1, round(dw / st)) if st else 1
            proj_rows.append(dict(
                building=bid, fold=fold, arm=man["arm"], building_type=man["building_type"],
                layout_route_status=man["layout_route_status"], probe_emitted=man["probe_emitted"],
                observed_dwellings=int(dw), observed_storeys=st,
                zone_count_built=int(man["zone_count_built"]),
                storeys_without_a_dwelling=int(man["storeys_without_a_dwelling"]),
                k_nocore=k, n_u_nocore=k * st, dwelling_deficit_nocore=k * st - int(dw),
            ))

    for path, rows in ((a.out_void, void_rows), (a.out_projection, proj_rows)):
        if rows:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)

    print(f"buildings: {len(void_rows)}  zones_total: {sum(r['zones_total'] for r in void_rows)}")
    for arm in ("dwelling", "whole"):
        sub = [r for r in void_rows if r["arm_geometry"] == arm]
        if not sub:
            continue
        v = [r["void_share_vs_footprint_max"] for r in sub
             if r["void_share_vs_footprint_max"] == r["void_share_vs_footprint_max"]]
        h = [r["void_share_vs_hull_max"] for r in sub if r["void_share_vs_hull_max"] != ""]
        print(f"  {arm:8s} n={len(sub):2d} zones={sum(r['zones_total'] for r in sub):3d} "
              f"void_vs_footprint max={max(v):.5f} median={statistics.median(v):.5f} | "
              f"void_vs_hull max={max(h):.5f}")
    if proj_rows:
        b = sum(r["zone_count_built"] for r in proj_rows)
        n = sum(r["n_u_nocore"] for r in proj_rows)
        dw = sum(r["observed_dwellings"] for r in proj_rows)
        nz = [r for r in proj_rows if r["dwelling_deficit_nocore"] != 0]
        print(f"projection: zones built={b}  N_u(no-core)={n}  observed dwellings={dw}  "
              f"buildings where k*storeys != dwellings: {len(nz)}/{len(proj_rows)}  "
              f"largest deficit: {min(r['dwelling_deficit_nocore'] for r in proj_rows)}  "
              f"largest surplus: {max(r['dwelling_deficit_nocore'] for r in proj_rows)}")
        print(f"  Arm F with k>=2: {sum(1 for r in proj_rows if r['arm'] == 'F' and r['k_nocore'] >= 2)} "
              f"of {sum(1 for r in proj_rows if r['arm'] == 'F')}; "
              f"Arm D with k=1: {sum(1 for r in proj_rows if r['arm'] == 'D' and r['k_nocore'] == 1)} "
              f"of {sum(1 for r in proj_rows if r['arm'] == 'D')}; "
              f"k>12: {sum(1 for r in proj_rows if r['k_nocore'] > 12)}")


if __name__ == "__main__":
    main()
