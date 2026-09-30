# dr_1J-09: reference and claim check for the revised manuscript (run in Gemini; paste the whole file)

You are checking the reference list of a revised journal manuscript. You are NOT asked to find new literature.
For each numbered item below, open the publisher page or the DOI record (https://api.crossref.org/works/<DOI>) and, where a
claim is listed, the full text. Report only what you actually read.

Rules:
1. Open the source before reporting anything about it. If you could not open it, write NOT OPENED.
2. Resolve every DOI through Crossref and report the title, the full author list, the journal, the year, the volume, the issue
   and the pages exactly as the Crossref record gives them.
3. For each claim, answer SUPPORTED, NOT SUPPORTED or NOT FOUND, and copy the exact sentence from the paper that supports it, with
   the page or section. "NOT FOUND" is a good answer; an invented or paraphrased quote is a failure.
4. Do not use em dashes or en dashes anywhere in your answer. Use commas or the word "to".
5. Do not read or use any file on the user's disk.
6. Control item: item 0 is a paper whose details are known. If your item 0 answer differs from the Crossref record, say so.

Return one table with columns: item | DOI resolves (yes/no) | Crossref title | Crossref authors | journal, year, volume, issue, pages | claim verdict | exact supporting sentence and page.

## Items

0. (control) DOI 10.1016/j.enbuild.2008.02.006. No claim.
1. DOI 10.1016/j.joule.2018.01.003 (Sekar, Williams and Chen, Joule, 2018). Claim: comparing the American Time Use Survey
   2003 with 2012, Americans spent more time at home in 2012, and less time travelling and in non-residential buildings.
2. DOI 10.1016/j.enpol.2018.09.025 (Anderson and Torriti, Energy Policy, 2018). Claim: uses four UK time-use surveys from 1974
   to 2014 to explain shifts in the timing of residential electricity demand.
3. DOI 10.1177/23998083241280385 (Dias dos Santos, Moghadasi and Paez, Environment and Planning B). Claims: (a) it harmonises
   seven cycles of the Canadian General Social Survey time-use data from 1986 to 2015; (b) it does or does not project time use
   beyond the last survey; (c) it does or does not run a building energy simulation.
4. DOI 10.1016/j.buildenv.2023.110490 (Osman et al., Building and Environment 241, 2023). Claim: builds occupancy models from
   the 2015 Canadian General Social Survey time-use data.
5. DOI 10.1016/j.enbuild.2019.109713 (Mitra, Steinmetz, Chu and Cetin, Energy and Buildings 210, 2020). Claims: (a) derives
   residential occupancy profiles from several years of the American Time Use Survey; (b) reports weekend presence at home
   higher than weekday presence.
6. DOI 10.1016/j.enbuild.2021.110791 (Mitra, Chu and Cetin, Energy and Buildings 236, 2021). Claim: pools several American Time
   Use Survey years into one sample.
7. DOI 10.1016/j.apenergy.2022.119890 (Chen et al., Applied Energy 325, 2022). Claim: pools American Time Use Survey years and
   couples the schedules to a building stock energy model.
8. DOI 10.1016/j.trc.2019.07.006 (Borysov, Rich and Pereira, Transportation Research Part C 106, 2019). No claim; metadata only.
9. DOI 10.1007/s00521-021-06622-2 (Johnsen et al., Neural Computing and Applications). Claim: uses an empirical distribution
   table built from the training set as a baseline for a conditional generative population model.
10. DOI 10.1080/19401493.2025.2465508 (Sood et al., Journal of Building Performance Simulation, 2025). Metadata only: volume,
    issue, pages.
11. DOI 10.1177/1420326X251396163 (Duan, He and Yu, Indoor and Built Environment). Metadata only.
12. DOI 10.1016/j.egyr.2025.11.021 (Energy Reports 14, 2025, "Designing energy-positive neighborhoods"). Metadata only: the
    exact author list.
13. ASim2024 conference paper "Long-Term Changes in Time Use and Impacts on Residential Energy Demand" (Yin, Yamaguchi, Zajch,
    Uchida and Shimoda, pages 1321 to 1328). Does it have a DOI? Report it if the IBPSA or conference record shows one.
14. Statistics Canada: the exact title and catalogue number of (a) the 2011 National Household Survey User Guide, (b) the
    General Social Survey Cycle 19 (2005) Time Use public use microdata file user guide (catalogue 12M0019GPE), (c) the General
    Social Survey Cycle 29 (2015) Time Use public use microdata file user guide. Also: the NHS 2011 unweighted response rate
    stated in (a).
15. The U.S. Department of Energy / PNNL prototype building models page (energycodes.gov): the current URL for the residential
    (IECC) and the commercial (ASHRAE 90.1) prototype models.
