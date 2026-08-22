# -*- coding: utf-8 -*-
"""Step 7 gate battery -- `G7.1`-`G7.13` scored on GENERATED text.

  usage: python 4thJ_gates_step7.py --gen DIR --step2 DIR --crosswalk PATH
                                    [--folds es,uk,it] [--leg 4]
                                    [--perturb NAME] [--out JSON]

Everything before today's batches was scored on the CORPUS or on fixtures. This
module is the first thing in Step 7 that reads what the model actually wrote.

🔴 THREE READINGS ARE WRITTEN DOWN HERE RATHER THAN LEFT TO THE OPERATOR.

1. **`G7.1`-`G7.2` are ENFORCEMENT CONFIRMATIONS on the constrained batch.** The
   validation document says so in its own words and so does the coverage clause:
   they cannot fall while the mask is on, and a "gates seen failing" tally that
   counts them is a tally inflating itself. They are reported with the label
   attached to them in the artefact, not in a footnote.

2. 🔴 **`G7.4` IS TWO GATES WEARING ONE NAME, AND `D-S7-5` (1) RULED THEM
   APART on 2026-08-22.** Its SELF-CONTRADICTION half -- `cop_alone` asserted
   alongside company -- is now an ENFORCEMENT CONFIRMATION: the 31 impossible
   flag sets were removed from the `COP` alphabet after being verified absent
   from all 2,024,068 real episodes, so the grammar cannot emit one. It is the
   VERDICT. Its HOUSEHOLD-MEMBERSHIP half is REPORTED AND NEVER ENFORCED, because
   enforcing it would reject 1.49 % of real diaries at a 14.7x country spread --
   a basis change the ruling declined. It does NOT enter the verdict.
   🔴 Every Leg-4 rehearsal batch was generated BEFORE the ruling, so on those
   batches the first half is still a measurement and still falls. That is the
   defect the ruling removes, not a gate that fails.

3. 🔴 **`G7.7`'s firing rate is scored PER DIARY, not per token** -- see
   `D-S7-4`. vLLM exposes no count of mask interventions, and a per-token rate
   would read ~100 % for every batch (the mask removes at least one candidate at
   nearly every position), which is not a number anyone could act on. The
   operative reading is *the share of diaries the model gets wrong when the mask
   is OFF*, which is what the document's own expectations (`> 35 %` untuned,
   `< 2 %` tuned) are sized for. `G7.5` is that same quantity pooled; `G7.7` is
   it per stratum. Stated, because it is a definition and not a measurement.

`G7.10` is NOT re-run here. It has its own artefact from its own job and a gate
does not get scored twice by two different pieces of code.
"""

import argparse
import collections
import copy
import importlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

grammar = importlib.import_module("4thJ_step7_grammar")
indoor = importlib.import_module("4thJ_step7_indoor")
import decoder as dec
from encoder import SHARED_FLAGS, load_bit_positions

POLICY = grammar.TransitionPolicy.PERMISSIVE

# `FINDING 45`, measured on the real corpus. `G7.3` is a REPORTED RATE under
# `D-S7-2` (a); these are what the generated rate is reported AGAINST.
CORPUS_G73 = {"es": 43.18, "uk": 24.64, "it": 23.63, "all": 28.95}

G75_TARGET = 0.9990        # unconstrained well-formedness
G78_MAX_RATIO = 3.0        # highest stratum firing rate / population rate
G79_BAND_MIN = 5.0         # minutes/day per category
V7A_MIN_STRATA = 10        # strata carrying >= 100 records
V7A_MIN_RECORDS = 100

# `G7.4`. What the conditioning household makes IMPOSSIBLE, per flag. The rule is
# membership, not behaviour: a person whose household contains no partner cannot
# be co-present with a household partner. `cop_other_persons` is people from
# OUTSIDE the household and is never constrained by the household type.
HH_FORBIDS = {
    "one_person":                  ("cop_partner", "cop_children", "cop_parent", "cop_other_hh"),
    "couple_no_children":          ("cop_children",),
    "single_parent_with_children": ("cop_partner",),
    "couple_with_children":        (),
    "other_complex":               (),
    "unknown":                     (),
}


