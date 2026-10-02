# -*- coding: utf-8 -*-
"""5J Step 7 manager own-code check (Speed CPU job; Spain only; never a UK file). Written by the manager, imports no project module.
Part 1: check draw 4 rebuilt from the 100 per-dwelling hourly files (gzip + csv, no pandas) vs draws/d0004.npz (all and in-range).
Part 2: the 1,000 district draws: annual totals from the per-dwelling ANNUAL array (not hourly_all), peak hour from hourly_all,
percentiles by own linear interpolation; compared with out_step7/district_spread.csv (written %.6g, so tolerance 2e-5 relative).
Part 3: own settling list (first n with 90 % interval width within 5 % of the width at 1,000 draws), printed for the paper.
Planted faults: 1e-5 of the annual total added to one hour of one dwelling in part 1; one csv value moved by 1e-4 relative in part 2.
Exit 0 all pass and both plants caught; 1 a check failed or a plant not caught; 2 could not run."""
import csv, gzip, io, sys
import numpy as np

D = "/speed-scratch/o_iseri/5J/district/"
CL = "es_madrid_2010"
T = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
TN = ["heating", "cooling", "equipment", "total_elec"]
H = 8760
N = 1000
CK = [10, 20, 50, 100, 200, 500, 1000]
FAILS = []


def chk(name, ok, text=""):
    print("MGR %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def pct(x, p):
    s = sorted(x)
    pos = p / 100.0 * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (pos - lo) * (s[hi] - s[lo])


def part1():
    twins = list(csv.DictReader(io.open(D + "out/twin_range_es.csv", encoding="utf-8")))
    ha = np.zeros((H, 4))
    hi = np.zeros((H, 4))
    nd_tot = 0
    for t in twins:
        nd = int(t["dwellings"])
        a = np.zeros((H, 4))
        rows = 0
        with gzip.open("%spred_check/%s/es_madrid_%s_d004.csv.gz" % (D, CL, t["twin_id"]), "rt") as f:
            r = csv.reader(l for l in f if not l.startswith("#"))
            head = next(r)
            idx = [head.index(c) for c in T]
            ih = head.index("hour")
            for row in r:
                a[int(row[ih]) - 1] += [float(row[i]) for i in idx]
                rows += 1
        if rows != nd * H:
            chk("rows_%s" % t["twin_id"], False, "%d rows for %d dwellings" % (rows, nd))
        nd_tot += nd
        ha += a
        if t["range"] == "in_range":
            hi += a
    z = np.load(D + "draws/d0004.npz")
    chk("draw4_file_is_draw_4", int(z["draw"]) == 4 and len(z["annual"]) == nd_tot, "dwellings %d" % nd_tot)

    def diff(f, g):
        ann = float((np.abs(f.sum(0) - g.sum(0)) / np.where(f.sum(0) > 0, f.sum(0), 1.0)).max())
        hr = float(np.abs(f - g).max() / f.sum(1).max())
        return ann, hr
    for nm, f, g in (("all", ha, z["hourly_all"]), ("inrange", hi, z["hourly_inrange"])):
        a, h = diff(f, g)
        chk("draw4_%s_hourly_files_equal_draw_file" % nm, a <= 1e-6 and h <= 1e-6, "annual rel %.2e hourly/peak %.2e" % (a, h))
        print("MGR draw4 %s annual kWh own: %s" % (nm, " ".join("%s=%.1f" % (n, v) for n, v in zip(TN, f.sum(0)))))
    p = ha.copy()
    p[4000, 0] += 1e-5 * ha[:, 0].sum()
    a, h = diff(p, z["hourly_all"])
    chk("planted_part1_caught", not (a <= 1e-6 and h <= 1e-6), "annual rel %.2e hourly/peak %.2e" % (a, h))


def part2():
    seeds_ok = True
    ann_all = np.zeros((N, 4))
    pk_all = np.zeros((N, 4))
    pk_in = np.zeros((N, 4))
    ann_in = np.zeros((N, 4))
    for d in range(N):
        z = np.load(D + "draws/d%04d.npz" % d)
        if int(z["draw"]) != d:
            seeds_ok = False
        ann_all[d] = z["annual"].sum(0)
        ann_in[d] = z["hourly_inrange"].sum(0)
        pk_all[d] = z["hourly_all"].max(0)
        pk_in[d] = z["hourly_inrange"].max(0)
    chk("all_1000_draw_files_read", seeds_ok)
    rows = list(csv.DictReader(io.open(D + "out_step7/district_spread.csv", encoding="utf-8")))
    src = {("all", "annual"): ann_all, ("in_range", "annual"): ann_in, ("all", "peak_hour"): pk_all, ("in_range", "peak_hour"): pk_in}
    own = {}
    for (sc, m), arr in src.items():
        for ti, t in enumerate(TN):
            for n in CK:
                x = list(arr[:n, ti])
                own[(sc, t, m, n)] = (float(np.median(x)), pct(x, 5), pct(x, 95))
    worst, nrow = 0.0, 0
    first = None
    for r in rows:
        t = r["target"].replace("_kwh", "")
        k = (r["scope"], t, r["metric"], int(r["n_draws"]))
        if k not in own:
            continue
        for j, c in enumerate(("median_kwh", "p05_kwh", "p95_kwh")):
            v = float(r[c])
            e = abs(v - own[k][j]) / max(abs(own[k][j]), 1e-9)
            worst = max(worst, e)
            if first is None:
                first = (k, j, v)
        nrow += 1
    chk("spread_csv_equals_own_percentiles", nrow == 2 * 4 * 2 * len(CK) and worst <= 2e-5, "rows compared %d worst rel %.2e" % (nrow, worst))
    k, j, v = first
    e = abs(v * (1 + 1e-4) - own[k][j]) / max(abs(own[k][j]), 1e-9)
    chk("planted_part2_caught", e > 2e-5, "moved value rel %.2e" % e)
    for sc in ("all", "in_range"):
        for t in TN:
            for m in ("annual", "peak_hour"):
                md, a, b = own[(sc, t, m, N)]
                w = b - a
                fs = next(n for n in CK if abs((own[(sc, t, m, n)][2] - own[(sc, t, m, n)][1]) - w) <= 0.05 * w)
                ws = " ".join("n%d=%.4f" % (n, (own[(sc, t, m, n)][2] - own[(sc, t, m, n)][1]) / w) for n in CK)
                stable = all(abs((own[(sc, t, m, n)][2] - own[(sc, t, m, n)][1]) - w) <= 0.05 * w for n in CK if n >= fs)
                print("MGR SPREAD %s %s %s median=%.1f p05=%.1f p95=%.1f width=%.2f%% of median ; first n within 5%%: %d (stays within after: %s) ; width/width1000 %s"
                      % (sc, t, m, md, a, b, 100 * w / md, fs, stable, ws))


def main():
    try:
        part1()
        part2()
    except Exception as ex:
        print("MGR could not run: %r" % ex)
        sys.exit(2)
    print("MGR SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
