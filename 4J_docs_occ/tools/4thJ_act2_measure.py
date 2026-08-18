#!/usr/bin/env python
"""
4J Step 3, work item 3.2-bis: measure the token cost of adding ACT2 (secondary activity) to the
DUR,ACT,LOC,COP tuple. Mirrors tools/4thJ_cop_measure.py's methodology exactly, per the task doc's
instruction ("measure it, exactly the way COP packing was measured, D-S3-1, job 1252633"):

  * every candidate is measured IN SITU, inside a complete episode tuple and inside complete real
    diaries -- never as a bare string (the RL18 failure mode);
  * every legal ACT2 value is swept and the WORST case is reported, not a lucky example;
  * the sentinel used for "absent secondary" is verified against the shipped ACT2 target list before
    it is used (the Spain "999" near-miss: a perturbation that is secretly a legal code tests nothing).

Unlike the COP measurement, this one also runs on REAL data: a random sample of >=2000 diaries drawn
from harmonised.parquet, because the task doc requires it ("measure on real data, not on a
representative string").

Five candidate tuple forms (see task doc table):
  0  DUR,ACT,LOC,COP                  -- baseline, four elements, no ACT2 at all
  1  DUR,ACT,ACT2,LOC,COP             -- absent secondary = declared 2-digit sentinel
  2  DUR,ACT,LOC,COP,ACT2             -- absent secondary = declared 2-digit sentinel
  3  DUR,ACT,ACT2,LOC,COP             -- absent secondary = empty field
  4  DUR,ACT,LOC,COP,ACT2             -- absent secondary = empty field

No prefix, no <eor> -- matching 4thJ_cop_measure.py's methodology and the 200-token benchmark it is
compared against. G3.5's band (median <= 220, p99 <= 400) is anchored on that same bare-diary form.

🔴 LOC is read from the harmonised table's own `loc_class` column, which as of D-S2-3 is one of four
semantic-class strings (at_home / other_place / private_transport / public_transport), NOT a short
numeric HETUS code. This differs from 4thJ_cop_measure.py's own synthetic LOC placeholders
("11","31","91","41","21"), which were written before / independent of that decision. This script uses
the REAL, current alphabet throughout (both in the real-diary pass and in the synthetic in-situ sweep);
it does not attempt to re-measure or correct the earlier, already-accepted COP result. Flagged in the
implementation doc, not fixed here -- out of this task's scope.

Tokenizer: allenai/OLMo-2-0425-1B, stated stand-in for the 7B backbone's OLMo/dolma2 vocab (identical
vocabulary, far smaller download) -- a premise of the task, not re-derived here, exactly as the COP
round stated it.

Run with sbatch. Never on the login node.
"""

import csv
import os
import statistics
import sys
import traceback

import numpy as np
import pandas as pd

MODEL = "allenai/OLMo-2-0425-1B"
NOTE = ("stand-in for allenai/Olmo-3-1025-7B: identical dolma2 BPE vocabulary, "
        "used here only because it is far smaller to download -- vocabulary identity is a premise "
        "of this task, not re-derived here")

HARMONISED = "/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet"
CW_COP = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_copresence.csv"
CW_ACT2 = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_activity_secondary.csv"

N_SAMPLE_DIARIES = 2500  # >= the task doc's "at least 2,000"
SEED = 42

SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]

DIARY_KEY = ["country", "hid", "pid", "diary_day"]

CANDIDATE_SENTINEL = "98"  # verified against the shipped target list below before use


# ---------------------------------------------------------------------------
# Load the bit order from the crosswalk -- never hard-coded (same discipline G3.14(b) requires
# of the encoder, applied here even though this script does not touch G3.14).
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
        print("FATAL: crosswalk_copresence.csv is missing bit_position for: %s" % missing)
        sys.exit(1)
    if sorted(positions.values()) != [0, 1, 2, 3, 4, 5]:
        print("FATAL: bit positions are not exactly {0..5}: %s" % positions)
        sys.exit(1)
    return positions


# ---------------------------------------------------------------------------
# Load the legal ACT2 target vocabulary (2-digit codes) -- proper CSV parsing (quoted fields with
# embedded commas exist in this file), never a naive split.
# ---------------------------------------------------------------------------
def load_legal_act2_codes(path):
    codes = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = row["target_code_2d"].strip()
            if c:
                codes.add(c)
    return codes


