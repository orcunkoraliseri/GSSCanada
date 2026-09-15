# Figure 7 prompt — occupancy into heating is a null, and what survives instead

**Written 2026-09-14 for `4J_manuscript_submission.md` §5.11, to be referenced as Figure 7.**
**This file is the specification and the values in it are the authority.**
**Built 2026-09-14** by `writing/submission/figures/scripts/generate_fig07.py`, a matplotlib script
driven by the series printed below, so the drawn values are the measured values by construction.
To change the image, edit that script and re-run it. Never hand-edit the PNG.
Install to `writing/submission/figures/Figure_07_heating_null.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** Every number below is read verbatim from Table 10 of the
manuscript (`4J_manuscript_submission.md:872-879`) and from the prose of §5.11 immediately below it. No
value may be rounded, re-signed, re-scaled or averaged.

---

## Why this figure exists

This is a null, and nulls are the easiest result in a paper to read as "nothing happened" and skip. The
figure's job is to make the null legible as a measurement rather than as an absence, and to show the one
thing that does survive it. A reader who sees only this figure must come away with three things:

1. **The occupancy effect on peak heating is smaller than the spread between individual diaries**, in all
   three folds. That comparison, not the effect's own size, is what makes it a null.
2. **The sign is not even stable**, flipping negative in Italy.
3. **One ordering survives, and it is geometric, not behavioural.** Apartment buildings are the largest
   effect in every fold, and that ordering is identical on both sides of the four-hour correction that
   invalidated the first campaign.

---

## Structure

Two panels, stacked or side by side, the upper or left one carrying the null and the other carrying what
survives.

### Panel A — the effect against the spread it has to beat

Three fold groups: **Spain**, **Britain**, **Italy**. In each group, two bars on a shared scale.

**THE DATA. Draw exactly these six bars and print exactly these values.**

| Fold | Peak effect | Between-diary spread | Ratio of effect to spread | Annual median effect |
|---|---:|---:|---:|---:|
| Spain | +2.7145 % | 4.9837 | 0.54 | -1.5100 % |
| Britain | +0.0393 % | 2.3797 | 0.02 | -0.3605 % |
| Italy | -0.6332 % | 1.5959 | 0.40 | -0.4178 % |

The first bar of each pair is the **peak effect** and the second is the **between-diary spread**. The
effect bar is shorter than the spread bar in every fold, and Italy's effect bar points the other way.
Print the ratio beside each pair: **0.54**, **0.02**, **0.40**.

Draw a zero line and let Italy's bar cross it. Do not plot absolute values; the sign flip is the result.

Panel A's own line, beneath it:

> **The effect is smaller than the spread between individual diaries in every fold, and its sign is not
> stable.**

### Panel B — the annual channel, and the ordering that survives

Two small elements, side by side.

**B1, the annual channel.** Three bars, one per fold: **Spain -1.5100 %**, **Britain -0.3605 %**,
**Italy -0.4178 %**, on a zero-centred axis so all three read as negative. One line beneath:
> *Every annual median is negative at every sensitivity level in every fold, so the sign of the annual
> channel was a statement about the clock rather than about occupancy.*

**B2, the surviving ordering.** Three bars, one per fold, giving the apartment-building effect, which is
the largest dwelling class everywhere: **+3.46 %**, **+1.04 %**, **+0.50 %**. Label the three in the
order the manuscript prints them and label the class **apartment buildings**. One line beneath:
> *The effect is monotone in dwelling class in all three folds and the ordering is identical on both sides
> of the four-hour correction. This is a claim about geometry, not about behaviour.*

---

## Two notes that must appear

**(a) On the history, because the manuscript says the history is the result:**
> *A four-hour phase error invalidated the first campaign and correcting it changed the sign of the
> headline. These are the corrected values.*

**(b) On what the design does support:**
> *Every claim this design supports is a peak and timing claim. In the observed-stock campaign, going
> from no occupancy signal to full occupancy signal moves annual heating by under half a per cent while
> moving the hourly peak by up to 7.92 per cent and the peak hour by up to 41 hours.*

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

- **No absolute-value bars and no hidden signs.** Italy's negative peak effect and all three negative
  annual medians must read as negative.
- **No claim that occupancy does not matter.** The result is that this effect is below the diary-to-diary
  spread on this design, not that occupancy is irrelevant.
- **No comparison with the published quasi-steady-state monthly figures.** That comparison is permanently
  informational, has no band and will never get one, and putting it in a results figure would read as a
  validation. It stays in the text.
- **No green, no red, no tick, no cross.** Nulls have no winner.
- **No error bars or confidence intervals**; the between-diary spread is already the dispersion the
  figure reports, and drawing a second one would double-count it.
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, 300 dpi minimum, full page width, readable at 180 mm. Sans-serif throughout. Colour-blind
safe and legible in greyscale; sign and length carry the meaning, never hue.

**Caption to install with it:**

> **Figure 7.** - Occupancy effect on heating, and the ordering that survives.

**Caption rule, set by the author 2026-09-14: every table and figure caption in this paper is ten words or fewer.** Anything a reader needs beyond the caption belongs in the body text of the section that cites the figure, not in the caption and not printed inside the image.

