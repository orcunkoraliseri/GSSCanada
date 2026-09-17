# Deep-Research Prompt dr_2J-10 (Gemini version): live-search systematic search that tries to BREAK our novelty table

> SCOPE GUARD, READ FIRST. This is an **adversarial search**. Our paper claims that no published study
> combines six features (listed below). Your job is to find the study that proves us wrong. A study that
> fills all six columns is the most useful thing you can return. A study that fills five is the second most
> useful. If you find none, say so plainly. Do not flatter the claim, do not judge whether our paper is good,
> and do not score a paper you did not open.

---

## What our paper does (so you can score other papers against it)

We generate household occupancy and activity schedules from a national time-use survey with a trained
generative model, link them to census households, build scenario schedules for a future year (2030) that
cross the COVID-19 work-from-home change, and run them through EnergyPlus for four dwelling archetypes in six
Canadian climate zones. The results are hourly residential load shape: peak hour, load factor, midday share,
by end use. We compare against simple fixed schedules and against measured hourly utility data.

## The six columns (score each study on each, Y / N / PARTLY, with a quoted sentence)

| Col | Feature | Counts as Y only if |
|---|---|---|
| C1 | Time-series occupancy | Occupancy or activity varies within the day at 1 hour or finer, per household or person |
| C2 | Behaviour model grounded in survey data | Schedules come from time-use or similar behavioural microdata (Markov, survival, generative or matched diaries), not a code default |
| C3 | Future year or scenario across the COVID break | Occupancy is projected or scenario-built for a year after 2022, and the study states how post-pandemic home working enters it |
| C4 | Activity and end-use resolved | Loads are split by end use (at least heating, appliances, lighting or hot water) and linked to activities or presence |
| C5 | Stock or multi-archetype scale | At least several dwelling types or a stock model, and more than one climate or region |
| C6 | Load shape and peak as the main result | Hourly shape, peak timing, load factor or ramping is a headline result, not only annual energy |

## Rows already in our table (re-score them from the full text; our scores may be wrong)

| Study | DOI or URL as we hold it |
|---|---|
| Chiou et al. (2011), Energy and Buildings 43(12) | 10.1016/j.enbuild.2011.09.020 |
| Widén and Wäckelgård (2010), Applied Energy 87(6) | 10.1016/j.apenergy.2009.11.006 |
| Reinhart and Cerezo Davila (2016), Building and Environment 97 | 10.1016/j.buildenv.2015.12.001 |
| Fischer et al. (2020), Energy and Buildings 224 | 10.1016/j.enbuild.2020.110133 |
| Motuzienė et al. (2022), Sustainable Cities and Society 76 | 10.1016/j.scs.2021.103557 |
| Chen et al. (2022), Applied Energy 325 | 10.1016/j.apenergy.2022.119890 |
| Osman et al. (2023), Building and Environment 241 | 10.1016/j.buildenv.2023.110490 |
| Yin et al. (2024), ASim 2024 proceedings | https://publications.ibpsa.org/proceedings/asim/2024/papers/E17_asim2024_1285.pdf |
| Jalilian and Kamel (2025), Frontiers in Energy Research 13 | 10.3389/fenrg.2025.1683787 |
| Barsanti, Yilmaz and Binder (2024), Energy and Buildings 321 | 10.1016/j.enbuild.2024.114639 (not yet in our table; score it) |

**Positive control, do not skip.** Richardson, Thomson and Infield (2008), *A high-resolution domestic building
occupancy model for energy demand simulations*, Energy and Buildings 40(8), 1560 to 1566,
DOI 10.1016/j.enbuild.2008.02.006. This paper is real. If your search cannot find and open it, your method is
broken: stop and say so.

---

## Where to search (report each, with the query strings you used)

1. Scopus or Web of Science style keyword searches, 2015 to 2026: combinations of "time use survey",
   "occupancy", "activity", "residential", "building stock", "urban building energy", "load profile",
   "peak", "load shape", "work from home", "telework", "COVID-19", "post-pandemic", "2030", "scenario".
2. The citing papers of Chen et al. (2022) and of Osman et al. (2023): any later study that adds a future
   year or post-COVID scenario to their designs.
3. Stock models with occupancy modules: ResStock and its successors, CityBES, UMI, TEASER, CityGML-based
   workflows, EU building-stock models, UK (for example CREST and its successors), Japan, Korea, China.
4. Studies of post-pandemic residential load shape that use simulation rather than smart-meter statistics
   alone.
5. Canadian work 2019 to 2026 on time-use based residential simulation.

---

## Rules

- Open every paper before scoring it; abstracts alone are not enough for C3, C4 and C6. If you could only read
  the abstract, write ABSTRACT ONLY in the row and do not score C3 to C6.
- Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`) and give title, journal, year.
- Every Y or PARTLY carries a quoted sentence and a page or section number from the paper.
- `NOT FOUND` beats a guess. Do not invent studies, DOIs or quotes.
- Do not rank or praise our paper. Do not suggest wording for our paper.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** BROKEN (at least one study scores Y on all six) / NARROWED (best study scores Y on five,
   name the missing column) / HOLDS (no study scores more than four Y).
2. **Table A, re-scored existing rows:** study, DOI checked (yes/no), C1 to C6 each with Y/N/PARTLY, quote and
   page per Y or PARTLY.
3. **Table B, new studies found:** same columns, sorted by number of Y, highest first. At most 25 rows.
4. **The three closest studies**, one paragraph each: which columns they fill, which they miss, quoted.
5. **Positive control result.**
6. **Search log:** databases and query strings, number of hits screened, number opened.
7. **What I could not open**, in the first person, one line each.

Save the return as `dr_2J-10_novelty_matrix_search_gemini_results.md`. A companion no-search close-reading
pass runs in Fable on our own novelty argument (`dr_2J-10_novelty_matrix_search_fable_prompt.md`) — run
both, they check different things.
