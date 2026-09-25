# Reference check: 4 missing citations (3J, Building and Environment)
Checked 2026-09-25. Every field below was read from a live record (URL given). Nothing was filled in from memory.

---------------------------------------------------------------------
## GAP 1. How overlapping use times affect district and grid peaks

### Recommended (A): the best direct match, but it is a conference paper
Vecchi, F. and Berardi, U. (2024) Mixed-use neighbourhood to maximise urban energy community potential. E3S Web of Conferences, 523, 05002. https://doi.org/10.1051/e3sconf/202452305002
- Grade: VERIFIED (abstract read). It is peer-reviewed conference proceedings (AICARR 2024), not a journal article. I could not open the full PDF (the site returned 403).
- Fields: https://api.crossref.org/works/10.1051/e3sconf/202452305002 (authors Vecchi and Berardi; "Noro" and "Zilio" are the volume EDITORS, so leave them out); abstract from https://api.openalex.org/works/doi:10.1051/e3sconf/202452305002
- Support: "Residential users prevail in urban areas while planning mixed-use neighbourhoods would contribute to having complementary loads towards urban RECs. Mixed areas can optimise the use of renewable production at different hours and limit demand pressures on the network." ... "The integration of building functions flattens the energy peak loads in the district while increasing the use of PV production."

