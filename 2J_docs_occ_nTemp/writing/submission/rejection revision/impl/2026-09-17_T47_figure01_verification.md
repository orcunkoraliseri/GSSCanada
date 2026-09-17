# T47 - Figure 1 verification and overwrite check (2026-09-17)

VERDICT: ACCEPT WITH FINDINGS

The new Figure 1 workflow diagram matches the prompt spec on every checkable item
(24 boxes, 33 arrows, band structure, print size/DPI, must-not list). Two
process findings need the manager's decision: (1) an old figure file was
silently overwritten, recoverable from a backup copy, and (2) the generator
script overwrites four fixed output paths on every run regardless of the
--out flag, so it must never be rerun casually.

## Part A - the overwrite

### A1. Are submission/figures/Figure_01_pipeline.png and
submission/figures/Figure_01_workflow.png byte-identical?

YES. SHA-256 hashes computed with python (hashlib), both files:

- submission\figures\Figure_01_pipeline.png
  size = 666675 bytes, mtime = 2026-09-17T15:20:41.740662
  sha256 = c2c198e85e04dba625839ae5e92c3beb579d2bf16469f954637e4cfef376e11c

- submission\figures\Figure_01_workflow.png
  size = 666675 bytes, mtime = 2026-09-17T15:20:40.807756
  sha256 = c2c198e85e04dba625839ae5e92c3beb579d2bf16469f954637e4cfef376e11c

Same hash. The pipeline.png file now holds the new workflow diagram, not the
old pipeline overview it used to hold.

Also hashed for completeness:
- submission\figures\Figure_01_workflow.pdf: size = 40219 bytes,
  mtime = 2026-09-17T15:20:41.420103,
  sha256 = 30b05b99e04a4ac2886823fe29c1052fd4d317d412acea4f249ca9b80db73f04
- submission\figures\Prompts_Images\Figure_01_workflow.png: size = 666675 bytes,
  mtime = 2026-09-17T15:20:41.132307, sha256 = same as above
  (c2c198e85e04dba625839ae5e92c3beb579d2bf16469f954637e4cfef376e11c)

### A2. Is writing/figures/Figure_01_pipeline.png different, and what is it?

YES, it is a different file and it was NOT touched by the new run:

- writing\figures\Figure_01_pipeline.png
  size = 1871483 bytes, mtime = 2026-06-11T21:30:21.780197
  sha256 = 97aeb83bb0594535a0a7767081cb7e86e91d32e6ec16981b551756b23cbafc1a

Different size, different hash, June date, not September. This is the pre-
overwrite original and it still exists on disk. The overwrite did NOT destroy
anything unrecoverable: a full, byte-exact copy of the old image survives at
this path.

### A3. What did the OLD Figure 1 depict?

Read writing\figures\Figure_01_pipeline.md (the caption/prompt file that was
used to generate the old image). It specifies an axonometric (isometric)
graphical-abstract style pipeline, NOT the new flat 3-band box-and-arrow
workflow diagram. Old scene, left to right: "GSS Diaries" and "Census PUMF"
data-table icons -> "Harmonize" -> "Generator" (amber-highlighted, with a
neural-network glyph) -> "Census Linkage" -> "Forecast" -> "BEM Schedules" ->
"Simulate" (with small iso-house glyphs) -> "End-Use Loads" -> "Outputs" (bar
chart/curve glyph). Nine stages, each carrying its own overlay annotation
naming a project step, section code, and headline numbers (e.g. "64,061
diaries", "144,507 households", "6,000 runs", "48/48 cells <= +/-2.7% of
SHEU"). This is a visually and substantively different figure from the new
one: old = axonometric icons with result numbers overlaid per stage; new =
flat rectangles/arrows with no numbers, per the Applied Energy spec's
must-not list.

Note: the old prompt file itself is for a DIFFERENT image generation
convention (icons/axonometric, numbers overlaid afterward) than the new
spec (plain boxes, no numbers, no icons). The two are not simply two drafts
of the same figure; they are two different figure concepts, one retired.

### A4. Which filename does the manuscript actually reference?

Grepped every .md source under writing\submission and writing\submission\
rejection revision\manuscript for "Figure_01", "Figure 1", "fig01", and
"pipeline".

Live manuscript in progress (target: Applied Energy, this is the one that
matters going forward):
- writing\submission\rejection revision\manuscript\draft_S2_framework.md:3
  contains only a placeholder: "[Figure 1: workflow, image prompt to be
  written in WP11]" -- it does NOT yet cite a filename. Confirms the figure
  insertion step has not happened yet in the live draft.
