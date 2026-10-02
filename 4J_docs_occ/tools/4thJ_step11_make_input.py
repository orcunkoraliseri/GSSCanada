"""4J Step 11 input builder -- the `<district>_step11input` copy of a finished C2 run.

Written 2026-10-01 for the London + Bologna re-run after the OpenUBEM neighbourhood fix
(plan `IMP/docs/2026-10-01_rerun-London-Bologna-stock-enduse_plan.md`, sections 3b and 3.2).

What it does, and why each rule exists:
  * Keeps CASE B cells only.  C2 simulates every building twice: Case A copies one diary to every
    flat, Case B gives each flat its own (`4thJ_step10_paired.py:5-6`).  Step 11 keys flats by
    (building, case, unit), so feeding both cases counted every real flat twice (plan 3b).
  * Drops every building whose cells carry a floor-averaged diary
    (`merged_floor_averaged_occupancy`), whole building, named in the manifest -- the rule used for
    the 49 buildings of the 2026-09-12 run.
  * Drops cells that did not complete; a building with any missing or failed Case B cell is
    dropped whole and named, never half-kept.
  * CHECK 1: flats kept = sum of `observed_dwellings` over kept buildings = sum of emitted zones.
  * CHECK 2 (with `--openubem-counts`): every kept building's flat count equals OpenUBEM's
    `new_count` for that building.  A mismatch stops the run.
  * `--plant-case-a` adds one Case A cell to the copy, so CHECK 1 must FAIL (the check seen failing).

Exit codes: 0 = input written and both checks passed; 2 = a check failed (copy left for reading,
manifest says FAIL); 1 = refused before writing (bad arguments, missing input).
Scores nothing.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from collections import defaultdict

F_LEVELS = (0.00, 0.15, 0.30, 0.50, 1.00)


def f_slug(f):
    return "f%03d" % round(f * 100)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--c2-out", required=True, help="C2 output dir holding cells/")
    ap.add_argument("--dst", required=True, help="new <district>_step11input dir (must not exist)")
    ap.add_argument("--openubem-counts", default=None,
                    help="OpenUBEM per-building CSV with building_id,new_count")
    ap.add_argument("--plant-case-a", action="store_true",
                    help="planted fault: copy one Case A cell too; CHECK 1 must fail")
    a = ap.parse_args()

    src = os.path.join(a.c2_out, "cells")
    if not os.path.isdir(src):
        print("REFUSE: no cells dir at %s" % src)
        return 1
    if os.path.exists(a.dst):
        print("REFUSE: %s already exists; move it away first, never mix runs" % a.dst)
        return 1

    cells = {}
    for name in sorted(os.listdir(src)):
        if name.endswith(".json"):
            with open(os.path.join(src, name), encoding="utf-8") as fh:
                cells[name] = json.load(fh)
    if not cells:
        print("REFUSE: %s is empty" % src)
        return 1

    by_bldg = defaultdict(dict)
    merged, failed = set(), set()
    for name, c in cells.items():
        by_bldg[c["building_id"]][(c["case"], c["sensitivity_f"])] = name
        if not c.get("completed"):
            failed.add(c["building_id"])
        if any(s.get("merged_floor_averaged_occupancy") for s in c.get("schedules") or []):
            merged.add(c["building_id"])

    missing_b = set()
    for b, got in by_bldg.items():
        if any(("B", f) not in got for f in F_LEVELS):
            missing_b.add(b)

    dropped = merged | failed | missing_b
    kept = sorted(set(by_bldg) - dropped)

    os.makedirs(os.path.join(a.dst, "cells"))
    per_bldg = {}
    n_copied = 0
    for b in kept:
        units, zones_emitted, observed = set(), None, None
        for f in F_LEVELS:
            name = by_bldg[b][("B", f)]
            c = cells[name]
            shutil.copy2(os.path.join(src, name), os.path.join(a.dst, "cells", name))
            n_copied += 1
            units |= {s["unit_index"] for s in c["schedules"]}
            zones_emitted, observed = c.get("zone_count_emitted"), c.get("observed_dwellings")
        per_bldg[b] = {"flats": len(units), "observed_dwellings": observed,
                       "zone_count_emitted": zones_emitted}

    planted = None
    if a.plant_case_a:
        for b in kept:
            name = by_bldg[b].get(("A", 0.0))
            if name:
                shutil.copy2(os.path.join(src, name), os.path.join(a.dst, "cells", name))
                planted = name
                print("PLANTED FAULT: Case A cell %s copied in" % name)
                break

    # CHECK 1 -- read back from the COPY, keyed the way Step 11 keys flats.
    keys = set()
    for name in os.listdir(os.path.join(a.dst, "cells")):
        with open(os.path.join(a.dst, "cells", name), encoding="utf-8") as fh:
            c = json.load(fh)
        for s in c["schedules"]:
            keys.add((c["building_id"], c["case"], s["unit_index"]))
    n_step11_flats = len(keys)
    n_observed = sum(v["observed_dwellings"] or 0 for v in per_bldg.values())
    n_zones = sum(v["zone_count_emitted"] or 0 for v in per_bldg.values())
    check1 = n_step11_flats == n_observed == n_zones
    print("CHECK 1 flats as Step 11 keys them=%d, observed_dwellings=%d, emitted zones=%d -> %s"
          % (n_step11_flats, n_observed, n_zones, "PASS" if check1 else "FAIL"))

    # CHECK 2 -- against OpenUBEM's own per-building count.
    check2, mism = None, []
    if a.openubem_counts:
        theirs = {}
        with open(a.openubem_counts, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                theirs[row["building_id"]] = int(row["new_count"])
        for b in kept:
            if theirs.get(b) != per_bldg[b]["flats"]:
                mism.append((b, per_bldg[b]["flats"], theirs.get(b)))
        check2 = not mism
        print("CHECK 2 per-building flats vs OpenUBEM new_count: %d buildings, %d mismatches -> %s"
              % (len(kept), len(mism), "PASS" if check2 else "FAIL"))
        for m in mism[:20]:
            print("  mismatch %s ours=%s openubem=%s" % m)
    else:
        print("CHECK 2 NOT RUN: no --openubem-counts given")

    ok = check1 and (check2 is not False)
    manifest = {
        "tool": "4thJ_step11_make_input.py", "c2_out": a.c2_out,
        "cells_sha256": hashlib.sha256("".join(sorted(cells)).encode()).hexdigest(),
        "case_kept": "B", "n_cells_read": len(cells), "n_cells_copied": n_copied,
        "n_buildings_kept": len(kept), "n_flats": n_step11_flats,
        "dropped_floor_averaged": sorted(merged), "dropped_incomplete": sorted(failed),
        "dropped_missing_case_b": sorted(missing_b - merged - failed),
        "check1": "PASS" if check1 else "FAIL",
        "check2": None if check2 is None else ("PASS" if check2 else "FAIL"),
        "check2_mismatches": mism, "planted_fault": planted,
        "verdict": "PASS" if ok else "FAIL",
    }
    with open(os.path.join(a.dst, "step11input_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    print("WROTE %s: %d buildings, %d flats, dropped %d floor-averaged / %d incomplete / %d missing B"
          % (a.dst, len(kept), n_step11_flats, len(merged), len(failed),
             len(missing_b - merged - failed)))
    print("VERDICT: %s" % manifest["verdict"])
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
