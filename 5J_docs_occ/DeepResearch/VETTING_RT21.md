# Vetting RT21: open_home_sensor_occupancy_datasets

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Worse than RT19 on citations.** 8 of 10 author lists are wrong. Three DOIs, for ECO, ARAS and Building Data Genome 2, point to a different paper that shares only the title.
2. **The headline count is unsupported.** Section A's "under 1,200 home-days of ground truth worldwide" rests on:
   - ECO at "80 days per house", when its own cited abstract says about 8 months (N2);
   - ARAS at "30 days", when outside summaries say two months (N3);
   - SPHERE at "about 100 homes", with no row, URL or citation anywhere.
   The HUE dataset has 22 houses, not 42, and comes from Simon Fraser University, not UBC.
3. **Item 1 registry: 7 named sources silently dropped.** These are SPHERE, Smart*, Pecan Street, IEA Annex 79, LBNL, Canadian test houses, and Horizon projects. The "household composition known" column is missing from every row, and so are the roles R1 to R4. Two of the three licence quotes that could be checked are not on their pages (ECO, CASAS).
4. **Batch finding.** The tool wrote this report with a text-writing script, and its logs show no page fetch for it.
5. **What survives, checked here:**
   - REFIT: 20 UK homes, 2 years, 8-second data, CC BY 4.0. The authors are Murray, Stankovic and Stankovic, 2017.
   - IDEAL: 255 UK homes over 23 months, CC BY 4.0. It has no occupancy ground truth in its abstract.
   - UK-DALE (Kelly and Knottenbelt 2015): CC BY 4.0.
   - ECO: 6 Swiss households over 8 months, with occupancy files for 5 (Kleiminger et al. 2013, above 80 % accuracy).
   - Turley et al. 2020: 6 Colorado homes, 5.0 % HVAC saving.
   - CASAS: 21 or more testbeds.
   - The correct ARAS DOI is 10.4108/icst.pervasivehealth.2013.252120.

**What this means for the sensor-dataset form (A14, role R3 validate):** open, and smaller than it looks. Open home datasets with ground-truth presence number only a handful of homes, so they can check a schedule model's shape, not score a population. The exact home-day total is unknown.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 10 (match 2, wrong author lists 8, not resolved 0, of which 3 are entirely the
wrong paper under a matching title); use claims 4 (supported 1 full + 2 partial, not in abstract 1,
no abstract 1); URLs 8 (opened 5, blocked/unreachable 2, wrong link 404 1); quoted strings 3 checked
(found 2, not found 1); numeric facts 7 (confirmed 3, contradicted 3, not confirmed 1); prompt items
4 core items answered but registry (item 1) has 8 of at least 15 named sources dropped, including
SPHERE which Section A itself relies on; dashes em 0, en 0.

## 1. DOIs

All 10 unique DOIs resolved at CrossRef with HTTP 200. Table below: report's claimed author/year/venue
vs CrossRef's actual record for the same DOI.

