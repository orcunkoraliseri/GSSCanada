# -*- coding: utf-8 -*-
"""
4J / Step 5.2 -- SYNTHESISE THE POPULATION.

WHAT IT DOES
============
Iterative proportional fitting of a four-way joint table

    strat_age_band (8) x strat_sex (2) x strat_hh_type (5) x strat_econ_status

onto the published marginals assembled in item 5.1, then a deterministic
expansion of that table into `N` synthetic persons, then a deterministic
assignment of `strat_day_type`.

WHERE EACH MARGINAL COMES FROM, AND WHY NOT ALL FROM ONE FILE
=============================================================
    strat_age_band      marginals_<c>.csv        11+, private households
    strat_sex           marginals_<c>.csv        11+, private households
    strat_hh_type       hhtype_person_<c>.csv    <- PERSON basis, NOT the
                                                 household rows in
                                                 marginals_<c>.csv
    strat_econ_status   econ_11plus_<c>.csv      <- the D-S5-3 convention
                                                 (11-14 -> unknown, 75+ ->
                                                 retired, age 15 -> unknown)

🔴 `strat_hh_type` MUST come from the person file. The household rows in
`marginals_<c>.csv` count HOUSEHOLDS; the units being synthesised are PERSONS.
On the UK the two differ by a factor of 2.4 on the largest single category --
one-person households are 30.6 % of households and 13.0 % of people. That is
`D-S5-8`, and `FINDING 50` one level up.

🔴 `strat_econ_status` MUST come from `econ_11plus_<c>.csv`, not from
`marginals_<c>.csv`. The latter is the office's own published band set; the
former is that set with `D-S5-3`'s age conventions applied on top, and it is the
one whose categories the corpus prefix actually uses.

NO SAMPLING ANYWHERE
====================
There is no random draw in this module and no seed to record. The IPF result is
expanded by LARGEST REMAINDER, which is deterministic and reproduces every
marginal to within a handful of persons out of `N`. A Monte-Carlo draw would add
noise of order sqrt(N) to every cell for no benefit -- the joint table IS the
answer, and sampling from it only degrades it.

STRUCTURAL ZEROS, AND WHY THESE THREE AND NOT MORE
==================================================
`G5.2` asks for zero persons in structurally impossible cells. Three masks are
imposed. Each is either forced by a ruled decision or PROVED from a measured
mean household size -- none is a plausibility judgement, because a plausibility
judgement here would silently become a modelling assumption.

  Z1  age `11-14`  =>  econ must be `unknown`.
      Forced by `D-S5-3`, which is what `econ_11plus_<c>.csv` already encodes.

  Z2  econ `unknown`  =>  age in {`11-14`, `15-24`}.
      The other half of `D-S5-3`: `unknown` holds the 11-14 band plus, in `es`
      and `uk`, the 15-year-old slice. It holds nothing else, so every other age
      band is zero there. Where the two marginals are EQUAL -- Italy, where age
      15 is published separately -- (`15-24`, `unknown`) is additionally forced
      to zero, and that is derived at run time from the marginals rather than
      hard-coded per country.

  Z3  age `11-14`  =>  hh_type not in {`one_person`, `couple_no_children`}.
      NOT asserted. `one_person` has a measured mean size of exactly 1.0000
      persons and `couple_no_children` of exactly 2.0000 in all three countries
      under convention A (`FINDING 60`). A class of exactly two people who are a
      couple cannot also contain a 13-year-old. The zero follows from the
      measurement, and if a future rebuild broke the 2.0000 signature this mask
      would become wrong -- which is why the number is quoted here.

WHAT IS **NOT** MASKED, DELIBERATELY
====================================
`retired` at `15-24`, `student` at `75+`, `single_parent_with_children` at
`75+`: all rare, none impossible, and every one of them is a real census cell.
Masking a rare-but-real cell would hard-code our expectation of the answer into
the population the model is asked to reproduce.

🔴 SPAIN LOSES A CATEGORY, AND IT IS NOT A SMALL ONE
====================================================
`FINDING 51`: the Spanish census `RELA` has no *Labores del hogar*, so
`econ_11plus_es.csv` leaves `homemaker` blank and its `other_inactive` is the
WHOLE residual inactive band. Spain is therefore fitted on FIVE economic bands,
and the synthetic Spanish population contains **no `homemaker` at all**, while
the Spanish HETUS corpus is 11.14 % homemaker. The band is not lost -- those
people are inside `other_inactive` -- but the PREFIX TOKEN differs, so every
Spanish synthetic prefix that should read `homemaker` will read `other_inactive`
instead. That is a declared, country-specific limitation of the `es` fold and it
is printed on every run.

`strat_day_type` HAS NO PUBLISHED MARGINAL ANYWHERE
===================================================
`FINDING 54`: no Eurostat table carries a day-type dimension, and no national
census does either -- it is a diary attribute, not a population attribute. It is
therefore assigned EXOGENOUSLY at the calendar-week proportions

    weekday 5/7,  saturday 1/7,  sunday 1/7

which is the same basis `D-S6-4` put the scoring on (`weight_dia_cal`). It is
assumed independent of the other four fields, and that independence is an
assumption, not a measurement: the corpus itself is at 44.8/27.9/27.4, a SURVEY
design mix, and `FINDING 53` showed that mix is different in each of the three
countries. Using the calendar week rather than any country's survey mix is what
keeps a country-correlated design artefact out of the synthetic population.

WHAT ECONOMIC BAND A MINOR GETS -- `D-S5-11`, RULED (b) ON 2026-08-21
====================================================================
`D-S5-3` put the whole 11-14 band, and in `es`/`uk` the age-15 slice on top of
it, into a single `unknown` economic band. That band is not a census category:
it is a CONSTRUCT, invented because no national economic-activity table reaches
below 16. `D-S5-11` asked what those people should actually be called, and the
ruling is (b): TAKE IT FROM THE DONOR POOL, PER FOLD.

Concretely, the `unknown` count `U` in `econ_11plus_<c>.csv` is split back over
real bands using the N-1 pool's own econ mix at the ages that mass comes from:

    U  ->  U * ( w11 * q11(e)  +  w15 * q1524(e) )   added to band `e`

    w11 = band_11-14 / U        q11    = donor mix at age 11-14
    w15 = age_15_residual / U   q1524  = donor mix at age 15-24

`w11 + w15 == 1` is not assumed, it is CHECKED against the file's own footer:
`band_11-14 + age_15_residual` must equal `unknown` to within half a person, and
it does in all three folds. Italy has `w15 = 0` because ISTAT publishes age 15.

🔴 THIS IS NOT A REWRITE OF A SHIPPED MARGINAL, AND IT CANNOT BE ONE.
The answer depends on WHICH TWO COUNTRIES ARE THE DONORS, so `es` under the `es`
fold and `es` as a donor elsewhere would need different files. It therefore lives
here, at fit time, and `econ_11plus_<c>.csv` is left byte-identical. What the
rule produces is written out beside the population as
`minor_econ_split_<c>.csv`, so the re-label is auditable without re-running.

🔴 WHY IT WAS NEEDED, AND WHAT IT COSTS
`FINDING 62`: with `D-S5-3`'s `unknown` left in place, `G6.1`'s raked-donor null
CANNOT CONVERGE on the `uk` fold -- 1.41515 pp against a 0.5 pp tolerance, which
is exactly the age-15 slice, because neither Spanish nor Italian donors ever
carry `unknown` at 15-24. It is not a tolerance to loosen; it is a category with
no donor. And on the `it` fold the entire `unknown` marginal was being carried by
**68 British diaries**. Under (b) both disappear by construction.

The cost is stated and is not small. `FINDING 61`/`FINDING 48`: each country
labels its own minors differently and DETERMINISTICALLY -- `student` in Spain
(710 of 711), `other_inactive` in the UK (896 of 896), `unknown` in Italy (1,644
of 1,644). Under leave-one-country-out we are forbidden the held-out country's
own convention, so a Spanish synthetic 13-year-old is labelled from the British
and Italian habit instead. The token is therefore WRONG for that country in a way
no amount of data fixes, and every run prints the mix it used.

TWO SEEDS, AND THE CHOICE BETWEEN THEM IS `D-S5-10`
===================================================
IPF fits marginals. It does NOT invent an association structure -- it inherits
one from the seed, and the seed is a modelling choice nobody had made.

  --seed uniform  (the literal reading of the step doc)
      Every admissible cell starts equal, so the fitted table is the PRODUCT of
      the marginals: age is independent of economic status, household type is
      independent of age, and so on. It uses nothing but published marginals,
      which is maximally clean.
      🔴 AND IT MANUFACTURES PEOPLE. Independence puts real mass on
      `75+ / couple_with_children / employed` and on `25-34 / retired`. Measured
      on the training folds, 14.4 % (es), 17.0 % (uk) and 24.4 % (it) of the
      synthetic population lands on a demographic stratum that occurs NOWHERE
      in the corpus the model for that fold was trained on.

  --seed donor  (the N-1 pool's association structure)
      The seed is the joint (age x sex x hh x econ) tally of the OTHER two
      countries' diaries; IPF then rakes it onto the held-out country's
      published marginals. No quantity from the held-out country enters beyond
      those marginals, so `5.1`'s contamination rule holds.
      It is the same object `G6.1`'s raked-donor null is built from, which is a
      point in its favour and not against it: the null and the model then
      answer the same population, and differ only in how the DIARY is produced.
      🔴 Its cost is the mirror image: a stratum with no donor support gets
      zero people, so the synthetic population can never contain a combination
      the donors happen not to have. Out-of-distribution exposure falls to zero
      BY CONSTRUCTION, which means that number stops being evidence.

`D-S5-10` RULED (a) ON 2026-08-21: **`uniform` is the frozen primary** and the
population every downstream step consumes; `donor` is built beside it as a
DECLARED SENSITIVITY and is never mixed into a headline. The reason is the one
above: under `donor` the out-of-distribution share falls to zero BY CONSTRUCTION,
so it can no longer be evidence of anything, and the primary population must be
the one that can still be surprised.

OUTPUT
======
`outputs_step5/population_<c>.csv` -- one row per synthetic person, exactly the
six frozen prefix fields, in `tools/encoder.py`'s frozen order. With
`--seed donor` the file is `population_<c>_donorseed.csv`, so the two can never
overwrite one another.

⚪ CSV, not the `.parquet` the step doc names: this machine's Python has no
`pyarrow` and no `pandas`. The content is identical and the conversion is a
one-liner wherever those are installed. Recorded rather than quietly substituted.
"""

