# Deep-Research Prompt dr_1J-01: adversarial search that tries to BREAK our novelty claim (multi-cycle time-use studies for building energy)

> SCOPE GUARD, READ FIRST. This is an **adversarial search**. Our paper claims that no published study
> combines the six features listed below. Your job is to find the study that proves us wrong. A study that
> fills all six columns is the most useful thing you can return; one that fills five is the second most
> useful. If you find none, say so plainly. Do not flatter the claim, do not judge whether our paper is
> good, and do not score a paper you did not open.

Run in: Gemini (live search). Save the answer as `dr_1J-01_longitudinal_TUS_novelty_search_results.md`
in this folder.

---

## Why we are asking

A journal reviewer said our paper engages too little with the time-use survey (TUS) literature and that
its novelty is unclear next to earlier studies. We will add a comparison table of prior studies to the
Introduction. We need that table to be complete and honest, including studies that come close to ours.

## What our paper does (so you can score other papers against it)

We take four cycles of a national time-use survey (Canada, 2005, 2010, 2015 and 2022), harmonise them
into one schedule format, and assemble household-level occupancy schedules from the individual diaries.
We then use a generative model to project the population one step past the last census, and feed the
schedules into building energy simulation.

## The six columns (score each study Y / N / PARTLY, each Y or PARTLY with a quoted sentence and page)

| Col | Feature | Counts as Y only if |
|---|---|---|
| C1 | National time-use diary microdata | Schedules come from a national TUS (diaries), not sensors, smart meters or code defaults |
| C2 | Three or more survey cycles | At least three survey years are analysed in one harmonised format (repeated cross-sections count) |
| C3 | Household-level schedules | Presence is built for the whole household (members combined), not only per person |
| C4 | Projection past the last survey | The study projects or generates occupancy or population for a year after its last observed survey, not only describing past change |
| C5 | Projection validated with a number | The projection is checked against data it was not fitted on (a held-out survey or census, or official statistics), and a numeric error is reported |
| C6 | Used in building energy simulation | The schedules drive a building energy or performance simulation, or an energy demand model |

## Rows we already hold (re-score them from the full text; our scores may be wrong)

| Study | DOI or URL as we hold it |
|---|---|
| Osman and Ouf (2021), Building and Environment 196, 107785 (review) | 10.1016/j.buildenv.2021.107785 |
| Vosoughkhosravi, Jafari and Zhu (2023), Energy and Buildings 294, 113245 (review of ATUS) | 10.1016/j.enbuild.2023.113245 |
| Sekar, Williams and Chen (2018), Joule 2, 521 to 536 | 10.1016/j.joule.2018.01.003 |
| Mitra, Chu and Cetin (2020), ASCE conference paper on ATUS activity profiles | 10.1061/9780784482865.113 |
| Jeong, Kim and de Dear (2021), Energy and Buildings 252, 111440 | 10.1016/j.enbuild.2021.111440 |
| Sood et al. (2025), Journal of Building Performance Simulation | 10.1080/19401493.2025.2465508 |
| Gieter et al. (2017), Building Simulation 2017 conference | 10.26868/25222708.2017.478 |
| Reis, Loomans and Hajdukiewicz (2026), Building and Environment 287, 113796 (review, future scenarios) | 10.1016/j.buildenv.2025.113796 |
| Widén and Wäckelgård (2010), Applied Energy 87(6) | 10.1016/j.apenergy.2009.11.006 |
| Yin, Yamaguchi, Zajch, Uchida and Shimoda (2024), ASim 2024 | https://publications.ibpsa.org/proceedings/asim/2024/papers/E17_asim2024_1285.pdf |

For the three reviews (Osman and Ouf; Vosoughkhosravi et al.; Reis et al.), do not score the review
itself on C2 to C6. Instead, list every study the review describes as using **more than one survey
year**, and score those.

For Mitra, Chu and Cetin: find their **journal** papers on ATUS-based residential profiles (the row
above is a conference paper). List each with its DOI, verified on Crossref.

**Positive control, do not skip.** Richardson, Thomson and Infield (2008), *A high-resolution domestic
building occupancy model for energy demand simulations*, Energy and Buildings 40(8), 1560 to 1566,
DOI 10.1016/j.enbuild.2008.02.006. This paper is real. If your search cannot find and open it, your
method is broken: stop and say so.

---

## Where to search (report each, with the query strings you used)

1. Keyword searches, 2008 to 2026: combinations of "time use survey", "multiple waves", "repeated
   cross-section", "longitudinal", "trend", "decades", "occupancy", "activity", "residential",
   "energy demand", "building simulation", "projection", "forecast", "scenario", "generative",
   "synthetic population".
2. Harmonised multi-year time-use collections and the energy papers that use them: the Multinational
   Time Use Study (MTUS, Centre for Time Use Research), HETUS waves (Eurostat), the UK Time Use Surveys
   (2000, 2014 to 2015, and the 2020 to 2021 COVID-era surveys), the American Time Use Survey
   (2003 onward), Japan's Survey on Time Use and Leisure Activities (every five years), Korea's Time Use
   Survey, Australia's Time Use Survey.
3. The citing papers of Sekar et al. (2018) and of Yin et al. (2024).
4. Canadian work 2015 to 2026 using the General Social Survey time-use cycles for building energy.

---

## Rules

- Open every paper before scoring it. If you could only read the abstract, write ABSTRACT ONLY in the
  row and do not score C4 or C5.
- Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`) and give title, journal, year.
- Every Y or PARTLY carries a quoted sentence and a page or section number.
- `NOT FOUND` beats a guess. Do not invent studies, DOIs or quotes.
- Do not rank or praise our paper. Do not suggest wording for our paper.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** BROKEN (at least one study scores Y on all six) / NARROWED (best study scores Y
   on five; name the missing column) / HOLDS (no study scores more than four Y).
2. **Table A, re-scored rows we hold:** study, DOI checked (yes/no), C1 to C6, quote and page for each Y
   or PARTLY.
3. **Table B, new studies found:** same columns, sorted by number of Y, highest first. At most 25 rows.
4. **Table C, studies mined from the three reviews:** same columns.
5. **The three closest studies**, one paragraph each: which columns they fill and which they miss, quoted.
6. **Positive control result.**
7. **Search log:** databases and query strings, number of hits screened, number opened in full.
8. **What I could not open**, in the first person, one line each.
