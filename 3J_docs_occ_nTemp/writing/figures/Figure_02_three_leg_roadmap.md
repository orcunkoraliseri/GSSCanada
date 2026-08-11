# Figure 2 -- Three-Leg Roadmap (Leg 1 to Leg 2 to Leg 3)
**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** the paper's structural (additive) argument in one image -- what each leg added, and which artefacts carried forward unchanged.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (three-leg roadmap note; Step 3 tiling note on bit-identical paths)

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. Three large flat rounded-rectangle "leg" containers arranged left to right, each wider than the last (stepped/telescoping width, like nested building blocks), connected by thick flat arrows. Restrained academic palette: leg 1 filled pale warm-grey, leg 2 filled desaturated slate-blue/teal, leg 3 filled warm amber/gold outline with the slate-blue/teal Leg-2 content still visible inside it (leg 3 container visually CONTAINS leg 2's elements plus new amber elements, showing addition not replacement). Inside each leg container, small flat channel icons (a simple person-outline for residential, a briefcase outline for office, a shopping-bag outline for retail, a bed outline for hotel) appear only when that channel is first introduced. A thin horizontal "carried forward unchanged" connector line with a small chain-link icon runs UNDER all three legs, spanning from leg 1 through leg 2 into leg 3, to represent artefacts reused bit-identically. No other colours, no clutter, generous whitespace.

SCENE: Leg 1 (narrow, pale grey): one person-outline icon, label "Leg 1". Arrow right into Leg 2 (medium, slate-blue/teal, contains Leg 1's person-outline plus a new briefcase-outline icon): label "Leg 2". Arrow right into Leg 3 (wide, amber outline containing all of Leg 2's icons unchanged plus two new icons: a shopping-bag outline and a bed outline): label "Leg 3". The chain-link connector line beneath all three legs is labelled along its length "carried forward" (see the correction block above: it must NOT be labelled "bit-identical").
```

## 🔴 CORRECTION 2026-08-06 night -- the connector callout asserted a claim Table 6 declines to certify

The chain-link callout below originally read:

> "Residential + Office pipeline paths carried forward bit-identical into Leg 3 (Step 3: one tiler-list entry appends AT_RETAIL; residential + office CSV paths untouched)"

and the caution line beneath it cleared that wording as "directly sourced (Step 3 note)". Both were
wrong in the same way. The Step-3 note in `3rdJ_00_4split_Occupancy_Pipeline_Overview.md` is **prose
asserting a design intent**, and `Table_06_leg2_leg3_delta.md` grades exactly that claim
`⚠ check source`, with the explicit reason that "this prose claim is not itself acceptable evidence;
no independent file/column comparison of the tiler's residential/office output was performed."
Of the nine steps in Table 6, **only Step 7 carries an affirmative evidence verdict**, and even that
one is scoped to the base prototype geometry (four IDF files, md5-verified).

The caution was not absent, it was **under-scoped**: it guarded the Leg-1-to-Leg-2 arm and, by naming
only that arm, read as clearance for the Leg-2-to-Leg-3 arm. A caution that is correct about one arm
and silent about the other is read as permission for the other.

Corrected below: the callout now states the one bit-identical claim that has md5 evidence (Step 7
geometry) and reports Step 3 as additive by design with byte-equality unverified. Enforced from now on
by `f5_figure_check.py` arm **C7**, which reads Table 6 from disk and fails any figure asserting
"bit-identical" for a step whose evidence cell is not an affirmative Yes.

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Leg 1 label: "Residential (AT_HOME) -- complete, published separately"
- Leg 2 label: "+ Office (AT_WORK) -- complete, validated end-to-end 2026-07-01; People-schedule wiring-bug lesson learned here"
- Leg 3 label: "+ Retail (AT_RETAIL, GSS) + Hotel (non-GSS, tourism statistics) -- this paper"
- Chain-link connector callout: "Carried forward into the four-channel stage: the Step 7 base tower geometry is md5-verified byte-identical (4 IDF files); the Step 3 residential + office tiler paths are additive by design (retail kept in a separate CSV) but byte-equality was not verified -- see Table 6"
- Small footnote under Leg 3: "four occupancy channels driving four uses inside one building -- not four building archetypes"
- Do not label ANY leg-to-leg reuse "bit-identical" unless Table 6's evidence cell for that step is an affirmative Yes. Today that is Step 7 alone, and only for the base prototype geometry. Step 3 is graded ⚠ check source, so the Leg-2-to-Leg-3 tiler reuse may be called additive by design but never bit-identical. This applies to the Leg-1-to-Leg-2 arm and the Leg-2-to-Leg-3 arm equally.

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D, telescoping/nested containers to show additive growth, not replacement
- The single amber highlight in this figure is the Leg-3 container outline itself, since this figure's whole point is what Leg 3 adds
- Keep the "carried forward" connector visually distinct (thin line + chain-link icon) from the leg containers themselves, so a reviewer can see reuse and addition as two separate visual channels
