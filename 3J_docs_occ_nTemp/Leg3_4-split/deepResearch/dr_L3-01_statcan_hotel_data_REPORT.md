# Deep-Research Report dr_L3-01: StatCan Hotel-Occupancy Data
### Source Verification, Temporal Coverage, Access Routes, Licensing, and Downstream Modeling Implications
**Date:** July 2, 2026  
**Author:** Canadian Official-Statistics and Tourism-Data Specialist  
**Project:** 4-Channel Occupancy Pipeline for Canadian Tall / SuperTall Mixed-Use Building Energy Models (Leg 3)

---

## Executive Summary
This report provides source verification and acquisition details for the **monthly hotel-occupancy-rate series by province** (specifically Quebec and Alberta) covering the years **2005–2022**. This series is required to drive hotel guest-room occupancy schedules in EnergyPlus prototype building simulations and fit a SARIMA 2030 forecast.

### Critical Finding
> [!IMPORTANT]
> **Statistics Canada Table 24-10-0048-01 does not exist and has never existed in the Statistics Canada catalogue.** Furthermore, **no table in the Statistics Canada Common Output Data Repository (CODR) publishes monthly hotel occupancy rates, Average Daily Rate (ADR), or Revenue per Available Room (RevPAR) by province.** 
> 
> StatCan only publishes annual financial summary data for the accommodation industry (NAICS 721) and monthly Traveller Accommodation Services Price Indexes (TASPI), which measure relative price change but not absolute room occupancy.
> 
> To obtain the required monthly provincial occupancy rate series, we must bypass Statistics Canada and utilize datasets from **provincial statistical/tourism bodies (Tourisme Québec / Institut de la statistique du Québec (ISQ)** for Quebec, and **Travel Alberta / Alberta Economic Dashboard** for Alberta) and commercial tourism databases (**CBRE Hotels Canada** and **STR/CoStar**).

---

## REQUIRED OUTPUT TABLES

### Table 1 — Candidate Statistics Canada Tables (Verified against the live catalogue)

| Table ID | Exact Title | Variables | Geography Levels | Frequency | Years Covered | Status (Active / Terminated → Successor) | Source Link |
|---|---|---|---|---|---|---|---|
| **24-10-0048-01** | *None (Non-existent)* | N/A | N/A | N/A | N/A | **Does not exist**. Likely a memory typo for 18-10-0249-01 or 24-10-0049-01. | N/A |
| **18-10-0249-01** | Traveller accommodation services price index, monthly | Price index by client group (total, business, leisure) (2013=100) | Canada, Regions, Provinces | Monthly | Dec 2000 – Present | **Active**. (Predecessor: 18-10-0020-01, terminated). Note: Tracks *price change only*, not occupancy rate. | [Table 18-10-0249-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810024901) |
| **18-10-0250-01** | Traveller accommodation services price index, quarterly | Price index by client group (total, business, leisure) (2013=100) | Canada, Regions, Provinces | Quarterly | Q1 2001 – Present | **Active**. Tracks quarterly price changes. | [Table 18-10-0250-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810025001) |
| **24-10-0049-01** | Canadian Tourism Activity Tracker and Grouped Data Sources | Tourism activity tracker index (relative to 2019 baseline) | Canada, Provinces | Monthly | Jan 2019 – Dec 2024 | **Terminated**. Discontinued after the December 2024 reference period. Tracks broad activity, not occupancy. | [Table 24-10-0049-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2410004901) |
| **33-10-0102-01** | Accommodation services, summary statistics | Operating revenue, operating expenses, salaries, wages, profit margin | Canada, Provinces, Territories | Annual | 2012 – Present | **Active**. (Predecessor: 21-10-0001-01, covering 1997–2011). | [Table 33-10-0102-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3310010201) |
| **21-10-0237-01** | Accommodation services, distribution of sales by type of service provided | Percentage share of room accommodation, meals, beverages, other sales | Canada, Provinces, Territories | Annual | 2013 – Present | **Active**. | [Table 21-10-0237-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2110023701) |

---

### Table 2 — QC + AB Monthly Coverage Map, 2005–2022
This table outlines the availability of monthly, provincial-resolution occupancy data (`occupancy_rate` %, `ADR`, and `RevPAR`) from candidate sources.

