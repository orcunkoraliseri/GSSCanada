"""WP15: re-extract annual energy and peak demand from eplustbl.htm (no SQL, no plotting.py).
Modes:  selftest --htm F --mtr F --old CSV     (local, one run)
        run --root stage4 --old-dir DIR --out DIR --workers N
The old (defective) rule is reproduced only for gate W15.1: annual kWh + demand W of the same end use.
"""
import re, os, sys, csv, argparse, math, html
from collections import defaultdict

CONV = {"GJ": 277.778, "kWh": 1.0, "J": 1 / 3.6e6, "kBtu": 0.293071, "Btu": 0.000293071, "MJ": 0.277778}
YEARS = ["2005", "2010", "2015", "2022", "2025"]
TAG = re.compile(r"<[^>]+>")


def cells(row_html):
    return [html.unescape(TAG.sub("", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.S)]


def get_table(txt, report, table, occurrence=0):
    """rows (list of cell lists) of `table` inside `report`; row 0 = header. Located by the Report: heading."""
    m = re.search(r"<p>Report:<b>\s*" + re.escape(report) + r"</b></p>", txt)
    if not m:
        raise KeyError("report " + report)
    start = m.end()
    nxt = txt.find("<p>Report:<b>", start)
    seg = txt[start: nxt if nxt > 0 else len(txt)]
    hits = list(re.finditer(r"<b>" + re.escape(table) + r"</b><br><br>", seg))
    if len(hits) <= occurrence:
        raise KeyError("table " + table)
    s = hits[occurrence].end()
    e = seg.find("</table>", s)
    return [cells(r) for r in re.findall(r"<tr>(.*?)</tr>", seg[s:e], re.S)]


def col_unit(h):
    m = re.search(r"\[([^\]]*)\]\s*$", h)
    return m.group(1) if m else ""


def col_fuel(h):
    return re.sub(r"\s*\[[^\]]*\]\s*$", "", h)


def to_float(s):
    try:
        return float(s)
    except ValueError:
        return None


def eu_name(row_name, sub):
    """calculate_eui naming: 'General'/'Other'/'' -> the end use itself; else the subcategory."""
    return row_name if sub in ("General", "Other", "") else sub


def rows_of(tab, has_sub):
    hdr = tab[0]
    off = 2 if has_sub else 1
    out = []
    for r in tab[1:]:
        if not r or not r[0] or r[0].startswith("Total") or r[0].startswith("Time of Peak"):
            continue
        sub = r[1] if has_sub else ""
        for j in range(off, min(len(hdr), len(r))):
            v = to_float(r[j])
            if v is None:
                continue
            out.append((r[0], sub, col_fuel(hdr[j]), col_unit(hdr[j]), v))
    return out


def parse_htm(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    ABU = "Annual Building Utility Performance Summary"
    DEM = "Demand End Use Components Summary"
    R = {}
    area = {}
    for r in get_table(txt, ABU, "Building Area")[1:]:
        if len(r) > 1 and to_float(r[1]) is not None:
            area[r[0]] = to_float(r[1])
    R["area"] = area.get("Net Conditioned Building Area") or area.get("Total Building Area")
    if not R["area"]:
        raise ValueError("no area")
    R["ann_eu"] = rows_of(get_table(txt, ABU, "End Uses"), False)
    R["ann_sub"] = rows_of(get_table(txt, ABU, "End Uses By Subcategory"), True)
    R["dem_sub"] = rows_of(get_table(txt, DEM, "End Uses By Subcategory"), True)
    dem = get_table(txt, DEM, "End Uses")
    hdr = dem[0]
    pt, ptot = {}, {}
    for r in dem[1:]:
        if r and r[0] == "Time of Peak":
            for j in range(1, min(len(hdr), len(r))):
                pt[col_fuel(hdr[j])] = r[j]
        elif r and r[0] == "Total End Uses":
            for j in range(1, min(len(hdr), len(r))):
                ptot[col_fuel(hdr[j])] = (to_float(r[j]), col_unit(hdr[j]))
    R["peak_time"], R["peak_total"], R["dem_eu"] = pt, ptot, rows_of(dem, False)
    return R


def kwh(v, unit):
    """energy value -> kWh; None if not an energy unit (water volume, W, ...)"""
    if "m3" in unit or "gal" in unit.lower():
        return None
    return v * CONV[unit] if unit in CONV else None


def corrected_totals(R):
    tot = defaultdict(float)
    for eu, sub, fuel, unit, v in R["ann_sub"]:
        k = kwh(v, unit)
        if k is not None:
            tot[eu_name(eu, sub)] += k / R["area"]
    return dict(tot)


def old_reconstruction(R, include_demand=True):
    """calculate_eui as it behaved: unknown unit (W) taken as kWh and added to the same end use; /area, 3 decimals."""
    tot = defaultdict(float)
    tabs = [R["ann_sub"]] + ([R["dem_sub"]] if include_demand else [])
    for tab in tabs:
        for eu, sub, fuel, unit, v in tab:
            if "m3" in unit:
                continue
            val = v * CONV[unit] if unit in CONV else v
            if val != 0:
                tot[eu_name(eu, sub)] += val
    return {k: round(v / R["area"], 3) for k, v in tot.items()}


def w151(R, old, include_demand=True):
    rec = old_reconstruction(R, include_demand)
    md, worst = 0.0, None
    for eu, v in old.items():
        d = abs(rec.get(eu, 0.0) - v)
        if d > md:
            md, worst = d, eu
    for eu, v in rec.items():  # end uses the old file lacks must be ~0 in the reconstruction
        if eu not in old and abs(v) > md:
            md, worst = abs(v), eu + "(absent in old)"
    return md, len(old), worst


def read_old(path):
    d = defaultdict(dict)
    with open(path) as f:
        for r in csv.DictReader(f):
            d[(int(r["draw"]), r["year"])][r["end_use"]] = float(r["value"])
    return d


def mtr_sums(path):
    """{hourly meter name: kWh}"""
    ids = {}
    tot = defaultdict(float)
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith("End of Data Dictionary"):
                break
            m = re.match(r"(\d+),1,(\S+) \[J\] !Hourly", line)
            if m:
                ids[m.group(1)] = m.group(2)
        for line in f:
            p = line.rstrip("\n").split(",")
            if len(p) == 2 and p[0] in ids:
                tot[ids[p[0]]] += float(p[1]) / 3.6e6
    return dict(tot)


def w152(R, mtr_path):
    m = mtr_sums(mtr_path)
    eu = defaultdict(float)
    for name, sub, fuel, unit, v in R["ann_eu"]:
        k = kwh(v, unit)
        if k is not None:
            eu[name] += k
    mr, det = 0.0, []
    for a, b in [("Interior Equipment", "InteriorEquipment:Electricity"), ("Interior Lighting", "InteriorLights:Electricity")]:
        rel = abs(eu[a] - m[b]) / m[b]
        mr = max(mr, rel)
        det.append(f"{a} table={eu[a]:.1f} meter={m[b]:.1f} kWh rel={rel:.2e}")
    return mr, det


def w154(R):
    """End Uses table vs sum of its subcategory rows (kWh), max abs diff"""
    a, b = defaultdict(float), defaultdict(float)
    for eu, sub, fuel, unit, v in R["ann_eu"]:
        k = kwh(v, unit)
        if k is not None:
            a[eu] += k
    for eu, sub, fuel, unit, v in R["ann_sub"]:
        k = kwh(v, unit)
        if k is not None:
            b[eu] += k
    return max([abs(a[k] - b.get(k, 0.0)) for k in a] + [0.0])


def run_rows(nb, block, draw, year, R):
    A = R["area"]
    E, T, P, PE = [], [], [], []
    for eu, sub, fuel, unit, v in R["ann_eu"]:
        k = kwh(v, unit)
        if k is not None:
            E.append((nb, block, draw, year, eu, fuel, round(k, 3), round(k / A, 5), A))
    for eu, val in sorted(corrected_totals(R).items()):
        T.append((nb, draw, year, eu, round(val, 3)))
    for fuel, (pw, unit) in R["peak_total"].items():
        if unit == "W" and pw:
            P.append((nb, block, draw, year, fuel, pw, round(pw / A, 4), R["peak_time"].get(fuel, "")))
    for eu, sub, fuel, unit, v in R["dem_eu"]:
        if unit == "W" and v != 0:
            PE.append((nb, block, draw, year, eu, fuel, v, round(v / A, 4), R["peak_time"].get(fuel, "")))
    return E, T, P, PE


def selftest(a):
    R = parse_htm(a.htm)
    old = read_old(a.old)[(1, "2005")]
    print("area", R["area"])
    print("corrected kWh/m2:", {k: round(v, 3) for k, v in corrected_totals(R).items()})
    known = {"Heating": 39.029, "Cooling": 40.608, "Interior Lighting": 2.506, "Electric Equipment": 60.637, "Water Systems": 0.664}
    md0, n0, w0 = w151(R, old, include_demand=False)
    print(f"W15.1 WITHOUT demand term: maxdiff={md0:.3f} worst={w0} -> {'PASS' if md0 < 0.002 else 'FAIL'} (must FAIL)")
    md1, n1, w1 = w151(R, old, include_demand=True)
    print(f"W15.1 WITH demand term: maxdiff={md1:.5f} over {n1} end uses -> {'PASS' if md1 < 0.002 else 'FAIL'}")
    rec = old_reconstruction(R)
    print("reconstruction vs known old:", {k: (rec[k], known[k]) for k in known})
    mr, det = w152(R, a.mtr)
    print(f"W15.2 maxrel={mr:.2e} -> {'PASS' if mr < 1e-3 else 'FAIL'}", det)
    print("W15.4 End Uses vs subcategory max abs kWh diff", w154(R))
    print("peak_total", R["peak_total"])
    print("peak_time", R["peak_time"])
    E, T, P, PE = run_rows("NUS_RC1", 1, 1, "2005", R)
    print(len(E), len(T), len(P), len(PE))
    for t in T:
        print(t)
    for p in P:
        print(p)
    return 0 if (md0 >= 0.002 and md1 < 0.002 and mr < 1e-3) else 1


def one(task):
    nb, block, draw, year, folder = task
    p = os.path.join(folder, "eplustbl.htm")
    if not os.path.isfile(p) or os.path.getsize(p) == 0:
        return task, None, "MISSING htm"
    try:
        return task, parse_htm(p), None
    except Exception as ex:
        return task, None, "PARSE " + repr(ex)


def run(a):
    from multiprocessing import Pool
    tasks = []
    for n in range(1, 7):
        nb = f"NUS_RC{n}"
        for b in range(1, 7):
            base = os.path.join(a.root, "draws", f"block_{b}", nb)
            tasks.append((nb, b, 0, "Default", os.path.join(base, "Default")))
            for d in range(5 * b - 4, 5 * b + 1):
                for y in YEARS:
                    tasks.append((nb, b, d, y, os.path.join(base, f"iter_{d}", y)))
    os.makedirs(a.out, exist_ok=True)
    E, T, P, PE = [], [], [], []
    missing, found = defaultdict(list), defaultdict(int)
    old = {}
    for n in range(1, 7):
        for b in range(1, 7):
            old[(f"NUS_RC{n}", b)] = read_old(os.path.join(a.old_dir, f"b{b}_RC{n}_per_draw.csv"))
    maxdiff, worst_run, cmp_n = 0.0, None, 0
    defaults = defaultdict(dict)
    probe = {}
    with Pool(a.workers) as pool:
        for task, R, err in pool.imap(one, tasks, chunksize=4):
            nb, block, draw, year, folder = task
            if R is None:
                missing[nb].append((block, draw, year, err))
                print("W15 MISSING", nb, block, draw, year, err, flush=True)
                continue
            found[nb] += 1
            e, t, p, pe = run_rows(nb, block, draw, year, R)
            E += e; T += t; P += p; PE += pe
            o = old[(nb, block)].get((draw, year))
            if o:
                md, n, w = w151(R, o)
                cmp_n += n
                if md > maxdiff:
                    maxdiff, worst_run = md, (nb, block, draw, year, w)
                if md >= 0.002:
                    print("W15.1 DIFF", nb, block, draw, year, w, round(md, 4), flush=True)
            else:
                print("W15.1 NO OLD ROWS", nb, block, draw, year, flush=True)
            if year == "Default":
                defaults[nb][block] = corrected_totals(R)
            if block == 1 and draw == 1 and year == "2005":
                probe[nb] = (R, os.path.join(folder, "eplusout.mtr"))
            if w154(R) > 0.05:
                print("W15.4 END-USES vs SUBCATEGORY MISMATCH", nb, block, draw, year, flush=True)
    maxrel = 0.0
    for nb, (R, mp) in sorted(probe.items()):
        if os.path.isfile(mp):
            mr, det = w152(R, mp)
            maxrel = max(maxrel, mr)
            print("W15.2", nb, f"maxrel={mr:.2e}", det, flush=True)
        else:
            print("W15.2", nb, "NOT_EVALUABLE no mtr", flush=True)
            maxrel = float("nan")
    w152s = "NOT_EVALUABLE" if (math.isnan(maxrel) or len(probe) < 6) else ("PASS" if maxrel < 1e-3 else "FAIL")
    tot_missing = 0
    for n in range(1, 7):
        nb = f"NUS_RC{n}"
        tot_missing += len(missing[nb])
        print(f"W15 COUNT {nb} runs={found[nb]} missing={len(missing[nb])} (expected {5 * 30 + 6})", flush=True)
    spread = 0.0
    for nb, d in defaults.items():
        for eu in {k for t in d.values() for k in t}:
            vals = [t.get(eu, 0.0) for t in d.values()]
            spread = max(spread, max(vals) - min(vals))
    print(f"W15 DEFAULT max spread across blocks = {spread:.6f} kWh/m2 over {sum(len(d) for d in defaults.values())} default runs", flush=True)

    def wr(name, hdr, rows):
        with open(os.path.join(a.out, name), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(hdr)
            w.writerows(rows)
    wr("annual_enduse.csv", "neighbourhood,block,draw,year,end_use,fuel,kwh,kwh_m2,area_m2".split(","), E)
    wr("annual_enduse_totals.csv", "neighbourhood,draw,year,end_use,value".split(","), T)
    wr("peaks.csv", "neighbourhood,block,draw,year,fuel,peak_w,peak_w_m2,peak_time".split(","), P)
    wr("peaks_enduse.csv", "neighbourhood,block,draw,year,end_use,fuel,w,w_m2,peak_time".split(","), PE)
    w151s = "PASS" if (maxdiff < 0.002 and cmp_n > 0) else "FAIL"
    print(f"W15 SUMMARY runs={sum(found.values())} missing={tot_missing} W15.1={w151s} maxdiff={maxdiff:.5f} (worst {worst_run}, {cmp_n} comparisons) W15.2={w152s} maxreldiff={maxrel:.2e}", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode")
    ap.add_argument("--htm"); ap.add_argument("--mtr"); ap.add_argument("--old")
    ap.add_argument("--root"); ap.add_argument("--old-dir"); ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    sys.exit(selftest(a) if a.mode == "selftest" else run(a))
