# Figures 2 and 4, image generation prompts (v4, 2026-09-25)

Paste ONLY one prompt block at a time into Gemini. This file holds prompts only; no image is created here.
Save the results under the SAME file names so the manuscript picks them up:
- Figure 2 -> `Figure_03_three_head_transformer.png`
- Figure 4 -> `Figure_06_tag2_dispatch.png`
Long edge at least 3500 pixels. Tell the manager the folder when done.

## Why the installed images must be replaced

The installed Figures 2 and 4 are the old v3 drawings. They read as internal notes, not journal figures:
- code names (AT_WORK, AT_RETAIL, resid, HHSIZE, Number_of_People_Schedule_Name, SLAW/UW, pos_weight);
- process history ("the two-channel stage bug that passed every input-side check ...", "HARD WIRING
  GATE", "SLAW/UW dropped, unstable ...");
- a wrong hotel model line ("SARIMA(1,1,1)(1,1,1,12) per province"), now corrected in the text;
- "--" used as a dash, and a title banner ("3 GSS heads + 1 non-GSS side-track").
Exact settings (loss weights, thresholds, epochs) stay in the text, where they are already given.

## Prompt, Figure 2 (occupancy model)

```
Clean flat 2D flowchart for an academic building-energy paper. Strictly flat: no 3D, no isometric, no perspective, no shadows, no gradients, no clip art. Wide landscape, white background, sans-serif labels (Arial or Helvetica), generous white space, muted colours: warm grey for inputs, slate blue for the model, soft teal for outputs, one soft amber accent. Long edge at least 3500 pixels. Reading order left to right.

UPPER ROW (the main path):
  One warm-grey input card labelled "Person and calendar attributes, survey year".
  Arrow to one tall slate-blue box labelled "Shared Transformer encoder".
  From the encoder, three arrows fan out to three slate-blue boxes stacked vertically: "Residential head", "Office head", "Retail head".
  Each head points right to its own small teal box: "Presence at home", "Presence at work", "Presence in shops".
  The three teal boxes converge into one amber box labelled "One channel per time slot".
  One arrow leaves the amber box to the right, labelled "half-hourly schedules".

LOWER ROW (separate, below a thin horizontal gap, not connected to the encoder):
  One warm-grey card labelled "Monthly hotel occupancy, two provinces".
  Arrow to one slate-blue box labelled "Hotel model".
  One arrow leaves it to the right, labelled "guest-room multiplier".

No other text. No numbers. No abbreviations or codes (no GSS, SARIMA, AT_WORK, resid, PCGrad). No colour names written as text. No title banner, no notes, no footnote, no logos.
```

Acceptance: two rows; the hotel row does not touch the encoder; exactly the listed words; no title.

## Prompt, Figure 4 (routing by space tag)

```
Clean flat 2D flowchart for an academic building-energy paper. Strictly flat: no 3D, no isometric, no perspective, no shadows, no gradients, no clip art. Wide landscape, white background, sans-serif labels (Arial or Helvetica), generous white space, muted colours: slate blue for the routing step, soft amber for "replace", teal for "scale", warm grey for "unchanged". Long edge at least 3500 pixels. Reading order left to right.

LEFT: one slate-blue diamond labelled "Space use tag".

Four arrows leave the diamond to the right, each with a short label ON the arrow, and each ending at its own box on the right, stacked vertically in this order, one arrow per box, arrows must not cross:
  arrow "apartment" -> amber box "Replace occupant schedule" with a smaller line "household schedule, one household per apartment"
  arrow "office, retail, guest room" -> teal box "Scale code schedule" with a smaller line "lighting and plug loads follow occupancy above a standby floor"
  arrow "amenity, service" -> warm-grey box "Keep prototype schedule"
  arrow "no matching channel" -> warm-grey box with a dashed outline "Keep prototype schedule"

No other text. No numbers. No abbreviations or codes (no NECB, PNNL, HHSIZE, Tag 2, gate). No colour names written as text. No title banner, no notes, no footnote, no logos.
```

Acceptance: each arrow label sits on its own arrow and the arrow ends at the matching box; no notes at the bottom; exactly the listed words.
