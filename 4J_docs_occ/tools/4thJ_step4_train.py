"""
Step 4 -- the trainer, with the work-item 4.4 detectors wired in BEFORE the first run.

Deliberately written against torch + transformers + peft directly rather than trl's
SFTTrainer. `G4.5` exists to prove that prompt and pad positions carry label -100, and a
trainer that builds its own labels can be made to prove it. One that inherits masking
from a library can only be trusted about it.

Usage:
  python 4thJ_step4_train.py --fold es --leg 4 --run-type pilot
  python 4thJ_step4_train.py --fold es --leg 5 --run-type primary
  python 4thJ_step4_train.py --fold es --leg 5 --run-type ceiling
  python 4thJ_step4_train.py --fold es --leg 5 --run-type qwen
  ... plus --perturbation <name> for the "seen failing" battery.

Every run writes:
  <out>/run_manifest_<run>.json      G4.11 + G4.13 + G4.14
  <out>/training_metrics.csv         one row set per run, fold and run_type columns
  <out>/detectors_<run>.json         every 4.4 detector, every epoch
"""

import argparse
import csv
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
TH = importlib.import_module("4thJ_step4_thresholds")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
SHARDS = os.path.join(STEP4, "shards")
PREREG = os.path.join(STEP4, "prereg.md")
PREREG_SIDECAR = os.path.join(STEP4, "prereg.md.md5")
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")
STAGED = os.path.join(STEP4, "staged_weights.json")

MODEL_FOR = {
    "pilot":   "allenai/OLMo-2-0425-1B",
    "primary": "allenai/Olmo-3-1025-7B",
    "ceiling": "allenai/Olmo-3-1025-7B",
    "qwen":    "Qwen/Qwen2.5-7B",
}


def fail(msg):
    print()
    print("!" * 78)
    print("FAIL: %s" % msg)
    print("!" * 78)
    sys.exit(1)


def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path):
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# ---------------------------------------------------------------------------
# record parsing -- re-implemented, not imported from encoder.py, for the same
# reason the shard builder re-implements it: a detector that shares a parser with
# the thing it audits cannot disagree with it.
# ---------------------------------------------------------------------------
def split_prefix_body(text):
    i = text.find(TH.PREFIX_BODY_SEP)
    if i < 0:
        raise ValueError("no prefix separator")
    return text[:i + 1], text[i + 1:]


def parse_episodes(body):
    """body -> list of (dur, act, act2, loc, cop). Tolerant: used on GENERATED text
    too, where the model may emit something malformed, and a malformed episode must
    be counted rather than crash the detector."""
    body = body.replace(TH.G4_7_EOR, "")
    eps, bad = [], 0
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(",")
        if len(parts) != 5:
            bad += 1
            continue
        dur, act, act2, loc, cop = parts
        try:
            dur = int(dur)
        except ValueError:
            bad += 1
            continue
        eps.append((dur, act, act2, loc, cop))
    return eps, bad


def at_home_share(text):
    try:
        _, body = split_prefix_body(text)
    except ValueError:
        return None
    eps, _ = parse_episodes(body)
    total = sum(e[0] for e in eps)
    if total <= 0:
        return None
    home = sum(e[0] for e in eps if e[3] == TH.LOC_AT_HOME)
    return home / float(total)


def stratum_of(text):
    try:
        pref = text.split(TH.PREFIX_BODY_SEP)[0].split(",")
    except Exception:
        return None
    if len(pref) != len(TH.PREFIX_FIELDS):
        return None
    d = dict(zip(TH.PREFIX_FIELDS, pref))
    return (d["country"], d["strat_age_band"], d["strat_sex"],
            d["strat_hh_type"], d["strat_day_type"])


# ---------------------------------------------------------------------------
# dataset -- completion-only loss masking, built here so G4.5 can prove it
# ---------------------------------------------------------------------------
class DiaryDataset(Dataset):
    def __init__(self, recs, tokenizer, max_len, perturbation=None):
        self.items = []
        self.n_prompt_positions = 0
        self.n_pad_positions = 0
        self.max_len = max_len
        pad_id = tokenizer.pad_token_id
        for r in recs:
            text = r["text"]
            # strip_eor_1pct is applied ONCE, to train_recs, before G4.7 reads them
            # (FINDING 5). Doing it here as well would corrupt a second 1 %.
            prefix, body = split_prefix_body(text)
            if perturbation == "no_prefix":
                prefix = ""
            p_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
            b_ids = tokenizer(body, add_special_tokens=False)["input_ids"]
            ids = (p_ids + b_ids)[:max_len]
            labels = ([TH.G4_5_REQUIRED_LABEL] * len(p_ids) + list(b_ids))[:max_len]
            self.n_prompt_positions += min(len(p_ids), max_len)
            self.items.append({
                "input_ids": ids, "labels": labels,
                "country": r["country"], "text": text,
            })
        self.pad_id = pad_id

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def collate(batch, pad_id, perturbation=None):
    n = max(len(b["input_ids"]) for b in batch)
    input_ids, labels, attn = [], [], []
    for b in batch:
        k = n - len(b["input_ids"])
        input_ids.append(b["input_ids"] + [pad_id] * k)
        lab = b["labels"] + [TH.G4_5_REQUIRED_LABEL] * k
        if perturbation == "pad_labels_1pct" and k > 0:
            # deliberately break G4.5: set 1 % of pad labels to a real token id
            for j in range(len(b["labels"]), n):
                if random.random() < 0.01:
                    lab[j] = pad_id
        labels.append(lab)
        attn.append([1] * len(b["input_ids"]) + [0] * k)
    return (torch.tensor(input_ids), torch.tensor(labels), torch.tensor(attn))


# ---------------------------------------------------------------------------
# G4.5 -- padding and prompt labels
# ---------------------------------------------------------------------------
def gate_g4_5(loader, pad_id):
    n_pos = 0
    n_bad = 0
    for input_ids, labels, attn in loader:
        pad_mask = attn == 0
        n_pos += int(pad_mask.sum())
        n_bad += int(((labels != TH.G4_5_REQUIRED_LABEL) & pad_mask).sum())
    frac = 1.0 if n_pos == 0 else (n_pos - n_bad) / float(n_pos)
    verdict = "PASS" if (n_pos > 0 and frac >= TH.G4_5_REQUIRED_FRACTION) else "FAIL"
    if n_pos == 0:
        # V4.f in spirit: a check with nothing to check is not a pass
        verdict = "FAIL"
    return {"gate": "G4.5", "verdict": verdict, "pad_positions": n_pos,
            "pad_positions_not_masked": n_bad, "fraction_masked": frac,
            "note": "zero pad positions would make this gate vacuous, so it FAILs rather "
                    "than passing on an empty check"}


# ---------------------------------------------------------------------------
# G4.7 -- termination
# ---------------------------------------------------------------------------
def gate_g4_7(recs):
    n = len(recs)
    ok = sum(1 for r in recs if r["text"].rstrip().endswith(TH.G4_7_EOR))
    frac = ok / float(n) if n else 0.0
    return {"gate": "G4.7", "verdict": "PASS" if (n > 0 and frac >= TH.G4_7_REQUIRED_FRACTION) else "FAIL",
            "n": n, "n_terminated": ok, "fraction": frac}


# ---------------------------------------------------------------------------
# G4.8 -- tokenizer round-trip on 1000 cases
# ---------------------------------------------------------------------------
def gate_g4_8(tokenizer, recs, n_cases=None, base_repo=None):
    """Tokenizer IDENTITY, then round-trip.

    🔴 D-S4-2 (author ruling, 2026-08-18) -- FINDING 17.

    This gate used to perform the round-trip alone: encode a record, decode it, encode
    again, require the ids to match. That is a SELF-CONSISTENCY test, and self-consistency
    survives substitution -- any competent tokenizer round-trips its own output. In job
    1266911 the `swap_tokenizer` perturbation loaded `bert-base-uncased` in place of the
    OLMo tokenizer and the gate reported `PASS 600/600 tokenizer round-trips exact`. It had
    to. (Our record text is lower-case ASCII throughout, so `bert-base-uncased`'s
    lower-casing left no trace either; the gate had no second chance to notice.) The run
    then died in generation on `token_type_ids`, which BERT emits and OLMo's `generate`
    rejects -- so the row read NOT RUN and the blindness went unrecorded.

    The consequence was that NO perturbation in the battery could fell G4.8, which is why
    it sat in the coverage clause's `never made to fall` list. Repairing the crash alone
    would have bought a green row that demonstrates nothing.

    The gate now asserts IDENTITY against the base checkpoint FIRST, and only then
    consistency. A swap fells it on that first assertion, before generation is ever
    reached, which also makes the `token_type_ids` crash moot rather than a separate
    repair. This WIDENS what G4.8 asserts and is recorded as a basis change ruled by the
    author, not as a tightening applied by the implementer.
    """
    n_cases = n_cases or TH.G4_8_CASES
    rng = random.Random(TH.SEED)
    sample = rng.sample(recs, min(n_cases, len(recs)))

    # --- arm 1: identity -----------------------------------------------------
    held = getattr(tokenizer, "name_or_path", None)
    identity_ok = None
    if base_repo is None:
        # Not knowing what we should be holding is not the same as holding the right
        # thing. Say so rather than skipping the arm silently.
        identity = {"checked": False,
                    "reason": "no base_repo supplied -- identity NOT CHECKED, which is "
                              "not a pass"}
    else:
        identity_ok = (str(held) == str(base_repo))
        identity = {"checked": True, "tokenizer_name_or_path": str(held),
                    "expected_base_repo": str(base_repo), "match": identity_ok}

    # --- arm 2: round-trip ---------------------------------------------------
    ok = 0
    for r in sample:
        ids = tokenizer(r["text"], add_special_tokens=False)["input_ids"]
        detok = tokenizer.decode(ids)
        re_ids = tokenizer(detok, add_special_tokens=False)["input_ids"]
        if re_ids == ids:
            ok += 1

    roundtrip_ok = (ok == len(sample) and bool(sample))
    verdict = "PASS" if (identity_ok is True and roundtrip_ok) else "FAIL"
    if identity_ok is False:
        reason = ("tokenizer identity MISMATCH: holding %r, base checkpoint is %r. The "
                  "round-trip arm read %d/%d and is not evidence -- a tokenizer always "
                  "round-trips its own output (D-S4-2, FINDING 17)"
                  % (held, base_repo, ok, len(sample)))
    elif identity_ok is None:
        reason = "identity arm NOT CHECKED (no base_repo); NOT CHECKED is not a pass"
    elif not roundtrip_ok:
        reason = "round-trip arm failed: %d/%d exact" % (ok, len(sample))
    else:
        reason = None
    out = {"gate": "G4.8", "verdict": verdict,
           "n": len(sample), "n_roundtrip_ok": ok,
           "identity": identity, "roundtrip_pass": roundtrip_ok,
           "basis_note": "D-S4-2: asserts tokenizer IDENTITY and THEN round-trip. Before "
                         "2026-08-18 it asserted round-trip alone and was blind to a "
                         "tokenizer swap (FINDING 17)."}
    if reason:
        out["reason"] = reason
    return out


