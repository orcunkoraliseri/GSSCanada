# Image prompt — 4J pipeline steps figure (Steps 0 to 9)

**Deliverable:** one raster image, `HETUS_LLM_Pipeline_Steps.png`, generated **by the author** in their
own image tool. This file is the prompt. It is written so the image can be produced without asking a
follow-up question.

**Install path once generated:** `4J_docs_occ/writing/submission/figures/`
**Source of truth for the content:** `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md`, the ASCII
box diagram, Steps 0 to 9, reconciled against the project state on 2026-08-19.

> 🔴 **Revised 2026-08-14. The installed image is out of date and must be regenerated from this file.**
> Author decision 6 fixed the corpus at **one wave per country**, which retired two strings the
> installed figure still shows: Step 1's `several waves per country` / `how many waves earn their
> place`, and Step 2's `pooling level across waves` — cross-wave pooling cannot be an open question
> when there is one wave. Step 2's open line is now the **shared day origin** (decision D-S2-1), which
> is the question that actually blocks that step. Sections 4, 6, 9 and 10 carry the change.

> 🔴 **REVISED AGAIN 2026-08-19. The installed image is out of date a second time, and this revision
> is larger than the last one. Regenerate.** Between 2026-08-14 and now, Steps 1, 2 and 3 were closed
> and gate-validated, Step 4 began running, and **decision 16 excluded France**. Four defects in the
> installed figure, in descending order of how much damage they do:
>
> 1. 🔴 **Step 4 says `all countries trained jointly`. That is no longer the design and it describes a
>    weaker experiment than the one being run.** Since decision 16 the training is
>    **leave-one-country-out**: one adapter per held-out country, each trained on the others only. Joint
>    training would put the held-out country in the training set and destroy the Step 6 claim. A
>    reviewer reading the installed figure would conclude the transfer test is contaminated.
> 2. 🔴 **`N-1` reads as "three of four".** France is out; the corpus is three countries and each fold
>    trains on **two**. `N-1` is retired and replaced by the words `the other two`. It is no longer the
>    figure's only algebraic string — there is now no algebraic string at all.
> 3. **Steps 1 and 2 are shown `open`. Both are closed and gate-validated**, and their open lines are
>    both false: the countries not yet held are not being acquired (France was excluded, not deferred),
>    and the shared day origin was ruled (D-S2-5). Step 3 is shown `decided` but is built and validated.
> 4. **Step 4's open line `which model family` is closed.** The backbone was chosen by our own
>    measurement.
>
> Two structural changes follow from this, in Sections 4 and 5: a **fourth state chip** (`validated`),
> because the three-chip vocabulary can no longer tell "agreed on paper" from "built and shown to
> survive its own gate battery"; and a **sixth validation tile** covering Steps 1 to 4, because the
> installed figure implies validation begins at Step 6 when in fact every step from 1 onward ran a
> pre-declared gate battery. Sections 4, 5, 6, 7, 9 and 10 all carry the change.

> **Target generator, 2026-08-19: Gemini / Antigravity.** Section 11 is a condensed paste-ready
> version of this specification for a single-prompt image tool. **Sections 0 to 10 remain the source of
> truth** — Section 11 is a rendering of them, and if the two ever disagree, Sections 0 to 10 win and
> Section 11 is rewritten from them.

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

> 🔴 **NO NUMBER MAY APPEAR IN THIS IMAGE EXCEPT THE STEP NUMBERS 0 TO 9.**
> 🔴 **`N-1` is retired as of 2026-08-19 and must not appear.** France was excluded by decision 16, so
> each fold trains on **two** countries, and `N-1` printed next to a four-country reading is simply
> wrong. It is replaced by the words `the other two`. There is now no algebraic string in the figure.
>
> Paper 4 has produced **no reportable transfer results** — Step 6 has not been run. Every threshold,
> accuracy, token count, model size and year in it is either unmeasured or a target rather than an
> outcome. A figure that shows a plausible-looking `0.015`, `7B` or `2010` will be read as a settled
> fact, and several of those are exactly the values still open. 🔴 **This ban did not weaken because
> Steps 1 to 4 now have results.** Those results are gate outcomes, not the claim of the paper, and a
> corpus size or a gate count in this figure would be read as a transfer result.
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

The second thing, which the figure must not obscure: **the steps are not all in the same state.** The
figure distinguishes four states, and as of 2026-08-19 the front half of the pipeline is built while
the claim itself has not been tested. 🔴 **The figure must not let a reader mistake "the corpus and the
adapter exist" for "the transfer test passed".** Steps 1 to 3 are built and gate-validated, Step 4 is
running, and **Step 6 — the step the whole diagram exists for — has not been run.**

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
* The **right gutter** carries **six** small tiles, one per validation tier, each connected by a thin
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
* The **state chip** sits at the right edge of the card and is one of exactly **four**:
  * `cleared` — solid fill, checkmark glyph
  * `validated` — solid fill, **double-checkmark glyph** — 🔴 **new on 2026-08-19**
  * `decided` — solid fill, no glyph
  * `open` — **hollow outline only, no fill**
  Use fill weight and glyph, not colour alone, to separate them. A colour-blind reader must be able to
  tell an open step from a decided one, and a decided one from a validated one.

🔴 **Why a fourth chip was added, because it is the substantive change in this revision.** The old
three-chip vocabulary could only say whether a step had been *agreed*. It had no way to say that a step
had been *built and then shown to survive a pre-declared gate battery in which every gate was seen
failing on a deliberately broken control*. That distinction is this project's central methodological
claim — it is what the dashed caption in Section 5 asserts — and a figure that collapses `decided` and
`validated` into one chip throws it away. **`decided` now means agreed on paper and not yet built.
`validated` means built, and its gate battery ran and was seen to fail on purpose before it was
trusted.**

The cards, top to bottom, with the exact text each carries:

| # | Title | Decision line | Open line | State |
|---|---|---|---|---|
| 0 | `Feasibility gate` | `data reachable, prior art clear, method justified, release limits known` | — | `cleared` |
| 1 | `Corpus` | `national time-use series, one wave per country` | — | `validated` |
| 2 | `Harmonisation` | `common activity, location and co-presence coding, shared day origin` | — | `validated` |
| 3 | `Serialisation` | `episode form: duration, activity, location, co-presence` | — | `validated` |
| 4 | `Fine-tuning` | `open-weight base model, low-rank adapter, one adapter per held-out country` | — | `decided` |
| 5 | `Population linkage` | `synthetic population first, then one generated day per person` | — | `decided` |
| 6 | `Transfer test` | `train on the other two, generate the held-out one from published marginals` | `the scoring basis where survey and published wave differ` | `open` |
| 7 | `Constrained generation` | `well-formed diaries guaranteed at decoding` | — | `decided` |
| 8 | `Building simulation` | `European residential archetypes, uninjected control run first` | `archetype models built from published parameter tables` | `open` |
| 9 | `End-use loads` | `published activity-to-appliance mappings, adapted not authored` | — | `open` |

🔴 **CHANGED 2026-08-19 — READ THIS BEFORE COPYING THE TABLE.** Five rows moved and the reasons are
not cosmetic:

* **Step 4's decision line is the important one.** It read `all countries trained jointly`. It now
  reads **`one adapter per held-out country`**. Joint training over all countries would place the
  held-out country inside the training set, which is precisely what Step 6 must exclude; the old string
  described a contaminated experiment that the project is not running. **If only one line of this
  revision is carried into the image, it is this one.** Step 4's open line `which model family` is
  deleted: the backbone was chosen by our own measurement.
* **Step 6's decision line** no longer says `N-1`. With France excluded there are three countries and
  each fold trains on **two**, so `N-1` invites a four-country reading. Its open line
  `which country is held out` is deleted — **all three are held out in rotation**, that is the design,
  not an open question. What is genuinely open is the **scoring basis**: for one country the published
  aggregate wave and the survey we hold are different years, and that is unruled.
* **Steps 1, 2 and 3 are `validated`, not `open` or `decided`.** The corpus is fixed, harmonisation is
  built and its day origin is ruled, the serialised corpus exists, and each of the three passed a
  pre-declared gate battery in which the gates were seen failing before they were trusted. Step 1's old
  open line — acquisition outstanding — is **false and must be deleted**: the missing country was
  **excluded by decision, not deferred**, and leaving the line in advertises an intention the project
  has abandoned.
* **Step 4 stays `decided`, deliberately, and must not be drawn as `validated`.** Its training is under
  way and its gate battery is not complete. Promoting it would be the exact error Section 1 warns
  against.

🔴 **Card 6 is drawn larger than the others** and carries one extra line, in bold, beneath its decision
line:

* `the bar: beat real diaries from the other countries, reweighted to the held-out country`

🔴 **Card 6 must remain `open`, and the figure must not let the built front half imply the claim is
settled.** Steps 1 to 3 carry the strongest state chip in the figure while Step 6 — the largest card,
the one the diagram is built around — carries the weakest. **That contrast is the honest state of the
project on 2026-08-19 and it is intended. Do not soften it.**

This is the falsifiable claim of the paper and it is the single most important sentence in the figure.
If the layout is tight, shrink cards 8 and 9 rather than this line.

---

## 5. The validation tiers (right gutter)

**Six** small tiles, stacked, each joined by a thin horizontal line to the step or steps it guards.
Tiles are visually lighter than the step cards so the spine stays dominant.

| Tile label | Connects to |
|---|---|
| `pre-declared gate batteries` | **Steps 1, 2, 3 and 4** — 🔴 **new on 2026-08-19** |
| `distributional fidelity` | Step 6 |
| `collapse and memorisation` | Step 6 |
| `structural validity` | Step 7 |
| `transfer margin` | Step 6 |
| `downstream energy` | Steps 8 and 9 |

🔴 **Why the new tile was added.** The installed figure attaches no validation to Steps 1 to 5, which
tells the reader that checking begins at the transfer test. **That is false, and it undersells the
part of the work that is finished.** Every step from 1 onward ran a battery of gates fixed in advance,
each gate demonstrated failing on a deliberately broken input before its passing result was accepted.
The new tile spans Steps 1 to 4 with a single bracket rather than four separate lines, so the gutter
does not become a second spine.

Below the tiles, one small caption in a dashed-border box:

* `every tier is first shown failing on a deliberately broken control`

🔴 **This caption is not decoration.** A validation battery that has never been seen to fail has not
been shown to work, and it is the practice this project runs on. Keep it even if the gutter is crowded.
**As of 2026-08-19 the caption is no longer only an intention for the lower half of the figure — it is
a description of what has already happened in Steps 1 to 4**, which is exactly why those steps now
carry a tier of their own.

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
* `national time-use series, one wave per country`
* `common activity, location and co-presence coding, shared day origin`
* `episode form: duration, activity, location, co-presence`
* `open-weight base model, low-rank adapter, one adapter per held-out country`
* `synthetic population first, then one generated day per person`
* `train on the other two, generate the held-out one from published marginals`
* `the scoring basis where survey and published wave differ`
* `the bar: beat real diaries from the other countries, reweighted to the held-out country`
* `well-formed diaries guaranteed at decoding`
* `European residential archetypes, uninjected control run first`
* `archetype models built from published parameter tables`
* `published activity-to-appliance mappings, adapted not authored`

State chips:

* `cleared`, `validated`, `decided`, `open`

Validation tiles:

* `pre-declared gate batteries`, `distributional fidelity`, `collapse and memorisation`,
  `structural validity`, `transfer margin`, `downstream energy`
* `every tier is first shown failing on a deliberately broken control`

🔴 **FOUR STRINGS WERE DELETED ON 2026-08-19 AND ARE NOW FORBIDDEN. If any of them appears in the
generated image, the image is rejected and regenerated — they are the reason for this revision:**

* `all countries trained jointly` — describes a contaminated experiment the project is not running
* `N-1` — France was excluded, so each fold trains on two countries; the string invites a
  four-country reading and **no algebraic string remains in the figure**
* `acquisition outstanding for the countries not yet held` — the missing country was excluded by
  decision, not deferred; the line advertises an abandoned intention
* `which model family` and `which country is held out` — both closed; the second is not merely closed
  but was never really open, since all three countries are held out in rotation

**The word-form counts `one wave per country` and `the other two` are permitted**, under the same
exception as Section 9 item 1: they are closed author decisions, written as words and never as digits.

🔴 **SCAFFOLDING LABELS ARE FORBIDDEN, added 2026-08-19 after the generator printed them.**
The column names in Section 2 are **instructions for whoever composes the layout, not text to draw**.
The generated image printed **`LEFT COLUMN`, `CARDS & STATE CHIPS`, `RIGHT COLUMN`** as visible
headings across the top, and the version before it printed `LEFT COLUMN`, `CENTER COLUMN`,
`VALIDATION TIER`. **None of these is in Section 6 and none may appear.** A reader does not need to be
told that the left column is on the left; the phase bands and the tier tiles already say what each
column is.

🔴 **THE STEP DIGITS IN THE PHASE BANDS ARE ALSO FORBIDDEN.** The generated image repeated `0`, `1`,
`2`, `3`, `4`, `5`, `6-7`, `8-9` down the left gutter inside the phase bands. Section 6 permits the
digits `0` to `9` **only inside the number chips on the cards**, and `6-7` / `8-9` are ranges, which
are not permitted strings at all. **The bands span their steps visually; they must not be numbered.**

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
| State chip `cleared` / `validated` / `decided` | solid dark navy |
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

1. **No invented numbers.** Step numbers `0` to `9` are the entire permitted set — 🔴 **`N-1` was
   removed on 2026-08-19 and is now forbidden.** No thresholds, no percentages, no token counts, no
   country counts, no gate counts, no corpus sizes, no model sizes.
   🔴 **Two exceptions, both closed author decisions written as words and never as digits: the phrase
   `one wave per country` (added 2026-08-14) and the phrase `the other two` (added 2026-08-19).** They
   appear only inside the Step 1 and Step 6 body lines in Section 6. The ban still covers every other
   count, including the number of countries.
2. **No real country names and no real flags.** 🔴 **The stated reason for this rule expired on
   2026-08-19 — the corpus IS final (three countries, France excluded by decision 16) — but the rule is
   kept.** Naming the countries would put the figure's most volatile content into a diagram whose job
   is to show *stages*, and the graphical abstract already carries the country story. **This is now a
   deliberate editorial choice rather than a constraint, and the author may lift it by editing this one
   item; it is flagged here so the decision is made knowingly and not inherited by accident.**
3. **No named model** — no `Gemma`, no `Llama`, no `Qwen`, no `Mistral`, no `OLMo`, no parameter count.
   🔴 **Also now a choice rather than a constraint: the backbone WAS decided, by our own measurement,
   so `which model family` is deleted from Step 4's card.** The ban is kept because a figure that names
   a backbone dates faster than one that does not, and because the paper's claim does not depend on
   which open-weight model was used. Lift it only if a reviewer asks.
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
   that is not in Section 6 is a defect and is reported, not silently accepted. 🔴 **Reject on sight,
   2026-08-19 list: `all countries trained jointly`, `N-1`, `acquisition outstanding for the countries
   not yet held`, `which model family`, `which country is held out`** — the installed
   `HETUS_LLM_Pipeline_Steps.png` carries all five, and they are why this figure is being regenerated.
   Also still rejected from the previous round: `several waves per country`, `how many waves earn their
   place`, `pooling level across waves`.
4. 🔴 **Check the state chips one by one against this list, which changed on 2026-08-19:** Step 0
   `cleared`; **Steps 1, 2 and 3 `validated`**; Steps 4, 5 and 7 `decided`; Steps 6, 8 and 9 `open`.
   **Two failure directions, and both are defects.** Showing Steps 1 to 3 as `open` understates finished,
   gate-validated work. Showing **Step 4 or Step 6 as `validated`** overstates the project's position —
   Step 4 is still training and **Step 6 has not been run at all** — and that error is the more serious
   of the two, because Step 6 is the claim.
5. Check that Step 6 is the largest card, carries its bold bar line, and **still carries the hollow
   `open` chip** despite being the visual centre of the figure.
6. Check that no year, no threshold value, no model name, no country name and no count in digits appears
   anywhere; and that the only two word-form counts are `one wave per country` and `the other two`.
7. Check that the sixth validation tile `pre-declared gate batteries` is present and brackets Steps 1
   to 4.
8. Check legibility at full page width in print before it is accepted.
9. 🔴 **If the plan document changes, this prompt changes first and the image is regenerated from it.**
   The Section 4 table is a copy of the Overview's step list, and a copy that drifts from its source is
   worse than no figure.

---

## 11. PASTE-READY PROMPT (Gemini / Antigravity) — added 2026-08-19

🔴 **This section is a rendering of Sections 0 to 10, not a second specification.** Paste it as a
single prompt. If it ever disagrees with the sections above, the sections above win and this one is
rewritten from them. **Do not edit this section without editing its source.**

```
Create a flat vector process diagram, portrait orientation, about 1400 x 1900 pixels, on a white
background, in one clean sans-serif family.

