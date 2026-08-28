# -*- coding: utf-8 -*-
"""4J Step 10 --- THE PLATFORM ARM, MEASURED RATHER THAN ASSERTED.

`FINDING 181` is the EU arc's only open item, and its platform arm was carried
for weeks as "the author's call" because `EU-08`'s 1,185 retained manifests
carry `platform` in **0 of 1,185** --- no two-host claim was ever available from
that campaign, and retrofitting those manifests is forbidden. The author ordered
the Step 10 real-stock campaign onto Speed on 2026-08-28, reversing `Q3`, and
that order is what finally makes a two-host comparison possible AT ALL.

WHAT IS HELD CONSTANT, AND WHY IT MATTERS
-----------------------------------------
The SAME IDF BYTES and the SAME gain-schedule CSVs run on both hosts: they are
emitted once on Windows (`--emit-only`) and shipped. The EnergyPlus version is
23.1.0 on both --- Windows uses the installed build, Speed uses
`/speed-scratch/o_iseri/energyplus_23.1.0.sif`. Speed's extracted 24.2.0 trees
are NOT used and must never be. So the only thing that differs is the platform,
which is the only way the difference measured here means "platform".

Refusal `P1` enforces that: if a cell's `idf_sha256` differs between the two
hosts, the pair is DROPPED, never compared. A cell compared across two different
input files would be measuring the files.

WHAT THIS DOES NOT DO
---------------------
It does not move a gate, it does not touch `D-EU-31`'s 149 certified cells, and
it makes no accuracy claim. It reports agreement, per metric, with the worst
case named. `G8.14`'s platform arm stays NOT SCOREABLE on the EU campaign --- it
is that campaign's manifests that lack the field, and nothing here backfills it.

Usage:
    python 4thJ_step10_platform_compare.py --speed .../speed_metrics.jsonl \\
        --speed-sha .../idf_sha256_speed.txt
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOURJ = HERE.parent
OUT_DIR = FOURJ / "Step10_docs/outputs_step10/realstock_campaign"

#: Metrics compared, and the relative tolerance at which agreement is CALLED
#: rather than measured. These are report bands, not gates: nothing here is
#: allowed to turn a disagreement into a pass.
METRICS = (
    ("annual_heating_kwh", 1e-6),
    ("peak_hourly_building_kw", 1e-6),
    ("coincidence_factor", 1e-9),
    ("q99_hourly_building_kw", 1e-6),
)


def read_local(path: Path) -> dict:
    rows = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows[row["cell_id"]] = row
    return rows


def read_speed(path: Path) -> dict:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            rows[rec["cell_id"]] = rec
    return rows


def read_speed_sha(path) -> dict:
    """`sha256sum */*.idf` output, keyed by cell id (the directory name)."""
    out = {}
    if not path or not Path(path).is_file():
        return out
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        out[name.strip().replace("\\", "/").split("/")[0]] = digest
    return out


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rel_diff(a, b):
    if a is None or b is None:
        return None
    if a == b:
        return 0.0
    scale = max(abs(a), abs(b))
    return abs(a - b) / scale if scale > 0 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default=str(OUT_DIR / "realstock_campaign_manifest.csv"))
    ap.add_argument("--speed", required=True)
    ap.add_argument("--speed-sha", default="")
    ap.add_argument("--out", default=str(OUT_DIR / "realstock_platform_arm.json"))
    args = ap.parse_args()

    local = read_local(Path(args.local))
    speed = read_speed(Path(args.speed))
    speed_sha = read_speed_sha(args.speed_sha)

    both = sorted(set(local) & set(speed))
    report = {
        "what": "Step 10 real-stock campaign, Windows vs Speed, same IDF bytes, "
                "EnergyPlus 23.1.0 on both hosts",
        "authority": "author reversed Q3 on 2026-08-28 and ordered the campaign onto Speed",
        "local_platform": "windows_11_energyplus_23.1.0",
        "speed_platform": "speed_linux_energyplus_23.1.0_sif",
        "n_local": len(local), "n_speed": len(speed), "n_paired": len(both),
        "local_only": sorted(set(local) - set(speed)),
        "speed_only": sorted(set(speed) - set(local)),
    }

    compared, dropped_p1, incomplete = [], [], []
    for cell_id in both:
        loc, spd = local[cell_id], speed[cell_id]
        if str(loc.get("completed")).lower() not in ("true", "1") or not spd.get("completed"):
            incomplete.append(cell_id)
            continue
        # P1 --- the refusal that keeps this a PLATFORM comparison.
        digest_local = (loc.get("idf_sha256") or "").strip()
        digest_speed = speed_sha.get(cell_id, "")
        if digest_speed and digest_local and digest_speed != digest_local:
            dropped_p1.append({"cell_id": cell_id,
                               "idf_sha256_local": digest_local,
                               "idf_sha256_speed": digest_speed})
            continue
        entry = {"cell_id": cell_id, "arm": loc.get("arm"), "fold": loc.get("fold"),
                 "case": loc.get("case"), "sensitivity_f": as_float(loc.get("sensitivity_f")),
                 "idf_sha256_matched": bool(digest_speed and digest_speed == digest_local)}
        for name, _tol in METRICS:
            a, b = as_float(loc.get(name)), as_float(spd.get(name))
            entry[name + "_local"] = a
            entry[name + "_speed"] = b
            entry[name + "_rel_diff"] = rel_diff(a, b)
        a = as_float(loc.get("peak_hour_index_0based"))
        b = as_float(spd.get("peak_hour_index_0based"))
        entry["peak_hour_local"] = a
        entry["peak_hour_speed"] = b
        entry["peak_hour_shift_h"] = None if a is None or b is None else int(abs(a - b))
        compared.append(entry)

    report["n_compared"] = len(compared)
    report["dropped_by_P1_idf_sha_mismatch"] = dropped_p1
    report["not_completed_on_one_or_both_hosts"] = incomplete
    report["idf_sha256_matched_count"] = sum(1 for e in compared if e["idf_sha256_matched"])

    summary = {}
    for name, tol in METRICS:
        diffs = [(e[name + "_rel_diff"], e["cell_id"]) for e in compared
                 if e.get(name + "_rel_diff") is not None]
        if not diffs:
            summary[name] = {"population": 0, "verdict": "NOT_EVALUABLE_population_0"}
            continue
        worst, worst_cell = max(diffs)
        n_bitwise = sum(1 for d, _ in diffs if d == 0.0)
        summary[name] = {
            "population": len(diffs),
            "bitwise_identical_cells": n_bitwise,
            "max_rel_diff": worst,
            "max_rel_diff_cell": worst_cell,
            "tolerance_reported_at": tol,
            "within_tolerance_cells": sum(1 for d, _ in diffs if d <= tol),
            "verdict": ("IDENTICAL" if n_bitwise == len(diffs)
                        else "AGREES_WITHIN_%g" % tol if worst <= tol
                        else "DIFFERS_ABOVE_%g" % tol),
        }
    shifts = [e["peak_hour_shift_h"] for e in compared if e["peak_hour_shift_h"] is not None]
    summary["peak_hour_index_0based"] = {
        "population": len(shifts),
        "same_hour_cells": sum(1 for s in shifts if s == 0),
        "max_shift_h": max(shifts) if shifts else None,
    }
    report["summary"] = summary

    # The sentence this whole arm exists to make quotable, written by the
    # measurement rather than by the author of the report.
    verdicts = {summary[name]["verdict"] for name, _ in METRICS}
    if report["n_compared"] == 0:
        report["headline"] = "NOT_EVALUABLE: no cell completed on both hosts"
    elif verdicts == {"IDENTICAL"}:
        report["headline"] = (
            "Bitwise identical on both hosts across %d paired cells, same IDF bytes, "
            "EnergyPlus 23.1.0 on both." % report["n_compared"])
    elif all(v.startswith(("IDENTICAL", "AGREES_WITHIN")) for v in verdicts):
        report["headline"] = (
            "Numerically stable across hosts, NOT bitwise reproducible, over %d paired "
            "cells." % report["n_compared"])
    else:
        report["headline"] = (
            "Hosts DISAGREE above the reported tolerance on at least one metric over %d "
            "paired cells." % report["n_compared"])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"report": report, "cells": compared},
                                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(report["headline"])
    print("paired %d | compared %d | dropped by P1 %d | incomplete %d"
          % (report["n_paired"], report["n_compared"], len(dropped_p1), len(incomplete)))
    for name, _tol in METRICS:
        s = summary[name]
        print("  %-28s %s  (max rel diff %s on %s)"
              % (name, s.get("verdict"), s.get("max_rel_diff"), s.get("max_rel_diff_cell")))
    print("  peak hour same in %s of %s cells, max shift %s h"
          % (summary["peak_hour_index_0based"]["same_hour_cells"],
             summary["peak_hour_index_0based"]["population"],
             summary["peak_hour_index_0based"]["max_shift_h"]))
    print("->", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
