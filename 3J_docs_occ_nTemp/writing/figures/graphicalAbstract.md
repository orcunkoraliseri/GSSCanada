# Graphical abstract -- Four Populations, One Tower

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** carry the paper's headline claim in one image - four independent occupancy channels enter
one stacked mixed-use tower, they peak at four different hours, and the whole-building peak coincides
with none of them.
**Source:** Chapter 5 §5.1 and §5.3 (peak hours, coincidence factor); Chapter 3 §3.2 and §3.5
(architecture and dispatch); Table 2 (the four channels and their sources).
**Written:** 2026-08-09. There was no prompt file for the graphical abstract before this one.

## Prompt (paste into the image LLM)

```
Clean flat 2D vector graphical abstract for an academic building-energy paper. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no photorealism. Horizontal left-to-right reading order, wide landscape composition, white background, sans-serif labels, generous whitespace. Restrained academic palette on white: four distinct muted channel colours used consistently everywhere in the image -- desaturated amber/gold for residential, desaturated slate-blue for office, warm-grey for retail, desaturated teal for hotel -- plus thin neutral grey for structure and connectors. No decoration, no clutter.

SCENE, in three panels reading left to right, separated by generous white space rather than by boxes or borders:

LEFT PANEL, "Four populations": four small flat icons stacked vertically, each in its own channel colour with a short label to its right -- an amber house-outline labelled "Households", a slate-blue briefcase labelled "Workforce", a warm-grey shopping-bag labelled "Customers", a teal bed labelled "Guests". A thin bracket gathers all four and one arrow leaves it pointing right. Beneath the bracket, small type: "one jointly-trained model, three survey heads + one side-track".

CENTRE PANEL, "One tower": a single tall flat rectangular tower elevation, drawn as one outline divided into horizontal bands of the four channel colours -- teal band near the top, amber bands in the upper middle, slate-blue bands in the lower middle, one thin warm-grey band at ground level -- so the building visibly stacks all four uses inside one envelope. Four thin arrows enter the tower from the left panel, one per colour, each landing on its own band. Small type beneath the tower: "one envelope, one plant".

RIGHT PANEL, "Four different hours": a flat 24-hour line chart with a light horizontal baseline and hour ticks. Four thin curves in the four channel colours, each with one clearly marked peak: three of them peak close together near the middle of the day, and the teal curve peaks distinctly later, well to the right of the other three, near the evening. A fifth curve in thin neutral dark grey, drawn slightly heavier, represents the whole building and peaks at a point that visibly coincides with none of the four. A small flat callout card beside the chart reads "coincidence factor < 1".

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
- The three midday peaks must be visibly separated from each other as well as from hotel; they are
  close, not identical.
