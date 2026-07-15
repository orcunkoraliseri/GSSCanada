# 2 Datasets

The dataset inventory is summarized in Table 2; the preprocessing path from raw microdata to analysis-ready diaries is shown in Figure 2.

---

### 2.1 General Social Survey Time-Use Microdata (2005–2022)

The behavioural backbone of the analysis is four cross-sectional waves of the Statistics Canada General Social Survey (GSS) Time-Use program: Cycle 19 (2005), Cycle 24 (2010), Cycle 29 (2015), and the GSS Time Use 2022 cycle (GSSP) (Statistics Canada, 2022). Each respondent contributes a full 24-hour episode diary recording primary activity, co-presence, and location at fine temporal resolution. Time-use surveys are an established basis for deriving occupant presence and activity schedules in building performance simulation (Osman and Ouf, 2021; Wilke et al., 2011). After applying a 1,440-minute diary-closure filter — retaining only records whose episode durations sum to exactly one day — the analysis corpus comprises 64,061 valid respondent-diaries: 19,221 (2005), 15,114 (2010), 17,390 (2015), and 12,336 (2022). The closure-filter exclusion rate is negligible in all cycles (1.92 %, 1.79 %, 0.00 %, and 0.00 % respectively), indicating near-complete diary recording (Table 2). Population-weighted at-home fractions computed from the diary data are 62.7 % (2005), 62.3 % (2010), 64.5 % (2015), and 70.6 % (2022). The +6.1 pp jump at 2022 relative to 2015 is the COVID-19 and work-from-home behavioural signature; it is the primary non-stationarity the paper traces into residential load shape (§5.1).

Two cross-cycle design constraints shape the harmonization and modelling strategy. First, SURVMNTH (survey month) is absent for the 2005 and 2010 cycles; the temporal denominator therefore collapses to three day-type strata — Weekday, Saturday, Sunday — applied uniformly across all four cycles (§3.1). Second, TUI_10 (subjective episode-level well-being) was not collected in 2005 or 2010 and is available only for 2015 and 2022; it is used as an auxiliary signal for those two cycles only and is excluded from cross-cycle model inputs. Collection mode evolved across the series: the 2005 and 2010 cycles were conducted entirely by Computer-Assisted Telephone Interviewing (CATI) on a random-digit-dial frame, whereas the 2015 and 2022 cycles used a multi-mode design that added a self-administered electronic questionnaire (EQ, administered online) alongside CATI, with electronic self-administration becoming the predominant channel by the 2022 GSSP redesign. This progressive shift toward self-administration constitutes a potential measurement break that is absorbed by the harmonization protocol and addressed explicitly via a per-cycle COLLECT_MODE conditioning feature in the generative model (§3.2) — a binary indicator that marks the predominant-mode transition at 2022; its residual risk is examined in the Limitations section (§7). Each respondent contributes exactly one observed day-type, with the other two synthesized by the Step-4 generator (§3.2) — this is the methodological justification for the generative augmentation step. Raw activity codes are harmonized to a common 14-category occACT scheme aligned with the Eurostat (2018) HETUS guidelines, mapping 182, 264, 64, and 121 raw cycle-specific codes respectively, with zero coding conflicts and 0.00 % unmapped episodes in every cycle (SI Table B2). Co-presence is OR-merged from raw episode columns into nine unified channels; the `colleagues` channel was not collected in 2005 or 2010 and is masked for those cycles in the generator.

**Table 2.** *(insert `Table_02_gss_cycles.md` here)* — Per-cycle valid-diary counts, DIARY_VALID closure-filter exclusion rate, population-weighted at-home fraction, collection mode (CATI-only for 2005/2010 vs multi-mode CATI + electronic questionnaire for 2015/2022), and TUI_10 availability across the four GSS Time-Use cycles, with column totals.

**Figure 2.** *(insert `Figure_02_dataprep.png` here)* — **Dataset preprocessing and harmonization flow.** Raw GSS Main and Episode files across the four cycles pass through the 1,440-minute closure filter and cross-cycle schema harmonization to the common 14-category activity scheme, episode-to-HETUS 144×10-min tiling, and presence-priority majority-vote downsampling to the analysis-ready 48×30-min diary, with the mandatory 04:00→00:00 clock convention; the Census PUMF enters separately at the Step-5 linkage and bypasses diary preprocessing.

---

### 2.2 Census Public-Use Microdata for Dwelling-Stock Linkage

The Statistics Canada Census Public-Use Microdata File (PUMF), 2021 edition — supplemented by the 2006, 2011, and 2016 cycles for contextual continuity — provides the dwelling-stock variables required to situate diary respondents within a representative building population (Statistics Canada, 2021; 2012). The relevant variables include period of construction, dwelling type, number of bedrooms and rooms, condominium status, repair status, and assessed value. These attributes are not available in the GSS time-use files and cannot be inferred from diary data alone. The Census PUMF enters the pipeline exclusively at the Step-5 probabilistic Census–GSS linkage (§3.3), which maps 286,537 individuals onto the building stock and, after a plausibility-exclusion gate, yields the final 144,507-household building energy model (BEM) frame used in all downstream simulations. The Census PUMF bypasses diary preprocessing entirely (Figure 2) and does not contribute to the activity harmonization or generative modelling stages.