def pack_cop(row, bitpos, null_episodes=None):
    v = 0
    had_null = False
    for flag, pos in bitpos.items():
        val = row.get(flag)
        # D-S2-8: ~68,464 UK rows have all six shared flags set null (missingness-flagged).
        # Not a COP-packing decision this task makes; treated as bit-unset (0) for the sole purpose
        # of giving the ACT2 measurement a well-formed COP field to sit next to. Flagged, not decided.
        # NA-FIX 2026-08-17 (jobs 1255143/1255174 crash): the cop_* columns' missing values are
        # pandas' pd.NA sentinel (nullable "boolean" dtype), which is neither None nor a python
        # float NaN -- the old `isinstance(val, float) and pd.isna(val)` guard missed it and
        # int(pd.NA) raised TypeError. pd.isna() alone correctly detects None/NaN/NaT/pd.NA.
        if pd.isna(val):
            bit = 0
            had_null = True
        else:
            bit = 1 if int(val) != 0 else 0
        v |= (bit << pos)
    if had_null and null_episodes is not None:
        null_episodes.add((row["country"], row["hid"], row["pid"], row["diary_day"], row["episode_index"]))
    return v


def fmt_act(v):
    s = str(v).strip()
    if s.isdigit():
        return s.zfill(3)
    return s


def fmt_act2(v):
    s = str(v).strip()
    if s.isdigit():
        return s.zfill(2)
    return s


def episode_tuple_str(dur, act, loc, cop):
    return "%d,%s,%s,%d;" % (dur, act, loc, cop)


def episode_5_str(dur, act, act2_field, loc, cop, act2_after_cop):
    if act2_after_cop:
        return "%d,%s,%s,%d,%s;" % (dur, act, loc, cop, act2_field)
    return "%d,%s,%s,%s,%s;" % (dur, act, act2_field, loc, cop)


# candidate id -> (has_act2, act2_after_cop, absent_is_sentinel)
CANDIDATES = {
    0: (False, None, None),
    1: (True, False, True),
    2: (True, True, True),
    3: (True, False, False),
    4: (True, True, False),
}
CANDIDATE_DESC = {
    0: "DUR,ACT,LOC,COP -- baseline, four elements",
    1: "DUR,ACT,ACT2,LOC,COP -- absent = declared 2-digit sentinel '%s'" % CANDIDATE_SENTINEL,
    2: "DUR,ACT,LOC,COP,ACT2 -- absent = declared 2-digit sentinel '%s'" % CANDIDATE_SENTINEL,
    3: "DUR,ACT,ACT2,LOC,COP -- absent = empty field",
    4: "DUR,ACT,LOC,COP,ACT2 -- absent = empty field",
}


def act2_field_value(cand, act2_value):
    """act2_value is None for 'absent'. Returns the string to place in the tuple, or None if
    this candidate has no ACT2 field at all (candidate 0)."""
    has_act2, _, absent_is_sentinel = CANDIDATES[cand]
    if not has_act2:
        return None
    if act2_value is None:
        return CANDIDATE_SENTINEL if absent_is_sentinel else ""
    return fmt_act2(act2_value)


def build_episode_str(cand, dur, act, loc, cop, act2_value):
    has_act2, act2_after_cop, _ = CANDIDATES[cand]
    act_s = fmt_act(act)
    if not has_act2:
        return episode_tuple_str(dur, act_s, loc, cop)
    field = act2_field_value(cand, act2_value)
    return episode_5_str(dur, act_s, field, loc, cop, act2_after_cop)


def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def pct(x, p):
    return float(np.percentile(np.array(x), p, method="linear"))


