#!/usr/bin/env python
"""V3-J3 -- the decision-ledger check.

THE DEFECT IT CATCHES HAS HAPPENED TWICE, AND NEITHER TIME DID ANYONE NOTICE
---------------------------------------------------------------------------
1. On 2026-08-05 the v2 handoff's status line read "Waiting on the user: nothing
   blocking" while three decisions were owed.  A status line that cannot say
   SOMETHING IS OWED is not a status line.
2. Between 08-05 and 08-06 the deliverable "add a person-level retail gate" left
   the ledger entirely.  Nobody decided to drop it.  It became V3-J1 only because
   someone happened to re-read an old entry.

WHAT IT CHECKS
--------------
The plan, the manager prompt and the board must agree, in their own vocabularies,
about what is owed by the user:

    plan    summary-table rows marked with the decision glyph
    prompt  task-table rows marked "your call"
    board   task entries in state "waiting", AND the reader-facing decisions list

  C1  the three sets are identical
  C2  every owed ID has its own task section in the plan
  C3  the plan's status-panel DECISION count equals the number of owed rows
  C4  every owed ID is named in the board's reader-facing decisions block
      -- the 08-05 defect was reader-facing: a machine-readable field said one
      thing while the prose said "nothing"

A MISSING SECTION IS A HARD FAILURE, NEVER A SKIP.  A checker that skipped IDs it
could not find would have passed on 2026-08-05, which is the vacuous-gate pattern
this project already catalogues sixteen kinds of.

Usage
-----
  python j3_ledger_check.py                 # check the real tree
  python j3_ledger_check.py --falsify       # 2 controls + 6 perturbations, on a
                                            # SYNTHETIC fixture, in a temp dir

Exit 0 if consistent, 1 otherwise.  --falsify exits 1 unless every perturbation
is detected AND the unmodified control passes.
"""

import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "3rdJ_L3_v3_implementation.md")
# Pointed at the CURRENT handoff, not a fixed one: 2026-08-06 evening, the "_v3_open" prompt was
# superseded by "_v3_closed" when the last three decisions were taken.  A ledger check reading a
# stale prompt would agree with itself about a document nobody is following any more.
PROMPT = os.path.join(HERE, os.pardir, "prompts",
                      "3rdJ_L3_manager_prompt_2026-08-06_v3_closed.md")
BOARD = os.path.join(HERE, "board_v3.html")

ID_RE = r"V3-[A-Z]\d+"

# The synthetic fixture's owed id, as a CONSTANT rather than a literal.  The v4
# round reuses this falsifier with its own vocabulary, and the id was hard-coded
# in four places inside falsify() as well as in the fixture templates -- so
# retargeting only the templates left the perturbations hunting for a v3 id
# inside a v4 fixture, and the first arm died on StopIteration.  Anything that
# names the fixture id reads it from here.
FIX_ID = "V3-X1"


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def plan_owed(text):
    """Summary-table rows whose first cell carries the decision glyph."""
    out = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 3 and "\U0001F7E3" in cells[1]:      # the purple glyph
            m = re.search(ID_RE, cells[2])
            if m:
                out.append(m.group(0))
    return out


def plan_sections(text):
    return set(re.findall(r"^##+\s+(" + ID_RE + r")\b", text, re.M))


def plan_decision_count(text):
    m = re.search(r"^DECISION\s+(\d+)", text, re.M)
    return int(m.group(1)) if m else None


def prompt_owed(text):
    out = []
    for line in text.splitlines():
        if line.startswith("|") and "your call" in line:
            m = re.search(ID_RE, line)
            if m:
                out.append(m.group(0))
    return out


def board_owed(text):
    """Task entries in state "waiting" inside the board's task array."""
    return re.findall(r'\["(' + ID_RE + r')","[^"]*","waiting"', text)


def board_prose(text):
    """IDs named in the reader-facing decisions block, not the data array."""
    m = re.search(r'<section class="decisions">(.*?)</section>', text, re.S)
    return set(re.findall(ID_RE, m.group(1))) if m else set()


