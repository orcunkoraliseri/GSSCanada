# Figure 2 -- Three-Stage Roadmap (one channel, then two, then four)

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** the paper's structural (additive) argument in one image -- what each stage added, and which artefacts carried forward unchanged.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (three-stage roadmap note; Step 3 tiling note on bit-identical paths)

> **Filename note.** This prompt and its PNG keep the filename `Figure_02_three_leg_roadmap.*`. The
> filename is referenced by a placeholder in `Chapter_01_Introduction.md` and by the figure checker;
> renaming it breaks the build. Only the *drawn content* changes.

---

## 🔴 The rule this figure broke worst. Read before generating.

The 2026-08-09 image labels its three containers with this project's internal codes for its own
construction stages. Those codes are not defined anywhere a reader can reach, and the manuscript was rewritten on 2026-08-11 to remove them from every sentence. **The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must not appear anywhere in the image.**

The replacement is not a different label for the same idea. It is better: **label each container by
what it contains.** The figure's whole argument is that each stage adds channels without removing any,
so naming the containers by their channel sets makes the nesting self-evident and needs no legend.

| container | draw exactly this, and nothing else |
|---|---|
| leftmost, narrowest | `Residential only` |
| middle | `Residential + Office` |
| rightmost, widest | `Residential + Office + Retail + Hotel` with a second line `this paper` |

## 🔴 Two further rules, from the Figure 1 regeneration

- **Colour names are styling and must never be drawn as text.** The 2026-08-11 Figure 1 printed the
  literal word "amber" inside two boxes. Everything under **LABEL TEXT** is drawn verbatim; everything
  under **STYLING** is never drawn.
- **Crop tight.** The 2026-08-09 image left 106 px of empty white above and 84 below (25% of its
  height). In the manuscript that band separates the artwork from its caption. Even margin on all four
  sides, roughly 2% of image width. Render at 500 dpi or better for the printed width.

---

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. Horizontal left-to-right reading order, landscape composition, white background, sans-serif labels. The artwork must fill the frame with only a small even margin on all four sides.

DRAW ONLY THE TEXT LISTED UNDER "LABEL TEXT". Every colour word below is a styling instruction and must never be rendered as visible text in the image.

STYLING (never draw these words): three large flat rounded-rectangle containers arranged left to right, each wider than the last, telescoping like nested building blocks, connected by thick flat arrows. Container 1 filled pale warm grey. Container 2 filled desaturated slate-blue/teal. Container 3 drawn as a warm amber/gold outline whose interior still shows container 2's slate-blue/teal block unchanged, so that container 3 visibly CONTAINS container 2 rather than replacing it. The only amber element in the image is container 3's outline. No other colours.

LABEL TEXT (draw exactly these strings, once each, and no others):
  Container 1: "Residential only"
  Container 2: "Residential + Office"
  Container 3, first line:  "Residential + Office + Retail + Hotel"
  Container 3, second line, smaller: "this paper"
  Connector line beneath all three: "carried forward"

SCENE: Container 1, narrow, holds one simple person-outline icon. A flat arrow points right into container 2, medium width, which holds that same person-outline plus a new briefcase-outline icon. A flat arrow points right into container 3, wide, which holds all of container 2's icons unchanged plus two new icons, a shopping-bag outline and a bed outline. Each channel icon appears only in the container where that channel is first introduced, and is then carried unchanged into every container to its right. A thin horizontal connector line with a small chain-link icon runs UNDER all three containers, spanning the full width, labelled "carried forward" along its length. Do not label that line "bit-identical".
```

## 🔴 CORRECTION 2026-08-06 night -- the connector callout asserted a claim Table 6 declines to certify

The chain-link callout below originally read:

> "Residential + Office pipeline paths carried forward bit-identical into the four-channel stage (Step 3: one tiler-list entry appends AT_RETAIL; residential + office CSV paths untouched)"

and the caution line beneath it cleared that wording as "directly sourced (Step 3 note)". Both were
wrong in the same way. The Step-3 note in `3rdJ_00_4split_Occupancy_Pipeline_Overview.md` is **prose
asserting a design intent**, and `Table_06_leg2_leg3_delta.md` grades exactly that claim
`⚠ check source`, with the explicit reason that "this prose claim is not itself acceptable evidence;
no independent file/column comparison of the tiler's residential/office output was performed."
Of the nine steps in Table 6, **only Step 7 carries an affirmative evidence verdict**, and even that
one is scoped to the base prototype geometry (four IDF files, md5-verified).

The caution was not absent, it was **under-scoped**: it guarded the one-channel-to-two-channel arm
and, by naming only that arm, read as clearance for the two-channel-to-four-channel arm. A caution
that is correct about one arm and silent about the other is read as permission for the other.

Corrected below: the callout now states the one bit-identical claim that has md5 evidence (Step 7
geometry) and reports Step 3 as additive by design with byte-equality unverified. Enforced from now on
by `f5_figure_check.py` arm **C7**, which reads Table 6 from disk and fails any figure asserting
"bit-identical" for a step whose evidence cell is not an affirmative Yes.

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Container 1 caption: "Residential (AT_HOME) -- complete, published separately"
- Container 2 caption: "+ Office (AT_WORK) -- complete, validated end-to-end 2026-07-01; the People-schedule wiring-bug lesson was learned at this stage"
- Container 3 caption: "+ Retail (AT_RETAIL, GSS) + Hotel (non-GSS, tourism statistics) -- this paper"
- Chain-link connector callout: "Carried forward into the four-channel stage: the Step 7 base tower geometry is md5-verified byte-identical (4 IDF files); the Step 3 residential + office tiler paths are additive by design (retail kept in a separate CSV) but byte-equality was not verified -- see Table 6"
- Small footnote under container 3: "four occupancy channels driving four uses inside one building -- not four building archetypes"
- Do not label ANY stage-to-stage reuse "bit-identical" unless Table 6's evidence cell for that step is an affirmative Yes. Today that is Step 7 alone, and only for the base prototype geometry. Step 3 is graded ⚠ check source, so the two-channel-to-four-channel tiler reuse may be called additive by design but never bit-identical. This applies to both arms equally.

## Layout notes
- Aspect ratio: wide landscape (16:9), reading direction left to right
- Style: flat 2D, telescoping/nested containers to show additive growth, not replacement
- The single amber highlight in this figure is the outermost container's outline, since this figure's whole point is what this paper adds
- Keep the "carried forward" connector visually distinct (thin line + chain-link icon) from the containers themselves, so a reviewer can see reuse and addition as two separate visual channels
