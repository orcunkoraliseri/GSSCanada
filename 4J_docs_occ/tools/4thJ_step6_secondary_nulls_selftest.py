# -*- coding: utf-8 -*-
"""
Selftest for `4thJ_step6_secondary_nulls.py` -- the two SECONDARY nulls of
Step 6 work item 6.2.

Every guard is SEEN FIRING on constructed state, and every arithmetic claim is
checked against a hand-computable answer rather than against the module's own
output. `feedback_gates_must_be_seen_failing`: a guard that has never been
watched refusing is not a guard.

    py -3 tools/4thJ_step6_secondary_nulls_selftest.py
"""

import io
import os
import sys
import json
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib

sn = importlib.import_module('4thJ_step6_secondary_nulls')

OK = [0]
BAD = [0]


def check(name, cond, extra=''):
    if cond:
        OK[0] += 1
        print('  ok   %s %s' % (name, extra))
    else:
        BAD[0] += 1
        print('  FAIL %s %s' % (name, extra))


def refuses(name, fn, must_say):
    try:
        fn()
    except sn.NullError as e:
        if must_say.lower() in str(e).lower():
            OK[0] += 1
            print('  ok   %s -- refused: %s' % (name, str(e)[:78]))
            return
        BAD[0] += 1
        print('  FAIL %s -- refused for the WRONG reason: %s' % (name, e))
        return
    BAD[0] += 1
    print('  FAIL %s -- DID NOT REFUSE' % name)


# --------------------------------------------------------------------------
# A tiny corpus with a hand-computable answer.
#
#   country  pid   day  age    sex     hh          econ       daytype  weight
#   uk       p1    1    25-34  female  one_person  employed   monday   3.0
#   uk       p2    1    25-34  male    one_person  employed   monday   1.0
#   it       p3    1    35-44  female  one_person  retired    sunday   4.0
#   es       p4    1    35-44  male    one_person  student    monday   2.0
#
# For held_out='es' the pool is {uk p1, uk p2, it p3}, total weight 8.0, so the
# normalised weights are 0.375 / 0.125 / 0.500 exactly.
ROWS = [
    ('uk', 'p1', '1', '25-34', 'female', 'one_person', 'employed', 'monday', 3.0),
    ('uk', 'p2', '1', '25-34', 'male', 'one_person', 'employed', 'monday', 1.0),
    ('it', 'p3', '1', '35-44', 'female', 'one_person', 'retired', 'sunday', 4.0),
    ('es', 'p4', '1', '35-44', 'male', 'one_person', 'student', 'monday', 2.0),
]


def write_corpus(path, rows=None):
    fh = io.open(path, 'w', encoding='utf-8')
    for c, pid, dd, age, sex, hh, econ, dt, _w in (rows or ROWS):
        text = '%s,%s,%s,%s,%s,%s|60,011,,at_home,0' % (c, age, sex, hh, econ, dt)
        fh.write(json.dumps({'country': c, 'pid': pid, 'hid': pid,
                             'diary_day': dd, 'split': 'train',
                             'text': text}) + '\n')
    fh.close()


def wtable(rows=None, drop=(), null=()):
    w, nulls = {}, set()
    for c, pid, dd, _a, _s, _h, _e, _d, wt in (rows or ROWS):
        k = (c.upper(), pid, dd)
        if k[1] in drop:
            continue
        if k[1] in null:
            nulls.add(k)
            continue
        w[k] = wt
    return w, nulls


TMP = tempfile.mkdtemp(prefix='4j_sn_')
CORPUS = os.path.join(TMP, 'corpus.jsonl')
write_corpus(CORPUS)


print('--- 1. the pool is N-1, and the arithmetic is exact')
w, nulls = wtable()
donors, ws, meta = sn.build_pooled('es', w, corpus=CORPUS, null_keys=nulls)
check('pool excludes the held-out country', meta['donor_countries'] == ['it', 'uk'],
      '-> %s' % meta['donor_countries'])
check('n donors', meta['n_donors'] == 3, '-> %d' % meta['n_donors'])
check('weights normalise to 1', abs(sum(ws) - 1.0) < 1e-12)
got = sorted(round(x, 12) for x in ws)
check('weights are the survey weights, renormalised',
      got == [0.125, 0.375, 0.5], '-> %s' % got)