- writing\submission\rejection revision\00_REVISION_PLAN.md:1119-1126, 1550-
  1595 record that T35 wrote the prompt spec and the author was to generate
  the image "when convenient"; no filename is hard-referenced there beyond
  the prompt file path itself.

Old, REJECTED, ARCHIVED Building Simulation submission (superseded, not the
live target, but still on disk and still internally consistent in its own
text):
- writing\submission\extra\2J_manuscript_submission_BEFORE_journalform.md:124
  ![Figure 1](figures/Figure_01_pipeline.png)
- writing\submission\extra\2J_manuscript_submission_BEFORE_osman_orcid.md:122
  ![Figure 1](figures/Figure_01_pipeline.png)
- writing\submission\extra\2J_manuscript_submission_BEFORE_refs_captions.md:124
  ![Figure 1](figures/Figure_01_pipeline.png), and line 122 carries the old
  caption text ("End-to-end occupancy-to-energy pipeline (Steps 1-9)...").
- writing\submission\extra\2J_manuscript_submission_BEFORE_prose_cleanup.md:124
  ![Figure 1](figures/Figure_01_pipeline.png)
- writing\submission\extra\2J_manuscript_submission_BEFORE_short_captions.md:122
  ![Figure 1](figures/Figure_01_pipeline.png)
- writing\submission\extra\Blinded_Manuscript_BEFORE_journalform.md:105
  ![Figure 1](figures/Figure_01_pipeline.png)
- writing\submission\archive\submissionDocs\Blinded_Manuscript.md:105
  ![](figures/Figure_01_pipeline.png)
- writing\submission\archive\2J_manuscript_submission.md:124
  ![](figures/Figure_01_pipeline.png)

So: the filename "Figure_01_pipeline.png" is referenced only by OLD, already
-rejected Building Simulation submission drafts (archive/ and extra/), each
of which still carries the OLD caption text describing the axonometric
pipeline diagram. Those files now point at an image on disk that no longer
matches their own caption, because the file was overwritten. The CURRENT,
live Applied Energy revision manuscript does not reference either filename
yet - the figure insertion step is still pending.

The generator script itself (generate_fig01_workflow.py, confirmed by
reading it in full) writes to four fixed paths every run, one of which is
literally named Figure_01_pipeline.png (see Part C) - so the overwrite was a
deliberate act of that script, not an accident of the tool picking a random
name that happened to collide.

### Recommendation (one action, manager decides)

Restore submission\figures\Figure_01_pipeline.png from the untouched backup
at writing\figures\Figure_01_pipeline.png (byte-exact copy exists, sha256
97aeb83b...), so the old, archived Building-Simulation submission drafts
that still hard-reference this filename and its caption stay internally
consistent for the historical record. Then have the live Applied Energy
draft cite Figure_01_workflow.png (or Prompts_Images/Figure_01_workflow.png)
under its own name once WP11 inserts the figure, so the two figures never
share a filename again. Do not touch generate_fig01_workflow.py's hardcoded
pipeline_out write path without the manager's sign-off (see Part C finding).

