#!/usr/bin/env python
"""
4J Step 5.1 -- build `marginals_it.csv` and `econ_11plus_it.csv` for ITALY.

  usage: python 4thJ_step5_build_it.py <outputs_step5_dir>

WHY THIS FILE EXISTS AT ALL, AND WHY IT IS NOT AN ISTAT WAREHOUSE QUERY
----------------------------------------------------------------------
Italy was the last empty fold of Step 5.1 and the whole of the critical path:
`G6.1`'s raked-donor null rakes the N-1 donors onto the HELD-OUT country's
PUBLISHED marginals, so with no Italian marginal the `it` fold's null cannot be
computed and the LOCO claim is two thirds of a claim.

Every ISTAT dissemination route funnels into `esploradati.istat.it`, whose IP
`193.204.90.13` refuses TCP on 443 (connect timeout ~15-21 s; `dati.istat.it`
302s to `avvisi.istat.it/IdotStat/`, `dati-censimentopopolazione.istat.it` 302s
straight into `esploradati`). Retried across three days. That route is dead.

TWO ROUTES THAT ARE ALIVE, AND THEY AGREE TO THE PERSON
------------------------------------------------------
  A. ISTAT's own STATIC census-tract release, on `www.istat.it`, which is up:
     `dati-cpa_2011.zip`, 52,442,848 bytes, md5 bab8d744088761397c09ef8c70ca53d4
     -- 366,863 census tracts x 140 variables, all 20 regions. This is the
     national statistical office, i.e. `D-S5-1`'s frozen route 3.
  B. Eurostat's 2011 Census Hub, via the dissemination API, which republishes
     the hypercubes ISTAT transmitted under Regulation (EC) 763/2008.

🔴 THE TWO ROUTES WERE CROSS-CHECKED BEFORE EITHER WAS USED, AND EVERY QUANTITY
THEY SHARE IS IDENTICAL TO THE PERSON -- not to a rounding, to the person:

     total population        59,433,744   both
     males                   28,745,507   both
     ages 10-14              2,795,020    Eurostat single-year sum  == ISTAT P16
     each of 15-24 .. 75+    identical    Eurostat single-year sums == ISTAT P17..P29
     labour force            25,985,295   Eurostat ACT              == ISTAT P60
     employed                23,017,840   Eurostat EMP              == ISTAT P61
     unemployed              2,967,455    Eurostat UNE              == ISTAT P60-P61
     inactive incl. under-15 33,448,449   Eurostat INAC             == ISTAT P128 + P14..P16

That is the evidence for using B where A cannot answer, and it is why B is not
treated here as a second-best source. It is the same tabulation.

WHAT EACH SOURCE CONTRIBUTES, AND WHY THE OTHER COULD NOT
---------------------------------------------------------
  age       ISTAT stops at 5-year bands (P16 = 10-14) and our floor is 11.
            Eurostat `cens_11ag_r3` carries SINGLE YEAR of age, so 11-14 is
            EXACT and not a fifths assumption. Bands 15-24 .. 75+ are taken
            from Eurostat too and each is verified equal to its ISTAT sum.
  sex       Eurostat `cens_11ag_r3` is sex x single-year, so sex is EXACT ON
            THE 11+ BASE. 🔴 This is BETTER than the UK's marginal, which is an
            all-ages approximation because no UK-wide sex-by-age table exists.
  hh_type   ISTAT's tract file publishes households by SIZE only (PF3..PF8),
            never by TYPE, so the five composition categories are simply not
            derivable from it. Eurostat `cens_11htts_r2` is natively
            PRIVATE HOUSEHOLDS by type -- 24 `hhcomp` codes that partition
            exactly onto our five.
  econ      ISTAT P60/P61/P128/P130/P131/P135/P139. 🔴 ITALY PUBLISHES A
            HOMEMAKER BAND (P130, casalinghe) -- so `it` is fitted on SIX
            economic bands where Spain has five (`FINDING 51`). Eurostat cannot
            do this: its `wstatus` codelist is POP/ACT/EMP/UNE/INAC/UNK and
            lumps all inactivity into one `INAC`.
  communal  Neither ISTAT tract file nor any Eurostat cube crosses residence
            type with economic status for Italy (the UK had `DC1602EW`; there
            is no Italian equivalent). See THE ONE THING THIS FILE CANNOT DO.

`P139` -- A LABEL THAT IS WRONG, CAUGHT BY ARITHMETIC
-----------------------------------------------------
The tracciato calls P139 "percettori di reddito da lavoro o capitale" (income
from WORK or capital). A person outside the labour force cannot be drawing
income from work, so the label is self-contradictory. The arithmetic settles it:

    P128 = P130 + P131 + P135 + P139   exactly, residual 0

i.e. P139 IS the fourth non-labour-force band -- pension or capital income --
and the tracciato's wording is a typo for "pensione". It is mapped to `retired`
on that identity, never on the label. (`FINDING 47` is the standing reminder
that a plausible label is not a verified one.)

WHAT `D-S5-5` (private households) COSTS HERE, AND WHERE IT IS ONLY PARTIAL
--------------------------------------------------------------------------
`D-S5-5` restricts every marginal to residents of PRIVATE HOUSEHOLDS, the frame
HETUS samples. Italy's private-household population is published directly:

    PF2 (componenti delle famiglie residenti) = 59,132,045
    P1  (popolazione residente)               = 59,433,744
    convivenze                                =    301,699   (0.5076 % of P1)

which is close to Spain (0.515 %) and nothing like the UK (1.78 %).

Age and sex are corrected with the Eurostat CLQ (collective living quarters)
profile, scaled to ISTAT's own convivenze total -- exactly the construction the
UK marginal used with `DC1104EW` (there k = 1.12096051; here k = 0.858126).
Two declared assumptions, both the UK's:
  * the collective rate is uniform within a coarse Eurostat age band, which is
    how a coarse profile is pushed onto our finer bands;
  * Eurostat's CLQ (351,579) and ISTAT's convivenze (301,699) differ by 49,880
    persons, 0.084 % of the population, because they draw the collective/private
    boundary differently. The ISTAT total is authoritative (it is the national
    office and it is the definition PF2 uses); Eurostat supplies only the SHAPE.

🔴 THE ONE THING THIS FILE CANNOT DO -- STATED, NOT HIDDEN
----------------------------------------------------------
The ECONOMIC marginal stays on ALL RESIDENTS aged 15+. No published Italian
table crosses residence type with economic status, so the private-household
restriction `D-S5-5` ordered cannot be applied to this one field. The file
records it as an explicit status string, and prints the WORST-CASE bound: what
each band's share would be if every one of the ~295.5k collective residents
aged 15+ were `retired` (the direction the Y65-84 and Y_GE85 CLQ rates make
overwhelmingly likely). If the bound is small the declaration is cheap; the
point is that it is measured, not asserted.

🔴 AND ONE MORE LOCO ASYMMETRY, WHICH IS `FINDING 48`'s FAMILY
--------------------------------------------------------------
`D-S5-3` had to invent `unknown` for uk/es because their censuses publish
economic activity for 16-74 ONLY: 11-14 -> unknown, age 15 -> unknown,
75+ -> retired (imputed). ITALY PUBLISHES 15+ DIRECTLY. So on the `it` fold
  * age 15 is PUBLISHED, not `unknown`;
  * 75+ is PUBLISHED, not imputed to `retired`;
  * `unknown` contains the 11-14 band and NOTHING ELSE.
`unknown` and `retired` therefore mean different things in the three folds.
That is a country fingerprint of the same species as `FINDING 48` and it must
be read alongside any `it`-fold economic result.
"""

