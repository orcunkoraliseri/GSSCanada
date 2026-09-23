# Method figure M3: how activities at home become equipment power (image prompt)

Paste the prompt below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_M3_activity_to_power.png` in `submission/figures/`.
It explains Eqs. 8 and 9 of the Methods section. Final figure number is set when the paper is renumbered.

## Prompt to paste

Draw a simple, clean scientific explanatory diagram for a journal article in Applied Energy. It shows
how the activities of the people at home in one 30-minute time slot are turned into the household's
equipment power, and how that power is then scaled to a national annual total. Readable at a glance.

Style: white background, flat design, plain rounded rectangles, thin dark-grey outlines, soft
colour-blind-safe fills (light blue, light green, light orange, light grey). Sans-serif text (Arial or
Helvetica), one font size for labels. Simple flat person silhouettes are allowed for the three people
only; no other icons, no clip art, no 3D, no shadows, no gradients, no logos, no title inside the image.
Landscape, about 190 mm wide by 90 mm tall, at least 600 dpi.

Layout: left to right, four columns joined by solid arrows.

Column 1, heading "People at home (one 30-minute slot)". Three simple person silhouettes stacked
vertically, each with a label:
- "Person 1: Cooking"
- "Person 2: Watching TV"
- "Person 3: Using a computer"

Column 2, two boxes stacked:
- Top box, light green, heading "Shared devices", body text: "Cooking, TV, washer, dryer, dishwasher".
  Under it a short note: "Used once per household; grows less than the number of people at home".
- Bottom box, light blue, heading "Personal devices", body text: "Computer". Under it a short note:
  "Adds up per person".
Arrows: Person 1 and Person 2 go to the "Shared devices" box; Person 3 goes to the "Personal devices" box.

Column 3, one box, light orange, heading "Household equipment power". Body text:
"Always-on base load + shared devices + personal devices". Both boxes of column 2 have an arrow into it,
and one more small light-grey box above it labelled "Always-on base load (fridge, standby)" with an
arrow into it.

Column 4, one box, light grey, heading "Scaled to a national total". Body text:
"Annual total matched to the national household energy survey, by dwelling type".
Arrow from column 3 into column 4. Under column 4 a short note: "Scaling factor = target / simulated
annual energy".

Use these exact label texts, word for word. No other text anywhere in the image.

Must not:
- No numbers, watts, kWh or percentages anywhere.
- No abbreviations or equation symbols (no SHEU, NRCan, P_b, eta, f_e, w_b).
- No extra people, devices, boxes or captions.

## Acceptance checklist (author, after generating)

- Exactly three people with the listed activities; Persons 1 and 2 point to shared devices, Person 3
  to personal devices.
- Four columns in order; the base-load box feeds the household power box.
- Every label spelled exactly as listed; no numbers.
- Readable without zooming at 190 mm width.

## Draft caption (one sentence, per the author's caption rule)

Figure M3. Construction of household equipment power from the activities of the people at home.
