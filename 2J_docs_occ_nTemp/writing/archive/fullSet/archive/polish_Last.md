# polish_Last.md — Final Polish Pass on `readySubmission.md`

**Date:** 2026-07-02
**Source:** `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` (586 lines)
**Method:** Full manual read + four independent scan passes (numeric consistency, citation integrity, prose/language, journal-submission readiness). All line numbers refer to the current `readySubmission.md`.

**Overall verdict:** The manuscript is numerically airtight and structurally complete — every quantitative claim is consistent across Abstract, body, tables, and Conclusion; all §/Table/Figure cross-references resolve; all 7 figures, 9 SI figures, and 5 tables have captions and image links; the abstract is 233 words (under the 250 cap). What remains is a bounded set of fixes, listed below in priority order. Sections A and B are the ones that matter; C is mechanical sweeps with the decisions already made; D is optional.

---

## A — BLOCKERS (must be resolved before submission)

### A1. Front-matter placeholders (lines 35, 39, 53, 57)
- **Line 35:** department/institute marked "*to confirm*".
- **Line 39:** both ORCIDs marked `[confirm]`.
- **Line 53:** CRediT statement marked "*(draft — confirm/adjust the split)*" — delete the parenthetical once confirmed.
- **Line 57:** the entire italic "*Front-matter notes for the author*" block is a to-do note, not manuscript prose. **Delete it** regardless of the above.

### A2. Keywords: 13 → 7 (line 17)
Elsevier energy journals typically cap at 6–8. Replace the current list with:

> Occupancy Modelling; Building Performance Simulation; Time-Use Survey; Load Shape; Peak Demand; Longitudinal Forecasting; COVID-19 / Work-From-Home

Dropped (redundant or low search value as standalone keywords): Coincidence Factor, Conditional Transformer, Generative Deep Learning, Canadian General Social Survey (GSS), Residential Building Stock, EnergyPlus. Note the spelling fix bundled in: "Occupancy Model**l**ing" — the body is uniformly British ("modelling"), so the keyword should match.

### A3. "NECB/IECC" — wrong code cited (line 366, §5.2)
The text reads "…was set by the **NECB/IECC** envelope and Zone-6 weather…". IECC is the *US* International Energy Conservation Code; the paper states twice (§2.4, §4.1) that the archetypes are NECB 2017 / NBC 9.36 and *not* US prototypes. A reviewer who catches this will question the archetype provenance.
**Fix:** `NECB/IECC` → `NECB 2017 / NBC 9.36`.

### A4. "WFH" never defined (lines 24, 26, 93, 391, 393)
The abbreviation appears in the Highlights and three body locations but is never expanded. **Fix:** at its first body occurrence — line 75, §1.2 — write "…carried through the work-from-home (WFH) break…" (or define at "Work-from-home has settled…" in §1.3, line 100, and spell out the line-93 use). Highlights may keep "WFH" (they are allowed common abbreviations), but the body must define it.

### A5. Orphan reference: Statistics Canada (2026) (line 529 ↔ line 228)
The population-projections reference is in the list but never cited. §3.4 (line 228) mentions "the Statistics Canada M1 medium-growth population projection" with no parenthetical.
**Fix:** "…resampled to the M1 medium-growth population projection (Statistics Canada, 2026)…"

### A6. Prior-line citations missing in §1.4 (line 106)
The departure-point paragraph describes three prior works — "a journal treatment across six Montréal neighbourhood-unit typologies…, a companion conference study…, and a related … framework" — but only the third carries a citation (Iseri, Dino and Kalkan, 2026). The first two were blinded in the source files. **Restore their citations and add the reference-list entries before submission** (a reviewer cannot verify the departure point otherwise).

### A7. SI file coverage (external to this document)
This file references SI material that is *not* in its own appendix (which holds only Figures S1–S9). Verify the separate SI document contains: **SI Table B2** (activity-code crosswalk; cited lines 138, 185), **SI Table B1** (J3 architecture summary; line 199), **SI Tables A1–A3** (end-use crosswalk/calibration parameters; line 253), and **SI Appendix D** (deviation R1, lighting daylight-gate; line 255).

### A8. §6 Discussion and §7 Limitations are single mega-paragraphs (lines 413, 419)
§6 is one ~800-word paragraph; §7 is one ~560-word paragraph. This is the single most reviewer-visible style problem in the manuscript. Insert paragraph breaks at the existing seams — no rewording needed:

