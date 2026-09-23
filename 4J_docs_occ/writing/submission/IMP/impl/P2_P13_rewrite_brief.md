# P2 + P1 + P4 + P12 + P13 — the rewrite (brief, 2026-09-23, manager)

**Status:** brief written; execution delegated to one writing agent. State of the work lives in the
execution log at the end of this file (append, newest last).

## Inputs (read these, in this order)
1. Plan: `writing/submission/IMP/4J_improvement_plan_from_2J_lessons_2026-09-22.md`, sections "Rules",
   3 (problems 1-13), 4 (the 15 comments), 5 (P2, P1, P4, P12, P13).
2. Journal rules: `writing/submission/IMP/impl/P14_journal_guide_EandB_2026-09-23.md`.
3. Numbers: `writing/submission/IMP/prep/results_number_sheet.md` (fix every MISMATCH listed there).
4. In-sample result: `writing/submission/IMP/impl/P10_in_sample_vs_transfer.md` (label order confirmed).
5. Appliance result: `writing/submission/IMP/impl/P3_appliance_real_and_donor.md` (the result table and
   the decision-rule outcome are appended there; follow the rule's branch exactly).
6. Intervals: `writing/submission/IMP/impl/P5_intervals_table3.md`. The job is still running. Leave
   Table 3's interval column as the literal marker `[P5]` in each cell and one marked sentence in 2.6;
   the manager fills them later.
7. Sources: `DeepResearchPrompts/VETTING_RL34.md`, `VETTING_RL35.md`, `VETTING_RL36.md`. Only items
   marked ACCEPTED may be cited. Items "accept after open" are cited only in the form the vetting file
   allows (for Jutras-Dubé et al. 2024: the one metadata sentence in VETTING_RL35 section 5, nothing more).
   TABULA internal-gain value: cite the IWU TABULA calculator workbook as in VETTING_RL34 line ~259, and
   Loga et al. 2016 for the typology only. Never the TABULA Synthesis Report. Nothing numeric from RL36.
8. The current manuscript `writing/submission/4J_manuscript_submission.md` (~18,650 words) and SI
   `writing/submission/4J_supplementary_material.md`.

## Before any edit
Archive both files to `writing/submission/previous/` with suffix `.pre_rewrite_20260923` and check the
copies are non-empty (`[ -s file ]`). Never edit the .docx by hand.

## Targets
- Title (D2): "Can a fine-tuned language model generate time-use diaries for a country without survey
  data? A pre-registered test against reweighted real diaries".
- Main text (Introduction to Conclusion) about 7,500 words (D5). Discussion about 1,200, Limitations about
  900. Every limitation point kept: build a checklist of the current §7 points at
  `writing/submission/IMP/prep/limitations_checklist.md` and tick each one against its new home (main or SI).
- Structure exactly as the P2 table in the plan (1 Intro in three parts; 2.1-2.6 Methods; 3.1-3.7 Results;
  4 Discussion; 5 Limitations; 6 Conclusion; Nomenclature; Appendix A = Table 1; Appendix B = equations;
  declarations; References). Heading levels numbered 1, 1.1 (fix the H1-then-H3 problem).
- Abstract at most 250 words, no labels, no undefined abbreviations. Keywords 1-7.
- Highlights: 3-5 bullets, at most 85 characters each, in a SEPARATE file
  `writing/submission/4J_highlights.md` (purpose, finding, benefit). Remove from the manuscript.
- Declarations at the END, before References, in Elsevier order: CRediT, competing interests, funding
  (spelling "Volt-Age Seed Fund", as in the revised 2J; check 2J's text before copying), data statement
  (HETUS/UKTUS microdata cannot be redistributed; code, frozen pre-registration and its hash to be
  deposited at submission), "Declaration of generative AI and AI-assisted technologies in the manuscript
  preparation process" (draft wording; the author confirms), acknowledgements directly before References.
- Pre-registration wording (D4): "registered internally before training (hash-locked, 2026-08-18) and
  deposited at submission". No registry link invented.
- One sentence on sex/gender (sex is a conditioning stratum; not analysed separately).

## Content rules
- Headline factor 1.1 to 3.9, never "2 to 6". 320 collision cells stay excluded. No gate verdict, band or
  measured number changes. Every number in the new text must appear in the number sheet (or in P3/P10
  files); after writing, list any number that does not.
- Name the backbone model and its version (from the training record; SI S2 too).
- Delete the §3.4 internal instruction (lines ~332-334, "never to be ... 36 of 36") and every meta
  sentence, process-history sentence and "stated here rather than" phrasing. Journal, not report.
- "UK", never "Britain". "Limitation", never "failure", in prose; tables keep FAIL.
- Jargon inventory first, at `writing/submission/IMP/prep/jargon_inventory.md` (list in plan P1):
  replace or define each term once ("check" for gate, "tolerance" for band, "held-out country" for fold,
  "baseline" for null...). Round excess precision in text (exact values to SI).
- Replace "the author searched ... 2026-09-13" with citations; at most one sentence on search scope.
- §1.3 anecdote (thirteen-year-olds) to SI; keep the principle.
- Move to SI: §3.8 phase-error story (one Methods sentence stays), §6.6 lessons, §7.10, check tallies
  from §3.1-§3.4, the 410-cell record, documentation-defect notes, §4.4 campaign detail (one sentence stays).
  Tables and figures that are not load-bearing go to SI too.
- P10 in Results 3.1: two sentences (model also misses the absolute bar on its training countries,
  in-sample worst-band MAPE 33-158 % against a 15 % bar that real diaries meet at 5-12 %). Claim narrows
  as in P10. Table 4 remains the evidence.
- P4 reframe: the transfer verdict and the diagnostic are the paper; building half = appliance timing
  (as the P3 rule decides), heating null, the checks that did not pass in one short paragraph with their
  reason; one sentence that the transfer conclusion does not depend on any downstream check.
- P12: keep the existing self-citation; one funding spelling.
- Sentences about 20-25 words, one idea each. After writing, run a script that lists every sentence over
  30 words in the main text and fix or justify each.
- Never create images. Figures stay as they are; captions one sentence; move "how to read" text into prose.

## Deliverables
- New `writing/submission/4J_manuscript_submission.md` and updated `4J_supplementary_material.md`.
- `4J_highlights.md`; `prep/jargon_inventory.md`; `prep/limitations_checklist.md`.
- A word count per section (main text) appended to the log below.
- Do NOT rebuild the docx and do NOT run the P9 second pass; the manager does both.

## P3 outcome (manager, 2026-09-23; binding for the rewrite)
Decision rule gave **branch 2: the claim narrows.** Read the "result" entry at the end of
`P3_appliance_real_and_donor.md` and follow its "Wording limits" list exactly. In short:
- Remove the "six-hour spread" claim everywhere (Abstract, Results, Discussion, Conclusion, Highlights).
- Table 7 becomes a three-source table (generated / unweighted real / raked donor) using the values in the
  P3 result table (watts to one decimal; generated watts are 502.9 / 403.5 / 416.1, NOT 518 / 395 / 422).
- The result sentence: unweighted real diaries put the evening peak at 18:00-21:00 (UK 18:00, Italy 19:00,
  Spain 21:00); the generated diaries give a different order (Spain 14:00, Italy 18:00, UK 20:00), and the
  raked donor diaries put all three at 19:00-21:00; so neither synthetic source carries country timing.
- Peaks are flat-topped (runner-up hour within 1-8 %); no ranking on one-hour differences.
- The reproduction check detail (one 0.001 kWh rounding cell) goes to SI only, one sentence.
- Highlights and Conclusion follow this branch.

## Execution log (append below; newest last)

### 2026-09-23 — rewrite executed (writing agent, Opus)

**Archive.** `writing/submission/previous/4J_manuscript_submission.md.pre_rewrite_20260923` (116,858 B) and
`previous/4J_supplementary_material.md.pre_rewrite_20260923` (15,076 B), both checked with `[ -s ]` before
any edit. No .docx touched, no build, no P9 second pass, no compute, no web access.

**Files written.** New `writing/submission/4J_manuscript_submission.md` (481 lines); rewritten
`4J_supplementary_material.md` (S1-S12, 7,307 words); new `writing/submission/4J_highlights.md` (5 bullets,
80-85 characters each, highest 85); `IMP/prep/jargon_inventory.md`; `IMP/prep/limitations_checklist.md`.

**What changed (main text).**
- Title (D2). Highlights, graphical abstract and front-matter declarations removed from the manuscript;
  declarations now at the end in Elsevier order (CRediT, competing interest, funding with "Volt-Age Seed
  Fund", data availability, generative-AI declaration draft, acknowledgements), then References.
- Structure as the P2 table: 1.1-1.3; 2.1-2.6; 3.1-3.7; 4 (4.1-4.5); 5; 6; Nomenclature; Appendix A
  (Table A.1 plus a scoring sentence per column); Appendix B heading with the marker `[APPENDIX B]` (per the
  coordinator's message; my own draft appendix was removed). Headings: H1 for sections, H2 for 1.1-style.
- Abstract rewritten, no labels, 248 words. Keywords 7.
- Backbone named: OLMo 3 7B (`allenai/Olmo-3-1025-7B`), OLMo 2 1B, Qwen2.5-7B; revisions in SI S2
  (from `Step4_docs/4thJ_04_finetuneLLM.md:192-196`).
- P3 branch 2 applied: "six-hour spread" removed everywhere; Table 5 (old Table 7) is three-source with
  502.9 / 403.5 / 416.1 W generated; the result sentence, flat-top wording, Spain midday note and
  "unweighted real diaries" as in P3's wording limits; reproduction detail (0.001 kWh) in SI S7.5 only;
  no-interval point in Limitations only; Highlights and Conclusion follow.
- P10 two sentences in 3.1 (33-158 % against 15 %, real diaries 5-12 %), claim narrowed; Table S2 in the SI
  carries the six in-sample cells (fold/training-country order as confirmed in P10).
- P4: transfer verdict and diagnostic lead; building half = appliance timing (3.5), heating null (3.6), the
  checks that did not pass in one paragraph with their reason (3.5), and the sentence "The transfer
  conclusion of Sections 3.1 to 3.4 does not depend on any downstream check."
- P5: Table 2 (old Table 3) has a "95 % interval of the margin" column with `[P5]` in all nine cells; one
  marked `[P5]` sentence in 2.6, plus the one-seed sentence. 10 `[P5]` markers in total.
- Moved to SI: old §3.8 (S8; one Methods sentence stays in 2.5), §4.4 detail and the 410-cell record (S9,
  S7.6), §4.5 and §6.6 (S10), §7.10 and documentation defects (S12), check tallies of §3.1-§3.4 (S1, S6),
  the §1.3 anecdote (S6), old Table 2 in full (Table S1), old Table 5 (Table S3), old Table 8 (Table S5),
  old Figures 3, 5, 6, 7 (Figures S1-S4), the quasi-steady comparison (S7.6), privacy controls (S7.4).
- Renumbering (for the manager): old Table 1 -> Table A.1; new Table 1 = dataset-role table; old Table 3 ->
  Table 2; old Table 4 -> Table 3; old Table 6 -> Table 4; old Table 7 -> Table 5; old Tables 5 and 8 ->
  Tables S3 and S5; new Tables S2 (P10) and S4 (P3 runner-up hours). Figures: 1 and 2 unchanged; old
  Figure 4 -> Figure 3; old Figures 3, 5, 6, 7 -> S1, S2, S3, S4. Main text: 3 figures + 5 tables = 8.
- Citations added, all ACCEPTED in VETTING_RL34/RL35 and in the allowed form: Borisov et al. (DataCite
  author list, arXiv version), Solatorio and Dupriez, Dinh et al., Li et al., Gulrajani and Lopez-Paz, Koh
  et al. (benchmark name only; arXiv versions), Nosek et al., Hyndman and Koehler, Levin et al. (1st ed.),
  Lin, Lovelace and Ballas (as the contrast), Platzer and Reutterer ("as used by"), Ramdas et al. ("see
  also" level), IWU calculator workbook for 3.0 W/m2. Jutras-Dubé et al. (2024): only the one metadata
  sentence of VETTING_RL35 §5. Loga et al. (2012) Synthesis Report removed. No AAO item cited. Nothing
  from RL36. 36 references, each cited at least once (grep-checked).
- MISMATCH fixes from the number sheet: Table 7 watts (502.9 / 403.5 / 416.1); observed-stock cells now
  35,090 (Madrid 11,340 / Bologna 11,680 / London 12,070), SI only; wall time "about 7.5 to 11 hours" (per
  fold in SI S2); seed-alone spread "wider than the band in Spain and the UK, narrower in Italy" (SI S1.6,
  main 4.1); unconstrained 5,200 provenance note (SI S4). TB3-11 gloss fixed ("four to six times",
  "1.15 to 3.9 times"). Ratios recomputed per the sheet's note: backbone factor 4.9 (was 4.7), family wall
  time about 22 % (was 24 %).
- Coordinator's binding corrections (`IMP/prep/appendixB_equations_draft.md` section (c)) applied:
  (1) uniform seed for the synthetic population, Beckman cited for fitting only; (2) baseline raked onto the
  synthetic population's shares on five variables including day type at calendar-week shares; (3)
  discrimination = relative margin above 0.5 of the contending pair's published distance; (4) one constant
  start probability per appliance, eligibility = active occupant doing a mapped activity, cycles pause when
  no one is active except cold, laundry and custom appliances; (5) secondary activity "never a trigger";
  "used where coverage allows" removed (SI S7.5 simplified too); (6) iterative rescaling, up to six passes,
  2 % tolerance; (7) only the age-band mix is tilted, direction on the targeted group, amplitude over the
  five outcome groups; (8) Table 4 rows relabelled (worst activity; mean JSD with maximum at most 0.025;
  worst-activity budget error against real held-out diaries) plus one sentence each in 2.6 and 3.4; (9)
  "worst activity code", main and SI; (10) 0.264 stated as an error, Markov fitted on unweighted counts;
  (11) 10 min/day floor in 2.6 and Table 3, limitation criteria written as a disjunction with the
  MAPE > 20 % criterion (main, Table 3, SI S1.4); (13) TPR at 0.1 % FPR clause stated (at most 5 %); (15)
  alpha = 64, effective factor about 11.3. (12) and (14) were already in the brief. In-text appendix
  references use the draft's numbering (B.1-B.48); if the merge renumbers, these need updating.

**Word count, main text (prose only; tables, display equations, figure lines and captions excluded; awk
script, 2026-09-23).** Introduction 733 (1.1 247, 1.2 299, 1.3 187). Methods 2,754 (intro 51, 2.1 344,
2.2 227, 2.3 452, 2.4 388, 2.5 599, 2.6 693). Results 1,526 (3.1 314, 3.2 147, 3.3 110, 3.4 280, 3.5 390,
3.6 125, 3.7 160). Discussion 1,127 (4.1 312, 4.2 200, 4.3 181, 4.4 219, 4.5 215). Limitations 822.
Conclusion 241. **Total 7,203 words of prose; the five main-text tables add 456 words (about 7,660 with
tables).** Abstract 248 words.

**Sentences over 30 words.** Script: awk extract of Introduction to Conclusion; tables, equations and
captions dropped; split on sentence ends with abbreviations and decimals protected; words counted per
sentence. First run listed 19 (seen failing): 1.1 lineage (33), 1.2 search (40), 1.3 aim (31), 2.3 IPF
(32), 2.5 chaining (32), 2.6 joint-structure list (43), 2.6 [P5] (39), 2.6 fitted quantities (33), 3.1
in-sample (42), 3.1 narrowing (32), 3.2 full fine-tune (31), 3.4 neutrality (37), 3.5 reference profile
(38), 3.7 distance to closest record (33), 4.5 generator's value (32), 5 UK unknown household (31), 5
quasi-steady (34), 6 opening (42); one more appeared with the corrections (2.6 limitation criteria, 46).
All fixed by splitting. Final run: 0 sentences over 30 words.

**Numbers not traceable to the sheet, P3 or P10 (each carried from a named file; none invented).**
Main text: EnergyPlus version 24.2.0 (old manuscript, not a sheet row); model repository IDs (training
record, `Step4_docs/4thJ_04_finetuneLLM.md:192-196`); effective adapter factor about 11.3, JSD maximum
0.025, 10 and 15 min/day floor, MAPE > 20 %, TPR at most 5 % at 0.1 % FPR, six passes and 2 % (from the
coordinator's binding list, `appendixB_equations_draft.md` (c), and the code lines it cites; the TPR bound
read at `tools/4thJ_step6_privacy_mia.py:12,85-87`). SI: revision hashes (same training record); "about
one percentage point" at-home shift, "more than fifteen hundred" thirteen-year-olds, "under half a per
cent" annual heating (410-cell record) and "8,760 hourly values of 100 dwellings" (all from the old
manuscript, not sheet rows). Every other number matched the sheet (MATCH or ROUNDING rows), P3 or P10 in a
scripted sweep (312 distinct numeric tokens in the main text, 363 in the SI; the residue was rounding,
years and IDs, each checked by hand).

**Limitations checklist.** `IMP/prep/limitations_checklist.md`: 40 of 40 old points ticked (38 with a home
in the main text or data statement; 2 in the SI only, as the brief moves them: the manifest documentation
defect and the 840 Madrid cells / courtyard buildings). 10 new points added (survey-year confound, one
training seed, deposit date, search not systematic, unweighted real pool and no interval on the peak
hour, timing not checked against measured profiles, old British reference profile, sex/gender,
quasi-steady difference, England-only UK typology).

**Open questions for the manager.**
1. Funding: 2J reads "NSERC through a Discovery Grant, and the Volt-Age Seed Fund, Concordia University".
   The old 4J text named NSERC without "Discovery Grant", so the new 4J text does too. Add it if the same
   grant funds 4J.
2. The generative-AI declaration is a draft (Claude for language editing, Gemini for literature reports);
   the author confirms it, and says whether any figure image was AI-made (then a caption disclosure is
   needed).
3. SI S9 and S12 keep "840 cells in 84 Madrid buildings did not complete" (sheet B16 MATCH) next to 35,090
   completed cells. The planned Madrid figure (11,510) minus completed (11,340) is 170, not 840; this is not
   reconciled on disk. The main text carries no campaign count, so the question lives in the SI only.
4. Appendix B: the main text cites the draft's numbers (B.1-B.48) and keeps six numbered in-text equations
   (1)-(6); Eqs. (2) and (5) restate draft B.8 and B.2-B.3. The main Nomenclature was written independently
   of the draft's section (a); merge the two.
5. Main-text prose is 7,203 words, a little under the 7,500 target; about 7,660 with tables.
6. Figure 1 is still the old pipeline image ("Steps 0 to 11"); only its caption changed. The new three-row
   diagram remains an image prompt for the author.
7. The P5 interval column moved with its table: it is now Table 2 (was Table 3).

### Appendix B merge (agent, 2026-09-23)

**Archive.** `writing/submission/previous/4J_manuscript_submission.md.pre_appB_20260923` (66,640 B, `[ -s ]` checked, byte-identical to the pre-merge file). No docx build, no compute, no web access.

**What was merged.** Only the draft section "Appendix B. Definitions of the reported quantities" (plus reconciled nomenclature). Draft sections (a)-(c) and every bracketed `[Code | Source | Status]` line were not carried. Appendix = one plain intro paragraph, 17 unnumbered H2 subsections, equations in the manuscript's display style (`$$ ... \qquad (\mathrm{B.n})$$`, one line each). Manuscript now 863 lines, 100,375 B.

**Equation count.** Draft 49 -> appendix 44 (B.1-B.44), plus in-text (1)-(6) unchanged. Script check: 44 labels, consecutive; 50 `$$` lines, all single-line and closed.

**Duplicates removed (appendix points to the in-text equation instead).** Draft B.2-B.3 -> Eq. (5) (strict m > 0 rule and "raked on whole population, restricted to band" kept as prose); draft B.8 -> Eq. (2); draft B.37 -> Eq. (4) (prose: Eq. (4) with C = C_k, E = E_k, L = L_k, D = D_k; stop conditions kept); draft B.46 -> Eq. (3) (prose: g-bar over 8,760 hours; 3.0 W/m2 with IWU citation). B.37 and B.46 go beyond open question 4, which named only (2) and (5); they restated Eqs. (4) and (3) exactly, so they were treated the same way. Draft B.24 (OLS estimator) kept: it estimates Eq. (6), it does not restate it.

**Renumbering map (draft -> merged).** B.1->B.1; B.2, B.3 dropped (Eq. 5); B.4..B.7 -> B.2..B.5; B.8 dropped (Eq. 2); B.9..B.36 -> B.6..B.33; B.37 dropped (Eq. 4); B.38..B.45 -> B.34..B.41; B.46 dropped (Eq. 3); B.47..B.49 -> B.42..B.44.

**In-text references updated (every one grep-checked against the equation it names).** 2.3: B.48->B.43; IPF 1e-13 now cites B.10 (added), rounding B.13-B.15 -> B.12 (tightened: the sentence is about rounding only). 2.4: B.8-B.9 -> B.6 (B.8 is Eq. (2) itself, so only the stopping rule is cited); B.27->B.24; B.26->B.23. 2.5: E now cites B.33 (added, E is defined there); B.37-B.38 -> B.34 (B.37 is Eq. (4) itself); B.43-B.44 -> B.39-B.40. 2.6: B.1-B.3 -> B.1; B.4-B.5 -> B.2-B.3; B.6->B.4; B.7->B.5; B.17->B.14; B.19->B.16; B.20->B.17; B.21->B.18; B.22-B.23 -> B.19-B.20; B.24-B.25 -> B.21-B.22; B.28-B.30 -> B.25-B.27; B.31->B.28; B.33-B.34 -> B.30-B.31. No reference points past B.44; the SI carries no B.n reference.

**References added.** None. Every ACCEPTED source the appendix cites was already in the list: Beckman 1996, Deville and Särndal 1992, Hu 2022, Hyndman and Koehler 2006, IWU n.d., Jordan and Vajen 2001, Levin 2009 (1st ed.), Lin 1991, Lovelace and Ballas 2013 (contrast), Platzer and Reutterer 2021 ("used by"), Ramdas 2017 ("see"), Richardson 2008, Richardson 2010 (Section 2.7 for the calibration idea), Shokri 2017 (general setting). All 37 reference entries are cited at least once (script plus grep for narrative forms). Nothing REJECTED is cited; Loga et al. 2012 does not appear.

**[AUTHOR TO OPEN] sources left uncited (author adds after opening; strings in `IMP/prep/appendixB_equations_draft.md` reference list and VETTING_RL34 section 4).**
- B.1 / Eq. (5) MAE: Willmott and Matsuura 2005 (Hyndman and Koehler already cited at Eq. (5)).
- Raking prose (Eq. (2)) and B.10 IPF: Deming and Stephan 1940 (Deville and Särndal, Beckman kept).
- B.12 largest remainder: Balinski and Young 1982 (Lovelace and Ballas kept as contrast).
- B.14 Wasserstein: Vallender 1974 (Ramdas kept as "see").
- B.21 OLS slope and R2: Montgomery, Peck and Vining 2012 -> equation now UNCITED.
- B.24 Markov: Widén and Wäckelgård 2010 for the first-order transition-count claim (Richardson 2008 kept; Widén stays cited elsewhere in the paper).
- B.25 loss score: Yeom et al. 2018 (Shokri kept as general setting).
- B.27 rank AUC: Hanley and McNeil 1982 -> equation now UNCITED.
- B.28 TPR at 0.1 % FPR: Carlini et al. 2022 (corrected string) -> equation now UNCITED.
- B.30 DCR: Park et al. 2018 (Platzer and Reutterer kept).

**Nomenclature changes.** One list in the manuscript's Nomenclature section (two columns, units in the meaning column as before): 17 abbreviations then symbols, Latin then Greek; 22 old rows -> 124 rows. Main-text symbols kept as the base ($\hat B(a)$, $B^{pub}(a)$, $m$, $\mathrm{MAE}^{base}$, $w_i$, $T_v(k)$, $C_v(k)$, $\phi_{int}$, $\overline g$, $f$, $h$, $C$, $E$, $L$, $D$, $r$, $\alpha$, $\beta$), and the draft's symbols renamed to avoid clashes: $B_a(S)$->$\hat B_S(a)$; $\Delta$ (margin)->$m$, $\Delta^*_r$->$m^*_j$; $\mathrm{MAE}^{null}$->$\mathrm{MAE}^{base}$; $\hat p_v$, $p^*_v$->$C_v$, $T_v$; $\alpha(\cdot)$ crosswalk->$\kappa(\cdot)$; $\bar E_a$ (EU mean budget)->$\bar B^{EU}(a)$; $E_\ell(a)$->$x_\ell(a)$; $\bar E_p$->$E_k$; synthetic table $T$, $T_5$->$\Psi$, $\Psi_5$ (axis $x$->variable $v$); $h$ (percentile position)->$\xi$; LoRA written as $W=W_0+\gamma\mathbf{BA}$ (no output symbol $h$; matrices bold; dims $d_{in}$, $d_{out}$); household index $h$->$\eta$, $H$ households->$N_{hh}$; $n_h$->$n_{hh}$; $L$ tilt levels->$n_\lambda$; $L$ realised cycle->$L^{run}$; $\Delta_j$ draw duration->$L_j$; $\bar T$, $\varepsilon_T$->$\bar n$, $\Delta\bar n$; $\varepsilon_B$->$\Delta B_{max}$; $\delta_{max}$->$\Delta_{dec}$; $m_k$->$\bar d_k$; $D_W$->$W_1^{max}$; $G_a$->$F^{cand}_a$; $g$ (generated diary)->$i$, $g_{PPL}$->$G_{PPL}$; $\ell_\theta$->$\mathcal L_\theta$; token $x_{i,t}$->$o_{i,t}$; $d_c$, $o$, $r$ (B.23)->$\mathrm{MAE}_c$, $c_0$, $c'$; $\rho_b$ rank->index $j$; $\sigma$ stratum->$\varsigma$; $p(j,k)$ transitions->$\omega(a,a')$; Markov $s_t$, $P$, $\pi$->$a_t$, $\mathbb P$; member $m$->$i$; pass $m$->$n$; $r_k$->$\varphi_k$; $\bar c_k$->$\hat C_k$; $q$, $q'$ flow->$\dot V$, $\dot V'$; $V_d$->$V_{day}$; $P_{k,f,h}$ heating->$Q_{k,f,\eta}$; $\sigma_{k,f}$->$\mathrm{CV}_{k,f}$; $\phi(\cdot)$ profile map replaced by the code set $\mathcal C_k$; $u_p$->$\mathcal Q_{0.975}$; day index $y$->$j$. Internal labels (AC2, AC4-8, level-1) replaced by words (study, leisure, first-digit activity); "steering"->"direction", "fail if"/"pass if"->"not met if"/"met if".

**Other edits.** "British" -> "UK" three times (3.5 reference profile; Section 5 ownership shares and reference profile). No "Britain", no "failure", no code path, no "draft" in the appendix (script check).

**Word count of the appendix.** 2,814 words of prose (display equations and headings excluded); 3,423 whitespace tokens including equation lines.

**Not verified.** No pandoc render was run (no build allowed); `\mathbb{1}`, `cases`, `\operatorname`, `\varsigma` and `\mathcal{Q}` are standard texmath but were not seen rendered.

### P9 second pass (2026-09-23)

**Scope.** Second-pass number check of the manuscript, supplementary material and highlights against
`IMP/prep/results_number_sheet.md` (116 rows), after the appendix-B merge above. Backups made first:
`previous/4J_manuscript_submission.md.pre_P9b_20260923`,
`previous/4J_supplementary_material.md.pre_P9b_20260923`, `previous/4J_highlights.md.pre_P9b_20260923`.
No compute run, no external access, no email address written anywhere.

**Result: the rewrite already carries all eight sheet MISMATCH fixes.** Checked all 116 sheet rows
against the current (post-rewrite, post-appendix-merge) text, by content rather than by the sheet's
old section numbers (the rewrite renumbered every section and table). All eight previously-flagged
MISMATCH rows are already corrected in the current text:
- Table 5 (was "Table 7") peak powers: 502.9 / 403.5 / 416.1 W, no 518/395/422 anywhere (line 227-229;
  Supplementary Table S4 line 368-370).
- Observed-stock cells: 35,090 total (Madrid 11,340 / Bologna 11,680 / London 12,070), 3,529 buildings,
  31,591 dwellings, throughout SM S4/S9 (no 35,290/11,510/11,710 anywhere); 840 failed cells / 84
  buildings in Madrid correctly stated (SM S4, S9, S12).
- Training wall time: "about 7.5 to 11 hours per fold" (manuscript line 87); model card gives the three
  per-fold times exactly (SM S2 line 144).
- Fictional-country noise floor: "wider than its acceptance range in Spain and the UK" (manuscript line
  253); SM S1.6 gives the three numbers and states Italy is narrower (SM lines 100-102).
- Unconstrained-batch provenance: SM S4 now states the 5,200 count was verified at generation time and
  that the on-disk files were later superseded (SM lines 195-197).

Also checked and already correct: headline factor reads "1.1 to 3.9" everywhere (abstract, highlights,
body, conclusion), never "2 to 6"; "1.15" appears only as the ninth cell's own value, never as the
headline; the 320 collision cells are not mentioned anywhere and are not folded into any count; the real
appliance peaks (UK 18:00, Italy 19:00, Spain 21:00), generated peaks and the 19:00-21:00 raked-donor
range all match; Table 2's `[P5]` markers are untouched. Abstract and highlights numbers match the body.

**Counts.** 116 sheet rows checked; 116 matched the current text (exact or the sheet's own allowed
rounding), including all 8 previously-flagged rows, now via their corrected values. 0 new number
mismatches found. 1 non-number style fix made (below).

**Edit made.**
- `4J_supplementary_material.md:574` — "The ownership shares are British and about two decades old" ->
  "The ownership shares are from the UK and about two decades old". Not a number; this SI sentence was
  the one instance of "British" left behind by the appendix-merge pass's own "British -> UK three times"
  edit (this file's log above, "Other edits"). No other "Britain"/"British" instance remains in the
  manuscript, SM or highlights.

**Open items for the author (not edited, no clear error to fix):**
1. Manuscript line 175 says real diaries meet the in-sample MAPE bar "at 5 to 12 per cent"; the exact
   source values (confirmed against `Step6_docs/outputs_step6/g65_g69_corpus_calibration.json`) are
   4.64 / 5.96 / 11.50 per cent (Spain/UK/Italy), also given exactly in SM S7.2. The prose range rounds
   both ends outward (4.64 -> "5", 11.50 -> "12"). Not counted as a mismatch because it reads as an
   approximate gloss and SM carries the exact figures, but the author may want "about 5 to 12" or the
   exact range.
2. A few methods constants appear only in the Nomenclature/Appendix B (bootstrap replicates R = 2,000,
   confirmed against `IMP/impl/P5_intervals_table3.md`; tilt-level parameters n_lambda = 5, n_pre = 600,
   lambda_max = 0.6) that are not tracked as rows in the number sheet, since the sheet tracks results,
   not every design constant. R = 2,000 and n_pre = 600 are independently confirmed elsewhere; lambda_max
   = 0.6 was not independently re-derived from a primary source in this pass.
3. Table 2's `[P5]` interval column is still a literal marker, as instructed; it depends on the P5 job
   finishing.
