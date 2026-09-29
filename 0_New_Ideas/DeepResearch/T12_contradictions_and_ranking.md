# T12. Contradictions and ranking of the surviving angles

Paste `00_MASTER_BRIEF.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh
session. **Run alone.** Written 2026-09-19 by the manager, after every report `RT01` to `RT38` was
vetted.

## Why this prompt looks different

Thirty-eight reports have been vetted. In the last rounds the page logs were honest: every logged
excerpt was found again on its page. The failures were all in the text written after the fetching:
papers called "read" when only their CrossRef metadata was fetched, quotes that are on no page,
numbers that contradict the PDF the tool itself downloaded, log line numbers that point at the wrong
fetch, and self-grades ("verified") that the log contradicts.

So this prompt gives you the checked facts as a numbered table (`P1` to `P40` below) and asks
numbered questions. You write no free landscape. **Every sentence you write that states a fact ends
with a tag**:

* `[Pn]`: the fact is row `Pn` of the table below, used as it is written there;
* `[Ln]`: the fact is on the page logged at line `n` of your `RT12_pages.log` (lines counted from 1
  in the final file); several tags are allowed, as `[L12, L40]`;
* `[BRIEF s.n]`: the fact is in section `n` of the master brief;
* `[INFERENCE]`: your own reasoning, not a fact.

A factual sentence with no tag is struck by the vetter. A tag that points at a line whose excerpt does
not support the sentence is struck, and more than five such tags void the report.

## Rules (they win over the brief and the template where they differ)

* Read only three files: `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and this prompt. Open no other
  file in the project: no `RT` report, no `VETTING_*.md` note, no `*_round1.md`, nothing in `_scan/`.
* Write only two files, in `5J_docs_occ/DeepResearch/`: `RT12_contradictions_and_ranking.md` and
  `RT12_pages.log`. Creating, editing, renaming or deleting any other file in the project voids the
  report. Scratch scripts go outside `C:\Users\o_iseri\Desktop\GSSCanada\`. Scripts may fetch and
  log; no script may write report text.
* **Finish the log before you write the report**, and do not add to the log afterwards. Then the line
  numbers you cite are final.
* The page log has one line per page, API call or search query, written when you open it,
  tab-separated: time as `YYYY-MM-DDTHH:MM:SS`, the full URL or query string, the HTTP status, and
  about 200 characters copied verbatim from the body as returned. Log every call, including the ones
  you make only to look around.
* A page counts as opened only if it returned 200 **and** its logged excerpt is readable text of the
  thing you cite. An error, a bot block, an image, a script shell or a login page is `COULD NOT
  OPEN`, never "opened" or "read". If a page matters and the excerpt is boilerplate, fetch the part of
  the page that holds the text you need and log it as its own line.
* **A CrossRef record proves that a work exists, not what it says.** Any sentence about what a work
  did, found or measured needs a logged abstract or full text: the OpenAlex abstract
  (`https://api.openalex.org/works/https://doi.org/<DOI>`, rebuild `abstract_inverted_index`), the
  arXiv abstract page, or the publisher's page with the abstract in the excerpt. If you have only the
  CrossRef record, write `TITLE ONLY` and say nothing about the content. If OpenAlex returns 429,
  wait and retry, and log each try.
* Every DOI you give carries, beside it, the title CrossRef returns, and the author list pasted from
  that CrossRef record. If CrossRef lists two authors, you list two. One work carries one DOI in every
  section.
* A number is written only if it appears on a logged page, with its table or page where the source
  has one. Copy it exactly; never round, sum or recompute a published figure.
* Every "no study", "not found", "open" or "unclaimed" lists its queries beside it, each with its log
  line. Say it as "these queries found nothing", never as "none exists".
* Do not split the difference. Where two claims disagree, one of them is right, both are wrong, or
  you could not open the source. Averaging, "somewhere between" or "both may be valid" is not an
  answer.
* Do not introduce a new angle. The angles are the brief's `A1` to `A10` and `A14`, plus `A11`,
  `A12`, `A13`, defined in `P33` to `P35`.
