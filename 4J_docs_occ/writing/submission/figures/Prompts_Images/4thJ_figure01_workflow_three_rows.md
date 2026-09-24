# Image prompt — new Figure 1: workflow, three rows

## 1. Header

**Purpose.** Replace the old "Pipeline, Steps 0 to 11" project-report figure with a simple
three-row workflow diagram, as agreed in the improvement plan (`IMP/4J_improvement_plan_from_2J_lessons_2026-09-22.md`,
row M2a). Figure 1 shows the **method** (how the study was done), not results. It must not
duplicate the graphical abstract (`IMP/prep/graphical_abstract_prompt.md`), which shows findings
and numbers. No result numbers appear anywhere in Figure 1.

**Output file name:** `HETUS_LLM_Workflow_Figure1.png` (plus `HETUS_LLM_Workflow_Figure1.pdf` if
the generating tool can also export a vector or PDF version).

**Install path:** `writing/submission/figures/`

**Note:** this new figure replaces `HETUS_LLM_Pipeline_Steps.png` in the manuscript body only
after the author has reviewed and approved the generated image. Do not delete the old file before
that approval.

## 2. Journal rules (Energy and Buildings)

- Target width: full page, about 19 cm, or 1.5-column, about 14 cm. Design the layout so it stays
  legible at either width.
- Resolution: the Elsevier/E&B guide for authors treats a diagram of this kind as a chart or
  bitmapped line drawing, which needs a minimum resolution of 1000 dpi at the stated widths
  (`writing/resources/E_and_B_guide_for_authors_2026-09-23.txt`, line 881; photographs alone need
  only 300 dpi, line 874). Generate at the highest resolution the tool offers, and if that falls
  short of 1000 dpi at 19 cm width, the author should re-export or redraw the boxes and text as
  vector shapes in PowerPoint before submission rather than upscale the raster.
- Sans-serif font throughout (Arial, Helvetica or similar).
- All text must stay readable at print size, at least 7 pt, when the figure is shown at 14 cm
  width.
- White background, no title printed inside the image (the caption carries the title).
- No logos, no watermarks.
- No project step numbers, no internal codes: do not write "Step 0" through "Step 11", no gate
  IDs, no file names, no variable names, no fold names beyond the plain country names that the
  Methods text itself uses.

## 3. Exact content: three horizontal rows

Everything below is taken only from Sections 2.1 to 2.6 of `4J_manuscript_submission.md`. Nothing
else may be added. Boxes are joined left to right by arrows within a row.

### Row 1 — Data and harmonisation (Section 2.1, 2.2)

Five boxes, left to right:

1. `Spain survey: 19,295 diaries`
2. `Italy survey: 41,229 diaries`
3. `United Kingdom survey: 16,533 diaries`
4. `Harmonise to shared activity codes`
5. `Convert diaries to text records`

Boxes 1, 2 and 3 sit side by side and each feed one arrow into box 4; box 4 feeds one arrow into
box 5.

### Row 2 — Diary generation and comparison (Section 2.3, 2.4, 2.6)

Five boxes. This row forks and then joins:

1. `Train on two countries`
2. `Fine-tuned model generates held-out diaries`
3. `Reweight real diaries by IPF`
4. `Compare to published time budgets`
5. `Pre-registered pass or fail rule`

Box 1 feeds two arrows: one to box 2, one to box 3. Boxes 2 and 3 each feed an arrow into box 4.
Box 4 feeds one arrow into box 5.

### Row 3 — Building loads (Section 2.5)

Six boxes, left to right:

1. `Diaries drive building simulation`
2. `Occupancy-based internal gains`
3. `Activity-triggered appliance loads`
4. `Domestic hot water draws`
5. `Heating demand: Spain, Italy, UK archetypes`
6. `Stock-scale loads: London and Bologna`

Box 1 feeds arrows into boxes 2, 3 and 4 (three parallel branches). Box 2 feeds one arrow into
box 5. Boxes 3 and 4 each feed one arrow into box 6. Boxes 5 and 6 are both end points; there is
no arrow between them. (Manager fix 2026-09-23: the manuscript's data table, line 65-67, has heating
from the 88 TABULA archetypes and the London/Bologna stock runs covering appliance and hot-water
loads only; the first draft wrongly routed everything through heating into the stock box.)

No other labels, subtitles or captions appear inside the image.

## 4. Colour scheme (colour-blind safe, hex codes)

Reuse the palette already used elsewhere in the paper's figures, for consistency:

| Element | Colour |
|---|---|
| Spain boxes | `#CC6677` (rose) |
| Italy boxes | `#44AA99` (teal) |
| United Kingdom boxes | `#332288` (indigo) |
| Fine-tuned model box | `#1B2A4A` (dark navy fill, white text) |
| Reweighting (IPF) box | `#888888` (mid grey fill, white text) |
| All other process boxes (harmonisation, comparison, building-load boxes) | `#E0E0E0` fill, `#111111` text |
| Arrows | `#444444` |
| Row labels (if used as a light background band per row, optional) | `#F5F5F5` |

