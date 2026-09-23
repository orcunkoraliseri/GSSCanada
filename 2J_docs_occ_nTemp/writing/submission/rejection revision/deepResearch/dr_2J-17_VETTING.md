# Vetting: dr_2J-17 (a source for every equation)

Return: `dr_2J-17_equation_sources_gemini_results.md` (Gemini Antigravity, 2026-09-22).
Scope: Crossref lookup of every DOI the return gives for a source we use; arXiv lookup of the one
preprint id; our own code and Step-7 metabolic-map document for the two value tables. No new
literature search.

## Step 1: positive control
Richardson, Thomson and Infield (2008), DOI 10.1016/j.enbuild.2008.02.006: SUCCEEDED (return
reports the correct Crossref record; already in our reference list with the same metadata). Note:
the return's chat summary adds a fourth author "Clifford" to this 2008 paper; the results file itself
is correct. Return not discarded.

## Step 2: Crossref, sources we use
| Source | Crossref / check | Verdict |
|---|---|---|
| Richardson et al. 2009, EB 41(7) 781-789, 10.1016/j.enbuild.2009.02.010 | match (4 authors) | USED |
| Richardson et al. 2010, EB 42(10) 1878-1887, 10.1016/j.enbuild.2010.05.023 | match (4 authors) | USED |
| Caruana 1997, Mach. Learn. 28(1) 41-75, 10.1023/A:1007379606734 | match | USED |
| Deming and Stephan 1940, AMS 11(4) 427-444, 10.1214/aoms/1177731829 | match | USED |
| Herrmann et al. 2024, JSHS 13(1) 6-12, 10.1016/j.jshs.2023.10.010 | DOI, title, pages match; **author list in the return is WRONG** (lists Macera, Powell, Leon...; Crossref: Herrmann, Willis, Ainsworth, Barreira, Hastert, Kracht, Schuna, Cai, Quan, Tudor-Locke, Whitt-Glover, Jacobs) | USED as "Herrmann, S.D. et al." |
| Deru et al. 2011, NREL/TP-5500-46861, 10.2172/1009264 | match (13 authors) | USED |
| Vaswani et al. 2017, arXiv 1706.03762 | arXiv title matches | USED (NeurIPS 30, pp. 5998-6008) |
| Goel et al. 2014, PNNL-23269, 10.2172/1132646 | **not found on Crossref** | DROPPED (Deru 2011 carries the fixed-schedule source) |
| Aerts et al. 2014, 10.1016/j.buildenv.2014.01.015 | **wrong DOI**: resolves to a classroom-ventilation paper (Gao, Wargocki, Wang). Our reference list already has the correct DOI ...01.021 (checked) | not changed |
| Books: Goodfellow et al. 2016, Cochran 1977, Mardia and Jupp 2000, Montgomery and Runger 2018 | ISBN lookups blocked (Open Library empty, Google Books quota). Identity, publisher, year and edition are standard; printed without ISBN or page numbers | USED, no page numbers |
| NRCan SHEU-2019 data tables | page opens, title "2019 Survey of Household Energy Use (SHEU-2019) Data Tables"; no release date on page | USED as Natural Resources Canada (2019), accessed date |

## Step 3: claims checked against our own material
- Eq. B.7 metabolic lookup: the return's "Compendium MET x 70 W" basis matches our own Step-7
  verification (`2J_docs_occ_nTemp/07_metabolicMap_verification.md`, author-provided Compendium PDF;
  sleeping 1.0 MET = 70 W, eating seated 1.5 MET = 105 W). The return read that file, so this is not
  independent; the source PDF is the check. Paper now states "follow the Compendium, converted at 70 W
  per MET".
- Eq. 1 sharing factor eta = 1, 1.4, 1.7, 1.9, 2.0 (`activity_loads.py:54-58`): code comment says
  "Richardson 2008"; the return finds no published table with these values (concept only, Richardson
  2009 effective occupancy). Paper now says the FORM follows Richardson et al. (2009) and the values
  are set in this study. The return's "Terry and Palmer 2013" formula is not used (unverified).

## Steps 4-7: not used
Page-number locations for textbooks (e.g. "Eq. 10.15, p. 368") are unverified and not printed.
Grainger and Stevenson / Wood et al. for load factor, Deville and Sarndal, Fisher, Guglielmetti,
Haldi and Robinson, Armstrong-as-calibration-precedent, Chen-as-average-profile support: not needed,
not added. ASHRAE 2021 not added.

## Outcome in the paper
OWN (stated once, Appendix B intro): B.1, B.2, B.4-B.6, main Eqs. 3, 4, 6.
Cited in Section 2: Eq. 1 (Widen and Wackelgard 2010; Richardson et al. 2010; eta form Richardson et
al. 2009), Eq. 2 (NRCan 2019), Eq. 3 idea (Barrero et al. 2023), Eq. 5 and B.11 (Montgomery and
Runger 2018), B.3 (Vaswani et al. 2017; Caruana 1997; Goodfellow et al. 2016), B.4-B.5 contrast
(Deming and Stephan 1940), B.7 (Herrmann et al. 2024), B.8 (Cochran 1977), B.9-B.10 (Mardia and Jupp
2000), ramp (Denholm et al. 2015), B.12 (Deru et al. 2011). Reference list 36 -> 48.
