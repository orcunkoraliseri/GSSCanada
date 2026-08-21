# -*- coding: utf-8 -*-
"""
4J / `G6.1` -- RUN THE RAKED-DONOR NULL ON A REAL FOLD.

WHAT IT DOES
============
`tools/4thJ_step6_rakeddonor.py` is the mechanism and its selftest proves the
mechanism. This is the thing that puts REAL diaries and REAL published marginals
through it, one fold at a time, and reports whether the null can be built at all.

🔴 IT DOES NOT SCORE ANYTHING. `G6.1` is "does the model beat the raked-donor
null", and there is no model output yet. What this answers is the question that
comes first and that nobody had asked: **can the null be CONSTRUCTED for this
fold?** A null that cannot be built is not a null the model beats; it is a gate
that cannot run.

WHERE THE TARGET MARGINALS COME FROM, AND WHY FROM THE POPULATION
=================================================================
From `population_<c>.csv`, not from `marginals_<c>.csv`. That is deliberate and
it is Guard 1 of `score_margin`: the model is prompted with prefixes drawn from
the synthetic population, so the null must be raked onto the same distribution
the model was asked to reproduce. Raking the null onto the raw published file
while the model sees the fitted population would be comparing two different
populations and calling the difference transfer.

The population IS the published marginals -- fitted, `D-S5-11`-relabelled and
integerised -- so nothing extra enters here.

THE TWO COLLAPSES, NEITHER OF WHICH IS PRE-REGISTERED
=====================================================
🔴 Both are required for the null to exist at all, and `prereg.md` is frozen and
mentions neither. They are declared here and owed to the author.

  `strat_hh_type: unknown -> other_complex`
      The 551 UK diaries of `D-S3-14`. No census anywhere publishes an `unknown`
      household category, so as donors into an `es` or `it` target they are
      orphans, and `FINDING 52` made an orphan a refusal rather than a silent
      zero. `other_complex` is the residual class, which is where an
      unclassifiable household belongs, but it is still a choice.

  `strat_econ_status: homemaker -> other_inactive`, `es` fold only
      `FINDING 51`: the Spanish census `RELA` has no *Labores del hogar*, so the
      `es` target has six bands and the donors carry seven.

WHAT IS REPORTED BESIDE CONVERGENCE
===================================
Effective sample size `(sum w)^2 / sum w^2`, the largest single donor weight,
and the largest share of the target any ONE diary ends up carrying. No gate
looks at any of these, and `FINDING 62` is the reason they are printed: a null
can converge inside tolerance and still rest on a few dozen diaries, which is a
weak null and therefore an easy one to beat.

USAGE
=====
    4thJ_step6_g61_rake_folds.py                 all three folds
    4thJ_step6_g61_rake_folds.py es              one fold
    4thJ_step6_g61_rake_folds.py --no-collapse   show the refusals instead
"""

import io
import os
import sys
import csv
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import importlib

rd = importlib.import_module('4thJ_step6_rakeddonor')

OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
CORPUS = os.path.join(ROOT, 'Step3_docs', 'outputs_step3',
                      '4J_step3_corpus.jsonl')

VARS = ['strat_age_band', 'strat_sex', 'strat_hh_type', 'strat_econ_status',
        'strat_day_type']
PFX = {'strat_age_band': 1, 'strat_sex': 2, 'strat_hh_type': 3,
       'strat_econ_status': 4, 'strat_day_type': 5}


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def target_from_population(c):
    p = os.path.join(OUT, 'population_%s.csv' % c)
    if not os.path.exists(p):
        raise SystemExit('missing %s -- run 4thJ_step5_synthesise.py first' % p)
    cnt = dict((v, collections.Counter()) for v in VARS)
    n = 0
    fh = io.open(p, encoding='utf-8')
    rdr = csv.DictReader(fh)
    for row in rdr:
        for v in VARS:
            cnt[v][row[v]] += 1
        n += 1
    fh.close()
    return dict((v, dict((k, x / float(n)) for k, x in cnt[v].items()))
                for v in VARS), n


def donors_for(c):
    out = []
    for ln in io.open(CORPUS, encoding='utf-8'):
        r = json.loads(ln)
        if r['country'] == c:
            continue
        f = r['text'].split('|', 1)[0].split(',')
        d = {'country': r['country']}
        for v in VARS:
            d[v] = f[PFX[v]]
        out.append(d)
    return out


def ess(weights):
    s1 = sum(weights)
    s2 = sum(w * w for w in weights)
    return (s1 * s1 / s2) if s2 > 0 else 0.0


