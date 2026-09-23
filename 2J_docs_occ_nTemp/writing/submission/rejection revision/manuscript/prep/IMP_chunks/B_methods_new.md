# 2. Proposed modelling and simulation framework

The framework turns household time-use diaries into occupancy schedules for building energy
simulation (Figure 1). Time-use diaries and census households feed a generative occupancy model. The
resulting household schedules and activity-driven loads drive building simulations. These cover 2022
and three 2030 work-from-home scenarios.

![](../../figures/Figure_01_workflow.png){width=16cm}

**Figure 1.** Overview of the modelling and simulation framework.

The framework is a chain of eleven stages. The first three stages are diary harmonization, a
generative day-type model and marginal raking to match independent targets. Diary donors are then
matched to a census-representative population. Household members are aggregated into hourly
schedules, and activity-driven end-use loads are added. A scenario-based projection moves the
schedules to a future year. Households are then sampled for simulation, and the simulation output is
aggregated to the national housing stock. The last two stages are load-shape metrics and a paired
statistical comparison. This comparison runs across years and across alternative scheduling methods.
Sections 2.1 to 2.6 define each stage. Table 1 lists the datasets and their role. Measured hourly
load is used only as an external check, not as a model input.

**Table 1.** Datasets and their role in the framework.

| Dataset | Years / vintage | What it provides | Framework stage(s) |
|-----------|------------|------------------------------------------|------------------------------------|
| GSS time-use diaries | 2005, 2010, 2015, 2022 cycles | Respondent-level 10-minute activity and location diaries, harmonized to a common activity code list | Source diaries for the generative model (2.1, 2.2) and for the raking targets (2.2) |
| Census public-use microdata | 2021 | Household composition, dwelling type, tenure and geography for a representative population of households | Recipient population for diary matching and the base population whose schedules are aggregated (2.3) |
| NRCan SHEU end-use reference | 2019 survey | National annual end-use energy totals by dwelling type (appliances, lighting) | Calibration target for the activity-driven end-use loads (2.4) |
| Weather files | typical-meteorological-year (TMYx) | Hourly outdoor conditions for each climate zone | Building simulation input alongside the injected schedules (2.3, 2.5) |
| Building archetype models | fixed archetype geometry and construction | Four dwelling archetypes at six city/climate-zone weather stations, the physical envelope each household's schedule is run against | Building simulation and stock aggregation (2.5) |
| IESO hourly consumption by postal area (IESO 2022) | 2022 | Measured hourly electricity use of residential customers, with premise counts, aggregated for Toronto and for Ontario as a whole; an external reference series, not a model input | External check of the simulated load shape (3.6); no simulation input role |

## 2.1 Data and diary preparation

Each respondent's diary starts at 10-minute resolution. It holds 144 activity codes and 144 binary
at-home indicators. Together they cover one full day from a 04:00 origin. The diary is downsampled
to 48 slots of 30 minutes, which the generative model and every later stage use. The activity code
of a 30-minute slot is the majority vote (mode) of its three 10-minute codes. The rare three-way ties
are resolved in a separate step. A 30-minute slot counts as at home when at least two of its three
10-minute slots are at home (Appendix B, Eqs. B.1 and B.2). Figure 2 shows this step with a small
example. In Figure 2, two of Person A's first three ten-minute slots are at home, so Person A's first
30-minute slot counts as at home. Only one of Person A's next three slots is at home, so the second
30-minute slot counts as away. The activity of the first slot is Cooking, the most frequent of its
three codes.

![](../../figures/Figure_M1_diary_to_hourly.png){width=16cm}

**Figure 2.** Conversion of a ten-minute diary into an hourly household occupancy value.

The resulting 48-slot series is the common unit of the framework. The training target of the
generative model uses this form. So do the raking target, the census-matched donor and the
household-schedule input to the building simulation. All of them are expressed as the same 48 slots
from a 04:00 origin.

## 2.2 Generative occupancy model and calibration

