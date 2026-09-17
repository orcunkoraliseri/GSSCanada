# Deep-research prompts for the revision round (2026-09-15)

Run externally by the author. Paste each `*_prompt.md` as-is. Save the return next to it as
`dr_2J-0N_..._results.md`. Numbering continues the first round (`../../deepReserchPrompts/`, 01 to 05).

| Prompt | Question | Feeds |
|---|---|---|
| `dr_2J-06_measured_hourly_load_data_prompt.md` | Does measured hourly residential electricity data exist for Canada, 2019 to 2023, and can we get it? | Plan WP5, venue choice |
| `dr_2J-07_validation_bar_by_venue_prompt.md` | How often do recent matching papers at Applied Energy, SCS and JBE actually check hourly shape against measured data? | Venue choice |
| `dr_2J-09_existing_stock_envelope_prompt.md` (added 2026-09-15) | Measured wall, ceiling, window and air-tightness values of the existing Canadian single-detached stock | Plan WP7 step 3, task T31. Rule fixed in advance in `../impl/2026-09-15_T31_wp7_existing_stock_envelope.md`: MEASURED before SURVEY, never ASSUMED or code values; any of the four NOT FOUND means WP7.3 is not run and the one-envelope limitation is stated |
| `dr_2J-09b_envelope_verification_prompt.md` (added 2026-09-15) | Verification pass over the dr_2J-09 return: copy the printed rows of Swan (2010) Tables 3.4, 5.9, 5.10, 7.2, Khemet and Richman (2018), CanmetENERGY Slide 20; DOIs; CONFIRMED / CORRECTED / NOT FOUND | T31 value selection, rules fixed in `../impl/2026-09-15_T31_wp7_existing_stock_envelope.md` (manager vetting section). **Returned and applied 2026-09-15 (plan log (aq)): window U/SHGC NOT FOUND, WP7.3 not run** |
| `dr_2J-10_novelty_matrix_search_gemini_prompt.md` (added 2026-09-15, split into Gemini/Fable 2026-09-16) | Adversarial live-search: does any real study combine all six features of our novelty table? Re-scores the existing rows and Barsanti et al. (2024) | Plan WP12.3(a) and WP12.4; Introduction Table 1 in WP10. BROKEN = rewrite the gap claim; NARROWED = name the missing column in the text; HOLDS = keep the table with the re-scored rows |
| `dr_2J-10_novelty_matrix_search_fable_prompt.md` (added 2026-09-16) | No-search close-reading audit of our OWN novelty argument: internal consistency, circularity/overclaiming check, does the six-column scheme get applied consistently to the named competitors | Same feeds as the Gemini version, but checks argument soundness rather than external fact; run alongside it, not instead of it. **Returned 2026-09-16 as `dr_2J-10_novelty_matrix_search_fable_results.md` (Fable in Claude Code, reviewed the SUBMITTED text in `../../archive/`, same basis as dr_2J-12 Fable). Verdict HAS A STRUCTURAL PROBLEM: the six-column "open cell" is conceded (§1.2 para 2) not to separate the paper from the authors' own C-VAE work, which the matrix excludes by fiat; no column criteria stated, 6 of 9 rows unsupported by prose; Chiou ✗ / Yin ✓ in "Calibrated behavioural model" inconsistent with the manuscript's own descriptions; prose claim adds unscored qualifiers (through the break, paired). UNVETTED, 7-step vetting owed (step 7, offline audit, is the operative one: no external claims to check)** |
| `dr_2J-11_wfh_trajectory_and_tradeoff_gemini_prompt.md` (added 2026-09-15, split into Gemini/Fable 2026-09-16) | Home-working levels 2019 to now and published outlooks to 2030, from live search; home versus office energy trade-off from published studies | Plan WP12.3(b)(c); WP2 scenario justification and the system-boundary paragraph in WP10 |
| `dr_2J-11_wfh_trajectory_and_tradeoff_fable_prompt.md` (added 2026-09-16) | No-search close-reading audit of our OWN WFH-scenario argument: single-scenario vs. bracketed-range wording consistency, and whether the manuscript discloses the residential-only system boundary anywhere | Same feeds as the Gemini version, but checks argument soundness rather than external fact; run alongside it, not instead of it. **Returned 2026-09-16 as `dr_2J-11_wfh_trajectory_and_tradeoff_fable_results.md` (Fable in Claude Code, reviewed the SUBMITTED text in `../../archive/`, same basis as dr_2J-12 Fable; the S2/S7 redrafts noted separately at the end). Verdict HAS A STRUCTURAL PROBLEM: the scenario holds WFH fixed after 2022 ("persists with probability one", §7 para 9) so the 2022 to 2030 leg, the only one with CI-bearing shape deltas, contains no WFH change yet is labelled the WFH effect; the one 2030 number "+2.2 to +3.9 pp" is a level above pre-pandemic in four places and the 2022 to 2030 step in §7 para 5; §3.4 promises a sensitivity bound in §7 that §7 never delivers; Highlights call the 2030 forecast "validated". System boundary: NOT FOUND, no residential-only or office/commercial sentence anywhere (also absent from the S7 redraft). UNVETTED, 7-step vetting owed (step 7, offline quote spot-check, is the operative one)** |

