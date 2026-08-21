# -*- coding: utf-8 -*-
"""
4J / STEP 6 -- FIRST-ORDER INHOMOGENEOUS MARKOV COMPARATOR (`I-4`).

🔴 REPORTED ALONGSIDE `G6.1`. NEVER A FAIL CRITERION. `G6.5`'s FAIL criteria are
FROZEN in `prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) and this adds
nothing to them. The module refuses to emit a pass/fail verdict at all -- see
`compare_to_null()`.

WHY IT EXISTS
-------------
Our nulls are STRONGER than what the occupancy literature asks for: the
raked-donor null (`G6.1`) rakes real N-1 diaries onto the held-out country's own
published marginals, and the pooled average (`G6.3`) is the weak null we demoted.
Nothing is missing on rigour. **But the comparator a reviewer will name by
default is absent**: for a generative occupancy model the field's standard
baseline is a first-order INHOMOGENEOUS Markov chain fitted to the same
microdata -- Richardson et al. 2008, Widen & Wackelgard 2010, Wilke 2013. Adding
it makes the raked-donor null read as a deliberate strengthening rather than an
idiosyncratic choice.

Provenance: **category B, public literature.** The lineage above is public,
DOI-verified and cited. Nothing in the design is taken from any unpublished
source.

WHAT IS FITTED, AND THE THREE CHOICES THAT ARE OURS
---------------------------------------------------
1. **State space = the 10 HETUS Level-1 activities.** The published chains of
   this family use a small state space (Richardson: active/inactive occupancy;
   Widen: a handful of activity states). Our 159-symbol alphabet would need
   159 x 159 x 144 = 3.6M parameters against ~50k training diaries, which fits
   noise. Level-1 is also the basis every Tier 1 metric is already defined on,
   so the comparator is scored on exactly the quantities `G6.8` scores.
2. **Inhomogeneous in the 10-minute slot** -- P(j | i, t), t = 0..142 -- which is
   what "inhomogeneous" means in this lineage and is the whole point: a
   homogeneous chain cannot produce a diurnal profile.
3. **One chain per `strat_day_type`.** Weekday/weekend chains are standard in
   this literature. It is the only conditioning: the comparator is deliberately
   NOT given the demographic prefix the model gets, because a baseline handed
   the same conditioning is no longer a baseline -- it is a second model.

**Unseen transitions back off to the slot's own marginal**, not to an additive
constant. Additive smoothing would put a free parameter (alpha) into a baseline
whose whole value is having none.

Run:  py -3 tools/4thJ_step6_markov_comparator.py <corpus.jsonl> --fold it
"""

import io
import os
import sys
import json
import random
import argparse
import importlib
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = importlib.import_module('4thJ_step6_g68_joint')

SLOT_MINUTES = G.SLOT_MINUTES
N_SLOTS = G.N_SLOTS
DAY_TYPE = 'strat_day_type'

CITATION = ('Richardson, Thomson & Infield 2008; Widen & Wackelgard 2010; '
            'Wilke 2013 -- the published first-order inhomogeneous Markov '
            'lineage for occupancy and activity models.')


# ---------------------------------------------------------------------------
# fitting
# ---------------------------------------------------------------------------

def _slot_states(eps):
    """A diary -> 144 Level-1 states. Slots the diary never reaches are None."""
    out = [None] * N_SLOTS
    slot = 0
    for e in eps:
        n = e[0] // SLOT_MINUTES
        a = G.level1(e[1])
        for k in range(slot, min(slot + n, N_SLOTS)):
            out[k] = a
        slot += n
        if slot >= N_SLOTS:
            break
    return out


def fit(recs):
    """-> {day_type: {'init': {...}, 'trans': [ {i: {j: p}} x 143 ],
                      'marg': [ {j: p} x 144 ], 'n': int}}"""
    by = collections.defaultdict(list)
    for r in recs:
        by[r[0][DAY_TYPE]].append(_slot_states(r[1]))
    model = {}
    for dt, grids in by.items():
        init = collections.Counter()
        marg = [collections.Counter() for _ in range(N_SLOTS)]
        trans = [collections.defaultdict(collections.Counter)
                 for _ in range(N_SLOTS - 1)]
        for g in grids:
            if g[0] is not None:
                init[g[0]] += 1
            for k in range(N_SLOTS):
                if g[k] is not None:
                    marg[k][g[k]] += 1
            for k in range(N_SLOTS - 1):
                if g[k] is not None and g[k + 1] is not None:
                    trans[k][g[k]][g[k + 1]] += 1
        model[dt] = {
            'init': _norm(init),
            'marg': [_norm(m) for m in marg],
            'trans': [dict((i, _norm(c)) for i, c in t.items()) for t in trans],
            'n': len(grids),
        }
    return model


def _norm(counter):
    tot = float(sum(counter.values()))
    if tot <= 0:
        return {}
    return dict((k, v / tot) for k, v in counter.items())


# ---------------------------------------------------------------------------
# sampling
# ---------------------------------------------------------------------------

def _draw(dist, rng):
    r = rng.random()
    acc = 0.0
    for k, p in dist.items():
        acc += p
        if r <= acc:
            return k
    return list(dist)[-1] if dist else None