**§6 (line 413) — break before each of:**
1. "This positions the work against the nearest competitors…"
2. "The conservative annual-electricity increments are attributional…"
3. "Activity resolution earns its place on two honest grounds…"
4. "The operational reading follows directly…"
5. "For code and standards practice the implication is sharper still…"
6. "Finally, the paired within-household Monte-Carlo design…"

**§7 (line 419) — break before each of:**
1. "Of the standing scope limitations, the metabolic…"
2. "Two resolution choices simplify the temporal representation…"
3. "The simulation also holds a single Montréal Zone-6 envelope…"
4. "The Census–GSS linkage is a statistical match…"
5. "The four GSS cycles span a collection-mode transition…"
6. "Finally, the 2030 forecast is generated under a single scenario…"

Additionally, the opening sentence of §6 runs ~190 words. Split it after "…the annual total —" into: "…rather than the annual total. The present results fill it with a specific and partly counter-intuitive finding: …"

---

## B — REVIEWER-RISK FIXES (should fix)

### B1. Four near-verbatim duplicated passages
The manuscript states the same content twice in four places. Keep one full statement, replace the other with a cross-reference:

| # | Duplicated content | Keep (full) | Replace (with pointer) |
|---|---|---|---|
| 1 | Three-competitor matrix reading (Chen retrospective / Yin stops at analysis / Jalilian static) | "**Reading of the matrix**" paragraph after Table 1 (line 93) | §1.2 pre-table sentence "Read across the matrix, … load shape." (line 75) — **delete it**; the paragraph flows directly from "…gap matrix of Table 1 makes explicit" into the open-cell sentence |
| 2 | 14-category mapping (182/264/64/121 codes, zero conflicts) + co-presence OR-merge | §3.1 (line 185) — this is Methods material | §2.1 (line 138): replace the two sentences "Raw activity codes are harmonized… (SI Table B2)." and "Co-presence is OR-merged… masked for those cycles in the generator." with: *"Raw activity codes and co-presence columns are harmonized to a common 14-category scheme and nine unified channels as described in §3.1."* |
| 3 | Metabolic MET mapping (70 W/MET, 60 kg, ASHRAE 55/ISO 7730, ~83 W/MET) | §3.5 (line 238) | §4.2 (line 291): replace the two sentences with: *"Metabolic heat gain is mapped from the 14 activity categories to per-person watts via the conservative 70 W/MET basis described in §3.5."* |
| 4 | Donor-draw completion (copy-day −2.76 pp artefact) | §3.5 (line 240) | §4.2 (line 295): replace the first two sentences with: *"Households missing an observed day-type receive the donor-draw completion described in §3.5, preserving the calibrated weekend marginal."* — keep the rest of that paragraph (Step-7 scorecard, 78.48 % vs 78.44 %), which appears only here |

### B2. §1.2 "rarely meet" said three times (line 75)
"…and they rarely meet." → two sentences later "The two tracks rarely meet, a disconnection that…" (and the subsection title says it a third time). With the B1-#1 deletion, also reword the second occurrence, e.g.: *"Table 1 makes this disconnection explicit as a six-dimension gap matrix."*

### B3. Highlights at the 85-character limit (lines 24, 26)
Highlights 2 and 4 sit at exactly 85 characters — zero margin if Elsevier's counter differs by one. Safer rewrites:
- H2 (84): `2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test.`
- H4 (82): `WFH fills the midday valley and flattens load; the evening peak near 17:30 holds.`

### B4. Spelled-out numbers conflicting with numerals for the same statistic
- **Line 10 (Abstract):** "Six thousand paired EnergyPlus runs — …" — recast to avoid the sentence-initial numeral while matching "6,000" used everywhere else: *"A campaign of 6,000 paired EnergyPlus runs — the same 50 households across five cycle-years, with archetypes and weather frozen — isolates the pure occupancy effect…"* (note *isolates*, singular, agreeing with *campaign*). **[UPDATE 2026-07-13: this suggested rewrite predates the two-panel correction — do NOT apply "the same 50 households across five cycle-years" verbatim. The current canonical wording (`2J_full_manuscript.md` Abstract) is: "fixed 50-household panels held constant within each of two cycle-year spans (2005-2015; 2022-2030), with archetypes and weather frozen throughout" — apply the sentence-initial-numeral fix (if still wanted) against that text instead.]**
- **Line 114:** "more than forty trials" → "more than 40 trials".
- **Line 115:** "all forty-eight dwelling-by-year cells" → "all 48 dwelling-by-year cells".
- **Line 117:** "the same fifty households" → "the same 50 households" (superseded — this phrase itself was replaced by the two-panel wording; see the note above).

