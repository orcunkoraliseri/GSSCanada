"""Seen-failing-first check for wp13_metrics.py on a 3-household synthetic grid.
HAND values below are worked out on paper (see comments), not by the script.
  HH1 Quebec  HHSIZE 1: weekday 1 at h0-7,18-23 else 0 (14 h, day 0)      ; weekend all 1 (24 h, day 1)
  HH2 Ontario HHSIZE 2: weekday 1 at h0-8,17-23, 0.5 at h9-16 (20 h, day .5); weekend all .5 (12 h, day .5)
  HH3 Ontario HHSIZE 5: weekday all .5 (12 h, day .5)                      ; weekend all .25 (6 h, day .25)
Canada weekday: hours (14+20+12)/3 = 15.33333, day (0+.5+.5)/3 = 0.333333 ; Quebec 14, 0 ; diff -1.333333, -0.333333
Canada weekend: hours (24+12+6)/3 = 14, day (1+.5+.25)/3 = 0.583333        ; Quebec 24, 1 ; diff +10, +0.416667
HHSIZE 5+ weekday hours 12, weekend 6.
"""
import sys, os, subprocess, tempfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
HAND = {
    ("Canada", "Weekday", "occupied_hours"): 46 / 3, ("Canada", "Weekday", "daytime_fraction"): 1 / 3,
    ("Quebec", "Weekday", "occupied_hours"): 14.0, ("Quebec", "Weekday", "daytime_fraction"): 0.0,
    ("Canada", "Weekend", "occupied_hours"): 14.0, ("Canada", "Weekend", "daytime_fraction"): 0.7 / 1.2,  # 7/12
    ("Quebec", "Weekend", "occupied_hours"): 24.0, ("Quebec", "Weekend", "daytime_fraction"): 1.0,
}
HAND["Canada", "Weekend", "daytime_fraction"] = 7 / 12
HAND_DIFF = {"Weekday": (14 - 46 / 3, 0 - 1 / 3), "Weekend": (24 - 14, 1 - 7 / 12)}


def make(swap=False):
    rows = []
    def prof(dt, hh):
        h = np.arange(24)
        if hh == 1:
            return np.where(((h <= 7) | (h >= 18)), 1.0, 0.0) if dt == "Weekday" else np.ones(24)
        if hh == 2:
            w = np.where(h <= 8, 1.0, np.where(h <= 16, 0.5, 1.0))
            return w if dt == "Weekday" else np.full(24, 0.5)
        return np.full(24, 0.5) if dt == "Weekday" else np.full(24, 0.25)
    meta = {1: ("Quebec", 1), 2: ("Ontario", 2), 3: ("Ontario", 5)}
    for hh in (1, 2, 3):
        for dt in ("Weekday", "Weekend"):
            lab = dt
            if swap:
                lab = "Weekend" if dt == "Weekday" else "Weekday"
            for h, v in enumerate(prof(dt, hh)):
                rows.append(dict(SIM_HH_ID=hh, Day_Type=lab, Hour=h, HHSIZE=meta[hh][1], DTYPE="MidRise",
                                 BEDRM=1, CONDO=0, ROOM=3, REPAIR=1, PR=meta[hh][0], MATCH_TIER="2_Core",
                                 Occupancy_Schedule=v, Metabolic_Rate=70.0 if v > 0 else 0.0))
    return pd.DataFrame(rows)


def run(df, tag):
    d = tempfile.mkdtemp()
    f = os.path.join(d, "syn.csv")
    df.to_csv(f, index=False)
    out = os.path.join(HERE, "out_" + tag)
    r = subprocess.run([sys.executable, os.path.join(HERE, "wp13_metrics.py"), "--test-file", f, "--outdir", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("script failed")
    return pd.read_csv(os.path.join(out, "metrics_by_year_region.csv")), pd.read_csv(os.path.join(out, "quebec_vs_canada.csv")), \
        pd.read_csv(os.path.join(out, "metrics_by_hhsize.csv"))


def check(m, q, hs):
    bad = 0
    print(f"{'quantity':45s} {'hand':>10s} {'script':>10s}  ok")
    for (reg, dt, col), hv in HAND.items():
        sv = float(m[(m.year == "TEST") & (m.region == reg) & (m.day_type == dt)][col].iloc[0])
        ok = abs(sv - hv) < 1e-9
        bad += not ok
        print(f"{reg+' '+dt+' '+col:45s} {hv:10.6f} {sv:10.6f}  {ok}")
    for dt, (hh_, dd_) in HAND_DIFF.items():
        r = q[q.day_type == dt].iloc[0]
        for lab, hv, sv in [("diff_occupied_hours", hh_, r.diff_occupied_hours), ("diff_daytime_fraction", dd_, r.diff_daytime_fraction),
                            ("boot point hours", hh_, r.boot_point_diff_hours), ("boot point daytime", dd_, r.boot_point_diff_daytime)]:
            ok = abs(sv - hv) < 1e-9
            bad += not ok
            print(f"{'Q-C '+dt+' '+lab:45s} {hv:10.6f} {sv:10.6f}  {ok}")
    for dt, hv in [("Weekday", 12.0), ("Weekend", 6.0)]:
        sv = float(hs[(hs.hhsize == "5+") & (hs.day_type == dt)].occupied_hours.iloc[0])
        ok = abs(sv - hv) < 1e-9
        bad += not ok
        print(f"{'HHSIZE 5+ '+dt+' occupied_hours':45s} {hv:10.6f} {sv:10.6f}  {ok}")
    return bad


if __name__ == "__main__":
    print("--- CORRECT synthetic file: expect 0 mismatches")
    b1 = check(*run(make(False), "good"))
    print("MISMATCHES:", b1)
    print("--- BROKEN synthetic file (Day_Type labels swapped): expect mismatches (check must fail)")
    b2 = check(*run(make(True), "swapped"))
    print("MISMATCHES:", b2)
    print("VERDICT:", "check works (passes good, fails broken)" if b1 == 0 and b2 > 0 else "CHECK BROKEN")
    sys.exit(0 if (b1 == 0 and b2 > 0) else 1)