def sample_diary(model, day_type, rng):
    """-> episodes, exactly 1440 minutes by construction.

    A slot-driven sampler cannot produce a short day, so the comparator never
    suffers `FINDING 67`. Stated because it makes the comparison ASYMMETRIC in
    the comparator's favour on any coverage-sensitive statistic, and that has to
    be visible rather than quietly helpful.
    """
    m = model.get(day_type) or model[list(model)[0]]
    states = [None] * N_SLOTS
    states[0] = _draw(m['init'], rng)
    for k in range(N_SLOTS - 1):
        row = m['trans'][k].get(states[k])
        if not row:                      # BACKOFF: the slot's own marginal
            row = m['marg'][k + 1]
        states[k + 1] = _draw(row, rng)
    eps = []
    for s in states:
        if eps and eps[-1][1] == s:
            eps[-1] = (eps[-1][0] + SLOT_MINUTES, s)
        else:
            eps.append((SLOT_MINUTES, s))
    # back into the corpus's own 5-field episode shape. `act` is the Level-1
    # digit padded to three characters: the comparator has no finer resolution
    # and pretending otherwise would be a fabricated code.
    return [(d, '%s00' % s, '', 'unknown', '0') for d, s in eps]


def synthesise(model, like, rng):
    """One sampled diary per record in `like`, keeping its prefix and day type."""
    # D-S6-4: a synthesised diary inherits the weight of the real diary it was
    # drawn to stand in for, so the comparator and the corpus are scored on the
    # same population basis rather than one weighted and one not.
    return [(r[0], sample_diary(model, r[0][DAY_TYPE], rng), r[2]) for r in like]


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------

METRICS = ('diurnal_jsd_mean', 'budget_err_max_min', 'dwell_w1_max',
           'transitions_abs_err', 'transition_tvd')
LOWER_IS_BETTER = dict((m, True) for m in METRICS)


def score_against(real, cand):
    s = G.score_pair(real, cand, 'markov')
    return dict((m, s[m]) for m in METRICS)


def compare_to_null(comparator_values, null_values, marginals_source):
    """🔴 REPORTED, NEVER SCORED.

    `4thJ_step6_rakeddonor.score_margin` is deliberately NOT called here. It
    returns a `passes` boolean, and any boolean this module emitted would sooner
    or later be read as a verdict. `G6.5`'s FAIL criteria are frozen; this
    comparator is not one of them and must not acquire the shape of one.
    """
    out = {'marginals_source': marginals_source,
           'citation': CITATION,
           'is_fail_criterion': False,
           'reported_not_scored': True,
           'margins': {}}
    for m in METRICS:
        a, b = comparator_values.get(m), null_values.get(m)
        if a is None or b is None or a != a or b != b:
            continue
        # lower is better on every one of these, so a POSITIVE number means the
        # other side is closer to the real data than the Markov comparator is.
        out['margins'][m] = {'markov': a, 'other': b, 'markov_minus_other': a - b}
    return out


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--fold', required=True, choices=['es', 'uk', 'it'],
                    help='the HELD-OUT country; the chain is fitted on the '
                         'others and never sees this one')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--json-out')
    args = ap.parse_args()

    rng = random.Random(args.seed)
    print('=' * 74)
    print('FIRST-ORDER INHOMOGENEOUS MARKOV COMPARATOR -- fold %s' % args.fold)
    print('=' * 74)
    print('🔴 REPORTED ALONGSIDE G6.1, NEVER A FAIL CRITERION (G6.5 is frozen)')
    print('source: %s' % CITATION)

    allrecs = G.load(args.corpus)
    train = [r for r in allrecs if r[0]['country'] != args.fold]
    held = [r for r in allrecs if r[0]['country'] == args.fold]
    if not train or not held:
        raise SystemExit('!!! empty train or held-out set')
    seen = sorted(set(r[0]['country'] for r in train))
    if args.fold in seen:
        raise SystemExit('!!! the held-out country is in the training pool')
    print('')
    print('fitted on      : %s, %d diaries' % (', '.join(seen), len(train)))
    print('held out       : %s, %d diaries' % (args.fold, len(held)))

    model = fit(train)
    print('chains         : %s' % ', '.join(
        '%s (n=%d)' % (k, v['n']) for k, v in sorted(model.items())))
    npar = sum(len(t) * 10 for v in model.values() for t in v['trans'])
    print('parameters     : ~%d transition rows across %d chains'
          % (npar, len(model)))

    gen = synthesise(model, held, rng)
    print('sampled        : %d diaries, one per held-out record' % len(gen))
    vals = score_against(held, gen)
    print('')
    print('--- the comparator against the held-out country -------------------')
    for m in METRICS:
        print('  %-24s %10.4f' % (m, vals[m]))
    print('')
    print('🔴 Read with the asymmetry stated: the sampler emits exactly 1440')
    print('   minutes by construction, so it can never lose coverage the way a')
    print('   generated diary can. On any coverage-sensitive statistic this')
    print('   FAVOURS the comparator, and the comparison must say so.')

    out = {'fold': args.fold, 'trained_on': seen,
           'n_train': len(train), 'n_heldout': len(held),
           'seed': args.seed, 'citation': CITATION,
           'is_fail_criterion': False, 'reported_not_scored': True,
           'metrics': vals}
    if args.json_out:
        io.open(args.json_out, 'w', encoding='utf-8').write(
            json.dumps(out, indent=2, sort_keys=True))
        print('')
        print('wrote %s' % args.json_out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
