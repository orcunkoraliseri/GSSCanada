# L20. Is the Norwegian time-use file admissible to our corpus, or not?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief was written before nineteen reports came back and before the author took six
decisions. **Four things in it are now wrong, and if you answer from the brief alone you will answer
the wrong question.**

1. **The corpus is HETUS only. Canada and the United States are out of the paper.** No GSS, no ATUS,
   no MTUS-mediated North American comparison.
2. **One survey wave per country, not several.** Earlier waves are held-out validation only; newer
   waves are excluded entirely. **Do not recommend adding waves.**
3. **The corpus is currently four countries: Italy 2013-14, Spain 2009-10, United Kingdom 2014-15,
   France 2009-10.** Those four are fixed and are not the subject of this round.
4. **There is no forecast and no temporal claim anywhere in the paper.**

Everything else in the brief still holds, including the two hard constraints: **the fine-tuned model
will never be released**, and **the evaluation is leave-one-country-out transfer against a hard null**
(real diaries from the other countries, reweighted to the held-out country's demographics).

---

## The question, in one sentence

**Does the Norwegian time-use survey file that we could actually obtain carry activity codes in the
Eurostat Activity Coding List, produced by Statistics Norway, or does it carry only Statistics
Norway's own national code list?**

Everything else in this prompt is secondary to that sentence. **If the answer is that no official
ACL-coded variable is delivered, the correct report is short and negative, and it is a complete
report.**

## Why it is being asked, so you can tell a useful answer from a complete one

Our corpus is four countries, so leave-one-country-out trains on three. That is the weakest structural
feature of the design. Norway would make it four, and Norway is a genuinely hard held-out target
rather than a fifth Western or Southern European neighbour, so its value is larger than its count.

**The blocker is coding.** A previous round in this series (`RL19`) reported that the national file
uses **Statistics Norway's own classification of roughly 170 categories**, not ACL 2008, and asserted
that a documented one-to-one recode table is supplied. **We could not confirm that assertion**, and
Statistics Norway's own methodology page names no coding list at all.

This matters because a **hand-built** crosswalk from a 170-code national list to 3-digit ACL 2008 is
precisely the arbitrary one-to-many mapping that an earlier round in this series (`RL17` B3) says
cannot be defended across heterogeneous surveys. It would sit inside the training corpus, unauditable,
and it would land on the appliance-triggering step, which is the step 3-digit codes were preserved
for. We will not build one. **So Norway is admissible only if somebody else, with authority, has
already done the recode.**

🔴 **The convenient answer is "yes, Norway is obtainable and harmonised."** That answer rescues the
weakest part of our design, which is exactly why it must be tested hardest. A claim that an ACL recode
exists belongs in this report only if you can name the variable, name the document that documents it,
and give the URL of the page you opened. **Everything else is `NOT FOUND`.**

## 🔴 What is already suspect, and must be re-derived rather than repeated

`RL19` is the report that recommended Norway. **Parts of it did not survive vetting**, so do not treat
any of the following as established. Re-derive each from a primary Statistics Norway or Sikt document,
or return `NOT FOUND`.

* Its claim that a documented one-to-one recode table is provided.
* Its Sikt landing URL, given in a `study/NSD1849` form, where the current catalogue addresses studies
  by UUID.
* Its documentation citation, given as **Vaage 2012, Rapporter 2012/36**. The documentation report for
  this survey appears instead to be **Holmøy, Lillegård and Löfgren (2012)**. **Establish which report
  actually documents the 2010-11 survey, and give its correct title, number and URL.** A real author
  from the right institution attached to the wrong document is a failure class this project has been
  caught by twice.

Independently confirmed by us and **not** in dispute: the 2010-11 survey uses 10-minute intervals, two
diary days, ages 9 to 79, paper diary.

---

# PART A — THE DECIDING FACT

## A1. What the delivery actually contains

Find the **variable list or codebook of the file that a foreign academic user receives**, not the
survey description and not the Eurostat aggregate tables. Then answer:

| # | Question | Required form of answer |
|---|---|---|
| A1.1 | Is there a variable in the delivered file holding the activity in **Eurostat ACL** codes? | Variable name, code depth (2-digit or 3-digit), and the document that lists it |
| A1.2 | If yes, **who produced it** — Statistics Norway, Eurostat, the archive, or a researcher? | Named, with the document that says so |
| A1.3 | Which **edition** of the ACL: 1997/2000, 2008, 2010, 2020? | Named, with source |
| A1.4 | Is there a published **recode or correspondence table** between the Norwegian national list and the ACL? | Title, author, year, URL, and whether it is one-to-one or one-to-many |
| A1.5 | How many categories does the national list actually have, and at what depth is it released? | Number and source. `RL19` says about 170; verify or correct it |

🔴 **A1.1 and A1.2 together decide this round.** If the ACL variable exists but was produced by a
third-party researcher rather than by Statistics Norway or Eurostat, say so explicitly: that is a
different finding from an official recode and we will treat it differently.

## A2. Where the answer came from

For each row of A1, state whether it came from **a codebook you opened**, from **a methodology
report**, from **an archive catalogue page**, or from **your own inference**. An inferred coding list
is a hypothesis and we will treat it as one.

---

# PART B — THE ROUTE, ONLY IF PART A IS POSITIVE

If A1.1 is `NOT FOUND` or negative, **skip Part B entirely and say so.** Do not fill it in for
completeness. A negative Part A ends the question.

**B1.** The holding institution, the catalogue identifier in its **current** form, and the landing URL
you opened.

**B2.** The credential class on this ladder, and do not soften a tier because a form looks short:

* **Tier 0** open download, no registration.
* **Tier 1** free individual registration.
* **Tier 2** free registration requiring institutional affiliation.
* **Tier 3** written application per project, assessed.
* **Tier 4** the applicant **institution** must be pre-accredited.
* **Tier 5** secure enclave only, the file never leaves the facility.

🔴 **Tier 4 and Tier 5 are worth nothing to us here**, because they reintroduce exactly the
institutional barrier that makes the Eurostat route slow. Say so plainly rather than listing Norway
alongside reachable sources.

**B3.** Cost in NOK and EUR, with the date checked. Stated turnaround as published; if unpublished,
`NOT FOUND`, do not estimate.

**B4.** Language of the codebook and of the variable labels. This is a real cost to us and is usually
omitted from access summaries.

**B5.** File shape: relational episode file, or wide file with slot columns. Do `START` and `DURATION`
exist natively?

**B6.** Weight variables present (individual, diary day, household), and whether household linkage is
present so co-presence can be reconstructed.

**B7.** Co-presence: is it recorded as the five HETUS binary flags (alone, with partner, with
children, with other household members, with other persons), as a single code, or not at all?

**B8.** Location: is it the HETUS location list (10 to 19 stationary, 20 to 39 transport, 11 = home),
or a national location list? If national, how many codes and is there a recode?

---

# PART C — THE LICENCE QUESTION THAT DOES NOT TRANSFER

An earlier round established that our current agreements forbid releasing model weights or adapters,
and that the releasable artefact is a **synthetic diary corpus** under CC BY 4.0 with Apache 2.0 code.
That finding was reached for four specific agreements. **Adding Norway adds an agreement.**

**C1.** Does the Norwegian licence permit publication of **synthetic data generated by a model trained
on that file**? Quote the clause. If the licence is silent, say **silent**, not **permitted**. Those
are different findings and only one of them is safe.

**C2.** Does it permit the file to be **combined with microdata from other countries** under different
licences, in a pooled training corpus?

🔴 **A clause forbidding release of generated output would remove the only releasable artefact this
paper has. That is a veto, not a caveat.** Report any such clause in the first line of your summary.

---

# PART D — THE JUDGEMENT

**D1.** Given your Part A finding, is Norway admissible **without any crosswalk built by us**? One
word, then the evidence.

**D2.** If a crosswalk would be required, is there a **published, citable** one by a named author or
institution that other studies have used, so that it would be a citation rather than an invention?
Name the studies that used it. If nobody has published one, say so — that is the answer.

**D3.** Is there any **other** country in the HETUS 2010 round that ships an official ACL-coded file
through a Tier 0 to Tier 3 national route? `RL19` says none, and we accept that; **name the single
strongest counter-example if one exists**, otherwise confirm the negative in one sentence and move on.

---

# PART E — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: four HETUS countries, one paper-diary wave each under one coding
generation, one open-weight model fine-tuned once, leave-one-country-out against a demographically
reweighted real-diary null, output driving EnergyPlus residential archetypes, no forecast, no model
release.

**Name the one thing most likely to be wrong with admitting Norway specifically.** Not a generic risk.
One specific checkable thing, with the evidence that makes you suspect it and the cheapest document
that would confirm or kill it.

Two candidates we have already thought of, so do not offer either as your answer: the coding list
question, which is Part A, and the fact that a national archive may ship something other than the
Eurostat-harmonised file.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all five in plain sentences in Section G.

1. **List every document you opened in full**, with its URL, separating Statistics Norway documents
   from archive catalogue pages from third-party summaries. **A citation is not evidence until
   opened.**

2. **Did you at any point conclude that Norway uses the HETUS guidelines because Norway appears in a
   Eurostat time-use table?** Appearing in a Eurostat aggregate table means Eurostat received
   something. It does not establish what a national archive will send us. Say where, if anywhere, you
   made that step.

3. **Count your convenient findings.** The convenient answers here are: obtainable, cheap, fast,
   ACL-coded, official recode exists, licence permits release of generated data. 🔴 **If most axes came
   back convenient, stop and re-check.** State how many of the six came back convenient and how many
   you verified against a primary document.

4. **Did you find the recode table itself, or only a statement that one exists?** These are different
   and only one of them settles the round. If only a statement, name the document that makes it and
   say whether that document is Statistics Norway's own.

5. **State plainly whether your answer would change if the recode turns out not to exist.** If your
   recommendation is the same either way, your recommendation is not being driven by the evidence.

Also required, as in every round of this series:

* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always. **A short negative report is the expected outcome
  here** and will be acted on immediately.
* Every version, price, size, licence term or quantity carries the date it was checked.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware,
  our storage or our cluster. You cannot see them.
* No em dashes and no en dashes in the returned text.
