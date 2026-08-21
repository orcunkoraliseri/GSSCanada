# Review — SOFTX-D-26-00798R1

**Manuscript.** *BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research*
**Round.** R1 (I was not one of the R1 reviewers; I have read the R1 comments and the author's responses)
**Reviewer.** O. K. Iseri, Concordia University
**Date.** 2026-08-21 · **Due.** 2026-09-04

> Confidential. Prepared for the SoftwareX editors only.

---

## 0. Recommendation

**Major revision.**

I want to be clear about why this is not "minor", because the R1 round went well and the
author deserves an explanation. The responses to R1 are, almost without exception, good ones.
Comment 8 in particular — the withdrawal of the 1200-fold claim — was handled better than most
authors handle such a challenge: the author did not merely soften the number, he diagnosed
*why* it was not a measurement (the value was governed by the smoothing constant ε, not by any
behavioural error) and removed it. That is the correct instinct, and it is the reason I think
the remaining problems are fixable.

The reason for "major" is that I installed the released package and audited the probability
table it ships. **Four of every twenty-four hours in the simulated day are not ATUS-grounded at
all — they are a hard-coded constant — and the four hours before them are built on between 4%
and 38% of the sample.** The two probability tables inside the same wheel contradict each other
about when people go to sleep. This affects the numbers in Section 3, not only how they are
described, and it lands on the evening window the demand-response scenarios are about.

Everything I report below is reproducible in under a second from a clean `pip install buildocc`,
with no API key and no network. I have attached the two scripts (`verification/`). I would ask
the editor to pass them to the author; they are written to be run, not to be taken on trust.

The software itself is well built. The three-layer interface is sensibly factored, the plugin
registry via entry points is the right mechanism, all three artefact links resolve, versions
agree across GitHub, PyPI and Zenodo, and the test suite runs offline against a mock provider.
Ten minutes of installing raised my opinion of the engineering. That is exactly what a SoftwareX
artefact should do, and I would like to see this published once Section 3 rests on solid ground.

---

## 1. SoftwareX criteria

| Criterion | Rating |
|---|---|
| Significance / impact of the software | **Good** — the plugin architecture is a real contribution; the field needs this kind of scaffolding |
| Quality of software and documentation | **Good** — clean layering, docstrings, offline tests, honest `BaseX` extension points |
| Were you able to install and run it? | **Yes** — `pip install buildocc`, imported as `occupant_agent`, ran scheduler-only work with no key |
| Quality of the manuscript | **Fair** — well written and responsive, but Section 3 currently reports numbers that do not measure what they are said to measure |
| Overall | **Major revision** |

---

## 2. Major points

### Point 1 — The shipped grounding table has no data for a third of the day, and the scheduler fills the gap with a hard-coded constant

This is the finding that drives my recommendation. It is not an inference about ATUS; it is a
property of the file inside the wheel, and the package contradicts itself about it.

`occupant_agent/data/time_at_activity.csv` is the table `ActivityScheduler` turns into
P(category | stratum, day type, hour). Because the eight categories of Table A.1 partition the
day, `weighted_pct` must total 100.0 in every (stratum, day type, hour) cell. It does not:

| Hours | Coverage (sum of `weighted_pct`) |
|---|---|
| 00–03 | **0.00 in every cell — no data at all** |
| 04–17 | 96.5 – 100.0 (sound) |
| 18 | 94.3 – 98.6 |
| 19 | 91.7 – 96.5 |
| 20 | 82.3 – 89.1 |
| 21 | 64.6 – 70.7 |
| 22 | 28.8 – 38.4 |
| 23 | **4.0 – 8.0** |

Three consequences follow, and each is checkable:

**(a) Hours 00:00–03:59 are fabricated.** `grounding/scheduler.py::_sample_category` returns the
literal string `"sleeping"` for hours 0–3, with the source comment *"Hours 0-3 are all-zero in the
bundled CSV (ATUS extended-hour encoding limitation)."* Sixteen of every 96 timesteps — one sixth
of every simulated day — are therefore a constant chosen by the author, not a draw from ATUS.
Section 2.2 and Appendix A describe the scheduler as ATUS-grounded without qualification. If this
survives revision it must at minimum be stated in the text; I think it should instead be fixed.

**(b) The evening is built on a shrinking and non-random subsample.** By 23:00 the table describes
4–8% of the stratum. Whatever normalisation is applied, an hour reconstructed from 6% of
respondents is not a population distribution, and the missing 94% are not missing at random —
they are the ones who have gone to bed.

**(c) The package's own two tables disagree.** `time_of_day_distributions.csv`, describing the
same O1 respondents, puts **51.8% of all sleeping time as beginning between 20:00 and 23:59**
(20:00 → 6.9%, 21:00 → 14.5%, 22:00 → 17.1%, 23:00 → 13.3%). The table the scheduler actually
samples puts P(sleeping) at **0.020–0.078 across every one of those hours** — it never rises. For
contrast, the morning hours, where coverage is complete, behave exactly as they should: P(sleeping)
falls 0.898 → 0.759 → 0.534 → 0.349 → 0.207 from 04:00 to 08:00. The defect is confined to the
end of the diary day.

**The likely cause, and it looks cheap to fix.** ATUS diaries run *"starting at 4 a.m. the previous
day and ending at 4 a.m. on the interview day"* (BLS ATUS User's Guide, module S4). The 27.05%
spike at hour 4 in `time_of_day_distributions.csv` is the signature of that boundary — overnight
sleep in progress at 04:00 is recorded as beginning at 04:00. The coverage profile above is what
happens when a 04:00–04:00 diary is binned on a 00:00–24:00 wall clock and respondents drop out
of the tally as they enter their final overnight episode. Wrapping the diary day at 04:00 instead
should recover both the missing four hours and the evening sleep onset in one change.

**Why this is not cosmetic.** The TOU peak in Section 3.3 is 16:00–21:00 and the demand-response
signal is delivered at 18:30. Coverage across 18:00–21:00 runs from ~97% down to ~67% and is
falling steeply. Table 7's "Peak SP" column and the whole of Table 8 sit on the degrading edge of
the table. I am not claiming those results are wrong — I am saying that as things stand neither
the author nor a reader can tell, and that has to be resolved before the numbers mean anything.

*Reproduce:* `verification/01_grounding_table_coverage.py`.

---

### Point 2 — Tier 1 measures sampling noise, and the author has already accepted the argument in its other form

Section 3.2 reports mean per-hour KL divergence over 180 simulated days: 0.0181, 0.0253, 0.0184,
0.0092 nats for O1–O4. In the R1 responses the verb "confirm" is retained specifically for Tier 1,
"whose divergence comparison over 180 simulated days per stratum does support it."

I do not think it does, and the reason is the same one the author gave when withdrawing the
1200-fold claim. There the argument was: *the fixed baseline's value is governed by ε rather than
by behavioural error, so it is not an effect size.* The identical objection applies to the other
column, with a different constant. The scheduler draws from P; Tier 1 then measures the divergence
between P and draws from P. For n draws over K categories that divergence has a floor of
(K−1)/2n even when the generator is perfect, and with K = 8 the floor is the same order as the
reported values.

Rather than argue this, I measured it. I drew from the scheduler's *own* tables — a generator with
zero fidelity error by construction — and evaluated the manuscript's Equation (1) with the
manuscript's ε at the same n:

| Stratum | Reported | Null, perfect sampler (mean, 95% interval) |
|---|---|---|
| O1 | 0.0181 | 0.0219 [0.0122, 0.0357] |
| O2 | 0.0253 | 0.0296 [0.0204, 0.0424] |
| O3 | 0.0184 | 0.0239 [0.0144, 0.0367] |
| O4 | 0.0092 | 0.0139 [0.0056, 0.0279] |

Under this reading every reported value is *below the mean divergence a perfect sampler produces*
and inside its 95% interval — the test cannot discriminate. Note also that the reported ordering
(O2 > O3 ≈ O1 > O4) is exactly the null's ordering: it tracks how concentrated each stratum's
activity distribution is, not how faithful the model is. That O4, the stratum the manuscript calls
"the noisiest of the four", scores *best* is a symptom of this.

**One honest caveat.** The above assumes 180 days split by calendar into ~129 weekday and ~51
weekend days. If instead 180 days of *each* type were simulated, the null drops to 0.0027–0.0095
and the reported values sit about 3× above it — a real but small margin, and one that is
suspiciously constant across strata. **The manuscript does not say which, and the result is not
interpretable without it.** That ambiguity is itself worth fixing.

*What I would ask for.* (i) State n per (hour, day-type) cell. (ii) Report the null — either the
analytical floor or the bootstrap above; it costs seconds. (iii) Rename the tier. It demonstrates
**sampler correctness**, which is a legitimate and worthwhile thing to demonstrate, and the paper
would be stronger for claiming it accurately than for claiming fidelity it cannot show. (iv) If a
fidelity claim is wanted, fit on ATUS 2022 and test against 2023; the data are already in hand.

*Reproduce:* `verification/02_durations_and_null.py`.

---

### Point 3 — There is no duration model, and the consequences are measurable in the released package

`ActivityScheduler.sample(timestep)` depends only on `timestep.hour` and the weekday/weekend flag.
It carries no state and no dependence on the previous timestep, so the four 15-minute slots within
an hour are i.i.d. draws from one distribution. Episode lengths are therefore geometric by
construction, and a divergence computed on per-hour marginals cannot detect this, because any
temporal reordering leaves the marginals unchanged.

The package ships the real ATUS episode durations in `activity_frequency_<stratum>.csv`
(`mean_duration_min`), so the comparison is entirely internal to the author's own artefact:

| | O1 real → sim | O2 real → sim | O3 real → sim | O4 real → sim |
|---|---|---|---|---|
| Sleeping | 338 → 67 (**5.1×**) | 318 → 79 (4.0×) | 314 → 85 (3.7×) | 325 → 67 (4.9×) |
| Work | 203 → 28 (**7.4×**) | — | 193 → 30 (6.5×) | 116 → 16 (7.2×) |
| Food prep | 66 → 16 (4.3×) | 63 → 16 (3.9×) | 66 → 16 (4.2×) | 77 → 17 (4.5×) |
| Television | 78 → 15 (5.1×) | 89 → 16 (5.6×) | 68 → 15 (4.4×) | 88 → 15 (5.7×) |
| Transitions/day | 41.1 | 29.4 | 38.8 | 36.2 |

Every category except the 172-code "Other" residual collapses to one or two timesteps. Real
diaries show roughly 16–22 activity transitions per day; the scheduler produces 29–41. Sleep is the
only category that survives at all, and it does so *only because of the hard-coded 00:00–03:59
block from Point 1* — which is to say the one realistic duration in the model is the one that is
not grounded.

This matters physically, not just statistically. Fragmented occupancy prevents occupancy-sensor
timeouts and thermostat setbacks from ever engaging, and smears clustered appliance events into
low-power noise; the reported sensitivities in the building simulation literature run to tens of
percent on lighting and HVAC. For a platform whose stated purpose is co-simulation with
EnergyPlus, duration realism is a functional requirement rather than a statistical nicety.

*What I would ask for.* Report mean episodes per day and the episode-length distribution against
the ATUS reference, per stratum — both references already ship with the package. If the intended
scope is "hour-marginal grounding, not a duration model", say so plainly in Section 2.2 and in the
limitations; that is a defensible scope, but it has to be declared, because a reader will otherwise
assume the generated schedules are usable as load-model inputs.

*A smaller point in the same area.* Figure 3's caption reads the model as producing "smooth
transitions" against a step-function baseline. A real time-use diary **is** a step function —
episodes have durations and the state is constant within them. Smoothness here is an artefact of
averaging over 180 days, and describing it as realism inverts the levels of description.

---

### Point 4 — The four strata are not cited into a twenty-year literature that did exactly this

I searched the manuscript for the lineage of stochastic occupancy models built from national
time-use surveys. Not one of the following appears: Richardson, Widén & Wäckelgård, Page, Wilke,
Aerts, Flett & Kelly, McKenna, Tanimoto, Buttitta, Mitra, Malekpour Koupaei, Chen/ResStock, Osman &
Ouf, Vosoughkhosravi. "Markov" occurs twice, both times as an example of something a user *could*
plug in via `BaseScheduler`.

I raise this for two reasons, and neither is about credit.

**It overstates novelty by omission.** "National time-use survey → conditional activity probability
table → sampler" has been standard practice since Richardson et al. (2008) and Widén & Wäckelgård
(2010). The novel contribution here is the *agent and interface layer*, which is real and does not
need the grounding pipeline to be novel as well. The paper would be stronger, not weaker, for
saying so.

**It costs the paper its baseline.** The fixed hour-of-day rule in Table 6 is not the comparator
this field uses; it was settled as inadequate around 2008. The accepted statistical baseline is a
first-order inhomogeneous Markov chain fitted to the *same* microdata. That baseline would also
resolve Point 3, since a Markov chain at least has dwell times. And — this is the part I would
stress — the manuscript's own architecture already names it: implementing it is one `BaseScheduler`
subclass, which is precisely the extensibility the paper advertises. Demonstrating the plugin
system by implementing the field's standard baseline inside it would strengthen the software
contribution and the validation at the same time.

Two review articles are the efficient entry points if the author wants one citation rather than
twelve: Osman & Ouf (2021), *Building and Environment* 196, 107785, and Vosoughkhosravi, Jafari &
Zhu (2023), *Energy and Buildings* 294, 113245 — the latter is specifically a review of ATUS in
building-energy occupant modelling.

Separately, **Deng & Peng (2026)**, *Buildings* 16(5), 887, `10.3390/buildings16050887`, is an
open-access LLM-agent framework for simulating occupant demand-response behaviour. It is the
closest published neighbour to this work and is uncited. I have no connection to it.

*Every DOI I list in this review resolved through CrossRef with matching title, journal, volume,
issue, pages and first author on 2026-08-21. I have no co-authorship or other interest in any of
them, and I am not asking for citations to my own work.*

---

## 3. Points on specific claims

### Point 5 — Stratum O4 is very probably the wrong ATUS filter, not merely a small sample

R1 Reviewer #1 (Comment 5) read n = 107 as a small-sample problem, and the author responded by
marking the O4 interpretation provisional. That was a reasonable response to the question asked,
but I think it is the wrong diagnosis, and the fix is better news for the author than the caveat.

Table 2 defines O4 as **"Unemployed adult — Not employed, age 25–44"**. Those are two different
populations. In ATUS, `TELFS` codes 3 and 4 are unemployed (on layoff / looking); code 5 is not in
the labour force. *Unemployed* is `TELFS ∈ {3,4}`; *not employed* is `TELFS ∈ {3,4,5}` and includes
homemakers, students, the disabled and the early-retired. For ages 25–44 pooled over 2022–2023
these differ by roughly an order of magnitude — on the order of 10² versus 10³ respondents.

n = 107 is consistent with the label and not with the definition. The manuscript uses "unemployed"
in every results sentence and "not employed" in the table that defines the stratum.

This is worth resolving because if the intended stratum is *not employed*, the corrected sample is
several times larger, the 15-minute tables stop being "the noisiest of the four", and the
provisional caveat added at R1 can simply be withdrawn. If the intended stratum really is
*unemployed job-seekers*, then the label is right, the definition line needs correcting, and the
stratum should be renamed throughout, since an unemployed 25–44-year-old is a much narrower
occupancy archetype than the text implies.

**Related, and it should be checked at the same time:** Table C.1's caption states that the work
location columns are *"restricted to employed respondents on diary days with a work episode"*, yet
values are reported for both non-employed strata — O2 (8.1 / 50.1) and O4 (0.0 / 98.4). Under the
stated restriction those cells should be empty. The columns also do not close: O1 94.5, O3 94.6,
O4 98.4, and **O2 58.2**. Publishing the exact variable-level filter for each stratum (the `TEAGE`,
`TELFS`, `TRDPFTPT`, `TRNUMHOU`, `TRCHILDNUM`, `TEWHERE` conditions, and the universe for each
column) would settle all of this at once and would materially help anyone reproducing the tables.

---

### Point 6 — The social-norm claim cites two papers that contain no social-norm evidence

Section 3.3 currently reads:

> "Social norm signals (Type C) drew no acceptance in any stratum, consistent with field evidence
> on the limited efficacy of peer-comparison messaging (Gyamfi and Krumdieck 2011; Albadi and
> El-Saadany 2008)."

I checked both. Gyamfi & Krumdieck (2011), *Energy Policy* 39(5), 2993–3004, is a stated-preference
survey of ~194 households in Christchurch testing price, environmental and supply-security
motivators. Albadi & El-Saadany (2008), *Electric Power Systems Research* 78(11), 1989–1996, is a
power-systems review of DR program classifications. **Neither reports any peer-comparison or
social-norm result.** Neither can support the sentence.

The underlying claim also needs scoping, and here I want to be fair to the author, because the
scoped version is defensible. For *chronic electricity conservation*, peer comparison is among the
best-evidenced behavioural interventions in energy: Allcott (2011), *Journal of Public Economics*
95(9–10), 1082–1095, reports ~2% average reduction across ~600,000 households, rising to ~6% in the
highest-consumption decile. Calling that "limited efficacy" would be a misreading. But this paper
is not about billing-cycle conservation — it is about acceptance of a signal delivered at 18:30
during a peak event, and for *event-based* peak response the evidence genuinely does show moral
suasion decaying quickly relative to price signals. Ito, Ida & Tanaka (2018), *AEJ: Economic Policy*
10(1), 240–267, `10.1257/pol.20160093`, is the head-to-head field experiment: moral suasion produced
an effect on the first event that had decayed to statistical insignificance by the third or fourth,
while critical-peak pricing held.

So: keep the finding, narrow the claim to peak events, and cite the work that measured it. One
sentence distinguishing kWh conservation from kW peak response would also pre-empt a very common
confusion in this literature.

---

### Point 7 — Reproducibility: the model version is never named

The R1 revision to Section 2.4 is a real improvement and I have little to add to the wording. One
technical refinement: determinism can fail *within* a fixed provider and version, because the
logits themselves are not bit-stable — the dominant practical cause is batch-size-dependent
reduction kernels, where a request served under a different dynamic batch takes a different
accumulation order (see He, *Defeating Nondeterminism in LLM Inference*, Thinking Machines Lab,
2025). "Relative to one specific set of model weights" is therefore slightly too generous to T = 0.
A one-clause hedge — "and even within a fixed version, batching and kernel selection can perturb
borderline logits" — would make the paragraph correct.

**The substantive gap:** the manuscript states the principle that reproducible studies should record
the provider and model version, but **no provider or model version string appears anywhere for any
reported result.** Tables 7 and 8 and every agent quotation came from some specific model. For an
open-science paper in a software journal this is the one omission I would call blocking, and it is
also the cheapest thing in this review to fix — one sentence in Section 3.

---

## 4. Minor points

1. Table A.1 lists eight categories; Figure 3 plots five. Neither says which three were dropped or why.
2. "Other" carries 172 of the 220 tier-3 codes, including all travel. A category holding most of the
   codebook limits what any category-level divergence can show; worth one line of acknowledgement.
3. The abstract's "16,684 respondents" overstates the grounding: 6,041 are in the four strata and
   10,643 are the unused residual. Both numbers are given correctly in Appendix C — the abstract
   should use the one that describes the tables.
4. Weight pooling: 2022 and 2023 both use `TUFINLWGT`, so pooling is admissible (the comparability
   condition in the BLS User's Guide is satisfied). Worth naming the weight variable and stating
   that condition — it is a question readers will have, and the answer here is favourable.
5. Section 3.3's five seeds vary the agent's sampling, not the grounding table, so the counts
   measure LLM variability at fixed demographics. The revised text is careful about significance;
   one clause on *what* the seeds vary would complete it.
6. Table 7: `move_room` at 17.0–21.5% of timesteps is one room change every 70–90 minutes sustained
   across the day. Worth a sanity check against the same duration reference as Point 3.
7. Section 2.7 states that cost bounded the simulation lengths but still reports no measured cost.
   A single figure — tokens per agent-day, or dollars for one reported run — would make the
   constraint concrete and is information readers will actually use.
8. 8 of 35 references (~23%) are self-citations. Several are apt; a few in the introduction read as
   substitutable and could give way to the lineage in Point 4.
9. The Zenodo capsule predates this revision. If code changed, deposit a new version and cite that
   DOI, so the archived artefact matches the paper.
10. Reference [3] is cited three times for three different claims. Please point each to the specific
    result relied on.
11. The typeset PDF loses inter-word spaces in several places ("BuildOccisdistributedasthepackage",
    "ATUSmicrodata"). A LaTeX/font issue for production, not the author's argument.

---

## 5. What I checked, and what I did not

**Checked.** Installed `buildocc` 1.0.0 from PyPI into a clean venv (Apache-2.0, Python ≥ 3.11,
imports as `occupant_agent` — correctly documented as of this revision). GitHub, PyPI and Zenodo
links all resolve and agree on version. Ran the scheduler for all four strata under Tier 1
conditions (180 days × 96 steps) with no LLM calls. Audited `time_at_activity.csv`,
`time_of_day_distributions.csv` and `activity_frequency_*.csv`. Read `grounding/scheduler.py`.
Computed the null for Equation (1) by drawing from the package's own tables. Table 7 rows sum to
100.0; Figure 4 bar counts reconcile with Table 7 × 288; 1,393 + 2,351 + 2,190 + 107 = 6,041 and
6,041 + 10,643 = 16,684. Table A.1's ATUS code filters match the lexicon. Confirmed the ATUS
4 a.m.–4 a.m. diary convention and the 10%-per-weekday / 25%-per-weekend-day sample allocation
against the BLS ATUS User's Guide. Verified every DOI cited above through CrossRef.

**Not checked.** I did not run the LLM-dependent paths, so Tiers 2 and 3 rest on the manuscript's
account. I did not obtain ATUS microdata and re-derive the stratum counts — Point 5 rests on the
`TELFS` code structure and the manuscript's own internal inconsistency, not on my recomputation of
n. My null in Point 2 is a bootstrap over the shipped tables, not a replication of the author's
pipeline; if his n per cell differs from either reading I gave, the numbers move and I have said so.
I did not evaluate the EnergyPlus co-simulation path.

---

## 6. To the Editor

Three notes.

**On the recommendation.** I have set this to major revision on the strength of Point 1, which
concerns the data inside the released artefact rather than the manuscript's prose. I would be
glad to look at a revision. If the author wraps the diary day at 04:00 and the coverage gap
closes, Points 1 and 3 largely resolve together and the remaining items are ordinary revision work.

**On the two verification scripts.** Please pass `verification/01_grounding_table_coverage.py` and
`verification/02_durations_and_null.py` to the author with this review. They need only
`pip install buildocc`, take about a second, and make no network or API calls. Every table in
Points 1–3 is their output. I would much rather the author reproduce and check my arithmetic than
take my word for it — and if I have misread the data, these are the files that will show it.

**No ethical concerns.** Nothing in this manuscript raised any question of plagiarism, fraud or
misconduct. The R1 responses are candid, including where they concede error, and the artefact is
genuinely open. My criticisms are technical.

I have no conflict of interest with the author and no connection to any work I have recommended
citing.
