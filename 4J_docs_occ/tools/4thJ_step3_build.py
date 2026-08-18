#!/usr/bin/env python
"""
4J Step 3, work items 3.3/3.4/3.5: build the corpus.

Runs (in order), on the FULL 2,024,068-row / 73,254-diary `harmonised.parquet`,
never a sample:

  1. Load the table, print rows/diaries read per country, assert them against
     the pre-registered totals (acceptance test 6). No filtering step exists in
     this loader, so "dropped" is 0 by construction -- printed anyway.
  2. For every diary: encode with `encoder.encode_diary`, decode with
     `decoder.decode_record`, and compare the decoded structure field-by-field
     against a structure built directly from the source rows (NOT re-derived
     through the encoder) -- the B1 100%-round-trip requirement. Any mismatch
     or any EncodeError/DecodeError is a FAIL; the corpus is NOT emitted if the
     round-trip is not 100%.
  3. Reconcile the explicit-null counts (D-S3-4 `unknown`, D-S3-5 `COP==64`)
     against harmonised.parquet, per country, against the pre-registered hard
     numbers (acceptance test 7).
  4. Split by respondent (country, hid, pid), 90/10, seed 42 -- ASSUMPTION, not
     specified anywhere in the task doc; recorded as such.
  5. Run the four tokenizer assertions (work item 3.4) over the FULL corpus.
  6. Emit `outputs_step3/corpus.jsonl` and `outputs_step3/token_stats.md`.

Tokenizer: allenai/OLMo-2-0425-1B, stated stand-in for the 7B backbone's
OLMo/dolma2 vocab -- a premise of this task, not re-derived here.

Run with sbatch. Never on the login node.
"""

import json
import statistics
import sys
import traceback

import numpy as np
import pandas as pd

sys.path.insert(0, "/speed-scratch/o_iseri")
import encoder as enc
import decoder as dec

MODEL = "allenai/OLMo-2-0425-1B"
NOTE = ("stand-in for allenai/Olmo-3-1025-7B: identical dolma2 BPE vocabulary, "
        "used here only because it is far smaller to download -- vocabulary identity is a premise "
        "of this task, not re-derived here")
EXPECTED_VOCAB_SIZE = 100278  # observed in job 1255237; asserted unchanged, never added to (RL05)

HARMONISED = "/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet"
CW_COP = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_copresence.csv"
CW_ACT2 = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_activity_secondary.csv"

OUT_CORPUS = "/speed-scratch/o_iseri/4J_step3_corpus.jsonl"
OUT_TOKEN_STATS = "/speed-scratch/o_iseri/4J_step3_token_stats.txt"

SPLIT_SEED = 42
HELDOUT_FRACTION = 0.10  # ASSUMPTION -- not specified anywhere in the task doc

# Pre-registered totals (B0 / acceptance test 6), ES / IT / UK order
EXPECTED_ROWS = {"es": 446547, "it": 1010140, "uk": 567381}
EXPECTED_DIARIES = {"es": 19140, "it": 38260, "uk": 15854}
EXPECTED_TOTAL_ROWS = 2024068
EXPECTED_TOTAL_DIARIES = 73254

# Pre-registered explicit-null reconciliation (acceptance test 7), ES / IT / UK order
EXPECTED_UNKNOWN_LOC = {"es": 0, "it": 8007, "uk": 16793}
EXPECTED_COP64 = {"es": 0, "it": 0, "uk": 68464}
EXPECTED_ACT000 = {"es": 3786, "it": 333, "uk": 4590}  # D-S3-9

READ_COLS = enc.DIARY_KEY + [
    "episode_index", "duration_min", "act", "act2", "loc_class",
] + enc.SHARED_FLAGS + [
    "strat_age_band", "strat_sex", "strat_hh_type", "strat_econ_status", "strat_day_type",
]  # D-S3-11: `mode` and `scheme` are no longer read -- they are not serialised.

MAX_FAILURES_PRINTED = 100


def fail(msg):
    print("FATAL: %s" % msg)
    sys.exit(1)


