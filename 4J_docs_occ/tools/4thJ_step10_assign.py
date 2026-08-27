# -*- coding: utf-8 -*-
"""4J Step 10, work item 10.4 --- PER-DWELLING DIARY ASSIGNMENT AND EMISSION.

    "The annual mean of phi_int is exactly 3.0 W/m2 PER ZONE and PER BUILDING at
     every f, asserted on the EMITTED CSV ON DISK, with the numeric bound derived
     from the write format --- not asserted in the generator."   (Step 10, §9)

WHAT THIS FILE IS
-----------------
`N_u` INDEPENDENT diaries per building, one per dwelling zone, drawn from the fold
that held the building's country out, with the seed recorded per
`(building_id, unit_index)`; `phi_int` emitted PER ZONE; and the gates that make
that checkable, each one exercised by a perturbation that fells it.

It is NOT a campaign.  The work-item table's gate column for 10.4 reads `no`.
No EnergyPlus is run here and none is owed --- that is 10.5 / 10.6, and both wait
on 10.3 / OpenUBEM `EU-04`.

WHY IT CAN BE WRITTEN BEFORE THE 4J GEOMETRY EXISTS
---------------------------------------------------
10.4's declared dependencies are 10.1 (closed) and the Step 7 pools (on disk).
The tool consumes a BUILDING TABLE with the columns OpenUBEM's own manifests
already carry, so when that table is the 4J one nothing here changes.

FOUR TRAPS, AND EACH IS A DECISION THIS FILE HAD TO TAKE
--------------------------------------------------------
  * `FINDING 132` is the conservation clause holding in the GENERATOR and not in
    the ARTEFACT --- 4.01e-07 relative at `%.6f`.  With `N_u` series it can now
    also fail PER ZONE while the building mean is right, so `G10.13` re-reads
    every emitted CSV off disk and never trusts the list it just wrote.
  * PER BUILDING IS AREA-WEIGHTED.  phi_int is W/m2, so the building mean is
    sum(A_z * mean phi_z) / sum(A_z).  With EQUAL zone areas that arm is
    satisfied trivially, which is a vacuity of the `FINDING 95` / `FINDING 127`
    shape --- so a perturbation with UNEQUAL areas is mandatory, and it is in
    the battery.
  * THE ARM COMES FROM `zone_source`, NEVER FROM `zone_count`.  A building with
    `zone_count = 4` under `FALLBACK_ONE_ZONE_PER_FLOOR` is four STOREYS, not
    four dwellings.  Assigning it four independent diaries would manufacture the
    exact diversity `H10` exists to test for.
  * ARM F GETS ONE DIARY FOR THE WHOLE BUILDING, repeated across its storey
    zones.  The fallback spatially averages non-coincident gains by construction
    (`G10.22` labels it a lower bound); pretending each storey is an independent
    household would hide the bias that makes it one.

The multiplier algebra, the write format and the residue bound are IMPORTED from
`4thJ_step8_scenario.py` rather than restated, so the property work item 8.4
probed is the property that runs here.
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7", "schedules")
OUT = os.path.join(PROJ, "Step10_docs", "outputs_step10")
CAMPAIGN8 = os.path.join(PROJ, "Step8_docs", "outputs_step8", "injected_campaign.json")
PREREG = os.path.join(PROJ, "Step6_docs", "outputs_step6", "prereg.md")
PREREG_MD5 = "e4243e07cdd80c9c846b91f40e3e8c45"

_spec = importlib.util.spec_from_file_location(
    "s8scen", os.path.join(HERE, "4thJ_step8_scenario.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

# ---------------------------------------------------------------------------
# constants that are DECISIONS, not defaults
# ---------------------------------------------------------------------------

#: Work item 8.5 wrote at 10 decimals, so the residue bound is 0.5e-10 rather
#: than the 0.5e-6 that let `FINDING 132` through.  Not re-tuned here.
WRITE_DECIMALS = 10

#: `D-S8-2` item 5 (c), imported so the sweep cannot drift between steps.
SWEEP_F = S.SWEEP_F
PHI_MEAN = S.PHI_INT_MEAN_W_M2          # 3.0 W/m2
HOURS = S.HOURS                         # 8760

#: Decision 11 / `G8.16`: a cell's schedules come from the fold that held its
#: country OUT.  Identity by construction --- fold `es` is the fold Spain was
#: held out of.  Written as a table anyway so a fourth country cannot be added
#: by accident.
COUNTRY_TO_FOLD = {"ES": "es", "GB": "uk", "UK": "uk", "IT": "it"}

#: `G10.19`: the `H10` test needs a population at both ends.
H10_MIN_BUILDINGS_PER_FOLD = 30
H10_MIN_NU = 2

ARM_D_SOURCE = "EUROPEAN_DWELLING_LAYOUT"
ARM_F_SOURCE = "FALLBACK_ONE_ZONE_PER_FLOOR"


def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# the Step 7 side, located BY CONTENT
# ---------------------------------------------------------------------------
def reported_bundles(campaign=CAMPAIGN8):
    """WHICH bundles are the reported ones -- read from the campaign, not globbed.

    🔴 Globbing `schedules/` is WRONG and it was caught by doing it. That directory
    also holds `leg4_*`, the `_cal<year>` survey-calendar variants, and seven
    `perturb_*` bundles built to be malformed. `perturb_hours_8759` has 8,759 values
    and blew up the reader on the first run -- which is the reader refusing, and the
    reason nothing silently trained on a short year.

    🔴 AND A MANIFEST FILTER ALONE IS NOT ENOUGH. `perturb_null`'s manifest is
    indistinguishable from a production one -- same leg, fold, rule, seed, rotation,
    and an all-`None` perturbation block, because the null perturbation IS "change
    nothing". So the authority is the campaign's own `schedule_bundles` field, the
    same artefact `G8.16` traces, and the manifest check below is a second opinion
    rather than the first.
    """
    man = json.load(io.open(campaign, encoding="utf-8"))
    names = sorted(set((man.get("schedule_bundles") or {}).values()))
    if not names:
        raise ValueError("%s names no schedule_bundles" % campaign)
    return names


def check_bundle(man, name):
    """Second opinion on a bundle the campaign already named. Returns [] or reasons."""
    bad = []
    if man.get("leg") != "leg5":
        bad.append("leg=%r" % man.get("leg"))
    if man.get("rule") != "independent" or man.get("seed") != 1:
        bad.append("rule/seed=%r/%r" % (man.get("rule"), man.get("seed")))
    if man.get("rotated_to_midnight") is not True:
        bad.append("rotated_to_midnight=%r" % man.get("rotated_to_midnight"))
    if man.get("year") != 2017:
        bad.append("year=%r" % man.get("year"))
    if man.get("n_values_per_schedule_expected") != HOURS:
        bad.append("n_values=%r" % man.get("n_values_per_schedule_expected"))
    p = man.get("perturbations") or {}
    if any(v not in (None, False, 0.0) for v in p.values()):
        bad.append("perturbations=%r" % p)
    return bad


def step7_index(root=SCHED7, bundles=None):
    """{fold: [(filename, md5, path)]} plus {filename: [(bundle, fold, md5)]}.

    The fold is read from each bundle's OWN `manifest.json`. `G8.16` was written
    that way for a reason: a filename convention is a claim about a file, and the
    manifest is the file's own statement about itself.

    `bundles` defaults to the REPORTED set named by the Step 8 campaign.
    """
    by_fold, by_name = {}, {}
    want = set(bundles) if bundles else set(reported_bundles())
    seen, rejected = [], {}
    for b in sorted(os.listdir(root)):
        d = os.path.join(root, b)
        mp = os.path.join(d, "manifest.json")
        if not os.path.isdir(d) or not os.path.exists(mp):
            continue
        if b not in want:
            continue
        man = json.load(io.open(mp, encoding="utf-8"))
        bad = check_bundle(man, b)
        if bad:
            rejected[b] = bad
            continue
        seen.append(b)
        fold = man.get("fold")
        for f in sorted(os.listdir(d)):
            if f.startswith("presence_") and f.endswith(".csv"):
                p = os.path.join(d, f)
                m5 = md5_of_file(p)
                by_fold.setdefault(fold, []).append((f, m5, p))
                by_name.setdefault(f, []).append((b, fold, m5))
    if rejected:
        raise ValueError("bundle(s) named by the campaign failed the manifest "
                         "check and this is NOT something to route around: %r" % rejected)
    missing = sorted(want - set(seen))
    if missing:
        raise ValueError("campaign names bundle(s) that are not on disk: %r" % missing)
    return by_fold, by_name


# ---------------------------------------------------------------------------
# the building table
# ---------------------------------------------------------------------------
def read_building_table(path, country_override=None):
    """OpenUBEM's own manifest columns, read as they are shipped."""
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            zc = int(float(r.get("zone_count") or 0))
            if zc <= 0:
                continue
            country = (r.get("country") or country_override or "").strip().upper()
            area = float(r.get("footprint_area_m2") or 0.0)
            # Per-zone areas if the table carries them; otherwise an EQUAL split,
            # declared as an assumption -- the real per-zone areas arrive with the
            # dwelling layout, and equal areas are exactly the case that makes the
            # area-weighted arm of G10.13 green for the wrong reason.
            if r.get("zone_areas_m2"):
                areas = [float(x) for x in r["zone_areas_m2"].split("|")]
                areas_basis = "declared"
            else:
                areas = [area / zc] * zc if area > 0 else [1.0] * zc
                areas_basis = "assumed_equal"
            rows.append({
                "building_id": r["building_id"],
                "country": country,
                "zone_count": zc,
                "zone_source": (r.get("zone_source") or "").strip(),
                "layout_status": (r.get("layout_status") or "").strip(),
                "footprint_area_m2": area,
                "zone_areas_m2": areas,
                "zone_areas_basis": areas_basis,
            })
    return rows


