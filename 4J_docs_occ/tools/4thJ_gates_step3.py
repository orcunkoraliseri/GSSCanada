#!/usr/bin/env python
"""
4J Step 3 -- independent gate battery. Sixteen gates (G3.1-G3.16, no G3.13-numbered-out-of-order
gap -- there is no G3.13 skip; see below), twenty-one perturbations, nine vacuity guards
(V3.a-V3.i), one coverage clause.

Governing spec, read verbatim: 4J_docs_occ/Step3_docs/4thJ_03_serialisation_val.md.
Record format, read verbatim: 4J_docs_occ/Step3_docs/4thJ_03_serialisation.md.

This script is the EMPLOYEE's own audit of Step 3's build (encoder.py/decoder.py, written by a
DIFFERENT employee). Design rules that shape every function below:

  * G3.1-G3.12, G3.14(a) and G3.15(a) MAY use decoder.py (imported as `dec`) -- that is the whole
    point of those gates: they read the encoder's output through the decoder we wrote, so they
    SHARE AN ANCESTOR with the encoder and cannot see a defect the encoder and decoder agree on.
  * G3.13, G3.14(b), G3.15(b) and G3.16 MUST NOT import anything from encoder.py or decoder.py.
    Each is implemented with its OWN minimal parser (`indep_parse`, below) and its OWN crosswalk
    loaders (`load_bitpos_independent`, `load_loc_alphabet_independent`,
    `load_act2_codes_independent`), and G3.15(b)/G3.16/G3.13 each read harmonised.parquet FRESH
    (a standalone `pd.read_parquet` call inside their own function, not a cache built elsewhere).
  * No threshold, perturbation or gate is ever adjusted because a result is unwelcome. A gate that
    fails is reported as FAILED, with evidence. DID NOT FIRE is reported as DID NOT FIRE. A
    perturbation that turns out to move a gate the val doc says should "stay clean" -- because the
    SHIPPED decoder is stricter than the val doc's narrative assumed -- is reported as a finding.

Run with sbatch. Never on the login node.
"""

import argparse
import csv
import json
import os
import random
import re
import statistics
import sys
import time
import zlib
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, "/speed-scratch/o_iseri")
import decoder as dec  # noqa: E402  -- used ONLY by the gates whose spec allows sharing ancestry

# ---------------------------------------------------------------------------
# Frozen record shape, DUPLICATED here deliberately (never imported) so the
# four independent gates (G3.13, G3.14(b), G3.15(b), G3.16) share no code
# with encoder.py/decoder.py at all.
# ---------------------------------------------------------------------------
# D-S3-11 (author, 2026-08-17): `mode` and `scheme` REMOVED. Six fields, not eight.
PREFIX_FIELDS = ["country", "strat_age_band", "strat_sex", "strat_hh_type",
                  "strat_econ_status", "strat_day_type"]
PREFIX_SEP = ","
PREFIX_BODY_SEP = "|"
EOR = "<eor>"
SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]
LOC_UNKNOWN = "unknown"
COP_NOT_COLLECTED = 64
ACT_NULL_CODE = "000"
DIARY_KEY = ["country", "hid", "pid", "diary_day"]
RESPONDENT_KEY = ["country", "hid", "pid"]

# V3.c: digits, comma, semicolon, lowercase a-z, underscore, hyphen, plus,
# the prefix delimiters (| and ,), and the four extra characters <eor> needs
# (e, o, r already in a-z; < and > are the only new ones). No whitespace.
ALPHABET_CHARS = set("0123456789abcdefghijklmnopqrstuvwxyz,;_-+|<>")

MODEL = "allenai/OLMo-2-0425-1B"
EXPECTED_VOCAB_SIZE = 100278
# D-S3-13 (author, 2026-08-17): the swap partner MOVED off `gpt2`. G3.3 is now a
# CHARACTER-level round trip, and gpt2 is byte-level and lossless, so it would
# round-trip characters perfectly and leave the re-specified gate green a second
# time -- reproducing the exact defect being repaired. `bert-base-uncased`
# normalises (strips case and accents), so it fells the gate. Supersedes
# Decision 8 of `impl/2026-08-17_step3-gates.md` for this row only.
SWAP_MODEL = "bert-base-uncased"

EXPECTED_ROWS = {"es": 446547, "it": 1010140, "uk": 567381}
EXPECTED_DIARIES = {"es": 19140, "it": 38260, "uk": 15854}
EXPECTED_TOTAL_ROWS = 2024068
EXPECTED_TOTAL_DIARIES = 73254
EXPECTED_UNKNOWN_LOC = {"es": 0, "it": 8007, "uk": 16793}
EXPECTED_COP64 = {"es": 0, "it": 0, "uk": 68464}
EXPECTED_ACT000 = {"es": 3786, "it": 333, "uk": 4590}

G35_MEDIAN_MAX = 300
G35_P99_MAX = 700
G35_MAX_MAX = 1200

READ_COLS = DIARY_KEY + [
    "episode_index", "duration_min", "act", "act2", "loc_class",
] + SHARED_FLAGS + [
    "strat_age_band", "strat_sex", "strat_hh_type", "strat_econ_status", "strat_day_type",
]  # D-S3-11: `mode` and `scheme` no longer read -- they are not serialised.

PERTURBATION_NAMES = [
    "drop_loc_decoder", "merge_episodes", "tokenizer_swap", "zero_pad_act4",
    "inject_150ep_diary", "strip_eor_1pct", "blank_prefix_field10",
    "assert_flag_not_recorded", "national_raw_hh_type_it", "add_year2013",
    "split_by_diary", "add_tokens_act311", "zero_pad_cop2",
    "reverse_bitorder", "act2_98_fill", "loader_drop_act2_italy",
    "loader_drop_it_null_loc", "loader_drop_uk_null_cop", "loader_drop_es_null_act",
    "spell_unknown_two_ways", "null_perturbation",
]
assert len(PERTURBATION_NAMES) == 21, len(PERTURBATION_NAMES)


def log(msg):
    print(msg, flush=True)


def fail_msg(msg):
    print("GUARD-FAIL: %s" % msg, flush=True)


# ---------------------------------------------------------------------------
# Independent minimal parser -- used by G3.2, G3.6, G3.7, G3.9, G3.10,
# G3.13, G3.14(a), G3.14(b), G3.15(a), G3.15(b), G3.16, V3.a, V3.c, V3.h.
# Deliberately NOT the decoder: no semantic null-mapping, just field splitting.
# ---------------------------------------------------------------------------
def indep_parse(text):
    if not text.endswith(EOR):
        raise ValueError("record does not end with %r" % EOR)
    body = text[: -len(EOR)]
    if PREFIX_BODY_SEP not in body:
        raise ValueError("no %r prefix/body separator" % PREFIX_BODY_SEP)
    prefix_str, ep_str = body.split(PREFIX_BODY_SEP, 1)
    prefix_fields = prefix_str.split(PREFIX_SEP)
    if not ep_str.endswith(";"):
        raise ValueError("episode block does not end with ';'")
    pieces = ep_str.split(";")
    if pieces[-1] != "":
        raise ValueError("trailing piece not empty: %r" % pieces[-1])
    episodes = []
    for p in pieces[:-1]:
        f = p.split(",")
        if len(f) != 5:
            raise ValueError("episode has %d comma-fields, expected 5: %r" % (len(f), p))
        episodes.append(tuple(f))  # (dur_s, act, act2, loc, cop_s)
    if not episodes:
        raise ValueError("zero episodes")
    return prefix_fields, episodes


def load_bitpos_independent(path):
    positions = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            flag = row["shared_flag"]
            if flag in SHARED_FLAGS and flag not in positions:
                positions[flag] = int(row["bit_position"])
    return positions


def load_loc_alphabet_independent(path):
    classes = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = row["target_class"].strip()
            if c:
                classes.add(c)
    return classes | {LOC_UNKNOWN}


def load_act2_codes_independent(path):
    codes = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = row["target_code_2d"].strip()
            if c:
                codes.add(c)
    return codes


def reverse_bits_6(v):
    return int(format(v, "06b")[::-1], 2)


def pctl(values, p):
    return float(np.percentile(np.array(values), p, method="linear"))


