# Figure S4 — Activity-Driven End-Use Load Model Structure
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Horizontal, two stacked lanes separated by a dashed divider: a TOP lane drawn as a flat bar labelled "Baseload" carrying small flat appliance glyphs (fridge, freezer, standby), running left→right. The MAIN lane below, left→right: "Activity Sequence" box → "Crosswalk" box with a small flat grid glyph → "Co-presence Scaling" box → "SHEU Calibration" box (AMBER) → "End-Use Loads" output curves box → a flat house-outline glyph labelled "EnergyPlus". Both lanes read left→right.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Baseload slab: "Flat 24/7 baseload — never occupancy-modulated"
- Appliance labels: "Fridge  448 kWh/yr" / "Freezer  343 kWh/yr" / "Standby  ~400–430 kWh/yr"
- "Activity" input: "14-category activity sequence (48 slots per day)"
- "Crosswalk" tile: "9-end-use × 14-activity weight matrix (Tables A1–A2)"
- "Co-presence" tile — shared devices label: "Shared devices (cooking, dishwasher, washer/dryer, TV): EFF(N) = 1.0 / 1.4 / 1.7 / 1.9 / 2.0"
- "Co-presence" tile — personal devices label: "Personal devices (PC, hair-dryer, DHW): linear scaling"
- "Calibrate" tile (amber): "Per-end-use SHEU calibration scalar: f_e = SHEU_target_e / simulated_annual_e"
- Output annotation: "48/48 cell-years ≤ ±2.7% of SHEU · max +2.33% equipment · +2.63% lighting"
- House label: "Per-household Schedule:Compact → EnergyPlus v24.2"
- Tier divider note: "Baseload held fixed at calibration; only activity tier carries the f_e scalar"

## Layout notes
- Aspect ratio: wide landscape (16:9 or 3:2), reading direction left → right in both lanes
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: the "SHEU Calibration" box (the per-end-use SHEU calibration scalar — anchors the model to survey energy benchmarks)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- The baseload lane sits clearly above and visually separate from the activity-tier chain below, separated by a dashed divider; both lanes read left→right
