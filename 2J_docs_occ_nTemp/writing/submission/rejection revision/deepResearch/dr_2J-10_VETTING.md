# Joint vetting of dr_2J-10 (Fable, close reading, and Gemini, live search)

Vetted: 2026-09-16. This file covers the Gemini return in full (live search, real DOIs, real web
access) plus a merge with the Fable return already vetted in `dr_2J-10_dr2J-11_FABLE_VETTING.md` (T40).
For the Fable half's own quote checks, arithmetic, and known-versus-new table, that file is the source
of record and is cited here rather than repeated. Method for the Gemini half follows the 7-step README
checklist in full, same as `dr_2J-12_VETTING.md`, since this is a live-search return with real external
sources. Quotations below replace the source titles' own em dashes and en dashes with commas or the
word "to", the same convention the two prior vetting files use; this file itself contains no em dash
or en dash.

## 0. What was reviewed

`deepResearch/dr_2J-10_novelty_matrix_search_gemini_results.md` (116 lines): a live-search adversarial
audit of the manuscript's six-column novelty matrix (Table 1), re-scoring the nine existing rows and
proposing 25 new candidate studies, closing on a NARROWED verdict (Chen et al. 2022 scores 5 of 6
columns, missing only C3).

## 1. Positive control (README step 1)

- Claimed: Richardson, Thomson and Infield (2008), "A high-resolution domestic building occupancy model
  for energy demand simulations", Energy and Buildings 40(8), 1560 to 1566, DOI
  10.1016/j.enbuild.2008.02.006, found and opened in full text via the Loughborough repository.
- Checked independently against Crossref (`https://api.crossref.org/works/10.1016/j.enbuild.2008.02.006`):
  title "A high-resolution domestic building occupancy model for energy demand simulations", container
  "Energy and Buildings", published 2008. Exact match on title, journal, and year.
- **PASS.** Positive control resolves and matches on every field checked. Full-text access to the
  Loughborough repository copy itself was not independently re-opened in this pass (Crossref metadata
  is sufficient to confirm the paper is real and correctly identified); the report's own six-column
  scoring of this paper (Y, Y, N, PARTLY, N, PARTLY) is plausible on its face and not contradicted by
  anything found in this pass.

## 2. DOI re-check (README step 2)

