"""FINDING 8 smoke -- ATTRIBUTION table.

The smoke test reported 7 objects off the no-op requirement. This script answers the only question
that decides what those 7 mean: **did the fix move them, or were they already off before it?**

For every WaterUse:Equipment object it prints, side by side:

    armE  = armE_Y2022 / armE_NECB     (the ratio the pre-fix injector produced)
    fixed = new_Y2022  / new_NECB      (the ratio the fixed injector produces)
    d     = fixed / armE               (what the fix itself changed)

  d == 1.000  -> the fix did not touch this object. If `fixed` is off 1.000, the cause is
                 PRE-EXISTING and is a different defect from FINDING 8.
  d != 1.000  -> the fix moved it, and `fixed` is the fix's own result.

It also lists every water-related output variable in the SQL, because the smoke run reported the
volume ratio as nan and that must be explained rather than left as a blank cell in the table.

Usage (on the cluster, under sbatch):
    python 3rdJ_09F_smoke_delta.py <new_campaign_dir> <armE_campaign_dir>
"""
from __future__ import annotations

import os
import sqlite3
import sys

ENERGY_VAR = "WATER USE EQUIPMENT HEATING ENERGY"
TOL = 0.002
CELL = "Y2022__Tall__MTL"
NECB = "Default_NECB__Tall__MTL"


def find_sql(d):
    for root, _dirs, files in os.walk(d):
        for n in files:
            if n.lower().endswith(".sql"):
                return os.path.join(root, n)
    return None


def per_object(path, varname):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT ReportDataDictionaryIndex, KeyValue FROM ReportDataDictionary "
                "WHERE UPPER(Name) = ?", (varname,))
    idx = {i: (k or "").strip().upper() for i, k in cur.fetchall()}
    out = {}
    if idx:
        qs = ",".join("?" * len(idx))
        cur.execute(f"SELECT ReportDataDictionaryIndex, SUM(Value) FROM ReportData "
                    f"WHERE ReportDataDictionaryIndex IN ({qs}) "
                    f"GROUP BY ReportDataDictionaryIndex", tuple(idx))
        for i, s in cur.fetchall():
            out[idx[i]] = float(s or 0.0)
    con.close()
    return out


def water_vars(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    rows = con.execute("SELECT DISTINCT Name FROM ReportDataDictionary "
                       "WHERE UPPER(Name) LIKE '%WATER%' ORDER BY Name").fetchall()
    con.close()
    return [r[0] for r in rows]


def ratio(a, b):
    return (a / b) if b else float("nan")


def main():
    new_c, arm_c = sys.argv[1], sys.argv[2]
    paths = {k: find_sql(os.path.join(root, cell))
             for k, (root, cell) in {"new_y": (new_c, CELL), "new_n": (new_c, NECB),
                                     "arm_y": (arm_c, CELL), "arm_n": (arm_c, NECB)}.items()}
    for k, p in paths.items():
        if not p:
            raise SystemExit(f"missing sql for {k}")
        print(f"{k}: {p}")
    E = {k: per_object(p, ENERGY_VAR) for k, p in paths.items()}

    print(f"\nwater-related output variables present in the new Y2022 sql "
          f"(explains the nan volume column):")
    for v in water_vars(paths["new_y"]):
        print(f"    {v}")

    keys = sorted(set(E["new_y"]) | set(E["arm_y"]))
    print(f"\n{'object':<58}{'armE':>9}{'fixed':>9}{'d=fix/armE':>12}  attribution")
    n_moved = n_pre = 0
    for k in keys:
        r_arm = ratio(E["arm_y"].get(k, float("nan")), E["arm_n"].get(k, 0.0))
        r_new = ratio(E["new_y"].get(k, float("nan")), E["new_n"].get(k, 0.0))
        d = ratio(r_new, r_arm)
        moved = abs(d - 1.0) > TOL
        off = abs(r_new - 1.0) > TOL
        if moved:
            n_moved += 1
            att = "MOVED BY THE FIX"
        elif off:
            n_pre += 1
            att = "PRE-EXISTING (fix did not touch it)"
        else:
            att = "no-op, clean"
        print(f"  {k[:56]:<58}{r_arm:>9.3f}{r_new:>9.3f}{d:>12.4f}  {att}")

    print(f"\n{len(keys)} objects | {n_moved} moved by the fix | "
          f"{n_pre} off no-op but NOT moved by the fix (pre-existing, separate defect)")

    # channel roll-up: the objects that are off, grouped, so the pattern is visible
    print("\nreference-cell sanity: new NECB vs armE NECB, per object")
    worst = 0.0
    for k in sorted(set(E["new_n"]) | set(E["arm_n"])):
        r = ratio(E["new_n"].get(k, float("nan")), E["arm_n"].get(k, 0.0))
        worst = max(worst, abs(r - 1.0))
    print(f"  worst |ratio - 1| across {len(E['new_n'])} objects = {worst:.6f}  "
          f"({'reference is stable' if worst <= 1e-6 else 'REFERENCE MOVED -- ratios are not comparable'})")


if __name__ == "__main__":
    main()
