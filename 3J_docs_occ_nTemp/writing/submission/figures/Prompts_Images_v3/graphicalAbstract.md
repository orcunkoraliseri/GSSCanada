# Graphical abstract -- Four Populations, One Tower

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** carry the paper's headline claim in one image - four independent occupancy channels enter
one stacked mixed-use tower, three of them peak within half an hour of midday while hotel peaks about
seven hours later, and the whole-building peak coincides with none of them.
**Source:** Chapter 5 §5.1 and §5.3 (peak hours, coincidence factor); Chapter 3 §3.2 and §3.5
(architecture and dispatch); Table 2 (the four channels and their sources).
**Written:** 2026-08-09. There was no prompt file for the graphical abstract before this one.

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
Clean flat 2D vector graphical abstract for an academic building-energy paper. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no photorealism. Horizontal left-to-right reading order, wide landscape composition, white background, sans-serif labels, generous whitespace. Restrained academic palette on white: four distinct muted channel colours used consistently everywhere in the image -- desaturated amber/gold for residential, desaturated slate-blue for office, warm-grey for retail, desaturated teal for hotel -- plus thin neutral grey for structure and connectors. No decoration, no clutter.

SCENE, in three panels reading left to right, separated by generous white space rather than by boxes or borders:

LEFT PANEL, "Four populations": four small flat icons stacked vertically, each in its own channel colour with a short label to its right -- an amber house-outline labelled "Households", a slate-blue briefcase labelled "Workforce", a warm-grey shopping-bag labelled "Customers", a teal bed labelled "Guests". A thin bracket gathers all four and one arrow leaves it pointing right. Beneath the bracket, small type: "one jointly-trained model, three survey heads + one side-track".

CENTRE PANEL, "One tower": a single tall flat rectangular tower elevation, drawn as one outline divided into horizontal bands of the four channel colours -- teal band near the top, amber bands in the upper middle, slate-blue bands in the lower middle, one thin warm-grey band at ground level -- so the building visibly stacks all four uses inside one envelope. Four thin arrows enter the tower from the left panel, one per colour, each landing on its own band. Small type beneath the tower: "one envelope, one plant".

RIGHT PANEL, headed "Peak hours": a flat 24-hour line chart with a light horizontal baseline and hour ticks at 0, 6, 12, 18, 24. Five thin curves, each with one clearly marked peak, and the peaks must sit at these hours on the axis, not anywhere else:
  amber residential -- peak at 12
  slate-blue office -- peak at 12 (essentially the same hour as residential; the two peaks nearly touch)
  warm-grey retail -- peak at 12 (also essentially the same hour; all three of these peak in one tight cluster around midday, only minutes apart, and must be drawn overlapping)
  teal hotel -- peak at 19, far to the right of the cluster, in the evening
  neutral dark grey whole building, drawn slightly heavier -- peak at 15, in the empty gap between the midday cluster and the hotel peak, coinciding with none of the four
The three midday curves must visibly form ONE cluster. Do not spread them across the morning and afternoon; do not draw residential peaking before office. A small flat callout card beside the chart reads "coincidence factor < 1".

Include a small four-swatch legend in the bottom corner: amber "Residential", slate-blue "Office", warm-grey "Retail", teal "Hotel". Flat, horizontal, crisp, legible at small size.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)

Image models mis-set digits. Add every number below as text on top of the finished image, never inside
the prompt.

- Hotel peak hour: **18.91 h**; the other three cluster near **12 h** (circular mean, §5.3, Figure 10).
- Whole-building coincidence factor: **below 1 in all four building-city cells, median 0.941** (§5.3).
- Campaign: **56 cells** = four channels x two prototypes (Tall, SuperTall) x two cities (Montreal 6A,
  Calgary 7A) x fourteen scenarios, forecast **2005-2030**.
- Channel sources, if a source line is wanted: residential / office / retail from four **GSS Time-Use**
  cycles; hotel from **provincial tourism statistics** (ISQ for Quebec, CBRE / Travel Alberta for
  Alberta), which never enters the Transformer.

## Rules this figure must satisfy

- The centre tower must read as **one building**, not four buildings side by side. The whole point of
  the paper is that the four uses share one envelope; a district of four blocks is the thing this study
  is distinguished FROM (see Table 1, the mixed-use-single-building axis).
- The hotel arrow must not pass through anything drawn as the Transformer. If any model element is
  shown in the left panel, the hotel channel bypasses it.
- Do not write "four heads" anywhere. See `README.md`, rule 1.
- 🔴 **Corrected 2026-08-11, and it reverses the previous instruction.** The earlier version of this
  line asked for the three midday peaks to be "visibly separated from each other", and the panel was
  headed "Four different hours". Both were wrong against the paper's own measurement. §5.3 and
  Figure 10 give office, residential and retail peaking between **11.90 h and 12.37 h** -- a spread of
  **28 minutes**, which at the width of a graphical-abstract chart is one line, not three -- and hotel
  at **18.91 h**, about seven hours later. The whole-building peak is **14.95 h**.
  The shipped image, following the old wording, drew residential near 09:00, office near 12:00, retail
  near 13:00 and hotel near 17:00: four evenly spread peaks, in an order that puts residential two
  hours *before* office when it in fact peaks fractionally *after* it. That is the paper's headline
  claim drawn as something the paper's own results contradict. The finding is "three coincide and one
  does not", and the image must show exactly that.
- The panel heading must not be "Four different hours". The three midday channels differ by minutes;
  a heading that promises four distinct hours pushes the generator into spreading them out, which is
  how the defect above was introduced in the first place.
