#!/usr/bin/env python
"""
4J Step 3, work item 3.3: the encoder. `encode_diary(...) -> str`.

Record format, frozen 2026-08-17 (night) in `4thJ_03_serialisation.md`, amended
the same day by D-S3-11:

    <6-field prefix> | DUR,ACT,ACT2,LOC,COP DUR,ACT,ACT2,LOC,COP ... <eor>

No whitespace anywhere (V3.c). Concretely:

    record = prefix_csv + "|" + episode_1 + episode_2 + ... + episode_n + "<eor>"

where each episode_i = "DUR,ACT,ACT2,LOC,COP;" (terminal semicolon, no separator
between consecutive episodes -- the same convention already used by the accepted
`tools/4thJ_cop_measure.py` / `tools/4thJ_act2_measure.py` measurements that this
record format was costed against).

Prefix, in this fixed order, SIX fields (D-S2-19 dropped `season`; D-S3-11
dropped `mode` and `scheme`), joined by a plain comma -- comma is already in the
declared alphabet and is unambiguous here because the decoder always splits on
the first "|" before touching the prefix:

    country, strat_age_band, strat_sex, strat_hh_type, strat_econ_status,
    strat_day_type

D-S3-11 (author, 2026-08-17) -- `mode` and `scheme` were REMOVED from the prefix.
Both columns remain in `harmonised.parquet` and are simply never serialised, like
the six `strat_*_raw` carriers. They were documented as constants across the whole
corpus; the shipped table populates them PER COUNTRY (`eet_2009_2010` /
`uktus_2014_2015` / `usodeltempo_2013_2014`, and two `mode` values), each one a
module constant hard-coded in its reader rather than anything read from a
respondent. So they carried exactly what `country` already carries, and under LOCO
they handed the held-out country a symbol training never showed the model. Their
removal is what makes `G3.10` (no four-digit year in the prefix) pass -- the corpus
stopped carrying years; the gate was NOT narrowed to admit them.

Field encodings:
    DUR  -- plain decimal integer, no leading zeros: str(int(duration_min)).
    ACT  -- the 3-digit target activity code, taken as-is from the `act` column
            (already a fixed-width digit string coming out of Step 2's crosswalk
            join -- validated here, not reformatted); or the literal string
            `000` when `act` is null (D-S3-9), meaning "the diary entry here was
            not a usable activity" -- 8,709 episodes, ES 3,786 / IT 333 / UK
            4,590, all from eight source codes Step 2 declined to map on
            purpose (`crosswalk_unmapped.md`). Durations are untouched.
    ACT2 -- empty string (two adjacent commas in the tuple) when absent; else the
            2-digit `act2` target code, taken as-is and validated against the 43
            shipped codes (D-S3-2). Never a sentinel, never whitespace.
    LOC  -- one of five lowercase strings: at_home, other_place, private_transport,
            public_transport (the four `crosswalk_location.csv` target_class
            values, taken as-is) or `unknown` for a null `loc_class` (D-S3-4).
    COP  -- single decimal integer, no leading zeros, 0-64. Bits 0-5 packed from
            the six `cop_*` boolean flags using the bit order read LIVE from
            `crosswalk_copresence.csv`'s `bit_position` column (never hard-coded).
            64 is emitted iff all six flags are null on that row (D-S3-5) -- "not
            collected", one greater than the largest legal bit pattern.

D-S3-6 -- `strat_age_band` ships VERBATIM, no transliteration. The frozen 8
values are `11-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+`
(`Step2_docs/outputs_step2/crosswalk_strata.csv`'s `target_band` column).
`V3.c`'s declared alphabet is amended to admit `-` and `+` for this field only.
A closed two-way lookup table was proposed and REFUSED by the author: an
encoder and decoder that agree with each other about a wrong mapping round-trip
perfectly and mean something else -- the exact defect class the bit-order
perturbation exists to catch, volunteered into a field no gate is watching. The
band labels are frozen upstream, so shipping them unchanged means there is no
mapping to get wrong. `enc_age_band` therefore only VALIDATES membership in the
frozen 8-value set and returns the value unchanged; there is no reverse table
because there is nothing to reverse.

`pd.NA`, not `NaN` -- `loc_class`, `act2` and the six `cop_*` flags are pandas
nullable dtypes. Every null test below is `pd.isna(x)` alone, checked BEFORE any
`==` comparison (RL: four failed jobs, two sites, this exact data).
"""

