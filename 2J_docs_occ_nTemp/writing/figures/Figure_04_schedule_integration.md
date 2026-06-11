# Figure 4 — Occupancy-to-EnergyPlus Schedule Integration
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Horizontal left→right: "Predicted Occupancy" input box → "Clock Shift" box with a tiny flat circular-arrow glyph (AMBER — the bug-fix) → "Activity MET Map" box → a fork into 4 stacked horizontal channel lanes ("Occupancy", "Metabolic", "Equipment", "Lighting") → the 4 lanes converge into a flat house-outline glyph labelled "Schedule Compact" → "EnergyPlus" box at right. Left→right.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Input slabs: "Predicted 30-min AT_HOME fraction" / "14-category activity sequence (48 slots)"
- "Shift" tile: "Clock alignment: 04:00 → 00:00 circular shift · np.roll(..., 4) · bug-fix (Step-8 v2 corrected campaign)"
- "MET Map" tile: "Activity → MET · ASHRAE 55 / ISO 7730 / 2024 Compendium"
- "Occupancy" channel annotation: "AT_HOME fraction → occupancy schedule"
- "Metabolic" channel annotation: "MET → metabolic rate schedule"
- "Equipment" channel annotation: "Activity crosswalk + co-presence scaling → equipment load"
- "Lighting" channel annotation: "Binary occupied-and-awake × SHEU scale → lighting schedule"
- House annotation: "Per-household Schedule:Compact IDF block → EnergyPlus v24.2"
- Day-completion note: "Donor-draw day-completion preserves calibrated weekend marginal"

## Layout notes
- Aspect ratio: wide landscape (16:9 or 3:2), reading direction left → right
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: "Clock Shift" box with flat circular-arrow glyph (the 04:00→00:00 clock-rotation bug-fix — the single most important correctness step)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- Four parallel output channel lanes fan out from the MET mapping box; all four converge into the terminal flat house-outline glyph
