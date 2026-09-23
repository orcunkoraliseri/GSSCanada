# Deep-Research Prompt dr_2J-17: a source reference for every equation in the Methods section

> SCOPE GUARD, READ FIRST. This is a **citation search** for the equations of one journal manuscript
> (Applied Energy, residential building energy simulation). For each equation below we need to know:
> is it a STANDARD method (then give the original or textbook source), an ADAPTED version of a
> published method (then give the closest published source and say what differs), or the authors'
> OWN definition (then say NO SOURCE NEEDED). Do not change, improve or comment on the equations.
> If a source cannot be confirmed, write NOT FOUND. An honest NOT FOUND is better than a guessed reference.

> Run in Gemini Antigravity with live web search.

---

## Context (for you, not to be cited)

The paper builds household occupancy schedules from Canada's national time-use survey (diaries at
10-minute resolution), trains a generative sequence model (encoder-decoder with cross-attention) on
them, matches diaries to census households, turns activities into equipment and lighting loads,
projects 2030 work-from-home scenarios, simulates the buildings, and compares hourly load-shape
metrics between years with a paired confidence interval.

References ALREADY in the paper (you may recommend them if they fit; say "already cited"):
Richardson, Thomson and Infield (2008), Energy and Buildings 40(8) 1560-1566, doi 10.1016/j.enbuild.2008.02.006;
Widen and Wackelgard (2010), Applied Energy 87(6) 1880-1892, doi 10.1016/j.apenergy.2009.11.006;
Eurostat (2018), HETUS 2018 Guidelines; Denholm et al. (2015), NREL "duck chart" report;
Barrero, Bloom and Davis (2021, 2023) on work from home; Armstrong et al. (2009); Wilke et al. (2013).

---

## The equations (exact text from the manuscript; numbers are the manuscript's)

**Eq. 1 (activity per 30-minute slot, majority vote of three 10-minute codes)**
act30_s = mode(slot_{3s-2}, slot_{3s-1}, slot_{3s})

**Eq. 2 (at home in a 30-minute slot if at least 2 of 3 ten-minute slots are at home)**
hom30_s = 1[ sum_{k=1..3} home_{3(s-1)+k} >= 2 ]
Question: is there a published time-use harmonization practice for aggregating 10-minute diary slots
into coarser slots by majority rule (for example in HETUS guidelines, the Multinational Time Use Study
(MTUS), or occupancy-modelling papers that down-sample time-use diaries)?

**Eq. 3 (training loss of the generative model)**
L = sum_{t=1..48} [ lambda_act * l_act_t + lambda_home * l_home_t + lambda_cop * l_cop_t ] + lambda_marg * l_marg + lambda_aux * l_aux
where l_act is categorical cross-entropy, l_home and l_cop are binary cross-entropy, l_marg is a
penalty on the gap between the model's and the observed average at-home rate, l_aux is an auxiliary
classification loss. Needed: (a) a standard source for cross-entropy losses as negative log-likelihood;
(b) a source for a weighted sum of task losses in multi-task learning; (c) the original source of the
encoder-decoder architecture with cross-attention (the Transformer).

**Eq. 4 and Eq. 5 (raking the at-home share of each slot to a target)**
n_tgt_{s,t} = clip(round(p_{s,t} * N_s), 0, N_s)
Delta_{s,t} = n_tgt_{s,t} - n_cur_{s,t}
Then Delta records are flipped (away to home, or home to away), preferring records at an activity
change point. It is a single pass that hits an exact integer count, NOT iterative proportional fitting.
Needed: the original raking / iterative proportional fitting source (Deming and Stephan 1940 is our
guess; verify), a standard calibration-weighting source (Deville and Sarndal 1992 is our guess;
verify), and, if one exists, any published method that adjusts binary sequences to exact marginal
counts by flipping the fewest records (for example in synthetic population or microsimulation work).
If none exists, say NOT FOUND and we will call it the authors' own variant.

