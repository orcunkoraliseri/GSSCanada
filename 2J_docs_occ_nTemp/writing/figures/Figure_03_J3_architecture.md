# Figure 3 — Calibrated-J3 Conditional Generator Architecture
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Horizontal left→right: "Diary Input" box → "Shared Encoder" box → a fork into two stacked horizontal lanes: upper lane "AR Decoder" → "Activity Output"; lower lane "NAT Heads" → "AT Home Output" — the two lanes are separated by a dashed horizontal divider line labelled "Detach Barrier" (AMBER dashed line/element). Both lanes converge into a "Raking" box → "Calibrated Output" box at the right. A "Conditioning" box sits below the main flow, with two thin arrows pointing up into the encoder and the decoder. Flat, horizontal.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- Input slab: "48-slot multivariate diary token stream"
- Condition slab: "Conditioning vector  d_cond = 90" · variables: "demographics, cycle-year, COLLECT_MODE, ATTSCH, POWST/WFH, MODE"
- Encoder tower: "Shared Transformer encoder · 6 layers · d_model = 384 · ~29.25M params"
- AR Decoder tower: "Autoregressive activity decoder · 6 layers"
- Activity output: "14-category activity sequence (48 slots)"
- Amber barrier label: "Gradient-detach barrier (stop-gradient)"
- NAT heads: "Non-autoregressive binary heads: AT_HOME + 9 co-presence channels"
- Raking tile: "Post-hoc marginal raking · per (cycle × stratum × slot) · Phase-8B"
- Output slab: "Calibrated diary-day"
- Gate annotations (as callout box): "Hard gates: act_JS ≤ 0.05 · AT_HOME RMS ≤ 5.3 pp · co-presence max ≤ 5.0 pp · sole 4/4-gate model"

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left → right
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: the "Detach Barrier" dashed line/element between the fork and the NAT binary heads lane
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- The conditioning vector box sits below the main horizontal flow and sends two arrows upward — one to the encoder, one to the decoder area — both must be visible; the fork clearly splits into an upper AR path and a lower NAT path separated by the amber dashed divider