The generative model is a sequence model with an encoder-decoder structure. The encoder builds one
conditioning representation from three inputs. These are the respondent's demographic profile, the
survey cycle and the target day-type stratum (weekday, Saturday, Sunday). The demographic profile
covers age group, sex, marital status, household size and labour-force status. The decoder produces
the 48-slot day, conditioned on that representation through cross-attention. At each slot, the
decoder outputs three sets of logits. The first is a 14-way activity categorical. The second is a
binary at-home indicator. The third is a 9-channel co-presence indicator (who else is present).

Training minimizes a weighted combination of the per-slot negative log-likelihoods of these three
outputs. Given the decoder state, the three distributions are treated as conditionally independent.
Two regularization terms are added to this loss (Appendix B, Eq. B.3). The first penalizes the gap
between the model's average at-home rate and the observed average at-home rate. The second is a small
auxiliary loss that predicts the target day-type stratum from the decoder state. The loss weights are
fixed training parameters, not fitted.

Raking then adjusts the at-home share to independent targets. It is applied after census-to-diary
matching (Section 2.3), to the matched population. There are two rakes, each run per day-type stratum
and 30-minute slot. For the survey year, the model-generated diary-days are raked to the at-home rate
of the real respondents. For 2030, the matched population is raked to the scenario target of Section
2.5. Both rakes use the same mechanism, which is a single deterministic pass.

For each stratum and slot, the target at-home rate times the number of diaries gives a target count.
This count is rounded to an integer and clipped to the valid range. The number of records to flip is
the gap between the target count and the current count of at-home records (Appendix B, Eqs. B.4 and
B.5). If the gap is positive, that many away records are flipped to at home. If it is negative, that
many at-home records are flipped to away. Candidates at an activity-transition boundary are chosen
first. At such a record, the neighbouring slot's value differs from the current slot. Remaining ties
are broken by a fixed random seed. Figure 3 shows this adjustment for one slot. In Figure 3, 4 of 10
records are at home and the target share is 0.6. The target count is therefore 6, so 2 records
change from away to at home.

![](../../figures/Figure_M2_raking.png){width=16cm}

**Figure 3.** Adjustment of the at-home count in one time slot to its target.

The target count is met exactly by construction, up to the number of available candidate records.
There is therefore no convergence tolerance and no iteration count. One pass over every (stratum,
slot) pair reproduces the target count exactly, or as closely as the available candidates allow. The
procedure is thus a minimal-flip integer rake to an exact per-slot count. It is not an iterative
multiplicative proportional fitting. For the survey year, a floor guard follows. It applies to
single-person households whose daily at-home mean the rake pushed below a fixed floor. For these
households, night slots are restored to at home until the floor is met.

## 2.3 From diaries to household schedules

Each synthetic (census) household member receives a donor diary. The donor comes from a four-level
fallback search. The levels are tried in order until one gives a non-empty donor group for that
Census record:

1. an exact match on age group, sex, marital status, household size, labour-force status and
   province, within the same day-type stratum;
2. a match on age group, sex, labour-force status and province only, within the same day-type
   stratum;
3. a match on age group and sex only, within the same day-type stratum;
4. a random draw from every diary of the same day-type stratum, regardless of demographics. This
   level is used only when no donor shares even age group and sex.

Within the level that supplies the donor group, one donor is drawn uniformly at random. The day-type
stratum is assigned to each Census record first, because the census record carries no diary day. The
assignment uses a fixed 5:1:1 weekday-to-Saturday-to-Sunday probability split. All random draws use
a fixed seed. Survey cycle is not a matching key. The donor pool for a given year is built from that
year's own diaries only. The 2022 stock uses 2022 diaries, and each earlier cycle uses its own
diaries. Metropolitan area is not a key either. It is nested within province. It was dropped from
the first level so that more people keep household size as a matched attribute. As a consequence, a
donor shares the recipient's metropolitan area less often, which is a limitation.