def arm_of(row):
    """ARM FROM `zone_source`, NEVER FROM `zone_count` -- see the module header."""
    if row["zone_source"] == ARM_D_SOURCE:
        return "D"
    if row["zone_source"] == ARM_F_SOURCE:
        return "F"
    return "UNASSIGNED"


# ---------------------------------------------------------------------------
# assignment
# ---------------------------------------------------------------------------
def assign(rows, by_fold, seed_base=1, arm_from_zone_count=False,
           force_fold=None, arm_f_independent=False, mislabel_fold=None):
    """One row per (building_id, unit_index).  Seed recorded per dwelling.

    The three keyword flags exist ONLY for the perturbation battery.  Every one
    of them is a defect this file argues against in its own header, and each is
    wired to fell a named gate.
    """
    out, skipped = [], []
    for row in rows:
        arm = arm_of(row)
        if arm_from_zone_count:                       # PERTURBATION
            arm = "D" if row["zone_count"] > 1 else "F"
        if arm == "UNASSIGNED":
            skipped.append({"building_id": row["building_id"],
                            "reason": "zone_source %r is neither %s nor %s"
                                      % (row["zone_source"], ARM_D_SOURCE, ARM_F_SOURCE)})
            continue
        fold = force_fold or COUNTRY_TO_FOLD.get(row["country"])
        if not fold:
            skipped.append({"building_id": row["building_id"],
                            "reason": "no fold for country %r" % row["country"]})
            continue
        pool = by_fold.get(fold) or []
        if not pool:
            skipped.append({"building_id": row["building_id"],
                            "reason": "fold %r has no presence files on disk" % fold})
            continue

        nz = row["zone_count"]
        # ARM F: ONE diary for the whole building, repeated across storey zones.
        independent = (arm == "D") or arm_f_independent
        rng = random.Random("%s|%s|%d" % (row["building_id"], fold, seed_base))
        if independent:
            picks = ([rng.choice(pool) for _ in range(nz)] if nz > len(pool)
                     else rng.sample(pool, nz))
        else:
            picks = [rng.choice(pool)] * nz

        for u in range(nz):
            name, m5, path = picks[u]
            # PERTURBATION `mislabel_fold`: the diary really is drawn from `fold`,
            # but the dwelling RECORDS a different one -- a genuine cross-fold drive.
            # 🔴 The first attempt at this perturbation set the fold to a name with no
            # pool, which skipped every building and left the gate with nothing to
            # score. It read PASS. A perturbation that empties the population does not
            # test the gate, it removes it.
            declared = mislabel_fold or fold
            out.append({
                "building_id": row["building_id"], "unit_index": u,
                "arm": arm, "country": row["country"], "fold": declared,
                "zone_area_m2": row["zone_areas_m2"][u],
                "zone_areas_basis": row["zone_areas_basis"],
                "presence_file": name, "presence_md5": m5, "presence_path": path,
                # 🔴 The seed is recorded PER DWELLING, per §9. A per-building seed
                # would make one dwelling's draw unreproducible without replaying
                # every other dwelling in the same building.
                "seed": "%s|%s|%d|u%d" % (row["building_id"], fold, seed_base, u),
                "independent": independent,
            })
    return out, skipped


