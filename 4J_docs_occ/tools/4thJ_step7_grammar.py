#!/usr/bin/env python
"""
4J Step 7, work item 7.1: the grammar, and the hand-written oracle `G7.10`
compares XGrammar against.

WHAT THIS IS
------------
Two things that must never be the same code:

  1. `build_alphabets(...)`  -- the constraint *definition*, read LIVE from the
     shipped Step 2 crosswalks. This is what a grammar back-end (XGrammar) is
     compiled from.
  2. `validate_record(...)`  -- a hand-written recogniser for the SAME language,
     written independently. `G7.10` requires the two accept/reject identically
     on 10,000 sampled strings including deliberately malformed ones. If the
     oracle imported the grammar's own accept function this gate would compare a
     thing to itself, which is the `V5.d` / `V6.b` failure class.

Record format, frozen 2026-08-17 and amended by D-S3-11, from `tools/encoder.py`:

    <6-field prefix>|DUR,ACT,ACT2,LOC,COP;DUR,ACT,ACT2,LOC,COP;...<eor>

No whitespace anywhere (V3.c). Episodes carry a TERMINAL semicolon and there is
no separator between consecutive episodes.

THREE THINGS THIS MODULE REFUSES TO DECIDE FOR YOU
--------------------------------------------------
* 🔴 `TransitionPolicy` has NO default. Pass it explicitly. See FINDING 45:
  28.95 % of the real corpus contains a direct `other_place -> at_home`
  transition with no travel episode between them, and the rate is
  COUNTRY-DEPENDENT (ES 43.18 %, UK 24.64 %, IT 23.63 %). A grammar that
  forbids it would mask nearly a third of the training distribution and would
  do so 1.8x harder on Spanish diaries than Italian ones. That is `D-S7-2`.
* 🔴 The ACT alphabet is the 158 shipped target codes UNION {"000"}. `000` is
  D-S3-9's null-activity code, it is in 8,709 corpus episodes, and it is NOT in
  `activity_target_list.csv`. See FINDING 43. Building the alphabet from that
  file alone silently forbids a code the corpus defines.
* This module never writes a schedule and never decides what a `000` episode
  contributes to one (D-S7-1 (c)).

NOTHING HERE HAS BEEN RUN AGAINST A GENERATED BATCH. No batch exists.
"""

import csv
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from encoder import load_bit_positions

DAY_MINUTES = 1440
SLOT_MINUTES = 10
N_TALLY_STATES = DAY_MINUTES // SLOT_MINUTES + 1  # 145: 0..144 inclusive

PREFIX_BODY_SEP = "|"
EPISODE_SEP = ";"
FIELD_SEP = ","
EOR = "<eor>"
N_PREFIX_FIELDS = 6          # D-S2-19 dropped `season`; D-S3-11 dropped `mode`, `scheme`
N_EPISODE_FIELDS = 5         # DUR, ACT, ACT2, LOC, COP

ACT_NULL_CODE = "000"        # D-S3-9. Deliberately admitted -- see FINDING 43.
COP_MIN, COP_MAX = 0, 64     # 64 == "not collected" (D-S3-5)

LOC_ALPHABET = ("at_home", "other_place", "private_transport", "public_transport", "unknown")
LOC_TRANSPORT = ("private_transport", "public_transport")


class GrammarError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Transition policy. Explicit, never defaulted. D-S7-2.
# ---------------------------------------------------------------------------
class TransitionPolicy(object):
    """`G7.3` says "no workplace-to-home with no travel episode".

    🔴 The serialised `LOC` CANNOT EXPRESS "workplace". Step 2 maps every
    non-home, non-transport place -- workplace, second home, shop, restaurant,
    someone else's house -- onto the single class `other_place`
    (`crosswalk_location.csv`). So the rule as written is not implementable as
    written, and the nearest implementable rule is strictly broader than the one
    that was specified.
    """

    #: Accept whatever the corpus accepts. The measured baseline.
    #: D-S7-2 RULED (a) by the author 2026-08-20: THIS IS THE OPERATIVE MODE.
    #: The travel requirement is NOT enforced; G7.3 becomes a reported rate.
    PERMISSIVE = "permissive"
    #: Forbid `other_place -> at_home` unless a transport episode intervenes.
    #: 🔴 This is the literal reading of `G7.3`, and it rejects 28.95 % of the
    #: real corpus. Refused unless `acknowledge_finding_45=True` is passed.
    REQUIRE_TRAVEL = "require_travel"

    ALL = (PERMISSIVE, REQUIRE_TRAVEL)


