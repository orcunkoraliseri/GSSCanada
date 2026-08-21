# -*- coding: utf-8 -*-
"""
4J / Step 7 -- RUN `G7.13` AGAINST THE REAL CORPUS.

WHY THIS EXISTS
===============
`4thJ_step7_indoor.py` has been 36/36 green since it was written, but every one
of those 36 assertions is a hand-built record. Its own docstring says so:
*"which has never been run against a corpus or a generated batch"*. A gate that
has only ever seen fixtures has not been shown to survive real data -- and
`FINDING 42` was a rule that passed everything except reality.

This module decodes all 73,254 Step 3 records through the SHIPPED decoder and
puts them through the SHIPPED gate. It adds no rule of its own.

WHAT IT REPORTS AND WHY EACH NUMBER IS THERE
============================================
  * the gate verdict on the whole corpus, and on each country separately,
    because `FINDING 53` established that anything country-correlated has to be
    read per fold or not at all;
  * the presence share, which is the number every downstream load depends on;
  * the four excluded activity codes, counted, so that "the exclusion list
    binds" is a measurement rather than a claim;
  * the at-home `000` episodes, which `D-S7-1 (c)` declared PRESENT and which
    the Step 7 validation doc quoted at 1,927 -- a figure this module can now
    confirm or refute against the corpus rather than repeat;
  * the PRE-REGISTERED PERTURBATION: the same corpus re-run with an exclusion
    list that differs by exactly one code, which `V7.c` requires to FAIL.

🔴 The perturbation is the only part of this that proves anything about the
gate. A pass on real data shows the gate runs; only the failure shows it binds.
"""

import io
import os
import sys
import json
import collections
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import encoder                                          # noqa: E402
import decoder                                          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    'indoor', os.path.join(HERE, '4thJ_step7_indoor.py'))
indoor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(indoor)

CORPUS = os.path.join(ROOT, 'Step3_docs', 'outputs_step3',
                      '4J_step3_corpus.jsonl')
STEP2 = os.path.join(ROOT, 'Step2_docs', 'outputs_step2')
COP_XWALK = os.path.join(STEP2, 'crosswalk_copresence.csv')


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def main():
    if not os.path.exists(CORPUS):
        sys.stderr.write('REFUSED: corpus not present at %s\n' % CORPUS)
        return 1
    bitpos = encoder.load_bit_positions(COP_XWALK)

    say('=== decoding the corpus through the SHIPPED decoder ===')
    by_country = collections.defaultdict(list)
    n = 0
    for ln in io.open(CORPUS, encoding='utf-8'):
        r = json.loads(ln)
        rec = decoder.decode_record(r['text'], bitpos)
        by_country[r['country']].append(rec)
        n += 1
    say('  %d records decoded, 0 refused' % n)

    allrecs = []
    for c in ('es', 'uk', 'it'):
        allrecs.extend(by_country[c])

    say('')
    say('=== G7.13 on the WHOLE corpus ===')
    res = indoor.gate_g7_13(allrecs, STEP2)
    say(indoor.report(res))

    say('')
    say('=== G7.13 per country (FINDING 53: read per fold or not at all) ===')
    for c in ('es', 'uk', 'it'):
        r = indoor.gate_g7_13(by_country[c], STEP2)
        say('  %s  records %6d  presence %.4f %%  at_home eps %8d  '
            'excluded %5d  null-act at home %5d  %s'
            % (c, r['n_records'], 100.0 * r['present_share'],
               r['n_at_home_episodes'], r['n_at_home_outdoor_episodes'],
               r['n_at_home_null_act_episodes'],
               'PASS' if r['passes'] else 'FAIL'))

    say('')
    say('=== PRE-REGISTERED PERTURBATION (V7.c): drop ONE code from the list ===')
    shipped, _ = indoor.load_outdoor_at_home(STEP2)
    dropped = sorted(shipped)[0]
    perturbed = frozenset(shipped) - {dropped}
    pres = indoor.gate_g7_13(allrecs, STEP2, outdoor=perturbed)
    say('  removed code %s from the caller\'s copy' % dropped)
    say('  verdict %s' % ('PASS' if pres['passes'] else 'FAIL'))
    for r in pres['reasons']:
        say('    - %s' % r)
    ok_pert = not pres['passes']

    say('')
    say('=== SECOND PERTURBATION: an all-at-home batch must FAIL as VACUOUS ===')
    flat = [{'episodes': [{'duration_min': 1440, 'act': '110',
                           'loc_class': 'at_home'}]} for _ in range(50)]
    vres = indoor.gate_g7_13(flat, STEP2)
    say('  verdict %s' % ('PASS' if vres['passes'] else 'FAIL'))
    for r in vres['reasons']:
        say('    - %s' % r)
    ok_vac = not vres['passes']

    say('')
    say('=== SUMMARY ===')
    say('  baseline on real data      %s' % ('PASS' if res['passes'] else 'FAIL'))
    say('  V7.c list perturbation     %s'
        % ('FAILED as required' if ok_pert else '*** PASSED -- gate is vacuous ***'))
    say('  vacuity perturbation       %s'
        % ('FAILED as required' if ok_vac else '*** PASSED -- guard is dead ***'))
    good = res['passes'] and ok_pert and ok_vac
    say('  G7.13 %s' % ('IS NOW SEEN PASSING ON REAL DATA AND FAILING TWICE'
                        if good else 'IS NOT ESTABLISHED'))
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
