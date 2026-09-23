# Method figure M1: from a 10-minute diary to an hourly household schedule (image prompt)

Paste the prompt below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_M1_diary_to_hourly.png` in `submission/figures/`.
It explains Eqs. 1, 2, 6 and 7 and the hour averaging of the Methods section. Final figure number is
set when the paper is renumbered.

## Prompt to paste

Draw a simple, clean scientific explanatory diagram for a journal article in Applied Energy. It shows,
with one small made-up example, how a person's 10-minute time-use diary becomes one hourly value of a
household occupancy schedule. Readable at a glance: few elements, short labels, left-to-right flow.

Style: white background, flat design, thin dark-grey outlines, small square cells for time slots.
Two colours only for cells: light blue = "At home", white = "Away". Sans-serif text (Arial or
Helvetica), one font size for labels. No icons, no clip art, no 3D, no shadows, no gradients, no logos,
no title inside the image. Landscape, about 190 mm wide by 80 mm tall, at least 600 dpi.

Layout: four panels from left to right, joined by solid arrows. Each panel has a short bold heading.

Panel 1, heading "1. Ten-minute diary". Two rows of six small cells (one hour of diary), labelled
at the left "Person A" and "Person B". Above the cells, a thin time ruler with two ticks labelled
"30 min" and "30 min", each spanning three cells.
- Person A cells, left to right: home, home, away | away, away, home
- Person B cells, left to right: home, home, home | home, away, home
Under Person A's first three cells, three tiny activity words: "Cooking", "Cooking", "Eating".

Panel 2, heading "2. Thirty-minute slots". Same two rows, now two wider cells each.
- Person A: home | away
- Person B: home | home
A small note under the panel: "At home if 2 of 3 ten-minute slots are at home".
Under Person A's first cell: "Cooking" with the note "Activity = most frequent of 3".

Panel 3, heading "3. Household average". One row of two wider cells showing numbers:
"1.0" | "0.5". A small note: "Share of household members at home".

Panel 4, heading "4. Hourly value". One single cell showing "0.75". A small note: "Mean of the two
30-minute values". Under it, one more small line: "Clock shifted so the day starts at midnight".

Use these exact label texts and numbers, word for word. No other text anywhere in the image.

Must not:
- No numbers other than those listed (30 min, 1.0, 0.5, 0.75, and 2 of 3).
- No abbreviations or codes (no GSS, act30, hom30, occ48, slot numbers, equation numbers).
- No extra people, rows, panels or captions.

## Acceptance checklist (author, after generating)

- Four panels, left to right, headings exactly as listed.
- Cell colours follow the listed pattern exactly (check every cell: the example must be arithmetically
  right; Person A slot 1 = home because 2 of 3 are home; slot 2 = away because 1 of 3 is home).
- Numbers 1.0, 0.5 and 0.75 appear exactly once each.
- Readable without zooming at 190 mm width.

## Draft caption (one sentence, per the author's caption rule)

Figure M1. Conversion of a ten-minute diary into an hourly household occupancy value.
