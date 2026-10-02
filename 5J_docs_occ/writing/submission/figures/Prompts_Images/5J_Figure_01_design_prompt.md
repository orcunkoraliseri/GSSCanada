# Figure 1 prompt (5J paper: design of the study), 2026-10-01

The author makes this image. This file is the brief. Figure 1 is a drawing (no measured values), so an image generator may be
used for it; if one is used, it is named in the manuscript's generative AI declaration and nowhere else.

Manuscript place: Section 2, file `writing/figures/Figure_01_design.png` (the draft already points there).
Caption in the draft (do not change it; the image must match it):
> **Figure 1.** - Design of the study. One building and one weather year receive different households; the surrogate is scored
> on the hourly difference between two households in the same flat.

## 1. Size and format
- Double-column width: 190 mm wide, about 85 to 95 mm tall (landscape, about 2.1 : 1).
- Export at 600 dpi PNG (at least 4,500 px wide) plus a vector PDF with fonts embedded.
- All text at least 7 pt at 190 mm width (prefer 8 pt). A label that does not fit is shortened from the list in section 4,
  never shrunk below 7 pt.

## 2. What it must say
Only the household changes between the two runs of a pair, so the difference in load belongs to the household; the surrogate
and a household-blind control are both scored on that difference, on test sets sealed before training.

## 3. Layout: four zones, left to right, joined by thin arrows

**Zone 1, "Households" (about 20 % of width).** A short stack of three thin horizontal day strips (24 cells each, different
filled patterns = hours at home and activities). Left edge colour of each strip: rose #CC6677 (Spain) or teal #44AA99 (Italy).
Label above: **Time-use diaries, Spain and Italy**. Below the strips, two small household icons drawn as plain circles in a
row (no faces): one row of 2 circles tagged **Household A**, one row of 4 circles tagged **Household B**.

**Zone 2, "Paired EnergyPlus runs" (about 30 %).** One simple apartment building outline split into 4 floors with 3 flats per
floor (a grid of 12 rectangles). One flat is highlighted with a navy outline. Above the building, a small flat sun-and-cloud
mark with the tag **Same building, same weather**. Two arrows from Household A and Household B enter the highlighted flat.
Label on the building: **EnergyPlus**. Small footer tag: **every flat has its own household**.

**Zone 3, "The household effect" (about 25 %).** Two small stacked hourly load curves over one day (24 h), the upper one tagged
**Run with A**, the lower **Run with B**; then a third curve below them, drawn in navy, tagged **Difference B minus A**. A
small minus sign between the two upper curves and an equals sign before the third. Axis words only: **hour of day**.

**Zone 4, "Scoring" (about 25 %).** Two rounded boxes stacked:
- dark navy box, white text: **Surrogate** with a small input tag **household, building, weather**;
- mid-grey box: **Blind control** with a small crossed-out day strip as its input and the tag **household shuffled**.
From each box an arrow leads to a small navy difference curve (surrogate) and a flat grey line (control). A bracket joins each
to the EnergyPlus difference from Zone 3 with the word **compared**. Under Zone 4, one line: **Test sets sealed before
training: new households, new buildings, both new**.

## 4. Permitted text (complete list; nothing else appears)
Households · Time-use diaries, Spain and Italy · Household A · Household B · Paired EnergyPlus runs · Same building, same weather ·
EnergyPlus · every flat has its own household · The household effect · Run with A · Run with B · Difference B minus A ·
hour of day · Scoring · Surrogate · household, building, weather · Blind control · household shuffled · compared ·
Test sets sealed before training: new households, new buildings, both new

## 5. Palette and style
White background, one sans-serif font (Arial or Helvetica), all text horizontal, flat shapes, thin lines (0.5 to 1 pt).
Spain #CC6677, Italy #44AA99, surrogate dark navy #1E293B with white text, control and axes mid grey #64748B, text #111111.
No red-green pair as the only distinction.

## 6. Do not
- No numbers of any kind (no run counts, no scores, no speed-up, no R2), no axis values.
- No UK, no flag, no map, no logo, no institute name.
- No model or project names or codes: no "TCN", "temporal convolution", "5J", "G5J", "HETUS", "TABULA", "S3", "B4", "LOCO".
- No people, faces, robots, brains, glowing circuits, 3D, shadows or gradients.
- No meta notes ("illustrative", "schematic", "not to scale").

## 7. Image-generator prompt (copy as one block)

> Flat vector scientific diagram on a white background, landscape 2.1 : 1, four zones left to right joined by thin dark grey
> arrows, one sans-serif font, all text horizontal, thin lines, no shadows, no gradients, no 3D, no people. Zone 1 titled
> "Households": three thin horizontal 24-cell day strips with different filled patterns, left edges coloured rose #CC6677 and
> teal #44AA99, labelled "Time-use diaries, Spain and Italy"; below them a row of two plain circles tagged "Household A" and a
> row of four plain circles tagged "Household B". Zone 2 titled "Paired EnergyPlus runs": one simple apartment building outline
> divided into 4 floors of 3 flats, one flat outlined in dark navy #1E293B, a small flat sun-and-cloud mark above tagged "Same
> building, same weather", the label "EnergyPlus" on the building, two arrows from Household A and Household B into the
> outlined flat, small footer "every flat has its own household". Zone 3 titled "The household effect": two small stacked
> 24-hour load curves tagged "Run with A" and "Run with B", a minus sign between them, an equals sign, and a navy curve below
> tagged "Difference B minus A", axis word "hour of day". Zone 4 titled "Scoring": a dark navy rounded box with white text
> "Surrogate" and input tag "household, building, weather", and below it a mid-grey #64748B rounded box "Blind control" with a
> crossed-out day strip and tag "household shuffled"; each box points to a small curve, navy for the surrogate and a flat grey
> line for the control, each joined to the navy difference curve by a bracket labelled "compared"; one line under the zone
> "Test sets sealed before training: new households, new buildings, both new". Text colour #111111. Use no other words and no
> numbers.

## 8. After it is made (author, then manager)
- Check every string against section 4; remove any extra word or number (common with image generators) or redraw.
- View at 190 mm width on screen: every label reads without zoom.
- Save as `writing/figures/Figure_01_design.png` (+ `.pdf`); the manager checks it against the caption and records its md5 in
  `Step8_docs/impl/` and the Progress Log.

## 9. Fixes after the first version (2026-10-01 14:17, manager check of `Figure_01_design.png` md5 ee3a295c...)
Checked against sections 3 to 6 and the caption: every string is on the permitted list, no numbers, palette right, 4 floors of 3
flats, both household arrows enter the outlined flat. Two fixes (copy as one block into the tool that wrote `figures/scripts/fig01_design.py`):
> 1. The label "Same building, same weather" runs across the dotted line between zones 2 and 3 and almost touches "Run with A".
>    Move the sun mark and the label left inside zone 2, or set the label on two lines ("Same building," / "same weather").
> 2. The arrow from "Difference B minus A" ends in empty space. Route it to the tip of the "compared" bracket, so that both
>    model outputs are visibly compared with the EnergyPlus difference (section 3, zone 4).
> 3. Add the dotted zone dividers to the clash check (every drawn object type must be in it), re-run, and print the result.
Then save over the same files and print the new md5.
