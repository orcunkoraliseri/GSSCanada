"""FINDING 8 smoke -- the one residual the day-type mechanism does NOT explain.

F30 HOTEL_BOT_LAUNDRY measured 1.019 where the schedule-only prediction says 1.0000 exactly (its
prototype has Saturday == Sunday, so the 2-day-type rebuild is lossless for it). Two candidates:

  (a) the injector rescaled its Peak_Flow_Rate -- a code behaviour, and a defect at r = 1.000
  (b) plant-loop coupling -- the main LAUNDRY draw on the same loop fell 67 %, which can move the
      loop/mains temperatures and hence another object's heating energy at unchanged flow

This distinguishes them by reading Peak_Flow_Rate for all 47 objects out of both IDFs. If (a), the
number changed and that is the answer. If every peak is identical, (a) is excluded and (b) is what
remains -- stated as the remaining candidate, not as a proven one, because this script cannot
prove (b).

Usage: python 3rdJ_09F_peakflow_check.py <injected.idf> <source.idf>
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict


def read_we(path):
    txt = re.sub(r"!.*?$", "", open(path, encoding="utf-8", errors="replace").read(), flags=re.M)
    out = {}
    for chunk in txt.split(";"):
        f = [x.strip() for x in chunk.split(",")]
        f = [x for x in f if x != ""]
        if len(f) >= 4 and f[0].upper() == "WATERUSE:EQUIPMENT":
            # Name, EndUseSubcategory, PeakFlowRate, FlowRateFractionScheduleName, ...
            out[f[1].upper()] = {"peak": f[3], "sched": f[4] if len(f) > 4 else ""}
    return out


def main():
    inj, src = read_we(sys.argv[1]), read_we(sys.argv[2])
    print(f"injected n={len(inj)}  source n={len(src)}")
    changed = []
    for nm in sorted(set(inj) | set(src)):
        a = src.get(nm, {}).get("peak")
        b = inj.get(nm, {}).get("peak")
        if a is None or b is None:
            changed.append((nm, a, b, "object present in only one IDF"))
            continue
        if abs(float(a) - float(b)) > 1e-12:
            changed.append((nm, a, b, f"ratio {float(b) / float(a):.6f}"))
    print(f"\nPeak_Flow_Rate changed on {len(changed)} of {len(src)} objects")
    for nm, a, b, note in changed:
        print(f"  {nm[:58]:<60} {a} -> {b}   {note}")
    if not changed:
        print("  none -- the injector left every Peak_Flow_Rate untouched, so candidate (a) is")
        print("  EXCLUDED for every object including F30. Candidate (b), plant-loop coupling,")
        print("  is what remains; this script does not prove it.")

    print("\nF30 / LAUNDRY detail (same loop, the one that moved most):")
    for nm in sorted(inj):
        if "LAUNDRY" in nm:
            print(f"  {nm}")
            print(f"      source  peak={src.get(nm, {}).get('peak')} "
                  f"sched={src.get(nm, {}).get('sched')}")
            print(f"      injected peak={inj[nm]['peak']} sched={inj[nm]['sched']}")


if __name__ == "__main__":
    main()
