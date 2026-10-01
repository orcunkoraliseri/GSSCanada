# Canadian residential occupancy schedules from four time-use cycles (2005–2022) and a hindcast-tested projection to 2025

Orcun Koral Iseri^a,\*^, Caroline Hachem-Vermette^a^

^a^ Department of Building, Civil and Environmental Engineering, Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* Corresponding author. E-mail address: orcunkoral.oseri@concordia.ca

### Abstract

Occupancy schedules for building performance simulation are usually fitted to one survey year and treated as fixed. This study builds household presence, activity and metabolic schedules for Canada from four General Social Survey time-use cycles (2005–2022) linked to the Census, and projects the household population to 2025 with a conditional variational autoencoder and a cluster-based drift model. In a hindcast against the held-out 2021 Census, the projection beat carrying the 2016 population forward on only 7 of 24 variables, missing the pre-set pass rule, so the 2025 cohort is used as a scenario, not a forecast. Households were at home 15.6–16.2 h per weekday in 2005–2015 and 17.9 h in 2022. Against a standard apartment schedule, the survey-based schedules raised simulated heating by 6–16 % and lowered cooling by 1–9 % in three Montreal house neighbourhoods, and changed both by under 7 % in three apartment neighbourhoods.

### Keywords

Occupancy schedules; time-use survey; longitudinal analysis; occupant behaviour; conditional variational autoencoder; population projection; building performance simulation; Canada

### Highlights

- Four Canadian time-use cycles (2005–2022) harmonised into household schedules
- Presence was flat from 2005 to 2015 and rose in weekday daytime in 2022
- A hindcast against the held-out 2021 Census tests the 2025 projection
- Survey schedules raise house heating 6–16 % and cut cooling 1–9 % vs a default
- Occupancy changes the size of the cooling peak, not its timing

# 1 Introduction

## 1.1 Time-use surveys in occupancy modelling

Occupancy models for building performance simulation (BPS) turn observed or surveyed behaviour into schedules that a simulation engine can read [@vellei2022; @wilke2011]. Deterministic models apply fixed schedules such as those of the ASHRAE prototype buildings, stochastic models such as Markov chains draw presence and activity from transition probabilities, and data-driven models learn patterns from large samples [@osman2021; @duan2025]. Residential occupancy is harder to model than commercial occupancy, because household routines are not set by opening hours and differ between members of the same household [@hong2017; @mahdavi2021; @xia2023].

National time-use surveys (TUS) are the main empirical source for residential schedules. A respondent records every activity of one day, with its location and the people present, so a diary gives presence, activity and co-presence at a fine time step and can be linked to the respondent's age, employment and household [@osman2021; @vosough2023]; recent models resolve it down to the room [@sood2025]. The modelling lineage starts with Markov-chain models of occupancy and domestic activity built from the UK survey [@richardson2008; @widen2010] and continues with clustering of diaries into household archetypes [@gieter2017], household profiles from national surveys [@jeong2021] and activity-based profiles from the American Time Use Survey (ATUS) [@mitra2020asce; @mitra2020eb]. Vosoughkhosravi et al. [@vosough2023] review how the ATUS has been used to model energy-related occupant–building interactions, and Osman and Ouf [@osman2021] review TUS-based occupancy modelling more broadly. Two limits recur in these reviews. A diary covers a single day, so it says little about seasonal or long-term habits [@mylonas2023; @reis2026], and most models are fitted to one survey year and then used as if behaviour were fixed.

## 1.2 Longitudinal and multi-cycle time-use studies

A smaller group of studies uses several cycles of the same survey to follow change over time. Sekar et al. [@sekar2018] compared ATUS years 2003 to 2012 and found that Americans spent more time at home in 2012 than in 2003, and less time travelling and in non-residential buildings, with consequences for energy use across sectors. Anderson and Torriti [@anderson2018] used four UK time-use surveys from 1974 to 2014 to explain shifts in the timing of residential electricity demand. Yin et al. [@yin2024] fitted logistic regression models of activity probability to five Japanese surveys from 2001 to 2021 and found that time spent on sleep, work and housework fell across demographic groups in 2021, with a lower probability of night-time sleep. Dias dos Santos et al. [@diasdossantos2025] harmonised seven cycles of the Canadian General Social Survey (GSS) time-use module, from 1986 to 2022, into an open data set on active travel. In Canada, Osman et al. [@osman2023] built a stochastic bottom-up load-profile generator for household electricity demand. Other work pools several ATUS years into one sample rather than comparing them [@mitra2021eb; @chen2022].

Table 1 places these studies side by side. They describe change between survey years, but none projects the schedules beyond the last survey, none tests such a projection against a later observation, and only some carry the schedules into a building simulation.

Table 1. Position of this study among time-use studies used for building energy (full references in the reference list).

| Study | Survey and country | Cycles used | Unit modelled | Projection beyond last survey | Projection tested against later data | Building simulation |
|:--|:--|:--|:--|:--|:--|:--|
| Richardson et al. (2008) [@richardson2008] | UK TUS | 1 | Household occupancy (Markov) | No | No | Demand model |
| Widén and Wäckelgård (2010) [@widen2010] | Swedish TUS | 1 | Household activity (Markov) | No | No | Electricity demand |
| Mitra et al. (2020) [@mitra2020eb] | US ATUS | Several years, pooled by type | Individual occupancy profiles | No | No | Comparison with standard schedules |
| Sekar et al. (2018) [@sekar2018] | US ATUS | 10 (2003–2012) | Individual time use | No | No | Energy accounting, no BPS |
| Anderson and Torriti (2018) [@anderson2018] | UK TUS | 4 (1974–2014) | Activity timing | No | No | Electricity demand, no BPS |
| Yin et al. (2024) [@yin2024] | Japanese STULA | 5 (2001–2021) | Activity probability by group | No | No | No |
| Dias dos Santos et al. (2025) [@diasdossantos2025] | Canadian GSS | 7 (1986–2022) | Active-travel episodes | No | No | No |
| This study | Canadian GSS + Census | 4 (2005–2022) | Household presence, activity, metabolic rate | Yes (2025) | Yes (2016→2021 hindcast) | EnergyPlus, six neighbourhoods |

