# Figure 4 -- Exclusivity Projection (Independent Heads to One-Hot Decode)

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show independent binary heads passing through a threshold-normalized argmax projection, and the Impossible-State Rate collapsing from a small raw value to zero after projection.
**Source:** `Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md`; Overview.md VALIDATION GATES table, row "Transformer (Exclusivity)"

> 🔴 **Naming rule, 2026-08-11.** The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## 🔴 What the shipped version gets wrong. Read before generating.

**1. The bottom mini-panels are EMPTY.** The shipped image draws the two panels as a pair of blank
white rectangles with one tiny stub bar and no values, because the numbers they exist to show were
filed under "overlay afterward" and no one ever overlays them. Nothing in this figure carries the
result. **The two ISR values are now inside the fenced prompt and must be drawn as text.**

**2. The one-hot decode is not one-hot.** The shipped image draws the right-hand cluster as one full
bar, one bar filled about a quarter of the way, and one empty. A partly-filled bar is precisely the
state the projection exists to eliminate, so the figure currently illustrates its own failure case.
Exactly one bar at full height; the other two flat at zero.

**3. Framing.** 28% of the image height is empty white above the artwork (217 px of 768). Crop tight.

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. The artwork must fill the frame with only a small even margin on all four sides; no large empty band above or below.

On the left, three small flat vertical bar icons in a row, each a different fill (slate-blue, teal, warm-grey), of clearly different heights, two of them rising above a thin dashed horizontal line labelled "threshold" so the raw conflict is visible. An arrow leads right into a single amber-filled box labelled "Threshold-Normalized Argmax Projection". A second arrow leads right into the one-hot output: three bars again, of which EXACTLY ONE is filled to full height and the other TWO are flat at zero (empty outlines, no partial fill of any kind). A partly-filled bar in this right-hand group is an error -- it is the exact state the projection removes.

Below the whole diagram, a small flat two-panel bar-chart pair, both panels drawn with a visible baseline: the LEFT panel is labelled "raw ISR <= 0.5%" and contains one short bar; the RIGHT panel is labelled "0% after projection" and contains no bar at all, just the baseline. Both value labels must be drawn as visible text. Neither panel may be left blank and unlabelled.

Draw these text strings, once each: "Independent Binary Heads", "three independent sigmoid probability outputs", "threshold", "Exclusivity Projection", "Threshold-Normalized Argmax Projection", "Mutually Exclusive Decode", "one-hot output", "raw ISR <= 0.5%", "0% after projection".

SCENE: Left cluster "Independent Binary Heads" (three probability bars of different heights, two above the threshold line) to the amber "Exclusivity Projection" box to the right cluster "Mutually Exclusive Decode" (three bars, exactly one at full height, two at zero). Beneath, the labelled before/after ISR mini panel pair.

FINAL CHECK: exactly three bars in the left group and three in the right group; exactly one filled bar on the right; both bottom panels carry their value text.
```

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Left cluster label: "Independent binary heads (resid / AT_WORK / AT_RETAIL), calibrated logit-adjusted sigmoid outputs"
- Projection box label: "Threshold-Normalized Argmax Projection (decode-time)"
- Right cluster label: "Mutually exclusive one-hot decode, 100% physical consistency"
- Metric name: "Impossible-State Rate (ISR): slots with more than one of AT_HOME, AT_WORK, AT_RETAIL active"
- Before/after mini-chart values: "raw ISR <= 0.5%" (left mini-panel) to "0% after projection" (right mini-panel)
- Gate line callout: "ISR <= 0.5% raw; = 0% after the decode-time projection (dr_L3-12)"

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D, no isometric or 3D treatment
- The single amber-filled element is the "Threshold-Normalized Argmax Projection" box, since it is the mechanism this figure exists to explain
- Keep "as-modelled raw" and "after projection" values visually and numerically separate -- never blend or average the two bars