def canonical_from_source(prefix_row, episode_rows, bitpos):
    """Build the same-shaped structure decode_record would return, directly
    from the source rows -- not by round-tripping through the encoder. This is
    the independent expectation the 100%-round-trip check is compared against."""
    prefix = {
        "country": enc.enc_country(prefix_row["country"]),
        "strat_age_band": str(prefix_row["strat_age_band"]).strip(),  # decoder returns the ORIGINAL hyphenated label
        "strat_sex": str(prefix_row["strat_sex"]).strip().lower(),
        "strat_hh_type": str(prefix_row["strat_hh_type"]).strip().lower(),
        "strat_econ_status": str(prefix_row["strat_econ_status"]).strip().lower(),
        "strat_day_type": str(prefix_row["strat_day_type"]).strip().lower(),
        # D-S3-11: `mode` and `scheme` dropped from the prefix.
    }
    episodes = []
    for r in episode_rows:
        act2_val = None if (pd.isna(r["act2"]) or r["act2"] == "") else str(r["act2"]).strip()
        loc_val = None if pd.isna(r["loc_class"]) else str(r["loc_class"]).strip()
        null_flags = [f for f in enc.SHARED_FLAGS if pd.isna(r[f])]
        if len(null_flags) == 6:
            cop_val = None
        else:
            cop_val = {flag: bool(int(r[flag]) != 0) for flag in enc.SHARED_FLAGS}
        act_val = None if pd.isna(r["act"]) else str(r["act"]).strip()  # D-S3-9: "000" decodes to None
        episodes.append({
            "duration_min": int(r["duration_min"]),
            "act": act_val,
            "act2": act2_val,
            "loc_class": loc_val,
            "cop": cop_val,
        })
    return {"prefix": prefix, "episodes": episodes}


def structures_equal(a, b):
    if a["prefix"] != b["prefix"]:
        return False, "prefix"
    if len(a["episodes"]) != len(b["episodes"]):
        return False, "episode_count"
    for i, (ea, eb) in enumerate(zip(a["episodes"], b["episodes"])):
        if ea != eb:
            return False, "episode[%d]: %r != %r" % (i, ea, eb)
    return True, None