import csv
import re
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Frozen record shape
# ---------------------------------------------------------------------------
PREFIX_FIELDS = [
    "country", "strat_age_band", "strat_sex", "strat_hh_type",
    "strat_econ_status", "strat_day_type",
]  # D-S3-11: `mode` and `scheme` removed. Six fields, not eight.
PREFIX_SEP = ","          # joins the 6 prefix fields
PREFIX_BODY_SEP = "|"     # separates the prefix block from the episode block
EOR = "<eor>"

SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]

LOC_CLASSES = {"at_home", "other_place", "private_transport", "public_transport"}
LOC_UNKNOWN = "unknown"
LOC_ALPHABET = LOC_CLASSES | {LOC_UNKNOWN}

COP_NOT_COLLECTED = 64  # D-S3-5: one greater than the largest legal 0-63 bit pattern
ACT_NULL_CODE = "000"  # D-S3-9: null `act` -> the literal 3-digit string "000"

DIARY_KEY = ["country", "hid", "pid", "diary_day"]
RESPONDENT_KEY = ["country", "hid", "pid"]

# D-S3-6: strat_age_band ships VERBATIM. Frozen, closed 8-value set -- no
# transliteration table. enc_age_band() validates membership only.
AGE_BANDS = {
    "11-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+",
}

_SAFE_TOKEN_RE = re.compile(r"^[a-z0-9_]+$")


class EncodeError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Crosswalk loaders -- read live, never hard-coded (D-S3-1 / G3.14(b) discipline)
# ---------------------------------------------------------------------------
def load_bit_positions(path):
    positions = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            flag = row["shared_flag"]
            if flag in SHARED_FLAGS and flag not in positions:
                positions[flag] = int(row["bit_position"])
    missing = set(SHARED_FLAGS) - set(positions)
    if missing:
        raise EncodeError("crosswalk_copresence.csv missing bit_position for: %s" % missing)
    if sorted(positions.values()) != [0, 1, 2, 3, 4, 5]:
        raise EncodeError("crosswalk_copresence.csv bit positions are not exactly {0..5}: %s" % positions)
    return positions


def load_legal_act2_codes(path):
    codes = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = row["target_code_2d"].strip()
            if c:
                codes.add(c)
    if not codes:
        raise EncodeError("crosswalk_activity_secondary.csv yielded zero target_code_2d values")
    return codes


# ---------------------------------------------------------------------------
# Field-level encoders. Each one fails loud (EncodeError) rather than
# silently coercing or dropping.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Decision item 5 (a), 2026-08-20 -- G6.7's control token
# ---------------------------------------------------------------------------
# G6.7 asks whether the model follows its conditioning vector or a national stereotype,
# and it asks by generating under a FICTIONAL country. The production whitelist is
# {es, uk, it}, so `enc_country()` refused the fictional token and the gate could not be
# run at all -- FINDING 41.
#
# 🔴 The hole this must not open: if the whitelist were simply widened, a real run could
# ship a country token that never appeared in training and nothing would say so. So the
# hook is not a widening. A synthetic token must match SYNTHETIC_COUNTRY_RE -- an `x_`
# prefix that no ISO code has and no real value in the corpus can collide with -- AND
# the caller must ask for it explicitly, per call, with a keyword. Both, or it fails.
# The default is off, which means every existing caller keeps the old behaviour without
# being edited.
SYNTHETIC_COUNTRY_RE = re.compile(r"^x_[a-z]{2,16}$")
REAL_COUNTRIES = ("es", "uk", "it")


def enc_country(v, allow_synthetic_controls=False):
    if pd.isna(v):
        raise EncodeError("country is null")
    s = str(v).strip().lower()
    if s in REAL_COUNTRIES:
        return s
    if allow_synthetic_controls and SYNTHETIC_COUNTRY_RE.match(s):
        # 🔴 Deliberately reachable ONLY through the keyword. A synthetic token in a
        # corpus build or a scoring run is a defect, and the keyword is what makes that
        # defect visible in the call site rather than hidden in a value.
        return s
    if SYNTHETIC_COUNTRY_RE.match(s):
        raise EncodeError(
            "country %r is a synthetic control token, and this call did not ask for one. "
            "Pass allow_synthetic_controls=True -- which only G6.7's fictional-country "
            "control may do. Production paths must not." % v)
    raise EncodeError("country %r lowercased to %r, not one of es/uk/it, and not a "
                      "synthetic control token matching %s"
                      % (v, s, SYNTHETIC_COUNTRY_RE.pattern))


def enc_age_band(v):
    """D-S3-6: verbatim, no transliteration. Validate membership, return as-is."""
    if pd.isna(v):
        raise EncodeError("strat_age_band is null")
    s = str(v).strip()
    if s not in AGE_BANDS:
        raise EncodeError("strat_age_band %r is not one of the 8 known bands %s"
                           % (s, sorted(AGE_BANDS)))
    return s


