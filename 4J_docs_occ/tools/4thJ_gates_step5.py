# -*- coding: utf-8 -*-
"""
4J / STEP 5 GATE BATTERY.

Runs the gates of `Step5_docs/4thJ_05_populationLinkage_val.md` against the real
artefacts, then runs every perturbation that document names and checks that each
one fells EXACTLY the gate it is supposed to fell, then applies the coverage
clause: a gate that passed at baseline and was never made to fall is a gate
nobody has evidence for.

WHAT IT COVERS AND WHAT IT CANNOT
=================================
Runnable today: `G5.1`-`G5.7`, `G5.10`, `G5.11`.

🔴 NOT runnable, and NOT reported as passing: `G5.8` (temperature calibration
reported) and `G5.9` (`top_p <= 0.98` in the generation config). Both read
artefacts item 5.4 and Step 7 have not produced -- there is no checkpoint, so
there is no temperature sweep and no generation config. They are printed as
BLOCKED, which is a third verdict on purpose: a gate whose input does not exist
has not passed, and writing it PASS would be the exact failure this project has
a 52-item catalogue about.

🟢 `G5.6` IS SPLIT IN TWO -- `D-S5-12` RULED (a), 2026-08-21.
The single gate read "count of marginals with no published source, OR DERIVED
FROM MICRODATA: 0", and it FAILED `es` 30/36 and `it` 12/36 because three later
rulings -- `D-S5-4` (b), `D-S5-5`, `D-S5-9` -- put census microdata into the
marginals ON PURPOSE. The measured split is what made it decidable: ZERO rows
in any fold failed for "no published source"; all 42 failed only the microdata
clause, and the microdata in question is the INE Censo 2011 / ISTAT CPA 2011
PUBLIC-USE CENSUS files, not the HETUS diaries the contamination claim is about.

It is now two gates, each with its own perturbation:

  `G5.6i`   zero marginals derived from the held-out country's TIME-USE
            DIARIES -- this is the contamination gate, and it is the one the
            paper's claim actually rests on.
  `G5.6ii`  zero marginals without a published source carrying a URL AND a
            table id.

🔴 THE OLD TEXT IS STILL RUN, as `G5.6-as-written`, and is printed as
INFORMATIONAL -- not scored, not counted in the verdicts. It still FAILS on
`es` and `it`, and that failure is the evidence for why the split was needed.
A superseded gate is retired in the open, not deleted.

NOTHING SHIPPED IS MUTATED
==========================
Every perturbation acts on an in-memory copy, except the `G5.1` one, which has
to re-run IPF and does so through `--out-suffix` into a file of its own. The
battery md5s `population_<c>.csv` before and after and refuses if either moved.
"""

import io
import os
import sys
import csv
import copy
import json
import hashlib
import subprocess
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import importlib

syn = importlib.import_module('4thJ_step5_synthesise')
encoder = importlib.import_module('encoder')

OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
CORPUS = os.path.join(ROOT, 'Step3_docs', 'outputs_step3',
                      '4J_step3_corpus.jsonl')
FOLDS = ['es', 'uk', 'it']

# 🔴 `G5.11`. The five scored fields are DERIVED from the encoder, here, once.
# There is no literal list of field names anywhere in this file, and `G5.11`
# below proves that by reading this file's own source.
SCORED = [f for f in encoder.PREFIX_FIELDS if f != 'country']

TOL_MARGIN_PP = 0.5
TOL_SIZE_FRAC = 0.001
N_TARGET = 100000


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def md5(p):
    h = hashlib.md5()
    h.update(io.open(p, 'rb').read())
    return h.hexdigest()


# ---------------------------------------------------------------- fold state

def load_population(path):
    fh = io.open(path, encoding='utf-8')
    rows = [dict(r) for r in csv.DictReader(fh)]
    fh.close()
    return rows


