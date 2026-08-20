# Progress Log — Step 4 gate battery and author rulings

Append-only. Never delete, reorder or reformat an existing entry.

Governing spec: `4thJ_04_finetuneLLM_val.md` (fourteen gates `G4.1`–`G4.14`, vacuity guards
`V4.a`–`V4.h`, one coverage clause per battery).
Implementation state: `Step4_docs/impl/2026-08-18_step4-training.md`.
Pre-registration: `Step6_docs/outputs_step6/prereg.md`, frozen, md5
`e4243e07cdd80c9c846b91f40e3e8c45` held in the sidecar `prereg.md.md5`. Never edited.

---

### 2026-08-18 — Speed job `1266911`. The training-side battery RAN CLEANLY and moved DoD item 6 off zero.

**Job.** `4thJ_step4_perturb_battery.sh`, submitted with `sbatch` from `/speed-scratch/o_iseri`
after `squeue` was verified free of our GPU jobs (FINDING 2 forbids two of ours on one shared
slice). `sacct`: **COMPLETED**, ExitCode **`0:0`**, Elapsed **`03:43:00`**. Output
`/speed-scratch/o_iseri/4J_step4_perturb_1266911.out`. Eleven training runs at
`--limit-train 600`, fold `es`, scored by `4thJ_step4_perturbtable.py`, followed by the
FINDING-13 two-arm `G4.3`/`G4.12` demonstration and an md5 re-proof of `prereg.md`.

**Six gates were seen falling, each felled by its own pre-registered perturbation and by
nothing else.**

| gate | perturbation that felled it |
|---|---|
| `G4.5` | `pad_labels_1pct` |
| `G4.7` | `strip_eor_1pct` |
| `G4.9` | `sequential_countries` |
| `G4.11` | `drop_revision` |
| `G4.13` | `leak_1pct` |
| `G4.14` | `edit_prereg` |

Off-target movement was confined to `G4.6`, which was already FAIL at baseline and therefore
cannot be disturbed by anything.

🔴 **The coverage clause nevertheless returned FAIL**, and correctly:

```
  gates PASSing at baseline: ['G4.11','G4.13','G4.14','G4.2','G4.5','G4.7','G4.8','G4.9']
  never made to fall:        ['G4.2', 'G4.8']
  COVERAGE CLAUSE VERDICT: FAIL
```

**This measurement is recorded here; the rulings it triggered are the entry below and are not
applied to any number above.**

---

### 2026-08-18 — AUTHOR RULING D-S4-1: `G4.6` is measured in fp32. Route (a).

**What was measured.** `G4.6` compares logits before and after `merge_adapter()` and requires the
maximum absolute difference to fall under `1e-4`. Baseline reading: **`max_logit_diff = 13.71875`**
— a value exactly representable in bf16, which is the diagnostic giveaway.

**Why it could never pass.** LoRA leaves `W` untouched and applies `W·x + 8·(BA)·x` on the fly.
Merging writes `W + 8·BA` back into storage. The two are algebraically identical, but storage is
**bfloat16** — 8 mantissa bits, relative precision ≈ 7.8e-3 — so the write **re-rounds every
merged weight**, and across 32 layers the rounding compounds into a logit displacement of order
1–10. A float32 tolerance applied to a bf16 merge is unsatisfiable by construction.

**The control that proved it is not a code fault.** In the `freeze_adapter` row of job `1266911`,
`G4.6` reads **PASS** — the only row where it does. A frozen adapter leaves `B` at its zero
initialisation, so `BA = 0`, so `W + 0 = W`, so nothing is re-rounded and drift is exactly zero.
Train the adapter and the gate cannot pass; freeze it and it passes trivially. **The merge logic
is correct; the drift is storage rounding.**

**RULING (author, 2026-08-18): route (a).** The comparison is performed in **float32** — both
logit tensors are upcast before differencing — and the `1e-4` band is **kept, not relaxed**. This
restores what `G4.6` was written to catch, a fault in the merge arithmetic itself, with storage
rounding taken out of the picture.

**Standing consequence.** The bf16 merged-vs-unmerged displacement is a real property of
deployment and is reported as such, once, as a number. **The adapter is not merged for any result
in this paper** — `4thJ_step4_diagnostics.py` already loads it unmerged — so no reported figure
depends on the merged model.

🔴 **Not retroactive.** Every `G4.6` reading published before this ruling, including the
`13.71875` above, stands as measured. The ruling changes future measurements only.

---

### 2026-08-18 — AUTHOR RULING D-S4-2: `G4.8` asserts tokenizer identity. Route (a).

**What was measured.** The `swap_tokenizer` row reads **NOT RUN**. The run loaded
`bert-base-uncased` in place of the OLMo tokenizer, printed
**`G4.8 PASS 600/600 tokenizer round-trips exact`**, and then died in generation on
`ValueError: The following model_kwargs are not used by the model: ['token_type_ids']` — BERT
emits `token_type_ids`, OLMo's `generate` does not accept them.

**Why the crash is the smaller half.** `G4.8` encodes a record and decodes it with **the same**
tokenizer and checks the string returns. That is a self-consistency test, and self-consistency
survives substitution: any competent tokenizer round-trips its own output. The gate is
structurally blind to *which* tokenizer it holds. Repairing the crash would buy a green row that
demonstrates nothing. `G4.8` was therefore uninfellable by the battery as written — its place in
`never made to fall` is not an accident of this run.

(Incidental: our record text is lower-case ASCII throughout, so `bert-base-uncased`'s
lower-casing left no trace either. The gate had no second chance to notice.)

**RULING (author, 2026-08-18): route (a).** `G4.8` now asserts **tokenizer identity against the
base model** — the tokenizer's resolved name/path is compared with the base checkpoint's — before
performing the round-trip. A swap fells the gate on that first assertion, before generation is
reached, which also makes the `token_type_ids` crash moot rather than needing a separate repair.

🔴 **This widens what `G4.8` asserts** (identity *and* consistency, where before it asserted
consistency alone). It is recorded here as a basis change, ruled by the author, not as a
tightening applied by the implementer.

---

### 2026-08-18 — Implementer-side repairs, additive, no ruling required

Two further defects from job `1266911` are repaired without an author ruling because neither
changes what any gate asserts.

**FINDING 18 — `seen falling` was computed wrongly.** `4thJ_step4_perturbtable.py` built the
`gates seen falling` list from *"FAILs under some perturbation"* instead of *"PASSed at baseline
**and** FAILed under a perturbation"*, so `G4.6` — already down at baseline, and explicitly
excluded from the clause two lines earlier in the same report — entered the credited list for
free. The printed verdict was unaffected, since the clause is computed against the
`PASSing at baseline` set, but the printed evidence overstated itself by one gate.
🔴 **The credited count for job `1266911` is SIX, not seven.**

**`G4.2` had no perturbation at all.** `G4.2` is the format-collapse halt: it FAILs when
`delimiter_loss < 0.05` **and** generated activity entropy `< 1.5` (strict on both arms, `V4.d`) —
that is, when the model has learned the record format perfectly while emitting degenerate content.
No perturbation in the pre-registered set targeted that condition, which is why `G4.2` sits in
`never made to fall` beside `G4.8`. A `collapse_content` perturbation is added: delimiters left
intact, content replaced by a single repeated activity, which drives both arms down together.
**Adding coverage is required by the coverage clause, not a violation of the pre-registration** —
no existing `EXPECTED` row is edited.

---

### 2026-08-18 — Leg-4 fold `es` submitted, cancelled, and resubmitted so all three folds share one gate code

`sbatch 4thJ_step4_leg4_fold.sh es` was submitted as job **`1269370`** and **cancelled while still
`PENDING`, before it allocated a GPU or wrote a line of output.** Nothing was computed and nothing
is discarded.

Reason: the two rulings above change `G4.6` and `G4.8`. Had `1269370` run first, fold `es` would
have reported those gates under the old code and folds `uk` and `it` under the new. The trained
adapter would have been identical either way — neither ruling touches training — but the gate
verdicts would not have been comparable across folds. **The folds are resubmitted after the
repairs so that all three are scored by one and the same battery.**

🔴 **Standing prediction, on record before any fold is scored: Italy will be the weakest fold** —
smallest pool (31,560 records) and fewest usable strata (112 at N ≥ 100, against 166 for `es` and
168 for `uk`). `prereg.md` §8 forbids explaining this away after the fact.

---

### 2026-08-18 — Job `1270491`, read MID-RUN. Three defects, and one gate reclassified.

The repaired battery was submitted as job **`1270491`** and read line by line while running.
Four things are recorded here. Only the last needs an author ruling, and not yet.

**🟢 D-S4-2 worked on its first attempt.** The `swap_tokenizer` row printed

```
G4.8 FAIL  identity=False (holding bert-base-uncased, base allenai/OLMo-2-0425-1B)  round-trip 600/600 exact
```

The identity arm fells the gate and the round-trip arm still reads `600/600` — FINDING 17
restated as a measurement rather than an argument. **The ruling is confirmed by the run.**

**🔴 FINDING 19 — the gate fell and the run threw the evidence away.** Four lines later the run
died at the first generation call on the same `ValueError: ... ['token_type_ids']`. Because
`detectors_<run>.json` is written only in the last block of `main()`, the `G4.8 FAIL` that had
just been scored was discarded and the row read `NOT RUN` for a second battery. **The battery
cannot distinguish "the gate was never felled" from "the gate was felled and the run died
afterwards" — both print `NOT RUN`, and only one of them is a success.** This applies to every
gate scored before any crash, in any run. Repaired additively: the `detectors` dict is handed to
a module global and flushed by a top-level handler, marked `crashed`, with gates never reached
left **absent** rather than written `PASS`. The exception is re-raised, so the job still exits
non-zero. No ruling — nothing changes what a gate asserts.

**🔴 FINDING 20 — `collapse_content` did not fell `G4.2`, and the perturbation was mis-designed.**
`[epoch 0] delim=1.7315 content=8.7335 entropy=0.000 G4.2 PASS`. The entropy arm crossed
perfectly; the delimiter arm went the **wrong way**, `0.109 → 1.73` against a `< 0.05` band.
`V4.d` requires both arms, so PASSing was correct. Cause: the delimiter loss is measured on the
**held-in, unperturbed** validation loader, so flattening the durations as well as the activities
trained the model off the real record distribution and made it *worse* at real delimiters — the
opposite of the "format learned perfectly, content degenerate" condition the halt encodes.
Redesigned to collapse **only `ACT`/`ACT2`**, leaving `DUR`/`LOC`/`COP` real. No ruling — this is
a defect in a perturbation, not in a gate.

**🔴 FINDING 21 — `G4.6` is right about the cause and still fails. AUTHOR RULING PENDING.**
Baseline `max_logit_diff` moved **`13.71875` (bf16) → `3.204e-04` (fp32)** against the unchanged
`1e-4` band; the other rows read `2.480e-04`, `2.861e-04`, `3.009e-04`, `3.033e-04` and
`8.469e-04`. **D-S4-1's diagnosis is confirmed: bf16 storage rounding was ~99.998 % of the
drift.** The gate nevertheless fails by ~3×. A residual of `3e-4` on logits of order 10 is
~`3e-5` relative — the scale of fp32/TF32 matmul accumulation-order noise on an A100 — so the
band may sit below the hardware's own reproducibility floor, which would make `G4.6`
unsatisfiable for a second and entirely different reason.

🔴 **The band was NOT touched.** The decisive control is added instead and is reported beside the
verdict: the maximum absolute difference between **two identical unmerged forward passes**, same
weights, same inputs, same mask, same reduction, both taken *before* `merge_adapter()`. The
reading rule is printed with it — floor `>= 1e-4` means the band is the thing to rule on; floor
`~0` means the `3e-4` is a real merge property to report. **Measured first, ruled second.**

**🔴 FINDING 22 — `G4.2` is a model-quality gate and was mis-classified. Pre-registered here
BEFORE the demonstration is run.** The same job pins the clean delimiter loss at **`0.1094`** to
four decimal places across five different perturbations (`null`, `pad_labels_1pct`,
`perturb_merged_weight`, `strip_eor_1pct` `0.1096`, `drop_revision` `0.1095`). Four decimals of
agreement across five different training runs is a **floor**, not a coincidence: at 600 records
and 2 epochs the model has learned the format as well as this budget allows. `G4.2`'s first arm
needs `delim < 0.05` — a factor of **2.2 below the floor**. The FINDING 20 repair moves that arm
in the right direction and cannot reach the band, because the arm is not a statement about the
perturbation at all. **`G4.2` therefore belongs with `G4.1`, `G4.3`, `G4.4` and `G4.12` in
FINDING 16's model-quality class.**

Remedy, two arms, for the same reason the FINDING-13 `G4.3`/`G4.12` demonstration has two — one
arm cannot separate *the perturbation fell the gate* from *the budget fell the gate*:

| arm | training | EXPECTED |
|---|---|---|
| ctrl | `--limit-train 4000`, no perturbation | `G4.2` **PASS** — delim below 0.05, entropy ~2.8 |
| collapse | `--limit-train 4000 --perturbation collapse_content` | `G4.2` **FAIL** — delim below 0.05, entropy ~0.000 |

🔴 **If the ctrl arm's delimiter loss does not cross `0.05` at 4,000 records the demonstration is
VOID and is reported VOID** — the collapse arm failing would then show nothing — and `G4.2` moves
to the Leg-4 folds. Declared in advance so it cannot later be presented as a result. The
demonstration writes to a **separate run directory**; sharing `runs_perturb` would overwrite the
600-record `collapse_content` row and score one row of the main table at a different budget from
the other ten.

**No band is touched and no `EXPECTED` row is edited by any of the above.** FINDING 22 changes
*where* `G4.2` is scored, not what it asserts.

🔴 **Sequencing, on record.** All repairs above were written while `1270491` was still running and
**deliberately not shipped.** The battery re-reads `4thJ_step4_train.py` for every remaining
perturbation, so copying a new file to Speed mid-run would have scored one battery under two code
versions — the exact defect the fold-`es` cancellation was made to avoid.

---

## 2026-08-18 — job `1270491` returned. FINDING 23.

`1270491` finished its eleven perturbations and scored them. The table is a **line-for-line
reproduction of job `1266911`**, which is the useful result: it is the pre-repair baseline, taken
under the code that was on Speed, and it confirms that all four repairs written since are still
required and none of them was silently already in effect.

```
never made to fall:   ['G4.2', 'G4.8']        COVERAGE CLAUSE VERDICT: FAIL
swap_tokenizer        NOT RUN                  <- FINDING 19, the verdict died with the run
collapse_content      DID NOT FELL ITS GATE    <- FINDING 20 / 22, G4.2 PASS
perturb_merged_weight VOID                     <- FINDING 18, now printing honestly
freeze_adapter        G4.6 PASS                <- FINDING 15, BA = 0 so drift is exactly zero
prereg.md md5         e4243e07cdd80c9c846b91f40e3e8c45, matches the sidecar
FINDINGS: 0
```

### 🔴 FINDING 23 — the STAY CLEAN check had no baseline condition either

Three rows printed a violation that did not happen:

```
pad_labels_1pct   was required to STAY CLEAN and did not: G4.6 = FAIL
drop_revision     was required to STAY CLEAN and did not: G4.6 = FAIL
edit_prereg       was required to STAY CLEAN and did not: G4.6 = FAIL
```

None of those three perturbations touches `G4.6`. It was already `FAIL` at baseline — the same
report says so eleven lines earlier, under `EXCLUDED FROM THE COVERAGE CLAUSE`. The STAY CLEAN loop
in `4thJ_step4_perturbtable.py` tested only `v[g] != PASS`, with no reference to `base`, so any gate
that is down at baseline is reported as freshly dirtied by every perturbation that lists it as a
clean-check. This is **the exact twin of FINDING 18**, in the other half of the same function:
FINDING 18 was the missing baseline condition on the *target* arm, FINDING 23 is the missing baseline
condition on the *collateral* arm. Repairing one and not the other left the report half-honest.

**Verdict unaffected** — this loop never appends to `findings`, and `FINDINGS: 0` was correct. What
was wrong is the printed evidence, in three rows out of eleven, in the direction that invents
collateral damage. A reader auditing this table would have concluded that three unrelated
perturbations each broke the merge-drift gate.

**Fixed additively.** A gate that does not PASS at baseline now prints
`NOT ASSESSABLE as STAY CLEAN -- already <verdict> at baseline. Stated, not silently dropped.`
rather than either a false violation or silence. No `EXPECTED` row was edited and no band moved.
`4thJ_step4_perturbtable.py` is now 237 lines, md5 `df47f30e42ea215d5afae686ed46dc4a`, `py_compile`
clean. Pre-repair copy kept at `scratchpad/perturbtable_pre_f23.py`.

**Method note, not a project defect.** The background watcher on `1270491` reported the job had left
the queue when in fact `ssh` had dropped the connection and returned an empty state string; the
until-loop read "not RUNNING" as "finished". A poller that treats an unreachable host as a completed
job is the same failure shape as a gate that treats `NOT CHECKED` as a pass. The job was still
`RUNNING` at 02:57:46 and was verified directly with `sacct` before anything was acted on.

---

## 2026-08-18 — job `1270491` finished: the FINDING 13 two-arm demonstration is **VOID**, as pre-registered

`sacct`: `1270491 COMPLETED 04:01:57 0:0`. Both arms of the `G4.3` / `G4.12` demonstration ran to
completion on the same 600-record cap. The numbers, read from
`/speed-scratch/o_iseri/4J_step4_perturb_1270491.out` lines 734–748 (`ctrl`) and 771–785 (`nopfx`):

| gate | reading | `ctrl` arm | `nopfx` arm | band |
|---|---|---|---|---|
| `G4.3`  | CE true / permuted / rise | 0.6779 / 0.6967 / **+0.0188** | 0.7495 / 0.7491 / **−0.0004** | rise ≥ 0.15 |
| `G4.12` | CE rise                   | **+0.0023**                   | **−0.0008**                   | ≥ 0.15 |
| `G4.12` | MI drop                   | **+0.015**                    | **−0.085**                    | ≥ 0.10 |
| `G4.4`  | evening / morning ratio   | 0.494 / 0.202 → **FAIL**      | 2.279 / 0.819 → **PASS**      | reported separately |

**`G4.3` and `G4.12`: the direction is right, the magnitude is not.** Removing the prefix collapses
the `G4.3` conditioning signal from `+0.0188` to `−0.0004` — a factor of roughly 47 — and flips both
`G4.12` readings from positive to negative. That is exactly the direction the demonstration
predicted. But **both arms FAIL the band**, so the `ctrl` arm cannot serve as a baseline, and a
demonstration whose control is already down demonstrates nothing. This is the fallback that was
declared in advance, in the battery comment, before the run:

> *"one arm cannot separate 'the perturbation fell the gate' from 'the budget fell the gate'"*

and it is being reported as the comment said it would be. **`G4.3` and `G4.12` are therefore NOT
credited by this battery.** They move to the Leg-4 folds, where the training budget is two orders of
magnitude larger. Nothing in the `EXPECTED` table was edited; the pre-registered rows still read
`FAIL` / `FAIL`, and they did read `FAIL` — the defect is that the control read `FAIL` too.

This is the second time the same shape has bitten in two days: **a verdict is only meaningful
relative to that gate's own baseline** (FINDING 18 on the target arm, FINDING 23 on the collateral
arm, and now the demonstration's control arm). It is worth saying plainly that the principle keeps
being rediscovered in new places rather than applied once.

### FINDING 24 — `G4.4` reads *better* on the arm trained with no prefix, so its 600-record readings carry no signal

`G4.4` is a diurnal-shape gate: it checks that generated diaries put activity in the evening and the
morning in roughly the proportions the reference set does. On the two arms above it read:

* `ctrl`  (prefix present, 600 records) — evening **0.494**, morning **0.202**, **FAIL** on both
* `nopfx` (prefix stripped, 600 records) — evening **2.279**, morning **0.819**, **PASS** on both

The arm that was *deliberately deprived of every conditioning signal in the corpus* produced the
better-shaped day. There is no mechanism by which removing the prefix improves the diurnal profile,
so this is not a result about prefixes; it is evidence that **at 600 records `G4.4` is reading
sampling noise in the generator, not a property of the model**. `G4.4` was never part of the
FINDING 13 demonstration — it belongs to `4thJ_step4_genperturb.py`'s `EXPECTED` map and is scored
on the Leg-4 folds — so no credited verdict changes. What changes is that **no `G4.4` reading taken
at the 600-record budget may be quoted anywhere**, in either direction, including the `ctrl` arm's
`FAIL`. Both are recorded here and both are marked uninterpretable.

This also strengthens FINDING 16 and FINDING 22: the list of gates that cannot be demonstrated
against an undertrained model is now `G4.1`, `G4.2`, `G4.3`, `G4.4`, `G4.12`.

### Shipped and re-launched

The queue was confirmed empty (`squeue -u o_iseri` → header only, and zero of our GPU jobs) before
anything was written to `/speed-scratch`, because `bash` reads a running script by byte offset and
overwriting the battery mid-run can corrupt it. Three files shipped, md5 verified on **both** sides:

| file | lines | md5 | Speed held before |
|---|---|---|---|
| `4thJ_step4_train.py`           | 1505 | `661b11e74ac38b9d29ecc5d875cc87fc` | 1360 |
| `4thJ_step4_perturb_battery.sh` | 150  | `a2d99e15f7264e0398edb4256f4df27d` | 108 |
| `4thJ_step4_perturbtable.py`    | 237  | `df47f30e42ea215d5afae686ed46dc4a` | 221 |

`1270491`'s scoring table was copied to `perturb_table_train_side_es_1270491.txt` first — the re-run
writes to the same path and the old evidence would otherwise have been lost silently.

