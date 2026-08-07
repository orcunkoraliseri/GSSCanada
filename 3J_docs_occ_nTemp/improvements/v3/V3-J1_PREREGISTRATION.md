# V3-J1 — pre-registration: the person-level retail gate

**Written 2026-08-06, before a single agreement statistic was computed.** Everything below —
statistic, null, bands, arms and predictions — is fixed at this point. 🔴 **If a result disagrees
with a band, the result is recorded and the band is not moved.** That is the whole reason this file
exists and is dated.

---

## 0. What I looked at BEFORE writing this, and what I did not

**Looked at (structure and code only):**

- the pool's column families and row structure — `occID`, `CYCLE_YEAR`, `DDAY_STRATA`,
  `IS_SYNTHETIC`, `ret30_001..048`, 192,183 rows;
- the row grid: **64,061 persons × 3 day-type strata**, exactly **one** row per person with
  `IS_SYNTHETIC=0` and **two** with `=1`;
- the marginal sparsity: observed **28.53 %** of rows have any retail (mean 0.935 slots),
  synthetic **20.45 %** (mean 1.009 slots);
- `3rdJ_04E_inference_4split.py:347` — generation for person *i* is conditioned on **that person's
  own** `act_seq[i]` and `aux_seq[i]`, and `aux_seq[:,2]` **is the observed AT_RETAIL vector**.

**Did not look at:** any agreement, overlap, correlation or null statistic. None has been computed.

🔴 **Two structural facts change the design and are recorded before they can be rationalised:**

1. **A same-day-type comparison is impossible by construction.** A person's observed row carries
   their real diary day; their two synthetic rows are the *other two* strata. So the gate compares a
   generated day of one type against an observed day of another. **A perfect model would not
   reproduce the observed vector**, which is exactly why the bar has to be a shuffle null and not a
   fixed distance.
2. **The model is given the person's own observed retail vector as encoder input.** So this gate
   asks a sharp question with a real possibility of a bad answer: *does the generator retain the
   person-level information it is handed?*

---

## 1. The statistic

For every synthetic row *s* belonging to person *p*, its partner is *p*'s own observed row *o*.
**128,122 pairs.** Both vectors are binary, length 48.

**J1a — participation (the headline).** Does the model know *who* shops?

```
lift_a = P(syn has any retail | obs has any retail) / E_null[same] - 1
```

**J1b — timing.** Among pairs where **both** sides have retail, does it know *when*?

```
lift_b = mean |s ∩ o| / E_null[mean |s ∩ o|] - 1        (intersection of active slots)
```

Both are **null-relative**, so neither can be inflated by the sample size. Both are reported with a
z-score against the permutation spread.

## 2. The null

**Permute the person assignment within a cell, nothing else.**

```
cell = (CYCLE_YEAR, PR, DDAY_STRATA of the synthetic row, DDAY_STRATA of the person's observed row)
```

🔴 **The last term is the one that matters and it is not decoration.** A true pair always has
observed strata ≠ synthetic strata. If the null were taken over the first three terms only, some
shuffled partners would have *matching* strata and could agree more for a reason that has nothing to
do with person identity — the null would be measuring day type. This is the lesson V2-E1 paid for:
*a perturbation that changes more than one thing cannot attribute what it breaks.*

**R = 200 permutations.** Cells with fewer than 2 distinct persons cannot be permuted: they are
**excluded and counted in the output**, never silently dropped.

**Secondary null (INFO, not scored):** the same permutation restricted further to
`AGEGRP × SEX × LFTAG`. It separates *person identity* from *demographics*: if the lift survives the
tighter null, the model retains information about the individual rather than about their stratum.

## 3. Bands — fixed now

| | J1a and J1b |
|---|---|
| **PASS** | `lift ≥ 0.10` **and** `z ≥ 5` |
| **WARN** | `lift ≥ 0.02` (or `lift ≥ 0.10` with `z < 5`) |
| **FAIL** | `lift < 0.02` |

**Why 0.10.** Under the null hypothesis this gate exists to test — *the generator retains no
person-level retail information* — the lift is **0**. The bar is therefore not a tolerance around a
reference value but a minimum detectable retention: *a person's generated day must be at least 10 %
more likely to resemble their own observed day than a random same-cell stranger's.* Given that the
model is **handed** the observed vector, 10 % is a low bar deliberately — a gate this permissive
that still fails would be reporting something serious.

