# -*- coding: utf-8 -*-
"""
SELFTEST for `G6.8`'s joint-structure checkers (`4thJ_step6_g68_joint.py`).

🔴 A gate that has never been seen to fall has not been shown to work. This file
runs the registered negative controls against the REAL corpus and asserts that
each one moves the arm it is supposed to move and leaves the other alone.

The registered controls (Overview, "Three negative controls, and the battery
must be seen failing on each before it is trusted"):

  | Control                | Must PASS                    | Must FAIL              |
  | shuffled diary         | Tier 1 marginals, budgets    | transitions, dwell     |
  | modal-collapse         | structural validity, marginals| diversity, variance    |

Run:  py -3 tools/4thJ_step6_g68_selftest.py [corpus.jsonl] [country]
"""

import io
import os
import sys
import math
import random
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = importlib.import_module('4thJ_step6_g68_joint')

DEFAULT_CORPUS = os.path.join(os.path.dirname(HERE), 'Step3_docs',
                              'outputs_step3', '4J_step3_corpus.jsonl')

FAILS = []


def check(name, cond, detail=''):
    print('  %-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                           ('  -- ' + detail) if detail else ''))
    if not cond:
        FAILS.append(name)
    return cond


def arms(ref, cand):
    s = G.score_pair(ref, cand, 'x')
    v = G.verdicts(s)
    seq = all(v[k] for k in G.SEQUENCE_ARM)
    mar = all(v[k] for k in G.MARGINAL_ARM)
    return s, v, seq, mar


def main():
    corpus = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CORPUS
    country = sys.argv[2] if len(sys.argv) > 2 else 'it'
    print('=' * 74)
    print('G6.8 SELFTEST -- registered controls against the real corpus')
    print('=' * 74)

    # ---- 1. the metric primitives, on cases with a closed form -------------
    print('')
    print('1. Metric primitives against analytic values')
    check('W1 between two point masses 10 and 30 is exactly 20',
          abs(G.wasserstein1([10.0] * 50, [30.0] * 50) - 20.0) < 1e-12,
          '%.6f' % G.wasserstein1([10.0] * 50, [30.0] * 50))
    check('W1 of a sample with itself is 0',
          G.wasserstein1([10.0, 30.0, 60.0], [10.0, 30.0, 60.0]) == 0.0)
    check('JSD of two disjoint supports is exactly 1 bit',
          abs(G.jsd_bits([1.0, 0.0], [0.0, 1.0]) - 1.0) < 1e-12)
    check('JSD of a vector with itself is 0',
          abs(G.jsd_bits([3.0, 1.0, 6.0], [3.0, 1.0, 6.0])) < 1e-12)
    check('TVD of two disjoint distributions is 1',
          abs(G.tvd({'a': 1.0}, {'b': 1.0}) - 1.0) < 1e-12)
    check('TVD of a distribution with itself is 0',
          G.tvd({'a': 0.4, 'b': 0.6}, {'a': 0.4, 'b': 0.6}) == 0.0)

    # ---- 2. the real corpus -----------------------------------------------
    print('')
    print('2. Loading the real corpus, country %s' % country)
    if not os.path.isfile(corpus):
        print('  !! corpus not found at %s -- structural checks skipped' % corpus)
        return 1 if FAILS else 0
    recs = G.load(corpus, country=country)
    check('corpus loaded and parses', len(recs) > 1000, '%d diaries' % len(recs))
    bad = sum(1 for r in recs if sum(e[0] for e in r[1]) != 1440)
    check('every real diary sums to exactly 1440 minutes', bad == 0,
          '%d exceptions' % bad)

    rng = random.Random(42)

    # ---- 3. the real-real floor: the battery must NOT fire on real data ----
    print('')
    print('3. REAL vs REAL split-half -- the null floor')
    a, b = G.split_half(recs, rng)
    s, v, seq, mar = arms(a, b)
    check('sequence arm PASSES on real-vs-real', seq,
          'dwell %.3f, trans %.3f, tvd %.4f'
          % (s['dwell_w1_max'], s['transitions_abs_err'], s['transition_tvd']))
    check('marginal arm PASSES on real-vs-real', mar,
          'budget %.3f min, JSD mean %.5f bits'
          % (s['budget_err_max_min'], s['diurnal_jsd_mean']))

    # ---- 4. 🔴 THE REGISTERED CONTROL --------------------------------------
    print('')
    print('4. 🔴 SHUFFLED DIARY, across-diary (the registered control)')
    sh = G.control_shuffled_across(recs, random.Random(7))
    s, v, seq, mar = arms(recs, sh)
    check('marginal arm PASSES -- and EXACTLY, by construction', mar
          and s['budget_err_max_min'] < 1e-9 and s['diurnal_jsd_mean'] < 1e-12,
          'budget %.9f min, JSD mean %.12f bits'
          % (s['budget_err_max_min'], s['diurnal_jsd_mean']))
    check('dwell-time arm is FELLED', not v['dwell_w1'],
          'W1 %.1f min against a %.1f min band'
          % (s['dwell_w1_max'], G.G68_DWELL_W1_MAX_MIN))
    check('transitions arm is FELLED', not v['transitions'],
          'error %.1f/day against a %.2f band (%.1f real vs %.1f shuffled)'
          % (s['transitions_abs_err'], G.G68_TRANSITIONS_MAX_ABS_ERR,
             s['transitions_ref'], s['transitions_cand']))
    check('transition-matrix TVD arm is FELLED', not v['transition_tvd'],
          '%.4f against a %.3f band'
          % (s['transition_tvd'], G.G68_TRANSITION_TVD_MAX))

    # ---- 5. the within-diary variant, and why it is NOT the control -------
    print('')
    print('5. SHUFFLED DIARY, within-diary -- built, reported, NOT the control')
    sw = G.control_shuffled_within(recs, random.Random(7))
    s2, v2, seq2, mar2 = arms(recs, sw)
    check('it fells the sequence arm too', not seq2)
    check('but it ALSO fells the diurnal marginal, so it cannot be the '
          'control the table describes', not v2['diurnal_jsd'],
          'JSD mean %.5f bits against a %.3f band'
          % (s2['diurnal_jsd_mean'], G.G68_DIURNAL_JSD_MEAN_MAX))
    print('       => "slots permuted, totals preserved" is ambiguous. Permuting')
    print('          a diary against ITSELF preserves that diary`s budget and')
    print('          destroys the population day-shape; permuting ACROSS diaries')
    print('          at a fixed slot preserves BOTH marginals exactly. Only the')
    print('          second satisfies "must PASS Tier 1 marginals".')

    # ---- 6. modal collapse: G6.8 is NOT the gate that catches it -----------
    print('')
    print('6. MODAL COLLAPSE -- reported, and the counterfactual stated')
    mc = G.control_modal_collapse(recs, random.Random(7))
    s3, v3, seq3, mar3 = arms(recs, mc)
    check('transitions/day survives modal collapse -- as it must, because a '
          'modal day is a REAL day', v3['transitions'],
          'error %.3f/day' % s3['transitions_abs_err'])
    print('       => G6.8 is not the collapse gate. Tier 2 (within-stratum')
    print('          variance ratio, unique-sequence fraction) is. Measured here')
    print('          so G6.8 is never quoted as evidence against collapse:')
    print('          dwell %s, TVD %s, budgets %s, diurnal %s.'
          % (v3['dwell_w1'], v3['transition_tvd'], v3['budgets'],
             v3['diurnal_jsd']))

    # ---- 7. the finite-sample floor -- FINDING 68 --------------------------
    print('')
    print('7. 🔴 FINDING 68 -- the absolute bands at CELL level')
    rows, skipped = G.score_conditioned(a, b, random.Random(42))
    band_fail = sum(1 for r in rows
                    if not all(r['verdicts'].values()))
    floor_fail = sum(1 for r in rows if r.get('floor_verdicts')
                     and not all(r['floor_verdicts'].values()))
    p1 = 1.0 / (G.FLOOR_REPEATS + 1)
    exp_cells = len(rows) * (1.0 - (1.0 - p1) ** len(G.FLOOR_KEYS))
    check('a SECOND REAL SAMPLE fails the absolute bands in most cells -- '
          'which is why the per-cell verdict is not taken on them',
          band_fail > 0.5 * len(rows),
          '%d of %d cells' % (band_fail, len(rows)))
    check('against the sample-size-matched floor the same real sample lands '
          'on its null expectation',
          abs(floor_fail - exp_cells) <= max(6.0, 0.5 * exp_cells),
          '%d of %d cells, null expects %.1f' % (floor_fail, len(rows),
                                                 exp_cells))

    # ---- 8. D-S6-4 -- DIARY WEIGHTS, ruled 2026-08-21 ---------------------
    print('')
    print('8. \U0001f7e2 D-S6-4 -- `weight_dia_cal` weighting')

    # (i) a constant weight changes NOTHING. This is the additivity claim, and
    #     it is checked on every registered statistic at once rather than on a
    #     convenient one.
    KEYS = ('dwell_w1_max', 'transitions_abs_err', 'transition_tvd',
            'budget_err_max_min', 'diurnal_jsd_mean', 'diurnal_jsd_max')
    w1 = [(r[0], r[1], 1.0) for r in a[:400]]
    w7 = [(r[0], r[1], 7.0) for r in a[:400]]
    c1 = [(r[0], r[1], 1.0) for r in b[:400]]
    c7 = [(r[0], r[1], 7.0) for r in b[:400]]
    s_one = G.score_pair(w1, c1, 'w=1')
    s_sev = G.score_pair(w7, c7, 'w=7')
    same = all(abs(s_one[k] - s_sev[k]) < 1e-9
               for k in KEYS if s_one[k] == s_one[k])
    check('a CONSTANT weight leaves every registered statistic unchanged -- '
          'the weight is a basis, not a scale', same,
          'checked on %d statistics, w=1 vs w=7' % len(KEYS))

    # (ii) a NON-constant weight must actually move something, or the wiring
    #      would be decorative. Weight the first half of the reference 10x.
    half = len(a[:400]) // 2
    skew = ([(r[0], r[1], 10.0) for r in a[:half]] +
            [(r[0], r[1], 1.0) for r in a[half:400]])
    s_skew = G.score_pair(skew, c1, 'skewed')
    moved = [k for k in KEYS
             if s_one[k] == s_one[k] and abs(s_one[k] - s_skew[k]) > 1e-9]
    check('a NON-constant weight moves the statistics -- the wiring is live, '
          'not decorative', len(moved) >= 4,
          '%d of %d statistics moved: %s' % (len(moved), len(KEYS),
                                             ', '.join(moved)))

    # (iii) the real join. `weight_dia_cal` is not in the corpus file at all --
    #       it is joined from harmonised.parquet on (COUNTRY, pid, diary_day).
    try:
        wt, wnull = G.load_weights('weight_dia_cal')
    except SystemExit as exc:
        wt, wnull = None, str(exc)
    if wt is None:
        print('  SKIP real weight join: %s' % wnull)
    else:
        check('the weight table keys the whole corpus',
              len(wt) >= 73000, '%d diaries keyed, %d null and excluded'
              % (len(wt), wnull))
        wrecs = G.load(corpus, country=country, weights=wt)
        d = G.load.last
        check('every real diary of this fold joined a weight',
              d['unmatched_no_pid'] == 0,
              '%d loaded, %d dropped unweighted, %d unkeyed'
              % (d['n'], d['dropped_unweighted'], d['unmatched_no_pid']))
        uw = G.load(corpus, country=country)
        bu = G.time_budgets(uw)
        bw = G.time_budgets(wrecs)
        worst = max(abs(bw.get(k, 0.0) - bu.get(k, 0.0))
                    for k in set(bu) | set(bw))
        check('the ruled weight actually re-bases the real time budgets -- '
              'reported so the size of D-S6-4 is visible, never as a threshold',
              worst > 0.0,
              'largest Level-1 budget shift %.2f min/day on fold %s'
              % (worst, country))

    print('')
    print('=' * 74)
    if FAILS:
        print('🔴 %d CHECK(S) FAILED: %s' % (len(FAILS), '; '.join(FAILS)))
        return 1
    print('🟢 ALL CHECKS PASS -- G6.8`s checkers were SEEN felling every arm the')
    print('   registered controls say they must fell, and leaving alone every arm')
    print('   they must not.')
    print('=' * 74)
    return 0


if __name__ == '__main__':
    sys.exit(main())