**Re-run submitted: job `1274838`.** It carries FINDING 19 (crash-flush, so `G4.8` is credited when
`swap_tokenizer` dies), FINDING 20 (`collapse_content` redesigned to collapse only `ACT`/`ACT2` and
`fail()` on an empty flatten), FINDING 21 (the `G4.6` noise floor: two identical unmerged passes
before `merge_adapter()`), FINDING 22 (the 4000-record two-arm `G4.2` demonstration, which Speed's
108-line copy did not contain at all), and FINDING 23 (the honest STAY CLEAN report).

---

## 2026-08-18 — FINDING 21 RESOLVED BY MEASUREMENT: the noise-floor hypothesis is **refuted**, and `G4.6`'s drift is real

Job `1274838`, null baseline, printed the control FINDING 21 was written to obtain:

```
G4.6 FAIL  max_logit_diff=2.498e-04 threshold=1e-04 over 20103 positions
     G4.6 repeat-noise floor=0.000e+00 (two IDENTICAL unmerged forward passes;
     tf32 matmul=False cudnn=True). drift/noise=n/a. floor is BELOW the band, so
     the band is resolvable here and the drift is a real signal, not accumulation noise
```

**The floor is exactly `0.000e+00`.** Two identical unmerged forward passes over 20,103 positions
agree bit-for-bit. TF32 is off for matmul. So the instrument is sharp far beyond the `1e-4` band,
and the hypothesis I raised in FINDING 21 — *that the band might sit below the hardware's own
reproducibility floor* — **is wrong, and is recorded as wrong.** It was a reasonable hypothesis and
it took one control to kill it. That is what the control was for.

**This removes the only argument that could have justified re-banding `G4.6`, so the band stays at
`1e-4` and no ruling is needed on that question.** I had queued FINDING 21 as the author's one open
decision; the measurement has answered it instead, in the direction that keeps the band.

### What the residual actually is

With the floor at zero, the `2.498e-04` has to come from the merge itself. Three readings now bracket
the mechanism, and they agree:

| condition | adapter delta | merged-vs-unmerged logit drift |
|---|---|---|
| `freeze_adapter` (FINDING 15 control) | `BA = 0` exactly | `0` → **PASS** |
| trained baseline, bf16 comparison | `BA ≠ 0` | `13.71875` → FAIL |
| trained baseline, fp32 comparison (D-S4-1) | `BA ≠ 0` | `2.5e-4`–`3.2e-4` → FAIL |
| two identical passes, no merge at all | — | `0.000e+00` |

D-S4-1 moved the *comparison* to float32. It did not move the *storage*: the model is loaded in
bfloat16, so `merge_adapter()` computes `W + (α/√r)·BA` and writes the result back into bf16, which
re-rounds every weight it touches. bf16 carries 8 mantissa bits, relative eps ≈ `7.8e-3`. That
rounding is **deterministic quantisation, not noise** — which is exactly what a zero noise floor
proves. `freeze_adapter` closes the argument from the other side: when the delta is exactly zero,
`W + 0` rounds to itself and the drift is zero.

So `G4.6` at `1e-4` is unsatisfiable for **any** adapter that actually trained, and satisfiable only
for one that did not. **The gate as banded rewards a frozen adapter and penalises a trained one.**
That is a statement about the gate, and it is now supported by four measurements rather than by an
argument.

🔴 **The remaining question is a BASIS question, not a band question, and it is the author's.**
Per the standing rule — *additive fixes only; basis changes are band changes* — I am not touching it.
The options, stated neutrally:

* **(a)** Keep the band at `1e-4` and report `G4.6` as a **standing, explained FAIL**: the mechanism
  is bf16 storage quantisation of the merge, documented with the four readings above and the
  `freeze_adapter` control. Nothing is hidden and nothing is relaxed. Cost: `G4.6` never passes and
  `perturb_merged_weight`, the perturbation written to fell it, stays VOID for the whole project.
* **(b)** Upcast the weights to float32 **for the merge** and compare there, so the gate measures
  merge *arithmetic* rather than merge *storage*. This is a change of basis: it asks a different
  question than the pre-registered one, and it would need the `EXPECTED` row re-stated as such
  rather than silently reinterpreted.

**No band is being moved and no `EXPECTED` row has been edited.** Recorded here so the choice is made
on the record with the numbers already in hand.

### Two smaller readings from the same block

* **`delim=0.1094` again**, at epoch 1 of a fresh baseline in a new job. Third independent
  reproduction of the training floor behind FINDING 22. `G4.2`'s first arm needs `< 0.05`; the
  600-record budget cannot reach it. The 4000-record demonstration later in this same job is the
  test of whether any budget we can afford reaches it.
* **`max_logit_diff` moved between jobs**: `3.204e-04` in `1270491`, `2.498e-04` in `1274838`, same
  baseline configuration. With the forward pass proven bit-deterministic, that difference can only
  come from **training** not being bit-reproducible across jobs — non-deterministic backward kernels
  and/or dataloader ordering. This is expected for CUDA training and is **not** claimed as a defect;
  it is recorded because it means `G4.6`'s exact value is not a fixed constant of the recipe, only
  its order of magnitude is, and no future entry should quote one of these two numbers as *the*
  drift.

---

## 2026-08-19 — job `1274838` closed: **`G4.8` is credited, coverage is 7 of 8, and `G4.2` is the last gate standing**

`sacct`: `1274838 COMPLETED 05:08:01 0:0`.

### Three repairs confirmed by the table, not by assertion

**FINDING 19 — FIXED, and it is the substantive win of this battery.** The `swap_tokenizer` row now
reads `G4.8 FAIL` instead of `NOT RUN`. The crash-flush writes `detectors_<run>.json` before the
`token_type_ids` `ValueError` kills the run, so the gate that had already been felled is no longer
discarded with the process. The row's honesty is visible in the same line: `G4.2`, `G4.6`, `G4.9` and
`G4.11` print `-`, because the run died before those gates were reached. A partial row that says
which gates it did and did not reach is worth more than a whole row that never appears.

**`gates seen falling` went from six to SEVEN**: `G4.5 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14`.

**FINDING 23 — FIXED, visible three times.** `pad_labels_1pct`, `drop_revision` and `edit_prereg`
each now print `G4.6 NOT ASSESSABLE as STAY CLEAN -- already FAIL at baseline. Stated, not silently
dropped.` The three invented collateral-damage claims are gone and nothing was silently suppressed
in their place.

**FINDING 18 — still holding.** `perturb_merged_weight` prints `VOID` with the reason attached, and
is not counted as seen falling.

**FINDING 15 control — still holding.** `freeze_adapter` is the only row where `G4.6 PASS`.

### FINDING 22's demonstration is **VOID — exactly as pre-registered, and for the pre-registered reason**

The battery comment, written before the run:

> *"If the CTRL arm's delimiter loss does not fall below 0.05 at 4,000 records, this demonstration
> is VOID and is reported VOID … That fallback is declared HERE, in advance, so it can never be
> presented afterwards as though it were a result."*

It did not fall below 0.05:

| arm | budget | epoch 0 | epoch 1 | entropy | `G4.2` |
|---|---|---|---|---|---|
| clean | 600 | `delim=0.1094` | — | 2.892 | PASS |
| clean | **4000** | `delim=0.1084` | **`delim=0.1022`** | 3.011 | PASS |
| collapse (redesigned) | 600 | `delim=0.5657` | `delim=0.5024` | **0.000** | PASS |
| collapse (redesigned) | **4000** | `delim=0.5750` | `delim=0.7342` | **0.000** | PASS |

**VOID. Reported VOID.** `G4.2` stays in `never made to fall` and is now the *only* entry there.

### FINDING 25 — `G4.2`'s first arm is not a perturbation target, it is a **precondition our model never meets**

This is the diagnosis the two-arm demonstration was for, and it is worth more than the demonstration
would have been had it succeeded.

`G4.2` halts on `delimiter_loss < 0.05` **AND** `gen_entropy < 1.5`, strict on both arms (`V4.d`).

* **The second arm is not the problem. It is nailed, everywhere.** The redesigned
  `collapse_content` (FINDING 20) drives `gen_entropy` to **`0.000`** at both budgets and both
  epochs. As a lever on arm two it is perfect. FINDING 20's redesign also did what it was meant to:
  the old design put delimiter loss at `1.7315`, the redesign puts it at `0.5024` — a 3.4×
  improvement — because it now collapses only `ACT`/`ACT2` and leaves durations alone.
* **The first arm is never satisfied — not by the perturbation, and not by the CLEAN model either.**
  The best delimiter loss this project has ever produced is `0.1022`, a factor of **2.0 above** the
  arm it must cross. No perturbation is responsible for that; the clean baseline does it.

**Two consequences, and the second is the serious one.**

**(1) The arms are in mechanical opposition under any training-side content perturbation.**
`delimiter_loss` is measured on the **held-in, unperturbed** validation set. Any perturbation strong
enough to drive generated entropy to zero does so by destroying content in *training*, which makes
the model worse on *real* data — so it pushes arm one **away** from its band while pushing arm two
into it. Every reading above shows this: entropy `2.9 → 0.000` costs delimiter loss `0.10 → 0.50`.
A training-side perturbation cannot satisfy both arms at once, and this is structural, not a tuning
problem.

**(2) The budget is not closing the gap, and extrapolation says it never will.** From `600 → 4000`
records — a 6.7× increase — delimiter loss moved `0.1094 → 0.1022`, i.e. **6.6 %**. Fitting the only
two points available as a power law gives an exponent of about `0.036`, on which:

* the full Leg-4 fold (58,801 records, 14.7× the 4000 run) would reach about **`0.093`**, still ~1.9×
  above the band;
* reaching `0.05` would need on the order of **10^12** records — roughly seven orders of magnitude
  beyond the entire corpus.

**A two-point power-law fit is a weak instrument and is not being presented as a precise
forecast.** The exponent could be off by a factor of several and the conclusion would not change:
the gap is not closing at anything like the rate needed. **The `es` fold now running (job `1274884`,
full 58,801 records) will replace this extrapolation with a measurement, and that measurement is
what should be quoted — not the fit above.**

**If the fold confirms it, `G4.2` cannot be felled at any budget available to this project, and
the reason is a gate-design question for the author, in the same class as `G4.6`.** Stated neutrally,
without a recommendation and without touching anything:

* **(a)** Report `G4.2` as **permanently NOT DEMONSTRABLE**, with the mechanism above on the record —
  the coverage clause then closes at 7 of 8 with one stated, explained exception, the way `G2.10` was
  handled in Step 2. Honest, and costs one gate's worth of evidence.
* **(b)** Fell arm two only, via a **generation-side** lever in `4thJ_step4_genperturb.py` (degenerate
  decoding on an otherwise intact adapter), and re-state `G4.2` as a gate whose arms are demonstrated
  **separately** rather than jointly. This is a change to what the gate claims, so it is a basis
  change and needs the ruling.
* **(c)** Re-base arm one on the model's own clean floor rather than an absolute `0.05`.
  **I flag this one against itself:** it is a band change justified by our own artefact failing,
  which is the exact move the project forbids. Listed only so it is on the record as considered and
  rejected, not omitted.

**Nothing has been edited. No band moved, no `EXPECTED` row touched.**

### FINDING 26 — `collapse_content` also fells `G4.9`, and the table caught it unprompted

At 4000 records the attribution block printed:

```
collapse_content   DID NOT FELL ITS GATE target G4.2 -> PASS
                   UNEXPECTED FALL -- FINDING: also moved ['G4.9']
```

`G4.9` is the forgetting gate. Training two epochs on a corpus whose activity content has been
flattened to a single constant should indeed cause measurable forgetting, so the fall is
*mechanistically unsurprising* — but it was **not pre-registered**, and the perturbation was declared
as a single-gate lever. The table flagged it without being asked, which is the collateral-damage
check working as designed. Recorded because a perturbation with an undeclared second effect is not a
clean instrument: if `collapse_content` is ever used to credit `G4.2`, this row has to be quoted
alongside it. It did **not** fire at the 600-record budget, only at 4000 — consistent with the
forgetting being real and dose-dependent rather than a scoring artefact.

### Next

Leg-4 fold `es` submitted as job **`1274884`** (full 58,801 records, named GPU profile
`nvidia_a100_2g.20gb`, GPU verified free of our jobs first, one at a time per FINDING 2). It is the
only route to `G4.1`, `G4.3`, `G4.4` and `G4.12`, and it will settle FINDING 25's extrapolation with
a real delimiter-loss reading at full budget.

**CORRECTION, same day.** I wrote job `1274884` as running on "full 58,801 records". Wrong number for a
fold: 58,801 is the whole training portion of the corpus after the 6,533 held-out households are
removed. Fold `es` holds `es` OUT, so its training set is `it` + `uk` = **48,594** records
(`by_country={'it': 34366, 'uk': 14228}`), held-in validation 5,520. The startup gates all read
clean on that set: `G4.14 PASS`, `G4.13 PASS` (0 held-out-country records in train), `G4.7 PASS`
48,594/48,594, `G4.8 PASS` identity + round-trip 1000/1000 exact, `G4.5 PASS` 2,980,205 pad positions
0 unmasked. Loss 2.0767 -> 0.8448 by step 200. The FINDING 25 extrapolation should therefore be read
against **12.1x** the 4000-record run, not 14.7x; the fitted prediction moves from ~0.093 to ~0.094,
which changes nothing about the conclusion and is corrected here only because the number was quoted.

---

## 2026-08-19 — INVESTIGATION BEFORE THE TWO RULINGS. TWO FINDINGS. NOTHING TOUCHED.

The author asked for the two open gate-design questions to be investigated rather than ruled blind.
No gate code, no band, no `EXPECTED` row and no spec was edited. What follows is measurement.

### 🔴 FINDING 27 — the `G4.6` question as posed is a NO-OP: option (b) is ALREADY IN FORCE

Every entry so far has said that D-S4-1 "moved the COMPARISON to fp32 but not the STORAGE — the model
is loaded bf16, so `merge_adapter()` writes `W + 8BA` back into bf16 and re-rounds every weight."
**That is not what the shipped code does.** `4thJ_step4_train.py` (1505 lines, md5
`661b11e74ac38b9d29ecc5d875cc87fc`, byte-identical on Speed) calls **`model.float()` at line 1283,
BEFORE the measurement loop** — `nn.Module.float()` upcasts *every* floating parameter and buffer,
base weights and LoRA `A`/`B` alike. `base.merge_adapter()` at line 1317 therefore adds the delta into
**float32 storage**, not bf16, and the dtypes are restored in the `finally` block afterwards.

The evidence is in the numbers already on the record: had only the *comparison* moved to fp32, the
baseline could not have fallen `13.71875 -> 3.204e-04`. Logits were cast with `.logits.float()` in
both code versions; the four-order-of-magnitude drop IS `model.float()` taking effect on the weights.

**So the ruling offered as (b) — "upcast weights to fp32 for the merge" — would change nothing.**
It was implemented on 2026-08-18 as part of D-S4-1 and it is what produced the `2.5e-4` residual. The
decision as written cannot be taken; it must be re-posed against what the residual actually is.

### 🔴 FINDING 27b — the repeat-noise floor is the WRONG CONTROL, so FINDING 21's conclusion does not follow

FINDING 21 measured `repeat_noise_floor = 0.000e+00` (two identical unmerged forward passes) and
concluded, in the line the battery prints, *"the band is resolvable here and the drift is a real
signal, not accumulation noise."* **The control does not support that.** Two identical calls run the
same kernels over the same tensors in the same reduction order; on a deterministic GPU path they are
bit-identical **by construction**, and a floor of exactly zero is the expected result of a check that
cannot fail. It bounds *run-to-run* nondeterminism. It says nothing about the quantity `G4.6`
actually measures, which is the difference between **two different computation graphs**:

* unmerged: `x·W  +  s·((x·A)·B)`  — one full GEMM, one rank-32 path, one add
* merged:   `x·(W + s·BA)`         — one full GEMM on a different matrix

These are algebraically equal and numerically **re-associated**. In fp32 the reassociation error is
proportional to the magnitude of the delta folded in and compounds with depth. That is the only
candidate left for the residual once bf16 storage is excluded (FINDING 27) and run-to-run
nondeterminism is excluded (floor = 0), and **it is not a merge fault** — it is the arithmetic cost
of merging at all.

Supporting reading, from job `1274838`'s eleven runs: `max_logit_diff` = `2.498e-04`, `2.995e-04`,
`3.347e-04`, `3.283e-04`, `3.128e-04`, `3.262e-04`, `4.749e-04`, `3.220e-04` … — it clusters in one
narrow band across perturbations that have nothing to do with the merge, and it does not track
anything the perturbations did. A statistic that lands on the same number regardless of the
treatment is measuring the arithmetic, not the treatment. Note also that `perturb_merged_weight`'s
`1e-3` nudge reaches only `4.7e-4` against a `2.5e-4` baseline — **the lever and the floor are the
same order of magnitude**, so even a re-banded `G4.6` would demonstrate weakly.

**The decisive experiment, NOT run and NOT proposed as a fix — an α-sweep.** Scale the trained
adapter's `B` by α ∈ {1, 0.1, 0.01, 0.001}, merge, measure, unmerge, restore. If `max_logit_diff`
falls linearly with α, the residual is reassociation of the delta and `G4.6`-as-banded is
unsatisfiable for any adapter that trained. If it plateaus, there is a constant floor to name. Either
outcome is a number instead of an argument, it is additive, and it runs in minutes against the
adapter already saved in `runs_perturb/leg4_perturb_fold_es/adapter`.

