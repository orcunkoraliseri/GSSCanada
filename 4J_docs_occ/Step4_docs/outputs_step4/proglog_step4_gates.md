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
