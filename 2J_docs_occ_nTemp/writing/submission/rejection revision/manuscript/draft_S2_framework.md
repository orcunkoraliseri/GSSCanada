# 2. Proposed modelling and simulation framework

[Figure 1: workflow, image prompt to be written in WP11]

The framework turns household time-use diaries into building-energy occupancy schedules through a
chain of eleven stages: diary harmonisation, a generative day-type model, marginal raking to match
independent targets, matching of diary donors to a census-representative population, household
aggregation into hourly schedules, activity-driven end-use loads, a scenario-based projection to a
future year, sampling of households for simulation, aggregation of simulation output to the national
housing stock, load-shape metrics, and a paired statistical comparison across years and across
alternative scheduling methods. Each stage is defined below from the code that produced the results,
with a trace to the exact file and line read for every equation (trace table at the end of this
draft; it is removed before submission).

## Table 1. Datasets and their role in the framework

| Dataset | Years / vintage | What it provides | Framework stage(s) |
|---|---|---|---|
| GSS time-use diaries | 2005, 2010, 2015, 2022 cycles | Respondent-level 10-minute activity and location diaries, harmonised to a common activity code list | Source diaries for the generative model (2.1, 2.2) and for the raking targets (2.3) |
| Census public-use microdata | 2021 | Household composition, dwelling type, tenure and geography for a representative population of households | Recipient population for diary matching (2.4) and the base population whose schedules are aggregated (2.5) |
| NRCan SHEU end-use reference | 2019 survey | National annual end-use energy totals by dwelling type (appliances, lighting) | Calibration target for the activity-driven end-use loads (2.6) |
| Weather files | typical-meteorological-year (TMYx) | Hourly outdoor conditions for each climate zone | Building simulation input alongside the injected schedules (2.5, 2.8) |
| Building archetype models | fixed archetype geometry and construction | Four dwelling archetypes at six city/climate-zone weather stations, the physical envelope each household's schedule is run against | Building simulation and stock aggregation (2.8, 2.9) |
| IESO measured hourly data | recent Ontario system data | Province-level measured hourly electricity data, used as an external reference series, not as a model input | External reference for the simulated load shape (referenced in 2.10 to 2.12; no simulation input role) |

## 2.1 Diary harmonisation to 30-minute slots

Each respondent's diary is first represented at 10-minute resolution as 144 activity codes
(`slot_001` to `slot_144`) and 144 binary at-home indicators (`home_001` to `home_144`), covering one full
day from a 04:00 origin. These are downsampled to 48 slots of 30 minutes for the generative model
and for every later stage. For slot $s \in \{1, \dots, 48\}$, the activity code is the majority vote
(mode) of the three underlying 10-minute codes, with the rare three-way ties resolved in a separate
step:

$$
\text{act30}_s = \operatorname{mode}\big(\text{slot}_{3s-2},\ \text{slot}_{3s-1},\ \text{slot}_{3s}\big)
\tag{1}
$$

and the at-home indicator is set to 1 when at least two of the three underlying slots are at home:

$$
\text{hom30}_s = \mathbb{1}\!\left[\ \sum_{k=1}^{3} \text{home}_{3(s-1)+k} \ \ge\ 2\ \right]
\tag{2}
$$

The resulting 48-slot series (`act30_001` to `act30_048`, `hom30_001` to `hom30_048`) is the unit
that every later stage of the framework consumes: the generative model's training target, the raking
target, the census-matched donor, and the household-schedule input to the building simulation are all
expressed in this same 48-slot, 04:00-origin form.

## 2.2 Generative day-type model

The model is a sequence model with an encoder-decoder structure: an encoder builds a single
conditioning representation from the respondent's demographic profile (age group, sex, marital
status, household size, labour-force status), the survey cycle, and the target day-type stratum
(weekday, Saturday, Sunday), and a decoder produces the 48-slot day conditioned on that
representation through cross-attention. At each slot $t$ the decoder outputs three sets of logits:
a 14-way activity categorical, a binary at-home indicator, and a 9-channel co-presence indicator
(who else is present). Training maximises a weighted combination of the per-slot negative
log-likelihoods of these three (conditionally independent, given the decoder state) distributions,
plus two regularisation terms:

