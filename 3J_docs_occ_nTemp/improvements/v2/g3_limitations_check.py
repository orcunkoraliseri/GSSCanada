#!/usr/bin/env python3
"""V2-G3 test method, executed rather than asserted.

The task's own test method reads: "Every limitation names its evidence. No limitation is a hedge
without a number." That is checkable, so it is checked here instead of being claimed in a log entry.

Two assertions per limitation item:
  1. it carries an `*Evidence:*` pointer;
  2. it carries at least one bounding NUMBER that is not merely an identifier.

Assertion 2 is the one that needs care. A naive `\\d` search passes on any item mentioning a year, a
task ID, a standard edition or its own label -- i.e. it would pass a pure hedge that happens to cite
"V2-B1 (2026)". So identifiers are stripped BEFORE the search: item labels, V2-/B- task IDs, 4-digit
years, `90.1-<yr>` editions, `Table 7.1`, `Step 8`, `CZ 6A`, `Leg 3`. What survives is a quantity.

🔴 AND THAT WAS STILL NOT ENOUGH -- recorded because the check was caught passing when it should have
failed. Falsification case F2 stripped L14 of its live measurements and the check still returned PASS,
because L14 *quotes the superseded claim it replaced* ("~2.1-2.3 %, stable across cycles") and that
quotation carries digits. A limitation citing the wrong old number while stating no new one would have
passed. The fix follows the section's own writing convention: **live measurements are bolded, quoted
and superseded ones are not**, so the digit must be found INSIDE a `**bold**` span. F2 fails now.
The general lesson is the project's own: a gate is worth what its falsification showed, and this one
was worth nothing until F2 was run.

EXPECTED RESULT: 16 items, 0 missing evidence, and exactly ONE item with no bounding number --
**L15**, the ground-level-EPW limitation, which says in its own text that it is not quantified. The
exception is hard-coded here on purpose: if L15 ever gains a real measurement, or if a SECOND
unquantified item appears, this check fails and someone has to look.

Read-only. Run: py improvements/v2/g3_limitations_check.py
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.abspath(os.path.join(HERE, "..", "..", "Leg3_4-split",
                                   "3rdJ_00_4split_Occupancy_Pipeline.md"))
HEADING = "## LIMITATIONS — CONSOLIDATED"
EXPECTED_ITEMS = 16
DECLARED_UNQUANTIFIED = ["L15"]      # ground-level EPW on a supertall -- says so in its own text

IDENTIFIERS = [r"\*\*L\d+", r"V2-[A-Z]\d+", r"\bB-\d+\b", r"\bL\d+\b", r"\b(?:19|20)\d{2}\b",
               r"90\.1-\d+", r"Table [\d.]+", r"Step[- ]?\d+", r"CZ ?\d+[A-Z]?", r"Leg[- ]?\d"]


def main():
    if not os.path.isfile(DOC):
        print("[FAIL] master doc not found: %s" % DOC)
        return 1
    text = io.open(DOC, encoding="utf-8").read()
    if HEADING not in text:
        print("[FAIL] no consolidated limitations section in %s" % os.path.basename(DOC))
        return 1
    sec = text.split(HEADING, 1)[1]
    items = [b for b in re.split(r"\n(?=\*\*L\d+ — )", sec) if re.match(r"\*\*L\d+ — ", b)]

    no_evidence, no_number = [], []
    for b in items:
        lid = re.match(r"\*\*(L\d+)", b).group(1)
        body = b.split("### ")[0]                    # stop at the self-check table
        if "*Evidence:*" not in body:
            no_evidence.append(lid)
        # Only BOLD spans count as live measurements -- see the F2 note in the module docstring.
        quantified = False
        for span in re.findall(r"\*\*(.+?)\*\*", body, flags=re.S):
            for pat in IDENTIFIERS:
                span = re.sub(pat, " ", span)
            if re.search(r"\d", span):
                quantified = True
                break
        if not quantified:
            no_number.append(lid)

    print("V2-G3 limitations check -- %s" % os.path.basename(DOC))
    print("  items found            : %d (expected %d)" % (len(items), EXPECTED_ITEMS))
    print("  missing *Evidence:*    : %s" % (", ".join(no_evidence) or "none"))
    print("  no bounding number     : %s" % (", ".join(no_number) or "none"))
    print("  declared unquantified  : %s" % ", ".join(DECLARED_UNQUANTIFIED))

    bad = []
    if len(items) != EXPECTED_ITEMS:
        bad.append("expected %d items, found %d" % (EXPECTED_ITEMS, len(items)))
    if no_evidence:
        bad.append("no *Evidence:* pointer: %s" % ", ".join(no_evidence))
    if no_number != DECLARED_UNQUANTIFIED:
        bad.append("unquantified set is %s, declared %s -- an item is hedging without a number, or "
                   "L15 gained one and the declaration is stale"
                   % (no_number or "[]", DECLARED_UNQUANTIFIED))
    if bad:
        print("\n[FAIL]")
        for b in bad:
            print("   - " + b)
        return 1
    print("\n[PASS] every limitation names its evidence; every limitation but the one declared "
          "unquantified carries a bounding measurement.")
    print("REMINDER: this checks that a number is PRESENT, never that it is RIGHT. It cannot fail "
          "on a limitation bounded by a wrong measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
