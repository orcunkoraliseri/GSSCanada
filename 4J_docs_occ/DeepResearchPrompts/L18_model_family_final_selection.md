# L18. The final model-family decision, re-asked under the constraints we did not have when L04 was written

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections B, C and D are the deliverable. **Every row needs a `Date checked`.**

---

## What this prompt is

`L04` asked which open-weight model to use. Its answer (`RL04`) is now unusable, not because it was
badly researched, but because **three of the four constraints it optimised for have changed**, and one
of its central factual claims was overturned by `RL17`. This prompt asks the same decision again, with
the real constraints, and it is the prompt that closes the decision. There will not be a third round.

🔴 **Do not treat `RL04` as a starting point.** If your recommendation lands on the same model that
`RL04` recommended, say explicitly which **new** evidence supports it, because agreement with a report
written under superseded constraints is not confirmation.

---

## What changed since L04, stated so your recommendation is usable

**1. We will not publish the model.** `RL10` established that the Eurostat and Statistics Canada
microdata agreements forbid releasing weights or adapters trained on the licensed microdata. This is
**settled and accepted, and it is not to be re-opened or worked around.** Every licence question in
`L04` about publishing fine-tuned weights is therefore dead. A completely different licence question
takes its place, and it is Part B of this prompt.

**2. What we DO publish is the model's output.** The releasable artefacts are: a synthetic diary
dataset intended for **CC BY 4.0** on Zenodo and Hugging Face, the training and generation code under
Apache 2.0, and a fully public stand-in pipeline. **The output, not the model, is the artefact.** So
the operative licence question is what each model's licence permits us to do with **generated text**.

**3. Compute is not the binding constraint we assumed.** We have confirmed access to a **full NVIDIA
A100 80 GB** (MIG profile `nvidia_a100_7g.80gb`, one per node on `speed-37` and `speed-39` to
`speed-43`, partitions `ps`, `pt`, `cl`), single node, single GPU, seven-day walltime, verified by our
own `sinfo` query on 2026-08-13. `L04` was answered as though we were scraping for the smallest thing
that fits. We are not. **A 7B model is no longer chosen by necessity, and the question of whether we
should go larger is genuinely open.** Still: single node, one GPU, seven days, and **zero budget** for
API access or rented cloud. Fallback queues are 48 GB RTX 6000 and 32 GB V100 (no bf16 on the V100s,
and 16 GB Tesla P6 cards that are useless to us).

**4. The token-efficiency argument that `RL17` decided on has been weakened by our own serialisation
choice.** We adopted an **episode** serialisation, `DUR,ACT,LOC,COP` per episode with no start time,
which we measured at **196 to 326 tokens per diary** against 924 to 1310 for a 144-slot compact form.
`RL17` measured that `meta-llama/Llama-3.1-8B` writes a three-digit activity code as **one** token
while Qwen2.5, Gemma 2 and Mistral NeMo use three and Mistral 7B v0.3 uses four, and recommended Llama
on that basis. Under the episode form a diary holds on the order of twenty to forty episodes, so the
difference is roughly sixty extra tokens on a few hundred, which is **irrelevant to context length**.
It may still matter to **generation throughput**, because we must generate millions of diaries. Part D
asks you to settle which of those two framings is the real one.

**5. The author's standing question, which you must answer directly and are free to answer with "no".**
The author has understood that Google's open models are small compared with the alternatives, and has
again referred to a **Gemma version number we are not confident exists**. Report what Google actually
ships today, at what sizes, and **state plainly in the first sentence of Section A whether the named
version exists**. Do not confirm a version because this prompt or the author mentioned it.

---

# PART A. The landscape as it actually stands on your check date

One row per model family and size with **weights downloadable today**. Mark every row `WEIGHTS
CONFIRMED` or `ANNOUNCEMENT ONLY`, and do not report a row you have not confirmed resolves to a real
repository. Cover at minimum the Google (Gemma and any successor line), Qwen, Llama, Mistral, Phi, OLMo
and DeepSeek families, plus anything released since that belongs on the list.

| Model repository id | Params (and active params if MoE) | Base checkpoint released? | Release date | Superseded? | Context length | Vocab size and tokenizer type | Weight precision | Licence | Status |

Three columns need care:

