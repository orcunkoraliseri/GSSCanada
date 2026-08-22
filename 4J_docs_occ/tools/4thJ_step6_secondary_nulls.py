# -*- coding: utf-8 -*-
"""
4J / Step 6 work item 6.2 -- THE TWO SECONDARY NULLS.

`prereg.md` (FROZEN, md5 e4243e07cdd80c9c846b91f40e3e8c45) section 5 names three
nulls. One of them, the raked-donor null, is `G6.1`'s pre-registered BAR and is
built by `4thJ_step6_rakeddonor.py` + `4thJ_step6_g61_rake_folds.py`. The other
two were listed as "not built, still owed" at `Step6_docs/4thJ_06_transfer.md:881`
and this module is them:

    | Pooled all-country average diary  | weak     | secondary, reported | -> G6.3
    | Nearest-neighbouring-country model| moderate | secondary; answers  | -> G6.2
    |                                   |          | the geographic-     |
    |                                   |          | proxy objection     |

WHAT A NULL IS IN THIS PROJECT, AND WHY THAT MAKES THESE TWO CHEAP
==================================================================
`G6.1` established the shape: a null is a WEIGHTING over the real N-1 donor
diaries. The raked null solves for weights that reproduce the held-out country's
strata. These two do not solve for anything -- and that is exactly what makes
them weaker, on purpose:

    G6.3  every donor in the N-1 pool, at its OWN survey weight, each donor
          COUNTRY renormalised to equal mass (`D-S6-7` (a), ruled 2026-08-22).
          No raking. It ignores the held-out country's demographics completely.
    G6.2  the same, restricted to ONE donor country -- and by `D-S6-6` (a),
          ruled 2026-08-22, EVERY donor country in the fold's pool is built and
          reported, so there are TWO of them per fold and none is nominated.

🔴 THEY MUST NOT BE RAKED. A raked pooled null is the raked-donor null with a
different name, and reporting it as a second, independent null would be reporting
the same bar twice. `prereg.md` permits raking in exactly one place.

WEIGHT BASIS
============
`weight_dia_cal`, by `D-S6-4` (ruled 2026-08-21): Step 6 scores on the
calendar-week re-based diary weight, with `weight_dia` available as a DECLARED
SENSITIVITY and the two NEVER mixed. `FINDING 53` is why it matters here more
than anywhere: the three countries' raw diary weights hit three different day
bases (uk 71.45/14.32/14.24, es 50/25/25, it 33/33/33), so an unweighted pooled
null would be a null about weekends, unequally per fold.

🔴 THIS MODULE SCORES NOTHING. There is no model output yet. Like
`4thJ_step6_g61_rake_folds.py` before it, it answers the question that comes
first: can the null be CONSTRUCTED, and once built, HOW WEAK IS IT? The second
half is not decoration -- `FINDING 62` showed a null can be arithmetically
perfect and still rest on 68 diaries.

🟢 `D-S6-6` RULED (a) BY THE AUTHOR, 2026-08-22 -- see `REGISTERED_NEIGHBOURS`.
🟢 `D-S6-7` RULED (a) BY THE AUTHOR, 2026-08-22 -- see `POOL_BASIS`.
"""

import io
import os
import sys
import csv
import json
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import importlib

_g61 = importlib.import_module('4thJ_step6_g61_rake_folds')
_g68 = importlib.import_module('4thJ_step6_g68_joint')
_rd = importlib.import_module('4thJ_step6_rakeddonor')

FOLDS = ('es', 'uk', 'it')
VARS = _g61.VARS
PFX = _g61.PFX
OUT5 = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
OUT6 = os.path.join(ROOT, 'Step6_docs', 'outputs_step6')
CORPUS = _g61.CORPUS
HARMONISED = os.path.join(ROOT, 'Step2_docs', 'outputs_step2',
                          'harmonised.parquet')