# Measured on `4J_step3_corpus.jsonl` (73,254 records) 2026-08-20 by grep over
# the shipped file. Counts are DIARIES CONTAINING AT LEAST ONE occurrence, not
# occurrences, because that is what a line-oriented grep can honestly report.
FINDING_45_MEASURED = {
    "all": (21210, 73254),
    "es": (8264, 19140),
    "uk": (3907, 15854),
    "it": (9039, 38260),
}


# ---------------------------------------------------------------------------
# Alphabets -- read LIVE from the shipped crosswalks, never hard-coded.
# ---------------------------------------------------------------------------
def _read_column(path, column):
    if not os.path.exists(path):
        raise GrammarError("crosswalk not found: %s" % path)
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        if column not in (rdr.fieldnames or []):
            raise GrammarError("%s has no column %r (has %s)" % (path, column, rdr.fieldnames))
        for row in rdr:
            v = (row[column] or "").strip()
            if v:
                out.append(v)
    if not out:
        raise GrammarError("%s yielded zero values for column %r" % (path, column))
    return out


def build_alphabets(step2_dir):
    """Returns the terminal alphabets the grammar is compiled from.

    🔴 `act` is 158 shipped codes UNION {"000"}. The union is declared here, in
    one place, with its reason, rather than being sprinkled through the grammar.
    """
    act = set(_read_column(os.path.join(step2_dir, "activity_target_list.csv"), "target_code"))
    if ACT_NULL_CODE in act:
        raise GrammarError(
            "activity_target_list.csv now contains %r. FINDING 43 assumed it did not; "
            "re-read that finding before changing this line." % ACT_NULL_CODE)
    n_shipped = len(act)
    act.add(ACT_NULL_CODE)

    act2 = set(_read_column(
        os.path.join(step2_dir, "crosswalk_activity_secondary.csv"), "target_code_2d"))

    outdoor = set(_read_column(os.path.join(step2_dir, "outdoor_at_home.csv"), "target_code"))

    bad = sorted(c for c in act if not (len(c) == 3 and c.isdigit()))
    if bad:
        raise GrammarError("non 3-digit ACT codes: %s" % bad)
    bad2 = sorted(c for c in act2 if not (len(c) == 2 and c.isdigit()))
    if bad2:
        raise GrammarError("non 2-digit ACT2 codes: %s" % bad2)
    if not outdoor <= act:
        raise GrammarError("outdoor_at_home codes not in the activity list: %s"
                           % sorted(outdoor - act))

    # -----------------------------------------------------------------------
    # `D-S7-5` OPTION (1), RULED 2026-08-22 BY THE AUTHOR AND APPLIED HERE.
    #
    # `COP` is a six-bit flag set. A person cannot be ALONE and simultaneously be
    # with someone: `cop_alone` set alongside any other flag is an episode that
    # contradicts itself, with no household knowledge required to see it.
    #
    # 🔴 Thirty-one patterns are removed, not thirty-two. Of the 32 values with the
    # `cop_alone` bit set, one -- the bit alone -- is legal and stays. The count was
    # written as 32 once; it is 31, and the discrepancy is recorded rather than
    # quietly corrected, because the number appears in a ruling.
    #
    # 🔴 `COP_MAX` (= 64, "not collected") is a SENTINEL, not a flag set, and is
    # never touched by this rule.
    #
    # VERIFIED before enforcing, against all 73,254 diaries / 2,024,068 episodes:
    # ZERO episodes carry an excluded pattern. This is why the rule is ADDITIVE and
    # not a basis change -- the discipline `FINDING 45` cost 28.95 % of the corpus
    # to learn. The Leg-4 pilot emitted 39 (`es`) / 23 (`uk`) / 59 (`it`).
    # -----------------------------------------------------------------------
    bits = load_bit_positions(os.path.join(step2_dir, "crosswalk_copresence.csv"))
    if "cop_alone" not in bits:
        raise GrammarError(
            "crosswalk_copresence.csv no longer declares `cop_alone`. D-S7-5 (1) "
            "is defined in terms of that flag and cannot be applied without it.")
    alone = 1 << bits["cop_alone"]
    cop = set(c for c in range(COP_MIN, COP_MAX + 1)
              if c == COP_MAX or not (c & alone and c & ~alone))
    excluded = sorted(set(range(COP_MIN, COP_MAX + 1)) - cop)
    if len(excluded) != 31:
        raise GrammarError(
            "D-S7-5 (1) excludes %d patterns, not 31. The COP width or the bit "
            "positions have changed and the ruling must be re-read." % len(excluded))

    return {
        "act": act,
        "act_n_shipped": n_shipped,
        "act2": act2,
        "loc": set(LOC_ALPHABET),
        "cop": cop,
        "outdoor_at_home": outdoor,
        "cop_excluded_self_contradiction": set(excluded),
    }


