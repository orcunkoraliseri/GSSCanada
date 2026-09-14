# Figure 2 prompt — the leave-one-country-out design and the two nulls

**Written 2026-09-13 for `4J_manuscript_submission.md` §1.5, referenced as Figure 2.**
**Not generated here.** The author generates the image; this file is the specification.
Install to `writing/submission/figures/Figure_02_loco_design.png` and verify against the installed
manuscript, not against this file.

🔴 **No value in this prompt may be altered.** Every number below is read from the manuscript, which reads
it from the step documents. If a number looks wrong, stop and check the manuscript rather than adjusting
the drawing.

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

If the drawing achieves those three and nothing else, it is a success.

---

## Structure

A left-to-right flow in three vertical bands. One fold is drawn; a small caption note says the same
structure runs three times, once per country.

### Band 1 (left) — the corpus, split

Three country tiles stacked: **Spain**, **Italy**, **United Kingdom**. Draw the fold in which **Britain is
held out**, because it contains the closest miss and is therefore the fold most favourable to the model;
choosing the most favourable fold for the illustration is deliberate and the caption says so.

- Spain and Italy tiles are **solid** and carry a label **"training, 2 countries"**.
- The Britain tile is **outlined only, not filled**, and carries **"held out, never seen in training"**.
- Under the three tiles, one small line: **73,254 diaries · 2,024,068 episodes · one wave each**.

### Band 2 (middle) — the two candidates, side by side, visually parallel

🔴 **The two candidate boxes must be the same size, the same shape and the same visual weight.** Neither
may look like the hero. This is a fairness drawing.

**Upper candidate — the model.**
"Fine-tuned language model" · "7.30 B backbone, low-rank adapter, 79.95 M trainable parameters" ·
"grammar-constrained generation" · output label **"5,200 generated diaries"**.

**Lower candidate — the null.**
"Raked donor pool" · "real Spanish and Italian diaries, reweighted by iterative proportional fitting" ·
"every day is a day somebody lived" · output label **"reweighted real diaries"**.

### Band 2b — the shared input, drawn ONCE and split to both

🔴 **This is the load-bearing element of the whole figure.** A single box labelled

> **Britain's published census marginals**
> age band · sex · household type · economic status
> *published by the national statistical office before either candidate existed*

has **one** arrow leaving it that **forks** into the two candidate boxes. It must be visually obvious that
this is one source feeding both, not two similar sources feeding one each. Do not draw two boxes. Do not
draw two separate arrows from two copies.

Beside the fork, small, set apart: **"the same tables, the same geography, the same strata"**.

### Band 3 (right) — scoring

Both candidates' outputs converge on one scoring box:

> **Time-budget mean absolute error**
> against Britain's own published tables
> three age bands: Y25-44 · Y45-64 · Y_GE65

Below it, the verdict strip, which is the figure's punchline. Three small paired bars, one pair per age
band, model against null, with the values printed:

| Band | Model | Null |
|---|---|---|
| Y25-44 | 58.91 | 21.79 |
| Y45-64 | 60.44 | 19.21 |
| Y_GE65 | 21.24 | 18.54 |

Axis label: **minutes per day, lower is better**. The null bar is shorter in all three pairs.

Under the bars, one line in the figure's largest non-title text:

> **The null wins every band of every fold. 9 of 9. Closest miss 2.70 min/day.**

Far right, small and greyed, the held-out country's real diaries with a single label **"ground truth,
never seen by either side until scoring"**.

---

## Two annotations that must appear

Small, unobtrusive, but present. Each answers an objection a reviewer will raise at the figure rather than
at the text.

**(a) On the shared marginals**, near the fork:
> *Both sides get the same marginals by design. Giving the null weaker ones would convert a null into a
> handicap.*

**(b) On the null's construction**, near the lower candidate:
> *The raking starts from a uniform seed, so the donor surveys' own weights are discarded. The null is not
> given an advantage the model does not have.*

---

## What must NOT appear

- **No accuracy or quality claim for the model.** No tick marks, no "improved", no green on the model side.
- **No colour that codes one candidate as good and the other as bad.** Use the same palette for both; the
  bar lengths carry the result.
- **Do not draw a fourth country.** The corpus is three.
- **Do not draw a forecast, a year axis, or a 2030 anywhere.** There is no forecast in this paper.
- **Do not draw a Step 12 or any downstream box beyond scoring.** This figure covers the transfer test
  only; the pipeline figure is Figure 1.
- **Do not draw the privacy audit, the archetypes, or EnergyPlus here.**
- **No em dashes and no en dashes** in any label.

---

## Format

Vector-first, exported at 300 dpi minimum, single column width or full width, readable at 90 mm. Sans-serif
throughout. Colour-blind-safe palette; the figure must survive greyscale printing, so the two candidates
must be distinguishable by shape or fill pattern and not by hue alone.

**Caption to install with it:**

> **Figure 2.** - Leave-one-country-out design, drawn for the Britain fold, which contains the closest
> miss. Both candidates receive the identical set of published marginals for the held-out country and are
> scored against a reference neither produced. Bars give time-budget mean absolute error in minutes per
> day, lower being better. The same structure runs three times, once per country.