| Source | Monthly? | Provincial? | Back to 2005? | 2005–2009 | 2010–2014 | 2015–2019 | 2020–2022 | Known breaks / redesigns / COVID collection changes |
|---|---|---|---|---|---|---|---|---|
| **StatCan** (Best Tables from Table 1) | **NO** | **NO** | **NO** | NO | NO | NO | NO | **No occupancy tables exist.** TASPI (18-10-0249-01) covers price indexes only. |
| **CBRE Hotels Canada** | **YES** | **YES** | **YES** | YES | YES | YES | YES | Continuous coverage. Data compiled from voluntary submissions representing ~40% of the Canadian industry. |
| **STR / CoStar** | **YES** | **YES** | **YES** | YES | YES | YES | YES | Continuous coverage. Global industry gold standard. |
| **Institut de la statistique du Québec (ISQ)** | **YES** | **YES** (QC only) | **YES** | YES | YES | YES | YES | **No breaks.** Enquête sur la fréquentation has run since 1983. Mode shifted to census (4+ units) in May 2025. COVID questionnaires adapted for non-tourist occupancy (quarantine/shelter). |
| **Travel Alberta / Alberta Economic Dashboard** | **YES** | **YES** (AB only) | **NO** | NO | YES | YES | YES | **Dashboard data starts in 2008/2010**. Sourced from CBRE. Excludes major resort areas (Banff, Jasper, etc.) from the general provincial index. |

---

### Table 3 — Access Route and Licensing

| Source | Programmatic Access | Licence / Terms for Academic Use | Required Citation Format |
|---|---|---|---|
| **StatCan** | StatCan Web Data Service (WDS) API or direct download of full-table CSVs. | **Statistics Canada Open Licence**. Free academic and commercial use with attribution. | Statistics Canada, Table [Table ID]: [Table Title], [Year/Period]. |
| **CBRE Hotels Canada** | No public API. Standard reports are issued as monthly PDFs/excels. | **Proprietary**. Restricted to paying subscribers. Academic use requires custom agreement or institutional purchase. | CBRE Hotels Canada, "Trends in the Canadian Hotel Industry: National Market Report", [Month, Year]. |
| **STR / CoStar** | No public API. Data delivered via paid subscriptions (STR reports). | **Proprietary**. Restricted. Academic licensing available through CoStar Group under strict non-disclosure. | CoStar Group / STR, "Destination Report: Canada", [Month, Year]. |
| **ISQ (Tourisme Québec)** | Power BI dashboard extraction or public tables on ISQ portal (CSV/Excel). | **Québec Open Government Licence**. Free academic use with attribution. | Institut de la statistique du Québec (ISQ), "Enquête sur la fréquentation des établissements d'hébergement du Québec", [Month, Year]. |
| **Alberta Economic Dashboard** | Direct download of CSV/XLSX/JSON from indicator dashboard pages. | **Alberta Open Government Licence**. Free academic use with attribution. | Government of Alberta, "Alberta Economic Dashboard: Accommodation occupancy rate", sourced from CBRE, accessed [Date], [URL]. |

---

### Table 4 — Fallback and Complementary Sources, Ranked

| Source | Geography | Frequency | Years | Cost / Access Barrier | Fitness for Filling StatCan Gaps (High/Med/Low) + Why |
|---|---|---|---|---|---|
| **1. Tourisme Québec / ISQ** | Quebec provincial, tourist regions, cities/MRC | Monthly | 1983–Present | **None** (Free, Open Data) | **High (for QC)**. Authoritative government statistic, covers the entire 2005–2022 window monthly, includes ADR and location revenues. |
| **2. Travel Alberta / Alberta Economic Dashboard** | Alberta provincial, tourism regions, cities | Monthly | 2008/10–Present | **None** (Free, Open Data) | **High (for AB)**. Publicly accessible download, sourced from CBRE. Fills 2010–2022 completely. Gaps in 2005–2009 must be spliced. |
| **3. CBRE Hotels Canada** | Canada, Provinces, major municipal markets | Monthly | Pre-2005–Present | **High** (Proprietary subscription) | **High**. Standard industry report series. Directly covers the 2005–2009 gap for Alberta, and covers Quebec. |
| **4. STR / CoStar** | Canada, Provinces, municipal markets/sub-markets | Monthly | Pre-2005–Present | **High** (Proprietary subscription) | **High**. Fills all gaps with high granularity. Expensive licensing is the only barrier. |
| **5. Destination Canada** | Canada, Provinces | Monthly / Quarterly | Varies (Recent focus) | **None** (Free hub) | **Medium**. Acts as an aggregator of STR/CBRE. Good for validation but lacks raw historical CSV downloads back to 2005. |

---

### Table 5 — Sanity Magnitudes (For Validating Downloaded Series)