def main():
    print("4J ACT2 tuple-cost measurement (work item 3.2-bis)")
    print("=" * 78)
    print("pandas %s, numpy %s" % (pd.__version__, np.__version__))
    try:
        import transformers
        print("transformers version: %s" % transformers.__version__)
    except Exception:
        print("FATAL: transformers is not importable in this environment.")
        traceback.print_exc()
        sys.exit(1)
    from transformers import AutoTokenizer

    print("MODEL   %s" % MODEL)
    print("NOTE    %s" % NOTE)
    try:
        tok = AutoTokenizer.from_pretrained(MODEL)
    except Exception as exc:
        print("STATUS  COULD NOT LOAD")
        print("REASON  %s: %s" % (type(exc).__name__, str(exc)[:300]))
        sys.exit(1)
    print("STATUS  loaded, vocab=%s" % getattr(tok, "vocab_size", "unknown"))

    # -----------------------------------------------------------------
    # Bit order and legal ACT2 vocabulary, both read live, never hard-coded.
    # -----------------------------------------------------------------
    bitpos = load_bit_positions(CW_COP)
    print()
    print("bit_position (from crosswalk_copresence.csv, read live): %s" % bitpos)

    legal_act2 = load_legal_act2_codes(CW_ACT2)
    print("legal ACT2 target codes (from crosswalk_activity_secondary.csv, %d distinct): %s"
          % (len(legal_act2), sorted(legal_act2)))
    if CANDIDATE_SENTINEL in legal_act2:
        print("FATAL: chosen sentinel '%s' IS a legal ACT2 code. Refusing to measure with it."
              % CANDIDATE_SENTINEL)
        sys.exit(1)
    print("SENTINEL CHECK: '%s' is NOT in the shipped ACT2 target list -- safe to use as the "
          "declared out-of-list sentinel." % CANDIDATE_SENTINEL)

    # -----------------------------------------------------------------
    # Load harmonised.parquet, minimum columns.
    # -----------------------------------------------------------------
    cols = DIARY_KEY + ["episode_index", "duration_min", "act", "loc_class", "act2"] + SHARED_FLAGS
    print()
    print("reading %s, columns=%s" % (HARMONISED, cols))
    df = pd.read_parquet(HARMONISED, columns=cols)
    print("rows read: %d" % len(df))
    print("distinct loc_class values observed: %s" % sorted(df["loc_class"].dropna().unique().tolist()))
    print("distinct country values observed: %s" % sorted(df["country"].dropna().unique().tolist()))

    df["_diary_key"] = list(zip(df["country"], df["hid"], df["pid"], df["diary_day"]))
    all_keys = df["_diary_key"].unique()
    print("distinct diaries in harmonised.parquet: %d" % len(all_keys))

    # -----------------------------------------------------------------
    # NA extent, measured on the full table before any sampling/Part B: per country per cop_*
    # flag, how many rows are null and how many distinct diaries are touched. This is the finding
    # behind jobs 1255143/1255174's crash -- reported, not just worked around.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("NULL EXTENT of cop_* flags (measured before Part B, full harmonised.parquet)")
    print("%-8s %-16s %12s %18s" % ("country", "flag", "null_rows", "distinct_diaries"))
    for _country in sorted(df["country"].dropna().unique().tolist()):
        _cmask = df["country"] == _country
        for _flag in SHARED_FLAGS:
            _nullmask = _cmask & df[_flag].isna()
            _n_null = int(_nullmask.sum())
            _n_diaries = int(df.loc[_nullmask, "_diary_key"].nunique()) if _n_null else 0
            print("%-8s %-16s %12d %18d" % (_country, _flag, _n_null, _n_diaries))
    _any_null_rows = int(df[SHARED_FLAGS].isna().any(axis=1).sum())
    _any_null_diaries = int(df.loc[df[SHARED_FLAGS].isna().any(axis=1), "_diary_key"].nunique())
    print("TOTAL rows with >=1 null cop_* flag: %d, distinct diaries touched: %d"
          % (_any_null_rows, _any_null_diaries))

    rng = np.random.default_rng(SEED)
    n_sample = min(N_SAMPLE_DIARIES, len(all_keys))
    sample_keys = set(rng.choice(all_keys, size=n_sample, replace=False).tolist())
    print("sampling %d diaries (seed=%d, requested %d, available %d)"
          % (n_sample, SEED, N_SAMPLE_DIARIES, len(all_keys)))

    sample_df = df[df["_diary_key"].isin(sample_keys)].sort_values(DIARY_KEY + ["episode_index"])
    print("episodes in sample: %d" % len(sample_df))
    country_counts = sample_df.drop_duplicates(subset=DIARY_KEY)["country"].value_counts().to_dict()
    print("sampled diaries per country: %s" % country_counts)

    n_act2_present = int((sample_df["act2"].notna() & (sample_df["act2"] != "")).sum())
    n_act2_absent = int(len(sample_df) - n_act2_present)
    print("sampled episodes: act2 present=%d, absent(null-or-blank)=%d" % (n_act2_present, n_act2_absent))

    # -----------------------------------------------------------------
    # PART A -- in-situ worst-case sweep, representative episode, all 5 candidates.
    # Sweep dimensions: every legal ACT2 code + the sentinel-or-empty absent case, x all 4 LOC
    # classes actually observed x a representative ACT/COP/DUR -- reported as the max, with argmax,
    # so the worst case is auditable rather than assumed to sit at one particular LOC.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART A -- in-situ worst-case sweep (representative episode, not a bare string)")
    REP_DUR, REP_ACT, REP_COP = 30, "311", 22
    loc_values = sorted(df["loc_class"].dropna().unique().tolist())
    act2_sweep_values = sorted(legal_act2) + [None]  # None = the "absent" case

    worst_by_cand = {}
    for cand in range(5):
        max_tok = -1
        argmax = None
        for loc in loc_values:
            for a2 in act2_sweep_values:
                s = build_episode_str(cand, REP_DUR, REP_ACT, loc, REP_COP, a2)
                t = n_tok(tok, s)
                if t > max_tok:
                    max_tok = t
                    argmax = (loc, a2, s)
        worst_by_cand[cand] = (max_tok, argmax)
        print("candidate %d  %s" % (cand, CANDIDATE_DESC[cand]))
        print("   worst case = %d tokens, at loc=%r act2=%r, string=%r"
              % (max_tok, argmax[0], argmax[1], argmax[2]))

    # -----------------------------------------------------------------
    # PART B -- real data, >=2000 diaries, all 5 candidates, median/p99 tokens/diary.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART B -- real diaries (n=%d), median/p99 tokens/diary, all 5 candidates" % n_sample)

    grouped = list(sample_df.groupby(DIARY_KEY, sort=False))
    results = {cand: [] for cand in range(5)}
    null_flag_episodes = set()
    for _, g in grouped:
        g = g.sort_values("episode_index")
        for cand in range(5):
            parts = []
            for _, row in g.iterrows():
                cop_v = pack_cop(row, bitpos, null_flag_episodes)
                a2 = row["act2"]
                a2_val = None if (pd.isna(a2) or a2 == "") else a2
                parts.append(build_episode_str(cand, int(row["duration_min"]), row["act"],
                                                row["loc_class"], cop_v, a2_val))
            diary_str = "".join(parts)
            results[cand].append(n_tok(tok, diary_str))

    print()
    print("episodes in Part B sample with >=1 null cop_* flag (treated as bit-unset=0, NOT dropped): "
          "%d" % len(null_flag_episodes))
    print()
    print("%-4s %-55s %8s %8s %8s %8s" % ("cand", "form", "n", "median", "p99", "max"))
    summary = {}
    for cand in range(5):
        vals = results[cand]
        med = statistics.median(vals)
        p99 = pct(vals, 99)
        mx = max(vals)
        summary[cand] = (med, p99, mx)
        print("%-4d %-55s %8d %8.1f %8.1f %8d" % (cand, CANDIDATE_DESC[cand][:55], len(vals), med, p99, mx))

    print()
    print("G3.5 pre-registered band: median <= 220, p99 <= 400 (anchored on the measured 200-token "
          "single-25-episode-diary benchmark)")
    for cand in range(5):
        med, p99, mx = summary[cand]
        med_ok = med <= 220
        p99_ok = p99 <= 400
        print("candidate %d: median %.1f (%s), p99 %.1f (%s)"
              % (cand, med, "within band" if med_ok else "EXCEEDS band",
                 p99, "within band" if p99_ok else "EXCEEDS band"))

    print()
    print("=" * 78)
    print("SUMMARY (worst-case in-situ episode tokens, and real-diary median/p99)")
    print("%-4s %-55s %8s %8s %8s" % ("cand", "form", "worst/ep", "median", "p99"))
    for cand in range(5):
        med, p99, mx = summary[cand]
        w, _ = worst_by_cand[cand]
        print("%-4d %-55s %8d %8.1f %8.1f" % (cand, CANDIDATE_DESC[cand][:55], w, med, p99))

    print()
    print("Reference: 4thJ_cop_measure.py's single-25-episode-diary benchmark = 200 tokens (bare "
          "chained-episode-tuple form, no prefix, no <eor>, same convention used here).")


if __name__ == "__main__":
    main()
