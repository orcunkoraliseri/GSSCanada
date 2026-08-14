# L04. Which open-weight LLM: what actually exists today, at what sizes, under what licence, with what multilingual coverage

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and F are the deliverable. **Every row needs a `Date checked`.**

## Why we are asking

The author has named **Gemma** as a candidate and referred to a version number that we are not
confident exists. **Do not confirm a version because this prompt or the author mentioned it.** Report
what is actually released, downloadable, and licensed today, and say plainly if the named version does
not exist.

We need to choose one model family and one size to build a year of work on. Getting this wrong is
expensive but recoverable; getting the **licence** wrong is not, because it could prevent us from
publishing the fine-tuned weights, which is a large part of the paper's value.

## Our constraints, restated so your recommendation is usable

* Training hardware: a shared SLURM cluster. The best GPU we can request is **one NVIDIA A100 80 GB**
  (available as a full-GPU MIG profile), with 20 GB A100 slices, 48 GB RTX 6000 cards, and 32 GB V100
  cards as the alternatives. **Single node, single GPU, seven-day maximum walltime.** No multi-node
  training. Verified on our cluster on 2026-08-13.
* Budget for commercial API access or rented cloud GPUs: **zero**.
* The training corpus will be **structured survey records serialised to text**, on the order of
  hundreds of thousands of short sequences, not a web-scale corpus.
* Inference will need to generate **millions** of diaries to populate an urban model, so tokens per
  diary and generation throughput are first-class selection criteria, not afterthoughts.
* The output must be **structurally constrained** (see `L15`), so support in the constrained-decoding
  and serving ecosystem matters.
* Some of the training data may be **restricted-access microdata** (see `L01`, `L10`), so the licence
  must permit training on private data and, ideally, releasing an adapter without releasing the data.

## What we need

### Item 1. The current open-weight landscape, as a table we can choose from

One row per model family and size that is **actually downloadable today**. Cover at minimum the Gemma,
Qwen, Llama, Mistral, Phi and OLMo families, plus anything else that belongs. For each row:

1. Exact model identifier as published (the repository name, not a marketing name).
2. Parameter count, and whether a base (pretrained) checkpoint is released or only an
   instruction-tuned one. **We probably want the base checkpoint**, because we are teaching a new
   output format rather than a new instruction-following behaviour, so mark this column carefully.
3. Release date, and whether the family has been superseded.
4. Native context length, and the attention or positional scheme, since our sequences are long and
   highly repetitive.
5. Vocabulary size and tokenizer type. This drives `L07` directly.
6. Whether the weights are dense or mixture-of-experts, and if MoE, the active parameter count, because
   that changes the memory arithmetic completely.
7. Precision the weights are released in.

### Item 2. Licences, read properly

For each family, do not just write the licence name. Answer these questions from the licence text:

1. Is **commercial use** permitted, and is **academic research use** unambiguously permitted?
2. May we **publish the fine-tuned weights or a LoRA adapter**, and under what conditions? Name any
   requirement to propagate the licence, to preserve a use policy, or to name the base model.
3. Does the licence contain a **use-restriction annex** or acceptable-use policy that is incorporated by
   reference, and does anything in it plausibly bear on generating synthetic representations of people
   from survey data?
4. Is there any restriction on **using outputs to train other models**? We may want to distil.
5. Is the **tokenizer** under the same licence as the weights? This has caught people out.
6. For each family, name the specific licence document and its URL, and quote the clause you relied on
   for questions 1 and 2. A one-word answer of "permissive" is not usable to us.

### Item 3. Multilingual and cross-national coverage

Our data spans many European countries. Two different things matter and they are often conflated:

1. **Language coverage.** Do we even need it? Our serialisation may be entirely numeric and English-
   keyed, in which case multilingual capability is irrelevant and we should not pay for it. State the
   argument both ways.
2. **World knowledge about the countries.** Whether the model plausibly encodes anything about daily
   life in, say, Bulgaria versus Finland is the mechanism by which cross-national transfer could beat a
   from-scratch model. Is there any published evaluation of **cultural or country-level knowledge
   asymmetry** in these model families? Benchmarks that measure Western or Anglophone bias in world
   knowledge would be directly relevant. If the asymmetry is large, that is a limitation we must
   pre-register, because it would mean the model transfers better to countries it knows more about,
   which is exactly the wrong direction for our claim.

### Item 4. The small-model question, asked seriously

We suspect the right answer may be a **small** model, in the 1 to 8 billion parameter range, rather
than the largest thing that fits.

1. Is there evidence on the relationship between model scale and performance for **structured
   generation and format-following after fine-tuning**, as opposed to general reasoning? Our task
   requires almost no reasoning and a great deal of exact format adherence.
2. At what scale, if any, does the pretrained prior start contributing useful knowledge about human
   daily routines, rather than just providing a well-initialised sequence model?
3. Is there a published result showing a small fine-tuned model matching a large one on a narrow
   structured-generation task? If yes, cite it precisely, because it would justify our whole compute
   plan.
4. State plainly what we would lose by choosing 4B over 27B.

### Item 5. Memory arithmetic, per candidate, on our actual GPU

For the three or four candidates you would shortlist, give the arithmetic for **one A100 80 GB**:

| Model | Full fine-tune feasible? | LoRA in bf16 feasible? | QLoRA 4-bit feasible? | Estimated peak VRAM at sequence length 2048, batch 1, with gradient checkpointing | Assumptions |

Show the calculation, do not just assert the number. State every assumption: optimiser state,
gradient accumulation, activation checkpointing, attention implementation, and the sequence length you
assumed. If a configuration does not fit, say so; we would much rather be told a 27B full fine-tune is
impossible than discover it in a failed job.

Then repeat the feasibility column only, for a **48 GB RTX 6000** and a **32 GB V100**, since those are
our fallback queues. Note explicitly if a card lacks bfloat16 support, because that changes the recipe.

### Item 6. Practical ecosystem readiness

For each shortlisted model: is it supported today, and at which library version, by

1. Hugging Face `transformers` and `peft`,
2. a fine-tuning stack we could run offline on a cluster with no internet from the compute node,
3. at least one constrained-decoding or structured-output library (see `L15`),
4. a high-throughput inference engine for the generation phase.

Name versions. A model that is two weeks old and not yet supported by the stack is a bad choice for us
regardless of its benchmark scores.

## Named leads

The model developers' own model cards and technical reports; the licence texts themselves rather than
summaries of them; Hugging Face model repository pages for release dates and availability; the
`transformers`, `peft`, `trl`, `bitsandbytes`, `vllm` and `llama.cpp` release notes and documentation
for support matrices; published multilingual and cultural-knowledge benchmark papers.

## Hard constraints specific to this prompt

* **Do not report a model that you have not confirmed has downloadable weights.** An announcement, a
  blog post, a benchmark table or a waitlist is not a release. Mark each row `WEIGHTS CONFIRMED` or
  `ANNOUNCEMENT ONLY`.
* **Do not paraphrase a licence.** Quote the operative sentence and give its section number.
* **Do not recommend anything requiring more than one GPU or more than seven days.**
* Do not recommend a hosted API, under any framing, including "just for the baseline".
* If the model version the author named does not exist, say so in the first sentence of Section A,
  without softening it.

## Deliverable

**Section B** is the landscape table from item 1 plus the licence answers from item 2.

**Section D** is the memory arithmetic from item 5.

**Section C** carries your single recommendation: one family, one size, one checkpoint type, with the
three strongest reasons and the one strongest reason against.

**Section G** carries the multilingual asymmetry evidence, the small-model evidence, and your negative
controls.
