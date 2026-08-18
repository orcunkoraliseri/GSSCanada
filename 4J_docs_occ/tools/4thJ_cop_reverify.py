#!/usr/bin/env python
"""
4J: RE-VERIFY the accepted D-S3-1 COP-packing measurement (job 1252633,
tools/4thJ_cop_measure.py) against a flagged possible defect: that script serialised the LOC
slot using short numeric placeholders ("11","31","91","41","21"), but D-S2-3 (the later,
authoritative decision, Step2_docs/4thJ_02_harmonisation.md lines 131-141) fixes LOC as ONE OF
FOUR SEMANTIC-CLASS STRINGS emitted by crosswalk_location.csv's target_class column: at_home,
other_place, private_transport, public_transport. "public_transport" (16 chars) tokenizes very
differently from "41" (2 chars).

This script does NOT edit or replace 4thJ_cop_measure.py, does NOT change D-S3-1, and does NOT
move any threshold. It reproduces the SAME comparison (the same 5 COP-encoding candidates, the
same DUR/ACT skeleton, the same COP value sweep, the same tokenizer) with ONLY the LOC slot
corrected to the real alphabet, plus a real-diary median/p99 pass (which the original script did
not have -- it only measured one synthetic diary) so the ranking can be checked against actual
LOC-class prevalence across all three countries.

Two parts:
  PART A -- in-situ worst-case sweep, synthetic representative episode (DUR=30, ACT=311),
            swept over ALL 4 real LOC classes (read live from crosswalk_location.csv) x
            ALL 64 COP values = 256 combinations per candidate. Reports the true worst case
            and its (loc, v) argmax -- the original script only swept COP with LOC fixed at
            a hard-coded placeholder, which is exactly the gap being checked here.
  PART B -- real diaries (>=2000, sampled from harmonised.parquet), real duration_min/act/
            loc_class per episode, COP packed live from crosswalk_copresence.csv's
            bit_position column (same pack_cop logic as tools/4thJ_act2_measure.py). Reports
            median/p99/max tokens per diary per candidate, compared against G3.5's band
            (median <= 220, p99 <= 400).

Tuple form: DUR,ACT,LOC,<COP-encoding>; -- no ACT2, no prefix, no <eor> -- matching
4thJ_cop_measure.py's own scope and methodology exactly (D-S3-1 only decided the COP packing,
not the ACT2 question, which is a separate, later item).

Tokenizer: allenai/OLMo-2-0425-1B, same stated stand-in for the 7B backbone
(allenai/Olmo-3-1025-7B) used by the accepted measurement -- a premise of the original task, not
re-derived here.

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
        "used here only because it is far smaller to download -- vocabulary identity is a "
        "premise of this task, carried over unchanged from the accepted D-S3-1 measurement, "
        "not re-derived here")

HARMONISED = "/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet"
CW_COP = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_copresence.csv"
CW_LOC = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_location.csv"

N_SAMPLE_DIARIES = 2500  # matches the ACT2 re-measurement's sample size
SEED = 42

SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]

DIARY_KEY = ["country", "hid", "pid", "diary_day"]

# ---------------------------------------------------------------------------
# The 5 COP-encoding candidates, BYTE-IDENTICAL to tools/4thJ_cop_measure.py's functions.
# Only the LOC slot changes in this script -- these functions are unchanged on purpose.
# ---------------------------------------------------------------------------
def enc_decimal(v):
    return str(v)


def enc_binary6(v):
    return format(v, "06b")


def enc_octal2(v):
    return format(v, "02o")


def enc_hex2(v):
    return format(v, "02x")


def enc_baseline(v):
    return ",".join(format(v, "06b"))


CANDIDATES = [
    ("1_decimal_0-63", enc_decimal, "single decimal integer, 0-63"),
    ("2_six_chars", enc_binary6, "six characters, e.g. 010110"),
    ("3_two_octal", enc_octal2, "two octal digits, e.g. 26"),
    ("4_two_hex", enc_hex2, "two hex characters, e.g. 16"),
    ("5_baseline_csv_bits", enc_baseline, "six comma-separated digits, do-nothing baseline"),
]

# ---------------------------------------------------------------------------
# Same DUR/ACT skeleton and same per-episode COP value formula as 4thJ_cop_measure.py,
# unchanged. Only _LOC (below, PART A) and the real-diary pass (PART B) are new.
# ---------------------------------------------------------------------------
_DUR = [480, 240, 30, 20, 10, 40, 30, 60, 20, 10, 90, 30, 20, 10, 50, 30, 20, 10, 60,
        30, 20, 10, 40, 30, 50]
_ACT = ["311", "411", "111", "911", "311", "121", "411", "211", "511", "311", "111",
        "621", "411", "811", "311", "911", "121", "821", "411", "211", "311", "511",
        "111", "911", "311"]
assert len(_DUR) == len(_ACT) == 25
assert sum(_DUR) == 1440

_COP_VALS = [(7 * i + 3) % 64 for i in range(25)]

REP_DUR, REP_ACT, REP_V = 30, "311", 22


def load_loc_classes(path):
    """Live from crosswalk_location.csv's target_class column -- never hard-coded (D-S2-3's
    own discipline: 'The serialised alphabet is whatever crosswalk_location.csv emits, read
    from that file, never written here as a range')."""
    classes = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = row["target_class"].strip()
            if c:
                classes.add(c)
    return sorted(classes)


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


