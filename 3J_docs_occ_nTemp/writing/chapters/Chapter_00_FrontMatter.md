# Front Matter - Abstract, Keywords, Highlights

**Manuscript:** From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005-2030)
**Authors:** O. Iseri and C. Hachem-Vermette · Concordia University

---

## Abstract

*Context.* Tall buildings increasingly stack residential, office, retail and hospitality uses inside one structure, yet the occupancy schedules driving their energy models remain single-channel, borrowed from one use and held at code default everywhere else. *Gap.* No published occupancy generator produces multiple independent, jointly-trained presence channels for one mixed-use building, and the energy-use-intensity references used to judge such channels were built for single-use stock, not stacked towers. *Aim.* This study jointly trains one model to generate four independent time-use presence channels and injects them into a mixed-use tower. *Methodology.* A three-head conditional Transformer, trained on four Canadian General Social Survey time-use cycles, generates residential, office and retail presence; a SARIMA side-track driven by provincial tourism statistics generates hotel presence; a per-space Tag-2 dispatch injects all four into PNNL Tall and SuperTall prototypes across two Canadian cities, forecast 2005-2030 (56 cells: four channels, two prototypes, two cities). *Key quantified results.* Three of four channel EUI gates fail: the uninjected office control alone scores 85.45 kWh/m2/yr against a floor of 100; the hotel gate splits into two prototype clusters 84.64 kWh/m2/yr apart, 70.5% of the band width, with the 300 ceiling inside that gap; the retail median sits 5.47% below its floor. *Impact.* These failures are findings about reference-band applicability to mixed-use towers, not model error, reported at full strength with no band widened to pass them.

---

## Keywords

Multi-Channel Occupancy; Mixed-Use Buildings; Time-Use Survey; Joint Multi-Task Transformer; Retail Occupancy; Hotel Occupancy; Tourism Statistics; Building Energy Simulation; Energy Use Intensity Reference Bands; Canadian General Social Survey (GSS); National Energy Code for Buildings (NECB); PNNL Prototype Buildings; Longitudinal Forecasting

---

## Highlights

*(5 bullets, each <=85 characters.)*

- One Transformer jointly generates four independent occupancy channels.
- Tag-2 dispatch injects residential, office, retail and hotel into one tower.
- 56-cell campaign spans four channels, two prototypes, two cities, 2005-2030.
- Uninjected office control fails its own band, 85.45 kWh/m2/yr vs a floor of 100.
- Hotel gate splits into two clusters 84.64 kWh/m2/yr apart, deciding the verdict.

---

## Author Information

**Orcun Koral Iseri**\textsuperscript{1,\*} · **Caroline Hachem-Vermette**\textsuperscript{1}

1 Concordia University, Montreal, Quebec, Canada - *(department/institute to confirm)*

\* *Corresponding author:* orcunkoral.oseri@concordia.ca

*ORCID:* Iseri - [confirm]; Hachem-Vermette - [confirm]

---

## Declarations

**Funding.** This postdoctoral research was financially supported by the Natural Sciences and Engineering Research Council of Canada (NSERC) and the Voltage-Age Seed fund. *(reused from the 2J front matter; confirm still accurate for this manuscript before submission)*

**Data availability.** The General Social Survey Time-Use microdata and the provincial tourism-statistics series (ISQ for Quebec, CBRE/Travel Alberta for Alberta) analysed in this study are publicly available under the catalogue numbers listed in §2. The derived four-channel occupancy schedules, the injected IDFs, and the analysis code are available from the corresponding author on reasonable request.

**Declaration of competing interest.** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

**CRediT authorship contribution statement.** *(draft - confirm/adjust the split)* **Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing - original draft. **Caroline Hachem-Vermette:** Conceptualization, Supervision, Funding acquisition, Resources, Writing - review & editing.

---

*Front-matter notes for the author: items marked **[confirm]** need input before submission (department/institute, ORCIDs, exact CRediT split, funding-line accuracy for this manuscript). No result or magnitude from the two-channel construction stage this paper builds on appears anywhere above; that stage is a construction step for this paper and is discussed only in Methods and in the Introduction's departure-point narrative (§1.4).*

---

**Graphical abstract.** *(insert `graphicalAbstract.png` here)*

