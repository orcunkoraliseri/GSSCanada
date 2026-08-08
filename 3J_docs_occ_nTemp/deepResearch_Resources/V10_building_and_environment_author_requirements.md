# V10. Everything Building and Environment requires of a submission, from the journal's own pages

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H).

---

## Why we are asking

The 3J manuscript is finished and targeted at **Building and Environment** (Elsevier). It is being
prepared entirely from what is on disk, because nobody in this project has ever opened the journal's
Guide for Authors. Every submission-shaping number currently in the manuscript is therefore an
assumption, and at least one of them is already known to be a guess.

This is not a hypothetical risk. In the immediately preceding paper of this line, the abstract was
cut to satisfy a **200-word limit that no source ever stated**. The limit was believed, acted on, and
only later found to have no origin. The abstract of this manuscript is currently **272 words** and
the same mistake is one careless step away.

Three further facts make this prompt urgent rather than routine.

1. **This author line has already been rejected by Building and Environment once**, for the earliest
   paper of the series, and the stated reason was insufficient quality. Whatever the journal states
   about scope, article types and expectations is therefore not boilerplate to skim; it is the bar
   the paper has already failed once.
2. **Five of the eleven main figures are at 140 dpi.** The paper before this one went into review
   with 13 of 16 figures below 600 dpi. We need the journal's actual stated minimum, per artwork
   type, before deciding what to regenerate.
3. **We do not know whether the review is anonymized.** If it is, the manuscript needs a blinded
   build, which is a different output file, not an edit.

Answer only from the journal's and the publisher's own pages. Where a page does not state something,
the correct answer is that it does not state it.

---

## What we need

**Part A. Manuscript limits, stated exactly.**

1. The **abstract word limit** for a Research Paper in Building and Environment. Quote the sentence
   that states it and give the URL. If the Guide for Authors does not state a limit, say
   **NOT STATED** in those words. Do not substitute the limit of another Elsevier journal, and do not
   infer one from published papers.
2. The **highlights** requirement: how many bullets, the maximum characters per bullet, whether they
   are mandatory, and the file format expected.
3. Any **total manuscript length** limit, in words or pages, and whether it is a hard cap or guidance.
   State whether it counts references, tables and captions.
4. The available **article types** (Research Paper, Review, Short Communication, and any others) with
   the distinguishing criteria and any per-type limits. Say which type a 12,000-word original
   modelling study with 11 figures and 7 tables should be submitted as.
5. The **title length** limit and any restriction on the title's form (no abbreviations, no formulae,
   and so on).
6. The **keywords** count.

**Part B. Figures, tables and artwork.**

7. The **minimum resolution** the journal requires, broken out by artwork class as Elsevier states it:
   line art, halftone, and combination art. Give the number for each in dpi and quote the source.
8. Whether there is a **limit on the number of figures** or tables in a Research Paper, and if so what
   it is. If there is no limit, say so explicitly rather than leaving it out.
9. The **accepted file formats** for figures, the preferred one, and whether vector formats are
   preferred over raster for plots and schematics.
10. Whether figures must be supplied as **separate files** or embedded in the manuscript at
    submission, and what the rule is at revision versus first submission.
11. **Colour**: whether colour figures are free online, whether there is any charge for colour in
    print, and whether the journal still has a print edition.
12. The **graphical abstract** specification: whether it is required or optional, the pixel
    dimensions, minimum resolution, and the file format.
13. Figure **caption placement** and numbering conventions, and whether supplementary figures must be
    numbered in a separate series.

**Part C. Review model and blinding.**

14. Does Building and Environment use **single-anonymized**, **double-anonymized**, or open review?
    Quote the statement.
15. If double-anonymized: exactly what must be removed from the manuscript file, whether a separate
    title page file is required, and whether self-citations must be masked.
16. Whether **suggested reviewers** are requested or required, how many, and what exclusion rules
    apply (same institution, recent co-authors, and so on).
17. Whether a **cover letter** is required, what it should contain, and whether it is seen by
    reviewers or only by the editor.

**Part D. Declarations, and the things that block a submission at the last click.**

