# L06. Is fine-tuning the right instrument at all? The alternatives, judged against the same task

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. **This prompt is licensed to conclude that the plan is wrong.**

## Why we are asking

The author's proposed method is fine-tuning an open-weight LLM. That was chosen because it is the
method they had heard of, not because it was compared against alternatives. Before a year is spent, we
want the comparison done honestly by someone with no stake in the answer.

The task, stated neutrally and without naming a method:

> Given a conditioning vector of household and individual attributes, a country, a season and a day
> type, produce a full-day sequence of 144 or 48 slots, each carrying an activity code from a
> hierarchical list of order one hundred, a location code, and a co-presence flag, such that a large
> generated population reproduces the joint and marginal distributions of a real surveyed population,
> and such that the model transfers to countries with little or no training data.

Nothing in that statement requires a language model. It requires a **conditional generative model of
discrete sequences with heavy structure and a strong requirement of distributional fidelity**.

## What we need

Assess each candidate below against the **same six criteria**, in one comparison table:

* **Fidelity**: can it match marginal and joint distributions of a real population.
* **Transfer**: can it serve a country with little or no training data. This is our headline claim.
* **Conditioning richness**: how many conditioning attributes it can absorb without blowing up.
* **Structural validity**: can output be guaranteed well-formed, or only encouraged.
* **Cost**: training and, crucially, **inference cost to generate one million diaries** on our hardware.
* **Reviewability**: how hard the method is to explain and defend in a building-science journal.

### The candidates

1. **Fine-tuned open-weight LLM.** The author's proposal. Judge it honestly on the same axes.

2. **In-context learning with a frozen open-weight LLM.** Put the codebook, a handful of real example
   diaries and the conditioning vector in the prompt; generate. Zero training. Question: is there
   evidence that few-shot generation can match a distribution, rather than produce individually
   plausible but distributionally wrong samples? We suspect not, and want the evidence either way.
   Also: what does this cost per generated diary at our scale, since prompt tokens dominate.

3. **Retrieval-augmented generation over the survey itself.** Retrieve the k nearest real respondents
   by demographic similarity, and have the model recombine or perturb their diaries. Question: at what
   point does this become **nearest-neighbour resampling with extra steps**, and would a reviewer be
   right to say so? Note that plain nearest-neighbour donor resampling is a legitimate and very strong
   baseline in survey statistics, and we must report it as such.

4. **The specialist sequence model we already have.** A conditional Transformer trained from scratch,
   which is exactly what our published work uses, with a country embedding added. It is cheap, we know
   how to build it, and it is the honest baseline. Question: on what axis, specifically, could an LLM
   beat it? If the only axis is transfer to unseen countries, then **the entire paper must be built
   around transfer**, and everything else is a distraction. Say so if you believe it.

5. **Discrete diffusion or masked-diffusion sequence models.** These have been proposed for exactly
   this shape of problem. Our previous round of research examined and rejected one such family on
   latency and transition-noise grounds. Has the evidence moved since? Cite specifics.

6. **Classical and statistical approaches**: Markov chains of various order, hidden semi-Markov models,
   which handle dwell time natively, agent-based activity schedulers, and the activity-based travel
   demand model tradition, which has generated synthetic daily schedules for decades and is a
   literature our reviewers may know better than we do. Our published work already reports high-order
   Markov chains at 0.691 accuracy against 0.98 for deep models on a multi-task classification framing,
   so do not re-derive that; instead say whether the **hidden semi-Markov** family, which we have not
   tested, would be a stronger baseline than the Markov chains we did test.

7. **Statistical matching, donor imputation and synthetic population synthesis**: iterative proportional
   fitting, combinatorial optimisation, copula methods, and the established synthetic-population
   literature in transport and urban simulation. These are the incumbent methods in our application
   area. **A reviewer will ask why we did not use them.** Give us the answer, and if the honest answer
   is that they are adequate for the within-country case and we are only better in the cross-country
   case, say that.

8. **A hybrid**: LLM to generate, then a statistical post-processing layer (raking, reweighting,
   rejection sampling) to correct the distributions. Question: does this exist in the literature, does
   it work, and does it undermine the claim that the model learned the distribution? There is a real
   tension between "our model is faithful" and "we corrected our model's output until it was faithful",
   and we would rather face it now.

## Additional questions

### Item A. Is there evidence that pretraining actually helps on this task?

This is the load-bearing empirical question for the whole paper. An LLM brings a prior over human
routines from pretraining. Either that prior is worth something on unseen countries, or the LLM is just
an expensively initialised sequence model.

Find any study that isolates this: a comparison of a pretrained model fine-tuned on a small target
sample against the same architecture trained from scratch on the same sample, on a **behavioural or
tabular or sequential** task rather than a language task. Report the measured advantage and at what
training-set size it disappears. If no such study exists for this task family, say `NOT FOUND` and name
the nearest analogue.

### Item B. The transfer claim, sharpened

If our claim is "the model generalises to countries whose microdata we do not have", the experiment
that tests it is **leave-one-country-out**: train on N-1 countries, generate for the held-out country
conditioned only on its published demographic marginals, and score against that country's published
aggregate statistics.

1. Is this design used in the literature you found, under this or another name?
2. What are its known weaknesses, and how would a hostile reviewer attack it?
3. What is the appropriate **null model** to compare the transferred model against? Candidates: the
   pooled all-country average diary, the nearest neighbouring country's model, and a demographics-only
   regression. Name the strongest null, because a transfer result that does not beat the pooled average
   is not a result.

### Item C. Your verdict

Rank the eight candidates for our specific task and constraints. If fine-tuning an LLM is not first,
say so in the first sentence of Section A. If it is first, say what it is first *at*, and name the
axis on which it loses.

## Hard constraints specific to this prompt

* **Do not be diplomatic.** A ranking where everything has merit is not usable. Rank them.
* **Do not assume we want the LLM to win.** We want the paper to survive review. A negative finding here
  saves us a year.
* Every performance claim needs a citation. Method descriptions may be uncited if they are textbook.
* Cost estimates must be tied to our hardware (one A100 80 GB, single node, no API budget).

## Deliverable

**Section B** is the eight-row comparison table on the six criteria.

**Section C** is the ranking and the verdict.

**Section G** carries item A's evidence, item B's null-model recommendation, and your negative controls.
