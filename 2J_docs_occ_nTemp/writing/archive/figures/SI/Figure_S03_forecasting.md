# Figure S3 — Progressive Fine-Tuning and True-Future-Test Protocol
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: A horizontal timeline rail with five flat node markers left→right ("2005", "2010", "2015", "2022", "2030 Forecast"); solid arrows labelled "Fine-tune" connect node to node along the rail; dashed arrows labelled "Future Test" drop from each node to small holdout boxes below; small square "Drift" markers sit at each transition; the "2030 Forecast" node is larger with a small scenario-burst glyph (AMBER). Horizontal.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Pillar 1: "2005"
- Pillar 2: "2010"
- Pillar 3: "2015"
- Pillar 4: "2022"
- Pillar 5: "2030" (amber)
- Recency weight labels at each pillar: 0.10 / 0.20 / 0.30 / 0.40 (at pillars 1–4)
- Solid arrows: "Fine-tune (weight inheritance)"
- Dashed arrows: "True-Future-Test on next unseen cycle"
- Holdout tile annotation: "Holdout"
- Drift cube annotation: "DRIFT_MATRIX"
- 2030 burst annotation: "StatCan M1 scenario injection · 37,008 diary-rows · AGEGRP resampling · POWST/WFH shift"
- Validation callout: "WD JS = 0.0630 PASS · weekend ceiling 0.16 data-intrinsic"

## Layout notes
- Aspect ratio: wide landscape (16:9 or 2:1), reading direction left → right along the timeline rail
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: the "2030 Forecast" node with scenario-injection burst glyph (the forward-forecast terminus — the study's unique horizon)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- Five nodes evenly spaced along the rail; the 2030 node is larger to signal its special forward-forecast status; dashed holdout arrows drop below the rail to visually distinguish them from the solid fine-tuning arrows
