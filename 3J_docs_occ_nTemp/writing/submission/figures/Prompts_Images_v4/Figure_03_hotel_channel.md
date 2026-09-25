# Figure 3 (file `Figure_05_hotel_sidetrack.png`), hotel channel, image generation prompt (v4, 2026-09-25)

> SUPERSEDED 2026-09-25: use `Figure_03_hotel_channel_v5.md` (complete, standalone).

Paste ONLY the prompt block below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_05_hotel_sidetrack.png` (same file name, so the manuscript picks it up) and
tell the manager the folder. Long edge at least 3500 pixels.

## Why the v3 image must be replaced

A fact trace of the code (`writing/implementation/IMP/hotel_channel_fact_trace_2026-09-25.md`) found
the v3 image wrong in four places:
- The Alberta source is the Government of Alberta tourism market monitor, not CBRE.
- The seasonal model is SARIMA(1,1,0)(0,1,0,12), fitted on Alberta and reused for Quebec, not
  SARIMA(1,1,1)(1,1,1,12) per province.
- The seasonal model does NOT produce the monthly rate used in the simulations. 2022 uses the observed
  monthly rate; 2030 uses the 2019 monthly pattern rescaled to a recovery level. The model only checks
  the seasonal pattern and the pandemic dip.
- The backcast check covers 2015 to 2019 for Alberta but 2019 only for Quebec.
It also carries a process note at the bottom and "--" dashes, which a journal figure must not.

## Prompt to paste

```
Clean flat 2D flowchart for an academic building-energy paper. Strictly flat: no 3D, no isometric, no perspective, no shadows, no gradients, no clip art. Wide landscape, white background, sans-serif labels (Arial or Helvetica), generous white space, muted colours: warm grey for data, slate blue for processing, one soft amber accent. Long edge at least 3500 pixels. Reading order left to right.

LEFT: two small flat data cards stacked vertically, warm grey, each with a small table icon:
  card 1 labelled "Quebec monthly hotel occupancy, 2019 to 2022"
  card 2 labelled "Alberta monthly hotel occupancy, 2011 to 2022"

CENTRE: two slate-blue boxes stacked vertically, both fed by arrows from both data cards:
  upper box labelled "2022: observed monthly rate"
  lower box labelled "2030: 2019 monthly pattern scaled to recovery level", with a small note under it "three bands: 0.92, 1.00, 1.05"
  Both boxes point right into one small slate-blue box labelled "Monthly rate r".

BELOW THE DATA CARDS, off the main path: one thin-outlined white box labelled "Seasonal model check" with a tiny seasonal wave icon, fed by a thin dashed arrow from the data cards. Inside it, two short lines: "pattern and pandemic dip" and "not used for the simulated rate". No arrow leaves this box.

LOWER CENTRE: one slate-blue box labelled "Daily guest-room shape s(t)" containing a flat two-level step curve over 24 hours: high flat segments at night on both ends, one lower flat dip in the daytime middle. It is a step shape, not a smooth wave.

RIGHT: one amber box labelled "Hotel multiplier = s(t) x r", fed by arrows from "Monthly rate r" and from "Daily guest-room shape s(t)". One arrow leaves it to the right, labelled "guest-room schedule".

No other text. No numbers other than the years and band values written above. No abbreviations or codes (no SARIMA, ISQ, CBRE, COVID, GSS, gate, MAE). No colour names written as text. No title banner, no footnote, no logos.
```

## Acceptance checklist (author, after generating)

- The seasonal-model box sits off the main path, with no arrow into "Monthly rate r".
- Year spans read exactly "2019 to 2022" (Quebec) and "2011 to 2022" (Alberta).
- The step curve is two-level (night high, day low), not a sine wave.
- No note along the bottom, no dashes used as punctuation, long edge at least 3500 px.

## Caption (already in the manuscript, `02_Framework.md`)

"Hotel occupancy model, from monthly provincial series to the half-hourly multiplier." The exact s(t)
values (1.00 at night; 0.200 weekday and 0.308 weekend in the day) stay in the text, not the image.

## Fix round 2 (2026-09-25, after checking the first Gemini image)

Problem in the first image: a dashed arrow runs OUT of "Seasonal model check" back INTO the Alberta card, and a
solid arrow runs into the check box from the Quebec lines. The check must have nothing leaving it.
Paste the full prompt above again, then add:

"Arrow rules, strict: the ONLY arrow touching the box 'Seasonal model check' is one thin DASHED arrow that starts
at the lower edge of the Alberta card and ends at the top edge of the check box, arrowhead on the check box. No
arrow leaves the check box. No solid line touches the check box. Each data card sends exactly two solid arrows,
one to '2022: observed monthly rate' and one to '2030: 2019 monthly pattern scaled to recovery level'; no line
crosses another."