$$
\mathcal{L} \;=\; \sum_{t=1}^{48}\Big[
\lambda_{\text{act}}\, \ell^{\text{act}}_t
\;+\; \lambda_{\text{home}}\, \ell^{\text{home}}_t
\;+\; \lambda_{\text{cop}}\, \ell^{\text{cop}}_t
\Big]
\;+\; \lambda_{\text{marg}}\, \ell_{\text{marg}}
\;+\; \lambda_{\text{aux}}\, \ell_{\text{aux}}
\tag{3}
$$

where $\ell^{\text{act}}_t$ is the categorical cross-entropy of the activity head against the
observed activity at slot $t$; $\ell^{\text{home}}_t$ is the binary cross-entropy of the at-home
head; $\ell^{\text{cop}}_t$ is the binary cross-entropy of the 9 co-presence channels, masked by
the availability of each co-presence channel for that respondent and, for the colleagues channel,
zeroed for cycles that do not carry a colleagues category; $\ell_{\text{marg}}$ is a
direction-agnostic penalty on the gap between the model's average at-home rate and the observed
average at-home rate; and $\ell_{\text{aux}}$ is a small auxiliary classification loss that predicts
the target day-type stratum from the decoder state. The $\lambda$ weights are fixed training
parameters, not fitted. Two further terms exist in the code (a logic-consistency penalty between the
at-home and co-presence heads, and a transition-rate penalty) but their default weight is zero, so
they do not enter the trained model discussed in this paper; they are noted here only because the
code defines them.

## 2.3 Marginal raking of at-home slots

Raking is applied after census-to-diary matching (section 2.4), to the matched population. Two rakes
adjust the at-home marginal, one per day-type stratum $s$ and 30-minute slot $t$: for the survey year,
the model-generated diary-days are raked to the at-home rate of the real respondents; for 2030, the
matched population is raked to the scenario target of section 2.7. Both use the same mechanism, which is a
single deterministic pass, not an iterative multiplicative procedure. For a target at-home rate
$p_{s,t} \in [0,1]$ and a group of $N_s$ diaries sharing stratum $s$, the integer target count is

$$
n^{\text{tgt}}_{s,t} = \operatorname{clip}\big(\operatorname{round}(p_{s,t}\, N_s),\ 0,\ N_s\big)
\tag{4}
$$

and the number of records to flip at slot $t$ is the shortfall against the current count of ones,
$n^{\text{cur}}_{s,t}$:

$$
\Delta_{s,t} = n^{\text{tgt}}_{s,t} - n^{\text{cur}}_{s,t}
\tag{5}
$$

