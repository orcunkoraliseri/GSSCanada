"""EU-09 scorer over the D-EU-28 ruled perimeter (149 marker-free certified cells).

Read-only over the OpenUBEM tree.  Nothing is simulated: the single re-run
budget is SPENT (D-EU-27), and every mutation below is applied to a COPY of a
retained artefact in a scratch directory, then re-scored.  No EnergyPlus run.

Bands and gate contracts are imported from OpenUBEM's single-source modules
(V8.c); this file never restates a threshold.

Perimeter rule (D-EU-28 Option B, ruled 2026-08-28):
    certified   = 3/3 replicates completed AND bitwise-identical heating_kwh
                  AND severe_count == 0 AND fatal_count == 0
    quotable    = certified AND marker-free in all three replicates
Expected: 149 cells (uk 75, it 74, es 0).  es is not quotable at all.

Usage:
    python 4thJ_step10_eu09_scorer.py --out <report.json>
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

OPENUBEM_ROOT = Path("C:/Users/o_iseri/Desktop/OpenUBEM")
sys.path.insert(0, str(OPENUBEM_ROOT))

from openubem.validation.step8_bands import STEP8_GATE_BANDS  # noqa: E402
from openubem.validation.step8_gates import (  # noqa: E402
    HARD_SEVERITY,
    PERTURBATION_MATRIX,
    GateFinding,
    audit_saved_idf_geometries,
    evaluate_peak_gates,
    evaluate_reproducibility_gates,
    evaluate_saved_idf_schedule_gates,
    evaluate_warning_gate,
    read_saved_idf_geometry,
)

CAMPAIGN_TABLE = (
    OPENUBEM_ROOT
    / "docs/docs_ACTIVE/europeanLocations/outputs/deu27_rerun_cells.csv"
)
RUN_ROOT = OPENUBEM_ROOT / "openubem/outputs/eu_certified_rerun_2026-08-28"
REPS = ("rep1", "rep2", "rep3")
DECLARED_CELLS = 510
MARKER_COLUMNS = ("marker_psy", "marker_inside_hb", "marker_calchb")
# No approved warning-kind list has ever been ruled (MVP caveat C-08); triage
# therefore runs against an empty approval set and G8.15 is expected to fail.
APPROVED_WARNING_KINDS: tuple[str, ...] = ()

VACUOUS = "VACUOUS"


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def load_table() -> list[dict[str, str]]:
    with CAMPAIGN_TABLE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def derive_perimeter(rows: list[dict[str, str]]) -> dict[str, dict]:
    """Re-derive certification and the marker-free filter from the table alone."""
    by_cell: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_cell[row["cell_id"]].append(row)

    certified: dict[str, dict] = {}
    counts = {"cells": len(by_cell), "runs": len(rows), "certified": 0, "marker_free": 0}
    for cell_id, reps in by_cell.items():
        if len(reps) != len(REPS):
            continue
        if not all(_truthy(r["completed"]) for r in reps):
            continue
        if any(int(r["severe_count"] or 0) or int(r["fatal_count"] or 0) for r in reps):
            continue
        values = {r["heating_kwh"] for r in reps}
        if len(values) != 1 or values == {"None"} or "" in values:
            continue
        counts["certified"] += 1
        marker_free = not any(_truthy(r[c]) for r in reps for c in MARKER_COLUMNS)
        if not marker_free:
            continue
        counts["marker_free"] += 1
        certified[cell_id] = {
            "cell_id": cell_id,
            "archetype_id": reps[0]["archetype_id"],
            "survey_fold": reps[0]["survey_fold"],
            "sensitivity_f": float(reps[0]["sensitivity_f"]),
            "heating_kwh": float(reps[0]["heating_kwh"]),
        }
    return certified, counts


def load_manifest(rep: str, cell_id: str) -> dict:
    path = RUN_ROOT / rep / "manifests" / f"{cell_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def hourly_series(rep: str, cell_id: str) -> list[float]:
    path = RUN_ROOT / rep / cell_id / "eplusout.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)
        return [float(row[1]) for row in reader if len(row) > 1 and row[1].strip()]


def monthly_from_hourly(series: list[float]) -> list[float]:
    """Aggregate 8760 hourly values into 12 calendar months (non-leap year)."""
    lengths = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    out, index = [], 0
    for days in lengths:
        hours = days * 24
        out.append(sum(series[index:index + hours]))
        index += hours
    return out


def finding(gate: str, passed: bool, detail: str) -> GateFinding:
    return GateFinding(gate, passed, detail, HARD_SEVERITY)


def read_geometry_tolerant(idf_path: Path, archetype_id: str):
    """V8.d read-back that survives a rounded serialized ceiling height.

    OpenUBEM's ``read_saved_idf_geometry`` requires ``V / (A * h)`` to be
    integral to ``abs_tol=1e-9``.  Two archetypes serialize ``Zone.Ceiling_Height``
    to 7 significant figures, so the quotient lands at 10.999998 / 7.999999 and
    the reader raises.  The geometry itself is fine; the tolerance is not.
    We fall back to the same positional parse with a relative tolerance and
    FLAG the cell, rather than skipping it or loosening anyone's gate.
    Reported to OpenUBEM as FINDING 183.
    """
    try:
        return read_saved_idf_geometry(idf_path, archetype_id), False
    except ValueError as exc:
        if "integral storey count" not in str(exc):
            raise
        from openubem.validation.step8_gates import _idf_objects_preserving_empty_fields
        objects = _idf_objects_preserving_empty_fields(idf_path.read_text(encoding="utf-8"))
        zone = [fields for kind, fields in objects if kind == "zone"][0]
        height, volume, area = float(zone[7]), float(zone[8]), float(zone[9])
        storeys_exact = volume / (area * height)
        storeys = round(storeys_exact)
        if abs(storeys_exact - storeys) > 1e-5 or storeys < 1:
            raise
        from openubem.validation.step8_gates import SavedIdfGeometry
        return SavedIdfGeometry(archetype_id, idf_path, area, volume, storeys), True


# --------------------------------------------------------------------------
# Gate scoring over the ruled perimeter
# --------------------------------------------------------------------------

def score_gates(perimeter: dict[str, dict]) -> tuple[dict, dict]:
    results: dict[str, dict] = {}
    manifests = {rep: {cid: load_manifest(rep, cid) for cid in perimeter} for rep in REPS}
    m1 = manifests["rep1"]

    # --- V8.g / G8.16: survey_fold present and matching the cell_id prefix ---
    fold_ok, fold_bad = 0, []
    for cid, man in m1.items():
        fold = man.get("survey_fold")
        if fold and cid.startswith(f"{fold}__"):
            fold_ok += 1
        else:
            fold_bad.append(cid)
    v8g = not fold_bad
    results["G8.16"] = {
        "status": "PASS" if v8g else "FAIL",
        "detail": f"survey_fold present and matches cell_id prefix on {fold_ok}/{len(m1)}",
        "n": len(m1),
    }

    # --- G8.0: every f>0 cell has a completed f=0 control in the same run ---
    ctrl_missing, ctrl_rep1_only, ctrl_outside_perimeter = [], [], []
    n_f0_cells = 0
    for cid, man in m1.items():
        if float(man["sensitivity_f"]) <= 0:
            continue
        n_f0_cells += 1
        control = man.get("control_cell_id", "")
        if not control:
            ctrl_missing.append(cid)
            continue
        states = []
        for rep in REPS:
            path = RUN_ROOT / rep / "manifests" / f"{control}.json"
            states.append(path.is_file() and load_manifest(rep, control).get("completed") is True)
        if not all(states):
            ctrl_missing.append(cid)
            if states[0]:
                ctrl_rep1_only.append(cid)
        if control not in perimeter:
            ctrl_outside_perimeter.append(cid)
    results["G8.0"] = {
        "status": "PASS" if not ctrl_missing and n_f0_cells else ("FAIL" if ctrl_missing else VACUOUS),
        "detail": f"{n_f0_cells - len(ctrl_missing)}/{n_f0_cells} f>0 perimeter cells have an f=0 control that "
                  f"completed in ALL THREE replicates - the same strictness the perimeter itself is defined at. "
                  f"{len(ctrl_rep1_only)} of the {len(ctrl_missing)} failures completed in replicate 1 and failed "
                  f"in a later replicate. Separately, {len(ctrl_outside_perimeter)}/{n_f0_cells} f>0 cells have an "
                  f"f=0 control that is NOT itself inside the ruled perimeter, so no f-versus-baseline difference "
                  f"may be quoted for those cells.",
        "n": n_f0_cells,
        "control_not_completed_3of3": ctrl_missing[:20],
        "control_outside_perimeter_count": len(ctrl_outside_perimeter),
    }

    # --- G8.8: distinct emitted schedule digests across f, within archetype x fold ---
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for cid, man in m1.items():
        groups[(man["survey_fold"], man["archetype_id"])].append(cid)
    scored, failed_groups, single = 0, [], 0
    for key, cids in groups.items():
        if len(cids) < 2:
            single += 1
            continue
        scored += 1
        digests = [m1[c].get("gain_csv_sha256") for c in cids]
        if len(set(digests)) != len(digests) or not all(digests):
            failed_groups.append("__".join(key))
    results["G8.8"] = {
        "status": "PASS" if scored and not failed_groups else ("FAIL" if failed_groups else VACUOUS),
        "detail": f"{scored - len(failed_groups)}/{scored} archetype x fold groups have distinct schedule digests per f "
                  f"({single} single-level groups excluded)",
        "n": scored,
    }

    # --- G8.9: no cache layer and no dependency digest was retained ---
    results["G8.9"] = {
        "status": VACUOUS,
        "detail": "each replicate executed into its own fresh run root; no cache was consulted and no "
                  "dependency_digest field exists in the retained manifests, so the stale-output guard has "
                  "no population",
        "n": 0,
    }

    # --- G8.10 / G8.11: no Output:Meter exists in any campaign IDF ---
    meter_counts = 0
    for cid in perimeter:
        text = (RUN_ROOT / "rep1" / "idfs" / f"{cid}.idf").read_text(encoding="utf-8")
        meter_counts += text.lower().count("output:meter")
    for gate in ("G8.10", "G8.11"):
        results[gate] = {
            "status": VACUOUS,
            "detail": f"0 Output:Meter objects across {len(perimeter)} perimeter IDFs "
                      f"(observed count {meter_counts}); heating comes from the Zone Ideal Loads hourly "
                      f"variable, never a meter. No meter population exists to score.",
            "n": 0,
        }

    # --- G8.12 / G8.13: independent saved-IDF read-back ---
    g12_fail, g13_fail, n_sched = [], [], 0
    for cid, man in m1.items():
        idf = Path(man["idf_path"])
        sched = Path(man["gain_csv_path"])
        name = f"EU_Step8_GainSchedule_{cid}_f{int(round(man['sensitivity_f'] * 100)):03d}"
        consumer = f"EU_Step8_InternalGain_{cid}_f{int(round(man['sensitivity_f'] * 100)):03d}"
        f12, f13 = evaluate_saved_idf_schedule_gates(
            idf,
            schedule_name=name,
            schedule_path=sched,
            schedule_sha256=man["gain_csv_sha256"],
            assignment_object_type="OtherEquipment",
            assignment_object_name=consumer,
        )
        n_sched += 1
        if not f12.passed:
            g12_fail.append(cid)
        if not f13.passed:
            g13_fail.append(cid)
    results["G8.12"] = {
        "status": "PASS" if not g12_fail else "FAIL",
        "detail": f"{n_sched - len(g12_fail)}/{n_sched} saved IDFs: Schedule:File path + measured file digest "
                  f"match the manifest AND the consuming OtherEquipment object names that schedule",
        "n": n_sched,
        "failing": g12_fail[:10],
    }
    results["G8.13"] = {
        "status": "PASS" if not g13_fail else "FAIL",
        "detail": f"{n_sched - len(g13_fail)}/{n_sched} saved Schedule:File objects carry Interpolate to Timestep = No",
        "n": n_sched,
        "failing": g13_fail[:10],
    }

    # --- G8.14: manifest completeness (immutable fields that exist on disk) ---
    required = ("cell_id", "created_utc", "idf_sha256", "openubem_git_commit", "energyplus_version")
    bad = [cid for cid, man in m1.items()
           if man.get("cell_id") != cid or not all(man.get(f) for f in required)]
    results["G8.14"] = {
        "status": "PASS" if not bad else "FAIL",
        "detail": f"{len(m1) - len(bad)}/{len(m1)} manifests are self-identifying and populated on "
                  f"{', '.join(required)}. NOTE: the retained manifests carry no `platform` field, so the "
                  f"platform arm of G8.14 is not scoreable here and is reported as a coverage gap.",
        "n": len(m1),
        "arms_not_scoreable": ["platform"],
    }

    # --- G8.15: warning triage by kind, against an empty approved set ---
    g15_fail, kinds_seen = [], set()
    for cid in perimeter:
        text = (RUN_ROOT / "rep1" / cid / "eplusout.err").read_text(encoding="utf-8", errors="replace")
        f15 = evaluate_warning_gate(text, APPROVED_WARNING_KINDS)
        if not f15.passed:
            g15_fail.append(cid)
            for part in f15.detail.split("untriaged=", 1)[-1].split("severe=")[0].split(","):
                if part.strip() and part.strip() != "none":
                    kinds_seen.add(part.strip())
    results["G8.15"] = {
        "status": "PASS" if not g15_fail else "FAIL",
        "detail": f"{len(g15_fail)}/{len(perimeter)} cells carry at least one untriaged warning kind. "
                  f"{len(kinds_seen)} distinct kinds; no approved_warning_kinds list has ever been ruled, so "
                  f"triage ran against an empty approval set. severe/fatal are 0 by the perimeter definition.",
        "n": len(perimeter),
        "distinct_kinds": sorted(kinds_seen),
    }

    # --- G8.1-G8.4 + G8.5/G8.6: reproducibility against the same cell's re-runs ---
    repro = {g: {"pass": 0, "fail": [], "worst": 0.0} for g in ("G8.1", "G8.2", "G8.3", "G8.4")}
    peaks = {g: {"pass": 0, "fail": []} for g in ("G8.5", "G8.6")}
    pairs = 0
    for cid in perimeter:
        s1 = hourly_series("rep1", cid)
        for rep in ("rep2", "rep3"):
            s2 = hourly_series(rep, cid)
            if len(s1) != len(s2) or len(s1) < 24:
                repro["G8.1"]["fail"].append(cid)
                continue
            pairs += 1
            fs = evaluate_reproducibility_gates(
                monthly_from_hourly(s1), monthly_from_hourly(s2), s1, s2,
            )
            for f in fs:
                if f.passed:
                    repro[f.gate]["pass"] += 1
                else:
                    repro[f.gate]["fail"].append(f"{cid}:{rep}")
            try:
                p5, p6 = evaluate_peak_gates(s1, s2, comparison_label=f"same-cell re-run ({rep})")
                for f in (p5, p6):
                    if f.passed:
                        peaks[f.gate]["pass"] += 1
                    else:
                        peaks[f.gate]["fail"].append(f"{cid}:{rep}")
            except ValueError:
                # a tied or non-unique peak is not a gate failure; it is an
                # unscoreable pair and is counted as such
                peaks["G8.5"].setdefault("unscoreable", []).append(f"{cid}:{rep}")
                peaks["G8.6"].setdefault("unscoreable", []).append(f"{cid}:{rep}")
    for gate, data in repro.items():
        results[gate] = {
            "status": "PASS" if data["pass"] == pairs and pairs else "FAIL",
            "detail": f"{data['pass']}/{pairs} replicate pairs within band "
                      f"({STEP8_GATE_BANDS[[k for k in STEP8_GATE_BANDS if k.startswith(gate + '.')][0]]}). "
                      f"Reference = a re-run of the same cell.",
            "n": pairs,
            "failing": data["fail"][:10],
        }
    for gate, data in peaks.items():
        uns = len(data.get("unscoreable", []))
        results[gate] = {
            "status": "PASS" if data["pass"] and not data["fail"] else ("FAIL" if data["fail"] else VACUOUS),
            "detail": f"{data['pass']}/{pairs - uns} replicate pairs within band; {uns} pairs had no unique "
                      f"positive peak and were not scoreable. Comparison series is the same cell's re-run, "
                      f"NOT a measured series.",
            "n": pairs - uns,
            "failing": data["fail"][:10],
        }

    # --- G8.7: no ruled as-modelled EUI band exists per TABULA archetype ---
    results["G8.7"] = {
        "status": VACUOUS,
        "detail": "G8.7 grades an as-modelled published band per archetype. No such band has been ruled for "
                  "the TABULA archetypes of this campaign, so there is nothing to grade against. The geometry "
                  "identity arm that perturbation 11 targets IS exercised, under V8.d.",
        "n": 0,
    }

    # --- V8.d: per-archetype geometry read back from that archetype's own IDF ---
    geom = {}
    geom_fallback: set[str] = set()
    for cid, man in m1.items():
        arch = man["archetype_id"]
        g, fell_back = read_geometry_tolerant(Path(man["idf_path"]), arch)
        if fell_back:
            geom_fallback.add(arch)
        prev = geom.get(arch)
        geom[arch] = g
        if prev is not None and (
            abs(prev.floor_area_m2 - g.floor_area_m2) > 1e-9
            or abs(prev.volume_m3 - g.volume_m3) > 1e-9
            or prev.storey_count != g.storey_count
        ):
            raise AssertionError(f"V8.d: geometry differs between cells of archetype {arch}")
    guards = {
        "V8.a": {"passed": len(m1) == len(perimeter),
                 "detail": f"scorer read {len(m1)} cells; ruled perimeter declares {len(perimeter)} "
                           f"(campaign declares {DECLARED_CELLS} cells before D-EU-26/27/28)"},
        "V8.b": {"passed": True,
                 "detail": f"perimeter and scoring both read {CAMPAIGN_TABLE}"},
        "V8.c": {"passed": True,
                 "detail": "bands imported from openubem.validation.step8_bands; no threshold restated here"},
        "V8.d": {"passed": True,
                 "detail": f"area/volume/storeys read per archetype from that archetype's own saved IDF "
                           f"({len(geom)} archetypes); consistent across every cell of the archetype. "
                           f"{len(geom_fallback)} archetypes needed the tolerant read-back "
                           f"({', '.join(sorted(geom_fallback)) or 'none'}) because Zone.Ceiling_Height is "
                           f"serialized to 7 significant figures and OpenUBEM's reader demands an integral "
                           f"V/(A*h) to abs_tol=1e-9 - FINDING 183, reader tolerance, not a geometry defect",
                 "tolerant_readback_archetypes": sorted(geom_fallback)},
        "V8.e": {"passed": True, "detail": "every GateFinding produced here is hard severity"},
        "V8.f": {"passed": True, "detail": "G8.15 triages by warning kind, never by frequency"},
        "V8.g": {"passed": v8g,
                 "detail": f"survey_fold present on {fold_ok}/{len(m1)} manifests, so G8.16 is scored rather than forced to FAIL"},
    }
    return results, guards


# --------------------------------------------------------------------------
# Table 17 coverage — every gate must be seen failing
# --------------------------------------------------------------------------

def score_coverage(perimeter: dict[str, dict], scratch: Path) -> list[dict]:
    """Mutate COPIES of retained artefacts and re-score. No simulation is run."""
    m1 = {cid: load_manifest("rep1", cid) for cid in perimeter}
    # pick an archetype x fold group with at least two f levels
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for cid, man in m1.items():
        groups[(man["survey_fold"], man["archetype_id"])].append(cid)
    def strict_readable(cell_id: str) -> bool:
        man_ = m1[cell_id]
        try:
            read_saved_idf_geometry(Path(man_["idf_path"]), man_["archetype_id"])
            return True
        except ValueError:
            return False

    group = sorted(next(cids for cids in groups.values()
                        if len(cids) >= 2 and strict_readable(cids[0])))
    cell = group[-1]
    other = sorted(c for c in m1 if c not in group and strict_readable(c))[0]
    man = m1[cell]
    f_token = f"f{int(round(man['sensitivity_f'] * 100)):03d}"
    sched_name = f"EU_Step8_GainSchedule_{cell}_{f_token}"
    consumer = f"EU_Step8_InternalGain_{cell}_{f_token}"
    idf_src = Path(man["idf_path"])
    sched_src = Path(man["gain_csv_path"])

    def schedule_gates(idf: Path, name: str = sched_name, cons: str = consumer) -> dict[str, bool]:
        f12, f13 = evaluate_saved_idf_schedule_gates(
            idf, schedule_name=name, schedule_path=sched_src,
            schedule_sha256=man["gain_csv_sha256"],
            assignment_object_type="OtherEquipment", assignment_object_name=cons,
        )
        return {"G8.12": f12.passed, "G8.13": f13.passed}

    def g88(digests: list[str]) -> bool:
        return len(set(digests)) == len(digests) and all(digests)

    def g814(manifest: dict, cell_id: str) -> bool:
        return manifest.get("cell_id") == cell_id and all(
            manifest.get(f) for f in ("cell_id", "created_utc", "idf_sha256"))

    def g816(manifest: dict, cell_id: str) -> bool:
        fold = manifest.get("survey_fold")
        return bool(fold) and cell_id.startswith(f"{fold}__")

    base_digests = [m1[c]["gain_csv_sha256"] for c in group]
    base_sched = schedule_gates(idf_src)
    s1 = hourly_series("rep1", cell)
    s2 = hourly_series("rep2", cell)
    base_repro = {f.gate: f.passed for f in evaluate_reproducibility_gates(
        monthly_from_hourly(s1), monthly_from_hourly(s2), s1, s2)}
    base_peak = {f.gate: f.passed for f in evaluate_peak_gates(
        s1, s2, comparison_label="same-cell re-run (rep2)")}
    geom_base = read_saved_idf_geometry(idf_src, man["archetype_id"])

    baseline = {
        "G8.8": g88(base_digests),
        "G8.12": base_sched["G8.12"],
        "G8.12.value": _value_arm(idf_src, sched_name, sched_src, man["gain_csv_sha256"]),
        "G8.12.assignment": base_sched["G8.12"],
        "G8.13": base_sched["G8.13"],
        "G8.14": g814(man, cell),
        "G8.16": g816(man, cell),
        "G8.1": base_repro["G8.1"], "G8.3": base_repro["G8.3"],
        "G8.5": base_peak["G8.5"], "G8.6": base_peak["G8.6"],
    }

    probes: dict[str, dict[str, bool]] = {}

    # P01 - two f levels driven by the same schedule file
    probes["P01"] = {"G8.8": g88([base_digests[0]] * len(base_digests))}

    # P05 - the consuming object points at a different schedule
    mutated = scratch / "p05.idf"
    text = idf_src.read_text(encoding="utf-8")
    other_name = f"EU_Step8_GainSchedule_{other}_f{int(round(m1[other]['sensitivity_f'] * 100)):03d}"
    p05_text = text.replace(
        f"    {sched_name},    !- Schedule Name",
        f"    {other_name},    !- Schedule Name",
    )
    assert p05_text != text, "P05 mutation did not apply"
    mutated.write_text(p05_text, encoding="utf-8")
    p05 = evaluate_saved_idf_schedule_gates(
        mutated, schedule_name=sched_name, schedule_path=sched_src,
        schedule_sha256=man["gain_csv_sha256"],
        assignment_object_type="OtherEquipment", assignment_object_name=consumer)
    # value arm = the Schedule:File object itself is untouched; only the
    # consuming object was re-pointed, so the assignment arm must fall alone
    p05_value = _value_arm(mutated, sched_name, sched_src, man["gain_csv_sha256"])
    probes["P05"] = {"G8.12.assignment": p05[0].passed, "G8.12.value": p05_value}

    # P06 - Interpolate to Timestep = Yes
    mutated = scratch / "p06.idf"
    p06_text = text.replace("    No,                       !- Interpolate to Timestep",
                            "    Yes,                      !- Interpolate to Timestep")
    assert p06_text != text, "P06 mutation did not apply"
    mutated.write_text(p06_text, encoding="utf-8")
    p06 = schedule_gates(mutated)
    probes["P06"] = {"G8.13": p06["G8.13"], "G8.12": p06["G8.12"]}

    # P07 - another cell's manifest copied wholesale
    probes["P07"] = {"G8.14": g814(m1[other], cell), "G8.12": base_sched["G8.12"]}

    # P08 - the cell is driven by a fold that did not hold its country out
    wrong = dict(man)
    wrong["survey_fold"] = "it" if man["survey_fold"] != "it" else "uk"
    probes["P08"] = {"G8.16": g816(wrong, cell), "G8.12": base_sched["G8.12"],
                     "G8.14": g814(man, cell)}

    # P09 - modelled profile shifted two hours later
    shifted = s2[-2:] + s2[:-2]
    p09 = {f.gate: f.passed for f in evaluate_peak_gates(
        s1, shifted, comparison_label="same-cell re-run, shifted 2 h")}
    probes["P09"] = {"G8.6": p09["G8.6"], "G8.5": p09["G8.5"]}

    # P10 - annual energy scaled by 1.2
    scaled = [v * 1.2 for v in s2]
    p10r = {f.gate: f.passed for f in evaluate_reproducibility_gates(
        monthly_from_hourly(s1), monthly_from_hourly(scaled), s1, scaled)}
    p10p = {f.gate: f.passed for f in evaluate_peak_gates(
        s1, scaled, comparison_label="same-cell re-run, scaled 1.2")}
    probes["P10"] = {"G8.1": p10r["G8.1"], "G8.3": p10r["G8.3"], "G8.6": p10p["G8.6"]}

    # P11 - geometry taken from a different archetype (V8.d arm)
    other_geom = read_saved_idf_geometry(Path(m1[other]["idf_path"]), m1[other]["archetype_id"])
    v8d_probe = audit_saved_idf_geometries(
        {man["archetype_id"]: idf_src},
        {man["archetype_id"]: {"floor_area_m2": other_geom.floor_area_m2,
                               "volume_m3": other_geom.volume_m3,
                               "storey_count": other_geom.storey_count}},
    )
    v8d_base = audit_saved_idf_geometries(
        {man["archetype_id"]: idf_src},
        {man["archetype_id"]: {"floor_area_m2": geom_base.floor_area_m2,
                               "volume_m3": geom_base.volume_m3,
                               "storey_count": geom_base.storey_count}},
    )

    # P12 - null perturbation
    probes["P12"] = dict(baseline)

    report = []
    for expectation in PERTURBATION_MATRIX:
        pid = expectation.identifier
        if pid in ("P02", "P03", "P04"):
            reason = ("no cache layer and no dependency_digest was retained"
                      if pid == "P02" else
                      "no Output:Meter exists in any campaign IDF, so the meter gates have no population")
            report.append({"perturbation": pid, "status": VACUOUS,
                           "description": expectation.description, "detail": reason})
            continue
        if pid == "P11":
            passed = (not v8d_probe[0].passed) and v8d_base[0].passed
            report.append({
                "perturbation": pid, "status": "PASS" if passed else "FAIL",
                "description": expectation.description,
                "detail": ("G8.7 has no ruled band and is VACUOUS; the geometry identity arm this row "
                           "targets was exercised under V8.d instead: borrowed geometry FAILs "
                           f"({v8d_probe[0].detail}) while the archetype's own geometry passes"),
            })
            continue
        probe = probes[pid]
        if pid == "P12":
            missing = [g for g, ok in probe.items() if not ok]
            report.append({"perturbation": pid,
                           "status": "PASS" if not missing else "FAIL",
                           "description": expectation.description,
                           "detail": f"null perturbation leaves {len(probe) - len(missing)}/{len(probe)} "
                                     f"baseline checkpoints clean"})
            continue
        missing_failures = [g for g in expectation.must_fail
                            if not baseline.get(g, False) or probe.get(g, True)]
        clean_scoreable = [g for g in expectation.must_stay_clean if g in baseline]
        clean_vacuous = [g for g in expectation.must_stay_clean if g not in baseline]
        dirty = [g for g in clean_scoreable if not probe.get(g, False)]
        report.append({
            "perturbation": pid,
            "status": "PASS" if not missing_failures and not dirty else "FAIL",
            "description": expectation.description,
            "detail": f"must_fail={list(expectation.must_fail)} not_seen_falling={missing_failures}; "
                      f"must_stay_clean={clean_scoreable} dirtied={dirty}; "
                      f"clean_arms_with_no_population={clean_vacuous}",
        })
    return report


def _value_arm(idf: Path, sched_name: str, sched_path: Path, digest: str) -> bool:
    """G8.12 value arm alone: the Schedule:File path and file digest still match.

    Parsed with OpenUBEM's own independent IDF reader, so the value arm is
    evaluated exactly as the gate evaluates it, minus the assignment clause.
    """
    from openubem.validation.step8_gates import _idf_objects, _sha256_file

    expected = str(sched_path).replace("\\", "/").casefold()
    objects = _idf_objects(idf.read_text(encoding="utf-8"))
    matching = [
        fields for kind, fields in objects
        if kind == "schedule:file" and len(fields) >= 8
        and fields[0].casefold() == sched_name.casefold()
        and fields[2].replace("\\", "/").casefold() == expected
    ]
    return bool(matching) and sched_path.is_file() and _sha256_file(sched_path) == digest.casefold()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = load_table()
    perimeter, counts = derive_perimeter(rows)
    print(f"table rows={counts['runs']} cells={counts['cells']} "
          f"certified={counts['certified']} marker_free={counts['marker_free']}")
    by_fold = defaultdict(int)
    for cell in perimeter.values():
        by_fold[cell["survey_fold"]] += 1
    print("perimeter by fold:", dict(by_fold))

    gates, guards = score_gates(perimeter)
    scratch = Path(tempfile.mkdtemp(prefix="eu09_"))
    try:
        coverage = score_coverage(perimeter, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    report = {
        "work_package": "EU-09",
        "ruling": "D-EU-28 Option B, ruled 2026-08-28 by the OpenUBEM owner",
        "perimeter": {
            "definition": "certified (3/3 completed, bitwise-identical heating_kwh, severe=0, fatal=0) "
                          "AND marker-free in all three replicates",
            "n_cells": len(perimeter),
            "by_fold": dict(by_fold),
            "certified_intermediate_count": counts["certified"],
            "campaign_table": str(CAMPAIGN_TABLE),
            "run_root": str(RUN_ROOT),
        },
        "reproducibility_disclaimer": (
            "G8.1-G8.4 are reproducibility gates. They compare a cell against a re-run of itself. They are "
            "not a validation of simulated energy against measured energy, and no such validation is claimed "
            "anywhere in this paper."
        ),
        "gates": gates,
        "vacuity_guards": guards,
        "perturbation_coverage": coverage,
    }
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    for gate in sorted(gates, key=lambda g: (len(g), g)):
        print(f"{gate:6s} {gates[gate]['status']:8s} n={gates[gate]['n']}")
    for row in coverage:
        print(f"{row['perturbation']} {row['status']}")
    print("written:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
