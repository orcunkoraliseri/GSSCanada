# Figure 1 workflow diagram, image generation prompt

Paste the prompt below into an image generator. This file is a prompt only. No image is created here.

## Prompt to paste

Purpose: a methods workflow diagram for Figure 1 of a journal article submitted to Applied Energy. The
figure shows the full modelling chain, from raw datasets through the occupancy model to the building
simulation and analysis stage. Print target: double column width, 190 mm wide, at least 600 dpi. White
background. Colour-blind-safe palette (use a standard qualitative set such as Okabe-Ito or ColorBrewer
Set2; avoid red-green as the only contrast). Sans-serif labels (for example Arial or Helvetica), a single
consistent font size for all box text and a single consistent font size for arrow labels. Plain rectangle
boxes with rounded corners. No decorative icons, no clip art, no photographs, no 3D effects, no gradients,
no drop shadows, no logos.

Layout: three horizontal bands, stacked top to bottom, each band in its own light fill colour with a plain
text band title on the left margin: "Data" (top band), "Occupancy model" (middle band), "Building
simulation and analysis" (bottom band). Boxes flow left to right and top to bottom within each band.
Arrows may cross between bands. Keep the whole diagram legible when printed at 190 mm width.

### Boxes, grouped by band, in reading order

**Band 1: Data**
1. GSS time-use diaries, 2005 to 2022
2. Census microdata, 2021
3. NRCan end-use reference
4. Weather files
5. Building archetype models
6. IESO measured hourly data

**Band 2: Occupancy model**
7. Diary harmonisation to 30-minute slots
8. Generative day-type model
9. Census-to-diary matching
10. Marginal raking of at-home targets
11. Household aggregation to schedules
12. Activity-driven end-use loads
13. 2030 scenario construction
14. Persistence share 1
15. Persistence share 0.5
16. Persistence share 0

**Band 3: Building simulation and analysis**
17. Household sampling per cell
18. Building simulation
19. Load-shape metrics per cell
20. Stock aggregation to national figure
21. Fixed schedule arm
22. Average survey profile arm
23. Paired difference and confidence interval
24. Measured vs simulated comparison

Use these exact label texts, word for word, inside the boxes. Boxes 14, 15 and 16 are drawn smaller and
placed side by side directly below box 13, showing that box 13 branches into three parallel paths. Boxes
21 and 22 are drawn side by side, showing that they are two separate, parallel alternatives. Box 24 (in
Band 3) is where box 6 (IESO measured hourly data, in Band 1) connects, by a long dashed arrow crossing
both bands, labelled along its length "external check, not an input". Draw this as the only dashed arrow
in the whole diagram; every other arrow is a solid line.

### Arrows, numbered, exactly as listed (box name to box name; all solid unless marked dashed)

1. GSS time-use diaries, 2005 to 2022 -> Diary harmonisation to 30-minute slots
2. Diary harmonisation to 30-minute slots -> Generative day-type model
3. Diary harmonisation to 30-minute slots -> Marginal raking of at-home targets
4. Generative day-type model -> Census-to-diary matching
5. Census-to-diary matching -> Marginal raking of at-home targets
6. Census microdata, 2021 -> Census-to-diary matching
7. Marginal raking of at-home targets -> Household aggregation to schedules
8. Marginal raking of at-home targets -> Activity-driven end-use loads
9. Activity-driven end-use loads -> Household aggregation to schedules
10. NRCan end-use reference -> Activity-driven end-use loads
11. Diary harmonisation to 30-minute slots -> 2030 scenario construction
12. 2030 scenario construction -> Persistence share 1
13. 2030 scenario construction -> Persistence share 0.5
14. 2030 scenario construction -> Persistence share 0
15. Persistence share 1 -> Marginal raking of at-home targets
16. Persistence share 0.5 -> Marginal raking of at-home targets
17. Persistence share 0 -> Marginal raking of at-home targets
18. Household aggregation to schedules -> Household sampling per cell
19. Household sampling per cell -> Building simulation
20. Weather files -> Building simulation
21. Building archetype models -> Building simulation
22. Household sampling per cell -> Fixed schedule arm
23. Activity-driven end-use loads -> Fixed schedule arm
24. Household aggregation to schedules -> Average survey profile arm
25. Activity-driven end-use loads -> Average survey profile arm
26. Fixed schedule arm -> Building simulation
27. Average survey profile arm -> Building simulation
28. Building simulation -> Load-shape metrics per cell
29. Load-shape metrics per cell -> Stock aggregation to national figure
30. Load-shape metrics per cell -> Paired difference and confidence interval
31. Load-shape metrics per cell -> Measured vs simulated comparison
32. IESO measured hourly data -> Measured vs simulated comparison (dashed; label along the arrow:
    "external check, not an input")
33. Household sampling per cell -> Average survey profile arm