# --------------------------------------------------------------------------
# 🟢 `D-S6-6` -- RULED (a) BY THE AUTHOR, 2026-08-22.
#
# THE PROBLEM. `prereg.md` section 5 names a "nearest-neighbouring-country
# model" and DEFINES NO RULE for picking the neighbour. It did not need one when
# it was written: the design then had FOUR countries including France, which
# borders both Spain and Italy, so every fold had an obvious neighbour. **Author
# decision 16 (2026-08-15) excluded France.** The pool per fold is now two
# countries, none of them a land-border neighbour of any fold, and the obvious
# repair -- nearest by great-circle distance -- was COMPUTED, not assumed, and
# does not survive: the `es` fold's answer FLIPS from `uk` (capitals) to `it`
# (centroids) and the basis is itself unregistered. See
# `IMP/docs/2026-08-22_D-S6-6_neighbour-null.md` section 4.
#
# THE RULING, (a). Build the single-donor-country null for EVERY country in the
# fold's pool -- two per fold, six in total -- and report them all. The word
# "nearest" is DROPPED. Nothing is nominated, so nothing is chosen after the
# fact; this removes a degree of freedom rather than registering one. It is the
# same logic `G6.9` already uses (compare against ALL the others, nominate
# none), and it is strictly more informative than any single pick: if the model
# merely mapped the held-out country onto one donor, the null for THAT donor is
# the one that becomes near-unbeatable, and reporting both is how a reader sees
# it.
#
# 🔴 IT IS A POST-REGISTRATION REINTERPRETATION of a pre-registered null's NAME
# -- not of its construction, its role, or any threshold -- declared as such in
# the addendum. It must never be presented as what section 5 said.
REGISTERED_NEIGHBOURS = {           # fold -> (donor countries, ruling reference)
    'es': (('it', 'uk'), 'D-S6-6 (a), author 2026-08-22'),
    'uk': (('es', 'it'), 'D-S6-6 (a), author 2026-08-22'),
    'it': (('es', 'uk'), 'D-S6-6 (a), author 2026-08-22'),
}
NEIGHBOUR_ADDENDUM = 'Step6_docs/outputs_step6/prereg_addendum_02.md'

# 🔴 `FINDING 78` / 🟢 `D-S6-7` -- RULED (a) BY THE AUTHOR, 2026-08-22.
#
# THE DEFECT. The three surveys' weights are not on one scale. `weight_dia_cal`
# sums to 1.6250e8 for ES and 1.6280e8 for IT -- national population GROSSING
# weights -- but to 15,919.8 for the UK, whose weights have mean 1.0043 and are
# SCALE-FREE. It is the same in every weight column, so it is a property of the
# SOURCE MICRODATA, not of `weight_dia_cal` and not of `D-S6-4`. Pooling the
# donors raw therefore weighted the countries by an arbitrary factor of ~10,000:
# `G6.3` carried 99.9902 % Italian mass on the `es` fold and 99.9902 % Spanish
# mass on the `it` fold, and on `es` it agreed with the `it`-ONLY null to four
# decimal places -- the same object under two names.
#
# THE RULING, (a). EQUAL COUNTRY MASS: each donor country's weights are
# renormalised to sum to 1.0 BEFORE the pool is formed, so every donor country
# contributes the same total mass and, WITHIN a country, the survey weights keep
# their exact relative values -- which is what `FINDING 53` requires, since
# `weight_dia_cal` is what corrects the three different day bases. This restores
# `G6.3` to a genuine all-country baseline instead of a duplicate of one `G6.2`.
# Declared cost: a Spanish diary then counts ~1.2x a UK diary within the null,
# because 15,852 UK and 19,140 Spanish diaries share the mass equally.
# See `IMP/docs/2026-08-22_D-S6-7_pooled-null-weight-scale.md`.
POOL_BASIS = 'equal country mass (each donor country renormalised to 1.0)'
POOL_BASIS_REF = 'D-S6-7 (a), author 2026-08-22'
POOL_BASIS_ADDENDUM = 'Step6_docs/outputs_step6/prereg_addendum_02.md'

