# Figure 2 prompt — the leave-one-country-out design and the three nulls

**Written 2026-09-13 for `4J_manuscript_submission.md` §1.5, referenced as Figure 2.**
**Not generated here.** The author generates the image; this file is the specification.
Install to `writing/submission/figures/Figure_02_loco_design.png` and verify against the installed
manuscript, not against this file.

---

> 🔴 **PASTE SECTION 12 AND NOTHING ELSE. Changed 2026-09-14, third revision.**
> Until now this file said to paste the whole document, and that is what caused three of the five
> faults of the 2026-09-14 generation. The generator read this file's own markdown headings and drew
> them as headings in the picture (`Corpus and split`, `Visual candidates`, `Scoring`); it read the
> house-palette table at the foot of the file and printed `Upper: #332288` and `#882255` inside the
> boxes; and it read the sentence *"Far right, small and greyed, the held-out country's real diaries
> with a single label ground truth"* and printed most of that sentence as the label. None of those
> were the generator inventing text. They were this file handing it text and not saying which text
> was to be drawn. **Section 12 is now a single self-contained block that contains only drawable
> text plus instructions that name themselves as instructions. Sections 1 to 11 are the source it
> was written from; if they ever disagree, they win and Section 12 is rewritten from them, but they
> are never pasted.**

🔴 **No value in this prompt may be altered.** Every number below is read from the manuscript, which reads
it from the step documents. If a number looks wrong, stop and check the manuscript rather than adjusting
the drawing.

---

> 🔴 **REVISED 2026-09-14. The installed image must not be submitted and must be regenerated from
> this file.** Three changes, the first of which is disqualifying on its own.
>
> 1. 🔴 **The fork is drawn backwards, and the fork is the whole point of the figure.** Band 2b
>    below asks for **one** marginals box with **one arrow leaving it**, splitting into both candidates.
>    As installed, the box is drawn once correctly, but the only arrow touching it **arrives**: it runs
>    from the fine-tuned model's right edge down into the box, and **no arrow leaves the box, and nothing
>    connects it to the raked donor pool at all.** Read literally, the installed image says the model
>    produces Britain's published marginals, and it does not show the null receiving them. That inverts
>    the one claim the figure exists to prove. Redraw so that the marginals box is a **source**: arrows
>    leave it, one into the model and one into the raked donor pool, and no arrow enters it from either
>    candidate.
> 2. **Recolour onto the house palette below.** The rest of the paper's figures were recoloured on
>    2026-09-14 and this one has not been.
> 3. **Remove any explanatory note text from inside the image.** See the rule below.
>
> Every number on the installed image is correct and none of them changes: 58.91 / 21.79, 60.44 / 19.21
> and 21.24 / 18.54 minutes per day, closest miss 2.70, and 73,254 diaries / 2,024,068 episodes.

---

## What the figure has to make true in one look

A reader who sees only this figure must come away with three things, in this order of prominence:

1. **The model is given less than the null is given? No.** Both sides are given exactly the same thing.
   This is the single most important thing the drawing must communicate, because the commonest objection
   to the result is that the comparison was unfair or circular, and the drawing answers it before the text
   does.
2. **The reference both are scored against was published by someone else, before either side existed.**
3. **The held-out country's diaries touch nothing** on the left-hand side of the figure. They appear only
   at the far right, as the thing being predicted.

If the drawing achieves those three and nothing else, it is a success. All three are carried by the
**arrows and the bar lengths**, not by sentences printed in the picture.

---

## 🔴 This is a diagram, not a report

**Shortened 2026-09-14, author request: "lets use less text inside the pictures, these are not reports,
these are representative images."** Every label below is the whole of its text. Do not expand a label
into a sentence, do not add a heading over a band, do not add a title to the image, and do not print any
explanatory note, caveat or verdict paragraph anywhere in it. **Set the type large**: the text was cut so
that what remains can be read at 90 mm.

Two arguments that used to be printed inside the image were removed on 2026-09-14 and now belong in the
body text of the section that cites this figure: that giving the null weaker marginals would convert a
null into a handicap, and that the raking starts from a uniform seed so the donor surveys' own weights
are discarded. **Do not draw them.**