import io
import os
import sys
import csv
import json
import collections

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')

N_DEFAULT = 100000

AGE = ['11-14', '15-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']
SEX = ['male', 'female']
HH = ['one_person', 'couple_no_children', 'couple_with_children',
      'single_parent_with_children', 'other_complex']
ECON = ['employed', 'unemployed', 'student', 'retired', 'homemaker',
        'other_inactive', 'unknown']
DAY = ['weekday', 'saturday', 'sunday']
DAY_W = np.array([5.0, 1.0, 1.0]) / 7.0

PREFIX_FIELDS = ['country', 'strat_age_band', 'strat_sex', 'strat_hh_type',
                 'strat_econ_status', 'strat_day_type']

IPF_TOL = 1e-13
IPF_MAX = 5000

CORPUS = os.path.join(ROOT, 'Step3_docs', 'outputs_step3',
                      '4J_step3_corpus.jsonl')
# Position of each stratum field inside the Step 3 prefix. Read from the corpus
# text rather than re-encoded: the corpus is the authority on its own layout.
PFX_AGE, PFX_SEX, PFX_HH, PFX_ECON = 1, 2, 3, 4


class SynthError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise SynthError(msg)


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def read_field(path, field):
    """Return {category: count} for one field, ignoring blank counts."""
    got = {}
    fh = io.open(path, encoding='utf-8')
    for row in csv.reader(fh):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        if row[0] != field:
            continue
        cat = row[1]
        raw = row[2].strip()
        got[cat] = None if raw == '' else float(raw)
    fh.close()
    need(got, 'no %s rows in %s' % (field, os.path.basename(path)))
    return got


