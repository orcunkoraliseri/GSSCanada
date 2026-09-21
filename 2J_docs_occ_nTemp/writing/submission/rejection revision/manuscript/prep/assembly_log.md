# T84 -- WP10 assembly log

Task doc: `../../impl/2026-09-21_T84_wp10_assembly.md`. Outputs: `../2J_manuscript_AE_revised.md`,
`../2J_SI_AE_revised.md`, this file. Plan log (ds)-(dx) read and followed as binding.

## Changes made (where / before / after / why)

1. Title -- before: three title options listed in `draft_S1_introduction.md`. After: only "Title
   option 1" (the plan's candidate) used, marked `[TITLE: AUTHOR TO CONFIRM]`, per task doc Output #1.
   The "Alternative 1/2" options were not copied into the assembled file (they stay in the draft).
2. Introduction heading -- before: `# Section 1. Introduction`. After: `# 1. Introduction`, to match
   the numbering style already used by every other section (`# 2. ...`, `# 3. ...`).
3. Introduction 1.5, cross-reference -- before: "...are stated in full in Section 7." After:
   "...are stated in full in Section 5." Why: Limitations is renumbered Section 5 in this assembly
   (allowed edit #1).
4. Introduction 1.5, placeholder fill -- before: "([NUMBER FROM RESULTS] households per panel,
   [NUMBER FROM RESULTS] simulation runs)". After: "(50 households per panel, [NUMBER FROM RESULTS]
   simulation runs)". Source: Section 2.8 ("N = 50 households" drawn per cell) and the task doc's own
   instruction ("Households: 50 per cell, 24 cells"). The simulation-run count was left as a
   placeholder per the task doc's explicit "Do not guess ... the run count."
5. Introduction 1.5, placeholder fill -- before: "([NUMBER FROM RESULTS] agreement across
   dwelling-by-year cells)". After: "(48 of 48 cells within the plus or minus 15 percent band around
   the fitted target, agreement across dwelling-by-year cells)". Source: task doc's own instruction,
   matching Results 3.3's stated SHEU-check result. The architecture-search-count placeholder in the
   same paragraph 2 was left open (task doc: "Do not guess the architecture count").
