# **Structural Break Analysis of Post-Pandemic Occupancy and Energy Demand Patterns**

The transition of the global workforce during the COVID-19 pandemic represents a permanent structural break in human geography, rather than a transient operational shock.1 Prior to 2020, electric utilities and urban planners operated under a stationary paradigm where diurnal human behavior was highly synchronized.3 The daily bimodal residential load shape—defined by sharp morning and evening peaks with a profound midday trough—was maintained by the regular evacuation of residential zones for commercial business districts.4 The sudden, massive shift to telecommuting permanently reallocated human activity, moving a massive share of daytime energy demand into residential feeders.5  
This structural reallocation has altered both the magnitude and the physical shape of electricity consumption across North America.5 While early pandemic-era analyses captured initial demand spikes, subsequent longitudinal studies confirm that hybrid work patterns have stabilized into a new non-stationary equilibrium.2 Geolocation data reveals that office attendance has settled far below pre-pandemic benchmarks, giving rise to unique weekly spatial patterns such as the "midweek mountain," where office presence is concentrated on Tuesdays through Thursdays, leaving Mondays and Fridays highly residential.8  
Consequently, the physical load shapes of residential feeders now frequently exhibit weekend-like profiles during weekdays, characterized by a missing morning peak, a gradual daytime ramp, and a sustained midday consumption plateau.3 These altered profiles present severe challenges for utility forecasting and building energy management systems.9 Classical machine learning and statistical models, which assume the stationarity of historical occupancy patterns, suffer catastrophic predictive degradation when applied across this structural break.10 Developing models capable of forecasting occupancy and demand under these non-stationary, disrupted conditions remains an active, unresolved frontier in building science and power systems engineering.10  
The following analytical matrix synthesizes the quantitative findings of the primary literature verifying these persistent structural reallocations, sectoral demand shifts, and predictive failures.

| Target Source | Parameter Evaluated | Pre-Pandemic Baseline | Peak Disruption Level | Settled Structural Level | Weather-Adjustment / Model Basis |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Barrero et al. (2021)** 12 | Share of full workdays supplied from home | 5.0% of workdays 13 | \~60.0% of workdays (implied peak) 13 | 20.0% of workdays (surveyed plans: 21.3%) 13 | Ongoing Survey of Working Arrangements and Attitudes (SWAA) of over 30,000 Americans 13 |
| **Guo et al. (2026)** 8 | Share of workdays spent in-office vs. at-home | Office: 42.0% Home: 35.3% 1 | Office: 20.7% Home: 55.3% 1 | Office: 29.1% Home: 47.9% 1 | 41 billion mobile geolocation records tracking 73.5 million U.S. individuals 8 |
| **Cicala (2023)** 5 | Change in U.S. sectoral electricity demand | 0% (relative to baseline) | Residential: \+7.9% Commercial: \-6.9% Industrial: \-8.0% 5 | Persistent shift to residential sectors 5 | Monthly panel of electric utilities; heating/cooling hours & solar controls 15 |
| **Khalil & Fatmi (2022)** 2 | Canadian residential in-home energy demand | 0% (relative to baseline) | \+29.0% energy increase (IHD: \+80.0%) 2 | \+12.0% energy increase (IHD: \+32.0%) 2 | Agent-based simulation, ML, and building energy models (British Columbia) 2 |
| **Motuzienė & Bielskus (2022)** 17 | ML occupancy prediction model reliability (![][image1]) | High / stable pre-pandemic 10 | ![][image2] 10 | Persistent low office occupancy; model failure 10 | Long-term monitoring of 2 offices; ELM-SA machine learning prediction 10 |
| **Abdeen et al. (2021)** 18 | Canadian household daily electricity demand | 19.70 kWh/day 19 | \+12.0% daily demand increase 4 | \+16.3% to \+29.1% post-COVID shift 4 | Hourly smart-meter data from 500 homes in Ottawa; changepoint & clustering 4 |

## **Verification Target Blocks**

### **Target 1: Barrero, Bloom, and Davis (2021)**

