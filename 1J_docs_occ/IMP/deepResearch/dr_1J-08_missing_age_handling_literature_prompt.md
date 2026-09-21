# Deep-Research Prompt dr_1J-08: how published studies handle persons with a missing age when building households from census microdata

> SCOPE GUARD, READ FIRST. We want to know **which published studies exist and what each one says it did**,
> not a verdict on what is best. Every study you list must be one you **opened**, with its full reference
> and DOI, and the sentence where it describes its handling of missing or suppressed values, quoted with
> page or section. A citation you did not open is not evidence: leave it out. A DOI must resolve on
> Crossref. `NOT FOUND` beats an invented study. Do not report any energy, occupancy or error number
> from any study; we do not need them and will discard a report that contains them.

Run in: Gemini (live search). Save the answer as `dr_1J-08_missing_age_handling_literature_results.md`
in this folder.

---

## Why we are asking

We build synthetic households from a national census public-use microdata file and attach a time-use
diary to each person by matching on age group, sex, household size and other traits. On some census
files a share of persons has age coded "not available". There are three broad ways to handle such a
person, and each changes the household differently:

- **(a)** remove the person and keep the rest of the household;
- **(b)** remove the whole household;
- **(c)** keep the person and fill the age in (imputation, a donor, or a rule).

We need to know how the published literature handles this, so the paper can state its choice honestly
against practice. We are equally interested in studies that did (b) or (c) and in studies that say
nothing at all.

## What we need

1. **Synthetic population and household construction from census microdata** (iterative proportional
   fitting, combinatorial optimisation, sample-based or agent-based synthesis): studies that state how
   they treated persons or households with missing or suppressed attributes, especially age. For each:
   full reference, DOI, country and census file used, which of (a), (b), (c) or something else, and the
   quoted sentence.
2. **Occupancy and time-use based building energy models** that attach diaries or schedules to census
   persons or households (for example work in the building simulation, residential demand and
   activity-based modelling literature): same fields as item 1.
3. **Methodological guidance** on missing values in census or survey microdata from a statistical agency
   or a methods text (for example on whether dropping records biases household composition): the
   document, the quoted advice, page.
4. **Studies that report the size of the effect** of their choice, in words only (for example "we found
   the households kept were larger on average"). Quote; give no numbers.
5. Studies using the **Canadian** Census PUMF specifically that mention its "not available" codes.

## Named leads

Journals and venues where this work appears: Journal of Building Performance Simulation, Energy and
Buildings, Building and Environment, Applied Energy, Environment and Planning B, Computers, Environment
and Urban Systems, Transportation Research (activity-based modelling), Journal of Artificial Societies
and Social Simulation, International Journal of Microsimulation, Population Research and Policy Review,
Statistics Canada's Survey Methodology journal. Tools whose documentation may state a missing-value
rule: PopGen, SimPop (R package), synthpop (R package), MultiLevelIPF, humanleague. These are leads,
not claims that any of them addresses the question.

---

## Rules

- Only studies you opened. For each, quote the handling sentence; if the study builds households but
  says nothing about missing values, you may list it in a separate "silent" list with its reference.
- Do not rank (a), (b) and (c), and do not tell us which one to use. Report practice only.
- If fewer than three studies state a handling rule, say so plainly; that is a useful finding.
- `NOT FOUND` beats a guess. No numbers from any study.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A:** one row per study that states a rule. Columns: reference, DOI, country and data file,
   handling (a / b / c / other, in words), exact quote, page or section.
2. **Silent list:** studies that build households from census microdata and state no rule (reference
   and DOI only).
3. **Table B (guidance):** statistical agency or methods-text advice, quoted, with page.
4. **Documents opened in full**, as a list (zero is a permitted answer), and the search terms you used.
5. **What would have made you write `NOT FOUND` for item 5**, in one sentence.