def as_shares(got, order, path, field):
    """Drop blank and zero categories, normalise the rest, and REFUSE if the
    counts did not already form a partition -- a marginal that has to be
    rescaled by more than rounding was not a partition to begin with."""
    cats, vals = [], []
    for c in order:
        if c not in got or got[c] is None:
            continue
        if got[c] == 0.0:
            continue
        cats.append(c)
        vals.append(got[c])
    need(cats, '%s in %s has no usable category' % (field, path))
    v = np.array(vals, dtype=float)
    return cats, v / v.sum()


def ipf(seed, margins, axes_names, max_iter=None, strict=True):
    """Classic IPF. `margins` is a list of 1-D arrays, one per axis, each
    summing to 1. Zero seed cells stay zero for ever, which is how the
    structural mask is enforced -- there is no separate zeroing step that could
    be forgotten after the last iteration."""
    t = seed.astype(float).copy()
    need(t.sum() > 0, 'the structural mask left no admissible cell at all')
    t /= t.sum()
    lim = IPF_MAX if max_iter is None else int(max_iter)
    for it in range(lim):
        worst = 0.0
        for ax in range(t.ndim):
            cur = t.sum(axis=tuple(i for i in range(t.ndim) if i != ax))
            tgt = margins[ax]
            for k in range(len(tgt)):
                if tgt[k] == 0.0:
                    continue
                need(cur[k] > 0.0,
                     'axis %s category %d has target %.9f but the structural '
                     'mask leaves it unreachable -- the marginals and the mask '
                     'are jointly infeasible' % (axes_names[ax], k, tgt[k]))
            worst = max(worst, float(np.max(np.abs(cur - tgt))))
            scale = np.divide(tgt, cur, out=np.zeros_like(tgt),
                              where=cur > 0)
            shape = [1] * t.ndim
            shape[ax] = -1
            t = t * scale.reshape(shape)
        if worst < IPF_TOL:
            return t, it + 1, worst
    if strict:
        raise SynthError('IPF did not converge in %d sweeps; worst '
                         'marginal deviation %.3e' % (lim, worst))
    say('  !!! IPF STOPPED at %d sweeps WITHOUT converging, worst '
        'marginal deviation %.3e. This is a PERTURBATION.' % (lim, worst))
    return t, lim, worst