READ THIS FIRST. Everything below describes what to DRAW. Words like "column", "gutter", "spine",
"band" and "tile" are layout instructions for you, not text to put in the picture. Draw NO headings,
NO section labels and NO captions of any kind except the exact strings listed under QUOTED TEXT.
Nothing that names a part of the layout may appear in the image.

ALL TEXT IS HORIZONTAL. Nothing is rotated, sideways or vertical anywhere in the image, including the
four tinted bars down the left side. Their labels DATA, MODEL, CLAIM and ENERGY are written
horizontally, reading left to right, like every other word in the picture. This is the single most
important formatting rule here.

At the very top, centred, exactly two lines of text with nothing above them:
  From Harmonised Time-Use Surveys to Simulated Building Energy
  The ten steps of the cross-national occupancy pipeline

STRUCTURE. Down the centre runs a single vertical column of ten rounded rectangular cards, numbered 0
at the top to 9 at the bottom, each joined to the next by one short downward arrow. Along the left
edge, four tall tinted rounded bars sit beside the cards they group. Along the right edge, six small
pale tiles each connect to the cards they guard by one thin horizontal line. Those tier lines are the
only horizontal connectors in the picture; every other arrow points down.

THE FOUR TINTED BARS ON THE LEFT, labelled horizontally, each spanning the cards named:
  DATA   beside cards 0, 1 and 2, light grey
  MODEL  beside cards 3, 4 and 5, soft teal
  CLAIM  beside cards 6 and 7, soft dark navy, the strongest tint of the four and slightly wider
  ENERGY beside cards 8 and 9, soft orange