def check(plan_p=PLAN, prompt_p=PROMPT, board_p=BOARD, verbose=True):
    plan, prompt, board = _read(plan_p), _read(prompt_p), _read(board_p)
    P, R, B = set(plan_owed(plan)), set(prompt_owed(prompt)), set(board_owed(board))
    secs, prose = plan_sections(plan), board_prose(board)
    n_panel = plan_decision_count(plan)

    fails = []
    if not (P == R == B):
        fails.append(f"C1 the three artefacts disagree about what is owed: "
                     f"plan={sorted(P)} prompt={sorted(R)} board={sorted(B)}")
    missing = sorted((P | R | B) - secs)
    if missing:
        fails.append(f"C2 owed with no task section in the plan: {missing} "
                     f"(a missing section is a HARD FAILURE, never a skip)")
    if n_panel is None:
        fails.append("C3 the plan's status panel has no DECISION count to check")
    elif n_panel != len(P):
        fails.append(f"C3 status panel says DECISION {n_panel}, the summary "
                     f"table has {len(P)} decision rows")
    silent = sorted((P | R | B) - prose)
    if silent:
        fails.append(f"C4 owed but not named in the board's reader-facing "
                     f"decisions block: {silent} -- the 08-05 defect was exactly "
                     f"this: the prose said nothing was owed")

    if verbose:
        print(f"owed  plan={sorted(P)}")
        print(f"      prompt={sorted(R)}")
        print(f"      board={sorted(B)}")
        print(f"      sections={sorted(secs)}")
        for f in fails:
            print(f"  [FAIL] {f}")
        print("  [PASS] plan, prompt and board agree; every owed item has a "
              "task section and is visible to a reader" if not fails else "")
    return fails


# ── falsifier ────────────────────────────────────────────────────────────────

# ── the fixture is SYNTHETIC, and that is the second thing this file got wrong ──
#
# Until 2026-08-06 evening the perturbation arms were built by copying the LIVE
# plan/prompt/board and deleting things out of them.  That worked only while the
# live tree happened to contain an owed item.  The moment the last three
# decisions were taken, every anchor vanished and `--falsify` died with a
# StopIteration -- i.e. THE FALSIFIER STOPPED WORKING AT EXACTLY THE MOMENT THE
# LEDGER WENT EMPTY, which is the state in which a reader most needs to know
# whether the check still works.  A test whose fixtures are the thing under
# observation is not independent of it.
#
# So the fixture is now a minimal three-artefact ledger written from scratch,
# carrying one owed item (V3-X1) in each artefact's own vocabulary.  It exercises
# the same four parsers.  The live tree is still checked -- as its own arm.

_FIX_PLAN = """# fixture plan

```
DONE        0 / 1
DECISION    1
```

| ✔ | ID | Task | Cost | Depends on | Status |
|---|---|---|---|---|---|
| \U0001F7E3 | **V3-X1** | the fixture's one owed item | decision | none | **DECISION** |

## V3-X1 — the fixture's one owed item

Body.
"""

_FIX_PROMPT = """# fixture prompt

| ID | | |
|---|---|---|
| **V3-X1** | \U0001F7E3 your call | the fixture's one owed item |

## 3. Standing constraints
none.
"""

_FIX_BOARD = """<section class="decisions">
  <h2>One thing is waiting on you</h2>
  <p><strong>The fixture's one owed item <span class="mono">V3-X1</span></strong></p>
</section>
<script>
const WP=[["V3-X1","the fixture's one owed item","waiting","short","tag",
  "explain"]];
</script>
"""


def _fixture(tmp, tag="f"):
    d = os.path.join(tmp, tag)
    os.makedirs(d, exist_ok=True)
    paths = []
    for name, body in (("plan.md", _FIX_PLAN), ("prompt.md", _FIX_PROMPT),
                       ("board.html", _FIX_BOARD)):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        paths.append(p)
    return tuple(paths)


def _fixture_live(tmp):
    """The real artefacts, copied. Used for the live arm only."""
    d = os.path.join(tmp, "live")
    os.makedirs(d, exist_ok=True)
    out = []
    for src, name in ((PLAN, "plan.md"), (PROMPT, "prompt.md"), (BOARD, "board.html")):
        dst = os.path.join(d, name)
        shutil.copy(src, dst)
        out.append(dst)
    return tuple(out)


