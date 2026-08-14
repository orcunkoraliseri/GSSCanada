# Image prompt — 4J graphical abstract

**Deliverable:** one raster image, `HETUS_LLM_CrossNational_Pipeline.png`, generated **by the author**
in their own image tool. This file is the prompt. It is written so the image can be produced without
asking a follow-up question.

**Install path once generated:** `4J_docs_occ/writing/submission/figures/`
**Sibling to match:** `3J_docs_occ_nTemp/Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png`

> **Updated 2026-08-14**, after all sixteen `L`-series research reports came back. Four things changed
> and each of them changes the drawing, not only the wording:
>
> 1. **The pipeline is now explicitly two-stage.** Census marginals no longer feed the model directly.
>    They build a synthetic population first, and the model is conditioned on each synthetic person.
>    A figure showing marginals feeding the model states a design we examined and rejected.
> 2. **The episode tuple lost its `start` field.** Start time is the running sum of the durations, so
>    carrying it would be redundant and would misdescribe what the model emits.
> 3. **The held-out lane is now scored against something specific**, and naming it is the whole point
>    of the experiment.
> 4. **No forecast, no future year, no time arrow.** The longitudinal axis of papers 2 and 3 does not
>    survive into paper 4. See Section 7, item 10.
>
> **Updated again 2026-08-14, later**, after `RL17`, `RL18` and our own measurement on Speed. Two
> changes, and the first one changes a drawn element:
>
> 5. 🔴 **The corpus is now HETUS only, four countries, ONE wave each — not several.** Author decisions
>    5 and 6. The Canadian and American surveys left the paper, and the multi-wave depth went with
>    them: `RL17`'s wave inventory showed that three of the four candidate second waves sit past the
>    ACL 2000 coding break and that UK 2000-01 uses 15-minute slots, which our duration grammar cannot
>    accept. **The stacked offset cards in Band 1 must become a single card.** A stack now states a
>    corpus the paper does not have, which is exactly the failure Section 0 exists to prevent.
> 6. **The backbone is decided** (`allenai/Olmo-3-1025-7B`, measured, not chosen from a report). The
>    figure still does not name it — see the revised Section 7 item 3 for why that is now a choice
>    rather than a necessity.

---

## 0. Read this before generating

> 🔴 **NO NUMBER MAY APPEAR IN THIS IMAGE THAT IS NOT LISTED IN SECTION 6 BELOW.**
> Paper 4 has produced **no results**. Every metric, accuracy, percentage, country count and year range
> is either unmeasured or undecided. An image that invents a plausible-looking "0.94" or "18 countries"
> is worse than an image with no numbers, because it will be read as a result. The previous paper's
> generated supplementary figure shipped with a share labelled `4.0.1` and a garbled footnote, and that
> is the failure this section exists to prevent.
>
> If the layout leaves a space that looks like it wants a number, **leave it empty or write the label
> without a value.** Section 6 is the complete allowed list. Nothing outside it.

This is a **method diagram**, not a results figure. It shows what flows into what.

---

## 1. What the figure must communicate, in one sentence

Many national time-use surveys, already harmonised by the HETUS framework, are serialised into a common
token format and used to fine-tune **one** open-weight language model, which is then conditioned on
each person of a separately synthesised population to generate activity-resolved daily diaries for
**any** country in the framework, including one held out of training entirely, and those diaries drive
European residential building energy models.

If a reader takes away only one thing, it should be: **one model, many countries, and one of those
countries was never seen in training.**

The second thing, which the figure must not obscure: **the population and the day are produced by two
different machines.** An established statistical method makes the people; the language model gives each
person their day. Drawing them as one step would merge two claims a reviewer should be able to attack
separately.

---

## 2. Overall composition

Landscape, wide. Roughly 2000 x 1100 pixels or the same aspect. Left-to-right flow in **five vertical
bands**, exactly as the 3J sibling figure does. White background.

```
  BAND 1          BAND 2              BAND 3            BAND 4           BAND 5
  sources    ->   harmonisation  ->   the model    ->   generation   ->  buildings
  (left col)      (lanes fan in)      (dark centre)     (fan out)        (right col)
```

The visual grammar of the 3J figure is deliberately reused so the two read as a series: a narrow
left-hand column of data sources in a light grey rounded panel, coloured horizontal lanes carrying
labelled arrows into a **dark navy central block** that holds the model, and outputs fanning to the
right toward a building and a set of small schedule curves.

