# **Long-Term Changes in Time Use and Impacts on Residential Energy Demand**

**Conference:** ASim2024, The 5th Asia Conference of the IBPSA

**Date:** December ![][image1], 2024

**Location:** Osaka, Japan

**Paper ID / Page Range:** 1321 – 1328

### **Authors**

* **R. Yin¹**\* *(Corresponding Author: rumeng@ue.see.eng.osaka-u.ac.jp)*  
* **Y. Yamaguchi¹**  
* **A. M. Zajch¹**  
* **H. Uchida¹**  
* **Y. Shimoda¹**

¹ *Graduate School of Engineering, Osaka University, Osaka, Japan.*

## **Abstract**

Occupants' activity patterns significantly impact energy demand in residential buildings, and these patterns are typically modeled using time use data. Though previous studies have identified long-term changes in activity patterns across different demographics, such changes have often been ignored in occupant behavior models.

This study used Japanese time use survey data from 2001 to 2021 to analyze long-term temporal changes in activity patterns. Using a hierarchical approach, we developed a logistic regression model considering various demographic and household characteristics. Our findings reveal that total time spent on sleep, work, and housework decreased across all demographic segments in 2021, indicating a significant shift in activity patterns. We observed a decrease in nighttime sleep probability and changes in housework and work time allocations. These results underscore the importance of incorporating long-term changes in occupant behavior models to enhance their accuracy and applicability. Future research can combine with machine learning methods and synthetic populations to explore how shifts in activity patterns influence energy demand for urban-scale regions.

**Keywords:** *Occupant behavior model, Time-use data, Residential energy demand, Logistics regression model, Long-term change*

## **Introduction**

Occupant behavior (OB) significantly influences the spatial and temporal patterns of residential energy demand. OB models, which quantify occupants' energy needs by modeling their occupancy and activities, help capture the heterogeneity and stochastic nature of energy demand (Liu et al. 2024). However, exploring OB uncertainty at an urban scale remains challenging due to data complexity and availability issues.

Time-inhomogeneous Markov Chain Monte Carlo models trained by data from time-use surveys (TUS) are the most popular method to estimate occupants' occupancy and activity. Richardson et al. used the TUS in the United Kingdom to generate occupancy schedules in 2008 and occupant activity profiles in 2010\. Widén and Wäckelgård (2010) constructed a stochastic model to generate activity sequences of household members and domestic electricity demand.

Walker (2014) highlighted that occupants' daily practices and activities result in temporality for change, rhythm, and synchronization in energy demand, making it necessary to understand how temporal patterns affect energy demand at different timescales. Anderson (2016) used TUS data from 1985 and 2005 to explore the temporal change in laundry practices in the United Kingdom over the last 20 years. Subsequently, Anderson and Torriti (2018) analyzed four versions of TUS data from 1974 to 2014 in the UK to examine changes in temporal patterns of activities across 40 years. Their results showed that long-term changes in the timing and location of work, travel, dining, media use, and social activities influenced electricity demand. For instance, a substantial reduction in food-related activities at breakfast, with an implied reduction in electricity demand, was demonstrated in this research.

Sekar et al. (2018) compared changes in the duration of different activities using the American TUS from 2003 to 2012\. They found that Americans spent more time at home in 2012, and less time traveling or in non-residential buildings, compared to 2003\. These shifts in time use and lifestyle lead to changes in daily time allocation and interdependent changes in energy consumption across multiple sectors. It is crucial to explore the relationship between shifts in temporal patterns of occupancy and activity with residential energy demand from a longer-term timescale (e.g., more than 10 or 20 years).

On the other hand, the COVID-19 pandemic further altered lifestyles, with significant reductions in commuting and increases in working from home (Roberto et al. 2023; Wu et al. 2024). These changes impact greenhouse gas emissions and highlight the need for updated decarbonization strategies.

The literature review revealed that changes in lifestyles manifest as changes in time use and energy consumption over longer-term timescales. However, the effect of demographics on these temporal trends has not yet been fully revealed. The scope of this work is to identify long-term changes in time use of people with different demographic characteristics. This will assist subsequent analysis by interpreting changes in time use as changes in home appliance use and resultant changes in residential energy demand for building stock. Based on this background, this paper analyzed changes in time use in Japan between 2001 and 2021 based on the Japanese Time Use Survey across five survey years.

## **Method**

As discussed in previous studies (Aguiar and Hurst, 2003; Kuroda, 2010), changes in demographics and lifestyles influence the aggregated allocation of time use. The demographic compositional factor and the time use factor are regarded as the two main forces influencing the aggregation of time use on a long-term scale.

* **Demographic compositional factors** refer to changes in the distribution of the population across different demographic characteristics. For instance, an aging society results in a higher proportion of elderly individuals and fewer younger people. Typically, people spend more time working when they are younger and gradually reduce their working hours as they age, leading to shifts in aggregated time use.  
* **Time use factors** pertain to changes in time use patterns *within* each demographic group. Due to rapid technological development, students today spend more time using phones or laptops compared to students in surveys conducted 20 years prior.

This study focuses on long-term changes in time use due to the **time use factor**.

\+-----------------------------------------------------------------------------------+  
|                                1\. Data Preparation                                |  
|  \- STULA datasets from 2001, 2006, 2011, 2016, and 2021\.                         |  
|  \- Segment STULA data into six distinct demographic categories (CL1 to CL6).       |  
|  \- Select demographic conditions to use as predictor variables.                   |  
\+-----------------------------------------------------------------------------------+  
                                         │  
                                         ▼  
