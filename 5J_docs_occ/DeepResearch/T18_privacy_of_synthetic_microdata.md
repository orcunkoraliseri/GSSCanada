# T18. Privacy and release of generators trained on survey microdata: is it a live research topic, what audits are expected, and what may ship

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Our fourth paper's research round covered release
policy for one model; this prompt asks whether the topic itself is a paper.

## Why we are asking

Our fourth paper's membership-inference audit failed its pre-registered bar, so the fine-tuned weights
are withheld and one country's synthetic set is withheld (master brief section 3, item 2). That
outcome is a result about generators trained on restricted microdata: a small fine-tuning corpus, a
pretrained prior, and a released synthetic population. Every angle that trains on HETUS or GSS
inherits the question. We want to know whether privacy of generative models trained on official
microdata is an active topic in statistics and machine learning, what audits reviewers and data
custodians now expect, and whether a rigorous release protocol is itself publishable.

## What we need

### Item 1. The state of privacy auditing for generative models on tabular and sequential data

The 2022 to 2026 methods for auditing synthetic data and generative models trained on microdata:
membership inference (shadow models, loss-based, reference-model), attribute inference, singling out
and linkability metrics (the Anonymeter line), distance-to-closest-record and its critiques,
canary-based memorisation tests, differential-privacy accounting. Per method: what it measures, its
known blind spots, the benchmark or study that stress-tested it. Section C rows. Say in Section A
whether the field has converged on a standard audit or is still contested.

### Item 2. What custodians and regulators require

What Eurostat, national statistical institutes (INE, ISTAT, ONS, Statistics Canada), the UK Data
Service and the Research Data Centre network in Canada say about **outputs derived from microdata**:
whether a fine-tuned model is an output subject to disclosure control, whether synthetic microdata may
be released, and under what test. Quote the rules with the date checked. Include the EDPB Opinion
28/2024 on AI models and personal data, and any 2025 to 2026 guidance from data-protection authorities
on trained models as personal data.

### Item 3. Differentially private fine-tuning and generation

Evidence on differentially private fine-tuning of language models and of tabular generators for
small corpora: the utility cost at useful epsilon, the studies that measured it on survey-like data,
and whether any reached distributional fidelity comparable to a non-private model. This decides
whether a private version of our generator is a realistic paper or a known dead end.

### Item 4. Released synthetic populations as precedents

Which synthetic populations or synthetic time-use and mobility datasets have been released publicly
after a privacy audit, by whom, with what audit, under what licence? Include national statistical
institutes' synthetic files, transport synthetic populations, and any synthetic activity-diary release.
Section F rows. Report what the release documentation says was withheld and why.

### Item 5. Is the release protocol a paper?

Which venues have published papers whose contribution is a **release protocol or privacy audit for a
generative model in an applied domain** (health, transport, energy), 2022 to 2026? Cite three. Say
what made them publishable: a new metric, a new failure found, a custodian-accepted protocol. Then say
whether our situation (pre-registered bar, measured failure, partial release) resembles them.

### Item 6. Reviewer expectations in our venues

What do *Energy and Buildings*, *Building and Environment*, *Applied Energy* and *Scientific Data*
currently require or expect about privacy of released synthetic occupancy or load data? Quote author
guidelines and any editorials. If nothing exists, `NOT FOUND`, which itself tells us the bar is unset.

## Named leads

arXiv `cs.CR`, `cs.LG`, `stat.ML`; IEEE S&P, USENIX Security, PETS, CCS for audits; *Journal of
Official Statistics*, *Transactions on Data Privacy*, *Journal of Privacy and Confidentiality*; the
UNECE synthetic-data guidance; Eurostat and national microdata access rules; EDPB opinions; the
Anonymeter and TAPAS repositories; Statistics Canada's synthetic data programme.

## Hard constraints specific to this prompt

* Every rule quoted from the custodian's page with the date checked.
* Every utility cost in item 3 carries its epsilon, its dataset and its metric.
* Do not tell us our audit should have used a different bar. The bar was pre-registered.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences whether privacy auditing of generative models on
microdata has a standard, and whether a fine-tuned model is treated as a disclosive output by the
custodians named.

**Section C** is the audit-method table from item 1.

**Section F** is the released-population table from item 4.

**Section E** is items 3, 5 and 6.

**Section G** carries the custodian rules from item 2 and your negative controls.