# ---------------------------------------------------------------------------
# emission --- one multiplier CSV per zone per f
# ---------------------------------------------------------------------------
RETAIN_BUILDINGS = 2        # how many buildings keep their CSVs on disk


def emit(assignments, outdir, f_values=SWEEP_F, decimals=WRITE_DECIMALS,
         perturb_zone=None, retain=RETAIN_BUILDINGS, on_written=None):
    """Writes `<outdir>/f<ff>/<building>/u<NN>.csv`. Returns the emission table.

    🔴 REDUCED IN FLIGHT, and declared rather than discovered. The exercise table
    emits 7,880 hourly CSVs at 8,760 lines each -- 2.6 GB for ONE run, and the
    perturbation battery runs it six times. Step 8 met this exactly (9,000 retained
    run directories is a quarter of a terabyte) and answered it the same way: score
    the artefact as it is written, keep a named sample, delete the rest.

    🔴 THE GATE STILL READS EVERY FILE OFF DISK. `on_written` is called on the file
    the moment it exists, before it can be removed, so `V10.h` -- "conservation
    asserted on disk, never on the generator's list" -- is unaffected. What is
    dropped is the artefact, never the measurement.
    """
    emitted = []
    keep = sorted({a["building_id"] for a in assignments})[:retain]
    for a in assignments:
        g = S.read_presence(a["presence_path"])
        for f in f_values:
            m = S.multiplier_series(g, f)
            if perturb_zone is not None and a["unit_index"] == perturb_zone and f > 0:
                # PERTURBATION: one zone's series scaled off its own mean. The
                # BUILDING mean stays close while THIS ZONE is wrong -- the
                # failure mode N_u series make possible and G10.13 exists for.
                m = [x * 1.02 for x in m]
            d = os.path.join(outdir, "f%.2f" % f, a["building_id"])
            dst = os.path.join(d, "u%02d.csv" % a["unit_index"])
            S.write_multiplier_csv(dst, m, "PhiMult", decimals=decimals)
            rec = {"building_id": a["building_id"],
                   "unit_index": a["unit_index"], "arm": a["arm"],
                   "fold": a["fold"], "f": f, "csv": dst,
                   "zone_area_m2": a["zone_area_m2"], "retained": False}
            if on_written is not None:
                on_written(rec)          # read from disk BEFORE anything is removed
            if a["building_id"] in keep:
                rec["retained"] = True
            else:
                os.remove(dst)
            emitted.append(rec)
    for root, dirs, files in os.walk(outdir, topdown=False):
        if not dirs and not files:
            os.rmdir(root)
    return emitted


