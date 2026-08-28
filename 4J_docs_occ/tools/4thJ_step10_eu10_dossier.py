"""EU-10 dossier export over the D-EU-28 ruled perimeter (149 marker-free cells).

Read-only over the OpenUBEM tree; nothing is simulated. Every number is read
from the retained campaign artefacts of `eu_certified_rerun_2026-08-28`.

Reporting bars carried into the dossier itself, not left to the reader:
  * `es` contributes nothing and is not quotable at any level (D-EU-28, rule 3).
  * `uk` may not be quoted at fold level or as nationally representative
    (D-EU-26: 17 of 36 archetypes refuse deterministically).
  * `it` is therefore the ONLY fold that survives both bars at fold level.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, "C:/Users/o_iseri/Desktop/OpenUBEM")

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "eu09", TOOLS / "4thJ_step10_eu09_scorer.py")
eu09 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eu09)

J_PER_KWH = 3_600_000.0
SCHEMA = "eu10-dossier-campaign/1.0-deu28"


def cell_record(cell_id: str, meta: dict) -> dict:
    man = eu09.load_manifest("rep1", cell_id)
    joules = eu09.hourly_series("rep1", cell_id)
    kwh = [value / J_PER_KWH for value in joules]
    monthly = eu09.monthly_from_hourly(kwh)
    peak = max(kwh)
    peak_hour = kwh.index(peak)
    geometry, tolerant = eu09.read_geometry_tolerant(
        Path(man["idf_path"]), man["archetype_id"])
    annual = sum(kwh)
    return {
        "cell_id": cell_id,
        "archetype_id": man["archetype_id"],
        "survey_fold": man["survey_fold"],
        "sensitivity_f": float(man["sensitivity_f"]),
        "weather_id": man["weather_id"],
        "weather_calendar_year": man["epw_calendar_year"],
        "annual_heating_kwh": annual,
        "monthly_heating_kwh": monthly,
        "peak_hourly_heating_kwh": peak,
        "peak_hour_index_0based": peak_hour,
        "denominator_area_m2": geometry.floor_area_m2,
        "storey_count": geometry.storey_count,
        "heating_eui_kwh_m2": annual / geometry.floor_area_m2,
        "geometry_readback": "tolerant" if tolerant else "strict",
        "manifest_heating_kwh": man["heating_kwh"],
        "hourly_sum_matches_manifest": abs(annual - float(man["heating_kwh"])) <= 1e-6 * max(annual, 1.0),
    }


def aggregate(records: list[dict]) -> dict:
    euis = [r["heating_eui_kwh_m2"] for r in records]
    area = sum(r["denominator_area_m2"] for r in records)
    energy = sum(r["annual_heating_kwh"] for r in records)
    return {
        "n_cells": len(records),
        "total_heating_kwh": energy,
        "total_denominator_area_m2": area,
        "area_pooled_heating_eui_kwh_m2": energy / area if area else None,
        "eui_kwh_m2_min": min(euis) if euis else None,
        "eui_kwh_m2_median": statistics.median(euis) if euis else None,
        "eui_kwh_m2_max": max(euis) if euis else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-report", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = eu09.load_table()
    perimeter, counts = eu09.derive_perimeter(rows)
    gate_report = json.loads(Path(args.gate_report).read_text(encoding="utf-8"))
    if gate_report["perimeter"]["n_cells"] != len(perimeter):
        raise SystemExit("gate report and dossier disagree about the perimeter")

    records = [cell_record(cid, meta) for cid, meta in sorted(perimeter.items())]
    mismatched = [r["cell_id"] for r in records if not r["hourly_sum_matches_manifest"]]

    by_fold: dict[str, list[dict]] = defaultdict(list)
    by_arch: dict[str, list[dict]] = defaultdict(list)
    levels: dict[tuple[str, str], set[float]] = defaultdict(set)
    for record in records:
        by_fold[record["survey_fold"]].append(record)
        by_arch[f"{record['survey_fold']}__{record['archetype_id']}"].append(record)
        levels[(record["survey_fold"], record["archetype_id"])].add(record["sensitivity_f"])

    five_f = sorted(f"{fold}__{arch}" for (fold, arch), fs in levels.items() if len(fs) == 5)
    five_f_by_fold: dict[str, int] = defaultdict(int)
    for key in five_f:
        five_f_by_fold[key.split("__")[0]] += 1

    f_sweep = []
    for key in five_f:
        fold, arch = key.split("__", 1)
        group = sorted(by_arch[key], key=lambda r: r["sensitivity_f"])
        base = next(r for r in group if r["sensitivity_f"] == 0.0)
        f_sweep.append({
            "fold": fold,
            "archetype_id": arch,
            "baseline_f0_annual_kwh": base["annual_heating_kwh"],
            "levels": [{
                "f": r["sensitivity_f"],
                "annual_heating_kwh": r["annual_heating_kwh"],
                "pct_vs_f0": 100.0 * (r["annual_heating_kwh"] - base["annual_heating_kwh"]) / base["annual_heating_kwh"],
                "peak_hourly_heating_kwh": r["peak_hourly_heating_kwh"],
                "peak_hour_index_0based": r["peak_hour_index_0based"],
            } for r in group],
        })

    gates = gate_report["gates"]
    dossier = {
        "schema_version": SCHEMA,
        "evidence_scope": (
            "D-EU-27 certified AND marker-free campaign cells, ruled quotable by D-EU-28 Option B on "
            "2026-08-28. 149 cells: uk 75, it 74, es 0. The intermediate certified count is 191 and is "
            "SUPERSEDED as a reporting perimeter."
        ),
        "source_campaign_table": str(eu09.CAMPAIGN_TABLE),
        "source_run_root": str(eu09.RUN_ROOT),
        "source_gate_report": str(Path(args.gate_report).resolve()),
        "n_cells": len(records),
        "by_fold_counts": {fold: len(items) for fold, items in sorted(by_fold.items())},
        "quotation_bars": {
            "es": "NOT QUOTABLE AT ANY LEVEL. Every certified es cell carries PsyPsatFnTemp in all three "
                  "replicates (FINDING 182); D-EU-28 rule 3.",
            "uk": "NO fold-level or nationally representative figure. D-EU-26 Option B: 17 of 36 uk "
                  "archetypes refuse deterministically on the S0 exterior-host check. Archetype-level and "
                  "within-archetype f comparisons only.",
            "it": "The only fold that survives both bars at fold level.",
            "cross_fold": "Any cross-fold absolute comparison must name the meteorological year in the same "
                          "sentence as the country (uk 2014, it 2014).",
        },
        "denominator_definition": (
            "Zone Floor Area read per archetype from that archetype's own saved IDF (V8.d), never carried "
            "across geometries."
        ),
        "end_use_accounting": {
            "eui_accounting_mode": "single_simulated_end_use_no_reconstruction",
            "simulated_end_uses": ["space heating (Zone Ideal Loads Zone Total Heating Energy, hourly)"],
            "not_simulated_end_uses": ["DHW", "cooking", "appliances", "lighting", "refrigeration",
                                       "elevators", "space cooling"],
            "reconstructed_end_uses": [],
            "note": "Neither §9.10 physical mode nor four-end-use mode applies: no service-load object is "
                    "emitted and no reconstruction table is applied, so no end use can be double counted. "
                    "Every EUI here is a HEATING-ONLY EUI and must never be compared against a whole-building "
                    "EUI or against a measured total.",
            "meters": "No Output:Meter exists in any campaign IDF; heating comes from the Zone Ideal Loads "
                      "hourly variable. G8.10/G8.11 are VACUOUS by construction.",
        },
        "hourly_sum_reconciles_to_manifest": {
            "n_cells_checked": len(records),
            "n_mismatched": len(mismatched),
            "mismatched": mismatched[:10],
        },
        "headline_heating_eui": {
            "it_fold_level": aggregate(by_fold.get("it", [])),
            "uk_archetype_level_only": {
                "n_cells": len(by_fold.get("uk", [])),
                "note": "aggregate withheld by D-EU-26; per-archetype records are in cells[]",
            },
            "all_perimeter_cells_informational": aggregate(records),
        },
        "f_sweep": {
            "supported_pairs": len(five_f),
            "by_fold": dict(five_f_by_fold),
            "note": "An f-sweep statement is supportable on these archetype x fold pairs and nowhere else.",
            "pairs": f_sweep,
        },
        "gate_summary": {
            "n_gates": len(gates),
            "PASS": sorted([g for g, v in gates.items() if v["status"] == "PASS"]),
            "FAIL": sorted([g for g, v in gates.items() if v["status"] == "FAIL"]),
            "VACUOUS": sorted([g for g, v in gates.items() if v["status"] == "VACUOUS"]),
            "reproducibility_disclaimer": gate_report["reproducibility_disclaimer"],
            "perturbation_coverage": {
                row["perturbation"]: row["status"] for row in gate_report["perturbation_coverage"]
            },
        },
        "findings_carried_forward": {
            "FINDING 181": "A cell can finish with return code 0 and be numerically meaningless; EnergyPlus "
                           "reports a diverging inside-surface heat balance as a Warning. Closed BY "
                           "CONSTRUCTION for uk and it; NOT closed for es. Stays OPEN.",
            "FINDING 182": "The D-EU-27 certification rule does not screen the .err instability markers. All "
                           "42 certified es cells carry marker_psy in all three replicates; marker_inside_hb "
                           "and marker_calchb are 0 on every certified cell, so marker_psy is perfectly "
                           "confounded with the es fold. Basis of D-EU-28.",
            "FINDING 183": "OpenUBEM's read_saved_idf_geometry requires V/(A*h) integral to abs_tol=1e-9, but "
                           "Zone.Ceiling_Height is serialized to 7 significant figures, so 2 of 39 perimeter "
                           "archetypes raise instead of reading. A reader tolerance defect, not a geometry "
                           "defect; the tolerant read-back is flagged per cell.",
            "G8.0": gates["G8.0"]["detail"],
            "G8.15": gates["G8.15"]["detail"],
        },
        "cells": records,
    }
    Path(args.out).write_text(json.dumps(dossier, indent=2), encoding="utf-8")
    print(f"cells={len(records)} folds={dossier['by_fold_counts']} "
          f"five_f={len(five_f)} {dict(five_f_by_fold)} mismatched={len(mismatched)}")
    print("it fold-level pooled heating EUI:",
          dossier["headline_heating_eui"]["it_fold_level"]["area_pooled_heating_eui_kwh_m2"])
    print("written:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