# 🔴 A pooled null in which one country holds more than this share of the weight
# is not a pooled null. Under `D-S6-7` (a) this can no longer happen by
# construction (every country holds 1/k), so the flag is now a CHECK that the
# ruling was applied, not a description of the defect. It repairs nothing.
POOL_DOMINANCE_FLAG_PP = 0.90

# Source labels. `score_margin`'s Guard 1 refuses to compare two values whose
# `marginals_source` differs, which is what stops a pooled null being quoted
# against a raked null's number as though they were the same construction. 🔴 The
# neighbour label carries its donor country, so the two nulls of one fold can
# never be quoted against each other's number either.
SRC_POOLED = ('G6.3 pooled all-country average, EQUAL COUNTRY MASS (D-S6-7 (a): '
              'each donor country renormalised to 1.0 before pooling); NO '
              'raking; weight_dia_cal')
SRC_NEIGHBOUR = ('G6.2 single-donor-country null, donor %s (D-S6-6 (a): every '
                 'donor country reported, none nominated); NO raking; '
                 'weight_dia_cal')


class NullError(ValueError):
    pass


def say(*a):
    """🔴 Never let the CONSOLE ENCODING kill a run. Seen once, 2026-08-22: a
    cp1252 stdout raised UnicodeEncodeError on the last emoji line of `main()`,
    AFTER all six nulls were built and BEFORE `--json` was written, so a
    completed run produced no artefact and exit 1. The characters are replaced,
    the numbers never are."""
    s = ' '.join(str(x) for x in a) + '\n'
    try:
        sys.stdout.write(s)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, 'encoding', None) or 'ascii'
        sys.stdout.write(s.encode(enc, 'replace').decode(enc))


# --------------------------------------------------------------------------
def load_donors(held_out, corpus=None, restrict_to=None):
    """-> [donor dict]. Every corpus diary NOT from the held-out country.

    Guard 1: the held-out country is never a donor. `rake()` refuses this for
    `G6.1` and the reason is not raking-specific -- a self-donor makes any null
    unbeatable for the right reason and the claim unfalsifiable.
    """
    if restrict_to is not None and restrict_to == held_out:
        raise NullError('SELF-DONOR: the donor country %r is the held-out '
                        'country' % held_out)
    path = corpus or CORPUS
    out = []
    fh = io.open(path, encoding='utf-8')
    for ln in fh:
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        c = r['country']
        if c == held_out:
            continue
        if restrict_to is not None and c != restrict_to:
            continue
        f = r['text'].split('|', 1)[0].split(',')
        d = {'country': c, 'pid': r['pid'], 'diary_day': r['diary_day']}
        for v in VARS:
            d[v] = f[PFX[v]]
        out.append(d)
    fh.close()
    if not out:
        raise NullError('empty donor pool for held_out=%r restrict_to=%r'
                        % (held_out, restrict_to))
    seen = set(d['country'] for d in out)
    if held_out in seen:
        raise NullError('SELF-DONOR: held-out country %r is in its own donor '
                        'pool' % held_out)
    return out


def load_weight_table(field=None, parquet=None):
    """-> ({key: w}, {keys whose weight is NULL}).

    `_g68.load_weights` silently drops null-weight diaries, which makes a
    respondent the survey never weighted indistinguishable from a join that
    missed. Both are read here so `weigh()` can treat them differently -- the
    first is a declared exclusion, the second is a defect.
    """
    field = field or _g68.DEFAULT_WEIGHT_FIELD
    if field not in _g68.WEIGHT_FIELDS:
        raise NullError('unknown weight field %r; D-S6-4 ruled on %s'
                        % (field, ' and '.join(_g68.WEIGHT_FIELDS)))
    import pandas as pd
    path = parquet or HARMONISED
    df = pd.read_parquet(path, columns=['country', 'pid', 'diary_day', field])
    df = df.drop_duplicates(['country', 'pid', 'diary_day'])
    w, nulls = {}, set()
    for c, pid, dd, v in zip(df['country'], df['pid'], df['diary_day'],
                             df[field]):
        k = (str(c).upper(), str(pid), str(dd))
        if v != v or v is None:
            nulls.add(k)
        else:
            w[k] = float(v)
    return w, nulls