def read_emitted_mean(path):
    """Re-read the file EnergyPlus would read. NEVER the list we just wrote."""
    with io.open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() != ""]
    vals = [float(x) for x in lines[1:]]
    if len(vals) != HOURS:
        raise ValueError("%s has %d values, expected %d" % (path, len(vals), HOURS))
    return sum(vals) / len(vals), len(vals)


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def gate_g10_13(emitted, decimals=WRITE_DECIMALS, means=None):
    """Annual mean phi_int == 3.0 W/m2 PER ZONE and PER BUILDING, from disk.

    The bound is DERIVED FROM THE WRITE FORMAT -- half a unit in the last place
    -- so the caller chooses it rather than measuring it after the fact.
    """
    bound_mult = 0.5 * 10 ** (-decimals)
    bound_phi = PHI_MEAN * bound_mult
    rows, zone_fail, bldg_fail = [], 0, 0
    per_building = {}
    for e in emitted:
        key = (e["csv"], e["f"])
        if means is not None and key in means:
            mean_m, n = means[key]      # read off disk at write time, before reduction
        else:
            mean_m, n = read_emitted_mean(e["csv"])
        phi = PHI_MEAN * mean_m
        ok = abs(phi - PHI_MEAN) <= bound_phi
        if not ok:
            zone_fail += 1
        rows.append({"scope": "zone", "building_id": e["building_id"],
                     "unit_index": e["unit_index"], "f": e["f"],
                     "mean_phi_w_m2": phi, "abs_dev": abs(phi - PHI_MEAN),
                     "bound": bound_phi, "verdict": "PASS" if ok else "FAIL",
                     "n_values": n, "read_from": e["csv"]})
        key = (e["building_id"], e["f"])
        per_building.setdefault(key, []).append((e["zone_area_m2"], phi))

    for (bid, f), zs in sorted(per_building.items()):
        # AREA-WEIGHTED. phi_int is W/m2; an unweighted mean would be a different
        # quantity that happens to agree whenever the zones are equal.
        tot_a = sum(a for a, _ in zs)
        if tot_a <= 0:
            continue
        phi_b = sum(a * p for a, p in zs) / tot_a
        ok = abs(phi_b - PHI_MEAN) <= bound_phi
        if not ok:
            bldg_fail += 1
        rows.append({"scope": "building", "building_id": bid, "unit_index": "",
                     "f": f, "mean_phi_w_m2": phi_b,
                     "abs_dev": abs(phi_b - PHI_MEAN), "bound": bound_phi,
                     "verdict": "PASS" if ok else "FAIL",
                     "n_values": len(zs), "read_from": "area-weighted over zones"})
    if not emitted:
        return {"gate": "G10.13", "verdict": "NOT_EVALUABLE", "bound_w_m2": bound_phi,
                "decimals": decimals, "zone_rows": 0, "zone_fails": 0,
                "building_fails": 0,
                "note": "nothing was emitted, so conservation was never asserted. "
                        "NOT a pass."}, []
    verdict = "PASS" if (zone_fail == 0 and bldg_fail == 0) else "FAIL"
    return {"gate": "G10.13", "verdict": verdict, "bound_w_m2": bound_phi,
            "decimals": decimals, "zone_rows": len(emitted),
            "zone_fails": zone_fail, "building_fails": bldg_fail,
            "note": "read from the emitted CSV on disk (V10.h), never from the "
                    "generator's own list"}, rows


