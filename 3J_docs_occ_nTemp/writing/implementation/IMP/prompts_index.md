# PROMPTS work package - index of the four deep-research prompts written 2026-09-22

Source task: `writing/implementation/3J_IMP_execution_2026-09-22.md` section "PROMPTS", plan
`writing/submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md` Sections 2, 3, 5 (P6, P7, P8)
and 7a (V1, V2). None of these prompts were run; the author runs each in Gemini Deep Research and saves
the return beside the prompt as `RV<NN>_...md`, then the manager vets it before anything is quoted.

## The four prompts

| File | Unblocks | What it asks for |
|---|---|---|
| `deepResearch_Resources/V11_3J_equation_sources.md` | P6 | A source for every equation in the Methods chapter not yet sourced: the multi-task training loss (PCGrad, SLAW, uncertainty weighting, fixed-weight scalarization, class-imbalance logit correction), the checkpoint-selection composite, the exclusivity projection, the SARIMA hotel side-track and its COVID indicator, EUI on two floor-area bases, REPLACE-vs-MODULATE injection, the coincidence factor, and the weekday day/night ratio. Also asks it to confirm two equations (circular-mean and circular-standard-deviation peak hour) still using the sources already vetted for 2J's `dr_2J-17`, rather than re-searching from zero. |
| `deepResearch_Resources/V12_3J_literature_novelty_references.md` | P7 | Tries to break Table 1's novelty claim (searches for a competitor combining time-use-survey-driven, multi-channel, forecast-to-future-year, mixed-use-single-building); names the closest competitor either way; finds motivation sources for why peak timing matters (plant sizing, shared central plant, district/grid peaks); sources the two unsourced §1.3 claims (international retail/e-commerce decline, persistent post-2022 hybrid work); re-verifies all 18 existing references; fills the five "not reported" reference gaps (ASHRAE Guideline 14 edition, CBRE report identifier, ISQ table identifier, SCIEU year/table, DOE/PNNL prototype release). |
| `deepResearch_Resources/V13_3J_measured_hourly_occupancy_and_load.md` | P8 + V2 | Measured hourly presence or load data per use type (residential, office, retail, hotel, mixed-use), Canada or comparable cold climate, for an independent check of the manuscript's weekday peak hours and coincidence factor. Requires the data to be independent of both the GSS Time-Use survey (what residential/office/retail were trained on) and the ISQ/CBRE hotel-occupancy series (what the hotel SARIMA side-track was fit to); asks for access, licence, resolution and years for every candidate, and whether an hourly weekday profile can actually be extracted. |
| `deepResearch_Resources/V14_3J_measured_annual_eui_canada.md` | V1 | Measured (metered/billed, not simulated) annual EUI by building use in Canada: Montreal's large-building disclosure open data, Toronto/Calgary benchmarking if they exist, ENERGY STAR Portfolio Manager Canadian medians, NRCan SCIEU tables, and any other Canadian measured-EUI source, to check the three failing gate bands (office, hotel, retail) against real measured Canadian buildings, independent of the as-modelled bands already in the manuscript. States plainly that the frozen gate verdicts are not to be changed by anything this prompt returns. |

All four: paste `deepResearch_Resources/00_MASTER_BRIEF_V2.md` ahead of the prompt; answer in the
schema of `deepResearch_Resources/_RESPONSE_TEMPLATE.md` (Sections A-H); every prompt demands a URL or
DOI for every item ("items without a working link are discarded") and states plainly that fabricated
citations are expected in the returned report and will be checked one by one before anything is quoted.
No em dashes or en dashes; reference bands and gate verdicts stay frozen regardless of what any prompt
returns.

## The 7-step vetting the manager applies to every RV<NN> return before anything is quoted

(the standing practice this project already uses, for example `2J_docs_occ_nTemp/.../dr_2J-17_VETTING.md`
and `3J_docs_occ_nTemp/deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md`)

1. Open every DOI/URL the report gives, via Crossref for DOIs and by loading the landing page or portal
   directly for everything else; drop anything that does not resolve to the claimed source.
2. Check the search log is present and non-empty; a "nothing found" claim with no queries listed is
   treated as not run, not as a negative result.
3. Cross-check every quoted number or definition against the source actually opened, not against the
   report's paraphrase of it.
4. Confirm basis separation held: as-modelled figures and empirical/measured figures were not blended,
   and no reference band was recommended to move because this project's own model fails it.
5. Flag every internal contradiction and every place the report disagrees with another vetted response
   already on file (for example `V09`'s two disputed DOIs, or 2J's already-vetted circular-statistics
   sources reused in `V11`).
6. Mark every finding Tier 1/2/3 and record whether it was read in full text, abstract only, or could
   not be opened; anything not opened is not citable yet.
7. Write the vetting result to its own file beside the prompt (`V<NN>..._VETTING.md`, following the
   `VETTING_RV09_RV10_2026-08-08.md` pattern), listing accepted items, rejected items and why, before any
   accepted item is written into the manuscript.
