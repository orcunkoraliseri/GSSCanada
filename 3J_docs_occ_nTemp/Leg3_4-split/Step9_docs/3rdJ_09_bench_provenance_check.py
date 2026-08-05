#!/usr/bin/env python3
"""3J Leg-3 Step 9 -- V2-D4 provenance check on the scorer's ``BENCH`` table.

**What this checks, and what it deliberately does not.**

It checks that every ``src=`` string in ``3rdJ_09_activityDrivenLoads_4split.py``'s ``BENCH`` names a
document path that **actually resolves from the repo root**, and it prints the band values so a
reviewer can diff them by eye against the master docs. Before V2-D4 the office band's ``src=`` read
``Step8_docs/deepResearch/...As-Modelled Bands.md``, which resolves to nothing: there is no
``deepResearch/`` under ``Leg3_4-split/Step8_docs/``. The document lives in the frozen Leg-2 tree.
A provenance string that does not resolve is the same defect as no provenance at all; it only takes
longer to discover.

It does **not** check that the band *values* are right, and it must never be read as if it did.
That is a WP-B decision (V2-B2 / V2-C6) resting on external evidence that is still out. This script
can pass on a band whose floor is wrong. Stated here so nobody later cites a green run from this
file as band validation -- that would be a vacuous gate of the "explanation that cannot fail" kind.

The paths are read by AST rather than by importing the scorer, so the check has no side effects and
does not need the scorer's runtime dependencies.

Usage (from the repo root, so relative paths resolve):
    py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09_bench_provenance_check.py

Exit code 0 = every ``src=`` path resolves. Exit code 1 = at least one is broken.
"""
import ast
import os
import re
import sys

SCORER = os.path.join("3J_docs_occ_nTemp", "Leg3_4-split", "Step9_docs",
                      "3rdJ_09_activityDrivenLoads_4split.py")
# Any src= that quotes a repo path must start here. Channels with no as-modelled band (residential)
# legitimately carry no path and are reported as such rather than silently skipped.
PATH_RE = re.compile(r"(3J_docs_occ_nTemp/.+?\.md)")


def load_bench(path):
    """Return the BENCH dict without importing the scorer.

    ``ast.literal_eval`` cannot be used: the entries are ``dict(...)`` calls, not dict literals.
    So the single BENCH assignment node is compiled and executed in an empty namespace.
    """
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    nodes = [n for n in tree.body
             if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "BENCH"]
    if len(nodes) != 1:
        raise SystemExit("REFUSING: expected exactly 1 top-level BENCH assignment in %s, found %d"
                         % (path, len(nodes)))
    ns = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<bench>", "exec"), ns)
    return ns["BENCH"]


def main():
    if not os.path.isfile(SCORER):
        raise SystemExit("REFUSING: run this from the repo root -- %s not found from %s"
                         % (SCORER, os.getcwd()))
    bench = load_bench(SCORER)

    print("### BENCH src= path resolution")
    broken = []
    for ch, d in bench.items():
        src = d.get("src", "")
        m = PATH_RE.search(src)
        if not m:
            # Only legitimate when the channel has no as-modelled band at all.
            if d.get("lo") is None and d.get("hi") is None:
                print("  %-12s no band, no path required : %s" % (ch, src))
            else:
                print("  %-12s NO PATH IN src= (band exists, provenance does not) : %s" % (ch, src))
                broken.append(ch)
            continue
        fp = m.group(1)
        if os.path.isfile(fp):
            print("  %-12s OK     %s" % (ch, fp))
        else:
            print("  %-12s BROKEN %s" % (ch, fp))
            broken.append(ch)

    print("\n### band values (printed for eye-diff against the master docs; NOT validated here)")
    for ch, d in bench.items():
        print("  %-12s lo=%-7s central=%-7s hi=%-7s" % (ch, d["lo"], d["central"], d["hi"]))

    if broken:
        print("\nFAIL: %d broken provenance entr%s: %s"
              % (len(broken), "y" if len(broken) == 1 else "ies", ", ".join(broken)))
        return 1
    print("\nPASS: every band with a value names a document that resolves.")
    print("      This says nothing about whether the values themselves are correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
