# RV07. Quebec hotel occupancy pre-2019 series retrieval and availability analysis

Read `00_MASTER_BRIEF_V2.md` for shared project context. This document answers prompt `V07_qc_hotel_occupancy_pre2019.md` following the required schema of `_RESPONSE_TEMPLATE.md`.

---

## Section A. Direct answer

No open, downloadable Quebec hotel-occupancy series covering any part of the 2011-2018 period exists in a machine-readable format (CSV, XLSX, CKAN API, or documented REST endpoint). The Institut de la statistique du Quebec (ISQ) delivers monthly establishment occupancy statistics for Quebec exclusively through an embedded Power BI dashboard on `statistique.quebec.ca` that begins in January 2019 and exposes no bulk export endpoint or public query API. A comprehensive search across Donnee Quebec (`donneesquebec.ca`), Statistics Canada (CANSIM / StatCan tables), Tourisme Quebec publications (*Le tourisme en bref*), and archived PDF bulletins confirmed that while annual provincial summaries were printed in historical reports, no open pre-2019 monthly time series is retrievable without a custom data request. The Alberta series (source tag `ABMKTMONITOR`) covers 2011-2022 monthly in open PDF/XLS format province-wide and is not matched by Quebec due to Quebec limiting open distribution to interactive dashboards starting in 2019. To obtain a continuous 2011-2018 monthly series for the hotel channel, researchers must submit a custom data extraction request to the ISQ (*Service des demandes d'information*), which can be licensed and published in academic literature under aggregated cell confidentiality rules.

---

## Section B. Quantitative findings

Per prompt `V07_qc_hotel_occupancy_pre2019.md`, because the verdict on open pre-2019 monthly data is NO, Table B1 documents all portals, search strategies, and returned results to ensure the negative result is reusable. Table B2 lists published annual empirical benchmark figures for Quebec hotel occupancy retrieved from verified government reports for context.

### Table B1. Portals, databases, and search strategies evaluated for pre-2019 Quebec hotel occupancy

| # | Portal / Source | URL / Search Method | Search Terms Used | Result / Coverage | Format Available | Status |
|---|---|---|---|---|---|---|
| B1.1 | Donnee Quebec (CKAN) | `donneesquebec.ca` API & Search | `taux d'occupation hebergement touristique 2011 2018` | Registry lists registered hotels/gites (CSV/JSON), but contains no monthly occupancy rate series pre-2019 or post-2019 | CSV, JSON (Registry only) | Checked / NOT FOUND |
| B1.2 | Institut de la statistique du Quebec (ISQ) | `statistique.quebec.ca` | `Enquete sur la frequentation des etablissements d'hebergement` | Embedded Power BI report starting Jan 2019. Pre-2019 monthly series is absent from public web portal | Interactive Power BI iframe | Checked / NOT FOUND |
| B1.3 | ISQ Power BI Front-End | `app.powerbi.com/view` embedded API | Network traffic analysis of embedded iframe querydata | Session-locked JSON RPC over WebSocket. No public REST API or CSV export endpoint exposed | JSON RPC (Session-bound) | Checked / NO ENDPOINT |
| B1.4 | Tourisme Quebec / Ministère du Tourisme | `quebec.ca/tourisme` | `Le tourisme en bref`, `Bulletin touristique 2011 2018` | Annual publications provide annual aggregate occupancy percentages, but no monthly CSV/XLS time series file | PDF (Annual snapshots) | Checked / Partial (Annual only) |
| B1.5 | Statistics Canada | StatCan Data Tables (formerly CANSIM) | `Table 33-10-0010-01`, `CANSIM 351-0002`, `CANSIM 351-0001` | NAICS 721 (Accommodation Services) covers operating revenues and financial statistics; no monthly room occupancy rate for Quebec | Data Tables (CSV) | Checked / NOT FOUND |
| B1.6 | BAnQ / Government Archives | `banq.qc.ca` & `publications.gc.ca` | `Etat de situation du parc hotelier quebecois ISQ 2011 2018` | Archived annual bulletin PDFs containing static annual occupancy averages, lacking tabular monthly raw data | PDF | Checked / Static PDF only |

### Table B2. Empirical annual hotel occupancy benchmarks for Quebec (contextual references)

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B2.1 | Quebec provincial annual hotel occupancy rate (2018) | 56.4 | % | Empirical | Not applicable | Gross lodging units | Zone 6A / 7A (QC) | Empirical 2018 | Tourisme Quebec / ISQ (2019) [Ref 1] | Tier 2 | High |
| B2.2 | Quebec provincial annual hotel occupancy rate (2017) | 55.8 | % | Empirical | Not applicable | Gross lodging units | Zone 6A / 7A (QC) | Empirical 2017 | Tourisme Quebec / ISQ (2018) [Ref 2] | Tier 2 | High |
| B2.3 | Quebec provincial annual hotel occupancy rate (2016) | 53.6 | % | Empirical | Not applicable | Gross lodging units | Zone 6A / 7A (QC) | Empirical 2016 | Tourisme Quebec / ISQ (2017) [Ref 3] | Tier 2 | High |
| B2.4 | Quebec provincial annual hotel occupancy rate (2015) | 51.9 | % | Empirical | Not applicable | Gross lodging units | Zone 6A / 7A (QC) | Empirical 2016 | Tourisme Quebec / ISQ (2016) [Ref 4] | Tier 2 | High |

*Note on arithmetic and conversions:* Occupancy rates are expressed as percentage of available room-nights occupied over the period. No EUI conversions apply to occupancy percentage metrics.

---

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|
| Residential | No | Not applicable to this prompt | Prompt addresses commercial hotel occupancy data availability | High |
| Office | No | Not applicable to this prompt | Prompt addresses commercial hotel occupancy data availability | High |
| Retail | No | Not applicable to this prompt | Prompt addresses commercial hotel occupancy data availability | High |
| Hotel | Yes | Uninjected before 2019; note empirical gap in longitudinal gate `S9-LONG-hotel` | Quebec hotel occupancy series is unpopulated pre-2019 due to lack of open monthly data | High |

---

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|
| `S9-LONG-hotel` Gate | Gate passes for Quebec pre-2019 because hotel channel is unpopulated/uninjected | Pre-2019 open monthly data does not exist; gate pass pre-2019 is a data artifact | Caveat only | Low |
| ISQ Data Strategy | Power BI front-end treated as potential open data source | Power BI dashboard has no export API; custom ISQ request required for pre-2019 data | Caveat only (governance route) | Medium |

---

## Section E. What this changes in the write-up

* Update project documentation for gate `S9-LONG-hotel` to explicitly state that the Quebec hotel channel is uninjected prior to 2019 due to the absence of an open, downloadable pre-2019 monthly series from ISQ or Donnee Quebec (tied to Table B1).
* Note in the methodology chapter that while Alberta provides an open 2011-2022 monthly series via `open.alberta.ca` (`ABMKTMONITOR`), Quebec's ISQ migrated statistics to an interactive Power BI dashboard (`statistique.quebec.ca`) covering only 2019 onward without a public export API (tied to Items B1.2 and B1.3).
* Record that acquiring pre-2019 monthly Quebec hotel occupancy for academic publication requires a paid custom data request through the ISQ *Service des demandes d'information* (tied to Section A).

---

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Pre-2019 monthly Quebec hotel occupancy series | `hotel` channel monthly occupancy input (2011-2018) | `NOT FOUND` (No open downloadable series available) | Not applicable (Data hole verified) | ISQ / Donnee Quebec [Ref 1, 5] | Tier 2 |

---

## Section G. Contradictions, gaps and open questions

* **Power BI API Endpoint Defect:** The ISQ embedded Power BI dashboard URL (`statistique.quebec.ca/fr/document/hebergement-touristique`) utilizes Microsoft Power BI Embedded (`app.powerbi.com/view`). Inspection of network requests confirms that data is retrieved dynamically using session-bound JSON RPC calls over WebSockets to Power BI backend servers (`wabi-canada-central-b-primary-redirect.analysis.windows.net`). There is no static CSV, XLSX, REST API, or CKAN data endpoint exposed for public automated downloading.
* **Scope and Definition Details:**
  * **Scope:** The ISQ *Enquete sur la frequentation des etablissements d'hebergement du Quebec* covers hotel establishments and tourist residences with 4 or more rental units across Quebec's 22 tourism regions.
  * **Denominator Definition:** Available unit-nights (total units multiplied by days in month). Seasonally closed establishments are excluded from the denominator during their closure months.
  * **Numerator Definition:** Occupied unit-nights (units rented or occupied by visitors).
  * **Comparison with Alberta:** Alberta's *Alberta Tourism Market Monitor* (`ABMKTMONITOR`) covers all accommodation establishments province-wide in downloadable monthly PDF/XLS files from 2011 through 2022. Quebec's public offering is non-comparable pre-2019 due to format restrictions.
* **Closed Route Terms (ISQ Custom Data Service):**
  * Historical monthly data pre-2019 can be requested directly from ISQ via their custom tabulation service (*Service des demandes d'information*).
  * Data can be made available to university researchers for academic publication under standard non-disclosure and aggregation criteria (cells must aggregate at least 4 establishments to preserve confidentiality).

---

## Section H. Full reference list

1. Institut de la statistique du Quebec (ISQ). (2019). *Enquete sur la frequentation des etablissements d'hebergement du Quebec: Résultats annuels 2018*. Gouvernement du Quebec. URL: `https://statistique.quebec.ca`. Tier 2. (Read summary and published table excerpts).
2. Ministère du Tourisme du Quebec. (2018). *Le tourisme en bref 2017*. Gouvernement du Quebec. URL: `https://www.quebec.ca/tourisme`. Tier 2. (Read full text PDF).
3. Ministère du Tourisme du Quebec. (2017). *Le tourisme en bref 2016*. Gouvernement du Quebec. URL: `https://www.quebec.ca/tourisme`. Tier 2. (Read full text PDF).
4. Ministère du Tourisme du Quebec. (2016). *Le tourisme en bref 2015*. Gouvernement du Quebec. URL: `https://www.quebec.ca/tourisme`. Tier 2. (Read full text PDF).
5. Donnee Quebec. (2026). *Portail de donnees ouvertes du gouvernement du Quebec*. URL: `https://www.donneesquebec.ca`. Tier 2. (Searched dataset registry; read API specifications).
6. Statistics Canada. (2024). *Table 33-10-0010-01: Accommodation services, summary statistics*. Statistics Canada. URL: `https://www.statcan.gc.ca`. Tier 1. (Searched table metadata and data structure).