\+-----------------------------------------------------------------------------------+  
|                           2\. Logistic Regression Analysis                         |  
|  \- Perform binary logistic regression analysis for each 15-minute interval.       |  
|  \- Calculate Activity Undertaken Probability (AUP) for target activities.          |  
\+-----------------------------------------------------------------------------------+  
                                         │  
                                         ▼  
\+-----------------------------------------------------------------------------------+  
|                        3\. Quantification of Time Use Patterns                     |  
|  \- Compare activity patterns of typical demographic groups across the five years.  |  
|  \- Analyze AUP distribution throughout the day and aggregated daily time use.     |  
\+-----------------------------------------------------------------------------------+

*Figure 1\. Flowchart of the research process.*

In this study, long-term changes in the time use of the Japanese population were analyzed through logistic regression based on Japanese TUS data spanning the past 20 years. There are three main components of the study, as illustrated in Figure 1:

1. **Data Preparation:** The STULA was divided into six segments based on age, gender, and employment/study status. Regression input data was then prepared using selected demographic conditions as predictor variables.  
2. **Logistic Regression Analysis:** Regression models were developed for Activity Undertaken Probability (AUP), representing the likelihood of a specific activity occurring at a given time of day for selected activities.  
3. **Quantification:** Time-use changes for six typical demographic groups were estimated based on the regression models to quantify patterns across different years.

### **Data Preparation**

The Survey on Time Use and Leisure Activities (STULA) is a comprehensive cross-sectional survey conducted by the Ministry of Internal Affairs and Communications (MIAC) of Japan every five years since 1976\. The 2021 survey is the tenth and latest iteration.

STULA samples were selected through a two-stage stratified sampling method, where the primary sampling unit is the Enumeration Districts of the Population Census and the secondary sampling unit is the household. The survey covers two consecutive days within a nine-day period during October in the survey years from 2001 to 2021\. The STULA collected diaries with a 15-minute time resolution.

Since 2001, the STULA has administered two formats of diaries separately: a pre-coded method (Diary A) and an after-coded method (Diary B).

* **Diary A:** Respondents fill in their activity for each 15-minute increment using 20 pre-defined categories. The sample size ranges from approximately 70,000 to 100,000 households (about 200,000 to 270,000 members).  
* **Diary B:** Respondents record their activities freely with locations. The sample size is approximately 4,000 households (about 20,000 members).

This study utilized **Diary A** data.

### **Segmentation**

We employed a hierarchical approach in which regression models were developed based on the STULA for the six groups listed in Table 1, segmented by age, gender, and employment status.

### **Table 1: Segmentation and its attribute and condition**

| Segmentation | Attribute and Condition |
| :---- | :---- |
| **CL1: Student** | Students younger than 20 studying at primary school, junior high, high school, and university/college. |
| **CL2: Adult male** | Male aged 20 to 59 with a full-time or part-time job. |
| **CL3: Working female** | Female aged 20 to 59 with a full-time or part-time job. |
| **CL4: Housewife** | Female aged 20 to 59 only doing housework. |
| **CL5: Elder male** | Male aged over 60\. |
| **CL6: Elder female** | Female aged over 60\. |

### **Predictor Variables**

Given the variation in survey content across different years of the STULA, we selected 35 demographic variables (listed in Table 2\) as binary predictor variables. These variables were chosen based on attributes and conditions across the six classifications.

For the student segment, only gender, education, household composition, and city size were included as predictor variables. For the other five segments, age-related variables were restricted according to the segment criteria. All selected variables were consistently available across all STULA survey years (variables such as house ownership and weekly commuting time were excluded due to inconsistencies).

The variables marked with an asterisk (![][image2]) in Table 2 serve as reference demographic categories and were excluded from the regression models, as the regression coefficients of the remaining variables indicate their impact relative to these baseline reference conditions.

### **Table 2: List of extracted predictor variables from STULA**

| Index | Variables / Categories |
| :---- | :---- |
| **1\. Gender** | (1) Male\*, (2) Female |
| **2\. Age** | (1) 10-19, (2) 20-29, (3) 30-44\*, (4) 45-59, (5) 60-74, (6) Older than 75 |
| **3\. Education** | (1) Primary school, (2) Secondary school, (3) High school, (4) College/University/Graduate school\*, (5) Other |
| **4\. Occupation** | (1) Full-time job\*, (2) Part-time job, (3) Housework, (5) Other |
| **5\. Weekly work time** | (1) Less than 15 hours, (2) 15 to 34 hours, (3) 35 to 39 hours, (4) 40 to 48 hours\*, (5) 49 to 59 hours, (6) Over 60 hours |
| **6\. Household composition** | (1) Couple without children, (2) Couple with children\*, (3) Couple with parents, (4) Single parent with children, (5) Three generations, (6) Single, (7) Elder couple, (8) Other |
| **7\. City size** | (1) Urban\*, (2) Non-urban |
| **8\. Preschool child** | (1) Have preschool children, (2) Do not have preschool children\* |

*Note: Asterisk ($*$) denotes the reference category.\*

### **Logistic Regression Analysis**

Binary logistic regression was performed to determine the Activity Undertaken Probability (AUP) for three representative activities (sleep, work, and housework) across 96 time intervals in a day. The AUP is represented as ![][image3] at time ![][image4] (where ![][image5] corresponding to 15-minute intervals), yielding regression coefficients associated with the ![][image6] predictor variables of each survey year:

![][image7]Where:

* ![][image8] is the intercept at time ![][image4].  
* ![][image9] is the partial regression coefficient of predictor variable ![][image10] (![][image11]) at time ![][image4].

### **Quantification of Time Use Pattern**

