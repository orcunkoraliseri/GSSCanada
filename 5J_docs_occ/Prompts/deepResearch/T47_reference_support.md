# T47. Reference support: check the reference list, and find sources for the methods and claims that have none

Paste `00_MASTER_BRIEF_5J.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh session. **Run it alone**
(it does not depend on T46 and does not repeat it). Written 2026-10-01 by the 5J manager (Step 8, validation gates 2.1 and 2.2).
Your files are `RT47_reference_support.md` and `RT47_pages.log` (one line per page, record or file you opened: URL, what it
was, full / abstract / title, date). Save both in this folder.

## Why we are asking

The draft cites only 17 works. Several methods it uses are named without a source, and some sentences of context state facts
without one. A journal reviewer will ask for both. We need real, opened sources, not a longer list. **A short honest answer
beats a long one: `NOT FOUND` is a good answer.**

Note on the brief: the results of the paper use **Spain and Italy only** (the UK runs are on hold). Nothing in this prompt
needs UK data.

## Part 1. Check the 17 references we already cite (gate 2.2)

For each entry below, open the Crossref record (`https://api.crossref.org/works/<DOI>`) and the publisher or repository page,
and report: authors (all, with initials), year, title, venue, volume, issue, pages or article number, DOI. Print every field
that differs from our entry. Where our entry lacks initials (He et al. 2015; Dabirian et al. 2025; Li, Bae and Im 2021), give
the full author list from the record.

1. ASHRAE (2002) Guideline 14-2002 (no DOI: give the catalogue record).
2. Crawley et al. (2001) EnergyPlus, Energy and Buildings 33(4) 319-331, 10.1016/s0378-7788(00)00114-6
3. Dabirian, Alamatsaz, Eicker (2025) IBPC 2024, LNCE 553, 3-12, 10.1007/978-981-97-8309-0_1
4. Govindarajan, Ortner, Han (2025) Energy and Buildings 347, 116366, 10.1016/j.enbuild.2025.116366
5. He, Lee, Taylor, Firth, Lomas (2015) BS2015, 2101-2108, 10.26868/25222708.2015.2655
6. INE (2011) Encuesta de Empleo del Tiempo 2009-2010: Metodologia (give the official record or URL)
7. Iseri, Gursel Dino, Kalkan (2026) Energy and Buildings 357, 117155, 10.1016/j.enbuild.2026.117155
8. ISTAT (2016) I tempi della vita quotidiana, Anno 2013-2014 (give the official record or URL)
9. Li, Bae, Im (2021) ORNL/LTR-2021/1923, 10.2172/1817464
10. Loga, Stein, Diefenbach (2016) Energy and Buildings 132, 4-12, 10.1016/j.enbuild.2016.06.094
11. Osman, Ouf (2021) Building and Environment 196, 107785, 10.1016/j.buildenv.2021.107785
12. Pan, Xu, Hong (2024) Journal of Building Performance Simulation 19(5), 875-893, 10.1080/19401493.2024.2359985
13. Park, Park (2023) Journal of Building Performance Simulation 17(3), 361-370, 10.1080/19401493.2023.2282078
14. Richardson, Thomson, Infield (2008) Energy and Buildings 40(8), 1560-1566, 10.1016/j.enbuild.2008.02.006
15. Richardson, Thomson, Infield, Clifford (2010) Energy and Buildings 42(10), 1878-1887, 10.1016/j.enbuild.2010.05.023
16. Vosoughkhosravi, Jafari, Zhu (2023) Energy and Buildings 294, 113245, 10.1016/j.enbuild.2023.113245
17. Widen, Wackelgard (2010) Applied Energy 87(6), 1880-1892, 10.1016/j.apenergy.2009.11.006

Also: is there a **2014 edition of ASHRAE Guideline 14**, and does its hourly calibration criterion still read CV(RMSE) at most
30 % and NMBE within 10 %? Quote the clause number and page if you can open it; otherwise give the catalogue record and write
`CLAUSE NOT OPENED`.

## Part 2. Sources for methods the draft names without a citation

For each, give the ORIGINAL source (the paper or manual that introduced or defines it), opened, with full reference and DOI or
arXiv ID, and one sentence on what it defines. One source per item unless the item says otherwise.