| # | DOI | Report claims | CrossRef actual | Verdict |
|---|---|---|---|---|
| 1 | 10.1145/2602044.2602056 | Beckel, Sadamori, Staake, Santini (2014), "Windy with a chance of profit", cited as the ECO dataset source | Kurandwad, Subramanian, P, Vasan, Sarangan, Chellaboina, Sivasubramaniam (2014), "Windy with a chance of profit", *Proceedings of the 5th international conference on Future energy systems* (e-Energy), pp.39-49 | WRONG PAPER. Title happens to match but every author is different, the venue is different, and the real subject (weather-based demand response) has nothing to do with ECO or occupancy. "Sadamori" appears on no version of this paper. |
| 2 | 10.1145/3264996.3265001 | Alemdar et al. (2013), "Activity Recognition in New Smart Home Environments", cited as the ARAS dataset source | Wang, Miao (2018), same title, *Proc. 3rd Intl Workshop on Multimedia for Personal Health and Health Care*, pp.29-37 | WRONG PAPER. Title coincidence again; real first author is Wang, real year is 2018, not Alemdar/2013. The genuine ARAS paper (Alemdar, Durmaz Incel, Ertan, Ersoy, 2013, "ARAS Human Activity Datasets in Multiple Homes with Multiple Residents") has DOI 10.4108/icst.pervasivehealth.2013.252120, confirmed at CrossRef, and is not the DOI the report used anywhere. |
| 3 | 10.1038/sdata.2016.122 | Firth, Kane, Dimitriou, Hassan, Coleman (2016), REFIT | Murray, Stankovic, Stankovic (2017), same title | AUTHOR + YEAR MISMATCH. This is the real REFIT data descriptor, but authored by Murray/Stankovic/Stankovic, published 2017 (online 2016, but CrossRef issued date is 2017); "Firth" et al. do not appear as authors. |
| 4 | 10.1038/sdata.2015.7 | Kelly, Knottenbelt (2015), UK-DALE | Kelly, Knottenbelt (2015), same title | MATCH |
| 5 | 10.1088/1742-6596/2600/3/032003 | Miller et al. (2020), cited as "Building Data Genome 2" (1,636 non-residential buildings) | Jin, Fu, Kazmi, Balint, Canaydin, Quintana, Biljecki, Xiao, Miller (2023), "The Building Data Genome Directory", *J. Phys. Conf. Ser.* | WRONG PAPER. This is a 2023 paper about the "Building Data Genome Directory" (a 60-dataset discovery portal), not the "Building Data Genome 2" (BDG2) energy-meter dataset paper by Miller et al. (2020, *Scientific Data*), which has a different DOI never used in this report. Miller is present only as the last of nine authors, not first. |
| 6 | 10.1038/s41597-021-00921-y | Pullinger, Kilgour, Goddard, ... Shipworth (2021), IDEAL | Pullinger, Kilgour, Goddard, Berliner, Webb, Dzikovska, Lovell, Mann, Sutton, Webb, Zhong (2021), same title | AUTHOR MISMATCH: "Shipworth" is not in the CrossRef author list; year and title match. |
| 7 | 10.1038/s41597-022-01475-3 | Dong, Liu, Mu, Shen, ... Yan (2022), ASHRAE Global Occupant Behavior Database | Dong, Liu, Mu, Jiang, Pandey, ... Yan (2022), same title | AUTHOR MISMATCH: "Shen, X." is invented; third author is Jiang, not Shen. |
| 8 | 10.1016/j.buildenv.2017.05.005 | Li, Dong, Xiao (2017) | Li, Dong (2017), same title, pp.277-290 | AUTHOR MISMATCH: only two real authors (Li, Dong); "Xiao, J." invented. Page range also off by one (report: 276-290, CrossRef: 277-290). |
| 9 | 10.3390/en13205396 | Turley, Thurston, Zhang (2020) | Turley, Jacoby, Pavlak, Henze (2020), same title | AUTHOR MISMATCH: co-authors entirely wrong; real co-authors are Jacoby, Pavlak, Henze. |
| 10 | 10.1145/2528282.2528295 | Kleiminger, Beckel, Staake, Santini (2013) | Kleiminger, Beckel, Staake, Santini (2013), same title | MATCH |

**Count of wrong author lists: 8 of 10.** Three of those eight (rows 1, 2, 5) are not just wrong
author lists but a completely different paper attached to the DOI, sharing only a coincidental or
near title match. This matches the pattern flagged for RT19.

## 2. Use claims (Section C, L01-L04)

| Row | Claim | Abstract check | Verdict |
|---|---|---|---|
| L01 | Dong et al. (2022): "Measured presence exhibits 35% to 55% higher diversity than static code schedules across zones", compared against "ASHRAE 90.1, EN 16798-1" | OpenAlex abstract describes the database (34 datasets, 15 countries, occupancy patterns and behaviors) but contains no diversity percentage and no mention of ASHRAE 90.1 or EN 16798-1 | NOT IN ABSTRACT |
| L02 | Li et al. (2017): "6 residential homes in Colorado", F1 improved 0.68 to 0.84 vs Markov baseline | No abstract available at OpenAlex or CrossRef | NO ABSTRACT |
| L03 | Turley et al. (2020): "6 Colorado residential homes with ecobee and environmental sensors" vs fixed setpoint, "5.0% average HVAC energy reduction" | Abstract: "Real occupancy data from six homes located in Colorado... savings on average of 5.0% and without degradation of thermal comfort" | SUPPORTED (home count and 5.0% figure both confirmed; "ecobee" brand name not itself in the abstract, but "connected thermostat" is) |
| L04 | Kleiminger et al.: ECO dataset, "5 Swiss residential households, tablet presence ground truth"; "supervised classifiers achieved 80% to 85% accuracy; 30-minute aggregation degraded accuracy below 72%" | Abstract: "fine-grained electricity consumption data along with ground-truth occupancy information for 5 households during a period of about 8 months... accuracies of more than 80%" | PARTIALLY SUPPORTED: 5 households and >80% both confirmed. The specific 85% ceiling and the 72%-at-30-minutes figure are NOT IN ABSTRACT. More importantly, this abstract says ground truth was collected "during a period of about 8 months" for all 5 households, which conflicts with the report's own Key Finding #2 (Section B row 2), which caps ECO ground truth at "only 80 days per house". See Section 4 below. |

