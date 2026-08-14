# L08. Evaluation: how to prove a generated population of diaries is faithful, and what the gate values should be

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. **Do not propose a threshold that our model would conveniently pass; you cannot see
our results, so any such number is invented.**

## Why we are asking

Our previous papers were governed by a **pre-registered gate table**: metrics and thresholds fixed
before any model was trained, so that a failing model is reported as failing. That discipline is the
reason those papers survive review, and we intend to keep it. We need the gate table for this paper
built from the literature, before we train anything.

The hard part is that our task is **not prediction**. Accuracy on a held-out diary is close to
meaningless: two people with identical demographics legitimately have different days, so a model that
maximises per-slot accuracy will produce the modal day for everyone and score well while being useless.
Our published work reports 0.98 accuracy on a multi-task classification framing, and we are aware that
a reviewer of a *generative* paper will not accept accuracy as the headline. We need the metrics that
detect **distributional collapse**.

## What we need

### Item 1. Metrics for distributional fidelity of generated activity sequences

For each metric: definition, what it detects, what it misses, how it is normalised, whether it has an
interpretable scale, and at least one paper that uses it on activity or mobility sequences.

Candidate families, and please add any we have missed:

1. **Time-of-day marginals**: the share of the population in each activity or location at each slot,
   compared curve against curve. Which divergence measure is standard: Jensen-Shannon, earth mover,
   RMSE in percentage points? Our previous gates used JS below 0.02 bits and EMD below 0.05, both
   project-chosen; is there a literature-standard value?
2. **Activity time budgets**: mean minutes per day per activity category, per demographic stratum.
   Eurostat publishes exactly this, which makes it our best externally-anchored target.
3. **Transition structure**: transition matrix distance, and the number of transitions per day.
   Over-smoothed generators produce too few transitions; this is the classic tell and we want the
   metric and the reference value.
4. **Dwell-time distributions**: per activity, compared with a two-sample test. Which test, and what to
   do about its sensitivity to large sample sizes, since with a million generated diaries every test
   rejects.
5. **Sequence-level diversity**: entropy of the generated diary distribution, count of unique
   sequences, nearest-neighbour distance from each generated diary to the training set. The last of
   these is also our memorisation check (`L10`), so please treat it carefully.
6. **Joint and conditional fidelity**: does the generated population reproduce the *association* between
   demographics and behaviour, not just the marginals. Name the metric. A model can match every
   marginal and still assign the wrong days to the wrong people, and that failure is invisible to
   marginal metrics.
7. **Within-stratum variance**: the variance-collapse detector. If the model produces the modal day for
   everyone in a stratum, marginals may still look acceptable in aggregate while variance is far too
   low. Which statistic detects this, and what is the reference value from real survey data?

### Item 2. The large-sample problem with hypothesis tests

We will generate a very large synthetic population. Any null-hypothesis test will reject at that size.
What is the correct practice: effect sizes rather than p values, subsampling to the real sample size,
equivalence testing with a pre-specified margin, or something else? Cite the methodological source.
This will be raised in review and we want the answer in the method section from the start.

### Item 3. External validation targets that do not require microdata

Because microdata access is uncertain (`L01`), we want as much of the evaluation as possible anchored
to **published aggregate statistics**.

1. What exactly can the Eurostat HETUS published tables validate? Time budgets per country per
   activity per sex per age band, participation rates, and at what time resolution. Be specific about
   granularity, since it decides which of the item 1 metrics can be scored on a country whose microdata
   we never obtain.
2. Are there other published cross-national behavioural aggregates useful as targets: employment and
   working-time statistics, teleworking prevalence by country and year, retail opening-hours
   regulation, school calendars. Our previous papers used exactly this class of external anchor.
3. For building energy specifically, are there published **measured** occupancy or presence-at-home
   rates by country that a generated population should reproduce? Distinguish surveyed from metered.

### Item 4. Structural validity metrics

Define the checks, and give the pass criterion for each. We expect: correct slot count, all codes in
the coding list, exactly one location per slot, durations summing to the day, no impossible transitions
(name a source for which transitions are impossible rather than merely rare), and internal consistency
of co-presence. State whether the pass criterion should be 100 percent, and what to do with the
malformed remainder at generation time (discard and resample, repair, or count as failure).

### Item 5. Baselines the evaluation must include

List the baselines a 2026 reviewer will require, and for each say what it is and why it is hard to
beat. We expect at least: the training-set empirical distribution itself as the upper bound, a
demographically-matched donor resampling baseline, a Markov model, our own published conditional
Transformer, and, for the transfer experiment, the pooled cross-country average. Say which of these is
the **hardest to beat** and be blunt about it.

### Item 6. The transfer evaluation

For the leave-one-country-out design described in `L06` item B:

1. What metrics are meaningful when only aggregate statistics exist for the held-out country?
2. How should the result be reported so that a modest transfer result is not oversold? Name a reporting
   convention or a figure type used in the literature for this.
3. What would constitute **failure** of the transfer claim, stated as a number or a comparison, before
   we run it?

### Item 7. Propose the gate table

Close with a proposed pre-registration table:

| Gate | Metric | Threshold | Source of the threshold | Literature-derived or project-chosen? |

**Mark every row honestly.** A project-chosen threshold is legitimate if labelled as such; our previous
papers carry exactly that distinction and reviewers accepted it. A project-chosen threshold presented
as literature-derived is the defect we are guarding against. If a metric has no defensible threshold in
the literature, write `NO LITERATURE VALUE` and propose one explicitly labelled as our judgement.

## Named leads

The occupant-behaviour validation literature and IEA EBC Annex 66, 79 and 87 outputs; ASHRAE Guideline
14 and its calibration criteria, which we already use for the downstream energy comparison; the
synthetic-data evaluation literature, including published critiques of the metrics commonly used there;
the mobility and trajectory generation literature for sequence-fidelity metrics; the statistical
disclosure control literature for nearest-neighbour distance measures; Eurostat's own HETUS statistical
tables and their metadata for what is published and at what granularity.

## Hard constraints specific to this prompt

* **You cannot see our results. Any threshold you propose must come from a source or be explicitly
  labelled as your judgement with the reasoning shown.**
* **Do not propose accuracy as a headline metric.** If you believe accuracy belongs anywhere, say
  exactly where and why, and what it must be paired with.
* Prefer metrics with a bounded, interpretable scale, and say which of your recommendations do not have
  one.
* For every metric, say what a **model that cheats** would score. A metric that a memorising model
  scores perfectly on is not a validation metric, it is a memorisation detector, and we need to know
  which of these it is.

## Deliverable

**Section B** is the metric catalogue.

**Section C** is the proposed gate table from item 7.

**Section F** is the list of retrievable external validation datasets and tables, with direct URLs.

**Section G** carries the large-sample problem's resolution, the hardest baseline, the transfer failure
criterion, and your negative controls.
