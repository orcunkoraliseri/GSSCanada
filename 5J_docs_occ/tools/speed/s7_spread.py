# -*- coding: utf-8 -*-
"""5J Step 7 part F (Speed CPU job): district spread over the N draws. Reads draws/d<DDDD>.npz (written by s7_draws_gpu.py), writes
out_step7/district_spread.csv: per scope (all dwellings / in-range twins only), target, metric (annual = sum over the 8,760 h, peak_hour = max
over the hours of the district hourly total, kWh): median and 90 % interval (5th and 95th percentile, numpy linear) over the first n draws,
n in 10, 20, 50, 100, 200, 500, 1000 (<= N), N//2 and N. Validation 1.1 (draws written = draws counted), 1.3 (different seeds give different
totals) and 1.4 (first half within 5 % of the full interval; WARN) are printed."""
import io, json, os, sys
sys.dont_write_bytecode = True
import numpy as np
import s7_common as s7
import s5_common as c

OUT = s7.D + "out_step7/"
CKPT = [10, 20, 50, 100, 200, 500, 1000]
WRITER = "s7_draws_gpu v1 2026-10-01"


def main():
    s7.stamp("s7_spread start")
    os.makedirs(OUT, exist_ok=True)
    fails = []
    N = int(io.open(s7.D + "out/n_chosen_B.txt").read().split()[0])
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    seals = {l.split()[1]: l.split()[0] for l in io.open(s7.IN + "SEALS.md5", encoding="utf-8") if len(l.split()) == 2}
    print("GATE draws_json_sealed_and_unchanged %s" % ("PASS" if seals.get("draws.json") == s7.md5(s7.IN + "draws.json") else "FAIL"))
    ha = np.zeros((N, c.H, 4))
    hi = np.zeros((N, c.H, 4))
    nin = []
    ok = True
    for d in range(N):
        p = s7.D + "draws/d%04d.npz" % d
        if not os.path.exists(p):
            ok = False
            print("MISSING %s" % p)
            continue
        z = np.load(p)
        if not (str(z["writer"]) == WRITER and int(z["draw"]) == d and int(z["seed"]) == dj["seeds"][d]):
            ok = False
            print("BAD FILE %s" % p)
        ha[d], hi[d] = z["hourly_all"], z["hourly_inrange"]
        nin.append(len(z["annual"]))
    print("GATE 1.1 draw_count_written_equals_draws_counted %s (N=%d, files read %d, dwellings per draw min %d max %d)" % ("PASS" if ok and len(nin) == N else "FAIL", N, len(nin), min(nin), max(nin)))
    if not ok:
        sys.exit(1)
    tot = ha.sum(1)[:, 3]
    print("GATE 1.3 different_seeds_different_district_totals %s (distinct total_elec annual values %d of %d)" % ("PASS" if len(set(np.round(tot, 3))) == N else "FAIL", len(set(np.round(tot, 3))), N))
    rows = []
    cps = sorted({n for n in CKPT if n <= N} | {N // 2, N})
    summ = {}
    for scope, arr in (("all", ha), ("in_range", hi)):
        for ti, t in enumerate(c.TARGETS):
            for metric, v in (("annual", arr.sum(1)[:, ti]), ("peak_hour", arr.max(1)[:, ti])):
                for n in cps:
                    x = v[:n]
                    med, p05, p95 = float(np.median(x)), float(np.percentile(x, 5)), float(np.percentile(x, 95))
                    rows.append([scope, t, metric, n, "%.6g" % med, "%.6g" % p05, "%.6g" % p95, "%.6g" % (p95 - p05)])
                    summ[(scope, t, metric, n)] = (med, p05, p95)
    s7.write_csv(OUT + "district_spread.csv", ["scope", "target", "metric", "n_draws", "median_kwh", "p05_kwh", "p95_kwh", "interval_width_kwh"], rows)
    print("WROTE %s rows %d md5 %s" % (OUT + "district_spread.csv", len(rows), s7.md5(OUT + "district_spread.csv")))
    for scope in ("all", "in_range"):
        for t in c.TARGETS:
            for metric in ("annual", "peak_hour"):
                m, a, b = summ[(scope, t, metric, N)]
                mh, ah, bh = summ[(scope, t, metric, N // 2)]
                w, wh = b - a, bh - ah
                first = next((n for n in cps if abs((summ[(scope, t, metric, n)][2] - summ[(scope, t, metric, n)][1]) - w) <= 0.05 * w), None)
                print("SPREAD scope=%s %s %s N=%d median=%.1f p05=%.1f p95=%.1f width=%.1f (%.2f%% of median) ; first-half width ratio %.3f (1.4 %s) ; first n in the list with width within 5%% of full: %s" %
                      (scope, t, metric, N, m, a, b, w, 100 * w / m if m else float("nan"), wh / w if w else float("nan"), "ok" if w and abs(wh / w - 1) <= 0.05 else "WARN", first))
    print("SUMMARY fails=%d %s" % (len(fails), fails))
    sys.exit(0)


if __name__ == "__main__":
    main()
