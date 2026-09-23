# Deep-Research Prompt L34: a source reference for every equation in the Methods section

> SCOPE GUARD, READ FIRST. This is a **citation search** for the equations of one journal manuscript
> (target *Energy and Buildings*; synthetic time-use diaries and residential building energy). For each
> equation below we need to know: is it a STANDARD method (then give the original or textbook source), an
> ADAPTED version of a published method (then give the closest published source and say what differs), or
> the author's OWN definition (then say NO SOURCE NEEDED). Do not change, improve or comment on the
> equations, and do not judge the thresholds. If a source cannot be confirmed, write NOT FOUND. An honest
> NOT FOUND is better than a guessed reference.

> Run in Gemini Antigravity with live web search. Save the return as `RL34_equation_sources.md` in this
> folder (`4J_docs_occ/DeepResearchPrompts/`).

---

## Context (for you, not to be cited)

The paper fine-tunes a large language model on daily time-use diaries (10-minute resolution) from two of
three European surveys (Spain 2009-10, Italy 2013-14, United Kingdom 2014-15; Harmonised European Time Use
Survey family) and asks it to write diaries for the third, given only that country's published
demographic tables. The comparison baseline is a raked donor pool: real diaries of the other two countries
reweighted by iterative proportional fitting onto the held-out country's margins. Generated diaries then
drive an appliance and hot-water model and TABULA residential archetypes simulated in EnergyPlus.

References ALREADY in the paper (you may recommend them if they fit; say "already cited"):
Deville and Sarndal (1992), JASA 87(418) 376-382, doi 10.1080/01621459.1992.10475217;
Lovelace et al. (2015), JASSS 18(2) 21, doi 10.18564/jasss.2768;
Beckman, Baggerly and McKay (1996), Transportation Research A 30(6) 415-429;
Richardson, Thomson and Infield (2008), Energy and Buildings 40(8) 1560-1566;
Richardson, Thomson, Infield and Clifford (2010), Energy and Buildings 42(10) 1878-1887 (CREST);
Widen and Wackelgard (2010), Applied Energy 87(6) 1880-1892;
Jordan and Vajen (2001), IEA-SHC Task 26 hot-water profiles report;
Shokri et al. (2017), IEEE S&P, doi 10.1109/sp.2017.41;
Loga, Stein and Diefenbach (2016), Energy and Buildings 132 4-12 (TABULA);
Eurostat HETUS 2008 and 2018 Guidelines.

Notation: a = one of six HETUS level-1 activity aggregates, labelled AC0 (personal care incl. sleep and
eating), AC1_TR (employment incl. related travel), AC2 (study), AC3 (household and family care), AC4-8
(volunteering, social life, sport, hobbies, mass media; the closure category), AC9A (travel other than
work travel). Budgets are minutes per day.

---

## The equations (exact definitions as implemented; symbols defined)

**Eq. 1. Iterative proportional fitting of the donor weights (the baseline).**
Start w_i = 1 for every donor diary i. For each margin variable v in turn (age band, sex, household type,
economic status, day type), with k = category of diary i on v:
cur_v(k) = sum_i w_i * 1[cat(i,v) = k] / sum_i w_i
w_i <- w_i * target_v(k) / cur_v(k)
Repeat full sweeps until max over (v,k) of |cur_v(k) - target_v(k)| <= 0.5 percentage points (at most
200 sweeps). Weights are not integerised.
Needed: the original IPF source (Deming and Stephan 1940 is our guess; verify), and a standard raking /
calibration source (Deville and Sarndal 1992 already cited; confirm it covers raking as a special case,
with the section).

**Eq. 2. Synthetic population: IPF on a multi-way table seeded from a donor joint tally, then
integerisation by the largest-remainder method.**
Same multiplicative update on each axis of an N-dimensional table (structural zeros stay zero), tolerance
1e-13, then counts = floor(x) plus one unit to the cells with the largest fractional parts until the total
is met (ties by index, no random draw).
Needed: a source for IPF with a seed table in population synthesis (Beckman et al. 1996 already cited;
confirm), and a source for largest-remainder (Hamilton) integerisation in population synthesis or
microsimulation (for example Lovelace and Ballas 2013 on integerisation, "truncate, replicate, sample";
verify, and say whether plain largest-remainder is discussed there).