* Do not grade your own report: never write "verified", "confirmed", "definitive", "comprehensive"
  or "without exception" about your work. The log is the evidence.
* Say nothing about our own models, results or numbers beyond what brief section 2 states. Name no
  individuals connected to the fellowship programmes. Never propose a change to the 4J pre-registered
  gate, null or threshold. No em dashes and no en dashes, in the report or the log.

## The checked facts (filled by the manager, 2026-09-19)

Each row is a fact that a checker found at its source. The last column names the vetting note that
holds the check; you may not open it, and you do not need to. "Pointer" means the work exists and is
correctly identified, and nobody has read it for us.

### Angles already decided (do not rank these; do not reopen them without a logged source)

| # | Fact | Held in |
|---|---|---|
| P1 | `A1` is closed as a paper, except an error-diagnostician form with a scripted ablation. Prior work with a logged abstract: Geo2UBEM (Wu et al., arXiv 2026), an autonomous multi-agent UBEM framework calibrated on six Purdue campus buildings (101,170 m2) | `VETTING_RT03`, `VETTING_RT02` |
| P2 | `A10` is closed as a paper; at most a short communication or an appendix. Kontokosta and Tull 2017 is the one checked empirical test of area weighting. Lim and Koo 2026 benchmark 3,001 buildings in Seoul (abstract) | `VETTING_RT16`, `VETTING_RT02` |
| P3 | `A5` is dropped: no report produced a supporting row for it | ideas document, ledger |
| P4 | `A3` is closed as a "beat the null" paper. What remains is a "cross-national pretrained generative sequence model" framing on corpora we can hold; the "foundation model" label is closed. MTUS and ATUS are open to a Canadian university; the Eurostat scientific-use files are closed to us | `VETTING_RT13`, `VETTING_RT07` |
| P5 | A hybrid "donor plus edit" generator was recommended by one report on rows that were struck or author-reported; it is a claim to test, not a finding | `VETTING_RT13` |

### Facts about the open angles

