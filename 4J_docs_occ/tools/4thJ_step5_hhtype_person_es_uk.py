# -*- coding: utf-8 -*-
"""
4J / Step 5.1 -- `strat_hh_type` ON A PERSON BASIS for `es` and `uk`.

THE PROBLEM THIS CLOSES (D-S5-8)
================================
Every census publishes household type on a HOUSEHOLD base: one row per
household. The rake donors in Step 5.2 are PEOPLE -- one row per diarist. Raking
a person file onto a household marginal is a category error: it would drive
one-person households to ~31 % of PEOPLE in the UK when they are ~13 % of
people and 31 % of HOUSEHOLDS. `FINDING 50`'s frame error, one level up.

Italy is handled by `4thJ_step5_build_it_microdata.py`. This module does `es`
and `uk`, and neither needs an assumption:

  uk  ONS publishes BOTH bases. `KS105UK` counts households, `QS112UK` counts
      *people* in each household-composition class. The person basis is a
      published full count, not a conversion.
  es  INE's Censo 2011 person microdata carries `ESTHOG` (estructura del hogar)
      on EVERY PERSON RECORD. Tabulating persons by `ESTHOG` IS the person
      basis; no mean-household-size factor appears anywhere.

So all three folds end up on a person basis with NO household-to-person
conversion factor in any of them. D-S5-8's three options are moot: the data had
the answer in all three countries.

>>> CONVENTION A, AND WHY IT IS NOT A PREFERENCE
>>> =============================================
>>> A household containing a family nucleus PLUS other resident people can be
>>> classified two ways, and the three statistical offices do not agree:
>>>
>>>   CONVENTION A  it goes to `other_complex`.        ONS (uk), INE (es)
>>>   CONVENTION B  it keeps its nucleus's type.       Eurostat (used for it)
>>>
>>> This module and its Italian twin both emit CONVENTION A, for one hard
>>> reason and one soft one.
>>>
>>> HARD: the UK CANNOT express convention B. `QS112UK`'s "Other household
>>> types" is published as a single class with no decomposition by whether a
>>> nucleus is present, so there is no way to pull those households back out.
>>> A is the only convention all three folds can actually be put on.
>>>
>>> SOFT, but it is what exposed the problem: under A, `couple_no_children`
>>> comes out at a mean size of EXACTLY 2.0000 in Spain and in Italy, and
>>> 2.0022 in the UK. Under B, Italy's reads 2.0794 and Spain's household file
>>> disagrees with its own person file. Two people is what a childless couple
>>> is; anything above it means the class is absorbing somebody else.
>>>
>>> THIS WAS CAUGHT, NOT ASSUMED. The first version of this module split Spain's
>>> `ESTHOG` 10 into the nucleus types (convention B, to match Italy). The
>>> mean-household-size check then reported `es other_complex` at 1.6495 persons
>>> per household -- IMPOSSIBLE, since every household in that class has at
>>> least two people. The already-shipped Spanish HOUSEHOLD file was on A while
>>> the new person file was on B, and the ratio between them was the only thing
>>> that could show it. The guard band has since been tightened from 1.5 to 1.95
>>> so that this exact failure cannot pass again.

WHAT IS BEING CHECKED, AND WHY THE CHECK IS REAL
================================================
For each fold the person-basis counts are divided by the household-basis counts
already carried in `marginals_<c>.csv`. The ratio must be a believable mean
household size, category by category. That is a genuine test because the two
sides come from separate publications (uk) or from a published table and a
microdata file (es) -- nothing forces them to agree.

  one_person MUST come out at EXACTLY 1.00, or the mapping has crossed a wire.
  couple_no_children must land at 2.00 and is refused outside 1.95-2.25.
  couple_with_children must exceed couple_no_children.

The uk `couple_no_children` ratio lands at 2.0020, which is the same 2.00042
that `D-S5-2` measured on `QS112UK` when it folded the all-65+ block. Two
different questions, one number, and it was not arranged.

THE DECLARED PIECES -- both small, both stated rather than hidden
=================================================================
uk  `QS112UK` publishes "One family only: Same-sex civil partnership couple:
    Total" (75,188 people) with NO children breakdown. It is assigned in full
    to `couple_no_children`. Bound: 0.121 % of the UK person base, and the
    error is at most that if every one of them in fact had children.

uk  "One family only: All aged 65 and over" (4,263,276 people) is a SEPARATE
    class in the ONS hierarchy, not a subset -- verified here by addition: the
    five sibling classes sum to the "One family only: Total" exactly. It goes to
    `couple_no_children`, which is `D-S5-2`'s ruling applied to the person table
    it was measured on.

WHAT CONVENTION A COSTS ITALY, AND WHY IT IS STILL WORTH IT
===========================================================
Moving Italy from B to A reclassifies 7.222 % of Italian persons (4.446 % of
Italian households) out of the nucleus types and into `other_complex`, which
goes from 5.62 % to 12.84 % of persons. That is a large move and it is recorded
as such. But leaving it undone means the three folds are raked onto marginals
built by three different rules, and the difference between those rules is
COUNTRY-CORRELATED -- i.e. confounded with the leave-one-country-out signal
itself. Same argument as `FINDING 57`'s EU boundary conditions: a harmonised
basis that is slightly further from each national publication beats three
national bases that differ from each other along the axis being measured.

>>> ONE CONSEQUENCE IS NOT CLOSED HERE. `marginals_it.csv`'s HOUSEHOLD-basis
>>> `strat_hh_type` rows are still on convention B, because they come from
>>> Eurostat and Eurostat cannot express A. Italy's household basis and Italy's
>>> person basis therefore now disagree, and only the ISTAT microdata can put
>>> them back together. That is a change to an already-shipped file, so it is
>>> raised as a decision rather than taken here.

OUTPUTS
=======
  outputs_step5/hhtype_person_es.csv
  outputs_step5/hhtype_person_uk.csv

  usage:  python 4thJ_step5_hhtype_person_es_uk.py [path/to/Microdatos_personas_nacional.zip]
  The zip is 155,860,498 bytes and is NOT committed. Without it the uk half
  still runs and the es half is skipped WITH A LOUD LINE, never silently.
  Source: https://www.ine.es/ftp/microdatos/censopv/cen11/Microdatos_personas_nacional.zip
"""

