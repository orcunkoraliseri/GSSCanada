# Figure 2 — Dataset Preprocessing and Harmonization Flow
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Horizontal lane left→right: four small stacked database-cylinder input glyphs labelled "GSS 2005", "GSS 2010", "GSS 2015", "GSS 2022" → a merge/funnel node labelled "Closure Filter" → "Harmonize" box → "Tile Episodes" box → "Downsample" box → "Clock Shift" box with a tiny flat circular-arrow glyph (AMBER) → "30-min Diary" output box. Below the main lane, a separate small database-cylinder glyph labelled "Census PUMF" with a thin dashed arrow pointing right toward a small box labelled "Census Linkage" (does NOT join the main preprocessing lane). Left→right.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Drum 1: "GSS 2005  n = 19,221"
- Drum 2: "GSS 2010  n = 15,114"
- Drum 3: "GSS 2015  n = 17,390"
- Drum 4: "GSS 2022  n = 12,336"
- Funnel label: "1,440-min closure filter → 64,061 valid diaries"
- "Harmonize" tile annotation: "Cross-cycle schema harmonization → 14-category activity scheme · 0.00% unmapped"
- "Tile" tile annotation: "Episode → HETUS 144 × 10-min tiling"
- "Downsample" tile annotation: "Presence-priority majority-vote → 48 × 30-min slots · 3-way tie rate 0.82%"
- "Shift" tile annotation: "04:00 → 00:00 circular shift · diary origin → simulation clock · np.roll(..., 4)"
- Output slab annotation: "DDAY_STRATA: Weekday / Saturday / Sunday"
- Census lane annotation: "Census PUMF 2021 · 286,537 individuals · enters at Step 5 only"
- Dashed arrow label: "→ Step 5 Linkage (bypasses diary preprocessing)"

## Layout notes
- Aspect ratio: wide landscape (16:9 or 3:2), reading direction left → right
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: "Clock Shift" box (the 04:00→00:00 clock rotation — diary-origin convention)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- Two lanes: main diary-preprocessing lane (upper) and Census parallel lane (lower, dashed arrow); the four cycle input glyphs feed through the funnel node; the Census PUMF glyph is a separate parallel path below that does not join the main lane