Every household member now has a 48-slot activity and at-home series. The series comes from the
harmonized diary, the generative model or the matched donor, depending on the year. The household
schedule is built by averaging across members, for each day type and slot. The day types are weekday
and weekend, with Saturday and Sunday pooled into one weekend day type. The fraction of the household
at home is the mean of the members' at-home indicators. The household metabolic rate is the mean,
over the same records, of a fixed activity-to-watts lookup (Appendix B, Eqs. B.6 and B.7). A fixed
default applies to activity codes without an entry.

Both 48-slot series are then averaged in pairs into 24 hourly values (Appendix B). The result is
rolled by four hours, so that clock hour 0 (midnight) lines up with the weather file's clock. The
diary's own origin is 04:00, not midnight. Figure 2 shows these last two steps. Persons A and B are
both at home in the first 30-minute slot, so the household value is 1.0. In the second slot only
Person B is at home, so the value is 0.5. The hourly value is the mean of the two, 0.75.

The equipment and lighting fractions of Section 2.4 are attached to the same household, day-type and
hour rows. They receive the same four-hour roll. The output is one row per household, day type and
hour. Its column format is the one the schedule-injection function of the building simulation
consumes. Each household contributes exactly one weekday row set and one weekend row set. These form
the schedule file of that year's simulation.

## 2.4 Activity-driven end-use loads

End-use equipment power and lighting state are built slot by slot from the same household diary. This
step comes before the 48-to-24 averaging of Section 2.3. The equipment power of a slot depends on who
is at home and what they do (Figure 4). Some devices are shared by the household, and some are
personal. In Figure 4, Person 1 is cooking and Person 2 is watching TV, so both feed the shared
devices. Shared devices are used once per household. Person 3 is using a computer, which is a
personal device and adds up per person.

![](../../figures/Figure_M3_activity_to_power.png){width=16cm}

**Figure 4.** Construction of household equipment power from the activities of the people at home.

At slot $t$, $n_t$ household members are present (at home), with activities $a_1, \dots, a_{n_t}$.
The raw equipment power is a baseload plus a sum over device categories:

$$
P_t = P_{\text{base}} + \sum_{b \in B_{\text{shared}}} \Big(\max_{i=1,\dots,n_t} w_b(a_i)\Big) P_b\, \eta(n_t)
\;+\; \sum_{b \in B_{\text{personal}}} \Big(\sum_{i=1,\dots,n_t} w_b(a_i)\Big) P_b
\;+\; P_{\text{dw}}(t)\, \eta(n_t)
\tag{1}
$$

Here, $B_{\text{shared}}$ is the set of appliance categories one household uses at a time (cooking,
washer, dryer, television). $B_{\text{personal}}$ is the set used per person (a personal computer).
$w_b(a)$ is a fixed weight giving how strongly activity $a$ implies use of category $b$. $P_b$ is a
fixed rated power for category $b$. $\eta(n_t)$ is a fixed, non-decreasing diminishing-returns factor
for shared-device co-occupancy. It has $\eta(0)=0$ and $\eta(1)=1$, and it saturates at a fixed cap
for five or more present members. $P_{\text{dw}}(t)$ is a separate dishwasher term. Once a present
member's activity triggers it, it runs for a fixed number of slots. It then enforces a fixed cooldown
before it can trigger again. The lighting indicator is binary. $\text{light}_t = 1$ if any present
member's activity has a non-zero lighting weight, else 0.

The 48-slot raw series is averaged into 24 hourly values exactly as in Section 2.3. It is then scaled
to an external annual-energy target by dwelling type from the NRCan SHEU reference. The equipment
target is net of the refrigerator load, which the building model already represents separately. This
avoids double-counting. $E_{\text{raw}}$ is the raw annual equipment energy. It follows from the
24-hour weekday/weekend profile and a fixed weekday/weekend day count. $E_{\text{tgt}}$ is the SHEU
target for that dwelling type. The calibration scalar is

$$
f_e = \frac{E_{\text{tgt}}}{E_{\text{raw}}}
\tag{2}
$$

The scalar is applied to the peak raw hourly power to obtain the design power of the building
simulation. It is also applied to the raw hourly series divided by its own peak. This gives an
equipment fraction schedule from 0 to 1. Lighting is scaled the same way, using total annual
lit-hours in place of raw energy. This SHEU agreement calibrates the design power and duty fraction to
an external annual total. It is not a validation of the sub-hourly shape. That shape is not compared
against any external end-use time series.

