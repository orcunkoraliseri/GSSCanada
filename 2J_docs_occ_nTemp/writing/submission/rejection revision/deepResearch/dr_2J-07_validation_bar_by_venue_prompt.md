# Deep-Research Prompt dr_2J-07: What measured-data check do recent papers at the candidate journals actually have?

> SCOPE GUARD, READ FIRST. This is an **evidence count from published articles**, not advice about
> where to submit. We want to know, from real recent papers, how stock-scale residential load-shape
> simulation studies in three journals checked their simulated hourly profiles against measured data,
> and how often they had no such check at all. **Every article you count must be opened and its DOI
> verified.** Reputation, editorial statements you cannot link, and "typically" are not evidence.

---

## Why we need this

Our manuscript simulates hourly electricity for a national stock of Canadian homes under
occupancy schedules built from time-use surveys, including scenarios to 2030. We are choosing between
**Applied Energy**, **Sustainable Cities and Society**, and **Journal of Building Engineering**. The
choice depends on whether we can add a direct comparison with measured hourly data (searched
separately in `dr_2J-06`). We need to know how high the bar actually is at each journal.

---

## Role

Evidence analyst. You sample real articles, open them, and record what their validation section
contains. You do not rank the journals and you do not recommend one.

---

## What to sample

For **each of the three journals**, find **8 to 12 articles published 2022 to 2026** that match this
description as closely as possible:

- residential buildings (not commercial only);
- simulation or modelling of **hourly or sub-hourly** energy or electricity demand;
- at **stock, district, city, regional or national** scale (not a single house);
- occupancy, time-use, behaviour, or work-from-home as a driver, if possible.

If a journal has fewer than 8 matching articles, list what exists and say how many you found. Do not
pad the sample with off-topic articles.

---

## REQUIRED OUTPUT TABLES, fill every cell

### Table 1: The sampled articles

| # | Journal | Authors, year, title | DOI (Crossref-verified) | Country / region | Scale | Occupancy or time-use driven? | Hourly profile checked against MEASURED data? YES / NO / ONLY ANNUAL OR MONTHLY | If yes: what measured data (smart meters, utility class profile, system operator, submetered sample), how many homes, which years | If no: what did they use instead (other model, survey totals, literature ranges, none) | Quote from the article's validation section, with section number |
|---|---|---|---|---|---|---|---|---|---|---|

### Table 2: Count per journal

| Journal | Articles sampled | Hourly shape checked against measured data | Only annual or monthly totals checked | No measured-data check | Checked against measured data from a different country than the one modelled |
|---|---|---|---|---|---|
| Applied Energy | | | | | |
| Sustainable Cities and Society | | | | | |
| Journal of Building Engineering | | | | | |

### Table 3: The journals' own stated requirements

Only statements you can link. Quote the exact sentence.

| Journal | Page (Guide for Authors, aims and scope, editorial) | Live URL | Exact sentence about validation, measured data, novelty for modelling papers, or scope for simulation studies | Word or length limit for research articles, with the sentence that states it |
|---|---|---|---|---|

If a journal's pages say nothing on validation, write **NOTHING STATED**.

### Table 4: Closest competitors found while sampling

Any article in the sample that does most of the following together: time-use or occupancy driven
schedules, national residential stock, hourly load shape, a structural break (e.g., COVID-19 or
work-from-home), and scenarios to a future year. Tell us what it does and does not do.

| DOI | What it does | Which of the five elements it has | Which it lacks |
|---|---|---|---|

Write **NONE FOUND** if none. That is an acceptable answer.

---

## Part C: Summary (facts only)

1. For each journal, the share of sampled articles with a measured **hourly** check.
2. Whether any journal published matching articles with **no** measured-data check at all, with DOIs.
3. Whether any journal published articles that validated against measured data **from a different
   country**, with DOIs.
4. What neither the articles nor the journal pages reveal.

## Output format (follow exactly)

1. Tables 1 to 4, then Part C.
2. Every row carries its DOI or live link.
3. **No recommendations and no ranking of journals.**
4. **No em dashes and no en dashes in the returned text.**

## Hard requirements

- **Every DOI is checked** against `https://api.crossref.org/works/<DOI>`; title, authors, journal
  and year must match. A DOI that resolves to another paper is an error, not a near miss.
- **Positive control:** Widen, J. and Wackelgard, E. (2010), *A high-resolution stochastic model of
  domestic activity patterns and electricity demand*, Applied Energy 87(6), 1880 to 1892. It is real
  but outside the date window; confirm its DOI resolves, then exclude it from the sample. If you
  cannot resolve it, your DOI method is broken: stop and say so.
- **Do not quote a journal policy without the URL where that exact sentence appears.**
- **Do not report acceptance rates, impact factors or review times.** They are out of scope.
- **No em dashes and no en dashes in the returned text.**
