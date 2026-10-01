# 5J campaign design FIX: old (v1) vs new run tables. Runs on Speed. Reads csv only (es, it); no UK file.
import csv, io, collections, hashlib, sys
R = "/speed-scratch/o_iseri/5J/campaign_prep/"
OUT = R + "out/"


def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


bad = 0
for cc in ("es", "it"):
    po = OUT + "campaign_runs_%s.v1_2026-09-30.csv" % cc
    pn = OUT + "campaign_runs_%s.csv" % cc
    old, new = rd(po), rd(pn)
    print("MD5_OLD %s %s" % (cc, md5(po)))
    print("MD5_NEW %s %s" % (cc, md5(pn)))
    co = collections.Counter((r["class"], r["pool"], "rep" if r["replicate"] != "0" else "main") for r in old)
    cn = collections.Counter((r["class"], r["pool"], "rep" if r["replicate"] != "0" else "main") for r in new)
    for k in sorted(set(co) | set(cn)):
        print("COUNT_OLD_NEW %s %s %s old=%d new=%d %s" % (cc, k[0], k[1], co[k], cn[k], "same" if co[k] == cn[k] else "DIFFERENT") if k[2] == "main"
              else "COUNT_OLD_NEW %s %s %s(replicates) old=%d new=%d %s" % (cc, k[0], k[1], co[k], cn[k], "same" if co[k] == cn[k] else "DIFFERENT"))
        bad += co[k] != cn[k]
    print("COUNT_TOTAL %s old=%d new=%d %s" % (cc, len(old), len(new), "same" if len(old) == len(new) else "DIFFERENT"))
    bad += len(old) != len(new)
    same_ids = [r["run_id"] for r in old] == [r["run_id"] for r in new]
    print("RUNID_ORDER_SAME %s %s" % (cc, same_ids))
    bad += not same_ids
    other_cols = [c for c in old[0] if c != "placement"]
    diff_other = sum(1 for a, b in zip(old, new) if any(a[c] != b[c] for c in other_cols))
    diff_pl = sum(1 for a, b in zip(old, new) if a["placement"] != b["placement"])
    print("ROWS_DIFFER %s other_columns=%d placement=%d of %d rows" % (cc, diff_other, diff_pl, len(new)))
    bad += diff_other != 0
    # the rows that changed must be MFH/AB main rows only
    ch = collections.Counter((b["class"], b["pool"], b["replicate"]) for a, b in zip(old, new) if a["placement"] != b["placement"])
    print("PLACEMENT_CHANGED_BY_CLASS_POOL_REP %s %s" % (cc, dict(ch)))
    # slots per household per building unchanged (who sits how often)
    def slotcount(rows):
        c = collections.Counter()
        for r in rows:
            if r["replicate"] == "0" and r["class"] in ("MFH", "AB"):
                for it in r["placement"].split(";"):
                    c[(r["building_id"], r["climate_id"], r["pool"], it.split(":", 1)[1])] += 1
        return c
    same_sc = slotcount(old) == slotcount(new)
    print("SLOTS_PER_HOUSEHOLD_UNCHANGED %s %s" % (cc, same_sc))
    bad += not same_sc
print("COMPARE_RESULT %s" % ("ALL SAME (counts, run_ids, other columns, slots per household)" if bad == 0 else "PROBLEM %d" % bad))