def assemble_targets(c):
    """The marginals the population was fitted to.

    Re-uses the synthesiser's own readers rather than restating them: the same
    rule that makes `G5.5` import the encoder instead of copying it.
    """
    p_marg = os.path.join(OUT, 'marginals_%s.csv' % c)
    p_hh = os.path.join(OUT, 'hhtype_person_%s.csv' % c)
    p_econ = os.path.join(OUT, 'econ_11plus_%s.csv' % c)
    ec_raw = syn.read_field(p_econ, 'strat_econ_status')
    ec_raw, _a, _q, _cnt, _q11 = syn.relabel_minors(
        c, ec_raw, syn.read_notes(p_econ), p_econ, syn.ECON)
    out = {}
    for field, path, order in (
            ('strat_age_band', p_marg, syn.AGE),
            ('strat_sex', p_marg, syn.SEX),
            ('strat_hh_type', p_hh, syn.HH)):
        cats, sh = syn.as_shares(syn.read_field(path, field), order, path, field)
        out[field] = dict(zip(cats, [float(x) for x in sh]))
    cats, sh = syn.as_shares(ec_raw, syn.ECON, p_econ, 'strat_econ_status')
    out['strat_econ_status'] = dict(zip(cats, [float(x) for x in sh]))
    out['strat_day_type'] = dict(zip(syn.DAY, [float(x) for x in syn.DAY_W]))
    return out


def impossibility_table(c, targets):
    """`G5.2`'s explicit table, as (field, value, field, value) pairs.

    Built from the SAME two sources the synthesiser's mask is built from -- the
    donor pool's observed minor bands and the measured mean household sizes --
    so a change there changes this, and the gate cannot go stale against the
    population it scores.
    """
    pool = collections.Counter()
    for r in corpus_records():
        if r['country'] == c:
            continue
        if r['fields']['strat_age_band'] == '11-14':
            pool[r['fields']['strat_econ_status']] += 1
    has_home = 'homemaker' in targets['strat_econ_status']
    seen = set('other_inactive' if (e == 'homemaker' and not has_home) else e
               for e in pool)
    tab = []
    for e in targets['strat_econ_status']:
        if e not in seen:
            tab.append(('strat_age_band', '11-14', 'strat_econ_status', e))
    for h in ('one_person', 'couple_no_children'):
        tab.append(('strat_age_band', '11-14', 'strat_hh_type', h))
    for a in targets['strat_age_band']:
        if a not in ('11-14', '15-24') and 'unknown' in targets['strat_econ_status']:
            tab.append(('strat_age_band', a, 'strat_econ_status', 'unknown'))
    if 'unknown' in targets['strat_econ_status'] and pool_has(c, '15-24') is False:
        tab.append(('strat_age_band', '15-24', 'strat_econ_status', 'unknown'))
    return tab


_CORPUS_CACHE = []


def corpus_records():
    if not _CORPUS_CACHE:
        pos = dict((f, i) for i, f in enumerate(encoder.PREFIX_FIELDS))
        for ln in io.open(CORPUS, encoding='utf-8'):
            r = json.loads(ln)
            f = r['text'].split(encoder.PREFIX_BODY_SEP, 1)[0].split(
                encoder.PREFIX_SEP)
            _CORPUS_CACHE.append(
                {'country': r['country'],
                 'fields': dict((k, f[pos[k]]) for k in encoder.PREFIX_FIELDS)})
    return _CORPUS_CACHE


def pool_has(held_out, band):
    for r in corpus_records():
        if r['country'] == held_out:
            continue
        if (r['fields']['strat_age_band'] == band
                and r['fields']['strat_econ_status'] == 'unknown'):
            return True
    return False


def build_state(c):
    pop = load_population(os.path.join(OUT, 'population_%s.csv' % c))
    tgt = assemble_targets(c)
    st = {
        'country': c,
        'pop': pop,
        'targets': tgt,
        'impossible': impossibility_table(c, tgt),
        'n_target': N_TARGET,
        'scored_fields': list(SCORED),
        'prefix_fields': list(encoder.PREFIX_FIELDS),
        'copresence_asserted': [],
        'extra_marginal_rows': [],
        'gen_extra_source': '',
        'checker_restates_fields': False,
    }
    st['prefixes'] = [ln.strip() for ln in
                      io.open(os.path.join(OUT, 'prefixes_%s.jsonl' % c),
                              encoding='utf-8')]
    return st


# --------------------------------------------------------------------- gates

def g5_1(st):
    """Marginal fit: every target margin reproduced to within +/- 0.5 pp."""
    n = len(st['pop'])
    worst, where = 0.0, ''
    for var, tgt in st['targets'].items():
        cnt = collections.Counter(r[var] for r in st['pop'])
        for cat, want in tgt.items():
            d = abs(cnt[cat] / float(n) - want) * 100.0
            if d > worst:
                worst, where = d, '%s=%s' % (var, cat)
    return (worst <= TOL_MARGIN_PP,
            'worst margin %.4f pp at %s (tolerance %.2f pp)'
            % (worst, where, TOL_MARGIN_PP))


