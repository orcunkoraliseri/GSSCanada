# -*- coding: utf-8 -*-
"""
4J / STEP 6, `G6.14` -- HOUR-SUPPORT CONSTANCY. NEW GATE, registered 2026-08-21.

🔴 THE GAP THIS FILLS, STATED PLAINLY.
Every battery we run is EPISODE-based: durations sum to 1440, round-trips are
exact, codes are legal, the 145-state tally automaton enforces the budget. **A
time-of-day table binned on the wrong origin passes every one of them**, because
the error is in SUPPORT PER SLOT, not in any total. `D-S2-5` set our origin to
04:00 cyclic, so we do not have the bug -- but nothing we run would tell us if
we reintroduced it, and that is the definition of an untested invariant.

THE GATE
--------
Wherever episodes are binned into a time-of-day profile, the number of
CONTRIBUTING DIARIES must be constant across all 144 slots, within whatever cell
is being conditioned on.

  threshold   support_min / support_max == 1.000 EXACTLY, over diaries whose
              durations sum to 1440
  provenance  🔴 PROJECT-CHOSEN. Nobody publishes this; it is a completeness
              invariant we are choosing to assert. It is not literature-derived
              and must never be cited as if it were.
  perturbation  bin one fold onto a 00:00-24:00 WALL-CLOCK FRAME instead of the
              cyclic 04:00 one. Support must collapse over the first four hours
              and the gate must FAIL. Measured: `it`, support 0 in slots 0-23,
              ratio 0.0000.

🔴 A ROTATION IS NOT THE DEFECT, AND THIS COST ONE RUN TO ESTABLISH.
Reading the diary's minute 0 as wall-clock 00:00 -- i.e. `--origin 0` -- is a
ROTATION of the axis. It puts every profile four hours out of place and it is
wrong, but every slot keeps its full denominator and `G6.14` correctly PASSES:
measured on `it`, 38260/38260 = 1.0000. The defect this gate is for is the FRAME
error: the diary runs 04:00 -> 28:00, it is placed at its true wall-clock time,
and the part past midnight is DROPPED instead of wrapped -- so 00:00-04:00 is
supported by nothing. That is `--origin 240 --no-cyclic`, which is what
`--perturb` runs. A gate whose perturbation does not fell it has not been shown
to work, and the first construction tried here did not fell it.

WHY EXACT EQUALITY IS THE RIGHT BAR HERE, AND WHERE IT DOES NOT APPLY
--------------------------------------------------------------------
On COMPLETE diaries -- every one of the 73,254 real ones sums to exactly 1440 --
a correct binning gives every slot the same denominator by construction, so any
departure at all is a defect and no tolerance is needed. 🔴 It does NOT apply to
GENERATED diaries, which routinely stop short (`sum_1440_frac` 0.05-0.135): there
the coverage curve is legitimately not flat, and that is `FINDING 67`'s subject,
measured by `at_home_mae_pp_covered`, not by this gate. **`G6.14` scores the
BINNING, not the generator.** A checker that pointed it at raw generated output
would fail for the wrong reason, so `assert_complete` is on by default and the
gate refuses rather than scores when the input is not complete.

Run:  py -3 tools/4thJ_step6_g614_hoursupport.py <corpus.jsonl> [country]
"""

import io
import os
import sys
import json
import argparse
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = importlib.import_module('4thJ_step6_g68_joint')

SLOT_MINUTES = G.SLOT_MINUTES
N_SLOTS = G.N_SLOTS

# `D-S2-5`, ruled 2026-08-16: the diary origin is 04:00 and the axis is CYCLIC.
DIARY_ORIGIN_MINUTES = 4 * 60
G614_SUPPORT_RATIO_MIN = 1.0          # exact; see the docstring


