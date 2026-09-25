# Figure 1 framework diagram, image generation prompt (simplified, 2026-09-25)

Paste ONLY the prompt block below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_01_pipeline_4split.png` (keep this exact name, the manuscript build reads it)
and tell the manager the folder. It replaces the report-style "Steps 1-9" diagram (plan item R1-M2a:
a simple 8-10 box, three-row diagram, as the 2J redraw). The v3 prompt
`Prompts_Images_v3/Figure_01_pipeline_4split.md` is superseded.

## Prompt to paste

```
Draw a simple, clean scientific workflow diagram for Figure 1 of a journal article in Building and Environment.
It must be readable at a glance: few boxes, short labels, straight arrows.

Style: white background, flat design, plain rounded rectangles, thin dark-grey outlines, one soft colour per row (colour-blind-safe, for example light blue, light green, light orange). Sans-serif text (Arial or Helvetica), one font size for all box labels. No icons, no clip art, no 3D, no shadows, no gradients, no logos, no title inside the image. Landscape, about 190 mm wide by 90 mm tall, high resolution (long edge at least 3500 pixels).

Layout: three horizontal rows, top to bottom. Each row has a short row label at its left edge.

Row 1, label "Data" (four boxes, left to right):
1. "Time-use diaries, 2005 to 2022"
2. "Census households and workers, 2021"
3. "Monthly hotel occupancy, Quebec and Alberta"
4. "Two mixed-use tower models and weather"

Row 2, label "Occupancy model" (three boxes, left to right):
5. "One generative model: residential, office, retail"
6. "Hotel time-series model"
7. "Four hourly occupancy schedules"

Row 3, label "Simulation and analysis" (three boxes, left to right):
8. "Building simulation: survey years and 2030 scenarios"
9. "Energy use and load timing by use"
10. "Comparison with building-code schedules"

Arrows (all solid, one arrowhead, no labels):
- Box 1 down to box 5.
- Box 2 down to box 5.
- Box 3 down to box 6.
- Box 5 right to box 7.
- Box 6 right to box 7 (route it cleanly so it does not pass through box 5 or touch it).
- Box 7 down to box 8.
- Box 4 down to box 8 (route the arrow cleanly around row 2, on the right side).
- Box 8 right to box 9, box 9 right to box 10.

Use these exact label texts, word for word. No other text anywhere in the image.

Must not:
- No numbers other than the years already in the labels. No percentages, no kWh, no counts.
- No abbreviations or codes (no GSS, NECB, SARIMA, EUI, ISQ, CBRE, Leg, 2J, 3J, gate).
- No word "forecast".
- No colour names written as text.
- No extra boxes, arrows or captions beyond those listed.
- The hotel path (box 3 to box 6 to box 7) must never pass through box 5.
```

## Acceptance checklist (author, after generating)

- Exactly 10 boxes in three labelled rows.
- Every label spelled exactly as listed; no extra text; no colour words drawn.
- The hotel arrow reaches box 7 without touching box 5.
- Long edge at least 3500 px (do not upscale afterwards; regenerate larger).
- Readable without zooming at 190 mm width.

## Matching caption (manager updates the manuscript when the image is installed)

Figure 1. Framework overview. Time-use diaries and census records feed one generative occupancy model
for the residential, office and retail uses; monthly hotel-occupancy statistics feed a separate hotel
model. The four hourly schedules drive simulations of two mixed-use tower models for four survey years
and three 2030 scenarios, and the results are compared with building-code schedules.
