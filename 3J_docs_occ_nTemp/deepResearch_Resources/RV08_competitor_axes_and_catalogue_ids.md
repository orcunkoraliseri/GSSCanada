# RV08. Six competitor-positioning axes and two dataset catalogue identifiers

## Section A. Direct answer

This report settles six competitor-positioning axes across two primary studies (Doma and Ouf; Buttitta and Finn) and clarifies the bibliographic catalogue identifiers for two hotel-occupancy statistical sources (ISQ and CBRE/Travel Alberta). All eight items are settled without relaxing any project gates or relying on unverified claims. Crucially, none of the Settled findings alter or weaken our core manuscript claim: no published work combines a time-use-survey-driven, multi-channel, forecast-to-a-future-year occupancy model inside a single mixed-use building. Additionally, Crossref verification revealed two severe DOI citation errors in our prior report (`dr_L3-10`), which had assigned unrelated DOIs to both primary competitor studies.

| # | Item | Verdict | Settled Value / Finding |
|---|---|:---:|---|
| 1 | Doma and Ouf: Time-series occupancy (within-day resolution) | **SETTLED** | Yes. Mobile positioning data is aggregated into 24-hour diurnal profiles resolving hourly visitor variation across weekday and weekend day-types. |
| 2 | Doma and Ouf: Calibrated behavioural model | **SETTLED** | Case (c): No calibration reported. Model derives data-driven schedules without calibrating against measured occupancy ground truth or utility energy records. |
| 3 | Doma and Ouf: Stock-scale | **SETTLED** | District scale (221 buildings covering office, retail, and residential uses in downtown Montreal, Quebec). |
| 4 | Buttitta and Finn: Calibrated behavioural model | **SETTLED** | Case (c): No calibration reported. Stochastic occupancy profiles are generated via MCMC without calibration against measured occupancy or billing data in this paper. |
| 5 | Buttitta and Finn: Activity or end-use resolved | **SETTLED** | Presence / occupancy state count only. Resolves state presence (active home, sleeping, away) for space heating integration, not specific activity breakdowns like cooking or hot water. |
| 6 | Buttitta and Finn: Stock-scale | **SETTLED** | Archetype dwellings. Models 4 residential building archetypes (detached, semi-detached, terraced, apartment) representing national stock rather than individual counted real-world buildings. |
| 7 | ISQ monthly hotel-occupancy statistics catalogue ID | **SETTLED** | Named series without catalog number: *Enquête sur la fréquentation des établissements d'hébergement du Québec*, published by Institut de la statistique du Québec (ISQ). Database BDSO closed Dec 2025; served via Power BI dashboard on `statistique.quebec.ca`. License: *Licence du gouvernement ouvert - Québec*. |
| 8 | CBRE / Travel Alberta hotel-occupancy catalogue ID | **OUR ERROR** | Misnamed 2005-2009 source. The 2005-2009 span derives from *Trends in the Canadian Hotel Industry* (PKF Consulting / CBRE Hotels) and *Canadian Hotel Market Report* (CBRE Hotels). The 2010-2022 open series is *Alberta Tourism Market Monitor* (Government of Alberta / Travel Alberta, `open.alberta.ca`, source tag `ABMKTMONITOR`, Open Government Licence - Alberta). |

---

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Doma and Ouf modeled district building count | 221 | buildings | empirical | all-fuel | GFA | 6A (Montreal) | N/A | Doma and Ouf (2023, 2024) | Tier 3 | H |
| B2 | Doma and Ouf sub-daily temporal resolution | 1 | hour | empirical | N/A | N/A | 6A (Montreal) | N/A | Doma and Ouf (2023, 2024) | Tier 3 | H |
| B3 | Buttitta and Finn residential building archetypes | 4 | archetypes | as-modelled | all-fuel | CFA | 5A (Ireland) | N/A | Buttitta and Finn (2020) | Tier 3 | H |
| B4 | Buttitta and Finn temporal resolution | 10 | minute | empirical | N/A | N/A | 5A (Ireland) | N/A | Buttitta and Finn (2020) | Tier 3 | H |
| B5 | ISQ hotel occupancy minimum establishment size | 4 | rental units | empirical | N/A | N/A | 6A (Quebec) | N/A | ISQ (2024) | Tier 2 | H |
| B6 | Alberta Tourism Market Monitor series start year | 2010 | year | empirical | N/A | N/A | 7A (Alberta) | N/A | Government of Alberta (2024) | Tier 2 | H |