check('null is NOT raked', meta['raked'] is False)
check('source label names the construction', 'NO raking' in meta['marginals_source'])

print('')
print('--- 2. shares are weighted, not counted')
# sex: female = p1 (0.375) + p3 (0.5) = 0.875 ; male = p2 = 0.125.
# An UNWEIGHTED pool would read 2/3 vs 1/3, so this separates the two.
sh = sn.shares(donors, ws, 'strat_sex')
check('weighted female share', abs(sh['female'] - 0.875) < 1e-12,
      '-> %.4f (unweighted would be 0.6667)' % sh['female'])
check('weighted male share', abs(sh['male'] - 0.125) < 1e-12, '-> %.4f' % sh['male'])

print('')
print('--- 3. the distance-to-target number, hand-checked')
tgt = {'strat_sex': {'female': 0.5, 'male': 0.5},
       'strat_age_band': {'25-34': 0.5, '35-44': 0.5},
       'strat_hh_type': {'one_person': 1.0},
       'strat_econ_status': {'employed': 1.0},
       'strat_day_type': {'monday': 1.0}}
rows = sn.worst_gap_pp(donors, ws, tgt)
# widest is econ: retired 50.0 % in the null vs 0.0 % in the target -> 50 pp.
check('worst gap is the econ column', rows[0][1] == 'strat_econ_status',
      '-> %s %s' % (rows[0][1], rows[0][2]))
check('worst gap is 50.0000 pp', abs(rows[0][0] - 50.0) < 1e-9,
      '-> %.4f pp' % rows[0][0])
check('gaps are sorted widest first',
      all(rows[i][0] >= rows[i + 1][0] for i in range(len(rows) - 1)))

print('')
print('--- 4. GUARD: a self-donor is refused')
refuses('held-out country present in its own pool',
        lambda: sn.load_donors('uk', corpus=CORPUS, restrict_to='uk'),
        'self-donor')

print('')
print('--- 5. GUARD: an unkeyed donor is NOT defaulted to 1.0')
w2, n2 = wtable(drop=('p1',))
refuses('donor missing from the weight table',
        lambda: sn.build_pooled('es', w2, corpus=CORPUS, null_keys=n2),
        'not keyed by the weight table')

print('')
print('--- 6. a NULL source weight is EXCLUDED and counted, not refused')
w3, n3 = wtable(null=('p1',))
d3, ws3, m3 = sn.build_pooled('es', w3, corpus=CORPUS, null_keys=n3)
check('kept 2 of 3', m3['n_donors'] == 2 and m3['n_donors_seen'] == 3,
      '-> %d of %d' % (m3['n_donors'], m3['n_donors_seen']))
check('exclusion is counted', m3['n_excluded_null_weight'] == 1)
check('remaining weights renormalise to 1', abs(sum(ws3) - 1.0) < 1e-12)
# 🔴 CHANGED BY D-S6-7 (a), 2026-08-22. Excluding p1 leaves ONE uk diary and
# ONE it diary, so under equal country mass they are 0.5 / 0.5. On the RAW
# survey weights this read 1.0/5.0 and 4.0/5.0 = 0.2 / 0.8; the ruling is what
# moves it, and this line is the smallest place where that is visible.
check('and are 0.5 / 0.5 under equal country mass (was 0.2 / 0.8 raw)',
      sorted(round(x, 12) for x in ws3) == [0.5, 0.5],
      '-> %s' % sorted(round(x, 12) for x in ws3))
check('the excluded donor is gone from the pool',
      all(d['pid'] != 'p1' for d in d3))

print('')
print('--- 7. GUARD: a zero-weight pool is not a distribution')
w4 = dict((k, 0.0) for k in w)
refuses('all weights zero',
        lambda: sn.weigh(donors, w4, nulls), 'not a distribution')

print('')
print('--- 7b. D-S6-7 (a): EQUAL COUNTRY MASS, every number hand-computed')
# The donors are, in corpus order, uk p1 / uk p2 / it p3.
# NOTE the toy weights of section 1 already give uk and it 4.0 each, so the
# ruling is INVISIBLE there -- that is a coincidence of the test data, and it is
# why this section drives the function with weights that are NOT balanced.
raw = [0.90, 0.09, 0.01]            # uk holds 99 % of the mass, it holds 1 %
eq = sn.equal_country_mass(donors, raw)
mraw = sn.country_mass(donors, raw)
check('BEFORE: one country holds 99 % -- FINDING 78 in miniature',
      abs(mraw['uk'] - 0.99) < 1e-12, '-> uk %.4f' % mraw['uk'])
