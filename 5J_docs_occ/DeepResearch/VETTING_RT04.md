# VETTING RT04 occupant_behaviour_frontier

VERDICT: FAILED ROUND (manager, 2026-09-07). Failed negative controls: identities it cannot fake, and claims about our own work. Six of twelve DOIs resolve to other papers, including our own CENTUS paper, for which H5 prints an invented CrossRef title; Widén 2009, McKenna 2014, Barthelmes 2016, Fischer 2016 and the BDG2 data paper are mis-paired; BuildOcc Zenodo and the ASHRAE occupant database figshare DOI return 404. Half of Section C has no verified identity, and G3 ("did you describe our own papers back to us? No") is contradicted by C01 and H5. Salvage: B4 and G2 NOT FOUND for heat-responsive presence stands as a negative on absence (with reduced confidence, corroborated by RT05 and RT08); B2 and B3 Annex 79 closure and Annex 95 succession as pointers to open; F rows ATUS and MTUS as access routes (also in RT07); G1's four defects of time-use derived occupancy as argument. Angles: narrows A2 as the prompt intended; nothing else may be quoted from this report. Re-run with the CrossRef title required beside every DOI and our paper's row copied from the brief verbatim.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (12 unique, 4 MATCH, 6 MISMATCH, 2 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claimed title/work (first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1016/j.buildenv.2020.106738 | 200 | Introducing IEA EBC annex 79: Key challenges and opportunities in the field  | O'Brien et al. (2020): Introducing IEA EBC annex 79: Key challenges and opp | MATCH |
| 10.1016/j.enbuild.2009.02.013 | 200 | Constructing load profiles for household electricity and hot water from tim | Widen et al. (2009): A combined Markov-chain and bottom-up approach to mode | MISMATCH |
| 10.1016/j.enbuild.2014.07.039 | 200 | Hygrothermal performance of exterior walls covered with aerogel-based insul | McKenna et al. (2014): Four-state domestic building occupancy model for ene | MISMATCH |
| 10.1016/j.enbuild.2016.03.011 | 200 | Thermal properties of porous stones in cultural heritage: Experimental find | Barthelmes et al. (2016): Occupant behavior lifestyles in a residential nea | MISMATCH |
| 10.1016/j.enbuild.2016.03.018 | 200 | In memoriam Professor Milorad Bojic, Ph.D.Sci. | Fischer et al. (2016): Model for electric load profiles with high time reso | MISMATCH |
| 10.1016/j.enbuild.2018.06.029 | 200 | Building occupancy modeling using generative adversarial network | Chen & Jiang (2018): Building occupancy modeling using generative adversari | MATCH |
| 10.1016/j.enbuild.2026.117155 | 200 | Occupancy modeling using population statistics and machine learning for urb | Iseri et al. (2026) [OUR PAPER]: Deep learning-based daily activity and pre | MISMATCH |
| 10.1016/j.enbuild.2026.117181 | 200 | Conversational preference learning for personalized thermal comfort control | Liu et al. (2026): Conversational preference learning for personalized the | MATCH |
| 10.1038/s41597-020-00712-x | 200 | The Building Data Genome Project 2, energy meter data from the ASHRAE Great | Miller et al. (2020): The Building Data Genome Project 2, energy meter data | MISMATCH |
| 10.1038/s41597-022-01475-3 | 200 | A Global Building Occupant Behavior Database | Dong et al. (2022): A global building occupant behavior database | MATCH |
| 10.5281/zenodo.21192895 | 404 | (not found) | BuildOcc software DOI | NOT RESOLVED |
| 10.6084/m9.figshare.16920118.v6 | 404 | (not found) | ASHRAE Global Occupant Behavior Database dataset | NOT RESOLVED |

Note: for items 2-5 and 9, the report gives real-looking author names and a plausible title, but the DOI resolves to a different (also real) paper by different authors/subject; item 7 is the author's own CENTUS paper, where the report's claimed title and its own asserted "CrossRef title:" do not match what CrossRef returns for that DOI.

## 2. Dashes

em: 0  en: 0

## 3. URLs (1 checked of 1)

| URL | HTTP status |
|---|---|
| https://github.com/buds-lab/building-data-genome-project-2 | 200 |

## 4. OpenAlex counts

NONE QUOTED. Row B4/B5 mention "Systematic search in OpenAlex, Scopus, and WoS" / "Literature search across BEM, travel demand, and sociodemographics" as sources but give no query strings, API URLs, or counts.

## 5. Provenance columns

Section C (Landscape table, "Read" column, 9 rows C01-C09): 9 of 9 rows carry an explicit value ("Full" or "Abstract"). 0 empty/generic.
Section D (Gap and fit table, 5 rows D1-D5): 0 of 5 rows carry a "date checked" or "read" column (columns present: # / Missing capability / Agenda document naming it / Our assets addressing it / Status for our group / Fit with 5J angles - no provenance column exists).
Section F (datasets table, 5 rows): 0 of 5 rows carry a "date checked" or "read" column (columns present: Dataset / What it contains / Resolution / Licence / Access route / Held-out validation potential - no provenance column exists).

## 6. Own-work claims beyond the brief

1. Line 94 (Section H, item 5): "Iseri, O.K., Gursel Dino, I., Kalkan, S. (2026). Deep learning-based daily activity and presence profile generation conditioned on demographic and household characteristics. ... CrossRef title: 'Deep learning-based daily activity and presence profile generation conditioned on demographic and household characteristics'." - the master brief gives only the journal/volume/DOI for CENTUS, not a title; the title stated here, and the "CrossRef title" the report claims to have verified, do not match what CrossRef actually returns for this DOI (see Section 1, row 10.1016/j.enbuild.2026.117155).
