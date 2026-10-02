# Step 7 district check: S against EnergyPlus, 20 check draws x 100 twins (40680 dwelling-years)

Conventions as the frozen scorer: e = S - EnergyPlus; CV(RMSE) = RMSE / mean(EnergyPlus); NMBE = sum(e) / sum(EnergyPlus); per dwelling over 8,760 h. Reported, not gated.

## All dwellings

| group | target | dwelling-years | median CV(RMSE) % | p10 | p90 | median NMBE % | pooled NMBE % (annual) | share CV<=30 and |NMBE|<=10 |
|---|---|---|---|---|---|---|---|---|
| all | heating | 40680 | 38.6 | 18.6 | 214.9 | -2.17 | 10.16 | 0.233 |
| all | cooling | 40680 | 106.3 | 51.1 | 344.2 | 29.74 | 9.98 | 0.002 |
| all | equipment | 40680 | 3.5 | 2.3 | 7.3 | -1.33 | -0.67 | 0.966 |
| all | total_elec | 40680 | 29.9 | 14.1 | 84.6 | 0.53 | 5.77 | 0.451 |

## By twin range

| group | target | dwelling-years | median CV(RMSE) % | p10 | p90 | median NMBE % | pooled NMBE % (annual) | share CV<=30 and |NMBE|<=10 |
|---|---|---|---|---|---|---|---|---|
| in_range | heating | 23260 | 27.1 | 16.3 | 46.6 | -9.80 | -7.62 | 0.359 |
| in_range | cooling | 23260 | 75.5 | 46.5 | 148.0 | 14.73 | 5.38 | 0.003 |
| in_range | equipment | 23260 | 3.3 | 2.2 | 7.1 | -2.13 | -2.56 | 0.953 |
| in_range | total_elec | 23260 | 21.9 | 12.7 | 34.4 | -3.09 | -2.47 | 0.720 |
| out_of_range | heating | 17420 | 165.1 | 33.3 | 290.0 | 102.13 | 58.09 | 0.064 |
| out_of_range | cooling | 17420 | 263.2 | 106.5 | 494.8 | 132.55 | 16.96 | 0.001 |
| out_of_range | equipment | 17420 | 3.9 | 2.5 | 7.5 | 1.90 | 1.87 | 0.984 |
| out_of_range | total_elec | 17420 | 67.0 | 29.4 | 103.6 | 47.84 | 19.96 | 0.093 |

## By building code (seen / new in development)

| group | target | dwelling-years | median CV(RMSE) % | p10 | p90 | median NMBE % | pooled NMBE % (annual) | share CV<=30 and |NMBE|<=10 |
|---|---|---|---|---|---|---|---|---|
| seen | heating | 23060 | 25.7 | 15.7 | 42.5 | -10.81 | -9.79 | 0.397 |
| seen | cooling | 23060 | 74.1 | 46.0 | 124.6 | 5.70 | 3.42 | 0.004 |
| seen | equipment | 23060 | 3.2 | 2.2 | 5.1 | -2.00 | -1.87 | 0.999 |
| seen | total_elec | 23060 | 21.1 | 12.4 | 32.6 | -3.74 | -3.55 | 0.759 |
| new | heating | 17620 | 164.3 | 52.5 | 289.0 | 101.53 | 64.02 | 0.017 |
| new | cooling | 17620 | 260.3 | 134.0 | 488.1 | 131.54 | 20.06 | 0.000 |
| new | equipment | 17620 | 4.4 | 2.6 | 10.5 | 1.87 | 0.90 | 0.922 |
| new | total_elec | 17620 | 66.9 | 38.2 | 103.4 | 47.53 | 21.73 | 0.048 |

## By household (trained_by_model / new to the model)

