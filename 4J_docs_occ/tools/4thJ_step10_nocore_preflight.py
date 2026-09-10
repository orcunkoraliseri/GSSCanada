"""4thJ_step10_nocore_preflight.py -- read-only preflight guard for Step 10 campaign C2 (no-core).

Written 2026-09-03 for IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md, box 4 (I-4). Re-homed 2026-09-03 under D-IMP-4: there is no Step 12; this guards
Step 10 campaign C2, gate series G10N.x, specified in Step10_docs/nocore/.

Asserts, per layout payload, that it is eligible for campaign C2 (no-core real stock):
  1. manifest["geometry_outcome"] is DWELLING_LAYOUT_EMITTED,
     DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT, or (widened by the author 2026-09-08 under
     an explicit re-pre-registration) DWELLING_LAYOUT_EMITTED_BEST_EFFORT /
     DWELLING_LAYOUT_EMITTED_BEST_EFFORT_IMPUTED_COUNT -- i.e. flats were actually drawn.
     A best-effort payload must also NAME what it waived, and may waive only C6/C10/C11.
  2. manifest["scheme"] == "nocore_equal_area"
  3. floors carry at least one zone (the drawn plate is the dwelling, D-EU ruling
     2026-09-08); a payload with zero zones is never eligible
  4. the sha256 of openubem/geometry/european_residential.py on disk equals a pinned
     no-core digest (D-IMP-2 / D-EU-84 / D-EU-87 dependency)
  5. the sha256 of openubem/geometry/european_nocore.py on disk equals its pinned digest

PINNED 2026-09-08 by the author (freeze condition 3 of prereg_step10_nocore_DRAFT.md).
Before that date both pins read TBD_by_owner and the guard failed by construction,
because no no-core engine build existed. TWO files are pinned, not one: the carry-in
put the accepted cutter in european_nocore.py and european_residential.py imports
cut_storey_nocore from it, so hashing only the caller would leave the cutter unpinned.

Never edit either pin to make a run pass; they are set by the author. Moving a pin is
never a repair -- if a digest no longer matches, the engine changed, and that is a fact
to record and rule on, not a value to update.

BASIS DECISION 2026-09-08 by the author (recorded in prereg_step10_nocore_DRAFT.md
and in impl/2026-09-08_openubem-layouts-reemitted-verified.md section 13). The two
assertions written on 2026-09-03 -- status == "direct" and check.verdict is not None --
named keys the emitted payload does not carry: measured 0 of 1211 Bologna files with a
"status" key and 0 with a "check" key. They were guesses made before any plate had been
cut. They are REPLACED, not relaxed: the author ruled that the campaign-C2 eligibility
verdict is geometry_outcome, and the admitting values are the two that mean "flats were
actually drawn here": DWELLING_LAYOUT_EMITTED (census dwelling count used as given) and
DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT (count imputed). Whether the count was imputed is
provenance and is reported, never gated.

FALLBACK_PENDING_LAYOUT payloads (scheme null, zero zones) are Arm F. They are EXCLUDED,
not FAILED: being ineligible is their correct state, and a layout probe must never
promote Arm F to Arm D. Any other geometry_outcome value is a FAIL.

partition_audit is REPORTED, NEVER GATED. On the Bologna population 980 of 1036 drawn
payloads carry passed=false, but the worst area error is 1.651e-04 (0.0165 %), median
1.416e-05, none above 2e-04. That is FINDING 258, carried as a declared limitation with
the payload pre-repair -- it is not an eligibility criterion and gating on it would
discard 980 sound buildings.

CHARACTERISATION CORRECTED 2026-09-08 (same day, later). The line above used to end
"...discard 980 sound buildings for a rounding residue", and that reason was WRONG --
the decision is unchanged, only its stated cause. Read
audit_european_floor_partition in european_residential.py: passed is false when ANY of
DWELLING_COUNT / INVALID_DWELLING / AREA_GAP / AREA_OVERLAP / OUTSIDE_FOOTPRINT /
AREA_CONSERVATION fires. AREA_CONSERVATION uses relative_area_tolerance = 0.01, so a
1.9e-05 area error clears it by a factor of ~500 and CANNOT be what failed. The three
topology checks use footprint_area * EUROPEAN_TOPOLOGY_TOLERANCE_FRACTION = 1e-9, so a
gap of ~1.9e-05 of the plate is ~19,000x that tolerance. FINDING 258 is a TOPOLOGY GAP
measured against a 1e-9 tolerance, not a rounding residue on the area.

We cannot say which of the three topology checks fired, because the emitted side-car
keeps only {passed, area_error_fraction} and drops the audit's own failures tuple and
its gap_area_m2 / overlap_area_m2 / outside_area_m2. Asked of OpenUBEM 2026-09-08.
This matters beyond bookkeeping: D-EU-111's best-effort tier is gated on that same
audit passing, so if the residue is still present at re-emission the tier admits only
the buildings that happen to be gap-free.

No EnergyPlus is invoked, no network call is made, no cluster job is submitted. This
script only reads manifests already on disk and hashes one file already on disk.

Usage:
  C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe 4thJ_step10_nocore_preflight.py \
      --manifests <dir of *.json> [--engine <path to european_residential.py>]
"""
import argparse
import hashlib
import json
import os
import sys

