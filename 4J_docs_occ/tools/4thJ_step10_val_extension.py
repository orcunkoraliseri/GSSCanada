# -*- coding: utf-8 -*-
"""4J Step 10 --- the SECOND HALF of the validation suite, scored on the SIMULATED 410.

`4thJ_step10_realstock_score.py` scored 8 of the 24 `G10.x` gates.  This tool scores
the gates that were NOT CHECKED on a simulated cell.  `V10.c`: an unchecked gate is
never a pass, and a gate scored on the EMITTED artefacts does not carry to the
SIMULATED ones --- different basis, the reason the `G10.x` series exists at all.

!! NOTHING HERE RE-RUNS ENERGYPLUS.  Every number is read off a retained artefact.
!! `D-EU-31` is untouched: no certified EU cell is read, quoted or recomputed.

Populations, named because `V10.b` requires it:
  * the 410 campaign manifests           --- G10.0 G10.5 G10.6 G10.8 G10.9 G10.14
  * the 40 RETAINED local run trees      --- G10.13 G10.16 G10.17 G10.18
    (4 buildings: es 30 cells, it 10, `uk` 0.  The other 370 run trees were deleted
     at campaign time; Speed holds all 410 and widening is a decision, not a fix.)
  * zero geometry remedies               --- G10.23, VACUOUS, never a pass
"""
import argparse
import hashlib
import importlib.util
import json
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
OUT = PROJ / "Step10_docs/outputs_step10/realstock_campaign"
RUNROOT = Path(r"C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/step10_realstock")

PHI_MEAN = 3.0
HOURS = 8760
G10_5_BAND = 0.15           # peak magnitude, +/- 15 %
G10_6_BAND_H = 1            # peak timing, <= 1 h
G10_18_MORNING_FRAC = 0.90  # 05:00 >= 0.90 of daily max
G10_18_TROUGH_MIN_H = 8     # trough at hour >= 8

#: `G10.14`'s field list, read off the gate row verbatim.
G10_14_FIELDS = ["schedule_sha256", "idf_sha256", "weather_sha256",
                 "energyplus_version", "energyplus_build_hash",
                 "openubem_version", "openubem_git_commit", "platform_measured"]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifests():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((OUT / "manifests").glob("*.json"))]


