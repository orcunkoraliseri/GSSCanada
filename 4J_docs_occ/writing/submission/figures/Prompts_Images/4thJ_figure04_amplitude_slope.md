# Figure 4 prompt — the fictional-country control: direction versus amplitude

**Written 2026-09-14 for `4J_manuscript_submission.md` §5.4, to be referenced as Figure 4.**
**This file is the specification and the values in it are the authority.**
**Built 2026-09-14** by `writing/submission/figures/scripts/generate_fig04.py`, a matplotlib script
driven by the series printed below, so the drawn values are the measured values by construction.
To change the image, edit that script and re-run it. Never hand-edit the PNG.
Install to `writing/submission/figures/Figure_04_amplitude_slope.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** The five-level series and the three slopes are read
verbatim from `Step6_docs/4thJ_06_transfer.md:2989-2993`; the slopes, the floor and the steering figures
are read verbatim from `4J_manuscript_submission.md:704-722`. No value may be rounded, re-scaled,
smoothed, monotonised or re-fitted.

🔴 **Two qualifiers are load-bearing and both must be drawn, not omitted as clutter.** They are the
reason this figure is worth making, and a version of it that drops them would overclaim:
* **the steering arm was never measured on the model this paper reports.** It is inherited from the
  smaller pilot. It may appear only as text, clearly marked inherited, and never as a plotted series.
* **the plotted slope is the six-channel pre-split figure**, while the registered definition of the
  check counts five channels with one excluded by name. The registered definition was never applied to
  the reported model. The figure must say so.

---

## Why this figure exists

The paper's most quotable sentence is that the model *steers correctly and delivers about half the
amplitude*. This figure is where that sentence is either earned or qualified, and at present the reader
gets only prose. A reader who sees only this figure must come away with three things:

1. **The model is not inert.** Push the conditioning vector and the output moves with it, monotonically,
   in two folds of three. This is the paper's clearest evidence that conditioning is received at all.
2. **It moves too little.** Every fitted slope is roughly half the registered floor, and the check fails
   in all three folds.
3. **Half of this diagnostic is inherited from a smaller model**, and the figure says which half.

---

## Structure

Two panels side by side, the left one large and the right one narrow.

### Left panel — the response curves

A line plot, three lines, one per fold, five points each, markers drawn at every point.

**THE DATA. Plot exactly these fifteen points. Do not smooth and do not force monotonicity.**

| Fold | level 0 | level 1 | level 2 | level 3 | level 4 | fitted slope |
|---|---:|---:|---:|---:|---:|---:|
| Spain held out | 60.71 | 59.15 | 49.04 | 34.19 | 16.64 | 0.4153 |
| Britain held out | 35.76 | 34.06 | 24.38 | 18.77 | 15.39 | 0.5329 |
| Italy held out | 36.49 | 28.55 | 15.89 | 12.42 | 19.02 | 0.4049 |

🔴 **The Italy line turns back up at level 4**, from 12.42 to 19.02. That upturn is measured and it must
be drawn. Do not straighten it, do not drop the point, do not label it an outlier.

X axis: **conditioning level pushed along the tilt**, ticks at 0, 1, 2, 3, 4.
Y axis: **distance to the fictional conditioning vector**, with no unit asserted beyond what is written
here. Falling is responding.

Print each fold's fitted slope at the right-hand end of its line: **slope 0.4153**, **slope 0.5329**,
**slope 0.4049**.

### Right panel — the three slopes against the floor

A small horizontal bar chart, three bars, one per fold, on a scale running 0 to 1.0.

| Fold | slope |
|---|---:|
| Spain held out | 0.4153 |
| Britain held out | 0.5329 |
| Italy held out | 0.4049 |

One vertical reference line at **0.80**, drawn heavier than the bars and labelled, horizontally:
**registered floor 0.80**. All three bars stop well short of it. Beneath the bars, one line:

> **Fails 3 of 3. The response is real and roughly half the required strength.**

---

## The three notes that must appear

Small, set apart, in the figure, not left to the caption.

**(a) On the steering arm, because it is what this figure does not show:**
> *Direction was measured only on the smaller pilot model, where it passes at R-squared 0.8455, 0.9808
> and 0.9836 against the same floor of 0.80. It was never recomputed on the model reported here and is
> inherited, not measured.*

**(b) On the basis of the plotted slope:**
> *These slopes are computed over six conditioning channels. The registered definition of this check
> counts five, with one excluded by name, and was never applied to the reported model.*

**(c) On what a failing slope does and does not mean:**
> *A low slope means under-response, not indifference. An indifferent model would give a flat line.*

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

- **No steering series, no second set of lines, no R-squared plotted as a bar.** The steering numbers
  appear as the text of note (a) and nowhere else. Drawing them would imply they were measured here.
- **No pilot-model curve on the left panel.** One model is plotted: the reported one.
- **No extrapolation past level 4** and no projected line reaching 0.80.
- **No green, no red, no tick, no cross.** This check fails; do not colour any bar as a success.
- **No regression band, no confidence interval, no p-value.** None was computed.
- **Do not relabel the floor**, do not draw a second softer threshold, and do not draw the 0.80 line as
  dashed-and-optional. The floor was registered in advance and never moved.
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, 300 dpi minimum, full page width, readable at 180 mm. Sans-serif throughout. Colour-blind
safe; the three folds must be separable by marker shape and line pattern as well as by tone, because the
figure must survive greyscale printing.

**Caption to install with it:**

> **Figure 4.** - The fictional-country control: response curves and fitted slopes.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