Standing fact that bears on the ruling: **no result in this paper uses a merged adapter** (the gate's
own `basis_note` says so, and decision 16's clause forbids releasing weights), so `G4.6`'s verdict has
no downstream consumer. The bf16 figure `13.71875` remains the honest number for a hypothetical merged
*deployment* and should be reported as such if it is reported at all.

### 🔴 FINDING 28 — `G4.2` arm one is 96 % consumed by ONE token that is content, not format

Measured directly from `4J_step3_corpus.jsonl`, **md5 `ca89d2295603c547f2384a40dd1909ba`, which is the
`corpus_md5` in the fold-`es` run manifest** — the same bytes the trainer read. Read-only analysis on
the author's desktop; scripts shipped as `tools/4thJ_step4_g42_delim_decomposition.py`,
`tools/4thJ_step4_g42_act2_floor.py`, `tools/4thJ_step4_g42_percountry.py`.

`DELIM_CHARS = {',', ';', '|'}` and `delimiter_token_ids()` takes every token whose decoding is
entirely delimiter characters — **which includes the two-comma token `,,`**. In this record format an
absent `ACT2` is written as two adjacent commas. So the question *"did this respondent record a
secondary activity?"* is answered **inside the delimiter bucket**, and `G4.2`'s first arm charges the
model for failing to predict it.

**That `,,` is really one token, confirmed without a tokenizer.** The detector reported
`delimiter_tokens = 675169` over the 5,520 held-in validation records = **122.3 per record**. The
`uk`+`it` mix averages 29.15 episodes per record. Five standalone delimiters per episode predicts
145.8; `,,`-merged predicts `(5 − 0.747) × 29.15 = 124.0`. Measured 122.3.

**How much of the 0.1094 is irreducible.** `P(act2 empty | context)` fitted on 80 % of the `uk`+`it`
records and scored on the held-out 20 %, Laplace-smoothed, backoff on unseen contexts:

| conditioning | nats per empty-`act2` token | nats per delimiter token | vs the `< 0.05` band |
|---|---|---|---|
| marginal | 0.2934 | **0.0515** | over |
| (country) | 0.2928 | **0.0513** | over |
| (country, act) | 0.2740 | **0.0480** | under, by 4 % |
| (country, act, loc) | 0.2730 | **0.0479** | under |
| (country, act, loc, dur band) | 0.2718 | **0.0477** | under |

**An oracle that predicts `act2` presence as well as the data allows still spends 0.048 of the 0.05
band on that one token.** Everything else in the format — 3.5 delimiter tokens per episode — would
have to be predicted at essentially zero loss to leave the arm satisfiable, and richer conditioning
does not help: marginal to full context moves it 7 %, because the decision is genuinely stochastic.

**This supersedes FINDING 25's diagnosis while confirming its verdict.** The power-law fit said
`0.05` needs ~10^12 records. The reason is not that the model is undertrained: **no quantity of data
closes the gap, because the residual entropy is in the corpus, not in the model.** Quote FINDING 28,
not the fit.

Two smaller terms measured on the way, both far below the `act2` term and both listed so the
decomposition is complete: the `DUR`-terminating comma carries 0.0192 nats and the `COP`-terminating
semicolon 0.0914 nats *at character level* — and both vanish if multi-digit numbers are single
tokens, which the content-token census (5.35 content tokens per episode) says they mostly are. The
`ACT`-terminating comma (always 3 fixed digits), the `LOC`-terminating comma (5 closed values, none a
prefix of another) and all six prefix delimiters are structurally forced and cost ~0 — and the prefix
ones are masked `-100` as prompt anyway, so they never enter the bucket.

### What is NOT claimed

Re-pointing the delimiter mask off the `act2` slot would make arm one **satisfiable in principle**; it
would not make it pass. Removing the `act2` token's share leaves ~0.26 nats over ~3.5 tokens per
episode ≈ **0.075**, still above `0.05`, and that arithmetic assumes the model matches the oracle on
`act2`, which is unmeasured. The honest next measurement is a delimiter-loss split **by token id**,
which is additive, changes no band, and needs one short scoring pass against the saved adapter.

---

## 2026-08-19 — BOTH RULINGS TAKEN. D-S4-3 AND D-S4-4.

### D-S4-3 — `G4.6`: measure the residual, then rule

Ruled (a) on the re-posed question: **the α-sweep runs first and nothing is decided until it
reports.** Band untouched at `1e-4`; `G4.6` remains a standing FAIL in the meantime.

`tools/4thJ_step4_g46_alpha_sweep.py` (+ `.sh`, 2 h walltime, named GRES). It scales every `lora_B`
by α ∈ {1, 0.1, 0.01, 0.001, 0, 1}, merges, measures the gate's own statistic, unmerges and restores.
It draws **the same sample the gate draws** — `random.Random(TH.SEED)`, `TH.G4_6_SAMPLE_N`, same
truncation — so the α = 1 row is directly comparable with the `max_logit_diff` already on the record
instead of being a second, differently-drawn number. Two controls are built in:

* **α = 0 must return exactly `0.0`.** `B = 0` makes `W + 0 = W` bitwise. This reproduces the
  `freeze_adapter` result from the other direction, and anything else means the *script* is wrong.
* **α = 1 is measured twice, first and last.** `(W + Δ) − Δ` is not bitwise `W` in floating point, so
  a sweep that merges and unmerges repeatedly can contaminate its own later rows. The repeat says by
  how much; if the two α = 1 rows disagree by anything near the effect, the sweep is **inconclusive
  and reported as such**, not averaged.

Reading, pre-registered here before it runs: **`drift/α` roughly constant** ⇒ the residual is the
delta's own re-association error, it scales with how much the adapter learned, and `G4.6` at `1e-4`
is unsatisfiable for any adapter that trained — satisfiable only for one that did not. **`drift`
roughly constant instead** ⇒ there is a floor with nothing to do with the adapter, and that floor is
the number a band should be ruled against. The script writes a JSON and stops; it moves no band and
re-points no gate.

🔴 **NOT SUBMITTED.** It needs the GPU and fold `es` (`1274884`) has it. One GPU job at a time
(FINDING 2).

### D-S4-4 — `G4.2`: the first arm is re-based onto forced delimiters. Band unchanged.

Ruled: exclude any delimiter token containing `,,` — the empty-`ACT2` slot — from the arm.
`G4_2_DELIM_LOSS_HALT` stays `0.05`. Registered in `4thJ_04_finetuneLLM_val.md` **before** the run
that reports under it, with its perturbation row and its VOID condition, and marked there as chosen
after seeing the data.

**The premise was measured, not inferred — job `1274891`, `COMPLETED 00:00:38`, CPU only.**
FINDING 28 reached "`,,` is one pure delimiter token" arithmetically (122.3 delimiter tokens per
record against 124.0 predicted merged and 145.8 standalone), and a third explanation fitted the same
count: delimiters fusing with adjacent digits into tokens that are not pure delimiters at all, which
would have put the `act2` decision in the **content** bucket and made D-S4-4 aimed at nothing. The
census settles it on the tokenizer itself:

| id | decodes to | count | per record |
|---|---|---|---|
| 11 | `','` | 21,591 | 71.97 |
| 26 | `';'` | 7,988 | 26.63 |
| **10856** | **`',,'`** | **5,982** | **19.94** |
| 91 | `'|'` | 300 | 1.00 |

300 records, 8,288 episodes, **5,982 empty-`ACT2` episodes — and 5,982 occurrences of id 10856,
ratio 1.0000.** One `,,` token per empty slot, exactly as FINDING 28 asserts. Eleven further pure
delimiter ids exist in the vocabulary (`';;'`, `',,,'`, `';,'`, …) and every one occurs **zero**
times. Pure-delimiter tokens 119.54 per record here against the detector's 122.3 on the full 5,520
— consistent, the sample runs 27.63 episodes per record against the fold's 29.15.

**A second thing the census found, unprompted and left alone.** Some delimiters are *already* fused
with what follows and are therefore *already* scored as content: `',private'` 355, `';<'` 300 (one
per record — the final `;` before `<eor>`), `',c'` 209, `',s'` 188, `',f'` 145, `',m'` 130, `',h'`
45, `'+,'` 25 (the `75+` age band). About 3 % of delimiter characters. This is pre-existing, it
predates every ruling here, and **nothing was changed to tidy it** — it is recorded because it means
the delimiter bucket has never been the complete set of delimiters, and any future re-point has to
start from that fact rather than from the val doc's narrative.

**What changed in code** (`tools/4thJ_step4_train.py`, 1505 → 1614 lines, md5
`661b11e74ac38b9d29ecc5d875cc87fc` → `610cd7659001ffe4aaa6720a99ea90a2`):

* new `forced_delimiter_token_ids()` — drops any delimiter token whose decoding contains `,,`, and
  returns what it dropped so the log can print it;
* `detector_delim_vs_content()` now returns `delimiter_loss` (forced basis — the number the arm
  reads), `delimiter_loss_all_basis` (the pre-ruling number, so `0.1094` and `0.1022` stay
  comparable), and `act2_slot_loss` on its own line;
* `content_loss` is **unchanged on both bases** — it is `G4.9`'s input, `G4.9` is seen falling and
  credited in DoD item 6, and the excluded tokens are scored in **neither** bucket rather than moved
  into content;
* the runner prints which ids the arm dropped, and prints `NOTHING -- basis unchanged` if it dropped
  none. A basis change that cannot be read off the log is a basis change nobody can audit; an empty
  drop set is a FINDING, not a detail.

🔴 **LOCAL ONLY, NOT SHIPPED.** `4thJ_step4_leg4_fold.sh` runs three python invocations in sequence
(`train`, `diagnostics`, `genperturb`), so replacing a `.py` on Speed while `1274884` is up would
score one job under two code versions. Ship after the queue clears, md5 both sides.

### What these two rulings do NOT do

Neither makes a gate pass. `G4.6` stays a standing FAIL until the sweep reports, and `G4.2`'s first
arm on the forced basis is expected around `0.075` — **still above the band** — in which case the
`collapse_content` demonstration is VOID again, `G4.2` stays in `never made to fall`, and the
coverage clause stays `FAIL`. Both rulings buy the same thing and only that thing: a gate that
*could* fail for the reason it was written, instead of one that could not.

### 2026-08-19 — CORRECTION TO MY OWN LAUNCHERS: WALLTIME

Both `.sh` files written for the D-S4-3/D-S4-4 work asked for **short walltimes** — the α-sweep for
2 h, the `G4.2` census for 1 h — against the standing rule that every job requests **7 days unless
the partition's `MaxTime` is lower**. `scontrol` was checked rather than assumed: `pg` and `ps` both
report `MaxTime=7-00:00:00`, so the exemption does **not** apply and the rule stands at its full
value for both.

* `4thJ_step4_g46_alpha_sweep.sh` — `0-02:00:00` → `7-00:00:00`. md5 now `3bea9e672837562770f25d68dc47b476`. **Not yet submitted**, so the wrong value never reached the scheduler.
* `4thJ_step4_g42_token_census.sh` — `0-01:00:00` → `7-00:00:00`. This one **did** run at the wrong
  value (job `1274891`, `COMPLETED 00:00:38`). It finished far inside the hour so nothing was lost,
  but the job that ran is not the file that is now on disk, and the census result stands on the
  `.py` (md5 `8fb5599e687d5ad10c09664afddaff0c`, unchanged both sides), not on the launcher.

Every other launcher in `tools/` was audited in the same pass — eighteen files, all already at
`7-00:00:00`. These two were the only offenders and both were mine, written today.

Both scripts also `py_compile` clean locally (`4thJ_step4_g46_alpha_sweep.py`,
`4thJ_step4_train.py`), so a syntax error will not be what burns the GPU slot the sweep is waiting
for.

**Queue at the time of writing:** `1274884` (fold `es`) still `R`, 4:36:06 elapsed, `speed-39`. It
holds the only GPU we may occupy (FINDING 2), so the ship list is unchanged and nothing moved to
Speed in this pass.

### 2026-08-19 — THE D-S4-4 RE-SCORE IS WRITTEN. `tools/4thJ_step4_g42_rerun_ds44.sh`

Two runs, not eleven. D-S4-4 re-points exactly one number — `delimiter_loss` — and exactly one
gate reads it. `content_loss` was left unchanged on both bases precisely so that `G4.9`, which is
seen falling and credited in DoD item 6, keeps the input it was scored on; re-running the other
nine perturbations would spend GPU hours reproducing numbers that cannot have moved, and every
reproduction is an opportunity to overwrite one that did.

* **New run directory**, `runs_g42_ds44`. The pre-ruling detectors in `runs_g42_demo/` are the
  only evidence that `0.1022` was ever read, and the point of the re-run is to set the two bases
  side by side. Overwriting the old reading destroys the comparison the ruling must be judged on.
* **Budget copied verbatim** from the battery's own `G4.2` block — `--epochs 2 --limit-train 4000
  --gen-n 16 --batch-size 1 --grad-accum 16 --max-len 1280`. If the budget moved alongside the
  basis, a delimiter loss that fell could not be attributed to either.
* **The log is instructed to be read for the negative case.** The runner prints which ids the arm
  dropped; if it prints `NOTHING -- basis unchanged`, the ruling did not take effect and the two
  arms are the old basis wearing a new directory name. The launcher says so above the first run
  rather than leaving it to whoever reads the output.

**`--limit-train 4000` was re-verified before writing this, not assumed.** That flag is the exact
setting behind FINDING 1, where a plain `[:4000]` on a country-ordered shard nearly trained the
pilot on Italy alone. `4thJ_step4_train.py:838-867` now takes the cap **proportionally per
country** from a seeded sample and **asserts** that no country was dropped, failing loudly if one
was. The re-run inherits that guard.

**Pre-registered outcome, in the launcher header, written before submission.** Removing the
`act2` share from the last all-basis reading leaves roughly `0.075`, still above `0.05`. So the
expectation on the record is: ctrl arm ABOVE the band → **the demonstration is VOID and is
reported VOID**, `G4.2` stays in `never made to fall`, the coverage clause stays `FAIL`. The
collateral is quoted with the lever as always — `collapse_content` also fells `G4.9` at 4,000
records and above (FINDING 26).

**Submission order once the queue clears** — the sweep first, alone, because it takes minutes and
its answer may change what is worth spending training hours on:

1. ship `4thJ_step4_train.py` (`610cd7659001ffe4aaa6720a99ea90a2`), `4thJ_step4_g46_alpha_sweep.py`
   (`d403cecc6b5f714a60c40b4e983dbc12`), `4thJ_step4_g46_alpha_sweep.sh`,
   `4thJ_step4_g42_rerun_ds44.sh`, and the re-timed `4thJ_step4_g42_token_census.sh`; md5 both sides
2. `sbatch 4thJ_step4_g46_alpha_sweep.sh` — read `alpha=0 == 0.0` and the two `alpha=1` rows FIRST;
   if those two disagree by anything near the effect, the sweep is inconclusive and is reported so
3. `sbatch 4thJ_step4_g42_rerun_ds44.sh`

---

## 2026-08-19 (late) — LEG-4 FOLD `es` COLLECTED. FIRST MODEL-SIDE VERDICTS IN THE PROJECT, AND FINDING 29.

**Job `1274884`, `COMPLETED 05:17:27`, exit `0:0`**, verified with `sacct` directly (not from a
watcher — three of those have reported a job left the queue on an empty `sacct` state). `squeue -u`
was empty at the same moment. It is the first chain in this project to run **train → diagnostics →
genperturb** to the end on a **full fold**: 48,594 train records (`it` 34,366, `uk` 14,228),
5,520 held-in val, loss `2.0767 → 0.4519`, peak VRAM 7.67 GiB, 17,853.6 s.

Log fetched to the scratchpad as `4J_step4_leg4_1274884.out` (398 lines); the detectors, the
conditioning diagnostics and the genperturb JSON were fetched with it. Note the path: the log is
`/speed-scratch/o_iseri/4J_step4_leg4_1274884.out`, **not** `..._leg4_es_1274884.out` as the
previous handoff recorded — the fold is not in the filename.

**Startup and end-of-run gates, all mechanical, all as before:** `G4.14 PASS`
(`e4243e07cdd80c9c846b91f40e3e8c45` live == recorded, `prereg.md` untouched), `G4.13 PASS`
(0 held-out-country records in train), `G4.7 PASS` (48,594/48,594 terminate with `<eor>`),
`G4.8 PASS` (identity True + round-trip 1000/1000), `G4.5 PASS` (2,980,205 pad positions, 0
unmasked), `G4.9 PASS` per country, `G4.11 PASS`, `G4.10` reported not thresholded.

### The five model-quality gates of FINDING 16, now measured on a real fold

| gate | verdict | reading |
|---|---|---|
| `G4.1` | **FAIL** both epochs | ep0: 6 scorable strata, **4 above** band `[0.8, 1.25]`, worst_high `1.664`, `end=upper`. ep1: **0 above, 2 below**, worst_low `0.537`, `end=lower (collapse)` |
| `G4.2` | **PASS** both epochs | delim `0.1020 / 0.0974`, entropy `3.284 / 3.282`, `gen-terminated 600/600` |
| `G4.3` | **FAIL** | CE true `0.5428` permuted `0.6357` **rise `0.0929`** against a `0.15` band; 2 prefixes unchanged by the shuffle |
| `G4.4` | **PASS** | evening ratio `0.831`, morning ratio `0.606`, both above `0.5`, reported separately |
| `G4.12` | **FAIL** | moved 595, stuck-in-singletons 0, CE rise `0.0053` (need `0.15`), **MI drop `0.085` (need `0.10`)** |
| `G4.6` | **FAIL** | `max_logit_diff = 3.471e-04` against `1e-4`, fp32, 20,103 positions; repeat-noise floor `0.000e+00` |

**`G4.1` DID NOT JUST FAIL, IT CHANGED END BETWEEN EPOCHS.** Epoch 0 had four strata **above** the
band and `n_below_band_COLLAPSE_END = 0`; epoch 1 has none above and **two below**, with
`which_end = "lower (collapse)"`. That is the `V4.a` collapse branch, which the pilot never reached
— every earlier reading was the band branch. The whole distribution moved down together
(worst_high `1.664 → 0.964`, worst_low `1.100 → 0.537`), and a shift that is systematic across all
six strata is more consistent with a real training effect than with generation sampling noise. It is
**not** claimed as settled: the generation budget is still 600 diaries (6 strata x 100), the same
budget that made every `G4.4` reading unquotable in FINDING 24. What can be said without hedging is
that at full budget the model overshoots the at-home band **through** it rather than approaching it,
and that a third epoch is not obviously an improvement. **This is the one reading on this fold that
should decide something and cannot be decided from one fold.**

**`G4.3` improved and still fails.** The pilot read `0.0616`; the full fold reads `0.0929` against
`0.15`. Budget moved it by half the remaining distance and it is still short. Quote both numbers
together — the direction is the informative part, not either level.

**`G4.12` is the near miss.** MI drop `0.085` against a `0.10` band is the closest any conditioning
gate has come. CE rise `0.0053` against `0.15` is not close, and the gate needs both.

**`G4.2` at full budget replaces FINDING 25's extrapolation with a measurement, as promised.** The
two-point power-law fit predicted ~`0.093` at the full fold; the measurement is **`0.0974`** at
48,594 records (ep1), against `0.1022` at 4,000 and `0.1094` at 600. **Quote `0.0974`. The fit
over-predicted the improvement and is now retired.** This is scored on the **all-basis** — Speed was
still holding the 1505-line `4thJ_step4_train.py` when the fold ran, so D-S4-4 was not in force.
That does not disturb the verdict: D-S4-4 *removes* the low-entropy `,,` token, which moves the
number **up**, further from the `< 0.05` arm, so `G4.2 PASS` holds on either basis. It does mean
folds `uk` and `it` will report a forced-basis `delimiter_loss` that is **not** comparable
line-for-line with `es`; both bases are printed side by side from now on, and `es` has only the one.

### 🔴 FINDING 29 — the generation-side battery credited two perturbations for felling a gate that was already down, and called the same gate an unexpected fall on the arm that changes nothing

`G4.1`'s verdict inside `4thJ_step4_genperturb.py` is **identical on all five arms**, `null`
included:

```
"n_scorable_strata": 0,
"reason": "V4.a: only 0 strata reach N >= 100 on BOTH sides. A variance gate evaluated on
           that many strata is satisfied by nothing, so it FAILs rather than skipping.",
"verdict": "FAIL"
```

So on the generation-side probe `G4.1` is **vacuous** — it is `V4.a` firing on an eligibility rule
(`N >= 100` on *both* sides) that the 600-diary generated set cannot satisfy, not a reading about
the model. The trainer's own `G4.1` had six scorable strata on the same run; the vacuity belongs to
this probe's scoring path alone.

The report nevertheless printed, from the same run:

* `modal_day` → `G4.1 expected FAIL -> FAIL AS EXPECTED`, and `duplicate_500` → the same. **Both
  false.** This is exactly **FINDING 18**, repaired in `4thJ_step4_perturbtable.py` on 2026-08-18
  and never ported to this file.
* `null` → `G4.1 expected clean -> FAIL UNEXPECTED FALL -- FINDING`, on the arm whose own `info`
  reads `{'changed': 0}`. And `within_stratum_shuffle` → the same. **Both false, in the opposite
  direction.** This is exactly **FINDING 23**, repaired in the same file on the same day and
  likewise never ported.

The coverage clause itself was **not** affected — it already filtered on `passing_at_baseline`, so
`never_felled: ['G4.7']` and `COVERAGE CLAUSE VERDICT: FAIL` stand as printed.

**What the honest table is, re-derived from `genperturb_es.json` by hand:**

* `G4.1` — **NOT ASSESSABLE** on this probe, all five arms, `V4.a` vacuity. Credited to nothing.
* `G4.4` — baseline `PASS` (evening ratio `0.731`), `blank_evening` `FAIL` (evening ratio `0.307`).
  Pre-declared `must_fail`, baseline clean, felled. **This is a legitimate seen-falling credit and
  the only one on the generation side.**
* `G4.7` — `PASS` on all five arms and no lever in the map targets it. Its lever is `strip_eor_1pct`
  on the **training** side, where `G4.7` is already credited. The gen-side coverage `FAIL` is
  therefore structural, not a new defect.
* **Undeclared collateral:** `within_stratum_shuffle` also felled `G4.4` (morning ratio `0.457`
  against `0.5`), and it is in neither list for that gate, so nothing printed it. Same class as
  FINDING 26.

**The repair, additive, no ruling needed** — it is the same class as the three additive repairs that
went with D-S4-1/D-S4-2, and it changes only what the report may claim, never how a gate is scored,
and moves no band. `4thJ_step4_genperturb.py` 314 → **366 lines**, md5
`bd2df2f3e9f11e237b6d5a0d4b1a895f`, `py_compile` clean, **shipped, md5 identical both sides**.
Attribution moved out of the scoring loop into a **second pass that runs after the baseline is
known** — the old code attributed each arm without knowing what `null` had done, and `null` was
attributed against itself. A `must_fail` gate already `FAIL` at baseline now prints `VOID`, is
**not** credited; a `must_stay_clean` gate already `FAIL` at baseline prints `NOT ASSESSABLE`; an
undeclared collateral fall is printed; and the run ends by naming `GATES CREDITED AS SEEN FALLING`
and the gates that are not creditable here.

**Re-scored as job `1274945`** — CPU partition `pt`, 7-day walltime, no GPU, so it does not contend
with the sweep (FINDING 2 is about GPU jobs). Output goes to a **new** directory
`4J_step4/genperturb_f29/`, deliberately: `genperturb/genperturb_es.json` is the evidence that the
false credits were ever printed, and overwriting it would destroy the comparison the repair has to
be judged on — the same reason `runs_g42_ds44` was kept apart from `runs_g42_demo`.

**DoD item 6 is not moved on this entry.** `G4.4` looks creditable by hand, but the credit must come
from the harness printing it, and the harness that printed this run was the broken one. The count
stays at **seven** until job `1274945`'s table says otherwise in its own output.

### Ship record

Queue confirmed empty before anything was sent. All five files md5-identical on both sides after
`scp`; `4thJ_step4_train.py` verified at **1614 lines** on Speed, replacing the 1505-line
`661b11e7...`.

| file | md5 shipped |
|---|---|
| `4thJ_step4_train.py` | `610cd7659001ffe4aaa6720a99ea90a2` |
| `4thJ_step4_g46_alpha_sweep.py` | `d403cecc6b5f714a60c40b4e983dbc12` |
| `4thJ_step4_g46_alpha_sweep.sh` | `6d4f1f60d271794584c9c261ff60678d` |
| `4thJ_step4_g42_rerun_ds44.sh` | `ac95e75a90201da2ffac9ddb6512596d` |
| `4thJ_step4_g42_token_census.sh` | `d095068a9830085542af0234fc8b7376` |
| `4thJ_step4_genperturb.py` (FINDING 29) | `bd2df2f3e9f11e237b6d5a0d4b1a895f` |

🔴 **One recorded discrepancy, not silently absorbed.** The previous handoff recorded
`4thJ_step4_g46_alpha_sweep.sh` as md5 `3bea9e672837562770f25d68dc47b476`; the file on disk is
`6d4f1f60d271794584c9c261ff60678d`. The **content** is correct — `#SBATCH --time=7-00:00:00` and the
replaced walltime comment are both present, which is what the recorded md5 was taken to attest — so
the recorded hash was stale, taken before the last edit landed. `4thJ_step4_g42_token_census.sh` is
in the same position. Nothing was reverted; the hashes above are the ones actually shipped and
verified on both sides, and they supersede the handoff's table.

**`sbatch 4thJ_step4_g46_alpha_sweep.sh` submitted as job `1274944`** — with the adapter given
**explicitly** as `4J_step4/runs/leg4_primary_fold_es/adapter`, **not** the script's default
`runs_perturb/leg4_perturb_fold_es/adapter`. Recorded as a deliberate departure: the default was
written when only the 600-record pilot-perturb adapter existed, and the full-fold adapter is the one
that produced the `3.471e-04` FAIL the sweep exists to explain. The `alpha = 0` control is unaffected
by the choice — it must return exactly `0.0` for any adapter.

### 🟢 JOB `1274945` CLOSED — THE FINDING 29 REPAIR IS DEMONSTRATED, AND DoD ITEM 6 MOVES FROM SEVEN TO EIGHT

`COMPLETED 00:00:49`, exit `0:0`, CPU partition, no GPU touched. Same generated file, same seed,
same gates, same scoring code — **only the attribution changed**, which is what makes the two tables
a controlled comparison. All four repaired behaviours are visible in one run:

| arm | before (job `1274884`) | after (job `1274945`) |
|---|---|---|
| `null` | `G4.1 expected clean -> FAIL 🔴 UNEXPECTED FALL -- FINDING` | `G4.1 NOT ASSESSABLE as STAY CLEAN -- already FAIL at baseline (null)` |
| `modal_day` | `G4.1 expected FAIL -> FAIL AS EXPECTED` | `G4.1 VOID -- already FAIL at baseline (null); a gate down before the perturbation cannot be seen falling` |
| `duplicate_500` | `G4.1 expected FAIL -> FAIL AS EXPECTED` | `G4.1 VOID -- ...` |
| `blank_evening` | `G4.4 expected FAIL -> FAIL AS EXPECTED` | unchanged — **the one credit that was always real** |
| `within_stratum_shuffle` | `G4.1 ... UNEXPECTED FALL`, and its `G4.4` fall printed nowhere | `G4.1 NOT ASSESSABLE`, plus `🔴 UNDECLARED COLLATERAL -- also fell, in neither list: ['G4.4']` |

The run now ends by naming what it may claim:

```
GATES CREDITED AS SEEN FALLING on this probe: ['G4.4']
Gates already FAIL at baseline, so NOT creditable here: ['G4.1']
```

The coverage clause is byte-identical to the broken run — `never_felled: ['G4.7']`,
`COVERAGE CLAUSE VERDICT: FAIL` — which is the control this repair needed: it proves the repair
touched attribution only and left scoring alone.

🟢 **`G4.4` IS THEREFORE SEEN FALLING, PRINTED BY THE HARNESS, AND IT IS THE FIRST
GENERATION-SIDE CREDIT IN THE PROJECT.** DoD item 6 goes to **EIGHT**:
`G4.4 G4.5 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14`.

**Two things declared with the credit, not buried under it.** First, `blank_evening` reports
`changed: 0` — it acts on the MI estimator's evening-window label association and deliberately does
**not** modify the diary text, exactly as its own `note` says. That is a legitimate detector test
(it asks whether the estimator responds at all) and it is pre-declared in the val doc as
`must_fail: [G4.4]`, but it is a lever on the **estimator**, not on the model, and any sentence
crediting `G4.4` has to say so. Second, `G4.4`'s baseline margin is not large — evening `0.831`,
morning `0.606`, against `0.5` — and FINDING 24 established that 600-diary `G4.4` readings carry
real sampling noise. The credit is for the gate having **power**, which is what DoD item 6 asks; it
is not a claim that the model's diurnal shape is settled.

**`G4.2` remains the only gate in `never made to fall`,** and FINDING 28 settled why: its first arm
is a precondition the corpus itself does not meet. `G4.6` remains a standing explained FAIL pending
D-S4-3, whose sweep is job `1274944`.

**`G4.1` is now correctly credited to nothing on this probe.** Its `V4.a` vacuity there
(`n_scorable_strata = 0`, all five arms) is a separate open item from its trainer-side FAIL: the
generation-side eligibility rule asks for `N >= 100` on **both** sides while the generated set holds
exactly 100 per stratum before any parsing loss, so the probe cannot in principle score it at this
generation budget. **That is a probe-design question, not a model question, and it is not repaired
here** — raising `--gen-stratified-k`'s per-stratum count, or scoring the generated side at
`N >= 100` against a real side that already clears it, are both basis changes to the eligibility
rule and belong to the author.

### 🔴 D-S4-3 — THE `G4.6` ALPHA SWEEP IS IN. JOB `1274944`, `COMPLETED 00:21:23`, EXIT `0:0`. THE ANSWER IS NEITHER OF THE TWO BRANCHES THE RULING PRE-REGISTERED.

**The controls first, as the ruling and the launcher both require, before any trend is read.**

* **`alpha = 0` returned exactly `0.000000e+00`, `PASS`.** `B = 0` means `W + 0 = W` bitwise, so the
  script is measuring what it claims to measure. This also reproduces `freeze_adapter`'s
  `G4.6 PASS` from the opposite direction — FINDING 15's control, arrived at a second way.
* **`alpha = 1` measured twice, first and last: `3.471375e-04` and `3.623962e-04`, spread
  `1.526e-05`.** That is merge/unmerge contamination — `(W + D) - D` is not bitwise `W` — and it is
  **4.4 % of the `alpha = 1` reading and 1.7 % of the span the sweep is trying to resolve**
  (`3.47e-04` to `1.24e-03`, a span of `8.9e-04`). The pre-registered rule was that the sweep is
  reported **inconclusive** if the two rows disagree by anything near the effect size. They do not:
  the contamination is roughly **58x smaller** than the effect. **The sweep is conclusive to that
  precision, and the two rows are reported as measured — not averaged.**

**The readings.** First row is the deployment case and it reproduces the fold's own `G4.6` verdict
to the digit (`3.471375e-04`, against `3.471e-04` in job `1274884`), which is a third control nobody
asked for.

| alpha | max_logit_diff | drift / alpha | verdict |
|---|---|---|---|
| 1 | `3.471375e-04` | `3.47e-04` | FAIL |
| 0.1 | `1.033783e-03` | `1.03e-02` | FAIL |
| 0.01 | `1.237869e-03` | `1.24e-01` | FAIL |
| 0.001 | `6.427765e-04` | `6.43e-01` | FAIL |
| 0 | `0.000000e+00` | — | **PASS** |
| 1 (repeat) | `3.623962e-04` | `3.62e-04` | FAIL |

**Which branch this is, by the script's own rule.** The ruling asked: is `drift` proportional to
`alpha` (⇒ the residual is the delta's own re-association, unsatisfiable for any trained adapter),
or does `drift` plateau (⇒ there is a floor, and the floor is the number a band gets ruled against)?

* **Proportional is dead.** Over three decades of `alpha`, a proportional residual would have moved
  the drift by **1000x**. `drift / alpha` instead varies by a factor of **1,850**, which is the
  signature of the opposite of proportionality.
* **Plateau is the branch,** but it is a rough one and is reported rough. `drift` varies by a factor
  of **3.6** across `alpha` from `1` down to `0.001` — against the 1000x that proportionality
  predicts — so it is far closer to constant than to proportional. It is **not** flat, and it is
  **not monotonic**: it peaks at `alpha = 0.01` and the *largest* alpha gives the *smallest* drift.
  **No mechanism on the record explains that shape, and it is recorded as unexplained rather than
  narrated into one.** The consequence is that a single number may not be quoted as "the floor":
  what is on the record is a band of roughly `3.5e-04` to `1.2e-03`, with `3.5e-04` being the
  deployment case (`alpha = 1`).

🔴 **THE RESULT THAT MATTERS FOR THE RULING, AND IT IS NOT WHAT EITHER OPTION ASSUMED.** Every
non-zero `alpha` FAILs, including `alpha = 0.001`, where the adapter's contribution is scaled to one
thousandth and the drift is still **6.4x over the band**. So `G4.6` at `1e-4` does not measure *how
much* the adapter trained, and it does not measure merge arithmetic quality either. **It is a binary
detector for whether the adapter is exactly zero.** It PASSes for `B = 0` and FAILs for every other
adapter that has ever been put through it, by between 3.5x and 12x, independent of magnitude.

That kills the argument that was standing behind D-S4-3 option (a) — "the residual is proportional
to how much the adapter learned, so an explained FAIL is honest" — because it is **not**
proportional. What is left is a gate whose only PASS state is the state the project is trying to
prove it is not in.

**Nothing was moved.** No band, no basis, no `EXPECTED` row. The sweep wrote its JSON
(`4J_step4/g46_alpha_sweep_1274944.json`) and stopped, exactly as D-S4-3 specified. **D-S4-3 now
goes back to the author with the number in hand, and the options have changed shape:** (a) keep
`1e-4` and report `G4.6` as a standing EXPLAINED FAIL — now explained by *this* measurement rather
than by the dead bf16 story, with `perturb_merged_weight` staying VOID project-wide; or (b) re-state
what the gate is for, since a binary is-the-adapter-zero detector is not what its `EXPECTED` row
describes — a **basis** change, which must be registered before the run that reports under it. 🔴 A
third option, re-banding to `~1.2e-03` so the trained adapter passes, **is flagged against itself
and rejected on the record**: it is a band relaxed because our own artefact fails it, which is the
one move this project forbids. It is listed only so it is visible as considered.

**One cost of the sweep, declared.** The adapter was passed **explicitly** as
`4J_step4/runs/leg4_primary_fold_es/adapter` rather than the script's default 600-record
`runs_perturb` adapter — recorded above as a deliberate departure. The `alpha = 1` row reproducing
the fold's `G4.6` to four significant figures is the evidence that the substitution was the right
one: the sweep is measuring the exact object whose FAIL is under question.

### Step 3 of the handoff order — `sbatch 4thJ_step4_g42_rerun_ds44.sh` submitted as job `1274954`

Queue was confirmed empty of our GPU jobs first (FINDING 2); the sweep had left the queue, verified
with `sacct` directly. Its pre-registered outcome is unchanged and stands in the launcher header:
removing the `act2` share leaves roughly `0.075` on the forced basis, still above `0.05`, so the
expectation on the record is **ABOVE the band → the demonstration is VOID**, `G4.2` stays in
`never made to fall`, and the coverage clause stays `FAIL`. FINDING 28 is the reason and it does not
depend on budget. Read the log for the negative case: if the runner prints
`NOTHING -- basis unchanged` for the dropped token ids, D-S4-4 did not take effect and the two arms
are the old basis under a new directory name. `collapse_content` also fells `G4.9` at 4,000 records
and above (FINDING 26) — quote it with the lever.

### 🟢 D-S4-4 CLOSED — JOB `1274954`, `COMPLETED 00:50:24`, EXIT `0:0`. THE PRE-REGISTERED EXPECTATION WAS **WRONG**, AND `G4.2` IS SEEN FALLING. DoD ITEM 6 GOES TO **NINE**.

**Say the falsification first, because it is the part that matters for how this may be written.** The
launcher header and the handoff both pre-registered the negative outcome: *"removing the `act2` share
leaves roughly `0.075` on the forced basis, still above `0.05`, so the expectation is ABOVE the band
→ the demonstration is VOID, `G4.2` stays in `never made to fall`."* **That expectation was
falsified by the measurement.** The perturbed arm came in at `0.011058`, not `~0.075` — off by a
factor of about seven, in the direction that makes the demonstration work. 🔴 **This credit was
pre-registered to FAIL and succeeded anyway. Nothing was tuned to get it: the basis (D-S4-4), the
band (`0.05`, untouched), the budget and the expected outcome were all on the record before the job
was submitted. It must never be written as though the demonstration went to plan.** Where the
estimate went wrong is now visible and is recorded: it assumed the `act2` slot carried roughly its
baseline loss, but under `collapse_content` the `act2` slot loss is `3.1617` — the perturbation puts
almost the entire delimiter-basis loss *into* the tokens D-S4-4 removes, so subtracting them takes
far more out than the estimate allowed for.

**D-S4-4 took effect — the negative case did not print.** Both arms show, identically:

```
delimiter token ids: 15
  D-S4-4 forced-delimiter basis: 11 of 15 ids kept; dropped
      {10856: "',,'", 27856: "',,,,'", 57082: "',,,,,,,,'", 61823: "',,,'"}
```

**The two arms, both bases side by side, as the ruling requires from now on.** `halt_rule` is
`delimiter_loss < 0.05 AND activity_entropy < 1.50`, strict on both arms per `V4.d`.

| arm | epoch | delim (forced, D-S4-4) | delim (all, pre-ruling) | act2-slot | entropy | `G4.2` |
|---|---|---|---|---|---|---|
| ctrl (`null`) | ep0 | `0.06526` | `0.10800` | `0.3067` | `2.945` | **PASS** |
| ctrl (`null`) | ep1 | `0.07223` | `0.10200` | `0.2404` | `3.254` | **PASS** |
| `collapse_content` | ep0 | **`0.011058`** | `0.56878` | `3.1617` | **`0.000`** | **FAIL** |

Token counts are constant across every row — `555,651` forced, `675,169` all, `119,518` in the
`act2` slot — so the two bases differ by exactly the tokens D-S4-4 named and by nothing else.

🔴 **THIS IS THE LINE THAT JUSTIFIES THE RULING, AND IT SHOULD BE QUOTED WHEREVER D-S4-4 IS
DEFENDED.** On the **all** basis the perturbed arm reads `0.5688`, which is *not* `< 0.05`, so arm
one does not fire, the `AND` does not close, and **`G4.2` would have returned PASS on a run whose
activity entropy was exactly zero** — a model that had collapsed to a single activity token and was
still being called healthy by the detector built to catch precisely that. That is FINDING 28 stated
as a measurement instead of an argument. On the **forced** basis both arms fire and the gate FAILs.
The band did not move; only which tokens the first arm is computed over.

The trainer stopped itself, printing what the detector is for:

```
🔴 G4.2 HALT CONDITION MET -- stopping. Loss fell while content collapsed,
   which is the failure this detector exists for.
```

**The harness named the credit itself, in its own coverage clause:**

```
gates PASSing at baseline: ['G4.11','G4.13','G4.14','G4.2','G4.5','G4.7','G4.8','G4.9']
gates seen falling:        ['G4.2']
```

`G4.2` was `PASS` at baseline on this same two-run pair, at the same budget, in the same directory;
`collapse_content` is pre-declared `must_fail: [G4.2]`; it felled it. The credit is clean.

🟢 **DoD ITEM 6 GOES FROM EIGHT TO NINE:**
`G4.2 G4.4 G4.5 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14`. **`never made to fall` is, for the first time in
Step 4, empty of gates that have a lever pointed at them** — what remains uncredited is `G4.1`,
`G4.3`, `G4.6`, `G4.10` and `G4.12`, and each of those is uncredited because it does not PASS at
baseline (or is not thresholded), not because a lever missed.

🔴 **THE ONE LIMITATION ON THIS CREDIT, DECLARED, NOT BURIED.** The credit is scored on the
**forced** basis, and the main training-side battery table `perturb_table_train_side_es.txt` was
produced by the 1505-line trainer, which wrote no forced-basis field at all. **The battery's own
coverage clause therefore still prints `G4.2` in `never made to fall`, and it is not retro-fitted
from here** — the runner said so itself in the last two lines of the log: *"the coverage clause
printed above covers this TWO-RUN re-score ONLY. The battery's real clause remains
`perturb_table_train_side_es.txt`."* The old detector JSONs cannot be re-scored offline either: they
do not carry `act2_slot_loss`, so the forced number is not recoverable from them. **Printing the
credit inside the battery's own table requires re-running the training-side battery under the
1614-line trainer — eleven perturbations, and a cost question that belongs to the author.** Until
that happens the honest sentence is: *`G4.2` has been seen falling, on the D-S4-4 forced basis, in a
dedicated pre-registered two-run control, and the battery table has not yet been re-scored to show
it.*

### 🔴 FINDING 30 — the training-side table reports a gate that was never scored as an UNEXPECTED FALL

Same class as FINDINGS 18, 23 and 29, and in the *other* file this time.
`4thJ_step4_perturbtable.py` printed:

```
collapse_content   OK  target G4.2 -> FAIL
                   UNEXPECTED FALL -- FINDING: also moved ['G4.9']
```

`G4.9`'s verdict on that arm is **`NOT CHECKED`**, not `FAIL`. The `G4.2` halt fired at the end of
epoch 0 and stopped the run before `G4.9` was ever scored, so there is no reading to have fallen.
The table's attribution asks "is this verdict different from baseline" and treats `NOT CHECKED` as a
move. **It is not a false seen-falling credit** — the coverage clause filters on `PASS`/`FAIL` and
correctly leaves `G4.9` in `never made to fall` — **but it is a false FINDING flag, and it would put
a defect in the paper that the run does not support.** Not repaired here: the repair is one
condition in the attribution pass and it is the same additive class as the FINDING 29 fix, but
shipping it now would change the file that produced the `G4.2` credit above, and the credit is
better left standing on the code that printed it. Recorded for the next additive round.
**Coincidence worth stating so it is not read as confirmation:** FINDING 26 established that
`collapse_content` *does* fell `G4.9` at 4,000 records and above. The flag points at a real
phenomenon on the wrong evidence.

**One more `G4.6` reading, free.** The ctrl arm's merged-weight drift is `2.632e-04` and the
perturbed arm's is `4.425e-04`, both against `1e-4`, both with a repeat-noise floor of exactly
`0.000e+00`. Together with the sweep's `3.471e-04` and `3.624e-04` on the full-fold adapter, four
independent adapters now sit between `2.6e-04` and `4.4e-04`, none of them near the band. **That is
further evidence for the D-S4-3 conclusion — `G4.6` at `1e-4` PASSes only when the adapter is
exactly zero — and it is offered as corroboration, not as a new argument.**

### Fold `uk` submitted as job `1274964`

Queue confirmed empty of our GPU jobs first (FINDING 2), and the two shipped tools re-verified on
Speed at the moment of submission: `4thJ_step4_train.py` `610cd7659001ffe4aaa6720a99ea90a2` (1614
lines, D-S4-4 in force) and `4thJ_step4_genperturb.py` `bd2df2f3e9f11e237b6d5a0d4b1a895f` (366
lines, FINDING 29 repaired). **Fold `uk` is therefore the first fold in the project to run with both
repairs live**, which has two consequences to expect in its log and to not mistake for new defects:
its `G4.2` will print `delim(forced)` and `delim(all)` side by side and only the forced number is
comparable with `es`'s single all-basis `0.0974`; and its generation-side battery will print `VOID`
/ `NOT ASSESSABLE` / `UNDECLARED COLLATERAL` lines and a closing `GATES CREDITED AS SEEN FALLING`
list, none of which the `es` fold's log contains. Log will be
`/speed-scratch/o_iseri/4J_step4_leg4_1274964.out` — **the fold is not in the filename**, the same
trap that cost time on `es`. Expect roughly 5–6 h on the `uk` shard.

---

## Fold `uk` CLOSED — job `1274964`, `COMPLETED 0:0`, `05:08:26`, peak VRAM 5.99 GiB

`sacct` consulted directly, not the watcher. `G4.14` verified live on both sides:
`e4243e07cdd80c9c846b91f40e3e8c45` matches the sidecar, so `prereg.md` is intact and this fold is
reported under the frozen pre-registration.

`G4.13 PASS  heldout-country records in train = 0  by_country={'es': 17332, 'it': 34366}` — the
held-out country is genuinely absent, the LOCO assertion holds on a second fold, and this is the
reading that FINDING 1's `[:4000]` cap would have destroyed.

### The two folds side by side — every number that exists on both

| reading | `es` (1274884) | `uk` (1274964) |
|---|---|---|
| `G4.1` epoch 0 | FAIL, 0 below / **4 above**, worst 1.100/1.664, `end=upper` | FAIL, 0 below / **2 above**, worst 0.894/1.441, `end=upper` |
| `G4.1` epoch 1 | FAIL, **2 below** / 0 above, worst 0.537/0.964, `end=lower (collapse)` | FAIL, **1 below** / 0 above, worst 0.674/1.234, `end=lower (collapse)` |
| content loss ep0 → ep1 | 0.9034 → 0.8887 | 0.8705 → 0.8522 |
| `delim` ep0 → ep1 | 0.1020 → 0.0974 (all-basis, pre-D-S4-4) | 0.0538 → 0.0666 (**forced**); all-basis 0.0895 → 0.0868 |
| `G4.2` | PASS both epochs | PASS both epochs |
| `G4.3` | FAIL, CE rise 0.0929 (need 0.15), 2 prefixes unchanged | FAIL, CE rise 0.0755 (need 0.15), 1 prefix unchanged |
| `G4.4` | **PASS** — evening 0.831, morning 0.606 | **FAIL** — evening 0.614 PASS, morning **0.474** FAIL |
| `G4.6` | FAIL, 3.471e-04 over 20103 positions | FAIL, 3.223e-04 over 16554 positions |
| `G4.12` | FAIL, CE rise 0.0053, MI drop 0.085 (need 0.10) | FAIL, CE rise 0.0037, MI drop **0.161 (clears 0.10)** |
| `G4.5` `G4.7` `G4.8` `G4.9` `G4.11` `G4.13` `G4.14` | PASS | PASS |
| `G4.10` | `REPORTED_NOT_THRESHOLDED` | `REPORTED_NOT_THRESHOLDED` |
| coverage clause | FAIL | FAIL |

### 🔴 FINDING 32 — the epoch-1 collapse is systematic, not an `es` quirk. `G4.1` is measuring training length.

The single question this fold was watched for. `es` had gone `end=upper` at epoch 0 and flipped to
`end=lower (collapse)` at epoch 1, and the open half was whether that was the fold or the schedule.
**`uk` flipped the same way, in the same direction, at the same epoch boundary: `end=upper` (2
above) → `end=lower (collapse)` (1 below).** Two folds out of two, on disjoint training sets, with
different shard sizes and a different held-out country. That is not a fold property.

What it means, stated carefully and separated from what it does not mean:

- **It does not mean the model gets worse at epoch 1.** Content loss *falls* on both folds
  (0.9034 → 0.8887 on `es`, 0.8705 → 0.8522 on `uk`) and `G4.2` PASSes at both epochs on both folds.
  By the losses the second epoch is an improvement.
- **What flips is the direction of the diversity miss.** At epoch 0 the generated strata are too
  *spread* relative to the reference (ratios above 1.25); at epoch 1 they are too *concentrated*
  (ratios below 0.8). The run crosses the band rather than converging into it, and the band is
  narrow enough (`[0.8, 1.25]`) that it is crossed inside a single epoch.
- **`G4.1` therefore never PASSes at any checkpoint on any fold, in either direction.** It is FAIL at
  epoch 0 for being too wide and FAIL at epoch 1 for being too narrow.

🔴 **The consequence for DoD item 6 is unchanged and must not be softened: `G4.1` is VOID on both
folds and cannot be credited as seen falling on either.** A gate already FAIL at baseline is void by
our own rule, and the generation-side probe said so itself in five separate places on this fold
(`G4.1 VOID -- already FAIL at baseline (null); a gate down before the perturbation cannot be seen
falling`). Two folds of evidence do not convert a void into a credit — they convert a suspected fold
quirk into a known property of the gate as banded.

🔴 **And it is NOT a licence to re-band `G4.1`.** No band is relaxed because our own artefact fails
it. Whether `[0.8, 1.25]` is the wrong band, whether the crossing means the correct checkpoint is
somewhere inside epoch 1, or whether the two-epoch schedule is simply wrong for this shard size, is
an author decision registered *before* the run that reports under it. **Opened as D-S4-5 below.**

### 🔴 FINDING 33 — `G4.3` and `G4.12` agree with each other and disagree with their band, on both folds

Two independent probes of the same underlying question — *does the model condition on the prefix?* —
and four independent readings, all far below a shared `0.15` CE-rise band:

```
G4.3   es 0.0929   uk 0.0755     (prefix shuffled across diaries)
G4.12  es 0.0053   uk 0.0037     (within-stratum reassignment)
```

The two probes are not redundant: `G4.3` breaks the prefix→diary pairing globally, `G4.12` moves
diaries only within their own stratum, so `G4.12`'s rise is expected to be the smaller of the two
and it is, by roughly twenty-fold, on both folds. **The ordering is the physically sensible one, which
is evidence the probes are measuring what they claim.** What neither of them does is clear `0.15`.

**Where the `0.15` band came from is the thing to check before anything is concluded from this, and
it is not in this log.** Four readings from two probes on two folds, none above `0.093`, is either
(a) a real and reportable finding that the adapter conditions only weakly on the prefix, or (b) a
band set by analogy rather than from a measured null. Those have opposite consequences for the
paper and the log cannot distinguish them. **The distinguishing measurement is cheap and is not a
band change**: score `G4.3` and `G4.12` on the *base* model with no adapter, which gives the floor
that a rise of `0.15` was implicitly claimed to be above. If the base model also sits near `0.08`,
the band is the problem; if the base model sits near `0.00`, the adapter is conditioning weakly and
that is the finding. **Neither reading permits moving the band** — it is a basis question about what
the band was ever measured against. Recorded, not repaired.

**`G4.12`'s MI leg is the one place the folds genuinely differ:** MI drop `0.085` on `es` (misses
`0.10`) and `0.161` on `uk` (clears it). `G4.12` FAILs on both folds regardless, because the CE leg
fails on both, so this difference changes no verdict — but it does mean the two legs of `G4.12` are
not moving together and the gate's two-condition form should be re-read before it is quoted.

### 🔴 FINDING 34 — `G4.4` is the first gate to disagree across folds, and it costs `uk` the fold's only credit

`G4.4` PASSes on `es` (evening 0.831, morning 0.606, both above their floor) and FAILs on `uk`
(evening 0.614 PASS, **morning 0.474** FAIL). The morning window is the one that breaks, and it
breaks only on the fold whose held-out country is the UK.

The consequence is procedural and it is the reason this matters more than one FAIL:

- On `es`, `G4.4` PASSed at baseline and was felled by `blank_evening` → **`G4.4` is credited as
  seen falling, and that credit stands, on the `es` fold, on the record.**
- On `uk`, `G4.4` is FAIL at baseline, so `blank_evening` printed `G4.4 VOID -- already FAIL at
  baseline`. **The same perturbation that earned the credit on one fold cannot earn it on the other.**

🔴 **This is the first demonstration in Step 4 that a seen-falling credit is fold-specific, and it
must be written that way.** The honest sentence is *"`G4.4` was seen falling on the `es` fold"*, not
*"`G4.4` was seen falling"*. Whether one fold's credit satisfies DoD item 6 for a gate that is not
even PASSing on the other folds is an author call — **opened as D-S4-6 below.**

### `uk` coverage clause FAIL — and why it is worse than `es`'s

```
BASELINE (null) verdicts: {'G4.1': 'FAIL', 'G4.4': 'FAIL', 'G4.7': 'PASS'}
Gates already FAIL at baseline, so NOT creditable here: ['G4.1', 'G4.4']
Gates that PASS at baseline and were NEVER felled by any perturbation: ['G4.7']
GATES CREDITED AS SEEN FALLING on this probe: none
COVERAGE CLAUSE VERDICT: FAIL
```

On `es` the same probe credited `G4.4`. On `uk` it credits **nothing**: of the three gates the
generation-side probe can reach, two are down before the probe starts and the third (`G4.7`,
termination) survives all five perturbations — which is itself the FINDING-29 clause working as
designed, *"a gate that passes and cannot be made to fall has not been shown to have power. This is
a FAIL of the probe, not of the model."* `G4.7` PASSing everywhere is expected — none of the five
perturbations touches the `<eor>` token — and the clause is correctly refusing to call that a
demonstration.

**FINDING 29's repair is confirmed working on a fold that needed it.** The `VOID` / `NOT ASSESSABLE`
distinction fired five times and prevented five false credits that the pre-repair `es` code would
have been at risk of printing.

### `G4.6`: a fifth and sixth adapter in the same narrow range

`uk` reads `3.223e-04` against the `1e-4` band, with a repeat-noise floor of exactly `0.000e+00`
from two identical unmerged forward passes — so the band is resolvable and the drift is real signal,
not accumulation noise. With `es`'s `3.471e-04`, the sweep's `3.624e-04`, and the two control arms'
`2.632e-04` and `4.425e-04`, **six independent adapters now sit between `2.6e-04` and `4.4e-04` and
not one of them is within 3× of `1e-4`.** This is corroboration for D-S4-3, not a new argument: at
`1e-4`, `G4.6` PASSes only when the adapter is exactly zero. **D-S4-3 remains the author's to rule
and the band is not touched from here.**

### D-S4-4 forced basis reconciles on the second fold

```
ep0  delim(forced)=0.0538 over 489900 tok | delim(all)=0.0895 over 601973 tok | act2-slot=0.2454 over 112073 tok
ep1  delim(forced)=0.0666 over 489900 tok | delim(all)=0.0868 over 601973 tok | act2-slot=0.1748 over 112073 tok
```

`489900 + 112073 = 601973` exactly, at both epochs. The two bases differ by the tokens D-S4-4 names
and by nothing else. 🔴 **Only the forced number is comparable with anything; `es`'s `0.0974` is an
all-basis figure and must never be set beside `uk`'s `0.0666`.** The comparable `es` all-basis pair
is `0.1020 → 0.0974` against `uk`'s `0.0895 → 0.0868`.

### 🔴 D-S4-5 — OPEN, author. `G4.1` crosses its band inside epoch 1 on both folds.

Established: `end=upper` at epoch 0, `end=lower (collapse)` at epoch 1, on 2 of 2 folds, while
content loss improves. `G4.1` PASSes at no checkpoint on any fold. Options, none of which may be
taken by us:

- **(a)** Report `G4.1` as a standing EXPLAINED FAIL for Step 4, as D-S4-3 proposes for `G4.6`, with
  the two-fold crossing evidence as the explanation. Nothing is re-banded, nothing is re-run.
- **(b)** Register a checkpoint-selection basis *before* re-running — e.g. evaluate `G4.1` at a
  mid-epoch-1 checkpoint — and declare post-hoc that the basis was registered after seeing the
  epoch-boundary readings. Costs a re-run of all three folds.
- **(c)** Re-band `[0.8, 1.25]`. **Flagged against itself and recommended against**: the band would
  be moved because our own artefact fails it, which is exactly what our rule forbids.

**Recommendation: (a).** It costs nothing, it is honest, and the crossing behaviour is a more
interesting thing to report than a passing gate would have been.

### 🔴 D-S4-6 — OPEN, author. Does a one-fold seen-falling credit satisfy DoD item 6?

`G4.4` was seen falling on `es` and is void on `uk` (FINDING 34). Options:

- **(a)** One fold suffices; write *"seen falling on the `es` fold"* everywhere and never *"seen
  falling"* unqualified.
- **(b)** Credit requires the gate to be demonstrated on every fold where it PASSes at baseline;
  `G4.4` then has one credit and one void and the count is reported as such.
- **(c)** Credit requires all folds; `G4.4` loses its credit entirely.

**Recommendation: (a) with the qualification made mandatory in the text.** The demonstration on `es`
happened and deleting it would be under-reporting; but an unqualified sentence would over-claim on a
fold where the gate is not even up.

### Fold `it` submitted as job `1281612`

Queue verified clear of our GPU jobs first (34 queued jobs are all `ps`-partition `openubem` CPU
arrays from another project — FINDING 2 is about GPU jobs and is not violated). This is the last of
the three LOCO folds, and it is **the small shard: 31,560 records / 97 strata, already predicted to
be the weakest fold** at shard-build time. Log will be
`/speed-scratch/o_iseri/4J_step4_leg4_1281612.out` — 🔴 **the fold is not in the filename.**

🔴 **Training `it` is not scoring `it`. D-S6-2 is unaffected by this submission** — it blocks the
Eurostat *scoring* of the `it` fold in Step 6, not the fine-tune, and Italy's ISTAT 2013-14 basis
question is still open and still the author's.

---

# 🟢 2026-08-19 20:02 — ALL FOUR OPEN RULINGS LANDED. AUTHOR RULED D-S4-3 (b), D-S6-2 (a), D-S4-5 (b), D-S4-6 (a).

Ruled in one sitting while fold `it` (job `1281612`) was still `RUNNING` on `speed-39` — no cluster
action was taken to obtain them and none was taken on them before this entry was written. The order
below is the order they were put and answered.

| decision | ruling | class |
|---|---|---|
| **D-S4-3** | **(b)** re-state what `G4.6` is for | **BASIS change**, declared post-hoc |
| **D-S6-2** | **(a)** both renames + score `it` against 2008-09, gap declared | corrections of fact + a **fold-specific basis limitation** |
| **D-S4-5** | **(b)** register a mid-epoch checkpoint basis and re-run all three folds | **BASIS change**, registered *before* the run that reports under it |
| **D-S4-6** | **(a)** one-fold credit counts, fold named every time | reporting rule, no basis moved |

🔴 **Two of the four are basis changes and they are not the same kind.** D-S4-3 re-describes a gate
whose readings are already taken and cannot be re-taken; it is therefore declared **post-hoc** and
must never be presented as pre-registered. D-S4-5 changes *where* a gate is read, so it governs runs
that have not happened yet; it is registered **here, in advance**, and the runs that report under it
are submitted after this entry exists. **No band moved in either.**

## D-S4-3 RULED (b) — `G4.6` is re-stated, not re-banded

**What the gate now claims, stated plainly:** `G4.6` at `1e-4` is a **binary detector for whether the
adapter is exactly zero.** It is not a measure of merge-arithmetic quality and it is not a measure of
how much the adapter trained.

**The evidence that forced the re-statement, all of it already on the record:**

* the α-sweep (job `1274944`): `drift/alpha` varies by **1,850×** across three decades of α, the
  signature of a non-proportional residual — a proportional one moves 1000×;
* the sweep is **not monotonic** — it peaks at `alpha = 0.01`, and the *largest* α gives the
  *smallest* drift. **No mechanism on the record explains that shape and none was invented for it.**
* every non-zero α **FAILs**, including `alpha = 0.001`, where the adapter is scaled to one
  thousandth and the drift is still **6.4× over the band**;
* `alpha = 0` returns exactly `0.000000e+00`, and the repeat-noise floor is exactly `0.000e+00` over
  20,103 positions with TF32 off — so the band **is** resolvable on this hardware and the residual is
  a real, deterministic signal;
* **six independent adapters** now sit between `2.6e-04` and `4.4e-04`; **not one is within 3× of the
  band.**

**What follows, and it is the whole point of ruling (b) rather than (a):** the argument that stood
behind (a) — *"the residual is proportional to how much it learned, so an explained FAIL is honest"* —
**is dead**, killed by the 1,850× figure. Keeping the band and calling the result an explained FAIL
would have kept the number while quietly keeping a story the sweep disproved.

🔴 **CONSEQUENCES, WRITTEN OUT SO NOTHING IS SOFTENED LATER:**

1. `G4.6`'s **`EXPECTED` row no longer describes what the gate does.** The re-statement above replaces
   it, and every place the old wording appears must carry the post-hoc declaration beside it.
2. `G4.6`'s only PASS state is the state the project exists to prove it is **not** in. **It therefore
   cannot be credited as seen falling and `perturb_merged_weight` stays VOID project-wide.**
3. The band **stays at `1e-4`.** Option (c) — re-banding to ~`1.2e-03` so a trained adapter passes —
   was flagged against itself and **rejected on the record**: it is a band relaxed because our own
   artefact fails it.
4. The four bracketing measurements stay attached to the gate wherever it is reported:
   `freeze_adapter` (BA = 0) → `0`; no merge at all → `0`; trained adapter, bf16 compare →
   `13.71875`; trained adapter, fp32 compare → `2.5e-04`..`4.4e-04`.
5. 🔴 **Never quote a single number as "the drift."** `max_logit_diff` moved `3.204e-04` → `2.498e-04`
   between two jobs on a forward pass proven bit-deterministic, which can only be training not being
   bit-reproducible across jobs. Report the range and its six adapters.

**Mechanism, unchanged and still the explanation:** D-S4-1 moved the *comparison* to fp32 but not the
*storage*. The model is loaded bf16, so `merge_adapter()` writes `W + αBA` back into bf16 and
re-rounds every weight. That is deterministic **quantisation** — which is exactly what a zero
repeat-noise floor proves it must be.

## D-S6-2 RULED (a) — both renames accepted, Italy scored against 2008-09 with the gap declared

**(1) The two renames are accepted as corrections of fact.**

| declared in `prereg.md` / `4thJ_06` | corrected to | why |
|---|---|---|
| `tus_00hh` | **`tus_00hhstatus`** | `tus_00hh` **does not exist** — Eurostat returns `ERR_NOT_FOUND_4: TUS_00HH ... is not available for dissemination` and it is absent from the catalogue |
| `tus_20startime` | **`tus_00startime`** | `tus_20` is the HETUS **2020** wave; its coverage is `AT BG DE EE FI NO RS` and **none of ES, IT or UK appear in it at all**. `tus_00startime` covers `{2000, 2010}`, returns data for all three, and carries **145 start-time slots = 10-minute resolution** |

The quantity each threshold is written against is published under the corrected name in both cases,
and the thresholds are expressed against **the quantity, not the string**. `tus_00age`, `tus_00educ`
and `tus_00selfstat` were confirmed correct and need no action.

**(2) Italy's basis — ruled (a).** The `it` fold is scored against Italy's published **2008-09**
Eurostat marginals, and the gap is declared as a **limitation on that fold only**.

🔴 **THE LIMITATION, IN THE WORDS IT MUST BE WRITTEN IN.** Eurostat's ESMS gives the fieldwork behind
the `2010` column per country: **Spain 2009-2010** (= our microdata ✅), **UK 2014-2015**
(= our microdata ✅), **Italy 2008-2009** — but our Italian microdata is **ISTAT 2013-14**, roughly
five years later. Italy's contribution to the European 2010 wave is the *Uso del Tempo 2008-2009*
edition, confirmed independently. **ISTAT 2013-14 appears in no Eurostat HETUS aggregate table at
all** — the 2020 wave has no `IT`. It is a national wave sitting between two European rounds.
**So when Italy is held out, "score against its published aggregate tables" scores 2013-14 diaries
against 2008-09 marginals, and every `it` transfer number carries a ~5-year basis gap.**

🔴 **(3) THE LOCO RESULT IS NOT BASIS-UNIFORM ACROSS ITS FOLDS, AND THAT MUST BE STATED, NEVER
AVERAGED AWAY.** `es` and `uk` are scored on an exact basis; `it` is not. A three-fold mean over those
three numbers hides the one thing a reader needs to know about the third. Report the folds
separately, with `it` carrying the gap in the same sentence as its number.

**Option (c) — re-open decision 16 and swap Italy to the 2008-09 wave — was flagged against itself and
rejected:** it invalidates the corpus, every Step 1–4 gate result and the frozen pre-registration.

🔴 **`prereg.md` IS NOT EDITED AND MUST NOT BE.** md5 stays `e4243e07cdd80c9c846b91f40e3e8c45`, held
in its sidecar. The corrections live in `Step6_docs/4thJ_06_transfer.md` as **declared post-hoc
errata**. Editing the frozen file would fail `G4.14` on every run in the project at once, including
runs that already passed.

**Still not settled by this ruling, and it is now unblocked:** the tables were confirmed to exist, be
reachable and cover our countries; their **contents** have not been compared against anything we
hold, and no §6 threshold has been re-checked for achievability against the real published numbers.

## 🔴 D-S4-5 RULED (b) — THE MID-EPOCH CHECKPOINT BASIS, REGISTERED HERE, BEFORE ANY RUN REPORTS UNDER IT

**This section is the registration. It is written before the trainer was modified and before any
re-run was submitted, and the runs that report under it must postdate this entry.**

### What is being measured and why the epoch boundary is the wrong place to look

`G4.1` compares, per stratum, the generated at-home share against the real at-home share, band
`[0.8, 1.25]`. On **two folds of two**, disjoint training sets, different shard sizes and different
held-out countries:

| checkpoint | `es` (1274884) | `uk` (1274964) | direction |
|---|---|---|---|
| end of epoch 0 | 0 below / **4 above**, worst 1.100/1.664, `end=upper` | 0 below / **2 above**, worst 0.894/1.441, `end=upper` | over-spread |
| end of epoch 1 | **2 below** / 0 above, worst 0.537/0.964, `end=lower (collapse)` | **1 below** / 0 above, worst 0.674/1.234, `end=lower (collapse)` | over-concentrated |

The sign of the miss **inverts** between the only two points we look at, while content loss falls on
both folds (`0.9034 → 0.8887`, `0.8705 → 0.8522`) and `G4.2` PASSes at every checkpoint. **The run
crosses the band inside epoch 1 rather than converging into it** (FINDING 32), and we have never
looked inside that interval. That is the reachability question this basis exists to answer.

### 🔴 THE BASIS, AND THE ONE RULE THAT KEEPS IT FROM BEING A BAND CHANGE IN COSTUME

**The obvious way to run this is cheating and is forbidden here:** probing several mid-points and then
quoting whichever one lands inside the band is **selecting an artefact because it passes** — the same
move as re-banding, wearing different clothes. The registration therefore fixes the reporting
checkpoint **by name, in advance**:

1. **Probe grid.** During the **final epoch only**, `G4.1` is additionally evaluated at the
   **0.25, 0.50 and 0.75** points of that epoch's optimiser steps. A uniform grid, not a search.
2. 🔴 **The verdict checkpoint is the `0.50` point, named now, before any of the three re-runs are
   submitted.** The `0.25` and `0.75` probes are **descriptive context only** — they exist to make
   the crossing visible as a trajectory. **They are explicitly NOT eligible to supply `G4.1`'s
   verdict, on any fold, whatever they read.**
3. **Epoch-end scoring is unchanged and still reported.** The mid-epoch probes are strictly
   **additive**; nothing about the end-of-epoch-0 or end-of-epoch-1 readings moves.
4. **The mid-point is not re-chosen.** If `0.50` misses, the answer is not `0.375`. See the
   pre-registered negative below.

### 🔴 THE NEGATIVE OUTCOME, PRE-REGISTERED BEFORE THE RUNS EXIST

**If the `0.50` checkpoint is outside `[0.8, 1.25]` on any fold, `G4.1` is a standing EXPLAINED FAIL
on that fold and what we report is D-S4-5 option (a) — the outcome this ruling declined.** The
re-runs are not repeated with a different mid-point, the grid is not refined, and the band is not
touched. The mid-epoch basis is then reported as **a reachability question asked and answered in the
negative**, which is a result and must be written as one.

**A second pre-registered negative:** it is entirely possible that no checkpoint anywhere is inside
the band and the trajectory simply passes through it between two probes. That is also an answer, and
the 0.25/0.75 probes are what will make it visible. It is not licence for a finer grid.

### The control this re-run supplies for free, and its known limit

Each re-run re-scores the **same fold, same shard, same recipe** as the closed run. Its end-of-epoch
readings should land near the originals. 🔴 **They will not be identical, and that is not a defect:
training is already established as not bit-reproducible across jobs on this hardware** (the forward
pass is bit-deterministic — repeat-noise floor `0.000e+00` — so the drift between jobs is the training,
which is normal for CUDA and was recorded, not claimed as a fault). **A large divergence in the
epoch-end readings invalidates the re-run's mid-epoch numbers; a small one corroborates them.** No
threshold is pre-set for "large", because none can be justified from two folds — the comparison is
reported and read, not scored.

### Cost, stated before it is spent

Each mid-epoch probe costs one full stratified generation pass (600 diaries) plus one validation
pass. Three probes per fold, three folds. `uk` ran `05:08:26` and `es` `05:17:27` end to end with two
generation passes each, so **expect roughly a doubling per fold.** Folds run **one at a time**
(FINDING 2), named GRES `nvidia_a100_2g.20gb`, `--time=7-00:00:00`.

### 🔴 What this ruling does NOT do

* It does **not** re-band `[0.8, 1.25]`. Option (c) stays flagged against itself and rejected.
* It does **not** make `G4.1` creditable as seen falling. `G4.1` still PASSes at no checkpoint that
  has been read so far, and a gate that is FAIL at baseline cannot be seen falling.
* It does **not** disturb any other gate. Every other Step 4 reading stands on the closed runs.
* It does **not** touch `prereg.md`.

## D-S4-6 RULED (a) — one fold suffices, and the fold is named every time

**The credit stands:** `G4.4` was seen falling on the `es` fold, felled by `blank_evening`, printed by
the FINDING-29-repaired harness itself (`GATES CREDITED AS SEEN FALLING on this probe: ['G4.4']`).

🔴 **THE QUALIFICATION IS NOW MANDATORY, NOT STYLISTIC.** Every mention, in every document, table,
caption and sentence, reads **"`G4.4` was seen falling on the `es` fold."** The unqualified form
**"`G4.4` was seen falling"** is forbidden — on `uk` the gate is FAIL at baseline (morning `0.474`),
so the same perturbation correctly printed `VOID` and the demonstration was **impossible there, not
unsuccessful**. Writing it unqualified over-claims on a fold where the gate is not even up.

**Why (a) and not (b) or (c):** (c) would revoke a demonstration that genuinely happened, which is
under-reporting; (b) binds a rule to a condition — "every fold where the gate PASSes at baseline" —
that is today identical to (a) and would become a hidden new obligation the moment `it` reports.
**(a) with a mandatory qualification says exactly what is true and no more.**

🔴 **Two things this ruling does not decide.** It does not say what happens if the `it` fold reports
`G4.4` PASS at baseline — that fold is still training and its reading is unknown; the credit sentence
simply gains a second fold name if it is also felled there. And it does not generalise beyond
`G4.4`: **a seen-falling credit is fold-specific from here on**, for every gate, which is FINDING 34
promoted from an observation to a reporting rule.

**DoD item 6 stands at NINE gates: `G4.2 G4.4 G4.5 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14`** — with `G4.4`
carrying its fold name and `G4.2` carrying the D-S4-4 forced-basis limitation already declared.

---

## 🟢 2026-08-19 (evening) — THE ADDITIVE ROUND THAT FOLLOWED THE RULINGS. FINDING 30 REPAIRED, AND IT WAS WIDER THAN IT WAS WRITTEN UP.

Done locally while fold `it` (job `1281612`) held the GPU. **Nothing was shipped to Speed** — a
running job's scripts are not overwritten (`bash` reads a running script by byte offset, and the
`it` chain still has `4thJ_step4_diagnostics.py` and `4thJ_step4_genperturb.py` ahead of it). Ship
order is at the end of this entry.

