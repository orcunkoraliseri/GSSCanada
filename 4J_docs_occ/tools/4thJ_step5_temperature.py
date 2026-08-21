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

    The 144-slot at-home curve is the same QUANTITY `G4.1` scores
    (`TH.G4_1_STATISTIC == 'at_home_share'`) and the same family Step 6 scores
    its time-of-day cells on -- chosen for that continuity, not invented here.

    🔴 D-S5-14(a) / FINDING 67 -- THE PER-SLOT DENOMINATOR, ADDED 2026-08-21.
    A generated diary whose episodes total less than 1440 minutes stops filling
    at `slot < 144`. Before this change the untouched tail kept its initial `0`
    and the diary was still counted in the denominator for all 144 slots, so a
    MISSING tail was scored as AWAY FROM HOME. Real diaries are unaffected (all
    73,254 sum to exactly 1440); generated ones are (`sum_1440_frac` 0.05-0.135),
    and the failure rate MOVES ALONG THE TEMPERATURE AXIS being swept.

    🔴 THE RULING IS ADDITIVE AND NOTHING REGISTERED MOVES. Three things are
    returned, not one:

      `profile`         -- EXISTING, BIT-IDENTICAL to the pre-D-S5-14 curve
                           (divide by the diary count, phantom tail included),
                           so every number already recorded stays comparable;
      `profile_covered` -- NEW, each slot divided by the number of diaries that
                           actually REACH it; `None` where nothing reaches it;
      `coverage_curve`  -- NEW, 144 counts, the diagnostic that makes the
                           confound visible instead of merely arguable.

    ⚪ SCOPE, verified rather than asserted (the item ledger left this open):
    `G4.1` does NOT use this function. It uses `at_home_share()` in
    `4thJ_step4_train.py:150`, which is a per-diary SCALAR normalised by that
    diary's OWN total minutes -- a short diary is scored on its own length and
    grows no phantom tail. `at_home_profile` is defined once, in this file, and
    called twice, both in this file. So option (a)'s scope claim holds by
    CONSTRUCTION and not merely by ruling.
    """
    num = [0.0] * N_SLOTS
    den = [0] * N_SLOTS          # D-S5-14: den becomes a VECTOR
    n_diaries = 0
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
        n_diaries += 1
        covered = min(slot, N_SLOTS)
        for k in range(covered):
            den[k] += 1
            num[k] += home[k]
        # `home[k]` is 0 for every k >= covered, so accumulating only up to
        # `covered` leaves `num` identical to the pre-D-S5-14 accumulation. That
        # is what makes `profile` below bit-identical, and the selftest proves it
        # against a verbatim copy of the old function rather than asserting it.
    if n_diaries == 0:
        return None
    return {'profile': [num[k] / float(n_diaries) for k in range(N_SLOTS)],
            'profile_covered': [(num[k] / float(den[k])) if den[k] else None
                                for k in range(N_SLOTS)],
            'coverage_curve': den,
            'n': n_diaries}


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


def profile_mae_pp_covered(a, b):
    """D-S5-14(a): the SAME mean absolute error, averaged over the slots where
    BOTH curves are defined -- i.e. where at least one diary on each side reaches
    the slot. Returns (mae_pp, n_slots_compared). It is reported ALONGSIDE
    `profile_mae_pp`; it does not replace it and it does not choose anything."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return float('nan'), 0
    return (100.0 * sum(abs(x - y) for x, y in pairs) / float(len(pairs)),
            len(pairs))


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


