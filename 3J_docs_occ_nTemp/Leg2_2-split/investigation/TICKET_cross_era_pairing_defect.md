# TICKET — Cross-era "paired design" claim does not hold across eras

**Status:** FILED, not fixed (out of scope for the Step-8/9 2-split cascade)
**Filed:** 2026-07-17
**Severity:** Documentation / claim-scope — NOT a results defect
**Blocking?** No. Does not affect any published number; affects only how the "paired" comparison is described.

---

## Aim

Record a scope limitation in the paired-Monte-Carlo design so the manuscript does not
over-claim variance reduction across the full 2005→2030 trajectory.

## The defect

`Step8_docs/3rdJ_08B_run_paired_mc.py:196` claims a **paired design**: the same random
seed is reused across scenarios so that Monte-Carlo draws are common-random-number (CRN)
paired, cancelling sampling noise in scenario *differences*.

This pairing is **valid only within a shared household pool**. It does **not** hold across eras:

- **Historical scenarios (2005 / 2010 / 2015)** draw from the **2,883** real 2022 GSS
  respondents (historical stock built in `3rdJ_08A_gen_historical_schedules.py:495`).
- **2022 / 2030 scenarios** draw from the full post-exclusion frame of **23,150** HH.

Same seed, **different pools** ⇒ the *n*-th draw in a historical scenario and the *n*-th draw
in a 2022/2030 scenario are **not the same household**. CRN pairing therefore cancels noise
only for comparisons **within** an era-pool:

- ✅ **Valid pairing:** 2022 ↔ 2030 bands (conservative / hybrid / fullyhybrid) — same 23,150-HH pool.
- ✅ **Valid pairing:** among the historical years that share the 2,883-HH stock.
- ❌ **Invalid pairing:** any comparison spanning the 2,883-HH historical stock and the
  23,150-HH 2022/2030 pool — i.e. the **2005→2030 longitudinal trend** is *not* CRN-paired.

## Why it is out of scope here

- **Pre-existing.** The June single-channel structure had the same two-pool design; this is
  not introduced by the 04T rake or the multi-zone injection fix.
- **Not a results error.** Each scenario's absolute energy/occupancy estimate is unbiased;
  only the *variance-reduction efficiency* of cross-era *differences* is weaker than the
  within-pool case. Nothing published is wrong — the point estimates stand.
- Fixing it would mean re-architecting the sampling to share one pool across all eras, which
  changes the historical-stock definition (deliberately the real 2022 respondents) — a design
  change, not a bug fix. Do **not** touch the pipeline for this.

## Recommended manuscript action (one sentence)

State that CRN pairing (and its variance-reduction benefit) applies to the **2022↔2030 band
comparisons** and within the historical stock, **not** along the 2005→2030 trend, where
historical scenarios draw from the 2,883 real 2022 respondents and 2022/2030 draw from the
23,150-HH frame. Report cross-era trend differences as unpaired.

## Verification note

Fact established from pipeline structure and the frozen frame numbers
(historical stock = 2,883 real 2022 GSS respondents at `3rdJ_08A:495`; frame = 23,150 HH).
Confirm against the archived June run manifests before citing in the manuscript
(the two-pool split should appear identically there).

## Disposition

File and leave. Revisit only if a future revision needs a genuinely paired longitudinal
trend, which would require a shared cross-era household pool by design.