---

### 2.3 NRCan SHEU End-Use Calibration Reference

The NRCan Survey of Household Energy Use (SHEU 2019) serves as the external end-use calibration anchor for the activity-resolved load model (§3.6 and §5.4) (Natural Resources Canada, 2019). SHEU provides independently measured annual electricity consumption disaggregated by end-use category and dwelling type, making it the appropriate benchmark against which the simulated equipment and lighting channels are validated. The per-dwelling annual equipment (plug-load) targets used in calibration are: SingleDetached 3,700 kWh, OtherDwelling (attached) 3,139 kWh, MidRise 2,166 kWh, and HighRise 1,922 kWh. The corresponding annual lighting targets are: SingleDetached 1,262 kWh, OtherDwelling 1,100 kWh, MidRise 736 kWh, and HighRise 736 kWh. These targets define the per-end-use scalars that constrain each archetype's simulated annual energy to the survey benchmark; the validation outcome is reported in §5.4.

---

### 2.4 Weather Files and Building Archetypes

The simulation domain spans six Canadian cities selected to cover the principal ASHRAE climate zones of the inhabited Canadian stock (5A through 7A): Toronto (5A), Kelowna (5B), Vancouver (5C), Montréal (6A), Calgary (6B), and Winnipeg (7A). Typical Meteorological Year (TMY) EnergyPlus weather files (EPW) are used for each city, and the building stock is represented by four Canadian code-compliant residential archetypes — SingleDetached, OtherDwelling (attached), MidRise, and HighRise — developed under NECB 2017 and NBC 9.36 Zone-6 envelope assumptions (National Research Council Canada, 2017; 2020); these are Canadian code archetypes, not US DOE prototype buildings. All simulations are executed in EnergyPlus v24.2 (U.S. Department of Energy, 2024). The full 4 × 6 archetype-by-city matrix, the weather file specifications, and the held-versus-varied factorial design are defined in the Experimental Design section (§4, Tables 3–4); this subsection inventories the inputs only.

---

## References (this chapter)

*Verified from the authors' prior publications (1st_Occ_Journal, ConferencePaper); to be merged into the manuscript master bibliography.*

- Osman, M. and Ouf, M. (2021) "A comprehensive review of time use surveys in modelling occupant presence and behavior: Data, methods, and applications," *Building and Environment*, 196, 107785. https://doi.org/10.1016/j.buildenv.2021.107785.
- Statistics Canada (2012) *2011 National Household Survey*. https://www12.statcan.gc.ca/nhs-enm/index-eng.cfm (accessed 15 February 2026).
- Statistics Canada (2021) *Census of Population, 2021: Public Use Microdata Files* (Series Catalogue no. 98M0001X). Individuals File: 98M0001X2021001 (released 12 September 2023); Hierarchical File: 98M0001X2021002 (released 20 March 2024). https://www150.statcan.gc.ca/n1/en/catalogue/98M0001X (accessed 15 February 2026).
- Statistics Canada (2022) *General Social Survey – Time Use: Public Use Microdata Files* (Series Catalogue no. 45-25-0001; series DOI https://doi.org/10.25318/45250001-eng). Individual cycles: 12M0019X (Cycle 19, 2005), 12M0024X (Cycle 24, 2010), 89M0034X (Cycle 29, 2015), and 45-25-0001 issue 2025001 (Time Use, 2022). https://www150.statcan.gc.ca/n1/pub/45-25-0001/index-eng.htm (accessed 15 February 2026).
- Wilke, U., Haldi, F. and Robinson, D. (2011) "A model of occupants' activities based on time use survey data," *Proceedings of Building Simulation 2011 (IBPSA)*.

**Standards, codes, and data sources** *(web-verified June 2026):*

- Eurostat (2018) *Harmonised European Time Use Surveys (HETUS): 2018 Guidelines*. Luxembourg: Publications Office of the European Union (KS-GQ-19-003; re-edition 2020, KS-GQ-20-011). https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/ks-gq-19-003.
- National Research Council Canada (2017) *National Energy Code of Canada for Buildings 2017*, Fourth Edition. Ottawa: Canadian Commission on Building and Fire Codes (Cat. NR24-24/2017E-PDF; ISBN 0-660-24321-4; https://doi.org/10.4224/40002011). https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-energy-code-canada-buildings-2017.
- National Research Council Canada (2020) *National Building Code of Canada 2020*, Division B, Section 9.36 (Energy Efficiency), Fifteenth Edition. Ottawa: Canadian Commission on Building and Fire Codes (Cat. NR24-28/2020E-PDF; ISBN 978-0-660-37912-8; https://doi.org/10.4224/w324-hv93). https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications.
- Natural Resources Canada (2019) *Survey of Household Energy Use (SHEU), 2019* — Data Tables. Office of Energy Efficiency, Natural Resources Canada (comparative energy-intensity series: CODR table 25-10-0061-01). https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm (accessed 10 June 2026).
- U.S. Department of Energy (2024) *EnergyPlus™ (Version 24.2.0)*. National Renewable Energy Laboratory (NREL). https://energyplus.net/.
