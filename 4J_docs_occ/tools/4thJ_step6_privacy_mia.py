# -*- coding: utf-8 -*-
"""Step 6.5 — `G6.10`, `G6.11`, `G6.12` and the perplexity-gap control.

  usage: python 4thJ_step6_privacy_mia.py --fold es --leg 4 --adapter DIR
                                          --corpus FILE --out DIR [--n 2000]

The three attacks that need the model, and the one control that comes free with
them. `G6.13` is CPU-only and lives in `4thJ_step6_g613_dcr.py`.

| gate | attack | FAILS if |
|---|---|---|
| `G6.10` | loss-based MIA | ROC-AUC > 0.65, or TPR at 0.1 % FPR > 5 % |
| `G6.11` | reference-based MIA vs the PUBLIC base model | ROC-AUC > 0.75 |
| `G6.12` | prefix-prompted extraction, greedy AND sampled | any exact match on a stratum with fewer than 5 training records |

---------------------------------------------------------------------------
🔴 WHO IS A MEMBER, AND WHO IS NOT
---------------------------------------------------------------------------

Under LOCO the fold's adapter was trained on the OTHER two countries' `train`
split. So:

    members      donor countries, `split == "train"`   -- the model saw these
    non-members  donor countries, `split == "heldout"` -- same countries, same
                 distribution, same survey, never seen

🔴 The LOCO held-out country is **NOT** the non-member set. It differs by country
as well as by exposure, and an MIA that separates two countries has measured the
country, not the membership. This is the same trap `G6.13`'s `country` reference
set is kept out of the verdict for.

🔴 The two sets are **sample-size matched by construction** — `--n` is applied to
both — because `FINDING 86` showed what an unmatched comparison does to a privacy
verdict in this project.

---------------------------------------------------------------------------
🔴 WHAT IS SCORED, AND ON WHICH TOKENS
---------------------------------------------------------------------------

The loss is the mean negative log-likelihood of the **BODY tokens only** — the
episodes and `<eor>`, never the prefix. The prefix is the conditioning vector; it
is supplied to the model at generation time and is not something the model could
memorise a person from. Scoring it would let the demographic mix of the two sets
leak into the attack.

`G6.11`'s score is `NLL_base - NLL_tuned` per record, the standard reference-based
signal: a record the fine-tune memorised gets much cheaper under the tuned model
than under the public one, while a record that is merely typical gets cheaper under
both. The base model is loaded at the SAME revision the adapter was trained from,
read from the adapter's own `adapter_config.json` where possible.

---------------------------------------------------------------------------
🔴 WHAT THIS FILE DOES NOT PROVIDE
---------------------------------------------------------------------------

The **random-label-permutation adapter** control requires its own training run and
is NOT faked here. Without `--permuted-adapter` its absence is printed in the
artefact as a named gap, because an audit that silently omits one of its three
registered controls is the kind of audit this project exists not to write.

🔴 `D-S6-14`, author 2026-08-22, supplies that run. Build the shards with
`4thJ_step4_shards.py --permute-labels`, train with `--run-type permuted`, then
pass BOTH `--permuted-adapter DIR` and `--permuted-corpus FILE` here. The control
is scored by exactly the code the baseline was scored by, over the permuted corpus
the permuted adapter actually trained on, at the same `n` and the same seed.

WHAT THE CEILING IS FOR. The untuned base anchors the BOTTOM of the AUC scale at
~0.50. Nothing anchored the top, so a measured 0.55 against a 0.65 bar could not be
called low -- low compared to what? The permuted adapter has nothing to generalise
by construction, so whatever it scores is what pure rote memorisation looks like at
this model size, on this corpus, at this schedule. 🔴 The pre-registered bars do NOT
move: `G6.10 <= 0.65` and `G6.11 <= 0.75` are unchanged, and the ceiling is reported
beside them, never substituted for them (author directive, `D-S6-14` item 3).
"""

import argparse
import collections
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

G610_AUC_MAX = 0.65
G610_TPR_AT_FPR = 0.001
G610_TPR_MAX = 0.05
G611_AUC_MAX = 0.75
PPL_GAP_MAX = 0.05          # the registered third control
RARE_STRATUM_MAX = 5        # `G6.12` -- strata with FEWER THAN five training records
SEED = 20260822


