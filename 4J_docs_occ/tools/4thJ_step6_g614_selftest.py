# -*- coding: utf-8 -*-
"""
SELFTEST for `G6.14` -- hour-support constancy (`4thJ_step6_g614_hoursupport.py`).

🔴 `G6.14` is a NEW gate, so it does not exist until it has been seen failing.
This file runs the registered perturbation and the two near-misses that do NOT
count as it, on the real corpus.

Run:  py -3 tools/4thJ_step6_g614_selftest.py [corpus.jsonl] [country]
"""

import os
import sys
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = importlib.import_module('4thJ_step6_g68_joint')
H = importlib.import_module('4thJ_step6_g614_hoursupport')

DEFAULT_CORPUS = os.path.join(os.path.dirname(HERE), 'Step3_docs',
                              'outputs_step3', '4J_step3_corpus.jsonl')
FAILS = []


def check(name, cond, detail=''):
    print('  %-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                           ('  -- ' + detail) if detail else ''))
    if not cond:
        FAILS.append(name)
    return cond


def truncate(recs, minutes):
    """Drop whatever runs past `minutes` -- an INCOMPLETE diary, which G6.14
    must REFUSE rather than score."""
    out = []
    for pref, eps in recs:
        used, keep = 0, []
        for e in eps:
            if used >= minutes:
                break
            take = min(e[0], minutes - used)
            keep.append((take,) + tuple(e[1:]))
            used += take
        if keep:
            out.append((pref, keep))
    return out


def main():
    corpus = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CORPUS
    country = sys.argv[2] if len(sys.argv) > 2 else 'it'
    print('=' * 74)
    print('G6.14 SELFTEST -- hour-support constancy')
    print('=' * 74)
    if not os.path.isfile(corpus):
        print('  !! corpus not found at %s' % corpus)
        return 1
    recs = G.load(corpus, country=country)
    print('diaries: %d (country %s)' % (len(recs), country))

    print('')
    print('1. BASELINE -- the D-S2-5 basis: origin 04:00, cyclic')
    ok, msg, sup = H.g6_14(recs)
    check('G6.14 PASSES and the support is EXACTLY flat', ok is True, msg)
    check('every one of the 144 slots has the full denominator',
          sup is not None and min(sup) == max(sup) == len(recs),
          'min %d max %d of %d diaries' % (min(sup), max(sup), len(recs)))

    print('')
    print('2. A ROTATION is wrong but is NOT this defect')
    ok0, msg0, sup0 = H.g6_14(recs, origin_minutes=0, cyclic=True)
    check('reading minute 0 as 00:00 leaves support untouched -> PASS',
          ok0 is True, msg0)
    print('       => the profile is four hours out of place and G6.14 cannot')
    print('          see it. G6.14 scores SUPPORT, not alignment; the alignment')
    print('          claim rests on D-S2-5, not on this gate. Recorded so the')
    print('          gate is never quoted for more than it detects.')

    print('')
    print('3. 🔴 THE REGISTERED PERTURBATION -- the 00:00-24:00 wall-clock frame')
    okp, msgp, supp = H.g6_14(recs, origin_minutes=H.DIARY_ORIGIN_MINUTES,
                              cyclic=False)
    check('G6.14 FAILS', okp is False, msgp)
    zeros = [i for i, s in enumerate(supp) if s == 0]
    check('support collapses to ZERO over exactly the first four hours',
          zeros == list(range(24)),
          '%d zero slots, first %d, last %d'
          % (len(zeros), zeros[0] if zeros else -1, zeros[-1] if zeros else -1))
    check('and nowhere else', min(supp[24:]) == max(supp[24:]) == len(recs))

    print('')
    print('4. The same perturbation, WITHIN each conditioning cell')
    rows = H.g6_14_by_cell(recs, G.ATTRIBUTE_PAIRS[0],
                           origin_minutes=H.DIARY_ORIGIN_MINUTES, cyclic=False)
    base = H.g6_14_by_cell(recs, G.ATTRIBUTE_PAIRS[0])
    check('every scored cell PASSES at baseline',
          bool(base) and all(r[1] is True for r in base),
          '%d cells' % len(base))
    check('every scored cell FAILS under the perturbation',
          bool(rows) and all(r[1] is False for r in rows),
          '%d cells' % len(rows))

    print('')
    print('5. INCOMPLETE diaries are REFUSED, not scored')
    okr, msgr, _ = H.g6_14(truncate(recs[:2000], 1000))
    check('G6.14 refuses input that does not sum to 1440', okr is None, msgr)
    print('       => an incomplete diary legitimately has a ragged denominator.')
    print('          That is FINDING 67s subject and at_home_mae_pp_covered')
    print('          measures it. G6.14 scores the BINNING and would otherwise')
    print('          fail for the generator`s reason, not the binner`s.')

    print('')
    print('=' * 74)
    if FAILS:
        print('🔴 %d CHECK(S) FAILED: %s' % (len(FAILS), '; '.join(FAILS)))
        return 1
    print('🟢 ALL CHECKS PASS -- G6.14 was SEEN FAILING under its registered')
    print('   perturbation, and seen NOT firing on a defect it does not cover.')
    print('=' * 74)
    return 0


if __name__ == '__main__':
    sys.exit(main())