# Pinned 2026-09-08 by the author. NEVER moved to make a run pass -- see the module docstring.
#
# PIN 2, authorised by the author 2026-09-08 ("lets go. i give confirmation"),
# in reply to a report that the engine had advanced and been committed.
#   european_residential.py
#     sha256 6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3
#     149,238 bytes, commit fda7f067 "feat(eu): implement 95% recut dwelling
#     schemes, delta merge harvest, and Wall-B second pass validation"
#     (2026-09-08 14:34 -0400), working tree clean under
#     openubem/geometry/ at the moment of measurement.
#   LINE-ENDING CONVENTION: CRLF, i.e. the bytes AS CHECKED OUT on this
#     machine. `git show <commit>:<path> | sha256sum` gives the LF blob and
#     will NOT reproduce this value. Every future pin records the convention.
#   Reproducible from our own repo at
#     Step10_docs/impl/engine_pin_20260908b/european_residential.py
#
# SUPERSEDED, kept for the record, NOT deleted:
#   PIN 1, 2026-09-08, european_residential.py commit 4431f2fe,
#     sha256 8e1dcda193bd2e68165ec7267c637e9fdf5abb0d3a0be464c6eb4cdb1db4d2d5
#     (148,132 bytes; bytes at Step10_docs/impl/engine_pin_20260908/).
#   The move is authorised because the engine legitimately advanced and landed
#   as a commit -- NOT because a run was failing. No population was measured
#   against PIN 2 before it was authorised, and none is re-scored by it.
ENGINE_DIGEST_PIN = "6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3"
# european_nocore.py, 91,468 bytes, commit 4431f2fe, CRLF as checked out.
# UNCHANGED across PIN 1 and PIN 2 -- the cutter did not move.
NOCORE_DIGEST_PIN = "21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae"

DEFAULT_ENGINE_PATH = (
    r"C:\Users\o_iseri\Desktop\OpenUBEM\openubem\geometry\european_residential.py"
)


DEFAULT_NOCORE_PATH = os.path.join(
    os.path.dirname(DEFAULT_ENGINE_PATH), 'european_nocore.py'
)


