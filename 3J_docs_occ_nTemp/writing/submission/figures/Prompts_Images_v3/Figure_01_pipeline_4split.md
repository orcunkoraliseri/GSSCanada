# Figure 1 -- End-to-End Four-Channel Pipeline (Steps 1-9)

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the nine-step occupancy-to-BEM pipeline in one image, with channel provenance (inherited from the two-channel construction stage vs added by this study) colour-coded, and the hotel side-track shown bypassing the Transformer.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (box diagram, STEP 1 through STEP 9)

---

## 🔴 Three rules that the 2026-08-11 regeneration broke. Read before generating.

**1. The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must not appear anywhere in the
image.** They are this project's internal names for its own construction stages. The manuscript was
rewritten on 2026-08-11 to remove them from every sentence, and a legend that still names the two
stages by those internal codes reintroduces, in print, the exact vocabulary the text no longer
defines. A reader has no way to resolve them.

**2. Colour names are styling instructions and must never be drawn as label text.** The 2026-08-11
image printed the literal word **"amber"** inside two boxes -- Step 3 read `amber (retail addition)`
and Step 5 read `amber (retail)` -- because the previous prompt wrote the fill colour and the label in
the same phrase. The generator could not tell which part was an instruction and which part was text.
This version separates them: everything under **LABEL TEXT** is drawn verbatim; everything under
**STYLING** is never drawn.

**3. Draw only the label text given, once.** The 2026-08-11 Step 4 box read
`two heads, two heads, third head` -- a description of the *colouring* repeated as if it were a label.

---

## 🔴🔴 Rules 4 to 6: what the *second* 2026-08-11 regeneration broke

The second attempt fixed rules 1 to 3 -- no stage codes, no colour words, no repeated colour
description -- and then broke the diagram's arithmetic instead. It drew **twelve boxes for nine
steps**, wrapped into three stacked rows:

| what was drawn | what is wrong |
|---|---|
| `STEP 6 Forecast 2030` **twice** | once on the top row, once on the middle row |
| `STEP 5` **twice** | one of the two carries a step number and a neural-network icon and **no title text at all** |
| `STEP 7` **twice** | once as `BEM/UBEM Integration` (correct), once as `End-Use Loads` (which is STEP 9) |
| `End-Use Loads` **twice** | as STEP 7 and again as STEP 9 |
| `STEP 4 3-Head Transformer` | placed *after* STEP 7 in the reading order |
| the `Hotel Side-Track` dashed lane | wrapped around STEP 7, STEP 4 and STEP 5 instead of running parallel below the chain |

**4. EXACTLY NINE BOXES. Count them before finishing.** Each of the numbers STEP 1 through STEP 9
appears **exactly once**. Each label string in the LABEL TEXT list appears **exactly once**. If a box
would be a duplicate of one already drawn, it is not a box -- delete it.

**5. ONE SINGLE HORIZONTAL ROW. Never wrap.** All nine boxes sit on one line, left to right, in
numeric order 1 to 9. This is the root cause of rule 4's failure: the diagram was wrapped to fit a
16:9 frame, and every wrap point duplicated the box it broke on. If nine boxes do not fit, **make the
canvas wider and the boxes narrower** -- a 3:1 or wider strip is correct and expected here. Do not
stack rows.

**6. Every box carries its title text.** A box showing only `STEP 5` and an icon, with no words in it,
is an error. Number, title and icon, in every one of the nine.

## 🔴 Framing

The 2026-08-11 image wasted **34% of its height on empty white above the diagram** (264 px of 768).
In the manuscript that white band separates the artwork from its caption and reads as a layout fault.
**Crop tight:** the artwork must fill the frame, with an even margin on all four sides of roughly 2%
of the image width. No large empty band on any side.