Write only those four words on them. Put NO digits and NO number ranges on these bars.

EACH CARD carries, left to right: a small filled circle holding the card's digit, then a bold title,
then one to three body lines in smaller regular type, then a small chip at the right edge. The chips
are drawn four ways, distinguished by fill and by glyph rather than by colour:
  cleared    solid dark navy fill, white text, one checkmark
  validated  solid dark navy fill, white text, two checkmarks
  decided    solid dark navy fill, white text, no glyph
  open       white fill, navy outline, navy text, no glyph

THE TEN CARDS, with the exact wording of every line:

circle 0, title Feasibility gate, chip cleared
  data reachable, prior art clear, method justified, release limits known
circle 1, title Corpus, chip validated
  national time-use series, one wave per country
circle 2, title Harmonisation, chip validated
  common activity, location and co-presence coding, shared day origin
circle 3, title Serialisation, chip validated
  episode form: duration, activity, location, co-presence
circle 4, title Fine-tuning, chip decided
  open-weight base model, low-rank adapter, one adapter per held-out country
circle 5, title Population linkage, chip decided
  synthetic population first, then one generated day per person
circle 6, title Transfer test, chip open
  train on the other two, generate the held-out one from published marginals
  the bar: beat real diaries from the other countries, reweighted to the held-out country
  the scoring basis where survey and published wave differ