import csv
import io
import json
import os
import sys
import zipfile

# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------
ISTAT_ZIP = 'it_istat_dati-cpa_2011.zip'
ISTAT_MD5 = 'bab8d744088761397c09ef8c70ca53d4'
ISTAT_URL = ('https://www.istat.it/storage/cartografia/variabili-censuarie/'
             'dati-cpa_2011.zip')
ESTAT_URL = ('https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/'
             'data/%s?format=JSON&lang=EN&geo=IT')
DL_DATE = '2026-08-21'

ESTAT = {
    'age':  ('cens_11ag_r3',   'it_eurostat_cens_11ag_r3_age_single_year_by_sex.json'),
    'hh':   ('cens_11htts_r2', 'it_eurostat_cens_11htts_r2_private_households_by_type.json'),
    'hou':  ('cens_11hou_r2',  'it_eurostat_cens_11hou_r2_population_by_housing_arrangement.json'),
    'aed':  ('cens_11aed_r2',  'it_eurostat_cens_11aed_r2_activity_status_by_education.json'),
}

BANDS = [('11-14', 11, 14), ('15-24', 15, 24), ('25-34', 25, 34),
         ('35-44', 35, 44), ('45-54', 45, 54), ('55-64', 55, 64),
         ('65-74', 65, 74), ('75+', 75, 200)]