def g5_2(st):
    """Joint plausibility: zero persons in structurally impossible cells."""
    tab = st['impossible']
    if not tab:
        return False, 'V5.a: the impossibility table is EMPTY'
    bad = collections.Counter()
    for r in st['pop']:
        for f1, v1, f2, v2 in tab:
            if r[f1] == v1 and r[f2] == v2:
                bad['%s=%s & %s=%s' % (f1, v1, f2, v2)] += 1
    tot = sum(bad.values())
    return (tot == 0,
            '%d cell(s) in the table, %d person(s) inside them%s'
            % (len(tab), tot,
               '' if not bad else ' -- worst %s x%d' % bad.most_common(1)[0]))


def g5_3(st):
    """Population size within +/- 0.1 % of target."""
    n, t = len(st['pop']), st['n_target']
    d = abs(n - t) / float(t)
    return d <= TOL_SIZE_FRAC, '%d of %d, off by %.4f %%' % (n, t, 100.0 * d)


def g5_4(st):
    """Every value of the five non-country fields appears in the fold's
    TRAINING corpus. `country` is out by ruling, not by omission."""
    seen = dict((f, set()) for f in st['scored_fields'])
    for r in corpus_records():
        if r['country'] == st['country']:
            continue
        for f in st['scored_fields']:
            if f in r['fields']:
                seen[f].add(r['fields'][f])
    miss = collections.Counter()
    for r in st['pop']:
        for f in st['scored_fields']:
            if r.get(f) not in seen[f]:
                miss['%s=%s' % (f, r.get(f))] += 1
    n = len(st['pop'])
    ok = sum(miss.values()) == 0
    return (ok, '%d field(s) scored, %d person(s) of %d carry an unseen value%s'
            % (len(st['scored_fields']), sum(miss.values()), n,
               '' if ok else ' -- %s' % dict(miss.most_common(3))))


def g5_5(st):
    """Prefix encoder identity: byte-identical to tools/encoder.py."""
    bad, n = 0, 0
    for r, line in zip(st['pop'], st['prefixes']):
        obj = json.loads(line)
        # V5.d: the field order comes from the ENCODER, never from this
        # step's copy of it, or the gate reduces to comparing a thing
        # to itself.
        want = encoder.encode_prefix(
            dict((f, r[f]) for f in encoder.PREFIX_FIELDS))
        got = obj.get('prefix', obj.get('text', ''))
        n += 1
        if got != want:
            bad += 1
    return bad == 0, '%d prefixes compared, %d differ from the encoder' % (n, bad)


MICRODATA_MARK = ('microdat', 'microdati', 'MICRODATA')


def marginal_rows(st):
    """Every marginal row the held-out fold was fitted to, as dicts.

    One reader for all three provenance gates: a second copy of the file list
    is how `G5.6i` and `G5.6ii` would end up scoring different populations.
    """
    rows = []
    for name in ('marginals_%s.csv', 'hhtype_person_%s.csv',
                 'econ_11plus_%s.csv'):
        p = os.path.join(OUT, name % st['country'])
        if not os.path.exists(p):
            continue
        fh = io.open(p, encoding='utf-8')
        for row in csv.DictReader(fh):
            if not row or not row.get('field'):
                continue
            if row['field'].startswith('#'):
                continue
            rows.append(row)
        fh.close()
    rows.extend(st.get('extra_marginal_rows', []))
    return rows


# 🔴 `G5.6i`. Markers for "this number came out of somebody's TIME-USE
# DIARIES". Deliberately WIDE: `tus_` catches published Eurostat time-use
# tables too, which are aggregates rather than diaries. No Step 5 marginal
# matches any of these today, so the width costs nothing now and makes the
# gate fail towards caution if one ever does.
DIARY_MARK = ('hetus', 'diary', 'diaries', 'time-use', 'time use',
              'time_use', 'tus_', 'step3_corpus', 'harmonised.parquet')


