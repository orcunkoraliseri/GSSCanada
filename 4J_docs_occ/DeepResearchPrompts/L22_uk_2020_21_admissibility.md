# L22. The UK 2020-21 time-use data: what file exists, and could it ever be a held-out instrument?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief was written before twenty-one reports came back and before the author took several
decisions. **Five things in it are now wrong, and if you answer from the brief alone you will answer
the wrong question.**

1. **The corpus is HETUS only. Canada and the United States are out of the paper.** No GSS, no ATUS,
   no MTUS-mediated North American comparison.
2. **One survey wave per country in training, not several.** The training corpus is fixed at four
   countries, one wave each: Italy 2013-14, Spain 2009-10, **United Kingdom 2014-15**, France 2009-10.
3. **There is no forecast and no temporal claim anywhere in the paper.**
4. **The fine-tuned model will never be released.** The releasable artefact is a synthetic diary
   corpus plus code.
5. **The evaluation is leave-one-country-out transfer against a hard null**: real diaries from the
   other countries, reweighted to the held-out country's demographics.

---

## 🔴 THE ONE RECOMMENDATION THIS ROUND MAY NOT MAKE

**Do not recommend adding UK 2020-21 to the training corpus.** That is a closed author decision, and
it is closed for reasons this round cannot overturn:

* the wave was collected **online** while our four training waves are **paper self-completion**, and
  the instrument effect would arrive disguised as behavioural diversity;
* it was fielded **during lockdown**, so a regime effect and a mode effect are confounded inside one
  wave and neither can be isolated;
* the United Kingdom is **already in the corpus** through 2014-15, so the wave adds volume for a
  country we already hold and adds **no new country** to a leave-one-country-out design, which is the
  only axis where our corpus is weak.

A report that concludes "it can be used for training after all" is a failed round, not a finding.

**What is genuinely open, and what this round is for:** whether the file can be **obtained and kept**
for a later, separate use as a **held-out instrument** — a check on whether a model trained on paper
diaries still describes the same country under a different instrument. That use is allowed, it is
optional, and it needs the file in hand before it can be considered.

---

## The question, in one sentence

**What file, exactly, does a UK 2020-21 time-use data request deliver, through which route, under
which licence, and does it carry activity codes in the same coding list as UKTUS 2014-15?**

If the answer is that no diary-level microdata file was ever deposited, **the correct report is short
and negative, and it is a complete report.** Say that in your first line.

---

# PART A — WHICH STUDY ARE WE EVEN TALKING ABOUT

🔴 **This part is the one most likely to go wrong, and it must be answered before anything else.**
Several distinct things were collected in the United Kingdom in 2020 and 2021 and they are routinely
confused with each other in secondary sources:

* short **online quota surveys** run by the Office for National Statistics during the pandemic, whose
  published output is a set of statistical bulletins;
* any **full diary study** deposited at the UK Data Service with its own study number;
* re-releases, teaching subsets and harmonised third-party versions of either.

**A1.** Enumerate every distinct UK time-use data collection with fieldwork in 2020 or 2021. For each
one give: the collecting institution, the fieldwork dates, the collection mode, whether a
**diary-level microdata file** was deposited anywhere, and if so the **archive and study number in
its current form**.

**A2.** For each, state plainly whether what is available is **microdata** or **published aggregate
tables only**. 🔴 A statistical bulletin is not a file. A report that treats one as the other has
answered a different question.

**A3.** Name the single study that a reader would mean by "UK 2020-21 time use", and say whether that
name is unambiguous. If it is not, say what the ambiguity is.

**A4.** Confirm or correct each of these, which we hold on weak authority and have not verified:
online collection; minimum age raised to 16; fieldwork spanning lockdown periods. Give the document
and page for each, or `NOT FOUND`.

---

# PART B — THE DECIDING FACT: THE CODING LIST

Our four training waves share one coding-list generation, which is what lets the activity field keep
**three digits**. A held-out instrument test is only interpretable if the held-out file's activity
codes can be placed against the training corpus's codes **without a crosswalk built by us**.

**B1.** Which activity coding list does the delivered file use? Name the list, its **edition year**,
and its **depth in the delivered file** (1, 2 or 3 digits). Give the codebook page.

**B2.** Is it the same list as **UKTUS 2014-15** (which is in our training corpus)? If it is not,
state exactly what differs.

**B3.** If the 2020-21 collection used a **reduced or simplified** activity list rather than the full
Eurostat list, say so explicitly and give the number of categories. 🔴 **This is the most likely
finding and it would settle the round.** A short list is not a defect in their survey and it is not a
scandal; it simply decides what we can do with the file.

**B4.** Location coding: full HETUS location list, a reduced list, or none? Number of codes, and the
codebook page.

**B5.** Co-presence: recorded as HETUS binary flags, as a single code, or not at all? Name each flag
the file carries, with its national definition. 🔴 Do not assume five. One of our four countries turned
out to field six, and we found that only by reading the layout.

**B6.** Diary mechanics: slot length in minutes, number of slots or episodes per diary, diary days per
respondent, and whether `START` and `DURATION` exist natively or must be reconstructed from slots.

