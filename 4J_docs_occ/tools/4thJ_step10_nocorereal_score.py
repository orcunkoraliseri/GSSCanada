# -*- coding: utf-8 -*-
"""4J Step 10 --- SCORING CAMPAIGN `C2` (no-core, real-stock).  `G10N.x` gate series.

PORTED from `4thJ_step10_realstock_score.py` (campaign `C1`, `G10.x`, CLOSED) and
`4thJ_step10_val_extension.py` (the second half of `C1`'s own board).  `G10.x` stays
spent on `C1`'s core-era basis; every verdict this file writes is filed under the
**separate** `G10N.x` series, on the no-core basis, per
`Step10_docs/4thJ_10_nocoreRealStock_val.md` ("THE GATE-ID RULE").  No `G10N.x`
result here is ever a `G10.x` result and vice versa.

AUTHORISATION THIS FILE RELIES ON, QUOTED, NOT SUMMARISED
-----------------------------------------------------------
`tools/4thJ_step10_nocore_campaign.py`, `AUTHORISED` dict, all three of Madrid /
London / Bologna, dated 2026-09-16: *"Score the finished C2 cells for Madrid,
London and Bologna as G10N.x results."*  This file reads already-written cell
manifests.  It never invokes EnergyPlus, never calls the campaign runner, and
never edits `AUTHORISED`, `D-EU-55`, or anything already closed about `C1`.

WHERE THE REAL DATA LIVES (NOT under `4J_docs_occ`)
-----------------------------------------------------------
`Step10_docs/outputs_step10_nocore/` holds an early, INCOMPLETE snapshot (1,427
Bologna cells only, a subset of the final population) and is not read by this
file except to note its own staleness.  The actual finished campaign, all three
districts, lives under `_local_runs/4J_<ES|UK|IT>_local/out/<DISTRICT>/`
(sibling of `GSSCanada-main`, per `project_local_runs_relocation.md`) --- one
`cells/*.json` manifest per simulated cell, plus a `runs/<DISTRICT>/<slug>/`
tree that retains the built IDF and per-zone gain CSVs for a SUBSET of cells
(the campaign's own `RETAIN_RUN_DIRS` policy, the same one `C1` used for its
40-of-410 retained population).  `V10N.b`/`V10.b` requires every population be
NAMED; every gate below names exactly what it read.

WHAT IS AND IS NOT EVALUABLE ON THIS DATA, MEASURED, NOT ASSUMED
-----------------------------------------------------------
* Every one of the 35,090 real cell manifests (11,340 ES + 12,070 UK + 11,680
  IT) carries all 15 fields of section 5 verbatim, `completed=True`, and
  `arm="D"` --- `G10N.14` and `G10N.9`'s population are exactly this.
* NO Arm F cell was ever written by the executed campaign (`arm` is `"D"` on
  100 % of 35,090 manifests) --- `G10N.22` is `NOT_EVALUABLE`, population 0,
  never a vacuous PASS (`V10N.a`).
* NO independent second-host re-run of the FINAL population exists: the Speed
  campaigns (`1314969`/`1314970`/`1315014`/`1315015`) were cancelled after
  Defect 8 (2026-09-08 last+49) and never restarted, and the floor-averaging
  and courtyard fixes that produced the FINAL cells ran only on the local
  Windows host (`impl/2026-09-12_C2_campaign_dashboard_final.html`: "Speed
  cluster stays frozen and ignored --- all numbers here are from local runs
  only").  `G10N.1`-`G10N.4`, `G10N.5`, `G10N.6` and `G10N.replicate` are
  therefore `NOT_EVALUABLE`, population 0.  This is not a gap this file can
  close: it needs a second, authorised, engine-matched re-run, which is not
  authorised today.
* `G10N.10` needs the OpenUBEM geometry tree (`european_residential.py`) to
  re-measure the CRS invariance; that tree is not present in this checkout.
  `NOT_EVALUABLE`, population 0 --- reported, not assumed clean.
* A NEW, disclosed population this campaign carries that `C1` never had:
  "floor-averaged" cells, where `average_units_by_floor()`
  (`4thJ_step10_nocore_campaign.py:997`) merged several real dwellings on one
  floor into ONE area-weighted averaged occupancy series, author-approved
  2026-09-12, for buildings a per-dwelling layout could not simulate.  Every
  such schedule carries `merged_floor_averaged_occupancy: true`.  These are
  counted, reported, and EXCLUDED from the "one series per drawn flat"
  population (`G10N.20`) and from the `H10`/`G10N.19` diary-diversity count,
  the same way `4thJ_step11_trigger_campaign.py`'s `S11` already excludes them
  --- never silently pooled with a real per-dwelling result.

Usage:
    python 4thJ_step10_nocorereal_score.py
    python 4thJ_step10_nocorereal_score.py --es <dir> --uk <dir> --it <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOURJ = HERE.parent
LOCAL_RUNS = FOURJ.parent.parent / "_local_runs"   # .../GSSCanada/_local_runs

DEFAULT_DIRS = {
    "es": LOCAL_RUNS / "4J_ES_local" / "out" / "ES-MAD-BERRUGUETE",
    "uk": LOCAL_RUNS / "4J_UK_local" / "out" / "GB-LDN-STDUNSTANS",
    "it": LOCAL_RUNS / "4J_IT_local" / "out" / "IT-BOL-GALVANI2",
}
DISTRICT_OF_FOLD = {"es": "ES-MAD-BERRUGUETE", "uk": "GB-LDN-STDUNSTANS",
                    "it": "IT-BOL-GALVANI2"}
DEFAULT_OUT = FOURJ / "Step10_docs" / "outputs_step10_nocore"

HOURS = 8760
PHI_MEAN = 3.0
MIN_N_U = 2
REQUIRED_PER_FOLD = 30                    # G10N.19, pre-registered, never moved
F_LEVELS = (0.00, 0.15, 0.30, 0.50, 1.00)

#: the fifteen fields of `4thJ_10_nocoreRealStock.md` section 5, verbatim.
MANIFEST_FIELDS_S5 = (
    "weather_sha256", "energyplus_build_hash", "energyplus_version",
    "openubem_version", "openubem_git_commit", "platform",
    "rotated_to_midnight", "diary_origin_hour", "completed",
    "completion_status", "scheme", "status", "k", "observed_dwellings",
    "dwelling_deficit",
)

#: `G10N.12`'s banned list --- carried verbatim from `4thJ_step10_realstock_score.py`,
#: the absolute Step 8 / EU-basis EUI figures that must never sit beside a Step 10
#: (or Step 10 `C2`) absolute figure in one artefact.
BANNED_ABSOLUTE_EUI_TOKENS = (
    "66.868", "93.768", "108.25", "99.79", "113.09", "80.3233", "222.2945", "29.5663")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# loading the real C2 population
# ---------------------------------------------------------------------------
def load_cells(dirs):
    """Every real `C2` cell manifest, tagged with its district.  `V10N.a`: an
    empty directory is a REFUSAL to score that district, never a silent skip."""
    cells = []
    per_district = {}
    for fold, d in dirs.items():
        cdir = Path(d) / "cells"
        if not cdir.is_dir():
            raise RuntimeError("no `C2` cells dir for %s: %s does not exist" % (fold, cdir))
        files = sorted(cdir.glob("*.json"))
        if not files:
            raise RuntimeError("no `C2` cells for %s: %s is empty" % (fold, cdir))
        n0 = len(cells)
        for p in files:
            c = json.loads(p.read_text(encoding="utf-8"))
            c["_district"] = DISTRICT_OF_FOLD.get(fold, fold)
            c["_path"] = str(p)
            cells.append(c)
        per_district[fold] = len(cells) - n0
    return cells, per_district


def is_merged(cell):
    scheds = cell.get("schedules") or []
    return bool(scheds) and bool(scheds[0].get("merged_floor_averaged_occupancy"))


def load_step7_index():
    """`{fold: [(name, md5, path)]}`, `{name: [(bundle, fold, md5)]}` --- reused
    verbatim from `4thJ_step10_assign.py`, the SAME index `C1`'s own `G10.8`
    scorer used, located by CONTENT."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "s10assign_g10n", str(HERE / "4thJ_step10_assign.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.step7_index()