import io
import os
import sys
import csv
import zipfile
import hashlib
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
RAW = os.path.join(OUT, 'raw')

ES_ZIP_MD5 = '0c8f9b44b70b079b25f2f20fdbd2e83f'
ES_ZIP_SIZE = 155860498
CATS = ['one_person', 'couple_no_children', 'couple_with_children',
        'single_parent_with_children', 'other_complex', 'unknown']

# ---- ESTHOG (INE Censo 2011, person record, cols 203-204, 1-based) ---------
# CONVENTION A: 10 is "pareja O padre/madre que convive con algun hijo menor de
# 25 anos y otra(s) persona(s)" -- a nucleus PLUS other people -> other_complex.
ES_MAP = {'01': 'one_person', '02': 'one_person',
          '03': 'one_person', '04': 'one_person',
          '05': 'single_parent_with_children',
          '06': 'single_parent_with_children',
          '07': 'couple_no_children',
          '08': 'couple_with_children', '09': 'couple_with_children',
          '10': 'other_complex',
          '11': 'other_complex'}
# fixed-width slices, 0-based python
ES_FACTOR = (19, 33)    # 20-33
ES_NMIEM = (196, 198)   # 197-198, household size
ES_ESTHOG = (202, 204)  # 203-204

# ---- QS112UK: category code -> our five ------------------------------------
UK_MAP = {
    '1': 'one_person',                       # One person household: Total
    '5': 'couple_no_children',               # One family only: All aged 65 and over
    '7': 'couple_no_children',               # Married couple: No children
    '8': 'couple_with_children',
    '9': 'couple_with_children',
    '10': 'couple_with_children',
    '11': 'couple_no_children',              # Same-sex civil partnership: Total (declared)
    '13': 'couple_no_children',              # Cohabiting couple: No children
    '14': 'couple_with_children',
    '15': 'couple_with_children',
    '16': 'couple_with_children',
    '17': 'single_parent_with_children',     # Lone parent: Total
    '21': 'other_complex',                   # Other household types: Total
}
# Aggregate rows. Each is verified to be the exact sum of its children before
# being discarded, so nothing is double-counted and no hidden subset survives.
UK_SUMS = {
    '0': ['1', '4', '21'],                       # All categories
    '4': ['5', '6', '11', '12', '17'],           # One family only: Total
    '6': ['7', '8', '9', '10'],                  # Married couple: Total
    '12': ['13', '14', '15', '16'],              # Cohabiting couple: Total
    '17': ['18', '19', '20'],                    # Lone parent: Total
    '21': ['22', '23', '24', '25', '26'],        # Other household types: Total
}


