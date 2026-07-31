"""3rdJ_08P_probe_driver.py -- Step 8 (3J Leg-3 4-split): PROBE cell runner.

Runs ONE probe cell out of the 7-cell §P pre-campaign probe table (manager handoff
2026-07-28_employee_step8_probes_P1P4.md §3.2). Each cell injects office/retail/hotel
schedule products (or none, or a deliberately-missing one) into the SuperTall v24.2
mixed-use tower IDF via inject_mixed_use(), ensures the output objects needed for the
P1-P4 gates, simulates via EnergyPlus (through a Singularity wrapper -- Speed is
AlmaLinux 9, the E+ binary is Ubuntu-compiled), extracts two hourly CSVs from the SQL
output, and writes a manifest.json carrying everything the gate script
(3rdJ_08P_probe_gates.py, run separately after the array lands) needs to score P1-P4.

Scope boundary (handoff §1): residential is OUT. No residential channel config is ever
built here; residential Spaces stay at NECB baseline in every cell (the injector already
skips residential Tag-2 unconditionally -- see commercial_integration.py L386-387).

Runs on the cluster via sbatch array (3rdJ_08P_probes.sh), OR locally on Windows via
3rdJ_08P_probes_local.py (LOCAL PORT, 2026-07-28 -- see --engine below). Does NOT modify
commercial_integration.py, eSim_datapreprocessing.py, eSim_dynamicML_mHead.py, or
eSim_dynamicML_mHead_alignment.py.

2026-07-28 built (P1-P4 armament, employee handoff).
2026-07-28 fixed (job 1169671 bug-fix pass): channel_hourly.csv case-mismatch join bug
(zone_to_channel keys vs. SQL KeyValue -- see _build_zone_channel_map / _write_channel_hourly_csv);
loud unmapped-row reporting + hard-fail on 0 mapped rows; driver_md5 added to manifest; added
--postprocess-only (re-derive both CSVs + manifest from an existing eplusout.sql, no re-simulation).
2026-07-28 LOCAL PORT (additive, cluster path unchanged -- see
3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md): added
--engine {auto,cluster,local} + --outroot + --repo-root. On engine=="local", paths resolve
against the local repo checkout instead of /speed-scratch, EnergyPlus is invoked directly
(no Singularity wrapper) via eSim_bem_utils/config.py's ENERGYPLUS_EXE, and every manifest
now carries PLATFORM (sys.platform) + the EnergyPlus version/build actually used, so
3rdJ_08P_probe_gates.py can refuse to compare cells simulated on different platforms.

2026-07-28 Defaut-3 fix ("trou d'empreinte", see the reference doc's OPEN structural
defect): the output path is keyed ONLY by INJ_HASH = md5(commercial_integration.py)[:8],
so a Step-7 product change (the actual content that determines injected schedules) with
an unchanged injector leaves the path unchanged too -- a re-simulation would overwrite
in place with no guard. Added a SEPARATE INPUTS_HASH = md5 over the Step-7 product CSVs
this cell actually reads (see _compute_inputs_hash), written into every manifest.json.
Deliberately NOT merged into INJ_HASH: INJ_HASH must keep owning the output directory
PATH so --postprocess-only recovery (re-derive CSVs from an untouched eplusout.sql,
seconds instead of tens of minutes) keeps working even when only post-processing code
changes. Before writing anything into an existing outdir, _check_inputs_hash_guard()
compares INPUTS_HASH against the manifest already there and refuses (exit 1) on any
mismatch -- including a missing/legacy INPUTS_HASH (pre-fix manifest), treated as
UNKNOWN rather than safe -- unless --allow-stale-inputs is passed. Same guard call runs
identically for engine=="cluster" and engine=="local" (inserted before the
engine-specific simulate branch, so the verbatim Singularity wrapper is untouched).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (Linux, cluster-only; grouped here per 3rdJ_08W_audit_wiring.py convention)
# ---------------------------------------------------------------------------
SCRATCH8 = "/speed-scratch/o_iseri/step8_4split"
UPLOAD = SCRATCH8 + "/upload"
PROBES_ROOT = SCRATCH8 + "/probes"

# IDF stock: reused from Leg-2's v24.2 transition, NOT re-transitioned (handoff §2).
# SuperTall is the probe building (7,721,326 B, verified 2026-07-28).
IDF_SUPERTALL = (
    "/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/"
    "Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/"
    "SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf"
)

# EPW -- NOTE (2026-07-28, verified on cluster by ls): the handoff doc's stated path
# (.../step8_4split/upload/BEM_Setup/WeatherFile/...) does NOT exist; the file lives
# under the step8_2split upload tree, alongside the reused IDF stock. Corrected here;
# see the Progress Log entry for this discrepancy.
EPW = (
    "/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/"
    "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
)

SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"

STEP7_OUT = UPLOAD + "/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7"
INJECTOR_PY = UPLOAD + "/eSim_bem_utils/commercial_integration.py"

sys.path.insert(0, UPLOAD)  # fallback in case PYTHONPATH wasn't propagated to the job env

# ---------------------------------------------------------------------------
# LOCAL (Windows) path defaults -- ADDITIVE, 2026-07-28 port. None of the cluster
# constants above are modified; --engine (see main()) selects which set is actually
# used for a given run. Resolved from the repo checkout this script itself lives in
# (Step8_docs -> Leg3_4-split -> 3J_docs_occ_nTemp -> repo root), so it works from any
# clone path, not just this machine's.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

LOCAL_PROBES_ROOT = os.path.join(
    LOCAL_REPO_ROOT, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs", "probes_local")
LOCAL_IDF_SUPERTALL = os.path.join(
    LOCAL_REPO_ROOT, "3J_docs_occ_nTemp", "Leg2_2-split", "Step8_docs", "outputs_step8",
    "office_idfs_v242", "CAN_MTL", "SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf")
LOCAL_EPW = os.path.join(
    LOCAL_REPO_ROOT, "BEM_Setup", "WeatherFile",
    "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw")
LOCAL_STEP7_OUT = os.path.join(
    LOCAL_REPO_ROOT, "3J_docs_occ_nTemp", "Leg3_4-split", "Step7_docs", "outputs_step7")
LOCAL_INJECTOR_PY = os.path.join(LOCAL_REPO_ROOT, "eSim_bem_utils", "commercial_integration.py")

# On Windows, eSim_bem_utils lives at LOCAL_REPO_ROOT directly (no /upload mirror like the
# cluster scratch tree) -- add it so `from eSim_bem_utils...` resolves. Does not touch the
# cluster sys.path.insert(0, UPLOAD) above; on Linux this block is simply skipped.
if sys.platform == "win32":
    sys.path.insert(0, LOCAL_REPO_ROOT)


# ---------------------------------------------------------------------------
# Probe cell table (handoff §3.2, SuperTall / MTL Z6, one-at-a-time design).
# Parametrized on step7_out (2026-07-28 LOCAL PORT) so the same table can be built
# against either the cluster STEP7_OUT or a local one -- see _resolve_engine_paths().
# CELLS below (module level) preserves the exact cluster-default value for any code
# that imports this module and reads CELLS directly, unchanged from before this port.
# ---------------------------------------------------------------------------
def _build_cells(step7_out: str) -> list:
    def _csv(name: str) -> str:
        return os.path.join(step7_out, name)

    office_2022 = _csv("office_presence_multiplier_2022.csv")
    office_2030 = _csv("office_presence_multiplier_2030.csv")
    retail_2022 = _csv("retail_presence_multiplier_2022.csv")
    retail_2030_central = _csv("retail_presence_multiplier_2030_central.csv")
    retail_2030_opt = _csv("retail_presence_multiplier_2030_opt.csv")
    hotel_2022 = _csv("hotel_schedule_multiplier_2022.csv")
    hotel_2030_central = _csv("hotel_schedule_multiplier_2030_central.csv")
    hotel_2030_opt = _csv("hotel_schedule_multiplier_2030_opt.csv")
    # Deliberately nonexistent -- the P4/W5 fall-back trip wire for cell 6. Never create this file.
    retail_nonexistent = _csv("retail_presence_multiplier_2030_DOES_NOT_EXIST.csv")

    return [
        {"tag": "baseline_necb", "channels": {}},
        {"tag": "B_central", "channels": {
            "office": {"csv": office_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
            "retail": {"csv": retail_2030_central, "pr": "QC"},
            "hotel": {"csv": hotel_2030_central, "pr": "QC"},
        }},
        {"tag": "var_office", "channels": {
            "office": {"csv": office_2030, "archetype": "Office_Knowledge", "band": "fullyhybrid"},
            "retail": {"csv": retail_2030_central, "pr": "QC"},
            "hotel": {"csv": hotel_2030_central, "pr": "QC"},
        }},
        {"tag": "var_retail", "channels": {
            "office": {"csv": office_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
            "retail": {"csv": retail_2030_opt, "pr": "QC"},
            "hotel": {"csv": hotel_2030_central, "pr": "QC"},
        }},
        {"tag": "var_hotel", "channels": {
            "office": {"csv": office_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
            "retail": {"csv": retail_2030_central, "pr": "QC"},
            "hotel": {"csv": hotel_2030_opt, "pr": "QC"},
        }},
        {"tag": "cycle_2022", "channels": {
            "office": {"csv": office_2022, "archetype": "Office_Knowledge", "band": "observed"},
            "retail": {"csv": retail_2022, "pr": "QC"},
            "hotel": {"csv": hotel_2022, "pr": "QC"},
        }},
        {"tag": "fallback_retail", "channels": {
            "office": {"csv": office_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
            "retail": {"csv": retail_nonexistent, "pr": "QC"},
            "hotel": {"csv": hotel_2030_central, "pr": "QC"},
        }},
    ]


CELLS = _build_cells(STEP7_OUT)  # cluster default -- identical to the pre-port literal table

# ---------------------------------------------------------------------------
# Output objects to ensure on every injected IDF (handoff §3.1 step 3 -- the Leg-2
# office SQL-gap lesson: do this on every path, no exceptions)
# ---------------------------------------------------------------------------
# --- Meters -----------------------------------------------------------------
# 🔴 FIXED 2026-07-31 (Defaut 5). The previous list asked for `Gas:Facility`, `Heating:Gas`,
# `InteriorEquipment:Gas`, `WaterSystems:Gas`. EnergyPlus 9.4 renamed the resource `Gas` ->
# `NaturalGas`; in 24.2 those four names DO NOT EXIST (verified: eplusout.mdd has no
# `Gas:Facility` at all, and does have `NaturalGas:Facility`). EnergyPlus warned four times --
# `Output:Meter: invalid Key Name="GAS:FACILITY" - not found.`, eplusout.err:916-919 -- the SQL
# had no such rows, and the zero-fill in _write_hourly_meters_csv turned "absent" into "0.0".
# The CLG cell therefore reported 0 J of gas while the End Uses table of the SAME run reported
# 13,884.91 GJ: DHW 7,726.75 + heating 4,082.08 + hotel laundry 2,076.08 = 53.5 % of site energy.
# Three electricity end uses were missing too (ExteriorLights 682.88 + HeatRejection 168.28 +
# HeatRecovery 537.48 GJ), leaving 11.52 % of Electricity:Facility unattributed.
#
# This list is NOT claimed to be prophetic. Completeness is proved per run by
# _check_fuel_closure() -- the §6b-4 unmetered-end-use tripwire, declared since 2J Bug B and
# never implemented until now, which is exactly why the defect shipped. A building with an end
# use we did not list makes closure FAIL loudly instead of silently under-reporting.
FUEL_TOTAL_METERS = ["Electricity:Facility", "NaturalGas:Facility"]
END_USE_METERS = {
    "Electricity": [
        "InteriorLights:Electricity", "ExteriorLights:Electricity",
        "InteriorEquipment:Electricity", "Fans:Electricity", "Pumps:Electricity",
        "Cooling:Electricity", "Heating:Electricity", "HeatRejection:Electricity",
        "HeatRecovery:Electricity", "WaterSystems:Electricity",
    ],
    "NaturalGas": [
        "InteriorEquipment:NaturalGas", "Heating:NaturalGas", "WaterSystems:NaturalGas",
    ],
}
# Relative tolerance on |Sigma(end uses) - <Fuel>:Facility| / <Fuel>:Facility. EnergyPlus
# end-use meters partition the fuel total exactly; anything above float noise means an end use
# is missing from the list above.
FUEL_CLOSURE_TOL = 1e-3
REQUIRED_METERS = FUEL_TOTAL_METERS + [m for ms in END_USE_METERS.values() for m in ms]

REQUIRED_VARIABLES = [
    "Zone People Occupant Count",
    "Zone Lights Electricity Energy",
    "Zone Electric Equipment Electricity Energy",
    # Added 2026-07-31 (Defaut 5, point 4). dr_L3-10 locks "hourly load-weighted" central-plant
    # allocation ("never area-weighted, never unattributed"), but nothing in the campaign
    # reported a per-zone HVAC load, so that allocation was not computable at all. Both names
    # verified present in eplusout.rdd of the CLG cell before being requested.
    "Zone Air System Sensible Cooling Energy",
    "Zone Air System Sensible Heating Energy",
    # Gas equipment is 2,076.08 GJ on the Tall tower and lives in exactly two Spaces
    # (F30 Hotel_bot_Laundry, F38 Hotel_top_Kitchen -- both hotel). Attributing it through the
    # zone variable rather than hard-coding "it is all hotel" keeps the rule general: another
    # prototype with a gas kitchen in the office podium still lands in the right channel.
    "Zone Gas Equipment NaturalGas Energy",
]
VAR_METRIC = {
    "Zone People Occupant Count": "people",
    "Zone Lights Electricity Energy": "lights",
    "Zone Electric Equipment Electricity Energy": "equip",
    "Zone Air System Sensible Cooling Energy": "syscool",
    "Zone Air System Sensible Heating Energy": "sysheat",
    "Zone Gas Equipment NaturalGas Energy": "gasequip",
}
# DHW is 7,726.75 GJ of gas on the Tall tower -- ~30 % of site energy, hotel-dominated -- and
# WaterUse:Equipment objects carry a BLANK `Zone Name`, so they cannot ride the zone->channel
# map. Their NAMES do carry the channel: every one is "<SpaceName> Service Water Use <x>gpm <T>F"
# (e.g. "F21 Resi_bot_E_Apartment Service Water Use 0.08gpm 140F"), except two plant-level units
# ("Booster ...", "Laundry ...") resolved by the prototype token in their flow-fraction schedule.
# All 47 objects on the Tall tower resolve, none unassigned (validated 2026-07-31).
DHW_VARIABLE = "Water Use Equipment Heating Energy"

# Defaut 5, point 5 -- the OTHER end of the Defaut-3 fingerprint hole. INJ_HASH =
# md5(commercial_integration.py) owns the output PATH, so it catches a wiring change but is
# blind to a change in WHAT WE ASK ENERGYPLUS TO REPORT. Without this, fixing the meter list
# would leave every existing cell looking "done" and the resume logic would skip them all --
# the same class of silent staleness, on the reporting side. Written into every manifest by
# _do_postprocess() and checked by _cell_complete().
OUTPUT_SCHEMA_HASH = hashlib.md5(
    json.dumps({"meters": REQUIRED_METERS,
                "variables": REQUIRED_VARIABLES + [DHW_VARIABLE]},
               sort_keys=True).encode("utf-8")
).hexdigest()[:8]
CHANNEL_AGG = {
    "residential": {"residential"},
    # residential_common (corridors/common areas, TAG2_RESIDENTIAL_COMMON) is emitted as its
    # OWN column, NOT folded into "residential" -- unlike office_support/hotel_support, which
    # genuinely ARE modulated by their channel's injection, residential_common is injected by
    # NOBODY: the commercial MODULATE loop skips it (`continue`, commercial_integration.py
    # ~L640) and inject_residential() iterates only TAG2_RESIDENTIAL (the apartments). Folding
    # an uninjected constant-NECB-baseline Space into "residential" would dilute the reported
    # residential level relative to office/hotel (whose *_support counterparts ARE injected),
    # biasing per-channel attribution. See 3rdJ_08_simulation_4split.md Progress Log,
    # 2026-07-28 residential_common column split.
    "residential_common": {"residential_common"},
    "office": {"office", "office_support"},
    "retail": {"retail"},
    "hotel": {"hotel", "hotel_support"},
    "service_MEP": {"service_mep"},
}
_FINE_TO_AGG = {fine: agg for agg, fines in CHANNEL_AGG.items() for fine in fines}

# Tag-2 field priority on a SPACE object -- verbatim from 3rdJ_08W_audit_wiring.py
# (empirically verified 2026-07-28 against the real IDF, L13682: eppy attribute `Tag_2`).
_SPACE_TAG2_FIELDS = ("Tag_2", "Space_Type_Name", "Space_Type", "Name")


def _get_space_tag2(space_obj) -> str:
    for f in _SPACE_TAG2_FIELDS:
        v = getattr(space_obj, f, "")
        if v:
            return str(v).strip()
    return ""


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _compute_inputs_hash(channels: dict) -> tuple:
    """INPUTS_HASH -- Defaut-3 fix ("trou d'empreinte", 3rdJ_08_implementation_improvements.md).

    md5 over the Step-7 product CSVs this cell actually reads. Exact, reproducible
    recipe: for each channel name in the cell's `channels` dict, in SORTED
    (alphabetical) order -- deliberately NOT the dict's insertion order, which is an
    incidental property of how _build_cells() happens to list its keys, not a
    contract -- append one line "<channel>|<csv_path-as-configured>|<md5-or-MISSING>"
    (csv path exactly as configured, i.e. NOT normalized/resolved -- two cells that
    read files at different paths must hash differently even if the bytes happen to
    match; "MISSING" if the path is empty or the file doesn't exist, e.g. cell 6's
    deliberately-absent retail CSV). Lines are '\\n'-joined and md5'd. A cell with no
    channels at all (baseline_necb) hashes the empty string -- a fixed, deterministic
    value, not an error.

    Deliberately a SEPARATE hash from INJ_HASH (which fingerprints only
    commercial_integration.py and owns the output directory PATH, see main()): a
    product-only change must be able to change INPUTS_HASH without moving the path
    (that is exactly the defect being closed), and a post-processing-only change to
    THIS driver must never change INPUTS_HASH at all (it never touches the Step-7
    CSVs) -- that is what keeps --postprocess-only recovery working.

    Returns (hash[:8], detail) where detail is a list of
    {"channel", "csv_path", "csv_md5"} dicts (csv_md5 is None when the file was
    "MISSING") -- written into the manifest as INPUTS_HASH_DETAIL and used by
    _diff_inputs() to name exactly which product file(s) changed.
    """
    entries = []
    detail = []
    for ch in sorted(channels.keys()):
        csv_path = channels[ch].get("csv", "")
        exists = bool(csv_path) and os.path.isfile(csv_path)
        file_md5 = md5_file(csv_path) if exists else "MISSING"
        entries.append(f"{ch}|{csv_path}|{file_md5}")
        detail.append({
            "channel": ch, "csv_path": csv_path,
            "csv_md5": None if file_md5 == "MISSING" else file_md5,
        })
    h = hashlib.md5("\n".join(entries).encode("utf-8")).hexdigest()
    return h[:8], detail


def _diff_inputs(old_detail, new_detail) -> str:
    """Human-readable list of which product file(s) differ between two
    INPUTS_HASH_DETAIL lists (existing manifest vs. the current run), for the
    STALE-INPUTS GUARD refusal message. old_detail may be None (legacy manifest that
    predates INPUTS_HASH_DETAIL entirely)."""
    if not old_detail:
        return "unknown -- existing manifest has no INPUTS_HASH_DETAIL (legacy/pre-Defaut-3-fix run)"
    old_by_ch = {d.get("channel"): d for d in old_detail}
    new_by_ch = {d.get("channel"): d for d in new_detail}
    diffs = []
    for ch in sorted(set(old_by_ch) | set(new_by_ch)):
        o, n = old_by_ch.get(ch), new_by_ch.get(ch)
        o_md5 = (o.get("csv_md5") or "MISSING") if o else "(channel absent)"
        n_md5 = (n.get("csv_md5") or "MISSING") if n else "(channel absent)"
        if o_md5 != n_md5:
            diffs.append(f"{ch}: {o_md5} -> {n_md5}")
    return "; ".join(diffs) if diffs else "(no per-channel csv_md5 difference found)"


def _archive_stale_dir(outdir: str) -> str:
    """Never overwrite an existing outdir in place -- rename it aside with a
    timestamp suffix instead. Same '_STALE_<timestamp>' convention as
    3rdJ_08P_probes_local.py::_archive_stale (reused deliberately, per the reference
    doc: 'reuse it rather than inventing a second convention'). Archives, never
    deletes."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = outdir.rstrip("\\/") + f"_STALE_{ts}"
    os.rename(outdir, dest)
    print(f"[archive] stale-inputs outdir archived -> {dest} (never overwritten in place)")
    return dest


