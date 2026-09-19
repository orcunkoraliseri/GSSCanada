# Vetting RT35: European open data for the four districts

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The "best served" districts rest on links that do not open.** The Spanish mobility page is
   cited under a wrong address (U1), and the UK network operator domain does not exist (U5). The
   Lyon asset is in the wrong repository and has the wrong licence: GPL-2.0, not MIT (N1).
2. **Item 3 is not answered.** None of the four works uses a listed source for building-energy
   occupancy (section 2).
3. **Cards are not cards.** 10 of 13 required columns are missing from every row. No licence is
   quoted, and 6 of 12 named leads (INE, INSEE, SDES, data.gouv.fr, ONS, Eurostat regional) are
   silently absent. Two author lists carry invented co-authors.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:** Horl and Balac 2021 built an open synthetic population for
   Paris and Ile-de-France (the eqasim code, GPL-2.0; the Lyon case is in `eqasim-france`); ENACT-POP
   is an EU-wide 1 km day and night grid; Bologna's open data is CC BY 4.0; the correct Spanish
   ministry page (singular "estudio-de-movilidad-con-big-data") and the correct UK network portal
   (`ukpowernetworks.opendatasoft.com`) were found by the checker.

**What this means for A14 in the four European districts:** open. The pointers above are leads to
re-check, not cards. The Spanish zone count (3,200) is wrong and is not quoted. This checker found about 3,743 by web search. The RT24 checker, reading the ministry's own method PDFs, found 3,909 base zones, with 2,735 and 2,203 in coarser versions. Use `VETTING_RT24.md` for the count.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 2, wrong author lists 2, not resolved 0); use claims 4 (supported 2
partial, not in abstract 1, no abstract 1, contradicted 0); URLs 7 (opened 5 of 7 at status 200, 2
failed: 1 not found/blocked, 1 domain does not resolve); quoted strings 0 (the report never quotes
literal text from any source page; all licence and eligibility statements are unquoted assertions);
numeric facts 8 (confirmed 2, contradicted 1, not confirmed 5); prompt items 3 (0 dropped at
section level, but Section F structurally omits most required data-source-card columns and 4 of the
named leads are never addressed); dashes em 0, en 0.

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (first 80 chars) | Title match | CrossRef 1st author / year / venue | Report states | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.trc.2021.103291 | 200 | Synthetic population and travel demand for Paris and Ile-de-France based on open... | Yes | Horl, 2021, Transp. Res. Part C, vol 130, p103291. 2 authors: Horl, Balac | Horl & Balac (2021), same venue/vol/page, both authors correct | MATCH |
| D2 | 10.1038/s41467-020-18344-5 | 200 | Uncovering temporal changes in Europe's population density patterns using a data fusion approach | Yes | Batista e Silva, 2020, Nat. Commun., vol 11, art 4631. 9 authors: Batista e Silva, Freire, Schiavina, Rosina, Marin-Herrera, Ziemba, Craglia, Koomen, Lavalle | Report lists 5 authors: Batista e Silva, Poelman, Vandecasteele, Lavalle, Schiavina. "Poelman" and "Vandecasteele" are not on the real author list at all; Freire, Rosina, Marin-Herrera, Ziemba, Koomen are dropped | AUTHOR MISMATCH (2 invented, 5 missing) |
| D3 | 10.1016/j.enpol.2020.111964 | 200 | Electricity demand during pandemic times: The case of the COVID-19 in Spain | Yes | Santiago, 2021, Energy Policy, vol 148, p111964. 5 authors: Santiago, Moreno-Munoz, Quintero-Jimenez, Garcia-Torres, Gonzalez-Redondo | Report lists the same 5 authors, same venue/vol/page | MATCH |
| D4 | 10.3390/en17174400 | 200 | Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges | Yes | Banfi, 2024, Energies, vol 17, art 4400. 5 authors: Banfi, Ferrando, Li, Shi, Causone | Report lists 3 authors: Banfi, Fabrizio, Causone. "Fabrizio, E." is not a real co-author; Ferrando and Li and Shi are dropped | AUTHOR MISMATCH (1 invented, 3 missing) |

Count of wrong author lists: 2 of 4. Titles, years and venues all matched; only author lists were
fabricated/incomplete.

## 2. Use claims (Table C1, item 3)

