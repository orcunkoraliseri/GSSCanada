# HETUS-Wide Occupancy Generation with a Fine-Tuned Open-Weight LLM
### Cross-National Occupant Behaviour for BEM/UBEM — Paper 4 of the series
#### Full Pipeline Overview — one model, many countries (Residential first)

---

## AIM

Replace the **one country, one trained-from-scratch model** pattern of papers 1 to 3 with **one
open-weight language model, fine-tuned once, that generates activity-resolved daily diaries and the
occupant attributes attached to them, for any country inside the HETUS harmonised framework** — and
prove the transfer claim by holding a country out of training entirely and scoring the generated
population against that country's published aggregate statistics.

The building-science payload stays: diaries become EnergyPlus schedules and activity-driven end-use
loads for European residential archetypes, so the paper ends in simulated energy, not in a metric table.

> **Series position.** Paper 1 (*Energy and Buildings* 357 (2026) 117155, CENTUS) = Italy, ISTAT CENSUS
> plus TUS, LSTM and Transformer, 0.98 multitask classification accuracy, and an **explicit but untested
> claim that HETUS standardisation makes the approach globally adaptable.** Paper 2 (2J) = Canada,
> residential plus temperature, EnergyPlus. Paper 3 (3J) = Canada, four channels, mixed-use tower, 2005
> to 2030. **Paper 4 (this doc) tests paper 1's untested claim, with a different class of model.**

---

## 🔴🔴 AMENDMENT 2026-08-15 — READ THIS BEFORE ANY COUNT BELOW. **THE CORPUS IS THREE COUNTRIES.**

**Author decision 16, 2026-08-15: FRANCE IS EXCLUDED.** Progedo demande n°38663 has no arrival date
and the project will not wait on it. **Everywhere this document says four countries, read THREE —
Italy 2013-14, Spain 2009-10, UK 2014-15**, all three already built. The rows below are kept unedited
because this document's style is to make reversals visible, not to rewrite history.

| Reads below | Now |
|---|---|
| four countries, LOCO trains on three | 🔴 **three countries, LOCO trains on TWO** |
| four-fold rotation, four adapters, four reported results | 🔴 **three-fold rotation** |
| 6 Leg-5 + 4 Leg-4 jobs | 🔴 **5 Leg-5 + 3 Leg-4** |
| Step 8: four populations | 🔴 **three populations** |
| `V1.a`/`V2.a` FAIL below 4 countries | 🔴 **below 3** |
| Track A widens 4 → 17 | 🔴 **3 → 17**, so it is worth more, not less |

✅ **The pre-named fold does not move: it is still held-out SPAIN**, because the alphabetical ISO rule
(ES, FR, GB, IT) returns ES with or without France. **Nothing about the pre-registration was re-taken.**

🔴 **If France arrives later:** before any fold is **scored** it may be re-admitted in full and every
count reverts. After the first fold is scored the design is frozen — France can then only be an extra
held-out country reported separately, never a fourth fold. Full text in the parent plan's progress log.

**Also amended the same day, earlier:** Step 1 is now a **sixteen-gate** specification (M-1 to M-5;
`G1.6` split into `G1.6a`/`G1.6b`, new `G1.12`), and Step 2's day origin is **decided — 04:00, cyclic
rotation, D-S2-5**, with the age floor moving 11 → **10** because 11 was France's minimum.

---

## 🔴 STATUS 2026-08-14 — ALL SIXTEEN REPORTS ARE BACK AND VETTED

> **Superseded in part.** `RL17` and `RL18` returned later the same day; open decision 3 was closed by
> our own measurement on Speed; the author then narrowed the corpus to **HETUS only, four countries,
> one wave each**. One claim in this section's lineage — the Llama licence clause — turned out to be
> false. Read the scope table, then **STATUS 2026-08-14, LATER** immediately after it.

The 2026-08-13 banner said *nothing is decided and nothing is built*. Half of that is no longer true.
**Nine of the twelve open decisions are now closed on evidence. Nothing is still built.**

**Both kill switches cleared, and a third fired.**

| Switch | Report | Verdict |
|---|---|---|
| Can we get the data at all? | `RL01` | **CLEARED, with a route change.** Eurostat central microdata exists only for the 2010 round and needs institutional recognition Concordia does not yet hold, at 12 to 14 weeks. **Track B becomes the primary corpus**, not the fallback |
| Is it already published? | `RL03` | **CLEARED.** Zero direct hits. Adjacent LLM-mobility work exists and is the honest nearest neighbour, not a competitor |
| Is an LLM even the right instrument? | `RL06` | **CLEARED CONDITIONALLY, and the condition is severe.** The LLM loses to a from-scratch conditional Transformer on every axis except cross-national transfer. **If the paper is not framed on transfer, the method is wrong.** That was already our position; it is now evidenced rather than asserted |
| 🔴 May we release the model? | `RL10` | **FIRED. NO.** Weights and adapters trained on restricted microdata may not be published. The deliverable changes from a model to a **synthetic dataset plus code plus a fully public stand-in pipeline** |

> **On `RL10`, author's decision 2026-08-14: accepted, and it is not treated as a wound.** The paper
> describes the method fully enough to be reproduced by anyone who obtains the same data, which is what
> a methods paper is for. We publish the generated data and the code; the weights stay internal. This is
> a normal position for work built on official statistics, not a concession.
>
> Note that `RL04` reached the opposite conclusion by reading only the *model* licence (Apache 2.0
> permits adapter release) and never reading the *data* agreement. Both are right about their own
> object. **The binding constraint is the data agreement, not the model licence**, so `RL10` governs.
> Recorded rather than smoothed over, because it is exactly the class of error that reaches a
> manuscript.

---

## 🔴 SCOPE, FIXED BY THE AUTHOR 2026-08-14

Four decisions taken after reading the reports. They **narrow** the paper, which is the direction that
makes it finishable.

| # | Decision | Consequence |
|---|---|---|
| 1 | **The model is not released, and that is fine.** The method is described in the paper | Stop treating this as a limitation to apologise for. It becomes a Data Availability statement |
| 2 | ~~**The corpus is five countries, and it is MULTI-WAVE** — Italy, Canada, Spain, UK, France, with several survey cycles each~~ | 🔴 **SUPERSEDED the same day by decisions 5 and 6 below.** The entry is kept rather than deleted so the reversal is visible: it was taken before the wave inventory existed, and the inventory is what reversed it |
| 3 | 🔴 **There is no forecast in this paper.** Not deferred, not attempted, not a limitation. **Out of scope** | The genuine idea is *the method of applying a fine-tuned LLM across the HETUS and wider time-use framework*. That is the contribution and it does not need a projection to be one |
| 4 | 🔴 **The hard null is the aim, not an obstacle** | Beating real diaries from the other countries reweighted to the held-out country's demographics is **what the experiment is for**. Stated as the objective in the introduction, not buried in the evaluation section |
| 5 | 🔴 **The corpus is HETUS ONLY. No Canada, no United States** | **Four countries: Italy, Spain, UK, France.** The Canadian GSS cycles and ATUS leave the corpus entirely. The paper tests paper 1's claim about **HETUS standardisation**, so a corpus made only of HETUS members is the corpus that tests it. **Two consequences: Track C, the public ATUS stand-in, goes with them, and leave-one-country-out now trains on three** |
| 6 | 🔴 **ONE wave per country — the HETUS 2010 round** | **Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10.** Earlier waves stay in the project as held-out validation and are never training data. This keeps 3-digit activity codes, one slot length, one collection mode and one coding-list generation, and it is the exact round the Eurostat SUF covers — so if Track A lands, the corpus widens from four countries to seventeen **with no harmonisation change at all** |

**Decisions 5 and 6 reverse decision 2, and the reversal is the point.** Decision 2 was taken before
the wave inventory existed. `RL17` then built it, and the inventory shows that three of the four
second waves sit on the far side of the ACL 2000 coding break — which our own Step 2 rule says forces
pooling at 2-digit, and 2-digit is what starves Step 9's appliance mapping. Worse, **UK 2000-01 uses
15-minute slots, so its episode durations are multiples of 15 and our grammar requires multiples of
10.** That single wave is not admissible to the 145-state tally automaton without re-quantising every
episode boundary. Depth in time cost more than it bought, and the cost was only visible once the
inventory was on the table. **Limitation C3 falls away with the pooling it described.**