## 2.5 2030 scenarios, household sampling and stock weighting

The 2030 stock keeps the same households and the same raking mechanism as Section 2.2. Only the
at-home target changes. A linear trend $\text{slope}_{s,t}$ is fit through the stratum-slot at-home
means of the 2005, 2010 and 2015 cycles. The 2022 deviation from that trend line is
$\text{jump}_{s,t} = \text{obs}_{2022,s,t} - \text{trend}_{s,t}(2022)$. It is treated as a
pandemic-era level shift that may or may not persist. The three scenarios differ only in the share
$\lambda$ of that shift assumed to remain in 2030 (Figure 5). In Figure 5, the blue line keeps all of
the 2022 jump and runs parallel to the trend. The green line keeps half of the jump. The orange line
goes back to the pre-pandemic trend by 2030.

![](../../figures/Figure_M4_2030_scenarios.png){width=16cm}

**Figure 5.** Construction of the three 2030 scenarios from the pre-pandemic trend and the 2022 jump.

The 2030 at-home target of each scenario is

$$
\text{target}_{\lambda}[s,t] = \operatorname{clip}\Big(
\text{stock}_{2022}[s,t] + 8 \cdot \text{slope}_{s,t} - (1-\lambda)\,\text{jump}_{s,t}
,\ 0,\ 1\Big),
\qquad \lambda \in \{1,\ 0.5,\ 0\}
\tag{3}
$$

Thus $\lambda = 1$ keeps the full 2022 shift, and $\lambda = 0.5$ assumes half of it has faded.
$\lambda = 0$ assumes it has fully faded, so 2030 sits on the pre-2022 trend line. A second,
standardized version of the same equation, $\text{target}_{\text{std}}$, serves as a sensitivity
check. Its trend and shift are computed after reweighting every cycle's diaries to the 2030 stock's
composition. This composition is by age group, sex and labour-force status. The standardized version
is reported alongside the primary version. The result is a target array in the same form as the
survey-year target, raked exactly as in Section 2.2. This is a scenario-based projection of a stated
persistence assumption, not a forecast. No scenario claims to predict which value of $\lambda$ will
occur.

The building simulations cover 24 modelled cells (4 dwelling archetypes $\times$ 6 city/climate-zone
stations). For each cell, the candidate pool holds every household identifier present in the schedule
files of all years simulated together. The pool is restricted to that cell's archetype and province.
It is further restricted to households whose loaded schedules pass a plausibility check on the daily
occupancy pattern. This check belongs to the integration layer itself. The pool therefore depends on
the numeric content of the schedule files, not only on which households they list. The Supplementary
Information states what this implies for comparing this study's schedule set against an earlier one.

From this pool, $N = 50$ households are drawn without replacement (Appendix B, Eq. B.8). Sampling
with replacement is a fallback, used only if the pool holds fewer than 50 households for that cell.
This case was not encountered in the campaign reported in this paper. The random generator of each
cell is seeded by a fixed base seed together with a deterministic offset. The offset is derived from a
hash of the cell's own label. The same base seed therefore reproduces the same 50 households for a
given cell on any machine. The same 50 households are used for every cycle-year simulated for that
cell, which makes a paired panel. Only the injected occupancy, equipment and lighting schedule changes
by year. The building archetype and weather file are held fixed.

A national figure summarizes the 24 simulated cells. Each cell's result is weighted by its dwelling
archetype's share of the national housing stock. This share is an external reference composition. It
is held fixed across all years and is not derived from this paper's own samples. The shares are
renormalized over the four modelled archetypes. Each archetype-level weight is then split equally
across the (up to six) cities that host that archetype:

$$
w_{a,c} = \frac{w_a}{\lvert C_a \rvert}, \qquad \sum_{a} w_a = 1
\tag{4}
$$

