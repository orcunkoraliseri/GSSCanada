# -*- coding: utf-8 -*-
"""Selftest for `G5.8` and `G5.9` -- the two Step 5 checkers that have never
been seen doing anything but BLOCKED.

Every other checker in this project carries a `_selftest.py` and has been seen
failing. `G5.8`/`G5.9` could not be, because they read artefacts that do not
exist yet (`temperature_calibration_<fold>_replicates.json` and
`generation_config_<fold>.json`, both owed by jobs 1285712-1285714).

This drives BOTH checkers through PASS / FAIL / BLOCKED on CONSTRUCTED state,
so that the logic is demonstrated before the real artefacts land. It is NOT a
substitute for the real verdict: a gate is only "seen failing" for the record
when its REGISTERED perturbation fells it on the REAL artefact. What this file
buys is that we already know the perturbation will fire, instead of finding out
at the last step.

Run:  py -3 tools/4thJ_step5_g58_g59_selftest.py
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    'g5', os.path.join(HERE, '4thJ_gates_step5.py'))
g5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g5)

FAILURES = []


def check(name, got, want):
    ok, msg = got
    verdict = {True: 'PASS', False: 'FAIL', None: 'BLOCKED'}[ok]
    hit = (ok is want) if want is None or isinstance(want, bool) else False
    print('  %-4s %-52s -> %-7s  %s'
          % ('ok' if hit else 'XX', name, verdict, msg[:96]))
    if not hit:
        FAILURES.append('%s: expected %s, got %s'
                        % (name, {True: 'PASS', False: 'FAIL',
                                  None: 'BLOCKED'}[want], verdict))


# --------------------------------------------------------------------------
# fixtures. A minimal but STRUCTURALLY HONEST calibration artefact: the row
# keys are the ones `4thJ_step5_temperature.py` actually writes.
# --------------------------------------------------------------------------
def cal_full():
    return {'T_entropy': 1.10, 'T_fidelity': 1.00, 'agree': True,
            'T_chosen': 1.10, 'grid': [0.9, 1.0, 1.1],
            'rows': [{'T': t, 'H_gen': 2.0, 'dH': 0.01,
                      'at_home_mae_pp': 3.0, 'usable': True}
                     for t in (0.9, 1.0, 1.1)]}


def rep_full(n_seeds=5, step_exceeds=True, with_spread=True):
    r = {'gen_seeds': list(range(101, 101 + n_seeds)),
         'grid': [1.0, 1.1, 1.2], 'replicate_mode': True}
    if with_spread:
        r['spread'] = {
            'per_T': [],
            'at_home_mae_pp': {
                'max_step_between_adjacent_T': 0.90 if step_exceeds else 0.05,
                'max_within_T_range_over_seeds': 0.10,
                'step_exceeds_noise': bool(step_exceeds)}}
    return r


def st(cal=None, rep=None, cfg=None):
    return {'calibration': cal, 'replicates': rep, 'gen_config': cfg}


print('')
print('=== G5.8 -- temperature calibration reported + the sensitivity clause ===')

check('no calibration artefact at all',
      g5.g5_8(st()), None)

# the REGISTERED perturbation: "report only the fidelity curve".
p = cal_full()
for row in p['rows']:
    del row['H_gen']
    del row['dH']
del p['T_entropy']
check('PERTURBATION p_only_fidelity: entropy curve removed',
      g5.g5_8(st(cal=p)), False)

# the mirror case, so the gate is not merely counting keys
p = cal_full()
for row in p['rows']:
    del row['at_home_mae_pp']
del p['T_fidelity']
check('mirror: fidelity curve removed',
      g5.g5_8(st(cal=p)), False)

p = cal_full()
del p['agree']
check('both curves present, agreement NOT stated',
      g5.g5_8(st(cal=p)), False)

check('reporting satisfied, no replicate artefact yet (today)',
      g5.g5_8(st(cal=cal_full())), None)

check('replicates carry only 4 seeds (val doc demands >= 5)',
      g5.g5_8(st(cal=cal_full(), rep=rep_full(n_seeds=4))), False)

check('replicates carry no spread block',
      g5.g5_8(st(cal=cal_full(), rep=rep_full(with_spread=False))), False)

check('NOISE DOMINATES: step 0.05 < re-run range 0.10 -> BAND',
      g5.g5_8(st(cal=cal_full(), rep=rep_full(step_exceeds=False))), False)

check('everything satisfied: step 0.90 > re-run range 0.10',
      g5.g5_8(st(cal=cal_full(), rep=rep_full())), True)

# the gate must not pass on the sensitivity clause while the REPORTING half is
# broken -- the whole reason both conditions are scored.
p = cal_full()
del p['agree']
check('sensitivity OK but agreement missing -> still FAIL',
      g5.g5_8(st(cal=p, rep=rep_full())), False)


print('')
print('=== G5.9 -- no truncation creep (FINDING 69 lives here) ===')

check('no generation config for this fold',
      g5.g5_9(st()), None)

check('config does not assert top_p at all',
      g5.g5_9(st(cfg={'top_k': 0})), False)

check('our configuration: top_p = 1.0, top-p NOT USED -> vacuous',
      g5.g5_9(st(cfg={'top_p': 1.0})), True)

# the REGISTERED perturbation. Under the AS-WRITTEN reading (p <= 0.98) this
# would PASS and the register would be self-contradictory; under the coherent
# reading (p >= 0.98) it fells the gate, which is what the register says.
check('PERTURBATION p_top_p_09: top_p = 0.9',
      g5.g5_9(st(cfg={'top_p': 0.9})), False)

check('top_p = 0.99 -- used, but deletes almost nothing',
      g5.g5_9(st(cfg={'top_p': 0.99})), True)

# FINDING 69 in one line: the as-written reading ADMITS this.
check('FINDING 69: top_p = 0.5 -- half the tail deleted',
      g5.g5_9(st(cfg={'top_p': 0.5})), False)

check('boundary: top_p = 0.98 exactly',
      g5.g5_9(st(cfg={'top_p': 0.98})), True)


print('')
if FAILURES:
    print('SELFTEST FAILED -- %d case(s):' % len(FAILURES))
    for f in FAILURES:
        print('  * %s' % f)
    sys.exit(1)
print('SELFTEST GREEN -- 17 of 17 cases.')
print('')
print('Demonstrated here, on constructed state: both registered perturbations')
print('fell their gate, BLOCKED is returned only when the artefact is absent,')
print('and G5.8 cannot be carried by either half of its two conditions alone.')
print('NOT demonstrated: the real verdict. That needs 1285712-1285714.')
sys.exit(0)
