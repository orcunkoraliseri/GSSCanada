# Figure 3 (hotel channel), FINAL prompt v5, 2026-09-25

Replaces `Figure_03_hotel_channel.md` and its "Fix round 2". This file is complete on its own.
Paste ONLY the block under "Prompt to paste" into Gemini, in ONE message, nothing added.
Save the result as `Figure_05_hotel_sidetrack.png` in `writing/submission/figures/` (same name, the build picks it up).

## What went wrong last time, and how this prompt prevents it

- Last image: a dashed arrow ran OUT of the seasonal check box back into the Alberta card, and a solid line
  ran into the check box. Fix: the prompt lists every arrow by number, start and end, and says no other lines exist.
- The years were removed from the data cards on purpose: they sit in the caption and text, so the image
  does not need a redraw if the 2030 hotel level changes.

## Prompt to paste

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

## Check before saving (author, 1 minute)

1. Count the boxes: exactly 8 (2 grey cards, 1 white check box, 4 blue boxes counting s(t), 1 amber). If more or fewer, regenerate.
2. The white "Seasonal model check" box: exactly ONE dashed arrow comes IN (from Alberta). Nothing goes out. No solid line touches it.
3. Each grey card sends one arrow to "2022" and one to "2030". Nothing points INTO a grey card.
4. "Monthly rate r" and "Daily guest-room shape s(t)" both point into the amber box; the amber box points to "guest-room schedule".
5. The s(t) line is square steps: high, low, high. Not a wave.
6. Spelling: "occupancy", "guest-room", "recovery", "pandemic". No extra words anywhere.
If any check fails, regenerate with the same prompt; do not ask Gemini to "fix" an image (it adds new errors).
