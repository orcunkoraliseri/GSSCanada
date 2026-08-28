# `D-S6-16` — the memorisation ceiling was scored, it alarmed, and the measurement says it is not a ceiling

**Date:** 2026-08-24 (night)
**Raised by:** the first scored `D-S6-14` control — job `1286941`, fold `it`, Leg 4
**Status:** 🟢 **RULED (a′) 2026-08-28 — CLOSED.** See §9. It was OPEN but **NARROWED** on 2026-08-25: the governing Leg-5 audit was read and `G6.10` **FAILS its pre-registered bar**, so this decision never gated the release; it governed only how the ceiling is written up in the methods — §8.
**Evidence:** `Step6_docs/outputs_step6/privacy_mia_leg4_it.json`,
`Step6_docs/outputs_step6/4J_step6_mia_1286941.out`, the training logs of `1281612` (reported `it`)
and `1286899` (permuted `it`). `4thJ_06_transfer.md`, entry 2026-08-24 (night), `FINDING 112` /
`FINDING 113`.

---

## 0. What was ruled, and what has now been measured

`D-S6-14` was ruled **(a)** on 2026-08-22: build a control adapter by permuting the prefix-to-body
pairing (strict derangement, seed `614614`, 0 fixed points), train it exactly as the reported model
is trained, and score the same MIA against it. The ruling's logic was that such a model **can only
memorise** — with the pairing destroyed there is nothing generalisable left to learn — so its MIA AUC
is an upper bound on what memorisation can produce, and the reported model must come in **below** it.

The first one has now been scored. It came in **above**, on both attacks:

| | reported adapter | ceiling (permuted) | headroom | pre-registered bar |
|---|---|---|---|---|
| `G6.10` loss MIA AUC | **0.5539** | **0.5488** | **−0.0051** | ≤ 0.65 |
| `G6.11` reference MIA AUC | **0.5274** | **0.5147** | **−0.0127** | ≤ 0.75 |
| perplexity gap | 0.0182 | 0.0168 | −0.0014 | ≤ 0.05 |

The module printed the alarm it was built to print:

> 🔴 A model that could only memorise did not leak more than the reported one. Either the reported
> run memorised, or the control did not train. Neither reading permits a release.