## 1.3 Gap, aim and contribution

Prior TUS-based work either models a single survey cycle, or describes change across cycles without projecting beyond the last survey. This study harmonises four Canadian GSS cycles (2005, 2010, 2015 and 2022) into one household schedule format, links them to four Census cycles, and adds a generative projection of the household population past the last census, tested by a held-out-cycle hindcast. The contribution is the combination of these parts for Canada, across the COVID-19 break, at household level: a longitudinal-plus-projective occupant-behaviour pipeline rather than a new modelling paradigm.

The study has three objectives:

1. build household-level presence, activity and metabolic schedules for 2005, 2010, 2015 and 2022 from the GSS and Census, with the same definitions in every cycle;
2. project the household population to 2025 with a conditional variational autoencoder (C-VAE) and a cluster-based drift model, and test that projection quantitatively against the 2021 Census and simple baselines;
3. show whether the cycle-to-cycle differences in occupancy, and the projection, are large enough to change simulated heating, cooling and peak timing, under a fixed building and a fixed weather file.

The building simulation serves the third objective only. It is a demonstration for one cold-climate city (Montreal, climate zone 6A), not a stock model and not a basis for code factors.

This paper shares its GSS and Census processing with a companion study by the same authors [@iseri2026b], which asks a different question: how household electricity load shapes change at stock scale across Canadian cycles and scenarios to 2030. The present paper is about the occupancy schedules themselves, their change across cycles, and the validity of the projected cohort; the companion paper takes schedules of this kind as its input. An earlier version of the schedule pipeline, covering the 2005, 2015 and 2025 cycles and one single-family house in three climate zones, was presented at eSim 2026 [@iseri2026esim]; the present paper adds the 2010 and 2022 cycles, the hindcast test and the neighbourhood simulations, and its energy results, obtained with a corrected extraction, replace those of the conference paper.

# 2 Data

The study combines two Statistics Canada microdata sources: the Census of Population public-use microdata files (PUMF), which give the structure of households, and the GSS time-use cycles, which give what people do and where they are over a day. Section 2.1 describes the Census files, Section 2.2 the GSS cycles, Section 2.3 how the two were harmonised, and Section 2.4 the regional scope.

## 2.1 Census of Population PUMF (2006, 2011, 2016, 2021)

The hierarchical Census PUMF gives one record per person with household and dwelling identifiers, so households can be rebuilt from their members. Four cycles were used (Table 2). The 2011 cycle is the voluntary National Household Survey (NHS), whose response rate was 68.6 % [@statcan_nhs2011]; the other three cycles come from the mandatory long-form census [@statcan_census2021]. The PUMF identifies province and, for large cities, census metropolitan area (CMA); Montreal is CMA 462 in the 2016 and 2021 files.

## 2.2 GSS time-use cycles (2005, 2010, 2015, 2022)

The GSS time-use cycles (Cycles 19, 24, 29 and 38) ask one person aged 15 or over per household to report a 24-hour diary of episodes, each with an activity code, a location and the people present [@statcan_gss2022]. The 2005 cycle had 19,597 respondents and a response rate of 58.6 % [@statcan_gss2005]; the 2015 cycle had 17,390 usable responses and a response rate of 38.2 % [@statcan_gss2015]. Table 2 gives the respondents and episodes retained after harmonisation. The 2022 cycle was collected after the COVID-19 pandemic and includes more detail on work done at home. Children under 15 have no diary.

Table 2. Sample sizes per cycle (national; Quebec in brackets). Census counts are persons and private households in the PUMF file read by the pipeline; GSS counts are respondents and diary episodes retained after harmonisation; the last two rows are the households in the schedule files and the households simulated.

| | 2005 / 2006 | 2010 / 2011 | 2015 / 2016 | 2022 / 2021 | 2025 |
|:--|--:|--:|--:|--:|--:|
| Census persons | 309,841 (73,860) | 333,008 (79,580) | 343,330 (79,498) | 361,915 (82,992) | — |
| Census households | 124,358 (31,895) | 133,192 (34,458) | 140,720 (35,306) | 149,789 (37,512) | — |
| GSS respondents retained | 13,519 (2,717) | 11,748 (1,798) | 15,240 (3,139) | 10,618 (2,084) | — |
| GSS diary episodes retained | 234,743 (47,266) | 219,584 (30,966) | 241,227 (52,291) | 145,417 (28,906) | — |
| Households in the schedule file | 28,455 (6,914) | 32,440 (7,070) | 31,167 (7,731) | 36,785 (8,844) | 23,882 (6,615) |
| Households simulated per draw and neighbourhood | one per building (24, 48, 56, 8, 12 and 4 buildings in the six NUs); 30 draws | | | | |

## 2.3 Harmonisation

The four Census cycles were brought to one structure in four steps: parsing and cleaning of the raw files; harmonisation of variable names and categories, notably dwelling type (DTYPE); derivation of household variables such as household size (HHSIZE) from the member records; and export with the same variable set in every cycle. The GSS needed more work because its activity coding changed: 2005 and 2010 use ACTCODE with 182 and 264 codes, while 2015 and 2022 use TUI_01 with 64 and 121 codes. All codes were mapped to 14 activity categories (Appendix B, Table B1), and locations and co-presence to 18 presence categories (Table B2). Diary episodes were converted to 288 five-minute states per day. Table 3 defines the variables used for linking and the output variables.

Table 3. Key variables. Linking variables are coded the same way in the Census and GSS after harmonisation; output variables are computed from the five-minute household schedules.

