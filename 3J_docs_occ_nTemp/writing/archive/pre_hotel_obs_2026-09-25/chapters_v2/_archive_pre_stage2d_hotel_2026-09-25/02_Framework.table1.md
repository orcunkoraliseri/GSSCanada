# 2. Proposed modelling and simulation framework

The framework turns time-use diaries and tourism statistics into four occupancy schedules and runs them in two mixed-use tower models (Figure 1). Survey diaries feed a generative occupancy model for the residential, office and retail uses. A separate time-series model supplies hotel presence. The four schedules are routed into the tower spaces, and the towers are simulated for four survey years, nine scenarios to 2030 and one code-schedule control.

**Figure 1.** *(insert `Figure_01_pipeline_4split.png` here)* Framework overview.

## 2.1 Data and the four occupancy channels

Three of the four channels come from the Statistics Canada General Social Survey (GSS) time-use program (Statistics Canada, 2022). The study uses the 2005, 2010, 2015 and 2022 cycles, the same four used in the authors' residential work. Each diary is placed on a common grid of 48 half-hour slots per day. Residential presence is read as time at home, and office presence as time at work.

The retail channel is new in this study. It marks a respondent as present in a store when the diary location is a store, or when the activity is purchasing goods and services at one of two away-from-home location codes (Appendix B, Eq. B.1). Purchases made from home are excluded, since they are online shopping rather than store presence. The location codes changed between cycles. In 2015 and 2022, grocery and general-merchandise stores share one code and cannot be separated. The retail channel therefore uses one retail space type and covers customers only. Store staff are recorded as at work, so their presence stays on the code schedule.

Residential and office diaries are linked to the 2021 Census public-use microdata file (Statistics Canada, 2021). Households are matched on dwelling type, tenure and size. Workers are matched on occupation and industry. Retail and hotel use no individual linkage.

Hotel guests are outside the GSS sampling frame, which interviews residents at their home address. The hotel channel is therefore built from monthly provincial hotel-occupancy statistics. The Quebec series comes from the Institut de la statistique du Québec (2026), and the Alberta series from the Government of Alberta's tourism market monitor (Government of Alberta, 2022). The Alberta series covers 2011 to 2022 and the Quebec series 2019 to 2022. Table 1 lists the role of each data source.

**Table 1.** Data sources and the four occupancy channels.

| Channel | Source | How presence is derived | How it enters the model | 2030 scenario lever |
|---|---|---|---|---|
| Residential | GSS time-use diaries; 2021 Census households | Residential decoder head; household matched on dwelling type, tenure and size | Replaces the apartment occupant schedule; count set by household size | None of its own (coupled to the office lever) |
| Office | GSS time-use diaries; 2021 Census workers | Office decoder head; worker matched on occupation and industry | Scales the NECB office occupant density by the modelled presence fraction | Work-from-home band: conservative, hybrid (central), fully hybrid |
| Retail | GSS time-use diaries (new channel) | Retail decoder head; location and activity rule (Eq. B.1) | Scales the retail occupant schedule by 0.95 times a normalised customer-hours shape | In-store share: 0.90, 0.97 (central), 1.05; Quebec Sunday hours |
| Hotel | Monthly hotel-occupancy series, Quebec and Alberta | Seasonal time-series model per province with a pandemic indicator | Scales the NECB guest-room schedule by a monthly multiplier | Hotel band: 0.92, 1.00 (central), 1.05 |

## 2.2 Generative occupancy model and hotel model

The residential, office and retail channels come from one conditional Transformer (Vaswani et al., 2017) with a shared encoder and three decoder heads, one per channel (Figure 2). The encoder reads the respondent's demographic and calendar attributes, including the survey cycle year as a continuous value. That choice lets the model generate a 2030 year without a new category. The model was grown from an earlier two-channel version with residential and office heads, and the retail head is the one addition. A regression check limits how far the two reused heads may drift from that earlier version, measured as a Jensen-Shannon divergence.

The three heads are trained with fixed loss weights of 1.0, 0.5 and 0.3 for residential, office and retail. A gradient-projection method removes the part of each head's gradient that conflicts with another head [REF NEEDED: PCGrad, gradient surgery for multi-task learning]. Retail presence is rare, at about 2 % of slots. Its loss therefore carries a positive-class weight of 49, and the matching logit shift is removed at inference (Appendix B, Eqs. B.2 and B.3). Training runs five epochs on the heads alone, then 15 epochs jointly. Decoding uses a temperature of 0.7, a minimum stay of two slots and presence thresholds of 0.50, 0.40 and 0.15 for residential, office and retail.

Independent heads can place one person in two channels in the same slot. A decode-time exclusivity step assigns each slot to at most one channel by comparing each head's probability with its own threshold (Appendix B, Eq. B.4). The share of slots with more than one channel active is at most 0.5 % before this step and zero after it (Supplementary Figure S5). The full hyperparameter set is given in the Supplementary material (Table S3), with the checkpoint-selection record.

