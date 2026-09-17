# Image prompt — 4J pipeline steps figure (Steps 0 to 11)

**Deliverable:** one raster image, `HETUS_LLM_Pipeline_Steps.png`, generated **by the author** in their
own image tool. This file is the prompt. It is written so the image can be produced without asking a
follow-up question.

**Install path once generated:** `4J_docs_occ/writing/submission/figures/`
**Source of truth for the content:** `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md`, the ASCII
box diagram, ⚪ **Steps 0 to 11**, reconciled against the project state on ⚪ **2026-08-26**,
and again on 🔴 **2026-09-07** (cards 10 and 11 only — see the 2026-09-07 banner below).

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

---

> 🔴 **REVISED 2026-09-14, author request. Regenerate. Three changes.**
>
> 1. 🔴 **The figure becomes HORIZONTAL (landscape).** The twelve step cards run **left to right
>    along one spine**, not top to bottom. Target canvas **2400 x 1000 px at 300 dpi**, an aspect ratio of
>    roughly 12:5, sized to be read across a full journal page width or across a slide. Concretely:
>    - The **five phase bands** move from a left gutter to a **band along the top**, each spanning the
>      cards that belong to it, so the phase a card sits in is read by looking up rather than left.
>    - The **twelve cards** sit in one horizontal row, equal width, equal height, joined left to right by
>      a single arrow spine. If twelve cards in one row makes the type smaller than 8 pt at the target
>      size, wrap to **two rows of six**, reading left to right on the top row and then left to right on
>      the bottom row, with one return arrow between them - never a snake that reverses direction.
>    - The **seven validation tiles** move from a right gutter to a **strip along the bottom**, each tile
>      sitting under the cards it guards, aligned to them.
>    - Card text stacks vertically inside each card as before: step number, short title, state chip, then
>      the body lines. Nothing about the content changes; only the direction of flow.
> 2. **Recolour onto the house palette below**, so this figure matches Figures 3 to 7.
> 3. **Remove any explanatory note text from inside the image.** See the rule below.
>
> 🔴 **And one string must go.** Card 6, the transfer-test card, prints
> *"the reported folds are not yet trained"*. That was true when the card was written and the manuscript
> now contradicts it: all three folds are trained, generated and scored, and Step 11 is complete. Delete
> that line. If card 10 still carries *"the no-core engine does not exist yet"*, delete that too, for the
> same reason. No other card text changes.

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

> 🔴 **REVISED A THIRD TIME, 2026-08-26. The installed image is out of date again. Regenerate.**
> Two things changed and both are structural. **Steps 8 and 9 were built, run and gate-scored** — they
> are no longer `open`, and Step 8's result is a **null** that the figure must not hide. And **Steps 10
> and 11 were added**: the OpenUBEM extension is registered as new steps rather than as an edit to Steps
> 8 and 9, because those two are a closed chapter with a scored pre-registration. The spine therefore
> grows from ten cards to **twelve**, the left gutter from four phase bands to **five**, and the right
> gutter from six tiles to **seven**. Sections 2, 3, 4, 5, 6 and 11 carry the change.
>
> ⚪ **Cards 6 and 7 were NOT re-verified in this revision.** Their state chips and body lines are
> carried forward from 2026-08-22 unchanged. Check them against `Step6_docs/` and `Step7_docs/` before
> generating — Step 7's work item 7.4 closed on 2026-08-26 and this file has not been reconciled
> against it. **Do not promote either card on the strength of this banner.**

> 🔴 **REVISED A FOURTH TIME, 2026-09-07. THE INSTALLED IMAGE IS OUT OF DATE AGAIN. Regenerate
> — but read this banner before touching the table, because the largest change since 2026-08-26 is
> one the figure must deliberately NOT make.**
>
> **What happened.** Step 10 was **built, run and gate-scored** on 2026-08-28: 410 cells across two
> hosts, a 24-gate validation suite closed at **18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED /
> 2 NOT_EVALUABLE**. Then the owner ruled a **no-core** dwelling-subdivision regime
> (`D-EU-79`/`80`/`81`, 2026-09-02/03) that changes the population underneath that campaign, and
> `D-IMP-4` (2026-09-03) folded the replacement into Step 10 rather than into a new step. **Step 10
> now has two campaigns:**
>
> * **`C1`, core-era** — the one that was run and scored. **Archived, closed, and NOT REPORTED.**
> * **`C2`, no-core** — the one that **will** be reported. **Spec only: no cell, no run, no result.**
>
> 🔴 **THE TRAP, AND IT IS THE WHOLE REASON THIS REVISION EXISTS: CARD 10 STAYS `open`.**
> Anyone reading the project files will find an 18-PASS gate board with Step 10's name on it and
> promote the card to `validated`. **That board belongs to a campaign the paper does not report.**
> This figure describes the paper, not the repository. Promoting card 10 would assert a validated
> real-stock result that appears nowhere in the manuscript — and it is the most dangerous defect
> this file has ever had to prevent, worse than `all countries trained jointly`, because it would be
> **defended with a real gate board**. The same reasoning bars any mention of `C1` in the image: it
> is a method and reproducibility record, and a figure that drew it would be advertising evidence
> the paper does not present.
>
> 🔴 **THE PIPELINE ENDS AT STEP 11 BY RULING (`D-IMP-4`). TWELVE CARDS IS FINAL.** Never draw
> a thirteenth card and never draw a `Step 12`. One was created on 2026-09-03 and dissolved the
> same day; the folders on disk are `Step0_docs` – `Step11_docs` only.
>
> **Three strings move, all on cards 10 and 11, and one of them is a stale-string defect of the
> `season` class** — card 11's `hot water magnitude diagnosed before it is re-measured` was
> falsified by `D-S11-1` on **2026-08-27, the day after this file was last written**. Sections 4, 6,
> 10 and 11 carry the change.
>
> ⚪ **Cards 0 to 9 were NOT re-verified in this revision.** Steps 4, 6 and 7 were re-read on
> 2026-09-07 and their STATUS blocks still say what they said (`Step4_docs`: *"Implementation OPEN,
> nothing trained"*; `Step6_docs`: *"OPEN – this is where the paper is won or lost"*;
> `Step7_docs`: OPEN with work items 7.4, 7.5 and 7.6 outstanding), so nothing was moved — **but
> that is a spot check, not an audit. Do not promote any card 0 to 9 on the strength of this banner.**

> 🔴 **REVISED 2026-09-16. Card 6 moves from `open` to `validated`. Cards 10 and 11 are UNCHANGED
> and stay `open` — do not touch them on the strength of this banner.**
>
> **Why card 6 moves.** `validated` means built, and its gate battery ran and was seen to fail on
> purpose before it was trusted (Section 4's own definition, 2026-08-19). Step 6's gate
> (`G6.1`) has now done exactly that: all three folds are trained, generated and scored, the
> pre-registered comparison ran, and it failed 9 of 9 as designed — that is the manuscript's own
> reported headline, not a shortfall. The author confirmed closing this card 2026-09-16.
> **Why cards 10 and 11 do not move with it.** Both are explicitly gated on campaign `C2` being
> run *and scored* (see the 2026-09-07 banner above, "THE TRAP"). `C2` scoring is authorized and in
> progress but not complete — no `G10N.x` verdict exists yet. Moving either now would be exactly the
> defect that banner exists to prevent. Re-ask once scoring lands.
>
> **What changed:** Section 4's table row for card 6 (chip only), Section 11's `circle 6` line,
> and `writing/submission/figures/scripts/generate_fig01_pipeline.py`'s `CARDS` tuple (chip
> `"open"` → `"validated"` for card 6 only). The image was regenerated from the updated script.
> No body-line text changed on any card.

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

