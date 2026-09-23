# Abstract

Static, deterministic occupancy schedules in residential building energy simulation miss the timing of
demand, not only its annual total. Occupant behaviour became non-stationary through the COVID-19
pandemic. Future load shapes need an explicit, stated persistence assumption, not a single
prediction. This study builds a household-level, survey-based occupancy model for the Canadian housing
stock. Checked on a held-out survey year, the model drives paired, stock-scale building energy
simulation across several dwelling archetypes and climate zones. The study compares 2022 against four
stated 2030 scenarios. Three set how much of the pandemic shift persists: main persistence, partial
persistence and full reversion. The fourth is a standardized-reversion check. The model is also
compared with a simpler average-profile method on the same households. The simulated load shape is
checked, not validated, against a year of measured Toronto and Ontario electricity data. In 2022, the
weekday at-home rate sits 4.73 percentage points above its 2005-to-2015 trend. Under the main 2030
scenario, annual electricity is nearly flat, rising 0.12 percent. Midday share rises 0.73 and load
factor 0.49 percentage points. Both changes and the scenario spread are real. Full reversion falls 0.12
percent; the standardized-reversion check falls 0.44 percent. Partial persistence is indistinguishable
from zero. The average-profile method shifts one cell's annual total by about 9 percent. Yet it
collapses household-to-household peak-timing diversity almost to zero; only the household-level model
preserves it. For grid planning, this shift is mainly a timing question, not a sizing one. Annual
demand changes little, but when it is delivered does.

# Highlights

- Survey-based household occupancy model runs from 2005 to 2030 across Canadian homes.
- For grid planning, work from home is mainly a timing question, not a sizing one.
- Annual electricity rises only 0.12 percent, but midday share and load factor rise.
- Three 2030 scenarios and a reversion check test how much of the pandemic shift lasts.
- Our household model keeps the peak-timing spread that average schedules erase.

# Keywords

Residential occupancy modelling; time-use survey data; stock-scale building energy simulation;
work-from-home scenarios; residential load shape; peak demand and load factor; Canadian housing stock.

# 1. Introduction

## 1.1 The performance gap and static occupancy schedules

The performance gap is the persistent gap between predicted and measured building energy use. It
remains a central credibility problem for building performance simulation (de Wilde 2014). Occupant
behaviour is now the largest identified unexplained driver of this gap (Yan et al. 2015; Hong et al.
2017). IEA EBC Annex 66 and its successor Annex 79 took up this problem directly (Yan et al. 2017;
O'Brien et al. 2020). Routine practice still relies on static, deterministic occupancy schedules drawn
from reference standards. These schedules fit residential buildings poorly. In homes, daily life follows
individual routines rather than regulated operation (Mahdavi et al. 2021). Fixed schedules miss
day-to-day behavioural variability (Wilke, Haldi and Robinson 2011; Elsayed et al. 2023).
Survey-derived occupancy profiles differ from standard schedules by up to 41 percent at individual
hours. This is a timing discrepancy, not an annual-energy one (Mitra et al. 2020). Static schedules
therefore carry a timing error that an annual-total comparison cannot reveal.

Timing matters because a home's daily load shape counts, not only its yearly sum. The load shape sets
the home's contribution to grid peak demand, the evening ramp and demand-response suitability (Denholm
et al. 2015). This study uses 2030 as its scenario horizon for two reasons. First, 2030 sits beyond the
latest available survey data. It therefore requires an explicit assumption about how far the
pandemic-era change has settled or receded. Second, 2030 is a commonly used planning horizon (IEA
2021). The Canadian time-use survey runs roughly every five years, and no cycle after 2022 has been
announced (Statistics Canada 2024a).

## 1.2 Two research tracks and the gap they leave open

Two research traditions address occupancy in building energy modelling, and they rarely meet. The first
builds high-fidelity stochastic occupant models. These models are applied mostly to single buildings
and already-elapsed periods (Richardson, Thomson and Infield 2008; Widén and Wäckelgård 2010; Wilke et
al. 2013; Aerts et al. 2014). This track includes a growing Canadian strand (Armstrong et al. 2009;
Osman and Ouf 2021; Osman et al. 2023; Ferreira et al. 2024). The authors' own prior work also belongs
to this track. It used a conditional variational autoencoder, a generative model referred to here as a
C-VAE, paired with a cluster-based scheme. This prior C-VAE line synthesized longitudinally consistent
Canadian residential occupancy schedules from successive General Social Survey cycles. It then carried
these schedules into building energy simulation. The line spans a journal treatment across several
Montreal neighbourhood-unit typologies (companion manuscript, under review). It also includes a
companion conference study across three climate-zone cities (Iseri and Hachem-Vermette 2026). A related
population-statistics and machine-learning occupancy framework completes it (Iseri, Dino and Kalkan
2026).

