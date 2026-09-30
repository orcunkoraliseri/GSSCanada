# Response to the editor and reviewers

Manuscript ID 266775447, Journal of Building Performance Simulation

Revised title: *Canadian residential occupancy schedules from four time-use cycles (2005–2022) and a hindcast-tested projection to 2025*

Dear Editor,

We thank you and the reviewer for the careful reading of our manuscript. We have revised it substantially. The paper is now positioned around the longitudinal-plus-projective occupant-behaviour pipeline, the projection is tested quantitatively against a held-out census, the data section is restructured and auditable, and the building simulations are presented as a demonstration. All changes are shown in the tracked-changes version. Below, each comment is in italics, followed by our response and the location of each change (section, table or figure of the revised manuscript).

While revising, we also re-checked every number in the paper against the data and the code, and found three errors in the submitted energy results. We report them here so that the editor and the reviewers can see what changed and why:

1. The energy figures of the submitted Section 4.2 came from a three-draw pilot batch, not from the 100 households per pairing stated in the text, and in that batch the 2010 schedule file was an exact copy of the 2005 file, so the 2010 and 2005 energy results were identical.
2. The annual end-use intensities were extracted with a routine that added each end use's peak demand (in W) to its annual energy (in kWh), which inflated every energy intensity.
3. In the 2005 and 2015 schedule inputs, weekday and weekend were swapped.

All schedules were rebuilt, and every simulation was run again with a pre-registered design: 30 random draws of households per neighbourhood and year, a stopping rule fixed before any result was read, and every result reported as a mean with its 95 % confidence interval. The energy extraction was corrected, reproduces the old values exactly when the peak-demand term is added back, and agrees with the hourly meters to within 0.02 %. The revised Sections 4.1 and 4.3 and all energy numbers in the Abstract, Discussion and Conclusion come from these new runs. The main message changes: against the reference schedule, the survey-based schedules raise heating by 6 to 16 % and lower cooling by 1 to 9 % in houses, change both by less than 7 % in apartment buildings, and do not move the time of the cooling peak, and we no longer propose correction factors for building codes.

## Reviewer 1

**Comment 1.** *The manuscript engages little of the existing TUS- and ATUS-based occupancy modeling literature. The authors should position their contribution against the existing body of work, including the ATUS review by Vosoughkhosravi, Jafari, and Zhu (2023), and state clearly what the longitudinal C-VAE framework adds beyond prior TUS-based approaches.*

**Response.** We agree. The Introduction has been rewritten into three parts: 1.1 time-use surveys in occupancy modelling, which now cites and uses the review by Vosoughkhosravi, Jafari and Zhu (2023), the review by Osman and Ouf (2021), the Markov-chain lineage (Richardson et al. 2008; Widén and Wäckelgård 2010) and the ATUS activity-profile work of Mitra, Chu and Cetin; 1.2 longitudinal and multi-cycle time-use studies (Sekar et al. 2018; Anderson and Torriti 2018; Yin et al. 2024; Dias dos Santos et al. 2025); and 1.3 the gap and contribution. A new Table 1 places these studies side by side on survey, number of cycles, unit modelled, projection beyond the last survey, test of the projection, and building simulation. The contribution is stated in one sentence: prior work either models one survey cycle or describes change across cycles without projecting beyond the last survey; this study harmonises four Canadian cycles into one household schedule format and adds a generative projection past the last census, tested by a held-out-cycle hindcast (Section 1.3). The generic background of the former Sections 1.1 to 1.4 was shortened by about half.

Location: Section 1, Table 1.

**Comment 2.** *Section 2 contains only a single subsection (2.1); either remove the subsection heading or restructure into multiple subsections. The section should also provide more detail, particularly on the regional representativeness of using national Census and GSS data for Montreal-specific simulations (e.g., whether the data were subset to Quebec or Montreal), along with per-cycle sample sizes and definitions of the key variables used.*

**Response.** Section 2 now has four subsections: 2.1 Census of Population PUMF, 2.2 GSS time-use cycles, 2.3 harmonisation, and 2.4 regional scope and representativeness. We added Table 2 (sample sizes per cycle, national and Quebec: Census persons and households, GSS respondents and episodes retained, households in each schedule file, households simulated) and Table 3 (definitions of the linking variables and of the output variables). On representativeness: the data were not subset to Quebec or Montreal, and no survey weights were used. The first matching tier requires the same province and CMA class, so Quebec households are matched to Quebec diaries when that tier succeeds. We now compare the occupancy metrics of Canada and of the Quebec subset for every cycle (Table 4): Quebec households are at home at most 0.3 h per weekday longer (0.9 h on 2022 weekends), with daytime occupancy fractions within 0.04 of the national values. These differences are smaller than the difference between cycles, so the national schedules were kept and no scenario was re-run with the Quebec subset. Because no weights were applied, we removed the claim that the schedules are nationally representative.

Location: Section 2, Tables 2–4.

**Comment 3.** *The novelty needs to be sharpened and better positioned. The longitudinal multi-cycle framing overlaps with prior work (e.g., Sekar et al.; the Mitra/Chu/Cetin line), so the authors should make explicit what their occupant behavior characterization adds beyond existing ATUS-based studies, particularly any distinctive OB patterns captured here (a cross-comparison with prior work, even on a qualitative level, would be interesting).*

