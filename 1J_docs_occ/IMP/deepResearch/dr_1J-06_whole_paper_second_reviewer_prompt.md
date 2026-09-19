# Deep-Research Prompt dr_1J-06: act as the second reviewer of our submitted paper

> ATTACH BEFORE RUNNING: the submitted PDF, `1J_docs_occ/IMP/86e336cb-ac8c-4230-946f-20ff060f5bc4.pdf`.
>
> SCOPE GUARD, READ FIRST. Review **only the attached PDF**. Every point must quote the PDF with its page
> number. Do not praise the paper. Do not rewrite it. Do not suggest new studies to cite unless you opened
> them.

Run in: Gemini (with the PDF uploaded; live search allowed only for the overlap check in item 4). Save
the answer as `dr_1J-06_whole_paper_second_reviewer_results.md` in this folder.

---

## Why we are asking

The attached paper was submitted to the Journal of Building Performance Simulation and returned for major
revision. One reviewer's report arrived; a second report is overdue and may arrive later. We want to find
the problems a second expert reviewer would raise, before they do.

The first reviewer already raised four points, so **do not spend your review on these**:
(1) too little engagement with the time-use survey literature; (2) too little detail on the data
(sample sizes, variable definitions, regional representativeness); (3) novelty unclear next to earlier
US studies; (4) the EnergyPlus part adds little, and the generative projection is not validated enough.

## What we need

You are an expert reviewer in occupant-behaviour modelling, time-use surveys and residential building
energy simulation. Read the whole paper, including the appendices.

1. **Internal consistency.** Every place where two parts of the paper disagree: a number quoted
   differently in two sections, a mechanism that does not match the result it explains, a figure that
   does not match its text, a claim in the abstract or conclusion that the results do not support.
   Quote both places with page numbers.
2. **Methods a reviewer would challenge**: data selection, matching of schedules to households, how
   schedules enter the simulation, building models used, equations, and the explanations given for
   unusual results.
3. **Presentation**: garbled equations, duplicated sentences, unclear figures, reference errors.
4. **Overlap risk**: search for published or preprint papers by other groups, or conference versions,
   that report the same pipeline or results. Report only what you opened.
5. **A recommendation** (accept, minor, major, reject) with the three points that decide it.

---

## Rules

- Quote the PDF exactly for every point, with page number. A point without a quote does not count.
- Rank points by how likely they are to cause rejection.
- Do not repeat the first reviewer's four points.
- `NOT FOUND` beats a guess. Do not invent quotes, page numbers or papers.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Recommendation, one line**, and the three deciding points.
2. **Table A, major issues:** number, category (consistency, method, presentation, overlap), exact quote,
   page, why a reviewer would object, what evidence would settle it.
3. **Table B, minor issues:** same columns.
4. **Overlap check:** what you searched, what you opened, what you found.
5. **What I could not read in the PDF** (figures, tables, equations), in the first person.