**B7.** Weight variables: names, which file each sits on, and whether individual, diary-day and
household weights are all present.

---

# PART C — ROUTE, CREDENTIALS, COST

**C1.** The holding archive, the catalogue identifier in its **current** form, and the landing URL you
opened.

**C2.** The credential class on this ladder. Do not soften a tier because a form looks short:

* **Tier 0** open download, no registration.
* **Tier 1** free individual registration.
* **Tier 2** free registration requiring institutional affiliation.
* **Tier 3** written application per project, assessed.
* **Tier 4** the applicant **institution** must be pre-accredited.
* **Tier 5** secure enclave only, the file never leaves the facility.

State whether a **Canadian-based academic** can complete it, and name the step that would stop them if
one exists.

**C3.** Cost in GBP, with the date checked. Stated turnaround as published; if unpublished,
`NOT FOUND`, do not estimate.

**C4.** Is the 2020-21 file under the **same** licence class as the UKTUS 2014-15 file we already hold
a route to, or a different one? If different, say which is stricter.

---

# PART D — THE THING THAT WOULD MAKE THIS WAVE WORTH HAVING

A confounded wave is still useful **if the confound is measured rather than hidden.**

**D1.** Is the **collection mode recorded per diary or per respondent** in the delivered file, as a
variable? Name it if so.

**D2.** Are **fieldwork dates** recorded per diary, at any resolution — day, week, month, sub-wave?
Name the variable and its resolution.

🔴 **D1 and D2 are the questions this round exists to answer, after Part B.** If either variable is
present, the wave stops being a confound we must avoid and becomes a file where an instrument effect
or a lockdown period can be **conditioned on**. If both are absent, the wave is unusable for us in any
role and we will stop thinking about it. Answer both explicitly, with the variable names or with
`NOT FOUND`.

**D3.** Does the delivery allow the lockdown periods to be separated from the periods between them, on
the file alone, without our importing an external chronology?

---

# PART E — LICENCE

An earlier round established that our current agreements forbid releasing model weights or adapters,
and that the releasable artefact is a **synthetic diary corpus** under CC BY 4.0 with Apache 2.0 code.
That finding was reached for four specific agreements. **Adding this file adds an agreement.**

**E1.** Does the licence permit publication of **synthetic data generated by a model trained on that
file**? Quote the clause. If the licence is silent, say **silent**, not **permitted**. Those are
different findings and only one of them is safe.

**E2.** Does it permit the file to be **combined with microdata from other countries** under different
licences?

**E3.** Are there retention, destruction or reporting obligations that persist after the project ends?
Quote them.

🔴 **A clause forbidding release of generated output would remove the only releasable artefact this
paper has. That is a veto, not a caveat.** Report any such clause in the first line of your summary.

---

# PART F — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: four HETUS countries, one paper-diary wave each under one coding
generation, one open-weight model fine-tuned once, leave-one-country-out against a demographically
reweighted real-diary null, output driving EnergyPlus residential archetypes, no forecast, no model
release.

**Name the one thing most likely to be wrong with obtaining this file at all.** Not a generic risk.
One specific checkable thing, with the evidence that makes you suspect it and the cheapest document
that would confirm or kill it.

Three candidates we have already thought of, so do not offer any of them: the coding list, which is
Part B; the mode and lockdown confound, which is why the wave is not training data; and the fact that
a bulletin is not a microdata file, which is Part A.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all six in plain sentences in Section G.

1. **List every document you opened in full**, with its URL, separating collecting-institution
   documents from archive catalogue pages from third-party summaries. **A citation is not evidence
   until opened.**

2. **Did you at any point conclude that the file follows HETUS guidelines because the United Kingdom
   participates in HETUS?** Participation establishes what a country sent to Eurostat once. It does
   not establish what a 2020-21 collection recorded or what an archive will deliver. Say where, if
   anywhere, you made that step.

3. **Distinguish "the survey happened" from "the microdata is deposited" from "the microdata is
   obtainable by us".** State which of the three you actually verified, for each study you named in
   Part A.

4. **Count your convenient findings.** The convenient answers here are: a full diary file exists, it
   is Tier 0 to Tier 2, it is free, it uses the same coding list as 2014-15, mode is a variable,
   fieldwork date is a variable, the licence permits releasing generated data. 🔴 **If most axes came
   back convenient, stop and re-check.** State how many of the seven came back convenient and how many
   you verified against a primary document.

5. **State plainly whether your answer would change if the activity list turns out to be a reduced
   one.** If your recommendation is the same either way, your recommendation is not being driven by
   the evidence.

6. **Did you recommend adding this wave to training anywhere in your report, in any wording?** If so,
   delete it and say here that you did. That recommendation is out of scope by author decision.

Also required, as in every round of this series:

* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always. **A short negative report is an acceptable and
  expected outcome here** and will be acted on immediately.
* Every version, price, size, licence term or quantity carries the date it was checked.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware,
  our storage or our cluster. You cannot see them.
* No em dashes and no en dashes in the returned text.
