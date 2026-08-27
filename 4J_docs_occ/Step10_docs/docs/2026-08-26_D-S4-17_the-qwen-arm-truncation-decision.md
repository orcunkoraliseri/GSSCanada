# `D-S4-17` — the Qwen comparison arm and `--max-len`, decided before the number arrives

## 🟢 RULED 2026-08-26 — **OPTION (A)**. The rule in §4 stands as written and is now the ruling.

**`--max-len 1280` stays fixed on every arm. The Qwen arm is reported with its exact measured
truncation rate printed beside its losses**, under the pre-declared ≤ 1.0 % contamination
threshold. Full ruling and the three directives: §8.

🔴 **The ruling was made while job `1287613` was still `PD`** — the number had not been
seen by anyone when the decision was taken. That is the property this document was written to
have, and it is worth more than the decision itself.

---

**2026-08-26 (night, last).** Job `1287613`, `PD` on `ps` at the time of writing. This document
exists so the answer is fixed **before** the measurement lands, not chosen after seeing it.

🔴 **Why it is written now.** The alternative is to read the truncation count and then pick the
option that makes the arm look better. That is selecting an artefact because it passes, and this
project has already refused that move twice (`D-S4-5`'s named checkpoint, `D-S2-20 Q2`'s refused
option (c)). The rule below is written blind on purpose.

⚪ Filed here at the author's instruction. It is a **Step 4** decision by subject.

---

## 0. What is being decided, in one line

**If the Qwen arm truncates any training record, do we raise `--max-len`, or do we report the arm
with its truncation rate beside it?**

---

## 1. Why the question exists at all

The comparison arm's entire claim is *"the same recipe, a different backbone"*
(`4thJ_04_finetuneLLM.md:62` — it *"states what the alternative backbone cost"*). Everything is held
constant: LoRA `r = 32` rsLoRA on seven projections, bf16, 3 epochs, effective batch `2 × 8 = 16`,
`--max-len 1280`.

🔴 **But `--max-len` is not backbone-neutral, and that is the flaw in "hold everything constant".**
`4thJ_04_finetuneLLM.md:92–97` measured the same diary at **200 OLMo tokens and 303 Qwen tokens**,
and the `311` marker at **1 OLMo token against 3**. A fixed token budget is therefore a **tighter**
budget for Qwen. Holding the number constant does not hold the *constraint* constant.

🔴 **And the trainer truncated silently.** `DiaryDataset.__init__` sliced
`(p_ids + b_ids)[:max_len]` with no count and no warning. On the OLMo runs that was harmless. On a
tokenizer producing ~1.5× the tokens it is the exact shape of defect this project exists to catch:
**a comparison in which one arm quietly trains on cut-off diaries is a comparison of truncation, not
of backbones.**

⚪ **Fixed before the arm was submitted, additively.** `DiaryDataset` now counts `n_truncated` and
`max_tokens_seen` and prints, **for every run and not only this one**, so the OLMo arms supply the
baseline this number has to be read against:

```
TRUNCATION train tokenizer=Qwen/Qwen2.5-7B max_len=1280 : N of M records truncated (P %), longest record L tokens
```

🔴 **It is a COUNTER, not a gate.** Nothing stops the run. No `G4.x` id, no band, no verdict — a
number nobody had, now printed. The counter was seen both silent (0 of 10 when nothing is cut) and
firing (10 of 10 when everything is) on a synthetic tokenizer before the arm was submitted.

---

## 2. What the number is likely to be — estimated, and declared as an estimate

Measured on the frozen corpus `Step3_docs/outputs_step3/4J_step3_corpus.jsonl`, **73,254 records**:

| | chars |
|---|---|
| median | 587 |
| p90 | 948 |
| p99 | 1,406 |
| p99.9 | 1,817 |
| max | 2,896 |

Converting with a **linear chars-per-token ratio anchored at the median** (587 chars = 200 OLMo
tokens = 303 Qwen tokens):

| backbone | chars/token | estimated longest record | estimated records over `max_len = 1280` |
|---|---|---|---|
| OLMo 3 7B | 2.935 | ~987 tokens | **0 of 73,254** |
| Qwen 2.5 7B | 1.937 | ~1,495 tokens | **1 of 73,254 (0.0014 %)** |

🔴 **This is a proxy and must not be quoted as a measurement.** Tokenization is not linear in
character count, and a long record in this corpus is long because it repeats grammar the tokenizer
handles efficiently — so the tail is **more likely over-stated than under-stated**. The real number
comes from the job. ⚪ Fold `es`'s training shard is **48,594** records, not the full 73,254, so the
fold-level count can only be smaller.

**What this changes about the decision: nothing.** It tells us the likely regime is *zero or a
handful*, which is why the decision is cheap to fix in advance rather than agonised over later.

---

## 3. The options

### (A) Report the arm with its truncation rate beside it — **RECOMMENDED**

Leave `--max-len 1280`. Print the count. Any sentence quoting the arm's loss carries the truncation
rate in the same breath.

* ✅ **The recipe stays identical**, which is the only thing that makes the two arms comparable.
* ✅ **The asymmetry becomes a reported finding rather than a hidden one** — "a fixed token budget is
  a tighter budget for a tokenizer with a coarser vocabulary" is itself part of *what the
  alternative backbone would have cost*, which is the arm's stated purpose.
* ✅ **No re-run**, and no second decision later.
* ⚪ Cost: if the rate is large, the loss comparison is genuinely contaminated and must be stated as
  such. At an estimated 1 record in 73,254 it is not.