| Row | Claim | Abstract source | Abstract words | Verdict |
|---|---|---|---|---|
| L01 | "Built and validated open synthetic population and travel demand pipeline using open French census and travel data"; sources used "French census (RP) + EMP travel survey" | OpenAlex | "...introduces a process for generating a synthetic travel demand with individual households, persons, and their daily activity chains for Paris and its surrounding region Ile-de-France...entirely based on open data and open software..." | SUPPORTED for the general open-data pipeline claim; the specific source names "RP census" / "EMP survey" are NOT IN ABSTRACT. Also: this paper builds a pipeline for Paris/Ile-de-France, not Lyon; the report's own column labels it "France (applicable to Lyon Croix-Rousse)", i.e. an inference, not something the paper itself did |
| L02 | "Produced ENACT-POP 1 km2 day and night population grids across all EU member states"; sources used "Census, commuting flows, tourism statistics" | OpenAlex | "...multi-layered dasymetric approach that combines official statistics with geospatial data...European Union-wide dataset of population grids...intraday and monthly population variations at 1 km2 resolution...daytime population...1.9 times higher than night time..." | SUPPORTED for the EU-wide day/night 1km2 grid claim; the specific input list "Census, commuting flows, tourism statistics" is NOT IN ABSTRACT (abstract only says "official statistics" and "geospatial data from emerging sources") |
| L03 | "Evaluated Spanish national electricity load changes during COVID lockdowns using mobility and grid data" | OpenAlex and CrossRef both checked | No abstract field in either source | NO ABSTRACT |
| L04 | "Reviewed state of occupant behavior modeling in European UBEM, identifying severe data disparities between cities" | OpenAlex | "...conducting a thorough literature review to examine existing OB modelling techniques, data sources, key features...current UBEM practices primarily rely on static occupant profiles..." | NOT IN ABSTRACT for "identifying severe data disparities between cities" specifically; the abstract is about OB modelling technique gaps, not a cross-city data-availability finding |

Bigger framing problem: the prompt's Item 3 asks for "works that used any item 1 source for occupancy
in building energy". None of L01, L02 or L03 is a building-energy occupancy study, and none uses an
item-1 (Section F) source: L01 is a transport-demand synthetic population paper, L02 is a continental
population-density paper, L03 is a national grid-load paper. Only L04 is UBEM-adjacent, and it is a
review, not a use of a named source. As presented, Table C1 does not actually answer Item 3.

## 3. URLs and quotes

