"""
Step 4, work item 4.5 -- conditioning diagnostics. Implements G4.3, G4.4 and G4.12.

  G4.3  shuffled-prefix cross-entropy   -- is the conditioning driving generation at all
  G4.4  slot-wise mutual information    -- with the 18:00-23:00 window scored SEPARATELY
  G4.12 within-stratum shuffle          -- "the single most informative check in this step"

🔴 WHY G4.12 IS THE ONE THAT MATTERS.  G4.1 to G4.4 are computed over generated output,
and a battery of that shape can measure the AGGREGATE while being entirely blind to
whether the model links a person to *their own* day. G4.12 permutes generated diaries
within (country x age band x sex x household type x day type) cells: every conditional
marginal survives exactly, the person-to-day association does not. If every gate returns
the same status under that shuffle, the battery measures marginals and the conditioning
claim is unsupported no matter what the other numbers say.

Origin convention: minute 0 of a diary is 04:00 local (D-S2-5, cyclic rotation), so
clock minute = (minute_from_origin + 240) mod 1440.

Usage:
  python 4thJ_step4_diagnostics.py --fold es --adapter <dir> --run-type pilot --gen-n 400
"""

import argparse
import importlib
import json
import math
import os
import random
import sys
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TH = importlib.import_module("4thJ_step4_thresholds")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")
STAGED = os.path.join(STEP4, "staged_weights.json")

ORIGIN_OFFSET_MIN = 240   # 04:00
DAY_MIN = 1440

MODEL_FOR = {
    "pilot":   "allenai/OLMo-2-0425-1B",
    "primary": "allenai/Olmo-3-1025-7B",
    "ceiling": "allenai/Olmo-3-1025-7B",
    "qwen":    "Qwen/Qwen2.5-7B",
    "permuted": "allenai/Olmo-3-1025-7B",   # `D-S6-14`; leg 4 still overrides to the 1B
}


def read_jsonl(path):
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def split_prefix_body(text):
    i = text.find(TH.PREFIX_BODY_SEP)
    if i < 0:
        raise ValueError("no prefix separator")
    return text[:i + 1], text[i + 1:]


def parse_episodes(body):
    body = body.replace(TH.G4_7_EOR, "")
    eps = []
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(",")
        if len(parts) != 5:
            continue
        try:
            dur = int(parts[0])
        except ValueError:
            continue
        eps.append((dur, parts[1], parts[2], parts[3], parts[4]))
    return eps


def prefix_dict(text):
    pref = text.split(TH.PREFIX_BODY_SEP)[0].split(",")
    if len(pref) != len(TH.PREFIX_FIELDS):
        return None
    return dict(zip(TH.PREFIX_FIELDS, pref))


def stratum_key(d):
    return (d["country"], d["strat_age_band"], d["strat_sex"],
            d["strat_hh_type"], d["strat_day_type"])


