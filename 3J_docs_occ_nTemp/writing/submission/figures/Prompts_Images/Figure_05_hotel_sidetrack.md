# Figure 5 -- Hotel Side-Track (Tourism Statistics to SARIMA to Guest-Room Multiplier)
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the non-GSS hotel channel end to end: monthly tourism-statistics series, SARIMA forecast with a COVID indicator, the diurnal shape function s(t), and the resulting hotel_multiplier used to modulate guest-room schedules.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 6 box ("HOTEL SIDE-TRACK"); `deepResearch/dr_L3-05_hotel_diurnal_shape_REPORT.md`

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
