# Figure 3 -- Three-Head Transformer + Non-GSS Hotel Side-Track

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** shared encoder with three GSS decoder heads, explicitly labelled "3 GSS heads + 1 non-GSS side-track" -- the existing PNG's "4 heads" shorthand is not authoritative and must not be reproduced.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 4 box + dr_L3-11/dr_L3-12/dr_L3-13 design-freeze notes

> 🔴 **Naming rule, 2026-08-11.** The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. A single flat rounded-rectangle "Shared Encoder" box on the left in desaturated slate-blue, forking rightward into exactly THREE stacked horizontal decoder-head lanes, each a small flat box: "Resid Head", "AT_WORK Head", "AT_RETAIL Head", all three in the same slate-blue/teal family (they are GSS heads, same palette). Physically separate from this fork, drawn BELOW and set apart with a visible gap and a thin dashed boundary box around it, is a single amber-filled box labelled "Hotel Side-Track (non-GSS)" with a small calendar/SARIMA-curve icon, NOT connected to the Shared Encoder by any arrow -- it receives its own separate input arrow from outside the diagram. A large caption banner spans the top of the whole figure reading "3 GSS heads + 1 non-GSS side-track". No box or label anywhere reads "4 heads". Flat, minimal, generous whitespace, restrained academic palette.

SCENE: Left: "Diary Input" box feeds into "Shared Encoder" box. Encoder forks right into three stacked lanes (top to bottom): "Resid Head" to "Resid Output"; "AT_WORK Head" to "AT_WORK Output"; "AT_RETAIL Head" to "AT_RETAIL Output" -- each head-to-output pair connected by a thin arrow, all three lanes converging visually at a shared "Exclusivity Projection" box on the right. Separately, below and outside the bracket that groups the three GSS lanes, the dashed amber "Hotel Side-Track (non-GSS)" box sits alone with its own input arrow from a small "Tourism Stats" icon and its own output arrow, never touching the Shared Encoder or the three-lane bracket. Top banner text "3 GSS heads + 1 non-GSS side-track".
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Top banner (verbatim, must appear): "3 GSS heads + 1 non-GSS side-track"
- Encoder label: "Shared Transformer encoder"
- Head labels: "Head 1: resid" · "Head 2: AT_WORK" · "Head 3: AT_RETAIL"
- Loss weights callout: "loss weights a_resid : a_work : a_retail = 1.0 : 0.5 : 0.3"
- Balancing callout: "fixed-weight scalarization + PCGrad (SLAW/UW dropped, unstable on the ~2% AT_RETAIL head)"
- Rare-class callout on the AT_RETAIL head only: "pos_weight = 49; inference-time logit shift = -ln(49) is approximately 3.89"
- Training schedule callout: "warmup 5 epochs (heads only) then joint fine-tuning 15 epochs with PCGrad"
- Decode callout (on the Exclusivity Projection box): "decode temperature T = 0.7 + 2-slot minimum-dwell constraint"
- Threshold callout: "decode thresholds 0.50 / 0.40 / 0.15 (resid / AT_WORK / AT_RETAIL)"
- Hotel side-track callout: "SARIMA(1,1,1)(1,1,1,12) per province; population-aggregate monthly series, no GSS respondents behind it -- bypasses the Transformer entirely"
- Explicit non-label: do NOT render or overlay "4 heads" anywhere on this figure

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- The single amber-filled element is the Hotel Side-Track box; all three GSS heads share one slate-blue/teal family so the visual grouping reads as "3 + 1", never "4 equal heads"
- The dashed boundary and physical gap around the Hotel Side-Track box, plus the absence of any connecting arrow from the Shared Encoder, are load-bearing -- they are what makes "3 GSS heads + 1 non-GSS side-track" visually true, not just captioned
- Top banner caption is mandatory and must not be replaced with any "4 heads" phrasing