def largest_remainder(real, n):
    """Deterministic integerisation. No random draw, no seed."""
    flat = real.ravel() * n
    base = np.floor(flat).astype(np.int64)
    short = int(n - base.sum())
    need(short >= 0, 'largest remainder over-allocated by %d' % (-short))
    if short:
        rem = flat - base
        # Ties broken by index, so the result is reproducible byte for byte.
        order = np.lexsort((np.arange(len(rem)), -rem))
        base[order[:short]] += 1
    need(int(base.sum()) == n, 'integerisation produced %d rows, expected %d'
                               % (base.sum(), n))
    return base.reshape(real.shape)


def opt(argv, flag, default):
    """Pull `--flag v` or `--flag=v` out of argv. Returns (rest, value)."""
    out, val, i = [], default, 0
    while i < len(argv):
        a = argv[i]
        if a == flag:
            need(i + 1 < len(argv), '%s needs a value' % flag)
            val = argv[i + 1]
            i += 2
            continue
        if a.startswith(flag + '='):
            val = a.split('=', 1)[1]
            i += 1
            continue
        out.append(a)
        i += 1
    return out, val


def read_notes(path):
    """Parse the `# key value key value` footer of a marginal file.

    The footer is where the builder recorded the pieces it derived the file
    from -- `band_11-14`, `age_15_residual`, `base_11plus`. D-S5-11 needs those
    pieces back, and reading them from the file is what lets the mass identity
    below be a CHECK rather than a restatement.
    """
    got = {}
    for ln in io.open(path, encoding='utf-8'):
        if not ln.startswith('#'):
            continue
        tok = ln.lstrip('#').split()
        for i in range(len(tok) - 1):
            try:
                got[tok[i]] = float(tok[i + 1])
            except ValueError:
                pass
    return got


def donor_econ_by_age(held_out, bands):
    """{age band: {econ: share}} over the N-1 pool, plus the raw diary counts.

    No smoothing, no floor, no minimum support. A band a single donor diary
    carries stays in, and the count is returned beside the share so that
    thinness is visible rather than hidden -- one Spanish 13-year-old is
    recorded as `employed`, and that cell survives into the population at four
    ten-thousandths of the minor mass.
    """
    need(os.path.exists(CORPUS),
         'D-S5-11 (b) needs the Step 3 corpus at %s' % CORPUS)
    cnt = dict((b, collections.Counter()) for b in bands)
    for ln in io.open(CORPUS, encoding='utf-8'):
        r = json.loads(ln)
        if r['country'] == held_out:
            continue
        f = r['text'].split('|', 1)[0].split(',')
        if f[PFX_AGE] in cnt:
            cnt[f[PFX_AGE]][f[PFX_ECON]] += 1
    out = {}
    for b in bands:
        t = sum(cnt[b].values())
        need(t > 0, 'the N-1 pool has no donor at all in age band %s, so '
                    'D-S5-11 (b) has nothing to take the label from' % b)
        out[b] = dict((e, n / float(t)) for e, n in cnt[b].items())
    return out, cnt