If $\Delta_{s,t} > 0$, that many zero-valued records are flipped to one; if $\Delta_{s,t} < 0$, that
many one-valued records are flipped to zero. Candidates are chosen with priority given to records at
an activity-transition boundary (where the neighbouring slot's value differs from slot $t$), with
remaining ties broken by a fixed random seed. Because the target count is met exactly by
construction (up to the number of available candidate records), there is no convergence tolerance or
iteration count: one pass over every (stratum, slot) pair reproduces the target count exactly, or as
closely as the available candidates allow. The procedure is therefore a minimal-flip integer rake to
an exact per-slot count, not an iterative multiplicative proportional fitting. For the survey year, a
floor guard follows: a single-person household whose daily at-home mean the rake pushed below a fixed
floor has night slots restored to at home until the floor is met.

## 2.4 Census-to-diary matching

Each synthetic (census) household member is assigned a donor diary by a four-level fallback search,
attempted in order until a non-empty donor group is found for that Census record:

1. an exact match on age group, sex, marital status, household size, labour-force status and
   province, within the same day-type stratum;
2. a match on age group, sex, labour-force status and province only, within the same day-type
   stratum;
3. a match on age group and sex only, within the same day-type stratum;
4. a random draw from every diary of the same day-type stratum, regardless of demographics, used
   only when no donor shares even age group and sex.

Within whichever level supplies the donor group, one donor is drawn uniformly at random. The
day-type stratum itself is assigned to each Census record first (the census record carries no diary
day), with a fixed 5:1:1 weekday-to-Saturday-to-Sunday probability split. All random draws use a
fixed seed. Survey cycle is not a matching key: the donor pool for a given year is built from that
year's own diaries only (2022 diaries for the 2022 stock; each earlier cycle from its own diaries).
Metropolitan area is not a key either; it is nested within province and was dropped from the first
level so that more people keep household size as a matched attribute. As a consequence, a donor
shares the recipient's metropolitan area less often, which is stated as a limitation.

## 2.5 Household aggregation and conversion to schedules

Once every household member has a 48-slot activity and at-home series (from the harmonised diary,
the generative model, or the matched donor, depending on the year), the household-level schedule is
built by averaging across members. For household $h$, day type $d$ (weekday or weekend, with
Saturday and Sunday pooled into one weekend day type) and slot $t$, the fraction of the household at
home is the mean of the members' at-home indicators:

$$
\text{occ48}_{h,d,t} = \frac{1}{M_h}\sum_{m=1}^{M_h} \text{hom30}_{h,d,t}^{(m)}
\tag{6}
$$

where $M_h$ counts the member diary-days pooled into that day type (Saturday and Sunday records
both enter the weekend mean). The household metabolic rate is the mean, over the same records, of a
fixed activity-to-watts lookup applied to each activity code (a fixed default applies to codes
without an entry):

$$
\text{met48}_{h,d,t} = \frac{1}{M_h}\sum_{m=1}^{M_h} W_{\text{met}}\!\big(\text{act30}_{h,d,t}^{(m)}\big)
\tag{7}
$$

Both 48-slot series are then averaged pairwise into 24 hourly values,
$\text{occ24}_{h,d,k} = \tfrac{1}{2}(\text{occ48}_{h,d,2k-1} + \text{occ48}_{h,d,2k})$ for hour
$k = 1,\dots,24$ (and likewise for the metabolic series), and the result is rolled by four hours so
that clock hour 0 (midnight) lines up with the weather file's clock; the diary's own origin is 04:00,
not midnight. The equipment and lighting fractions from section 2.6 are attached to the same
household/day-type/hour rows after the same four-hour roll. The output is one row per household, day
type and hour, in the column format the building-simulation stage's schedule-injection function
consumes; each household contributes exactly one weekday row set and one weekend row set to the
schedule file used for that year's simulation.

## 2.6 Activity-driven end-use loads and the calibration scalar $f_e$

End-use equipment power and lighting state are built slot by slot from the same household diary,
before the 48-to-24 averaging of section 2.5. At slot $t$, with $n_t$ household members present
(at home) and their activities $a_1, \dots, a_{n_t}$, the raw equipment power is a baseload plus a
sum over device categories:

$$
P_t = P_{\text{base}} + \sum_{b \in B_{\text{shared}}} \Big(\max_{i=1,\dots,n_t} w_b(a_i)\Big) P_b\, \eta(n_t)
\;+\; \sum_{b \in B_{\text{personal}}} \Big(\sum_{i=1,\dots,n_t} w_b(a_i)\Big) P_b
\;+\; P_{\text{dw}}(t)\, \eta(n_t)
\tag{8}
$$

where $B_{\text{shared}}$ is the set of appliance categories one household uses at a time (cooking,
washer, dryer, television), $B_{\text{personal}}$ is the set used per person (a personal computer),
$w_b(a)$ is a fixed weight giving how strongly activity $a$ implies use of category $b$, $P_b$ is a
fixed rated power for category $b$, $\eta(n_t)$ is a fixed, non-decreasing diminishing-returns factor
for shared-device co-occupancy ($\eta(0)=0$, $\eta(1)=1$, saturating at a fixed cap for five or more
present members), and $P_{\text{dw}}(t)$ is a separate dishwasher term that, once triggered by a
present member's activity, runs for a fixed number of slots and then enforces a fixed cooldown before
it can trigger again. The lighting indicator is binary: $\text{light}_t = 1$ if any present member's
activity has a non-zero lighting weight, else 0.

The 48-slot raw series is averaged into 24 hourly values exactly as in section 2.5, then scaled to an
external annual-energy target by dwelling type from the NRCan SHEU reference (the equipment target is
net of the refrigerator load already represented separately in the building model, to avoid
double-counting). Writing $E_{\text{raw}}$ for the raw annual equipment energy implied by the 24-hour
weekday/weekend profile and a fixed weekday/weekend day count, and $E_{\text{tgt}}$ for the SHEU
target for that dwelling type, the calibration scalar is

$$
f_e = \frac{E_{\text{tgt}}}{E_{\text{raw}}}
\tag{9}
$$

applied to the peak raw hourly power to obtain the building-simulation design power, and to the raw
hourly series (divided by its own peak) to obtain a 0-1 equipment fraction schedule. Lighting is
scaled the same way, using total annual lit-hours in place of raw energy. This SHEU agreement is a
calibration of the design power and duty fraction to an external annual total: it is not a
validation of the sub-hourly shape, which is not compared against any external end-use time series.

## 2.7 2030 scenario construction

The 2030 stock keeps the same households and the same raking mechanism as section 2.3, changing only
the at-home target. A linear trend $\text{slope}_{s,t}$ is fit through the 2005, 2010 and 2015
cycle's stratum-slot at-home means, and the 2022 deviation from that trend line,
$\text{jump}_{s,t} = \text{obs}_{2022,s,t} - \text{trend}_{s,t}(2022)$, is treated as a pandemic-era
level shift that may or may not persist. Three scenarios differ only in the share $\lambda$ of that
shift assumed to remain in 2030:

$$
\text{target}_{\lambda}[s,t] = \operatorname{clip}\Big(
\text{stock}_{2022}[s,t] + 8 \cdot \text{slope}_{s,t} - (1-\lambda)\,\text{jump}_{s,t}
,\ 0,\ 1\Big),
\qquad \lambda \in \{1,\ 0.5,\ 0\}
\tag{10}
$$

so that $\lambda = 1$ keeps the full 2022 shift, $\lambda = 0.5$ assumes half of it has faded, and
$\lambda = 0$ assumes it has fully faded and 2030 sits on the pre-2022 trend line. A second,
standardised version of the same equation, $\text{target}_{\text{std}}$, uses a trend and a shift
computed after reweighting every cycle's diaries to the 2030 stock's age-group by sex by
labour-force-status composition, reported alongside the primary version as a sensitivity check. The
result is a target array in the same form as section 2.3, raked exactly as there. This is a
scenario-based projection of a stated persistence assumption, not a forecast: no scenario claims to
predict which value of $\lambda$ will occur.

## 2.8 Sampling procedure

For each of the 24 modelled cells (4 dwelling archetypes $\times$ 6 city/climate-zone stations),
the candidate pool is every household identifier present in the schedule files of all years
simulated together, restricted to that cell's archetype and province. From this pool, $N = 50$ households are drawn
without replacement:

$$
\text{sample} = \text{SRS}_{\text{without replacement}}(\text{pool}_{\text{cell}},\ N=50)
\tag{11}
$$

falling back to sampling with replacement only if the pool itself holds fewer than 50 households for
that cell (not encountered in the campaign reported in this paper). The random generator for each
cell is seeded by a fixed base seed together with a deterministic offset derived from a hash of the
cell's own label, so that the same base seed reproduces the same 50 households for a given cell on
any machine. The same 50 households are used for every cycle-year simulated for that cell (a paired
panel): only the injected occupancy, equipment and lighting schedule changes by year, while the
building archetype and weather file are held fixed.

## 2.9 Stock aggregation weights

To summarise the 24 simulated cells as one national figure, each cell's result is weighted by its
dwelling archetype's share of the national housing stock (an external reference composition, held
fixed across all years and not derived from this paper's own samples), renormalised over the four
modelled archetypes, and that archetype-level weight is split equally across the (up to six) cities
that host that archetype:

$$
w_{a,c} = \frac{w_a}{\lvert C_a \rvert}, \qquad \sum_{a} w_a = 1
\tag{12}
$$

where $C_a$ is the set of cities simulated for archetype $a$. A national metric is then the
weight-average of the 24 cells' values, $\bar{x} = \sum_{a,c} w_{a,c}\, x_{a,c}$; for the circular
peak-hour metric of section 2.10, the averaging is done on the sine and cosine components before
re-computing the mean angle, for the same reason circular quantities cannot be averaged directly
(the 23:00-to-00:00 wrap).

## 2.10 Load-shape metrics

All load-shape metrics are computed from the hourly whole-building electricity meter, after
conversion from the simulator's native energy units to kW. Annual energy is the sum of the 8,760
hourly kW values for the year. Daily peak is the mean, over the year's days, of that day's maximum
hourly kW. The peak hour of day is circular (0-23, wrapping at midnight), so its central tendency
uses the circular mean: with angle $\theta_i = 2\pi h_i / 24$ for each day's peak hour $h_i$,

$$
\bar{h} = \frac{24}{2\pi}\, \operatorname{atan2}\!\Big(\overline{\sin\theta},\ \overline{\cos\theta}\Big) \bmod 24
\tag{13}
$$

and its dispersion is Mardia's circular standard deviation, from the resultant length
$R = \sqrt{\overline{\sin\theta}^2 + \overline{\cos\theta}^2}$:

$$
\text{sd}_{\text{circ}} = \frac{24}{2\pi}\sqrt{-2\ln R}
\tag{14}
$$

Load factor is the ratio of the year's mean hourly load to its single annual peak hourly load,
$\text{LF} = \overline{P}/P_{\max}$. Midday share is the fraction of annual energy delivered in the
09:00-17:00 window, $\text{midday} = \sum_{h \in [9,17)} P_h \big/ \sum_h P_h$. Morning-leaning share
is the fraction of units (households or days, depending on the aggregation level) whose circular
mean peak hour falls in $[0,12)$. No ramp metric is defined anywhere in the plotting code read for
this section; none is reported here (NOT VERIFIED as present in the code, checked by search).

## 2.11 Paired difference and its confidence interval

Every year-to-year or arm-to-arm comparison in this paper uses the same paired-difference
construction. For a metric $M$ and two conditions (for example, simulation years) A and B, the
household-level results are joined on the household's identifying key (archetype, city, household
identifier), keeping only households present under both conditions, and the paired difference is

