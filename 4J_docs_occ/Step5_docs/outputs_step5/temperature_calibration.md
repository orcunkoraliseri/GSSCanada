# Step 5 — temperature calibration

**Artefact of record for the generation temperature of all three LOCO folds.** Written by
`tools/4thJ_step5_mk_calibration_doc.py` from the calibration artefacts themselves; every
number below is read from a JSON in this directory, none is transcribed by hand. Regenerate
rather than edit.

🔴 **Read `Step5_docs/impl/2026-08-21_item5.4-temperature.md` before quoting any number here.**
It carries `FINDING 67`, `FINDING 71`, `FINDING 74`, `FINDING 76` and `D-S5-16`, **RULED (a)
by the author 2026-08-22**.

## 1. What was run

Three passes, all on the same engine (`4thJ_step5_temperature.py`), all with the sampling
configuration held fixed and only the temperature varying.

| pass | grid | seeds | purpose | chooses? |
|---|---|---|---|---|
| **primary sweep** | 0.50 … 1.30 step 0.10 (9 points) | one realisation, seed 42 | select `T_chosen` | 🔴 **yes** — this is the pass the choice comes from |
| **replicates** (`D-S5-13`(a)) | 3 points around `T_chosen` | **101–105** | measure re-run spread against step size | ⚪ no — replicate mode refuses |
| **coverage-101** (`D-S5-15`(a)) | the 6 points the replicate window misses | 101 only | complete the covered-basis curve to 9 points | ⚪ no — replicate mode refuses |

Held identical across all three passes: `n_prompts` **600** per grid point, prompt seed **42**,
`top_p` **1.0**, `top_k` **0**, `max_new_tokens` **1200**, base `allenai/OLMo-2-0425-1B` pinned at
revision `a1847dff35000b4271fa70afc5db10fd29fedbdf`, per-fold LoRA adapter from the Step 4 Leg-4
primary run. Generations are persisted (`--save-gen`) so no statistic here ever needs a GPU to be
re-derived.

## 2. The chosen temperature

| fold | `T_chosen` | basis | `T_entropy` | `T_fidelity` | curves agree? | grid endpoint? |
|---|---|---|---|---|---|---|
| `es` (Spain) | **1.30** | entropy matching | 1.30 | 0.70 | 🔴 **no** | 🔴 **entropy at grid top** |
| `uk` (United Kingdom) | **1.10** | entropy matching | 1.10 | 1.00 | 🟢 **yes** | no |
| `it` (Italy) | **1.20** | entropy matching | 1.20 | 0.80 | 🔴 **no** | no |

**The selection rule is pre-registered and it is not the fidelity curve.** Where the two curves
disagree, **entropy wins** (`4thJ_step5_temperature.py:607`); `agree` is defined as
abs(`T_entropy` − `T_fidelity`) ≤ `agree_tol`.

🔴 **`uk`'s `agree = True` holds by `0.0001`.** abs(1.10 − 1.00) = `0.1000` against `agree_tol`
= `0.1001`. That is a floating-point guard band, not a finding about the model. Write **"the two
curves agree to within one grid step"**, never *"the two curves agree"*.

🔴 **And that margin does not survive a re-run — see §6.5 (`FINDING 76`).**
At generation seed `101` the `uk` fidelity argmin moves one further grid step away, the gap
becomes `0.2000`, and `agree` would read **False**. The single `True` in this column is a
property of one realisation, not of the method. ⚪ `T_chosen` is unaffected — entropy
wins on disagreement by pre-registration.

🔴 **`es`'s `T_chosen = 1.30` is the TOP of the pre-registered grid.** The entropy-matching
optimum may lie above it and the grid cannot see it. **The grid is not extended** — extending
it now, having seen the result, would be choosing the search space on the outcome. This caveat
travels with every `es` number in this project.

## 3. The two curves, per fold (primary sweep, one realisation, seed 42)

Both curves are reported for every fold, as the gate row requires. `dH` = generated token entropy
minus the real held-in validation entropy `H_real`; `at_home_mae_pp` = mean absolute error of the
144-slot at-home profile against the same real reference, in percentage points.

### `es` — `H_real` = 3.5880, validation n = 5520

| `T` | `H_gen` | `dH` | at-home MAE (pp) | ACT TVD (pp) | parseable | terminated | sums to 1440 | episodes/diary |
|---|---|---|---|---|---|---|---|---|
| **real** | 3.5880 | — | — | — | 1.000 | 1.000 | **1.000** | **28.38** |
| 0.50 | 2.8394 | -0.7486 | 10.694 | 27.696 | 1.000 | 0.262 | 0.060 | 103.86 |
| 0.60 | 2.8719 | -0.7161 | 9.157 | 19.982 | 1.000 | 0.500 | 0.080 | 83.43 |
| 0.70 ⬅ `T_fidelity` | 3.0826 | -0.5054 | 7.580 | 13.502 | 1.000 | 0.852 | 0.103 | 55.72 |
| 0.80 | 3.2777 | -0.3103 | 8.353 | 10.976 | 1.000 | 0.987 | 0.108 | 38.52 |
| 0.90 | 3.3716 | -0.2164 | 9.007 | 12.204 | 1.000 | 0.998 | 0.102 | 30.39 |
| 1.00 | 3.4718 | -0.1162 | 9.227 | 10.626 | 1.000 | 1.000 | 0.120 | 25.93 |
| 1.10 | 3.5058 | -0.0822 | 9.387 | 11.167 | 1.000 | 1.000 | 0.088 | 22.93 |
| 1.20 | 3.5345 | -0.0535 | 9.042 | 11.303 | 1.000 | 1.000 | 0.100 | 20.55 |
| 1.30 ⬅ **`T_chosen`** | 3.5892 | +0.0012 | 9.400 | 11.477 | 1.000 | 1.000 | 0.097 | 19.17 |