**Why `z ≥ 5` is required for PASS but not for WARN.** With 128,122 pairs a trivial lift can be
statistically certain; and a large lift with an unstable null is not evidence either. PASS needs
both. **The z requirement can only ever downgrade a verdict, never upgrade one.**

## 4. Arms — the gate must be seen failing, and seen passing

| arm | what it does | required verdict |
|---|---|---|
| **F0 control** | the shipped pool, unmodified | *no requirement* — this is the measurement, and it is allowed to fail |
| **F1 shuffle** | permute synthetic retail vectors within the null cell | 🔴 **FAIL**, `lift ≈ 0` |
| **F2 zero** | all synthetic retail set to 0 | 🔴 **FAIL**, and **must not crash** |
| **F3 half** | permute 50 % of synthetic rows | lift strictly between F1 and F0 |
| **F4 copy** | synthetic := the person's own observed vector | 🔴 **PASS**, large lift |

**F4 is not optional.** Without a positive control, a gate that always reads ≈ 0 looks like a real
failure instead of a broken gate. F1 proves it can fail; **F4 proves it can pass.**

## 5. Predictions

| # | prediction |
|---|---|
| **P1** | F0 J1a lift **≥ 0.10** ⇒ PASS. The model is given the vector, so it should retain participation |
| **P2** | F0 J1b lift **≥ 0.10** ⇒ PASS. Less confident than P1: timing is harder than participation |
| **P3** | F1 lift within **±0.02 of 0** on both, both FAIL |
| **P4** | F2 runs clean and FAILs, no exception, and the report says why rather than printing a bare 0 |
| **P5** | F3 lift is **0.35–0.65×** the F0 lift on J1a |
| **P6** | F4 J1a lift **≥ 2.0** ⇒ PASS |
| **P7** | The tighter demographic null reduces the F0 J1a lift by **less than half** ⇒ the signal is person-level, not stratum-level |
| **P8** | Wiring the gate changes **no existing gate line** in the validator — the run diff is additions only |
| **P9** | J1a and J1b do **not** return the same verdict class on F0 (participation and timing are different skills, and if they read identically I have probably written one statistic twice) |

**Where I expect to be wrong:** P2 and P5. Timing over a 48-slot day with ~1 active slot per row is
a thin signal, and the half-shuffle's linearity assumes the lift is additive in the fraction
shuffled, which it need not be.

---

## 5b. ADDENDUM, written after the five arms ran and before the two diagnostics

**Disclosed in order, because the order is what makes the rest of this credible.** The five arms
are done: **8/8 required conditions met**, and the control reads **J1a FAIL (lift +0.0179)** while
the positive control F4 reads **+2.3778**. So the gate works and the shipped pool shows almost no
person-level retail retention. **P1 and P2 are already lost and are not being rewritten.**

Two diagnostics follow. **Their predictions are written here, now, before either is run**, because
each could soften or sharpen a FAIL that is already on the record.

🔴 **The honest counterargument to the whole gate, stated before the diagnostics rather than after
them.** Each person has **exactly one observed diary day**. So the true cross-day-type persistence
of retail behaviour — how much a person's Tuesday *should* predict their Saturday — **is not
measurable from this data at all.** The gate measures retention against **zero**, not against the
truth. If real retail behaviour is near-independent across day types for a given person, then a lift
of 0 is *correct behaviour and not a defect*, and the 0.10 bar would be wrong. **The bar stays where
it was pre-registered**; what changes is that this limitation is published beside the verdict.

**D1 — the cross-channel test.** Run the identical statistic on `hom30` and `wrk30`, whose gates
PASS. Work schedules are strongly person-specific, so this is the closest thing to an internal
reference for "how much persistence a channel of this generator can carry".

- **P10**: `wrk30` J1a lift is **at least 3×** retail's, and clears the 0.10 PASS bar.
- **P11**: if `hom30` and `wrk30` *also* read below 0.02, the finding is **generator-wide**, not
  retail-specific — which would make it a much larger finding and would not be reported as a retail
  defect.

**D2 — the demographic null** (P7, already registered): the tighter
`cell × AGEGRP × SEX × LFTAG` null reduces the F0 J1a lift by less than half.