### 🔴 FINDING 30 ESCALATED: THE SAME PREDICATE SAT IN THREE PLACES, AND ONE OF THEM COULD MINT A FALSE SEEN-FALLING CREDIT

FINDING 30 was recorded on `uk` as *"the attribution asks 'is this verdict different from baseline'
and treats `NOT CHECKED` as a move"*, and written up as **a false FINDING flag, not a false credit**.
**Reading the file to repair it showed the predicate governs three sites, not one:**

| site | old test | what it did to an unscored gate |
|---|---|---|
| collateral list (`moved`) | `v.get(g) not in (None, "PASS")` | printed `UNEXPECTED FALL -- FINDING: also moved [...]` — **the reported case** |
| 🔴 **target arm** (`target_down`) | `v.get(target) not in (None, "PASS")` | **counted the target as felled and CREDITED IT AS SEEN FALLING** |
| STAY CLEAN loop | `v[g] not in ("PASS", "REPORTED_NOT_THRESHOLDED")` | printed `was required to STAY CLEAN and did not` |

🔴 **The target arm is the serious one and it was not in the write-up.** A target gate returning
`NOT CHECKED` — which is exactly what happens when the `G4.2` halt stops a run before the later gates
are scored — would have entered `gates seen falling` on a fold where it PASSes at baseline. **That is
a gate credited with a demonstration that never ran**, which is the precise failure DoD item 6 exists
to prevent. It has not fired on any run to date **only because the halt happened to land on a
collateral gate rather than on a target** — luck, not design, and it is recorded as luck.