| Variable | Source | Harmonised categories or definition |
|:--|:--|:--|
| AGEGRP | Census, GSS | Age group, 5- to 10-year bands; age code 88 ("not available") removed, see Section 3.5 |
| SEX | Census, GSS | Female, male |
| HHSIZE | Census, GSS | Household size 1, 2, 3, 4, 5 or more |
| DTYPE | Census | Dwelling type: detached, semi-detached, row, duplex, low-rise apartment, high-rise apartment, other, movable (three coarse classes in 2016 and 2021 PUMF, expanded, see Section 3.4) |
| MARSTH | Census, GSS | Legal marital status |
| LFTAG / COW | Census, GSS | Labour force status; class of worker |
| HRSWRK | Census, GSS | Weekly hours worked, grouped |
| NOCS | Census, GSS | Occupation, broad group |
| KOL | Census, GSS | Knowledge of official languages |
| PR | Census, GSS | Province or region (six-value scheme) |
| CMA | Census, GSS | Large census metropolitan area or not (two classes) |
| MODE | Census, GSS | Main mode of commuting |
| Occupancy fraction | Output | Share of the household members with a diary who are at home, per hour (0–1) |
| Occupied hours | Output | Sum over the 24 hours of the mean hourly occupancy fraction (hours per day) |
| Daytime occupancy fraction | Output | Mean occupancy fraction over 09:00–17:00 |
| Metabolic rate | Output | Mean metabolic heat of the members at home, from activity (W per person) |

## 2.4 Regional scope and representativeness

The Census and GSS records come from all of Canada; neither the Census households nor the GSS respondents were restricted to Quebec or Montreal, and no survey weights were used when the schedules were built. The first matching tier (Section 3.4) requires a Census person and a GSS respondent to share the same province and the same CMA class, so a Quebec household is matched to Quebec diaries whenever that tier succeeds; later tiers relax this. Quebec accounts for about a quarter of the households in each Census cycle and 15 to 21 % of the retained GSS respondents (Table 2). The Quebec GSS samples are small (1,798 to 3,139 respondents per cycle), and CMA is not coded at the same detail in every PUMF cycle, which is why the national files were used.

To test whether this choice matters for a Montreal simulation, the occupancy metrics were computed for Canada and for the Quebec subset of each schedule file (Table 4). The Quebec households are at home slightly longer in most cycles, but the differences are small: at most 0.3 h per weekday and 0.02 in the weekday daytime fraction, and at most 0.9 h and 0.04 on weekends (2022). These are smaller than the difference between 2022 and the other cycles (1.5 to 2.3 h per weekday), so the national schedules were kept and no scenario was re-run with the Quebec subset. Because no weights were applied, the schedules describe the survey samples as matched, not the Canadian population, and the paper does not claim national representativeness.

Table 4. Occupied hours per day and daytime (09:00–17:00) occupancy fraction for Canada and for the Quebec subset, per cycle and day type. Differences are Quebec minus Canada with 95 % bootstrap intervals (1,000 resamples of households).

[[TABLE 4 = IMP/impl/wp13/out/table_quebec.md]]

# 3 Methods

The pipeline has two branches that share their definitions (Figure 1). For 2005, 2010, 2015 and 2022, each Census cycle is paired with the nearest GSS cycle and real diaries are matched to real Census persons (Section 3.5). For 2025, a generative model projects the Census population forward, and the synthetic persons are then matched to diaries in the same way (Sections 3.1 to 3.4). Section 3.6 describes the building simulations.

![](../figures/docx_media/word/media/image1.png)

Figure 1. Flow chart of the pipeline, from Census and GSS microdata to occupancy schedules and building simulation.

## 3.1 Linking Census and GSS records

Census records are one row per person, while the GSS comes as a person file (one row per respondent) and an episode file (many rows per respondent). The two GSS files were joined on the respondent identifier (PUMFID), which attaches the respondent's attributes to every episode (Figure 2); the episode files were read in blocks of 100,000 rows. Variable names were then mapped to the Census names (for example PRV to PR and HSDSIZEC to HHSIZE).

![](../figures/docx_media/word/media/image3.png)

Figure 2. Alignment of Census and GSS categorical data in five steps.

## 3.2 Generative model of the household population

A census is taken every five years and the latest cycle used here is 2021, so a 2025 population has to be projected. Census cycles are cross-sections of different households, so a model cannot follow the same household through time. The approach taken here models the population distribution instead. A multi-head C-VAE (Figure 3) compresses each person's demographic attributes into a latent vector, conditioned on the attributes of the dwelling (dwelling type, tenure, number of rooms and bedrooms, condition and value), and a decoder reconstructs the demographic attributes from the latent vector and the dwelling attributes. The encoder and decoder were trained on the pooled 2006, 2011, 2016 and 2021 Census files for 100 epochs with the Adam optimiser and a 128-dimensional latent space, with softmax heads for categorical variables and sigmoid heads for scaled continuous variables. On the training data, the decoder recovered the original category in more than 80 % of records for the categorical variables and reproduced more than 92 % of the variance of the continuous variables (age, household size and income).

![](../figures/docx_media/word/media/image4.png)

Figure 3. Structure of the multi-head C-VAE.

## 3.3 Cluster-based drift to 2025 and its hindcast test

The latent vectors of each census year are the starting point of the projection. A single mean shift of the whole population would move every person the same way and pull the projected population towards its average. The cluster-based vector momentum (CBVM) model instead groups the 2006 latent vectors into K = 8 clusters with k-means, assigns the vectors of every later year to those clusters, and tracks each cluster's mean from cycle to cycle. The velocity of cluster k is the change of its mean per year over each census interval; the last interval gets a weight of 0.5 and the earlier ones share the remaining 0.5. A person drawn from the last census year is moved by the velocity of its cluster times the projection horizon, multiplied by a decay of 0.95 per five years to keep long projections from diverging. Gaussian noise equal to 15 % of each latent dimension's spread is then added, and the decoder produces the projected person, conditioned on dwelling attributes resampled from the last census year. For 2025, the source year is 2021 and the horizon four years. The dwelling stock is therefore held at its 2021 composition, so the 2025 cohort reflects demographic drift only.