**Eq. 3. Time-budget error and the transfer margin (the primary test).**
MAE = (1/6) * sum over the six aggregates a of |B_model(a) - B_pub(a)|   [minutes per day]
B_pub = the country's published HETUS level-1 time budget for one age band; B_model = the mean budget of
the generated (or raked, weighted) diaries in that band.
margin = MAE_baseline - MAE_model; the model passes a cell only if margin > 0 (strict).
Needed: a standard source for mean absolute error as a forecast or model accuracy measure (for example
Willmott and Matsuura 2005, Climate Research; Hyndman and Koehler 2006, International Journal of
Forecasting; verify). The margin rule is probably our own; say so if you find no precedent.

**Eq. 4. Mean absolute percentage error (the in-sample check).**
APE_a = 100 * |B_model(a) - B_pub(a)| / B_pub(a), only where B_pub(a) >= 10 min/day;
MAPE = mean of APE_a over scored aggregates; below 10 min/day an absolute test |difference| < 15 min/day
is used instead.
Needed: a standard MAPE source (Hyndman and Koehler 2006 discusses MAPE's small-denominator problem;
verify and give the section), which would support the floor rule.

**Eq. 5. Fictional-country steering test: slope and R-squared.**
Published margins are perturbed in five steps to create fictional countries with known expected budgets.
Ordinary least squares of the generated budget y on the expected budget x, each aggregate centred on its
own mean before pooling:  y_c = beta * x_c + e.  Steering: on AC2 alone, beta > 0 and R^2 >= 0.80.
Amplitude: pooled beta over five aggregates (AC4-8 excluded) >= 0.80.
Needed: a standard OLS / coefficient of determination textbook source (for example Montgomery, Peck and
Vining, Introduction to Linear Regression Analysis; verify edition). Also: any published use of
synthetic or "fictional" perturbed target margins to test whether a conditional generator follows its
conditioning (we think NOT FOUND; say so if so).

**Eq. 6. Dwell-time distance (first-order Wasserstein).**
W1 = integral |F_a(x) - F_b(x)| dx, F = weighted empirical cumulative distribution of the length of
uninterrupted stays in one activity, computed exactly on the merged support, survey weights as weights.
Needed: a standard source for the 1-Wasserstein distance as the area between two CDFs (for example
Vallender 1974; Villani, Optimal Transport; or Ramdas, Garcia Trillos and Cuturi 2017; verify which gives
the CDF form, with equation or page).

**Eq. 7. Transition structure (total variation distance).**
TVD(p,q) = 0.5 * sum_k |p(k) - q(k)|, p and q = joint distributions of (from-activity, to-activity)
transitions pooled over diaries.
Needed: a standard source for total variation distance (for example Levin, Peres and Wilmer, Markov Chains
and Mixing Times; verify the definition and page).

**Eq. 8. Diurnal pattern (Jensen-Shannon divergence, base 2).**
JSD(p,q) = H((p+q)/2) - 0.5*H(p) - 0.5*H(q), H(v) = -sum_i v_i log2 v_i, p and q = activity shares per
10-minute slot; bounded in [0,1] bits.
Needed: the original source (Lin 1991, IEEE Transactions on Information Theory; verify volume, pages, DOI,
and whether it states the [0,1] bound for base 2).

**Eq. 9. First-order time-inhomogeneous Markov chain (comparison model).**
P(s_{t+1} = j | s_t = i, t), ten level-1 activity states, 143 ten-minute steps, one chain per day type,
estimated by transition counts; unseen transitions fall back to the next slot's marginal.
Needed: Richardson et al. (2008) and Widen and Wackelgard (2010) are already cited; confirm that each uses a
first-order time-inhomogeneous chain estimated from time-use transition counts, with the section.

**Eq. 10. Membership-inference audit (area under the ROC curve).**
Score per record = mean negative log-likelihood of the record's diary tokens under the fine-tuned model;
reference-calibrated variant = NLL_base - NLL_tuned (base = the same pretrained model before fine-tuning).
AUC computed by the Mann-Whitney rank formula; also true-positive rate at 0.1 % false-positive rate.
Needed: Shokri et al. (2017) already cited; confirm it is the right source for a loss-based attack, or name
the better one (for example Yeom et al. 2018, CSF, for loss thresholds; Carlini et al. 2022, IEEE S&P,
"Membership inference attacks from first principles", for TPR at low FPR and reference-model calibration;
verify both). Also the Mann-Whitney / AUC equivalence (Hanley and McNeil 1982, Radiology; verify).

**Eq. 11. Distance to closest record.**
d = (number of mismatched 10-minute slots) / 144 (normalised Hamming distance); DCR = distance to the
nearest training diary; NNDR = d_nearest / d_second_nearest.
Needed: a source for distance-to-closest-record and nearest-neighbour distance ratio as privacy checks for
synthetic data (for example Park et al. 2018, "Data synthesis based on generative adversarial networks",
PVLDB; or later synthetic-data privacy papers; verify which defines NNDR).