🔴 **The real reference row is MEASURED IN THIS RUN, on the same 600 prompts — not asserted**
**from the corpus.** It parses, terminates and **sums to 1440 in 100.0 % of diaries**; the
model at `T_chosen` manages **9.7 %**. `FINDING 67` therefore rests on a within-run
comparison against an identically-computed reference, which is the strongest form available
and closes the *"asserted from the corpus measurement, not from this run"* caveat carried by
the earlier entries in the impl doc.

🔴 **Non-termination at low temperature on this fold:** `T=0.50` terminates 26.2 %, `T=0.60` terminates 50.0 %, `T=0.70` terminates 85.2 %.
A diary that never emits its stop token is not a short diary, it is a failed one, and
`sum_1440_frac` collapses with it. Any fidelity statistic read at those temperatures is
read on a population that is mostly broken output — which is `FINDING 67`.

### `uk` — `H_real` = 3.4365, validation n = 5702

| `T` | `H_gen` | `dH` | at-home MAE (pp) | ACT TVD (pp) | parseable | terminated | sums to 1440 | episodes/diary |
|---|---|---|---|---|---|---|---|---|
| **real** | 3.4365 | — | — | — | 1.000 | 1.000 | **1.000** | **25.18** |
| 0.50 | 3.1924 | -0.2441 | 11.150 | 24.900 | 1.000 | 0.465 | 0.087 | 82.57 |
| 0.60 | 3.2326 | -0.2040 | 5.917 | 15.831 | 1.000 | 0.785 | 0.092 | 56.77 |
| 0.70 | 3.2825 | -0.1541 | 4.858 | 10.915 | 1.000 | 0.942 | 0.120 | 40.17 |
| 0.80 | 3.2706 | -0.1660 | 4.344 | 9.837 | 1.000 | 0.998 | 0.127 | 30.68 |
| 0.90 | 3.3506 | -0.0860 | 3.216 | 7.968 | 1.000 | 1.000 | 0.135 | 28.23 |
| 1.00 ⬅ `T_fidelity` | 3.3771 | -0.0595 | 2.566 | 6.752 | 1.000 | 1.000 | 0.092 | 25.88 |
| 1.10 ⬅ **`T_chosen`** | 3.4438 | +0.0072 | 3.277 | 7.182 | 1.000 | 1.000 | 0.085 | 23.99 |
| 1.20 | 3.4541 | +0.0176 | 4.830 | 7.865 | 1.000 | 1.000 | 0.077 | 21.84 |
| 1.30 | 3.5467 | +0.1102 | 7.033 | 10.126 | 1.000 | 1.000 | 0.062 | 20.12 |

🔴 **The real reference row is MEASURED IN THIS RUN, on the same 600 prompts — not asserted**
**from the corpus.** It parses, terminates and **sums to 1440 in 100.0 % of diaries**; the
model at `T_chosen` manages **8.5 %**. `FINDING 67` therefore rests on a within-run
comparison against an identically-computed reference, which is the strongest form available
and closes the *"asserted from the corpus measurement, not from this run"* caveat carried by
the earlier entries in the impl doc.

🔴 **Non-termination at low temperature on this fold:** `T=0.50` terminates 46.5 %, `T=0.60` terminates 78.5 %, `T=0.70` terminates 94.2 %.
A diary that never emits its stop token is not a short diary, it is a failed one, and
`sum_1440_frac` collapses with it. Any fidelity statistic read at those temperatures is
read on a population that is mostly broken output — which is `FINDING 67`.

### `it` — `H_real` = 3.5207, validation n = 3434

| `T` | `H_gen` | `dH` | at-home MAE (pp) | ACT TVD (pp) | parseable | terminated | sums to 1440 | episodes/diary |
|---|---|---|---|---|---|---|---|---|
| **real** | 3.5207 | — | — | — | 1.000 | 1.000 | **1.000** | **28.62** |
| 0.50 | 2.3753 | -1.1454 | 8.083 | 26.712 | 1.000 | 0.637 | 0.078 | 74.82 |
| 0.60 | 2.4856 | -1.0350 | 7.685 | 21.918 | 1.000 | 0.743 | 0.050 | 66.64 |
| 0.70 | 2.6290 | -0.8916 | 5.116 | 17.611 | 1.000 | 0.888 | 0.050 | 55.27 |
| 0.80 ⬅ `T_fidelity` | 2.8902 | -0.6304 | 3.933 | 13.139 | 1.000 | 0.967 | 0.100 | 42.69 |
| 0.90 | 3.1472 | -0.3735 | 4.397 | 10.024 | 1.000 | 1.000 | 0.067 | 32.97 |
| 1.00 | 3.3097 | -0.2110 | 6.344 | 8.743 | 1.000 | 1.000 | 0.072 | 27.57 |
| 1.10 | 3.4276 | -0.0931 | 10.759 | 9.333 | 1.000 | 1.000 | 0.063 | 23.79 |
| 1.20 ⬅ **`T_chosen`** | 3.5258 | +0.0052 | 13.124 | 10.743 | 1.000 | 1.000 | 0.062 | 21.86 |
| 1.30 | 3.5911 | +0.0704 | 16.889 | 12.890 | 1.000 | 0.998 | 0.068 | 19.83 |

