#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5-F4 -- manuscript prose-rule check.

Run:  py -3 writing/implementation/f4_prose_rules_check.py
      py -3 writing/implementation/f4_prose_rules_check.py --falsify

Written 2026-08-06 during the 3J build, after a `grep -P` for em dashes returned
exit code 2 (unsupported flag) and was read as "clean". A check that fails silently
is worse than no check, so this one refuses to pass vacuously and ships a falsifier.

SCOPE. Manuscript-facing text only: writing/chapters, writing/tables (incl. SI),
writing/figures (the .md generation prompts). Deliberately NOT scanned:
writing/implementation (build docs, this file, the brief) and any archive/ directory,
whose job is to preserve predecessors verbatim, dashes and all.

C1  no em dash (U+2014) or en dash (U+2013) in any scanned file
C2  the 2J phrase "four building archetypes" appears only inside a negation
C3  no scanned file cites the superseded outputs_step9/ as a source
C4  every scanned file names at least one source (a path, or a "Sources" block)
C5  vacuity guard: the scan actually saw files, and C1 is demonstrably falsifiable
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../writing
SCAN = ["chapters", "tables", "figures"]
EM, EN = "—", "–"

# "four building archetypes" is legitimate inside a sentence that rejects it.
NEG = re.compile(r"(not|never|rather than|instead of|is wrong|avoid|no longer)[^.\n]{0,80}four building archetypes", re.I)

# outputs_step9/ is a legitimate mention when the text is warning about it.
SUPERSEDED_OK = re.compile(
    r"(supersede|superseded|sibling|not used|never|must not|inverts|retained|do not|cannot be deleted|"
    r"predates|2026-07-31|V4-A1|wrong|hazard|collision|nowhere else)", re.I)


def files():
    out = []
    for sub in SCAN:
        base = os.path.join(ROOT, sub)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != "archive"]
            for f in sorted(filenames):
                if f.endswith(".md"):
                    out.append(os.path.join(dirpath, f))
    return out


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def run(extra_text=None, orphan_number=None):
    paths = files()
    docs = []
    for p in paths:
        with io.open(p, encoding="utf-8") as fh:
            t = fh.read()
        # falsifier for C6: plant a number in the front matter that exists nowhere else
        if orphan_number and p.endswith("Chapter_00_FrontMatter.md"):
            t += "\n\nSynthetic drifted abstract figure: %s kWh/m2/yr.\n" % orphan_number
        docs.append((p, t))
    if extra_text is not None:
        docs.append((os.path.join(ROOT, "chapters", "__falsifier__.md"), extra_text))

    results = []

    # C1 -- dashes
    hits = [(rel(p), t.count(EM), t.count(EN)) for p, t in docs if EM in t or EN in t]
    results.append(("C1", not hits, "no em dash or en dash in manuscript text",
                    ["%s  em=%d en=%d" % h for h in hits]))

    # C2 -- the 2J phrase
    bad = []
    for p, t in docs:
        for m in re.finditer(r"four building archetypes", t, re.I):
            s = max(0, m.start() - 120)
            if not NEG.search(t[s:m.end()]):
                bad.append("%s  line %d, not in a negation" % (rel(p), t[:m.start()].count("\n") + 1))
    results.append(("C2", not bad, 'the 2J phrase "four building archetypes" appears only negated', bad))

    # C3 -- superseded directory cited as a source
    bad = []
    for p, t in docs:
        for m in re.finditer(r"outputs_step9(?!_deliverable)", t):
            line_start = t.rfind("\n", 0, m.start()) + 1
            line_end = t.find("\n", m.end())
            line = t[line_start:line_end if line_end > 0 else len(t)]
            if not SUPERSEDED_OK.search(line):
                bad.append("%s  line %d: %s" % (rel(p), t[:m.start()].count("\n") + 1, line.strip()[:110]))
    results.append(("C3", not bad, "the superseded outputs_step9/ is never cited as a source", bad))

    # C4 -- every file names a source, except two declared summary sections.
    # The exemption is NOT a way to let those two off: C6 below holds them to a
    # STRICTER rule, so narrowing C4 here cannot silence a real case.
    EXEMPT = {"chapters/Chapter_00_FrontMatter.md", "chapters/Chapter_08_Conclusion.md"}
    bad = [rel(p) for p, t in docs
           if rel(p) not in EXEMPT
           and not re.search(r"(^|\n)#+\s*Sources|\.md|\.csv|\.json|\.py|\.png|dr_L3-|Table \d", t)]
    results.append(("C4", not bad,
                    "every scanned file names a source (front matter and conclusion exempt, see C6)", bad))

    # C6 -- the exempt files may state no number that is not already stated elsewhere.
    # An abstract whose figures have drifted from the tables is the failure this catches.
    body = "\n".join(t for p, t in docs if rel(p) not in EXEMPT)
    bad = []
    for p, t in docs:
        if rel(p) not in EXEMPT:
            continue
        for m in re.finditer(r"\d+\.\d+", t):
            if m.group() not in body:
                ln = t[:m.start()].count("\n") + 1
                bad.append("%s  line %d: %s appears nowhere else in the manuscript" % (rel(p), ln, m.group()))
    results.append(("C6", not bad,
                    "every number in the front matter and conclusion is stated somewhere else too", bad))

    # C5 -- vacuity guard
    n = len(paths)
    results.append(("C5", n >= 10, "the scan saw files (%d found; a real build has 10+)" % n,
                    [] if n >= 10 else ["only %d file(s) scanned -- C1 to C4 would pass vacuously" % n]))
    return results, len(paths)


def main():
    falsify = "--falsify" in sys.argv
    print("V5-F4 -- manuscript prose rules")
    if falsify:
        print("  FALSIFY MODE: one em dash into a synthetic chapter (C1 must fail), and one")
        print("  drifted figure into the front matter that appears nowhere else (C6 must fail).\n")
        results, n = run(extra_text="A synthetic line with an em dash %s here. See Table 1." % EM,
                         orphan_number="777.77")
    else:
        results, n = run()
        print("  scanning %d markdown file(s) under writing/{%s}\n" % (n, ",".join(SCAN)))

    npass = 0
    for cid, ok, desc, detail in results:
        print("  [%s] %s  %s" % ("PASS" if ok else "FAIL", cid, desc))
        for d in detail[:12]:
            print("        %s" % d)
        if len(detail) > 12:
            print("        ... and %d more" % (len(detail) - 12))
        npass += 1 if ok else 0

    print("\n  %d PASS / %d FAIL" % (npass, len(results) - npass))
    if falsify:
        by = dict((r[0], r[1]) for r in results)
        want_fail = ["C1", "C6"]
        still_passing = [c for c in want_fail if by.get(c, True)]
        for c in want_fail:
            print("  falsifier: %s %s" % (c, "failed as required -- it has teeth"
                                          if not by.get(c, True) else "STILL PASSED -- this arm is broken"))
        return 1 if still_passing else 0
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
