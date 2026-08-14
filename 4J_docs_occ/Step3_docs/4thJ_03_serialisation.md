# Step 3 — Serialisation and tokenisation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 3. Validation: `4thJ_03_serialisation_val.md`

---

## STATUS

**✅ FORMAT DECIDED (`RL07`, field semantics from `RL02`). ✅ TOKENIZER DECIDED 2026-08-14 by our own
measurement. Implementation OPEN, nothing built.**

---

## AIM

Turn one harmonised episode table into text the model reads, and back again **exactly**.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| Episode form, not slot form | `RL07`, measured: 196-326 tokens against 924-1310 |
| Tuple is `DUR,ACT,LOC,COP` — **no `START`** | `RL07`. Start is the running sum; carrying it is redundant and misdescribes what the model emits |
| `LOC` is the real HETUS code 10-39 | `RL02`, correcting `RL07`'s invented 1-6 |
| `COP` is **five flags**, not one digit | `RL02`, correcting `RL07` |
| `ACT` keeps **3 digits** | Author decision 6 |
| **No tokens are added to the vocabulary** | `RL05`. LoRA freezes embeddings; unfreezing costs ~16.8 GB of optimizer state and breaks GGUF and vLLM export |
| 🔴 **No mnemonic code remapping** | Our own measurement. It saves 12.9 % on Qwen and **costs 5.5 %** on the OLMo tokenizer we adopted |
| Tokenizer: **OLMo / dolma2 BPE** (`allenai/Olmo-3-1025-7B`, and identically `allenai/OLMo-2-0425-1B` for Leg-4) | Speed jobs 1234177, 1234199, 1234216 |

### The measurement that decided the tokenizer

One 25-episode diary in the adopted form, measured on Speed:

| Tokenizer | `311` | `45` | Episode | Full diary |
|---|---|---|---|---|
| **OLMo 2 / OLMo 3** | **1** | **1** | **8** | **200** |
| Qwen 2.5 / 3 / 3.5 | 3 | 2 | 12 | 303 |
| Mistral NeMo | 3 | 2 | 12 | 303 |
| Mistral 7B v0.3 | 4 | 3 | 13 | 304 |
| Llama 3.1, Gemma | *gated — not measured, nothing claimed* | | | |

**34 % shorter sequences for the identical string.** Leg-4 and Leg-5 share this tokenizer and this
vocabulary byte for byte, so **the serialised corpus is produced once and used by both legs.**

---

## INPUTS

* `../Step2_docs/outputs_step2/harmonised.parquet`
* `../Step2_docs/outputs_step2/copresence_availability.md` — the prefix must not claim a flag a
  country never recorded

---

## WORK ITEMS

### 3.1 — The record

```
<conditioning prefix>  |  DUR,ACT,LOC,COP  DUR,ACT,LOC,COP  ...  <eor>
```

**Prefix fields**, in a fixed order, all drawn from the design strata so that Step 5's unweighted-loss
argument holds:

`country`, `age band`, `sex`, `household type`, `economic status`, `day type`, `season`,
**`MODE`**, **`SCHEME`**

🔴 **`MODE` and `SCHEME` are constant across the entire training corpus** (paper self-completion;
ACL 2008/2010). They teach the model nothing today and cost a handful of tokens. They exist so that
adding a wave, or seventeen Track A countries, never changes the record format.

🔴 **There is no `YEAR` field and there never will be.** Naming the instrument cannot be
extrapolated; naming the time invites exactly the projection this paper does not make.

### 3.2 — The `COP` packing decision

Five binary flags must reach the model without costing five tokens per episode. Options, to be
decided at implementation and **recorded with the measurement that decided it**:

* a single 0-31 integer (one token on this tokenizer if the value is a single small number — verify);
* two digits;
* five characters.

**Whatever is chosen, discarding flags to save tokens is forbidden.** Paper 1 identifies co-presence
handling as the source of load overestimation, and the flags are why we can fix it.

**Definition of done:** the packing is chosen by measuring token cost on the real tokenizer, and the
measurement is in `outputs_step3/cop_packing_measurement.md`.

### 3.3 — The encoder and the decoder

Two functions, and the decoder is not optional:

* `encode(diary) -> str`
* `decode(str) -> diary`

**Requirement: `decode(encode(d)) == d` exactly, for 100 % of the corpus**, compared field by field,
not as a string. Reversibility is what makes the episode form lossless: each episode unpacks to
`DUR / 10` identical slots.

### 3.4 — Tokenizer assertions before any training run

From `RL05`'s failure-mode list, run once over 1,000 sampled records and again over the full corpus:

* `tokenize(detokenize(ids)) == ids`;
* every 3-digit `ACT` code is **1 token**;
* no record exceeds the context budget;
* 100 % of records terminate with the `<eor>` marker. 🔴 A corpus where some completions do not
  terminate produces a model whose generation never stops.

### 3.5 — Emit the training corpus

`outputs_step3/corpus.jsonl` — one record per diary, with a held-out split that is **by respondent,
never by diary**, so a person's two diary days cannot straddle the split.

Also emit `outputs_step3/token_stats.md`: token-length distribution per country, per stratum, and the
packing efficiency actually achieved against the 200-token benchmark.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step3/corpus.jsonl` | Step 4 (both legs) |
| `outputs_step3/encoder.py` + `decoder.py` | Step 7 — the decoder is what turns generated text back into diaries |
| `outputs_step3/token_stats.md` | Step 4 sequence-packing configuration |
| `outputs_step3/cop_packing_measurement.md` | The methods section |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`. CPU only — tokenizer work needs no GPU. Reuse the venv pattern from
`../tools/4thJ_tok_setup_and_run.sh`; it does not touch `envs/step4`.

---

## WHAT BLOCKS THIS STEP

Step 2 must have emitted `harmonised.parquet`.

**What this step blocks:** Step 4 has no input without it. Step 7's grammar is defined against this
record format, so a format change here is a Step 7 change.

---

## DEFINITION OF DONE

1. Record format frozen, prefix field order fixed and written down.
2. `COP` packing chosen **by measurement**, and the measurement recorded.
3. Round-trip exact on 100 % of the corpus.
4. All four tokenizer assertions pass on the full corpus, not a sample.
5. Corpus emitted with a respondent-level split.
6. All Step 3 gates PASS **and each has been seen failing**.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* Tokenizer closed by our own measurement rather than by `RL18`, which recommended the opposite on a
  mis-counted figure: it reported the mnemonic episode `45,wrk,11,0;` at 8 Qwen tokens when it is 11.
* 🔴 **The mnemonic remapping was one edit away from entering this document as a design element.**
  It would have made every diary 5.5 % *longer* on the tokenizer we actually adopted. Recorded
  because the near-miss is the useful part: a workaround devised for one tokenizer was about to be
  written into the serialisation schema for another.
