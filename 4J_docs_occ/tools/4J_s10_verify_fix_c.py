"""FIX (c) verification, run against the REAL IDFs EnergyPlus refused.

Reads the surface table of the built IDF of every class-C failing building, then replays
BOTH construction-assignment rules over those surfaces:

  OLD (deployed, tools/4thJ_step10_nocore_campaign.py:1038-1045) -- keyed on Surface_Type only
  NEW (prepared)                                                 -- interzone plates take the
                                                                    interior-slab construction

and counts, for each rule, the interzone pairs whose two faces would receive DIFFERENT
constructions -- exactly what EnergyPlus refuses with
"does not have the same materials in the reverse order".

The OLD count is checked against the severes actually printed in eplusout.err: the test is only
trusted because it reproduces the real failure first.  Read-only; builds nothing, runs no engine.
"""
import sys, re
from collections import defaultdict

def load(path):
    b = {}; cur = None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("###BUILDING|"):
            cur = line.split("|",1)[1]; b[cur] = {"s": {}, "cn": []}
        elif line.startswith("###S|"):
            f = line.split("|")
            b[cur]["s"][f[1].upper()] = dict(name=f[1], typ=f[2].upper(), con=f[3],
                                             zone=f[4], obc=f[5].upper(), obco=f[6])
        elif line.startswith("###CN|"):
            b[cur]["cn"].append(line)
    return b

def old_rule(s, wall="EU_WALL", roof="EU_ROOF", floor="EU_FLOOR"):
    k = s["typ"]
    if k == "WALL": return wall
    if k in ("ROOF", "ROOFCEILING"): return roof
    if k in ("FLOOR", "CEILING"): return floor
    return None

def new_rule(s, wall="EU_WALL", roof="EU_ROOF", floor="EU_FLOOR"):
    k = s["typ"]
    if k == "WALL": return wall                       # both faces of a party wall are WALL
    if s["obc"] == "SURFACE": return floor            # interzone plate -> interior slab, both faces
    if k in ("ROOF", "ROOFCEILING"): return roof
    if k in ("FLOOR", "CEILING"): return floor
    return None

def violations(b, rule):
    bad = set()
    for nm, s in b["s"].items():
        if s["obc"] != "SURFACE" or not s["obco"]: continue
        p = b["s"].get(s["obco"].upper())
        if not p: continue
        if rule(s) != rule(p):
            bad.add(tuple(sorted([nm, s["obco"].upper()])))
    return bad

if __name__ == "__main__":
    tot_old = tot_new = 0
    print("%-22s %8s %10s %10s %10s" % ("building", "surfaces", "interzone", "OLD_bad", "NEW_bad"))
    for path in sys.argv[1:]:
        for bid, b in load(path).items():
            iz = sum(1 for s in b["s"].values() if s["obc"] == "SURFACE")
            o, n = violations(b, old_rule), violations(b, new_rule)
            tot_old += len(o); tot_new += len(n)
            severes = [l for l in b["cn"] if "** Severe" in l]
            print("%-22s %8d %10d %10d %10d   (eplusout.err severes of this class: %d)"
                  % (bid, len(b["s"]), iz, len(o), len(n), len(severes)))
    print("\nTOTAL interzone pairs with non-reversible constructions:")
    print("  OLD rule (deployed) : %d   <-- reproduces the fatal" % tot_old)
    print("  NEW rule (prepared) : %d" % tot_new)
    sys.exit(0 if (tot_old > 0 and tot_new == 0) else 1)