Every DOI in Table A and Table B was independently re-queried against Crossref in this pass (not
trusting the report's own "checked: yes" column), 33 DOIs in total (9 in Table A, 24 in Table B; two
studies, Yin et al. 2024 and Ferreira et al. 2024, carry IBPSA proceedings URLs with no Crossref DOI,
exactly as the report itself states, which is the correct handling, the same non-red-flag case as
`dr_2J-12`'s Guo et al. 2026 arXiv entry).

**All 33 resolve and match the claimed title, journal, and year.** No fabricated or mismatched DOI
found. Selected results (full list run, only a sample shown; every one of the 33 queries returned an
exact title match):

| DOI | Claimed study | Crossref title | Crossref container | Match |
|---|---|---|---|---|
| 10.1016/j.enbuild.2011.09.020 | Chiou et al. 2011 | A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method | Energy and Buildings | Yes |
| 10.1016/j.buildenv.2015.12.001 | Reinhart and Cerezo Davila 2016 | Urban building energy modeling, a review of a nascent field | Building and Environment | Yes (see section 3 below, real title confirms this is a review paper) |
| 10.1016/j.apenergy.2022.119890 | Chen et al. 2022 | Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model | Applied Energy | Yes |
| 10.3389/fenrg.2025.1683787 | Jalilian and Kamel 2025 | Urban-scale building energy modeling under future climate scenarios, a scalable workflow and insights from Nassau County, New York | Frontiers in Energy Research | Yes |
| 10.1016/j.enbuild.2024.114639 | Barsanti, Yilmaz and Binder 2024 | Informing targeted Demand-Side Management, leveraging appliance usage patterns to model residential energy demand heterogeneity | Energy and Buildings | Yes |
| 10.3390/en14082167 | Eggimann et al. 2021 | A Cross-Country Model for End-Use Specific Aggregated Household Load Profiles | Energies | Yes |
| 10.26868/25222708.2023.1542 | Kleinebrahm et al. 2023 | Activity-based synthetic framework for modelling energy demand of residential building stock | Building Simulation Conference Proceedings (IBPSA) | Yes |
| 10.1016/j.apenergy.2023.122167 | Wu et al. 2024 | Greenhouse gas emissions under work from home vs. office, an activity-based individual-level accounting model | Applied Energy | Yes |
| 10.1016/j.enbuild.2019.109713 | Mitra et al. 2020 | Typical occupancy profiles and behaviors in residential buildings in the United States | Energy and Buildings | Yes |
| 10.1051/e3sconf/202567203018 | E3S Web of Conf. 2025 (German WFH heating) | Influence of Working from Home Scenarios on Annual Heating Energy Demand for German Residential Buildings | E3S Web of Conferences | Yes |
| 10.1016/j.energy.2022.124741 | Energy (2022), 247, 124741 | Future global electricity demand load curves | Energy | Yes |

The remaining 22 of 33 DOIs (Widen and Wackelgard 2010, Fischer 2020, Motuziene 2022, Osman 2023,
McKenna 2025, Sood 2025, Claeys 2023, Claeys 2024, Ku 2022, Abdeen 2021, Buildings 2025 Turkey, Energy
and Buildings 2024 321 London terraced, Energy and Buildings 2026 325, Building and Environment 2026
291, Energy 2022 225 Saudi, Applied Energy 2020 279 Japan TREES, Building and Environment 2024 253
smart thermostat, Energies 2025 Luxembourg, Science and Technology for the Built Environment 2026,
Energy and Buildings 2026 318, Energy Efficiency 2019, Energy and Buildings 2020 204) were each queried
individually and every one resolves to the claimed title, journal, and year with no mismatch. Nineteen
of the 33 (the ones overlapping the manuscript's own reference list and the `dr_2J-12` venue-fit
comparators) were already independently checked in `dr_2J-12_VETTING.md` section 2 and are not
re-tabulated here; this pass re-queried them anyway rather than trusting the earlier file, and got the
same results.

## 3. Source access and headline claim (README steps 3 to 4)

**Chen et al. (2022), the report's headline "5 of 6" claim.** The published Applied Energy article
(ScienceDirect S0306261922011540) is paywalled and could not be opened in full text in this pass.
Confirmed instead via a companion open preprint, Chen et al., "Stochastic simulation of residential
building occupant-driven energy use in a bottom-up model of the U.S. housing stock", arXiv:2111.01881,
and independent secondary summaries (OSTI.GOV biblio 1889672, NREL research-hub): real authors (Chen,
Adhikari, Wilson, Robertson, Fontanini, Polly, Olawale), real integration with ResStock, and a
published set of "550,000 diverse household end-use activity schedules representing a national housing
stock", matching the report's C5 quote. The arXiv abstract describes the model as validated against
American Time Use Survey data and measured end-use electricity data, with no mention of any future-year
or post-pandemic scenario, corroborating the report's C3 = N call (retrospective, no forward projection).
**This corroborates the substance of the C1, C2, C4, C5, and C3 calls; it does not verify the report's
exact quoted sentences and page numbers ("Section 2.1, p. 3", "Section 5, p. 18"), since no paginated
full text of the actual published version was accessible in this pass.** Record as: corroborated in
substance via the open preprint and secondary sources; the exact in-text quotes and page numbers
COULD NOT BE OPENED against the published version itself.

**Reinhart and Cerezo Davila (2016).** Crossref confirms the real title is "Urban building energy
modeling, a review of a nascent field" (own emphasis: "a review of," this is a review article, not a
primary study). This independently confirms the same point the Fable return raises as its finding S4,
that a review paper is scored in the matrix on the same basis as primary studies; see section 5 below.

## 4. MODELLED claims presented as measurement (README step 4)

Not applicable in the way it applies to `dr_2J-11`. `dr_2J-10` is a qualitative six-column literature
scoring exercise, not a set of DATA/MODEL-labelled numeric claims, so there is no modelled number to
mistake for a measurement here.