def weigh(donors, weights, null_keys=None):
    """-> ([w], report). Attaches `weight_dia_cal` to each donor.

    Guard 2, in two halves that must not be confused:

      * a donor whose weight is NULL IN THE SOURCE is EXCLUDED and counted.
        `G6.8` set that precedent (73,252 scored, 2 null excluded) and the two
        diaries in question -- `UK/12110816_2`, days 1 and 2 -- carry NaN in
        EVERY weight column, so this is a survey gap, not a `weight_dia_cal`
        artefact and not basis-dependent.
      * a donor the weight table does not key AT ALL is a join defect and is
        REFUSED. It does NOT silently become 1.0. `FINDING 52` is the
        precedent: a silent zero deleted 16.67 % of a pool and reported a
        residual of 5.6e-15.
    """
    null_keys = null_keys or set()
    ws, kept, excluded, unmatched = [], [], [], []
    for d in donors:
        k = (str(d['country']).upper(), str(d['pid']), str(d['diary_day']))
        w = weights.get(k)
        if w is not None:
            ws.append(float(w))
            kept.append(d)
        elif k in null_keys:
            excluded.append(k)
        else:
            unmatched.append(k)
    if unmatched:
        raise NullError('%d of %d donors are not keyed by the weight table at '
                        'all -- refusing to default them to 1.0 (first: %r)'
                        % (len(unmatched), len(donors), unmatched[0]))
    tot = sum(ws)
    if tot <= 0:
        raise NullError('total donor weight is %r -- not a distribution' % tot)
    ws = [w / tot for w in ws]
    return ws, {'n_donors': len(kept), 'n_donors_seen': len(donors),
                'n_excluded_null_weight': len(excluded),
                'n_unmatched': 0, 'kept': kept}


def shares(donors, ws, var):
    acc = collections.defaultdict(float)
    for d, w in zip(donors, ws):
        acc[d[var]] += w
    return dict(acc)


def target_shares(fold):
    """The held-out country's FITTED population -- the same target `G6.1` rakes
    onto, read the same way, so the two nulls' distances are comparable."""
    tgt, n = _g61.target_from_population(fold)
    return tgt, n


def worst_gap_pp(donors, ws, tgt):
    """How far this null sits from the population it is a null FOR, in pp.

    🔴 This is the number that says how weak the null is. The raked null is
    <= 0.5 pp on every variable BY CONSTRUCTION; an unraked null is not, and
    the gap is the thing `G6.2`/`G6.3` are secondary BECAUSE of.
    """
    rows = []
    for v in VARS:
        got = shares(donors, ws, v)
        keys = set(got) | set(tgt[v])
        for k in sorted(keys):
            rows.append((abs(got.get(k, 0.0) - tgt[v].get(k, 0.0)) * 100.0,
                         v, k, got.get(k, 0.0) * 100.0,
                         tgt[v].get(k, 0.0) * 100.0))
    rows.sort(reverse=True)
    return rows


def country_mass(donors, ws):
    """-> {country: share of the null's total weight}. Purely diagnostic.

    🔴 `FINDING 78`. Added 2026-08-22, after `D-S6-6` (a) put the per-country
    nulls beside the pooled one and they turned out to be THE SAME NULL on two
    folds of three. The three surveys' weights are not on one scale:
    `weight_dia_cal` sums to 1.625e8 for ES and 1.628e8 for IT -- national
    population grossing weights -- but to 15,919.8 for the UK, whose weights
    have mean 1.0043 and are SCALE-FREE. That is a property of the source
    microdata, not of anything built here. Pooling them raw therefore weights
    the countries by an arbitrary factor of ~10,000, and `G6.3` on the `es` and
    `it` folds is 99.99 % a ONE-COUNTRY null wearing a pooled label.
    🔴 This function does NOT repair it: the pooling basis is a BASIS CHOICE and
    belongs to the author (`D-S6-7`). It makes the composition impossible to
    miss, which the pooled null's own summary statistics did not.
    """
    tot = sum(ws)
    acc = collections.defaultdict(float)
    for d, w in zip(donors, ws):
        acc[d['country']] += w
    return dict((c, v / tot) for c, v in acc.items())