def slot_activities(text):
    """-> dict slot_index -> level-1 activity code (first digit of ACT).
    Slots are TH.G4_4_SLOT_MINUTES wide over the 24 h clock."""
    try:
        _, body = split_prefix_body(text)
    except ValueError:
        return {}
    eps = parse_episodes(body)
    out = {}
    t = 0
    for dur, act, _a2, _loc, _cop in eps:
        if dur <= 0:
            continue
        lvl1 = act[0] if act else "?"
        for m in range(t, min(t + dur, DAY_MIN)):
            clock = (m + ORIGIN_OFFSET_MIN) % DAY_MIN
            out[clock // TH.G4_4_SLOT_MINUTES] = lvl1
        t += dur
        if t >= DAY_MIN:
            break
    return out


# ---------------------------------------------------------------------------
# mutual information, plug-in estimator with an explicit bias warning
# ---------------------------------------------------------------------------
def mutual_information(xs, ys):
    """I(X;Y) in nats, plug-in. 🔴 The plug-in estimator is biased UPWARD and the bias
    grows with the number of cells and shrinks with N. It is used on both the real and
    the generated side with the same alphabet and the same N, so the RATIO the gate
    scores is far more trustworthy than either absolute value. Never quote a single
    absolute MI from this function as if it were unbiased."""
    n = len(xs)
    if n == 0:
        return float("nan")
    jx, px, py = defaultdict(int), defaultdict(int), defaultdict(int)
    for a, b in zip(xs, ys):
        jx[(a, b)] += 1
        px[a] += 1
        py[b] += 1
    mi = 0.0
    for (a, b), c in jx.items():
        pab = c / n
        mi += pab * math.log(pab / ((px[a] / n) * (py[b] / n)))
    return mi


def mi_curve(pairs):
    """pairs = [(prefix_dict, text)] -> {slot: mean MI over the 5 conditioning fields}"""
    attrs = [f for f in TH.PREFIX_FIELDS if f != "country"]
    per_slot = {}
    slots = defaultdict(lambda: defaultdict(list))   # slot -> attr -> [(val, act)]
    for d, text in pairs:
        sa = slot_activities(text)
        for slot, act in sa.items():
            for a in attrs:
                slots[slot][a].append((d[a], act))
    for slot, byattr in slots.items():
        vals = []
        for a, pl in byattr.items():
            if len(pl) < 30:
                continue
            vals.append(mutual_information([p[0] for p in pl], [p[1] for p in pl]))
        if vals:
            per_slot[slot] = float(np.mean(vals))
    return per_slot


def window_mean(curve, window):
    lo, hi = window
    s0, s1 = lo // TH.G4_4_SLOT_MINUTES, hi // TH.G4_4_SLOT_MINUTES
    vals = [v for k, v in curve.items() if s0 <= k < s1]
    return float(np.mean(vals)) if vals else float("nan")


# ---------------------------------------------------------------------------
# cross-entropy of a body given a prefix
# ---------------------------------------------------------------------------
@torch.no_grad()
def ce_per_token(model, tokenizer, pairs, device, max_len, batch_size=4):
    """pairs = [(prefix_str, body_str)] -> mean nats per BODY token."""
    model.eval()
    tot, ntok = 0.0, 0
    for i in range(0, len(pairs), batch_size):
        chunk = pairs[i:i + batch_size]
        seqs, labs = [], []
        for prefix, body in chunk:
            p = tokenizer(prefix, add_special_tokens=False)["input_ids"]
            b = tokenizer(body, add_special_tokens=False)["input_ids"]
            ids = (p + b)[:max_len]
            lab = ([-100] * len(p) + list(b))[:max_len]
            seqs.append(ids)
            labs.append(lab)
        n = max(len(s) for s in seqs)
        pad = tokenizer.pad_token_id
        inp = torch.tensor([s + [pad] * (n - len(s)) for s in seqs]).to(device)
        att = torch.tensor([[1] * len(s) + [0] * (n - len(s)) for s in seqs]).to(device)
        lb = torch.tensor([l + [-100] * (n - len(l)) for l in labs]).to(device)
        logits = model(input_ids=inp, attention_mask=att).logits[:, :-1, :].float()
        tgt = lb[:, 1:]
        mask = tgt != -100
        if mask.sum() == 0:
            continue
        lp = F.cross_entropy(logits.reshape(-1, logits.size(-1)),
                             tgt.reshape(-1).clamp(min=0),
                             reduction="none").view(tgt.shape)
        tot += float((lp * mask).sum())
        ntok += int(mask.sum())
    return tot / ntok if ntok else float("nan"), ntok


def within_stratum_permutation(items, key_fn, rng):
    """Permute items inside each key cell. Cells of size 1 cannot move -- counted and
    reported, because a shuffle that could not shuffle is not a shuffle."""
    by = defaultdict(list)
    for i, it in enumerate(items):
        by[key_fn(it)].append(i)
    out = list(items)
    n_moved, n_stuck = 0, 0
    for k, idxs in by.items():
        if len(idxs) < 2:
            n_stuck += len(idxs)
            continue
        perm = list(idxs)
        rng.shuffle(perm)
        for a, b in zip(idxs, perm):
            out[a] = items[b]
            if a != b:
                n_moved += 1
    return out, n_moved, n_stuck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    # FINDING 13: "perturb" added so the no_prefix adapter can be scored HERE. It writes
    # generated_perturb_<fold>.jsonl and conditioning_diagnostics_perturb_<fold>.json, so
    # it cannot overwrite the pilot or primary artefacts. leg 4 always loads
    # MODEL_FOR["pilot"], so the run-type does not change which base model is used.
    # 🔴 `D-S6-14`: "permuted" is the memorisation-ceiling control. Running the
    # conditioning diagnostics on it is not decoration -- the permutation is supposed
    # to have destroyed prefix conditioning, and these are the readings that say so
    # from the MODEL rather than from the shard builder's own invariants. Expect the
    # prefix-sensitivity numbers to collapse; if they do not, the control did not work
    # and nothing downstream of it may be reported.
    ap.add_argument("--run-type", default="pilot",
                    choices=["pilot", "primary", "ceiling", "qwen", "perturb", "permuted"])
    ap.add_argument("--adapter", default=None, help="peft adapter dir; omit for base model")
    ap.add_argument("--gen-n", type=int, default=400)
    ap.add_argument("--leg", type=int, default=4, choices=[4, 5])
    ap.add_argument("--gen-stratified-k", type=int, default=6)
    ap.add_argument("--gen-batch", type=int, default=8)
    ap.add_argument("--ce-n", type=int, default=256)
    ap.add_argument("--max-len", type=int, default=1280)
    # D-S4-12 arm (b), author ruling 2026-08-24. Additive: the default IS TH.SEED, so
    # every existing invocation is byte-identical. A second seed exists only to
    # QUANTIFY the sampling spread of G4.4, never to pick a better-looking run.
    ap.add_argument("--seed", type=int, default=TH.SEED,
                    help="sampling seed; default TH.SEED, the frozen value")
    ap.add_argument("--out", default=os.path.join(STEP4, "diagnostics"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)
    torch.manual_seed(args.seed)
    if args.seed != TH.SEED:
        print("🔴 SEED OVERRIDE: %d (frozen TH.SEED is %d). This run is a "
              "SPREAD MEASUREMENT, not a gate verdict." % (args.seed, TH.SEED))

    # V4.h -- say which fold and which held-out country BEFORE any verdict
    print("=" * 78)
    print("CONDITIONING DIAGNOSTICS -- FOLD %s, HELD-OUT COUNTRY %s, run-type %s"
          % (args.fold, args.fold, args.run_type))
    print("=" * 78)

    sm = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    fold_m = sm["folds"][args.fold]
    val_recs = read_jsonl(fold_m["heldin_val"]["path"])
    # FINDING 11: the real reference for stratum eligibility and for the real MI curve is
    # the whole held-in set, not the validation split alone.
    real_ref = read_jsonl(fold_m["train"]["path"]) + val_recs
    print("held-in validation diaries: %d (real reference set: %d)"
          % (len(val_recs), len(real_ref)))

    from transformers import AutoModelForCausalLM, AutoTokenizer
    staged = json.load(open(STAGED, "r", encoding="utf-8"))
    # same rule as the trainer: leg 4 is the small backbone regardless of run-type, so a
    # diagnostics run loads the base the adapter was actually trained on.
    repo = MODEL_FOR["pilot"] if args.leg == 4 else MODEL_FOR[args.run_type]
    rev = next((r["revision"] for r in staged["repos"] if r["repo_id"] == repo), None)
    if rev is None:
        raise SystemExit("no staged revision for %s" % repo)
    tokenizer = AutoTokenizer.from_pretrained(repo, revision=rev)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev,
                                                 torch_dtype=torch.bfloat16)
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
        print("adapter loaded: %s" % args.adapter)
    else:
        print("🔴 NO ADAPTER -- these are BASE-MODEL diagnostics. A base model has never "
              "seen this format, so G4.3 failing here is expected and is NOT evidence "
              "about the fine-tuned model.")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()

    # ---------------------------------------------------------------- G4.3
    ce_sample = rng.sample(val_recs, min(args.ce_n, len(val_recs)))
    true_pairs = []
    for r in ce_sample:
        p, b = split_prefix_body(r["text"])
        true_pairs.append((p, b))
    prefixes = [p for p, _ in true_pairs]
    shuffled = prefixes[:]
    rng.shuffle(shuffled)
    n_same = sum(1 for a, b in zip(prefixes, shuffled) if a == b)
    perm_pairs = [(sp, b) for sp, (_p, b) in zip(shuffled, true_pairs)]

    ce_true, ntok_true = ce_per_token(model, tokenizer, true_pairs, device, args.max_len)
    ce_perm, ntok_perm = ce_per_token(model, tokenizer, perm_pairs, device, args.max_len)
    rise = ce_perm - ce_true
    g3 = {"gate": "G4.3",
          "verdict": "PASS" if rise >= TH.G4_3_MIN_CE_RISE_NATS_PER_TOKEN else "FAIL",
          "ce_true_prefix": ce_true, "ce_permuted_prefix": ce_perm,
          "rise_nats_per_token": rise,
          "threshold": TH.G4_3_MIN_CE_RISE_NATS_PER_TOKEN,
          "n_pairs": len(true_pairs), "body_tokens_true": ntok_true,
          "n_prefixes_unchanged_by_the_permutation": n_same,
          "note": "a permutation that left many prefixes in place cannot raise CE; "
                  "n_prefixes_unchanged is reported so a weak shuffle is visible rather "
                  "than being read as a weak model"}
    print("G4.3 %s  CE true=%.4f permuted=%.4f rise=%.4f (need >= %.2f), %d prefixes "
          "unchanged by the shuffle"
          % (g3["verdict"], ce_true, ce_perm, rise,
             TH.G4_3_MIN_CE_RISE_NATS_PER_TOKEN, n_same))

    # ------------------------------------------------------- generation, G4.4
    # FINDING 8 applies here too: the generation-side perturbations scored against this
    # file include two that target G4.1, and G4.1 needs N >= 100 in each of >= 5 strata
    # (V4.a). A random draw over hundreds of strata cannot deliver that at any volume
    # this project can afford, so the draw is stratified over the K largest eligible
    # strata -- chosen by REAL count only, never by anything measured on the generated
    # side. Batched because 600 one-at-a-time generations is an hour of wall-clock on a
    # shared slice.
    # 🔴 FINDING 11: eligibility was counted on the held-in VALIDATION split, which
    # reaches N >= 100 in ZERO strata on all three folds (job 1266866). This script
    # therefore generated 0 diaries and then scored G4.4 and G4.12 on an empty file --
    # both returned FAIL with nan, which is the right verdict for the wrong reason. The
    # reference is now the full held-in real set, and the key is the SAME five-field
    # stratum the trainer's G4.1 uses, not the six-field prefix.
    if args.gen_stratified_k:
        def _stratum(t):
            d = prefix_dict(t)
            if not d:
                return None
            return (d["country"], d["strat_age_band"], d["strat_sex"],
                    d["strat_hh_type"], d["strat_day_type"])
        by_ref, by_draw = defaultdict(list), defaultdict(list)
        for r in real_ref:
            s = _stratum(r["text"])
            if s:
                by_ref[s].append(r)
        for r in val_recs:
            s = _stratum(r["text"])
            if s:
                by_draw[s].append(r)
        eligible = sorted([s for s in by_ref if len(by_ref[s]) >= TH.G4_1_MIN_STRATUM_N],
                          key=lambda s: (-len(by_ref[s]), s))[:args.gen_stratified_k]
        per = TH.G4_1_MIN_STRATUM_N
        print("stratified generation: %d strata x %d = %d diaries (%d strata in the real "
              "reference set of %d diaries reach N >= %d)"
              % (len(eligible), per, len(eligible) * per,
                 sum(1 for s in by_ref if len(by_ref[s]) >= TH.G4_1_MIN_STRATUM_N),
                 len(real_ref), TH.G4_1_MIN_STRATUM_N))
        if len(eligible) < TH.V4_A_MIN_STRATA:
            print("only %d strata reach N >= %d in the REAL data. G4.1 cannot be "
                  "satisfied on this fold at any generation volume and will FAIL with "
                  "V4.a's reason. That is the guard, not a defect."
                  % (len(eligible), TH.G4_1_MIN_STRATUM_N))
        gen_sample = []
        for s in eligible:
            pool = by_draw.get(s) or by_ref[s]
            gen_sample.extend([rng.choice(pool) for _ in range(per)])
    else:
        gen_sample = rng.sample(val_recs, min(args.gen_n, len(val_recs)))

    # FINDING 12: wire <eor> as the stop token, as the trainer does.
    eor_ids = tokenizer(TH.G4_7_EOR, add_special_tokens=False)["input_ids"]
    eos_arg = eor_ids[-1] if len(eor_ids) == 1 else None
    # FINDING 12, second half: three ids, so eos_token_id cannot express it. See trainer.
    stop_kw = ({"eos_token_id": eos_arg} if eos_arg is not None
               else {"stop_strings": [TH.G4_7_EOR], "tokenizer": tokenizer})
    print("generation stop token: %s -> ids %s, %s"
          % (TH.G4_7_EOR, eor_ids,
             "wired as eos_token_id" if eos_arg is not None else
             "MULTI-TOKEN, wired as stop_strings"))

    old_side = tokenizer.padding_side
    tokenizer.padding_side = "left"   # decoder-only: the prompt must be flush right
    gen_texts = []
    try:
        for i in range(0, len(gen_sample), args.gen_batch):
            chunk = gen_sample[i:i + args.gen_batch]
            prefixes = [split_prefix_body(r["text"])[0] for r in chunk]
            enc = tokenizer(prefixes, add_special_tokens=False, return_tensors="pt",
                            padding=True).to(device)
            with torch.no_grad():
                gkw = stop_kw
                g = model.generate(**enc, max_new_tokens=args.max_len, do_sample=True,
                                   temperature=1.0, top_p=1.0,
                                   pad_token_id=tokenizer.pad_token_id, **gkw)
            for row in g:
                gen_texts.append(tokenizer.decode(row, skip_special_tokens=True))
            if i % (args.gen_batch * 10) == 0:
                print("    generated %d/%d" % (len(gen_texts), len(gen_sample)), flush=True)
    finally:
        tokenizer.padding_side = old_side
    print("generated %d diaries" % len(gen_texts))

    # Persist the generated set. The generation-side perturbations (modal-day,
    # 500x duplication, evening blanking) are scored by 4thJ_step4_genperturb.py
    # against THIS file, so that a perturbation and its baseline are provably the
    # same generation rather than two separate sampling runs that differ for
    # reasons nobody controlled.
    gen_path = os.path.join(args.out, "generated_%s_%s.jsonl" % (args.run_type, args.fold))
    with open(gen_path, "w", encoding="utf-8") as fh:
        for r, gt in zip(gen_sample, gen_texts):
            fh.write(json.dumps({"country": r["country"], "hid": r["hid"],
                                 "pid": r["pid"], "diary_day": r["diary_day"],
                                 "prompt_text": r["text"], "text": gt}) + "\n")
    print("wrote %s" % gen_path)

    real_pairs = [(prefix_dict(r["text"]), r["text"]) for r in real_ref]
    real_pairs = [(d, t) for d, t in real_pairs if d]
    gen_pairs = [(prefix_dict(r["text"]), gt)
                 for r, gt in zip(gen_sample, gen_texts) if prefix_dict(r["text"])]

    mi_real = mi_curve(real_pairs)
    mi_gen = mi_curve(gen_pairs)

    def win(curve, w):
        return window_mean(curve, w)

    ev_real, ev_gen = win(mi_real, TH.G4_4_EVENING_WINDOW), win(mi_gen, TH.G4_4_EVENING_WINDOW)
    mo_real, mo_gen = win(mi_real, TH.G4_4_MORNING_WINDOW), win(mi_gen, TH.G4_4_MORNING_WINDOW)
    ev_ratio = ev_gen / ev_real if ev_real else float("nan")
    mo_ratio = mo_gen / mo_real if mo_real else float("nan")
    g4 = {"gate": "G4.4",
          "evening_window_1800_2300": {
              "mi_real": ev_real, "mi_generated": ev_gen, "ratio": ev_ratio,
              "verdict": "PASS" if ev_ratio >= TH.G4_4_MIN_MI_RATIO else "FAIL"},
          "morning_window_0600_1100": {
              "mi_real": mo_real, "mi_generated": mo_gen, "ratio": mo_ratio,
              "verdict": "PASS" if mo_ratio >= TH.G4_4_MIN_MI_RATIO else "FAIL"},
          "min_ratio": TH.G4_4_MIN_MI_RATIO,
          "estimator_note": "plug-in MI is biased upward; the same alphabet and the same "
                            "N are used on both sides, so the RATIO is the trustworthy "
                            "quantity and neither absolute value should be quoted alone"}
    g4["verdict"] = ("PASS" if g4["evening_window_1800_2300"]["verdict"] == "PASS"
                     and g4["morning_window_0600_1100"]["verdict"] == "PASS" else "FAIL")
    print("G4.4 %s  evening ratio %.3f (%s)  morning ratio %.3f (%s)  -- reported separately"
          % (g4["verdict"], ev_ratio, g4["evening_window_1800_2300"]["verdict"],
             mo_ratio, g4["morning_window_0600_1100"]["verdict"]))

    # ------------------------------------------------------------- G4.12
    shuf_items, n_moved, n_stuck = within_stratum_permutation(
        gen_pairs, lambda it: stratum_key(it[0]), rng)
    # re-pair: keep each prefix, give it another diary from the same stratum cell
    shuffled_pairs = [(d, shuf[1]) for (d, _t), shuf in zip(gen_pairs, shuf_items)]
    mi_shuf = mi_curve(shuffled_pairs)
    ev_shuf = win(mi_shuf, TH.G4_4_EVENING_WINDOW)
    mi_drop = (ev_gen - ev_shuf) / ev_gen if ev_gen else float("nan")

    ce_pairs_shuf = []
    for (d, t) in shuffled_pairs[:args.ce_n]:
        pref = ",".join(d[f] for f in TH.PREFIX_FIELDS) + TH.PREFIX_BODY_SEP
        try:
            _, body = split_prefix_body(t)
        except ValueError:
            continue
        ce_pairs_shuf.append((pref, body))
    ce_shuf, _ = ce_per_token(model, tokenizer, ce_pairs_shuf, device, args.max_len)

    gen_ce_pairs = []
    for (d, t) in gen_pairs[:args.ce_n]:
        pref = ",".join(d[f] for f in TH.PREFIX_FIELDS) + TH.PREFIX_BODY_SEP
        try:
            _, body = split_prefix_body(t)
        except ValueError:
            continue
        gen_ce_pairs.append((pref, body))
    ce_gen, _ = ce_per_token(model, tokenizer, gen_ce_pairs, device, args.max_len)

    ce_rise_shuf = ce_shuf - ce_gen
    g12 = {"gate": "G4.12",
           "n_generated": len(gen_pairs),
           "n_moved_by_shuffle": n_moved,
           "n_in_singleton_cells_could_not_move": n_stuck,
           "ce_generated_pairing": ce_gen,
           "ce_within_stratum_shuffled": ce_shuf,
           "ce_rise_nats_per_token": ce_rise_shuf,
           "ce_rise_required": TH.G4_12_MIN_CE_RISE_NATS_PER_TOKEN,
           "mi_evening_generated": ev_gen,
           "mi_evening_shuffled": ev_shuf,
           "mi_drop_ratio": mi_drop,
           "mi_drop_required": TH.G4_12_MIN_MI_DROP_RATIO,
           "g4_1_note": "G4.1 is ANALYTICALLY INVARIANT under a within-stratum "
                        "permutation -- the multiset of diaries inside each cell is "
                        "unchanged, so the within-stratum variance cannot move. That is "
                        "not a measurement result, it is the reason G4.1 cannot "
                        "substitute for G4.12."}
    degraded_ce = ce_rise_shuf >= TH.G4_12_MIN_CE_RISE_NATS_PER_TOKEN
    degraded_mi = mi_drop >= TH.G4_12_MIN_MI_DROP_RATIO
    if n_moved == 0:
        g12["verdict"] = "FAIL"
        g12["reason"] = ("the shuffle moved nothing -- every generated diary sat in a "
                         "singleton stratum cell. A shuffle that could not shuffle "
                         "proves nothing and must not be read as a pass.")
    else:
        g12["verdict"] = "PASS" if (degraded_ce and degraded_mi) else "FAIL"
        g12["degraded_ce"] = degraded_ce
        g12["degraded_mi"] = degraded_mi
        if not (degraded_ce or degraded_mi):
            g12["reason"] = ("🔴 NEITHER G4.3's metric NOR G4.4's moved under the "
                             "within-stratum shuffle. On the val doc's own terms the "
                             "battery is measuring marginals rather than skill, and the "
                             "conditioning claim is unsupported regardless of what the "
                             "other gates report.")
    print("G4.12 %s  moved=%d stuck-in-singletons=%d  CE rise %.4f (need %.2f)  "
          "MI drop %.3f (need %.2f)"
          % (g12["verdict"], n_moved, n_stuck, ce_rise_shuf,
             TH.G4_12_MIN_CE_RISE_NATS_PER_TOKEN, mi_drop,
             TH.G4_12_MIN_MI_DROP_RATIO))

    report = {"fold": args.fold, "held_out_country": args.fold,
              "run_type": args.run_type, "adapter": args.adapter,
              "base_repo": repo, "base_revision": rev,
              "G4.3": g3, "G4.4": g4, "G4.12": g12,
              "mi_curve_real": {str(k): v for k, v in sorted(mi_real.items())},
              "mi_curve_generated": {str(k): v for k, v in sorted(mi_gen.items())},
              "mi_curve_shuffled": {str(k): v for k, v in sorted(mi_shuf.items())}}
    path = os.path.join(args.out, "conditioning_diagnostics_%s_%s.json"
                        % (args.run_type, args.fold))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True, default=str)
    print()
    print("wrote %s" % path)
    print("=" * 78)
    for g in (g3, g4, g12):
        print("  %-6s %s" % (g["gate"], g["verdict"]))
    print("=" * 78)


if __name__ == "__main__":
    main()
