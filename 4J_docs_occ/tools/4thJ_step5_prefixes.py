# -*- coding: utf-8 -*-
"""
4J / Step 5.3 -- BUILD THE CONDITIONING PREFIXES.

THE WHOLE POINT OF THIS FILE IS THAT IT CONTAINS NO MAPPING
===========================================================
The step doc is explicit: *"The mapping is one function, shared with Step 3's
encoder, not a reimplementation. A second copy of a field order drifts invisibly
from the first."* So this module imports `tools/encoder.py` and calls
`encode_prefix()`. It does not know the field order, the separator, or the
alphabet, and it must not learn them -- if `encoder.py` changes, this file must
follow silently or fail loudly, never disagree quietly.

The one thing it DOES assert about the encoder is `PREFIX_FIELDS`, and it
asserts it against the header of `population_<c>.csv` rather than against a
literal written here. That is the drift check: Step 5.2 wrote that header from
the same constant.

WHAT IS VERIFIED, AND WHY EACH CHECK CAN ACTUALLY FAIL
======================================================
1. ROUND TRIP. Every emitted prefix is split back on the encoder's own
   separator and compared field-by-field with the row it came from. This fails
   if the encoder ever lower-cases, re-orders, or normalises a value -- which it
   is entitled to do, and which we would otherwise discover in Step 7 as a
   model that was conditioned on something other than the population.
2. STRATUM CLOSURE. The number of distinct prefixes must equal the number of
   distinct strata in the population. Fails if two different strata collapse to
   the same prefix string, i.e. if the prefix is not injective on the
   population -- which would make the conditioning ambiguous.
3. CORPUS COVERAGE. Every distinct synthetic prefix is looked up in the Step 3
   corpus. This one is a DIAGNOSTIC and is allowed to be imperfect: a synthetic
   prefix that never occurred in training is a genuine out-of-distribution
   request, and the fraction of the synthetic population sitting on such
   prefixes is exactly the exposure `D5.1` will have to talk about. It is
   printed, not enforced -- enforcing it would amount to deleting the hard
   cases.

   🔴 The lookup is against the corpus MINUS the held-out country, because that
   is what the model for this fold was trained on. Looking the `es` population
   up in a corpus that contains `es` would report a coverage the LOCO model
   never had.

OUTPUT
======
`outputs_step5/prefixes_<c>.jsonl` -- one object per synthetic person, carrying
the six fields AND the prefix string. Both, deliberately: the string is what
Step 7 feeds the model, the fields are what Step 6 aggregates on, and keeping
them in one record makes it impossible to join them wrongly later.

`outputs_step5/population_<c>.parquet` -- the same population as the CSV Step
5.2 wrote, in the format the step doc names. Written here rather than there
because only this module's interpreter has `pyarrow`.
"""

import io
import os
import sys
import csv
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
CORPUS = os.path.join(ROOT, 'Step3_docs', 'outputs_step3',
                      '4J_step3_corpus.jsonl')

sys.path.insert(0, HERE)
import encoder  # noqa: E402  -- the shared mapping, not a copy of it


class PrefixError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise PrefixError(msg)


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def corpus_prefixes(exclude_country):
    """Distinct prefix strings in the Step 3 corpus, excluding one country.

    The corpus text is `<prefix>|<episodes><eor>`, so the prefix is everything
    before the first body separator. Read as text: re-encoding the corpus here
    would be the second copy this module exists to avoid.
    """
    seen = collections.Counter()
    fh = io.open(CORPUS, encoding='utf-8')
    for ln in fh:
        r = json.loads(ln)
        if r['country'] == exclude_country:
            continue
        seen[r['text'].split(encoder.PREFIX_BODY_SEP, 1)[0]] += 1
    fh.close()
    return seen


