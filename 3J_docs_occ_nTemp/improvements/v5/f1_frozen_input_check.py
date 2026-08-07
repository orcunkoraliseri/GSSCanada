#!/usr/bin/env python3
"""V5-F1 -- fail when a round's code reads an output directory that is not the frozen one.

WHY THIS EXISTS. On 2026-08-06 four consecutive v4 tasks were computed from
`Leg3_4-split/Step9_docs/outputs_step9/` (2026-07-31) instead of the frozen
`outputs_step9_deliverable/` (2026-08-06 00:05). Office and retail differ by ~0.1 % between
the two, so nothing looked wrong; the hotel channel INVERTS (28 below the floor vs 28 above the
ceiling). On that basis a correct master document was "corrected" in three places.

🔴 The reason no existing check caught it: BOTH directories report "28 of 56". Every check that
compares counts or band values passes straight through a failure-direction inversion. This one does
not look at numbers at all -- it looks at which file was opened.

THE REGISTRY IS NOT HARD-CODED. The frozen directories are read from the freeze document
(`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`), and the superseded siblings are whatever else
exists next to them on disk. If a later round freezes a different arm, this check follows it.

FOUR CHECKS:
  C1  no script in the round names a superseded sibling of a frozen directory.
  C2  no script assembles one from pieces (`os.path.join(..., "outputs_step9", ...)`) -- C1 alone is
      dodged by string concatenation, which is exactly how a path gets built in real code.
  C3  the registry is non-empty and every frozen directory it names exists on disk. A check whose
      registry silently came up empty passes everything.
  C4  every frozen directory has at least one superseded sibling. Without one, C1 CANNOT fail, and a
      check that cannot fail is not a check -- it is a comment.

A line may opt out with a trailing `# FROZEN-INPUT-OK: <reason>`; the reason is required.

    python f1_frozen_input_check.py [--round v4] [--falsify]
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMPROVEMENTS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(IMPROVEMENTS, ".."))
FREEZE_DOC = os.path.join(IMPROVEMENTS, "v2", "V2-G1_FROZEN_DELIVERABLE.md")
FIXTURES = os.path.join(HERE, "fixtures")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# a repo-relative directory path in a markdown table cell, e.g.
# | Step-9 scorecard + report + figures | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/` |
PATH_CELL = re.compile(r"`([A-Za-z0-9_./-]+/)`")
OPT_OUT = re.compile(r"#\s*FROZEN-INPUT-OK:\s*\S")

_N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %-3s %s" % ("PASS" if ok else "FAIL", tag, detail))


def registry():
    """(frozen_dirs, superseded_siblings) read from the freeze document + disk."""
    with io.open(FREEZE_DOC, encoding="utf-8") as fh:
        text = fh.read()
    frozen = []
    for m in PATH_CELL.finditer(text):
        rel = m.group(1).rstrip("/")
        if "deliverable" not in rel.rsplit("/", 1)[-1]:
            continue
        if rel not in frozen:
            frozen.append(rel)
    siblings = {}
    for rel in frozen:
        parent = os.path.join(ROOT, os.path.dirname(rel))
        leaf = os.path.basename(rel)
        sibs = []
        if os.path.isdir(parent):
            for name in sorted(os.listdir(parent)):
                if name == leaf or not os.path.isdir(os.path.join(parent, name)):
                    continue
                # a sibling is superseded only if the frozen name contains it:
                # outputs_step9_deliverable supersedes outputs_step9; agg_deliverable supersedes agg
                if leaf.startswith(name):
                    sibs.append(name)
        siblings[rel] = sibs
    return frozen, siblings


def scripts(round_dir):
    out = []
    for name in sorted(os.listdir(round_dir)):
        if name.endswith(".py") and not name.startswith("f1_"):
            out.append(os.path.join(round_dir, name))
    return out


def scan(paths, siblings):
    """(c1_hits, c2_hits) -- (file, lineno, line, offending name)."""
    all_sibs = sorted({s for v in siblings.values() for s in v})
    # C1: the sibling directory named inside a path-looking string
    c1_pat = re.compile(r"[\"'/]((?:%s))(?:[\"'/])" % "|".join(re.escape(s) for s in all_sibs)) \
        if all_sibs else None
    # C2: the sibling name as a bare join component
    c2_pat = re.compile(r"join\([^)]*[\"'](%s)[\"']" % "|".join(re.escape(s) for s in all_sibs)) \
        if all_sibs else None
    c1, c2 = [], []
    for p in paths:
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                if OPT_OUT.search(line):
                    continue
                if c2_pat is not None:
                    m = c2_pat.search(line)
                    if m:
                        c2.append((p, i, line.strip(), m.group(1)))
                        continue
                if c1_pat is not None:
                    m = c1_pat.search(line)
                    if m:
                        c1.append((p, i, line.strip(), m.group(1)))
    return c1, c2


def main(round_name, falsify):
    frozen, siblings = registry()
    print("V5-F1 -- frozen-input check   (round: %s%s)"
          % (round_name, "   FALSIFY MODE" if falsify else ""))
    print("  registry, read from %s:" % os.path.relpath(FREEZE_DOC, ROOT).replace("\\", "/"))
    for rel in frozen:
        print("    frozen  %s   superseded siblings: %s"
              % (rel, ", ".join(siblings[rel]) or "(none)"))

    target = FIXTURES if falsify else os.path.join(IMPROVEMENTS, round_name)
    paths = scripts(target)
    print("  scanning %d script(s) in %s\n" % (len(paths), os.path.relpath(target, ROOT).replace("\\", "/")))

    c1, c2 = scan(paths, siblings)
    rec("C1", not c1, "no script names a superseded sibling"
        if not c1 else "%d line(s) read a superseded directory:" % len(c1))
    for p, i, line, name in c1:
        print("        %s:%d  (%s)  %s" % (os.path.basename(p), i, name, line[:100]))

    rec("C2", not c2, "no script assembles one from join() pieces"
        if not c2 else "%d line(s) build a superseded path from pieces:" % len(c2))
    for p, i, line, name in c2:
        print("        %s:%d  (%s)  %s" % (os.path.basename(p), i, name, line[:100]))

    missing = [r for r in frozen if not os.path.isdir(os.path.join(ROOT, r))]
    rec("C3", bool(frozen) and not missing,
        "%d frozen directory(ies), all present on disk" % len(frozen) if frozen and not missing
        else "registry empty or missing on disk: %s" % (missing or "EMPTY"))

    barren = [r for r in frozen if not siblings[r]]
    rec("C4", not barren,
        "every frozen directory has a superseded sibling, so C1 can fail"
        if not barren else "no sibling for %s -- C1 is vacuous there" % ", ".join(barren))

    print("\n  %d PASS / %d FAIL" % (_N["pass"], _N["fail"]))
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="v4")
    ap.add_argument("--falsify", action="store_true",
                    help="scan fixtures/ instead -- the v4 scripts as they were first written")
    a = ap.parse_args()
    sys.exit(main(a.round, a.falsify))
