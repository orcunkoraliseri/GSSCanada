# Deep-Research Prompt dr_1J-03: official methodology of the Canadian GSS time-use cycles and the Census public-use files

> SCOPE GUARD, READ FIRST. Every answer must come from an **official Statistics Canada document you
> opened** (a user guide, a codebook, a Daily release, a technical report), with its title, URL and page
> number. We hold the microdata for all these files, so every count you give will be checked against our
> own files. A number you cannot find in a document must be written `NOT FOUND`.

Run in: Gemini (live search). Save the answer as `dr_1J-03_GSS_and_census_methodology_results.md` in
this folder.

---

## Why we are asking

A reviewer asked for more detail on our data: sample sizes per cycle, variable definitions, and whether
the data represent Montreal and Quebec. While preparing the answer we also need the official account of
how each survey cycle was collected and weighted, because our paper explains one cycle's unusual result
by its weighting method and we must check that explanation against the source.

## What we need

**Part 1. GSS time-use cycles.** For each of Cycle 19 (2005), Cycle 24 (2010), Cycle 29 (2015) and the
2022 time-use cycle (Cycle 38):

1. The official user guide: exact title, URL, publication year.
2. Collection period and collection mode (telephone interview, electronic questionnaire, or both).
3. Number of respondents in the main file and in the episode file, for Canada and, if published, for
   Quebec.
4. Response rate.
5. How the diary day is defined (start and end time) and the time resolution of episodes.
6. The variable that records **where** each activity took place (its name and its categories), and any
   change in those categories from one cycle to the next.
7. **Weighting.** How the final person weights were built: which population totals they were calibrated
   to (for example demographic population estimates by age, sex and province), which census or estimate
   base those totals came from, and whether bootstrap weights exist. Quote the user guide for each cycle
   separately. Do not summarise across cycles.
8. Any Statistics Canada note on **comparability** between these cycles (changes in mode, questions,
   coding or sampling that affect time-at-home comparisons).

**Part 2. Census public-use microdata files (PUMF).** For the 2006 Census, the 2011 National Household
Survey, the 2016 Census and the 2021 Census:

1. Which PUMF exist (individuals file, hierarchical file) and their sampling fraction and record counts.
2. Which geography is on each file: province only, or also census metropolitan area. Is Montreal
   identifiable on each file?
3. For the 2011 National Household Survey: its response rate and the official caution on data quality.

## Named leads

Statistics Canada catalogue numbers and pages for the General Social Survey (time use), for example the
89F0115X series of user guides, the Integrated Metadatabank (IMDB) survey pages (survey number 4503), and
the PUMF documentation for catalogue 97M0001X / 98M0001X. These are leads: confirm each number on the
page you open.

---

## Rules

- Quote the source for every fact, with page or section. Separate each cycle's answer; never write "the
  same as the previous cycle" unless the document says so.
- Do not explain or interpret anomalies in the data. Report methods only.
- `NOT FOUND` beats a guess. Do not reconstruct a number from other numbers.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A (GSS):** one row per cycle and item (Part 1, items 1 to 8). Columns: cycle, item, answer,
   exact quote, document title, URL, page.
2. **Table B (Census PUMF):** one row per file and item. Same columns.
3. **Comparability notes:** every Statistics Canada caution you found, quoted.
4. **Documents opened in full**, as a list (zero is a permitted answer), and for each item left
   `NOT FOUND`, one line on where you looked.
