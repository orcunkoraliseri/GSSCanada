# -*- coding: utf-8 -*-
"""
4J / STEP 5 -- SELFTEST FOR `D-S5-14`(a) / `FINDING 67`: THE PER-SLOT DENOMINATOR.

🔴 THIS FILE EXISTS TO BE SEEN FAILING. `feedback_gates_must_be_seen_failing`: a
diagnostic that has never been observed to detect the thing it is for has not
been shown to work. The ruling names the perturbation explicitly:

    "feed it diaries truncated at 1000 minutes. The coverage curve must drop to
     zero after slot 100 and the two MAEs must diverge. If they do not, the
     per-slot denominator is not wired in and the result must not be reported."

and it names the constraint that makes the change additive:

    "`at_home_mae_pp` unchanged so every recorded number stays comparable"

so the identity of the legacy curve is not asserted here -- it is CHECKED, value
by value, against a VERBATIM COPY of the pre-`D-S5-14` function kept below.

Run:  py -3 tools/4thJ_step5_athome_selftest.py
"""

import io
import os
import sys
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

T5 = importlib.import_module('4thJ_step5_temperature')
TH = T5.TH

N_SLOTS = T5.N_SLOTS            # 144
SLOT = T5.SLOT_MINUTES          # 10
HOME = TH.LOC_AT_HOME           # 'at_home'
AWAY = 'private_transport'      # any legal non-home LOC; the code tests equality


# ---------------------------------------------------------------------------
# THE PRE-`D-S5-14` FUNCTION, COPIED VERBATIM FROM
# tools/4thJ_step5_temperature.py.bak_ds514 lines 130-161. Do not "improve" it:
# its only job is to be the thing the new `profile` must still equal exactly.
# ---------------------------------------------------------------------------

def old_at_home_profile(texts):
    num = [0.0] * N_SLOTS
    den = 0
    for t in texts:
        eps = T5.episodes_of(t)
        if eps is None:
            continue
        slot, ok = 0, True
        home = [0] * N_SLOTS
        for e in eps:
            dur, loc = e[0], e[3]
            if dur % SLOT:
                ok = False
                break
            n = dur // SLOT
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


# ---------------------------------------------------------------------------
# synthetic diaries -- the format is the corpus format, not a mock of it
# ---------------------------------------------------------------------------

PREFIX = 'uk,25-44,f,couple_no_children,weekday' + TH.PREFIX_BODY_SEP


def diary(segments, terminate=True):
    """segments = [(minutes, loc), ...]; loc is 'at_home' or something else."""
    body = ';'.join('%03d,110,000,%s,1' % (m, loc) for m, loc in segments)
    return PREFIX + body + (TH.G4_7_EOR if terminate else '')


def realistic(total=1440):
    """At home 00:00-08:00 and 18:00-24:00, away in between -- then TRUNCATED to
    `total` minutes by dropping whatever falls past it. A diary that stops early
    is exactly the object `FINDING 67` mis-scores."""
    plan = [(480, HOME), (600, AWAY), (360, HOME)]     # 480+600+360 = 1440
    out, used = [], 0
    for m, loc in plan:
        if used >= total:
            break
        take = min(m, total - used)
        out.append((take, loc))
        used += take
    return diary(out)


# ---------------------------------------------------------------------------

FAILS = []