---

## Structure

A left-to-right flow in three vertical bands, landscape, white background, flat vector. **No image
title. No band headings.** The words *corpus*, *candidate*, *evaluation*, *split* and *verdict* are
layout words for the person reading this specification and must not appear in the picture.

### Band 1 (left) - the corpus, split

Three country tiles stacked: **Spain**, **Italy**, **United Kingdom**. Draw the fold in which **Britain is
held out**, because it contains the closest miss and is therefore the fold most favourable to the model.

- Spain and Italy tiles are **solid** and carry one word each: **training**.
- The Britain tile is **outlined only, not filled**, and carries **held out**.
- Under the three tiles, one small line: **73,254 diaries . 2,024,068 episodes**.

Nothing else is written in this band.

### Band 2 (middle) - the two candidates, side by side, visually parallel

🔴 **The two candidate boxes must be the same size, the same shape and the same visual weight.**
Neither may look like the hero. This is a fairness drawing.

**Upper candidate - the model.** Two lines inside the box:
**Fine-tuned language model** / 7.30 B backbone, low-rank adapter
Output arrow label: **5,200 generated diaries**.

**Lower candidate - the null.** Two lines inside the box:
**Raked donor pool** / real Spanish and Italian diaries, reweighted
Output arrow label: **reweighted real diaries**.

Nothing else is written in either box.

### Band 2b - the shared input, drawn ONCE and split to both

🔴 **This is the load-bearing element of the whole figure, and it is carried by the arrows, not
by words.** A single box, three short lines:

> **Britain's published census marginals**
> age . sex . household type . economic status
> published before either candidate existed

It has **one** arrow leaving it that **forks** into the two candidate boxes: one branch up into the
model, one branch down into the raked donor pool. **No arrow arrives at this box from either candidate.**
It must be visually obvious that this is one source feeding both, not two similar sources feeding one
each. Do not draw two boxes. Do not draw two separate arrows from two copies.

Nothing is written beside the fork.

### Band 3 (right) - scoring

Both candidates' outputs converge on one scoring box, two lines:

> **Time-budget mean absolute error**
> against Britain's published tables

Below it, three small paired bars, one pair per age band, model against null, with the values printed
above the bars and nothing else:

| Band | Model | Null |
|---|---|---|
| Y25-44 | 58.91 | 21.79 |
| Y45-64 | 60.44 | 19.21 |
| Y_GE65 | 21.24 | 18.54 |

Band labels under the pairs: **Y25-44**, **Y45-64**, **Y_GE65**. Axis label: **minutes per day, lower is
better**. The null bar is shorter in all three pairs.

Under the bars, ONE short line, and it is the only sentence in the picture:

> **The null wins 9 of 9. Closest miss 2.70 min/day.**

Far right, small and greyed, the held-out country's real diaries with a single label **ground truth**.

---

## What must NOT appear

- **No sentences except the one under the bars.** No annotations, no notes, no caveats, no footnote band.
- **No image title and no band headings.**
- **No accuracy or quality claim for the model.** No tick marks, no "improved", no green on the model side.
- **No colour that codes one candidate as good and the other as bad.** Use the same palette for both; the
  bar lengths carry the result.
- **Do not draw a fourth country.** The corpus is three.
- **Do not draw a forecast, a year axis, or a 2030 anywhere.** There is no forecast in this paper.
- **Do not draw a Step 12 or any downstream box beyond scoring.** This figure covers the transfer test
  only; the pipeline figure is Figure 1.
- **Do not draw the privacy audit, the archetypes, or EnergyPlus here.**
- **No em dashes and no en dashes** in any label.
- **Do not print any label twice.** The 2026-09-14 return printed one annotation in two places.

---

## Format

Vector-first, sans-serif throughout, readable at 90 mm. Colour-blind-safe palette; the figure must
survive greyscale printing, so the two candidates must be distinguishable by shape or fill pattern and
not by hue alone.

🔴 **Render at the largest canvas the tool offers, and at least 2000 pixels wide. Return a PNG
that was never a JPEG.** The 2026-09-14 return was 1376 x 768 and JPEG-sourced, about 197 dpi at full
page width where publishers ask for 300 (`FINDING 282`).

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

