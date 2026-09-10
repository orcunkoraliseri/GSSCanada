# -*- coding: utf-8 -*-
"""4J Step 10 --- CAMPAIGN `C2`, THE NO-CORE REAL-STOCK CAMPAIGN RUNNER.

Specification: `Step10_docs/4thJ_10_nocoreRealStock.md` (implementation) and
`Step10_docs/4thJ_10_nocoreRealStock_val.md` (gate series `G10N.x`, guards
`V10N.x`).  Pre-registration: `Step10_docs/prereg_step10_nocore_DRAFT.md`,
FROZEN, md5 `1bc21094b0e09e3ac4332fa2e80abf75` (`RE-PRE-REGISTRATION 1`,
superseding `8176327149c3d36e06c822264ee676e8`).

WHAT THIS IS
------------
The runner campaign `C2` did not have.  It reads the layout payloads OpenUBEM
emitted under the no-core rule, keeps the buildings the author's ruled basis
admits, gives every drawn flat its own independent series, builds one IDF per
(building, case, f), runs EnergyPlus, and writes a manifest carrying all fifteen
fields of the spec's section 5.

WHAT IT IS NOT
--------------
* It is **NOT** `tools/4thJ_step10_realstock_campaign.py`.  That file is campaign
  `C1`, the core-era campaign: 41 Lyon footprints x 5 f-levels, pinned to
  `prereg.md` `e4243e07...`, scored under `G10.x`, CLOSED and ARCHIVED.  `C1` is
  not re-opened, not re-scored, not reported, and not edited by this work.
* It **SCORES NOTHING**.  No `G10N.x` verdict is computed, written or implied
  here.  This tool produces cells and manifests; scoring is a separate act on a
  separate authorisation, and the first district to run is a SHAKEDOWN by the
  author's own sentence (see `R2`).
* It is **NOT** an accuracy claim.  Heating only (Zone Ideal Loads hourly), the
  same two-end-use model `FINDING 169` / `FINDING 171` measured, with no
  lighting, no appliances, no DHW and no cooling.
* It is **NOT** a national stock claim.  Three districts carry folds; the fourth
  (Lyon) is a physical baseline and is refused by construction (`R3`).

THE POPULATION, AND WHO DECIDED IT
----------------------------------
The author ruled the eligibility basis on 2026-09-08: a building enters `C2`
**when flats were actually drawn in it**, and the verdict field is the payload's
own `geometry_outcome`.  That ruling is implemented ONCE, in
`4thJ_step10_nocore_preflight.py`, and this runner IMPORTS it rather than
restating it.  Restating an admission rule in a second file is how two files
come to admit two different populations under one campaign name.

The author also ruled, in the viewer, that **the drawn plate IS the dwelling**:
the smallest unit the floor plate is divided into is the emitted zone.  That
ruling stands.  How this file COUNTED those plates was wrong, and was corrected
on 2026-09-09 on the author's ruling.

    SUPERSEDED 2026-09-09:
        N_u  :=  sum over floors of len(floor["zones"])       <- PAYLOAD ROWS
    IN FORCE (amendment
    `Step10_docs/prereg_step10_nocore_AMENDMENT_2026-09-09_population.md`):
        N_u  :=  number of DISTINCT zone names in the payload  <- what gates read
              ==  `dwellings_total`, the emitter's authoritative field

A zone that spans n storeys is written out ONCE PER STOREY ROW, byte-identical,
so a viewer can draw every floor (`scripts/emit_eu11_layout_sidecars.py:364-369`);
upstream's `FINDING 201` invariant is one zone per dwelling, extruded over the
group's full height, never one zone per storey.  Summing the rows therefore
counted a tall flat once per floor: 27,352 registered against 26,095 real, 1,257
dwellings that do not exist (London 34% inflated).  Measured here over every
payload in all four districts: distinct zone names == `dwellings_total` on
2,926 of 2,926 buildings, zero mismatches, none missing.

Still NEVER `units_per_floor x storeys`.  `units_per_floor` is the MAXIMUM
per-storey count, not a constant; multiplying it by the storey count is not a
population.  `dwellings_total` was PROVENANCE under the superseded rule and is
now the CHECKED basis (`R11`).  `k` remains provenance and is never gated
(`FINDING 246` / `FINDING 266`: the census cuts one `k` per building, the engine
re-derives `k` per storey, and the two legitimately disagree) --- that finding is
about `k` per storey, not about the building total.

TEN PREFLIGHT REFUSALS, none downgradeable
------------------------------------------
  R1   the frozen pre-registration's md5 is not the one on the sidecar
  R2   the district is not authorised by the author's own `D-EU-55` sentence
  R3   the district is France (Lyon) --- never a fold, never an occupancy run
  R4   either engine digest differs from its pin
  R5   any payload classifies FAIL under the ruled basis
  R6   EnergyPlus is not 23.1, MEASURED from the binary (`FINDING 187`),
       or its IDD is missing / from a different install than the binary
  R7   the cell list is not paired, not unique, or not deterministically ordered
  R8   a scored run was requested --- this tool scores nothing
  R9   a pinned EPW is missing, or the fold has no pinned EPW
  R10  the payload set's digest is not the one the caller expected
  --- reporting, added by the 2026-09-09 reporting amendment (additive; no
      refusal was relaxed and no manifest field changed) ---
  A cell that does NOT complete now writes `cells_failed/<slug>.json` carrying
  `"record_kind": "FAILURE_NOT_A_RESULT"`, and every finished cell appends one
  flushed line to `campaign_progress.jsonl` with `campaign_status.json` rewritten
  every PROGRESS_EVERY cells.  Before this, a failing cell wrote NOTHING and
  `campaign_results.json` appeared only after the last of 35,290 cells.
  🔴 Failure records never enter `cells/`, which is the manifest population.

  R11  the drawn dwellings do not equal the payload's own `dwellings_total`,
       or one zone name carries two DIFFERENT geometries (added by the
       2026-09-09 population amendment; additive, nothing was relaxed)

🔴 NEVER move `ENGINE_DIGEST_PIN` or `NOCORE_DIGEST_PIN` to make a run pass, and
never rewrite a guard's field names so a population passes --- that is the same
act.  Both pins live in the preflight module and are read from there.

Usage:
    python 4thJ_step10_nocore_campaign.py --district IT-BOL-GALVANI2 --dry-run
    python 4thJ_step10_nocore_campaign.py --district IT-BOL-GALVANI2 --shakedown --workers 6
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import importlib.util
import json
import os
import platform as platform_mod
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOURJ = HERE.parent
OPENUBEM_ROOT = Path(os.environ.get("OPENUBEM_ROOT", r"C:/Users/o_iseri/Desktop/OpenUBEM"))
if str(OPENUBEM_ROOT) not in sys.path:
    sys.path.insert(0, str(OPENUBEM_ROOT))

# --- the frozen pre-registration.  NOT `C1`'s `prereg.md`. -------------------
PREREG = FOURJ / "Step10_docs/prereg_step10_nocore_DRAFT.md"
PREREG_MD5_SIDECAR = FOURJ / "Step10_docs/prereg_step10_nocore_DRAFT.md.md5"
#: `RE-PRE-REGISTRATION 4`, 2026-09-08 --- defect 8, and the `R7` blind spot the
#: running campaigns exposed in their first eighty cells.  Every superseded value
#: is recorded beside it so a run against older text is refused BY NAME, not by
#: silence.
PREREG_MD5 = "e1f2822a800932ff099c15aed6be7ead"
PREREG_MD5_SUPERSEDED = {
    "7ce1c0417440798e0ca5d0b32a47d6c4":
        "RE-PRE-REGISTRATION 3, the text the two Speed campaigns and the local "
        "Bologna shakedown ran under before all three were STOPPED. It is "
        "superseded by RR4: the no-core emitter names every storey "
        "`F0_dwelling_0` when a building has one dwelling per floor, so 233 of "
        "1,100 Madrid buildings and 35 of 1,036 Bologna buildings emit distinct "
        "flats under ONE name and `zone_count_emitted` counts flats that cannot "
        "be told apart. The 22 manifests written under this value are EVIDENCE, "
        "never cells to be scored.",
    "8176327149c3d36e06c822264ee676e8":
        "the pre-RE-PRE-REGISTRATION-1 text, before the author admitted the two "
        "D-EU-111 best-effort outcomes",
    "1bc21094b0e09e3ac4332fa2e80abf75":
        "the RE-PRE-REGISTRATION-1 text, before the author's 2026-09-08 sentence "
        "\"lets go use bigger datasets\" replaced London's 451-of-706 DATED "
        "SNAPSHOT with the full 706 -- uk 439 -> 685 eligible, C2 population "
        "26,764 -> 27,352 Arm D zones",
    "055331f285426a9928ca8f124fab7cc3":
        "the RE-PRE-REGISTRATION-2 text, before the author's 2026-09-08 sentences "
        "\"finish all three cities ... use 32 cpu of all speed reserouces\" and "
        "\"all neighbourhoods done you can go until the end\" widened `D-EU-55` "
        "to Madrid, London and Bologna and moved the compute to Speed -- the "
        "population is UNCHANGED by that section",
    "ffe7eb39490b698d291e7332e89789fb":
        "RE-PRE-REGISTRATION 3 without its own RR3.9 correction -- it existed "
        "for minutes and NO RUN EVER CITED IT; the correction records that "
        "RR3.5's stage_4j.tar.gz digest names a tar built before RR3 existed",
    "0dde360489096662781450a75c092e1e":
        "RE-PRE-REGISTRATION 3 through RR3.10, before RR3.11 recorded the "
        "cell_id-slash-in-a-path defect, recorded that R5 refuses London on "
        "its own 12 rerouted payloads, and withdrew RR3.4's \"all three "
        "cities or none\" gloss -- no run ever cited it either",
    "b944706a79d1ebd4da78a309c184ef84":
        "RE-PRE-REGISTRATION 3 through RR3.12, before RR3.13 recorded DEFECT 6 "
        "-- the IDD resolving to eppy's bundled v8.0.0 with a WARNING and not "
        "an error -- and extended R6 to refuse an IDD that is missing or from "
        "a different install than the binary; no run ever cited it either",
    "32ec52baf058a3da08cb78ac9808152f":
        "RE-PRE-REGISTRATION 3 through RR3.14, before RR3.15 recorded DEFECT 7 "
        "-- the payload's `/` reaching the per-flat gain CSV FILE NAME, which "
        "put the file in a subdirectory the IDF could not find -- extended R7 "
        "to refuse gain-csv name collisions, and recorded that Madrid cells "
        "carry COMPLETED_WITH_UNSTABLE_MARKERS from a SIZING-period "
        "psychrometric warning, screen deliberately not narrowed; no run ever "
        "cited it either",
}

WEATHER_DIR = OPENUBEM_ROOT / "openubem/data/weather"
WEATHER_REGISTRY = WEATHER_DIR / "weather_registry.json"
LAYOUT_ROOT = OPENUBEM_ROOT / "openubem/outputs/3D"
ARCHETYPE_DIR = OPENUBEM_ROOT / "openubem/data/construction"

DEFAULT_OUT = FOURJ / "Step10_docs/outputs_step10_nocore"
DEFAULT_RUN_ROOT = Path(r"C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/step10_nocore")

#: 🔴 Amendment 2 (2026-09-09, reporting).  How often the at-a-glance status
#: file is rewritten during a run.  The per-cell JSONL line is written and
#: flushed for EVERY cell regardless; this only paces the summary.
PROGRESS_EVERY = 25
DEFAULT_EPLUS = Path(r"C:/EnergyPlusV23-1-0/energyplus.exe")

#: `D-S10-1` Option A --- the pinned majority calendar year per fold, carried
#: from `C1` unchanged (the weather basis is not what no-core changed).
FOLD_EPW = {
    "es": "es_madrid_2009_2010_y2010.epw",
    "uk": "uk_london_2014_2015_y2014.epw",
    "it": "it_bologna_2013_2014_y2014.epw",
}
#: 🔴 `fr` is ABSENT ON PURPOSE and its absence is load-bearing (`G10N.11`).
#: Adding an `fr` row here would make France a fold by typing.

DISTRICTS = {
    "ES-MAD-BERRUGUETE": {"city": "Madrid", "country": "ES", "fold": "es",
                          "archetypes": "tabula_archetypes_es.json"},
    "GB-LDN-STDUNSTANS": {"city": "London", "country": "GB", "fold": "uk",
                          "archetypes": "tabula_archetypes_gb.json"},
    "IT-BOL-GALVANI2":   {"city": "Bologna", "country": "IT", "fold": "it",
                          "archetypes": "tabula_archetypes_it.json"},
    # 🔴 Lyon carries NO fold.  `R3` refuses it before anything else is read.
    "FR-LYO-HAUTCOEURPENTES": {"city": "Lyon", "country": "FR", "fold": None,
                               "archetypes": "tabula_archetypes_fr.json"},
}

# ---------------------------------------------------------------------------
# `D-EU-55` --- the author's own sentence is the authorisation, and it is
# QUOTED here rather than summarised.  A district absent from this table cannot
# run, and the refusal names exactly what would be needed to change that: a
# SECOND sentence from the author, not an edit to this file by whoever is at the
# keyboard.
# ---------------------------------------------------------------------------
AUTHORISED = {
    # ---------------------------------------------------------------- 1 ----
    # 🔴 Bologna now carries THREE sentences, not one.  `SENTENCE 1` opened it
    # as a shakedown; `SENTENCE 2` ("all three cities") and `SENTENCE 3` ("all
    # neighbourhoods ... go until the end") widened it into the campaign.  The
    # first is kept verbatim and is NOT superseded, because the local Windows
    # run launched at 21:29:52 loaded `AUTHORISED` before this edit existed:
    # every manifest it writes says `shakedown`, which is exactly what it is,
    # and it is never pooled with the Speed campaign.
    "IT-BOL-GALVANI2": {
        "mode": 'campaign',
        "scores": False,
        "sentence": (
            'I authorise EnergyPlus to run on our side for the no-core '
            'work, starting with Bologna only as a shakedown that scores '
            'nothing. || you choose as you reccommend also finish all three '
            'cities, not important order, for any computation simulation use '
            '32 cpu of all speed reserouces, lets go || all neighbourhoods '
            'done you can go until the end thank you'),
        "date": '2026-09-08',
    },
    # ---------------------------------------------------------------- 2 ----
    # 🔴 `SENTENCE 2` AND `SENTENCE 3`, 2026-09-08, the author's own words,
    # quoted and not summarised.  Together they name the DISTRICTS ("all three
    # cities", "all neighbourhoods"), name the ACT ("any computation
    # simulation", "go until the end") and name the RESOURCE ("32 cpu of all
    # speed reserouces").  That is what `D-EU-55` asks for and "lets go use
    # bigger datasets" was refused for lacking.
    #
    # 🔴 WHAT THESE SENTENCES DO **NOT** DO --- three things, each load-bearing:
    #   * They do not make Lyon a district that runs.  "all neighbourhoods"
    #     cannot reach `FR-LYO-HAUTCOEURPENTES` because Lyon carries NO FOLD
    #     (`R3` fires before `R2` is even read) and because its eligible
    #     population is measured at ZERO.  Promoting it is the never-list.
    #   * They do not authorise a SCORED read.  `scores` stays False on all
    #     three and `R8` still refuses `--scored`.  The cells this produces are
    #     byte-for-byte what a scored campaign would produce --- scoring is a
    #     DOWNSTREAM READ of them, so nothing is lost by waiting for the
    #     sentence and everything is lost by inventing it here.
    #   * They do not license mixing engines.  See `PLATFORM COHERENCE` below.
    "ES-MAD-BERRUGUETE": {
        "mode": 'campaign',
        "scores": False,
        "sentence": (
            'you choose as you reccommend also finish all three cities, not '
            'important order, for any computation simulation use 32 cpu of '
            'all speed reserouces, lets go || all neighbourhoods done you '
            'can go until the end thank you'),
        "date": '2026-09-08',
    },
    "GB-LDN-STDUNSTANS": {
        "mode": 'campaign',
        "scores": False,
        "sentence": (
            'you choose as you reccommend also finish all three cities, not '
            'important order, for any computation simulation use 32 cpu of '
            'all speed reserouces, lets go || all neighbourhoods done you '
            'can go until the end thank you'),
        "date": '2026-09-08',
    },
}

# ---------------------------------------------------------------------------
# 🔴 PLATFORM COHERENCE --- the hazard `SENTENCE 2` creates by moving the
# compute.  "use 32 cpu of all speed reserouces" moves EnergyPlus from this
# Windows box to Linux compute nodes.  `REQUIRED_EP_VERSION` pins 23.1 and
# `energyplus_build_hash` is RECORDED, not pinned --- so a Linux 23.1 build
# passes every guard in this file while being a DIFFERENT BINARY.  A population
# whose Bologna cells came from Windows and whose Madrid/London cells came from
# Linux would confound district with engine build, and no gate downstream could
# see it.  The rule taken, written here so it cannot be lost:
#
#   ONE CAMPAIGN, ONE ENGINE BUILD.  Every cell that may ever be read together
#   is produced by the same `energyplus_build_hash`.  The Windows Bologna run
#   is a SHAKEDOWN under `SENTENCE 1` and is never pooled with the Speed
#   campaign; the Speed campaign runs ALL THREE cities or none.
#
# 🔴 AND THE OBVIOUS CHECK DOES NOT WORK --- measured, not assumed.
# `energyplus_build_hash()` reads the sha EnergyPlus prints beside its version,
# and that sha is the SOURCE COMMIT of release 23.1.0: it is `87ed9199d4` on
# the Windows build on this box AND on every official Linux build of the same
# release.  So the field that looks like it separates the two engines DOES NOT.
# The only manifest field that does is `platform` (`platform_mod.platform()`).
# Anyone auditing engine coherence must read `platform`, not the build hash.
# ---------------------------------------------------------------------------
F_LEVELS = (0.00, 0.15, 0.30, 0.50, 1.00)
EXPECTED_CASES = ("A", "B")
CHAINING_RULE = "independent"       # decision 14, carried verbatim
SEED_BASE = 1                       # decision 14, carried verbatim
REQUIRED_EP_VERSION = "23.1"
J_TO_KWH = 1.0 / 3.6e6
RETAIN_RUN_DIRS = 4                 # the Step 8 / 10.4 precedent
ARM_D_SOURCE = "EUROPEAN_DWELLING_LAYOUT"
ARM_F_SOURCE = "FALLBACK_ONE_ZONE_PER_FLOOR"

#: A diverging heat balance EnergyPlus still calls a success.  Screened here
#: because no gate downstream of this file can see it.
UNSTABLE_MARKERS = (
    "Temperature out of range",
    "CalcHeatBalanceInsideSurf",
    "Inside surface heat balance did not converge",
    "Zone Air Heat Balance did not converge",
)

#: The fifteen fields of `4thJ_10_nocoreRealStock.md` section 5.  `G10N.14`
#: scores 0 blank fields against exactly this list; it is written once, here,
#: and the manifest writer is checked against it before the file is closed.
MANIFEST_FIELDS_S5 = (
    "weather_sha256", "energyplus_build_hash", "energyplus_version",
    "openubem_version", "openubem_git_commit", "platform",
    "rotated_to_midnight", "diary_origin_hour", "completed",
    "completion_status", "scheme", "status", "k", "observed_dwellings",
    "dwelling_deficit",
)


class Refusal(RuntimeError):
    """A named preflight refusal.  None of these is downgradeable to a warning."""


# ---------------------------------------------------------------------------
# digests
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def energyplus_version(exe: Path) -> str:
    """MEASURED from the binary, never the literal in a config (`FINDING 187`)."""
    out = subprocess.run([str(exe), "--version"], capture_output=True, text=True,
                         timeout=60)
    text = (out.stdout or "") + (out.stderr or "")
    match = re.search(r"(\d+\.\d+\.\d+)", text)
    if not match:
        raise Refusal("R6 EnergyPlus did not report a version: %r" % text[:200])
    return match.group(1)


#: 🔴 `FILESYSTEM SLUG` --- Madrid and London building ids are `relation/<n>` and
#: `way/<n>`, Bologna's are bare numbers.  The `/` is part of the identity and
#: MUST stay in `cell_id`; it must never reach a path, where it silently becomes
#: a directory level and the `.idf` write fails on a parent that was never made.
#: SEEN: every Madrid cell died `HARNESS_ERROR` before this existed.  So the
#: identity is kept and a separate slug is derived for paths only, and `R7`
#: refuses if the mapping is ever not one-to-one.
def cell_slug(cell_id: str) -> str:
    return cell_id.replace("/", "-").replace("\\", "-")


def energyplus_build_hash(exe: Path) -> str:
    """The build sha EnergyPlus prints beside its version, when it prints one."""
    out = subprocess.run([str(exe), "--version"], capture_output=True, text=True,
                         timeout=60)
    text = (out.stdout or "") + (out.stderr or "")
    match = re.search(r"[0-9a-f]{7,40}", text)
    return match.group(0) if match else "not_reported_by_binary"


def openubem_commit() -> str:
    try:
        out = subprocess.run(["git", "-C", str(OPENUBEM_ROOT), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        return (out.stdout or "").strip() or "not_a_git_checkout"
    except Exception:
        return "git_unavailable"


def openubem_dirty() -> bool:
    """🔴 A dirty tree is RECORDED, not silently accepted.  `R4`'s digests are
    what actually bind; this is the human-readable fact beside them."""
    try:
        out = subprocess.run(["git", "-C", str(OPENUBEM_ROOT), "status", "--porcelain"],
                             capture_output=True, text=True, timeout=30)
        return bool((out.stdout or "").strip())
    except Exception:
        return True


# ---------------------------------------------------------------------------
# the ruled basis, imported rather than restated
# ---------------------------------------------------------------------------
def load_preflight_module():
    """The eligibility ruling lives in ONE file and this is it.

    🔴 Do not copy `classify()` in here "for convenience".  The basis is the
    author's, it was ruled once, and two implementations of one ruling is how a
    campaign quietly acquires two populations.
    """
    spec = importlib.util.spec_from_file_location(
        "s10nocore_preflight", str(HERE / "4thJ_step10_nocore_preflight.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_paired_module():
    """`10.9`'s pairing, imported rather than restated.

    `G10N.20` inherits `G10.20` verbatim: BOTH cases on the same footprint,
    archetype, weather, `f` and seed policy.  Reproducing the pairing here would
    make the simulated pair a different pair from the emitted one --- which is
    the defect the gate exists to catch, committed by the tool the gate reads.
    """
    spec = importlib.util.spec_from_file_location(
        "s10paired", str(HERE / "4thJ_step10_paired.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# payload -> rows
# ---------------------------------------------------------------------------
def shoelace_area(coords) -> float:
    """Polygon area from the payload's own vertices.

    `C1` had to ASSUME an equal per-zone split (`zone_areas_basis =
    assumed_equal`) and flagged it as exactly the case that turns `G10.13`'s
    area-weighted arm green for the wrong reason.  The no-core payload draws
    every flat, so the areas here are DECLARED and that weakness does not carry
    over.
    """
    n = len(coords)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) * 0.5


def zone_records(manifest):
    """Every drawn DWELLING, once, in payload order.  The drawn plate IS the
    dwelling --- but a dwelling is a ZONE, not a zone-row.

    🔴 BASIS CORRECTED 2026-09-09 (author's ruling; amendment
    `Step10_docs/prereg_step10_nocore_AMENDMENT_2026-09-09_population.md`).
    The superseded body returned one record per storey ROW, so a five-storey
    single-dwelling building came back as five flats.  It also read the ROW's
    `z_floor_m` as the zone's elevation whenever the zone omitted `z_floor` ---
    that fallback is what made byte-identical repeats look geometrically
    distinct and produced our retracted `FINDING 268`.

    The repeat is byte-identical (measured: 0 of 1,288 repeated names differ),
    so the FIRST occurrence is kept and the rest are the same flat seen again.
    A repeated name whose geometry actually DIFFERS is not a storey repeat --- it
    is the genuine two-flats-one-name fault, and it refuses here (`R11`) instead
    of being silently collapsed.
    """
    out, seen = [], {}
    for floor in manifest.get("floors") or []:
        storey = int(floor.get("storey_index", 0))
        z_floor = float(floor.get("z_floor_m", 0.0))
        for zone in floor.get("zones") or []:
            coords = [(float(x), float(y)) for x, y in zone["coords_m"]]
            rec = {
                "name": zone["name"],
                "coords_m": coords,
                # 🔴 The ZONE's own elevation.  The storey row's `z_floor_m`
                # is a last-resort fallback, never the dwelling's extent.
                "z_floor": float(zone.get("z_floor", z_floor)),
                "z_ceiling": float(zone.get("z_ceiling", z_floor + 3.0)),
                "storey_index": storey,
                "area_m2": shoelace_area(coords),
            }
            prev = seen.get(rec["name"])
            if prev is None:
                seen[rec["name"]] = rec
                out.append(rec)
                continue
            if (prev["coords_m"] != rec["coords_m"]
                    or prev["z_floor"] != rec["z_floor"]
                    or prev["z_ceiling"] != rec["z_ceiling"]):
                raise Refusal(
                    "R11 %s repeats zone name %r with DIFFERENT geometry "
                    "(z %.3f-%.3f vs %.3f-%.3f) -- two distinct flats under one "
                    "name is not a storey repeat; one flat's gain series would "
                    "overwrite the other's and the run would still succeed"
                    % (manifest.get("building_id"), rec["name"],
                       prev["z_floor"], prev["z_ceiling"],
                       rec["z_floor"], rec["z_ceiling"]))
    return out


def payload_rows(district: str, pre, expect_digest=None):
    """Read one district's payloads, classify each with the RULED basis, and
    return (rows, geometry, census, digest, report).

    Arm F payloads are EXCLUDED here, not carried as `zone_count = storeys`.
    🔴 A layout probe must never promote Arm F to Arm D, and the inverse also
    holds: this runner never manufactures storey zones for a building whose
    plate was never cut.  Arm F's lower-bound arm is a separate emission on a
    separate authorisation, and it is not this file's to invent.
    """
    root = LAYOUT_ROOT / ("eu_%s_data" % district) / "layouts"
    if not root.is_dir():
        raise Refusal("R5 no layouts directory for %s at %s" % (district, root))

    meta = DISTRICTS[district]
    paths = sorted(pre.payload_paths(str(root)))
    if not paths:
        raise Refusal("R5 no *.json payload under %s -- a campaign that read "
                      "nothing is not a campaign" % root)

    digest_lines = []
    rows, geometry, census = [], {}, {}
    dwellings_registered, zone_entries_total = 0, 0
    counts = {"ELIGIBLE": 0, "EXCLUDED": 0, "FAIL": 0}
    best_effort, audit_false, worst_err = 0, 0, 0.0
    failures = []

    for path in paths:
        rel = os.path.relpath(path, str(root)).replace("\\", "/")
        digest_lines.append("%s %s" % (sha256_file(Path(path)), rel))
        with open(path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        verdict, problems = pre.classify(manifest)
        counts[verdict] += 1
        if verdict == "FAIL":
            failures.append((rel, "; ".join(problems)))
            continue
        if verdict == "EXCLUDED":
            continue

        building_id = str(manifest["building_id"])
        zones = zone_records(manifest)
        if not zones:
            # classify() already refuses a zero-zone drawn payload; belt and braces.
            raise Refusal("R5 %s classified ELIGIBLE with zero zones" % rel)
        if manifest.get("geometry_outcome") in pre.BEST_EFFORT_OUTCOMES:
            best_effort += 1
        audit = manifest.get("partition_audit") or {}
        if audit.get("passed") is False:
            audit_false += 1
            worst_err = max(worst_err, float(audit.get("area_error_fraction") or 0.0))

        # `k` is the census's per-building quotient; it is PROVENANCE here and the
        # deficit is REPORTED, NEVER GATED (spec section 3.1).
        storeys = int(manifest.get("storeys") or len({z["storey_index"] for z in zones}))
        dwellings_total = manifest.get("dwellings_total")
        k = (max(1, round(float(dwellings_total) / storeys))
             if dwellings_total and storeys else None)
        n_u = len(zones)                 # DWELLINGS --- what the gates read
        n_entries = sum(len(fl.get("zones") or [])
                        for fl in manifest.get("floors") or [])

        # R11 --- the population is CHECKED against the emitter's own
        # authoritative field instead of merely reported beside it.  That is the
        # 2026-09-09 amendment's whole point: under the superseded rule the two
        # were allowed to disagree by construction, and across the three fold
        # districts they disagreed by 1,257 dwellings.
        if dwellings_total is not None and int(dwellings_total) != n_u:
            raise Refusal(
                "R11 %s draws %d distinct dwellings but declares "
                "dwellings_total=%s -- the emitter's authoritative count and the "
                "drawn plates disagree, and a population that two fields "
                "contradict is not a population"
                % (building_id, n_u, dwellings_total))

        rows.append({
            "building_id": building_id,
            "country": meta["country"],
            "zone_count": n_u,
            "zone_source": ARM_D_SOURCE,
            "layout_status": manifest["geometry_outcome"],
            "footprint_area_m2": float(manifest.get("gross_footprint_area_m2") or 0.0),
            "zone_areas_m2": [z["area_m2"] for z in zones],
            "zone_areas_basis": "declared",
        })
        geometry[building_id] = zones
        dwellings_registered += n_u
        zone_entries_total += n_entries
        census[building_id] = {
            "archetype_id": manifest.get("archetype_id"),
            "building_type": manifest.get("building_type"),
            "storeys": storeys,
            "scheme": manifest.get("scheme"),
            "geometry_outcome": manifest["geometry_outcome"],
            "best_effort": manifest.get("geometry_outcome") in pre.BEST_EFFORT_OUTCOMES,
            "best_effort_failed_checks": manifest.get("best_effort_failed_checks") or [],
            "dwellings_total": dwellings_total,       # provenance, never a check
            "k": k,                                    # provenance, never a check
            "dwelling_deficit": (None if dwellings_total is None
                                 else n_u - int(dwellings_total)),
            "zone_count_emitted": n_u,                 # DWELLINGS; what gates read
            # provenance only: the superseded rule's number, kept so a reader can
            # see how far the frozen 27,352 stood from the stock on disk.
            "zone_entries_in_payload": n_entries,
            "conditioned_floor_area_m2": manifest.get("conditioned_floor_area_m2"),
            "floor_to_floor_m": float(manifest.get("floor_to_floor_m") or 3.0),
            "crs": manifest.get("crs"),
            "partition_audit_passed": audit.get("passed"),
            "partition_audit_area_error_fraction": audit.get("area_error_fraction"),
        }

    if failures:
        raise Refusal(
            "R5 %d payload(s) classify FAIL under the ruled basis and a partial "
            "population is not a campaign; first three: %r"
            % (len(failures), failures[:3]))

    payload_digest = hashlib.sha256(
        "\n".join(digest_lines).encode("utf-8")).hexdigest()
    if expect_digest and expect_digest != payload_digest:
        raise Refusal(
            "R10 payload set digest %s != expected %s -- the emission on disk is "
            "not the one this run was authorised against. A campaign that spans "
            "two emissions is two campaigns."
            % (payload_digest, expect_digest))

    report = {
        "district": district,
        "payloads_seen": len(paths),
        "eligible": counts["ELIGIBLE"],
        "excluded_arm_f": counts["EXCLUDED"],
        "failed": counts["FAIL"],
        # REPORTED, NEVER GATED -- both of these.
        "best_effort_reported_not_gated": best_effort,
        "partition_audit_false_reported_not_gated": audit_false,
        "partition_audit_worst_area_error_fraction": worst_err,
        # The REGISTERED POPULATION under the 2026-09-09 amendment, and beside it
        # the superseded rule's number, so any reader can see the gap without
        # re-deriving it.  These two were 26,095 and 27,352 across es+uk+it on the
        # 2026-09-08 emission.
        "dwellings_registered": dwellings_registered,
        "payload_zone_entries_superseded_basis": zone_entries_total,
        "payload_set_sha256": payload_digest,
    }
    return rows, geometry, census, payload_digest, report


# ---------------------------------------------------------------------------
# the cell list
# ---------------------------------------------------------------------------
def build_cells(rows, census, fold, paired_mod):
    """One record per (building, case, f).  The pairing is `10.9`, imported."""
    by_fold, _by_name = paired_mod.A.step7_index()
    assignments, skipped = paired_mod.build_pairs(rows, by_fold, seed_base=SEED_BASE)
    if skipped:
        raise Refusal("R7 pairing skipped %d building(s) and this campaign refuses "
                      "a partial population: %r" % (len(skipped), skipped[:3]))

    grouped = {}
    for a in assignments:
        grouped.setdefault((a["building_id"], a["case"]), []).append(a)
    for units in grouped.values():
        units.sort(key=lambda u: u["unit_index"])

    cells = []
    for key in sorted(grouped):
        building_id, case = key
        units = grouped[key]
        crow = census[building_id]
        for f in F_LEVELS:
            cells.append({
                "cell_id": "%s__%s__case%s__f%03d"
                           % (fold, building_id, case, int(round(f * 100))),
                "cell_slug": cell_slug(
                    "%s__%s__case%s__f%03d"
                    % (fold, building_id, case, int(round(f * 100)))),
                "campaign": "C2",
                "building_id": building_id,
                "case": case,
                "fold": fold,
                # 🔴 Arm D only.  Arm F payloads never reached `rows`.
                "arm": "D",
                "zone_semantics": "dwelling",
                "sensitivity_f": f,
                # `N_u` is the number of INDEPENDENT diaries, never the zone count.
                "n_u": len({u["presence_md5"] for u in units}),
                "zone_count_emitted": crow["zone_count_emitted"],
                "units": units,
                "census": crow,
            })
    cells.sort(key=lambda c: c["cell_id"])
    return cells


# ---------------------------------------------------------------------------
# the ten refusals
# ---------------------------------------------------------------------------
def preflight(district: str, scored: bool, energyplus_exe: Path, expect_digest,
              pre, dry_run: bool):
    """Every refusal, in the order that fails cheapest first --- except `R3`,
    which is deliberately first because refusing France is a rule, not a cost."""
    meta = DISTRICTS.get(district)
    if meta is None:
        raise Refusal("R2 %r is not one of the four districts: %s"
                      % (district, ", ".join(sorted(DISTRICTS))))

    # R3 --- France is never a fold, never a diary, never an occupancy run.
    if meta["country"] == "FR" or meta["fold"] is None:
        raise Refusal(
            "R3 %s is the French baseline. `G10N.11` is not a threshold that can "
            "be met -- France carries no fold, no diary and no `f>0` cell, and "
            "Lyon is a physical baseline that can never host a Step 11 run. This "
            "refusal is not waivable by any authorisation." % district)

    # R2 --- the author's own D-EU-55 sentence.
    auth = AUTHORISED.get(district)
    if auth is None:
        raise Refusal(
            "R2 %s is NOT authorised. `D-EU-55` binds: no EnergyPlus without "
            "the author's own sentence. Three sentences are on record and they "
            "reach Madrid, London and Bologna only. Running %s needs a FURTHER "
            "sentence from the author, quoted in `AUTHORISED` beside the "
            "others. Editing this table without one is the same act as moving "
            "a pinned digest." % (district, district))
    if scored and not auth["scores"]:
        raise Refusal(
            "R8 the authorisation on record for %s is a %s that SCORES NOTHING "
            "(%s, %s). Reading this run as a scored `G10N.x` result needs a "
            "second sentence. This tool computes no verdict under any flag."
            % (district, auth["mode"], auth["date"], auth["sentence"]))

    # R1 --- the frozen pre-registration.
    if not PREREG.is_file():
        raise Refusal("R1 the frozen pre-registration is not on disk: %s" % PREREG)
    live = md5_file(PREREG)
    if live != PREREG_MD5:
        why = PREREG_MD5_SUPERSEDED.get(live)
        raise Refusal(
            "R1 pre-registration md5 %s != frozen %s%s"
            % (live, PREREG_MD5,
               (" -- that is %s; a run against superseded text is refused by "
                "name, and the way to change the frozen document is a new "
                "re-pre-registration, never an edit" % why) if why else ""))
    if PREREG_MD5_SIDECAR.is_file():
        recorded = PREREG_MD5_SIDECAR.read_text(encoding="utf-8").split()[0].strip()
        if recorded != PREREG_MD5:
            raise Refusal("R1 sidecar records md5 %s, this runner is pinned to %s"
                          % (recorded, PREREG_MD5))

    # R4 --- BOTH engine digests.  Read from the preflight module; never restated.
    engine_path = Path(os.environ.get("C2_ENGINE_PATH", pre.DEFAULT_ENGINE_PATH))
    nocore_path = Path(os.environ.get("C2_NOCORE_PATH", pre.DEFAULT_NOCORE_PATH))
    for label, path in (("engine", engine_path), ("nocore", nocore_path)):
        if not path.is_file():
            raise Refusal("R4 %s file not found at %s" % (label, path))
    engine_digest = sha256_file(engine_path)
    nocore_digest = sha256_file(nocore_path)
    digest_problems = pre.check_manifest({}, engine_digest, nocore_digest)
    if digest_problems:
        raise Refusal(
            "R4 %s -- the engine changed. That is a fact to record and rule on, "
            "never a pin to update." % "; ".join(digest_problems))

    # R9 --- the pinned EPW for this fold, and only this fold.
    fold = meta["fold"]
    if fold not in FOLD_EPW:
        raise Refusal("R9 fold %r has no pinned EPW" % fold)
    epw_path = WEATHER_DIR / FOLD_EPW[fold]
    if not epw_path.is_file():
        raise Refusal("R9 pinned EPW missing for fold %s: %s" % (fold, epw_path))

    # R6 --- EnergyPlus, measured.  Skipped on a dry run because a dry run
    # invokes no binary; the flag is recorded in the report so nobody reads a
    # dry-run preflight as a full one.
    version, build_hash = None, None
    if not dry_run:
        if not energyplus_exe.is_file():
            raise Refusal("R6 EnergyPlus not found at %s" % energyplus_exe)
        version = energyplus_version(energyplus_exe)
        if not version.startswith(REQUIRED_EP_VERSION):
            raise Refusal(
                "R6 EnergyPlus is %s; this campaign is pinned to %s. A "
                "23.1-labelled manifest written by another binary is "
                "unfalsifiable afterwards." % (version, REQUIRED_EP_VERSION))
        build_hash = energyplus_build_hash(energyplus_exe)

    # R6 continued --- 🔴 THE IDD MUST COME FROM THE SAME INSTALL AS THE BINARY.
    # `openubem.config` resolves the IDD from `ENERGYPLUS_PATH`, defaulting to
    # `C:\EnergyPlusV23-1-0`.  On any other machine that default is absent and
    # **eppy falls back to its own bundled IDD v8.0.0 with a WARNING, not an
    # error** -- and a v8 IDD shifts `BuildingSurface:Detailed`'s fields, so the
    # IDF is built against the wrong schema and every cell dies far from the
    # cause.  SEEN on Speed: 8 of 8 Madrid cells `HARNESS_ERROR` behind one
    # printed line.  A warning is not a gate, so this is one.
    from openubem.config import ENERGYPLUS_IDD_PATH
    idd = Path(str(ENERGYPLUS_IDD_PATH))
    if not idd.is_file():
        raise Refusal(
            "R6 the EnergyPlus IDD is not on disk at %s. eppy would fall back "
            "to its own bundled v8.0.0 IDD with only a warning. Set "
            "ENERGYPLUS_PATH (or OPENUBEM_ENERGYPLUS_IDD_PATH) to the install "
            "that owns %s." % (idd, energyplus_exe))
    if idd.parent.resolve() != energyplus_exe.parent.resolve():
        raise Refusal(
            "R6 the IDD and the binary come from DIFFERENT installs -- idd=%s "
            "binary=%s. One schema and one engine, or the IDF is built against "
            "a version that is not the one that runs it."
            % (idd, energyplus_exe))

    return {
        "district": district,
        "fold": fold,
        "authorisation": dict(auth),
        "prereg_md5": live,
        "engine_sha256": engine_digest,
        "engine_pin": pre.ENGINE_DIGEST_PIN,
        "nocore_sha256": nocore_digest,
        "nocore_pin": pre.NOCORE_DIGEST_PIN,
        "engine_path": str(engine_path),
        "nocore_path": str(nocore_path),
        "epw": FOLD_EPW[fold],
        "epw_path": str(epw_path),
        "weather_sha256": sha256_file(epw_path),
        "weather_registry_sha256": (sha256_file(WEATHER_REGISTRY)
                                    if WEATHER_REGISTRY.is_file() else None),
        "energyplus_version_measured": version,
        "energyplus_build_hash": build_hash,
        "energyplus_measured": not dry_run,
        "openubem_git_commit": openubem_commit(),
        "openubem_tree_dirty": openubem_dirty(),
        "platform": "%s %s %s" % (platform_mod.system(), platform_mod.release(),
                                  platform_mod.machine()),
        "expect_payload_digest": expect_digest,
    }


def preflight_cells(cells, geometry):
    """`R7` --- pairing, uniqueness, deterministic order, and one-to-one paths
    at BOTH levels (cell directory and per-flat gain csv).  `G10N.20`'s own
    clause, enforced BEFORE the campaign rather than scored after it."""
    if not cells:
        raise Refusal("R7 the cell list is empty; a campaign that runs nothing "
                      "is not a pass")
    order = [c["cell_id"] for c in cells]
    if order != sorted(order):
        raise Refusal("R7 run order is not deterministic")
    if len(set(order)) != len(order):
        raise Refusal("R7 cell ids are not unique")
    slugs = [c["cell_slug"] for c in cells]
    if len(set(slugs)) != len(slugs):
        # 🔴 Two identities collapsing onto one path would have one cell
        # overwrite the other's IDF and manifest with no error anywhere.
        dupe = sorted({x for x in slugs if slugs.count(x) > 1})[:3]
        raise Refusal(
            "R7 the filesystem slug is not one-to-one with the cell id -- %d "
            "ids collapse onto %d paths; first three collisions: %r. A path "
            "collision silently overwrites a finished cell."
            % (len(slugs), len(set(slugs)), dupe))
    # 🔴 The same one-to-one requirement, one level down: every drawn flat in a
    # building writes its own `<zone>_gain.csv` into one run directory, so two
    # zone names that slug to the same file name would have one flat's gain
    # series silently overwrite another's --- and EnergyPlus would run happily
    # on the survivor.  Checked here, before any cell is built.
    #
    # 🔴 DEFECT 8, and the blind spot was in THIS GUARD.  It compared
    # `len(set(slugged))` against `len(set(names))`, so two zones carrying the
    # SAME name were collapsed by `set(names)` on the left of the comparison as
    # well as the right, and the check passed itself.  It caught two DISTINCT
    # names that slug alike and was blind to the plainer fault: one name used
    # twice.  The comparison is now against `len(names)` -- the number of drawn
    # flats -- which is what "one file per flat" actually means.
    # ⚪ SEEN: `relation/12638102` carries FIVE geometrically distinct flats all
    # named `relation/12638102_F0_dwelling_0` (the storey index does not advance
    # when a building has one dwelling per floor).  Upstream's
    # `add_european_heating_controls` refused the second emission and the cell
    # died `HARNESS_ERROR`; had it not refused, five flats would have written one
    # gain csv in turn and EnergyPlus would have run the survivor happily.
    # 🔴 `zone_count_emitted` -- "what the gates read" -- counts flats that
    # cannot be told apart, so the population is not the one on record.  Which
    # buildings are EXCLUDED rather than FATAL is a basis change and therefore
    # the author's to pre-register, not this file's to assume.
    for cell in cells:
        names = [z["name"] for z in geometry.get(cell["building_id"], [])]
        slugged = [cell_slug(n) for n in names]
        if len(set(slugged)) != len(names):
            dupe = sorted({x for x in slugged if slugged.count(x) > 1})[:3]
            raise Refusal(
                "R7 building %s emits %d drawn flats under only %d distinct gain "
                "csv file names: %r. One flat's gain series would overwrite "
                "another's and the run would still succeed; zone_count_emitted "
                "counts flats that cannot be told apart."
                % (cell["building_id"], len(names), len(set(slugged)), dupe))
    cases = {c["case"] for c in cells}
    if cases != set(EXPECTED_CASES):
        raise Refusal("R7 cases present are %r, expected %r"
                      % (sorted(cases), list(EXPECTED_CASES)))
    per = {}
    for cell in cells:
        per.setdefault((cell["building_id"], cell["sensitivity_f"]), set()).add(cell["case"])
    unpaired = [k for k, v in per.items() if v != set(EXPECTED_CASES)]
    if unpaired:
        raise Refusal("R7 %d (building, f) pairs are missing a case: %r"
                      % (len(unpaired), unpaired[:3]))
    n_buildings = len({c["building_id"] for c in cells})
    expected = n_buildings * len(EXPECTED_CASES) * len(F_LEVELS)
    if len(cells) != expected:
        raise Refusal("R7 cell count is %d, expected %d buildings x %d cases x %d f"
                      % (len(cells), n_buildings, len(EXPECTED_CASES), len(F_LEVELS)))
    return {"n_buildings": n_buildings, "n_cells": len(cells)}


# ---------------------------------------------------------------------------
# geometry and IDF
# ---------------------------------------------------------------------------
def load_archetype(district: str, archetype_id: str) -> dict:
    """The district's OWN country archetype, named by the payload.

    🔴 This is one place `C2` is not `C1`. `C1` ran the Lyon census under FR
    TABULA and relabelled the folds; here each district carries its own national
    registry, because each district is its own real stock.
    """
    path = ARCHETYPE_DIR / DISTRICTS[district]["archetypes"]
    records = json.loads(path.read_text(encoding="utf-8"))["records"]
    for record in records:
        if record["archetype_id"] == archetype_id:
            return record
    raise Refusal("R5 archetype %r named by the payload is not in %s"
                  % (archetype_id, path.name))


def zones_for_cell(cell, geometry):
    """Zones taken FROM THE PAYLOAD, never re-derived.

    🔴 `C1` re-probed the layout engine to build its zones and had to argue at
    length that a successful probe must not promote a census-refused building.
    Here there is nothing to promote: the plate was cut by the engine that is
    pinned, and the flats it drew are the flats we simulate. Re-cutting them
    would simulate a different building from the one the population was measured
    on.
    """
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    out = []
    for record in geometry[cell["building_id"]]:
        polygon = orient(Polygon(record["coords_m"]), sign=1.0)
        out.append({
            "name": record["name"],
            "floor_polygon": polygon,
            "coords_m": list(polygon.exterior.coords)[:-1],
            "z_floor_m": record["z_floor"],
            "height_m": record["z_ceiling"] - record["z_floor"],
            "storey_index": record["storey_index"],
            "area_m2": record["area_m2"],
        })
    return out


def build_idf_for_cell(cell, record, zones, run_dir: Path, epw_path: Path, paired_mod):
    from geomeppy import IDF
    from eppy.modeleditor import IDDAlreadySetError
    from openubem.config import ENERGYPLUS_IDD_PATH
    from openubem.idf.european_controls import add_european_heating_controls
    from openubem.idf.european_physics import (add_european_internal_mass,
                                               add_nomass_construction)
    from openubem.idf.builder import write_zone_volumes
    from openubem.idf.surfaces import extrude_geometry
    from openubem.semantic.european_schedules import emit_step8_gain_schedule
    from scripts.run_eu_s2_campaign import (
        IDF_HEADER_TEMPLATE,
        SHADOW_CALCULATION_METHOD,
        SHADOW_CALCULATION_UPDATE_FREQUENCY_METHOD,
        SHADOW_CALCULATION_UPDATE_FREQUENCY_DAYS,
    )

    try:
        IDF.setiddname(str(ENERGYPLUS_IDD_PATH))
    except IDDAlreadySetError:
        pass

    with epw_path.open(encoding="utf-8", errors="replace") as stream:
        fields = stream.readline().strip().split(",")
    city = fields[1]
    latitude, longitude, time_zone, elevation = (float(v) for v in fields[6:10])

    run_dir.mkdir(parents=True, exist_ok=True)
    idf_path = run_dir / ("%s.idf" % cell["cell_slug"])
    idf_path.write_text(
        # 🔴 The three shadow fields are IMPORTED, never typed here.  They are
        # `D-EU-40 R7`'s own constants (`PolygonClipping` / `Periodic` / 1 day),
        # chosen upstream BEFORE any EnergyPlus run and reported, not tuned.
        # Typing a value here would be this file quietly holding a second
        # physics setting under one campaign name.
        IDF_HEADER_TEMPLATE.format(
            city=city, latitude=latitude, longitude=longitude,
            time_zone=time_zone, elevation=elevation,
            shadow_method=SHADOW_CALCULATION_METHOD,
            shadow_update_method=SHADOW_CALCULATION_UPDATE_FREQUENCY_METHOD,
            shadow_update_days=SHADOW_CALCULATION_UPDATE_FREQUENCY_DAYS),
        encoding="utf-8")
    idf = IDF(str(idf_path))
    extrude_geometry(idf, zones, [])
    write_zone_volumes(idf, zones)

    def construction(component):
        f_red = float(record["f_red_temp"])
        return add_nomass_construction(
            idf, "EU_%s" % component,
            float(record["u_%s_w_m2k" % component]) * f_red,
            float(record["delta_u_tb_w_m2k"]) * f_red)

    wall, roof, floor = construction("wall"), construction("roof"), construction("floor")
    for surface in idf.idfobjects["BUILDINGSURFACE:DETAILED"]:
        kind = str(surface.Surface_Type).upper()
        if kind == "WALL":
            surface.Construction_Name = wall
        elif kind in ("ROOF", "ROOFCEILING"):
            surface.Construction_Name = roof
        elif kind in ("FLOOR", "CEILING"):
            surface.Construction_Name = floor

    f = cell["sensitivity_f"]
    units = cell["units"]
    # 🔴 One drawn flat, one series. If the payload's zone count and the unit
    # list ever disagree the cell is REFUSED, not recycled -- a recycled series
    # is exactly the `G10N.20` collision the binding rule exists to catch.
    if len(zones) != len(units):
        raise Refusal("R7 %s has %d drawn zones and %d assigned series"
                      % (cell["building_id"], len(zones), len(units)))

    schedules = []
    for index, zone in enumerate(zones):
        unit = units[index]
        area = float(zone["floor_polygon"].area)
        add_european_internal_mass(idf, zone["name"], area,
                                   c_m_wh_m2k=float(record["c_m_wh_m2k"]))
        idf.newidfobject(
            "SIZING:ZONE", Zone_or_ZoneList_Name=zone["name"],
            Zone_Cooling_Design_Supply_Air_Temperature_Input_Method="SupplyAirTemperature",
            Zone_Cooling_Design_Supply_Air_Temperature=13.0,
            Zone_Heating_Design_Supply_Air_Temperature_Input_Method="SupplyAirTemperature",
            Zone_Heating_Design_Supply_Air_Temperature=50.0,
            Zone_Cooling_Design_Supply_Air_Humidity_Ratio=0.008,
            Zone_Heating_Design_Supply_Air_Humidity_Ratio=0.008,
        )
        names = add_european_heating_controls(idf, record, zone["name"])
        legacy = idf.getobject("OTHEREQUIPMENT", names["gains"])
        if legacy is not None:
            idf.removeidfobject(legacy)
        limits = idf.getobject("SCHEDULETYPELIMITS", "EU_Step8_AnyNumber_Wm2")
        if limits is not None:
            idf.removeidfobject(limits)
        presence = None
        if f > 0.0:
            presence = paired_mod.S.read_presence(unit["presence_path"])
        info = emit_step8_gain_schedule(
            idf,
            sensitivity_f=f,
            dwelling_zone=zone["name"],
            dwelling_id=zone["name"],
            # 🔴 The zone NAME keeps the payload's `relation/<n>` exactly --- it
            # is the identity and it goes into the IDF unchanged.  The CSV FILE
            # NAME must not: upstream writes the series to this path and puts
            # only `path.name` into `Schedule:File`, so a `/` here puts the file
            # in a subdirectory that the IDF then cannot find.  SEEN on Speed:
            # 18 severe `Schedule:File ... not found` and a fatal before the
            # simulation began, on every Madrid cell.
            emitted_csv_path=run_dir / ("%s_gain.csv" % cell_slug(zone["name"])),
            presence=presence,
            chaining_rule=CHAINING_RULE if f > 0.0 else None,
        )
        schedules.append({
            "zone": zone["name"], "unit_index": unit["unit_index"],
            "storey_index": zone["storey_index"],
            "presence_file": unit["presence_file"], "presence_md5": unit["presence_md5"],
            "seed": unit["seed"], "independent": unit["independent"],
            "gain_sha256": info["sha256"],
            "mean_phi_int_w_m2": info["mean_phi_int_w_m2"],
            "zone_area_m2": area,
        })

    # 🔴 PORTABLE SCHEDULE PATHS, carried from `C1`. `emit_step8_gain_schedule`
    # writes an ABSOLUTE Windows path into `Schedule:File`, which cannot resolve
    # on Speed. EnergyPlus resolves a bare file name against the run directory,
    # and the CSV already sits there -- so the SAME IDF BYTES are valid on both
    # platforms, which is the only way a platform arm compares platforms.
    for sched in idf.idfobjects["SCHEDULE:FILE"]:
        sched.File_Name = str(sched.File_Name).replace("\\", "/").rsplit("/", 1)[-1]

    idf.newidfobject("OUTPUT:VARIABLE", Key_Value="*",
                     Variable_Name="Zone Ideal Loads Zone Total Heating Energy",
                     Reporting_Frequency="Hourly")
    idf.saveas(str(idf_path))
    return idf_path, schedules


# ---------------------------------------------------------------------------
# run and extract
# ---------------------------------------------------------------------------
def parse_hourly_heating(csv_path: Path):
    """Read from the file EnergyPlus wrote, never from what we asked for."""
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("eplusout.csv has no header: %s" % csv_path)
        columns = [c for c in reader.fieldnames
                   if "zone ideal loads zone total heating energy" in c.casefold()
                   and "[j]" in c.casefold() and "(hourly)" in c.casefold()]
        if not columns:
            raise ValueError("eplusout.csv lacks the hourly heating variable: %s"
                             % csv_path)
        series = {c: [] for c in columns}
        for row in reader:
            for c in columns:
                series[c].append(float(row[c]))
    return columns, series


def percentile_linear(sorted_values, q):
    """The definition `10.9` already scored q99 with; carried unchanged."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (pos - low)


