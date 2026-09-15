# Figure 6 prompt — one appliance model, three diaries, peaks six hours apart

**Written 2026-09-14 for `4J_manuscript_submission.md` §5.8, to be referenced as Figure 6.**
**This file is the specification and the values in it are the authority.**
**Built 2026-09-14** by `writing/submission/figures/scripts/generate_fig06.py`, a matplotlib script
driven by the series printed below, so the drawn values are the measured values by construction.
To change the image, edit that script and re-run it. Never hand-edit the PNG.
Install to `writing/submission/figures/Figure_06_appliance_peaks.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** The 72 values below are read verbatim from
`Step9_docs/outputs_step9/agg_diurnal.csv`, column `elec_w_per_dwelling`, which is the file the three
peaks printed in Table 9 of the manuscript come from. No value may be rounded, smoothed, resampled to a
coarser step, normalised or rescaled.

🔴 **ONE THING MUST BE SETTLED BEFORE THIS FIGURE IS GENERATED: what scale it is labelled at.**
See `FINDING 278` in `writing/4thJ_writeup_notes.md`. The values below are the **archetype-scale** run of
100 dwellings; the manuscript's Table 9 prints them under a **stock-scale** caption, and the stock-scale
run is a different set of numbers that does not cover Spain at all. **Until the author rules, the figure
is labelled archetype scale, because that is what the plotted numbers are.** If the author rules the
other way, this prompt must be rewritten against the stock-scale file, and Spain cannot appear in it.

---

## Why this figure exists

This is the clearest positive result in the paper and it is currently three rows of a table naming three
hours. The shape is the result, and a table cannot show a shape. A reader who sees only this figure must
come away with two things:

1. **Three curves, visibly different, peaking six hours apart**, at 14:00, 18:00 and 20:00.
2. **Nothing but the diary differs between them.** One appliance set, one set of published parameters,
   one calibration, one trigger rule. The spread is the activity data speaking and nothing else.

---

## Structure

One line plot. Three lines, one per fold, 24 points each, markers optional, lines drawn through every
hour. X axis: **hour of day**, 0 to 23, ticks every three hours. Y axis: **mean appliance electricity,
watts per dwelling**, starting at zero.

**THE DATA. Plot exactly these 72 values.**

**Spain, watts per dwelling, hours 00 to 23:**
161.0065, 167.1608, 152.1853, 183.7966, 88.2520, 86.4613, 90.2884, 231.1866, 322.3911, 288.9154,
209.8567, 261.4761, 283.1428, 329.5136, 502.8777, 288.2443, 237.4997, 276.7177, 278.3329, 436.4504,
359.7059, 375.2607, 321.2966, 216.3090

**Italy, watts per dwelling, hours 00 to 23:**
257.7229, 205.4651, 168.9858, 192.3412, 87.1615, 86.4866, 95.4819, 246.0244, 240.4165, 226.5512,
197.5258, 154.0847, 275.6615, 235.6975, 253.3758, 280.1487, 232.5131, 235.8322, 403.5225, 322.3697,
330.7499, 307.4528, 332.0188, 290.9912

**Britain, watts per dwelling, hours 00 to 23:**
163.9499, 120.1332, 104.7535, 137.8746, 86.2880, 92.6489, 92.8075, 215.0523, 215.0066, 269.7648,
297.1429, 198.7250, 255.4478, 348.0092, 327.7575, 333.2554, 287.5917, 268.0605, 243.6590, 310.9027,
416.1349, 347.0145, 324.7435, 254.8932

### The three peaks, marked

Each line's maximum carries a small marker and a horizontal label:

> **Spain 14:00, 503 W** · **Italy 18:00, 404 W** · **Britain 20:00, 416 W**

The printed values are the manuscript's rounded ones; the plotted points are the full-precision ones
above. Both are correct and they must not be reconciled by altering either.

### The span that is the result

A light horizontal span, or a pair of vertical guides, running from **14:00 to 20:00**, labelled once,
horizontally: **six hours**. This is the figure's punchline and it must be readable at a glance.

Under the chart, in the figure's largest non-title text:

> **One appliance model. One calibration. One trigger rule. Only the diary differs, and the peak moves six
> hours.**

---

## Two notes that must appear

**(a) On what this is a claim about:**
> *This is a shape and timing result. It is not an accuracy claim, and it is never reported for an
> individual dwelling.*

**(b) On the check that fails on these same numbers, because the paper reports both readings:**
> *Scored against a published British reference load shape assembled around the year 2000, this same
> measurement is a failing check. A Spanish load shape built from Spanish diaries is supposed to disagree
> with a British reference, and the band was not moved.*

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

- **No claim of validation against measured metering data.** None was done.
- **No per-dwelling curve, no individual household, no envelope of individual dwellings.**
- **No smoothing, no spline that overshoots the plotted points, no interpolation to sub-hourly.** The data
  is hourly; draw it hourly.
- **No normalisation to a common peak.** The vertical differences are part of the result.
- **No green, no red, no tick, no cross, and no flag or map.** Label the countries in words.
- **Do not print the word stock anywhere** until `FINDING 278` is resolved.
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, 300 dpi minimum, full page width, readable at 180 mm. Sans-serif throughout. Colour-blind
safe; the three countries must be separable by line pattern as well as by tone, because the figure must
survive greyscale printing.

**Caption to install with it:**

> **Figure 6.** - Mean appliance electricity by hour of day, three folds.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