def _check_inputs_hash_guard(outdir: str, inputs_hash: str, inputs_detail: list,
                              allow_override: bool, postprocess_only: bool) -> None:
    """Defaut-3 fix -- the actual guard. Called once, early, before ANY write into
    outdir (before os.makedirs), identically for engine=="cluster" and
    engine=="local". If outdir doesn't exist yet, or its manifest.json's INPUTS_HASH
    already equals the current run's, this is a silent no-op (the common case).

    Otherwise it refuses (exit 1) and prints both hashes + which product file(s)
    differ, UNLESS --allow-stale-inputs was passed -- and even then the remedy
    differs by mode, because "override" cannot mean the same thing in both:

      * normal simulate path (postprocess_only=False): override ARCHIVES the stale
        outdir aside (_archive_stale_dir, never deleted) and lets a fresh outdir be
        created for a real re-simulation. This is the "legitimate re-simulation
        after a known product fix" case.
      * --postprocess-only (postprocess_only=True): archiving would delete the very
        eplusout.sql this mode exists to reuse, so override NEVER archives here.
        Override is honored ONLY for a LEGACY manifest (no INPUTS_HASH at all,
        pre-dating this fix) -- there it just adopts the current INPUTS_HASH in
        place as a one-time operator assertion that the existing sql really was
        built from today's products. A GENUINE mismatch (manifest has an
        INPUTS_HASH and it disagrees) is refused unconditionally even with
        --allow-stale-inputs: postprocess-only never re-simulates, so it can never
        legitimately resolve a real product mismatch -- that requires a real
        re-simulation via the normal path.

    A missing/legacy manifest (no INPUTS_HASH key -- predates this fix) is treated
    as UNKNOWN, not as safe-to-reuse: an old manifest can carry a fully valid
    ~16-38 min simulation, and "no data recorded" is not evidence that today's
    products match it. Refuse by default like any other mismatch; the operator
    opts in via --allow-stale-inputs exactly like a genuine mismatch (see above for
    the postprocess-only carve-out).
    """
    manifest_path = os.path.join(outdir, "manifest.json")
    if not os.path.isfile(manifest_path):
        return  # nothing to protect

    existing, read_error = None, None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception as e:
        read_error = str(e)

    existing_hash = existing.get("INPUTS_HASH") if existing else None
    if read_error is None and existing_hash == inputs_hash:
        return  # identical inputs (or both empty, e.g. baseline_necb) -- safe to reuse in place

    legacy = False
    if read_error is not None:
        reason = f"existing manifest.json at {manifest_path} is unreadable ({read_error})"
        detail_msg = "cannot compare -- treat as UNKNOWN"
    elif existing_hash is None:
        legacy = True
        reason = ("existing manifest predates INPUTS_HASH (legacy/pre-Defaut-3-fix run) -- "
                  "treated as UNKNOWN, not as safe-to-reuse")
        detail_msg = _diff_inputs(existing.get("INPUTS_HASH_DETAIL"), inputs_detail)
    else:
        reason = f"existing INPUTS_HASH={existing_hash} != current INPUTS_HASH={inputs_hash}"
        detail_msg = _diff_inputs(existing.get("INPUTS_HASH_DETAIL"), inputs_detail)

    print(f"[FAIL] STALE-INPUTS GUARD ({outdir}):")
    print(f"       {reason}")
    print(f"       differing product file(s): {detail_msg}")

    if postprocess_only:
        if allow_override and legacy:
            print("       --allow-stale-inputs on a LEGACY manifest under --postprocess-only: "
                  "adopting the current INPUTS_HASH in place, NOT archiving (archiving would "
                  "delete the eplusout.sql this mode exists to reuse). One-time operator "
                  "assertion that the existing simulation output really was built from today's "
                  "products.")
            return
        if allow_override and not legacy:
            print("       --allow-stale-inputs is NOT honored here: a genuine INPUTS_HASH "
                  "mismatch under --postprocess-only means the existing eplusout.sql was built "
                  "from DIFFERENT products than today's -- postprocess-only never re-simulates, "
                  "so it cannot legitimately fix that. Run a real simulation instead.")
        print("       Refusing to write.")
        sys.exit(1)
    else:
        if allow_override:
            _archive_stale_dir(outdir)
            return
        print("       Refusing to write. Pass --allow-stale-inputs to archive the existing "
              "outdir aside (never overwritten in place, never deleted) and proceed with a "
              "real re-simulation against the current products -- only for a deliberate "
              "re-simulation after a known product fix.")
        sys.exit(1)


