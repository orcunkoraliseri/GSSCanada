# -*- coding: utf-8 -*-
"""
4J / Step 5.1 -- ITALY, from the ISTAT 2011 CENSUS 1% PUBLIC-USE MICRODATA SAMPLE.

WHY THIS FILE EXISTS AND WHAT IT IS *NOT*
=========================================
It is NOT a replacement for `4thJ_step5_build_it.py`. That builder produced
`marginals_it.csv` from FULL-COUNT published tables (ISTAT census-tract release
for the private-household base and the economic bands, Eurostat 2011 Census Hub
for single-year age, the sex split, the collective-quarters profile and
household type). Those are exact counts. This file does something the published
tables cannot do at all, and it MEASURES two things that were previously only
BOUNDED.

It answers, with data instead of an assumption:

  D-S5-8  `strat_hh_type` is published on a HOUSEHOLD base, but the rake donors
          are PERSONS. `uk` converts exactly and `es` is derivable; ITALY was
          NOT derivable from any published table, because an Italian *nucleo
          familiare* is not a household and the published person-by-household-
          type cross-tabulation does not exist. In the microdata every person
          carries their own household's type, so the person-basis marginal is a
          direct tabulation and needs NO conversion, NO mean-household-size
          assumption and NO third declared basis.

  D-S5-7  `strat_econ_status` for Italy sits on ALL RESIDENTS 15+, while D-S5-5
          requires PRIVATE-HOUSEHOLD residents. There is no published Italian
          residence-type x activity table, so the effect was BOUNDED at 0.44 pp
          and accepted. Here it is MEASURED: both universes are tabulated from
          the same records and differenced.

WHAT THE SOURCE IS
==================
`CensPop2011_1%` -- ISTAT, 15th General Population and Housing Census (2011),
public-use 1 per cent sample. National statistical office, so it is inside
D-S5-1 route 3; Eurostat is not involved in anything this module emits.

    individuals file  CensPop2011_1__Microdati_Anno_2011_individui.txt
    md5               9f3ae2f2f9022e7e73ccd3107c0aa7a9
    594,247 person records, tab-delimited, header row, latin-1
    NO WEIGHT COLUMN -- the sample is self-weighting; the expansion factor is
    exactly 100 and is applied as such.

>>> ISTAT'S OWN CAVEAT, QUOTED FROM `!Leggimi.html`, AND IT IS THE REASON THIS
>>> MODULE DOES NOT OVERWRITE ANY FULL-COUNT FIGURE:
>>>   "a causa del trattamento dei dati per la tutela della riservatezza, le
>>>    elaborazioni effettuate sui file ad uso pubblico possono condurre a
>>>    risultati in qualche misura difformi rispetto a quelli pubblicati"
>>> Disclosure control is applied to the public file, so its tabulations can
>>> differ from the published ones. Combined with 1% sampling error this puts a
>>> floor of a few tenths of a percentage point under everything below.

THE ONE THING IT CANNOT DO
==========================
`ETA_CLASSI` bottoms out at "0-14". The `11-14` band is TRAPPED inside it and
cannot be recovered here at any price. `11-14` therefore keeps the derivation
already in `marginals_it.csv`, and this module refuses to emit an age marginal
at all rather than emit a 15+ one that looks like the full thing.

TWO PUBLISHED-LABEL DEFECTS, AGAIN
==================================
`TIPOLOGIA_FAM`'s classification page lists 13 modalities whose text reads as a
hierarchy (1 "Famiglie senza nuclei" with 2 "Non in coabitazione" and 3 "In
coabitazione" beneath it; 4 "Famiglie con un solo nucleo" with 5-12 beneath it;
13 "due o piu' nuclei"). THE DATA DO NOT MATCH THAT READING. Cross-tabulated
against `NROCOMPO` and against the presence of a spouse/partner and of children:

    tf 1, 2, 3   ALL have exactly 1 component, no couple, no children.
                 Together they are 76,391 households = EXACTLY the count of
                 NROCOMPO == 1. They are one-person households, all three.
    tf 4         2+ persons, no couple, mostly no children -> a family with NO
                 nucleus, which the label assigns to code 1's branch.
    tf 5         exactly 2.00 persons/household, couple, no children.
    tf 6         3.66 persons/household, couple, children.
    tf 7, 8      lone mother / lone father with children.
    tf 9-12      the same four nucleus forms PLUS other resident persons.
    tf 13        5.17 persons/household, two or more nuclei.

So the modality numbers are offset from the descriptive text by one branch
header. Same class as FINDING 47, FINDING 56 (`P139` in ISTAT's own tracciato)
and the `F_red_htr` unit in TABULA: a published label that contradicts its own
values. The mapping below is therefore keyed on the CODE whose behaviour was
verified, and the verification is re-run as a refusal every time this module
executes.

WHY THE NUCLEUS-CODE MAPPING AND NOT A COMPOSITION MAPPING
==========================================================
Two candidate ways of reading `TIPOLOGIA_FAM` were built and both were scored
against the Eurostat household-basis counts already carried in
`marginals_it.csv` -- a real test, because those counts come from a different
route and are a full count.

    reading                       max |deviation| over the five categories
    nucleus code (tf)                       1.49 %   (four of five under 1 %)
    composition (REL_PAR presence)         71.90 %

The composition reading collapses because it cannot tell "couple + children"
from "couple + children + grandmother". The nucleus-code reading is adopted, and
its agreement is ALSO an independent validation of the household-basis Eurostat
mapping used by the other builder, obtained without using Eurostat.

>>> CONVENTION A vs CONVENTION B, WHICH IS A DIFFERENT QUESTION AND THE HARDER ONE
>>> ==============================================================================
>>> Reading the codes correctly still leaves a choice about where a household
>>> that holds a family nucleus PLUS other resident people (`tf` 9-12) belongs.
>>>
>>>   CONVENTION A  -> other_complex.        ONS (uk), INE (es)
>>>   CONVENTION B  -> keeps its nucleus.    Eurostat (and so marginals_it.csv)
>>>
>>> This module SCORES B (that is how we know Eurostat is on B) and EMITS A.
>>>
>>> A is forced, not preferred. `QS112UK` publishes "Other household types" as
>>> one indivisible class, so the UK cannot be put on B by any means. A is the
>>> only convention the three folds can share, and raking three folds onto
>>> marginals built by different rules would confound the classification
>>> difference with the leave-one-country-out signal itself -- the same argument
>>> that kept `FINDING 57` on TABULA's EU boundary conditions.
>>>
>>> The corroboration: under A, `couple_no_children` has a mean size of EXACTLY
>>> 2.0000 persons per household here and in Spain, and 2.0022 in the UK. Under
>>> B, Italy reads 2.0794 -- the class is carrying somebody who is not in the
>>> couple. Two people is what a childless couple is.
>>>
>>> WHAT IT COSTS: 7.222 % of Italian persons and 4.446 % of Italian households
>>> move, and `other_complex` goes from 5.62 % to 12.84 % of persons. Large, and
>>> printed on every run rather than buried.
>>>
>>> WHAT IT NO LONGER LEAVES OPEN: `marginals_it.csv`'s HOUSEHOLD-basis rows
>>> were Eurostat's and therefore on B, so Italy's two bases disagreed. That was
>>> raised as `D-S5-9` and RULED (a) on 2026-08-21: this module now also emits
>>> the household-basis table on convention A, from the same records, and
>>> `4thJ_step5_apply_ds59.py` patches `marginals_it.csv` from it.
>>>
>>> THE PRICE, WHICH IS REAL: those five rows stop being a full count. They
>>> become a 1 % sample estimate whose accuracy is bounded by the SAME 1.49 %
>>> like-for-like score above -- the deviation of this sample, on convention B,
>>> from the Eurostat full count on convention B. That number is not a guess and
>>> it is not asserted; it is recomputed and printed on every run, and the module
>>> refuses if it exceeds 3 %.

OUTPUTS
=======
  outputs_step5/hhtype_person_it.csv     person-basis household type, private
                                         households, Italy. NEW -- this field did
                                         not exist on a person basis before.
  outputs_step5/hhtype_household_it.csv  household-basis household type on
                                         CONVENTION A (D-S5-9a). Replaces the
                                         Eurostat convention-B rows that
                                         marginals_it.csv carried.
  outputs_step5/econ_basis_check_it.csv  the D-S5-7 measurement: private-household
                                         15+ vs all-resident 15+, same records,
                                         plus the same-universe comparison against
                                         the full-count tract table that separates
                                         sampling noise from the basis effect.

WHAT THE MEASUREMENT SAYS, AND IT DOES NOT POINT THE WAY IT WAS ASSUMED TO
==========================================================================
The private-household restriction moves the economic shares by AT MOST 0.178 pp
(employed +0.178, retired -0.177, other_inactive -0.127 -- collective quarters
in Italy are overwhelmingly care homes, so they hold retired and other-inactive
people, exactly the expected sign). The 0.44 pp bound was correct but loose.

BUT the SAME microdata, tabulated on the SAME universe as the published tract
table (all residents 15+), deviates from it by up to 0.207 pp. That is sampling
error plus ISTAT's disclosure control, and IT IS LARGER THAN THE BASIS EFFECT IT
WOULD CORRECT. Replacing the full-count economic marginal with the microdata one
would trade a 0.178 pp known, signed bias for a 0.207 pp unsigned random error.
So this module DOES NOT REWRITE `econ_11plus_it.csv`. It emits the measurement,
and the recommendation that follows from it is to keep the full count and
declare the basis effect as MEASURED rather than bounded.
"""