def pack_cop(row, bitpos, null_episodes=None):
    v = 0
    had_null = False
    for flag, pos in bitpos.items():
        val = row.get(flag)
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


def episode_str(dur, act, loc, cop_enc):
    return "%d,%s,%s,%s;" % (dur, act, loc, cop_enc)


def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def pct(x, p):
    return float(np.percentile(np.array(x), p, method="linear"))


def main():
    print("4J COP packing RE-VERIFICATION (LOC-alphabet check on D-S3-1 / job 1252633)")
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

    loc_classes = load_loc_classes(CW_LOC)
    print()
    print("LOC classes (from crosswalk_location.csv target_class column, read live, %d distinct): %s"
          % (len(loc_classes), loc_classes))
    if sorted(loc_classes) != sorted(["at_home", "other_place", "private_transport",
                                       "public_transport"]):
        print("WARNING: LOC classes read from the crosswalk do not match the four expected by "
              "D-S2-3 -- proceeding with what was actually read, not the hard-coded expectation.")

    bitpos = load_bit_positions(CW_COP)
    print("bit_position (from crosswalk_copresence.csv, read live): %s" % bitpos)

    REP_LOC = "at_home"  # what "11" (the original script's fixed placeholder) actually maps to
    if REP_LOC not in loc_classes:
        print("FATAL: representative LOC class %r not among classes read from the crosswalk." % REP_LOC)
        sys.exit(1)

    print()
    print("-- diary skeleton (shared across all candidates, unchanged from 4thJ_cop_measure.py)")
    print("   DUR (25, multiples of 10, sum=%d): %s" % (sum(_DUR), _DUR))
    print("   ACT (25, 3-digit):                  %s" % _ACT)
    print("   per-episode COP integer v (0-63), v_i=(7i+3) mod 64: %s" % _COP_VALS)
    print("   representative episode uses DUR=%d ACT=%s LOC=%s v=%d"
          % (REP_DUR, REP_ACT, REP_LOC, REP_V))

    # -----------------------------------------------------------------
    # PART A -- in-situ worst-case sweep: LOC (4 classes) x COP (64 values) = 256 combinations,
    # at the representative DUR/ACT slot. This is the corrected version of the original script's
    # sweep, which only varied COP with LOC held fixed at a hard-coded placeholder.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART A -- in-situ worst-case sweep over LOC x COP (256 combinations per candidate)")

    part_a_results = []
    for name, enc_fn, desc in CANDIDATES:
        rep_encoded = enc_fn(REP_V)
        rep_str = episode_str(REP_DUR, REP_ACT, REP_LOC, rep_encoded)
        rep_n = n_tok(tok, rep_str)

        max_tok = -1
        argmax = None
        for loc in loc_classes:
            for v in range(64):
                s = episode_str(REP_DUR, REP_ACT, loc, enc_fn(v))
                t = n_tok(tok, s)
                if t > max_tok:
                    max_tok = t
                    argmax = (loc, v, s)

        print()
        print("CANDIDATE %s -- %s" % (name, desc))
        print("   representative episode (LOC=%s, v=%d): %r -> %d tokens" % (REP_LOC, REP_V, rep_str, rep_n))
        print("   worst case over LOC x COP (256 combos): %d tokens, at loc=%r v=%d, string=%r"
              % (max_tok, argmax[0], argmax[1], argmax[2]))
        part_a_results.append({"name": name, "rep_tokens": rep_n, "worst_tokens": max_tok,
                                "worst_loc": argmax[0], "worst_v": argmax[1]})

    # -----------------------------------------------------------------
    # PART B -- real diaries, median/p99 tokens/diary per candidate.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART B -- real diaries, median/p99 tokens/diary per candidate")

    cols = DIARY_KEY + ["episode_index", "duration_min", "act", "loc_class"] + SHARED_FLAGS
    print("reading %s, columns=%s" % (HARMONISED, cols))
    df = pd.read_parquet(HARMONISED, columns=cols)
    print("rows read: %d" % len(df))

    # -----------------------------------------------------------------
    # NA extent, measured on the full table before any sampling/Part B loop: per country per
    # cop_* flag, how many rows are null and how many distinct diaries are touched. This is the
    # finding behind jobs 1255143/1255174's crash -- reported, not just worked around. Local
    # diary-key series, not written back onto df, so nothing downstream in this function changes.
    # -----------------------------------------------------------------
    _diary_key_series = pd.Series(list(zip(df["country"], df["hid"], df["pid"], df["diary_day"])),
                                   index=df.index)
    print()
    print("=" * 78)
    print("NULL EXTENT of cop_* flags (measured before Part B, full harmonised.parquet)")
    print("%-8s %-16s %12s %18s" % ("country", "flag", "null_rows", "distinct_diaries"))
    for _country in sorted(df["country"].dropna().unique().tolist()):
        _cmask = df["country"] == _country
        for _flag in SHARED_FLAGS:
            _nullmask = _cmask & df[_flag].isna()
            _n_null = int(_nullmask.sum())
            _n_diaries = int(_diary_key_series[_nullmask].nunique()) if _n_null else 0
            print("%-8s %-16s %12d %18d" % (_country, _flag, _n_null, _n_diaries))
    _any_null_mask = df[SHARED_FLAGS].isna().any(axis=1)
    print("TOTAL rows with >=1 null cop_* flag: %d, distinct diaries touched: %d"
          % (int(_any_null_mask.sum()), int(_diary_key_series[_any_null_mask].nunique())))

    n_loc_null = int(df["loc_class"].isna().sum())
    obs_loc = sorted(df["loc_class"].dropna().unique().tolist())
    print("distinct loc_class values observed in real data: %s (null count: %d)" % (obs_loc, n_loc_null))
    unexpected = set(obs_loc) - set(loc_classes)
    if unexpected:
        print("WARNING: loc_class values observed in the data but NOT in crosswalk_location.csv's "
              "target_class column: %s" % unexpected)
    if n_loc_null > 0:
        print("WARNING: %d rows have a null loc_class -- these diaries will emit a Python 'None' "
              "string in the tuple unless handled; sentinel policy is NOT decided by this script "
              "(out of scope), episodes with null loc_class are DROPPED from the real-diary sample "
              "below and the drop count is reported, not silently included." % n_loc_null)

    df_clean = df.dropna(subset=["loc_class"]).copy()
    df_clean["_diary_key"] = list(zip(df_clean["country"], df_clean["hid"], df_clean["pid"],
                                       df_clean["diary_day"]))

    # Diaries are only usable whole -- if any episode in a diary was dropped for null loc_class,
    # that diary is incomplete and excluded from sampling (never a partial diary string).
    diary_full = df.assign(_diary_key=list(zip(df["country"], df["hid"], df["pid"], df["diary_day"])))
    full_ep_count = diary_full.groupby("_diary_key").size()
    clean_ep_count = df_clean.groupby("_diary_key").size()
    complete_diaries = clean_ep_count[clean_ep_count.index.isin(full_ep_count.index) &
                                       (clean_ep_count == full_ep_count.reindex(clean_ep_count.index))]
    usable_keys = complete_diaries.index.to_numpy()
    print("diaries total=%d, usable (no dropped episodes)=%d, excluded for a null-LOC episode=%d"
          % (len(full_ep_count), len(usable_keys), len(full_ep_count) - len(usable_keys)))

    rng = np.random.default_rng(SEED)
    n_sample = min(N_SAMPLE_DIARIES, len(usable_keys))
    sample_keys = set(rng.choice(usable_keys, size=n_sample, replace=False).tolist())
    print("sampling %d diaries (seed=%d, requested %d, usable %d)"
          % (n_sample, SEED, N_SAMPLE_DIARIES, len(usable_keys)))

    sample_df = df_clean[df_clean["_diary_key"].isin(sample_keys)].sort_values(DIARY_KEY + ["episode_index"])
    print("episodes in sample: %d" % len(sample_df))
    country_counts = sample_df.drop_duplicates(subset=DIARY_KEY)["country"].value_counts().to_dict()
    print("sampled diaries per country: %s" % country_counts)
    loc_prevalence = sample_df["loc_class"].value_counts(normalize=True).to_dict()
    print("loc_class prevalence in the sample: %s" % {k: round(v, 4) for k, v in loc_prevalence.items()})

    grouped = list(sample_df.groupby(DIARY_KEY, sort=False))
    results = {name: [] for name, _, _ in CANDIDATES}
    null_flag_episodes = set()
    for _, g in grouped:
        g = g.sort_values("episode_index")
        for name, enc_fn, _ in CANDIDATES:
            parts = []
            for _, row in g.iterrows():
                cop_v = pack_cop(row, bitpos, null_flag_episodes)
                dur = int(row["duration_min"])
                act = str(row["act"]).strip()
                loc = row["loc_class"]
                parts.append(episode_str(dur, act, loc, enc_fn(cop_v)))
            d_str = "".join(parts)
            results[name].append(n_tok(tok, d_str))

    print()
    print("episodes in Part B sample with >=1 null cop_* flag (treated as bit-unset=0, NOT dropped): "
          "%d" % len(null_flag_episodes))
    print()
    print("%-24s %8s %8s %8s %8s" % ("candidate", "n", "median", "p99", "max"))
    summary = {}
    for name, _, _ in CANDIDATES:
        vals = results[name]
        med = statistics.median(vals)
        p99 = pct(vals, 99)
        mx = max(vals)
        summary[name] = (med, p99, mx)
        print("%-24s %8d %8.1f %8.1f %8d" % (name, len(vals), med, p99, mx))

    print()
    print("G3.5 pre-registered band: median <= 220, p99 <= 400")
    for name, _, _ in CANDIDATES:
        med, p99, mx = summary[name]
        med_ok = med <= 220
        p99_ok = p99 <= 400
        print("candidate %-24s median %.1f (%s), p99 %.1f (%s)"
              % (name, med, "within band" if med_ok else "EXCEEDS band",
                 p99, "within band" if p99_ok else "EXCEEDS band"))

    # -----------------------------------------------------------------
    # SUMMARY -- compare against the accepted D-S3-1 result and state whether the ranking survives.
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("SUMMARY -- accepted D-S3-1 result (job 1252633, wrong-alphabet LOC placeholders) vs this "
          "re-verification (correct 4-class LOC alphabet)")
    accepted = {
        "1_decimal_0-63": (8, 200),
        "2_six_chars": (9, 225),
        "3_two_octal": (8, 200),
        "4_two_hex": (9, 210),
        "5_baseline_csv_bits": (18, 450),
    }
    print("%-24s %14s %14s %10s %10s %10s" % ("candidate", "accepted_worst", "accepted_diary",
                                                "new_worst", "new_median", "new_p99"))
    for r in part_a_results:
        name = r["name"]
        acc_worst, acc_diary = accepted[name]
        med, p99, mx = summary[name]
        print("%-24s %14d %14d %10d %10.1f %10.1f"
              % (name, acc_worst, acc_diary, r["worst_tokens"], med, p99))

    print()
    print("D-S3-1's decision picked candidate 1 (decimal) over candidate 2 (six chars) because "
          "candidate 2's accepted diary cost (225) exceeded G3.5's median band (220); candidates 1 "
          "and 3 tied for cheapest. RANKING CHECK (read the table above): does candidate 1 (or the "
          "1/3 tie) still sit at or below every other candidate's new_median, and does candidate 2 "
          "still exceed 220 -- or has the ranking changed under the corrected LOC alphabet? This "
          "script does not decide -- report the table to the author.")

    print()
    print("diaries dropped for a null loc_class episode: see 'excluded for a null-LOC episode' line above")
    print("Reference: original (wrong-alphabet) measurement, job 1252633, "
          "outputs_step3/cop_packing_measurement.md.")


if __name__ == "__main__":
    main()