# A three-digit string that is NOT one of the 159 ACT codes. Asserted against the
# live alphabet at run time, never trusted -- see the `g72_out_of_list_act` note.
OUT_OF_LIST_ACT = "100"


class GateError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def load_batch(gen_dir, leg, fold, tag):
    path = os.path.join(gen_dir, "generated_leg%d_%s_%s.jsonl" % (leg, fold, tag))
    if not os.path.exists(path):
        return None, path, None
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    spath = os.path.join(gen_dir, "generated_leg%d_%s_%s_summary.json" % (leg, fold, tag))
    summary = None
    if os.path.exists(spath):
        with open(spath, encoding="utf-8") as fh:
            summary = json.load(fh)
    return rows, path, summary


def stratum_key(rec):
    """Step 4's convention, verbatim (`4thJ_step4_diagnostics.py:96`). Reused
    rather than redefined -- two steps disagreeing about what a stratum is would
    make every cross-step comparison in the paper quietly wrong."""
    return (rec["country"], rec["strat_age_band"], rec["strat_sex"],
            rec["strat_hh_type"], rec["strat_day_type"])


# ---------------------------------------------------------------------------
# perturbations -- each one corrupts the BATCH, which is what the defect it
# stands for would actually look like downstream
# ---------------------------------------------------------------------------
def _split(text):
    body = text[:-len(grammar.EOR)]
    prefix, eps = body.split(grammar.PREFIX_BODY_SEP, 1)
    chunks = eps.split(grammar.EPISODE_SEP)[:-1]
    return prefix, [c.split(grammar.FIELD_SEP) for c in chunks]


def _join(prefix, fields):
    eps = "".join(grammar.FIELD_SEP.join(f) + grammar.EPISODE_SEP for f in fields)
    return prefix + grammar.PREFIX_BODY_SEP + eps + grammar.EOR