def _energyplus_provenance(engine: str) -> dict:
    """Platform + EnergyPlus provenance for the manifest (2026-07-28 LOCAL PORT,
    Contrainte n3): PLATFORM (sys.platform), the EnergyPlus version/build actually
    used, and the executable path. 3rdJ_08P_probe_gates.py adds a gate that FAILs if
    cells being compared don't share PLATFORM -- same build hash is NOT proof of
    bit-identical output across compilers/libm/rounding (win32 vs Linux).

    cluster: derived from the SIF_EXE constant path -- no extra subprocess/singularity
    call, zero behavioural change to the cluster path.
    local: derived by actually invoking `energyplus.exe --version` (cheap, ms-scale) so
    the recorded build hash is verified against what really ran, not assumed.
    """
    info: dict = {"PLATFORM": sys.platform, "engine": engine}
    if engine == "cluster":
        m = re.search(r"EnergyPlus-([\d.]+)-([0-9a-f]+)-", SIF_EXE)
        info["energyplus_version"] = m.group(1) if m else None
        info["energyplus_build"] = m.group(2) if m else None
        info["energyplus_exe_used"] = f"singularity exec {SIF} {SIF_EXE}"
    else:
        try:
            from eSim_bem_utils.config import ENERGYPLUS_EXE
            out = subprocess.run([ENERGYPLUS_EXE, "--version"], capture_output=True,
                                  text=True, timeout=30)
            text = (out.stdout or "") + (out.stderr or "")
            m = re.search(r"Version\s+([\d.]+)-([0-9a-f]+)", text)
            info["energyplus_version"] = m.group(1) if m else None
            info["energyplus_build"] = m.group(2) if m else None
            info["energyplus_exe_used"] = ENERGYPLUS_EXE
            info["energyplus_version_raw"] = text.strip()
        except Exception as e:
            info["energyplus_version"] = None
            info["energyplus_build"] = None
            info["energyplus_exe_used"] = None
            info["energyplus_provenance_error"] = str(e)
    return info