### The rule now implemented

**A perturbation MOVED a gate only if the gate has an actual verdict and that verdict is `FAIL`.**
`NOT CHECKED`, `NOT RUN`, `VOID`, `REPORTED_NOT_THRESHOLDED` and absence are not verdicts and are not
evidence **in either direction**. Unscored gates are **printed as unscored**, never dropped — *"we did
not measure it"* and *"it was fine"* must not look the same in this table. An unrecognised status now
prints as a FINDING about the harness rather than being silently bucketed as a failure.

### 🔴 THE REPAIR WAS DEMONSTRATED ON A FIXTURE THAT REPRODUCES THE DEFECT, NOT ASSERTED

A four-run fixture (`null` + the three failure modes) was scored by the **pre-repair file** and the
**post-repair file** in turn. Pre-repair output, in full:

```
  collapse_content         OK  target G4.2 -> FAIL
                           UNEXPECTED FALL -- FINDING: also moved ['G4.9']
  sequential_countries     OK  target G4.9 -> NOT CHECKED
  drop_revision            OK  target G4.11 -> FAIL
                           UNEXPECTED FALL -- FINDING: also moved ['G4.7']
                           was required to STAY CLEAN and did not: G4.7 = NOT CHECKED
  gates seen falling:        ['G4.11', 'G4.2', 'G4.9']
  FINDINGS: 2
```