import io
import os
import sys
import collections
import csv
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MICRO = os.path.join(
    ROOT, 'Datasets',
    'CensPop2011_1%_2011_IT-20260821T110923Z-1-001', 'CensPop2011_1__2011_IT',
    'MICRODATI', 'CensPop2011_1__Microdati_Anno_2011_individui.txt')
OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
MICRO_MD5 = '9f3ae2f2f9022e7e73ccd3107c0aa7a9'
EXPANSION = 100          # self-weighting 1 % sample

CATS = ['one_person', 'couple_no_children', 'couple_with_children',
        'single_parent_with_children', 'other_complex', 'unknown']
ECON_BANDS = ['employed', 'unemployed', 'student', 'retired',
              'homemaker', 'other_inactive', 'unknown']

# COND_PROF -> our six bands. 2 "in cerca di prima occupazione" and 3
# "disoccupata (in cerca di nuova occupazione)" are both unemployment; the
# corpus has no first-job distinction to receive it.
ECON_MAP = {'1': 'employed', '2': 'unemployed', '3': 'unemployed',
            '4': 'retired', '5': 'student', '6': 'homemaker',
            '7': 'other_inactive'}

# TIPOLOGIA_FAM -> our five categories. Keyed on the code, whose behaviour is
# re-verified below; NOT on the classification page's text, which is offset.
#
# TWO mappings, and both are used, for different purposes.
#
# TF_EUROSTAT is CONVENTION B: a household holding a nucleus PLUS other resident
# people (tf 9-12) keeps its nucleus's type. It is NOT emitted. It exists only to
# be scored against the Eurostat household counts already in marginals_it.csv,
# which is how we know Eurostat is on convention B.
TF_EUROSTAT = {'1': 'one_person', '2': 'one_person', '3': 'one_person',
               '4': 'other_complex',        # family with NO nucleus, 2+ persons
               '5': 'couple_no_children', '9': 'couple_no_children',
               '6': 'couple_with_children', '10': 'couple_with_children',
               '7': 'single_parent_with_children',
               '8': 'single_parent_with_children',
               '11': 'single_parent_with_children',
               '12': 'single_parent_with_children',
               '13': 'other_complex'}       # two or more nuclei