class BuildError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise BuildError(msg)


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def md5(path):
    h = hashlib.md5()
    fh = open(path, 'rb')
    try:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    finally:
        fh.close()
    return h.hexdigest()


def household_basis(fold):
    """The household-basis counts already shipped, used as the denominator of
    the mean-household-size check. Read from the file, never re-typed."""
    p = os.path.join(OUT, 'marginals_%s.csv' % fold)
    need(os.path.exists(p), 'missing %s' % p)
    got = {}
    base = None
    fh = io.open(p, encoding='utf-8')
    for row in csv.reader(fh):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        if row[0] == 'strat_hh_type':
            got[row[1]] = float(row[2])
            base = float(row[5])
    fh.close()
    need(set(got) == set(CATS),
         '%s carries household-type categories %s' % (fold, sorted(got)))
    return got, base


def size_check(fold, counts, hh, hh_base):
    tot = float(sum(counts.values()))
    say('--- %s : person basis vs the household basis already shipped ---' % fold)
    say('  %-30s %12s %12s %8s' % ('category', 'persons', 'households', 'mean size'))
    for c in CATS:
        if hh[c] == 0:
            say('  %-30s %12.0f %12.0f %8s' % (c, counts[c], hh[c], '-'))
            continue
        r = counts[c] / hh[c]
        say('  %-30s %12.0f %12.0f %8.4f' % (c, counts[c], hh[c], r))
        if c == 'one_person':
            need(abs(r - 1.0) < 0.005,
                 '%s: one_person implies %.4f persons per household. It must be '
                 'exactly 1.00; the two bases are not describing the same '
                 'category.' % (fold, r))
        else:
            # 1.95 and not 1.5: an es other_complex of 1.6495 is what a
            # convention mismatch looks like, and 1.5 let it through once.
            need(1.95 < r < 6.0,
                 '%s: %s implies %.4f persons per household. Every household in '
                 'that class holds at least two people, so the person and '
                 'household files are not on the same classification '
                 'convention.' % (fold, c, r))
    r_cnc = counts['couple_no_children'] / hh['couple_no_children']
    r_cwc = counts['couple_with_children'] / hh['couple_with_children']
    need(r_cnc < r_cwc,
         '%s: couples WITHOUT children (%.4f) are not smaller than couples WITH '
         'children (%.4f).' % (fold, r_cnc, r_cwc))
    need(r_cnc < 2.25,
         '%s: couple_no_children implies %.4f persons per household. A childless '
         'couple is two people; above 2.25 the class is absorbing somebody '
         'else, which is convention B leaking in.' % (fold, r_cnc))
    say('  implied overall mean household size %.4f (persons %.0f / households %.0f)'
        % (tot / hh_base, tot, hh_base))


def emit(fold, counts, base_desc, source, url, note_lines):
    tot = float(sum(counts.values()))
    need(tot > 0, '%s: person base is zero' % fold)
    hh, hh_base = household_basis(fold)
    size_check(fold, counts, hh, hh_base)
    p = os.path.join(OUT, 'hhtype_person_%s.csv' % fold)
    fh = io.open(p, 'w', newline='', encoding='utf-8')
    fh.write(u'field,category,count,share,base_name,base_count,source_table,'
             u'derivation,source_url,download_date,status\n')
    for c in CATS:
        # 9 dp, not 6. At 6 dp the five shares sum to 0.999999, and
        # 4thJ_step6_rakeddonor.rake() refuses a target that misses 1.0 by 1e-6
        # -- so a rounding choice in this writer would have blocked G6.1.
        fh.write(u'strat_hh_type,%s,%.2f,%.9f,%s,%.2f,"%s","%s",%s,2026-08-21,%s\n'
                 % (c, counts[c], counts[c] / tot, base_desc, tot, source,
                    'person basis, CONVENTION A (nucleus plus other people -> '
                    'other_complex); no household-to-person conversion', url,
                    'PERSON_BASIS_D-S5-8_CONVENTION_A_PRIVATE_HH_D-S5-5'
                    if c != 'unknown'
                    else 'NOT_PUBLISHED_census_has_no_nonresponse_band'))
    for l in note_lines:
        fh.write(u'# %s\n' % l)
    fh.close()
    verify_shares(p)
    say('  wrote %s  md5 %s' % (os.path.basename(p), md5(p)))
    return p