🔴 **`G4.9` is in `gates seen falling` on a run that never scored it, and `sequential_countries` reads
`OK`.** That is the latent defect, reproduced rather than argued. Post-repair, same fixture:

```
  collapse_content         OK  target G4.2 -> FAIL
                           NOT SCORED on this arm: ['G4.9']. ... not counted as moved and
                           not counted as clean (FINDING 30).
  sequential_countries     DID NOT FELL ITS GATE target G4.9 -> NOT CHECKED
                           TARGET NOT SCORED -- G4.9 came back NOT CHECKED, so this row
                           demonstrates NOTHING about it and is not credited.
  drop_revision            OK  target G4.11 -> FAIL
                           G4.7 NOT SCORED -- STAY CLEAN cannot be assessed on a gate this
                           run never reached.
  gates seen falling:        ['G4.11', 'G4.2']
  never made to fall:        [... 'G4.9']
  FINDINGS: 0
```

**Both FINDINGS were false and both are gone; the false credit is gone; `G4.9` correctly returns to
`never made to fall`; and every unscored gate is named.**

### The control, which is what makes the repair safe to ship

A **second** fixture in which **every gate carries a real `PASS`/`FAIL` verdict** — including `G4.6`
FAILing at baseline, as it really does on `es` and `uk` — was scored by both files. 🟢 **The two
outputs are BYTE-IDENTICAL.** The repair therefore touches unscored gates and nothing else, which is
the property that lets it be shipped without re-running anything that has already reported.

`4thJ_step4_perturbtable.py`: **237 → 295 lines**, md5 `df47f30e42ea215d5afae686ed46dc4a` →
**`8a5277b18073055798fc352992faa9b4`**. `diff` removes exactly the three predicate lines and adds
nothing else that was there before.

🔴 **What this repair does NOT do.** It does not retro-fit any table already produced. The
`uk`-fold table that printed the false `also moved ['G4.9']` flag **stays on disk as evidence**, in
the same way FINDING 29's broken table was preserved in `genperturb_f29/`. The finding is corrected
forward, in the log, not erased backwards.

### 🔴 D-S4-5 IS IMPLEMENTED — `4thJ_step4_train.py` 1614 → 1808 LINES, PURELY ADDITIVE

`diff` against the shipped 1614-line file: **194 lines added, ZERO removed.** With the new flag
absent, the schedule dict is empty, the probe is never entered and the run behaves exactly as the
closed folds did — which is the property that makes the `es`/`uk`/`it` results still stand.

md5 `610cd7659001ffe4aaa6720a99ea90a2` → **`f6746949271e0164de0fa31de66499c0`**. Compiles.

**What was added, all of it under the basis registered above:**

* `G41_MIDEPOCH_FRACS = (0.25, 0.50, 0.75)` and `G41_MIDEPOCH_VERDICT_FRAC = 0.50` as **module
  constants**. 🔴 **Deliberately NOT command-line flags.** A flag would let a launcher move the grid
  or the verdict point silently, which is precisely the "probe several, quote the one that passes"
  failure the registration exists to forbid. Changing them requires a **new registered basis in this
  log**, not an edit to the script.
* `--g41-midepoch`, off by default. Additive by construction.
* A schedule that is **computed and PRINTED before the epoch runs**, so the checkpoints are on the
  record ahead of their readings rather than inferred from them afterwards. Each fraction snaps
  **back** to an optimiser-step boundary — probing mid-accumulation would read a model with a partial
  gradient pending, which is not a checkpoint anyone could reproduce. Verified on a schedule
  simulation: at realistic epoch lengths (15,000 / 24,000 / 8,000 steps, `grad_accum` 8) the probes
  land at exactly 0.250 / 0.500 / 0.750.
* **Loud degradation, never silent**: a fraction that snaps below step 0 prints `SKIPPED`, and two
  fractions colliding on one step print `🔴 D-S4-5 COLLISION ... this is a FINDING`. Verified on the
  same simulation at absurd epoch lengths, which is the only way to see those branches.
* Every probe row prints its role — **`VERDICT`** or **`DESCRIPTIVE`** — and each descriptive row
  restates in its own line that it is **not eligible to supply the verdict, whatever it reads**.
* The probe hands training back exactly as it found it: `model.train()` restored and
  `use_cache = False` restored, because generation turns both around and gradient checkpointing
  breaks if they are left that way.
* The basis travels **inside** `detectors_<run>.json` as `D_S4_5_midepoch_basis`, including the
  pre-registered negative in words, so a later reader cannot mistake a mid-epoch number for an
  epoch-end one.
* An end-of-run summary that prints the whole trajectory, names the verdict, and prints the
  pre-registered negative **whether or not it fired** — and, if the verdict checkpoint PASSes, prints
  that **a PASS on a post-hoc-registered basis must be written as one** and never presented as
  pre-registered from the start of Step 4.

**New launcher: `4thJ_step4_ds45_midepoch_fold.sh`.** Named GRES `nvidia_a100_2g.20gb`,
`--time=7-00:00:00`, effective batch held at 16 exactly as the closed folds. 🔴 **It writes to
`4J_step4/runs_ds45`, never `runs`** — the closed folds and their adapters are evidence and are not
overwritten by a re-run. 🔴 **It runs the TRAINER ONLY** — no diagnostics, no genperturb: D-S4-5
concerns `G4.1`'s checkpoint basis and nothing else, and a second set of `G4.3`/`G4.4`/`G4.12`
readings would put two numbers for one gate on the record with nothing to choose between them.

### 🔴 SHIP ORDER — NOTHING IS ON SPEED YET

To be shipped **only after `squeue` shows the queue clear of our GPU jobs**, md5 verified both sides:

| file | local md5 | lines |
|---|---|---|
| `4thJ_step4_train.py` | `f6746949271e0164de0fa31de66499c0` | 1808 |
| `4thJ_step4_perturbtable.py` | `8a5277b18073055798fc352992faa9b4` | 295 |
| `4thJ_step4_ds45_midepoch_fold.sh` | `6e6183011337d58ee9785304eb2e9606` (new) | 73 |

Then, **one at a time** (FINDING 2): `sbatch 4thJ_step4_ds45_midepoch_fold.sh es`, then `uk`, then
`it`.

### 🟢 THE FINDING 30 CONTROL WAS RE-RUN ON REAL DATA, NOT ONLY ON THE FIXTURE

The control reported above was a **synthetic** fixture in which every gate was given a real
`PASS`/`FAIL` verdict. That is the right shape of test but it is a test against a file we wrote
ourselves. It has now been repeated against **the real training-side battery**: the twelve
`detectors_*.json` files of `4J_step4/runs_perturb` — the `es` train-side run, `null` plus its eleven
perturbation arms — pulled off Speed and scored **locally** by the pre-repair file (`/tmp/pt_bk.py`,
md5 `df47f30e42ea215d5afae686ed46dc4a`) and by the repaired file
(`8a5277b18073055798fc352992faa9b4`) in turn.

🟢 **`diff` is empty. 64 lines each, byte-identical, and both exit `1` for the same reason** — the
coverage clause is `FAIL` on that battery because `G4.2` is still in `never made to fall`. The
identical exit code matters as much as the identical text: the repair does not change what the
harness *decides*, only what it is willing to claim about gates it never measured.

This is the property that lets the file be shipped without re-running anything that has already
reported. **It does not retract FINDING 30** — the arm that produced the false flag is a `uk`-fold
arm where the `G4.2` halt fired, and that arm is not in this tree, which is exactly why the fixture
was built in the first place. The two tests answer different questions and both were needed: the
fixture shows the defect is really gone, this control shows nothing else moved with it.

---

## 🟢 2026-08-19 (night) — FOLD `it` CLOSED. ALL THREE LOCO FOLDS ARE NOW REPORTED UNDER THE EPOCH-END BASIS — AND THE THIRD FOLD FALSIFIES FINDING 32.

Job `1281612`, `COMPLETED`, elapsed `03:36:10`, trainer `11980.8 s`, peak VRAM `7.63 GiB`. The full
chain ran: trainer → `4thJ_step4_diagnostics.py` → `4thJ_step4_genperturb.py` → `G4.14` md5 re-check.
🔴 **The `G4.2` halt did not fire on this fold at either epoch**, so unlike the perturbation arms this
run reached and scored every end-of-run gate. Log: `/speed-scratch/o_iseri/4J_step4_leg4_1281612.out`
(318 lines; 🔴 the fold is not in the filename). Adapter:
`4J_step4/runs/leg4_primary_fold_it/adapter`.

Shard: **31,560 train / 3,434 held-in val**, `by_country = es 17,332 + uk 14,228`, held-out-country
records in train **= 0** (`G4.13` PASS). LoRA trainable 24,117,248 / 1,509,033,984 = **1.5982 %**,
identical to the other two folds. `G4.14` PASS, live md5 `e4243e07cdd80c9c846b91f40e3e8c45` =
recorded — the frozen `prereg.md` is intact on Speed.

### 🔴 FINDING 35 — FINDING 32 IS FALSIFIED. THE EPOCH-1 COLLAPSE IS **NOT** SYSTEMATIC; IT IS FOLD-DEPENDENT.

FINDING 32 was written on two folds and stated: *"the epoch-1 collapse is systematic, not an `es`
quirk … two folds out of two, on disjoint training sets … that is not a fold property."* **The third
fold contradicts it, and the contradiction is not marginal — it is the opposite sign.**

