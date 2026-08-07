# 8 Conclusion

This paper asked whether one jointly-trained occupancy model can drive four functionally distinct uses inside a single stacked building, and where the energy-use-intensity references built for single-use building stock do, and do not, still apply to such a building. Answering the first half of that question required building a shared-encoder Transformer with three time-use-survey decoder heads and a separate, non-survey side-track for the one use the source survey cannot see, then dispatching all four resulting channels into the same tower geometry through a per-space, exact-match routing key so that a missing channel falls back safely to the untouched code baseline rather than to an undefined state. Answering the second half required taking the resulting failing gates seriously rather than resolving them, which is where this paper's central contribution sits.

The evidence supports a clear pair of answers. First, four independent, per-use occupancy channels can be jointly trained and injected into one mixed-use tower without collapsing into one blended signal, and doing so is additive on the two-channel construction stage this project grew from in the specific, evidenced sense that a missing channel is handled safely and the underlying tower geometry is confirmed unchanged, without claiming a bit-identity between construction stages that was not tested. Second, three of the four channel-level energy-use-intensity gates fail, and in each case the failure is a finding about whether a reference band built for single-use stock applies to a stacked mixed-use tower, not a defect in the occupancy model that produced the injected schedules. The office gate fails alongside its own uninjected, occupancy-free control, which fails the same floor on its own. The hotel gate's 56 cells separate into two prototype-driven clusters with a gap wide enough, relative to the band's own width, to decide most of the verdict before any occupancy signal is injected. The retail gate fails a median-in-band rule chosen in advance of the numbers, on a channel this study's own review found has no population-level, time-of-day presence reference to validate against at all. In every one of the three cases, the reference value was left exactly where it started, and no scoring rule was swapped once it was known which rule would pass.

Taken together, these results establish that jointly-trained, per-use occupancy injection into a stacked mixed-use building is feasible with the architecture and dispatch mechanism this paper describes, and that the more immediate barrier to a clean validation story is not the occupancy model but the reference bands available to judge it, none of which were built with a stacked mixed-use tower in mind. The limitations set out in §7, an occupancy frame that cannot see hotel guests or retail staff, internal-gain parameters carried over unchanged from a single office reference, and a domestic-hot-water plant whose capacity pinning defeats a global correction, bound how far the present results generalise, and several of them point directly at what a following study would need to build: reference bands constructed for, and validated against, buildings that stack more than one use, rather than borrowed from single-use stock and applied to a tower they were never designed to score.

---

## Supplementary material

**Table A1.** *(insert `Table_A1_A2.md` here)*

**Table B1.** *(insert `Table_B1_improvement_rounds.md` here)*

**Table C1.** *(insert `Appendix_C_corrections.md` here)*

**Figure S3.** *(insert `Figure_S03_leg2_pipeline.png` here)*

