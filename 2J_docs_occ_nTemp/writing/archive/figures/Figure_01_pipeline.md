# Figure 1 — End-to-End Pipeline Overview
**Target:** web image-generation LLM · **Style family:** axonometric (Figure 1 only)

## Prompt (paste into the image LLM)

```
Polished axonometric (isometric) graphical-abstract illustration in a clean professional scientific-journal style. Light, subtle 3D depth ONLY — soft isometric boxes, simple iso-buildings, and a smooth left-to-right connecting pipeline — NOT a heavy photorealistic 3D render: no dramatic lighting, no glow, no busy machinery, no clutter. Horizontal left-to-right reading order, landscape composition, light near-white background. Muted professional academic palette: desaturated slate-blue and teal with warm-grey neutrals, plus a SINGLE amber-highlighted element. Use simple flat-shaded iso icons (stacked data tables/cylinders for inputs, a small neural-network node cluster for the generator, iso houses for simulation, a small bar-chart/curve for outputs). Render ONLY short 2-3 word labels beside each stage — NO section numbers, NO long phrases, NO full numbers or percentages (those are added afterward as overlay text). Uncluttered, generous whitespace, "clean and logical" not "maximally detailed".

SCENE: A single left→right axonometric pipeline: on the far left, two iso stacked data-table/cylinder glyphs labelled "GSS Diaries" and "Census PUMF" feeding into → "Harmonize" iso box → "Generator" iso box (AMBER, with a small neural-network node cluster glyph) → "Census Linkage" iso box → "Forecast" iso box → "BEM Schedules" iso box → "Simulate" iso box (with small iso house glyphs beside it) → "End-Use Loads" iso box → "Outputs" iso box (with a small bar-chart + curve glyph). Thin iso connector arrows flow left to right between each stage. Landscape (16:9 or wider). Generous whitespace, minimal clutter.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Stage 1 label: "GSS Time-Use (4 cycles: 2005 / 2010 / 2015 / 2022) + Census PUMF 2021"
- Stage 2 label: "Steps 2–3: Harmonization & 30-min diary" · section code: §2
- Stage 2 annotation: "64,061 diaries · 14-category scheme · 48 × 30-min slots"
- Stage 3 label: "Step 4: Generative augmentation (calibrated J3)" · section code: §3.2
- Stage 3 annotation: "~192,183 diary-days · gate-selected Transformer · sole 4/4-gate model"
- Stage 4 label: "Step 5: Census–GSS linkage" · section code: §3.3
- Stage 4 annotation: "144,507 households"
- Stage 5 label: "Step 6: Longitudinal forecast to 2030" · section code: §3.4
- Stage 5 annotation: "True-Future-Test · progressive fine-tuning"
- Stage 6 label: "Step 7: BEM schedule conversion" · section code: §3.5
- Stage 6 annotation: "4 × Schedule:Compact channels"
- Stage 7 label: "Step 8: Paired EnergyPlus simulation" · section code: §3.6 / §4
- Stage 7 annotation: "6,000 runs · 4 archetypes × 6 cities × 5 years"
- Stage 8 label: "Step 9: Activity-resolved end-use loads" · section code: §3.6
- Stage 8 annotation: "48/48 cells ≤ ±2.7% of SHEU"
- Stage 9 label: "Outputs: Load-shape metrics + EUI"
- Small section label under each tile: §2, §3.2, §3.3, §3.4, §3.5, §3.5, §4, §3.6

## Layout notes
- Aspect ratio: wide landscape (16:9 or wider), reading direction left → right
- Style: axonometric (isometric) — soft iso boxes and iso icons; minimal 3D depth only, no heavy photorealism or clutter
- Amber-highlight element: "Generator" iso box (calibrated J3 — the key methodological contribution)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- Nine stages evenly spaced horizontally; iso house glyphs sit beside the Simulate stage; generous whitespace throughout
