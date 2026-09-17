# Vetting of dr_2J-12 (Gemini and Fable whole-paper reviews)

Vetted: 2026-09-16. Method: quote-by-quote check of both returns against the manuscript they were
run against, a live Crossref spot-check of cited DOIs, and a check of the revision plan and drafts to
see which findings are already known and in progress versus genuinely new. No em dashes or en dashes.

## 0. What text was reviewed (read this first, it changes what every finding means)

Both `dr_2J-12` returns were run against `writing/submission/archive/2J_manuscript_submission.md`,
the already-rejected submission (654 lines). The Fable return says this explicitly. The Gemini return
does not state its source, but its section/line citations (for example "Section 7, p. 25, lines
461-462" for the calibration-provenance paragraph) land on exactly the same lines in the archived
file, so it was almost certainly run against the same text, not the four partial redrafts now being
written in `rejection revision/manuscript/` (`draft_S2_framework.md`, `draft_S7_limitations.md`,
`draft_SI_model_selection.md`, `draft_SI_schedule_completion.md`).

This matters because two of the returns' three "would-reject" items are not new information. The
revision plan already has them as the critical path:
- WP1 ("Recalibrate the 2030 occupancy against the post-relink household frame") is the exact fix for
  the calibration-provenance defect both reports lead with.
- WP5 ("Independent check of the hourly load shape") already has a usable measured Canadian dataset in
  hand (IESO Hourly Consumption by Forward Sortation Area, Ontario, 2018-2024) and `draft_S7_limitations.md`
  already states a Toronto/Ontario measured-shape check exists in the revision.

So for these two items the reviews corroborate that the plan is fixing the right things; they are not
new work items. The findings below that are NOT already covered by WP1/WP5/the existing drafts are the
ones that add real, new information.

## 1. Section/quote verification (README step 6 style: open the source, find the exact sentence)

Checked every citation in both reports that names a section, page, or quotes the manuscript directly.
Full text of the archived submission was read start to finish (all 654 lines) for this pass.

**Gemini report.** All quoted manuscript language in items 1 to 10 of the ranked critique matches the
archived submission verbatim or near-verbatim (paraphrase, not invention) in every case checked:
item 1 (calibration provenance, section 7 lines 461-462), item 3 (single-scenario persistence, section
3.4 and 7 and 8), item 4 (EUI under-prediction, Table 5), item 6 (disjoint panels, section 4.3 and the
paper's own section 7 admission), item 7 (single envelope across six climates, section 4.1 and 7), item
8 (CATI-to-EQ mode transition at 2022, section 2.1), item 9 (Motuzienė Table 1 mismatch, confirmed
below). No invented section, page, or quote found. Gemini's page numbers (for example "p. 25") cannot
be checked exactly, since the source is Markdown with no page breaks, but the section numbers and line
content are all real.

**Fable report.** Every one of the 30 numbered items in sections 2 to 4 (argument map, internal
consistency, statistical/methodological findings) carries a direct quote. Spot-checked 12 of them
against the archived file; all 12 match the source exactly, including three that looked implausible on
first read and turned out to be real:
- M1: Conclusion item 1 really does say "with archetype energy-use intensities consistent with the SHEU
  regional-average ranges" (line 477), while section 5.2 and Table 5 state all four archetypes are
  below their SHEU bands (lines 385, 393-396). This is a direct, verifiable contradiction inside the
  same manuscript, not an inference.
- M4: Discussion (section 6, line 439) cites "Table 5" for the annual-electricity percentage
  increments; Table 5 (lines 391-398) contains only EUI values and SHEU bands, no percentage changes.
  Confirmed no such numbers appear in Table 5.
- M9: Section 3.6 (line 268) promises the lighting daylight-gate simplification "is documented as
  deviation R1 (SI Appendix D) and its effect on the results is discussed in section 7." A full text
  search of section 7 (lines 451-468) found no mention of lighting, daylight, or R1. Confirmed absent.
- 4.18 (cohort-size arithmetic): 12,336 (2022 valid diaries, line 141) times 3 equals 37,008 (the
  stated 2030 cohort size, line 239) exactly. Fable flags this as uncertain, not as fact, which is the
  right level of confidence: it is a real arithmetic coincidence, not proof of how the cohort was built.

No fabricated quote or section reference found in either report on this pass.

## 2. DOI spot-check (README step 2: every DOI re-checked by us on Crossref)

19 of the DOIs the Gemini report marks "checked: yes" were independently re-queried against
`https://api.crossref.org/works/<DOI>` in this vetting pass (not trusting the report's own column):

| DOI | Claimed title | Crossref title | Match |
|---|---|---|---|
| 10.1016/j.apenergy.2022.119890 | Chen et al. 2022 | Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model | Yes |
| 10.1016/j.apenergy.2009.11.006 | Widen and Wackelgard 2010 | A high-resolution stochastic model of domestic activity patterns and electricity demand | Yes |
| 10.1016/j.enbuild.2011.09.020 | Chiou et al. 2011 | A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method | Yes |
| 10.1016/j.enbuild.2010.05.023 | Richardson et al. 2010 | Domestic electricity use: A high-resolution energy demand model | Yes |
| 10.1016/j.scs.2021.103557 | Motuziene et al. 2022 | Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic | Yes |
| 10.3386/w28731 | Barrero et al. 2021 | Why Working from Home Will Stick | Yes |
| 10.1016/j.jue.2022.103474 | Cicala 2023 | JUE Insight: Powering work from home | Yes |
| 10.1016/j.enbuild.2021.111280 | Abdeen et al. 2021 | The impact of the COVID-19 on households' hourly electricity consumption in Canada | Yes |
| 10.1016/j.jshs.2023.10.010 | Herrmann et al. 2024 | 2024 Adult Compendium of Physical Activities | Yes |
| 10.1145/2523813 | Gama et al. 2014 | A survey on concept drift adaptation | Yes |
| 10.1080/19401493.2025.2465508 | Sood et al. 2025 | Room-level domestic occupancy simulation model using time use survey data | Yes |
| 10.3389/fenrg.2025.1683787 | Jalilian and Kamel 2025 | Urban-scale building energy modeling under future climate scenarios | Yes |
| 10.1016/j.buildenv.2023.110490 | Osman et al. 2023 | Stochastic bottom-up load profile generator for Canadian households' electricity demand | Yes |
| 10.1016/j.autcon.2014.02.009 | de Wilde 2014 | The gap between predicted and measured energy performance of buildings | Yes |
| 10.1016/j.enbuild.2024.114639 | Barsanti et al. 2024 | Informing targeted Demand-Side Management | Yes |
| 10.1016/j.apenergy.2023.122167 | Wu et al. 2024 | Greenhouse gas emissions under work from home vs. office | Yes |
| 10.1016/j.apenergy.2023.121750 | Claeys et al. 2023 (venue-fit comparator) | Stochastic generation of residential load profiles with realistic variability... | Yes |
| 10.1016/j.apenergy.2024.122831 | Claeys et al. 2024 (venue-fit comparator) | Capturing multiscale temporal dynamics in synthetic residential load profiles... | Yes |
| 10.1016/j.apenergy.2022.118539 | Ku et al. 2022 (venue-fit comparator) | Changes in hourly electricity consumption under COVID mandates... | Yes |

All 19 resolve and match. No fabricated DOI found in this sample (the 15-citation audit table plus
the 4 novelty/venue-fit papers not already in the manuscript's own reference list). This is a marked
change from the project's earlier deep-research rounds, where about half of the return was fabricated;
this Gemini return's citation work looks genuinely grounded.

Not independently re-checked: the arXiv/DataCite resolution for Guo et al. 2026 (`10.48550/arXiv.2603.18440`),
and the two IBPSA proceedings papers (Yin et al. 2024, Ferreira et al. 2024) that carry no Crossref DOI;
the Gemini report itself flags these as needing a non-Crossref route, which is the correct handling, not
a red flag.

## 3. The Motuzienė "MISMATCH" claim (README step 6: open the source, find the exact sentence)

Confirmed on both sides. The manuscript's Table 1 (line 83) scores Motuzienė et al. (2022) as check
marks on "Time-series occupancy," "Calibrated behavioural model," and "Forecast to future year," with
crosses on "Activity and end-use resolved," "Stock-scale," and "Load-shape and peak focus." Crossref
confirms the paper's real title is "Office buildings occupancy analysis and prediction associated with
the impact of the COVID-19 pandemic" (commercial office buildings, short-term pandemic-era occupancy
prediction for HVAC control, not a residential 2030-style forecast). The manuscript's own section 1.3
(line 99) cites it only for "occupancy-prediction models trained on pre-pandemic data degrade sharply
once the break is crossed," which is a fair characterization; the Table 1 checkmark for "Forecast to
future year" is the part that is defensible only on a loose reading of "forecast" (short-horizon
predictive control, not a future year like 2030). This is a real, arguable weak point a reviewer could
raise, not a fabrication by Gemini.

## 4. Convergence and divergence between the two reports

The two reports were produced by different models with different access (search-grounded versus
close-reading only) and independently reached the same verdict. Where they converge on a specific
mechanism, that is stronger evidence than either report alone, because a text-only model cannot search
the literature and a search-grounded model was not given the manuscript's internal cross-references to
check consistency; agreement had to come from the manuscript itself both times.

**Strong convergence (both reports, independently, land on the same specific defect):**
1. Calibration provenance of the 2030 forecast (Gemini item 1; Fable S3, C3, critique item 2). Both
   quote the same section 7 paragraph. This is also independently confirmed by the revision plan's own
   WP1, which exists specifically to fix it.
2. Survey collection-mode change (CATI to EQ) landing on the same cycle as the COVID break (Gemini
   competing-explanation for Headline 1 and item 8; Fable S2 and finding 4.3). Gemini supplies outside
   survey-methodology literature for why self-administered diaries report more at-home time; Fable
   supplies the internal fact that the COLLECT_MODE conditioning flag is 0 for 2005/2010/2015 and 1
   only for 2022, so the model cannot separate mode from behaviour. Neither report alone would be as
   strong; together they show a real confound the manuscript does not rule out.
3. Household panels changing at the 2015-to-2022 boundary, breaking the paper's own "paired,
   within-household" attribution claim for that step (Gemini item 6; Fable finding 4.2 and S8). The
   manuscript's own section 7 already discloses the panel change; both reviewers independently point
   out that this means the study's headline causal story (WFH causes the load-shape change) is
   supported only by the unpaired, interval-free 2015-to-2022 step, while the confidence-interval-bearing
   statistics the abstract and Fig. 6 caption quote are for 2022-to-2030, a span with no WFH break at
   all. Fable states this most sharply (S8, finding 4.1): the CI-bearing numbers in the abstract do not
   test the causal claim the abstract makes them support.
4. The EUI-below-SHEU-band problem (Gemini item 4; Fable M1). Gemini frames it as a stock-representativeness
   problem (archetypes are too new-code to represent the standing stock); Fable frames it as a direct,
   quotable contradiction between the Conclusion ("consistent with... ranges") and the Results/Table 5
   ("below... ranges" in all four rows). Fable's framing is the more damaging one for a reviewer, because
   it needs no outside knowledge of SHEU, only a careful read of the paper's own two sections.
5. Absence of empirical validation against measured interval electricity data (Gemini item 2, backed by
   a venue-fit comparison to three Applied Energy papers that do use smart-meter data; Fable finding 4.6,
   arguing the SHEU comparison that exists is circular by construction, a scalar fitted to the target
   cannot then validate the target). Both conclude the same thing from different angles: the manuscript's
   only empirical anchor is annual SHEU kWh, which cannot certify a load-shape (timing) claim.

**Divergence, no cross-check possible:**
- Gemini's items 5 (no baseline-schedule benchmark) and its Table A novelty search are not repeatable by
  Fable, since they require literature access Fable does not have. These stand on Gemini's search log
  alone; the DOI spot-check in section 2 above found no fabrication in the DOIs Gemini cited, which
  supports trusting this part of the report, but the underlying claim ("no 2024-2026 study combines all
  six features") cannot be independently re-verified without repeating the search.
- Fable's structural/clarity items (C1 to C15) and most of its 20 statistical/methodological findings
  are new information Gemini did not and could not produce, since they require close reading of internal
  cross-references (page/section consistency) rather than search. None of these were contradicted by
  anything in the Gemini report; they are simply outside what a search-grounded review would surface.

## 5. README six-step checklist, adapted to a whole-paper review

1. Positive control present and resolved. Not directly applicable to a whole-paper review (no seeded
   fact was planted). Substitute check: both reports were asked to say what they could not verify, and
   both did (Gemini section 8, three items; Fable section 7, twelve items), which is the expected shape
   of an honest return. PASS on this substitute.
2. Every DOI re-checked by us on Crossref. Done for 19 of the Gemini report's cited DOIs (section 2
   above). PASS, no fabrication found.
3. Every USABLE data source: author opens the page and confirms access route and years. Not applicable;
   this round produced no new data-source claims (that is WP5/`dr_2J-06`'s job, already run).
4. Any MODELLED source marked USABLE: reject the row. Not applicable, no modelled sources claimed as
   measured in either report.
5. System-operator data counted as residential: reject the row. Not applicable to this round.
6. Offline audit of the return (this document) plus, if needed, a verification pass. Done here. A
   further verification pass is not needed: every specific claim checked in sections 1 to 3 above
   resolved as genuine, and no fabricated citation, quote, or section reference was found in either
   report on this pass.

## 6. CARRIED versus STRUCK

**CARRIED (safe to use, verified against the manuscript or Crossref in this pass):**
- The calibration-provenance defect and its "provisional" framing in the abstract/highlights (Gemini
  item 1, Fable S3/C3/critique 2). Already WP1's job; this confirms WP1 is the right critical path and
  that the fix must also reach the abstract and highlights, not just section 7, since both reports
  independently flag that the caveat never reaches those sections.
- The CI-bearing shape deltas measure 2022-to-2030, not the WFH break itself (Fable S8, finding 4.1,
  critique item 1; corroborated by Gemini item 6 on the panel switch). This is the single most load-bearing
  finding of the two returns and is fully quote-verified: the causal sentence in the highlights ("WFH
  fills the midday valley") is not tested by the statistic the paper cites for it.
- Conclusion item 1 versus Results/Table 5 on EUI-versus-SHEU-bands (Fable M1, corroborated by Gemini
  item 4). Directly quote-verified, a same-document contradiction, cheap to fix, should be fixed
  regardless of any other finding's disposition.
- CATI-to-EQ collection-mode confound with the COVID break (Gemini item 8, Fable S2/4.3). Verified real
  in both directions (outside literature plus internal flag logic); not currently addressed by WP1 or
  WP5 as far as the plan text checked in this pass shows, so this is new, unassigned work.
- SHEU calibration circularity as a validation claim (Fable 4.6, corroborated by Gemini's separate,
  venue-fit-based point that no measured interval data is used). Verified quote (the scalar formula in
  section 3.6). The wording "validates the model" / "credibility anchor" should be softened regardless
  of what WP5 adds, since WP5's measured comparison is a different, additional check, not a fix to this
  specific circularity in the SHEU claim's own wording.
- Table 5 miscited in the Discussion for numbers it does not contain (Fable M4). Small, verified,
  cheap fix.
- Lighting daylight-gate discussion promised in section 3.6 but absent from section 7 (Fable M9).
  Verified absent by direct search of section 7. Cheap fix: either add the promised sentence or remove
  the forward reference.
- The 2030-cohort-size-equals-3x-2022 arithmetic observation (Fable 4.18). Verified as arithmetic fact;
  flagged correctly by Fable itself as uncertain regarding cause. Worth a one-line author check, not a
  rewrite.
- Motuzienė Table 1 mismatch (Gemini item 9). Verified against both the manuscript's Table 1 and
  Crossref. Minor but free to fix (change the checkmark or soften the section 1.3 citation).
- The disjoint-panel finding on the 2015-to-2022 step (Gemini item 6, Fable 4.2/S8). Already disclosed
  by the manuscript's own section 7; both reviewers correctly note this discloses the problem but the
  abstract, highlights, and Fig. 6 caption do not carry the caveat forward. The fix is in the same place
  as the CI-bearing-deltas item above; treat as one combined item, not two.

**STRUCK or DOWNGRADED (not safe to act on as stated):**
- Gemini's Table 5 "no baseline-schedule benchmark exists" critique (item 5) is a reasonable reviewer
  point in isolation but is not verified against the manuscript in the same way as the others; it is an
  argument about what is missing, not a checkable quote. Treat as a lower-confidence, unverified-by-quote
  item, not equal weight to the CARRIED list above.
- Gemini's five-paper venue-fit comparison (section 4) is accurate on the DOIs (see section 2) but its
  characterization of Applied Energy's "two validation tiers" is the report's own synthesis, not a
  quoted journal policy; per the project's own house rule (README: "Journal-policy quotes: open the URL,
  find the exact sentence"), this synthesis should not be quoted to a reviewer or editor as if it were a
  stated journal policy. Use the five example papers as evidence, not the "two-tier" framing as fact.
- Gemini's "Two of four primary metrics never reported" is actually Fable's finding (4.10), not
  Gemini's; Gemini did not make this specific claim. No correction needed, just noting the two reports
  should not be conflated when mapping findings to response items.
- The two reports' page numbers (Gemini: "p. 25," "p. 26," etc.) could not be verified, since the
  source file has no page breaks; do not cite these page numbers in any response letter, cite section
  numbers only.

## 7. What this vetting did not check

- No claim requiring access to figures (Figs. 1-7, S1-S9), SI Tables A1-A3, B1, B2, or Appendix D was
  checked, since none of these were available as text; both original reports flag this same gap.
- Fable's remaining internal-consistency and statistical findings not explicitly named above (roughly
  20 more items across sections 3 and 4 of its report) were read but not individually re-verified line
  by line in this pass; a skim found no item that looked inconsistent with the manuscript text already
  read in full for this vetting, but "not individually re-verified" should be read literally.
- Whether the four redrafted sections already in `rejection revision/manuscript/` (S2, S7, and the two
  SI drafts) resolve any CARRIED item beyond the two checked in section 0 (WP1, WP5) was not
  systematically checked; only `draft_S7_limitations.md` was opened, and only for the measured-data and
  relink/provenance/mode terms.