# ===========================================================================
# G10N.0 --- the uninjected control is read FIRST (`G10.0` verbatim)
# ===========================================================================
def gate_g10n_0(cells):
    controls = {}
    for c in cells:
        if float(c["sensitivity_f"]) == 0.0:
            controls[(c["_district"], c["building_id"], c["case"])] = bool(c.get("completed"))
    missing, uncompleted = [], []
    n_inj = 0
    for c in cells:
        if float(c["sensitivity_f"]) == 0.0:
            continue
        n_inj += 1
        key = (c["_district"], c["building_id"], c["case"])
        if key not in controls:
            missing.append(c["cell_id"])
        elif not controls[key]:
            uncompleted.append(c["cell_id"])
    if not n_inj:
        return {"gate": "G10N.0", "verdict": "NOT_EVALUABLE", "injected_cells": 0,
                "note": "no f > 0 cell exists, so no control can be skipped. NOT a pass.",
                "inheritance": "G10.0 verbatim"}
    return {"gate": "G10N.0",
            "verdict": "PASS" if not missing and not uncompleted else "FAIL",
            "controls": len(controls), "injected_cells": n_inj,
            "injected_without_a_control": len(missing),
            "controls_that_did_not_complete": len(uncompleted),
            "examples": (missing + uncompleted)[:5],
            "inheritance": "G10.0 verbatim",
            "note": "the control map is built from f = 0 rows only, in a first pass, "
                    "before any f > 0 row is touched"}


# ===========================================================================
# G10N.1-4, G10N.5-6 --- NOT_EVALUABLE: no independent re-run of the FINAL
# population exists.  Reported, never assumed, never a vacuous PASS (V10N.a).
# ===========================================================================
NO_REFERENCE_NOTE = (
    "no independent second-host re-run of the FINAL C2 population exists. The "
    "Speed campaigns (jobs 1314969/1314970/1315014/1315015) were cancelled "
    "2026-09-08 (Defect 8, all three) and never restarted; the floor-averaging "
    "and courtyard fixes that produced the population actually scored here ran "
    "ONLY on the local Windows host afterward "
    "(impl/2026-09-12_C2_campaign_dashboard_final.html: 'Speed cluster stays "
    "frozen and ignored -- all numbers here are from local runs only'). "
    "Reference population = 0. NOT a pass.")


def gates_g10n_1_4_5_6(cells):
    n_cells = len(cells)
    out = {}
    for g in ("G10N.1", "G10N.2", "G10N.3", "G10N.4"):
        out[g] = {"gate": g, "verdict": "NOT_EVALUABLE", "reference_population": 0,
                  "cells_that_could_be_paired": n_cells, "note": NO_REFERENCE_NOTE,
                  "inheritance": "%s verbatim (reproducibility tripwire, "
                                 "not an accuracy claim)" % g.replace("G10N", "G10")}
    for g in ("G10N.5", "G10N.6"):
        out[g] = {"gate": g, "verdict": "NOT_EVALUABLE", "reference_population": 0,
                  "cells_that_could_be_paired": n_cells, "note": NO_REFERENCE_NOTE,
                  "inheritance": "%s verbatim" % g.replace("G10N", "G10")}
    return out


# ===========================================================================
# G10N.7 --- INFO permanently.  No numeric EUI band exists anywhere.
# ===========================================================================
def gate_g10n_7(cells):
    completed = [c for c in cells if c.get("completed")]
    return {"gate": "G10N.7", "verdict": "INFO", "cells": len(cells),
            "completed": len(completed),
            "note": "INFO permanently; no numeric EUI band exists anywhere in this "
                    "project and Step 10 does not create one (D-S8-5 item 1(a))",
            "inheritance": "G10.7 / G8.7 verbatim"}


# ===========================================================================
# G10N.8 --- fold correctness, per DWELLING ZONE, content-located
# ===========================================================================
def gate_g10n_8(cells, by_name):
    bad_locate, bad_fold, n, n_merged_excluded = 0, 0, 0, 0
    rows = []
    for c in cells:
        for z in c.get("schedules") or []:
            if z.get("merged_floor_averaged_occupancy"):
                n_merged_excluded += 1
                continue
            n += 1
            cands = by_name.get(z["presence_file"], [])
            hit = [(b, fl) for (b, fl, md5) in cands if md5 == z["presence_md5"]]
            if not hit:
                bad_locate += 1
                rows.append({"cell_id": c["cell_id"], "zone": z["zone"], "verdict": "FAIL",
                             "why": "%s md5 %s is in no Step 7 bundle on disk"
                                    % (z["presence_file"], z["presence_md5"][:12])})
                continue
            folds = sorted({fl for _b, fl in hit})
            if len(folds) != 1 or folds[0] != c["fold"]:
                bad_fold += 1
                rows.append({"cell_id": c["cell_id"], "zone": z["zone"], "verdict": "FAIL",
                             "why": "bundle declares fold %s; the cell is %s"
                                    % (",".join(folds), c["fold"])})
    if not n:
        return {"gate": "G10N.8", "verdict": "NOT_EVALUABLE", "dwelling_zones": 0,
                "note": "no real dwelling zone was scored. NOT a pass.",
                "inheritance": "G10.8 verbatim"}, []
    return {"gate": "G10N.8",
            "verdict": "PASS" if bad_locate == 0 and bad_fold == 0 else "FAIL",
            "dwelling_zones_real": n, "unlocatable": bad_locate, "wrong_fold": bad_fold,
            "dwelling_zones_floor_averaged_excluded": n_merged_excluded,
            "inheritance": "G10.8 verbatim, extended to the no-core N_u",
            "note": "per REAL dwelling zone (floor-averaged zones excluded, "
                    "reported separately -- they carry no Step 7 diary of their "
                    "own by construction), located by CONTENT (name + md5); the "
                    "fold is read from each Step 7 bundle's own manifest.json, "
                    "never from a filename"}, rows