def _write_manifest(outdir: str, manifest: dict) -> str:
    path = os.path.join(outdir, "manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"[manifest] written: {path}")
    return path


# ---------------------------------------------------------------------------
# Step 3 -- ensure Output:SQLite / hourly Output:Meter / hourly Output:Variable(*) /
# full-year RunPeriod on the injected IDF (idempotent: add only what's missing).
# ---------------------------------------------------------------------------
def _ensure_output_objects(idf, verbose: bool = True) -> None:
    # Output:SQLite = SimpleAndTabular
    sql_objs = idf.idfobjects.get("OUTPUT:SQLITE", [])
    if not sql_objs:
        obj = idf.newidfobject("Output:SQLite")
        obj.Option_Type = "SimpleAndTabular"
        if verbose:
            print("  [ensure-outputs] added Output:SQLite (SimpleAndTabular)")
    else:
        for obj in sql_objs:
            if str(getattr(obj, "Option_Type", "")).strip() != "SimpleAndTabular":
                obj.Option_Type = "SimpleAndTabular"
                if verbose:
                    print("  [ensure-outputs] forced Output:SQLite Option_Type=SimpleAndTabular")

    # Hourly Output:Meter (add if absent, matched on name + Hourly frequency)
    existing_meters = set()
    for m in idf.idfobjects.get("OUTPUT:METER", []):
        freq = str(getattr(m, "Reporting_Frequency", "")).strip().lower()
        existing_meters.add((str(getattr(m, "Key_Name", "")).strip(), freq))
    n_added = 0
    for meter_name in REQUIRED_METERS:
        if (meter_name, "hourly") not in existing_meters:
            obj = idf.newidfobject("Output:Meter")
            obj.Key_Name = meter_name
            obj.Reporting_Frequency = "Hourly"
            n_added += 1
    if verbose and n_added:
        print(f"  [ensure-outputs] added {n_added} hourly Output:Meter objects")

    # Hourly Output:Variable, Key_Value="*" (add if absent, matched on key + name + frequency)
    existing_vars = set()
    for v in idf.idfobjects.get("OUTPUT:VARIABLE", []):
        freq = str(getattr(v, "Reporting_Frequency", "")).strip().lower()
        key = str(getattr(v, "Key_Value", "")).strip()
        name = str(getattr(v, "Variable_Name", "")).strip()
        existing_vars.add((key, name, freq))
    n_added_v = 0
    for var_name in REQUIRED_VARIABLES + [DHW_VARIABLE]:
        if ("*", var_name, "hourly") not in existing_vars:
            obj = idf.newidfobject("Output:Variable")
            obj.Key_Value = "*"
            obj.Variable_Name = var_name
            obj.Reporting_Frequency = "Hourly"
            n_added_v += 1
    if verbose and n_added_v:
        print(f"  [ensure-outputs] added {n_added_v} hourly Output:Variable(*) objects")

    # RunPeriod = full year (Timestep left as-is per handoff §3.1 step 3)
    rps = idf.idfobjects.get("RUNPERIOD", [])
    if not rps:
        rp = idf.newidfobject("RunPeriod")
        rp.Name = "P_Probe_FullYear"
        rp.Begin_Month = 1
        rp.Begin_Day_of_Month = 1
        rp.End_Month = 12
        rp.End_Day_of_Month = 31
        if verbose:
            print("  [ensure-outputs] created full-year RunPeriod (none existed)")
    else:
        for rp in rps:
            changed = False

            def _asint(v):
                try:
                    return int(str(v).strip())
                except (TypeError, ValueError):
                    return None

            if _asint(getattr(rp, "Begin_Month", None)) != 1 or _asint(getattr(rp, "Begin_Day_of_Month", None)) != 1:
                rp.Begin_Month = 1
                rp.Begin_Day_of_Month = 1
                changed = True
            if _asint(getattr(rp, "End_Month", None)) != 12 or _asint(getattr(rp, "End_Day_of_Month", None)) != 31:
                rp.End_Month = 12
                rp.End_Day_of_Month = 31
                changed = True
            if verbose and changed:
                print(f"  [ensure-outputs] forced RunPeriod '{getattr(rp, 'Name', '')}' to full year")


# ---------------------------------------------------------------------------
# Step 5 -- SQL -> CSV extraction. Ports the query shape of Leg-2's
# eSim_bem_utils_3J/plotting.py::get_hourly_meter_data (ReportData/ReportDataDictionary,
# EnvironmentType=3, Hourly), reimplemented here restricted to the requested
# meters/variables and pivoted to one-column-per-series (stated in the Progress Log).
# ---------------------------------------------------------------------------
def _check_fuel_closure(pivot, absent: list) -> dict:
    """§6b point 4 -- the unmetered-end-use tripwire, declared since 2J Bug B and never
    implemented until 2026-07-31 (that is exactly why Defaut 5 shipped).

    EnergyPlus end-use meters PARTITION their fuel total, so Sigma(end uses) == <Fuel>:Facility
    holds to float noise whenever the requested list is complete. A residual above
    FUEL_CLOSURE_TOL therefore means one of two things, both fatal to per-channel EUI: an end
    use exists that REQUIRED_METERS does not list, or a listed meter name is wrong for this
    EnergyPlus version and was zero-filled.

    Validated 2026-07-31 by being SEEN FAILING on the pre-fix CLG SQL (Electricity residual
    11.5216 %, NaturalGas total meter absent), failing on an injected 5 % shortfall, and
    passing on a complete pivot. Returns a per-fuel report; never raises -- the caller decides,
    so a diagnostic run can still produce its CSVs.
    """
    report = {}
    for fuel, ends in END_USE_METERS.items():
        total_col = f"{fuel}:Facility"
        total = float(pivot[total_col].sum()) if total_col in pivot.columns else 0.0
        parts = float(sum(pivot[c].sum() for c in ends if c in pivot.columns))
        resid = parts - total
        rel = 0.0 if total == 0.0 else abs(resid) / abs(total)
        # A fuel whose TOTAL meter is itself absent closes trivially at 0 == 0 and would sail
        # through -- which is precisely how Defaut 5 would have survived its own tripwire. An
        # absent total is never evidence of "no such fuel"; it is evidence of a bad name.
        total_absent = total_col in absent
        report[fuel] = {
            "facility_total_J": total,
            "sum_end_uses_J": parts,
            "residual_J": resid,
            "residual_rel": rel,
            "facility_meter_absent": total_absent,
            "closed": bool(rel <= FUEL_CLOSURE_TOL) and not total_absent,
            "end_use_meters": ends,
        }
    report["absent_meters"] = absent
    return report


def _write_hourly_meters_csv(sql_path: str, out_csv: str) -> tuple:
    conn = sqlite3.connect(sql_path)
    try:
        placeholders = ",".join("?" * len(REQUIRED_METERS))
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, Name "
            "FROM ReportDataDictionary "
            f"WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name IN ({placeholders})",
            conn, params=REQUIRED_METERS,
        )
        if meta.empty:
            raise RuntimeError("no matching Hourly meter rows in ReportDataDictionary")
        idx_list = meta["ReportDataDictionaryIndex"].tolist()
        idx_placeholders = ",".join("?" * len(idx_list))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS idx, rd.Value AS value, rd.TimeIndex AS t "
            "FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({idx_placeholders}) "
            "ORDER BY rd.TimeIndex ASC",
            conn, params=idx_list,
        )
    finally:
        conn.close()

    idx_to_name = dict(zip(meta["ReportDataDictionaryIndex"], meta["Name"]))
    data["name"] = data["idx"].map(idx_to_name)
    pivot = data.pivot_table(index="t", columns="name", values="value", aggfunc="sum")
    pivot = pivot.reindex(sorted(pivot.index))
    # 🔴 This zero-fill is what made Defaut 5 invisible: a meter EnergyPlus never produced
    # became a column of hard zeros, indistinguishable from a genuine zero. The fill stays (a
    # missing column would break every downstream reader) but it is now RECORDED and
    # cross-checked by _check_fuel_closure -- absence must leave a trace.
    absent = [m for m in REQUIRED_METERS if m not in pivot.columns]
    for m in absent:
        pivot[m] = 0.0
    if absent:
        print(f"  [hourly_meters] {len(absent)} requested meter(s) ABSENT from the SQL, "
              f"zero-filled and recorded in the manifest: {absent}")
    pivot = pivot[REQUIRED_METERS]
    pivot.to_csv(out_csv, index=False)
    return len(pivot), _check_fuel_closure(pivot, absent)


