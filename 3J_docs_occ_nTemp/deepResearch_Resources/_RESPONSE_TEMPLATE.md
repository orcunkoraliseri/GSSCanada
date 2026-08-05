# Response template (the external assistant must follow this exactly)

Return **one Markdown file per prompt**, named `RV<NN>_<topic>.md` (for example
`RV01_prototype_eui_by_climate_zone.md`), saved into
`3J_docs_occ_nTemp/deepResearch_Resources/`, beside the prompt it answers.

Sections A, B, G and H are required in every answer. Sections C to F are used where the prompt asks
for them; a prompt that does not need one says so, and you then write `not applicable to this prompt`
rather than deleting the heading. Keep the headings and their letters stable, because the responses
are read side by side.

---

## Section A. Direct answer

Three to eight sentences. What the prompt asked, answered, before any table. If the honest answer is
that the evidence does not settle it, say that here in the first sentence rather than at the end.

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|

One row per number you want us to be able to cite. A finding with no number does not go in this table,
it goes in Section G. Convert every EUI to kWh/m2.yr and show the arithmetic in the row note below the
table.

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|

Channels are residential, office, retail and hotel (master brief section 2). Say plainly where a
figure covers a whole building rather than one channel, because our gates score per channel.

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|

Be conservative. A band change requires external sources for **each endpoint separately** and must
never be motivated by our own failing results. If the evidence is suggestive but not sufficient,
the honest classification is `caveat only`, and you should say so.

## Section E. What this changes in the write-up

Bullet list of the specific sentences, caveats or table footnotes our documents should carry as a
result of this research, each tied to a Section B row number.

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|

State the tolerance as a range or percentage, and say what would count as a **failure** rather than a
difference. If you conclude no defensible target can be set from the available sources, write that and
explain what document would settle it.

## Section G. Contradictions, gaps and open questions

Bullet list. Flag every place where two Tier 1 or Tier 2 sources disagree, state which one we should
adopt and why, and name what you searched for and did not find. A clean `NOT FOUND` with the search
terms is more useful to us than a substituted number.

Include here any citation defect you uncover: a DOI that resolves to the wrong paper, a report number
that does not exist, a URL that 404s. We have been burned by all three and we want them named.

## Section H. Full reference list

Numbered, with title, author or issuing body, year, edition, and URL or stable identifier. Mark each
entry Tier 1, 2 or 3. Cross-reference the numbers used in Sections B and F.

For each entry state explicitly whether you **read the full text**, **read only the abstract or
summary**, or **could not open it**. For every DOI, give the title that
`https://api.crossref.org/works/<DOI>` actually returned, so the match can be checked without
re-fetching.