def g5_6i(st):
    """CONTAMINATION. Zero marginals derived from the held-out country's own
    time-use diaries. `D-S5-12` (a), condition (i)."""
    checked, bad, hits = 0, 0, []
    for row in marginal_rows(st):
        checked += 1
        blob = ' '.join(str(v) for v in row.values()).lower()
        m = [w for w in DIARY_MARK if w in blob]
        if m:
            bad += 1
            hits.append('%s=%s (%s)' % (row.get('field'), row.get('category'),
                                        ','.join(m)))
    if checked == 0:
        return False, 'V5.b: zero marginals were checked'
    return (bad == 0, '%d marginal rows checked, %d trace to time-use diaries%s'
            % (checked, bad, '' if not bad else ' -- %s' % '; '.join(hits[:4])))


def g5_6ii(st):
    """PUBLISHED SOURCE. Every marginal carries a URL and a table id.
    `D-S5-12` (a), condition (ii)."""
    checked, bad, hits = 0, 0, []
    for row in marginal_rows(st):
        checked += 1
        url = (row.get('source_url') or '').strip()
        tab = (row.get('source_table') or '').strip()
        if not url or not tab:
            bad += 1
            hits.append('%s=%s (%s)' % (
                row.get('field'), row.get('category'),
                'no url' if not url else 'no table id'))
    if checked == 0:
        return False, 'V5.b: zero marginals were checked'
    return (bad == 0, '%d marginal rows checked, %d without a published '
                      'source%s'
            % (checked, bad, '' if not bad else ' -- %s' % '; '.join(hits[:4])))


def g5_6(st):
    """SUPERSEDED by `D-S5-12` (a). The gate as originally written -- no
    published source OR derived from microdata -- run for the record, reported
    as INFORMATIONAL, never scored. It fails on `es` and `it` by design."""
    checked, bad, why = 0, 0, collections.Counter()
    for name in ('marginals_%s.csv', 'hhtype_person_%s.csv',
                 'econ_11plus_%s.csv'):
        p = os.path.join(OUT, name % st['country'])
        if not os.path.exists(p):
            continue
        fh = io.open(p, encoding='utf-8')
        for row in csv.DictReader(fh):
            if not row or not row.get('field'):
                continue
            if row['field'].startswith('#'):
                continue
            checked += 1
            url = (row.get('source_url') or '').strip()
            tab = (row.get('source_table') or '').strip()
            blob = ' '.join(str(v) for v in row.values()).lower()
            if not url or not tab:
                bad += 1
                why['no published source'] += 1
            elif any(m.lower() in blob for m in MICRODATA_MARK):
                bad += 1
                why['derived from microdata'] += 1
        fh.close()
    for row in st.get('extra_marginal_rows', []):
        checked += 1
        blob = ' '.join(str(v) for v in row.values()).lower()
        if any(m.lower() in blob for m in MICRODATA_MARK):
            bad += 1
            why['derived from microdata'] += 1
    if checked == 0:
        return False, 'V5.b: zero marginals were checked'
    return (bad == 0, '%d marginal rows checked, %d violate the rule%s'
            % (checked, bad, '' if not bad else ' -- %s' % dict(why)))


def g5_7(st):
    """Co-presence honesty: no prefix asserts a flag the country never
    recorded. Prints what it scanned (there is no co-presence field in the
    frozen prefix at all, and that absence is the reason it passes)."""
    if st['copresence_asserted']:
        return (False, 'prefix asserts %r, which the fold never recorded'
                % st['copresence_asserted'])
    return (True, 'scanned %d prefix fields (%s); none is a co-presence flag'
            % (len(st['prefix_fields']), ', '.join(st['prefix_fields'])))


GEN_PATH = ['4thJ_step5_synthesise.py', '4thJ_step5_prefixes.py',
            'encoder.py', 'decoder.py', '4thJ_step7_grammar.py',
            '4thJ_step7_indoor.py']
RAKE_WORDS = ('rake(', 'reweight', 'post_hoc_calibrat', 'raking')


def g5_10(st):
    """No output raking anywhere on the generation path. V5.c: print the file
    list, and FAIL if a file could not be read rather than reporting nothing
    found."""
    scanned, hits, missing = [], [], []
    for f in GEN_PATH:
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            missing.append(f)
            continue
        src = io.open(p, encoding='utf-8').read()
        scanned.append(f)
        for w in RAKE_WORDS:
            if w in src:
                hits.append('%s:%s' % (f, w))
    if st['gen_extra_source']:
        scanned.append('<injected>')
        for w in RAKE_WORDS:
            if w in st['gen_extra_source']:
                hits.append('<injected>:%s' % w)
    if missing:
        return False, 'V5.c: could not read %d of %d generation-path files: %s' \
            % (len(missing), len(GEN_PATH), ', '.join(missing))
    return (not hits, 'scanned %d files (%s); %d hit(s)%s'
            % (len(scanned), ', '.join(scanned), len(hits),
               '' if not hits else ' -- ' + ', '.join(hits)))