def gate_g10_8(assignments, by_name):
    """Per DWELLING: the diary is located by CONTENT and its fold is the cell's."""
    bad_locate, bad_fold, rows = 0, 0, []
    for a in assignments:
        cands = by_name.get(a["presence_file"], [])
        hit = [(b, fl) for (b, fl, m5) in cands if m5 == a["presence_md5"]]
        if not hit:
            bad_locate += 1
            rows.append({"building_id": a["building_id"], "unit_index": a["unit_index"],
                         "verdict": "FAIL", "why": "%s md5 %s is in no bundle on disk"
                                                   % (a["presence_file"], a["presence_md5"][:12])})
            continue
        folds = sorted({fl for _b, fl in hit})
        ok = len(folds) == 1 and folds[0] == a["fold"]
        if not ok:
            bad_fold += 1
            rows.append({"building_id": a["building_id"], "unit_index": a["unit_index"],
                         "verdict": "FAIL",
                         "why": "bundle declares fold %s; the dwelling is %s"
                                % (",".join(folds), a["fold"])})
    # 🔴 FOUND BY THE BATTERY, 2026-08-26. The first `force_fold` perturbation left
    # ZERO dwellings (every building was skipped for want of a pool) and this gate
    # returned PASS -- 0 unlocatable, 0 wrong-fold, therefore green. A gate whose
    # population is empty has not been satisfied, it has not been ASKED. That is the
    # `FINDING 95` / `FINDING 127` vacuity, and it is why the perturbation read MISS.
    if not assignments:
        return {"gate": "G10.8", "verdict": "NOT_EVALUABLE", "dwellings": 0,
                "unlocatable": 0, "wrong_fold": 0,
                "note": "no dwellings were assigned, so there is no fold to "
                        "mis-drive. NOT a pass."}, []
    verdict = "PASS" if (bad_locate == 0 and bad_fold == 0) else "FAIL"
    return {"gate": "G10.8", "verdict": verdict, "dwellings": len(assignments),
            "unlocatable": bad_locate, "wrong_fold": bad_fold,
            "note": "per DWELLING, not per building; the fold is read from the "
                    "bundle's own manifest.json, never from a filename"}, rows