def check(name, cond, detail=''):
    print('  %-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                           ('  -- ' + detail) if detail else ''))
    if not cond:
        FAILS.append(name)
    return cond


def main():
    print('=' * 74)
    print('D-S5-14(a) SELFTEST -- per-slot denominator, coverage curve, two MAEs')
    print('=' * 74)

    # ---- 1. the legacy curve is bit-identical -----------------------------
    print('')
    print('1. `at_home_mae_pp`s input curve is UNCHANGED (the additivity claim)')
    mixed = ([realistic(1440)] * 5 + [realistic(1000)] * 3 + [realistic(700)] * 2)
    new = T5.at_home_profile(mixed)
    old_prof, old_den = old_at_home_profile(mixed)
    check('legacy profile identical, all 144 slots',
          new['profile'] == old_prof,
          'max |diff| = %.3e' % max(abs(a - b) for a, b in
                                    zip(new['profile'], old_prof)))
    check('diary count identical', new['n'] == old_den,
          'new n=%d, old den=%d' % (new['n'], old_den))

    # ---- 2. full coverage: the two bases must COINCIDE --------------------
    print('')
    print('2. On diaries that all fill the day, the two bases must agree exactly')
    full = [realistic(1440)] * 10
    f = T5.at_home_profile(full)
    check('coverage curve is flat at n', set(f['coverage_curve']) == {f['n']},
          'min=%d max=%d n=%d' % (min(f['coverage_curve']),
                                  max(f['coverage_curve']), f['n']))
    check('covered profile == legacy profile',
          f['profile_covered'] == f['profile'])
    mae_c, n_cmp = T5.profile_mae_pp_covered(f['profile_covered'],
                                             f['profile_covered'])
    check('144 slots compared', n_cmp == 144, 'n_slots_compared=%d' % n_cmp)

    # ---- 3. 🔴 THE PERTURBATION THE RULING NAMES --------------------------
    print('')
    print('3. 🔴 PERTURBATION -- diaries truncated at 1000 minutes')
    real = [realistic(1440)] * 10                 # the reference, always complete
    gen = [realistic(1000)] * 10                 # the "generated" side, truncated
    R = T5.at_home_profile(real)
    G = T5.at_home_profile(gen)

    zero_after_100 = all(c == 0 for c in G['coverage_curve'][100:])
    full_before_100 = all(c == G['n'] for c in G['coverage_curve'][:100])
    check('coverage curve falls to ZERO after slot 100',
          zero_after_100 and full_before_100,
          'slots 0-99 = %d, slots 100-143 = %d'
          % (G['coverage_curve'][0], G['coverage_curve'][100]))
    check('covered profile is None exactly where nothing reaches',
          all(v is None for v in G['profile_covered'][100:])
          and all(v is not None for v in G['profile_covered'][:100]))

    mae_legacy = T5.profile_mae_pp(G['profile'], R['profile'])
    mae_cov, n_cmp = T5.profile_mae_pp_covered(G['profile_covered'],
                                               R['profile_covered'])
    diverge = abs(mae_legacy - mae_cov)
    check('the two MAEs DIVERGE', diverge > 1.0,
          'legacy %.3f pp vs covered %.3f pp over %d slots  (gap %.3f pp)'
          % (mae_legacy, mae_cov, n_cmp, diverge))
    # the truncated tail is 44 slots, of which 36 are at-home in the reference
    # (18:00-24:00 = 36 slots) -- so the legacy basis invents 36/144 = 25.0 pp of
    # phantom absence and the covered basis, comparing only slots both sides
    # reach, reads exactly zero error. Those numbers are arithmetic, not a fit.
    check('covered MAE reads ~0 where the two curves actually overlap',
          mae_cov < 1e-9, 'covered = %.6f pp' % mae_cov)
    check('legacy MAE is inflated by the phantom tail alone',
          abs(mae_legacy - 25.0) < 1e-9, 'legacy = %.6f pp, arithmetic = 25.0'
          % mae_legacy)

    # ---- 4. the WIRING test: without the fix the perturbation is invisible -
    print('')
    print('4. 🔴 SEEN FAILING -- the same perturbation against the OLD function')
    old_g, _ = old_at_home_profile(gen)
    old_r, _ = old_at_home_profile(real)
    old_mae = T5.profile_mae_pp(old_g, old_r)
    check('the old function reports ONE number and it is the contaminated one',
          abs(old_mae - mae_legacy) < 1e-12,
          'old %.6f pp == new legacy %.6f pp' % (old_mae, mae_legacy))
    check('the old function emits NO coverage curve to inspect',
          not isinstance(old_at_home_profile(gen), dict),
          'returns (profile, scalar den) -- the truncation is unobservable')
    print('     => with the per-slot denominator NOT wired in, a diary that fills')
    print('        69.4 % of the day and one that fills all of it are scored the')
    print('        same way, and nothing in the output says so. That is the')
    print('        failure this diagnostic was added to make visible.')

    # ---- 5. degenerate inputs --------------------------------------------
    print('')
    print('5. Degenerate inputs')
    check('nothing parseable -> None', T5.at_home_profile(['garbage']) is None)
    check('empty input -> None', T5.at_home_profile([]) is None)
    odd = diary([(7, HOME), (1433, AWAY)])       # 7 is not a multiple of 10
    check('non-multiple-of-10 durations still rejected',
          T5.at_home_profile([odd]) is None)

    print('')
    print('=' * 74)
    if FAILS:
        print('🔴 %d CHECK(S) FAILED: %s' % (len(FAILS), ', '.join(FAILS)))
        return 1
    print('🟢 ALL CHECKS PASS -- the per-slot denominator is wired in, the legacy')
    print('   number is unchanged, and the truncation perturbation was SEEN felling')
    print('   the coverage curve and separating the two MAEs by %.3f pp.' % diverge)
    print('=' * 74)
    return 0


if __name__ == '__main__':
    sys.exit(main())
