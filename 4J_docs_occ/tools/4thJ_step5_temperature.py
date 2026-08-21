# -*- coding: utf-8 -*-
"""
4J / STEP 5, WORK ITEM 5.4 -- FIX THE DECODING TEMPERATURE ON A VALIDATION SPLIT.

The question item 5.4 asks, in the step document's own words: *does a temperature
exist at which the generated population's entropy matches the real population's,
and is it the same temperature that optimises the fidelity metrics?*

This script answers it per fold and writes `temperature_calibration.md`,
`temperature_calibration.json` and `generation_config.json`.

🔴 EVERYTHING BELOW THE LINE `PRE-REGISTERED` IS FIXED BEFORE THE FIRST RUN.
The grid is uniform and is NOT a search. The chosen temperature is picked by a
rule written down in advance, not by looking at the curves and taking the nicest
point -- that is the same move as re-banding a gate, wearing different clothes.

WHAT IS CALIBRATED ON, AND WHY IT CANNOT BE ANYTHING ELSE
=========================================================
The fold's OWN held-in validation split (`shard_manifest.json` -> `fold.heldin_val`),
i.e. diaries from the N-1 donor countries that the model never trained on.
5,520 / 3,434 / 5,702 diaries on `es` / `it` / `uk` (FINDING 11's counts).

🔴 THE TEMPERATURE IS CALIBRATED PER FOLD AND CANNOT BE SHARED. A single global
temperature would be chosen partly on Spanish validation diaries -- and Spain is
the HELD-OUT country on fold `es`. That is contamination, by the same argument
`G5.6i` scores. Three folds, three models, three temperatures.

🔴 THE PROMPTS ARE DRAWN ONCE AND REUSED AT EVERY TEMPERATURE. The comparison is
PAIRED: the same 600 real prefixes, the same 600 real diaries as the reference,
at every grid point. An unpaired draw would put sampling noise between the curve
and the knob it is supposed to be measuring.

⚪ NO DIARY WEIGHTS. `weight_dia_cal` (FINDING 53) re-bases the real population
onto the calendar week. That changes WHICH POPULATION the reference is, not what
the decoding knob does, and the design here is paired against the drawn diaries
themselves. Stated, not silently omitted.

WHAT IS IMPORTED RATHER THAN REIMPLEMENTED
==========================================
`activity_entropy_nats`, `split_prefix_body`, `parse_episodes`, `at_home_share`
and the thresholds module come from `4thJ_step4_train`. A second copy of the
entropy definition drifting from the first is exactly the failure `G5.5` exists
to prevent, and Step 4 already prints this entropy at every checkpoint -- the
numbers here have to be comparable with those.

The generation LOOP is local, because it is the one thing that must differ: the
trainer hardcodes `temperature=1.0, top_p=1.0`. Nothing in Step 4 is edited.
"""

import io
import os
import sys
import json
import math
import time
import random
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import importlib

tr = importlib.import_module('4thJ_step4_train')
TH = tr.TH

STEP4 = tr.STEP4
MANIFEST_IN = tr.MANIFEST_IN
STAGED = tr.STAGED

# ---------------------------------------------------------------------------
# PRE-REGISTERED -- written before the first run, and not tuned afterwards.
# ---------------------------------------------------------------------------

# The grid. Uniform, 0.1 apart, spanning "sharper than the model" to "flatter
# than the model". It is not refined after seeing the curve; if the optimum sits
# at an endpoint that is REPORTED as an endpoint, not chased with more points.
GRID = (0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30)

# 🔴 No truncation, at any grid point. Item 5.4's tail hazard: top-k and top-p
# delete rare behaviour, and rare behaviour -- laundry at 03:00, the shift
# worker, the early-morning charge -- is what a peak-demand study exists to
# capture. `G5.9` allows top-p only at p <= 0.98; we do not use it at all.
TOP_P = 1.0
TOP_K = 0

N_PROMPTS = 600          # same order as Step 4's stratified generation
MAX_NEW_TOKENS = 1200    # the D-S3-11 / G3.5 band, unchanged
SEED = TH.SEED

# The decision rule, in advance:
#   T_entropy  = argmin |H_gen(T) - H_real|
#   T_fidelity = argmin FID_AT_HOME(T)
#   they AGREE if |T_entropy - T_fidelity| <= AGREE_TOL (one grid step).
# 🔴 If they disagree, the step document rules it already: PICK ENTROPY
# MATCHING, because diversity is the property the downstream energy result
# depends on. That rule is not re-opened here.
AGREE_TOL = 0.1001       # one grid step, with a float-comparison margin