18. The **Declaration of Generative AI in Scientific Writing** statement: whether it is required, the
    exact wording the publisher prescribes, and where in the manuscript it goes.
19. **CRediT** author-contribution requirement: mandatory or optional, and the accepted role
    vocabulary.
20. The **Data Availability Statement**: required or optional, the accepted forms, and whether a
    statement of the form "data are available on request" is accepted.
21. Whether **ORCID is mandatory** for the corresponding author, for all authors, or optional.
22. **Declaration of Competing Interest**: the required form and whether a null declaration must
    still be submitted.
23. **Funding** statement formatting requirements.
24. **Ethics / informed consent**: what a study using anonymized national survey microdata under a
    university data agreement is expected to declare, if anything.
25. The **reference style** name, whether numbered or author-date, and whether there is a limit on the
    number of references.
26. Accepted **submission file formats** (Word, LaTeX, PDF) and whether a single combined PDF is
    acceptable at first submission.
27. Whether **preprints** are permitted, and whether posting one affects consideration.

**Part E. Scope, editors, and cost.**

28. The journal's **aims and scope** statement, quoted. Then state plainly whether a paper on
    survey-driven multi-channel occupancy modelling for mixed-use building energy simulation sits
    inside it, and name the part of the scope statement it sits under.
29. The **editorial board**: the Editor-in-Chief and the subject editors, with affiliations. Flag any
    editor at Concordia University or with a recent co-authorship with the named authors, because a
    conflict of that kind was found and acted on in the previous paper of this line.
30. **Open access and cost**: the article publishing charge for gold open access, whether a
    subscription route at zero cost to the author exists, and **whether Building and Environment is
    covered by the Canadian Research Knowledge Network (CRKN) Elsevier read-and-publish agreement for
    Concordia University authors.** The equivalent question for the previous paper's venue was
    answered wrongly by assumption and cost a real decision; check the CRKN journal list itself, not a
    summary of it.
31. Any stated **time to first decision** and whether the journal publishes a desk-rejection rate.
32. Whether the journal states any **desk-rejection criteria** explicitly (scope, formatting, English
    language, similarity index).

---

## Named leads

The Building and Environment Guide for Authors on sciencedirect.com and on elsevier.com; the journal's
homepage, aims-and-scope, and editorial-board pages; Elsevier's shared author-policy pages, in
particular the artwork instructions ("Electronic artwork" / "Preparing your artwork"), the
generative-AI policy page, the CRediT page, the research-data policy page, and the competing-interests
page; the Elsevier Editorial Manager submission-step help pages for this journal; the CRKN Elsevier
agreement pages and Concordia University Library's own open-access agreement listing; Scopus and JCR
only for descriptive metrics, and only if the numbers are quoted from the source page.

---

## Deliverable

Section A of your answer must be **one table, one row per numbered item above**, with the columns:

`item | what the journal states | STATED or NOT STATED | source URL | the quoted sentence`

Rules for that table, and they are the point of this prompt:

- **`NOT STATED` is a correct and valuable answer.** An item the guide is silent about must be marked
  `NOT STATED`, not filled with the norm for Elsevier journals generally and not filled from another
  journal. This project has already been damaged once by a plausible number with no source.
- **Every `STATED` row must carry a quoted sentence and the URL it came from.** A row with a value and
  no quotation is treated as not answered.
- Do not merge two questions into one row. If item 7 asks for three resolution numbers, give three.

Then, still in Section A:

1. A short **blocking list**: the items where the manuscript as described above is currently out of
   compliance, most severe first, with what would have to change.
2. A one-line answer to each of these three, because they are what the next work session acts on:
   **(a)** is 272 words over the abstract limit, and by how much; **(b)** is 11 main figures plus a
   graphical abstract over any stated figure limit; **(c)** must a blinded manuscript be prepared.
3. If any part of the Guide for Authors could not be reached, say which part and why, rather than
   filling the gap.

Rules restated, because every previous round in this project needed them:

- A page is not evidence until it has been opened. Report what you opened.
- `NOT FOUND` beats an invented number, an invented limit, or an invented policy.
- Keep the journal's own statements strictly separate from your own commentary, and label which is
  which.
- No em dashes and no en dashes anywhere in the returned text.