def _write_dhw_hourly_csv(sql_path: str, injected_idf_path: str, eplus_idd: str, out_csv: str) -> tuple:
    """Per-channel DHW (Water Use Equipment Heating Energy).

    WaterUse:Equipment carries a blank `Zone Name`, so these series cannot ride the
    zone->channel map. Two resolution rules, in order, both read off the IDF (never guessed):

      1. The equipment Name is "<SpaceName> Service Water Use <x>gpm <T>F" -- split at
         " SERVICE WATER USE" and classify the resulting Space through the Tag-2 census.
      2. Plant-level units with no Space prefix ("Booster ...", "Laundry ...") are resolved by
         the prototype token in their Flow Rate Fraction Schedule Name (HotelLarge -> hotel,
         OfficeLarge -> office, RetailStandalone -> retail, *Apartment -> residential).

    On the Tall tower all 47 objects resolve (27 residential, 16 hotel, 2 retail, 2 office);
    the two schedule-resolved ones are Booster and Laundry, both HOTELLARGE. Anything
    unresolved goes to an `unassigned` column rather than being dropped, so the total still
    closes against WaterSystems:*.
    """
    from eppy.modeleditor import IDF
    from eSim_bem_utils.commercial_integration import classify_tag2
    IDF.setiddname(eplus_idd)
    idf = IDF(injected_idf_path)

    space_to_channel = {}
    for sp in idf.idfobjects.get("SPACE", []):
        agg = _FINE_TO_AGG.get(classify_tag2(_get_space_tag2(sp)))
        if agg:
            space_to_channel[str(sp.Name).strip().upper()] = agg
    SCHED_TOKEN = (("HOTELLARGE", "hotel"), ("OFFICELARGE", "office"),
                   ("RETAILSTANDALONE", "retail"), ("MIDRISEAPARTMENT", "residential"),
                   ("HIGHRISEAPARTMENT", "residential"))

    equip_to_channel = {}
    for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
        key = str(we.Name).strip().upper()
        head = key.split(" SERVICE WATER USE")[0].strip()
        ch = space_to_channel.get(head)
        if ch is None:
            sched = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").upper()
            ch = next((c for tok, c in SCHED_TOKEN if tok in sched), None)
        equip_to_channel[key] = ch

    conn = sqlite3.connect(sql_path)
    try:
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, KeyValue, Name FROM ReportDataDictionary "
            "WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name = ?",
            conn, params=[DHW_VARIABLE],
        )
        if meta.empty:
            raise RuntimeError(f"no Hourly '{DHW_VARIABLE}' rows in ReportDataDictionary")
        idx_list = meta["ReportDataDictionaryIndex"].tolist()
        idx_ph = ",".join("?" * len(idx_list))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS idx, rd.Value AS value, rd.TimeIndex AS t "
            "FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({idx_ph}) "
            "ORDER BY rd.TimeIndex ASC",
            conn, params=idx_list,
        )
    finally:
        conn.close()

    df = data.join(meta.set_index("ReportDataDictionaryIndex")[["KeyValue"]], on="idx")
    df["channel"] = (df["KeyValue"].astype(str).str.strip().str.upper()
                     .map(equip_to_channel).fillna("unassigned"))
    unresolved = sorted({k for k, v in equip_to_channel.items() if v is None})
    if unresolved:
        print(f"  [dhw_hourly] {len(unresolved)} WaterUse:Equipment unresolved -> 'unassigned' "
              f"(<=5 shown): {unresolved[:5]}")
    pivot = df.pivot_table(index="t", columns="channel", values="value", aggfunc="sum")
    pivot = pivot.reindex(sorted(pivot.index))
    cols = ["office", "retail", "hotel", "residential", "residential_common",
            "service_MEP", "unassigned"]
    for c in cols:
        if c not in pivot.columns:
            pivot[c] = 0.0
    pivot = pivot[cols]
    pivot.columns = [f"dhw_{c}" for c in cols]
    pivot.to_csv(out_csv, index=False)
    return len(pivot), unresolved


def _build_zone_channel_map(idf) -> tuple[dict, list]:
    zone_to_channel = {}
    unknown_zones = []
    for sp in idf.idfobjects.get("SPACE", []):
        zone_name = str(getattr(sp, "Zone_Name", "") or getattr(sp, "Name", "")).strip()
        tag2 = _get_space_tag2(sp)
        from eSim_bem_utils.commercial_integration import classify_tag2  # local import, avoids top-level order issues
        fine = classify_tag2(tag2)
        agg = _FINE_TO_AGG.get(fine)
        if agg is None:
            unknown_zones.append(zone_name)
            continue
        # Canonical key = upper-cased, stripped. EnergyPlus writes zone/space names in
        # ReportDataDictionary.KeyValue in ALL-CAPS regardless of the IDF's own case
        # (e.g. IDF 'Basement_Corridor ZN' -> SQL 'BASEMENT_CORRIDOR ZN'). Building this
        # map in the IDF's mixed case caused a 100% join miss against the SQL side (every
        # KeyValue.map() -> NaN, dropna emptied the table) -- diagnosed job 1169671,
        # 2026-07-28. Upper-case is the canonical form here because that's what EnergyPlus
        # emits; the SQL-side KeyValue is normalized the same way in _write_channel_hourly_csv.
        zone_to_channel[zone_name.upper()] = agg
    return zone_to_channel, unknown_zones


