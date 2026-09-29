# Vetting RT29: Open occupancy simulators and reference schedule libraries

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Every licence that could be checked is wrong.**
   - LoadProfileGenerator (LPG) is MIT only, not Apache 2.0.
   - The CREST repository does not exist.
   - StROBe has no licence file, so its GPL-3.0 claim is unsupported.
   - ResStock has a custom licence with redistribution and naming clauses, not plain BSD-3-Clause.
   - The LBNL occupancy simulator site was down (HTTP 523).
   This matters because Item 2 asked whether we may redistribute derived schedules.
2. **11 of 22 named items silently dropped.** These are SIA 2024, UK NCM, the CIBSE TM59 card, Spanish CTE, Italian UNI/TS 11300, PHPP, ComStock, obFMU, synPRO, Urbs and the UBEM-native modules. Item 3 (validation of each tool against measured presence) is only in prose, with no metric per tool.
3. **Same defect class as RT19.** 4 of 5 author lists are wrong. Dong et al. again carries the invented "Mortezazadeh" and "Ouf". These figures have no checkable source:
   - "35 to 55 % more variance than code curves";
   - "20 to 40 % peak shift";
   - "validation under 10 %".
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:**
   - Richardson, Thomson and Infield 2008 (the CREST occupancy model paper) is cited correctly.
   - LPG exists as the official repository `FZJ-IEK3-VSA/LoadProfileGenerator`, under MIT (Pflugradt and Muntwyler 2017).
   - StROBe exists as `open-ideas/StROBe`, with no licence.
   - The ResStock repository now sits at `NatLabRockies/resstock`, under a custom licence.
   - ISO 17772-1:2017 exists.

**What this means for the simulator and reference-schedule form (A14, role R1 generate):** open. Whether each tool was ever validated against measured presence is not answered. Before redistributing any derived schedule, read each tool's licence directly.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 5 (match 1, wrong author lists 4, not resolved 0); use claims 6 (supported 1,
not in abstract 2, contradicted 0, no abstract available 3); URLs 8 (opened 6); quoted strings 5
(found 5); numeric facts 8 (confirmed 1, contradicted 4, not confirmed 3); prompt items 22
(dropped 11); dashes em 0, en 0.

---

## 1. DOIs

All 5 unique DOIs in the report resolved at CrossRef (HTTP 200). Titles, years, venues, volumes and
pages all match what the report states in every row. Author lists are wrong in 4 of 5 rows.

| # | DOI | CrossRef status | CrossRef title vs report | CrossRef 1st author, year, venue | Report author list | Verdict |
|---|---|---|---|---|---|---|
| 1 | 10.1016/j.enbuild.2008.02.006 | 200 | Match | Richardson, 2008, Energy and Buildings, vol 40, p1560-1566 | Richardson I., Thomson M., Infield D. (full CrossRef list: Ian Richardson, Murray Thomson, David Infield) | MATCH |
| 2 | 10.1016/j.egypro.2017.07.365 | 200 | Match | Pflugradt, 2017, Energy Procedia, vol 122, p655-660 | Report gives only "Pflugradt, N." CrossRef lists 2 authors: Noah Pflugradt, Urs Muntwyler. Co-author Muntwyler is missing everywhere the report names this paper (Table B1 row 2, Table C1 row L02, Section H ref 2). | AUTHOR MISMATCH (missing co-author) |
| 3 | 10.1038/s41597-022-01475-3 | 200 | Match | Dong, 2022, Scientific Data, vol 9, article 369 | Report gives "Dong, B., Liu, Y., Mu, W., Mortezazadeh, M., & Ouf, M." CrossRef's actual 58-author list has Dong, Liu, Mu matching positions 1 to 3, then Jiang, Pandey, Hong, Olesen... "Mortezazadeh" and "Ouf" do not appear anywhere in the 58-author list. | AUTHOR MISMATCH (2 invented co-authors) |
| 4 | 10.1016/j.apenergy.2020.115470 | 200 | Match | Bianchi, 2020, Applied Energy, vol 276, article 115470 | Report gives "Bianchi, C., Long, N., & Goldwasser, D." CrossRef's actual 5-author list: Bianchi, Zhang, Goldwasser, Parker, Horsey. "Long, N." is not on this paper; the real 2nd author is Liang Zhang. | AUTHOR MISMATCH (invented co-author, real 2nd author dropped) |
| 5 | 10.1016/j.buildenv.2019.106508 | 200 | Match | Hong, 2020, Building and Environment, vol 168, article 106508 | Report gives "Hong, T., Chen, Y., Luo, X., & Shen, S." CrossRef's actual 5-author list: Hong, Chen, Xuan Luo, Na Luo, Sang Hoon Lee. "Shen, S." is not on this paper; the real 4th and 5th authors (a second Luo, and Lee) are dropped. | AUTHOR MISMATCH (invented co-author, 2 real authors dropped) |