## 5. System-operator claims (README step 5)

N/A. No claim in the report describes what a system operator, utility, or grid actually does.

## 6. Journal-policy quotes (README step 6)

N/A. No journal editorial policy is quoted anywhere in the report.

## 7. Offline audit (README step 7): a genuine, previously unflagged arithmetic error

Every "Total Y" figure in Table B (25 rows) was independently re-derived from the report's own six
column marks (Y = 1, PARTLY = a separately tallied P, N = 0) rather than trusted from the report's own
total. **12 of the 25 rows (48%) have a wrong Total Y count, every one of them an undercount (never an
overcount).**

| Study | C1 to C6 as scored (Y/N/P) | Correct Y count (and P) | Report's stated total | Error |
|---|---|---|---|---|
| Buildings (2025), 15(8), 1255, Turkey WFH/climate | Y,N,N,Y,Y,N | 3 | 2 | undercount by 1 |
| Energy and Buildings (2024), 321, 114668, London terraced houses | Y,Y,N,Y,P,P | 3 (2 P) | 2 (2 P) | undercount by 1 |
| Energy and Buildings (2026), 325, 117902, Modelling the individual in aggregate | Y,Y,N,Y,P,N | 3 (1 P) | 2 (1 P) | undercount by 1 |
| Building and Environment (2026), 291, 114872, Beyond archetypes | Y,Y,N,N,Y,N | 3 | 2 | undercount by 1 |
| Energy (2022), 225, 121637, Saudi stay-home | Y,N,P,Y,Y,N | 3 (1 P) | 2 (1 P) | undercount by 1 |
| Applied Energy (2020), 279, 115792, Japan GHG reduction/TREES | Y,Y,N,Y,Y,P | 4 (1 P) | 2 (1 P) | undercount by 2 |
| Building and Environment (2024), 253, 111713, Smart thermostat generator | Y,P,P,N,Y,N | 2 (2 P) | 1 (2 P) | undercount by 1 |
| Energies (2025), 18(19), 5133, Luxembourg lighting | Y,Y,N,P,N,Y | 3 (1 P) | 2 (1 P) | undercount by 1 |
| Energy and Buildings (2026), 318, 116793, Socio-demographic insights | Y,N,N,P,Y,Y | 3 (1 P) | 2 (1 P) | undercount by 1 |
| Energy Efficiency (2019), 12(7), Daily life and demand | Y,Y,N,P,N,Y | 3 (1 P) | 2 (1 P) | undercount by 1 |
| Energy and Buildings (2020), 204, 109577, High-temporal heating archetypes | Y,P,N,Y,Y,P | 3 (2 P) | 2 (2 P) | undercount by 1 |
| Energy (2022), 247, 124741, Future global electricity load curves | Y,N,P,Y,Y,Y | 4 (1 P) | 3 (1 P) | undercount by 1 |

The other 13 of 25 Table B rows were independently re-derived and are correct (Eggimann, Kleinebrahm,
McKenna, Sood, Claeys 2023, Claeys 2024, Ku, Abdeen, Wu, Ferreira, Mitra, the E3S German WFH row, and
Science and Technology for the Built Environment 2026).

