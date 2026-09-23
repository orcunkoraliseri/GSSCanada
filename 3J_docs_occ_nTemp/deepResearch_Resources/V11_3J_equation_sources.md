# V11. A source for every equation in the 3J Methods chapter

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H). Sections C to F of that template do not fit a citation
search; write `not applicable to this prompt` under each and put all findings in the tables below,
inside Section A.

> SCOPE GUARD. This is a citation search for the equations of one journal manuscript (Building and
> Environment, mixed-use tower energy simulation), unblocking plan item P6. For each equation we need
> one of three verdicts: **STANDARD** (a textbook or foundational-paper method; give the original
> source), **ADAPTED** (a published method changed in a stated way; give the closest published source
> and say what differs), or **OWN** (the authors' own definition; say NO SOURCE NEEDED, but still try,
> because a reviewer may know a precedent we do not). Do not change, improve or comment on the
> equations. `NOT FOUND` beats a guessed reference.

---

## Why we are asking

A Building and Environment reviewer already asked the companion paper (2J) for "a mathematical
formulation of models and metrics" with sourced equations (2J reviewer comment M2b/D11), and 3J
currently has only three displayed equations against fifteen described methods. Two equations below
(circular mean and circular standard deviation of a peak time) were already searched for 2J and vetted;
carry those sources over and confirm they still apply, rather than re-searching from zero.

## Part A. Carry-over check (already vetted in 2J, confirm applicability only)

2J's `dr_2J-17` (vetted, `2J_docs_occ_nTemp/.../dr_2J-17_equation_sources_gemini_results.md`) already
sourced these two, in the same functional form 3J uses on the daily **peak hour** of each occupancy
channel rather than on time-of-use generally:

- Circular mean: `h_bar = (24/2pi) * atan2(mean(sin theta), mean(cos theta)) mod 24`, `theta_i = 2*pi*h_i/24`.
  2J's source: Mardia and Jupp (2000), *Directional Statistics*, Sec 2.3.1, Eq. 2.3.1; Fisher (1993),
  *Statistical Analysis of Circular Data*, Sec 2.2, Eq. 2.9.
- Circular standard deviation: `sd_circ = (24/2pi) * sqrt(-2 * ln(R))`, `R = sqrt(mean(sin theta)^2 + mean(cos theta)^2)`.
  Same two sources, Mardia and Jupp Eq. 2.3.6; Fisher Eq. 2.12.

1. Open both DOIs/ISBNs again and confirm the equation and page/section numbers still match.
2. State explicitly whether the 3J usage (circular statistics of a *peak hour*, one value per
   building-city cell, rather than of time-of-use generally) is still a correct application of the same
   textbook definition, or whether it needs a different citation.

## Part B. New equations, not yet sourced

For each equation below, give: class (STANDARD / ADAPTED / OWN), recommended citation(s) in
author-year form, DOI or ISBN, whether you verified it via Crossref
(`https://api.crossref.org/works/<DOI>`), where in the source it appears (equation, table or page
number), and, if ADAPTED, one line on what differs from the published method.

**Eq. 1 (retail-presence derivation from paired location and activity codes; OWN, but check for a precedent)**
`AT_RETAIL = (occPRE = 5) OR [(occACT = 4) AND (occPRE in {5, 9})]`
Two survey columns (occPRE = coded location, occACT = coded activity) are combined so that a
"purchasing goods and services" activity only counts as retail-space presence when the paired
location is a store or an unspecified location, excluding purchases coded as occurring at the
respondent's own home (online shopping). Question: is there a published time-use-survey practice for
deriving a single-purpose presence indicator (retail, in this case) by combining a location code and
an activity code with this kind of AND/OR gating, in HETUS, ATUS, MTUS or building-occupancy papers
that consume time-use diaries? If none exists, say OWN, NO SOURCE NEEDED.