> 🔴 **ORIENTATION OVERRIDE, 2026-09-14.** This section was written for a PORTRAIT figure and still says *left gutter*, *right gutter* and *vertical spine*. The figure is now LANDSCAPE: the phase bands run along the TOP, the twelve cards run LEFT TO RIGHT in one row (or two rows of six), and the validation tiles run along the BOTTOM. Everything this section says about CONTENT - which cards, which strings, which chips, which tiles - still holds unchanged. Only the direction is different. See the 2026-09-14 banner at the head of this file.


**Portrait or square, tall.** Roughly 1400 x 1900 pixels or the same aspect. This is deliberately the
opposite orientation to the graphical abstract, so the two are never confused.

Three columns:

```
   left gutter          main spine                right gutter
   (phase bands)        (the twelve step cards)    (validation tiers)
   narrow               wide, vertical            narrow
```

* The **main spine** is a single vertical column of 🔴 **twelve** rounded rectangular cards, Step 0 at
  the top, 🔴 **Step 11** at the bottom, joined by short downward arrows.
* The **left gutter** carries 🔴 **five** tall vertical phase bands, each spanning the steps it groups, drawn
  as a soft-tinted rounded bar with the phase name in it.
* The **right gutter** carries 🔴 **seven** small tiles, one per validation tier, each connected by a thin
  horizontal line to the step or steps it guards. These lines are the only horizontal connectors in the
  figure.

White background. Flat vector style, matching the graphical abstract and the 3J figures.

---

## 3. The five phase bands (left gutter)

> 🔴 **ORIENTATION OVERRIDE, 2026-09-14.** This section was written for a PORTRAIT figure and still says *left gutter*, *right gutter* and *vertical spine*. The figure is now LANDSCAPE: the phase bands run along the TOP, the twelve cards run LEFT TO RIGHT in one row (or two rows of six), and the validation tiles run along the BOTTOM. Everything this section says about CONTENT - which cards, which strings, which chips, which tiles - still holds unchanged. Only the direction is different. See the 2026-09-14 banner at the head of this file.


Each band spans a contiguous run of steps and is labelled with horizontal text at its top, not rotated.

| Band | Spans | Label |
|---|---|---|
| 1 | Steps 0 to 2 | `DATA` |
| 2 | Steps 3 to 5 | `MODEL` |
| 3 | Steps 6 to 7 | `CLAIM` |
| 4 | Steps 8 to 9 | `ENERGY` |
| 5 | 🔴 Steps 10 to 11 | 🔴 `STOCK` |

🔴 **The `CLAIM` band is the one that must stand out.** Give it the strongest tint of the five, and make
it slightly wider than the others so it reads as the centre of gravity of the diagram. Everything above
it is preparation and everything below it is consequence.

---

## 4. The twelve step cards (main spine)

> 🔴 **SHORTENED 2026-09-14, author request: "these are not reports, these are representative
> images."** The card **body lines** below were cut to one short line per card, with a second line kept
> only on cards 5, 6, 8 and 9, and **Section 11's card list is now the authoritative wording for the body
> lines.** Card titles, chip words, the twelve numbers and the seven tile labels are unchanged and this
> section still governs them. The line *every tier is first shown failing on a deliberately broken
> control* was removed from the image altogether and belongs in the body text of §3.

> 🔴 **ORIENTATION OVERRIDE, 2026-09-14.** This section was written for a PORTRAIT figure and still says *left gutter*, *right gutter* and *vertical spine*. The figure is now LANDSCAPE: the phase bands run along the TOP, the twelve cards run LEFT TO RIGHT in one row (or two rows of six), and the validation tiles run along the BOTTOM. Everything this section says about CONTENT - which cards, which strings, which chips, which tiles - still holds unchanged. Only the direction is different. See the 2026-09-14 banner at the head of this file.


Every card has the same internal layout, so the eye can scan down the column:

```
  ┌──────────────────────────────────────────────┐
  │  [n]   STEP TITLE                    [state] │   <- number chip, title, state chip
  │        one line: what closes this step       │   <- the decision line
  │        one line: open here, or a declared caveat │   <- omitted if there is neither
  └──────────────────────────────────────────────┘
```

* The **number chip** is a small filled circle at the left edge containing `0` to 🔴 `11`.
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
| 5 | `Population linkage` | `synthetic population first, then one generated day per person` | `two gates fail and ship as a declared exception` | 🔴 `validated` |
| 6 | `Transfer test` | `train on the other two, generate the held-out one from published marginals` | 🔴 `the reported folds are not yet trained` | 🔴 `validated` — **changed 2026-09-16, see banner below; open line retired 2026-09-07, see Section 11** |
| 7 | `Constrained generation` | `well-formed diaries guaranteed at decoding` | 🔴 `throughput, chaining rule and schedule emission` | `decided` |
| 8 | `Building simulation` | `European residential archetypes, uninjected control run first` | 🔴 `the occupancy effect does not survive at full injection` | 🔴 `validated` |
| 9 | `End-use loads` | `published activity-to-appliance mappings, adapted not authored` | 🔴 `three gates ship as declared failures` | 🔴 `validated` |
| 🔴 10 | `Real-stock UBEM` | 🔴 `observed footprints, dwellings only, one independent diary per dwelling` | 🔴 `the no-core engine does not exist yet` | `open` |
| 🔴 11 | `Stock-scale end-use loads` | `the same mapping, at the scale its sources were validated at` | 🔴 `the bands are inherited unmoved, not re-set at stock scale` | `open` |

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

🔴 **CHANGED AGAIN 2026-08-22 — THREE CARDS MOVED AND TWO TILES CHANGED. REGENERATE.** The layout is
untouched; every change is a chip or a string, and each is tied to the step document that rules it.

* 🔴 **Step 5 goes `decided` → `validated`, and it is the one judgement call in this revision.**
  Step 5 closed on 2026-08-22: `tools/4thJ_gates_step5.py` exists, the board reads **34 PASS / 2 FAIL
  / 0 BLOCKED**, the coverage clause is clean, and gates were seen failing before any was trusted —
  which is exactly what the `validated` chip was defined to mean. 🔴 **But `G5.8` FAILs on `es` and
  `uk` are the TERMINAL VERDICT, not a demonstration**, and Step 5's Definition of Done closed at
  **4 of 5 items plus item 5 by declared exception**. A bare `validated` chip would hide that. So the
  chip moves **and the card gains a third line**, `two gates fail and ship as a declared exception`,
  which is where the honesty now lives. **If the author prefers the chip to carry it instead, the
  alternative is to leave Step 5 at `decided` and drop the third line — one word, one line, either
  way. What must not happen is `validated` with no third line.**
