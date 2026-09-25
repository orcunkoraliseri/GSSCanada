# Graphical abstract, image generation prompt (new lead, 2026-09-25)

> SUPERSEDED 2026-09-25: use `graphicalAbstract_v5.md` (complete, standalone).

Paste ONLY the prompt block below into Gemini. This file is a prompt only; no image is created here.
Save the result as `graphicalAbstract.png` and tell the manager the folder. It replaces the v3 image,
whose lead ("four peak hours", "coincidence factor < 1" as the headline) the paper no longer makes.
The new lead follows the current Highlights: survey schedules change WHEN PEOPLE ARE PRESENT far more
than WHEN ENERGY IS USED; office and retail energy follow survey occupancy, but the building peak is set
by a winter-morning plant start-up under both schedule sets.

The image carries NO numbers on purpose: the rebuilt simulation numbers are being substituted into the
text now, and an image model mis-draws digits. If a number is wanted later, add it as an overlay on the
finished image, never through the prompt.

## Prompt to paste

```
Clean flat 2D graphical abstract for an academic building-energy paper in Building and Environment. Strictly flat: no 3D, no isometric, no perspective, no shadows, no gradients, no photorealism, no clip art. Wide landscape, white background, sans-serif labels (Arial or Helvetica), generous white space. Four muted, colour-blind-safe channel colours used consistently everywhere (one for residents, one for office workers, one for shoppers, one for hotel guests) plus thin neutral grey for structure. Long edge at least 3500 pixels.

Three panels reading left to right, separated by white space, not by boxes.

LEFT PANEL, heading "Four occupancy schedules": four small flat symbols stacked vertically, each in its channel colour with a short label to its right: a house outline labelled "Residents", a briefcase labelled "Office workers", a shopping bag labelled "Shoppers", a bed labelled "Hotel guests". The first three are gathered by one thin bracket labelled "time-use diaries"; the bed has its own thin line labelled "hotel statistics". One arrow leaves the panel to the right.

CENTRE PANEL, heading "One mixed-use tower": one tall flat tower outline divided into horizontal bands in the four channel colours (hotel band at the top, residential bands in the upper middle, office bands in the lower middle, one thin shop band at street level), so all four uses clearly sit inside ONE building. One small grey box at the base labelled "shared plant".

RIGHT PANEL, two small flat 24-hour line charts stacked one above the other, same width, hour ticks at 0, 6, 12, 18, 24 with no other numbers:
  Top chart, labelled "When people are present": two thin curves for office workers, one dashed grey labelled "code schedule" and one solid in the office colour labelled "survey schedule". Both are low at night and high in the working day, but the survey curve is clearly LOWER through the whole working day, at little more than half the height of the code curve.
  Bottom chart, labelled "When energy is used": the same two line styles, dashed grey "code schedule" and solid "survey schedule", nearly on top of each other, with their highest point at the same hour.
Beside the bottom chart, one small flat callout card reading "presence shifts, energy timing holds".

No other text. No numbers anywhere except the hour ticks. No colour names written as text. No abbreviations or codes (no GSS, NECB, EUI, Leg, 2J, 3J). No logos, no title banner.
```

## Acceptance checklist (author, after generating)

- One building in the centre (not four buildings side by side).
- Top chart: the two curves visibly differ; bottom chart: the two curves nearly overlap and peak at the same hour.
- Only the listed words appear; no numbers other than hour ticks; no colour words drawn.
- Long edge at least 3500 px.

## Change 2026-09-25 (after stage 2c)

Top chart switched from hotel to office. The dwelling-unit code control (V3c) also puts guests and
residents in the tower at night, so the hotel night contrast is no longer a finding of the paper. The
office presence gap (3.14 against 1.80 occupants per 100 m2, weekday daytime) holds against both controls.

## Note for the manager

Re-read this prompt against the final Highlights after the stage 2 rewrite. If the rewrite changes the
lead (for example the V3c limitation: part of the night-presence contrast comes from the code schedule
itself), adjust the top-chart wording before the author generates the image.

## Fix round 2 (2026-09-25, after checking the first Gemini image)

Problems in the first image: (1) the top chart writes "survey schedule" twice; (2) the hotel colour is not
consistent: the bed icon uses the residents' mauve while the hotel band in the tower is a pale teal close to the
office teal. Paste the full prompt above again, then add:

"Colour rule, strict: exactly four channel colours, each used for one channel only and the same everywhere:
residents = mauve, office workers = teal, shoppers = coral, hotel guests = amber. The bed icon and the hotel band
at the top of the tower are both amber. No other element is amber. Label rule, strict: in each chart the words
'code schedule' appear once and 'survey schedule' appear once, each next to its own line."