**Eq. 6 and Eq. 7 (household average of members' at-home and metabolic values)**
occ48_{h,d,t} = (1/M_h) * sum_{m=1..M_h} hom30^{(m)}_{h,d,t}
met48_{h,d,t} = (1/M_h) * sum_{m=1..M_h} W_met(act30^{(m)}_{h,d,t})
W_met is a fixed activity-to-watts-per-person table. Values used (watts per person): work and
related 125; household work and maintenance 175; caregiving and help 190; purchasing goods and
services 195; sleep, naps and resting 70; eating and drinking 105; personal care 170; education 110;
socializing 90; passive leisure 85; active leisure 245; community and volunteer 105; travel 140;
miscellaneous or idle 135; unknown activity 100. Needed: the most likely published source of such per-activity metabolic rates
for building simulation (for example ASHRAE Handbook of Fundamentals, the chapter on thermal comfort,
metabolic rate table; ISO 8996; the EnergyPlus documentation; or the Compendium of Physical
Activities). Report which source's table matches these values best, with the table number.

**Eq. 8 (activity-driven equipment power at one slot)**
P_t = P_base + sum_{b in B_shared} ( max_{i=1..n_t} w_b(a_i) ) * P_b * eta(n_t) + sum_{b in B_personal} ( sum_{i=1..n_t} w_b(a_i) ) * P_b + P_dw(t) * eta(n_t)
Shared devices (cooking, washer, dryer, TV) use the highest weight among the people present times a
diminishing co-occupancy factor eta(n); personal devices (computer) add up per person; P_base is an
always-on baseload. eta values used: eta(1) = 1.0, eta(2) = 1.4, eta(3) = 1.7, eta(4) = 1.9,
eta(5 or more) = 2.0. Our code notes point to the CREST model: Richardson et al. (2010), "Domestic
electricity use: A high-resolution energy demand model", Energy and Buildings; and the "effective
occupancy" table of Richardson et al. (2009), "Domestic lighting: A high-resolution energy demand
model", Energy and Buildings. Verify both (volume, pages, DOI) and report the exact effective-occupancy
values each paper gives, so we can state honestly whether our eta values are taken from it, rounded
from it, or only inspired by it. Also say whether Widen and Wackelgard (2010) supports the
activity-to-appliance mapping idea.

**Eq. 9 (calibration scalar)**
f_e = E_tgt / E_raw
E_tgt is the annual end-use energy by dwelling type from Natural Resources Canada's Survey of
Household Energy Use (SHEU) 2019. Needed: the correct citation of SHEU 2019 (publisher, year, URL),
and one published building-energy paper that scales simulated appliance energy to a national survey
total in this way.

**Eq. 10 (2030 scenario target)**
target_lambda[s,t] = clip( stock_2022[s,t] + 8 * slope_{s,t} - (1 - lambda) * jump_{s,t}, 0, 1 ), lambda in {1, 0.5, 0}
slope is a linear trend fitted through the 2005, 2010 and 2015 values; jump is the 2022 value minus
the trend at 2022. We think this is the authors' own definition. Needed only: one or two published
sources that treat the post-pandemic work-from-home level as a persistence share or scenario (keep all,
keep part, revert), to support the idea, not the formula.

**Eq. 11 (simple random sample of 50 households, without replacement)**
Needed: a standard survey-sampling textbook source (Cochran, Sampling Techniques, is our guess; verify
the edition).

**Eq. 12 (stock weights)**
w_{a,c} = w_a / |C_a|, sum_a w_a = 1
Own definition, we think. Needed only if you find a published stock-weighting precedent in
urban or national building stock energy modelling; otherwise NO SOURCE NEEDED.

**Eq. 13 and Eq. 14 (circular mean and circular standard deviation of the daily peak hour)**
h_bar = (24 / 2 pi) * atan2( mean(sin theta), mean(cos theta) ) mod 24, theta_i = 2 pi h_i / 24
R = sqrt( mean(sin theta)^2 + mean(cos theta)^2 )
sd_circ = (24 / 2 pi) * sqrt( -2 ln R )
Needed: the standard textbook sources for the circular mean and for the circular standard deviation
sqrt(-2 ln R) (Mardia and Jupp, Directional Statistics; Fisher, Statistical Analysis of Circular Data;
verify which one defines sqrt(-2 ln R), with the equation or page number).

**Load factor, midday share and evening ramp (inline definitions)**
LF = mean hourly load / annual peak hourly load;
midday share = energy between 09:00 and 17:00 / daily energy;
ramp = mean over days of (load at 17:00 minus load at 14:00).
Needed: a standard power-systems source defining load factor; a source for evening ramp as a grid
metric (Denholm et al. 2015 is already cited; confirm it fits or suggest a better one).

**Eq. 15 and Eq. 16 (paired difference and its Student-t confidence interval)**
d_i = M_i^(B) - M_i^(A);  d_bar +/- t_{0.975, n-1} * s_d / sqrt(n)
Needed: one standard statistics textbook source for the paired t confidence interval (for example
Montgomery and Runger, Applied Statistics and Probability for Engineers; verify edition).

**Eq. 17 (fixed-schedule comparison arm)**
S_fixed_{h,d,k} = R_{d,k} for every household h
R is the standard mid-rise apartment weekday/weekend schedule of the US Department of Energy
prototype building models for ASHRAE Standard 90.1 (the "ApartmentMidRise" prototype, developed by
PNNL), as distributed in the OpenStudio-Standards schedule library. Needed: the correct citation for
the DOE/PNNL prototype building models (the ApartmentMidRise model and its schedules), and for
OpenStudio-Standards if it has a citable reference.

**Eq. 18 (average-profile comparison arm)**
S_avg_{c,y,d,k} = (1/|Pool_c|) * sum_{h in Pool_c} S_full_{h,y,d,k}
Own definition, we think. Needed: one or two published studies that compare an average (or standard)
occupancy profile with stochastic or household-level profiles in building energy simulation, to
support the comparison idea.

---

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref (https://api.crossref.org/works/<DOI>)
  and report that you did. For books give publisher, edition, year and ISBN.
- Where possible give the equation number, table number or page where the formula appears.
- Do not recommend a source only because it is popular; it must actually contain the formula or idea.
- Do not change the equations and do not suggest new methods.
- NOT FOUND beats an invented or approximate reference. Expect that some equations are the authors' own.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report the Crossref record (title, journal, year) for DOI 10.1016/j.enbuild.2008.02.006. It certainly
exists (Richardson et al. 2008, already in our reference list). If you cannot retrieve it, say your
search is broken and stop.

## Output format

1. Summary table, one row per equation (Eq. 1 to Eq. 18, plus "LF / midday / ramp"): class
   (STANDARD / ADAPTED / OWN), recommended citation(s) in author-year form, DOI or ISBN, Crossref
   checked (yes/no), where in the source (equation, table or page), and one short line saying what
   differs if ADAPTED.
2. Full reference list of every recommended source, in Elsevier author-year style.
3. For Eq. 7: the metabolic-rate table comparison (our values vs the source's values).
4. For Eq. 8: the effective-occupancy values from Richardson et al. (2009) and (2010), side by side
   with ours.
5. Positive control result.
6. What you could not find, in the first person, one line each.

Save the return as `dr_2J-17_equation_sources_gemini_results.md` in the same folder as this prompt.
