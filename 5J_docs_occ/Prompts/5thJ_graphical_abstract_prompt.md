# Graphical abstract prompt (5J, occupancy-aware EnergyPlus surrogate), 2026-09-28

The author makes this image. This file is the text brief. It is written at the design stage: **no
result exists yet.** Panels A and B show the method and can be made now. Panel C shows results and
stays a grey placeholder until the one scoring of the sealed tests (Step 6) is done; its numbers are
then copied from the Step 6 result file, and no value may be altered, rounded differently or added.

Panel C carries measured values, so it is drawn in plotting software (matplotlib, PowerPoint,
Illustrator) from the frozen results, never by an image generator. Panels A and B are drawings and
may be made with an image generator from the prompt in section 7. If any AI tool is used for any part,
it must follow the journal's GenAI policy and be named in the manuscript's generative AI declaration,
and nowhere else in the manuscript.

## 1. Journal rules (venue still open; these are the Elsevier rules used for 4J, re-check when the venue is chosen)

- Uploaded as a SEPARATE file, not inside the manuscript.
- At least 531 x 1328 pixels (height x width). Aim for 1062 x 2656 or larger, landscape, about 1 : 2.5.
- Readable at 5 x 13 cm: no text smaller than about 7 pt, prefer 8 pt and up. A label that does not
  survive that size is deleted, not shrunk.
- Vector PDF (fonts embedded) plus a TIFF copy. File name `5J_graphical_abstract.pdf` / `.tiff`.
- No third-party material (logos, map tiles, licensed icons). No institute logos (INE, ISTAT, UKDS).

## 2. What it must say, in one sentence

A fast learned stand-in for EnergyPlus is trusted only if it gets the occupancy effect right, the
difference between two households in the same building, and a copy that cannot see occupancy fails
that test.

## 3. Layout: three panels, left to right, equal height

White background. Thin grey rules between panels. One sans-serif font (Arial, Helvetica or similar).
All text horizontal. Flat shapes only.

### Panel A (left, about 35 % of width): "Paired simulations"

- One simple house outline in the centre, with a small sun-and-cloud weather mark above it. Both are
  drawn once, heavy, with a small tag under them: **Same building, same weather**.
- To the left, a column of five thin horizontal day strips (24 cells each), each strip a different
  pattern of filled and empty cells, standing for five households' at-home hours. Column label:
  **Time-use diaries: Spain, Italy, UK**. Country colours on the strip edges (palette below).
- Five thin arrows from the strips into the house, then out of the house into five small hourly load
  curves stacked on the right, each slightly different. Label on the house: **EnergyPlus**.
- Label over the curves: **Only occupancy changes**.
- Footer line of the panel: **[N] paired annual runs** (N from the Step 3 ledger; until then leave the
  bracket empty and grey).

### Panel B (centre, about 30 % of width): "A fast stand-in"

- A dark navy rounded box: **Learned surrogate**. Three inputs enter from the left as small tags:
  **occupancy sequence**, **building**, **weather**. Three outputs leave on the right as small tags:
  **heating**, **cooling**, **electricity**, each with the word **hourly** once, above the three.
- Below it, a grey box of the same shape with a small crossed-out occupancy strip as its only input
  mark: **Control: same model, occupancy shuffled**.
- Under both boxes, one line: **Scored on new households, new buildings and a new country**.

### Panel C (right, about 35 % of width): "The occupancy effect test" (PLACEHOLDER until Step 6)

- Title: **Difference between two households in the same building**
- A scatter: horizontal axis **EnergyPlus difference**, vertical axis **surrogate difference**, one
  diagonal line. Two dot clouds: navy dots **surrogate** close to the diagonal (if the result says so),
  grey dots **control** flat around zero (if the result says so). Units on the axes: **kWh per year**.
- Print only the values listed in the table below, as small labels near each cloud.
- Until Step 6 is done, draw the panel as an empty grey frame with the title and axis labels only.

| Label | Value | Source (filled after Step 6) |
|---|---|---|
| surrogate, fit on paired differences | [R2 value] | Step 6 result file, G5J.3 row, electricity |
| control, fit on paired differences | [R2 value] | Step 6 result file, G5J.4 row |
| end uses shown | [electricity only, or more] | only end uses above the noise floor; an end use scored NOT_EVALUABLE is not drawn |

### Bottom strip (full width, thin)

One centred line, bold: **[One-sentence finding, written from the Step 6 result]**. Until then:
**A surrogate is trusted only where it passes the occupancy test.**
Right-aligned, small: **[N] times faster than EnergyPlus** (from G5J.7; leave out if not measured).

## 4. Palette (colour-blind safe, same as 4J)

| Element | Colour |
|---|---|
| Spain | #CC6677 (rose) |
| UK | #332288 (indigo) |
| Italy | #44AA99 (teal) |
| Surrogate box and dots | dark navy fill, white text |
| Control box and dots, rules, axes | mid grey |
| Text | #111111 |

