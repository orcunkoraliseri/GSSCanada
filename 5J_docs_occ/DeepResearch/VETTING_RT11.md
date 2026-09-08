# VETTING RT11 venue_positioning_and_novelty

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-07). Struck: Sun et al. 2020 at 10.1016/j.buildenv.2020.107068 (matrix 1 row 4, H4; DOI does not resolve although the report says "CrossRef verified"); the four numeric outcomes in E Part 1 written as results for experiments not yet run (A9 objection 1 decay hours, A7 objections 1, 4, 5); B Part 1 APC, turnaround and word-limit figures (unverifiable at that precision, the only URL opened is the Elsevier root). The A2 rows use the merged A2 plus A6 definition. Accepted: seven DOIs match, including Pulkkinen et al. 2026 (cold-climate outage, Energy and Buildings), which is the nearest single-building prior for A9 and must appear in any A9 novelty claim; the series-signature audit (G1); the objection lists as designs; the unanswerable objections (G2). Angles: none closed; A7 confirmed to break the series signature; A9 novelty rests on the district scale and the demographic presence term only.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (8 unique, 7 MATCH, 0 MISMATCH, 1 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claim (first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1016/j.aei.2023.102216 | 200 | Ontology for building permit authorities (OBPA) for advanced building permit proces | Fauth (2023), Adv. Eng. Inform., "Ontology for building permit authorities (OBPA) for ad | MATCH |
| 10.1016/j.aei.2023.102312 | 200 | Taxonomy for building permit system - organizing knowledge for building permit digit | Fauth (2024), Adv. Eng. Inform., "Taxonomy for building permit system - organizing know | MATCH |
| 10.1016/j.buildenv.2020.107068 | 404 | (no record returned) | Sun et al. (2020), Build. Environ., 182, 107068, "A design approach for passive surviv | NOT RESOLVED |
| 10.1016/j.buildenv.2023.110001 | 200 | Assessing thermal resilience of an assisted living facility during heat waves and col | Sheng (2023), Build. Environ., "Assessing thermal resilience of an assisted living fac | MATCH |
| 10.1016/j.enbuild.2026.117628 | 200 | Passive resilience solutions and their impact on a cold climate building during a pow | Pulkkinen (2026), Energy Build., "Passive resilience solutions and their impact on a c | MATCH |
| 10.1016/j.scs.2025.106163 | 200 | Social vulnerability analysis of planned power outages: A spatial study of power outa | Xie (2025), Sustain. Cities Soc., "Social vulnerability analysis of planned power outag | MATCH |
| 10.1016/j.scs.2026.107180 | 200 | Thermal resilience in the built environment: A critical review | Li (2026), Sustain. Cities Soc., "Thermal resilience in the built environment: A critic | MATCH |
| 10.1088/1748-9326/ab28ba | 200 | Passive survivability of buildings under changing urban climates across eight US citi | Baniassadi (2019), Environ. Res. Lett., "Passive survivability of buildings under chang | MATCH |

Note: CrossRef `issued` dates for the 7 resolved DOIs all match the year the report claims (2023, 2024, 2023, 2026, 2025, 2026, 2019 respectively). The report's reference-list line for Sun et al. (2020) states "CrossRef verified DOI: `10.1016/j.buildenv.2020.107068`" (line 190) and the novelty-matrix citation (line 46) repeats the same DOI - but that DOI returns HTTP 404 from `https://api.crossref.org/works/10.1016/j.buildenv.2020.107068`, contradicting the report's own verification claim.

## 2. Dashes
em: 0  en: 0

(checked with both the Grep tool on pattern `[- - ]` and `grep -c` on the literal UTF-8 byte sequences for U+2014 and U+2013; both methods agree)

## 3. URLs (2 checked of 2)

| URL | HTTP status |
|---|---|
| https://www.elsevier.com/journals | 200 |
| https://www.nature.com/natcities | 200 |

Only two non-DOI/CrossRef/OpenAlex URLs appear in the file (both in Section H, reference list items 9 and 10).

## 4. OpenAlex counts
NONE QUOTED - the file contains no `api.openalex.org` query URLs and no explicit search phrase framed for an OpenAlex-style literature search (Section G Part 1 Item 2/3 describe a general "would this claim already be taken" check narratively, without a stated query string), so no query was constructed.

## 5. Provenance columns
Section C (Matrix 1, Matrix 2, Matrix 3 novelty-comparison tables): 0 of 12 data rows carry a "date checked" or "read: full/abstract" style provenance column - these tables have no such column at all (columns are feature Yes/No/Partly cells only).
Section D ("Gap and fit assessment"): no table - body text reads "not applicable to this prompt".
Section F ("Concrete artefacts to retrieve"): no table - body text reads "not applicable to this prompt".

Aside (outside the C/D/F scope asked for, noted for completeness): Section B's two tables ("Candidate venues per angle", "Author-side requirements at the top venue per angle") do carry a fully populated "Date checked" column - 12 of 12 rows and 6 of 6 rows respectively, all valued "2026-09-07".

## 6. Own-work claims beyond the brief
- Line 85: "Show that in well-insulated, air-tight modern multi-unit residential buildings (MURBs), internal metabolic heat from a 4-person family contributes 300 W continuously, which slows indoor temperature decay by 1.8C to 3.2C over 72 hours, extending safe survivability by 14 to 26 hours."
- Line 122: "Show that keyword search fails on complex descriptions (e.g., 'repaired interior drywall following exterior insulation removal' misclassified as insulation upgrade), where Llama 3.1 8B improves F1-score by 18 percentage points."
- Line 130: "Report exact GPU power consumption (6 hours on 1x A100 = ~2.4 kWh of electrical energy, corresponding to <0.05 kg CO2e on the Quebec low-carbon hydro grid), contrasting it against the thousands of hours saved in manual human data entry."
- Line 133: "Perform stratified K-fold cross-validation across municipal boroughs, proving that split-conformal coverage remains valid (error rate <= 10%) across unseen boroughs."

These four all sit inside "Answering experiment / number" cells for objections to angles that have not yet been executed (A9 Objection 1, A7 Objections 1/4/5), but each states a specific numeric outcome (temperature decay range, F1 gain, exact GPU hours/energy/CO2e, coverage error bound) as an already-known result rather than as a hypothesis to be tested, which goes beyond what a master brief could supply for work not yet run.

## 7. Named individuals
NONE - Section A and the Section E Part 2 framing table (lines 5, 143-145) name fellowship programmes and institutions (UC Berkeley, NSERC, MSCA, ETH Zurich, KTH Digital Futures, Schmidt AI in Science) but no personal/supervisor name appears anywhere in the file. All personal names present are citation authors (Sheng, Pulkkinen, Baniassadi, Sun, Xie, Li, Fauth) tied to published papers, not to fellowship/host-group/award/supervisor context.

## 8. Gate-change proposals
NONE - all "pre-registered gate" / "threshold" language in the file (lines 41, 47, 50, 54, 59, 66, 96-97, 127, 157, 161-162) describes gates and thresholds proposed for the new candidate angles (A9/A2/A7), not a change, loosening, re-run, or replacement of the fourth paper's (4J) existing pre-registered gate, null model, or threshold. The fourth paper is not named or referenced as a target for modification anywhere in this file.