**Hindcast.** The submitted version of this paper supported the projection with a qualitative comparison only. The projection is now tested quantitatively. The C-VAE was retrained on the 2006, 2011 and 2016 files only, CBVM was fitted to those three years, and the 2016 population was projected five years ahead to 2021, conditioned on the 2016 dwelling stock (the same rule as the 2025 projection). The projected 2021 population was compared with the held-out 2021 Census on every generated demographic variable, using the total-variation distance for categorical variables and the Wasserstein-1 distance on range-scaled values for continuous ones. Three baselines were scored the same way [@borysov2019; @johnsen2021]: B0, carry-forward (the 2016 population used as the 2021 prediction); B1, linear extrapolation of each variable's 2011–2016 change in category shares (or percentiles); and B2, a population-mean drift (the same model with a single cluster). The pass rule was written before the hindcast was run: CBVM must have a smaller distance than B0 on more than half of the variables, averaged over five random seeds; otherwise the claim that CBVM projects better than carrying the last census forward is dropped. The sensitivity of the hindcast and of the 2025 cohort to K (4, 8, 12), the decay factor (0.90, 0.95, 1.00) and the latent size (64, 128, 256) was also computed. The hindcast is unweighted, like the rest of the pipeline.

## 3.4 From synthetic persons to household schedules

The projected persons were assembled into households by a priority-based algorithm that enforces household size, spousal age differences and parent–child age relationships. Each person was then matched to a GSS diary, separately for a weekday and a weekend diary, through four tiers (Figure 4). In the 2025 branch, Tier 1 requires an exact match on ten person variables (household size, weekly hours worked, age group, marital status, sex, knowledge of official languages, occupation, province, class of worker and commuting mode) and five dwelling variables (dwelling type, bedrooms, condominium status, rooms and condition); Tier 2 keeps household size, hours worked, age group, sex, class of worker and the five dwelling variables; Tier 3 keeps household size, hours worked and age group; and Tier 4 matches on household size only. The historical branches (Section 3.5) use the same cascade with the variables available in each cycle: Tier 1 uses all harmonised linking variables, Tier 2 household size, age group, sex, marital status, labour force status and province, Tier 3 household size, age group and sex, and Tier 4 household size. Table 5 gives the share of persons matched at each tier, read from the matcher's output. In 2025, 97 % of the weekday matches and 94 % of the weekend matches were made at Tier 1 or 2; in the historical cycles, which have fewer linking variables, most matches were made at Tier 2 or 3, and Tier 4 was never above 2 % on weekdays or 5.3 % on weekends.

Table 5. Share of persons (%) matched at each tier, weekday and weekend diaries.

[[TABLE 5 = IMP/impl/wp13/out/table_tiers.md]]

![](../figures/docx_media/word/media/image6.png)

Figure 4. Behavioural profile matching workflow.

The C-VAE outputs three coarse dwelling classes. Two random forest classifiers trained on the 2006 and 2011 Census, where the eight-class dwelling type is available, split them into the eight classes by probabilistic sampling (Appendix A, Figure A2).

The five-minute diary states of all members with a diary were combined into a household schedule. The occupancy fraction at each time step is the share of these members who are at home; children under 15 have no diary, so they do not enter the fraction, and the denominator is the number of members who have a schedule. Activities were mapped to metabolic rates (sleep 70 W, passive leisure 85 W, work 125 W, active leisure 245 W per person) and the five-minute values were averaged to hourly values for EnergyPlus.

## 3.5 Historical cycles

The four historical datasets pair each Census cycle with the nearest GSS cycle (06CEN05GSS, 11CEN10GSS, 16CEN15GSS and 21CEN22GSS) and use real respondents only: the same harmonisation, the same tiered matching, the same household aggregation and the same hourly conversion as the 2025 branch, without the generative step (Table 6). The number of harmonised linking variables falls from 11 to 8 in the newer cycles because the public files dropped variables. The 2016 PUMF gives only three dwelling classes, which were expanded with the classifiers of Section 3.4; the 2021 PUMF keeps the three classes.

Table 6. The four historical pipelines.

| Feature | 06CEN05GSS | 11CEN10GSS | 16CEN15GSS | 21CEN22GSS |
|:--|:--:|:--:|:--:|:--:|
| Census year | 2006 | 2011 | 2016 | 2021 |
| GSS year (cycle) | 2005 (19) | 2010 (24) | 2015 (29) | 2022 (38) |
| Harmonised linking variables | 11 | 10 | 9 | 8 |
| Census households sampled | 25 % | 25 % | 25 % | 25 % |
| Dwelling type detail | 8 classes | 8 classes | 3 classes expanded to 8 | 3 classes |

Three data limitations are handled explicitly. (i) Census persons whose age is coded 88 ("not available") were removed before matching; this concerns 2.8 % of the sampled 2010 persons and 5.4 % of the sampled 2022 persons and left 39 and 119 households with no member, which were dropped; 2005 and 2015 are unaffected. (ii) In the pooled schedule files, 70,281 households carry more than one dwelling-type label across their records; they were kept. (iii) The three GSS-based pools for 2005, 2010 and 2015 draw on one household population and differ in their diaries, so these cycles differ in behaviour, not in household composition.

## 3.6 Building simulations

**Buildings and neighbourhoods.** Six neighbourhood units (NUs) in Montreal were simulated with EnergyPlus 24.2 (Table 7) [@hachem2025; @hachem2023]. All buildings in the six NUs share one high-performance envelope: exterior walls of stucco, 200 mm concrete and 330 mm insulation (U ≈ 0.14 W/m²K), roofs with 690 mm insulation over metal decking (U ≈ 0.07 W/m²K), and low-e double glazing. Every zone is served by an ideal-loads air system, so the heating and cooling reported here are the energy delivered to the zones, not the consumption of a specific plant. Envelope and HVAC were the same in every scenario. The weather file is the TMYx file for Montreal McGill (WMO 716120), whose typical months are drawn from 1994 to 2023.

Table 7. Neighbourhood units.

