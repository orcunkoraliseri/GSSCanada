# Figure S2 -- One Scenario Lever per Channel

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

**Target:** web image-generation LLM · **Style family:** flat-2D horizontal (shared across all schematics)
**Purpose:** the reviewer-defusing pattern carried from the two-channel construction stage -- show that each channel has exactly one, independently re-runnable 2030 sensitivity lever, and that Residential deliberately has none.
**Source:** `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 6 box + KEY DESIGN DECISIONS SUMMARY ("One scenario lever per channel")

> 🔴 **Naming rule, 2026-08-11.** The project's internal stage names -- the word "Leg" followed by a digit,
in any spelling or punctuation -- must
> not appear anywhere in the generated image. They are this project's internal names for its own
> construction stages; the manuscript was rewritten on 2026-08-11 to remove them from every sentence,
> so a reader has no way to resolve them. Use "the two-channel construction stage" and "this study".
> Colour names are styling instructions and must never be drawn as label text -- the 2026-08-11
> Figure 1 printed the literal word "amber" inside two boxes. Crop tight: no large empty band on any
> side, even margin of roughly 2% of image width, 500 dpi or better for the printed width.

## 🔴 TERMINOLOGY LOCK (v2) -- applies to every string drawn in this image

The project's internal stage codes must **not** appear anywhere in the artwork, in any spelling or
punctuation: `Leg-1`, `Leg 1`, `Leg1`, `Leg-2`, `Leg-3`, `leg`, `2J`, `3J`, `1J`, `0J`.
They are internal build names, undefined for any reader, and the manuscript text was cleared of them
on 2026-08-11. If a stage must be named, use the descriptive form:

| do NOT draw | draw this instead |
|---|---|
| Leg-1 | `single-channel stage` (or `Residential only`) |
| Leg-2 | `two-channel stage` (or `Residential + Office`) |
| Leg-3 / 3J / this leg | `this study` (or `Residential + Office + Retail + Hotel`) |
| "three legs" / "the legs" | `three stages` |
| 2J / 1J / 0J | `the predecessor study` |

`**Source:**` lines elsewhere in this file cite real folder names on disk (`Leg3_4-split/...`).
Those are provenance for the authors and are **outside the fenced prompt** -- they are never drawn.

**Resolution.** Elsevier requires 500 dpi for combination art. Placed at 7 in wide that is
**3500 px minimum on the long edge**; generate as large as the tool allows and do not upscale
afterwards. The 2026-08-09/11 images came back at 1376 x 768 (~197 dpi), which fails.

---

## Prompt (paste into the image LLM)

```
Clean flat 2D vector diagram in the style of a polished journal graphical abstract / SI figure. Strictly flat: NO 3D, no isometric, no perspective, no drop shadows, no gradients. White background, sans-serif labels, restrained academic palette. Four vertical lanes side by side, one per channel, evenly spaced, each headed by a small flat monochrome channel icon (a single flat silhouette in the lane's own colour, NOT a colour emoji and not a pictorial illustration) and a channel-name label. Three of the four lanes (Office, Retail, Hotel) each contain a small flat horizontal three-position slider icon with three tick marks, each slider filled in a distinct muted colour (slate-blue for Office, teal for Retail, amber for Hotel). The fourth lane (Residential) contains NO slider icon at all -- instead a small flat "no lever" glyph (a simple horizontal line with a small flat circular dot fixed in the centre, non-adjustable, greyed out) and a short text label stating explicitly that there is no lever for this channel. No other colours, minimal, crisp and legible. The artwork must fill the frame with a small even margin on all four sides.

EACH SLIDER'S THREE TICKS CARRY THEIR REAL VALUES AS TEXT. Do NOT label them "low", "default" or "high" -- those generic words are what the previous version drew, and they throw away the only information this figure exists to carry. The exact strings, left tick to right tick:
  Office lane:   "conservative"   "hybrid"          "fullyhybrid"
  Retail lane:   "0.90"           "0.97 (default)"  "1.05"
  Hotel lane:    "0.92"           "1.00"            "1.05"
The middle tick of each slider carries the filled knob, because the middle value is the default in all three cases.

Also draw, as text: the four lane headings "Residential", "Office", "Retail", "Hotel"; under the Residential lane, "Residential has no lever."; and a caption line along the bottom, "one lever per channel -- re-runnable sensitivity bands".

SCENE: Four lanes left to right: "Residential" (grey, fixed-dot "no lever" glyph, explicit no-lever label) -- "Office" (slate-blue slider) -- "Retail" (teal slider) -- "Hotel" (amber slider), each slider's three ticks labelled with the real values listed above.

FINAL CHECK: nine value strings are readable in the finished image (three per slider). If any tick reads "low", "default" or "high", the figure has failed.
```

## 🔴 Why the fenced block changed on 2026-08-11

The shipped image is clean and well drawn, and it carries **none of the numbers**. Its three sliders
are ticked "low / default / high", because the previous version of this prompt instructed exactly
that and filed the real values under "overlay afterward" -- an overlay step that has never once been
performed on any figure in this set. An SI figure whose entire subject is the width of three
sensitivity bands, printed without the bands, is an empty frame with good typography.

A second, smaller defect: the 2026-08-11 regeneration drew the four channel icons as **colour emoji**
(house, briefcase, shopping cart, hotel), which breaks the flat monochrome style every other figure in
the set shares. That version was not installed. The icon instruction above is now explicit.

## Annotations to overlay afterward (exact text/numbers -- keep OUT of the AI image)
- Residential lane label: "Residential -- no scenario lever (REPLACE injection, GSS-driven, not a code-density modulation)"
- Office lane, slider positions: "conservative" · "hybrid" · "fullyhybrid" (WFH band)
- Retail lane, slider positions: "0.90" · "0.97 (default)" · "1.05" (in-store share)
- Hotel lane, slider positions: "0.92" · "1.00" · "1.05" (SARIMA 2030 band)
- Caption line: "one lever per channel -- re-runnable sensitivity bands, the reviewer-defusing pattern carried from the two-channel stage"
- Explicit statement to render as overlay text under the Residential lane: "Residential has no lever."

## Layout notes
- Aspect ratio: can be narrower than the main-text figures (SI figure), landscape strip acceptable
- Style: flat 2D, no isometric or 3D treatment
- No single amber highlight convention here -- each of the three lever channels keeps its own distinct colour (slate-blue Office, teal Retail, amber Hotel) so the four lanes read as a comparison set, not a process flow
- The Residential lane's "no lever" glyph must be visually and unmistakably different from a slider (fixed centre dot, greyed out, no tick marks) -- it must not read as "a slider set to default", since the point of the figure is that no lever exists for this channel at all
