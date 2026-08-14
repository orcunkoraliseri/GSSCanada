# L10. Privacy, statistical disclosure and what we are allowed to release: does a model trained on microdata leak the microdata?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. **This prompt can end the project's release plan. Do not soften the answer.**

## Why we are asking

Our published work's stated ethical advantage is that it uses **anonymised official statistics** rather
than sensor data, avoiding the privacy problems of monitoring real buildings. That claim was easy to
make when the model was a small classifier trained locally and never released.

It becomes much harder when we propose to **fine-tune a language model on restricted-access microdata
and publish the weights**. Language models are known to memorise and regurgitate training data. A
released model that can be induced to emit a real respondent's diary, with their demographic vector
attached, is a disclosure event involving a national statistical institute's confidential data, and it
would be a serious matter for the author and the institution, not merely a paper defect.

We need to know, before we design anything: what the data-use agreements will forbid, what memorisation
risk actually is at our data scale, and what a defensible release looks like.

## What we need

### Item 1. What the data agreements say

Building on `L01`, and reading the actual instruments:

1. For Eurostat scientific-use and secure-use microdata, what do the governing texts say about
   **derived outputs**? Specifically: is a **trained model** a derived output, an intermediate result,
   or something the agreements do not contemplate at all? Quote the relevant clauses.
2. Is there an **output-checking** requirement, where results must be reviewed before publication? If
   so, does it apply only to tables and statistics or also to model artefacts? Name the procedure.
3. What do national statistical institute agreements typically say for the countries whose microdata is
   downloadable directly (see `L01` item 4)? Note where they are stricter than Eurostat.
4. Is there **any published precedent** of a machine learning model trained on official microdata being
   publicly released with weights, and what conditions applied? A single documented precedent would be
   worth a great deal to us. If you find none, say `NOT FOUND`.

### Item 2. Memorisation, measured

1. What is the current evidence on **verbatim memorisation** in LLMs: how it scales with model size,
   with number of epochs, and with duplication of a record in the training set? Give the quantitative
   findings, not the headline.
2. Crucially: what is known about memorisation when fine-tuning a **small number of epochs on a small,
   highly repetitive, structured corpus** rather than pretraining on a web corpus? Our corpus is on the
   order of hundreds of thousands of short, highly similar records. Intuition cuts both ways: high
   similarity might mean no single record is distinctive, or it might mean the few distinctive records
   are memorised very sharply. Which does the evidence support?
3. What is known about memorisation with **LoRA and other PEFT methods** compared with full fine-tuning?
   If PEFT memorises measurably less, that is a design argument and we want the citation.
4. What is the actual **attack**: how would someone extract a training record from our model? Describe
   the practical procedure, including membership inference and extraction attacks, so that we can run
   the attack against our own model before release. **We intend to attack our own model and report the
   result**, and this item is the specification for that experiment.

### Item 3. The disclosure question specific to our data

A time-use diary is unusually identifying. A person's full day, at ten-minute resolution, plus
municipality, household composition, age band, occupation and employment status, is close to a
fingerprint even without a name.

1. Is there literature on the **re-identification risk of time-use or activity-sequence data**
   specifically? Mobility data is famously re-identifiable from very few points; does the same result
   hold or transfer for activity diaries?
2. What disclosure-control measures do statistical institutes apply to time-use microdata before
   release: coarsening of geography, top-coding, collapsing rare activity codes, suppression of rare
   household types? Name them, because they constrain what our model can even learn.
3. What is the accepted **similarity-based disclosure metric** for synthetic data: distance to closest
   record, nearest-neighbour distance ratio, and their known weaknesses? Give the operational
   definition we should implement, and say what value indicates a problem. Note that our previous
   research rounds taught us that a metric with no failing condition is not a metric, so we want the
   failing condition stated.

### Item 4. Differential privacy: is it worth it here?

1. What would **DP fine-tuning** cost us in utility, at our data scale and model scale? Give measured
   numbers from published work, and be honest about the fact that most published DP fine-tuning results
   are on classification tasks, not on distribution-matching generation.
2. Is DP even the right frame? Our output is meant to reproduce the population distribution, which is
   exactly what DP protects at the individual level and permits at the population level. Say whether DP
   is a natural fit or an awkward one for our objective.
3. Are there **cheaper practical mitigations** that get most of the protection: deduplicating the
   training set, limiting epochs, discarding rare strata, adding noise to the conditioning vector,
   coarsening geography before training, or refusing to release the model at all and releasing only
   generated data. Rank them by protection per unit of utility lost.

### Item 5. What a defensible release looks like

Give us the options, ranked, with what each costs and what each buys:

1. Release the fine-tuned weights or adapter publicly.
2. Release the weights on request, under an agreement.
3. Release only the **generated synthetic dataset**, not the model.
4. Release only the code and the recipe, with neither weights nor data.
5. Release nothing and report results only.

For each: is it compatible with the data agreements from item 1, does it satisfy typical journal
data-availability policies (`L15` covers those in detail), and what is the reputational and legal
exposure. **State which you would advise**, given that the author is a postdoctoral researcher at a
Canadian institution working with European statistical microdata.

### Item 6. Ethics review

1. Would this work typically require research-ethics board review at a Canadian university, given that
   it uses already-collected, anonymised, official statistical microdata? Cite the applicable policy
   framework, and note where a secondary-use-of-anonymised-data exemption normally applies and where it
   does not.
2. Does training a generative model on anonymised data change that answer? This is the interesting
   question and it may not be settled; if it is not, say so.
3. Does GDPR bear on this at all, given the data concerns EU residents and the researcher is in Canada?
   Distinguish anonymised from pseudonymised, since the answer hinges on it.

## Named leads

The Commission regulations governing access to confidential data for scientific purposes, and Eurostat
microdata access documentation; national statistical institute microdata licence texts; the published
literature on memorisation and extraction in language models; the statistical disclosure control
literature and the synthetic data privacy metric literature; the Canadian Tri-Council Policy Statement
on ethical conduct for research involving humans; GDPR recitals and guidance on anonymisation.

## Hard constraints specific to this prompt

* **Quote clauses, do not summarise them.** For anything legal or contractual, give the document, the
  clause number and the operative sentence. An unsourced legal claim is worse than no answer.
* Where a question is genuinely unsettled, say it is unsettled. Do not manufacture a confident answer
  on an open legal question.
* **Do not tell us it will probably be fine.** Name the condition under which it would not be.
* You are not our lawyer and we are not asking you to be. Give sources and let us take advice.

## Deliverable

**Section A** opens with a one-sentence answer to: may we publish a model fine-tuned on restricted
statistical microdata.

**Section B** carries the memorisation evidence with numbers.

**Section C** carries the ranked release options from item 5 and your recommendation.

**Section G** carries the extraction-attack specification from item 2 item 4, which we will implement,
and your negative controls.