| NU | Setting | Buildings | Description |
|:--|:--|:--|:--|
| RC-R | Outer suburb | 24 detached houses | Low density, car dependent |
| RC-D | Outer suburb | 48 detached houses | Subdivision houses |
| RC-T | Outer suburb | 56 attached (row) houses | Medium-density blocks |
| RC-MR2 | Inner suburb | 8 mid-rise apartment buildings | Clusters around shared courtyards |
| RC-MR3 | Urban mid-zone | 12 mid-rise apartment buildings | Dense, transit-oriented blocks |
| RC-HR2 | Urban core | 4 high-rise apartment buildings | Towers near transit nodes |

**Default scenario.** The reference ("Default") scenario uses the schedules of the U.S. Department of Energy MidriseApartment prototype building [@doe_refbldg] for occupancy, lighting, equipment, domestic hot water (DHW) and activity level, extracted with the OpenStudio Standards Gem [@nrel_osstd], in all six NUs. One schedule set is used for every building type so that every scenario is compared with the same reference; for the three house NUs this reference is an apartment schedule, not the IECC house schedule, and the house results should be read as differences from that common reference.

**Schedule integration.** Each building receives the hourly occupancy fraction O_t of one household. Occupant counts follow the household size. Equipment and DHW schedules are derived from the Default schedule by a presence filter:

$$
S_t = \begin{cases} O_t\,S_t^{\mathrm{def}} + (1 - O_t)\,S^{\mathrm{base}}, & O_t > \varepsilon \\ S^{\mathrm{base}}, & O_t \le \varepsilon \end{cases}
$$

where S_t^def is the Default schedule value at hour t, S^base is the lowest Default value during the hours when the household is away (or during 09:00–17:00 if it is never away), and ε = 10⁻³. For DHW the first branch is used at every hour, so that one member at home produces a proportional share of the demand. Lighting follows occupancy with a monthly daylight adjustment (Figures 5 and 6).

![](../figures/docx_media/word/media/image9.png)

Figure 5. Schedule integration: Default scenario and occupancy-integrated scenarios.

![](../figures/docx_media/word/media/image10.png)

Figure 6. Presence filter applied to a household load profile.

**Draws and stopping rule.** In each draw, every building receives one household from the schedule file of the scenario year, drawn at random with a fixed seed from the households of the same dwelling type; the household size of each building is drawn once per draw with probabilities proportional to the pool, and every year then draws a household of that type and size. Each NU and year was simulated in blocks of five draws. The reported quantity is the mean annual heating and cooling energy per unit floor area over the draws, with its 95 % confidence interval. The stopping rule, fixed before any result was read, was to stop when the half-width of every interval was at most 1 % of its mean, or at 30 draws. The Default scenario is deterministic and was run once per NU. A year-to-year difference is called a difference only when its own 95 % interval (Welch) excludes zero; because the years share the household size drawn for each building, this test is conservative.

# 4 Results

## 4.1 Occupancy patterns, 2005–2025

All numbers in this section are computed from the household schedule files used in the simulations (Table 2), with the definitions of Table 3. They replace the numbers of the submitted version, which came from earlier files in which weekday and weekend were swapped for 2005 and 2015 and the occupancy fraction was defined differently.

### 4.1.1 Presence

Figure 7 and Table 8 show the hourly presence profiles and their summary metrics. On weekdays, households are at home 15.6 to 16.2 h per day in 2005, 2010 and 2015 and 17.9 h in 2022; on weekends, 17.4 to 17.6 h before 2022 and 18.6 h in 2022. The weekday daytime occupancy fraction (09:00–17:00) is 0.36 to 0.40 in the three pre-pandemic cycles and 0.52 in 2022. Presence was thus nearly flat from 2005 to 2015 and rose after the COVID-19 pandemic, mainly during working hours on weekdays, which narrowed the weekday–weekend gap from 1.4 to 1.8 h before 2022 to 0.6 h in 2022. The 2010 cycle is slightly lower than 2005 and 2015 on weekdays (by about 0.5 h); the cause of this difference was not identified. The 2025 cohort, whose persons are matched to 2022 diaries, has 16.5 h on weekdays and a daytime fraction of 0.40, close to the pre-pandemic cycles. Because the diaries are the same as in 2022, this difference comes from the projected population and from how its persons were matched (Section 3.4), not from a change in behaviour.

![](../figures/Fig7_presence_R1.png)

Figure 7. Hourly presence profiles (top; mean with ±1 standard deviation across households), occupied hours and daytime occupancy fraction (middle), and summary metrics against the Default (bottom), for each cycle.

Table 8. Occupancy metrics per cycle (Canada) and for the Default schedule. Occupied hours are the sum of the 24 hourly mean occupancy fractions.

[[TABLE 8 = IMP/impl/wp13/out/table_occupancy.md]]

### 4.1.2 Metabolic rate

Figure 8 shows the mean metabolic rate per person at home. It falls to about 70 W at night, when most members sleep, and rises to 110–133 W during the day, highest in 2022. The Default applies a constant 95 W, so it overstates night-time gains by about a third and understates daytime gains, while its mean is close to the survey mean over occupied hours (93 to 101 W). The Default error in metabolic heat is therefore mainly one of timing, not of magnitude.

![](../figures/Fig8_metabolic_R1.png)

Figure 8. Mean hourly metabolic rate per person at home, by cycle, and the constant Default value.

### 4.1.3 Default and survey-based schedules

Figure 9 compares the Default occupancy schedule with the survey-based profiles. Over a whole day the two are close: the Default mean occupancy is 0.68 on every day, against 0.65 to 0.75 on weekdays and 0.73 to 0.77 on weekends in the survey-based files. Their shape differs. The Default keeps every occupant at home until 07:00, drops to 0.25 between 09:00 and 16:00 and returns to 0.87–1.0 from 18:00, whereas the survey-based profiles fall gradually from 06:00, stay between 0.32 and 0.59 during the working day and rise gradually from 15:00. The Default daytime fraction (0.26) is thus below every cycle on weekdays (0.36 to 0.52) and far below them on weekends (0.54 to 0.58), and the Default has no weekday–weekend difference at all.

![](../figures/Fig9_default_vs_cycles_R1.png)

