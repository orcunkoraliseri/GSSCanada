# Figure S2 -- One Scenario Lever per Channel
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** the reviewer-defusing pattern carried from Leg-2 -- show that each channel has exactly one, independently re-runnable 2030 sensitivity lever, and that Residential deliberately has none.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 6 box + KEY DESIGN DECISIONS SUMMARY ("One scenario lever per channel")

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract / SI figure. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. White background, sans-serif labels, restrained academic palette. Four vertical lanes side by side, one per channel, evenly spaced, each headed by a small flat channel icon and a channel-name label. Three of the four lanes (Office, Retail, Hotel) each contain a small flat horizontal three-position slider/dial icon with three labelled tick marks (low, default/central, high), each slider filled in a distinct muted colour (slate-blue for Office, teal for Retail, amber for Hotel). The fourth lane (Residential) contains NO slider icon at all -- instead a small flat "no lever" glyph (a simple horizontal line with a small flat circular dot fixed in the centre, non-adjustable, greyed out) and a short text label stating explicitly that there is no lever for this channel. No other colours, minimal, generous whitespace, crisp and legible.

SCENE: Four lanes left to right: "Residential" (grey, fixed-dot "no lever" glyph, explicit no-lever label) -- "Office" (slate-blue three-position slider) -- "Retail" (teal three-position slider) -- "Hotel" (amber three-position slider). Each slider's three tick marks are labelled with short generic position words only (low / default / high) inside the image; the actual named scenario values are added afterward as overlay text.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Residential lane label: "Residential -- no scenario lever (REPLACE injection, GSS-driven, not a code-density modulation)"
- Office lane, slider positions: "conservative" · "hybrid" · "fullyhybrid" (WFH band)
- Retail lane, slider positions: "0.90" · "0.97 (default)" · "1.05" (in-store share)
- Hotel lane, slider positions: "0.92" · "1.00" · "1.05" (SARIMA 2030 band)
- Caption line: "one lever per channel -- re-runnable sensitivity bands, the reviewer-defusing pattern"
- Explicit statement to render as overlay text under the Residential lane: "Residential has no lever."

## Layout notes
- Aspect ratio: can be narrower than the main-text figures (SI figure), landscape strip acceptable
- Style: flat 2D, no isometric or 3D treatment
- No single amber highlight convention here -- each of the three lever channels keeps its own distinct colour (slate-blue Office, teal Retail, amber Hotel) so the four lanes read as a comparison set, not a process flow
- The Residential lane's "no lever" glyph must be visually and unmistakably different from a slider (fixed centre dot, greyed out, no tick marks) -- it must not read as "a slider set to default", since the point of the figure is that no lever exists for this channel at all