## Part B - image vs spec checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Box count = 24, exact labels | PASS | Counted 6 (Data) + 10 (Occupancy model) + 8 (Building simulation and analysis) = 24 boxes in the rendered PNG, matching the spec's 24-item list. Labels verified NOT by eye but with a python script that extracted the spec's 24 numbered box strings by regex from Figure_01_workflow_prompt.md and the script's BOX_LABELS dict by regex from generate_fig01_workflow.py, and diffed all 24 pairs: 0 mismatches. |
| 2 | Arrow count = 33, only arrow 32 dashed, directions correct | PASS (verified via script, not by eye) | 30+ arrows cannot be reliably counted by eye at this density, so I read generate_fig01_workflow.py's drawing code line by line instead. Every one of the 33 spec arrows (1 to 33) has exactly one corresponding draw call, each labelled by number in a comment, each using the same box-to-box direction as the spec list. Only arrow 32 (box 6 IESO -> box 24 Measured vs simulated) passes dashed=True; the other 32 calls use the default dashed=False. Arrow label text on arrow 32, "external check, not an input" (script constant ARROW_LABEL_32), is character-for-character the spec's required label and is visible in the rendered image running vertically along the dashed line at the right edge. |
| 3 | Band structure and titles | PASS | Three bands rendered top to bottom: "Data" (light blue), "Occupancy model" (light amber/sand), "Building simulation and analysis" (light lavender), each with a left-margin title, matching the spec's three names, order, and wording. Script's BAND_TITLES dict values, once newlines are joined back to spaces, equal the spec's three band-title strings exactly. |
| 4 | Print size and resolution | PASS | Read the PNG with Pillow. Pixel size 4488 x 3732. Embedded DPI (599.9988, 599.9988), i.e. 600 dpi. Physical width at that DPI = 4488 / 600 * 25.4 = 190.0 mm, height = 158.0 mm. Matches the spec's "190 mm wide, at least 600 dpi" exactly; the script's own WIDTH_MM/HEIGHT_MM constants (190.0, 158.0) confirm this was the deliberate target, not a coincidence. |
| 5 | Legibility (no clipped/overlapping/too-small labels) | PASS, with a caveat | Visual inspection of the rendered PNG (viewed at 2000x1663 on-screen, downscaled from the true 4488x3732 file) found no box label clipped by its own box edge and no label overlapping another label or box. All 24 box texts sit fully inside their rounded rectangles with visible margin. The one caveat: several hub boxes (10 "Marginal raking of at-home targets", 11 "Household aggregation to schedules", 18 "Building simulation") have many arrows converging on them at close spacing, and the three curved persistence-share return arrows arrive at the bottom of box 10 close together; this is arrow-line congestion, not text clipping, and it follows directly from the spec's own topology (many-to-one arrows into those three boxes) rather than being a placement defect. I could not zoom into the file at full 4488x3732 pixel resolution through this tool, so a final pixel-level legibility check at literal 190 mm print size (e.g. opening the PNG at 100 percent in an image viewer, or a physical proof print) was not done here. |
| 6 | Must-not list (no result numbers, no internal codes, no "forecast", no watermark/logo/author name) | PASS | Visual inspection of the rendered image found no numbers, percentages, internal project codes (J3, True-Future-Test, frozen frame, Tier, FailSafe, COLLECT_MODE, DDAY_STRATA, Step-8, Step-9, occACT, gate), the word "forecast", logos, watermarks, or author names anywhere in the figure. This is corroborated structurally: the script only ever calls ax.text() with three sources of text - BOX_LABELS/BOX_WRAPS (already diff-checked clean against the spec in item 1), BAND_TITLES (checked in item 3), and the single ARROW_LABEL_32 string "external check, not an input" - so no other text string can appear in the rendered output regardless of how it looks on screen. |

## Part C - the generator script

- generate_fig01_workflow.py (27338 bytes) is a self-contained matplotlib
  script. It imports only sys, os, argparse, and matplotlib (Agg backend,
  FancyBboxPatch, FancyArrowPatch, PathPatch, Path); it reads no external
  data files and calls no network or project-specific modules. Given a
  working Python + matplotlib install, it needs nothing else from the
  repository to run.
- Box label strings were checked programmatically against the spec (Part B,
  item 1): 0 mismatches across all 24. The script also self-checks this at
  import time: lines 87-91 assert that each BOX_WRAPS entry, once its line
  breaks are collapsed back to spaces, equals the corresponding BOX_LABELS
  entry, so a future hand-edit that broke a line wrap and changed the
  underlying text would fail loudly at run time.
- Rerun command: `python generate_fig01_workflow.py --dpi 600 --out <path>`
  (both arguments optional; default dpi is 600, default --out is
  figures/Figure_01_workflow.png).
- IMPORTANT FINDING: the --out argument only changes where the FIRST output
  file is written. The script unconditionally writes three more fixed paths
  on every single run, regardless of --out or --dpi:
  figures/Prompts_Images/Figure_01_workflow.png (lines 681-686),
  figures/Figure_01_workflow.pdf (lines 688-693), and
  figures/Figure_01_pipeline.png (lines 695-700, this is the exact line that
  produced the Part A overwrite). There is no flag to skip these three, and
  no dry-run mode. This means the script cannot safely be rerun at all,
  for any reason (including a resolution/preview check), without it
  overwriting Figure_01_pipeline.png again. Per the task's hard rule, this
  script was NOT rerun as part of this verification.