Figure 9. Hourly occupancy fraction of the Default schedule and of each cycle: (a) weekday, (b) weekend.

### 4.1.4 Household size

With the occupancy fraction defined as the share of members at home, household size has little effect on presence: in 2025, weekday occupied hours range from 16.1 h (one person) to 17.0 h (three persons), and in the other cycles the range across sizes is at most 1.8 h. One-person households have the highest weekday daytime fraction in 2005, 2010 and 2015 (0.43 to 0.47, against 0.29 to 0.40 for larger households), but not in 2022 or 2025. The strong decline with household size reported in the submitted version (from 18.2 h to 5.2 h) came from the earlier files, in which the occupancy fraction was divided by the full household size, including members without a diary; it does not hold under the definition used here.

## 4.2 Hindcast of the projection

Table 9 gives the distance of each method to the held-out 2021 Census. CBVM was closer to 2021 than carry-forward (B0) on 7 of the 24 variables (sex, marital status, official languages, class of worker, occupation, place of work status and commuting mode) and farther on the other 17. The pass rule set before the test was therefore not met, and the claim that CBVM projects better than carrying the last census forward is dropped. The differences between the methods were small: averaged over the 24 variables, the distance was 0.037 for B0, 0.041 for B1, 0.039 for B2 and 0.040 for CBVM. CBVM was also close to the single-cluster drift B2 and was closer to 2021 than B2 on only 5 of the 24 variables, so grouping the population into clusters did not improve the projection of these distributions. The largest distances, about 0.17 for every method, were for hours worked, place of work status and commuting mode; the 2021 Census was taken in May 2021, during the COVID-19 pandemic, and none of the methods reproduced the change in work arrangements it recorded. The verdict did not depend on the settings: every combination of K (4, 8, 12) and decay (0.90, 0.95, 1.00) left CBVM closer than B0 on 7 of the 24 variables, and latent sizes of 64, 128 and 256 gave 5 to 7 (Appendix A, Table A1 and Figure A1). The 2025 cohort itself was stable across settings: changing K, the decay or the seed moved it by at most 0.0044 on any variable (Table A2).

Table 9. Distance of each projection method to the held-out 2021 Census, per variable: total-variation distance (TVD) for categorical variables and Wasserstein-1 distance on range-scaled values (W1) for continuous ones; lower is closer. B0 and B1 are deterministic; B2 and CBVM are means over five seeds, with the CBVM range in brackets. Methods as defined in Section 3.3.

[[TABLE 9 = IMP/impl/wp4/out/table_hindcast.md]]

## 4.3 Energy consequences of the occupancy schedules (demonstration)

The simulations ask one question: are the occupancy differences between cycles, and the projected cohort, large enough to change simulated energy use in fixed buildings? Annual end-use energy was read from the annual summary report of each EnergyPlus run and divided by the net conditioned floor area; interior equipment and lighting energy agree with the hourly meters to within 0.02 %. The stopping rule reached its 30-draw limit with 31 of the 60 heating and cooling intervals within ±1 % of their means; the other 29 reached half-widths of 1.0 to 4.7 % of their means (median of all 60: 0.9 %). The target was therefore not met in every cell, and all results below are reported with the intervals actually achieved.

Figure 10 and Table 10 give the deviation of each scenario from the Default. In the three house neighbourhoods, the survey-based schedules raise heating by 6.2 to 16.4 % and lower cooling by 1.0 to 9.0 %. In the three apartment neighbourhoods the same schedules raise heating by only 0.3 to 1.5 % and lower cooling by 1.1 to 6.5 %. The heating response is small in the apartment buildings because their heating intensity is much higher (Default 78 to 100 kWh/m², against 6 to 13 kWh/m² in the house NUs), so the same change in internal gains is a small share of the heat balance. All 30 heating deviations and 29 of the 30 cooling deviations have intervals that exclude zero; the exception is the 2022 cooling deviation of RC-R. Equipment (−1.9 to −5.8 %), DHW (0 to −14.5 %) and lighting (−8.0 to −18.9 %) are also lower than in the Default, because the Default schedule assumes more hours at home.

![](../figures/Fig15_annual_deviation_R1.png)

Figure 10. Deviation of annual end-use energy from the Default schedules, by neighbourhood unit and scenario year: (a) heating, (b) cooling, (c) electric equipment, (d) domestic hot water. Bars are means over 30 draws; error bars are 95 % confidence intervals. RC-R, RC-D and RC-T are house neighbourhoods; RC-MR2, RC-MR3 and RC-HR2 are apartment neighbourhoods.

Table 10. Deviation of annual heating and cooling from the Default (%), mean over 30 draws with 95 % confidence interval in brackets. Default values in kWh/m² of net conditioned floor area.

[[TABLE 10 = IMP/impl/wp12_stage5/out/table_deviation.md]]

The differences between cycles are smaller than the difference from the Default. The 2022 schedules stand apart: in the house NUs they give the smallest heating increase (+6.2 to +7.0 %) and the smallest cooling decrease (−1.0 to −3.9 %), and most year-to-year differences whose interval excludes zero involve 2022 (heating 18 of 22 such differences, cooling 20 of 24, out of 60 pairs each). The 2005, 2010, 2015 and 2025 schedules give deviations that overlap in most NUs, so the projected 2025 cohort behaves like the pre-pandemic cycles rather than like 2022. The survey-based schedules lower equipment, lighting and hot-water use and the night-time metabolic gains relative to the Default, which lowers internal gains and so raises heating and lowers cooling; the 2022 schedules, with the most daytime presence (Section 4.1.1), lower equipment use by only 1.9 to 2.8 % and lighting by 8.3 to 12.6 %, against 3.0 to 5.8 % and 8.0 to 18.9 % in the other years, and therefore depart least from the Default.

