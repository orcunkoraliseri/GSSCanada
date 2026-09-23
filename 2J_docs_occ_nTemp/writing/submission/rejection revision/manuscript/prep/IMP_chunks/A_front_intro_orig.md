# Abstract

Static, deterministic occupancy schedules in residential building energy simulation miss the timing of
demand, not only its annual total, and occupant behaviour became non-stationary through the COVID-19
pandemic, so the future load shape needs an explicit, stated persistence assumption rather than a single
prediction. This study builds a household-level, survey-based occupancy model for the Canadian housing
stock, checked on a held-out survey year, and carries it into paired, stock-scale building energy
simulation across several dwelling archetypes and climate zones, comparing 2022 against four stated 2030
scenarios: main persistence, partial persistence, full reversion, and a standardized-reversion check.
The household-level model is also compared against a simpler average-profile method on the same
households, and the simulated load shape is checked, not validated, against a year of measured Toronto
and Ontario electricity data. In 2022 the weekday at-home rate sits 4.73 percentage points
above its 2005-to-2015 trend. Under the main 2030 scenario, annual electricity is nearly
flat, rising 0.12 percent, while midday share rises 0.73 and load factor rises 0.49 percentage points,
both real changes. The scenario spread is real: full reversion falls 0.12 percent and the
standardized-reversion check falls 0.44 percent, while partial persistence is not distinguishable from
zero. The average-profile method shifts the annual total by about 9 percent in one cell but collapses
household-to-household peak-timing diversity almost to zero, diversity only the household-level model preserves. For
grid planning, this shift is mainly a timing question, not a sizing one: annual demand changes little,
but when it is delivered does.

# Highlights

- Annual electricity nearly flat (0.12 percent) as midday share and load factor rise.
- Reversion scenarios fall 0.12 to 0.44 percent; partial persistence is not detectable.
- 2022 weekday at-home rate sits 4.73 percentage points above the 2005-to-2015 trend.
- Household model keeps peak-timing diversity an average-profile method erases.
- Load shape checked, not validated, against measured Toronto/Ontario 2022 data.

# Keywords

Residential occupancy modelling; time-use survey data; stock-scale building energy simulation;
work-from-home scenarios; residential load shape; peak demand and load factor; Canadian housing stock.

# 1. Introduction

## 1.1 The performance gap and static occupancy schedules

