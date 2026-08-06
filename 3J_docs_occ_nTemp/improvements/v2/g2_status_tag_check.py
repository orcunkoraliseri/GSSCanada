#!/usr/bin/env python3
"""V2-G2's test method, executed rather than asserted.

The plan states it in one line: *"Every `DONE` tag names an artefact that exists on disk. Check each
one."* That is the whole point of the task. Flipping `PLANNED` to `DONE` is worth nothing on its own
-- both are unfalsifiable claims about a document. What makes the new tag better than the old one is
that it can be WRONG, and this script is what makes it wrong when it is.

THREE CHECKS, and the third is the one that stops the other two being cosmetic:

  C1  every artefact named on a DONE line exists on disk.
  C2  no `PLANNED (Leg 3)` tag survives OUTSIDE struck-through text. A superseded convention is kept
      visible with `~~...~~` (the project's correction rule: struck, never deleted), so the check has
      to distinguish "still claimed" from "recorded as withdrawn" instead of counting the substring.
  C3  every DONE line actually NAMES something. A `DONE` tag with no artefact on the line passes C1
      vacuously -- there is nothing to stat -- and that is precisely the tag this task exists to
      remove. Without C3, replacing every `PLANNED` with a bare `DONE` would score 100 %.

Run with `--falsify` to see all three fail on purpose.

    python g2_status_tag_check.py [--falsify]
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# SEARCH ROOT is the whole 3J tree, not `Leg3_4-split`. Corrected 2026-08-05 after the check
# reported `3rdJ_00_2split_Occupancy_Pipeline.md` missing: that file exists, in `Leg2_2-split`, and
# the master doc cites it correctly as a cross-leg reference. A checker that cannot see half the
# repository reports true statements as false, which is worse than not checking -- it spends the
# reader's trust on a defect that is the checker's own. The check is not being loosened: every
# artefact still has to be found, on disk, by name.
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LEG3 = os.path.join(ROOT, "Leg3_4-split")
DOCS = [os.path.join(LEG3, "3rdJ_00_4split_Occupancy_Pipeline.md"),
        os.path.join(LEG3, "3rdJ_00_4split_Occupancy_Pipeline_Overview.md")]

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ART = re.compile(r"(?:Step\d_docs/)?3rdJ_[A-Za-z0-9_]+\.(?:py|md)")
STRUCK = re.compile(r"~~.*?~~", re.S)
_N = {"pass": 0, "fail": 0}


def rec(ok, tag, detail=""):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", tag, ("  -- " + detail) if detail else ""))
    return ok


def resolve(name):
    """Resolve an artefact reference to a real file, or None.

    Three forms occur in the two documents and all three are legitimate, so all three are tried
    before anything is called missing:
      * `Step7_docs/3rdJ_07_aug_to_bem_4split.py` -- relative to `Leg3_4-split`, the prose form.
      * `../Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` -- relative to the 3J tree root, a
        cross-leg reference.
      * a bare `3rdJ_x.py` -- the diagram form. The box is 78 characters wide and cannot carry a
        directory prefix, so the check finds the file by name rather than demanding the document
        spell out a path it has no room for.
    Resolution order is most-specific first; the walk is the last resort, never the first.
    """
    rel = name.replace("/", os.sep)
    for base in (LEG3, ROOT):
        p = os.path.join(base, rel)
        if os.path.isfile(p):
            return p
    leaf = os.path.basename(rel)
    for root, _dirs, files in os.walk(ROOT):
        if leaf in files:
            return os.path.join(root, leaf)
    return None


def done_lines(text):
    """DONE lines, ignoring anything inside a struck-through span."""
    live = STRUCK.sub("", text)
    return [l for l in live.split("\n") if "DONE (Leg 3" in l or "DONE (Leg 3)" in l]


def main(falsify=False):
    print("=" * 88)
    print("V2-G2 status-tag check%s" % ("  [FALSIFY MODE -- all three MUST fail]" if falsify else ""))
    print("=" * 88)

    total_art, missing, bare = 0, [], []
    for doc in DOCS:
        text = open(doc, encoding="utf-8").read()
        if falsify:
            # F1: name an artefact that does not exist. F3: a DONE tag that names nothing.
            text += ("\n║  Status: DONE (Leg 3) -- 3rdJ_99_does_not_exist.py"
                     "\n║  Status: DONE (Leg 3)\n")
        for line in done_lines(text):
            names = ART.findall(line)
            if not names:
                bare.append((os.path.basename(doc), line.strip()[:70]))
                continue
            for n in names:
                total_art += 1
                if resolve(n) is None:
                    missing.append((os.path.basename(doc), n))

    rec(not missing, "C1  every artefact named on a DONE line exists",
        "%d artefact reference(s) checked%s"
        % (total_art, "" if not missing else "; MISSING " + ", ".join(m[1] for m in missing)))

    live_planned = []
    for doc in DOCS:
        text = open(doc, encoding="utf-8").read()
        if falsify:
            text += "\n### Step 10 ⚠️ PLANNED (Leg 3)\n"
        for line in STRUCK.sub("", text).split("\n"):
            if "PLANNED (Leg 3" in line:
                live_planned.append((os.path.basename(doc), line.strip()[:70]))
    rec(not live_planned, "C2  no live PLANNED (Leg 3) tag survives",
        "0 outside struck text" if not live_planned
        else "%d still claimed: %s" % (len(live_planned), live_planned[:2]))

    rec(not bare, "C3  every DONE line names an artefact",
        "no bare DONE tags" if not bare else "%d bare: %s" % (len(bare), bare[:2]))

    print("-" * 88)
    print("%d PASS / %d FAIL" % (_N["pass"], _N["fail"]))
    if falsify:
        ok = _N["fail"] == 3
        print("FALSIFIER %s -- expected 3 FAIL, got %d"
              % ("HOLDS" if ok else "IS BROKEN", _N["fail"]))
        return 0 if ok else 1
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main("--falsify" in sys.argv))