Peak cooling demand follows the same pattern (Table 11). In the house NUs the survey-based schedules lower the annual peak by 3.8 to 10.2 %, least in 2022; in the apartment NUs the change is between −1.9 and +0.3 %. The peak falls on the same day and at the same quarter-hour as in the Default in most draws (26 July at 19:30–19:45 in the house NUs, 10 August at 13:15 in the mid-rise NUs and 14 July at 19:00 in the high-rise NU), so in this weather file the occupancy schedules change the size of the cooling peak but not its timing.

Table 11. Deviation of the annual peak cooling demand from the Default (%), mean over 30 draws with 95 % confidence interval, and the time of the Default peak.

[[TABLE 11 = IMP/impl/wp12_stage5/out/table_peak.md]]

# 5 Discussion

## 5.1 Comparison with other longitudinal time-use findings

Table 12 compares the patterns found here with those reported for the United States and Japan. The comparison is qualitative: the surveys differ in design, population and definitions, and only presence and activity summaries are compared.

Table 12. Qualitative comparison with longitudinal time-use findings in other countries.

| Pattern | This study (Canada, 2005–2022) | Other countries | Agree or differ |
|:--|:--|:--|:--|
| Time at home over the pre-pandemic years | Nearly flat: 15.6 to 16.2 h per weekday in 2005, 2010 and 2015 | United States, 2003 to 2012: more time at home [@sekar2018] | Differ |
| Change after the COVID-19 pandemic | Weekday presence +1.5 to 2.3 h in 2022, mostly during working hours | Japan, 2021: less time on work, sleep and housework, lower night-time sleep probability [@yin2024] | Both show a post-pandemic change in daily structure; the measures differ |
| Weekday–weekend difference | 1.4 to 1.8 h before 2022, 0.6 h in 2022 | United States: weekend presence higher than weekday presence [@mitra2020eb] | Agree before 2022; the gap narrowed in 2022 |
| Household size | Little effect on the share of members at home | Not compared | — |
| Timing of internal gains | Metabolic rate about 70 W at night and 110–133 W by day, against a constant 95 W default | — | — |

Two patterns stand out as visible only across several Canadian cycles. First, presence did not rise from 2005 to 2015, unlike the rise in time at home reported for the United States over a similar period [@sekar2018]; a single-cycle model fitted to any of the three pre-pandemic cycles would therefore describe the others well. Second, the 2022 cycle departs from all earlier ones, with more presence during weekday working hours and a smaller weekday–weekend difference, which matches the post-pandemic change in daily structure reported for Japan [@yin2024]. A schedule set built from a pre-2020 survey would miss this shift, while the projected 2025 cohort, whose population differs from the 2022 respondents, returns towards the pre-pandemic level. The difference between the Default and all survey cycles is one of timing: over a whole day the Default mean occupancy and mean metabolic rate are close to the survey values, but the Default places presence and metabolic heat at the wrong hours and ignores the weekday–weekend difference.

## 5.2 What the projection and the simulations add

The hindcast does not support the claim that the cluster-based projection forecasts the population better than carrying the last census forward: over five years and averaged over the variables, the 2016 population was closer to the 2021 Census than any of the projections tested, and the clusters added nothing measurable to a single mean drift. Over the four years from 2021 to 2025 the projected cohort stays close to the 2021 population, and it moved by less than 0.005 on any variable across the settings tested. The 2025 cohort is therefore best read as the 2021 population with a small, model-based demographic drift, matched to the 2022 diaries; its value for simulation lies in providing complete, dwelling-conditioned households for a year without a census, not in anticipating demographic change. A projection that should beat carry-forward would need information beyond past census trends, such as population projections or post-2021 survey data.

The simulations show that, in this climate and in these buildings, replacing the Default schedule with survey-based household schedules raises heating by 6 to 16 % and lowers cooling by 1 to 9 % in houses, changes both by less than 7 % in apartment buildings, and lowers the peak cooling demand of houses by 4 to 10 % without moving its timing. Among the cycles, only the post-pandemic 2022 schedules are clearly distinguishable from the others. The differences are indicative of the direction and size of the occupancy effect for Montreal and for these archetypes; they are not proposed as correction factors for building codes, and the study covers one climate zone only. The size of the effect also depends on the reference: for the house NUs the Default is an apartment schedule (Section 3.6).

## 5.3 Limitations

The study has the following limitations. The schedules are unweighted and national; a Quebec comparison is given (Section 2.4) but no weighted estimates. Only Montreal (climate zone 6A) and one weather file were simulated, with fixed envelopes and ideal-loads systems. All buildings share one high-performance envelope, so the house heating intensities are low (6 to 13 kWh/m² under the Default) and internal gains weigh more in their heat balance than they would in older, less insulated housing; the relative effects reported here may therefore be larger than for the existing Canadian stock. The 2025 cohort holds the dwelling stock at its 2021 composition and extrapolates demographic change from 2006–2021; it cannot anticipate changes after 2021 that the census did not yet show. The dwelling-type classifiers were trained on the 2006 and 2011 Census. Census persons whose age was not available were removed before matching (2.8 % of the sampled 2010 persons and 5.4 % of the sampled 2022 persons), which left 39 and 119 households with no member; 2005 and 2015 are unaffected. In the pooled files, 70,281 households carry more than one dwelling-type label and were kept. Children under 15 have no diary and are not counted in the occupancy fraction. Each building receives the schedule of one household, so the apartment buildings do not represent a mix of households. The 30-draw limit left 29 of 60 heating and cooling intervals wider than the 1 % target (up to 4.7 % of the mean). The reason for the low 2010 occupancy in the submitted version, a link to the 2011 NHS weighting, was wrong on chronology (the 2010 GSS was collected before the NHS) and is withdrawn; in the rebuilt files 2010 is about 0.5 h per weekday below 2005 and 2015, and the cause of this smaller difference was not identified.

# 6 Conclusion