def gate_g10_9(assignments):
    """Arm D and Arm F must never be pooled in one statistic."""
    mixed = sorted({a["building_id"] for a in assignments
                    if len({b["arm"] for b in assignments
                            if b["building_id"] == a["building_id"]}) > 1})
    arms = sorted({a["arm"] for a in assignments})
    return {"gate": "G10.9", "verdict": "PASS" if not mixed else "FAIL",
            "arms_present": arms, "buildings_with_mixed_arms": len(mixed),
            "note": "a building carrying both arms means the arm was decided per "
                    "zone; it is a property of the BUILDING's zone_source"}


def gate_g10_19(assignments):
    """H10 vacuity. NOT_EVALUABLE names the population -- never a pass, never a fail."""
    per_fold = {}
    for a in assignments:
        if a["arm"] != "D":
            continue
        per_fold.setdefault(a["fold"], {}).setdefault(a["building_id"], 0)
        per_fold[a["fold"]][a["building_id"]] += 1
    counts = {fl: sum(1 for _b, n in bs.items() if n >= H10_MIN_NU)
              for fl, bs in per_fold.items()}
    short = {fl: n for fl, n in counts.items() if n < H10_MIN_BUILDINGS_PER_FOLD}
    missing = [fl for fl in ("es", "uk", "it") if fl not in counts]
    ok = not short and not missing
    return {"gate": "G10.19",
            "verdict": "PASS" if ok else "NOT_EVALUABLE",
            "required_per_fold": H10_MIN_BUILDINGS_PER_FOLD,
            "min_N_u": H10_MIN_NU,
            "qualifying_buildings_per_fold": counts,
            "folds_short": short, "folds_absent": missing,
            "note": "below the population H10 is NOT_EVALUABLE with the population "
                    "named. It is never reported as a pass and never as a fail."}