**Figure 2.** *(insert `Figure_03_three_head_transformer.png` here)* Occupancy model with three decoder heads and the separate hotel model.

The hotel channel does not pass through the Transformer. Its monthly rate r comes from the provincial series. For 2022, r is the observed monthly rate; the last three months of 2022, missing from the Alberta series, repeat its September value. For 2030, r is the 2019 monthly pattern rescaled to a post-pandemic recovery level of 0.615 in Alberta and 0.635 in Quebec [REF NEEDED: source of the 2023 to 2025 hotel recovery levels]. A seasonal ARIMA model, SARIMA(1,1,0)(0,1,0,12) [REF NEEDED: Box-Jenkins seasonal ARIMA source], is fitted to each series with a pandemic pulse from March 2020 to June 2022 and a level shift from March 2020. Its order was selected on Alberta's pre-pandemic months and reused for Quebec, whose series is too short to select its own. The model checks the seasonal pattern and the pandemic dip. Its long-range forecast is not used, because it drifts above full occupancy by 2030. The monthly rate r is turned into a half-hourly multiplier,

$$m(t, \mathrm{month}, \mathrm{PR}) = s(t)\, r(\mathrm{month}, \mathrm{PR}) \qquad (1)$$

where PR is the province and s(t) is a guest-room daily shape shared by both provinces. The shape holds 1.00 from 22:00 to 06:00 and falls to 0.200 on weekdays and 0.308 on weekends during the day (Figure 3).

**Figure 3.** *(insert `Figure_05_hotel_sidetrack.png` here)* Hotel occupancy model, from monthly provincial series to the half-hourly multiplier.

## 2.3 Scenarios to 2030

Each 2030 channel is built from the model conditioned on the 2030 cycle year. The generated diaries are then adjusted to 2022 survey targets. Weekday work presence outside business hours, weekend work and home presence, and retail presence are held at their 2022 levels within each labour-force group. Inside weekday business hours, the work-from-home band sets the change.

Each non-residential channel carries one scenario lever (Table 1). Office uses a work-from-home band with conservative, hybrid and fully hybrid values, the hybrid band being central. Retail uses an in-store share of 0.90, 0.97 or 1.05, applied before the customer-hours shape is normalised, with a Quebec Sunday sub-case for that province's regulated opening hours. Hotel uses a band of 0.92, 1.00 or 1.05 around the central seasonal projection. Residential has no lever of its own. Its 2030 schedules come from the same function and work-from-home parameter as the office schedules, so the two move together.

The three levers form three 2030 bundles: conservative, central and optimistic. Six further scenarios each move one lever to its conservative or optimistic value and hold the other two at central. Each lever is thus tested both jointly and in isolation.

## 2.4 Injection into the tower and end-use loads

The prototype towers leave the standard EnergyPlus space-type field blank. Each space instead carries a tag that names its use, and that tag is used as an exact-match key for routing (Figure 4). Apartment spaces receive the residential channel, and office, retail and guest-room spaces receive their own channels. Amenity and service spaces keep the prototype schedules. Any space whose tag matches no channel also keeps its prototype schedule.

The residential channel replaces the apartment occupant schedule with the modelled household schedule. Each tower draws one set of distinct synthetic households without replacement, 27 for the Tall tower and 41 for the SuperTall tower, one per apartment, with one fixed random seed. Montreal and Calgary models of the same tower and scenario receive the identical household set. The office schedule is also the same national product in both cities. Only the retail and hotel inputs differ by province. Differences between the cities therefore reflect climate and the retail and hotel inputs, not a new household draw.

The other three channels scale a code schedule rather than replace it. Office presence multiplies the NECB office occupant density (National Research Council Canada, 2017) by the modelled presence fraction. Retail presence is 0.95 times a normalised customer-hours shape, and slots with baseline occupancy at or below 0.10 are treated as staff-only and left unchanged. Retail spaces use the NECB office occupant density of 24.97 m2 per person rather than the retail value of 29.97 m2 per person. Guest-room occupancy is the NECB guest-room schedule times the hotel multiplier of Eq. (1).

In office, retail and guest-room spaces, lighting and plug loads follow occupancy above the prototype's standby floor (Appendix B, Eq. B.5). In apartments, only the occupant schedule changes, and lighting and plug loads stay on the prototype schedules. This split decides where occupancy can reach energy.

**Figure 4.** *(insert `Figure_06_tag2_dispatch.png` here)* Routing of the four channels to the tower spaces by space tag.

## 2.5 Buildings, climates and simulation campaign

