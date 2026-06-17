"""
3rdJ Step 4N -- Pareto comparison of RAKED candidate bases (R7 / R8 / R10).

Rationale: the joint rake equalizes the binary marginals (G2/OW1 -> 0.00 by
construction) for ANY base, so those gates cannot discriminate between bases.
The bases differ only on what the rake does NOT touch:
  - OW5  (per-person day-type ordering)       -- raw-model behavioral consistency
  - act30 work&home  (load-driving telework)  -- raw-model activity calibration
  - S8   (distributional: EMD / KS / MAE / ACF) -- raw-model shape quality

So we Pareto-compare the raked variants ONLY on these rake-insensitive axes.
NEVER a composite score -- we print the axes and flag Pareto dominance.

Reads each variant's step4_validation_report.txt (already produced by the
validator on the _raked dir) + runs the home-gated act30 probe on its diaries.
"""
import os
import re
import sys
import numpy as np
import pandas as pd

N_SLOTS = 48
WORK_PEAK_SLOTS = list(range(8, 20))
WORK_CAT = 1
ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

DEFAULT_VARIANTS = ["R7_cap_raked", "R8_deep_raked", "R10_fast_raked"]


def home_gated(diaries_path):
    """Return JOINT/AWAY/COND deltas (obs vs syn) for act30 work-peak."""
    df = pd.read_csv(diaries_path, low_memory=False)
    out = {}
    for name, d in (("obs", df[df["IS_SYNTHETIC"] == 0]),
                    ("syn", df[df["IS_SYNTHETIC"] == 1])):
        a = d[ACT].to_numpy(dtype=float)[:, WORK_PEAK_SLOTS]
        h = d[HOM].to_numpy(dtype=float)[:, WORK_PEAK_SLOTS]
        work = (a == WORK_CAT); home = (h == 1)
        out[name] = (
            float((work & home).mean()) * 100,                              # joint
            float((work & ~home).mean()) * 100,                             # away
            float(work[home].mean()) * 100 if home.sum() else float("nan"), # cond
        )
    o, s = out["obs"], out["syn"]
    return {"joint": abs(o[0] - s[0]), "away": abs(o[1] - s[1]), "cond": abs(o[2] - s[2])}


def parse_report(txt_path):
    """Pull the rake-insensitive metrics out of a validation report .txt."""
    t = open(txt_path, encoding="utf-8", errors="replace").read()
    g = {}

    def grab(pat, cast=float):
        m = re.search(pat, t)
        return cast(m.group(1)) if m else None

    g["pass"] = grab(r"PASS:\s*(\d+)", int)
    g["warn"] = grab(r"WARN:\s*(\d+)", int)
    g["fail"] = grab(r"FAIL:\s*(\d+)", int)
    g["ow5"] = grab(r"Day-type ordering wkdy>=Sat>=Sun:\s*([\d.]+)%")
    g["g4_uncond"] = grab(r"Work peak-slot delta:\s*([\d.]+) pp")
    g["s8w_emd"] = grab(r"\[AT_WORK\] EMD\(daily-presence-count\):\s*([\d.]+)")
    g["s8w_mae"] = grab(r"\[AT_WORK\] mean-curve MAE:\s*([\d.]+)")
    g["s8w_acf"] = grab(r"\[AT_WORK\] ACF-MAE \(lags 1-24\):\s*([\d.]+)")
    g["s8h_mae"] = grab(r"\[AT_HOME\] mean-curve MAE:\s*([\d.]+)")
    g["s8h_acf"] = grab(r"\[AT_HOME\] ACF-MAE \(lags 1-24\):\s*([\d.]+)")
    return g


def fmt(v, nd=2):
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) and v == v else "  --"


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "outputs_step4/sweep"
    variants = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_VARIANTS

    rows = []
    for v in variants:
        vdir = os.path.join(base, v)
        rpt = os.path.join(vdir, "step4_validation_report.txt")
        dia = os.path.join(vdir, "augmented_diaries.csv")
        if not os.path.isfile(rpt) or not os.path.isfile(dia):
            print(f"[skip] {v}: missing report or diaries ({vdir})")
            continue
        g = parse_report(rpt)
        hg = home_gated(dia)
        g.update({f"hg_{k}": val for k, val in hg.items()})
        g["variant"] = v
        rows.append(g)

    if not rows:
        print("No variants available to compare.")
        return

    print("\n================ RAKED-BASE PARETO COMPARISON ================")
    print("(rake equalizes binaries; we compare only what the rake leaves to the base)\n")
    hdr = (f"{'variant':<16}{'P/W/F':>10}{'OW5%':>8}{'work&home':>11}"
           f"{'cond':>8}{'W-ACF':>9}{'W-MAE':>8}{'H-ACF':>9}{'H-MAE':>8}")
    print(hdr); print("-" * len(hdr))
    for g in rows:
        pwf = f"{g.get('pass','?')}/{g.get('warn','?')}/{g.get('fail','?')}"
        print(f"{g['variant']:<16}{pwf:>10}{fmt(g.get('ow5'),1):>8}"
              f"{fmt(g.get('hg_joint')):>11}{fmt(g.get('hg_cond')):>8}"
              f"{fmt(g.get('s8w_acf'),4):>9}{fmt(g.get('s8w_mae')):>8}"
              f"{fmt(g.get('s8h_acf'),4):>9}{fmt(g.get('s8h_mae')):>8}")
    print("\nLegend: OW5% higher=better; everything else lower=better.")
    print("work&home = act30 load-driving delta (pp); cond = act30 telework accuracy (pp).")

    # ---- Pareto dominance (OW5 higher better; rest lower better) ----
    def dominates(a, b):
        axes_lo = ["hg_joint", "s8w_acf", "s8w_mae", "s8h_acf", "s8h_mae"]
        ge_all = (a.get("ow5", -1) >= b.get("ow5", -1))
        for k in axes_lo:
            av, bv = a.get(k), b.get(k)
            if av is None or bv is None:
                return False
            ge_all = ge_all and (av <= bv)
        strict = (a.get("ow5", -1) > b.get("ow5", -1)) or any(
            (a.get(k) is not None and b.get(k) is not None and a[k] < b[k]) for k in axes_lo)
        return ge_all and strict

    print("\n---- Pareto verdict ----")
    nondom = []
    for a in rows:
        if not any(dominates(b, a) for b in rows if b is not a):
            nondom.append(a["variant"])
    for a in rows:
        beaten = [b["variant"] for b in rows if b is not a and dominates(a, b)]
        if beaten:
            print(f"  {a['variant']} dominates: {', '.join(beaten)}")
    print(f"\nNon-dominated (Pareto front): {', '.join(nondom)}")
    if nondom == ["R7_cap_raked"] or (len(nondom) == 1 and nondom[0] == "R7_cap_raked"):
        print("=> R7_cap_raked is the sole non-dominated base. Close Step 4 on it.")
    else:
        print("=> Pareto front has >1 base. Inspect axes above; pick by OW5/work&home priority.")


if __name__ == "__main__":
    main()
