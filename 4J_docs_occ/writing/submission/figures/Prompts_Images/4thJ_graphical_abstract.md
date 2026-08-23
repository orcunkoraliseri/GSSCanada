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

> 🔴 **UPDATED AGAIN 2026-08-19, AND THIS ONE CHANGES THE CENTRE OF THE FIGURE. Regenerate.**
> Two author decisions landed since 2026-08-14 and between them they falsify the single most prominent
> string in the drawing.
>
> 7. 🔴 **`One open-weight LLM, fine-tuned once` IS NO LONGER TRUE AND MUST BE REPLACED.** The training
>    is **leave-one-country-out**: one low-rank adapter per held-out country, each trained only on the
>    others. There is one *base* model and one *recipe*, but there is not one fine-tune. **A single
>    joint fine-tune would put the held-out country into the training set, which is precisely what the
>    held-out lane in Band 4 claims did not happen.** The old title contradicts the figure's own
>    experiment, in white text, in the largest type in the image. New title in Section 3, Band 3.
>    Same defect, same day, as the pipeline-steps figure's `all countries trained jointly`.
> 8. 🔴 **Decision 16 excluded FRANCE. The corpus is THREE countries, not four.** So: **three lanes,
>    not four or five**; generic labels run **`Country A`, `Country B`, `Country C`** and **`Country D`
>    is retired**; the held-out lane is **`Country C — held out`**; and **`trained on: N-1 countries`
>    becomes `trained on: the other two`** — `N-1` beside four lanes read as "three of four" and is now
>    simply wrong. No algebraic string remains in the figure.
> 9. **Decision 11 — which country is held out — is CLOSED, and the reason the lanes are anonymous has
>    therefore changed.** All three are held out in rotation, one fold each, so there is no answer left
>    for a reader to guess. Section 7 item 2's stated reason is withdrawn and replaced; **the rule is
>    kept, now as an editorial choice, and Section 3 gains one line so the dashed lane is not read as a
>    permanent role.** See Section 3, Band 2.
>
> 🔴 **UPDATED AGAIN 2026-08-22. REGENERATE. Three drawn strings are now false and one is incomplete.**
> Nothing about the layout changes. Every change below is a string, and each was checked against the
> step document that rules it rather than against memory.
>
> 10. 🔴 **`season` IS NOT IN THE CONDITIONING PREFIX AND MUST BE STRUCK.** `D-S2-19` (author,
>     2026-08-17) dropped the stratum for all three countries: Spain's `TRIM` and Italy's `meseri` are
>     each delivered pre-banded, their boundaries are offset by one month at every edge, neither is a
>     union of the other, and no non-trivial season classification is expressible in all three
>     deliveries. `D-S3-11` then dropped `mode` and `scheme`, leaving **six** prefix fields:
>     `country, age band, sex, household type, economic status, day type`
>     (`Step3_docs/4thJ_03_serialisation.md:74`). The navy block's line becomes
>     **`conditioned on: country, demographics, day type`** — the same six fields, worded generically.
>     🔴 **This ruling predates the 2026-08-19 revision by two days and that revision missed it**,
>     which is the second time in this file that a retired phrase survived in a place nobody grepped.
>     Fixed in all three occurrences: Section 3 Band 3, Section 6, and the Section 10 paste block.
> 11. 🔴 **`census marginals` OVERSTATES THE BASIS AND BECOMES `published population marginals`.**
>     Step 5.1 was built after the last revision and two of the three folds do not rest on a census
>     table. `D-S5-4 (b)` takes **Spain's economic status from the microdata** because the Spanish
>     census publishes no economic-activity table for private households (`FINDING 49`), and Spain's
>     age and sex followed it; the UK has no UK-wide sex-by-age table, so sex there is an all-ages
>     **approximation**; and `D-S5-5` restricts every fold to **private households**, not all
>     residents. A box drawn `census marginals` states a provenance the figure does not have.
> 12. **Band 4's callout gains a fourth line: `three independent nulls, all reported`.** Work item 6.2
>     closed on 2026-08-22 with three, not one: the raked-donor null (`G6.1`), six single-donor-country
>     nulls (`G6.2`, two per fold), and the pooled all-country null at equal country mass (`G6.3`).
>     The existing line 4 names only the raked-donor bar. 🔴 **`FINDING 85`: the raked-donor null is
>     NOT the strongest of the three**, so a figure showing one comparison understates the test it is
>     drawing. The new line says how many and says they are all reported; **it states no result and
>     names no winner**, which Section 0 forbids.
>

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
token format and used to fine-tune **one** open-weight base language model with **one low-rank recipe,
applied once per held-out country**, which is then conditioned on each person of a separately
synthesised population to generate activity-resolved daily diaries for **any** country in the
framework — including the one held out of that fold's training entirely — and those diaries drive
European residential building energy models.