**The one structural change from 3J:** in 3J the lanes were four *building uses* and they stayed
parallel end to end. Here the lanes are *countries*, and they **converge** into the single model, then
**fan back out**. That convergence and re-divergence is the entire point of the figure and should be
the most visually obvious thing in it.

---

## 3. Band by band

### Band 1 — sources (left column, light grey rounded panel)

A vertical stack of small labelled blocks, each with a simple flat icon:

* A calendar or clipboard icon labelled **"National time-use surveys"**, with the sub-label
  **"household + individual + diary files"**, and a second sub-label
  **"one harmonised survey round per country"**.
  🔴 **Draw this block as a SINGLE card, not a stack.** The earlier version of this prompt asked for
  two or three offset stacked cards to show depth in time. **That is now wrong**: author decision 6
  fixed the corpus at one wave per country, and a stack would state a corpus the paper does not have.
  **No dates on the card**, per Section 0.
* A document icon labelled **"HETUS framework"**, sub-label
  **"common diary structure, common activity coding list, common location and co-presence fields"**.
* A people icon labelled **"Census and population marginals"**, sub-label
  **"household composition, age, employment"**.

Below the panel, small and unobtrusive, the Eurostat-style caption **"Harmonised European Time Use
Surveys"**. Do **not** reproduce any institutional logo.

### Band 2 — harmonisation and serialisation (the lanes begin)

Four or five coloured horizontal lanes emerge from Band 1 and run rightward, each a soft-tinted rounded
rectangle in the palette of Section 5. Each lane is **one country**, and they must be visually
identical in structure, because the point is that the pipeline treats every country the same way.

Inside **each** lane, left to right, three small steps joined by arrows:

1. A small national outline or a neutral flag-shaped placeholder tile. **Use generic labels: "Country
   A", "Country B", "Country C", "Country D".** Do not name real countries. **The corpus is now
   settled at four — which is why there are exactly four lanes — but which of them is held out is
   open decision 11, and naming them would let a reader guess.**
2. `episode diary` with the sub-label `(duration, activity, location, co-presence)`.
   🔴 **`start` is deliberately absent.** Start time is the running sum of the durations and the model
   never emits it. Adding it back would misdescribe the record.
3. `serialised record` with the sub-label `conditioning prefix + day sequence`.

The lanes should visibly **converge** as they approach Band 3, narrowing toward the dark block, the way
several roads merge into one.

**One lane is different, and it is the fourth or lowest one.** Draw it with a **dashed outline** rather
than solid, and its country tile is labelled **"Country D — held out"**. Its arrow does **not** enter
the model block. Instead it passes underneath or around the dark block and re-enters on the right-hand
side of Band 4. A short caption beside it reads **"never seen in training"**.

### Band 3 — the model (dark navy centre block, the visual anchor)

A single large rounded rectangle in dark navy, the same weight as the central block in the 3J figure.
Inside, stacked vertically:

* Title line, large, white text: **"One open-weight LLM, fine-tuned once"**.
* Below it, a simple abstract transformer motif: a small stack of three or four horizontal layer bars
  with an attention-style fan of thin connecting lines between two of them. Keep it schematic. Do not
  draw a brain, a robot, a chip, or a chat bubble.
* A small badge on the layer stack labelled **"low-rank adapter"**, connected by a thin line to the
  layer bars, to signal that only a small part is trained.
* Below the motif, three short lines of white text, one per line:
  * **"conditioned on: country, demographics, season, day type"**
  * **"trained on: N-1 countries"**
  * **"structure guaranteed at decoding"**

### Band 3b — the population track (a separate chain, drawn BELOW the navy block)

🔴 **This is the element added on 2026-08-14 and it is not optional.** In the previous version a single
strip labelled "survey weights + population marginals" ran along the bottom of the navy block, implying
that weighting happens inside the model. It does not. Weighting and representativeness are handled in a
separate, earlier, entirely conventional stage, and the figure has to show that.

Draw a **second, thinner horizontal chain running beneath the navy block**, in neutral grey so it reads
as supporting machinery rather than as a competing headline, with two boxes joined by an arrow:

1. `census marginals` (small icon: a grid or a table)
2. `synthetic population` with the sub-label `iterative proportional fitting`

From the second box, draw an arrow that turns **upward into Band 4**, joining the point where the model
output becomes individual diaries. The reading it must produce is: *the marginals make the people, the
model gives each person a day.* The arrow must **not** enter the navy block, because the population is
not an input to the language model's training.

Beside this chain, one small caption: **"population and day are generated separately"**.