The persistent gap between predicted and measured building energy use, the performance gap, remains a
central credibility problem for building performance simulation (de Wilde 2014); occupant behaviour is
now the largest identified unexplained driver (Yan et al. 2015; Hong et al. 2017), taken up directly by
IEA EBC Annex 66 and its successor Annex 79 (Yan et al. 2017; O'Brien et al. 2020). Routine practice
still relies on static, deterministic occupancy schedules drawn from reference standards, a poor fit
for residential buildings, where daily life follows individual routines rather than regulated
operation (Mahdavi et al. 2021). Fixed schedules miss day-to-day behavioural variability (Wilke, Haldi
and Robinson 2011; Elsayed et al. 2023): survey-derived occupancy profiles differ from standard
schedules by up to 41 percent at individual hours, a timing discrepancy, not an annual-energy one
(Mitra et al. 2020). Static schedules therefore carry a timing error an annual-total comparison cannot
reveal.

Timing matters because a home's daily load shape, not only its yearly sum, sets its contribution to
grid peak demand, the evening ramp, and demand-response suitability (Denholm et al. 2015). This study uses
2030 as its scenario horizon because it sits beyond the latest available survey data, requiring an
explicit assumption about how far the pandemic-era change has settled or receded, and because 2030 is
a commonly used planning horizon (IEA 2021); the Canadian time-use survey runs roughly every five
years, and no cycle after 2022 has been announced (Statistics Canada 2024a).

## 1.2 Two research tracks and the gap they leave open

Two research traditions address occupancy in building energy modelling and rarely meet. The first
builds high-fidelity stochastic occupant models, applied mostly to single buildings and already-elapsed
periods (Richardson, Thomson and Infield 2008; Widén and Wäckelgård 2010; Wilke et al. 2013; Aerts et
al. 2014), including a growing Canadian strand (Armstrong et al. 2009; Osman and Ouf 2021; Osman et
al. 2023; Ferreira et al. 2024). The second runs stock- and urban-scale energy engines across
thousands of dwellings but feeds them simplified, single-period schedules (Reinhart and Cerezo Davila
2016); Chen et al. (2022)'s paired stock-scale design is the closest precedent to this study.

Table 1 scores nine external studies and the authors' own prior work against six framework dimensions
(C1 to C6), present, absent or partial, by the written criterion given below the table, not an
unstated judgement call.

**Table 1.** Framework dimensions: external competitors, the authors' own prior work, and this study.

| Study | C1 Time-series occupancy | C2 Calibrated model | C3 Future-year scenario (pandemic break) | C4 Activity/end-use resolved | C5 Stock-scale | C6 Load-shape/peak |
|------------------------------------|:-----------:|:------------:|:-----------:|:---------:|:--------:|:--------:|
| Chiou et al. (2011) | check | cross | cross | check | cross | check |
| Widén and Wäckelgård (2010) | check | check | cross | check | cross | check |
| Reinhart and Cerezo Davila (2016) | cross | cross | cross | cross | check | cross |
| Fischer et al. (2020) | check | check | cross | check | cross | check |
| Motuzienė et al. (2022) | check | check | cross (footnote c) | cross | cross | cross |
| Chen et al. (2022, ResStock) | check | check | cross | check | check | check |
| Osman et al. (2023, Canada) | check | check | cross | check | cross | check |
| Yin et al. (2024) | check | check | cross | cross | cross | cross |
| Jalilian and Kamel (2025) | cross | cross | check | cross | check | cross |
| Authors' own prior line: companion journal manuscript, under review, and companion conference study (Iseri and Hachem-Vermette 2026) | check | check | cross | cross | P | P |
| **This study** | **check** | **check** | **check** | **check** | **check** | **check** |

Column criteria (one footnote per column):

a. **C1.** Present when occupancy varies within the day, not only as one daily or annual value.
b. **C2.** Present when parameters are fitted or checked against measured or surveyed data. Chiou et
   al. (2011) derives loads directly from diaries with no fitted model (absent); Yin et al. (2024) fits
   trend statistics to four decades of survey cycles (present, despite no simulation).
c. **C3.** Present only when the study projects to a stated year beyond its own data window. Motuzienė
   et al. (2022) predicts short-horizon pandemic occupancy, not a future year, so C3 is absent here.
d. **C4.** Present when the model distinguishes specific activities, or the equipment and lighting
   loads they imply, not one presence indicator or total.
e. **C5.** Present when the study aggregates across many dwellings, not one or a few.
f. **C6.** Present when the study reports the sub-daily load curve or its peak, not only totals.

Chen et al. (2022) is the strongest external precedent, sharing five of six dimensions; the one it
lacks is C3, since it evaluates an already-elapsed period rather than carrying occupancy through the
pandemic break to a future year. That is the one axis of difference; no wider novelty claim is made.

The authors' own prior line scores present on C1 and C2, since it uses time-series, calibrated
occupancy. It scores partial on stock-scale and load-shape focus (fewer typologies, only a first look
at peak timing) and absent on C3 and C4 (a same-period synthetic year, presence-filtered end uses).
The delta from that line is the pipeline-stage advances in Section 1.5, not one more column.

## 1.3 Occupant behaviour is non-stationary

The assumption that occupant behaviour is stationary did not hold through the COVID-19 pandemic. Work
from home rose sharply, to roughly four times its pre-pandemic level: about 20 percent of full
workdays afterward, against 5 percent before (Barrero, Bloom and Davis 2021). Weekday electricity
profiles show a change associated with the pandemic and the shift to more work from home, the loss of
bimodal commuting peaks and a weekend-like weekday shape (Abdeen et al. 2021), with a weather-adjusted
increase of about 7.9 percent in electricity use associated with the pandemic period (Cicala 2023).
Occupancy-prediction models trained only on pre-pandemic data degrade sharply once this period is
crossed (Motuzienė et al. 2022), the problem a pre-pandemic-anchored projection would inherit.

What happens to work from home after 2022 is not settled by the material available here. This study
does not assume the pandemic-era at-home level holds unchanged to 2030; instead, the share of that
shift retained in 2030 is treated as an explicit, stated assumption tested across more than one value,
not a single predicted number (Barrero, Bloom and Davis 2023; Statistics Canada 2024b). A pre-pandemic-anchored projection would instead carry the structural break as a
systematic bias, misjudging not only how much energy is used but when.

## 1.4 Departure from the authors' prior line

The present study departs from a specific prior line by the authors: a conditional variational
autoencoder, a generative model referred to here as a C-VAE, paired with a cluster-based scheme, used
to synthesize longitudinally consistent Canadian residential occupancy schedules from successive
General Social Survey cycles and carry them into building energy simulation. That line spans a journal
treatment across several Montreal neighbourhood-unit typologies (companion manuscript, under review), a
companion conference study across three climate-zone cities (Iseri and Hachem-Vermette 2026), and a
related population-statistics and machine-learning occupancy framework (Iseri, Dino and Kalkan 2026).

That line established what this paper does not re-claim: that survey-grounded, time-series occupancy
can be built for Canadian building energy models and moves predicted heating and cooling demand
relative to default assumptions, with a first look at diurnal and peak timing. The predecessor asked
how much, comparing period-specific occupancy datasets against one default schedule in one climate
zone, ending at a same-period synthetic year. This paper asks when: cycle-versus-cycle and
within-household rather than default-versus-cycle; occupancy carried through the pandemic break to a
stated future year, 2030; scope widened to several Canadian dwelling archetypes across multiple
climate zones; end uses anchored to a national household-energy survey rather than filtered from
default profiles; and the primary result is the diurnal load shape, not annual totals.

## 1.5 Aim and contributions of the present study

This paper asks whether, and how, occupancy-driven change reshapes the residential load curve at
stock scale, under explicit work-from-home scenarios carried to 2030.

The paper makes three scientific contributions: a generative occupancy model chosen from a broader
architecture search against distributional checks the prior C-VAE line did not apply, preserving
sharper within-day activity timing (over 40 architectures searched); occupancy carried
through the pandemic break to 2030 under explicit scenarios, with the generator checked on a held-out
year (trained through 2015, tested on the unseen 2022 cycle) rather than on a same-period synthetic year; and attribution
from a paired, within-household stock-scale design holding the same households fixed across each
compared year pair, across multiple Canadian archetypes and climate zones (50 households per panel, 5,997 simulation runs).

It also makes two practical contributions: activity-resolved equipment and lighting loads checked
against a national end-use energy survey by dwelling type, a fitted-target check rather than an
independent validation of the sub-daily shape (all 48 archetype-by-city-by-year cells fall within plus or minus 15 percent of the fitted target); and diurnal load-shape metrics, load factor, midday energy share, and daily peak timing,
reported directly for grid ramping and demand-response planning rather than only annual totals.

None of these advances is specific to Canada: the pipeline needs a repeated national time-use survey,
a census-type household frame linking diaries to a dwelling stock, and a national end-use benchmark, a
trio supplied elsewhere by the American Time Use Survey (Chiou et al. 2011) and the Harmonised
European Time Use Survey (Eurostat 2018), whose guidelines the activity vocabulary here already
follows. What is country-specific is the calibration data and its magnitudes; the generator, the
held-out-year evaluation, and the paired design carry over unchanged.

The framework operationalizing this aim is in Section 2 (Sections 2.1 to 2.12); its limitations,
including scope, the scenario treatment of 2030, and the 2022 survey's collection-mode confound with
the pandemic-era shift, are stated in full in Section 5.