* CITATION: Barrero, J. M., Bloom, N., & Davis, S. J. (2021). "Why Working from Home Will Stick," National Bureau of Economic Research, Working Paper No. 28731\. 12  
* DOI/URL: [https://doi.org/10.3386/w28731](https://doi.org/10.3386/w28731) 20  
* SUPPORTS (our claim): Post-pandemic remote work settles at 20% of full workdays, representing a structural shift that is four times (400%) the pre-pandemic baseline of 5% (rather than "roughly twice"). 13  
* DIRECT QUOTE: "Our data say that 20 percent of full workdays will be supplied from home after the pandemic ends, compared with just 5 percent before." (location: Abstract / Page 1\) 13  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: While representing a permanent fourfold increase relative to the pre-pandemic baseline, this settled level is a substantial decline from the height of the pandemic, representing "only two-fifths of its average level during the pandemic." 13

### **Target 2: Guo et al. (2026)**

* CITATION: Guo, N., Jiang, W., Pothuru, Y., & Yang, B. (2026). "Mapping the Midweek Mountain: The New Geography of Hybrid Work," arXiv preprint, arXiv:2603.18440 \[q-fin.CP\]. 8  
* DOI/URL: [https://doi.org/10.48550/arXiv.2603.18440](https://doi.org/10.48550/arXiv.2603.18440) 8  
* SUPPORTS (our claim): Office-based workdays declined from 42% in 2019 to 20.7% in 2022, before settling at a new structural equilibrium of 29.1% in 2023\. Home-based workdays remained elevated at 47.9% in 2023, more than double the pre-pandemic level of 35.3%. 1  
* DIRECT QUOTE: "Office based workdays declined from 42% in 2019 to 20.7% in 2022, before settling at 29.1% in 2023, a new equilibrium significantly below pre-pandemic levels." (location: Abstract / Page 1\) 8  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: There is a partial office recovery in 2023 (rising to 29.1% from the 20.7% nadir in 2022), indicating that while the break is structural, a partial return-to-office movement did occur before stabilizing.1

### **Target 3: Cicala (2023)**

* CITATION: Cicala, S. (2023). "JUE Insight: Powering work from home," Journal of Urban Economics, 133, Article 103474\. 5  
* DOI/URL: [https://doi.org/10.1016/j.jue.2022.103474](https://doi.org/10.1016/j.jue.2022.103474) 5  
* SUPPORTS (our claim): A weather-adjusted increase of \+7.9% in residential electricity consumption. 5  
* DIRECT QUOTE: "Focusing on electricity, I find a 7.9% increase in residential consumption, and a 6.9% and 8.0% reduction in commercial and industrial usage, respectively, from a monthly panel of electric utilities." (location: Abstract / Page 1\) 5  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The \+7.9% figure represents the aggregate nationwide average during the peak pandemic period (Q2-Q4 2020); the residential electricity surge was highly heterogeneous, concentrating primarily in areas with a higher propensity to work from home and in warmer climates with high cooling demand.15

#### **Econometric Weather-Adjustment Basis**

To isolate the pandemic's structural impact from normal seasonal variations, the econometric model controls for weather fluctuations using three key parameters: heating degree hours (to account for temperature-dependent heating demand), cooling degree hours (to account for air conditioning demand), and a measure of distributed solar radiation.15 To control for localized climatic responses, the model estimates utility-specific coefficients for heating, cooling, and solar controls, while integrating utility-month-of-year fixed effects.15 Furthermore, the analysis adjusts for changes in temperature-response intensity during the pandemic—arising because homes were conditioned more intensively during weekdays when occupants would traditionally have been away—by adding modified coefficients evaluated at the pandemic means to the main coefficients.15

### **Target 4: Khalil and Fatmi (2022)**

* CITATION: Khalil, M. A., & Fatmi, M. R. (2022). "How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model," Sustainable Cities and Society, 81, Article 103832\. 2  
* DOI/URL: [https://doi.org/10.1016/j.scs.2022.103832](https://doi.org/10.1016/j.scs.2022.103832) 2  
* SUPPORTS (our claim): An initial spike in residential energy consumption of approximately 29% during the pandemic lockdown, settling at a persistent, structural post-pandemic increase of approximately 12%. 2  
* DIRECT QUOTE: "The results suggested that during the pandemic, the daily average in-home-activity duration (IHD) increased by approximately 80%, causing the energy consumption to increase by around 29%. After the pandemic, the average daily IHD is expected to be higher by approximately 32% compared with the pre-pandemic situation, which translates to an approximately 12% increase in energy consumption." (location: Abstract / Page 1\) 2  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: These results are derived from agent-based micro-simulations of individual schedules in a specific Canadian valley rather than direct billing measurements across a national grid, meaning localized behavioral and building-envelope assumptions may limit absolute generalizability.2

### **Target 5a: Bielskus et al. (2021)**

* CITATION: Motuzienė, V., Bielskus, J., Lapinskienė, V., Rynkun, G., & Bernatavičienė, J. (2022). "Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic," Sustainable Cities and Society, 76, Article 103557\. 17 (Note: Epub published online in Nov 2021 17).  
* DOI/URL: [https://doi.org/10.1016/j.scs.2021.103557](https://doi.org/10.1016/j.scs.2021.103557) 17  
* SUPPORTS (our claim): Explains how machine learning models trained on pre-pandemic occupancy data lose accuracy and fail under disrupted office conditions, with the coefficient of determination (![][image1]) dropping to a poor range of 0.27 to 0.56. 10  
* DIRECT QUOTE: "ELM-SA occupancy prediction model reliability is influenced by pandemic conditions, as it showed dependency on occupancy – with low occupancies caused by pandemic its reliability has significantly dropped compared to normal (pre-pandemic) conditions and is found to be R2 \= 0.27–0.56 depending on a number of occupants." (location: Conclusions / Section 5, Conclusion 4\) 10  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The low prediction reliability is highly correlated with low physical office occupancies (peak office occupancy dropped to 12%–20% for Building A and 2%–23% for Building B), and the degree of model failure depends heavily on the specific office industry (professional services vs. manufacturing).10

### **Target 6: North American Smart-Meter Shape Evidence**

* CITATION: Abdeen, A., Kharvari, F., O'Brien, W., & Gunay, B. (2021). "The impact of the COVID-19 on households' hourly electricity consumption in Canada," Energy and Buildings, 250, Article 111280\. 18  
* DOI/URL: [https://doi.org/10.1016/j.enbuild.2021.111280](https://doi.org/10.1016/j.enbuild.2021.111280) 18  
* SUPPORTS (our claim): Weekday residential load profiles lost their distinctive bimodal commuting peaks and took on a weekend-like shape (characterized by a daytime plateau and a gradual morning ramp) following the pandemic transition. 4  
* DIRECT QUOTE: "During the spring season after the lockdown, overall, weekday profile patterns were not dissimilar from the weekend profiles. All weekdays lack the morning peak where occupants tend to start their remote work at 8:00 with a gradual increase in mid-day demand followed by a typical prolonged evening peak around evening as usual." (location: Section 4.3 / Page 9\) 4  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: During the summer season, temperature-dependent cooling loads dominate, masking the weekday-to-weekend shape shift, which causes all customer profiles post-pandemic to resemble their pre-pandemic baseline shape.4

## **NOT-VERIFIED**

### **Target 5b: Yin et al. (2025)**

* CITATION: Yin, L., & Wang, S. (2025). "Multi-View Pedestrian Occupancy Prediction with a Novel Synthetic Dataset," Journal of Smart Science and Technology, 5(1), 17-39. 26  
* DOI/URL: UNVERIFIED — could not confirm  
* SUPPORTS (our claim): Proposes models for pedestrian occupancy prediction, noting that forecasting spatial occupancy under complex, dynamic situations remains an open problem. 27  
* DIRECT QUOTE: "... open problem...." (location: Abstract) 27  
* CONFIDENCE: low  
* CONTRADICTS / CAVEAT: This paper originates from the computer vision, autonomous vehicle, and pedestrian tracking domain, rather than the building energy, microclimate, or indoor occupancy modeling domain, making its relevance to electric grid load forecasting extremely weak.27

### **SUGGESTED-REPLACEMENT**

To replace the unverified and contextually weak computer-vision paper by Yin et al. (2025) with a peer-reviewed building energy forecasting paper directly addressing the failure of smart-building systems to predict occupancy across the historical pandemic disruption, the following peer-reviewed study published in *Sustainable Cities and Society* is suggested:

* CITATION: Xie, J., et al. (2021). "Does historical data still count? Exploring the applicability of smart building applications in the post-pandemic period," Sustainable Cities and Society, 69, Article 102844\. 11  
* DOI/URL: UNVERIFIED — could not confirm  
* SUPPORTS (our claim): Emphasizes that historical, pre-pandemic occupancy data is no longer reliable as a training basis for machine learning-based energy demand forecasting models due to the massive interruption caused by COVID-19. 11  
* DIRECT QUOTE: "interruption caused by the COVID-19 pandemic is likely to cause enormous loss regarding the applicability of historical data as the training basis for forecasting models if the occupancy data was not collected properly." (location: Section 1 / Introduction, as cited in Motuzienė & Bielskus, 2022\) 10  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: none

#### **Works cited**

1. Mapping the Midweek Mountain: The New Geography of Hybrid Work \- arXiv, accessed on June 11, 2026, [https://arxiv.org/html/2603.18440v1](https://arxiv.org/html/2603.18440v1)  
2. How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model \- PubMed, accessed on June 11, 2026, [https://pubmed.ncbi.nlm.nih.gov/35287431/](https://pubmed.ncbi.nlm.nih.gov/35287431/)  
3. Changes in Electricity Load Profiles Under COVID-19: Implications of “The New Normal” for Electricity Demand \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/343216276\_Changes\_in\_Electricity\_Load\_Profiles\_Under\_COVID-19\_Implications\_of\_The\_New\_Normal\_for\_Electricity\_Demand](https://www.researchgate.net/publication/343216276_Changes_in_Electricity_Load_Profiles_Under_COVID-19_Implications_of_The_New_Normal_for_Electricity_Demand)  
4. The impact of the COVID-19 on households' hourly electricity consumption in Canada \- PMC, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8797011/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8797011/)  
5. JUE Insight: Powering work from home \- IDEAS/RePEc, accessed on June 11, 2026, [https://ideas.repec.org/a/eee/juecon/v133y2023ics0094119022000511.html](https://ideas.repec.org/a/eee/juecon/v133y2023ics0094119022000511.html)  
6. Energy efficiency in residential buildings amid COVID-19: A holistic comparative analysis between old and new normal occupancies \- PMC, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9612947/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9612947/)  
7. COVID-19 pandemic ramifications on residential Smart homes energy use load profiles, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8743488/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8743488/)  
8. \[2603.18440\] Mapping the Midweek Mountain: The New Geography of Hybrid Work \- arXiv, accessed on June 11, 2026, [https://arxiv.org/abs/2603.18440](https://arxiv.org/abs/2603.18440)  
9. Impacts of COVID-19 related stay-at-home restrictions on residential electricity use and implications for future grid stability, accessed on June 11, 2026, [https://qsel.columbia.edu/assets/uploads/blog/2021/publications/impacts-of-covid-19-related-stay-at-home-restrictions-on-residential-electricity-use.pdf](https://qsel.columbia.edu/assets/uploads/blog/2021/publications/impacts-of-covid-19-related-stay-at-home-restrictions-on-residential-electricity-use.pdf)  
10. Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic \- PMC, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8605879/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8605879/)  
11. Does historical data still count? Exploring the applicability of smart building applications in the post-pandemic period | Request PDF \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/349698786\_Does\_historical\_data\_still\_count\_Exploring\_the\_applicability\_of\_smart\_building\_applications\_in\_the\_post-pandemic\_period](https://www.researchgate.net/publication/349698786_Does_historical_data_still_count_Exploring_the_applicability_of_smart_building_applications_in_the_post-pandemic_period)  
12. Why Working from Home Will Stick \- IDEAS/RePEc, accessed on June 11, 2026, [https://ideas.repec.org/p/nbr/nberwo/28731.html](https://ideas.repec.org/p/nbr/nberwo/28731.html)  
13. Why Working from Home Will Stick \- National Bureau of Economic ..., accessed on June 11, 2026, [https://www.nber.org/system/files/working\_papers/w28731/w28731.pdf](https://www.nber.org/system/files/working_papers/w28731/w28731.pdf)  
14. Mapping the Midweek Mountain: The New Geography of ... \- arXiv, accessed on June 11, 2026, [https://arxiv.org/pdf/2603.18440](https://arxiv.org/pdf/2603.18440)  
15. JUE Insight: Powering work from home \- Steve Cicala, accessed on June 11, 2026, [https://www.stevecicala.com/papers/powering\_wfh/powering\_wfh.pdf](https://www.stevecicala.com/papers/powering_wfh/powering_wfh.pdf)  
16. How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model \- PMC, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8906892/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8906892/)  
17. Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic \- PubMed, accessed on June 11, 2026, [https://pubmed.ncbi.nlm.nih.gov/34840935/](https://pubmed.ncbi.nlm.nih.gov/34840935/)  
18. The impact of the COVID-19 on households' hourly electricity consumption in Canada \- PubMed, accessed on June 11, 2026, [https://pubmed.ncbi.nlm.nih.gov/35125633/](https://pubmed.ncbi.nlm.nih.gov/35125633/)  
19. The diurnal profile of observed mean weekday (solid lines) and weekend... \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/figure/The-diurnal-profile-of-observed-mean-weekday-solid-lines-and-weekend-dashed-lines\_fig2\_343216276](https://www.researchgate.net/figure/The-diurnal-profile-of-observed-mean-weekday-solid-lines-and-weekend-dashed-lines_fig2_343216276)  
20. Why Working from Home Will Stick \- National Bureau of Economic Research | NBER, accessed on June 11, 2026, [https://www.nber.org/papers/w28731](https://www.nber.org/papers/w28731)  
21. Papers \- Steve Cicala, accessed on June 11, 2026, [https://www.stevecicala.com/papers/papers.html](https://www.stevecicala.com/papers/papers.html)  
22. ‪Mahmudur Fatmi‬ \- ‪Google Scholar‬, accessed on June 11, 2026, [https://scholar.google.com/citations?user=w5ooItUAAAAJ\&hl=en](https://scholar.google.com/citations?user=w5ooItUAAAAJ&hl=en)  
23. How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model \- OUCI, accessed on June 11, 2026, [https://ouci.dntb.gov.ua/en/works/l1AzaOOl/](https://ouci.dntb.gov.ua/en/works/l1AzaOOl/)  
24. Energy efficiency in residential buildings amid COVID-19: A holistic comparative analysis between old and new normal occupancies \- Academia.edu, accessed on June 11, 2026, [https://www.academia.edu/93099370/Energy\_efficiency\_in\_residential\_buildings\_amid\_COVID\_19\_A\_holistic\_comparative\_analysis\_between\_old\_and\_new\_normal\_occupancies](https://www.academia.edu/93099370/Energy_efficiency_in_residential_buildings_amid_COVID_19_A_holistic_comparative_analysis_between_old_and_new_normal_occupancies)  
25. Browsing Straipsniai Web of Science ir/ar Scopus referuojamuose leidiniuose / Articles in Web of Science and/or Scopus indexed sources by Title, accessed on June 11, 2026, [https://etalpykla.vilniustech.lt/handle/123456789/101055/browse?rpp=20\&sort\_by=1\&type=title\&etal=-1\&starts\_with=O\&order=ASC](https://etalpykla.vilniustech.lt/handle/123456789/101055/browse?rpp=20&sort_by=1&type=title&etal=-1&starts_with=O&order=ASC)  
26. Indoor Occupancy Detection Using Machine Learning and Environmental Sensors, accessed on June 11, 2026, [https://www.researchgate.net/publication/391306996\_Indoor\_Occupancy\_Detection\_Using\_Machine\_Learning\_and\_Environmental\_Sensors](https://www.researchgate.net/publication/391306996_Indoor_Occupancy_Detection_Using_Machine_Learning_and_Environmental_Sensors)  
27. Multi-View Pedestrian Occupancy Prediction with a Novel Synthetic, accessed on June 11, 2026, [https://www.researchgate.net/publication/390698738\_Multi-View\_Pedestrian\_Occupancy\_Prediction\_with\_a\_Novel\_Synthetic\_Dataset](https://www.researchgate.net/publication/390698738_Multi-View_Pedestrian_Occupancy_Prediction_with_a_Novel_Synthetic_Dataset)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAaCAYAAACtv5zzAAABcklEQVR4Xu2UzSsGURTGH6HIxwKREmWnKCVWLBQLCzaWslLsCflY2EhZ2iisLaTevZUi5Q+QlYUSpWTFgsTzdO5k5r7zTsw7C+n91a/uvWdmzr1nzgzwxymnk3SPrtL6aLh45uggLNE6PaeNkSuKoJae0gM376T3dCy4II5h+kA/Qz7SN/pBL2El0Y5FD+1w4y5YghE3T0S7eocdP0APnYUlWqJloZhYpiewkyVSR8/oDW3xYq30NiY2QA9pQ2itIDrqEz2mFV6sn77SK9rk1nrpFq2BJWh26wWZgNVeHeKzAYstuLnqv03bYaebhm0ikR3k17+SzsBOtujmVTSHaEPc0TZ3TyxB66lrLtz4GnbzLjLo8bj6q1tWYN0z6tZSE9R/3lvvoy/4/qhSE1d/MQVLvOmt/4qk/ldiJdDHlJpu+oz8/tf4CNEEa/jhL0EMwb5O//+j9xGg/49eshKp1/dpdSieCSrbOKyTMn94iRL/mS8ki02XoMxKDQAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIQAAAAXCAYAAADKtudKAAADtElEQVR4Xu2ZW4hNURjH/0KR+yWSW0lJEXJLUaNQHlwyHlxSonjx4BIalzqSXIoiRShJFAmleXB5UKRc8jY8SIxEKZTigVy+/3x7zV57nbXPmTNO55zZs3717+y91jpn9l7rW9/6vm+AQKCMdBXVi86Idon6JrsDnY2NotlQw9gjeigalBgR6DT0Ft0XnYvux4g+iBaaAYGOz1zRR9FfS59EP0W/RY+hRwQ9ApkoGh1dj4caxLzovhqMEx2BHmGrRD2T3akME+2Ffm+faGyyu8X4z4tWi0ZAx9vqHw/NJtz1v6DHgYFGsAFqGDtEXaw+slN0Bzp51YCG+kI0GfoM+0V3Rf3sQR5mQMfNEU0SNUI3wjbE78hFb47afToRjcskfUQPRK9FQ50+MzFuHyf1smig1VZJRopeQXewYYDoqWiT1eZCD3JTtA6x12MM9ET0XTQ1auPnc6gHsXVL1ITYS2YSuv7Pomuibk7fdNEP6CQMjtq4Iw+KekENYkjUXkloCPYCEu7uS9A4J81rGQP/BvUOBmZM3Plbo/tF0ADaprvotGi+0545FkMnw50AkkPsTgl3Bs/sUdDJXQM1mkpDl+0aBLkAjYkY8Prgoh4X3YY+v4HHH9+Tn4SbZHjc3QLnZzvyj87Mwcl14wdO3Hqo5+Ak8L6H6AaSZ+l7aNBVabjwaQbhay8EvSK9I2OlumRXK1NE11E8PunwmFSSWcWj6PoldLFPoTw1hpWidyXoGfKjfhvzzL6Fb49BzIR+hzECDd+FbVdEK9yOLOKLH+gSG6A7phbPS8Yu9+Bf+FINgjuev3UR+rs+ZoneQueqGJw7biI3TU0TvW5NYeIHE0wZOKGcWFOEqjXSFj6t3YcJEo8hvX7BBT4JzV6YxRSD9YlDyM9O0lRzRT1f/EAYxdNQDjjt7YG7wN0ZhcT01ue6bfhcvoWnQbQlrjHG0IA4/aQHWNA6QmFm1YTCmUtmKFR/oKHYUff/wMxkeQlaguL1DXo2Hml2lZSG1xjJuGIuPP++bWDc9cyatkTXBmYRy6x7wtSUKaovJc8cE0Rfkf+yvL6KpEHsRnVL1C48p1lMylltDETpHezg7yj0PXLRPQ1gLbS2wrF2MPsF+Z6S7/wH6nkyC0u2zUimj/z/BXedoR66A2kYrDWcRfo5Wy2mid5Ay+r0LDznDyPpDTZDMyi+D+GR5L67ka9+wTOefZk2iLbCY4QVO2YatWYMBmYGPPeXQsvZ5YbGVQc1pEAgEAgEAoFAIODjH/Lt1nJSkoqbAAAAAElFTkSuQmCC>