$$
d_i = M_i^{(B)} - M_i^{(A)}
\tag{15}
$$

for each of the $n$ paired households. The reported interval is the standard pooled paired
Student-t 95% confidence interval on the mean difference,

$$
\bar{d} \;\pm\; t_{0.975,\,n-1}\ \frac{s_d}{\sqrt{n}}
\tag{16}
$$

where $s_d$ is the sample standard deviation of $d_i$ across the $n$ paired households (pooled
across every simulated cell, not computed separately per cell), and a one-sample t-test of
$H_0: \bar{d}=0$ is reported alongside it. A difference is treated as separable from zero only when
this interval excludes zero. This interval treats households as independent and does not account for
households sharing a city or an archetype; the consequence of that clustering is examined in the
Supplementary Information.

## 2.12 Comparison arms

Two simplified scheduling methods are run against the same sampled households and the same
per-household calibrated design powers as the full framework, to isolate what the framework's
diary-based schedule contributes.

The fixed-schedule arm replaces the household's own occupancy, equipment and lighting schedule with
a single reference schedule (the standard residential mid-rise weekday/weekend profile shipped with
the building-model templates) that does not depend on the household, the archetype, or the simulated
year:

$$
S^{\text{fixed}}_{h,d,k} = R_{d,k} \qquad \text{for every household } h
\tag{17}
$$

