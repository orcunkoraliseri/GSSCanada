# L17. Adjudicate the contradictions between rounds 1 to 16, and establish the multi-wave inventory

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## What this prompt is, and why it is different from L01 to L16

The first sixteen prompts were **exploratory**: each asked an open question and returned a report. This
one is **adjudicative**. Sixteen reports came back and they disagree with each other in eight specific
places, and they assert fourteen specific things that no one has checked. This prompt hands you those
disputes and asks you to settle them.

🔴 **The single most important instruction in this prompt: DO NOT SPLIT THE DIFFERENCE.**

When you are shown two conflicting claims, the overwhelmingly likely situation is that **one of them is
simply wrong**, or that both are describing different objects and one has been mislabelled. A synthesis
that says "both are partly right, it depends" is the least useful answer you can produce and, in this
project's experience, it is usually a sign that neither claim was actually checked. For every dispute
below, the acceptable answers are:

* **"A is correct, B is wrong"**, with the document and page or clause that shows it.
* **"B is correct, A is wrong"**, likewise.
* **"Both are wrong, the truth is C"**, likewise.
* **"They describe different objects"**, naming both objects precisely and saying which one applies to
  a researcher receiving a Eurostat Scientific Use File.
* **`NOT FOUND`** — nobody outside the data provider can determine this from public documents.

`NOT FOUND` is a **good** answer here and will be acted on. It tells us to ask the provider directly
instead of trusting a report. An invented resolution costs us months, because we would build on it.

🔴 **You are not being asked to be helpful. You are being asked to be right.** Several of the disputes
below have a "convenient" side, the one that makes our project easier. If the evidence points at the
inconvenient side, say so plainly. A report that resolves every dispute in the direction that suits us
will be treated as a failed round and re-run.

---

## Background you need

The project fine-tunes one open-weight language model on harmonised time-use diary microdata to
generate activity-resolved occupant schedules for building energy simulation, and tests whether it
transfers to a country held out of training. **Four things have been decided by the author since the
sixteen reports came back, and they change what matters in this prompt:**

1. **The trained model will not be published.** That is settled and accepted. The paper describes the
   method; the artefacts released are the generated synthetic data and the code. **Do not re-open this
   question and do not propose ways around it.**
2. **The corpus is five countries: Italy, Canada, Spain, the United Kingdom, France** — and it is
   explicitly **multi-wave**. We want several survey cycles per country, not one. **Part B of this
   prompt is entirely about establishing what those waves actually are.**
3. **There is no forecast in this paper.** No projection to a future year. The contribution is the
   method of applying a language model across the HETUS and wider time-use framework. Do not propose
   forecasting designs, scenario levers or projection datasets. That axis is closed.
4. **The hard null model is the target, not an obstacle.** Beating a pool of real diaries from other
   countries, reweighted to the held-out country's demographics, is the stated aim of the experiment.

---

# PART A — THE EIGHT CONTRADICTIONS

For each: state which side is right, cite the document that shows it, and say what a researcher should
expect to actually receive or observe.

## A1. What shape does a HETUS Scientific Use File actually arrive in?

* **Claim from RL02:** Three linked relational files — `INDFILE` (household and individual), `DDFILE`
  (one row per diary day), `EFILE` (one row per activity **episode**, with `START` and `DURATION`).
* **Claim from RL01:** One flat **wide** file per diary day containing approximately 1,950 variables,
  with the day held as 144 slot columns.

These cannot both describe the same delivery. This decides how we write the parser, so it is the single
most operationally expensive dispute in this list.

**Answer specifically:** which is delivered for the 2010 round; whether both exist (for example a wide
extract generated for a statistical package alongside a relational source); the actual file names and
formats; and whether the episode-level `START` and `DURATION` fields exist in the delivered file or must
be reconstructed by run-length-encoding the slot columns. **Name the document and the page.**

## A2. What are the weight variables called?

* **RL02:** `WGHT_IND` and `WGHT_DIA`.
* **RL09:** `IND_WGT` and `DIA_WGT`.

Trivial to look up, impossible to guess, and it is a symptom: if two reports invented plausible variable
names, the rest of both variable lists is suspect. **Give the actual variable names from the official
variable list, and say how many weight variables the file carries in total.** If national files differ
from the Eurostat file, say so.