| # | Fact | Held in |
|---|---|---|
| P6 | `A2`: overheating assessed on static archetypes is taken; `A2` is open only with a presence module. The report returned NOT FOUND for heat-responsive presence and for indoor overheating validated at dwelling level | `VETTING_RT05` |
| P7 | `A2`: address-level income and bills are reachable only through the research data centres, which limits an exposure result to tract-level aggregation | `VETTING_RT10` |
| P8 | Heat-responsive presence at population scale: three logged queries found nothing. Weak evidence of absence | `VETTING_RT04` |
| P9 | A building-energy model coupled to time-activity data for heat exposure, and an energy-poverty indicator that uses time at home: logged queries found nothing for either. Weak evidence of absence | `VETTING_RT08` |
| P10 | British Columbia, summer 2021, Coroners review "Extreme Heat and Human Mortality: A Review of Heat-Related Deaths in B.C. in Summer 2021", 619 deaths: 98 % of heat injuries occurred indoors (pages 5, 17); 67 % aged 70 or older (page 5); 56 % lived alone (page 5, Table 8); 452 of 619, 73.0 %, in private residences (Table 7, page 38); air conditioning present 7.4 %, absent 66.9 %, unknown 24.1 % (Table 11, page 39) | `VETTING_RT08` |
| P11 | Chicago, July 1995, Semenza et al. 1996 (New England Journal of Medicine, DOI 10.1056/NEJM199607113350203), abstract: not leaving home each day, odds ratio 6.7; a working air conditioner, odds ratio 0.3 | `VETTING_RT08` |
| P12 | Pointers: Multnomah County 2021 final heat report, 68 of 72 (94 %) died in their own residence (page 10); Ballester et al. 2023, Nature Medicine, 61,672 heat-related deaths in Europe in summer 2022 (abstract) | `VETTING_RT08` |
| P13 | `A4` is open at the intersection of future population, future weather and stock change; fewer than five studies were found, and none with demographic occupancy. Its cost is a full factorial run matrix and a hindcast. No UBEM hindcasting study was found. Reyna and Chester 2017 and Sandberg et al. 2016 are correctly identified | `VETTING_RT14` |
| P14 | `A4`: the future peak-demand claim depends on an air-conditioning uptake assumption | `VETTING_RT05` |
| P15 | `A6`: Katia et al. 2023 and Heidelberger and Rakha 2022 (socioeconomic data in UBEM) are correctly identified pointers; Walker and Day 2012 and Sovacool and Dworkin 2015 (energy justice) likewise | `VETTING_RT08` |
| P16 | `A7` is partly taken for material stock (Schmid 2025 resolves). `A7` breaks the series signature (no occupancy, no time use). It is feasible on paper, with a fallback to categorical classification | `VETTING_RT01`, `VETTING_RT11`, `VETTING_RT10` |
| P17 | `A7`: three logged CrossRef phrasings found no precedent for records reading with abstention feeding a stock model. Weak evidence of absence | `VETTING_RT02` |
| P18 | `A7` pointers: Zhang et al. 2023, arXiv:2311.08535, uses language models to process three open municipal building datasets (abstract). Identity only: Pan et al. 2026 (DOI 10.1016/j.autcon.2026.106791), Gunay et al. 2023 (DOI 10.1016/j.buildenv.2023.110848, municipal housing permit data for the Canadian stock), Borrotti 2024 (DOI 10.3390/en17174348, conformal prediction for heating and cooling load in building simulation), Angelopoulos and Bates 2023 (DOI 10.1561/2200000101) | `VETTING_RT17` |
| P19 | `A7` data: Toronto building permits are under the Open Government Licence (Toronto); England EPC data under the Open Government Licence v3.0 | `VETTING_RT17` |
| P20 | `A8`: Shirzadi et al. tested seven NECB 2020 reference models (abstract). Open building-level disclosure data was not found for Montreal or Calgary. Montreal by-law 21-042 covers buildings of 2,000 m2 or more, or 25 or more homes; Ontario O. Reg. 506/18 covers buildings of 50,000 sq ft or more | `VETTING_RT02`, `VETTING_RT16`, `VETTING_RT34` |
| P21 | `A9` is open on two terms only: occupancy that varies with who lives there, and district scale. Searches found no survivability study with dynamic or demographic occupancy (three reports agree) | `VETTING_RT15`, `VETTING_RT11`, `VETTING_RT01` |
| P22 | `A9` rows that survived: Sheng et al. 2023 and Sailor et al. 2019, both with constant occupancy, quoted. Pulkkinen et al. 2026 (Energy and Buildings, cold-climate outage) is the nearest single-building prior and must appear in any `A9` novelty claim. A six-climate-zone US outage study of single-family homes (abstract) | `VETTING_RT15`, `VETTING_RT11`, `VETTING_RT02` |
| P23 | `A9`: Texas winter storm Uri, through Pecan Street, is the one measured-outage route found. Habitability references whose pages resolve: LEED IPpc100, WHO, RELi, the National Building Code; Toronto Green Standard 72-hour credit as a pointer | `VETTING_RT15` |
| P24 | `A9` winter arm: a Concordia winter-outage study of multi-unit residential buildings was claimed (Baba et al. 2022, Journal of Building Engineering); its DOI resolved to a precast-column paper, so whether such a study exists is unknown | `VETTING_RT15` |
| P25 | Rows claimed for `A9` that failed identity: Sun et al. 2020 (DOIs 10.1016/j.buildenv.2020.107068 does not resolve, 10.1016/j.buildenv.2020.106884 resolves to a different paper); Baniassadi et al. 2018 (DOI 10.1016/j.buildenv.2018.06.019 resolves to a body-heat-loss paper) | `VETTING_RT15`, `VETTING_RT11` |
| P26 | `A11`: an idea whose effect sizes must be measured by us; the zoning percentages that one report attributed to Cerezo Davila et al. 2016 and Dogan and Reinhart 2017 are unknown | `VETTING_RT06` |
| P27 | `A12`: open as a short protocol paper built from 4J's privacy audit as pre-registered; no standard audit exists in the literature searched; no privacy guidance was found in building-energy journals | `VETTING_RT18` |
| P28 | `A13`: no vetted row supports it | ideas document, ledger |
| P29 | `A14`, form 1: smart-thermostat presence as a source for, and check on, time-use schedules. Narrowed: done for Canada by Doma, Prajapati and Ouf 2024 (DOI 10.1016/j.buildenv.2024.111713) and for the US by Jung, Wang, Hong and Jazizadeh 2023 (DOI 10.1016/j.buildenv.2023.110628). Open: splits by household and dwelling type, arrival and departure times, matching the homes to the Canadian population. The ecobee licence terms were never read | `VETTING_RT20` |
| P30 | `A14`, form 2: Doma's comparison is hourly and in aggregate: Canadian time-use survey mean daily occupied share 71 %, thermostat profiles 68 %, 8,880 of 22,940 Canadian homes; the thesis says its aim was representativeness, "rather than to verify accuracy by quantifying the match"; the dataset carries no socio-demographic information. The energy consequence of the difference is unassessed | `VETTING_RT32` |
| P31 | `A14`, form 3: activity-based travel-model populations as the occupancy engine of a UBEM. Done abroad (a 2026 UrbanSim, POLARIS and CityBES co-simulation; Binder et al. 2020 for Tokyo; Yamaguchi et al. 2023 for Japan). Open: a Canadian version. Toronto model code is GPL-3.0; whether a Toronto or Montreal synthetic population may be used is unknown | `VETTING_RT27` |
| P32 | `A14`, form 4: open half-hourly feeder data exists for UK Power Networks (CC BY 4.0, free after registration). Hydro-Quebec publishes one hourly file for 3 Montreal substations, 64,605 rows, 2022-01-01 to 2024-06-30, CC BY-NC 4.0, no per-home rows, no presence field. Other `A14` forms are routes only | `VETTING_RT23` |

