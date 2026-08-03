"""FINDING 9 smoke -- PRE-REGISTERED scorer. Written and uploaded BEFORE the cells were run.

Compares the FINDING-9-fixed cells (arm G) against the FINDING-8-fixed cells (arm F), each over
its own `Default_NECB` reference, so every number is a ratio-of-ratios and the reference cancels.

The predictions are not guesses. `3rdJ_09F_daytype_loss.py` predicts each object's ratio from the
SCHEDULES ALONE, and on arm F that prediction matched the simulated energy to three decimals for
every commercial object. After the fix the same predictor returns 1.0000 for all of them
(verified locally, `3rdJ_09G_finding9_verify.py`). So the energy must follow.

  MUST MOVE TO 1.000 -- the six objects whose prototype has Saturday != Sunday
      F1 / F2 RETAIL_*_BACKSPACE ............ 0.923 -> 1.000
      F3-F11 / F12-F20 OFFICE_RESTROOM ...... 0.952 -> 1.000
      BOOSTER ............................... 0.995 -> 1.000
      F38 HOTEL_TOP_KITCHEN ................. 0.995 -> 1.000

  MUST NOT MOVE -- prototypes with Saturday == Sunday, which FINDING 9 never touched
      F30 HOTEL_BOT_LAUNDRY ................. stays 1.019   <-- THE DISCRIMINATING ONE
      LAUNDRY ............................... stays 1.000
      F31-F37 / F38 guest rooms (12) ........ stay  1.000
      residential (27) ...................... unchanged from arm F, |delta| < 0.002

F30 is the sharp test. The FINDING 8 report attributed its 1.9 % residual to something OTHER than
the day-type collapse, on the grounds that its prototype has Saturday == Sunday. If F30 moves to
1.000 here, that attribution was WRONG and this file says so -- the prediction is not adjusted
after the fact.

Usage:  python 3rdJ_09G_score_f9.py <armG_campaign_dir> <armF_campaign_dir>
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys

ENERGY_VAR = "WATER USE EQUIPMENT HEATING ENERGY"
CELL, NECB = "Y2022__Tall__MTL", "Default_NECB__Tall__MTL"
TOL = 0.003

# (regex on the SQL key, arm-F ratio, required arm-G ratio, note)
PREDICTED = [
    (r"^F1 RETAIL_F1_BACKSPACE",        0.923, 1.000, "Sat != Sun -> must be fixed"),
    (r"^F2 RETAIL_F2_BACKSPACE",        0.923, 1.000, "Sat != Sun -> must be fixed"),
    (r"^F3-F11 OFFICE_RESTROOM",        0.952, 1.000, "Sat != Sun -> must be fixed"),
    (r"^F12-F20 OFFICE_RESTROOM",       0.952, 1.000, "Sat != Sun -> must be fixed"),
    (r"^BOOSTER SERVICE WATER USE",     0.995, 1.000, "Sat != Sun -> must be fixed"),
    (r"^F38 HOTEL_TOP_KITCHEN",         0.995, 1.000, "Sat != Sun -> must be fixed"),
    (r"^F30 HOTEL_BOT_LAUNDRY",         1.019, 1.019, "Sat == Sun -> MUST NOT MOVE"),
    (r"^LAUNDRY SERVICE WATER USE",     1.000, 1.000, "Sat == Sun -> must not move"),
]
GUESTROOM_RE = re.compile(r"GUESTRM", re.I)
RESID_RE = re.compile(r"(RESI_|APARTMENT)", re.I)


def find_sql(d):
    for root, _dirs, files in os.walk(d):
        for n in files:
            if n.lower().endswith(".sql"):
                return os.path.join(root, n)
    return None


def per_object(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT ReportDataDictionaryIndex, KeyValue FROM ReportDataDictionary "
                "WHERE UPPER(Name) = ?", (ENERGY_VAR,))
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


def main():
    g_root, f_root = sys.argv[1], sys.argv[2]
    sqls = {}
    for lbl, root, cell in (("g_y", g_root, CELL), ("g_n", g_root, NECB),
                            ("f_y", f_root, CELL), ("f_n", f_root, NECB)):
        p = find_sql(os.path.join(root, cell))
        if not p:
            raise SystemExit(f"missing sql for {lbl} under {os.path.join(root, cell)}")
        sqls[lbl] = p
        print(f"{lbl}: {p}")
    E = {k: per_object(p) for k, p in sqls.items()}

    def ratio(y, n, k):
        a, b = E[y].get(k), E[n].get(k)
        return (a / b) if (a is not None and b) else float("nan")

    keys = sorted(E["g_y"])
    print(f"\nobjects reporting '{ENERGY_VAR}': armG={len(E['g_y'])} armF={len(E['f_y'])}")

    n_pass = n_fail = 0
    print(f"\n=== PRE-REGISTERED ===\n  {'object':<50}{'armF':>8}{'armG':>8}"
          f"{'req':>8}  verdict  note")
    matched = set()
    for pat, f_exp, g_req, note in PREDICTED:
        rx = re.compile(pat, re.I)
        hits = [k for k in keys if rx.search(k)]
        if len(hits) != 1:
            n_fail += 1
            print(f"  {pat:<50}{'--':>8}{'--':>8}{g_req:>8.3f}  FAIL     "
                  f"{len(hits)} SQL keys matched, need exactly 1")
            continue
        k = hits[0]
        matched.add(k)
        rf, rg = ratio("f_y", "f_n", k), ratio("g_y", "g_n", k)
        ok_f = abs(rf - f_exp) <= TOL
        ok_g = abs(rg - g_req) <= TOL
        ok = ok_f and ok_g
        n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
        tail = "" if ok_f else f"  (armF baseline was {rf:.3f}, expected {f_exp:.3f})"
        print(f"  {k[:48]:<50}{rf:>8.3f}{rg:>8.3f}{g_req:>8.3f}  "
              f"{'PASS' if ok else 'FAIL'}     {note}{tail}")

    print("\n=== GUEST ROOMS (must stay 1.000) ===")
    gr = [k for k in keys if GUESTROOM_RE.search(k)]
    worst = max((abs(ratio("g_y", "g_n", k) - 1.0) for k in gr), default=float("nan"))
    ok = len(gr) == 12 and worst <= TOL
    n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
    print(f"  n={len(gr)} (expect 12), worst |ratio-1| = {worst:.4f}  "
          f"{'PASS' if ok else 'FAIL'}")

    print("\n=== RESIDENTIAL (must be unchanged from arm F) ===")
    rs = [k for k in keys if RESID_RE.search(k)]
    worst_r = max((abs(ratio("g_y", "g_n", k) - ratio("f_y", "f_n", k)) for k in rs),
                  default=float("nan"))
    ok = len(rs) == 27 and worst_r <= 0.002
    n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
    print(f"  n={len(rs)} (expect 27), worst |armG - armF| = {worst_r:.4f}  "
          f"{'PASS' if ok else 'FAIL'}")

    print("\n=== ANY OTHER OBJECT THAT MOVED (none was predicted to) ===")
    others = [k for k in keys if k not in matched and not GUESTROOM_RE.search(k)
              and not RESID_RE.search(k)]
    moved = [(k, ratio("f_y", "f_n", k), ratio("g_y", "g_n", k)) for k in others
             if abs(ratio("g_y", "g_n", k) - ratio("f_y", "f_n", k)) > TOL]
    for k, a, b in moved:
        print(f"  UNPREDICTED MOVE  {k[:50]:<52}{a:>8.3f} -> {b:>8.3f}")
        n_fail += 1
    print(f"  {len(others)} other objects, {len(moved)} moved")

    print(f"\n=== VERDICT: {n_pass} PASS / {n_fail} FAIL ===")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