circle 7, title Constrained generation, chip decided
  well-formed diaries guaranteed at decoding
circle 8, title Building simulation, chip open
  European residential archetypes, uninjected control run first
  archetype models built from published parameter tables
circle 9, title End-use loads, chip open
  published activity-to-appliance mappings, adapted not authored

CARD 6 IS THE CENTREPIECE. Draw it noticeably larger than every other card, with a very light navy
fill and a thicker border. Its middle line, the one beginning "the bar:", is BOLD, and it is the only
bold body line in the whole picture. Card 6 nevertheless keeps the hollow white "open" chip. If space
runs short, shrink cards 8 and 9 rather than that bold line.

THE SIX PALE TILES ON THE RIGHT, each with its thin connecting line:
  pre-declared gate batteries   joined by ONE bracket that spans cards 1, 2, 3 and 4 together,
                                reaching from card 1 down to card 4, not stopping at card 2
  distributional fidelity       to card 6
  collapse and memorisation     to card 6
  transfer margin               to card 6
  structural validity           to card 7
  downstream energy             to cards 8 and 9 together
Beneath the tiles, one small line inside a dashed-outline box:
  every tier is first shown failing on a deliberately broken control

QUOTED TEXT. The image contains the two title lines, the four bar labels, the digits 0 to 9 inside the
ten circles, the ten card titles, the card body lines, the four chip words, the six tile labels, and
the dashed-box line. Nothing else. In particular:
  Write no other heading, label or caption of any kind.
  Write no number anywhere except the digits 0 to 9 inside the circles. No ranges such as 6-7 or 8-9.
  Write no percentage, threshold, accuracy, token count, corpus size, model size, year or date.
  Do not write N-1 or any algebraic expression.
  Do not write any of: all countries trained jointly; acquisition outstanding for the countries not
  yet held; which model family; which country is held out; several waves per country; how many waves
  earn their place; pooling level across waves.
  The only counts written as words are "one wave per country" and "the other two", both required.
  No country names and no flags. No model names such as Gemma, Llama, Qwen, Mistral or OLMo.