**Decision 3 deserves one more sentence, because it removes something the series has always had.**
Papers 2 and 3 both ended in a projection, and dropping it will feel like a loss. It is not. Those
papers had four survey cycles from one country and a defensible trend. Here the contribution is that
**one model serves a framework of countries at all**, and attaching a weakly-supported forecast to a
strong methodological claim would have given a reviewer the easiest possible thing to attack.

---

## 🔴 STATUS 2026-08-14, LATER — `RL17` AND `RL18` BACK, AND THE BACKBONE WAS SETTLED BY OUR OWN MEASUREMENT

Two more reports returned (`RL17` adjudication, `RL18` model family) and **open decision 3 was then
closed on Speed rather than on either of them.** Five CPU jobs were run — `1234177`, `1234192`,
`1234199`, `1234211`, `1234216` — loading the real tokenizers, reading the real configs, reading the
vLLM registry source, and reading the licence metadata of every candidate. The scripts are in
`tools/` and the raw logs are on `/speed-scratch/o_iseri/`.

**This was worth doing, and the reason is uncomfortable: `RL18` recommended a backbone on two claims
that are false, and one of them is a number it presents as measured.**

### What the tokenizers actually do

One 25-episode diary in the adopted `DUR,ACT,LOC,COP;` form, and the same nine code strings, put
through every candidate we could load. Gemma and Llama are gated repositories and returned `401`
without a token, so **those two rows are not measured and are not claimed.**

| Repository | Architecture | Context | `311` | `45` | Diary, numeric | Diary, mnemonic |
|---|---|---|---|---|---|---|
| **`allenai/Olmo-3-1025-7B`** | `Olmo3ForCausalLM` | **65,536** (sliding 4,096) | **1** | **1** | **200** | 211 |
| `allenai/Olmo-3-1125-32B` | `Olmo3ForCausalLM` | 65,536 (sliding 4,096) | 1 | 1 | 200 | 211 |
| `allenai/OLMo-2-1124-7B` | `Olmo2ForCausalLM` | 4,096 | 1 | 1 | 200 | 211 |
| `allenai/OLMo-2-0425-1B` | `Olmo2ForCausalLM` | 4,096 | 1 | 1 | 200 | 211 |
| `Qwen/Qwen2.5-7B` | `Qwen2ForCausalLM` | 131,072 | 3 | 2 | 303 | 264 |
| `Qwen/Qwen3-8B-Base` | `Qwen3ForCausalLM` | 32,768 | 3 | 2 | 303 | 264 |
| `Qwen/Qwen3.5-9B-Base` | `Qwen3_5ForConditionalGeneration` | not readable | 3 | 2 | 303 | 264 |
| `mistralai/Mistral-Nemo-Base-2407` | — | — | 3 | 2 | 303 | 267 |
| `mistralai/Mistral-7B-v0.3` | — | — | 4 | 3 | 304 | 276 |

**The OLMo/dolma2 BPE holds every three-digit activity code as a single token, and the whole Qwen
lineage does not.** That is a **34 % shorter sequence** for the same diary, and it is the single
largest lever available on training and generation cost in this project. It survives the obvious
objection: Qwen3 and Qwen3.5 use the same tokenizer as Qwen2.5, so the gap is a property of the
tokenizer family and not of one ageing checkpoint.

### The two `RL18` defects

1. 🔴 **`RL18` D-Part-C states that the mnemonic episode `45,wrk,11,0;` costs 8 tokens in Qwen2.5,
   "fully matching Llama 3.1's token efficiency". Measured, it costs 11.** `RL18` counted `45` as one
   Qwen token; it is two, and `wrk` is two (`wr` + `k`), not one. The mnemonic trick is real but much
   smaller than advertised — it takes a Qwen diary from 303 to 264 tokens, a 12.9 % saving, not to
   parity with a one-token tokenizer. **And on the OLMo tokenizer the same trick makes diaries
   longer, 200 to 211**, because it replaces a one-token number with a two-token string. A workaround
   proposed for one tokenizer was about to be written into the serialisation schema for all of them.
2. **`RL18`'s "open-weight landscape as of 2026-08-14" contains no OLMo 3, no Qwen3 and no Llama 4.**
   It stops in early 2025 and then asserts that nothing after May 2026 changes its conclusions. The
   vLLM registry we fetched the same day lists `Olmo3ForCausalLM`, `Qwen3ForCausalLM`,
   `Qwen3MoeForCausalLM`, `Qwen3NextForCausalLM` and `Qwen3_5ForCausalLM`. This is exactly the version
   rot `L18` was written to catch, in the report written to catch it.

### The serving stack, read from the vLLM source rather than from a report

Fetched from `vllm/model_executor/models/registry.py` on `main`:

```
"Olmo3ForCausalLM":  ("olmo3",        "Olmo3ForCausalLM")        <- native kernel
"Qwen2ForCausalLM":  ("qwen2",        "Qwen2ForCausalLM")        <- native kernel
"Olmo2ForCausalLM":  ("transformers", "TransformersForCausalLM") <- generic fallback
"OlmoForCausalLM":   ("transformers", "TransformersForCausalLM") <- generic fallback
```

**OLMo 2 has no native vLLM implementation and OLMo 3 does.** That, plus the context lift from 4,096
to 65,536, is why the backbone is OLMo 3 and not the OLMo 2 row that first looked attractive.
XGrammar was cleared as a non-issue: it detects vocabulary type (`RAW` / `BYTE_FALLBACK` /
`BYTE_LEVEL`) from the vocabulary itself and is model-agnostic, so it constrains any of these.

### Licences, read from each repository rather than cited

| Repository | Parameters, from safetensors | Gated | Licence | Read from |
|---|---|---|---|---|
| `allenai/Olmo-3-1025-7B` | 7.30 B | no | Apache 2.0 | card tag **and** card body: *"The code and model are released under Apache 2.0"* |
| `allenai/Olmo-3-1125-32B` | 32.23 B | no | Apache 2.0 | same |
| `allenai/OLMo-2-0425-1B` | 1.48 B | no | Apache 2.0 | same |
| `Qwen/Qwen2.5-7B` | 7.62 B | no | Apache 2.0 | full `LICENSE` file, 11,343 bytes |
| `Qwen/Qwen2.5-0.5B` / `-1.5B` | 0.49 B / 1.54 B | no | Apache 2.0 | full `LICENSE` file |
| `Qwen/Qwen3-8B` | 8.19 B | no | Apache 2.0 | full `LICENSE` file |
| 🔴 `Qwen/Qwen2.5-3B` | 3.09 B | no | **Qwen Research License, non-commercial** | full `LICENSE` file, *"FOR NON-COMMERCIAL PURPOSES ONLY"* |
| `mistralai/Mistral-7B-v0.3` | 7.25 B | no | Apache 2.0 | card tag only |
| 🔴 `meta-llama/Llama-3.1-8B` | 8.03 B | **manual gate** | Llama 3.1 Community | **could not read**, see below |

Two honest caveats. **The Ai2 repositories carry no `LICENSE` file**; the Apache 2.0 statement is in
the model card, which also adds *"intended for research and educational use in accordance with Ai2's
Responsible Use Guidelines"*. That is a statement of intent in a card, not a term of Apache 2.0, and
it places no condition on generated text — but it is written down here so nobody rediscovers it in
review. And **`Qwen/Qwen2.5-3B` is confirmed non-commercial**, so the `RL04` warning about mixing
sizes inside the Qwen family is real and was verified, not repeated.

### 🔴 The Llama disqualification, as written in these documents, was wrong

This is the most serious finding of the round, and it is a correction to our own documents rather
than to a report alone. Every version of this plan disqualified Llama on one sentence, taken from
`RL04` and restated as fact by `RL18` B08: *"Llama 3.1 Community License Section 1.b forbids using
Llama outputs to improve any other non-Llama language model."*

**Meta's own licence files were fetched and read (job `1234219`). Llama 3.1 does not contain that
clause.** The Llama 3.1, 3.2 and 3.3 Community Licences contain a **naming requirement** instead:

> *"If you use the Llama Materials or any outputs or results of the Llama Materials to create,
> train, fine tune, or otherwise improve an AI model, which is distributed or made available, you
> shall also include 'Llama' at the beginning of any such AI model name."*

The anti-improvement clause is real, but it belongs to **Llama 2 and Llama 3**, where §1.b.v reads
*"You will not use the Llama Materials or any output or results of the Llama Materials to improve any
other large language model."* Meta dropped it at 3.1. The phrase count is unambiguous: the exact
string `improve any other large language model` occurs **once** in the Llama 2 licence, **once** in
the Llama 3 licence, and **zero** times in 3.1, 3.2 and 3.3.