## 3. URLs and quotes

| Dataset | URL in report | Result | Notes |
|---|---|---|---|
| ECO | `https://www.vs.inf.ethz.ch/res/show.html?what=eco-data` | 200, opened, full text read | Page states data "collected in 6 Swiss households", not 5 (see Section 4). Page lists the two real ECO citations (Beckel et al. BuildSys 2014; Kleiminger et al. BuildSys 2013) -- neither matches the DOI the report used for the ECO citation (row 1 above). Page contains **no licence statement of any kind**; the quoted string "Open for research and educational purposes with attribution" does not appear anywhere on the page. Quote verdict: NOT FOUND. |
| ARAS | `https://www.cmpe.boun.edu.tr/aras/` | Connection refused / timed out twice, and WebFetch also failed (ECONNREFUSED) | PAGE NOT READABLE. Cannot check the quoted licence "Free for academic research use." A WebSearch confirms the page exists and is indexed, and that outside summaries describe the deployment as "two months", not the report's "30 days" -- see Section 4. |
| REFIT (via DOI) | `https://doi.org/10.1038/sdata.2016.122` | 200, opened | Abstract confirms 20 houses, 2 years, 8-second whole-house and appliance data. Quoted licence "Creative Commons Attribution 4.0 International (CC BY 4.0)" -- FOUND verbatim on the page ("licensed under a Creative Commons Attribution 4.0 International License"). |
| IDEAL (via DOI) | `https://doi.org/10.1038/s41597-021-00921-y` | 200, opened | Abstract confirms 255 UK homes, 23-month period (report rounds to "2 years", acceptable). Quoted licence CC BY 4.0 -- FOUND. Abstract makes **no mention of occupancy inference at all** (it lists temperature/humidity/light sensors, not presence) -- the report's "NO MANUAL LOG: Algorithmic occupancy estimation only" claim is not supported by this page; NOT IN ABSTRACT. |
| UK-DALE (via DOI) | `https://doi.org/10.1038/sdata.2015.7` | 200, opened | Quoted licence CC BY 4.0 -- FOUND on page. |
| HUE | `https://github.com/intelligent-systems-lab/HUE` | **404 Not Found** (checked twice, urllib and WebFetch agree) | The real HUE code repository is `github.com/smakonin/HUE.dataset`, owned by Stephen Makonin, and the real custodian institution is **Simon Fraser University**, not "Univ. of British Columbia" as the report states. See Section 4 for the home-count discrepancy too. |
| CASAS | `https://casas.wsu.edu/datasets/` | 200, opened | Page lists 21+ distinct testbeds with widely varying resident counts (1 to 40) and annotation status (Yes/Partial/No), not a single "~10 apartments" figure. The words "license" and "academic" do not appear anywhere on this page, so the quoted "CASAS Academic Use License. Free for non-commercial research." is NOT FOUND on the page cited. |
| BDG2 (via DOI) | `https://doi.org/10.1088/1742-6596/2600/3/032003` | Blocked by Radware bot-protection challenge (both urllib and WebFetch redirected to `validate.perfdrive.com`) | PAGE NOT READABLE directly; OpenAlex abstract obtained instead (see Section 1, row 5): confirms this is the wrong paper for the claimed "Miller et al. 2020, 1,636 non-residential buildings" citation. |

## 4. Key numeric facts

