# Front Matter - Abstract, Keywords, Highlights

**Manuscript:** From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005-2030)
**Authors:** O. Iseri and C. Hachem-Vermette · Concordia University

---

## Abstract

*Context.* Tall buildings increasingly stack residential, office, retail and hospitality uses inside one structure, yet the occupancy schedules driving their energy models remain single-channel, borrowed from one use and held at code default everywhere else. *Gap.* No published occupancy generator produces multiple independent, jointly-trained presence channels for one mixed-use building, and the energy-use-intensity references used to judge such channels were built for single-use stock, not stacked towers. *Aim.* This study jointly trains one model to generate four independent time-use presence channels and injects them into a mixed-use tower. *Methodology.* A three-head conditional Transformer, trained on four Canadian General Social Survey time-use cycles, generates residential, office and retail presence; a SARIMA side-track driven by provincial tourism statistics generates hotel presence; a per-space Tag-2 dispatch injects all four into PNNL Tall and SuperTall prototypes across two Canadian cities, forecast 2005-2030 (56 cells: four channels, two prototypes, two cities). *Key quantified results.* The four populations do not behave as one occupant: they peak at four different hours, hotel at 18.91 h against a midday cluster near 12 h for the other three, and the resulting whole-building coincidence factor stays below 1 in all four building-city cells (median 0.941), so use-type diversity attenuates the aggregate peak inside a single building. Three of four channel EUI gates fail: the uninjected office control alone scores 85.45 kWh/m2/yr against a floor of 100; the hotel gate splits into two prototype clusters 84.64 kWh/m2/yr apart, 70.5% of the band width, with the 300 ceiling inside that gap; the retail median sits 5.47% below its floor. *Impact.* These failures are findings about reference-band applicability to mixed-use towers, not model error, reported at full strength with no band widened to pass them.<!-- BUILD NOTE RESOLVED 2026-08-08 by RV10 item 1: THERE IS NO CAP. The Building and Environment guide for authors states only "A concise and factual abstract is required" and gives no numeric word limit for Research Papers; the report marked the item NOT STATED, which is the answer the prompt asked for rather than a number invented to fill the row. The abstract stays at 272 words and is NOT cut. This is the exact question the 2J round got wrong in the other direction, cutting to a 200-word limit that had no source; the discipline that paid off was refusing to cut before reading, so it is recorded here rather than deleted. -->

---

## Keywords

Multi-channel occupancy; Mixed-use tall building; Time-use survey; Joint multi-task transformer; Building energy simulation; Energy use intensity band<!-- BUILD NOTE RESOLVED 2026-08-08 by RV10 item 6. This list was 13 keywords; the Building and Environment guide caps it at 6 and asks for American spelling, no plural forms, and no composite phrases joined by "and" or "of". Cut to 6, keeping one term per dimension the paper is indexed on: method, object, data source, model, field, finding. Dropped, and where each survives in the text: Retail Occupancy and Hotel Occupancy (both channels are named in the title-adjacent abstract and throughout Section 3); Tourism Statistics (Section 3.4); Canadian General Social Survey and NECB (both spelled out in the abstract); PNNL Prototype Buildings (abstract); Longitudinal Forecasting (the 2005-2030 range is in the title). Nothing indexed here was lost from the manuscript, only from this list. -->


---

## Highlights

<!-- APPARATUS NOTE: house rule for this section - 5 bullets, each <= 85 characters. Checked by f4. Not reader-facing; stripped from the submission copy. -->

- Four occupant populations in one tower peak at four different hours.
- Coincidence factor below 1 in all four cells: use diversity flattens the peak.
- One Transformer jointly generates four independent occupancy channels.
- Uninjected office control fails its own band, 85.45 kWh/m2/yr vs a floor of 100.
- Hotel gate splits into two clusters 84.64 kWh/m2/yr apart, deciding the verdict.

---

## Author Information

**Orcun Koral Iseri**\textsuperscript{1,\*} · **Caroline Hachem-Vermette**\textsuperscript{1}

1 Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* *Corresponding author:* orcunkoral.oseri@concordia.ca

*ORCID:* Orcun Koral Iseri - https://orcid.org/0000-0001-7735-3363<!-- BUILD NOTE RESOLVED 2026-08-08, see the note immediately following: affiliation, address and Iseri ORCID are taken verbatim from the 2J title page as submitted to Building Simulation on 2026-08-07 (2J_docs_occ_nTemp/writing/submission/submissionDocs/Title_Page_and_Cover_Letter.md), so they are confirmed, not drafted. Hachem-Vermette carries no ORCID there either, so none is stated here: an ORCID is an identifier and inventing one would point at a real stranger. Ask the co-author, then add. --><!-- BUILD NOTE RESOLVED 2026-08-08 by RV10 item 21: the missing co-author ORCID does NOT block submission. Elsevier requires an ORCID iD for the CORRESPONDING author, which Iseri has and which is stated above; co-author iDs are optional. Asking Hachem-Vermette is still worth doing, because an iD added at submission is easier than one added at proof, but it is now a courtesy rather than a blocker. -->

---

## Declarations

**Funding.** This postdoctoral research was financially supported by the Natural Sciences and Engineering Research Council of Canada (NSERC) and the Voltage-Age Seed fund. The authors gratefully acknowledge this support.

**Data availability.** The General Social Survey Time-Use microdata and the provincial tourism-statistics series (ISQ for Quebec, CBRE/Travel Alberta for Alberta) analysed in this study are publicly available under the catalogue numbers listed in §2. The derived four-channel occupancy schedules, the injected IDFs, and the analysis code are available from the corresponding author on reasonable request.

**Declaration of competing interest.** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

**CRediT authorship contribution statement.** **Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing - original draft. **Caroline Hachem-Vermette:** Conceptualization, Supervision, Funding acquisition, Resources, Writing - review and editing. Both authors read and approved the final manuscript.

**Ethical approval.** This study does not contain any studies with human or animal subjects performed by any of the authors. The analysis uses anonymized public-use microdata files released by Statistics Canada, together with published provincial tourism-occupancy statistics.

---

<!-- APPARATUS NOTE: no result or magnitude from the two-channel construction stage this paper builds on appears anywhere above; that stage is a construction step for this paper and is discussed only in Methods and in the Introduction's departure-point narrative (section 1.4). This is a standing check on the front matter, not a statement to the reader; stripped from the submission copy. -->

---

**Graphical abstract.** *(insert `graphicalAbstract.png` here)*