If a reader takes away only one thing, it should be: **one recipe, many countries, and the country being
generated was never seen in training.**

🔴 **Reworded 2026-08-19, from "one model, many countries, and one of those countries was never seen in
training".** With leave-one-country-out there is one base model and one recipe but **one adapter per
fold**, so "one model" overstates it — and "one of those countries" suggests a single permanent test
country, when in fact each takes the held-out role in turn. The claim being made is that **the method**
transfers, not that a single artefact does.

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

🔴 **THREE** coloured horizontal lanes emerge from Band 1 and run rightward, each a soft-tinted rounded
rectangle in the palette of Section 5. Each lane is **one country**, and they must be visually
identical in structure, because the point is that the pipeline treats every country the same way.
**Three, not four and not five — decision 16 excluded France on 2026-08-15. A fourth lane draws a
country the paper does not have.**

Inside **each** lane, left to right, three small steps joined by arrows:

1. A small national outline or a neutral flag-shaped placeholder tile. 🔴 **Use generic labels:
   "Country A", "Country B", "Country C". `Country D` is retired and must not appear.** Do not name
   real countries. **The corpus is settled at three, which is why there are exactly three lanes.**
   The lanes stay anonymous by editorial choice — see Section 7 item 2, whose original reason
   (decision 11, which country is held out) was closed and withdrawn.
2. `episode diary` with the sub-label `(duration, activity, location, co-presence)`.
   🔴 **`start` is deliberately absent.** Start time is the running sum of the durations and the model
   never emits it. Adding it back would misdescribe the record.
3. `serialised record` with the sub-label `conditioning prefix + day sequence`.

The lanes should visibly **converge** as they approach Band 3, narrowing toward the dark block, the way
several roads merge into one.

**One lane is different, and it is the third or lowest one.** Draw it with a **dashed outline** rather
than solid, and its country tile is labelled **"Country C — held out"**. Its arrow does **not** enter
the model block. Instead it passes underneath or around the dark block and re-enters on the right-hand
side of Band 4. A short caption beside it reads **"never seen in training"**.

🔴 **One line is added beneath that caption, 2026-08-19, and it is not optional:**
**`each country is held out in turn`**. Without it the figure states that one particular country is
permanently the test set, which is not the design — every country takes the held-out role in its own
fold, and the result reported in the paper is the rotation, not a single lucky split. **This line is
also what stops a reader asking why the anonymous lanes are anonymous: there is no hidden choice
left to guess.**

### Band 3 — the model (dark navy centre block, the visual anchor)

A single large rounded rectangle in dark navy, the same weight as the central block in the 3J figure.
Inside, stacked vertically:

* Title line, large, white text: 🔴 **"One open-weight LLM, one recipe per held-out country"**.
  **CHANGED 2026-08-19. It read `One open-weight LLM, fine-tuned once`, and that string is now
  forbidden.** The training is leave-one-country-out: one low-rank adapter per fold, each trained only
  on the countries that are not held out. `fine-tuned once` describes a single joint fine-tune, which
  would place the held-out country inside the training set and contradict the dashed lane drawn three
  centimetres to its left. **This is the largest text in the figure, so it is also the most expensive
  string in the figure to get wrong.**
* Below it, a simple abstract transformer motif: a small stack of three or four horizontal layer bars
  with an attention-style fan of thin connecting lines between two of them. Keep it schematic. Do not
  draw a brain, a robot, a chip, or a chat bubble.
* A small badge on the layer stack labelled **"low-rank adapter"**, connected by a thin line to the
  layer bars, to signal that only a small part is trained.
* Below the motif, three short lines of white text, one per line:
  * **"conditioned on: country, demographics, day type"**
  * 🔴 **"trained on: the other two"** — **CHANGED 2026-08-19, was `trained on: N-1 countries`.**
    With three lanes drawn, `N-1` invited a four-country reading and is retired. **No algebraic string
    remains anywhere in the figure.**
  * **"structure guaranteed at decoding"**

### Band 3b — the population track (a separate chain, drawn BELOW the navy block)

