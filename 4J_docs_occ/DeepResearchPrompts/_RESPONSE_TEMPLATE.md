# Response template (the external assistant must follow this exactly)

Return **one Markdown file per prompt**, named `RL<NN>_<topic>.md` (for example
`RL01_hetus_microdata_access.md`), saved into `4J_docs_occ/DeepResearchPrompts/`, beside the prompt it
answers.

Sections A, B, G and H are required in every answer. Sections C to F are used where the prompt asks for
them; a prompt that does not need one says so, and you then write `not applicable to this prompt`
rather than deleting the heading. Keep the headings and their letters stable, because the responses are
read side by side.

---

## Section A. Direct answer

Three to eight sentences. What the prompt asked, answered, before any table. If the honest answer is
that the evidence does not settle it, or that the plan as described will not work, **say that in the
first sentence**, not at the end.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|

One row per thing you want us to be able to cite. Every row needs a source. A row whose source is
"general knowledge" does not belong in this table; put it in Section G and label it as your own
assessment.

For any **version, price, size, licence term, deadline or quantity**, the `Date checked` column is
mandatory, because all of them rot.

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|

Be conservative. `stop` is a permitted and sometimes correct value. `design change` requires you to
name the alternative, not merely to object.

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|

Use master brief section 4. If a recommendation implies hardware we do not have, say so in this table
rather than leaving it implicit.

## Section E. What this changes in the write-up

Bullet list of the specific sentences, caveats, limitations or method-section claims our documents
should carry as a result, each tied to a Section B row number.

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|

A programme homepage, a search results page or a news release is **not** an answer; the row reads
`NO RETRIEVABLE FILE` instead.

## Section G. Contradictions, gaps, open questions, and your own negative controls

Bullet list. Flag every place where two sources disagree, say which one we should adopt and why, and
name what you searched for and did not find.

Then answer these two questions in plain sentences, always:

1. **Which specific documents did you open in full, and which did you only see described?** List them
   separately. If the count of documents you opened in full is zero, say zero.
2. **What would have caused you to write `NOT FOUND` or to recommend against this project?** Name the
   condition. A report that cannot reach a negative under any circumstance is a report that cannot
   fail, and we have received several.

Include here any citation defect you uncover: a DOI that resolves to the wrong paper, an identifier
that does not exist, a URL that 404s, a model name that has no artefact behind it. We have been burned
by all of these and we want them named.

## Section H. Full reference list

Numbered, with title, author or issuing body, year, version or edition, and URL or stable identifier.
Mark each entry Tier 1, 2 or 3. Cross-reference the numbers used in Sections B and F.

For each entry state explicitly whether you **read the full text**, **read only the abstract or
summary**, or **could not open it**. For every DOI, give the title that
`https://api.crossref.org/works/<DOI>` actually returned. For every arXiv entry, give the arXiv ID, the
version you read, and whether it has since appeared in a peer-reviewed venue.
