#!/usr/bin/env python3
"""v4 ledger check -- the same four conditions as its v3 predecessor, on the v4 round.

WHY IT IS A SEPARATE FILE AND NOT A FLAG
----------------------------------------
The v3 check reads V3-* ids out of three artefacts and asserts they agree.  v4's
tasks live on the SAME board, so a single check with a widened id pattern would
see v4's five owed rows while reading v3's plan, which owes nothing, and would
report a disagreement that does not exist.  Keeping one checker per round means
each one compares like with like; the board simply carries two vocabularies.

WHAT THIS ROUND EXISTS TO FIX, RESTATED SO THE CHECK IS NOT MISREAD
-------------------------------------------------------------------
On 2026-08-06 v3 closed 6/6 and the v3 check went green -- correctly, because
nothing was owed.  At the same moment the board was telling a reader that the
LEG was finished, while Step 9 carried three failures that had never been on it.
Green check, misleading board, no contradiction between them: the check's four
conditions were all satisfied by an empty set.

So a green run of THIS file means "the five owed items are visible in all three
artefacts".  It does not mean the leg is fine, and it never could.  That is what
the scope band on the board is for.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(HERE, os.pardir, "v3")
sys.path.insert(0, V3)

import j3_ledger_check as L                                      # noqa: E402

# The parsers read L.ID_RE at call time, so retargeting the module is enough.
# The fixture strings are rewritten the same way, so --falsify exercises v4's
# vocabulary rather than v3's and cannot pass by matching a stale id.
L.ID_RE = r"V4-[A-Z]\d+"
_OLD, _NEW = L.FIX_ID, "V4-X1"
for _name in ("_FIX_PLAN", "_FIX_PROMPT", "_FIX_BOARD"):
    setattr(L, _name, getattr(L, _name).replace(_OLD, _NEW))
# Retargeting the TEMPLATES is not enough: falsify() names the fixture id itself
# when it builds each perturbation.  Missing this is what made the first v4
# --falsify run die on StopIteration instead of reporting arms.
L.FIX_ID = _NEW

PLAN = os.path.join(HERE, "3rdJ_L3_v4_implementation.md")
PROMPT = os.path.join(HERE, os.pardir, "prompts",
                      "3rdJ_L3_manager_prompt_2026-08-06_v4_open.md")
BOARD = os.path.join(V3, "board_v3.html")            # one board, both rounds

L.PLAN, L.PROMPT, L.BOARD = PLAN, PROMPT, BOARD


def main():
    if "--falsify" in sys.argv:
        return L.falsify()
    # check() returns the LIST OF FAILURES, so empty means pass.  Written the
    # other way round first, which exits 1 on a healthy tree and 0 on a broken
    # one -- worse than no check, and it only showed up because the first live
    # run printed [PASS] beside a non-zero exit code.  Same shape as the `tee`
    # defect on 08-06: never read the banner, read the status.
    return 1 if L.check(PLAN, PROMPT, BOARD) else 0


if __name__ == "__main__":
    sys.exit(main())