**So Llama 3.1 was excluded from this project on a clause from a licence version we were not using.**
`RL04` introduced the error, `RL18` repeated it as a Tier-1 fact with High confidence, and both plan
documents carried it. It is corrected here rather than quietly deleted, because it is exactly the
class of error the vetting record exists to catch, and because the same mistake in the manuscript
would be a factual claim about a third party's licence.

**The decision does not change; the reason does.** Llama is still not selected, now for three
measured reasons instead of one misquoted one:

* the tokenizer advantage that was the entire case for Llama is **matched** by `Olmo-3-1025-7B` at
  200 tokens per diary, under Apache 2.0, so we no longer trade a licence for a tokenizer;
* Llama 3.1 still attaches a **naming condition** and an **Acceptable Use Policy incorporated by
  reference** to anything built downstream from its outputs, while Apache 2.0 attaches nothing at
  all. For a corpus released as unconditional CC BY 4.0 the cleaner licence is the correct one, and
  that argument stands on the clause that actually exists;
* the repository is **manually gated**, which is why we could not measure its tokenizer ourselves.
  🔴 **The "Llama tokenises `411` in one token" claim is therefore still unverified by us.** Both
  `RL17` and `RL18` assert it; neither is our own measurement, and the row stays labelled as such.

### What this means for the backbone

**Recommended: `allenai/Olmo-3-1025-7B` as the primary backbone, `Qwen/Qwen2.5-7B` retained as the
named comparison arm.** OLMo 3 wins on the only axis that is a hard cost — 200 tokens against 303 for
the same diary — while matching Qwen on everything that was supposed to be Qwen's advantage: Apache
2.0 with no condition on output, a native vLLM kernel, ungated weights, and enough context.

**It costs us one thing, and it is the thing the author asked for.** The OLMo 3 family has no base
checkpoint below 7B; the HF API returns 31 OLMo 3 repositories and only two are base models, 7B and
32B. The 3J Leg-2 → Leg-3 pattern of a cheap pilot leg before the reported leg therefore cannot be
run inside the OLMo 3 family.

✅ **Resolved by the author 2026-08-14. The legs continue the series numbering: 3J ended at Leg-3, so
4J is Leg-4 and Leg-5.**

| Leg | Model | Role |
|---|---|---|
| **Leg-4, pilot** | `allenai/OLMo-2-0425-1B` (1.48 B, Apache 2.0) | **Byte-identical tokenizer and vocabulary to Leg-5.** Shakes out the serialisation, the grammar, the tally automaton and the data pipeline — all of which are tokenizer-bound, so they carry to Leg-5 unchanged. Architecture and the 4,096 context differ, and that is the honest cost |
| **Leg-5, reported** | `allenai/Olmo-3-1025-7B` (7.30 B) | The measured backbone. This is the model the paper reports |

The alternative — Qwen2.5-0.5B → Qwen2.5-7B — keeps one architecture family across both legs but pays
the 50 % token penalty on every run, forever. A pilot exists to shake out the pipeline, and the
pipeline is tokenizer-shaped, so the same-tokenizer pilot is the better pilot even though the
architecture differs.

---