def payload_paths(root):
    """Every *.json under root, at any depth. Districts differ: Bologna is flat, Madrid
    and London nest under relation/ and way/."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".json"):
                yield os.path.join(dirpath, name)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# Both drawn outcomes are eligible. Corrected 2026-09-08 the same day: the first cut of
# this guard named only the IMPUTED_COUNT variant because that is the only one Bologna
# emits, and it failed 1,099 sound Madrid buildings whose dwelling count came from the
# census and needed no imputation. The author's ruling is "flats were actually drawn
# here"; the imputation flag is PROVENANCE, an attribute, never an eligibility test.
ELIGIBLE_OUTCOMES = (
    "DWELLING_LAYOUT_EMITTED",
    "DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT",
    # WIDENED 2026-09-08 by the author, in their own words: "yes, accept the new
    # buildings". This is D-EU-111's best-effort tier, announced by openubem-6e before
    # the re-emission. It is a BASIS CHANGE to a frozen pre-registration and it was made
    # the only way that is allowed: an explicit re-pre-registration -- a new dated
    # section appended to prereg_step10_nocore_DRAFT.md and a NEW md5 sidecar, with the
    # superseded md5 8176327149c3d36e06c822264ee676e8 recorded beside it. It was NOT
    # made by quietly adding two strings to this tuple, which is the same act as moving
    # a pinned digest. See impl/2026-09-08_openubem-layouts-reemitted-verified.md 15.
    #
    # What the author accepted: a cut that fails ONLY the three shape checks C6/C10/C11
    # still has every dwelling drawn, so it satisfies the 2026-09-08 basis ("a building
    # is eligible when flats were actually drawn in it"). C1/C3/C4/C5, the partition
    # audit and the 12-per-floor density cap still refuse on OpenUBEM's side, and a
    # payload that claims best-effort while waiving anything else FAILS here.
    "DWELLING_LAYOUT_EMITTED_BEST_EFFORT",
    "DWELLING_LAYOUT_EMITTED_BEST_EFFORT_IMPUTED_COUNT",
)
# Admitted, but never silently mixed into the plain population: counted and REPORTED
# separately by main(), because a best-effort building carries a real FAIL verdict in its
# own checks block and any EUI drawn from it must be quotable as such.
BEST_EFFORT_OUTCOMES = (
    "DWELLING_LAYOUT_EMITTED_BEST_EFFORT",
    "DWELLING_LAYOUT_EMITTED_BEST_EFFORT_IMPUTED_COUNT",
)
# D-EU-111 waives these three SHAPE checks and no others. A payload flagged best-effort
# that lists anything else is a contract violation, not a building we admit.
BEST_EFFORT_WAIVABLE_CHECKS = frozenset(("C6", "C10", "C11"))
ARM_F_OUTCOME = "FALLBACK_PENDING_LAYOUT"
# Present ONLY in the Lyon payload, which was never re-emitted (2026-09-01, core era,
# ruled_grid_* schemes). Not eligible for campaign C2 and not Arm F either -- it is a
# core-era artefact. Lyon is a physical baseline, never a fold, never an occupancy run.
CORE_ERA_OUTCOME = "DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED"


def zone_count(manifest):
    n = 0
    for fl in manifest.get("floors") or []:
        n += len(fl.get("zones") or [])
    return n


def classify(manifest):
    """ELIGIBLE (Arm D candidate) / EXCLUDED (Arm F) / FAIL, per the 2026-09-08 basis."""
    outcome = manifest.get("geometry_outcome")
    if outcome == ARM_F_OUTCOME:
        if manifest.get("scheme") is None and zone_count(manifest) == 0:
            return "EXCLUDED", []
        return "FAIL", ["fallback payload with scheme=%r and %d zones (want null and 0)"
                        % (manifest.get("scheme"), zone_count(manifest))]
    if outcome == CORE_ERA_OUTCOME:
        return "FAIL", ["geometry_outcome=%r -- core-era payload, not campaign C2"
                        % (outcome,)]
    if outcome not in ELIGIBLE_OUTCOMES:
        return "FAIL", ["geometry_outcome=%r (want one of %s, or %s)"
                        % (outcome, "/".join(ELIGIBLE_OUTCOMES), ARM_F_OUTCOME)]
    problems = []
    scheme = manifest.get("scheme")
    if scheme != "nocore_equal_area":
        problems.append("scheme=%r (want nocore_equal_area)" % (scheme,))
    if zone_count(manifest) < 1:
        problems.append("zero zones on a drawn payload")
    if outcome in BEST_EFFORT_OUTCOMES:
        waived = manifest.get("best_effort_failed_checks")
        if not waived:
            problems.append("best-effort payload carries no best_effort_failed_checks "
                            "list -- what was waived must be stated on the payload")
        else:
            stray = sorted(set(waived) - BEST_EFFORT_WAIVABLE_CHECKS)
            if stray:
                problems.append("best-effort payload waives %s -- D-EU-111 waives only "
                                "C6/C10/C11" % (",".join(stray),))
    return ("FAIL" if problems else "ELIGIBLE"), problems


def check_manifest(manifest, engine_digest, nocore_digest=None):
    failures = []
    if engine_digest != ENGINE_DIGEST_PIN:
        failures.append(
            "engine sha256=%s != pinned %s" % (engine_digest, ENGINE_DIGEST_PIN)
        )
    if nocore_digest != NOCORE_DIGEST_PIN:
        failures.append(
            "nocore sha256=%s != pinned %s" % (nocore_digest, NOCORE_DIGEST_PIN)
        )
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", required=True, help="directory of *.json manifests")
    ap.add_argument("--engine", default=DEFAULT_ENGINE_PATH)
    ap.add_argument("--nocore", default=DEFAULT_NOCORE_PATH)
    args = ap.parse_args()

    for label, path in (("engine", args.engine), ("nocore", args.nocore)):
        if not os.path.isfile(path):
            print("REFUSE: %s file not found at %s" % (label, path))
            sys.exit(2)
    engine_digest = sha256_of(args.engine)
    nocore_digest = sha256_of(args.nocore)

    n_checked = 0
    n_eligible = 0
    n_best_effort = 0
    n_excluded = 0
    n_failed = 0
    n_audit_false = 0
    worst_err = 0.0
    digest_failures = check_manifest({}, engine_digest, nocore_digest)
    if digest_failures:
        print("REFUSE: %s" % ("; ".join(digest_failures),))
        sys.exit(1)
    # RECURSIVE by necessity, fixed 2026-09-08: Madrid and London nest their payloads
    # one level deeper (layouts/relation/, layouts/way/) while Bologna is flat. The
    # 2026-09-03 os.listdir walk saw ZERO files in the nested districts and exited 0 --
    # a preflight that inspected nothing reported success. See the checked==0 refusal
    # below; that silent pass is the reason it exists.
    for path in sorted(payload_paths(args.manifests)):
        name = os.path.relpath(path, args.manifests)
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        n_checked += 1
        verdict, problems = classify(manifest)
        if verdict == "ELIGIBLE":
            n_eligible += 1
            if manifest.get("geometry_outcome") in BEST_EFFORT_OUTCOMES:
                n_best_effort += 1
            audit = manifest.get("partition_audit") or {}
            if audit.get("passed") is False:
                n_audit_false += 1
                err = audit.get("area_error_fraction") or 0.0
                if err > worst_err:
                    worst_err = err
        elif verdict == "EXCLUDED":
            n_excluded += 1
        else:
            n_failed += 1
            print("FAIL %s: %s" % (name, "; ".join(problems)))

    if n_checked == 0:
        print("REFUSE: no *.json payload found under %s -- a preflight that inspected "
              "nothing is not a pass" % (args.manifests,))
        sys.exit(2)

    print("checked=%d eligible=%d excluded_armF=%d failed=%d" % (
        n_checked, n_eligible, n_excluded, n_failed))
    print("REPORTED NOT GATED: %d of %d eligible are D-EU-111 best-effort (shape checks "
          "C6/C10/C11 waived, real FAIL kept in their own checks block) -- admitted by "
          "the author 2026-09-08, never quoted as a clean cut" % (
          n_best_effort, n_eligible))
    print("REPORTED NOT GATED: partition_audit passed=false on %d of %d eligible, "
          "worst area_error_fraction=%.3e (FINDING 258, payload pre-repair)" % (
          n_audit_false, n_eligible, worst_err))
    print("engine_sha256=%s pin=%s nocore_sha256=%s pin=%s" % (
        engine_digest, ENGINE_DIGEST_PIN, nocore_digest, NOCORE_DIGEST_PIN))
    sys.exit(1 if n_failed else 0)


if __name__ == "__main__":
    main()