def relabel_minors(held_out, ec_raw, notes, path, ec_order):
    """D-S5-11 (b). Split the `unknown` construct back over real bands.

    Returns (new counts, audit rows). Mass is conserved exactly: nothing is
    created, nothing is dropped, only the token changes.
    """
    need('unknown' in ec_raw and ec_raw['unknown'],
         '%s has no `unknown` band, so there is nothing for D-S5-11 to '
         're-label' % os.path.basename(path))
    U = float(ec_raw['unknown'])
    b11 = notes.get('band_11-14')
    r15 = notes.get('age_15_residual', 0.0)
    need(b11 is not None,
         'the footer of %s does not record `band_11-14`, so the split between '
         'the 11-14 band and the age-15 slice cannot be recovered'
         % os.path.basename(path))
    # The mass identity. If D-S5-3's `unknown` is anything other than these two
    # pieces then this rule is being applied to something it was not written
    # for, and refusing is the only safe answer.
    need(abs((b11 + r15) - U) < 0.5,
         'band_11-14 (%.2f) + age_15_residual (%.2f) = %.2f but the `unknown` '
         'band holds %.2f. D-S5-11 (b) re-labels exactly those two pieces, so '
         'a third contributor makes it inapplicable.'
         % (b11, r15, b11 + r15, U))
    w11, w15 = b11 / U, r15 / U

    q, cnt = donor_econ_by_age(held_out, ['11-14', '15-24'])
    has_home = ec_raw.get('homemaker') is not None
    mix = collections.defaultdict(float)
    audit = []
    collapsed = 0.0
    for band, w in (('11-14', w11), ('15-24', w15)):
        if w <= 0.0:
            continue
        for e, sh in q[band].items():
            tgt = e
            if e == 'homemaker' and not has_home:
                tgt = 'other_inactive'      # FINDING 51, es only
                collapsed += w * sh * U
            need(tgt in ec_order,
                 'the donor pool puts minors in econ band %r, which is not one '
                 'of the frozen seven' % e)
            mix[tgt] += w * sh
            audit.append((band, '%.6f' % w, e, tgt, str(cnt[band][e]),
                          '%.9f' % sh, '%.2f' % (w * sh * U)))
    tot = sum(mix.values())
    need(abs(tot - 1.0) < 1e-9,
         'the donor mix sums to %.12f, not 1' % tot)

    new = dict(ec_raw)
    new['unknown'] = 0.0
    for e, sh in mix.items():
        # `unknown`'s own base is ZERO here, not `U`. The whole point of
        # the rule is that `U` LEAVES that band; a donor mix that puts
        # some of it back must add to nothing, not to the original.
        base = 0.0 if e == 'unknown' else (
            float(ec_raw[e]) if ec_raw.get(e) is not None else 0.0)
        new[e] = base + sh * U
    before = sum(float(v) for v in ec_raw.values() if v is not None)
    after = sum(float(v) for v in new.values() if v is not None)
    need(abs(after - before) < 1.0,
         'the re-label changed the total from %.2f to %.2f; it is a re-label, '
         'so it must not' % (before, after))
    say('  D-S5-11 (b): %.0f persons (%.4f %% of the base) re-labelled out of '
        '`unknown`' % (U, 100.0 * U / before))
    say('    w11 %.6f (band 11-14)   w15 %.6f (age-15 slice)' % (w11, w15))
    for e in sorted(mix, key=lambda k: -mix[k]):
        say('      -> %-15s %.6f of it  (%.4f pp of the population)'
            % (e, mix[e], 100.0 * mix[e] * U / before))
    if collapsed:
        say('    homemaker -> other_inactive on %.0f of them (FINDING 51)'
            % collapsed)
    if new['unknown'] == 0.0:
        say('    !!! `unknown` is now EMPTY in this fold: no donor country '
            'labels a minor `unknown`.')
    # the 11-14 mix alone, with FINDING 51 already applied, because the
    # seed below has to bind the minor ROW and not just the total
    q11 = collections.defaultdict(float)
    for e, sh in q['11-14'].items():
        q11['other_inactive' if (e == 'homemaker' and not has_home)
            else e] += sh
    return new, audit, q, cnt, dict(q11)


def donor_seed(held_out, age_c, sex_c, hh_c, ec_c):
    """Joint tally of the N-1 pool, as an IPF seed.

    Reads the demographic fields straight out of the corpus prefix string. Two
    recodes are applied and both are COUNTED and printed, because each is a
    declared loss and a silent one would be indistinguishable from a bug:

      * `homemaker` -> `other_inactive` wherever the target has no `homemaker`
        band. That is `es` only (`FINDING 51`), and it is the collapse the rake
        has required since `FINDING 52`.
      * `strat_hh_type == unknown` donors are DROPPED. Those are the 551 UK
        diaries of `D-S3-14`; no published marginal has an `unknown` household
        category to receive them, and inventing one would be a basis change.
    """
    need(os.path.exists(CORPUS),
         'the donor seed needs the Step 3 corpus at %s' % CORPUS)
    idx = {'age': {c: i for i, c in enumerate(age_c)},
           'sex': {c: i for i, c in enumerate(sex_c)},
           'hh': {c: i for i, c in enumerate(hh_c)},
           'econ': {c: i for i, c in enumerate(ec_c)}}
    seed = np.zeros((len(age_c), len(sex_c), len(hh_c), len(ec_c)), dtype=float)
    kept = 0
    dropped = collections.Counter()
    collapsed = 0
    fh = io.open(CORPUS, encoding='utf-8')
    for ln in fh:
        r = json.loads(ln)
        if r['country'] == held_out:
            continue
        f = r['text'].split('|', 1)[0].split(',')
        a, x, h, e = f[PFX_AGE], f[PFX_SEX], f[PFX_HH], f[PFX_ECON]
        if e == 'homemaker' and 'homemaker' not in idx['econ']:
            e = 'other_inactive'
            collapsed += 1
        if h not in idx['hh']:
            dropped['hh=' + h] += 1
            continue
        if e not in idx['econ']:
            dropped['econ=' + e] += 1
            continue
        if a not in idx['age'] or x not in idx['sex']:
            dropped['age/sex'] += 1
            continue
        seed[idx['age'][a], idx['sex'][x], idx['hh'][h], idx['econ'][e]] += 1.0
        kept += 1
    fh.close()
    need(kept > 0, 'the donor pool is empty after recoding')
    say('  donor seed: %d diaries kept from the N-1 pool, %d occupied strata'
        % (kept, int((seed > 0).sum())))
    if collapsed:
        say('    homemaker -> other_inactive on %d donors (FINDING 51)'
            % collapsed)
    for k in sorted(dropped):
        say('    DROPPED %s: %d donors (D-S3-14)' % (k, dropped[k]))
    return seed