def hour_support(recs, origin_minutes=DIARY_ORIGIN_MINUTES, cyclic=True):
    """Per-slot count of diaries contributing to a wall-clock time-of-day bin.

    `origin_minutes` is the wall-clock time the diary's first episode starts at.
    With `cyclic=True` the day wraps, which is what `D-S2-5` specifies; with
    `cyclic=False` anything past midnight is DROPPED, which is the defect.
    """
    sup = [0] * N_SLOTS
    o = origin_minutes // SLOT_MINUTES
    for _, eps in recs:
        seen = set()
        slot = 0
        for e in eps:
            n = e[0] // SLOT_MINUTES
            for k in range(slot, slot + n):
                w = o + k
                if w >= N_SLOTS:
                    if not cyclic:
                        continue          # 🔴 the defect: the tail is dropped
                    w -= N_SLOTS
                if 0 <= w < N_SLOTS:
                    seen.add(w)
            slot += n
        for w in seen:
            sup[w] += 1
    return sup


def g6_14(recs, origin_minutes=DIARY_ORIGIN_MINUTES, cyclic=True,
          assert_complete=True):
    """-> (ok, message, support). `ok is None` means REFUSED, not scored."""
    if assert_complete:
        bad = sum(1 for _, eps in recs if sum(e[0] for e in eps) != 1440)
        if bad:
            return (None, 'REFUSED: %d of %d diaries do not sum to 1440. G6.14 '
                          'scores the BINNING and only complete diaries can '
                          'carry a constant denominator (see FINDING 67 for the '
                          'incomplete case)' % (bad, len(recs)), None)
    sup = hour_support(recs, origin_minutes, cyclic)
    lo, hi = min(sup), max(sup)
    if hi == 0:
        return False, 'no support anywhere -- nothing was binned', sup
    ratio = lo / float(hi)
    zeros = sum(1 for s in sup if s == 0)
    ok = (ratio >= G614_SUPPORT_RATIO_MIN)
    return (ok, 'support min %d / max %d = %.4f over %d slots%s'
            % (lo, hi, ratio, len(sup),
               '' if not zeros else ', %d slot(s) with ZERO support' % zeros),
            sup)


def g6_14_by_cell(recs, pair, **kw):
    """The gate within each conditioning cell -- the denominator must be
    constant WITHIN a cell, which is the form the external defect took."""
    out = []
    for key, group in sorted(G.cells_of(recs, pair).items()):
        if len(group) < G.MIN_CELL_N:
            continue
        ok, msg, _ = g6_14(group, **kw)
        out.append(('%s=%s x %s=%s' % (pair[0], key[0], pair[1], key[1]),
                    ok, msg, len(group)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--country')
    ap.add_argument('--origin', type=int, default=DIARY_ORIGIN_MINUTES)
    ap.add_argument('--no-cyclic', action='store_true',
                    help='drop what runs past midnight instead of wrapping')
    ap.add_argument('--perturb', action='store_true',
                    help='the REGISTERED perturbation: the 00:00-24:00 '
                         'wall-clock frame (origin 04:00, truncating). G6.14 '
                         'must FAIL under it.')
    ap.add_argument('--by-cell', action='store_true')
    args = ap.parse_args()
    if args.perturb:
        args.origin, args.no_cyclic = DIARY_ORIGIN_MINUTES, True

    recs = G.load(args.corpus, country=args.country)
    print('=' * 74)
    print('G6.14 -- HOUR-SUPPORT CONSTANCY  (origin %02d:%02d, %s)'
          % (args.origin // 60, args.origin % 60,
             'truncating' if args.no_cyclic else 'cyclic'))
    print('=' * 74)
    print('diaries        : %d%s' % (len(recs),
                                     '' if not args.country
                                     else '  (country %s)' % args.country))
    ok, msg, sup = g6_14(recs, args.origin, not args.no_cyclic)
    print('%-8s %s' % ({True: 'PASS', False: 'FAIL', None: 'REFUSED'}[ok], msg))
    if sup:
        print('support, every 12th slot: %s'
              % ' '.join(str(sup[i]) for i in range(0, N_SLOTS, 12)))
    if args.by_cell:
        print('')
        for pair in G.ATTRIBUTE_PAIRS:
            for label, cok, cmsg, n in g6_14_by_cell(
                    recs, pair, origin_minutes=args.origin,
                    cyclic=not args.no_cyclic):
                print('  %-52s %-7s n=%d' % (
                    label, {True: 'PASS', False: 'FAIL',
                            None: 'REFUSED'}[cok], n))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