def _write_channel_hourly_csv(sql_path: str, injected_idf_path: str, eplus_idd: str, out_csv: str) -> int:
    from eppy.modeleditor import IDF
    IDF.setiddname(eplus_idd)
    idf = IDF(injected_idf_path)
    zone_to_channel, unknown_zones = _build_zone_channel_map(idf)
    if unknown_zones:
        distinct = sorted(set(unknown_zones))
        print(f"  [channel_hourly] {len(distinct)} distinct Space/zone names did not classify to a "
              f"known channel (<=10 shown): {distinct[:10]}")

    conn = sqlite3.connect(sql_path)
    try:
        # 🔴 Defaut 6 (2026-07-31). Zone-level Output:Variables report ONE zone instance and do
        # NOT include Zones.Multiplier; the facility meters do. On the Tall tower the
        # multipliers are {1,4,7,8,9,10,28,70} and Sigma(zone vars) came to 25.4 % of the
        # matching meter. Worse, the mean multiplier differs BY CHANNEL (office F3-F11 x9,
        # residential F22-F29 x8, retail F1/F2 x1), so it is not a common mode that cancels in
        # shares -- it silently biased every per-channel share toward the low-multiplier
        # channels. The multiplier is applied here, at the only place that has the zone
        # identity, and the result is verified against the facility meters by
        # _check_channel_closure() (measured: 0.2541 before, 1.000000 after).
        zmul = pd.read_sql_query("SELECT ZoneName, Multiplier FROM Zones", conn)
        zmul["KEY"] = zmul["ZoneName"].astype(str).str.strip().str.upper()
        zone_multiplier = dict(zip(zmul["KEY"], zmul["Multiplier"].astype(float)))

        var_names = list(VAR_METRIC.keys())
        placeholders = ",".join("?" * len(var_names))
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, KeyValue, Name "
            "FROM ReportDataDictionary "
            f"WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name IN ({placeholders})",
            conn, params=var_names,
        )
        if meta.empty:
            raise RuntimeError("no matching Hourly Zone-variable rows in ReportDataDictionary")
        idx_list = meta["ReportDataDictionaryIndex"].tolist()
        idx_placeholders = ",".join("?" * len(idx_list))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS idx, rd.Value AS value, rd.TimeIndex AS t "
            "FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({idx_placeholders}) "
            "ORDER BY rd.TimeIndex ASC",
            conn, params=idx_list,
        )
    finally:
        conn.close()

    idx_meta = meta.set_index("ReportDataDictionaryIndex")[["KeyValue", "Name"]]
    df = data.join(idx_meta, on="idx")
    df["metric"] = df["Name"].map(VAR_METRIC)
    # Normalize the SQL-side join key the same way as zone_to_channel's keys (upper + strip)
    # -- EnergyPlus's ReportDataDictionary.KeyValue is ALL-CAPS regardless of the IDF's own
    # case, so a mixed-case join here silently produced 0 matches (100% NaN, dropna emptied
    # the table downstream) -- diagnosed job 1169671, 2026-07-28.
    df["channel"] = df["KeyValue"].astype(str).str.strip().str.upper().map(zone_to_channel)
    n_total = len(df)
    n_mapped = int(df["channel"].notna().sum())
    n_unmapped = n_total - n_mapped
    print(f"  [channel_hourly] mapped={n_mapped} unmapped={n_unmapped} (of {n_total} report rows)")
    if n_unmapped:
        distinct_unmapped = sorted(set(df.loc[df["channel"].isna(), "KeyValue"].astype(str)))
        print(f"  [channel_hourly] {len(distinct_unmapped)} distinct unmapped KeyValue strings "
              f"(<=10 shown, verbatim): {distinct_unmapped[:10]}")
    if n_mapped == 0:
        # Hard error: a 0-row channel_hourly.csv must never be written and silently counted as
        # "produced" (this is exactly how job 1169671 went unnoticed). A SMALL unmapped set is
        # expected and tolerated -- plenum Spaces carry no Tag-2 and no loads (4 such in Tall,
        # accepted-as-documented) -- but total non-mapping means the join key is broken again.
        raise RuntimeError(
            f"channel_hourly: 0 of {n_total} report rows mapped to a channel -- refusing to "
            f"write a 0-row channel_hourly.csv. Check zone_to_channel casing / Tag-2 census "
            f"(sample unmapped KeyValues: {sorted(set(df['KeyValue'].astype(str)))[:10]})"
        )
    df = df.dropna(subset=["channel", "metric"])
    # Defaut 6: scale each zone's series by its own Multiplier BEFORE summing into channels. A
    # zone missing from Zones (impossible in practice) defaults to 1.0 rather than dropping the
    # row -- under-reporting must never be the quiet outcome.
    df["mult"] = df["KeyValue"].astype(str).str.strip().str.upper().map(zone_multiplier).fillna(1.0)
    df["value"] = df["value"] * df["mult"]
    df["col"] = df["channel"] + "_" + df["metric"]

    pivot = df.pivot_table(index="t", columns="col", values="value", aggfunc="sum")
    pivot = pivot.reindex(sorted(pivot.index))

    channels = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]
    metrics = ["people", "lights", "equip", "gasequip", "syscool", "sysheat"]
    all_cols = [f"{c}_{m}" for c in channels for m in metrics]
    for c in all_cols:
        if c not in pivot.columns:
            pivot[c] = 0.0
    pivot = pivot[all_cols]
    pivot.to_csv(out_csv, index=False)
    return len(pivot)


def _check_channel_closure(outdir: str) -> dict:
    """Prove the Defaut-6 multiplier handling on every run instead of trusting it.

    Sigma over channels of the per-channel lights / electric-equipment / gas-equipment series
    must equal the matching facility meter, because the zone variables partition the meter once
    the multiplier is applied. Measured on the CLG cell: unmultiplied, 0.2541 of the meter;
    multiplied, residual 0.000000 %. This check is what makes that a fact of every run rather
    than of one spot-check.
    """
    hourly = pd.read_csv(os.path.join(outdir, "hourly_meters.csv"))
    chan = pd.read_csv(os.path.join(outdir, "channel_hourly.csv"))
    channels = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]
    report = {}
    for metric, meter in (("lights", "InteriorLights:Electricity"),
                          ("equip", "InteriorEquipment:Electricity"),
                          ("gasequip", "InteriorEquipment:NaturalGas")):
        chan_sum = float(sum(chan[f"{c}_{metric}"].sum() for c in channels))
        meter_sum = float(hourly[meter].sum()) if meter in hourly.columns else 0.0
        rel = 0.0 if meter_sum == 0.0 else abs(chan_sum - meter_sum) / abs(meter_sum)
        report[metric] = {
            "sum_channels_J": chan_sum, "facility_meter_J": meter_sum,
            "residual_rel": rel, "closed": bool(rel <= FUEL_CLOSURE_TOL), "meter": meter,
        }
    return report


SQL_EXTRACTION_METHOD = (
    "reimplemented locally in this driver, porting the query shape of "
    "Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py::get_hourly_meter_data "
    "(ReportData/ReportDataDictionary join, EnvironmentType=3, Hourly), restricted "
    "to the requested meters/variables and pivoted to one column per series/channel"
)


def _do_postprocess(sql_path: str, injected_idf_path: str, eplus_idd: str, outdir: str,
                     manifest: dict) -> tuple[int, int]:
    """Step 5 (SQL -> hourly_meters.csv + channel_hourly.csv), shared by the normal
    inject-simulate-postprocess path and --postprocess-only. Mutates manifest in place;
    returns (rows_hourly, rows_channel) so the caller can apply the same row-count gate."""
    manifest["OUTPUT_SCHEMA_HASH"] = OUTPUT_SCHEMA_HASH
    hourly_csv = os.path.join(outdir, "hourly_meters.csv")
    channel_csv = os.path.join(outdir, "channel_hourly.csv")
    dhw_csv = os.path.join(outdir, "dhw_hourly.csv")
    rows_hourly = rows_channel = rows_dhw = 0

    if os.path.isfile(sql_path):
        try:
            rows_hourly, closure = _write_hourly_meters_csv(sql_path, hourly_csv)
            manifest["fuel_closure"] = closure
            print(f"[postprocess] hourly_meters.csv: {rows_hourly} rows -> {hourly_csv}")
            for fuel in END_USE_METERS:
                r = closure[fuel]
                verdict = "OK" if r["closed"] else "FAIL"
                print(f"  [fuel-closure {verdict}] {fuel}: Sigma(end uses) = "
                      f"{r['sum_end_uses_J']:.6g} J, {fuel}:Facility = "
                      f"{r['facility_total_J']:.6g} J, residual = {r['residual_rel'] * 100:.4f} %")
                if not r["closed"]:
                    print(f"[FAIL] fuel closure ({fuel}): an end use is missing from "
                          f"REQUIRED_METERS, or a meter name is wrong for this EnergyPlus "
                          f"version and was zero-filled -- §6b-4 tripwire (Defaut 5).")
        except Exception as e:
            print(f"[FAIL] hourly_meters extraction raised: {e}")
            manifest["hourly_meters_exception"] = str(e)
        try:
            rows_dhw, unresolved = _write_dhw_hourly_csv(sql_path, injected_idf_path,
                                                         eplus_idd, dhw_csv)
            manifest["dhw_unresolved_equipment"] = unresolved
            print(f"[postprocess] dhw_hourly.csv: {rows_dhw} rows -> {dhw_csv}")
        except Exception as e:
            print(f"[FAIL] dhw_hourly extraction raised: {e}")
            manifest["dhw_hourly_exception"] = str(e)
        try:
            rows_channel = _write_channel_hourly_csv(sql_path, injected_idf_path, eplus_idd, channel_csv)
            print(f"[postprocess] channel_hourly.csv: {rows_channel} rows -> {channel_csv}")
        except Exception as e:
            print(f"[FAIL] channel_hourly extraction raised: {e}")
            manifest["channel_hourly_exception"] = str(e)
    else:
        print(f"[FAIL] eplusout.sql not found at {sql_path}")

    manifest["hourly_meters_csv"] = {
        "path": hourly_csv, "rows": rows_hourly,
        "md5": md5_file(hourly_csv) if os.path.isfile(hourly_csv) else None,
    }
    manifest["channel_hourly_csv"] = {
        "path": channel_csv, "rows": rows_channel,
        "md5": md5_file(channel_csv) if os.path.isfile(channel_csv) else None,
    }
    manifest["dhw_hourly_csv"] = {
        "path": dhw_csv, "rows": rows_dhw,
        "md5": md5_file(dhw_csv) if os.path.isfile(dhw_csv) else None,
    }
    manifest["channel_hourly_convention"] = (
        "per-zone Output:Variable values MULTIPLIED by Zones.Multiplier before channel "
        "aggregation (fixed 2026-07-31, Defaut 6). Sigma(channels) therefore closes against "
        "the matching facility meter -- verified per run by channel_closure. Files written "
        "BEFORE 2026-07-31 are UNMULTIPLIED and not comparable in magnitude."
    )
    if rows_hourly and rows_channel:
        try:
            cc = _check_channel_closure(outdir)
            manifest["channel_closure"] = cc
            for metric, r in cc.items():
                verdict = "OK" if r["closed"] else "FAIL"
                print(f"  [channel-closure {verdict}] {metric}: Sigma(channels) = "
                      f"{r['sum_channels_J']:.6g} J vs {r['meter']} = "
                      f"{r['facility_meter_J']:.6g} J, residual = {r['residual_rel'] * 100:.4f} %")
                if not r["closed"]:
                    print(f"[FAIL] channel closure ({metric}): per-channel attribution does not "
                          f"partition the facility meter -- Zones.Multiplier handling or the "
                          f"Tag-2 census is wrong (Defaut 6).")
        except Exception as e:
            print(f"[FAIL] channel closure check raised: {e}")
            manifest["channel_closure_exception"] = str(e)
    return rows_hourly, rows_channel