#
# TF_MAP is CONVENTION A, and it is what this module EMITS: a nucleus plus other
# people goes to other_complex. The UK cannot express B at all (ONS publishes
# "Other household types" as one indivisible class), so A is the only basis the
# three folds can share -- and under A `couple_no_children` comes out at exactly
# 2.00 persons per household in all three countries, which is what a childless
# couple actually is.
TF_MAP = dict(TF_EUROSTAT)
for _t in ('9', '10', '11', '12'):
    TF_MAP[_t] = 'other_complex'

# Full-count household counts already carried by marginals_it.csv (Eurostat
# cens_11htts_r2). Used ONLY to score the mapping, never copied into an output.
EURO_HH = {'one_person': 7641106, 'couple_no_children': 4968407,
           'couple_with_children': 8532394,
           'single_parent_with_children': 2438716, 'other_complex': 1002567}
# Full-count economic shares already carried by marginals_it.csv (ISTAT tracts,
# ALL RESIDENTS 15+). Used ONLY to size the sampling+disclosure noise.
TRACT_ECON = {'employed': 0.450379, 'unemployed': 0.058063, 'student': 0.073108,
              'retired': 0.248051, 'homemaker': 0.113936,
              'other_inactive': 0.056463}
# Published collective-quarters population, ISTAT 2011.
PUB_CONVIVENZE = 301699
# Published private households, Eurostat cens_11htts_r2 total.
PUB_HOUSEHOLDS = 24583190


class BuildError(Exception):
    pass


