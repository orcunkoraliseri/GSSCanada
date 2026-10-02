# -*- coding: utf-8 -*-
"""Figure 5 data job (Speed CPU job). Reads the N sealed district draw files (district/draws/d0000.npz ... d<N-1>.npz, integer loop, no glob),
district_spread.csv and district_check_draws.csv (all district outputs; no test-split file) and writes
figures/data/fig5_draws.parquet (draw, target, annual_kwh, peak_hour_kwh; scope = all dwellings) and its md5. No verdict on the surrogate.

CHECKS (printed as CHECK <name> PASS|FAIL, no verdict on the surrogate):
 (a) median, p05, p95 of the annual and the peak-hour totals at n = N and n = 100 equal district_spread.csv (scope all), rel 1e-5;
 (b) for the 20 check draws the S annual totals equal annual_S_kwh of district_check_draws.csv (scope all), rel 1e-5 (a path (a) cannot reach);
 (c) planted: one check draw's annual total x 1.001 must make (a) or (b) FAIL (the quantity itself is changed, then the same checks are re-run).
Exit code: 0 all real checks pass and the planted fault fired; 1 a real check failed or the planted fault did not fire; 2 a check did not run
(missing file or row, any exception).
Usage: fig05_data.py --root /speed-scratch/o_iseri/5J/district --out /speed-scratch/o_iseri/5J/figures/data
"""
import argparse, hashlib, io, os, sys, traceback
import numpy as np
import pandas as pd

TN = ["heating", "cooling", "equipment", "total_elec"]          # target order of hourly_all columns = s5_common.TARGETS without the _kwh suffix
H = 8760
WRITER_KEYS = ("hourly_all", "hourly_inrange", "annual", "writer", "draw", "seed")


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def norm(t):
    t = str(t)
    return t[:-4] if t.endswith("_kwh") else t