1. Temporal convolution network with dilated causal convolutions (the generic sequence-modelling architecture).
2. Transformer encoder (self-attention).
3. Histogram-based gradient boosting as implemented in scikit-learn (`HistGradientBoostingRegressor`): the scikit-learn
   reference, and the algorithm paper the scikit-learn documentation itself names as its basis.
4. ERA5 reanalysis (the dataset description paper).
5. Cluster (block) bootstrap for confidence intervals when units are grouped (a standard statistics source; textbook or paper).
6. The HETUS harmonised European time-use survey guidelines (Eurostat, the edition that covers the 2010 wave).
7. The EnergyPlus version used (23.1): the official documentation record (Engineering Reference or Input Output Reference),
   as the developers ask it to be cited.
8. PyTorch (the framework paper).

## Part 3. Sources for context statements that carry no citation

For each statement, find up to three opened sources (2005 to today) that support it, or that **contradict** it, and say which.
Quote the sentence or give the page and section that supports or contradicts it. If nothing supports it, write `NOT FOUND`;
we will then soften or drop the sentence.

1. "Most studies run one average schedule" in residential stock or urban building energy models (standard or deterministic
   schedules instead of stochastic household samples).
2. Occupant behaviour is a major source of uncertainty or of the gap between simulated and measured residential energy
   (for example work of IEA EBC Annex 66 or Annex 79, and reviews of occupant behaviour modelling).
3. Urban building energy modelling (UBEM) review papers that describe archetypes and the cost of simulation at stock scale.
4. Studies that sample many stochastic occupancy profiles per building in a stock or district model and report the spread of
   demand (beyond He et al. 2015 and Dabirian et al. 2025): how many samples they used, if stated.
5. Household size and appliance ownership or use as the main drivers of annual residential electricity use (reviews of
   socio-economic determinants of household energy).
6. Heating demand in residential buildings responds weakly to occupancy, compared with electricity, through internal gains
   and presence (any simulation or measurement study that quantifies it).
7. Machine-learning building energy models scored mainly on accuracy metrics (CV(RMSE), NMBE, R2) rather than on the
   relationships between inputs and outputs; reviews that say so.
8. TABULA archetypes used as the building description in urban or national residential energy models.
9. Graphics processing units (GPUs) used to speed up surrogates or building energy prediction at district or city scale,
   with a reported speed comparison to the simulation engine.

## Part 4. Data credits

Give the formal citation, as each data owner asks to be cited, for: (a) the Spanish time-use survey 2009-2010 microdata (INE);
(b) the Italian time-use survey 2013-2014 public-use microdata (ISTAT); (c) TABULA / EPISCOPE webtool data. Quote the
owner's own "how to cite" text with its URL, or write `NOT FOUND`.

## Hard constraints specific to this prompt
* **Positive controls:** entries 2 (Crawley 2001) and 10 (Loga 2016) in Part 1 must come back with every field matching the
  Crossref record; describe each in one sentence from its record. Misdescribing either fails the round.
* **Negative control:** also look up `10.1016/j.enbuild.2099.000001`. It must come back `DOI NOT FOUND`. If you return a
  title for it, the round fails.
* Open every source before citing it; log every page in `RT47_pages.log`. Verify every DOI against Crossref. `TITLE ONLY`
  only after one logged attempt at an open copy.
* No number (accuracy, speed-up, share of variance, sample count) unless quoted with its page.
* Do not suggest changes to the paper's method or thresholds, and never suggest relaxing a band because a model fails it.
* No em dashes and no en dashes anywhere.

## Deliverable
**Section A** (at most six sentences): how many of the 17 references are correct as written, which need fixing, and how many
Part 2 and Part 3 items found an opened source. **Section B**: one row per citable fact. **Section C**: Part 1 table (field by
field, ours vs record). **Section D**: Part 2 table (item, source, DOI or arXiv ID, read: full / abstract / title, what it
defines). **Section E**: Part 3 table (statement, sources, supports or contradicts, quote or page, read level). **Section F**:
Part 4 citations with the owners' own wording and URLs. **Section G**: controls (both positive, the negative), works you could
not open, the four standard questions. **Section H**: full references in the journal style of the draft (author, year, title,
venue, volume(issue), pages, DOI).