This study harmonised four Canadian time-use cycles, from 2005 to 2022, into household presence, activity and metabolic schedules with the same definitions in every cycle, and projected the household population to 2025. Presence at home was nearly constant from 2005 to 2015 and rose in 2022, mostly during weekday working hours, a change that a schedule built from any single pre-pandemic survey would miss. A hindcast against the held-out 2021 Census found that the projection was not closer to the census than carrying the previous cycle forward, so the 2025 cohort is a scenario close to the 2021 population rather than a forecast of demographic change. In fixed Montreal buildings with one high-performance envelope, the survey-based schedules raised heating by 6 to 16 % and lowered cooling by 1 to 9 % in houses relative to a standard apartment schedule, changed both by less than 7 % in apartment buildings, and left the timing of the cooling peak unchanged. These effects come from the timing of presence and internal gains rather than from their daily totals, which supports the use of time-resolved, survey-based household schedules in residential simulation, updated as new survey cycles appear.

# CRediT authorship contribution statement

**Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing – original draft. **Caroline Hachem-Vermette:** Conceptualization, Supervision, Funding acquisition, Resources, Writing – review and editing.

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Funding

This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC) through a Discovery Grant, and by the Volt-Age Seed Fund, Concordia University. The funders had no role in the study design, in the collection, analysis and interpretation of data, in the writing of the article, or in the decision to submit it for publication.

# Data availability

This study uses the Statistics Canada General Social Survey time-use public-use microdata files (2005, 2010, 2015 and 2022 cycles) and the Census of Population public-use microdata files (2006, 2011, 2016 and 2021). These files are available from Statistics Canada under its licence terms, which do not allow the authors to redistribute them. The derived schedules, building model files and scripts that support the findings of this study are available from the corresponding author upon reasonable request.

# Declaration of generative AI in the writing process

During the preparation of this work the authors used Claude Opus 5.5 (Anthropic) to assist with writing analysis code and to improve the grammar and readability of the text, and Gemini 3 Pro Deep Research (Google) to prepare literature research reports. Every source named in the research reports was checked by the authors against the publisher record before use. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.

# References

[[REFERENCES — generated by the build script from R1_references.md, numbered in order of first citation]]

# Appendices

## Appendix A. Projection

Figure A1 shows the hindcast distances of Table 9 per variable and method; Table A1 gives the hindcast for each setting of K, decay and latent size, and Table A2 the change of the 2025 cohort when K, the decay or the seed is changed.

![](../figures/FigA1_hindcast_R1.png)

Figure A1. Distance of each projection method to the held-out 2021 Census, per variable (log scale). CBVM: mean over five seeds with the minimum–maximum range; B2: mean over five seeds.

Table A1. Hindcast sensitivity: mean distance to the 2021 Census over the 24 variables, and number of variables on which CBVM is closer than carry-forward (B0), per setting.

[[TABLE A1 = IMP/impl/wp4/out/table_sensitivity.md]]

Table A2. Sensitivity of the 2025 cohort: distance of each variant from the reference cohort (K = 8, decay 0.95, latent 128, seed 1), mean over the 24 variables and largest single variable. A repeat of the reference gave a distance of zero.

[[TABLE A2 = IMP/impl/wp4/out/table_sens2025.md]]

![](../figures/docx_media/word/media/image23.png)

Figure A2. Dwelling type distribution: historical Census cycles and the refined 2025 cohort.

## Appendix B. Harmonisation tables

Table B1. Standardised activity categories for the four GSS cycles.

| # | Category | Description |
|:--:|:--|:--|
| 1 | Work and related | Paid or unpaid work, job searching, overtime, and work-related breaks or idle time (excluding travel) |
| 2 | Household work and maintenance | Cooking, cleaning, laundry, repairs, gardening, pet and plant care, household finances and organisation |
| 3 | Caregiving and help | Caring for children, adults or non-household members, including physical, emotional or medical help |
| 4 | Purchasing goods and services | Shopping, errands, and personal, financial, government, medical or professional services |
| 5 | Sleep, naps and resting | Night sleep, naps, or lying down to rest |
| 6 | Eating and drinking | All eating and drinking, at home or away |
| 7 | Personal care | Grooming, hygiene, personal medical care and private activities |
| 8 | Education | Attending classes, studying, homework, school or training events |
| 9 | Socialising | Visiting, parties, weddings, bars, clubs or other direct social contact |
| 10 | Passive leisure | Relaxing, reading, watching television, gaming, listening to music, meditation or private prayer |
| 11 | Active leisure | Sports, exercise, hobbies, outdoor recreation, arts or dancing |
| 12 | Community and volunteer | Civic participation, religious services, volunteering and organised community activities |
| 13 | Travel | All travel between locations, for any purpose |
| 14 | Miscellaneous or idle | Waiting, unspecified or unclassifiable time |

Table B2. Harmonised location and presence categories.

| Code | Description | Original context (merged) | Code | Description | Original context (merged) |
|:--:|:--|:--|:--:|:--|:--|
| 1 | Respondent's home | Home, property | 10 | Car (driver) | Travel, driver (car, truck, van) |
| 2 | Work or school | Place of work, school, business trip | 11 | Car (passenger) | Travel, passenger (car, truck, van) |
| 3 | Someone else's home | Friend's or relative's home or property | 12 | Walk | Travel, walking |
| 4 | Outdoors | Outdoors away from home, neighbourhood | 13 | Public transit | Bus, subway, metro, light rail |
| 5 | Grocery or stores | Grocery store, other store, mall | 14 | Airplane | Travel, airplane |
| 6 | Library or museum | Library, museum, theatre | 15 | Bicycle | Travel, bicycle |
| 7 | Restaurant or bar | Restaurant, bar, club | 16 | Taxi or limousine | Travel, taxi, limousine service |
| 8 | Place of worship | Religious institution | 17 | Other transit | Boat, ferry, motorcycle, other |
| 9 | Other place | Medical, dental, elsewhere | 18 | Valid skip | Data skipped by design (for example, a child) |

## Appendix C. Supplementary energy results

Table C1. Annual end-use energy per unit of net conditioned floor area (kWh/m²): Default value and mean ± 95 % confidence half-width over 30 draws, per neighbourhood unit and scenario year.

[[TABLE C1 = IMP/impl/wp12_stage5/out/table_absolute_appendix.md]]