| # | Fact | Result |
|---|---|---|
| 1 | "ECO dataset contains 5 Swiss households" | CONTRADICTED (partial): the ECO project's own page states data was "collected in 6 Swiss households over a period of 8 months"; occupancy CSVs are provided for 5 of those 6 (household 06 has no occupancy folder). The report's blanket "5 households" for the dataset is not what the source page says. |
| 2 | "ECO ground-truth tablet presence logs exist for only 80 days per house (approx. 400 home-days total)" | NOT CONFIRMED, and in tension with the report's own cited source: the Kleiminger et al. abstract (used by the report itself as L04) says ground-truth occupancy was collected "for 5 households during a period of about 8 months" -- i.e. closer to the full 8-month deployment, not 80 days. If the fuller reading is right, ECO alone approaches or exceeds the report's global "under 1,200 home-days" total by itself. |
| 3 | "ARAS: 2 houses, 30 days" | NOT CONFIRMED, possibly CONTRADICTED: the ARAS site could not be opened (Section 3), but outside summaries (WebSearch, independent of the report) describe the ARAS collection as running "during two months" in each of the two houses, not 30 days. This would double the report's ARAS home-day count. |
| 4 | "REFIT: 20 UK homes, 2 years, 8-second" | CONFIRMED at the Nature abstract. |
| 5 | "IDEAL: 255 UK homes" | CONFIRMED at the Nature abstract (255 UK homes, 23-month period, mean participation 286 days). |
| 6 | "Building Data Genome 2: 1,636 non-residential buildings, zero residential" | NOT CONFIRMED: the DOI actually cited resolves to a different 2023 paper (the Building Data Genome Directory, a 60-dataset portal), never opened by the report for this number. The 1,636-building, all-commercial figure is consistent with general knowledge of the real BDG2 dataset but rests on a citation to the wrong paper, so it is not verified from any source this report actually opened. |
| 7 | "HUE: Univ. of British Columbia, 42 homes" | CONTRADICTED: independent search results describe HUE as created by Stephen Makonin at Simon Fraser University (not UBC) with "twenty-two houses" in the released dataset, not 42, and hosted at a different GitHub org than the report's (dead) link. |

## 5. Completeness

Against the T21 prompt items:

| Item | Status |
|---|---|
| Item 1, registry (Section F) | ANSWERED but incomplete against the prompt's own search list. Present: ECO, ARAS, REFIT, IDEAL, UK-DALE, HUE, CASAS, BDG2 (8 rows). **Silently DROPPED as registry rows**, despite being explicitly named in the prompt: SPHERE, Smart* / UMass Smart Home, Pecan Street Dataport, IEA EBC Annex 79 occupant datasets, LBNL occupancy datasets, any Canadian university test house or utility pilot dataset, any European Horizon project household sensor release. SPHERE is the most serious drop: Section A's own headline sentence names SPHERE as one of only four datasets worldwide with ground-truth presence, at "approx. 100 homes" (by far the largest home count claimed anywhere in the report), yet SPHERE has zero registry row, zero URL, zero citation, and is never mentioned again outside that one sentence -- so its 100-home figure is completely unsourced within the report. |
| Item 1, "household composition known or not" | DROPPED for every row; no row states whether household composition is known. |
| Item 2, fitness to score a population | ANSWERED (Section G, item 2), but the underlying ECO and ARAS home-day counts it depends on are themselves not confirmed (Section 4 above). |
| Item 3, prior comparison studies | ANSWERED (Section C, 4 rows). |
| Item 4, coverage gaps | ANSWERED (Section G, item 4). |
| Named leads: NREL OEDI, Pecan Street Dataport access pages, ASHRAE OB database portal, Dryad, Figshare | Never mentioned as checked or ruled out; silently absent. |
| Section F data-source-card columns required by brief section 9 | Present: source & custodian, country/geography, sample size, ground-truth presence, room/dwelling. **Missing from every row**: whether the source is still updated; unit (household/dwelling/device etc. as its own column); the occupancy variable quoted verbatim from documentation; roles `R1` to `R4` (an explicit hard requirement of section 9, absent from the entire table); known selection bias; one verified example of use in building energy research or `NONE FOUND`. |

## 6. Dashes

U+2014 (em dash): 0. U+2013 (en dash): 0. Compliant.

## 7. Rules

- No named individual is connected to a fellowship programme anywhere in the report.
- No proposal to change the 4J gate.
- No claim that this report itself was vetted or accepted.