def verify_shares(path):
    """Re-read what was actually written and check the shares sum to 1. The
    intent summing to 1 is not the point; the FILE is what the rake consumes."""
    tot = 0.0
    n = 0
    fh = io.open(path, encoding='utf-8')
    for row in csv.reader(fh):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        tot += float(row[3])
        n += 1
    fh.close()
    need(n == len(CATS), '%s wrote %d category rows, expected %d'
         % (os.path.basename(path), n, len(CATS)))
    # 1e-7, not 1e-9: nine printed decimals leave up to ~1e-9 of
    # truncation and 0.999999999 is a correct file, not a broken one.
    # rake() refuses at 1e-6, so this still sits an order of magnitude
    # inside the limit that matters.
    need(abs(tot - 1.0) < 1e-7,
         '%s: the shares AS WRITTEN sum to %.12f. rake() refuses a target that '
         'misses 1.0 by more than 1e-6, so this file would be rejected.'
         % (os.path.basename(path), tot))


def build_uk():
    src = os.path.join(RAW, 'uk_QS112UK_household_composition_people.csv')
    need(os.path.exists(src), 'missing %s' % src)
    val = {}
    fh = io.open(src, encoding='utf-8')
    rd = csv.reader(fh)
    hdr = next(rd)
    ic = hdr.index('C_HHCHUK11')
    iv = hdr.index('OBS_VALUE')
    ig = hdr.index('GEOGRAPHY_NAME')
    for row in rd:
        need(row[ig] == 'United Kingdom',
             'QS112UK carries geography %r; this module wants the UK row only'
             % row[ig])
        val[row[ic]] = float(row[iv])
    fh.close()
    say('--- uk QS112UK (people, not households) ---')
    say('  %d categories, all-categories total %.0f' % (len(val), val['0']))
    for parent, kids in sorted(UK_SUMS.items(), key=lambda x: int(x[0])):
        s = sum(val[k] for k in kids)
        need(abs(s - val[parent]) < 0.5,
             'QS112UK category %s is %.0f but its children %s sum to %.0f. The '
             'hierarchy this module assumes is not the one published.'
             % (parent, val[parent], kids, s))
    say('  every parent category equals the exact sum of its children')
    say('  (so no row is double-counted and none is a hidden subset)')
    counts = collections.Counter()
    for k, c in UK_MAP.items():
        counts[c] += val[k]
    counts['unknown'] = 0.0
    need(abs(sum(counts.values()) - val['0']) < 0.5,
         'the five categories sum to %.0f, the published all-categories total '
         'is %.0f' % (sum(counts.values()), val['0']))
    say('  five categories sum to the published total exactly')
    cp = val['11']
    say('  DECLARED: same-sex civil partnership %.0f people (%.3f %% of the base),'
        % (cp, 100.0 * cp / val['0']))
    say('  no children breakdown, assigned in full to couple_no_children.')
    return emit(
        'uk', counts, 'persons_in_private_households',
        'QS112UK household composition (people), Nomis',
        'https://www.nomisweb.co.uk/api/v01/dataset/NM_1537_1.data.csv',
        ['D-S5-8: PERSON basis. ONS publishes it directly (QS112UK); KS105UK is',
         'the household-basis twin and stays in marginals_uk.csv.',
         'CONVENTION A: a household holding a family PLUS other people is inside',
         'ONS "Other household types" and cannot be pulled back out, which is',
         'why A is the only convention all three folds can share.',
         'Same-sex civil partnership (75,188 people, 0.121 pct of the base) has',
         'no children breakdown and is assigned in full to couple_no_children.',
         'One family only: All aged 65 and over (4,263,276) is a SEPARATE class,',
         'verified by addition, and follows D-S5-2 into couple_no_children.'])