### B5. Internal pipeline jargon leaking into the paper
- **"Phase 8B calibration" (line 201):** the phase number is meaningless to readers (there is no Phase 1–8A in the paper). Fix: "…marginal raking step — **the post-hoc calibration stage** — snaps the AT_HOME marginals…".
- **"Step-6 / Step-7 / Step-9 validation scorecard" (lines 230, 295, 257):** Figure 1's caption declares Steps 1–9, but the prose never maps numbers to stages. Lowest-risk fix: replace with stage names — "the **forecasting-stage** validation scorecard" (line 230), "**Schedule-integration** validation" (line 295, already half-done), "the **end-use-layer** validation scorecard" (line 257). "Step-4"/"Step-5" in §2 (lines 138, 152, 161) same treatment ("the generative augmentation step (§3.2)", "the Census–GSS linkage (§3.3)").
- **`BEM_Schedules_2022.csv` filenames (lines 289, 324):** generalize to "the per-cycle-year schedule files" (a reviewer may ask why internal filenames are published; keeping them is defensible if the data availability statement will name them — your call, low stakes).
- **"occACT" (lines 138, 185):** expand once: "a common 14-category occupant-activity (occACT) scheme".

### B6. Table 1: the de Wilde (2014) row (line 83)
A framework/review paper scoring ✗ on all six dimensions is an odd "competitor" — it anchors the performance-gap motivation, not the capability comparison, and a reviewer may ask why it is in the matrix. Recommend **dropping the row** (the citation stays in §1.1) or footnoting it as the motivating-framework baseline.

---

## C — GLOBAL MECHANICAL SWEEPS (decisions made; apply with find-and-replace)

### C1. Spelling: adopt Oxford spelling (-ize + behaviour/modelling)
The body is 100 % British for -our/-elling (behaviour, modelling, labour, artefact — zero exceptions) but mixes ~32 "-ize/-ization" tokens with ~18 "-ise/-isation" tokens. **Decision: convert the 18 minority s-forms to z-forms** (Oxford spelling — fully journal-legitimate, fewer edits, and consistent with the z-forms already baked into figure captions and likely the figure artwork itself):

| Change | Lines |
|---|---|
| recognised → recognized | 69, 419 |
| characterises → characterizes | 75 |
| synthesise → synthesize | 106 |
| summarised → summarized | 119, 197, 199, 263 |
| operationalises → operationalizes | 119 |
| destabilising → destabilizing | 199 |
| initialisation → initialization; reinitialising → reinitializing | 224 |
| materialised → materialized | 236, 289 |
| standardising → standardizing; standardised → standardized | 242 |
| organised → organized | 263 |
| generalisation → generalization | 271 |

**Do NOT touch:** "Harmonised European Time Use Surveys" (line 471 — Eurostat's actual title), "International Organization for Standardization" (line 485 — ISO's legal name), CRediT terms "Conceptualization/Visualization" (line 53 — fixed taxonomy vocabulary), and any spelling inside quoted reference titles (lines 483, 487, 489, 491, 495, 507, 515, 539, 541, 543). Keep behaviour/modelling/labour/artefact exactly as they are.

### C2. Percent spacing: close up everywhere ("2.7%", not "2.7 %")
The manuscript splits by section (§2–§4 + Highlights + Table 5 body unspaced; Abstract, §1, §5, §7, §8, Table 5 note, SI captions spaced). **Decision: unspaced**, matching common Elsevier typesetting and avoiding bad line-breaks. Fix the spaced instances at lines: 10, 69, 75, 93, 100, 106, 115, 119, 351, 353, 364, 366, 380, 389, 401, 413, 419, 429, 433, 435, 551, 555, 567, 571. Verification probes after the sweep: line 27 vs 115/380/429 (±2.7%), line 214 vs 419/555 (match tiers), line 197 vs 551 (2%→20%→100%) must all match.

