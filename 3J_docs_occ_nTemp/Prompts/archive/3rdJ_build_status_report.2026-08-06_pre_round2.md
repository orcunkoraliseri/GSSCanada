# 3J build status report

**Date:** 2026-08-06 · **Mode:** RUN TO COMPLETION (user instruction, *"continuer jusqu'a la fin avec
des taches"*) · **Ledger:** `writing/implementation/3rdJ_paper_TASKS.md`
**Brief:** `writing/implementation/3rd_Occ_Journal_BuildInstructions.md` §9 template

**Twelve tasks, twelve closed. Nothing BLOCKED.**

---

## STEP 1 - Asset verification

**Deliverable figures found** in `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` - five,
as predicted: `fig_diurnal_4ch.png`, `fig_eui_4ch.png`, `fig_longitudinal_4ch.png`,
`fig_peakhour_4ch.png`, `fig_scenario_4ch.png`.
`Step5_docs/outputs_step5/` holds the two expected PNGs (`3rdJ_25CEN_aug_BEM_temporals.png`,
`3rdJ_25CEN_aug_Validation_Plot.png`); neither is in the relocation table, both left in place.
`Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` and
`Leg2_2-split/Residential-Office_Pipeline.png` both exist.

**Source directory used for every result figure:**
`Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` - the frozen canonical arm, never the
superseded `outputs_step9/`.

**Provenance recorded for `fig_diurnal_4ch.png`** (the one file the content check can never see,
because it is byte-identical in both arms): copied from
**`Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/`**. Recorded at copy time in Progress
Log #2 because it cannot be recovered afterwards. It does not generalise: the other four figures do
differ between the arms and the check distinguishes them.

**All seven copies verified by md5 against their named sources on disk**, source and copy compared
pairwise, all seven pairs identical, all hashes full 32-hex (Progress Log #2).

---

## Bucket A - Schematics (8)

- [x] Fig 1 pipeline   [x] Fig 2 roadmap   [x] Fig 3 three-head   [x] Fig 4 projection
- [x] Fig 5 tag2       [x] Fig 6 hotel     [x] Fig S1 shares      [x] Fig S2 levers

Prompt text only; no image generated. Figure 3 is labelled **"3 GSS heads + 1 non-GSS side-track"**
in three places, and the string "4 heads" appears only inside instructions not to render it.

## Bucket B - Tables (10)

- [x] T1 gap  [x] T2 channels  [x] T3 domain  [x] T4 gates  [x] T5 EUI bands
- [x] T6 leg2/leg3 delta  [x] T7 limitations  [x] A1-A2  [x] B1 rounds  [x] Appendix C

## Bucket C - Relocations (7)

All seven relocated. Sources and md5s in Progress Log #2.

## Bucket D - Chapters (9)

All nine drafted: Front Matter, Introduction, Datasets, Methods, Experimental Design, Results,
Discussion, Limitations, Conclusion.

## Assembly

`fullSet/3J_full_manuscript.md` and `fullSet/readySubmission.md`, **2,186 lines each, md5
`c68924293b636061398154d9e31de948` on both**. Built by `fullSet/assemble_3J.py` in **one assembly
pass**: the document is composed once into a single in-memory string and that same string is written
to both files, so they cannot diverge. Both additionally carry a **campaign-identifier block** naming
the arm (base + V2-D9 + V2-D10), the frozen source directory, the 56/56 cell count and the 17/10/3
scorecard, so a future divergence would be visible rather than silent. All 10 tables and all 7 figures
are inlined at placeholders; the appendix-of-leftovers is empty.

---

## Checks, all re-run AT CLOSURE

| check | result | note |
|---|---|---|
| `f1_frozen_input_check.py` | **4 PASS / 0 FAIL** | ⚠️ scans `improvements/v4` scripts, **not** this round's output. Green about something else. |
| `f2_no_reopen_check.py` | **4 PASS / 0 FAIL** | ⚠️ same scope caveat: reads the v4 plan, not this build. |
| `f3_asset_provenance_check.py` | **4 PASS / 1 FAIL** | C1 PASS. The C2 failure is explained below and was pre-registered before closure. |
| `f4_prose_rules_check.py` (new) | **6 PASS / 0 FAIL** | falsifier run: C1 and C6 both proved to have teeth. |

**The f1/f2 scope caveat is stated rather than glossed.** Both are green, and neither examines the
manuscript. The gap they leave over manuscript text is what `f4` was written to cover.

**The `f3` C2 failure, explained and not waved through.** C2 names exactly two assets:
`figures/graphicalAbstract.png` and `figures/SI/Figure_S03_leg2_pipeline.png`. Neither is a Step-9
output; they come from `Leg3_4-split/` and `Leg2_2-split/` and were never in either arm, so they are
absent from the frozen registry - while brief §6 instructs copying them. Verified **against disk**:
each copy's md5 equals its named source's md5. **The brief's predicted "5 PASS / 0 FAIL" conflicts
with the brief's own instruction, and the prediction is the part that is wrong.** `f3` was **not**
modified: narrowing C2 would silence the arm that catches a genuinely regenerated or edited figure.
Standing expectation amended instead - the correct result is **C1 PASS with C2 naming exactly these
two files and nothing else**. Any third name, or any C1 hit, is a real failure.

**New tool this round.** `writing/implementation/f4_prose_rules_check.py`, in the f1/f2/f3 idiom.
C1 em/en dashes · C2 the phrase "four building archetypes" only ever negated · C3 the superseded
`outputs_step9/` never cited as a source · C4 every file names a source · C5 a **vacuity guard** that
FAILS if fewer than ten files are scanned · C6 every number in the front matter and conclusion is
stated somewhere else in the manuscript. `--falsify` injects an em dash and a drifted abstract figure
and confirms C1 and C6 both still fail. **It exists because a `grep -P` sweep returned exit code 2
and was read as "clean"; 96 dashes were actually present.**

---

## Flags

### Values left blank with `⚠ check source` - ~~13~~ **19** in total

🔴 **Corrected at closure, and the correction is the point.** The figure ~~13~~ was written from the
employees' own reported counts, added up by hand and never enumerated. Enumerated from the files, the
marks total **19**. A count taken from a summary rather than from the artefact is the failure this
project keeps finding in other people's documents; here it was in this report, in the paragraph
introducing the honesty table. The table below is the enumeration.

| where | cell | why |
|---|---|---|
| Table 6 | Bit-identical? on Steps 1, 2, 3, 5, 8 (5 cells) | no cross-leg byte or column comparison exists; running one needs a simulation |
| Table 6 | the measured ΔJS for the Step-4 regression gate | value not located in the artefacts read |
| Table 5 | office and residential empirical-band **central** (2 cells) | `info_central` is not a column in the deliverable CSV; a midpoint was not invented |
| Table 1 | Doma & Ouf: time-series occupancy, calibrated behavioural model, stock-scale (3 cells) | not characterisable from dr_L3-10 or the 2J matrix, and deep research is external |
| Table 1 | Buttitta & Finn: calibrated behavioural model, activity/end-use resolved, stock-scale (3 cells) | same |
| Figure 2 prompt | Leg-1 to Leg-2 residential bit-identity | only the Leg-2 to Leg-3 reuse is sourced |
| Chapter 2 | ISQ and CBRE/Travel Alberta catalogue identifiers (2) | citation work belonging to an external round |

**Enumeration, by file and line, produced with a scan rather than by adding up reports:**

| file | marks | where |
|---|--:|---|
| `tables/Table_01_gap_matrix.md` | **6** | lines 9 and 10, three cells each |
| `tables/Table_06_leg2_leg3_delta.md` | **6** | lines 12, 13, 14, 16, 19 (bit-identity, Steps 1/2/3/5/8) and line 15 (the Step-4 ΔJS value) |
| `tables/Table_05_eui_bands.md` | **2** | lines 15 and 18, the empirical-band central cells |
| `tables/Table_04_validation_gates.md` | **1** | line 68, the decode thresholds are named only in a provenance blockquote, never as a gate row |
| `chapters/Chapter_02_Datasets.md` | **2** | lines 106 and 109, the ISQ and CBRE catalogue identifiers |
| `chapters/Chapter_04_ExperimentalDesign.md` | **1** | line 46, a pointer that 85.45 belongs in Table 5 |
| `figures/Figure_02_three_leg_roadmap.md` | **1** | line 20, Leg-1 to Leg-2 bit-identity not sourced |
| **total** | **19** | |

*(A further seven occurrences of the string are prose explaining the convention rather than marking a
value; they are excluded. The two assembled files in `fullSet/` reproduce all of the above and are not
counted twice.)*

### Places a project-chosen threshold was at risk of being cited to the literature

**One, and it was handled by design rather than caught late.** Table 4 carries a mandatory
`Provenance` column classifying all 28 threshold rows: **2** to ASHRAE Guideline 14 (NMBE, CV(RMSE)),
**1** heuristic (PR-AUC >= 0.15 / F1 >= 0.25), and **25** as `project-chosen (set before tuning)`.
No project-chosen threshold is cited to the literature anywhere in the manuscript.

### Confirmation

🟢 **No band value was moved and no gate verdict was changed.** Verified rather than asserted:
`step9_gates.json` in the frozen deliverable still reads **30 gates, 17 PASS / 10 INFO / 3 FAIL**,
with the three FAILs still `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`. Every data file in
`outputs_step9_deliverable/` still carries its **2026-08-06 00:05** freeze timestamp. (`_PROVENANCE.md`
in both Step-9 directories shows 20:21 the same day; a sweep of files modified in that window returns
eleven, all of them the *previous* session's v4-closure and writing-phase setup - the build brief,
`PAPER_SERIES.md`, the manager prompt, `f3`. Nothing in this session touched the deliverable.)

---

## Six things this build changed about what the manuscript may claim

1. 🔴 **The additive claim is weakened to what the evidence supports.** Of nine pipeline steps, only
   Step 7 (base prototype geometry) is provably bit-identical; three are explicitly No; five carry no
   cross-leg comparison. The injector `integration.py` exists in three non-matching copies. The paper
   claims **additive by construction** and explicitly does not claim *"no prior figure invalidated"*.
2. 🔴 **Leg-2's published office EUI 172.7 is superseded by V4-B2's 106.56** (verdict unchanged, IN
   both before and after). Magnitudes must be the corrected value.
3. 🔴 **The consolidated limitations section numbers `L8` twice** - seventeen statements under sixteen
   IDs, found independently by two readers. Table 7 follows the source's own count of sixteen, with
   the collision documented and a reopen trigger. **No manuscript sentence may claim the count was
   verified.**
4. 🔴 **The shipped model checkpoint was selected by a composite score**, which the project's own
   standing principle forbids. Already a decided item (V3-H1, option C) with three reopen triggers.
   Now disclosed in Methods §3.2 rather than only in the SI.
5. 🔴 **Hotel is deliberately uninjected in 2005/2010/2015** (QC ground truth starts 2019), so its
   flatness across cycles is a campaign-design artefact. Stated in Results §5.1 where a reader meets
   the longitudinal result, not only in Limitations.
6. **The retail median sits 5.47 % below its floor, not 0.15 %.** The 0.15 % is the decision margin of
   the retired all-cells rule. A first draft conflated them; both now appear with the distinction
   stated.

## Two things a human must decide

1. **`readySubmission.md` still carries build apparatus.** The inlined tables bring their own
   "Sources" and "Manager notes" blocks into the assembled file. That is deliberate for a working
   draft and traceability, and wrong for an actual submission. Stripping it is an **editorial** pass,
   not a data question, and it was not done automatically because an automated strip could silently
   remove a caveat.
2. **The abstract runs 225 words** against the brief's ~180 target. 2J's own shipped abstract runs
   240, so this is in house style, but it will need trimming to a target journal's limit.
