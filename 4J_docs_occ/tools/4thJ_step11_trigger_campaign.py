# -*- coding: utf-8 -*-
"""4J Step 11, work item 11.3 -- THE PER-DWELLING TRIGGER CAMPAIGN.

    python 4thJ_step11_trigger_campaign.py --root <4J_docs_occ> \
        --c2-out <dir written by 4thJ_step10_nocore_campaign.py> \
        --diary-diversity {replicate|reseed} [--dry-run] [--limit N] [--out DIR]

WHAT THIS IS
------------
Step 10 campaign `C2` simulated one EnergyPlus cell per (building, case, `f`),
and inside each cell one DRAWN FLAT per emitted zone, each flat carrying its own
Step 7 diary.  This runner takes those same flats and runs the Step 9 activity
trigger on them, so that every drawn flat gets an appliance-electricity and a
DHW series to sit beside the heating the `C2` cell already produced.

🔴 IT SCORES NOTHING.  No `G11.x` verdict is computed here.  Scoring the Step 11
suite is work item 11.6, and a runner that both produces the numbers and grades
them is the failure shape `V11.g` exists to prevent.

WHAT IS IMPORTED, AND WHY IT IS NOT RE-IMPLEMENTED
--------------------------------------------------
Three things could have been rewritten here and all three are imported instead,
for the reason `4thJ_gates_step11.py` gives for importing `g9_1`-`g9_4`: a
re-implementation produces a SECOND OPINION, and a second opinion is not an
inheritance.  The two would agree until they did not.

  * THE STATE MACHINE.  `4thJ_step9_trigger.simulate_dwelling` -- extracted
    verbatim from that module's own inner loop on 2026-09-08, byte-identical
    output verified by re-running Step 9 fold `it` before and after the
    extraction and comparing the md5 of every emitted artefact.
  * THE DWELLINGS.  `4thJ_step9_trigger.build_dwellings`, which rebuilds the
    fold's households and REFUSES unless it reproduces Step 8's shipped presence
    schedules exactly.  Step 11 must inject loads into the same people Step 10
    simulated, and that guard is the only thing that can see otherwise.
  * THE FLAT-TO-DIARY BINDING.  Read out of the `C2` cell manifests themselves
    (`schedules[].presence_file` / `presence_md5`), never re-derived.  Re-running
    the assignment here would give a second population that agrees with the first
    only as long as nothing drifts.

🔴 THE SEAM WITH STEP 10 -- WHAT `G11.15` IS ACTUALLY GUARDING
--------------------------------------------------------------
Measured in `openubem/semantic/european_schedules.py`, not assumed:
`build_step8_gain_series` emits a series whose ANNUAL MEAN IS EXACTLY
`BASE_GAIN_W_M2` for every `f`, and asserts that conservation itself.  `f`
REDISTRIBUTES the internal gain in time; it never rescales it.  So Step 10's
`C2` cell carries ONE LUMPED internal-gain term -- occupants, appliances and
lighting together -- as its INPUT, and produces SPACE HEATING as its result.

Therefore:

  * Step 10's path  : space heating.  The lumped gain is an INPUT, never an
                      end-use result, and must never be reported as appliance
                      electricity.
  * Step 11's path  : appliance electricity and DHW, per drawn flat.
  * 🔴 Step 11's appliance electricity MUST NOT be injected back into a Step 10
    heating model.  The appliance heat is ALREADY inside the conserved
    `BASE_GAIN_W_M2`; adding it again is the double count `G11.15` names, and it
    is invisible in either artefact read alone.

⚪ A consequence worth stating rather than discovering later: because the annual
mean is conserved, a flat's appliance MAGNITUDE has no path into its heating
number at all.  Only the TIMING crosses the seam.  Any Step 11 sentence implying
that dwelling-specific appliance loads changed a Step 10 heating result is false.

🔴 THE ONE DECISION THIS RUNNER REFUSES TO MAKE -- `--diary-diversity`
---------------------------------------------------------------------
Step 7 shipped ONE HUNDRED households per fold and no more; `4thJ_step10_assign
.step7_index()` indexes exactly those, so every drawn flat in every district
draws from a pool of 100.  Step 9's per-dwelling RNG is seeded
`"s9|<seed>|<hid>"` and appliance ownership is drawn per `hid`, so TWO FLATS THAT
DREW THE SAME HOUSEHOLD GET IDENTICAL LOADS.

That matters for the claim section 1.1 of the Step 11 specification makes -- that
Step 11 is the first configuration inside the 100-500 dwelling range the source
models were validated in.  It is the first with that many BUILDINGS.  It is not
the first with that many distinct occupancy diaries, and it cannot be, on this
Step 7 emission.  So:

  replicate : one trigger run per HOUSEHOLD (100 per fold), the record replicated
              onto every flat that drew it.  Cheap (~2 min per fold).  Honest,
              and it makes plain that the stock variance comes from WHICH
              household each flat drew, not from new occupants.
  reseed    : one trigger run per FLAT, re-seeded `"s11|<seed>|<hid>|<building>|
              <unit>"`, with appliance ownership redrawn per flat.  The diary --
              the occupancy -- is still one of the same 100.  Appliance diversity
              grows with N; occupant diversity does not.  Expensive: ~1.2 s per
              flat, so Bologna Case B alone is ~9 h and belongs in `sbatch`.

🔴 NEITHER IS A DEFAULT.  The flag has no default value and the run refuses
without it (`S9`), because the choice changes what a stock-scale number MEANS and
that is the author's to rule, not a runner's to assume.  Whichever is chosen is
stamped into every manifest this tool writes.

THE REFUSALS
------------
`S1` France       `S2` Arm F / mixed arms   `S3` no `C2` cells
`S4` a `C2` manifest that `G10N.14` would fail
`S5` `G11.14` runtime columns          `S6` diary identity
`S7` a scored run  `S8` mixed fold/district  `S9` `--diary-diversity` unset
`S10` the `G11.15` seam

Every one raises `Refusal` and none is downgradeable to a warning.

THE EXCLUSIONS -- not a `Refusal`, a counted skip
--------------------------------------------------
`S11` a flat whose only occupancy series is Step 10's floor-merged AREA-WEIGHTED
AVERAGE (`merged_floor_averaged_occupancy`, `average_units_by_floor`, `FINDING
254`) never entered Step 7's shipped bundle -- it was never one real household,
so `S6` can never find its identity there and never should. It is excluded from
the trigger population the same way `S2` excludes Arm F: a known, named category,
counted in the manifest, never silently dropped and never assigned a diary it was
not simulated with.
"""
import argparse
import collections
import hashlib
import importlib.util
import io
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# The two accounting paths, kept as data so `S10` compares sets rather than
# trusting a sentence.  See the seam note in the module docstring.
STEP10_END_USES = frozenset(["space_heating"])
STEP11_END_USES = frozenset(["appliance_electricity", "dhw"])