## 5. Permitted text (complete list; nothing else appears in the image)

Paired simulations · Same building, same weather · Time-use diaries: Spain, Italy, UK · EnergyPlus ·
Only occupancy changes · [N] paired annual runs · A fast stand-in · Learned surrogate · occupancy
sequence · building · weather · hourly · heating · cooling · electricity · Control: same model,
occupancy shuffled · Scored on new households, new buildings and a new country · The occupancy effect
test · Difference between two households in the same building · EnergyPlus difference · surrogate
difference · kWh per year · surrogate · control · the Panel C values · the bottom-strip sentence ·
[N] times faster than EnergyPlus

## 6. Do not

- No result number before Step 6 is done; no invented "R2 = 0.9" or "1000x faster" as decoration.
- No model name, no parameter counts, no project codes ("B4", "5J", "G5J", "WP", "HETUS", "TCN",
  "LOCO", "NOT_EVALUABLE", "noise floor").
- No people, faces, photographs of houses, robots, brains or glowing circuits. Simple flat shapes only.
- No map, no flags, no institute logos.
- No red-green pair as the only distinction. No rotated text. No 3D, no shadows, no gradients.
- No meta notes ("illustrative", "not to scale", "values from Table 3", "placeholder").
- If the UK is dropped (licence decision, O-1), remove "UK" from Panel A and from the palette.

## 7. Image-generator prompt for Panels A and B only (copy as one block)

> Flat vector scientific illustration, white background, landscape 2.5 : 1, two panels side by side
> separated by a thin grey vertical rule, one sans-serif font, all text horizontal, no people, no
> shadows, no gradients, no 3D. Left panel titled "Paired simulations": on the left a column of five
> thin horizontal 24-cell day strips, each with a different pattern of filled cells, edges coloured
> rose #CC6677, teal #44AA99 and indigo #332288, labelled "Time-use diaries: Spain, Italy, UK"; five
> thin arrows run from the strips into one simple house outline labelled "EnergyPlus", with a small
> flat sun-and-cloud mark above it and the tag "Same building, same weather" below it; five arrows
> leave the house into five small stacked hourly load curves, each slightly different, labelled "Only
> occupancy changes". Right panel titled "A fast stand-in": a dark navy rounded box with white text
> "Learned surrogate", three small input tags on its left "occupancy sequence", "building",
> "weather", three small output tags on its right "heating", "cooling", "electricity" with the word
> "hourly" above them; below it a mid-grey rounded box "Control: same model, occupancy shuffled" with
> a small crossed-out day strip as its input; one line under both boxes "Scored on new households,
> new buildings and a new country". Use no other words. Text colour #111111.

Leave the right third of the canvas empty for Panel C, which is plotted from data and placed after.

## 8. After it is made (author, then manager)

- Check every string against section 5; any extra word (common with image generators) is removed or
  the panel is redrawn.
- Check at 13 cm wide on screen: every label reads without zoom.
- After Step 6: plot Panel C from the frozen result file, fill the table in section 3, write the
  bottom-strip sentence from the result, and record the source file of each number in the checklist
  Progress Log.

## 9. Fix list for draft 1 (2026-09-28, copy as one block into the tool that wrote the script)

> Edit `5J_docs_occ/figures/scripts/generate_5J_graphical_abstract.py` only, then re-run it once. It writes
> `5J_docs_occ/figures/5J_graphical_abstract.{pdf,png,tiff}`. Do not copy the outputs anywhere else. Do not change any
> wording, and keep the permitted-text list in section 5.
> 1. Even spacing. `strip_ys` (line ~147) is `[25.8, 22.4, 19.0, 16.5, 11.0]`. Make it five equally spaced values that
>    span the house height. The five load curves use the same list, so they follow.
> 2. Visible arrows. Each strip-to-house and house-to-curve arrow must show as a line with a head, at least about 1.5 mm
>    long at 13 cm width. Draw the arrows above the house outline (raise their zorder), or end them on the house wall, so
>    no line is hidden under the house.
> 3. Palette. The cross over the shuffled strip (lines ~308-314, colour `#DC2626`) becomes mid grey `#64748B`. No red
>    anywhere.
> 4. Text size. Every text item goes from 7.0 pt to at least 8.0 pt, and titles to about 8.5 pt. If a label no longer
>    fits, reflow the panel or shorten the line break. Never go back below 8 pt, and never delete a permitted string.
> 5. While reflowing, set the panel widths to about 35 / 30 / 35 % (dividers near 35 and 65), and keep every gap between
>    items at least 1 pt.
> After the run, print the smallest font size, the smallest gap and the three divider positions, and confirm the clash
> check still covers every drawn object type (text, boxes, arrows, strips, curves, house, frame).