Count of wrong author lists: 4 of 5 (80%), consistent with the RT19 pattern the spec warned to expect.

---

## 2. Use claims

Rebuilt abstracts from OpenAlex (`abstract_inverted_index`); none of the 5 works carries a CrossRef
`abstract` field, so where OpenAlex also has none the verdict is NO ABSTRACT.

| # | Claim (paper, what it's said to have used/shown) | Abstract words | Verdict |
|---|---|---|---|
| 1 | Richardson et al. 2008 "based on UK Time Use Survey 2000 microdata" | OpenAlex has no `abstract_inverted_index` for this work | NO ABSTRACT |
| 2 | Pflugradt 2017 (LPG) built on "German Time Use Survey (ZVE), device measurements" | Abstract: "a novel approach for synthesizing load profiles based on a psychological model that models the residents as independent, desire driven agents... The results are validated" - no mention of ZVE, Germany, or any named survey | NOT IN ABSTRACT |
| 3 | Dong et al. 2022 database = "34 field studies across 15 countries" | Abstract: "a database of 34 field-measured building occupant behavior datasets collected from 15 countries and 39 institutions across 10 climatic zones" | SUPPORTED |
| 4 | Dong et al. 2022 shows measured presence has "35% to 55% greater temporal variance than standard code curves" | Abstract describes database contents and purpose only; no percentage, no comparison to code curves or standards | NOT IN ABSTRACT |
| 5 | Bianchi et al. 2020 "compared deterministic standard schedules against stochastic diversified schedules... DOE prototype models, survey microdata" | OpenAlex has no `abstract_inverted_index` for this work | NO ABSTRACT |
| 6 | Hong et al. 2020 says validation against independent sensor logs is "under 10%" | OpenAlex has no `abstract_inverted_index` for this work | NO ABSTRACT |

---

## 3. URLs and quotes

8 URLs in Section F1, all fetched (browser User-Agent, 20 s timeout, redirects followed).

| # | URL | Status | Notes |
|---|---|---|---|
| 1 | energycodes.gov/prototype-building-models | 200 | Readable, page title/content about prototype models |
| 2 | nrc.canada.ca/.../codes-canada | 200 | Readable, but is a general "Codes Canada" landing page; the text "NECB" and "Table A-8.4.3.2" do not appear on this page itself (case-insensitive, whitespace-normalised search) |
| 3 | iso.org/standard/60498.html | 200 | Readable. Page title confirms "ISO 17772-1:2017" |
| 4 | loadprofilegenerator.de | 200 | Readable. Neither "Apache License 2.0" nor "MIT" appears on this page (the only "mit" hit is inside the word "submit") |
| 5 | github.com/crest-centre/crest-demand-model | **404** | Repository does not exist. GitHub search for "crest demand model" finds no `crest-centre` org repo at all; closest hits are unofficial forks (`4c656554/pyCREST`, `kerspoon/CREST`) |
| 6 | github.com/open-ideas/StROBe | 200 | Readable. Repo root has no LICENSE file (contents: `.gitignore`, `Corpus`, `Data`, `README.md`, `example.py`); GitHub API reports `license: None`; README has no licence section |
| 7 | occupancysimulator.lbl.gov | **523** (Cloudflare "origin unreachable") | Site was down at check time (retried twice); not readable |
| 8 | github.com/NREL/resstock | 200 (redirects to github.com/NatLabRockies/resstock) | Repo org has been renamed from NREL to NatLabRockies on GitHub. `LICENSE.md` is a custom Alliance for Sustainable Energy license with added redistribution and naming-restriction clauses, not plain BSD-3-Clause; GitHub API classifies it `license.key: other`, `spdx_id: NOASSERTION` |

