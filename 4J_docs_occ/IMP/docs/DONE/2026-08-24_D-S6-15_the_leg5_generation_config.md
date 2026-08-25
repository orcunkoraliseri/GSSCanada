# `D-S6-15` — for the author, 2026-08-24

**Status:** 🔴 OPEN — three items. Nothing has been submitted and nothing has been changed.

**Raised by:** trying to submit Step 6.3 the moment Step 4 closed. The blocker is not compute and it
is not Step 4. It is that the generation configuration Steps 6 and 7 both consume is frozen to
Leg 4, and `--leg 5` does not override it.

---

## 1. What I set out to do, and why I stopped

Step 4 closed on 2026-08-24, so **Step 6.3 — run the folds** became the critical path. The mechanism
was already built and already rehearsed: `LEG=5 sbatch 4thJ_step7_generate.sh <fold> <n>`, the same
launcher that produced the Leg-4 rehearsal (jobs `1286195`–`1286200` primary, `1286254`–`1286274`
auxiliary), whose output feeds `G6.4`, `G6.6`, `G6.7` and the entire Step 7 battery.

Before submitting a 7 B campaign I checked what `--leg 5` actually changes. It changes less than its
name implies.

---

## 2. 🔴 `FINDING 102` — `--leg 5` changes the filename and the provenance stamp. It does not change the model.

`tools/4thJ_step7_generate.py` resolves the adapter and the backbone from `cfg[...]`, i.e. from
`generation_config_<fold>.json` — **never from `--leg`**:

```
137:    print("adapter    : %s" % cfg["adapter"])
146:    if not os.path.isdir(cfg["adapter"]):
203:                        lora_request=LoRARequest(a.fold, 1, cfg["adapter"]))
```

The three configs live at `/speed-scratch/o_iseri/4J_step5/inputs/` and read, today:

| fold | `adapter` | `base_repo` | `temperature` |
|---|---|---|---:|
| `es` | `4J_step4/runs_ds45/leg4_primary_fold_es/adapter` | `allenai/OLMo-2-0425-1B` | 1.30 |
| `uk` | `4J_step4/runs_ds45/leg4_primary_fold_uk/adapter` | `allenai/OLMo-2-0425-1B` | 1.10 |
| `it` | `4J_step4/runs_ds45/leg4_primary_fold_it/adapter` | `allenai/OLMo-2-0425-1B` | 1.20 |

What `--leg 5` **does** do, all three of them cosmetic or protective, none of them model selection:

1. names the output `generated_leg5_<fold>_<tag>.jsonl` (line 214);
2. **removes** the `"provenance": "LEG-4 PILOT -- NOT REPORTABLE"` stamp from every record and from
   the summary (lines 142–144, 236–237, 274–275);
3. enforces `N >= 5200` in the launcher, per `D-S7-4` (a).

🔴 **So a `LEG=5` submission today would generate from the 1.48 B Leg-4 adapter, write it to a file
named `generated_leg5_*`, strip the not-reportable stamp, and hand it to every downstream Step 6 and
Step 7 gate as the paper result.** Nothing in the pipeline would object; the `N >= 5200` guard would
pass, because it counts prompts, not parameters.

This is the same shape as `FINDING 56` — a default quietly covering for a selector that was never
wired — and it is caught for the same reason: the guard was checked before the number was wanted,
not after.

⚪ The three Leg-5 adapters exist and are complete:
`/speed-scratch/o_iseri/4J_step4/runs_leg5/leg5_primary_fold_{es,uk,it}/adapter`.

**This half is a defect, not a decision. It is item 1 below and it is an additive fix.**

---

## 3. 🔴 The real decision: the sampling temperature is a 1 B measurement

`temperature` 1.30 / 1.10 / 1.20 was not a free choice — Step 5 chose it by **entropy matching**, and
each config says so in its own words: `"temperature_basis": "entropy matching"`, and
`"_what": "... every field is copied from the calibration artefact it was decided in; nothing here is
a fresh choice."`

`H_real` (3.588 on `es`) is a property of the **corpus**. The temperature that reproduces it is a
property of the **model**. Step 5 measured it against `OLMo-2-0425-1B` and Step 4's reported leg is
`Olmo-3-1025-7B` — 4.7× the parameters, a different tokeniser family and a different pre-training
mixture.

🔴 **There is no ruling to apply, because the question was never asked.** Step 5's record does not
contain the word "leg" anywhere:

```
$ grep -n "leg 4\|Leg 4\|leg 5\|Leg 5" Step5_docs/4thJ_05_populationLinkage.md \
                                       Step5_docs/4thJ_05_populationLinkage_val.md
(no matches)
```

