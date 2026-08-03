#!/usr/bin/env python3
"""Falsifier for G4 -- the 'every schedule was READ, not skipped' gate.

G4 passed 56/56 on its first run. A gate that has only ever passed is not validation; it has to be
shown capable of FAILING, and failing for the right reason. G4 exists because the predictor's old
behaviour -- silently returning 0.0 for a schedule form it could not parse -- turned a reader gap
into a -100 % error blamed on EnergyPlus. So the falsifier reproduces exactly that gap.

Perturbation: disable the Schedule:Year chain reader (make `yearly_daytype_means` return None for
everything), leaving the Schedule:Compact path untouched. That is the predictor as it stood when it
produced the 16 FAILs in job 1171607.

PREDICTIONS, written before running:
  P1  On `Default_NECB__Tall__CLG` (zero injection -- NO channel is a Schedule:Compact), G4 FAILs
      and itemises a NON-ZERO number of unreadable objects.
  P2  On the same cell G1 also FAILs, at about -100 % on every channel -- i.e. the old symptom is
      reproduced, not merely a different error.
  P3  On `Y2022__Tall__CLG` (all four channels injected -> all Schedule:Compact), G4 still PASSES
      with 0 unreadable, because nothing there depends on the year reader. If P3 fails, the
      perturbation is not surgical and P1/P2 prove nothing.

Any of the three landing the wrong way means G4 is not measuring what it claims.

    python falsify_g4.py <control_cell_dir> <injected_cell_dir>
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "dtv", os.path.join(HERE, "3rdJ_09H_daytype_volume_verify.py"))
dtv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dtv)


def probe(cell_dir):
    """(n_unreadable, {channel: sat err fraction}) for one cell under the CURRENT dtv module."""
    idf = None
    for n in sorted(os.listdir(cell_dir)):
        if n.endswith(".idf") and "injected" in n:
            idf = os.path.join(cell_dir, n)
            break
    pred, _dow, unreadable = dtv.predict_daytype(idf)
    return len(unreadable), pred, unreadable


def main():
    control, injected = sys.argv[1], sys.argv[2]

    print("=" * 86)
    print("BASELINE -- year reader ENABLED")
    print("=" * 86)
    for tag, d in (("control (zero injection)", control), ("injected (all 4 channels)", injected)):
        n, pred, _ = probe(d)
        print("  %-26s %-32s unreadable=%d  channels predicted>0: %s"
              % (tag, os.path.basename(d.rstrip("/\\")), n,
                 sorted(k for k, v in pred.items() if v["sat"] > 0)))

    print("")
    print("=" * 86)
    print("PERTURBED -- Schedule:Year chain reader DISABLED (the pre-fix predictor)")
    print("=" * 86)
    dtv.yearly_daytype_means = lambda idx, name: None

    n_ctrl, pred_ctrl, items = probe(control)
    print("  control  %-32s unreadable=%d" % (os.path.basename(control.rstrip("/\\")), n_ctrl))
    for u in items[:6]:
        print("      %s" % u)
    print("      channels still predicted>0: %s"
          % sorted(k for k, v in pred_ctrl.items() if v["sat"] > 0))
    p1 = n_ctrl > 0
    p2 = not [k for k, v in pred_ctrl.items() if v["sat"] > 0]

    n_inj, pred_inj, _ = probe(injected)
    print("  injected %-32s unreadable=%d" % (os.path.basename(injected.rstrip("/\\")), n_inj))
    print("      channels still predicted>0: %s"
          % sorted(k for k, v in pred_inj.items() if v["sat"] > 0))
    p3 = n_inj == 0

    print("")
    print("  [%s] P1  G4 FAILs on the control with a non-zero itemised count (got %d)"
          % ("PASS" if p1 else "FAIL", n_ctrl))
    print("  [%s] P2  the old symptom is reproduced: every channel back to 0.0 predicted"
          % ("PASS" if p2 else "FAIL"))
    print("  [%s] P3  the injected cell is UNAFFECTED -- perturbation is surgical (unreadable=%d)"
          % ("PASS" if p3 else "FAIL", n_inj))
    ok = p1 and p2 and p3
    print("")
    print("  G4 FALSIFIER: %s" % ("PASS -- the gate can fail, and fails for the stated reason"
                                  if ok else "FAIL -- G4 is not measuring what it claims"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
