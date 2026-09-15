# T35 — WP11: workflow diagram, image PROMPT only

Task doc and implementation state in one file. Written by the manager 2026-09-15 (plan log (av)).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster. Never create or draw an image.**

## Aim
Write the text prompt the author will paste into an image generator to produce Figure 1, the workflow diagram
requested by reviewer 1 (plan §2 M2a). Output: `writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md`
(create the folder locally if it does not exist).

## Inputs (read; do not edit)
- `../manuscript/draft_S2_framework.md` (the accepted Section 2 draft: the stages, Table 1, the equations).
- `2026-09-15_T34_wp10_framework_equations_draft.md`, section "Manager review" only.
- `../00_REVISION_PLAN.md` §3 WP10 (lines 355 to 400) and WP11 (lines 402 to 414).

## Content of the prompt file
1. One paragraph: purpose, journal (Applied Energy), print width (double column, 190 mm), target 600 dpi, white
   background, colour-blind-safe palette, sans-serif labels, no decorative icons or 3D effects.
2. The exact boxes, in order, with the exact label text for each box (short plain labels, at most 6 words each), grouped
   in three bands: **Data** (the datasets of Table 1), **Occupancy model** (sections 2.1 to 2.7), **Building
   simulation and analysis** (sections 2.8 to 2.12). The IESO measured data box connects only to the comparison stage,
   drawn with a dashed arrow and labelled "external check, not an input".
3. The exact arrows (from box, to box, solid or dashed), as a numbered list.
4. Where the three 2030 scenarios branch (persistence share 1, 0.5, 0) and where the two comparison arms (fixed
   schedule, one average profile) branch.
5. A "must not" list: no result numbers, no internal labels (J3, True-Future-Test, frozen frame, Tier, FailSafe,
   COLLECT_MODE, DDAY_STRATA, Step-8, Step-9, occACT, gate), no word "forecast" (write "scenario-based projection"),
   no logos, no invented stages or datasets, no text outside the listed labels.
6. A short checklist the author uses to accept the generated image (every box present, every arrow direction right,
   labels spelled exactly, legible at print width).

## Rules
- Every box and arrow must map to a stage or dataset in the Section 2 draft; add a final table "box → draft section".
- No em dashes and no en dashes. Do not create any other file. Never generate an image.
- Append to "Ledger" and "Verified" below; end the turn when the prompt file exists.

## Ledger

Status: DONE. Read CLAUDE.md, this task doc, `../manuscript/draft_S2_framework.md` (full file, 414
lines), `2026-09-15_T34_wp10_framework_equations_draft.md` (Manager review section only, plus enough
of the rest to see what T34 verified), `../00_REVISION_PLAN.md` lines 355 to 414 (WP10 and WP11), and
`2026-09-15_T02_wp5_ieso_measured_profiles.md` (to confirm how the IESO comparison relates to Section
2.10 to 2.12, needed to place the "Measured vs simulated comparison" box correctly). Checked the
folder structure with `find`/`ls` before writing (see Decisions, path resolution). Wrote one file:
`2J_docs_occ_nTemp/writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md` (created
both `figures/` parent, which already existed from the archived original submission, and the new
`Prompts_Images/` subfolder).

## Verified

- Every one of the 24 boxes in the prompt traces to a named row of Table 1 or a lettered subsection
  (2.1 to 2.12) in `draft_S2_framework.md`; the prompt file's own closing table repeats this mapping
  so the author can check it without re-opening this doc.