🔴 **Both bars are still passed with room** — `G6.10` 0.5539 against 0.65, `G6.11` 0.5274 against
0.75, and `G6.12` found 0 exact matches in 103 rare records. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45`, verified live inside the job. Nothing below asks for a bar to
move.

---

## 1. `FINDING 112` — the control did train, and it reached the same loss as the reported model. That is what makes it not a ceiling.

The alarm offered two readings. **The measurement supports a third one that it did not offer**, and
three independent numbers say the same thing.

**(i) The training loss.** Mean of the last 20 logged steps of epoch 2:

| run | job | start | last-20 mean | sd |
|---|---|---|---|---|
| reported `it` | `1281612` | 1.7323 | **0.5565** | 0.0386 |
| permuted `it` | `1286899` | 1.7134 | **0.5536** | 0.0733 |

🔴 **The model whose prefix-to-body pairing was destroyed ended 0.0029 *below* the correctly-paired
one.** It did train — 1.71 → 0.55 — and it trained to the same place.

**(ii) The perplexity, measured inside the audit itself, on held-in text.** Reported model train
`1.7189`; ceiling model train `1.7353`. **0.95 % apart.**

**(iii) The conditioning gates, on the permuted adapters.** `G4.3`, `G4.4` and `G4.12` **all FAIL**
on both permuted runs read so far (`1286899` `it`, `1286898` `uk`; `G4.12` `it` CE rise 0.0023
against a required 0.15, MI drop −0.070 against 0.10). The permutation did exactly what it was
designed to do — it destroyed conditioning on age, sex, household type, economic status and day type.

Put (iii) beside (i) and (ii) and the mechanism is not in doubt: **conditioning on the prefix
contributes almost nothing to the training loss.** A model that has entirely lost it reaches the same
likelihood as one that has it.

The consequence for `D-S6-14` is structural. The ruling assumed that destroying the pairing leaves
nothing generalisable to learn, so the control is *forced* to memorise. **That premise is false for
this corpus.** The permutation shuffles which prefix sits in front of which body; the bodies
themselves are untouched, and are checked by the builder to be an unchanged multiset. Every diary
body in the permuted corpus is still a real, well-formed, grammatical diary. The control model
therefore has a large, entirely generalisable thing left to learn — **the diary language itself** —
and it learns that instead of memorising. Its MIA AUC is near chance because it never needed to
memorise, **not** because memorisation is impossible at this capacity.

🔴 **A control that is not forced to memorise does not bound memorisation. `0.5488` is not a
ceiling; it is another model's near-chance MIA score.**

⚪ This is the same class of defect as `FINDING 56` — a guard that returns a number for a reason
other than the one it was built to test. It was caught the same way: by measuring rather than
reading the design again.

## 2. `FINDING 113` — the comparison has no tolerance, and the alarm fires on noise

`D-S6-14` pre-registered the direction of the comparison and no margin for it. The module implements
a strict test, so any headroom below zero alarms. At `n = 2000` per class the Hanley–McNeil standard
error of a single AUC near 0.55 is **0.0091**:

| | observed gap | SE of the difference | z |
|---|---|---|---|
| `G6.10` | 0.0051 | 0.0128 | **0.40** |
| `G6.11` | 0.0127 | 0.0129 | **0.99** |

🔴 **Neither difference is distinguishable from zero.** The reported model and the ceiling model are,
on this evidence, tied. Even if §1 were wrong and the control were a valid ceiling, this particular
alarm would not be evidence that the reported model leaks more — it would be two indistinguishable
numbers ordered by noise. `FINDING 86` already forced size-matching on this attack for a related
reason; the tolerance was never added.

---

## 3. The decision

**What does an alarmed `D-S6-14` control mean for the release decision?**

| | option | what it does | cost |
|---|---|---|---|
| 🟢 **(a)** | **Read the alarm as informative about the control, not about the reported model, and say so in the audit.** `D-S6-14`'s premise is refuted by §1's three measurements; the control is reported as **INCONCLUSIVE AS A CEILING**, with the loss/perplexity/gate evidence printed beside it. The release decision rests on the two pre-registered bars (`G6.10` ≤ 0.65, `G6.11` ≤ 0.75), the untuned-base floor, the perplexity-gap control and `G6.12`, **all four of which pass**. | Honest, additive, and costs no compute. The ceiling stays in the paper as a control that was built, run, and found not to do what it was designed to do — which is a result. | The release rests on four controls instead of five. A reviewer may ask why the fifth was kept in the paper; the answer is that removing a control after seeing its result is the thing we do not do. |
| **(b)** | **(a), plus add the pre-registered tolerance `D-S6-14` never had** — declare the alarm to fire only when headroom is negative **beyond** the sampling noise (e.g. 2 SE of the difference, ≈ 0.026 at `n = 2000`), and re-score. | Fixes `FINDING 113` as well. Under it, `it` does not alarm at all. | 🔴 It is a threshold set **after** seeing the number it would decide. Even with the correct noise model, this is the pattern this project has refused everywhere else. **Not recommended as a repair — only as a pre-registration for any future fold.** |
| **(c)** | **Build a ceiling that is actually forced to memorise** — randomise the *bodies* (shuffle tokens within each body, or replace them with random draws from the alphabet) so nothing generalisable survives, and retrain. | Would be a real upper bound. | A full retrain per fold. On Leg 5 that is the 7 B model and the `a100_7g.80gb` instance — days, and it lands on the critical path of everything. And it answers a question the four passing controls already answer. |
| **(d)** | **Treat the alarm at face value and refuse the release.** | Nothing to build. | Refuses on the strength of a control whose own premise §1 shows to be false, and on a 0.4-sigma difference. It would be a refusal caused by a defective instrument. |

🟢 **Recommendation: (a).** It changes no threshold, discards no control, and repairs no number after
the fact. It records what was measured — that the control did not do what it was designed to do, and
why — and leaves the release resting on the four controls that did.

⚪ If **(a)**, the same reading applies to `uk` (`1286945`, running), `es` (owed when `1286897`
lands) and to the governing Leg-5 `it` control, **whatever they return** — and that must be stated
now, before they are read, or (a) becomes a rule invented per result.

## 4. What does not change whichever way this goes

* The two pre-registered bars. `G6.10` ≤ 0.65 and `G6.11` ≤ 0.75 are untouched, and both pass on the
  reported adapter by a wide margin.
* The permuted shards, the seed `614614`, the derangement, and the `POISONED_CONTROL` interlock
  (seen refusing in both directions, job `1286901`).
* `G6.12` — 0 exact matches, greedy and sampled, over 103 rare records.
* 🔴 **This is Leg 4. It is the pilot and it is NOT REPORTABLE** — the module prints that itself. The
  governing control is the Leg-5 `it` run, and it is still owed a submission at
  `--gres=gpu:nvidia_a100_7g.80gb:1` and `--mem=192G`.

## 5. How to answer

One line: `D-S6-16 = (a)`, `(b)`, `(c)` or `(d)`. If (a), `privacy_audit.md` is written from the
four passing controls with the ceiling reported as inconclusive, and the release decision follows on
Leg 5.

---

## 6. ADDENDUM, same night — the `uk` control landed and it makes the case stronger, not weaker

Job `1286945`, fold `uk`, Leg 4. **It did not alarm**: `G6.10` reported 0.5336 against a ceiling of
0.5484 (headroom **+0.0148**), `G6.11` 0.5074 against 0.5116 (**+0.0041**). All four registered
controls pass. On its own that reads as the ceiling working.

🔴 **`FINDING 114` — the ceiling does not move between folds.**

| fold | reported `G6.10` | ceiling `G6.10` | headroom | alarm? |
|---|---|---|---|---|
| `it` | 0.5539 | **0.5488** | −0.0051 | 🔴 YES |
| `uk` | 0.5336 | **0.5484** | +0.0148 | no |

The two ceilings are **0.0004** apart — **1/23 of one Hanley–McNeil standard error** (0.0091) —
across two independently trained adapters, two corpora and two held-out countries. Over the same two
folds the *reported* AUCs differ by **0.0203**, fifty times as much.

A quantity that is supposed to bound *how much this model could memorise* and instead comes out
constant to four decimals is not measuring memorisation capacity. It is measuring a fixed property of
the setup — precisely what §1 predicts, because the permuted model learns the diary language rather
than memorising, and the diary language is the same in every fold.

🔴 **The operative consequence: `D-S6-14` has been acting as an unregistered bar at ≈ 0.548.**
`it` alarmed and `uk` did not, and the ceiling did not move between them — the reported AUC did. So
in practice the control substitutes a hidden `G6.10 ≤ 0.5484` for the pre-registered `≤ 0.65`: a
threshold **82 % tighter**, set by an artefact, never registered, and discovered only after it fired.

This is an independent reason for **(a)**, and it does not depend on accepting §1's mechanism. Even a
reader who rejects the language-learning explanation has to account for a ceiling that is identical
across folds to 0.0004.

⚪ `FINDING 112` also reproduces on `uk`: permuted last-20 mean loss 0.5195 vs reported 0.5005 —
+0.0190 against an SE of the difference of ≈ 0.021, under one sigma, the same verdict as `it`
(where the permuted run came out 0.0029 *lower*). Held-in perplexity 1.6701 vs 1.6572, **0.78 %**
apart, against `it`'s 0.95 %.

⚪ §3's undertaking is now partly spent and the record says so: this recommendation was written and
committed **before** `1286945` was opened, and `uk` came back in the direction that would have made
dropping the recommendation convenient. It stands unchanged. `es` (`1286955`) and the governing Leg-5
`it` control are still to come, and (a) applies to them whatever they return.

---

## 7. SECOND ADDENDUM, 2026-08-25 — all three Leg-4 folds are in, and the ceiling has a standard deviation of 0.00117

Job `1286955`, fold `es`, **ALARMED** — by the smallest margin yet, headroom **−0.0015** on
`G6.10` and **−0.0021** on `G6.11`. The Leg-4 board is complete:

| fold | job | reported `G6.10` | ceiling `G6.10` | headroom | z | alarm? |
|---|---|---|---|---|---|---|
| `it` | `1286941` | 0.5539 | **0.5488** | −0.0051 | 0.40 | 🔴 YES |
| `uk` | `1286945` | 0.5336 | **0.5484** | +0.0148 | 1.16 | no |
| `es` | `1286955` | 0.5481 | **0.5466** | −0.0015 | **0.12** | 🔴 YES |

| over the three folds | mean | sd | range |
|---|---|---|---|
| **ceiling** `G6.10` | 0.5479 | **0.00117** | **0.0022** |
| **reported** `G6.10` | 0.5452 | 0.01046 | **0.0203** |

🔴 The between-fold sd of the ceiling is **one eighth of the Hanley–McNeil SE of a single one
of these AUCs** (0.0091). Three independently trained adapters, three corpora, three held-out
countries — 0.5488, 0.5484, 0.5466. The quantity it is meant to bound ranges **9.2×** more widely.
`G6.11` agrees: ceiling range 0.0067 against a reported range of 0.0200.

**So which folds alarm is decided by noise on the reported side alone.** `es` alarms on a gap of
0.0015 against a difference SE of 0.0128. Two of three folds alarming says nothing about two of three
models; it is three reported AUCs scattering by ±0.01 around a constant that sits among them.

🔴 **`D-S6-14` has been imposing an unregistered bar at 0.5479 ± 0.001** — **82 % tighter**
than the pre-registered `≤ 0.65`.

⚪ §1 also reproduces on all three folds. Permuted minus reported last-20 mean loss: `it`
**−0.0029** (z −0.15), `uk` +0.0190 (z 0.90), `es` +0.0165 (z 1.07) — nothing reaches 1.1 sigma,
in either direction. Held-in perplexity penalty: **0.95 % / 0.78 % / 0.88 %**, under 1 % everywhere,
while `G4.3`/`G4.4`/`G4.12` FAIL on every permuted adapter.

⚪ **All four registered controls PASS on all three folds**, including `G6.12` — zero exact
matches, greedy and sampled, over 103 / 40 / 91 rare records — and untuned-base floors of 0.4874 /
0.5012 / 0.4914, all within 0.013 of 0.50.

**The recommendation is unchanged: (a).** It now rests on three folds rather than one, and on a
measurement — sd 0.00117 — that does not require accepting §1's mechanism to be damning.
🔴 Still Leg 4, still `NOT REPORTABLE`; the governing control is the Leg-5 `it` run `1286896`,
still training.

---

## 8. THIRD ADDENDUM, 2026-08-25 — the governing run changes what this decision is for

Job `1286976`, Leg 5, `Olmo-3-1025-7B`, fold `it`, the run this decision was waiting on.

| | measured | bar | verdict |
|---|---|---|---|
| `G6.10` | **0.6645** | ≤ **0.65** | 🔴 **FAIL** (z = 1.70 over the bar) |
| `G6.11` | 0.5594 | ≤ 0.75 | PASS |
| perplexity gap | **0.0570** | ≤ **0.05** | 🔴 **FAIL** |
| `G6.12` | 0 exact of 103 rare | 0 | PASS |
| untuned-base floor | **0.4886** | ≈ 0.50 | clean |

🔴 **Option (a) as written is no longer available.** It said *“rest the release on the two
pre-registered bars, the untuned-base floor, the perplexity-gap control and `G6.12`, all four of
which pass”*. On the governing run **two of them fail**, and the floor being clean (0.4886) is what
makes the failure readable as membership signal rather than a split artefact.

**So the release decision is settled by the registered bar, not by this decision.** `G6.10` is a
registered gate, scored on the reported leg with the reported model, and it failed. What remains open
here is narrower and still real: **how the `D-S6-14` ceiling is reported in the methods.** The four
options collapse to two:

| | option | what it does |
|---|---|---|
| 🟢 **(a′)** | **Report the ceiling as measured, with both corrections stated.** It is constant across folds at fixed capacity (Leg 4: 0.5479 ± 0.00117 over three folds) and rises sharply with capacity (Leg 5: **0.6496**, +0.102). It discriminates backbones, not folds. Its alarms are recorded on all four runs, with their z-values, and it is **not** used to license or refuse anything — the registered bars do that. | Costs nothing, discards nothing, and states plainly what the instrument does and does not measure. |
| **(c′)** | Build the body-randomised ceiling of §3(c) as well, now that Leg-5 capacity is known to move the ceiling. | A full 7 B retrain. It would sharpen the methods section and cannot change the release, which the bar has already decided. |

🟢 **Recommendation: (a′).**

### 🔴 Two corrections to this brief's own earlier sections

1. **§6/§7 (`FINDING 114`) were stated too broadly.** *“The ceiling is not a property of the fold —
   it is a constant of the setup”* holds **within Leg 4 only**. The Leg-5 ceiling is 0.6496, +0.102
   over the Leg-4 mean and **87×** its between-fold sd. The “unregistered bar at ≈ 0.548, 82 %
   tighter than ≤ 0.65” reading is Leg-4-only; on Leg 5 the implicit bar is 0.6496, *above* the
   registered one.
2. **§1 (`FINDING 112`) had an inference that does not survive 7 B.** The measurement reproduces on
   every run — permuted minus reported last-20 loss −0.0029 / +0.0190 / +0.0165 / **+0.0045
   (Leg 5, z = 0.23)**. But “so the control never needed to memorise, so its AUC is near chance” is
   false at 7 B, where the control reaches **0.6496**. The control memorises substantially there while
   its aggregate loss stays indistinguishable from the reported model's. The inference is withdrawn
   for Leg 5 and stands for Leg 4.

⚪ Both corrections came from running the governing arm instead of generalising from the pilot —
the same lesson as `FINDING 105` and `FINDING 106` at Step 7.

---

## 9. RULING, 2026-08-28 — **(a′)**, delegated by the author

🟢 **`D-S6-16` is RULED (a′): report the ceiling as measured, with both corrections stated.** The
author delegated the choice to this session on 2026-08-28 (*"progress comme tu recommends"*) against
the standing recommendation in §8. **(c′) is declined** — it is a full 7 B retrain that cannot change
the release, which `G6.10`'s registered bar has already decided, and the Speed budget is not
re-opened for a methods refinement.

⚪ **What the ruling does.** It closes the last open item of the `D-S6-14` / `D-S6-16` chain. The
passages drafted at `writing/4thJ_writeup_notes.md` §8 were written under (a′) and are now the ruled
text: §8.1 methods, §8.2 results and limitations, §8.3 the `FINDING 112` withdrawal. They stand
unchanged; ruling (a′) adds nothing to them and removes nothing from them.

🔴 **What the ruling does NOT do.** It moves no threshold, re-scores no control, removes no control
from the paper, and reverses neither of §8's two corrections. It does **not** make the privacy audit
pass — the paper still ships **two registered FAILs and one partial** (`G6.10` 0.6645 > 0.65, the
perplexity gap 0.0570 > 0.05, `G6.13` 2 PASS / 1 FAIL on `uk`), the weights are **not** released and
the `uk` synthetic set is withheld. It does not build the body-randomised ceiling, which remains
**specified and not built** and is named as such in the limitation sentence.

⚪ **Reopen trigger, one only.** If a body-randomised ceiling is ever built for an unrelated reason,
its number is added to §8.1 and the limitation sentence is deleted. Nothing else reopens this.

**Status: RULED (a′), CLOSED.**