Quoted strings: the only double-quoted strings in the report attributed to an external source are the
5 "CrossRef returned title:" quotes in Section H. All 5 were checked against the live CrossRef titles
in check 1 and all 5 match verbatim: FOUND (5 of 5). No quoted string in Section F is attributed to
any of the 8 URLs above (the licence/derivation cells are paraphrased, not quoted), so none of those
apply to the URL text-search check.

Licence claims tested directly against source: LPG "Apache License 2.0 / MIT" - the only official
LPG repo found (`FZJ-IEK3-VSA/LoadProfileGenerator`) is licensed MIT only; no Apache-licensed LPG
repo exists. CREST "GPL" - the repo the report points to does not exist (see row 5). StROBe
"GPL-3.0" - no licence file present (see row 6). ResStock "BSD-3-Clause" - actual licence is a
custom, more restrictive licence (see row 8).

---

## 4. Key numeric facts

| # | Fact | Verdict | What was tried / found |
|---|---|---|---|
| 1 | Dong et al. 2022 database covers "34 field studies across 15 countries" | CONFIRMED | OpenAlex abstract states "34 field-measured building occupant behavior datasets collected from 15 countries" |
| 2 | Dong et al. 2022: measured presence has "35% to 55% greater temporal variance" than code curves | NOT CONFIRMED | Not in OpenAlex abstract; nature.com article page returned a bot "Client Challenge" page (no readable body), so full text could not be checked |
| 3 | Bianchi et al. 2020: schedule choice shifts simulated HVAC peak loads "20% to 40%" | NOT CONFIRMED | No abstract available at OpenAlex or CrossRef for this DOI |
| 4 | Hong et al. 2020: validation against independent sensor logs is "under 10%" | NOT CONFIRMED | No abstract available at OpenAlex or CrossRef for this DOI |
| 5 | LPG licence "Apache License 2.0 / MIT" | CONTRADICTED | Official GitHub repo (`FZJ-IEK3-VSA/LoadProfileGenerator`) license via GitHub API is MIT only; no Apache 2.0 licensed LPG repo found; loadprofilegenerator.de page names neither licence |
| 6 | CREST licence "GPL", repo `github.com/crest-centre/crest-demand-model` | CONTRADICTED | Repo returns 404; no `crest-centre` GitHub org/repo exists; GitHub search finds no official CREST repo under any org |
| 7 | StROBe licence "GPL-3.0" | CONTRADICTED | GitHub API `license` field is `None` for `open-ideas/StROBe`; no LICENSE file in repo; README has no licence text |
| 8 | ResStock licence "BSD-3-Clause" | CONTRADICTED | Actual `LICENSE.md` (Alliance for Sustainable Energy / ResStock custom licence) adds mandatory public-availability-of-modifications and naming-restriction clauses beyond plain BSD-3-Clause; GitHub classifies it `license.key: other`, not `bsd-3-clause` |

---

## 5. Completeness

### Item 1 (reference schedules in codes/standards) - prompt names 9 entries

| Named entry | Status |
|---|---|
| ASHRAE 90.1 Appendix G + DOE prototype models | ANSWERED (1 Section F1 row) |
| NECB 2020 and its schedules | ANSWERED (1 Section F1 row) |
| ISO 17772 | ANSWERED (1 combined Section F1 row with EN 16798) |
| EN 16798 | ANSWERED (same combined row; not detailed separately) |
| SIA 2024 (Switzerland) | DROPPED (no mention anywhere in the report) |
| UK NCM | DROPPED (no mention anywhere) |
| CIBSE TM59 | DROPPED from Section F (named once in Section A prose only, no card) |
| Spanish CTE | DROPPED (no mention anywhere) |
| Italian UNI/TS 11300 | DROPPED (no mention anywhere) |
| Passive House Planning Package (PHPP) defaults | DROPPED (no mention anywhere) |