and `D-S7-3` (a) directive 4 says only *"Train Leg-5 (OLMo-3-1025-7B) on 80GB MIG slice and execute
paper campaign"* — silent on the configuration. Carrying the number forward is a choice. Re-measuring
it is a choice. Neither is the status quo.

### Already on the record, and it weakens the number even on its own model

* `"temperature_curves_agree": false` on all three folds. On `es` the **entropy** argmin is 1.30 and
  the **fidelity** argmin is 0.70; on `it`, 1.20 against 0.80.
* At `T = 0.70` on `es`, **14.8 %** of diaries never terminate (`FINDING 71` context).
* `G5.8` ships **FAILING** on `es` and `uk` as the terminal verdict (`D-S5-16` (a)), and fidelity
  ships as a **band per fold**, not a point.

So the chosen temperature is not a robust optimum on the model it was measured on, which makes the
unmeasured transfer to a second model harder to defend by silence.

### ⚪ What is *not* evidence, stated so it is not mistaken for evidence

Every Leg-5 generation that exists today — the `G4.7` / `G4.16` sets — ran at a **hard-coded
`temperature=1.0`** (`tools/4thJ_step4_train.py:811`, `tools/4thJ_step4_diagnostics.py:413`), a
diagnostic default that predates Step 5 and was never meant to be the campaign temperature. It tells
us the 7 B adapter generates valid, terminating diaries at `T = 1.0`. It tells us **nothing** about
its behaviour at 1.30 / 1.10 / 1.20.

---

## 4. What is *not* at issue — checked, so the decision is not larger than it looks

* ⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` **intact**. No gate threshold is touched by
  any option here.
* ⚪ The three nulls `G6.1` / `G6.2` / `G6.3` are **model-free** and stay exactly as scored. So do all
  the corpus-side calibration arms.
* 🟢 **I checked for a third copy of the `D-S4-8` `eos_token_id` defect and it is not here.** The
  Step 7 path is vLLM with `stop=[grammar.EOR]` and `include_stop_str_in_output=True`
  (`4thJ_step7_generate.py:182-183`); vLLM terminates each sequence independently under continuous
  batching and never needs `eos_token_id` to pad a finished row, which is precisely the mechanism
  that failed in HF `transformers`. Nothing to patch. This was worth checking because Leg 4 ran on
  `OLMo-2-0425-1B`, which **does** ship an `eos_token_id`, so the defect would have been invisible in
  the rehearsal and would have appeared for the first time in the paper campaign.

---

## 5. The cost, because it is what item 3 turns on

The Leg-5 campaign as currently specified is **27 batches**:

| purpose | batches | Leg-4 precedent |
|---|---:|---|
| primary per fold, constrained + unconstrained | 6 | `1286195`–`1286200`, N = 600 |
| `G6.6` held-in, one per ordered `(fold, donor)` pair | 6 | `1286254`–`1286259`, N = 600 |
| `G6.7` fictional-country levels, 3 folds × 5 levels | 15 | `1286260`–`1286274`, N = 600 |

The launcher's `N >= 5200` refusal is written as `if [ "$LEG" = "5" ] && [ "$N" -lt 5200 ]` — it is
**unconditional on the batch's purpose**. Its stated justification is `V7.a`, which refuses to score
`G7.7` / `G7.8` below ten strata carrying 100 records. But `V7.a` is a Step 7 vacuity guard and the
Step 6 scorers do not invoke it:

```
$ grep -ln "V7\.a\|V7_a" tools/4thJ_step6_g66_heldin.py tools/4thJ_step6_g67_score.py \
                          tools/4thJ_step6_level1.py
