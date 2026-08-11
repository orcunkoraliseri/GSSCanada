# Figure 1 -- End-to-End 4-Split Pipeline (Steps 1-9)
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the nine-step 4-split occupancy-to-BEM pipeline in one image, with channel provenance (Leg-2 inherited vs Leg-3 added) colour-coded and the hotel side-track shown bypassing the Transformer.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (box diagram, STEP 1 through STEP 9)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. Nine evenly spaced flat rounded-rectangle boxes connected by thin straight connector lines with small arrowheads, numbered STEP 1 through STEP 9 in small type at the top-left corner of each box. Restrained academic palette on white: use TWO distinct muted fills across the nine boxes -- a desaturated slate-blue/teal fill for elements inherited from Leg 2, and a warm amber/gold fill for elements added in Leg 3 -- plus warm-grey neutrals for shared/untouched elements. No decoration, no photorealism, no clutter, generous whitespace.

SCENE: Horizontal left-to-right chain of nine boxes: (1) "Data Collection" -- warm-grey, small database-cylinder icon -- (2) "Harmonization" -- warm-grey -- (3) "Merge & Tiling" -- half slate-blue/teal (residential + office) half amber (retail addition), small link/chain icon -- (4) "3-Head Transformer" -- slate-blue/teal for two heads, amber for the third head, small neural-network node-cluster icon -- (5) "Archetype Linkage" -- slate-blue/teal (residential, office) plus amber (retail) -- (6) "Forecast 2030" -- slate-blue/teal, small calendar-grid icon -- (7) "BEM/UBEM Integration" -- mixed slate-blue/teal and amber, small house-outline icon -- (8) "BEM Simulation" -- warm-grey, small iso-building icon -- (9) "End-Use Loads" -- warm-grey, small bar-chart icon. Below box 2, a separate amber-outlined dashed lane begins labelled "Hotel Side-Track", runs parallel and below the main chain, passes UNDER and visibly AROUND box 4 "3-Head Transformer" with a small "bypass" arrow curving around that box only, then rejoins the main chain to merge back in at box 5. Add a small two-swatch legend in the bottom corner: slate-blue/teal swatch labelled "Leg-2 inherited", amber swatch labelled "Leg-3 added". Flat, horizontal, no other colours.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- STEP 1: "Data Collection & Column Selection" -- GSS columns + hotel source (ISQ QC / CBRE AB monthly series)
- STEP 2: "Data Harmonization" -- crosswalk + OR-rule; AT_RETAIL derivation; hotel series harmonization
- STEP 3: "Merge & Tiling" -- one tiler list entry appends AT_RETAIL; retail kept in a separate CSV (byte-equality not verified, Table 6)

  🔴 CORRECTION 2026-08-06 night: this line originally ended "residential + office paths bit-identical". That is the pipeline overview's prose statement of design intent, and `Table_06_leg2_leg3_delta.md` grades the same claim `⚠ check source` because no file or column comparison of the tiler's output was ever run. Only Step 7 carries an affirmative evidence verdict in Table 6, and only for the base prototype geometry. Enforced by `f5_figure_check.py` arm C7.
- STEP 4: "Three-GSS-Head Transformer" -- heads = resid / AT_WORK / AT_RETAIL; hotel NOT in model
- STEP 5: "Archetype Linkage" -- residential Census linkage (Leg 1); office NOCxNAICS (Leg 2); retail population-level fraction; hotel province-level multiplier (Leg 3)
- STEP 6: "Forecast 2030 + Hotel Side-Track" -- GSS channels via drift matrix; hotel SARIMA(1,1,1)(1,1,1,12) + COVID indicator, bypasses the Transformer entirely
- STEP 7: "BEM/UBEM Integration" -- Tag-2 dispatch: apartment REPLACE; office/retail/guest-room MODULATE; amenity + service/MEP untouched NECB
- STEP 8: "BEM Simulation" -- 56/56 cells; 2-city sweep CAN_MTL 6A + CAN_CLG 7A
- STEP 9: "Activity-Driven End-Use Loads" -- equipment + lighting; calibrated vs NRCan SCIEU
- Legend: slate-blue/teal = "Leg-2 inherited (Residential AT_HOME, Office AT_WORK)"; amber = "Leg-3 added (Retail AT_RETAIL, Hotel non-GSS)"
- Bypass callout on the hotel lane: "Hotel side-track bypasses the Transformer entirely -- SARIMA, not the 3-head model"

## Layout notes
- Aspect ratio: wide landscape (16:9 or wider), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- Two-colour coding is the organizing device of this figure: slate-blue/teal for the two Leg-2 channels, amber/gold for the two Leg-3 additions -- apply consistently to sub-elements inside boxes 3, 4, 5 and 7, since those are the boxes where the four channels are actually processed
- The hotel side-track lane must visibly route around box 4 only, not around any other box, and must rejoin the main chain at box 5
- Nine boxes evenly spaced; small STEP N numerals in the top-left corner of each box function as the section reference back to the pipeline overview document