**Eq. 2 (multi-task training loss, fixed-weight scalarization with gradient-conflict correction)**
The three decoder heads (residential, office, retail presence) are trained jointly with fixed loss
weights 1.0 : 0.5 : 0.3 combined with "PCGrad pairwise gradient-conflict correction" against two
rejected dynamic alternatives, "SLAW" and "uncertainty weighting". Retail's approximately 2%-positive
class additionally carries a binary cross-entropy positive-class weight of 49, corrected at inference
by subtracting the logit shift `-ln(49)`. Needed:
(a) the original source of PCGrad (we believe this is Yu et al., "Gradient Surgery for Multi-Task
    Learning", NeurIPS 2020; verify title, venue, year and arXiv/DOI id);
(b) the original source of "SLAW" as a dynamic multi-task loss-balancing scheme (verify the expansion
    of the acronym and the paper it names);
(c) the original source of uncertainty weighting for multi-task losses (we believe this is Kendall,
    Gal and Cipolla, "Multi-Task Learning Using Uncertainty to Weigh Losses...", CVPR 2018; verify);
(d) a standard source for fixed-weight (static) scalarization of multiple task losses as the baseline
    multi-task-learning approach these two are compared against;
(e) a standard source for correcting a class-imbalance positive-class weight at inference by
    subtracting its corresponding log-prior/logit shift (for example Menon et al., "Long-Tail Learning
    via Logit Adjustment", or an earlier source if one better matches this exact operation).

**Eq. 3 (checkpoint-selection composite score; OWN, but check for a precedent)**
`val_score = mean(JS) + (1/2) * (g_home + g_work + g_retail) / 3`
where `mean(JS)` is the mean Jensen-Shannon divergence across heads against a validation baseline and
`g_home, g_work, g_retail` are per-head presence-rate gaps. Question: is there a published precedent
for a model-selection composite that sums a distributional-divergence term and a marginal-rate-gap
term for a generative sequence model? If none exists, say OWN, NO SOURCE NEEDED, and give the standard
definition and source for Jensen-Shannon divergence itself (we believe Lin (1991), IEEE Transactions on
Information Theory; verify).

**Eq. 4 (decode-time exclusivity projection)**
Independent per-head sigmoid outputs (residential, office, retail) can jointly fire at the same
30-minute slot; a "decode-time, threshold-normalized argmax projection" forces exactly one channel (or
none) per slot before the output is used downstream, reported as an Impossible-State Rate (ISR) gate
(raw ISR must be at or below 0.5%, projected ISR must reach exactly 0%). Question: is there a published
precedent for converting independent multi-label sigmoid outputs into a mutually exclusive decision by
a threshold-normalized argmax, in multi-label-to-multi-class conversion literature or in occupancy/
activity-recognition modelling specifically? If none exists, say OWN, NO SOURCE NEEDED.

**Eq. 5 (hotel side-track: SARIMA forecast and half-hourly multiplier)**
Each of two provincial monthly hotel-occupancy-rate series is fit with a SARIMA(1,1,1)(1,1,1,12) model,
with an explicit COVID-19 indicator covering March 2020 through June 2022, then converted to a
half-hourly multiplier by `m(t, month, PR) = s(t) * r(month, PR)`, where `r` is the forecast monthly
occupancy rate and `s(t)` is a unit-normalized 48-slot guest-room diurnal shape (overnight plateau at
1.00 from 22:00 to 06:00, weekday day trough 0.200, weekend day trough 0.308). Needed:
(a) the standard SARIMA source (Box, Jenkins and Reinsel, or the original Box-Jenkins methodology;
    verify edition);
(b) a published source for adding an explicit pandemic/structural-break indicator variable to a SARIMA
    model of hotel or tourism occupancy (2020-2022 specifically);
(c) any published precedent for decomposing a monthly occupancy-rate forecast into a sub-monthly
    (hourly or half-hourly) profile by multiplying it against a fixed within-day shape, in hotel,
    hospitality or building-energy demand modelling.

**Eq. 6 (per-channel EUI on two floor-area bases)**
Energy use intensity is reported on a conditioned-floor-area (CFA) basis (the zones assigned to that
use) and separately on a gross-floor-area, occupiable-share (GFA-share) basis (whole-building GFA times
the parsed occupiable-area fraction for that channel), and the two are never averaged. Needed: the
standard source(s) that define conditioned floor area versus gross floor area as EUI denominators in
building energy benchmarking (for example ASHRAE, ENERGY STAR Portfolio Manager technical reference, or
CBECS/NRCan survey methodology), and whether any of them explicitly warns against averaging EUI figures
computed on different area bases.

**Eq. 7 (REPLACE versus MODULATE injection)**
Apartment (residential) tags REPLACE the code-default occupancy schedule outright with the modelled
one; office, retail and guest-room tags MODULATE the NECB code-density schedule by multiplying it with
the modelled temporal fraction, so the code-of-record peak density is preserved while the temporal
signal is injected. Needed: any published precedent for this specific REPLACE-versus-MODULATE
distinction, that is, fully substituting a code-default schedule for some space types while only
rescaling it by a temporal factor for others in the same building energy model. Check first whether
Buttitta and Finn (2020) or Widen and Wackelgard (2010), already cited in this paper, use a replace-only
or a modulate-style injection; if neither does, say OWN, NO SOURCE NEEDED, and name the closest
published injection-methodology paper you found even if it does not draw this exact distinction.

**Eq. 8 (whole-building coincidence factor)**
"The ratio of the simultaneous building peak to the sum of the four channels' own individual peaks."
Needed: the standard source that defines coincidence factor (equivalently, the inverse of diversity
factor) in building or power-systems load analysis (for example the ASHRAE Handbook of Fundamentals,
load-diversity chapter, or a power-systems textbook such as Grainger and Stevenson). Give the exact
definition as stated in the source and say whether it matches "peak of the sum divided by sum of the
peaks" exactly or is stated as its reciprocal (diversity factor, sum of peaks divided by peak of sum).

**Eq. 9 (weekday day/night demand ratio)**
Reported per channel as median weekday midday demand divided by median weekday night demand (for
example Retail near 34 to 1, Hotel's ratio inverting to below 1). Needed: any standard or widely used
source in building-energy or power-systems load-shape analysis that defines a day/night or peak/off-peak
demand ratio as a load-shape metric distinct from load factor (2J's `dr_2J-17` already sourced load
factor to Grainger and Stevenson (1994) and Wood et al. (2013); say whether either book, or a different
source, also defines a day/night ratio specifically). If none exists, say OWN, NO SOURCE NEEDED.

---

## Named leads

Crossref REST API; arXiv for PCGrad, SLAW and uncertainty-weighting papers (NeurIPS/CVPR/ICML
proceedings); ASHRAE Handbook of Fundamentals (load diversity, coincidence factor chapter); ASHRAE
Guideline 14; ENERGY STAR Portfolio Manager Technical Reference; Statistics Canada and Eurostat
time-use-survey methodological guides (HETUS Guidelines, MTUS documentation); IBPSA Building Simulation
proceedings for occupancy-injection methodology papers; Box, Jenkins and Reinsel, *Time Series Analysis:
Forecasting and Control*; power-systems textbooks (Grainger and Stevenson; Wood et al.).

---

## Deliverable

1. Summary table, one row per equation (Part A's two, and Part B's Eq. 1 to Eq. 9), with columns:
   `equation | class (STANDARD/ADAPTED/OWN) | recommended citation | DOI or ISBN | Crossref checked
   (yes/no) | where in the source | what differs if ADAPTED`.
2. Full reference list of every recommended source, in Elsevier author-year style, each marked
   Tier 1/2/3 and whether you read the full text, the abstract only, or could not open it.
3. For Eq. 2: state plainly whether PCGrad, SLAW and uncertainty weighting are three genuinely distinct
   published methods, or whether any two of the names refer to the same underlying technique.
4. What you could not find, in the first person, one line each.
5. Section G (per the response template): flag any DOI that resolves to the wrong paper.

Rules restated, because every previous round in this project needed them:

- Open every source before citing it; verify every DOI via Crossref and report that you did.
- Give URL or DOI for every item. Items without a working link are discarded.
- Do not change the equations and do not suggest new methods.
- `NOT FOUND` beats an invented or approximate reference. Expect that some equations are the authors'
  own; fabricated citations are expected in Gemini's returned reports and will be checked, one by one,
  before anything is quoted in the manuscript.
- No em dashes and no en dashes anywhere in the returned text.

Save the return as `RV11_3J_equation_sources.md` in this same folder.