(no matches)
```

So as written, the guard would force the 21 auxiliary batches to 8.7× their rehearsal size for a
reason that does not apply to them.

---

## 6. THE DECISIONS

### Item 1 — how `--leg 5` should select the adapter and the backbone

* **(a) RECOMMENDED — resolve it from the leg, additively.** `--leg 5` resolves
  `runs_leg5/leg5_primary_fold_<fold>/adapter` and `allenai/Olmo-3-1025-7B` @ `a81bae42…`, and
  **refuses to run** if the resolved directory is absent rather than falling back. The `--leg 4`
  path is left byte-identical, so the rehearsal and everything scored from it are undisturbed and
  need no re-run.
* **(b)** Write three new `generation_config_<fold>_leg5.json` and pass them explicitly. Correct, but
  it leaves the silent-fallback shape in place for whoever submits next without noticing.
* **(c) REJECTED** — pass the adapter by hand on each of 27 submissions. That *is* the failure mode.

### Item 2 — the sampling temperature on Leg 5

* **(a) Carry 1.30 / 1.10 / 1.20 forward unchanged** and declare in the methods that the temperature
  was entropy-matched on the 1.48 B pilot and **transferred to the 7 B model without re-measurement**.
  Zero cost, and honest — but it is a declared basis carry-over across a 4.7× change in model size,
  onto a number whose own entropy/fidelity curves already disagree.
* **(b) Re-run the Step 5 entropy sweep against the three Leg-5 adapters** and freeze new per-fold
  temperatures before the campaign. The defensible answer. It re-opens a **CLOSED** step, and it
  costs a 7 B sweep (9 grid points × 600 prompts × 3 folds, plus replicate seeds if it is to be read
  the way Step 5 read its own) *before* the 27-batch campaign starts.
* **(c) Generate at `T = 1.0`**, matching the only setting at which the 7 B adapter has actually been
  observed, and declare the departure from Step 5's chosen values. Cheapest defensible option; it
  discards Step 5's entropy matching entirely, which is a real loss.

🔴 **Under every option the temperature's basis must be written into the methods.** Right now each
config asserts *"nothing here is a fresh choice"*, and that sentence is true only of Leg 4.

### Item 3 — the `N >= 5200` refusal on the auxiliary batches

* **(a) RECOMMENDED — narrow it to the primary per-fold batches.** `V7.a` is its only stated
  justification and the Step 6 scorers do not invoke it. Holding `G6.6` and `G6.7` at their Leg-4 N
  also keeps the pair-to-pair and level-to-level comparisons on **one** basis, which is the whole
  point of `G6.6` clause 2 and `G6.7`'s slope.
* **(b)** Apply it everywhere: 27 batches at N ≥ 5,200 on a 7 B model. Nothing is wrong with the
  numbers it would produce; it is a cost decision, and it should be taken deliberately rather than
  inherited from a guard aimed at something else.

---

## 7. What I am doing while this is open

Nothing that depends on it, and nothing has been submitted. Two things that do not depend on it are
done and reported separately:

* 🟢 The two Step 6.5 jobs the handoff listed as **unread** are read. `1286305` is the
  `GUARD-B FAILED TO FAIL` attempt — Guard A refused correctly, Guard B sailed past and began loading
  models, and it was cancelled at 2 m 52 s. `1286311` is the re-push: `GUARD-B-REFUSED-GOOD` and
  `GUARD-C-REFUSED-GOOD`, 1 m 21 s, no model loaded. **The record in `4thJ_06_transfer.md` line 2696
  was already correct**; the handoff's "unread / do not trust the exit code" note is retired.
* 🔴 Unchanged and unaffected by any option here: **Step 6.5's third registered control, the
  random-label-permutation adapter, is still not trained**, so `privacy_audit.md` cannot be written
  and no release decision can be made on either leg. `4J_step4/runs/leg4_permuted_fold_it/` exists
  and is **empty**.

---

## 8. AUTHOR'S ANSWER

> **Item 1** — (a) / (b) / (c): **🟢 (a) Resolve from leg additively.**
> In `tools/4thJ_step7_generate.py`, `--leg 5` resolves `runs_leg5/leg5_primary_fold_<fold>/adapter` and base `allenai/Olmo-3-1025-7B` @ `a81bae42…`, with hard `SystemExit` if the target path is missing. Keeps `--leg 4` byte-identical.
>
> **Item 2** — (a) / (b) / (c): **🟢 (a) Carry 1.30 / 1.10 / 1.20 forward unchanged.**
> Declare in the methodology that temperatures were calibrated via entropy matching on the 1.48 B pilot and transferred to the 7 B model without re-measurement. Preserves the entropy-matching rationale without reopening closed Step 5.
>
> **Item 3** — (a) / (b): **🟢 (a) Narrow `N >= 5200` to primary per-fold batches.**
> Primary per-fold generation batches (6 batches feeding Step 7 vacuity guard `V7.a`) enforce $N \ge 5200$. The 21 auxiliary batches (`G6.6` held-in: 6 batches; `G6.7` fictional country levels: 15 batches) run at $N = 600$, maintaining direct basis parity with the Leg-4 rehearsal.

---

## Author's Directives & Action Plan

| # | Item | Ruling | Core Action | Compute / Code Impact |
|---|---|---|---|---|
| **1** | Model Selection in `--leg 5` | 🟢 **Option (a)** | **Wire `--leg 5` to resolve Leg-5 7B adapters and base repo dynamically** with hard refusal on missing paths; keep `--leg 4` intact. | Modify `tools/4thJ_step7_generate.py`; prevents silent fallback to 1.48 B model. |
| **2** | Sampling Temperature | 🟢 **Option (a)** | **Carry $T = 1.30$ (`es`), $1.10$ (`uk`), $1.20$ (`it`) forward**; document transfer from 1.48 B entropy matching in manuscript methods. | Zero compute; avoids reopening closed Step 5. |
| **3** | Campaign Batch Sizing | 🟢 **Option (a)** | **Enforce $N \ge 5200$ for the 6 primary per-fold batches** (Step 7 `V7.a`); run the **21 auxiliary batches at $N = 600$** (`G6.6`/`G6.7`). | Sizing optimization; maintains direct basis parity with Leg-4 rehearsal. |

⚪ `prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) remains strictly frozen and verified.