def main():
    need(len(sys.argv) >= 2, 'usage: 4thJ_step5_prefixes.py <country>')
    c = sys.argv[1].strip().lower()
    need(c in ('es', 'uk', 'it'), 'country %r is not one of es/uk/it' % c)

    p_pop = os.path.join(OUT, 'population_%s.csv' % c)
    need(os.path.exists(p_pop),
         'population_%s.csv does not exist -- run 4thJ_step5_synthesise.py '
         'first' % c)
    say('=== Step 5.3  country %s ===' % c)

    rows = []
    fh = io.open(p_pop, encoding='utf-8')
    rd = csv.reader(fh)
    hdr = next(rd)
    need(hdr == encoder.PREFIX_FIELDS,
         'population_%s.csv header %r is not encoder.PREFIX_FIELDS %r -- the '
         'two copies of the field order have drifted, which is exactly what '
         'sharing the encoder was meant to prevent'
         % (c, hdr, encoder.PREFIX_FIELDS))
    for r in rd:
        rows.append(dict(zip(hdr, r)))
    fh.close()
    say('  %d persons, header matches encoder.PREFIX_FIELDS' % len(rows))

    # ---- encode, and round-trip every single one --------------------------
    p_out = os.path.join(OUT, 'prefixes_%s.jsonl' % c)
    fo = io.open(p_out, 'w', encoding='utf-8', newline='')
    strata = set()
    pref_count = collections.Counter()
    for i, r in enumerate(rows):
        p = encoder.encode_prefix(r)
        back = p.split(encoder.PREFIX_SEP)
        need(len(back) == len(encoder.PREFIX_FIELDS),
             'prefix %r split into %d fields, expected %d'
             % (p, len(back), len(encoder.PREFIX_FIELDS)))
        for f, v in zip(encoder.PREFIX_FIELDS, back):
            need(v == r[f],
                 'round trip failed on row %d field %s: population has %r, the '
                 'prefix carries %r. The encoder normalised a value, so the '
                 'model would be conditioned on something the population does '
                 'not say.' % (i, f, r[f], v))
        strata.add(tuple(r[f] for f in encoder.PREFIX_FIELDS))
        pref_count[p] += 1
        rec = dict(r)
        rec['prefix'] = p
        fo.write(json.dumps(rec, sort_keys=True) + u'\n')
    fo.close()
    need(len(pref_count) == len(strata),
         '%d distinct prefixes but %d distinct strata -- the prefix is not '
         'injective on this population, so the conditioning is ambiguous'
         % (len(pref_count), len(strata)))
    say('  round trip exact on all %d rows' % len(rows))
    say('  %d distinct prefixes == %d distinct strata'
        % (len(pref_count), len(strata)))

    # ---- corpus coverage, a diagnostic ------------------------------------
    #
    # 🔴 TWO measurements, and the first one is DEGENERATE BY CONSTRUCTION.
    # The prefix's first field is `country`, and the training corpus for this
    # fold is the corpus MINUS this country, so not one synthetic prefix string
    # can ever have been seen. The whole-string number is therefore identically
    # 100 % unseen in every fold, for every population, always. It is printed
    # anyway, because that is the same mechanism that made `G5.4` read 0 %, and
    # a reader who sees only the second number would not know the first exists.
    #
    # The number that carries information is the second: coverage of the FIVE
    # demographic fields, with the country token stripped. That is what the
    # model can actually transfer.
    if os.path.exists(CORPUS):
        seen = corpus_prefixes(c)

        def demo(pfx):
            """Drop the leading country field -- the one the fold holds out."""
            return pfx.split(encoder.PREFIX_SEP, 1)[1]

        say('  --- coverage against the TRAINING corpus for this fold '
            '(corpus minus %s) ---' % c)
        miss = [q for q in pref_count if q not in seen]
        miss_pop = sum(pref_count[q] for q in miss)
        say('    corpus distinct prefixes                 %d' % len(seen))
        say('    [1] WHOLE STRING, unseen strata          %d of %d (%.2f %%)'
            % (len(miss), len(pref_count),
               100.0 * len(miss) / len(pref_count)))
        say('        WHOLE STRING, unseen persons         %d of %d (%.3f %%)'
            % (miss_pop, len(rows), 100.0 * miss_pop / len(rows)))
        need(len(miss) == len(pref_count),
             'the whole-string coverage is NOT 100 %% unseen. Either the '
             'corpus contains %s after all -- a leak -- or the prefix no '
             'longer starts with the country field.' % c)
        say('        ^ identically 100 %% by construction: the country token is '
            'held out.')

        seen_demo = set(demo(q) for q in seen)
        miss2 = [q for q in pref_count if demo(q) not in seen_demo]
        miss2_pop = sum(pref_count[q] for q in miss2)
        say('    [2] COUNTRY STRIPPED, unseen strata      %d of %d (%.2f %%)'
            % (len(miss2), len(pref_count),
               100.0 * len(miss2) / len(pref_count)))
        say('        COUNTRY STRIPPED, unseen persons     %d of %d (%.3f %%)'
            % (miss2_pop, len(rows), 100.0 * miss2_pop / len(rows)))
        say('        ^ THIS is the fold\'s real out-of-distribution exposure, '
            'and it is')
        say('          a diagnostic, not a gate: deleting an unseen stratum '
            'would delete')
        say('          exactly the cases the transfer claim is about.')
        big = sorted(((pref_count[q], q) for q in miss2), reverse=True)[:5]
        for k, q in big:
            say('          %6d  %s' % (k, q))
        if not miss2:
            say('          (none -- every synthetic stratum occurs in the '
                'training folds)')
    else:
        say('  corpus not present locally -- coverage diagnostic SKIPPED')

    # ---- parquet, the format the step doc names ---------------------------
    try:
        import pandas as pd
        df = pd.DataFrame(rows, columns=encoder.PREFIX_FIELDS)
        p_pq = os.path.join(OUT, 'population_%s.parquet' % c)
        df.to_parquet(p_pq, index=False)
        chk = pd.read_parquet(p_pq)
        need(list(chk.columns) == encoder.PREFIX_FIELDS,
             'parquet columns %r' % list(chk.columns))
        need(len(chk) == len(rows), 'parquet holds %d rows, expected %d'
                                    % (len(chk), len(rows)))
        say('  wrote population_%s.parquet (%d rows, re-read and verified)'
            % (c, len(chk)))
    except ImportError:
        say('  pyarrow/pandas absent -- parquet NOT written, CSV stands')

    say('  wrote %s' % os.path.basename(p_out))
    say('OK')


if __name__ == '__main__':
    try:
        main()
    except PrefixError as e:
        sys.stderr.write('REFUSED: %s\n' % e)
        sys.exit(1)