def g5_11(st):
    """The five scored fields must be READ from the encoder, never restated.

    Proved against this file's own source: if any of the encoder's prefix field
    names appears as a quoted literal in a checker context here, the field set
    has a second home and can go stale.
    """
    if st['checker_restates_fields']:
        return False, 'the checker carries its own copy of the field list'
    src = io.open(os.path.abspath(__file__), encoding='utf-8').read()
    body = src.split('SCORED = ', 1)[1]
    restated = [f for f in encoder.PREFIX_FIELDS
                if ("'%s'" % f) in body or ('"%s"' % f) in body]
    # the gate functions legitimately name the fields they are ABOUT; what is
    # forbidden is a list that stands in for PREFIX_FIELDS. Detect that shape.
    listy = [f for f in restated
             if ("'%s'," % f) in body.replace('\n', ' ').replace('  ', ' ')
             and 'SCORED' not in body.split("'%s'," % f)[0][-80:]]
    if len(listy) >= len(SCORED):
        return (False, 'the field set is restated as a literal list of %d names'
                % len(listy))
    if st['scored_fields'] != [f for f in encoder.PREFIX_FIELDS
                               if f != 'country']:
        return False, 'the scored set has drifted from the encoder'
    return (True, 'scored set derived from encoder.PREFIX_FIELDS (%d of %d '
                  'fields, `country` removed by ruling)'
            % (len(SCORED), len(encoder.PREFIX_FIELDS)))


GATES = [('G5.1', g5_1), ('G5.2', g5_2), ('G5.3', g5_3), ('G5.4', g5_4),
         ('G5.5', g5_5), ('G5.6i', g5_6i), ('G5.6ii', g5_6ii),
         ('G5.7', g5_7), ('G5.10', g5_10),
         ('G5.11', g5_11)]
BLOCKED = {'G5.8': 'no temperature sweep exists -- item 5.4 needs a fold '
                   'checkpoint and a generation pass',
           'G5.9': 'no generation config exists -- Step 7 has not run'}


def run_gates(st, quiet=False):
    res = {}
    for gid, fn in GATES:
        try:
            ok, msg = fn(st)
        except Exception as e:                      # a gate that crashes FAILS
            ok, msg = False, 'raised %s: %s' % (type(e).__name__, e)
        res[gid] = ok
        if not quiet:
            say('    %-6s %-4s %s' % (gid, 'PASS' if ok else 'FAIL', msg))
    return res


# ------------------------------------------------------------- perturbations

def resync_prefixes(st):
    """Re-encode after a perturbation that edited people.

    A perturbation is supposed to fell ONE gate. Editing a person and leaving
    the prefix file stale fells `G5.5` too, and that failure is about the
    battery, not about the artefact.
    """
    st['prefixes'] = [json.dumps({'prefix': encoder.encode_prefix(
        dict((f, r[f]) for f in encoder.PREFIX_FIELDS))}) for r in st['pop']]
    return st