> 🟡 **Added 2026-09-03.** The box below is stale on several step statuses (Steps 2, 7, 8, 9 read OPEN;
> Step 10 reads PLANNED); the dated corrections are in `4thJ_00_HETUS_LLM_Pipeline.md`'s own per-step
> headers, not repeated here. The box itself is kept unedited, per this document's own registration rule
> at `:683` (new work is a new step, not a silent edit). No-core review:
> `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md`.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  STEP 0 — FEASIBILITY GATE                                                   ║
║  Status: ✅ CLEARED 2026-08-14 -- RL01, RL03, RL06, RL10 back and vetted     ║
║                                                                              ║
║  RL01 microdata: Track B is primary. Eurostat 2010 SUF applied for in        ║
║       parallel. Concordia is NOT a recognised research entity yet.           ║
║  RL03 prior art: zero direct hits. the gap is real.                          ║
║  RL06 method: LLM retained, but ONLY as a transfer instrument.               ║
║  RL10 release: weights withheld. synthetic data + code. ATUS track GONE      ║
║  EXIT CRITERION MET: corpus named, method chosen, release plan stated        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 1 — CORPUS DEFINITION & ACQUISITION                                    ║
║  Status: OPEN (executable) -- decided by RL01                                ║
║                                                                              ║
║  FOUR HETUS COUNTRIES, ONE WAVE EACH. author's decisions 5 and 6,            ║
║    2026-08-14. NO CANADA, NO UNITED STATES: this paper tests a claim about   ║
║    HETUS standardisation, so the corpus is HETUS members only.               ║
║    ISTAT IT 2013-14 (HELD, paper 1)  + INE ES 2009-10 (open download)        ║
║    UKDS UK 2014-15 (EUL registration) + INSEE FR 2009-10 (Progedo/ADISP)     ║
║  🔴 WHY ONE WAVE. RL17 Part B built the inventory (IT 5, ES 3, UK 5, FR 4)   ║
║    and recommended TWO. the inventory itself argues against it: 3 of the 4   ║
║    second waves sit past the ACL 2000 break, which forces 2-digit codes      ║
║    and starves Step 9. UK 2000-01 is 15-MIN SLOTS, so its durations are      ║
║    multiples of 15 and the tally automaton takes multiples of 10.            ║
║    the one-wave set is ONE coding generation, ONE slot length, ONE mode.     ║
║  EARLIER WAVES STAY as HELD-OUT VALIDATION. never training data.             ║
║  TRACK A (parallel, not blocking): Eurostat HETUS 2010 SUF, 17 countries.    ║
║    Form A entity recognition for Concordia ~4 wk, then ~8-10 wk proposal.    ║
║    🔴 NOW MORE VALUABLE: our set IS the 2010 round, so Track A widens 4 ->   ║
║    17 countries with NO harmonisation change. LOCO trains on 3 without it.   ║
║  🔴 TRACK C IS GONE with ATUS. the zero-credential reproduction path went    ║
║    with it. INE ES is the only remaining no-registration source. OPEN.       ║
║  🔴 Round 1 (2000) has NO central Eurostat microdata, ever. Round 3 not      ║
║    before 2027. OUR WAVES COME FROM THE NATIONAL SERIES, NOT FROM EUROSTAT.  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — HARMONIZATION  <- the alphabet the model speaks                    ║
║  Status: OPEN -- specified by RL02                                           ║
║                                                                              ║
║  ACL: 10 major / 36 two-digit groups IDENTICAL across 2008 and 2018.         ║
║    3-digit differs (108 vs 116 codes). ACL 2000 (144 codes) is a real break. ║
║    -> ONE WAVE PER COUNTRY, so nothing is cross-wave and 3-DIGIT CODES       ║
║       ARE KEPT. this is what Step 9's appliance mapping needs.               ║
║  LOCATION: 10-19 stationary, 20-39 transport. 11 = Home.                     ║
║  🔴 CODE 11 MERGES DWELLING + YARD + GARDEN. presence in the CONDITIONED     ║
║    VOLUME is therefore NOT recoverable from location alone. rule adopted:    ║
║    indoor = (LOC==11 AND ACT not in {gardening, outdoor construction})       ║
║  CO-PRESENCE IS 5 BINARY FLAGS, not one code: alone / partner / children /   ║
║    other HH / other persons. paper 1's overestimation problem lives here.    ║
║  FILE SHAPE: RL17 adjudicated for RL02. the SUF is 3 relational files        ║
║    INDFILE/DDFILE/EFILE, with NATIVE START and DURATION in EFILE. RL01's     ║
║    flat 144-slot wide file is a national export, not the Eurostat delivery.  ║
║    -> parser STILL handles both. a verdict from a report is not a file.      ║
║  crosswalk: no longer needed for the primary corpus, which is HETUS-only.    ║
║    MTUS 69 stays as the bridge IF earlier waves are used in validation.      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — SERIALIZATION & TOKENIZATION                                       ║
║  Status: ✅ DECIDED. format by RL07, tokenizer by our own measurement.       ║
║                                                                              ║
║  EPISODE FORM WINS ON MEASURED TOKENS, not on preference:                    ║
║    verbose key-value 144 slots ... 2719-3327 tok                             ║
║    compact delimited 144 slots ... 924-1310 tok                              ║
║    EPISODE, minutes ............... 196-326 tok   <- adopted                 ║
║    JSON episodes ................. 753-975 tok                               ║
║  record = <conditioning prefix> | <episode tuples> <eor>                     ║
║  tuple  = DUR,ACT,LOC,COP   (no START: it is implied by the running sum)     ║
║  🔴 RL07's example strings use invented LOC codes 1-6 and a single COP       ║
║    digit. REPLACE with the real RL02 codes and 5 co-presence bits before     ║
║    any data is written. an example string is not a specification.            ║
║  NO ADDED TOKENS. LoRA freezes embeddings; unfreezing costs ~16.8 GB of      ║
║    optimizer state and breaks GGUF/vLLM export. trap named, trap avoided.    ║
║  MEASURED, not reported: OLMo tokenizer 200 tok/diary, Qwen 303. code 311    ║
║    is ONE token in OLMo, THREE in every Qwen. see STEP 4 and the status      ║
║    section above. the mnemonic workaround HURTS the OLMo tokenizer.          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: FINE-TUNED OPEN-WEIGHT LLM                               ║
║  Status: ✅ FAMILY DECIDED by measurement. recipe DECIDED by RL05.           ║
║                                                                              ║
║  🔴 "GEMMA 4" DOES NOT EXIST. Gemma 2 = 2B/9B/27B, Gemma 3 = 1B/4B/12B/27B.  ║
║    there is no gemma-2-7b and no gemma-3-8b either. (RL04 caught the trap.)  ║
║  THE TRADE-OFF WAS RESOLVED BY MEASUREMENT, jobs 1234177/92/99/211/216:      ║
║    allenai/Olmo-3-1025-7B  200 tok/diary, Apache 2.0, native vLLM kernel,    ║
║      65536 ctx, ungated, 7.30B   <- ADOPTED as the primary backbone          ║
║    Qwen/Qwen2.5-7B  303 tok/diary, Apache 2.0, native vLLM, 131072 ctx       ║
║      <- retained as the named COMPARISON ARM, not the primary                ║
║    Mistral-7B-v0.3  304 tok/diary. the "Tekken 3-digit atomic" claim in      ║
║      RL04 and RL07 is FALSE: v0.3 splits 311 into FOUR tokens. RL17 was      ║
║      right about this and we confirmed it ourselves.                         ║
║  🔴 THE LLAMA CLAUSE WE DISQUALIFIED IT ON DOES NOT EXIST IN LLAMA 3.1.      ║
║    "improve any other large language model" is Llama 2 and Llama 3 only.     ║
║    3.1/3.2/3.3 carry a NAMING requirement instead. RL04 and RL18 both got    ║
║    this wrong and we carried it. Llama is still not selected, but for        ║
║    measured reasons now: see the status section above.                       ║
║  🔴 NO SUB-7B BASE EXISTS IN OLMo 3, so the legs use two checkpoints:        ║
║    LEG-4 pilot  allenai/OLMo-2-0425-1B  1.48B, SAME tokenizer and vocab      ║
║    LEG-5 report allenai/Olmo-3-1025-7B  7.30B, the measured backbone         ║
║    author decided 2026-08-14. numbering continues from 3J, which ended at    ║
║    Leg-3. this is the one thing the switch costs.                            ║
║  RECIPE (RL05): base checkpoint, SFT with completion-only loss masking,      ║
║    rsLoRA r=32 on ALL linear layers (attn + MLP), bf16, packed sequences     ║
║    with block-diagonal masks, 3 epochs. Full FT with 8-bit AdamW as the      ║
║    CEILING run, not the primary. QLoRA rejected: we have 80 GB, we do not    ║
║    need 4-bit. (note: RL05's 2-6% QLoRA degradation rests partly on an       ║
║    unverifiable Tier-3 source. we reject QLoRA for sufficiency, not proof.)  ║
║  🔴 NO SEQUENTIAL COUNTRY-BY-COUNTRY FINE-TUNING. joint multi-task with a    ║
║    country token. sequential costs 40-70% on earlier countries.              ║
║  HARDWARE, MEASURED 2026-08-13: A100 80GB reachable as nvidia_a100_7g.80gb,  ║
║    one per node on speed-37,39-43. LoRA peak ~18-22 GB. full FT 8-bit ~41-49 ║
║    GB. both fit. 20GB slices carry the sweeps.                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — CONDITIONING & POPULATION LINKAGE                                  ║
║  Status: ✅ DECIDED -- by RL09                                               ║
║                                                                              ║
║  TWO STAGES, and the separation is now evidenced not merely tidy:            ║
║    (a) IPF / combinatorial optimisation on census marginals -> the people    ║
║    (b) the LLM conditioned on each synthetic person -> their day             ║
║  🔴 TRAINING LOSS IS UNWEIGHTED. because the prefix carries the design       ║
║    strata, sampling is conditionally ignorable; weighted loss in an          ║
║    overparameterised net inflates gradient variance and moves nothing.       ║
║    representativeness is enforced in stage (a), where it is exact.           ║
║  🔴 WE DO NOT RAKE OUR OWN OUTPUT. raking repairs margins and cannot repair  ║
║    joints. raking is used ONLY to build the null we must beat (Step 6).      ║
║    we do not get to use the trick we benchmark against.                      ║
║  NO AGGRESSIVE top-p / top-k. truncation deletes the 03:00 laundry household ║
║    and that household is the peak-load case. temperature scaling on a        ║
║    validation split + grammar mask instead. p<=0.98 if p is used at all.     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — TRANSFER  <- WHERE THE PAPER IS WON OR LOST                        ║
║  Status: OPEN -- null model HARDENED by RL06 and ADOPTED AS THE OBJECTIVE    ║
║                                                                              ║
║  LEAVE-ONE-COUNTRY-OUT: train on N-1, generate the held-out country from     ║
║    its published marginals ONLY, score against its published tables.         ║
║    N = 4 (IT, ES, UK, FR), so TRAINING IS ON THREE. Track A would raise it.  ║
║  🔴 THE NULL IS THE AIM, NOT AN OBSTACLE. author's decision 2026-08-14.      ║
║    the target: BEAT REAL DIARIES FROM THE N-1 POOL, RAKED BY IPF TO THE      ║
║    HELD-OUT COUNTRY'S PUBLISHED MARGINALS.               (RL06 Null 3)       ║
║    every raked donor is an authentic human day with perfect grammar and      ║
║    real variance. this is stated in the INTRODUCTION as the objective, not   ║
║    buried in the evaluation section. an experiment whose bar is announced    ║
║    up front and then met is worth more than one that meets a bar chosen      ║
║    afterwards. RL08's pooled-average null is demoted to secondary.           ║
║  THREE NAMED REVIEWER ATTACKS ON TRANSFER, each with its counter-measure:    ║
║    contamination (model read about the country on the web) -> fictional-     ║
║      country token with perturbed marginals must still follow the vector     ║
║    marginal-matching illusion -> score joints and co-presence cross-tabs     ║
║      that were NOT in the conditioning prompt                                ║
║    geographic-proximity proxy -> the nearest-neighbour-country null          ║
║  🔴 NO FORECAST. NOT DEFERRED, NOT ATTEMPTED: OUT OF SCOPE.                  ║
║    author's decision 2026-08-14, and RL16 independently says the data        ║
║    could not have carried one anyway. no year token, no projection, no       ║
║    scenario levers, no 2030. THE CONTRIBUTION IS THE METHOD OF APPLYING A    ║
║    FINE-TUNED LLM ACROSS THE HETUS AND WIDER TUS FRAMEWORK. that is a        ║
║    contribution on its own and does not need a projection bolted to it.      ║
║  EXTRA WAVES ARE OUT OF THE TRAINING CORPUS (author decision 6). they are    ║
║    HELD-OUT VALIDATION only. there is no leave-one-wave-out axis, and        ║
║    there was never a trend to extend.                                        ║
║  COVID and the paper-to-app mode change sit inside the most recent waves     ║
║    unevenly by country -> flagged regime, excluded from pooling if needed.   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — CONSTRAINED GENERATION AT SCALE -> SCHEDULES                       ║
║  Status: OPEN -- mechanism DECIDED by RL12                                   ║
║                                                                              ║
║  RL07 (episodes, for tokens) vs RL12 (fixed slots, for grammar) RESOLVED     ║
║    IN FAVOUR OF EPISODES: durations are multiples of 10 min summing to       ║
║    1440, so the "unbounded sum" is a 145-state TALLY AUTOMATON. finite,      ║
║    therefore regular, therefore enforceable. RL12 names this escape itself.  ║
║    we keep the 4x token saving AND the hard guarantee.                       ║
║  ENGINE: vLLM with XGrammar (<8% latency). NOT naive Outlines/LogitsProcessor║
║    (50-200% penalty). custom processor kept only as a unit-test oracle.      ║
║    VERIFIED IN THE vLLM SOURCE: Olmo3ForCausalLM and Qwen2ForCausalLM have   ║
║    NATIVE kernels; Olmo2ForCausalLM routes to the generic Transformers       ║
║    fallback. XGrammar is model-agnostic (it detects vocab type itself).      ║
║  🔴 REPORT THE CONSTRAINT-FIRING RATE, PER STRATUM. 100% validity after      ║
║    masking is a property of the DECODER, not the model. the base model must  ║
║    show a high firing rate or the mask is not doing anything.                ║
║  masking renormalises probability over allowed tokens: not neutral. audit    ║
║    against an unconstrained rejection-sampled control batch.                 ║
║  Schedule:File, not Schedule:Compact, at urban scale. Interpolate=No.        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 8 — BEM/UBEM SIMULATION (European archetypes)                          ║
║  Status: OPEN -- scoped by RL13                                              ║
║                                                                              ║
║  🔴 THERE IS NO EUROPEAN DOE PROTOTYPE LIBRARY. no official .idf archetypes  ║
║    exist. TABULA/EPISCOPE ships PARAMETER TABLES AND EXCEL, not models.      ║
║    -> we build the .idf from TABULA Italy parameters via OpenStudio, or      ║
║       generate via TEASER. that model-building is OURS and it was not in     ║
║       the original scope. 3 to 5 days, and it is on the critical path.       ║
║  🔴 EN 16798-1 IS PAYWALLED AND RL13 CORRECTLY REPORTED "COULD NOT OPEN"     ║
║    RATHER THAN RECONSTRUCTING ANNEX C. the negative control fired. so the    ║
║    baseline we replace is the OPEN one: ISO 13790 Annex G Table G.12 /       ║
║    UNI/TS 11300-1 flat 4.0 W/m2. that is a better foil anyway: a flat        ║
║    continuous gain is exactly what a diary is supposed to beat.              ║
║  EUI plausibility bands: as-modelled = PASS, empirical = INFO.               ║
║  🔴 UNINJECTED CONTROL RUNS FIRST. 3J's most expensive lesson: a gate that   ║
║    no untreated control can pass is measuring the band, not the model.       ║
║  two probes before any campaign: scenario-differentiation (byte-identical    ║
║    outputs = automatic FAIL) and the stale-output guard.                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 9 — ACTIVITY-DRIVEN END-USE LOADS  <- the reason to use a DIARY at all ║
║  Status: OPEN -- sourced by RL13                                             ║
║                                                                              ║
║  DO NOT INVENT THE MAPPING. CREST (Richardson 2010), Widen (2009),           ║
║    LoadProfileGenerator (Pflugradt 2016) and RAMP already map activity ->    ║
║    appliance via a two-stage stochastic trigger: P(appliance | activity)     ║
║    then a rated power curve runs its cycle to completion. we ADAPT, we do    ║
║    not author. an ad-hoc mapping is the easiest thing in this paper for a    ║
║    reviewer to reject.                                                       ║
║  DHW: Jordan & Vajen 4-event tapping model, 30-50 L/person/day at 60 C.      ║
║    3J found the DHW plant load-bearing in the energy result.                 ║
║  🔴 VALIDATION SCALE IS THE CATCH: these models validate at AGGREGATE        ║
║    scale (N=100-500 dwellings, R2>0.90) and NOT per dwelling. so the         ║
║    downstream claim is about load SHAPES and distributions, never about      ║
║    predicting one household. every mapping labelled VALIDATED or NOT.        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> 🔴 **The DHW line in the box above is a citation-collapse and must not be quoted** (2026-08-27,
> `FINDING 163`, work item 11.2 —
> `Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`). The **four-event tapping model**
> is Jordan & Vajen (2001), whose volumes are **per dwelling, 200 l/day, with no temperature stated
> anywhere in the report**. The **30–50 L/person/day at 60 °C** is a different source —
> **Fuentes et al. (2018)**, RSER 81(1): 1530–1547, DOI `10.1016/j.rser.2017.05.229`, named in
> `RL13` row 15 and cited in no artefact of this project. Step 9 built on the first and gated on the
> second, so `G9.7`'s scored quantity is **`200 / n_members`**. **No band is moved**; the manuscript
> question is `D-S11-1`, ruled together with `D-S9-2` item 7.

