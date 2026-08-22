# -*- coding: utf-8 -*-
"""`G7.10` -- oracle agreement.

  "The hand-written LogitsProcessor oracle and XGrammar accept/reject IDENTICALLY
   on 10,000 sampled strings, including deliberately malformed ones."
                                        -- 4thJ_07_constrainedGeneration_val.md

Two recognisers, written from the same definition by different means:

  * the oracle   -- `4thJ_step7_grammar.py:validate_record()`, procedural
  * the back-end -- the EBNF from `4thJ_step7_ebnf.py`, compiled by XGrammar

They share `build_alphabets()` and nothing else. `G7.10` PASSES only if they
disagree on zero strings AND the sample was not vacuous -- a set the oracle
accepts entirely would make agreement meaningless (`V7.e`).

  usage: python 4thJ_step7_g710.py [--n 10000] [--seed 20260822] [--step2 DIR]
                                   [--out DIR]

🔴 If XGrammar offers no way to match a COMPLETE STRING against a grammar, this
script exits non-zero and says so. It does not fall back to a weaker comparison
and call the gate passed: a gate that cannot be run reports NOT RUN, and NOT RUN
is not a pass.
"""

import argparse
import importlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

grammar = importlib.import_module("4thJ_step7_grammar")
ebnf = importlib.import_module("4thJ_step7_ebnf")

DEFAULT_STEP2 = os.path.normpath(os.path.join(_HERE, "..", "Step2_docs", "outputs_step2"))
DEFAULT_OUT = os.path.normpath(os.path.join(_HERE, "..", "Step7_docs", "outputs_step7"))


class NotRun(RuntimeError):
    """The gate could not be executed. Distinct from the gate failing."""


def xgrammar_version(xgr):
    """The installed version, by whatever route this build exposes it.

    `xgr.__version__` is absent in the build on Speed and printed "unknown",
    which is not good enough for a provenance field: the whole point of
    recording it is that the next API change is traceable to a version.
    """
    v = getattr(xgr, "__version__", None)
    if v:
        return v
    try:
        import importlib.metadata as md
        return md.version("xgrammar")
    except Exception as e:
        return "unknown (%s)" % type(e).__name__


def describe_api(xgr):
    """Print what the installed XGrammar actually offers.

    Printed unconditionally, not only on failure. The version that made a run
    possible is part of the run's provenance, and the next person to hit an API
    change needs the surface that was present, not the one I assumed.
    """
    print("xgrammar version : %s" % xgrammar_version(xgr))
    print("xgrammar top-level: %s" % ", ".join(sorted(n for n in dir(xgr)
                                                      if not n.startswith("__"))))
    try:
        t = importlib.import_module("xgrammar.testing")
        print("xgrammar.testing  : %s" % ", ".join(sorted(n for n in dir(t)
                                                          if not n.startswith("__"))))
    except Exception as e:
        print("xgrammar.testing  : unavailable (%s: %s)" % (type(e).__name__, e))


def probe_pair(alph):
    """One string the language contains and one it does not, both CONFIRMED.

    🔴 Built from the alphabets, never typed out. The first version of this
    function carried a hand-written record whose `ACT` code `110` is not in the
    shipped list, so both probes were invalid and the "usable recogniser" test
    below would have been decided by two rejections -- passing any entry point
    that answers False to everything. Derived, then checked.
    """
    good = ebnf._valid_record(__import__("random").Random(7), alph)
    p, chunks = ebnf._split_episodes(good)
    f = chunks[0].split(",")
    f[0] = str(int(f[0]) + 5)            # no longer a multiple of 10
    chunks[0] = ",".join(f)
    bad = ebnf._rejoin(p, chunks)

    pol = grammar.TransitionPolicy.PERMISSIVE
    ok_g, why_g = grammar.validate_record(good, alph, pol)
    ok_b, _why_b = grammar.validate_record(bad, alph, pol)
    if not ok_g or ok_b:
        raise NotRun("the probe pair is not a probe pair: oracle says good=%s (%s), bad=%s"
                     % (ok_g, why_g, ok_b))
    return good, bad