* **Base checkpoint released?** We want the **pretrained base**, not the instruction-tuned variant,
  because we are teaching an output format rather than an instruction-following behaviour. Several
  recent families ship instruct-only. A family with no base checkpoint is a materially worse fit for us
  and must be marked as such, not quietly listed.
* **MoE.** If the weights are mixture-of-experts, give total and active parameters. This changes the
  memory arithmetic completely and it changes whether the model fits our single GPU at all.
* **Superseded.** Version rot is the specific failure mode of this series. A family superseded two
  months ago is a bad choice regardless of its benchmarks.

Then answer, in plain sentences:

**A1.** What is the complete current Google open-weight lineup, at what parameter sizes, with what
licence, and does the version the author named exist? If the largest Google open model is smaller than
the largest Qwen or Llama open model, say by how much. If it is not smaller, say that too, because the
author's premise would then be wrong and we would rather know.

**A2.** Which families ship a **base** checkpoint in the 7B to 32B range today?

**A3.** Has anything been released since 2026-05 that would change this decision and that a report
written earlier could not have known about?

---

# PART B. The licence question we actually have, which is not the one L04 asked

This is the most important part of this prompt. **Do not paraphrase a licence. Quote the operative
sentence and give its section number and the URL of the document you quoted.**

We are **not** distributing weights. We **are** distributing, under CC BY 4.0, a dataset of synthetic
human daily activity diaries that the fine-tuned model generated. For each candidate family, answer:

**B1. Output ownership and restrictions.** Does the licence assert any claim, restriction or condition
on **the text the model generates**? Quote the clause. Does it survive after we stop distributing the
model, that is, does it attach to the output itself or only to the weights?

**B2. The improve-another-model clause.** Meta's Llama community licences contain a restriction on
using Llama outputs to improve any other large language model. **Quote it exactly, for the specific
version you are reporting on, with its clause number.** Then answer the operative question for us:
**if we publish generated diaries under CC BY 4.0, a licence which permits any downstream use including
training other models, are we in breach?** We believe we are, and that this alone disqualifies Llama.
Tell us if we are wrong, and if we are right, say whether the same clause appears in any other family's
licence. Check Gemma's terms and prohibited-use policy for an equivalent, since Gemma's terms are also
not a standard open-source licence.

**B3. Propagation.** For each family, does the licence require that any restriction, use policy or
naming requirement be **passed through to recipients of derivative material**, and does "derivative
material" as defined include generated output? A licence that forces us to attach a use policy to the
diary dataset is incompatible with CC BY 4.0 and must be flagged as such.

**B4. Training on restricted microdata.** Does anything in the licence bear on **training on
confidential or licensed third-party data**, for example a clause requiring disclosure of training
data, or an acceptable-use annex touching the generation of synthetic representations of real people
from survey records? We are generating synthetic humans from national statistical microdata and we
would rather find the awkward clause now.

**B5. The tokenizer.** Is the tokenizer released under the same licence as the weights, for each
family? This has caught people out before.

**B6. The verdict table.** Close Part B with one table, and it is the single most useful thing you can
give us:

| Family | May we fine-tune on licensed microdata we cannot share? | May we publish the generated diaries under CC BY 4.0 with no conditions attached? | Clause relied on | Compatible with our release plan: YES / NO / UNCLEAR |

`UNCLEAR` is an acceptable and useful answer. An invented `YES` costs us the artefact that is the
paper's only public deliverable.

---

# PART C. Size, and the staged design we intend to use

🔴 **Read this before answering any of Part C, because it changes what the size question is.**

We do not intend to pick one size and build a year of work on it. We intend to run the project in
**two legs**, the way we ran the previous paper (a two-way split first, then the four-way split it
prepared for):

* **Leg 1, a pilot on the smallest model that can plausibly do the task at all.** Its purpose is to
  exercise the entire pipeline end to end: parser, serialisation, fine-tuning, grammar-constrained
  decoding, every validation gate including the three deliberately broken negative controls, and the
  EnergyPlus coupling. It is a rehearsal of the plumbing, and it pays off whatever it scores.
* **Leg 2, the model we actually report**, run only once Leg 1 has proven the pipeline.

So the question is **not** "7B or 30B". It is **three** questions, and we want all three answered
separately:

**C0a.** What is the **smallest model with a released base checkpoint** that can plausibly learn this
task at all? Name candidates below roughly 4B, including the small members of the families in Part A
(0.5B, 1B, 1.5B, 3B, 4B tiers). For each: base checkpoint yes or no, licence, tokenizer behaviour, and
whether the current `vLLM` plus `XGrammar` stack supports it. A tiny model that cannot be
grammar-constrained is useless to us as a pilot, because constrained decoding is one of the things the
pilot exists to test.

**C0b.** 🔴 **Does a pilot at 0.5B to 4B actually predict anything about the same pipeline at 7B to
30B, or only about the plumbing?** Be careful and be honest here, because this is the question we most
need answered correctly. Address separately:

1. Is the **ranking** of design choices (serialisation format, LoRA rank, prompt structure, constraint
   set) preserved across model scale? Is there published evidence either way? If small-scale ablations
   do not predict large-scale ablation rankings, then our pilot can validate the code but must not be
   used to choose the recipe, and we need to know that before we trust a pilot result.
2. Do **evaluation gates** calibrated on a small model transfer? Specifically the distribution-collapse
   gate: a small model may collapse for reasons of capacity that a larger one does not share, so a
   threshold tuned on the pilot could be either too lenient or meaningless at full scale.
3. Is there a **scale below which the task simply fails** for capacity reasons, so that a null result
   from the pilot would tell us nothing about the method? If so, name it, because that is the floor for
   the pilot, and a pilot beneath the floor is wasted work.

**C0c.** Is there **published precedent** for this staged design in applied machine-learning work, a
small-model pilot used to validate a pipeline before committing compute to the reported model? If it is
standard practice, say so and cite it, because we would then describe it as such in the methods. If it
is not, say that too.

Only after those, the original size question, which now applies to Leg 2 alone.

`L04` was answered under the assumption that we should take the smallest model that works. That was
never quite the question and it is definitely not the question now.

**C1.** On **one A100 80 GB**, single node, seven days, show the memory arithmetic (do not assert it)
for LoRA in bf16 and for a full fine-tune with 8-bit AdamW, at sequence length 2048, batch 1, gradient
checkpointing on, for a 7B to 9B dense model, a roughly 27B to 32B dense model, and one MoE candidate.
State every assumption: optimiser state, gradient accumulation, activation checkpointing, attention
implementation. Where a configuration does not fit, say so.

**C2.** Given roughly 200,000 to 400,000 short training sequences (a few hundred tokens each), estimate
the **wall-clock training time** for each of those three sizes on one A100 80 GB for three epochs. Our
hard limit is seven days per job with no multi-node. If a 27B to 32B full fine-tune cannot finish in
seven days, that is the answer and we want it stated numerically, not hedged.

**C3.** Is there **published evidence** on the relationship between model scale and quality for
**structured generation and exact format adherence after fine-tuning**, as opposed to general
reasoning? Our task requires almost no reasoning and a great deal of format adherence. Cite precisely.
If the evidence says a 7B fine-tune matches a 30B fine-tune on narrow structured generation, that
settles our decision and saves us a month.

**C4.** At what scale, if any, does the pretrained prior begin to contribute genuine knowledge about
**human daily routines**, as opposed to merely providing a well-initialised sequence model? This is the
mechanism by which our cross-national transfer claim can succeed, so it is the one argument that would
justify paying for a larger model. Is there any evidence for it, or is it a hope?

**C5.** State plainly what we lose by choosing 7B over 30B, and what we lose by choosing 30B over 7B.

---

# PART D. Token efficiency, reassessed at generation scale

**D1.** Given the episode serialisation described above (196 to 326 tokens per diary), quantify what a
three-tokens-per-code tokenizer actually costs us, separately for:

* **training**, in extra tokens per epoch and therefore in extra GPU hours;
* **generation of several million diaries** with vLLM, in throughput and wall-clock, since decoding is
  sequential and every extra token is an extra forward pass;
* **context**, which we believe is a non-issue at these lengths. Say if we are wrong.

Give numbers with your assumptions shown. We expect training and context to be negligible and
generation to be the only place it bites. **If that expectation is wrong, say so.**

**D2.** Re-verify `RL17`'s per-model tokenisation measurement from each model's tokenizer configuration
rather than from a blog post, and extend it to whatever new candidates Part A adds: how many tokens do
the strings `011`, `111`, `411` and `911` each produce, and what does one complete episode string such
as `45,311,11,0;` cost per family?