### C3. Em-dash convention: spaced " — " everywhere
The whole manuscript uses spaced em-dashes **except §5** (22 unspaced instances at lines 345, 351, 366, 387, 389, 391, 401, 403 — line 401 even mixes both in one line). Fix §5 to spaced (22 edits) rather than the reverse (83 edits).

### C4. "-ly adverb + hyphen" errors (6 fixes)
- Line 230: demographically-standardized → demographically standardized
- Line 263: fully-specified → fully specified
- Lines 403, 413, 435: behaviourally-timed → behaviourally timed
- Line 425: behaviourally-grounded → behaviourally grounded

### C5. Small local fixes
- **Line 387:** "remains between 17.5 and 17.7 h (17.51–17.71 h across years)" — redundant double-precision. Use: "remains within a narrow 17.51–17.71 h band across all years".
- **Line 115:** "an SHEU-calibrated" → "a SHEU-calibrated" (SHEU read as a word; every other use is "the SHEU" so this is the only instance).
- **Line 106:** terminology drift "hard-gate-selected" (§1.5) vs "gate-selected" (Abstract, Highlights, §3.2). Standardize on **"gate-selected"**.
- **Line 413:** "≈ +12%" but "~17:30" in the same paragraph — standardize approximations on "~" in running prose (matches the Abstract and §5 usage).

---

## D — MINOR / OPTIONAL (won't attract reviews, fix if convenient)

1. **Reference formatting:** four DOIs missing the trailing period used elsewhere (lines 457, 465, 477, 511); Statistics Canada (2026) lacks an accessed date while the other four web sources carry one (cf. lines 503, 523, 525, 527).
2. **Alphabetization:** "de Wilde" filed under D (line 467) — an accepted variant; leave unless the target journal's guide says otherwise.
3. **Heading hierarchy:** body uses `#` chapter → `###` subsection (skips `##`). Irrelevant after conversion to the journal template; only matters if the markdown is rendered directly.
4. **Table 4 structure:** one caption over "Section A / Section B" sub-tables plus a summary block (lines 309–331) — unconventional; check the journal's table rules allow it, or merge into a single two-column "Held / Varied" table.
5. **Abstract style:** 233 words, compliant. It is dense with parenthetical statistics; acceptable for this venue — no change required.
6. **Wilke et al. (2011) reference (line 535):** proceedings entry has no page numbers or URL/DOI — add if available.

---

## E — VERIFIED CLEAN (no action needed)

- **Numeric consistency:** every repeated quantitative claim checks out across Abstract/Highlights/body/tables/Conclusion — diary counts (64,061 = 19,221+15,114+17,390+12,336), 286,537 agents, 144,507 households, 37,008-row 2030 cohort, 6,000 = 4×6×5×50 runs, 4,800/4,795 Step-9 runs, at-home series and all deltas (+6.1/+6.6/+5.2 pp; +2.2–3.9 pp), energy deltas (+1.4–2.6%; +0.6–1.2%), load-shape stats (+0.367 pp ≈ +0.37; +0.0117 ≈ +0.012; 17.5–17.7 h; 0 ± 1 h), SHEU targets and ±2.7% (max +2.33/+2.63%), EUIs (208/152/128/117; ×1.11 → ≈168/≈130), J3 gates (0.0191/4.57/2.03/0.6355 vs thresholds), MDLM (0.559, 7.81 pp), TFT (0.0619 < 0.20; 0.0630 < 0.10), match tiers and stock shares (both sum to 100%), MC precision (1.80%/4.04%), and all scorecards.
- **Citations:** every in-text citation (including all Table 1 rows) has a reference entry; the only orphan is A5 above; alphabetical order OK.
- **Cross-references:** every §, Table 1–5, Figure 1–7, and Figure S1–S9 mention resolves within this file; all figures/tables have captions and image links.
- **British -our/-elling spelling:** fully consistent in body text (American forms appear only inside quoted reference titles, which is correct).
- **Decimal/thousands separators:** consistent throughout.

---

*End of polish pass. Suggested application order: A1–A8 first (blockers), then B1–B6, then run the C sweeps in one editing session (C1 spelling → C2 percent → C3 dashes → C4 hyphens → C5 locals) so the verification probes in C2 stay valid.*