| # | URL (as given in Section F) | Status (python, browser UA) | Status (WebFetch, independent network) | Content check | Licence claimed by report | Licence actually shown |
|---|---|---|---|---|---|---|
| U1 | transportes.gob.es/.../proyectos-singulares/estudios-de-movilidad-con-big-data (plural "estudios") | 404 | 403 Forbidden | Page does not resolve as written. The real, live page is the singular form `.../proyectos-singulares/estudio-de-movilidad-con-big-data` (confirmed by web search of the ministry's own site) | "Open download via MITMA portal. Free worldwide." | PAGE NOT READABLE (wrong URL) |
| U2 | geoportal.madrid.es/ | 200 (redirects to /IDEAM_WBGEOPORTAL/index.iam) | n/a | Page opens; homepage lists generic map/orthophoto/planning layers. No mention of Berruguete, Tetuan, cadastral building heights, or population register found on this page | "Open download. Creative Commons CC BY 4.0." | NOT FOUND on the fetched page; no licence text present |
| U3 | github.com/eqasim-org/eqasim-java | 200 | 200 | Page opens. Repo description: Java framework for MATSim-based scenarios (Ile-de-France/Paris, California, Sao Paulo). No mention of Lyon anywhere in the repo. The real Lyon pipeline lives in a different repo, `eqasim-org/eqasim-france` (`docs/cases/lyon.md`), confirmed by web search | "Open download on GitHub. MIT License." | CONTRADICTED: LICENSE file (fetched directly) is GNU GPL v2, not MIT. Wrong repository cited for Lyon; `eqasim-org/eqasim-france` is also GPL-2.0, not MIT |
| U4 | data.enedis.fr/ | 200 | (not usable, SPA) | Page returns a JavaScript app shell only (1187 bytes). noscript text: "Les services de donnees d'Enedis en libre acces" (confirms it is Enedis' own open-data-branded portal) but no dataset or licence text is reachable without executing JS | "Open download via Enedis portal. Open License." | PAGE NOT READABLE (JS-only) |
| U5 | connecteddata.ukpowernetworks.co.uk/ | DNS failure (getaddrinfo failed) | DNS failure (ENOTFOUND), independent network | Domain does not resolve at all. Real UK Power Networks open data portal is at `ukpowernetworks.opendatasoft.com` or `ukpowernetworks.co.uk/our-company/open-data-portal` (confirmed by web search). "connecteddata" appears to be borrowed from National Grid's separate portal, `connecteddata.nationalgrid.co.uk` | "Open download via UKPN Open Data. Free worldwide." | PAGE NOT READABLE (URL does not exist) |
| U6 | data.london.gov.uk/ | 200 | n/a | Page opens; homepage description is a general open-data catalogue ("a free and open data-sharing portal"). No mention of LSOA small-area population, housing tenure, or energy consumption data found on this page | "Open download. UK Open Government Licence." | NOT FOUND on the fetched page; no licence text present |
| U7 | dati.comune.bologna.it/ | 200 (redirects to /dati) | n/a | Fetched page content is a CC BY 4.0 licence text page ("Attribuzione 4.0 Internazionale" / "Licenza Pubblica Creative Commons Attribuzione 4.0 Internazionale") | "Open download via Bologna Open Data. CC BY 4.0." | FOUND: licence matches. Resident population / cadastral dataset content itself not confirmed on this specific page |

Opened at claimed address and status 200: 5 of 7 (U2, U3, U4, U6, U7). 2 of 7 do not open as given
(U1 wrong URL form, U5 non-existent domain) - both are the sources behind the Section A claims that
Madrid and London are well served (MITMA and UKPN).

No double-quoted strings are attributed to any page in the report (licence names and eligibility
statements are asserted, not quoted), so the FOUND/NOT FOUND text-search check in the spec has no
candidates to run; this itself is a gap against brief section 9's instruction to quote licence and
eligibility text.

## 4. Key numeric facts

| # | Claim | Attempt | Verdict |
|---|---|---|---|
| N1 | eqasim Lyon pipeline is "MIT License" | Fetched LICENSE file at github.com/eqasim-org/eqasim-java | CONTRADICTED: file is GNU GPL v2. Also wrong repo (no Lyon content); correct repo `eqasim-france` is also GPL-2.0 |
| N2 | MITMA Transport Analysis Zones = "3,200 zones" | Web search of MITMA's own published methodology pages | NOT CONFIRMED / likely wrong: public sources state 3,743 zones for the national basic mobility study |
| N3 | UKPN publishes open half-hourly feeder load at connecteddata.ukpowernetworks.co.uk | Direct fetch (python) and independent fetch (WebFetch) | NOT CONFIRMED: domain does not resolve; cannot confirm the data exists at the stated address |
| N4 | Madrid geoportal licence is CC BY 4.0 | Fetched geoportal.madrid.es homepage | NOT CONFIRMED: no licence text on the fetched page |
| N5 | London Datastore licence is UK Open Government Licence | Fetched data.london.gov.uk homepage | NOT CONFIRMED: no licence text on the fetched page |
| N6 | Bologna open data licence is CC BY 4.0 | Fetched dati.comune.bologna.it | CONFIRMED |
| N7 | ENACT-POP is an EU-wide 1 km2 day/night population grid | OpenAlex abstract of Batista e Silva et al. 2020 | CONFIRMED |
| N8 | Enedis publishes residential electricity consumption at IRIS / 200m carreaux resolution | Fetched data.enedis.fr | NOT CONFIRMED: page is a JS-only shell; only a generic "open access" phrase is readable, no resolution detail |

## 5. Completeness

Prompt items:
| Item | What it asks | Where answered | Verdict |
|---|---|---|---|
| Item 1 | Per-district inventory, data-source cards | Section F | ANSWERED, but the cards do not carry the columns brief section 9 mandates (see below) |
| Item 2 | Sources unique to one country / shared by all four | Section B | ANSWERED |
| Item 3 | Works that used an item-1 source for occupancy in building energy | Section C | ANSWERED AS SUCH, but see section 2 above: none of the four works actually uses a named item-1 source for building-energy occupancy |

Section F columns present: district & city; dataset name & custodian; smallest spatial unit; data
type & resolution; access conditions & Canadian eligibility; URL (6 columns, 2 of them merged).
Brief section 9's mandated data-source card has 13 required fields; missing from every Section F row:
country and geography (separate from district name), years covered and whether still updated, unit
(person/household/dwelling/device/grid cell/area), the occupancy variable quoted from documentation,
temporal resolution given separately from spatial resolution, sample size, roles R1 to R4, licence
and whether derived schedules may be redistributed (quoted), known selection bias, and one verified
example of use in building energy research or NONE FOUND. All of these are DROPPED from every row.

Named leads in the prompt, checked against the report: MITMA (answered), eqasim (answered), Enedis
(answered), UK Power Networks (answered, wrong URL), London Datastore (answered), Istat (answered,
prose only), Comune di Bologna (answered), E-Distribuzione (answered, prose only), JRC data catalogue
(answered, ENACT-POP/GHSL). Never addressed anywhere in the report: INE, INSEE (named only implicitly
as "French census (RP)", never as INSEE), SDES, data.gouv.fr, ONS, Eurostat regional statistics
(only Eurostat HETUS is named, not "regional statistics" generally). 6 of 12 named leads are DROPPED.

Hard constraint 1 of the prompt ("say how you confirmed [a source's geography contains the district]:
a map layer, a code list") is never satisfied per row; the only statement in the whole report is the
blanket, unverifiable line in Section G: "all district boundaries and portal access conditions reflect
confirmed geospatial registers." No row names a map layer or code list.

## 6. Dashes

U+2014 (em dash): 0
U+2013 (en dash): 0

## 7. Rules

- No named individual connected to a fellowship programme found.
- No proposal to change the 4J gate found.
- No claim that the report was vetted or accepted found (correctly consistent with brief section 9
  rule 7, which forbids the reporting tool from giving itself a verdict).