🔴 **The real reference row is MEASURED IN THIS RUN, on the same 600 prompts — not asserted**
**from the corpus.** It parses, terminates and **sums to 1440 in 100.0 % of diaries**; the
model at `T_chosen` manages **6.2 %**. `FINDING 67` therefore rests on a within-run
comparison against an identically-computed reference, which is the strongest form available
and closes the *"asserted from the corpus measurement, not from this run"* caveat carried by
the earlier entries in the impl doc.

🔴 **Non-termination at low temperature on this fold:** `T=0.50` terminates 63.7 %, `T=0.60` terminates 74.3 %, `T=0.70` terminates 88.8 %.
A diary that never emits its stop token is not a short diary, it is a failed one, and
`sum_1440_frac` collapses with it. Any fidelity statistic read at those temperatures is
read on a population that is mostly broken output — which is `FINDING 67`.

## 4. The sensitivity trap (`D-S5-13`(a)) — 5 seeds × 3 levels

The val doc registered the trap: *the step-to-step difference along the curve must exceed the
spread from re-running one level*, **else the deliverable is the BAND, not a value**. Each fold's
window is the three grid points around its own `T_chosen`.

| fold | window | seeds | job | md5 |
|---|---|---|---|---|
| `es` | 1.10, 1.20, 1.30 | 101–105 | `1285712` | `6d14b493b03fd37b8af917338f7d6776` |
| `uk` | 1.00, 1.10, 1.20 | 101–105 | `1285713` | `62f17f9f580b495d6bf8e86bd8a0b38b` |
| `it` | 1.10, 1.20, 1.30 | 101–105 | `1285714` | `eeb1fe2e9dc6fdd273d770e1fcf11e0b` |

**Verdict per statistic.** `step` = max difference between adjacent grid points;
`noise` = max range over the five re-runs of a single level.

| statistic | `es` step | `es` noise | `es` | `uk` step | `uk` noise | `uk` | `it` step | `it` noise | `it` |
|---|---|---|---|---|---|---|---|---|---|
| `H_gen` | 0.0584 | 0.0318 | 🟢 step > noise | 0.0705 | 0.0581 | 🟢 step > noise | 0.0888 | 0.0594 | 🟢 step > noise |
| `dH` | 0.0584 | 0.0318 | 🟢 step > noise | 0.0705 | 0.0581 | 🟢 step > noise | 0.0888 | 0.0594 | 🟢 step > noise |
| `at_home_mae_pp` | 0.9315 | 1.8127 | 🔴 **NOISE DOMINATES** | 1.3994 | 1.4072 | 🔴 **NOISE DOMINATES** | 4.1114 | 3.1993 | 🟢 step > noise |
| `at_home_mae_pp_covered` | 0.6631 | 1.7613 | 🔴 **NOISE DOMINATES** | 1.3684 | 1.4759 | 🔴 **NOISE DOMINATES** | 4.2130 | 3.2276 | 🟢 step > noise |
| `act_tvd_pp` | 0.2890 | 1.8034 | 🔴 **NOISE DOMINATES** | 0.8391 | 1.2828 | 🔴 **NOISE DOMINATES** | 1.4613 | 2.2365 | 🔴 **NOISE DOMINATES** |
| `sum_1440_frac` | 0.0057 | 0.0283 | 🔴 **NOISE DOMINATES** | 0.0193 | 0.0367 | 🔴 **NOISE DOMINATES** | 0.0040 | 0.0183 | 🔴 **NOISE DOMINATES** |
| `terminated_frac` | 0.0003 | 0.0017 | 🔴 **NOISE DOMINATES** | 0.0007 | 0.0033 | 🔴 **NOISE DOMINATES** | 0.0013 | 0.0050 | 🔴 **NOISE DOMINATES** |

🔴 **The split is not cosmetic: it separates the statistic the choice was MADE on from the ones it
was not.** `T_chosen` rests on entropy matching, and `dH` clears the trap on every fold that has
landed. Statistics that carry no part of the decision are noise-dominated in places.

## 5. The test the spread block does not run: does the SELECTION move?

*Step exceeds noise* compares magnitudes. The question that decides whether a number is a result
is whether **a different seed would have produced a different decision**. Each selection rule is
re-applied independently inside each of the five realisations.

| fold | rule | s101 | s102 | s103 | s104 | s105 | verdict |
|---|---|---|---|---|---|---|---|
| `es` | argmin abs(`dH`) — **the choice** | 1.30 | 1.30 | 1.30 | 1.30 | 1.30 | 🟢 **STABLE 5/5** |
| `es` | argmin `at_home_mae_pp` | 1.20 | 1.10 | 1.20 | 1.10 | 1.10 | 🔴 **MOVES** — 1.10, 1.20 |
| `es` | argmin `at_home_mae_pp_covered` | 1.20 | 1.20 | 1.20 | 1.20 | 1.10 | 🔴 **MOVES** — 1.10, 1.20 |
| `uk` | argmin abs(`dH`) — **the choice** | 1.10 | 1.10 | 1.10 | 1.10 | 1.10 | 🟢 **STABLE 5/5** |
| `uk` | argmin `at_home_mae_pp` | 1.00 | 1.10 | 1.00 | 1.10 | 1.00 | 🔴 **MOVES** — 1.00, 1.10 |
| `uk` | argmin `at_home_mae_pp_covered` | 1.00 | 1.10 | 1.00 | 1.10 | 1.00 | 🔴 **MOVES** — 1.00, 1.10 |
| `it` | argmin abs(`dH`) — **the choice** | 1.20 | 1.20 | 1.20 | 1.20 | 1.20 | 🟢 **STABLE 5/5** |
| `it` | argmin `at_home_mae_pp` | 1.10 | 1.10 | 1.10 | 1.10 | 1.10 | 🟢 **STABLE 5/5** |
| `it` | argmin `at_home_mae_pp_covered` | 1.10 | 1.10 | 1.10 | 1.10 | 1.10 | 🟢 **STABLE 5/5** |