# ---------------------------------------------------------------------------
# Corpus I/O
# ---------------------------------------------------------------------------
def read_corpus(path):
    records = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_corpus(records, path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


# ---------------------------------------------------------------------------
# harmonised.parquet loading + canonical index (built ONCE, reused for every
# baseline/perturbation run -- none of the 21 perturbations mutate
# harmonised.parquet, only the corpus copy, so this is safe and matches
# "G3.15(b)/G3.16 read the parquet fresh" being about not deriving from the
# corpus, not about re-reading the file from a cold cache every single time).
# ---------------------------------------------------------------------------
def load_harmonised(path):
    df = pd.read_parquet(path, columns=READ_COLS)
    df["country"] = df["country"].astype(str).str.lower()
    return df


def check_v3i(df):
    """Loader accounting guard on THIS BATTERY's own parquet read (see Decision 7
    in the implementation doc). Printed BEFORE any gate runs."""
    log("=" * 78)
    log("V3.i -- loader accounting on this battery's own harmonised.parquet read")
    ok = True
    for c in ("es", "it", "uk"):
        sub = df[df["country"] == c]
        n_rows = len(sub)
        n_diaries = sub[DIARY_KEY].drop_duplicates().shape[0]
        log("  country=%s rows=%d (expected %d) diaries=%d (expected %d)"
            % (c, n_rows, EXPECTED_ROWS[c], n_diaries, EXPECTED_DIARIES[c]))
        if n_rows != EXPECTED_ROWS[c] or n_diaries != EXPECTED_DIARIES[c]:
            ok = False
    total_rows = len(df)
    total_diaries = df[DIARY_KEY].drop_duplicates().shape[0]
    log("  TOTAL rows=%d (expected %d) diaries=%d (expected %d)"
        % (total_rows, EXPECTED_TOTAL_ROWS, total_diaries, EXPECTED_TOTAL_DIARIES))
    if total_rows != EXPECTED_TOTAL_ROWS or total_diaries != EXPECTED_TOTAL_DIARIES:
        ok = False
    verdict = "PASS" if ok else "FAIL"
    log("V3.i verdict: %s" % verdict)
    return verdict


def check_v3g(crosswalks_dir):
    log("=" * 78)
    log("V3.g -- per-country matched-key check, lowercased join, on Step 2 crosswalks")
    targets = [
        ("crosswalk_location.csv", "country"),
        ("crosswalk_strata.csv", "country"),
        ("crosswalk_activity_secondary.csv", "country"),
        ("crosswalk_copresence.csv", "country"),
    ]
    ok = True
    results = {}
    for fname, col in targets:
        path = os.path.join(crosswalks_dir, fname)
        counts = Counter()
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                c = row[col].strip().lower()
                if c in ("es", "it", "uk"):
                    counts[c] += 1
        results[fname] = dict(counts)
        log("  %s: %s" % (fname, dict(counts)))
        for c in ("es", "it", "uk"):
            if counts.get(c, 0) == 0:
                ok = False
                fail_msg("%s has zero matched rows for country=%s" % (fname, c))
    verdict = "PASS" if ok else "FAIL"
    log("V3.g verdict: %s" % verdict)
    return verdict, results


def check_v3e(bitpos):
    ok = True
    reasons = []
    if not bitpos:
        ok = False
        reasons.append("crosswalk_copresence.csv missing or unreadable / no bit_position column")
    else:
        missing = set(SHARED_FLAGS) - set(bitpos)
        if missing:
            ok = False
            reasons.append("missing bit_position for: %s" % sorted(missing))
        if sorted(bitpos.values()) != [0, 1, 2, 3, 4, 5]:
            ok = False
            reasons.append("bit positions not exactly {0..5}: %s" % bitpos)
    return ("PASS" if ok else "FAIL"), reasons


def check_v3c(records):
    bad_chars = set()
    n_bad_records = 0
    for r in records:
        t = r["text"]
        illegal = set(t) - ALPHABET_CHARS
        if illegal:
            bad_chars |= illegal
            n_bad_records += 1
    if bad_chars:
        fail_msg("V3.c illegal characters found: %s (in %d records)" % (sorted(bad_chars), n_bad_records))
        return "FAIL", sorted(bad_chars), n_bad_records
    return "PASS", [], 0


def build_canonical_index(df):
    """One structure per diary key, built directly from harmonised.parquet rows --
    NOT via the encoder. This is G3.1's independent expectation, exactly as
    4thJ_step3_build.py's canonical_from_source built it (re-derived here, not
    imported, since 4thJ_step3_build.py is a script, not a library)."""
    log("Building canonical index from harmonised.parquet (%d rows)..." % len(df))
    idx = {}
    for key, g in df.groupby(DIARY_KEY, sort=False):
        g = g.sort_values("episode_index")
        rows = g.to_dict("records")
        prefix_row = rows[0]
        prefix = {
            "country": str(prefix_row["country"]).strip().lower(),
            "strat_age_band": str(prefix_row["strat_age_band"]).strip(),
            "strat_sex": str(prefix_row["strat_sex"]).strip().lower(),
            "strat_hh_type": str(prefix_row["strat_hh_type"]).strip().lower(),
            "strat_econ_status": str(prefix_row["strat_econ_status"]).strip().lower(),
            "strat_day_type": str(prefix_row["strat_day_type"]).strip().lower(),
            # D-S3-11: `mode` and `scheme` are no longer part of the prefix.
        }
        episodes = []
        for r in rows:
            act2_val = None if (pd.isna(r["act2"]) or r["act2"] == "") else str(r["act2"]).strip()
            loc_val = None if pd.isna(r["loc_class"]) else str(r["loc_class"]).strip()
            null_flags = [f for f in SHARED_FLAGS if pd.isna(r[f])]
            if len(null_flags) == 6:
                cop_val = None
            else:
                cop_val = {flag: bool(int(r[flag]) != 0) for flag in SHARED_FLAGS}
            act_val = None if pd.isna(r["act"]) else str(r["act"]).strip()
            episodes.append({
                "duration_min": int(r["duration_min"]),
                "act": act_val, "act2": act2_val, "loc_class": loc_val, "cop": cop_val,
            })
        idx[key] = {"prefix": prefix, "episodes": episodes}
    log("Canonical index built: %d diaries." % len(idx))
    return idx


# ---------------------------------------------------------------------------
# G3.1 -- round-trip exactness. Uses decoder.py (ancestry with the encoder is
# the point). canonical_override / decode_bitpos_override / act2_absent_extra
# let one perturbation run simulate "the decoder also saw the defect" without
# forking decoder.py's code (see implementation-doc Decision 5).
# ---------------------------------------------------------------------------
def structures_equal(a, b):
    if a["prefix"] != b["prefix"]:
        return False, "prefix"
    if len(a["episodes"]) != len(b["episodes"]):
        return False, "episode_count %d!=%d" % (len(a["episodes"]), len(b["episodes"]))
    for i, (ea, eb) in enumerate(zip(a["episodes"], b["episodes"])):
        if ea != eb:
            return False, "episode[%d]: %r != %r" % (i, ea, eb)
    return True, None


def gate_g31(records, canonical_index, bitpos_true,
             canonical_override=None, decode_bitpos_override=None,
             act2_absent_extra=None, drop_loc=False):
    bitpos = decode_bitpos_override if decode_bitpos_override is not None else bitpos_true
    n_compared = 0
    n_ok = 0
    n_no_source = 0
    failures = []
    for r in records:
        key = (r["country"], r["hid"], r["pid"], r["diary_day"])
        canon = (canonical_override or canonical_index).get(key)
        if canon is None:
            n_no_source += 1
            continue
        n_compared += 1
        try:
            decoded = dec.decode_record(r["text"], bitpos)
        except Exception as exc:  # noqa: BLE001
            failures.append((key, "decode error: %s" % exc))
            continue
        if act2_absent_extra:
            for ep in decoded["episodes"]:
                if ep["act2"] in act2_absent_extra:
                    ep["act2"] = None
        if drop_loc:
            for ep in decoded["episodes"]:
                ep["loc_class"] = None
        ok, where = structures_equal(decoded, canon)
        if ok:
            n_ok += 1
        else:
            failures.append((key, where))
    verdict = "PASS" if (n_compared > 0 and n_ok == n_compared) else "FAIL"
    return {
        "verdict": verdict, "n_compared": n_compared, "n_ok": n_ok,
        "n_no_source_diaries_excluded": n_no_source,
        "n_failures": len(failures), "examples": failures[:10],
    }


# ---------------------------------------------------------------------------
# G3.2 -- duration closure (independent parse, not decoder-dependent)
# ---------------------------------------------------------------------------
def gate_g32(records):
    n = len(records)
    bad = []
    for r in records:
        try:
            _, episodes = indep_parse(r["text"])
        except Exception as exc:
            bad.append((r.get("hid"), "parse error: %s" % exc))
            continue
        total = sum(int(e[0]) for e in episodes)
        if total != 1440:
            bad.append((r.get("hid"), "sum=%d" % total))
    verdict = "PASS" if not bad else "FAIL"
    return {"verdict": verdict, "n": n, "n_bad": len(bad), "examples": bad[:10]}


# ---------------------------------------------------------------------------
# G3.3, G3.5, G3.12 -- tokenizer-dependent, computed together in one pass.
# ---------------------------------------------------------------------------
def tokenizer_pass(records, tok, expected_vocab_len, add_tokens=None):
    if add_tokens:
        tok.add_tokens(add_tokens)
    n = len(records)
    n_rt_ok = 0          # idempotency -- kept as a REPORTED NUMBER only, no longer a gate
    n_char_ok = 0        # D-S3-13: the gate
    n_eor_ok = 0
    lens = []
    max_id = -1
    char_examples = []
    for r in records:
        text = r["text"]
        ids = tok.encode(text, add_special_tokens=False)
        detok = tok.decode(ids)
        ids2 = tok.encode(detok, add_special_tokens=False)
        if ids2 == ids:
            n_rt_ok += 1
        if detok == text:
            n_char_ok += 1
        elif len(char_examples) < 5:
            char_examples.append({"expected": text[:120], "got": detok[:120]})
        if detok.endswith(EOR):
            n_eor_ok += 1
        lens.append(len(ids))
        if ids:
            max_id = max(max_id, max(ids))
    vocab_len = len(tok)
    # D-S3-13 (author, 2026-08-17): G3.3 RE-SPECIFIED.
    #   WAS: tok.encode(tok.decode(ids)) == ids -- tokenizer IDEMPOTENCY, a property
    #        of essentially every well-formed BPE tokenizer and of nothing we built.
    #        Measured PASS under the gpt2 swap ("DID NOT FIRE"), so the gate could
    #        not fail and the coverage clause FAILed on it (job 1256012).
    #   IS:  tok.decode(tok.encode(text)) == text, exact string equality, 100% of
    #        the corpus -- a statement about OUR TEXT under the real backbone
    #        tokenizer. It guards what nothing else guards: our records carry
    #        `<eor>`, a literal `+` in the `75+` age band, underscores, and absent
    #        fields written as two ADJACENT COMMAS. G3.4 counts tokens per ACT code
    #        and G3.12 checks the vocabulary was not extended; neither would notice
    #        a tokenizer that ate a `+` or collapsed two commas into one.
    #   The idempotency number is still printed, as a number, never as a verdict.
    g33_verdict = "PASS" if n_char_ok == n else "FAIL"
    g312_subset_ok = max_id < vocab_len
    g312_len_ok = vocab_len == expected_vocab_len
    g312_verdict = "PASS" if (g312_subset_ok and g312_len_ok) else "FAIL"
    med = statistics.median(lens) if lens else float("nan")
    p99 = pctl(lens, 99) if lens else float("nan")
    mx = max(lens) if lens else 0
    med_ok = med <= G35_MEDIAN_MAX
    p99_ok = p99 <= G35_P99_MAX
    max_ok = mx <= G35_MAX_MAX
    g35_verdict = "PASS" if (med_ok and p99_ok and max_ok) else "FAIL"
    g35_end = []
    if not med_ok:
        g35_end.append("median EXCEEDS (upper end)")
    if not p99_ok:
        g35_end.append("p99 EXCEEDS (upper end)")
    if not max_ok:
        g35_end.append("max EXCEEDS (upper end)")
    return {
        "g33": {"verdict": g33_verdict, "n": n,
                "n_char_roundtrip_ok": n_char_ok,
                "n_idempotency_ok_REPORTED_NOT_SCORED": n_rt_ok,
                "n_eor_ok_detok": n_eor_ok,
                "examples": char_examples},
        "g35": {"verdict": g35_verdict, "median": med, "p99": p99, "max": mx,
                "band": "median<=%d p99<=%d max<=%d" % (G35_MEDIAN_MAX, G35_P99_MAX, G35_MAX_MAX),
                "which_end_exceeds": g35_end},
        "g312": {"verdict": g312_verdict, "vocab_len": vocab_len, "expected_vocab_len": expected_vocab_len,
                 "subset_ok": g312_subset_ok, "max_token_id": max_id},
    }


# ---------------------------------------------------------------------------
# G3.4 -- one-token ACT codes (raw literal ACT strings, independent parse)
# ---------------------------------------------------------------------------
def gate_g34(records, tok):
    acts = set()
    for r in records:
        try:
            _, episodes = indep_parse(r["text"])
        except Exception:
            continue
        for e in episodes:
            acts.add(e[1])
    bad = []
    for a in sorted(acts):
        if not (len(a) == 3 and a.isdigit()):
            bad.append((a, "not a 3-digit code"))
            continue
        ids = tok.encode(a, add_special_tokens=False)
        if len(ids) != 1:
            bad.append((a, "%d tokens" % len(ids)))
    verdict = "PASS" if not bad else "FAIL"
    return {"verdict": verdict, "n_distinct_act_codes": len(acts), "n_bad": len(bad), "examples": bad[:20]}


# ---------------------------------------------------------------------------
# G3.6 -- <eor> presence (raw suffix check on the literal text, all records)
# ---------------------------------------------------------------------------
def gate_g36(records):
    n = len(records)
    n_ok = sum(1 for r in records if r["text"].endswith(EOR))
    verdict = "PASS" if n_ok == n else "FAIL"
    return {"verdict": verdict, "n": n, "n_ok": n_ok}


# ---------------------------------------------------------------------------
# G3.7 + V3.h -- prefix completeness (first 8 fields present/non-empty) and
# width consistency across records (frozen at 8).
# ---------------------------------------------------------------------------
def gate_g37(records):
    n = len(records)
    n_missing = 0
    widths = Counter()
    examples = []
    for r in records:
        try:
            prefix_fields, _ = indep_parse(r["text"])
        except Exception as exc:
            n_missing += 1
            examples.append((r.get("hid"), "parse error: %s" % exc))
            continue
        widths[len(prefix_fields)] += 1
        first_n = prefix_fields[:len(PREFIX_FIELDS)]  # SIX after D-S3-11, not eight
        if len(prefix_fields) < len(PREFIX_FIELDS) or any(v == "" for v in first_n):
            n_missing += 1
            examples.append((r.get("hid"), "missing/empty among first %d fields: %s"
                              % (len(PREFIX_FIELDS), first_n)))
    verdict = "PASS" if n_missing == 0 else "FAIL"
    v3h_uniform = len(widths) == 1
    v3h_matches_frozen = widths.get(len(PREFIX_FIELDS), 0) == n
    return {
        "verdict": verdict, "n": n, "n_missing_or_empty": n_missing, "examples": examples[:10],
        "v3h_width_distribution": dict(widths), "v3h_uniform_across_records": v3h_uniform,
        "v3h_matches_frozen_field_count": v3h_matches_frozen,
        "v3h_frozen_field_count": len(PREFIX_FIELDS),
    }


# ---------------------------------------------------------------------------
# G3.8 -- prefix honesty. Uses decoded COP flags + country vs an availability
# grid file (real or a mutated copy for the perturbation).
# ---------------------------------------------------------------------------
def load_availability_grid(path):
    """country -> set of flags marked 'recorded'."""
    grid = defaultdict(set)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # crude markdown-table parse: locate the header row and the 3 country rows
    lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    header = None
    for l in lines:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if header is None and cells and cells[0].lower() == "country":
            header = cells
            continue
        if header is None:
            continue
        if not cells or cells[0].lower() not in ("es", "uk", "it"):
            continue
        country = cells[0].lower()
        for flag_name, val in zip(header[1:], cells[1:]):
            if val.strip().lower() == "recorded":
                grid[country].add(flag_name.strip())
    return grid


def gate_g38(records, bitpos_true, availability_path):
    grid = load_availability_grid(availability_path)
    n_violations = 0
    examples = []
    for r in records:
        try:
            decoded = dec.decode_record(r["text"], bitpos_true)
        except Exception:
            continue
        country = decoded["prefix"]["country"]
        recorded = grid.get(country, set())
        for ep in decoded["episodes"]:
            if ep["cop"] is None:
                continue
            for flag, val in ep["cop"].items():
                if val and flag not in recorded:
                    n_violations += 1
                    if len(examples) < 10:
                        examples.append((r.get("hid"), country, flag))
    verdict = "PASS" if n_violations == 0 else "FAIL"
    return {"verdict": verdict, "n_violations": n_violations, "examples": examples,
            "availability_path": availability_path, "grid": {k: sorted(v) for k, v in grid.items()}}


# ---------------------------------------------------------------------------
# G3.9 -- RE-POINTED by D-S3-12 (author, 2026-08-17).
#
# WAS: "exactly one distinct MODE and one distinct SCHEME across the whole
# corpus". Both fields were removed from the prefix by D-S3-11, so that
# threshold lost its subject entirely.
#
# IS: cross-country vocabulary, in its FOLD-AWARE form --
#   For each of the three LOCO folds, every prefix value emitted by the HELD-OUT
#   country must also appear in the union of the two TRAINING countries.
#   Evaluated per prefix field, over OBSERVED values, not declared ones.
#
# 🔴 Why observed and not declared: `crosswalk_strata.csv` declares `unknown`
# legal for all three countries "for cross-country parity" (D-S2-19 section 3)
# while only the UK actually emits it in `strat_hh_type`. A declared-vocabulary
# check therefore passes a corpus that has a real defect in it -- measured, see
# Finding 4 of `impl/2026-08-17_step3-gates.md`.
#
# 🔴 `country` itself is excluded: it is an explicit prefix field, so it is
# *supposed* to differ per country. This gate is not about disclosing country
# identity -- nothing is disclosed -- it is about a symbol appearing at test time
# that training never showed the model.
#
# 🔴 REGISTRATION: this threshold was written AFTER seeing job 1256012's data.
# It is pre-registered in `4thJ_03_serialisation_val.md` before the rebuild, and
# it must be SEEN FAILING on its own perturbation. It may not be presented as
# though it had been there from the start.
# ---------------------------------------------------------------------------
def gate_g39(records):
    per_field = {}   # field name -> country -> {value: n_records}
    for r in records:
        try:
            prefix_fields, _ = indep_parse(r["text"])
        except Exception:
            continue
        if len(prefix_fields) < len(PREFIX_FIELDS):
            continue
        c = prefix_fields[0]
        for i, fname in enumerate(PREFIX_FIELDS):
            if fname == "country":
                continue
            d = per_field.setdefault(fname, {}).setdefault(c, {})
            d[prefix_fields[i]] = d.get(prefix_fields[i], 0) + 1

    countries = sorted({c for by_c in per_field.values() for c in by_c})
    per_fold = {}
    violations = []
    for held in countries:
        train = [c for c in countries if c != held]
        unseen = []
        for fname in PREFIX_FIELDS:
            if fname == "country":
                continue
            by_c = per_field.get(fname, {})
            held_vals = set(by_c.get(held, {}))
            train_vals = set()
            for t in train:
                train_vals |= set(by_c.get(t, {}))
            for v in sorted(held_vals - train_vals):
                unseen.append({"field": fname, "value": v, "held_out": held,
                               "training": train,
                               "n_records_held_out": by_c[held][v]})
        per_fold[held] = {"verdict": "PASS" if not unseen else "FAIL", "n_unseen": len(unseen),
                          "unseen": unseen}
        violations.extend(unseen)

    verdict = "PASS" if not violations else "FAIL"
    return {"verdict": verdict, "n_violations": len(violations),
            "folds_evaluated": countries, "per_fold": per_fold,
            "examples": violations[:10],
            "vocabulary_sizes": {f: {c: len(d) for c, d in sorted(by_c.items())}
                                  for f, by_c in sorted(per_field.items())}}


# ---------------------------------------------------------------------------
# G3.10 -- no YEAR token, no 4-digit year, anywhere in the prefix
# ---------------------------------------------------------------------------
YEAR_RE = re.compile(r"(?<!\d)(19|20)\d{2}(?!\d)")


def gate_g310(records):
    hits = []
    for r in records:
        try:
            prefix_fields, _ = indep_parse(r["text"])
        except Exception:
            continue
        prefix_str = ",".join(prefix_fields)
        if "YEAR" in prefix_str or YEAR_RE.search(prefix_str):
            hits.append(r.get("hid"))
    verdict = "PASS" if not hits else "FAIL"
    return {"verdict": verdict, "n_hits": len(hits), "examples": hits[:10]}


# ---------------------------------------------------------------------------
# G3.11 -- split integrity (JSON fields only, no text parsing needed)
# ---------------------------------------------------------------------------
def gate_g311(records):
    train = set()
    heldout = set()
    for r in records:
        key = (r["country"], r["hid"], r["pid"])
        if r["split"] == "train":
            train.add(key)
        elif r["split"] == "heldout":
            heldout.add(key)
    inter = train & heldout
    verdict = "PASS" if not inter else "FAIL"
    return {"verdict": verdict, "n_train_respondents": len(train), "n_heldout_respondents": len(heldout),
            "intersection": len(inter), "examples": list(inter)[:10]}


# ---------------------------------------------------------------------------
# G3.14(a) -- COP range/spelling, independent parse
# ---------------------------------------------------------------------------
def gate_g314a(records):
    bad = []
    for r in records:
        try:
            _, episodes = indep_parse(r["text"])
        except Exception as exc:
            bad.append((r.get("hid"), "parse error: %s" % exc))
            continue
        for e in episodes:
            cop_s = e[4]
            if not cop_s.isdigit():
                bad.append((r.get("hid"), "cop %r not a digit string" % cop_s))
                continue
            if cop_s != str(int(cop_s)):
                bad.append((r.get("hid"), "cop %r carries a leading zero" % cop_s))
                continue
            v = int(cop_s)
            if not (0 <= v <= 64):
                bad.append((r.get("hid"), "cop %d out of range 0-64" % v))
    verdict = "PASS" if not bad else "FAIL"
    return {"verdict": verdict, "n_violations": len(bad), "examples": bad[:10]}


# ---------------------------------------------------------------------------
# G3.14(b) -- bit-order fidelity, fully independent (own bitpos load, own
# corpus parse, own harmonised.parquet read). V3.f prevalence table included.
# ---------------------------------------------------------------------------
def gate_g314b(records, harmonised_path, crosswalks_dir, v3e_verdict):
    log("G3.14(b): reading harmonised.parquet FRESH (independent, no encoder/decoder import)")
    if v3e_verdict != "PASS":
        return {"verdict": "FAIL", "reason": "V3.e guard failed: crosswalk_copresence.csv is not usable"}
    df = pd.read_parquet(harmonised_path, columns=DIARY_KEY + SHARED_FLAGS)
    df["country"] = df["country"].astype(str).str.lower()
    bitpos = load_bitpos_independent(os.path.join(crosswalks_dir, "crosswalk_copresence.csv"))

    corpus_counts = {c: {f: 0 for f in SHARED_FLAGS} for c in ("es", "it", "uk")}
    for r in records:
        country = r.get("country")
        if country not in corpus_counts:
            continue
        try:
            _, episodes = indep_parse(r["text"])
        except Exception:
            continue
        for e in episodes:
            cop_s = e[4]
            if not cop_s.isdigit():
                continue
            v = int(cop_s)
            if v == COP_NOT_COLLECTED:
                continue
            for flag, pos in bitpos.items():
                if (v >> pos) & 1:
                    corpus_counts[country][flag] += 1

    parquet_counts = {c: {} for c in ("es", "it", "uk")}
    for c in ("es", "it", "uk"):
        sub = df[df["country"] == c]
        # exclude all-six-null rows on the parquet side, matching the corpus-side
        # exclusion of COP==64 episodes from both sides of the comparison
        all_null = sub[SHARED_FLAGS].isna().all(axis=1)
        sub_included = sub[~all_null]
        for flag in SHARED_FLAGS:
            parquet_counts[c][flag] = int((sub_included[flag].fillna(0).astype(int) != 0).sum())

    log("  V3.f -- per-country per-flag prevalence, both sides, before verdict:")
    mismatches = []
    for c in ("es", "it", "uk"):
        for flag in SHARED_FLAGS:
            cc = corpus_counts[c][flag]
            pc = parquet_counts[c][flag]
            log("    country=%s flag=%s corpus=%d parquet=%d %s"
                % (c, flag, cc, pc, "" if cc == pc else "<== MISMATCH"))
            if cc != pc:
                mismatches.append((c, flag, cc, pc))
    verdict = "PASS" if not mismatches else "FAIL"
    return {"verdict": verdict, "n_mismatches": len(mismatches), "examples": mismatches[:20],
            "corpus_counts": corpus_counts, "parquet_counts": parquet_counts}


# ---------------------------------------------------------------------------
# G3.15(a) -- ACT2 field alphabet (independent parse + independent legal set)
# ---------------------------------------------------------------------------
def gate_g315a(records, crosswalks_dir):
    legal = load_act2_codes_independent(os.path.join(crosswalks_dir, "crosswalk_activity_secondary.csv"))
    bad = []
    for r in records:
        try:
            _, episodes = indep_parse(r["text"])
        except Exception:
            continue
        for e in episodes:
            act2 = e[2]
            if act2 == "":
                continue
            if act2.strip() == "" and act2 != "":
                bad.append((r.get("hid"), "whitespace used as absent form: %r" % act2))
                continue
            if act2 not in legal:
                bad.append((r.get("hid"), "act2 %r not one of the %d shipped codes" % (act2, len(legal))))
    verdict = "PASS" if not bad else "FAIL"
    return {"verdict": verdict, "n_violations": len(bad), "examples": bad[:10]}


# ---------------------------------------------------------------------------
# G3.15(b) -- ACT2 count reconciliation, fully independent, fresh parquet read
# ---------------------------------------------------------------------------
def gate_g315b(records, harmonised_path):
    log("G3.15(b): reading harmonised.parquet FRESH (independent, no encoder/decoder import)")
    df = pd.read_parquet(harmonised_path, columns=DIARY_KEY + ["act2"])
    df["country"] = df["country"].astype(str).str.lower()
    parquet_counts = {}
    for c in ("es", "it", "uk"):
        sub = df[df["country"] == c]
        parquet_counts[c] = int((~sub["act2"].isna() & (sub["act2"].astype(str).str.strip() != "")).sum())

    corpus_counts = {c: 0 for c in ("es", "it", "uk")}
    for r in records:
        country = r.get("country")
        if country not in corpus_counts:
            continue
        try:
            _, episodes = indep_parse(r["text"])
        except Exception:
            continue
        for e in episodes:
            if e[2] != "":
                corpus_counts[country] += 1

    mismatches = []
    for c in ("es", "it", "uk"):
        if corpus_counts[c] != parquet_counts[c]:
            mismatches.append((c, corpus_counts[c], parquet_counts[c]))
    verdict = "PASS" if not mismatches else "FAIL"
    return {"verdict": verdict, "corpus_counts": corpus_counts, "parquet_counts": parquet_counts,
            "mismatches": mismatches}


# ---------------------------------------------------------------------------
# G3.16(a)/(b)/(c) -- explicit-null reconciliation, fully independent, fresh
# parquet read, own LOC alphabet loaded live from crosswalk_location.csv.
# ---------------------------------------------------------------------------
def gate_g316(records, harmonised_path, crosswalks_dir):
    log("G3.16: reading harmonised.parquet FRESH (independent, no encoder/decoder import)")
    df = pd.read_parquet(harmonised_path, columns=DIARY_KEY + ["loc_class", "act"] + SHARED_FLAGS)
    df["country"] = df["country"].astype(str).str.lower()
    loc_alphabet = load_loc_alphabet_independent(os.path.join(crosswalks_dir, "crosswalk_location.csv"))

    parquet_unknown = {}
    parquet_cop64 = {}
    parquet_act000 = {}
    for c in ("es", "it", "uk"):
        sub = df[df["country"] == c]
        parquet_unknown[c] = int(sub["loc_class"].isna().sum())
        all_null = sub[SHARED_FLAGS].isna().all(axis=1)
        parquet_cop64[c] = int(all_null.sum())
        parquet_act000[c] = int(sub["act"].isna().sum())

    corpus_unknown = {c: 0 for c in ("es", "it", "uk")}
    corpus_cop64 = {c: 0 for c in ("es", "it", "uk")}
    corpus_act000 = {c: 0 for c in ("es", "it", "uk")}
    loc_spelling_bad = []
    for r in records:
        country = r.get("country")
        if country not in corpus_unknown:
            continue
        try:
            _, episodes = indep_parse(r["text"])
        except Exception:
            continue
        for e in episodes:
            dur_s, act, act2, loc, cop_s = e
            if loc == LOC_UNKNOWN:
                corpus_unknown[country] += 1
            elif loc not in loc_alphabet:
                loc_spelling_bad.append((r.get("hid"), loc))
            if cop_s.isdigit() and int(cop_s) == COP_NOT_COLLECTED:
                corpus_cop64[country] += 1
            if act == ACT_NULL_CODE:
                corpus_act000[country] += 1

    a_mismatch = [(c, corpus_unknown[c], parquet_unknown[c])
                  for c in ("es", "it", "uk") if corpus_unknown[c] != parquet_unknown[c]]
    b_mismatch = [(c, corpus_cop64[c], parquet_cop64[c])
                  for c in ("es", "it", "uk") if corpus_cop64[c] != parquet_cop64[c]]
    c_mismatch = [(c, corpus_act000[c], parquet_act000[c])
                  for c in ("es", "it", "uk") if corpus_act000[c] != parquet_act000[c]]

    a_verdict = "PASS" if (not a_mismatch and not loc_spelling_bad) else "FAIL"
    b_verdict = "PASS" if not b_mismatch else "FAIL"
    c_verdict = "PASS" if not c_mismatch else "FAIL"
    overall = "PASS" if (a_verdict == "PASS" and b_verdict == "PASS" and c_verdict == "PASS") else "FAIL"

    return {
        "verdict": overall,
        "a": {"verdict": a_verdict, "corpus": corpus_unknown, "parquet": parquet_unknown,
              "mismatches": a_mismatch, "spelling_violations": loc_spelling_bad[:10],
              "expected": EXPECTED_UNKNOWN_LOC},
        "b": {"verdict": b_verdict, "corpus": corpus_cop64, "parquet": parquet_cop64,
              "mismatches": b_mismatch, "expected": EXPECTED_COP64},
        "c": {"verdict": c_verdict, "corpus": corpus_act000, "parquet": parquet_act000,
              "mismatches": c_mismatch, "expected": EXPECTED_ACT000},
    }


# ---------------------------------------------------------------------------
# G3.13 -- independent re-derivation of the per-diary Level-1 time budget.
# 500 random records, own parser, own fresh parquet read. Level-1 category =
# first digit of the 3-digit ACT code; the literal null code "000" (D-S3-9)
# is its own NULL category, kept separate from real codes starting with "0"
# (several exist, e.g. 011/012/021 -- see implementation-doc Decision 3).
# ---------------------------------------------------------------------------
def level1_of(act_str):
    if act_str == ACT_NULL_CODE:
        return "NULL"
    return act_str[0] if act_str else "?"


def gate_g313(records, harmonised_path, n_sample=500, seed=1301):
    log("G3.13: reading harmonised.parquet FRESH (independent, no encoder/decoder import)")
    df = pd.read_parquet(harmonised_path, columns=DIARY_KEY + ["episode_index", "duration_min", "act"])
    df["country"] = df["country"].astype(str).str.lower()

    real_keys = set(tuple(x) for x in df[DIARY_KEY].drop_duplicates().itertuples(index=False, name=None))
    candidates = [r for r in records if (r["country"], r["hid"], r["pid"], r["diary_day"]) in real_keys]
    rng = random.Random(seed)
    sample = rng.sample(candidates, min(n_sample, len(candidates)))
    log("  G3.13 sample: %d / %d real-diary records available, %d sampled"
        % (len(candidates), len(records), len(sample)))

    n_diary_cat_pairs = 0
    n_bad_pairs = 0
    examples = []
    for r in sample:
        key = (r["country"], r["hid"], r["pid"], r["diary_day"])
        try:
            _, episodes = indep_parse(r["text"])
        except Exception as exc:
            n_bad_pairs += 1
            examples.append((key, "parse error: %s" % exc))
            continue
        corpus_budget = defaultdict(int)
        for e in episodes:
            dur_s, act, act2, loc, cop_s = e
            corpus_budget[level1_of(act)] += int(dur_s)

        # boolean mask, not MultiIndex .loc -- avoids any sortedness assumption
        sub = df[(df["country"] == key[0]) & (df["hid"] == key[1])
                 & (df["pid"] == key[2]) & (df["diary_day"] == key[3])]
        parquet_budget = defaultdict(int)
        for _, row in sub.iterrows():
            cat = "NULL" if pd.isna(row["act"]) else str(row["act"]).strip()[0]
            parquet_budget[cat] += int(row["duration_min"])

        cats = set(corpus_budget) | set(parquet_budget)
        for cat in cats:
            n_diary_cat_pairs += 1
            diff = abs(corpus_budget.get(cat, 0) - parquet_budget.get(cat, 0))
            if diff >= 1:
                n_bad_pairs += 1
                if len(examples) < 15:
                    examples.append((key, cat, corpus_budget.get(cat, 0), parquet_budget.get(cat, 0)))

    verdict = "PASS" if n_bad_pairs == 0 else "FAIL"
    return {"verdict": verdict, "n_diaries_sampled": len(sample),
            "n_diary_category_pairs": n_diary_cat_pairs, "n_bad_pairs": n_bad_pairs,
            "examples": examples}


# ---------------------------------------------------------------------------
# Perturbation builders. Each returns (new_records, overrides_dict, notes).
# overrides_dict may carry: canonical_override, decode_bitpos_override,
# act2_absent_extra, drop_loc, availability_path, tokenizer_model,
# add_tokens, harmonised_override_path (never used -- see Decision, none of
# the 21 rows mutate harmonised.parquet).
# ---------------------------------------------------------------------------
def clone_records(records):
    return [dict(r) for r in records]


def reserialize(prefix_fields, episodes):
    ep_str = "".join("%s,%s,%s,%s,%s;" % e for e in episodes)
    return PREFIX_SEP.join(prefix_fields) + PREFIX_BODY_SEP + ep_str + EOR


def perturb_drop_loc_decoder(records, ctx):
    return clone_records(records), {"drop_loc": True}, "decoder-side override: LOC forced to None on decode"


def perturb_merge_episodes(records, ctx):
    new = []
    n_merged = 0
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        if len(episodes) >= 2:
            e0, e1 = episodes[0], episodes[1]
            merged_dur = str(int(e0[0]) + int(e1[0]))
            merged_ep = (merged_dur, e0[1], e0[2], e0[3], e0[4])
            new_eps = [merged_ep] + episodes[2:]
            r2["text"] = reserialize(prefix_fields, new_eps)
            n_merged += 1
        new.append(r2)
    return new, {}, "merged first two episodes on %d/%d diaries" % (n_merged, len(records))


def perturb_tokenizer_swap(records, ctx):
    return clone_records(records), {"tokenizer_model": SWAP_MODEL}, "swap tokenizer to %s" % SWAP_MODEL


def perturb_zero_pad_act4(records, ctx):
    new = []
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        padded = [(e[0], "0" + e[1], e[2], e[3], e[4]) for e in episodes]
        r2["text"] = reserialize(prefix_fields, padded)
        new.append(r2)
    return new, {}, "zero-padded every ACT code to 4 digits"


def perturb_inject_150ep(records, ctx):
    new = clone_records(records)
    template = records[0]
    prefix_fields, _ = indep_parse(template["text"])
    durs = [9] * 149
    durs.append(1440 - sum(durs))
    assert sum(durs) == 1440 and durs[-1] > 0
    episodes = [(str(d), "311", "", "at_home", "0") for d in durs]
    text = reserialize(prefix_fields, episodes)
    new.append({"country": prefix_fields[0], "hid": "INJECT150", "pid": "INJECT150",
                "diary_day": "INJECT150", "split": "train", "text": text})
    return new, {}, "appended one synthetic 150-episode diary, durations sum to 1440"


def perturb_strip_eor_1pct(records, ctx):
    rng = random.Random(4242)
    new = clone_records(records)
    idxs = rng.sample(range(len(new)), max(1, len(new) // 100))
    for i in idxs:
        if new[i]["text"].endswith(EOR):
            new[i]["text"] = new[i]["text"][: -len(EOR)]
    return new, {}, "stripped <eor> from %d/%d records (1%%)" % (len(idxs), len(new))


def perturb_blank_prefix_field10(records, ctx):
    new = clone_records(records)
    for i in range(min(10, len(new))):
        try:
            prefix_fields, episodes = indep_parse(new[i]["text"])
        except Exception:
            continue
        prefix_fields[1] = ""  # strat_age_band
        new[i]["text"] = reserialize(prefix_fields, episodes)
    return new, {}, "blanked strat_age_band on the first 10 records"


def perturb_assert_flag_not_recorded(records, ctx):
    real_path = ctx["availability_path"]
    mutated_path = os.path.join(ctx["out_dir"], "copresence_availability_MUTATED_it_no_partner.md")
    with open(real_path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    out = []
    header = None
    for l in lines:
        if l.strip().startswith("|"):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if header is None and cells and cells[0].lower() == "country":
                header = cells
            elif header is not None and cells and cells[0].lower() == "it":
                try:
                    col = header.index("cop_partner")
                    cells[col] = "not recorded"
                    l = "| " + " | ".join(cells) + " |"
                except ValueError:
                    pass
        out.append(l)
    with open(mutated_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    new = clone_records(records)
    # find an IT record and force cop_partner's bit on for its first episode so
    # the corpus actually asserts the now-forbidden flag
    bitpos = ctx["bitpos_true"]
    partner_pos = bitpos["cop_partner"]
    for i, r in enumerate(new):
        if r["country"] == "it":
            try:
                prefix_fields, episodes = indep_parse(r["text"])
            except Exception:
                continue
            e0 = episodes[0]
            cop_v = int(e0[4]) if e0[4].isdigit() else 0
            if cop_v == COP_NOT_COLLECTED:
                cop_v = 0
            cop_v |= (1 << partner_pos)
            episodes[0] = (e0[0], e0[1], e0[2], e0[3], str(cop_v))
            new[i]["text"] = reserialize(prefix_fields, episodes)
            break
    return new, {"availability_path": mutated_path}, "IT cop_partner marked 'not recorded'; one IT record asserts it"


def perturb_national_raw_hh_type_it(records, ctx):
    """D-S3-12's perturbation for the RE-POINTED G3.9. Replaces
    `mode_second_value`, whose target field D-S3-11 removed from the prefix.

    Puts a NATIONAL RAW value back into one field for one country -- Italy's
    `tipfa2m` household-type code into `strat_hh_type` -- which is literally what
    the encoder did before D-S2-18 closed it. Italy then emits a symbol neither
    Spain nor the UK can produce, so the ITALY fold fails: held out on IT, the
    model trains on ES+UK and meets `tipfa2m_05` for the first time at test.

    🔴 Aimed at the ITALY fold deliberately. The UK fold already FAILs at
    baseline on `strat_hh_type = unknown` (Finding 4 / open item D-S3-14), and a
    sub-verdict that is already red cannot be seen falling. The Italy fold PASSes
    at baseline, so its PASS -> FAIL is the demonstration.
    """
    new = []
    n_hit = 0
    for r in records:
        r2 = dict(r)
        if r.get("country") == "it":
            try:
                prefix_fields, episodes = indep_parse(r["text"])
                prefix_fields[3] = "tipfa2m_05"   # strat_hh_type
                r2["text"] = reserialize(prefix_fields, episodes)
                n_hit += 1
            except Exception:
                pass
        new.append(r2)
    return new, {}, "national raw tipfa2m_05 written into strat_hh_type on %d IT records" % n_hit


def perturb_add_year2013(records, ctx):
    new = []
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        prefix_fields = prefix_fields + ["2013"]
        r2["text"] = reserialize(prefix_fields, episodes)
        new.append(r2)
    return new, {}, "appended an extra prefix field '2013' to every record"


def perturb_split_by_diary(records, ctx):
    new = clone_records(records)
    for r in new:
        key = "%s|%s|%s|%s" % (r["country"], r["hid"], r["pid"], r["diary_day"])
        h = zlib.crc32(key.encode("utf-8")) % 10  # stable across runs, unlike built-in hash()
        r["split"] = "heldout" if h == 0 else "train"
    return new, {}, "re-split by diary key (not respondent), stable crc32 hash"


def perturb_add_tokens_act311(records, ctx):
    return clone_records(records), {"add_tokens": ["<act311>"]}, "tokenizer.add_tokens(['<act311>'])"


def perturb_zero_pad_cop2(records, ctx):
    new = []
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        padded = []
        for e in episodes:
            cop_s = e[4]
            if cop_s.isdigit() and 0 <= int(cop_s) <= 9:
                cop_s = "0" + cop_s
            padded.append((e[0], e[1], e[2], e[3], cop_s))
        r2["text"] = reserialize(prefix_fields, padded)
        new.append(r2)
    return new, {}, "zero-padded single-digit COP values to 2 digits"


def perturb_reverse_bitorder(records, ctx):
    new = []
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        reversed_eps = []
        for e in episodes:
            cop_s = e[4]
            if cop_s.isdigit():
                v = int(cop_s)
                if v != COP_NOT_COLLECTED:
                    v = reverse_bits_6(v)
                cop_s = str(v)
            reversed_eps.append((e[0], e[1], e[2], e[3], cop_s))
        r2["text"] = reserialize(prefix_fields, reversed_eps)
        new.append(r2)
    bitpos_true = ctx["bitpos_true"]
    reversed_bitpos = {f: 5 - p for f, p in bitpos_true.items()}
    return new, {"decode_bitpos_override": reversed_bitpos}, \
        "COP values 6-bit-reversed in corpus text; G3.1 decodes with the SAME reversed bit order"


def perturb_act2_98_fill(records, ctx):
    new = []
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        filled = [(e[0], e[1], "98" if e[2] == "" else e[2], e[3], e[4]) for e in episodes]
        r2["text"] = reserialize(prefix_fields, filled)
        new.append(r2)
    return new, {"act2_absent_extra": {"98"}}, "absent ACT2 slot filled with literal '98'"


def perturb_loader_drop_act2_italy(records, ctx, canonical_index):
    new = []
    for r in records:
        r2 = dict(r)
        if r["country"] == "it":
            try:
                prefix_fields, episodes = indep_parse(r["text"])
                blanked = [(e[0], e[1], "", e[3], e[4]) for e in episodes]
                r2["text"] = reserialize(prefix_fields, blanked)
            except Exception:
                pass
        new.append(r2)
    override = {}
    for key, struct in canonical_index.items():
        if key[0] == "it":
            struct2 = {"prefix": struct["prefix"],
                       "episodes": [dict(ep, act2=None) for ep in struct["episodes"]]}
            override[key] = struct2
        else:
            override[key] = struct
    return new, {"canonical_override": override}, \
        "IT act2 blanked in corpus text; G3.1's canonical side also treats IT act2 as never-read"


def _diary_keys_with_condition(df, country, cond_series):
    sub = df[(df["country"] == country) & cond_series]
    return set(tuple(x) for x in sub[DIARY_KEY].drop_duplicates().itertuples(index=False, name=None))


def perturb_loader_drop_it_null_loc(records, ctx):
    df = ctx["df"]
    keys = _diary_keys_with_condition(df, "it", df["loc_class"].isna())
    new = [r for r in records if (r["country"], r["hid"], r["pid"], r["diary_day"]) not in keys]
    return new, {}, "dropped %d IT diaries with >=1 null loc_class row" % len(keys)


def perturb_loader_drop_uk_null_cop(records, ctx):
    df = ctx["df"]
    all_null = df[SHARED_FLAGS].isna().all(axis=1)
    keys = _diary_keys_with_condition(df, "uk", all_null)
    new = [r for r in records if (r["country"], r["hid"], r["pid"], r["diary_day"]) not in keys]
    return new, {}, "dropped %d UK diaries with >=1 all-six-null cop_* row" % len(keys)


def perturb_loader_drop_es_null_act(records, ctx):
    df = ctx["df"]
    keys = _diary_keys_with_condition(df, "es", df["act"].isna())
    new = [r for r in records if (r["country"], r["hid"], r["pid"], r["diary_day"]) not in keys]
    return new, {}, "dropped %d ES diaries with >=1 null act row" % len(keys)


def perturb_spell_unknown_two_ways(records, ctx):
    new = []
    flipped = 0
    toggle = True
    for r in records:
        r2 = dict(r)
        try:
            prefix_fields, episodes = indep_parse(r["text"])
        except Exception:
            new.append(r2)
            continue
        changed = False
        out_eps = []
        for e in episodes:
            if e[3] == LOC_UNKNOWN and toggle:
                out_eps.append((e[0], e[1], e[2], "UNKNOWN", e[4]))
                changed = True
                toggle = False
            else:
                out_eps.append(e)
        if changed:
            r2["text"] = reserialize(prefix_fields, out_eps)
            flipped += 1
            toggle = True
        new.append(r2)
    return new, {}, "respelled roughly half of 'unknown' occurrences as 'UNKNOWN' (%d records touched)" % flipped


def perturb_null(records, ctx):
    return clone_records(records), {}, "no change"


PERTURBATION_FUNCS = {
    "drop_loc_decoder": perturb_drop_loc_decoder,
    "merge_episodes": perturb_merge_episodes,
    "tokenizer_swap": perturb_tokenizer_swap,
    "zero_pad_act4": perturb_zero_pad_act4,
    "inject_150ep_diary": perturb_inject_150ep,
    "strip_eor_1pct": perturb_strip_eor_1pct,
    "blank_prefix_field10": perturb_blank_prefix_field10,
    "assert_flag_not_recorded": perturb_assert_flag_not_recorded,
    "national_raw_hh_type_it": perturb_national_raw_hh_type_it,
    "add_year2013": perturb_add_year2013,
    "split_by_diary": perturb_split_by_diary,
    "add_tokens_act311": perturb_add_tokens_act311,
    "zero_pad_cop2": perturb_zero_pad_cop2,
    "reverse_bitorder": perturb_reverse_bitorder,
    "act2_98_fill": perturb_act2_98_fill,
    # loader_drop_act2_italy handled specially (needs canonical_index)
    "loader_drop_it_null_loc": perturb_loader_drop_it_null_loc,
    "loader_drop_uk_null_cop": perturb_loader_drop_uk_null_cop,
    "loader_drop_es_null_act": perturb_loader_drop_es_null_act,
    "spell_unknown_two_ways": perturb_spell_unknown_two_ways,
    "null_perturbation": perturb_null,
}

# Gates this perturbation is expected (per the val doc) to move / leave clean.
# Used only for the human-readable comparison in the acceptance-test summary,
# NEVER to alter what is actually measured.
EXPECTED_EFFECT = {
    "drop_loc_decoder": {"fail": ["G3.1"], "clean": ["G3.2"]},
    "merge_episodes": {"fail": ["G3.1"], "clean": ["G3.2"]},
    "tokenizer_swap": {"fail": ["G3.3", "G3.4", "G3.12"], "clean": [], "coverage_only": True},
    "zero_pad_act4": {"fail": ["G3.4"], "clean": ["G3.1"]},
    "inject_150ep_diary": {"fail": ["G3.5"], "clean": ["G3.2"]},
    "strip_eor_1pct": {"fail": ["G3.6"], "clean": ["G3.1"]},
    "blank_prefix_field10": {"fail": ["G3.7"], "clean": ["G3.8"]},
    "assert_flag_not_recorded": {"fail": ["G3.8"], "clean": ["G3.7"]},
    # D-S3-12: replaces `mode_second_value`. Expected to fell the re-pointed G3.9
    # via its ITALY fold sub-verdict, and to leave G3.7 clean (the field is still
    # present and non-empty, only its VALUE became national).
    "national_raw_hh_type_it": {"fail": ["G3.9"], "clean": ["G3.7"]},
    "add_year2013": {"fail": ["G3.10"], "clean": ["G3.7"]},
    "split_by_diary": {"fail": ["G3.11"], "clean": []},
    "add_tokens_act311": {"fail": ["G3.12"], "clean": ["G3.1"]},
    "zero_pad_cop2": {"fail": ["G3.14a"], "clean": ["G3.1", "G3.4"]},
    "reverse_bitorder": {"fail": ["G3.14b"], "clean": ["G3.1"]},
    "act2_98_fill": {"fail": ["G3.15a"], "clean": ["G3.1"]},
    "loader_drop_act2_italy": {"fail": ["G3.15b"], "clean": ["G3.1", "G3.7"]},
    "loader_drop_it_null_loc": {"fail": ["G3.16a"], "clean": ["G3.1", "G3.2", "G3.16b"]},
    "loader_drop_uk_null_cop": {"fail": ["G3.16b", "G3.16a"], "clean": ["G3.1", "G3.2"], "coverage_only": True},
    "loader_drop_es_null_act": {"fail": ["G3.16c"], "clean": ["G3.1", "G3.2", "G3.16a", "G3.16b"]},
    "spell_unknown_two_ways": {"fail": ["G3.16a"], "clean": ["G3.1"]},
    "null_perturbation": {"fail": [], "clean": ["ALL"]},
}


# ---------------------------------------------------------------------------
# Full battery for one variant
# ---------------------------------------------------------------------------
def run_battery(name, records, ctx, overrides, tok_cache):
    report = {"name": name}
    availability_path = overrides.get("availability_path", ctx["availability_path"])
    bitpos_true = ctx["bitpos_true"]

    report["V3.i"] = ctx["v3i_verdict"]
    report["V3.g"] = ctx["v3g_verdict"]
    v3c_verdict, v3c_bad_chars, v3c_n = check_v3c(records)
    report["V3.c"] = {"verdict": v3c_verdict, "bad_chars": v3c_bad_chars, "n_records": v3c_n}
    report["V3.e"] = ctx["v3e_verdict"]

    tokenizer_model = overrides.get("tokenizer_model", MODEL)
    if overrides.get("add_tokens"):
        # 🔴 must NOT reuse/mutate the shared cached tokenizer -- tok.add_tokens() mutates
        # its vocabulary in place, and every later variant sharing tok_cache[tokenizer_model]
        # would silently inherit the added token, corrupting their G3.12 result. Load a private,
        # uncached instance for this one variant only.
        from transformers import AutoTokenizer
        log("Loading a PRIVATE (uncached) tokenizer %s for this variant, because add_tokens is set..."
            % tokenizer_model)
        tok = AutoTokenizer.from_pretrained(tokenizer_model)
    else:
        if tokenizer_model not in tok_cache:
            from transformers import AutoTokenizer
            log("Loading tokenizer %s ..." % tokenizer_model)
            tok_cache[tokenizer_model] = AutoTokenizer.from_pretrained(tokenizer_model)
        tok = tok_cache[tokenizer_model]
    expected_vocab_len = EXPECTED_VOCAB_SIZE  # always compare against the FROZEN base value, on purpose

    canonical_index = ctx["canonical_index"]
    if name == "loader_drop_act2_italy":
        records, extra_over, note = perturb_loader_drop_act2_italy(records, ctx, canonical_index)
        overrides = dict(overrides)
        overrides.update(extra_over)

    report["G3.1"] = gate_g31(
        records, canonical_index, bitpos_true,
        canonical_override=overrides.get("canonical_override"),
        decode_bitpos_override=overrides.get("decode_bitpos_override"),
        act2_absent_extra=overrides.get("act2_absent_extra"),
        drop_loc=overrides.get("drop_loc", False),
    )
    report["G3.2"] = gate_g32(records)
    tokres = tokenizer_pass(records, tok, expected_vocab_len, add_tokens=overrides.get("add_tokens"))
    report["G3.3"] = tokres["g33"]
    report["G3.5"] = tokres["g35"]
    report["G3.12"] = tokres["g312"]
    report["G3.4"] = gate_g34(records, tok)
    report["G3.6"] = gate_g36(records)
    report["G3.7"] = gate_g37(records)
    report["G3.8"] = gate_g38(records, bitpos_true, availability_path)
    report["G3.9"] = gate_g39(records)
    report["G3.10"] = gate_g310(records)
    report["G3.11"] = gate_g311(records)
    report["G3.14a"] = gate_g314a(records)
    report["G3.14b"] = gate_g314b(records, ctx["harmonised_path"], ctx["crosswalks_dir"], report["V3.e"])
    report["G3.15a"] = gate_g315a(records, ctx["crosswalks_dir"])
    report["G3.15b"] = gate_g315b(records, ctx["harmonised_path"])
    g316 = gate_g316(records, ctx["harmonised_path"], ctx["crosswalks_dir"])
    report["G3.16"] = g316["verdict"]
    report["G3.16a"] = g316["a"]
    report["G3.16b"] = g316["b"]
    report["G3.16c"] = g316["c"]
    report["G3.13"] = gate_g313(records, ctx["harmonised_path"])

    return report, records


GATE_NAMES_SCORED = ["G3.1", "G3.2", "G3.3", "G3.4", "G3.5", "G3.6", "G3.7", "G3.8", "G3.9",
                      "G3.10", "G3.11", "G3.12", "G3.13", "G3.14a", "G3.14b", "G3.15a", "G3.15b",
                      "G3.16a", "G3.16b", "G3.16c"]


def verdict_of(report, gate_key):
    v = report.get(gate_key)
    if isinstance(v, dict):
        return v.get("verdict", "NOT CHECKED")
    if isinstance(v, str):
        return v
    return "NOT CHECKED"


def write_report_text(path, report):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Gate report: %s\n" % report["name"])
        fh.write("=" * 78 + "\n")
        for gate in ["V3.i", "V3.g", "V3.c", "V3.e"] + GATE_NAMES_SCORED:
            fh.write("%-10s %s\n" % (gate, verdict_of(report, gate)))
        fh.write("\n")
        fh.write(json.dumps(report, indent=2, default=str))
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--harmonised", required=True)
    ap.add_argument("--crosswalks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--perturbation", required=True,
                     choices=["baseline", "all"] + PERTURBATION_NAMES)
    ap.add_argument("--availability", default=None,
                     help="path to copresence_availability.md (defaults to <crosswalks>/copresence_availability.md)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    availability_path = args.availability or os.path.join(args.crosswalks, "copresence_availability.md")

    t0 = time.time()
    log("4J Step 3 gate battery starting. pandas %s, numpy %s" % (pd.__version__, np.__version__))
    log("corpus=%s" % args.corpus)
    log("harmonised=%s" % args.harmonised)
    log("crosswalks=%s" % args.crosswalks)
    log("availability=%s" % availability_path)
    log("out=%s" % args.out)
    log("perturbation=%s" % args.perturbation)

    df = load_harmonised(args.harmonised)
    v3i_verdict = check_v3i(df)
    v3g_verdict, v3g_results = check_v3g(args.crosswalks)
    bitpos_true = load_bitpos_independent(os.path.join(args.crosswalks, "crosswalk_copresence.csv"))
    v3e_verdict, v3e_reasons = check_v3e(bitpos_true)
    log("V3.e verdict: %s %s" % (v3e_verdict, v3e_reasons))

    canonical_index = build_canonical_index(df)

    baseline_records = read_corpus(args.corpus)
    log("V3.a: baseline corpus has %d records (own file); this run will scan every line read." % len(baseline_records))
    log("=" * 78)
    log("V3.b -- pre-verdict summary: %d records" % len(baseline_records))
    modes0 = set()
    schemes0 = set()
    for r in baseline_records[:2000]:
        try:
            pf, _ = indep_parse(r["text"])
            modes0.add(pf[6])
            schemes0.add(pf[7])
        except Exception:
            pass
    log("  (sampled first 2000) distinct MODE=%s SCHEME=%s" % (sorted(modes0), sorted(schemes0)))

    ctx = {
        "df": df, "harmonised_path": args.harmonised, "crosswalks_dir": args.crosswalks,
        "availability_path": availability_path, "bitpos_true": bitpos_true,
        "canonical_index": canonical_index, "out_dir": args.out,
        "v3i_verdict": v3i_verdict, "v3g_verdict": v3g_verdict, "v3e_verdict": v3e_verdict,
    }

    tok_cache = {}

    names = [args.perturbation]
    if args.perturbation == "all":
        names = ["baseline"] + PERTURBATION_NAMES

    all_reports = {}
    for name in names:
        log("")
        log("#" * 78)
        log("# RUNNING VARIANT: %s" % name)
        log("#" * 78)
        if name == "baseline":
            records = clone_records(baseline_records)
            overrides = {}
            notes = "unperturbed baseline"
        elif name == "loader_drop_act2_italy":
            records = clone_records(baseline_records)
            overrides = {}
            notes = "handled inside run_battery (needs canonical_index)"
        else:
            fn = PERTURBATION_FUNCS[name]
            records, overrides, notes = fn(clone_records(baseline_records), ctx)
        log("notes: %s" % notes)
        log("record count for this variant: %d" % len(records))
        report, records_final = run_battery(name, records, ctx, overrides, tok_cache)
        report["notes"] = notes
        report["n_records"] = len(records_final)
        all_reports[name] = report
        out_path = os.path.join(args.out, "gate_report_%s.txt" % name)
        write_report_text(out_path, report)
        log("Wrote %s" % out_path)
        for gate in GATE_NAMES_SCORED:
            log("  %-10s %s" % (gate, verdict_of(report, gate)))

    if args.perturbation == "all":
        log("")
        log("=" * 78)
        log("COVERAGE CROSS-TAB")
        log("=" * 78)
        baseline_report = all_reports["baseline"]
        baseline_pass = {g for g in GATE_NAMES_SCORED if verdict_of(baseline_report, g) == "PASS"}
        felled_by = defaultdict(list)
        crosstab_lines = []
        header = "perturbation".ljust(28) + "".join(g.ljust(9) for g in GATE_NAMES_SCORED)
        crosstab_lines.append(header)
        for name in ["baseline"] + PERTURBATION_NAMES:
            row = all_reports[name]
            cells = []
            for g in GATE_NAMES_SCORED:
                v = verdict_of(row, g)
                cells.append(v[:4].ljust(9))
                if name != "baseline" and v == "FAIL" and g in baseline_pass:
                    felled_by[g].append(name)
            crosstab_lines.append(name.ljust(28) + "".join(cells))
        for line in crosstab_lines:
            log(line)
        with open(os.path.join(args.out, "coverage_crosstab.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(crosstab_lines) + "\n")

        never_felled = sorted(baseline_pass - set(felled_by.keys()))
        log("")
        log("Gates that PASS at baseline and WERE felled by at least one perturbation: %d / %d"
            % (len(felled_by), len(baseline_pass)))
        for g in sorted(felled_by):
            log("  %s felled by: %s" % (g, felled_by[g]))
        log("Gates that PASS at baseline and were NEVER felled by any perturbation (coverage-clause FAIL if non-empty): %s"
            % never_felled)
        coverage_verdict = "PASS" if not never_felled else "FAIL"
        log("COVERAGE CLAUSE VERDICT: %s" % coverage_verdict)

        log("")
        log("=" * 78)
        log("ACCEPTANCE-TEST-3-STYLE COMPARISON: measured vs val-doc-expected 'must fail' / 'must stay clean'")
        log("=" * 78)
        for name in PERTURBATION_NAMES:
            row = all_reports[name]
            expect = EXPECTED_EFFECT[name]
            log("-- %s --" % name)
            for g in expect.get("fail", []):
                v = verdict_of(row, g)
                status = "AS EXPECTED (fell)" if v == "FAIL" else "DID NOT FIRE" if v != "NOT CHECKED" else "NOT CHECKED"
                log("   expected FAIL %-10s measured %-6s %s" % (g, v, status))
            for g in expect.get("clean", []):
                if g == "ALL":
                    continue
                v = verdict_of(row, g)
                status = "AS EXPECTED (clean)" if v == "PASS" else ("UNEXPECTED FALL -- FINDING" if v == "FAIL" else v)
                log("   expected CLEAN %-10s measured %-6s %s" % (g, v, status))
            if expect.get("coverage_only"):
                log("   (coverage-only row -- cannot attribute per the val doc)")

        summary = {
            "baseline_pass_gates": sorted(baseline_pass),
            "felled_by": {g: v for g, v in felled_by.items()},
            "never_felled": never_felled,
            "coverage_verdict": coverage_verdict,
        }
        with open(os.path.join(args.out, "battery_summary.json"), "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, default=str)

    log("")
    log("DONE. Elapsed: %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