# ---------------------------------------------------------------------------
def write_outputs(outdir, assignments, skipped, emitted, board, g13_rows, g8_rows,
                  meta):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    with io.open(os.path.join(outdir, "assignment_table.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["building_id", "unit_index", "arm", "country", "fold",
                    "zone_area_m2", "zone_areas_basis", "presence_file",
                    "presence_md5", "seed", "independent"])
        for a in assignments:
            w.writerow([a["building_id"], a["unit_index"], a["arm"], a["country"],
                        a["fold"], "%.4f" % a["zone_area_m2"], a["zone_areas_basis"],
                        a["presence_file"], a["presence_md5"], a["seed"],
                        a["independent"]])
    with io.open(os.path.join(outdir, "conservation_g10_13.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["scope", "building_id", "unit_index", "f",
                                           "mean_phi_w_m2", "abs_dev", "bound",
                                           "verdict", "n_values", "read_from"])
        w.writeheader()
        for r in g13_rows:
            w.writerow(r)
    payload = dict(meta)
    payload.update({"gate_board": board, "n_assignments": len(assignments),
                    "n_emitted_csv": len(emitted), "skipped": skipped,
                    "g10_8_failures": g8_rows[:200]})
    with io.open(os.path.join(outdir, "assignment_report.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(payload, indent=2, sort_keys=True))


def run(table, outdir, country_override=None, seed_base=1, f_values=SWEEP_F,
        decimals=WRITE_DECIMALS, bundles=None, label="",
        arm_from_zone_count=False, force_fold=None, arm_f_independent=False,
        perturb_zone=None, break_md5=False, unequal_areas=False,
        mislabel_fold=None, quiet=False):
    rows = read_building_table(table, country_override)
    if unequal_areas:
        # PERTURBATION: real, very unequal zone areas. Equal areas make the
        # area-weighted arm of G10.13 true by symmetry; this is what stops that
        # arm being vacuous.
        for r in rows:
            n = r["zone_count"]
            tot = sum(r["zone_areas_m2"])
            w = [(i + 1) ** 3 for i in range(n)]
            sw = float(sum(w))
            r["zone_areas_m2"] = [tot * x / sw for x in w]
            r["zone_areas_basis"] = "perturbed_unequal"
    by_fold, by_name = step7_index(bundles=bundles)
    assignments, skipped = assign(rows, by_fold, seed_base=seed_base,
                                  arm_from_zone_count=arm_from_zone_count,
                                  force_fold=force_fold,
                                  arm_f_independent=arm_f_independent,
                                  mislabel_fold=mislabel_fold)
    if break_md5:
        # PERTURBATION: the recorded md5 no longer matches the file it names.
        for a in assignments:
            a["presence_md5"] = "0" * 32
    means = {}

    def _read_on_disk(rec):
        # 🔴 V10.h: the number comes from the FILE, at the moment the file exists.
        means[(rec["csv"], rec["f"])] = read_emitted_mean(rec["csv"])

    emitted = emit(assignments, outdir, f_values=f_values, decimals=decimals,
                   perturb_zone=perturb_zone, on_written=_read_on_disk)
    g13, g13_rows = gate_g10_13(emitted, decimals=decimals, means=means)
    g8, g8_rows = gate_g10_8(assignments, by_name)
    board = {"G10.13": g13, "G10.8": g8, "G10.9": gate_g10_9(assignments),
             "G10.19": gate_g10_19(assignments)}
    live = md5_of_file(PREREG) if os.path.exists(PREREG) else "MISSING"
    board["W10.8"] = {"gate": "W10.8", "verdict": "PASS" if live == PREREG_MD5 else "FAIL",
                      "live": live, "recorded": PREREG_MD5,
                      "note": "prereg.md is frozen; recomputed from disk"}
    meta = {"label": label, "building_table": table, "n_buildings": len(rows),
            "n_csv_retained": sum(1 for e in emitted if e["retained"]),
            "reduction_note": "every emitted CSV was READ FROM DISK by G10.13 at the "
                              "moment it was written; only a named sample is kept, "
                              "because 7,880 hourly files is 2.6 GB per run and the "
                              "battery runs it six times (the Step 8 precedent)",
            "seed_base": seed_base, "write_decimals": decimals,
            "f_values": list(f_values), "country_override": country_override,
            "perturbations": {"arm_from_zone_count": arm_from_zone_count,
                              "force_fold": force_fold,
                              "arm_f_independent": arm_f_independent,
                              "mislabel_fold": mislabel_fold,
                              "perturb_zone": perturb_zone,
                              "break_md5": break_md5,
                              "unequal_areas": unequal_areas}}
    write_outputs(outdir, assignments, skipped, emitted, board, g13_rows, g8_rows, meta)
    if not quiet:
        print("  buildings %d  dwellings %d  emitted CSV %d  skipped %d"
              % (len(rows), len(assignments), len(emitted), len(skipped)))
        for k in ("G10.13", "G10.8", "G10.9", "G10.19", "W10.8"):
            b = board[k]
            print("  %-7s %-14s %s" % (k, b["verdict"],
                                       {kk: vv for kk, vv in b.items()
                                        if kk not in ("gate", "verdict", "note")}))
    return board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="building table CSV")
    ap.add_argument("--out", default=os.path.join(OUT, "assign"))
    ap.add_argument("--country", default=None,
                    help="country code when the table does not carry one")
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--decimals", type=int, default=WRITE_DECIMALS)
    ap.add_argument("--bundles", default=None,
                    help="comma-separated Step 7 bundle names to index")
    ap.add_argument("--label", default="")
    ap.add_argument("--perturb", action="store_true",
                    help="run the battery: every gate must be SEEN FAILING")
    a = ap.parse_args()
    bundles = a.bundles.split(",") if a.bundles else None

    print("=" * 78)
    print("work item 10.4 -- per-dwelling assignment and emission")
    print("=" * 78)
    print("BASELINE  %s" % a.label)
    board = run(a.table, a.out, country_override=a.country, seed_base=a.seed_base,
                decimals=a.decimals, bundles=bundles, label=a.label)
    fails = [k for k, v in board.items() if v["verdict"] == "FAIL"]
    if not a.perturb:
        return 1 if fails else 0

    print()
    print("PERTURBATION BATTERY -- a gate nobody has watched fail is an assumption")
    print("-" * 78)
    # 🔴 EACH CASE DECLARES THE VERDICT IT EXPECTS, and it is not always FAIL.
    # `G10.19` never returns FAIL -- a vacuity guard that could fail would be a
    # hypothesis test. Its defect mode is the opposite: saying PASS on a population
    # that was manufactured. So its perturbation is scored on flipping
    # NOT_EVALUABLE -> PASS, which is the gate proving it is sensitive to the arm
    # rule rather than proving it can go red.
    cases = [
        ("one zone scaled 1.02, building mean left near-right", "G10.13", "FAIL",
         dict(perturb_zone=0)),
        ("zone areas made VERY unequal (the area-weighted arm)", "G10.13", "FAIL",
         dict(unequal_areas=True, perturb_zone=0)),
        ("recorded md5 broken -- diary unlocatable by content", "G10.8", "FAIL",
         dict(break_md5=True)),
        ("every dwelling RECORDS a fold its diary did not come from", "G10.8", "FAIL",
         dict(mislabel_fold="it")),
        ("arm read from zone_count: storeys become an H10 population", "G10.19",
         "PASS", dict(arm_from_zone_count=True)),
        ("write format coarsened to 6 decimals (FINDING 132's residue)", "G10.13",
         "FAIL", dict(decimals=6, perturb_zone=0)),
    ]
    hits = 0
    for i, (name, target, expect, kw) in enumerate(cases):
        d = os.path.join(a.out, "_perturb%d" % i)
        try:
            b = run(a.table, d, country_override=a.country, seed_base=a.seed_base,
                    decimals=kw.pop("decimals", a.decimals), bundles=bundles,
                    label="perturb:%s" % name, quiet=True, **kw)
            v = b[target]["verdict"]
        except Exception as e:                       # a crash is NOT a FAIL
            v = "CRASH(%s)" % type(e).__name__
        hit = (v == expect)
        hits += 1 if hit else 0
        print("  %-56s %-7s want %-14s got %-14s %s"
              % (name[:56], target, expect, v, "HIT" if hit else "*** MISS ***"))
    print("-" * 78)
    print("battery: %d of %d moved their target gate to the declared verdict"
          % (hits, len(cases)))
    if hits != len(cases):
        print("*** A MISS is a gate that could not be made to fail. It is NOT a pass.")
    return 0 if (not fails and hits == len(cases)) else 1


if __name__ == "__main__":
    sys.exit(main())