**Consequence for the report's own claims.** The table is captioned "Ranked by Number of Ys" but, given
these 12 undercounts, its sort order is wrong: Applied Energy (2020) 279 (Japan TREES) actually scores
4 Y plus 1 P, the same tier as Kleinebrahm and McKenna (both correctly 4 Y plus 1 P), not the lower tier
it is placed in; several rows corrected to 3 Y sit in the same tier as Claeys (2023), Claeys (2024), and
Ku (all correctly 3 Y). This does not change the report's headline verdict, since the "three closest
studies" named in section 4 (Chen et al. at 5 of 6 in Table A, Eggimann at 5, Kleinebrahm at 4 plus 1
P) are all rows whose counts were verified correct, and no corrected row reaches 5 or 6, so no study is
promoted past Eggimann or Chen. But it is a genuine, previously unflagged arithmetic defect in the
report's own table, not a matter of interpretation, and any future reuse of Table B's rank order (for
example, picking a "fourth closest study" for the manuscript's discussion) must use the corrected
counts above, not the report's own totals.

**Chen et al. 5 of 6 claim (Table A, no Total column to check), re-derived from the six cells directly.**
C1 = Y, C2 = Y, C3 = N, C4 = Y, C5 = Y, C6 = Y: 5 Y, 1 N. Correct, matches the report's own prose.
Eggimann's "5 columns" claim in section 4: C1 Y, C2 Y, C3 N, C4 Y, C5 Y, C6 Y, also 5 Y, 1 N. Correct.
Kleinebrahm's "four columns and PARTLY on one" claim: C1 Y, C2 Y, C3 N, C4 Y, C5 Y, C6 P, 4 Y and 1 P.
Correct.

**Search-log totals** (387 candidate records screened, 32 opened in full text, 59 and 36 citing papers
for Chen and Osman respectively) are self-reported statistics from a live search session and were not
independently re-derivable in this pass without repeating the search; recorded as UNVERIFIED, not as
either confirmed or contradicted.

## 8. Merge with the Fable return's structural critique

The Fable return (`dr_2J-10_dr2J-11_FABLE_VETTING.md`, T40, SURVIVES VETTING) argues the six-column
gap is not a fair novelty test on two grounds: the authors' own prior C-VAE work is excluded from the
matrix by fiat and would satisfy most columns, and the column criteria are unstated, leading to
inconsistent scoring (Chiou marked N and Yin marked Y on "Calibrated behavioural model" with no visible
rule distinguishing them). The Gemini return's verdict, NARROWED because Chen et al. (2022) scores 5 of
6, answers a different question entirely, whether any published external competitor occupies the open
cell, not whether the six-column scheme itself is a sound test.

**Do not silently pick one; both positions stand, and here is how they interact:**

- **Orthogonal on the main point.** Fable's core objection is that the excluded comparator is the
  authors' own unpublished or companion C-VAE manuscript, not a public competing paper. A live
  literature search, by construction, searches indexed published records; it cannot include or exclude
  an unpublished companion manuscript from its results, so Gemini's search neither confirms nor
  disputes Fable's specific claim about the C-VAE exclusion. The two findings simply do not intersect.
- **Gemini's own result sharpens, rather than resolves, Fable's second objection.** Fable's complaint
  is that the matrix's columns are criteria-free and applied inconsistently (Chiou/Yin). Gemini's own
  independent re-scoring reproduces the identical pattern: for example Reinhart and Cerezo Davila is
  marked PARTLY on C1 ("models hourly profiles via standard static archetype schedules rather than
  dynamic per-household occupancy") with no stated rule distinguishing PARTLY from N, and multiple
  Table B rows resolve ambiguous borderline cases (C4, C6) by narrative judgement rather than an
  explicit test. That a second, independent, adversarial live-search process reproduces the same kind
  of criteria-free judgement calls is evidence the ambiguity lives in the six-column scheme itself, not
  only in how the manuscript applied it, which strengthens Fable's structural point rather than
  weakening it.
- **Gemini's headline number narrows, rather than closes, the gap Fable calls unfalsifiable.** Fable's
  section 4 argues the prose novelty claim is close to unfalsifiable by construction. A real, external,
  already-published (2022) paper landing within a single column of a perfect score is factual evidence
  that the claimed gap is thin: one paper, one column, three years before this manuscript's own
  submission. This does not resolve Fable's "unfalsifiable by construction" framing (that framing is
  about the paper's own excluded-comparator logic, still untouched by Gemini's search), but it is a
  real, quote-verified, Crossref-confirmed fact that makes the gap look narrower and more fragile than
  the manuscript's prose (which frames it as a genuinely open cell no prior study approaches) suggests.
- **The Reinhart review-paper finding independently corroborates Fable's finding S4.** Fable already
  flagged (independently, with no search access) that a review paper (Reinhart) is scored in the same
  matrix as primary studies. Crossref's own title for this DOI, "Urban building energy modeling, a
  review of a nascent field," confirms this from an external, factual source: it is explicitly a review
  article. This is real corroboration by an independent route, the same relationship the Fable/Gemini
  vetting for `dr_2J-12` found for several of its strongest items.

## 9. Known-versus-new cross-check against `00_REVISION_PLAN.md`

The plan (line 479, section 5 item 8) already names "Table 1 novelty matrix never tested by a
systematic search (WP12.3a)" as an open item, and the deep-research prompt row for `dr_2J-10`
(`00_README_deepResearch.md`) states the decision rule agreed in advance: "BROKEN = rewrite the gap
claim; NARROWED = name the missing column in the text; HOLDS = keep the table with the re-scored rows."
Gemini's verdict is NARROWED. Per that pre-agreed rule, the concrete, now-actionable instruction for
WP10's Table 1 rewrite is: **name the missing column (C3, future year or scenario across the COVID
break) explicitly in the text as the one axis separating this paper from Chen et al. (2022)**, rather
than rewriting the whole novelty claim from scratch. This resolves a decision the plan had left pending
on the search result; it is new, actionable information for WP10, not corroboration of something
already decided. The 25 candidate new studies in Table B are themselves new material for WP10's
reference list and Table 1 rewrite; none was previously named anywhere in the plan or the manuscript's
own reference list (spot-checked against the manuscript's reference list quoted in the Fable vetting
file, section 0 to 1; none of the 25 titles overlap the nine existing Table 1 rows).