# A grid point whose generations are structurally broken cannot supply a
# temperature, whatever its entropy reads. Pre-registered floor, not a filter
# invented after seeing the output.
MIN_PARSEABLE_FRAC = 0.95

SLOT_MINUTES = 10        # 144 slots; the corpus has zero non-multiple-of-10
                         # durations (checked in Step 7, item 7.1)
N_SLOTS = 1440 // SLOT_MINUTES


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

def episodes_of(text):
    """(duration, act, loc) triples, or None if the text will not parse."""
    try:
        _, body = tr.split_prefix_body(text)
    except ValueError:
        return None
    try:
        eps, _ = tr.parse_episodes(body)
    except Exception:
        return None
    if not eps:
        return None
    return eps


def at_home_profile(texts):
    """Fraction at home in each 10-minute slot, over the diaries that parse.

    The 144-slot at-home curve is the same statistic `G4.1` scores
    (`TH.G4_1_STATISTIC == 'at_home_share'`) and the same family Step 6 scores
    its time-of-day cells on -- chosen for that continuity, not invented here.
    """
    num = [0.0] * N_SLOTS
    den = 0
    for t in texts:
        eps = episodes_of(t)
        if eps is None:
            continue
        slot, ok = 0, True
        home = [0] * N_SLOTS
        for e in eps:
            dur, loc = e[0], e[3]
            if dur % SLOT_MINUTES:
                ok = False
                break
            n = dur // SLOT_MINUTES
            for k in range(slot, min(slot + n, N_SLOTS)):
                home[k] = 1 if loc == TH.LOC_AT_HOME else 0
            slot += n
        if not ok or slot == 0:
            continue
        den += 1
        for k in range(N_SLOTS):
            num[k] += home[k]
    if den == 0:
        return None, 0
    return [x / float(den) for x in num], den


def act_time_shares(texts):
    """Share of TOTAL MINUTES spent in each activity code."""
    mins = collections.Counter()
    tot = 0
    for t in texts:
        eps = episodes_of(t)
        if eps is None:
            continue
        for e in eps:
            mins[e[1]] += e[0]
            tot += e[0]
    if tot == 0:
        return {}
    return dict((a, m / float(tot)) for a, m in mins.items())


def profile_mae_pp(a, b):
    return 100.0 * sum(abs(x - y) for x, y in zip(a, b)) / float(len(a))


def tvd_pp(pa, pb):
    """Total variation distance between two activity-share dicts, in points."""
    keys = set(pa) | set(pb)
    return 100.0 * 0.5 * sum(abs(pa.get(k, 0.0) - pb.get(k, 0.0)) for k in keys)


def structural(texts):
    n = len(texts)
    parse = sum(1 for t in texts if episodes_of(t) is not None)
    term = sum(1 for t in texts if TH.G4_7_EOR in t)
    sums = 0
    epc = []
    for t in texts:
        eps = episodes_of(t)
        if eps is None:
            continue
        epc.append(len(eps))
        if sum(e[0] for e in eps) == 1440:
            sums += 1
    return {'n': n,
            'parseable_frac': parse / float(n) if n else 0.0,
            'terminated_frac': term / float(n) if n else 0.0,
            'sum_1440_frac': sums / float(parse) if parse else 0.0,
            'episodes_per_diary': (sum(epc) / float(len(epc))) if epc else float('nan')}


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------

def build_model(fold, adapter, leg=4, run_type='primary'):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    staged = json.load(io.open(STAGED, encoding='utf-8'))
    # the same rule the trainer and the diagnostics use: leg 4 is the small
    # backbone regardless of run-type, so we load the base the adapter was
    # actually trained on.
    repo = tr.MODEL_FOR['pilot'] if leg == 4 else tr.MODEL_FOR[run_type]
    rev = next((r['revision'] for r in staged['repos'] if r['repo_id'] == repo), None)
    if rev is None:
        raise SystemExit('no staged revision for %s -- a checkpoint named without a '
                         'revision is not a reproducible checkpoint (G4.11)' % repo)
    tok = AutoTokenizer.from_pretrained(repo, revision=rev)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev,
                                                 torch_dtype=torch.bfloat16)
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, adapter)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device).eval()
    print('base %s @ %s + adapter %s on %s' % (repo, rev[:12], adapter, device))
    return model, tok, device, repo, rev


