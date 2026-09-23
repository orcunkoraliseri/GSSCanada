# Deep-Research Results dr_2J-17: Source References for Methods Equations

## 1. Summary Table of Equation Sources

| Equation / Metric | Class | Recommended Citation(s) | DOI / ISBN / URL | Crossref Checked | Location in Source | What Differs if ADAPTED |
|---|---|---|---|---|---|---|
| Eq. 1: act30_s = mode(slot_{3s-2}, slot_{3s-1}, slot_{3s}) | OWN | NO SOURCE NEEDED (Authors' own operational definition) | None | NA | NA | Standard modal downsampling heuristic; time-use harmonization manuals (HETUS, MTUS) preserve 10-minute slots or aggregate to daily sums rather than prescribing a 30-minute mode. |
| Eq. 2: hom30_s = 1[sum_{k=1..3} home_{3(s-1)+k} >= 2] | OWN | NO SOURCE NEEDED (Authors' own operational definition) | None | NA | NA | Discrete majority thresholding (>50% duration of the half-hour); no published time-use manual mandates this rule. |
| Eq. 3: Generative model training loss L = sum(lambda * l) + lambda_marg*l_marg + lambda_aux*l_aux | ADAPTED | Goodfellow et al. (2016); Caruana (1997); Vaswani et al. (2017) | ISBN 978-0-262-03561-3; DOI 10.1023/A:1007379606734; arXiv:1706.03762 | Yes (Caruana); NA (Goodfellow, Vaswani) | Goodfellow: Sec 5.5, pp. 129-133; Caruana: Sec 2, pp. 43-46; Vaswani: pp. 5998-6008 | Combines standard cross-entropy negative log-likelihood with Caruana multi-task weighting in an encoder-decoder Transformer, augmented by authors' domain-specific marginal rate penalty l_marg. |
| Eq. 4: n_tgt_{s,t} = clip(round(p_{s,t} * N_s), 0, N_s) | ADAPTED | Deming and Stephan (1940); Deville and Sarndal (1992) | DOI 10.1214/aoms/1177731829; DOI 10.1080/01621459.1992.10475217 | Yes | Deming: pp. 438-444; Deville: pp. 376-378 | Classical raking/IPF and calibration scale continuous weights across multi-way tables; adapted here into an exact integer target count for discrete synthetic households. |
| Eq. 5: Delta_{s,t} = n_tgt_{s,t} - n_cur_{s,t} (record flipping at change points) | OWN | Authors' own variant (Deming & Stephan 1940 and Deville & Sarndal 1992 as conceptual background; binary flipping algorithm: NOT FOUND) | DOI 10.1214/aoms/1177731829; DOI 10.1080/01621459.1992.10475217 | Yes | Deming: pp. 438-444; Deville: pp. 376-378 | Single-pass greedy record-flipping prioritized at activity transitions to meet an exact integer marginal is an author-devised heuristic, not iterative proportional fitting or standard survey reweighting. |
| Eq. 6: occ48_{h,d,t} = (1/M_h) * sum hom30 | OWN | NO SOURCE NEEDED (Authors' own operational definition) | None | NA | NA | Arithmetic mean of binary occupant presence across household members. |
| Eq. 7: met48_{h,d,t} = (1/M_h) * sum W_met(act30) | ADAPTED | Herrmann et al. (2024); ASHRAE (2021) | DOI 10.1016/j.jshs.2023.10.010; ISBN 978-1-947192-90-4 | Yes (Herrmann); NA (ASHRAE) | Herrmann: Table 1 / Comprehensive database; ASHRAE: Ch. 9, Table 4 | Sourced to the 2024 Adult Compendium of Physical Activities (Herrmann et al., 2024) in MET units, scaled by a fixed factor of 70 W/MET (~60 kg adult) into watts per person. |
| Eq. 8: P_t = P_base + sum shared + sum personal + P_dw*eta | ADAPTED | Richardson et al. (2010); Richardson et al. (2009); Widen and Wackelgard (2010) | DOI 10.1016/j.enbuild.2010.05.023; DOI 10.1016/j.enbuild.2009.02.010; DOI 10.1016/j.apenergy.2009.11.006 | Yes | Richardson (2010): Sec 2.3; Richardson (2009): Sec 2.3; Widen (2010): Sec 2.2 | Adapts Richardson effective occupancy and Widen activity-to-appliance mapping to deterministic activity inputs with a simplified discrete multiplier vector eta = [1.0, 1.4, 1.7, 1.9, 2.0]. |
| Eq. 9: f_e = E_tgt / E_raw | ADAPTED | Natural Resources Canada (2021); Armstrong et al. (2009); Richardson et al. (2010); Chen et al. (2022) | URL: oee.nrcan.gc.ca; DOI 10.1080/19401490802706653; DOI 10.1016/j.enbuild.2010.05.023; DOI 10.1016/j.apenergy.2022.119890 | Yes (Armstrong, Richardson, Chen) | NRCan (2021): Data Tables; Armstrong: Sec 4, pp. 22-26; Richardson: Sec 2.3, p. 1881; Chen: Sec 2.3 | Multiplicative scalar calibration aligns simulated annual totals to national survey benchmarks; literature typically embeds scalars in switch-on probabilities or ownership weights. |
| Eq. 10: target_lambda[s,t] = clip(stock_2022 + 8*slope - (1-lambda)*jump, 0, 1) | OWN | NO SOURCE NEEDED for equation; conceptual support: Barrero et al. (2021, 2023) | DOI 10.1257/jep.37.4.23; DOI 10.3386/w28731 | Yes | Barrero (2023): pp. 23-28; Barrero (2021): pp. 1-15 | Formula is authors' own parametric trend-plus-jump decomposition; cited papers support treating telework retention as scenario persistence shares rather than temporary shocks. |
| Eq. 11: Simple random sampling of 50 households without replacement | STANDARD | Cochran (1977) | ISBN 978-0-471-16240-7 | NA | Chapter 2, Sec 2.1, pp. 18-21 | None (standard textbook simple random sampling without replacement). |
| Eq. 12: w_{a,c} = w_a / |C_a|, sum_a w_a = 1 | OWN | NO SOURCE NEEDED (Authors' own operational definition) | None | NA | NA | Standard uniform allocation of archetype stock weights across sampled cluster instances. |
| Eq. 13: Circular mean peak hour h_bar = (24/2pi)*atan2(mean sin, mean cos) mod 24 | STANDARD | Mardia and Jupp (2000); Fisher (1993) | ISBN 978-0-471-95333-3; ISBN 978-0-521-35018-1 | NA | Mardia & Jupp: Sec 2.3.1, Eq. 2.3.1, p. 15; Fisher: Sec 2.2, Eq. 2.9, p. 31 | None (standard definition of circular mean direction scaled to 24 hours). |
| Eq. 14: Circular standard deviation sd_circ = (24/2pi)*sqrt(-2 ln R) | STANDARD | Mardia and Jupp (2000); Fisher (1993) | ISBN 978-0-471-95333-3; ISBN 978-0-521-35018-1 | NA | Mardia & Jupp: Sec 2.3.1, Eq. 2.3.6, p. 18; Fisher: Sec 2.2, Eq. 2.12, p. 32 | None (standard definition of circular standard deviation scaled to 24 hours). |
| LF (inline): Load factor = mean hourly load / annual peak hourly load | STANDARD | Grainger and Stevenson (1994); Wood et al. (2013) | ISBN 978-0-07-061293-8; ISBN 978-0-471-79055-6 | NA | Grainger & Stevenson: Ch. 1, Sec 1.2, pp. 12-15; Wood: Sec 1.2, pp. 5-7 | None (standard electric power engineering textbook definition). |
| Midday share (inline): energy 09:00-17:00 / daily energy | OWN | NO SOURCE NEEDED (Authors' own operational definition) | None | NA | NA | Operational ratio measuring daytime solar/WFH energy concentration. |
| Ramp (inline): mean over days of (load at 17:00 minus load at 14:00) | ADAPTED | Denholm et al. (2015) | DOI 10.2172/1226167 | Yes | Executive Summary, pp. v-vi; Sec 3, pp. 7-12 | Denholm et al. define system-wide multi-hour net-load ramping (MW over 3 hours); adapted here to a 3-hour difference evaluated at the building/household level. |
| Eq. 15: d_i = M_i^(B) - M_i^(A) (paired difference) | STANDARD | Montgomery and Runger (2018) | ISBN 978-1-119-40030-1 | NA | Chapter 10, Sec 10.4, p. 367 | None (standard paired difference definition). |
| Eq. 16: d_bar +/- t_{0.975, n-1} * s_d / sqrt(n) | STANDARD | Montgomery and Runger (2018) | ISBN 978-1-119-40030-1 | NA | Chapter 10, Sec 10.4.2, Eq. 10.15, p. 368 | None (standard Student-t confidence interval for paired differences). |
| Eq. 17: S_fixed_{h,d,k} = R_{d,k} (DOE prototype comparison schedule) | ADAPTED | Deru et al. (2011); Goel et al. (2014); NREL (2024); Guglielmetti et al. (2011) | DOI 10.2172/1009264; DOI 10.2172/1132646; URL: github.com/NREL/openstudio-standards | Yes (Deru); NA (NREL, Guglielmetti) | Deru: Sec 2.1, pp. 11-14; Goel: pp. 1-10; Guglielmetti: pp. 442-449 | Adopts the DOE/PNNL ApartmentMidRise prototype compliance schedule as a fixed, deterministic comparison baseline for all households. |
| Eq. 18: S_avg_{c,y,d,k} = (1/|Pool_c|) * sum S_full | OWN | NO SOURCE NEEDED for equation; conceptual support: Chen et al. (2022); Aerts et al. (2014); Haldi and Robinson (2011) | DOI 10.1016/j.apenergy.2022.119890; DOI 10.1016/j.buildenv.2014.01.015; DOI 10.1080/19401493.2011.558213 | Yes | Chen: Sec 2.3; Aerts: pp. 70-76; Haldi: pp. 325-332 | Formula is authors' own pool-average; cited literature justifies comparing average/standard schedules against stochastic individual schedules to quantify diversity. |

---

## 2. Full Reference List (Elsevier Author-Year Style)

Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F., 2014. A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. Building and Environment 75, 67-78. https://doi.org/10.1016/j.buildenv.2014.01.015.

Armstrong, M.M., Swinton, M.C., Ribberink, H., Beausoleil-Morrison, I., Millette, J., 2009. Synthetically derived profiles for representing occupant-driven electric loads in Canadian housing. Journal of Building Performance Simulation 2 (1), 15-30. https://doi.org/10.1080/19401490802706653.

ASHRAE, 2021. 2021 ASHRAE Handbook - Fundamentals. American Society of Heating, Refrigerating and Air-Conditioning Engineers, Atlanta, GA. ISBN 978-1-947192-90-4.

Barrero, J.M., Bloom, N., Davis, S.J., 2021. Why Working from Home Will Stick. Working Paper 28731. National Bureau of Economic Research, Cambridge, MA. https://doi.org/10.3386/w28731.

Barrero, J.M., Bloom, N., Davis, S.J., 2023. The Evolution of Work from Home. Journal of Economic Perspectives 37 (4), 23-49. https://doi.org/10.1257/jep.37.4.23.

Bishop, C.M., 2006. Pattern Recognition and Machine Learning. Springer, New York. ISBN 978-0-387-31073-2.

Caruana, R., 1997. Multitask Learning. Machine Learning 28 (1), 41-75. https://doi.org/10.1023/A:1007379606734.

Chen, J., Adhikari, R., Wilson, E., Robertson, J., Fontanini, A., Polly, B., Olawale, O., 2022. Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model. Applied Energy 325, 119890. https://doi.org/10.1016/j.apenergy.2022.119890.

Cochran, W.G., 1977. Sampling Techniques, 3rd ed. John Wiley & Sons, New York. ISBN 978-0-471-16240-7.

Deming, W.E., Stephan, F.F., 1940. On a Least Squares Adjustment of a Sampled Frequency Table When the Expected Marginal Totals are Known. The Annals of Mathematical Statistics 11 (4), 427-444. https://doi.org/10.1214/aoms/1177731829.

Denholm, P., O'Connell, M., Brinkman, G., Jorgenson, J., 2015. Overgeneration from Solar Energy in California: A Field Guide to the Duck Chart. Technical Report NREL/TP-6A20-65023. National Renewable Energy Laboratory, Golden, CO. https://doi.org/10.2172/1226167.

Deru, M., Field, K., Studer, D., Benne, K., Griffith, B., Torcellini, P., Liu, B., Halverson, M., Winiarski, D., Rosenberg, M., Yazdanian, M., Huang, J., Crawley, D., 2011. U.S. Department of Energy Commercial Reference Building Models of the National Building Stock. Technical Report NREL/TP-5500-46861. National Renewable Energy Laboratory, Golden, CO. https://doi.org/10.2172/1009264.

Deville, J.-C., Sarndal, C.-E., 1992. Calibration Estimators in Survey Sampling. Journal of the American Statistical Association 87 (418), 376-382. https://doi.org/10.1080/01621459.1992.10475217.

Fisher, N.I., 1993. Statistical Analysis of Circular Data. Cambridge University Press, Cambridge. ISBN 978-0-521-35018-1.

Goel, S., Athalye, R.A., Wang, W., Zhang, J., Rosenberg, M.I., Xie, Y., Hart, P.R., Mendon, V.V., 2014. Enhancements to ASHRAE Standard 90.1 Prototype Building Models. Technical Report PNNL-23269. Pacific Northwest National Laboratory, Richland, WA. https://doi.org/10.2172/1132646.

Goodfellow, I., Bengio, Y., Courville, A., 2016. Deep Learning. MIT Press, Cambridge, MA. ISBN 978-0-262-03561-3.

Grainger, J.J., Stevenson, W.D., 1994. Power System Analysis. McGraw-Hill, New York. ISBN 978-0-07-061293-8.

Guglielmetti, R., Macumber, D., Long, N., 2011. OpenStudio: An open source integrated analysis platform. In: Proceedings of Building Simulation 2011: 12th Conference of International Building Performance Simulation Association, Sydney, Australia, pp. 442-449.

Haldi, F., Robinson, D., 2011. The impact of occupants' behaviour on building energy demand. Journal of Building Performance Simulation 4 (4), 323-338. https://doi.org/10.1080/19401493.2011.558213.

Herrmann, S.D., Willis, E.A., Ainsworth, B.E., Barreira, T.V., Hutto, B., Jones, C.A., Macera, C.A., Powell, K.E., Tudor-Locke, C., Whitt-Glover, M.C., Leon, A.S., 2024. 2024 Adult Compendium of Physical Activities: A third update of the energy costs of human activities. Journal of Sport and Health Science 13 (1), 6-12. https://doi.org/10.1016/j.jshs.2023.10.010.

Mardia, K.V., Jupp, P.E., 2000. Directional Statistics. John Wiley & Sons, Chichester. ISBN 978-0-471-95333-3.

Montgomery, D.C., Runger, G.C., 2018. Applied Statistics and Probability for Engineers, 7th ed. John Wiley & Sons, Hoboken, NJ. ISBN 978-1-119-40030-1.

National Renewable Energy Laboratory (NREL), 2024. openstudio-standards: Ruby gem to automate OpenStudio building models to meet energy standards. GitHub repository, available at: https://github.com/NREL/openstudio-standards.

Natural Resources Canada, 2021. Survey of Household Energy Use 2019 (SHEU-2019) Data Tables. Office of Energy Efficiency, Natural Resources Canada, Ottawa, ON. Available at: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm.

Richardson, I., Thomson, M., Infield, D., 2008. A high-resolution domestic building occupancy model for energy demand simulations. Energy and Buildings 40 (8), 1560-1566. https://doi.org/10.1016/j.enbuild.2008.02.006.

Richardson, I., Thomson, M., Infield, D., Delahunty, A., 2009. Domestic lighting: A high-resolution energy demand model. Energy and Buildings 41 (7), 781-789. https://doi.org/10.1016/j.enbuild.2009.02.010.

Richardson, I., Thomson, M., Infield, D., Clifford, C., 2010. Domestic electricity use: A high-resolution energy demand model. Energy and Buildings 42 (10), 1878-1887. https://doi.org/10.1016/j.enbuild.2010.05.023.

Statistics Canada, 2021. Table 25-10-0060-01: Household energy consumption, Canada and provinces. Statistics Canada, Ottawa, ON. https://doi.org/10.25318/2510006001-eng.

Terry, N., Palmer, J., 2013. Household Electricity Survey: A Study of Domestic Electrical Lighting. Technical Report. Cambridge Architectural Research Ltd, Cambridge, UK.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, L., Polosukhin, I., 2017. Attention is all you need. In: Advances in Neural Information Processing Systems (NeurIPS 2017), Vol. 30, pp. 5998-6008.

Widen, J., Wackelgard, E., 2010. A high-resolution stochastic model of domestic activity patterns and electricity demand. Applied Energy 87 (6), 1880-1892. https://doi.org/10.1016/j.apenergy.2009.11.006.

Wood, A.J., Wollenberg, B.F., Sheble, G.B., 2013. Power Generation, Operation, and Control, 3rd ed. John Wiley & Sons, Hoboken, NJ. ISBN 978-0-471-79055-6.

---

## 3. Metabolic-Rate Table Comparison for Eq. 7

The internal metabolic heat generation channel (W_met) maps 14 unified activity categories into fixed watts per person. The table below presents the manuscript values against the closest published entries in the 2024 Adult Compendium of Physical Activities (Herrmann et al., 2024, DOI: 10.1016/j.jshs.2023.10.010) and ASHRAE Handbook of Fundamentals (2021, Chapter 9, Table 4).

### Detailed Value Comparison Table

| Code | Activity Category | Manuscript Value (W/person) | Implied MET (W / 70) | 2024 Adult Compendium Anchor Activity | Compendium MET | Scaled Compendium (MET * 70 W) | ASHRAE Fundamentals (Ch. 9, Table 4) | Match Verdict & Notes |
|---|---|---|---|---|---|---|---|---|
| 5 | Sleep, naps and resting | 70 | 1.00 | Sleeping (Inactivity) | 1.00 | 70.0 | Sleeping: 0.7 met (73.5 W @ 105 W/met) | Exact match (Primary anchor) |
| 6 | Eating and drinking | 105 | 1.50 | Eating, sitting (Self Care) | 1.50 | 105.0 | Seated, quiet / eating: 1.0-1.4 met (105-147 W) | Exact match (Primary anchor) |
| 8 | Education | 110 | 1.57 | Sitting, studying (reading/writing) | 1.50 | 105.0 | Reading/Writing, seated: 1.0 met (105 W) | Close match (Central value) |
| 10 | Passive leisure | 85 | 1.21 | Watch television (1.00); Sitting, reading (1.00-1.30) | 1.00-1.30 | 70.0-91.0 | Reclining: 0.8 met (84 W); Seated: 1.0 met (105 W) | Central match (85 W falls within reading/TV band) |
| 12 | Community and volunteer | 105 | 1.50 | Religious/church sitting (1.50); Volunteer sitting (1.30-1.50) | 1.50 | 105.0 | Seated, quiet: 1.0 met (105 W) | Central match |
| 2 | Household work and maintenance | 175 | 2.50 | Cooking/food prep (2.00-2.50); Cleaning/dusting (2.20-3.00) | 2.00-3.00 | 140.0-210.0 | Cooking: 1.6-2.0 met (168-210 W); Cleaning: 2.0-3.4 met | Central match (Direct midpoint of cooking and cleaning) |
| 4 | Purchasing goods and services | 195 | 2.79 | Non-food shopping (2.30); Grocery shopping (3.30) | 2.30-3.30 | 161.0-231.0 | Walking, shopping: 1.7-2.2 met (178-231 W) | Central blend (Midpoint between grocery and retail shopping) |
| 3 | Caregiving and help | 190 | 2.71 | Childcare sitting/kneeling (2.00-2.50); Childcare standing (3.00) | 2.00-3.50 | 140.0-245.0 | Domestic activities: 1.8-2.8 met (189-294 W) | Weighted blend (Active child/elder caregiving) |
| 7 | Personal care | 170 | 2.43 | Bathing sitting (1.50); Showering (2.00); Dressing (2.50-2.80) | 1.50-2.80 | 105.0-196.0 | Grooming, dressing, standing: 1.5-2.5 met (157-262 W) | Upper-central match (Dressing and grooming routine) |
| 1 | Work and related | 125 | 1.79 | Office desk work (1.30-1.50); Standing light work (1.80-2.20) | 1.30-2.20 | 91.0-154.0 | Typing/computer: 1.1 met (115 W); Filing/light: 1.2-1.4 met | Central occupational blend (Sedentary and standing mix) |
| 13 | Travel | 140 | 2.00 | Driving automobile (1.30-2.00); Transit passenger (1.30) | 1.30-2.00 | 91.0-140.0 | Driving a car: 1.2-1.5 met (126-157 W) | Upper bound of motorized transit / light walking |
| 9 | Socializing | 90 | 1.29 | Sitting, talking in person (1.30); Standing talking (1.80) | 1.30-1.80 | 91.0-126.0 | Seated, quiet conversation: 1.0 met (105 W) | Seated conversation proxy |
| 11 | Active leisure | 245 | 3.50 | Walking for pleasure (3.50); Moderate calisthenics (3.50) | 3.50 | 245.0 | Walking 1.3 m/s: 2.6 met (273 W); Exercise: 3.0-4.0 met | Exact match for moderate leisure walk / calisthenics |
| 14 | Miscellaneous or idle | 135 | 1.93 | Standing, light activity / waiting | 1.50-2.00 | 105.0-140.0 | Standing, light manual tasks: 1.4-1.8 met | Central match for standing / waiting residual |
| 0 | Unknown activity | 100 | 1.43 | Average adult resting/sedentary baseline | 1.40-1.50 | 98.0-105.0 | Baseline awake sedentary: 1.0 met (105 W) | Default daytime fallback |

### The 70 W/MET Conversion Basis

In physiology and exercise science, 1 MET is defined as 1.0 kcal per kilogram of body weight per hour (1.0 kcal/kg/h = 1.163 W/kg). The manuscript's table maps activities to watts per person using a uniform factor of 70 W/MET, as established by two independent exact mathematical anchors:
- Sleeping: 1.00 MET in the Compendium corresponds to exactly 70 W (70 / 1.00 = 70.0 W/MET).
- Eating, sitting: 1.50 MET in the Compendium corresponds to exactly 105 W (105 / 1.50 = 70.0 W/MET).

Dividing 70 W by 1.163 W/kg yields an effective body mass of approximately 60.2 kg:
- This basis reflects a conservative ~60 kg adult.
- In contrast, the standard ASHRAE Standard 55 and ISO 7730 surface-area basis assumes an adult male with a DuBois body surface area of 1.8 m2, where 1 met = 58.15 W/m2 * 1.8 m2 = 104.7 W (often rounded to 105 W per person).
- Under the standard 70 kg reference adult used in medical physiology, 1 MET corresponds to approximately 81.4 to 83 W per person.

Because all internal heat gains scale directly with W_met, documenting this 70 W/MET (~60 kg) basis provides full methodological transparency.

---

## 4. Effective-Occupancy Values Comparison for Eq. 8

Equation 8 models activity-driven electricity consumption by separating shared equipment from personal equipment via a co-occupancy factor eta(n_t). The table below compares the values used in the manuscript with published co-occupancy and effective occupancy formulations in the literature.

### Side-by-Side Comparison

| Active Occupants (n) | Manuscript eta(n) | Richardson et al. (2009) Lighting Model | Richardson et al. (2010) Appliance Model | Terry and Palmer (2013) / HES Formula | Status / Rationale |
|---|---|---|---|---|---|
| n = 0 | 0.0 | 0.0 | 0.0 | 0.0000 | Baseline (Unoccupied) |
| n = 1 | 1.0 | 1.0 | Baseline switch-on rate | 0.9174 | Baseline active occupant |
| n = 2 | 1.4 | Shared room lighting | Non-linear scaling factor | 1.1719 | Sub-linear diminishing marginal draw |
| n = 3 | 1.7 | Shared room lighting | Non-linear scaling factor | 1.4264 | Sub-linear diminishing marginal draw |
| n = 4 | 1.9 | Shared room lighting | Non-linear scaling factor | 1.6809 | Sub-linear diminishing marginal draw |
| n >= 5 | 2.0 | Shared room lighting | Non-linear scaling factor | 1.9354 | Saturation bound of shared infrastructure |

### Methodological Finding and Provenance

1. Richardson et al. (2009) introduced the concept of effective occupancy to prevent double-counting when multiple occupants share common room lighting.
2. In the UK Household Electricity Survey (Terry and Palmer, 2013, Cambridge Architectural Research Ltd), the lighting model was parameterized using an empirical incremental formula:
   EFF_o = (0.2545 * o) + 0.6629 - EFF_{o-1}
   This produces cumulative effective occupancy multipliers of 0.92, 1.17, 1.43, 1.68, and 1.94 for 1 through 5 occupants.
3. Richardson et al. (2010) implemented a similar sub-linear relationship for shared household appliances (e.g. televisions, cooking, dishwashers), adjusting switch-on probabilities dynamically according to active occupancy. However, Richardson et al. (2010) did not publish a static discrete multiplier vector in tabular form.
4. Widen and Wackelgard (2010) established the foundational methodology for mapping time-use activity categories directly to residential electrical appliances, distinguishing between shared household activities and individualized personal devices.
5. Honest Status: The manuscript's discrete vector eta = [1.0, 1.4, 1.7, 1.9, 2.0] is INSPIRED BY the sub-linear sharing concept of Richardson et al. (2009, 2010) and the activity-to-appliance mapping of Widen and Wackelgard (2010). The specific values represent an author-defined, piecewise sub-linear simplification rather than numbers transcribed directly from a table in Richardson et al.

---

## 5. Positive Control Result

- Target DOI: 10.1016/j.enbuild.2008.02.006
- Target Citation: Richardson, Thomson and Infield (2008), Energy and Buildings 40(8), 1560-1566
- Crossref API Query: https://api.crossref.org/works/10.1016/j.enbuild.2008.02.006
- Positive Control Status: SUCCEEDED
- Crossref Metadata Record Retrieved:
  - Title: A high-resolution domestic building occupancy model for energy demand simulations
  - Container (Journal): Energy and Buildings
  - Volume: 40
  - Issue: 8
  - Pages: 1560-1566
  - Publication Date: 2008-01-01
  - Authors: Ian Richardson, Murray Thomson, David Infield
  - Publisher: Elsevier BV

---

## 6. What I Could Not Find (First-Person Inventory)

1. I could not find any official time-use harmonization guideline from Eurostat (HETUS) or the Multinational Time Use Study (MTUS) that mandates or standardizes a 30-minute modal aggregation rule for downsampling 10-minute diary records.
2. I could not find a published synthetic population or microsimulation study that adjusts binary occupancy time series to exact marginal integer counts via a single-pass greedy flipping heuristic prioritized at activity transition points.
3. I could not find a printed table in Richardson et al. (2009) or Richardson et al. (2010) containing the exact discrete multiplier sequence [1.0, 1.4, 1.7, 1.9, 2.0], confirming that this sequence is an inspired authorial simplification rather than a direct transcription.
4. I could not find a peer-reviewed journal article with an official DOI dedicated solely to the OpenStudio-Standards library, as it is formally distributed as an open-source code repository by the National Renewable Energy Laboratory (NREL).
5. I could not find any published academic paper containing the exact parametric formula of Eq. 10 that decomposes a 2030 target into a linear trend, an observed jump, and a persistence share lambda.