Countries keep their own colour only where a box names a single country (Row 1 survey boxes; the
Spain/Italy/UK archetype box in Row 3 may show the three colours as a small side-by-side swatch or
just use the neutral grey if a single box cannot cleanly split three colours). All shared or
process boxes stay neutral grey. Do not use a red/green pair as the only distinction between any
two elements.

## 5. PROMPT FOR GEMINI

Copy everything between the lines into Gemini as one prompt.

---

Create a clean, flat, vector-style diagram for a scientific journal figure. White background, no
3D effects, no clip art, no photographs, no people, no icons of people, no logos, no watermarks,
no title text inside the image, and no extra text beyond what is listed below. Use a plain
sans-serif font for all labels, large enough to be readable when the image is shrunk to 14
centimeters wide. Spell every label exactly as given below, with no typos, no added words, and no
removed words. Do not invent any numbers; use only the numbers given below.

The diagram has three horizontal rows, stacked top to bottom, each row flowing left to right with
arrows connecting its boxes. Use rounded rectangles for all boxes.

Row 1, top, titled by its position only (do not print a row title): five boxes in a line. Three
boxes side by side on the left, colored rose for the box labeled "Spain survey: 19,295 diaries",
teal for the box labeled "Italy survey: 41,229 diaries", and indigo for the box labeled "United
Kingdom survey: 16,533 diaries". Arrows from all three of these boxes point to a fourth, light grey
box labeled "Harmonise to shared activity codes". An arrow from that box points to a fifth, light
grey box labeled "Convert diaries to text records".

Row 2, middle: five boxes. On the left, a light grey box labeled "Train on two countries". Two
arrows leave this box: one going up-right to a dark navy box labeled "Fine-tuned model generates
held-out diaries", and one going down-right to a medium grey box labeled "Reweight real diaries by
IPF". Arrows from both of these boxes converge into one light grey box labeled "Compare to
published time budgets". An arrow from that box points to a final light grey box labeled
"Pre-registered pass or fail rule".

Row 3, bottom: six boxes. On the left, a light grey box labeled "Diaries drive building
simulation". Three arrows leave this box, branching to three light grey boxes labeled "Occupancy-
based internal gains", "Activity-triggered appliance loads", and "Domestic hot water draws". On the right,
two final light grey boxes, one above the other. An arrow from "Occupancy-based internal gains"
points to the upper final box, labeled "Heating demand: Spain, Italy, UK archetypes". Arrows from
"Activity-triggered appliance loads" and from "Domestic hot water draws" both point to the lower
final box, labeled "Stock-scale loads: London and Bologna". There is no arrow between the two final
boxes.

Use exactly these hex colors: rose #CC6677, teal #44AA99, indigo #332288, dark navy #1B2A4A (white
text on this box), medium grey #888888 (white text on this box), light grey #E0E0E0 (dark text on
these boxes), and dark grey #444444 for all arrows. Keep consistent box sizes within each row,
consistent arrow style throughout, and generous white space between the three rows so the image
reads clearly as three separate stages from top to bottom.

---

## 6. Check after generation

- Every label matches Section 3 above character for character: no missing words, no added words,
  no misspelled country names, no changed numbers (19,295; 41,229; 16,533).
- No box contains any text beyond its one listed label.
- Arrows point in the directions given: left to right within each row, the Row 2 fork converging
  correctly, Row 3 splitting into two separate end boxes (gains to heating; appliances and hot water
  to stock loads) with no arrow between them, and no arrow pointing backward.
- No step numbers, gate IDs, file names, or internal project codes appear anywhere in the image.
- The image is readable (every label legible without zooming) when viewed at 14 cm width.
- Gemini and similar image generators frequently misspell or garble text baked into an image. If
  any label is misspelled, garbled, duplicated, or missing, regenerate the image, or export it and
  fix the text boxes directly in PowerPoint rather than accepting a wrong label.

## 7. Generative-AI disclosure (Elsevier policy)

Per Elsevier's GenAI policy for figures (cited in `writing/resources/E_and_B_guide_for_authors_2026-09-23.txt`,
section "Generative AI and figures, images and other artwork"), AI tools may be used for
explanatory diagrams such as this workflow figure, but the use must be disclosed in the figure
caption and in the manuscript's general Generative AI disclosure statement.

Draft caption sentence (add to the Figure 1 caption if the generated image is used as submitted):

> This figure was created with the assistance of a generative AI image tool (Gemini) and reviewed
> and edited by the author for accuracy.

If the image is used, the manager also adds the figure to the manuscript's AI declaration (sole
author: "the author", never "the authors").
