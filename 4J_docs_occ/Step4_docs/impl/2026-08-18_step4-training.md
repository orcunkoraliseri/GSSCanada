# Step 4 — training — implementation state

Task doc:   `Step4_docs/4thJ_04_finetuneLLM.md` (spec) + `Step4_docs/4thJ_04_finetuneLLM_val.md` (14 gates, 15 perturbations, V4.a–V4.h)
Status:     **IN PROGRESS** — prereg frozen, shards built, trainer written, **Leg-4 pilot fold 1 submitted (job 1266825) and NOT yet read**
Started:    2026-08-18, on the author's instruction *"option b et apres continuer avec step 4, jusqu'a la fin"*

🔴 **Read `Step6_docs/outputs_step6/prereg.md` before touching anything here. It is FROZEN.**
md5 `e4243e07cdd80c9c846b91f40e3e8c45`. If it is edited, `G4.14` fails every run in the project at
once, including runs that already passed.

---

## Ledger

| JobID | what | state | exit | output |
|---|---|---|---|---|
| `1245620` | 4.1 — stage the three checkpoints | ✅ COMPLETED | 0:0 | `outputs_step4/staged_weights.json`, 3 revision hashes |
| `1266814` | D-S6-1 (b) — re-split the corpus by household | ✅ COMPLETED | 0:0, 00:00:48 | `Step6_docs/outputs_step6/4J_split_report_household.md` |
| `1266818` | Step 4 shard builder | ✅ COMPLETED | 0:0, 00:00:08 | `/speed-scratch/o_iseri/4J_step4/shards/`, `shard_manifest.json` |
| `1266819` | Step 4 environment pre-flight (GPU + package versions) | ✅ COMPLETED | 0:0 | `outputs_step4/4J_step4_envprobe_1266819.out` |
| `1266825` | 4.2 — Leg-4 pilot, fold 1 (held-out SPAIN), OLMo-2-1B | 🔴 **CANCELLED at 3:39 — `G4.13` FAILED, and the failure was real** | — | `outputs_step4/4J_step4_pilot_es_1266825.out` |
| `1266826` | 4.2 — Leg-4 pilot, fold 1 (held-out SPAIN), **after the `--limit-train` fix** | ▶ SUBMITTED | — | `4J_step4_pilot_es_1266826.out` |

Append-only. A failed job is never dropped — it stays with the line that supersedes it.

---

## Verified

**The frozen pre-registration, checked from disk by the shard builder before it read anything else:**
`prereg.md` recomputed md5 `e4243e07cdd80c9c846b91f40e3e8c45` == the sidecar's recorded value.
`G4.14` has its reference value and it was not taken from a manifest.

**Corpus md5 `ca89d2295603c547f2384a40dd1909ba`** — `4J_step3_corpus.jsonl`, 73,254 records, the
**household** split (D-S6-1 b). Goes into every run manifest for `G4.11`.

**Per-country diaries, re-derived by the builder and matching Step 3 exactly:**
es 19,140 (train 17,332 / heldout 1,808) · it 38,260 (34,366 / 3,894) · uk 15,854 (14,228 / 1,626).

**Shards, one set per fold.** Each fold's three shards partition the corpus exactly once — asserted,
not assumed.

| fold | holds out | trains on | train | held-in val | transfer | strata | strata N≥100 |
|---|---|---|---|---|---|---|---|
| **es** | es | it, uk | 48,594 | 5,520 | 19,140 | 493 | **150** |
| **uk** | uk | es, it | 51,698 | 5,702 | 15,854 | 455 | **151** |
| **it** | it | es, uk | 31,560 | 3,434 | 38,260 | 492 | **97** |

🔴 **Builder-side fold isolation: 0 held-out-country records in every training shard and every
held-in validation shard.** That count is **not** `G4.13`. `G4.13` re-counts from the shard the
trainer actually loaded, at training start. **Two independent counts on purpose** — a builder that
certifies its own output is the shape of check this project keeps rejecting.

**`V4.a` clears on all three folds** — the floor is 5 strata with N ≥ 100 and the worst fold has 97.

🔴 **Fold `it` is the small one and it is small for a structural reason.** Italy is the largest
country, so holding it out leaves the *smallest* training pool (31,560 diaries against 51,698 for the
UK fold) and the fewest usable strata (97 against 151). **Expect the Italy fold to be the weakest and
do not treat that as an anomaly to explain away** — `prereg.md` §8 forbids removing or averaging away
the worst fold, and this is the fold most likely to be it. It is predicted here, before any training,
so that it cannot later be discovered and rationalised.

**Probe sets for `G4.9`:** 200 diaries per training country per fold, drawn from the held-in
validation pool with seed **4242** — deliberately *not* the split seed 42, because a probe drawn with
the split's own seed is correlated with the split by construction.

---

## Decisions

* **D-S6-1 ruled (b) by the author, 2026-08-18.** Second hold-out is by **household** `(country, hid)`,
  10 %, seed 42. Applied by job `1266814` as a **re-label only** — 0 records changed text, 0 changed
  key, 13,149 changed label. The measured leak it removed: **4,900 straddling households, 15.22 % of
  all households, 21.06 % of the corpus.** Larger than the argument for making the change assumed.
* **`prereg.md` frozen 2026-08-18**, before any training job of any leg. Its md5 lives in a **sidecar**,
  not inside the file, because a file cannot contain its own hash — writing the value in changes it.
* **The shard builder re-implements the prefix parser** rather than importing `encoder.py`. Its counts
  are what the gates read, and a builder sharing a parser with the encoder cannot disagree with it.
* **`transfer_<fold>.jsonl` is written but never touched by Step 4.** It exists so Steps 5-7 read a
  file whose provenance is this manifest, and so `G4.13` has a non-zero comparison rather than only a
  zero.

---

---

## 🔴 FINDING 1 — the pilot earned its keep in three minutes. Job `1266825`.

**What happened.** The pilot was submitted with `--limit-train 4000` to keep the schedule short.
`G4.13` reported:

```
G4.13 FAIL  heldout-country records in train = None  by_country={'it': 4000}
```

**The cap was a plain `train_recs[:4000]` on a shard written in country order, so it took 4,000
Italian diaries and no UK ones.** The pilot was about to train on **one country**.

**Why that is not a small bug.** The recipe's own words: *"🔴 Joint multi-country training, never
sequential. Sequential costs 40 to 70 % on earlier countries. One model, country token in the
prefix."* A single-country pilot is not a short version of the real run — it is a **different
experiment**, and it would have produced a plausible loss curve, a plausible perplexity split and a
plausible set of generated diaries. 🔴 **Nothing in any metric would have said so.**

**What caught it, and it was not the gate's headline clause.** `G4.13` asks "how many held-out-country
records are in the training shard" and the answer was **zero** — the *right* answer, for the *wrong*
reason. What fired was **`V4.f`**, the vacuity guard: *"an isolation check over an empty shard finds
zero held-out records for the wrong reason, and reports the same number as a clean fold."* The
implementation extends that to a shard carrying fewer than two countries, and that extension is what
turned a silent pass into a FAIL.

🔴 **Read that again, because it is the transferable part: the gate's own threshold was satisfied.
Only the guard against the gate being vacuous noticed.** This is the fourth time in this project that
a vacuity guard, not a gate, has been the thing that worked — and it is the argument for writing
`V4.a` to `V4.h` before the gates rather than after.

**The repair.** `--limit-train` now takes the cap **proportionally per country**, samples within each
country with the run seed, reshuffles, and **asserts that no country was dropped** — failing loudly if
one was. Job `1266826` is the resubmission.

**Not repaired, deliberately:** the shards themselves are still written in country order.
`DataLoader(shuffle=True)` handles it for training, and re-ordering the files would invalidate the
`shard_manifest.json` md5s that `G4.11` carries. The ordering is a property worth knowing about, so it
is recorded here rather than smoothed away.

## The environment, measured — job `1266819`

**GPU: `NVIDIA A100-SXM4-80GB MIG 2g.20gb`**, compute capability `(8, 0)`, **bf16 supported**,
**19.3 / 19.5 GiB** free. 🔴 **A bare `--gres=gpu:1` gets a 20 GB MIG SLICE, not the 80 GB card.**
That is fine for the 1B pilot and for the LoRA folds by `RL18`'s arithmetic (18.27 GB), but it is
**not** enough for the ceiling run's full fine-tune (48.86 GB). The 80 GB profile
(`nvidia_a100_7g.80gb`) must be requested explicitly for that run, and a ceiling job submitted with a
bare `gpu:1` will OOM rather than fail informatively.

**Packages in `envs/step4`:** `torch 2.5.1+cu121` ✅, `numpy 2.2.6` ✅ — and `transformers`, `peft`,
`trl`, `datasets`, `accelerate`, `bitsandbytes`, `safetensors` **all MISSING**. The pilot launcher
pip-installs `transformers`, `peft`, `accelerate`, `safetensors`, `sentencepiece`, `protobuf`
**inside `sbatch`** (compute nodes on `ps` have outbound network, measured 2026-08-14).
🔴 **`bitsandbytes` is NOT installed and the ceiling run needs it for 8-bit AdamW.** Install it in
that run's own launcher and verify it imports against this CUDA build before the run, not during it.

---

## The code, written this session

| file | what it is |
|---|---|
| `tools/4thJ_resplit_household.py` | D-S6-1 (b). Re-label only, proved so against a size-matched backup |
| `tools/4thJ_step4_shards.py` | per-fold shards + `shard_manifest.json`; checks `prereg.md` against its sidecar **before** reading anything else |
| `tools/4thJ_step4_thresholds.py` | **V4.e** — the single source of every band. Imported by trainer and validator alike |
| `tools/4thJ_step4_train.py` | the trainer, with the 4.4 detectors wired in **before** the first run |

**Written against `torch` + `transformers` + `peft` directly, not `trl`.** `G4.5` exists to prove
prompt and pad positions carry `-100`. A trainer that builds its own labels can be made to prove
that; one that inherits masking from a library can only be trusted about it.

**Vacuity guards implemented, not just cited.** `G4.5` **FAILs** on zero pad positions rather than
passing an empty check. `G4.13` **FAILs** on an empty shard *and* on a single-country shard —
`V4.f`'s point is that an isolation check over a degenerate shard reports zero for the wrong reason
and prints the same number as a clean fold. `G4.1` **FAILs** with `V4.a`'s reason when fewer than 5
strata reach N ≥ 100 on **both** sides. `G4.9` reports **`NOT CHECKED`** on a single-epoch run,
because a forgetting gate needs a trajectory and one point cannot regress from itself — and
`NOT CHECKED` is never printed as a pass. `G4.2`'s halt uses strict `<` on **both** arms (`V4.d`).
`G4.14` recomputes the md5 **from disk** and never reads it from the manifest it is checking
(`V4.g`). The run banner prints the fold and its held-out country **before any verdict** (`V4.h`).

---

## Decisions taken by the code, recorded because they were not in the spec

* 🔴 **`G4.1`'s statistic had to be chosen — the val doc says "within-stratum variance ratio" and
  never says of what.** Chosen: the per-diary **at-home share**, `sum(DUR where LOC == at_home) /
  sum(DUR)`. Reason: it is the quantity this whole project exists to produce — an occupancy schedule
  for a building model — so a variance gate on it fails for reasons that matter downstream. Episodes
  per diary is computed alongside and **reported, not scored**. Recorded in
  `4thJ_step4_thresholds.py` as an ASSUMPTION, at the top, where it cannot be missed.