6. Framework Table -- before: `## Table 1. Datasets and their role in the framework`. After:
   `## Table 2. Datasets and their role in the framework`. Why: Table 1 is the Introduction's
   comparison table (allowed edit #3); this is the next table encountered.
7. Framework Figure 1 -- before: `[Figure 1: workflow, image prompt to be written in WP11]`. After: an
   image reference to `../../figures/Figure_01_workflow.png` (confirmed to exist; never
   `Figure_01_pipeline.png`, per the task doc) plus a one-line caption written by this assembly task,
   since no caption existed in any accepted draft. Flagged in "Open for the manager" below.
8. Results section -- every `[R#-tag]` placeholder replaced with its final Figure/Table number (see
   Figure list and Table list below). No prose changed, only the bracket tags.
9. Discussion -- `[R6-measured]` replaced with `8` (Figure 8), matching Results.
10. Limitations heading -- before: `# S7. Limitations`. After: `# 5. Limitations`. Body text
    unchanged (it already said "This work has eleven limitations... the first eight...", which needed
    no further edit since Discussion and Conclusion already referenced "Section 5" in their own
    accepted drafts).
11. SI section headers -- before: `## S.1` ... `## S.10` (dotted form) across the three source
    drafts. After: `## S1` ... `## S10` (task doc: "SI sections numbered S1, S2, ... in one
    sequence"). Internal cross-references updated to match: "section S.7" -> "section S7", "S.7" ->
    "S7" (twice), "S.9" -> "S9", "S.5" -> "S5" (all in `draft_SI_schedule_completion.md`'s own S8/S9
    text).
12. SI S1 -- before: "The architecture is summarized in SI Table B1 (already in the supplementary
    tables)." After: "The architecture is summarized in Table S1 (already in the supplementary
    tables; Table S1's own content, `tables/SI/Table_B1_B2.md`, is not one of the three SI drafts
    named for this assembly and is NOT merged into this file -- see assembly_log.md)." Why: renumbered
    per the SI's own Figure/Table S-sequence, but flagged since the actual table content was not
    brought in (out of this task's stated scope: "the three SI drafts merged").
13. SI S10 -- added one caption line, "**Table S2. Clustering-aware versus plain paired-difference
    confidence intervals for midday share and load factor.**", immediately above the existing
    interval-width table, since the source draft had the table but no caption line of its own.
14. Results 3.8 cross-references -- "(Supplementary Information Table [R8-modelcard-SI])" ->
    "(Supplementary Information Table S1)"; "(Supplementary Information Figure [R8-threshold-SI])" ->
    "(Supplementary Information Figure S2)"; "(Supplementary Information Table [R9-clustering-SI])" ->
    "(Supplementary Information Table S2)"; Results 3.7 "(Supplementary Information, Figure
    [R7-n200-SI])" -> "(Supplementary Information, Figure S1)".
15. Excluded from both assembled files (not copied, per task doc: "Every draft's own trailer... is
    NOT copied"): every draft's Number trace table, Ledger, Verified, Decisions, Next, Reviewer-item
    closure table, Citations-used list, Open for the manager/author, and WHAT I DID NOT VERIFY
    sections. Also excluded: each of the three SI drafts' own opening provenance paragraph (e.g.
    "Draft written by T36 (WP10), 2026-09-15...", "Draft written by the manager, 2026-09-20,
    delivering the promise made in the main text..."), on the judgement that this is drafting-process
    metadata (names internal task IDs T36/T67/WP10, reviewer-item codes) rather than reader-facing
    Supplementary Information content, analogous to a trailer. Flagged as a judgement call, not an
    explicit task-doc instruction.
16. Duplicate-sentence check (allowed edit #6): scanned the assembled main body by machine for
    word-for-word identical sentences (40+ characters) appearing in more than one place. None found.
    No sentences removed.
17. References: built as one author-year list from `../../archive/2J_manuscript_submission.md`
    (read only, lines 491-595), keeping only the 30 works actually cited in the assembled main text
    (verified against `draft_S1_introduction.md`'s own "Citations used" list, then independently
    re-confirmed by searching every other draft's body text for "(Author Year)" patterns -- Discussion
    added no citation beyond Chen et al. (2022), already in the Introduction's list). Zero
    `[REFERENCE ENTRY NEEDED]` tags required -- all 30 were already in the archive. Guo et al. (2026)
    was deliberately not carried (per `draft_S1_introduction.md`'s own note: the persistence-framing
    claim it supported was found unsupported by the deep-research vetting, so the draft cites nothing
    there but `[CITATION NEEDED]`).

## Figure list (main text)

| Figure | First appears | Caption source | Image file | Status |
|---|---|---|---|---|
| 1 | Section 2 (Framework) | Written by this assembly task (no caption drafted upstream) | `../../figures/Figure_01_workflow.png` | EXISTS |
| 2 | Section 3.1 (tag `R1-athome`) | `draft_S3_results.md`, figure box after 3.1 | expected `fig01_athome_by_hour.png` | FILE NOT FOUND (only the CSV exists, at `impl/T79_in/fig01_athome_by_hour.csv`; no PNG under `impl/` or `../figures/`) |
| 3 | Section 3.3 (tag `R3-enduse`) | `draft_S3_results.md`, figure box after 3.3 | `impl/T71_out/fig02_annual_by_enduse.png` | EXISTS |
| 4 | Section 3.4 (tag `R4-loadshape`) | `draft_S3_results.md`, figure box in 3.4 | `impl/T71_out/fig03_intraday_load_shape.png` | EXISTS |
| 5 | Section 3.4 (tag `R4-peak-lf-ramp`) | `draft_S3_results.md`, figure box in 3.4 | `impl/T71_out/fig04_peak_loadfactor_ramp_ci.png` | EXISTS |
| 6 | Section 3.4 (tag `R4-heatmap`) | `draft_S3_results.md`, figure box in 3.4 | `impl/T71_out/fig05_enduse_hour_diff.png` | EXISTS |
| 7 | Section 3.5 (tag `R5-comparison`) | `draft_S3_results.md`, figure box after 3.5 | expected `figure_06_full_vs_avgarm.png` | FILE NOT FOUND (T77's job output was never scp'd to a local `T77_out/`; only reconciliation CSVs made it into `impl/T79_in/`) |
| 8 | Section 3.6 (tag `R6-measured`); also cited from Discussion | `draft_S3_results.md`, figure box after 3.6 | expected under `impl/T73_out/` | FILE NOT FOUND (`T73_out/` holds 2 CSVs + `t70_run_meta.json`, no PNG) |
| S1 | Section 3.7 (tag `R7-n200-SI`) | Cited from Results 3.7; no draft among the three merged SI files contains its caption | expected under `impl/T75_out/` | FILE NOT FOUND (`T75_out/` is empty; only the script is present) |
| S2 | Section 3.8 (tag `R8-threshold-SI`) | Cited from Results 3.8; no draft among the three merged SI files contains its caption | `impl/T74_out/figures/fig09_threshold_sensitivity.png` | EXISTS, but not referenced by name inside the merged SI file (see Open for the manager) |

**Numbering note (judgement call).** Section 3.2's own text mentions Figures `R4-loadshape` and
`R4-heatmap` (in a forward reference to Section 3.4's own figures) before Section 3.3 first mentions
`R3-enduse`. A strict, literal "order of first mention" reading would therefore number `R4-loadshape`
ahead of `R3-enduse`. Instead, this assembly numbered each figure by the section that carries its own
dedicated caption box (`R3-enduse` in 3.3, `R4-*` in 3.4), matching the pre-existing WP11 sheet
numbering already encoded in the source file names (`fig01`..`fig07`, `fig09`) and in
`draft_S3_results.md`'s own "Figure and table references used" table. This is the natural reading (a
forward reference to a figure shown fully later is normal in a paper) but is a judgement call, not a
mechanical one; flagged for the manager to confirm.

No image files were moved or copied, per the task doc.

## Table list (main text)

| Table | Section | Content | Notes |
|---|---|---|---|
| 1 | 1.2 (Introduction) | Framework-dimension comparison: 9 external studies, the authors' own prior work, and this study, against C1-C6 | Unchanged from the draft; also cross-referenced from Discussion |
| 2 | 2 (Framework) | Datasets and their role in the framework | Renumbered from the draft's own "Table 1" |

## SI Figure/Table list

| Label | Cited from | Content | Status |
|---|---|---|---|
| Figure S1 | Results 3.7 | N=200 vs N=150 sample-size convergence check | Not present in the merged SI file (none of the three source drafts contains it); image FILE NOT FOUND locally |
| Figure S2 | Results 3.8 | Model-selection threshold-sensitivity | Not present in the merged SI file; image EXISTS at `impl/T74_out/figures/fig09_threshold_sensitivity.png` but was never drafted into an SI section |
| Table S1 | SI S1; also Results 3.8 | Model architecture / J3 gate-score summary ("SI Table B1") | Label renumbered only; actual table content lives in `tables/SI/Table_B1_B2.md`, not one of the three SI drafts merged -- content NOT brought into this file |
| Table S2 | SI S10 | Clustering-aware vs. plain paired-difference confidence-interval widths, midday share and load factor | Content present; caption line added by this assembly task |

## Placeholders still open (main text)

- `[TITLE: AUTHOR TO CONFIRM]` -- title line (deliberate, per task doc Output #1).
- `[STATUS TO CONFIRM BY AUTHOR]` -- Table 1, row for the authors' own prior-line companion journal
  manuscript (Section 1.2).
- `[NUMBER FROM RESULTS]` x2 -- Section 1.5: candidate-architecture count and simulation-run count.
  Left open per the task doc's explicit "Do not guess the architecture count or run count."
- `[NUMBER NEEDED: EUI]` -- Section 3.3. No rebuilt energy-use-intensity figure exists per plan log
  (ds) Ruling 2; the archived Table 5 EUI values are not carried forward.

SI file (informational, not a required check target): 3 `[VALUE PENDING: ...]` placeholders remain,
carried unchanged from `draft_SI_schedule_completion.md` (S6 x2, S8 x1).

## CITATION NEEDED list (main text)

1. Section 1.1, paragraph 2 (Introduction): source on why residential load timing, not only annual
   energy, matters for grid peak demand, the evening ramp and demand response.
2. Section 1.1, paragraph 2 (Introduction): source establishing 2030 as a recognized planning
   horizon, and the timing of the next comparable time-use survey cycle.
3. Section 1.3, paragraph 2 (Introduction): source on the post-2022 trajectory of work-from-home
   prevalence in Canada or comparable economies.
4. Section 4, paragraph 3 (Discussion): source on why residential load timing matters for grid peak
   demand, the evening ramp and demand response (restates item 1).
5. Section 4, paragraph 3 (Discussion): source establishing 2030 as a recognized planning horizon
   (restates item 2).
6. Section 4, paragraph 8 (Discussion): StatCan Daily reference for the Canadian telework-share
   decline (41.1 percent April 2020 to 18.7 percent May 2024).

Total: 6 (3 distinct claims, each stated once in the Introduction and once in the Discussion; items
4-5 are not word-for-word identical to items 1-2, so the duplicate-sentence rule did not remove
either copy).

## Check results (assembled main file, Abstract through Conclusion, References excluded)

- **No "forecast": FAIL.** 3 occurrences, all in deliberate negated usage distinguishing the paper's
  scenario framing from a single-point forecast (the reviewer item this itself closes,
  R2-3/R3-2): Section 2.7 ("...a scenario-based projection of a stated persistence assumption, not a
  forecast: no scenario claims..."); Section 5/Limitations, two occurrences ("The 2030 results are a
  scenario, not a forecast." and "...not as a probabilistic forecast of 2030 occupancy."). NOT fixed:
  prose rewrite to remove the word is outside this task's allowed-edit list (copy text as it stands).
  Flagged below for the manager.
- **No em or en dash (byte-level): PASS.** Zero occurrences in the Abstract-to-Conclusion body.
  (The References section, excluded from this check by the word-count scope definition, does contain
  en dashes in page ranges -- standard citation style, not a violation.)
- **No "failure": PASS.** Zero occurrences.
- **No internal labels (bare, outside parentheses): PASS.** The only matches found (`S-None`,
  `S-Partial`, `S-Revert-std`, Results 3.2) all sit inside parentheses ("(code S-None)" etc.), which
  the rule permits. No bare `J3`, T-numbers, `COLLECT_MODE`, or `Tier-1` found anywhere in the body.
- **No retired numbers ("2.2 to 3.9", "5.2 p", "17.0-17.7", "2.7 %", "2.7 percent", "6,000",
  "64,061", "144,507"): PASS.** None found.
- **Every figure and table number cited in text exists, and each exists once: PASS.** Figures 1-8
  and S1-S2 each have exactly one defining caption/box; Table 1 and Table 2 each defined once. (Table
  S1's content gap is a separate, logged issue -- a missing merge, not a duplicate or dangling
  number.)
- **Word count of the main text (Abstract to Conclusion, excluding references): 12,076 words**,
  counted with `wc -w` on the exact line range from `# Abstract` through the end of Section 6
  Conclusion, in the session scratch directory.

## Open for the manager

1. Figure numbering resolved a forward-reference ordering conflict (see "Numbering note" above);
   confirm the resolution.
2. Six of ten cited data/SI figures have no local image file (Figures 2, 7, 8, S1). These need to be
   produced or collected (from the T76, T77, T73 and T75 cluster job outputs respectively) before
   typesetting.
3. Figure 1's caption was written by this assembly task since no draft supplied one; review and
   replace if a better caption exists.
4. Table S1 ("SI Table B1", model architecture / gate-score summary) is cross-referenced from both
   the SI and the main text but its content lives in `tables/SI/Table_B1_B2.md`, outside the three
   named SI drafts -- not merged here. That external table also still needs its own correction (the
   "sole 4/4-gate model" claim, per `draft_SI_model_selection.md`'s own "Next" section) before it can
   be folded in.
5. Figures S1 and S2 are cited from Results 3.7/3.8 as living in the Supplementary Information, but
   none of the three merged SI drafts actually contains a captioned figure for either -- a real
   content gap, not just a missing image file.
6. The "no forecast" check FAILS on 3 occurrences, all deliberate negated usage ("not a forecast").
   This task's allowed-edit list does not permit prose rewriting to fix this; the manager must decide
   whether the literal-word rule is meant to catch on-purpose negated usage like this, or whether
   these three instances should be granted an exception.
7. Table 2 (Framework datasets) names NRCan SHEU, StatCan Census PUMF, StatCan GSS, and EnergyPlus as
   data/methodology sources; the archive holds formal reference entries for all four
   (`naturalresourcescanada2019`, `statisticscanada2021`, `statisticscanada2022`,
   `usdepartmentofenergy2024`), but none is cited in (Author Year) form anywhere in the assembled
   running prose, so none made the final reference list under the "keep only what's cited" rule.
   Flag for whether Table 2 or the Framework text should carry inline citations before submission.
8. Every item still open from the individual drafts' own "Open for the manager"/"Open for the
   author" sections remains open and is not repeated here in full (title choice among 3 options;
   JBPS companion-manuscript status; the 3-decimal-place de-risking question for the two "0.12
   percent" Abstract figures; whether the Discussion's grid-planning citations should differ from the
   Introduction's; etc.) -- see the individual draft files, which are unedited and stay on disk.
9. This assembly excluded each of the three SI drafts' own opening provenance paragraph (drafting
   metadata, internal task IDs) as a judgement call, not an explicit task-doc instruction (see Change
   17 above / item 15). Confirm this reading is correct.
10. SI-only, informational (not a required check target): the merged SI file still contains 3
    `[VALUE PENDING]` placeholders, 2 uses of "forecast" (S7, plain descriptive use, not negated), 2
    em dashes (S8, S10), and one bare internal label ("T21", S10). None were altered, since this
    task's edit authority does not extend to SI prose beyond section/figure/table renumbering.

## WHAT I DID NOT VERIFY

- Did not verify that any FILE NOT FOUND figure exists somewhere else on the machine outside the
  `rejection revision/impl/` and `../figures/` trees searched (for example, on the cluster or in a
  personal folder); searched only the local project tree with `find`/`ls`.
- Did not open or read `tables/SI/Table_B1_B2.md`'s actual content; confirmed only that the file
  exists on disk, consistent with the decision to keep its content out of this assembly's scope.
- Did not independently re-derive or re-check any number copied from the seven main-text drafts or
  the three SI drafts; per the task's "copy text as it stands" rule, every figure was carried over
  exactly as the accepted draft stated it, not re-derived from a raw CSV or cluster output.
- Did not check the assembled manuscript against Applied Energy's own house-style or submission
  requirements (word limits by section, reference style, figure-file format) beyond the specific
  mechanical checks the task doc lists.
- Ran the "no forecast" / "no em-or-en-dash" / "no failure" / "no internal labels" / "no retired
  numbers" checks only on the main manuscript file (Abstract through Conclusion, References
  excluded), as the task doc scopes them; the same greps were also run informally on the SI file and
  noted above, but the SI file was not itself a required check target.
- Did not verify that the 30-item reference list's DOIs/URLs still resolve; copied them byte-for-byte
  from the archive's own reference list without checking any link.
- Did not verify that the duplicate-sentence scan (40+ character exact-match sentences) caught every
  possible near-duplicate; it is an automated exact-match check, not a semantic one, so a
  paraphrased repeat (like the two CITATION NEEDED sentences, which are similar but not identical)
  would not be flagged, and per the task's own rule ("only if word-for-word identical") that is the
  correct behaviour.

## Verified

- Both output files' headers and section order checked by `grep -n "^# "` against the task doc's
  required order (Title, Abstract, Highlights, Keywords, 1 Introduction, 2 Framework, 3 Results,
  4 Discussion, 5 Limitations, 6 Conclusion, References).
- Figure/Table caption uniqueness checked by `grep -n "^\*\*Figure [0-9]"` / `"^\*\*Table [0-9]"` /
  `"^## Table [0-9]"` against every in-text `Figure N` / `Table N` mention: each number appears in
  exactly one caption/heading and is referenced consistently.
- Image-file existence checked with `find`/`ls` against `impl/T71_out/`, `impl/T73_out/`,
  `impl/T74_out/`, `impl/T75_out/`, `impl/T76*`, `impl/T77*`, `impl/T79_in/`, and `../figures/`.
- Reference count (30) and every key's presence in the archive checked by `grep` of each of the 30
  `#ref-<key>` anchors against `../../archive/2J_manuscript_submission.md` lines 491-595.
- Word count (12,076) computed with `wc -w` on the exact `# Abstract` to (end of) `# 6. Conclusion`
  line range of the final assembled file.

## Decisions

- SI document order: S1-S4 (model selection/diary validation) before S5-S9 (schedule completion)
  before S10 (clustering CI), matching each source draft's own internal numbering exactly (no
  reordering needed).
- Excluded each SI draft's opening provenance paragraph from the merged SI file (see Change 15/Open
  item 9).
- Numbered Figures 2-8 (and S1-S2) by each figure's own "home" section rather than by a stray forward
  mention elsewhere in the text (see "Numbering note" under Figure list).
- Did not attempt to merge `tables/SI/Table_B1_B2.md` into the SI file, since it is not one of "the
  three SI drafts" the task doc names for merging.

## Next

- Manager to resolve the "Open for the manager" items above, starting with the FILE NOT FOUND
  figures (item 2) and the "no forecast" check's FAIL verdict (item 6).
- Once figures land, WP10's remaining step (thread `response_map.md`) and WP13 (house-style /
  submission checks) follow, per plan log (dx).

## Status: DONE

## Manager review (2026-09-21, plan log (dz))
- Line 1 title: before = T84 candidate title with `[TITLE: AUTHOR TO CONFIRM]`; after = the original
  submitted title verbatim; why = author order "keep the same title".
- Figure list correction: Figures 2, 7, 8 and S1 are NOT missing. Images exist at
  `impl/T76_out/fig01_athome_by_hour.png`, `impl/T77_out/figure_06_full_vs_avgarm.png`,
  `impl/T73_out/fig07_measured_vs_simulated_shape.png`, `impl/T75_out/fig08_n200_convergence.png`.
- Open item 6 ruled: the three negated "not a forecast" uses are ALLOWED.

- 2026-09-21 (manager): Word copies built with pandoc 3.9: `2J_manuscript_AE_revised.docx`, `2J_SI_AE_revised.docx`. The .md stays the source of record; rebuild the .docx after any .md edit. Equations 17 and 18: `\tag{N}` replaced by `\qquad (N)` in a scratch copy only, because Word cannot convert that form; the .md is unchanged. Only Figure 1 is embedded as an image; Figures 2-8 and S1-S2 are caption text only.
- 2026-09-21 (manager, author asked): all figures now embedded in the .docx via scratch copies (scripts `add_figs.pl`, `si_figs_tail.md` in the session scratchpad). Main: Figures 1-8 (paths as in the corrected figure list, plan log (dz)); the "[image to be inserted from the WP11 output]" tag is dropped in the .docx only. SI: a "Supplementary figures" section is appended in the .docx only, with Figure S1 (`impl/T75_out/fig08_n200_convergence.png`) and Figure S2 (`impl/T74_out/figures/fig09_threshold_sensitivity.png`) under manager-drafted captions marked "[DRAFT CAPTION, TO BE CONFIRMED]", written only from Results 3.7 and 3.8. The .md files are unchanged; the SI clean-up task must write the real captions into the .md.
- 2026-09-21 (manager, author asked for the earlier Word format): main .docx rebuilt with the Building Simulation-era style template `../../extra/build_scripts/ref_submit.docx` (`pandoc --reference-doc`: 12 pt Times New Roman, double spaced, centred page-number footer, 10 pt single-spaced captions), then `../../extra/build_scripts/post.py` run UNCHANGED (tables 10 pt single spaced; 2 tables, xml ok). `finalize.py` NOT applied: its "Fig. N" and de-comma rules were Building Simulation house style, not Applied Energy. Build = `perl add_figs.pl` scratch copy -> pandoc with reference doc -> `py post.py`. The SI .docx gets the same build after T85 is scored.

## T85 SI clean-up (2026-09-21, employee)

Task doc: `../../impl/2026-09-21_T85_wp10_si_cleanup.md`. Edits made to `2J_SI_AE_revised.md` only
(and its rebuilt `.docx`); no cluster, no python, text editing only.

1. S1, about line 30 -- before: the sentence stating Table S1's content is not merged into the file.
   After: "The architecture is summarized in Table S1 below, with the related activity codebook in
   Table S1b." Why: the content is now actually merged (see next item).
2. S1, before "## S2" -- before: nothing (gap). After: inserted Table S1 (Calibrated generator model
   card, reader-facing adaptation of `tables/SI/Table_B1_B2.md`'s Table B1) and Table S1b (Activity
   codebook and co-presence columns, adaptation of Table B2). Why: task item 1. Internal-only
   references stripped during adaptation: the file-provenance line at the top of each source table
   (cites a `.py` file and internal draft names), the `impl/2026-09-15_T04_wp9_threshold_provenance.md`
   path and "WP9"/task-ID reference, and the "(reviewer R2-1)" tag on the plain-term gloss. Numbers and
   technical content kept unchanged. Checked against main-text Results 3.8 ("Four candidate models
   clear all four selection checks"; 0.0191, 4.57, negative 2.03, 0.6355): **no disagreement found**,
   both sources state the same four numbers and the same "best composite among four passers" framing.
   Not fixed / flagged, not resolved: Table B2's "Raw-code magnitudes" column carries five "check
   source" placeholder markers inherited unchanged from `Table_B1_B2.md`; this task has no way to
   verify those counts (no cluster/python) and the task doc's edit list does not cover this cell
   content, so it is carried as-is and reported here, not silently dropped and not invented.
3. S1, same location -- inserted Table S3 (glossary), adapted from `tables/SI/Table_SI_glossary.md`'s
   term table, with a one-line lead-in. Why: task item 2, "next free S number" (S1, S1b and S2 were
   already taken; S3 is next). Placed physically near the start of the document (within S1, before S2)
   even though its number (S3) is not in strict physical order with Table S2 (which stays put in S10,
   since the main text already cites it as "Table S2" and the main text is read-only) -- a deliberate
   numbering choice, not an oversight. Only the term-definition table itself was carried in, not the
   glossary source's own "Terms considered and left out" / "Note for whoever assembles" sections
   (drafting-process content, analogous to the trailers already excluded from the SI by T84). Rewrote
   four rows (COLLECT_MODE, DDAY_STRATA, DRIFT_MATRIX, and their descriptions) to state the plain
   meaning as the row's own label ("Collection-mode flag", "Day-type-stratum flag", "Structural-break
   check") rather than keep the bare internal name as the term column, since item 5 names
   "COLLECT_MODE" specifically for removal from prose; the row's own explanation text already carried
   the plain meaning, so this is a minimal rename, not a new sentence. Updated "SI Table B1" to "SI
   Table S1" in the J3/COLLECT_MODE/DDAY_STRATA rows' "where used" column.
4. S1 intro paragraph (top of file) -- before: "Sections S1 to S10 cover ... clustering-aware
   confidence intervals." After: "Sections S1 to S11 cover ... clustering-aware confidence intervals,
   and the supplementary figures." Why: mechanical update needed once S11 was added (item 3); no other
   wording changed.
5. S7, about line 196 (now ~264 after insertions) -- before: "the 2030 forecast year ... the 2030
   forecast rather than". After: "the 2030 scenario year ... the 2030 scenario rather than". Why: task
   item 5.
6. S8, about line 256 (pre-edit numbering) -- before: "...0.11 percentage points -- inside the
   0.5-point tolerance...". After: em dash removed, replaced with a comma. Why: task item 5.
7. S10 -- before: "(T21, all 24 cells x 50 households, 2,400 rows...)". After: "paired simulation data
   (all 24 cells x 50 households, 2,400 rows...)", no task ID. Why: task item 5.
8. S10 -- two em-dash pairs removed (the cell-cluster-bootstrap method sentence, and the "widens the
   honest uncertainty band" sentence), replaced with parentheses. Why: task item 5.
9. Table S2 (clustering CI table) -- before: two table cells reading "--" (literal double hyphen,
   marking "not applicable" for the plain-pooled row's own "change from plain interval" column). After:
   "n/a". Why: task item 5 counts double-hyphen-as-dash.
10. S10 -- deleted the sentence "Whoever writes the main-text point estimate and 'separable from zero'
    statement for midday share should cite the wider, cluster-aware interval above rather than the
    plain one, since it is the more honest number and the two disagree by a material margin (Ruling
    5)." in full. Why: task item 5, explicit instruction.
11. S10 -- deleted the whole paragraph "A retired, invalid number, kept only for the record (DO NOT
    QUOTE)..." through the end of the (pre-edit) file, including its `impl/T03_scripts/...`,
    "plan §5 items", and "1.0-3.3%" content. Why: task item 5, explicit instruction; this also removed
    the file's only remaining `.py`, `impl/T`, `plan §` and `Ruling`/`DO NOT QUOTE`/`1.0-3.3`
    occurrences (confirmed zero by grep afterward).
12. End of file -- added a new "## S11 Supplementary figures" section with the two image lines
    (`../impl/T75_out/fig08_n200_convergence.png`, `../impl/T74_out/figures/fig09_threshold_sensitivity.png`)
    and captions **Figure S1.** / **Figure S2.**, written from `2026-09-21_T75_wp11_figure8_n200_convergence.md`
    and `2026-09-21_T74_wp11_figure9_threshold_sensitivity.md` (every number in each caption re-derived
    from those docs' own Verified/Decisions sections, not invented). **Disagreement found and reported,
    not resolved**: main-text Section 3.7 describes the sample-size check as covering "24 cells"; the
    T75 doc's own source data (`T28/out/t28_b4_convergence.csv`) covers only 4 archetype cells, all in
    Montreal, x 6 metrics = 24 cell-by-metric COMBINATIONS, not 24 archetype-by-city cells of the kind
    used elsewhere in the paper (the check does not cover the other two cities at all). Figure S1's
    caption states this plainly and flags the wording gap; the main text was not touched (read-only).
    No disagreement found for Figure S2 against Results 3.8 (the "2 of 21 scenarios, one-of-four-to-six
    candidates passing" language matches the CSV exactly).
13. `[VALUE PENDING]` x3 (S6 x2, S8 x1) -- checked against `results_number_sheet.md` (no match for any
    of the three topics: day-type-stratum at-home rate, Saturday/Sunday at-home split, 24-group
    sanity-check drop-count audit) and against every accepted impl doc found by grepping the whole
    `rejection revision/` tree for the three topics' keywords; the only hits were the SI/main-text
    files themselves and the two source drafts (`draft_SI_schedule_completion.md`,
    `2026-09-15_T38_wp10_si_schedule_completion_draft.md`), which state plainly that the value was
    never produced by any run. **None filled.** Left as `[VALUE PENDING: ...]`, unchanged, per task
    item 4's "otherwise leave it."
14. Rebuilt `2J_SI_AE_revised.docx` with the exact pandoc command from the task doc (plain
    `-f markdown -t docx --resource-path=.`, no reference-doc template -- that richer build is a
    separate manager step per the line above). Zero pandoc warnings printed. `unzip -l ... | grep
    media/` confirms 2 embedded images (`rId19.png` 1,436,522 bytes, `rId22.png` 875,513 bytes).

### Checks (recorded)

- `wc -w 2J_SI_AE_revised.md`: **4,470 words before -> 6,438 words after.**
- grep for `—`, `–`, `\ -- \ ` (as a dash), `forecast`, `failure`, `\bT[0-9]+\b`, `.py`, `plan §`,
  `Ruling`, `DO NOT QUOTE`, `1.0-3.3`: **zero hits, all clean.**
- grep for `impl/T`: exactly 2 hits, both are the two allowed image lines in S11.
- grep for `VALUE PENDING`: 3 hits (S6 x2, S8 x1), all pre-existing and left unfilled by design (item
  13 above) -- expected, not a failure of the check.
- grep for `J3`: 3 hits, all inside Table S1's own gloss paragraph/heading or the Table S3 glossary
  row that defines it -- none bare/unglossed.
- Every Figure S / Table S cited in the main text (Table S1, Table S2, Figure S1, Figure S2) has
  exactly one matching caption in the SI, confirmed by grep of both files. Table S1b and Table S3 are
  new tables not cited by the main text (task-doc-directed additions), each also appears exactly once.

### Decisions

- Table numbering: Table S1 = model card (B1, cited by main text), Table S1b = activity codebook (B2,
  uncited, per task's own suggested "S1b" naming so the main-text-cited Table S2 does not have to be
  renumbered), Table S2 = clustering CI (unchanged, main-text-cited), Table S3 = glossary (next free
  integer S number). The main text is read-only, so Table S1 and Table S2's numbers were never
  candidates for change.
- Kept `COLLECT_MODE`/model-card technical labels inside Table S1 itself (a data-dictionary table) and
  the Table S3 glossary (the table item 2 explicitly asks for), since these two tables are the
  project's own sanctioned place for such labels per the glossary's own stated design ("a term earns a
  row only if a reader will still meet it, in a supplementary table"); item 5's "COLLECT_MODE out of
  prose" was applied to the flowing S1-S10 narrative text, not to the technical tables item 1/2
  explicitly instruct to merge in. The Checks-section grep list (task doc, "## Checks") does not
  include `COLLECT_MODE` or `Tier-1` among the required-zero patterns, consistent with this reading.

### Next

- Manager: rebuild the SI `.docx` with the Building Simulation-era reference-doc template once ready
  (per the line above this section), same as the main manuscript's later build.
- Manager/author: confirm the Table S3 numbering choice (next free integer, physically out of strict
  sequence with Table S2) is acceptable, or renumber if preferred.
- Manager/author: decide whether Figure S1's flagged "24 cells" vs "24 cell-by-metric combinations,
  Montreal only" wording gap in the main text (Section 3.7, read-only in this task) needs a main-text
  edit.
- Author: the two genuinely un-fillable `[VALUE PENDING]` items in S6 and the one in S8 still need a
  real cluster run to produce a value, or a decision to drop the sentence instead.

## Manager review of T85 (2026-09-21, plan log (eb))
- T85 ACCEPTED; my re-grep of the SI matches its Verified list (only `J3` x3 glossed, 3 `[VALUE PENDING]` with no source anywhere, 2 allowed image paths).
- SI tables renumbered in order of appearance: S1 model card, S2 activity codebook (was "S1b"), S3 glossary, S4 clustering intervals (was "S2"); main text Results 3.8 now cites Table S4.
- Sample-size check: T75 doc lines 76, 149, 192 confirm 4 Montreal archetype cells x 6 metrics. Main text 3.7 "across 24 cells" -> "across the four Montreal archetype cells and six ... metrics (24 cell-by-metric combinations; ...)", and the run-on "this example and the check as a whole covers Montreal only" -> "The check covers Montreal only." Figure S1 caption: "other two cities" was WRONG (study has six cities) -> "other five cities"; its internal "Note: the main text..." sentence deleted now that the main text is fixed.
- Both .docx rebuilt with `ref_submit.docx` + `post.py` (main: 8 images, 2 tables; SI: 2 images, 6 tables; xml ok).

## T86 paper-voice sweep
Task doc: `../../impl/2026-09-21_T86_wp10_paper_voice_sweep.md`. Author instruction 2026-09-21: no
work-package/project-process wording in the manuscript. File edited: `../2J_manuscript_AE_revised.md`.
No numbers, intervals, citations or claims changed; rewording and one history-only sentence deleted.

1. Section 2.8, sampling pool -- before: "...comparing a rebuilt schedule set against a previously
   published one." After: "...comparing the schedule set used in this study against an earlier one."
2. Section 3 opener -- before: "trace one path through the rebuilt pipeline". After: "trace one path
   through the pipeline".
3. Section 3.3, SHEU check paragraph -- before: "a corrected version of the check ... On the rebuilt
   runs, all 48 ... cells pass this check. The original, uncorrected version of the same script had
   reported only 12 of 48 passing; that shortfall traced to an arithmetic error in the script itself
   for multi-unit buildings, since fixed, and the 12-of-48 figure is retained only as a control
   confirming the fix, never as a project result. No energy-use-intensity figure is available for this
   rebuild on this basis; the previously published per-archetype energy-use-intensity table has no
   reproduced source in the rebuild: [NUMBER NEEDED: EUI]." After: "a check that compares simulated
   and survey end-use totals ... All 48 ... cells pass this check. No energy-use-intensity figure is
   available on this basis; a previously published per-archetype energy-use-intensity table is not
   reproduced here: [NUMBER NEEDED: EUI]." The bug-fix-history sentence (original 12/48, arithmetic
   error) was deleted; it existed only to narrate a fix, not a study result. `[NUMBER NEEDED: EUI]`
   kept verbatim.
4. Section 3.4, peak/ramp -- before: "no confidence interval is available for either metric in the
   accepted output". After: "no confidence interval is available for either metric".
5. Section 3.4, peak-hour trend -- before: "exists in the rebuilt outputs; neither is stated here."
   After: "is reported; neither is stated here."
6. Section 3.5, fixed-schedule arm -- before: "A separate fixed-schedule arm was built earlier in this
   project but is not part of this comparison, since it is not a home-for-home comparison and was
   excluded on that basis." After: "A separate fixed-schedule arm is not part of this comparison, since
   it is not a home-for-home comparison."
7. Section 3.5, per-city range -- before: "...since that is the only archetype for which the accepted
   comparison table's per-city rows were read for this draft." After: "...since that is the only
   archetype for which the comparison table's per-city rows are reported here."
8. Section 3.6, sanity ratio -- before: "Two further checks support the rebuild's plausibility. First,
   a sanity ratio between the occupancy-only rebuild and the previously published (and now superseded)
   campaign shows the occupancy rebuild barely moved annual whole-building electricity". After: "Two
   further checks support the plausibility of these results. First, a sanity ratio between the
   occupancy-only simulations and a previously published campaign shows that occupancy-only changes
   barely moved annual whole-building electricity". Ratio values (1.0075, 0.9997, 1.0017, 1.0072)
   unchanged.
9. Section 4 (Discussion), SHEU check -- before: "On the rebuilt runs, all 48 ... cells fall inside the
   report-only band". After: "All 48 ... cells fall inside the report-only band".
10. Section 4, plug-load intuition -- before: "...on this rebuild, these two meters move in the
    opposite direction...". After: "...in this study, these two meters move in the opposite
    direction...".
11. Section 5 (Limitations), before-and-after schedules -- before: "The chosen model of occupant
    behaviour was rebuilt on diaries drawn only from the most recent survey year, replacing an earlier
    build that mixed in older survey years. This rebuild changes which households pass the simulation
    engine's own data-quality check, so the pool of households actually simulated is not the same pool
    as in the originally submitted results: ... the rebuilt pool holds 16,326 paired households against
    16,208 in the original...". After: "The model of occupant behaviour used here draws diaries only
    from the most recent survey year, unlike an earlier version that mixed in older survey years. This
    choice changes which households pass the simulation engine's own data-quality check, so the pool of
    households actually simulated differs between versions: ... the current pool holds 16,326 paired
    households against 16,208 in the earlier version...". Kept as a plain limitation statement per the
    task doc's Section 5 allowance; household counts (16,326, 16,208, 320) unchanged.
12. Section 1.2, companion-line note -- before: "...its publication status is unconfirmed and marked
    for the author." After: "...its publication status is unconfirmed." (`[STATUS TO CONFIRM BY
    AUTHOR]` placeholder earlier in the same table row, line 88, left untouched.)

### Remaining grep hits after the sweep, and why each stays
- Lines 88, 141: "manuscript" (substring match on "script" in the grep pattern) -- ordinary
  scientific-English word, refers to the authors' own companion journal paper; not notebook wording.
- Lines 726, 745, 749: "descriptive"/"description" (substring match on "script") -- ordinary English,
  not code-script wording.
- Line 967: "could rebuild the same generator, the same held-out-year evaluation, and the same paired
  stock-scale design for its own housing stock" (Section 4, generalizability paragraph) -- this uses
  "rebuild" as a forward-looking verb describing what another country's researchers could do to
  replicate the method; it does not describe this project's own build history, so it is left as
  written per the task doc's scope ("describes how the project was run rather than what the study
  did"). Flagged here for the manager to overrule if a stricter reading is wanted.