🟢 **`T_chosen` is a seed-independent decision.** Five independent realisations of 600 diaries
each pick the same temperature every time. That is a stronger statement than the spread block's,
and it is the one that licenses reporting `T_chosen` as a value.

🔴 **The fidelity argmin is NOT stable, on two folds of three.** On `uk` it lands on 1.00 in three
realisations and 1.10 in two; on `es` it lands on 1.20 in two and 1.10 in three. **Both fold’s
fidelity results are BANDS** — `{1.00, 1.10}` on `uk`, `{1.10, 1.20}` on `es` — and neither may be
written as a single value.

⚪ **One asymmetry, stated rather than glossed.** `uk` and `it` choose an **interior** point of
their replicate window, so their argmin had two directions it could have moved in and moved in
neither. `es` chooses `1.30`, the **top of its window and of the whole grid**, so its argmin could
only have moved inward: stability is a **one-sided** test there and is correspondingly weaker
evidence than on the other two folds.

🔴 **The argmins in this table are IN-WINDOW argmins and must not be quoted as the
fidelity temperature.** On `es` and `it` the ruled `T_fidelity` lies **outside** the three-point
replicate window entirely, so for those folds the table shows the minimum of a truncated curve.
The coverage-101 points (`D-S5-15`(a)) have since landed and §6.3 settles the question on the
**full nine-point grid**: the fidelity argmin moves by one grid step on **all three folds** when
only the generation seed changes — 
`es` 0.70 → 0.60, `uk` 1.00 → 0.90, `it` 0.80 → 0.90. ⚪ Read §6.3, not this table, for the fidelity result.

## 5b. 🔴 The 1440-minute budget error is TWO-SIDED (`FINDING 75`)

`sum_1440_frac` says how often a diary lands **exactly** on the day budget. It does not say which
way it misses, and the two directions are handled by different code paths in the profiler and
produce different distortions. Recounted directly from the persisted generations:

| fold | `T` | n | exactly 1440 | **UNDER** | **OVER** | median abs. dev. |
|---|---|---|---|---|---|---|
| `es` | 1.10 | 2984 | 7.91 % | 39.61 % | 🔴 **52.48 %** | 30 min |
| `es` | 1.20 | 2966 | 7.75 % | 42.01 % | 🔴 **50.24 %** | 40 min |
| `es` | 1.30 ⬅ `T_chosen` | 2953 | 7.18 % | 44.12 % | 🔴 **48.70 %** | 40 min |
| `uk` | 1.00 | 2986 | 10.38 % | 28.57 % | 🔴 **61.05 %** | 30 min |
| `uk` | 1.10 ⬅ `T_chosen` | 2978 | 10.21 % | 24.28 % | 🔴 **65.51 %** | 30 min |
| `uk` | 1.20 | 2949 | 8.41 % | 23.23 % | 🔴 **68.36 %** | 40 min |
| `it` | 1.10 | 2974 | 6.42 % | 46.47 % | 🔴 **47.11 %** | 50 min |
| `it` | 1.20 ⬅ `T_chosen` | 2954 | 6.13 % | 44.55 % | 🔴 **49.32 %** | 50 min |
| `it` | 1.30 | 2917 | 5.83 % | 39.80 % | 🔴 **54.37 %** | 50 min |

🔴 **The bias is not one-sided, and on `uk` it runs OPPOSITE to what our own record said.** At
`T_chosen` the majority of `uk` diaries **overshoot**. `at_home_profile()` clamps with
`min(slot + n, 144)` and sets `covered = min(slot, 144)`, so:

- **UNDER 1440** — the profiler stops early and the untouched tail keeps its `0`, i.e. a missing
  tail is scored as *away from home*. 🟢 This is `FINDING 67`, and `D-S5-14`(a)'s covered basis
  removes exactly it.
- **OVER 1440** — the excess minutes are **silently discarded** and the diary reports **full**
  coverage. 🔴 No phantom tail, and **the covered basis cannot see it**, because by its own
  denominator such a diary is complete.

⚪ **The covered-basis remedy is correct and is not weakened** — but it addresses the *minority*
of diaries on `uk`, and there is a second distortion it does not address at all.

🔴 **`sum_1440_frac ≈ 0.06` must not be read as "the day is barely filled".** Median total
minutes is **1,460** on `uk` and **1,440** on `it`; median absolute deviation is **30** and
**50** minutes — 2 % and 3.5 % of a day; aggregate day-fill is **101.6 %** and **100.4 %**. The
budget error is **small and roughly centred**. What the model almost never does is land
*exactly* on 1440.