* 🔴 **Packing is DEFERRED and the run manifest says so in words.** The recipe calls for packed
  sequences with block-diagonal attention masks; these runs **pad** instead. Padding is slower, not
  wrong — and `G4.5` is only meaningful *while padding exists*, so packing would make that gate
  vacuous and the vacuity would look like a pass. Revisit for Leg-5 throughput, and if packing is
  adopted, `G4.5` must be re-pointed rather than quietly retired.
* **Probe seed 4242, not 42.** A probe set drawn with the split's own seed is correlated with the
  split by construction.
* **Both the shard builder and the trainer re-implement the prefix parser** instead of importing
  `encoder.py`. A detector that shares a parser with the thing it audits cannot disagree with it.

---

## Next

**The exact next action, written for a cold agent. Everything needed is on disk.**

1. **Read `4J_step4_pilot_es_1266826.out`.** 🔴 **Judge it on whether the detectors behaved, not on
   the loss.** §4.2: *"The success criterion is not a metric — it is that every detector in 4.4 fires
   when it should and stays silent when it should not."*
   **Already read and confirmed from the live output, before training finished:**
   * `G4.14` **PASS** — `e4243e07…` on both sides.
   * `G4.13` **PASS** — 0 held-out-country records, `by_country = {it: 2829, uk: 1171}`, both
     training countries present.
   * `G4.7` **PASS** — 4,000 / 4,000 training completions end in `<eor>`.
   * `G4.8` **PASS** — 1,000 / 1,000 tokenizer round-trips exact.
   * `G4.5` **PASS** — **507,808 pad positions, 0 unmasked.** 🔴 The non-zero count is the part that
     matters: a PASS at zero pad positions is the vacuity the guard exists to catch.
   * rsLoRA r=32 on all seven linear projections → **24,117,248 trainable of 1,509,033,984 (1.60 %)**.
   **Still to read:** the per-epoch block, `G4.1`, `G4.2`, `G4.6`, `G4.9`, `G4.10`.
   🔴 `G4.1` is **EXPECTED TO FAIL WITH `V4.a`'s REASON** at `--gen-n 64`: 64 generated diaries cannot
   put 5 strata over N ≥ 100 on the generated side. **That is the guard working.** If it reports PASS
   at 64 generations, the gate is wrong, not the model.
2. **Run the conditioning diagnostics** — `4thJ_step4_diagnostics.py --fold es --adapter <dir>
   --run-type pilot --gen-n 400`. Produces `G4.3`, `G4.4` (evening and morning scored separately) and
   **`G4.12`**, and writes `generated_pilot_es.jsonl`.
3. **Run the generation-side perturbations** — `4thJ_step4_genperturb.py --fold es --generated
   <that file> --perturbation all`. Four perturbations plus the null, a pre-registered `EXPECTED`
   table, per-gate attribution, and a **coverage clause**. 🔴 **Do not edit `EXPECTED` after seeing a
   result** — that table is the pre-registration, and Step 3 already paid for this lesson.
4. **Run the nine training-side perturbations** — `--perturbation` on the trainer: `leak_1pct`,
   `pad_labels_1pct`, `strip_eor_1pct`, `no_prefix`, `freeze_adapter`, `swap_tokenizer`,
   `drop_revision`, `perturb_merged_weight`, `edit_prereg`. 🔴 **`edit_prereg` is the one that needs
   care**: it must alter a COPY and restore the original, because a real edit to `prereg.md` fails
   `G4.14` on every run in the project, retroactively.
5. **Then the other two Leg-4 folds** (`uk`, `it`), then Leg-5.
   🔴 **The ceiling run needs `nvidia_a100_7g.80gb` and `bitsandbytes`, and has neither.**
   A bare `--gres=gpu:1` gets a **20 GB MIG slice** — measured, not assumed.

**Two things that must be true before any Leg-5 job is submitted:** every Step 4 gate has been **seen
failing**, and `G4.12` has been run at least once. The val doc calls `G4.12` *"the single most
informative check in this step"* — if every gate returns the same status under the within-stratum
shuffle, **the battery measures marginals rather than skill and the conditioning claim is unsupported
regardless of what the other numbers say.**
## WHAT I DID NOT VERIFY

* 🔴 **No training run has been read.** Job `1266825` was submitted, not collected. Every gate verdict
  above is a prediction written before the output existed — which is the point of writing it here,
  but it is not a result.
* 🔴 **`G4.3`, `G4.4` and `G4.12` do not exist in code.** Four of the fifteen perturbations do not
  either. **Step 4 cannot close, and no Leg-5 job may be submitted, until they do.**
* **The staged checkpoints were not re-hashed.** `staged_weights.json` carries three revisions from
  job `1245620`; that the files on disk still match them has not been re-checked this session.
* **No perturbation has been run**, so **no Step 4 gate has been seen failing.** Definition-of-Done
  item 6 is untouched.
* **`bitsandbytes` was never installed or imported**, so the 8-bit AdamW path is unproven.
* **The 80 GB MIG profile was never requested**, so it is unknown whether it is obtainable in
  practice or only in `sinfo`.
* **The Eurostat aggregate tables Step 6 will score against were never opened.** Carried from the
  Step 6 entry of the same date; not a Step 4 blocker, and not fixed either.

---

## 🔴 FINDING 2 — `--gres=gpu:1` is a slice, not a machine (job `1266826`, FAILED 1:0, 00:05:54)

The pilot reached `ep0 step200 loss 0.6955` and then died: `torch.OutOfMemoryError: Tried to
allocate 1.24 GiB. GPU 0 has a total capacity of 19.50 GiB of which 1.06 GiB is free.`

🔴 **The traceback named three other processes on the same physical card — 7.88, 10.30 and
15.74 GiB.** Those sum past our slice's 19.50 GiB, so what the run competes for is not a
private allocation: **the memory actually available to a `--gres=gpu:1` job is set by whoever
else is on the card, and it changes between submissions.** A run that fits today can OOM
tomorrow with no change on our side. This is not a tuning problem, it is a reproducibility
one, and it belongs in the run manifest.