### (B) Raise `--max-len` for the Qwen arm only

* ❌ **Breaks "same recipe" in the other direction.** Two arms at different token budgets is two
  schedules, not two backbones.
* ❌ **It is a post-hoc parameter change made because a number came out inconvenient** — the move
  this project refuses by rule.
* ⚪ The one thing in its favour: it removes the contamination rather than declaring it. That matters
  only if the rate is large enough to move the loss.

### (C) Raise `--max-len` for **both** arms and re-run everything

* ✅ Genuinely restores symmetry.
* ❌ **Re-runs three reported Leg-5 folds plus the ceiling** to fix an estimated single record, and
  every `G4.x` number on the board is re-derived. Cost wildly out of proportion.
* ❌ It would also **move a reported result to accommodate a comparison arm**, which inverts which of
  the two is load-bearing.

---

## 4. 🔴 THE RULE, FIXED IN ADVANCE

**Take (A) — report the arm with its truncation rate — unless the measured rate on fold `es`'s
training shard exceeds 1.0 %.**

Above 1.0 %, do **not** silently take (B) either: the arm is reported as **contaminated** and the
choice between (B) and (C) escalates to the author as a new decision, with the measured rate in hand.

⚪ **Why 1.0 % and why it is written now.** It is not tuned to the estimate — it is two to three
orders of magnitude above it, which is the point: a threshold that the expected outcome clears by a
wide margin cannot be accused of having been placed to produce a particular verdict. If the real
number lands near 1 %, that is a genuine surprise and deserves a person, not a rule.

🔴 **What may never be done, whatever the number:** raise `--max-len` on the Qwen arm alone and then
report the two arms as "the same recipe". If (B) is ever taken, the sentence "same recipe" comes out
of the paper with it.

---

## 5. What must be written up regardless of the count

1. **The truncation rate is reported beside the arm's losses**, even when it is exactly 0 — a zero
   that was measured is a result; a zero that was assumed is what this whole section is about.
2. **`G4.2`'s delimiter basis is tokenizer-dependent.** `delimiter_token_ids()` is computed from
   whichever tokenizer is loaded, so this arm's delimiter/content split is measured on **Qwen's
   vocabulary**. 🔴 **The VERDICT is comparable across arms; the NUMBERS are not.** Same discipline
   already applied to the ceiling run.
3. **`G4.8` asserts tokenizer identity against the base checkpoint** (`D-S4-2`), so a PASS here means
   *"this really is the Qwen tokenizer"*, not *"this matches OLMo"*.
4. **Single fold.** `es`, pre-named 2026-08-14. `prereg.md`: the pre-named fold is used for *exactly
   two* single-fold measurements — the ceiling and this arm — and **both must be reported as
   single-fold**. Quoting either across the corpus is quoting one fold as three. ⚪ The launcher
   **refuses** any other fold rather than accepting one silently.

---

## 6. What this document does NOT do

* **It does not move `--max-len`.** Nothing is changed by this file; it fixes what to do when a
  number arrives.
* **It does not create a gate.** The truncation count is a counter with no verdict, deliberately.
* **It does not touch `prereg.md`** — md5 `e4243e07cdd80c9c846b91f40e3e8c45`, unchanged.
* **It does not re-open the backbone choice.** `RL05` decided the recipe and `RL18`'s Qwen
  recommendation was already vetted and rejected as the primary; the arm exists to report the cost of
  the alternative, not to relitigate it.

---

## 7. Evidence

| | |
|---|---|
| the arm | `tools/4thJ_step4_qwen_fold.sh`, job **`1287613`** |
| the counter | `tools/4thJ_step4_train.py`, `DiaryDataset.__init__` (backup `.bak_f157`) |
| the 200 / 303 token measurement | `Step4_docs/4thJ_04_finetuneLLM.md:92–97`, Speed jobs `1234177`…`1234219` |
| the corpus the estimate was measured on | `Step3_docs/outputs_step3/4J_step3_corpus.jsonl`, 73,254 records, `corpus_md5 ca89d2295603c547f2384a40dd1909ba` |
| the single-fold rule | `Step6_docs/outputs_step6/prereg.md:90` |
| `G4.2`'s basis | `tools/4thJ_step4_train.py`, `delimiter_token_ids()` |

---

## 8. AUTHOR'S RULING

| | |
|---|---|
| **Decision** | 🟢 **Option (A) APPROVED**: Keep `--max-len 1280` fixed across all arms; report the Qwen comparison arm with its exact empirical truncation rate printed beside the losses and evaluation metrics (subject to the $\le 1.0\%$ threshold rule in §4). |
| **Rationale** | 1. **Recipe Integrity**: Preserves exact hyperparameter and token budget symmetry across OLMo and Qwen backbones.<br>2. **Transparent Reporting**: The tokenizer tokenization density difference is part of the comparative cost analysis and is reported transparently.<br>3. **Low Truncation Risk**: The estimated truncation rate is negligible ($\sim 0.0014\%$). If the measured rate exceeds $1.0\%$, the run will be flagged as contaminated and escalated before any claim is made. |
| **Date** | 2026-08-26 |

---

### Author's Directives:
1. **Single-Fold Reporting**: Report the Qwen comparison strictly on pre-named fold `es`, as pre-registered in `prereg.md:90`.
2. **Tokenizer Basis for `G4.2`**: Note in the manuscript that delimiter token parsing is evaluated on Qwen's native vocabulary.
3. **Invariants**: `prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) remains strictly frozen. No re-runs or threshold alterations permitted.