---

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|
| Residential | Yes | Direct positioning contrast | Buttitta and Finn (2020) and Doma and Ouf (2023, 2024) cover residential occupancy but lack multi-channel integration in a single building. | High |
| Office | Yes | Direct positioning contrast | Doma and Ouf cover office space at district scale; our pipeline covers stacked office native spaces inside one tower. | High |
| Retail | Yes | Direct positioning contrast | Doma and Ouf cover retail at district scale; our pipeline covers retail podium native spaces inside one tower. | High |
| Hotel | Yes | Catalogue metadata update | Clarifies ISQ Power BI web series and CBRE / Alberta Tourism Market Monitor (`ABMKTMONITOR`) identifiers for hotel guest-room multipliers. | High |

---

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|
| Table 1 Competitor Matrix | Eight cells marked `n/r` or `? check source` | Replace six matrix cells with settled values (Doma and Ouf: sub-daily Yes, calibration None, scale District 221 buildings; Buttitta and Finn: calibration None, activities No/Count, scale Archetypes). | Interpretation change | Low |
| Bibliography DOIs | Invalid DOIs cited in `dr_L3-10` | Update DOIs for Doma and Ouf (2024) to `10.1016/j.apenergy.2024.124081` and Buttitta and Finn (2020) to `10.1016/j.enbuild.2019.109577`. | Citation correction | Low |
| Hotel Data Citations | Cited CBRE archives generic span 2005-2009 | Split citation into PKF/CBRE *Trends in the Canadian Hotel Industry* (2005-2009) and *Alberta Tourism Market Monitor* (`ABMKTMONITOR`, 2010-2022). | Citation correction | Low |

---

## Section E. What this changes in the write-up

- Update Table 1 Competitor Positioning Matrix in manuscript text: replace all `n/r` cells for Doma and Ouf (2023, 2024) and Buttitta and Finn (2020) with settled entries.
- Section 2.4 "Closest Prior Works & Differentiation": add explicit notes stating Doma and Ouf operate at district scale (221 buildings) without sub-building core stacking or calibration, and Buttitta and Finn model 4 residential archetypes without activity breakdown or calibration.
- Reference List: replace incorrect DOIs from `dr_L3-10` with verified Crossref DOIs (`10.1016/j.apenergy.2024.124081` for Doma and Ouf 2024; `10.1016/j.enbuild.2019.109577` for Buttitta and Finn 2020).
- Data Sources Section: refine ISQ citation to *Enquête sur la fréquentation des établissements d'hébergement du Québec* (Institut de la statistique du Québec, served via web dashboard) and split Alberta hotel market series into PKF/CBRE reports (2005-2009) and Open Alberta `ABMKTMONITOR` (2010-2022).

---

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Competitor axis completeness | Matrix cell coverage | 100% characterisation across 7 axes | Zero uncharacterised `n/r` cells | Primary papers opened | Tier 3 |
| Bibliography DOI validity | Crossref API HTTP status | 200 OK returning exact title match | 100% exact match across all DOIs | Crossref API | Tier 1 |

---

## Section G. Contradictions, gaps and open questions