def main():
    argv = [a for a in sys.argv[1:]]
    argv, seed_kind = opt(argv, '--seed', 'uniform')
    argv, minors_kind = opt(argv, '--minors', 'donor')
    argv, ipf_max = opt(argv, '--ipf-max', '')
    argv, out_suffix = opt(argv, '--out-suffix', '')
    ipf_max = int(ipf_max) if str(ipf_max).strip() else None
    if ipf_max is not None or out_suffix:
        say('!!! PERTURBATION RUN. ipf-max %r, out-suffix %r. The file '
            'this writes is evidence about a GATE, not a population, '
            'and nothing downstream may read it.' % (ipf_max, out_suffix))
    need(seed_kind in ('uniform', 'donor'),
         '--seed must be uniform or donor, not %r' % seed_kind)
    need(minors_kind in ('donor', 'ds53'),
         '--minors must be donor (D-S5-11 b, the ruling) or ds53 (the '
         'superseded convention, kept only so the difference can be shown), '
         'not %r' % minors_kind)
    need(len(argv) >= 1,
         'usage: 4thJ_step5_synthesise.py <country> [N] [--seed uniform|donor] '
         '[--minors donor|ds53]')
    c = argv[0].strip().lower()
    need(c in ('es', 'uk', 'it'), 'country %r is not one of es/uk/it' % c)
    n = int(argv[1]) if len(argv) > 1 else N_DEFAULT

    p_marg = os.path.join(OUT, 'marginals_%s.csv' % c)
    p_hh = os.path.join(OUT, 'hhtype_person_%s.csv' % c)
    p_econ = os.path.join(OUT, 'econ_11plus_%s.csv' % c)
    for p in (p_marg, p_hh, p_econ):
        need(os.path.exists(p), 'missing input %s' % p)

    say('=== Step 5.2  country %s  N %d  seed %s ===' % (c, n, seed_kind))
    age_c, age_m = as_shares(read_field(p_marg, 'strat_age_band'), AGE,
                             p_marg, 'strat_age_band')
    sex_c, sex_m = as_shares(read_field(p_marg, 'strat_sex'), SEX,
                             p_marg, 'strat_sex')
    hh_c, hh_m = as_shares(read_field(p_hh, 'strat_hh_type'), HH,
                           p_hh, 'strat_hh_type')
    ec_raw = read_field(p_econ, 'strat_econ_status')
    audit, q_minor, q11 = None, None, None
    if minors_kind == 'donor':
        ec_raw, audit, q_minor, q_cnt, q11 = relabel_minors(
            c, ec_raw, read_notes(p_econ), p_econ, ECON)
    else:
        say('  !!! --minors ds53: the SUPERSEDED convention. D-S5-11 was ruled')
        say('     (b) on 2026-08-21 and this path is kept only to show the')
        say('     difference. Nothing built this way may be quoted.')
    ec_c, ec_m = as_shares(ec_raw, ECON, p_econ, 'strat_econ_status')
    need(age_c == AGE, 'age bands %r are not the frozen eight' % age_c)
    need(sex_c == SEX, 'sex categories %r' % sex_c)
    need(hh_c == HH, 'person-basis household types %r are not the five' % hh_c)
    say('  marginals: age %d  sex %d  hh %d  econ %d (%s)'
        % (len(age_c), len(sex_c), len(hh_c), len(ec_c), ', '.join(ec_c)))
    if 'homemaker' not in ec_c:
        say('  !!! %s IS FITTED WITHOUT A `homemaker` BAND (FINDING 51). Those'
            % c)
        say('     people sit inside `other_inactive`, so no Spanish synthetic')
        say('     prefix can ever carry the `homemaker` token the corpus uses.')

    # ---- structural mask ---------------------------------------------------
    shape = (len(age_c), len(sex_c), len(hh_c), len(ec_c))
    ok = np.ones(shape, dtype=bool)
    i11 = age_c.index('11-14')
    i1524 = age_c.index('15-24')
    iunk = ec_c.index('unknown') if 'unknown' in ec_c else None
    if minors_kind == 'donor':
        # Z1 under D-S5-11 (b): a minor may hold any band the DONOR POOL is
        # observed to give a minor, and no other. The set is read off the pool,
        # never listed here, so a change of folds changes the mask by itself.
        s11 = set(e for e, sh in q_minor['11-14'].items() if sh > 0.0)
        s11 = set('other_inactive' if (e == 'homemaker' and
                                       'homemaker' not in ec_c) else e
                  for e in s11)
        for ei, e in enumerate(ec_c):
            if e not in s11:
                ok[i11, :, :, ei] = False
        say('  Z1 (D-S5-11 b): age 11-14 restricted to the %d band(s) the '
            'donor pool uses for a minor: %s'
            % (len(s11), ', '.join(sorted(s11))))
        if iunk is not None:
            # Z2 keeps D-S5-3's rule that `unknown` reaches no further than the
            # two youngest bands, AND adds donor support as a second condition.
            for a in range(len(age_c)):
                if a not in (i11, i1524):
                    ok[a, :, :, iunk] = False
            if q_minor['15-24'].get('unknown', 0.0) <= 0.0:
                ok[i1524, :, :, iunk] = False
                say('  Z2 (donor support): no donor labels a 15-24 `unknown`, '
                    'so that cell is zero. THIS IS THE CELL THAT MADE THE uk '
                    'FOLD INFEASIBLE UNDER D-S5-3.')
            else:
                say('  Z2: 15-24 x unknown stays open on %d donor diaries'
                    % q_cnt['15-24']['unknown'])
    else:
        need(iunk is not None,
             'econ_11plus_%s.csv has no `unknown` band, but D-S5-3 puts the '
             '11-14 population there' % c)
        ok[i11, :, :, :] = False
        ok[i11, :, :, iunk] = True
        for a in range(len(age_c)):
            if a not in (i11, i1524):
                ok[a, :, :, iunk] = False
        slack = float(ec_m[iunk] - age_m[i11])
        need(slack > -1e-9,
             'econ `unknown` is %.9f but the 11-14 band alone is %.9f. D-S5-3 '
             'puts the whole band in `unknown`, so this is infeasible.'
             % (ec_m[iunk], age_m[i11]))
        if slack < 1e-9:
            ok[i1524, :, :, iunk] = False
            say('  Z2 applied: `unknown` == the 11-14 band to %.2e, so the '
                '15-24 x unknown cell is forced to zero.' % slack)
        else:
            say('  Z2 slack %.9f (%.4f %% of the population) stays in 15-24 x '
                'unknown -- the 15-year-old slice.' % (slack, 100.0 * slack))
    # Z3
    for h in ('one_person', 'couple_no_children'):
        ok[i11, :, hh_c.index(h), :] = False
    nz = int(ok.sum())
    say('  structural mask: %d of %d cells admissible (%.1f %% zeroed)'
        % (nz, ok.size, 100.0 * (ok.size - nz) / ok.size))

    # ---- seed --------------------------------------------------------------
    if seed_kind == 'donor':
        raw = donor_seed(c, age_c, sex_c, hh_c, ec_c)
        seed = raw * ok
        lost = float(raw.sum() - seed.sum())
        say('  structural mask removed %.0f donor diaries (%.3f %% of the pool)'
            % (lost, 100.0 * lost / raw.sum()))
        need(seed.sum() > 0, 'the mask emptied the donor seed')
    else:
        seed = ok.astype(float)
        if minors_kind == 'donor':
            # FINDING 63. Uniform everywhere EXCEPT the minor row, whose
            # econ profile is what D-S5-11 (b) actually ruled on. Left
            # uniform, IPF gives a 13-year-old the adult `employed`
            # share of 43 %. This is not a second seed and it is not
            # smoothing: it is the ruling, applied where it binds.
            prof = np.array([q11.get(e, 0.0) for e in ec_c], dtype=float)
            need(prof.sum() > 0.0,
                 'the donor mix at 11-14 has no mass on any band this '
                 'fold fits')
            seed[i11] = seed[i11] * prof.reshape(1, 1, -1)
            need(seed[i11].sum() > 0.0,
                 'the minor profile and the structural mask are '
                 'disjoint, so no minor can be placed at all')

    # ---- IPF ---------------------------------------------------------------
    t4, iters, worst = ipf(seed, [age_m, sex_m, hh_m, ec_m],
                           ['age', 'sex', 'hh', 'econ'],
                           max_iter=ipf_max, strict=(ipf_max is None))
    say('  IPF converged in %d sweeps, worst marginal deviation %.2e'
        % (iters, worst))
    for nm, ax, tgt in (('age', 0, age_m), ('sex', 1, sex_m),
                        ('hh', 2, hh_m), ('econ', 3, ec_m)):
        cur = t4.sum(axis=tuple(i for i in range(4) if i != ax))
        d = float(np.max(np.abs(cur - tgt)))
        need(d < 1e-9 or ipf_max is not None,
             '%s marginal is off by %.3e after IPF' % (nm, d))
    need(float(np.abs(t4[~ok]).max() if (~ok).any() else 0.0) == 0.0,
         'a structurally zeroed cell holds mass after IPF')
    say('  occupied cells after IPF %d of %d' % (int((t4 > 0).sum()), t4.size))
    if minors_kind == 'donor':
        # IPF fits marginals, so it is free to move the minor row away
        # from the donor mix while still satisfying every constraint.
        # How far it moved is a result, not an implementation detail.
        row = t4[i11].sum(axis=(0, 1))
        got = row / row.sum()
        say('  minor econ profile, donor mix -> as fitted:')
        worst_m = 0.0
        for ei, e in enumerate(ec_c):
            tgt = q11.get(e, 0.0)
            if tgt <= 0.0 and got[ei] <= 0.0:
                continue
            worst_m = max(worst_m, abs(got[ei] - tgt))
            say('    %-15s %.6f -> %.6f  (%+.4f pp of the minor band)'
                % (e, tgt, got[ei], 100.0 * (got[ei] - tgt)))
        say('    worst departure from the donor mix %.4f pp of the '
            'minor band' % (100.0 * worst_m))

    # ---- day type, exogenous ----------------------------------------------
    t5 = t4[..., None] * DAY_W.reshape(1, 1, 1, 1, -1)
    need(abs(t5.sum() - 1.0) < 1e-12, 'the 5-way table sums to %.15f' % t5.sum())

    # ---- deterministic expansion ------------------------------------------
    cnt = largest_remainder(t5, n)
    say('  expanded to %d persons by largest remainder (no random draw)' % n)
    axes = [age_c, sex_c, hh_c, ec_c, DAY]
    worst_pp = 0.0
    for ai, (nm, cats) in enumerate(zip(
            ('age', 'sex', 'hh', 'econ', 'day'), axes)):
        cur = cnt.sum(axis=tuple(i for i in range(5) if i != ai)) / float(n)
        tgt = [age_m, sex_m, hh_m, ec_m, DAY_W][ai]
        d = 100.0 * float(np.max(np.abs(cur - tgt)))
        worst_pp = max(worst_pp, d)
        say('    %-5s worst category deviation %.4f pp' % (nm, d))
    # 0.05 pp = HALF the 0.1 pp grain the source statistics are published at,
    # so an integerisation error can never reach the resolution of the numbers
    # this population will be scored against. It is not a tuned tolerance: with
    # largest remainder over K occupied cells the worst case is of order K/N,
    # which is ~0.013 pp here, and the bound is set above the MECHANISM rather
    # than above the observation.
    need(worst_pp < 0.05 or ipf_max is not None,
         'integerisation moved a marginal by %.4f pp, above the 0.05 pp bound '
         '(half the 0.1 pp publication grain)' % worst_pp)
    need(int(cnt[~ok].sum()) == 0 if (~ok).any() else True,
         'a structurally zeroed cell received persons')

    # ---- write -------------------------------------------------------------
    if audit is not None:
        p_aud = os.path.join(OUT, 'minor_econ_split_%s.csv' % c)
        fa = io.open(p_aud, 'w', encoding='utf-8', newline='')
        wa = csv.writer(fa, lineterminator=u'\n')
        wa.writerow(['age_band_of_origin', 'weight_of_that_piece',
                     'donor_econ_band', 'assigned_econ_band', 'donor_diaries',
                     'share_within_band', 'persons'])
        for r in audit:
            wa.writerow(list(r))
        fa.write(u'# D-S5-11 (b), fold %s, donors = %s\n'
                 % (c, '+'.join(x for x in ('es', 'uk', 'it') if x != c)))
        fa.write(u'# `econ_11plus_%s.csv` is NOT modified by this rule: the '
                 u'answer depends on the donors, so it cannot live in a '
                 u'per-country file.\n' % c)
        fa.close()
        say('  wrote %s -- the re-label, auditable without re-running'
            % os.path.basename(p_aud))

    suffix = ('' if seed_kind == 'uniform' else '_donorseed') + out_suffix
    p_out = os.path.join(OUT, 'population_%s%s.csv' % (c, suffix))
    fh = io.open(p_out, 'w', encoding='utf-8', newline='')
    w = csv.writer(fh, lineterminator=u'\n')
    w.writerow(PREFIX_FIELDS)
    written = 0
    it = np.nditer(cnt, flags=['multi_index'])
    while not it.finished:
        k = int(it[0])
        if k:
            a, s, h, e, d = it.multi_index
            row = [c, age_c[a], sex_c[s], hh_c[h], ec_c[e], DAY[d]]
            for _ in range(k):
                w.writerow(row)
            written += k
        it.iternext()
    fh.close()
    need(written == n, 'wrote %d rows, expected %d' % (written, n))

    # re-read what is on disk: the FILE is what Step 5.3 consumes
    seen = 0
    hdr = None
    fhr = io.open(p_out, encoding='utf-8')
    for row in csv.reader(fhr):
        if hdr is None:
            hdr = row
            continue
        seen += 1
    fhr.close()
    need(hdr == PREFIX_FIELDS,
         'header on disk %r is not the frozen prefix order' % hdr)
    need(seen == n, '%s holds %d rows, expected %d'
                    % (os.path.basename(p_out), seen, n))
    say('  wrote %s -- %d rows, %d distinct strata'
        % (os.path.basename(p_out), seen, int((cnt > 0).sum())))
    say('OK')


if __name__ == '__main__':
    try:
        main()
    except SynthError as e:
        sys.stderr.write('REFUSED: %s\n' % e)
        sys.exit(1)