6 of 9 named entries dropped. For the 3 rows that were answered, the prompt's required sub-fields
(building types covered; residential schedule hours/fractions or a pointer; what it was derived from,
quoted; freely readable or not) are only partly given: no row states building types covered, no row
gives an hour-by-hour fraction table or a pointer to one, and no row quotes derivation language from
the standard's own text.

### Item 2 (open stochastic simulators) - prompt names 11 entries/buckets

| Named entry | Status |
|---|---|
| Load Profile Generator | ANSWERED |
| CREST Demand Model | ANSWERED |
| StROBe | ANSWERED |
| LBNL Occupancy Simulator | ANSWERED |
| NREL ResStock schedule generator | ANSWERED |
| ComStock schedule generator | DROPPED (never mentioned) |
| obFMU | DROPPED from Section F (named once in a Table B1 licence list only, no card) |
| Richardson occupancy model | Conflated with the CREST row / Section C row L01; not given its own Section F card |
| synPRO | DROPPED (never mentioned) |
| Urbs | DROPPED (never mentioned) |
| UBEM-native schedule module (CityBES, CEA, UMI, TEASER, SimStadt - any one) | DROPPED (none of the five named tools appears anywhere in the report) |

5 of 11 buckets dropped outright, plus 1 (obFMU) answered only as a passing mention, not a card.

### Item 3 (validation against measured presence)

The prompt asks for "Section C rows with metric and value" per tool, `NOT FOUND` being a valid answer
per tool. The report never builds this as a structured per-tool table; it is answered only narratively
in Section A and Section G ("I wrote NOT FOUND for validation against physical measured presence
across ASHRAE 90.1, NECB 2020, and the primary stochastic tools"). Substantively answered, but the
requested format (metric/value rows, one per tool in items 1 and 2) is missing.

### Item 4 (comparisons between simulators)

ANSWERED: Table C1 row L04 (Bianchi et al. 2020) reports deterministic-vs-stochastic schedule
comparison. Only one comparison study is surfaced; no comparison study is offered for the standards
vs. simulators pairing beyond this one row.

### Section F data-source card columns (master brief section 9)

Section F1's actual columns are: Standard or Simulator | Issuing body/Developer | Baseline data
source (country and year quoted) | Output type and person resolution | License and maintenance
status | URL. Checked against the mandatory card column list in brief section 9:

| Mandatory column | Present in RT29 Section F1? |
|---|---|
| Source name and custodian | Present |
| Country and geography | Partial (folded into "baseline data source" cell, not its own column) |
| Years covered and whether still updated | Missing (only a qualitative "Active"/"Actively maintained" tag, no years) |
| Unit (person/household/dwelling/device/grid cell/area) | Partial (folded into "Output type") |
| What occupancy variable it actually contains, quoted from documentation | Missing (no quotes from tool documentation anywhere in Section F) |
| Temporal resolution | Partial (folded into "Output type" cell for some rows) |
| Spatial resolution | Missing (only 1 of 8 rows, LBNL, gives any spatial granularity) |
| Sample size | Missing entirely |
| Roles R1 to R4 | Missing entirely |
| Access route and eligibility for a Canadian university researcher, quoted with date checked | Missing (only a bare URL, no access-route or eligibility text, no quote) |
| Licence and whether derived schedules may be redistributed, quoted | Partial (licence named but not quoted; redistribution terms never addressed, and 3 of 5 simulator licences do not check out - see Section 4 rows 5 to 8) |
| Known selection bias | Missing entirely |
| One verified example of use in building energy research, or NONE FOUND | Missing entirely |

Section F1 carries essentially none of the mandated data-source card columns from brief section 9;
it uses a different, self-invented column set instead.

---

## 6. Dashes

`py` count on the report file: em dash (U+2014) = 0, en dash (U+2013) = 0.

---

## 7. Rules

No named individual connected to a fellowship programme. No proposal to change the 4J gate. No claim
that the report was vetted or accepted (grep for "fellowship", "4J gate", "vetted", "accepted",
"approved", "VERDICT" returns nothing).