#: Eurostat coarse band -> (lo, hi) in single years. `cens_11hou_r2`'s only
#: age resolution, and therefore the resolution of the communal correction.
COARSE = [('Y_LT15', 0, 14), ('Y15-29', 15, 29), ('Y30-49', 30, 49),
          ('Y50-64', 50, 64), ('Y65-84', 65, 84), ('Y_GE85', 85, 200)]

#: `cens_11htts_r2` hhcomp -> our five. `REP*` (registered partnership) is
#: present in the codelist and is 0 for Italy in 2011; kept in the mapping so
#: the partition check below cannot pass by ignoring it.
HH_MAP = {
    'one_person':                  ['P1'],
    'couple_no_children':          ['MAR_NCH', 'CSU_NCH', 'REP_NCH'],
    'couple_with_children':        ['MAR_YCH', 'MAR_OCH', 'CSU_YCH', 'CSU_OCH',
                                    'REP_YCH', 'REP_OCH'],
    'single_parent_with_children': ['M1_CH', 'F1_CH'],
    'other_complex':               ['FAM_GE2', 'MULTI'],
}
HH_ORDER = ['one_person', 'couple_no_children', 'couple_with_children',
            'single_parent_with_children', 'other_complex', 'unknown']

ECON_ORDER = ['employed', 'unemployed', 'student', 'retired', 'homemaker',
              'other_inactive', 'unknown']


class BuildError(RuntimeError):
    pass


def need(cond, msg):
    """A check that refuses rather than warns. Every identity below is an
    equality the sources assert about themselves; if one breaks, the file we
    would write is not the census."""
    if not cond:
        raise BuildError(msg)


# --------------------------------------------------------------------------
# JSON-stat reader
# --------------------------------------------------------------------------
def jsonstat(path):
    d = json.load(open(path))
    ids = d.get('id') or list(d['dimension'])
    sizes = d.get('size') or [len(d['dimension'][k]['category']['index']) for k in ids]
    idx = {}
    for k in ids:
        ci = d['dimension'][k]['category']['index']
        if isinstance(ci, list):
            ci = dict((c, i) for i, c in enumerate(ci))
        idx[k] = ci
    val = d['value']

    def get(**sel):
        pos = 0
        for k, n in zip(ids, sizes):
            pos = pos * n + idx[k][sel[k]]
        v = val.get(str(pos))
        return 0 if v is None else v
    return idx, get


# --------------------------------------------------------------------------
# ISTAT census-tract aggregation -- from the zip, every tract, every region
# --------------------------------------------------------------------------
def istat_national(zip_path):
    z = zipfile.ZipFile(zip_path)
    members = sorted(m for m in z.namelist()
                     if m.startswith('Sezioni di Censimento/R')
                     and m.endswith('_sezioni.csv'))
    need(len(members) == 20,
         'expected 20 regional tract files, found %d -- a partial archive would '
         'give a national total that is silently short' % len(members))
    hdr = None
    tot = None
    first = None
    nrow = 0
    nnull = {}
    for m in members:
        with z.open(m) as fh:
            r = io.TextIOWrapper(fh, encoding='latin-1', newline='')
            head = r.readline().rstrip('\r\n').split(';')
            if hdr is None:
                hdr = head
                first = hdr.index('P1')
                tot = [0] * len(hdr)
            need(head == hdr, 'header mismatch in %s' % m)
            for line in r:
                line = line.rstrip('\r\n')
                if not line:
                    continue
                f = line.split(';')
                need(len(f) == len(hdr), '%s: %d fields, expected %d'
                     % (m, len(f), len(hdr)))
                nrow += 1
                for i in range(first, len(hdr)):
                    v = f[i].strip()
                    if v == '' or v.lower() == 'null':
                        nnull[hdr[i]] = nnull.get(hdr[i], 0) + 1
                        continue
                    tot[i] += int(v)
    out = dict((hdr[i], tot[i]) for i in range(first, len(hdr)))
    return out, nrow, nnull