| fold | `G4.1` epoch 0 | `G4.1` epoch 1 | direction across the epoch |
|---|---|---|---|
| `es` | FAIL, 0 below / **4 above**, worst 1.100/1.664, `end=upper` | FAIL, **2 below** / 0 above, worst 0.537/0.964, `end=lower (collapse)` | **crossed** the band, upper → lower |
| `uk` | FAIL, 0 below / **2 above**, worst 0.894/1.441, `end=upper` | FAIL, **1 below** / 0 above, worst 0.674/1.234, `end=lower (collapse)` | **crossed** the band, upper → lower |
| **`it`** | FAIL, 0 below / **2 above**, worst 0.996/1.311, `end=upper` | FAIL, 0 below / **6 above**, worst 1.547/**2.010**, `end=upper` | 🔴 **did NOT cross. Moved further above, and all 6 strata are now out of band.** |

Stated carefully, separating what this does and does not overturn:

- **What survives from FINDING 32.** `G4.1` **never PASSes at any checkpoint on any fold in either
  direction** — now 3 folds × 2 epochs = 6 readings, 6 FAILs. That claim is stronger than it was.
- **What is retracted.** *"The run crosses the band rather than converging into it"* is false as a
  general statement. It describes `es` and `uk`. On `it` the run **runs away from the band in the
  direction it started**, ending at `2.010` — the worst single-stratum ratio anywhere in the campaign.
- **What is retracted about the mechanism.** FINDING 32 concluded *"`G4.1` is measuring training
  length."* A quantity that goes down on two folds and up on the third across the same epoch boundary,
  with the same schedule and the same effective batch, is **not** a function of training length alone.
  The honest reduced claim is: **`G4.1` moves substantially within one epoch on every fold, and its
  direction is not predictable from the schedule.** That is enough to motivate D-S4-5 and it is all
  the data supports.
- **What is unchanged.** Content loss falls on all three folds (`it`: 0.9492 → 0.9310, joining `es`
  0.9034 → 0.8887 and `uk` 0.8705 → 0.8522) and `G4.2` PASSes at every epoch of every fold. By the
  losses the second epoch is an improvement on `it` too, while `G4.1` gets **much** worse. The
  loss/`G4.1` divergence first noted on `es` is now confirmed on 3/3.
- 🔴 **`G4.1` remains VOID for DoD item 6 on all three folds.** It is FAIL at baseline everywhere, and
  a gate that is already down cannot be seen falling. That verdict is untouched by this finding.

🔴 **The `it` shard was pre-registered as the PREDICTED WEAKEST fold** (31,560 records, 97 strata, the
small one). On `G4.1` it is the **worst** fold at epoch 1 — consistent with the prediction — but it was
also the **mildest** of the three at epoch 0 (`1.311` vs `1.664` and `1.441`). The prediction is
therefore recorded as **not cleanly borne out**: the ordering depends entirely on which checkpoint is
read, which is itself the D-S4-5 problem restated. Written up here rather than quietly resolved.

### 🔴 CONSEQUENCE FOR D-S4-5, AND IT CHANGES WHAT THE `it` PROBE CAN SHOW

D-S4-5 registered mid-epoch `G4.1` checkpoints at 0.25/0.50/0.75 of the final epoch, and the argument
put to the author was that **`G4.1` crosses its band inside epoch 1**. That argument is now known to
hold on `es` and `uk` and **not** on `it`. The ruling stands as given — it applies to all three folds
and the basis is already registered — but the expectation attached to it must be corrected **before**
the re-runs report, not after:

- On `es` and `uk` the three probe points sit on a trajectory that crosses the band, so a mid-epoch
  reading may land inside `[0.8, 1.25]`.
- 🔴 **On `it` there is no crossing to find.** Both endpoints are above the band and the second is
  further out. The probe will most likely read three points on a monotone climb, and **a mid-epoch
  FAIL on `it` is the expected result, not a surprise and not evidence the probe is broken.**
- The pre-registered negative therefore has real teeth on `it`: **if the `it` verdict checkpoint comes
  back PASS, that is a result the epoch-end readings do not anticipate at all**, and it must be
  reported as such rather than absorbed as a convenient PASS. This is written down here, before the
  run, which is the only time it counts.

### End-of-run gate table, `it`, and the three folds side by side

| gate | `es` (1274884) | `uk` (1274964) | **`it` (1281612)** |
|---|---|---|---|
| `G4.1` | FAIL (see above) | FAIL | **FAIL**, 6 above band, worst **2.010** |
| `G4.2` | PASS both epochs | PASS both epochs | **PASS both epochs** |
| `G4.3` | FAIL, CE rise 0.0929, 2 prefixes unchanged | FAIL, CE rise 0.0755, 1 prefix unchanged | **FAIL, CE rise 0.0682** (need 0.15), 1 prefix unchanged |
| `G4.4` | **PASS** — evening 0.831, morning 0.606 | **FAIL** — evening 0.614 PASS, morning **0.474** FAIL | **PASS** — evening **1.144**, morning **1.123** |
| `G4.6` | FAIL, 3.471e-04 / 20103 pos | FAIL, 3.223e-04 / 16554 pos | **FAIL, 3.853e-04 / 16706 pos** — the largest drift of the three |
| `G4.12` | FAIL, CE rise 0.0053, MI drop 0.085 | FAIL, CE rise 0.0037, MI drop **0.161** | **FAIL, CE rise 0.0043, MI drop 0.199** (clears 0.10; the CE arm is what fails) |
| `G4.5` `G4.7` `G4.8` `G4.9` `G4.11` `G4.13` `G4.14` | PASS | PASS | **PASS** |
| `G4.10` | `REPORTED_NOT_THRESHOLDED` | `REPORTED_NOT_THRESHOLDED` | `REPORTED_NOT_THRESHOLDED` |
| coverage clause | FAIL | FAIL | **FAIL** |

**`G4.6` FAILs on 3/3 folds**, here at `3.853e-04` against a `1e-4` band, with the repeat-noise floor
measured at **`0.000e+00`** from two identical unmerged forward passes (`tf32 matmul=False`,
`cudnn=True`). The floor is below the band on this fold as on the others, so the band is resolvable
here and **the drift is a real signal, not accumulation noise.** Per D-S4-3 → (b) this is re-stated,
not re-banded.

🔴 **Second directional coincidence, recorded without a mechanism attached.** On `it` both `G4.1`
(worst 2.010) and `G4.4` (evening 1.144, morning 1.123) sit **above 1**, where on `es` and `uk` both
sat **below 1**. `G4.4` PASSes on `it` from the *opposite side* of unity from where it PASSed on `es`.
A gate that can pass from either side of its band is not thereby wrong, but the campaign has now seen
it do so, and that is a fact a reader of the `G4.4` column needs. **No mechanism is claimed** — two
gates moving together on one fold is a coincidence until a third observation says otherwise.

### `G4.4` is credited SEEN FALLING on `it` — naming the fold, per D-S4-6 → (a)

Generation-side probe, `genperturb_it.json`, real held-in val 3,434 vs generated 600:

- `blank_evening` → **`G4.4` expected FAIL → FAIL AS EXPECTED.** 🔴 **`G4.4` is credited as seen
  falling ON FOLD `it`.** D-S4-6 → (a) requires the fold be named every time; this credit is not
  transferable to `es` or `uk` without their own arms.
- `G4.1` is **VOID / NOT ASSESSABLE** on every arm — already FAIL at baseline (`null`), and a gate
  down before the perturbation cannot be seen falling.
- `modal_day` changed 594 across 6 strata; `duplicate_500` changed 100, **capped at the cell size** —
  the cell `es|35-44|female|couple_with_children|weekday` is smaller than 500 and the *actual* count
  is reported, not the nominal one; `within_stratum_shuffle` changed 594 with **0 singletons unable
  to move**.
- 🔴 **COVERAGE CLAUSE VERDICT: FAIL.** `G4.7` PASSes at baseline and **was never felled by any
  perturbation on this fold**. A gate that passes and cannot be made to fail has not been shown to
  have power. **This is a FAIL of the probe, not of the model**, and it is the third fold in a row to
  record it.

### D-S4-4 token reconciliation — 🔴 the decomposition CLOSES EXACTLY on this fold

The three delimiter bases printed at both epochs, with the arithmetic between them checked rather
than assumed:

| epoch | `delim(forced)` / tok | `act2-slot` / tok | `delim(all, pre-ruling)` / tok |
|---|---|---|---|
| 0 | **0.0720** / 344,579 | 0.1963 / 76,997 | 0.0947 / 421,576 |
| 1 | **0.0670** / 344,579 | 0.2226 / 76,997 | 0.0954 / 421,576 |

- **Token counts close:** 344,579 + 76,997 = **421,576** exactly. The forced basis and the act2-slot
  remainder partition the all-basis population with nothing left over and nothing double-counted.
- **Rates close:** `(0.0720·344579 + 0.1963·76997)/421576 = 0.094702` vs logged **0.0947**;
  `(0.0670·344579 + 0.2226·76997)/421576 = 0.095419` vs logged **0.0954**. Both to four decimals.
- 🔴 **This is the first time the D-S4-4 decomposition has been closed arithmetically rather than
  reported side by side.** It confirms the ruling did what it was meant to do: the pre-ruling
  all-basis number is inflated by the act2-slot tokens, whose rate (0.1963–0.2226) is roughly **3×**
  the forced rate, and the forced basis is the smaller, cleaner quantity — 0.0670 against 0.0954.
  Note the two bases move in **opposite directions** across the epoch (forced 0.0720 → 0.0670 falls;
  all-basis 0.0947 → 0.0954 rises), driven entirely by the act2-slot rate climbing 0.1963 → 0.2226.
  **Reporting the pre-ruling number would have shown the delimiter rate getting worse when on the
  ruled basis it is getting better.** D-S4-4 is load-bearing, not cosmetic.

### Status after this fold

**All three LOCO folds are now reported under the epoch-end basis.** `G4.6` FAILs on 3/3; `G4.3` and
`G4.12` FAIL on 3/3; `G4.1` is FAIL-at-both-epochs and VOID for DoD item 6 on 3/3; the coverage clause
FAILs on 3/3 with `G4.7` never felled on any of them. `G4.4` is the one gate with a real seen-falling
credit from the generation-side probe — **on `es` and on `it`** — and it is the gate that FAILed at
baseline on `uk`. Nothing here is a band change and nothing here is retracted from an earlier fold;
FINDING 32 is corrected **forward**, in this entry, and its original text stays on disk at line 1310.

### 🟢 STATIC PRE-FLIGHT ON THE D-S4-5 PROBE, BEFORE IT IS GIVEN A GPU

The mid-epoch probe is a **code path that has never executed on real hardware** — the schedule was
verified on a simulation, and a simulation cannot call a model. Committing ~14 GPU-hours across three
folds before seeing it run once is how a night is spent on a defect visible in the first minute, so
the call graph was checked statically first. Four things were checked and all four hold:

1. **The probe measures the SAME WAY as the thing it will be compared against.** Its call is
   argument-for-argument identical to the epoch-end call at line 1319 — same `val_recs` prefixes, same
   `args.gen_n`, same `max_new_tokens=args.max_len`, same `stratified_k`, same `gen_batch`, and the
   same `ref_recs=real_ref` (the FINDING 11 full held-in real set, not the validation split). A probe
   measured differently from its comparator measures nothing, so this was the first thing verified and
   not the last.
2. **`generate_samples` returns `(real_sample, gen_texts)`; the probe takes `[1]`.** Correct element.
   `gate_g4_1(real_texts, gen_texts)` and `detector_delim_vs_content(model, loader, delim_ids, device,
   forced_ids)` both match their definitions positionally.
3. 🔴 **The probe does NOT restore training mode itself — the call site does.** `generate_samples`
   sets `model.eval()` and turns the KV cache back **on** (it must; training disabled it for gradient
   checkpointing). The restore is the two lines immediately after the probe returns, `model.train()`
   and `model.config.use_cache = False`. Had that sat inside the probe's `return` path it would have
   been skipped on any early return. This is the one failure mode that would have crashed the run
   *after* the probe, i.e. hours in, with the probe row already printed and looking fine.
4. **The probe cannot land mid-accumulation.** The schedule snaps each fraction **back** until
   `(step + 1) % grad_accum == 0`, and the probe fires after `opt.step()` / `opt.zero_grad()` for that
   step, so it reads a model with no partial gradient pending. `detectors["midepoch_probes"]` is
   initialised under the same flag that fills `probe_at`, so the append cannot `KeyError`.

**This is a static check and is written up as one.** It shows the wiring is right; it does not show the
probe produces a sane number. That is what submitting `es` **alone** is for.

---

## 2026-08-20 (00:20) — THE D-S4-5 CHAIN IS SUBMITTED FOR ALL THREE FOLDS, AND THE ORDERING DECISION IS RECORDED HERE BECAUSE IT WAS CHANGED

| job | fold | submitted | dependency |
|---|---|---|---|
| `1284898` | `es` | alone, first | — |
| `1284911` | `uk` | 2026-08-20 00:20 | `afterany:1284898` |
| `1284912` | `it` | 2026-08-20 00:20 | `afterany:1284911` |

All three run `4thJ_step4_ds45_midepoch_fold.sh` (md5 `6e6183011337d58ee9785304eb2e9606`) against
`4thJ_step4_train.py` md5 `f6746949271e0164de0fa31de66499c0`, writing to `4J_step4/runs_ds45`, and
each runs the **trainer only** — no diagnostics, no genperturb — so no second set of `G4.3`/`G4.4`/
`G4.12` numbers can reach the record alongside the closed folds'.

`afterany`, not `afterok`: a fold that dies must not silently strand the two behind it. The
dependency chain also **is** FINDING 2's one-GPU-job-at-a-time rule, enforced by the scheduler
instead of by a person watching a queue.

🔴 **The ordering was deliberately changed, and it is written down rather than left implicit.** The
plan of record was *verify the `es` probe on real hardware, then submit `uk` and `it`*. On the
author's instruction the chain was submitted **before** that verification. **This does not weaken the
verification, and the reason is specific:** `1284911` and `1284912` are `PENDING` behind a
dependency, so neither holds a GPU or produces a number until `es` completes. If the `es` schedule
prints `SKIPPED`, `D-S4-5 COLLISION`, or anything other than three checkpoints at 0.250/0.500/0.750,
`scancel 1284911 1284912` kills both before either can report under a probe shown not to work. The
gate is still the `es` schedule; only the submission moved ahead of it.

🔴 **What would make this wrong, stated in advance:** if `uk` or `it` were allowed to run and report
after a defective `es` schedule, this entry becomes the record of a mistake — three folds reporting
under an unverified probe basis. The verification is therefore not optional bookkeeping; it is the
condition under which the two queued jobs are permitted to proceed.

Expectations already registered above and unchanged: on `es`/`uk` a mid-epoch reading may land inside
`[0.8, 1.25]`; 🔴 **on `it` there is no crossing to find and a mid-epoch FAIL is the EXPECTED result**
(FINDING 35), so an `it` PASS at the verdict checkpoint is genuinely unanticipated and must be
reported as such.

---

## 🔴 2026-08-20 (overnight) — FINDING 36: THE D-S4-5 `es` RE-RUN IS AN UNPLANNED EXACT REPLICATE OF FOLD `es`, AND IT SHOWS `G4.1` HAS LARGE RUN-TO-RUN VARIABILITY AT FIXED CONFIGURATION

This was not designed as a replicate and it was not noticed until the re-run's epoch-0 checkpoint was
read against the closed fold. **Job `1284898` re-runs fold `es` under a command line that differs from
the closed job `1274884` in exactly two tokens: `--g41-midepoch` (a flag that touches nothing before
epoch 1) and `--out .../runs_ds45` instead of `.../runs`.** Everything else is byte-identical, and the
logs confirm it rather than the command line alone:

| | `1274884` (closed) | `1284898` (D-S4-5 re-run) |
|---|---|---|
| shard | 48,594 train / 5,520 held-in val | **identical** |
| `G4.13` | `by_country={'it': 34366, 'uk': 14228}`, held-out = 0 | **identical** |
| base checkpoint | `allenai/OLMo-2-0425-1B @ a1847dff35000b4271fa70afc5db10fd29fedbdf` | **identical** |
| trainable | 24,117,248 / 1,509,033,984 = 1.5982 % | **identical** |
| `G4.5` | 2,980,205 pad positions, 0 unmasked | **identical** |
| `G4.14` | `e4243e07cdd80c9c846b91f40e3e8c45` | **identical** |
| `ep0 step0 loss` | **2.0767** | **2.0767** |

🔴 **The two runs are bit-identical at step 0 and diverge immediately afterwards** — `step200`
0.8448 vs 0.8472, `step400` 0.7261 vs 0.7247, `step600` 0.6901 vs 0.6923, `step800` 0.5859 vs 0.5875.
Same initialisation, same first batch, same order; the divergence is floating-point non-determinism in
the GPU kernels, amplified over 24,297 optimiser steps. **This is the only replicate pair in the entire
Step 4 campaign**, and it arrived by accident.

### What reproduces, and what does not

End of **epoch 0**, the same code path in both runs (the D-S4-5 patch is additive and does not execute
before epoch 1):

| quantity at end of epoch 0 | `1274884` | `1284898` | Δ |
|---|---|---|---|
| `delim` on the **all / pre-ruling** basis | **0.1020** | **0.1020** | **0.0000** |
| content loss | 0.9034 | 0.9039 | +0.0005 |
| entropy | 3.284 | 3.282 | −0.002 |
| `G4.2` | PASS | PASS | — |
| gen-terminated | 600/600 | 600/600 | — |
| `ep1 step0 loss` | 0.4744 | 0.4750 | +0.0006 |
| 🔴 `G4.1` strata **above** band | **4** | **2** | **−2 of 6** |
| 🔴 `G4.1` worst_low | **1.100** | **0.970** | **−0.130** |
| 🔴 `G4.1` worst_high | **1.664** | **1.553** | **−0.111** |

**The aggregate scalars reproduce to three or four decimals. The `G4.1` per-stratum panel does not.**
The count of out-of-band strata **halved**, and `worst_high` moved by `0.111` — **25 % of the width of
the band `[0.8, 1.25]` itself** (0.45). `worst_low` moved from `1.100`, comfortably above the band, to
`0.970`, which is **inside** it: a stratum that was out of band in one run is in band in the other,
with no change to the configuration.

### 🔴 What this does and does not overturn

- **The verdict does not move.** `G4.1` FAILs at epoch 0 in both runs, and `end=upper` in both. No
  conclusion recorded anywhere in this log flips. **Nothing is retracted.**
- **What it costs is the precision of every `G4.1` number the campaign has quoted.** "4 strata above,
  worst 1.664" is a single draw. The replicate says the same run re-executed gives "2 strata above,
  worst 1.553". 🔴 **`G4.1` counts and worst-ratios must therefore never be compared across folds at
  a resolution finer than this replicate spread**, and the three-fold table in FINDING 35 must be read
  with that in mind. FINDING 35's *direction* claim survives — `it` ending `end=upper` with all 6
  strata above and `worst 2.010` is far outside a `0.11` spread — but its finer orderings do not.
- 🔴 **This is one replicate pair, `n = 1`.** It demonstrates the variability is **at least** this
  large. It does not estimate it. No standard deviation is claimed and none should be quoted.

### 🔴 CONSEQUENCE FOR D-S4-5 — REGISTERED BEFORE THE VERDICT CHECKPOINT IS READ

D-S4-5 puts the verdict on a single mid-epoch `G4.1` reading at frac 0.50. This finding says that
reading carries a repeat spread of order `0.11–0.13` in ratio units on a band `0.45` wide.

**Therefore, registered here, before frac 0.50 has printed anything:**

- 🔴 **A mid-epoch `G4.1` that lands inside `[0.8, 1.25]` but within ~`0.13` of either edge is NOT
  distinguishable from the replicate spread and MUST NOT be reported as a PASS on its own.** It is
  reported as a reading inside the band whose margin is smaller than the measured repeat spread.
- A mid-epoch reading that clears both edges by more than that spread is a genuine PASS.
- A mid-epoch FAIL is unaffected — the gate is already FAIL at both endpoints on this fold, and noise
  of this size cannot manufacture a FAIL out of a comfortable PASS.

This is the same discipline already applied to `G4.6`, where the repeat-noise floor was measured at
`0.000e+00` and the drift was therefore declared real. **Here the floor is large relative to the band,
and the honest consequence runs the other way.** No band is being changed and no result is being
excused: the band stays `[0.8, 1.25]`, and what is being written down is the resolution at which it
can be read.

### 🔴 A SECOND REPLICATE POINT IS COMING — THE EXPECTATION IS REGISTERED NOW, BEFORE IT PRINTS

Job `1284898` will also produce an **end-of-epoch-1** reading on the same basis as the closed run, so
the campaign gets a second replicate point for free. The closed run gave epoch 1 = **FAIL, 2 below /
0 above, worst 0.537/0.964, `end=lower (collapse)`**. Written down before the re-run reports:

- **Expected:** FAIL, `end=lower`, with counts and worst-ratios differing by roughly the epoch-0
  spread. That would confirm both the replicate spread and FINDING 35's `es` direction.
- 🔴 **If the re-run's epoch 1 comes back `end=upper`, the direction claim in FINDING 35 is itself
  unstable**, and FINDING 35 must be corrected forward exactly as it corrected FINDING 32. That
  outcome is named here so it cannot later be absorbed as a curiosity.

### D-S4-4 closes on `es` too — first time it has been checked on this fold

The closed `es` run predates D-S4-4 and reported only the pre-ruling number, `delim=0.1020`. The
re-run prints all three bases at epoch 0:

| basis | rate | tokens |
|---|---|---|
| `delim(forced)` — the ruled basis | **0.0591** | 555,651 |
| `act2-slot` remainder | 0.3018 | 119,518 |
| `delim(all, pre-ruling)` | 0.1020 | 675,169 |

`555,651 + 119,518 = 675,169` exactly, and
`(0.0591·555651 + 0.3018·119518)/675169 = 0.102063` against the logged `0.1020`. 🟢 **The
decomposition closes on `es` as it did on `it`, and the all-basis rate `0.1020` reproduces the closed
run's headline number to four decimals** — which is a third, independent confirmation that the two runs
really are the same run, and that D-S4-4 re-partitioned the same token population rather than changing
what was measured.

---

## 🟢 2026-08-20 (overnight) — D-S4-5, FOLD `es`, FRAC 0.25 REPORTED: A **NEGATIVE**, AND THE EXPECTATION FOR FRAC 0.50 / 0.75 IS REGISTERED **BEFORE** EITHER PRINTS

Job `1284898`, fold `es`, still `RUNNING`. Two structural facts and one result, in the order the log
produced them.

**Structural — the role label precedes the number, demonstrated twice on real hardware.** Line 208
opened the frac 0.25 checkpoint with `[DESCRIPTIVE]` and line 252 opened frac 0.50 with `[VERDICT]`,
each *before* its 600 diaries were generated and therefore before any number existed. The descriptive
row also carried its restatement clause (*"NOT eligible to supply `G4.1`'s verdict, whatever it
reads"*). The snapped boundaries are exact: `6072 = 8 × 759`, `12144 = 8 × 1518`. 🟢 **No `SKIPPED`
and no `D-S4-5 COLLISION` line anywhere in the file.** This is the anti-post-hoc property of the
D-S4-5 implementation observed rather than asserted from the source.

**Result — frac 0.25, stamped `DESCRIPTIVE` at both ends of the row:**
```
[ep 1 frac 0.25] G4.1 FAIL [6 strata, 0 below / 4 above band [0.8, 1.25], worst 1.104/1.622, end=upper]
                 delim=0.0604 content=0.8985 entropy=3.339  DESCRIPTIVE
```

🔴 **This must be read against FINDING 36's replicate spread, and when it is, it is a negative.**
Against this run's *own* epoch 0 (`0 below / 2 above, worst 0.970/1.553`) the frac-0.25 point moved
`worst_low` **+0.134**, `worst_high` **+0.069**, and the out-of-band count `2 → 4`. FINDING 36
measured the run-to-run spread at fixed configuration as **0.130** on `worst_low`, **0.111** on
`worst_high`, and **2 strata** on the count. The movement is the same size as the noise. The claim
this log will make is therefore the weak one, which is the only one the data supports:

> **After 25 % of the final epoch, `G4.1` on `es` has not moved by more than the replicate spread.**
> No movement toward the band is detectable, and whatever produces the end-of-epoch-1 collapse to
> `end=lower (collapse)` happens **later than the first quarter of that epoch.**

Equivalently, the frac-0.25 point lies inside the envelope spanned by the two epoch-0 replicates on
every one of the three numbers (`4 ∈ {2,4}`; `1.104` against `1.100` and `0.970`; `1.622` between
`1.553` and `1.664`).

**Aggregates.** `delim(forced)` `0.0591 → 0.0604`, content `0.9039 → 0.8985`, entropy `3.282 →
3.339`. 🔴 The content loss **falls** while `G4.1` does not improve. The loss/`G4.1` divergence
recorded at the epoch boundary on 3/3 folds is now seen **within** a single epoch as well, which
removes "the epoch boundary does something special" as an explanation for it.

### 🔴 REGISTERED NOW, BEFORE FRAC 0.50 AND FRAC 0.75 PRINT

On `es` the two endpoints are known (`end=upper` at epoch 0, `end=lower (collapse)` at epoch 1) and
frac 0.25 is now known to be indistinguishable from the epoch-0 endpoint. The crossing therefore lies
in `(0.25, 1.0]` of epoch 1. Written down before the readings exist:

- **Expected:** frac 0.50 and frac 0.75 trace the crossing — at least one of them differs from
  epoch 0 by **more** than the `0.13` spread, and frac 0.75 is at or below frac 0.50.
- 🔴 **If frac 0.50 AND frac 0.75 are BOTH still indistinguishable from epoch 0**, then the entire
  `es` collapse occurs in the **last quarter** of epoch 1, and a three-point schedule at
  0.25/0.50/0.75 is **too coarse to locate it**. That is a limitation of the D-S4-5 basis as ruled,
  it would be reported as one, and it is registered here rather than discovered afterwards.
- 🔴 **A frac 0.50 reading inside `[0.8, 1.25]` but within ~`0.13` of either edge is NOT a PASS**
  (FINDING 36's resolution rule). This is restated here so that it cannot be quietly dropped when the
  number arrives.
- Nothing in this entry changes a band, a basis, or any fold's verdict.

---

## 🔴 2026-08-20 (overnight) — D-S4-5 VERDICT CHECKPOINT, FOLD `es`: **`G4.1` FAIL.** THE MID-EPOCH BASIS DOES NOT RESCUE `G4.1` ON THIS FOLD, AND THE PRE-REGISTERED "TOO COARSE" BRANCH IS THE ONE THE DATA IS TAKING.

Line 263 of `/speed-scratch/o_iseri/4J_step4_ds45_1284898.out`, stamped `VERDICT` at the end of the
row as well as in its header:

```
[ep 1 frac 0.50] G4.1 FAIL [6 strata, 0 below / 1 above band [0.8, 1.25], worst 0.850/1.650, end=upper]
                 delim=0.0816 content=0.8926 entropy=3.209  VERDICT
```

🔴 **The verdict checkpoint registered under D-S4-5 for fold `es` is a FAIL.** D-S4-5 was granted so
that `G4.1` would get a reading that was not an artefact of stopping at an epoch boundary. On `es`
that reading is still a FAIL. This is stated plainly and is not softened anywhere in this project's
outputs.

### The FAIL is ROBUST under FINDING 36's resolution rule — the rule is applied, not waived

| quantity | value | band edge | margin | FINDING 36 spread | margin / spread |
|---|---|---|---|---|---|
| `worst_high` | **1.650** | 1.25 (upper) | **0.400 outside** | 0.111 | **3.6×** — resolvable |
| `worst_low` | 0.850 | 0.80 (lower) | 0.050 inside | 0.130 | 0.38× — 🔴 **NOT resolvable** |

- **The FAIL stands on `worst_high`**, which is outside the band by 3.6× the measured replicate
  spread. There is no reading of FINDING 36 under which this becomes a PASS.
- 🔴 **The corollary must not be dropped: the claim "the low end has entered the band" CANNOT be
  made.** `0.850` sits `0.050` inside a lower edge whose own resolution is `0.130`. That sub-claim is
  unresolvable and is not asserted.

### 🔴 THE PRE-REGISTERED EXPECTATION IS **NOT** CONFIRMED — the second branch is what happened

Registered in this log before frac 0.50 printed: *"at least one of frac 0.50 / frac 0.75 differs from
epoch 0 by MORE than the `0.13` spread"*, with the alternative that if both are indistinguishable
then the schedule is **too coarse to locate the `es` collapse**. Measured against this run's own
epoch 0 (`0 below / 2 above, worst 0.970/1.553, end=upper`):

| frac 0.50 vs its own epoch 0 | Δ | spread | resolvable? |
|---|---|---|---|
| `worst_low` `0.970 → 0.850` | **−0.120** | 0.130 | **no** |
| `worst_high` `1.553 → 1.650` | **+0.097** | 0.111 | **no** |
| strata above `2 → 1` | −1 | 2 strata | **no** |
| `end=` | `upper → upper` | — | unchanged |

**Not one of the three is resolvable.** Halfway through the final epoch, `G4.1` on `es` is still not
distinguishable from where it was at the end of epoch 0 — and the epoch-1 endpoint of the replicate
run is `0 above / 2 below, worst 0.537/0.964, end=lower (collapse)`, which is nowhere near this. So
unless frac 0.75 moves resolvably, **the entire `es` band crossing occurs in the last quarter of
epoch 1 and the 0.25/0.50/0.75 schedule cannot locate it.** That limitation was written down before
the data arrived; it is now the live branch, and it will be reported as a limitation of the D-S4-5
basis as ruled — not quietly absorbed.

### 🔴 The more damaging observation: within-epoch fluctuation is as large as between-run fluctuation

The three mid-epoch points do **not** trace a monotone path. Taking the panel width `worst_high −
worst_low` as a crude dispersion measure:

| checkpoint | below / above | `worst_low` | `worst_high` | width | `end=` |
|---|---|---|---|---|---|
| epoch 0 | 0 / 2 | 0.970 | 1.553 | 0.583 | upper |
| frac 0.25 | 0 / **4** | 1.104 | 1.622 | 0.518 | upper |
| **frac 0.50 (VERDICT)** | 0 / **1** | **0.850** | **1.650** | **0.800** | upper |
| epoch 1 END (replicate `1274884`) | **2** / 0 | 0.537 | 0.964 | 0.427 | **lower** |

`worst_low` moves `1.104 → 0.850` between frac 0.25 and frac 0.50 — **−0.254, about 2× the replicate
spread and therefore resolvable** — while neither point is resolvably displaced from epoch 0. The
out-of-band count goes `2 → 4 → 1`. 🔴 **`G4.1` fluctuates within a single epoch by more than the
run-to-run spread, without making resolvable net progress toward its band.** For a gate that is meant
to carry a verdict, that is a worse property than a simple drift would be, and it is recorded here as
an observation about the *gate*, not about the model.

🔴 **Honesty about the yardstick:** the `0.130` / `0.111` spread comes from **one** replicate pair at
**one** checkpoint (FINDING 36, `n = 1`). Using it at mid-epoch checkpoints is an extrapolation. It is
used here only to say what is **not** resolvable — the conservative direction — and no standard
deviation is quoted anywhere.

### Aggregates along epoch 1, for the record

| checkpoint | `delim(forced)` | content | entropy |
|---|---|---|---|
| epoch 0 | 0.0591 | 0.9039 | 3.282 |
| frac 0.25 | 0.0604 | 0.8985 | 3.339 |
| frac 0.50 | **0.0816** | 0.8926 | 3.209 |

The forced-basis delimiter rate rises monotonically and the last step is large (+0.021, ~35 % of its
own value) while the content loss falls monotonically. 🔴 The loss/`G4.1` divergence recorded at the
epoch boundary on 3/3 folds is confirmed **within** an epoch: content loss improves at every one of
these checkpoints and `G4.1` does not.

### What this does and does not change

- **Does not change:** any band, any basis, any earlier fold's verdict, or `G4.1`'s **VOID** status
  for DoD item 6 (it is FAIL at baseline everywhere, and a gate already down cannot be seen falling).
- **Adds:** `G4.1` is now FAIL at **three** checkpoints on `es` in this run (epoch 0, frac 0.25,
  frac 0.50) on top of 3 folds × 2 epochs = 6 epoch-end FAILs. **`G4.1` has never PASSed at any
  checkpoint, on any fold, under any basis, in this campaign.**
- 🔴 **Says explicitly:** the D-S4-5 mid-epoch basis, which was argued for and granted on the strength
  of a real phenomenon, **does not turn `G4.1` into a passing gate on `es`.** Folds `uk` (`1284911`)
  and `it` (`1284912`) are still queued; `it` was already pre-registered as expected-FAIL (FINDING 35).

---

## 🔴 2026-08-20 (overnight) — FINDING 37: `G4.1` **PASSES** AT FRAC 0.75 ON `es` — THE FIRST PASS IN THE CAMPAIGN. IT IS A `DESCRIPTIVE` CHECKPOINT, IT DOES NOT SUPPLY THE VERDICT, AND IT IS NOT ROBUST EITHER. THE VERDICT FOR `es` REMAINS **FAIL**.

Line 308 of `/speed-scratch/o_iseri/4J_step4_ds45_1284898.out`:

```
[ep 1 frac 0.75] G4.1 PASS [6 strata, 0 below / 0 above band [0.8, 1.25], worst 0.974/1.182, end=none]
                 delim=0.0603 content=0.8916 entropy=3.195  DESCRIPTIVE
```

**`G4.1` has passed. For the first time anywhere in this campaign, all six strata are inside
`[0.8, 1.25]` and `end=none`.** And it changes **nothing** about fold `es`'s verdict, for two
independent reasons, each of which was written down **before** the number existed.

### 🔴 REASON 1 — it is a `DESCRIPTIVE` checkpoint. This is exactly the case D-S4-5 was built to stop.

D-S4-5 registered **frac 0.50 as the sole verdict checkpoint** and 0.25/0.75 as descriptive, and the
trainer stamps the role into the log **when the checkpoint opens, before the 600 diaries are
generated** — observed three times in this run (lines 208, 252, 296). The frac 0.75 row carried its
restatement clause: *"NOT eligible to supply `G4.1`'s verdict, whatever it reads."*

🔴 **The verdict for fold `es` is the frac 0.50 reading: `G4.1` FAIL, 1 stratum above, worst
0.850/1.650, `end=upper`.** The frac 0.75 PASS is reported, in full, and is **not** promoted to a
verdict. Had the verdict fraction been chosen after seeing these three numbers, `es` would read PASS.
It was not, and it does not.

**This is the entry that shows the pre-registration was load-bearing rather than ceremonial.** Every
prior pre-registration in this project cost nothing to honour, because the result went the way the
registration expected. This one costs a PASS — the only one the campaign has produced — and it is
still honoured. That is the whole value of having written it down first.

### 🔴 REASON 2 — even ignoring reason 1, the PASS is NOT robust under FINDING 36

| quantity | value | nearest edge | margin **inside** | spread (FINDING 36) | margin / spread |
|---|---|---|---|---|---|
| `worst_high` | **1.182** | 1.25 | **0.068** | 0.111 | 🔴 **0.61× — NOT resolvable** |
| `worst_low` | 0.974 | 0.80 | 0.174 | 0.130 | 1.34× — marginally resolvable |

FINDING 36's rule, registered before frac 0.50 printed: *a reading inside `[0.8, 1.25]` but within
~`0.13` of an edge is not reportable as a PASS on its own.* **`worst_high` clears its edge by
`0.068`, roughly six-tenths of the measured replicate spread.** So even if this had been the verdict
checkpoint, the correct report would have been *"inside the band, with a margin smaller than the
run-to-run spread"* — not a PASS. Both pre-registered rules point the same way, independently.

### 🔴 CORRECTION FORWARD — the "schedule is too coarse" branch is FALSIFIED

The previous entry registered two branches and said the second was live: *"unless frac 0.75 moves
resolvably, the entire `es` crossing sits in the last quarter and the 0.25/0.50/0.75 schedule cannot
locate it."* **Frac 0.75 moved.** Against this run's own epoch 0 (`0.970/1.553`):

| frac 0.75 vs epoch 0 | Δ | spread | resolvable? |
|---|---|---|---|
| `worst_high` `1.553 → 1.182` | **−0.371** | 0.111 | 🟢 **yes, 3.3×** |
| `worst_low` `0.970 → 0.974` | +0.004 | 0.130 | no |
| strata above `2 → 0` | −2 | 2 strata | at the spread |

🔴 **The pre-registered expectation is therefore CONFIRMED, at frac 0.75, and the "too coarse"
limitation is withdrawn.** The schedule *does* locate the movement: on `es` the upper crossing
happens **between frac 0.50 and frac 0.75**, and the lower crossing to `end=lower (collapse)` happens
**after frac 0.75**. The previous entry's text stays on disk as written; this is the correction,
forward, in the same form used for FINDING 32 → 35.

### What the four checkpoints actually show: `G4.1` **transits** the band

| checkpoint | below / above | `worst_low` | `worst_high` | `end=` | role |
|---|---|---|---|---|---|
| epoch 0 | 0 / 2 | 0.970 | 1.553 | upper | epoch-end |
| frac 0.25 | 0 / **4** | 1.104 | 1.622 | upper | DESCRIPTIVE |
| **frac 0.50** | 0 / 1 | 0.850 | 1.650 | upper | 🔴 **VERDICT — FAIL** |
| frac 0.75 | **0 / 0** | 0.974 | **1.182** | **none** | DESCRIPTIVE — **PASS**, not robust |
| epoch 1 END (replicate `1274884`) | **2** / 0 | 0.537 | 0.964 | **lower** | epoch-end |

**`G4.1` on `es` starts above its band, stays above through half the final epoch, passes *through* the
band around three-quarters, and exits below it by the end.** The gate is satisfied only **transiently**,
in a window the run passes through, and the epoch-end basis that Step 4 was originally specified on
lands on the far side of it. That is the strongest statement this campaign can make about `G4.1`, and
it is only visible because D-S4-5 was ruled and implemented.

🔴 **It also means `G4.1`'s reading is a function of where you stop**, which is precisely the criticism
D-S4-5 was raised to answer — the answer turns out to be *yes, and severely*. A gate whose verdict
depends on the stopping point to this degree cannot carry a headline claim on its own, and the paper
must say so.

### Correction forward, second item

The previous entry stated *"the forced-basis delimiter rate rises monotonically"*, on three points.
**Falsified by the fourth:** `0.0591 → 0.0604 → 0.0816 → 0.0603`. It is **not** monotone; frac 0.50 is
a spike. Content loss remains monotone-falling across all four (`0.9039 → 0.8985 → 0.8926 → 0.8916`)
and entropy is `3.282 → 3.339 → 3.209 → 3.195`. 🔴 The loss/`G4.1` relationship is now clearly not a
simple one: the content loss improves smoothly and monotonically while `G4.1` goes above-band →
in-band → below-band across the same four points.

### Standing after this finding

- **`es` D-S4-5 verdict: `G4.1` FAIL** (frac 0.50). Unchanged by the PASS at 0.75.
- 🔴 The campaign-wide claim *"`G4.1` has never PASSed at any checkpoint"* — written one entry ago —
  **is now false and is retracted here.** It passed once, at a descriptive checkpoint, non-robustly.
  The claim that survives is: **`G4.1` has never PASSed at a checkpoint eligible to supply a verdict.**
- `G4.1` remains **VOID** for DoD item 6 (FAIL at baseline on every fold; a gate already down cannot
  be seen falling).
- No band, no basis, and no earlier fold verdict is changed.
- Folds `uk` (`1284911`) and `it` (`1284912`) are queued. 🔴 **FINDING 35 pre-registered `it` as
  expected-FAIL mid-epoch; that stands, and this `es` transit does not license expecting a transit
  on `it`, whose two endpoints are BOTH above the band.**

---

## 🔴 2026-08-20 (overnight) — FINDING 38: THE SECOND REPLICATE POINT. THE EPOCH-1 SPREAD IS **LARGER** THAN THE EPOCH-0 SPREAD, `G4.6`'s FOLD ORDERING IS NOT RESOLVABLE, AND `G4.1` STILL HAS NO REPEAT-NOISE FLOOR.

Job `1284898` **`COMPLETED`, `06:01:06`, exit `0:0`**, trainer `21569.3 s`, peak VRAM `7.67 GiB`,
adapter written to `runs_ds45/leg4_primary_fold_es/adapter` (🟢 **not** `runs`; the closed folds are
untouched). `G4.14` re-verified at the end of the run: live md5 `e4243e07cdd80c9c846b91f40e3e8c45` =
the sidecar. `uk` `1284911` was released by the dependency and is now `RUNNING` on `speed-43`.

### The trainer's own summary block — machine-written, quoted verbatim

```
================ D-S4-5 MID-EPOCH BASIS, FOLD es ================
  frac 0.25  step 6072/24297   G4.1 FAIL  DESCRIPTIVE  0 below / 4 above, end=upper
  frac 0.50  step 12144/24297  G4.1 FAIL  VERDICT      0 below / 1 above, end=upper
  frac 0.75  step 18216/24297  G4.1 PASS  DESCRIPTIVE  0 below / 0 above, end=none
G4.1 ON THE D-S4-5 BASIS (frac 0.50, the checkpoint named in advance): FAIL
```

**The verdict line is produced by the code, not by this log's prose**, and it names the fraction as
*the checkpoint named in advance*. FINDING 37's conclusion is therefore not an interpretation imposed
after the fact.

### 🔴 STEP 3 OF THE ORDER — THE REGISTERED PREDICTION IS ONLY PARTLY CONFIRMED

Registered before the reading: *FAIL, `end=lower`, differing by about the epoch-0 spread*, with the
trigger *if it comes back `end=upper`, FINDING 35's direction claim is unstable*.

| end of epoch 1 | closed `1274884` | re-run `1284898` | Δ | vs epoch-0 spread |
|---|---|---|---|---|
| `delim(all, pre-ruling)` | 0.0974 | **0.0974** | **0.0000** | — |
| content loss | 0.8887 | **0.8887** | **0.0000** | — |
| entropy | 3.282 | 3.302 | +0.020 | — |
| `G4.2` | PASS | PASS | — | — |
| gen-terminated | 600/600 | 600/600 | — | — |
| `G4.1` strata **below** | 2 | **2** | 0 | — |
| `G4.1` strata **above** | 0 | **1** | **+1** | — |
| 🔴 `worst_low` | 0.537 | **0.731** | **+0.194** | **1.5×** |
| 🔴 `worst_high` | 0.964 | **1.325** | **+0.361** | **3.3×** |
| 🔴 `end=` | `lower (collapse)` | **`both`** | changed | — |
| `G4.6` | 3.471e-04 | **3.090e-04** | −0.381e-04 | — |

- 🟢 **FAIL: confirmed.** Both runs FAIL, and `2 below` reproduces exactly.
- 🔴 **`end=lower`: NOT confirmed — it is `end=both`**, a state this campaign has not seen before
  (`es` and `uk` were `end=lower`, `it` was `end=upper`).
- 🔴 **"about the epoch-0 spread": NOT confirmed.** The epoch-1 deltas are **1.5×** and **3.3×** the
  epoch-0 ones. **The replicate spread is larger at the later checkpoint.**

**FINDING 35's trigger did not fire** — `end=both` is not `end=upper`, and the two strata below the
band reproduce exactly, so the claim that `es` crosses to the low side stands and is **not** retracted.
What is refined is the *descriptor*: "the panel crosses the band" is too tidy. On this replicate the
panel ends with strata on **both** sides at once. It **disperses across** the band rather than
translating through it as a block.

### 🔴 CONSEQUENCE 1 — FINDING 36's YARDSTICK UNDERSTATES THE SPREAD, WHICH ONLY HARDENS FINDING 37

FINDING 36 measured `0.130` / `0.111` at the **epoch-0** checkpoint. The epoch-1 pair gives
`0.194` / `0.361` on the same two quantities. 🔴 **The `0.13` figure quoted throughout the last three
entries is a LOWER bound on the relevant spread at late-epoch checkpoints, not an estimate of it.**

Checked rather than assumed, against every conclusion already drawn:

- **FINDING 37's refusal of the frac 0.75 PASS gets stronger.** `worst_high 1.182` clears its edge by
  `0.068`. Against `0.111` that was `0.61×`; against the epoch-1 spread `0.361` it is **`0.19×`**. The
  PASS is *less* resolvable than stated, not more.
- **The frac 0.50 FAIL stays robust, but by less.** `worst_high 1.650` is `0.400` outside the band =
  **1.1×** even the larger spread. 🔴 **The `3.6×` figure in the previous entry is corrected forward
  here to ~`1.1×`.** The verdict does not change; the confidence attached to it must.
- 🔴 **No `G4.1` count or worst-ratio may be compared across folds at all** until a proper floor
  exists. FINDING 36 said "not at a finer resolution than `0.13`". With `n = 2` pairs disagreeing by a
  factor of three on the same quantity, the honest position is that **the resolution is unknown.**

### 🔴 CONSEQUENCE 2 — `G4.6`'s FOLD ORDERING IS NOT RESOLVABLE, AND AN EARLIER CLAIM IS CORRECTED

`G4.6` is the one gate with a measured *within-run* repeat-noise floor (`0.000e+00`, two identical
unmerged forward passes). This replicate gives it a **between-run** spread for the first time:
**`|3.471 − 3.090| = 3.81e-05`.** These are different quantities, and only the second is the right one
for comparing runs to each other.

| comparison | difference | vs the `3.81e-05` spread | resolvable? |
|---|---|---|---|
| `it` 3.853e-04 vs `es` 3.471e-04 | 3.82e-05 | **1.00×** | 🔴 **no** |
| `es` 3.471e-04 vs `uk` 3.223e-04 | 2.48e-05 | 0.65× | 🔴 **no** |
| `it` 3.853e-04 vs `uk` 3.223e-04 | 6.30e-05 | 1.65× | marginal at best |
| every fold vs the `1e-4` band | 2.2–2.9e-04 | 5.8–7.6× | 🟢 **yes — the FAILs are real** |

🔴 **CORRECTION FORWARD.** The fold-`it` entry states that `G4.6` on `it` is *the largest drift of the
three*. **That claim is not supported** — `it` exceeds `es` by exactly one replicate spread. The
original text stays on disk. What survives: **`G4.6` FAILs its `1e-4` band on 3/3 folds by 5–8× the
between-run spread, and the three folds cannot be ranked against one another.**

### 🔴 CONSEQUENCE 3 — WHERE `G4.1`'s NOISE COMES FROM

Look at what reproduces and what does not, at **both** epoch checkpoints:

| quantity | basis | epoch 0 | epoch 1 | reproduces? |
|---|---|---|---|---|
| `delim(all)` | 675,169 teacher-forced tokens | 0.1020 vs 0.1020 | 0.0974 vs 0.0974 | 🟢 **exactly, 4 dp** |
| content loss | held-in val set | 0.9034 vs 0.9039 | 0.8887 vs 0.8887 | 🟢 **3–4 dp** |
| `G4.1` panel | **600 stochastically generated diaries, 100 per stratum** | 4 above vs 2 above | `end=lower` vs `end=both` | 🔴 **no** |

**Token-level aggregates over 675k tokens are stable to four decimals across the replicate. The
six-stratum `G4.1` panel, built from 100 sampled diaries per cell, is not.** The natural reading is
that `G4.1`'s instability is **sampling variance in the generation step**, not instability in the
weights — the same weights produce identical aggregates. 🔴 **This is a hypothesis, not a result.** It
is recorded as one, and it is directly testable.

### 🔴 OWED, AND THIS ENTRY IS WHY: `G4.1` HAS NO REPEAT-NOISE FLOOR

`G4.6` has one because someone asked whether its drift was real, and the trainer now measures it every
run. **`G4.1` — the gate this entire D-S4-5 decision was about — has never had one.** The measurement
is cheap and exactly analogous: **regenerate the 600 diaries at fixed merged weights under a second
seed and re-score `G4.1`.** No training, one generation pass. It would convert every
"resolvable / not resolvable" judgement in FINDINGS 36–38 from an `n = 1` or `n = 2` extrapolation
into a measured floor, and it would settle whether the source is sampling or weights.

🔴 **It is a NEW MEASUREMENT, not a band change and not a basis change** — `G4.1`'s band `[0.8, 1.25]`
and its per-stratum definition are untouched by it, exactly as `G4.6`'s floor left `1e-4` untouched.
On that reading it needs no author ruling. **It is nevertheless recorded as an open item for the
author to confirm that reading**, because this project registers a basis change before the run that
reports under it, and the line between "new measurement" and "new basis" is the author's to draw.

### D-S4-4 closes arithmetically on `es` at epoch 1, and confirms the replicate a fourth time

```
D-S4-4 delim(forced)=0.0732 over 555651 tok | delim(all, pre-ruling)=0.0974 over 675169 tok | act2-slot=0.2096 over 119518 tok
```

`555,651 + 119,518 = 675,169` exactly, and `(0.0732·555651 + 0.2096·119518)/675169 = 0.09734` against
the logged `0.0974`. 🔴 The all-basis value is **identical to the closed run's headline `delim=0.0974`**
— a fourth independent confirmation that `1284898` and `1274884` are the same run, and the reason the
`0.0732` figure must **never** be compared to the closed run's `0.0974`: different bases, D-S4-4 having
been ruled after the closed run reported.

Across all four checkpoints the forced basis reads `0.0591 → 0.0604 → 0.0816 → 0.0732` — 🔴 **not
monotone in either direction**, which confirms FINDING 37's retraction and extends it: frac 0.50 is a
spike and epoch 1 comes back down.

### Standing

- **Fold `es`, D-S4-5 verdict: `G4.1` FAIL.** Printed by the trainer itself.
- Gates scored in this run: `G4.14` `G4.13` `G4.7` `G4.8` `G4.5` `G4.9` `G4.11` PASS; `G4.6` **FAIL**;
  `G4.10` `REPORTED_NOT_THRESHOLDED`. 🔴 `G4.3` `G4.4` `G4.12` are **absent by design** — the D-S4-5
  launcher runs the trainer only, no diagnostics and no genperturb. They are **NOT CHECKED** for this
  run, which under the coverage clause is a gap in **either** direction and is recorded as one.
- `G4.1` remains **VOID** for DoD item 6.
- No band, no basis and no earlier fold verdict is changed by this entry. Two claims are corrected
  forward: `G4.6`'s fold ordering, and the `3.6×` robustness figure for the frac 0.50 FAIL.
