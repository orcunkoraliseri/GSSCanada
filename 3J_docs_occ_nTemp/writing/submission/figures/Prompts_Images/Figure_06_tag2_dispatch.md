# Figure 6 -- Tag-2 Dispatch Inside One Tower

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show the Tag-2 exact-match routing that decides REPLACE vs MODULATE vs untouched-baseline vs fallback for every Space in the tower, with the two-channel stage wiring-bug gate called out.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 7 box ("Tag-2 exact-match dispatch" + "HARD WIRING GATE")

> 🔴 **Naming rule, 2026-08-11.** The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## 🔴 What the shipped version gets wrong. Read before generating.

**The Hard Wiring Gate card is empty.** The shipped image draws the card, the warning triangle, the
checkmark and the cross correctly -- and then puts two blank grey pill shapes where the two field
names belong. The two field names ARE the figure: the whole point is that
`Number_of_People_Schedule_Name` and `Schedule_Name` look alike, and that writing the wrong one runs
without erroring. A card with a tick beside one blank box and a cross beside another blank box tells
a reader nothing.

The cause is this file's own convention: the field names were filed under "overlay afterward", the
generator never saw them, and nobody overlays anything afterward. **They are now inside the fenced
prompt, to be drawn as literal text.** The same correction applies wherever a card, panel or axis in
these prompts exists in order to carry a specific string.

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. A single flat rounded diamond decision box on the left labelled "Tag 2 Match" branches into four flat horizontal lanes on the right, each ending in a small rounded-rectangle outcome box: lane 1 "Apartment tags" to amber outcome box "REPLACE"; lane 2 "Office / Retail / Guest-Room tags" to slate-blue/teal outcome box "MODULATE"; lane 3 "Amenity + Service/MEP tags" to warm-grey outcome box "NECB Baseline (untouched)"; lane 4 "Missing / unrecognized tag" to warm-grey dashed outcome box "NECB Fallback".

Below the whole diagram, a distinct flat callout card with a warning-triangle icon and a thin red-brown outline (the only non-palette accent, used only for this one gate card), titled "Hard Wiring Gate". The card contains exactly two stacked rows, and EACH ROW MUST CONTAIN ITS TEXT, in monospace, drawn legibly:
  row 1, marked with a small checkmark: Number_of_People_Schedule_Name
  row 2, marked with a small cross:     Schedule_Name
Neither row may be drawn as an empty box, a blank pill or a placeholder bar. If the two field names are not readable in the finished image, the figure has failed.

No other colours, minimal, generous whitespace.

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
- Gate card note: "the two-channel stage bug that passed every input-side check and was only caught output-side; this study runs a mandatory scenario-differentiation probe because of it"

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D flowchart, no isometric or 3D treatment
- The single amber-filled element is the "REPLACE" outcome box; the wiring-gate callout card uses its own restrained red-brown outline accent, separate from amber, since it functions as a warning rather than a highlighted pipeline stage
- The wiring-gate callout must show a field-name comparison (correct field vs the wrong field it is not), not just a warning icon, since the whole point is that the two field names look similar and the wrong one still runs without erroring