⚪ **Cross-checked, not merely re-parsed.** Counting diaries that reach slot 143 from this
recount reproduces the artefacts' own `coverage_last_slot_frac` row by row across all
realisations, worst absolute disagreement **0.0253**, typically 0.002–0.010, and **always
positive** — as predicted, since the artefact counts only diaries surviving
`transcoder.parse_episodes`, which drops malformed trailing episodes. The gap grows with `T`
exactly as that explanation requires.

🟢 **Step 7 does NOT inherit a design gap — the grammar is ALREADY TWO-SIDED BY CONSTRUCTION,**
**checked in the code rather than assumed.** `tally_automaton()` (`tools/4thJ_step7_grammar.py:169`)
has 145 states and a **single** accepting state `{144}`; `tally_step` returns `None` whenever
`state + dur/10 > 144`. Run directly: `tally_step(143, 10) → 144` (accept), `tally_step(144, 10)`
`→ None`, `tally_step(140, 60) → None`, and from state 140 the only legal durations are
**10–40 min**. Overshoot has no transition; undershoot never reaches the accepting state.

🔴 **What this section supplies is the MAGNITUDE of the work that mask does.** Unmasked, 90–94 %
of generated diaries miss the budget and **the majority miss it by OVERSHOOTING**, so the
constraint the mask most often has to enforce is the **upper** one — the opposite of what a
"pad the short tail" reading of `FINDING 67` would predict. ⚪ `G7.10` (the XGrammar back-end
that would apply the mask during decoding) has **still never been run**, so the grammar is a
specification plus a hand-written oracle, not something demonstrated inside the generation loop.

### Episodes per diary against the real reference

| fold | real (measured in the same run) | at `T_chosen` | ratio |
|---|---|---|---|
| `es` | 28.38 | 19.17 | **0.68×** |
| `uk` | 25.18 | 23.99 | **0.95×** |
| `it` | 28.62 | 21.86 | **0.76×** |

🔴 **The deficit is country-correlated, in the LOCO-dangerous shape** — the same shape as
`FINDING 53` and `FINDING 72`: `uk` nearly right, `es` and `it` badly short. Read together with
the totals above the reading is **fewer, longer episodes filling the same day**, not a shorter
day. ⚪ Reported, not thresholded — and a Step 6 input, since `G6.8` scores transitions per day
and dwell-time distributions, both of which this moves on two folds of three.

## 6. 🟢 The `D-S5-15`(a) SPLICE — LANDED, and the nine-point covered curve EXISTS

The covered-basis statistic `at_home_mae_pp_covered` (`D-S5-14`(a)) exists only in replicate-mode
rows, so the primary sweep carries none. The replicate windows cover **3** of the 9 grid points.
Rather than re-run all nine, the author ruled that the **six missing points** be run at seed `101`
only and **spliced** with the seed-`101` rows of the replicate artefact.

| fold | already at seed 101 (replicates) | added by coverage-101 | job | landed? | md5 of the coverage artefact |
|---|---|---|---|---|---|
| `es` | 1.10, 1.20, 1.30 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.00 | `1285777` | 🟢 **yes** | `61b7c47782b7ea267591de163ef119b3` |
| `uk` | 1.00, 1.10, 1.20 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.30 | `1285778` | 🟢 **yes** | `d991683f718c81d6ebbcf98476712808` |
| `it` | 1.10, 1.20, 1.30 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.00 | `1285779` | 🟢 **yes** | `325d6653d5b30b68ec12d77619632112` |

🔴 **The splice is declared, not silent.** The nine-point covered curve is assembled from
**two jobs**, not one. It is legal because every replicate-mode row records its own `gen_seed`, so
the assembled curve is a **single-seed** curve and not a mixture of realisations. Both jobs hold
the prompt seed, prompt set, sampling configuration, base revision and adapter identical —
verified, not assumed: `real_structural` and `H_real` are **byte-identical** between the primary
and coverage artefacts on all three folds, so the reference side of every comparison is the same
object.

### 6.1 The spliced nine-point curves (all at generation seed `101`)

**`es` (Spain)** — 9 of 9 points, 🟢 complete

| `T` | source job | `parseable_frac` | usable | `at_home_mae_pp` | `at_home_mae_pp_covered` | `coverage_last_slot_frac` | \|`dH`\| |
|---|---|---|---|---|---|---|---|
| **0.50** | coverage-101 | 1.0000 | yes | 10.2269 | 9.7157 | 0.8683 | 0.7312 |
| **0.60** | coverage-101 | 1.0000 | yes | 7.4398 | 6.9253 | 0.8133 | 0.5711 |
| **0.70** | coverage-101 | 1.0000 | yes | 7.9062 | 7.3501 | 0.7533 | 0.4344 |
| **0.80** | coverage-101 | 1.0000 | yes | 8.4444 | 8.0863 | 0.6817 | 0.3058 |
| **0.90** | coverage-101 | 1.0000 | yes | 9.2676 | 8.8202 | 0.6327 | 0.2413 |
| **1.00** | coverage-101 | 1.0000 | yes | 8.5865 | 7.9464 | 0.6286 | 0.1271 |
| **1.10** | replicates | 1.0000 | yes | 9.2001 | 8.4096 | 0.6007 | 0.0990 |
| **1.20** | replicates | 1.0000 | yes | 8.1105 | 7.2564 | 0.5753 | 0.0383 |
| **1.30** | replicates | 1.0000 | yes | 9.2691 | 7.5578 | 0.5436 | 0.0251 |

**`uk` (United Kingdom)** — 9 of 9 points, 🟢 complete