### Definitions of the three new angles (from one report; do not change them)

| # | Angle |
|---|---|
| P33 | `A11` zoning bias benchmark: what core-and-perimeter zoning does to a residential stock's simulated results relative to dwelling-level division with no core zone, measured on our own engine |
| P34 | `A12` privacy-utility and release protocol: a short paper on releasing a generator trained on survey microdata, built from 4J's pre-registered membership-inference audit and the partial release that followed it (brief section 3) |
| P35 | `A13` counterfactual shock synthesis: using the generator to synthesise occupancy under a shock that no survey observed |

### Programme facts

| # | Fact | Held in |
|---|---|---|
| P36 | UC Berkeley's Climate Futures fellowship is listed under the UC President's postdoctoral programme; that programme's deadline is 1 November 2026. The Berkeley research-office page and the Toronto AI in Science page return 403, so no criterion from either is known | `VETTING_RT09` |
| P37 | NSERC postdoctoral deadline 17 October; the page states that the research must be significantly distinct from, or go significantly beyond, the doctoral thesis | `VETTING_RT09` |
| P38 | MSCA postdoctoral fellowships: the researcher must not have lived or worked in the host country for more than 12 months in the 36 months before the deadline | `VETTING_RT09` |
| P39 | The Digital Futures postdoctoral page carries the context labels Digitalized Industry, Rich and Healthy Life, Smart Society and the themes Cooperate, Learn, Trust | `VETTING_RT09` |
| P40 | Every 2026 programme deadline falls before any possible 5J preprint, so 5J serves the 2027 cycle | manager's state note |

### Contradictions the manager has already settled (do not reopen)

* The Berkeley programme: the brief (section 5) and `P36` agree that the Climate Futures fellowship
  runs through the UC President's programme.
* NSERC: an earlier report said the thesis-distinctness rule was replaced; `P37` shows it on the
  programme's own page.
* `A2` is defined as in brief section 4. Two earlier reports merged `A2` with `A6`; that merged angle
  is not ranked.

