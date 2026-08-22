# `D-S6-14` — the random-label-permutation control: what it permutes, and on which model

**Raised** 2026-08-22, after `D-S6-12` and `D-S6-13` were ruled and applied and `IMP/docs/` emptied.
**Status** OPEN. **Blocks** `privacy_audit.md`, and therefore any release decision.
**Costs GPU time** — see §6. Nothing has been run for this; no job is queued for it.

---

## 1. Why this is being raised now rather than left as a named gap

It has been carried as a NAMED GAP since Step 6.5 was built, and the gap is honest — the artefact
prints it and refuses to imply otherwise:

> 🔴 CONTROL NOT RUN: random-label-permutation adapter. Two of three registered controls are
> present. No release decision can rest on this.

What has changed is that **the pilot numbers are now in, and they make the gap load-bearing rather
than procedural.** All three folds ran (`privacy_mia_leg4_{es,uk,it}.json`) and every privacy gate
PASSES:

| fold | `G6.10` AUC (max 0.65) | `G6.11` AUC (max 0.75) | untuned-base control | ppl gap (max 0.05) |
|---|---|---|---|---|
| `es` | 0.5481 | 0.5204 | 0.4914 | 0.0143 |
| `uk` | 0.5336 | 0.5074 | 0.5012 | 0.0097 |
| `it` | 0.5539 | 0.5274 | 0.4874 | 0.0182 |

🔴 **The attack AUCs sit 0.03–0.07 above the untuned-base control, and the bar sits 0.10–0.12 above
the attack.** The base control anchors the *bottom* of the scale: it confirms that a model which saw
no training data scores ~0.50, so the two splits do not differ for a reason that is not membership.
**Nothing anchors the top.** We do not know what a model that memorised its training set outright
would score on this attack, on this data, at this record length. If that number were 0.62, a
measured 0.55 would be alarming. If it were 0.99, a measured 0.55 would be reassuring. The gate
cannot distinguish those two worlds, and the 0.65 bar was chosen without reference to either.

That is exactly what the random-label-permutation adapter provides — the **memorisation ceiling** —
and it is why the audit cannot conclude without it. The gap is not a missing tick on a checklist; it
is the missing half of the scale.

⚪ `G6.12` (extraction) is not affected: it attempted all 91 records in the 33 rare strata and found
**0 exact matches** under both greedy and sampled decoding. That is an absolute result and needs no
ceiling.

---

## 2. The problem: "random label permutation" has no single meaning for a generative model

The phrase is borrowed from classifier privacy work, where it is unambiguous — shuffle the labels,
retrain, and whatever attack success remains can only come from memorising individual examples,
because the label is no longer predictable from the features. **Our model has no labels.** It is a
conditional sequence model, `PREFIX -> BODY`, and there are at least four non-equivalent things the
phrase could mean here. They do not measure the same thing and they do not cost the same.

**(a) Permute the prefix-to-body pairing.** Shuffle which prefix is attached to which diary body
across the training shard, keeping both multisets intact. The conditional structure becomes pure
noise, so nothing generalisable remains to learn and any residual attack signal is memorisation of
specific `(prefix, body)` pairs. This is the closest structural analogue to the classifier
construction: the "label" our model predicts is the body, and the prefix is the feature vector.

**(b) Permute the activity alphabet.** Apply one fixed random bijection to the 158 `ACT` codes (and
optionally `LOC`/`COP`) across the whole shard. The grammar, the durations, the 1440-minute closure
and the tally automaton all survive untouched; only the semantics are scrambled. This measures
memorisation of **surface strings** while leaving the sequence statistics learnable — so it is a
weaker ceiling than (a), because the model can still learn "long runs of one code", "transitions
cluster at 10-minute boundaries", and so on.

**(c) Shuffle episode order within each diary.** Keeps every duration and code, destroys the
temporal structure. 🔴 This one is defective for our purposes and is listed only to rule it out: the
durations still sum to 1440 so the grammar holds, but the resulting strings are not diaries in any
sense, and a model trained on them is not a control for a model trained on diaries — it is a
different experiment.

**(d) Randomise the prefix only.** Assign each training record a uniformly random prefix drawn from
the observed prefix distribution, leaving the bodies untouched and in place. Cheapest to construct
and it isolates one specific question — does the attack signal come from the conditioning or from
the body? — but it is **not** a memorisation ceiling: the bodies are still real, still learnable,
and the model can still generalise over them.

