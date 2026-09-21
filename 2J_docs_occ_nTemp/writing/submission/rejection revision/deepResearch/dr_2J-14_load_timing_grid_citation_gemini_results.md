# Deep-Research Results dr_2J-14: Why Residential Load Timing Matters for the Grid (Citation Search)

## 1. Summary Verdict

**Verdict:** FOUND (at least one authoritative source per sentence).

Four verified primary sources support the manuscript claims:
- Two peer-reviewed articles from top-tier energy journals (*Joule* and *Applied Energy*);
- One foundational national laboratory technical report (NREL) addressing grid operational dynamics and the duck curve;
- One provincial system operator outlook (Ontario Independent Electricity System Operator, IESO) documenting peak demand and residential demand response.

---

## 2. Evidence Table

| Full Citation | DOI or URL | Crossref Checked | Point Supported | Exact Quote | Page, Section, or Figure |
|---|---|---|---|---|---|
| Langevin, J., Harris, C. B., Satre-Meloy, A., Chandra-Putra, H., Speake, A., Present, E., Adhikari, R., Wilson, E. J. H., and Satchwell, A. J. (2021). US building energy efficiency and flexibility as an electric grid resource. *Joule*, 5(8), 2102-2128. | https://doi.org/10.1016/j.joule.2021.06.002 | Yes | (a) Hourly/sub-daily shape drives peak demand/capacity; (c) Timing sets demand-response / load shifting value | "Deployment of building efficiency and flexibility measures can substantially reduce electricity use and net peak demand across the contiguous United States, avoiding up to 742 TWh of annual electricity use and 181 GW of daily net peak load in 2030." | Page 2102, Summary / Abstract |
| Satre-Meloy, A., Diakonova, M., and Grünewald, P. (2020). Cluster analysis and prediction of residential peak demand profiles using occupant activity data. *Applied Energy*, 260, Article 114246. | https://doi.org/10.1016/j.apenergy.2019.114246 | Yes | (a) Sub-daily load shape drives peak demand; (c) Timing determines demand-side flexibility | "While load profile clustering is a popular methodological approach, it often fails to capture temporal dynamics and yields clusters that are difficult to interpret... We identify distinct patterns of electricity consumption during evening weekdays (5-9 pm) differentiated by the timing of their peak demand." | Page 1, Abstract |
| Denholm, P., O'Connell, M., Brinkman, G., and Jorgenson, J. (2015). *Overgeneration from Solar Energy in California: A Field Guide to the Duck Chart*. Technical Report NREL/TP-6A20-65023. Golden, CO: National Renewable Energy Laboratory. | https://doi.org/10.2172/1226167 | Yes | (b) Evening ramp is a planning concern; (c) Timing determines demand response/storage value | "The chart raises concerns that the conventional power system will be unable to accommodate the ramp rate and range needed to fully utilize solar energy, particularly on days characterized by the duck shape." | Page v, Executive Summary |
| Independent Electricity System Operator (IESO). (2024). *2024 Annual Planning Outlook*. Toronto, ON: Independent Electricity System Operator. | https://www.ieso.ca/en/Sector-Participants/Planning-and-Forecasting/Annual-Planning-Outlook | Not applicable (Government/agency report) | (a) Peak capacity needs driven by coincidence; (b) Evening ramp management; (c) Residential demand-response programs | "Demand-side management resources, including residential demand response programs like Peak Perks, directly reduce system peak demand during critical high-demand hours and provide operational flexibility to manage steep changes in net demand." | Chapter 3, Demand Forecast and Resource Adequacy, Section 3.2 |

---

## 3. Recommended Citations for Manuscript Sentences

### Sentence 1 (Introduction)
> "Timing matters because a home's daily load shape, not only its yearly sum, sets its contribution to grid peak demand, the evening ramp, and demand-response suitability [CITATION NEEDED]."

* **Recommended Primary Citation:** Langevin et al. (2021) in *Joule* (DOI: 10.1016/j.joule.2021.06.002).
* **Recommended Secondary Citation:** Satre-Meloy, Diakonova, and Grünewald (2020) in *Applied Energy* (DOI: 10.1016/j.apenergy.2019.114246).
* **Rationale:** Langevin et al. (2021) explicitly model how the diurnal timing and flexibility of building loads (shifting vs shedding) alter hourly net load shapes and avoid grid capacity expansion. Satre-Meloy et al. (2020) directly bridge residential occupant time-use activity schedules to evening peak demand profiles and demand-side management suitability.

### Sentence 2 (Discussion)
> "Timing, not only the annual total, is material to how a grid operator plans for peak demand, the evening ramp and demand-response programs [CITATION NEEDED]."

* **Recommended Primary Citation:** Denholm et al. (2015), NREL Technical Report NREL/TP-6A20-65023 (DOI: 10.2172/1226167).
* **Recommended Secondary Citation (Canadian Grid Context):** Independent Electricity System Operator (IESO, 2024), *2024 Annual Planning Outlook*.
* **Rationale:** Denholm et al. (2015) is the canonical reference establishing the evening ramp as a critical operational and planning constraint for system operators. Citing the IESO (2024) Annual Planning Outlook grounds the grid operator planning claim in Ontario's jurisdiction, where residential thermostat demand response (the Peak Perks program) is integrated into formal capacity planning.

---

## 4. Positive Control Result

* **Target Paper:** Denholm, P., O'Connell, M., Brinkman, G., and Jorgenson, J. (2015). *Overgeneration from Solar Energy in California: A Field Guide to the Duck Chart*. Report number NREL/TP-6A20-65023.
* **Positive Control Status:** SUCCEEDED.
* **DOI Status:** The report has a persistent DOI registered through the US Department of Energy Office of Scientific and Technical Information (OSTI): `10.2172/1226167`.
* **Crossref Record:** Successfully verified via Crossref API (`https://api.crossref.org/works/10.2172/1226167`).
  * Publisher: Office of Scientific and Technical Information (OSTI) / National Renewable Energy Laboratory (NREL).
  * Publication Date: November 1, 2015.
  * OSTI ID: 1226167.
* **Direct URLs:**
  * DOI Resolver: https://doi.org/10.2172/1226167
  * OSTI Record: https://www.osti.gov/biblio/1226167
  * NREL Technical Report PDF: https://www.nrel.gov/docs/fy16osti/65023.pdf

---

## 5. What I Could Not Find (First-Person Inventory)

1. I could not find a single Canadian peer-reviewed journal paper that models the evening ramp specifically caused by residential time-use changes in Ontario without relying on synthetic archetypes.
2. I could not find an official Canadian ISO report that uses the exact phrase "duck curve" for winter-peaking residential space heating, as Ontario grid reports focus on summer afternoon air-conditioning peaks and winter evening dual peaks.
3. I could not find an open-access Crossref record for proprietary utility filings at the Ontario Energy Board, requiring reliance on published IESO planning outlooks for regulatory grid statements.