🔴 **This is the element added on 2026-08-14 and it is not optional.** In the previous version a single
strip labelled "survey weights + population marginals" ran along the bottom of the navy block, implying
that weighting happens inside the model. It does not. Weighting and representativeness are handled in a
separate, earlier, entirely conventional stage, and the figure has to show that.

Draw a **second, thinner horizontal chain running beneath the navy block**, in neutral grey so it reads
as supporting machinery rather than as a competing headline, with two boxes joined by an arrow:

1. `published population marginals` (small icon: a grid or a table)
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
`00` at the left end and `24` at the right end. 🔴 **THREE** such ribbons, one per lane (was four, before decision 16 excluded France), and they must be
**visibly different from each other**, because diversity is the point.

The dashed held-out lane re-joins here from below, and its ribbon is drawn with the same dashed outline
so the reader can trace it. Beside it, a small callout box, dashed border, containing:

* line 1: **"held-out country"**
* line 2: **"generated from published marginals only"**
* line 3: **"scored against published aggregate statistics"**
* line 4: **"compared against real diaries reweighted to the same marginals"**
* line 5: 🔴 **"three independent nulls, all reported"** — NEW 2026-08-22

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
* To the right of the buildings, a small vertical stack of 🔴 **three miniature schedule curves** (was four), each in
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
| Lane 3 (Country C, held out) | magenta or rose, **dashed outline** |
| 🔴 Lane 4 | **REMOVED 2026-08-19 — France was excluded, there is no fourth lane** |
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
* 🔴 `One Recipe, Many Countries: HETUS-Harmonised Time-Use Diaries for Building Energy Modelling`

🔴 **CORRECTED 2026-08-19, SECOND PASS — THIS WAS MISSED IN THE FIRST PASS OF THE SAME DAY.** The
subtitle read **`One Model, Many Countries: ...`**. That is the identical defect repaired in the navy
block on the same day, surviving in a second place: with leave-one-country-out there is one base model
and one recipe but **one adapter per fold**, so `One Model` overstates what is trained. The first pass
fixed the navy block title and the Section 1 takeaway line and **did not check the subtitle**, so the
image generated from that pass prints the corrected navy block **directly underneath the uncorrected
subtitle**, contradicting itself inside a single figure. **Lesson worth keeping: when a phrase is
retired, grep the whole prompt for it rather than fixing the occurrence you happen to be looking at.**

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

* `Country A`, `Country B`, `Country C — held out`
* `each country is held out in turn`
* `episode diary`
* `(duration, activity, location, co-presence)`
* `serialised record`
* `conditioning prefix + day sequence`
* `never seen in training`

Band 3:

* `One open-weight LLM, one recipe per held-out country`
* `low-rank adapter`
* `conditioned on: country, demographics, day type`
* `trained on: the other two`
* `structure guaranteed at decoding`

Band 3b:

* `published population marginals`
* `synthetic population`
* `iterative proportional fitting`
* `population and day are generated separately`

Band 4:

* `held-out country`
* `generated from published marginals only`
* `scored against published aggregate statistics`
* `compared against real diaries reweighted to the same marginals`
* `three independent nulls, all reported`
* `00` and `24` as the only axis labels on the activity ribbons

Band 5:

* `occupancy and activity-driven internal gains`
* `EnergyPlus schedules`
* `0` and `24` as the only axis labels on the schedule curves

🔴 **`N-1` WAS RETIRED ON 2026-08-19 AND MUST NOT APPEAR.** There is no algebraic string in the figure
any more. The words `the other two` replace it, permitted as a word-form count under the same exception
as `one wave per country`: a closed author decision, written as words and never as digits.

🔴 **STRINGS DELETED ON 2026-08-19. If any appears in the generated image, reject and regenerate —
they are the reason for this revision:**

* `One open-weight LLM, fine-tuned once` — contradicts the leave-one-country-out design drawn in the
  same figure
* `trained on: N-1 countries` — and `N-1` in any form
* `Country D`, and `Country D — held out` — France was excluded, the corpus is three countries
* 🔴 `One Model, Many Countries` — in the subtitle or anywhere else; it is `One Recipe, Many Countries`

🔴 **STRINGS DELETED ON 2026-08-22. Same rule: if any appears in the generated image, reject and
regenerate.**

* `conditioned on: country, demographics, season, day type` — and the word **`season`** in any
  conditioning line anywhere. `D-S2-19` dropped the stratum for all three countries.
* `census marginals` — replaced by `published population marginals`; two of three folds are not on a
  census basis (`D-S5-4 (b)`, `D-S5-5`, `FINDING 49`)

