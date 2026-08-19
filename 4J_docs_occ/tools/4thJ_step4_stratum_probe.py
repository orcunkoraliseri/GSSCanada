"""FINDING 11 probe -- how many strata reach N >= 100, and on which real set.

G4.1 scores a stratum only when BOTH the real and the generated side carry
N >= TH.G4_1_MIN_STRATUM_N, and V4.a FAILs the gate outright when fewer than 5
strata qualify. Job 1266855 reported ZERO qualifying strata on fold es, so the
gate is unsatisfiable at any generation volume -- not because generation is too
small, but because the REAL side is the 5,520-diary held-in validation split.

This probe reports the stratum-size distribution on three real sets per fold so
the choice of basis is made against counts, not against a guess. It scores
nothing and changes nothing.
"""
import json, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
TH = importlib.import_module("4thJ_step4_thresholds")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")


def stratum_of(text):
    try:
        pref = text.split(TH.PREFIX_BODY_SEP)[0].split(",")
    except Exception:
        return None
    if len(pref) != len(TH.PREFIX_FIELDS):
        return None
    d = dict(zip(TH.PREFIX_FIELDS, pref))
    return (d["country"], d["strat_age_band"], d["strat_sex"],
            d["strat_hh_type"], d["strat_day_type"])


def read_jsonl(p):
    out = []
    with open(p, "r", encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def report(name, recs):
    c = Counter()
    for r in recs:
        s = stratum_of(r["text"])
        if s:
            c[s] += 1
    sizes = sorted(c.values(), reverse=True)
    n100 = sum(1 for v in sizes if v >= TH.G4_1_MIN_STRATUM_N)
    print("  %-28s records=%6d  strata=%4d  N>=100: %3d   top10=%s"
          % (name, len(recs), len(c), n100, sizes[:10]))
    return n100


m = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
print("G4.1 needs N >= %d in >= %d strata (V4.a). Stratum = %s"
      % (TH.G4_1_MIN_STRATUM_N, TH.V4_A_MIN_STRATA,
         "country,age_band,sex,hh_type,day_type"))
for fold in sorted(m["folds"]):
    fm = m["folds"][fold]
    tr = read_jsonl(fm["train"]["path"])
    va = read_jsonl(fm["heldin_val"]["path"])
    print("fold %s (held-out %s)" % (fold, fold))
    a = report("heldin_val ONLY  (current)", va)
    b = report("train ONLY", tr)
    c = report("train + heldin_val", tr + va)
    print("    -> on the current basis G4.1 %s; on train+val it %s"
          % ("FAILS via V4.a" if a < TH.V4_A_MIN_STRATA else "is reachable",
             "FAILS via V4.a" if c < TH.V4_A_MIN_STRATA else "is reachable"))