The building models are the U.S. Department of Energy and Pacific Northwest National Laboratory (PNNL) Tall and SuperTall mixed-use prototypes, adapted to the National Energy Code of Canada for Buildings (NECB) 2017 (U.S. Department of Energy and Pacific Northwest National Laboratory; National Research Council Canada, 2017). Their total floor areas, parsed from the model geometry, are 72,623.1 m2 (Tall) and 135,857.6 m2 (SuperTall). Both towers hold all four uses plus amenity and service space, in different proportions (Supplementary Figure S1). The prototype axis is therefore a real experimental factor, not a size rescaling.

The two cities are Montreal (ASHRAE climate zone 6A) and Calgary (zone 7A), each with one typical meteorological year weather file. The Montreal and Calgary models of each tower share the same geometry and differ in their climate location and design-day sizing data. All runs use EnergyPlus 24.2 (U.S. Department of Energy, 2024).

The campaign crosses two towers, two cities and 14 scenarios, for 56 simulations (Table 2). One scenario is the code-schedule control, in which no schedule is injected. Four are the survey years 2005, 2010, 2015 and 2022. The remaining nine are the three 2030 bundles and the six one-lever variants. Hotel is injected from 2022 onwards only. In 2005, 2010 and 2015 the guest rooms stay on the code schedule, because the provincial series do not cover those years in both provinces.

**Table 2.** Simulation domain.

| Prototype | Total floor area (m2) | Cities | ASHRAE climate zone | Weather | Standard | Simulations |
|---|---|---|---|---|---|---|
| SuperTall | 135,857.6 | Montreal, Calgary | 6A, 7A | Typical year, one file per city | NECB 2017 | 28 |
| Tall | 72,623.1 | Montreal, Calgary | 6A, 7A | Typical year, one file per city | NECB 2017 | 28 |

The code-schedule control must be read exactly. In it, apartment and hotel guest-room occupants follow the NECB office occupancy schedule (NECB-A). Retail occupants follow the NECB retail schedule (NECB-C). Lighting keeps the PNNL prototype schedules for apartments and for the hotel. The control is therefore the tower as a practitioner would receive it, with residents and guests on office hours. A second control, run once for each of the four models, moves apartment and guest-room occupants to the NECB dwelling-unit schedule (NECB-G) and changes nothing else. In both controls, office and retail lighting and plug loads stay on the prototype schedules, while in the survey-based runs they follow occupancy above a standby floor.

Two checks guard the injection itself. After each injection, every modulated occupant object is checked for a reference to the injected schedule. Before a simulation is accepted, scenarios that should differ must give different outputs. The history of both checks is given in the Supplementary material.

## 2.6 Metrics, fitted parts and independent checks

Annual energy use intensity (EUI) is reported per channel on two floor-area bases, never averaged: the conditioned floor area of that use, and the gross floor area times that use's share of occupiable area (Appendix B, Eq. B.6). Load shape is described by three measures. The peak hour of a channel is the load-weighted circular mean of its average weekday profile (Eq. B.7) (Mardia and Jupp, 2000). The midday-to-night ratio is the mean weekday demand from 11 to 14 h divided by the mean from 22 to 04 h. The coincidence factor of the building is

$$\mathrm{CF} = \frac{\max_t \sum_{c} P_c(t)}{\sum_{c} \max_t P_c(t)} \qquad (2)$$

where P_c(t) is the hourly demand of channel c over the year [REF NEEDED: standard definition of coincidence factor]. The sum runs over six load channels: the four uses plus residential common space and service and mechanical space. CF is at most 1 by construction and equals 1 only when all channels peak in the same hour. Its level alone therefore says nothing; only its change between schedule sets does.

**Fitted or calibrated parts.** The Transformer is fitted to the GSS diaries of 2005 to 2022. The 2030 schedules are adjusted to 2022 survey targets (Section 2.3). The hotel model is fitted to the provincial series. Its reconstruction is checked against the same series over 2015 to 2019 for Alberta and over 2019 only for Quebec, and it reproduces the direction of the April 2020 dip but not its full depth. The activity-driven end-use layer is calibrated against the Survey of Commercial and Institutional Energy Use (Natural Resources Canada). None of these is an independent validation.

**Independent checks.** Three comparisons use information the model never saw. The first is the code-schedule control run on the same towers (Section 3.2). The second is a set of reference intensity ranges for each use, taken from published prototype results and literature (Section 3.4). An office, retail or hotel range is scored as met or not met. For retail, the rule is that the median of all 56 simulations must lie inside the range. For office and hotel, every simulation must lie inside. A wider empirical range, and the residential range from the Survey of Household Energy Use (Natural Resources Canada, 2019), are shown as context only. The ranges were not changed after the results were known. The retail median rule was adopted after an earlier run's numbers had been seen, and it was written down before the reported runs were read. Retail meets its range under the median rule but not under the all-simulations rule, where 19 of 56 simulations fall below the floor. The third check is the pair of injection checks in Section 2.5. The full list of thresholds and their sources is given in the Supplementary material (Table S1).