## A3. Does Mistral 7B v0.3 tokenise a three-digit number as one token?

* **RL04 and RL07 both state** that Mistral 7B v0.3 uses the "Tekken" tokenizer and groups up to three
  digits into a single token.
* **Our suspicion:** Tekken was introduced with **Mistral NeMo**, not with Mistral 7B v0.3. Mistral 7B
  v0.3 is generally understood to use a SentencePiece tokenizer with a 32,768-token vocabulary. If that
  is right, both reports repeated the same error, which matters because it is a model we were about to
  select on the strength of it.

**Answer specifically, per model:** `mistralai/Mistral-7B-v0.3`, `mistralai/Mistral-Nemo-Base-2407`,
`Qwen/Qwen2.5-7B`, `meta-llama/Llama-3.1-8B`, and `google/gemma-2-9b` — the tokenizer type, the
vocabulary size, and **how many tokens the strings `011`, `111`, `411` and `911` each produce**. The
answer should come from each model's tokenizer configuration, not from a blog post.

> We will also measure this ourselves. The value of your answer is that a disagreement between your
> answer and our measurement tells us something is wrong with our setup.

## A4. What is the correct identifier for the LLM-Mob paper?

Three reports gave three different answers for the same paper:

* **RL03:** arXiv:2308.15197, authors Wang, Fang, Zeng, Cheng.
* **RL06:** arXiv:2308.15043, authors Wang, Jiang, Li, Meng, Ding, Gao.
* **RL14:** arXiv:2309.04477, authors Jindong Wang, Xixun Lin, Yiqiao Jin, Chendi Ge, Xing Xie.

At most one is right. **Give the correct arXiv identifier, the correct author list, the correct title
and the publication venue if it has one.** Then do the same for the GReaT tabular-generation paper,
which appears as arXiv:2210.06280 in two reports and arXiv:2210.01637 in a third.

**Then answer the diagnostic question:** having found two fabricated or garbled identifiers in one
reference list (RL14), is there any reason to trust the rest of that list? We intend to discard it
entirely and would like to know if that is an overreaction.

## A5. Widén and Wäckelgård 2010 — which volume, issue and pages?

* **RL08:** *Applied Energy* 87(3), 780-789.
* **RL06 and RL13:** *Applied Energy* 87(6), 1880-1892.

Both cite the title "A high-resolution stochastic model of domestic activity patterns and electricity
demand". **Resolve it via CrossRef and report the title the API returned.** Then check whether the other
page range belongs to a *different real paper* by the same group, because if it does we may be
conflating two papers that we should be citing separately.

## A6. Where did the "±12 to 18 minutes per day" survey margin of error come from?

`RL08` sets one of our validation gates at 15 minutes per day and labels it **literature-derived**,
justified by "the Eurostat HETUS sample margin of error at 95 % confidence for typical national
subsamples of N ≈ 500 to 1000 per stratum". No source is given for that figure.

**Find it or report `NOT FOUND`.** Specifically: do the HETUS methodological guidelines or the national
quality reports publish standard errors or confidence intervals for mean daily minutes per activity per
demographic stratum? If they do, give the actual figures and the document. If they do not, say so, and
we will relabel the gate as project-chosen, which is a perfectly acceptable outcome and costs us
nothing except honesty.

## A7. Is the unique-sequence fraction of a real time-use survey really above 0.98?

`RL08` asserts that real 144-slot time-use surveys show a unique-sequence fraction U > 0.98 and builds a
distribution-collapse gate on it. **Is this published anywhere, for any national time-use survey?** Give
the figure, the survey and the source, or report `NOT FOUND`.

We can and will compute this on our own held data. The question is whether a published reference value
exists that a reviewer would expect us to cite.

## A8. What are the actual partition names on the Concordia Speed cluster?

`RL11` asserts partitions `pt`, `pn`, `pg` and gives a full job template built on them. Our own `sinfo`
query on 2026-08-13 returned `ps`, `pt` and `cl` on the A100 nodes and did not show `pn` or `pg` in that
role.