def p_ipf2(st):
    """Stop IPF early. Two sweeps as the validation doc specifies; if the gate
    survives that, one sweep, and the escalation is printed.

    🔴 Italy needs the escalation and Spain and the UK do not. That is a
    property of the country, not of the code: Italy's four marginals are close
    enough to independent that two sweeps of IPF already land inside the 0.5 pp
    tolerance. Worth knowing before anyone reads `G5.1` as evidence that the
    Italian fit was hard.
    """
    c = st['country']
    for sweeps in (2, 1):
        sub = os.path.join(OUT, 'population_%s_p_ipf2.csv' % c)
        subprocess.call([sys.executable,
                         os.path.join(HERE, '4thJ_step5_synthesise.py'), c,
                         '--ipf-max', str(sweeps),
                         '--out-suffix', '_p_ipf2'],
                        stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        st['pop'] = load_population(sub)
        resync_prefixes(st)
        ok, _msg = g5_1(st)
        if not ok:
            if sweeps != 2:
                say('         (escalated to %d sweep: %s survives 2, its '
                    'marginals are nearly independent)' % (sweeps, c))
            return st
    return st


def p_drop_constraint(st):
    st['impossible'] = st['impossible'][1:]
    # and put someone in the cell that was just un-forbidden
    f1, v1, f2, v2 = st['impossible'][0] if st['impossible'] else (
        'strat_age_band', '11-14', 'strat_hh_type', 'one_person')
    for r in st['pop'][:400]:
        r[f1], r[f2] = v1, v2
    return resync_prefixes(st)


def p_drop_rows(st):
    # every 20th row, not the first 5 %: the population file is ordered
    # by stratum, so a head slice deletes whole categories and fells
    # G5.1 as well. The validation doc asks precisely whether the
    # margins survive a PROPORTIONAL loss.
    st['pop'] = [r for i, r in enumerate(st['pop']) if i % 20]
    return resync_prefixes(st)


def p_unseen_hh(st):
    for r in st['pop'][:50]:
        r['strat_hh_type'] = 'communal_establishment'
    return resync_prefixes(st)


def p_design_as_specified(st):
    return st          # the country token is already the held-out one


def p_literal_fields(st):
    # the checker keeps its own five names while the prefix grows a
    # sixth scored field. G5.4 goes on passing -- it is scoring a prefix
    # that no longer exists -- and only G5.11 can see it.
    st['checker_restates_fields'] = True
    st['prefix_fields'] = list(st['prefix_fields']) + ['strat_seventh']
    return st


def p_reorder_prefix(st):
    a, b = 1, 2
    for i, line in enumerate(st['prefixes'][:200]):
        o = json.loads(line)
        k = 'prefix' if 'prefix' in o else 'text'
        parts = o[k].split(encoder.PREFIX_SEP)
        parts[a], parts[b] = parts[b], parts[a]
        o[k] = encoder.PREFIX_SEP.join(parts)
        st['prefixes'][i] = json.dumps(o)
    return st


def p_microdata_marginal(st):
    # Substitute one held-out marginal with a value computed from that
    # country's own CENSUS microdata. The FIT is untouched, which is the point:
    # only a provenance gate can see this.
    #
    # 🔴 Under `D-S5-12` (a) this perturbation MUST FELL NOTHING. That is
    # not a weak perturbation, it is the ruling's own test: `D-S5-4` (b),
    # `D-S5-5` and `D-S5-9` deliberately admit published-census microdata, so a
    # split that still fells a gate here has not actually split anything. It
    # DOES still fell `G5.6-as-written`, which is printed informationally.
    st['extra_marginal_rows'] = [{
        'field': 'strat_age_band', 'category': '25-34',
        'count': '1', 'source_table': 'cen11_microdata_personas',
        'source_url': 'https://www.ine.es/ftp/microdatos/censopv/cen11/',
        'status': 'DERIVED_FROM_MICRODATA'}]
    return st


def p_diary_marginal(st):
    # `G5.6i`. The contamination move the paper's claim forbids: take a
    # marginal for the HELD-OUT country out of that country's own time-use
    # diaries. Published, sourced, and fatal.
    st['extra_marginal_rows'] = [{
        'field': 'strat_age_band', 'category': '25-34',
        'count': '1', 'source_table': 'HETUS_2010_held_out_diaries',
        'source_url': 'https://ec.europa.eu/eurostat/web/time-use-surveys',
        'status': 'RECOUNTED_FROM_THE_HELD_OUT_DIARIES'}]
    return st


def p_unsourced_marginal(st):
    # `G5.6ii`. A marginal with a number and no way to check it. Not diary
    # derived, so `G5.6i` must NOT move: the two conditions have to be
    # independently felled or the split is cosmetic.
    st['extra_marginal_rows'] = [{
        'field': 'strat_age_band', 'category': '25-34',
        'count': '1', 'source_table': '',
        'source_url': '',
        'status': 'ASSUMED'}]
    return st


def p_copresence(st):
    st['copresence_asserted'] = ['co_present_child']
    return st


def p_rake_in_genpath(st):
    st['gen_extra_source'] = 'w = rake(generated, marginals)  # post-hoc\n'
    return st


def p_null(st):
    return st


PERTURBATIONS = [
    ('stop IPF after 2 sweeps', p_ipf2, {'G5.1'}),
    ('remove one impossibility constraint', p_drop_constraint, {'G5.2'}),
    ('drop 5 % of synthetic rows', p_drop_rows, {'G5.3'}),
    ('household type absent from training', p_unseen_hh, {'G5.4'}),
    ('run the design as specified (held-out country token)',
     p_design_as_specified, set()),
    ('restate the field list and add a seventh field', p_literal_fields,
     {'G5.11'}),
    ('reorder two prefix fields in a local copy', p_reorder_prefix, {'G5.5'}),
    ('substitute a held-out marginal computed from census microdata',
     p_microdata_marginal, set()),
    ("substitute a held-out marginal recounted from the held-out diaries",
     p_diary_marginal, {'G5.6i'}),
    ('add a marginal with no URL and no table id',
     p_unsourced_marginal, {'G5.6ii'}),
    ('assert an unrecorded co-presence flag', p_copresence, {'G5.7'}),
    ('add a rake call to the generation path', p_rake_in_genpath, {'G5.10'}),
    ('NULL perturbation: change nothing', p_null, set()),
]


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith('-')]
    folds = argv if argv else FOLDS
    before = dict((c, md5(os.path.join(OUT, 'population_%s.csv' % c)))
                  for c in FOLDS)

    say('=' * 74)
    say('STEP 5 GATE BATTERY')
    say('=' * 74)
    for gid in sorted(BLOCKED):
        say('  %-6s BLOCKED  %s' % (gid, BLOCKED[gid]))
    say('')

    fell = collections.defaultdict(set)
    passed_at_base = collections.defaultdict(set)
    verdict = {}

    for c in folds:
        say('--- fold %s : baseline' % c)
        base = build_state(c)
        res = run_gates(base)
        verdict[c] = res
        # 🔴 `D-S5-12`: the superseded single gate, run and shown, never
        # scored. Its FAIL is the evidence for the split, so it is not deleted.
        try:
            ok_aw, msg_aw = g5_6(base)
        except Exception as e:
            ok_aw, msg_aw = False, 'raised %s: %s' % (type(e).__name__, e)
        say('    %-6s %-4s %s  [INFORMATIONAL -- superseded by D-S5-12 (a), '
            'not counted]' % ('G5.6', 'PASS' if ok_aw else 'FAIL', msg_aw))
        for gid, ok in res.items():
            if ok:
                passed_at_base[c].add(gid)
        say('')
        say('--- fold %s : perturbations' % c)
        for name, fn, must in PERTURBATIONS:
            st = fn(copy.deepcopy(base))
            got = run_gates(st, quiet=True)
            down = set(g for g, ok in res.items() if not ok)
            broke = set(g for g, ok in got.items() if not ok) - down
            # a perturbation aimed at a gate that is already FAILING at
            # baseline cannot fell it, and that is not a mismatch
            unreachable = must & down
            good = (broke == (must - down))
            for g in broke:
                fell[c].add(g)
            tag = 'n/a' if (unreachable and not broke) else (
                'ok' if good else '!!')
            say('    %-4s %-52s felled %s' %
                (tag, name[:52],
                 ', '.join(sorted(broke)) if broke else '(nothing)'))
            if tag == 'n/a':
                say('         %s already FAILS at baseline on this fold'
                    % ', '.join(sorted(unreachable)))
            elif not good:
                say('         expected %s'
                    % (', '.join(sorted(must - down)) if (must - down)
                       else '(nothing)'))
        say('')

    say('--- coverage clause: a gate that PASSED and never FELL')
    holes = []
    for c in folds:
        for gid in sorted(passed_at_base[c]):
            if gid not in fell[c]:
                holes.append('%s/%s' % (c, gid))
    if holes:
        say('    !!! %d hole(s): %s' % (len(holes), ', '.join(holes)))
    else:
        say('    none -- every passing gate was made to fall')
    say('')

    after = dict((c, md5(os.path.join(OUT, 'population_%s.csv' % c)))
                 for c in FOLDS)
    for c in FOLDS:
        if before[c] != after[c]:
            say('!!! population_%s.csv CHANGED during the battery' % c)
            return 2
    say('shipped populations unchanged (md5 verified before and after)')

    nfail = sum(1 for c in folds for g, ok in verdict[c].items() if not ok)
    say('')
    say('%d gate-fold verdicts, %d FAIL, %d BLOCKED per fold'
        % (len(folds) * len(GATES), nfail, len(BLOCKED)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