---

## 12. PASTE-READY PROMPT (Gemini / Antigravity) - added 2026-09-14, third revision

🔴 **This is the only block to paste. It is a rendering of Sections 1 to 11, not a second
specification.** Everything the picture is allowed to contain is inside the fence, and the fence
contains no markdown heading, no table of colour codes and no sentence that could be mistaken for a
label.

```
Create a flat vector diagram, LANDSCAPE orientation, as wide as the tool will allow, on a white
background, in one clean sans-serif family. The flow runs left to right.

READ THIS FIRST. This is a REPRESENTATIVE DIAGRAM, NOT A REPORT. Every string you are allowed to
draw is listed under TEXT INVENTORY at the end of this prompt, numbered. Draw each of those strings
exactly once, except where the inventory says otherwise. Draw no other text of any kind.

NEVER DRAW A WORD THAT CAME OUT OF THESE INSTRUCTIONS. If a word appears in this prompt but not in
the TEXT INVENTORY, it must not appear in the picture. In particular:
  Draw no heading over any group of elements, and draw no title for the image.
  Never draw the words upper, lower, left, middle, right, group, box, tile, arrow, fork, source,
  outline, hatch, greyed, palette, indigo, wine, rose, teal, sand, TEXT INVENTORY, ARROWS or OUTPUT.
  Never draw a colour code. Strings such as #332288 and #882255 are instructions to your renderer.
  The character # appears nowhere in the image.
  Never turn a sentence of this prompt into a label. The 2026-09-14 generation printed the sentence
  that told it how to draw the far-right element as the label of that element. The label is two
  words and they are numbered 29 in the inventory.
  Draw no note, no caveat, no legend, no key, no credit line and no caption.

DRAW EVERY STRING EXACTLY ONCE. Read each line of text in the picture back word by word before you
finish and delete any word or line you have written twice.

SET THE TYPE LARGE. The text was cut short on purpose so that what remains can be read at 90 mm
width. If a line does not fit, widen the element that holds it. Never shrink the type to fit.

WHAT THE PICTURE HAS TO MAKE TRUE IN ONE LOOK, and it is carried by the arrows and the bar lengths,
never by a sentence: both of the two competing methods are given exactly the same inputs, and the
thing they are scored against was published by somebody else before either of them existed.

LAYOUT, left to right in three groups, with generous white space between the groups.

GROUP ONE, at the left. Three rounded tiles stacked vertically.
  The top tile is filled rose (#CC6677) and carries two lines: Spain, then training.
  The middle tile is filled teal (#44AA99) and carries two lines: Italy, then training.
  The bottom tile is NOT filled. It is white with a thick indigo (#332288) outline, it sits a little
  lower than the other two with a visible gap above it, and it carries two lines: United Kingdom,
  then held out.
  Draw one thin rounded outline around the top two tiles only, enclosing them as a pair. The bottom
  tile is outside that enclosure. The enclosure carries no label.
  Under all three tiles, one small line: 73,254 diaries . 2,024,068 episodes

GROUP TWO, in the middle, two competing method boxes plus one shared input box.
  The two method boxes are the same width, the same height, the same corner radius and the same
  border thickness. Both have a white fill. Neither may look like the more important of the two.
  The only difference between them is the border colour and a small hatch.
  The top method box has an indigo (#332288) border and two lines inside it:
    Fine-tuned language model
    7.30 B backbone, low-rank adapter
  The bottom method box has a wine (#882255) border, a light sand (#DDCC77) diagonal hatch filling
  it, and two lines inside it:
    Raked donor pool
    real Spanish and Italian diaries, reweighted
  Between the two boxes and to their left, a third box with three lines inside it:
    Britain's published census marginals
    age . sex . household type . economic status
    published before either candidate existed
  This third box is the load-bearing element of the picture. Draw it once. Do not draw two copies of
  it. Nothing is written beside it.

ARROWS. There are exactly three lines in this picture. Two of them fork, so there are exactly six
arrowheads. Draw the three lines one at a time and check each one before drawing the next.

Line one starts at the right edge of the enclosure that holds the Spain tile and the Italy tile. It runs
right a short way, then forks into exactly two branches. One branch goes up and ends with an arrowhead on
the left edge of the top method box. The other goes down and ends with an arrowhead on the left edge of
the bottom method box. Line one has two branches, not three. It does not touch the box that holds
Britain's published census marginals; it passes above and below that box and neither branch stops at it.

Line two starts at the right edge of the box that holds Britain's published census marginals. It runs
right a short way, then forks into exactly two branches. One branch goes up and ends with an arrowhead on
the left edge of the top method box. The other goes down and ends with an arrowhead on the left edge of
the bottom method box. Line two goes nowhere else at all: it does not reach the scoring box, it does not
reach the bars, and it does not reach the right-hand side of the picture. Nothing is drawn to the right
of that box except these two branches turning back toward the two method boxes.

Line three is two separate lines with the same destination. One starts at the right edge of the top
method box and ends with an arrowhead on the left edge of the scoring box. The other starts at the right
edge of the bottom method box and ends with an arrowhead on the left edge of the scoring box. They do not
merge before they arrive; the scoring box has two separate arrowheads on its left edge and nothing else
joins either of them on the way.

Every arrowhead in the picture is on the left edge of the top method box, the left edge of the bottom
method box, or the left edge of the scoring box. There are two on each of those three edges, six in all.
An arrowhead anywhere else is wrong. In particular, the box holding Britain's published census marginals
has no arrowhead on it anywhere: every line that touches that box leaves it. That box is the thing both
methods are given, so it is a starting point and never a destination. If you find yourself drawing a line
that ends at it, you have the picture backwards.

No arrow points left. No arrow loops back. No arrowhead lands on a country tile.

Two arrow labels, and they are the only text on any arrow:
  5,200 generated diaries          on the arrow into the scoring box from the top method box
  reweighted real diaries          on the arrow into the scoring box from the bottom method box

GROUP THREE, at the right.
  One scoring box with two lines inside it:
    Time-budget mean absolute error
    against Britain's published tables
  Below the scoring box, three pairs of vertical bars, one pair per age band, drawn to scale against
  a common baseline. In each pair the left bar is indigo (#332288) and the right bar is sand
  (#DDCC77) with a diagonal hatch. The value is printed above each bar and nothing else is:
    first pair   left bar 58.91   right bar 21.79
    second pair  left bar 60.44   right bar 19.21
    third pair   left bar 21.24   right bar 18.54
  The right bar is visibly shorter than the left bar in all three pairs. Draw them to scale.
  Under each pair, its band label: Y25-44 under the first, Y45-64 under the second, Y_GE65 under the
  third.
  Beside the vertical axis, one line: minutes per day, lower is better
  Under the bars, one short line, and it is the only sentence in the whole picture:
    The null wins 9 of 9. Closest miss 2.70 min/day.
  At the far right edge, a small pale grey rounded shape holding a few thin horizontal grey lines,
  drawn smaller than everything else. Its label is two words and the two words are: ground truth
  A thin grey DASHED line, with NO arrowhead at either end, runs from that shape to the scoring box.

COLOUR. Use only these five hues and the two greys, and never print any of the codes: rose #CC6677,
indigo #332288, teal #44AA99, sand #DDCC77 always with a hatch as well as its hue, wine #882255, and
light neutral greys #F2F2F2 and #D0D0D0 for fills and gridlines, with #111111 for text. There is NO
GREEN and NO RED anywhere in this image. Green reads as pass and red as fail, and no element of this
picture is being marked right or wrong. The picture must survive greyscale printing, so the two
method boxes and the two bars in each pair are told apart by hatch as well as by hue.

STYLE. Flat vector only: no 3D, no perspective, no drop shadows, no gradients on text. No logos, no
brain, no robot, no chat bubble. No tick marks, no crosses, no medals, no trophies, no thumbs: the
picture scores nothing and the bar lengths carry the result. No flags and no maps. Do not draw a
fourth country. Do not draw a year axis, a forecast, or anything dated. Do not draw any step beyond
the scoring box. Do not draw a privacy audit, a building, an archetype or an energy model. Use no em
dash and no en dash in any label.

TEXT INVENTORY. The picture contains these 29 strings and nothing else.
  1  Spain
  2  Italy
  3  training          (this is the only string drawn more than once: once on the Spain tile and
                        once on the Italy tile, and nowhere else in the picture)
  4  United Kingdom
  5  held out
  6  73,254 diaries . 2,024,068 episodes
  7  Fine-tuned language model
  8  7.30 B backbone, low-rank adapter
  9  Raked donor pool
  10 real Spanish and Italian diaries, reweighted
  11 Britain's published census marginals
  12 age . sex . household type . economic status
  13 published before either candidate existed
  14 5,200 generated diaries
  15 reweighted real diaries
  16 Time-budget mean absolute error
  17 against Britain's published tables
  18 58.91
  19 21.79
  20 60.44
  21 19.21
  22 21.24
  23 18.54
  24 Y25-44
  25 Y45-64
  26 Y_GE65
  27 minutes per day, lower is better
  28 The null wins 9 of 9. Closest miss 2.70 min/day.
  29 ground truth
No number appears anywhere except the ones inside entries 6, 8, 14, 18 to 23 and 28 above. No
percentage, no year, no date, no gate count, no step number, no country count.

OUTPUT. Render at the largest pixel size the tool offers, and at least 2000 pixels wide. Return a
PNG, not a JPEG: this is line art, and JPEG compression frays small type. Before you generate, choose
the widest canvas and the highest resolution your image tool exposes. If your tool cannot produce an
image wider than 1376 pixels, SAY SO IN YOUR REPLY IN PLAIN WORDS instead of returning a small image
without comment: a silent small return costs another round trip.

BEFORE YOU REPLY, CHECK THESE SIX AND SAY IN YOUR REPLY WHAT EACH ONE CAME OUT AS.
  1. How many arrowheads touch the box that holds Britain's published census marginals? It must be
     zero, and two lines must LEAVE it.
  2. How many arrowheads touch the scoring box? It must be exactly two.
  3. Does the character # appear anywhere in the image? It must not.
  4. Is there a heading above any group of elements, or a title on the image? There must not be.
  5. What exactly is written as the label of the small pale shape at the far right edge? It must be
     the two words: ground truth
  6. What are the pixel dimensions of the image you are returning?
Answer all six honestly, including where the answer is wrong. A wrong answer reported is one round
trip; a wrong answer reported as correct is three.
```

