# Item 3: candidate references from VETTING_RV11_RV14, checked online (2026-09-25)

**Input.** `3J_docs_occ_nTemp/deepResearch_Resources/VETTING_RV11_RV14_2026-09-25.md`, M-list rows M1-M40.
Every row graded `CANDIDATE` or `CANDIDATE-AUTHOR-OPENS` was checked. That is 19 M-rows (M4, M5, M9, M11, M12, M15, M17,
M18, M19, M22, M24, M25, M26, M28, M30, M31, M33, M34, M39) plus one row with no M number, Goel et al. (2014)
(RV11 table, Eq. 1). One new lead turned up along the way (X1, Happle et al. 2020). No manuscript or chapter file
was edited.

**How it was checked.** I used the Crossref REST API (`api.crossref.org/works/<doi>` and `query.bibliographic`),
OpenAlex (for abstracts), the arXiv API, the NeurIPS proceedings, the OpenReview API, the OSTI API, the DataCite API,
the NRC Publications Archive, Government of Canada Publications, NRCan OEE pages, the StatCan IMDB, the CKAN APIs of
open.alberta.ca and donnees.montreal.ca, quebec.ca, bls.gov (through WebFetch, because curl got HTTP 403), Open
Library, Google Books, and ASHRAE's own 2021 table-of-contents PDF. Where Crossref and the vetting file disagree,
**Crossref wins**, and the row says so. Every field below was read off the page at the URL given. None was filled
from memory.

**Line numbers.** The chapter files were edited after the vetting file was written, so its line numbers have
moved. This file uses the current positions (read 2026-09-25):
- `01_Introduction.md:5` has **already been filled** (de Wilde; Mahdavi et al.; Richardson et al.; Widén and
  Wäckelgård; Wilke et al.), so M4 no longer has a placeholder to fill.
- `02_Framework.md:85` already cites Mardia and Jupp (2000). It has no placeholder left.
- `11_References.md`: Guideline 14 is at line 5, Alberta at 19, ISQ at 21, NECB at 29, SCIEU at 33, PNNL at 45.
  Doma and Ouf (2023) is at line 13.
- **A new placeholder the vetting file does not cover:** `02_Framework.md:36` "[REF NEEDED: source of the 2023 to
  2025 hotel recovery levels]". No candidate exists for it. The author has to supply it.

**Orphans (for the author).** Neither Guideline 14 nor SCIEU is cited anywhere in the `chapters_v2` body text.
SCIEU appears only in `07_Nomenclature.md:19`, and Guideline 14 only in the SI. If the SI does not cite them either,
delete the entries instead of filling them.

---

## Row-by-row results

### M4. McKenna, Higgins and Ramirez-Mendiola (2022), E&B 268, 112124 (placeholder `01_Introduction.md:5`, now filled)

- **Exists? NO, as proposed.** RV12 gives DOI `10.1016/j.enbuild.2022.112124`. Crossref resolves that DOI to
  *Jung, Y., Oh, J., Han, U., Lee, H. (2022) "A comprehensive review of thermal potential and heat utilization for
  water source heat pump systems", Energy and Buildings 266, 112124*
  (https://api.crossref.org/works/10.1016/j.enbuild.2022.112124). The volume is 266, not 268, and the paper is a
  different one.
- Crossref title search for "Inhomogeneous Markov models for high-resolution residential occupancy simulation from
  time use data": no match. OpenAlex search: no match. Crossref author search (McKenna, E&B ISSN 0378-7788,
  2021-2023) lists four McKenna papers, none on this topic. Crossref author search for Ramirez-Mendiola: no E&B
  paper.
- **Grade: REJECT** (fabricated metadata). The placeholder is already filled, so nothing is lost.

### M5. `01_Introduction.md:11`, "[REF NEEDED: sources linking mixed-use load diversity to plant sizing and grid peak]"

Sentence: *"Central plant sizing, shared-system operation and the building's contribution to district and grid
peaks all depend on how the uses overlap in time."*

