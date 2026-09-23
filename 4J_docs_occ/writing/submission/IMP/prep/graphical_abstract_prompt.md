# Graphical abstract prompt (4J, Energy and Buildings), 2026-09-23

The author makes this image. This file is the text brief. Every number below comes from
`IMP/prep/results_number_sheet.md`, `IMP/impl/P3_appliance_real_and_donor.md` (result entry) or
`IMP/impl/P10_in_sample_vs_transfer.md`. No value may be altered, rounded differently, or added.

Because the marks carry measured values (dot positions, peak hours), draw it in plotting or slide
software (matplotlib, PowerPoint, Illustrator), not an image generator. If any AI tool is used for any
part of it, the use must follow Elsevier's GenAI policy and be named in the manuscript's generative AI
declaration.

## 1. Journal rules (E&B guide, `writing/resources/E_and_B_guide_for_authors_2026-09-23.txt`)

- Required at submission, uploaded as a SEPARATE file (not inside the manuscript).
- At least 531 x 1328 pixels (height x width), or proportionally more. Aim for 1062 x 2656 pixels or
  larger, landscape, aspect about 1 : 2.5.
- Must be readable at 5 x 13 cm. At that size, no text smaller than about 7 pt; prefer 8 pt and up.
  If a label does not survive that size, delete it rather than shrink it.
- Preferred file types: TIFF, EPS, PDF or MS Office. Recommended: vector PDF (fonts embedded), plus a
  TIFF copy at the pixel size above.
- File name: `4J_graphical_abstract.pdf` (and `.tiff`). Save in `writing/submission/figures/`.
- No third-party material (logos, map tiles, icons under licence) unless permission is held.

## 2. What it must say, in one sentence

When a country has no diaries, a fine-tuned language model generates worse diaries than simply
reweighting real diaries from other countries, and its diaries do not carry the country's appliance
timing.

## 3. Layout: three panels, left to right, equal height

White background. Thin grey rules between panels. One sans-serif font (Arial, Helvetica or similar).
All text horizontal.

### Panel A (left, about 30 % of width): "The test"

- Three small country tiles in a row: **Spain**, **Italy**, **UK**. One tile (draw it as the UK tile)
  has a dashed outline and the tag **held out**.
- Under the tiles, two arrows lead from the two solid tiles toward the held-out tile, one above the
  other:
  - Upper arrow, through a dark navy box: **Fine-tuned language model**, small line under it:
    **trained on the other two countries**.
  - Lower arrow, through a grey box: **Real diaries of the other two**, small line under it:
    **reweighted to the held-out country's margins**.
- Both arrows end at a small box: **Scored against the held-out country's published tables**.
- Footer line of the panel: **Each country held out in turn. 73,254 diaries.**

### Panel B (centre, about 35 % of width): "Result: the model does not beat reweighting"

- One horizontal axis, label **Model error / reweighted-diary error**, ticks at 1, 2, 3, 4.
- A solid vertical line at 1 with the label **reweighted real diaries**.
- Nine dots, one per country-by-age cell, coloured by country (palette below), placed at
  model MAE / baseline MAE computed from the table below. Print no value on the dots.
- Print only two value labels under the axis: **1.1** at the lowest dot and **3.9** at the highest.
- Headline above the axis, bold: **Worse in 9 of 9 cells: 1.1 to 3.9 times the error**
- Second line below the axis, regular: **Also misses the 15 % bar on its own training countries
  (33 to 158 %); real diaries meet it (5 to 12 %)**

Data for the dots (time-budget mean absolute error, minutes per day; source: number sheet rows TB3-1
to TB3-9). Positions only; do not print these values.

| Held-out country | Age band | Model | Reweighted real diaries |
|---|---|---|---|
| Spain | 25-44 | 36.81 | 9.94 |
| Spain | 45-64 | 34.52 | 8.82 |
| Spain | 65+ | 44.32 | 11.81 |
| UK | 25-44 | 58.91 | 21.79 |
| UK | 45-64 | 60.44 | 19.21 |
| UK | 65+ | 21.24 | 18.54 |
| Italy | 25-44 | 62.24 | 19.51 |
| Italy | 45-64 | 33.95 | 13.85 |
| Italy | 65+ | 35.84 | 15.51 |

### Panel C (right, about 35 % of width): "For building energy models: appliance timing"

- Title: **Evening appliance electricity peak, by diary source**
- One horizontal hour axis from 12:00 to 22:00, ticks every 2 hours.
- Three rows, top to bottom, each with one marker per country at its peak hour (country colours,
  country initial or short name next to the marker):

| Row label | Spain | Italy | UK |
|---|---|---|---|
| **Real diaries** | 21:00 | 19:00 | 18:00 |
| **Generated diaries** | 14:00 | 18:00 | 20:00 |
| **Reweighted diaries** | 19:00 | 21:00 | 21:00 |

- Draw the "Real diaries" row slightly heavier (it is the reference). Do not draw arrows, brackets or
  spans between markers, and do not rank countries: peaks are flat-topped, so one-hour differences
  carry no order.
- Line under the rows: **Neither synthetic source carries the country's timing**

### Bottom strip (full width, thin)

One centred line, bold: **Where a country has no diaries, reweighted real diaries from comparable
countries are the stronger default.**
Right-aligned, small: **Pre-registered before training, 2026-08-18**

## 4. Palette (matches the paper's figures, colour-blind safe)

| Element | Colour |
|---|---|
| Spain | #CC6677 (rose) |
| UK | #332288 (indigo) |
| Italy | #44AA99 (teal) |
| Model box | dark navy fill, white text |
| Reweighting box, rules, axis | mid grey |
| Text | #111111 |

## 5. Permitted text (complete list; nothing else appears in the image)

Spain · Italy · UK · held out · Fine-tuned language model · trained on the other two countries ·
Real diaries of the other two · reweighted to the held-out country's margins · Scored against the
held-out country's published tables · Each country held out in turn. 73,254 diaries. · The test ·
Result: the model does not beat reweighting · Model error / reweighted-diary error · 1 · 2 · 3 · 4 ·
reweighted real diaries · 1.1 · 3.9 · Worse in 9 of 9 cells: 1.1 to 3.9 times the error · Also misses
the 15 % bar on its own training countries (33 to 158 %); real diaries meet it (5 to 12 %) · For
building energy models: appliance timing · Evening appliance electricity peak, by diary source · hour
labels 12:00 to 22:00 · Real diaries · Generated diaries · Reweighted diaries · Neither synthetic source
carries the country's timing · Where a country has no diaries, reweighted real diaries from comparable
countries are the stronger default. · Pre-registered before training, 2026-08-18

## 6. Do not

- Do not write "Britain", "six hours", "2 to 6", or the watt values 518, 395 or 422 anywhere.
- Do not show any spread or span between the generated peaks.
- No model name, no parameter counts, no project codes (no "LOCO", "IPF", "MAE", "fold", "gate",
  "band", "null").
- No people, faces, houses drawn as photographs, robots or brain icons. Simple flat shapes only.
- No red-green pair as the only distinction. No rotated text. No 3D, no shadows.
- No meta notes ("illustrative", "not to scale", "values from Table 3").

## 7. After it is made (author, then manager)

- Check every string against section 5 and every dot against the table in Panel B.
- Check it at 13 cm wide on screen: every label must read without zoom.
- Save as PDF and TIFF in `writing/submission/figures/`; the manager removes the old embedded graphical
  abstract (`figures/HETUS_LLM_CrossNational_Pipeline.png`) from the manuscript body and lists the new
  file in `IMP/impl/P14_package_checklist.md`.