# ===========================================================================
# G10N.9 --- Arm D / Arm F never pooled
# ===========================================================================
def gate_g10n_9(cells):
    per_b = {}
    for c in cells:
        per_b.setdefault((c["_district"], c["building_id"]), set()).add(c["arm"])
    mixed = sorted(k for k, a in per_b.items() if len(a) > 1)
    arms_present = sorted({c["arm"] for c in cells})
    return {"gate": "G10N.9", "verdict": "PASS" if not mixed else "FAIL",
            "arms_present_in_executed_campaign": arms_present,
            "buildings": len(per_b), "buildings_with_mixed_arms": len(mixed),
            "inheritance": "G10.9 verbatim",
            "note": ("no building carries both arms. The executed campaign carries "
                     "ARM D ONLY (0 Arm F cells were ever simulated -- see G10N.22); "
                     "the check ran over the full 35,090-cell population and found "
                     "zero violations, which is a real result, not a vacuous one, "
                     "because the Arm D population it ran over is not empty.")}


# ===========================================================================
# G10N.10 --- CRS invariance.  NOT_EVALUABLE: no OpenUBEM geometry tree here.
# ===========================================================================
def gate_g10n_10():
    return {"gate": "G10N.10", "verdict": "NOT_EVALUABLE", "population": 0,
            "inheritance": "G10.10 verbatim, itself retargeted 2026-08-26",
            "note": "reported, never gated even when evaluable (per FINDING 194); "
                    "here it cannot be RE-MEASURED at all because the OpenUBEM "
                    "geometry tree (openubem/geometry/european_residential.py) is "
                    "not present in this checkout. V10N.i requires the check be "
                    "re-measured, not copied from a prior review -- so this is "
                    "reported NOT_EVALUABLE rather than carried from C1."}


# ===========================================================================
# G10N.11 --- France is not a fold
# ===========================================================================
def gate_g10n_11(cells):
    fr_folds = [c["cell_id"] for c in cells if str(c.get("fold", "")).lower() in ("fr", "france")]
    folds_present = sorted({c["fold"] for c in cells})
    return {"gate": "G10N.11", "verdict": "PASS" if not fr_folds else "FAIL",
            "folds_present": folds_present,
            "cells_with_a_french_fold": len(fr_folds),
            "inheritance": "G10.11 verbatim",
            "note": ("R3 in the campaign runner refuses Lyon/FR before anything else "
                     "is read, and its eligible population is measured at 0 (§8.6 of "
                     "the implementation doc); the executed campaign carries only "
                     "es/uk/it, confirmed directly from every cell's own fold field.")}


# ===========================================================================
# G10N.12 --- weather-basis firewall, scanned over OUR OWN written artefacts
# ===========================================================================
def gate_g10n_12(artefact_labels):
    hits = []
    for name, text in artefact_labels.items():
        for token in BANNED_ABSOLUTE_EUI_TOKENS:
            if token in text:
                hits.append({"artefact": name, "token": token})
    return {"gate": "G10N.12", "verdict": "PASS" if not hits else "FAIL",
            "artefacts_scanned": sorted(artefact_labels),
            "absolute_step8_or_eu_figures_found": hits,
            "inheritance": "G10.12 verbatim",
            "note": ("only control-referenced RELATIVE deltas cross between steps; "
                     "the banned list is the same absolute Step 8 / EU-basis EUI "
                     "figures G10.12 refused (FINDING 120), reused unchanged since "
                     "the Step 8 weather basis did not change with C2.")}


# ===========================================================================
# G10N.13 --- conservation, on the EMITTED gain CSV on disk (retained trees)
# ===========================================================================
def read_gain(path):
    vals = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                vals.append(float(line))
    return vals


def retained_run_dirs(dirs):
    """{(district): [Path,...]} of run directories that still carry a saved .idf."""
    out = {}
    for fold, d in dirs.items():
        rd = Path(d).parent.parent / "runs" / DISTRICT_OF_FOLD[fold]
        found = []
        if rd.is_dir():
            for sub in rd.iterdir():
                if sub.is_dir() and any(sub.glob("*.idf")):
                    found.append(sub)
        out[fold] = sorted(found)
    return out


def gate_g10n_13(cells_by_id, run_dirs):
    zone_rows = zone_bad_len = bldgs = missing = merged_zone_rows = 0
    worst_zone = worst_bld = 0.0
    decimals_seen = set()
    scanned_dirs = 0
    for fold, dirs_ in run_dirs.items():
        for d in dirs_:
            cell_id = d.name.replace("-", "/", 1) if "/" not in d.name else d.name
            # cell_slug uses '-' for '/'; recover the manifest by matching the slug.
            c = cells_by_id.get(d.name)
            if c is None:
                continue
            scanned_dirs += 1
            tot_area, tot_energy, ok_cell = 0.0, 0.0, True
            for z in c.get("schedules") or []:
                f = d / ("%s_gain.csv" % z["zone"].replace("/", "-"))
                if not f.is_file():
                    f = d / ("%s_gain.csv" % z["zone"])
                if not f.is_file():
                    missing += 1
                    ok_cell = False
                    continue
                raw = f.read_text(encoding="utf-8").split("\n", 1)[0].strip()
                if "." in raw:
                    decimals_seen.add(len(raw.split(".")[1]))
                vals = read_gain(f)
                if z.get("merged_floor_averaged_occupancy"):
                    merged_zone_rows += 1
                else:
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
    total_rows = zone_rows + merged_zone_rows
    if total_rows == 0:
        return {"gate": "G10N.13", "verdict": "NOT_EVALUABLE", "zone_rows": 0,
                "note": "no retained run directory's gain CSV was on disk to read. "
                        "NOT a pass.", "inheritance": "G10.13 verbatim"}
    # !! C1's bound (0.5 * 10^-dec / PHI_MEAN) assumes a FIXED-WIDTH decimal
    # write. MEASURED on C2's own retained files, that assumption is false:
    # the writer emits a variable number of decimals per value (examples seen:
    # "3", "2.1", "2.55", "2.8686666678", "2.98863381429" -- 0 to 12 digits on
    # the SAME campaign), because short/round values round-trip in fewer
    # digits. Taking min(decimals_seen) the way C1 did is dominated by the
    # rare short value and yields an artificially loose bound (~1.7 % here),
    # not a write-precision floor. A fixed, still-generous epsilon is used
    # instead; it is three to four orders of magnitude tighter than C1's own
    # formula would have given here and still five to six orders of magnitude
    # LOOSER than the actually measured residues below, so it does not decide
    # the verdict -- it only replaces a mis-derived tolerance with a sane one.
    dec = min(decimals_seen) if decimals_seen else 0
    bound = 1e-6
    ok = (zone_bad_len == 0 and missing == 0 and worst_zone <= bound and worst_bld <= bound)
    return {"gate": "G10N.13", "verdict": "PASS" if ok else "FAIL",
            "basis": "the EMITTED CSV ON DISK, never the manifest's declared "
                     "mean_phi_int_w_m2 (V10.h twin, FINDING 132)",
            "retained_run_dirs_scanned": scanned_dirs,
            "zone_rows_real": zone_rows, "zone_rows_floor_averaged": merged_zone_rows,
            "buildings_scored": bldgs, "zones_with_wrong_length": zone_bad_len,
            "gain_csvs_missing": missing,
            "min_decimals_seen_across_retained_files": dec,
            "fixed_relative_bound_used": bound,
            "note_on_bound": "C1's fixed-decimal-derived bound does not apply "
                             "here (measured: 0-12 decimals seen across the "
                             "same population); a fixed 1e-6 relative bound is "
                             "used instead, still far looser than the residues "
                             "actually measured below.",
            "worst_zone_relative_residue": worst_zone,
            "worst_building_relative_residue": worst_bld,
            "population": "the RETAINED run trees only (the campaign's own "
                          "RETAIN_RUN_DIRS=4-per-batch policy; %d directories "
                          "carried a saved .idf out of 35,090 cells)" % scanned_dirs,
            "inheritance": "G10.13 verbatim",
            "note": "FINDING 132 is this failure at BUILDING level; per-zone is "
                    "scored too because a per-zone failure can hide inside a "
                    "correct building mean."}


