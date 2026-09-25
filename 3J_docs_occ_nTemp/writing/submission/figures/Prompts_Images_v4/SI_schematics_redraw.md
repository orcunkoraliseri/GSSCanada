# Supplementary schematics S2 to S5, image generation prompts (v4, 2026-09-25)

> 2026-09-25: S2, S3, S4 from this file are DONE and accepted. For S5 use `SI_S5_exclusivity_v5.md` (complete, standalone).

Paste ONLY one prompt block at a time into Gemini. This file holds prompts only; no image is created here.
Save each result under the file name given, so the SI build picks it up. Long edge at least 3500 px.

Why: the installed S2 to S5 are old v3 drawings with internal notes ("the reviewer-defusing pattern",
"wiring-bug lesson learned here", "md5-verified byte-identical", "(dr_L3-12)", "Step 7", code names such as
AT_WORK and REPLACE), "--" used as a dash, title banners, and in S3 two labels printed on top of each
other. A journal figure carries none of these; the caption does the explaining.

Common style for all four (repeat inside each prompt, already included below): flat 2D, white
background, sans-serif, muted colours (warm grey residential, slate blue office, teal retail, amber
hotel), no 3D, no shadows, no gradients, no title banner, no notes, no footnote, no logos, no colour
names written as text, no codes or abbreviations.

## S2, one scenario lever per channel -> `SI/Figure_S02_scenario_levers.png`

```
Clean flat 2D diagram for an academic paper. White background, sans-serif labels, generous white space, no 3D, no shadows, no gradients, no clip art. Wide landscape, long edge at least 3500 pixels.
Four columns, each with a small coloured header box: "Residential" (warm grey), "Office" (slate blue), "Retail" (teal), "Hotel" (amber).
Under Office, Retail and Hotel: one horizontal slider line with a tick at each end and one filled circle in the middle. Tick labels under each slider:
  Office: "conservative", "hybrid", "fully hybrid" (the circle sits on "hybrid").
  Retail: "0.90", "0.97", "1.05" (the circle sits on "0.97").
  Hotel: "0.92", "1.00", "1.05" (the circle sits on "1.00").
Under Residential: a plain grey line with no ticks and the short text "follows the office setting".
No other text. No title, no notes, no footnote.
```

## S3, two-channel version of the framework -> `SI/Figure_S03_leg2_pipeline.png`

```
Clean flat 2D flowchart for an academic paper. White background, sans-serif labels, generous white space, no 3D, no shadows, no gradients, no clip art. Wide landscape, long edge at least 3500 pixels. Reading order left to right.
Six rounded boxes in one row joined by arrows, labelled in order: "Survey diaries and census", "Harmonised records", "Two-head occupancy model", "2030 scenarios", "Building model", "Energy by end use".
Inside boxes 3 to 6, two small stacked bars: a slate-blue one labelled "residential" and a teal one labelled "office". Every label sits alone; no two labels overlap.
A small legend at bottom right: slate-blue square "residential", teal square "office".
No other text. No step numbers, no title, no notes, no footnote.
```

## S4, three-stage development of the model -> `Figure_02_three_leg_roadmap.png`

```
Clean flat 2D diagram for an academic paper. White background, sans-serif labels, generous white space, no 3D, no shadows, no gradients, no clip art. Wide landscape, long edge at least 3500 pixels. Reading order left to right.
Three rounded boxes joined by two thick arrows, each box larger than the one before:
  box 1, warm grey, a simple person icon, labelled "Residential".
  box 2, slate blue, a person icon and a briefcase icon, labelled "Residential and office".
  box 3, white with an amber outline, containing a small slate-blue inset (person and briefcase icons) plus a shopping-bag icon and a bed icon, labelled "Residential, office, retail and hotel".
Under box 1 the short caption "earlier studies"; under box 2 "two-channel stage"; under box 3 "this study".
No other text. No dates, no notes, no footnote, no title.
```

## S5, exclusivity step across the three decoder heads -> `Figure_04_exclusivity_projection.png`

```
Clean flat 2D diagram for an academic paper. White background, sans-serif labels, generous white space, no 3D, no shadows, no gradients, no clip art. Wide landscape, long edge at least 3500 pixels. Reading order left to right.
LEFT: three vertical bars of different heights (slate blue, teal, warm grey) with a short dashed horizontal threshold mark across each bar at its own height; above them the label "Three head probabilities, one time slot".
CENTRE: one amber box labelled "Compare each head with its own threshold", with an arrow in from the left and an arrow out to the right.
RIGHT: the same three bar positions, where only the teal bar remains full height and the other two are flat lines at zero; above them the label "At most one channel per slot".
No other text. No numbers, no percentages, no notes, no footnote, no title.
```

## S1 (occupiable-area shares) is a data plot, not a schematic

It is redrawn from data by the manager's figure script (title and the dated footnote removed); no prompt.

## S5 fix round 2 (2026-09-25, after checking the first Gemini image)

Problem in the first image: all three bars reach above their thresholds, yet only teal is kept. Under the paper's
rule (Appendix B, Eq. B.4) the winner is the candidate furthest above its own threshold, and in that drawing that
would be the grey bar, so the figure contradicts the text. Paste the S5 prompt above again, then add:

"LEFT panel, strict: the teal bar is well above its dashed threshold mark; the slate-blue bar and the warm-grey bar
both end clearly BELOW their own dashed threshold marks. Every dashed mark spans only the width of its own bar."
