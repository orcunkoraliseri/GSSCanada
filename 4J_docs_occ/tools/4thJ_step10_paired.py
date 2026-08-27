# -*- coding: utf-8 -*-
"""4J Step 10, work item 10.9 --- PAIRED CASE A / CASE B EMISSION.

    "Every Step 10 building therefore runs TWICE at each f:
       Case A --- synchronised   : one diary, replicated to all N_u zones
       Case B --- independent    : N_u independently sampled diaries
     The effect is delta_div = Metric(B) - Metric(A), WITHIN FOOTPRINT."   (Step 10, section 6.6)

WHAT THIS FILE IS
-----------------
The pairing, emitted and scored.  It is the control that stops a diversity effect
being read off a geometry difference: buildings that carry different `N_u` also
carry different volume, envelope area and shape factor, so a CROSS-BUILDING
comparison confounds diversity with geometry.  `G10.20` is the gate.

WHAT THIS FILE IS NOT
---------------------
!! IT IS NOT THE `H10` TEST AND IT IS NOT `G10.21`.
`G10.21` scores `CF = P_peak,bldg / sum(P_peak,zone)` on SIMULATED BUILDING POWER.
No Step 10 cell has been simulated --- 10.5 / 10.6 own that, and both wait on 10.3
/ OpenUBEM `EU-04`.  What is measurable today is the coincidence factor of the
DRIVER, `phi_int`, and it is reported here under a different name, `CF_phi`, on a
`cf_basis` field that says so in every artefact.

  !! `CF_phi` IS NOT `CF`.  Heating demand peaks when gains are LOW, so the
  gain-channel peak and the demand peak are not the same hour and need not move
  together.  `G10.21` is scored `NOT_EVALUABLE` here WITH ITS POPULATION NAMED
  (`V10.b`), never PASS.  Quoting `CF_phi` as `CF` would be a basis change wearing
  a result's clothes --- the move `G10.12` and the gate-ID rule exist to refuse.

WHAT `CF_phi` IS GOOD FOR, AND IT IS NOT NOTHING
------------------------------------------------
`G10.21`(ii): "Case A returns `CF = 1.000` to the declared numeric bound --- it is
1 by construction, so a Case A `CF` != 1 is a defect in the HARNESS, not a result."
That arm is a statement about the emission, not about EnergyPlus, so it can be
checked NOW, before a single cell is simulated, and it is checked here as `W10.9`.
A harness that cannot return 1 on the synchronised case would have produced a
`CF(N)` curve from EnergyPlus that nobody could have separated from its own bug.

THE ONE READING THIS ITEM HAD TO TAKE, AND IT IS RECORDED BECAUSE TWO DOCUMENTS PULL
------------------------------------------------------------------------------------
Work item 10.4 ruled: ARM F GETS ONE DIARY FOR THE WHOLE BUILDING, repeated across
its storey zones, because "pretending each storey is an independent household would
hide the bias that makes it one" (`G10.22`, the lower-bound label).  Section 6.6 says
"EVERY Step 10 building therefore runs twice at each f" and that the pairing "makes
`H10` testable on Arm F geometry".  Read together:

  * 10.4 governs the PRODUCTION assignment --- the single Arm F cell that is the
    Step 8 configuration on real geometry.  Unchanged.  Nothing here edits it.
  * 10.9 is a PAIRED PROBE.  On Arm F, Case B's zones are STOREYS, not dwellings,
    so its delta_div measures diversity ACROSS STACKED STOREY ZONES.  That is the
    magnitude of the very averaging bias `G10.22` labels --- measured instead of
    asserted.  It is NEVER an `H10` dwelling population: `G10.19` counts Arm D
    only, and `G10.9` keeps the two arms out of one statistic.

Every emitted row carries `zone_semantics` = `dwelling` (Arm D) or `storey` (Arm F)
so no downstream reader has to reconstruct that from the arm letter.

WHAT CASE A REPLICATES, AND WHY THAT CHOICE IS ITSELF A FREE PARAMETER
----------------------------------------------------------------------
Case A replicates CASE B's UNIT-0 DRAW.  The pair then differs in exactly one
thing --- whether the other N_u-1 zones got their own diary --- and the seed policy
is literally the same stream, which is what `G10.20`'s "same seed policy" clause
asks for.

!! But WHICH diary is replicated is a free parameter, and on a peak channel a
free parameter can be worth more than the effect.  `FINDING 143` died exactly
there.  So the Case-A CHOICE SPREAD is reported beside every delta_div: with all
zones sharing one series, the building peak is `3.0 * sum(A_z) * max(m_u)`, so the
N_u alternative Case A's are computable from Case B's own zone series at zero extra
cost.  A delta_div smaller than that spread is NOT a diversity result, and the
table prints the ratio rather than leaving it to a reader.

THE ANNUAL CHANNEL IS DEAD HERE BY CONSTRUCTION, AND THAT IS WORTH PRINTING
---------------------------------------------------------------------------
`G10.13` holds the annual mean of `phi_int` at exactly 3.0 W/m2 per zone AND per
building at every f, in both cases.  Therefore the annual delta_div is identically
zero --- not small, zero --- and `H10` cannot live on it.  `W10.10` asserts it from
the emitted files rather than from that sentence.
"""
import argparse
import csv
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location(
    "s10assign", os.path.join(HERE, "4thJ_step10_assign.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
S = A.S

OUT = A.OUT
PHI_MEAN = A.PHI_MEAN
HOURS = A.HOURS
SWEEP_F = A.SWEEP_F
WRITE_DECIMALS = A.WRITE_DECIMALS

#: `G10.21`(ii) --- Case A is `CF = 1` BY CONSTRUCTION, so the bound is a
#: floating-point summation bound, not a tolerance on a physical quantity.
#: Declared here rather than measured after the fact.
CF_ONE_BOUND = 1e-12

PAIR_CASES = ("A", "B")


# ---------------------------------------------------------------------------
# reading the artefact, never the generator (V10.h)
# ---------------------------------------------------------------------------
def read_series(path):
    """The file EnergyPlus would read, as floats.  NEVER the list we just wrote."""
    with io.open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() != ""]
    vals = [float(x) for x in lines[1:]]
    if len(vals) != HOURS:
        raise ValueError("%s has %d values, expected %d" % (path, len(vals), HOURS))
    return vals


def percentile_linear(sorted_vals, q):
    """Linear-interpolation percentile on an ALREADY SORTED list.

    Declared, not assumed: `numpy.percentile`'s default and R's type 7.  A
    nearest-rank percentile would differ in the last digits and the two are not
    interchangeable in a residual table.
    """
    n = len(sorted_vals)
    if n == 0:
        raise ValueError("percentile of an empty series")
    if n == 1:
        return sorted_vals[0]
    pos = (q / 100.0) * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def cell_metrics(zone_series, areas):
    """Gain-channel metrics for ONE (building, case, f) cell, from the disk series.

    P_z(t) = A_z * 3.0 * m_z(t)  [W]        --- the zone's internal-gain power
    P_b(t) = sum_z P_z(t)        [W]        --- the building's

    `CF_phi = max_t P_b(t) / sum_z max_t P_z(t)`.  With one shared series this is
    exactly 1: numerator and denominator are the same sum times the same maximum.
    """
    n = len(zone_series)
    if n == 0 or len(areas) != n:
        raise ValueError("%d series against %d areas" % (n, len(areas)))
    p_b = [0.0] * HOURS
    sum_peak_zone = 0.0
    zone_peaks = []
    for z in range(n):
        a = areas[z]
        s = zone_series[z]
        pk = max(s) * a * PHI_MEAN
        zone_peaks.append(pk)
        sum_peak_zone += pk
        for t in range(HOURS):
            p_b[t] += a * PHI_MEAN * s[t]
    peak_b = max(p_b)
    srt = sorted(p_b)
    # !! FINDING 158's measurement, taken per cell rather than argued once in prose:
    # how many hours have EVERY zone simultaneously at its own maximum. If that
    # count is > 0 the coincidence factor is 1 EXACTLY, for any N_u and any f, and
    # no diversity can appear on this channel.
    zmax = [max(s) for s in zone_series]
    all_at_max = 0
    for t in range(HOURS):
        for z in range(n):
            if zone_series[z][t] != zmax[z]:
                break
        else:
            all_at_max += 1
    return {
        "n_zones": n,
        "peak_w": peak_b,
        "sum_zone_peak_w": sum_peak_zone,
        "cf_phi": (peak_b / sum_peak_zone) if sum_peak_zone > 0 else float("nan"),
        "p99_w": percentile_linear(srt, 99.0),
        "mean_w": sum(p_b) / HOURS,
        "peak_hour": p_b.index(peak_b),
        "zone_peak_w": zone_peaks,
        "hours_all_zones_at_max": all_at_max,
        "total_area_m2": sum(areas),
    }


# ---------------------------------------------------------------------------
# the pairing
# ---------------------------------------------------------------------------
def build_pairs(rows, by_fold, seed_base=1, arm_from_zone_count=False,
                force_fold=None, mislabel_fold=None, case_a_independent=False,
                drop_case_a=None):
    """Case B first --- it IS 10.4's assignment --- then Case A derived from it.

    !! Case B is produced by `4thJ_step10_assign.assign(...,
    arm_f_independent=True)`.  On ARM D that call reproduces the production draws
    BIT FOR BIT (the RNG is seeded per building and Arm D was already independent),
    which is asserted by `W10.11` rather than assumed.  On ARM F it is the paired
    probe the module header argues for.
    """
    case_b, skipped = A.assign(rows, by_fold, seed_base=seed_base,
                               arm_from_zone_count=arm_from_zone_count,
                               force_fold=force_fold, arm_f_independent=True,
                               mislabel_fold=mislabel_fold)
    for r in case_b:
        r["case"] = "B"
        r["zone_semantics"] = "dwelling" if r["arm"] == "D" else "storey"
        r["replicated_from_unit"] = ""

    by_b = {}
    for r in case_b:
        by_b.setdefault(r["building_id"], []).append(r)

    case_a = []
    for bid, units in by_b.items():
        units = sorted(units, key=lambda x: x["unit_index"])
        if drop_case_a is not None and bid == drop_case_a:
            # PERTURBATION: the synchronised partner of a real building is missing.
            # G10.20 must REFUSE the pair, not quietly compare it to another
            # building's Case A.
            continue
        if case_a_independent:
            # PERTURBATION: Case A given N_u INDEPENDENT diaries. It is then not
            # synchronised at all, so CF_phi != 1 --- the harness defect
            # `G10.21`(ii) names, and W10.9 is the thing that must catch it.
            src = units
        else:
            src = [units[0]] * len(units)
        for u, s in enumerate(src):
            r = dict(units[u])          # geometry/fold/area of THIS zone
            r["case"] = "A"
            r["presence_file"] = s["presence_file"]
            r["presence_md5"] = s["presence_md5"]
            r["presence_path"] = s["presence_path"]
            r["seed"] = s["seed"]
            r["independent"] = bool(case_a_independent)
            r["replicated_from_unit"] = "" if case_a_independent else 0
            case_a.append(r)
    return case_a + case_b, skipped


# ---------------------------------------------------------------------------
# emission --- one CSV per zone per case per f, read back off disk at once
# ---------------------------------------------------------------------------
def emit_paired(assignments, outdir, f_values=SWEEP_F, decimals=WRITE_DECIMALS,
                perturb_zone=None, retain_ids=(), on_written=None):
    """`<outdir>/case<A|B>/f<ff>/<building>/u<NN>.csv`, then metrics per cell.

    !! REDUCED IN FLIGHT, DECLARED NOT DISCOVERED --- the 10.4 precedent
    verbatim.  The paired emission is 2x 10.4's, so every file is READ FROM DISK
    the moment it exists (`on_written`, and the metric series comes from the same
    read), and only the named sample survives.  What is dropped is the artefact,
    never the measurement.
    """
    emitted, metrics = [], {}
    groups = {}
    for a in assignments:
        groups.setdefault((a["building_id"], a["case"]), []).append(a)
    for (bid, case) in sorted(groups):
        units = sorted(groups[(bid, case)], key=lambda x: x["unit_index"])
        cache = {}
        for f in f_values:
            series, areas, digests = [], [], []
            for a in units:
                if a["presence_path"] not in cache:
                    cache[a["presence_path"]] = S.read_presence(a["presence_path"])
                m = S.multiplier_series(cache[a["presence_path"]], f)
                if perturb_zone is not None and a["unit_index"] == perturb_zone and f > 0:
                    # PERTURBATION: one zone off its own mean; the BUILDING mean
                    # stays near-right. The failure N_u series make possible.
                    m = [x * 1.02 for x in m]
                dst = os.path.join(outdir, "case%s" % case, "f%.2f" % f, bid,
                                   "u%02d.csv" % a["unit_index"])
                S.write_multiplier_csv(dst, m, "PhiMult", decimals=decimals)
                vals = read_series(dst)           # <-- from the FILE, V10.h
                # The digest is of the EMITTED BYTES, taken before the file can be
                # removed. `W10.9` needs it: on this artefact CF = 1 does NOT
                # discriminate a synchronised cell from an independent one
                # (`FINDING 158`), and series identity does.
                sha = S.sha256(dst)
                rec = {"building_id": bid, "unit_index": a["unit_index"],
                       "arm": a["arm"], "fold": a["fold"], "case": case, "f": f,
                       "csv": dst, "sha256": sha, "zone_area_m2": a["zone_area_m2"],
                       "zone_semantics": a["zone_semantics"], "retained": False}
                if on_written is not None:
                    on_written(rec, vals)
                if bid in retain_ids:
                    rec["retained"] = True
                else:
                    os.remove(dst)
                emitted.append(rec)
                series.append(vals)
                areas.append(a["zone_area_m2"])
                digests.append(sha)
            met = cell_metrics(series, areas)
            met.update({"building_id": bid, "case": case, "f": f,
                        "arm": units[0]["arm"], "fold": units[0]["fold"],
                        "country": units[0]["country"],
                        "zone_semantics": units[0]["zone_semantics"],
                        "zone_areas_m2": areas, "zone_digests": digests,
                        "cf_basis": "phi_int_gain_channel_NOT_simulated_power"})
            metrics[(bid, case, f)] = met
    for root, dirs, files in os.walk(outdir, topdown=False):
        if not dirs and not files:
            os.rmdir(root)
    return emitted, metrics


# ---------------------------------------------------------------------------
# delta_div --- WITHIN FOOTPRINT, and the pairing is explicit in every row
# ---------------------------------------------------------------------------
def delta_table(metrics, cross_building=False):
    """One row per (building, f) pair.  Refusals are COUNTED, never dropped."""
    rows, refused = [], []
    bids = sorted({b for (b, _c, _f) in metrics})
    order = {b: i for i, b in enumerate(bids)}
    for (bid, case, f) in sorted(metrics):
        if case != "B":
            continue
        b = metrics[(bid, "B", f)]
        a_bid = bid
        if cross_building:
            # PERTURBATION: pair this building's Case B with ANOTHER building's
            # Case A. It is a different footprint, and that is precisely the
            # comparison G10.20 exists to refuse.
            cand = [x for x in bids if x != bid and (x, "A", f) in metrics]
            if cand:
                a_bid = cand[order[bid] % len(cand)]
        a = metrics.get((a_bid, "A", f))
        if a is None:
            refused.append({"building_id": bid, "f": f,
                            "why": "no Case A partner on disk --- the pair is "
                                   "REFUSED, not compared across buildings"})
            continue
        # The Case-A CHOICE SPREAD, from Case B's own zone series: replicating
        # unit u gives a building peak of 3.0 * sum(A_z) * max(m_u), i.e. the
        # zone peak scaled to the whole floor area.
        tot = b["total_area_m2"]
        alts = [pk / ar * tot for pk, ar in zip(b["zone_peak_w"], b["zone_areas_m2"])
                if ar > 0]
        alts_sorted = sorted(alts)
        med = percentile_linear(alts_sorted, 50.0)
        spread = alts_sorted[-1] - alts_sorted[0]
        d_peak = b["peak_w"] - a["peak_w"]
        d_p99 = b["p99_w"] - a["p99_w"]
        rows.append({
            "building_id": bid, "case_a_building_id": a_bid,
            "pair_basis": "within_footprint" if a_bid == bid else "cross_building",
            "arm": b["arm"], "fold": b["fold"], "zone_semantics": b["zone_semantics"],
            "N_u": b["n_zones"], "f": f,
            "peak_a_w": a["peak_w"], "peak_b_w": b["peak_w"],
            "delta_div_peak_w": d_peak,
            "delta_div_peak_pct": 100.0 * d_peak / a["peak_w"] if a["peak_w"] else float("nan"),
            "p99_a_w": a["p99_w"], "p99_b_w": b["p99_w"],
            "delta_div_p99_pct": 100.0 * d_p99 / a["p99_w"] if a["p99_w"] else float("nan"),
            "mean_a_w": a["mean_w"], "mean_b_w": b["mean_w"],
            "delta_div_mean_w": b["mean_w"] - a["mean_w"],
            "cf_phi_a": a["cf_phi"], "cf_phi_b": b["cf_phi"],
            "case_a_choice_spread_w": spread,
            "case_a_choice_spread_pct": 100.0 * spread / med if med else float("nan"),
            # !! FINDING 143's discipline, printed rather than left to a reader:
            # an effect smaller than the spread of the free parameter is not a result.
            "abs_delta_over_choice_spread": (abs(d_peak) / spread) if spread > 0 else float("nan"),
            "cf_basis": b["cf_basis"],
        })
    return rows, refused


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def gate_g10_20(metrics, deltas, refused, f_values, scanned):
    """Paired control present, WITHIN FOOTPRINT, on identical geometry and fold.

    Four arms, because the row's own clause has four halves and a gate that
    checks one of them is a gate that was never written for the other three:
      (i)   every (building, f) carries BOTH cases                --> refusals
      (ii)  no delta_div row is a cross-building comparison
      (iii) the partners agree on N_u, zone areas, arm and fold   --> same footprint
      (iv)  the pair is scored at EVERY f in the sweep
    """
    bids = sorted({b for (b, _c, _f) in metrics})
    missing, mismatch = [], []
    for bid in bids:
        for f in f_values:
            a = metrics.get((bid, "A", f))
            b = metrics.get((bid, "B", f))
            if a is None or b is None:
                missing.append({"building_id": bid, "f": f,
                                "have": [c for c in PAIR_CASES
                                         if (bid, c, f) in metrics]})
                continue
            same = (a["n_zones"] == b["n_zones"]
                    and a["arm"] == b["arm"] and a["fold"] == b["fold"]
                    and all(abs(x - y) <= 1e-9 for x, y in
                            zip(a["zone_areas_m2"], b["zone_areas_m2"])))
            if not same:
                mismatch.append({"building_id": bid, "f": f,
                                 "why": "the partners differ in N_u / zone areas / "
                                        "arm / fold --- not the same footprint"})
    cross = [r for r in deltas if r["pair_basis"] != "within_footprint"]
    if not bids:
        return {"gate": "G10.20", "verdict": "NOT_EVALUABLE", "buildings": 0,
                "note": "no building was paired, so no pairing was asserted. "
                        "NOT a pass.", "files_scanned": len(scanned)}, []
    bad = len(missing) + len(mismatch) + len(cross) + len(refused)
    return ({"gate": "G10.20", "verdict": "PASS" if bad == 0 else "FAIL",
             "buildings": len(bids), "f_values": list(f_values),
             "cells_expected": len(bids) * len(f_values) * 2,
             "cells_present": len(metrics),
             "pairs_missing_a_partner": len(missing),
             "pairs_with_geometry_mismatch": len(mismatch),
             "delta_rows": len(deltas),
             "cross_building_delta_rows": len(cross),
             "pairs_refused": len(refused),
             # V10.d: a search gate that scans nothing passes everything.
             "files_scanned": len(scanned),
             "note": "delta_div is WITHIN FOOTPRINT. A missing Case A partner is "
                     "REFUSED and counted, never silently compared across buildings"},
            missing + mismatch + cross[:50])


def gate_g10_21(metrics):
    """!! NOT_EVALUABLE, WITH ITS POPULATION NAMED --- and that is the gate working.

    `G10.21` scores `CF` on SIMULATED BUILDING POWER and the `sqrt(N)` fit with its
    residuals.  Zero Step 10 cells have been simulated.  Reporting the gain-channel
    number as though it discharged the gate is the basis change the gate-ID rule and
    `G10.12` exist to refuse, so it is reported BESIDE the gate and never AS it.
    """
    return {"gate": "G10.21", "verdict": "NOT_EVALUABLE",
            "population": "simulated Step 10 cells",
            "population_size": 0,
            "gain_channel_cells_available": len(metrics),
            "owed_by": "work items 10.6 / 10.7 (both wait on 10.3 / OpenUBEM EU-04)",
            "note": "CF_phi is the DRIVER's coincidence factor. Heating demand "
                    "peaks when gains are LOW, so CF_phi is not CF and is never "
                    "quoted as it. Arm (ii) --- Case A is 1 BY CONSTRUCTION --- is "
                    "a statement about the harness and IS checkable now: W10.9"}


def check_w10_9(metrics):
    """Case A really IS synchronised --- and the verdict does NOT come from CF.

    !! REWRITTEN AFTER THE BATTERY FELLED THE FIRST VERSION (`FINDING 158`).
    The first `W10.9` scored `G10.21`(ii) literally: Case A's `CF_phi` must be 1.
    The battery's `case_a_independent` case --- Case A given N_u INDEPENDENT
    diaries, which is the exact harness defect the clause exists to catch --- came
    back **PASS**.  `CF_phi` is 1 for the independent case TOO, because every Step 7
    presence series reaches 1.0 and every pair of them shares hours at which both
    are there.  A guard whose discriminator is CONSTANT in the ground truth is not
    a guard.

    So the verdict is taken on the thing that does discriminate:

      (i)  SCORED    --- the N_u emitted series of a Case A cell are BYTE-IDENTICAL
                         (sha256 of the emitted file, taken before reduction).
      (ii) CARRIED, NOT SCORED --- `CF_phi` = 1 to the bound. True, checked, and
                         reported, but it is 1 on this artefact whatever the
                         diaries are, so it may never be quoted as evidence that
                         the synchronised case was built correctly.
    """
    pop = [(k, m) for k, m in metrics.items() if k[1] == "A"]
    if not pop:
        return {"gate": "W10.9", "verdict": "NOT_EVALUABLE", "case_a_cells": 0,
                "note": "no Case A cell exists, so synchronisation was never "
                        "asserted. NOT a pass."}
    not_identical, cf_off = [], []
    for (bid, _c, f), m in sorted(pop):
        if len(set(m["zone_digests"])) != 1:
            not_identical.append({"building_id": bid, "f": f,
                                  "distinct_series": len(set(m["zone_digests"])),
                                  "n_zones": m["n_zones"]})
        if abs(m["cf_phi"] - 1.0) > CF_ONE_BOUND:
            cf_off.append({"building_id": bid, "f": f, "cf_phi": m["cf_phi"]})
    worst = max(abs(m["cf_phi"] - 1.0) for _k, m in pop)
    return {"gate": "W10.9", "verdict": "PASS" if not not_identical else "FAIL",
            "case_a_cells": len(pop),
            "cells_with_non_identical_series": len(not_identical),
            "examples": not_identical[:5],
            "cf_one_arm": "CARRIED, NOT SCORED (FINDING 158): the discriminator is "
                          "constant on this artefact",
            "cf_bound": CF_ONE_BOUND, "cf_worst_abs_dev": worst,
            "cf_cells_off": len(cf_off),
            "note": "scored on SERIES IDENTITY, not on CF. The first version scored "
                    "CF and the battery's own independent-Case-A case passed it"}


def check_w10_12(metrics):
    """INFO --- the driver channel's coincidence factor is DEGENERATE.  Measured.

    `FINDING 158`.  Reported so that nobody reads a `CF_phi` of 1 anywhere in this
    artefact as a property of the pairing.  `hours_all_zones_at_max` > 0 in a cell
    is a PROOF that its `CF_phi` is exactly 1: the building's maximum is attained
    at an hour where every zone is at its own.
    """
    pop = [m for k, m in metrics.items() if k[1] == "B" and m["n_zones"] >= 2]
    if not pop:
        return {"gate": "W10.12", "verdict": "NOT_EVALUABLE", "cells": 0,
                "note": "no Case B cell with N_u >= 2, so the degeneracy was never "
                        "measured. NOT a pass and NOT a clean bill."}
    ones = [m for m in pop if abs(m["cf_phi"] - 1.0) <= CF_ONE_BOUND]
    coincident = [m for m in pop if m["hours_all_zones_at_max"] > 0]
    hrs = sorted(m["hours_all_zones_at_max"] for m in pop)
    return {"gate": "W10.12", "verdict": "INFO",
            "case_b_cells_n_u_ge_2": len(pop),
            "cells_with_cf_phi_exactly_one": len(ones),
            "cells_with_a_fully_coincident_hour": len(coincident),
            "median_hours_all_zones_at_max": percentile_linear(hrs, 50.0),
            "min_hours_all_zones_at_max": hrs[0],
            "note": "FINDING 158: every Step 7 presence series reaches 1.0, so "
                    "independent dwellings still share hours at which all are "
                    "present. On the DRIVER channel diversity cannot lower the "
                    "peak. Any CF < 1 in Step 10 must come from the THERMAL "
                    "response, which means G10.21 cannot be discharged by any "
                    "pre-simulation artefact"}


def check_w10_10(deltas):
    """The annual channel is dead BY CONSTRUCTION, asserted from the emitted files.

    `G10.13` holds the annual mean at 3.0 W/m2 per zone AND per building in both
    cases, so `Metric(B) - Metric(A)` on the annual mean is identically zero.
    """
    if not deltas:
        return {"gate": "W10.10", "verdict": "NOT_EVALUABLE", "rows": 0,
                "note": "no delta row exists. NOT a pass."}
    worst, worst_row = 0.0, None
    for r in deltas:
        rel = abs(r["delta_div_mean_w"]) / r["mean_a_w"] if r["mean_a_w"] else 0.0
        if rel > worst:
            worst, worst_row = rel, r
    ok = worst <= 1e-9
    return {"gate": "W10.10", "verdict": "PASS" if ok else "FAIL",
            "rows": len(deltas), "worst_relative_annual_delta": worst,
            "bound": 1e-9,
            "worst_row": None if worst_row is None else
                         {"building_id": worst_row["building_id"],
                          "f": worst_row["f"]},
            "note": "H10 CANNOT live on the annual channel of this artefact: "
                    "conservation makes the annual delta_div exactly zero, so a "
                    "non-zero one is a conservation failure, not an effect"}


def check_w10_11(assignments, production_table):
    """ARM D Case B must reproduce the 10.4 PRODUCTION assignment, diary for diary.

    !! Not asserted from the fact that both call the same function --- read off
    the shipped `assignment_table.csv`.  A tool that reproduces its own reasoning
    proves nothing; this compares against the artefact 10.4 shipped.
    """
    if not production_table or not os.path.exists(production_table):
        return {"gate": "W10.11", "verdict": "NOT_EVALUABLE",
                "production_table": production_table,
                "note": "10.4's assignment_table.csv was not found, so Case B was "
                        "never compared to the production draws. NOT a pass."}
    prod = {}
    with io.open(production_table, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["arm"] != "D":
                continue
            prod[(r["building_id"], int(r["unit_index"]))] = (r["presence_file"],
                                                             r["presence_md5"],
                                                             r["seed"])
    mine = {(a["building_id"], a["unit_index"]): (a["presence_file"],
                                                  a["presence_md5"], a["seed"])
            for a in assignments if a["case"] == "B" and a["arm"] == "D"}
    if not prod or not mine:
        return {"gate": "W10.11", "verdict": "NOT_EVALUABLE",
                "production_arm_d_rows": len(prod), "paired_arm_d_rows": len(mine),
                "note": "one side has no Arm D rows, so nothing was compared. "
                        "NOT a pass."}
    keys = set(prod) | set(mine)
    diff = [k for k in sorted(keys) if prod.get(k) != mine.get(k)]
    return {"gate": "W10.11", "verdict": "PASS" if not diff else "FAIL",
            "production_arm_d_rows": len(prod), "paired_arm_d_rows": len(mine),
            "rows_differing": len(diff), "examples": [list(k) for k in diff[:5]],
            "note": "Case B on Arm D IS 10.4's production draw --- compared against "
                    "the shipped table, not against this tool's own logic"}


# ---------------------------------------------------------------------------
def write_outputs(outdir, assignments, skipped, emitted, board, g13_rows, g8_rows,
                  deltas, refused, metrics, meta):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    with io.open(os.path.join(outdir, "paired_assignment_table.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["building_id", "unit_index", "case", "arm", "zone_semantics",
                    "country", "fold", "zone_area_m2", "zone_areas_basis",
                    "presence_file", "presence_md5", "seed", "independent",
                    "replicated_from_unit"])
        for a in sorted(assignments, key=lambda x: (x["building_id"], x["case"],
                                                    x["unit_index"])):
            w.writerow([a["building_id"], a["unit_index"], a["case"], a["arm"],
                        a["zone_semantics"], a["country"], a["fold"],
                        "%.4f" % a["zone_area_m2"], a["zone_areas_basis"],
                        a["presence_file"], a["presence_md5"], a["seed"],
                        a["independent"], a["replicated_from_unit"]])
    dfields = ["building_id", "case_a_building_id", "pair_basis", "arm", "fold",
               "zone_semantics", "N_u", "f", "peak_a_w", "peak_b_w",
               "delta_div_peak_w", "delta_div_peak_pct", "p99_a_w", "p99_b_w",
               "delta_div_p99_pct", "mean_a_w", "mean_b_w", "delta_div_mean_w",
               "cf_phi_a", "cf_phi_b", "case_a_choice_spread_w",
               "case_a_choice_spread_pct", "abs_delta_over_choice_spread",
               "cf_basis"]
    with io.open(os.path.join(outdir, "delta_div_within_footprint.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=dfields)
        w.writeheader()
        for r in deltas:
            w.writerow(r)
    with io.open(os.path.join(outdir, "cell_metrics_gain_channel.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["building_id", "case", "arm", "fold", "zone_semantics", "N_u",
                    "f", "peak_w", "peak_hour", "sum_zone_peak_w", "cf_phi",
                    "p99_w", "mean_w", "total_area_m2", "cf_basis"])
        for (bid, case, f) in sorted(metrics):
            m = metrics[(bid, case, f)]
            w.writerow([bid, case, m["arm"], m["fold"], m["zone_semantics"],
                        m["n_zones"], f, "%.6f" % m["peak_w"], m["peak_hour"],
                        "%.6f" % m["sum_zone_peak_w"], "%.12f" % m["cf_phi"],
                        "%.6f" % m["p99_w"], "%.9f" % m["mean_w"],
                        "%.4f" % m["total_area_m2"], m["cf_basis"]])
    with io.open(os.path.join(outdir, "conservation_g10_13_paired.csv"), "w",
                 encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["case", "scope", "building_id",
                                           "unit_index", "f", "mean_phi_w_m2",
                                           "abs_dev", "bound", "verdict",
                                           "n_values", "read_from"])
        w.writeheader()
        for r in g13_rows:
            w.writerow(r)
    payload = dict(meta)
    payload.update({"gate_board": board, "n_assignments": len(assignments),
                    "n_emitted_csv": len(emitted), "n_delta_rows": len(deltas),
                    "pairs_refused": refused, "skipped": skipped,
                    "g10_8_failures": g8_rows[:200]})
    with io.open(os.path.join(outdir, "paired_report.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(payload, indent=2, sort_keys=True))


def summarise(deltas):
    """Per (arm, f): the median delta_div on peak, BESIDE the choice spread."""
    by = {}
    for r in deltas:
        if r["pair_basis"] != "within_footprint" or r["N_u"] < 2:
            continue
        by.setdefault((r["arm"], r["f"]), []).append(r)
    out = []
    for (arm, f), rs in sorted(by.items()):
        pk = sorted(x["delta_div_peak_pct"] for x in rs)
        sp = sorted(x["case_a_choice_spread_pct"] for x in rs)
        rt = sorted(x["abs_delta_over_choice_spread"] for x in rs
                    if x["abs_delta_over_choice_spread"] ==
                    x["abs_delta_over_choice_spread"])
        cf = sorted(x["cf_phi_b"] for x in rs)
        out.append({"arm": arm, "f": f, "n_buildings": len(rs),
                    "median_delta_div_peak_pct": percentile_linear(pk, 50.0),
                    "median_case_a_choice_spread_pct": percentile_linear(sp, 50.0),
                    "median_abs_delta_over_choice_spread":
                        percentile_linear(rt, 50.0) if rt else float("nan"),
                    "median_cf_phi_b": percentile_linear(cf, 50.0)})
    return out


def run(table, outdir, country_override=None, seed_base=1, f_values=SWEEP_F,
        decimals=WRITE_DECIMALS, bundles=None, label="", production_table=None,
        arm_from_zone_count=False, force_fold=None, mislabel_fold=None,
        case_a_independent=False, drop_case_a=False, cross_building=False,
        perturb_zone=None, break_md5=False, unequal_areas=False,
        case_a_shift_areas=False, quiet=False):
    rows = A.read_building_table(table, country_override)
    if unequal_areas:
        for r in rows:
            n = r["zone_count"]
            tot = sum(r["zone_areas_m2"])
            w = [(i + 1) ** 3 for i in range(n)]
            sw = float(sum(w))
            r["zone_areas_m2"] = [tot * x / sw for x in w]
            r["zone_areas_basis"] = "perturbed_unequal"
    by_fold, by_name = A.step7_index(bundles=bundles)

    # `drop_case_a` names a building by POSITION so the battery does not have to
    # know an id: the first Arm D building carrying N_u >= 2.
    drop_id = None
    if drop_case_a:
        cand = [r["building_id"] for r in rows
                if A.arm_of(r) == "D" and r["zone_count"] >= 2]
        drop_id = cand[0] if cand else None

    assignments, skipped = build_pairs(rows, by_fold, seed_base=seed_base,
                                       arm_from_zone_count=arm_from_zone_count,
                                       force_fold=force_fold,
                                       mislabel_fold=mislabel_fold,
                                       case_a_independent=case_a_independent,
                                       drop_case_a=drop_id)
    if break_md5:
        for a in assignments:
            a["presence_md5"] = "0" * 32
    if case_a_shift_areas:
        # PERTURBATION: only CASE A's zone areas move. The pair is then not on the
        # same footprint --- G10.20's clause (iii), which no other case tests.
        for a in assignments:
            if a["case"] == "A":
                a["zone_area_m2"] = a["zone_area_m2"] * 1.10

    # the retained sample: one Arm D building with N_u >= 2 and one Arm F, NAMED
    nz = {}
    for a in assignments:
        nz.setdefault(a["building_id"], set()).add(a["unit_index"])
    retain = []
    for want, need in (("D", 2), ("F", 1)):
        cand = sorted({a["building_id"] for a in assignments if a["arm"] == want
                       and len(nz[a["building_id"]]) >= need})
        if cand:
            retain.append(cand[0])
    retain = tuple(retain)

    means = {}

    def _on_written(rec, vals):
        means[(rec["csv"], rec["f"])] = (sum(vals) / len(vals), len(vals))

    emitted, metrics = emit_paired(assignments, outdir, f_values=f_values,
                                   decimals=decimals, perturb_zone=perturb_zone,
                                   retain_ids=retain, on_written=_on_written)

    # G10.13 is scored PER CASE: keying the per-building arm by building_id alone
    # would area-weight Case A's zones together with Case B's and hide a zone
    # failure inside a pooled building mean.
    g13_rows, zone_fails, bldg_fails, zone_rows = [], 0, 0, 0
    g13_bound = None
    for case in PAIR_CASES:
        sub = [e for e in emitted if e["case"] == case]
        if not sub:
            continue
        g, rws = A.gate_g10_13(sub, decimals=decimals, means=means)
        g13_bound = g["bound_w_m2"]
        zone_fails += g.get("zone_fails", 0)
        bldg_fails += g.get("building_fails", 0)
        zone_rows += g.get("zone_rows", 0)
        for r in rws:
            r = dict(r)
            r["case"] = case
            g13_rows.append(r)
    if not emitted:
        g13 = {"gate": "G10.13", "verdict": "NOT_EVALUABLE", "zone_rows": 0,
               "note": "nothing was emitted, so conservation was never asserted. "
                       "NOT a pass."}
    else:
        g13 = {"gate": "G10.13",
               "verdict": "PASS" if (zone_fails == 0 and bldg_fails == 0) else "FAIL",
               "bound_w_m2": g13_bound, "decimals": decimals,
               "zone_rows": zone_rows, "zone_fails": zone_fails,
               "building_fails": bldg_fails, "scored_per_case": list(PAIR_CASES),
               "note": "read from the emitted CSV on disk (V10.h); scored PER CASE "
                       "so Case A's zones are never area-weighted with Case B's"}

    deltas, refused = delta_table(metrics, cross_building=cross_building)
    scanned = sorted({e["csv"] for e in emitted})
    g20, g20_rows = gate_g10_20(metrics, deltas, refused, f_values, scanned)
    g8, g8_rows = A.gate_g10_8(assignments, by_name)
    board = {"G10.20": g20, "G10.13": g13, "G10.8": g8,
             "G10.9": A.gate_g10_9(assignments),
             "G10.19": A.gate_g10_19([a for a in assignments if a["case"] == "B"]),
             "G10.21": gate_g10_21(metrics),
             "W10.9": check_w10_9(metrics),
             "W10.10": check_w10_10(deltas),
             "W10.11": check_w10_11(assignments, production_table),
             "W10.12": check_w10_12(metrics)}
    live = A.md5_of_file(A.PREREG) if os.path.exists(A.PREREG) else "MISSING"
    board["W10.8"] = {"gate": "W10.8",
                      "verdict": "PASS" if live == A.PREREG_MD5 else "FAIL",
                      "live": live, "recorded": A.PREREG_MD5,
                      "note": "prereg.md is frozen; recomputed from disk"}
    meta = {"label": label, "building_table": table, "n_buildings": len(rows),
            "production_table": production_table,
            "retained_buildings": list(retain),
            "n_csv_retained": sum(1 for e in emitted if e["retained"]),
            "reduction_note": "the paired emission is 2x work item 10.4's, so every "
                              "file is read from disk the moment it is written and "
                              "only the named sample is kept (the 10.4 precedent)",
            "seed_base": seed_base, "write_decimals": decimals,
            "f_values": list(f_values), "country_override": country_override,
            "cf_basis_note": "CF_phi is the coincidence factor of the DRIVER. "
                             "G10.21 scores CF on SIMULATED BUILDING POWER and is "
                             "NOT_EVALUABLE until 10.6 runs.",
            "g10_20_failing_rows": g20_rows[:50],
            "summary_by_arm_f": summarise(deltas),
            "perturbations": {"arm_from_zone_count": arm_from_zone_count,
                              "force_fold": force_fold,
                              "mislabel_fold": mislabel_fold,
                              "case_a_independent": case_a_independent,
                              "drop_case_a": drop_id,
                              "cross_building": cross_building,
                              "case_a_shift_areas": case_a_shift_areas,
                              "perturb_zone": perturb_zone,
                              "break_md5": break_md5,
                              "unequal_areas": unequal_areas}}
    write_outputs(outdir, assignments, skipped, emitted, board, g13_rows, g8_rows,
                  deltas, refused, metrics, meta)
    if not quiet:
        print("  buildings %d  paired rows %d  emitted CSV %d  delta rows %d  "
              "refused %d" % (len(rows), len(assignments), len(emitted),
                              len(deltas), len(refused)))
        for k in ("G10.20", "G10.13", "G10.8", "G10.9", "G10.19", "G10.21",
                  "W10.9", "W10.10", "W10.11", "W10.12", "W10.8"):
            b = board[k]
            keys = {kk: vv for kk, vv in b.items()
                    if kk not in ("gate", "verdict", "note", "examples",
                                  "worst_row", "population")}
            print("  %-7s %-14s %s" % (k, b["verdict"], keys))
        print()
        print("  delta_div on the GAIN channel, within footprint, N_u >= 2")
        print("  (CF_phi basis --- NOT simulated power, NOT the H10 test):")
        print("  %-4s %-5s %5s %14s %14s %9s %11s"
              % ("arm", "f", "n", "med d_peak %", "med spread %", "d/spread",
                 "med CF_phi"))
        for s in meta["summary_by_arm_f"]:
            print("  %-4s %-5.2f %5d %14.4f %14.4f %9.3f %11.6f"
                  % (s["arm"], s["f"], s["n_buildings"],
                     s["median_delta_div_peak_pct"],
                     s["median_case_a_choice_spread_pct"],
                     s["median_abs_delta_over_choice_spread"],
                     s["median_cf_phi_b"]))
    return board


BATTERY = [
    ("Case A partner deleted for one real Arm D building", "G10.20", "FAIL",
     dict(drop_case_a=True)),
    ("delta_div paired ACROSS buildings instead of within", "G10.20", "FAIL",
     dict(cross_building=True)),
    ("Case A's zone areas moved 10 % --- not the same footprint", "G10.20", "FAIL",
     dict(case_a_shift_areas=True)),
    ("Case A given N_u INDEPENDENT diaries (harness defect)", "W10.9", "FAIL",
     dict(case_a_independent=True)),
    ("one zone scaled 1.02, building mean left near-right", "G10.13", "FAIL",
     dict(perturb_zone=0)),
    ("write format coarsened to 6 decimals (FINDING 132)", "G10.13", "FAIL",
     dict(decimals=6, perturb_zone=0)),
    ("recorded md5 broken --- diary unlocatable by content", "G10.8", "FAIL",
     dict(break_md5=True)),
    ("every dwelling RECORDS a fold its diary did not come from", "G10.8", "FAIL",
     dict(mislabel_fold="it")),
    ("arm read from zone_count: storeys become an H10 population", "G10.19",
     "PASS", dict(arm_from_zone_count=True)),
    # !! V10.a's other half. A battery in which every case fires proves the cases
    # fire; it does not prove the gates are quiet when nothing is wrong.
    ("NULL --- nothing perturbed", "*", "NO CHANGE", dict()),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="building table CSV")
    ap.add_argument("--out", default=os.path.join(OUT, "paired"))
    ap.add_argument("--country", default=None)
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--decimals", type=int, default=WRITE_DECIMALS)
    ap.add_argument("--bundles", default=None)
    ap.add_argument("--production-table", default=os.path.join(
        OUT, "assign_exercise", "assignment_table.csv"),
        help="10.4's shipped assignment_table.csv, for W10.11")
    ap.add_argument("--label", default="")
    ap.add_argument("--perturb", action="store_true",
                    help="run the battery: every gate must be SEEN FAILING")
    a = ap.parse_args()
    bundles = a.bundles.split(",") if a.bundles else None

    print("=" * 78)
    print("work item 10.9 -- paired Case A / Case B emission (Step 10 section 6.6)")
    print("=" * 78)
    print("BASELINE  %s" % a.label)
    board = run(a.table, a.out, country_override=a.country, seed_base=a.seed_base,
                decimals=a.decimals, bundles=bundles, label=a.label,
                production_table=a.production_table)
    fails = [k for k, v in board.items() if v["verdict"] == "FAIL"]
    if not a.perturb:
        return 1 if fails else 0

    base_verdicts = {k: v["verdict"] for k, v in board.items()}
    print()
    print("PERTURBATION BATTERY -- a gate nobody has watched fail is an assumption")
    print("-" * 78)
    hits = 0
    for i, (name, target, expect, kw) in enumerate(BATTERY):
        d = os.path.join(a.out, "_perturb%d" % i)
        kw = dict(kw)
        try:
            b = run(a.table, d, country_override=a.country, seed_base=a.seed_base,
                    decimals=kw.pop("decimals", a.decimals), bundles=bundles,
                    production_table=a.production_table,
                    label="perturb:%s" % name, quiet=True, **kw)
            if target == "*":
                got = {k: v["verdict"] for k, v in b.items()}
                moved = sorted(k for k in got if got[k] != base_verdicts.get(k))
                v = "NO CHANGE" if not moved else "MOVED:%s" % ",".join(moved)
            else:
                v = b[target]["verdict"]
        except Exception as e:                       # a crash is NOT a FAIL
            v = "CRASH(%s)" % type(e).__name__
        hit = (v == expect)
        hits += 1 if hit else 0
        print("  %-54s %-7s want %-10s got %-24s %s"
              % (name[:54], target, expect, v[:24], "HIT" if hit else "*** MISS ***"))
    print("-" * 78)
    print("battery: %d of %d moved their target gate to the declared verdict"
          % (hits, len(BATTERY)))
    if hits != len(BATTERY):
        print("*** A MISS is a gate that could not be made to fail. It is NOT a pass.")
    return 0 if (not fails and hits == len(BATTERY)) else 1


if __name__ == "__main__":
    sys.exit(main())
