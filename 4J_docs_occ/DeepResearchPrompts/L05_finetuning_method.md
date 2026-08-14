# L05. Fine-tuning method: continued pretraining versus instruction tuning, full versus PEFT, and the recipe that actually works for structured generation

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and E are the deliverable. `L06` asks whether to fine-tune at all; **this prompt assumes
we do, and asks how.**

## Why we are asking

The author has never fine-tuned a language model. Every previous model in this project series was a
small Transformer trained from scratch with a hand-written PyTorch loop. The vocabulary of the
fine-tuning world (LoRA rank, adapter merging, packing, masking the prompt, chat templates, gradient
checkpointing) is entirely new here, and the failure modes are not obvious from the outside.

We need a **defensible recipe with cited justification for every choice**, because the method section
of the paper will be read by building-science reviewers who will not know this field either, and by at
least one machine-learning reviewer who will.

## What we need

### Item 1. The framing question: what kind of fine-tuning is this?

Our task: given a demographic and contextual conditioning vector, emit a full-day sequence of activity,
location and co-presence codes that is structurally valid and distributionally faithful.

Three framings are possible and we do not know which the literature supports:

1. **Continued pretraining** on serialised diaries as raw text, then conditional generation by prefix.
2. **Supervised fine-tuning** on `(conditioning prompt, diary completion)` pairs, with the loss masked
   to the completion only.
3. **Instruction tuning** on a chat-formatted version of the same pairs.

For each: what it is, what evidence supports it for structured non-natural-language sequence
generation, and what it costs. **State which one you would choose and why.** Address specifically
whether loss masking of the prompt helps or hurts when the "prompt" is a short structured conditioning
vector rather than a natural-language instruction, and cite evidence rather than asserting.

Also address: **should we start from the base checkpoint or the instruction-tuned checkpoint?** There
is a real argument each way and we want the argument, with citations, not a preference.

### Item 2. PEFT choices, with evidence not folklore

1. **LoRA**: what the current evidence says about choosing rank and alpha, which modules to target
   (attention projections only, versus attention plus MLP, versus all linear layers), and whether
   targeting all linear layers is now the default recommendation. Give the source of each claim.
2. **QLoRA**: what quality cost, if any, current evidence attributes to 4-bit base weights during
   fine-tuning. Is the "no measurable degradation" claim still supported by independent evaluation, or
   has it been qualified since?
3. **DoRA, rsLoRA, LoRA+, and any successor** that has independent evidence behind it. Which of these
   are worth the complexity, and which are noise? Be willing to say that a technique is not worth it.
4. **Full fine-tuning**: at what model scale does it become both feasible on one 80 GB GPU and
   preferable? Is there evidence that full fine-tuning materially beats LoRA when the target
   distribution is far from the pretraining distribution, which our serialised survey records certainly
   are? This is the crux: our data does not look like text, so the usual "LoRA is enough" evidence,
   which is mostly gathered on natural-language tasks, may not transfer.

### Item 3. The recipe, concretely

Give a starting configuration we could run, with a citation or a stated rationale for each value:

* Learning rate and schedule, and how they should differ between full fine-tuning and LoRA.
* Warmup, batch size, gradient accumulation, and the effective batch size to target.
* Number of epochs, and how to detect the point where the model starts memorising individual diaries.
  This is not only an overfitting concern for us, it is a **disclosure** concern (`L10`).
* Sequence packing: should multiple diaries be packed into one training sequence, and what does packing
  do to the boundary between records? If packing risks the model learning to run one diary into the
  next, say so and give the mitigation.
* Precision: bf16 versus fp16 versus mixed, and what to do on a V100 which lacks bf16.
* Optimiser, including whether a paged or 8-bit optimiser is needed at our scale.
* Gradient checkpointing, flash or memory-efficient attention, and their interaction with the model
  families shortlisted in `L04`.

### Item 4. The failure modes a first-timer will hit

This is the item we most want. Name the specific, documented failure modes, what they look like in the
logs or the outputs, and the fix:

1. Loss going to a low value while outputs are degenerate.
2. The model emitting the correct format but a collapsed distribution: every generated person does the
  same thing. This is the failure that would silently destroy our paper, because our metrics are
  distributional. See `L08`.
3. Catastrophic forgetting of the format when we later fine-tune on a second country.
4. Chat-template mismatch between training and inference, which silently degrades everything.
5. Tokenizer or special-token mismatch after adding tokens (`L07`).
6. Padding and attention-mask errors that train on padding.
7. Adapter merge changing behaviour relative to the unmerged adapter.
8. Anything else that is well documented and bites beginners.

For each, say **how we would detect it before it costs us a week on a shared cluster**.

### Item 5. Progressive and multi-country fine-tuning

Our previous paper fine-tuned progressively across survey cycles (2005 to 2010 to 2015 to 2022), each
stage initialised from the last, which let us forecast forward. We want to know whether the same
strategy is sound for an LLM, because we intend to do two things:

1. Fine-tune across **countries**, and
2. Fine-tune across **survey waves in time**, so the model can be pushed to a future year.

Address: does sequential fine-tuning cause forgetting of earlier countries or waves, what is the
measured severity, and what are the mitigations (mixing a replay buffer, separate adapters per country
with a shared base, adapter composition or merging, a country token in the conditioning). **Is
per-country LoRA with a shared base a better design than one model trained on everything?** Give the
evidence, and name what each design costs at inference time when we need to generate millions of
diaries.

### Item 6. Reproducibility and reporting

What does a 2026 reviewer expect to see reported for a fine-tuning experiment? Seeds, exact library
versions, hardware, wall-clock, energy or carbon if the venue asks, hyperparameter search protocol,
and the number of runs behind each reported number. Point at a checklist or a venue policy if one
exists.

## Named leads

The original LoRA and QLoRA papers and their independent replications; the `peft`, `trl` and
`transformers` documentation, with versions; the `unsloth` and `axolotl` project documentation for
practical recipes, treated as Tier 3 and checked against Tier 1 where they make quality claims;
published surveys of parameter-efficient fine-tuning from 2024 to 2026; the continual-learning
literature for the forgetting question in item 5.

## Hard constraints specific to this prompt

* **Every hyperparameter you recommend must carry a reason.** "Commonly used" is not a reason. If the
  honest reason is that it is a widely adopted default with no strong evidence behind it, write exactly
  that; it is useful and we will report it as such.
* **Do not recommend a technique whose only evidence is a blog post that reports no baseline.** Mark
  such techniques `UNSUPPORTED CLAIM` and move on.
* **Do not assume our data looks like natural language.** It does not. Flag every recommendation whose
  supporting evidence comes only from natural-language tasks, because that is the main way this answer
  could mislead us.
* Nothing multi-node. Nothing over seven days per job.

## Deliverable

**Section B** is the evidence table behind the choices.

**Section C** is the recommended recipe as a single configuration block we could hand to an engineer.

**Section D** is the feasibility check on one A100 80 GB.

**Section G** is the failure-mode catalogue from item 4, which we will turn into pre-registered
diagnostic checks, and your negative controls.