- Every one of the 32 arrows connects two boxes that the draft text actually links: diary to
  harmonisation (opening paragraph), harmonisation to both the generative model and raking (2.1 last
  sentence, 2.3 opening "the model's or the projection's at-home marginal"), the three lambda branches
  and their loop back into raking (2.7: "the same raking mechanism as section 2.3... raked exactly as
  there"), matching feeding both aggregation and end-use loads with end-use looping into aggregation
  (2.5: "the equipment and lighting fractions from section 2.6 are attached to the same
  household/day-type/hour rows", 2.6: "built... from the same household diary, before the 48-to-24
  averaging of section 2.5"), the two comparison arms keeping the sampled households and the
  calibrated design powers but not the framework's own schedule shape (2.12: "the same sampled
  households and the same per-household calibrated design powers", "only the sub-daily shape is
  replaced"), and the IESO dashed arrow landing only on the comparison box, never on the simulation or
  metrics boxes directly (Table 1 IESO row: "no simulation input role").
- Confirmed by rereading Table 1 and 2.9 to 2.10 together: the draft's subsection order lists stock
  aggregation (2.9) before load-shape metrics (2.10), but 2.9's own text says a national metric is
  "the weight-average of the 24 cells' values" (values = the per-cell metrics section 2.10 defines).
  The prompt therefore orders the boxes "Building simulation" then "Load-shape metrics per cell" then
  "Stock aggregation to national figure" (arrows 28, 29), the true data-dependency order, not the
  manuscript's expository order. Recorded as a decision below since it departs from subsection
  reading order.
- Confirmed the archived original submission's figures live at
  `2J_docs_occ_nTemp/writing/submission/figures/` (`Figure_01_pipeline.png` etc., `ls` output), which
  is the existing folder the new `Prompts_Images/` subfolder was added under.

## Decisions

- **Path resolution for the output file.** The task doc names the output as
  `writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md` and states relative paths
  are relative to `impl/`. Taken completely literally that would create a new, nested
  `impl/writing/submission/figures/...` folder, duplicating "writing/submission" a second time inside
  itself, which does not match any existing structure. `CLAUDE.md`'s own hard rule states the
  deliverable goes "under `<paper>_docs_*/writing/submission/figures/Prompts_Images/`", and I found a
  real, already-existing `2J_docs_occ_nTemp/writing/submission/figures/` folder (holding the original
  submission's PNGs) that matches this pattern exactly, sibling to `rejection revision/`, not nested
  inside it. I resolved the output path against the paper root (`2J_docs_occ_nTemp/`) per the
  `CLAUDE.md` hard rule and the folder evidence, not against `impl/` literally. File written to
  `2J_docs_occ_nTemp/writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md`. If this
  is not the intended location, the file is a plain markdown file and can be moved without changing
  its content.
- **Added one box not named as its own lettered subsection: "Building simulation".** Sections 2.8 and
  2.9 assume a simulation run happens between sampling and aggregation, and Table 1 states weather
  files and archetype models are "Building simulation input" for exactly those two stages, but no
  subsection title covers the simulation step itself. Omitting it would have broken the pipeline (an
  arrow straight from sampling to national aggregation, skipping the physical simulation, would be
  false). Added the box, mapped in the closing table to the Table 1 dataset-role citations, flagged
  there as the one box without its own subsection.
- Ordered "Load-shape metrics per cell" before "Stock aggregation to national figure" in the diagram
  (see Verified above), reversing the draft's own subsection numbering (2.9 before 2.10), because 2.9's
  text only makes sense once the per-cell metric values it aggregates already exist.
- Kept the fixed-schedule arm's inputs as "Household sampling per cell" and "Activity-driven end-use
  loads" only (same households, same calibrated design powers), not "Household aggregation to
  schedules", since 2.12 says the fixed arm replaces the household's own schedule shape entirely; the
  average-profile arm does draw from "Household aggregation to schedules" since 2.12 says it "uses the
  framework's own diaries".
- Did not add a separate box for "the comparison arms" as a parent grouping label; the two arms
  (fixed, average) are drawn directly as the two branch boxes, per the task doc's instruction to name
  branch points, not to add an extra summarising box.
- No em dashes or en dashes used anywhere in the prompt file or this entry.

## Next

Nothing further planned for T35. The prompt file is ready for the author to paste into an image
generator. A later task should decide whether the generated image needs a second look once produced
(per `CLAUDE.md`'s figure rule: "verify against the installed document" after the author generates and
inserts it), since that verification cannot happen before an image exists.

## WHAT I DID NOT VERIFY

- Did not re-open `impl/2026-09-15_T33_wp10_response_map_and_prep.md` or any WP10 task doc besides T34
  and the T02 IESO doc; relied on `draft_S2_framework.md` itself (the accepted output of T34, per this
  task's own "Inputs" instruction) as the authority for every box and arrow, rather than re-deriving
  from the underlying code files T34 already cited.
- Did not check whether an image generator can actually render a diagram this dense (24 boxes, 32
  arrows, one dashed, three curved return arrows) legibly in one pass; the prompt asks for it but
  producing and judging the actual image is explicitly out of scope (never generate an image) and is
  the author's step.
- Did not check `2J_docs_occ_nTemp/writing/submission/archive/` for whether the original
  `Figure_01_pipeline.png` prompt (if one exists there) used a different box/arrow convention worth
  matching stylistically; only confirmed the archived PNG's existence and location, not its content.

## Status
DONE.

## Manager review (plan log (aw))
The prompt followed the draft's section order, which put raking before matching. The code rakes AFTER census
linkage (`05_postlink_rake.py:1-20`, "Post-Linkage"; it rakes the model-generated rows to the real respondents'
rate), and the 2030 rake works on the matched stock, with its trend taken from the observed cycles
(`06_forecast_rake.py:100-161`). Corrections to the prompt: boxes 9 and 10 swapped; arrows 4, 5, 7, 8 now run
model -> matching -> raking -> aggregation and end-use loads; arrow 11 now runs harmonised diaries -> scenario
construction; arrow 30 now runs per-cell metrics -> paired interval (the interval is household-level, not from the
national aggregate, `08_simulation_val.py:957-975`); new arrow 33 sampling -> average-profile arm. Output location
accepted (paper `figures/Prompts_Images/`). The Section 2 draft's 2.3 text was also corrected (applied after
matching, what each rake targets, the single-person floor guard); WP10 should put 2.4 before 2.3.
**Status: T35 DONE (accepted with corrections).**