**Eq. 12. Appliance start hazard (two-stage trigger).**
Stage 1: an appliance is eligible in a minute only if a household member's diary activity maps to it.
Stage 2: a constant per-eligible-minute start probability h, calibrated so that the stock reproduces the
published cycles per year:
available = E - C * (L + D) * (E / 525600);   h = C / available
E = mean eligible minutes per dwelling-year, C = cycles per year, L = cycle length (min), D = restart
delay (min). Cycle length Gaussian N(L, L/10) for some appliances. The code states this is CREST's
calibration adapted (CREST: lambda = cycles / (year minutes * P_occupied - running time - cycles * delay),
divided by the mean activity probability).
Needed: confirm in Richardson et al. (2010) the exact CREST calibration equation (equation number) so that
we can state precisely how ours differs.

**Eq. 13. Domestic hot water draws.**
Four draw categories after Jordan and Vajen (2001), 200 litres per day for a single-family house, flow per
event from a Gaussian, discretised to 0.2 l/min; per-category hazard h = N / (E - N * (d - 1)), N = target
draws, E = eligible minutes, d = draw duration. Draws are placed by diary activity instead of Jordan and
Vajen's calendar probabilities.
Needed: the exact bibliographic record of Jordan and Vajen (2001) (report number, version, publisher,
URL) and, if it exists, a peer-reviewed paper by the same authors describing the same tapping model
(for example in Solar Energy); and the table in which the four categories and their mean flows are given.

**Eq. 14. Occupancy-driven internal gains (already displayed in the paper).**
phi_int(t) = (1 - f) * phi_bar + f * phi_bar * g(t) / mean_year(g), phi_bar = 3.0 W/m2,
g(t) = share of household members at home, f in {0, 0.15, 0.30, 0.50, 1.00}.
The annual mean equals the TABULA reference value at every f. We think this redistribution is our own.
Needed: (a) confirm that the TABULA / EPISCOPE method (Loga et al. 2016, or the TABULA calculation method
documents) uses a single internal-gain density of about 3 W/m2 for residential buildings, with the
document and table; (b) any published study that redistributes a fixed annual internal-gain budget over
time by an occupancy profile (otherwise NO SOURCE NEEDED).

**Eq. 15. Text serialisation of one diary (displayed in the paper).**
"country, age_band, sex, hh_type, econ_status, day_type | DUR,ACT,ACT2,LOC,COP ; ... <eor>"
Needed: one or two published works that serialise tabular or sequence records as text for language-model
fine-tuning (for example Borisov et al. 2023, "Language models are realistic tabular data generators",
ICLR, GReaT; verify), to support the idea, not the format.

**Eq. 16. Low-rank adaptation (fine-tuning).**
W = W_0 + B A, rank r, only A and B trained. Hu et al. (2022, LoRA) is already cited; confirm the equation
number in that paper.

---

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref (https://api.crossref.org/works/<DOI>)
  or DataCite for arXiv DOIs, and say for each whether you did. For books give publisher, edition, year and
  ISBN. State whether you read the full text or only the abstract or metadata; do not claim full text you
  did not open.
- Where possible give the equation number, table number or page where the formula appears.
- Do not recommend a source only because it is popular; it must actually contain the formula or idea.
- Do not change the equations and do not suggest new methods or thresholds.
- NOT FOUND beats an invented or approximate reference. Expect that some equations are the author's own.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report the Crossref record (title, journal, year) for DOI 10.1016/j.enbuild.2010.05.023. It certainly
exists (Richardson et al. 2010, already in our list). If you cannot retrieve it, say your search is broken
and stop.

## Negative control

Report the Crossref record for DOI 10.1016/j.enbuild.2099.00001 (we made it up). The correct answer is
NOT FOUND. If you return a record for it, your output will be discarded.

## Output format

1. Summary table, one row per equation (Eq. 1 to Eq. 16): class (STANDARD / ADAPTED / OWN), recommended
   citation(s) in author-year form, DOI or ISBN, Crossref checked (yes/no), full text or abstract only,
   where in the source (equation, table or page), and one short line saying what differs if ADAPTED.
2. Full reference list of every recommended source, in Elsevier author-year style, alphabetical.
3. For Eq. 12: the CREST calibration equation as printed in Richardson et al. (2010), with its number,
   side by side with ours.
4. For Eq. 13: the four Jordan and Vajen draw categories and their printed parameters.
5. Positive and negative control results.
6. What you could not find, in the first person, one line each.