def generate_at(model, tok, device, prompts, temperature, gen_batch, log_every=10):
    import torch
    eor_ids = tok(TH.G4_7_EOR, add_special_tokens=False)['input_ids']
    eos_arg = eor_ids[-1] if len(eor_ids) == 1 else None
    # FINDING 12: <eor> is multi-token, so eos_token_id cannot express it.
    stop_kw = ({'eos_token_id': eos_arg} if eos_arg is not None
               else {'stop_strings': [TH.G4_7_EOR], 'tokenizer': tok})
    old_side = tok.padding_side
    tok.padding_side = 'left'          # decoder-only: prompt flush right
    out = []
    t0 = time.time()
    try:
        for i in range(0, len(prompts), gen_batch):
            chunk = prompts[i:i + gen_batch]
            enc = tok(chunk, add_special_tokens=False, return_tensors='pt',
                      padding=True).to(device)
            with torch.no_grad():
                g = model.generate(**enc, max_new_tokens=MAX_NEW_TOKENS,
                                   do_sample=True, temperature=temperature,
                                   top_p=TOP_P,
                                   pad_token_id=tok.pad_token_id, **stop_kw)
            for row in g:
                out.append(tok.decode(row, skip_special_tokens=True))
            if (i // gen_batch) % log_every == 0:
                print('    T=%.2f  generated %d/%d  (%.1f min)'
                      % (temperature, len(out), len(prompts),
                         (time.time() - t0) / 60.0), flush=True)
    finally:
        tok.padding_side = old_side
    return out


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fold', required=True, choices=['es', 'uk', 'it'])
    ap.add_argument('--adapter', required=True)
    ap.add_argument('--out', default=os.path.join(STEP4, '..', '4J_step5'))
    ap.add_argument('--gen-batch', type=int, default=8)
    ap.add_argument('--n-prompts', type=int, default=N_PROMPTS)
    ap.add_argument('--grid', default=','.join('%.2f' % t for t in GRID))
    ap.add_argument('--dry-run', action='store_true',
                    help='resolve everything and score the REAL reference only; '
                         'no model is loaded and nothing is generated')
    args = ap.parse_args()

    grid = [float(x) for x in args.grid.split(',') if x.strip()]
    outdir = os.path.abspath(args.out)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    print('=' * 74)
    print('STEP 5 ITEM 5.4 -- TEMPERATURE CALIBRATION, fold %s' % args.fold)
    print('=' * 74)
    print('grid           : %s' % ', '.join('%.2f' % t for t in grid))
    print('top_p          : %.2f  (NOT USED -- no truncation at any grid point)' % TOP_P)
    print('prompts        : %d, drawn ONCE with seed %d and reused at every T'
          % (args.n_prompts, SEED))
    print('decision rule  : T_entropy = argmin |dH|; T_fidelity = argmin at-home MAE; '
          'agree if |dT| <= %.2f; on disagreement ENTROPY WINS' % AGREE_TOL)
    print('')

    # ---- the validation split, from the shard manifest the trainer wrote ----
    man = json.load(io.open(MANIFEST_IN, encoding='utf-8'))
    fold_m = man['folds'][args.fold]
    val_path = fold_m['heldin_val']['path']
    val = tr.read_jsonl(val_path)
    print('validation split: %s' % val_path)
    print('                  %d diaries, held-in, donor countries only' % len(val))
    # the manifest carries the shard's md5; a calibration run that silently read a
    # different file than the trainer did would be undetectable afterwards.
    got = tr.md5_of_file(val_path)
    want = fold_m['heldin_val']['md5']
    if got != want:
        raise SystemExit('!!! validation shard md5 %s != manifest %s -- this is not '
                         'the split the model was trained against' % (got, want))
    if len(val) != fold_m['heldin_val']['n']:
        raise SystemExit('!!! validation shard has %d records, manifest says %d'
                         % (len(val), fold_m['heldin_val']['n']))
    print('                  md5 %s matches the shard manifest' % got)
    seen = collections.Counter(r.get('country', '?') for r in val)
    print('                  by country: %s' % dict(seen))
    if args.fold in seen:
        raise SystemExit('!!! the held-out country %s appears in its own validation '
                         'split -- refusing to calibrate on it' % args.fold)

    rng = random.Random(SEED)
    sample = rng.sample(val, min(args.n_prompts, len(val)))
    prompts = [tr.split_prefix_body(r['text'])[0] for r in sample]
    real_texts = [r['text'] for r in sample]
    print('drawn           : %d prompts (paired reference = the same %d real diaries)'
          % (len(prompts), len(real_texts)))

    # ---- the real reference, scored once ----
    h_real = tr.activity_entropy_nats(real_texts)
    prof_real, n_real = at_home_profile(real_texts)
    share_real = act_time_shares(real_texts)
    st_real = structural(real_texts)
    if prof_real is None:
        raise SystemExit('!!! the REAL reference did not parse -- nothing to match to')
    print('real reference  : H = %.4f nats over %d activity codes; at-home %.4f; '
          '%d diaries profiled' % (h_real, len(share_real),
                                   sum(prof_real) / float(N_SLOTS), n_real))
    print('')

    rows = []
    if not args.dry_run:
        model, tok, device, repo, rev = build_model(args.fold, args.adapter)
        for T in grid:
            print('--- T = %.2f' % T)
            gen = generate_at(model, tok, device, prompts, T, args.gen_batch)
            st = structural(gen)
            h = tr.activity_entropy_nats(gen)
            prof, n_prof = at_home_profile(gen)
            share = act_time_shares(gen)
            row = {'T': T,
                   'H_gen': h,
                   'dH': (h - h_real) if h == h else float('nan'),
                   'at_home_mae_pp': (profile_mae_pp(prof, prof_real)
                                      if prof else float('nan')),
                   'act_tvd_pp': tvd_pp(share, share_real) if share else float('nan'),
                   'n_activity_codes': len(share),
                   'n_profiled': n_prof}
            row.update(st)
            row['usable'] = (row['parseable_frac'] >= MIN_PARSEABLE_FRAC
                             and row['H_gen'] == row['H_gen'])
            rows.append(row)
            print('    H=%.4f  dH=%+.4f  at-home MAE=%.3f pp  ACT TVD=%.3f pp  '
                  'parse=%.3f  term=%.3f  1440=%.3f  usable=%s'
                  % (row['H_gen'], row['dH'], row['at_home_mae_pp'],
                     row['act_tvd_pp'], row['parseable_frac'],
                     row['terminated_frac'], row['sum_1440_frac'], row['usable']),
                  flush=True)
    else:
        repo = rev = '(dry run)'
        print('DRY RUN: no model loaded, no generation, no curve. The real reference '
              'above is the only thing scored.')

    usable = [r for r in rows if r['usable']]
    result = {'fold': args.fold, 'adapter': args.adapter,
              'base_repo': repo, 'base_revision': rev,
              'grid': grid, 'top_p': TOP_P, 'top_k': TOP_K,
              'n_prompts': len(prompts), 'seed': SEED,
              'max_new_tokens': MAX_NEW_TOKENS,
              'validation_split': val_path, 'validation_n': len(val),
              'H_real': h_real, 'real_structural': st_real,
              'min_parseable_frac': MIN_PARSEABLE_FRAC,
              'agree_tol': AGREE_TOL,
              'rows': rows}

    if usable:
        t_ent = min(usable, key=lambda r: abs(r['dH']))
        t_fid = min(usable, key=lambda r: r['at_home_mae_pp'])
        agree = abs(t_ent['T'] - t_fid['T']) <= AGREE_TOL
        chosen = t_ent['T']          # 🔴 entropy wins on disagreement, pre-registered
        result.update({'T_entropy': t_ent['T'], 'T_fidelity': t_fid['T'],
                       'agree': agree, 'T_chosen': chosen,
                       'chosen_basis': 'entropy matching',
                       'endpoint_entropy': t_ent['T'] in (grid[0], grid[-1]),
                       'endpoint_fidelity': t_fid['T'] in (grid[0], grid[-1])})
        print('')
        print('T_entropy  = %.2f  (|dH| = %.4f nats)' % (t_ent['T'], abs(t_ent['dH'])))
        print('T_fidelity = %.2f  (at-home MAE = %.3f pp)'
              % (t_fid['T'], t_fid['at_home_mae_pp']))
        print('%s -- chosen T = %.2f, on ENTROPY MATCHING'
              % ('THE TWO CURVES AGREE' if agree
                 else '🔴 THE TWO CURVES DISAGREE, and that is reported as a '
                      'disagreement', chosen))
        if result['endpoint_entropy'] or result['endpoint_fidelity']:
            print('🔴 an optimum sits at a GRID ENDPOINT -- reported as an endpoint. '
                  'The grid is not extended to chase it.')

    jp = os.path.join(outdir, 'temperature_calibration_%s.json' % args.fold)
    io.open(jp, 'w', encoding='utf-8').write(
        json.dumps(result, indent=2, sort_keys=True))
    print('')
    print('wrote %s' % jp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