| group | target | dwelling-years | median CV(RMSE) % | p10 | p90 | median NMBE % | pooled NMBE % (annual) | share CV<=30 and |NMBE|<=10 |
|---|---|---|---|---|---|---|---|---|
| trained | heating | 2940 | 39.2 | 18.4 | 211.8 | -2.05 | 10.25 | 0.235 |
| trained | cooling | 2940 | 107.6 | 51.1 | 347.6 | 28.23 | 8.53 | 0.002 |
| trained | equipment | 2940 | 3.5 | 2.4 | 7.2 | -1.18 | -0.61 | 0.965 |
| trained | total_elec | 2940 | 29.8 | 14.1 | 83.3 | 0.50 | 5.47 | 0.452 |
| new | heating | 37740 | 38.5 | 18.6 | 215.2 | -2.17 | 10.15 | 0.233 |
| new | cooling | 37740 | 106.2 | 51.1 | 343.8 | 29.84 | 10.10 | 0.002 |
| new | equipment | 37740 | 3.5 | 2.3 | 7.3 | -1.34 | -0.67 | 0.966 |
| new | total_elec | 37740 | 29.9 | 14.1 | 84.8 | 0.53 | 5.80 | 0.451 |

## Run level (the scorer's unit: all dwelling-hours of a run), median over runs

| group | target | runs | median CV(RMSE) % | median NMBE % |
|---|---|---|---|---|
| in_range | heating | 1660 | 25.5 | -9.56 |
| in_range | cooling | 1660 | 74.1 | 3.39 |
| in_range | equipment | 1660 | 3.2 | -1.96 |
| in_range | total_elec | 1660 | 24.9 | -3.63 |
| out_of_range | heating | 340 | 132.7 | 69.97 |
| out_of_range | cooling | 340 | 283.3 | 13.07 |
| out_of_range | equipment | 340 | 4.0 | 2.02 |
| out_of_range | total_elec | 340 | 89.6 | 22.41 |
| seen | heating | 1560 | 23.7 | -9.77 |
| seen | cooling | 1560 | 73.1 | 2.58 |
| seen | equipment | 1560 | 3.2 | -1.86 |
| seen | total_elec | 1560 | 23.1 | -3.75 |
| new | heating | 440 | 108.3 | 31.24 |
| new | cooling | 440 | 140.6 | 23.56 |
| new | equipment | 440 | 4.9 | -2.43 |
| new | total_elec | 440 | 76.2 | 17.35 |

## District totals per draw (annual, kWh) and the spread over the 20 draws

