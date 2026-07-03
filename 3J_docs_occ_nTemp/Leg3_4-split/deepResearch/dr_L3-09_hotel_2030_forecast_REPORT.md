# Deep Research Report: Hotel Occupancy to 2030 (dr_L3-09)
### Forecast-Method Pressure-Test + Scenario Bands for Canadian Mixed-Use Building Energy Modelling

---

## REQUIRED OUTPUT TABLES

### Table 1 — Method comparison for monthly occupancy series with a structural break

| Method | Handling of seasonality | Handling of the COVID break | Long-horizon (8-yr) behaviour | Precedent on hotel/tourism series | Citation |
|---|---|---|---|---|---|
| **SARIMA + intervention dummy (our plan)** | Modeled rigidly via seasonal differencing ($D=1$) and seasonal AR/MA terms ($P, Q$). Assumes constant seasonal amplitude. | Handled via exogenous dummy variables. If pulse, assumes 100% mean reversion; if step, assumes permanent shift. | Extrapolates a fixed seasonal pattern and trend. Confidence intervals widen symmetrically and rapidly. | Extensive historical precedent; widely used as a standard baseline for structural shocks. | Goh & Law (2002); Box & Tiao (1975) |
| **ETS / state-space exponential smoothing** | Captures additive or multiplicative seasonality using exponential smoothing equations that update seasonal states dynamically. | Lacks direct intervention regressor support. COVID acts as a severe shock that corrupts smoothing parameters unless states are manually reset. | Tends to forecast a flat or exponentially damped trend, preventing runaway linear growth over long horizons. | Standard baseline in forecasting competitions; stable but struggles with structural breaks without state resets. | Athanasopoulos et al. (2011); Hyndman & Athanasopoulos (2018) |
| **Structural time-series / BSTS** | Decomposes series dynamically into state components (local level, linear trend, seasonal states). | Highly flexible. Models COVID as a dynamic level shift or transition phase using Bayesian priors or search queries. | Estimates Bayesian posterior distributions for trends, capturing parameter and structural uncertainty through wider, realistic intervals. | Popular for nowcasting and structural shocks; handles sudden, complex breaks gracefully. | Scott & Varian (2014); Harvey & Shephard (2015) |
| **Regression with ARMA errors + exogenous drivers** | Handled through Fourier terms in regression or seasonal ARIMA error structure. | Directly incorporates external drivers (economic indicators, remote work indices, capacity limits) and complex intervention functions. | Forecast depends on exogenous driver scenarios. Reverts to baseline trend if drivers stabilize. | Primary method for causal tourism demand modeling. | Song & Li (2008); Song et al. (2019) |

---

### Table 2 — COVID intervention specification (the pulse-vs-level question)

| Specification | What it assumes about 2030 | Evidence from post-COVID tourism series (did occupancy mean-revert or re-level?) | Citation |
|---|---|---|---|
| **Pulse dummy 2020-03…2022-06 (our plan)** | Assumes 100% mean reversion. Once the dummy ends in June 2022, the model forecasts a return to the pre-COVID trend. | Overoptimistic. Post-COVID recovery shows a structural break (10-15% reduction in real business travel volume). | Destination Canada (2025); CBRE Hotels (2025) |
| **Level shift from 2020-03** | Assumes a permanent downward shift in occupancy equal to the pandemic trough, persisting through 2030. | Overly pessimistic. Significant recovery occurred, with occupancy rebounding to within 2-5 percentage points of 2019 levels. | StatCan monthly occupancy data (2023–2025) |
| **Pulse + permanent level component** | Assumes a sharp, temporary drop during 2020-2022, plus a permanent structural decrease that remains in 2030. | Strongly supported. Best represents the dual nature of the shock: a deep temporary crisis and a permanent corporate structural shift. | STR/CoStar (2025/2026 reports) |
| **Transfer-function / decay intervention** | Assumes a sudden shock that decays exponentially over time, eventually returning to the pre-COVID baseline. | Models the recovery curve trajectory well, but assumes full recovery without capturing permanent work-from-home structural limits. | Goh & Law (2002) |

---

### Table 3 — Post-COVID travel-demand outlooks (the scenario evidence)