---

## 9. APPLIED — 2026-08-24, and the fix was SEEN WORKING before anything was generated

All three items applied the day they were ruled. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` untouched; no threshold moved; the frozen Step 5 configs at
`4J_step5/inputs/generation_config_<fold>.json` were **not edited** — the leg overrides three fields
in memory and prints both values.

| item | file | change |
|---|---|---|
| 1 | `tools/4thJ_step7_generate.py` | `resolve_leg()`; `--leg` now `choices=(4, 5)` |
| 2 | same | `TEMPERATURE_PROVENANCE_LEG5` written into every leg-5 record and summary |
| 3 | `tools/4thJ_step7_generate.sh` | `IS_PRIMARY` derived from the invocation; refusal narrowed |

Backups verified non-empty first: `.bak_ds615` — `4thJ_step7_generate.py` md5
`2ea98c3690fba099caf42cbe11483b92`, `.sh` md5 `4bafdb2cd839c15d76e1919bd3547945`, both **identical
to what was staged on Speed**, so the pre-patch state is recoverable byte-for-byte. Patched:
`.py` `9840897345905bcf7e808ee484965530`, `.sh` `adbd34ebefa38eb94444d7853078976a`.

### 🟢 The fix-check — job `1286834`, 46 s, CPU only, **6 / 6 PASS**, and check 0 is the control

🔴 `FINDING 56` is the reason this job exists: Leg 4's `600/600` was a model-repo default covering
for a broken harness. A guard that cannot be seen refusing is not a guard, so the **control runs
first** and the run is VOID if it does not fire.

| # | check | result |
|---|---|---|
| 1 | `py_compile` the patched generator | PASS |
| **0** | **CONTROL — `LEG5_ADAPTER_FMT` pointed at a missing directory** | **PASS, `SystemExit` code 3, "Nothing was generated."** |
| 2 | `--leg 4` returns the config **identical** (`==`), still `runs_ds45` + `OLMo-2-0425-1B` | PASS |
| 3 | `--leg 5` resolves `runs_leg5/leg5_primary_fold_es/adapter` + `Olmo-3-1025-7B` @ `a81bae42` | PASS |
| 4 | temperature, `top_p`, `top_k`, seed **unchanged**; provenance string present | PASS |
| 5 | all three leg-5 adapters on disk, `adapter_config.json` readable, `r = 32` in each | PASS |

The refusal exits **3**, deliberately not `NotRun`'s **2**: `2` is a legitimate "NOT RUN" the launcher
reports, and a missing Leg-5 adapter must never be readable as an ordinary outcome.

### 🟢 Item 3's classification, tested against the file's own bytes

The guard block was extracted from `4thJ_step7_generate.sh` with `sed` and evaluated under five
invocations — not reimplemented, so the test cannot pass while the file is wrong:

| invocation | classified | outcome |
|---|---|---|
| `LEG=5 es 600` | primary | **REFUSED, exit 1** |
| `LEG=5 es 5200` | primary | allowed |
| `LEG=5 es 600` prefixes `it`, tag `g66it` | auxiliary | allowed |
| `LEG=5 es 600` prefixes `g67_es_t00`, tag `g67t00` | auxiliary | allowed |
| `LEG=4 es 600` | primary | allowed — Leg 4 never reaches the refusal |

`IS_PRIMARY` is **derived** from the invocation (own prefixes **and** no tag), never hand-labelled:
every `G6.6` batch names a donor country and every `G6.7` level names a tag, so no auxiliary batch
can be mistaken for a primary one by a typo in a submission line.