| scope | target | S range (max-min) | EnergyPlus range | S SD | EnergyPlus SD | range ratio S/E | Pearson r over 20 draws | S mean | EnergyPlus mean |
|---|---|---|---|---|---|---|---|---|---|
| all | heating | 60794.364 | 69128.537 | 19061.3 | 21819.2 | 0.8794 | 0.9716 | 12729451 | 11555853 |
| all | cooling | 59350.455 | 70366.084 | 17021.8 | 18950.9 | 0.8435 | 0.9809 | 10264193 | 9332477.6 |
| all | equipment | 180257.82 | 180876.45 | 43633.6 | 43696.3 | 0.9966 | 0.9999 | 4621674.4 | 4652779.8 |
| all | total_elec | 186740.91 | 185135.94 | 43729.8 | 43405.6 | 1.0087 | 0.9992 | 12286223 | 11615557 |
| in_range | heating | 57434.121 | 62914.724 | 16156.3 | 18166.2 | 0.9129 | 0.9822 | 7788275.7 | 8430322.5 |
| in_range | cooling | 49664.93 | 50541.757 | 12975.9 | 14454 | 0.9827 | 0.9843 | 5920988.8 | 5618924.6 |
| in_range | equipment | 104341.85 | 104089.54 | 31719.3 | 31696.3 | 1.0024 | 0.9999 | 2594489.1 | 2662767.5 |
| in_range | total_elec | 102639.07 | 100365.13 | 30963.8 | 30987.9 | 1.0227 | 0.9991 | 7164244 | 7345849.9 |
| out_of_range | heating | 46732.733 | 58188.613 | 11781 | 14750.3 | 0.8031 | 0.9872 | 4941175.4 | 3125530.6 |
| out_of_range | cooling | 52588.329 | 53657.303 | 13097.2 | 13564.5 | 0.9801 | 0.9873 | 4343204.6 | 3713553 |
| out_of_range | equipment | 108746.21 | 108841.34 | 27408.4 | 27461.8 | 0.9991 | 0.9999 | 2027185.2 | 1990012.2 |
| out_of_range | total_elec | 112161.38 | 109748.61 | 28107 | 27285 | 1.0220 | 0.9993 | 5121978.6 | 4269706.8 |
| code_seen | heating | 53680.339 | 63653.181 | 16081.3 | 18853.9 | 0.8433 | 0.9928 | 7607399.5 | 8433029 |
| code_seen | cooling | 51337.603 | 55484.578 | 13810.6 | 15327.8 | 0.9253 | 0.9864 | 5846039.6 | 5652661.7 |
| code_seen | equipment | 122961.28 | 123002.44 | 33930.1 | 33959.6 | 0.9997 | 1.0000 | 2587843.7 | 2637112.8 |
| code_seen | total_elec | 123100.6 | 121253.55 | 33394.2 | 33298.3 | 1.0152 | 0.9992 | 7072323.4 | 7332343.1 |
| code_new | heating | 47269.898 | 60725.497 | 12172.7 | 14211.5 | 0.7784 | 0.9600 | 5122051.7 | 3122824.1 |
| code_new | cooling | 53116.907 | 53357.059 | 12533.2 | 12693.7 | 0.9955 | 0.9851 | 4418153.8 | 3679815.9 |
| code_new | equipment | 115921.06 | 115253.21 | 27411.1 | 27309.1 | 1.0058 | 0.9998 | 2033830.7 | 2015666.9 |
| code_new | total_elec | 120170.25 | 115321.71 | 27944.9 | 26923.3 | 1.0420 | 0.9990 | 5213899.2 | 4283213.6 |
| hh_trained | heating | 306215.44 | 304547.25 | 83007.2 | 78943.9 | 1.0055 | 0.9622 | 933359.21 | 846555.61 |
| hh_trained | cooling | 234896.82 | 267410.02 | 56023.1 | 69659.7 | 0.8784 | 0.7141 | 743090.85 | 684715.42 |
| hh_trained | equipment | 90403.26 | 90634.233 | 25377.8 | 25329.3 | 0.9975 | 0.9995 | 334580.59 | 336637.34 |
| hh_trained | total_elec | 244816.54 | 223756.53 | 67312.2 | 65069.5 | 1.0941 | 0.9505 | 893397.27 | 847061.01 |
| hh_new | heating | 295559.3 | 327928.64 | 87232.4 | 85465.5 | 0.9013 | 0.9682 | 11796092 | 10709297 |
| hh_new | cooling | 206520.55 | 230960.42 | 55775.8 | 64996.1 | 0.8942 | 0.6901 | 9521102.5 | 8647762.2 |
| hh_new | equipment | 224797.52 | 223378.54 | 52405.1 | 52164.2 | 1.0064 | 0.9998 | 4287093.8 | 4316142.4 |
| hh_new | total_elec | 336778.52 | 287442.04 | 82623.4 | 76183.1 | 1.1716 | 0.9686 | 11392825 | 10768496 |

## District peak hour, scope all (kWh): S vs EnergyPlus, mean difference over the 20 draws

* heating: annual difference S - E 10.16 % (mean over draws), peak-hour difference 9.53 % (mean), peak hour same in 20 of 20 draws
* cooling: annual difference S - E 9.98 % (mean over draws), peak-hour difference 3.64 % (mean), peak hour same in 0 of 20 draws
* equipment: annual difference S - E -0.67 % (mean over draws), peak-hour difference 0.72 % (mean), peak hour same in 17 of 20 draws
* total_elec: annual difference S - E 5.77 % (mean over draws), peak-hour difference 0.82 % (mean), peak hour same in 9 of 20 draws
