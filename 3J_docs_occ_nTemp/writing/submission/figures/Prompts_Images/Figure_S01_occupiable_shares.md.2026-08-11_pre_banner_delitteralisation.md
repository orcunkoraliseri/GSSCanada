# Figure S1 -- Measured Occupiable-Area Shares per Tower
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the corrected (Defaut 7, 2026-07-31) occupiable-area share per channel for both tower prototypes, with a footnote flagging the superseded figures it replaces.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` header note ("Surfaces CORRIGEES 2026-07-31 (Defaut 7)"); `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md` section Defaut 7

> 🔴 **Naming rule, 2026-08-11.** The words `Leg-1`, `Leg-2`, `Leg-3`, `Leg 1`, `Leg 2`, `Leg 3` must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## Prompt (paste into the image LLM)

```
Clean flat 2D vector stacked-bar chart in the style of a polished journal graphical abstract / SI figure. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. White background, sans-serif labels, restrained academic palette (desaturated slate-blue, teal, amber, warm-grey -- four distinct muted fills, one per channel, consistent across both bars). Two vertical stacked bars side by side, one labelled "SuperTall" and one labelled "Tall", each bar divided into four stacked segments proportional to share: office (slate-blue), hotel (teal), residential (amber), retail (warm-grey), ordered largest to smallest top to bottom within each bar. A thin separate horizontal band beneath both bars, shaded a lighter neutral grey and clearly set apart from the occupiable stack, represents service/MEP as a share of GROSS floor area (not occupiable), labelled distinctly so it is not read as a fifth occupiable-share segment. A small numeric total sits above each bar. A small asterisk-footnote line sits at the very bottom of the image in small type. No decoration, generous whitespace, crisp and legible.

SCENE: Two stacked bars "SuperTall" and "Tall" with four proportional segments each (office, hotel, residential, retail) in the four palette colours, totals labelled above each bar, a separate lighter service/MEP gross-area band beneath both bars, and a small footnote line at the bottom of the figure.
```

## 🔴 CORRECTION 2026-08-06 night - the annotation block below has TWO errors, do not copy it as written

Found by cross-footing the numbers against `writing/tables/SI/Appendix_C_corrections.md` (line ~29),
which is the authoritative source. Both errors are in this prompt file, not in the figure script.

1. **A fifth segment is missing.** The four shares listed below sum to **97.59 %** (SuperTall) and
   **97.49 %** (Tall), not 100 %. The source states a fifth occupiable share,
   **residential-common 2.40 % / 2.50 %**, which closes both bars to 99.99 %.
2. **The bar total is the wrong denominator.** The totals below (135,857.6 / 72,623.1) are the
   **GROSS** areas, while every listed share is a share of the **OCCUPIABLE** area
   (**107,816.0 / 57,075.4 m2**). A reader who multiplies gets a wrong number for every channel.
   *Proof that the shares cannot be of gross:* office at 44.33 % of gross is 60,225.7 m2, and the
   shares plus service/MEP would then exceed the gross total. Independently:
   occupiable / gross = **79.36 %** and **78.59 %**, which plus service/MEP **20.6 %** and **21.4 %**
   gives **99.96 %** and **99.99 %** - so occupiable + service/MEP = gross, and the two denominators
   are confirmed distinct.

**The figure must label each bar with the occupiable area as the quantity its segments divide.**

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Bar 1 "SuperTall", total: "135,857.6 m2" -- office 44.33% · hotel 26.37% · residential 22.50% · retail 4.39% *(see correction above: this total is GROSS; the shares are of OCCUPIABLE 107,816.0 m2, and residential-common 2.40% is missing)*
- Bar 2 "Tall", total: "72,623.1 m2" -- office 44.65% · hotel 24.91% · residential 22.40% · retail 5.53% *(see correction above: this total is GROSS; the shares are of OCCUPIABLE 57,075.4 m2, and residential-common 2.50% is missing)*
- Service/MEP band: "20.6% of gross (SuperTall) / 21.4% of gross (Tall) -- share of GROSS floor area, not occupiable"
- Legend: slate-blue "Office" · teal "Hotel" · amber "Residential" · warm-grey "Retail"
- Footnote (verbatim, must appear at the bottom of the figure): "Corrected 2026-07-31 (Defaut 7) parse, from Sigma FloorArea x Multiplier on IsPartOfTotalArea = 1, reproducing EnergyPlus Total Building Area exactly. Superseded figures (40,846 m2 SuperTall / 26,750 m2 Tall) were 2.7 to 3.3x too small and shifted every EUI proportionally."
- Caption line: "measured occupiable-area shares per tower prototype"

## Layout notes
- Aspect ratio: can be narrower than the main-text figures (SI figure), portrait or square acceptable, but keep the two bars side by side and readable
- Style: flat 2D stacked bar chart, no isometric or 3D treatment
- No single amber highlight convention here -- all four channel colours are equally weighted since this is a compositional (share) figure, not a process/flow figure
- The service/MEP band MUST be visually separated (different shading, distinct label, clear gap) from the four occupiable-share segments, since it is a share of a different denominator (gross floor area, not occupiable area) and must never be stacked into the same 100% as the other four
- The footnote text must be reproduced verbatim as overlay text, not paraphrased, since it is the correction record for a 2.7 to 3.3x error that shifted every downstream EUI number
