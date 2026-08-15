# L23. The Italian 2022-23 time-use data: is it released, and can ACL 2020 be placed against ACL 2008?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief was written before twenty-one reports came back and before the author took several
decisions. **Five things in it are now wrong, and if you answer from the brief alone you will answer
the wrong question.**

1. **The corpus is HETUS only. Canada and the United States are out of the paper.** No GSS, no ATUS,
   no MTUS-mediated North American comparison.
2. **One survey wave per country in training, not several.** The training corpus is fixed at four
   countries, one wave each: **Italy 2013-14**, Spain 2009-10, United Kingdom 2014-15, France 2009-10.
3. **There is no forecast and no temporal claim anywhere in the paper.**
4. **The fine-tuned model will never be released.** The releasable artefact is a synthetic diary
   corpus plus code.
5. **The evaluation is leave-one-country-out transfer against a hard null**: real diaries from the
   other countries, reweighted to the held-out country's demographics.

---

## 🔴 THE ONE RECOMMENDATION THIS ROUND MAY NOT MAKE

**Do not recommend adding Italy 2022-23 to the training corpus.** That is a closed author decision:

* the wave uses a **different activity coding list generation** from our four training waves, and the
  three-digit activity field only survives because all four share one generation;
* it was collected at least partly by **web or app**, while our four are paper self-completion, and
  digital diaries record more short fragments and fewer secondary activities than paper booklets;
* **Italy is already in the corpus** through 2013-14, so the wave adds volume for a country we already
  hold and **no new country** to a leave-one-country-out design.

A report that concludes "it can be used for training after all" is a failed round, not a finding.

**What is genuinely open, and what this round is for:** whether the file **exists, is released, and
can be obtained and kept** for a later, separate use as a **held-out instrument** — a check on whether
a model trained on paper diaries still describes the same country under a different instrument and a
newer coding list. That use is allowed, it is optional, and it needs the file in hand.

---

## The question, in one sentence

**Has the Italian 2022-23 time-use microdata actually been released, and does an official
correspondence exist between its activity coding list and the one our Italian training wave uses?**

If the microdata has not been released, **the correct report is short and negative, and it is a
complete report.** Say that in your first line, with the date you checked.

---

# PART A — RELEASE STATUS, WHICH IS THE FIRST THING THAT CAN END THE ROUND

**A1.** Name the survey exactly as the collecting institution names it, in Italian, with its fieldwork
period.

**A2.** State, with the date checked and the URL you opened, whether a **diary-level microdata file**
has been released, in any form. Distinguish between:

* published **aggregate tables or statistical reports**;
* a **public-use or research file** that a foreign academic can request;
* a file available only inside a **secure enclave**;
* **announced but not yet released**.

🔴 **A report that finds published tables and reports the survey as available has failed the round.**
Our Spanish round already caught a report presenting a dead catalogue URL as a source read in full.

**A3.** If it is not released, is a release date **published** by the institution? Quote it with its
URL, or return `NOT FOUND`. Do not estimate.

**A4.** We already hold the **2013-14** Italian file from an earlier paper in this series. State what
has changed between the 2013-14 delivery and the 2022-23 delivery, if anything, in: file shape,
variable naming convention, request route, and licence.

---

# PART B — THE DECIDING FACT: CAN THE NEW CODING LIST BE PLACED AGAINST THE OLD ONE

Our four training waves share one coding-list generation. A held-out instrument test is only
interpretable if the held-out file's activity codes can be placed against the training corpus's codes
**without a crosswalk built by us**. We will not hand-build one: an arbitrary one-to-many mapping
inside the evaluation is the same defect we refuse inside the training corpus.

**B1.** Which activity coding list does the 2022-23 file use? Name the list, its **edition year**, and
its **depth in the delivered file** (1, 2 or 3 digits), with the codebook page.

**B2.** 🔴 **Does an official correspondence table exist between that edition and the 2008 or 2010
edition?** Answer with:

* the title, author institution, year and URL of the table itself, not of a document that mentions it;
* whether it is **one-to-one** or **one-to-many** at the depth the file is delivered;
* who produced it: Eurostat, the national institute, an archive, or a third-party researcher.

**Naming a document that says a correspondence exists is not the same as finding the correspondence.**
Say which of the two you have. This exact distinction decided an earlier round in this series, and the
report that blurred it was wrong.

**B3.** If no official correspondence exists, say so in one sentence and **stop Part B there.** That is
a complete and useful answer.

**B4.** Location coding: which list, how many codes, and does it differ from the list used in 2013-14?
🔴 Do not describe it as "10 to 19 stationary, 20 to 39 transport". A report in this series said that
and we found a public-transport code above 39 in the first file we opened.

