# V4-B2 — PRE-REGISTRATION for the residential sample

**Written 2026-08-06, BEFORE the first residential `eplusout.sql` was fetched.** Nothing below was
edited after any residential number was seen; corrections, if any, are appended under a dated heading.

---

## Why a sample, and why that is stated rather than worked around

The four published residential rows are **medians over 2,100 runs each — 8,400 files at ~43 MB, about
12 hours of transfer.** The office half took all 252 because 252 is affordable. **8,400 is not.**

This is a **bandwidth** limit, not a permission limit — the user's amendment of 2026-08-06 (*"tu peux
obtenir ce que choses tu veux sur le speed, mais tu ne peux pas utiliser pour des simulations"*) allows
the retrieval. **So the honest report is a sample with an interval, not a silent extrapolation and not
a claim of blockage.**

**Design.** 100 runs per archetype, **drawn with a fixed seed (20260806)** from
`Leg2_2-split/Step8_docs/outputs_step8/agg/agg_meta.csv`, restricted to `channel == resid` and
`status == ok`, pooled over every scenario and city exactly as `build_eui()` pools them. The draw is
reproducible and **was not redrawn**. Each run's `eplusout.sql` is copied, read locally, and deleted.

**Interval.** The corrected median is reported with an **exact distribution-free confidence interval
from order statistics** — no normality assumption, no bootstrap. For n = 100 the 95 % interval is
`[x(40), x(61)]` of the sorted sample.

---

## The three predictions

### P1 — `OtherDwelling` and `HighRise` fall below their floors

`V4-B2_defect_reach.md` §3 said both fall **BELOW** their floors under **every** factor in the measured
range 1.4868–1.7601, which was the strongest claim in that document and the one it could not measure.

**Prediction:** both corrected sample medians land **below** their floors — `OtherDwelling` below
136.1, `HighRise` below 113.9 — **and the upper end of the 95 % interval stays below too.**

🔴 **Falsified if** either median lands inside its band, or the interval crosses its floor. In that
case §3's "BELOW, either way" is **withdrawn**, not softened.

### P2 — `SingleD` has no predicted direction

§3 said the sole published WARN (211.7, **above** the SHEU ceiling of 186.1) can move **either way** —
into the band, or out at the opposite end.

**No direction is predicted.** Whichever it does is reported as measured. **Recording "no prediction"
is the point:** a prediction invented after the fact would make this row look confirmatory whatever it
did.

### P3 — the sample must reproduce the published population

**Prediction:** the **shipped** sample median lands within ~2 % of the published value for every
archetype (211.7 / 140.0 / 177.5 / 143.0).

🔴 **If P3 fails, nothing else in this document means anything** — the sample would not be from the
published population, and P1/P2 would be measuring something else. **P3 is checked and reported first,
before any corrected number is read.**

---

## What is deliberately not claimed

- **Not** that the residential factor range equals the office one. The office half measured
  **1.5183–1.9062**, which already runs past the residential smoke range's top of 1.7601 — the factor
  tracks the building, so the two channels are not interchangeable and neither substitutes for the
  other.
- **Not** a corrected value for any run outside the sample.
- **Not** a disclosure route. This produces the magnitude; the erratum-versus-re-publication choice
  stays with the user, as §4.3 reserved it.

## Reopen trigger

If a future session can transfer the full 8,400, the sample medians are replaced by population medians
and **this document stays** as the record of what was predicted before they were known.
