# Review — SOFTX-D-26-00798R2

**BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research**
Reviewer: O. K. Iseri, Concordia University · 2026-09-09 · Confidential

**Recommendation: Accept.**

Every point from the first round has been fixed. I installed the released software myself
(`pip install buildocc==1.0.1`) and checked the shipped data directly rather than take the
response letter's word for it:

- The missing-hours bug (00:00–03:59 showing no data) is genuinely fixed — every hour of every
  stratum now adds up correctly.
- The reported sleep-episode durations match the shipped data almost exactly.
- The model names, category list, and package version all match what the manuscript now states.
- The author also found and fixed two further bugs on their own initiative while checking my
  comments, and explained both clearly. That is a good sign, not a concern.

One small thing I could not fully confirm: a null-comparison number in Table 6 came out a bit
different when I recomputed it myself from the same public formula and the same shipped data.
It does not change the paper's conclusion — I get the same result either way, the model matches
its own reference table. I've asked the author to double check that one number, but it is not
something that should hold up acceptance.

**Ratings** — Significance/impact: Good · Software and documentation: Good · Able to install and
run: Yes · Manuscript quality: Good.

No ethical concerns, no conflict of interest.