# --------------------------------------------------------------------------
def build(outdir):
    raw = os.path.join(outdir, 'raw')
    log = []

    def say(s=''):
        log.append(s)
        print(s)

    # ---------------- sources ------------------------------------------
    zpath = os.path.join(raw, ISTAT_ZIP)
    need(os.path.exists(zpath),
         'ISTAT tract archive missing: %s\n  retrieve with:  curl -L -o "%s" "%s"'
         % (zpath, zpath, ISTAT_URL))
    P, nrow, nnull = istat_national(zpath)
    say('ISTAT %s: %d tracts aggregated, 20 regions' % (ISTAT_ZIP, nrow))
    say('  null cells: %s' % (nnull if nnull else 'NONE'))
    need(not [k for k in nnull if k.startswith(('P', 'PF'))],
         'null cells in a P/PF variable we use: %s' % nnull)

    idx_a, A = jsonstat(os.path.join(raw, ESTAT['age'][1]))
    idx_h, H = jsonstat(os.path.join(raw, ESTAT['hh'][1]))
    idx_o, O = jsonstat(os.path.join(raw, ESTAT['hou'][1]))
    idx_e, E = jsonstat(os.path.join(raw, ESTAT['aed'][1]))

    def age(a, s='T'):
        return A(freq='A', age=a, sex=s, unit='NR', geo='IT', time='2011')

    def yr(y, s='T'):
        return age('Y_LT1' if y == 0 else 'Y%d' % y, s)

    def pop(lo, hi, s='T'):
        if hi >= 100:
            return sum(yr(y, s) for y in range(lo, 100)) + age('Y_GE100', s)
        return sum(yr(y, s) for y in range(lo, hi + 1))

    def hh(c):
        return H(freq='A', hhcomp=c, tenure='TOTAL', unit='NR', geo='IT', time='2011')

    def hou(h, a='TOTAL', s='T'):
        return O(freq='A', sex=s, age=a, housing=h, unit='NR', geo='IT', time='2011')

    def wst(w):
        return E(freq='A', age='TOTAL', sex='T', wstatus=w, isced97='TOTAL',
                 unit='NR', geo='IT', time='2011')

    # ---------------- 1. ISTAT internal identities ----------------------
    say()
    say('--- ISTAT internal identities (all must be residual 0) ---')
    checks = [
        ('P14..P29 == P1', sum(P['P%d' % i] for i in range(14, 30)), P['P1']),
        ('P2+P3 == P1', P['P2'] + P['P3'], P['P1']),
        ('P30..P45 == P2', sum(P['P%d' % i] for i in range(30, 46)), P['P2']),
        ('P130+P131+P135+P139 == P128',
         P['P130'] + P['P131'] + P['P135'] + P['P139'], P['P128']),
        ('P17..P29 == P60+P128',
         sum(P['P%d' % i] for i in range(17, 30)), P['P60'] + P['P128']),
        ('PF3..PF8 == PF1', sum(P['PF%d' % i] for i in range(3, 9)), P['PF1']),
        ('size-weighted PF == PF2',
         P['PF3'] + 2 * P['PF4'] + 3 * P['PF5'] + 4 * P['PF6'] + 5 * P['PF7'] + P['PF9'],
         P['PF2']),
    ]
    for name, got, want in checks:
        say('  %-28s %14d vs %14d  residual %d' % (name, got, want, got - want))
        need(got == want, 'ISTAT identity broken: %s (%d vs %d)' % (name, got, want))

    # ---------------- 2. cross-source identities ------------------------
    say()
    say('--- ISTAT vs Eurostat, the same census by two routes ---')
    cross = [
        ('total population', age('TOTAL'), P['P1']),
        ('males', age('TOTAL', 'M'), P['P2']),
        ('females', age('TOTAL', 'F'), P['P3']),
        ('ages 10-14', pop(10, 14), P['P16']),
        ('ages 15-24', pop(15, 24), P['P17'] + P['P18']),
        ('ages 25-34', pop(25, 34), P['P19'] + P['P20']),
        ('ages 35-44', pop(35, 44), P['P21'] + P['P22']),
        ('ages 45-54', pop(45, 54), P['P23'] + P['P24']),
        ('ages 55-64', pop(55, 64), P['P25'] + P['P26']),
        ('ages 65-74', pop(65, 74), P['P27'] + P['P28']),
        ('ages 75+', pop(75, 200), P['P29']),
        ('labour force', wst('ACT'), P['P60']),
        ('employed', wst('EMP'), P['P61']),
        ('unemployed', wst('UNE'), P['P60'] - P['P61']),
        ('inactive (incl. <15)', wst('INAC'),
         P['P128'] + P['P14'] + P['P15'] + P['P16']),
    ]
    for name, e, i in cross:
        say('  %-22s eurostat %12d  istat %12d  residual %d' % (name, e, i, e - i))
        need(e == i, 'the two routes disagree on %s: %d vs %d -- they are supposed '
                     'to be the same tabulation, so a disagreement means one of '
                     'them is not the 2011 census' % (name, e, i))
    need(wst('UNK') == 0, 'Eurostat reports non-zero UNK activity status for Italy')
    say('  activity-status UNK = 0, so the economic classification covers 100 % of 15+')

    # ---------------- 3. private-household frame ------------------------
    say()
    say('--- D-S5-5: the private-household frame ---')
    priv_all = P['PF2']
    conviv = P['P1'] - priv_all
    clq_tot = hou('CLQ')
    k = float(conviv) / clq_tot
    say('  PF2 persons in famiglie      %12d' % priv_all)
    say('  P1 - PF2 convivenze          %12d   (%.4f %% of P1)'
        % (conviv, 100.0 * conviv / P['P1']))
    say('  Eurostat CLQ                 %12d   differs by %d (%.4f %% of P1)'
        % (clq_tot, clq_tot - conviv, 100.0 * (clq_tot - conviv) / P['P1']))
    say('  scale k = convivenze / CLQ = %.6f   (UK used the same construction, k=1.12096051)'
        % k)
    need(sum(hou('CLQ', a) for a, _, _ in COARSE) == clq_tot,
         'Eurostat CLQ coarse bands do not sum to the CLQ total')

    # collective persons per OUR band, by pushing each coarse CLQ count onto
    # the fine bands in proportion to single-year population inside it.
    clq_band = dict((b, 0.0) for b, _, _ in BANDS)
    clq_sex = {'M': 0.0, 'F': 0.0}
    for cb, clo, chi in COARSE:
        cpop = pop(clo, chi)
        need(cpop > 0, 'coarse band %s has zero population' % cb)
        c_t = hou('CLQ', cb)
        for b, blo, bhi in BANDS:
            lo, hi = max(blo, clo), min(bhi, chi)
            if lo > hi:
                continue
            clq_band[b] += c_t * float(pop(lo, hi)) / cpop
        for s in ('M', 'F'):
            spop = pop(clo, chi, s)
            lo, hi = max(11, clo), min(200, chi)
            if lo > hi or spop <= 0:
                continue
            clq_sex[s] += hou('CLQ', cb, s) * float(pop(lo, hi, s)) / spop

    rows = []

    # ---------------- 4. age --------------------------------------------
    say()
    say('--- strat_age_band (Eurostat single-year, minus scaled convivenze) ---')
    age_priv = {}
    for b, lo, hi in BANDS:
        allres = pop(lo, hi)
        age_priv[b] = allres - k * clq_band[b]
    base11 = sum(age_priv.values())
    for b, lo, hi in BANDS:
        say('  %-6s all_residents %12d  private_hh %14.2f  removed %8.2f'
            % (b, pop(lo, hi), age_priv[b], k * clq_band[b]))
        rows.append(dict(
            field='strat_age_band', category=b, count='%.2f' % age_priv[b],
            share='%.6f' % (age_priv[b] / base11),
            base_name='persons_aged_11_and_over_in_private_households',
            base_count='%.2f' % base11,
            source_table='cens_11ag_r3 + dati-cpa_2011(PF2,P1) + cens_11hou_r2',
            source_cell_code='age=Y%d..Y%s sex=T, minus CLQ profile scaled k=%.8f'
                             % (lo, ('GE100' if hi >= 100 else str(hi)), k),
            source_url=ESTAT_URL % ESTAT['age'][0], download_date=DL_DATE,
            status='PRIVATE_HH_D-S5-5_ISTAT_TOTAL_EUROSTAT_PROFILE'))
    say('  base 11+ in private households = %.2f' % base11)

    # ---------------- 5. sex --------------------------------------------
    say()
    say('--- strat_sex (Eurostat single-year 11+, EXACT base -- not the UK approximation) ---')
    sex_priv = {}
    for s, nm in (('M', 'male'), ('F', 'female')):
        sex_priv[nm] = pop(11, 200, s) - k * clq_sex[s]
    sex_tot = sum(sex_priv.values())
    say('  sex partition %.2f vs age base %.2f  residual %.4f'
        % (sex_tot, base11, sex_tot - base11))
    need(abs(sex_tot - base11) < 1.0,
         'sex and age bases disagree by %.4f persons' % (sex_tot - base11))
    for nm in ('male', 'female'):
        say('  %-7s %14.2f  share %.6f' % (nm, sex_priv[nm], sex_priv[nm] / sex_tot))
        rows.append(dict(
            field='strat_sex', category=nm, count='%.2f' % sex_priv[nm],
            share='%.6f' % (sex_priv[nm] / sex_tot),
            base_name='persons_aged_11_and_over_in_private_households',
            base_count='%.2f' % sex_tot,
            source_table='cens_11ag_r3 + dati-cpa_2011(PF2,P1) + cens_11hou_r2',
            source_cell_code='sex=%s age 11+, minus CLQ profile scaled k=%.8f'
                             % (nm[0].upper(), k),
            source_url=ESTAT_URL % ESTAT['age'][0], download_date=DL_DATE,
            status='EXACT_11PLUS_BASE_PRIVATE_HH_D-S5-5'))

    # ---------------- 6. economic status --------------------------------
    say()
    say('--- strat_econ_status (ISTAT 15+, ALL RESIDENTS -- see the bound below) ---')
    econ = {
        'employed':       P['P61'],
        'unemployed':     P['P60'] - P['P61'],
        'student':        P['P131'],
        'retired':        P['P139'],
        'homemaker':      P['P130'],
        'other_inactive': P['P135'],
        'unknown':        0,
    }
    econ_base = P['P60'] + P['P128']
    need(sum(econ.values()) == econ_base,
         'economic bands sum to %d, base 15+ is %d' % (sum(econ.values()), econ_base))
    say('  partition_sum %d == base_15plus %d  residual 0' % (sum(econ.values()), econ_base))
    for c in ECON_ORDER:
        say('  %-15s %12d  share %.6f' % (c, econ[c], float(econ[c]) / econ_base))
        rows.append(dict(
            field='strat_econ_status', category=c, count='%d' % econ[c],
            share='%.6f' % (float(econ[c]) / econ_base),
            base_name='persons_aged_15_and_over_ALL_RESIDENTS',
            base_count='%d' % econ_base,
            source_table='dati-cpa_2011 sezioni',
            source_cell_code={'employed': 'P61', 'unemployed': 'P60-P61',
                              'student': 'P131', 'retired': 'P139',
                              'homemaker': 'P130', 'other_inactive': 'P135',
                              'unknown': 'NONE'}[c],
            source_url=ISTAT_URL, download_date=DL_DATE,
            status=('NOT_PUBLISHED_census_has_no_nonresponse_band' if c == 'unknown'
                    else 'ALL_RESIDENTS_15PLUS_D-S5-5_NOT_APPLIED_no_published_'
                         'residence_by_activity_table_for_IT')))

    # the bound: what the private-household restriction could at most do.
    # Collective residents aged 15+. `Y_LT15` is 0-14 entirely, so it drops
    # out whole and no within-band assumption is needed for this number.
    clq15 = k * (clq_tot - hou('CLQ', 'Y_LT15'))
    say()
    say('  BOUND on the unapplied D-S5-5 correction (worst case: every collective')
    say('  resident aged 15+ is `retired`) -- %.0f persons, %.4f %% of the 15+ base:'
        % (clq15, 100.0 * clq15 / econ_base))
    for c in ECON_ORDER:
        now = 100.0 * econ[c] / econ_base
        if c == 'retired':
            then = 100.0 * (econ[c] - clq15) / (econ_base - clq15)
        else:
            then = 100.0 * econ[c] / (econ_base - clq15)
        say('    %-15s %7.4f %%  ->  %7.4f %%   (%+0.4f pp)' % (c, now, then, then - now))

    # ---------------- 7. household type ---------------------------------
    say()
    say('--- strat_hh_type (cens_11htts_r2, natively PRIVATE households) ---')
    hh_tot = hh('TOTAL')
    named = sum(hh(c) for cats in HH_MAP.values() for c in cats)
    say('  Eurostat private households TOTAL %12d' % hh_tot)
    say('  mapped categories sum             %12d  residual %d' % (named, named - hh_tot))
    need(named == hh_tot,
         'the five categories sum to %d but the published total is %d -- a household '
         'type that maps nowhere is a silent deletion' % (named, hh_tot))
    say('  ISTAT PF1 famiglie                %12d  differs by %d (%.4f %%)'
        % (P['PF1'], hh_tot - P['PF1'], 100.0 * (hh_tot - P['PF1']) / P['PF1']))
    need(hh('REP') == 0,
         'REP (registered partnership) is non-zero for Italy 2011; the mapping '
         'assumed it empty')
    for c in HH_ORDER:
        v = 0 if c == 'unknown' else sum(hh(x) for x in HH_MAP[c])
        say('  %-28s %12d  share %.6f' % (c, v, float(v) / hh_tot))
        rows.append(dict(
            field='strat_hh_type', category=c, count='%d' % v,
            share='%.6f' % (float(v) / hh_tot),
            base_name='private_households', base_count='%d' % hh_tot,
            source_table='cens_11htts_r2',
            source_cell_code=('NONE' if c == 'unknown' else '+'.join(HH_MAP[c])),
            source_url=ESTAT_URL % ESTAT['hh'][0], download_date=DL_DATE,
            status=('NOT_PUBLISHED_census_has_no_nonresponse_band' if c == 'unknown'
                    else 'EXACT_WITHIN_BASE_PRIVATE_HOUSEHOLDS')))

    # ---------------- 8. write marginals_it.csv -------------------------
    cols = ['field', 'category', 'count', 'share', 'base_name', 'base_count',
            'source_table', 'source_cell_code', 'source_url', 'download_date',
            'status']
    mpath = os.path.join(outdir, 'marginals_it.csv')
    with io.open(mpath, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        fh.write(
            '# ROUTE: ISTAT static census-tract release (national office, D-S5-1 route 3) for the\n'
            '# private-household base and every economic band; Eurostat 2011 Census Hub for single-year\n'
            '# age, the sex-by-age split, the collective-quarters profile and household type -- the two\n'
            '# routes were verified identical to the person on all 15 quantities they share.\n'
            '# ISTAT zip md5 %s from %s\n'
            '# k_convivenze = %.8f = %d / %d\n'
            % (ISTAT_MD5, ISTAT_URL, k, conviv, clq_tot))

    # ---------------- 9. econ_11plus_it.csv -----------------------------
    # 🔴 Italy publishes 15+, so D-S5-3's uk/es repairs do NOT apply: age 15 is
    # published, 75+ is published, and `unknown` is the 11-14 band alone.
    say()
    say('--- econ_11plus_it.csv (D-S5-3 applies ONLY its 11-14 clause here) ---')
    # 🔴 THE BASE MISMATCH, AND WHY RESCALING IS THE ONLY HONEST CLOSE.
    # The six economic bands are ALL-RESIDENTS 15+ (51,107,701); the age base is
    # PRIVATE-HOUSEHOLD 11+. Writing them into one partition unchanged leaves a
    # residual of exactly the collective 15+ population, 295,531.65 persons --
    # a `FINDING 50`-class mixture of two universes, not a rounding. So the
    # composition is carried onto the private-household 15+ total: the
    # collective population is assumed to share the private-household economic
    # composition.
    #
    # 🔴 THIS ASSUMPTION CANNOT MOVE `G6.1`. `rake()` consumes SHARES, and a
    # proportional rescaling leaves every share bit-identical; it changes only
    # the base, which is what makes the file internally consistent. The BOUND
    # printed above is what the assumption is worth if it is wrong, and the
    # worst band moves 0.44 pp.
    econ15_priv = base11 - age_priv['11-14']
    say('  collective 15+          %14.2f' % clq15)
    say('  all-residents 15+ base  %14d' % econ_base)
    say('  private-hh 15+ base     %14.2f   (= base11 - band 11-14)' % econ15_priv)
    say('  cross-check base_15plus - collective_15plus = %.2f  residual %.4f'
        % (econ_base - clq15, (econ_base - clq15) - econ15_priv))
    need(abs((econ_base - clq15) - econ15_priv) < 1.0,
         'the private-household 15+ base derived two independent ways disagrees '
         'by %.4f persons' % ((econ_base - clq15) - econ15_priv))

    e11 = dict((c, float(econ[c]) / econ_base * econ15_priv) for c in ECON_ORDER)
    e11['unknown'] = age_priv['11-14']
    tot11 = sum(e11.values())
    say('  11-14 -> unknown        %14.2f' % e11['unknown'])
    say('  age 15   PUBLISHED (uk/es imputed it to `unknown`)')
    say('  75+      PUBLISHED (uk/es imputed it to `retired`)')
    say('  partition_sum %.2f  vs base_11plus %.2f  residual %.4f'
        % (tot11, base11, tot11 - base11))
    need(abs(tot11 - base11) < 1.0,
         'econ_11plus partition misses the 11+ base by %.4f persons' % (tot11 - base11))
    for c in ECON_ORDER:
        say('  %-15s %14.2f  share %.6f' % (c, e11[c], e11[c] / tot11))

    epath = os.path.join(outdir, 'econ_11plus_it.csv')
    with io.open(epath, 'w', newline='', encoding='utf-8') as fh:
        fh.write('field,category,count,share,base_name,base_count,source_table,'
                 'derivation,source_url,download_date,status\n')
        for c in ECON_ORDER:
            der = ('D-S5-3_band_11-14_only_age15_and_75plus_are_PUBLISHED'
                   if c == 'unknown' else
                   'published_15_plus_share_rescaled_to_private_hh_base')
            fh.write('strat_econ_status,%s,%.2f,%.6f,'
                     'persons_aged_11_and_over_in_private_households,%.2f,'
                     'dati-cpa_2011 sezioni,%s,%s,%s,%s\n'
                     % (c, e11[c], e11[c] / tot11, tot11, der, ISTAT_URL, DL_DATE,
                        'D-S5-3_11-14_CLAUSE_ONLY_ITALY_PUBLISHES_15PLUS'))
        fh.write('# 🔴 it differs from uk/es: age 15 and 75+ are PUBLISHED here, so `unknown`\n'
                 '# holds the 11-14 band ALONE and `retired` carries no imputation.\n'
                 '# 🔴 the six economic bands are on ALL RESIDENTS 15+; D-S5-5 could not be\n'
                 '# applied to this field (no published IT residence-type x activity table).\n'
                 '# base_11plus %.2f  band_11-14 %.2f  base_15plus %d\n'
                 '# partition_sum %.2f  residual_vs_base_11plus %.2f\n'
                 % (base11, e11['unknown'], econ_base, tot11, tot11 - base11))

    say()
    say('WROTE %s' % mpath)
    say('WROTE %s' % epath)
    return log


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        sys.exit(2)
    try:
        build(sys.argv[1])
    except BuildError as exc:
        print('BUILD REFUSED: %s' % exc, file=sys.stderr)
        sys.exit(1)