Gates at the moment of death — all five that had run were green, and none of them is
implicated: `G4.14` PASS, `G4.13` PASS `{it: 2829, uk: 1171}` (FINDING 1's fix holding),
`G4.7` PASS 4000/4000, `G4.8` PASS 1000/1000, `G4.5` PASS 507,808 pad positions 0 unmasked.
Loss fell 1.6553 → 0.6955 over 200 steps, which is the only thing the run got to say about
learning and is **not** evidence of anything yet.

**Fix, three parts, all of which trade time for memory rather than changing the recipe:**

| change | where | why it is not a recipe change |
|---|---|---|
| `model.gradient_checkpointing_enable()` + `use_cache=False` during training | `4thJ_step4_train.py` | activations are recomputed, not dropped; the optimiser sees identical gradients |
| micro-batch 4 → **1**, grad-accum 4 → **16** | `4thJ_step4_pilot_es.sh` | **effective batch stays 16** — this is the point, and it is why the pilot's result stays comparable |
| `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` | sbatch env | fragmentation only |

`use_cache` is re-enabled inside `generate_samples` and switched off again at the top of every
training epoch, because generation needs the KV cache and checkpointing does not tolerate it.

🔴 **What this costs the ceiling run:** it was already blocked on `nvidia_a100_7g.80gb` +
`bitsandbytes`. FINDING 2 says the 80 GB profile is not merely *preferable* for it — a shared
20 GB slice cannot be sized against at all, so the ceiling run must be given an exclusive
profile or it is not a controlled comparison.

**Resubmitted as job `1266850`.** Same fold (es), same 4,000-record proportional cap, same
2 epochs, same `--gen-n 64`. `G4.1` is still EXPECTED TO FAIL with `V4.a`'s reason at 64
generations — that remains the guard working, not a defect.

---

## 🔴 FINDING 3 — the memory fix made a gate vacuous, and the gate said so (job `1266850`)

`G4.5 FAIL  0 pad positions, 0 not masked`.

**Cause: FINDING 2's own fix.** Dropping the micro-batch to 1 means every batch holds one
sequence, and a batch of one is never padded. `G4.5` exists to prove that pad and prompt
positions carry label `-100`; with nothing padded there is nothing to prove.

🔴 **The gate did the right thing.** It was written to FAIL rather than pass on `n_pos == 0`
("a check with nothing to check is not a pass"), so the vacuity surfaced as a red line instead
of a green one. The Step 4 doc had already flagged exactly this shape — *"packing would make
`G4.5` vacuous, and the vacuity would look like a pass"* — and the flag earned its keep against
a cause nobody predicted: not packing, but a batch-size change made for a memory reason two
findings earlier. **One fix silently disarmed an unrelated detector.**

It also silently disarmed a perturbation: `pad_labels_1pct` corrupts pad labels, and at batch
size 1 there are none to corrupt, so that perturbation would have "failed to fell its gate"
for a reason having nothing to do with the gate.

**Fix — report the trainer's loader, score a probe loader, never collapse the two:**

* the trainer's own loader is measured and reported; when it yields 0 pad positions it prints
  `G4.5 (trainer loader) NOT APPLICABLE -- batch size 1 yields 0 pad positions. This is NOT a pass.`
* the gate is then **scored** on a probe loader at batch ≥ 4 built from the same dataset and
  the same collate function, and the print says so in brackets.
* the manifest keeps both results, and the probe carries `note_finding_3` stating in words that
  what was proven is **the collate function, not this run's tensors**.

🔴 **The honest reading, which must survive into the paper:** for any run at micro-batch 1,
`G4.5` is a property of the code, not of the training that happened. It is still worth having —
it is what catches a broken collate before a fold run — but it must not be quoted as evidence
about that run's tensors.

**Decision on job `1266850`: let it finish.** The pilot exists to find wiring defects and it
found one; killing it would cost the adapter that `G4.3`/`G4.4`/`G4.12` need and would not make
the finding truer. Its manifest keeps `G4.5 FAIL`, correctly. The fix is in the trainer as of
this entry and carries into all three fold runs.

---

## FINDINGS 4, 5, 6 — three defects found by WRITING the perturbation battery, before running it

All three have the same shape and it is the shape this project keeps meeting: **a
perturbation that could not have felled its gate, for a reason that would have been
reported as "the perturbation did not work" rather than "the gate was not there."**

### 🔴 FINDING 4 — `G4.11` had no verdict at all

The val doc's table says *"Delete the revision hash from the run manifest → must fail
G4.11"*. `drop_revision` was implemented — it pops `base_revision` out of the manifest —
and **nothing checked the manifest.** `G4.11` existed only as an early `fail()` on a
different condition (no staged revision for the repo), which `drop_revision` never
triggers. The battery would have printed `G4.11: never made to fall` and the natural
reading — *the perturbation is too weak* — would have been wrong.

Fixed: `gate_g4_11(manifest)` requires twelve top-level keys plus three inside
`train_shard`, and is **scored on the manifest as it will be written**, after any
perturbation has had its effect. Scoring it on the pre-perturbation dict would have
recreated the same hole one layer down.

### 🔴 FINDING 5 — `strip_eor_1pct` corrupted a copy the gate never read

The perturbation stripped `<eor>` inside `DiaryDataset`, i.e. from the tokenised text the
model sees. `G4.7` is scored on `train_recs`, the raw records. **So the model trained on
mutilated text while the gate read clean records and PASSED.** The perturbation reached
the training, not the detector.

Fixed by moving the corruption to `train_recs`, before `G4.7` reads them — which is also
the honest place for it, because the claim under test is *"a corpus with missing
terminators is detected"*, not *"a tokeniser drops them"*. The dataset-level copy was
removed so a second 1 % is not corrupted on top.

### 🔴 FINDING 6 — a perturbation in the specification simply did not exist

The val doc lists fifteen perturbations. **Nine were implemented as `--perturbation`
flags, four are generation-side, and one — "train country-by-country sequentially →
G4.9" — was absent entirely.** Not stubbed, not `NotImplemented`: absent. `G4.9` had no
lever at all, and nothing in the code or the docs said so.

Implemented as the recipe's actual prohibition (RL05: *"joint multi-country training,
never sequential"*): with `--perturbation sequential_countries`, epoch *e* trains on one
country only, in sorted order, so the country trained first is measurably forgotten by
the last epoch — which is exactly what `G4.9` measures (final within +5 % of that
country's own best).

### What these three have in common, and it is worth saying in the paper

**A perturbation battery can be under-powered in a way that looks like a result.** In all
three cases the output would have been a clean-looking table with one gate marked "never
made to fall", inviting the conclusion that the perturbation needed strengthening. The
truth was that the gate had no implementation (4), the perturbation never reached the
gate (5), or the perturbation did not exist (6). **None of the three would have been
visible from a passing run.** They were visible only from writing the cross-tab and
asking, for each row, *which line of code makes this fall?*

### The battery itself

`tools/4thJ_step4_perturbtable.py` holds the `EXPECTED` map — perturbation → the one gate
it must fell, plus the gates that must stay clean — and is the pre-registration for the
training-side half. It prints the cross-tab, the attribution (including
`UNEXPECTED FALL -- FINDING` when a perturbation moves a gate that is not its own), and
the coverage clause.

🔴 **Its scope is stated in the file and must not be over-read:** it scores only gates a
*training* run can fell — `G4.2, G4.5, G4.6, G4.7, G4.8, G4.9, G4.11, G4.13, G4.14`.
`G4.1`, `G4.3`, `G4.4` and `G4.12` are generation-side and are scored elsewhere, on a
trained adapter at generation volumes that satisfy `V4.a`. **Any gate that does not PASS
at baseline is excluded from the coverage clause with its reason printed** — a gate red at
baseline cannot be seen falling, and dropping it silently is how a coverage clause becomes
a formality.

🔴 **`edit_prereg` never touches the real pre-registration.** It copies `prereg.md` and its
sidecar into the run directory, appends one byte to the **copy**, and points `G4.14` at
the copy. The battery script ends by printing `md5sum prereg.md` next to the sidecar, so
the claim "the original is untouched" is evidenced by the job, not asserted here.

---

## 🔴 FINDING 7 — the trainer trained and threw the weights away

`grep save_pretrained 4thJ_step4_train.py` returned nothing. **No run in Step 4 had ever
saved an adapter.** Every job so far — both pilot attempts included — trained a LoRA to
completion, printed a clean gate summary, and exited with the trained weights living only
in a process that was about to die.

This is not a cosmetic gap. `G4.3`, `G4.4` and `G4.12` all take `--adapter <dir>`, so the
**entire conditioning half of Step 4 was unreachable**, and nothing said so: the failure
mode is a run that looks complete and leaves no artefact. It would have been discovered
only by trying to run the diagnostics — which is exactly what the pilot leg is for, and
exactly the class of defect the val doc says the pilot exists to catch.

Fixed: the adapter and tokenizer are saved to `<run>/adapter` **before** `G4.6` merges
anything, and the path is recorded in the run manifest. Perturbation runs deliberately do
**not** save — eleven adapters is a gigabyte and none of them is a model anyone should
reuse.

**Cost of the finding: job `1266850` was cancelled at 00:09:58.** Continuing would have
spent roughly another hour to produce, once again, nothing the next stage could read.

## 🔴 FINDING 8 — `G4.1` was unreachable at any generation volume this project can afford

`G4.1` scores strata with **N ≥ 100 on both the real and the generated side**, and `V4.a`
FAILs the gate outright if fewer than 5 strata qualify. Generation drew prefixes **at
random** from the held-in validation set, which spreads them across hundreds of strata in
their natural, very uneven proportions.

🔴 **To land 100 generated diaries in each of 5 strata by random draw would take many
thousands of generations.** At 64, or 200, or even 600, `G4.1` returns `FAIL` with
`V4.a`'s reason — every single time, on every fold, forever.

**A gate that cannot be satisfied is not a gate. It is a permanent red light**, and the
predictable end of a permanent red light is that someone stops reading it — or worse,
"fixes" it by lowering `G4_1_MIN_STRATUM_N` after seeing a run, which is precisely the
band-relaxation this project forbids.

Fixed by **stratified generation**: `--gen-stratified-k K` draws 100 prefixes from each of
the K largest eligible strata, so the gate is reachable at K × 100 generations. The strata
are selected **by real-data count only** — never by anything measured on the generated
side, which would let the sampler choose the strata that flatter the model. Generation is
also batched (left-padded, as a decoder-only model requires), because 600 one-at-a-time
generations is an hour of wall-clock on a slice we share.

🔴 **The honest limitation, which must reach the paper:** `G4.1` is now scored on the
**six largest strata**, not on all of them. It is a statement about where the data is
dense, and it is silent about the thin tail. That is a real narrowing of the claim and it
is recorded here rather than discovered later.

## Where Step 4 stands

Job **`1266855`** runs the whole chain in one submission — train → save adapter →
`4thJ_step4_diagnostics.py` (`G4.3`, `G4.4`, `G4.12`) → `4thJ_step4_genperturb.py`. The
job begins with `py_compile` on all four scripts, because a `NameError` an hour into a
chained job costs the chain.

Still to run after it: `4thJ_step4_perturb_battery.sh` — eleven short runs (null baseline
plus ten perturbations) scored by `4thJ_step4_perturbtable.py`. It is **not** submitted
concurrently: FINDING 2 established that the GPU is shared, and two of our own jobs on one
slice is a self-inflicted OOM.

---

## 🟢 FINDING 9 — the 80 GB profile exists and is requestable. The ceiling run was never hardware-blocked

`scontrol show node` on the GPU nodes:

```
Gres=gpu:nvidia_a100_2g.20gb:9, gpu:nvidia_a100_1g.20gb:3, gpu:nvidia_a100_7g.80gb:1
```

🔴 **Every GPU node carries one `nvidia_a100_7g.80gb` — the whole card, un-partitioned —
and it is a normal `--gres` request.** The impl doc has been carrying "the ceiling run needs
`nvidia_a100_7g.80gb` and has neither" since the environment probe. Half of that was wrong:
the profile was there the whole time and nobody had asked for it. What was missing is the
*request*, not the *hardware*.

This also explains FINDING 2 properly. A bare `--gres=gpu:1` lets Slurm hand out any free
slice, and our pilot landed on a `2g.20gb` shared with other jobs. **The fix for Leg-5 is
not to shrink the batch — it is to name the profile.**

* Leg-5 primary folds (7B, LoRA): `--gres=gpu:nvidia_a100_2g.20gb:1` at minimum, and the
  7B weights alone are ~14 GB in bf16, so realistically the 80 GB profile too.
* **Ceiling run (full fine-tune, 48.86 GB measured): `--gres=gpu:nvidia_a100_7g.80gb:1`.**
  There is exactly **one per node**, and `AllocTRES` shows it already taken on several, so
  this run will queue. Queueing is not a blocker; a 7-day walltime is requested for
  precisely this reason.
* `bitsandbytes` remains genuinely missing, but compute nodes on `ps` have outbound network
  and the venv is pip-installed inside `sbatch` already, so it is one line, not a blocker.

🔴 **Corrected claim, and the earlier one must not be quoted:** the ceiling run is blocked
on a `pip install` and a queue wait, **not** on the cluster lacking suitable hardware.

---

## Job `1266855` — the first pilot chain that ran to the end, and what it found

`COMPLETED 0:0`, 31:46, peak VRAM 7.57 GiB. Training itself was uneventful: loss 2.08 → 0.56
over two epochs, `G4.13`, `G4.7`, `G4.8`, `G4.5`, `G4.9`, `G4.11` and `G4.14` all PASS, the
adapter saved (FINDING 7's fix, confirmed), `md5sum prereg.md` unchanged. Everything
downstream of that failed, and three of the four failures were defects in the harness rather
than readings of the model.

| gate | verdict | what it actually was |
|---|---|---|
| `G4.6` | FAIL | **defect** — the check OOMed. FINDING 10 |
| `G4.1` | FAIL (V4.a) | **defect** — 0 scorable strata, on every fold. FINDING 11 |
| `G4.4` | FAIL (nan) | **cascade** of FINDING 11: scored on 0 generated diaries |
| `G4.12` | FAIL (nan) | **cascade** of FINDING 11 |
| `G4.3` | FAIL | 🔴 **a real reading.** CE rise 0.0616, band ≥ 0.15 |

🔴 **`G4.3` is the one result here that is not a defect, and it must not be explained away.**
`CE true=0.5916 permuted=0.6533 rise=0.0616` against a pre-registered `≥ 0.15`: after two
epochs on 4,000 records the model is barely conditioned on its prefix. That is the expected
shape for a pilot trained on 8 % of the fold, and the full folds train on 48,594 — but the
number is on the record now, before those runs, and `prereg.md` §8 forbids reaching for that
explanation after the fact if the full folds do not clear the band.

## 🔴 FINDING 10 — `G4.6` FAILed because it could not be computed, not because the merge drifted

The gate forwards `G4_6_SAMPLE_N = 64` validation records through the adapter model, merges
the adapter, forwards the same 64 again, and takes the largest absolute logit difference. It
did all of that **in one batch**, and held the first logit tensor while computing the second.
At 1,280 positions and a ~100k vocabulary each tensor is ~32 GiB of float32. The reason
string in the detector JSON reads, in full:

> `merge check raised OutOfMemoryError: CUDA out of memory. Tried to allocate 18.40 GiB.`

The verdict was right — *a check that could not run is not a check that passed* — but the
FAIL says nothing about merge drift, which is the thing `G4.6` exists to detect.

**Fix.** The two passes are interleaved micro-batch by micro-batch through
`merge_adapter()` / `unmerge_adapter()`, which is the same numerical operation as
`merge_and_unload()` but reversible, so only one micro-batch of logits is ever resident and
the statistic is unchanged. `G4_6_MICRO_BATCH = 2` is added to the thresholds module and
labelled there as an **execution parameter, not a band** — the maximum over every compared
position does not depend on how the positions are grouped.

**Second defect in the same place, worth its own line.** The old code printed
`print("G4.6 %s" % verdict)` and nothing else. A gate that prints a verdict without the
number that produced it forces every reader to open a JSON file to find out whether a FAIL
means drift, or an exception, or an empty sample. It now prints the diff, the threshold and
how many positions were compared — or, when it could not run, the reason.

## 🔴 FINDING 11 — `G4.1` was unsatisfiable on **all three folds**, and FINDING 8's fix did not reach it

FINDING 8 made generation stratified so that `G4.1` could reach `N ≥ 100` on the generated
side. It could not, and the run said so plainly:

```
stratified generation: 0 strata x 100 = 0 diaries; eligible strata in the real data: 0
```

The eligibility test asks how many strata carry `N ≥ 100` **real** diaries, and it asked that
of the held-in **validation split**. Job `1266866` counted it on all three folds:

| fold | held-in val only (the old basis) | train + val (the new basis) |
|---|---|---|
| es | 5,520 diaries, 429 strata, **0** reach N ≥ 100 (largest 77) | 54,114 diaries, **166** |
| it | 3,434 diaries, 416 strata, **0** reach N ≥ 100 (largest 84) | 34,994 diaries, **112** |
| uk | 5,702 diaries, 421 strata, **0** reach N ≥ 100 (largest 84) | 57,400 diaries, **168** |

So `G4.1` would have FAILed with `V4.a`'s reason on **every fold of the real campaign**, and
`G4.4` and `G4.12` would have been scored on an empty generated file and returned `nan`
alongside it. Three gates, one cause, and the run still printed `COMPLETED 0:0`.

🔴 **What makes this the same mistake as FINDING 8, one level up.** FINDING 8's diagnosis was
*"the generated side cannot reach 100 under a random draw"*, and the fix addressed exactly
that. The real side was never counted. **The lesson is that a reachability argument has to be
made for every term in the gate's condition, not for the one that prompted the question.**

**Fix.** `G4.1`'s real reference is now the full held-in real set — `train + heldin_val` —
and the same set decides which strata are scorable. The band `0.80 ≤ VR ≤ 1.25`, the
`N ≥ 100` rule and `V4.a`'s five-stratum floor are **all untouched**: what changed is how many
real diaries estimate the real variance, and both sets are the same population (held-in
respondents of the same countries), so this is a sample-size correction rather than a change
of basis. The reference is snapshotted **before** any perturbation and **before**
`--limit-train`, which matters three ways: `leak_1pct` cannot put held-out-country records
into the reference, `strip_eor_1pct`'s in-place edit cannot reach it, and the reference is the
fold's data rather than whatever slice a given run trained on — which is what makes `G4.1`
comparable between the pilot and the full folds.

The diagnostics script carried the same defect and one of its own: it counted eligibility on
the **six-field prefix** while the trainer's `G4.1` strata are **five fields** (`country`,
`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_day_type` — `strat_econ_status` is not
in the stratum). Both are now the five-field key.

## FINDING 12 — every generation ran the full 1,280-token budget

Nothing told `generate` how a diary ends. `<eor>` is an ordinary token in this tokenizer, not
a special one, so generation continued to `max_new_tokens` for every sample no matter how
early the model terminated the diary. That was affordable while FINDING 11 kept the generated
count at zero; with `G4.1` reachable it is 600 generations per validation epoch plus 600 in
the diagnostics, and the wasted tail is hours.

`<eor>` is now resolved to its token ids at generation time and, when it is a single token,
passed as `eos_token_id`. The run prints which path it took, because a stop token that
silently failed to resolve would look exactly like the old behaviour. This changes no
statistic: `<eor>` is not special, so it survives `skip_special_tokens=True` and the
`gen-terminated` counter still measures the model's own termination.

## Where Step 4 stands after `1266855`

* The **training-side** half of the gate battery works end to end: 7 gates PASS, the adapter
  is written, the pre-registration is provably untouched.
* The **generation-side** half has never once been scored on real output. `G4.1`, `G4.4` and
  `G4.12` have produced nothing but `V4.a` and `nan`.
* **No Step 4 gate has yet been seen failing for the reason it was written to detect.**
  DoD item 6 remains untouched. Six FAILs are on the board and five of them are harness
  defects; the sixth (`G4.3`) is a genuine reading of an under-trained pilot.
* Re-run submitted as job **`1266877`** with FINDINGS 10, 11 and 12 fixed.

---

### 2026-08-18, job `1266877` — the two FINDING-11 fixes land, and FINDING 12 turns out to have been half a fix

Read from `/speed-scratch/o_iseri/4J_step4_pilot_es_1266877.out` while the job was running:

```
G4.14 PASS  live=e4243e07cdd80c9c846b91f40e3e8c45 recorded=e4243e07cdd80c9c846b91f40e3e8c45
G4.13 PASS  heldout-country records in train = 0  by_country={'uk': 1171, 'it': 2829}
G4.7  PASS  4000/4000 completions terminate with <eor>
G4.8  PASS  1000/1000 tokenizer round-trips exact
G4.5  PASS  493878 pad positions, 0 not masked  [SCORED on pad probe loader, batch 4]
stratified generation: 6 strata x 100 = 600 diaries; eligible strata in the real
    reference set (54114 diaries): 166
```

**FINDING 11 is fixed and the number proves it.** The eligible-strata count went from **0 to 166** on
this fold, and generation is drawing the 600 diaries `G4.1` needs. The reference set is 54,114
diaries — `train + heldin_val`, per the limitation recorded above.

Training is unchanged and healthy: loss 2.0802 → 0.5840 over one epoch of 4,000 records.
Generation is called **inside** the epoch loop (`detectors_<run>.json`, "every 4.4 detector, every
epoch"), so a two-epoch run generates 600 diaries twice, and the diagnostics stage generates 600
more. That is by design, not a defect — but it is what made the next line expensive.

#### 🔴 FINDING 12 was half a fix — `<eor>` is a THREE-token string

```
generation stop token: <eor> -> ids [27, 24274, 29],
    MULTI-TOKEN, so generation runs the full budget and this is a known cost
```

The fix written earlier resolved `<eor>` to token ids and passed it as `eos_token_id` **only when it
came back as a single id**. It does not: OLMo-2's tokenizer splits it into `<`, `eor`, `>`.
`eos_token_id` takes one id and cannot express a three-token string, so the guard fell through to
its honest else-branch and every one of the 600 diaries ran the **full 1,280-token budget**.

This is worth recording as a pattern rather than a typo. The earlier fix printed the branch it took,
which is the only reason the defect was visible at all — a fix that had silently done nothing would
have read as a fix. **A conditional fix must print which branch fired, or it is indistinguishable
from no fix.**

**What was changed** (`4thJ_step4_train.py`, `4thJ_step4_diagnostics.py`, identically):

```python
stop_kw = ({"eos_token_id": eos_arg} if eos_arg is not None
           else {"stop_strings": [TH.G4_7_EOR], "tokenizer": tokenizer})
```

`stop_strings` is a `transformers` 4.39+ feature and the environment has **4.57.6**, confirmed from
`envs/step4/lib/python3.10/site-packages/transformers-4.57.6.dist-info`. No threshold moved; this is
an execution parameter, like `G4_6_MICRO_BATCH`.

It also **removes a second problem nobody had raised**: with no stop condition, the returned text
continues past `<eor>` with whatever the model emits next, and the episode parser reads that trailing
material as data. Stopping at `<eor>` makes the generated record end where a record ends.

#### Why job `1266877` was cancelled at 25 minutes rather than left to finish

`scancel 1266877`, resubmitted as **`1266881`**. The pilot exists to shake out wiring, and the stop
condition *is* wiring. Letting the pilot validate one generation path and then running the
eleven-run perturbation battery on a **different, never-executed** path is the exact shape of
FINDINGS 3, 5 and 12 — a change that was never exercised by the run that was supposed to exercise it.
The cost of the restart is 22 minutes of training. `py_compile` runs as step 1 of the pilot script,
so a syntax error cannot reach the GPU.

---

## 2026-08-18 — 🔴 FINDING 13, found by reading the battery rather than by running it: **G4.3 and G4.12 had no lever anywhere in the project**

Job `1266881` was still generating, so instead of waiting I read the two scripts that run
after it. The question asked of the battery was the FINDING-6 question — *for every gate,
which line of code makes this one fall?* — and two gates had no answer.

**The three coverage maps, laid side by side.**

| where | what it scores |
|---|---|
| `4thJ_step4_perturbtable.py` `ORDER` | `G4.2 G4.5 G4.6 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14` |
| `4thJ_step4_genperturb.py` `EXPECTED` | `G4.1 G4.4 G4.7` |
| **neither** | **`G4.3`, `G4.12`** |

The exclusion in `perturbtable.py` is correct and documented: `G4.3` and `G4.12` are
conditioning gates scored on a trained adapter, and a training-side battery cannot reach
them. The exclusion in `genperturb.py` is also correct: it acts on an already-generated
file, and neither gate is a property of that file. Both scripts are individually right.
**The gap is between them**, which is exactly where a per-script review does not look.

**The one lever that exists, and why it was being destroyed.** `--perturbation no_prefix`
sets `prefix = ""` at trainer line 159. A model trained that way has never seen a prefix,
so shuffling the prefix cannot raise cross-entropy (`G4.3`) and permuting diaries within
a stratum cannot degrade anything (`G4.12`). It is the correct lever for both. But
`no_prefix` is a `run_type == "perturb"` run, and line 945 read:

```python
if args.run_type != "ceiling" and args.run_type != "perturb" and hasattr(model, "save_pretrained"):
```

with a deliberate, reasoned `elif` explaining that eleven adapters would cost a gigabyte
and none is a model anyone should reuse. That reasoning is sound for ten of the eleven.
It is wrong for the eleventh, because **both gates take `--adapter <dir>`** — so the only
artefact that could demonstrate them falling was written to memory and dropped on exit.
This is FINDING 7 in miniature: not a missing check, a missing *artefact*, failing
silently.

**Why one arm would not have been a demonstration.** The first fix saved only the
`no_prefix` adapter. That is not enough. The battery trains at `--limit-train 600`, and
`G4.3` already read **0.0616 against a band of 0.15 at 4,000 records** — so a `G4.3` FAIL
on a 600-record `no_prefix` adapter cannot distinguish *the prefix was removed* from *600
records condition on nothing*. The confound is live, not hypothetical. The null baseline
adapter is therefore saved as well, and the demonstration runs **two arms at an identical
cap**:

```
ctrl   = leg4_perturb_fold_es/adapter                      (prefix intact)
nopfx  = leg4_perturb_fold_es__PERTURB_no_prefix/adapter   (prefix emptied)
```

Two adapters, not eleven; the disk argument still holds for the other ten.

**Pre-registered before the run, and not to be edited after seeing it:**

* `G4.3` **FAIL** on `nopfx` — no prefix was ever seen, so shuffling it changes nothing.
* `G4.12` **FAIL** on `nopfx` — the same, at the within-stratum level.
* If either **PASSES** on `nopfx`, the gate is not measuring conditioning, and that is a
  further FINDING rather than a relaxation.
* 🔴 If the `ctrl` arm fails the same gate by the same margin, **the demonstration is void
  and must be reported as void** — it would show only that neither model is conditioned.
  It does not become a demonstration by being the only one we ran.

**Changes made** (all syntax-checked locally with Python 3.13 before leaving this machine):

1. `4thJ_step4_train.py` — `save_this = (args.run_type not in ("ceiling", "perturb") or
   args.perturbation in (None, "no_prefix"))`.
2. `4thJ_step4_diagnostics.py` — `--run-type` gains the choice `perturb`. It was
   `pilot|primary|ceiling|qwen`, so the demonstration had nowhere to write. Output paths
   are `%(run_type)s_%(fold)s`, and `leg == 4` always loads `MODEL_FOR["pilot"]`, so no
   pilot or primary artefact can be overwritten and the base model does not change.
3. `4thJ_step4_perturb_battery.sh` — a two-arm demonstration stage appended after the
   scoring, `4thJ_step4_diagnostics.py` added to the `py_compile` guard, and `mkdir -p`
   for each arm's output directory.

**Two defects introduced by the edits themselves, caught before submission.** A `perl`
replacement wrote a **literal `\n`** into the `py_compile` line, which `bash -n` accepts
as valid syntax — the file parses, and `py_compile` would simply have been handed a
filename called `\n` and failed the whole battery at step one. Rewritten with `awk` and
verified with `cat -A`, which shows the byte rather than rendering it. The lesson is the
narrow one: **`bash -n` proves a script parses, not that its arguments exist.** The
second was the missing `mkdir -p`.

**Scripts are edited locally and not yet copied to Speed.** Job `1266881` is mid-chain and
about to launch `4thJ_step4_diagnostics.py` as a separate process; overwriting that file
underneath a running chain is the kind of avoidable risk this log exists to record. The
`scp` happens once the job leaves the queue.

### The coverage accounting FINDING 13 forced, now complete for all fourteen gates

Having found two gates with no lever, the same question was put to the other twelve.

| gate | what fells it | where |
|---|---|---|
| `G4.1`, `G4.4`, `G4.7` | `modal_day`, `duplicate_500`, `blank_evening`, `strip_eor_1pct` | `4thJ_step4_genperturb.py` (`G4.7` also training-side) |
| `G4.2`, `G4.5`, `G4.6`, `G4.8`, `G4.9`, `G4.11`, `G4.13`, `G4.14` | the eight named perturbations | `4thJ_step4_perturb_battery.sh` → `perturbtable.py` |
| `G4.3`, `G4.12` | `no_prefix`, against a null-baseline control | the FINDING-13 stage, added today |
| `G4.10` | **nothing, correctly** — its verdict is the literal string `REPORTED_NOT_THRESHOLDED` | trainer line 996 |

`G4.10` is the one gate that needs no lever, and the reason is visible in the artefact
rather than only in this log: it never emits `PASS`, so there is no pass to falsify. It is
excluded from `ORDER` for that reason and not silently dropped.

Every other gate now has a named perturbation and a script that runs it. **That is a
coverage argument, not a result** — nothing has yet been *seen* falling, and DoD item 6
stays open until the battery has run and the cross-tab is on the board.

---

## 2026-08-18 — job `1266881`, epoch 0: the stop fix is total, `G4.1` produces its first real reading, and 🔴 **FINDING 14**

```
stratified generation: 6 strata x 100 = 600 diaries; eligible strata in the real reference set (54114 diaries): 166
generation stop token: <eor> -> ids [27, 24274, 29], MULTI-TOKEN, wired as stop_strings
  [epoch 0] delim=0.1082 content=1.0064 entropy=3.273  G4.1 FAIL  G4.2 PASS  gen-terminated 600/600
```

**`gen-terminated 600/600`.** FINDING 12 is closed by a number. Every one of 600 diaries
ended at `<eor>` instead of running the 1,280-token budget, and the throughput shows it:
roughly 45 diaries a minute against the previous full-budget rate. `G4.7`'s training-side
reading (`4000/4000 completions terminate with <eor>`) and this generation-side one now
agree, which they could not do before.

**`G4.1` is now reachable and it FAILS.** That is the first `G4.1` verdict in this project
that is about the model rather than about the harness — 166 eligible real strata, 600
generated diaries, six cells at N = 100 each.

### 🔴 FINDING 14: `G4.1` printed a verdict and no number, and its two FAIL branches are opposite in meaning

`gate_g4_1` returns one of two FAILs:

* the **`V4.a` branch** — fewer than five strata reach N ≥ 100 on *both* sides. This is a
  reachability failure **of ours**, and the response is to fix the harness. It is what
  FINDING 11 was.
* the **band branch** — the variance ratio leaves `[0.80, 1.25]`. This is a **real reading
  about the model**, and the response is to record it and not touch the band.

The epoch line printed `G4.1 FAIL` for both. The dict already carried
`n_scorable_strata`, `which_end`, `worst_low`, `worst_high` and, on the `V4.a` branch, a
written `reason` — **none of it reached the log.**

This is **FINDING 10 exactly**: there, `G4.6` FAILed because it OOMed rather than because
the merge drifted, and the code "printed the verdict and no number". That was fixed for
`G4.6` alone. The general form — *a gate that prints a verdict without the quantity it
thresholded cannot be acted on* — was never applied to the other thirteen. Fixed now for
`G4.1`; the epoch line carries either `V4.a: only N scorable strata` or `N strata, x
below / y above band [...], worst .../..., end=...`.

The pattern for the paper: **a fix applied to the instance that prompted it is half a
fix.** FINDING 12 was the same shape one step earlier — a conditional that never printed
its branch. Both were found only because something downstream needed the number and it
was not there.

This run's `detectors_*.json` still records the full dict, so **epoch 0's FAIL branch is
recoverable for `1266881`** and nothing is lost. The fix is for every run after it.

---

## FINDING 15 — `G4.6` cannot pass on a bf16 model, which voids `perturb_merged_weight`

Job `1266881`, fold `es`, printed at the end of training:

```
G4.6 FAIL  max_logit_diff=1.372e+01 threshold=1e-04 over 24282 positions
```

and the detectors JSON carries the exact value:

```json
{"gate": "G4.6", "verdict": "FAIL", "max_logit_diff": 13.71875,
 "threshold": 0.0001, "n": 64, "n_positions_compared": 24282}
```

`13.71875` is exactly representable in bfloat16. That is the giveaway: this is not
merge *arithmetic* going wrong, it is merge *storage* rounding.

### Cause 1 — a float32 threshold applied to a bf16 model

`G4_6_MAX_LOGIT_DIFF = 1e-4` is the tolerance you would pick for a float32 merge.
The model is loaded bf16. bfloat16 carries 8 mantissa bits, so its relative epsilon
is about 7.8e-3. `base.merge_adapter()` writes `W + (alpha/sqrt(r)) * B @ A` back
into bf16 parameters, and under RL05 that scale is `64/sqrt(32) = 8`, so every
merged weight is re-rounded to bf16 at a magnitude the rounding can see. Accumulated
across 32 layers, a logit displacement of order 1-10 is the *expected* magnitude of
that rounding, not an anomaly.

**`G4.6` as written cannot pass on this model under any training outcome.** The band
is unreachable by construction, which is a gate-design defect and not a reading
about the run.

### Cause 2 — padded positions are compared (an unambiguous bug)

The statistic is computed at line ~1062 as

```python
diff = max(diff, float((a - b).abs().max()))
```

over the **entire** logit tensor. The micro-batch is padded to `n = max(len(x) for x
in chunk)` and an `attention_mask` is built, but the mask is used only for the
forward pass -- it never reaches the comparison. Logits at `attention_mask == 0`
positions are unconstrained garbage, are typically the largest in magnitude in the
tensor, and are therefore the most likely home of the maximum being reported.
`n_positions_compared = 24282` counts `a.shape[0] * a.shape[1]`, i.e. padded extent,
not real tokens, so the printed denominator is inflated by the same bug.

This one is wrong regardless of what is decided about Cause 1, and is fixed.

### 🔴 The consequence that matters: a void battery row

`perturb_merged_weight` is the one perturbation written to fell `G4.6`. It lives
inside this very block -- it nudges a single merged parameter by `1e-3` after
`merge_adapter()` on the first micro-batch, and expects the gate to fall.

**A gate that already FAILs at baseline cannot be seen falling.** So the
`perturb_merged_weight` row of the training battery demonstrates nothing while
`G4.6` FAILs at baseline, and DoD item 6 stays UNMET for `G4.6` no matter what the
battery prints. This is the same class of gap as FINDING 13: each script is
internally correct and the defect lives in what they jointly fail to establish.

Note also that a `1e-3` nudge to one weight is *four orders of magnitude smaller*
than the 13.72 baseline drift. Even if the threshold were raised to accommodate
bf16, the perturbation would be invisible against that noise floor -- so raising
the band would not rescue the demonstration either. The gate needs a statistic with
a floor near zero, not a wider band.

### The band is NOT being relaxed

Raising `1e-4` to clear 13.72 would be changing a band so that our own artefact
passes, which this project forbids in writing, and per the paragraph above it would
not even work. Two admissible routes, and this is a decision, not a fix I will make
silently:

- **(a) Measure what the gate claims to measure.** Merge drift is an arithmetic
  property. Cast the two logit passes (or the merge itself) to float32 so the
  statistic reflects merge correctness rather than bf16 storage, and keep `1e-4`.
  `perturb_merged_weight` then has a real floor to rise from and becomes a genuine
  demonstration.
- **(b) Keep bf16 and report the FAIL as a result.** If merged bf16 checkpoints
  really do move logits by ~13.7, that is a deployment finding worth stating in the
  paper -- never distribute a merged bf16 adapter, always ship adapter + base --
  and `G4.6` is then re-scoped to "merged bf16 differs from unmerged" with the
  perturbation retired as unreachable rather than left in the table as void.

Recommendation: **(a)**, with the Cause-2 mask fix applied in both routes. (a) keeps
the gate testing a property that can be true or false, which is the only kind of
gate worth having; (b) is the honest fallback if the fp32 pass proves too expensive
in VRAM, and it must then be reported as a *retired* perturbation, never as a pass.

### Status

Cause 2 is a bug and is fixed. Cause 1 is recorded here and left open for the
author. Until it closes, the battery's `perturb_merged_weight` row must be read as
**VOID**, and `G4.6` must not be counted among the gates seen failing.

---

## FINDING 16 — five gates FAIL at baseline on the pilot, so every perturbation aimed at them is VOID

Job `1266881` is the first Leg-4 chain to run all four stages to completion
(`COMPLETED 01:22:24`). The full baseline picture, fold `es`, 4,000 records, 2 epochs:

| verdict | gates |
|---|---|
| PASS | `G4.2` `G4.5` `G4.7` `G4.8` `G4.9` `G4.11` `G4.13` `G4.14` |
| FAIL | `G4.1` `G4.3` `G4.4` `G4.6` `G4.12` |
| neither | `G4.10` (`REPORTED_NOT_THRESHOLDED`, by design) |

The generation-side battery then said so itself, without being asked:

```
-- null -- {'changed': 0}
   G4.1 expected clean -> FAIL 🔴 UNEXPECTED FALL -- FINDING
   G4.4 expected clean -> FAIL 🔴 UNEXPECTED FALL -- FINDING
BASELINE (null) verdicts: {'G4.1': 'FAIL', 'G4.4': 'FAIL', 'G4.7': 'PASS'}
Gates that PASS at baseline and were NEVER felled by any perturbation: ['G4.7']
COVERAGE CLAUSE VERDICT: FAIL
```

This is the coverage clause working exactly as designed, and the answer it gives is
that **the generation-side battery cannot demonstrate anything on this model.**
`G4.1` and `G4.4` are red before any perturbation is applied, so `modal_day`,
`duplicate_500`, `blank_evening` and `within_stratum_shuffle` are all pushing on
gates that are already down. `G4.7` is the only gate left standing, and nothing
felled it, so the clause fails on the other side too.

### The distinction that matters: mechanical gates vs. model-quality gates

The eight gates that PASS at baseline are **mechanical** -- tokenizer round-trip,
pad masking, leak count, pre-registration md5, `<eor>` termination, delimiter loss.
None of them depends on how well the model was trained, which is why they pass on a
4,000-record pilot and will pass on the 600-record battery runs too.

The five that FAIL are **model-quality** gates -- at-home share by stratum (`G4.1`),
prefix-shuffle CE rise (`G4.3`), diurnal ratios (`G4.4`), within-stratum conditioning
(`G4.12`) -- plus `G4.6`, which fails for the separate structural reason in FINDING 15.

**A model-quality gate cannot be demonstrated against an undertrained model.** The
pilot saw 4,000 of 58,801 training records, 6.8 % of the corpus, for 2 epochs.

### Consequence for the schedule

- The **training battery** (`ORDER = G4.2 G4.5 G4.6 G4.7 G4.8 G4.9 G4.11 G4.13
  G4.14`) is almost entirely mechanical: eight of its nine gates pass at baseline
  even at `--limit-train 600`. **It can and should run now**, and it is what finally
  moves DoD item 6 off zero. Its `perturb_merged_weight` row is VOID per FINDING 15
  and must be reported as void, not as a pass.
- The **generation-side battery** (`G4.1` `G4.4` `G4.7`) must be re-run against a
  **fully-trained Leg-4 fold adapter**, not the pilot. Its result on `1266881` is
  recorded as evidence that the harness works, and as a COVERAGE CLAUSE FAIL that is
  a true statement about a 6.8 %-data model.
- The **FINDING-13 two-arm `G4.3`/`G4.12` demonstration** is now predicted VOID in
  advance: the `ctrl` arm is trained on 600 records and the pilot already failed
  `G4.3` at 4,000 (`rise = 0.0621`, need `0.15`). **The void condition
  pre-registered for that stage is expected to trigger.** It is run anyway, because a
  pre-registration that is only honoured when convenient is not one, and the void
  verdict is itself the finding.

### The encouraging half

`G4.1` is not stuck. Across the pilot's two epochs the upper end closed steadily:

| epoch | scorable strata | below band (collapse) | above band | worst high |
|---|---|---|---|---|
| 0 | 6 | 0 | 3 | 1.503 |
| 1 | 6 | 0 | 1 | 1.312 |

Band `[0.80, 1.25]`. Zero collapse-end failures at either epoch, three out-of-band
strata reduced to one, worst case 1.503 -> 1.312 after a single additional epoch on
6.8 % of the data. The model over-predicts time at home and is correcting. That is a
reading worth having, and it is the first `G4.1` number in this project that is about
the model rather than the harness.

`G4.3` is the one that should be watched rather than assumed: `rise = 0.0621` at
4,000 records against a pre-registered `>= 0.15`, essentially unchanged from the
0.0616 measured earlier. `prereg.md` section 8 forbids explaining it away after the
fact. If the full folds do not move it, it is a result about how weakly the model
conditions on its prefix, and it gets reported as one.

---

## Job 1266911 -- the training-side perturbation battery ran to completion

`COMPLETED 03:43:00`, exit `0:0`. Eleven training runs at `--limit-train 600`,
scored by `4thJ_step4_perturbtable.py`, then the two-arm `G4.3`/`G4.12`
demonstration. This is the first battery in Step 4 to produce gates seen failing
for the reason they were written to detect, so Definition-of-Done item 6 is no
longer at zero.

### Six gates seen falling, each felled by its own pre-registered perturbation

```
perturbation             | G4.2    G4.5    G4.6    G4.7    G4.8    G4.9    G4.11   G4.13   G4.14
null                     | PASS    PASS    FAIL    PASS    PASS    PASS    PASS    PASS    PASS
pad_labels_1pct          | PASS    FAIL    FAIL    PASS    PASS    PASS    PASS    PASS    PASS
perturb_merged_weight    | PASS    PASS    FAIL    PASS    PASS    PASS    PASS    PASS    PASS
strip_eor_1pct           | PASS    PASS    FAIL    FAIL    PASS    PASS    PASS    PASS    PASS
swap_tokenizer           | NOT RUN
sequential_countries     | PASS    PASS    FAIL    PASS    PASS    FAIL    PASS    PASS    PASS
drop_revision            | PASS    PASS    FAIL    PASS    PASS    PASS    FAIL    PASS    PASS
leak_1pct                | PASS    PASS    FAIL    PASS    PASS    PASS    PASS    FAIL    PASS
edit_prereg              | PASS    PASS    FAIL    PASS    PASS    PASS    PASS    PASS    FAIL
no_prefix                | PASS    PASS    FAIL    PASS    PASS    PASS    PASS    PASS    PASS
freeze_adapter           | PASS    PASS    PASS    PASS    PASS    PASS    PASS    PASS    PASS
```

Six clean single-gate attributions, each moving its target and nothing else:
`G4.5` by `pad_labels_1pct`, `G4.7` by `strip_eor_1pct`, `G4.9` by
`sequential_countries`, `G4.11` by `drop_revision`, `G4.13` by `leak_1pct`,
`G4.14` by `edit_prereg`. Off-target movement is confined to `G4.6`, which was
already FAIL at baseline and so cannot be disturbed by anything.

The coverage clause still returns FAIL, and correctly:

```
  gates PASSing at baseline: ['G4.11','G4.13','G4.14','G4.2','G4.5','G4.7','G4.8','G4.9']
  never made to fall:        ['G4.2', 'G4.8']
  COVERAGE CLAUSE VERDICT: FAIL
```

Two gates remain unfelled. They are the subject of the two findings below.

---

## FINDING 17 -- `G4.8` cannot detect a tokenizer swap, and its perturbation crashed before anyone noticed

The `swap_tokenizer` row reads `NOT RUN`. The run died in generation:

```
PERTURBATION swap_tokenizer: tokenizer <- bert-base-uncased
G4.8 PASS  600/600 tokenizer round-trips exact
  ...
ValueError: The following `model_kwargs` are not used by the model: ['token_type_ids']
```

The crash is the smaller half. BERT's tokenizer emits `token_type_ids`, OLMo's
`generate` does not accept them, and the run ended at the first generation call.
That alone makes the row `NOT RUN` rather than a result.

The larger half is the line above the crash. **With `bert-base-uncased` loaded in
place of the OLMo tokenizer, `G4.8` reported `PASS 600/600 tokenizer round-trips
exact`.** It had to. `G4.8` encodes a record and decodes it with *the same*
tokenizer and checks the string comes back. That is a self-consistency test, and
self-consistency is preserved under substitution: any competent tokenizer
round-trips its own output. The gate is blind to *which* tokenizer it holds.

So `swap_tokenizer` was mis-targeted from the day it was written. Fixing the
`token_type_ids` crash would let the row run, and it would run to `G4.8 PASS` --
a green row that demonstrates nothing. `G4.8` appearing in the coverage clause's
`never made to fall` list is not an accident of this run; no perturbation in the
battery as written can fell it.

Two admissible repairs, neither taken here:

- **(a)** Re-point `G4.8` at identity as well as consistency -- assert the
  tokenizer's name-or-hash against the base model's own, then round-trip. The
  swap then fells it on the first line, before generation is ever reached, and
  the `token_type_ids` crash becomes irrelevant.
- **(b)** Retire `swap_tokenizer` and accept `G4.8` as a consistency check that
  is never independently demonstrated, stating that in the paper.

(a) is the honest repair and is cheap, but it changes what `G4.8` asserts, and
the project's rule is that a basis change is a band change. **Left to the
author.** Until it is ruled, the coverage clause stays FAIL and is reported FAIL.

`G4.2` is the other unfelled gate and its situation is simpler: no perturbation
in the battery targets it at all. That is an omission in the pre-registered
perturbation set, not a defect in the gate.

---

## FINDING 18 -- the report credits `G4.6` as "seen falling" two lines after excluding it

Same report, two lines apart:

```
EXCLUDED FROM THE COVERAGE CLAUSE -- ... cannot be SEEN FALLING here ...
     G4.6    FAIL
  ...
  gates seen falling:        ['G4.11','G4.13','G4.14','G4.5','G4.6','G4.7','G4.9']
```

`4thJ_step4_perturbtable.py` builds `seen falling` from "verdict is FAIL under
some perturbation" rather than from "PASSed at baseline and FAILed under a
perturbation". A gate already FAILing at baseline therefore enters the list for
free. It does not change the verdict here -- the clause is computed against the
`PASSing at baseline` set and still returns FAIL -- but the printed list
overstates the evidence by one gate, and if `G4.6` is ever repaired without the
list being repaired the error survives into a green report. **The credited count
is six, not seven.**

### The same run supplies the confirming experiment for FINDING 15

`freeze_adapter` is the only row where `G4.6` reads `PASS`. Freezing the adapter
leaves `B` at its zero initialisation, so `BA = 0`, so `merge_adapter()` writes
`W + 0` back and re-rounds nothing. Drift is exactly zero and the `1e-4` band is
met with room to spare.

That is the control FINDING 15 needed. The baseline `max_logit_diff = 13.71875`
is not a code fault and is not the pad-masking bug fixed this session -- it is
the arithmetic of writing a *trained* adapter's `W + 8*BA` back into bf16
storage. Train the adapter and the gate cannot pass; freeze it and the gate
passes trivially. Both routes offered under FINDING 15 stand, and route (a),
measuring the merge in fp32 while keeping `1e-4`, is now the better-supported
one.

---

## The two-arm `G4.3`/`G4.12` demonstration is VOID, as predicted -- but the statistics separate

Predicted VOID in advance under FINDING 16, and void it is: both gates read FAIL
in the control arm, so the no-prefix arm failing demonstrates nothing about
either gate.

The underlying quantities are another matter, and they are worth recording
because they were not predicted:

| statistic | ctrl arm | no-prefix arm | band |
|---|---|---|---|
| `G4.3` CE rise on prefix shuffle | 0.0181 | **-0.0004** | >= 0.15 |
| `G4.12` MI drop | 0.095 | 0.020 | >= 0.10 |

Both statistics move the right way and move a long way. The no-prefix arm sits at
zero prefix sensitivity to three decimal places, which is exactly what a model
trained without a prefix should show, and the control arm's `G4.12` MI drop of
0.095 is within a whisker of its 0.10 band on 600 training records. **The
statistics are wired correctly and do respond to the prefix; what is missing is
training signal, not instrumentation.** That raises the prior that the full folds
move these gates, without licensing any claim that they will.

One reading in the table looks backwards and is not a defect. `G4.4` PASSes in
the no-prefix arm (evening 1.893, morning 0.771) and FAILs in the control arm
(0.507, 0.179). A model with no prefix generates the pooled marginal, and the
pooled marginal matches a pooled reference well. A weakly-conditioned model
generating for six named strata does not. `G4.4` compares against the real
reference set, so the unconditional model is flattered by construction. This is a
reason to read `G4.4` only alongside `G4.3`, never alone.

---

## Author rulings D-S4-1 and D-S4-2, applied 2026-08-18

Both ruled **(a)**. Recorded in `Step4_docs/outputs_step4/proglog_step4_gates.md`, which is
the progress log for Step 4 and is append-only. What follows is the implementation, not
the ruling.

### D-S4-1 -- `G4.6` is measured in float32

`4thJ_step4_train.py`, the `G4.6` block. The band is **unchanged at `1e-4`**; only the
arithmetic precision of the comparison moved.

Parameter and floating-point buffer dtypes are captured per name, the model is cast with
`model.float()`, the merge/unmerge comparison runs as before, and the dtypes are restored.
Three details are deliberate:

- **The restore lives in a `finally`, not on the success path.** The adapter is saved
  after this block. Restoring only when the measurement succeeds would hand a silently
  upcast adapter to disk on any raise -- which is the same shape of defect as FINDING 15
  itself.
- **The `g6_upcast` flag is raised *before* `model.float()`, not after.** The cast converts
  module by module, so an OOM part-way through leaves the model in mixed precision. A flag
  set only on success would skip the restore for exactly the case that needs it. Restoring
  dtypes that were never changed is a no-op, so raising it early costs nothing.
- **A failed upcast raises rather than falling back.** Silently reverting to the bf16
  measurement would quietly reinstate the basis the ruling just retired, and the outer
  handler already records `G4.6 FAIL` with the reason -- a check that could not run is not
  a check that passed.

`bf16 -> fp32` is exact and `fp32 -> bf16` returns a value that was already
bf16-representable, so the round trip is lossless. The verdict JSON now carries
`measured_in`, `storage_dtype` and a `basis_note`, so no future reader can mistake an
fp32 reading for a bf16 one.

### D-S4-2 -- `G4.8` asserts tokenizer identity, then round-trip

`gate_g4_8` takes a new `base_repo` argument and scores two arms. Arm 1 compares the
tokenizer's `name_or_path` against the base checkpoint. Arm 2 is the round-trip exactly as
before. **PASS requires both.** If `base_repo` is not supplied the identity arm reports
`NOT CHECKED` and the gate FAILs -- not knowing what we should be holding is not the same
as holding the right thing.

The print now shows both arms and the reason, so a FAIL never has to be looked up in the
JSON. `swap_tokenizer` will now fell `G4.8` on the identity assertion, before generation is
reached, which also disposes of the `token_type_ids` crash without a separate repair.

### Implementer-side, additive, no ruling required

**FINDING 18 fixed.** `4thJ_step4_perturbtable.py` credited `felled.add(target)` whenever
the target FAILed under a perturbation, without checking that it had PASSed at baseline.
Now `hit = target_down and base_ok`. A target that was already down prints **`VOID`** with
an explicit line saying the perturbation may well have worked and that this run cannot show
it. The verdict was never wrong -- the clause is computed against `passing_at_baseline` --
but the printed evidence was overstated by one gate.

**`collapse_content` added, targeting `G4.2`.** `G4.2` halts when
`delimiter_loss < 0.05` **and** generated activity entropy `< 1.5`, strict on both arms
(`V4.d`) -- the model having learned the format perfectly while emitting degenerate
content. Nothing in the battery produced that condition, which is why `G4.2` sat in
`never made to fall` beside `G4.8`. The perturbation replaces every episode with the single
constant `060,110,000,1,1` while leaving the prefix, the `|`, the `;`, the `,` and the
trailing `<eor>` exactly where they were, so the format is intact and only the values are
degenerate. Pre-registered as `("G4.2", ["G4.5", "G4.13", "G4.14"])`. **No existing
`EXPECTED` row was edited.**

**Perturbation names are now whitelisted.** `--perturbation` had no `choices` and no
validation, so a misspelled name trained a perfectly clean run and was then scored as
`DID NOT FELL ITS GATE` -- indistinguishable in the table from a perturbation that
genuinely failed. Unknown names now stop the run. A battery that cannot tell a typo from a
negative result is not a battery.

### Sequencing

Fold `es` had been submitted as job `1269370` and was **cancelled while still `PENDING`**,
before it allocated a GPU or wrote a line of output. Nothing was computed and nothing is
discarded. Two reasons:

1. The rulings change `G4.6` and `G4.8`. Had `1269370` run first, fold `es` would have
   reported those gates under the old code and `uk` and `it` under the new. The trained
   adapter would have been identical either way -- neither ruling touches training -- but
   the verdicts would not have been comparable across folds.
2. The repaired battery costs 3-4 h and exercises every line of the new `G4.6` fp32 path.
   A fold costs an order of magnitude more and calls the same code. Validating the cheap
   run first is worth the delay; discovering an fp32 OOM at the end of a full fold is not.

The repaired battery is job **`1270491`**.

---

## Job 1270491 -- the repaired battery, read while it was still running

Three of the four pre-registered expectations can already be settled from the first
seven rows. One is a clean success, two are new defects, and the fourth is not yet
reachable.

### D-S4-2 worked on its first attempt

```
PERTURBATION swap_tokenizer: tokenizer <- bert-base-uncased
G4.8 FAIL  identity=False (holding bert-base-uncased, base allenai/OLMo-2-0425-1B)  round-trip 600/600 exact
     G4.8 reason: tokenizer identity MISMATCH: holding 'bert-base-uncased', base checkpoint
     is 'allenai/OLMo-2-0425-1B'. The round-trip arm read 600/600 and is not evidence --
     a tokenizer always round-trips its own output (D-S4-2, FINDING 17)
```

The round-trip arm still reads `600/600`, which is the whole of FINDING 17 stated as a
measurement: the arm that used to be the gate is intact, was never wrong, and never had
anything to say about identity.

## FINDING 19 -- the gate fell and the run then threw the evidence away

The run died four lines later, at the first generation call, on the same
`ValueError: The following model_kwargs are not used by the model: ['token_type_ids']`
as before. `detectors_<run>.json` is written only in the LAST block of `main()`, so the
crash discarded the `G4.8 FAIL` that had just been scored, and
`4thJ_step4_perturbtable.py` rendered the row `NOT RUN` for the second battery running.

**The battery cannot distinguish "the gate was never felled" from "the gate was felled
and the run died afterwards".** Both print `NOT RUN`, and only the second one is a
success. Had this not been read line by line, D-S4-2 would have been recorded as
ineffective on the strength of a row that actually contains the proof that it worked.

The class is wider than the row. Every gate scored before any crash, in any run, was
being discarded the same way.

Repaired additively: `detectors` is registered in a module global as soon as it exists,
and a top-level handler flushes it before re-raising. Gates never reached are **absent**
from the flushed file -- never written as `PASS` -- and the file carries a `crashed`
block so no reader can mistake a partial run for a complete one. The exception is
re-raised, so the job still exits non-zero.

## FINDING 20 -- `collapse_content` did not fell `G4.2`, and the reason is where the loss is measured

```
[epoch 0] delim=1.7315 content=8.7335 entropy=0.000  G4.2 PASS
[epoch 1] delim=1.6935 content=8.5423 entropy=0.000  G4.2 PASS
```

The entropy arm crossed perfectly -- `0.000` against a `< 1.5` halt, the model having
learned exactly one activity code. The delimiter arm went the wrong way: `0.109` at
baseline to `1.73`, against a `< 0.05` halt. `V4.d` requires both arms strictly, so
`G4.2` PASSed and PASSing was correct.

The cause is that `detector_delim_vs_content` runs on the **held-in validation loader**,
which the perturbation does not touch and must not touch. Replacing every episode with
`060,110,000,1,1` flattened the **durations** as well as the activities, so the model was
trained off the real record distribution and became worse at predicting real delimiters.
That is the opposite of what `G4.2` encodes, which is a model that has learned the format
**perfectly** while emitting degenerate **content**.

Redesigned: only `ACT` and `ACT2` are collapsed. `DUR`, `LOC` and `COP` keep their real
values, every episode boundary stays where it was, and the record remains an ordinary
member of the training distribution in every respect except that one column is constant.
Generated entropy still goes to zero because the model has never seen a second activity
code; the delimiter loss is now free to fall because nothing about the format changed.

🔴 **Recorded before the re-run, so it cannot be claimed afterwards:** if the delimiter
arm still does not cross `0.05` at 600 records, that is a training-budget limit, not a
perturbation defect -- the arm is model-quality in FINDING 16's sense, and `G4.2` would
then be demonstrable only at fold scale. The perturbation is correct either way; what
would be missing is training.

## FINDING 21 -- `G4.6` in fp32 is right about the cause and still fails

| basis | baseline `max_logit_diff` | band |
|---|---|---|
| bfloat16 (before D-S4-1) | `13.71875` | `1e-4` |
| float32 (after D-S4-1) | **`3.204e-04`** | `1e-4` |

D-S4-1 is confirmed as a diagnosis: **bf16 storage rounding accounted for roughly
99.998 % of the drift.** The gate nevertheless still FAILs, by a factor of about three.

The residual is a different question from the one the ruling answered. Three parts in
ten thousand, on logits of order ten, is about `3e-5` relative -- the scale of
floating-point **accumulation-order** noise in fp32 matmuls on an A100, and smaller still
than TF32's ~`1e-3` relative precision if TF32 kernels are in play. It is entirely
possible that `1e-4` sits below what this hardware can resolve at all, in which case
`G4.6` is unsatisfiable by construction for a **second** reason, unrelated to the first.

🔴 **The band is not touched.** What is added is the control that decides the question:
two **identical** unmerged forward passes, same weights, same inputs, same mask, same
reduction, differenced the same way. Whatever that reports is not the merge, because
nothing was merged. Both passes are taken *before* `merge_adapter()` so that
`perturb_merged_weight`, which pokes a weight and does not undo it, cannot contaminate
the floor. The TF32 flags are recorded alongside.

The reading rule is printed with the number:

- floor **`>= 1e-4`** -- the band is below the hardware's own reproducibility and is the
  thing to rule on;
- floor **`~0`** -- the band is resolvable here, and the remaining `3e-4` is a real
  property of the merge that has to be reported as one.

**Measured and reported first, ruled by the author second.** No verdict in the code
depends on the floor.

### Sequencing note

All three repairs were written while `1270491` was still running and **deliberately not
shipped**. The battery re-reads `4thJ_step4_train.py` for every remaining perturbation, so
copying a new file to Speed mid-run would have scored one battery under two code versions
-- the exact defect the fold-`es` cancellation was made to avoid.

---

## FINDING 22 -- `G4.2` cannot be felled at 600 records, and the reason is arithmetic, not design

Recorded **before** the repaired battery is run, so it is a prediction and not an excuse.

Job `1270491` prints the delimiter loss for every row. The clean rows are not merely similar,
they are pinned:

```
[epoch 1] delim=0.1094   null
[epoch 1] delim=0.1094   pad_labels_1pct
[epoch 1] delim=0.1094   perturb_merged_weight
[epoch 1] delim=0.1096   strip_eor_1pct
[epoch 1] delim=0.1095   drop_revision
[epoch 1] delim=0.1163   sequential_countries
[epoch 1] delim=1.6935   collapse_content   <- FINDING 20, wrong direction
```

Four decimal places of agreement across five different perturbations is a **floor**, not a
coincidence. At 600 records and 2 epochs the model has learned the record format as well as
this budget allows, and that is `0.1094` nats.

`G4.2` halts on `delimiter_loss < 0.05` **and** `gen_entropy < 1.5`, strict on both arms
(`V4.d`). The band is a factor of **2.2 below the floor**. The FINDING 20 repair takes the
delimiter arm off `1.73` and back toward the clean value -- which is the correct direction and
still not far enough. **No training-side perturbation can fell `G4.2` at this budget**, because
the first arm is not a statement about the perturbation at all: it says *the model has learned
the format almost perfectly*, and an undertrained model cannot satisfy it however its content is
mangled.

🔴 **`G4.2` therefore belongs to FINDING 16's model-quality class**, beside `G4.1`, `G4.3`,
`G4.4` and `G4.12`. It was mis-classified as a mechanical gate when the battery was written.
The delimiter arm falls as training proceeds; the entropy arm is what the perturbation controls.
Only when the first arm is genuinely satisfied does the second arm mean anything.

### The demonstration this requires, pre-registered here

A **two-arm** run at a larger cap, exactly parallel to the FINDING-13 `G4.3`/`G4.12`
demonstration already in the battery script, and for the same reason: one arm cannot separate
*the perturbation fell the gate* from *the budget fell the gate*.

| arm | training | EXPECTED |
|---|---|---|
| ctrl | `--limit-train 4000`, no perturbation | `G4.2` **PASS** -- delim below 0.05, entropy ~2.8 |
| collapse | `--limit-train 4000 --perturbation collapse_content` | `G4.2` **FAIL** -- delim below 0.05, entropy ~0.000 |

`4000` is chosen because it is a budget this project has already run (the FINDING-13 note
records `G4.3 = 0.0616` at 4,000 records), not because it is known to cross. **If the ctrl arm's
delimiter loss does not fall below `0.05` at 4,000 records, the demonstration is VOID and is
reported VOID** -- the collapse arm failing would then show nothing, and `G4.2` moves to the
Leg-4 folds, where the budget is another order of magnitude larger. That fallback is stated now
so it cannot be presented later as a result.

🔴 The demonstration writes to a **separate run directory**. Sharing `runs_perturb` would
overwrite the 600-record `collapse_content` detectors file, and the main table would then be
scored with one row trained at a different budget from the other ten.

**The band is not touched and no `EXPECTED` row is edited.** This changes where `G4.2` is
scored, not what it asserts.

---

## FINDING 23 -- the STAY CLEAN check had no baseline condition either

Job `1270491`, attribution block. Three rows reported a violation that never happened:

```
pad_labels_1pct   was required to STAY CLEAN and did not: G4.6 = FAIL
drop_revision     was required to STAY CLEAN and did not: G4.6 = FAIL
edit_prereg       was required to STAY CLEAN and did not: G4.6 = FAIL
```

`pad_labels_1pct` pads 1 % of the label tensor. `drop_revision` removes the git revision from the
run record. `edit_prereg` rewrites a copy of the pre-registration. **None of the three goes anywhere
near the merge-drift gate.** `G4.6` was already `FAIL` at baseline, and the very same report says so
eleven lines earlier under `EXCLUDED FROM THE COVERAGE CLAUSE`.

The loop read:

```python
for g in clean:
    if g in v and v[g] not in ("PASS", "REPORTED_NOT_THRESHOLDED") and g != target:
```

`base` is never consulted. Any gate that is down at baseline is therefore reported as freshly
dirtied by every perturbation that happens to list it as a clean-check.

### Why this is the same defect twice

FINDING 18 was the missing baseline condition on the **target** arm -- a gate already `FAIL` was
credited as *seen falling*. FINDING 23 is the missing baseline condition on the **collateral** arm --
a gate already `FAIL` is charged as *newly broken*. Same function, same missing test, opposite
directions of error. Repairing the first and not the second left the report half-honest, and in the
half that still lied it lied three times in eleven rows.

Both arms now share one rule: **a verdict about a gate is only meaningful relative to that gate's
own baseline.**

### What was and was not affected

**The verdict was not affected.** This loop never appended to `findings`, and the run correctly
printed `FINDINGS: 0`. The coverage clause is computed against `passing_at_baseline` and was
correct at `FAIL` on `['G4.2', 'G4.8']`. What was wrong is the **printed evidence**, in the
direction that invents collateral damage: an auditor reading this table would have concluded that
three unrelated perturbations each break merge integrity, and would have gone looking for a
coupling that does not exist.

### The repair

Additive. A gate that does not `PASS` at baseline now prints

```
G4.6 NOT ASSESSABLE as STAY CLEAN -- already FAIL at baseline. Stated, not silently dropped.
```

-- neither a false violation nor silence, matching the discipline the `EXCLUDED` block already
follows. A gate that does `PASS` at baseline is checked exactly as before.

No `EXPECTED` row was edited, no band moved, no gate's assertion changed.
`4thJ_step4_perturbtable.py`: 237 lines, md5 `df47f30e42ea215d5afae686ed46dc4a`, `py_compile`
clean. Pre-repair copy preserved at `scratchpad/perturbtable_pre_f23.py`.

---

## Job `1270491` closed — the `G4.3` / `G4.12` demonstration is VOID, and `G4.4` joins the undertrained list

`sacct`: `COMPLETED 04:01:57 0:0`. Full numbers, both arms, and FINDING 24 are written up in
`outputs_step4/proglog_step4_gates.md` and are not duplicated here. The consequences for this
document's gate ledger are:

* **`G4.3` — NOT CREDITED.** `ctrl` rise `+0.0188`, `nopfx` rise `−0.0004`, band `≥ 0.15`. Both arms
  below the band. The separation is real (≈47×) and in the pre-registered direction, but a control
  that FAILs its own gate cannot baseline anything. Moves to the Leg-4 folds.
* **`G4.12` — NOT CREDITED.** `ctrl` CE rise `+0.0023` / MI drop `+0.015`; `nopfx` `−0.0008` / `−0.085`.
  Same reasoning. Moves to the Leg-4 folds.
* **`G4.4` — every 600-record reading is now void in BOTH directions** (FINDING 24). The
  prefix-stripped arm scored *better* on diurnal shape than the control, which cannot happen for any
  reason connected to conditioning. Neither the `ctrl` `FAIL` nor the `nopfx` `PASS` may be quoted.

**Gates that cannot be demonstrated against an undertrained model** — the list is now five, not four:
`G4.1`, `G4.2` (FINDING 22), `G4.3`, `G4.4` (FINDING 24), `G4.12`. Only the Leg-4 folds can credit
any of them. This is the single largest block of DoD item 6 still outstanding, and it is blocked on
compute, not on design.

## Ship + re-run

Three files shipped to `/speed-scratch/o_iseri/` after the queue was confirmed empty, md5 matched on
both sides: `4thJ_step4_train.py` 1505 `661b11e7…`, `4thJ_step4_perturb_battery.sh` 150 `a2d99e15…`,
`4thJ_step4_perturbtable.py` 237 `df47f30e…`. Speed had held 1360 / 108 / 221; in particular its
108-line battery did not contain the FINDING 22 `G4.2` section at all, so that demonstration has
never yet run.

`1270491`'s table preserved as `perturb_table_train_side_es_1270491.txt` before the re-run overwrote
the path.

**Job `1274838` RUNNING.** Expected ≈7 h: ≈3.5 h for the twelve 600-record runs plus the two-arm
`G4.3`/`G4.12` demo, then ≈3.3 h for the two 4000-record `G4.2` arms. What it must deliver:

1. `G4.8` credited — FINDING 19's crash-flush writes detectors before `swap_tokenizer` dies.
2. `G4.2` moved by `collapse_content` — FINDING 20's redesign, which now `fail()`s rather than
   silently no-ops when the flatten is empty.
3. The `G4.6` noise floor measured — FINDING 21. **This is the number the author's pending ruling
   depends on**, and it is the only reason to ask them anything at all.
4. The 4000-record two-arm `G4.2` demonstration — FINDING 22. Declared VOID in advance if the `ctrl`
   arm's delimiter loss does not fall below `0.05`.
5. An honest STAY CLEAN report — FINDING 23.

Nothing in `prereg.md` was touched; its md5 is re-checked from disk inside the job.

## FINDING 21 closed — noise floor `0.000e+00`, hypothesis refuted, band stays

Job `1274838` baseline: `G4.6 FAIL max_logit_diff=2.498e-04 threshold=1e-04 over 20103 positions`,
`repeat-noise floor=0.000e+00`, TF32 matmul off. Two identical unmerged passes agree bit-for-bit, so
the `1e-4` band is resolvable and the drift is real. **The re-banding argument is dead and the band
stays.** Full write-up, the four bracketing measurements and the two neutrally-stated options are in
`outputs_step4/proglog_step4_gates.md`; the residual is bf16 *storage* quantisation of the merge
(D-S4-1 moved the comparison to fp32, not the storage), which makes `G4.6` unsatisfiable for any
adapter that trained and satisfiable only for one that did not.

Author's remaining choice is a **basis** question — (a) standing explained FAIL at `1e-4`, or
(b) upcast for the merge and re-state the `EXPECTED` row. Untouched pending the ruling.

## Battery `1274838` closed — coverage 7 of 8, `G4.2` alone outstanding

`COMPLETED 05:08:01 0:0`. Full write-up in `outputs_step4/proglog_step4_gates.md`; the ledger changes
for this document are:

**Credited, seen falling (7):** `G4.5 G4.7 G4.8 G4.9 G4.11 G4.13 G4.14`.
`G4.8` is new — FINDING 19's crash-flush kept the felled verdict that the `token_type_ids` crash used
to discard. Its row honestly prints `-` for the four gates the dead run never reached.

**Excluded from the clause, stated not silent:** `G4.1 FAIL`, `G4.6 FAIL`, `G4.10` unthresholded.

**Outstanding (1):** `G4.2`.

### `G4.2` — FINDING 25

The 4000-record two-arm demonstration is **VOID as pre-registered**: the clean arm's delimiter loss
reached only `0.1022`, against an arm needing `< 0.05`. The diagnosis is worth more than the
demonstration would have been:

* arm two (`gen_entropy < 1.5`) is **nailed** — redesigned `collapse_content` gives `0.000` at every
  budget and epoch. FINDING 20's redesign worked (`1.7315 → 0.5024`).
* arm one (`delimiter_loss < 0.05`) is **never satisfied by the CLEAN model**, so it is a
  precondition, not a perturbation target.
* the arms are in **mechanical opposition** under any training-side content perturbation, because
  delimiter loss is measured on the unperturbed validation set: killing entropy in training costs
  `0.10 → 0.50` on real delimiters.
* budget is not closing the gap — `600 → 4000` records moved it 6.6 %; a two-point power-law fit
  (weak, and flagged as weak) puts the full fold at ≈ `0.093` and `0.05` at ~10^12 records.

**Job `1274884` (fold `es`, full 58,801 records) replaces that extrapolation with a measurement.**
Quote the measurement, never the fit. If it confirms, `G4.2` becomes a gate-design question for the
author — options (a) permanently NOT DEMONSTRABLE, (b) generation-side lever felling arm two alone,
(c) re-base arm one, which is flagged against itself as the forbidden move. Nothing touched.

### FINDING 26

`collapse_content` also fells `G4.9` at 4000 records — `UNEXPECTED FALL -- FINDING: also moved
['G4.9']`, printed by the collateral check unprompted. Mechanistically sensible (content flattened to
a constant → forgetting) but undeclared, and absent at 600 records, so dose-dependent. If
`collapse_content` is ever used to credit `G4.2`, this must be quoted alongside it.

### Leg-4 fold `es` — job `1274884`

Submitted after `squeue` confirmed zero of our GPU jobs (FINDING 2). Named GRES
`nvidia_a100_2g.20gb`. It is the only route to `G4.1`, `G4.3`, `G4.4`, `G4.12`, and it settles
FINDING 25.
