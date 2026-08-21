# Review — SOFTX-D-26-00798R1

**BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research**
O. K. Iseri, Concordia University · 2026-08-21

**Recommendation: minor revision.** Well-built software, good R1 responses. I installed the
package and ran the scheduler; the points below are small, concrete fixes.

Impact: **Good** · Software & docs: **Good** · Installed and ran: **Yes** · Manuscript: **Fair to good**

## Main

- **No data for hours 00:00–03:59 in the shipped table.** In `data/time_at_activity.csv` the eight
  category percentages should total 100 per (stratum, day type, hour). They total 0.00 for hours
  0–3, and 82 / 67 / 35 / 6 for hours 20 / 21 / 22 / 23. `scheduler.py` fills hours 0–3 with the
  literal `"sleeping"`. ATUS diaries run 4 a.m. to 4 a.m., so **wrapping the day at 04:00 rather
  than binning on the wall clock should fix it in one place.** Please fix or declare it.

- **The package's two tables disagree.** `time_of_day_distributions.csv` puts ~52% of O1 sleeping
  time as starting 20:00–23:59; the table above gives P(sleeping) = 0.02–0.08 across those hours.

- **Tier 1 needs a null.** The scheduler draws from P and Tier 1 compares P against draws from P.
  Drawing from your own tables and evaluating Eq. (1) at the same n gives 0.014–0.030 nats — the
  range of the reported 0.0092–0.0253. **Please state n per (hour, day-type) cell and report the
  null.** Consider renaming the tier "sampler correctness", which is what it shows.

- **One duration statistic, please.** `sample()` uses only hour and day type, so episode lengths are
  geometric and hour marginals cannot detect it. Against the durations your own package ships in
  `activity_frequency_*.csv`: sleep 67 min vs 338 real, work 28 vs 203, 29–41 transitions/day.
  **Mean episodes/day plus the episode-length distribution would close it** — both references are
  already in the package. If a duration model is out of scope, say so in Section 2.2.

- **Two citation fixes, Section 3.3.** Gyamfi & Krumdieck (2011) is a stated-preference survey on
  price/environment/security; Albadi & El-Saadany (2008) is a power-systems review. **Neither
  contains a peer-comparison result.** The claim holds for *peak events* — Ito, Ida & Tanaka (2018),
  *AEJ: Econ. Policy* 10(1) 240–267, `10.1257/pol.20160093`. For billing-cycle conservation the
  evidence runs the other way (Allcott 2011, ~2%). Swap the citations, narrow to peak events.

- **Name the model version.** The paper says studies should record provider and model version, but
  no version string appears for any reported result. One sentence.

- **Missing literature.** The TUS occupancy lineage is uncited (Richardson 2008; Widén & Wäckelgård
  2010; Wilke 2013; Flett & Kelly 2016; ATUS: Mitra 2020, Malekpour Koupaei 2022). Two reviews cover
  it: Osman & Ouf (2021) *Build. Environ.* 196, 107785; Vosoughkhosravi et al. (2023) *Energy Build.*
  294, 113245. Also Deng & Peng (2026) *Buildings* 16(5), 887. A first-order Markov chain on the
  same ATUS data would be a stronger baseline than the fixed schedule — and one `BaseScheduler`
  subclass, so it also demonstrates the plugin system. *(No connection to any of these; not
  requesting citations to my own work.)*

## Minor

- Table 2: O4 is "Unemployed adult — **Not employed**, age 25–44". In ATUS these are different
  filters (`TELFS ∈ {3,4}` vs `{3,4,5}`), an order of magnitude apart; n = 107 matches the narrower.
  If *not employed* is intended, the sample is much larger and the R1 noise caveat can go.
- Table C.1: caption restricts work-location columns to employed respondents with a work episode,
  yet both non-employed strata have values; columns sum to 94.5 / 58.2 / 94.6 / 98.4, not 100.
  Publishing the exact variable filters settles both.
- Table A.1 has eight categories; Figure 3 plots five — say which and why.
- "Other" holds 172 tier-3 codes including travel — worth one line.
- Abstract's "16,684 respondents": 6,041 are in the four strata; use that.
- Name the ATUS weight variable. (2022 and 2023 both use `TUFINLWGT`, so pooling is fine.)
- Section 2.7 says cost bounded the runs but gives no measured cost.
- Figure 3 caption contrasts "smooth transitions" with a step function; a real diary *is* a step
  function, and the smoothness comes from averaging 180 days.
- Zenodo capsule predates this revision.
- Typeset PDF loses inter-word spaces ("ATUSmicrodata") — production issue.

## To the editor

Two scripts reproducing every number above are in `verification/`: `pip install buildocc`, ~1 s, no
network or API calls. Please pass them to the author. No ethical concerns, no conflict of interest.