Also add, in Band 2 beside the dashed lane: `each country is held out in turn`.

🔴 **SCAFFOLDING LABELS ARE FORBIDDEN, added 2026-08-19 after the generator printed them.**
The band names in Section 3 are **instructions for the person composing the layout, not text to draw**.
The generated image printed the literal word **`TITLE`** above the title, and printed
**`BAND 1: Sources`, `BAND 2: Harmonisation & Serialisation`, `BAND 3: The Model`, `BAND 3b`,
`BAND 4: Generation`, `BAND 5: Buildings & Energy Schedules`** as visible column headers. **None of
these is in Section 6 and none may appear.** The bands are meant to be read from the layout itself —
a reader does not need to be told that the left column is the left column. If a heading feels needed
above a band, it must first be added to Section 6; until then there is none.

---

## 7. Explicit do-nots

1. **No invented numbers.** See Section 0 and Section 6.
2. **No real country names and no real flags.** 🔴 **The stated reason expired on 2026-08-19 and the
   rule is kept anyway — read this before assuming it still means what it said.** It read: the corpus
   is four HETUS countries but *which one is held out is not decided*, so a named lane would let a
   reader guess. **Both halves are now false.** The corpus is **three** countries (decision 16 excluded
   France) and **every one of them is held out in turn**, so there is no undecided choice to leak. The
   rule survives on a different and weaker footing: anonymous lanes keep the abstract about the method
   rather than about three particular national statistical offices, and they let the same figure stand
   if a country is ever added or dropped. **This is now an editorial preference, not a constraint, and
   the author may lift it by editing this one item. It is flagged so the decision is made knowingly
   rather than inherited.**
3. **No named model** — no `OLMo`, no `Gemma`, no `Llama`, no `Qwen`, no parameter count. 🔴 **The
   reason changed on 2026-08-14 and the rule did not.** The backbone is now decided
   (`allenai/Olmo-3-1025-7B`, settled by our own measurement), so this is no longer "the model is not
   chosen". It is that **the figure's claim is architectural — *one* open-weight base model and *one*
   recipe — and naming a checkpoint dates the figure without strengthening the claim.** 🔴 **The words
   `fine-tuned once` were removed from this rationale on 2026-08-19 along with the title string itself:
   the recipe is applied once per fold, not once in total.** If the author wants
   the checkpoint visible, it belongs in the figure *caption*, which is text and can be corrected,
   never inside the navy block.
4. **No institutional logos** for Eurostat, statistical institutes, universities or model developers.
5. **No brain, robot, android, glowing orb, neural-network-as-constellation, or chat bubble.** This is a
   method diagram in a building-science journal, not an AI illustration.
6. **No 3D perspective, no drop shadows, no gradients on text.** Flat vector style, as in the 3J figure.
7. **No rotated text.**
8. **No decorative arrows that do not carry data.** Every arrow in the figure means something flows.
9. **No results.** No bars, no scatter, no confusion matrix, no metric callouts. The only chart-like
   elements permitted are the three activity ribbons and the three schedule curves, and both are
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
6c. 🔴 **Added 2026-08-19, and these four are what this revision exists for. Any one of them failing
   means regenerate, not accept:**
   * The navy block title reads **`One open-weight LLM, one recipe per held-out country`**. If it reads
     `fine-tuned once`, the figure contradicts its own dashed lane and must be regenerated.
   * There are **exactly three country lanes**, and **`Country D` appears nowhere**.
   * The model block reads **`trained on: the other two`**. **`N-1` appears nowhere.**
   * The line **`each country is held out in turn`** is present beside the dashed lane.
7b. 🔴 **Check these strings character by character rather than reading the image for general
   correctness.** A generated figure that looks entirely right and says `fine-tuned once` is the exact
   failure being repaired here, and it is the kind a quick glance passes.

---

## 9. RESULT OF THE FIRST GENERATION FROM THIS REVISION — 2026-08-19

The author generated `HETUS_LLM_CrossNational_Pipeline.png` and it was checked string by string
against Section 6.

**What came out correct, and must not regress:**

* The navy block reads **`One open-weight LLM, one recipe per held-out country`** and
  **`trained on: the other two`**. **`N-1` and `fine-tuned once` are gone from the block.**
* **Three lanes**, `Country A`, `Country B`, `Country C — held out`. No `Country D`.
* `each country is held out in turn` is drawn beside the dashed lane, as required.
* The dashed lane bypasses the navy block and re-enters at Band 4. The population chain runs **below**
  the block with its arrow turning up into Band 4 — the two checks in Section 8 items 4 and 5 that
  matter most, both PASS.
