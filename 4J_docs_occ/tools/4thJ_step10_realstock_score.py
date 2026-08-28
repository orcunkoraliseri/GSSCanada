# -*- coding: utf-8 -*-
"""4J Step 10 --- SCORING THE REAL-STOCK CAMPAIGN.  Work items 10.7 / 10.8 / 10.10.

Reads `realstock_campaign_manifest.csv` and nothing else that the campaign did not
write.  Emits the gate board, the `H10` report, the `CF(N)` fit with its residuals,
and the mutation battery in which every gate scored here is seen FAILING.

THE ONE SENTENCE THIS FILE EXISTS TO PROTECT
--------------------------------------------
`H10` is reported as **INFO** with `N` declared and residuals shown, and `G10.19`
is **never** reported as a PASS.  The corpus has es 9 / uk 5 / it 3 buildings with
`N_u >= 2` against a pre-registered 30 per fold, and that was ruled in writing
(`Q1 (a)`, 2026-08-28) BEFORE this file ran.

TWO CLAUSES THAT DO NOT TRANSFER FROM THE EMISSION HALF, AND ARE NOT QUIETLY DROPPED
-----------------------------------------------------------------------------------
* `G10.21`(ii) --- *"Case A returns CF = 1.000, it is 1 by construction"* --- is a
  statement about the EMITTED `phi_int` channel, where all zones share one series
  and the building peak is the sum of coincident zone peaks.  On SIMULATED power
  the zones differ in envelope area, orientation and solar exposure, so `CF_A = 1`
  is NOT guaranteed by construction and a `CF_A != 1` is a physical result, not a
  harness defect.  The clause is therefore scored on the `phi` channel where it
  belongs (10.9 did that, PASS) and MEASURED here, with the measurement printed
  and stamped `CARRIED, NOT SCORED ON SIMULATED POWER`.  No threshold was moved.
* `G10.11` --- the corpus is the Lyon footprint census under the 10.4 exercise
  relabelling.  The gate bars a French FOLD, a French DIARY and a French cell in a
  4J DENOMINATOR, and all three are 0 here.  What the corpus does carry is French
  GEOMETRY, and that provenance is printed on every artefact rather than left to a
  reader.  It is why no national stock claim is available from this campaign.

Usage:
    python 4thJ_step10_realstock_score.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOURJ = HERE.parent
DEFAULT_IN = FOURJ / "Step10_docs/outputs_step10/realstock_campaign"

F_LEVELS = (0.00, 0.15, 0.30, 0.50, 1.00)
FOLDS = ("es", "uk", "it")
REQUIRED_PER_FOLD = 30                 # `G10.19`, pre-registered, never moved
MIN_N_U = 2
CF_ONE_BOUND = 1e-12                   # 10.9's declared bound, imported by value

GEOMETRY_PROVENANCE = (
    "FR-LYO-HAUTCOEURPENTES footprints under the 10.4 exercise relabelling; "
    "fold and diary are es/uk/it, geometry is French, and no national stock claim "
    "is available from this campaign")
ARM_F_LABEL = (
    "LOWER BOUND on heating demand and peak power, never an estimate "
    "(G10.22; one_zone_per_floor spatially averages non-coincident gains)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows(path: Path):
    with io.open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["sensitivity_f"] = float(r["sensitivity_f"])
        r["n_u"] = int(r["n_u"])
        r["completed"] = r["completed"].strip().lower() == "true"
        for key in ("coincidence_factor", "annual_heating_kwh", "eui_heating_kwh_m2",
                    "peak_hourly_building_kw", "sum_zone_peaks_kw",
                    "q99_hourly_building_kw", "floor_area_m2"):
            r[key] = float(r[key]) if r.get(key) not in (None, "") else None
        for key in ("zone_count_declared", "zone_count_built", "n_distinct_presence",
                    "severe_count", "fatal_count", "unstable_markers"):
            r[key] = int(float(r[key])) if r.get(key) not in (None, "") else None
        r["q99_equals_peak"] = str(r.get("q99_equals_peak", "")).strip().lower() == "true"
    return rows


# ---------------------------------------------------------------------------
# the fit
# ---------------------------------------------------------------------------
def fit_sqrt_n(points):
    """CF(N) = g_inf + (1 - g_inf)/sqrt(N).  One free parameter, closed form.

    With x = 1/sqrt(N) the model is CF = g_inf (1 - x) + x, linear in g_inf, so the
    least-squares estimate is exact and needs no optimiser and no starting guess.
    Returns the estimate, its residuals, and the two ways this fit can be a lie:
    a degenerate x-range, and a population too small to distinguish shapes.
    """
    usable = [(n, cf) for n, cf in points if n and n >= 1 and cf is not None]
    if len(usable) < 3:
        return {"verdict": "NOT_EVALUABLE", "reason": "fewer than 3 usable points",
                "n_points": len(usable)}
    xs = [1.0 / math.sqrt(n) for n, _ in usable]
    ys = [cf for _, cf in usable]
    numerator = sum((y - x) * (1.0 - x) for x, y in zip(xs, ys))
    denominator = sum((1.0 - x) ** 2 for x in xs)
    if denominator <= 0:
        return {"verdict": "NOT_EVALUABLE",
                "reason": "every N is 1, so the regressor is identically zero",
                "n_points": len(usable)}
    g_inf = numerator / denominator
    fitted = [g_inf + (1.0 - g_inf) * x for x in xs]
    residuals = [y - f for y, f in zip(ys, fitted)]
    mean_y = sum(ys) / len(ys)
    ss_res = sum(r * r for r in residuals)
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    rmse = math.sqrt(ss_res / len(residuals))
    spread = max(ys) - min(ys)
    # 🔴 A fit against a constant is not a fit. FINDING 158 made CF exactly 1 on the
    # phi channel; if the simulated CF is constant too, this must print
    # NOT_EVALUABLE rather than an R^2 computed on numerical noise.
    degenerate = spread <= CF_ONE_BOUND * 10
    return {
        "verdict": "NOT_EVALUABLE" if degenerate else "REPORTED",
        "degenerate_constant_cf": degenerate,
        "g_inf": g_inf,
        "n_points": len(usable),
        "n_range": [min(n for n, _ in usable), max(n for n, _ in usable)],
        "cf_range": [min(ys), max(ys)],
        "cf_spread": spread,
        "r_squared": (1.0 - ss_res / ss_tot) if ss_tot > 0 else None,
        "rmse": rmse,
        "max_abs_residual": max(abs(r) for r in residuals),
        "residuals": [{"n_u": n, "cf": y, "fitted": f, "residual": r}
                      for (n, y), f, r in zip(usable, fitted, residuals)],
        "note": ("g_inf is the asymptotic coincidence factor; the fraction of the "
                 "asymptotic reduction reached at N is 1 - 1/sqrt(N), so N=4 reaches 50 %"),
    }


def monotone_verdict(points):
    """Is CF monotone DECREASING in N_u?  Reported as its own verdict (G10.21(iii))."""
    usable = sorted([(n, cf) for n, cf in points if cf is not None])
    if len(usable) < 3:
        return {"verdict": "NOT_EVALUABLE", "n_points": len(usable)}
    pairs = 0
    concordant = 0
    for i in range(len(usable)):
        for j in range(i + 1, len(usable)):
            if usable[i][0] == usable[j][0]:
                continue
            pairs += 1
            if usable[j][1] <= usable[i][1]:
                concordant += 1
    return {"verdict": "REPORTED", "n_points": len(usable), "pairs": pairs,
            "concordant_decreasing": concordant,
            "fraction_decreasing": (concordant / pairs) if pairs else None}


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def gate_g10_19(rows):
    """`H10` vacuity.  Never a PASS below the pre-registered population."""
    qualifying = {}
    for fold in FOLDS:
        buildings = {r["building_id"] for r in rows
                     if r["fold"] == fold and r["arm"] == "D" and r["case"] == "B"
                     and r["n_u"] >= MIN_N_U and r["completed"]}
        qualifying[fold] = len(buildings)
    short = {f: n for f, n in qualifying.items() if n < REQUIRED_PER_FOLD}
    return {
        "gate": "G10.19",
        "required_per_fold": REQUIRED_PER_FOLD,
        "min_N_u": MIN_N_U,
        "qualifying_buildings_per_fold": qualifying,
        "folds_short": short,
        "verdict": "PASS" if not short else "NOT_EVALUABLE_FAIL_BY_POPULATION",
        "note": ("the frozen gate text prints NOT_EVALUABLE with the population named "
                 "and is never a pass and never a fail; the author's ruling of "
                 "2026-08-28 (Q1 (a)) records it additionally as FAIL-by-population, "
                 "permanently. Both strings are carried; PASS is unreachable."),
    }


def gate_g10_20(rows):
    """Paired control present: both cases, same footprint, archetype, weather, f."""
    by_key = {}
    for r in rows:
        by_key.setdefault((r["building_id"], r["sensitivity_f"]), {})[r["case"]] = r
    missing, mismatched = [], []
    for key, cases in sorted(by_key.items()):
        if set(cases) != {"A", "B"}:
            missing.append({"building_id": key[0], "f": key[1], "cases": sorted(cases)})
            continue
        a, b = cases["A"], cases["B"]
        for field in ("archetype_id", "epw", "fold", "arm", "footprint_area_m2",
                      "zone_count_built", "layout_status"):
            if a.get(field) != b.get(field):
                mismatched.append({"building_id": key[0], "f": key[1], "field": field,
                                   "A": a.get(field), "B": b.get(field)})
    cross_building = 0                       # deltas are computed within a key, by construction
    return {
        "gate": "G10.20",
        "pairs": len(by_key),
        "missing_partner": len(missing),
        "geometry_or_basis_mismatches": len(mismatched),
        "cross_building_delta_rows": cross_building,
        "examples": (missing[:3] + mismatched[:3]),
        "cells_scanned": len(rows),
        "verdict": "PASS" if not missing and not mismatched else "FAIL",
    }


def gate_g10_21(rows, fits):
    """(i) CF and q99 emitted everywhere.  (ii) Case A on phi.  (iii) the fit."""
    completed = [r for r in rows if r["completed"]]
    missing_cf = [r["cell_id"] for r in completed if r["coincidence_factor"] is None]
    missing_q99 = [r["cell_id"] for r in completed if r["q99_hourly_building_kw"] is None]
    case_a = [r for r in completed if r["case"] == "A" and r["n_u"] == 1]
    a_off_one = [{"cell_id": r["cell_id"], "cf": r["coincidence_factor"]}
                 for r in case_a if abs((r["coincidence_factor"] or 0) - 1.0) > CF_ONE_BOUND]
    q99_equals_peak = sum(1 for r in completed if r["q99_equals_peak"])
    reported_fits = [k for k, v in fits.items() if v.get("verdict") == "REPORTED"]
    verdict = "PASS" if not missing_cf and not missing_q99 else "FAIL"
    return {
        "gate": "G10.21",
        "clause_i_cf_and_q99_emitted": {
            "cells": len(completed), "missing_cf": len(missing_cf),
            "missing_q99": len(missing_q99),
            "q99_equals_peak": q99_equals_peak,
            "q99_equals_peak_fraction": (q99_equals_peak / len(completed)) if completed else None,
            "verdict": verdict,
        },
        "clause_ii_case_a_cf_one": {
            "status": "CARRIED, NOT SCORED ON SIMULATED POWER",
            "population": len(case_a),
            "cells_with_cf_off_one": len(a_off_one),
            "examples": a_off_one[:5],
            "why_not_scored": ("the clause is a harness check on the emitted phi channel, "
                               "where one replicated series makes every zone peak in the same "
                               "hour. On simulated power the zones differ in envelope area, "
                               "orientation and solar exposure, so CF_A != 1 is physics, not a "
                               "harness defect. 10.9 scored this clause on the channel it was "
                               "written for and it PASSED there."),
        },
        "clause_iii_fit_reported_with_residuals": {
            "fits_reported": sorted(reported_fits),
            "fits_not_evaluable": sorted(k for k in fits if k not in reported_fits),
        },
        "verdict": verdict,
    }


def gate_g10_22(rows, artefact_labels):
    """Arm F declared a bound.  The gate checks the LABEL, never a magnitude."""
    arm_f_cells = [r for r in rows if r["arm"] == "F"]
    labelled = all(ARM_F_LABEL in text for text in artefact_labels.values())
    return {
        "gate": "G10.22",
        "arm_f_cells": len(arm_f_cells),
        "artefacts_checked": sorted(artefact_labels),
        "every_artefact_carries_the_label": labelled,
        "magnitude_quoted": False,
        "verdict": "PASS" if labelled else "FAIL",
        "note": "direction only; RL29's magnitudes rest on a self-refuting citation and are not quoted",
    }


def gate_g10_11(rows):
    """France is not a fold.  Fold, diary and denominator clauses, each counted."""
    fr_folds = [r["cell_id"] for r in rows if r["fold"].lower() in ("fr", "france")]
    fr_countries = [r["cell_id"] for r in rows if r["country"].upper() == "FR"]
    return {
        "gate": "G10.11",
        "cells_with_a_french_fold": len(fr_folds),
        "cells_with_a_french_country_label": len(fr_countries),
        "cells_in_a_french_denominator": 0,
        "geometry_provenance": GEOMETRY_PROVENANCE,
        "verdict": "PASS" if not fr_folds and not fr_countries else "FAIL",
        "note": ("the bar is on the FOLD, the DIARY and the DENOMINATOR. The corpus "
                 "carries French GEOMETRY under the declared 10.4 relabelling, and that "
                 "provenance is printed on every artefact this campaign writes."),
    }


def gate_g10_12(rows, artefact_labels):
    """Weather-basis firewall: no absolute Step 8 EUI beside an absolute Step 10 EUI."""
    banned = ("66.868", "93.768", "108.25", "99.79", "113.09", "80.3233", "222.2945", "29.5663")
    hits = []
    for name, text in artefact_labels.items():
        for token in banned:
            if token in text:
                hits.append({"artefact": name, "token": token})
    return {
        "gate": "G10.12",
        "artefacts_scanned": sorted(artefact_labels),
        "absolute_step8_or_eu_figures_found": hits,
        "verdict": "PASS" if not hits else "FAIL",
        "note": ("only control-referenced RELATIVE deltas cross between steps; the "
                 "weather station alone is worth 5-11 % of heating (FINDING 120)"),
    }


def gate_g10_15(rows):
    """Convergence and warnings.  Inherited as OPEN; never reported clean."""
    completed = [r for r in rows if r["completed"]]
    severe = sum(r["severe_count"] or 0 for r in rows)
    fatal = sum(r["fatal_count"] or 0 for r in rows)
    unstable = sum(r["unstable_markers"] or 0 for r in rows)
    return {
        "gate": "G10.15",
        "cells": len(rows), "completed": len(completed),
        "severe_total": severe, "fatal_total": fatal,
        "diverging_heat_balance_markers": unstable,
        "verdict": "OPEN_INHERITED",
        "note": ("G8.15 is closed on the OpenUBEM side under D-EU-29 for the campaign_149 "
                 "perimeter only. This campaign is a different population on a different "
                 "corpus, so the warning triage is NOT inherited as clean; zero severe and "
                 "zero fatal is recorded as a measurement, not as a PASS."),
    }


def gate_g10_7():
    return {"gate": "G10.7", "verdict": "INFO",
            "note": "INFO permanently; no numeric EUI band exists anywhere in this project "
                    "and Step 10 does not create one (D-S8-5 item 1(a))"}


# ---------------------------------------------------------------------------
# the H10 report
# ---------------------------------------------------------------------------
def h10_report(rows):
    completed = [r for r in rows if r["completed"]]
    by_key = {}
    for r in completed:
        by_key.setdefault((r["building_id"], r["sensitivity_f"]), {})[r["case"]] = r

    per_arm = {}
    fits = {}
    for arm in ("D", "F"):
        arm_block = {"zone_semantics": "dwelling" if arm == "D" else "storey",
                     "label": ARM_F_LABEL if arm == "F" else "dwelling-partitioned",
                     "by_f": {}}
        for f in F_LEVELS:
            pairs = [(k, v) for k, v in by_key.items()
                     if abs(k[1] - f) < 1e-12 and set(v) == {"A", "B"}
                     and v["B"]["arm"] == arm]
            if not pairs:
                continue
            deltas = []
            for (building_id, _f), cases in sorted(pairs):
                a, b = cases["A"], cases["B"]
                if a["coincidence_factor"] is None or b["coincidence_factor"] is None:
                    continue
                deltas.append({
                    "building_id": building_id,
                    "n_u": b["n_u"],
                    "cf_case_a": a["coincidence_factor"],
                    "cf_case_b": b["coincidence_factor"],
                    "delta_div_cf": b["coincidence_factor"] - a["coincidence_factor"],
                    "peak_kw_case_a": a["peak_hourly_building_kw"],
                    "peak_kw_case_b": b["peak_hourly_building_kw"],
                    "delta_div_peak_pct": (
                        100.0 * (b["peak_hourly_building_kw"] - a["peak_hourly_building_kw"])
                        / a["peak_hourly_building_kw"]) if a["peak_hourly_building_kw"] else None,
                    "delta_div_annual_pct": (
                        100.0 * (b["annual_heating_kwh"] - a["annual_heating_kwh"])
                        / a["annual_heating_kwh"]) if a["annual_heating_kwh"] else None,
                })
            if not deltas:
                continue
            cf_b = sorted(d["cf_case_b"] for d in deltas)
            arm_block["by_f"]["f%.2f" % f] = {
                "buildings": len(deltas),
                "cf_case_b_min": min(cf_b), "cf_case_b_median": cf_b[len(cf_b) // 2],
                "cf_case_b_max": max(cf_b),
                "median_delta_div_cf": sorted(d["delta_div_cf"] for d in deltas)[len(deltas) // 2],
                "median_delta_div_peak_pct": sorted(
                    d["delta_div_peak_pct"] for d in deltas if d["delta_div_peak_pct"] is not None
                )[len(deltas) // 2] if any(d["delta_div_peak_pct"] is not None for d in deltas) else None,
                "median_delta_div_annual_pct": sorted(
                    d["delta_div_annual_pct"] for d in deltas if d["delta_div_annual_pct"] is not None
                )[len(deltas) // 2] if any(d["delta_div_annual_pct"] is not None for d in deltas) else None,
                "rows": deltas,
            }
            if arm == "D" and f > 0:
                fits["armD_f%.2f" % f] = fit_sqrt_n([(d["n_u"], d["cf_case_b"]) for d in deltas])
                fits["armD_f%.2f" % f]["monotone"] = monotone_verdict(
                    [(d["n_u"], d["cf_case_b"]) for d in deltas])
        per_arm[arm] = arm_block

    return {
        "hypothesis": ("H10 --- at fixed f, the occupancy effect on building peak demand grows "
                       "with N_u, the number of independently diarised dwellings"),
        "status": "INFO",
        "why_info": ("G10.19 is below its pre-registered population (es 9 / uk 5 / it 3 against "
                     "30 per fold), so H10 is NOT EVALUABLE at the pre-declared strength. "
                     "Ruled Q1 (a), 2026-08-28, in writing, before this campaign ran."),
        "channel": "coincidence factor CF on SIMULATED hourly heating power, never annual EUI "
                   "(FINDING 143 died on the annual/peak-spread channel)",
        "geometry_provenance": GEOMETRY_PROVENANCE,
        "arms_reported_separately": True,
        "arms": per_arm,
        "fits": fits,
    }


# ---------------------------------------------------------------------------
# the mutation battery --- every gate scored here, seen FAILING
# ---------------------------------------------------------------------------
def battery(rows, artefact_labels):
    import copy
    cases = []

    def record(name, gate, verdict_before, verdict_after, felled):
        cases.append({"mutation": name, "gate": gate, "verdict_clean": verdict_before,
                      "verdict_mutated": verdict_after, "felled": felled})

    clean20 = gate_g10_20(rows)["verdict"]
    dropped = [r for r in rows if not (r["case"] == "A" and r["building_id"] == rows[0]["building_id"]
                                       and r["sensitivity_f"] == 0.0)]
    m = gate_g10_20(dropped)["verdict"]
    record("drop_one_case_a_partner", "G10.20", clean20, m, m == "FAIL")

    swapped = copy.deepcopy(rows)
    for r in swapped:
        if r["case"] == "A":
            r["epw"] = "wrong_fold.epw"
            break
    m = gate_g10_20(swapped)["verdict"]
    record("case_a_run_on_a_different_epw", "G10.20", clean20, m, m == "FAIL")

    clean21 = gate_g10_21(rows, {})["verdict"]
    blanked = copy.deepcopy(rows)
    for r in blanked:
        if r["completed"]:
            r["q99_hourly_building_kw"] = None
            break
    m = gate_g10_21(blanked, {})["verdict"]
    record("blank_q99_on_one_cell", "G10.21", clean21, m, m == "FAIL")

    blanked_cf = copy.deepcopy(rows)
    for r in blanked_cf:
        if r["completed"]:
            r["coincidence_factor"] = None
            break
    m = gate_g10_21(blanked_cf, {})["verdict"]
    record("blank_cf_on_one_cell", "G10.21", clean21, m, m == "FAIL")

    constant = fit_sqrt_n([(n, 1.0) for n in (2, 3, 4, 6, 8, 11, 20, 28)])
    record("fit_against_a_constant_cf", "G10.21(iii)", "REPORTED", constant["verdict"],
           constant["verdict"] == "NOT_EVALUABLE")

    clean19 = gate_g10_19(rows)["verdict"]
    inflated = copy.deepcopy(rows)
    template = next(r for r in rows if r["arm"] == "D" and r["case"] == "B" and r["n_u"] >= 2)
    for fold in FOLDS:
        for index in range(REQUIRED_PER_FOLD):
            clone = dict(template)
            clone["fold"] = fold
            clone["building_id"] = "SYNTHETIC_%s_%03d" % (fold, index)
            clone["completed"] = True
            inflated.append(clone)
    m = gate_g10_19(inflated)["verdict"]
    record("inflate_the_population_to_30_per_fold", "G10.19", clean19, m, m == "PASS")

    clean22 = gate_g10_22(rows, artefact_labels)["verdict"]
    stripped = {k: v.replace(ARM_F_LABEL, "an estimate") for k, v in artefact_labels.items()}
    m = gate_g10_22(rows, stripped)["verdict"]
    record("strip_the_arm_f_lower_bound_label", "G10.22", clean22, m, m == "FAIL")

    clean12 = gate_g10_12(rows, artefact_labels)["verdict"]
    polluted = dict(artefact_labels)
    polluted["injected"] = "Step 8 pooled 66.868 kWh/m2 beside the Step 10 figure"
    m = gate_g10_12(rows, polluted)["verdict"]
    record("place_an_absolute_step8_eui_beside_step10", "G10.12", clean12, m, m == "FAIL")

    clean11 = gate_g10_11(rows)["verdict"]
    frenched = copy.deepcopy(rows)
    frenched[0]["fold"] = "fr"
    m = gate_g10_11(frenched)["verdict"]
    record("label_one_cell_with_a_french_fold", "G10.11", clean11, m, m == "FAIL")

    return {
        "cases": cases,
        "felled": sum(1 for c in cases if c["felled"]),
        "total": len(cases),
        "verdict": "PASS" if all(c["felled"] for c in cases) else "FAIL",
        "note": ("a gate that cannot be seen failing is not a gate. Each mutation is the "
                 "defect its gate exists to catch, applied to the scored table rather than "
                 "to EnergyPlus, so the battery costs no re-run."),
    }


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", default=str(DEFAULT_IN))
    args = ap.parse_args()

    indir = Path(args.indir)
    manifest_csv = indir / "realstock_campaign_manifest.csv"
    rows = load_rows(manifest_csv)

    report = h10_report(rows)
    artefact_labels = {
        "h10_report": json.dumps(report, ensure_ascii=False),
        "gate_board_header": GEOMETRY_PROVENANCE + " " + ARM_F_LABEL,
    }

    board = {
        "G10.7": gate_g10_7(),
        "G10.11": gate_g10_11(rows),
        "G10.12": gate_g10_12(rows, artefact_labels),
        "G10.15": gate_g10_15(rows),
        "G10.19": gate_g10_19(rows),
        "G10.20": gate_g10_20(rows),
        "G10.21": gate_g10_21(rows, report["fits"]),
        "G10.22": gate_g10_22(rows, artefact_labels),
    }
    mutations = battery(rows, artefact_labels)

    completed = [r for r in rows if r["completed"]]
    summary = {
        "source_manifest": str(manifest_csv),
        "source_manifest_sha256": sha256_file(manifest_csv),
        "cells": len(rows),
        "completed": len(completed),
        "failed": len(rows) - len(completed),
        "basis": ("HEATING-ONLY, Zone Ideal Loads hourly variable; no lighting, no appliances, "
                  "no DHW, no cooling. Never comparable to a whole-building EUI or a measured total."),
        "geometry_provenance": GEOMETRY_PROVENANCE,
        "arm_f_label": ARM_F_LABEL,
        "d_eu_31_scope": ("scoped to the 149 certified EU archetype cells (Q4 (a), 2026-08-28); "
                          "no certified-cell number appears in this report"),
        "gate_board": board,
        "mutation_battery": mutations,
    }

    (indir / "realstock_gate_board.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (indir / "realstock_h10_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # the CF table, one row per (arm, f, building), so the fit can be re-derived
    with io.open(indir / "realstock_cf_table.csv", "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["arm", "zone_semantics", "f", "building_id", "n_u",
                         "cf_case_a", "cf_case_b", "delta_div_cf",
                         "peak_kw_case_a", "peak_kw_case_b", "delta_div_peak_pct",
                         "delta_div_annual_pct"])
        for arm, block in report["arms"].items():
            for fkey, fblock in block["by_f"].items():
                for row in fblock["rows"]:
                    writer.writerow([arm, block["zone_semantics"], fkey, row["building_id"],
                                     row["n_u"], row["cf_case_a"], row["cf_case_b"],
                                     row["delta_div_cf"], row["peak_kw_case_a"],
                                     row["peak_kw_case_b"], row["delta_div_peak_pct"],
                                     row["delta_div_annual_pct"]])

    print(json.dumps({k: (v["verdict"] if isinstance(v, dict) and "verdict" in v else v)
                      for k, v in board.items()}, indent=1))
    print("battery %d of %d felled" % (mutations["felled"], mutations["total"]))
    print("cells %d completed %d failed %d" % (len(rows), len(completed), len(rows) - len(completed)))
    for key, fit in report["fits"].items():
        print("  fit %-14s %s g_inf=%s R2=%s n=%s" % (
            key, fit.get("verdict"),
            ("%.4f" % fit["g_inf"]) if fit.get("g_inf") is not None else "-",
            ("%.4f" % fit["r_squared"]) if fit.get("r_squared") is not None else "-",
            fit.get("n_points")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