Here, $C_a$ is the set of cities simulated for archetype $a$. A national metric is then the weighted
average of the 24 cells' values, $\bar{x} = \sum_{a,c} w_{a,c}\, x_{a,c}$. The circular peak-hour
metric of Section 2.6 is averaged on its sine and cosine components. The mean angle is then computed
again from these averages. This is needed because circular quantities cannot be averaged directly,
due to the wrap from 23:00 to 00:00.

## 2.6 Load-shape metrics, statistics and comparison methods

All load-shape metrics are computed from the hourly whole-building electricity meter. The meter output
is first converted from the simulator's native energy units to kW. Annual energy is the sum of the
8,760 hourly kW values for the year. Daily peak is the mean, over the year's days, of that day's
maximum hourly kW. The peak hour of day is circular (0 to 23, wrapping at midnight). Its central
tendency therefore uses the circular mean. Its dispersion is Mardia's circular standard deviation
(Appendix B, Eqs. B.9 and B.10).

Load factor is the ratio of the year's mean hourly load to its single annual peak hourly load,
$\text{LF} = \overline{P}/P_{\max}$. Midday share is the fraction of annual energy delivered in the
09:00 to 17:00 window, $\text{midday} = \sum_{h \in [9,17)} P_h \big/ \sum_h P_h$. Morning-leaning
share is the fraction of units whose circular mean peak hour falls in $[0,12)$. The units are
households or days, depending on the aggregation level. Evening ramp is the increase in whole-building
hourly load from the 14:00 hour to the 17:00 hour. It is averaged over the 365 days of the year,
$\text{ramp} = \frac{1}{365}\sum_{d} (P_{d,17} - P_{d,14})$.

Every year-to-year or arm-to-arm comparison in this paper uses the same paired-difference
construction. Take a metric $M$ and two conditions A and B, for example two simulation years. The
household-level results are joined on the household's identifying key (archetype, city, household
identifier). Only households present under both conditions are kept. The paired difference is the
metric under B minus the metric under A. It is computed for each of the $n$ paired households
(Appendix B, Eq. B.11). The reported interval is the standard pooled paired Student-t 95% confidence
interval on the mean difference:

$$
\bar{d} \;\pm\; t_{0.975,\,n-1}\ \frac{s_d}{\sqrt{n}}
\tag{5}
$$

Here, $s_d$ is the sample standard deviation of $d_i$ across the $n$ paired households. It is pooled
across every simulated cell, not computed separately per cell. A one-sample t-test of
$H_0: \bar{d}=0$ is reported alongside it. A difference is treated as separable from zero only when
this interval excludes zero. The interval treats households as independent. It does not account for
households sharing a city or an archetype. Section 3.8 and the Supplementary Information examine the
consequence of this clustering. For midday share, where it matters, the wider clustering-aware
interval is the one reported (Section 3.4).

Two simplified scheduling methods, the comparison arms, isolate what the framework's diary-based
schedule contributes. Both run against the same sampled households as the full framework. Both also
use the same per-household calibrated design powers. The fixed-schedule arm replaces the household's
own occupancy, equipment and lighting schedule with a single reference schedule. This is the standard
residential mid-rise weekday/weekend profile shipped with the building-model templates. It does not
depend on the household, the archetype or the simulated year (Appendix B, Eq. B.12).

The average-survey-profile arm instead uses the framework's own diaries. It removes all
household-to-household variation within a cell. Every sampled household receives the same cell-level
average profile for that year. For cell $c$ and year $y$, $\text{Pool}_c$ is the full candidate
population of that cell, not only the 50 sampled households:

$$
S^{\text{avg}}_{c,y,d,k} = \frac{1}{\lvert \text{Pool}_c \rvert} \sum_{h \in \text{Pool}_c} S^{\text{full}}_{h,y,d,k}
\qquad \text{for every sampled household in } c
\tag{6}
$$

This average applies identically to the occupancy, equipment fraction, lighting fraction and metabolic
series. Each household keeps its own SHEU-calibrated design powers (Section 2.4). Only the sub-daily
shape is replaced, not the annual scale.