| `dr_2J-12_whole_paper_review_gemini_prompt.md` (added 2026-09-16) | Adversarial whole-paper review, Gemini version: live-search-grounded novelty check, citation audit, venue fit, reviewer critique | Pre-submission review only; requires the full manuscript pasted/attached by the author, not provided here. **Returned 2026-09-16 as `dr_2J-12_whole_paper_review_gemini_results.md`, verdict REJECT-LIKELY, reviewed the SUBMITTED text (same as Fable). VETTED 2026-09-16 (plan log (bf)): 19/19 spot-checked DOIs resolved on Crossref, no fabrication found, all quoted sections genuine — see `dr_2J-12_VETTING.md`** |
| `dr_2J-12_whole_paper_review_fable_prompt.md` (added 2026-09-16) | Adversarial whole-paper review, Fable version: no external search, close reading only (argument map, internal consistency, statistical soundness, structure) | Same as above; run alongside the Gemini version, not instead of it. **Returned 2026-09-16 (plan log (be)) as `dr_2J-12_whole_paper_review_fable_results.md`, reviewed the SUBMITTED text in `../../archive/`, not the redrafts. Verdict REJECT-LIKELY; top item: the CI-bearing shape deltas are 2022 to 2030, not the WFH break. VETTED 2026-09-16 (plan log (bf)), all 12 spot-checked quotes genuine — see `dr_2J-12_VETTING.md`** |
| `dr_2J-12_VETTING.md` (added 2026-09-16) | Joint 7-step vetting of both dr_2J-12 returns: quote verification, Crossref DOI re-check, cross-report convergence, CARRIED/STRUCK list | **Verdict: REJECT-LIKELY survives vetting.** Two headline items corroborate WP1/WP5 (not new); CARRIED findings folded into `00_REVISION_PLAN.md` §5 items 10-15 and the new "currently unassigned work" note (WP1 + WP10) |

| `dr_2J-13_sheu_enduse_split_gemini_prompt.md` (added 2026-09-17) | Measured/survey residential end-use energy split for Canada (space heating, water heating, appliances, lighting, cooling), units and denominator explicit | Plan WP7 step 2 (T44). Gemini only, no Fable twin (no-search hunt for published numbers is worthless). Rule fixed in advance in `../impl/2026-09-17_T44_dr2j13_enduse_split_prompt.md`: unambiguous split with denominator -> full breakdown; shares only -> report shares only; space heating NOT FOUND -> breakdown not run at all; our simulated values are never rescaled |

(`dr_2J-08` is reserved for the pre-submission audit, plan §10 Wave 5, written only after the package is built.)

**Run 06 first.** 07 is only needed if 06 comes back PARTLY USABLE or empty.

**Confidentiality.** The rejection letter is confidential. The prompts contain no reviewer text and
must not be edited to add any.

## Vetting before anything is used (the first round was about half fabricated)

1. Positive control present and resolved? If not, discard the whole return.
2. Every DOI re-checked by us on Crossref.
3. Every USABLE data source: the author opens the page and confirms access route and years.
4. Any MODELLED source marked USABLE: reject the row.
5. System-operator data counted as residential: reject the row.
6. Journal-policy quotes: open the URL, find the exact sentence.
7. Offline audit of the return, then, if needed, a verification pass prompt (as `dr_2J-05` did).

## Decision rule (agreed in advance so the result cannot be argued after)

| `dr_2J-06` outcome after vetting | WP5 action | Venue |
|---|---|---|
| At least one USABLE Canadian source covering 2021 to 2023, in hand within about 2 months | Build the measured vs simulated 2022 comparison | **Applied Energy** |
| Only PARTLY USABLE (published profile values only, or no heating-fuel split, or non-Canadian substitute) | Build the partial comparison, state its limits | Read `dr_2J-07`: Applied Energy only if its sample shows matching papers accepted with a similar partial check; otherwise **Sustainable Cities and Society** |
| NOT FOUND, or access longer than about 2 months | Narrow the load-shape claim (plan WP5 fallback) | **Sustainable Cities and Society** (declare the Concordia editor conflict), **Journal of Building Engineering** if that conflict is unroutable |

Record the outcome and the chosen venue in `../../02_journal_options.md` and in `../00_REVISION_PLAN.md` §8.
