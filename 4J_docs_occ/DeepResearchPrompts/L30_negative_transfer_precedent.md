# L30. Our cross-national transfer claim FAILED against its pre-registered null. Is that result already known in the literature, and on what evidence?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, E, F, G and H used. Section D: answer `not applicable to this prompt`.

**This prompt is for Step 6 and for the manuscript** (`Step6_docs/`, `writing/4thJ_crossStep_analysis.md`).
It is a **reading** prompt, not a rescue prompt. We are not asking you how to make the result go away.
The companion prompt `L31` asks about method alternatives; **do not answer `L31` here.**

---

## 🔴 Corrections block — this overrides the master brief on four points

The brief predates author decisions 5, 6 and 16 (2026-08-14) and decision `D-IMP-4` (2026-09-03).

1. **The corpus is HETUS only, three countries — Spain, the UK, Italy — one wave each.** Not four, not
   five, no Canada, no France, no ATUS. France is a physical baseline only and is never a denominator.
2. **One wave per country. Adding a second wave to training is a closed decision and is banned.**
3. **There is no forecast in this paper.** No year token, no scenario lever, no 2030, no
   Kitagawa-Oaxaca-Blinder decomposition. Out of scope, not deferred.
4. **The pipeline is Steps 0 to 11 and Step 11 is terminal.** Do not propose work that presupposes a
   further step.

Model weights are **withheld** by decision; synthetic data and code are released. Any recommendation
that requires releasing adapter weights is inadmissible.

---

## What we already hold, and must not be told again

* `RL03` prior art on LLMs for time-use generation.
* `RL06` alternatives to fine-tuning: the eight-candidate comparison and its ranking. **Do not re-rank
  those eight candidates.** We have it.
* `RL08` evaluation and gates.
* `RL06`'s central verdict, which is the reason this prompt exists: *"Pretraining provides zero
  measurable fidelity benefit for within-country diary generation where 10,000+ survey diaries are
  available. The pretraining prior is useful exclusively for cross-national transfer."* And:
  *"If the fine-tuned LLM cannot generate higher joint fidelity and transition accuracy on the held-out
  country than a demographically raked pool of real European survey donors, the LLM transfer claim
  fails."*

We designed the whole paper on that sentence. **We ran the test and the LLM lost.**

---

## What we measured ourselves, so you are not guessing

Leave-one-country-out, three folds (`es`, `uk`, `it`), train on two, generate the third conditioned
**only** on its published demographic marginals. Fine-tuned open-weight backbone, LoRA adapter,
grammar-constrained decoding. The null is a pool of **real donor diaries** from the other two countries
re-weighted by IPF to the held-out country's published marginals.

**Time-budget mean absolute error, minutes per day, three activity bands per fold. Lower is better.**

| Fold | Model | Raked-donor null | Margin |
|---|---|---|---|
| `es` | 36.81 / 34.52 / 44.32 | 9.94 / 8.82 / 11.81 | -26.9 / -25.7 / -32.5 |
| `uk` | 58.91 / 60.44 / 21.24 | 21.79 / 19.21 / 18.54 | -37.1 / -41.2 / -2.70 |
| `it` | 62.24 / 33.95 / 35.84 | 19.51 / 13.85 / 15.51 | -42.7 / -20.1 / -20.3 |

**The null wins every band of every fold, by roughly two to six times.** Supporting gates agree:
level-1 budget MAPE under 15 % passes 0 of 9; joint structure fails on dwell-time, total variation and
diurnal divergence in every fold under both weight bases; the nearest-neighbour-country null also beats
the model 9 of 9.

**Capacity is eliminated from three independent directions.**

1. **Backbone size.** 1.48 B to 7 B, a 4.7 times increase, moved mean MAE from **42.05 to 43.14**. Worse.
2. **Trainable parameters.** A full fine-tune of all 7,377,965,056 parameters against the adapter's
   79,953,920, a **92 times** increase, everything else identical, ended at a **higher** train loss at
   every epoch.
3. **Backbone family.** A second 7 B family costs 24 % more wall time and 16 % more VRAM and changes
   nothing any evaluation gate can see.

**One diagnostic result matters more than all of the above.** Our fictional-country control conditions
the model on a country token it has never seen with deliberately perturbed marginals, and scores two
things separately: does the output move in the direction the conditioning vector says, and does it move
by the right amount. **Direction passes in all three folds (R-squared at or above 0.80). Amplitude fails
in all three folds, at a slope of 0.40 to 0.53.** In plain terms: **the model steers correctly and
delivers about half the amplitude.** It is not ignoring the conditioning. It is under-responding to it.

---