| `T` | source job | `parseable_frac` | usable | `at_home_mae_pp` | `at_home_mae_pp_covered` | `coverage_last_slot_frac` | \|`dH`\| |
|---|---|---|---|---|---|---|---|
| **0.50** | coverage-101 | 1.0000 | yes | 9.9479 | 8.6392 | 0.6550 | 0.3282 |
| **0.60** | coverage-101 | 1.0000 | yes | 5.7569 | 4.8402 | 0.6050 | 0.1598 |
| **0.70** | coverage-101 | 1.0000 | yes | 4.6642 | 3.9998 | 0.6694 | 0.1661 |
| **0.80** | coverage-101 | 1.0000 | yes | 3.2755 | 2.7632 | 0.6733 | 0.1033 |
| **0.90** | coverage-101 | 1.0000 | yes | 2.2454 | 1.8960 | 0.7433 | 0.0798 |
| **1.00** | replicates | 1.0000 | yes | 2.2891 | 1.7551 | 0.7145 | 0.0337 |
| **1.10** | replicates | 1.0000 | yes | 3.4198 | 2.9732 | 0.7647 | 0.0069 |
| **1.20** | replicates | 1.0000 | yes | 5.3884 | 4.7874 | 0.7222 | 0.0844 |
| **1.30** | coverage-101 | 1.0000 | yes | 7.0976 | 6.3866 | 0.7560 | 0.1622 |

**`it` (Italy)** — 9 of 9 points, 🟢 complete

| `T` | source job | `parseable_frac` | usable | `at_home_mae_pp` | `at_home_mae_pp_covered` | `coverage_last_slot_frac` | \|`dH`\| |
|---|---|---|---|---|---|---|---|
| **0.50** | coverage-101 | 1.0000 | yes | 9.2917 | 7.5033 | 0.5800 | 1.0594 |
| **0.60** | coverage-101 | 1.0000 | yes | 7.2859 | 5.7141 | 0.5833 | 1.0515 |
| **0.70** | coverage-101 | 1.0000 | yes | 6.0614 | 4.4255 | 0.5409 | 0.9621 |
| **0.80** | coverage-101 | 1.0000 | yes | 5.1746 | 3.6076 | 0.5209 | 0.7877 |
| **0.90** | coverage-101 | 1.0000 | yes | 5.0590 | 3.5132 | 0.4925 | 0.4621 |
| **1.00** | coverage-101 | 1.0000 | yes | 6.9309 | 5.2758 | 0.4950 | 0.2286 |
| **1.10** | replicates | 1.0000 | yes | 8.3694 | 6.9409 | 0.5334 | 0.1248 |
| **1.20** | replicates | 1.0000 | yes | 11.3462 | 10.0651 | 0.5370 | 0.0259 |
| **1.30** | replicates | 0.9983 | yes | 14.3799 | 13.0812 | 0.5932 | 0.0573 |

### 6.2 ⚪ `fidelity_argmin_moved_under_D_S5_14` — derived OFFLINE

The engine emits this flag only in the **non**-replicate branch, so it is derived here from the
spliced rows: the fidelity argmin is taken over the usable points of the nine-point curve on each
basis and the two are compared.

| fold | argmin on `at_home_mae_pp` | argmin on `at_home_mae_pp_covered` | **moved?** | gap to the runner-up on the uncovered basis | re-run spread (`G5.8`) |
|---|---|---|---|---|---|
| `es` | **0.60** (7.4398) | **0.60** (6.9253) | ⚪ no | 0.4664 pp | 1.8127 pp |
| `uk` | **0.90** (2.2454) | **1.00** (1.7551) | 🔴 **YES** | 0.0437 pp | 1.4072 pp |
| `it` | **0.90** (5.0590) | **0.90** (3.5132) | ⚪ no | 0.1156 pp | 3.1993 pp |

🔴 **The flag fires on `uk` and nowhere else.** Removing the phantom tail moves the
fidelity argmin by one grid step — which is exactly the effect `D-S5-14`(a) was registered to
detect, so the remedy is doing work. ⚪ **But read the magnitude before reading the flag:** on
`uk` the two competing minima are **0.0437 pp** apart on the uncovered basis against a
re-run spread of **1.4072 pp** — a factor of **32**.
The argmin moved because the curve is *flat* there, not because the basis change is
decisive. That is `D-S5-16`'s point restated on a second, independent statistic.

### 6.3 🔴 What the splice bought that was not asked for: an INDEPENDENT noise estimate

The six coverage-101 points are a **second realisation** of six grid points the primary sweep
already measured at generation seed `42`. Nobody designed them as a replicate — but that is what
they are, and they sit at **six grid points the replicate window never reaches**. Comparing the
two realisations point by point gives a re-run spread estimate that is **not** derived from the
same three temperatures `G5.8` scores.

| fold | mean \|diff\| over the 6 shared points | max \|diff\| | at `T` | mean signed diff | `G5.8` step | `G5.8` spread |
|---|---|---|---|---|---|---|
| `es` | 0.5840 pp | 1.7176 pp | 0.60 | -0.3579 pp | 0.9315 | 1.8127 |
| `uk` | 0.6100 pp | 1.2025 pp | 0.50 | -0.5883 pp | 1.3994 | 1.4072 |
| `it` | 0.8407 pp | 1.2418 pp | 0.80 | +0.7076 pp | 4.1114 | 3.1993 |