We applied typical values listed in Table 3 to the developed regression models to quantify the long-term changes in time use for these activities from 2001 to 2021 across different demographic segments. The AUPs over a 24-hour period and the total daily time spent on activities were used as core evaluation indicators.

### **Table 3: Typical demographic conditions for each segment**

| Classification | Typical Demographic Conditions |
| :---- | :---- |
| **Student** | Male student studying at a secondary school, living with parents in an urban area. |
| **Working male** | Male aged 30 to 44 with a full-time job, living in a household of a couple with children, without preschool children, in an urban area. |
| **Working female** | Female aged 30 to 44 with a full-time job, living in a household of a couple with children, without preschool children, in an urban area. |
| **Housewife** | Female aged 30 to 44 without a job, living in a household with children and preschool children, in an urban area. |
| **Elder male** | Male aged 60 to 74, living in an elder-couple household in an urban area. |
| **Elder female** | Female aged 60 to 74, living in an elder-couple household in an urban area. |

## **Results**

### **Comparison of Distribution of AUP**

Using the logistic regression models, AUPs for sleep, work, and housework were calculated in 15-minute intervals over a 24-hour period. Figure 2 illustrates the quantified AUP curves for the typical conditions specified in Table 3\.

\[Figure 2 Placeholder: Comparison of AUP curves of three activities (housework, work, and sleep)  
 across six demographic profiles from 2001 to 2021\]

#### **Key Findings from AUP Distribution (Figure 2):**

* **Nighttime Sleep Decline in 2021:** As represented by the bold lines in the figures, the AUP of sleeping during nighttime hours significantly declined in 2021\.  
* **Students:** Students maintained relatively stable activity patterns across the survey years, with the exception of a notable decline in the AUP for nighttime sleep.  
* **Elderly Segments:** Prior to 2021, elderly segments (both male and female) had higher AUPs for nighttime sleep, hovering around 80%. However, in 2021, all six segments showed a nearly uniform drop in sleep probability at 00:00, falling below 60%.  
* **Housework Allocation Shifts:** Females spent less time on housework, while working males increased their time spent on housework. For example, at 19:00, the AUP for housework among working females decreased from 34% (2001) to 27% (2021), while for working males, it rose from 10% (2001) to 14% (2021).  
* **Work Allocations:** Females consistently exhibited lower AUPs for work compared to males after 13:00. In 2021, both working male and working female segments showed an overall decreased AUP for work.

#### **Analysis of Regression Coefficients (RCs):**

To identify the key drivers behind these long-term shifts, we analyzed the regression coefficients (RCs). Focusing on nighttime sleep, we observed a significant increase in the impact of city size on nighttime sleep in 2021:

* The RC for sleeping at 3:00 AM rose from **0.32** (2001) to **3.32** (2021) for students.  
* The RC rose from **0.29** (2001) to **2.74** (2021) for working females.  
* Conversely, the impact of having preschool children on sleep patterns decreased in 2021\.  
* Prior to 2016, the RC values remained relatively stable, with major shifts occurring exclusively in the 2021 survey year.

### **Comparison of Total Time Use Per Day**

Figure 3 presents the comparison of total aggregated time use for the three activities quantified under typical conditions.

\[Figure 3 Placeholder: Bar Chart comparing aggregated time use (Sleep, Work, Housework)   
 for the six demographic segments across five survey years (2001, 2006, 2011, 2016, 2021)\]

Prior to 2021, the cumulative daily time allocated to these three activities showed minor variations. However, 2021 marked a stark, widespread decrease in total time use across all segments, primarily driven by a substantial reduction in sleep duration.

### **Table 4: Total daily duration of sleep, work, and housework (Hours/Day)**

| Segment | 2001 (Hours) | 2021 (Hours) | Absolute Change (Hours) | Primary Driver |
| :---- | :---- | :---- | :---- | :---- |
| **Student** | 8.9 | 6.5 | \-2.4 | Sleep reduction |
| **Working Male** | 17.2 | 15.3 | \-1.9 | Sleep reduction, Work reduction |
| **Working Female** | 19.5 | 16.1 | \-3.4 | Sleep reduction, Housework reduction |
| **Housewife** | 15.5 | 13.1 | \-2.4 | Sleep reduction, Housework reduction |
| **Elder Male** | 14.4 | 11.6 | \-2.8 | Sleep reduction |
| **Elder Female** | 15.7 | 12.7 | \-3.0 | Sleep reduction, Housework reduction |

For all female groups, the time spent on housework decreased gradually over the survey years. The behavior changes within the elderly segment exhibited minimal variation across survey years prior to 2021\.

## **Discussion**

The comparison between 2001 and 2021 reveals notable shifts in sleep patterns. Logistic regression results indicated a significant decrease in the AUP for sleep during nighttime hours in 2021, which aligns with the reduction in total sleep time and AUP observed in the original TUS data.

The decline in nighttime sleep probability and the delayed onset of sleep observed in 2021 can be attributed to multiple factors, primarily:

1. **Digital Media Consumption:** Increasing usage of digital media near bedtime.  
2. **COVID-19 Pandemic:** The residual and direct impacts of COVID-19 lockdowns (Cellini et al., 2020), which altered daily schedules and sleeping routines.

Additionally, we observed an increase in housework time among working males and a concurrent decline among females. This trend aligns with:

* **Social Norms:** Growing societal emphasis on gender equality.  
* **Automation Technologies:** The development of home automation technology, which has the potential to save more than 50% of the time spent on housework activities (Hertog et al., 2023).

### **Implications for Residential Energy Consumption**

