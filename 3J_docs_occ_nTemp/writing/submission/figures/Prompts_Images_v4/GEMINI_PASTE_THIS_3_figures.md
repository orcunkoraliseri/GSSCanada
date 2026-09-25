# Instructions for Gemini: draw 3 figures (2026-09-25)

Draw the three images below, one at a time. For each one: generate it from its prompt exactly as written, then check it against its list. If any check fails, generate it again from the same prompt (do not edit the image). When it passes, first copy the old file into `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures\_archive_v4_before_v5_redraw_2026-09-25\`, then save the new image as a PNG, at least 3600 pixels on the long edge, to the exact path given (overwrite).

## Image 1 of 3: hotel figure

Save to: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures\Figure_05_hotel_sidetrack.png`

Prompt:

```
Draw a clean, flat, 2D flowchart for a scientific journal. White background. No 3D, no perspective, no shadows, no gradients, no clip art, no decorative icons except the two named below. Sans-serif font (Arial or Helvetica), dark grey text (#333333), all text horizontal. Landscape, 16:9, at least 3600 x 2025 pixels. All boxes are plain rectangles with square corners and no outline unless stated.

COLOURS (use only these):
- Data cards: warm grey fill #CFC8BD, dark text.
- Processing boxes: slate blue fill #4F6D8F, white text.
- Final box: amber fill #E8B04B, dark text.
- Check box: white fill with a thin grey outline #8A8A8A, dark text.
- Arrows: solid dark grey #555555, 3 px, filled triangular arrowheads. The one dashed arrow is #8A8A8A, dashed.

LAYOUT GRID: imagine the canvas split into 4 equal columns (C1 to C4, left to right) and 3 equal rows (R1 top, R2 middle, R3 bottom). Place each element in its cell, centred in that cell.

ELEMENTS (exactly these eight boxes, nothing else):
1. C1-R1: data card "Quebec monthly hotel occupancy", with a tiny table icon above the text.
2. C1-R2: data card "Alberta monthly hotel occupancy", with a tiny table icon above the text.
3. C1-R3: check box "Seasonal model check". Under the title, two smaller lines of text: "pattern and pandemic dip" and "not used for the simulated rate". A tiny single wave icon at the right end of the title.
4. C2-R1: processing box "2022: observed monthly rate".
5. C2-R2: processing box "2030: 2019 monthly pattern scaled to recovery level". Directly under this box, outside it, small dark text: "three bands: 0.92, 1.00, 1.05".
6. C3-R1.5 (in column 3, vertically halfway between row 1 and row 2): processing box "Monthly rate r".
7. C3-R3: processing box "Daily guest-room shape s(t)". Inside it, under the title, a white step line over a thin horizontal axis: the line is HIGH on the left third, drops to a LOW flat level in the middle third, and returns HIGH on the right third. Three small white labels under the axis: "night" at the left, "day" in the middle, "night" at the right. Square steps only, no curves.
8. C4-R2: amber box "Hotel multiplier = s(t) x r". To its right, outside the box, the words "guest-room schedule" after an arrow.

ARROWS (exactly these eight, no other lines anywhere in the image):
A1. From the right edge of box 1 to the left edge of box 4 (straight, horizontal).
A2. From the right edge of box 2 to the left edge of box 5 (straight, horizontal).
A3. From the right edge of box 1 to the left edge of box 5 (one diagonal line, going down-right).
A4. From the right edge of box 2 to the left edge of box 4 (one diagonal line, going up-right). A3 and A4 cross once in the gap between column 1 and column 2; that single crossing is allowed.
A5. From the right edge of box 4 to the left edge of box 6.
A6. From the right edge of box 5 to the left edge of box 6.
A7. From the right edge of box 6 to the left edge of box 8.
A8. From the top edge of box 7 up to the bottom edge of box 8.
Plus ONE dashed arrow D1: from the bottom edge of box 2 straight down to the top edge of box 3, arrowhead touching box 3.
Box 3 has NO arrow leaving it. No arrow goes into box 6 except A5 and A6. Nothing touches box 1 or box 2 on their left, top or bottom, except D1 leaving the bottom of box 2.
Finally, one short arrow leaves the right edge of box 8 and ends at the words "guest-room schedule".

TEXT: the only words and numbers in the image are the ones in quotation marks above. No title, no caption, no legend, no footnote, no notes, no step numbers, no letters A1 to A8, no box numbers, no abbreviations (no SARIMA, ISQ, CBRE, COVID, STR), no colour names, no dashes used as punctuation, no years other than 2019, 2022 and 2030.
```

