#!/usr/bin/env python
"""
4J Step 3, work item 3.3: the decoder. `decode_record(text) -> dict`, the exact
inverse of `encoder.encode_diary`.

Returned shape:
    {
      "prefix": {
          "country": str, "strat_age_band": str (verbatim, e.g. "11-14"; D-S3-6,
              no transliteration -- the record already carries the exact label),
          "strat_sex": str, "strat_hh_type": str, "strat_econ_status": str,
          "strat_day_type": str,
      },   # SIX fields -- D-S3-11 removed `mode` and `scheme`
      "episodes": [
          {"duration_min": int, "act": str or None,  # None iff ACT slot was "000" (D-S3-9)
           "act2": str or None,
           "loc_class": str or None,           # None iff the LOC slot was "unknown"
           "cop": {flag: bool, ...} or None,    # None iff COP == 64 ("not collected")
          }, ...
      ],
    }

🔴 `decode(64)` returns `cop: None` -- the null co-presence state, NOT six False
flags. `decode('unknown')` returns `loc_class: None` -- a null value, not a string
"unknown". `decode('000')` returns `act: None` -- the null-activity state
(D-S3-9), not the string "000". All three are explicit per the acceptance tests;
treating any of them as a real value is exactly the defect D-S3-4/D-S3-5/D-S3-9
exist to repair (a "not collected"/"not usable" episode silently read back as a
value that means something).

The bit order and the frozen age-band set are imported from `encoder.py` rather
than duplicated, because they are genuinely one piece of shared knowledge (the
crosswalk's bit order, the closed age-band vocabulary) that encoder and decoder
must agree on to round-trip at all -- this is NOT the kind of sharing `G3.13` /
`G3.14(b)` forbid. Those gates must import NOTHING from either this file or
`encoder.py`; that independence is the gates' job, not this pair's.

D-S3-6: `strat_age_band` ships verbatim (no transliteration table), so
`decode_prefix` only validates membership in the frozen 8-value set and returns
the value unchanged -- there is no reverse mapping because there is nothing to
reverse.
"""

from encoder import (
    ACT_NULL_CODE, AGE_BANDS, COP_NOT_COLLECTED, EOR, LOC_UNKNOWN,
    PREFIX_BODY_SEP, PREFIX_FIELDS, PREFIX_SEP, SHARED_FLAGS,
)


class DecodeError(ValueError):
    pass


def decode_prefix(prefix_str):
    fields = prefix_str.split(PREFIX_SEP)
    if len(fields) != len(PREFIX_FIELDS):
        raise DecodeError("prefix has %d fields, expected %d: %r"
                           % (len(fields), len(PREFIX_FIELDS), prefix_str))
    # D-S3-11: six fields, not eight. `mode` and `scheme` are no longer serialised.
    country, age_band, sex, hh_type, econ_status, day_type = fields
    if age_band not in AGE_BANDS:
        raise DecodeError("prefix strat_age_band %r is not one of the 8 known bands" % age_band)
    return {
        "country": country,
        "strat_age_band": age_band,
        "strat_sex": sex,
        "strat_hh_type": hh_type,
        "strat_econ_status": econ_status,
        "strat_day_type": day_type,
    }


def decode_cop(cop_int, bitpos):
    if cop_int == COP_NOT_COLLECTED:
        return None
    if not (0 <= cop_int < COP_NOT_COLLECTED):
        raise DecodeError("COP value %d is out of range 0-64" % cop_int)
    return {flag: bool((cop_int >> pos) & 1) for flag, pos in bitpos.items()}


def decode_episode(episode_str, bitpos):
    if not episode_str.endswith(";"):
        raise DecodeError("episode %r does not end with ';'" % episode_str)
    body = episode_str[:-1]
    fields = body.split(",")
    if len(fields) != 5:
        raise DecodeError("episode %r has %d comma-fields, expected 5" % (episode_str, len(fields)))
    dur_s, act, act2, loc, cop_s = fields
    if not dur_s.isdigit():
        raise DecodeError("DUR %r is not a plain decimal integer" % dur_s)
    if dur_s != str(int(dur_s)):
        raise DecodeError("DUR %r carries a leading zero or other non-canonical spelling" % dur_s)
    if not (len(act) == 3 and act.isdigit()):
        raise DecodeError("ACT %r is not a 3-digit code" % act)
    act_val = None if act == ACT_NULL_CODE else act
    if act2 == "":
        act2_val = None
    else:
        act2_val = act2
    if loc == LOC_UNKNOWN:
        loc_val = None
    elif loc == "":
        raise DecodeError("LOC slot is empty -- LOC must be one of the five declared classes")
    else:
        loc_val = loc
    if not cop_s.isdigit():
        raise DecodeError("COP %r is not a plain decimal integer" % cop_s)
    if cop_s != str(int(cop_s)):
        raise DecodeError("COP %r carries a leading zero or other non-canonical spelling" % cop_s)
    cop_int = int(cop_s)
    return {
        "duration_min": int(dur_s),
        "act": act_val,
        "act2": act2_val,
        "loc_class": loc_val,
        "cop": decode_cop(cop_int, bitpos),
    }


def decode_record(text, bitpos):
    if not text.endswith(EOR):
        raise DecodeError("record does not end with %r: %r" % (EOR, text[-40:]))
    body = text[: -len(EOR)]
    if PREFIX_BODY_SEP not in body:
        raise DecodeError("record has no %r prefix/body separator" % PREFIX_BODY_SEP)
    prefix_str, episodes_str = body.split(PREFIX_BODY_SEP, 1)
    prefix = decode_prefix(prefix_str)
    if not episodes_str.endswith(";"):
        raise DecodeError("episode block does not end with ';': %r" % episodes_str[-40:])
    # Episodes are concatenated with no separator, each ending in ';'. Splitting
    # on ';' and dropping the trailing empty element (produced by the final ';')
    # recovers each episode string with its terminator re-attached.
    pieces = episodes_str.split(";")
    if pieces[-1] != "":
        raise DecodeError("episode block does not cleanly split on ';': trailing piece %r" % pieces[-1])
    episode_strs = [p + ";" for p in pieces[:-1]]
    if not episode_strs:
        raise DecodeError("record has zero episodes")
    episodes = [decode_episode(e, bitpos) for e in episode_strs]
    return {"prefix": prefix, "episodes": episodes}


if __name__ == "__main__":
    import sys
    print("This module is a library (decode_record, decode_prefix, decode_episode, "
          "decode_cop). Run 4thJ_step3_build.py to build and round-trip the corpus.",
          file=sys.stderr)