The second track runs stock-scale and urban-scale energy engines across thousands of dwellings.
However, it feeds them simplified, single-period schedules (Reinhart and Cerezo Davila 2016). Chen et
al. (2022)'s paired stock-scale design is the closest precedent to this study.

Table A1 in Appendix A scores nine external studies and the authors' own prior work against six
framework dimensions (C1 to C6). Each dimension is scored present, absent or partial. The score follows
a written criterion, not an unstated judgement call.

Chen et al. (2022) is the strongest external precedent and shares five of the six dimensions. It lacks
only C3. It evaluates an already-elapsed period rather than carrying occupancy through the pandemic
break to a future year. That is the one axis of difference, and no wider novelty claim is made.

The authors' own prior line scores present on C1 and C2, since it uses time-series, calibrated
occupancy. It scores partial on stock-scale and load-shape focus, with fewer typologies and only a
first look at peak timing. It scores absent on C3 and C4, with a same-period synthetic year and
presence-filtered end uses. The advance over that line lies in the pipeline stages set out in Section
1.4, not in one more column.

## 1.3 Occupant behaviour is non-stationary

The assumption that occupant behaviour is stationary did not hold through the COVID-19 pandemic. Work
from home rose sharply, to roughly four times its pre-pandemic level. It reached about 20 percent of
full workdays afterward, against 5 percent before (Barrero, Bloom and Davis 2021). Weekday electricity
profiles show a change associated with the pandemic and the shift to more work from home. They lose
their bimodal commuting peaks and take on a weekend-like weekday shape (Abdeen et al. 2021). A
weather-adjusted increase of about 7.9 percent in electricity use is associated with the pandemic
period (Cicala 2023). Occupancy-prediction models trained only on pre-pandemic data degrade sharply once
this period is crossed (Motuzienė et al. 2022). A projection anchored before the pandemic would inherit
this problem.

The evidence available to this study does not settle what happens to work from home after 2022. The
study therefore does not assume that the pandemic-era at-home level holds unchanged to 2030. Instead,
it treats the share of that shift retained in 2030 as an explicit, stated assumption. This share is
tested across more than one value, not given as a single predicted number (Barrero, Bloom and Davis
2023; Statistics Canada 2024b). A projection anchored before the pandemic would instead carry the
structural break as a systematic bias. It would misjudge not only how much energy is used, but also
when.

## 1.4 Aim and contributions of the present study

This paper asks whether, and how, occupancy-driven change reshapes the residential load curve at stock
scale, under explicit work-from-home scenarios carried to 2030. The prior C-VAE line showed that
survey-grounded, time-series occupancy can be built for Canadian building energy models. It also showed
that this occupancy moves predicted heating and cooling demand relative to default assumptions, with a
first look at diurnal and peak timing. This paper does not re-claim those results. The prior line asked
how much: it compared period-specific occupancy datasets against one default schedule in one climate
zone. This paper asks when: it compares survey cycles against each other within the same households,
rather than default against cycle. Its primary result is the diurnal load shape, not annual totals. The paper makes three scientific contributions. First, it uses a
generative occupancy model chosen from a broader architecture search (over 40 architectures searched).
The search applied distributional checks that the prior C-VAE line did not apply, and the chosen model
preserves sharper within-day activity timing. Second, it carries occupancy through the pandemic break
to 2030 under explicit scenarios. The generator is checked on a held-out year (trained through 2015,
tested on the unseen 2022 cycle) rather than on a same-period synthetic year. Third, it attributes
change with a paired, within-household, stock-scale design. This design holds the same households fixed
across each compared year pair, across multiple Canadian archetypes and climate zones (50 households
per panel, 5,997 simulation runs).

The paper also makes two practical contributions. First, equipment and lighting loads are resolved by
activity and checked against a national end-use energy survey by dwelling type. This is a
fitted-target check rather than an independent validation of the sub-daily shape. All 48
archetype-by-city-by-year cells fall within plus or minus 15 percent of the fitted target. Second, the
paper reports diurnal load-shape metrics directly for grid ramping and demand-response planning, rather
than only annual totals. These metrics are load factor, midday energy share and daily peak timing.

None of these advances is specific to Canada. The pipeline needs three inputs: a repeated national
time-use survey, a census-type household frame linking diaries to a dwelling stock, and a national
end-use benchmark. Elsewhere, the American Time Use Survey (Chiou et al. 2011) and the Harmonised
European Time Use Survey (Eurostat 2018) supply this trio. The activity vocabulary used here already
follows the Harmonised European Time Use Survey guidelines. What is country-specific is the calibration
data and its magnitudes. The generator, the held-out-year evaluation and the paired design carry over
unchanged.

Section 2 (Sections 2.1 to 2.6) sets out the framework that puts this aim into practice. Section 5
states its limitations in full. These include scope, the scenario treatment of 2030, and the 2022
survey's collection-mode confound with the pandemic-era shift.
