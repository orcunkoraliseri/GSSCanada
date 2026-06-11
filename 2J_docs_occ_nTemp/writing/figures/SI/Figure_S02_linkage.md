# Figure S2 — Census–GSS Probabilistic Linkage Workflow
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector flowchart in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients, no rendering effects. Horizontal left-to-right reading order, landscape composition, white background. Each step is a simple flat rounded-rectangle box (or a soft-tinted grouped container holding one or two small white sub-boxes) with a thin darker outline, connected by thin straight connector lines with small arrowheads. Use minimal FLAT single-colour line icons (database-cylinder, plain house outline, calendar grid, small bar-chart, link/chain glyph) — flat line art only, no shading. Muted professional academic palette: desaturated slate-blue, teal, and warm-grey fills on white, with a SINGLE amber-filled box reserved for the one highlighted element. Inside each box render ONLY a short 2-3 word sans-serif label — NO section numbers, NO long phrases, NO full numbers, equations, or percentages (those are added afterward as overlay text). Even spacing, generous whitespace, crisp and legible.

SCENE: Two flat source lanes on the left feeding inward into a central matching mechanism, then a short chain to a terminal box on the right. Top-left lane "GSS Side": a diary database-cylinder glyph → "Diary Pool" box → "Day-Type Strata" box. Bottom-left lane "Census Side": a "PUMF" database-cylinder glyph → "Demographics" box → "Dwelling Vars" box. Both lanes converge with thin arrows into a central grouped container "Tiered Match" holding a small "Match Keys" box above four stacked descending bars labelled "Tier 1", "Tier 2", "Tier 3", "FailSafe" (the FailSafe bar drawn as a thin near-empty sliver). From the central match a thin arrow leads right through two small chained boxes "HH Aggregate" → "Plausibility Gate" to a terminal box on the far right: "Linked Frame" (AMBER). Left→right.
```

## Annotations to overlay afterward (exact text/numbers — keep OUT of the AI image)
- GSS drum: "Augmented GSS diary-days (~192,183)"
- Diary Pool tile: "Per-day-type donor pools"
- Day-Type Strata tile: "Weekday / Saturday / Sunday strata"
- Census drum: "Census PUMF 2021  286,537 individuals"
- Demographics tile: "7 match keys + day-type stratum"
- Dwelling Vars tile: "Carried from matched Census record: dwelling type, period of construction, bedrooms, rooms, condo, repair, value"
- Match Keys box: "7 keys: AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA (+ DDAY_STRATA)"
- Tier 1 bar: "Tier-1 Perfect — all 7 keys + stratum  44.94%"
- Tier 2 bar: "Tier-2 Core — AGEGRP, SEX, LFTAG, PR + stratum  21.39%"
- Tier 3 bar: "Tier-3 Constraints — AGEGRP, SEX + stratum  33.67%"
- FailSafe sliver: "Tier-4 FailSafe — stratum only  0.00% (never invoked)"
- HH Aggregate tile: "Per-slot MAX AT_HOME across household members"
- Plausibility Gate tile: "Remove HH with mean AT_HOME < 0.30 → removes 1,082 households"
- Amber output slab: "144,507-household BEM frame"

## Layout notes
- Aspect ratio: wide landscape (3:2), reading direction left → right
- Style: flat 2D flowchart; no isometric or 3D treatment
- Amber-highlight element: the "Linked Frame" terminal output box (the 144,507-household final product of the linkage step)
- Labels inside image: 2-3 words each; no section numbers inside the rendered scene
- Two source lanes (GSS diary pool + Census individuals) converge into the central four-tier demographic key-descent match — the structural heart of the linkage; the post-match HH aggregation and plausibility gate lead to the amber terminal frame on the far right
- METHOD NOTE: this is a slot-native 4-tier hierarchical **demographic key-descent match** (each Census individual draws one augmented diary row by descending key specificity). It is NOT a K-means / Random-Forest archetype scheme — that was the superseded 1st-journal per-census-year pipeline. The PNG must be regenerated from this corrected prompt.