* 🔴 **Step 6's open line was STALE and is replaced.** It read `the scoring basis where survey and
  published wave differ`. `D-S6-2` ruled that on **2026-08-19, the same evening the last revision was
  written**: both Eurostat table renames accepted, Italy scored against the 2008-09 wave with the gap
  declared, the asymmetry stated. It is no longer open. What is genuinely open at Step 6 is that the
  reported folds have not been trained — the 7 B Leg-5 run is queued and has not started — so the line
  becomes **`the reported folds are not yet trained`**.
* **Step 7 gains an open line and keeps `decided`.** Since the last revision the grammar was built and
  its oracle agreement passed on 10,000 strings, all three folds generated both constrained and
  unconstrained, and a gate battery ran on generated text. It is still not `validated`: the board is
  **12 PASS / 15 FAIL**, `G7.12` fails because the throughput comparison has not run, and the schedule
  gates `G7.14`–`G7.17` have never been scored because no schedule has been emitted. The new line names
  exactly that: **`throughput, chaining rule and schedule emission`**.
* **The `pre-declared gate batteries` bracket extends from Steps 1–4 to Steps 1–5.** Step 5 now has a
  battery; leaving the bracket short would say it does not.
* 🔴 **The tile `collapse and memorisation` becomes `collapse, memorisation and privacy`.** Step 6.5
  was built after the last revision: `G6.10`–`G6.13` — loss-based MIA, reference-based MIA against the
  public base model, prefix-prompted extraction, and DCR/NNDR — all pass on all three Leg-4 folds with
  both running controls. That is a distinct guard from collapse, it is why the adapter's weights cannot
  be released, and the gutter had no tile for it. **Renaming beats adding a seventh tile**: the
  2026-08-19 generation already dropped and merged tiles when the gutter was crowded.

🔴 **CHANGED AGAIN 2026-08-26 — cards 8 and 9 were promoted, and two cards were added.**

* **Cards 8 and 9 become `validated`, and this is not a promotion of their results.** `validated` means
  *built, and its gate battery ran and was seen failing on purpose before it was trusted* — it has
  never meant *everything passed*. Step 8 closed all six work items with **0 gate-unit FAILs** over
  31,687 band rows and a battery of **19 of 19** injections hitting; Step 9's board is
  **15 PASS / 3 FAIL / 1 NOT CHECKED** with a battery of 12 HIT / 0 MISS / 3 already-failing and its
  coverage clause passing. Both were built and both had their gates seen failing. Leaving them `open`
  would have said the work has not been done.
* 🔴 **Card 8's second line is the null, and it is mandatory.** Step 8's own conclusion is that
  at full injection **no occupancy claim survives on either channel** — the peak claim's ratio to the
  between-diary spread is 0.54 / 0.02 / 0.40 and every annual median is negative. **A figure that shows
  Step 8 as validated and does not show that it returned a null is dishonest**, and the state chip alone
  cannot say it. If the layout is tight, shrink something else.
* 🔴 **Card 9's second line is the three FAILs.** They ship as results — saturation, a hot
  water band whose basis its own source does not define, and a load shape that genuinely disagrees with
  the source model's activity timing — and **no band was moved.** That is the claim the figure is
  making about how this project works, so it is drawn.
* **Cards 10 and 11 are `open` and must stay `open`.** Nothing is built. They exist in the figure
  because the paper contains them, not because they have results.

🔴 **CHANGED AGAIN 2026-09-07 — CARDS 10 AND 11 ONLY. NO CHIP MOVES, THREE STRINGS DO.**
This is the revision that has to be read rather than skimmed, because its central instruction is a
**refusal to promote a card that now has a gate board behind it.**

* 🔴 **Card 10 stays `open`, and the 18-PASS board is not a reason to move it.** Step 10's
  410-cell campaign was real, was scored, and is **archived as `C1` and not reported**; the campaign
  the paper reports is **`C2`, the no-core one, which has no cell**. `validated` is defined in this
  file as *built, and its gate battery ran and was seen failing on purpose before it was trusted* —
  and by that definition `C1` qualifies. **That is exactly why the rule has to be written down: the
  chip would be defensible on the repository and false about the paper.** The hollow chip on card 10
  is the honest state of the reported work.
* 🔴 **Card 10's decision line gains the rule that defines the campaign:**
  **`observed footprints, dwellings only, one independent diary per dwelling`**. Under `D-EU-79`,
  `D-EU-80` and `D-EU-81` a floor plate divides into **dwellings only** — no core, no corridor, no
  access band, no unconditioned zone; every square metre belongs to a flat; one flat = one zone.
  ⚪ The old string `observed footprints, one independent diary per dwelling` is **superseded, not
  forbidden**: it is not false, it is silent on the one rule that made the campaign be rewritten.
* 🔴 **Card 10's open line `the engine, and which year the diaries belong to` is RETIRED,
  because it names the wrong blocker.** Section 8 of `Step10_docs/4thJ_10_nocoreRealStock.md` names
  what actually waits, and the diary year is not on the list: the **engine carry-in of the no-core
  rule into `european_residential.py`** (recorded as *"identified, not ordered"*), `D-EU-84`,
  `D-EU-87`, `D-EU-88`, and `D-EU-55`, which forbids any EnergyPlus run without the owner's own
  sentence. The new line is **`the no-core engine does not exist yet`** — the single fact that
  stops a reviewer reading card 10 as work merely awaiting a queue slot. ⚪ This does not assert
  that the diary-year question is closed; it asserts that it is not what holds Step 10.
* 🔴 **Card 11's open line is a STALE-STRING DEFECT and is FORBIDDEN.**
  `hot water magnitude diagnosed before it is re-measured` was falsified by **`D-S11-1`, ruled
  2026-08-27 — the day after this file was last revised.** The diagnosis happened and its outcome
  was the opposite of the line's promise: `G9.7` and `G11.7` are both **`INFO`, permanently**, the
  30–50 band is inherited **unmoved**, the deviation is **reported and not scored**, and
  🔴 **it will not be re-measured at stock scale.** The line advertises a measurement the
  project has decided not to make. **Same class as `season` and as `the scoring basis where survey
  and published wave differ`: a string that outlived the ruling that killed it, in a file nobody
  grepped.**
* 🔴 **Card 11's replacement line carries the claim that matters:**
  **`the bands are inherited unmoved, not re-set at stock scale`**. Step 11 inherits Step 9's three
  FAILs — `G9.6` saturation, `G9.7` DHW volume, `G9.12` stock-scale agreement — with their
  bands untouched, and its own document says it **does not exist to make them pass**. That is the
  same species of honesty as card 8's null and card 9's three declared failures, and it is what the
  bottom third of the figure is for.
* ⚪ **Card 11 stays `open` and needs no other change.** Its work item 11.2 is done and no
  Step 11 decision waits on the author, but nothing is built and it depends on a campaign that has
  not run.

🔴 **A first district landing is NOT a campaign, and must not move card 10.** The four-district
population (Madrid, Lyon, London, Bologna) is expected to arrive **one district first**, and
`G10N.19` requires **30 qualifying buildings per fold** before `H10` is evaluable at all. One
district cannot satisfy a per-fold floor across three folds. Until the four-district campaign has
run and been scored, card 10 carries the hollow chip — **regenerating this figure on the strength
of a first delivery is the predictable way this rule gets broken.**

🔴 **France is a site, not a fold, and this figure must not leak the difference.** Lyon is one of
the four districts as a **physical baseline** and never enters a 4J denominator: no French fold, no
French held-out fold, no French diary (`G10.11`, carried to `G10N.11`). The corpus is still **three
countries**. Since this figure names no country and draws no map, the rule costs it nothing — **it
is written here so that a future revision does not "helpfully" add a fourth something to cards 10
and 11 and quietly contradict card 6.**

🔴 **Step 4 still stays `decided`, and this revision does not change that.** The Leg-5 fold is queued
and has not run; `G4.3`, `G4.4` and `G4.12` have never been run and 4 of 15 perturbations are
outstanding. The Section 1 warning against promoting it applies unchanged.

🔴 **Card 6 is drawn larger than the others** and carries one extra line, in bold, beneath its decision
line:

* `the bar: beat real diaries from the other countries, reweighted to the held-out country`

🔴 **Card 6 must remain `open`, and the figure must not let the built front half imply the claim is
settled.** Steps 1 to 3 carry the strongest state chip in the figure while Step 6 — the largest card,
the one the diagram is built around — carries the weakest. **That contrast is the honest state of the
project on 2026-08-19 and it is intended. Do not soften it.**

This is the falsifiable claim of the paper and it is the single most important sentence in the figure.
If the layout is tight, shrink cards 10 and 11 rather than this line. 🔴 **Cards 8 and 9
may no longer be shrunk to make room** — each now carries a second line the figure is not allowed to
drop.

---

## 5. The validation tiers (right gutter)

> 🔴 **SHORTENED 2026-09-14.** The seven tile labels are unchanged and this section still governs
> them, but they now sit along the **bottom** of a landscape figure, not in a right gutter, and the line
> `every tier is first shown failing on a deliberately broken control` was **removed from the image**.
> It is an explanatory sentence, and the picture no longer carries any. It belongs in the body text of
> §3 of the manuscript. Section 11 is the authoritative list of what is drawn.

> 🔴 **ORIENTATION OVERRIDE, 2026-09-14.** This section was written for a PORTRAIT figure and still says *left gutter*, *right gutter* and *vertical spine*. The figure is now LANDSCAPE: the phase bands run along the TOP, the twelve cards run LEFT TO RIGHT in one row (or two rows of six), and the validation tiles run along the BOTTOM. Everything this section says about CONTENT - which cards, which strings, which chips, which tiles - still holds unchanged. Only the direction is different. See the 2026-09-14 banner at the head of this file.


🔴 **Seven** small tiles, stacked, each joined by a thin horizontal line to the step or steps it guards.
Tiles are visually lighter than the step cards so the spine stays dominant.

| Tile label | Connects to |
|---|---|
| `pre-declared gate batteries` | **Steps 1, 2, 3, 4 and 5** — 🔴 **new on 2026-08-19, extended to Step 5 on 2026-08-22** |
| `distributional fidelity` | Step 6 |
| 🔴 `collapse, memorisation and privacy` | Step 6 — 🔴 **renamed 2026-08-22** |
| `structural validity` | Step 7 |
| `transfer margin` | Step 6 |
| `downstream energy` | Steps 8 and 9 |
| 🔴 `basis and denominator` | Steps 10 and 11 — 🔴 **new 2026-08-26** |

🔴 **Why the new tile was added.** The installed figure attaches no validation to Steps 1 to 5, which
tells the reader that checking begins at the transfer test. **That is false, and it undersells the
part of the work that is finished.** Every step from 1 onward ran a battery of gates fixed in advance,
each gate demonstrated failing on a deliberately broken input before its passing result was accepted.
The new tile spans Steps 1 to 5 with a single bracket rather than five separate lines, so the gutter
does not become a second spine.

🔴 **Why a seventh tile, when this file's own rule is that renaming beats adding.** The rule holds
where a new guard is a variant of an old one. This one is not. Steps 10 and 11 introduce a class of check
that does not exist anywhere above them: that a **basis change is not reported as an effect** (the weather
station alone is worth 5–11 % of heating demand, against an occupancy channel of a few per cent), that
two populations selected on different geometry are **not pooled**, and that an end-use is **not counted
twice** at the seam between a reconstruction and a simulation. None of the six existing tiles can be
renamed to cover that without lying about what it guards.

Below the tiles, one small caption in a dashed-border box:

* `every tier is first shown failing on a deliberately broken control`

🔴 **This caption is not decoration.** A validation battery that has never been seen to fail has not
been shown to work, and it is the practice this project runs on. Keep it even if the gutter is crowded.
**As of 2026-08-19 the caption is no longer only an intention for the lower half of the figure — it is
a description of what has already happened in Steps 1 to 5**, which is exactly why those steps now
carry a tier of their own.

---

## 6. THE COMPLETE LIST OF PERMITTED TEXT STRINGS

> 🔴 **SUPERSEDED IN PART, 2026-09-14.** This list still names every string that is *allowed*, and
> nothing outside it may ever appear. But the card **body lines** were cut short on the author's
> instruction that these are representative images and not reports, and the bottom sentence
> `every tier is first shown failing on a deliberately broken control` was dropped altogether.
> **Section 11's card list is the authoritative wording of what is actually drawn.** A string that appears
> here but not in Section 11 is permitted-but-retired: it must not be drawn.

Every string that may appear in the image. Nothing else.

Title, two lines at the top, centred:

* `From Harmonised Time-Use Surveys to Simulated Building Energy`
* 🔴 `The twelve steps of the cross-national occupancy pipeline`

Phase bands:

* `DATA`, `MODEL`, `CLAIM`, `ENERGY`, 🔴 `STOCK`

Step numbers:

* `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, 🔴 `10`, 🔴 `11` — **only inside the number chips**

