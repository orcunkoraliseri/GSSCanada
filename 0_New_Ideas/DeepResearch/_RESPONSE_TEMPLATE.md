# Response template (the external assistant must follow this exactly)

Return **one Markdown file per prompt**, named `RT<NN>_<topic>.md` (for example
`RT01_field_map_llm_occupancy_ubem.md`), saved into `5J_docs_occ/DeepResearch/`, beside the prompt it
answers.

Sections A, B, G and H are required in every answer. Sections C to F are used where the prompt asks for
them; a prompt that does not need one says so, and you then write `not applicable to this prompt`
rather than deleting the heading. Keep the headings and their letters stable, because the responses are
read side by side.

This series scouts **research topics**, not engineering facts. The fabricable class here is therefore
different from earlier series: the danger is not an invented energy intensity but an **invented paper,
an invented funding call, an invented "gap"**, or a field map that flatters the asker. The controls in
Section G are written for that.

---

## Section A. Direct answer

Three to eight sentences. What the prompt asked, answered, before any table. If the honest answer is
that the topic is crowded, that the proposed angle is already published, or that the group's assets do
not support it, **say that in the first sentence**, not at the end.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|

One row per thing you want us to be able to cite. Every row needs a source. A row whose source is
"general knowledge" does not belong in this table; put it in Section G and label it as your own
assessment. For any **count, date, deadline, funding amount, version or quantity**, `Date checked` is
mandatory.

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|

Only works you actually opened. A work you know of but could not open is listed in Section G, not here.

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|

`no` is a permitted and useful value. Do not manufacture a gap by narrowing the angle until nobody has
done exactly that; say instead that the field is occupied.

## Section E. What this changes in our planning

Bullet list of the specific decisions, framings, or dropped ideas that follow, each tied to a Section B
or C row number.

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|

Datasets, benchmarks, code, calls for papers, special-issue calls, funding-programme documents. A
programme homepage or a search results page is **not** an answer; the row reads `NO RETRIEVABLE FILE`.

## Section G. Contradictions, gaps, open questions, and your own negative controls

Bullet list. Flag every place where two sources disagree, say which one we should adopt and why, and
name what you searched for and did not find.

Then answer these questions in plain sentences, always:

1. **Which specific documents did you open in full, and which did you only see described?** List them
   separately. If the count of documents you opened in full is zero, say zero.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?** Name the
   condition. A report that cannot reach a negative under any circumstance cannot fail.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?** If the
   answer is none, explain why the field has left every angle we named untouched, because that is the
   less likely state of the world.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?** Re-check your own
   Section C against the CrossRef titles you actually retrieved before answering.

Include here any citation defect you uncover: a DOI that resolves to the wrong paper, an arXiv ID with
no artefact, a funding call whose page no longer exists.

## Section H. Full reference list

Numbered, with title, author or issuing body, year, version or edition, and URL or stable identifier.
Mark each entry Tier 1, 2 or 3. Cross-reference the numbers used in Sections B, C and F.

For each entry state explicitly whether you **read the full text**, **read only the abstract or
summary**, or **could not open it**. For every DOI, give the title that
`https://api.crossref.org/works/<DOI>` actually returned. For every arXiv entry, give the arXiv ID, the
version you read, and whether it has since appeared in a peer-reviewed venue.

No em dashes and no en dashes anywhere in the output text.
