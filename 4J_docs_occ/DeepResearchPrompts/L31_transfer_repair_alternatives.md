# L31. Given a failed cross-national transfer, which concrete method changes have published evidence of fixing it — and which of them are admissible here?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D, E, F, G and H all used. **Section D is load-bearing in this prompt**: a method we cannot
run is not an alternative.

**This prompt is for Step 6.** It is the companion to `L30`. `L30` asks whether our negative result is
already known; **this one asks what, if anything, would change it.** Read `L30` first if you have it.
Do not restate `L30`'s answer here.

---

## 🔴 Corrections block — this overrides the master brief on four points

1. **HETUS only, three countries — Spain, the UK, Italy — one wave each.** No Canada, no France, no
   ATUS. France is a physical baseline, never a denominator.
2. **One wave per country. Adding a wave to training is a closed decision and is banned.**
3. **No forecast.** No year token, no scenario lever, no 2030.
4. **The pipeline is Steps 0 to 11 and Step 11 is terminal.**

---

## 🔴 The hard constraint that decides whether an answer is usable

**Our evaluation is pre-registered and frozen.** The pre-registration file was md5-locked before the
first training submission and two gates enforce it. **Bands cannot be moved, and a metric cannot be
changed after seeing the result.**

That has a precise consequence for your answer, and it is the most important instruction in this prompt:

* A method change that improves our numbers **against the frozen bands** is admissible, and would be
  reported as a **new, separately pre-registered experiment**, with the original result kept and
  reported alongside it. We do not delete the failure.
* A change that requires **re-defining the metric, the null, or the band** is **inadmissible**, no
  matter how well it is evidenced. Say so and move on.

🔴 **Sort every recommendation you make into one of those two boxes, explicitly, in Section C.** An
answer that does not sort is not usable to us.

---

## What we already hold, and must not be told again

* `RL06`'s eight-candidate comparison and ranking. **Do not re-rank it.**
* `RL05` fine-tuning method, `RL12` constrained decoding, `RL18` model family selection.
* We already run: LoRA adapters, grammar-constrained decoding with a state tally automaton,
  validation-set temperature scaling, no aggressive truncation, unweighted loss with the design strata
  carried in the prefix, joint multi-country training, and no raking of our own output.
* **We have already eliminated capacity as an explanation, three ways.** A 4.7 times larger backbone made
  it worse (mean MAE 42.05 to 43.14). A full fine-tune of all 7,377,965,056 parameters against the
  adapter's 79,953,920, a 92 times increase with everything else identical, ended at a **higher** train
  loss at every epoch. A second 7 B backbone family cost 24 % more wall time and 16 % more VRAM and
  changed nothing any gate can see.

🔴 **Therefore: any recommendation whose mechanism is "more parameters", "a bigger base model", "train
longer" or "a better backbone" is already falsified by our own measurements. Do not make it.** If you
believe our elimination is wrong, argue that directly in Section G with evidence, and say what we
should measure to settle it.

---

## The one diagnostic you should build your answer around

Our fictional-country control conditions the model on an unseen country token with deliberately
perturbed marginals, and scores **direction** and **amplitude** separately.

* **Direction: PASSES in all three folds**, R-squared at or above 0.80.
* **Amplitude: FAILS in all three folds**, slope 0.40 to 0.53.

**The model steers correctly and delivers about half the amplitude.** It is not ignoring the
conditioning vector. It responds to it at roughly half strength, and it is beaten two to six times over
by a pool of real donor diaries raked to the same marginals.

Meanwhile the joint structure fails hard: dwell-time Wasserstein at 5 to 6.7 times its band, total
variation at 3.3 to 4.7 times, diurnal divergence at 4.6 to 7.9 times.

---

## What we need

### Item 1. Methods with published evidence of increasing conditioning strength at generation time

Not methods that exist. Methods that were **measured** to increase the response of a conditional
generative model to its conditioning vector, on a task where the target is a **distribution**.

Candidates we are aware of and want judged rather than listed: classifier-free guidance and its
autoregressive analogues; contrastive or negative-prompt decoding; conditioning dropout during training;
auxiliary distribution-matching or moment-matching losses added to the token loss; reinforcement or
preference optimisation against a distributional reward; explicit calibration of the generated
distribution after sampling.

