# -*- coding: utf-8 -*-
"""4J Step 8 --- THE ONE PLACE A THRESHOLD IS WRITTEN DOWN.

`V8.c`: *"the scorer imports its bands from a single module.  A second copy
drifts, and the copy that drifts is the one being quoted."*  Every number in
this file is copied from `Step8_docs/4thJ_08_bemSimulation_val.md`, and every
one carries the line it came from.  Nothing here may be edited to make a gate
pass --- `G8.0` is explicit that a band the untreated control fails is reported
as a band-applicability limitation and its value is NOT moved.

🔴 THE ONE THING THIS MODULE REFUSES TO DO --- AND IT IS NOW RULED
------------------------------------------------------------------
`G8.7` reads *"Per-archetype EUI vs published band --- as-modelled = PASS,
empirical = INFO"* and **names no numeric band anywhere in the project.**
Measured, not assumed: grep of every `.md` under `Step8_docs/` and of
`Prompts/RESUME.md` returns the gate's own row and its commentary, and no
tolerance.  Choosing one here, at the exact moment the first control numbers
exist, is how a band gets fitted to the answer.

`D-S8-5` item 1 (author, 2026-08-25) ruled **(a): G8.7 is reported as INFO,
permanently, with no pass/fail band.**  `G87_TOLERANCE_PCT` therefore stays
`None` for good and the scorer emits `INFO`.  The reason is on the record:
EnergyPlus hourly-dynamic against TABULA monthly quasi-steady-state is a
model-to-model structural comparison, not a compliance test --- `FINDING 121`
is published as a declared methodological limitation instead
(`Step8_docs/docs/2026-08-25_item-8.3_uninjected-control-campaign.md` §10).
A future edit that puts a number here is a band being fitted to an answer
already in hand, and this ruling says it does not happen.
"""

# --------------------------------------------------------------------------
# Tier 5 --- downstream energy.  4thJ_08_bemSimulation_val.md, lines 43-49.
# --------------------------------------------------------------------------
# `D-S8-1` ruled (a) on 2026-08-20: G8.1-G8.4 keep these thresholds and are
# re-cast as REPRODUCIBILITY gates.  "The thresholds do not move; the reference
# is named."  Reference = an independent re-run of the same cell.
G81_NMBE_MONTHLY_PCT = 5.0
G82_NMBE_HOURLY_PCT = 10.0
G83_CVRMSE_MONTHLY_PCT = 15.0
G84_CVRMSE_HOURLY_PCT = 30.0

# G8.5 / G8.6, "inherited from papers 2 and 3".
G85_PEAK_MAGNITUDE_PCT = 15.0
G86_PEAK_TIMING_H = 1

# G8.7 --- see the refusal above.  Ruled permanent by D-S8-5 item 1 (a).
G87_TOLERANCE_PCT = None

# --------------------------------------------------------------------------
# Wiring gates.  Same document, lines 61-69.
# --------------------------------------------------------------------------
G810_METER_CLOSURE_PCT = 0.5      # sum of end uses vs the reported total
G815_SEVERE_MAX = 0               # zero severe errors

# --------------------------------------------------------------------------
# Cross-checks this campaign adds, and where each threshold comes from.
# --------------------------------------------------------------------------
# V8.d wants areas read per archetype from that archetype's OWN artefact.  The
# control reads the floor area EnergyPlus computed from the geometry and checks
# a_ref = floor_area * n_storey against the 8.1 manifest.  0.1 % is a rounding
# tolerance on a quantity that should agree exactly, not a physical band.
AREA_CONSISTENCY_PCT = 0.1

# The two heating series EnergyPlus reports (supply-air hourly, zone monthly)
# are different quantities for a general system; for an ideal-loads zone with no
# outdoor air they must agree closely.  1 % catches a wiring mistake without
# claiming they are the same variable.
SERIES_CONSISTENCY_PCT = 1.0