🔴 **This corroborates the `G5.8` failures from outside the window that produced them.** On
`es` the `G5.8` step is **0.9315 pp**; two independent realisations of six *other* grid points
disagree by up to **1.7176 pp** and by **0.5840 pp** on average. The step the gate is asked to
call meaningful is smaller than the disagreement between two runs of the same configuration at
neighbouring temperatures. ⚪ The same holds on `uk` (step 1.3994 vs max disagreement 1.2025)
and is comfortably cleared on `it` (step 4.1114 vs 1.2418).

🔴 **And the fidelity argmin moves under a SEED change on all three folds, over the full
nine-point grid.** Primary sweep at seed `42` → spliced curve at seed `101`: `es` **0.70 →
0.60**, `uk` **1.00 → 0.90**, `it` **0.80 → 0.90**. Every fold moves by exactly one grid step;
two move down and one up, so there is no systematic direction. ⚪ This is a stronger statement
than the replicate spread block makes, because the earlier `es` band `{1.10, 1.20}` and `uk` band
`{1.00, 1.10}` were argmins taken **inside the three-point replicate window** — a local minimum
of a truncated curve. These are argmins over the **whole grid**. 🔴 **Never quote the
window argmin as the fidelity temperature; quote these.**

⚪ **The confound, stated rather than glossed.** The primary sweep and the
replicate/coverage jobs are different invocations of the engine, and **no cell shares both `T` and
`gen_seed`**, so a seed change and an engine change cannot be separated by an exact-reproduction
test. Two things bound it: the reference side (`H_real`, `real_structural`) is byte-identical, so
any difference must live on the generated side; and the per-fold **mean signed** difference has
inconsistent signs (`es` −0.3579, `uk` −0.5884, `it` **+0.7076**), which is what sampling noise
looks like and not what a systematic engine change looks like. That is evidence, not proof.

### 6.4 🟢 The entropy argmin over the full grid at a seed that chose nothing

The spliced curve permits the check the replicate block could not run: `argmin |dH|` over **all
nine** grid points at a generation seed that played no part in the selection.

| fold | `T_chosen` (primary, seed 42) | argmin \|`dH`\| on the spliced seed-101 curve | agree? | \|`dH`\| at that point |
|---|---|---|---|---|
| `es` | **1.30** | **1.30** | 🟢 **yes** | 0.0251 |
| `uk` | **1.10** | **1.10** | 🟢 **yes** | 0.0069 |
| `it` | **1.20** | **1.20** | 🟢 **yes** | 0.0259 |

🟢 **Three folds for three.** `T_chosen` is reproduced exactly by an independent
realisation over the entire grid — not merely inside a three-point window. Combined with the
5/5 per-seed stability in §5, the entropy-matched choice is the one quantity in Step 5 that has
survived every attempt made to move it.

⚪ **The `es` asymmetry survives too and must still be stated.** `es` chooses **1.30, the top of
the grid**; its argmin can only move inward, so stability there is a **one-sided** test. `uk`
(1.10) and `it` (1.20) choose interior points and had two directions available. `endpoint_entropy
= True` on `es` belongs in the same sentence as its stability claim.

### 6.5 🔴 `FINDING 76` — `uk`’s `agree = True` DOES NOT SURVIVE A SEED CHANGE

`agree` asks whether the entropy-matched and fidelity-matched temperatures land within
`agree_tol` of one another. It is `True` on **exactly one** fold of three, and that one `True` is
the only evidence anywhere in Step 5 that the two criteria ever point the same way.

| fold | `T_chosen` | `T_fidelity` at seed 42 | gap | `agree` as recorded | `T_fidelity` at seed 101 | gap | `agree` under seed 101 |
|---|---|---|---|---|---|---|---|
| `es` | 1.30 | 0.70 | 0.6000 | ⚪ False | 0.60 | 0.7000 | 🔴 **False** |
| `uk` | 1.10 | 1.00 | 0.1000 | 🟢 **True** | 0.90 | 0.2000 | 🔴 **False** |
| `it` | 1.20 | 0.80 | 0.4000 | ⚪ False | 0.90 | 0.3000 | 🔴 **False** |

🔴 **The single `True` on the board flips to `False` under nothing but a different
generation seed.** `uk`’s recorded agreement rests on a gap of exactly `0.1000` against
`agree_tol = 0.1001` — a margin of `0.0001`, one ten-thousandth. Re-running the same
configuration at seed `101` moves the fidelity argmin one grid step further away, the gap becomes
`0.2000`, and the criteria no longer agree at all. The other two folds disagree under both seeds.

🟢 **`T_chosen` is unaffected, and that is by pre-registration, not by luck.**
`4thJ_step5_temperature.py:607` fixes that **entropy wins on disagreement**; `uk` would have
selected `1.10` whether `agree` read `True` or `False`. Nothing about the chosen temperature moves.

🔴 **What must change is the CLAIM.** “On the UK fold the entropy and fidelity
criteria agree” is not a property of the method — it is a property of one realisation,
and it does not replicate. It must never be written as corroboration that the two criteria
converge. ⚪ This is the third independent measurement pointing the same way (`FINDING 74`
the trap, `§6.3` the argmin walk, this): **the fidelity curve carries no seed-stable
signal on `es` or `uk`,** which is precisely what `G5.8` reports and what `D-S5-16`(a), **ruled
by the author on 2026-08-22**, lets stand.

## 7. The frozen generation configuration