# Step 7 shipped this many households per fold and no more.  It is not a knob:
# `build_dwellings` refuses to run at any other value because the draw order,
# and therefore every diary, would differ from the shipped bundle.
STEP7_HOUSEHOLDS_PER_FOLD = 100

# ---------------------------------------------------------------------------
# `--diary-diversity` --- THE AUTHOR'S RULING, 2026-09-08, quoted not summarised
# ---------------------------------------------------------------------------
#   "continue as you recommend lets go use bigger datasets"
#
# Read as `reseed`: one trigger run per DRAWN FLAT, appliance ownership redrawn
# per flat, so no two flats carry a byte-identical load series.  `replicate`
# would have been the smaller dataset -- 100 runs per fold, copied onto
# thousands of flats -- and the sentence declines the smaller one.
#
# 🔴 WHAT `reseed` DOES NOT DO, AND MUST NEVER BE SAID TO DO: it does not
# widen the occupancy pool.  Presence still comes from the %d diaries Step 7
# shipped, bound to the flat by the `C2` manifest.  `reseed` varies OWNERSHIP
# and the stochastic draw, never WHO LIVES THERE.  A stock number computed this
# way is still evidence about geometry and aggregation, never about occupant
# diversity.
#
# ⚪ The flag still has NO DEFAULT.  A ruling recorded here is not a licence for
# the runner to choose: the caller states the mode, and a mode other than the
# ruled one is refused BY NAME (`S9b`) rather than run quietly.
DIARY_DIVERSITY_RULED = "reseed"
DIARY_DIVERSITY_RULING_DATE = "2026-09-08"
DIARY_DIVERSITY_RULING_SENTENCE = (
    "continue as you recommend lets go use bigger datasets")


# Step 9's campaign settings, carried unchanged.  A Step 11 run on different
# ones would not be the same trigger.
LEG = "leg5"
YEAR = 2017
SEED = 1
TIMESTEP_MIN = 60
DHW_L_PER_DAY = 200.0
CALIBRATION_PASSES = 6

# 🔴 `fr` IS ABSENT ON PURPOSE and its absence is load-bearing.  Lyon is a
# physical baseline; it can never host a Step 11 campaign (item 11.7 withdrawn
# 2026-08-28) and its payloads FAIL the ruled `C2` basis anyway.
STEP11_FOLDS = ("es", "uk", "it")