**Consult the Speed HPC documentation at `https://nag-devops.github.io/speed-hpc/` and the
`NAG-DevOps/speed-hpc` repository, and report the current partition list with what each is for**,
including which partitions carry GPUs and the maximum walltime of each. Quote the document version and
date. If the documentation contradicts a live cluster query, say that the live query wins and that the
documentation is stale, because that is useful to know too.

---

# PART B — THE MULTI-WAVE INVENTORY (the new design question)

The corpus is now **five countries by several waves each**. This part is the largest single block of new
work in this prompt, and it has an operational purpose: we need to know exactly which files exist,
whether we can obtain them, and whether they can be pooled without manufacturing a false trend.

## B1. The inventory table

For **Italy, Canada, Spain, the United Kingdom and France**, list **every** national time-use survey
wave, from the earliest to the most recent, with one row per wave:

| Country | Wave and fieldwork years | Conducting body and survey name | Diary slot length | Diary days per respondent | Minimum respondent age | Activity coding scheme used | Microdata obtainable? By whom, how, at what cost, how long? | Direct URL to the download or the application record |

Cover at minimum, and correct these if they are wrong, because they come from an earlier report that may
have invented them:

* **Italy** — ISTAT *Indagine sull'uso del tempo*, reportedly 1988, 1995, 2002-03, 2008-09, 2013-14, and
  any wave after 2013-14.
* **United Kingdom** — reportedly 1983, 1987, 1995, 2000-01, 2014-15, and the 2020-2023 online waves.
* **France** — INSEE *Enquête Emploi du Temps*, reportedly 1974, 1985, 1998-99, 2009-10, and any wave
  after that.
* **Spain** — INE *Encuesta de Empleo del Tiempo*, reportedly 2002-03, 2009-10, and a wave around
  2024-25.
* **Canada** — Statistics Canada GSS time-use cycles. We hold several already. **Give the complete list
  of GSS time-use cycles with their years and cycle numbers**, so we know what we are missing.

🔴 **For each row, state whether the microdata is actually downloadable by an academic researcher based
in Canada, and how.** A wave that exists but cannot be obtained is worth knowing about but is not part
of the corpus, and it should be marked as such.

## B2. Comparability breaks between waves, per country

This is the part that decides whether multi-wave training is honest or is manufacturing artefacts.

For each country, list every **known break** between consecutive waves, and for each say whether it is
documented by the statistical institute or is your inference:

* Activity coding scheme changes, and whether the institute published a bridge or crosswalk.
* Diary slot length changes (we already know UK 2000 used 15 minutes against the later 10).
* Collection mode changes: paper booklet, telephone, computer-assisted, web, smartphone app. **Name the
  wave in which each country switched**, because mode change is the break most likely to be mistaken for
  behavioural change.
* Sample frame or minimum age changes.
* Whether secondary activity, location and co-presence were collected in that wave at all. A wave
  missing the location field is nearly useless to us, since location is what maps a diary to a building.
* Any wave whose fieldwork overlaps national COVID-19 restrictions, with the months.

## B3. The crosswalk question, sharpened

Our five-country corpus spans at least three different activity coding traditions: HETUS ACL (in two or
three editions), the Canadian GSS scheme, and any national scheme used in the older waves.

* **Does the MTUS 69-activity harmonised frame cover all five of these countries across all the waves
  listed in B1?** Give the coverage per country and wave. Where MTUS does not reach, say so.
* **Is MTUS itself obtainable** by a Canada-based academic, and does obtaining it bring restrictions
  comparable to the Eurostat ones? We need to know before we depend on it.
* At what level of the activity hierarchy does a **defensible** cross-wave, cross-country mapping
  actually exist: 1-digit, 2-digit or 3-digit? Give the level and the evidence. We would rather pool at
  a coarse level that is true than a fine level that is asserted.
* Is there a published example of a study that pooled several national time-use surveys across several
  decades? If so, **what did they do about the breaks**, and what did reviewers make of it? A worked
  precedent is worth more here than a principle.

## B4. What multi-wave data buys us, assessed honestly

Given that **this paper contains no forecast**, evaluate what having several waves per country actually
provides. Be willing to conclude "not much, use the most recent wave per country and keep it simple",
because that is a real possible answer and it would save us months.

Address each of these separately:

1. **More training data.** Roughly how many additional diary-days do the extra waves add per country?
   Approximate is fine; state your basis.