Step titles:

* `Feasibility gate`, `Corpus`, `Harmonisation`, `Serialisation`, `Fine-tuning`,
  `Population linkage`, `Transfer test`, `Constrained generation`, `Building simulation`,
  `End-use loads`, 🔴 `Real-stock UBEM`, 🔴 `Stock-scale end-use loads`

Step body lines, exactly as written in the Section 4 table:

* `data reachable, prior art clear, method justified, release limits known`
* `national time-use series, one wave per country`
* `common activity, location and co-presence coding, shared day origin`
* `episode form: duration, activity, location, co-presence`
* `open-weight base model, low-rank adapter, one adapter per held-out country`
* `synthetic population first, then one generated day per person`
* `train on the other two, generate the held-out one from published marginals`
* `the reported folds are not yet trained`
* `two gates fail and ship as a declared exception`
* `throughput, chaining rule and schedule emission`
* `the bar: beat real diaries from the other countries, reweighted to the held-out country`
* `well-formed diaries guaranteed at decoding`
* `European residential archetypes, uninjected control run first`
* `archetype models built from published parameter tables`
* `published activity-to-appliance mappings, adapted not authored`
* 🔴 `the occupancy effect does not survive at full injection`
* 🔴 `three gates ship as declared failures`
* 🔴 `observed footprints, dwellings only, one independent diary per dwelling`
  — **rewritten 2026-09-07**; the old form is superseded, not forbidden
