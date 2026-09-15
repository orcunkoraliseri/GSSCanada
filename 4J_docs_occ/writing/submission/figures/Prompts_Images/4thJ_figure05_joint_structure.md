# Figure 5 prompt — joint structure: every band exceeded, several times over

**Written 2026-09-14 for `4J_manuscript_submission.md` §5.5, to be referenced as Figure 5.**
**This file is the specification and the values in it are the authority.**
**Built 2026-09-14** by `writing/submission/figures/scripts/generate_fig05.py`, a matplotlib script
driven by the series printed below, so the drawn values are the measured values by construction.
To change the image, edit that script and re-run it. Never hand-edit the PNG.
Install to `writing/submission/figures/Figure_05_joint_structure.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** Every number below is read verbatim from Table 8 of the
manuscript (`4J_manuscript_submission.md:734-741`). The measured column is a **range across the three
folds**, not a single value, and it must be drawn as a range. Do not average it, do not pick its midpoint,
do not pick its worst end, and do not invent per-fold values that the table does not carry.

---

## Why this figure exists

§5.1 shows the model losing on the quantity it was conditioned on. This figure shows it losing on the
quantities it was never given at all, which is the deeper half of the result and is currently four rows of
a table. A reader who sees only this figure must come away with two things:

1. **Four independent structural properties were checked and all four fail**, on bands fixed in advance.
2. **They do not fail narrowly.** The smallest overshoot is more than three times its band and the largest
   is more than eight times it. This is not a near miss that a little more training would close.

---

## Structure

A single horizontal chart with four rows, one per quantity, drawn as a **multiple of the registered band**
so that four different units can share one axis. This is the only figure in the paper where a derived
quantity is plotted, and it is admissible only because the manuscript's own table prints that multiple in
its last column; take the multiple from the table, do not recompute it.

**THE DATA. Draw exactly these four rows and print exactly these strings.**

| Quantity | Registered band | Measured across the three folds | Multiple of band |
|---|---|---|---|
| Dwell-time Wasserstein distance | 10.0 min | 50.13 to 66.57 | 5.0 to 6.7 |
| Transition-matrix total variation | 0.050 | 0.1623 to 0.2344 | 3.3 to 4.7 |
| Diurnal Jensen-Shannon divergence | 0.015 | 0.0690 to 0.1189 | 4.6 to 7.9 |
| Time-budget error | 8.0 min | 38.26 to 68.67 | 4.8 to 8.6 |

Each row is a **range bar**: a bar drawn from the low end of the multiple to the high end, with a marker at
each end, on an axis running from 0 to at least 9. It is not a single-valued bar; the three folds sit
somewhere inside that span and the figure does not claim to know where.

One vertical reference line at **1.0**, drawn heavier than the bars, labelled horizontally:
**the registered band**. Every range bar sits entirely to the right of it, and none of them comes near it.

At the left of each row, the quantity's name. At the right of each row, in small type, the row's own units
restated as the table gives them: **band 10.0 min, measured 50.13 to 66.57**, and so on for the other
three. The reader must be able to recover the real units from the figure without the caption.

Axis title: **measured value as a multiple of the band registered before training**. Beneath it, in the
same size: **1.0 is the band. Anything to the right of it fails.**

Under the chart, in the figure's largest non-title text:

> **None of these quantities was in the prompt. All four fail, on every fold, at three to nine times
> their band.**

---

## Two notes that must appear

**(a) On what these quantities are, because it is the point:**
> *The model was conditioned on a time budget. Dwell times, transition structure and diurnal shape were
> never supplied to it and were never optimised for. They are what the joint distribution looks like when
> only its margins are specified.*

**(b) On robustness, taken from the sentence immediately below the table:**
> *Verdicts are identical under the calendar-re-based weights and unweighted, so the failure is not an
> artefact of the weighting correction.*

---

## Palette

🔴 **Added 2026-09-14 after the first build broke the bar below.** The first set of images drew Italy in
green, and drew the registered floor, the registered band and one negative value in red. That breaks the
*no green, no red* line in the next section twice over. **Red and green together are the one pair a
colour-blind reader cannot separate**, and they carried two of the three countries. And on a page of
failing checks and nulls, **any hue a reader decodes as good-or-bad misreads the result**: green on the
fold that turns back upward, red on the one negative number.

Use this palette and no other.

| Role | Colour |
|---|---|
| Spain | `#E69F00` orange |
| Britain | `#0072B2` blue |
| Italy | `#7B3294` purple |
| Model series, and any single-series bar | `#3E6B99` slate blue, solid fill |
| Null series, and the between-diary spread | `#D19C65` ochre, hatched `///` |
| Registered band, registered floor, zero line | `#000000` black, solid, heavier than the data |
| Every printed value, every verdict line | `#111111` |
| Grid | `#BBBBBB` dotted |

Colour is never the only carrier. **Every series must also differ by line style and marker, or by fill
pattern**, so that the figure still reads with the colour taken out. Callout boxes tint to the series
they point at, never to a verdict.

---

## What must NOT appear

- **No per-fold value.** The table carries ranges. Inventing three points inside a range is fabrication.
- **No average, no pooled multiple, no total, no fifth summary row.**
- **No green, no red, no tick, no cross.** Four failures; do not colour-code a verdict.
- **No log axis** unless every tick is labelled with its real value; the spread is 3.3 to 8.6 and fits a
  linear axis comfortably, so a linear axis is preferred.
- **Do not draw the band line as dashed-and-optional**, and do not add a softer secondary threshold. The
  bands were registered before training and were never moved.
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, 300 dpi minimum, single column or full width, readable at 90 mm. Sans-serif throughout.
Colour-blind safe and legible in greyscale; the four rows carry their meaning by position and label, so no
hue may be load-bearing.

**Caption to install with it:**

> **Figure 5.** - Four structural properties, each as a multiple of its band.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