def cell_metrics(columns, series, areas):
    """`CF = P_peak,building / sum_z P_peak,zone` --- the one thing `C2` exists
    to measure, computed per cell and NEVER compared to a threshold here."""
    n = len(series[columns[0]]) if columns else 0
    building = [0.0] * n
    zone_peaks, zone_kwh = [], []
    for column in columns:
        values = series[column]
        for i, v in enumerate(values):
            building[i] += v
        zone_peaks.append(max(values) if values else 0.0)
        zone_kwh.append(sum(values) * J_TO_KWH)
    peak_building = max(building) if building else 0.0
    sum_zone_peaks = sum(zone_peaks)
    total_area = sum(areas) if areas else 0.0
    ordered = sorted(building)
    return {
        "n_hours": n,
        "n_zones": len(columns),
        "peak_building_j": peak_building,
        "sum_zone_peak_j": sum_zone_peaks,
        "cf": (peak_building / sum_zone_peaks) if sum_zone_peaks else None,
        "q99_building_j": percentile_linear(ordered, 0.99),
        "annual_kwh": sum(zone_kwh),
        "floor_area_m2": total_area,
        "eui_kwh_m2": (sum(zone_kwh) / total_area) if total_area else None,
    }


def write_failure_record(cell, args, base_manifest, result, started):
    """Leave a FILE behind for a cell that did not complete.

    🔴 Amendment 2, 2026-09-09 (`prereg_step10_nocore_AMENDMENT_2026-09-09b_reporting.md`).
    Until this existed, a failing cell wrote nothing at all: its status lived in
    the returned dict, in RAM, until `campaign_results.json` was written after
    the LAST of 35,290 cells.  `DEFECT 8` had to be reproduced on a second
    machine to be read at all.  That is the defect this closes, and it closes it
    by ADDING a file, not by changing what a passing cell writes.

    🔴 The record goes to `cells_failed/`, NEVER to `cells/`.  `cells/` is the
    manifest population --- `G10N.14` counts blank fields there --- and a failure
    that landed in it could be mistaken for a result.  A failure record carries
    `"record_kind": "FAILURE_NOT_A_RESULT"` for the same reason.
    """
    rec = dict(base_manifest)
    rec.update({
        "record_kind": "FAILURE_NOT_A_RESULT",
        "cell_id": cell["cell_id"],
        "cell_slug": cell["cell_slug"],
        "campaign": "C2",
        "building_id": cell["building_id"],
        "case": cell["case"],
        "arm": cell["arm"],
        "fold": cell["fold"],
        "sensitivity_f": cell["sensitivity_f"],
        "n_u": cell["n_u"],
        "zone_count_emitted": cell["zone_count_emitted"],
        "completed": False,
        "completion_status": result.get("completion_status"),
        "failure": {k: v for k, v in result.items() if k != "cell_id"},
        "wall_seconds": round(time.time() - started, 1),
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    out_path = Path(args.out) / "cells_failed" / ("%s.json" % cell["cell_slug"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return out_path


def run_cell(cell, args, geometry, paired_mod, energyplus_exe: Path, epw_path: Path,
             base_manifest: dict, keep: set):
    """Run one cell and, if it does not complete, leave a file saying so.

    🔴 Amendment 2 wrapper.  `run_cell_inner` is the 2026-09-08 body, unchanged
    in what it does on the success path: same manifest, same fields, same
    `cells/` destination, same return dict.  Nothing here can rescue a failing
    cell or soften its status --- it only makes the failure legible while the run
    is still going.  A failure while WRITING the record must never mask the
    failure being recorded, so it is caught and reported beside it.
    """
    started = time.time()
    result = run_cell_inner(cell, args, geometry, paired_mod, energyplus_exe,
                            epw_path, base_manifest, keep)
    if not result.get("completed") and result.get("completion_status") != "DRY_RUN":
        try:
            write_failure_record(cell, args, base_manifest, result, started)
            result["failure_record_written"] = True
        except Exception as exc:                                # noqa: BLE001
            result["failure_record_written"] = False
            result["failure_record_error"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def run_cell_inner(cell, args, geometry, paired_mod, energyplus_exe: Path, epw_path: Path,
                   base_manifest: dict, keep: set):
    run_dir = Path(args.run_root) / cell["cell_slug"]
    started = time.time()
    try:
        record = load_archetype(args.district, cell["census"]["archetype_id"])
        zones = zones_for_cell(cell, geometry)
        idf_path, schedules = build_idf_for_cell(cell, record, zones, run_dir,
                                                 epw_path, paired_mod)
        if args.dry_run:
            return {"cell_id": cell["cell_id"], "completion_status": "DRY_RUN",
                    "completed": False, "n_zones": len(zones)}
        # 🔴 `-x` runs ExpandObjects.  `add_european_heating_controls` writes
        # `HVACTemplate:Zone:IdealLoadsAirSystem`, which EnergyPlus REFUSES to read
        # directly ("HVACTemplate:* objects found ... not supported directly").
        # The flag set is the upstream campaign's own (`-w -x -r -d`), copied so
        # our cells and theirs are produced by one invocation, not two.
        # 🔴 `cwd=run_dir` with `-d .` is NOT cosmetic.  `-r` runs ReadVarsESO,
        # which writes `readvars.audit` into the PROCESS working directory and not
        # into `-d`.  With a shared cwd, parallel workers delete each other's audit
        # file and EnergyPlus dies with "the process cannot access the file because
        # it is being used by another process" -- SEEN, 3 of 4 cells, one building.
        # ⚪ A cell that fails this way is a HARNESS artefact, never a physics
        # result, and it is exactly the kind of failure a 4-cell smoke exists to
        # find before 10,360 are launched.  Flags and cwd copied from upstream.
        proc = subprocess.run(
            [str(energyplus_exe), "-w", str(epw_path), "-d", ".",
             "-x", "-r", str(idf_path)],
            cwd=str(run_dir), capture_output=True, text=True, timeout=args.timeout)
        err_path = run_dir / "eplusout.err"
        err_text = err_path.read_text(encoding="utf-8", errors="replace") \
            if err_path.is_file() else ""
        unstable = [m for m in UNSTABLE_MARKERS if m in err_text]
        csv_path = run_dir / "eplusout.csv"
        if proc.returncode != 0 or not csv_path.is_file():
            return {"cell_id": cell["cell_id"], "completion_status": "ENERGYPLUS_FAILED",
                    "completed": False, "returncode": proc.returncode,
                    "unstable_markers": unstable}
        columns, series = parse_hourly_heating(csv_path)
        metrics = cell_metrics(columns, series, [s["zone_area_m2"] for s in schedules])
        crow = cell["census"]
        manifest = dict(base_manifest)
        manifest.update({
            "cell_id": cell["cell_id"],
            # 🔴 recorded so the path a cell was written to can be checked
            # against the identity it claims, without re-deriving either.
            "cell_slug": cell["cell_slug"],
            "campaign": "C2",
            "building_id": cell["building_id"],
            "case": cell["case"],
            "arm": cell["arm"],
            "fold": cell["fold"],
            "sensitivity_f": cell["sensitivity_f"],
            "chaining_rule": CHAINING_RULE if cell["sensitivity_f"] > 0 else None,
            "n_u": cell["n_u"],
            "zone_count_emitted": cell["zone_count_emitted"],
            # --- the fifteen fields of section 5 ---------------------------
            "rotated_to_midnight": True,          # `D-S9-3`(a), written, never assumed
            "diary_origin_hour": 0,
            "completed": True,
            "completion_status": ("COMPLETED_WITH_UNSTABLE_MARKERS" if unstable
                                  else "COMPLETED"),
            "scheme": crow["scheme"],
            # 🔴 `status` is OURS. The payload carries no `status` key -- asserting
            # one on the payload is the 2026-09-03 defect the author's basis
            # ruling replaced. Here it records what OUR classification decided.
            "status": "ELIGIBLE_ARM_D",
            "k": crow["k"],
            "observed_dwellings": crow["dwellings_total"],
            "dwelling_deficit": crow["dwelling_deficit"],
            # ---------------------------------------------------------------
            "geometry_outcome": crow["geometry_outcome"],
            "best_effort": crow["best_effort"],
            "best_effort_failed_checks": crow["best_effort_failed_checks"],
            "partition_audit_passed": crow["partition_audit_passed"],
            "partition_audit_area_error_fraction":
                crow["partition_audit_area_error_fraction"],
            "unstable_markers": unstable,
            "schedules": schedules,
            "metrics": metrics,
            "wall_seconds": round(time.time() - started, 1),
        })
        missing = [f for f in MANIFEST_FIELDS_S5
                   if f not in manifest or manifest[f] is None]
        if missing:
            # `G10N.14` scores 0 blank fields. A manifest that would fail it is
            # not written -- the run is reported failed instead, so nobody is
            # ever asked to retrofit a field afterwards.
            return {"cell_id": cell["cell_id"], "completion_status": "MANIFEST_INCOMPLETE",
                    "completed": False, "missing_fields": missing}
        out_path = Path(args.out) / "cells" / ("%s.json" % cell["cell_slug"])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        if cell["building_id"] not in keep:
            for junk in run_dir.glob("*"):
                if junk.suffix in (".idf", ".csv", ".err", ".eso", ".mtr", ".audit"):
                    try:
                        junk.unlink()
                    except OSError:
                        pass
        return {"cell_id": cell["cell_id"], "completion_status": manifest["completion_status"],
                "completed": True, "cf": metrics["cf"], "n_zones": metrics["n_zones"]}
    except Exception as exc:                                    # noqa: BLE001
        return {"cell_id": cell["cell_id"], "completion_status": "HARNESS_ERROR",
                "completed": False, "error": "%s: %s" % (type(exc).__name__, exc),
                "traceback": traceback.format_exc()[-2000:]}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Step 10 campaign C2 (no-core) runner. Scores nothing.")
    ap.add_argument("--district", required=True, choices=sorted(DISTRICTS))
    ap.add_argument("--dry-run", action="store_true",
                    help="build cells and IDFs, invoke no binary")
    ap.add_argument("--shakedown", action="store_true",
                    help="run EnergyPlus under the authorisation on record")
    ap.add_argument("--scored", action="store_true",
                    help="refused by R8; present so the refusal is reachable")
    ap.add_argument("--expect-payload-digest", default=None)
    ap.add_argument("--energyplus", default=str(DEFAULT_EPLUS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--limit", type=int, default=0,
                    help="cap the cell count (a smoke run, never a population)")
    args = ap.parse_args()

    if not args.dry_run and not args.shakedown:
        print("REFUSE: pass --dry-run, or --shakedown to invoke EnergyPlus under "
              "the authorisation on record. There is no default that runs.")
        return 2

    pre = load_preflight_module()
    try:
        report = preflight(args.district, args.scored, Path(args.energyplus),
                           args.expect_payload_digest, pre, args.dry_run)
        rows, geometry, census, digest, population = payload_rows(
            args.district, pre, args.expect_payload_digest)
        paired_mod = load_paired_module()
        cells = build_cells(rows, census, report["fold"], paired_mod)
        shape = preflight_cells(cells, geometry)
    except Refusal as exc:
        print("REFUSE: %s" % exc)
        return 1

    report.update(population)
    report.update(shape)
    print("PREFLIGHT OK  district=%s fold=%s mode=%s scores=%s"
          % (args.district, report["fold"], report["authorisation"]["mode"],
             report["authorisation"]["scores"]))
    print("  population: %d payloads -> %d eligible / %d Arm F excluded / %d FAIL"
          % (population["payloads_seen"], population["eligible"],
             population["excluded_arm_f"], population["failed"]))
    print("  REPORTED NOT GATED: %d best-effort (C6/C10/C11 waived, never quoted "
          "as a clean cut)" % population["best_effort_reported_not_gated"])
    print("  REPORTED NOT GATED: partition_audit passed=false on %d, worst "
          "area_error_fraction=%.3e (FINDING 258)"
          % (population["partition_audit_false_reported_not_gated"],
             population["partition_audit_worst_area_error_fraction"]))
    print("  cells: %d buildings x %d cases x %d f = %d"
          % (shape["n_buildings"], len(EXPECTED_CASES), len(F_LEVELS),
             shape["n_cells"]))
    print("  dwellings registered: %d (superseded sum-over-floors rule would "
          "have registered %d)"
          % (population["dwellings_registered"],
             population["payload_zone_entries_superseded_basis"]))
    print("  payload_set_sha256=%s" % digest)
    print("  SCORES NOTHING: no G10N.x verdict is computed by this tool.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "preflight_report.json").write_text(json.dumps(report, indent=2),
                                               encoding="utf-8")

    todo = cells[:args.limit] if args.limit else cells
    keep = set(sorted({c["building_id"] for c in todo})[:RETAIN_RUN_DIRS])
    base_manifest = {
        "weather_sha256": report["weather_sha256"],
        "energyplus_build_hash": report["energyplus_build_hash"],
        "energyplus_version": report["energyplus_version_measured"],
        "openubem_version": report["engine_sha256"][:12],
        "openubem_git_commit": report["openubem_git_commit"],
        "platform": report["platform"],
        "engine_sha256": report["engine_sha256"],
        "nocore_sha256": report["nocore_sha256"],
        "prereg_md5": report["prereg_md5"],
        "payload_set_sha256": digest,
        "authorisation": report["authorisation"],
    }

    if args.dry_run and not args.limit:
        # Enumerated and paired, not built: building 10,360 IDFs to prove the
        # preflight holds would take longer than the refusals it is checking.
        # `--limit N --dry-run` DOES build, and that is the geometry smoke path.
        print("DRY RUN: %d cells enumerated, no IDF written, no binary invoked. "
              "Add --limit N to build N cells' IDFs without running EnergyPlus."
              % len(todo))
        return 0

    # 🔴 Amendment 2 (2026-09-09, reporting).  Two files are written DURING the
    # run so a campaign is readable before its last cell: an append-only JSONL
    # with one line per finished cell, flushed immediately, and a small status
    # summary rewritten every `PROGRESS_EVERY` cells.  The JSONL is APPENDED, not
    # truncated --- a second run adds a RUN_HEADER line and its own cells rather
    # than erasing the evidence of the first.  `campaign_results.json` is still
    # written at the end, unchanged, and remains the complete record.
    progress_path = out / "campaign_progress.jsonl"
    status_path = out / "campaign_status.json"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    counts = {}

    results = []
    with open(progress_path, "a", encoding="utf-8") as prog:
        prog.write(json.dumps({
            "record_kind": "RUN_HEADER",
            "started_at": started_at,
            "district": args.district,
            "cells_planned": len(todo),
            "payload_set_sha256": digest,
            "prereg_md5": report["prereg_md5"],
            "engine_sha256": report["engine_sha256"],
            "workers": args.workers,
        }) + "\n")
        prog.flush()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_cell, c, args, geometry, paired_mod,
                                   Path(args.energyplus), Path(report["epw_path"]),
                                   base_manifest, keep): c for c in todo}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                print("  %-52s %s" % (result["cell_id"], result["completion_status"]))
                status = result.get("completion_status")
                counts[status] = counts.get(status, 0) + 1
                # one line per cell, flushed --- this is the whole point: a
                # failure is on disk the moment it happens, not 35,290 cells later.
                prog.write(json.dumps(dict(result, record_kind="CELL",
                                           at=time.strftime("%Y-%m-%dT%H:%M:%S"))) + "\n")
                prog.flush()
                if len(results) % PROGRESS_EVERY == 0 or len(results) == len(todo):
                    status_path.write_text(json.dumps({
                        "record_kind": "RUN_STATUS",
                        "district": args.district,
                        "started_at": started_at,
                        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "cells_planned": len(todo),
                        "cells_finished": len(results),
                        "completed": sum(1 for r in results if r.get("completed")),
                        "by_completion_status": dict(sorted(counts.items())),
                        "payload_set_sha256": digest,
                        "note": ("in flight; campaign_results.json is written "
                                 "only when every cell has finished"),
                    }, indent=2), encoding="utf-8")

    results.sort(key=lambda r: r["cell_id"])
    (out / "campaign_results.json").write_text(json.dumps(results, indent=2),
                                               encoding="utf-8")
    done = sum(1 for r in results if r.get("completed"))
    failed = [r for r in results if not r.get("completed")
              and r.get("completion_status") != "DRY_RUN"]
    if failed:
        print("  %d cell(s) did not complete; one record each under %s"
              % (len(failed), out / "cells_failed"))
    print("  progress: %s (one line per cell, written as it finished)" % progress_path)
    print("DONE: %d of %d cells completed. SCORES NOTHING." % (done, len(results)))
    return 0 if done == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