STYLE. Flat vector only: no 3D, no perspective, no drop shadows, no gradients on text. No logos. No
brain, robot, android, glowing orb or chat bubble. No loop-back arrows, no feedback cycles, no
iteration loops, since the steps run once in order. No time axis, no years, no forecast arrow. Nothing
suggesting the trained model is released: no download icon, no repository mark, no open-weights badge.
Do not rely on red and green as the only pair distinguishing anything. Every line must stay legible
when the picture is printed at full page width.
```

### 11.1 What to check the moment the image comes back

Run Section 10 in full before installing. These four are the ones this revision exists for, and any
one of them failing means regenerate rather than accept:

1. Step 4 reads **`one adapter per held-out country`**, never `all countries trained jointly`.
2. **`N-1` appears nowhere.**
3. Steps 1, 2 and 3 carry **`validated`**; Steps 4, 5 and 7 carry `decided`; Steps 6, 8 and 9 carry
   the hollow **`open`** chip.
4. The sixth tile **`pre-declared gate batteries`** is present and brackets Steps 1 to 4.

🔴 **Generators drop or merge tiles and chips when the gutter is crowded, and they silently
re-word body lines that are long.** Check the strings character by character against Section 6 rather
than reading the image for general correctness — a figure that looks right and says
`all countries trained jointly` is the exact failure this revision is repairing.

---

## 12. RESULT OF THE FIRST GENERATION FROM THIS REVISION — 2026-08-19

The author generated `HETUS_LLM_Pipeline_Steps.png` from Section 11 and it was checked string by
string against Sections 6 and 10. **All four items in Section 11.1 PASS.** Recorded here so the next
round starts from what is already right rather than re-deriving it.

**What came out correct, and must not regress:**

* Step 4 reads `open-weight base model, low-rank adapter, one adapter per held-out country`. **The
  defect this whole revision existed for is gone.**
* `N-1` appears nowhere; Step 6 reads `train on the other two, generate the held-out one from
  published marginals`.
* State chips are exactly right: `0` cleared; `1`, `2`, `3` validated with a double check; `4`, `5`,
  `7` decided; `6`, `8`, `9` hollow open. **Step 6 is the largest card and still carries the hollow
  chip**, which is the contrast Section 4 asks for and the one most likely to be lost.
* The sixth tile `pre-declared gate batteries` is present. The dashed caption is present.
* No year, no threshold, no model name, no country name.

🔴 **Four defects, none fatal, all fixable in one more generation:**

1. 🔴 **The phase band labels `DATA`, `MODEL`, `CLAIM`, `ENERGY` are drawn ROTATED, reading bottom to
   top.** Section 8 bans this explicitly and by name — *"All text horizontal. No rotated text
   anywhere, including the phase band labels. The 3J figure's rotated block was the hardest element to
   read at journal scale and it is not repeated."* **The generator repeated it anyway.** This is the
   one defect that costs the reader something real at print size, and it is the first to fix.
2. 🔴 **The `pre-declared gate batteries` bracket spans only Steps 1 and 2.** Section 5 requires it to
   bracket **Steps 1, 2, 3 and 4**. As drawn, the figure says Serialisation and Fine-tuning have no
   gate battery, which is false — Step 3's battery is the largest in the project so far.
3. **Three scaffolding headings were printed** — `LEFT COLUMN`, `CARDS & STATE CHIPS`, `RIGHT
   COLUMN` — and **the step digits were repeated down the phase bands** as `0`,`1`,`2`,`3`,`4`,`5`,
   `6-7`,`8-9`. Neither is in Section 6; the ranges `6-7` and `8-9` are not permitted strings in any
   form. See the new note at the end of Section 6.
4. **Card 6's `the bar:` line is not bold.** Section 4 requires it bold: it is the falsifiable claim
   of the paper and the only bolded body line in the figure.

**Two off-spec choices that are accepted rather than defects, recorded so they are not "fixed" by
accident:** Steps 8 and 9 are drawn with an orange card fill instead of white — it ties them to the
`ENERGY` band and does no harm; and `transfer margin` is drawn nearer Step 7 than Step 6, which is a
routing nuisance, not a false statement, as long as its line still lands on Step 6.

**For the next generation, add this line to the end of the Section 11 prompt block:**

```
The four phase band labels DATA, MODEL, CLAIM and ENERGY must be written HORIZONTALLY, not rotated
and not vertical. Do not print any column headings such as LEFT COLUMN, RIGHT COLUMN or CARDS AND
STATE CHIPS. Do not print step numbers inside the phase bands and do not print ranges such as 6-7 or
8-9 anywhere; the digits appear only inside the round number chips on the cards. The tile reading
"pre-declared gate batteries" must bracket steps 1, 2, 3 and 4 together, not steps 1 and 2 only. The
line beginning "the bar:" on card 6 must be bold.
```