# ---------------------------------------------------------------------------
# Main -- one probe cell
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Run one 3J Leg-3 Step-8 §P probe cell.")
    ap.add_argument("--cell", type=int, required=True, help="index into the CELLS table (0-6)")
    ap.add_argument("--force-inj-hash", type=str, default=None,
                     help="P3(a) only: override INJ_HASH instead of computing md5(injector)[:8]")
    ap.add_argument("--postprocess-only", action="store_true",
                     help="Skip injection + EnergyPlus entirely; re-derive hourly_meters.csv "
                          "and channel_hourly.csv from the already-existing "
                          "<outdir>/run/eplusout.sql for this cell, and rewrite manifest.json. "
                          "Errors clearly if that sql file is absent. Lets a post-processing-only "
                          "fix (e.g. job 1169671) be applied to completed sims without re-simulating.")
    ap.add_argument("--engine", choices=["auto", "cluster", "local"], default="auto",
                     help="auto (default) = platform-detected: Windows -> local, else cluster. "
                          "cluster = original Singularity/scratch path, unchanged. local = direct "
                          "EnergyPlus.exe via eSim_bem_utils/config.py, local repo checkout paths.")
    ap.add_argument("--outroot", type=str, default=None,
                     help="override the probes root dir (default: PROBES_ROOT on cluster, "
                          "LOCAL_PROBES_ROOT locally).")
    ap.add_argument("--repo-root", type=str, default=None,
                     help="engine=local only: override the repo checkout root used to derive "
                          "IDF/EPW/STEP7_OUT/injector paths (default: auto-derived from this "
                          "script's own location).")
    ap.add_argument("--allow-stale-inputs", action="store_true",
                     help="Defaut-3 fix: explicit override for the STALE-INPUTS GUARD. Without "
                          "this flag, the driver refuses (exit 1) to write into an existing "
                          "outdir whose manifest.json carries a different INPUTS_HASH (md5 of "
                          "the Step-7 product CSVs this cell reads) than the current run -- "
                          "including a missing/legacy INPUTS_HASH, treated as unknown. Normal "
                          "simulate path: archives the stale outdir aside (_STALE_<timestamp>, "
                          "never deleted) and proceeds with a real re-simulation. "
                          "--postprocess-only: only unblocks a LEGACY (no-INPUTS_HASH) manifest, "
                          "adopted in place without archiving; a genuine mismatch is refused "
                          "regardless of this flag (postprocess-only cannot fix a real product "
                          "change -- it never re-simulates). Use only for a deliberate "
                          "re-simulation after a known Step-7 product fix.")
    args = ap.parse_args()

    # ---- 0. Resolve engine + paths (2026-07-28 LOCAL PORT). Cluster branch reproduces the
    # pre-port constants EXACTLY (same STEP7_OUT/IDF_SUPERTALL/EPW/INJECTOR_PY/PROBES_ROOT
    # values unless --outroot is explicitly passed) -- no behavioural change on Linux. ----
    engine = args.engine
    if engine == "auto":
        engine = "local" if sys.platform == "win32" else "cluster"
    if engine == "cluster":
        step7_out = STEP7_OUT
        idf_supertall = IDF_SUPERTALL
        epw = EPW
        injector_py = INJECTOR_PY
        probes_root = args.outroot if args.outroot else PROBES_ROOT
    elif args.repo_root:
        # Non-default checkout location -- rebuild every path from the given root.
        repo_root = args.repo_root
        step7_out = os.path.join(repo_root, "3J_docs_occ_nTemp", "Leg3_4-split", "Step7_docs",
                                  "outputs_step7")
        idf_supertall = os.path.join(
            repo_root, "3J_docs_occ_nTemp", "Leg2_2-split", "Step8_docs", "outputs_step8",
            "office_idfs_v242", "CAN_MTL",
            "SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf")
        epw = os.path.join(repo_root, "BEM_Setup", "WeatherFile",
                            "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw")
        injector_py = os.path.join(repo_root, "eSim_bem_utils", "commercial_integration.py")
        probes_root = args.outroot if args.outroot else LOCAL_PROBES_ROOT
    else:
        # Default local checkout -- the LOCAL_* constants derived at module import time.
        step7_out = LOCAL_STEP7_OUT
        idf_supertall = LOCAL_IDF_SUPERTALL
        epw = LOCAL_EPW
        injector_py = LOCAL_INJECTOR_PY
        probes_root = args.outroot if args.outroot else LOCAL_PROBES_ROOT
    cell_table = _build_cells(step7_out)
    print(f"[setup] engine={engine} (arg={args.engine}, sys.platform={sys.platform})")

    # INJ_HASH fingerprints the *injector* (commercial_integration.py) only, so a
    # post-processing-only change to THIS driver does not (and should not) invalidate the
    # simulation output path/campaign dir. But the provenance of the derived CSVs still has
    # to be traceable back to the exact driver code that produced them, so the driver's own
    # md5 is recorded separately in the manifest (see below).
    driver_md5 = md5_file(os.path.abspath(__file__))

    if not (0 <= args.cell < len(cell_table)):
        print(f"[FAIL] --cell {args.cell} out of range 0..{len(cell_table) - 1}")
        sys.exit(1)
    cell = cell_table[args.cell]
    tag = cell["tag"]

    # ---- 1. Injector fingerprint (the structural stale-output guard, §6b) ----
    if not os.path.isfile(injector_py):
        print(f"[FAIL] injector not found at {injector_py}")
        sys.exit(1)
    inj_hash = args.force_inj_hash if args.force_inj_hash else md5_file(injector_py)[:8]
    outdir = os.path.join(probes_root, f"campaign_{inj_hash}", tag)

    # ---- 1b. STALE-INPUTS GUARD (Defaut-3 fix) -- runs BEFORE any write into outdir,
    # identically for both engines. Must run before os.makedirs() below: makedirs is the
    # first of the four silent-overwrite sites named in the reference doc (:494-495 in the
    # pre-fix line numbering), and the guard has to see the pre-existing outdir/manifest
    # (if any) before it gets touched. ----
    inputs_hash, inputs_detail = _compute_inputs_hash(cell["channels"])
    _check_inputs_hash_guard(outdir, inputs_hash, inputs_detail,
                              args.allow_stale_inputs, args.postprocess_only)

    os.makedirs(outdir, exist_ok=True)
    print(f"[setup] cell={args.cell} tag={tag} INJ_HASH={inj_hash} INPUTS_HASH={inputs_hash}")
    print(f"[setup] outdir={outdir}")
    print(f"[setup] source IDF={idf_supertall}")

    eplus_idd = os.environ.get("EPLUS_IDD", "")
    if engine == "local" and (not eplus_idd or not os.path.isfile(eplus_idd)):
        # Local-only fallback: config.py already knows how to resolve + version-check the IDD
        # (config.py:88-124). Cluster keeps requiring the EPLUS_IDD env var exactly as before --
        # this branch is skipped entirely when engine == "cluster".
        try:
            from eSim_bem_utils.config import resolve_idd_path
            eplus_idd = resolve_idd_path()
            print(f"[setup] EPLUS_IDD not set; resolved locally via config.py -> {eplus_idd}")
        except Exception as e:
            print(f"[FAIL] local IDD resolution via config.py failed: {e}")
            sys.exit(1)
    if not eplus_idd or not os.path.isfile(eplus_idd):
        print(f"[FAIL] EPLUS_IDD not set or file missing: '{eplus_idd}'")
        sys.exit(1)
    # commercial_integration.py::_find_idd() reads the EPLUS_IDD env var directly (it has no
    # explicit-IDD parameter on inject_mixed_use); the local fallback above only resolved a
    # local variable, so export it too -- otherwise inject_mixed_use() raises FileNotFoundError
    # even though eplus_idd is valid here. No-op when the cluster/sbatch job already exported it.
    os.environ["EPLUS_IDD"] = eplus_idd

    # ---- --postprocess-only: re-derive the two CSVs + manifest, no injection, no EnergyPlus ----
    if args.postprocess_only:
        injected_idf_path = os.path.join(outdir, "injected.idf")
        run_dir = os.path.join(outdir, "run")
        sql_path = os.path.join(run_dir, "eplusout.sql")
        if not os.path.isfile(sql_path):
            print(f"[FAIL] --postprocess-only: eplusout.sql not found at {sql_path} "
                  f"-- nothing to re-derive from (this cell must have been simulated already)")
            sys.exit(1)
        if not os.path.isfile(injected_idf_path):
            print(f"[FAIL] --postprocess-only: injected.idf not found at {injected_idf_path} "
                  f"-- needed to rebuild the Space->channel map")
            sys.exit(1)

        manifest_path = os.path.join(outdir, "manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"[postprocess-only] loaded existing manifest: {manifest_path}")
        else:
            print(f"[postprocess-only] no existing manifest at {manifest_path}; starting fresh "
                  f"(channels_requested/inject_mixed_use_result will be absent)")
            manifest = {
                "cell_index": args.cell, "cell_tag": tag, "scenario_label": tag,
                "INJ_HASH": inj_hash, "outdir": outdir, "channels_requested": {},
            }
        manifest["driver_md5"] = driver_md5
        manifest["postprocess_only"] = True
        # Defaut-3 fix: record the CURRENT INPUTS_HASH. Reached this point only if the
        # guard above already found it identical to (or explicitly adopted over) whatever
        # was previously recorded, so this is always an accurate, non-lying value.
        manifest["INPUTS_HASH"] = inputs_hash
        manifest["INPUTS_HASH_DETAIL"] = inputs_detail
        manifest.update(_energyplus_provenance(engine))

        rows_hourly, rows_channel = _do_postprocess(sql_path, injected_idf_path, eplus_idd, outdir, manifest)
        manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["sql_extraction_method"] = SQL_EXTRACTION_METHOD
        _write_manifest(outdir, manifest)

        exit_rc = 0
        if rows_hourly != 8760:
            print(f"[FAIL] hourly_meters.csv row count = {rows_hourly}, expected 8760")
            exit_rc = 1
        if rows_channel != 8760:
            print(f"[FAIL] channel_hourly.csv row count = {rows_channel}, expected 8760")
            exit_rc = 1
        print(f"[done] cell={args.cell} tag={tag} postprocess-only exit={exit_rc}")
        sys.exit(exit_rc)

    try:
        from eppy.modeleditor import IDF
    except ImportError as e:
        print(f"[FAIL] eppy not importable: {e}")
        sys.exit(1)
    try:
        from eSim_bem_utils.commercial_integration import inject_mixed_use
    except ImportError as e:
        print(f"[FAIL] cannot import eSim_bem_utils.commercial_integration: {e}")
        sys.exit(1)

    IDF.setiddname(eplus_idd)

    manifest = {
        "cell_index": args.cell,
        "cell_tag": tag,
        "scenario_label": tag,
        "INJ_HASH": inj_hash,
        "INPUTS_HASH": inputs_hash,
        "INPUTS_HASH_DETAIL": inputs_detail,
        "driver_md5": driver_md5,
        "outdir": outdir,
        "channels_requested": {},
    }
    manifest.update(_energyplus_provenance(engine))
    for ch, cfg in cell["channels"].items():
        csv_path = cfg.get("csv", "")
        exists = bool(csv_path) and os.path.isfile(csv_path)
        manifest["channels_requested"][ch] = {
            "csv_path": csv_path,
            "csv_md5": md5_file(csv_path) if exists else None,
            "exists": exists,
            **{k: v for k, v in cfg.items() if k != "csv"},
        }

    # ---- 2. Inject ----
    injected_idf_path = os.path.join(outdir, "injected.idf")
    building_meta = {
        "building": "SuperTall", "city": "MTL", "cz": "Z6",
        "purpose": "P-probe", "cell_index": args.cell, "scenario_label": tag,
    }
    try:
        inj_result = inject_mixed_use(idf_supertall, injected_idf_path, cell["channels"],
                                       building_meta, verbose=True)
    except Exception as e:
        print(f"[FAIL] inject_mixed_use raised: {e}")
        manifest["inject_exception"] = str(e)
        _write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["inject_mixed_use_result"] = inj_result
    fallback = sorted(set(inj_result.get("fallback", [])))
    banner_lines = []
    if fallback:
        manifest["FALLBACK_LOUD"] = fallback
        for ch in fallback:
            line = f"!!! FALLBACK: {ch} reverted to NECB baseline !!!"
            print(line)
            banner_lines.append(line)
    manifest["banner_lines"] = banner_lines

    # ---- 3. Ensure outputs on the injected IDF (every path, no exceptions) ----
    try:
        idf = IDF(injected_idf_path)
        _ensure_output_objects(idf, verbose=True)
        idf.saveas(injected_idf_path)
    except Exception as e:
        print(f"[FAIL] ensure-outputs step raised: {e}")
        manifest["ensure_outputs_exception"] = str(e)
        _write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["injected_idf_md5"] = md5_file(injected_idf_path)

    # ---- 4. Simulate ----
    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    if engine == "cluster":
        # UNCHANGED cluster path: Singularity wrapper script, exactly as before this port.
        epwrap_dir = os.path.join(outdir, "epwrap")
        os.makedirs(epwrap_dir, exist_ok=True)
        wrapper_path = os.path.join(epwrap_dir, "energyplus")
        with open(wrapper_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"singularity exec --bind /speed-scratch --bind /nfs/speed-scratch {SIF} {SIF_EXE} \"$@\"\n")
        os.chmod(wrapper_path, 0o755)
        ep_cmd = [wrapper_path, "-w", epw, "-d", run_dir, injected_idf_path]
        print(f"[sim] launching EnergyPlus: wrapper={wrapper_path}")
    else:
        # Local: no Singularity, no wrapper -- call the resolved energyplus.exe directly.
        # config.py:12 already points ENERGYPLUS_DIR at the local v24.2 install and
        # config.py:88-124 (resolve_idd_path) refuses to start on a non-24.2 IDD; the EPLUS_IDD
        # resolved above already went through that same guard.
        from eSim_bem_utils.config import ENERGYPLUS_EXE
        if not os.path.isfile(ENERGYPLUS_EXE):
            print(f"[FAIL] local EnergyPlus executable not found: {ENERGYPLUS_EXE}")
            _write_manifest(outdir, manifest)
            sys.exit(1)
        ep_cmd = [ENERGYPLUS_EXE, "-w", epw, "-d", run_dir, injected_idf_path]
        print(f"[sim] launching EnergyPlus directly: exe={ENERGYPLUS_EXE}")
    print(f"[sim] args: -w {epw} -d {run_dir} {injected_idf_path}")
    proc = subprocess.run(ep_cmd)
    ep_rc = proc.returncode
    manifest["ep_return_code"] = ep_rc
    print(f"[sim] EnergyPlus return code = {ep_rc}")

    # ---- 5. Post-process ----
    sql_path = os.path.join(run_dir, "eplusout.sql")
    rows_hourly, rows_channel = _do_postprocess(sql_path, injected_idf_path, eplus_idd, outdir, manifest)
    manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["sql_extraction_method"] = SQL_EXTRACTION_METHOD

    _write_manifest(outdir, manifest)

    # ---- 7. Exit non-zero on EP failure or wrong row counts ----
    exit_rc = 0
    if ep_rc != 0:
        print(f"[FAIL] EnergyPlus exited nonzero ({ep_rc})")
        exit_rc = 1
    if rows_hourly != 8760:
        print(f"[FAIL] hourly_meters.csv row count = {rows_hourly}, expected 8760")
        exit_rc = 1
    if rows_channel != 8760:
        print(f"[FAIL] channel_hourly.csv row count = {rows_channel}, expected 8760")
        exit_rc = 1

    print(f"[done] cell={args.cell} tag={tag} exit={exit_rc}")
    sys.exit(exit_rc)


if __name__ == "__main__":
    main()