# ---------------------------------------------------------------------------
# G4.13 -- fold isolation, counted from the shard the trainer LOADED
# ---------------------------------------------------------------------------
def gate_g4_13(train_recs, held_out_country):
    n = len(train_recs)
    by_country = defaultdict(int)
    for r in train_recs:
        by_country[r["country"]] += 1
    leak = by_country.get(held_out_country, 0)
    # V4.f: FAIL, not pass, on an empty or single-country shard
    if n == 0:
        return {"gate": "G4.13", "verdict": "FAIL", "reason": "empty shard",
                "n_train": 0, "by_country": {}}
    if len(by_country) < 2:
        return {"gate": "G4.13", "verdict": "FAIL",
                "reason": "shard carries fewer than two countries -- an isolation check "
                          "over a one-country shard finds zero held-out records for the "
                          "wrong reason (V4.f)",
                "n_train": n, "by_country": dict(by_country)}
    return {"gate": "G4.13",
            "verdict": "PASS" if leak <= TH.G4_13_MAX_HELDOUT_RECORDS_IN_TRAIN else "FAIL",
            "held_out_country": held_out_country, "n_train": n,
            "n_heldout_country_in_train": leak, "by_country": dict(by_country),
            "counted_from": "the shard the trainer loaded"}


# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# G4.11 -- run manifest completeness
# ---------------------------------------------------------------------------
# 🔴 FINDING 4, found while wiring the perturbation battery: `drop_revision` removed
# `base_revision` from the manifest and NOTHING CHECKED IT. The perturbation would have
# been reported as "did not fell its gate" when the truth is that G4.11 had no verdict
# at all -- it existed only as a `fail()` earlier in the run, on a different condition.
# A perturbation that cannot fell its gate because the gate is not there is the exact
# vacuity this project's battery exists to catch, and it was caught by writing the
# battery rather than by running it.
G4_11_REQUIRED = ["run", "fold", "held_out_country", "leg", "run_type",
                  "base_repo", "base_revision", "tokenizer_repo",
                  "corpus_md5", "prereg_md5", "seed", "config"]


def gate_g4_11(manifest):
    missing = [k for k in G4_11_REQUIRED
               if k not in manifest or manifest[k] in (None, "", [], {})]
    nested = []
    ts = manifest.get("train_shard") or {}
    for k in ["path", "md5", "n_loaded"]:
        if k not in ts or ts[k] in (None, "", 0):
            nested.append("train_shard.%s" % k)
    missing = missing + nested
    return {"gate": "G4.11", "verdict": "PASS" if not missing else "FAIL",
            "n_required": len(G4_11_REQUIRED) + 3, "missing": missing,
            "note": "a run that cannot say which weights it started from is not "
                    "reproducible, however good its numbers are"}


# ---------------------------------------------------------------------------
# G4.14 -- pre-registration precedence. V4.g: recompute FROM DISK.
# ---------------------------------------------------------------------------
def gate_g4_14(prereg=None, sidecar=None):
    prereg = prereg or PREREG
    sidecar = sidecar or PREREG_SIDECAR
    if not os.path.exists(prereg):
        return {"gate": "G4.14", "verdict": "FAIL", "reason": "prereg.md absent"}
    if not os.path.exists(sidecar):
        return {"gate": "G4.14", "verdict": "FAIL", "reason": "recorded md5 sidecar absent"}
    live = md5_of_file(prereg)
    with open(sidecar, "r", encoding="utf-8") as fh:
        recorded = fh.read().strip().split()[0]
    return {"gate": "G4.14", "verdict": "PASS" if live == recorded else "FAIL",
            "path_checked": prereg,
            "md5_recomputed_from_disk": live, "md5_recorded": recorded,
            "note": "recomputed from the file on disk (V4.g), never read from the manifest "
                    "this gate is checking"}


# ---------------------------------------------------------------------------
# 4.4 detector 1 -- delimiter vs content perplexity, and activity entropy
# ---------------------------------------------------------------------------
DELIM_CHARS = set(",;|")


def delimiter_token_ids(tokenizer, limit=None):
    """Token ids whose decoded string is entirely delimiter characters."""
    ids = set()
    vocab_size = len(tokenizer)
    for i in range(vocab_size if limit is None else min(limit, vocab_size)):
        try:
            s = tokenizer.decode([i])
        except Exception:
            continue
        if s and all(ch in DELIM_CHARS for ch in s):
            ids.add(i)
    return ids


# 🔴 D-S4-4 (author ruling, 2026-08-19) -- FINDING 28.
#
# An absent ACT2 is serialised as TWO ADJACENT COMMAS, and the dolma2 BPE emits that
# pair as a SINGLE token. `delimiter_token_ids` admits it, because every character in
# it is a delimiter character -- so the question "did this respondent record a secondary
# activity?" was being scored in the DELIMITER bucket, and G4.2's first arm charged the
# model for failing to predict it.
#
# It is not a format decision. Measured on the corpus the trainer actually read
# (`4J_step3_corpus.jsonl`, md5 ca89d2295603c547f2384a40dd1909ba), a model of
# P(act2 empty | country, act) fitted on 80 % of the uk+it records and scored on the
# held-out 20 % still pays 0.2740 nats at each such token, which is 0.0480 nats per
# delimiter token -- 96 % of the 0.05 band, spent before the model predicts a single
# real delimiter. Richer conditioning does not rescue it: (country, act, loc, dur band)
# moves it to 0.0477. The decision is genuinely stochastic, so NO training budget closes
# the gap. That is why FINDING 25's power-law fit ran to 10^12 records.
#
# The BAND IS NOT MOVED. It stays at 0.05. What moves is which tokens the arm is
# measured over: delimiters whose presence is FORCED by the record grammar.
#
# 🔴 Two costs, both declared rather than absorbed:
#   1. Dropping the ",," token also drops the ACT-terminating comma FUSED INTO IT, which
#      IS structurally forced. The exclusion is therefore slightly WIDER than the defect.
#      Excluding a forced delimiter makes the arm harder to pass, not easier, so the
#      error is in the conservative direction -- but it is an error and it is recorded.
#   2. The excluded tokens are NOT moved into the content bucket. `content_loss` feeds
#      G4.9, which has been SEEN FALLING and is credited in DoD item 6; re-basing its
#      input to fix G4.2 would disturb a gate that is already working. They are scored
#      in neither bucket and reported on their own line instead.
#
# 🔴 REGISTRATION. This basis was chosen AFTER seeing the 0.1094 readings. It is recorded
# in `4thJ_04_finetuneLLM_val.md` before the re-run, with its perturbation row, and it
# must be SEEN FAILING there. It may not be presented as though it had been
# pre-registered. The old basis is still computed and still reported as
# `delimiter_loss_all_basis`, so every historical number stays comparable.
def forced_delimiter_token_ids(tokenizer, all_delim_ids):
    """The subset of `all_delim_ids` whose presence the record grammar forces.

    Concretely: drop any delimiter token whose decoding contains two adjacent commas,
    which is the empty-ACT2 slot and nothing else -- ACT is a fixed 3 digits, LOC is one
    of five closed values none of which prefixes another, and DUR/COP terminate their own
    numbers.
    """
    forced, dropped = set(), {}
    for i in sorted(all_delim_ids):
        try:
            s = tokenizer.decode([i])
        except Exception:
            continue
        if ",," in s:
            dropped[i] = s
        else:
            forced.add(i)
    return forced, dropped


@torch.no_grad()
def detector_delim_vs_content(model, loader, delim_ids, device, forced_ids=None):
    """Delimiter/content split.

    `delimiter_loss` is scored over `forced_ids` (D-S4-4) and is the number G4.2's first
    arm reads. `delimiter_loss_all_basis` is the pre-D-S4-4 number over every delimiter
    token, computed and reported so the 0.1094 readings stay comparable. `content_loss`
    is UNCHANGED on both bases -- it is G4.9's input and is not re-based here.
    """
    if forced_ids is None:
        forced_ids = delim_ids
    model.eval()
    d_loss_sum, d_n = 0.0, 0            # forced basis -- the gate reads this
    a_loss_sum, a_n = 0.0, 0            # old all-delimiter basis -- reported only
    c_loss_sum, c_n = 0.0, 0
    x_loss_sum, x_n = 0.0, 0            # the excluded act2-slot tokens, on their own line
    for input_ids, labels, attn in loader:
        input_ids, labels, attn = input_ids.to(device), labels.to(device), attn.to(device)
        out = model(input_ids=input_ids, attention_mask=attn)
        logits = out.logits[:, :-1, :]
        tgt = labels[:, 1:]
        mask = tgt != TH.G4_5_REQUIRED_LABEL
        if mask.sum() == 0:
            continue
        lp = F.cross_entropy(
            logits.reshape(-1, logits.size(-1)).float(),
            tgt.reshape(-1).clamp(min=0),
            reduction="none").view(tgt.shape)
        is_delim = torch.zeros_like(tgt, dtype=torch.bool)
        for did in delim_ids:
            is_delim |= (tgt == did)
        is_forced = torch.zeros_like(tgt, dtype=torch.bool)
        for did in forced_ids:
            is_forced |= (tgt == did)
        am = mask & is_delim
        dm = mask & is_forced
        xm = am & (~is_forced)
        cm = mask & (~is_delim)
        d_loss_sum += float((lp * dm).sum()); d_n += int(dm.sum())
        a_loss_sum += float((lp * am).sum()); a_n += int(am.sum())
        x_loss_sum += float((lp * xm).sum()); x_n += int(xm.sum())
        c_loss_sum += float((lp * cm).sum()); c_n += int(cm.sum())
    return {"delimiter_loss": d_loss_sum / d_n if d_n else float("nan"),
            "delimiter_tokens": d_n,
            "delimiter_basis": "forced delimiters only (D-S4-4, FINDING 28)",
            "delimiter_loss_all_basis": a_loss_sum / a_n if a_n else float("nan"),
            "delimiter_tokens_all_basis": a_n,
            "act2_slot_loss": x_loss_sum / x_n if x_n else float("nan"),
            "act2_slot_tokens": x_n,
            "content_loss": c_loss_sum / c_n if c_n else float("nan"),
            "content_tokens": c_n}


