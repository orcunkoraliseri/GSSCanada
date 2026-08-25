# -*- coding: utf-8 -*-
"""D-S3-14 -- the UK-fold split report: strat_hh_type = unknown vs the rest.

Computes, and asserts nothing it has not computed:
  * the size and household count of the cell
  * its stratum profile against the rest of the UK fold
  * the LEVEL-1 TIME BUDGET of each side -- the SAME quantity G6.1's MAE and
    G6.4's MAPE are taken on -- and each side's error against the published
    Eurostat UK column
  * whether the model side of the split exists at all
"""
import collections
import importlib
import io
import json
import os
import sys

HERE = os.path.abspath('tools')
sys.path.insert(0, HERE)
L1 = importlib.import_module('4thJ_step6_level1')
import decoder as dec
from encoder import load_bit_positions

STEP2 = 'Step2_docs/outputs_step2/crosswalk_copresence.csv'
CORPUS = 'Step3_docs/outputs_step3/4J_step3_corpus.jsonl'
EUROSTAT = 'Step6_docs/outputs_step6/eurostat_raw'
GEN = 'Step7_docs/outputs_step7'

bitpos = load_bit_positions(STEP2)
PFX = ['country', 'strat_age_band', 'strat_sex', 'strat_hh_type',
       'strat_econ_status', 'strat_day_type']

unk, rest = [], []
unk_hh, rest_hh = set(), set()
prof = {v: {'unknown': collections.Counter(), 'rest': collections.Counter()}
        for v in PFX[1:]}
split_label = collections.Counter()
refused = collections.Counter()

for line in io.open(CORPUS, encoding='utf-8'):
    r = json.loads(line)
    if r['country'] != 'uk':
        continue
    f = r['text'].split('|', 1)[0].split(',')
    d = dict(zip(PFX, f))
    is_unk = (d['strat_hh_type'] == 'unknown')
    side = 'unknown' if is_unk else 'rest'
    for v in PFX[1:]:
        prof[v][side][d[v]] += 1
    if is_unk:
        split_label[r['split']] += 1
        unk_hh.add(r['hid'])
    else:
        rest_hh.add(r['hid'])
    try:
        rec = dec.decode_record(r['text'], bitpos)
    except Exception as e:                      # never silently drop
        refused[side] += 1
        continue
    (unk if is_unk else rest).append(rec)

print('=' * 78)
print('D-S3-14 -- UK FOLD SPLIT REPORT: strat_hh_type = unknown vs the rest')
print('=' * 78)
n_u, n_r = len(unk), len(rest)
print('diaries        unknown %d | rest %d | total %d (%.2f %% unknown)'
      % (n_u, n_r, n_u + n_r, 100.0 * n_u / (n_u + n_r)))
print('households     unknown %d | rest %d' % (len(unk_hh), len(rest_hh)))
print('D-S6-1(b) hh split of the 551: %s' % dict(split_label))
print('records refused by the decoder: %s' % (dict(refused) or 'none'))

print('')
print('-' * 78)
print('STRATUM PROFILE -- is the cell a random slice of the UK fold, or a biased one?')
print('-' * 78)
for v in PFX[1:]:
    if v == 'strat_hh_type':
        continue
    keys = sorted(set(prof[v]['unknown']) | set(prof[v]['rest']))
    tu = float(sum(prof[v]['unknown'].values())) or 1.0
    tr = float(sum(prof[v]['rest'].values())) or 1.0
    print('')
    print('%-20s %10s %10s %10s' % (v, 'unknown %', 'rest %', 'diff pp'))
    for k in keys:
        pu = 100.0 * prof[v]['unknown'][k] / tu
        pr = 100.0 * prof[v]['rest'][k] / tr
        print('  %-18s %9.2f %10.2f %10.2f' % (k, pu, pr, pu - pr))

b_u = L1.budget(unk)
b_r = L1.budget(rest)
b_all = L1.budget(unk + rest)
pub = L1.published(EUROSTAT, 'uk')

AGG = L1.AGGREGATES
print('')
print('-' * 78)
print('LEVEL-1 TIME BUDGET, min/day -- the quantity G6.1 (MAE) and G6.4 (MAPE) score')
print('-' * 78)
print('%-10s %10s %10s %10s %10s %10s' %
      ('aggregate', 'unknown', 'rest', 'all UK', 'published', 'unk-rest'))
for a in AGG:
    print('%-10s %10.2f %10.2f %10.2f %10s %10.2f'
          % (a, b_u[a], b_r[a], b_all[a],
             ('%.2f' % pub[a]) if pub.get(a) is not None else 'n/a',
             b_u[a] - b_r[a]))


def mae(side):
    d = [abs(side[a] - pub[a]) for a in AGG if pub.get(a) is not None]
    return sum(d) / len(d)


def mape(side):
    d = [100.0 * abs(side[a] - pub[a]) / pub[a]
         for a in AGG if pub.get(a) not in (None, 0)]
    return sum(d) / len(d)


print('')
print('error against the published UK column (Eurostat tus_00age, TOTAL, 2010):')
for tag, side in (('unknown cell', b_u), ('rest of fold', b_r), ('whole UK fold', b_all)):
    print('  %-14s MAE %7.3f min/day   MAPE %7.3f %%' % (tag, mae(side), mape(side)))
print('')
print('  MAE of the whole fold MINUS MAE of the fold without the cell: %+.4f min/day'
      % (mae(b_all) - mae(b_r)))
_w = max(((a, b_all[a] - b_r[a]) for a in AGG), key=lambda t: abs(t[1]))
print('  worst single aggregate shift from dropping the cell: %s %+.4f min/day' % _w)

print('')
print('-' * 78)
print('THE MODEL SIDE OF THE SPLIT')
print('-' * 78)
for leg in (4, 5):
    for tag in ('constrained', 'nogrammar'):
        p = os.path.join(GEN, 'generated_leg%d_uk_%s.jsonl' % (leg, tag))
        if not os.path.exists(p):
            print('  leg %d %-12s MISSING' % (leg, tag))
            continue
        c = collections.Counter()
        for line in io.open(p, encoding='utf-8'):
            c[json.loads(line).get('strat_hh_type', '?')] += 1
        print('  leg %d %-12s n=%6d   diaries at strat_hh_type=unknown: %d'
              % (leg, tag, sum(c.values()), c.get('unknown', 0)))
cfg = json.load(io.open('Step5_docs/outputs_step5/generation_config_uk.json',
                        encoding='utf-8'))
print('  generation_config_uk.json mentions "unknown": %s'
      % ('unknown' in json.dumps(cfg)))
