# -*- coding: utf-8 -*-
"""5J design checker.

Usage: 5thJ_check_design.py [--dir Step2_docs/outputs_step2] [--manifest archetype_idf_manifest.csv]
       [--uk-households households_uk.csv]   (optional; once the author has run the UK script)

Each check prints PASS / FAIL / NOT_EVALUABLE.  SUMMARY line gives the three counts.
EXIT CODE: 0 = all PASS; 1 = at least one FAIL; 2 = at least one NOT_EVALUABLE and no FAIL
(a missing or unreadable file is never a pass and never silently a fail).
Checks: 40 buildings per country, 10 per class, every archetype period of the class used, archetype
codes exist in the manifest, building_ids unique; 60 households per country (es, it) with no duplicate
hid, split counts 40/10/10; pilot has 50 rows, run_ids unique, 5 buildings, 10 households, every pilot
household and building exists in the tables with the pilot flag set, climate exists in climates.csv.
"""
import argparse
import collections
import csv
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT5 = os.path.dirname(HERE)
DIR_DEFAULT = os.path.join(ROOT5, "Step2_docs", "outputs_step2")
MAN_DEFAULT = os.path.join(os.path.dirname(ROOT5), "4J_docs_occ", "Step8_docs", "outputs_step8",
                           "archetype_idf_manifest.csv")


def rd(path):
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DIR_DEFAULT)
    ap.add_argument("--manifest", default=MAN_DEFAULT)
    ap.add_argument("--uk-households", default=None)
    a = ap.parse_args()
    res = []   # (name, outcome, detail)

    def rec(name, ok, detail=""):
        res.append((name, "PASS" if ok else "FAIL", detail))

    try:
        B = rd(os.path.join(a.dir, "buildings.csv"))
        H = rd(os.path.join(a.dir, "households.csv"))
        C = rd(os.path.join(a.dir, "climates.csv"))
        P = rd(os.path.join(a.dir, "pilot_runs.csv"))
        M = rd(a.manifest)
    except (IOError, OSError, csv.Error, UnicodeDecodeError) as e:
        print("NOT_EVALUABLE tables: %s" % e)
        print("SUMMARY PASS=0 FAIL=0 NOT_EVALUABLE=1")
        return 2
    if a.uk_households:
        try:
            H = H + rd(a.uk_households)
        except (IOError, OSError, csv.Error) as e:
            res.append(("uk_households_readable", "NOT_EVALUABLE", str(e)))

    rec("building_ids_unique", len(set(b["building_id"] for b in B)) == len(B), "%d rows" % len(B))
    man_codes = set(m["code"] for m in M)
    for c in ("es", "uk", "it"):
        bc = [b for b in B if b["country"] == c]
        rec("buildings_%s_40" % c, len(bc) == 40, "n=%d" % len(bc))
        rec("archetype_codes_in_manifest_%s" % c, all(b["archetype_code"] in man_codes for b in bc))
        for cls in ("SFH", "TH", "MFH", "AB"):
            bcc = [b for b in bc if b["class"] == cls]
            rec("buildings_%s_%s_10" % (c, cls), len(bcc) == 10, "n=%d" % len(bcc))
            need = set(m["cell_period"] for m in M if m["fold"] == c and m["cls"] == cls)
            got = set(b["period"] for b in bcc)
            rec("periods_%s_%s_all_used" % (c, cls), need and need <= got,
                "missing=%s" % sorted(need - got))
    hh_by = {}
    for c in ("es", "it"):
        hc = [h for h in H if h["country"] == c]
        hh_by[c] = hc
        rec("households_%s_60" % c, len(hc) == 60, "n=%d" % len(hc))
        rec("households_%s_no_dup_hid" % c, len(set(h["hid"] for h in hc)) == len(hc))
        def _pos(v):   # 5J change (households v2)
            try:
                return float(v) > 0
            except (TypeError, ValueError):
                return False
        nbad = sum(1 for h in hc if not _pos(h.get("weight")))
        rec("weight_%s_nonblank_positive" % c, nbad == 0, "bad=%d of %d" % (nbad, len(hc)))
        sp = collections.Counter(h["split_draft"] for h in hc)
        rec("split_%s_40_10_10" % c, sp["dev"] == 40 and sp["val"] == 10 and sp["test"] == 10,
            dict(sp).__repr__())
    ukc = [h for h in H if h["country"] == "uk"]
    if ukc:
        rec("households_uk_60_no_dup", len(ukc) == 60 and len(set(h["hid"] for h in ukc)) == 60)
    else:
        print("NOTE UK households not checked: no --uk-households file (author runs the UK script)")

    rec("pilot_50_rows", len(P) == 50, "n=%d" % len(P))
    rec("pilot_run_ids_unique", len(set(p["run_id"] for p in P)) == len(P))
    bid = dict((b["building_id"], b) for b in B)
    hid = dict((h["household_id"], h) for h in H)
    cid = set(c["climate_id"] for c in C)
    rec("pilot_buildings_exist_es_flagged",
        all(p["building_id"] in bid and bid[p["building_id"]]["country"] == "es"
            and bid[p["building_id"]]["pilot"] == "1" for p in P))
    rec("pilot_households_exist_es_flagged",
        all(p["household_id"] in hid and hid[p["household_id"]]["country"] == "es"
            and hid[p["household_id"]]["pilot"] == "1" for p in P))
    rec("pilot_5_buildings_10_households",
        len(set(p["building_id"] for p in P)) == 5 and len(set(p["household_id"] for p in P)) == 10)
    rec("pilot_climate_exists", all(p["climate"] in cid for p in P))
    rec("climates_9", len(C) == 9, "n=%d" % len(C))

    for n, o, d in res:
        print("%s %s %s" % (o, n, d))
    cnt = collections.Counter(o for _, o, _ in res)
    print("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d" % (cnt["PASS"], cnt["FAIL"], cnt["NOT_EVALUABLE"]))
    if cnt["FAIL"]:
        return 1
    return 2 if cnt["NOT_EVALUABLE"] else 0


if __name__ == "__main__":
    sys.exit(main())