* 🔴 `the no-core engine does not exist yet` — **new 2026-09-07**
* 🔴 `the same mapping, at the scale its sources were validated at`
* 🔴 `the bands are inherited unmoved, not re-set at stock scale` — **new 2026-09-07**

State chips:

* `cleared`, `validated`, `decided`, `open`

Validation tiles:

* `pre-declared gate batteries`, `distributional fidelity`, `collapse, memorisation and privacy`,
  `structural validity`, `transfer margin`, `downstream energy`, 🔴 `basis and denominator`
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

🔴 **TWO MORE STRINGS DELETED ON 2026-08-22. Same rule — if either appears, reject and regenerate:**

* `the scoring basis where survey and published wave differ` — ruled by `D-S6-2` on 2026-08-19, the
  same evening the previous revision was written. It is not an open question and must not be drawn as
  one.
* `collapse and memorisation` — the tile is now `collapse, memorisation and privacy`

🔴 **THREE STRINGS DELETED ON 2026-09-07. Same rule — if any appears, reject and regenerate:**

* `the engine, and which year the diaries belong to` — it names the wrong blocker. Section 8 of
  `Step10_docs/4thJ_10_nocoreRealStock.md` lists what actually waits (the no-core engine carry-in,
  `D-EU-84`, `D-EU-87`, `D-EU-88`, `D-EU-55`) and the diary year is not on it.
* `hot water magnitude diagnosed before it is re-measured` — falsified by `D-S11-1` on
  **2026-08-27**, the day after the previous revision was written. `G9.7` and `G11.7` are both
  **`INFO` permanently**, the band is inherited unmoved, and it **will not be re-measured at stock
  scale**. The line promises a measurement the project decided not to make.
* `Step 12`, `campaign C1`, `campaign C2`, and any thirteenth card — **`D-IMP-4` ended the
  pipeline at Step 11.** The two-campaign split inside Step 10 is repository bookkeeping; the paper
  reports one Step 10 and the figure draws one card for it.

🔴 **AND ONE STRING THAT IS NOT FORBIDDEN BUT MUST NOT BE DRAWN AS A RESULT: the Step 10 gate
board.** `18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE` is real, and it belongs to
the **archived, unreported** core-era campaign. No count from it, in digits or in words, may enter
this figure, and it is never a reason to move card 10's chip. See the 2026-09-07 banner.

**The word-form counts `one wave per country`, `the other two` and 🔴 `two gates` are permitted**, under
the same exception as Section 9 item 1: they are closed author decisions, written as words and never as
digits. 🔴 `two gates` was added on 2026-08-22 with card 5 and is permitted on that card only, and
🔴 `three gates` was added on 2026-08-26 with card 9 and is permitted on that card only.

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

> 🔴 **PALETTE OVERRIDE, 2026-09-14.** Superseded by the *House palette* section at the end of this file. No green and no red anywhere.


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
   🔴 **Corrected 2026-08-26 and again 2026-09-07 — the list in item 4 above is the
   2026-08-19 one and is superseded. The current list is: Step 0 `cleared`; Steps 1, 2, 3, 5, 8 and 9
   `validated`; Steps 4 and 7 `decided`; Steps 6, 10 and 11 hollow `open`.** 🔴 **Cards 10 and
   11 carrying anything but `open` is an automatic reject, and the reject holds even if the person
   generating the image can point at Step 10's 18-PASS board — that board is the archived,
   unreported core-era campaign. See the 2026-09-07 banner.**
5. Check that Step 6 is the largest card, carries its bold bar line, and **still carries the hollow
   `open` chip** despite being the visual centre of the figure.
6. Check that no year, no threshold value, no model name, no country name and no count in digits appears
   anywhere; and that the only two word-form counts are `one wave per country` and `the other two`.
7. Check that the sixth validation tile `pre-declared gate batteries` is present and brackets Steps 1
   to 5.
8. Check legibility at full page width in print before it is accepted.
9. 🔴 **If the plan document changes, this prompt changes first and the image is regenerated from it.**
   The Section 4 table is a copy of the Overview's step list, and a copy that drifts from its source is
   worse than no figure.

---

## 11. PASTE-READY PROMPT (Gemini / Antigravity) — added 2026-08-19, 🔴 **rewritten 2026-08-26 for twelve cards**

🔴 **This section is a rendering of Sections 0 to 10, not a second specification.** Paste it as a
single prompt. If it ever disagrees with the sections above, the sections above win and this one is
rewritten from them. **Do not edit this section without editing its source.**