The average-survey-profile arm instead uses the framework's own diaries, but removes all
household-to-household variation within a cell by assigning every sampled household the same,
cell-level average profile for that year: for cell $c$ and year $y$, with $\text{Pool}_c$ the full
candidate population of that cell (not only the 50 sampled households),

$$
S^{\text{avg}}_{c,y,d,k} = \frac{1}{\lvert \text{Pool}_c \rvert} \sum_{h \in \text{Pool}_c} S^{\text{full}}_{h,y,d,k}
\qquad \text{for every sampled household in } c
\tag{18}
$$

applied identically to the occupancy, equipment fraction, lighting fraction and metabolic series;
each household's own SHEU-calibrated design powers (section 2.6) are kept, so only the sub-daily
shape is replaced, not the annual scale.

## Symbol list

- $s$: day-type stratum (weekday, Saturday, Sunday), or archetype index in section 2.9 where noted.
- $t$: a 30-minute slot index, $t = 1,\dots,48$, 04:00 origin.
- $h,k$: an hour-of-day index, $h,k = 0,\dots,23$ (clock time) or $1,\dots,24$ (position).
- $\text{act30}_t$, $\text{hom30}_t$: the 48-slot activity code and at-home indicator for one diary-day.
- $M_h$: number of member diary-days of household $h$ pooled into one day type.
- $p_{s,t}$: an external target at-home rate for stratum $s$, slot $t$.
- $N_s$: number of diary-days in stratum $s$ being raked.
- $\lambda$: the work-from-home persistence share retained in the 2030 scenario, $\lambda \in \{0, 0.5, 1\}$.
- $\lambda_{\text{act}},\lambda_{\text{home}},\lambda_{\text{cop}},\lambda_{\text{marg}},\lambda_{\text{aux}}$: fixed training loss weights (Eq. 3).
- $w_a$, $w_{a,c}$: national dwelling-stock share of archetype $a$, and its per-city split.
- $B_{\text{shared}}$, $B_{\text{personal}}$: appliance categories used once per household, or once per present person.
- $w_b(a)$: fixed weight of activity $a$ toward appliance category $b$.
- $P_b$, $P_{\text{base}}$: fixed rated power of appliance category $b$, and the fixed baseload power.
- $\eta(n)$: fixed diminishing-returns factor for $n$ co-present members sharing a device.
- $f_e$: the equipment calibration scalar, target annual energy divided by raw annual energy (Eq. 9).
- $R$: the resultant vector length of a circular mean (Eq. 14); $\bar{h}$, $\text{sd}_{\text{circ}}$: circular mean and standard deviation of an hour-of-day quantity.
- $d_i$: the paired difference in a metric for household $i$ between two conditions; $\bar{d}, s_d$: its mean and standard deviation across $n$ paired households.

