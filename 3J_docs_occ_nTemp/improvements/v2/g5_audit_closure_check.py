#!/usr/bin/env python3
"""V2-G5's test method: count the findings, count the terminal statuses, and require them to match.

The plan states it as *"Count the findings; count the terminal statuses; they must match: 13 + 5 + 6
= 24."* That is a check that can genuinely fail -- a finding left without a disposition, a status
invented for a finding that does not exist, or a row silently dropped while re-writing the tables.

FOUR CHECKS, because the count alone is weaker than it looks:

  C1  every one of the 24 finding IDs appears in the closure with a terminal status.
  C2  every status is one of the three permitted words. "Partly fixed", "in progress" and "open" are
      NOT terminal, and the whole point of the task is that nothing is left in that state.
  C3  no EXTRA finding ID appears -- a closure that invents `B-14` is as wrong as one that forgets
      `B-9`. Counting only forwards would miss it.
  C4  every FIXED status names the task that did it (`V2-xx`). "FIXED" with nothing after it is an
      unfalsifiable claim, the same defect V2-G2 removed from the master documents.

Run with `--falsify` to see all four fail on purpose.

    python g5_audit_closure_check.py [--falsify]
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.abspath(os.path.join(
    HERE, "..", "v0", "investigation", "investigation_v2",
    "3rdJ_L3_backward_audit_2026-08-04.md"))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EXPECTED = ([f"B-{i}" for i in range(1, 14)] +
            [f"C-{i}" for i in range(1, 6)] +
            [f"G-{i}" for i in range(1, 7)])
TERMINAL = ("FIXED", "ACCEPTED-AS-DOCUMENTED", "WITHDRAWN")
ROW = re.compile(r"^\|\s*\*\*([BCG]-\d+)\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", re.M)
_N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %-3s %s" % ("PASS" if ok else "FAIL", tag, detail))


def main(falsify=False):
    text = open(AUDIT, encoding="utf-8").read()
    head = text.index("# AUDIT CLOSED")
    closure = text[head:]
    if falsify:
        # Each mutation must hit ONE check. The first version of this block dropped B-9 and then
        # re-added it with a non-terminal status, so C1 still saw a B-9 row and PASSED -- the
        # falsifier tested C2 twice and C1 not at all. Caught by running it: a falsifier that does
        # not fail is the same defect as a gate that does not fail.
        #   C1: B-9 is REMOVED and not replaced.
        #   C2: a DIFFERENT finding (B-2) is given a non-terminal status.
        #   C3: an invented finding.
        #   C4: a FIXED naming no task.
        closure = re.sub(r"^\|\s*\*\*B-9\*\*.*$", "", closure, flags=re.M)
        closure = re.sub(r"^(\|\s*\*\*B-2\*\*\s*\|)[^|]*\|",
                         r"\1 **IN PROGRESS** |", closure, count=1, flags=re.M)
        closure += ("\n| **B-14** | **FIXED** — **V2-Z9** | invented |\n"
                    "| **C-1** | **FIXED** | names no task |\n")

    rows = {m.group(1): (m.group(2), m.group(3)) for m in ROW.finditer(closure)}
    print("=" * 92)
    print("V2-G5 audit-closure check%s" % ("   [FALSIFY MODE -- all four MUST fail]" if falsify
                                           else ""))
    print("=" * 92)
    print("  parsed %d finding row(s) from the closure section\n" % len(rows))

    missing = [f for f in EXPECTED if f not in rows]
    rec("C1", not missing and len(rows) >= 24,
        "%d/%d findings carry a status%s"
        % (len(EXPECTED) - len(missing), len(EXPECTED),
           "" if not missing else "; MISSING " + ", ".join(missing)))

    bad = {f: s for f, (s, _) in rows.items()
           if not any(t in s for t in TERMINAL)}
    rec("C2", not bad, "every status is one of %s%s"
        % ("/".join(TERMINAL), "" if not bad else "; NON-TERMINAL " + str(bad)))

    extra = [f for f in rows if f not in EXPECTED]
    rec("C3", not extra, "no invented findings%s"
        % ("" if not extra else "; EXTRA " + ", ".join(extra)))

    unsourced = [f for f, (s, _) in rows.items()
                 if "FIXED" in s and not re.search(r"V2-[A-Z]\d+", s)]
    rec("C4", not unsourced, "every FIXED names its task%s"
        % ("" if not unsourced else "; UNSOURCED " + ", ".join(unsourced)))

    if not falsify:
        tally = {}
        for f, (s, _) in rows.items():
            k = next((t for t in TERMINAL if t in s), "?")
            tally[k] = tally.get(k, 0) + 1
        print("\n  terminal statuses: %s" % tally)
        print("  count check: 13 B + 5 C + 6 G = %d, parsed %d" % (len(EXPECTED), len(rows)))

    print("-" * 92)
    print("%d PASS / %d FAIL" % (_N["pass"], _N["fail"]))
    if falsify:
        ok = _N["fail"] == 4
        print("FALSIFIER %s -- expected 4 FAIL, got %d" % ("HOLDS" if ok else "IS BROKEN",
                                                           _N["fail"]))
        return 0 if ok else 1
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main("--falsify" in sys.argv))