## Part A. The open contradictions and unchecked claims

For each question: open the deciding source, log it, and give one verdict. Answer as a table with the
columns: question | verdict | the value or text that decides it, copied | log line(s) | what it
changes for which angle.

Verdict words: `FIRST CLAIM`, `SECOND CLAIM`, `NEITHER` (give the right value), `EXISTS` / `NOT
FOUND` (with its queries), or `COULD NOT OPEN` (with the URLs tried).

* **Q1. pyepwmorph.** One report said version 2.0.0 at the repository `justinfmccarty/pyepwmorph`;
  another said 2.0.1 at `intelligent-environments-lab/pyepwmorph`. Open the package's PyPI page and
  both repository URLs. Which version is current, where is the code, and under which licence?
* **Q2. Annex 79 and its successor.** One report said IEA EBC Annex 79 concluded in 2024; another
  named Annex 95 as a 2024 to 2029 successor, titled "Human-centric Building Design". Open the IEA EBC
  pages for both annexes. Give Annex 79's stated end and Annex 95's stated title, period and scope, as
  written on the pages.
* **Q3. The winter-outage competitor (decides the novelty of `A9`'s winter arm).** Does a published
  study exist of indoor conditions in Canadian (in particular Montreal) multi-unit residential
  buildings during a winter power outage? `P24` is the unverified claim. Search CrossRef and OpenAlex
  with at least three phrasings, log each, and for every candidate give the DOI, the CrossRef title
  and a logged abstract. Say whether any candidate varies occupancy.
* **Q4. `A9`'s rows survive their CrossRef titles.** For each work in `P22`, resolve it through
  CrossRef (log the query and the record), paste its title and authors, and fetch its abstract.
  Quote the abstract sentence that states how occupancy was treated, or write `NOT IN ABSTRACT`. For
  the two failed rows in `P25`, search for the real paper by title words and authors; give its DOI
  and CrossRef title, or `NOT FOUND`.
* **Q5. Occupancy in survivability studies.** Is there any published passive-survivability or
  thermal-autonomy study, at building or district scale, whose occupancy varies over time or by
  household (not a fixed schedule)? Search at least four phrasings (for example: passive
  survivability occupancy schedule; thermal autonomy power outage occupants; habitability outage
  household composition; outage indoor temperature occupant presence). For every hit you cite, a
  logged abstract. This tests `P21`.
* **Q6. Heat exposure with time-use presence.** Is there any published study that combines
  time-use or time-activity presence with a building thermal model to estimate indoor heat exposure
  of residents, at any scale? At least four phrasings, logged; a logged abstract for every hit. This
  tests `P6`, `P8` and `P9` together.
* **Q7. Language models reading building records.** Is there any published study in which a
  language model extracts building attributes or renovation state from permits, certificates or
  cadastral text **and** reports abstention, prediction sets or calibrated uncertainty? At least four
  phrasings, logged; a logged abstract for every hit. Then open the abstracts of Gunay et al. 2023
  and Borrotti 2024 (`P18`) and say, from the abstract only, what each did. This tests `P16` to `P18`.
* **Q8. Demographic occupancy in future scenarios.** Is there any published district or stock study
  that changes population and household composition, future weather and the building stock
  together? At least three phrasings, logged; a logged abstract for every hit. This tests `P13`.
* **Q9. The zoning effect sizes behind `A11`.** Resolve Cerezo Davila et al. 2016 and Dogan and
  Reinhart 2017 through CrossRef (title words and authors), fetch their abstracts, and copy any
  number they give for the effect of zoning simplification on simulated energy use. If the abstract
  gives none, `NOT IN ABSTRACT`. This tests `P26`.
* **Q10. The ecobee Donate Your Data terms.** Find and open the page that holds the terms under which
  researchers receive the data. Copy the clauses on publication of derived results and on
  redistribution. If the terms are behind a form or a login, `COULD NOT OPEN`. This decides the
  licence gap in `P29`.
* **Q11. The BuildOcc record.** Earlier reports cited "BuildOcc" as arXiv:2609.02729 with a Zenodo
  record 10.5281/zenodo.21192895; the Zenodo DOI returned 404 in three checks. Open the arXiv
  abstract page and the Zenodo DOI. Does it exist, what is its title, and does its abstract describe
  an occupancy generator? This decides whether `A3` has an unlisted competitor.

## Part B. One ranking of the open angles

Rank these eleven angles, and only these: `A2`, `A3` (in the narrowed form of `P4`), `A4`, `A6`,
`A7`, `A8`, `A9`, `A11`, `A12`, `A13`, `A14` (its best form among `P29` to `P32`, named). `A1`,
`A5` and `A10` are not ranked (`P1` to `P3`).

**The rule, stated here and applied without exception:**

S = 0.40 G + 0.30 F + 0.20 D + 0.10 P, with each part scored on the levels below and nowhere in
between.

* G, openness (0, 20 or 40): 40 if Part A's search for the angle's own combination found nothing
  **and** the nearest works (with logged abstracts) each lack a named part of it; 20 if the
  combination is partly done, or if the only evidence of openness is a search with no logged
  abstracts behind its nearest works; 0 if a work with a logged abstract does the combination.
* F, fit with what we hold (0, 20 or 30): 30 if the brief's section 3 assets cover every input; 20
  if one input from the "Asset it lacks" column of brief section 4 must be obtained; 0 if an input is
  blocked (closed data, a licence that forbids publication, or no route found).
* D, defensibility (0, 10 or 20): 20 if the strongest reviewer objection is answered by an asset we
  hold or a result a reader could check; 10 if it can only be qualified; 0 if it is fatal.
* P, programme fit (0, 5 or 10): from brief section 5 and `P36` to `P40` only. 10 if the angle is
  the drafted or live topic of two or more programmes; 5 if of one; 0 if of none. Programme themes
  in the brief are the researcher's framing, not programme criteria; say so where you use them.

Answer as one table with the columns: rank | angle | G | tag for G | F | tag for F | D | tag for D |
P | tag for P | S | the objection used for D, in one sentence | stand-alone paper or a module of
which angle. Every score cell carries its tag (`[Pn]`, `[Ln]`, `[BRIEF s.n]`); a score whose only
tag is `[INFERENCE]` must be the lower of the two levels it sits between, and say so.

Then answer, one line each:

* **B1.** Does the top three change if every G of 40 that rests on Part A searches alone is set to
  20? Give the new top three.
* **B2.** Does the top three change if P is dropped? Give it.
* **B3. The flattering direction.** Four earlier reports put `A9` first with maximal scores, and the
  consensus was partly inherited from one report to the next. If `A9` ranks first here, name the
  Part A rows (with their log lines) that put it there, other than the agreement of earlier reports.
  If an angle the brief describes warmly ranks first, say which evidence other than that warmth put
  it there.
* **B4.** For the top three, the one thing that, if found next month, would drop each angle by one
  G level.

## Deliverable

Use the template's sections as follows.

* **Section A**: the ranked list in eleven lines, each with S, then one line saying which Part A
  verdicts changed a fact in the table above.
* **Section B**: Part A, the answer table for Q1 to Q11.
* **Section C**: only the works you cite in Part A, one row each: DOI or arXiv ID with the CrossRef
  (or arXiv) title beside it, authors pasted from the record, the log line of the record, the log
  line of the abstract or `TITLE ONLY`, and the Part A question it answers.
* **Section D**: the Part B table and B1 to B4.
* **Section E**: for the top three only, what each changes in our planning, tagged.
* **Section F**: the artefacts from Q1, Q2, Q10 and Q11: URL, HTTP status, log line.
* **Section G**: your negative controls: (1) every query behind every `NOT FOUND`, with log lines;
  (2) the list of works whose abstract you fetched, each with its log line, and the list of works
  you know by CrossRef record only; (3) any tag you could not place, and the sentence you struck
  because of it.
* **Section H**: the full reference list, CrossRef titles beside the DOIs.
