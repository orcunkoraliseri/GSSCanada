# L19. Can the corpus be widened past four countries **without** a Eurostat licence?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief was written before eighteen reports came back and before the author took six
decisions. **Four things in it are now wrong, and if you answer from the brief alone you will answer
the wrong question.**

1. **The corpus is HETUS only. Canada and the United States are out of the paper.** No GSS, no ATUS,
   no MTUS-mediated North American comparison. Do not propose one, and do not treat the Canadian
   inventory in `RL17` as live.
2. **One survey wave per country, not several.** The multi-wave design in the brief and in `L17` was
   examined and rejected. Earlier waves are held-out validation only; newer waves are excluded
   entirely. **Do not recommend adding waves.** See the admissibility screen in Part B for why.
3. **The corpus is currently four countries: Italy 2013-14, Spain 2009-10, United Kingdom 2014-15,
   France 2009-10.** These four are fixed and are not up for revision in this round.
4. **There is no forecast and no temporal claim anywhere in the paper.**

Everything else in the brief still holds, including the two hard constraints that shape this prompt:
**the fine-tuned model will never be released**, and **the evaluation is leave-one-country-out
transfer against a hard null** (real diaries from the other countries, reweighted to the held-out
country's demographics).

---

## The question, in one sentence

**Which other countries in the HETUS 2010 round hold time-use microdata that we can actually obtain
through a national route, and that is admissible to our pipeline unchanged?**

## Why it is being asked, so you can tell a useful answer from a complete one

With four countries, leave-one-country-out trains on **three**. That is the weakest structural feature
of the whole design and it is written into the paper as a limitation. Two routes could widen it:

* **Track A**, the Eurostat Scientific Use File, would give roughly seventeen countries in one step
  with no harmonisation change at all, because our four waves *are* the HETUS 2010 round. It requires
  the applicant institution to hold **Eurostat research-entity recognition**. Concordia does not, the
  application has not been filed, and the outcome is not ours to control.
* **National routes**, country by country, from the national statistical institute or a national data
  archive. Slower per country, but each one is independent, and **none of them depends on Eurostat
  saying yes.**

**This prompt is entirely about the second route.** Track A is being pursued in parallel and is not
your subject. Do not spend the report advising us to file the Eurostat application; we know.

🔴 **The convenient answer is "yes, plenty of countries, freely available."** That answer would rescue
the weakest part of our design, which is exactly why it should be the one you test hardest. A country
belongs on the obtainable list only when you can name the archive, the study number or catalogue
identifier, the credential required, the cost, and the URL you opened. **Everything else is
`NOT FOUND`, and `NOT FOUND` for eleven of thirteen countries is a perfectly acceptable report.**

---

# PART A — THE INVENTORY

## A1. Establish the population of candidates first

List the countries that participated in the **HETUS 2010 round** (round 2, fieldwork approximately
2008 to 2015). Give the number and the source document. Reports in this series have quoted "17
countries" and "18 countries" for this round; **settle which, and say what the discrepancy is** —
almost certainly one of them counts a country whose file Eurostat holds but does not distribute, or
counts a non-member participant.

Then remove our four. **The remainder is the candidate set for the rest of this prompt.**

## A2. One row per candidate country

| Field | What is required |
|---|---|
| Country | |
| Survey name, in the national language and in English | |
| Fieldwork years of the round-2 wave | |
| **Holding institution** | The NSI or the national archive that actually distributes the file, not Eurostat |
| **Catalogue or study identifier** | The number a user quotes when requesting it. If none exists, say so |
| **Landing URL** | The page you opened. Not a search result, not a homepage |
| **Credential class** | See the ladder in A3 |
| **Cost** | In the local currency and in EUR, with the date checked |
| **Stated turnaround** | As published by the holder. If unpublished, `NOT FOUND` — do not estimate |
| **Language of the codebook** | This is a real cost to us and is usually omitted from access summaries |
| Approximate diary-day count | With its source |

**A country with no landing URL you personally opened does not go in this table.** Put it in the
`NOT FOUND` list in A4 instead.

## A3. Classify every candidate on this credential ladder

The ladder is the point of the exercise, because it is what decides whether a country is reachable
this year:

* **Tier 0 — open download.** No registration of any kind. (Spain's INE is our existing example.)
* **Tier 1 — free registration by an individual researcher.** Click-through or email confirmation.
* **Tier 2 — free registration requiring institutional affiliation**, granted more or less
  automatically to a university address.
* **Tier 3 — a written application per project**, assessed, with a stated turnaround.
* **Tier 4 — the applicant institution must be pre-recognised or accredited**, by the NSI or by a
  national accreditation scheme.
* **Tier 5 — physical or remote secure facility only.** The file never leaves the enclave.

🔴 **Tier 4 and Tier 5 countries are worth as little to us as Track A is**, because they reintroduce
exactly the institutional barrier the national route exists to avoid. Say so plainly for each one
rather than listing them alongside the reachable ones. **Do not soften a Tier 4 into a Tier 3 because
the form looks short.** If accreditation of the institution is required anywhere in the chain, it is
Tier 4.

## A4. The countries you could not resolve

A plain list, one line each, saying what you looked for and where you stopped. This list is useful to
us and will be acted on: it tells us which NSIs to email directly. **A short obtainable list plus an
honest unresolved list is a better report than a long obtainable list.**

---

# PART B — THE ADMISSIBILITY SCREEN

Access is only half the question. A file we can download but cannot use costs us more than one we
never found, because we find out late.

**For every country you placed at Tier 0 to Tier 3 in Part A, answer all seven of these.** For
countries at Tier 4 and above, answer them only if the documentation is public.

| # | Screen | Why it is disqualifying |
|---|---|---|
| **B1** | **Diary slot length.** 10 minutes, 15 minutes, or something else | 🔴 **A 15-minute file is inadmissible.** Our constrained decoder is a tally automaton over durations that are multiples of 10 summing to 1440. A 15-minute file would have to be re-quantised by up to five minutes per episode boundary, and that error lands directly on the dwell-time and transition gates. This is the screen that killed UK 2000-01 |
| **B2** | **Activity coding list edition.** ACL 1997/2000, ACL 2008, ACL 2010, ACL 2020, or a national list | 🔴 Our four waves share **one coding generation** and that is what lets our records keep **3-digit** activity codes. A country on ACL 2000 or ACL 2020 forces 2-digit pooling on the whole corpus, and 2-digit codes starve the appliance mapping in Step 9. **This is not a merge inconvenience; it is a downstream capability we would lose** |
| **B3** | **Coding depth actually released.** Full 3-digit, or truncated to 2-digit in the public file | A file coded at 3 digits but **released** at 2 digits fails for the same reason as B2, and access summaries almost never mention it. Check the codebook, not the survey description |
| **B4** | **Collection mode.** Paper self-completion booklet, web, app, telephone recall, or interviewer-assisted | Our four waves are **all paper self-completion**. Web and app diaries capture more short fragments and fewer secondary activities; a mode change arrives disguised as behavioural diversity, which is the failure mode we can least easily see |
| **B5** | **Diary days per respondent, and which days** | Our corpus mixes one-day and two-day designs already. We need to know, not to exclude |
| **B6** | **Minimum age, and whether children's diaries are included** | Changes the population the model is conditioned on. State the age and whether proxy or parent-completed diaries are in the file |
| **B7** | **File shape and whether `START` and `DURATION` exist natively** | Relational episode file, or a wide file with slot columns to be reconstructed into episodes. Both are parseable; we need to know which, per country, before writing the reader |

Also give, per country: **the weight variables present** (individual, diary-day, household), and
whether the public file carries the **household linkage** that lets us reconstruct co-presence.

🔴 **State explicitly, per country, whether each of these seven came from the codebook, from the
methodology report, or from your own inference.** An inferred slot length is a hypothesis. We will
treat it as one.

---

# PART C — TWO LICENCE QUESTIONS THAT DO NOT TRANSFER FROM WHAT WE ALREADY KNOW

`RL10` established that our current agreements forbid releasing model weights or adapters, and that the
releasable artefact is the **synthetic diary corpus** under CC BY 4.0 with Apache 2.0 code. That
finding was reached for four specific agreements. **Adding a country adds an agreement, and the answer
does not carry over.**

**C1.** For each Tier 0 to Tier 3 country: does its licence permit the publication of **synthetic data
generated by a model trained on that file**? Quote the clause. The relevant language is usually about
derived works, statistical outputs, or the disclosure of individual records. If the licence is silent,
say **silent** rather than **permitted** — those are different findings and only one of them is safe.

**C2.** For each: does the licence permit the file to be **combined with microdata from another
country** under a different licence? Some NSI end-user licences restrict linkage or matching with other
datasets in terms broad enough to catch a pooled training corpus.

🔴 **A single country whose licence forbids releasing generated output would remove the only
releasable artefact this paper has.** That is a veto, not a caveat, and it is worth more to us than
three additional countries. Report any such clause in the first line of your Section A summary.

---

# PART D — THE THREE QUESTIONS THAT DECIDE WHETHER THIS IS WORTH DOING AT ALL

Short answers, but do not skip them. They are the reason the round was commissioned.

**D1. How many countries would actually change the design?** We have four. Leave-one-country-out
currently trains on three. Is there published evidence on how the number of source domains affects
cross-domain generalisation for this class of problem, and is the useful gain at five, at seven, at
ten? If the honest answer is that nobody has measured it for tabular or sequence transfer at this
scale, say so — **that itself decides the question**, because it means the argument for expansion is
qualitative and we should weigh it against months of acquisition work.

**D2. Is there a country whose inclusion would be worth more than its count?** Our four are Western and
Southern European, which limitation C4 names as a weakness: leave-one-out over four neighbours is a
gentle test. A **Nordic** country (different daily rhythm, different labour participation, different
daylight) or a **Central or Eastern European** one would be a harder held-out target than a fifth
neighbour. Rank the reachable candidates by **how much they would stress the transfer claim**, not by
how easy they are to get. **Name the single best one and defend it.**

**D3. What is the cheapest walkable path to one additional country?** One country, named, with the
literal sequence of steps: this URL, this form, this credential, this file, this codebook language,
this many weeks. **A walkable path for one country is worth more to us than a survey of thirteen.**
This project has repeatedly found that a retrieval route we can execute beats a table we have to
verify.

---

# PART E — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: four HETUS countries, one paper-diary wave each under one coding
generation, one open-weight model fine-tuned once, leave-one-country-out against a demographically
reweighted real-diary null, output driving EnergyPlus residential archetypes, no forecast, no model
release, and a proposal to widen the corpus through national routes rather than Eurostat.

**Name the one thing most likely to be wrong with the expansion plan specifically.** Not a generic
risk. One specific checkable thing, with the evidence that makes you suspect it and the cheapest
document or test that would confirm or kill it.

One candidate we have already thought of, so do not offer it as your answer: that national files
distributed by NSIs may differ from the Eurostat-harmonised versions of the same survey, so that
"HETUS country" and "file harmonised to HETUS" are not the same object. **If that is true, say so with
evidence, because it would change what Part A even means** — but find us a second one.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all four in plain sentences in Section G.

1. **How many candidate countries did you place at Tier 0 to Tier 2, and for how many of those did you
   personally open the landing page?** Give both numbers. If the second is smaller than the first, the
   difference is a list of guesses and we need to see it.

2. **Count the convenient answers.** For each country, the convenient finding is: obtainable, cheap,
   fast, 10-minute slots, ACL 2008 or 2010, paper diary, licence permits release. 🔴 **If most of your
   countries came back convenient on most axes, stop and re-check**, because our four countries were
   themselves selected partly for these properties and it would be surprising for the rest of the
   round to match them by accident.

3. **Which screens in Part B did you answer from a codebook you opened, and which from a survey
   description or a methodology summary?** Two lists. A slot length taken from a survey description is
   the single most common way a 15-minute file gets onto an admissible list.

4. **Did you at any point infer that a country uses the HETUS guidelines because it appears in a
   Eurostat table?** Appearing in a Eurostat aggregate table means Eurostat received something. It does
   not establish the coding list edition, the slot length, or the mode of the file a national archive
   will send us. Say where, if anywhere, you made that step.

Also required, as in every round of this series:

* A citation is not evidence until opened. Say which documents you opened in full.
* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always. In this prompt especially: a short obtainable list
  with an honest unresolved list redirects us to email the right NSIs, which is a real outcome.
* Every version, price, size, licence term or quantity carries the date it was checked.
* Do not state, estimate or reproduce any result of our models.
* No em dashes and no en dashes in the returned text.