def enc_safe_categorical(v, field_name):
    """Generic validator for strat_sex / strat_hh_type / strat_econ_status /
    strat_day_type -- pass through as-is (lowercased) but FAIL
    if a character outside the declared alphabet (a-z, 0-9, underscore) shows
    up, rather than silently widening what we accept."""
    if pd.isna(v):
        raise EncodeError("%s is null" % field_name)
    s = str(v).strip().lower()
    if not _SAFE_TOKEN_RE.match(s):
        raise EncodeError("%s value %r (lowercased %r) contains a character outside "
                           "[a-z0-9_] -- not in V3.c's declared alphabet" % (field_name, v, s))
    return s


def enc_dur(v):
    if pd.isna(v):
        raise EncodeError("duration_min is null")
    iv = int(v)
    if iv <= 0:
        raise EncodeError("duration_min %r is not positive" % v)
    return str(iv)


def enc_act(v):
    """D-S3-9: null `act` -> the literal code ACT_NULL_CODE ("000"), meaning
    "the diary entry here was not a usable activity". Durations are untouched."""
    if pd.isna(v):
        return ACT_NULL_CODE
    s = str(v).strip()
    if not (len(s) == 3 and s.isdigit()):
        raise EncodeError("act %r is not a 3-digit code" % v)
    return s


def enc_act2(v, legal_act2):
    if pd.isna(v) or v == "":
        return ""
    s = str(v).strip()
    if s not in legal_act2:
        raise EncodeError("act2 %r is not one of the 43 shipped ACT2 target codes" % v)
    return s


def enc_loc(v):
    if pd.isna(v):
        return LOC_UNKNOWN
    s = str(v).strip()
    if s not in LOC_CLASSES:
        raise EncodeError("loc_class %r is not one of %s" % (v, sorted(LOC_CLASSES)))
    return s


def enc_cop(row, bitpos):
    """Pack the six cop_* flags into 0-63, or return 64 if all six are null
    (D-S3-5). A PARTIAL null (some but not all six) is an invariant violation
    the null-structure measurement never observed -- fail loud rather than
    guess which state was intended."""
    null_flags = [f for f in SHARED_FLAGS if pd.isna(row[f])]
    if len(null_flags) == 6:
        return COP_NOT_COLLECTED
    if null_flags:
        raise EncodeError("partial null cop_* flags (%s null, %s not) -- expected all-six-or-none"
                           % (null_flags, [f for f in SHARED_FLAGS if f not in null_flags]))
    v = 0
    for flag, pos in bitpos.items():
        bit = 1 if int(row[flag]) != 0 else 0
        v |= (bit << pos)
    return v


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def encode_prefix(row, allow_synthetic_controls=False):
    fields = [
        enc_country(row["country"], allow_synthetic_controls=allow_synthetic_controls),
        enc_age_band(row["strat_age_band"]),
        enc_safe_categorical(row["strat_sex"], "strat_sex"),
        enc_safe_categorical(row["strat_hh_type"], "strat_hh_type"),
        enc_safe_categorical(row["strat_econ_status"], "strat_econ_status"),
        enc_safe_categorical(row["strat_day_type"], "strat_day_type"),
    ]  # D-S3-11: `mode` and `scheme` are no longer serialised.
    return PREFIX_SEP.join(fields)


def encode_episode(row, bitpos, legal_act2):
    dur = enc_dur(row["duration_min"])
    act = enc_act(row["act"])
    act2 = enc_act2(row["act2"], legal_act2)
    loc = enc_loc(row["loc_class"])
    cop = enc_cop(row, bitpos)
    return "%s,%s,%s,%s,%d;" % (dur, act, act2, loc, cop)


def encode_diary(prefix_row, episode_rows_sorted, bitpos, legal_act2,
                 allow_synthetic_controls=False):
    """prefix_row: a single row (Series/dict) carrying the 6 prefix columns.
    episode_rows_sorted: an iterable of rows for this diary, already sorted by
    episode_index, each carrying duration_min/act/act2/loc_class/cop_* columns.
    """
    prefix = encode_prefix(prefix_row,
                           allow_synthetic_controls=allow_synthetic_controls)
    episodes = "".join(encode_episode(r, bitpos, legal_act2) for r in episode_rows_sorted)
    if not episodes:
        raise EncodeError("diary has zero episodes")
    return prefix + PREFIX_BODY_SEP + episodes + EOR


if __name__ == "__main__":
    print("This module is a library (encode_diary, encode_prefix, encode_episode, "
          "enc_* field encoders, load_bit_positions, load_legal_act2_codes). "
          "Run 4thJ_step3_build.py to build the corpus.", file=sys.stderr)