---

## 5c. ADDENDUM 2 (V3-J2), written before the arm it predicts

**Rebuilding the lost V2-E1 falsifier surfaced a confound in E1's own design, and it is visible in
the run diff rather than inferred.** Permuting the `ret30` block between people — E1's
`SHUFFLE-STRAT`, and my arm B — **also destroys channel exclusivity**: a person who was AT_HOME at
14:00 acquires a donor's retail episode at 14:00, so two channels are active in the same slot.
Measured, arm A → arm B:

- `ISR-final` **0.000000 % PASS → 1.421611 % FAIL** (87,427 / 6,149,856 slots)
- `X-3` **0 cells PASS → 73,448 cells (1.19 %) WARN** on the hom∧ret pair
- `S9` semantic "purchasing but AT_RETAIL=0" **10.8 % → 93.6 %**

🔴 **So E1's conclusion that *"`ISR-final` and `X-3` catch the person shuffle"* is wrong.** They
caught **simultaneity**, an artefact the perturbation introduced — not person-level scrambling.
E1's *surviving* claim is untouched and is reproduced here exactly: **all 10 RW/RETM gates are
byte-identical** under the same perturbation. *A perturbation that changes more than one thing
cannot attribute what it breaks* — the lesson E1 wrote down, applied to E1.

**Arm E, and its predictions, written now:** permute **`hom30`, `wrk30` and `ret30` together** —
the whole day moves to another person within the same cell. Exclusivity is preserved by
construction (each row still holds one internally consistent day) and every marginal of every
channel is preserved exactly.

| # | prediction |
|---|---|
| **P12** | `ISR-final` stays **PASS** at 0.000000 % and `X-3` stays PASS on all three pairs — i.e. the confound is gone |
| **P13** | the RW/RETM battery is **byte-identical** to arm A, as in arm B |
| **P14** | RW9's participation lift falls below **+0.010** (from +0.0179) |
| **P15** | `S9`'s semantic line stays within **2 pp** of arm A's 10.8 % |

**P14 is the one at risk**, and for the reason J1 already established: there is very little person
signal in the control to destroy, so the drop may be small and noisy.

### 5d. ADDENDUM 3 — arm F, written after E ran and before F did

**Arm E traded one confound for another, and the trade is visible in the diff.** Exclusivity is
preserved exactly (`ISR-final` and `X-3` never move — **P12 holds**), but moving the three presence
channels while leaving `act30` behind destroys presence↔activity consistency:
`S9` *"purchasing activity but AT_RETAIL=0"* goes **10.8 % → 93.6 %**, `GA-3` floating excess
**+1.32 pp → +17.40 pp FAIL**, `OW5` 58.2 % → 55.0 %. **P15 fails.**

🔴 **So there is no perturbation that destroys ONLY the person→retail link.** Retail presence is
entangled with the other presence channels through exclusivity and with the activity sequence
through semantics. **The way out is to move the whole day**: permute **all thirteen 48-column
channel blocks together** — `act30`, the three presence channels and the nine co-presence channels —
within the same cell. Every row remains an internally consistent day; every marginal is preserved;
the only thing destroyed is the link between that day and *whose* day it is.

| # | prediction |
|---|---|
| **P16** | `ISR-final` and `X-3` unchanged from arm A |
| **P17** | the RW/RETM battery unchanged from arm A |
| **P18** | RW9 participation lift falls below **+0.010** |
| **P19** | 🔴 **at most 6 lines change in the entire validator output, and every one of them is either RW9 or a per-respondent longitudinal gate (the `OW5` family)** — i.e. the whole Step-4 battery contains exactly **two** checks that can see the person at all |

**P19 is the claim worth making and the one most likely to be wrong.** It asserts an inventory of
the entire validator, not a property of one gate.

## 6. Rules that bind this task

- **No band moves after a result is seen.** If F0 lands at 0.09, the gate reads WARN and the number
  is published.
- **A new FAIL is not a reason to weaken the gate.** V2-E1 predicted this gap; finding it is the
  point.
- **The shipped pool is never mutated.** All arms operate on in-memory copies.
- **No threshold anywhere else in the project moves**, and no existing gate is touched.
- Local only. No Speed, no simulation.