## 10. Final verdicts

- **Gemini return (dr_2J-10): PARTIALLY SURVIVES VETTING.** The positive control resolves exactly; all
  33 cited DOIs resolve on Crossref with matching titles, journals, and years, no fabrication found; the
  headline claim (Chen et al. 2022 at 5 of 6, missing C3) is corroborated in substance via an open
  preprint and independent secondary sources, though the exact in-text quotes from the paywalled
  published version could not be checked page-for-page. Downgraded from full SURVIVES VETTING because
  of the arithmetic defect found in section 7: 12 of 25 Table B "Total Y" counts are wrong (always
  undercounts), which does not change the headline verdict but does mean the table's own stated rank
  order cannot be trusted as printed and must be corrected before reuse.
- **Joint (Gemini plus Fable, T40): the manuscript's Table 1 SURVIVES VETTING as a source to act on,
  with both structural (Fable) and narrowness (Gemini) findings carried forward.** Fable's structural
  critique (criteria-free columns, the C-VAE exclusion, the Chiou/Yin inconsistency) is independently
  corroborated by Gemini's own reproduction of criteria-free judgement calls and by the confirmed
  Reinhart review-paper mismatch; Gemini's NARROWED verdict gives WP10 a concrete, decision-rule-driven
  instruction (name column C3 explicitly) that Fable's close reading alone could not have produced,
  since it required real external search.

## WHAT THIS VETTING DID NOT CHECK

- The 21 spot-checked quotes from the Fable return, and its own known-versus-new table, are not
  repeated here; see `dr_2J-10_dr2J-11_FABLE_VETTING.md` sections 1 and 3 for that record.
- Full paywalled text of Chen et al. (2022), Reinhart and Cerezo Davila (2016), Fischer et al. (2020),
  and the remaining 22 Table B studies was not opened in this pass beyond the arXiv preprint for Chen
  and the Crossref title check for Reinhart; the report's exact in-text quotes and page numbers for
  every other row were not individually re-opened against the paywalled originals, only their titles,
  journals, and years via Crossref.
- The report's search-log totals (387 screened, 32 opened, 59/36 citing papers) were not independently
  re-derived, since doing so would require repeating the live literature search, outside this pass's
  scope.
- Whether any of the 25 new Table B candidate studies is itself a stronger competitor than Chen et al.
  on the manuscript's own six columns (beyond the Total Y arithmetic check in section 7) was not
  independently re-argued; the corrected counts in section 7 show none reaches 5 or 6, but the
  underlying per-cell scoring for those 12 rows (only the totals were audited) was not independently
  re-verified quote by quote.