| fold | `temperature` | `top_p` | `top_k` | `max_new_tokens` | md5 of config |
|---|---|---|---|---|---|
| `es` | **1.30** | 1.0 | 0 | 1200 | `b9ed52d112892372cc302724ef56c724` |
| `uk` | **1.10** | 1.0 | 0 | 1200 | `800f131b0816ff23fd23459c2b288d9c` |
| `it` | **1.20** | 1.0 | 0 | 1200 | `af4dc33a332abe51fe4f4a34a93d0d08` |

Common to all three: `do_sample = true`, base `allenai/OLMo-2-0425-1B` @
`a1847dff35000b4271fa70afc5db10fd29fedbdf`, per-fold LoRA adapter, prompt seed 42.

🔴 **`top_p = 1.0` and `top_k = 0` together mean the sampling distribution is not truncated at
all** — temperature is the only sampling control. `G5.9`'s antecedent (*"if top-p is used at
all"*) is therefore false and the gate is vacuously satisfied. See `FINDING 69`, ruled 2026-08-21:
the registered text read `p ≤ 0.98`, which in nucleus sampling admits `p = 0.5` and rejects
`p = 1.0` — the opposite of a gate named *no truncation creep*. The ruled reading is **`p ≥ 0.98`**,
a declared post-registration erratum.

## 8. What the gates read, and the two folds that fail

`tools/4thJ_gates_step5.py`, baseline, all three folds: **34 PASS, 2 FAIL, 0 BLOCKED**, coverage
clause clean, shipped populations md5-unchanged before and after.

- 🟢 **`G5.9` PASSES on all three folds and its registered perturbation (`top_p = 0.9`) fells it
  on all three.** Under the superseded as-written reading this was impossible in both directions.
- 🟢 **`G5.8` PASSES on `it`** — both curves and the agreement statement reported, and
  `5 seeds × 3 levels` with `step 4.1114 > re-run spread 3.1993`. Its perturbation (*report only
  the fidelity curve*) fells it, so the gate is demonstrated capable of failing.
- 🔴 **`G5.8` FAILS on `es` and on `uk`** — the sensitivity clause, on `at_home_mae_pp`:

| fold | step | re-run spread | ratio | verdict |
|---|---|---|---|---|
| `es` | 0.9315 | **1.8127** | **0.51×** | 🔴 **FAIL — decisively noise-dominated** |
| `uk` | 1.3994 | **1.4072** | **0.99×** | 🔴 **FAIL — marginal** |
| `it` | 4.1114 | 3.1993 | 1.29× | 🟢 PASS |

**Both failures are left standing.** They are the trap we registered catching our own curves.

### 🟢 `D-S5-16` — RULED **(a)** BY THE AUTHOR, 2026-08-22. THE TWO FAILS ARE THE TERMINAL VERDICT

The registered clause says the step must exceed the spread *"else the deliverable is the BAND,
not a value"*, which can be read as a **remedy** as well as a **failure condition**; the checker
implements only the second. Both readings were defensible and they gave different verdicts on
`es` and `uk`. 🔴 **The assistant did not resolve it, deliberately** — the ambiguity surfaced by
running the gate and watching it fail, so amending the checker in the direction that clears the
board would have been selecting the test on the outcome, and the file order is checkable.

**The author ruled (a): `G5.8` stands exactly as written. `es` and `uk` FAIL, permanently and in
the paper.** The checker is not amended, no fold is re-run, and no temperature is re-tuned. The
fidelity result is delivered as a **band** per fold — `es` {0.60, 0.70}, `uk` {0.90, 1.00},
`it` {0.80, 0.90} — with the FAIL reported as the reason it is a band and not a value. Options,
the three post-draft measurements that supported the ruling, and the ruling itself:
`IMP/docs/2026-08-22_questions-for-the-author.md` and
`Step5_docs/impl/2026-08-21_item5.4-temperature.md`.

⚪ Whatever is ruled, **`T_chosen` does not move**: it rests on entropy matching, which clears the
trap on **all three** folds and whose argmin is stable across all five seeds on all three.
`D-S5-16` decides how a **reporting** gate is scored, not what temperature we generate at.

## 9. Declared limitations

1. 🔴 **`es`: `T_chosen` is the grid endpoint.** The optimum may lie above 1.30, unseen. The grid
   is pre-registered and is not extended.
2. 🔴 **The fidelity temperature is a BAND on all three folds, not a value.** Over the
   full nine-point grid the argmin moves by one grid step under a seed change alone: `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}.
   🔴 `G5.8` fails on `es` and `uk` for exactly this reason. ⚪ **The earlier
   in-window bands (§5) are NOT this quantity** — they are argmins of a truncated
   three-point curve. Quote §6.3.
3. 🔴 **`uk`: `agree = True` rests on a `1e-4` margin AND DOES NOT REPLICATE.** Report
   it as agreement *to within one grid step*, and never as evidence that the two criteria
   converge — at seed 101 it reads `False` (`FINDING 76`, §6.5).
4. ⚪ **The covered-basis curve is spliced from two jobs** at one seed — declared in §6.
5. 🟢 **`es` and `it` fidelity optima sit outside the replicate window** — that gap
   is now closed: the coverage-101 points landed and §6 carries the full nine-point curve at
   generation seed 101 for all three folds.
6. ⚪ **One realisation is 600 diaries.** Every statistic here is a sample statistic and the
   replicate spread in §4 is the honest measure of its precision.

---

*Generated from the artefacts in this directory. Do not edit by hand — regenerate.*