> We will measure this ourselves locally. The value of your answer is that a disagreement between your
> numbers and our measurement tells us something is wrong with our setup.

**D3.** Can a tokenizer's digit behaviour be **worked around** without adding vocabulary tokens, for
instance by choosing a code alphabet that the tokenizer already merges efficiently? We cannot add
tokens: unfreezing the embedding matrix costs roughly 16.8 GB of optimiser state and breaks our export
path. But we are free to choose how we spell the codes. Is there a spelling that a three-token
tokenizer handles in one token? If yes, the whole tokenizer argument dissolves and we should know that.

---

# PART E. Country knowledge, which is the mechanism our claim depends on

Our claim is that a model fine-tuned on four countries generates useful diaries for a fifth country it
never saw. If the model's pretrained knowledge of daily life is heavily skewed towards Anglophone or
Western European countries, then it transfers best to the countries it already knows, which is the
wrong direction for the claim and is a limitation we must pre-register.

**E1.** Is there any published evaluation of **country-level or cultural knowledge asymmetry** across
these model families? Benchmarks measuring Western or Anglophone bias in world knowledge are directly
relevant. Give per-family results if they exist.

**E2.** Our serialisation is numeric and English-keyed. Does **multilingual capability** matter to us at
all, or are we about to pay for something we will never use? Argue it both ways and then commit.

**E3.** Does any family document its **pretraining data composition by country or language** in enough
detail that we could state, in the paper, that the held-out country was or was not well represented?
Being able to say this would strengthen the transfer analysis considerably.

---

# PART F. Ecosystem readiness, per shortlisted model

Name library versions and the date you checked them.

1. `transformers`, `peft`, `trl`: supported, at which version.
2. A fine-tuning stack runnable **fully offline** on a compute node with no internet, weights staged in
   advance.
3. `vLLM` with `XGrammar` structured output, since our generation must be grammar-constrained. Confirm
   that the specific model architecture is supported by the current vLLM release, not merely that vLLM
   supports the family name.
4. Generation throughput on one A100 80 GB, tokens per second, for each shortlisted model, from a
   published benchmark you can cite rather than an estimate. If no citable benchmark exists, say
   `NOT FOUND` rather than estimating.

A model that is three weeks old and not yet supported by this stack is a bad choice for us regardless
of its scores.

---

# PART G. Your single recommendation

One family, one size, one checkpoint type. Give:

1. The three strongest reasons for it.
2. **The strongest reason against it**, which must not be a token thrown in for balance.
3. The **second choice**, and the specific finding that would make us switch to it.
4. One sentence on what we should do if the licence verdict in Part B disqualifies your first choice.

We currently believe the answer is `Qwen/Qwen2.5-7B` or its current successor, on the grounds that
Apache 2.0 places no condition on the generated output, and that the token disadvantage is small under
episode serialisation. **This is a belief, not an instruction. If it is wrong, say so plainly.** Note
also that a report agreeing with the option we already named has told us very little; the diagnostic
value is in what we did not supply.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all of these in plain sentences in Section G.

1. **Which licence clauses did you read in the licence document itself, and which did you report from
   memory or from a summary?** List them in two groups. A clause reported from memory will be treated
   as a hypothesis, not a finding, and we will read it ourselves before acting on it.
2. **Did your recommendation land on the model we named as our current belief?** If yes, name the
   evidence that would have made you recommend against it, and say why it did not apply.
3. **How many of your answers happen to make our plan easier?** Count them. A round in which the
   licence is permissive, the small model is sufficient, the tokenizer does not matter and the compute
   is ample will be treated as a failed round and re-run with the controls tightened.
4. Name one thing about this model decision that we have not asked about and should have.

Also required, as in every round of this series:

* A citation is not evidence until opened. Say which documents you opened in full.
* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always.
* Never recommend the option that happens to rescue us.
* Every version, size, licence term or quantity carries the date it was checked.
* Do not report a model whose weights you have not confirmed are downloadable.
* Do not recommend anything needing more than one GPU, more than seven days, or any paid API.
* Do not state, estimate or reproduce any result of our models.
* No em dashes and no en dashes in the returned text.
