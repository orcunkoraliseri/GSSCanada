#!/usr/bin/env python3
"""V2-D4 -- three-way agreement check: scorer BENCH == master-doc bands == decision record.

Q7 asked whether every band written in the documents equals the band in the scorer. Until now
nobody could answer it, because the answer required reading two files and trusting the reader.
This script answers it mechanically.

WHAT IT CHECKS, per banded channel:
  * as-modelled triple (lo, central, hi)   code vs doc
  * empirical INFO triple (lo, central, hi) code vs doc
  * the decision RULE ("all_cells" / "median")  code vs doc

WHAT IT CANNOT DO, stated here so it is never miscited (the sibling
3rdJ_09_bench_provenance_check.py carries the same disclaimer for the same reason):

  * It CANNOT tell you a band is CORRECT. It tells you the code and the docs tell the same story.
    Two documents agreeing on a wrong number is exactly the state this project has been in twice.
  * It CANNOT check a channel nobody wrote down -- so a channel present in the code and ABSENT
    from the doc is a HARD FAILURE here, never a skip. That is not a defensive nicety: until
    2026-08-05 the OFFICE band, the one blocking gate whose floor is contested, existed only in
    the scorer. A checker that skipped missing channels would have passed that state and reported
    "all bands agree", which is the vacuous-gate pattern this project catalogues.

Read-only. Parses BENCH by AST (no import, no pandas, no side effects) -- the entries are
dict(...) CALLS, so ast.literal_eval will not take them; each keyword is walked instead.
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.join(HERE, "3rdJ_09_activityDrivenLoads_4split.py")
DOC = os.path.abspath(os.path.join(HERE, "..", "3rdJ_00_4split_Occupancy_Pipeline.md"))

BANDED = ["office", "retail", "hotel"]
# The doc writes rules in prose-friendly form; the code uses identifiers. One mapping, in one
# place, so a rename cannot silently make the two sides "agree" by failing to compare.
RULE_DOC_TO_CODE = {"all-cells": "all_cells", "median-in-band": "median"}

TRIPLE = re.compile(r"low\s+([\d.]+),\s*central\s+([\d.]+),\s*high\s+([\d.]+)")
RULE = re.compile(r"`rule:\s*([a-z-]+)`")

# 🔴 An ordering trap this check found on its first run, recorded so nobody "fixes" it by
# reordering the wrong side. The scorer's empirical tuple is info=(CENTRAL, lo, hi) -- central
# FIRST -- which is why it is read as b["info"][1], b["info"][2] for the bounds and b["info"][0]
# for the centre. Every other triple in this project, in code and in prose, is (lo, central, hi).
# Comparing the two tuples position-by-position therefore reports a mismatch on bands that are
# in fact identical. The tuple order is NOT changed here: it is load-bearing at
# 3rdJ_09_activityDrivenLoads_4split.py (info_lo/info_hi and the S9-EUI INFO strings), and
# silently re-ordering it while this check "confirmed" the result would be the worse outcome.


def info_as_lo_central_hi(info):
    """Normalise the scorer's central-first empirical tuple to (lo, central, hi)."""
    central, lo, hi = info
    return (lo, central, hi)


def read_bench(path):
    """Return {channel: dict(lo, central, hi, rule, info)} straight from the scorer's source."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and
                any(getattr(t, "id", None) == "BENCH" for t in node.targets)):
            continue
        out = {}
        for k, v in zip(node.value.keys, node.value.values):
            entry = {}
            for kw in v.keywords:
                try:
                    entry[kw.arg] = ast.literal_eval(kw.value)
                except ValueError:
                    entry[kw.arg] = None  # a joined string (src=) -- not compared here
            out[k.value] = entry
        return out
    raise SystemExit("[FAIL] no BENCH assignment found in " + SCORER)


def read_doc_bands(path):
    """Return {channel: dict(asmodelled, info, rule)} from the master doc's band bullets."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    out = {}
    for c in BANDED:
        marker = "**%s EUI Bands" % c.capitalize()
        hits = [ln for ln in lines if marker in ln]
        if not hits:
            out[c] = None          # absent -> caller FAILS. Never a skip. See module docstring.
            continue
        if len(hits) > 1:
            raise SystemExit("[FAIL] %s: %d band bullets in the doc; ambiguous provenance is a "
                             "defect, not a tie to break" % (c, len(hits)))
        triples = TRIPLE.findall(hits[0])
        if len(triples) != 2:
            raise SystemExit("[FAIL] %s: expected 2 triples (as-modelled then INFO), found %d"
                             % (c, len(triples)))
        rule = RULE.search(hits[0])
        out[c] = dict(asmodelled=tuple(float(x) for x in triples[0]),
                      info=tuple(float(x) for x in triples[1]),
                      rule=RULE_DOC_TO_CODE.get(rule.group(1)) if rule else None,
                      rule_raw=rule.group(1) if rule else None)
    return out


def main():
    bench, doc = read_bench(SCORER), read_doc_bands(DOC)
    bad = []
    print("V2-D4 three-way agreement: scorer BENCH vs %s\n" % os.path.basename(DOC))
    print("  %-12s %-22s %-22s %s" % ("channel", "code (lo/central/hi)", "doc (lo/central/hi)", "rule"))
    for c in BANDED:
        b, d = bench.get(c), doc.get(c)
        if b is None:
            bad.append("%s: absent from BENCH" % c)
            continue
        code_t = (b["lo"], b["central"], b["hi"])
        if d is None:
            print("  %-12s %-22s %-22s %s" % (c, "%g/%g/%g" % code_t, "*** NOT IN DOC ***", "-"))
            bad.append("%s: banded in the scorer, written NOWHERE in the master doc -- the band "
                       "cannot be checked by a reader" % c)
            continue
        doc_t = d["asmodelled"]
        code_rule = b.get("rule")
        code_info = info_as_lo_central_hi(b["info"])
        ok = (code_t == doc_t and code_info == d["info"] and code_rule == d["rule"])
        print("  %-12s %-22s %-22s %s%s" % (
            c, "%g/%g/%g" % code_t, "%g/%g/%g" % doc_t,
            "%s vs %s" % (code_rule, d["rule_raw"]), "" if ok else "   <-- MISMATCH"))
        if code_t != doc_t:
            bad.append("%s as-modelled band: code %s vs doc %s" % (c, code_t, doc_t))
        if code_info != d["info"]:
            bad.append("%s INFO band: code %s vs doc %s (both normalised to lo/central/hi)"
                       % (c, code_info, d["info"]))
        if code_rule != d["rule"]:
            bad.append("%s rule: code %r vs doc %r" % (c, code_rule, d["rule_raw"]))

    # Residential is asserted, not skipped: "no band" is a STATE to verify, not an absence to
    # ignore. If the scorer ever gains a residential band, the doc must gain the bullet too.
    res = bench.get("residential", {})
    if res.get("lo") is None:
        print("\n  residential  no as-modelled band in code, no doc bullet required -- consistent")
    else:
        bad.append("residential gained a band in the scorer (lo=%s) with no doc bullet"
                   % res.get("lo"))

    if bad:
        print("\n[FAIL] %d disagreement(s):" % len(bad))
        for b in bad:
            print("   - " + b)
        print("\nThis check compares two descriptions of the same numbers. It does NOT say the "
              "numbers are right.")
        return 1
    print("\n[PASS] code and doc agree on every band value, every INFO band and every rule.")
    print("REMINDER: agreement is not correctness. This gate cannot fail on a band that is "
          "wrong in both places.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