def run_checks(tab, spread, chk, N):
    """Returns (fails_a, fails_b, lines). Raises KeyError / ValueError when a row needed by a check does not exist (check did not run)."""
    lines, fa, fb = [], 0, 0
    nchk_a = 0
    for t in TN:
        sub = tab[tab["target"] == t].sort_values("draw")
        for metric, col in (("annual", "annual_kwh"), ("peak_hour", "peak_hour_kwh")):
            v = sub[col].to_numpy(dtype=float)
            for n in (N, 100):
                row = spread[(spread["scope"] == "all") & (spread["target"] == t) & (spread["metric"] == metric) & (spread["n_draws"] == n)]
                if len(row) != 1:
                    raise ValueError("spread row not found or not unique: %s %s %s n=%d (rows %d)" % ("all", t, metric, n, len(row)))
                r = row.iloc[0]
                x = v[:n]
                mine = (float(np.median(x)), float(np.percentile(x, 5)), float(np.percentile(x, 95)))
                theirs = (float(r["median_kwh"]), float(r["p05_kwh"]), float(r["p95_kwh"]))
                nchk_a += 1
                if not np.allclose(mine, theirs, rtol=1e-5, atol=0):
                    fa += 1
                    lines.append("  a mismatch %s %s n=%d mine=%s csv=%s" % (t, metric, n, mine, theirs))
    nchk_b = 0
    for _, r in chk.iterrows():
        d, t = int(r["draw"]), r["target"]
        got = tab[(tab["draw"] == d) & (tab["target"] == t)]
        if len(got) != 1:
            raise ValueError("draw table row not found: draw %d target %s" % (d, t))
        nchk_b += 1
        if not np.isclose(float(got["annual_kwh"].iloc[0]), float(r["annual_S_kwh"]), rtol=1e-5, atol=0):
            fb += 1
            lines.append("  b mismatch draw %d %s table=%.8g csv=%.8g" % (d, t, float(got["annual_kwh"].iloc[0]), float(r["annual_S_kwh"])))
    lines.append("  counts: (a) quantities compared %d x 3 numbers, (b) draw x target pairs compared %d" % (nchk_a, nchk_b))
    return fa, fb, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = a.root.rstrip("/") + "/"
    os.makedirs(a.out, exist_ok=True)
    try:
        N = int(io.open(root + "out/n_chosen_B.txt").read().split()[0])
        print("INFO N=%d" % N, flush=True)
        rows, nbad = [], 0
        for d in range(N):
            p = root + "draws/d%04d.npz" % d
            z = np.load(p)
            if any(k not in z.files for k in WRITER_KEYS) or int(z["draw"]) != d:
                nbad += 1
                print("BAD FILE %s keys=%s" % (p, z.files), flush=True)
                continue
            ha = np.asarray(z["hourly_all"], dtype=np.float64)
            if ha.shape != (H, 4):
                nbad += 1
                print("BAD SHAPE %s %s" % (p, ha.shape), flush=True)
                continue
            s, m = ha.sum(0), ha.max(0)
            for k, t in enumerate(TN):
                rows.append((d, t, float(s[k]), float(m[k])))
        print("CHECK draw_files_read %s files=%d bad=%d" % ("PASS" if nbad == 0 and len(rows) == 4 * N else "FAIL", N, nbad), flush=True)
        if nbad or len(rows) != 4 * N:
            sys.exit(2)
        tab = pd.DataFrame(rows, columns=["draw", "target", "annual_kwh", "peak_hour_kwh"])
        sp_path = root + "out_step7/district_spread.csv"
        ck_path = root + "out_step7/district_check_draws.csv"
        spread = pd.read_csv(sp_path)
        spread["target"] = spread["target"].map(norm)
        for c in ("n_draws", "median_kwh", "p05_kwh", "p95_kwh"):
            spread[c] = pd.to_numeric(spread[c])
        cd = pd.read_csv(ck_path)
        cd["target"] = cd["target"].map(norm)
        chk = cd[cd["scope"] == "all"].copy()
        print("INFO check rows (scope all) %d, distinct draws %d, targets %s" % (len(chk), chk["draw"].nunique(), sorted(chk["target"].unique())), flush=True)
        if len(chk) != 80:
            print("CHECK check_draw_rows FAIL expected 80 (20 draws x 4 targets) found %d" % len(chk), flush=True)
            sys.exit(2)
        fa, fb, lines = run_checks(tab, spread, chk, N)
        for ln in lines:
            print(ln, flush=True)
        print("CHECK spread_csv_equals_draw_table_n%d_and_n100 %s mismatches=%d" % (N, "PASS" if fa == 0 else "FAIL", fa), flush=True)
        print("CHECK check_draws_S_annual_equals_draw_table %s mismatches=%d" % ("PASS" if fb == 0 else "FAIL", fb), flush=True)
        # planted: the quantity itself changed for one check draw, same checks re-run; verdict counts compared with the unplanted run
        d0 = int(chk["draw"].iloc[0])
        tab2 = tab.copy()
        m0 = (tab2["draw"] == d0) & (tab2["target"] == "total_elec")
        tab2.loc[m0, "annual_kwh"] = tab2.loc[m0, "annual_kwh"] * 1.001
        fa2, fb2, _ = run_checks(tab2, spread, chk, N)
        fired = (fa2 + fb2) > (fa + fb)
        print("CHECK_PLANTED draw %d total_elec annual x 1.001: fails unplanted a=%d b=%d, planted a=%d b=%d -> %s" %
              (d0, fa, fb, fa2, fb2, "FIRED" if fired else "DID NOT FIRE"), flush=True)
        out = os.path.join(a.out, "fig5_draws.parquet")
        tab.to_parquet(out, index=False)
        with io.open(out + ".md5.txt", "w", encoding="utf-8") as fh:
            fh.write("%s  fig5_draws.parquet rows=%d N=%d\n" % (md5_file(out), len(tab), N))
            fh.write("%s  INPUT %s\n" % (md5_file(sp_path), sp_path))
            fh.write("%s  INPUT %s\n" % (md5_file(ck_path), ck_path))
        print("WROTE %s rows %d md5 %s" % (out, len(tab), md5_file(out)), flush=True)
        if fa or fb or not fired:
            print("EXIT 1 (a real check failed or the planted fault did not fire)", flush=True)
            sys.exit(1)
        print("EXIT 0", flush=True)
        sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        print("CHECK did_not_run EXCEPTION", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