Render at **500 dpi or better for the printed width** (Elsevier's minimum for combination art). The
supplied images so far are about 184 dpi.

---

## 🔴 TERMINOLOGY LOCK (v2) -- applies to every string drawn in this image

The project's internal stage codes must **not** appear anywhere in the artwork, in any spelling or
punctuation: `Leg-1`, `Leg 1`, `Leg1`, `Leg-2`, `Leg-3`, `leg`, `2J`, `3J`, `1J`, `0J`.
They are internal build names, undefined for any reader, and the manuscript text was cleared of them
on 2026-08-11. If a stage must be named, use the descriptive form:

| do NOT draw | draw this instead |
|---|---|
| Leg-1 | `single-channel stage` (or `Residential only`) |
| Leg-2 | `two-channel stage` (or `Residential + Office`) |
| Leg-3 / 3J / this leg | `this study` (or `Residential + Office + Retail + Hotel`) |
| "three legs" / "the legs" | `three stages` |
| 2J / 1J / 0J | `the predecessor study` |

`**Source:**` lines elsewhere in this file cite real folder names on disk (`Leg3_4-split/...`).
Those are provenance for the authors and are **outside the fenced prompt** -- they are never drawn.

**Resolution.** Elsevier requires 500 dpi for combination art. Placed at 7 in wide that is
**3500 px minimum on the long edge**; generate as large as the tool allows and do not upscale
afterwards. The 2026-08-09/11 images came back at 1376 x 768 (~197 dpi), which fails.

---

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Very wide landscape strip, aspect ratio 3:1 or wider, white background, sans-serif labels.

COUNT AND LAYOUT, THE TWO HARDEST CONSTRAINTS IN THIS PROMPT:
- Draw EXACTLY NINE boxes. Not eight, not twelve. Count them before you finish.
- Put all nine on ONE SINGLE HORIZONTAL ROW, left to right, in numeric order STEP 1, STEP 2, STEP 3, STEP 4, STEP 5, STEP 6, STEP 7, STEP 8, STEP 9. Do NOT wrap onto a second or third row. If they do not fit, widen the canvas and narrow the boxes.
- Each STEP number appears exactly once in the whole image. Each label string appears exactly once in the whole image. No box is repeated.
- Every box contains all three of: its STEP number in small type at the top-left corner, its title text, and its icon. A box with a number and an icon but no title text is wrong.

Flat rounded-rectangle boxes connected by thin straight connector lines with small arrowheads. The artwork must fill the frame with only a small even margin on all four sides; do not leave a large empty band above or below the diagram.

DRAW ONLY THE TEXT LISTED UNDER "LABEL TEXT". Every colour word below is a styling instruction and must never be rendered as visible text in the image.

STYLING (never draw these words): restrained academic palette on white. Three fills only -- a desaturated slate-blue/teal for anything inherited from the earlier two-channel stage, a warm amber/gold for anything this study adds, and warm grey for shared or untouched elements. Boxes 3, 4, 5 and 7 are split between the slate-blue/teal fill and the amber fill, because those are the four boxes where the channels are actually processed. Boxes 1, 2, 8 and 9 are warm grey. Box 6 is slate-blue/teal.

LABEL TEXT (draw exactly these strings, once each, and no others):
  Box 1: "Data Collection"          + small database-cylinder icon
  Box 2: "Harmonization"
  Box 3: "Merge & Tiling"           + small link/chain icon
  Box 4: "3-Head Transformer"       + small neural-network node-cluster icon
  Box 5: "Archetype Linkage"        + no icon
  Box 6: "Forecast 2030"            + small calendar-grid icon
  Box 7: "BEM/UBEM Integration"     + small house-outline icon
  Box 8: "BEM Simulation"           + small iso-building icon
  Box 9: "End-Use Loads"            + small bar-chart icon
  Side-track lane label: "Hotel Side-Track"
  Bypass arrow label: "bypass"
  Legend swatch 1 (slate-blue/teal): "Inherited from the two-channel stage"
  Legend swatch 2 (amber/gold):      "Added by this study"

No box carries a parenthetical, a channel list or a colour name as text. The channel provenance is communicated by the split fills and by the two-swatch legend only.

SCENE: one single horizontal left-to-right chain of the nine boxes above, in numeric order, on one row. Below box 2 a separate amber-outlined dashed lane begins, labelled "Hotel Side-Track", runs parallel and below the main chain, passes under and visibly around box 4 with a small arrow labelled "bypass" curving around that box only, then rejoins the main chain at box 5. The dashed lane must NOT enclose any box of the main chain -- it runs underneath them, in its own horizontal band. A small two-swatch legend sits in the bottom-right corner. Flat, horizontal, no other colours.

FINAL CHECK before returning the image: nine boxes, numbered 1 to 9 once each, on one row, every one of them carrying title text.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- STEP 1: "Data Collection & Column Selection" -- GSS columns + hotel source (ISQ QC / CBRE AB monthly series)
- STEP 2: "Data Harmonization" -- crosswalk + OR-rule; AT_RETAIL derivation; hotel series harmonization
- STEP 3: "Merge & Tiling" -- one tiler list entry appends AT_RETAIL; retail kept in a separate CSV (byte-equality not verified, Table 6)

  🔴 CORRECTION 2026-08-06 night: this line originally ended "residential + office paths bit-identical". That is the pipeline overview's prose statement of design intent, and `Table_06_leg2_leg3_delta.md` grades the same claim `⚠ check source` because no file or column comparison of the tiler's output was ever run. Only Step 7 carries an affirmative evidence verdict in Table 6, and only for the base prototype geometry. Enforced by `f5_figure_check.py` arm C7.
- STEP 4: "Three-GSS-Head Transformer" -- heads = resid / AT_WORK / AT_RETAIL; hotel NOT in model
- STEP 5: "Archetype Linkage" -- residential Census linkage (single-channel stage); office NOCxNAICS (two-channel stage); retail population-level fraction; hotel province-level multiplier (this study)
- STEP 6: "Forecast 2030 + Hotel Side-Track" -- GSS channels via drift matrix; hotel SARIMA(1,1,1)(1,1,1,12) + COVID indicator, bypasses the Transformer entirely
- STEP 7: "BEM/UBEM Integration" -- Tag-2 dispatch: apartment REPLACE; office/retail/guest-room MODULATE; amenity + service/MEP untouched NECB
- STEP 8: "BEM Simulation" -- 56/56 cells; 2-city sweep CAN_MTL 6A + CAN_CLG 7A
- STEP 9: "Activity-Driven End-Use Loads" -- equipment + lighting; calibrated vs NRCan SCIEU
- Legend, long form if the caption needs it: slate-blue/teal = "inherited from the two-channel construction stage (Residential AT_HOME, Office AT_WORK)"; amber = "added by this study (Retail AT_RETAIL, Hotel non-GSS)"
- Bypass callout on the hotel lane: "Hotel side-track bypasses the Transformer entirely -- SARIMA, not the 3-head model"

## Layout notes
- Aspect ratio: wide landscape (16:9 or wider), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- Two-colour coding is the organizing device of this figure: slate-blue/teal for the two inherited channels, amber/gold for the two this study adds -- apply consistently to sub-elements inside boxes 3, 4, 5 and 7, since those are the boxes where the four channels are actually processed
- The hotel side-track lane must visibly route around box 4 only, not around any other box, and must rejoin the main chain at box 5
- Nine boxes evenly spaced; small STEP N numerals in the top-left corner of each box function as the section reference back to the pipeline overview document