**Recommendation: (a).** It is the only one of the four that actually produces the ceiling the audit
needs, it is a one-line shuffle at shard-build time, and it changes nothing about the token
distribution, the sequence lengths, the grammar or the training budget — so the resulting AUC is
comparable to the real run by construction rather than by argument. (b) is a reasonable *second*
control if the author wants to separate surface memorisation from structural memorisation, but it
should not be the only one, and it is not what "sets the floor for pure sequence memorisation" in
the module's own words.

---

## 3. The second question, which is the expensive one: which leg does the control run on?

🔴 **A control must run on the same model as the thing it controls.** The reported privacy audit
will be the Leg-5 one (`allenai/Olmo-3-1025-7B`, 3 epochs). A permuted-label adapter trained at
Leg-4 scale (`OLMo-2-0425-1B`, 2 epochs) would establish the memorisation ceiling **for a 1.48 B
model at two epochs** — and memorisation capacity is precisely the thing that scales with parameter
count and epochs. Using the Leg-4 ceiling to interpret a Leg-5 attack would be a basis mismatch of
exactly the kind this project has caught four times already.

So the honest options are:

**(i) Three Leg-5 permuted runs**, one per fold, matching the reported model exactly. Gives a
directly comparable ceiling. Costs three more 7 B training runs on `gpu:nvidia_a100_7g.80gb:1`.

**(ii) One Leg-5 permuted run on a single pre-named fold.** The privacy attack is a per-fold
quantity, so one fold gives one ceiling; the other two would be interpreted against it as an
approximation, and that approximation must be declared. Costs one 7 B run. 🔴 The fold must be named
**before** the run, not chosen after seeing which one looks best — and note that `it` is already the
predicted-weakest fold (31,560 records, 97 strata), so it is the natural pre-named choice on
"weakest case" grounds rather than on any observed result.

**(iii) Three Leg-4 permuted runs**, cheap, and declare the ceiling as pilot-scale with the
scale mismatch stated in `privacy_audit.md`. Costs almost nothing but yields a ceiling that does not
govern the reported model. 🔴 My view: this is worth having as *corroboration* and is not worth
having as *the* control — but it is genuinely cheap, and it can be run now, whereas (i) and (ii)
cannot.

**(iv) Do not run it. Ship `privacy_audit.md` with two of three controls and the gap declared.**
Legitimate only if the audit's conclusion is written so that it does not depend on the ceiling —
which, given §1, means it cannot conclude that the measured AUCs are low. It would have to say the
attack found no evidence of memorisation *and that the sensitivity of that finding is unquantified*.

**Recommendation: (ii), pre-naming `it`, with (iii) run alongside at Leg-4 on all three folds.**
That buys the governing ceiling on the fold most likely to memorise, plus a cheap three-fold picture
of how the ceiling varies between folds, for one 7 B run rather than three. If the `it` Leg-5
ceiling and the `it` Leg-4 ceiling stand in a sensible relation to each other, the Leg-4 spread
across `es`/`uk` becomes usable evidence about the Leg-5 spread. If they do not, that is itself
worth knowing before release.

---

## 4. What is NOT in dispute

* The permuted adapter is scored by **exactly the same attack code**, unchanged, at the same
  thresholds. Nothing in `4thJ_step6_privacy_mia.py` needs to move; it takes an adapter path.
* The permutation is applied at **shard-build time** and the seed is recorded in the artefact. The
  module already carries `SEED = 20260822`; the permutation seed must be separate and printed, since
  a control whose randomisation cannot be reproduced is not a control.
* 🔴 The permuted shard must **never** be written into the real shard directory or reused by any
  other step. It is a poisoned corpus by design.
* This control does not change any gate's bar. `G6.10`'s 0.65 and `G6.11`'s 0.75 are pre-registered
  and stay. 🔴 **The ceiling must not be used to move them** — it is read alongside the result, not
  substituted for the bar. Retuning a pre-registered threshold to sit between a measured attack and
  a measured ceiling would be exactly the post-hoc fitting the whole gate design exists to prevent.

---

## 5. What I have deliberately not done

Not built the permutation, not queued a job, not modified the privacy module. `4thJ_step4_train.py`
already carries a `--perturbation` lever (`FINDING 6`) and the shard builder is small, so option (a)
is perhaps twenty lines — but *which* permutation and *which leg* are both the author's, and one of
them costs 7 B GPU hours on a `gres/gpu` allocation that is currently capping the reported model's
own training at `AssocGrpGRES`.

## 6. Queue context, which bears on the timing

