# Image prompt — 4J pipeline steps figure (Steps 0 to 9)

**Deliverable:** one raster image, `HETUS_LLM_Pipeline_Steps.png`, generated **by the author** in their
own image tool. This file is the prompt. It is written so the image can be produced without asking a
follow-up question.

**Install path once generated:** `4J_docs_occ/writing/submission/figures/`
**Source of truth for the content:** `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md`, the ASCII
box diagram, Steps 0 to 9, as it stood on 2026-08-14.

> **This is the second figure of paper 4 and it is not the graphical abstract.**
> `4thJ_graphical_abstract.md` shows *what flows into what*: five bands, left to right, countries
> converging into one model. **This figure shows how the work is organised**: ten sequential steps, the
> decision that closes each one, and the validation tier that guards it. The two must not be merged and
> must not repeat each other's layout. If a reader sees both, the abstract answers *what is the idea*
> and this one answers *what are the stages and where can it fail*.
>
> Intended use: the first figure of the Methods section, or a supplementary overview figure. It is
> allowed to be denser than the graphical abstract, because it is read at full page width and not at
> thumbnail size.

---

## 0. Read this before generating

> 🔴 **NO NUMBER MAY APPEAR IN THIS IMAGE EXCEPT THE STEP NUMBERS 0 TO 9 AND THE SYMBOL `N-1`.**
> Paper 4 has produced **no results**. Every threshold, accuracy, token count, wave count, country
> count, model size and year is either unmeasured, undecided, or a target rather than an outcome. A
> figure that shows a plausible-looking `0.015`, `7B`, `5 countries` or `2010` will be read as a
> settled fact, and several of those are exactly the values still open.
>
> If the layout leaves a space that wants a number, **leave it empty or write the label without a
> value.** Section 6 is the complete allowed list of strings. Nothing outside it.

This is a **process diagram**. It shows the order of the work, not the flow of data.

---

## 1. What the figure must communicate, in one sentence

The project runs as **ten sequential steps**, from a feasibility gate through corpus, harmonisation,
serialisation, fine-tuning, population linkage, the held-out transfer test, constrained generation,
building simulation and end-use loads; **each step is closed by a stated decision**, and **each step is
guarded by a validation tier that can fail it**.

If a reader takes away only one thing, it should be: **the transfer step is the middle of the diagram
and everything before it exists to make it testable.**

The second thing, which the figure must not obscure: **the steps are not all in the same state.** Some
are decided, most are not. The figure distinguishes them.

---

## 2. Overall composition

**Portrait or square, tall.** Roughly 1400 x 1900 pixels or the same aspect. This is deliberately the
opposite orientation to the graphical abstract, so the two are never confused.

Three columns:

```
   left gutter          main spine                right gutter
   (phase bands)        (the ten step cards)      (validation tiers)
   narrow               wide, vertical            narrow
```

* The **main spine** is a single vertical column of ten rounded rectangular cards, Step 0 at the top,
  Step 9 at the bottom, joined by short downward arrows.
* The **left gutter** carries four tall vertical phase bands, each spanning the steps it groups, drawn
  as a soft-tinted rounded bar with the phase name in it.
* The **right gutter** carries five small tiles, one per validation tier, each connected by a thin
  horizontal line to the step or steps it guards. These lines are the only horizontal connectors in the
  figure.

White background. Flat vector style, matching the graphical abstract and the 3J figures.

---

## 3. The four phase bands (left gutter)

Each band spans a contiguous run of steps and is labelled with horizontal text at its top, not rotated.

| Band | Spans | Label |
|---|---|---|
| 1 | Steps 0 to 2 | `DATA` |
| 2 | Steps 3 to 5 | `MODEL` |
| 3 | Steps 6 to 7 | `CLAIM` |
| 4 | Steps 8 to 9 | `ENERGY` |

🔴 **The `CLAIM` band is the one that must stand out.** Give it the strongest tint of the four, and make
it slightly wider than the others so it reads as the centre of gravity of the diagram. Everything above
it is preparation and everything below it is consequence.

---

## 4. The ten step cards (main spine)

Every card has the same internal layout, so the eye can scan down the column:

```
  ┌──────────────────────────────────────────────┐
  │  [n]   STEP TITLE                    [state] │   <- number chip, title, state chip
  │        one line: what closes this step       │   <- the decision line
  │        one line: what is still open here     │   <- omitted if nothing is open
  └──────────────────────────────────────────────┘
```