```
Create a flat vector process diagram, LANDSCAPE orientation, as wide as the tool will allow and about
2.4 times wider than it is tall, on a white background, in one clean sans-serif family. The picture is
wide and short, meant to be read across a full journal page width or across a slide.

READ THIS FIRST. This is a REPRESENTATIVE DIAGRAM, NOT A REPORT. It carries very little text on
purpose. Only the strings listed under QUOTED TEXT may appear anywhere in the image, and nothing else.
Words like "column", "spine", "band" and "tile" are layout instructions for you, not text to put in the
picture. Draw NO headings, NO section labels, NO captions and NO explanatory sentences of any kind.

NEVER DRAW A WORD THAT CAME OUT OF THESE INSTRUCTIONS. Everything you are allowed to draw is listed
under TEXT INVENTORY near the end of this prompt. If a word appears in these instructions but not in
that inventory, it must not appear in the picture. In particular:
  Never draw the words circle, title, chip, card, band, tile, bracket, bold, centrepiece, spine,
  gutter, QUOTED TEXT, STYLE, OUTPUT, READ THIS FIRST or TEXT INVENTORY.
  Never draw a colour code. Strings such as #332288, #F2F2F2, #44AA99, #CC6677 and #DDCC77 are
  instructions to your renderer. The character # appears nowhere in the image.
  Never turn a sentence of this prompt into a label, a caption or a note.

DRAW EVERY STRING EXACTLY ONCE, AND EVERY WORD INSIDE A STRING EXACTLY AS MANY TIMES AS IT IS WRITTEN
HERE. The 2026-09-14 generation drew card 11's body line as "same mapping, mapping, bands inherited
unmoved", repeating one word, and that alone made the figure unusable. Before you finish, read every
line of text in the picture back against the list below, word by word, and delete any word you have
written twice. The word-count table after the card list is there so you can check this mechanically.

SET THE TYPE LARGE. The body line under a card title must be at least 60 per cent of the height of that
title, and every word in the picture must stay legible when the image is printed at full page width.
The text has been cut short on purpose so that what remains can be set large. If a line does not fit,
widen the card or widen the picture. Never shrink the type to make text fit.

ALL TEXT IS HORIZONTAL. Nothing is rotated, sideways or vertical anywhere in the image, including the
five tinted bands along the top. Their labels DATA, MODEL, CLAIM, ENERGY and STOCK are written
horizontally, reading left to right, like every other word in the picture.

At the very top, centred, ONE line of text and nothing above it:
  From harmonised time-use surveys to simulated building energy
That is the only title. Do not add a second title line, a subtitle or a strapline.

STRUCTURE. THE FLOW RUNS LEFT TO RIGHT. Across the middle of the picture runs a single horizontal ROW
of twelve rounded rectangular cards, numbered 0 at the far left to 11 at the far right, each joined to
the next by one short arrow pointing RIGHT. Along the TOP edge, five wide tinted rounded bands sit above
the cards they group, each band spanning exactly the cards named below it. Along the BOTTOM edge, seven
small pale tiles each connect UP to the cards they guard by one thin vertical line. Those tier lines are
the only vertical connectors in the picture; every other arrow points right.

If twelve cards in one row would make the card body type too small to read, wrap to TWO ROWS OF SIX
instead: cards 0 to 5 on the upper row reading left to right, cards 6 to 11 on the lower row also
reading left to right, with a single return arrow from the end of the upper row to the start of the
lower one. Never snake the row back on itself, and never let any arrow point left except that one
return arrow. With two rows, the five tinted bands still sit along the top and the seven tiles still sit
along the bottom.

THE FIVE TINTED BANDS ALONG THE TOP, labelled horizontally, each spanning the cards named. Use these
exact hues, which are this paper's house palette, and no others:
  DATA   above cards 0, 1 and 2,   a light neutral grey, #F2F2F2
  MODEL  above cards 3, 4 and 5,   a pale teal, #44AA99 at about 25 per cent tint
  CLAIM  above cards 6 and 7,      indigo #332288, the strongest tint of the five and slightly taller
  ENERGY above cards 8 and 9,      a pale rose, #CC6677 at about 25 per cent tint
  STOCK  above cards 10 and 11,    a pale sand, #DDCC77 at about 25 per cent tint
There is NO GREEN and NO RED anywhere in this image. Green reads as pass and red as fail, and this
figure scores nothing.
Write only those five words on the bands. Put NO digits and NO number ranges on them.

EACH CARD carries, stacked TOP TO BOTTOM inside the card: a small filled circle holding the card's
digit, then a bold title, then ONE short body line, then a small chip at the bottom of the card. Four
cards carry a SECOND body line and they are named below; no other card may be given one. Cards are
equal width and equal height. The chips are drawn four ways, distinguished by fill and by glyph rather
than by colour:
  cleared    solid dark navy fill, white text, one checkmark
  validated  solid dark navy fill, white text, two checkmarks
  decided    solid dark navy fill, white text, no glyph
  open       white fill, navy outline, navy text, no glyph
The number of checkmarks is not decoration. EVERY card whose chip word is validated carries TWO
checkmarks, cards 8 and 9 included; only card 0, whose chip word is cleared, carries one.

THE TWELVE CARDS, with the exact wording of every line:

circle 0, title Feasibility gate, chip cleared
  data, prior art, method, release limits
circle 1, title Corpus, chip validated
  one harmonised wave per country
circle 2, title Harmonisation, chip validated
  common activity, location, co-presence
circle 3, title Serialisation, chip validated
  duration, activity, location, co-presence
circle 4, title Fine-tuning, chip decided
  one adapter per held-out country
circle 5, title Population linkage, chip validated
  synthetic population, then one day each
  two gates ship as declared exceptions
circle 6, title Transfer test, chip validated
  train on two, generate the third
  the bar: beat real diaries, reweighted
circle 7, title Constrained generation, chip decided
  well-formed diaries guaranteed at decoding
circle 8, title Building simulation, chip validated
  European residential archetypes
  the occupancy effect does not survive
circle 9, title End-use loads, chip validated
  published activity-to-appliance mappings
  three gates ship as declared failures
circle 10, title Real-stock UBEM, chip open
  observed footprints, one diary per dwelling
circle 11, title Stock-scale end-use loads, chip open
  same mapping, bands inherited unmoved

WORD COUNTS, SO YOU CAN CHECK THE CARDS MECHANICALLY BEFORE YOU FINISH. Count the words you have
actually drawn on each card body line and compare. A line whose count is one too high almost always
has a word repeated, which is the exact defect of the 2026-09-14 generation.
  card 0  line 1 = 6 words        card 6  line 1 = 6 words   line 2 = 6 words
  card 1  line 1 = 5 words        card 7  line 1 = 5 words
  card 2  line 1 = 4 words        card 8  line 1 = 3 words   line 2 = 6 words
  card 3  line 1 = 4 words        card 9  line 1 = 3 words   line 2 = 6 words
  card 4  line 1 = 5 words        card 10 line 1 = 6 words
  card 5  line 1 = 6 words        card 11 line 1 = 5 words
          line 2 = 6 words
Card 11's five words are: same / mapping, / bands / inherited / unmoved. The word mapping appears on
card 11 once and only once.

CARD 6 IS THE CENTREPIECE. Draw it noticeably larger than every other card, with a very light navy fill
and a thicker border. Its second line, the one beginning "the bar:", is BOLD, and it is the only bold
body line in the whole picture. Card 6 nevertheless keeps the hollow white "open" chip. If space runs
short, shrink cards 10 and 11 rather than that bold line. Do not drop the second line of card 5, 8 or 9;
all three are required, because they are the lines that keep the diagram honest about what failed.

THE SEVEN PALE TILES ALONG THE BOTTOM, each with its thin vertical connecting line running UP to the
card or cards it guards. These seven labels are the whole of their text; add nothing to them:
  pre-declared gate batteries   to cards 1, 2, 3, 4 and 5
  distributional fidelity       to card 6
  collapse, memorisation and privacy   to card 6
  transfer margin               to card 6
  structural validity           to card 7
  downstream energy             to cards 8 and 9 together
  basis and denominator         to cards 10 and 11 together
Nothing is written below the tiles. There is no line of text along the bottom edge of the picture.
There are seven tile shapes and seven tile labels. Not eight, not nine. Every shape along the bottom
carries one of those seven labels; if you have drawn a shape you cannot label from that list, delete it.

The first of the seven tiles is joined to its cards by a single square bracket rather than by five
separate lines. That bracket begins under the left-hand side of the card numbered 1 and finishes under
the right-hand side of the card numbered 5, and its stem drops from the middle of it to the tile. This
paragraph describes a shape. None of its words is drawn.

The chip word on a card is always spelled out in full, as one of cleared, validated, decided or open.
Do not shorten, clip or abbreviate a chip word to fit the chip; widen the chip instead. The card
numbered 3 carries the word validated spelled in full. The card numbered 0 carries the word cleared and
exactly one checkmark beside it; a chip with no checkmark at all is wrong.

QUOTED TEXT. The image contains the one title line, the five band labels, the numbers 0 to 11 inside the
twelve circles, the twelve card titles, the sixteen card body lines, the four chip words and the seven
tile labels. Nothing else. In particular:
  Write no other heading, label, caption or sentence of any kind.
  Write no number anywhere except 0 to 11 inside the circles. No ranges such as 6-7 or 8-9.
  Write no percentage, threshold, accuracy, token count, corpus size, model size, year or date.
  Do not write N-1 or any algebraic expression.
  Do not write any of: all countries trained jointly; acquisition outstanding for the countries not
  yet held; which model family; which country is held out; several waves per country; how many waves
  earn their place; pooling level across waves; the engine, and which year the diaries belong to;
  hot water magnitude diagnosed before it is re-measured; Step 12; campaign C1; campaign C2;
  the reported folds are not yet trained; the no-core engine does not exist yet; every tier is first
  shown failing on a deliberately broken control.
  Draw exactly twelve cards. Do not add a thirteenth card and do not draw a card numbered 12.
  Cards 10 and 11 both keep the hollow open chip. Do not give either of them a checkmark.
  No country names and no flags. No model names such as Gemma, Llama, Qwen, Mistral or OLMo.

TEXT INVENTORY. The image contains these strings and no others. Count them when you have finished:
  1 title line, written once, at the top.
  5 band words: DATA, MODEL, CLAIM, ENERGY, STOCK. Each written once, horizontally, on its own band.
  12 digits, 0 to 11, one inside each card's circle, each written once.
  12 card titles, each written once, on its own card.
  16 card body lines: one on each of cards 0, 1, 2, 3, 4, 7, 10 and 11, and two on each of cards 5,
    6, 8 and 9. That is 8 + 8 = 16 lines. No card has three.
  12 chips, drawn from 4 words: cleared on card 0; validated on cards 1, 2, 3, 5, 8 and 9; decided on
    cards 4 and 7; open on cards 6, 10 and 11.
  7 tile labels along the bottom, each written once.
That is 1 + 5 + 12 + 12 + 16 + 12 + 7 pieces of text. Nothing else is written anywhere in the image:
no eighth tile, no sixth band, no thirteenth card, no note, no legend, no key, no caption, no credit
line, no watermark, no page number.

STYLE. Flat vector only: no 3D, no perspective, no drop shadows, no gradients on text. No logos. No
brain, robot, android, glowing orb or chat bubble. No loop-back arrows, no feedback cycles, no
iteration loops, since the steps run once in order. No time axis, no years, no forecast arrow. Nothing
suggesting the trained model is released: no download icon, no repository mark, no open-weights badge.
Use no green and no red anywhere; the palette above contains neither.

OUTPUT. Render at the largest pixel size the tool offers, and at least 2400 by 1000. Return a PNG, not
a JPEG: this is line art, and JPEG compression frays small type. A 1376 by 768 return is too small for
print and has to be regenerated, so choose the largest canvas available before generating.
Before you generate, choose the widest canvas and the highest resolution your image tool exposes, and
set the aspect ratio to about 21:9. If your tool cannot produce an image wider than 1376 pixels, SAY
SO IN YOUR REPLY IN PLAIN WORDS instead of returning a small image without comment: the figure will
then be rebuilt in code rather than regenerated, and a silent small return costs another round trip.

BEFORE YOU REPLY, CHECK THESE SIX AND SAY IN YOUR REPLY WHAT EACH ONE CAME OUT AS.
  1. How many cards did you draw, and are they numbered 0 to 11? It must be twelve.
  2. Read card 11's body line back word by word. Is any word written twice?
  3. Does the character # appear anywhere in the image? It must not.
  4. Is there any heading above the row of cards, or any text below the seven tiles? There must not be.
  5. Do cards 6, 10 and 11 all carry the hollow open chip with no checkmark?
  6. What are the pixel dimensions of the image you are returning?
Answer all six honestly, including where the answer is wrong. A wrong answer reported is one round
trip; a wrong answer reported as correct is three.
```

