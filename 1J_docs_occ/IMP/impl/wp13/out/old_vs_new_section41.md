# Section 4.1: old paper numbers vs values recomputed from the rebuilt files (WP13)

Definitions are the paper's own. New values are from the rebuilt grid files listed in the WP13 task doc.
'Old' is copied from `1J_docs_occ/manuscript/1st_Occ_Journal.md` at the line given. No threshold is applied.

| Line | Quantity | Old (paper) | New | Definition used for New |
|---|---|---|---|---|
| 173 | weekday occupied hours 2005 | 15.5 | 16.116 | sum of 24 hourly means, Weekday, Canada |
| 173 | weekday occupied hours 2010 | 11.9 | 15.618 | sum of 24 hourly means, Weekday, Canada |
| 173 | weekday occupied hours 2015 | 17.5 | 16.153 | sum of 24 hourly means, Weekday, Canada |
| 173 | weekday occupied hours 2022 | 15.9 | 17.937 | sum of 24 hourly means, Weekday, Canada |
| 173 | weekday occupied hours 2025 | 12.4 | 16.451 | sum of 24 hourly means, Weekday, Canada |
| 173 | daytime fraction 09-17, 2005 | 0.6 | 0.379 | mean of hours 9-16, Weekday |
| 173 | daytime fraction 09-17, 2025 | 0.3 | 0.404 | mean of hours 9-16, Weekday |
| 173 | (extra) daytime fraction weekday 2005 | not stated | 0.379 | mean of hours 9-16, Weekday |
| 173 | (extra) daytime fraction weekday 2010 | not stated | 0.359 | mean of hours 9-16, Weekday |
| 173 | (extra) daytime fraction weekday 2015 | not stated | 0.402 | mean of hours 9-16, Weekday |
| 173 | (extra) daytime fraction weekday 2022 | not stated | 0.525 | mean of hours 9-16, Weekday |
| 173 | (extra) daytime fraction weekday 2025 | not stated | 0.404 | mean of hours 9-16, Weekday |
| 179 | Default occupied hours (weekday = weekend) | 16.4 | 16.420 | sum of the 24 Default values (16.42) |
| 179 | weekday-weekend asymmetry, range over cycles (h) | 1.8 to 4.6 | 0.64 to 1.80 | abs(weekend hours - weekday hours) per year, all five years |
| 179 | weekend occupied hours 2005 | range 13.7 to 16.5 | 17.499 | sum of 24 hourly means, Weekend |
| 179 | weekend occupied hours 2010 | range 13.7 to 16.5 | 17.414 | sum of 24 hourly means, Weekend |
| 179 | weekend occupied hours 2015 | range 13.7 to 16.5 | 17.621 | sum of 24 hourly means, Weekend |
| 179 | weekend occupied hours 2022 | range 13.7 to 16.5 | 18.582 | sum of 24 hourly means, Weekend |
| 179 | weekend occupied hours 2025 | range 13.7 to 16.5 | 17.829 | sum of 24 hourly means, Weekend |
| 179 | 2022 weekend vs weekday (h) | 16.5 vs 15.9 | 18.58 vs 17.94 | same |
| 179 | Default vacancy minus cycle vacancy, 2005 (pct points) | ~58 | 12.320 | Default 74.4 minus (100*(1 - daytime fraction)), Weekday; old definition of the 58 is not stated in the paper |
| 179 | Default vacancy minus cycle vacancy, 2015 (pct points) | ~58 | 14.608 | Default 74.4 minus (100*(1 - daytime fraction)), Weekday; old definition of the 58 is not stated in the paper |
| 183 | sleep hours/day 2005 | 8.6 to 10.1, peak 2022 | 9.807 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | sleep hours/day 2010 | 8.6 to 10.1, peak 2022 | 8.672 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | sleep hours/day 2015 | 8.6 to 10.1, peak 2022 | 9.076 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | sleep hours/day 2022 | 8.6 to 10.1, peak 2022 | 10.329 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | sleep hours/day 2025 | 8.6 to 10.1, peak 2022 | 8.862 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | passive leisure hours/day 2005 | 4.1 (2005) to 3.0 (2022) | 4.107 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | passive leisure hours/day 2010 | 4.1 (2005) to 3.0 (2022) | 3.044 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | passive leisure hours/day 2015 | 4.1 (2005) to 3.0 (2022) | 4.205 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | passive leisure hours/day 2022 | 4.1 (2005) to 3.0 (2022) | 2.825 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | passive leisure hours/day 2025 | 4.1 (2005) to 3.0 (2022) | 2.331 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | 'Other' hours/day 2005 | 3.5 to 4.4 | 3.409 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | 'Other' hours/day 2010 | 3.5 to 4.4 | 3.261 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | 'Other' hours/day 2015 | 3.5 to 4.4 | 3.550 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | 'Other' hours/day 2022 | 3.5 to 4.4 | 2.441 | activity script: share of activity codes x 24 h (Figure 12) |
| 183 | 'Other' hours/day 2025 | 3.5 to 4.4 | 5.193 | activity script: share of activity codes x 24 h (Figure 12) |
| 189 | metabolic hourly mean, peak 2005 (W) | peak near 125 to 135 (2010, 2022) | 120.680 | mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter) |
| 189 | metabolic hourly mean, peak 2010 (W) | peak near 125 to 135 (2010, 2022) | 127.769 | mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter) |
| 189 | metabolic hourly mean, peak 2015 (W) | peak near 125 to 135 (2010, 2022) | 121.594 | mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter) |
| 189 | metabolic hourly mean, peak 2022 (W) | peak near 125 to 135 (2010, 2022) | 133.751 | mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter) |
| 189 | metabolic hourly mean, peak 2025 (W) | peak near 125 to 135 (2010, 2022) | 125.385 | mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter) |
| 193 | night overestimate, Default vs 2025 (pct) | +39 | 5.943 | Default mean hours 1-5 / 2025 weekday mean hours 1-5 - 1 (definition inferred; old code hard-coded the text) |
| 193 | Default sleep-hour metabolic overprediction vs 70 W floor (pct) | ~36 | 35.714 | (95-70)/70, definition-only, unchanged |
| 193 | midday: Default metabolic vs 2025 hours 10-14 (pct, + = Default higher) | under 24 to 30 (text); +60 in old figure label | 70.385 | 95 / GSS mean hours 10-14 - 1 |
| 193 | GSS metabolic midday value (W) | 125 to 135 | 55.756 | 2025 weekday mean Metabolic_Rate, hours 10-14, all rows |
| 199 | mean weekday occupancy, Default | 0.684 | 0.684 | mean of 24 Default values |
| 199 | mean weekday occupancy, 2025 | 0.465 | 0.685 | mean over 24 h, Weekday, Canada |
| 199 | mean weekend occupancy, 2025 | 0.502 | 0.743 | mean over 24 h, Weekend, Canada |
| 199 | weekday overestimate by Default (pct) | 32 | -0.190 | (Default - GSS)/Default |
| 199 | weekend overestimate by Default (pct) | 27 | -8.578 | (Default - GSS)/Default |
| 199 | mean metabolic rate 2025 (W), hourly-mean definition | 72.1 | 73.931 | mean of 24 hourly means of Metabolic_Rate, Weekday, all rows (Figure 13 panel b line) |
| 199 | mean metabolic rate 2025 (W), occupied rows only | 72.1 | 98.227 | mean of Metabolic_Rate over Weekday rows with Occupancy_Schedule > 0 |
| 199 | Default metabolic overestimate (pct) | 24 | 22.178 | (95 - GSS mean)/95, hourly-mean definition |
| 199 | daytime occupancy Default (%) | 25.6 | 25.625 | mean Default hours 9-16 x 100 |
| 199 | daytime occupancy 2025 (%) | 27.6 | 40.375 | mean Weekday hours 9-16 x 100 |
| 203 | 2025 weekday occupied hours, size 1 | 18.2 | 16.096 | sum of 24 hourly means, by HHSIZE (5+ = 5 or more) |
| 203 | 2025 weekday daytime %, size 1 | 56.1 | 38.600 | mean hours 9-16 x 100 |
| 203 | 2025 weekend occupied hours, size 1 | 19.2 | 17.847 | sum of 24 hourly means |
| 203 | 2025 weekend daytime %, size 1 | 63.8 | 53.857 | mean hours 9-16 x 100 |
| 203 | 2025 weekday occupied hours, size 5+ | 5.2 | 16.360 | sum of 24 hourly means, by HHSIZE (5+ = 5 or more) |
| 203 | 2025 weekday daytime %, size 5+ | 12.4 | 39.431 | mean hours 9-16 x 100 |
| 203 | 2025 weekend occupied hours, size 5+ | 6.9 | 17.542 | sum of 24 hourly means |
| 203 | 2025 weekend daytime %, size 5+ | 21.7 | 50.115 | mean hours 9-16 x 100 |
| 203 | weekday hours reduction 1-person to 5+ (pct) | 71 | -1.639 | (size1 - size5+)/size1 |