def _sub(path, old, new, count=1):
    t = _read(path)
    assert old in t, f"fixture anchor not found in {os.path.basename(path)}"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(t.replace(old, new, count))


def falsify():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        # F0 -- control
        p, r, b = _fixture(tmp, "f0")
        results.append(("F0 control, unmodified", check(p, r, b, False), False))

        # F0L -- the LIVE tree, as its own arm.  The fixture proves the check
        # still works; this proves the repository currently agrees with itself.
        p, r, b = _fixture_live(tmp)
        results.append(("F0L the live plan/prompt/board", check(p, r, b, False), False))

        # F1 -- an owed item drops out of the prompt
        p, r, b = _fixture(tmp, "f1")
        t = _read(r)
        line = next(l for l in t.splitlines() if "your call" in l and FIX_ID in l)
        _sub(r, line + "\n", "")
        results.append(("F1 owed item removed from the prompt", check(p, r, b, False), True))

        # F2 -- an owed item drops out of the board's task array
        p, r, b = _fixture(tmp, "f2")
        _sub(b, '["%s","the fixture\'s one owed item","waiting"' % FIX_ID,
             '["%s","the fixture\'s one owed item","open"' % FIX_ID)
        results.append(("F2 owed item removed from the board", check(p, r, b, False), True))

        # F3 -- the 2026-08-05 defect: the prompt says nothing is owed
        p, r, b = _fixture(tmp, "f3")
        t = _read(r)
        keep = [l for l in t.splitlines() if "your call" not in l]
        with open(r, "w", encoding="utf-8") as fh:
            fh.write("\n".join(keep).replace(
                "## 3. Standing constraints",
                "**Waiting on the user: nothing blocking.**\n\n## 3. Standing constraints"))
        results.append(("F3 the 08-05 defect: prompt says nothing is owed",
                        check(p, r, b, False), True))

        # F4 -- owed everywhere, but the plan has no task section for it
        p, r, b = _fixture(tmp, "f4")
        _sub(p, "## %s — the fixture's one owed item" % FIX_ID,
             "## the fixture's one owed item")
        results.append(("F4 owed item has no task section in the plan",
                        check(p, r, b, False), True))

        # F5 -- the status panel drifts away from the table
        p, r, b = _fixture(tmp, "f5")
        _sub(p, "DECISION    1", "DECISION    2")
        results.append(("F5 status panel count drifts from the table",
                        check(p, r, b, False), True))

        # F6 -- the machine-readable field still says "waiting", but the READER
        # is no longer told.  Added because on the first falsifier run C4 was
        # never the check that fired: a condition that has never fired has not
        # been shown to work, which is this project's own standard.
        p, r, b = _fixture(tmp, "f6")
        t = _read(b)
        m = re.search(r'<section class="decisions">(.*?)</section>', t, re.S)
        blinded = m.group(0).replace(FIX_ID, "the model-selection question")
        with open(b, "w", encoding="utf-8") as fh:
            fh.write(t.replace(m.group(0), blinded))
        results.append(("F6 owed in the data, invisible in the board's prose",
                        check(p, r, b, False), True))

    ok = True
    print()
    for name, fails, should_fail in results:
        detected = bool(fails)
        good = detected == should_fail
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: "
              f"{'detected' if detected else 'clean'}"
              f"{'' if good else '  <-- WRONG'}")
        for f in fails:
            print(f"           {f[:110]}")
    # "arms", not "perturbations": the controls are not things shown to fail,
    # and calling them perturbations would quietly inflate the count.  COUNTED,
    # not hard-coded -- the hard-coded version silently reported "1 control + 7"
    # the moment a second control (the live tree) was added.
    n_ctrl = sum(1 for _n, _f, should in results if not should)
    n_pert = len(results) - n_ctrl
    print(f"\n{sum(1 for n, f, s in results if bool(f) == s)}/{len(results)} "
          f"arms behaved as required "
          f"({n_ctrl} control{'s' if n_ctrl != 1 else ''} + {n_pert} perturbations)")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--falsify" in sys.argv:
        sys.exit(falsify())
    sys.exit(1 if check() else 0)