**(a) Fonseca, Nguyen, Schlueter and Marechal (2016)**
- **Exists: yes.** Crossref (https://api.crossref.org/works/10.1016/j.enbuild.2015.11.055) gives: "City Energy
  Analyst (CEA): Integrated framework for analysis and optimization of building energy systems in neighborhoods
  and city districts", Jimeno A. Fonseca, Thuy-An Nguyen, Arno Schlueter, Francois Marechal. *Energy and
  Buildings* 113, pp. 202-226, published February 2016. The metadata matches the vetting file.
- **Supports? NO.** The abstract (EPFL record https://infoscience.epfl.ch/record/217755) describes the CEA
  framework, a Swiss downtown case, thermal micro-grid integration, and savings in emissions, primary energy and
  cost. It says nothing about load diversity, coincidence or overlap, plant sizing, or grid peak. RV12's summary
  ("temporal load staggering ... lowers required generation capacity") is not in the abstract.
- **Grade: REJECT for this sentence.**

**(b) ASHRAE (2021) Handbook Fundamentals, Ch. 18**
- **Exists: yes.** ASHRAE's own 2021 table-of-contents PDF
  (https://www.ashrae.org/file%20library/professional%20development/i-p_f21-inside4voltoc.pdf) lists "2021
  FUNDAMENTALS ... 18. Nonresidential Cooling and Heating Load Calculations".
- **Supports?** CANNOT-OPEN (paywall). The author opens Ch. 18 and confirms that it discusses diversity or block
  (coincident) load in central plant sizing. The "15-35 % oversizing" figure stays REJECT (M6).
- **Grade: VERIFIED-METADATA-ONLY.**

**Better lead found by this check: see X1 (Happle et al. 2020).** Its abstract supports the plant-sizing half of
the sentence.

### M9. `02_Framework.md:30`, "[REF NEEDED: PCGrad, gradient surgery for multi-task learning]"

- **Exists: yes.** The NeurIPS proceedings BibTeX
  (https://proceedings.neurips.cc/paper_files/paper/2020/file/3fe78a8acf5fda99de95303940a2420c-Bibtex.bib) gives:
  authors Yu, Tianhe; Kumar, Saurabh; Gupta, Abhishek; Levine, Sergey; Hausman, Karol; Finn, Chelsea. Title
  "Gradient Surgery for Multi-Task Learning". *Advances in Neural Information Processing Systems* 33,
  pp. 5824-5836, 2020, Curran Associates. arXiv:2001.06782 (https://export.arxiv.org/api/query?id_list=2001.06782)
  has the same six authors and the comment "NeurIPS 2020". This matches the vetting file field for field.
- **Supports?** Yes. The abstract says the method "projects a task's gradient onto the normal plane of the gradient
  of any other task that has a conflicting gradient", which is exactly the sentence ("removes the part of each
  head's gradient that conflicts with another head"). This check does not confirm that the training code uses
  PCGrad; the author knows.
- **Grade: VERIFIED.**
- Reference: Yu, T., Kumar, S., Gupta, A., Levine, S., Hausman, K. and Finn, C. (2020) Gradient surgery for
  multi-task learning. In: *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*, pp. 5824-5836.

### M11. `02_Framework.md:36`, "[REF NEEDED: Box-Jenkins seasonal ARIMA source]"

- **Exists: yes.** The Wiley product page
  (https://www.wiley.com/en-us/Time+Series+Analysis:+Forecasting+and+Control,+5th+Edition-p-9781118675021) gives:
  "Time Series Analysis: Forecasting and Control, 5th Edition", George E. P. Box, Gwilym M. Jenkins, Gregory C.
  Reinsel, Greta M. Ljung, June 2015, ISBN 978-1-118-67502-1 (hardcover). A Crossref-indexed review
  (https://api.crossref.org/works/10.1111/jtsa.12194, *J. Time Series Analysis* 37(5) 709-711) gives the same
  authors, 2015, "John Wiley and Sons Inc., Hoboken, New Jersey", ISBN 978-1-118-67502-1. This matches the vetting
  file.
- **Supports?** Seasonal models are a named chapter. The Crossref chapter records of the 4th edition show
  "Seasonal Models" (ch. 9, `10.1002/9781118619193.ch9`) and "Intervention Analysis Models and Outlier Detection"
  (ch. 13). I did not open the 5th-edition table of contents myself: the Wiley page links it as a PDF, and a web
  search summary named "Seasonal Models" as chapter 9. The author confirms the chapter in the 5th edition.
  **Do not print chapter or page numbers.**
- **Grade: VERIFIED-METADATA-ONLY.**
- Reference: Box, G.E.P., Jenkins, G.M., Reinsel, G.C. and Ljung, G.M. (2015) *Time Series Analysis: Forecasting
  and Control*, 5th edn. Hoboken, NJ: John Wiley & Sons.

### M12. `02_Framework.md:36`, pandemic pulse and level shift (optional, no placeholder)

- **Exists: yes.** Crossref (https://api.crossref.org/works/10.1080/01621459.1975.10480264) gives: "Intervention
  Analysis with Applications to Economic and Environmental Problems", G. E. P. Box, G. C. Tiao. *Journal of the
  American Statistical Association* 70(349), pp. 70-79, March 1975. This matches the vetting file.
- **Supports?** Yes. The abstract (OpenAlex) says it "discusses the effect of interventions on a given response
  variable in the presence of dependent noise structure" and discusses "estimators of parameters measuring level
  changes". That fits the sentence "a pandemic pulse ... and a level shift".
- **Grade: VERIFIED.**
- Reference: Box, G.E.P. and Tiao, G.C. (1975) Intervention analysis with applications to economic and
  environmental problems. *Journal of the American Statistical Association*, 70(349), pp. 70-79.
  https://doi.org/10.1080/01621459.1975.10480264

### M15. `02_Framework.md:85`, circular statistics, second source (Mardia and Jupp is already cited)

- **Exists: yes.** Crossref (https://api.crossref.org/works/10.1017/CBO9780511564345) gives: "Statistical Analysis
  of Circular Data", N. I. Fisher, Cambridge University Press, monograph, issued 1993-10-14. The ISBNs listed are
  9780521350181, 9780521568906 and 9780511564345 (online).
- **Supports?** CANNOT-OPEN (paywall). The author confirms that Fisher defines the mean direction in a form that
  covers the **load-weighted** mean of Eq. B.7. The sentence is already sourced by Mardia and Jupp, so this is
  optional.
- **Grade: VERIFIED-METADATA-ONLY.**
- Reference: Fisher, N.I. (1993) *Statistical Analysis of Circular Data*. Cambridge: Cambridge University Press.
  https://doi.org/10.1017/CBO9780511564345

### M17. `02_Framework.md:89`, "[REF NEEDED: standard definition of coincidence factor]"

All three candidates exist, but none of their definitions could be opened.
- **IEEE Std 100-2000**, "The Authoritative Dictionary of IEEE Standards Terms, Seventh Edition". Open Library
  (https://openlibrary.org/isbn/0738126012.json) gives: IEEE, 1 December 2000, "Seventh Edition", ISBN-10
  0738126012 (check digit valid). The IEEE Xplore record is https://ieeexplore.ieee.org/document/4116787/ (seen as a
  search result; the page did not render for me). Crossref shows no DOI for it.
- **Grainger, J.J. and Stevenson, W.D., Jr. (1994)** *Power System Analysis*. Open Library
  (https://openlibrary.org/isbn/0070612935.json) gives: McGraw-Hill, New York, 1994, 787 pp., ISBN 0070612935.
- **ASHRAE (2021) Handbook Fundamentals**, Ch. 18: exists (see M5b).
- **Supports?** CANNOT-OPEN for all three. RV11's page numbers (IEEE p. 195; Grainger and Stevenson p. 13) were
  **not** checked and must not be printed. The author opens one source, confirms that its definition is "maximum
  of the sum over the sum of the maxima", and cites that one.
- **Grade: VERIFIED-METADATA-ONLY.**

### M18. `04_Discussion.md:7`, "[REF NEEDED: studies that link occupancy diversity to peak demand in large or mixed-use buildings]"

Sentence: *"...because occupancy detail is often assumed to matter most for peaks."*

- **Fonseca et al. (2016): REJECT.** Same reason as M5a: the abstract does not discuss peaks or diversity.
- **Doma et al. (2024)**, already in the list. Crossref and OpenAlex (https://doi.org/10.1016/j.apenergy.2024.124081)
  give: Doma, Padsala, Ouf, Eicker, *Applied Energy* 375, 124081. The abstract names a mixed-use Montreal district
  of **112 buildings** (RV13 said 221; that is wrong). It studies "the diversity between the generated profiles"
  and reports "an estimated reduction in district peak demand by up to 17%" from occupancy-based control and
  demand response.
  - It does link occupancy detail to peak demand, which supports the sentence as worded.
  - It does **not** show, in the abstract, cross-use diversity lowering a coincident peak (RV13's claim).
- **X1 (Happle et al. 2020)** also fits. See below.
- **Grade: VERIFIED** for Doma et al. (2024), cited for the weaker link only (occupancy-based strategies and
  district peak), not for RV13's claim.

### M19. `04_Discussion.md:15`, "[REF NEEDED: measured energy data for Canadian mixed-use or high-rise buildings by use]"

All three datasets exist. The sentence is worded as a need ("A reference built from measured mixed-use towers
would be needed"). What each source shows supports that need: the measured data are either whole-building or by
single primary activity.
- **NRCan SECMURBs 2018.** The page is https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/murb/2018/tables.cfm.
  Its title is "Survey of Energy Consumption of Multi-Unit Residential Buildings (SECMURBs) 2018 – Data Tables".
  It covers eight municipalities (including Montreal and Calgary); "survey coverage is not national"; 11,715 MURBs.
  The vetting file gave no URL for it. The `/secmurbs/2018/` path returns "File not found".
- **NRCan SCIEU 2019.** The page is https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm.
  Its title is "Survey of Commercial and Institutional Energy Use (SCIEU) - Buildings 2019 – Data Tables". Table 1
  is "Building and Establishment characteristics by primary activity, 2019", so the data are by primary activity,
  not by use within a building.
- **Ville de Montréal, Règlement 21-042.** The only dataset on donnees.montreal.ca (CKAN search "21-042",
  "divulgation", "cotation GES") is *"Consommation d'énergie et émissions de gaz à effet de serre des bâtiments
  municipaux de 2000 m² et plus"* (https://donnees.montreal.ca/dataset/consommation-emissions-batiments-municipaux,
  CC BY 4.0). It has yearly CSVs for 2019-2020 (pre-bylaw) and 2021, 2022, 2023. So the open data cover
  **municipal** buildings only. The bylaw page
  (https://montreal.ca/articles/reglement-sur-la-divulgation-et-la-cotation-ges-des-grands-batiments-20548)
  applies to all commercial, institutional and residential buildings of 2,000 m² or more, or 25 dwellings or more,
  and asks owners to report "de leur bâtiment", which is whole-building. RV14's "large-building disclosure open
  data" overstates what is published.
- **Grade: FIX.** Cite the Montréal dataset by its real title (municipal buildings), or drop it. SECMURBs and SCIEU
  are fine to cite for existence.
- References:
  - Natural Resources Canada (n.d.) *Survey of Energy Consumption of Multi-Unit Residential Buildings (SECMURBs)
    2018: Data Tables*. Ottawa: Office of Energy Efficiency.
    https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/murb/2018/tables.cfm (accessed ...). **Year of
    release not seen; the author fills it or uses the accessed date only.**
  - Ville de Montréal (2026) *Consommation d'énergie et émissions de gaz à effet de serre des bâtiments municipaux
    de 2000 m² et plus* [open data, Règlement 21-042]. https://donnees.montreal.ca/dataset/consommation-emissions-batiments-municipaux
    (accessed ...).

### M22. `04_Discussion.md:17`, "[REF NEEDED: ATUS source]"

- **Exists: yes.** https://www.bls.gov/tus/ (read through WebFetch; curl got HTTP 403) has the page title "American
  Time Use Survey". Its latest release is dated 06/25/2026 ("35% of employed people do some work at home on days
  they work in 2025"). The page suggests no citation format.
- **Supports?** Yes, as an existence citation for a national time-use survey. The sentence only names ATUS as a
  candidate data source.
- **Grade: VERIFIED.**
- Reference: U.S. Bureau of Labor Statistics (2026) *American Time Use Survey*. Washington, DC: U.S. Department of
  Labor. https://www.bls.gov/tus/ (accessed ...).

### M24. `08_AppendixA_Table1.md`, Yamaguchi and Shimoda (2017) as a Table A.1 competitor

- **Exists? NO, in either version.**
  - DOI `10.1016/j.apenergy.2017.01.011`, given by both RV09 and RV12, resolves in Crossref to *García-Gusano, D.,
    Iribarren, D., Garraín, D. "Prospective analysis of energy security: A practical life-cycle approach focused on
    renewable power generation and oriented towards policy-makers", Applied Energy 190, pp. 891-901 (2017)*
    (https://api.crossref.org/works/10.1016/j.apenergy.2017.01.011).
  - RV12's title ("A stochastic model to predict occupants' presence and energy use in commercial and residential
    buildings based on time use survey", AE 200, 160-174): no Crossref or OpenAlex match.
  - RV09's title ("Development of a district energy system simulation tool for carbon-neutral district planning",
    AE 190, 685-703): no match either.
  - A Crossref author search (Yamaguchi and Shimoda, Applied Energy ISSN 0306-2619, 2016-06 to 2018-06) returns no
    such paper.
- **Grade: REJECT.** Table A.1 stays as it is.

### M25. `09_AppendixB_Equations.md:17`, "[REF NEEDED: source for class-weighted cross-entropy and the matching logit adjustment]"

**(a) King and Zeng (2001)**
- **Exists: yes.** Crossref (https://api.crossref.org/works/10.1093/oxfordjournals.pan.a004868) gives: "Logistic
  Regression in Rare Events Data", Gary King, Langche Zeng. *Political Analysis* 9(2), pp. 137-163, 2001. This
  matches the vetting file.
- **Supports?** Yes. The free author copy (https://gking.harvard.edu/files/0s.pdf) contains:
  - Sec. 4.1, "Prior Correction".
  - Appendix B.4, Eq. (29): the slope estimate "need not be changed, but the constant term should be corrected by
    subtracting out the bias factor, ln[((1 − τ)/τ)(ȳ/(1 − ȳ))]". It adds: "Equation (29) also applies to any other
    model with a logit output function. For example, for a feed forward neural network model with a logit output".
  - This is the exact form of σ(z − ln 49). One caveat: King and Zeng derive it for over-sampling the ones.
    Up-weighting positives by 49 is the equivalent case, and the author should say that in one clause.
- **Grade: VERIFIED.**

**(b) Menon et al. (2021)**
- **Exists: yes.** arXiv:2007.07314v2 (https://export.arxiv.org/api/query?id_list=2007.07314) gives "Long-tail
  learning via logit adjustment", Aditya Krishna Menon, Sadeep Jayasumana, Ankit Singh Rawat, Himanshu Jain,
  Andreas Veit, Sanjiv Kumar, with the comment "Published as a conference paper in ICLR 2021". OpenReview
  (id 37nvvqkCo5) lists the venue as "ICLR 2021 Spotlight". This matches the vetting file.
- **Supports?** Yes, the general principle. The full text (Eq. 9) predicts `argmax f_y(x) − τ·log π_y`, "a
  label-dependent offset to each of the logits", applied post-hoc. It is written for multi-class softmax with
  class priors, not for a binary positive-class weight, so King and Zeng is the closer source for the exact form.
- **Grade: VERIFIED.**

References:
- King, G. and Zeng, L. (2001) Logistic regression in rare events data. *Political Analysis*, 9(2), pp. 137-163.
  https://doi.org/10.1093/oxfordjournals.pan.a004868
- Menon, A.K., Jayasumana, S., Rawat, A.S., Jain, H., Veit, A. and Kumar, S. (2021) Long-tail learning via logit
  adjustment. In: *International Conference on Learning Representations (ICLR 2021)*. arXiv:2007.07314.

### M26. `11_References.md:5`, Guideline 14 edition

- **Exists: yes, 14-2014.** Google Books
  (https://books.google.com/books/about/Ashrae_Guideline_14_2014.html?id=zlJkAQAACAAJ) gives: "Ashrae Guideline
  14-2014: Measurement of Energy, Demand and Water Savings", ASHRAE, 2014, 145 pages. **No ISBN is shown.**
- Search results show that **Guideline 14-2023 supersedes 14-2014**: the ANSI webstore
  (https://webstore.ansi.org/standards/ashrae/ashraeguideline142023) and ASHRAE's own "What Is Contained in
  Guideline 14-2023" PDF. I saw these as search results only. The ANSI and Accuris store pages returned 403.
- **ISBN 978-1-936504-80-0:** its check digit is valid, but it is not shown on Google Books, returns nothing on Open
  Library (`search.json?isbn=9781936504800`, 0 hits), and a web search gave no match. **Unconfirmed.**
- **Grade: FIX.** Print the edition year without the ISBN. The author picks the edition (2014 or 2023) behind SI
  Table S1, and checks whether the SI cites Guideline 14 at all, since chapters_v2 does not.
- Reference: ASHRAE (2014) *ASHRAE Guideline 14-2014: Measurement of Energy, Demand, and Water Savings*. Atlanta,
  GA: American Society of Heating, Refrigerating and Air-Conditioning Engineers.

### M28. `11_References.md:19`, Alberta Tourism Market Monitor (repo-based replacement for CBRE)

- **Exists: yes.** The open.alberta.ca CKAN API gives:
  - Dataset `1648658d-ec8e-4bf0-98d6-23bdf172ac4a`, titled "Alberta tourism market monitor : monthly update
    [2022]". Organisation: Jobs, Economy and Northern Development. It holds monthly PDFs January-November 2022,
    plus a "SEE ALSO: issues ... for other years" link.
  - A title search returns one dataset per year for **2011 to 2022** (names `6848998-2011` ... `6848998-2021`, and
    `6848998` for 2022). That matches the Step 1 span of AB 2011-2022.
- **Supports?** Yes, as the source of the Alberta monthly occupancy series.
- **Note for the author.** `02_Framework.md:36` says "the last three months of 2022, missing from the Alberta
  series". The 2022 dataset does list **October and November 2022** issues; only December is absent. Check whether
  the occupancy-rate row is missing inside those two issues, or correct the sentence.
- **Grade: VERIFIED.** Also cite the 2011-2021 issues and add an accessed date.
- Reference: Government of Alberta (2011-2022) *Alberta Tourism Market Monitor: Monthly Update* (monthly issues,
  2011 to 2022). Edmonton: Government of Alberta. https://open.alberta.ca/dataset/1648658d-ec8e-4bf0-98d6-23bdf172ac4a
  and the yearly datasets for 2011-2021 (accessed ...).

### M30. `11_References.md:21`, ISQ (repo-based replacement)

- **Exists: yes.** The quebec.ca dashboard
  (https://www.quebec.ca/tourisme-loisirs-sport/services-industrie-touristique/etudes-statistiques/tableaux-de-bord-donnees-tourisme/hebergement-touristique-camping/enquete-frequentation-par-region)
  has the title "Résultats de l'Enquête sur la fréquentation des établissements d'hébergement du Québec – Par
  région touristique et par MRC". Its notes say the survey is "réalisée mensuellement par l'Institut de la
  statistique du Québec pour le compte du ministère du Tourisme".
- The ISQ survey page is https://statistique.quebec.ca/en/enquetes/en-cours-de-collecte/survey-on-quebec-accomodation-establishment-occupancy.
- Our export's source line (`Leg3_4-split/deepResearch_v2/2022-province-mensuelle.txt:23`) reads: "Institut de la
  statistique du Québec, Enquête sur la fréquentation des établissements d'hébergement (régions et MRC/villes)".
  That matches.
- No table identifier is shown on either page.
- **Grade: VERIFIED.** Use the dashboard URL and an accessed date in place of a table ID.
- Reference: Institut de la statistique du Québec (2026) *Enquête sur la fréquentation des établissements
  d'hébergement* (régions et MRC/villes), monthly data. Tableau de bord, Gouvernement du Québec, ministère du
  Tourisme. https://www.quebec.ca/tourisme-loisirs-sport/services-industrie-touristique/etudes-statistiques/tableaux-de-bord-donnees-tourisme/hebergement-touristique-camping/enquete-frequentation-par-region
  (accessed ...).

### M31. `11_References.md:33`, SCIEU year and table

**What NRCan publishes.** Both years are online:
- **2019:** https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm, titled "Survey of
  Commercial and Institutional Energy Use (SCIEU) - Buildings 2019 – Data Tables". Table 1 is "Building and
  Establishment characteristics by primary activity, 2019". The page states: "As a result of fundamental
  methodological improvements to SCIEU 2019, this dataset is not comparable with earlier published SCIEU data for
  2009 and 2014."
- **2014:** https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2014/tables.cfm, titled "...
  Buildings 2014 – Data Tables". Table 1 is "Building characteristics, energy use and energy intensity by primary
  activity, 2014".

**RV12's identifiers are wrong.**
- StatCan IMDB record **SDDS 5032** is "Computer and peripherals price indexes (CPPI)"
  (https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5032). SCIEU is **record number 5034**
  (https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5034).
- The catalogue page `www150.statcan.gc.ca/n1/en/catalogue/57-603-X` returns HTTP 404.

**What the Step 9 code actually loads.**
- `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` loads **no SCIEU table file**. No file named
  `*scieu*` exists anywhere under `Leg3_4-split`.
- SCIEU enters only as hard-coded INFO tuples, not gates:
  - office `info=(230.0, 170.0, 360.0), info_src="SCIEU/CEUD"` (line 167), with no year;
  - retail `info=(280.0, 150.0, 380.0), info_src="dr_L3-02 empirical"`. That report
    (`Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md:75`) attributes 280.6 to "SCIEU 2019 Retail –
    non-food";
  - hotel `info=(350.0, 220.0, 480.0), info_src="dr_L3-03 empirical"`. That report (`dr_L3-03...REPORT.md:111`)
    says "SCIEU 2014 and 2019".
- The Step 9 doc (`3rdJ_09_activityDrivenLoads_4split.md:110`) lists "NRCan SCIEU 2019".
- So the only year signal is "2019", and it comes from unvetted Gemini reports. The code itself carries no year.
  The office 230 has no year at all.

**Grade: FIX.**
- Drop "SDDS 5032" and "57-603-X".
- The author confirms which year, if any, the INFO values rest on. If the values are not re-derived from an NRCan
  table, consider not citing SCIEU as a source of numbers.
- SCIEU is also not cited in the chapters_v2 body (see Orphans).

Reference (if kept, 2019): Natural Resources Canada (n.d.) *Survey of Commercial and Institutional Energy Use
(SCIEU) – Buildings 2019: Data Tables*. Ottawa: Office of Energy Efficiency.
https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm (accessed ...). **Release year
not seen on the page; use the accessed date only unless the author confirms it.**

### M33. `11_References.md:29`, NECB 2017 ISBN

- **Check digit arithmetic.**
  - `0-660-24321-4` fails the ISBN-10 check: weighted sum mod 11 = 4. The valid check digit for `0-660-24321-` is
    **0**.
  - `978-0-660-24321-4` passes as an ISBN-13.
  - `978-0-660-24718-2` passes as an ISBN-13.
- **What the authorities print.**
  - NRC Publications Archive (https://nrc-publications.canada.ca/eng/view/object/?id=3eea8f31-47ef-4280-86b0-1c148744f8f1)
    shows "ISBN 0-660-24321-4", 341 p., "Fourth Edition 2017", NRC number NRC-CONST-56215.
  - DataCite for DOI 10.4224/40002011 (https://api.datacite.org/dois/10.4224/40002011) gives: title "National
    Energy Code of Canada for Buildings: 2017"; creators Canadian Commission on Building and Fire Codes and Natural
    Resources Canada; publisher National Research Council Canada, 2017; ISBN "0-660-24321-4".
  - So **NRC itself prints the invalid ISBN-10**, and **978-0-660-24321-4 appears on no page I opened**.
  - Government of Canada Publications, record for **NR24-24/2017E-PDF**, which is the catalogue number our entry
    cites (https://publications.gc.ca/site/eng/9.850873/publication.html), gives: "ISBN 9780660247182 Catalogue
    number NR24-24/2017E-PDF ... Edition 4th ed., 2nd printing". It also notes: "The catalogue number
    (NR24-24/2017E) and ISBN (0660243214) for the print edition have been copied in this electronic publication."
- **Grade: FIX.** The vetting file's proposed `978-0-660-24321-4` is not shown by any authority. Print the ISBN that
  belongs to the cited PDF catalogue number, or drop the ISBN and keep the DOI.
- Reference: National Research Council Canada (2017) *National Energy Code of Canada for Buildings 2017*, Fourth
  Edition. Ottawa: Canadian Commission on Building and Fire Codes (Cat. NR24-24/2017E-PDF; ISBN 978-0-660-24718-2).
  https://doi.org/10.4224/40002011

### M34. `11_References.md:13`, Doma and Ouf (2023) DOI

- **The DOI exists.** Crossref (https://api.crossref.org/works/10.26868/25222708.2023.1671) gives: proceedings
  article "Leveraging mobile positioning data to model building occupant behaviour in a mixed-use district", Aya
  Doma, Mohamed Ouf, "Proceedings of Building Simulation 2023: 18th Conference of IBPSA", 2023-09-04. The DOI
  resolves to https://publications.ibpsa.org/conference/paper/?id=bs2023_1671.
- **Pages in our entry are wrong.** The IBPSA landing page shows **Pages: 596 - 603**, and the PDF's own footer
  runs "0596" to "0603" (8 pages). Our entry prints "pp. 1671-1678"; 1671 is the paper ID, not a page.
- The title printed in the PDF itself reads "...to Model Building **Occupancy** in a Mixed-use District". Crossref
  and the IBPSA landing page both give "occupant behaviour", which matches our entry, so keep it (Crossref wins).
- **Grade: FIX** (add the DOI, correct the pages).
- Reference: Doma, A. and Ouf, M. (2023) Leveraging mobile positioning data to model building occupant behaviour in
  a mixed-use district. *Proceedings of Building Simulation 2023: 18th Conference of IBPSA*, pp. 596-603.
  https://doi.org/10.26868/25222708.2023.1671

### M39. `02_Framework.md:28` and `SI_additions.md:23`, Jensen-Shannon divergence (optional, no placeholder)

- **Exists: yes.** Crossref (https://api.crossref.org/works/10.1109/18.61115) gives: "Divergence measures based on
  the Shannon entropy", J. Lin. *IEEE Transactions on Information Theory* 37(1), pp. 145-151, 1991. This matches
  the vetting file.
- **Supports?** The abstract (OpenAlex) introduces "a novel class of information-theoretic divergence measures based
  on the Shannon entropy" that "do not require the condition of absolute continuity". It does not use the words
  "Jensen-Shannon". The paper body is paywalled (IEEE); the author confirms that the JS form is defined there.
- **Grade: VERIFIED-METADATA-ONLY.**
- Reference: Lin, J. (1991) Divergence measures based on the Shannon entropy. *IEEE Transactions on Information
  Theory*, 37(1), pp. 145-151. https://doi.org/10.1109/18.61115

### G (no M number). Goel et al. (2014), RV11's second source for Eq. 1 (`02_Framework.md:38-42`)

- **RV11's DOI is wrong.** `10.2172/1132646` returns 404 at Crossref, and OSTI record 1132646 is "Structural basis of
  HIV-1 Vpu-mediated BST2 antagonism ..." (eLife).
- **The report exists under another DOI.** The OSTI API (https://www.osti.gov/api/v1/records/1129366) gives:
  "Enhancements to ASHRAE Standard 90.1 Prototype Building Models", Goel, S., Athalye, R.A., Wang, W., Zhang, J.,
  Rosenberg, M.I., Xie, Y., Hart, P.R., Mendon, V.V. Report **PNNL-23269**, April 2014, DOI **10.2172/1129366**. A
  second OSTI record (10.2172/1764628) has the same report number.
  - This also corrects 2J's "not found on Crossref": Crossref has it as a report.
- **Supports?** Not shown. The OSTI abstract describes prototype enhancements (design assumptions, accuracy,
  infrastructure) and does not mention hotel guest-room schedules. The author opens the free PDF on OSTI to confirm
  a Large Hotel schedule is there, or drops it (Deru et al. 2011 is TRUSTED-2J for the schedule).
- **Grade: FIX** (DOI). Support is unconfirmed.
- Reference (only if support is confirmed): Goel, S., Athalye, R.A., Wang, W., Zhang, J., Rosenberg, M.I., Xie, Y.,
  Hart, P.R. and Mendon, V.V. (2014) *Enhancements to ASHRAE Standard 90.1 Prototype Building Models*. PNNL-23269.
  Richland, WA: Pacific Northwest National Laboratory. https://doi.org/10.2172/1129366

### X1 (new lead, not in the vetting file). Happle, Fonseca and Schlueter (2020), for M5 and optionally M18

- **Exists: yes.** Crossref and OpenAlex (https://api.crossref.org/works/10.1016/j.apenergy.2020.115594) give:
  "Impacts of diversity in commercial building occupancy profiles on district energy demand and supply", Gabriel
  Happle, Jimeno A. Fonseca, Arno Schlueter. *Applied Energy* 277, 115594, November 2020.
- **RV09 and RV12 got this paper wrong.** They give this DOI either as "Fonseca, Nguyen, Schlueter, Marechal (2020)"
  with this title, or as "Fonseca et al. (2020) The City Energy Analyst v3.0". Both author lists are wrong; Crossref
  wins.
- **Supports M5?** Yes, for the plant-sizing half. The abstract: "occupancy profiles are highly sensitive
  parameters for district energy demand predictions ... the choice of UBOP influences the cooling demand to the
  degree that district cooling system design decisions might be impacted". It is a district (Singapore) study, not
  a single tower, and says nothing about the grid peak.
- **Supports M18?** It fits "occupancy detail is often assumed to matter" for system design. It does not use the
  word "peak".
- **Grade: VERIFIED** (for M5, plant-sizing half).
- Reference: Happle, G., Fonseca, J.A. and Schlueter, A. (2020) Impacts of diversity in commercial building
  occupancy profiles on district energy demand and supply. *Applied Energy*, 277, 115594.
  https://doi.org/10.1016/j.apenergy.2020.115594

---

## Summary table

| row id | placeholder location (current) | grade | what the author still must do |
|---|---|---|---|
| M4 | 01_Introduction.md:5 (already filled) | REJECT | nothing; the DOI belongs to Jung et al. (2022), a heat-pump review; title not found |
| M5a | 01_Introduction.md:11 | REJECT | do not cite Fonseca et al. (2016) here; its abstract is about the CEA framework, not diversity or peak |
| M5b | 01_Introduction.md:11 | VERIFIED-METADATA-ONLY | open ASHRAE 2021 Fundamentals Ch. 18 and confirm it covers diversity in plant sizing; never print "15-35 %" |
| X1 | 01_Introduction.md:11 (and 04_Discussion.md:7) | VERIFIED | consider Happle et al. (2020) for the plant-sizing half; the grid-peak half still needs a source |
| M9 | 02_Framework.md:30 | VERIFIED | confirm the training code really applies PCGrad |
| M11 | 02_Framework.md:36 | VERIFIED-METADATA-ONLY | confirm the seasonal-models chapter in the 5th edition; print no pages |
| M12 | 02_Framework.md:36 (optional) | VERIFIED | optional; cite for the pulse and level-shift intervention |
| (new) | 02_Framework.md:36, hotel recovery levels 0.615 / 0.635 | no candidate | supply the source; no report offered one |
| G | 02_Framework.md:38-42, Eq. 1 | FIX | use DOI 10.2172/1129366 (PNNL-23269), not 10.2172/1132646; open the OSTI PDF to confirm a hotel schedule, or drop it |
| M15 | 02_Framework.md:85 (optional) | VERIFIED-METADATA-ONLY | optional; confirm Fisher covers a weighted mean direction |
| M17 | 02_Framework.md:89 | VERIFIED-METADATA-ONLY | open one of IEEE Std 100-2000, Grainger and Stevenson (1994) or ASHRAE (2021), quote its CF definition, cite that one; no RV11 pages |
| M39 | 02_Framework.md:28; SI_additions.md:23 (optional) | VERIFIED-METADATA-ONLY | optional; confirm the JS definition in the paper body |
| M18 | 04_Discussion.md:7 | VERIFIED (Doma 2024) | cite Doma et al. (2024) for the occupancy-and-peak link only (112 buildings, up to 17 % peak reduction), not for cross-use diversity; optionally add X1 |
| M19 | 04_Discussion.md:15 | FIX | cite SECMURBs 2018 (murb URL) and SCIEU 2019 for existence; the Montréal open data cover municipal buildings only, so use that title or drop it |
| M22 | 04_Discussion.md:17 | VERIFIED | add the accessed date |
| M24 | 08_AppendixA_Table1.md | REJECT | leave Table A.1 as it is; neither Yamaguchi paper exists and the DOI belongs to García-Gusano et al. |
| M25 | 09_AppendixB_Equations.md:17 | VERIFIED (both) | cite King and Zeng (2001), Eq. 29, as the exact form, with Menon et al. (2021) optional; add one clause that up-weighting positives equals over-sampling them |
| M26 | 11_References.md:5 | FIX | the ISBN is unconfirmed, so drop it; choose 14-2014 or 14-2023 (2023 supersedes 2014) to match SI Table S1; check the SI cites it at all |
| M28 | 11_References.md:19 | VERIFIED | cite the 2011-2022 issues and add an accessed date; check the "last three months of 2022 missing" claim, since the October and November 2022 issues are listed |
| M30 | 11_References.md:21 | VERIFIED | use the quebec.ca dashboard URL and an accessed date; no table ID exists on either page |
| M31 | 11_References.md:33 | FIX | drop SDDS 5032 (that is a price index; SCIEU is 5034) and 57-603-X (404); decide the year, since the code loads no SCIEU file and carries no year; or delete the orphan entry |
| M33 | 11_References.md:29 | FIX | for Cat. NR24-24/2017E-PDF print ISBN 978-0-660-24718-2 (GC Publications), or drop the ISBN; 978-0-660-24321-4 appears on no authority page |
| M34 | 11_References.md:13 | FIX | add DOI 10.26868/25222708.2023.1671 and correct the pages to 596-603 (not 1671-1678) |

**Counts (22 graded rows: the 19 M-rows with M5 split into M5a and M5b, plus G and X1):**
- VERIFIED 8: M9, M12, M18, M22, M25, M28, M30, X1
- VERIFIED-METADATA-ONLY 5: M5b, M11, M15, M17, M39
- FIX 6: G, M19, M26, M31, M33, M34
- REJECT 3: M4, M5a, M24
- AUTHOR-OPENS 0

Every row could be checked online at least for existence.