meq = sn.country_mass(donors, eq)
check('AFTER: every donor country holds exactly 1/k',
      abs(meq['uk'] - 0.5) < 1e-12 and abs(meq['it'] - 0.5) < 1e-12,
      '-> %s' % dict((c, round(v, 6)) for c, v in meq.items()))
check('the null is still a distribution', abs(sum(eq) - 1.0) < 1e-12)
check('WITHIN a country the survey weights are preserved exactly '
      '(FINDING 53 depends on it)',
      abs(eq[0] / eq[1] - raw[0] / raw[1]) < 1e-12,
      '-> ratio %.6f, was %.6f' % (eq[0] / eq[1], raw[0] / raw[1]))
check('p1 is 0.9/0.99/2 exactly', abs(eq[0] - 0.9 / 0.99 / 2) < 1e-15,
      '-> %.9f' % eq[0])
check('a single-country null is untouched -- the scale factor cancels',
      sn.equal_country_mass([donors[2]], [1.0]) == [1.0])
refuses('a donor country carrying zero total weight',
        lambda: sn.equal_country_mass(donors, [0.5, 0.5, 0.0]),
        'cannot be renormalised')

# End to end: the ~10,000:1 scale artefact itself, through build_pooled.
w7 = {('UK', 'p1', '1'): 3000.0, ('UK', 'p2', '1'): 1000.0,
      ('IT', 'p3', '1'): 4.0}
d7, ws7, m7 = sn.build_pooled('es', w7, corpus=CORPUS, null_keys=set())
check('build_pooled APPLIES the ruling: a 1000x scale gap leaves the null '
      'identical to the equal-scale case',
      [round(x, 12) for x in ws7] == [0.375, 0.125, 0.5],
      '-> %s' % [round(x, 12) for x in ws7])
check('and the pooled null is 50/50, not 99.9/0.1',
      abs(sn.country_mass(d7, ws7)['uk'] - 0.5) < 1e-12)
check('the basis is recorded on the null', m7['pool_basis'] == sn.POOL_BASIS
      and m7['pool_basis_ref'] == sn.POOL_BASIS_REF,
      '-> %r' % m7['pool_basis_ref'])
check('and named in the source label, so it cannot be quoted as the old pool',
      'EQUAL COUNTRY MASS' in m7['marginals_source'])
_d8, _w8, m8 = sn.build_neighbour('es', w, neighbour='it', corpus=CORPUS,
                                  null_keys=nulls)
check('G6.2 carries NO pool basis -- it is ONE country, there is nothing to '
      'balance and nothing was changed',
      m8.get('pool_basis') is None and m8['null'] == 'G6.2')

print('')
print('--- 8. GUARD: G6.2 refuses an UNREGISTERED donor  (D-S6-6 (a))')
check('every fold is registered by the ruling',
      sorted(sn.REGISTERED_NEIGHBOURS) == ['es', 'it', 'uk'],
      '-> %r' % sorted(sn.REGISTERED_NEIGHBOURS))
check('and each fold registers BOTH donor countries, not one',
      all(len(sn.registered_donors(f)[0]) == 2 for f in ('es', 'uk', 'it')),
      '-> %s' % dict((f, sn.registered_donors(f)[0])
                     for f in ('es', 'uk', 'it')))
check('no fold registers itself as its own donor',
      all(f not in sn.registered_donors(f)[0] for f in ('es', 'uk', 'it')))
refuses('a fold the ruling does not cover',
        lambda: sn.build_neighbour('fr', w, corpus=CORPUS, null_keys=nulls),
        'registers no rule')
refuses('fold es, donor fr -- not in the registry',
        lambda: sn.build_neighbour('es', w, neighbour='fr', corpus=CORPUS,
                                   null_keys=nulls),
        'is not registered')

print('')
print('--- 8b. GUARD: with TWO donors registered, G6.2 REFUSES TO NOMINATE ONE')
print('        (this is the guard that IS the ruling: (a) removed the choice)')
for f in ('es', 'uk', 'it'):
    refuses('fold %s, no donor named' % f,
            lambda f=f: sn.build_neighbour(f, w, corpus=CORPUS,
                                           null_keys=nulls),
            'refuses to nominate')