# ---------------------------------------------------------------------------
# The 145-state duration tally automaton.
# ---------------------------------------------------------------------------
def tally_automaton():
    """`RL12` objected that `sum(DUR) == 1440` is unbounded arithmetic and so
    not regular. It is not unbounded: durations are multiples of 10 and the
    total is fixed, so the running tally takes exactly 145 values. This function
    returns that machine EXPLICITLY -- states 0..144, one accepting state -- so
    the regularity claim is a table anyone can count rather than a paragraph.

    Verified 2026-08-20 against the real corpus: a grep for any duration whose
    final digit is non-zero returned ZERO diaries across all 73,254 records, so
    the multiple-of-10 premise holds for ES, UK and IT alike -- including the two
    countries that ship native episodes rather than reconstructed slots.
    """
    states = list(range(N_TALLY_STATES))
    delta = {}
    for s in states:
        for k in range(1, N_TALLY_STATES - s):   # k = duration / 10, >= 1
            delta[(s, k)] = s + k
    return {"states": states, "start": 0, "accepting": {N_TALLY_STATES - 1}, "delta": delta}


def tally_step(state, duration_min):
    if duration_min <= 0 or duration_min % SLOT_MINUTES:
        return None
    nxt = state + duration_min // SLOT_MINUTES
    return nxt if nxt <= N_TALLY_STATES - 1 else None