* `start` is absent from the episode tuple. Band 1 is a single card, not a stack. Three ribbons, three
  schedule curves, `00`/`24` and `0`/`24` as the only axis labels. No year, no model name, no metric.

🔴 **Two defects. The first is mine, not the generator's.**

1. 🔴 **THE SUBTITLE STILL READS `One Model, Many Countries`.** The figure therefore prints, in its
   second line, the exact claim that the navy block three centimetres below it was corrected to stop
   making. **The generator did nothing wrong: it drew what Section 6 told it to draw.** The first pass
   of 2026-08-19 corrected the navy block title and the Section 1 takeaway and never checked the
   Section 6 subtitle. Section 6 now reads `One Recipe, Many Countries: ...` and the old string is on
   the rejection list. **The transferable lesson is in Section 6: when a phrase is retired, grep the
   prompt for it — do not fix the occurrence you happen to be looking at.**
2. **Scaffolding headings were printed**: the literal word `TITLE` above the title, and
   `BAND 1: Sources`, `BAND 2: Harmonisation & Serialisation`, `BAND 3: The Model`, `BAND 3b`,
   `BAND 4: Generation`, `BAND 5: Buildings & Energy Schedules` as visible column headers. None is in
   Section 6. The band structure is meant to be read from the layout, not labelled.

**For the next generation, add this line to the end of the prompt:**

```
The subtitle is exactly: One Recipe, Many Countries: HETUS-Harmonised Time-Use Diaries for Building
Energy Modelling. Do not write "One Model, Many Countries". Do not print the word TITLE anywhere. Do
not print band headings such as BAND 1: Sources, BAND 2, BAND 3, BAND 3b, BAND 4 or BAND 5 — the
bands are read from the layout and carry no headings of their own.
```

---

## 10. PASTE-READY PROMPT (Gemini / Antigravity) — added 2026-08-19, second pass

🔴 **A rendering of Sections 0 to 8, not a second specification.** If the two ever disagree, Sections 0
to 8 win and this block is rewritten from them. **It is written to be self-contained: every correction
of 2026-08-19 AND 2026-08-22 is inside the block, not appended after it.** 🔴 **Updated 2026-08-22 —
paste this block, not the 2026-08-19 one: `season` is struck, `census marginals` is replaced, and the
held-out callout has four lines.**