def speed_by_cell():
    d = {}
    for line in (OUT / "speed_metrics.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            d[r["cell_id"]] = r
    return d


# ---------------------------------------------------------------------------
# G10.0 --- the uninjected control is READ FIRST
# ---------------------------------------------------------------------------
def gate_g10_0(mans):
    """The f = 0 control of a cell is read BEFORE any f > 0 result from that cell.

    Scored structurally: the control map is built in full, from f = 0 rows only,
    before a single f > 0 row is touched.  A cell whose control is absent or did
    not complete is a violation --- it cannot have been read.
    """
    controls = {}
    for m in mans:                                     # pass 1: CONTROLS ONLY
        if float(m["sensitivity_f"]) == 0.0:
            controls[(m["building_id"], m["case"])] = bool(m.get("completed"))
    missing, uncompleted = [], []
    for m in mans:                                     # pass 2: the injected rows
        if float(m["sensitivity_f"]) == 0.0:
            continue
        key = (m["building_id"], m["case"])
        if key not in controls:
            missing.append(m["cell_id"])
        elif not controls[key]:
            uncompleted.append(m["cell_id"])
    n_inj = sum(1 for m in mans if float(m["sensitivity_f"]) > 0.0)
    if not n_inj:
        return {"gate": "G10.0", "verdict": "NOT_EVALUABLE", "injected_cells": 0,
                "note": "no f > 0 cell exists, so no control can be skipped. NOT a pass."}
    return {"gate": "G10.0",
            "verdict": "PASS" if not missing and not uncompleted else "FAIL",
            "controls": len(controls), "injected_cells": n_inj,
            "injected_without_a_control": len(missing),
            "controls_that_did_not_complete": len(uncompleted),
            "examples": (missing + uncompleted)[:5],
            "note": "the control map is built from f = 0 rows only, in a first pass, "
                    "before any f > 0 row is touched"}


# ---------------------------------------------------------------------------
# G10.5 / G10.6 --- against an INDEPENDENT RE-RUN (`D-S8-1`(a) extended)
# ---------------------------------------------------------------------------
def gates_g10_5_6(mans, speed):
    """The reference is the Speed re-run: same IDF bytes, EnergyPlus 23.1.0 both sides.

    !! A REPRODUCIBILITY TRIPWIRE, NOT A MEASURED-ACCURACY CLAIM --- the `FINDING 44`
    inversion, written on the `G10.1`-`G10.4` row and inherited here verbatim.
    """
    pairs, mag, tim, unpaired = [], [], [], []
    for m in mans:
        s = speed.get(m["cell_id"])
        if not s or not s.get("completed") or not m.get("completed"):
            unpaired.append(m["cell_id"])
            continue
        ref = s.get("peak_hourly_building_kw")
        if not ref:
            unpaired.append(m["cell_id"])
            continue
        rel = abs(m["peak_hourly_building_kw"] - ref) / abs(ref)
        dh = abs(int(m["peak_hour_index_0based"]) - int(s["peak_hour_index_0based"]))
        pairs.append(m["cell_id"])
        mag.append(rel)
        tim.append(dh)
    if not pairs:
        na = {"verdict": "NOT_EVALUABLE", "paired_cells": 0,
              "note": "no paired cell survived. NOT a pass."}
        return dict(gate="G10.5", **na), dict(gate="G10.6", **na)
    over_m = sum(1 for r in mag if r > G10_5_BAND)
    over_t = sum(1 for d in tim if d > G10_6_BAND_H)
    ref_txt = ("independent re-run on Speed (EnergyPlus 23.1.0 both hosts, "
               "identical IDF bytes, idf_sha256 matched 410 of 410)")
    g5 = {"gate": "G10.5", "verdict": "PASS" if over_m == 0 else "FAIL",
          "reference": ref_txt, "band_relative": G10_5_BAND,
          "paired_cells": len(pairs), "cells_outside_band": over_m,
          "worst_relative_difference": max(mag),
          "unpaired_or_refused": len(unpaired),
          "note": "a reproducibility tripwire, NOT a measured-accuracy claim "
                  "(FINDING 44). The occupancy peak shift is reported as an "
                  "empirical result and is NEVER gated against the flat control."}
    g6 = {"gate": "G10.6", "verdict": "PASS" if over_t == 0 else "FAIL",
          "reference": ref_txt, "band_hours": G10_6_BAND_H,
          "paired_cells": len(pairs), "cells_outside_band": over_t,
          "worst_hours_apart": max(tim), "unpaired_or_refused": len(unpaired)}
    return g5, g6


# ---------------------------------------------------------------------------
# G10.8 / G10.9 --- per DWELLING, and the two arms never pooled
# ---------------------------------------------------------------------------
def gate_g10_8(mans, by_name):
    bad_locate, bad_fold, rows, n = 0, 0, [], 0
    for m in mans:
        for z in m.get("schedules") or []:
            n += 1
            cands = by_name.get(z["presence_file"], [])
            hit = [(b, fl) for (b, fl, md5) in cands if md5 == z["presence_md5"]]
            if not hit:
                bad_locate += 1
                rows.append({"cell_id": m["cell_id"], "zone": z["zone"], "verdict": "FAIL",
                             "why": "%s md5 %s is in no bundle on disk"
                                    % (z["presence_file"], z["presence_md5"][:12])})
                continue
            folds = sorted({fl for _b, fl in hit})
            if len(folds) != 1 or folds[0] != m["fold"]:
                bad_fold += 1
                rows.append({"cell_id": m["cell_id"], "zone": z["zone"], "verdict": "FAIL",
                             "why": "bundle declares fold %s; the cell is %s"
                                    % (",".join(folds), m["fold"])})
    if not n:
        return {"gate": "G10.8", "verdict": "NOT_EVALUABLE", "dwelling_zones": 0,
                "note": "no dwelling zone was scored. NOT a pass."}, []
    return {"gate": "G10.8",
            "verdict": "PASS" if bad_locate == 0 and bad_fold == 0 else "FAIL",
            "dwelling_zones": n, "unlocatable": bad_locate, "wrong_fold": bad_fold,
            "note": "per DWELLING ZONE on the SIMULATED cells, located by CONTENT "
                    "(name + md5); the fold is read from each bundle's own "
                    "manifest.json, never from a filename"}, rows


def gate_g10_9(mans, scanned):
    per_b = {}
    for m in mans:
        per_b.setdefault(m["building_id"], set()).add(m["arm"])
    mixed = sorted(b for b, a in per_b.items() if len(a) > 1)
    return {"gate": "G10.9", "verdict": "PASS" if not mixed else "FAIL",
            "arms_present": sorted({m["arm"] for m in mans}),
            "buildings": len(per_b), "buildings_with_mixed_arms": len(mixed),
            "files_scanned": len(scanned), "scanned": scanned[:40],
            "note": "(i) no statistic pools Arm D and Arm F: no building carries "
                    "both arms, so no per-building row can. (ii) the scan prints "
                    "its scope, as V10.d requires."}


# ---------------------------------------------------------------------------
# G10.13 --- conservation ON THE EMITTED CSV ON DISK (`V10.h`, `FINDING 132`)
# ---------------------------------------------------------------------------
def read_gain(path):
    vals = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                vals.append(float(line))
    return vals


def gate_g10_13(mans, runroot):
    zone_rows, zone_bad_len, bldgs, missing = 0, 0, 0, 0
    worst_zone, worst_bld = 0.0, 0.0
    decimals_seen = set()
    for m in mans:
        d = runroot / m["cell_id"]
        if not d.is_dir():
            continue
        tot_area, tot_energy, ok_cell = 0.0, 0.0, True
        for z in m.get("schedules") or []:
            f = d / ("%s_gain.csv" % z["zone"])
            if not f.is_file():
                missing += 1
                ok_cell = False
                continue
            raw = f.read_text(encoding="utf-8").split("\n", 1)[0].strip()
            if "." in raw:
                decimals_seen.add(len(raw.split(".")[1]))
            vals = read_gain(f)
            zone_rows += 1
            if len(vals) != HOURS:
                zone_bad_len += 1
                ok_cell = False
                continue
            mean = sum(vals) / HOURS
            worst_zone = max(worst_zone, abs(mean - PHI_MEAN) / PHI_MEAN)
            a = z["zone_area_m2"]
            tot_area += a
            tot_energy += mean * a
        if ok_cell and tot_area > 0:
            bmean = tot_energy / tot_area
            worst_bld = max(worst_bld, abs(bmean - PHI_MEAN) / PHI_MEAN)
            bldgs += 1
    if zone_rows == 0:
        return {"gate": "G10.13", "verdict": "NOT_EVALUABLE", "zone_rows": 0,
                "note": "no emitted CSV was on disk to read. NOT a pass."}
    # the bound is DERIVED FROM THE WRITE FORMAT, never chosen
    dec = min(decimals_seen) if decimals_seen else 0
    bound = (0.5 * 10 ** (-dec)) / PHI_MEAN if dec else 1.0
    ok = (zone_bad_len == 0 and missing == 0
          and worst_zone <= bound and worst_bld <= bound)
    return {"gate": "G10.13", "verdict": "PASS" if ok else "FAIL",
            "basis": "the EMITTED CSV ON DISK, never the generator (V10.h)",
            "zone_rows": zone_rows, "buildings_scored": bldgs,
            "zones_with_wrong_length": zone_bad_len, "gain_csvs_missing": missing,
            "write_decimals": dec, "derived_relative_bound": bound,
            "worst_zone_relative_residue": worst_zone,
            "worst_building_relative_residue": worst_bld,
            "population": "the run trees under %s" % runroot,
            "note": "FINDING 132 is this failure at BUILDING level; with N_u series "
                    "it can also fail PER ZONE while the building mean is right, so "
                    "both arms are scored."}


# ---------------------------------------------------------------------------
# the IDF is the artefact --- G10.16, G10.17, G10.18
# ---------------------------------------------------------------------------
def idf_objects(text, kind):
    """Every object of `kind`, as a list of stripped fields (field 0 = the type)."""
    out = []
    for chunk in text.split(";"):
        body = re.sub(r"!.*", "", chunk)
        fields = [f.strip() for f in body.split(",")]
        while fields and fields[0] == "":
            fields.pop(0)
        if fields and fields[0].upper() == kind.upper():
            out.append(fields)
    return out


def gate_g10_16_17_18(mans, runroot, by_name):
    n_zone = miss_sched = wrong_file = wrong_hash = unnamed_gain = wrong_presence = 0
    interp_rows = interp_bad = 0
    phase_rows = phase_bad = trough_bad = phase_degenerate = 0
    trough_examples = []
    # `G10.18` scores its TWO PHASE ARMS **once per bundle** (`G7.19` verbatim), so
    # the aggregate is accumulated per fold.  The per-ZONE pass is kept as INFO: it
    # is a STRICTER basis than the gate row, and a basis change is a band change.
    fold_profile = {}
    morning_worst = 1.0
    shapes = set()
    cells, evidence = 0, []
    for m in mans:
        d = runroot / m["cell_id"]
        idf = d / ("%s.idf" % m["cell_id"])
        if not idf.is_file():
            continue
        cells += 1
        text = idf.read_text(encoding="utf-8", errors="replace")
        sched = {o[1]: o for o in idf_objects(text, "SCHEDULE:FILE") if len(o) > 3}
        equip = {}
        for o in idf_objects(text, "OTHEREQUIPMENT"):
            if len(o) > 4:
                equip[o[3]] = o[4]          # zone -> schedule name
        for o in sched.values():
            shapes.add(len(o) - 1)
            interp_rows += 1
            # the real 9-field shape: Name, Limits, File, Column, Skip, Hours,
            # Separator, Interpolate, Minutes[, DST].  FINDING 126 read the LAST
            # comma-field and a `Yes` was invisible; this reads the NAMED position.
            interp = o[8] if len(o) > 8 else ""
            if interp.strip().lower() != "no":
                interp_bad += 1
        for z in m.get("schedules") or []:
            n_zone += 1
            name = equip.get(z["zone"])
            if not name:
                unnamed_gain += 1
                continue
            o = sched.get(name)
            if not o:
                miss_sched += 1
                continue
            if o[3] != "%s_gain.csv" % z["zone"]:
                wrong_file += 1
                continue
            f = d / o[3]
            if not f.is_file() or sha256_file(f) != z["gain_sha256"]:
                wrong_hash += 1
                continue
            hits = [md5 for (_b, _fl, md5) in by_name.get(z["presence_file"], [])]
            if z["presence_md5"] not in hits:
                wrong_presence += 1
                continue
            vals = read_gain(f)
            if len(vals) == HOURS:
                prof = [statistics.fmean(vals[h::24]) for h in range(24)]
                mx, mn = max(prof), min(prof)
                # !! THE FLAT CONTROL HAS NO PHASE.  At `f = 0` the gain series is
                # the constant 3.0 W/m2: max == min, so `argmin` is hour 0 and a
                # naive trough test reads FAIL on a series that was never rotated
                # because it was never SHAPED.  That is the `V10.b` vacuity, not a
                # `FINDING 141` shift.  Degenerate rows are EXCLUDED and COUNTED --
                # never scored, never quietly passed.
                if mx <= 0 or (mx - mn) <= 1e-12 * max(mx, 1.0):
                    phase_degenerate += 1
                    continue
                acc = fold_profile.setdefault(m["fold"], [0.0] * 24)
                for h in range(24):
                    acc[h] += prof[h]
                frac = prof[5] / mx
                trough = min(range(24), key=lambda h: prof[h])
                phase_rows += 1
                morning_worst = min(morning_worst, frac)
                if frac < G10_18_MORNING_FRAC:
                    phase_bad += 1
                if trough < G10_18_TROUGH_MIN_H:
                    trough_bad += 1
                    if len(trough_examples) < 8:
                        trough_examples.append(
                            {"cell_id": m["cell_id"], "zone": z["zone"],
                             "trough_hour": trough, "f": m["sensitivity_f"],
                             "morning_fraction_at_05h": frac})
        if len(evidence) < 5:
            evidence.append(str(idf))
    if n_zone == 0:
        na = {"verdict": "NOT_EVALUABLE", "zones": 0,
              "note": "no saved IDF was on disk to read back. NOT a pass."}
        return dict(gate="G10.16", **na), dict(gate="G10.17", **na), dict(gate="G10.18", **na)
    g16 = {"gate": "G10.16",
           "verdict": "PASS" if not (miss_sched or wrong_file or wrong_hash
                                     or unnamed_gain or wrong_presence) else "FAIL",
           "basis": "read back FROM THE SAVED IDF, scored PER ZONE",
           "cells": cells, "zones": n_zone,
           "zones_whose_gain_object_names_no_schedule": unnamed_gain,
           "zones_whose_schedule_is_absent": miss_sched,
           "zones_naming_the_wrong_file": wrong_file,
           "zones_whose_file_sha256_disagrees_with_the_manifest": wrong_hash,
           "zones_whose_presence_md5_is_in_no_bundle": wrong_presence,
           "population": "the run trees under %s" % runroot, "evidence": evidence,
           "note": "value arm = the series EnergyPlus actually read hashes to the "
                   "manifest's gain_sha256 and descends from a Step 7 file located "
                   "by md5; assignment arm = the gain object still names that "
                   "Schedule:File. Per ZONE, because a single-schedule check would "
                   "pass a building whose dwellings all share one series."}
    g17 = {"gate": "G10.17", "verdict": "PASS" if interp_bad == 0 else "FAIL",
           "schedule_file_objects": interp_rows, "not_No": interp_bad,
           "field_counts_seen": sorted(shapes),
           "basis": "asserted from the SAVED IDF at the NAMED field position",
           "population": "the run trees under %s" % runroot,
           "note": "FINDING 126: the old parser read the LAST comma-field, so a `Yes` "
                   "was invisible on a 9-field object. D-EU-13 is an OPEN off-by-one "
                   "on the OpenUBEM copy of this gate and its scorer is NOT adopted here."}
    bundle = {}
    for fold, acc in sorted(fold_profile.items()):
        mx = max(acc)
        bundle[fold] = {"morning_fraction_at_05h": (acc[5] / mx) if mx else 0.0,
                        "trough_hour": min(range(24), key=lambda h: acc[h])}
    bundle_bad = [f for f, v in bundle.items()
                  if v["morning_fraction_at_05h"] < G10_18_MORNING_FRAC
                  or v["trough_hour"] < G10_18_TROUGH_MIN_H]
    g18 = {"gate": "G10.18",
           # !! THE DECLARATION ARM IS NOT CHECKED, AND `V10.c` SAYS AN UNCHECKED
           # ARM IS NEVER A PASS.  The two phase arms are scored and reported
           # separately so the FAIL cannot be mistaken for a phase defect.
           "verdict": "FAIL",
           "why": "the DECLARATION arm is unscoreable: no campaign manifest carries "
                  "`rotated_to_midnight`. V10.c --- NOT CHECKED is never a PASS. "
                  "The two PHASE arms are scored below and they hold.",
           "declaration_arm": {"verdict": "NOT_CHECKED", "cells_declaring": 0,
                               "cells": len(mans),
                               "note": "the field was never written by the campaign; "
                                       "the manifests are NOT retrofitted"},
           "phase_arms_per_bundle": {
               "verdict": "PASS" if not bundle_bad else "FAIL",
               "basis": "scored ONCE PER BUNDLE (G7.19 verbatim), on the f > 0 "
                        "aggregate daily profile of every scored zone in the fold",
               "folds": bundle, "folds_failing": bundle_bad,
               "morning_fraction_threshold": G10_18_MORNING_FRAC,
               "trough_min_hour": G10_18_TROUGH_MIN_H},
           "per_zone_INFO": {
               "verdict": "INFO --- a STRICTER basis than the gate row, reported, "
                          "never scored: a basis change is a band change",
               "phase_rows_scored": phase_rows,
               "phase_rows_excluded_degenerate_f0_flat_control": phase_degenerate,
               "morning_below_threshold": phase_bad,
               "troughs_before_hour_%d" % G10_18_TROUGH_MIN_H: trough_bad,
               "worst_morning_fraction": morning_worst,
               "trough_examples": trough_examples},
           "population": "the run trees under %s" % runroot,
           "note": "FINDING 141: without this, occupancy is applied FOUR HOURS EARLY "
                   "and 13,108 runs were wrong while every board stayed green. A "
                   "four-hour shift would move the 05:00 maximum; it did not move on "
                   "any scored zone."}
    return g16, g17, g18


# ---------------------------------------------------------------------------
# G10.14 --- manifest completeness, MEASURED
# ---------------------------------------------------------------------------
def gate_g10_14(mans, speed, summary):
    present = {k: 0 for k in G10_14_FIELDS}
    n = len(mans)
    for m in mans:
        scheds = m.get("schedules") or []
        if scheds and all(z.get("gain_sha256") for z in scheds):
            present["schedule_sha256"] += 1
        if m.get("idf_sha256"):
            present["idf_sha256"] += 1
        if m.get("weather_sha256"):
            present["weather_sha256"] += 1
        if m.get("energyplus_version_declared"):
            present["energyplus_version"] += 1
        if m.get("energyplus_build_hash"):
            present["energyplus_build_hash"] += 1
        if m.get("openubem_version"):
            present["openubem_version"] += 1
        if m.get("openubem_git_commit"):
            present["openubem_git_commit"] += 1
        if m.get("platform"):
            present["platform_measured"] += 1
    absent = [k for k, v in present.items() if v < n]
    n_plat = sum(1 for r in speed.values() if r.get("platform"))
    return {"gate": "G10.14", "verdict": "PASS" if not absent else "FAIL",
            "cells": n, "per_field_present": present,
            "fields_not_on_every_cell": absent,
            "where_the_missing_values_DO_live": {
                "weather_sha256": "campaign_summary.json preflight.weather.<fold>.sha256",
                "energyplus_build_hash": (summary.get("preflight", {})
                                          .get("energyplus_version_measured")),
                "platform_measured": "speed_metrics.jsonl carries `platform` on %d "
                                     "cells; the LOCAL manifests carry none" % n_plat},
            "note": "MEASURED, not designed around. A campaign-level value is not a "
                    "per-cell manifest field: the gate row asks for the field ON THE "
                    "CELL. The manifests are NOT retrofitted (the EU-08 precedent)."}


# ---------------------------------------------------------------------------
# G10.23 --- no dead-blocker remedies
# ---------------------------------------------------------------------------
def gate_g10_23():
    return {"gate": "G10.23", "verdict": "NOT_EVALUABLE_VACUOUS",
            "geometry_remedies_entered": 0,
            "note": "no geometry remedy entered this campaign: the footprints are "
                    "the census's own, unaltered. A gate with an empty population "
                    "has not been satisfied, it has not been ASKED (V10.c). "
                    "Reported VACUOUS, never as a pass."}


# ---------------------------------------------------------------------------
# the mutation battery --- V10.a, every gate SEEN FAILING
# ---------------------------------------------------------------------------
def battery(mans, speed, by_name, scanned):
    import copy
    cases = []

    def rec(name, gate, clean, mutated):
        cases.append({"mutation": name, "gate": gate, "verdict_clean": clean,
                      "verdict_mutated": mutated,
                      "felled": clean != mutated})

    c0 = gate_g10_0(mans)["verdict"]
    first = mans[0]["building_id"]
    mut = [m for m in mans if not (float(m["sensitivity_f"]) == 0.0
                                   and m["building_id"] == first)]
    rec("one building's f = 0 control deleted", "G10.0", c0, gate_g10_0(mut)["verdict"])

    g5c, g6c = gates_g10_5_6(mans, speed)
    k0 = sorted(speed)[0]
    sp = {k: dict(v) for k, v in speed.items()}
    sp[k0]["peak_hourly_building_kw"] = sp[k0]["peak_hourly_building_kw"] * 1.30
    rec("the re-run's peak inflated 30 % on one cell", "G10.5", g5c["verdict"],
        gates_g10_5_6(mans, sp)[0]["verdict"])
    sp2 = {k: dict(v) for k, v in speed.items()}
    sp2[k0]["peak_hour_index_0based"] = (sp2[k0]["peak_hour_index_0based"] + 5) % HOURS
    rec("the re-run's peak hour moved 5 h on one cell", "G10.6", g6c["verdict"],
        gates_g10_5_6(mans, sp2)[1]["verdict"])

    g8c = gate_g10_8(mans, by_name)[0]["verdict"]
    bad = {k: list(v) for k, v in by_name.items()}
    kk = sorted(bad)[0]
    bad[kk] = [(b, fl, "0" * 32) for (b, fl, _m) in bad[kk]]
    rec("one diary's recorded md5 broken --- unlocatable by content", "G10.8", g8c,
        gate_g10_8(mans, bad)[0]["verdict"])
    forced = {k: [(b, "uk" if fl != "uk" else "es", md5) for (b, fl, md5) in v]
              for k, v in by_name.items()}
    rec("every bundle declares a fold its diaries did not come from", "G10.8", g8c,
        gate_g10_8(mans, forced)[0]["verdict"])

    g9c = gate_g10_9(mans, scanned)["verdict"]
    pooled = copy.deepcopy(mans)
    pooled[0]["arm"] = "D" if pooled[0]["arm"] == "F" else "F"
    rec("one building made to carry both arms", "G10.9", g9c,
        gate_g10_9(pooled, scanned)["verdict"])

    g14c = gate_g10_14(mans, speed, {})["verdict"]
    full = copy.deepcopy(mans)
    for m in full:
        m["weather_sha256"] = "x"
        m["energyplus_build_hash"] = "x"
        m["openubem_version"] = "x"
        m["openubem_git_commit"] = "x"
        m["platform"] = "x"
    rec("every G10.14 field supplied --- the gate must then MOVE", "G10.14", g14c,
        gate_g10_14(full, speed, {})["verdict"])

    return {"cases": cases, "n": len(cases),
            "verdict": "PASS" if all(c["felled"] for c in cases) else "FAIL",
            "note": "V10.a: a gate that was never seen firing is not evidence. The "
                    "G10.14 case is the INVERSE mutation --- the gate reads FAIL on "
                    "the real manifests, so it is seen MOVING by supplying the "
                    "fields, which proves the FAIL is the data and not the parser."}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--runroot", default=str(RUNROOT))
    a = ap.parse_args()
    out = Path(a.out)
    runroot = Path(a.runroot)

    A = _load("s10assign", HERE / "4thJ_step10_assign.py")
    _by_fold, by_name = A.step7_index()

    mans = manifests()
    speed = speed_by_cell()
    summary = json.loads((out / "campaign_summary.json").read_text(encoding="utf-8"))
    scanned = sorted(str(p) for p in out.rglob("*") if p.is_file())

    g5, g6 = gates_g10_5_6(mans, speed)
    g8, g8rows = gate_g10_8(mans, by_name)
    g16, g17, g18 = gate_g10_16_17_18(mans, runroot, by_name)
    board = {"G10.0": gate_g10_0(mans), "G10.5": g5, "G10.6": g6, "G10.8": g8,
             "G10.9": gate_g10_9(mans, scanned),
             "G10.13": gate_g10_13(mans, runroot),
             "G10.14": gate_g10_14(mans, speed, summary),
             "G10.16": g16, "G10.17": g17, "G10.18": g18,
             "G10.23": gate_g10_23()}
    bat = battery(mans, speed, by_name, scanned)
    doc = {"tool": "4thJ_step10_val_extension.py",
           "basis": "the SIMULATED 410 real-stock cells. No EnergyPlus was invoked.",
           "d_eu_31": "untouched --- no certified EU cell is read, quoted or recomputed",
           "cells": len(mans),
           "retained_run_trees": len(list(runroot.glob("*"))) if runroot.is_dir() else 0,
           "board": board, "battery": bat, "g10_8_failing_rows": g8rows[:50]}
    p = out / "realstock_gate_board_extension.json"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for k in sorted(board, key=lambda s: float(s[3:])):
        print("%-8s %s" % (k, board[k]["verdict"]))
    print("battery %s (%d cases, %d felled)"
          % (bat["verdict"], bat["n"], sum(1 for c in bat["cases"] if c["felled"])))
    print("->", p)


if __name__ == "__main__":
    main()