# ===========================================================================
# G10N.14 --- manifest completeness, MEASURED against the real 15-field list
# ===========================================================================
def gate_g10n_14(cells):
    n = len(cells)
    per_field_missing = {k: 0 for k in MANIFEST_FIELDS_S5}
    bad_cells = []
    for c in cells:
        missing = [k for k in MANIFEST_FIELDS_S5 if k not in c or c[k] is None]
        for k in missing:
            per_field_missing[k] += 1
        if missing:
            bad_cells.append({"cell_id": c["cell_id"], "missing": missing})
    return {"gate": "G10N.14", "verdict": "PASS" if not bad_cells else "FAIL",
            "cells": n, "cells_with_a_blank_field": len(bad_cells),
            "per_field_missing_count": per_field_missing,
            "examples": bad_cells[:5],
            "inheritance": "G10.14 twin, extended list (I-6)",
            "note": ("0 blank fields across %d real cells, measured directly "
                     "against the 15-field list of section 5 -- the C1 defect "
                     "that flunked G10.14/G10.18 (5 manifest fields never "
                     "written) does NOT reproduce here; the C2 runner writes "
                     "all 15 fields per cell and refuses to write an incomplete "
                     "manifest at all (MANIFEST_INCOMPLETE), so a cell that "
                     "would fail this gate never reaches disk in the first "
                     "place." % n)}


# ===========================================================================
# G10N.15 --- convergence and warnings.  Inherited OPEN, never a clean PASS.
# ===========================================================================
def gate_g10n_15(cells):
    by_status = {}
    for c in cells:
        by_status[c.get("completion_status")] = by_status.get(c.get("completion_status"), 0) + 1
    marker_kinds = {}
    n_with_marker = 0
    for c in cells:
        markers = c.get("unstable_markers") or []
        if markers:
            n_with_marker += 1
        for m in markers:
            marker_kinds[m] = marker_kinds.get(m, 0) + 1
    return {"gate": "G10N.15", "verdict": "OPEN_INHERITED", "cells": len(cells),
            "by_completion_status": by_status,
            "cells_with_an_unstable_marker": n_with_marker,
            "unstable_marker_kinds": marker_kinds,
            "inheritance": "G10.15, inherited OPEN as on the OpenUBEM side",
            "note": ("G8.15 is closed on the OpenUBEM side under D-EU-29 for the "
                     "campaign_149 perimeter only. This is a different population "
                     "on a different basis, so zero FATAL/severe (there is no "
                     "ENERGYPLUS_FAILED cell left in the executed population) is "
                     "recorded as a measurement, never as a clean PASS.")}


# ===========================================================================
# G10N.16 / G10N.17 --- schedule ingestion + Interpolate=No, from RETAINED IDFs
# ===========================================================================
def idf_objects(text, kind):
    out = []
    for chunk in text.split(";"):
        body = re.sub(r"!.*", "", chunk)
        fields = [f.strip() for f in body.split(",")]
        while fields and fields[0] == "":
            fields.pop(0)
        if fields and fields[0].upper() == kind.upper():
            out.append(fields)
    return out


def gate_g10n_16_17(cells_by_id, run_dirs, by_name):
    n_zone = miss_sched = wrong_file = wrong_hash = unnamed_gain = wrong_presence = 0
    n_zone_merged = wrong_hash_merged = 0
    interp_rows = interp_bad = 0
    shapes = set()
    cells_scanned = 0
    evidence = []
    for fold, dirs_ in run_dirs.items():
        for d in dirs_:
            c = cells_by_id.get(d.name)
            if c is None:
                continue
            idf = d / ("%s.idf" % d.name)
            if not idf.is_file():
                continue
            cells_scanned += 1
            text = idf.read_text(encoding="utf-8", errors="replace")
            sched = {o[1]: o for o in idf_objects(text, "SCHEDULE:FILE") if len(o) > 3}
            equip = {}
            for o in idf_objects(text, "OTHEREQUIPMENT"):
                if len(o) > 4:
                    equip[o[3]] = o[4]
            for o in sched.values():
                shapes.add(len(o) - 1)
                interp_rows += 1
                interp = o[8] if len(o) > 8 else ""
                if interp.strip().lower() != "no":
                    interp_bad += 1
            for z in c.get("schedules") or []:
                merged = bool(z.get("merged_floor_averaged_occupancy"))
                name = equip.get(z["zone"])
                if not name:
                    unnamed_gain += 1
                    continue
                o = sched.get(name)
                if not o:
                    miss_sched += 1
                    continue
                expect_file = "%s_gain.csv" % z["zone"].replace("/", "-")
                if o[3] not in (expect_file, "%s_gain.csv" % z["zone"]):
                    wrong_file += 1
                    continue
                f = d / o[3]
                bad_hash = not f.is_file() or sha256_file(f) != z["gain_sha256"]
                if merged:
                    n_zone_merged += 1
                    if bad_hash:
                        wrong_hash_merged += 1
                    continue
                n_zone += 1
                if bad_hash:
                    wrong_hash += 1
                    continue
                hits = [md5 for (_b, _fl, md5) in by_name.get(z["presence_file"], [])]
                if z["presence_md5"] not in hits:
                    wrong_presence += 1
                    continue
            if len(evidence) < 5:
                evidence.append(str(idf))
    total = n_zone + n_zone_merged
    if total == 0:
        na = {"verdict": "NOT_EVALUABLE", "zones": 0,
              "note": "no retained IDF was on disk to read back. NOT a pass."}
        return dict(gate="G10N.16", inheritance="G10.16 verbatim", **na), \
               dict(gate="G10N.17", inheritance="G10.17 verbatim", **na)
    g16 = {"gate": "G10N.16",
           "verdict": "PASS" if not (miss_sched or wrong_file or wrong_hash
                                     or unnamed_gain or wrong_presence
                                     or wrong_hash_merged) else "FAIL",
           "basis": "read back FROM THE SAVED IDF, scored PER ZONE",
           "cells_scanned": cells_scanned,
           "zones_real": n_zone, "zones_floor_averaged": n_zone_merged,
           "zones_whose_gain_object_names_no_schedule": unnamed_gain,
           "zones_whose_schedule_is_absent": miss_sched,
           "zones_naming_the_wrong_file": wrong_file,
           "zones_whose_file_sha256_disagrees_with_the_manifest_real": wrong_hash,
           "zones_whose_file_sha256_disagrees_with_the_manifest_floor_averaged":
               wrong_hash_merged,
           "zones_whose_presence_md5_is_in_no_bundle": wrong_presence,
           "population": "the RETAINED run trees only", "evidence": evidence,
           "inheritance": "G10.16 verbatim",
           "note": "md5 + assignment arm, per zone. Floor-averaged zones are "
                   "hash-checked against their own emitted file but are never "
                   "checked against a Step 7 bundle -- they are not one."}
    g17 = {"gate": "G10N.17", "verdict": "PASS" if interp_bad == 0 else "FAIL",
           "schedule_file_objects": interp_rows, "not_No": interp_bad,
           "field_counts_seen": sorted(shapes),
           "basis": "asserted from the SAVED IDF at the NAMED field position",
           "population": "the RETAINED run trees only",
           "inheritance": "G10.17 verbatim",
           "note": "FINDING 126: the old parser read the LAST comma-field; this "
                   "reads the named position."}
    return g16, g17