def equal_country_mass(donors, ws):
    """-> ws in which every donor COUNTRY holds the same total mass, 1/k.

    🟢 `D-S6-7` (a), ruled 2026-08-22. Each country's weights are divided by
    that country's own total, so the country totals become equal and the
    WITHIN-country relative weights are untouched to the last bit -- a diary
    that carried twice its neighbour's `weight_dia_cal` still does.

    🔴 It is NOT raking. Nothing is solved for, nothing looks at the held-out
    country's marginals, and no diary's weight is fitted to a target. It removes
    ONE arbitrary factor -- the national statistical office's choice to gross to
    the population or not -- and nothing else. The null is as weak as it was.

    Guard 5: a country with no mass cannot be renormalised. It would previously
    have been divided by zero into NaN and pooled silently, which is `FINDING
    52`'s failure mode exactly (a silent zero deleted 16.67 % of a pool and the
    report showed a residual of 5.6e-15).
    """
    tot = collections.defaultdict(float)
    for d, w in zip(donors, ws):
        tot[d['country']] += w
    for c in sorted(tot):
        if tot[c] <= 0:
            raise NullError('country %r carries total donor weight %r -- it '
                            'cannot be renormalised to equal country mass '
                            '(D-S6-7 (a)); refusing to divide by it' % (c, tot[c]))
    k = float(len(tot))
    out = [w / tot[d['country']] / k for d, w in zip(donors, ws)]
    s = sum(out)
    return [w / s for w in out]


def build_pooled(fold, weights, corpus=None, null_keys=None):
    donors = load_donors(fold, corpus=corpus)
    ws, rp = weigh(donors, weights, null_keys)
    kept = rp.pop('kept')
    # 🟢 `D-S6-7` (a). Applied UNCONDITIONALLY, by ruling -- never triggered by
    # the dominance flag. A basis that switches itself on when the numbers look
    # bad is a basis chosen after the fact.
    ws = equal_country_mass(kept, ws)
    return kept, ws, dict(rp, null='G6.3', marginals_source=SRC_POOLED,
                          raked=False, fold=fold, pool_basis=POOL_BASIS,
                          pool_basis_ref=POOL_BASIS_REF,
                          donor_countries=sorted(set(d['country']
                                                     for d in kept)))


def registered_donors(fold, registry=None):
    """-> (donor countries, ruling reference) for `fold`. REFUSES if unruled.

    Guard 3: an unregistered fold means no author ruling covers it, and `G6.2`
    would then be a null whose donor pool was chosen after the fact -- which is
    the defect `G6.2` exists to answer.
    """
    reg = REGISTERED_NEIGHBOURS if registry is None else registry
    if fold not in reg:
        raise NullError(
            'G6.2 REFUSES on fold %r: prereg.md names a '
            '"nearest-neighbouring-country model" but registers NO RULE for '
            'choosing the neighbour, and author decision 16 removed France, '
            'which was the obvious neighbour of two folds. Choosing one now '
            'is choosing a null\'s strength after the fact. See D-S6-6; the '
            'ruling belongs in %s.' % (fold, NEIGHBOUR_ADDENDUM))
    who, ref = reg[fold]
    if isinstance(who, str):
        who = (who,)
    return tuple(who), ref