def need(cond, msg):
    """Refuse rather than warn. A marginal that is quietly wrong is worse than
    no marginal, because the rake will happily converge onto it."""
    if not cond:
        raise BuildError(msg)


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def md5(path):
    h = hashlib.md5()
    fh = open(path, 'rb')
    try:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    finally:
        fh.close()
    return h.hexdigest()


KEEP = ('ID_FAM', 'TIPCONV', 'TIPOLOGIA_FAM', 'NROCOMPO', 'REL_PAR',
        'SESSO', 'ETA_CLASSI', 'COND_PROF')


def load():
    need(os.path.exists(MICRO), 'microdata file absent: %s' % MICRO)
    got = md5(MICRO)
    need(got == MICRO_MD5,
         'microdata md5 is %s, expected %s. Every number in this module and in '
         'the provenance file was measured on the pinned file; a different file '
         'must be re-measured, not re-labelled.' % (got, MICRO_MD5))
    f = io.open(MICRO, encoding='latin-1')
    hdr = [h.strip() for h in f.readline().rstrip('\n').split('\t')]
    for c in KEEP:
        need(c in hdr, 'column %s absent from the microdata header' % c)
    ix = dict((h, i) for i, h in enumerate(hdr))
    persons = []
    ncol = len(hdr)
    for line in f:
        r = line.rstrip('\n').split('\t')
        need(len(r) == ncol,
             'a record has %d fields, header has %d -- the file is not the '
             'rectangular tab-delimited export this module assumes'
             % (len(r), ncol))
        persons.append(dict((c, r[ix[c]].strip()) for c in KEEP))
    f.close()
    return persons


def verify_tf_semantics(hh):
    """The classification page's text is offset from the codes (see docstring).
    Re-derive the semantics from the data, every run, and refuse if the file
    ever stops behaving the way the mapping assumes."""
    size = collections.defaultdict(list)
    couple = collections.Counter()
    kids = collections.Counter()
    for e in hh.values():
        size[e['tf']].append(e['n'])
        if e['rp'] & set(['2', '3']):
            couple[e['tf']] += 1
        if e['rp'] & set(['4', '5', '6']):
            kids[e['tf']] += 1
    for tf in ('1', '2', '3'):
        need(tf in size, 'TIPOLOGIA_FAM %s absent' % tf)
        need(set(size[tf]) == set([1]),
             'TIPOLOGIA_FAM %s is mapped to one_person, but it contains '
             'households of sizes %s. The code semantics changed.'
             % (tf, sorted(set(size[tf]))))
        need(couple[tf] == 0 and kids[tf] == 0,
             'TIPOLOGIA_FAM %s is mapped to one_person but carries couples or '
             'children.' % tf)
    need(set(size['5']) == set([2]),
         'TIPOLOGIA_FAM 5 is mapped to couple_no_children but is not uniformly '
         'two persons: sizes %s' % sorted(set(size['5'])))
    need(couple['5'] == len(size['5']) and kids['5'] == 0,
         'TIPOLOGIA_FAM 5 is mapped to couple_no_children but %d of %d have no '
         'couple and %d have children.'
         % (len(size['5']) - couple['5'], len(size['5']), kids['5']))
    need(couple['6'] > 0.99 * len(size['6']) and kids['6'] > 0.99 * len(size['6']),
         'TIPOLOGIA_FAM 6 is mapped to couple_with_children but only %d/%d '
         'carry a couple and %d/%d carry children.'
         % (couple['6'], len(size['6']), kids['6'], len(size['6'])))
    for tf in ('7', '8'):
        need(couple[tf] == 0,
             'TIPOLOGIA_FAM %s is mapped to single_parent_with_children but '
             '%d households carry a couple.' % (tf, couple[tf]))
    need(min(size['13']) >= 4,
         'TIPOLOGIA_FAM 13 is mapped to other_complex (two or more nuclei) but '
         'contains households as small as %d.' % min(size['13']))
    need(sorted(size.keys(), key=int) == [str(i) for i in range(1, 14)],
         'TIPOLOGIA_FAM takes codes %s; the mapping covers 1..13 exactly.'
         % sorted(size.keys(), key=int))
    say('  TIPOLOGIA_FAM semantics re-derived from the data and consistent with')
    say('  the mapping (the classification PAGE is not).')