def activity_entropy_nats(texts):
    counts = defaultdict(int)
    total = 0
    for t in texts:
        try:
            _, body = split_prefix_body(t)
        except ValueError:
            continue
        eps, _ = parse_episodes(body)
        for e in eps:
            counts[e[1]] += 1
            total += 1
    if total == 0:
        return float("nan")
    h = 0.0
    for c in counts.values():
        p = c / float(total)
        h -= p * math.log(p)
    return h


# ---------------------------------------------------------------------------
# 4.4 detector 2 / G4.1 -- within-stratum variance ratio
# ---------------------------------------------------------------------------
def gate_g4_1(real_texts, gen_texts):
    real_by, gen_by = defaultdict(list), defaultdict(list)
    for t in real_texts:
        s, v = stratum_of(t), at_home_share(t)
        if s and v is not None:
            real_by[s].append(v)
    for t in gen_texts:
        s, v = stratum_of(t), at_home_share(t)
        if s and v is not None:
            gen_by[s].append(v)

    rows = []
    for s, rv in real_by.items():
        gv = gen_by.get(s, [])
        if len(rv) < TH.G4_1_MIN_STRATUM_N or len(gv) < TH.G4_1_MIN_STRATUM_N:
            continue
        vr_real = float(np.var(rv))
        vr_gen = float(np.var(gv))
        if vr_real <= 0:
            continue
        rows.append({"stratum": "|".join(s), "n_real": len(rv), "n_gen": len(gv),
                     "var_real": vr_real, "var_gen": vr_gen, "vr": vr_gen / vr_real})

    if len(rows) < TH.V4_A_MIN_STRATA:
        return {"gate": "G4.1", "verdict": "FAIL",
                "reason": "V4.a: only %d strata have N >= %d on BOTH sides. A variance "
                          "gate evaluated on that many strata is satisfied by nothing, so "
                          "it FAILs rather than skipping."
                          % (len(rows), TH.G4_1_MIN_STRATUM_N),
                "n_scorable_strata": len(rows), "statistic": TH.G4_1_STATISTIC}

    low = [r for r in rows if r["vr"] < TH.G4_1_VR_LOW]
    high = [r for r in rows if r["vr"] > TH.G4_1_VR_HIGH]
    return {"gate": "G4.1", "verdict": "PASS" if not low and not high else "FAIL",
            "statistic": TH.G4_1_STATISTIC,
            "band": [TH.G4_1_VR_LOW, TH.G4_1_VR_HIGH],
            "n_scorable_strata": len(rows),
            "n_below_band_COLLAPSE_END": len(low),
            "n_above_band": len(high),
            "which_end": ("lower (collapse)" if low and not high else
                          "upper" if high and not low else
                          "both" if low and high else "none"),
            "worst_low": min((r["vr"] for r in rows), default=None),
            "worst_high": max((r["vr"] for r in rows), default=None)}


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------
@torch.no_grad()
def generate_samples(model, tokenizer, recs, device, n, max_new_tokens=1200,
                     stratified_k=0, per_stratum=None, gen_batch=8, ref_recs=None):
    """Generate diaries from real prefixes.

    🔴 FINDING 8: the original sampler drew prefixes at RANDOM, and G4.1 requires
    N >= 100 generated diaries in each of at least 5 strata (V4.a). Under a random draw
    that needs many thousands of generations, because the corpus has hundreds of strata
    and the draw follows their natural, very uneven distribution. G4.1 would therefore
    have FAILED with V4.a's reason at every affordable generation volume -- a gate that
    can never be satisfied is not a gate, it is a permanent red light, and after a few
    runs it would have been read as noise. `stratified_k` draws `per_stratum` prefixes
    from each of the K largest eligible strata instead, so the gate is REACHABLE at
    K * per_stratum generations. The strata are chosen by REAL count only, never by
    anything measured on the generated side.

    🔴 FINDING 11: FINDING 8's fix was still not enough. Eligibility was counted on the
    held-in VALIDATION split, and job 1266866 showed that split reaches N >= 100 in
    ZERO strata on all three folds (429/416/421 strata over 5,520/3,434/5,702 diaries;
    the largest holds 84). G4.1 was therefore unsatisfiable on every fold, and the run
    printed `0 strata x 100 = 0 diaries` and then scored G4.4 and G4.12 on nothing.
    `ref_recs` is the full held-in REAL set (train + val), where 166/112/168 strata
    qualify. The band (0.80-1.25), the N >= 100 rule and V4.a are all untouched -- what
    changed is how many real diaries estimate the real variance, and more of the same
    population can only sharpen that estimate. Prefixes are still drawn from `recs`.
    """
    model.eval()
    # generation needs the KV cache back; training turned it off for checkpointing.
    if hasattr(model, "config"):
        model.config.use_cache = True
    rng = random.Random(TH.SEED)

    if stratified_k:
        per_stratum = per_stratum or TH.G4_1_MIN_STRATUM_N
        ref = ref_recs if ref_recs else recs
        by_ref, by_draw = defaultdict(list), defaultdict(list)
        for r in ref:
            s = stratum_of(r["text"])
            if s:
                by_ref[s].append(r)
        for r in recs:
            s = stratum_of(r["text"])
            if s:
                by_draw[s].append(r)
        eligible = sorted([s for s in by_ref if len(by_ref[s]) >= TH.G4_1_MIN_STRATUM_N],
                          key=lambda s: (-len(by_ref[s]), s))[:stratified_k]
        print("stratified generation: %d strata x %d = %d diaries; eligible strata in "
              "the real reference set (%d diaries): %d"
              % (len(eligible), per_stratum, len(eligible) * per_stratum, len(ref),
                 sum(1 for s in by_ref if len(by_ref[s]) >= TH.G4_1_MIN_STRATUM_N)))
        if len(eligible) < TH.V4_A_MIN_STRATA:
            print("🔴 only %d strata reach N >= %d in the REAL reference set. G4.1 cannot "
                  "be satisfied on this fold at any generation volume, and will FAIL with "
                  "V4.a's reason. That is the guard, not a defect."
                  % (len(eligible), TH.G4_1_MIN_STRATUM_N))
        sample = []
        for s in eligible:
            # prefixes come from `recs`; the reference set only decides WHICH strata are
            # scorable. A stratum with no record in `recs` falls back to the reference.
            pool = by_draw.get(s) or by_ref[s]
            # with replacement: the same prefix generates a different diary each time,
            # which is the quantity G4.1 measures (within-stratum spread)
            sample.extend([rng.choice(pool) for _ in range(per_stratum)])
    else:
        sample = rng.sample(recs, min(n, len(recs)))

    # 🔴 FINDING 12: nothing ever told `generate` how a diary ends, so every generation
    # ran the full max_new_tokens budget even after emitting <eor>. With FINDING 11 making
    # G4.1 reachable at 600 generations per epoch that is hours of wall-clock spent past
    # the end of the text. <eor> is an ordinary token, not a special one, so it survives
    # skip_special_tokens and the "gen-terminated" counter still measures what it did.
    eor_ids = tokenizer(TH.G4_7_EOR, add_special_tokens=False)["input_ids"]
    eos_arg = eor_ids[-1] if len(eor_ids) == 1 else None
    # FINDING 12, second half: <eor> tokenises to THREE ids, so eos_token_id -- which
    # accepts a single id -- cannot express it, and job 1266877 ran the full 1280-token
    # budget on all 600 diaries. transformers 4.57 stop_strings does express it, and it
    # also makes the returned text END at <eor> rather than trailing whatever the model
    # emits afterwards, which the episode parser would otherwise have to read as data.
    stop_kw = ({"eos_token_id": eos_arg} if eos_arg is not None
               else {"stop_strings": [TH.G4_7_EOR], "tokenizer": tokenizer})
    print("generation stop token: %s -> ids %s, %s"
          % (TH.G4_7_EOR, eor_ids,
             "wired as eos_token_id" if eos_arg is not None else
             "MULTI-TOKEN, wired as stop_strings"))

    # left padding, because a decoder-only model must have its prompt flush right
    old_side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    out_texts = []
    try:
        for i in range(0, len(sample), gen_batch):
            chunk = sample[i:i + gen_batch]
            prefixes = [split_prefix_body(r["text"])[0] for r in chunk]
            enc = tokenizer(prefixes, add_special_tokens=False, return_tensors="pt",
                            padding=True).to(device)
            gkw = stop_kw
            gen = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=True,
                                 temperature=1.0, top_p=1.0,
                                 pad_token_id=tokenizer.pad_token_id, **gkw)
            for row in gen:
                out_texts.append(tokenizer.decode(row, skip_special_tokens=True))
            if i % (gen_batch * 10) == 0:
                print("    generated %d/%d" % (len(out_texts), len(sample)), flush=True)
    finally:
        tokenizer.padding_side = old_side
    return sample, out_texts


_CRASH_STATE = {}