print('')
print('--- 9. and it BUILDS one null PER REGISTERED DONOR  (the ruling path)')
reg = {'es': (('it',), 'TEST ONLY -- not an author ruling')}
d5, ws5, m5 = sn.build_neighbour('es', w, corpus=CORPUS, registry=reg,
                                 null_keys=nulls)
check('donor pool is the one country', m5['donor_countries'] == ['it'])
check('n donors', m5['n_donors'] == 1, '-> %d' % m5['n_donors'])
check('the single donor carries the whole null', abs(ws5[0] - 1.0) < 1e-12)
check('donor recorded in the source label', 'it' in m5['marginals_source'])
check('the label no longer claims a NEAREST neighbour',
      'nearest' not in m5['marginals_source'].lower(),
      '-> %r' % m5['marginals_source'])
built = sn.build_all_neighbours('es', w, corpus=CORPUS, null_keys=nulls,
                                registry={'es': (('it', 'uk'), 'TEST')})
check('build_all_neighbours returns ONE null per donor country',
      len(built) == 2, '-> %d' % len(built))
check('and they are different donor pools',
      [m['neighbour'] for _d, _ws, m in built] == ['it', 'uk'],
      '-> %s' % [m['neighbour'] for _d, _ws, m in built])
check('each is a distribution in its own right',
      all(abs(sum(_ws) - 1.0) < 1e-12 for _d, _ws, _m in built))
refuses('a registered donor that IS the held-out country',
        lambda: sn.build_neighbour('it', w, corpus=CORPUS,
                                   registry={'it': (('it',), 'x')},
                                   null_keys=nulls),
        'self-donor')

print('')
print('--- 9b. DIAGNOSTIC: country_mass, and FINDING 78 seen firing')
# uk p1 w=3, uk p2 w=1, it p3 w=4  ->  uk 4/8, it 4/8 on the es fold.
mm = sn.country_mass(donors, [3 / 8.0, 1 / 8.0, 4 / 8.0])
check('country mass is hand-computable', mm == {'uk': 0.5, 'it': 0.5},
      '-> %r' % mm)
mm2 = sn.country_mass(donors, [0.4995, 0.0005, 0.5])
check('and it tracks WEIGHT, not diary counts',
      abs(mm2['uk'] - 0.5) < 1e-12 and abs(mm2['it'] - 0.5) < 1e-12)
# The real defect: one country holding ~everything, which is what the live
# corpus does on the es and it folds because UK weights are scale-free.
mm3 = sn.country_mass(donors, [0.00005, 0.00005, 0.9999])
check('a 99.99 % one-country "pooled" null is over the flag',
      mm3['it'] > sn.POOL_DOMINANCE_FLAG_PP, '-> %.4f' % mm3['it'])
check('and a genuine 50/50 mix is not', max(mm.values()) <= sn.POOL_DOMINANCE_FLAG_PP)
# 🔴 Until D-S6-7 was ruled this section asserted that NOTHING is ever
# rescaled. That is no longer true -- (a) rescales by ruling -- so the claim is
# replaced by the one that still matters: the rescaling is unconditional, and
# the FLAG still repairs nothing. A basis that switches itself on when the
# numbers look bad would be a basis chosen after the fact.
SRC = io.open(sn.__file__, encoding='utf-8').read()
check('the equalisation is applied exactly once, in build_pooled',
      SRC.count('ws = equal_country_mass(kept, ws)') == 1)
_body = SRC.split('def build_pooled')[1].split('def registered_donors')[0]
check('and it is UNCONDITIONAL -- the dominance flag never triggers it',
      'POOL_DOMINANCE_FLAG_PP' not in _body and 'if ' not in _body.split(
          'ws = equal_country_mass')[0].split('kept = rp.pop')[1])

print('')
print('--- 10. GUARD: the weight field is the RULED one  (D-S6-4)')
refuses('an unknown weight field',
        lambda: sn.load_weight_table('weight_ind'), 'unknown weight field')

print('')
print('%d ok, %d FAILED' % (OK[0], BAD[0]))
sys.exit(1 if BAD[0] else 0)
