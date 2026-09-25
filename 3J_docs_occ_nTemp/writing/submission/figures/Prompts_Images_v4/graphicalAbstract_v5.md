# Graphical abstract, FINAL prompt v5, 2026-09-25

Replaces `graphicalAbstract.md` and its "Fix round 2". This file is complete on its own.
Paste ONLY the block under "Prompt to paste" into Gemini, in ONE message, nothing added.
Save the result as `graphicalAbstract.png` in `writing/submission/figures/` (same name, the build picks it up).

## What went wrong last time, and how this prompt prevents it

- "survey schedule" was written twice in the top chart. Fix: every label is listed once with its exact position.
- The hotel had two colours (mauve bed icon, pale-teal tower band) and looked like the residents and the office.
  Fix: each channel gets one hex colour, and the prompt lists every element that uses it.
- The two charts now say "office" in their titles, because both curves are the office channel. Shapes follow the
  paper's numbers: office presence peaks at hour 9 (code) and hour 12 (survey); office energy peaks at about
  hour 12 under both (Results table, `03_Results.md:29-30`). No numbers are drawn except the hour ticks.

## Prompt to paste

```
Draw a clean, flat, 2D graphical abstract for a scientific journal (Building and Environment). White background. No 3D, no perspective, no shadows, no gradients, no photorealism, no clip art. Sans-serif font (Arial or Helvetica), dark grey text (#333333), all text horizontal. Landscape, at least 3600 x 1800 pixels (2:1).

CHANNEL COLOURS (each colour belongs to ONE channel only and is used for nothing else):
- Residents: mauve #9B6B8E
- Office workers: teal #2A9D8F
- Shoppers: coral #E07A5F
- Hotel guests: amber #E8B04B
- Structure (brackets, arrows, axes, the code-schedule lines, the plant box): neutral grey #8A8A8A

THREE PANELS side by side, equal width, separated by white space only (no boxes around panels). Each panel has one heading at its top, centred, in bold.

LEFT PANEL. Heading: "Four occupancy schedules".
Four rows, top to bottom, each row = one small flat solid icon in its channel colour + a label to its right in dark grey text:
  row 1: house icon, mauve #9B6B8E, label "Residents"
  row 2: briefcase icon, teal #2A9D8F, label "Office workers"
  row 3: shopping-bag icon, coral #E07A5F, label "Shoppers"
  row 4: bed icon, amber #E8B04B, label "Hotel guests"
On the far left of the panel, a thin grey vertical bracket spans rows 1 to 3, with the rotated label "time-use diaries". A second, separate thin grey bracket spans row 4 only, with the rotated label "hotel statistics".
One grey arrow leaves the right side of the panel toward the centre panel.

CENTRE PANEL. Heading: "One mixed-use tower".
One single tall narrow tower drawn as a rectangle, divided into stacked horizontal floor bands separated by thin white lines. From top to bottom:
  top 2 bands: amber #E8B04B, with the label "hotel" to the right of the tower
  next 4 bands: mauve #9B6B8E, label "residential" to the right
  next 4 bands: teal #2A9D8F, label "office" to the right
  bottom 1 band (street level): coral #E07A5F, label "shop" to the right
Below the tower, a ground line, and under it one small light-grey box with dark text "shared plant".
Only one building. No other buildings, no trees, no people.

RIGHT PANEL. No panel heading; instead two small line charts stacked vertically, same size, each with a thin grey horizontal axis and hour ticks labelled "0", "6", "12", "18", "24" (these five numbers are the only numbers in the whole image). No vertical axis, no gridlines.
  TOP CHART. Title above it: "When office workers are present".
    Line A: dashed grey #8A8A8A. Near zero from hour 0 to 6, rises steeply to its maximum by hour 8, stays high and flat until hour 17, falls back near zero by hour 20.
    Line B: solid teal #2A9D8F, thicker. Near zero until hour 7, rises gently to a rounded peak at hour 12 that is only about HALF the height of line A, falls back near zero by hour 19.
    Label "code schedule" (grey text) placed ONCE, just above the flat top of line A, at about hour 18.
    Label "survey schedule" (teal text) placed ONCE, just above the peak of line B, at hour 12, inside the gap between the two lines.
  BOTTOM CHART. Title above it: "When office energy is used".
    Line A: dashed grey #8A8A8A, and Line B: solid teal #2A9D8F, almost on top of each other: both low at night, both rise from hour 6, both peak at hour 12, both fall by hour 20. Same height.
    Label "code schedule" (grey text) placed ONCE, at the left of the curves near hour 4, with a thin grey leader line to the dashed line.
    Label "survey schedule" (teal text) placed ONCE, at the right of the curves near hour 21, with a thin teal leader line to the solid line.
  To the right of the bottom chart, one small white rounded card with a thin grey outline and the text on three lines: "presence shifts," / "energy timing" / "holds".

TEXT: the only words and numbers in the image are the ones in quotation marks above; each appears exactly once, except "code schedule" and "survey schedule", which appear exactly once per chart (twice each in total). No title banner, no caption, no legend box, no footnote, no logos, no colour names, no abbreviations (no GSS, NECB, EUI, HVAC).
```

## Check before saving (author, 1 minute)

1. Colours: the bed icon AND the top tower bands are the same amber; nothing else is amber. House icon and residential bands are the same mauve. Briefcase, office bands and both solid chart lines are the same teal.
2. Top chart: "code schedule" once, "survey schedule" once. The teal curve peaks lower (about half) and later (hour 12) than the grey one.
3. Bottom chart: "code schedule" once, "survey schedule" once. The two curves nearly overlap and peak together at hour 12.
4. One building only. Only numbers: 0, 6, 12, 18, 24 on each chart.
5. Spelling: "occupancy", "mixed-use", "statistics", "diaries".
If any check fails, regenerate with the same prompt.