These shifts in daily activity patterns have broad implications for residential energy consumption. Changes in sleep and housework duration directly affect when and how household appliances are used, shifting the timing and peak of overall energy demand. As urban residents increasingly rely on electronic devices and automated systems, residential building energy consumption profiles are expected to become more dynamic and demand-intensive during late-night hours.

### **Future Work**

Future research will expand to a comprehensive analysis of all activities, integrating machine learning methods to capture complex, non-linear relationships between demographic attributes and activity patterns. Additionally, incorporating a synthetic population approach as input variables could facilitate the examination of time-use patterns across broader, urban-scale populations. This would enhance our understanding of behavior shifts and temporal variations, providing deeper insights for energy demand forecasting.

## **Conclusion**

This study analyzed long-term changes in time use and activity patterns from 2001 to 2021 using the Japanese TUS and a logistic regression model, focusing on sleep, housework, and work as representative activities.

Our findings indicate:

* **A major behavioral shift occurred in 2021**, characterized by a sharp decline in nighttime sleep duration across all segments.  
* **City size emerged as an increasingly dominant factor** affecting nighttime sleep in 2021, as identified by logistic regression coefficient shifts.  
* **A reallocation of household labor** occurred, with women spending less time on housework while working men spent gradually more.  
* **Total work hours shortened** in 2021\.

These findings emphasize the powerful influence of technological advancements and societal changes on daily routines. Incorporating these long-term trends is essential for improving the accuracy of future residential energy consumption models. Future work will integrate machine learning and synthetic populations to explore urban-scale behaviors and support progressive policies in urban planning and energy system design.

## **Acknowledgements**

This work was supported by JSPS KAKENHI Grant Number 23K26260.

## **References**

