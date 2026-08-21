# Review — SOFTX-D-26-00798R1

**BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research**
Reviewer: O. K. Iseri, Concordia University · 2026-08-21 · Confidential

**Recommendation: minor revision.**

The software is well built and the R1 responses are good — the withdrawal of the 1200-fold claim
was handled exactly right. I installed the package and ran the scheduler; everything below is a
small, concrete fix.

**Ratings** — Significance/impact: **Good** · Software and documentation: **Good** · Able to
install and run: **Yes** (`pip install buildocc`, imports as `occupant_agent`, ran with no API
key) · Manuscript quality: **Fair to good**

---

## Main points

- **The shipped activity table has no data for hours 00:00–03:59, and thins out through the
  evening.** In `occupant_agent/data/time_at_activity.csv` the eight category percentages should
  total 100 in every (stratum, day type, hour) cell. They total 0.00 for hours 0–3, and 82 / 67 /
  35 / 6 for hours 20 / 21 / 22 / 23. `scheduler.py` fills hours 0–3 by returning the literal
  `"sleeping"`. This looks like an ATUS diary-day boundary issue — diaries run 4 a.m. to 4 a.m. —
  so **wrapping the day at 04:00 instead of binning on the wall clock should fix it in one place.**
  Please check, and either fix it or state it as a limitation.

- **A cross-check inside the package.** `time_of_day_distributions.csv` puts ~52% of O1 sleeping
  time as starting between 20:00 and 23:59, while the table above gives P(sleeping) = 0.02–0.08
  across those same hours. Worth reconciling the two files.

- **Tier 1 needs a null to be interpretable.** The scheduler draws from P and Tier 1 then compares
  P against draws from P, so the reported values partly reflect sampling noise. Drawing from the
  package's own tables and evaluating Eq. (1) at the same n gives 0.014–0.030 nats — the same range
  as the reported 0.0092–0.0253. The fix is small: **state n per (hour, day-type) cell and report
  the null alongside.** Consider renaming the tier "sampler correctness", which is what it shows,
  and which is a fair thing to claim.

- **Please add one duration statistic.** `sample()` depends only on hour and day type, so episode
  lengths are geometric by construction and per-hour marginals cannot detect it. Measured against
  the durations the package itself ships in `activity_frequency_*.csv`: mean sleep episode 67 min
  vs 338 real, work 28 vs 203, and 29–41 transitions per day. **Reporting mean episodes/day and the
  episode-length distribution would close this** — both references are already in the package. If a
  duration model is out of scope, that is fine, but please say so in Section 2.2.

- **Two citation fixes in Section 3.3.** Gyamfi & Krumdieck (2011) is a stated-preference survey on
  price / environment / supply security; Albadi & El-Saadany (2008) is a power-systems review of
  program types. **Neither contains a peer-comparison result.** The claim itself is defensible for
  *peak events* — Ito, Ida & Tanaka (2018), *AEJ: Econ. Policy* 10(1), 240–267,
  `10.1257/pol.20160093`, measured moral suasion decaying to insignificance by the third event. For
  billing-cycle conservation the evidence runs the other way (Allcott 2011, ~2%). Suggest swapping
  the citations and narrowing the sentence to peak events.

- **Please name the model version.** The paper correctly says reproducible studies should record
  the provider and model version, but no version string appears for any reported result. One
  sentence in Section 3.

- **Missing literature.** No citation to the time-use-survey occupancy modelling lineage
  (Richardson 2008; Widén & Wäckelgård 2010; Wilke 2013; Flett & Kelly 2016; on the ATUS side Mitra
  2020, Malekpour Koupaei 2022). Two reviews cover it in one citation each: Osman & Ouf (2021),
  *Build. Environ.* 196, 107785; Vosoughkhosravi et al. (2023), *Energy Build.* 294, 113245. Also
  **Deng & Peng (2026)**, *Buildings* 16(5), 887 — the closest published LLM occupant-agent work. A
  first-order Markov chain on the same ATUS data would be a stronger baseline than the fixed
  schedule, and would be one `BaseScheduler` subclass — a neat demonstration of the plugin system.
  *(I have no connection to any of these and am not requesting citations to my own work.)*

## Minor

- Table 2 defines O4 as "Unemployed adult — **Not employed**, age 25–44". In ATUS these are
  different filters (`TELFS ∈ {3,4}` vs `{3,4,5}`), differing by roughly an order of magnitude, and
  n = 107 matches the narrower one. Worth confirming — if the intended stratum is *not employed*,
  the sample is much larger and the R1 noise caveat could be dropped.
- Table C.1: the caption restricts the work-location columns to employed respondents with a work
  episode, but values are given for the two non-employed strata; and the columns sum to 94.5 / 58.2
  / 94.6 / 98.4 rather than 100. Publishing the exact variable filters would settle both.
- Table A.1 lists eight categories; Figure 3 plots five — say which and why.
- "Other" holds 172 of the tier-3 codes, including travel; worth one line of acknowledgement.
- The abstract's "16,684 respondents" — 6,041 are in the four strata; use that number.
- Name the ATUS weight variable used. (2022 and 2023 both use `TUFINLWGT`, so pooling is fine.)
- Section 2.7 says cost bounded the simulation length but gives no measured cost; one figure would help.
- Figure 3's caption contrasts "smooth transitions" with a step function; a real diary *is* a step
  function, and the smoothness comes from averaging over 180 days.
- The Zenodo capsule predates this revision — deposit a new version if the code changed.
- The typeset PDF loses inter-word spaces in places ("ATUSmicrodata") — a production issue.

## To the editor

Two short scripts reproducing every number above are attached in `verification/`. They need only
`pip install buildocc`, run in about a second, and make no network or API calls. Please pass them
to the author — I would rather he check my arithmetic than take my word for it. No ethical
concerns; no conflict of interest.