Arrows 15, 16 and 17 loop back from the three persistence-share boxes to the marginal raking box already
drawn earlier in the diagram (the 2030 stock is the same matched households, raked to each scenario's target); draw these as curved return arrows so they are visibly distinct from the
forward-flowing arrows, but keep the same solid line style and arrowhead as every other non-dashed arrow.

### Branch points (explicit)

- The three 2030 scenarios branch at box 13, "2030 scenario construction": one arrow out to each of
  "Persistence share 1", "Persistence share 0.5" and "Persistence share 0" (arrows 12, 13, 14). Each of the
  three then feeds back into "Marginal raking of at-home targets" (arrows 15, 16, 17).
- The two comparison arms branch after "Household sampling per cell" and "Activity-driven end-use loads":
  one path goes to "Fixed schedule arm" (arrows 22, 23), the other to "Average survey profile arm" (arrows
  24, 25, 33). Both arms then feed into the same "Building simulation" box (arrows 26, 27), alongside the main
  path from "Household sampling per cell" (arrow 19).

### Must not

- No result numbers anywhere in the figure: no percentages, no kWh values, no hours, no counts of any kind.
- No internal project labels of any kind. Do not write any of the following words or codes anywhere in the
  figure: J3, True-Future-Test, frozen frame, Tier, FailSafe, COLLECT_MODE, DDAY_STRATA, Step-8, Step-9,
  occACT, gate.
- Do not use the word "forecast" anywhere. Where a future-facing idea appears, the box text already says
  "scenario-based projection" or "scenario construction"; do not add "forecast" as a caption or subtitle.
- No logos, no journal name printed inside the figure, no author names, no watermarks.
- Do not invent extra boxes, extra datasets, or extra pipeline stages beyond the 24 boxes listed above.
- No text anywhere in the image other than the 24 box labels listed above, the three band titles ("Data",
  "Occupancy model", "Building simulation and analysis"), and the one arrow label "external check, not an
  input" on the dashed arrow. No other captions, subtitles, footnotes or legends.

### Acceptance checklist (for the author, after the image is generated)

- All 24 boxes listed above are present, each with its exact label text and no other text added to it.
- Every arrow listed above is present, points in the stated direction, and only arrow 32 (IESO to Measured
  vs simulated comparison) is dashed; every other arrow is solid.
- The three persistence-share boxes sit below and branch from "2030 scenario construction", and each loops
  back to "Marginal raking of at-home targets".
- The two comparison-arm boxes sit side by side as parallel alternatives feeding into "Building simulation".
- Every label is spelled exactly as listed, with no abbreviation, no added punctuation and no internal
  project code from the "must not" list.
- The figure stays legible (box text readable without zooming) when viewed at 190 mm width.
- The three bands are visually distinct and labelled "Data", "Occupancy model" and "Building simulation and
  analysis".

## Box to draft-section map

| # | Box label | Band | Section 2 draft source |
|---|---|---|---|
| 1 | GSS time-use diaries, 2005 to 2022 | Data | Table 1, row "GSS time-use diaries" |
| 2 | Census microdata, 2021 | Data | Table 1, row "Census public-use microdata" |
| 3 | NRCan end-use reference | Data | Table 1, row "NRCan SHEU end-use reference" |
| 4 | Weather files | Data | Table 1, row "Weather files" |
| 5 | Building archetype models | Data | Table 1, row "Building archetype models" |
| 6 | IESO measured hourly data | Data | Table 1, row "IESO measured hourly data" |
| 7 | Diary harmonisation to 30-minute slots | Occupancy model | Section 2.1 |
| 8 | Generative day-type model | Occupancy model | Section 2.2 |
| 9 | Census-to-diary matching | Occupancy model | Section 2.4 |
| 10 | Marginal raking of at-home targets | Occupancy model | Section 2.3 (applied after matching) |
| 11 | Household aggregation to schedules | Occupancy model | Section 2.5 |
| 12 | Activity-driven end-use loads | Occupancy model | Section 2.6 |
| 13 | 2030 scenario construction | Occupancy model | Section 2.7 |
| 14 | Persistence share 1 | Occupancy model | Section 2.7, lambda = 1 |
| 15 | Persistence share 0.5 | Occupancy model | Section 2.7, lambda = 0.5 |
| 16 | Persistence share 0 | Occupancy model | Section 2.7, lambda = 0 |
| 17 | Household sampling per cell | Building simulation and analysis | Section 2.8 |
| 18 | Building simulation | Building simulation and analysis | Table 1, dataset roles for weather files and building archetype models (Section 2.8, 2.9); no separate lettered subsection covers the simulation run itself |
| 19 | Load-shape metrics per cell | Building simulation and analysis | Section 2.10 |
| 20 | Stock aggregation to national figure | Building simulation and analysis | Section 2.9 |
| 21 | Fixed schedule arm | Building simulation and analysis | Section 2.12 |
| 22 | Average survey profile arm | Building simulation and analysis | Section 2.12 |
| 23 | Paired difference and confidence interval | Building simulation and analysis | Section 2.11 |
| 24 | Measured vs simulated comparison | Building simulation and analysis | Table 1, row "IESO measured hourly data" ("referenced in 2.10 to 2.12; no simulation input role") |

Every arrow above connects two boxes from this table; no arrow was added between boxes that the draft does
not link.