**Response.** We removed every "first" claim and now state the novelty as a specific combination (Section 1.3): Canadian GSS, four harmonised cycles across the COVID-19 break (2005–2022), household-level schedules assembled from individual diaries, and a projection beyond the last cycle that is tested against a held-out census. Table 1 shows where the ATUS-based studies of Sekar et al. and of Mitra, Chu and Cetin stand on each of these points. A new Discussion subsection (5.1) compares our findings qualitatively with the US and Japanese longitudinal findings (Table 12): presence in Canada did not rise between 2005 and 2015, unlike the rise in time at home reported for the United States between 2003 and 2012; the 2022 cycle departs from all earlier cycles, with more presence during weekday working hours and a smaller weekday–weekend difference, in line with the post-pandemic change reported for Japan; and the gap between the standard (Default) schedule and every Canadian cycle is one of timing rather than of daily totals. These patterns can only be seen across several cycles. We also added a paragraph that separates this paper from the authors' companion study on stock-scale electricity load shapes, which uses the same data pipeline for a different question (Section 1.3).

Location: Sections 1.3 and 5.1, Tables 1 and 12.

**Comment 4.** *The EnergyPlus simulation component, in its current form, adds little discernible novelty and its purpose within the contribution is unclear; the authors should either clarify what it contributes beyond standard schedule integration or de-emphasize it. The generative C-VAE/CBVM projection is the strongest point of differentiation but is also the least validated, and the contribution should be repositioned around the longitudinal-plus-projective OB pipeline rather than implying a new modeling paradigm.*

**Response.** We agree on both points.

*Validation of the projection.* The submitted paper supported the projection with a qualitative figure only. We now test it quantitatively (Sections 3.3 and 4.2). The C-VAE was retrained on the 2006, 2011 and 2016 censuses only, the cluster-based drift model was fitted to those years, and the 2016 population was projected to 2021 and compared with the held-out 2021 Census on every generated variable (total-variation distance for categorical variables, Wasserstein distance for continuous ones). Three baselines were scored the same way: carrying 2016 forward, linear extrapolation of the 2011–2016 change, and a population-mean drift. The pass rule was fixed before the hindcast was run: the method must beat carry-forward on more than half of the variables, averaged over five random seeds. [[WP4: result and verdict, stated as measured]]. We also report the sensitivity to the number of clusters, the decay factor and the latent size, and the spread over five seeds (Appendix A). The matching step is now documented with all four tier shares (Section 3.4).

*Purpose of EnergyPlus.* The simulations now serve one stated purpose (Sections 1.3 and 4.3): to show whether the cycle-to-cycle occupancy differences, and the projection, are large enough to change simulated heating and cooling, under fixed buildings and a fixed weather file. Section 4.3 was shortened to one figure and two tables with confidence intervals; the tornado chart, the monthly stacks, the weekday–weekend chart and the "energy fingerprint" radar charts were removed, and the term "neighbourhood energy fingerprint" is no longer used. The building-code correction factors (+10 % heating, −20 % cooling) and the 18 % cooling-oversizing estimate were removed: they came from one city, one weather file and a few archetypes, and the corrected simulations no longer support them. Objective 2 no longer mentions "Canadian climate zones", as only Montreal was simulated. The paper is now framed as a longitudinal-plus-projective occupant-behaviour pipeline and makes no claim of a new modelling paradigm.

Location: Sections 1.3, 3.3, 4.2, 4.3, 5.2, Appendix A.

## Other changes

- The explanation of the low 2010 occupancy by the weighting of the 2011 National Household Survey was removed: the 2010 GSS was collected before the NHS. In the rebuilt files the 2010 cycle is only about 0.5 h per weekday below 2005 and 2015 (the submitted 11.9 h came from the faulty files), and we state that the cause of this small difference was not identified (Section 4.1.1).
- The Default daytime occupancy was quoted three different ways; the paper now gives one value for each defined quantity: Default daytime fraction 0.26, Default mean occupancy 0.68, Default occupied hours 16.4 h (Section 4.1.3, Table 8).
- The strong decline of presence with household size reported in the submitted version came from the earlier files, whose occupancy fraction was divided by the full household size including members without a diary; under the corrected definition household size has little effect, and Section 4.1.4 says so.
- The heating mechanism is now stated consistently with the results: relative to the Default, the survey-based schedules lower equipment, lighting and hot-water use and the night-time metabolic gains, which raises heating and lowers cooling; the 2022 schedules, with the most daytime presence, depart least from the Default (Section 4.3).
- Children under 15 have no diary; the paper now states that they are not counted in the occupancy fraction (Sections 2.2, 3.4 and 5.3).
- All four matching-tier shares are now reported for every cycle (Table 5).
- The household selection text described a filter (single-detached households of 2 to 4 persons) that the simulation code did not apply. In the new runs every building receives a household of its own dwelling type, and the text says so (Section 3.6).
- The submitted text described the buildings as DOE/ASHRAE 90.1 prototype archetypes. The simulated models share one high-performance envelope (wall U ≈ 0.14 W/m²K, roof U ≈ 0.07 W/m²K, low-e double glazing) with ideal-loads air systems; only the Default schedules come from the DOE MidriseApartment prototype. Section 3.6 now describes the buildings as simulated, and states that one apartment Default schedule is used for every building and what that implies for the house results.
- The presence-filter equation is now typeset correctly (Section 3.6).
- The 2025 cohort size was given as 323 households; the correct number is 23,882 households.
- A duplicated sentence in the former Section 4.1.3 was removed.
- Neighbourhood-unit labels: in the submitted text the heating intensities of RC-R and RC-MR2 were swapped; corrected.
- The weather file's period of record is 1994–2023 (TMYx), not 2009–2023.
- Limitations are now stated together in Section 5.3, including the removal of census persons whose age was not available, households with conflicting dwelling-type labels, children under 15 without a diary, and the precision reached by the 30-draw limit.
- The references were checked and completed.

We hope that the revised manuscript addresses the reviewer's concerns.