* The **number chip** is a small filled circle at the left edge containing the digit `0` to `9`.
* The **state chip** sits at the right edge of the card and is one of exactly three:
  * `cleared` — solid fill, checkmark glyph
  * `decided` — solid fill, no glyph
  * `open` — **hollow outline only, no fill**
  Use fill weight, not colour alone, to separate them. A colour-blind reader must be able to tell an
  open step from a decided one.

The cards, top to bottom, with the exact text each carries:

| # | Title | Decision line | Open line | State |
|---|---|---|---|---|
| 0 | `Feasibility gate` | `data reachable, prior art clear, method justified, release limits known` | — | `cleared` |
| 1 | `Corpus` | `national time-use series, several waves per country` | `how many waves earn their place` | `open` |
| 2 | `Harmonisation` | `common activity, location and co-presence coding` | `pooling level across waves` | `open` |
| 3 | `Serialisation` | `episode form: duration, activity, location, co-presence` | — | `decided` |
| 4 | `Fine-tuning` | `open-weight base model, low-rank adapter, all countries trained jointly` | `which model family` | `open` |
| 5 | `Population linkage` | `synthetic population first, then one generated day per person` | — | `decided` |
| 6 | `Transfer test` | `train on N-1 countries, generate the held-out one from published marginals` | `which country is held out` | `open` |
| 7 | `Constrained generation` | `well-formed diaries guaranteed at decoding` | — | `decided` |
| 8 | `Building simulation` | `European residential archetypes, uninjected control run first` | `archetype models built from published parameter tables` | `open` |
| 9 | `End-use loads` | `published activity-to-appliance mappings, adapted not authored` | — | `open` |

🔴 **Card 6 is drawn larger than the others** and carries one extra line, in bold, beneath its decision
line:

* `the bar: beat real diaries from the other countries, reweighted to the held-out country`

This is the falsifiable claim of the paper and it is the single most important sentence in the figure.
If the layout is tight, shrink cards 8 and 9 rather than this line.

---

## 5. The validation tiers (right gutter)

Five small tiles, stacked, each joined by a thin horizontal line to the step or steps it guards. Tiles
are visually lighter than the step cards so the spine stays dominant.

| Tile label | Connects to |
|---|---|
| `distributional fidelity` | Step 6 |
| `collapse and memorisation` | Step 6 |
| `structural validity` | Step 7 |
| `transfer margin` | Step 6 |
| `downstream energy` | Steps 8 and 9 |

Below the tiles, one small caption in a dashed-border box:

* `every tier is first shown failing on a deliberately broken control`

🔴 **This caption is not decoration.** A validation battery that has never been seen to fail has not
been shown to work, and it is the practice this project runs on. Keep it even if the gutter is crowded.

---

## 6. THE COMPLETE LIST OF PERMITTED TEXT STRINGS

Every string that may appear in the image. Nothing else.

Title, two lines at the top, centred:

* `From Harmonised Time-Use Surveys to Simulated Building Energy`
* `The ten steps of the cross-national occupancy pipeline`

Phase bands:

* `DATA`, `MODEL`, `CLAIM`, `ENERGY`

Step numbers:

* `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9` — **only inside the number chips**

Step titles:

* `Feasibility gate`, `Corpus`, `Harmonisation`, `Serialisation`, `Fine-tuning`,
  `Population linkage`, `Transfer test`, `Constrained generation`, `Building simulation`,
  `End-use loads`

Step body lines, exactly as written in the Section 4 table:

* `data reachable, prior art clear, method justified, release limits known`
* `national time-use series, several waves per country`
* `how many waves earn their place`
* `common activity, location and co-presence coding`
* `pooling level across waves`
* `episode form: duration, activity, location, co-presence`
* `open-weight base model, low-rank adapter, all countries trained jointly`
* `which model family`
* `synthetic population first, then one generated day per person`
* `train on N-1 countries, generate the held-out one from published marginals`
* `which country is held out`
* `the bar: beat real diaries from the other countries, reweighted to the held-out country`
* `well-formed diaries guaranteed at decoding`
* `European residential archetypes, uninjected control run first`
* `archetype models built from published parameter tables`
* `published activity-to-appliance mappings, adapted not authored`

State chips:

* `cleared`, `decided`, `open`

Validation tiles:

* `distributional fidelity`, `collapse and memorisation`, `structural validity`, `transfer margin`,
  `downstream energy`
* `every tier is first shown failing on a deliberately broken control`

**`N-1` is written exactly as that, as a symbol, not as a digit.** It is the only algebraic string in
the figure and it must not be resolved into a number.

---

## 7. Palette

Consistent with the graphical abstract so the two read as one series, and colour-blind safe.

| Element | Colour |
|---|---|
| Phase band `DATA` | light grey |
| Phase band `MODEL` | teal, soft tint |
| Phase band `CLAIM` | dark navy, soft tint, strongest of the four |
| Phase band `ENERGY` | orange, soft tint |
| Step card fill | white, thin grey border |
| Card 6 fill | very light navy, thicker border |
| State chip `cleared` / `decided` | solid dark navy |
| State chip `open` | white fill, navy outline |
| Validation tiles | light grey, thin border |
| Background | white |

Do not use red and green as the only distinguishing pair anywhere in the figure.

---

## 8. Typography

* One clean sans-serif family throughout, the same as the graphical abstract.
* Step titles bold; body lines regular and one step smaller; state chips small caps or regular, never
  bold.
* All text horizontal. **No rotated text anywhere**, including the phase band labels. The 3J figure's
  rotated block was the hardest element to read at journal scale and it is not repeated.
* The figure is read at full page width, so body lines may be smaller than in the graphical abstract,
  but every string in Section 6 must remain legible at 100 percent page width in print. If a body line
  cannot survive that, delete the line rather than shrinking the type.

---

## 9. Explicit do-nots

1. **No invented numbers.** Step numbers `0` to `9` and the symbol `N-1` are the entire permitted set.
   No thresholds, no percentages, no token counts, no wave counts, no country counts, no model sizes.
2. **No real country names and no real flags.** The corpus is not final.
3. **No named model** — no `Gemma`, no `Llama`, no `Qwen`, no `Mistral`, no parameter count. Step 4 is
   still open on exactly this question and a figure that names a model will outlive the decision.
4. **No institutional logos** for Eurostat, statistical institutes, universities or model developers.
5. **No brain, robot, android, glowing orb, or chat bubble.** This is a process diagram in a
   building-science journal.
6. **No 3D perspective, no drop shadows, no gradients on text.** Flat vector.
7. **No rotated text.**
8. **No horizontal connectors except the validation-tier lines.** The spine flows downward only. A
   figure with arrows in several directions stops reading as a sequence.
9. 🔴 **No loop-back arrows, no iteration cycles, no feedback loops.** The steps run once, in order.
   Drawing a cycle would state a workflow the project does not have.
10. 🔴 **No time axis, no years, no forecast arrow, no `2030`.** Paper 4 contains no forecast at all: it
    is out of scope, not merely unproven. The vertical axis of this figure is **sequence of work**, not
    time, and nothing in it may suggest otherwise.
11. 🔴 **Nothing that implies the model itself is released.** No download icon, no repository mark, no
    open-weights badge on Step 4. The trained model cannot be published.
12. **Do not redraw the graphical abstract.** No five-band horizontal layout, no converging country
    lanes, no building illustration, no activity ribbons, no schedule curves. If this figure starts to
    look like the abstract, it has failed at its only job, which is to show the stages.

---

## 10. After the author generates it

Handled by the assistant, not by the image tool:

1. Install the file at `4J_docs_occ/writing/submission/figures/HETUS_LLM_Pipeline_Steps.png`.
2. Verify it byte-identical inside the shipped document after any conversion step, and record the md5
   before and after.
3. Read the **installed** image and check it against Section 6 string by string. Any string in the image
   that is not in Section 6 is a defect and is reported, not silently accepted.
4. Check the state chips specifically: Step 0 `cleared`; Steps 3, 5 and 7 `decided`; Steps 1, 2, 4, 6, 8
   and 9 `open`. A figure that shows more closed steps than the plan does overstates the project's
   position and must be regenerated.
5. Check that Step 6 is the largest card and carries its bold bar line.
6. Check that no year, no threshold value and no model name appears anywhere.
7. Check legibility at full page width in print before it is accepted.
8. 🔴 **If the plan document changes, this prompt changes first and the image is regenerated from it.**
   The Section 4 table is a copy of the Overview's step list, and a copy that drifts from its source is
   worse than no figure.
