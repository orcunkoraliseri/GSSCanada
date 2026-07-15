# Front Matter — Abstract, Keywords, Highlights

**Manuscript:** From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)
**Authors:** O. Iseri and C. Hachem-Vermette · Concordia University

---

## Abstract

Stock-scale building energy models still run on static, pre-COVID occupancy schedules, yet the pandemic changed *when* residential energy is used, not only *how much*. This study forecasts the Canadian residential load shape from 2005 to 2030 from a calibrated behavioural occupancy time-series carried through the COVID/work-from-home structural break. Four General Social Survey time-use cycles (64,061 diaries) are harmonized, augmented with a gate-selected hybrid conditional Transformer, linked to the 2021 Census stock (144,507 households), and forecast by progressive fine-tuning under a True-Future-Test protocol. Six thousand paired EnergyPlus runs — fixed 50-household panels held constant within each of two cycle-year spans (2005-2015; 2022-2030), with archetypes and weather frozen throughout — isolate the pure occupancy effect, while activity-resolved end uses are anchored to the national household-energy survey (48 of 48 cell-years within ±2.7 %). Weekday at-home occupancy breaks +5.2 pp at COVID and persists to 2030 (+2.2 to +3.9 pp), yet annual electricity follows by only +1.4 to +2.6 % across the break and a further +0.6 to +1.2 % to 2030. The load shape, however, changes structurally — midday fill and flattening (Δmidday share +0.37 pp; Δload factor +0.012; both confidence intervals exclude zero) with the evening peak fixed at ~17:30, and activity resolution restructures the intraday equipment profile without displacing that peak (building-level shift 0 ± 1 h). Time-varying, survey-grounded schedules are therefore feasible at stock scale and materially change the ramping- and demand-response-relevant load metrics that static schedules cannot see.

*(Abstract structure: Context → Gap → Aim → Methodology → Key quantified results → Impact. ✔ ~185 words; trim toward ~150 at the target journal's limit if required.)*

---

## Keywords

Occupancy Modeling; Building Performance Simulation; Time-Use Survey; Load Shape; Peak Demand; Coincidence Factor; Conditional Transformer; Generative Deep Learning; Longitudinal Forecasting; COVID-19 / Work-From-Home; Canadian General Social Survey (GSS); Residential Building Stock; EnergyPlus

---

## Highlights

*(5 bullets, each ≤ 85 characters, every number verified against §5.)*

- Gate-selected Transformer augments 64,061 GSS diaries to ~192k calibrated days.
- 2030 occupancy forecast through the COVID/WFH break with a True-Future-Test protocol.
- 6,000 paired EnergyPlus runs isolate the pure occupancy effect at stock scale.
- WFH fills the midday valley and flattens load; the ~17:30 evening peak does not move.
- Activity-resolved end uses match SHEU within ±2.7% in all 48 dwelling-by-year cells.

---

## Author Information

**Orcun Koral Iseri**¹,\* · **Caroline Hachem-Vermette**¹

¹ Concordia University, Montréal, Québec, Canada — *(department/institute to confirm — e.g., Gina Cody School of Engineering and Computer Science / Next-Generation Cities Institute)*

\* *Corresponding author:* orcunkoral.oseri@concordia.ca

*ORCID:* Iseri — [confirm]; Hachem-Vermette — [confirm]

---

## Declarations

**Funding.** This postdoctoral research was financially supported by the Natural Sciences and Engineering Research Council of Canada (NSERC) and the Voltage-Age Seed fund.

**Acknowledgements.** The authors gratefully acknowledge the financial support provided for this postdoctoral research by NSERC and the Voltage-Age Seed fund.

**Data availability.** The General Social Survey Time-Use and Census Public-Use Microdata Files analysed in this study are publicly available from Statistics Canada under the catalogue numbers listed in §2 (GSS Time Use, Cat. 45-25-0001; 2021 Census PUMF, Cat. 98M0001X). The derived behavioural-occupancy schedules, the calibrated BEM schedule files, and the analysis code are available from the corresponding author on reasonable request.

**Declaration of competing interest.** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

**CRediT authorship contribution statement.** *(draft — confirm/adjust the split)* **Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing – original draft. **Caroline Hachem-Vermette:** Conceptualization, Supervision, Funding acquisition, Resources, Writing – review & editing.

---

*Front-matter notes for the author: items marked **[confirm]** need your input — the source papers (`resources/1st_Occ_Journal.md`, `resources/ConferencePaper.md`) are blinded for authorship, so department/institute, ORCIDs, and the exact CRediT split could not be drawn from them. Only the funding line ("NSERC and the Voltage-Age Seed fund") was recoverable from the conference paper.*
