# -*- coding: utf-8 -*-
"""Self-test for `4thJ_step7_ebnf.py` -- the grammar side of `G7.10`.

Runs anywhere, needs no GPU and no XGrammar. It checks the EMITTED TEXT and the
SAMPLER, which are the two things that can be wrong before a back-end is ever
involved. The oracle-versus-XGrammar comparison itself is `4thJ_step7_g710.py`.

  usage: py -3 4thJ_step7_ebnf_selftest.py [step2_dir]
"""

import ast
import importlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

ebnf = importlib.import_module("4thJ_step7_ebnf")
grammar = importlib.import_module("4thJ_step7_grammar")

DEFAULT_STEP2 = os.path.normpath(
    os.path.join(_HERE, "..", "Step2_docs", "outputs_step2"))

_PASS = []
_FAIL = []


def check(name, cond, detail=""):
    (_PASS if cond else _FAIL).append(name)
    print("%-4s %s%s" % ("ok" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


def raises(name, fn, exc=Exception):
    try:
        fn()
    except exc as e:
        check(name, True, "%s: %s" % (type(e).__name__, str(e)[:70]))
        return
    check(name, False, "did not raise")


def main(step2_dir):
    alph = grammar.build_alphabets(step2_dir)
    text = ebnf.build_ebnf(alph)
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    rules = {}
    for l in lines:
        head, body = l.split(" ::= ", 1)
        if head in rules:
            check("rule %s defined once" % head, False, "defined twice")
        rules[head] = body

    print("\n--- 1. the record ---")
    check("root exists", "root" in rules)
    check("root has %d PF fields" % ebnf.N_PREFIX_FIELDS,
          rules["root"].count("PF ") + rules["root"].count("PF\"") == 0 or
          len(re.findall(r"\bPF\b", rules["root"])) == ebnf.N_PREFIX_FIELDS,
          "found %d" % len(re.findall(r"\bPF\b", rules["root"])))
    check("root ends at <eor>", rules["root"].rstrip().endswith('"<eor>"'))
    check("root enters the tally at S0", " S0 " in rules["root"])
    check("PFCHAR class carries + and -", "+" in rules["PFCHAR"] and "-" in rules["PFCHAR"],
          rules["PFCHAR"])
    check("prefix sampler charset matches the class",
          all(c.isalnum() or c in "_+-" for c in ebnf.PREFIX_CHARS))

    print("\n--- 2. alphabets, read live ---")
    n_act = rules["ACT"].count('"') // 2
    n_act2 = rules["ACT2"].count('"') // 2
    n_loc = rules["LOC"].count('"') // 2
    n_cop = rules["COP"].count('"') // 2
    check("ACT literal count == alphabet", n_act == len(alph["act"]), "%d" % n_act)
    check("ACT is 158 shipped + 000 = 159", n_act == alph["act_n_shipped"] + 1 == 159,
          "shipped %d" % alph["act_n_shipped"])
    check('ACT contains "000" (FINDING 43)', '"000"' in rules["ACT"])
    check("ACT2 literal count == alphabet", n_act2 == len(alph["act2"]), "%d" % n_act2)
    check("LOC is exactly 5", n_loc == 5 == len(grammar.LOC_ALPHABET))
    check("COP is 0..64 = 65", n_cop == 65 == grammar.COP_MAX - grammar.COP_MIN + 1)
    check('LOC has no "workplace" class', '"workplace"' not in rules["LOC"])

    print("\n--- 3. the episode tail ---")
    check("TAIL has two alternatives (ACT2 present / empty)",
          rules["TAIL"].count("|") == 1, rules["TAIL"])
    check("TAIL empty-ACT2 branch is written as ,,", '",," LOC' in rules["TAIL"])

    print("\n--- 4. the 145-state tally, counted not asserted ---")
    e_rules = sorted(int(k[1:]) for k in rules if re.fullmatch(r"E\d+", k))
    s_rules = sorted(int(k[1:]) for k in rules if re.fullmatch(r"S\d+", k))
    check("144 duration rules E1..E144", e_rules == list(range(1, 145)), "%d rules" % len(e_rules))
    check("145 tally states, S0..S143 defined", s_rules == list(range(0, 144)),
          "%d rules" % len(s_rules))
    check("S144 is NEVER defined (the day ends on a bare E)",
          "S144" not in rules and "S144" not in text)
    check("E144 spells 1440", rules["E144"].startswith('"1440"'))
    check("E1 spells 10", rules["E1"].startswith('"10"'))
    check("S0 has 144 alternatives", rules["S0"].count("|") + 1 == 144)
    check("S143 has exactly one, E1", rules["S143"].strip() == "E1")
    check("S142 is E1 S143 | E2", rules["S142"].strip() == "E1 S143 | E2")

    refs_ok = True
    total_alts = 0
    for s in range(0, 144):
        alts = [a.strip() for a in rules["S%d" % s].split("|")]
        total_alts += len(alts)
        for a in alts:
            parts = a.split()
            k = int(parts[0][1:])
            if len(parts) == 1:
                if s + k != 144:
                    refs_ok = False
            else:
                if int(parts[1][1:]) != s + k:
                    refs_ok = False
    check("every alternative advances the tally by exactly its duration", refs_ok)
    check("10,440 transitions in total", total_alts == 10440, "%d" % total_alts)

    print("\n--- 5. independence from the oracle (V5.d / V6.b) ---")
    src = open(os.path.join(_HERE, "4thJ_step7_ebnf.py"), encoding="utf-8").read()
    # 🔴 Read the SYNTAX TREE, not the text. Two earlier shapes of this check were
    # both wrong: `"validate_record(" not in text` let a perturbation that BOUND
    # the oracle without calling it walk past at 42 ok / 0 FAILED, and the
    # substring fix that caught it then failed on a COMMENT that merely names the
    # function. Identifiers are the thing that matters; prose about them is not.
    tree = ast.parse(src)
    names = set()
    pulled = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
            if isinstance(node.value, ast.Name) and node.value.id == "_grammar":
                pulled.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    check("no identifier named validate_record anywhere in the module",
          "validate_record" not in names)
    check("no identifier named tally_step anywhere in the module",
          "tally_step" not in names)
    # The positive form: enumerate everything taken off the grammar module and
    # require it to be a CONSTANT. `build_alphabets` is shared deliberately -- it
    # is the constraint definition both sides compile from -- but it is called by
    # the caller, never reached through this module.
    ALLOWED = {"DAY_MINUTES", "SLOT_MINUTES", "N_TALLY_STATES", "COP_MIN", "COP_MAX",
               "LOC_ALPHABET", "N_PREFIX_FIELDS"}
    check("only constants are pulled from the grammar module",
          pulled <= ALLOWED, "pulled %s" % sorted(pulled))
    check("the shared definition build_alphabets is documented as shared",
          "build_alphabets" in src)

    print("\n--- 6. negative codes are computed, not guessed (V4.f) ---")
    bad_act = ebnf._out_of_alphabet(alph["act"], 3)
    bad_act2 = ebnf._out_of_alphabet(alph["act2"], 2)
    check("bad ACT is provably absent", bad_act not in alph["act"], bad_act)
    check("bad ACT2 is provably absent", bad_act2 not in alph["act2"], bad_act2)
    check("999 is NOT used as the bad ACT", bad_act != "999" or "999" not in alph["act"],
          "999 in alphabet: %s" % ("999" in alph["act"]))
    raises("a full alphabet yields no negative case, and says so",
           lambda: ebnf._out_of_alphabet({str(i).zfill(2) for i in range(100)}, 2),
           ebnf.EbnfError)

    print("\n--- 7. the sample set ---")
    s1 = ebnf.sample_strings(alph, n=600, seed=1)
    s2 = ebnf.sample_strings(alph, n=600, seed=1)
    s3 = ebnf.sample_strings(alph, n=600, seed=2)
    check("reproducible for a fixed seed", s1 == s2)
    check("a different seed gives a different set", s1 != s3)
    check("size is what was asked for", len(s1) == 600)
    labels = set(l for l, _ in s1)
    check("no mutator failed to fire", not any(l.startswith("MUTATOR_FAILED") for l in labels),
          ",".join(sorted(l for l in labels if l.startswith("MUTATOR_FAILED"))) or "none")
    expected = set(n for n, _ in ebnf._mutators(alph)) | {"valid"}
    check("every mutator class is represented", labels == expected,
          "missing %s" % sorted(expected - labels))

    print("\n--- 8. the sample is not vacuous (V7.e) ---")
    pol = grammar.TransitionPolicy.PERMISSIVE
    acc = {}
    for lab, t in s1:
        ok, _why = grammar.validate_record(t, alph, pol)
        acc.setdefault(lab, []).append(ok)
    check("every string labelled valid IS accepted by the oracle",
          all(acc.get("valid", [])), "%d/%d" % (sum(acc.get("valid", [])), len(acc.get("valid", []))))
    n_rej = sum(1 for lab, t in s1 if not grammar.validate_record(t, alph, pol)[0])
    check("the oracle REJECTS a substantial share", n_rej >= 200, "%d of 600" % n_rej)
    vacuous = sorted(l for l in labels
                     if l != "valid" and acc.get(l) and all(acc[l]))
    check("no mutator class is entirely accepted (a vacuous negative)",
          not vacuous, ",".join(vacuous) or "none")

    print("\n--- 9. the emitted text is stable ---")
    check("build_ebnf is deterministic", ebnf.build_ebnf(alph) == text)
    check("text is non-trivial", len(text) > 50000, "%d chars, %d rules" % (len(text), len(rules)))

    print("\n%d ok, %d FAILED" % (len(_PASS), len(_FAIL)))
    if _FAIL:
        print("failed: " + ", ".join(_FAIL))
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_STEP2))
