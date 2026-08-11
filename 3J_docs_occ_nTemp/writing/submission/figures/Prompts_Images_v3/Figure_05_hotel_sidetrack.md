# Figure 5 -- Hotel Side-Track (Tourism Statistics to SARIMA to Guest-Room Multiplier)

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the non-GSS hotel channel end to end: monthly tourism-statistics series, SARIMA forecast with a COVID indicator, the diurnal shape function s(t), and the resulting hotel_multiplier used to modulate guest-room schedules.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 6 box ("HOTEL SIDE-TRACK"); `deepResearch/dr_L3-05_hotel_diurnal_shape_REPORT.md`

> 🔴 **Naming rule, 2026-08-11.** The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## 🔴 TERMINOLOGY LOCK (v2) -- applies to every string drawn in this image

The project's internal stage codes must **not** appear anywhere in the artwork, in any spelling or
punctuation: `Leg-1`, `Leg 1`, `Leg1`, `Leg-2`, `Leg-3`, `leg`, `2J`, `3J`, `1J`, `0J`.
They are internal build names, undefined for any reader, and the manuscript text was cleared of them
on 2026-08-11. If a stage must be named, use the descriptive form:

| do NOT draw | draw this instead |
|---|---|
| Leg-1 | `single-channel stage` (or `Residential only`) |
| Leg-2 | `two-channel stage` (or `Residential + Office`) |
| Leg-3 / 3J / this leg | `this study` (or `Residential + Office + Retail + Hotel`) |
| "three legs" / "the legs" | `three stages` |
| 2J / 1J / 0J | `the predecessor study` |

`**Source:**` lines elsewhere in this file cite real folder names on disk (`Leg3_4-split/...`).
Those are provenance for the authors and are **outside the fenced prompt** -- they are never drawn.

**Resolution.** Elsevier requires 500 dpi for combination art. Placed at 7 in wide that is
**3500 px minimum on the long edge**; generate as large as the tool allows and do not upscale
afterwards. The 2026-08-09/11 images came back at 1376 x 768 (~197 dpi), which fails.

---

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. Left: two small flat stacked data-table/cylinder icons labelled "ISQ (QC)" and "CBRE (AB)", both warm-grey, feeding into a single amber-filled box labelled "SARIMA Forecast" with a small line-chart icon showing a seasonal wave. A small dashed vertical band inside or beside the SARIMA box marks a "COVID Indicator" period. The SARIMA box feeds right into a slate-blue/teal box labelled "Monthly Rate". Below and separate, a second small slate-blue/teal box labelled "Diurnal Shape s(t)" contains a simple flat 24-hour step-curve icon: flat high plateau on both ends (overnight) and a dip in the middle (daytime). The "Monthly Rate" box and the "Diurnal Shape s(t)" box both feed down/right into a final warm-grey box labelled "Hotel Multiplier", which has one output arrow labelled "to Guest-Room Schedule". A small separate flat validation-checkmark callout card sits below the SARIMA box labelled "Backcast Gate". Minimal, generous whitespace, restrained academic palette.

SCENE: "ISQ (QC)" and "CBRE (AB)" icons to amber "SARIMA Forecast" box (with COVID-indicator dashed band) to "Monthly Rate" box; separately "Diurnal Shape s(t)" box with its step-curve icon; both converge into "Hotel Multiplier" box with an output arrow to "Guest-Room Schedule". "Backcast Gate" validation card sits below the SARIMA box.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Input icons: "ISQ monthly occupancy series (QC)" · "CBRE monthly occupancy series (AB)"
- SARIMA box: "SARIMA(1,1,1)(1,1,1,12) per province"
- COVID indicator band label: "COVID indicator, 2020-03 to 2022-06"
- Formula callout (on the Hotel Multiplier box): "hotel_multiplier(t, month, PR) = s(t) x monthly_rate(month, PR)"
- Diurnal shape s(t) callout, with values on the step-curve: "overnight plateau 1.00, 22:00 to 06:00" · "day trough 0.200, weekday" · "day trough 0.308, weekend"
- Backcast gate card: "Backcast gate: QC + AB, 2015 to 2019, MAE < 0.05"
- 2030 scenario band callout (small side note near the output arrow): "2030 bands: 0.92 / 1.00 / 1.05"
- Side-track note (small text near the whole figure): "this entire channel bypasses the Transformer -- population-aggregate monthly series, no GSS respondents behind it"

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- The single amber-filled element is the "SARIMA Forecast" box
- The diurnal shape step-curve icon must show two flat high segments (overnight) and one lower dip (daytime), not a smooth sine wave -- it is a two-level step shape, not continuous
- Keep the monthly-rate path (province, seasonal, SARIMA) and the diurnal-shape path (time-of-day, fixed) visually separate until they multiply together in the final "Hotel Multiplier" box
