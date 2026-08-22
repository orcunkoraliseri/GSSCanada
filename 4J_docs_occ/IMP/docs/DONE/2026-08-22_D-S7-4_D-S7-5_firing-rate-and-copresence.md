# `D-S7-4` and `D-S7-5` — two Step 7 decisions, both raised by running the gates on generated text

**Date:** 2026-08-22 (evening)
**Raised by:** the first run of `tools/4thJ_gates_step7.py` on the Leg-4 rehearsal batches.
**Status:** both OPEN. Nothing enforced, no grammar rebuilt, `prereg.md` untouched (md5
`e4243e07cdd80c9c846b91f40e3e8c45`).

Read `Step7_docs/4thJ_07_constrainedGeneration.md`, the two entries of 2026-08-22 (evening), for the
full evidence. This document is the decision, short.

---

## `D-S7-4` — what "constraint-firing rate" means

`G7.7` asks *"how often the mask had to intervene"*, per stratum, and pre-registers the expectation
**> 35 %** on the untuned base model and **< 2 %** on the fine-tuned one.

**The problem.** vLLM's structured-output back-end exposes **no count of mask interventions**. The
literal per-token reading — the share of decoding positions where the mask removed at least one
candidate — is approximately **100 % for every batch that will ever be generated**, because the
grammar forbids most of the vocabulary at almost every position. It carries no information and it
cannot be compared to 35 % or to 2 %.

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Per DIARY: the share of diaries the model gets structurally wrong when the mask is OFF.** | It is the quantity the pre-registered 35 % / 2 % expectations are sized for. It is already measured: pooled it **is** `1 − G7.5`, and `G7.7` is the same thing per stratum. No new instrumentation. 🔴 The methods must then say plainly that `G7.5` and `G7.7` are one measurement at two granularities, rather than presenting them as independent evidence |
| **(b)** | Per TOKEN, with a custom `LogitsProcessor` counting positions where the sampled token would have been masked out | Honest, and much more expensive: a second decode of every diary, outside vLLM's structured-output path, producing a number with no pre-registered band to compare against |

**Currently implemented as (a)**, declared at the top of `tools/4thJ_gates_step7.py`. Nothing
downstream depends on it yet, so (b) is still reachable at the cost of rebuilding the gate.

### A sizing consequence that follows either way

`V7.a` refuses to score `G7.7`/`G7.8` unless **10 strata carry ≥ 100 records**. The pilot's `N = 600`
cannot fill more than six, so both gates are currently FAILING for that reason and have never been
scored. From the real 100,000-person prefix pools (**228 strata per fold**):

| fold | 10th-largest stratum share | 🔴 minimum `N` |
|---|---|---|
| `es` | 1.96 % | **5,115** |
| `uk` | 1.92 % | **5,203** |
| `it` | 2.06 % | **4,850** |

**The Leg-5 campaign must be sized at `N ≥ ~5,200` per fold** or `G7.7`/`G7.8` cannot be reported at
all. `G7.9` is harder: its rejection-sampled control needs enough *valid unconstrained* diaries to
match the constrained batch, which at Leg-4 yields would take ~22,500 draws on `es`. It becomes
affordable exactly to the extent Leg 5 raises `G7.5`.

---

## `D-S7-5` — what `G7.4` enforces

`G7.4` is specified as an enforcement confirmation delivered *"via pre-compiled grammar variants
indexed by household type"*. **Those variants do not exist** — one grammar is compiled, with the full
`COP` alphabet `0..64` — so `G7.4` currently measures, and it FAILS on all three folds.

The rule was then run against **all 73,254 real diaries before proposing to enforce it**, which is the
lesson `FINDING 45` cost 28.95 % of the corpus to learn. It splits cleanly in two.

### Half one — household membership. 🔴 A basis change.

A person whose household type contains no partner cannot be co-present with a household partner.

| fold | diaries | violating | share |
|---|---|---|---|
| `es` | 19,140 | 226 | 1.18 % |
| `it` | 38,260 | 124 | **0.32 %** |
| `uk` | 15,854 | 744 | **4.69 %** |
| **all** | **73,254** | **1,094** | **1.49 %** |

A **14.7× spread** between `uk` and `it`. Country-correlated, so it is read per fold or not at all,
and it can move a LOCO result by itself. The violations are the harmonised source disagreeing with
itself — household type from one survey field, company from another — and `D-S2-19` already forbids
repairing that class on a prevalence basis.

### Half two — self-contradiction. 🟢 Costs nothing.

An episode asserting `cop_alone` **and** some other co-presence flag at the same time. No household
knowledge needed; the episode contradicts itself.

* **Real corpus: 0 episodes in 73,254 diaries.** Not rare — zero.
* **Generated, Leg-4 pilot: 39 (`es`) / 23 (`uk`) / 59 (`it`).**

This is the first thing in Step 7 that cleanly separates *"the corpus is like this"* from *"the model
invented this"*.

### The options

| | option | consequence |
|---|---|---|
| **1** | 🟢 **Recommended. Enforce ONLY the self-contradiction rule.** | **Zero real diaries rejected**, so additive, not a basis change. One `COP` sub-alphabet rather than six: the 32 patterns with bit 0 set alongside any other bit are simply absent. Removes a defect the model demonstrably has |
| **2** | Enforce household membership as well, via the six household-indexed variants. | 🔴 **BASIS CHANGE.** 1.49 % of real diaries rejected, 14.7× unevenly by country, and it must be declared as a modelling intervention rather than as structural validity — exactly what `D-S7-2` (a) declined to do for `G7.3` |
| **3** | Enforce neither; report both rates alongside `G7.3`. | Cheapest and consistent with `D-S7-2` (a). But it leaves the model free to emit self-contradicting episodes no human day contains, and **Step 8 reads `COP`** |

🔴 **Nothing is enforced pending the ruling.** `G7.4` stays FAILING and reports both halves
separately. `tools/4thJ_step7_ebnf.py` is untouched and the grammar md5 is unchanged.