---

## VALIDATION GATES — thresholds now set

The 2026-08-13 version of this table read `TBD-RL08` in every row. `RL08` returned a ten-gate table
with each row marked literature-derived or project-chosen, which is what was asked for. **Three rows
are adopted with the provenance label corrected downward**, because `RL08` labelled as
literature-derived some thresholds whose *tolerance* is ours even though the underlying quantity is
published. The rule stands: never cite a project-chosen threshold to the literature.

**Tier 1 — Distributional fidelity (within-country, microdata available)**

| Metric | What it detects | Threshold | Provenance |
|---|---|---|---|
| Diurnal marginal divergence, mean JSD over 10 Level-1 activities | the generated day-shape is wrong | mean ≤ **0.015 bits**, max ≤ **0.025 bits** per activity, base-2 | **project-chosen** |
| Activity time-budget error, min/day/category/stratum | systematic over or under allocation | ≤ **15.0 min/day** per stratum, ≤ **8.0 min/day** population | 🔴 **project-chosen, now settled.** `RL17` A6 searched the Eurostat HETUS methodological guidelines (2008 and 2018/2020) and returned **`NOT FOUND`**: no universal margin-of-error table is published anywhere. The ±12-18 min figure is an analytical rule of thumb, not a standard. The literature label is dropped permanently; the tolerance is ours and is reported as such |
| Transitions per day, and transition-matrix TVD | over-smoothing, the classic generative tell | ≤ **1.50 transitions/day** absolute error; TVD ≤ **0.050** | **project-chosen** (the switching-rate literature bounds the quantity, not our tolerance) |
| Dwell-time distribution, Wasserstein-1 per activity | episodes the right length | ≤ **10.0 minutes** | **project-chosen** (= one survey slot width, which is why it is defensible) |

**Tier 2 — Collapse and memorisation (the two failures that would silently destroy the paper)**

| Metric | What it detects | Threshold | Provenance |
|---|---|---|---|
| 🔴 Within-stratum variance ratio, generated vs real | **distribution collapse**: everyone in a stratum gets the modal day | **0.80 ≤ VR ≤ 1.25** for every stratum with N ≥ 100 | **project-chosen**, pre-specified ±20 % band |
| Unique-sequence fraction and normalised entropy | diversity collapse at population scale | U ≥ **0.950** at N = 10,000; H_norm ≥ **0.900** | 🔴 **project-chosen, now settled as to provenance.** `RL17` A7 returned **`NOT FOUND`**: U > 0.98 is not a published benchmark in the time-use sequence literature, which works in entropy and optimal-matching terms instead. `RL08` invented it. **The threshold stays in the battery as a collapse sanity check, and the empirical baseline is still computed on the held ISTAT data before the gate is trusted. Not yet done** |
| 🔴 Distance to closest real record; nearest-neighbour distance ratio | **memorisation of a real respondent's diary** | P(d_min = 0) ≤ **0.05 %**; median d_min ≥ **12 slots**; NNDR < 0.33 in ≤ 0.1 % of records | **project-chosen**, disclosure-motivated (`RL10`) |
| 🔴 Membership inference, loss-based and reference-based | the adapter isolates individuals rather than population statistics | loss-MIA AUC ≤ **0.65**; reference-MIA (vs base model) AUC ≤ **0.75** | **new gate from `RL10`.** Reference-MIA is the sharper test because the base model is public |
| Conditional fidelity, classifier two-sample test | right days assigned to the wrong people | C2ST AUC ≤ **0.65** | **project-chosen.** Ideal is 0.50 and `RL08` set no bound |

**Tier 3 — Structural validity (`RL12`)**

| Check | Target |
|---|---|
| Episode durations sum to 1440 min | 100 %, enforced by the 145-state tally automaton |
| All codes inside the coding list | 100 % |
| Transition legality (no workplace-to-home with no travel episode) | 100 %, encoded as an FSM transition table |
| Co-presence consistent with the conditioning household | 100 %, via pre-compiled grammar variants indexed by household type |
| Unconstrained well-formedness, before any masking | ≥ **99.90 %** — this one measures the *model* |
| **Constraint-firing rate, per demographic stratum** | reported, not thresholded. Expect **> 35 %** on the untuned base model (control 1) and **< 2 %** on the fine-tuned model. A high rate with perfect validity means the harness did the work |

