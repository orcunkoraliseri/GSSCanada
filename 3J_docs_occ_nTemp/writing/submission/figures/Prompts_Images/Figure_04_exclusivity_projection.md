# Figure 4 -- Exclusivity Projection (Independent Heads to One-Hot Decode)
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** show independent binary heads passing through a threshold-normalized argmax projection, and the Impossible-State Rate collapsing from a small raw value to zero after projection.
**Source:** `Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md`; Overview.md VALIDATION GATES table, row "Transformer (Exclusivity)"

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. On the left, three small flat vertical bar icons in a row, each a different fill (slate-blue, teal, warm-grey), labelled as three independent sigmoid probability outputs, with a few bars shown overlapping/co-occurring above a thin dashed "threshold" line to suggest raw conflicts. An arrow labelled "Threshold-Normalized Argmax Projection" (single amber-filled box) leads right into a small flat one-hot output icon: three bars again, but now perfectly mutually exclusive with exactly one bar filled and the other two empty, no overlap. Below the whole diagram, a small flat two-panel bar-chart pair: left mini-panel labelled "raw" with a very short bar, right mini-panel labelled "after projection" with a bar at zero height. Minimal, no clutter, generous whitespace.

SCENE: Left cluster "Independent Binary Heads" (three overlapping probability bars, some conflicting) to amber "Exclusivity Projection" box to right cluster "Mutually Exclusive Decode" (three bars, exactly one active). Beneath, small before/after ISR mini bar-chart pair.
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