def perturb(name, con, unc):
    """Returns (constrained, unconstrained, note). Both lists are deep-copied."""
    con, unc = copy.deepcopy(con), copy.deepcopy(unc)
    if name in (None, "null"):
        return con, unc, "null perturbation: nothing changed"

    if name == "g71_break_tally":
        p, f = _split(con[0]["text"])
        f[0][0] = str(int(f[0][0]) + 10)
        con[0]["text"] = _join(p, f)
        return con, unc, "record 0's first duration +10 min: the day sums to 1450"

    if name == "g72_out_of_list_act":
        # 🔴 This perturbation was FIRST WRITTEN with `999`, which IS one of the
        # 159 codes -- so it changed nothing and `G7.2` stayed green. The coverage
        # clause caught it, which is the whole reason the clause exists. `100` is
        # checked against the live alphabet below rather than trusted.
        p, f = _split(con[0]["text"])
        f[0][1] = OUT_OF_LIST_ACT
        con[0]["text"] = _join(p, f)
        return con, unc, ("record 0's first ACT set to %s, which is not in the 159 "
                          "alphabet" % OUT_OF_LIST_ACT)

    if name == "g74_clean_cop":
        # `G7.4` FAILs at baseline (`FINDING 81`), so no perturbation can be seen
        # felling it. This is the opposite demonstration and it is the one that is
        # actually owed: with every COP set to "not collected" there is nothing to
        # contradict, and the gate must go GREEN. A gate stuck at FAIL is as
        # uninformative as one stuck at PASS.
        for r in con:
            pp, f = _split(r["text"])
            for e in f:
                e[4] = "64"
            r["text"] = _join(pp, f)
        return con, unc, ("every COP set to 64 (not collected): G7.4 has nothing "
                          "left to contradict and must PASS")

    if name == "g76_break_decoder":
        p, f = _split(con[0]["text"])
        f[0][1] = "99"          # two digits: `decode_episode` refuses it outright
        con[0]["text"] = _join(p, f)
        return con, unc, ("record 0's first ACT set to the two-digit 99, which the "
                          "SHIPPED decoder refuses. G7.2 falls with it, and that is "
                          "the finding: the decoder and the grammar accept the same "
                          "language, so G7.6 is a third enforcement confirmation "
                          "rather than an independent measurement")

    if name == "g74_wrong_hh_variant":
        for r in con:
            if r["strat_hh_type"] == "one_person":
                p, f = _split(r["text"])
                f[0][4] = "2"        # bit 1 == cop_partner
                r["text"] = _join(p, f)
                return con, unc, ("a one_person diary given cop_partner: the wrong "
                                  "household grammar variant, in effect")
        raise GateError("no one_person record in the batch to perturb")

    if name == "g75_control_is_valid":
        return con, copy.deepcopy(con), ("the unconstrained control replaced by the "
                                         "constrained batch: G7.5 must PASS, which is "
                                         "how the gate is shown to discriminate rather "
                                         "than to always fail")

    if name == "g78_concentrate":
        # Move every unconstrained INVALID record into one stratum, leaving the
        # population rate untouched. That is the pre-registered shape exactly.
        target = None
        for r in unc:
            if not r["oracle_valid"]:
                target = stratum_key(r)
                break
        if target is None:
            raise GateError("no invalid record in the control to concentrate")
        for r in unc:
            if not r["oracle_valid"]:
                (r["country"], r["strat_age_band"], r["strat_sex"],
                 r["strat_hh_type"], r["strat_day_type"]) = target
        return con, unc, ("every invalid control record relabelled into one stratum; "
                          "the population rate is unchanged by construction")

    if name == "g79_shift_mask":
        # Relabel the most common ACT in the constrained batch to the second most
        # common: level-1 minute marginals move, nothing else does.
        mins = act_minutes(con)
        top = sorted(mins, key=lambda k: -mins[k])[:2]
        for r in con:
            p, f = _split(r["text"])
            for e in f:
                if e[1] == top[0]:
                    e[1] = top[1]
            r["text"] = _join(p, f)
        return con, unc, ("ACT %s relabelled to %s throughout the constrained batch: "
                          "the mask forbidding a common activity" % (top[0], top[1]))

    if name == "g711_drop":
        k = max(1, len(con) // 100)
        return con[:-k], unc, "%d of %d constrained records silently discarded" % (k, len(con) + k)

    if name == "g713_local_copy":
        return con, unc, "handled inside G7.13 -- a local OUTDOOR_AT_HOME copy differing by one code"

    raise GateError("unknown perturbation %r" % name)


def act_minutes(rows):
    out = collections.Counter()
    for r in rows:
        try:
            _, f = _split(r["text"])
        except Exception:
            continue
        for e in f:
            if len(e) == 5 and e[0].isdigit():
                out[e[1]] += int(e[0])
    return out


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------
def structural(rows, alph):
    """One pass giving `G7.1`, `G7.2` and `G7.3` their counts."""
    n_tally, n_alpha, n_direct_return, n_scored = 0, 0, 0, 0
    tally_bad, alpha_bad = [], []
    for r in rows:
        text = r["text"]
        ok, why = grammar.validate_record(text, alph, POLICY)
        if not ok:
            if "sum to" in why or "multiple of" in why or "tally" in why:
                tally_bad.append(why)
            else:
                alpha_bad.append(why)
            continue
        n_scored += 1
        n_tally += 1
        n_alpha += 1
        # `G7.3`, reported not enforced (`D-S7-2` (a)).
        prev, seen_transport = None, False
        hit = False
        _, f = _split(text)
        for e in f:
            loc = e[3]
            if loc in grammar.LOC_TRANSPORT:
                seen_transport = True
            elif prev == "other_place" and loc == "at_home" and not seen_transport:
                hit = True
            if loc == "other_place":
                seen_transport = False
            prev = loc
        n_direct_return += 1 if hit else 0
    return dict(n=len(rows), n_scored=n_scored,
                g71_pass=len(tally_bad) == 0, g71_bad=len(tally_bad),
                g72_pass=len(alpha_bad) == 0, g72_bad=len(alpha_bad),
                g71_examples=tally_bad[:3], g72_examples=alpha_bad[:3],
                g73_direct_return=n_direct_return,
                g73_rate=100.0 * n_direct_return / max(n_scored, 1))


def gate_g7_4(rows, bitpos):
    """`G7.4`, split in two by `D-S7-5` (1), RULED 2026-08-22.

    HALF ONE -- SELF-CONTRADICTION. `cop_alone` asserted alongside any other
    co-presence flag. 🔴 This is now an ENFORCEMENT CONFIRMATION: the 31 flag sets
    that express it were removed from the grammar's `COP` alphabet, verified
    against 0 of 2,024,068 real episodes first. A hit on a batch generated under
    the ruled grammar means the grammar was not applied, not that the model erred.
    A hit on a batch generated BEFORE the ruling -- every Leg-4 rehearsal batch --
    is a MEASUREMENT of what the unconstrained alphabet allowed, and is exactly
    the defect the ruling removes. The two readings are not distinguishable from
    the record, so the batch's provenance decides which one applies and the
    artefact says which batch it scored.

    HALF TWO -- HOUSEHOLD MEMBERSHIP. Reported, NEVER enforced. The ruling was
    explicit: enforcing it would reject 1.49 % of real diaries at a 14.7x country
    spread, which is a basis change. It carries its own rate and its own count and
    it does NOT enter the verdict.
    """
    self_bad = collections.Counter()
    hh_bad = collections.Counter()
    n_ep, n_checked = 0, 0
    n_self_records, n_hh_records = 0, 0
    for r in rows:
        try:
            _, f = _split(r["text"])
        except Exception:
            continue
        forbidden = HH_FORBIDS.get(r["strat_hh_type"])
        if forbidden is None:
            raise GateError("household type %r has no G7.4 rule" % r["strat_hh_type"])
        rec_self, rec_hh = False, False
        for e in f:
            if len(e) != 5 or not e[4].isdigit():
                continue
            n_ep += 1
            flags = dec.decode_cop(int(e[4]), bitpos)
            if flags is None:            # 64 == not collected. Nothing to check.
                continue
            n_checked += 1
            if flags["cop_alone"] and any(flags[k] for k in SHARED_FLAGS
                                          if k != "cop_alone"):
                self_bad["cop_alone with company"] += 1
                rec_self = True
            for k in forbidden:
                if flags[k]:
                    hh_bad["%s in %s" % (k, r["strat_hh_type"])] += 1
                    rec_hh = True
        n_self_records += 1 if rec_self else 0
        n_hh_records += 1 if rec_hh else 0
    n = max(len(rows), 1)
    return dict(
        # 🔴 THE VERDICT IS THE SELF-CONTRADICTION HALF ALONE.
        passes=not self_bad,
        n_episodes=n_ep, n_checked=n_checked,
        self_contradiction=dict(
            violations=dict(self_bad), n_episodes=sum(self_bad.values()),
            n_records=n_self_records, rate_pct=100.0 * n_self_records / n,
            enforced_by_grammar_under="D-S7-5 (1), COP alphabet 65 -> 34"),
        household_membership=dict(
            violations=dict(hh_bad), n_episodes=sum(hh_bad.values()),
            n_records=n_hh_records, rate_pct=100.0 * n_hh_records / n,
            enforced=False,
            note="REPORTED, NOT ENFORCED and NOT IN THE VERDICT (D-S7-5 (1)). "
                 "The real corpus violates this rule in 1.49 % of diaries, "
                 "14.7x unevenly by country."),
        # kept so nothing downstream that read the old key breaks silently
        violations=dict(self_bad),
        n_records_violating=n_self_records,
        enforced_by_grammar=True)


def gate_g7_5(unc, alph):
    """🔴 The one Tier-3 gate that measures the MODEL."""
    if not unc:
        return dict(passes=False, blocked=True,
                    reason="no unconstrained control batch on disk. G7.5 FAILs "
                           "rather than skipping: an absent control is the state "
                           "in which every other number here is a tautology.")
    n_ok = sum(1 for r in unc if grammar.validate_record(r["text"], alph, POLICY)[0])
    rate = n_ok / float(len(unc))
    reasons = collections.Counter()
    for r in unc:
        ok, why = grammar.validate_record(r["text"], alph, POLICY)
        if not ok:
            reasons[why.split(" (")[0][:60]] += 1
    return dict(passes=rate >= G75_TARGET, blocked=False, n=len(unc), n_valid=n_ok,
                rate=rate, target=G75_TARGET,
                top_reasons=dict(reasons.most_common(8)))


def gate_g7_6(rows, bitpos):
    """Round-trip through the SHIPPED Step 3 decoder (`tools/decoder.py`)."""
    n_ok, fails = 0, []
    decoded = []
    for r in rows:
        try:
            d = dec.decode_record(r["text"], bitpos)
        except Exception as e:
            fails.append("%s: %s" % (type(e).__name__, str(e)[:90]))
            continue
        decoded.append(d)
        n_ok += 1
    return dict(passes=not fails, n=len(rows), n_decoded=n_ok,
                examples=fails[:3]), decoded


def gate_g7_7_g7_8(unc, alph):
    """`D-S7-4`: the firing rate is the share of diaries the model gets WRONG with
    the mask off, per stratum. `V7.a` FAILs both gates if fewer than 10 strata
    carry >= 100 records -- it does not skip them."""
    if not unc:
        return dict(passes=False, blocked=True,
                    reason="no unconstrained control: the firing rate is not "
                           "observable and both gates FAIL rather than skip (V7.a)")
    per = collections.defaultdict(lambda: [0, 0])   # stratum -> [n, n_invalid]
    n_bad = 0
    for r in unc:
        ok = grammar.validate_record(r["text"], alph, POLICY)[0]
        k = stratum_key(r)
        per[k][0] += 1
        per[k][1] += 0 if ok else 1
        n_bad += 0 if ok else 1
    pop_rate = n_bad / float(len(unc))
    big = {k: v for k, v in per.items() if v[0] >= V7A_MIN_RECORDS}
    v7a = len(big) >= V7A_MIN_STRATA
    rates = {k: v[1] / float(v[0]) for k, v in big.items()}
    worst_k = max(rates, key=rates.get) if rates else None
    ratio = (rates[worst_k] / pop_rate) if (worst_k and pop_rate > 0) else None

    reasons = []
    if not v7a:
        reasons.append(
            "V7.a: only %d stratum/strata carry >= %d records (need %d). Both G7.7 "
            "and G7.8 FAIL rather than skipping -- an evenness ratio computed over "
            "cells of size 3 is noise wearing a threshold's clothes."
            % (len(big), V7A_MIN_RECORDS, V7A_MIN_STRATA))
    if ratio is not None and ratio >= G78_MAX_RATIO:
        reasons.append("G7.8: worst-stratum ratio %.3f >= %.1f" % (ratio, G78_MAX_RATIO))

    return dict(passes=not reasons, blocked=False, reasons=reasons,
                n=len(unc), n_strata=len(per), n_strata_ge_100=len(big),
                population_firing_rate=round(pop_rate, 6),
                worst_stratum=list(worst_k) if worst_k else None,
                worst_stratum_rate=round(rates[worst_k], 6) if worst_k else None,
                ratio=round(ratio, 4) if ratio is not None else None,
                ratio_max=G78_MAX_RATIO,
                v7a_satisfied=v7a)


def gate_g7_9(con, unc, alph):
    """Renormalisation audit. The control is the REJECTION-SAMPLED subset of the
    unconstrained batch -- the valid ones -- which is what rejection sampling
    produces. Its size is the whole difficulty and it is reported first."""
    valid = [r for r in unc if grammar.validate_record(r["text"], alph, POLICY)[0]]
    if not valid:
        return dict(passes=False, blocked=True, n_control=0,
                    reason="the rejection-sampled control is EMPTY: not one "
                           "unconstrained diary is well-formed, so there is nothing "
                           "to audit the mask against.")
    a, b = act_minutes(con), act_minutes(valid)
    na, nb = float(len(con)), float(len(valid))
    cats = set(a) | set(b)
    devs = {c: (a[c] / na) - (b[c] / nb) for c in cats}
    worst = max(devs, key=lambda c: abs(devs[c]))
    # The control's own sampling error, so a FAIL can be read as "the mask moved
    # it" or "the control is too small to tell" rather than being ambiguous.
    implied = int(round(len(con) / (nb / len(unc)))) if nb else None
    reasons = []
    if abs(devs[worst]) > G79_BAND_MIN:
        reasons.append("worst category %s deviates %.2f min/day (band +/- %.1f)"
                       % (worst, devs[worst], G79_BAND_MIN))
    if nb < 0.5 * na:
        reasons.append(
            "the control carries %d valid diaries against %d constrained ones. A "
            "marginal estimated from %d diaries cannot resolve %.1f min/day, so "
            "this verdict is about the CONTROL, not about the mask. Matching the "
            "constrained batch would need ~%s unconstrained draws."
            % (nb, na, nb, G79_BAND_MIN, "{:,}".format(implied) if implied else "?"))
    return dict(passes=not reasons, blocked=False, reasons=reasons,
                n_constrained=int(na), n_control=int(nb),
                control_yield=round(nb / len(unc), 6),
                implied_draws_for_parity=implied,
                worst_category=worst, worst_deviation_min_day=round(devs[worst], 4),
                band_min_day=G79_BAND_MIN,
                deviations_over_band={c: round(d, 3) for c, d in devs.items()
                                      if abs(d) > G79_BAND_MIN})


def gate_g7_10(gen_dir):
    """NOT re-run. Read its own artefact, or FAIL."""
    p = os.path.join(gen_dir, "g710_oracle_agreement.json")
    if not os.path.exists(p):
        return dict(passes=False, reason="no g710_oracle_agreement.json at %s" % p)
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    return dict(passes=(d.get("verdict") == "PASS" and d.get("n_disagreements") == 0),
                artefact=p, n=d.get("n_strings"),
                n_disagreements=d.get("n_disagreements"),
                xgrammar_version=d.get("xgrammar_version"),
                note="read from its own job's artefact; not re-scored here")


def gate_g7_11(rows, summary, path):
    """`V7.d`: it COUNTS. It never asserts an expected number."""
    if summary is None:
        return dict(passes=False, reason="no summary beside %s, so the requested "
                                         "count is unknown and G7.11 cannot count "
                                         "against anything" % path)
    req = summary.get("n")
    got = len(rows)
    return dict(passes=(req == got), n_requested=req, n_on_disk=got,
                unexplained_discards=(req - got) if req is not None else None)


def gate_g7_12(gen_dir):
    p = os.path.join(gen_dir, "throughput_comparison.md")
    return dict(passes=os.path.exists(p), path=p,
                note=("work item 7.2. FAILs until the two-backbone comparison is "
                      "written; a campaign sized from one backbone's number is an "
                      "unsized campaign."))


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------
def run_fold(gen_dir, step2, bitpos, alph, leg, fold, pname):
    con, cpath, csum = load_batch(gen_dir, leg, fold, "constrained")
    unc, upath, usum = load_batch(gen_dir, leg, fold, "nogrammar")
    if con is None:
        return dict(fold=fold, blocked=True,
                    reason="no constrained batch at %s" % cpath)
    unc = unc or []

    con, unc, note = perturb(pname, con, unc)

    # `V7.b` -- counts and paths BEFORE any verdict.
    print("-" * 78)
    print("fold %s | leg %d | perturbation %s" % (fold, leg, pname or "null"))
    print("  %-14s %s" % ("constrained", cpath))
    print("  %-14s %s" % ("control", upath if unc else "MISSING"))
    print("  records        %d constrained, %d unconstrained" % (len(con), len(unc)))
    print("  alphabets      ACT %d | ACT2 %d | LOC %d | COP %d"
          % (len(alph["act"]), len(alph["act2"]), len(alph["loc"]), len(alph["cop"])))
    print("  tally states   %d" % grammar.N_TALLY_STATES)
    print("  adapter        %s" % (csum or {}).get("adapter", "?"))
    print("  note           %s" % note)

    st = structural(con, alph)
    g74 = gate_g7_4(con, bitpos)
    g75 = gate_g7_5(unc, alph)
    g76, decoded = gate_g7_6(con, bitpos)
    g78 = gate_g7_7_g7_8(unc, alph)
    g79 = gate_g7_9(con, unc, alph)
    g710 = gate_g7_10(gen_dir)
    g711 = gate_g7_11(con, csum, cpath)
    g712 = gate_g7_12(gen_dir)

    shipped, _ = indoor.load_outdoor_at_home(step2)
    used = None
    if pname == "g713_local_copy":
        used = set(shipped) - {sorted(shipped)[0]}
    if not decoded:
        g713 = dict(passes=False,
                    reasons=["no record decoded, so the indoor rule was never reached"])
    else:
        try:
            g713 = indoor.gate_g7_13(decoded, step2, outdoor=used)
        except indoor.IndoorRuleError as e:
            # `4thJ_step7_indoor.py` REFUSES a day that does not sum to 1440 rather
            # than padding it. That refusal is the module behaving correctly, but it
            # must arrive here as a FAILED gate, not as a traceback that takes the
            # whole board down with it -- the `g71_break_tally` perturbation is
            # exactly the case, and a crash there would hide every other verdict.
            g713 = dict(passes=False, reasons=[
                "the indoor rule could not be applied: %s" % str(e).split(". Refused")[0]])

    return dict(
        fold=fold, blocked=False, perturbation=pname or "null", note=note,
        n_constrained=len(con), n_control=len(unc),
        G7_1=dict(passes=st["g71_pass"], kind="ENFORCEMENT CONFIRMATION",
                  n_bad=st["g71_bad"], examples=st["g71_examples"]),
        G7_2=dict(passes=st["g72_pass"], kind="ENFORCEMENT CONFIRMATION",
                  n_bad=st["g72_bad"], examples=st["g72_examples"]),
        G7_3=dict(kind="REPORTED RATE (D-S7-2 (a)) -- no pass/fail",
                  generated_pct=round(st["g73_rate"], 2),
                  corpus_pct=CORPUS_G73.get(fold),
                  n_hit=st["g73_direct_return"], n_scored=st["n_scored"]),
        G7_4=g74, G7_5=g75, G7_6=g76, G7_7_G7_8=g78, G7_9=g79,
        G7_10=g710, G7_11=g711, G7_12=g712, G7_13=g713,
    )


SCORED = ["G7_4", "G7_5", "G7_6", "G7_7_G7_8", "G7_9", "G7_10", "G7_11", "G7_12", "G7_13"]
CONFIRMATIONS = ["G7_1", "G7_2"]


def verdict_line(res, key):
    d = res[key]
    if d.get("blocked"):
        return "BLOCKED"
    return "PASS" if d.get("passes") else "FAIL"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="outputs_step7 directory")
    ap.add_argument("--step2", required=True)
    ap.add_argument("--crosswalk", required=True, help="crosswalk_copresence.csv")
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    bitpos = load_bit_positions(a.crosswalk)
    alph = grammar.build_alphabets(a.step2)
    if OUT_OF_LIST_ACT in alph["act"]:
        raise GateError("OUT_OF_LIST_ACT %r is IN the alphabet, so the G7.2 "
                        "perturbation would be a no-op. That is exactly how the "
                        "first version of it -- which used 999 -- passed silently."
                        % OUT_OF_LIST_ACT)

    print("=" * 78)
    print("Step 7 gate battery -- G7.1-G7.13 on GENERATED text")
    print("=" * 78)
    print("bit positions (read live from the crosswalk): %s" % bitpos)
    if a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE. D-S7-3 (a): these verdicts "
              "rehearse the\n   battery. They are not the paper's numbers.\n")

    out = {"leg": a.leg, "perturbation": a.perturb or "null", "folds": {}}
    for fold in a.folds.split(","):
        res = run_fold(a.gen, a.step2, bitpos, alph, a.leg, fold, a.perturb)
        out["folds"][fold] = res
        if res.get("blocked"):
            print("  🔴 BLOCKED -- %s" % res["reason"])
            continue
        print("\n  %-10s %-28s %s" % ("gate", "verdict", "reading"))
        for k in CONFIRMATIONS:
            print("  %-10s %-28s %s" % (k.replace("_", "."),
                                        verdict_line(res, k) + "  (not a measurement)",
                                        res[k]["kind"]))
        g3 = res["G7_3"]
        print("  %-10s %-28s generated %.2f %% vs corpus %s %%"
              % ("G7.3", "REPORTED", g3["generated_pct"], g3["corpus_pct"]))
        for k in SCORED:
            print("  %-10s %-28s" % (k.replace("_", "."), verdict_line(res, k)), end="")
            d = res[k]
            if k == "G7_5" and not d.get("blocked"):
                print("  %d/%d = %.2f %% (target %.2f %%)"
                      % (d["n_valid"], d["n"], 100 * d["rate"], 100 * d["target"]))
            elif k == "G7_7_G7_8" and not d.get("blocked"):
                print("  pop %.2f %% | strata>=100: %d | ratio %s"
                      % (100 * d["population_firing_rate"], d["n_strata_ge_100"], d["ratio"]))
            elif k == "G7_9" and not d.get("blocked"):
                print("  control %d/%d | worst %s %.2f min/day"
                      % (d["n_control"], d["n_constrained"], d["worst_category"],
                         d["worst_deviation_min_day"]))
            elif k == "G7_4":
                print("  %d episodes checked, %d records violating"
                      % (d["n_checked"], d["n_records_violating"]))
            else:
                print("")
            for r in (d.get("reasons") or ([d["reason"]] if d.get("reason") else [])):
                print("             - %s" % r)
        if res["G7_4"]["violations"]:
            print("             G7.4 violations: %s" % res["G7_4"]["violations"])
        # `indoor.report()` renders the gate's own dict. When the rule could not
        # be applied at all there is no such dict, only a verdict, so the reasons
        # are printed instead of asking the renderer for fields never computed.
        if "outdoor_at_home" in res["G7_13"]:
            print("\n" + indoor.report(res["G7_13"]))
        else:
            print("\nG7.13  NOT APPLIED  " + "; ".join(res["G7_13"]["reasons"]))

    board = collections.Counter()
    for f, res in out["folds"].items():
        if res.get("blocked"):
            continue
        for k in SCORED:
            board[verdict_line(res, k)] += 1
    out["board"] = dict(board)
    print("\n" + "=" * 78)
    print("BOARD over SCORED gates only (G7.1/G7.2 excluded -- coverage clause): %s"
          % dict(board))
    print("=" * 78)

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
