# Figure S1 — Gated Generative Architecture Search
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Horizontal narrowing left→right: on the left, a tall stack of small flat boxes labelled with short model-family names ("Markov", "AR", "VAE", "GAN", "Cross Attn", "MDLM"); they pass rightward through a series of 4 vertical flat gate-filter bars inside a flat funnel/wedge shape that narrows toward the right; at the right end, two outcome boxes — a GREEN box labelled "J3 PASS" and an AMBER box labelled "MDLM FAIL". Green is the only non-palette colour and is used solely for the pass box; amber is the single highlight. Horizontal.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Funnel mouth label: "40+ model families · progressive 2% → 20% → 100% data funnel"
- Stage 1 annotation (wide): "2% data: all families enter (Markov, AR, VAE, GAN-adjacent, cross-attention, masked diffusion MDLM/SEDD)"
- Stage 2 annotation (mid): "20% data: survivors evaluated"
- Stage 3 annotation (narrow): "100% data: final evaluation"
- Gate bar 1: "Gate 1: activity JS ≤ 0.05"
- Gate bar 2: "Gate 2: AT_HOME RMS ≤ 5.3 pp"
- Gate bar 3: "Gate 3: co-presence max ≤ 5.0 pp"
- Gate bar 4: "Gate 4: composite score threshold"
- Green callout: "Calibrated J3 — PASS (4/4 gates)" · "act_JS 0.0191 · AT_HOME RMS 4.57 pp · co-presence max ~2.03 pp"
- Amber callout: "MDLM — FAIL (2/4 gates)" · "Best composite score 0.559 — but fails AT_HOME + co-presence gates"
- Note tile: "Best-training-loss cross-attention: collapsed 20+ pp co-presence at inference (exposure bias)"

## Layout notes
- Aspect ratio: wide landscape (16:9 or wider), reading direction left → right
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: the "MDLM FAIL" outcome box at the funnel exit (right side)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- The green "J3 PASS" box is the only green element; all other elements follow the muted slate-blue/teal/warm-grey palette; four gate filter bars span the funnel body at equally spaced intervals, narrowing the visual passage from left to right