### Recommended (B): journal article with open full text. It covers the district-peak mechanism, not mixing of uses
Weissmann, C., Hong, T. and Graubner, C.-A. (2017) Analysis of heating load diversity in German residential districts and implications for the application in district heating systems. Energy and Buildings, 139, 302-313. https://doi.org/10.1016/j.enbuild.2016.12.096
- Grade: VERIFIED (abstract and full accepted manuscript read, via OSTI 1532235 -> https://escholarship.org/content/qt7wx3g3xv/qt7wx3g3xv.pdf)
- Fields: https://api.crossref.org/works/10.1016/j.enbuild.2016.12.096
- Support (abstract): "Central supply systems can be very efficient due to diverse energy demand profiles which may lead to reduced installed equipment capacity."
- Support (full text, sect. 3): "In Fig. 6 the user profile related interval borders reveal that PLR increases if buildings with a different user profile are added to the district". PLR here means diversity, i.e. a lower district peak.
- Limits: the study covers residential heating only, not electricity, and does not mix commercial with residential uses.

### Checked, weaker fit
- Doma, A., Padsala, R., Ouf, M.M. and Eicker, U. (2024) Applied Energy 375, 124081, https://doi.org/10.1016/j.apenergy.2024.124081 (Crossref + OpenAlex abstract). The abstract covers occupancy-based demand-side management in a Montreal mixed-use district and says "to ensure the stability and reliability of the utility grid ... estimated reduction in district peak demand by up to 17%". It links occupancy to district peak and grid, but it does not claim that mixing uses changes the peak. It is PARTIAL support. It can sit next to (A) but cannot replace it.
- Hachem-Vermette, C. and Singh, K. (2019) Energy and Buildings 204, 109499, https://doi.org/10.1016/j.enbuild.2019.109499 (Crossref; abstract via Semantic Scholar API). The abstract says it optimizes the "residential and commercial buildings mixture" and "Optimizing the hourly energy load profile". It never says peak or grid. PARTIAL. Note that the supervisor is an author.
- REJECT for this sentence: Zhao et al. 2024 Energies 17(5) 1214 (peak reduction comes from retrofits and PV, not from mixing uses). Singh & Hachem-Vermette 2019 B&E 154 and Hachem-Vermette & Grewal 2019 AE 241 (no peak or grid content in the abstracts). Kang et al. 2024 SCS 115 105822 (abstract not readable). Zhang et al. 2026 SCS 143 107348 (about electrification peaks, not mixing uses).

---------------------------------------------------------------------
## GAP 2. Standard definition of the coincidence factor

### Recommended: open full text that gives the formula exactly
Weissmann, C., Hong, T. and Graubner, C.-A. (2017) [same as GAP 1-B] Energy and Buildings, 139, 302-313. https://doi.org/10.1016/j.enbuild.2016.12.096
- Grade: VERIFIED (full accepted manuscript read: https://escholarship.org/content/qt7wx3g3xv/qt7wx3g3xv.pdf, linked from https://www.osti.gov/biblio/1532235)
- Definition quoted (sect. 1.1): Guan et al. "define a 'coincidence factor' which is the total maximum load of the campus divided by the sum of the individual building load maxima."
- Equations (sect. 1.2): Q_AIS = sum_i Q_max,i (Eq. 1); Q_D(n),t = sum_i Q_i,t (Eq. 2); Q_CS = Max(Q_D(n),t) (Eq. 3); PLR = (Q_AIS - Q_CS)/Q_AIS (Eq. 4). So CF = Q_CS/Q_AIS = max_t(sum_c P_c(t)) / sum_c max_t P_c(t) = 1 - PLR. The paper also quotes the reciprocal "diversity factor" definition.

### Primary source for that definition (its text not seen directly)
Guan, J., Nord, N. and Chen, S. (2016) Energy planning of university campus building complex: Energy usage and coincidental analysis of individual buildings with a case study. Energy and Buildings, 124, 99-111. https://doi.org/10.1016/j.enbuild.2016.04.051
- Grade: METADATA-ONLY. Crossref confirms it exists (https://api.crossref.org/works?query.bibliographic=...coincidental+analysis). An accepted manuscript sits on NTNU Open / NVA (hdl 11250/2457605), but the download returned "Forbidden". Its definition is known only through Weissmann's quote above.
- Suggested wording: "... coincidence factor (Guan et al., 2016; Weissmann et al., 2017)".

### Rejected
- Gunkel et al. (arXiv 2210.03524): full text read. It defines CF as "the probability of simultaneous charging", which is a different definition.
- Energies 15(4) 1383 (2022) and WEVJ 13(7) 129 (2022) exist (OpenAlex), but MDPI blocked the full text (403). I did not use them.

---------------------------------------------------------------------
## GAP 3. Tall and SuperTall prototype models: who released them, and which version

Main finding: DOE/PNNL did NOT publish these prototypes on energycodes.gov. On 2026-09-25 the page https://www.energycodes.gov/prototype-building-models lists 16 commercial types ("in EnergyPlus Version 22.1.0"). No Tall or SuperTall model appears there (grep for "tall" found nothing). The "Release March 2023" claim cannot be supported from that page.

The models come from NREL's OpenStudio-Standards gem, and the Tall/SuperTall types were written by LBNL:
- Repo tree: data/geometry/ASHRAETallBuilding.json, ASHRAESuperTallBuilding.json, lib/openstudio-standards/prototypes/common/buildings/Prototype.TallBuilding.rb and Prototype.SuperTallBuilding.rb, docs/scorecards/Scorecard_TallandSuperTallBuildings.xlsx (https://api.github.com/repositories/15783073/git/trees/master?recursive=1). github.com/NREL/openstudio-standards now redirects (301) to github.com/NatLabRockies/openstudio-standards.
- Commit history (GitHub API): "Initially add tall building and super tall building prototype model." on 2020-07-21, then "Added the SuperTall building prototype model. Added scorecards of tall and supertall buildings." on 2020-09-03. Author Kaiyu Sun (ksun@lbl.gov).
- The scorecard (creator Kaiyu Sun, last modified 2020-09-02) says: "LBNL is developing a prototype energy model to support the evaluation of energy efficiency for mixed-use tall buildings." and "This is the initial version of the model specification, intended for review and obtaining feedback from stakeholders."
- The repo IDFs match the gem's naming. The IDF Building name is "-SuperTallBuilding-ASHRAE 169-2013-6A created: 2026-04-17 12:02:49 -0400". The gem's Prototype.Model.rb line 48 is `setName("-#{@instvarbuilding_type}-#{climate_zone} created: #{Time.new}")`. So the IDFs were generated locally with the gem on 2026-04-17, not downloaded from DOE.
- The gem release version is NOT recorded in the IDF, so I cannot confirm it. The IDF says EnergyPlus 22.1 (Version object). The gem has no journal paper or DOI (DOE CODE search found nothing). The latest release seen is v0.8.6 (2026-03-24).

Recommended citation (Grade: VERIFIED as software/source; no DOI exists):
National Renewable Energy Laboratory (2026) OpenStudio-Standards [Ruby gem], TallBuilding and SuperTallBuilding prototypes (developed by Lawrence Berkeley National Laboratory, 2020), ASHRAE 90.1-2019 template. Available at: https://github.com/NREL/openstudio-standards (Accessed: 17 April 2026).
- Author action: add the exact gem version used on 2026-04-17 (for example from `gem list openstudio-standards` or the OpenStudio version). Also change "U.S. DOE and PNNL" in the reference to NREL OpenStudio-Standards / LBNL.

Optional supporting report for the prototype method in general (not specific to Tall buildings):
Goel, S., Athalye, R., Wang, W., Zhang, J., Rosenberg, M., Xie, Y., Hart, P. and Mendon, V. (2014) Enhancements to ASHRAE Standard 90.1 Prototype Building Models. PNNL-23269. Richland, WA: Pacific Northwest National Laboratory. https://doi.org/10.2172/1129366
- Grade: METADATA-ONLY (report number from OSTI record 1129366; authors and title from https://api.crossref.org/works/10.2172/1129366). The Tall/SuperTall scorecard lists it as a reference.

---------------------------------------------------------------------
## GAP 4. Which SCIEU year the context ranges come from

Source: NRCan, Survey of Commercial and Institutional Energy Use (SCIEU), data tables (from Statistics Canada's survey). Conversion used: 1 GJ/m2 = 277.8 kWh/m2.

2019, Table 1 (https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=1&page=1):
- Office space, excluding medical: 1.05 GJ/m2 = 292 kWh/m2
- Retail, non-food: 1.01 GJ/m2 = 281 kWh/m2  <- matches 280
- Hotel, motel, hostel or lodge: 1.28 GJ/m2 = 356 kWh/m2  <- about 350 (1.7% off)
2019, Table 17.1 (by activity and size, rn=31): office excluding medical, over 18,580 m2: 0.83 GJ/m2 = 231 kWh/m2  <- matches 230
2019, Table 19 (by activity and floors, rn=35): office excluding medical, 10 or more floors: 0.82 GJ/m2 = 228 kWh/m2  <- matches 230

2014, Table 1 (…year=2014&rn=1): office (non-medical) 1.13 = 314; non-food retail 1.12 = 311; hotels 1.24 = 344.
2014, Table 17 (rn=17): office over 18,580 m2 = 1.09 = 303.

Verdict: the central values match SCIEU 2019. Office 230 is the 2019 large or tall office subset (Table 17.1 or 19), not the all-office mean of 292. Retail 280 and hotel 350 are the 2019 all-building means (Table 1). 2014 does not match office (303-314) or retail (311). Hotel alone could fit either year (344 vs 356).
The low-high bands (170-360, 150-380, 220-480) do NOT appear in any Table 1, 17.1 or 19 value I read. Their source is still unknown.
- Note: the 2019 page says the 2019 data are "not comparable with earlier published SCIEU data for 2009 and 2014".
- Code comment (…/Leg2_2-split/Step8_docs/archive/…preV3plot.py:1405) already says "SCIEU-2019/CEUD-2023 large & high-rise office", which agrees with the office match.

Recommended citation (Grade: VERIFIED, values read from the live tables):
Natural Resources Canada (2023) Survey of Commercial and Institutional Energy Use (SCIEU) - Buildings 2019: Data Tables. Ottawa: Office of Energy Efficiency. Available at: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm (Accessed: 25 September 2026).
- The page says the tables include "revisions to the Establishment data published in August 2023". I did not see a separate first-release date, so "2023" rests on that sentence.
- Suggested manuscript wording: "(SCIEU 2019; office value for buildings over 18,580 m2)".