**B5.** Co-presence: name each flag the file carries, with its national definition. 🔴 Do not assume
five. One of our four countries fields six, and we found that only by reading the layout.

**B6.** Diary mechanics: slot length, slots or episodes per diary, diary days per respondent, minimum
age, and whether `START` and `DURATION` exist natively.

**B7.** Weight variables: names, which file each sits on, and whether individual, diary-day and
household weights are all present.

---

# PART C — MODE, AND WHY IT COULD MAKE THIS FILE VALUABLE INSTEAD OF UNUSABLE

A mixed-mode wave is a problem when the mode is hidden and an **experiment** when it is recorded.

**C1.** Which collection modes were used, and in what proportions? Give the numbers the institution
publishes, with the page.

**C2.** 🔴 **Is the mode recorded per diary or per respondent, as a variable in the delivered file?**
Name the variable, or return `NOT FOUND`. This is the single most valuable question in this prompt
after Part B: a mode variable turns a confound we must avoid into an effect we could measure on
somebody else's data rather than assert from the literature.

**C3.** Was any part of the 2022-23 wave collected on **paper**? If a paper subsample exists and is
identifiable in the file, say how large it is.

**C4.** Does the institution publish its **own** analysis of the mode effect on diary content — number
of episodes per day, secondary activity reporting, short-episode capture? Title, page, URL. If it does
not, say `NOT FOUND` rather than reasoning about what the effect probably is.

---

# PART D — ROUTE, CREDENTIALS, COST

**D1.** The holding institution, the request route, the identifier of the file in its current form, and
the landing URL you opened.

**D2.** The credential class on this ladder. Do not soften a tier because a form looks short:

* **Tier 0** open download, no registration.
* **Tier 1** free individual registration.
* **Tier 2** free registration requiring institutional affiliation.
* **Tier 3** written application per project, assessed.
* **Tier 4** the applicant **institution** must be pre-accredited.
* **Tier 5** secure enclave only, the file never leaves the facility.

State whether a **Canadian-based academic** can complete it, and name the step that would stop them if
one exists. 🔴 **Tier 4 and Tier 5 are worth nothing to us here**, because they reintroduce exactly the
institutional barrier that makes the Eurostat route slow.

**D3.** Cost in EUR, with the date checked. Stated turnaround as published; if unpublished,
`NOT FOUND`.

**D4.** Language of the codebook and of the variable labels.

---

# PART E — LICENCE

An earlier round established that our current agreements forbid releasing model weights or adapters,
and that the releasable artefact is a **synthetic diary corpus** under CC BY 4.0 with Apache 2.0 code.
**Adding this file adds an agreement.**

**E1.** Does the licence permit publication of **synthetic data generated by a model trained on that
file**? Quote the clause. If the licence is silent, say **silent**, not **permitted**.

**E2.** Does it permit the file to be **combined with microdata from other countries** under different
licences?

**E3.** Retention, destruction or reporting obligations that persist after the project ends. Quote
them.

🔴 **A clause forbidding release of generated output would remove the only releasable artefact this
paper has. That is a veto, not a caveat.** Report it in the first line of your summary.

---

# PART F — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: four HETUS countries, one paper-diary wave each under one coding
generation, one open-weight model fine-tuned once, leave-one-country-out against a demographically
reweighted real-diary null, output driving EnergyPlus residential archetypes, no forecast, no model
release.

**Name the one thing most likely to be wrong with obtaining this file at all.** Not a generic risk.
One specific checkable thing, with the evidence that makes you suspect it and the cheapest document
that would confirm or kill it.

Three candidates we have already thought of, so do not offer any of them: the coding list generation,
which is Part B; the collection mode, which is Part C; and the possibility that the file is not
released yet, which is Part A.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all six in plain sentences in Section G.

1. **List every document you opened in full**, with its URL, separating institution documents from
   catalogue pages from third-party summaries. **A citation is not evidence until opened.**

2. **Did you at any point conclude something about this file because Italy participates in HETUS or
   because the HETUS guidelines say so?** Restating the guidelines per country, as though codebooks
   had been read, is the specific failure of an earlier round in this series. Say where, if anywhere,
   you made that step.

3. **Distinguish "the survey happened" from "the microdata is released" from "the microdata is
   obtainable by us".** State which of the three you actually verified, and on which date.

4. **Count your convenient findings.** The convenient answers here are: the file is released, it is
   Tier 0 to Tier 3, it is free, an official coding correspondence exists, it is one-to-one, mode is a
   variable, a paper subsample exists, the licence permits releasing generated data. 🔴 **If most axes
   came back convenient, stop and re-check.** State how many of the eight came back convenient and how
   many you verified against a primary document.

5. **State plainly whether your answer would change if no official coding correspondence exists.** If
   your recommendation is the same either way, your recommendation is not being driven by the
   evidence.

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
