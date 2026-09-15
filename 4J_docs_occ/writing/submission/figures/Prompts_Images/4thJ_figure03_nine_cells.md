# Figure 3 prompt — the pre-registered bar fails in nine of nine cells

**Written 2026-09-14 for `4J_manuscript_submission.md` §5.1, to be referenced as Figure 3.**
**This file is the specification and the values in it are the authority.**
**Built 2026-09-14** by `writing/submission/figures/scripts/generate_fig03.py`, a matplotlib script
driven by the series printed below, so the drawn values are the measured values by construction.
To change the image, edit that script and re-run it. Never hand-edit the PNG.
Install to `writing/submission/figures/Figure_03_nine_cells.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** Every number below is read verbatim from Table 5 of the
manuscript (`4J_manuscript_submission.md:609-621`), which reads it from the Step-6 transfer document. No
value may be rounded, re-scaled, re-ordered, averaged, interpolated or converted to a percentage or a
ratio. If a number looks wrong, stop and check the manuscript rather than adjusting the drawing.

---

## Why this figure exists

This is the paper's headline result and at present it is readable only as a table. Figure 2 draws the
*design* of the test; this figure draws its *outcome*. A reader who sees only this figure must come away
with three things:

1. **The null is shorter in every single pair.** Nine pairs, nine wins for the null, no exception, no
   cherry-picking, no fold where the model comes out ahead.
2. **The one near miss is visible and is not hidden.** Britain's oldest band is the only pair where the
   two bars are close. It must read as close, because the paper reports it as the closest miss.
3. **Lower is better.** The quantity is an error, so the shorter bar is the better result. If a reader
   reads the long bars as the winner, the figure has failed.

---

## Structure

A single grouped horizontal bar chart, full page width, nine rows.

Rows are grouped into three fold blocks with a small gap between blocks, in this order, which is the order
the manuscript prints them. Do not re-sort the rows by value.

**THE DATA. Draw exactly these eighteen bars and print exactly these values.**

| Fold | Band | Model | Raked-donor null | Margin |
|---|---|---:|---:|---:|
| Spain | Y25-44 | 36.81 | 9.94 | -26.9 |
| Spain | Y45-64 | 34.52 | 8.82 | -25.7 |
| Spain | Y_GE65 | 44.32 | 11.81 | -32.5 |
| Britain | Y25-44 | 58.91 | 21.79 | -37.1 |
| Britain | Y45-64 | 60.44 | 19.21 | -41.2 |
| Britain | Y_GE65 | 21.24 | 18.54 | -2.70 |
| Italy | Y25-44 | 62.24 | 19.51 | -42.7 |
| Italy | Y45-64 | 33.95 | 13.85 | -20.1 |
| Italy | Y_GE65 | 35.84 | 15.51 | -20.3 |

Each row shows two bars side by side: the upper bar is the **fine-tuned language model**, the lower bar is
the **raked donor null**. The two series keep the same fill throughout the figure so a reader learns them
once. Print each bar's value at the end of the bar.

Axis, running left to right from zero: **time-budget mean absolute error, minutes per day**. Directly
beneath the axis title, in the same size: **lower is better**. A single shared axis for all nine rows, one
common scale, so bar lengths are comparable across folds. Do not give any fold its own scale.

Fold block labels, at the left, horizontal: **Spain held out**, **Britain held out**, **Italy held out**.
Band labels at the left of each row: **Y25-44**, **Y45-64**, **Y_GE65**.

### The one row that gets extra treatment

The **Britain / Y_GE65** row carries a small call-out beside it, no larger than the body text:

> **closest miss, 2.70 min/day**

Nothing else on the chart is highlighted. Do not put a call-out on the largest margin; the point of the
figure is that the model loses everywhere, not that it loses worst somewhere.

### The verdict line

Beneath the chart, in the figure's largest non-title text, on one line:

> **Nine cells. Nine losses. The null is closer to the held-out country's published tables in every band
> of every fold.**

---

## Two annotations that must appear

Small, set apart, each answering an objection a reviewer raises at a figure rather than at the text.

**(a) On the null, once, near its legend entry:**
> *The null is real diaries from the other two countries, reweighted by iterative proportional fitting
> onto the held-out country's own published marginals. It is not a naive or random baseline.*

**(b) On the bar, once, near the axis:**
> *The bar was fixed and md5-locked before training and was never moved.*

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

- **No ratio, no fold-change, no per-cent improvement, no mean across cells.** The table carries three
  columns and the drawing carries those three columns only. Do not compute "x times better" anywhere.
- **No error bars, no confidence interval, no significance star.** None was computed; drawing one invents
  a quantity.
- **No green, no red, and no tick or cross.** The null winning is the *negative* result of the paper, so
  colouring the null as "good" misreads the paper. Use one neutral pair of fills distinguishable in
  greyscale by fill pattern, not by hue.
- **No trend line, no arrow of improvement, no "before and after".**
- **Do not sort the bars by length.** Publication order is manuscript order.
- **Do not add a tenth cell, a pooled row, an average row or a total.**
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, exported at 300 dpi minimum, full page width, readable at 180 mm. Sans-serif throughout.
Colour-blind-safe; the figure must survive greyscale printing, so the two series must be distinguishable
by fill pattern as well as by tone.

**Caption to install with it:**

> **Figure 3.** - Time-budget mean absolute error, model against raked-donor null.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

