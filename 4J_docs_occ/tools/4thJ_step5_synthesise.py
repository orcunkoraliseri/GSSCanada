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

Neither is obviously right and the difference is large, so both are built and
the choice is the author's. Nothing downstream may mix them.

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


def ipf(seed, margins, axes_names):
    """Classic IPF. `margins` is a list of 1-D arrays, one per axis, each
    summing to 1. Zero seed cells stay zero for ever, which is how the
    structural mask is enforced -- there is no separate zeroing step that could
    be forgotten after the last iteration."""
    t = seed.astype(float).copy()
    need(t.sum() > 0, 'the structural mask left no admissible cell at all')
    t /= t.sum()
    for it in range(IPF_MAX):
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
    raise SynthError('IPF did not converge in %d sweeps; worst marginal '
                     'deviation %.3e' % (IPF_MAX, worst))


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
    seed_kind = 'uniform'
    for a in list(argv):
        if a.startswith('--seed'):
            seed_kind = a.split('=', 1)[1] if '=' in a else argv[argv.index(a) + 1]
            argv = [x for x in argv if x != a and x != seed_kind]
    need(seed_kind in ('uniform', 'donor'),
         '--seed must be uniform or donor, not %r' % seed_kind)
    need(len(argv) >= 1,
         'usage: 4thJ_step5_synthesise.py <country> [N] [--seed uniform|donor]')
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
    ec_c, ec_m = as_shares(read_field(p_econ, 'strat_econ_status'), ECON,
                           p_econ, 'strat_econ_status')
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
    need(iunk is not None,
         'econ_11plus_%s.csv has no `unknown` band, but D-S5-3 puts the 11-14 '
         'population there' % c)
    # Z1
    ok[i11, :, :, :] = False
    ok[i11, :, :, iunk] = True
    # Z2
    keep = [i11, i1524]
    for a in range(len(age_c)):
        if a not in keep:
            ok[a, :, :, iunk] = False
    # Z2', derived not assumed: where `unknown` equals the 11-14 band exactly,
    # nothing is left for the 15-year-old slice.
    slack = float(ec_m[iunk] - age_m[i11])
    need(slack > -1e-9,
         'econ `unknown` is %.9f but the 11-14 band alone is %.9f. D-S5-3 puts '
         'the whole band in `unknown`, so this is infeasible.'
         % (ec_m[iunk], age_m[i11]))
    if slack < 1e-9:
        ok[i1524, :, :, iunk] = False
        say('  Z2\' applied: `unknown` == the 11-14 band to %.2e, so the 15-24 '
            'x unknown cell is forced to zero.' % slack)
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

    # ---- IPF ---------------------------------------------------------------
    t4, iters, worst = ipf(seed, [age_m, sex_m, hh_m, ec_m],
                           ['age', 'sex', 'hh', 'econ'])
    say('  IPF converged in %d sweeps, worst marginal deviation %.2e'
        % (iters, worst))
    for nm, ax, tgt in (('age', 0, age_m), ('sex', 1, sex_m),
                        ('hh', 2, hh_m), ('econ', 3, ec_m)):
        cur = t4.sum(axis=tuple(i for i in range(4) if i != ax))
        d = float(np.max(np.abs(cur - tgt)))
        need(d < 1e-9, '%s marginal is off by %.3e after IPF' % (nm, d))
    need(float(np.abs(t4[~ok]).max() if (~ok).any() else 0.0) == 0.0,
         'a structurally zeroed cell holds mass after IPF')
    say('  occupied cells after IPF %d of %d' % (int((t4 > 0).sum()), t4.size))

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
    need(worst_pp < 0.05,
         'integerisation moved a marginal by %.4f pp, above the 0.05 pp bound '
         '(half the 0.1 pp publication grain)' % worst_pp)
    need(int(cnt[~ok].sum()) == 0 if (~ok).any() else True,
         'a structurally zeroed cell received persons')

    # ---- write -------------------------------------------------------------
    suffix = '' if seed_kind == 'uniform' else '_donorseed'
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