### Band 4 — generation (lanes fan back out)

Out of the right edge of the navy block, the same coloured lanes re-emerge and fan outward. Each
carries a small horizontal strip diagram: a **stacked activity ribbon**, that is, a thin horizontal bar
of 20 to 30 coloured segments of unequal width representing an episode sequence across one day, with a
`00` at the left end and `24` at the right end. Four such ribbons, one per lane, and they must be
**visibly different from each other**, because diversity is the point.

The dashed held-out lane re-joins here from below, and its ribbon is drawn with the same dashed outline
so the reader can trace it. Beside it, a small callout box, dashed border, containing:

* line 1: **"held-out country"**
* line 2: **"generated from published marginals only"**
* line 3: **"scored against published aggregate statistics"**
* line 4: **"compared against real diaries reweighted to the same marginals"**

This callout is the second most important element in the figure after the navy block. Give it room.

🔴 **Line 4 is new on 2026-08-14 and it is the line that makes the experiment falsifiable.** The test is
not whether the generated diaries look reasonable. It is whether they beat a pool of *real* human diaries
from the training countries, reweighted to match the held-out country's demographics. A reader who takes
away only the first three lines will think the bar is lower than it is. Keep line 4 even if the callout
has to grow.

### Band 5 — buildings (right column)

* A simple flat illustration of a **European residential building typology row**: three or four
  adjoining dwelling forms of different heights and periods, side by side, not a tall tower. This is
  deliberately different from the 3J figure's single mixed-use tower, because paper 4 is residential
  stock across countries, not one building.
* To the right of the buildings, a small vertical stack of **four miniature schedule curves**, each in
  its lane's colour, each a simple line plot in a small white box with a `0` and `24` on the x axis and
  no y axis numbers. The curves must have visibly different shapes.
* Below the curves, one small line of text: **"occupancy and activity-driven internal gains"**.
* Below that, a second small line: **"EnergyPlus schedules"**.

Optionally, a very small EnergyPlus wordmark may be placed here as in the 3J figure, but only if the
author has the asset. Do not draw an approximation of a logo.

---

## 4. Typography

* One clean sans-serif family throughout, in the manner of the 3J figure.
* Title at the top of the image, centred, two lines, bold:
  * line 1: **"Cross-National Occupancy Generation with a Fine-Tuned Open-Weight LLM"**
  * line 2: **"One Model, Many Countries: HETUS-Harmonised Time-Use Diaries for Building Energy Modelling"**
* Lane labels bold; sub-labels regular and one step smaller.
* All text horizontal. **No rotated text anywhere**, including axis labels, because the 3J figure's
  rotated block was the hardest element to read at journal scale.
* Everything must remain legible when the image is reduced to a single journal column width. If a
  sub-label cannot survive that, delete the sub-label rather than shrinking it.

---

## 5. Palette

Match the 3J sibling so the two figures read as one series, and keep it colour-blind safe:

| Element | Colour |
|---|---|
| Lane 1 (Country A) | teal |
| Lane 2 (Country B) | orange |
| Lane 3 (Country C) | magenta or rose |
| Lane 4 (Country D, held out) | gold, **dashed outline** |
| Central model block | dark navy, white text |
| Source panel (Band 1) | light grey |
| Background | white |

Lane fills are soft tints; lane borders and arrows are the saturated version of the same hue. Do not
use red and green as the only distinguishing pair anywhere in the figure.

---

## 6. THE COMPLETE LIST OF PERMITTED TEXT STRINGS

Every string that may appear in the image. Nothing else. In particular **no accuracy, no percentage,
no country count, no year, no model name, no parameter count, and no metric value.**

Titles and headings:

* `Cross-National Occupancy Generation with a Fine-Tuned Open-Weight LLM`
* `One Model, Many Countries: HETUS-Harmonised Time-Use Diaries for Building Energy Modelling`

Band 1:

* `National time-use surveys`
* `household + individual + diary files`
* `one harmonised survey round per country`
* `HETUS framework`
* `common diary structure, common activity coding list, common location and co-presence fields`
* `Census and population marginals`
* `household composition, age, employment`
* `Harmonised European Time Use Surveys`

Band 2:

* `Country A`, `Country B`, `Country C`, `Country D — held out`
* `episode diary`
* `(duration, activity, location, co-presence)`
* `serialised record`
* `conditioning prefix + day sequence`
* `never seen in training`

Band 3:

* `One open-weight LLM, fine-tuned once`
* `low-rank adapter`
* `conditioned on: country, demographics, season, day type`
* `trained on: N-1 countries`
* `structure guaranteed at decoding`

Band 3b:

* `census marginals`
* `synthetic population`
* `iterative proportional fitting`
* `population and day are generated separately`

Band 4:

* `held-out country`
* `generated from published marginals only`
* `scored against published aggregate statistics`
* `compared against real diaries reweighted to the same marginals`
* `00` and `24` as the only axis labels on the activity ribbons

Band 5:

* `occupancy and activity-driven internal gains`
* `EnergyPlus schedules`
* `0` and `24` as the only axis labels on the schedule curves

**`N-1` is written exactly as that, as a symbol, not as a digit.** It is the only algebraic string in
the figure and it must not be resolved into a number.

---

## 7. Explicit do-nots

1. **No invented numbers.** See Section 0 and Section 6.
2. **No real country names and no real flags.** The corpus is now decided — four HETUS countries — but
   **which one is held out is not**, and a named lane would let a reader guess the answer to the
   experiment's central choice before it is made.
3. **No named model** — no `OLMo`, no `Gemma`, no `Llama`, no `Qwen`, no parameter count. 🔴 **The
   reason changed on 2026-08-14 and the rule did not.** The backbone is now decided
   (`allenai/Olmo-3-1025-7B`, settled by our own measurement), so this is no longer "the model is not
   chosen". It is that **the figure's claim is architectural — *one* open-weight LLM, fine-tuned once
   — and naming a checkpoint dates the figure without strengthening the claim.** If the author wants
   the checkpoint visible, it belongs in the figure *caption*, which is text and can be corrected,
   never inside the navy block.
4. **No institutional logos** for Eurostat, statistical institutes, universities or model developers.
5. **No brain, robot, android, glowing orb, neural-network-as-constellation, or chat bubble.** This is a
   method diagram in a building-science journal, not an AI illustration.
6. **No 3D perspective, no drop shadows, no gradients on text.** Flat vector style, as in the 3J figure.
7. **No rotated text.**
8. **No decorative arrows that do not carry data.** Every arrow in the figure means something flows.
9. **No results.** No bars, no scatter, no confusion matrix, no metric callouts. The only chart-like
   elements permitted are the four activity ribbons and the four schedule curves, and both are
   illustrative shapes, not plotted data.
10. 🔴 **No time axis, no years, no forecast arrow, no "2030".** Papers 2 and 3 both carried a temporal
    axis and it would be natural to reach for one here. **Paper 4 contains no forecast at all** — it is
    out of scope, not merely unproven. The figure must not imply an extrapolation the paper does not
    make.
    🔴 **The note that used to sit here is withdrawn.** It said that several *historical* survey waves
    feed the model and were worth showing as stacked cards. **Author decision 6 makes that false**:
    one wave per country, and the earlier waves are held-out validation rather than training data.
    Band 1 draws a single card. There is now no depth of data to show and no direction of time either.
11. 🔴 **Nothing that implies the model itself is released.** No download icon, no repository mark, no
    "open weights" badge attached to the navy block. The trained model cannot be published; the
    generated data and the code can. If any release is depicted at all, it attaches to the Band 4
    output, never to Band 3.
12. **No arrow from the population chain into the navy block.** The synthetic population conditions
    generation; it is not training input. This is the specific misreading Band 3b exists to prevent.

---

## 8. After the author generates it

Handled by the assistant, not by the image tool:

1. Install the file at `4J_docs_occ/writing/submission/figures/HETUS_LLM_CrossNational_Pipeline.png`.
2. Verify it byte-identical inside the shipped document after any conversion step, and record the md5
   before and after.
3. Read the **installed** image and check it against Section 6 string by string. Any string in the image
   that is not in Section 6 is a defect and is reported, not silently accepted.
4. Check the held-out lane specifically: dashed, bypassing the model block, re-entering at Band 4. If
   the generator drew it entering the model, the figure states the opposite of the paper's design and
   must be regenerated.
5. Check the population chain specifically: it runs **below** the navy block and its arrow turns up into
   Band 4. If the generator drew it entering the navy block, the figure says we trained on census
   marginals, which is false, and it must be regenerated.
6. Check that `start` does not appear in the episode sub-label, and that no year appears anywhere.
6b. 🔴 Check Band 1 draws **one card, not a stack**. A generator working from an older copy of this
   prompt will produce the stack, and a stack asserts a multi-wave corpus the paper does not have.
7. Check legibility at single-column width before it is accepted.