### 11.1 What to check the moment the image comes back

Run Section 10 in full before installing. These four are the ones this revision exists for, and any
one of them failing means regenerate rather than accept:

1. Step 4 reads **`one adapter per held-out country`**, never `all countries trained jointly`.
2. **`N-1` appears nowhere.**
3. 🔴 **CHANGED 2026-08-26.** Steps 1, 2, 3, 5, **8** and **9** carry **`validated`**; Steps 4 and 7
   carry `decided`; Steps 6, **10** and **11** carry the hollow **`open`** chip.
4. 🔴 **CHANGED 2026-08-22.** The sixth tile **`pre-declared gate batteries`** is present and brackets
   Steps 1 to **5**, and the second tile reads **`collapse, memorisation and privacy`**.
5. 🔴 **NEW 2026-08-26. The two lines that make the figure honest are present, verbatim:**
   card 8 carries **`the occupancy effect does not survive`** and card 9 carries
   **`three gates ship as declared failures`**. A generator that drops a second body line to fit
   twelve cards into the height will drop exactly these two, because they are the last lines added.
   **If either is missing, regenerate.** A figure showing Steps 8 and 9 as `validated` with no
   mention of the null and the three failures claims a clean downstream result this project does
   not have.
6. 🔴 **NEW 2026-08-26.** Twelve cards, five bars including **`STOCK`**, seven tiles including
   **`basis and denominator`**. Count them; do not read the image for general correctness.

7. 🔴 **REVISED 2026-09-14. Card 10 reads `observed footprints, dwellings only, one independent
   diary per dwelling` and NOTHING ELSE**; the second line `the no-core engine does not exist yet` was
   retired on 2026-09-14 and must not appear. **Card 6 likewise carries only its first two body lines**;
   `the reported folds are not yet trained` was retired in the same pass. Card 11 reads `the same
   mapping, at the scale its sources were validated at` and `the bands are inherited unmoved, not
   re-set at stock scale`. None of the four retired lines — `the engine, and which year the diaries
   belong to`, `hot water magnitude diagnosed before it is re-measured`, `the reported folds are not
   yet trained`, `the no-core engine does not exist yet` — may survive anywhere.
8. 🔴 **NEW 2026-09-07, and this is the one to check hardest. Cards 10 and 11 carry the
   HOLLOW `open` chip.** If either carries a checkmark, reject and regenerate — whatever the
   reason given. Step 10's scored campaign is archived and unreported, and the reported one has no
   cell. A first district arriving from OpenUBEM does not change this.
9. 🔴 **NEW 2026-09-07. Count the cards: exactly twelve, numbered 0 to 11.** No card 12, no
   thirteenth card, no `Step 12` anywhere in the image. The pipeline ends at Step 11 by ruling.

10. 🔴 **NEW 2026-09-14. The picture is WIDE, not tall.** The twelve cards run left to right,
    the five tinted bands run along the TOP, the seven tiles along the BOTTOM, and every arrow on the
    spine points RIGHT. A portrait image, whatever else is correct about it, is a reject. Two rows of
    six is acceptable; a vertical column of twelve is not.

11. 🔴 **NEW 2026-09-14. No note band.** No paragraph of small italic explanatory text anywhere
    in the image, top or bottom. If one appears, regenerate.

12. 🔴 **NEW 2026-09-14. No green and no red**, in the bands, the chips, the tiles or the
    arrows. The five band tints are the house palette named in Section 11 and nothing else.

13. 🔴 **NEW 2026-09-14, second pass. Count the words.** One title line only, one body line per
    card, two body lines on cards 5, 6, 8 and 9 and nowhere else, and **nothing at all written below the
    tiles**. A dashed box or any sentence along the bottom edge is a reject: the picture is a diagram,
    not a report.