| Quantity | Value | Source |
|---|---|---|
| **QC Annual-Average Occupancy, pre-COVID (2015–2019)** | **60.0% – 65.0%** | ISQ / Tourisme Québec |
| **AB Annual-Average Occupancy, pre-COVID (2015–2019)** | **54.0% – 58.0%** (Excluding resorts) | Alberta Economic Dashboard (CBRE) |
| **Montreal Market Occupancy, pre-COVID (2019)** | **~73.0%** | Greater Montreal Hotel Association / CBRE |
| **Calgary Market Occupancy, pre-COVID (2019)** | **~62.0%** | Calgary Hotel Association / CBRE |
| **2020-04 COVID Trough (National)** | **18.8%** (81.2% vacancy) | STR / CoStar |
| **2020-04 COVID Trough (Montreal)** | **< 4.0%** (Downtown market) | Greater Montreal Hotel Association / CBC |
| **2020-04 COVID Trough (Calgary)** | **3.0% – 8.0%** | Calgary Hotel Association / CBC |
| **2022 Recovery Level (vs 2019) (Montreal)** | **~61.0%** (vs 73.0% in 2019) | HVS / Marcus & Millichap |
| **2022 Recovery Level (vs 2019) (Calgary)** | **~58.0% – 60.0%** (vs 62.0% in 2019) | Calgary Hotel Association |

---

## Part C — Synthesis (The Acquisition Recipe)

### 1. Recommended Primary + Fallback Splicing Strategy
To construct a continuous, monthly, provincial-level dataset for Quebec (QC) and Alberta (AB) spanning **2005–2022**, the following hybrid recipe is recommended:

*   **Quebec (QC):**
    *   **Primary Source:** Use the **Institut de la statistique du Québec (ISQ)** "Enquête sur la fréquentation des établissements d'hébergement du Québec" dataset.
    *   **Method:** Download the historical monthly series directly from the ISQ website or Ministry of Tourism dashboards. This provides 100% of the coverage for 2005–2022 at the monthly provincial scale.
    *   **Splicing:** None required. The dataset is structurally consistent.
*   **Alberta (AB):**
    *   **Primary Source:** Use the **Alberta Economic Dashboard** "Accommodation occupancy rate" series (sourced from CBRE).
    *   **Method:** Download the public CSV dataset covering **2010–2022**.
    *   **Splicing / Fallback:** Since the dashboard's online CSV series does not cover 2005–2009, obtain the **CBRE Hotels Canada National Market Report** archives for **2005–2009**.
    *   **Splice Point:** **January 1, 2010**. Match the CBRE monthly reports to the Alberta Dashboard series. 
    *   *Splicing Calibration:* Calculate the average variance between the dashboard and the CBRE raw reports for the overlapping year 2010. Because the dashboard excludes resorts (Banff/Jasper), the dashboard occupancy is typically 2–4 percentage points lower than the raw CBRE provincial average (which includes resorts). Apply a scaling factor to the 2005–2009 CBRE provincial data to align it with the dashboard's "excluding resorts" definition:
    \[
    \text{Occupancy}_{\text{Spliced}}(t) = \text{Occupancy}_{\text{CBRE, Provincial}}(t) \times \left( \frac{\text{Mean}(\text{Dashboard}_{2010})}{\text{Mean}(\text{CBRE, Provincial}_{2010})} \right)
    \]

### 2. Data-Dictionary Verdict Against Project Schema
Our target schema is:
```
hotel_occupancy_monthly.csv: YEAR, MONTH, PR, occupancy_rate (0–1), ADR_CAD, RevPAR_CAD
```

*   **YEAR, MONTH, PR:** Sourced directly from all databases. `PR` is mapped to `QC` or `AB`.
*   **occupancy_rate (0–1):** Sourced directly. For ISQ, convert the percentage (e.g., 65.2%) to a decimal fraction (0.652). For the Alberta dashboard, do the same.
*   **ADR_CAD (Average Daily Rate):**
    *   *QC (ISQ):* Sourced from the *prix moyen de location* (average rental price) variable.
    *   *AB (CBRE/Dashboard):* Sourced from the *Average Daily Room Rate* variable.
*   **RevPAR_CAD (Revenue per Available Room):**
    *   *QC (ISQ):* Sourced from the *revenu de location par unité disponible* (RUD) variable. If missing in some sub-regional cuts, calculate as:
    \[
    \text{RevPAR\_CAD} = \text{occupancy\_rate} \times \text{ADR\_CAD}
    \]
    *   *AB (CBRE/Dashboard):* Sourced directly from the *Revenue per Available Room* variable in the dashboard.

---