class Refusal(RuntimeError):
    """A named preflight refusal.  None of these is downgradeable to a warning."""


# ---------------------------------------------------------------------------
# imports of the things that must not be re-implemented
# ---------------------------------------------------------------------------
def _load(name, filename):
    path = os.path.join(HERE, filename)
    if not os.path.isfile(path):
        raise Refusal("cannot import %s: %s is missing" % (name, path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_trigger():
    return _load("step9_trigger", "4thJ_step9_trigger.py")


def load_step9_gates():
    return _load("gates_step9", "4thJ_gates_step9.py")


# ---------------------------------------------------------------------------
# reading the C2 campaign off disk
# ---------------------------------------------------------------------------
# The fifteen fields of section 5 of the `C2` specification.  A cell whose
# manifest is missing any of them is one `G10N.14` would score as a blank field,
# and Step 11 does not consume what Step 10's own gate would fail.
MANIFEST_FIELDS_S5 = (
    "weather_sha256", "energyplus_build_hash", "energyplus_version",
    "openubem_version", "openubem_git_commit", "platform",
    "rotated_to_midnight", "diary_origin_hour", "completed",
    "completion_status", "scheme", "status", "k", "observed_dwellings",
    "dwelling_deficit",
)


def read_c2_cells(c2_out):
    """Every `C2` cell manifest, in a stable order.  `S3` lives here."""
    cells_dir = os.path.join(c2_out, "cells")
    if not os.path.isdir(cells_dir):
        raise Refusal(
            "S3 no `C2` cells: %s does not exist. Work item 11.3 depends on "
            "Step 10 items 10.4 and 10.6, and a Step 11 campaign built without "
            "a simulated `C2` cell is a fabrication, not a run." % cells_dir)
    paths = sorted(os.path.join(cells_dir, f)
                   for f in os.listdir(cells_dir) if f.endswith(".json"))
    if not paths:
        raise Refusal(
            "S3 no `C2` cells: %s is empty. An empty scan is a REFUSAL, never a "
            "pass -- the 2026-09-08 guard defect, repeated here on purpose."
            % cells_dir)
    cells = []
    for p in paths:
        with io.open(p, encoding="utf-8") as fh:
            cells.append(json.load(fh))
    return cells, paths


def check_cells(cells, paths):
    """`S1`, `S2`, `S4`, `S8`.  Every refusal names the cell that tripped it."""
    folds = sorted(set(c.get("fold") for c in cells))
    if len(folds) != 1:
        raise Refusal("S8 the cells span %d folds %r; a Step 11 campaign is one "
                      "fold, and an aggregate over two is the comparison "
                      "`G11.16` calls a FAIL" % (len(folds), folds))
    fold = folds[0]
    if fold not in STEP11_FOLDS:
        raise Refusal(
            "S1 fold %r can never host a Step 11 campaign. Lyon / `fr` is a "
            "PHYSICAL BASELINE, never a fold and never a diary or trigger "
            "population; item 11.7 was withdrawn 2026-08-28 for this reason."
            % fold)
    campaigns = sorted(set(c.get("campaign") for c in cells))
    if campaigns != ["C2"]:
        raise Refusal("S8 cells are not all campaign `C2`: %r. A `C1` result "
                      "never enters Step 11 and is never re-scored." % campaigns)
    arms = sorted(set(c.get("arm") for c in cells))
    if arms != ["D"]:
        raise Refusal(
            "S2 cells carry arm(s) %r. Arm F is ONE BOX PER FLOOR and a LOWER "
            "BOUND; it is never promoted to Arm D and the two are never pooled "
            "(`G11.17`). A Step 11 aggregate mixing them is a FAIL." % arms)
    for cell, path in zip(cells, paths):
        missing = [f for f in MANIFEST_FIELDS_S5
                   if f not in cell or cell[f] is None]
        if missing:
            raise Refusal(
                "S4 `C2` manifest %s is missing %r. `G10N.14` scores 0 blank "
                "fields; Step 11 does not consume a manifest Step 10's own gate "
                "would fail, and nobody is asked to retrofit a field later."
                % (os.path.basename(path), missing))
        if not cell.get("completed"):
            raise Refusal("S4 `C2` cell %s did not complete (%s); an incomplete "
                          "cell has no flats to trigger"
                          % (cell.get("cell_id"), cell.get("completion_status")))
        if cell.get("rotated_to_midnight") is not True:
            raise Refusal(
                "S4 `C2` cell %s was not rotated to midnight. `FINDING 141` / "
                "`D-S9-3`: a 04:00-origin series written into a `Schedule:File` "
                "is applied FOUR HOURS EARLY, and the trigger output would "
                "inherit the same offset." % cell.get("cell_id"))
    return fold


def flats_from_cells(cells):
    """One record per DRAWN FLAT, deduplicated across the `f` sweep, plus the
    `S11` exclusions counted alongside it.

    The `f` sweep changes only how Step 10 redistributes the conserved internal
    gain; it does not change which diary a flat holds.  So the trigger runs once
    per (building, case, unit) and is reported against every `f` that shares it.

    Returns `(flats, excluded_merged_floor)`.  A flat whose schedule carries
    `merged_floor_averaged_occupancy: True` is a Step 10 floor-merged
    area-weighted average, not a real household's diary (`S11`); it is routed
    into `excluded_merged_floor` instead of `flats` and never reaches `S6`.
    """
    flats = {}
    excluded_merged_floor = {}
    for cell in cells:
        for sched in cell.get("schedules") or []:
            key = (cell["building_id"], cell["case"], sched["unit_index"])
            if sched.get("merged_floor_averaged_occupancy"):
                rec = excluded_merged_floor.get(key)
                if rec is None:
                    excluded_merged_floor[key] = {
                        "building_id": cell["building_id"],
                        "case": cell["case"],
                        "unit_index": sched["unit_index"],
                        "zone": sched["zone"],
                        "storey_index": sched.get("storey_index"),
                        "presence_file": sched["presence_file"],
                        "merged_source_unit_indices":
                            sched.get("merged_source_unit_indices"),
                    }
                continue
            rec = flats.get(key)
            if rec is None:
                rec = {
                    "building_id": cell["building_id"],
                    "case": cell["case"],
                    "unit_index": sched["unit_index"],
                    "zone": sched["zone"],
                    "storey_index": sched.get("storey_index"),
                    "zone_area_m2": sched["zone_area_m2"],
                    "presence_file": sched["presence_file"],
                    "presence_md5": sched["presence_md5"],
                    "seed": sched.get("seed"),
                    "arm": cell["arm"],
                    "fold": cell["fold"],
                    "f_levels": [],
                    "cell_ids": [],
                }
                flats[key] = rec
            elif rec["presence_md5"] != sched["presence_md5"]:
                raise Refusal(
                    "S6 flat %r holds two different diaries across the `f` "
                    "sweep (%s vs %s). `f` redistributes a gain; it never "
                    "reassigns a dwelling."
                    % (key, rec["presence_md5"], sched["presence_md5"]))
            rec["f_levels"].append(cell["sensitivity_f"])
            rec["cell_ids"].append(cell["cell_id"])
    for rec in flats.values():
        rec["f_levels"] = sorted(set(rec["f_levels"]))
        rec["cell_ids"] = sorted(set(rec["cell_ids"]))
    return ([flats[k] for k in sorted(flats)],
            [excluded_merged_floor[k] for k in sorted(excluded_merged_floor)])


# ---------------------------------------------------------------------------
# S5 -- `G11.14`, asserted against the file
# ---------------------------------------------------------------------------
def check_runtime_columns(root, fold, mapping):
    """The trigger's runtime columns must be a SUBSET of the columns the
    GENERATED diaries carry, read from the file, and must not contain `act2`.

    Inherited from `G9.14` in substance and re-asserted here because Step 11's
    diaries are Step 10's, which did not exist when 11.1 ran -- that is exactly
    why `G11.14` was declared out of scope for the carry-over audit.
    """
    sys.path.insert(0, os.path.join(root, "tools"))
    import decoder as dec                                    # noqa: PLC0415
    from encoder import load_bit_positions                   # noqa: PLC0415
    bitpos = load_bit_positions(os.path.join(
        root, "Step2_docs", "outputs_step2", "crosswalk_copresence.csv"))
    path = os.path.join(root, "Step7_docs", "outputs_step7",
                        "generated_%s_%s_constrained.jsonl" % (LEG, fold))
    if not os.path.isfile(path):
        raise Refusal("S5 cannot assert `G11.14` against the file: %s is "
                      "missing" % path)
    with io.open(path, encoding="utf-8") as fh:
        rec = json.loads(fh.readline())
    episode = dec.decode_record(rec["text"], bitpos)["episodes"][0]
    present = set(episode.keys())
    wanted = set(mapping.runtime_input_columns())
    absent = sorted(wanted - present)
    if absent:
        raise Refusal(
            "S5 `G11.14`: the trigger reads %r, which the generated diaries do "
            "not carry. A trigger reading an absent column does not raise -- it "
            "silently never fires." % absent)
    if "act2" in wanted:
        raise Refusal(
            "S5 `G11.14`: `act2` is in the trigger's runtime column set. Its "
            "exclusion is a POLICY (`D-S9-1` ruled (d)), not an accident of the "
            "format -- `FINDING 137` measured `act2` on 29.816 %% of shipped "
            "episodes.")
    return sorted(wanted), sorted(present)


# ---------------------------------------------------------------------------
# S6 -- the diaries are the ones Step 10 simulated
# ---------------------------------------------------------------------------
def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hid_from_presence_file(name, fold):
    """`presence_HH_<fold>_<hid>.csv` -> `<hid>`, refusing anything else."""
    prefix = "presence_HH_%s_" % fold
    if not (name.startswith(prefix) and name.endswith(".csv")):
        raise Refusal("S6 %r is not a %s presence schedule name" % (name, fold))
    return name[len(prefix):-len(".csv")]


def check_diary_identity(flats, dwellings_by_hid, fold, assign_mod):
    """Every flat's diary must be one of the fold's rebuilt households, and the
    file on disk must still hash to what the `C2` manifest recorded."""
    by_fold, _by_name = assign_mod.step7_index()
    on_disk = dict((name, (m5, p)) for name, m5, p in by_fold.get(fold, []))
    if len(on_disk) != STEP7_HOUSEHOLDS_PER_FOLD:
        raise Refusal(
            "S6 fold %s indexes %d shipped presence schedules, not %d. The "
            "trigger's dwellings are built at exactly that count and a "
            "different one changes the draw order, hence every diary."
            % (fold, len(on_disk), STEP7_HOUSEHOLDS_PER_FOLD))
    used = collections.Counter()
    for flat in flats:
        name = flat["presence_file"]
        entry = on_disk.get(name)
        if entry is None:
            raise Refusal(
                "S6 flat %s/%s/u%s holds diary %r, which is not in the shipped "
                "Step 7 bundle for fold %s. Step 11 would be triggering loads "
                "for somebody Step 10 never simulated."
                % (flat["building_id"], flat["case"], flat["unit_index"],
                   name, fold))
        m5, path = entry
        if m5 != flat["presence_md5"]:
            raise Refusal(
                "S6 diary %r has changed on disk since the `C2` run: %s now, %s "
                "in the manifest. The Step 10 result and the Step 11 loads would "
                "come from two different occupancies."
                % (name, m5, flat["presence_md5"]))
        hid = hid_from_presence_file(name, fold)
        if hid not in dwellings_by_hid:
            raise Refusal(
                "S6 household %r is in the shipped bundle but not in the "
                "rebuilt dwellings. `build_dwellings` and the Step 8 bundle "
                "disagree, which is the one thing that check exists to see."
                % hid)
        flat["hid"] = hid
        used[hid] += 1
    return used


# ---------------------------------------------------------------------------
# S10 -- the `G11.15` seam
# ---------------------------------------------------------------------------
def check_seam(emitted_end_uses):
    both = sorted(set(emitted_end_uses) & STEP10_END_USES)
    if both:
        raise Refusal(
            "S10 `G11.15`: end-use(s) %r would be accounted on BOTH paths -- "
            "reconstructed by Step 10 and simulated by Step 11. Each end-use is "
            "accounted on exactly one path. The double count is invisible in "
            "either artefact read alone, which is why it is refused at the seam."
            % both)
    unknown = sorted(set(emitted_end_uses) - STEP11_END_USES)
    if unknown:
        raise Refusal(
            "S10 `G11.15`: end-use(s) %r are emitted but are on neither declared "
            "path. An unaccounted end-use is exactly the thing the seam gate "
            "cannot see later." % unknown)


# ---------------------------------------------------------------------------
# the campaign
# ---------------------------------------------------------------------------
def prepare_fold(root, fold, trigger, quiet=False):
    """The fold's dwellings, ownership and calibrated hazards -- once."""
    map_path = os.path.join(root, "Step9_docs", "outputs_step9",
                            "activity_appliance_map.csv")
    mapping = trigger.Mapping(map_path)
    acl_to_profile = dict(mapping.acl_to_profile)
    dwellings, pool_meta, _s7 = trigger.build_dwellings(
        root, fold, LEG, YEAR, SEED, STEP7_HOUSEHOLDS_PER_FOLD, TIMESTEP_MIN,
        verify_against_step8=True)
    n_days = len(dwellings[0]["members"][0])
    own_rng = random.Random(SEED)
    owned = trigger.sample_ownership(mapping, dwellings, own_rng,
                                     restrict_to_default_dwelling=True)
    mean_elig = trigger.count_eligible(dwellings, acl_to_profile, n_days)
    mean_elig.update(trigger.count_eligible_dhw(dwellings, mapping,
                                                acl_to_profile, n_days))
    hazards, dhw_haz, calib = trigger.calibrate_all(
        mapping, mean_elig, DHW_L_PER_DAY / 200.0)
    hazards, calib_trace = trigger.calibrate_to_published(
        dwellings, mapping, owned, hazards, acl_to_profile, n_days, SEED,
        max_passes=CALIBRATION_PASSES)
    if not quiet:
        print("  fold %s: %d dwellings rebuilt and verified against Step 8, "
              "%d appliances calibrated in %d pass(es)"
              % (fold, len(dwellings), len(hazards), len(calib_trace)))
    return {
        "mapping": mapping, "acl_to_profile": acl_to_profile,
        "dwellings": dwellings, "by_hid": dict((d["hid"], d) for d in dwellings),
        "owned": owned, "hazards": hazards, "dhw_haz": dhw_haz,
        "n_days": n_days, "pool_meta": pool_meta,
        "map_md5": md5_of_file(map_path),
        # Exposed 2026-09-13 for work item 11.6 (`G11.6`'s SATURATED
        # classification). Already computed by the call above; this is
        # additive -- 11.3 and 11.5 never read this key and are unaffected.
        "calib_trace": calib_trace,
    }


def summarise(rec, timestep_min):
    """The reportable scalars, without the two 8,760-long series."""
    return {
        "elec_kwh_year": rec["elec_kwh"],
        "dhw_litres_year": rec["dhw_litres"],
        "dhw_litres_per_day": rec["dhw_litres"] / 365.0,
        "n_members": rec["n_members"],
        "n_appliances": len(rec["appliances"]),
        "dhw_events_by_category": rec["dhw_events_by_category"],
        "dhw_litres_by_category": rec["dhw_litres_by_category"],
    }


def run_flat(flat, ctx, trigger, diversity):
    d = ctx["by_hid"][flat["hid"]]
    if diversity == "replicate":
        rng = None                      # the Step 9 stream, `"s9|<seed>|<hid>"`
        owned_ids = ctx["owned"][flat["hid"]]
    else:
        rng = random.Random("s11|%d|%s|%s|%s" % (SEED, flat["hid"],
                                                 flat["building_id"],
                                                 flat["unit_index"]))
        # Ownership redrawn PER FLAT.  The diary is still one of the same 100 --
        # appliance diversity grows with N, occupant diversity does not, and the
        # manifest says so rather than leaving it to be inferred.
        owned_ids = trigger.sample_ownership(
            ctx["mapping"], [d], rng, restrict_to_default_dwelling=True)[d["hid"]]
    return trigger.simulate_dwelling(
        d, owned_ids, ctx["mapping"], ctx["hazards"], ctx["dhw_haz"],
        ctx["acl_to_profile"], ctx["n_days"], TIMESTEP_MIN, SEED, rng=rng,
        rotate_origin=True)


def population_declaration(fold, district, flats, cells, used, diversity,
                           c2_out, cell_paths, excluded_merged_floor=()):
    """`G11.16`: every stock-scale statistic names its population, its spatial
    extent and its weather file.  Written here so no aggregate can be produced
    without one, rather than checked after the fact."""
    weather = sorted(set(c.get("weather_sha256") for c in cells))
    buildings = sorted(set(f["building_id"] for f in flats))
    return {
        "population": "Step 10 campaign `C2` Arm D drawn flats",
        "district": district,
        "fold": fold,
        "spatial_extent": "one neighbourhood, contiguous, one construction-epoch mix",
        "weather_file_sha256": weather[0] if len(weather) == 1 else weather,
        "n_buildings": len(buildings),
        "n_flats": len(flats),
        "n_c2_cells": len(cells),
        "arm": "D",
        "arm_note": "Arm D only. Arm F is a LOWER BOUND, never pooled with this "
                    "and never promoted (`G11.17`).",
        # 🔴 The declaration that section 1.1's claim actually rests on.
        "n_distinct_diaries": len(used),
        "diary_pool_size": STEP7_HOUSEHOLDS_PER_FOLD,
        "diary_diversity_mode": diversity,
        "diary_note": (
            "Every flat draws from the %d households Step 7 shipped for this "
            "fold. This population has %d BUILDINGS inside the range the source "
            "models were validated in; it does NOT have that many distinct "
            "occupancy diaries, and on this Step 7 emission it cannot. Under "
            "`replicate` two flats sharing a household have identical loads; "
            "under `reseed` their appliance ownership and start draws differ "
            "while the occupancy diary is still one of the same %d."
            % (STEP7_HOUSEHOLDS_PER_FOLD, len(buildings),
               STEP7_HOUSEHOLDS_PER_FOLD)),
        "comparability": (
            "NOT comparable to Step 9's R^2 without this declaration: Step 9's "
            "100 dwellings were drawn ACROSS a fold; these sit in one "
            "neighbourhood on one weather file, spatially adjacent and "
            "epoch-correlated (`G11.16`)."),
        "accounting_paths": {
            "step10": sorted(STEP10_END_USES),
            "step11": sorted(STEP11_END_USES),
            "note": "One path per end-use per building (`G11.15`). Step 10's "
                    "lumped internal gain is an INPUT, never an end-use result; "
                    "Step 11's appliance electricity is already inside it and "
                    "must never be injected back.",
        },
        "c2_out": os.path.abspath(c2_out),
        "c2_cell_set_sha256": cell_set_digest(cell_paths),
        "scores_nothing": True,
        # `S11`: named and counted, never a silent drop -- see `flats_from_cells`.
        "n_flats_excluded_merged_floor": len(excluded_merged_floor),
        "excluded_merged_floor_note": (
            "%d flat(s) over %d building(s) hold a Step 10 floor-merged, "
            "area-weighted AVERAGED occupancy series (`merged_floor_averaged_"
            "occupancy`), not a real per-household diary. `S11` excludes them "
            "from this trigger population the same way `S2` excludes Arm F: "
            "they are not in `n_flats` above and never received a diary they "
            "were not simulated with."
            % (len(excluded_merged_floor),
               len(set(r["building_id"] for r in excluded_merged_floor)))),
    }


def cell_set_digest(paths):
    """One digest over the whole `C2` cell set, so a Step 11 run cannot span two
    campaigns -- the same argument as `R10` on the Step 10 side."""
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(os.path.basename(p).encode("utf-8"))
        h.update(b"\0")
        h.update(md5_of_file(p).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Step 11 work item 11.3, the per-dwelling trigger campaign. "
                    "Scores nothing.")
    ap.add_argument("--root", required=True, help="the 4J_docs_occ directory")
    ap.add_argument("--c2-out", required=True,
                    help="the directory `4thJ_step10_nocore_campaign.py` wrote")
    ap.add_argument("--diary-diversity", choices=("replicate", "reseed"),
                    default=None,
                    help="THE AUTHOR'S RULING. No default; see the module "
                         "docstring. `S9` refuses without it.")
    ap.add_argument("--district", default=None,
                    help="recorded in the declaration; read from the cells if "
                         "omitted")
    ap.add_argument("--dry-run", action="store_true",
                    help="preflight and enumerate flats; run no trigger")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap the flat count (a smoke run, never a population)")
    ap.add_argument("--scored", action="store_true",
                    help="refused by `S7`; present so the refusal is reachable")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    try:
        if args.scored:
            raise Refusal(
                "S7 this runner scores nothing. No `G11.x` verdict is computed "
                "here; scoring the Step 11 suite is work item 11.6, and a tool "
                "that produces the numbers and grades them is the failure shape "
                "`V11.g` exists to prevent.")
        if args.diary_diversity is None:
            raise Refusal(
                "S9 --diary-diversity is unset and has NO DEFAULT. Every drawn "
                "flat draws from the %d households Step 7 shipped per fold, and "
                "the choice between `replicate` (one run per household, "
                "replicated onto flats) and `reseed` (one run per flat, "
                "ownership redrawn, same %d diaries) changes what a stock-scale "
                "number MEANS. That is the author's ruling, not a runner's "
                "default." % (STEP7_HOUSEHOLDS_PER_FOLD,
                              STEP7_HOUSEHOLDS_PER_FOLD))
        if args.diary_diversity != DIARY_DIVERSITY_RULED:
            raise Refusal(
                "S9b --diary-diversity=%s contradicts the ruling on record. The author ruled %r on %s (%r). Running the other mode needs a second sentence, recorded beside the first; passing it on the command line is not that sentence."
                % (args.diary_diversity, DIARY_DIVERSITY_RULED,
                   DIARY_DIVERSITY_RULING_DATE,
                   DIARY_DIVERSITY_RULING_SENTENCE))

        trigger = load_trigger()
        assign_mod = _load("step10_assign", "4thJ_step10_assign.py")

        cells, cell_paths = read_c2_cells(args.c2_out)
        fold = check_cells(cells, cell_paths)
        district = args.district or (cells[0].get("district")
                                     or cells[0].get("cell_id", "").split("__")[0])
        flats, excluded_merged_floor = flats_from_cells(cells)
        if not flats:
            raise Refusal("S3 the `C2` cells carry no drawn flats; there is "
                          "nothing for the trigger to run on")

        check_seam(STEP11_END_USES)

        print("PREFLIGHT")
        print("  `C2` cells      : %d from %s" % (len(cells), args.c2_out))
        print("  fold / district : %s / %s" % (fold, district))
        print("  drawn flats     : %d over %d buildings"
              % (len(flats), len(set(f["building_id"] for f in flats))))
        if excluded_merged_floor:
            print("  `S11` excluded  : %d flat(s) over %d building(s) carry a "
                  "Step 10 floor-merged averaged diary, not a real household -- "
                  "excluded, never simulated as if they were one"
                  % (len(excluded_merged_floor),
                     len(set(r["building_id"] for r in excluded_merged_floor))))

        ctx = prepare_fold(args.root, fold, trigger)
        wanted, present = check_runtime_columns(args.root, fold, ctx["mapping"])
        print("  `G11.14`        : trigger reads %r, diaries carry %d columns, "
              "`act2` excluded by policy" % (wanted, len(present)))
        used = check_diary_identity(flats, ctx["by_hid"], fold, assign_mod)
        print("  diary identity  : %d flats bound to %d distinct households of "
              "the %d shipped" % (len(flats), len(used),
                                  STEP7_HOUSEHOLDS_PER_FOLD))
        print("  !! the stock population has %d BUILDINGS and %d DISTINCT "
              "DIARIES -- see the declaration"
              % (len(set(f["building_id"] for f in flats)), len(used)))
        print("  SCORES NOTHING  : no `G11.x` verdict is computed by this tool.")

        decl = population_declaration(fold, district, flats, cells, used,
                                      args.diary_diversity, args.c2_out,
                                      cell_paths, excluded_merged_floor)

        todo = flats if args.limit is None else flats[:args.limit]
        if args.dry_run and args.limit is None:
            print("DRY RUN: %d flats enumerated, no trigger run, nothing "
                  "written. Add --limit N to trigger N flats." % len(todo))
            return 0

        out_dir = args.out or os.path.join(args.root, "Step11_docs",
                                           "outputs_step11", "c2_%s" % fold)
        os.makedirs(out_dir, exist_ok=True)

        started = time.time()
        cache = {}
        results = []
        for i, flat in enumerate(todo, 1):
            if args.diary_diversity == "replicate" and flat["hid"] in cache:
                rec = cache[flat["hid"]]
            else:
                rec = run_flat(flat, ctx, trigger, args.diary_diversity)
                if args.diary_diversity == "replicate":
                    cache[flat["hid"]] = rec
            results.append(dict(
                building_id=flat["building_id"], case=flat["case"],
                unit_index=flat["unit_index"], zone=flat["zone"],
                storey_index=flat["storey_index"],
                zone_area_m2=flat["zone_area_m2"], hid=flat["hid"],
                presence_file=flat["presence_file"],
                presence_md5=flat["presence_md5"],
                f_levels=flat["f_levels"], cell_ids=flat["cell_ids"],
                arm=flat["arm"], **summarise(rec, TIMESTEP_MIN)))
            if i % 250 == 0 or i == len(todo):
                print("  %d/%d flats (%.1f s)" % (i, len(todo),
                                                  time.time() - started))

        manifest = {
            "work_item": "11.3",
            "campaign": "C2",
            "tool": os.path.basename(__file__),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "declaration": decl,
            "diary_diversity": args.diary_diversity,
            "trigger": {
                "leg": LEG, "year": YEAR, "seed": SEED,
                "timestep_min": TIMESTEP_MIN,
                "dhw_l_per_day": DHW_L_PER_DAY,
                "households_per_fold": STEP7_HOUSEHOLDS_PER_FOLD,
                "activity_appliance_map_md5": ctx["map_md5"],
                "runtime_input_columns": wanted,
                "rotated_to_midnight": True,
                "diary_origin_hour": 0,
            },
            "n_flats_run": len(results),
            "n_flats_enumerated": len(flats),
            "n_flats_excluded_merged_floor": len(excluded_merged_floor),
            "smoke_run": args.limit is not None,
            "scores_nothing": True,
            "flats": results,
        }
        name = "step11_11-3_%s_%s%s.json" % (
            fold, args.diary_diversity, "_smoke" if args.limit else "")
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(manifest, indent=2, sort_keys=True))
        print("WROTE %s  (%d flats, %.1f s)"
              % (path, len(results), time.time() - started))
        if args.limit:
            print("!! SMOKE RUN -- --limit was set, so this is NOT a population "
                  "and no aggregate may be taken from it.")
        return 0
    except Refusal as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