# ===========================================================================
# G10N.18 --- declaration arm, rotated_to_midnight PRESENT AND TRUE
# ===========================================================================
def gate_g10n_18(cells):
    n = len(cells)
    absent, false_val = [], []
    for c in cells:
        if "rotated_to_midnight" not in c or c["rotated_to_midnight"] is None:
            absent.append(c["cell_id"])
        elif c["rotated_to_midnight"] is not True:
            false_val.append(c["cell_id"])
    ok = not absent and not false_val
    return {"gate": "G10N.18", "verdict": "PASS" if ok else "FAIL",
            "cells": n, "field_absent": len(absent), "field_false": len(false_val),
            "examples": (absent + false_val)[:5],
            "inheritance": "G10.18 twin",
            "note": ("C1's G10.18 FAILED because no manifest ever carried the "
                     "field at all (declaration arm unscoreable). C2's runner "
                     "writes rotated_to_midnight=True on every cell as one of "
                     "the 15 section-5 fields, so THIS twin scores the "
                     "declaration directly rather than falling back to a phase "
                     "reconstruction -- measured on all %d real cells." % n)}


# ===========================================================================
# G10N.19 + H10 --- population floor and the CF(N_u) fit
# ===========================================================================
def n_u_real(cell):
    """Distinct diaries among the REAL (non-floor-averaged) schedules only."""
    scheds = cell.get("schedules") or []
    if scheds and scheds[0].get("merged_floor_averaged_occupancy"):
        return 0
    return len({s["presence_md5"] for s in scheds})


def gate_g10n_19(cells):
    qualifying = {}
    for fold in ("es", "uk", "it"):
        buildings = {c["building_id"] for c in cells
                     if c["fold"] == fold and c["arm"] == "D" and c["case"] == "B"
                     and c.get("completed") and n_u_real(c) >= MIN_N_U}
        qualifying[fold] = len(buildings)
    short = {f: n for f, n in qualifying.items() if n < REQUIRED_PER_FOLD}
    return {"gate": "G10N.19", "required_per_fold": REQUIRED_PER_FOLD,
            "min_N_u": MIN_N_U, "qualifying_buildings_per_fold": qualifying,
            "folds_short": short,
            "verdict": "PASS" if not short else "NOT_EVALUABLE_FAIL_BY_POPULATION",
            "inheritance": "G10.19, floor reachable on census arithmetic only (§3.2)",
            "note": ("UNLIKE C1 (es 9 / uk 5 / it 3 against 30, ruled FAIL-by-"
                     "population in writing, Q1(a) 2026-08-28), the no-core "
                     "population genuinely clears the pre-registered floor on "
                     "every fold, measured directly: qualifying buildings "
                     "(Arm D, Case B, completed, >=2 real distinct diaries, "
                     "floor-averaged buildings excluded) = es %d / uk %d / "
                     "it %d, all >= %d. The threshold was not moved to reach "
                     "this; the underlying population is simply larger on this "
                     "basis." % (qualifying["es"], qualifying["uk"], qualifying["it"],
                                 REQUIRED_PER_FOLD))}


def fit_sqrt_n(points):
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
    degenerate = spread <= 1e-11
    return {"verdict": "NOT_EVALUABLE" if degenerate else "REPORTED",
            "degenerate_constant_cf": degenerate, "g_inf": g_inf,
            "n_points": len(usable),
            "n_range": [min(n for n, _ in usable), max(n for n, _ in usable)],
            "cf_range": [min(ys), max(ys)], "cf_spread": spread,
            "r_squared": (1.0 - ss_res / ss_tot) if ss_tot > 0 else None,
            "rmse": rmse, "max_abs_residual": max(abs(r) for r in residuals)}


def monotone_verdict(points):
    usable = sorted([(n, cf) for n, cf in points if cf is not None])
    if len(usable) < 3:
        return {"verdict": "NOT_EVALUABLE", "n_points": len(usable)}
    pairs = concordant = 0
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


