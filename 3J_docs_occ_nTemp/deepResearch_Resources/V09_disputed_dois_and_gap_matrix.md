# V09. Two disputed DOIs, and the first real test of the gap matrix

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H).

---

## Why we are asking

Two things are blocking the 3J submission to Building and Environment, and both are literature
questions this session cannot answer, because searching and DOI verification are done externally.

**First, two DOIs are disputed and the manuscript cannot ship until one of them is right.**
`RV08` reported that both competitor DOIs in the Chapter 1 reference list resolve to unrelated
papers, and gave replacement citations. The replacements were **not** applied, for one reason: in
the 2J round roughly half the citations in the returned research reports turned out to be
fabricated, and every one of them was internally consistent and plausible-looking. `RV08` is one
unverified report. Both the original and the replacement forms are internally consistent. Only
opening the DOI decides it, and that has not been done.

**Second, the gap matrix in Table 1 has never been tested against the literature.** Table 1 claims
an unoccupied cell: no published study combines a time-use-survey-driven behavioural occupancy
model, more than one occupancy channel, a forecast to a future year, and a single mixed-use
building. That claim currently rests on one positioning review, which is also the only citation
lookup ever performed for this project. **No search was ever run to look for a competitor.** The 2J
round established exactly this pattern and it is worth stating plainly: an empty competitor list is
evidence of no search far more often than it is evidence of no competitor. Table 1 is the paper's
novelty claim, and at a selective venue it is the first thing a reviewer will attack.

---

## What we need

**Part A. Resolve the two disputed DOIs, by opening them.**

1. `https://doi.org/10.1016/j.apenergy.2023.122247`. Report the actual title, authors, journal,
   volume, article number and year the DOI resolves to. Verify through
   `https://api.crossref.org/works/10.1016/j.apenergy.2023.122247` **and** by loading the landing
   page. State both results separately, and say so if they disagree.
2. Do the same for the replacement `RV08` proposed:
   `https://doi.org/10.1016/j.apenergy.2024.124081`, reportedly Doma, A., Padsala, R., Ouf, M. M.
   and Eicker, U. (2024), *Applied Energy*, 375, 124081.
3. `https://doi.org/10.1016/j.enbuild.2019.109562`, and the replacement
   `https://doi.org/10.1016/j.enbuild.2019.109577` (reportedly Buttitta and Finn, *Energy and
   Buildings*, 206). Both forms agree on volume 206, so the article number is the whole question.
4. For each of the four DOIs above, state one of exactly three verdicts: **RESOLVES TO THE CITED
   PAPER**, **RESOLVES TO A DIFFERENT PAPER** (name it), or **DOES NOT RESOLVE**. Do not soften
   these into "appears to" or "likely".
5. Separately, give the correct, complete citation for each of the two intended works, found by
   title search rather than by DOI, so that the citation can be rebuilt from scratch if both
   candidate DOIs are wrong.

**Part B. Try to break the gap matrix.**

6. Search for any published study, 2015 to 2026, that generates **two or more occupancy channels
   for functionally different uses** driven by a **time-use survey**, and applies them to **one
   mixed-use building**. Report every candidate found, including partial matches, with the axes it
   does and does not satisfy.
7. Do the same for the narrower and more dangerous case: any study that carries a survey-derived
   occupancy model **forward to a future year** for more than one use.
8. Report explicitly on hotel and retail occupancy specifically, since those are the two channels
   this paper adds. Anything that models guest-room or customer presence for building energy
   simulation from a population-level source is relevant even if it is single-channel.
9. State how many searches you ran, in which databases, and with which query strings. **A report
   that lists no competitor without listing its queries is not usable**, because it cannot be
   distinguished from a search that was never run.

---

## Named leads

Crossref REST API; Scopus and Web of Science; Google Scholar with a citation-chain walk both ways
from Doma and Ouf (2023, 2024), Buttitta and Finn (2020), and Widén and Wäckelgård (2010);
IBPSA proceedings (Building Simulation conference series, and the national affiliates eSim,
BSO, IBPSA-USA SimBuild); *Energy and Buildings*, *Building and Environment*, *Applied Energy*,
*Journal of Building Performance Simulation*, *Building Simulation*, *Journal of Building
Engineering*; the IEA EBC Annex 66 and Annex 79 output on occupant behaviour modelling; the
Harmonised European Time Use Survey and the American Time Use Survey methodological literature for
building-energy applications.

---

## Deliverable

Section A of your answer must contain:

1. A four-row table, one row per DOI, with columns `DOI | verdict | what it actually resolves to |
   how verified (API, landing page, or both)`.
2. A clean, complete, copy-ready citation for each of the two intended works.
3. A competitor table: one row per candidate study found in Part B, with a column per gap-matrix
   axis (time-series occupancy, multi-channel, calibrated behavioural model, forecast to a future
   year, mixed-use single building, activity or end-use resolution, stock-scale), marked satisfied
   or not, plus the DOI and how it was verified.
4. **A search log**: the databases queried, the exact query strings, and the result counts. This is
   mandatory and it is the part that makes the rest of the report trustworthy.
5. If Part B finds a genuine competitor for the unoccupied cell, say so directly in one sentence at
   the top of Section A. **A finding that the novelty claim is weaker than stated is a successful
   result of this prompt, not a failure of it.** Do not soften it and do not bury it.

Rules restated, because every previous round in this project needed them:

- A citation is not evidence until it has been opened. Report what you opened.
- `NOT FOUND` beats an invented number, an invented volume, or an invented author list.
- Never propose relaxing a reference band because this project's model fails it. That is out of
  scope for this prompt entirely.
- Keep as-modelled and empirical figures strictly separate.
- No em dashes and no en dashes anywhere in the returned text.