14. 🔴 **NEW 2026-09-14, second pass. Check the pixel size before installing.** At least
    2400 x 1000, and a PNG that was never a JPEG. The 2026-09-14 return was 1376 x 768 and JPEG-sourced,
    which is about 197 dpi at full page width where publishers ask for 300 (`FINDING 282`).

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
"pre-declared gate batteries" must bracket steps 1, 2, 3, 4 and 5 together, not steps 1 and 2 only. The
line beginning "the bar:" on card 6 must be bold.
```

---

## 13. RESULT OF THE 2026-09-07 GENERATION — the no-core revision, checked string by string

**Installed file.** `../HETUS_LLM_Pipeline_Steps.png`, md5 `c852194c9d213c5e7ac825688202befb`,
**896 × 1200 px**, installed 2026-09-07 12:00 by converting the image tool's `.jpg` output to PNG. The
previous generation (2026-08-19) is kept at `previous/HETUS_LLM_Pipeline_Steps.png`, md5
`207f42dcac694e2c9a299c13cb966829`, and was not overwritten.

🔴 **The headline: the refusal held. Cards 10 and 11 both carry the hollow `open` chip**, which is the
single thing the 2026-09-07 revision existed to protect, and the one a generator or a reader with the
Step 10 gate board in front of them would have got wrong. All three new strings landed verbatim.

### 13.1 What is correct and must not regress

* **Twelve cards, 0 to 11.** No thirteenth card, no card numbered 12, and `Step 12` appears nowhere.
* **Cards 10 and 11 both hollow `open`.** Card 10 reads `observed footprints, dwellings only, one
  independent diary per dwelling` and `the no-core engine does not exist yet`; card 11 reads `the same
  mapping, at the scale its sources were validated at` and `the bands are inherited unmoved, not
  re-set at stock scale`.
* **Every retired string is absent**, checked one at a time: `the engine, and which year the diaries
  belong to`, `hot water magnitude diagnosed before it is re-measured`, `N-1`, `all countries trained
  jointly`, `acquisition outstanding for the countries not yet held`, `which model family`, `which
  country is held out`, `several waves per country`, `how many waves earn their place`, `pooling level
  across waves`, `campaign C1`, `campaign C2`.
* **The chip words match the current list on all twelve cards:** 0 `cleared`; 1, 2, 3, 5, 8, 9
  `validated`; 4, 7 `decided`; 6, 10, 11 `open`.
* **Card 6 is the centrepiece and still hollow.** Largest card, thicker border, pale navy fill, and its
  `the bar:` line is the only bold body line in the picture — 🟢 **Section 12 defect 4 is fixed.**
* **The scaffolding is gone.** No `LEFT COLUMN`, `RIGHT COLUMN` or `CARDS & STATE CHIPS`; no step
  digits repeated down the phase bands; no `6-7` or `8-9` ranges anywhere — 🟢 **Section 12 defect 3
  is fixed.**
* Seven tiles, all present with their exact labels, and the dashed control line at the foot. No year,
  no threshold, no model name, no country name, and no digit outside the twelve circles. All four
  word-form counts present: `one wave per country`, `the other two`, `two gates`, `three gates`.

### 13.2 Defects. 🔴 **The first two are REPEATS of Section 12, and both were explicitly instructed against inside the block that was pasted.**

1. 🔴 **The five band labels are drawn VERTICALLY**, rotated to read bottom-to-top: `DATA`, `MODEL`,
   `CLAIM`, `ENERGY`, `STOCK`. The pasted block opens by calling horizontal text *"the single most
   important formatting rule here"*. It was ignored on 2026-08-19 and ignored again now. **It
   misstates nothing** — a rotated band label is a common figure convention and no reader is misled —
   but after two attempts the honest conclusion is that **more prompt text will not fix it**: either
   accept it, or the author straightens the five labels by hand.
2. 🔴 **The `pre-declared gate batteries` bracket stops at card 4. Card 5 sits outside it.** On
   2026-08-19 the same bracket spanned only cards 1 and 2; the block was rewritten to say *"reaching
   from card 1 down to card 5, not stopping short"*, and the bracket grew by two cards and still
   stopped short. **This one does misstate the project.** As drawn, Population linkage has no
   pre-declared battery — and Step 5's two declared exceptions, which the card itself prints, came out
   of exactly that battery.
3. ⚪ **Cards 8 and 9 carry `validated` with ONE checkmark**, where cards 1, 2, 3 and 5 carry two.
   Section 2 gives one checkmark to `cleared` and two to `validated`. In a figure whose whole subject
   is the chip vocabulary, the same word drawn two ways is a defect, if a quiet one.
4. ⚪ **Print quality is below spec and item 8 of Section 10 is NOT cleared.** 896 × 1200 against the
   1400 × 1900 asked for, and the PNG is a re-encode of a `.jpg`, so the body type carries JPEG
   ringing. At full page width that is roughly 130 dpi. It is legible on screen; it is not a
   submission raster.

**Off-spec but accepted, recorded so they are not "fixed" into something worse:** the card fills are
tinted to match their band rather than white (accepted since 2026-08-19); the `CLAIM` band is not
visibly wider or stronger than the other four; and `transfer margin` still sits nearer card 7 than
card 6, which is a routing nuisance, not a false statement, as long as its line lands on card 6 — it
does.

### 13.3 What was changed in this document as a result

The two fixable defects were **merged into the Section 11 paste block**, not appended after it, per
that section's own rule: the bracket instruction now names card 5 by its title and says the bracket
has been drawn short twice, and the chip description now says every `validated` chip carries two
checkmarks including cards 8 and 9. A resolution-and-format line was added to the STYLE paragraph.
🔴 **Paste Section 11 as it now stands; do not paste the copy used on 2026-09-07.**

---

## House palette (set 2026-09-14, applies to every figure in this paper)

The matplotlib figures of this paper (Figures 3 to 7) were recoloured onto the palette below on
2026-09-14 and this figure must match them, or the paper will read as two sets of figures.

| Role | Hex | Name |
|---|---|---|
| Spain | `#CC6677` | rose |
| United Kingdom / Britain | `#332288` | indigo |
| Italy | `#44AA99` | teal |
| Second series in a paired comparison | `#DDCC77` | sand, and give it a hatch as well as a hue |
| A negative or null channel | `#882255` | wine |
| Reference lines, thresholds, registered floors | `#000000` | black |
| Value labels and body text | `#111111` | near-black |
| Panel background, gridlines, neutral fills | `#F2F2F2` / `#D0D0D0` | light neutral greys |

Rules that go with it:

- **No green and no red anywhere.** Green reads as pass and red as fail, and this figure is not scoring
  anything. The palette above contains neither.
- The set is colour-blind safe and separates by lightness as well as hue, so it survives greyscale
  printing. Keep the shape, fill-pattern or line-style distinction as well; hue alone is never enough.
- Every hue used must come from the table above. Do not introduce a sixth colour.

---

## No explanatory notes inside the image (author rule, 2026-09-14)

**Do not print explanatory notes, verdict sentences, footnote blocks or caption-like paragraphs inside the
image, and in particular do not put a band of small italic text along the bottom.** The same rule was
applied to Figures 3 to 7 on 2026-09-14, and all such text was deleted from them.

What may appear inside the image: axis labels, tick labels, a short panel title, a legend, box and lane
labels, and the data values themselves. Everything else belongs in the body text of the section that
cites the figure. The caption itself is capped at ten words.

---

**Caption to install with it:**

> **Figure 1.** - Pipeline, Steps 0 to 11.