def get_matcher(xgr, g, alph):
    """Return (name, fn) where fn(str) -> bool, or raise NotRun.

    Tried in order of directness. Each candidate is EXERCISED on a string the
    grammar must accept and one it must reject before being returned -- an entry
    point that exists but always answers True (or always False) would otherwise
    turn `G7.10` into a tautology, which is the exact failure the gate exists to
    prevent.
    """
    good, bad = probe_pair(alph)
    candidates = []

    # The names are version-dependent and were NOT guessed correctly the first
    # time: run 1286175 asked for `_match_grammar_with_string`, found nothing,
    # fell through to a GrammarMatcher built on an UNCOMPILED grammar, and exited
    # NOT RUN. `_is_grammar_accept_string` is the name this build actually ships.
    # The list is ordered, every entry is probed, and an unknown build still ends
    # in NOT RUN rather than in a fabricated verdict.
    try:
        t = importlib.import_module("xgrammar.testing")
        for nm in ("_is_grammar_accept_string", "is_grammar_accept_string",
                   "_match_grammar_with_string", "match_grammar_with_string"):
            fn = getattr(t, nm, None)
            if fn is not None:
                candidates.append(("xgrammar.testing.%s" % nm,
                                   lambda s, _f=fn: bool(_f(g, s))))
        mk = getattr(t, "_get_matcher_from_grammar", None)
        if mk is not None:
            def _by_testing_matcher(s, _mk=mk):
                m = _mk(g)
                if not m.accept_string(s):
                    return False
                return bool(m.is_terminated())
            candidates.append(("xgrammar.testing._get_matcher_from_grammar", _by_testing_matcher))
    except Exception:
        pass

    if not candidates:
        raise NotRun("no string-acceptance entry point in this XGrammar build")

    errors = []
    for name, fn in candidates:
        try:
            if fn(good) and not fn(bad):
                return name, fn
            errors.append("%s answered good=%s bad=%s -- not a usable recogniser"
                          % (name, fn(good), fn(bad)))
        except Exception as e:
            errors.append("%s raised %s: %s" % (name, type(e).__name__, e))
    raise NotRun("; ".join(errors))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260822)
    ap.add_argument("--step2", default=DEFAULT_STEP2)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)

    print("=" * 78)
    print("G7.10  oracle agreement -- %d strings, seed %d" % (a.n, a.seed))
    print("=" * 78)

    alph = grammar.build_alphabets(a.step2)
    print("alphabets: ACT %d (=%d shipped + 000) | ACT2 %d | LOC %d | COP %d"
          % (len(alph["act"]), alph["act_n_shipped"], len(alph["act2"]),
             len(alph["loc"]), len(alph["cop"])))

    text = ebnf.build_ebnf(alph)
    os.makedirs(a.out, exist_ok=True)
    ebnf_path = os.path.join(a.out, "step7_grammar.ebnf")
    with open(ebnf_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("EBNF written: %s (%d chars)" % (ebnf_path, len(text)))

    import xgrammar as xgr
    describe_api(xgr)

    t0 = time.time()
    g = xgr.Grammar.from_ebnf(text)
    compile_s = time.time() - t0
    print("grammar compiled in %.2f s" % compile_s)

    name, accepts = get_matcher(xgr, g, alph)
    print("string-acceptance entry point: %s" % name)

    sample = ebnf.sample_strings(alph, n=a.n, seed=a.seed)
    pol = grammar.TransitionPolicy.PERMISSIVE
    print("policy: %s (D-S7-2 (a), author 2026-08-20)" % pol)

    per_label = {}
    disagreements = []
    n_oracle_ok = 0
    t0 = time.time()
    for label, s in sample:
        ok_oracle, why = grammar.validate_record(s, alph, pol)
        try:
            ok_xgr = accepts(s)
        except Exception as e:
            ok_xgr = "ERROR:%s" % type(e).__name__
        n_oracle_ok += 1 if ok_oracle else 0
        d = per_label.setdefault(label, {"n": 0, "oracle_ok": 0, "xgr_ok": 0, "disagree": 0})
        d["n"] += 1
        d["oracle_ok"] += 1 if ok_oracle else 0
        d["xgr_ok"] += 1 if ok_xgr is True else 0
        if ok_xgr is not ok_oracle:
            d["disagree"] += 1
            if len(disagreements) < 20:
                disagreements.append({"label": label, "oracle": ok_oracle,
                                      "xgrammar": ok_xgr, "oracle_reason": why,
                                      "text": s[:240]})
    match_s = time.time() - t0

    print("\nmatched %d strings in %.2f s (%.0f strings/s)"
          % (len(sample), match_s, len(sample) / max(match_s, 1e-9)))
    print("\n%-20s %6s %10s %8s %9s" % ("label", "n", "oracle ok", "xgr ok", "disagree"))
    for lab in sorted(per_label):
        d = per_label[lab]
        print("%-20s %6d %10d %8d %9d" % (lab, d["n"], d["oracle_ok"], d["xgr_ok"],
                                          d["disagree"]))

    n_disagree = sum(d["disagree"] for d in per_label.values())
    n_reject = len(sample) - n_oracle_ok

    # --- V7.e: the sample must not be vacuous -----------------------------
    vacuous_reasons = []
    if n_oracle_ok == 0:
        vacuous_reasons.append("the oracle accepted NOTHING -- agreement would be trivial")
    if n_reject == 0:
        vacuous_reasons.append("the oracle rejected NOTHING -- no malformed string was tested")
    all_accepted = sorted(l for l, d in per_label.items()
                          if l != "valid" and d["oracle_ok"] == d["n"])
    if all_accepted:
        vacuous_reasons.append("mutator classes the oracle never rejected: %s"
                               % ", ".join(all_accepted))
    failed_mut = sorted(l for l in per_label if l.startswith("MUTATOR_FAILED"))
    if failed_mut:
        vacuous_reasons.append("mutators that could not fire: %s" % ", ".join(failed_mut))

    print("\noracle accepted %d, rejected %d of %d" % (n_oracle_ok, n_reject, len(sample)))
    if disagreements:
        print("\nfirst %d disagreements:" % len(disagreements))
        for d in disagreements:
            print("  [%s] oracle=%s xgrammar=%s  %s"
                  % (d["label"], d["oracle"], d["xgrammar"], d["oracle_reason"][:60]))
            print("      %s" % d["text"][:160])

    verdict = "PASS" if (n_disagree == 0 and not vacuous_reasons) else "FAIL"
    print("\n" + "=" * 78)
    print("G7.10: %s -- %d disagreements on %d strings" % (verdict, n_disagree, len(sample)))
    for r in vacuous_reasons:
        print("  🔴 VACUITY: %s" % r)
    print("=" * 78)

    out = {
        "gate": "G7.10",
        "verdict": verdict,
        "n_strings": len(sample),
        "seed": a.seed,
        "n_disagreements": n_disagree,
        "n_oracle_accepted": n_oracle_ok,
        "n_oracle_rejected": n_reject,
        "vacuity_reasons": vacuous_reasons,
        "policy": pol,
        "policy_ref": "D-S7-2 (a), author 2026-08-20",
        "xgrammar_version": xgrammar_version(xgr),
        "matcher_entry_point": name,
        "compile_seconds": round(compile_s, 3),
        "match_seconds": round(match_s, 3),
        "ebnf_chars": len(text),
        "alphabet_sizes": {"act": len(alph["act"]), "act2": len(alph["act2"]),
                           "loc": len(alph["loc"]), "cop": len(alph["cop"])},
        "per_label": per_label,
        "disagreement_examples": disagreements,
    }
    p = os.path.join(a.out, "g710_oracle_agreement.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print("written: %s" % p)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotRun as e:
        print("\n" + "=" * 78)
        print("G7.10: NOT RUN -- %s" % e)
        print("NOT RUN IS NOT A PASS. The gate has no verdict.")
        print("=" * 78)
        sys.exit(2)