def build_neighbour(fold, weights, neighbour=None, corpus=None,
                    registry=None, null_keys=None):
    """🔴 REFUSES unless the donor country is REGISTERED. See `D-S6-6` (a).

    Guard 4, and it is the whole point of the ruling: when a fold registers more
    than one donor country -- which under (a) is every fold -- this function
    will NOT pick one. Naming one implicitly is exactly the nomination (a)
    removed. Callers use `build_all_neighbours()`, which builds them all.
    """
    who, _ref = registered_donors(fold, registry)
    if neighbour is None:
        if len(who) != 1:
            raise NullError(
                'G6.2 REFUSES to nominate: fold %r registers %d donor '
                'countries (%s) and D-S6-6 (a) requires EVERY one of them to be '
                'built and reported. Name one explicitly, or call '
                'build_all_neighbours(). Reporting one of %d would be the '
                'nomination the ruling removed.'
                % (fold, len(who), ', '.join(who), len(who)))
        neighbour = who[0]
    elif neighbour not in who:
        raise NullError(
            'G6.2 REFUSES: neighbour %r for fold %r is not registered in %s '
            '(registered: %s). An unregistered neighbour is a null chosen '
            'after the fact.'
            % (neighbour, fold, NEIGHBOUR_ADDENDUM, ', '.join(who)))
    if neighbour == fold:
        raise NullError('SELF-DONOR: neighbour %r is the held-out country'
                        % neighbour)
    donors = load_donors(fold, corpus=corpus, restrict_to=neighbour)
    ws, rp = weigh(donors, weights, null_keys)
    kept = rp.pop('kept')
    return kept, ws, dict(rp, null='G6.2', neighbour=neighbour,
                          marginals_source=SRC_NEIGHBOUR % neighbour,
                          raked=False, fold=fold,
                          donor_countries=[neighbour])


def build_all_neighbours(fold, weights, corpus=None, registry=None,
                         null_keys=None):
    """-> [(donors, ws, meta)], one per REGISTERED donor country.

    `D-S6-6` (a): every donor country in the fold's pool is built and reported,
    none is nominated. This is the only caller-facing way to build `G6.2`.
    """
    who, _ref = registered_donors(fold, registry)
    return [build_neighbour(fold, weights, neighbour=n, corpus=corpus,
                            registry=registry, null_keys=null_keys)
            for n in who]