For each: **the measured effect size**, the task it was measured on, whether the target was a
distribution or a single sample, the implementation cost, and whether it has been applied to structured
sequence or tabular generation as opposed to images or free text.

🔴 **State plainly which of these are known to help with amplitude specifically, and which only help
with sample quality.** They are not the same problem and the literature routinely conflates them.

### Item 2. The hybrid that our own null suggests

Our null is not only a benchmark, it is a working method: real donor diaries raked to the target
country's marginals, and it beat us everywhere. `RL06` already ranked a **hybrid** first overall, but it
imagined the hybrid one way round — LLM generates, raking calibrates afterwards.

**Ask the opposite question.** Is there published evidence for a hybrid in which the **donor pool is the
generator** and the learned model does something narrower that donors cannot do: selecting or reweighting
donors under conditioning, editing a donor day, imputing the parts of the day where no donor matches, or
adjusting transitions?

For each variant found: was it measured against a plain raked donor pool, and did it beat it? **If the
honest answer is that plain raking is not beaten in the published record, say so.** That would be the
most useful sentence in this report.

### Item 3. What would have to be true for transfer to work at three source countries

Given two training countries and one held out, with conditioning on published marginals only, what does
the evidence say is **necessary** for a learned generator to beat a raked donor pool?

We want conditions, not encouragement. Candidates to test against the literature: a minimum number of
source populations; a maximum behavioural distance between source and target; conditioning richer than
published marginals; a target statistic coarser than the joint structure we score; an auxiliary
alignment signal between countries.

🔴 **If the evidence says the answer is "more source countries and nothing else", say that.** We hold a
documented route to widen the corpus from three to a larger set of HETUS members with no harmonisation
change, and it is currently not on the critical path. A clear finding here would move it.

### Item 4. What is NOT worth trying

Name the approaches that look attractive from where we stand and that the evidence says will not help.
We would rather spend this report closing doors than opening them. Be specific about why each one fails,
and cite the measurement that shows it.

---

## Section D. Feasibility, and what our hardware actually is

Judge every recommendation you make against this, and mark it feasible, feasible with a stated cost, or
not feasible.

* All computation for this paper now runs **locally on a single machine**. The institutional cluster is
  **fetch and read-only** for this project.
* Historic cluster constraints, which still describe the scale of what we can afford: **nothing
  multi-node, nothing over seven days of wall time**, single-GPU MIG slices that cannot communicate.
* Adapter training at 7 B is affordable. A full fine-tune at 7 B has been run once, as a control, and is
  not something we can run repeatedly.
* Anything requiring paid API inference, a closed-weight model, or a licence that conditions on generated
  text is **inadmissible**. Model weights are **withheld** from release by decision; synthetic data and
  code are released.

---

## Negative controls, mandatory, answered explicitly in Section G

1. **Which of your recommendations moves in the direction that rescues this project, and what is your
   evidence that it is not simply the answer we wanted?** Every prior round of this series that
   concluded the data was obtainable, the licence permissive and the method right turned out to be a
   failed round. Assume that risk applies to you.
2. **What would have caused you to answer "nothing will fix this, report the negative result and move
   on"?** State the evidence that would have produced that answer, then say whether you found it. If you
   did find it, that is a complete and successful report.
3. **Which of your recommendations fail our frozen pre-registration** and are therefore inadmissible?
   List them separately rather than quietly omitting them.
4. **Did you recommend more parameters, a bigger backbone, longer training or a different backbone
   family in any disguised form?** We eliminated all four ourselves. Name any recommendation of yours
   that reduces to one of them.
5. **How many of your citations did you open, and how many did you infer from a title or an abstract
   snippet?** Give the two counts.
6. **Which of your DOIs did CrossRef resolve, and what title did the API return for each?**
7. **What did this prompt not ask that it should have?** One question, the one seventeen prompts by the
   same author would not have thought to ask.

## Bans

* No em dashes and no en dashes anywhere in the returned text.
* A citation is not evidence until opened. `NOT FOUND` beats an invented answer, always.
* Do not re-rank `RL06`'s eight candidates.
* Do not recommend adding countries **to training** as a way of fixing the held-out fold; the
  leave-one-country-out design is fixed. Widening the corpus is Item 3's question and is a different
  thing.
* Do not propose adding waves, or a forecast. Both are closed decisions.
* Do not recommend a venue. That is `L14`.
* Every version, date, licence term, price or quantity carries the date it was checked.