def main():
    say('--- ISTAT CensPop2011 1% sample, individuals ---')
    persons = load()
    say('  md5 %s  records %d' % (MICRO_MD5, len(persons)))
    need(len(persons) == 594247,
         'expected 594,247 person records, got %d' % len(persons))

    coll = [p for p in persons if p['TIPCONV'] != '']
    priv = [p for p in persons if p['TIPCONV'] == '']
    need(len(coll) + len(priv) == len(persons),
         'private/collective split lost records')
    say('  collective-quarters persons %d -> %d (published %d, dev %+.3f %%)'
        % (len(coll), len(coll) * EXPANSION, PUB_CONVIVENZE,
           100.0 * (len(coll) * EXPANSION - PUB_CONVIVENZE) / PUB_CONVIVENZE))
    need(abs(len(coll) * EXPANSION - PUB_CONVIVENZE) < 0.02 * PUB_CONVIVENZE,
         'collective-quarters population from the sample is %d against a '
         'published %d -- more than 2 %% apart, so TIPCONV is not identifying '
         'the universe this module thinks it is.'
         % (len(coll) * EXPANSION, PUB_CONVIVENZE))

    # ---- households -------------------------------------------------------
    hh = {}
    for p in priv:
        k = p['ID_FAM']
        if k not in hh:
            hh[k] = {'tf': p['TIPOLOGIA_FAM'], 'nc': p['NROCOMPO'], 'n': 0,
                     'rp': set()}
        e = hh[k]
        need(e['tf'] == p['TIPOLOGIA_FAM'] and e['nc'] == p['NROCOMPO'],
             'household %s carries two different TIPOLOGIA_FAM/NROCOMPO values; '
             'ID_FAM is not a household key.' % k)
        e['n'] += 1
        e['rp'].add(p['REL_PAR'])
    say('  private households %d -> %d (published %d, dev %+.3f %%)'
        % (len(hh), len(hh) * EXPANSION, PUB_HOUSEHOLDS,
           100.0 * (len(hh) * EXPANSION - PUB_HOUSEHOLDS) / PUB_HOUSEHOLDS))
    capped = [e for e in hh.values() if int(e['nc']) >= 6]
    for e in hh.values():
        if int(e['nc']) < 6:
            need(e['n'] == int(e['nc']),
                 'a household has %d records but NROCOMPO %s' % (e['n'], e['nc']))
    say('  member count == NROCOMPO for every household below the 6+ cap')
    say('  (%d households sit at the cap)' % len(capped))

    verify_tf_semantics(hh)

    # ---- mapping scored against the full count ---------------------------
    hcB = collections.Counter()
    for e in hh.values():
        need(e['tf'] in TF_EUROSTAT,
             'TIPOLOGIA_FAM %r is outside the mapping' % e['tf'])
        hcB[TF_EUROSTAT[e['tf']]] += 1
    say('--- CONVENTION B scored against the Eurostat full count ---')
    say('  (a diagnostic, not the output: it establishes that Eurostat keeps a')
    say('  nucleus-plus-others household with its nucleus type)')
    worst = 0.0
    for c in CATS[:-1]:
        v = hcB[c] * EXPANSION
        d = 100.0 * (v - EURO_HH[c]) / EURO_HH[c]
        worst = max(worst, abs(d))
        say('  %-30s %10d  vs %10d  %+7.2f %%' % (c, v, EURO_HH[c], d))
    need(worst < 3.0,
         'convention B deviates from the published Eurostat household counts by '
         '%.2f %%. Above 3 %% that is no longer sampling error, and the premise '
         'that Eurostat is on convention B is wrong.' % worst)
    say('  worst deviation %.2f %% -- within 1 %% on four of the five, so' % worst)
    say('  Eurostat IS convention B, and marginals_it.csv inherits that.')

    hc = collections.Counter()
    pc = collections.Counter()
    for e in hh.values():
        c = TF_MAP[e['tf']]
        hc[c] += 1
        pc[c] += e['n']
    nuc = ('9', '10', '11', '12')
    moved = sum(e['n'] for e in hh.values() if e['tf'] in nuc)
    movedh = sum(1 for e in hh.values() if e['tf'] in nuc)
    say('--- CONVENTION A, which is what is emitted ---')
    say('  %-30s %12s %12s %9s'
        % ('category', 'persons', 'households', 'mean size'))
    for c in CATS[:-1]:
        say('  %-30s %12d %12d %9.4f'
            % (c, pc[c] * EXPANSION, hc[c] * EXPANSION, pc[c] / float(hc[c])))
    r1 = pc['one_person'] / float(hc['one_person'])
    need(abs(r1 - 1.0) < 1e-9,
         'one_person implies %.6f persons per household; it must be exactly 1.'
         % r1)
    r = pc['couple_no_children'] / float(hc['couple_no_children'])
    need(abs(r - 2.0) < 0.05,
         'couple_no_children implies %.4f persons per household. Under '
         'convention A a childless couple is two people; 2.0794 is what '
         'convention B reads, so the mapping has not actually moved.' % r)
    say('  couple_no_children mean size %.4f -- the same exactly-2.00 signature'
        % r)
    say('  that es and uk produce under convention A.')
    say('  BLOCK MOVED B->A: %d persons (%.3f %%), %d households (%.3f %%)'
        % (moved * EXPANSION,
           100.0 * moved / float(sum(e['n'] for e in hh.values())),
           movedh * EXPANSION, 100.0 * movedh / float(len(hh))))

    # ---- person-basis household type, the D-S5-8 deliverable -------------
    tot_p = sum(pc.values())
    need(tot_p == len(priv),
         'person-basis household types cover %d persons but %d live in private '
         'households' % (tot_p, len(priv)))
    rows = []
    for c in CATS:
        n = pc[c] * EXPANSION
        rows.append((c, n, (float(pc[c]) / tot_p) if c != 'unknown' else 0.0))
    ssum = sum(r[2] for r in rows)
    need(abs(ssum - 1.0) < 1e-9, 'person-basis shares sum to %.12f' % ssum)
    p1 = os.path.join(OUT, 'hhtype_person_it.csv')
    fh = io.open(p1, 'w', newline='', encoding='utf-8')
    fh.write(u'field,category,count,share,base_name,base_count,source_table,'
             u'derivation,source_url,download_date,status\n')
    for c, n, s in rows:
        status = (u'PERSON_BASIS_D-S5-8_CONVENTION_A_PRIVATE_HH_D-S5-5'
                  if c != 'unknown'
                  else u'NOT_PUBLISHED_census_has_no_nonresponse_band')
        # 9 dp, not 6: at 6 dp the five shares sum to 0.999999 and
        # 4thJ_step6_rakeddonor.rake() refuses a target that misses 1.0 by 1e-6.
        fh.write(u'strat_hh_type,%s,%d,%.9f,persons_in_private_households,%d,'
                 u'"CensPop2011_1pct individui md5 %s",'
                 u'"TIPOLOGIA_FAM nucleus-code mapping, CONVENTION A, verified '
                 u'against NROCOMPO and REL_PAR; convention B scored vs '
                 u'cens_11htts_r2 full count, worst deviation %.2f pct",'
                 u'https://www.istat.it/it/archivio/microdati,2026-08-21,%s\n'
                 % (c, n, s, tot_p * EXPANSION, MICRO_MD5, worst, status))
    fh.write(u'# D-S5-8: PERSON basis, tabulated directly -- no household-to-person\n'
             u'# conversion, no mean-household-size assumption. Private households\n'
             u'# only (TIPCONV blank), which is D-S5-5 satisfied EXACTLY rather than\n'
             u'# approximated. 1 pct self-weighting sample, expansion factor exactly\n'
             u'# 100, no weight column. ISTAT applies disclosure control to the public\n'
             u'# file: its tabulations can differ from the published ones by a few\n'
             u'# tenths of a point.\n'
             u'# CONVENTION A: tf 9-12 (a nucleus PLUS other resident people) go to\n'
             u'# other_complex, matching ONS and INE. Eurostat -- and therefore the\n'
             u'# HOUSEHOLD-basis strat_hh_type rows still in marginals_it.csv -- is on\n'
             u'# convention B. D-S5-9 was ruled (a) on 2026-08-21: those household rows\n'
             u'# are REBUILT on convention A from this same microdata and written to\n'
             u'# hhtype_household_it.csv, from which marginals_it.csv is patched.\n')
    fh.close()
    # Re-read what was actually written: the FILE is what the rake consumes,
    # and a rounding choice in this writer could block G6.1 on its own.
    chk = 0.0
    nrow = 0
    fhr = io.open(p1, encoding='utf-8')
    for row in csv.reader(fhr):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        chk += float(row[3])
        nrow += 1
    fhr.close()
    need(nrow == len(CATS),
         'hhtype_person_it.csv wrote %d category rows, expected %d'
         % (nrow, len(CATS)))
    # 1e-7, not 1e-9: nine printed decimals leave up to ~1e-9 of
    # truncation. rake() refuses at 1e-6, so this is still an order
    # of magnitude inside the limit that matters.
    need(abs(chk - 1.0) < 1e-7,
         'hhtype_person_it.csv: the shares AS WRITTEN sum to %.12f. rake() '
         'refuses a target that misses 1.0 by more than 1e-6.' % chk)
    say('--- wrote %s ---' % os.path.basename(p1))
    for c, n, s in rows:
        say('  %-30s %10d  %.6f' % (c, n, s))

    # ---- D-S5-9: HOUSEHOLD basis, convention A ---------------------------
    # Ruled (a) 2026-08-21: marginals_it.csv's household-basis strat_hh_type
    # rows were on convention B (Eurostat cens_11htts_r2) and therefore
    # contradicted Italy's own person file, which is on A. Only this microdata
    # can put them on the same convention. The cost is stated in the file: they
    # stop being a full count and become a 1 % sample estimate.
    #
    # The accuracy that estimate inherits is NOT guessed. `worst` above is the
    # deviation of THIS sample, tabulated on convention B, from the Eurostat
    # full count on convention B -- a like-for-like comparison on the only
    # convention both can express. Whatever that number is, it bounds what the
    # convention-A rows below can be wrong by for the same reason.
    tot_h = sum(hc.values())
    need(tot_h == len(hh),
         'household-basis types cover %d households but %d exist'
         % (tot_h, len(hh)))
    hrows = []
    for c in CATS:
        hrows.append((c, hc[c] * EXPANSION,
                      (float(hc[c]) / tot_h) if c != 'unknown' else 0.0))
    hsum = sum(r[2] for r in hrows)
    need(abs(hsum - 1.0) < 1e-9, 'household-basis shares sum to %.12f' % hsum)
    p3 = os.path.join(OUT, 'hhtype_household_it.csv')
    fh = io.open(p3, 'w', newline='', encoding='utf-8')
    fh.write(u'field,category,count,share,base_name,base_count,source_table,'
             u'derivation,source_url,download_date,status\n')
    for c, n, s in hrows:
        status = (u'HOUSEHOLD_BASIS_D-S5-9a_CONVENTION_A_SAMPLE_PRIVATE_HH'
                  if c != 'unknown'
                  else u'NOT_PUBLISHED_census_has_no_nonresponse_band')
        fh.write(u'strat_hh_type,%s,%d,%.9f,private_households,%d,'
                 u'"CensPop2011_1pct individui md5 %s",'
                 u'"TIPOLOGIA_FAM nucleus-code mapping, CONVENTION A, household '
                 u'basis; same sample tabulated on convention B reproduces '
                 u'cens_11htts_r2 to %.2f pct worst-category",'
                 u'https://www.istat.it/it/archivio/microdati,2026-08-21,%s\n'
                 % (c, n, s, tot_h * EXPANSION, MICRO_MD5, worst, status))
    fh.write(u'# D-S5-9 ruled (a) 2026-08-21. These rows REPLACE the Eurostat\n'
             u'# cens_11htts_r2 household rows that marginals_it.csv carried, which\n'
             u'# were on convention B and contradicted hhtype_person_it.csv.\n'
             u'# WHAT IS LOST: these are no longer a full count. They are a 1 pct\n'
             u'# self-weighting sample, and the same sample on convention B misses\n'
             u'# the published full count by up to %.2f pct on its worst category.\n'
             u'# WHAT IS GAINED: one convention across every Italian file, and the\n'
             u'# household table no longer contradicts the person table that the\n'
             u'# G6.1 rake actually consumes.\n'
             u'# NOTE the two bases are not interchangeable: one_person is %.4f of\n'
             u'# HOUSEHOLDS here and %.4f of PERSONS in hhtype_person_it.csv. That\n'
             u'# factor is FINDING 50 one level up and is why D-S5-8 exists.\n'
             % (worst, hrows[0][2], rows[0][2]))
    fh.close()
    chk = 0.0
    nrow = 0
    fhr = io.open(p3, encoding='utf-8')
    for row in csv.reader(fhr):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        chk += float(row[3])
        nrow += 1
    fhr.close()
    need(nrow == len(CATS),
         'hhtype_household_it.csv wrote %d rows, expected %d'
         % (nrow, len(CATS)))
    need(abs(chk - 1.0) < 1e-7,
         'hhtype_household_it.csv: shares AS WRITTEN sum to %.12f' % chk)
    say('--- wrote %s (D-S5-9a) ---' % os.path.basename(p3))
    say('  %-30s %12s %12s %10s'
        % ('category', 'households', 'was (Euro B)', 'change pp'))
    for c, n, s in hrows[:-1]:
        was = EURO_HH[c] / float(PUB_HOUSEHOLDS)
        say('  %-30s %12d %12d %+10.3f'
            % (c, n, EURO_HH[c], 100.0 * (s - was)))

    # ---- D-S5-7 measurement ----------------------------------------------
    e_priv = collections.Counter()
    e_all = collections.Counter()
    for p in persons:
        if p['ETA_CLASSI'] in ('', '1'):
            continue
        need(p['COND_PROF'] in ECON_MAP,
             'COND_PROF %r for a 15+ person is outside the mapping'
             % p['COND_PROF'])
        b = ECON_MAP[p['COND_PROF']]
        e_all[b] += 1
        if p['TIPCONV'] == '':
            e_priv[b] += 1
    tp = float(sum(e_priv.values()))
    ta = float(sum(e_all.values()))
    say('--- D-S5-7 measurement (was: bounded at 0.44 pp) ---')
    say('  %-16s %10s %10s %8s | %10s %8s'
        % ('band', 'priv_hh', 'all_res', 'basis pp', 'tract', 'noise pp'))
    p2 = os.path.join(OUT, 'econ_basis_check_it.csv')
    fh = io.open(p2, 'w', newline='', encoding='utf-8')
    fh.write(u'band,share_private_household_15plus,share_all_residents_15plus,'
             u'basis_effect_pp,share_tract_fullcount_all_residents_15plus,'
             u'sampling_and_disclosure_noise_pp\n')
    mx_basis = 0.0
    mx_noise = 0.0
    for b in ECON_BANDS[:-1]:
        sp = e_priv[b] / tp
        sa = e_all[b] / ta
        d1 = (sp - sa) * 100.0
        d2 = (sa - TRACT_ECON[b]) * 100.0
        mx_basis = max(mx_basis, abs(d1))
        mx_noise = max(mx_noise, abs(d2))
        say('  %-16s %10.6f %10.6f %+8.3f | %10.6f %+8.3f'
            % (b, sp, sa, d1, TRACT_ECON[b], d2))
        fh.write(u'%s,%.6f,%.6f,%+.3f,%.6f,%+.3f\n'
                 % (b, sp, sa, d1, TRACT_ECON[b], d2))
    fh.write(u'# basis_effect_pp = private-household 15+ MINUS all-residents 15+,\n'
             u'#   same records, so it is the D-S5-5 restriction alone.\n'
             u'# noise_pp = the SAME universe (all residents 15+) from the sample\n'
             u'#   MINUS the ISTAT tract full count. Sampling error plus ISTAT\n'
             u'#   disclosure control.\n'
             u'# max basis effect %.3f pp; max noise %.3f pp.\n'
             u'# THE NOISE IS LARGER THAN THE EFFECT IT WOULD CORRECT, so\n'
             u'# econ_11plus_it.csv is NOT rewritten from this sample. The bound of\n'
             u'# 0.44 pp is replaced by a MEASUREMENT of %.3f pp, signed: employed up,\n'
             u'# retired and other_inactive down, which is the expected direction for a\n'
             u'# collective sector of care homes.\n'
             % (mx_basis, mx_noise, mx_basis))
    fh.close()
    say('  max basis effect %.3f pp   max sampling+disclosure noise %.3f pp'
        % (mx_basis, mx_noise))
    need(mx_basis < 0.44,
         'the measured basis effect %.3f pp exceeds the 0.44 pp bound that '
         'D-S5-7 accepted. The bound was wrong and the acceptance must be '
         're-argued.' % mx_basis)
    say('  wrote %s' % os.path.basename(p2))

    # ---- what this module refuses to emit --------------------------------
    say('--- NOT emitted ---')
    say('  age: ETA_CLASSI bottoms out at 0-14, so the 11-14 band cannot be')
    say('  recovered. marginals_it.csv keeps its derivation; no partial age')
    say('  marginal is written.')
    say('  md5 hhtype_person_it.csv     %s' % md5(p1))
    say('  md5 hhtype_household_it.csv  %s' % md5(p3))
    say('  md5 econ_basis_check_it.csv  %s' % md5(p2))
    say('OK')


if __name__ == '__main__':
    try:
        main()
    except BuildError as e:
        sys.stderr.write('REFUSED: %s\n' % e)
        sys.exit(2)