# --------------------------------------------------------------------------
def report(fold, donors, ws, meta, tgt, npop, top=6):
    say('')
    say('=== %s secondary null, fold %s (donors = %s) ==='
        % (meta['null'], fold, ', '.join(meta['donor_countries'])))
    say('    donors            %d of %d read  (%d excluded: null weight in '
        'the source)'
        % (meta['n_donors'], meta['n_donors_seen'],
           meta['n_excluded_null_weight']))
    say('    weight basis      weight_dia_cal   (D-S6-4, ruled)')
    say('    raked             NO   <- prereg permits raking for G6.1 only')
    e = _g61.ess(ws)
    say('    effective n       %.0f of %d  (%.1f %%)'
        % (e, len(ws), 100.0 * e / len(ws)))
    say('    heaviest diary    %.4f %% of the null'
        % (100.0 * max(ws)))
    if meta.get('pool_basis'):
        say('    pooling basis     %s   (%s)'
            % (meta['pool_basis'], meta['pool_basis_ref']))
    mass = country_mass(donors, ws)
    say('    donor mass        %s'
        % ('   '.join('%s %.4f %%' % (c, 100.0 * mass[c])
                      for c in sorted(mass))))
    if len(mass) > 1 and max(mass.values()) > POOL_DOMINANCE_FLAG_PP:
        dom = max(mass, key=mass.get)
        say('    🔴 FINDING 78 UNREPAIRED: this "pooled" null is %.2f %% %s. '
            'D-S6-7 (a) makes equal country mass unconditional, so this line '
            'means the ruling was NOT applied -- do not quote this null.'
            % (100.0 * mass[dom], dom))
    rows = worst_gap_pp(donors, ws, tgt)
    say('    target population %s (population_%s.csv, %d rows)' % (fold, fold, npop))
    say('    worst strata gap  %.4f pp   <- G6.1 is <= 0.5000 pp BY CONSTRUCTION'
        % rows[0][0])
    say('    the %d widest:' % top)
    for gap, v, k, got, want in rows[:top]:
        say('      %-9.4f pp  %-18s %-22s null %6.2f %%  vs  target %6.2f %%'
            % (gap, v, k, got, want))
    return {'fold': fold, 'null': meta['null'],
            'neighbour': meta.get('neighbour'),
            'donor_countries': meta['donor_countries'],
            'n_donors': meta['n_donors'],
            'n_donors_seen': meta['n_donors_seen'],
            'n_excluded_null_weight': meta['n_excluded_null_weight'],
            'n_unmatched': meta['n_unmatched'],
            'raked': False, 'weight_field': 'weight_dia_cal',
            'marginals_source': meta['marginals_source'],
            'pool_basis': meta.get('pool_basis'),
            'pool_basis_ref': meta.get('pool_basis_ref'),
            'donor_country_mass': mass,
            'pool_dominated_by': (max(mass, key=mass.get)
                                  if len(mass) > 1 and
                                  max(mass.values()) > POOL_DOMINANCE_FLAG_PP
                                  else None),
            'ess': e, 'ess_frac': e / float(len(ws)),
            'heaviest_diary_frac': max(ws),
            'worst_strata_gap_pp': rows[0][0],
            'worst_strata_gaps': [{'gap_pp': g, 'var': v, 'level': k,
                                   'null_pct': a, 'target_pct': b}
                                  for g, v, k, a, b in rows[:top]],
            'g61_gap_pp_by_construction': _rd.MARGIN_TOL_PP}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folds', nargs='*', default=None)
    ap.add_argument('--weight-field', default=_g68.DEFAULT_WEIGHT_FIELD)
    ap.add_argument('--harmonised', default=None)
    ap.add_argument('--json', default=None, help='write the report here')
    a = ap.parse_args()

    folds = a.folds or list(FOLDS)
    weights, null_keys = load_weight_table(a.weight_field,
                                          a.harmonised or HARMONISED)
    say('weight table: %d keys from %s (%d diaries carry a NULL weight and are '
        'EXCLUDED, not defaulted), field %s'
        % (len(weights), a.harmonised or HARMONISED, len(null_keys),
           a.weight_field))

    out = []
    for f in folds:
        tgt, npop = target_shares(f)
        donors, ws, meta = build_pooled(f, weights, null_keys=null_keys)
        out.append(report(f, donors, ws, meta, tgt, npop))
        try:
            who, ref = registered_donors(f)
            say('')
            say('--- G6.2, fold %s: %d donor countries registered (%s) by %s; '
                'ALL are built, none is nominated  [D-S6-6 (a)]'
                % (f, len(who), ', '.join(who), ref))
            for donors, ws, meta in build_all_neighbours(f, weights,
                                                         null_keys=null_keys):
                out.append(report(f, donors, ws, meta, tgt, npop))
        except NullError as e:
            say('')
            say('=== G6.2 secondary null, fold %s ===' % f)
            say('    🔴 REFUSED: %s' % e)
            out.append({'fold': f, 'null': 'G6.2', 'refused': str(e)})

    n62 = [r for r in out if r.get('null') == 'G6.2' and 'refused' not in r]
    say('')
    say('G6.3 built on %d fold(s). G6.2 built %d times over %d fold(s) -- '
        'D-S6-6 (a): every donor country reported, none nominated.'
        % (sum(1 for r in out if r.get('null') == 'G6.3' and 'refused' not in r),
           len(n62), len(set(r['fold'] for r in n62))))
    if n62:
        say('')
        say('    G6.2 per-donor-country nulls, worst strata gap vs the target:')
        for r in n62:
            say('      fold %-3s donor %-3s  %8d donors   ESS %5.1f %%   '
                'worst gap %8.4f pp'
                % (r['fold'], r['neighbour'], r['n_donors'],
                   100.0 * r['ess_frac'], r['worst_strata_gap_pp']))
    say('🔴 NOTHING HERE IS SCORED. There is no model output yet.')

    if a.json:
        io.open(a.json, 'w', encoding='utf-8').write(
            json.dumps(out, indent=2, sort_keys=True))
        say('wrote %s' % a.json)


if __name__ == '__main__':
    main()