## Trace table

| Eq. | What it defines | Source (file:line or task doc) | Read by me |
|---|---|---|---|
| 1, 2 | 30-min activity slot and at-home slot | `03_mergingGSS.md:424-432,460` | yes |
| 3 | Generative model training objective | `04D_train.py:60-69,166-330,374-380` | yes |
| 4, 5 | Raking target count and shortfall; applied after matching; floor guard | `05_postlink_rake.py:1-20,79-99`; `06_forecast_rake.py:228-294` | yes (manager) |
| n/a | Raking is single-pass, not iterative (decision) | `05_postlink_rake.py:79-144`; `06_forecast_rake.py:228-294` | yes |
| n/a | 4-level fallback matching, seed; first level without metropolitan area (2022 rebuild, T18b doc) | `impl/2026-09-15_T13_wp1_rebuild_2022_reading.md:96-121` (task doc; cites `05_census_linkage.py:75-213,142,184-193,272-279`) | yes (task doc) |
| 6, 7 | Household occupancy and metabolic aggregation | `07_aug_to_bem.py:93-117` | yes |
| n/a | 48-to-24 slot averaging and 4h clock roll | `07_aug_to_bem.py:103-110` | yes |
| 8 | Activity-driven equipment power per slot | `activity_loads.py:33-59,118-182` | yes |
| n/a | Lighting indicator | `activity_loads.py:169-170` | yes |
| 9 | Equipment calibration scalar $f_e$ | `activity_loads.py:197-265` | yes |
| n/a | "Calibration" framing (SHEU is not validation) | `activity_loads.py:1-20,197-202`; task instruction | yes |
| 10 | 2030 persistence-scenario target | `impl/2026-09-15_WP2_scenario_spec.md:8-19` (manager spec; cites `06_forecast_rake.py:100-161`) | yes |
| n/a | Standardised jump/slope variant | `impl/2026-09-15_WP2_scenario_spec.md:30-37,58-73` | yes |
| 11 | Household sampling, seed, paired panel | `impl/2026-09-15_T05_wp4_sample_size.md:52-74` (task doc; cites `Step8_docs/run_paired_mc.py:1-94`, `main.py:1952-2074`) | yes (task doc) |
| 12 | Stock aggregation weights | `Step8_docs/08_simulation_plots.py:74-77,300-321` | yes |
| 13, 14 | Circular mean and circular SD of peak hour | `Step8_docs/08_simulation_plots.py:278-297` | yes |
| n/a | Annual energy, daily peak | `Step8_docs/08_simulation_plots.py:340,361,377` | yes |
| n/a | Load factor, midday share | `Step8_docs/08_simulation_plots.py:385,387` (window `:114`) | yes |
| n/a | Morning-leaning share | `Step8_docs/08_simulation_plots.py:914-915` | yes |
| n/a | Ramp metric | not found in `Step8_docs/08_simulation_plots.py` (grepped for "ramp") | NOT VERIFIED (absent) |
| 15, 16 | Paired difference and pooled paired Student-t CI | `08_simulation_val.py:951-1027` | yes |
| 17 | Fixed-schedule comparison arm | `impl/2026-09-15_T19_wp3_static_arm_build_smoke.md:6-22` (task doc; cites `idf_optimizer.py:570-624`, `main.py:2029-2113`) | yes (task doc) |
| 18 | Average-survey-profile comparison arm | `impl/2026-09-15_T30_wp3_average_profile_arm.md:9-26` (task doc) | yes (task doc) |
| Table 1 row: IESO | dataset description only, no equation | `impl/2026-09-15_T02_wp5_ieso_measured_profiles.md:1-21` (task doc) | yes (task doc) |
| Table 1 row: weather, archetypes | dataset description only, no equation | `08_simulation.md:14,39,65,87,290` | yes |
