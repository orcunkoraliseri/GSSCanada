#!/usr/bin/env python3
"""V2-E7 -- prove the two INFO-channel defects, by OBSERVING them rather than reading the source.

    py -3 probe_defects.py

Both defects are exercised dynamically and the verdict comes from what the code actually did:

  P1  self.results had only pass/fail/warn, so _rec("info", ...) raised KeyError.
  P2  every status expression fell through to the FAIL branch, so a row whose Status is "INFO"
      PRINTED as [FAIL] -- and would have rendered with the fail-row CSS class.

Run it against the pre-R5 archive copy and both must reproduce; run it against the shipped file and
both must be gone. It builds the object with object.__new__ and sets only the attributes these two
code paths touch -- loading 67 MB of CSV to prove a KeyError would be theatre.

The first version of this probe decided P2 by regex-matching the ternary in the source. That worked
exactly once: the fix replaced the ternary with a dict, so the scraper stopped matching and printed
"?" while a hardcoded summary line below it still claimed the old result. A checker that reports a
verdict it did not measure is worse than no checker, so P2 is now read from captured output.
"""
import importlib.util as ilu
import io
import os
import re
import shutil
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
MAIN = "3rdJ_05_censusLinkage_4split.py"
VAL = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "3rdJ_05_censusLinkage_4split_val.py"
VAL = VAL.resolve()

# The validator imports its sibling main script by a path relative to ITS OWN directory, so an
# archived copy under archive/ dies with FileNotFoundError before the probe gets to run. Stage it
# beside the main script instead of asking the reader to work that out from a stack trace.
_staged = None
if not (VAL.parent / MAIN).is_file():
    _staged = HERE / ("_probe_staged_" + VAL.name)
    shutil.copyfile(VAL, _staged)
    print("[stage] %s has no %s beside it -> loaded via %s"
          % (VAL.name, MAIN, _staged.name))
    VAL_LOAD = _staged
else:
    VAL_LOAD = VAL

try:
    spec = ilu.spec_from_file_location("_v", VAL_LOAD)
    mod = ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
finally:
    if _staged and _staged.exists():
        _staged.unlink()
V = mod.CensusLinkageValidator4CH

print("=" * 84)
print("E7 defect probe -- validator under test: %s" % os.path.basename(str(VAL)))
print("=" * 84)

# ---- P1: does _rec("info", ...) survive? -----------------------------------------------------
src = VAL.read_text(encoding="utf-8")
m = re.search(r"self\.results:\s*dict\[str,\s*list\[str\]\]\s*=\s*(\{.*?\})", src, re.S)
declared = eval(m.group(1)) if m else {"pass": [], "fail": [], "warn": []}

o = object.__new__(V)
o.results = {k: [] for k in declared}
print("\nP1  declared result channels: %s" % sorted(o.results))
buf, sys.stdout = sys.stdout, io.StringIO()
try:
    o._rec("info", "probe | a non-scoring reference line")
    p1_raised, p1_out = None, sys.stdout.getvalue().strip()
except KeyError as e:
    p1_raised, p1_out = repr(e), sys.stdout.getvalue().strip()
finally:
    sys.stdout = buf
if p1_raised:
    print("P1  _rec('info', ...) -> \U0001F534 DEFECT PRESENT: KeyError %s" % p1_raised)
else:
    print("P1  _rec('info', ...) -> survived, printed: %s" % p1_out)

# ---- P2: how does a Status="INFO" summary row actually print? --------------------------------
o2 = object.__new__(V)
o2.summary_rows = [{"Gate / Check": "probe", "Threshold": "-", "Observed": "1.615 pp",
                    "Status": "INFO"}]
buf, sys.stdout = sys.stdout, io.StringIO()
try:
    o2.generate_summary_table()
finally:
    cap, sys.stdout = sys.stdout.getvalue(), buf
row = [l for l in cap.split("\n") if "probe" in l]
printed = row[0].strip() if row else "(no row printed)"
p2_defect = "[FAIL]" in printed
print("\nP2  a summary row with Status='INFO' printed as:")
print("      %s" % printed)
print("P2  -> %s" % ("\U0001F534 DEFECT PRESENT: an INFO row prints as a FAILURE" if p2_defect
                     else "renders as INFO, not as a failure"))

print("\n" + "-" * 84)
n_def = int(bool(p1_raised)) + int(p2_defect)
print("%d of 2 defects present in %s" % (n_def, os.path.basename(str(VAL))))
print("Expected: 2/2 against archive/..._2026-08-06_pre_R5.py, 0/2 against the shipped validator.")
sys.exit(0)