def main():
    print("4J Step 3 build: encoder/decoder round-trip, tokenizer assertions, corpus emission")
    print("=" * 78)
    print("pandas %s, numpy %s" % (pd.__version__, np.__version__))

    bitpos = enc.load_bit_positions(CW_COP)
    print("bit_position (from crosswalk_copresence.csv, read live): %s" % bitpos)
    legal_act2 = enc.load_legal_act2_codes(CW_ACT2)
    print("legal ACT2 target codes (from crosswalk_activity_secondary.csv, %d distinct)" % len(legal_act2))

    print()
    print("reading %s, columns=%s" % (HARMONISED, READ_COLS))
    df = pd.read_parquet(HARMONISED, columns=READ_COLS)
    df["country"] = df["country"].astype(str).str.lower()  # D-S2-16, lowercase on read
    print("rows read (total): %d" % len(df))

    # ---- V3.i-spirit loader accounting: read/dropped per country, before anything else ----
    print()
    print("=" * 78)
    print("LOADER ACCOUNTING (per country, before any encoding)")
    all_ok = True
    for c in ("es", "it", "uk"):
        sub = df[df["country"] == c]
        n_rows = len(sub)
        n_diaries = sub[enc.DIARY_KEY].drop_duplicates().shape[0]
        dropped_rows = 0  # no filtering step exists in this loader
        dropped_diaries = 0
        print("country=%s rows_read=%d dropped_rows=%d diaries_read=%d dropped_diaries=%d"
              % (c, n_rows, dropped_rows, n_diaries, dropped_diaries))
        if n_rows != EXPECTED_ROWS[c] or n_diaries != EXPECTED_DIARIES[c]:
            print("  MISMATCH: expected rows=%d diaries=%d" % (EXPECTED_ROWS[c], EXPECTED_DIARIES[c]))
            all_ok = False
    total_rows = len(df)
    total_diaries = df[enc.DIARY_KEY].drop_duplicates().shape[0]
    print("TOTAL rows=%d diaries=%d" % (total_rows, total_diaries))
    if total_rows != EXPECTED_TOTAL_ROWS or total_diaries != EXPECTED_TOTAL_DIARIES:
        all_ok = False
    if not all_ok:
        fail("loader accounting does not match the pre-registered totals -- STOP, do not proceed")
    print("Loader accounting: MATCHES pre-registered totals exactly. Dropped rows/diaries: 0/0.")

    # ---- main encode/decode/compare loop over every diary ----
    print()
    print("=" * 78)
    print("ENCODE/DECODE ROUND-TRIP (100%% of %d diaries)" % total_diaries)

    rng = np.random.default_rng(SPLIT_SEED)
    respondents = df[enc.RESPONDENT_KEY].drop_duplicates().reset_index(drop=True)
    n_resp = len(respondents)
    shuffled_idx = rng.permutation(n_resp)
    n_heldout = int(round(n_resp * HELDOUT_FRACTION))
    heldout_resp = set(
        tuple(x) for x in respondents.iloc[shuffled_idx[:n_heldout]][enc.RESPONDENT_KEY].itertuples(index=False, name=None)
    )
    print("respondents: %d, heldout fraction=%.2f (seed=%d) -> %d heldout respondents, %d train"
          % (n_resp, HELDOUT_FRACTION, SPLIT_SEED, len(heldout_resp), n_resp - len(heldout_resp)))

    records = []  # (country, hid, pid, diary_day, split, text)
    n_diary_ok = 0
    n_diary_fail = 0
    failures = []
    unknown_loc_count = {"es": 0, "it": 0, "uk": 0}
    cop64_count = {"es": 0, "it": 0, "uk": 0}
    act000_count = {"es": 0, "it": 0, "uk": 0}  # D-S3-9

    for key, g in df.groupby(enc.DIARY_KEY, sort=False):
        country, hid, pid, diary_day = key
        g = g.sort_values("episode_index")
        rows = g.to_dict("records")
        prefix_row = rows[0]
        try:
            text = enc.encode_diary(prefix_row, rows, bitpos, legal_act2)
            decoded = dec.decode_record(text, bitpos)
            expected = canonical_from_source(prefix_row, rows, bitpos)
            ok, where = structures_equal(decoded, expected)
            if not ok:
                raise AssertionError("round-trip mismatch at %s" % where)
        except Exception as exc:  # noqa: BLE001 -- deliberately broad: any diary that fails is recorded, not silently skipped
            n_diary_fail += 1
            if len(failures) < MAX_FAILURES_PRINTED:
                failures.append("%s: %s: %s" % (key, type(exc).__name__, exc))
            continue
        n_diary_ok += 1
        for r in rows:
            if pd.isna(r["loc_class"]):
                unknown_loc_count[country] += 1
            null_flags = sum(1 for f in enc.SHARED_FLAGS if pd.isna(r[f]))
            if null_flags == 6:
                cop64_count[country] += 1
            if pd.isna(r["act"]):
                act000_count[country] += 1
        split = "heldout" if (country, hid, pid) in heldout_resp else "train"
        records.append((country, hid, pid, diary_day, split, text))

    print("diaries OK: %d, diaries FAILED: %d" % (n_diary_ok, n_diary_fail))
    if failures:
        print("first %d failures:" % len(failures))
        for f in failures:
            print("  " + f)

    if n_diary_fail > 0:
        fail("round-trip is NOT 100%% (%d/%d diaries failed) -- corpus NOT emitted. Fix the encoder/"
             "decoder and re-run; do not emit a partial corpus." % (n_diary_fail, total_diaries))

    print("ROUND-TRIP: 100%% exact on %d/%d diaries." % (n_diary_ok, total_diaries))

    # ---- explicit-null reconciliation (acceptance test 7) ----
    print()
    print("=" * 78)
    print("EXPLICIT-NULL RECONCILIATION (per country)")
    null_ok = True
    for c in ("es", "it", "uk"):
        print("country=%s unknown_loc=%d (expected %d) cop64=%d (expected %d) act000=%d (expected %d)"
              % (c, unknown_loc_count[c], EXPECTED_UNKNOWN_LOC[c], cop64_count[c], EXPECTED_COP64[c],
                 act000_count[c], EXPECTED_ACT000[c]))
        if (unknown_loc_count[c] != EXPECTED_UNKNOWN_LOC[c] or cop64_count[c] != EXPECTED_COP64[c]
                or act000_count[c] != EXPECTED_ACT000[c]):
            null_ok = False
    if not null_ok:
        fail("explicit-null reconciliation does not match the pre-registered hard numbers -- STOP")
    print("Explicit-null reconciliation: MATCHES pre-registered numbers exactly.")

    # ---- split integrity ----
    train_resp = set((c, h, p) for (c, h, p, d, s, t) in records if s == "train")
    heldout_resp_actual = set((c, h, p) for (c, h, p, d, s, t) in records if s == "heldout")
    intersection = train_resp & heldout_resp_actual
    print()
    print("SPLIT INTEGRITY: train respondents=%d, heldout respondents=%d, intersection=%d"
          % (len(train_resp), len(heldout_resp_actual), len(intersection)))
    if intersection:
        fail("respondent split intersection is non-zero: %d" % len(intersection))

    # ---- tokenizer ----
    print()
    print("=" * 78)
    print("TOKENIZER ASSERTIONS (work item 3.4), full corpus")
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
    tok = AutoTokenizer.from_pretrained(MODEL)
    vocab_len = len(tok)
    print("len(tokenizer) = %d (expected %d, RL05: no tokens added)" % (vocab_len, EXPECTED_VOCAB_SIZE))
    if vocab_len != EXPECTED_VOCAB_SIZE:
        fail("len(tokenizer) changed: %d != %d -- a token was added to the vocabulary" % (vocab_len, EXPECTED_VOCAB_SIZE))

    # ---- D-S3-9: explicit token-count check for the "000" null-act sentinel ----
    act000_ids = tok.encode(enc.ACT_NULL_CODE, add_special_tokens=False)
    print("token count of literal ACT code %r (D-S3-9 null-act sentinel): %d"
          % (enc.ACT_NULL_CODE, len(act000_ids)))
    if len(act000_ids) != 1:
        fail("ACT code '000' does not tokenize to exactly 1 token (got %d ids: %s) -- G3.4 requires "
             "every 3-digit ACT code to be exactly 1 token. The code must change to another "
             "verified-free 3-digit string (998 and 999 are both already taken); the gate does not "
             "change. STOPPING per the task brief, corpus NOT emitted." % (len(act000_ids), act000_ids))

    # D-S3-11 removed MODE and SCHEME, so there is no longer a constant-field
    # report to print. What replaces it is the per-field prefix vocabulary, which
    # is what D-S3-12 re-pointed G3.9 at. Diagnostic only -- the gate is in the
    # battery, not here.
    for i, fname in enumerate(enc.PREFIX_FIELDS):
        vals = sorted(set(r[5].split("|", 1)[0].split(",")[i] for r in records))
        print("distinct %s values in corpus: %d %s" % (fname, len(vals), vals))

    distinct_acts = sorted(
        set(str(v).strip() for v in df["act"].dropna().unique().tolist()) | {enc.ACT_NULL_CODE}
    )  # "000" (D-S3-9) is a real ACT value in the emitted corpus though absent from the source column
    print("distinct ACT codes in corpus: %d" % len(distinct_acts))
    bad_act = []
    for a in distinct_acts:
        ids = tok.encode(a, add_special_tokens=False)
        if len(ids) != 1:
            bad_act.append((a, len(ids)))
    print("ACT codes NOT encoding to exactly 1 token: %d / %d" % (len(bad_act), len(distinct_acts)))
    if bad_act:
        print("  examples: %s" % bad_act[:20])

    n_eor_ok = 0
    n_roundtrip_ok = 0
    n_char_roundtrip_ok = 0  # D-S3-13
    n_over_1024 = 0
    tok_counts = []
    per_country_counts = {"es": [], "it": [], "uk": []}
    per_stratum_counts = {}

    for (country, hid, pid, diary_day, split, text) in records:
        if not text.endswith(enc.EOR):
            fail("record for %s does not end with %s (string level)" % ((country, hid, pid, diary_day), enc.EOR))
        ids = tok.encode(text, add_special_tokens=False)
        detok = tok.decode(ids)
        ids2 = tok.encode(detok, add_special_tokens=False)
        if ids2 == ids:
            n_roundtrip_ok += 1
        if detok == text:
            n_char_roundtrip_ok += 1  # D-S3-13: the check that is NOT a tautology
        if detok.endswith(enc.EOR):
            n_eor_ok += 1
        n_tok = len(ids)
        tok_counts.append(n_tok)
        per_country_counts[country].append(n_tok)
        if n_tok > 1024:
            n_over_1024 += 1
        prefix_fields = text.split("|", 1)[0].split(",")
        strat_keys = {
            "strat_age_band": prefix_fields[1], "strat_sex": prefix_fields[2],
            "strat_hh_type": prefix_fields[3], "strat_econ_status": prefix_fields[4],
            "strat_day_type": prefix_fields[5],
        }
        for field, val in strat_keys.items():
            per_stratum_counts.setdefault(field, {}).setdefault(val, []).append(n_tok)

    n_records = len(records)
    print()
    print("tokenize(detokenize(ids)) == ids: %d / %d  (idempotency -- true of any sane tokenizer, "
          "D-S3-13)" % (n_roundtrip_ok, n_records))
    print("detokenize(tokenize(text)) == text: %d / %d  (CHARACTER-level, the check G3.3 became)"
          % (n_char_roundtrip_ok, n_records))
    print("detokenized text ends with <eor>: %d / %d" % (n_eor_ok, n_records))
    print("records exceeding 1024 tokens (the SUPERSEDED G3.5 max; band is 1200 since D-S3-10, diagnostic only): %d / %d" % (n_over_1024, n_records))

    def pct(x, p):
        return float(np.percentile(np.array(x), p, method="linear"))

    med = statistics.median(tok_counts)
    p99 = pct(tok_counts, 99)
    mx = max(tok_counts)
    print()
    print("FULL-RECORD token stats (prefix + episodes + <eor>), n=%d: median=%.1f p99=%.1f max=%d"
          % (n_records, med, p99, mx))
    print("G3.5 current band: median<=300 p99<=700 max<=1200  (max raised 1024 -> 1200 by the author, D-S3-10)")
    print("median %s, p99 %s, max %s"
          % ("within band" if med <= 300 else "EXCEEDS band (upper end)",
             "within band" if p99 <= 700 else "EXCEEDS band (upper end)",
             "within band" if mx <= 1200 else "EXCEEDS band (upper end)"))
    print("NOTE: the 238.0/580.0/751 baseline job 1255237 measured was the BARE episode-tuple form, "
          "no prefix, no <eor>. This figure includes both. Not directly comparable; flagged for the "
          "author, reported as the real number that matters for RL05's 2048-token packing window.")

    print()
    print("Per-country token stats:")
    for c in ("es", "it", "uk"):
        vals = per_country_counts[c]
        print("  %s n=%d median=%.1f p99=%.1f max=%d" % (c, len(vals), statistics.median(vals), pct(vals, 99), max(vals)))

    print()
    print("Per-stratum token stats:")
    for field, groups in per_stratum_counts.items():
        for val, vals in sorted(groups.items()):
            print("  %s=%s n=%d median=%.1f p99=%.1f max=%d"
                  % (field, val, len(vals), statistics.median(vals), pct(vals, 99), max(vals)))

    # ---- emit ----
    print()
    print("=" * 78)
    print("WRITING %s" % OUT_CORPUS)
    with open(OUT_CORPUS, "w", encoding="utf-8") as fh:
        for (country, hid, pid, diary_day, split, text) in records:
            fh.write(json.dumps({
                "country": country, "hid": hid, "pid": pid, "diary_day": diary_day,
                "split": split, "text": text,
            }) + "\n")
    print("wrote %d records" % n_records)

    print("WRITING %s" % OUT_TOKEN_STATS)
    with open(OUT_TOKEN_STATS, "w", encoding="utf-8") as fh:
        fh.write("n_records=%d median=%.1f p99=%.1f max=%d\n" % (n_records, med, p99, mx))
        fh.write("vocab_len=%d\n" % vocab_len)
        fh.write("tokenizer_roundtrip_ok=%d/%d\n" % (n_roundtrip_ok, n_records))
        fh.write("eor_ok=%d/%d\n" % (n_eor_ok, n_records))
        fh.write("act_1token_bad=%d/%d\n" % (len(bad_act), len(distinct_acts)))
        fh.write("act000_token_count=%d\n" % len(act000_ids))
        fh.write("over_1024=%d/%d\n" % (n_over_1024, n_records))
        for c in ("es", "it", "uk"):
            fh.write("country=%s unknown_loc=%d cop64=%d act000=%d\n"
                      % (c, unknown_loc_count[c], cop64_count[c], act000_count[c]))
        for c in ("es", "it", "uk"):
            vals = per_country_counts[c]
            fh.write("country=%s n=%d median=%.1f p99=%.1f max=%d\n"
                      % (c, len(vals), statistics.median(vals), pct(vals, 99), max(vals)))
        for field, groups in per_stratum_counts.items():
            for val, vals in sorted(groups.items()):
                fh.write("stratum=%s value=%s n=%d median=%.1f p99=%.1f max=%d\n"
                          % (field, val, len(vals), statistics.median(vals), pct(vals, 99), max(vals)))

    print()
    print("=" * 78)
    print("DONE.")
    print("n_diaries_ok=%d n_records_emitted=%d bad_act_1token=%d tokenizer_roundtrip_ok=%d/%d "
          "eor_ok=%d/%d over_1024=%d median=%.1f p99=%.1f max=%d"
          % (n_diary_ok, n_records, len(bad_act), n_roundtrip_ok, n_records, n_eor_ok, n_records,
             n_over_1024, med, p99, mx))


if __name__ == "__main__":
    main()