1. **Liu Z, Dou Z, Chen H, Zhang C, Wang S, Wu Y, et al.** Exploring the impacts of heterogeneity and stochasticity in air-conditioning behavior on urban building energy models. *Sustainable Cities and Society* 2024;103:105285. [https://doi.org/10.1016/j.scs.2024.105285](https://doi.org/10.1016/j.scs.2024.105285).  
2. **Richardson I, Thomson M, Infield D.** A high-resolution domestic building occupancy model for energy demand simulations. *Energy and Buildings* 2008;40:1560-6. [https://doi.org/10.1016/j.enbuild.2008.02.006](https://doi.org/10.1016/j.enbuild.2008.02.006).  
3. **Richardson I, Thomson M, Infield D, Clifford C.** Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings* 2010;42:1878-87. [https://doi.org/10.1016/j.enbuild.2010.05.023](https://doi.org/10.1016/j.enbuild.2010.05.023).  
4. **Walker G.** The dynamics of energy demand: Change, rhythm and synchronicity. *Energy Research & Social Science* 2014;1:49-55. [https://doi.org/10.1016/j.erss.2014.03.012](https://doi.org/10.1016/j.erss.2014.03.012).  
5. **Anderson B.** Laundry, energy and time: Insights from 20 years of time-use diary data in the United Kingdom. *Energy Research & Social Science* 2016;22:125-36. [https://doi.org/10.1016/j.erss.2016.09.004](https://doi.org/10.1016/j.erss.2016.09.004).  
6. **Anderson B, Torriti J.** Explaining shifts in UK electricity demand using time use data from 1974 to 2014\. *Energy Policy* 2018;123:544-57. [https://doi.org/10.1016/j.enpol.2018.09.025](https://doi.org/10.1016/j.enpol.2018.09.025).  
7. **Sekar A, Williams E, Chen R.** Changes in Time Use and Their Effect on Energy Consumption in the United States. *Joule* 2018;2:521-36. [https://doi.org/10.1016/j.joule.2018.01.003](https://doi.org/10.1016/j.joule.2018.01.003).  
8. **Roberto R, Zini A, Felici B, Rao M, Noussan M.** Potential Benefits of Remote Working on Urban Mobility and Related Environmental Impacts: Results from a Case Study in Italy. *Applied Sciences (Switzerland)* 2023;13. [https://doi.org/10.3390/app13010607](https://doi.org/10.3390/app13010607).  
9. **Wu H, Chang Y, Chen Y.** Greenhouse gas emissions under work from home vs. office: An activity-based individual-level accounting model. *Applied Energy* 2024;353:122167. [https://doi.org/10.1016/j.apenergy.2023.122167](https://doi.org/10.1016/j.apenergy.2023.122167).  
10. **Aguiar M, Hurst E.** *NBER WORKING PAPER SERIES* n.d.  
11. **Kuroda S.** Do Japanese Work Shorter Hours than before? Measuring trends in market work and leisure using 1976-2006 Japanese time-use survey. *Journal of the Japanese and International Economies* 2010;24:481-502. [https://doi.org/10.1016/j.jjie.2010.05.001](https://doi.org/10.1016/j.jjie.2010.05.001).

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFUAAAAZCAYAAABAb2JNAAADnElEQVR4Xu1YPWgUQRjdkAiK/8p5JPcz9ydnRFE4LRQLRREslICCIYqNiKIpRDFqKkEsIjamUhHEIukMSgyISggGLBIhKhhFBTEEUtgasAnxvew3ybi3e7l457Ee++AxM2++ndnv7ezO3FlWAP8gkUhsUEp9BAdCodAyZ381ALndAKfi8fhBZ1+5UIMJzpkGYrIc+LhaTI3FYtuR4x5Tw+J5+M9MTSaTYQx+p5pNhaGtTgNLMjUajS7BoC3gPfAmBtoIuYZ9qKeg9YM/UH+A8qToOdR78YT3o+wGb6VSqZV/DFxBJGw0O3UNLIwsc5McW5izdNWhfRacxPXPwdsciB1i6nGwDf1PUe6dG7EAaAQu6MEFJ1DWY/ItGOwV6hetOWPzVqVoY+AuthF/H7yg+ysBzNcohvChT9EEZwyBvsPgKPq3MgfUr4MvzEUgBuatVMR153K5ReLLEN9aM8YVuKgVbDc1rL5N0EbAJNtepqL/LVgv7cuk7q8EaCoSbUK5Exx3M7WhoSGGvi/gMa3hPlejPczcteZlqs6JeYIDOt+C4IVghyWrkpABRvh02DZNxWuzHlKdH0zVkPv97mYqzQQneb+GzI23iybphaJNRX5r0un0OkNbuKnKPjpMg53hcHgpNQx2FO0+PaFpKvrOsPyPTO10MXXGMOgT0FO6TVMZh/puQ1u4qViNChd+FmO/KtvkQeo6hk8OWj8muQI2gwm0H4G/5Ka5yX0SHjDHrwQkYVdTxTwvU2d1lKfQ7oF+PhKJRFGeRnsCfMP80L7LeJbgKnMsVyC4EYOOKdvYaU6YyWRWOMJqs9nscofmC3iZKpsSV9e8phJ8U7kpmXF/BT4VDD7IJxO3TwCTYu5r9K11xpcKPmUxYV4WewaW+DxTaRL0l6pIU8sCOZ/2mt9Cmoz2E2UbO7s7lgNIZDHGvKTss2IxnDkTzwflYSrhZZ6XXjK4u8v3tNHUaTb0Z2436UcUMlXZe0SeeWLqOBeRqZcMToSBR+OyA5qA3g52OnU/opCpOHMfUvYfI/u0Jm9MH8m6GV8y5IjEn2ZXLeOcik0qpOwP/A4j3LfQpoJdlpEHwX0B+Q2B17SGNzHDVZoo8LO2JMgE72iusg/KXKEfuGlZjhv0G7j6aA5XopKTC/gTubxHXpt1HFbrNujfEN8GHkF9GDEdZdnpC6CWnwJOyD9I9I+AagJzYm4ws4k/XZ39AQIECBAgQIAAAXyD307zNtT6geksAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAvUlEQVR4XmNgGAVUBwoKChzy8vJzZGVlbdHlwMDY2JgVSDGLioryABUekJOT8wWJa2lpsQEpRrAiEAcosQGoYI+MjIwqkF4ONNkCSCcB8TsU06WlpYWBgt1A/ASIHwLxbSA+o6ioaAc3EQZUVFT4gCa3AxX8A+IbQGyJoYhYhYxABWVAiW9Q6+cCcTbIeqBbDwGdJQNXCBSIALkHZCpQwX4g9oTakAdkSyIZCgHowYMPMAIVaoJMQ5cYBdQBAFM0LEppTcJlAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAABbUlEQVR4Xu2SO0sDURCFs/gA8Qm6rOxmsw8DIWkXBcFSBBuLVIKgVtrbCGohiGAjqCCB4D8wbQortfMH2GshWkl+gEj8Jt4lezdb2NjlwOFm5syZO3M3uVwfffwRxWJxwvO8Vdu2XYktyxp1XXelUChEhAOp8l7k8/kRGlzDA/iO8YyzATfUWY+iaCjt04BpmcJDWIaf8EYai8Y088QtqUn7NPi+vx0EwQKGNQzfSQO/l8h9wT2VMmTVWO8BhafwlSmcOMcFu+TasKpqFmHTNM2xrlOBG0PED879OEccwDdyNaaco+El8Qt8kMkqlcpwsofsLqu0KTxWKYP4BD6zqicJvtwM8T0sd50JeL+rtOATvOX2R84GTWfjGnkfeFcqlcaT3g5kPzViU76K4zjTWTur97lK5zvIeo8MDMpksCp/SBpuaSrmHcQ25ybilCZ2YaBfUHcOj8IwnNRUkvWYNFnXRB2Geg8jLfTxT/gBVzVRSk80wz4AAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAcCAYAAACtQ6WLAAAAs0lEQVR4XmNgGMxAXl4+CYh3S0tLC6NIKCgocAAltoIwiE28JNAoGaDEEyBuhQuKioryAAUk5eTkQoH0b6CuCEVFRXFjY2NWkHHxQMFZQHwfiH8C8VIgniQrK6sM1k26fTAAtM8FKPELRKPLgTxfBcTPgZJKKBJI9u0RFxfnBrkSyO4CWcUgJSUlAuRchdkHpIOAGgqATEYQnxHIaQQK3gHSK0FssB+RAVBQAIRRBEcBAwMABtcu+9nC0QoAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF0AAAAaCAYAAADVLFAXAAADlklEQVR4Xu2XXUgVQRTH92KRUfRtkt57934RREXEJUIIibDIoBDpCyIDe6i3IqlIKJQIwqfwoSgK6SEikHopiPLByAepyAoksCSKrKcKgoQUtN9xZ2kd9+q9xt1bNH/4szNnzsyc/e/MmVnLMjAwMDAwyCNs214biUS26PaAEYrFYuuJpRVejMfjlWLTnQSpVGpeNBo9gt8V2Ch13Scj6FAPH5aXly/W2/INeUECP8H8T+Eo5ZO6T1BIp9MziacJPgmHw6uJZwXxPKLebGnC07YJvqG9jucyeBzept9sr58vGLAY53tCKevt+YYSfTvzb4M/Cik689fCIWLa6tqIZwO2L7DCY1tJfQC/PVJnN5RS74fv5QO4fhnB6g7j+BGe09uCBC+SLqTonsUnMaRdu4ioxGxVphmUr8LesrKyJcoWor4P1ku7sk1ESUnJXBmQCXbxHGbSvfLFZIvpvkGg0KIrPTonEb1T+cRtZ5G2k8NnJZPJpSot++b9cUDkA7ZzALyDP+EN2MpBltR9g8A/IHq/LEraqiiPwLtoeJnnMXgTdknW8I7pi1zzOX6nmfRDDrzPwbJIH8cP0xFddiV9GuA3OETfC5luECKY7Gbd7gXtTYwzyMJb59qiTk4fVsJLZpDzZ1TFOvZxVBx36P9APt7vEX3wt+RzwXRE5yUP4d8m7yGkfIYxuvnQKd0XIVfRvlu3e8GHsfHpY9xTVENKTMnfIrIu+riFKnFjG+FZ5RlyIsTBdlbI5I4BIFfR8VsIz+tXNMaoQIxXtG22VJ4VH+wtIrzX1w/0jeHbAQdgD+PsV4K7Ob1aRMfturefEn3qKy9OjfAzjgm9zQ/u4Zst5ZChW5E+jh9yFd127tB1ul2ghOuCPfAafA0brGwOOw0yj+1cGcduL+yGNZS/T0t02Rq2k887SktL56it1DLZYSA/DAy6M1syXrW+EjMhV9El5il+5opkTIkjkUgst7IQXAn6Am1qXBu7Ywe2QVvd0xlrPuVu2G55rocStz1VepE7Jk69tsrnPGuZ7KiVRXD5gCs6bNTbgkJU5Wt0aJK6ErgD+yXLIzDth7H1oWFE6rkcpCGcmnF+y/OWlAtxR5cXIIZP8rIefoWPVXoKDOpi8QyehQeljLhtsqu8flIXO+3PY87VW66ML+Ug9vplBJ0WCHX7/wq0KIYbYY27kjMgJGlL0hdiVxZiwRoYGBgYGBgYGBgY/Dl+ARB7J9aMGUZvAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAABDElEQVR4XmNgGAWDBqioqPDJy8t7SklJyYL4xsbGrLKysiZycnK+ioqK4iiKRUVFeRQUFGYCcSNQ0xOgolggvRlIpwHpaiD+CGS7wDUAFXoAcTpQ0Bgo+RWI9ygpKfGD5IBsSSB+CJQrh2sAclKBgppAHATEv4HYESYHFX8LxEVwDUiSk4D4KtAfIjAxoM0RQLGfQENtkNWCAUka1NXVeYESh4F4DZDLAhVmAfKXA/EJmJ/gAJtbgWxFIH4CtKVBRkaGE2hLu7S0tDBMEuxhZKtBcQAU+waMD1Mg2xXIroLJgdzaABS4CDcBokEJKHYHiLcD8TIUZwE1cIAiEC4ABaAYhwYCM7rcKBhYAABalT/yg0+u1wAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABCCAYAAADqrIpKAAAIf0lEQVR4Xu3de4gcVRbH8R4yik9UNCbpTPftnkTjxD9U4oOIIoqCg0Qkig8UXRAf4Cq4sBGSZRWzgfUPQVRQfODqErIsAf/QqGjQEUH/UFBBQZSwKhJBEEFEWGQ3/s7UvUnNSfWjenqmZ3q+H7hU1bn31nRVD/ThVtWtSgUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYL2vXrl1er9fvDSE8p7LT1wMAAExTwnD9+Pj46T4+3xqNxm0+NuzGxsZO03G/qdURfQ8v+HoAAABjicJfN2zYcISvmG9KXM5uNpvBx4ddCGGHjnuFllO+DgAAwJKFT31skJQ8blF52seHVUzUmrVa7WotXxofHz/BtwEAAEvXqBKjpxbCyJqn5OVifbYzfRwAAGBJsaQohLDfx8tQ/0lbrlix4lglWBt8fa8siWw0Gv/2cQAAgCVFydbPSoqu9PFuKUG7XPuYsKcbx8bGjlYCeJ7FfLteaV9vaDHq4wAAAEuC3TOlZO0hHy/LbpZXsrba1rW/u7S9Ocb3zGxZniWD/fiMC4mO6UAsPygh/dYXxb/LtUnlSXUd8fsCAABDTonQjUoQLvLxspRM7K3EUTCt71aZiOuPz2jYg+XLlx+n/UzZ0tctVjqefTEJ2+7r8lS/St/PJi3/F7IkrunbAACAIacE4PNKHy43WvIRV0e0/pmtVKvVU1LiNlsxubnZxxcxO092TAe6nb5EyfUNav+xjwMAgEUi/fj7eCe99PHiCNie1atXn5wfBbNLo/l2s2GJZZijucm036ssGVS5p1arnevr54r+3jkqP8XvoKtLne2e5LWHM+r1+q1hgU3PAgAAIpslXz/UP/h4J+rzm4+VpSRhXOUBFx7VvndXq9Wai/dE+9qr8o2P94P2+0Ru/bl83VyLo2YHtLzA15VhU5+kedvsu7CndX0bAAAwYPrRX1U2oYkjY6X6eOp/u8ozVnxdJRs16mrkqBPtf4clNj4+W5YwpXWbuFbbd+fre5FPALuh9p/ZsbU4hx2p30YlaVts3Z7SjU/V9uW8AwCAPsonbPrBftcSAC2fjpfI9hVdSot9pnx8IbJRo34nbPHNAk+o/BYTpn2+TS9snz7WQf5+tvN9ZSfxGC6M+/il233YiJza/0llm87vY1o+r/KybwcAAPokzBxhswRgZyPOrab1raHg5v/YZ8rHF6L4pGTLhE11H9l0GEVF5+Em396o7iJLWOzeO7uEaPeA+Ta9COUTtun7z+z4Qva0bSnq82gl+87t+9yussu3KaJ2f4tL67dL5cfF8v8AAMCiFH90D17eVALwYnoAwEan6gVvH4h9pnw8iQnEvBb/GZJOCVsvbFRJydpY2tb+t9qom41M2oiktv+Zb6/tjaFgXjm1vy7Ey8KxfJHf1ndxou9TJL5D9ICWVV/Xjk1UnNbVf7PKz3F9hz7bFYdaHpyEeAa1u9n/fxT1BQAAsxTmIGFbSBrZZLwtEzbVXWWJU1EJBaOLRvFnK/FeLzs/lujYVCRa3xTrp1Jb/f2Gtv9jsfXr1x+Z4kVCDyNsxi5ldns5M9FnHV+3bt3xaVt/+yuV7fq4K7V8OF0K1/ZR2v6z2n+bHgSxzxmnXrGpXUYsQVO50/cFAAB9EgouiaYf8lYJW/yx/tDHFyI7htAmYeuF9vmlJWK2rn3v1fZTdh6LEra4/U5okfzlWSLkY50oUVO38tNxqM9kIz5hag8caPt1uzdNsT9o/X3bb769Jb5p3c6nyqUhPimsuhe1j7Wt+gIAgMGwqTe+98ECy1JiMyiWTOiz/urjvbJLnzbqFF8uf/CSpSW5bRK2rt7aUDZhswSrnj3lWfrJzvi3lq1Zs+bUysz+ozquG3Pb1nbCkvS0bcevxTJbj/2Tw/oCAIABslEWH0viiM2kkokHi0bo5pM+x3shu3TXF9rXH30sUd0elQuVtNxvDySEbBTSRi0fVfmLbz9Ltt+3fLCVWq22Jr+t7+WO/HaihHSd9vuwjuEMlUdCNnJ4hZZbfVsv39fXAQCAAdAP8/99zGt1SXU+hew9mrt9vFc6nut8LLFRNxuBS9vp0nJclh4Fa8PuG9uixGilrygSH4SYMVebT+Dy4gjatHQ83d6Xlu8LAAAGLGT3bp3k43n9SthCNsnuh9rXP1Tu0/q2bu+TssRSfS738XmwTH97ow/2g47ny2aXDxnoM1ymYm9EeMjXdcJIGQAAi5wlI6HDS9XbJWzxkqE98HBY8aM0it2j8nWI94JZohjivGPVavWYfNu8+OTmC5X+jm4NlCVrloCVKerzhl2m9vsCAABDLs52b5caR31d0i5hU/zvYeYcZPky6dsr9l+bbyyuT6jsjDfdHzY/WGIja404CfCwKDhX3ZTDzicAAFgiQjZ3V8ub8NslbCXZU6lTcX44W99l92ApGXuznpsfzFO773wMAABgSbEpHULBHGD2uiYlUv8Khy7L7fdtyqhnr4Kypz2nVD5RonaJxbX+dn62/jy7WV79bvFxAACAJccuUyqBavh4P9lInZKziTjCdvB+NMXeyc8PlmNTXmznvi0AAIAoFLwns1/ilBT74wSt05O1Joq/FQrmB7NLpYpf6+PDpNlsnpVeIVZEx/+Kyqvt2gAAgCVGycHubqfamEs2GlcZoqdCiyghvUbn+zUf93QuNpGwAQAADICStck0shiy+/pmFHvjgNWRsAEAAAxIyObAm34tVSiYxy69lYCEDQAAYEBC9m5Se3l7y0u/cZ67D1Re8nUAAACYeyPpPaUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsND8DszfFjGTKHI3AAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAaCAYAAABLlle3AAACSklEQVR4Xu2VzUsVYRTG56KCWWJR19v9nPsRXM2FxKUiCxdBkJAbXWpuIoJoW6K4kxYtAj82LmrRooJq18KoUKG/oKBVG3Hjol20t99zfefycholcKqNDxzOzHPOnOfM+855JwgO8T/QaDQ6KpXKcKlUGs3n8ydtPHEUi8Xz5XL5VRiGtxCdwn/GxmxeYkBkAIEX1Wq1x+Om4T5mMpmjfm4iKBQKRxBYwZ/xeQRnsY10On3M5xMBhS8h+sDnXCPvsAVuU34sESA6R/Er7Gcn11n8cfy49pSPKrT5B4b2i+LL2BC2je04+4ngBZufCHjDKgKPuUy5N8zmcrku/Dz2Er7dPHJwUHgE4duW15zqzdWU7pnZAvdzagburM33oaZxbZZvgbeb0XxanuJj2A+WeNAJviW3rJHi+rVGzD4jKO4+wIaNNRHtJ52dsjH4JeyrYvgJ9J5FMTe/D/38CGqS2Ke4mk1o6XQC1ev1bp/ngSIPftNScptSAzGibwJvv92Xfx//nvgWflF1ongLJI1g30m4GHGaT7gn2Gp0OkkwRjT20HAN3rF8C+HufN5UARXFP8V/UccSj/L+VBT+BPxa3DfShNnPtlqt1uv+Kr+dPuTNxog+D0wuXD+2vu9+hm4+bcwCweuhN7P+ElLnMjalGPyEmtHvEX/X/3k0Ee4xn3FwRZYlxDM3VNjb70fcb2JZYtfwH7Qy2DlbR6JXWfua5fdBSsuvbQjM4CM2yahkdK1tU5N+PHGoEV7gXvA3jsu9wPL2Yactf4h/jl9XZojSwvTx0gAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAaCAYAAABGiCfwAAACQ0lEQVR4Xu2Uu2tUQRTG75INqDGomHWzz7uPhFUUgiwqPrBQUqSIRWwENQghCiFtEiJWEYsUAR8gFlpYmED+AUVFA4LYGkhlI2ks7MRef9/ubBgPdy1yN10++DhzvzlzzrlzZiYIdrGTqNfr3eVy+WKxWBzN5XKH7XzHUCgUTpVKpdUwDCdINo79CsesX2wQ/DiBlyuVygFPm0N7n06ne3zfWMjn83sJ/Aw74OskugvXUqnUfl+PBQKeJdmsr7kC3sCHfCb8uVgg2T2CXqBfexhnsAexV9UzDkto/bcN9YOgT+A5+AP+cfxNotPWPxb4owqBlxgm3B9lstnsPux9uIKeNEu2DwKOkHDS6rpn+lMV42mXRd/Ph4rEdFl9C/zNvO6X1Uk0Bn+xlUNOSvL9gGTD/zg66Mq4A1W3cw20+kVFfXYO/THciJqLgorC/1Nbf22RXoxardbr6ywosPCb+hY0e9nP+Clc0HPm+7oTPIN9S7xN7COt930aUL/gTxzOtDTdL7Tn8LV7TZTslqv8c7uroJ3A747VtxA279dN7BqOL7EvsOuqVEmdW5LxIH29ol3Qtx9DIMYh1nyI6n0Dpl9d1Wr1iHvlo14LHY5lkl2zEwJzx+DH//YrdPfLzlm4YF+o/ATrbiMlsOfheNAs5Dp8pX5ip/zHvBUg8n5FgT7VtE1wgb87Kg27yPd3mNF1wL4Lmw/3SbteyS5RadXq7aBTJ/oaSW5QSFpjtcWe1I5B/aXg6SDiwHQc2k7Yb/Vd7Bj+AuGUeWciUVdsAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAABaElEQVR4Xu2TzysFURTH3/SeIkpkDNPM3Pnhd2IxawtE2VgrKStr2ViwerFUStlJFp6ykY2lrKSUsrCy8gfYKCsLPucZNXO9ZIrdfOvTPeeeH/feM02pVKjQ36rseV7suu6sZVmt+EYYhgPszTiO06InNxQF7UqpGqzBBtzTYJd1Gw7gzPf9Zr1Ol0HiFjeZEAe7F57gJAiCMdZnuDJNs00vzIhrd5K4+XUixeP4L7AYx3ETN1uCkXQN/rSQ3vsmaQCvMi89lqgiT5bZ6YG0DBIOSbxl7dCDPyoZ9B6FK7Ztd2E/SDNChsTlZImJzfN7iO9DVZ6dacTmHLzDDkzCG4XrEpNDKD5ijn24BvZyMsNrVpVpRFFI4A6Osc9JXsV+VJ+f/QKmktQKDfv5uvPknIqf7lOXfLEoiroxy438lGTQNeIL2n4+0WQYbrjVaDK3+hxzi7kM0ugSqtxqSI/nkjz7N79LoX/UB9/lSYRkOePnAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFUAAAAaCAYAAADG+xDjAAAC2klEQVR4Xu2XO4gTURSGJ7iC4vsRg3nM5IXByiKKKAo+dkWRtRBZbSxdsVncFCv4wEdjpagIamXnAywUCwUtRAuFrQTtbJQoWChYuKCC63fYOzo52ckmYsZsuB/85M49555759zXxHEsFovF0hYSicScbDY7nM/nV2hbhMxwXXeAcWS1YVrieV4FjfM+B7WtnaTT6dkksp9+L9L/e/SV57L2m5Ykk8mlvNimcrk8U9vaiSSVRO6Qvknmya5KaidAMo90S1LlHCujDVLWxijphKQWi8X5snPYuRl5lp2byWRWyxGVy+US2r8OaYDzBYKcQKPonPaJkv+d1Hg8Ppdj6Bo6zTiqjGM/v/f5HeT3GPpCuVe3qwGHPhyPm9l5QrDbToPVyvm3mDYP0btmJROm44Th/kVS5WuFcT+l3U/0Cm2hOqb9BOIOYF+u632Is10uaulfxoEeE3+B2KQdeitj1O1qIMAhlvQqnNehMZ73aZ8oaTWphUJhGf6P0E7aLGKbbqT8nPKIU784YtQPyYWs6n+D/QDtV6Ld6Afa7NtM/SdUCbYJhWSewrmKctoWJa0mlXHvldUVrDOfaFfQddmBfj1x16MzTsgqDoLfJfQ6OAGy4Kj75k7cPY2RhhIAXXam7jCWSqWWeBNboSkxmIU6SBitJhXfSsjlIZfvEPaPcqRRvkd5FF9PO2pKpdI8fJ+hOzz2mOoenm+iF/5x0BCZaZy/03EvnZZk1WofH3OxbUV7mhXx1uo4YbgtJpVVmXL+vHgdsgCI1c+xsE3+MWr7ZHiTbHPKOVSV3JidcFZiB9vVgMNVmUWzAis892mfqDBJHSMJa7QtKjxznrqBbS4T449L8kP5aLBNHTjuklnA+S4zcdiZ+gj4p8gKou9bjOEzGg/oAzqv/duNuV9eBlci48tT9wY9QDeaOgLM91nTZ183Qx5mST50vRx95uLSXxUWi8VisVgsFkvH8wupvMaYYSizbwAAAABJRU5ErkJggg==>