# --------------------------------------------------------------------------
# 🔴 REGISTERED COLLAPSES -- `prereg_addendum_01.md`, 2026-08-21.
#
# `prereg.md` is frozen and cannot carry these; the author ruled (a) a dated
# sidecar addendum instead. The addendum is only worth anything if a fourth
# collapse cannot appear without somebody noticing, so this list is ENFORCED:
# the dict built below is checked against it and the rake REFUSES on anything
# unregistered, naming the pair.
#
# 🔴 There are THREE. Every note in the project said "both collapses" and
# named two; `C` is generated by the loop in `run()`, not written literally,
# and was found by reading this script's own output.
REGISTERED_COLLAPSES = {
    ('strat_hh_type', 'unknown', 'other_complex'):
        'A -- D-S3-14, 551 UK diaries, binds on es/it',
    ('strat_econ_status', 'homemaker', 'other_inactive'):
        'B -- D-S5-4 (b) / FINDING 51, 5584 donors, binds on es',
    ('strat_econ_status', 'unknown', 'other_inactive'):
        'C -- D-S5-11 (b), 68 UK diaries, binds on it',
}
ADDENDUM = 'Step6_docs/outputs_step6/prereg_addendum_01.md'


def check_registered(coll):
    """Return the list of (var, frm, to) triples the addendum does not name."""
    bad = []
    for var, mapping in (coll or {}).items():
        for frm, to in mapping.items():
            if (var, frm, to) not in REGISTERED_COLLAPSES:
                bad.append((var, frm, to))
    return sorted(bad)


def run(c, use_collapse=True):
    say('=== G6.1 raked-donor null, fold %s (donors = %s) ==='
        % (c, '+'.join(x for x in ('es', 'uk', 'it') if x != c)))
    tgt, n = target_from_population(c)
    don = donors_for(c)
    say('  target from population_%s.csv (%d persons, %d variables)'
        % (c, n, len(VARS)))
    say('  donor pool %d diaries' % len(don))

    coll = None
    if use_collapse:
        coll = {'strat_hh_type': {'unknown': 'other_complex'}}
        if 'homemaker' not in tgt['strat_econ_status']:
            coll['strat_econ_status'] = {'homemaker': 'other_inactive'}
        # a donor econ band the target lost entirely must go somewhere too
        for cat in set(d['strat_econ_status'] for d in don):
            if cat not in tgt['strat_econ_status'] and cat != 'homemaker':
                coll.setdefault('strat_econ_status', {})[cat] = 'other_inactive'
        say('  collapses (post-hoc, registered in %s): %s'
            % (ADDENDUM, json.dumps(coll, sort_keys=True)))
        unreg = check_registered(coll)
        if unreg:
            say('  !!! REFUSED: collapse(s) not registered in %s: %s'
                % (ADDENDUM,
                   '; '.join('%s: %s->%s' % t for t in unreg)))
            say('')
            return False
        for var, mapping in sorted(coll.items()):
            for frm, to in sorted(mapping.items()):
                say('      %s: %s -> %s   [%s]'
                    % (var, frm, to,
                       REGISTERED_COLLAPSES[(var, frm, to)]))

    try:
        res = rd.rake(don, tgt, c,
                      marginals_source='population_%s.csv|D-S5-11b' % c,
                      collapse=coll)
    except rd.RakeError as e:
        say('  !!! REFUSED: %s' % e)
        say('')
        return False

    w = res['weights']
    tot = sum(w)
    e = ess(w)
    top = max(w)
    # which country the heaviest diaries come from, and how much of the target
    # the single heaviest diary carries
    by_c = collections.Counter()
    for d, wi in zip(don, w):
        by_c[d['country']] += wi
    say('  CONVERGED in %d iterations, worst margin %.5f pp (tolerance %.2f pp)'
        % (res['iterations'], res['max_dev_pp'], rd.MARGIN_TOL_PP))
    say('  effective sample size %.0f of %d donors (%.1f %%)'
        % (e, len(don), 100.0 * e / len(don)))
    say('  heaviest single diary carries %.4f %% of the target'
        % (100.0 * top / tot))
    for k in sorted(by_c, key=lambda x: -by_c[x]):
        say('    donor country %s supplies %.3f %% of the raked weight'
            % (k, 100.0 * by_c[k] / tot))
    say('')
    return True


def main():
    argv = sys.argv[1:]
    use_collapse = '--no-collapse' not in argv
    argv = [a for a in argv if not a.startswith('--')]
    folds = argv if argv else ['es', 'uk', 'it']
    ok = [run(c, use_collapse) for c in folds]
    say('%d of %d folds can have their null BUILT.' % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == '__main__':
    sys.exit(main())