```
Create a flat vector method diagram, landscape orientation, about 2000 x 1100 pixels, on a white
background, in one clean sans-serif family.

READ THIS FIRST. Everything below describes what to DRAW. Words like "band", "column", "lane" and
"block" are layout instructions for you, not text to put in the picture. Draw NO headings, NO section
labels and NO captions of any kind except the exact strings listed under QUOTED TEXT. Do not write the
word TITLE. Do not write BAND, or BAND 1, or any heading naming a part of the layout. All text is
horizontal; nothing is rotated or vertical anywhere.

At the very top, centred, exactly two lines of text with nothing above them:
  Cross-National Occupancy Generation with a Fine-Tuned Open-Weight LLM
  One Recipe, Many Countries: HETUS-Harmonised Time-Use Diaries for Building Energy Modelling
The second line reads "One Recipe". Do not write "One Model, Many Countries".

STRUCTURE, left to right: a narrow light grey panel of source cards; then three coloured horizontal
lanes that converge rightward; then one large dark navy block; then the generation area; then
buildings and small schedule curves at the right edge. A separate short chain runs BELOW the navy
block. No headings label any of these areas.

LEFT PANEL, three stacked cards, each with a simple flat icon:
  a calendar or clipboard icon, bold label "National time-use surveys", beneath it
    "household + individual + diary files" and "one harmonised survey round per country"
    Draw this as ONE card. Do not draw stacked or offset copies behind it.
  a document icon, bold label "HETUS framework", beneath it
    "common diary structure, common activity coding list, common location and co-presence fields"
  a people icon, bold label "Census and population marginals", beneath it
    "household composition, age, employment"
At the foot of the panel, one small line: "Harmonised European Time Use Surveys"

THREE LANES, and exactly three. Each is a soft-tinted rounded strip, identical in structure to the
others, because the pipeline treats every country the same way. In each lane, left to right: a small
neutral country tile, then "episode diary" with "(duration, activity, location, co-presence)" beneath
it, then "serialised record" with "conditioning prefix + day sequence" beneath it. The word "start"
must not appear: the tuple has no start field.
  lane one, teal, tile reads "Country A"
  lane two, orange, tile reads "Country B"
  lane three, magenta or rose, DASHED outline, tile reads "Country C - held out"
The first two lanes converge into the navy block. The third does NOT enter it: its dashed arrow passes
under or around the block and re-enters on the right, in the generation area. Beside that dashed lane
write two small lines:
  each country is held out in turn
  never seen in training
Draw no fourth lane and write no "Country D".

THE DARK NAVY BLOCK, the visual anchor, with white text inside:
  large title line: One open-weight LLM, one recipe per held-out country
  below it a small schematic transformer motif, three or four stacked horizontal layer bars with a
  thin fan of connecting lines between two of them, and a small badge on the stack reading
  "low-rank adapter" joined to the bars by a thin line. Keep it abstract: no brain, no robot, no chip,
  no chat bubble.
  then three short lines:
    conditioned on: country, demographics, day type
    trained on: the other two
    structure guaranteed at decoding
Do not write "fine-tuned once". Do not write N-1.

THE CHAIN BELOW THE NAVY BLOCK, clearly outside it: "published population marginals" with an arrow to
"synthetic population", labelled "iterative proportional fitting", and its arrow then turns UP into
the generation area on the right. It must not enter the navy block. Beneath it one small line:
  population and day are generated separately

THE GENERATION AREA, right of the navy block: three thin horizontal stacked activity ribbons, one per
lane colour, each made of twenty to thirty coloured segments of unequal width, each labelled 00 at its
left end and 24 at its right end, and the three visibly different from one another. The third ribbon
has a dashed outline in the held-out lane's colour. Beside it, a dashed-outline box headed
"held-out country" containing four lines:
  generated from published marginals only
  scored against published aggregate statistics
  compared against real diaries reweighted to the same marginals
  three independent nulls, all reported

THE RIGHT EDGE: a flat row of three or four European residential building types, side by side, and
beneath them three small line-plot schedule curves in the three lane colours, each in a small white
box with 0 at the left and 24 at the right of its x axis and no y axis numbers, the three shapes
visibly different. Beneath them two lines:
  occupancy and activity-driven internal gains
  EnergyPlus schedules

QUOTED TEXT. The picture contains the two title lines and the strings named above, and nothing else.
In particular: write no number anywhere except 00, 24, 0 and 24 as the axis end labels. Write no
percentage, accuracy, metric, country count, year or parameter count. Write no real country name and
draw no flag. Write no model name such as OLMo, Gemma, Llama, Qwen or Mistral. Write no headings.

STYLE. Flat vector only: no 3D, no perspective, no drop shadows, no gradients on text. No logos. No
results, no bar charts, no scatter plots, no confusion matrices, no metric callouts; the ribbons and
the curves are illustrative shapes, not plotted data. No time axis, no years, no forecast arrow. Every
arrow must mean that something flows. Every line must stay legible at single-column print width.
```

### 10.1 What to check the moment the image comes back

1. The subtitle reads **`One Recipe, Many Countries`**, not `One Model`.
2. The words `TITLE`, `BAND`, and any `BAND n:` heading appear **nowhere**.
3. The navy block reads `One open-weight LLM, one recipe per held-out country` and
   `trained on: the other two`. No `fine-tuned once`, no `N-1`.
4. **Three lanes**, no `Country D`; the third is dashed, bypasses the navy block, and carries
   `each country is held out in turn`.
5. The population chain runs **below** the navy block and turns up into the generation area — if it
   enters the block, the figure says we trained on census marginals, which is false.
6. `start` is absent from the episode tuple; the source card is single, not stacked.

### 10.2 What to check on the 2026-08-22 regeneration, in addition to 10.1

7. 🔴 The navy block's first small line reads **`conditioned on: country, demographics, day type`**.
   **The word `season` appears nowhere in the image.** This is the item this revision exists for.
8. The grey chain below the navy block starts at **`published population marginals`**, not
   `census marginals`.
9. The dashed held-out callout has **four** lines, the fourth being
   **`three independent nulls, all reported`**. If the generator drops a line to fit the box, it is the
   box that grows, not the list that shrinks — the same rule Section 3 already gives for line 4.
10. Everything in 10.1 still holds. 🔴 **Check it again rather than assuming it survived**: the
    2026-08-19 generation was correct on all six of those points and this revision touches none of
    them, so any regression there is the generator re-drawing from scratch, not a prompt change.
