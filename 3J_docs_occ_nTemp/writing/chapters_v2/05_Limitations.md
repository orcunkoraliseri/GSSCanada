# 5. Limitations

Each tower draws one set of households, and the Montreal and Calgary models share that set and the same office schedules. City differences therefore reflect climate and the retail and hotel inputs, not independent draws. Run-to-run spread was measured with four further household draws in every tower and city. Across draws, channel intensity varies by about 0.5 % or less, most in the residential channel, and the load-weighted peak hours vary by about 0.1 h or less. The 2030-against-2022 changes in office, retail and hotel energy are 5 to 310 times this spread. The residential change is not clearly larger than the spread, and its sign depends on the draw.

The Quebec hotel series begins in 2019, so its seasonal model order is borrowed from Alberta, and its reconstruction error over 2019 (0.099) is above the 0.05 threshold met by Alberta. The 2030 hotel level rests on a single recovery level for each province, the observed 2023 to 2025 mean, held constant to 2030; the three hotel bands bracket it.

The main code-schedule control puts residents and hotel guests on the NECB office schedule. The dwelling-unit control shows that their night presence is not unique to the survey data (Section 4). Its energy results were compared on the conditioned-area basis only. In both controls, office and retail lighting and plug loads stay on the prototype schedules, while in the survey-based runs they follow occupancy above a standby floor. The office and retail differences in Section 3.2 therefore combine the survey occupancy with this change of load schedule, and the two parts were not separated in the reported runs.

The retail median rule was adopted after an earlier run had been seen. It was fixed before the reported runs were read. Retail meets its range under this rule, but not under the all-simulations rule, where 19 of 56 simulations fall below the floor.

The 2030 scenarios use typical-year weather, not a future climate.

Only one prototype tower family was modelled. Its Tall and SuperTall models are the only structural contrast tested, so the results may not carry over to towers with a different use mix, floor plate or plant.

The 2022 survey changed its collection mode, from telephone interviews to self-completed questionnaires, in the same cycle as the pandemic. Changes between 2015 and 2022, including the 2022 retail fall, may partly reflect the mode change. Lower office and retail presence is associated with working from home and online shopping, but this study does not identify either as a cause.

In the 2030 scenarios, weekday daytime home presence falls below its 2022 level in all three bands, even on a like-for-like population. This residual comes from the generative model, whose 2030 diaries of employed people carry less time both at home and at work, rather than from the scenario design.

Hotel guests and retail staff are outside the survey signal. Retail spaces use the NECB office occupant density. Equipment power density is one value across all space types. Ground-level weather is applied to the full height of the tower. The full list, with a bounding measurement for each item, is given in Supplementary Table S2.