### 3. Implications for the SARIMA Design
*   **Shorter Training Window (No Splice Option):** If the project elects not to splice the 2005–2009 CBRE data for Alberta due to cost/licensing barriers, the training window for the SARIMA model must be shortened to **2010–2022** (13 years of monthly data, or 156 observations). While 156 data points are technically sufficient to fit a robust `SARIMA(1,1,1)(1,1,1,12)` model, this reduces the model's ability to learn long-term pre-recession economic baselines (e.g., the 2008 oil shock recovery in Alberta).
*   **Splice Dummy Variables:** Splicing the 2005–2009 CBRE data introduces a risk of a level shift due to the inclusion/exclusion of mountain resorts in the sampling frame. If a level shift is detected in 2010, the SARIMA model must include an exogenous binary **level-shift dummy variable** (\(D_{\text{splice}} = 1\) for \(t \ge \text{Jan 2010}\), else \(0\)) to prevent the shift from distorting the forecast trend.
*   **COVID Indicator:** The COVID period (March 2020 to June 2022) represents a massive, non-seasonal structural shock (the occupancy rate fell to < 8% in Calgary and < 4% in Montreal). The SARIMA forecast *must* incorporate a binary indicator variable (\(D_{\text{COVID}} = 1\) for \(t \in [\text{2020-03}, \text{2022-06}]\), else \(0\)) to isolate this period; otherwise, the seasonal parameters and trend coefficients will be severely corrupted, leading to a collapsed or wildly fluctuating 2030 projection.

---

### 4. Market-Level (Montreal/Calgary) vs. Provincial (QC/AB) Modeling
Using city-market-level data (Calgary and Montreal) is **strongly recommended** over provincial-level averages for the following reasons:

1.  **Aesthetic and Magnitude Gaps:** Tall and SuperTall buildings are urban downtown typologies. Provincial averages smear urban demand with highway motels and secondary/rural markets, understating typical urban occupancy. Pre-COVID, Montreal's occupancy was **~73%** compared to the Quebec provincial average of **~60–65%**.
2.  **Calgary Stampede and Montreal Grand Prix Spikes:** Downtown markets exhibit highly localized, intense seasonal peaks. In Calgary, the Stampede in July creates a massive surge in occupancy (often > 85%) and a near-tripling of ADR. In Montreal, the Grand Prix weekend in June and major summer festivals create similar spikes. These spikes drive peak building cooling loads and domestic hot water (DHW) demand. If provincial data is used, these critical peaks are smoothed out, causing the EnergyPlus model to under-predict summer electrical and thermal peaks.
3.  **Data Availability:** Both ISQ (for Montreal region) and CBRE/STR (for Calgary market) publish monthly market-level data covering the entire window, making market-specific modeling highly feasible.

---

## Confidence and Caveats

> [!WARNING]
> **Least Certain Component:** The historical CBRE/STR provincial and city-level data for Alberta from **2005 to 2009** is the least certain to acquire without budget. While we know the data exists in CBRE archives, it is behind a commercial paywall.
> 
> **Resolution:** If access to 2005–2009 commercial CBRE data is blocked, the team should either:
> 1. Truncate the Alberta training window to start in **January 2010**, utilizing the free Alberta Economic Dashboard data.
> 2. Use the **Statistics Canada Traveller Accommodation Services Price Index (TASPI - Table 18-10-0249-01)** for Alberta from 2005–2009 as an exogenous proxy in a regression model to backcast the 2005–2009 Alberta occupancy rate based on the 2010–2022 dashboard relationship.

---

## References

1.  **Institut de la statistique du Québec (ISQ).** (2025). *Enquête sur la fréquentation des établissements d’hébergement du Québec.* Ministère du Tourisme. [ISQ Accommodation Program Info](https://www.quebec.ca/tourisme-et-loisirs/services-industrie-touristique/etudes-statistiques).
2.  **Government of Alberta.** (2026). *Alberta Economic Dashboard: Accommodation occupancy rate.* Sourced from CBRE Limited. [Alberta Economic Dashboard](https://economicdashboard.alberta.ca/dashboard/accommodation-occupancy-rate/).
3.  **Statistics Canada.** (2024). *Table 18-10-0249-01: Traveller accommodation services price index, monthly.* [StatCan TASPI Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810024901).
4.  **Statistics Canada.** (2024). *Table 24-10-0049-01: Canadian Tourism Activity Tracker and Grouped Data Sources (Archived).* [StatCan Tourism Tracker Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2410004901).
5.  **CBRE Hotels Canada.** (2019). *Trends in the Canadian Hotel Industry: National Market Report - 2019 Annual Review.* CBRE Limited. [CBRE Canada Hotels](https://www.cbre.ca/en/services/invest-finance-and-value/valuation-and-advisory/hotels).
6.  **CoStar Group / STR.** (2020). *STR Destination Report: Canadian Hotel Performance (April 2020 Trough Analysis).* [CoStar Canada Lodging Performance](https://www.costar.com).
7.  **Destination Canada.** (2025). *Canadian Tourism Data Collective.* [Tourism Data Collective Portal](https://ctdc.destinationcanada.com/).