- **Impact on Positioning Claim**: None of items 1 to 6 weaken our manuscript's core positioning claim. Neither Doma and Ouf (2023, 2024) nor Buttitta and Finn (2020) occupies the combination of a time-use-survey-driven, multi-channel, forecast-to-a-future-year occupancy model inside a single mixed-use building.
- **Major Citation Defects in Prior Report (`dr_L3-10`)**:
  - Doma and Ouf (2024): Cites DOI `10.1016/j.apenergy.2023.122247` in `dr_L3-10`. Crossref lookup confirms this resolves to an unrelated paper ("Environmental and material criticality assessment of hydrogen production via anion exchange membrane electrolysis" by E. Schropp et al., 2024). **The correct DOI is `10.1016/j.apenergy.2024.124081`**.
  - Buttitta and Finn (2020): Cites DOI `10.1016/j.enbuild.2019.109562` in `dr_L3-10`. Crossref lookup confirms this resolves to an unrelated paper ("The effect of a cold environment on sleep and thermoregulation..." by K. Tsuzuki et al., 2020). **The correct DOI is `10.1016/j.enbuild.2019.109577`**.
- **ISQ Catalogue Identifier Gap**: ISQ does not assign an alphanumeric dataset catalogue ID or table number to its hotel occupancy series. The BDSO (Banque de données des statistiques officielles) database was closed on December 18, 2025. Data is published on `statistique.quebec.ca` as an interactive Power BI dashboard under the title *Enquête sur la fréquentation des établissements d'hébergement du Québec*.
- **CBRE / Travel Alberta Attribution Gap**: The 2005-2009 historical span cited under "CBRE National Market Report archives" was published by PKF Consulting Canada under the title *Trends in the Canadian Hotel Industry* (PKF was acquired by CBRE Hotels in 2015). For 2010 onward, the primary dataset is the open-data *Alberta Tourism Market Monitor* published on `open.alberta.ca` under the Open Government Licence - Alberta.

---

## Section H. Full reference list

1. **Doma, A., Padsala, R., Ouf, M. M., & Eicker, U. (2024)**. Bottom-up framework for modelling occupancy-based demand-side management strategies in a mixed-use district. *Applied Energy*, 375, 124081. DOI: `10.1016/j.apenergy.2024.124081`. Tier 3.
   - *Full text read*: Yes.
   - *Crossref returned title*: "Bottom-up framework for modelling occupancy-based demand-side management strategies in a mixed-use district".

2. **Doma, A., & Ouf, M. (2023)**. Leveraging mobile positioning data to model building occupant behaviour in a mixed-use district. *Proceedings of Building Simulation 2023: 18th Conference of IBPSA*, 1671-1678. DOI: `10.26868/25222708.2023.1671`. Tier 3.
   - *Full text read*: Yes.
   - *Crossref returned title*: "Leveraging mobile positioning data to model building occupant behaviour in a mixed-use district".

3. **Buttitta, G., & Finn, D. P. (2020)**. A high-temporal resolution residential building occupancy model to generate high-temporal resolution heating load profiles of occupancy-integrated archetypes. *Energy and Buildings*, 206, 109577. DOI: `10.1016/j.enbuild.2019.109577`. Tier 3.
   - *Full text read*: Yes.
   - *Crossref returned title*: "A high-temporal resolution residential building occupancy model to generate high-temporal resolution heating load profiles of occupancy-integrated archetypes".

4. **Institut de la statistique du Québec (ISQ). (2024)**. *Enquête sur la fréquentation des établissements d'hébergement du Québec*. Direction des statistiques des entreprises, ISQ, Gouvernement du Québec. URL: `https://statistique.quebec.ca`. Tier 2.
   - *Full text read*: Yes (web methodology and dashboard documentation).
   - *Crossref returned title*: N/A (Government Statistical Data Dashboard).

5. **Government of Alberta. (2024)**. *Alberta Tourism Market Monitor*. Ministry of Tourism and Sport / Travel Alberta. Open Government Portal. Source tag: `ABMKTMONITOR`. URL: `https://open.alberta.ca/dataset/alberta-tourism-market-monitor`. Tier 2.
   - *Full text read*: Yes.
   - *Crossref returned title*: N/A (Open Government Data Series).

6. **PKF Consulting Canada & CBRE Hotels. (2009)**. *Trends in the Canadian Hotel Industry: National Market Report Archives (2005-2009)*. Toronto, ON: PKF / CBRE Hotels. Tier 2.
   - *Full text read*: Yes (archival summaries).
   - *Crossref returned title*: N/A (Proprietary Industry Report Series).
