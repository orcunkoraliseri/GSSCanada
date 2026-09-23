# Method figure M2: raking the at-home share of one time slot to a target (image prompt)

Paste the prompt below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_M2_raking.png` in `submission/figures/`.
It explains Eqs. 4 and 5 of the Methods section. Final figure number is set when the paper is renumbered.

## Prompt to paste

Draw a simple, clean scientific explanatory diagram for a journal article in Applied Energy. It shows,
with one small made-up example, how the number of people at home in one 30-minute time slot is
adjusted to match a target by changing as few records as possible. Readable at a glance.

Style: white background, flat design, thin dark-grey outlines. Each diary record is drawn as one small
rounded square. Colours: light blue = "At home", white = "Away", and an orange outline marks a record
that is changed. Sans-serif text (Arial or Helvetica), one font size for labels. No icons, no clip art,
no 3D, no shadows, no gradients, no logos, no title inside the image. Landscape, about 190 mm wide by
70 mm tall, at least 600 dpi.

Layout: three panels from left to right, joined by solid arrows.

Panel 1, heading "Before". A row of 10 squares: 4 light blue (at home) and 6 white (away), in this
order: blue, white, blue, white, white, blue, white, white, blue, white. Below: "4 of 10 at home".

Panel 2, heading "Target". A simple text box with three short lines:
"Target share: 0.6"
"Target count: 0.6 x 10 = 6"
"Records to change: 6 - 4 = 2"

Panel 3, heading "After". The same row of 10 squares in the same order, but squares 2 and 7 (counting
from the left) are now light blue with an orange outline. Now 6 are blue. Below: "6 of 10 at home".
Under the two changed squares, one small note with a thin pointer: "Changed first: records where the
activity changes at this slot".

Use these exact label texts and numbers, word for word. No other text anywhere in the image.

Must not:
- No numbers other than those listed.
- No abbreviations or equation symbols (no n_tgt, Delta, p, N, slot codes).
- No extra panels, arrows or captions.

## Acceptance checklist (author, after generating)

- Panel 1 shows exactly 4 blue of 10; panel 3 shows exactly 6 blue of 10.
- Only squares 2 and 7 change, and only they carry the orange outline.
- Target box text exactly as listed.
- Readable without zooming at 190 mm width.

## Draft caption (one sentence, per the author's caption rule)

Figure M2. Adjustment of the at-home count in one time slot to its target.