## Findings (numbered)

1. submission\figures\Figure_01_pipeline.png was silently overwritten by the
   new figure-generation run and is now byte-identical to
   Figure_01_workflow.png (same sha256, same size, one second apart in
   mtime). Confirmed with SHA-256 hashing in python, not by size/date alone.
2. The old image is not lost: an untouched, byte-exact backup survives at
   writing\figures\Figure_01_pipeline.png (June 2026, 1,871,483 bytes,
   different hash), together with its own caption/prompt file
   writing\figures\Figure_01_pipeline.md describing an axonometric pipeline
   diagram with per-stage result numbers overlaid - a different figure
   concept from the new one, not an earlier draft of it.
3. The overwrite was not an accident of matching filenames by chance: the
   generator script (generate_fig01_workflow.py, lines 695-700) hardcodes a
   write to Figure_01_pipeline.png on every invocation, with no flag to
   disable it. Any future rerun of this script, for any purpose, will
   overwrite that file again.
4. The overwritten filename (Figure_01_pipeline.png) is referenced only by
   OLD, already-rejected Building Simulation submission drafts under
   writing\submission\extra\ and writing\submission\archive\. Each of those
   files still carries the OLD caption text, which no longer matches the
   image now sitting at that path. The live, in-progress Applied Energy
   manuscript (writing\submission\rejection revision\manuscript\
   draft_S2_framework.md:3) has only a placeholder line and does not yet
   reference any figure filename, so nothing currently live was broken by
   the overwrite.
5. Content check: all 24 box labels, all 33 arrows (direction and the single
   dashed arrow with its exact label), the three band titles, and the print
   size/DPI target (190 mm at 600 dpi) all match the spec exactly, verified
   programmatically rather than by eye where the task required it (label
   diff, arrow-by-arrow script read, Pillow DPI/pixel read).
6. Minor layout note, not a spec failure: within Band 2, the physical left-
   to-right seating order is 7, 8, 9, 10, 12, 11, 13..., i.e. box 12
   ("Activity-driven end-use loads") sits to the left of box 11 ("Household
   aggregation to schedules"), whereas the spec's numbered list gives 10, 11,
   12 in that order. The spec's acceptance checklist does not require the
   listed numbering to equal physical seating order, and the direct arrow
   10 -> 11 (arrow 7) is drawn as an overhead orthogonal line that correctly
   skips over box 12, so the required topology (arrows 7, 8, 9) is intact.
   Flagged only for the record.
7. A thin dotted vertical line separates each band's title column from its
   diagram area (script lines 178-181). This is a layout divider, not an
   arrow and not text, so it does not violate the "only one dashed arrow"
   or "no other text" rules, but it is an element the prompt spec did not
   explicitly ask for. Cosmetic only.

## What I could not check and why

- Pixel-level legibility at literal 190 mm / 600 dpi print size: this tool
  renders the PNG for viewing at a downscaled 2000x1663 preview, not the
  true 4488x3732 pixel file, so a sub-pixel check for very slightly clipped
  serifs or exact optical kerning was not possible here. Nothing at the
  preview resolution suggested a problem; a final human check by opening
  the actual file at 100 percent zoom (or a proof print) is recommended
  before the figure is locked in.
- Arrow count and direction were not counted by eye (the task allows this
  for 30+ arrows); verification was instead done by reading the generator
  script's arrow-drawing calls line by line and matching each to its spec
  entry, as instructed.
- I did not open or evaluate writing\figures\Figure_01_pipeline.md as a spec
  for whether IT was correctly realized by the old (now-overwritten)
  Figure_01_pipeline.png at writing\figures\ - that image predates this task
  and was out of scope beyond confirming it still exists and differs from
  the new one.
- I did not attempt to determine who or what ran
  generate_fig01_workflow.py, when, or whether "Gemini Antigravity" in the
  task description refers to a tool that invoked this exact matplotlib
  script, versus a genuinely separate generative image process; the task
  only asked me to check the artifacts left behind, and this script and
  its fixed output paths are consistent with everything the task described
  finding on disk.