**Tier 4 — Transfer (the headline claim)**

| Check | Target |
|---|---|
| 🔴 Margin over the **demographically raked pooled-donor null** | **must be positive.** Pre-registered before the run. This replaces the pooled-average null as the bar |
| Margin over the nearest-neighbouring-country model | reported |
| Margin over the pooled all-country average diary | reported, now a **secondary** null |
| Held-out country vs its published Eurostat tables, Level-1 time budgets | MAPE ≤ **15.0 %** |
| 🔴 Pre-registered FAIL criteria, any one of which fails the claim | MAE ≥ the raked-donor null; **or** MAPE > 20 %; **or** the *sign* of the country's divergence from the European mean is inverted |
| Regression on held-*in* countries after adding a new one | bounded; joint training, not sequential, so this should be small by construction |

**Tier 5 — Downstream energy (ASHRAE Guideline 14 lineage, inherited from papers 2 and 3)**

| Check | Target |
|---|---|
| NMBE, monthly and hourly | ±5 % monthly, ±10 % hourly (Guideline 14) |
| CV(RMSE), monthly and hourly | 15 % monthly, 30 % hourly (Guideline 14) |
| Peak magnitude and timing | ±15 %, ≤ 1 h |
| Per-archetype EUI vs published band | as-modelled = PASS, empirical = INFO |
| 🔴 **Uninjected control run** | run **first**. If the control already fails a band, the band is being measured, not the model |

**Statistical discipline, and it is not optional at this N.** At 10^5 to 10^6 generated diaries every
two-sample test rejects: a 1.2 min/day difference in meal preparation gives p < 10^-15 while being
practically perfect. So **no gate above is a p-value**. Each is a bounded effect size, and each is
additionally reported as (a) a TOST equivalence test against a ±15 min/day margin and (b) a
sample-size-matched bootstrap, where the synthetic-to-real divergence must not exceed the real-to-real
split-half divergence. That last comparison is the honest one.

**Three negative controls, and the battery must be seen failing on each before it is trusted:**

| Control | Must PASS | Must FAIL | What it proves |
|---|---|---|---|
| Shuffled diary (slots permuted, totals preserved) | Tier 1 marginals, time budgets | transitions, dwell times | the battery sees sequence destruction |
| Modal-collapse generator (modal day per stratum) | structural validity, marginals | diversity, variance ratio | the battery sees collapse |
| Training-set replay | Tiers 1 to 7 perfectly | memorisation and MIA gates | the battery separates memorisation from generalisation |

---

## KEY DESIGN DECISIONS

| Decision | Rationale |
|---|---|
| The transfer experiment is the paper, not the model | **Now evidenced, not asserted.** `RL06` ranks a from-scratch 10M-parameter conditional Transformer above the LLM on fidelity, cost, throughput and structural validity, and gives it zero transfer ability. Pretraining buys nothing on tabular data past roughly 1,000 training records. Transfer is the only axis left, so it is the whole paper |
| Track B is the primary corpus and Track A runs in parallel | A 12 to 14 week institutional-recognition path is not a schedule risk we take on the critical path. Five countries we can download today beat seventeen that arrive in month four, and if they arrive the corpus simply widens |
| 🔴 ~~The public ATUS path is the *primary* reproducible experiment~~ **WITHDRAWN with the HETUS-only decision** | This was `RL15`'s answer to `RL10`: a fully public ATUS pipeline that anyone could run without a Eurostat licence. **The HETUS-only scope removes ATUS, and the reproducibility argument goes with it.** What remains is four national sources that are all free but not all instant — Spain's INE is an open download needing no registration, the other three need a free academic registration. 🔴 **This is now an open item, not a solved one** |
| Episode encoding, and the tally automaton that makes it safe | 196 to 326 tokens against 924 to 1310, measured. The grammar objection (a sum constraint is not regular) dissolves once you notice the sum is bounded and quantised: 145 states |
| 🔴 **The backbone is `allenai/Olmo-3-1025-7B`, chosen by our own measurement** | The OLMo tokenizer writes every three-digit activity code in **one** token and the whole Qwen lineage writes it in three: **200 tokens per diary against 303**, on the same string, measured on Speed. OLMo 3 also has a native vLLM kernel (OLMo 2 does not), 65,536 context, Apache 2.0 with no condition on generated text, and ungated weights. `Qwen/Qwen2.5-7B` is kept as the named comparison arm. **`RL18` recommended the opposite on two claims that measurement disproved** |
| 🔴 **The mnemonic code remapping is NOT adopted** | `RL18` proposed replacing numeric codes with one-token mnemonics and reported it brings Qwen to parity. Measured, it takes Qwen from 303 to 264 tokens, not to 200, and on the adopted OLMo tokenizer it makes diaries **longer** (200 → 211). A workaround for a tokenizer we are not using would have entered the serialisation schema for one we are |
| No tokens are added to the vocabulary | LoRA freezes embeddings by default. Unfreezing them costs about 16.8 GB of optimizer state and breaks standard export. This is the canonical first-timer error and we are avoiding it by construction |
| Unweighted loss, weights handled in population synthesis | The prefix contains the design strata, so sampling is conditionally ignorable. Weighted loss in an overparameterised network inflates gradient variance without moving the decision boundary |
| We do not rake our own output | Raking fixes margins and cannot fix joints. It is reserved for building the null we must beat, so we never benefit from the trick we are benchmarked against |
| Joint multi-country training, never sequential | Sequential adaptation costs 40 to 70 % on earlier countries. A country token is cheaper and does not forget |
| 🔴 **No forecast. The method is the contribution** | Author's decision, and `RL16` independently shows the data could not have carried a projection anyway. Papers 2 and 3 both ended in one, so dropping it feels like a loss and is not: attaching a weakly-supported forecast to a strong methodological claim hands a reviewer the easiest thing in the paper to attack |
| 🔴 **HETUS-only corpus, four countries, one wave each** | The paper tests paper 1's claim about **HETUS standardisation**, so the corpus is HETUS members: Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10. One wave each because `RL17`'s own inventory argues against two — three of the four second waves sit past the ACL 2000 break, which would force 2-digit codes and starve Step 9, and UK 2000-01's 15-minute slots are not admissible to a tally automaton built on multiples of 10. The set is exactly the HETUS 2010 round, so **Track A widens it from four countries to seventeen with no harmonisation change at all** |
| 🔴 **The hard null is the stated objective** | Announced in the introduction, not disclosed in the evaluation. A bar set in advance and then cleared is worth more than one chosen after the results are in, and this is the one place where the paper is genuinely falsifiable |
| Weights are withheld; synthetic data and code are released, and this is stated without apology | `RL10` finds no precedent for any statistical institute permitting weight release from restricted microdata, and reference-based MIA against a public base model is the specific attack that makes an adapter leaky. **A methods paper describes the method; that is what it is for.** Anyone with the same data licence can rebuild it from the paper and the code |
| Residential first, other channels later | Papers 2 and 3 spent their novelty budget on channel count. This paper spends it on countries |
| Held Italian data is the control, not a bonus | A new method that cannot reproduce paper 1's Italy result on paper 1's data has been demonstrated, not validated. **The Canadian GSS is no longer part of this paper**, so Italy carries the control on its own |
| Track B primary, Track A parallel — and Track A now matters more | With four countries, leave-one-country-out trains on three. That is thin, and the Eurostat 2010 Scientific Use File is the only route that widens it. It is still not on the critical path, but it is no longer a nice-to-have |
| The uninjected control runs first, always | 3J's most expensive lesson, unchanged |

---

## OPEN DECISIONS — 12 of 15 fully closed as of 2026-08-14

The list grew before it shrank, and that is the honest record. Decisions 1 and 3 closed; decision 9
partly reopened when the HETUS-only scope removed the ATUS reproduction path; **three genuinely new
items, 13, 14 and 15, appeared as consequences of decisions already taken**; **11 and 13 closed on
author calls**; and **15 closed the same evening when `RL20` came back negative.** None of 13, 14 or 15
was visible before `RL17`, the scope narrowing and `RL19`.

🔴 **Only decision 14 is genuinely open**, and `RL21` established that it **cannot be closed by
reading** — no published study has ever compared chaining rules on the same building, no standard
defines a protocol, and no citable threshold exists. It closes by our own experiment or not at all.