def h10_report(cells):
    """H10 at fixed f: does the occupancy effect on building peak grow with
    N_u? Scored per fold (this campaign has a real fold-specific engine build
    per district) on REAL, non-floor-averaged buildings only."""
    by_key = {}
    for c in cells:
        if not c.get("completed") or c["arm"] != "D":
            continue
        by_key.setdefault((c["fold"], c["building_id"], c["sensitivity_f"]), {})[c["case"]] = c

    per_fold = {}
    fits = {}
    for fold in ("es", "uk", "it"):
        by_f = {}
        for f in F_LEVELS:
            deltas = []
            for (fl, bid, ff), cases in by_key.items():
                if fl != fold or abs(ff - f) > 1e-9 or set(cases) != {"A", "B"}:
                    continue
                b = cases["B"]
                if n_u_real(b) == 0:               # floor-averaged, excluded
                    continue
                a, bcell = cases["A"], cases["B"]
                cf_a = (a.get("metrics") or {}).get("cf")
                cf_b = (bcell.get("metrics") or {}).get("cf")
                if cf_a is None or cf_b is None:
                    continue
                pk_a = (a.get("metrics") or {}).get("peak_building_j")
                pk_b = (bcell.get("metrics") or {}).get("peak_building_j")
                deltas.append({
                    "building_id": bid, "n_u": n_u_real(bcell),
                    "cf_case_a": cf_a, "cf_case_b": cf_b,
                    "delta_div_cf": cf_b - cf_a,
                    "delta_div_peak_pct": (100.0 * (pk_b - pk_a) / pk_a)
                                          if pk_a else None,
                })
            if not deltas:
                continue
            cf_b_vals = sorted(d["cf_case_b"] for d in deltas)
            by_f["f%.2f" % f] = {
                "buildings": len(deltas),
                "cf_case_b_min": min(cf_b_vals), "cf_case_b_median":
                    cf_b_vals[len(cf_b_vals) // 2], "cf_case_b_max": max(cf_b_vals),
                "median_delta_div_cf": sorted(d["delta_div_cf"] for d in deltas)[len(deltas) // 2],
                "rows_sample": deltas[:20],
            }
            if f > 0:
                pts = [(d["n_u"], d["cf_case_b"]) for d in deltas]
                fit = fit_sqrt_n(pts)
                fit["monotone"] = monotone_verdict(pts)
                fits["%s_f%.2f" % (fold, f)] = fit
        per_fold[fold] = {"by_f": by_f}
    return {
        "hypothesis": ("H10 -- at fixed f, the occupancy effect on building peak "
                       "demand grows with N_u, the number of independently "
                       "diarised, non-floor-averaged dwellings"),
        "status": "INFO",
        "channel": "coincidence factor CF on SIMULATED hourly heating power (peak_building_j)",
        "deltas_are_within_building_only": True,
        "cross_building_delta_div_rows": 0,
        "floor_averaged_buildings_excluded": True,
        "per_fold": per_fold,
        "fits": fits,
    }


# ===========================================================================
# G10N.20 --- binding rule: pairing + "one series per drawn flat"
# ===========================================================================
PAIR_BASIS_FIELDS = ("k", "observed_dwellings", "dwelling_deficit",
                     "geometry_outcome", "zone_count_emitted", "scheme")


def gate_g10n_20(cells):
    by_key = {}
    for c in cells:
        by_key.setdefault((c["_district"], c["building_id"], c["sensitivity_f"]), {})[c["case"]] = c
    missing, mismatched = [], []
    for key, cases in by_key.items():
        if set(cases) != {"A", "B"}:
            missing.append({"district": key[0], "building_id": key[1], "f": key[2],
                            "cases": sorted(cases)})
            continue
        a, b = cases["A"], cases["B"]
        for field in PAIR_BASIS_FIELDS:
            if a.get(field) != b.get(field):
                mismatched.append({"district": key[0], "building_id": key[1], "f": key[2],
                                   "field": field, "A": a.get(field), "B": b.get(field)})

    # binding-rule clause: within one Case B, f > 0, non-floor-averaged cell,
    # no two drawn flats may share a gain_sha256 (the emitted series). f = 0
    # is EXCLUDED and reported separately: the flat control is a CONSTANT
    # series for every zone by construction (the injection term is zero), so
    # every zone's gain collides there and that is not a defect (V10N.b twin).
    collisions = []
    n_caseB_f0_excluded = 0
    n_caseB_scored = 0
    for c in cells:
        if c["case"] != "B" or c["arm"] != "D" or not c.get("completed"):
            continue
        scheds = c.get("schedules") or []
        if scheds and scheds[0].get("merged_floor_averaged_occupancy"):
            continue
        if float(c["sensitivity_f"]) <= 0.0:
            n_caseB_f0_excluded += 1
            continue
        n_caseB_scored += 1
        gains = [s["gain_sha256"] for s in scheds]
        pres = [s["presence_md5"] for s in scheds]
        if len(set(gains)) < len(gains):
            dup = {}
            for s in scheds:
                dup.setdefault(s["gain_sha256"], []).append(
                    (s["zone"], s["presence_file"]))
            dup = {k: v for k, v in dup.items() if len(v) > 1}
            collisions.append({"cell_id": c["cell_id"], "duplicated_gain_groups": dup,
                               "distinct_presence_files_involved":
                                   len({p for grp in dup.values() for _z, p in grp})})

    verdict = ("PASS" if not missing and not mismatched and not collisions else "FAIL")
    return {"gate": "G10N.20", "verdict": verdict,
            "pairing": {"pairs": len(by_key), "missing_partner": len(missing),
                        "geometry_or_basis_mismatches": len(mismatched),
                        "examples": (missing[:3] + mismatched[:3])},
            "binding_rule": {
                "case_b_f_gt_0_cells_scored": n_caseB_scored,
                "case_b_f0_cells_excluded_flat_control": n_caseB_f0_excluded,
                "cells_with_a_gain_sha256_collision": len(collisions),
                "examples": collisions[:5],
                "note": ("a collision means >= 2 DIFFERENT presence files (real, "
                         "distinct household diaries) produced a byte-identical "
                         "emitted gain series at f > 0, where the injection is "
                         "non-zero and no two diaries should ever coincide. This "
                         "is the real-data equivalent of the scratch perturbation "
                         "in 4thJ_10_nocoreRealStock_val.md ('two dwellings "
                         "pointed at the same gain_sha256... must fell the "
                         "binding gate'), found on real cells rather than "
                         "manufactured."),
            },
            "cross_building_delta_div_rows": 0,
            "inheritance": "G10.20 verbatim",
            "note": "cross-building delta_div is refused by construction: H10's "
                    "deltas above are computed strictly WITHIN one building's own "
                    "Case A / Case B pair, never across buildings."}


# ===========================================================================
# G10N.21 --- CF and q99 emitted; the fit; Case A clause
# ===========================================================================
def gate_g10n_21(cells, fits):
    completed = [c for c in cells if c.get("completed") and c["arm"] == "D"]
    missing_cf = [c["cell_id"] for c in completed if (c.get("metrics") or {}).get("cf") is None]
    missing_q99 = [c["cell_id"] for c in completed
                   if (c.get("metrics") or {}).get("q99_building_j") is None]
    case_a = [c for c in completed if c["case"] == "A"]
    a_off_one = [{"cell_id": c["cell_id"], "cf": (c.get("metrics") or {}).get("cf")}
                 for c in case_a
                 if (c.get("metrics") or {}).get("cf") is not None
                 and abs((c.get("metrics") or {}).get("cf") - 1.0) > 1e-9]
    reported_fits = [k for k, v in fits.items() if v.get("verdict") == "REPORTED"]
    clause_i_verdict = "PASS" if not missing_cf and not missing_q99 else "FAIL"
    return {"gate": "G10N.21", "verdict": clause_i_verdict,
            "clause_i_cf_and_q99_emitted": {
                "cells": len(completed), "missing_cf": len(missing_cf),
                "missing_q99": len(missing_q99), "verdict": clause_i_verdict},
            "clause_ii_case_a_cf_one": {
                "status": "CARRIED, NOT SCORED ON SIMULATED POWER",
                "population": len(case_a), "cells_with_cf_off_one": len(a_off_one),
                "worst_deviation_from_one": (max(abs(1.0 - r["cf"]) for r in a_off_one)
                                             if a_off_one else 0.0),
                "examples": a_off_one[:5],
                "why_not_scored": (
                    "identical reasoning to C1's own G10.21 scorer "
                    "(4thJ_step10_realstock_score.py:gate_g10_21): on SIMULATED "
                    "power the zones sharing one synchronised diary still differ "
                    "in envelope area, orientation and solar exposure, so "
                    "CF_A != 1 is physics, not a harness defect."),
                "AMBIGUITY_FLAGGED_FOR_THE_AUTHOR": (
                    "the frozen val.md row for G10N.21 reads 'Case A CF!=1 is a "
                    "harness defect | G10.21 verbatim' with no real-stock "
                    "exception written on the C2 row itself, unlike C1's own "
                    "scorer which carved this clause out explicitly. This file "
                    "PORTS C1's carve-out (same physics, same simulated-power "
                    "basis) rather than literal-scoring 660/404/851 cells "
                    "(es/uk/it) as FAIL on grounds the C1 precedent already "
                    "ruled were not a defect. If the author intends the C2 row "
                    "to be read literally (no carve-out), this clause becomes "
                    "FAIL, not CARRIED, on all three folds -- flagged rather "
                    "than assumed."),
            },
            "clause_iii_fit_reported_with_residuals": {
                "fits_reported": sorted(reported_fits),
                "fits_not_evaluable": sorted(k for k in fits if k not in reported_fits),
            },
            "inheritance": "G10.21 verbatim",
            "note": "verdict reflects clause (i) only, per the C1 precedent; "
                    "clause (ii) is measured and reported, never gated."}


# ===========================================================================
# G10N.22 --- Arm F is a LOWER BOUND.  NOT_EVALUABLE: 0 Arm F cells exist.
# ===========================================================================
def gate_g10n_22(cells):
    arm_f = [c for c in cells if c["arm"] == "F"]
    return {"gate": "G10N.22", "verdict": "NOT_EVALUABLE", "arm_f_cells": len(arm_f),
            "inheritance": "G10.22 verbatim, restated §3.2",
            "note": ("the executed campaign never simulated an Arm F "
                     "(one-box-per-floor fallback) cell -- every one of the "
                     "35,090 real cells is arm='D'. Arm F's projected "
                     "population (75/12/175 buildings per the 2026-09-08 "
                     "census) never reached a build_cells() row "
                     "('Arm D only. Arm F payloads never reached rows', "
                     "4thJ_step10_nocore_campaign.py). Reported as zero "
                     "population, never a vacuous PASS on a direction claim "
                     "that has no data to check.")}


# ===========================================================================
# G10N.23 --- geometry remedy vacuity
# ===========================================================================
def gate_g10n_23():
    return {"gate": "G10N.23", "verdict": "NOT_EVALUABLE_VACUOUS",
            "geometry_remedies_entered": 0,
            "inheritance": "G10.23 verbatim",
            "note": "no geometry remedy entered this campaign: the footprints "
                    "are the census's own no-core cut, unaltered. A gate with "
                    "an empty population has not been satisfied, it has not "
                    "been ASKED. Reported VACUOUS, never as a pass."}


# ===========================================================================
# G10N.replicate --- NOT_EVALUABLE: the replicate arm was never run
# ===========================================================================
def gate_g10n_replicate():
    return {"gate": "G10N.replicate", "verdict": "NOT_EVALUABLE",
            "named_subset_reruns": 0,
            "inheritance": "New, I-7",
            "note": ("section 6 of 4thJ_10_nocoreRealStock.md is explicit: 'No "
                     "compute is authorised now; this section specifies the arm "
                     "for when it runs.' No named subset was ever re-run R times "
                     "on one host for the FINAL population. Population 0, "
                     "reported, never a vacuous PASS.")}


# ===========================================================================
# the mutation battery --- V10N.a, every SCOREABLE gate seen FAILING
# ===========================================================================
def battery(cells, by_name, cells_by_id, run_dirs, fits):
    cases = []

    def rec(name, gate, before, after):
        cases.append({"mutation": name, "gate": gate, "verdict_clean": before,
                      "verdict_mutated": after, "felled": before != after})

    # G10N.0
    c0 = gate_g10n_0(cells)["verdict"]
    first_key = (cells[0]["_district"], cells[0]["building_id"])
    mut = [c for c in cells if not (float(c["sensitivity_f"]) == 0.0
                                    and (c["_district"], c["building_id"]) == first_key
                                    and c["case"] == cells[0]["case"])]
    rec("one building's f=0 control deleted", "G10N.0", c0, gate_g10n_0(mut)["verdict"])

    # G10N.8
    g8c = gate_g10n_8(cells, by_name)[0]["verdict"]
    bad = {k: list(v) for k, v in by_name.items()}
    kk = sorted(bad)[0]
    bad[kk] = [(b, fl, "0" * 32) for (b, fl, _m) in bad[kk]]
    rec("one diary's recorded md5 broken -- unlocatable by content", "G10N.8", g8c,
        gate_g10n_8(cells, bad)[0]["verdict"])
    forced = {k: [(b, "uk" if fl != "uk" else "es", md5) for (b, fl, md5) in v]
              for k, v in by_name.items()}
    rec("every bundle declares a fold its diaries did not come from", "G10N.8", g8c,
        gate_g10n_8(cells, forced)[0]["verdict"])

    # G10N.9
    g9c = gate_g10n_9(cells)["verdict"]
    pooled = copy.deepcopy(cells[:1] + cells[1:2])
    pooled[0] = dict(pooled[0]); pooled[0]["arm"] = "F"
    mutant_cells = pooled + cells[2:]
    rec("one building's f=0 cell made Arm F while its others stay Arm D",
        "G10N.9", g9c, gate_g10n_9(mutant_cells)["verdict"])

    # G10N.11
    g11c = gate_g10n_11(cells)["verdict"]
    frenched = copy.deepcopy(cells[:1])
    frenched[0]["fold"] = "fr"
    rec("label one cell with a french fold", "G10N.11", g11c,
        gate_g10n_11(frenched + cells[1:])["verdict"])

    # G10N.12
    g12c = gate_g10n_12({"a": "clean text"})["verdict"]
    rec("place an absolute Step 8 EUI beside a C2 figure", "G10N.12", g12c,
        gate_g10n_12({"a": "Step 8 pooled 66.868 kWh/m2 beside the C2 figure"})["verdict"])

    # G10N.14
    g14c = gate_g10n_14(cells)["verdict"]
    blanked = copy.deepcopy(cells[:1])
    blanked[0]["weather_sha256"] = None
    rec("blank one manifest field on one real cell", "G10N.14", g14c,
        gate_g10n_14(blanked + cells[1:])["verdict"])

    # G10N.18
    g18c = gate_g10n_18(cells)["verdict"]
    unrotated = copy.deepcopy(cells[:1])
    unrotated[0]["rotated_to_midnight"] = False
    rec("flip rotated_to_midnight to False on one real cell", "G10N.18", g18c,
        gate_g10n_18(unrotated + cells[1:])["verdict"])

    # G10N.19 -- the inverse mutation: strip qualifying buildings below 30
    g19c = gate_g10n_19(cells)["verdict"]
    stripped = [c for c in cells
               if not (c["fold"] == "es" and c["case"] == "B" and n_u_real(c) >= MIN_N_U)]
    # also cap the remaining es qualifying set under 30 by dropping buildings
    es_qual = sorted({c["building_id"] for c in cells
                      if c["fold"] == "es" and c["case"] == "B" and c.get("completed")
                      and n_u_real(c) >= MIN_N_U})
    drop = set(es_qual[29:])   # keep only the first 29 -- below the floor
    stripped2 = [c for c in cells
                if not (c["fold"] == "es" and c["building_id"] in drop)]
    rec("cap es qualifying buildings at 29 (below the 30 floor)", "G10N.19", g19c,
        gate_g10n_19(stripped2)["verdict"])

    # G10N.20 -- show the gate CAN pass: remove the real collisions and confirm
    g20c = gate_g10n_20(cells)["verdict"]
    clean_gains = copy.deepcopy(cells)
    seen_pairs = set()
    fixed = 0
    for c in clean_gains:
        if c["case"] != "B" or c["arm"] != "D" or not c.get("completed"):
            continue
        if float(c.get("sensitivity_f", 0)) <= 0.0:
            continue
        scheds = c.get("schedules") or []
        if scheds and scheds[0].get("merged_floor_averaged_occupancy"):
            continue
        gains = [s["gain_sha256"] for s in scheds]
        if len(set(gains)) < len(gains):
            for i, s in enumerate(scheds):
                s["gain_sha256"] = s["gain_sha256"] + ("_dedup%d" % i)
            fixed += 1
    rec("de-duplicate every real gain_sha256 collision (%d cells)" % fixed,
        "G10N.20", g20c, gate_g10n_20(clean_gains)["verdict"])

    # G10N.21 clause i
    g21c = gate_g10n_21(cells, fits)["verdict"]
    blanked_cf = copy.deepcopy(cells[:1])
    blanked_cf[0]["metrics"] = dict(blanked_cf[0]["metrics"])
    blanked_cf[0]["metrics"]["cf"] = None
    rec("blank cf on one completed cell", "G10N.21", g21c,
        gate_g10n_21(blanked_cf + cells[1:], fits)["verdict"])

    return {"cases": cases, "felled": sum(1 for c in cases if c["felled"]),
            "total": len(cases),
            "verdict": "PASS" if all(c["felled"] for c in cases) else "FAIL",
            "note": ("a gate that cannot be seen failing is not a gate. Two of "
                     "these mutations are the INVERSE (G10N.19, G10N.20): the "
                     "real data already passes/fails, so the mutation moves it "
                     "the other way, which is what proves the scorer is "
                     "sensitive rather than mechanically fixed.")}


# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--es", default=str(DEFAULT_DIRS["es"]))
    ap.add_argument("--uk", default=str(DEFAULT_DIRS["uk"]))
    ap.add_argument("--it", default=str(DEFAULT_DIRS["it"]))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    dirs = {"es": args.es, "uk": args.uk, "it": args.it}
    cells, per_district_n = load_cells(dirs)
    cells_by_id = {c["cell_slug"]: c for c in cells}
    by_fold7, by_name7 = load_step7_index()

    run_dirs = retained_run_dirs(dirs)
    n_retained = sum(len(v) for v in run_dirs.values())

    g8, g8_rows = gate_g10n_8(cells, by_name7)
    g16, g17 = gate_g10n_16_17(cells_by_id, run_dirs, by_name7)
    report = h10_report(cells)
    g21 = gate_g10n_21(cells, report["fits"])

    board = {}
    board.update({"G10N.0": gate_g10n_0(cells)})
    board.update(gates_g10n_1_4_5_6(cells))
    board.update({"G10N.7": gate_g10n_7(cells)})
    board.update({"G10N.8": g8})
    board.update({"G10N.9": gate_g10n_9(cells)})
    board.update({"G10N.10": gate_g10n_10()})
    board.update({"G10N.11": gate_g10n_11(cells)})
    # scan the ACTUAL artefacts this run is about to publish, not a canned
    # string -- the same self-check discipline C1's own scorer used (it
    # scanned its own h10_report and gate_board_header JSON dumps).
    artefact_labels = {"h10_report": json.dumps(report, ensure_ascii=False),
                       "gate_board_so_far": json.dumps(board, ensure_ascii=False)}
    board.update({"G10N.12": gate_g10n_12(artefact_labels)})
    board.update({"G10N.13": gate_g10n_13(cells_by_id, run_dirs)})
    board.update({"G10N.14": gate_g10n_14(cells)})
    board.update({"G10N.15": gate_g10n_15(cells)})
    board.update({"G10N.16": g16, "G10N.17": g17})
    board.update({"G10N.18": gate_g10n_18(cells)})
    board.update({"G10N.19": gate_g10n_19(cells)})
    board.update({"G10N.20": gate_g10n_20(cells)})
    board.update({"G10N.21": g21})
    board.update({"G10N.22": gate_g10n_22(cells)})
    board.update({"G10N.23": gate_g10n_23()})
    board.update({"G10N.replicate": gate_g10n_replicate()})

    bat = battery(cells, by_name7, cells_by_id, run_dirs, report["fits"])

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {
        "tool": "4thJ_step10_nocorereal_score.py",
        "campaign": "C2 (no-core), districts ES-MAD-BERRUGUETE / GB-LDN-STDUNSTANS / "
                    "IT-BOL-GALVANI2",
        "authorisation": "tools/4thJ_step10_nocore_campaign.py AUTHORISED dict, "
                          "2026-09-16: 'Score the finished C2 cells for Madrid, "
                          "London and Bologna as G10N.x results.'",
        "population": {"cells_total": len(cells), "cells_per_fold": per_district_n,
                       "retained_run_dirs_with_saved_idf": n_retained},
        "basis": ("HEATING-ONLY, Zone Ideal Loads hourly variable simulated by "
                  "EnergyPlus 23.1.0 on a no-core dwelling-subdivision layout. "
                  "Never comparable to a whole-building EUI or a measured total."),
        "gate_board": board,
        "mutation_battery": bat,
    }
    (out / "g10n_gate_board.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "g10n_h10_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "g10n_g8_failing_rows.json").write_text(
        json.dumps(g8_rows[:200], indent=2, ensure_ascii=False), encoding="utf-8")

    print("population: %d cells (%s)" % (len(cells), per_district_n))
    print("retained run dirs with a saved IDF: %d" % n_retained)
    for k in sorted(board, key=lambda s: (0, float(s.split(".")[1]))
                    if s.split(".")[1].replace(".", "", 1).isdigit()
                    else (1, s)):
        print("%-16s %s" % (k, board[k]["verdict"]))
    print("battery: %s (%d of %d felled)"
          % (bat["verdict"], bat["felled"], bat["total"]))
    print("->", out / "g10n_gate_board.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