# --------------------------------------------------------------------------
# Which gates the uninjected control can and cannot evaluate, stated up front
# so a missing gate is a declaration and never an omission.
# --------------------------------------------------------------------------
EVALUABLE_AT_CONTROL = {
    "G8.0": "yes --- this campaign IS G8.0",
    "G8.1": "yes, as reproducibility (D-S8-1 (a)); reference = the re-run",
    "G8.2": "yes, as reproducibility (D-S8-1 (a)); reference = the re-run",
    "G8.3": "yes, as reproducibility (D-S8-1 (a)); reference = the re-run",
    "G8.4": "yes, as reproducibility (D-S8-1 (a)); reference = the re-run",
    "G8.5": "yes, as reproducibility (D-S8-5 item 2 extends D-S8-1 (a) "
            "verbatim); reference = the re-run, threshold unmoved at 15 %.",
    "G8.6": "yes, as reproducibility (D-S8-5 item 2 extends D-S8-1 (a) "
            "verbatim); reference = the re-run, threshold unmoved at 1 h.",
    "G8.7": "yes, as INFO and only as INFO -- D-S8-5 item 1 (a). The "
            "as-modelled reference exists (TABULA q_h_nd); no numeric band "
            "does, and none will be created.",
    "G8.8": "no, not at the control --- one scenario cannot differ from itself. "
            "EVALUATED by work item 8.4's probes, seen passing on two real "
            "scenarios and FAILING on a third wired to the second's schedule "
            "file: Step8_docs/outputs_step8/probes_step8.json.",
    "G8.9": "no, not at the control --- the 8.3 runner has no skip-if-done "
            "cache at all. EVALUATED by work item 8.4's probes, seen passing on "
            "an input-complete key and FAILING on a key over the cell name "
            "alone: Step8_docs/outputs_step8/probes_step8.json.",
    "G8.10": "yes, on the fuel columns EnergyPlus actually reports. The "
             "ELECTRICITY arm is vacuous here: the control model has no "
             "electric end use at all, and that is declared, not hidden.",
    "G8.11": "yes --- every requested Output:Variable is checked for DELIVERY in "
             "the output, which is the same question asked of the artefact.",
    "G8.12": "no --- there is no Step 7 schedule in the control. EVALUATED by "
             "work item 8.5, the first campaign in this project that wires a "
             "Step 7 diary into an IDF: the value arm rebuilds the multiplier "
             "from the published diary on disk and compares it against the "
             "series the SAVED in.idf points at, and the assignment arm checks "
             "that E_PHI_INT still names that Schedule:File object. Both arms "
             "seen failing: Step8_docs/outputs_step8/injected_bands.csv.",
    "G8.13": "yes --- asserted from the in.idf EnergyPlus actually read.",
    "G8.14": "yes --- manifest completeness, with the platform measured per run.",
    "G8.15": "yes --- severe count and warning triage BY KIND (V8.f).",
    "G8.16": "no --- no schedule, so no fold to mis-drive. V8.g's arm IS checked "
             "at the control: every control manifest carries an explicit `fold` "
             "field, so this gate could not later find zero violations over an "
             "absent field. EVALUATED by work item 8.5, which locates each "
             "driving diary BY CONTENT among the three Step 7 bundles on disk "
             "and reads the fold out of the bundle's own manifest.json rather "
             "than out of the cell's filename or the cell's own claim. Seen "
             "failing: Step8_docs/outputs_step8/injected_bands.csv.",
}

PROVENANCE = {
    "G8.1": "val doc line 43, ASHRAE G14 lineage, re-pointed by D-S8-1 (a)",
    "G8.2": "val doc line 44, ASHRAE G14 lineage, re-pointed by D-S8-1 (a)",
    "G8.3": "val doc line 45, ASHRAE G14 lineage, re-pointed by D-S8-1 (a)",
    "G8.4": "val doc line 46, ASHRAE G14 lineage, re-pointed by D-S8-1 (a)",
    "G8.5": "val doc line 47, inherited from papers 2 and 3; re-pointed to "
            "the re-run by D-S8-5 item 2",
    "G8.6": "val doc line 48, inherited; re-pointed by D-S8-5 item 2",
    "G8.7": "val doc line 49, RL13 + project. NO NUMERIC BAND EXISTS, and "
            "D-S8-5 item 1 (a) rules that none is created: INFO, permanently.",
    "G8.8": "val doc line 61. Boolean, no numeric band: two scenarios either "
            "write different result files or they do not. Probed by 8.4.",
    "G8.9": "val doc line 62. Boolean, no numeric band: a wiring change either "
            "moves the cache key or it does not. Probed by 8.4.",
    "G8.10": "val doc line 63",
    "G8.13": "val doc line 66. FINDING 126: the parser read only the LAST "
             "comma-field, so `Interpolate to Timestep = Yes` was invisible on "
             "a real 9-field Schedule:File. Fixed additively 2026-08-25 and "
             "seen firing on BOTH shapes (selftest I9 and I13).",
    "G8.15": "val doc line 69",
    "G8.12": "val doc line 65. Boolean, no numeric band, two arms: value and "
             "ASSIGNMENT. First evaluated by work item 8.5 (2026-08-25); the "
             "value arm is scored against the Step 7 diary re-read from disk, "
             "never against anything the injector reported about itself.",
    "G8.16": "val doc line 71. Boolean, no numeric band. First evaluated by "
             "work item 8.5 (2026-08-25). The count of cells simulating a "
             "country under another country's fold must be 0, and the fold is "
             "read from the Step 7 bundle manifest, not from a filename.",
    "V8.h": "not a val-doc row --- the arm that keeps `f = 0 has no schedule` "
            "from hiding a wrong one. The control endpoint's multiplier is "
            "asserted to be identically 1.0, so `G8.12`/`G8.16` reporting "
            "NOT_EVALUABLE at f = 0 costs no coverage (FINDING 95).",
}


def nmbe_pct(model, ref):
    """Normalised mean bias error, % --- ASHRAE's own form."""
    n = len(ref)
    if n == 0:
        return None
    denom = sum(ref)
    if denom == 0.0:
        return None
    return 100.0 * (sum(m - r for m, r in zip(model, ref))) / denom


def cvrmse_pct(model, ref):
    """CV(RMSE), % --- ASHRAE's own form."""
    n = len(ref)
    if n == 0:
        return None
    mean = sum(ref) / n
    if mean == 0.0:
        return None
    rmse = (sum((m - r) ** 2 for m, r in zip(model, ref)) / n) ** 0.5
    return 100.0 * rmse / mean