def generate_at(model, tok, device, prompts, temperature, gen_batch, log_every=10,
                gen_seed=None):
    """🔴 `FINDING 66` / `I-5`: the sampling RNG is seeded HERE, per call.

    Before this, `do_sample=True` ran off torch's default RNG state, which
    advanced across the whole sweep -- so no single realisation could be
    reproduced, not even by re-running the same script on the same node, while
    the result JSON wrote `seed: 42` beside the curve where a reader would take
    it to mean the curve was seeded. It scoped the PROMPT DRAW only, and that
    key is now called `prompt_seed` for exactly that reason.

    🔴 WHAT THIS DOES NOT BUY, and the sentence we may not write.
    `RP05`: bit-exact reproducibility additionally needs `batch_size=1`,
    `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`
    AND a fixed GPU architecture. Speed jobs land on whichever node is free, so
    **we cannot claim bit-reproducibility at all.** The claim this supports is
    "pinned base revision + pinned adapter + RECORDED SEEDS", never
    "reproducible". A seeded run is re-runnable and auditable; it is not
    bit-identical, and the JSON says so in `reproducibility_claim`.
    """
    import torch
    if gen_seed is not None:
        torch.manual_seed(gen_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(gen_seed)
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
    # --- D-S5-13(a): the replicate design, ruled 2026-08-21 -----------------
    ap.add_argument('--gen-seeds', default='',
                    help='D-S5-13(a). Comma-separated sampling seeds; ONE '
                         'generation pass per (T, seed). Empty = the primary '
                         'single-realisation design, unchanged.')
    ap.add_argument('--save-gen', default='',
                    help='directory to persist the generated text, one .jsonl '
                         'per (T, seed). Not saving it is why the covered-basis '
                         'numbers could not be re-derived for the first sweep.')
    ap.add_argument('--tag', default='',
                    help='suffix for the output JSON, so a replicate run cannot '
                         'overwrite the primary artefact')
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
    ahp_real = at_home_profile(real_texts)
    share_real = act_time_shares(real_texts)
    st_real = structural(real_texts)
    if ahp_real is None:
        raise SystemExit('!!! the REAL reference did not parse -- nothing to match to')
    prof_real = ahp_real['profile']
    prof_real_cov = ahp_real['profile_covered']
    cov_real = ahp_real['coverage_curve']
    n_real = ahp_real['n']
    print('real reference  : H = %.4f nats over %d activity codes; at-home %.4f; '
          '%d diaries profiled' % (h_real, len(share_real),
                                   sum(prof_real) / float(N_SLOTS), n_real))
    # D-S5-14: the reference's OWN coverage, printed rather than assumed. Every
    # real diary sums to 1440, so this must read 1.000 at slot 143; if it ever
    # does not, the reference is the thing that is broken.
    print('                  coverage curve: min %.3f, slot 143 %.3f (of %d diaries)'
          % (min(cov_real) / float(n_real), cov_real[-1] / float(n_real), n_real))
    print('')

    gen_seeds = [int(x) for x in args.gen_seeds.split(',') if x.strip()]
    replicate_mode = bool(gen_seeds)
    if not replicate_mode:
        gen_seeds = [None]          # the primary design, one unseeded pass
    if args.save_gen and not os.path.isdir(args.save_gen):
        os.makedirs(args.save_gen)

    rows = []
    if not args.dry_run:
        model, tok, device, repo, rev = build_model(args.fold, args.adapter)
        for T in grid:
          for gs in gen_seeds:
            print('--- T = %.2f%s' % (T, '' if gs is None else '  seed %d' % gs))
            gen = generate_at(model, tok, device, prompts, T, args.gen_batch,
                              gen_seed=gs)
            if args.save_gen:
                gp = os.path.join(args.save_gen, 'gen_%s_T%.2f_s%s.jsonl'
                                  % (args.fold, T, 'none' if gs is None else gs))
                with io.open(gp, 'w', encoding='utf-8') as fh:
                    for pr, tx in zip(prompts, gen):
                        fh.write(json.dumps({'T': T, 'gen_seed': gs,
                                             'prompt': pr, 'text': tx}) + '\n')
                print('    saved %d generations -> %s' % (len(gen), gp))
            st = structural(gen)
            h = tr.activity_entropy_nats(gen)
            ahp = at_home_profile(gen)
            share = act_time_shares(gen)
            # D-S5-14(a): THREE at-home numbers, not one. The first is the
            # existing statistic, untouched; the other two are the diagnostic.
            if ahp is None:
                mae, mae_cov, n_cmp, cov, n_prof = (float('nan'), float('nan'),
                                                    0, None, 0)
            else:
                mae = profile_mae_pp(ahp['profile'], prof_real)
                mae_cov, n_cmp = profile_mae_pp_covered(ahp['profile_covered'],
                                                        prof_real_cov)
                cov = ahp['coverage_curve']
                n_prof = ahp['n']
            row = {'T': T,
                   'gen_seed': gs,          # I-5 / FINDING 66: recorded per row
                   'H_gen': h,
                   'dH': (h - h_real) if h == h else float('nan'),
                   'at_home_mae_pp': mae,
                   'at_home_mae_pp_covered': mae_cov,
                   'coverage_curve': cov,
                   'coverage_min_frac': (min(cov) / float(n_prof)
                                         if cov and n_prof else float('nan')),
                   'coverage_last_slot_frac': (cov[-1] / float(n_prof)
                                               if cov and n_prof else float('nan')),
                   'n_slots_compared': n_cmp,
                   'act_tvd_pp': tvd_pp(share, share_real) if share else float('nan'),
                   'n_activity_codes': len(share),
                   'n_profiled': n_prof}
            row.update(st)
            row['usable'] = (row['parseable_frac'] >= MIN_PARSEABLE_FRAC
                             and row['H_gen'] == row['H_gen'])
            rows.append(row)
            print('    H=%.4f  dH=%+.4f  at-home MAE=%.3f pp  [covered %.3f pp over '
                  '%d slots, coverage @143 %.3f]  ACT TVD=%.3f pp  '
                  'parse=%.3f  term=%.3f  1440=%.3f  usable=%s'
                  % (row['H_gen'], row['dH'], row['at_home_mae_pp'],
                     row['at_home_mae_pp_covered'], row['n_slots_compared'],
                     row['coverage_last_slot_frac'],
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
              # 🔴 I-5: renamed from `seed`, which a reader took to mean the
              # curve was seeded. It scopes the PROMPT DRAW and nothing else.
              'n_prompts': len(prompts), 'prompt_seed': SEED,
              'gen_seeds': [s for s in gen_seeds if s is not None],
              'replicate_mode': replicate_mode,
              'saved_generations_to': args.save_gen or None,
              'reproducibility_claim':
                  ('pinned base revision + pinned adapter + recorded sampling '
                   'seeds. 🔴 NOT bit-reproducible: RP05 requires batch_size=1, '
                   'deterministic algorithms, CUBLAS_WORKSPACE_CONFIG and a '
                   'fixed GPU architecture, and Speed schedules across nodes.')
                  if replicate_mode else
                  ('🔴 NOT SEEDED (FINDING 66). The sampling RNG ran off torch '
                   'default state; this curve cannot be reproduced.'),
              'max_new_tokens': MAX_NEW_TOKENS,
              'validation_split': val_path, 'validation_n': len(val),
              'H_real': h_real, 'real_structural': st_real,
              'real_coverage_curve': cov_real,          # D-S5-14, 144 counts
              'real_n_profiled': n_real,
              'min_parseable_frac': MIN_PARSEABLE_FRAC,
              'agree_tol': AGREE_TOL,
              'rows': rows}

    # -----------------------------------------------------------------------
    # D-S5-13(a): in replicate mode the job is to MEASURE THE SPREAD, not to
    # choose again. `G5.8`'s clause compares the step-to-step difference with
    # the re-run spread, so both are emitted and neither is a new decision.
    # 🔴 The choice made by the primary run is NOT recomputed here.
    # -----------------------------------------------------------------------
    if replicate_mode and rows:
        by_t = collections.OrderedDict()
        for r in rows:
            by_t.setdefault(r['T'], []).append(r)
        METRICS = ('H_gen', 'dH', 'at_home_mae_pp', 'at_home_mae_pp_covered',
                   'act_tvd_pp', 'sum_1440_frac', 'terminated_frac')
        spread = []
        for T, rs in by_t.items():
            e = {'T': T, 'n_seeds': len(rs)}
            for m in METRICS:
                v = [r[m] for r in rs if r.get(m) == r.get(m)]
                if not v:
                    continue
                mu = sum(v) / float(len(v))
                sd = (sum((x - mu) ** 2 for x in v) / float(len(v) - 1)) ** 0.5 \
                    if len(v) > 1 else 0.0
                e[m] = {'mean': mu, 'sd': sd, 'min': min(v), 'max': max(v),
                        'range': max(v) - min(v)}
            spread.append(e)
        result_spread = {'per_T': spread}
        # the comparison `G5.8` actually asks for, computed rather than left to
        # the reader: is the step-to-step movement bigger than the re-run noise?
        ts = [e['T'] for e in spread]
        for m in METRICS:
            steps, ranges = [], []
            for i in range(len(spread) - 1):
                a, b = spread[i].get(m), spread[i + 1].get(m)
                if a and b:
                    steps.append(abs(b['mean'] - a['mean']))
            for e in spread:
                if e.get(m):
                    ranges.append(e[m]['range'])
            if steps and ranges:
                result_spread[m] = {
                    'max_step_between_adjacent_T': max(steps),
                    'max_within_T_range_over_seeds': max(ranges),
                    'step_exceeds_noise': max(steps) > max(ranges)}
        print('')
        print('--- D-S5-13(a) SPREAD, %d grid points x %d seeds ---'
              % (len(ts), len(gen_seeds)))
        for m in METRICS:
            d = result_spread.get(m)
            if d:
                print('  %-24s max step %9.4f   max re-run range %9.4f   %s'
                      % (m, d['max_step_between_adjacent_T'],
                         d['max_within_T_range_over_seeds'],
                         'step > noise' if d['step_exceeds_noise']
                         else '🔴 NOISE DOMINATES'))
        result['spread'] = result_spread

    # 🔴 D-S5-13(a): a replicate run MEASURES SPREAD. It does not choose again.
    # Taking argmin over (T, seed) rows would pick the luckiest realisation at
    # the luckiest temperature -- the exact move the pre-registered rule exists
    # to prevent. The choice stays where it was made, in the primary artefact.
    if replicate_mode:
        print('')
        print('🔴 REPLICATE MODE: no temperature is chosen here. T_chosen stays '
              'as ruled in temperature_calibration_%s.json.' % args.fold)
        result['choice_deliberately_not_recomputed'] = True
    elif usable:
        t_ent = min(usable, key=lambda r: abs(r['dH']))
        t_fid = min(usable, key=lambda r: r['at_home_mae_pp'])
        agree = abs(t_ent['T'] - t_fid['T']) <= AGREE_TOL
        chosen = t_ent['T']          # 🔴 entropy wins on disagreement, pre-registered
        result.update({'T_entropy': t_ent['T'], 'T_fidelity': t_fid['T'],
                       'agree': agree, 'T_chosen': chosen,
                       'chosen_basis': 'entropy matching',
                       'endpoint_entropy': t_ent['T'] in (grid[0], grid[-1]),
                       'endpoint_fidelity': t_fid['T'] in (grid[0], grid[-1])})
        # D-S5-14(a): the covered-basis argmin is REPORTED, never used. If it
        # differs from `T_fidelity` the confound moved the fidelity optimum, and
        # that is exactly the quantity FINDING 67 said did not yet exist. It is
        # deliberately NOT fed into `agree`, `chosen`, or any endpoint flag --
        # the decision rule is pre-registered and this does not re-open it.
        usable_cov = [r for r in usable
                      if r['at_home_mae_pp_covered'] == r['at_home_mae_pp_covered']]
        if usable_cov:
            t_fid_cov = min(usable_cov, key=lambda r: r['at_home_mae_pp_covered'])
            result.update({
                'T_fidelity_covered_REPORTED_NOT_USED': t_fid_cov['T'],
                'fidelity_argmin_moved_under_D_S5_14':
                    abs(t_fid_cov['T'] - t_fid['T']) > AGREE_TOL})
        print('')
        print('T_entropy  = %.2f  (|dH| = %.4f nats)' % (t_ent['T'], abs(t_ent['dH'])))
        print('T_fidelity = %.2f  (at-home MAE = %.3f pp)'
              % (t_fid['T'], t_fid['at_home_mae_pp']))
        if usable_cov:
            print('T_fidelity on the COVERED basis = %.2f (MAE %.3f pp) -- REPORTED, '
                  'NOT USED; the pre-registered rule is unchanged'
                  % (t_fid_cov['T'], t_fid_cov['at_home_mae_pp_covered']))
        print('%s -- chosen T = %.2f, on ENTROPY MATCHING'
              % ('THE TWO CURVES AGREE' if agree
                 else '🔴 THE TWO CURVES DISAGREE, and that is reported as a '
                      'disagreement', chosen))
        if result['endpoint_entropy'] or result['endpoint_fidelity']:
            print('🔴 an optimum sits at a GRID ENDPOINT -- reported as an endpoint. '
                  'The grid is not extended to chase it.')

    jp = os.path.join(outdir, 'temperature_calibration_%s%s.json'
                      % (args.fold, ('_' + args.tag) if args.tag else ''))
    io.open(jp, 'w', encoding='utf-8').write(
        json.dumps(result, indent=2, sort_keys=True))
    print('')
    print('wrote %s' % jp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