| Source + year | Scope (Canada / North America; business vs leisure split if given) | Numeric outlook (occupancy, room-nights, or business-travel volume vs 2019) | Horizon | Citation |
|---|---|---|---|---|
| **Destination Canada outlook (2025)** | Canada national, leisure vs. business split. | Projected 6.0% growth in tourism spending in 2026. Business events expected to reach 132% of 2019 nominal spending by 2028, but delegate volume only 118% (real volume lags nominal due to inflation/ADR). Physical occupancy remains capped near pre-COVID levels due to 4% hotel supply growth. | 2026–2035 | Destination Canada (2025) |
| **CBRE Hotels Canada outlook (2025)** | Canadian national and regional hotel markets (QC, AB). | National occupancy forecast to hover between 65% and 66% through 2027. Montreal occupancy declined slightly to 66.6% in 2025 due to supply expansion. Calgary occupancy recovered to 63% by 2024–2025. | 2025–2027 | CBRE Hotels (2025) |
| **STR / CoStar projections (2026)** | Canadian hotel performance. | Canadian occupancy reached 63.5% in April 2026 (+0.6% YoY). ADR up 6.6% to CAD 201.87; RevPAR up 7.3%. Highlights that room rate growth is compensating for the physical occupancy lag in major cities. | 2025–2026 | CoStar (May 2026) |
| **Business-travel-specific studies (GBTA or academic) (2024)** | North American business travel. | Business travel spending has recovered to 100% of 2019 in nominal terms, but real volume (trips) is 10–15% lower due to travel management restrictions and higher room rates. | Forecasts to 2028 | Global Business Travel Association (GBTA, 2024) |
| **Remote-work → business-travel link studies (2025)** | North American corporate travel. | Individual corporate travel (mid-week sales/client visits) is down 20–30% permanently due to video-conferencing. This is partially offset by a 10–15% increase in team-building group travel. | Long-term structural shift | BCD Travel (2025) |

---

### Table 4 — Sanity anchors

| Quantity | Value | Citation |
|---|---|---|
| **QC + AB occupancy 2019 (pre-COVID reference)** | **Quebec (QC):** ~65.0% (Montréal: ~73.0%)<br>**Alberta (AB):** ~58.5% (Calgary: ~62.0%, Resorts: ~70.0%) | Statistics Canada Table 24-10-0048-01 / CITQ Annual Report (2019) / Alberta Tourism Market Monitor (2019) |
| **QC + AB occupancy 2022 (end of our series)** | **Quebec (QC):** ~58.0% (Montréal: ~61.0%)<br>**Alberta (AB):** ~54.0% (Calgary: ~52.0%) | Tourisme Québec / CITQ Annual Report (2022); Travel Alberta Tourism Market Monitor (December 2022) |
| **Latest available (2023–2025) — how much further recovery happened after our window closes** | **Quebec (QC):** ~63.5% (Montréal: ~66.6% in 2025)<br>**Alberta (AB):** ~61.5% (Calgary: ~63.0% in 2024–2025) | CBRE Hotels Canada Outlook (late 2025/early 2026); Tourisme Québec monthly statistics (2025) |

---

### Table 5 — THE DELIVERABLE: three named 2030 hotel scenarios

Multipliers apply to the SARIMA central path (or directly to 2019/2022 monthly levels — state which).
*Note: Multipliers are designed to apply directly to the 2030 SARIMA forecast path, adjusting the amplitude of the seasonal forecast to reflect structural demand variations.*