🟢 **AND IT DID, 2026-08-25 (night) — 15 OF 15 CLOSED.** `G7.18` ran in Step 8 on **9,000
EnergyPlus runs** and returned `FINDING 136`: the whole chaining axis moves peak demand
**0.178 / 0.075 / 0.239 %** against the pre-registered **25 %** trigger, with the seed spread inside a
rule beating the spread between rules on every metric in every fold. **The author ruled `independent`,
seed 1 as the standard convention, and the empirical null itself as the published deliverable.**
Ruling: §8 of `Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md`.
Decision 12 is deferred scope, not an open question.

✅ **Decision 15 was the one to watch, because it could quietly reverse decision 6. It did not.**
`RL20` established that the Sikt delivery carries only SSB's 167-category national list, with no ACL
variable and no official recode table anywhere in SSB or Sikt documentation. **Norway is rejected on
the same screen that rejected UK 2000-01**, the four-country corpus stands, and limitation C4 now has a
documented reason rather than an untested hope of repair.

| # | Decision | State | Settled by |
|---|---|---|---|
| 1 | **Corpus** | ✅ **FULLY CLOSED 2026-08-14.** **HETUS only, four countries, one wave each:** Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10. Canada and the United States are out of the paper. Earlier waves are held-out validation, never training. Track A runs in parallel and would widen the set to seventeen with no harmonisation change | `RL01`, `RL15`, `RL17` + author decisions 5 and 6 |
| 2 | **Method** | ✅ **CLOSED.** Fine-tuned LLM retained, scope narrowed to transfer. Rejected outright: in-context learning, RAG, discrete diffusion | `RL06` |
| 3 | **Model family, size, checkpoint** | ✅ **CLOSED 2026-08-14 by our own measurement, not by a report.** Primary backbone **`allenai/Olmo-3-1025-7B`** (200 tokens per diary against Qwen's 303, Apache 2.0, native vLLM kernel, 65,536 context, ungated, 7.30 B). `Qwen/Qwen2.5-7B` retained as the named comparison arm. ✅ **Pilot size also closed 2026-08-14 by the author: `allenai/OLMo-2-0425-1B` is Leg-4, `allenai/Olmo-3-1025-7B` is Leg-5.** Series numbering continues from 3J, which ended at Leg-3 | Speed jobs `1234177`, `1234192`, `1234199`, `1234211`, `1234216`, `1234219` + author |
| 4 | **Full FT or PEFT** | ✅ **CLOSED.** rsLoRA r=32 all-linear primary; full FT with 8-bit AdamW as the ceiling run; QLoRA rejected | `RL05` |
| 5 | **Serialisation format** | ✅ **CLOSED.** Episode form, no added tokens. Field semantics corrected to real HETUS codes | `RL07` + `RL02` |
| 6 | **Survey weights** | ✅ **CLOSED.** Unweighted loss, two-stage IPF, no post-hoc raking of our output | `RL09` |
| 7 | **Gate thresholds** | ✅ **CLOSED.** Set above, provenance corrected in three rows, two new privacy gates added | `RL08` + `RL10` |
| 8 | **Is a forecast defensible** | ✅ **CLOSED, and then removed entirely.** `RL16` said no. The author then took it **out of scope** on 2026-08-14: no projection, no scenario levers, no year token. The method is the contribution | `RL16` + author |
| 9 | **What we may release** | ✅ **CLOSED on the artefacts:** synthetic dataset (CC BY 4.0, Parquet, Zenodo + Hugging Face) plus code (Apache 2.0). **Weights withheld, stated plainly, not apologised for.** ✅ **The reproduction path reopened when the HETUS-only decision removed the ATUS stand-in, and closed again the same day as decision 13: two tiers, Spain alone and Spain plus UK** | `RL10` (overriding `RL04` and `RL15`) + author |
| 13 | **What replaces the ATUS reproduction path** | ✅ **CLOSED 2026-08-14 by the author. Two tiers.** **Tier 1: Spain 2009-10 alone**, INE open download, no credentials, every stage executable end to end but **not transfer**, since one country cannot demonstrate it. **Tier 2: Spain + UK 2014-15**, two free registrations, which is the cheapest pair that can execute a real leave-one-country-out against the reweighted null. 🔴 Tier 1 cannot exercise any persistence-dependent chaining rule, because Spain fields **one diary day per respondent**. The UK pairing is the manager's implementation of the author's call, not the author's own selection | Author |
| 14 | 🔴 **The day-to-year chaining rule — THE ONLY DECISION STILL OPEN** | **OPEN**, from `RL17` Part D, and **`RL21` changed its shape without closing it.** ✅ `RL21` answered the commissioning question with **zero**: no published study compares two or more chaining rules on the same building with the daily generator held fixed, no ASHRAE/ISO/IBPSA document defines a protocol, IEA EBC Annex 66 and 79 are silent, and **no citable threshold exists** for when a convention dominates a result — so the 25 % figure is permanently project-chosen. 🔴 **It therefore cannot close by citation; it closes by our own experiment or not at all.** 🔴 **Every percentage in `RL21` is rejected**, including its headline 15-35 % peak divergence, which contradicts its own zero-studies finding. One accepted finding changes the design: a two-day survey of 1 weekday + 1 weekend **cannot identify consecutive-day transitions**, so the habit-coupled rule is run as a **sweep over the persistence parameter**, not as a fitted rule. Must close before the Step 8 campaign is designed | `RL21`, vetted V13-V14 |
| 15 | **Norway as a fifth country** | ✅ **CLOSED 2026-08-14. NO.** Opened by the author after `RL19` and closed the same day by `RL20`. Norway passes on slot length (10 minutes, 2 diary days, ages 9-79, paper diary) and is the only reachable Nordic candidate, **but it fails screen B2 outright**: the Sikt delivery carries only SSB's **167-category national list**, no ACL variable at any depth, and **`NOT FOUND` for any official recode table** in SSB publications, the SSB `Klass` database or the Sikt metadata. `RL19`'s recode claim is formally retracted; no published third-party crosswalk exists either. **Rejected on the same screen as UK 2000-01.** The four-country corpus stands | `RL20`, vetted V12 |
| 10 | **Venue** | ✅ **CLOSED.** *Energy and Buildings* primary, *Building and Environment* co-equal secondary, framed on transfer. Optional paired data descriptor | `RL14` |
| 11 | **Which country is held out** | ✅ **CLOSED 2026-08-14 by the author: none of them, and all of them.** **Four-fold rotation** — every country held out in turn, four leave-one-country-out runs rather than one. The hazard was never which country was picked but that a picked country can be picked late; **rotation leaves nothing to pick.** 🔴 Two pre-registered conditions travel with it: **all four folds are reported, including the worst**, and **no fold's result may change the design once any fold has been evaluated.** Cost: four Leg-5 runs instead of one, accepted. A random household hold-out inside the training countries is retained as an ordinary test set and **is never reported as transfer** | Author |
| 12 | **Household-joint generation** | 🔴 **STILL OPEN.** Now known to be *feasible*: a 4-person household week is about 7,000 tokens, well inside context. Deferred as scope, not excluded as impossible | `RL07` |

---

## LIMITATIONS — updated

| # | Limitation | Status after the reports |
|---|---|---|
| **A1** | Inherits every coverage and non-response bias of the source surveys | **Now carries a number.** HETUS unit non-response runs 30 to 65 % across member states, plus 10 to 25 % diary non-response. Not correctable by post-stratification |
| **A2** | One or two diary days per respondent, so multi-day dependence is largely unobservable | **Partly relieved.** The standard design is two linked days, one weekday and one weekend, which supports intra-person day-to-day structure. **But Spain and 1998 France fielded a single day**, so this is country-dependent |
| **A3** | Hotel guests, institutional populations and the homeless are outside the frame | Unchanged |
| **B1** | A pretrained model's world knowledge is not uniform across countries | **Now evidenced and it runs against us.** Cultural benchmarks show open-weight models are weakest on exactly the peripheral European countries a transfer claim is most interesting for. Pre-registered as a confound: **transfer is claimed as schema-guided statistical transfer, not as retrieved world knowledge** |
| **B2** | Transfer is scored against aggregates only | Unchanged, and now load-bearing since Track B countries have microdata but the widened Track A set may not |
| **C1** | ~~Two waves is not a trend~~ | 🔴 **No longer a limitation, because there is no longer a temporal claim.** Forecasting is out of scope by decision. The waves are training data and a possible second held-out axis. Nothing in the paper extrapolates, so nothing needs defending |
| **C2** | ~~The most recent waves straddle the pandemic, unevenly by country~~ | 🔴 **No longer a limitation, because those waves are not in the corpus.** All four training waves are pre-pandemic paper self-completion diaries. The COVID-era and app-era waves were the ones decision 6 discarded |
| 🔴 ~~**C3**~~ | ~~**Pooling waves may teach the model that instrument changes are behaviour changes**~~ | 🔴 **REMOVED on 2026-08-14, because the pooling it described no longer happens.** One wave per country means one collection mode, one slot length and one coding-list generation. **Removing a limitation by removing the practice it constrained is legitimate**, the same move that removed C1. It is struck through rather than deleted so the reasoning stays visible |
| 🔴 **C4** | 🔴 **REWRITTEN 2026-08-15: the corpus is THREE countries — Italy, Spain, the UK — all Western or Southern European, and leave-one-country-out trains on TWO.** France was excluded by decision 16 because its delivery had no arrival date, and **the paper states that as a scheduling decision, not as a design choice** — nothing about France failed a screen. The superseded four-country text follows | *(superseded)* **The corpus is four countries, and they are all Western or Southern European** | **NEW, and it is the cost of the HETUS-only decision.** Leave-one-country-out trains on three, and Italy, Spain, France and the UK are not a demanding spread — a reviewer can fairly ask whether transfer across four neighbours demonstrates transfer across a framework. **Track A is the only thing that fixes it**, and until it lands the claim is stated at the scale the corpus supports. 🔴 **Tested twice and it held.** `RL19` found no Tier 0 or Tier 1 national route among the 14 remaining countries; `RL20` then tested the single best candidate, Norway, and found no ACL-coded file and no official recode. **The limitation is not a gap we have failed to close, it is a property of what is distributed** |
| **D1** | Constrained decoding renormalises over allowed tokens, which is not neutral | Unchanged. Reported via the constraint-firing rate and audited against an unconstrained rejection-sampled batch |
| **D2** | Post-hoc raking would fix marginals while weakening the claim | **Resolved into a rule:** we do not rake our output at all |
| **E1** | Any activity-to-load mapping may itself be unvalidated | **Sharpened.** The published mappings validate at aggregate scale (100 to 500 dwellings), not per dwelling. The downstream claim is therefore about load shapes and distributions |
| **E2** | Reproducibility is statistical, not bit-exact | Unchanged. Floating-point non-associativity in parallel GPU reductions makes cross-platform bit-exactness impossible; the deposited synthetic dataset is the immutable record |
| **F1** | We do not release the trained model | **From `RL10`, and accepted by decision rather than regretted.** Readers cannot re-run our exact generator. They can rebuild it: the method is described in full, the code is released, and the synthetic output is released. 🔴 **The fourth leg of that answer — a pipeline anyone could run with no credentials — was ATUS, and it left with the HETUS-only decision.** ✅ **Replaced by decision 13: Spain alone with no credentials, and Spain plus UK with two free registrations for the transfer machinery.** Neither tier restores what Track C had, which was zero-credential *and* able to demonstrate the claim |
| 🔴 **F2** | **We build the European archetype models ourselves** | **NEW, from `RL13`.** No official European EnergyPlus archetype library exists, so the envelope models are our construction from TABULA parameters and inherit that uncertainty |
| 🔴 **F3** | **Concordia is not yet a Eurostat recognised research entity** | **NEW, from `RL01`.** The widest version of the corpus depends on an institutional application that has not been filed |

---

## COMPANION DOCUMENTS

| Document | What it holds |
|---|---|
| `4thJ_00_HETUS_LLM_Pipeline.md` | The step-by-step detail behind every box above, the report-vetting record, and the Progress Log |
| **`Step0_docs/` to `Step11_docs/`** | **The per-step working documents, created 2026-08-14 (`Step10_docs/` and `Step11_docs/` added 2026-08-26), following the 3J `Leg3_4-split` convention.** Each folder holds an **implementation** specification (`4thJ_0N_<name>.md`) and a **validation** specification (`4thJ_0N_<name>_val.md`), plus an `outputs_stepN/` directory. The implementation doc carries the aim, the decisions already fixed, the numbered work items with a definition of done, the interfaces, and an append-only Progress Log. The validation doc carries the gates with thresholds and provenance, the perturbation table (**every gate must be seen failing, and each perturbation must break exactly one gate**), the coverage clause, the vacuity guards, and an explicit statement of what that step's validation does **not** cover |
| `DeepResearchPrompts/README.md` | The 16 `L`-series prompts, their run order, and the vetting procedure |
| `DeepResearchPrompts/RL01` to `RL16` | The sixteen returned reports, all present as of 2026-08-14 |
| `DeepResearchPrompts/L17` + `RL17_contradiction_adjudication_and_multiwave.md` | **The adjudication round, run and returned.** Settles the eight inter-report contradictions and inventories the waves. Its two `NOT FOUND` verdicts (A6, A7) are the most useful thing in it, and **its wave inventory is what argued the author out of its own two-wave recommendation** |
| `DeepResearchPrompts/L18` + `RL18_model_family_final_selection.md` | **The model-family round, run and returned — and overturned by measurement.** Recommended `Qwen2.5-7B` on a mis-counted token figure and a licence clause that does not exist in Llama 3.1. Read the status section above before using anything from it |
| `DeepResearchPrompts/L19` + `RL19_corpus_expansion_national_routes.md` | **The corpus-expansion round, run and returned — accepted for its landscape, rejected for its recommendation.** Establishes that no national route reaches a Tier 0 or Tier 1 country and that **no national archive ships the Eurostat-harmonised file.** Its Netherlands entry and its convenience control both failed vetting. See V9 to V11 |
| `DeepResearchPrompts/L20` + `RL20_norway_admissibility.md` | **The Norway round, run and returned. Closed decision 15 as NO.** One question, one clean negative: the Sikt delivery carries only SSB's 167-category national list, with no ACL variable and no official recode table. Retracts `RL19`'s recode claim and corrects the Vaage 2012 citation. Its Part E was quoted from our own prompt. See V12 |
| `DeepResearchPrompts/L21` + `RL21_day_to_year_chaining.md` | **The chaining round, run and returned. Did not close decision 14 and proved nothing else can.** Zero published studies compare chaining rules on the same building; no standard, no citable threshold. 🔴 **Every percentage in it is rejected**, including a headline that contradicts its own zero-studies finding. See V13 and V14 |
| `tools/4thJ_tok_measure.py`, `4thJ_olmo_check.py`, `4thJ_olmo3_measure.py`, `4thJ_license_check.py`, `4thJ_final_checks.py`, `4thJ_llama_clause.py` (+ `.sh`) | **The measurement that closed decision 3.** Six CPU sbatch jobs on Speed: tokenizers, configs, the vLLM registry source, licence metadata, licence text. Every number in the status section comes from these and the logs are on `/speed-scratch/o_iseri/` |
| **`Step10_docs/` + `Step11_docs/`** | **Added 2026-08-26. The OpenUBEM extension, registered as new steps rather than as edits to Steps 8 and 9.** Step 10 re-tests the occupancy hypothesis on observed building stock with an **independent diary per dwelling**; Step 11 runs Step 9's mapping unchanged at real neighbourhood scale. 🔴 They open **new `G10.x` / `G11.x` gate series** and state their inheritance per gate, because `4thJ_08_bemSimulation_IMP.md` §8 and the engine's own MVP both already score a suite called `G8.0`–`G8.16` on a different basis — two documents claiming one ID on two bases is how a basis change hides as a fix |
| `DeepResearchPrompts/L28`, `L29` | **The two Step 10 rounds, authored 2026-08-26, not yet run.** `L28` asks whether the peak effect scales with the number of independently diarised dwellings, and whether our conserved-mean null already has company in the literature; `L29` asks how non-convex and courtyard footprints are subdivided, and what the one-zone-per-floor fallback costs. ⚪ A DHW round was deliberately **not** written: `RL25` §B10 already carries the Jordan & Vajen figures `G9.7` needs, and the next move is to vet them against the source table |
| `writing/submission/figures/Prompts_Images/4thJ_graphical_abstract.md` | The prompt from which the author generates the graphical abstract |

> **Graphical abstract.** Not yet generated. The prompt has been **updated on 2026-08-14** to match the
> decided pipeline: the two-stage population-then-diary structure now appears, the episode tuple lost
> its `start` field, and the held-out lane now shows what it is scored against. The author generates the
> image, as in papers 2 and 3.
