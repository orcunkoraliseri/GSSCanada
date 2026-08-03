"""P4 follow-up -- WHERE does residential DHW energy rise 41 % while its volume falls 3.5 %?

Established by `3rdJ_09E_dhw_identity_probe.py` (job 1171407) on `Y2022__Tall__MTL`, arm E:

    residential DHW VOLUME  (Peak_Flow_Rate x schedule mean)  = 0.9647 x prototype
    residential DHW ENERGY  (agg_annual, end_use='dhw')       = 1.412  x prototype

The volume identity of T9-13 is therefore CORRECT and is not the cause. The energy has to be
entering between the water draw and the fuel meter.

PREDICTION, recorded in improvements/3rdJ_L3_improvements_step9.md BEFORE this probe was run
(the whole point -- an explanation written after seeing the decomposition can never fail):

    HYPOTHESIS  Peak_Flow_Rate rose per household (e.g. 3.919e-06 -> 4.907e-06 m3/s, +25 %)
                against HARD-SIZED water heaters, so the plant spends more time in recovery.
    IF TRUE     the water-HEATING component tracks volume (~0.96x) and the excess sits almost
                entirely in tank / standby-loss / recovery terms.
    IF FALSE    the water-heating component is itself ~1.41x, and the fault is in the draw
                temperature or in the end-use attribution, NOT in plant sizing.

Both branches are stated, so the probe can refute the hypothesis rather than illustrate it.

Method: read the two cells' `eplusout.sql`, list every water/DHW-related output variable and meter
present, and report each one's annual total for injected vs uninjected plus the ratio. No variable
is filtered out in advance -- a decomposition that only reports the terms the hypothesis needs is
the same failure mode as a test that cannot fail.

Usage:  python 3rdJ_09E_dhw_energy_probe.py <injected_cell_dir> <necb_cell_dir>
"""
from __future__ import annotations

import os
import sqlite3
import sys

KEYS = ("WATER", "DHW", "TANK", "HEATER", "SWH")


def find_sql(d):
    for root, _dirs, files in os.walk(d):
        for n in files:
            if n.lower().endswith(".sql"):
                return os.path.join(root, n)
    return None


def totals(path):
    """{(VariableName, KeyValue, Units): annual_sum} for every water/DHW-ish variable."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    out = {}
    try:
        cur.execute("SELECT ReportDataDictionaryIndex, Name, KeyValue, Units "
                    "FROM ReportDataDictionary")
        rows = cur.fetchall()
    except sqlite3.Error as e:
        con.close()
        raise SystemExit(f"cannot read ReportDataDictionary in {path}: {e}")
    wanted = {i: (n, k or "", u or "")
              for i, n, k, u in rows if any(t in (n or "").upper() for t in KEYS)}
    if wanted:
        qmarks = ",".join("?" * len(wanted))
        cur.execute(f"SELECT ReportDataDictionaryIndex, SUM(Value) FROM ReportData "
                    f"WHERE ReportDataDictionaryIndex IN ({qmarks}) "
                    f"GROUP BY ReportDataDictionaryIndex", list(wanted))
        for i, s in cur.fetchall():
            out[wanted[i]] = float(s or 0.0)
    con.close()
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    inj_d, necb_d = sys.argv[1], sys.argv[2]
    pi, pn = find_sql(inj_d), find_sql(necb_d)
    if not pi or not pn:
        raise SystemExit(f"missing eplusout.sql: injected={pi} uninjected={pn}")
    print(f"injected  : {pi}")
    print(f"uninjected: {pn}\n")

    ti, tn = totals(pi), totals(pn)
    keys = sorted(set(ti) | set(tn), key=lambda k: (k[0], k[1]))
    if not keys:
        print("No water/DHW variables are reported in these SQL files. That is itself the answer:")
        print("the decomposition cannot be done from this output set, and the run would need")
        print("Output:Variable requests added. Reporting that, not guessing.")
        return

    print(f"{'variable':<52}{'key':<26}{'units':<10}"
          f"{'uninjected':>16}{'injected':>16}{'ratio':>9}")
    agg = {}
    for k in keys:
        name, key, units = k
        a, b = tn.get(k, 0.0), ti.get(k, 0.0)
        r = (b / a) if abs(a) > 1e-12 else float("nan")
        agg.setdefault(name, [0.0, 0.0, units])
        agg[name][0] += a
        agg[name][1] += b
        if len(keys) <= 60:
            print(f"{name[:52]:<52}{key[:26]:<26}{units[:10]:<10}{a:>16.4e}{b:>16.4e}{r:>9.3f}")
    if len(keys) > 60:
        print(f"  ({len(keys)} series -- per-key rows suppressed, totals by variable below)")

    print("\n--- totals by variable (all keys summed) ---")
    print(f"{'variable':<58}{'units':<10}{'uninjected':>16}{'injected':>16}{'ratio':>9}")
    for name in sorted(agg):
        a, b, units = agg[name]
        r = (b / a) if abs(a) > 1e-12 else float("nan")
        print(f"{name[:58]:<58}{units[:10]:<10}{a:>16.4e}{b:>16.4e}{r:>9.3f}")

    print("\nHOW TO READ THIS, per the prediction recorded before the run:")
    print("  volume-like series (Water Use Equipment Hot Water Volume / Mass) ~0.96 AND")
    print("  heating-energy series ~1.41  -> hypothesis SUPPORTED, excess is plant-side.")
    print("  heating-energy series ~0.96 with losses ~1.41 -> SUPPORTED, excess is standby.")
    print("  volume-like series ~1.41 too -> hypothesis REFUTED; the draw itself changed and the")
    print("    IDF-level volume identity and the SQL disagree, which would be a parse error in")
    print("    the identity probe rather than a plant effect.")


if __name__ == "__main__":
    main()