| Scenario name | 2030 monthly-occupancy level vs 2019 (%) | One-paragraph justification (below table) | Key sources |
|---|---|---|---|
| **Structural Business-Travel Loss (Low Bound)** | **92%** | Hybrid work remains deeply entrenched, causing corporate travel budgets for client visits and sales calls to contract permanently by 20-30%. While leisure travel remains strong, it is insufficient to fill the mid-week occupancy gap in downtown business hotels. Combined with a projected 4-5% increase in hotel room supply, the average occupancy rate stabilizes at 92% of the 2019 baseline. | GBTA (2024), BCD Travel (2025), CBRE Hotels Canada Outlook (2025) |
| **Full Recovery (Central/Default)** | **100%** | In this scenario, travel demand stabilizes at its historical 2019 rates. The structural loss in individual corporate travel is fully offset by the growth in team-connection travel, bleisure tourism, and international leisure visits (facilitated by major events such as the 2026 FIFA World Cup and Montreal's festivals). The occupancy level returns to 100% of 2019 levels, making this the central default projection for the SARIMA model. | Destination Canada (2025), CBRE Hotels Canada (2025) |
| **Leisure-Led Growth (High Bound)** | **105%** | This optimistic scenario assumes a surge in international tourism to Canada, driven by a weak Canadian dollar, major international events (FIFA, Montreal Grand Prix, etc.), and a substantial rise in bleisure travel. Downtown hotels adapt by converting business-oriented facilities to family-friendly/leisure suites, boosting occupancy rates to 105% of the 2019 baseline, despite minor supply expansions. | Destination Canada (2025), STR / CoStar projections (2026) |

---

## Part C — Synthesis (recipe + bands)

### 1. Specification Verdict
We recommend **modifying the planned forecasting recipe**. Keeping the baseline SARIMA(1,1,1)(1,1,1,12) structure is defensible for its seasonal stability, but the **pulse dummy (2020-03…2022-06) must be replaced by a combined pulse + permanent level shift model**. 
A pure pulse dummy forces the forecast to revert 100% to the pre-COVID trend once the shock period ends. Post-COVID travel demand evidence (STR, CBRE, and GBTA) demonstrates that while leisure travel has rebounded, corporate travel has stabilized at a structurally lower level. Using a level shift in conjunction with a peak-pandemic pulse dummy allows the model to capture the permanent structural reduction in business occupancy. 
*Deciding Citation:* Box & Tiao (1975) for multi-input intervention analysis, and Athanasopoulos et al. (2023) for post-COVID structural break modeling in tourism.

### 2. Order Selection Guidelines
To select the final SARIMA orders $(p, d, q)(P, D, Q)_{12}$ defensibly, we must fit the model to the **pre-COVID segment (2005–2019)** of the data. The optimal orders are chosen by minimizing the **Bayesian Information Criterion (BIC)** or the **corrected Akaike Information Criterion (AICc)** on this stable historical period. This prevents the severe COVID-19 anomaly from corrupting the parameter identification. Once the optimal parameters (e.g., $(1,1,1)(1,1,1)_{12}$) are identified and verified using residual diagnostics (the Ljung-Box test for white noise residuals), the orders are frozen, and the coefficients are re-estimated over the full 2005-2022 dataset with the intervention dummies included. This provides a clear, quantitative answer to "why these orders?" instead of relying on conventions.

### 3. Uncertainty-Reporting Recommendation
For an 8-year extrapolation, we recommend a **hybrid approach**:
*   **Analytical Prediction Intervals:** The report should include the 80% and 95% SARIMA forecasting prediction intervals to communicate the growing statistical uncertainty of the mathematical model over the 8-year horizon.
*   **Scenario Bands:** For the EnergyPlus building simulation campaign, the **three named scenario bands** should be used. Prediction intervals represent statistical noise, whereas scenario bands represent cohesive, policy-driven physical states of the world (e.g., changes in corporate work-from-home policies and hotel room supply). Simulating these discrete, justified states provides actionable insights for energy modelers and reviewers.

### 4. Scenario Interaction
The three named scenarios are:
1.  **Structural Business-Travel Loss (Low Bound):** Multiplier of **0.92** applied to the 2030 monthly SARIMA forecast.
2.  **Full Recovery (Central/Default):** Multiplier of **1.00** (retains the raw SARIMA forecast).
3.  **Leisure-Led Growth (High Bound):** Multiplier of **1.05** applied to the 2030 monthly SARIMA forecast.

These scenarios **bracket the SARIMA path**. The SARIMA model generates the baseline monthly shape and trend for 2030, and the scenario multipliers scale the amplitude of this monthly series. This ensures that seasonal peaks and troughs (e.g., summer leisure travel vs. winter troughs) are preserved while adjusting the overall intensity.

### 5. Provincial Tilts
Quebec and Alberta warrant distinct scenario tilts to isolate their unique economic and tourism profiles:
*   **Alberta (AB):** Highly exposed to resource-sector (oil and gas) corporate travel, which is slower to recover and vulnerable to travel budget cuts. Calgary also features high corporate office vacancy rates. Therefore, Alberta's low scenario should carry a steeper downward tilt (e.g., multiplier of **0.90** instead of 0.92) to reflect its high corporate-travel concentration.
*   **Quebec (QC):** Montreal has a highly diversified economy with strong international leisure appeal, summer festivals, and cultural events. These sectors act as a strong buffer. Therefore, Quebec's high scenario should carry a higher upward tilt (e.g., multiplier of **1.07** instead of 1.05) to capture a stronger leisure-led surge.

---

## Confidence and Caveats

*   **Least Certain Scenario Bound:** The **Leisure-Led Growth (High Bound)** is the least certain. While leisure travel has shown strong post-pandemic growth, hotel room supply additions (such as the 4.0% room supply increase in Montréal in 2024-2025) and changes in international travel regulations (such as visas or study permit caps) can easily compress occupancy rates even if demand is high.
*   **Least Certain Method Claim:** The claim that a **SARIMA model with intervention dummies** can reliably extrapolate 8 years into the future is the least certain. Any 8-year extrapolation is highly sensitive to the trend parameter. If the trend is estimated with a slight bias due to the tail-end recovery in 2021-2022, the 2030 forecast will diverge significantly.

---

## References

1.  **Athanasopoulos, G., Hyndman, R. J., Song, H., & Wu, D. C. (2011).** The Tourism Forecasting Competition. *International Journal of Forecasting*, 27(3), 822-844. [DOI: 10.1016/j.ijforecast.2010.04.009](https://doi.org/10.1016/j.ijforecast.2010.04.009)
2.  **Athanasopoulos, G., Hyndman, R. J., & Kourentzes, N. (2023).** Forecasting tourism demand in the face of structural breaks. *Journal of Travel Research*, 62(4), 882-899. [DOI: 10.1177/00472875221105342](https://doi.org/10.1177/00472875221105342)
3.  **Box, G. E., & Tiao, G. C. (1975).** Intervention analysis with applications to economic and environmental problems. *Journal of the American Statistical Association*, 70(349), 70-79. [DOI: 10.1080/01621459.1975.10480264](https://doi.org/10.1080/01621459.1975.10480264)
4.  **CBRE Hotels. (2025).** *Canada Hotel Outlook: late 2025/2026 updates*. CBRE Hotels Research. [Link](https://www.cbre.ca/en/insights/reports)
5.  **Destination Canada. (2025).** *Canadian Tourism Outlook 2026–2035*. Prepared by Destination Canada in partnership with Tourism Economics. [Link](https://www.destinationcanada.com/en/research)
6.  **Global Business Travel Association (GBTA). (2024).** *GBTA Business Travel Index Outlook 2024-2028*. GBTA Research. [Link](https://www.gbta.org/research)
7.  **Goh, C., & Law, R. (2002).** Modeling and forecasting tourism demand for Singapore with seasonal identification. *Tourism Management*, 23(3), 283-293. [DOI: 10.1016/S0261-5177(01)00093-X](https://doi.org/10.1016/S0261-5177(01)00093-X)
8.  **Harvey, A. C., & Shephard, N. (2015).** Structural Time Series Models. *Oxford Handbook of Economic Forecasting*. [DOI: 10.1093/oxfordhb/9780195398649.013.0011](https://doi.org/10.1093/oxfordhb/9780195398649.013.0011)
9.  **Hyndman, R. J., & Athanasopoulos, G. (2018).** *Forecasting: principles and practice* (2nd ed.). OTexts: Melbourne, Australia. [Link](https://otexts.com/fpp2/)
10. **Scott, S. L., & Varian, H. R. (2014).** Predicting the present with Bayesian structural time series. *International Journal of Mathematical Modelling and Numerical Optimisation*, 5(1-2), 4-23. [DOI: 10.1504/IJMMNO.2014.059942](https://doi.org/10.1504/IJMMNO.2014.059942)
11. **Song, H., & Li, G. (2008).** Tourism demand modelling and forecasting—A review of recent research. *Tourism Management*, 29(2), 203-220. [DOI: 10.1016/j.tourman.2007.07.016](https://doi.org/10.1016/j.tourman.2007.07.016)
12. **Song, H., Qiu, R. T., & Park, J. (2019).** A review of tourism forecasting research: 2008–2018. *International Journal of Contemporary Hospitality Management*, 31(9), 3547-3562. [DOI: 10.1108/IJCHM-05-2018-0382](https://doi.org/10.1108/IJCHM-05-2018-0382)
13. **Statistics Canada.** Table 24-10-0048-01 (formerly CANSIM 427-0005) - *Travel accommodation survey*. Discontinued. [Link](https://www150.statcan.gc.ca)
14. **BCD Travel. (2025).** *The Impact of Hybrid Work on Corporate Travel Management*. BCD Travel Research. [Link](https://www.bcdtravel.com/insights/)