2. **A second held-out axis.** Does leaving out a *wave* rather than a *country* give us a second,
   independent test of the same transfer claim? Is there precedent for that design?
3. **Wave as a conditioning attribute.** If the model is conditioned on wave alongside country and
   demographics, does that help it separate "how people behave" from "how the survey was run"? Or does
   it simply give the model a channel to memorise survey artefacts?
4. **The risk.** Does pooling waves with different coding schemes and collection modes **degrade** the
   model by teaching it that the same demographic profile has several different behaviour patterns, when
   the difference is really instrumentation? This is the question we are most worried about. Give it the
   most space.
5. **A recommendation**, in one paragraph: how many waves per country should we actually use, and on
   what principle do we cut the older ones off?

---

# PART C — SIX CLAIMS NOBODY HAS CHECKED

Short answers are fine. Each is a single fact that we are currently carrying on trust.

1. **Eurostat recognised research entities.** Is there a current public list, and are McGill, Université
   Laval, Queen's, UQAM and the University of Calgary actually on it? Is Concordia? **Give the document,
   its date, and quote the relevant lines.** If the list is not public, say so.
2. **The Eurostat application route from a non-EU institution.** Confirm or refute: any legal-entity
   recognition, the forms, the fee (we were told zero), and the stated turnaround. Quote the source.
3. **Elsevier article processing charges under the CRKN agreement.** Are they genuinely fully waived for
   a Concordia corresponding author in *Energy and Buildings* and *Building and Environment*, and does
   the subscription publication route cost nothing? Give the agreement document and its expiry date.
4. **EN 16798-1 Annex C.** `RL13` reported `COULD NOT OPEN` and did not reconstruct it, which was
   correct. **Is there any legitimately open source that reproduces the residential occupancy and
   internal-gain schedules from that annex** — a national implementation, a published paper that
   transcribes them with permission, a public standards preview? If not, say `NOT FOUND` and we will buy
   the standard. **Do not reconstruct the tables from secondary descriptions under any circumstances.**
5. **Constrained decoding libraries.** What are the current versions of vLLM, XGrammar and Outlines as
   of the date you check, and does vLLM still ship XGrammar as its structured-output backend? Version
   claims in this project go stale in months, so give the date.
6. **`Schedule:File` in current EnergyPlus.** Confirm the field name and accepted values for the
   interpolation setting in the version current at your check date, and confirm that sub-hourly external
   schedules at a 10-minute interval are supported. Give the version number.

---

# PART D — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

One short section, and it is not a formality.

You have now seen the full shape of this project through the master brief and this prompt: five
countries, several waves, one fine-tuned open-weight model, a leave-one-country-out transfer test
against a demographically reweighted real-diary null, output driving EnergyPlus residential archetypes,
no forecast, no model release.

**Name the one thing most likely to be wrong with this plan that none of the seventeen prompts has
asked about.** Not a generic risk. One specific, checkable thing, with the evidence that makes you
suspect it and the cheapest experiment or document that would confirm or kill it.

If you genuinely cannot find one, say so plainly rather than manufacturing something. But look hard
first: seventeen prompts written by the same person share that person's blind spots, and this section
exists precisely because we cannot see our own.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer both in plain sentences in Section G.

1. **Which of the eight contradictions did you resolve by opening a primary document, and which did you
   resolve by reasoning from what you already knew?** List them in two groups. A resolution reached by
   reasoning is not worthless, but we will treat it as a hypothesis and not as a finding, and we need to
   know which is which.

2. **Which side of each contradiction was the convenient one for this project, and did your answer
   happen to land on the convenient side?** Count them. **If you resolved seven or eight of the eight in
   the direction that suits us, stop and re-examine them**, because that pattern is far more likely to
   indicate an accommodating report than a lucky project.

Also required, as in every round of this series:

* A citation is not evidence until opened. Say which documents you opened in full.
* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always. In this prompt especially: **`NOT FOUND` is a
  successful outcome**, because it redirects us to ask the data provider instead of trusting a report.
* Every version, price, size, licence term or quantity carries the date it was checked.
* Do not state, estimate or reproduce any result of our models.
* No em dashes and no en dashes in the returned text.