# ---------------------------------------------------------------------------
# The hand-written oracle. Independent recogniser for the same language.
# ---------------------------------------------------------------------------
def validate_record(text, alphabets, policy, acknowledge_finding_45=False):
    """Returns (ok: bool, reason: str). `reason` is "" iff ok.

    `policy` is REQUIRED and has no default -- see D-S7-2.
    """
    if policy not in TransitionPolicy.ALL:
        raise GrammarError("policy must be one of %s, got %r. It has no default on "
                           "purpose: see FINDING 45 / D-S7-2." % (TransitionPolicy.ALL, policy))
    if policy == TransitionPolicy.REQUIRE_TRAVEL and not acknowledge_finding_45:
        raise GrammarError(
            "REQUIRE_TRAVEL rejects %d of %d real diaries (%.2f %%), unevenly by country "
            "(ES %.2f %%, UK %.2f %%, IT %.2f %%). Pass acknowledge_finding_45=True only "
            "after D-S7-2 is ruled." % (
                FINDING_45_MEASURED["all"][0], FINDING_45_MEASURED["all"][1],
                100.0 * FINDING_45_MEASURED["all"][0] / FINDING_45_MEASURED["all"][1],
                100.0 * FINDING_45_MEASURED["es"][0] / FINDING_45_MEASURED["es"][1],
                100.0 * FINDING_45_MEASURED["uk"][0] / FINDING_45_MEASURED["uk"][1],
                100.0 * FINDING_45_MEASURED["it"][0] / FINDING_45_MEASURED["it"][1]))

    if not isinstance(text, str):
        return False, "not a string"
    if any(ch.isspace() for ch in text):
        return False, "whitespace present (V3.c forbids it anywhere)"
    if not text.endswith(EOR):
        return False, "does not end with %s" % EOR
    body = text[:-len(EOR)]
    if PREFIX_BODY_SEP not in body:
        return False, "no %r separating prefix from episodes" % PREFIX_BODY_SEP

    prefix, episodes_str = body.split(PREFIX_BODY_SEP, 1)
    pf = prefix.split(FIELD_SEP)
    if len(pf) != N_PREFIX_FIELDS:
        return False, "prefix has %d fields, expected %d" % (len(pf), N_PREFIX_FIELDS)
    if any(f == "" for f in pf):
        return False, "prefix has an empty field"

    if episodes_str == "":
        return False, "zero episodes"
    if not episodes_str.endswith(EPISODE_SEP):
        return False, "last episode is missing its terminal %r" % EPISODE_SEP

    chunks = episodes_str.split(EPISODE_SEP)[:-1]
    if not chunks:
        return False, "zero episodes"

    state = 0
    prev_loc = None
    seen_transport_since_other = False
    for i, ch in enumerate(chunks):
        f = ch.split(FIELD_SEP)
        if len(f) != N_EPISODE_FIELDS:
            return False, "episode %d has %d fields, expected %d" % (i, len(f), N_EPISODE_FIELDS)
        dur_s, act, act2, loc, cop_s = f

        if not dur_s.isdigit() or (len(dur_s) > 1 and dur_s[0] == "0"):
            return False, "episode %d duration %r is not a leading-zero-free integer" % (i, dur_s)
        state = tally_step(state, int(dur_s))
        if state is None:
            return False, ("episode %d duration %s is not a positive multiple of %d, or the "
                           "running tally passed %d minutes" % (i, dur_s, SLOT_MINUTES, DAY_MINUTES))

        if act not in alphabets["act"]:
            return False, "episode %d ACT %r not in the alphabet" % (i, act)
        if act2 != "" and act2 not in alphabets["act2"]:
            return False, "episode %d ACT2 %r not in the alphabet" % (i, act2)
        if loc not in alphabets["loc"]:
            return False, "episode %d LOC %r not in the alphabet" % (i, loc)
        if not cop_s.isdigit() or (len(cop_s) > 1 and cop_s[0] == "0"):
            return False, "episode %d COP %r is not a leading-zero-free integer" % (i, cop_s)
        if int(cop_s) not in alphabets["cop"]:
            # 🔴 Two different rejections wear this one test, and reporting them
            # identically was actively misleading: after `D-S7-5` (1) cut the
            # alphabet from 65 values to 34, the common rejection is a value that
            # IS inside 0..64 and is simply not an admissible flag set. The old
            # message said "outside 0..64" about `COP 5`, which is inside it.
            if int(cop_s) < COP_MIN or int(cop_s) > COP_MAX:
                return False, ("episode %d COP %s outside the %d..%d encoding range"
                               % (i, cop_s, COP_MIN, COP_MAX))
            return False, ("episode %d COP %s is in 0..%d but is not one of the %d "
                           "admissible flag sets (D-S7-5 (1))"
                           % (i, cop_s, COP_MAX, len(alphabets["cop"])))

        if policy == TransitionPolicy.REQUIRE_TRAVEL:
            if loc in LOC_TRANSPORT:
                seen_transport_since_other = True
            elif prev_loc == "other_place" and loc == "at_home" and not seen_transport_since_other:
                return False, ("episode %d is a direct other_place -> at_home transition with no "
                               "travel episode (G7.3, literal reading)" % i)
            if loc == "other_place":
                seen_transport_since_other = False
        prev_loc = loc

    if state != N_TALLY_STATES - 1:
        return False, "durations sum to %d minutes, not %d" % (state * SLOT_MINUTES, DAY_MINUTES)
    return True, ""


if __name__ == "__main__":
    print("Library module. Run 4thJ_step7_grammar_selftest.py for its unit tests.",
          file=sys.stderr)