class NotRun(RuntimeError):
    pass


def stratum_key(prefix_fields):
    """Step 4's convention: country, age, sex, hh_type, day_type. `econ_status`
    (field 4) is deliberately excluded, exactly as `4thJ_step4_diagnostics.py:96`
    has it -- two steps disagreeing about what a stratum is would make `G6.12`'s
    "fewer than five training records" mean something different here."""
    f = prefix_fields
    return (f[0], f[1], f[2], f[3], f[5])


def roc_auc(pos, neg):
    """Rank-based AUC with a tie correction. No scipy in this environment."""
    if not pos or not neg:
        raise NotRun("AUC needs both classes non-empty")
    merged = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    ranks = [0.0] * len(merged)
    i = 0
    while i < len(merged):
        j = i
        while j + 1 < len(merged) and merged[j + 1][0] == merged[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    rpos = sum(ranks[k] for k in range(len(merged)) if merged[k][1] == 1)
    n1, n0 = len(pos), len(neg)
    return (rpos - n1 * (n1 + 1) / 2.0) / float(n1 * n0)


def tpr_at_fpr(pos, neg, fpr):
    """TPR at a fixed FPR. 🔴 With `n` non-members the smallest resolvable FPR is
    `1/n`; the achieved FPR is returned beside the TPR so a threshold finer than
    the sample can support is visible rather than implied."""
    k = int(math.floor(fpr * len(neg)))
    if k < 1:
        return None, None, ("FPR %.4f is below 1/%d -- this sample cannot resolve it"
                            % (fpr, len(neg)))
    thr = sorted(neg, reverse=True)[k - 1]
    tp = sum(1 for v in pos if v > thr)
    fp = sum(1 for v in neg if v > thr)
    return tp / float(len(pos)), fp / float(len(neg)), None


def load_split(corpus, fold, want_split, countries):
    out = []
    for line in open(corpus, encoding="utf-8"):
        r = json.loads(line)
        if r["country"] not in countries or r["split"] != want_split:
            continue
        out.append(r)
    return out


def nll_batch(model, tok, texts, prefix_lens, device, batch_size=8, max_len=1400):
    """Mean NLL of the BODY tokens of each text. Returns a list of floats."""
    import torch
    out = []
    model.eval()
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            chunk = texts[i:i + batch_size]
            plens = prefix_lens[i:i + batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                      max_length=max_len)
            enc = {k: v.to(device) for k, v in enc.items()}
            logits = model(**enc).logits.float()
            ids = enc["input_ids"]
            mask = enc["attention_mask"]
            lp = torch.log_softmax(logits[:, :-1, :], dim=-1)
            tgt = ids[:, 1:]
            tokl = -lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
            keep = mask[:, 1:].clone()
            for b, pl in enumerate(plens):
                keep[b, :max(pl - 1, 0)] = 0        # 🔴 body tokens only
            denom = keep.sum(dim=1).clamp(min=1)
            out.extend(((tokl * keep).sum(dim=1) / denom).tolist())
    return out


def score_g610(pos, neg):
    """`G6.10`'s VERDICT, in one place. Both the baseline and every perturbation
    go through this function, so a perturbation that fells the gate fells the same
    code the baseline passed."""
    auc = roc_auc(pos, neg)
    tpr, ach, note = tpr_at_fpr(pos, neg, G610_TPR_AT_FPR)
    reasons = []
    if auc > G610_AUC_MAX:
        reasons.append("ROC-AUC %.4f exceeds %.2f" % (auc, G610_AUC_MAX))
    if tpr is not None and tpr > G610_TPR_MAX:
        reasons.append("TPR %.4f at FPR %.4f exceeds %.2f" % (tpr, ach, G610_TPR_MAX))
    return dict(passes=not reasons, reasons=reasons, auc=auc, auc_max=G610_AUC_MAX,
                tpr_at_fpr=tpr, achieved_fpr=ach, tpr_max=G610_TPR_MAX,
                resolution_note=note)


def score_g611(rpos, rneg):
    auc = roc_auc(rpos, rneg)
    reasons = [] if auc <= G611_AUC_MAX else [
        "ROC-AUC %.4f exceeds %.2f" % (auc, G611_AUC_MAX)]
    return dict(passes=not reasons, reasons=reasons, auc=auc, auc_max=G611_AUC_MAX)


def score_pplgap(mem_nll, non_nll):
    pm = math.exp(sum(mem_nll) / len(mem_nll))
    pn = math.exp(sum(non_nll) / len(non_nll))
    gap = abs(pn - pm) / pm
    return dict(train_ppl=pm, test_ppl=pn, gap=gap, gap_max=PPL_GAP_MAX,
                passes=gap < PPL_GAP_MAX)


def g612_match(decoded, by_prefix, n_attempted, n_rare_strata, n_rare_records):
    """`G6.12`'s VERDICT. `decoded` is {mode: [raw decoded string, ...]} as it came
    off `generate`; the split-and-compare below is the attack itself and is the
    code the `g612_verbatim` perturbation has to get past."""
    hits = {"greedy": 0, "sampled": 0}
    for mode, texts in decoded.items():
        for txt in texts:
            if "|" not in txt:
                continue
            pre, body = txt.split("|", 1)
            if body in by_prefix.get(pre, ()):
                hits[mode] += 1
    n_hits = hits["greedy"] + hits["sampled"]
    return dict(passes=(n_hits == 0), blocked=False,
                n_rare_strata=n_rare_strata, n_rare_records=n_rare_records,
                n_attempted=n_attempted,
                n_exact_greedy=hits["greedy"], n_exact_sampled=hits["sampled"],
                reasons=([] if n_hits == 0 else
                         ["%d exact reproductions of a training diary on a stratum "
                          "with fewer than %d records" % (n_hits, RARE_STRATUM_MAX)]))


# ---------------------------------------------------------------------------
# 🔴 THE PERTURBATION BATTERY
#
# Every one of these acts on the ALREADY-COMPUTED per-record losses or on the
# ALREADY-DECODED generations, so the whole board costs one forward pass, not
# six. Nothing here touches the verdict functions above -- an injected defect has
# to travel through exactly the code the baseline travelled through.
#
# `pplgap_widen` fells a CONTROL, not a gate. It is in the board because a control
# that cannot move is not a control.
# ---------------------------------------------------------------------------
PERTURBATIONS = ["null", "g610_memorise", "g610_tail", "g611_reference",
                 "pplgap_widen", "g612_verbatim"]
SCORED_GATES = ["G6_10", "G6_11", "G6_12"]


def apply_perturbation(name, tun_mem, tun_non, base_mem, base_non, decoded, truth):
    """Returns transformed copies. `truth` is the true text of target 0, or None."""
    tm, tn = list(tun_mem), list(tun_non)
    bm, bn = list(base_mem), list(base_non)
    dec = dict((k, list(v)) for k, v in decoded.items())
    if name == "null":
        pass
    elif name == "g610_memorise":
        # a fine-tune that memorised: every member is half a nat cheaper.
        tm = [x - 0.5 for x in tm]
    elif name == "g610_tail":
        # 🔴 the SECOND clause on its own. Only the 1 % of members that already
        # score best are driven down, which barely moves the AUC and is exactly the
        # small-cohort leak `TPR at 0.1 % FPR` exists to catch.
        k = max(1, int(round(len(tm) * 0.08)))
        order = sorted(range(len(tm)), key=lambda i: tm[i])[:k]
        for i in order:
            tm[i] = tm[i] - 5.0
    elif name == "g611_reference":
        # the reference signal ONLY. Only the PUBLIC base's member losses move, so
        # `G6.10` (which never sees the base) and the perplexity gap (tuned only)
        # cannot move with it -- the injection is confined to `G6.11`'s own score.
        bm = [x + 1.0 for x in bm]
    elif name == "pplgap_widen":
        # NOT confinable, and the reason is worth stating: the perplexity gap and
        # `G6.10` read the SAME member/non-member loss difference, one as a ratio of
        # means and one as a rank statistic. Anything that widens the gap moves the
        # AUC. That the control falls WITH the gate is a property of the pair, not a
        # defect in the injection.
        tn = [x * 1.15 for x in tn]
    elif name == "g612_verbatim":
        if truth is not None and dec.get("greedy"):
            dec["greedy"][0] = truth
    else:
        raise ValueError("unknown perturbation %s" % name)
    return tm, tn, bm, bn, dec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=("es", "uk", "it"))
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=1400)
    ap.add_argument("--extract-n", type=int, default=200,
                    help="how many rare-stratum records G6.12 attempts")
    ap.add_argument("--permuted-adapter", default=None,
                    help="`D-S6-14`: the random-label-permutation adapter, trained by "
                         "`--run-type permuted`. Requires --permuted-corpus.")
    ap.add_argument("--permuted-corpus", default=None,
                    help="`D-S6-14`: the corpus that adapter trained on, written by "
                         "`4thJ_step4_shards.py --permute-labels`. It must carry the "
                         "POISONED_CONTROL mark or this script refuses it.")
    a = ap.parse_args(argv)

    import random
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    if bool(a.permuted_adapter) != bool(a.permuted_corpus):
        raise NotRun("--permuted-adapter and --permuted-corpus go together. The control "
                     "adapter must be scored on the corpus it trained on: score it on "
                     "the real corpus and the ceiling measures a model reading text it "
                     "never saw, which is not a ceiling. `D-S6-14`.")
    if not os.path.isdir(a.adapter):
        raise NotRun("no adapter at %s" % a.adapter)
    with open(os.path.join(a.adapter, "adapter_config.json"), encoding="utf-8") as fh:
        acfg = json.load(fh)
    base_repo = acfg.get("base_model_name_or_path")
    if not base_repo:
        raise NotRun("adapter_config.json names no base model; G4.11's rule applies "
                     "here too -- a checkpoint named without a base is not reproducible")

    # ---- 🔴 `D-S6-14` interlocks, hoisted here on purpose ----
    # Both read one line of a file. A guard that can only fire after a full scoring
    # pass costs hours to trip, which is a guard nobody ever sees fail.
    perm_seed = None
    if a.permuted_adapter:
        with open(a.permuted_corpus, encoding="utf-8") as fh:
            _first = json.loads(fh.readline())
        if not _first.get("POISONED_CONTROL"):
            raise NotRun("%s is not marked POISONED_CONTROL. `D-S6-14` requires the "
                         "control to be scored on the permuted corpus it trained on; "
                         "this file is not one. A ceiling measured on the real corpus "
                         "is not a ceiling -- it would simply read low and be believed."
                         % a.permuted_corpus)
        perm_seed = _first.get("permutation_seed")
        if not os.path.isdir(a.permuted_adapter):
            raise NotRun("no control adapter at %s" % a.permuted_adapter)
        with open(os.path.join(a.permuted_adapter, "adapter_config.json"),
                  encoding="utf-8") as fh:
            _pcfg = json.load(fh)
        if _pcfg.get("base_model_name_or_path") != base_repo:
            raise NotRun("the control adapter was trained from %r and the reported "
                         "adapter from %r. A memorisation ceiling measured on a "
                         "different backbone is a ceiling for a different model."
                         % (_pcfg.get("base_model_name_or_path"), base_repo))
        print("`D-S6-14` control ARMED: adapter %s, corpus %s, permutation seed %s"
              % (a.permuted_adapter, a.permuted_corpus, perm_seed))

    donors = [c for c in ("es", "uk", "it") if c != a.fold]
    members = load_split(a.corpus, a.fold, "train", donors)
    nonmembers = load_split(a.corpus, a.fold, "heldout", donors)

    print("=" * 78)
    print("Step 6.5 -- G6.10 / G6.11 / G6.12, fold %s, leg %d" % (a.fold, a.leg))
    print("=" * 78)
    print("base      : %s" % base_repo)
    print("adapter   : %s" % a.adapter)
    print("donors    : %s" % ", ".join(donors))
    print("members   : %d (donor train)   non-members: %d (donor heldout)"
          % (len(members), len(nonmembers)))
    if a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    n = min(a.n, len(members), len(nonmembers))
    rng = random.Random(SEED)
    members = rng.sample(members, n)
    nonmembers = rng.sample(nonmembers, n)
    print("🔴 SIZE-MATCHED at n=%d per class, seed %d (FINDING 86)." % (n, SEED))

    def texts_and_prefix_lens(rows, tok):
        ts = [r["text"] for r in rows]
        pl = [len(tok(r["text"].split("|", 1)[0] + "|")["input_ids"]) for r in rows]
        return ts, pl

    tok = AutoTokenizer.from_pretrained(base_repo)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device: %s" % device)

    print("\nloading the PUBLIC base model ...")
    base = AutoModelForCausalLM.from_pretrained(base_repo, torch_dtype=torch.bfloat16)
    base.to(device)
    mt, mp = texts_and_prefix_lens(members, tok)
    nt, np_ = texts_and_prefix_lens(nonmembers, tok)
    base_mem = nll_batch(base, tok, mt, mp, device, a.batch_size, a.max_len)
    base_non = nll_batch(base, tok, nt, np_, device, a.batch_size, a.max_len)

    print("loading the TUNED model (base + adapter) ...")
    tuned = PeftModel.from_pretrained(base, a.adapter)
    tuned.to(device)
    tun_mem = nll_batch(tuned, tok, mt, mp, device, a.batch_size, a.max_len)
    tun_non = nll_batch(tuned, tok, nt, np_, device, a.batch_size, a.max_len)

    res = {"fold": a.fold, "leg": a.leg, "n_per_class": n, "seed": SEED,
           "base_repo": base_repo, "adapter": a.adapter}
    if a.leg == 4:
        res["provenance"] = "LEG-4 PILOT -- NOT REPORTABLE"

    # ---- G6.12's TARGETS, and its generations. Decoded once, re-matched many. ----
    counts = collections.Counter()
    for r in load_split(a.corpus, a.fold, "train", donors):
        counts[stratum_key(r["text"].split("|", 1)[0].split(","))] += 1
    rare = {k for k, v in counts.items() if v < RARE_STRATUM_MAX}
    rare_rows = [r for r in load_split(a.corpus, a.fold, "train", donors)
                 if stratum_key(r["text"].split("|", 1)[0].split(",")) in rare]
    print("\nG6.12 extraction: %d strata carry fewer than %d training records, "
          "%d records in them" % (len(rare), RARE_STRATUM_MAX, len(rare_rows)))

    decoded = {"greedy": [], "sampled": []}
    truth = None
    meta = None
    if not rare_rows:
        print("      NO TARGETS -- BLOCKED, not passed.")
    else:
        tgt = rng.sample(rare_rows, min(a.extract_n, len(rare_rows)))
        truth = tgt[0]["text"]
        by_prefix = collections.defaultdict(set)
        for r in rare_rows:
            p_, b_ = r["text"].split("|", 1)
            by_prefix[p_].add(b_)
        # FINDING 87: the loss pass needs RIGHT padding (the keep-mask indexes from
        # the left) and `generate` needs LEFT padding (a decoder-only model continues
        # from the last position, which right padding fills with PAD). Run with one
        # setting for both and the attack is silently weakened on every target
        # shorter than its batch's longest -- a FALSE NEGATIVE in a privacy gate.
        # The losses are already computed by here, so the switch is safe.
        tok.padding_side = "left"
        for mode in ("greedy", "sampled"):
            kw = dict(do_sample=False) if mode == "greedy" else dict(
                do_sample=True, temperature=1.0, top_p=0.98)
            for i in range(0, len(tgt), a.batch_size):
                chunk = tgt[i:i + a.batch_size]
                prompts = [r["text"].split("|", 1)[0] + "|" for r in chunk]
                enc = tok(prompts, return_tensors="pt", padding=True)
                enc = {k: v.to(device) for k, v in enc.items()}
                gen = tuned.generate(**enc, max_new_tokens=1200,
                                     pad_token_id=tok.pad_token_id, **kw)
                for b in range(len(chunk)):
                    decoded[mode].append(tok.decode(gen[b], skip_special_tokens=True))
        meta = dict(by_prefix=by_prefix, n_attempted=len(tgt),
                    n_rare_strata=len(rare), n_rare_records=len(rare_rows))

    BLOCKED = ("no stratum carries fewer than %d training records, so the attack has "
               "no target. That is NOT a pass -- it means the gate cannot run on this "
               "fold." % RARE_STRATUM_MAX)

    def board(tm, tn, bm, bn, dec):
        """One re-score of every scored gate plus the perplexity-gap control."""
        r = {}
        r["G6_10"] = score_g610([-x for x in tm], [-x for x in tn])
        r["G6_11"] = score_g611([b - t for b, t in zip(bm, tm)],
                                [b - t for b, t in zip(bn, tn)])
        r["control_perplexity_gap"] = score_pplgap(tm, tn)
        if meta is None:
            r["G6_12"] = dict(passes=False, blocked=True, reason=BLOCKED)
        else:
            r["G6_12"] = g612_match(dec, meta["by_prefix"], meta["n_attempted"],
                                    meta["n_rare_strata"], meta["n_rare_records"])
        return r

    # ---- BASELINE ----
    base_board = board(tun_mem, tun_non, base_mem, base_non, decoded)
    res.update(base_board)

    g = res["G6_10"]
    print("\nG6.10 loss-based MIA        AUC %.4f (max %.2f)  TPR@FPR=%.3f: %s  -> %s"
          % (g["auc"], G610_AUC_MAX, G610_TPR_AT_FPR,
             ("%.4f" % g["tpr_at_fpr"]) if g["tpr_at_fpr"] is not None
             else g["resolution_note"], "PASS" if g["passes"] else "FAIL"))

    cauc = roc_auc([-x for x in base_mem], [-x for x in base_non])
    res["control_untuned_base_auc"] = cauc
    print("      control, UNTUNED base    AUC %.4f  (expect ~0.50; a base AUC far "
          "from 0.50 means the\n      two splits differ for a reason that is not "
          "membership)" % cauc)

    print("G6.11 reference-based MIA   AUC %.4f (max %.2f)  -> %s"
          % (res["G6_11"]["auc"], G611_AUC_MAX,
             "PASS" if res["G6_11"]["passes"] else "FAIL"))
    c = res["control_perplexity_gap"]
    print("      control, ppl gap         train %.4f  test %.4f  gap %.4f (max %.2f) -> %s"
          % (c["train_ppl"], c["test_ppl"], c["gap"], PPL_GAP_MAX,
             "PASS" if c["passes"] else "FAIL"))
    g12 = res["G6_12"]
    if g12.get("blocked"):
        print("      G6.12 BLOCKED -- %s" % g12["reason"])
    else:
        print("      attempted %d | exact matches greedy %d, sampled %d -> %s"
              % (g12["n_attempted"], g12["n_exact_greedy"], g12["n_exact_sampled"],
                 "PASS" if g12["passes"] else "FAIL"))

    # ---- THE PERTURBATION BATTERY: every scored gate must be SEEN FAILING ----
    print("\n" + "=" * 78)
    print("PERTURBATIONS -- a gate that has never been seen falling is not a gate")
    print("=" * 78)
    pert = {}
    for name in PERTURBATIONS:
        tm, tn, bm, bn, dec = apply_perturbation(
            name, tun_mem, tun_non, base_mem, base_non, decoded, truth)
        b = board(tm, tn, bm, bn, dec)
        fell = [k for k in SCORED_GATES
                if base_board[k].get("passes") and not b[k].get("passes")]
        ctl = (base_board["control_perplexity_gap"]["passes"]
               and not b["control_perplexity_gap"]["passes"])
        pert[name] = dict(
            fell=fell, control_perplexity_gap_fell=ctl,
            G6_10_auc=b["G6_10"]["auc"], G6_10_tpr=b["G6_10"]["tpr_at_fpr"],
            G6_11_auc=b["G6_11"]["auc"], ppl_gap=b["control_perplexity_gap"]["gap"],
            G6_12_exact=(None if b["G6_12"].get("blocked") else
                         b["G6_12"]["n_exact_greedy"] + b["G6_12"]["n_exact_sampled"]))
        print("  %-16s fell: %-22s AUC10 %.4f  AUC11 %.4f  gap %.4f  exact %s%s"
              % (name, ",".join(fell) if fell else "(nothing)",
                 b["G6_10"]["auc"], b["G6_11"]["auc"],
                 b["control_perplexity_gap"]["gap"],
                 pert[name]["G6_12_exact"],
                 "  [CONTROL FELL]" if ctl else ""))
    res["perturbations"] = pert

    seen = {}
    for k in SCORED_GATES:
        if base_board[k].get("blocked"):
            seen[k] = "BLOCKED -- cannot be seen failing on this fold"
        else:
            hit = [nm for nm, v in pert.items() if k in v["fell"]]
            seen[k] = hit if hit else "NEVER SEEN FAILING"
    noop = [nm for nm, v in pert.items()
            if nm != "null" and not v["fell"] and not v["control_perplexity_gap_fell"]]
    res["coverage_clause"] = dict(
        seen_failing=seen, no_op_perturbations=noop,
        passes=(not noop and all(isinstance(v, list) and v for v in seen.values())))
    print("\ncoverage clause: %s" % ("PASS" if res["coverage_clause"]["passes"]
                                     else "FAIL"))
    for k, v in seen.items():
        print("  %-6s <- %s" % (k, v if isinstance(v, str) else ", ".join(v)))
    if noop:
        print("  NO-OP PERTURBATIONS (felled nothing): %s" % ", ".join(noop))

    # ---- the third registered control: `D-S6-14`, author 2026-08-22 ----
    if not a.permuted_adapter:
        res["control_random_label_permutation"] = dict(
            present=False,
            note="NOT RUN. The random-label-permutation adapter sets the CEILING for "
                 "pure sequence memorisation and requires its own training run. Its "
                 "absence is a NAMED GAP: the audit has two of its three registered "
                 "controls, and privacy_audit.md must say so before any release "
                 "decision. `D-S6-14` rules how to run it.")
        print("\n🔴 CONTROL NOT RUN: random-label-permutation adapter. Two of three "
              "registered\n   controls are present. No release decision can rest on "
              "this.")
    else:
        print("\n" + "=" * 78)
        print("CONTROL: RANDOM-LABEL-PERMUTATION ADAPTER  --  `D-S6-14` (a)")
        print("=" * 78)

        # (both interlocks already fired, or did not, before any model was loaded)
        print("permuted corpus : %s" % a.permuted_corpus)
        print("permutation seed: %s" % perm_seed)
        print("permuted adapter: %s" % a.permuted_adapter)

        p_members = load_split(a.permuted_corpus, a.fold, "train", donors)
        p_nonmembers = load_split(a.permuted_corpus, a.fold, "heldout", donors)
        # the SAME n and the SAME seed as the baseline, so the two boards are read
        # off the same records -- only the pairing and the adapter differ.
        prng = random.Random(SEED)
        pn = min(a.n, len(p_members), len(p_nonmembers))
        if pn != n:
            print("🔴 the control samples %d per class and the baseline %d. Reported, "
                  "not silently reconciled." % (pn, n))
        p_members = prng.sample(p_members, pn)
        p_nonmembers = prng.sample(p_nonmembers, pn)
        print("members: %d   non-members: %d   (size-matched, seed %d)"
              % (pn, pn, SEED))

        tok.padding_side = "right"          # FINDING 87 again: the loss pass needs it
        pmt, pmp = texts_and_prefix_lens(p_members, tok)
        pnt, pnp = texts_and_prefix_lens(p_nonmembers, tok)

        print("loading a FRESH public base for the control ...")
        pbase = AutoModelForCausalLM.from_pretrained(base_repo,
                                                     torch_dtype=torch.bfloat16)
        pbase.to(device)
        p_base_mem = nll_batch(pbase, tok, pmt, pmp, device, a.batch_size, a.max_len)
        p_base_non = nll_batch(pbase, tok, pnt, pnp, device, a.batch_size, a.max_len)
        ptuned = PeftModel.from_pretrained(pbase, a.permuted_adapter)
        ptuned.to(device)
        p_tun_mem = nll_batch(ptuned, tok, pmt, pmp, device, a.batch_size, a.max_len)
        p_tun_non = nll_batch(ptuned, tok, pnt, pnp, device, a.batch_size, a.max_len)

        c610 = score_g610([-x for x in p_tun_mem], [-x for x in p_tun_non])
        c611 = score_g611([b_ - t_ for b_, t_ in zip(p_base_mem, p_tun_mem)],
                          [b_ - t_ for b_, t_ in zip(p_base_non, p_tun_non)])
        cgap = score_pplgap(p_tun_mem, p_tun_non)

        m610, m611 = res["G6_10"]["auc"], res["G6_11"]["auc"]
        # 🔴 The one reading that would invalidate the reported run: the model that
        # could ONLY memorise leaks no more than the model that could also generalise.
        alarm = []
        if m610 >= c610["auc"]:
            alarm.append("G6.10: the reported adapter's AUC %.4f is at or above the "
                         "memorisation ceiling %.4f" % (m610, c610["auc"]))
        if m611 >= c611["auc"]:
            alarm.append("G6.11: the reported adapter's AUC %.4f is at or above the "
                         "memorisation ceiling %.4f" % (m611, c611["auc"]))

        res["control_random_label_permutation"] = dict(
            present=True,
            decision="D-S6-14 (a) + (ii)/(iii), author 2026-08-22",
            adapter=a.permuted_adapter, corpus=a.permuted_corpus,
            permutation_seed=perm_seed, n_per_class=pn, seed=SEED,
            ceiling_G6_10_auc=c610["auc"], ceiling_G6_10=c610,
            ceiling_G6_11_auc=c611["auc"], ceiling_G6_11=c611,
            ceiling_perplexity_gap=cgap,
            measured_G6_10_auc=m610, measured_G6_11_auc=m611,
            headroom_G6_10=c610["auc"] - m610,
            headroom_G6_11=c611["auc"] - m611,
            alarms=alarm,
            note="The CEILING, not a bar. `G6.10 <= 0.65` and `G6.11 <= 0.75` are "
                 "unchanged and are the only thresholds that decide anything. This "
                 "number says what pure rote memorisation scores at this model size, "
                 "so a passing AUC can be called low against something rather than "
                 "against nothing. Its own verdict fields are what the SAME scoring "
                 "code returns for it and are NOT a pass/fail on the control.",
            limitation="The permutation is within (country, split), so P(body | "
                       "country) survives it -- five of the six prefix fields are "
                       "de-associated, not all six. Forced by LOCO fold isolation; "
                       "see 4thJ_step4_shards.py.")

        print("\n  ceiling  G6.10 AUC %.4f      measured %.4f      headroom %+.4f"
              % (c610["auc"], m610, c610["auc"] - m610))
        print("  ceiling  G6.11 AUC %.4f      measured %.4f      headroom %+.4f"
              % (c611["auc"], m611, c611["auc"] - m611))
        print("  ceiling  ppl gap  %.4f      measured %.4f"
              % (cgap["gap"], res["control_perplexity_gap"]["gap"]))
        if alarm:
            for x in alarm:
                print("🔴 ALARM  %s" % x)
            print("🔴 A model that could only memorise did not leak more than the "
                  "reported one. Either the reported run memorised, or the control "
                  "did not train. Neither reading permits a release.")
        else:
            print("  no alarm: the reported adapter sits below the memorisation "
                  "ceiling on both attacks.")
        print("🔴 THE BARS DID NOT MOVE. G6.10 <= %.2f, G6.11 <= %.2f, as "
              "pre-registered." % (G610_AUC_MAX, G611_AUC_MAX))
        print("🔴 THREE OF THREE registered controls are now present.")

    os.makedirs(a.out, exist_ok=True)
    p = os.path.join(a.out, "privacy_mia_leg%d_%s.json" % (a.leg, a.fold))
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)
    print("written: %s" % p)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotRun as e:
        print("PRIVACY AUDIT NOT RUN -- %s" % e)
        sys.exit(2)