def _flush_detectors_on_crash(exc):
    """Write whatever gate verdicts exist before the process dies (FINDING 19).

    A crash is not a verdict. Gates scored BEFORE the exception are real measurements and
    are kept; gates never reached are left absent rather than invented. The file is marked
    `crashed` so no reader can mistake a partial run for a complete one.
    """
    st = _CRASH_STATE
    if not st.get("detectors") or not st.get("outdir"):
        print("FINDING 19 flush: nothing to write -- the run died before the detectors "
              "dict was assembled. Gates printed above this point, if any, are NOT in any "
              "file and this run will read NOT RUN.")
        return
    try:
        det = st["detectors"]
        det["crashed"] = {"exception": type(exc).__name__, "message": str(exc)[:2000],
                          "note": "FINDING 19: gates scored before this exception are real "
                                  "and are kept. Gates never reached are ABSENT, not PASS. "
                                  "This run is NOT complete."}
        os.makedirs(st["outdir"], exist_ok=True)
        with open(os.path.join(st["outdir"], "detectors_%s.json" % st["run_name"]), "w",
                  encoding="utf-8") as fh:
            json.dump(det, fh, indent=2, sort_keys=True, default=str)
        print("FINDING 19 flush: detectors_%s.json written with the gates scored before the "
              "crash" % st["run_name"])
    except Exception as fexc:
        # A failing flusher must never mask the original exception.
        print("FINDING 19 flush FAILED (%s: %s) -- the original exception follows"
              % (type(fexc).__name__, fexc))



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    ap.add_argument("--leg", type=int, required=True, choices=[4, 5])
    ap.add_argument("--run-type", required=True,
                    choices=["pilot", "primary", "ceiling", "qwen", "perturb"])
    ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--max-len", type=int, default=1280)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--eval-batch-size", type=int, default=4,
                    help="evaluation runs under no_grad, so it can afford a wider batch "
                         "than training. Never smaller than --batch-size.")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--gen-n", type=int, default=200)
    ap.add_argument("--gen-stratified-k", type=int, default=0,
                    help="generate 100 diaries in each of the K largest eligible strata "
                         "instead of drawing at random. G4.1 is unreachable without it "
                         "(FINDING 8). 0 = random draw.")
    ap.add_argument("--gen-batch", type=int, default=8)
    ap.add_argument("--limit-train", type=int, default=None,
                    help="pilot only: cap training records, for a short schedule")
    ap.add_argument("--perturbation", default=None,
                    help="deliberately break one thing, for the seen-failing battery")
    ap.add_argument("--out", default=os.path.join(STEP4, "runs"))
    args = ap.parse_args()

    # 🔴 Vacuity guard, added 2026-08-18 while wiring `collapse_content`. `--perturbation`
    # had no whitelist, so a MISSPELLED name ran a perfectly clean baseline and was then
    # scored as "DID NOT FELL ITS GATE" -- indistinguishable in the table from a
    # perturbation that genuinely failed to move its gate. A battery that cannot tell a
    # typo from a negative result is not a battery. Unknown names now stop the run.
    KNOWN_PERTURBATIONS = {
        "pad_labels_1pct", "perturb_merged_weight", "strip_eor_1pct", "swap_tokenizer",
        "collapse_content", "sequential_countries", "drop_revision", "leak_1pct",
        "edit_prereg", "no_prefix", "freeze_adapter",
    }
    if args.perturbation is not None and args.perturbation not in KNOWN_PERTURBATIONS:
        fail("unknown --perturbation %r. Known: %s. A name that matches nothing would "
             "have trained a CLEAN run and been scored as a perturbation that did not "
             "fell its gate."
             % (args.perturbation, ", ".join(sorted(KNOWN_PERTURBATIONS))))

    run_name = "leg%d_%s_fold_%s" % (args.leg, args.run_type, args.fold)
    if args.perturbation:
        run_name += "__PERTURB_%s" % args.perturbation
    outdir = os.path.join(args.out, run_name)
    os.makedirs(outdir, exist_ok=True)

    torch.manual_seed(TH.SEED)
    random.seed(TH.SEED)
    np.random.seed(TH.SEED)

    print("=" * 78)
    # V4.h: say which fold, and which country it holds out, BEFORE any verdict
    print("RUN %s" % run_name)
    print("FOLD %s  ->  HELD-OUT COUNTRY: %s" % (args.fold, args.fold))
    print("LEG %d   RUN TYPE %s   PERTURBATION %s"
          % (args.leg, args.run_type, args.perturbation or "none"))
    print("=" * 78)

    # ---- G4.14 first: nothing is allowed to run against an unfrozen prereg ----
    # 🔴 The `edit_prereg` perturbation NEVER touches the real pre-registration. Editing
    # it would fail G4.14 on every run in the project at once, including runs that already
    # passed, and the damage would outlive this battery. Instead the file and its sidecar
    # are COPIED into this run's own directory, one byte is appended to the copy, and the
    # gate is pointed at the copy. The original is not opened for writing at any point.
    pr_path, sc_path = PREREG, PREREG_SIDECAR
    if args.perturbation == "edit_prereg":
        import shutil
        pr_path = os.path.join(outdir, "prereg_TAMPERED_COPY.md")
        sc_path = os.path.join(outdir, "prereg_TAMPERED_COPY.md.md5")
        shutil.copyfile(PREREG, pr_path)
        shutil.copyfile(PREREG_SIDECAR, sc_path)
        with open(pr_path, "a", encoding="utf-8") as fh:
            fh.write("\n")          # one byte, enough to move the hash
        print("PERTURBATION edit_prereg: tampering with a COPY at %s; the real "
              "prereg.md is untouched (md5 on disk %s)" % (pr_path, md5_of_file(PREREG)))
    g14 = gate_g4_14(pr_path, sc_path)
    print("G4.14 %s  live=%s recorded=%s"
          % (g14["verdict"], g14.get("md5_recomputed_from_disk"), g14.get("md5_recorded")))
    if g14["verdict"] != "PASS" and args.perturbation != "edit_prereg":
        fail("G4.14 FAILED and this run is not the G4.14 perturbation. "
             "A run against an unfrozen or altered pre-registration is not a run.")

    # ---- shards ----
    shard_manifest = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    fold_m = shard_manifest["folds"][args.fold]
    train_path = fold_m["train"]["path"]
    val_path = fold_m["heldin_val"]["path"]
    train_recs = read_jsonl(train_path)
    val_recs = read_jsonl(val_path)

    # 🔴 FINDING 11: G4.1's real reference. Snapshotted HERE, before any perturbation and
    # before --limit-train, so that (a) leak_1pct cannot put held-out-country records into
    # the reference, (b) strip_eor_1pct's in-place edit cannot reach it, and (c) the
    # reference is the fold's data rather than whatever slice this run happened to train
    # on -- which is what makes G4.1 comparable between the pilot and the full folds.
    real_ref = [{"text": r["text"], "country": r.get("country")}
                for r in train_recs + val_recs]

    if args.perturbation == "leak_1pct":
        xfer = read_jsonl(fold_m["transfer"]["path"])
        k = max(1, int(round(0.01 * len(train_recs))))
        train_recs = train_recs + random.Random(TH.SEED).sample(xfer, k)
        print("PERTURBATION leak_1pct: injected %d held-out-country records into train" % k)

    if args.limit_train:
        # 🔴 FINDING, pilot job 1266825: a plain `train_recs[:n]` truncation took the
        # first 4,000 records of a country-ORDERED shard and produced a single-country
        # training set. `G4.13`'s V4.f guard caught it -- "an isolation check over a
        # one-country shard finds zero held-out records for the wrong reason". Nothing
        # in the loss would have said so, and the recipe forbids sequential
        # single-country training outright ("Joint multi-country training, never
        # sequential. Sequential costs 40 to 70 % on earlier countries").
        # The cap is now taken PROPORTIONALLY PER COUNTRY, and the result is asserted.
        by_c = defaultdict(list)
        for r in train_recs:
            by_c[r["country"]].append(r)
        total = len(train_recs)
        capped = []
        rr = random.Random(TH.SEED)
        for c in sorted(by_c):
            share = int(round(args.limit_train * len(by_c[c]) / float(total)))
            share = max(1, min(share, len(by_c[c])))
            capped.extend(rr.sample(by_c[c], share))
        rr.shuffle(capped)
        got = defaultdict(int)
        for r in capped:
            got[r["country"]] += 1
        if len(got) < len(by_c):
            fail("the training cap dropped a country: kept %s of %s. A pilot that "
                 "trains on one country is not the pilot the recipe specifies."
                 % (dict(got), sorted(by_c)))
        train_recs = capped
        print("pilot: training records capped at %d, proportional per country: %s"
              % (len(train_recs), dict(sorted(got.items()))))

    print("train records loaded: %d   held-in val: %d" % (len(train_recs), len(val_recs)))

    # ---- G4.13, from the shard actually loaded ----
    g13 = gate_g4_13(train_recs, args.fold)
    print("G4.13 %s  heldout-country records in train = %s  by_country=%s"
          % (g13["verdict"], g13.get("n_heldout_country_in_train"), g13.get("by_country")))


    # 🔴 FINDING 5, found while wiring the battery: `strip_eor_1pct` was applied inside
    # DiaryDataset, but G4.7 is scored on `train_recs` -- so the perturbation removed
    # <eor> from what the model SAW while the gate went on reading unmodified records and
    # PASSED. The perturbation would have been logged as "did not fell its gate" when in
    # fact it never reached it. The corruption is moved here, to the records the gate
    # actually reads, which is also the honest place for it: the claim under test is that
    # a corpus with missing terminators is detected.
    if args.perturbation == "strip_eor_1pct":
        rr = random.Random(TH.SEED)
        n_stripped = 0
        for r in train_recs:
            if rr.random() < 0.01:
                r["text"] = r["text"].replace(TH.G4_7_EOR, "")
                n_stripped += 1
        print("PERTURBATION strip_eor_1pct: <eor> removed from %d of %d training records"
              % (n_stripped, len(train_recs)))
    # 🔴 FINDING 18 companion (implementer-side, additive -- no gate changes what it
    # asserts). `G4.2` is the format-collapse halt: it FAILs when delimiter_loss < 0.05
    # AND generated activity entropy < 1.5, strictly on BOTH arms (V4.d). That is the
    # model having learned the record FORMAT perfectly while emitting degenerate CONTENT.
    # No perturbation in the pre-registered set produced that condition, which is why
    # G4.2 sat in the coverage clause's `never made to fall` list beside G4.8.
    #
    # `collapse_content` produces it directly: every delimiter is left exactly where it
    # was -- the prefix, the `|`, the `;` between episodes, the `,` between fields and the
    # trailing <eor> are all untouched -- and only the VALUES are replaced, by one
    # constant episode repeated. A model trained on this learns the format in a few steps
    # (delimiter loss -> ~0) and can generate only one activity (entropy -> ~0), so both
    # arms of the halt cross together.
    #
    # Adding a perturbation is REQUIRED by the coverage clause, which says a gate never
    # seen failing is not evidence. No existing EXPECTED row is edited, so this is not a
    # change to the pre-registration of anything already measured.
    if args.perturbation == "collapse_content":
        # 🔴 FINDING 20, job 1270491. The first version of this perturbation replaced every
        # episode with the constant `060,110,000,1,1`, which flattened the DURATIONS as well
        # as the activities. It drove generated entropy to exactly 0.000 -- but it drove the
        # delimiter loss the WRONG WAY, 0.109 -> 1.73, so `G4.2` correctly PASSed on one arm
        # and the gate stayed unfelled.
        #
        # The cause is where the delimiter loss is measured: `detector_delim_vs_content` runs
        # on the HELD-IN VALIDATION loader, which this perturbation does not touch and must
        # not touch. Training on flattened durations moves the model off the real record
        # distribution, so it gets worse at predicting real delimiters -- the OPPOSITE of the
        # condition `G4.2` encodes, which is a model that has learned the format PERFECTLY
        # while emitting degenerate CONTENT.
        #
        # So only the activity fields are collapsed. `DUR`, `LOC` and `COP` keep their real
        # values, every episode boundary stays where it was, and the record remains a
        # perfectly ordinary member of the training distribution in every respect except
        # that one column is now constant. Generated activity entropy -> 0 because the model
        # has never seen a second activity code; the delimiter loss is free to fall because
        # nothing about the format changed.
        coll_act = TH.G4_2_COLLAPSE_EPISODE.split(",")[1]
        coll_act2 = TH.G4_2_COLLAPSE_EPISODE.split(",")[2]
        n_flat, n_eps_done, n_skipped = 0, 0, 0
        for r in train_recs:
            try:
                prefix, body = split_prefix_body(r["text"])
            except ValueError:
                n_skipped += 1
                continue
            has_eor = TH.G4_7_EOR in body
            core = body.replace(TH.G4_7_EOR, "")
            out_eps = []
            for ep_s in core.split(";"):
                if not ep_s.strip():
                    continue
                f = [x.strip() for x in ep_s.split(",")]
                if len(f) != 5:
                    # Not our record shape. Leave it exactly as it was rather than
                    # inventing fields -- a perturbation that silently repairs malformed
                    # input is measuring something other than what it claims.
                    out_eps.append(ep_s.strip())
                    continue
                f[1], f[2] = coll_act, coll_act2
                out_eps.append(",".join(f))
                n_eps_done += 1
            if not out_eps:
                n_skipped += 1
                continue
            r["text"] = (prefix + " " + "; ".join(out_eps)
                         + (" " + TH.G4_7_EOR if has_eor else ""))
            n_flat += 1
        if n_flat == 0:
            fail("collapse_content changed nothing -- it would have trained a CLEAN run and "
                 "been scored as a perturbation that did not fell its gate (FINDING 20 is "
                 "exactly that failure mode read from the other side).")
        print("PERTURBATION collapse_content: ACT<-%s ACT2<-%s in %d episodes across %d of "
              "%d training records (%d records skipped); DUR, LOC and COP keep their real "
              "values and every delimiter and every <eor> is left in place"
              % (coll_act, coll_act2, n_eps_done, n_flat, len(train_recs), n_skipped))

    # ---- G4.7 on the training completions ----
    g7 = gate_g4_7(train_recs)
    print("G4.7 %s  %d/%d completions terminate with %s"
          % (g7["verdict"], g7["n_terminated"], g7["n"], TH.G4_7_EOR))

    # ---- model ----
    from transformers import AutoModelForCausalLM, AutoTokenizer
    staged = json.load(open(STAGED, "r", encoding="utf-8"))
    # 🔴 Leg 4 is defined as "full pipeline, SMALL model, short schedule". The model
    # therefore follows the LEG, not the run-type: a --leg 4 run is always the 1B
    # backbone even when its run-type is `primary`, so that a Leg-4 fold and the Leg-4
    # pilot are the same experiment at different data volumes. Reading the model off the
    # run-type would have silently made Leg-4 folds 7B runs.
    repo = MODEL_FOR["pilot"] if args.leg == 4 else MODEL_FOR[args.run_type]
    rev = None
    for r in staged["repos"]:
        if r["repo_id"] == repo:
            rev = r["revision"]
    if rev is None:
        fail("no staged revision for %s -- G4.11: a checkpoint named without a revision "
             "is not a reproducible checkpoint" % repo)
    print("base %s @ %s" % (repo, rev))

    tok_repo = repo
    if args.perturbation == "swap_tokenizer":
        tok_repo = "bert-base-uncased"
        print("PERTURBATION swap_tokenizer: tokenizer <- %s" % tok_repo)
    tokenizer = AutoTokenizer.from_pretrained(tok_repo, revision=(rev if tok_repo == repo else None))
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ---- G4.8 before any generation ----
    g8 = gate_g4_8(tokenizer, train_recs, base_repo=repo)
    # 🔴 FINDING 10 shape again: print the numbers that decided the verdict, both arms,
    # so a FAIL never has to be looked up in the JSON to be understood.
    print("G4.8 %s  identity=%s (holding %s, base %s)  round-trip %d/%d exact"
          % (g8["verdict"],
             g8["identity"].get("match") if g8["identity"]["checked"] else "NOT CHECKED",
             g8["identity"].get("tokenizer_name_or_path", "?"),
             g8["identity"].get("expected_base_repo", "?"),
             g8["n_roundtrip_ok"], g8["n"]))
    if g8.get("reason"):
        print("     G4.8 reason: %s" % g8["reason"])

    model = AutoModelForCausalLM.from_pretrained(
        repo, revision=rev, torch_dtype=torch.bfloat16)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    if args.run_type != "ceiling":
        from peft import LoraConfig, get_peft_model
        lcfg = LoraConfig(
            r=TH.LORA_R, lora_alpha=TH.LORA_ALPHA, lora_dropout=TH.LORA_DROPOUT,
            target_modules=TH.LORA_TARGET_MODULES, use_rslora=TH.USE_RSLORA,
            bias="none", task_type="CAUSAL_LM")
        model = get_peft_model(model, lcfg)
        model.print_trainable_parameters()
    else:
        print("ceiling run: FULL fine-tune, no adapter")

    # FINDING 2, job 1266826: the pilot OOMed at ep0 step~200 on the 20 GB MIG slice,
    # and the traceback named THREE other processes on the same physical card
    # (7.88 + 10.30 + 15.74 GiB). `--gres=gpu:1` buys a slice, not a machine, and the
    # memory actually available is set by strangers. Activation memory is the only
    # part we control, so it is checkpointed. G4.10 reports peak memory, so the cost
    # of this choice stays visible in the run manifest rather than being absorbed.
    model.gradient_checkpointing_enable()
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    model.config.use_cache = False
    print("gradient checkpointing ENABLED, use_cache=False during training")

    if args.perturbation == "freeze_adapter":
        for p in model.parameters():
            p.requires_grad_(False)
        print("PERTURBATION freeze_adapter: zero trainable parameters")

    # ---- data ----
    train_ds = DiaryDataset(train_recs, tokenizer, args.max_len, args.perturbation)
    val_ds = DiaryDataset(val_recs, tokenizer, args.max_len, args.perturbation)
    pad_id = tokenizer.pad_token_id
    coll = lambda b: collate(b, pad_id, args.perturbation)
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, collate_fn=coll)
    eval_bs = max(args.batch_size, args.eval_batch_size)
    val_dl = DataLoader(val_ds, batch_size=eval_bs, shuffle=False, collate_fn=coll)

    # ---- G4.5 on the loader the trainer will actually iterate ----
    # FINDING 3, job 1266850: FINDING 2's memory fix set the micro-batch to 1, and a
    # batch of one is never padded, so `G4.5` reported `0 pad positions` and FAILED.
    # The gate was right to fail -- a check with nothing to check is not a pass -- but
    # the property it exists to prove (the collate function labels every pad position
    # -100) is still worth proving, and `pad_labels_1pct` would have become a vacuous
    # perturbation too. So the trainer's own loader is REPORTED and the gate is SCORED
    # on a probe loader that is guaranteed to pad. The distinction is printed, never
    # collapsed: a run that pads nothing must not be able to claim a padding pass.
    g5 = gate_g4_5(train_dl, pad_id)
    g5["loader"] = "the TRAINING loader itself, batch %d" % args.batch_size
    if g5["pad_positions"] == 0:
        probe_bs = max(4, args.batch_size)
        probe_dl = DataLoader(train_ds, batch_size=probe_bs, shuffle=False, collate_fn=coll)
        g5_probe = gate_g4_5(probe_dl, pad_id)
        g5_probe["loader"] = "pad probe loader, batch %d" % probe_bs
        g5_probe["trainer_loader_result"] = g5
        g5_probe["note_finding_3"] = (
            "this run trains at batch size %d and therefore pads nothing; G4.5 is scored "
            "on a probe loader at batch %d, which proves the collate function, not this "
            "run's tensors" % (args.batch_size, probe_bs))
        print("G4.5 (trainer loader) NOT APPLICABLE -- batch size %d yields 0 pad "
              "positions. This is NOT a pass." % args.batch_size)
        print("G4.5 %s  %d pad positions, %d not masked  [SCORED on pad probe loader, batch %d]"
              % (g5_probe["verdict"], g5_probe["pad_positions"],
                 g5_probe["pad_positions_not_masked"], probe_bs))
        g5 = g5_probe
    else:
        print("G4.5 %s  %d pad positions, %d not masked"
              % (g5["verdict"], g5["pad_positions"], g5["pad_positions_not_masked"]))

    delim_ids = delimiter_token_ids(tokenizer)
    forced_ids, dropped_ids = forced_delimiter_token_ids(tokenizer, delim_ids)
    print("delimiter token ids: %d" % len(delim_ids))
    # 🔴 D-S4-4: print WHICH ids the arm dropped and what they decode to. A basis change
    # that cannot be read off the log is a basis change nobody can audit. If this prints
    # an empty dict the re-point did nothing and G4.2 is still on the old basis -- that
    # is a FINDING, not a detail.
    print("  D-S4-4 forced-delimiter basis: %d of %d ids kept; dropped %s"
          % (len(forced_ids), len(delim_ids),
             {i: repr(s) for i, s in dropped_ids.items()} or "NOTHING -- basis unchanged"))

    epochs = args.epochs if args.epochs is not None else (1 if args.leg == 4 else TH.EPOCHS_LEG5)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr) \
        if any(p.requires_grad for p in model.parameters()) else None

    metrics_rows = []
    detectors = {"run": run_name, "fold": args.fold, "held_out_country": args.fold,
                 "leg": args.leg, "run_type": args.run_type,
                 "perturbation": args.perturbation,
                 "gates_at_start": {"G4.14": g14, "G4.13": g13, "G4.7": g7,
                                    "G4.8": g8, "G4.5": g5},
                 "epochs": []}

    # 🔴 FINDING 19, job 1270491. `detectors_<run>.json` used to be written only in the LAST
    # block of main(), so ANY exception after this point discarded every gate already scored.
    # That is how `swap_tokenizer` was lost twice: D-S4-2 worked on its first attempt and
    # printed `G4.8 FAIL identity=False`, then the run died at generation on the old
    # `token_type_ids` ValueError and the row came back `NOT RUN` -- indistinguishable in the
    # coverage clause from a gate no perturbation can fell. The dict is handed to a module
    # global here so the top-level handler can flush it on the way out.
    #
    # Gates never reached are simply ABSENT from the flushed file. They are never written as
    # PASS, and `4thJ_step4_perturbtable.py` already renders a missing gate as `-`.
    _CRASH_STATE.update(outdir=outdir, run_name=run_name, detectors=detectors)

    t0 = time.time()

    # 🔴 FINDING 6, found while wiring the battery: the val doc's perturbation table lists
    # "Train country-by-country sequentially -> G4.9", and NO SUCH PERTURBATION EXISTED in
    # the trainer. Nine flags were implemented and this one was silently absent, so the
    # coverage clause would have reported G4.9 as "never made to fall" without anyone
    # noticing there was no lever to pull. Implemented here as the recipe's actual
    # prohibition (RL05: "joint multi-country training, never sequential"): epoch e trains
    # on ONE country, so the country trained first is measurably forgotten by the end.
    seq_loaders = None
    if args.perturbation == "sequential_countries":
        from torch.utils.data import Subset
        seq_countries = sorted({r["country"] for r in train_recs})
        seq_loaders = []
        for c in seq_countries:
            idxs = [i for i, r in enumerate(train_recs) if r["country"] == c]
            seq_loaders.append((c, DataLoader(Subset(train_ds, idxs),
                                              batch_size=args.batch_size,
                                              shuffle=True, collate_fn=coll)))
        print("PERTURBATION sequential_countries: %s, one country per epoch, in that order"
              % seq_countries)
    halted = False
    for ep in range(epochs):
        model.train()
        if hasattr(model, "config"):
            model.config.use_cache = False   # generation re-enabled it last epoch
        run_loss, nb = 0.0, 0
        ep_dl = train_dl if seq_loaders is None else seq_loaders[ep % len(seq_loaders)][1]
        if seq_loaders is not None:
            print("  epoch %d trains on country %s ONLY" % (ep, seq_loaders[ep % len(seq_loaders)][0]))
        for step, (input_ids, labels, attn) in enumerate(ep_dl):
            if opt is None:
                break
            input_ids, labels, attn = input_ids.to(device), labels.to(device), attn.to(device)
            out = model(input_ids=input_ids, attention_mask=attn, labels=labels)
            loss = out.loss / args.grad_accum
            loss.backward()
            if (step + 1) % args.grad_accum == 0:
                opt.step()
                opt.zero_grad()
            run_loss += float(out.loss)
            nb += 1
            if step % 200 == 0:
                print("  ep%d step%d loss %.4f" % (ep, step, float(out.loss)), flush=True)

        # ---- validation epoch: every detector, every epoch ----
        dv = detector_delim_vs_content(model, val_dl, delim_ids, device, forced_ids)
        real_sample, gen_texts = generate_samples(
            model, tokenizer, val_recs, device, args.gen_n,
            max_new_tokens=args.max_len, stratified_k=args.gen_stratified_k,
            gen_batch=args.gen_batch, ref_recs=real_ref)
        gen_entropy = activity_entropy_nats(gen_texts)
        # FINDING 11: the real side of G4.1 is the full held-in real set, not the
        # validation split, which reaches N >= 100 in zero strata on every fold.
        g1 = gate_g4_1([r["text"] for r in real_ref], gen_texts)

        # probe loss per training country (G4.9 input)
        probe_losses = {}
        for c, pm in fold_m["probes"].items():
            precs = read_jsonl(pm["path"])
            pds = DiaryDataset(precs, tokenizer, args.max_len)
            pdl = DataLoader(pds, batch_size=eval_bs, shuffle=False, collate_fn=coll)
            d = detector_delim_vs_content(model, pdl, delim_ids, device, forced_ids)
            # G4.9 reads content_loss, which D-S4-4 did NOT re-base. Unchanged on purpose.
            probe_losses[c] = d["content_loss"]

        # G4.2 halt condition -- V4.d, strict `<` on BOTH arms
        halt = (dv["delimiter_loss"] < TH.G4_2_DELIM_LOSS_HALT and
                gen_entropy < TH.G4_2_ACT_ENTROPY_HALT_NATS)
        g2 = {"gate": "G4.2",
              "verdict": "FAIL" if halt else "PASS",
              "delimiter_loss": dv["delimiter_loss"],
              "delimiter_basis": dv["delimiter_basis"],
              "delimiter_loss_all_basis": dv["delimiter_loss_all_basis"],
              "delimiter_tokens": dv["delimiter_tokens"],
              "delimiter_tokens_all_basis": dv["delimiter_tokens_all_basis"],
              "act2_slot_loss": dv["act2_slot_loss"],
              "act2_slot_tokens": dv["act2_slot_tokens"],
              "content_loss": dv["content_loss"],
              "activity_entropy_nats": gen_entropy,
              "basis_note": "D-S4-4 (2026-08-19, FINDING 28): the first arm is scored "
                            "over FORCED delimiters only. The band is unchanged at "
                            "%.2f. `delimiter_loss_all_basis` is the pre-ruling number "
                            "and is what every reading before 2026-08-19 reports."
                            % TH.G4_2_DELIM_LOSS_HALT,
              "halt_rule": "delimiter_loss < %.2f AND activity_entropy < %.2f (strict on "
                           "both arms, V4.d)" % (TH.G4_2_DELIM_LOSS_HALT,
                                                 TH.G4_2_ACT_ENTROPY_HALT_NATS)}

        gen_term = sum(1 for t in gen_texts if t.rstrip().endswith(TH.G4_7_EOR))
        row = {
            "run": run_name, "fold": args.fold, "held_out_country": args.fold,
            "leg": args.leg, "run_type": args.run_type,
            "perturbation": args.perturbation or "", "epoch": ep,
            "train_loss": run_loss / nb if nb else float("nan"),
            "delimiter_loss": dv["delimiter_loss"], "content_loss": dv["content_loss"],
            "delimiter_loss_all_basis": dv["delimiter_loss_all_basis"],
            "act2_slot_loss": dv["act2_slot_loss"],
            "activity_entropy_nats": gen_entropy,
            "g4_1_verdict": g1["verdict"],
            "g4_1_n_strata": g1.get("n_scorable_strata"),
            "g4_2_verdict": g2["verdict"],
            "generated_terminated": gen_term, "generated_n": len(gen_texts),
        }
        for c, v in probe_losses.items():
            row["probe_loss_%s" % c] = v
        metrics_rows.append(row)
        detectors["epochs"].append({"epoch": ep, "delim_vs_content": dv,
                                    "G4.1": g1, "G4.2": g2,
                                    "probe_content_loss": probe_losses,
                                    "generated_terminated": gen_term,
                                    "generated_n": len(gen_texts)})
        # 🔴 FINDING 14: this line printed "G4.1 FAIL" and nothing else, so the two FAIL
        # branches were indistinguishable in the log -- V4.a (too few scorable strata: a
        # REACHABILITY failure of ours) and the band check (a REAL reading about the
        # model). They demand opposite responses. This is FINDING 10 exactly, which was
        # fixed for G4.6 and never generalised: a verdict without its number is a
        # verdict nobody can act on.
        g1_detail = ("V4.a: only %s scorable strata" % g1.get("n_scorable_strata")
                     if "reason" in g1 else
                     "%s strata, %s below / %s above band %s, worst %.3f/%.3f, end=%s"
                     % (g1.get("n_scorable_strata"), g1.get("n_below_band_COLLAPSE_END"),
                        g1.get("n_above_band"), g1.get("band"),
                        g1.get("worst_low") or float("nan"),
                        g1.get("worst_high") or float("nan"), g1.get("which_end")))
        print("  [epoch %d] delim=%.4f content=%.4f entropy=%.3f  G4.1 %s [%s]  G4.2 %s  "
              "gen-terminated %d/%d"
              % (ep, dv["delimiter_loss"], dv["content_loss"], gen_entropy,
                 g1["verdict"], g1_detail, g2["verdict"], gen_term, len(gen_texts)),
              flush=True)
        # 🔴 D-S4-4: the arm's own decomposition, on its own line. `delim=` above is the
        # FORCED basis; these are the number it replaced and the token it dropped, so a
        # reader can see the re-point rather than take it on trust.
        print("      D-S4-4 delim(forced)=%.4f over %d tok | delim(all, pre-ruling)="
              "%.4f over %d tok | act2-slot=%.4f over %d tok"
              % (dv["delimiter_loss"], dv["delimiter_tokens"],
                 dv["delimiter_loss_all_basis"], dv["delimiter_tokens_all_basis"],
                 dv["act2_slot_loss"], dv["act2_slot_tokens"]), flush=True)

        if halt:
            print("  🔴 G4.2 HALT CONDITION MET -- stopping. Loss fell while content "
                  "collapsed, which is the failure this detector exists for.")
            halted = True
            break

    elapsed = time.time() - t0

    # 🔴 FINDING 7: the trainer TRAINED AND THREW THE WEIGHTS AWAY. Nothing called
    # save_pretrained anywhere in this file, so every run so far -- pilot included --
    # ended with a fully trained adapter living only in the process that was about to
    # exit. G4.3, G4.4 and G4.12 all take `--adapter <dir>`, so the conditioning half of
    # Step 4 was unreachable and the failure mode was silence: the run prints a clean
    # summary and simply leaves no artefact. Saved BEFORE G4.6, which merges the adapter
    # into the base weights and must not be what gets written to disk.
    adapter_dir = None
    # 🔴 FINDING 13: excluding EVERY perturb run from saving cost G4.3 and G4.12 their
    # only lever. `no_prefix` empties the prefix, which is precisely what those two gates
    # are written to detect -- and both are scored by 4thJ_step4_diagnostics.py, which
    # takes `--adapter <dir>`. Nothing else in either battery fells them: the training-side
    # ORDER list omits both, and the generation-side EXPECTED map covers only G4.1, G4.4
    # and G4.7. So the one adapter that could demonstrate them falling was being thrown
    # away, and the gap would have surfaced as "never made to fall" with no cause visible.
    # TWO adapters, not eleven: no_prefix AND the null baseline. The baseline is not
    # optional. Both are trained on the same 600-record cap, so a bare no_prefix FAIL
    # cannot distinguish "the prefix was removed" from "600 records is not enough to
    # condition on anything" -- and G4.3 already read 0.0616 at 4,000 records, so that
    # confound is live, not hypothetical. The pair isolates the perturbation; a single
    # arm would have been an observation dressed as a demonstration.
    save_this = (args.run_type not in ("ceiling", "perturb")
                 or args.perturbation in (None, "no_prefix"))
    if save_this and hasattr(model, "save_pretrained"):
        adapter_dir = os.path.join(outdir, "adapter")
        model.save_pretrained(adapter_dir)
        tokenizer.save_pretrained(adapter_dir)
        print("adapter saved to %s" % adapter_dir)
    elif args.run_type == "perturb":
        print("perturbation run %s: adapter deliberately not saved (eleven of these would "
              "cost a gigabyte and none of them is a model anyone should reuse). The "
              "no_prefix adapter IS saved -- see FINDING 13." % args.perturbation)

    # ---- G4.9 from the recorded probe trajectory ----
    g9 = {"gate": "G4.9", "per_country": {}}
    worst = "PASS"
    for c in fold_m["probes"]:
        series = [e["probe_content_loss"].get(c) for e in detectors["epochs"]
                  if e["probe_content_loss"].get(c) == e["probe_content_loss"].get(c)]
        if not series:
            g9["per_country"][c] = {"verdict": "FAIL", "reason": "no probe readings"}
            worst = "FAIL"
            continue
        best = min(series)
        final = series[-1]
        ok = final <= best * (1.0 + TH.G4_9_MAX_REGRESSION_FRACTION)
        g9["per_country"][c] = {"verdict": "PASS" if ok else "FAIL",
                                "best": best, "final": final,
                                "regression": (final - best) / best if best else None}
        if not ok:
            worst = "FAIL"
    g9["verdict"] = worst if len(detectors["epochs"]) > 1 else "NOT CHECKED"
    if len(detectors["epochs"]) <= 1:
        g9["reason"] = ("a forgetting gate needs a trajectory. One epoch gives one "
                        "reading, and a single point cannot regress from itself. "
                        "NOT CHECKED is not a pass.")

    # ---- G4.10 ----
    peak = (torch.cuda.max_memory_allocated() / 2**30) if torch.cuda.is_available() else None
    g10 = {"gate": "G4.10", "verdict": "REPORTED_NOT_THRESHOLDED",
           "peak_vram_gib": peak, "elapsed_seconds": elapsed,
           "walltime_budget_days": TH.G4_10_WALLTIME_DAYS}

    # ---- G4.6 merge drift, adapters only ----
    g6 = {"gate": "G4.6", "verdict": "NOT CHECKED",
          "reason": "ceiling run has no adapter to merge"}
    if args.run_type != "ceiling":
        try:
            rng = random.Random(TH.SEED)
            samp = rng.sample(val_recs, min(TH.G4_6_SAMPLE_N, len(val_recs)))
            ids = [tokenizer(s["text"], add_special_tokens=False)["input_ids"][:args.max_len]
                   for s in samp]
            model.eval()
            # 🔴 FINDING 10: the first version ran all 64 sequences in ONE forward pass and
            # held the unmerged logits while computing the merged ones. At 1280 positions
            # and a ~100k vocabulary that is two 32 GiB float32 tensors, so the gate OOMed
            # and returned FAIL -- the right verdict for a reason that has nothing to do
            # with merge drift. The pair is now interleaved micro-batch by micro-batch via
            # merge_adapter/unmerge_adapter, which is the same numerical operation as
            # merge_and_unload, so only one micro-batch of logits is ever resident and the
            # statistic (max |logit difference|) is unchanged.
            base = getattr(model, "base_model", None)
            if not (hasattr(base, "merge_adapter") and hasattr(base, "unmerge_adapter")):
                raise RuntimeError(
                    "this peft build exposes no merge_adapter/unmerge_adapter, so the two "
                    "logit passes cannot be interleaved and the check would again need a "
                    "32 GiB tensor (FINDING 10)")
            # 🔴 D-S4-1 (author ruling, 2026-08-18) -- FINDING 15 route (a).
            # The band stays at 1e-4; the MEASUREMENT moves to float32.
            #
            # LoRA leaves W alone and applies `W.x + 8.(BA).x` on the fly; merging writes
            # `W + 8.BA` back into storage. Those are algebraically the same operation, so
            # the logits must not move -- that is the whole of what G4.6 asserts. But
            # storage is bfloat16 (8 mantissa bits, relative eps ~7.8e-3), so the write
            # RE-ROUNDS every merged weight, and over 32 layers the rounding compounds into
            # a logit displacement of order 1-10. Baseline read 13.71875, a number exactly
            # representable in bf16 -- the giveaway. A float32 tolerance on a bf16 merge is
            # unsatisfiable by construction, so the gate could never pass on a TRAINED
            # adapter and `perturb_merged_weight` (a 1e-3 nudge, four orders of magnitude
            # under the baseline drift) could never demonstrate anything.
            #
            # The control is in job 1266911: `freeze_adapter` is the ONE row where G4.6
            # PASSes. A frozen adapter leaves B at its zero init, so BA = 0, so W + 0 = W,
            # so nothing is re-rounded and drift is exactly zero. The merge LOGIC is
            # correct; the drift is storage rounding. Upcasting isolates the former, which
            # is the fault the gate was written to catch.
            #
            # bf16 -> fp32 is exact, and fp32 -> bf16 returns a value that was already
            # bf16-representable, so the round trip below is lossless. Dtypes are captured
            # per-parameter and restored in a `finally`, because the adapter is saved after
            # this block and must not be handed back in the wrong precision.
            g6_dtypes = {n: prm.dtype for n, prm in model.named_parameters()}
            g6_buf_dtypes = {n: b.dtype for n, b in model.named_buffers()
                             if b.is_floating_point()}
            # 🔴 The flag is raised BEFORE the cast, not after. `model.float()` converts
            # module by module, so an OOM part-way through leaves the model in MIXED
            # precision -- and a flag set only on success would then skip the restore and
            # hand that mixture to the adapter save. Setting it first makes the `finally`
            # unconditional, and restoring dtypes that were never changed is a no-op.
            g6_upcast = True
            try:
                if device == "cuda":
                    torch.cuda.empty_cache()
                model.float()
            except Exception as exc:
                # An upcast that cannot be afforded is NOT a licence to silently fall back
                # to the bf16 measurement the ruling just retired.
                raise RuntimeError(
                    "D-S4-1 requires the merge to be measured in float32 and the upcast "
                    "failed (%s: %s). A check that could not run is not a check that "
                    "passed." % (type(exc).__name__, exc))
            diff = 0.0
            n_pos = 0
            # 🔴 FINDING 21, job 1270491. D-S4-1 moved the baseline from 13.71875 (bf16) to
            # 3.204e-04 (fp32) -- bf16 storage rounding really was ~99.998 % of the drift --
            # and the gate STILL FAILs against 1e-4. Before anyone proposes touching the
            # band, the question has to be answered with a measurement: how much do the
            # logits move when NOTHING is done to them at all?
            #
            # `noise` is exactly that. Two forward passes, back to back, same weights, same
            # inputs, adapter unmerged in both -- a pure repeat. Anything it reports is
            # kernel scheduling and floating-point accumulation ORDER, not the merge. Both
            # passes are taken BEFORE merge_adapter() so that `perturb_merged_weight`, which
            # poked a weight and does not undo it, cannot contaminate the floor.
            #
            # This changes NO verdict. `G4.6` is still `diff < 1e-4` and the band is still
            # 1e-4. The floor is reported beside it so the author can rule on which of the
            # two numbers the band is actually being compared against.
            noise = 0.0
            for i in range(0, len(ids), TH.G4_6_MICRO_BATCH):
                chunk = ids[i:i + TH.G4_6_MICRO_BATCH]
                n = max(len(x) for x in chunk)
                inp = torch.tensor([x + [pad_id] * (n - len(x)) for x in chunk]).to(device)
                att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x in chunk]).to(device)
                with torch.no_grad():
                    a = model(input_ids=inp, attention_mask=att).logits.float()
                    a2 = model(input_ids=inp, attention_mask=att).logits.float()
                base.merge_adapter()
                if args.perturbation == "perturb_merged_weight" and i == 0:
                    with torch.no_grad():
                        for p in model.parameters():
                            if p.numel():
                                p.view(-1)[0] += 1e-3
                                break
                    print("PERTURBATION perturb_merged_weight: one merged weight moved "
                          "by 1e-3")
                with torch.no_grad():
                    b = model(input_ids=inp, attention_mask=att).logits.float()
                base.unmerge_adapter()
                # 🔴 FINDING 15 (cause 2): this was `(a - b).abs().max()` over the WHOLE
                # tensor, padded positions included. `att` was built and handed to the
                # forward pass and then never used again, so logits at attention_mask == 0
                # -- unconstrained, and typically the largest in magnitude anywhere in the
                # tensor -- were competing for the maximum against real tokens. The count
                # was `a.shape[0] * a.shape[1]`, i.e. padded extent, so the denominator
                # printed beside the verdict was inflated by the same bug. Mask both.
                m = att.bool().unsqueeze(-1)
                d = (a - b).abs().masked_fill(~m, 0.0)
                diff = max(diff, float(d.max()))
                # same mask, same reduction, so the floor and the drift are directly
                # comparable numbers rather than two differently-computed maxima
                dn = (a - a2).abs().masked_fill(~m, 0.0)
                noise = max(noise, float(dn.max()))
                n_pos += int(att.sum())
                del d, dn, m
                del a, a2, b
                if device == "cuda":
                    torch.cuda.empty_cache()
            if g6_upcast:
                with torch.no_grad():
                    for n_, prm in model.named_parameters():
                        if n_ in g6_dtypes and prm.dtype != g6_dtypes[n_]:
                            prm.data = prm.data.to(g6_dtypes[n_])
                    for n_, b_ in model.named_buffers():
                        if n_ in g6_buf_dtypes and b_.dtype != g6_buf_dtypes[n_]:
                            b_.data = b_.data.to(g6_buf_dtypes[n_])
                g6_upcast = False
                if device == "cuda":
                    torch.cuda.empty_cache()
            g6 = {"gate": "G4.6",
                  "measured_in": "float32 (D-S4-1, author ruling 2026-08-18)",
                  "storage_dtype": "bfloat16",
                  "basis_note": "the band is unchanged at 1e-4; only the arithmetic "
                                "precision of the comparison moved. The bf16 "
                                "merged-vs-unmerged displacement is a real property of "
                                "deployment and is reported separately -- no result in "
                                "this paper uses a merged adapter.",
                  "verdict": "PASS" if diff < TH.G4_6_MAX_LOGIT_DIFF else "FAIL",
                  "max_logit_diff": diff, "threshold": TH.G4_6_MAX_LOGIT_DIFF,
                  "n": len(samp), "n_positions_compared": n_pos,
                  "repeat_noise_floor": noise,
                  "drift_over_noise": (diff / noise) if noise > 0 else None,
                  "tf32_matmul": bool(getattr(torch.backends.cuda.matmul,
                                              "allow_tf32", False)),
                  "tf32_cudnn": bool(getattr(torch.backends.cudnn, "allow_tf32", False)),
                  "noise_floor_note": "FINDING 21: max |logit| difference between two "
                                      "IDENTICAL unmerged forward passes -- same weights, "
                                      "same inputs, same mask, same reduction. It is the "
                                      "floating-point accumulation-order floor of this GPU "
                                      "and kernel set, and it bounds from below what ANY "
                                      "logit comparison on this hardware can resolve. A "
                                      "band at or under this number is unsatisfiable by "
                                      "construction. REPORTED, NOT ACTED ON -- the verdict "
                                      "above is still diff < 1e-4 and the band is unchanged."}
        except Exception as exc:
            g6 = {"gate": "G4.6", "verdict": "FAIL",
                  "reason": "merge check raised %s: %s -- a check that could not run is "
                            "not a check that passed" % (type(exc).__name__, exc)}
        finally:
            # 🔴 D-S4-1: the adapter is SAVED after this block, so the model must never
            # leave here in the float32 the measurement borrowed. Restoring only on the
            # success path would hand a silently-upcast adapter to disk on any raise --
            # exactly the class of defect FINDING 15 was. bf16 -> fp32 -> bf16 is lossless,
            # so this is a restore, not a second rounding.
            try:
                if locals().get("g6_upcast"):
                    with torch.no_grad():
                        for n_, prm in model.named_parameters():
                            if n_ in g6_dtypes and prm.dtype != g6_dtypes[n_]:
                                prm.data = prm.data.to(g6_dtypes[n_])
                        for n_, b_ in model.named_buffers():
                            if n_ in g6_buf_dtypes and b_.dtype != g6_buf_dtypes[n_]:
                                b_.data = b_.data.to(g6_buf_dtypes[n_])
                    g6_upcast = False
                    if device == "cuda":
                        torch.cuda.empty_cache()
                    print("G4.6 float32 measurement basis restored to storage dtypes "
                          "after an exception")
            except Exception as rexc:
                raise RuntimeError(
                    "D-S4-1 could not restore parameter dtypes after the float32 merge "
                    "measurement (%s: %s). Refusing to continue -- the adapter would be "
                    "written in the wrong precision." % (type(rexc).__name__, rexc))
    # FINDING 10 also: the old line printed the verdict and nothing else, so the reason a
    # FAIL was a FAIL lived only in the JSON. Print the number that decided it.
    print("G4.6 %s  %s" % (g6["verdict"],
                           ("max_logit_diff=%.3e threshold=%.0e over %d positions"
                            % (g6["max_logit_diff"], g6["threshold"],
                               g6.get("n_positions_compared", 0)))
                           if "max_logit_diff" in g6 else g6.get("reason", "")))
    # FINDING 21: the floor is printed on its own line, never folded into the verdict line,
    # so it can never be mistaken for the number the gate was scored on.
    if g6.get("repeat_noise_floor") is not None:
        nf = g6["repeat_noise_floor"]
        print("     G4.6 repeat-noise floor=%.3e (two IDENTICAL unmerged forward passes; "
              "tf32 matmul=%s cudnn=%s). drift/noise=%s. %s"
              % (nf, g6.get("tf32_matmul"), g6.get("tf32_cudnn"),
                 ("%.1f" % g6["drift_over_noise"]) if g6.get("drift_over_noise")
                 else "n/a",
                 ("FLOOR IS AT OR ABOVE THE BAND -- G4.6 cannot be satisfied on this "
                  "hardware and the band is the thing to rule on"
                  if nf >= TH.G4_6_MAX_LOGIT_DIFF else
                  "floor is BELOW the band, so the band is resolvable here and the drift "
                  "is a real signal, not accumulation noise")))

    detectors["gates_at_end"] = {"G4.9": g9, "G4.10": g10, "G4.6": g6}
    detectors["halted_by_G4.2"] = halted

    # ---- G4.11 run manifest ----
    manifest = {
        "adapter_dir": adapter_dir,
        "run": run_name, "fold": args.fold, "held_out_country": args.fold,
        "leg": args.leg, "run_type": args.run_type,
        "perturbation": args.perturbation,
        "base_repo": repo, "base_revision": rev,
        "tokenizer_repo": tok_repo,
        "corpus_md5": shard_manifest["corpus"]["md5"],
        "train_shard": {"path": train_path, "md5": fold_m["train"]["md5"],
                        "n_loaded": len(train_recs)},
        "prereg_md5": g14.get("md5_recomputed_from_disk"),
        "seed": TH.SEED,
        "config": {"lora_r": TH.LORA_R, "lora_alpha": TH.LORA_ALPHA,
                   "use_rslora": TH.USE_RSLORA, "targets": TH.LORA_TARGET_MODULES,
                   "dtype": TH.DTYPE, "epochs": epochs, "lr": args.lr,
                   "batch_size": args.batch_size, "grad_accum": args.grad_accum,
                   "max_len": args.max_len,
                   "packing": False,
                   "packing_note": "ASSUMPTION/DEFERRAL: the recipe calls for packed "
                                   "sequences with block-diagonal masks. This run pads "
                                   "instead. Padding is slower, not wrong -- and G4.5 is "
                                   "only meaningful while padding exists. Recorded so it "
                                   "is a decision, not an omission."},
    }
    if args.perturbation == "drop_revision":
        manifest.pop("base_revision")
        print("PERTURBATION drop_revision: revision hash removed from the manifest")

    # G4.11 is scored on the manifest as it will be WRITTEN, after any perturbation has
    # had its effect -- scoring it on the pre-perturbation dict would make drop_revision
    # unfellable.
    g11 = gate_g4_11(manifest)
    print("G4.11 %s  missing=%s" % (g11["verdict"], g11["missing"] or "none"))
    detectors["gates_at_end"]["G4.11"] = g11

    with open(os.path.join(outdir, "run_manifest_%s.json" % run_name), "w",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    with open(os.path.join(outdir, "detectors_%s.json" % run_name), "w",
              encoding="utf-8") as fh:
        json.dump(detectors, fh, indent=2, sort_keys=True, default=str)
    if metrics_rows:
        keys = sorted({k for r in metrics_rows for k in r})
        with open(os.path.join(outdir, "training_metrics.csv"), "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            for r in metrics_rows:
                w.writerow(r)

    print()
    print("=" * 78)
    print("RUN %s COMPLETE. fold=%s held-out=%s" % (run_name, args.fold, args.fold))
    for g in [g14, g13, g7, g8, g5, g6, g9, g10, g11]:
        print("  %-6s %s" % (g["gate"], g["verdict"]))
    print("  peak VRAM %s GiB, %.1f s" % (peak, elapsed))
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        # Re-raised immediately after flushing: the job must still exit
        # non-zero. The point is to keep the evidence, not to hide the fault.
        _flush_detectors_on_crash(exc)
        raise