### 12.1 What to check the moment the image comes back

Read these off the installed PNG, magnifying where the answer is not obvious at full size. Any one of
them failing means regenerate rather than accept.

1. 🔴 **No arrow arrives at the marginals box.** Two lines leave it, one into each method box.
   This is the whole point of the figure and it has now been drawn wrong twice, in two different
   ways: on 2026-09-13 the only arrow touching the box arrived from the model, and on 2026-09-14 the
   arrow ran up into the box from the donor pool. **Magnify the arrowhead and look at which end it
   is on.** (`FINDING 276`, reopened as `FINDING 287`.)
2. 🔴 **Exactly two arrowheads land on the scoring box**, one from each method box. The
   2026-09-14 return had three, the extra one straight from the marginals box.
3. 🔴 **No heading sits above any group.** The words *corpus*, *candidate*, *split*, *scoring*
   and *evaluation* appear nowhere in the picture. The 2026-09-14 return printed three headings.
4. 🔴 **The character `#` appears nowhere.** The 2026-09-14 return printed `Upper: #332288` and
   `#882255` inside the boxes.
5. 🔴 **The far-right label is the two words `ground truth`** and nothing more. The 2026-09-14
   return printed the specification sentence there, clipped by the canvas edge.
6. The two method boxes are the same size, the same shape and the same border weight.
7. Every number is present and correct: 73,254 / 2,024,068, 7.30 B, 5,200, the three pairs
   58.91 / 21.79, 60.44 / 19.21, 21.24 / 18.54, and 2.70. The right-hand bar is shorter in all three
   pairs.
8. One sentence in the whole picture, under the bars. No note band anywhere.
9. No green and no red. Pixel width at least 2000, and a PNG that was never a JPEG (`FINDING 282`).

---

**Caption to install with it:**

> **Figure 2.** - Leave-one-country-out design and the three nulls.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

