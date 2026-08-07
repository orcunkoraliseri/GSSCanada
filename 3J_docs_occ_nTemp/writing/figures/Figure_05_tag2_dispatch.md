# Figure 5 -- Tag-2 Dispatch Inside One Tower
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the Tag-2 exact-match routing that decides REPLACE vs MODULATE vs untouched-baseline vs fallback for every Space in the tower, with the Leg-2 wiring-bug gate called out.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 7 box ("Tag-2 exact-match dispatch" + "HARD WIRING GATE")

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. A single flat rounded diamond decision box on the left labelled "Tag 2 Match" branches into four flat horizontal lanes on the right, each ending in a small rounded-rectangle outcome box: lane 1 "Apartment tags" to amber outcome box "REPLACE"; lane 2 "Office / Retail / Guest-Room tags" to slate-blue/teal outcome box "MODULATE"; lane 3 "Amenity + Service/MEP tags" to warm-grey outcome box "NECB Baseline (untouched)"; lane 4 "Missing / unrecognized tag" to warm-grey dashed outcome box "NECB Fallback". Below the whole diagram, a distinct flat callout card with a warning-triangle icon and a thin red-brown outline (the only non-palette accent, used only for this one gate card) labelled "Hard Wiring Gate", containing two small stacked text fields shown as a right-field-wrong-field comparison: one field marked with a small checkmark, one field marked with a small cross. No other colours, minimal, generous whitespace.

SCENE: "Tag 2 Match" diamond forks into four lanes as above, each terminating in its outcome box. Below, the separate "Hard Wiring Gate" callout card sits under the whole flowchart, visually connected by a thin line only to the "MODULATE" outcome box (since the gate applies to modulated schedules).
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Diamond label: "Tag 2 exact-match routing key (per-Space, PNNL prototypes leave Space Type blank)"
- Lane 1: "apartment tags" to "REPLACE -- Number_of_People = HHSIZE"
- Lane 2: "office / retail / guest-room tags" to "MODULATE -- NECB baseline x channel fraction(t)"
- Lane 3: "amenity + service/MEP tags" to "untouched NECB baseline (measured 20.6% SuperTall / 21.4% Tall of gross)"
- Lane 4: "missing channel" to "NECB fallback (additive-safe)"
- Gate card title: "HARD WIRING GATE"
- Gate card correct field (checkmark): "Number_of_People_Schedule_Name"
- Gate card wrong field (cross): "Schedule_Name"
- Gate card note: "the Leg-2 bug that passed every input-side check and was only caught output-side; Leg-3 runs a mandatory scenario-differentiation probe because of it"

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- The single amber-filled element is the "REPLACE" outcome box; the wiring-gate callout card uses its own restrained red-brown outline accent, separate from amber, since it functions as a warning rather than a highlighted pipeline stage
- The wiring-gate callout must show a field-name comparison (correct field vs the wrong field it is not), not just a warning icon, since the whole point is that the two field names look similar and the wrong one still runs without erroring