Checks:

1. Count the boxes: exactly 8 (2 grey cards, 1 white check box, 4 blue boxes counting s(t), 1 amber). If more or fewer, regenerate.
2. The white "Seasonal model check" box: exactly ONE dashed arrow comes IN (from Alberta). Nothing goes out. No solid line touches it.
3. Each grey card sends one arrow to "2022" and one to "2030". Nothing points INTO a grey card.
4. "Monthly rate r" and "Daily guest-room shape s(t)" both point into the amber box; the amber box points to "guest-room schedule".
5. The s(t) line is square steps: high, low, high. Not a wave.
6. Spelling: "occupancy", "guest-room", "recovery", "pandemic". No extra words anywhere.

## Image 2 of 3: one channel per time slot

Save to: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures\Figure_04_exclusivity_projection.png`

Prompt:

```
Draw a clean, flat, 2D explanatory diagram for a scientific journal. White background. No 3D, no perspective, no shadows, no gradients, no clip art, no axes, no gridlines. Sans-serif font (Arial or Helvetica), dark grey text (#333333), all text horizontal. Landscape, 16:9, at least 3600 x 2025 pixels.

COLOURS (use only these): bar 1 slate blue #4F6D8F, bar 2 teal #2A9D8F, bar 3 warm grey #A39A8E, centre box amber #E8B04B with dark text, arrows and dashed marks dark grey #444444.

THREE ZONES, left to right, each about one third of the width:

LEFT ZONE. Heading at the top, two lines, centred: "Three head probabilities," / "one time slot".
Below it, three wide vertical bars standing on one common invisible baseline, evenly spaced, same width, in this order left to right: slate blue, teal, warm grey.
Heights on a scale where 10 is the tallest possible bar:
- slate-blue bar: height 5. Its dashed threshold mark is at height 7, so the bar top is clearly BELOW its mark, with a visible white gap between the bar top and the dashed mark.
- teal bar: height 9. Its dashed threshold mark is at height 4, so the bar clearly passes its mark.
- warm-grey bar: height 3. Its dashed threshold mark is at height 6, so the bar top is clearly BELOW its mark, with a visible white gap.
Each dashed threshold mark is a short horizontal dashed line exactly as wide as its own bar, centred on its own bar, never reaching a neighbouring bar.

CENTRE ZONE. One amber rectangle with the text on three lines: "Compare each head" / "with its own" / "threshold". One arrow comes into its left edge from the left zone; one arrow leaves its right edge toward the right zone.

RIGHT ZONE. Heading at the top, two lines, centred: "At most one channel" / "per slot".
Below it, the same three bar positions and colours as the left zone, on the same baseline height:
- slate blue: a thin flat line at height 0 (just a short thick line on the baseline).
- teal: a full bar at height 9, same as on the left.
- warm grey: a thin flat line at height 0.
No dashed marks in the right zone.

TEXT: the only words in the image are the ones in quotation marks above. No numbers, no percentages, no axis labels, no legend, no title, no footnote, no notes, no colour names, no abbreviations.
```

Checks:

1. Left zone: ONLY the teal bar goes past its dashed mark. The blue and grey bar tops sit visibly BELOW their own dashed marks.
2. Each dashed mark covers only its own bar.
3. Right zone: teal full height, blue and grey flat on the baseline, no dashed marks.
4. No numbers anywhere; only the three text items.

## Image 3 of 3: graphical abstract

Save to: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures\graphicalAbstract.png`

Prompt:

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

Checks:

1. Colours: the bed icon AND the top tower bands are the same amber; nothing else is amber. House icon and residential bands are the same mauve. Briefcase, office bands and both solid chart lines are the same teal.
2. Top chart: "code schedule" once, "survey schedule" once. The teal curve peaks lower (about half) and later (hour 12) than the grey one.
3. Bottom chart: "code schedule" once, "survey schedule" once. The two curves nearly overlap and peak together at hour 12.
4. One building only. Only numbers: 0, 6, 12, 18, 24 on each chart.
5. Spelling: "occupancy", "mixed-use", "statistics", "diaries".

## When all three are saved

Reply with the three saved paths and their pixel sizes. Do not change any other file.