At the time of writing, job **1286209** (Leg-5 `es`, the critical path) is PENDING on
`AssocGrpGRES` with an estimated start of **2026-08-23T12:06**, and job **1286208** (item 7.2
throughput) is PENDING on `Resources`. `gres/gpu` is a **group-level** TRES counted across all MIG
slice types, so every GPU job submitted before Leg 5 starts can delay it. 🔴 Whichever option is
ruled, the permuted run should be submitted **after** Leg-5 training is under way, for the same
reason item 7.5's three rejection-control jobs are being held.

---

> ### Answer
>
> **Question 1 — what is permuted:**
> **Option (a) — Permute prefix-to-body pairing across the training shard.** Shuffle which prefix attaches to which diary body at shard-build time with a dedicated, printed seed (`SEED_PERM`), preserving token distributions, sequence lengths, and grammar support exactly.
>
> **Question 2 — which leg, and how many folds:**
> **Option (ii) + (iii) — Hybrid Scaling Strategy:**
> 1. **1 Leg-5 permuted run** on the pre-named **`it` fold** (the governing 7.30 B ceiling anchor on the largest/weakest training split).
> 2. **3 Leg-4 permuted runs** across all three folds (`es`, `uk`, `it`) to calibrate cross-national spread at minimal compute expense.
>
> **Anything else:**
> • **Queue scheduling directive**: Hold submission of all permuted training jobs until the critical-path Leg-5 training jobs (`1286209`) are actively running, preventing contention on `AssocGrpGRES`.
> • **Invariant**: Permuted shards are marked `POISONED_CONTROL` and stored strictly in isolated scratch paths, never into production shard directories. Pre-registered bars (`G6.10` $\le 0.65$, `G6.11` $\le 0.75$) remain strictly unchanged.

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|---|
| **1** | Permutation Construction | 🟢 **Option (a)** | **Permute prefix-to-body pairing at shard construction**; preserves token vocabulary and grammar invariants while completely severing conditioning signal. | Implement in shard builder with explicit `--permutation-seed`; isolate output paths from production shards. |
| **2** | Target Model Legs & Folds | 🟢 **Option (ii) + (iii)** | **1 Leg-5 run on fold `it` (7 B)** + **3 Leg-4 runs (`es`, `uk`, `it` at 1.48 B)**. | Submits after Leg-5 `es` starts; provides exact 7 B memorisation ceiling on the designated fold alongside full 3-fold 1.48 B baseline comparison. |
| **3** | Threshold Integrity & Audit Release | 🟢 **Confirmed** | **Bars remain frozen (`G6.10` $\le 0.65$, `G6.11` $\le 0.75$)**; control ceilings are reported alongside results to unblock `privacy_audit.md`. | Complete 3 of 3 registered controls to authorise final privacy release without moving pre-registered gate boundaries. |

---

### Detailed Rulings and Directives

#### 1. Question 1: Mathematical Definition of Generative Label Permutation
* **Choice**: Option (a) — Shuffle the prefix-to-body assignment across the training split.
* **Scientific Rationale**:
  - In conditional language modeling ($P(\text{diary} \mid \text{prefix})$), the prefix represents the input conditioning feature vector and the diary body constitutes the structured output sequence.
  - Randomly permuting prefix-body pairings destroys all generalisable conditional associations.
  - Any remaining MIA attack signal on the permuted adapter measures pure rote instance memorisation of arbitrary sequence pairings, establishing the exact theoretical memorisation ceiling required to interpret attack AUCs.

#### 2. Question 2: Hybrid Leg-5 Anchor and Cross-National Calibration
* **Choice**: Train 1 Leg-5 permuted adapter on pre-designated fold `it` (7.30 B, 3 epochs) and 3 Leg-4 permuted adapters (`es`, `uk`, `it` at 1.48 B).
* **Scientific Rationale**:
  - **Ex-ante designation**: Fold `it` is pre-designated as the primary 7 B control anchor based on prior reasoning (largest training pool: 31,560 records; highest stratum fragmentation: 97 strata), avoiding post-hoc selection bias.
  - **Direct model parity**: Leg-5 `it` establishes the true parameter-scale memorisation ceiling for the 7.30 B architecture.
  - **Efficient cross-fold context**: Running the 3 Leg-4 folds measures the cross-national sensitivity of the ceiling across differing population structures with negligible GPU burden.
  - **Audit release**: Fulfills the 3-of-3 registered control requirement, allowing `privacy_audit.md` to be published with full scientific authority.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
