# Figure 1 workflow diagram, image generation prompt (simplified version, 2026-09-21)

Paste the prompt below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_01_workflow.png` in `submission/figures/` (it replaces the earlier, more detailed
diagram, which the author found too complicated). The earlier 24-box prompt is superseded.

## Prompt to paste

Draw a simple, clean scientific workflow diagram for Figure 1 of a journal article in Applied Energy.
It must be readable at a glance: few boxes, short labels, straight arrows.

Style: white background, flat design, plain rounded rectangles, thin dark-grey outlines, one soft
colour per row (colour-blind-safe, for example light blue, light green, light orange). Sans-serif text
(Arial or Helvetica), one font size for all box labels. No icons, no clip art, no 3D, no shadows, no
gradients, no logos, no title inside the image. Landscape, about 190 mm wide by 90 mm tall, high
resolution (at least 600 dpi).

Layout: three horizontal rows, top to bottom. Each row has a short row label at its left edge.

Row 1, label "Data" (four boxes, left to right):
1. "Time-use diaries, 2005 to 2022"
2. "Census households, 2021"
3. "National end-use energy survey"
4. "Building archetypes and weather"

Row 2, label "Occupancy model" (three boxes, left to right):
5. "Generative occupancy model"
6. "Match diaries to census households"
7. "Hourly schedules and activity loads"

Row 3, label "Simulation and analysis" (three boxes, left to right):
8. "Building simulation: 2022 and three 2030 scenarios"
9. "Load-shape metrics and paired comparison"
10. "Check against measured hourly load"

Arrows (all solid, one arrowhead, no labels):
- Box 1 down to box 5.
- Box 2 down to box 6.
- Box 5 right to box 6, box 6 right to box 7.
- Box 3 down to box 7.
- Box 7 down to box 8.
- Box 4 down to box 8 (route the arrow cleanly around row 2, or straight down on the right if box 4
  sits above box 8).
- Box 8 right to box 9, box 9 right to box 10.

One extra element: a small grey box outside the rows, at the far right of row 3 or just above box 10,
labelled "Measured hourly load (Ontario)", connected to box 10 by the only dashed arrow in the figure.

Use these exact label texts, word for word. No other text anywhere in the image.

Must not:
- No numbers other than the years already in the labels. No percentages, no kWh, no counts.
- No abbreviations or codes (no GSS, SHEU, IESO, WFH, C-VAE, J3, gate).
- No word "forecast".
- No extra boxes, arrows or captions beyond those listed.

## Acceptance checklist (author, after generating)

- Exactly 10 boxes in three labelled rows plus the one grey "Measured hourly load (Ontario)" box.
- Every label spelled exactly as listed; no extra text.
- Only one dashed arrow (grey box to box 10); all other arrows solid.
- Readable without zooming at 190 mm width.

## Matching caption (already in the manuscript)

Figure 1. Overview of the framework (Sections 2.1 to 2.12). Time-use diaries and census households feed
a generative occupancy model; the resulting household schedules and activity-driven loads drive building
simulations for 2022 and for three 2030 work-from-home scenarios. Measured hourly load is used only as an
external check, not as a model input.