def build_es(zip_path):
    need(os.path.exists(zip_path), 'missing %s' % zip_path)
    sz = os.path.getsize(zip_path)
    need(sz == ES_ZIP_SIZE,
         'the INE zip is %d bytes, expected %d. A truncated download reads as a '
         'smaller Spain, not as an error.' % (sz, ES_ZIP_SIZE))
    got = md5(zip_path)
    need(got == ES_ZIP_MD5,
         'INE zip md5 is %s, expected %s' % (got, ES_ZIP_MD5))
    say('--- es INE Censo 2011 person microdata ---')
    say('  md5 %s  %d bytes' % (ES_ZIP_MD5, sz))
    z = zipfile.ZipFile(zip_path)
    names = z.namelist()
    need(len(names) == 1, 'the zip holds %d members: %s' % (len(names), names))

    counts = collections.Counter()
    hh_est = collections.Counter()
    codes = collections.Counter()
    tot_w = 0.0
    n = 0
    fh = z.open(names[0])
    for raw in fh:
        line = raw.decode('latin-1')
        n += 1
        e = line[ES_ESTHOG[0]:ES_ESTHOG[1]]
        need(e in ES_MAP, 'ESTHOG %r is outside the mapping' % e)
        w = float(line[ES_FACTOR[0]:ES_FACTOR[1]])
        nm = int(line[ES_NMIEM[0]:ES_NMIEM[1]])
        need(nm >= 1, 'NMIEM %d' % nm)
        tot_w += w
        codes[e] += w
        counts[ES_MAP[e]] += w
        hh_est[ES_MAP[e]] += w / nm
    fh.close()
    z.close()
    counts['unknown'] = 0.0
    need(n == 4107465, 'expected 4,107,465 person records, read %d' % n)
    need(abs(sum(counts.values()) - tot_w) < 1.0,
         'the five categories carry %.2f of a weighted %.2f'
         % (sum(counts.values()), tot_w))
    need(abs(tot_w - 46574725.58) < 1.0,
         'weighted total %.2f does not reproduce the 46,574,725.58 already '
         'recorded for this file.' % tot_w)
    say('  %d records, weighted total %.2f (matches the 2026-08-20 tabulation)'
        % (n, tot_w))
    say('  ESTHOG 10 (nucleus + other people) %.2f persons, %.3f %% of the base,'
        % (codes['10'], 100.0 * codes['10'] / tot_w))
    say('  goes to other_complex under CONVENTION A.')

    # The person file is a microdata tabulation and the household file is a
    # published PC-Axis table. Reconstructing households from the person file
    # (sum of w/NMIEM) must reproduce the published table, or the two are not
    # on the same classification after all.
    hh, hh_base = household_basis('es')
    say('  reconstructed households from the same records (sum of w/NMIEM):')
    for c in CATS[:-1]:
        d = hh_est[c] - hh[c]
        say('    %-30s %12.2f vs published %12.2f  %+8.2f' % (c, hh_est[c], hh[c], d))
        need(abs(d) < 1.0,
             'es %s: households reconstructed from the person microdata are '
             '%.2f but marginals_es.csv publishes %.2f. The person file and the '
             'household file are not on the same classification.'
             % (c, hh_est[c], hh[c]))
    say('  every category reproduces the published household count to under one')
    say('  household -- the two bases are now provably the same classification.')

    return emit(
        'es', counts, 'persons_in_private_households',
        'INE Censo 2011 person microdata, ESTHOG (md5 %s)' % ES_ZIP_MD5,
        'https://www.ine.es/ftp/microdatos/censopv/cen11/Microdatos_personas_nacional.zip',
        ['D-S5-8: PERSON basis, tabulated from ESTHOG on the person record.',
         'Universe is stated on line 2 of the INE record layout: "Un registro',
         'para cada persona residente en viviendas principales" -- private',
         'households already, so D-S5-5 needs no restriction step.',
         'CONVENTION A: ESTHOG 10 (nucleus with children PLUS other people) goes',
         'to other_complex, which is what the already-shipped household file',
         'marginals_es.csv does. Verified: summing w/NMIEM over these same',
         'records reproduces every published household count to under one',
         'household.'])


def main():
    built = []
    built.append(build_uk())
    say('')
    zp = (sys.argv[1] if len(sys.argv) > 1 else
          os.path.join(RAW, 'es_micro.zip'))
    if os.path.exists(zp):
        built.append(build_es(zp))
    else:
        say('--- es SKIPPED ---')
        say('  %s not present. The INE person microdata is 155,860,498 bytes' % zp)
        say('  and is not committed. Pass its path as argv[1] to build the es half.')
        say('  es is NOT built; do not read the absence as a zero.')
    say('')
    say('built: %s' % ', '.join(os.path.basename(b) for b in built))
    say('OK')


if __name__ == '__main__':
    try:
        main()
    except BuildError as e:
        sys.stderr.write('REFUSED: %s\n' % e)
        sys.exit(2)