## What we need

### Item 1. Is our result already published, by anyone, in any domain?

We want precedent, for or against. Find studies that ran a **like-for-like comparison** between a
fine-tuned or prompted large language model and a **reweighted real-donor or classical synthetic
population baseline**, on a population the generator had not seen, and reported which won.

Domains worth sweeping, in this order: synthetic population synthesis in transport and urban planning;
time-use and activity-based travel demand; human mobility and trajectory generation; cross-lingual and
cross-cultural zero-shot transfer where the target is a **distribution**, not a label; tabular
generative modelling under distribution shift.

For each study: the exact comparison, the metric, the direction of the result, sample sizes, and
**whether the baseline was raked to the target's marginals or merely pooled**. That last distinction is
the one most papers blur, and it is the whole difference between a weak null and ours.

🔴 **A result where the LLM won is as valuable to us as one where it lost.** If the LLM won, we need to
know what was different: more source populations, weaker null, a different target statistic, a different
conditioning depth. Report the difference, not the verdict.

### Item 2. Is "the strong donor baseline is very hard to beat" a known finding?

Independently of LLMs. In survey statistics, small-area estimation, synthetic population synthesis and
transfer learning, is there an established body of evidence on **how strong an IPF-raked donor pool is**
as a benchmark, and under what conditions a learned generator is expected to beat it?

We want the conditions stated as a rule, if the literature states one. For example: number of source
populations, degree of behavioural distance between source and target, dimensionality of conditioning,
whether the target statistic is marginal or joint.

🔴 **Specifically: is three countries, two in and one out, simply too few sources for transfer to be
possible at all?** If the literature gives a floor on the number of source populations below which
cross-population transfer is not expected to work, we need that number, its source, and whether it was
measured or asserted. This is the single most important line in this report for us, because it decides
whether our result is a fact about language models or a fact about our corpus size. **`NOT FOUND` is a
complete and successful answer here.**

### Item 3. The amplitude phenomenon

Our model steers in the right direction and delivers half the amplitude. Is this a named, documented
failure mode?

Candidate framings we have thought of, none of which we are attached to: regression to the training
mean under conditioning; conditional under-dispersion in autoregressive generative models; attenuation
of the conditioning signal at generation time; mode averaging across a multi-country training mixture.

For each framing you find in the literature: the name used, the domain, whether it was **measured**
with a slope-and-intercept style diagnostic as ours is, and what the paper concluded about its cause.
🔴 **We are asking whether the phenomenon is documented, not how to fix it.** Fixes belong in `L31`.

### Item 4. How is this kind of negative result reported, and does it get published?

We pre-registered the bar in the introduction, before training, and we did not clear it. Find published
examples in energy modelling, urban simulation, or applied machine learning where:

* a headline claim was pre-registered and then failed, and the paper was published anyway;
* the paper's contribution was relocated from the failed claim to the method or the apparatus.

For each: the venue, the year, how the abstract was worded, and where in the paper the negative result
sits. **We want the wording, not the encouragement.** If the honest finding is that this class of result
is mostly published in workshops or as short communications, say that plainly.

⚪ Venue selection itself is `L14`'s question and is not reopened here. Do not recommend a journal.

---

## Negative controls, mandatory, answered explicitly in Section G

1. **What in this prompt did you accept because we supplied it, rather than because you verified it?**
   You cannot see our runs, our cluster or our data. Every statement you make about our numbers is
   quoted from us or invented. Mark which.
2. **What would have made you answer that our result is unsurprising and well precedented?** State the
   evidence that would have produced that answer, then say whether you found it.
3. **Did you find yourself recommending anything that would rescue this project?** This prompt asks for
   no recommendation at all. If one appeared in your draft, name it and delete it.
4. **How many of your citations did you open, and how many did you infer from a title or an abstract
   snippet?** Give the two counts.
5. **Which of your DOIs did CrossRef resolve, and what title did the API return for each?** A DOI that
   does not resolve is reported as not resolving, not silently dropped.
6. **What is the strongest published evidence AGAINST our interpretation** that this is a genuine
   negative result about the method, rather than an artefact of our corpus, our null, or our metric?
   Argue that side properly for at least one paragraph.

## Bans

* No em dashes and no en dashes anywhere in the returned text.
* A citation is not evidence until opened. `NOT FOUND` beats an invented answer, always.
* Do not re-rank `RL06`'s eight candidates.
* Do not propose method changes. That is `L31`.
* Do not recommend a venue. That is `L14`.
* Do not propose adding countries, waves, or a forecast. All three are closed decisions.
* Every version, date, licence term or quantity carries the date it was checked.
