# Table 1 — Six-Dimension Competitor Positioning Matrix

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 2 (the literature matrix, adapted from DR-X1)

| Study | Time-series occupancy | Calibrated behavioural model | Forecast to future year | Activity & end-use resolved | Stock-scale | Load-shape & peak focus |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Chiou (2009) | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Widén & Wäckelgård (2010) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| de Wilde (2014) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Reinhart & Cerezo Davila (2016) | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Fischer et al. (2020) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Motuzienė et al. (2022) | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Chen et al. (2022, ResStock) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Osman et al. (2023, Canada) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Yin et al. (2024) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Jalilian & Kamel (2025) | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| **This study** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** |

**Reading of the matrix:** **Chen et al. (2022)** is the strongest competitor — stock-scale, calibrated, activity-resolved, and load-shape-focused — but retrospective: it does not forecast to a future year. **Yin et al. (2024)** tracks the very premise this paper builds on — long-term (2001–2021) change in time-use behaviour — but stops at statistical analysis: it neither forecasts forward nor runs building-energy simulation, and explicitly names stock-scale energy projection as *future work*. **Jalilian and Kamel (2025)** forecasts at stock scale to a future year yet holds occupancy static at pre-pandemic schedules. The open cell that none occupies — and that this study fills — is the simultaneous combination of a *calibrated behavioural occupancy forecast carried through the COVID/WFH structural break* with *stock-scale paired BEM simulation of the resulting load shape*.

> Note: The matrix lists **external** competitors only. The authors' own prior C-VAE work (Iseri & Hachem-Vermette, JBPS under review; eSim 2026) would satisfy most columns; its delta over the present paper is captured by the four advances described in §1.5 (generator, loads, horizon/validation, attribution), not by these six binary axes.

**Sources for matrix rows** *(DR-verified June 2026 unless flagged):*

- Chiou, Y.-S. (2009) Deriving U.S. household energy consumption profiles from American Time Use Survey data — a bootstrap approach. *Proc. Building Simulation 2009 (IBPSA)*, Glasgow. *(Journal extension: Chiou, Y.-S., Carley, K.M., Davidson, C.I. and Johnson, M.P. (2011) A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method. Energy and Buildings, 43(12), 3528–3538 — confirm DOI at typesetting.)*
- Widén, J. and Wäckelgård, E. (2010) A high-resolution stochastic model of domestic activity patterns and electricity demand. *Applied Energy*, 87(6), 1880–1892. https://doi.org/10.1016/j.apenergy.2009.11.006.
- de Wilde, P. (2014) The gap between predicted and measured energy performance of buildings. *Automation in Construction*, 41, 40–49. https://doi.org/10.1016/j.autcon.2014.02.009.
- Reinhart, C.F. and Cerezo Davila, C. (2016) Urban building energy modeling — A review of a nascent field. *Building and Environment*, 97, 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001.
- Fischer, D., Surmann, A., Biener, W. and Selinger-Lutz, O. (2020) From residential electric load profiles to flexibility profiles — A stochastic bottom-up approach. *Energy and Buildings*, 224, 110133. https://doi.org/10.1016/j.enbuild.2020.110133.
- Motuzienė, V., Bielskus, J., Lapinskienė, V., Rynkun, G. and Bernatavičienė, J. (2022) Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic. *Sustainable Cities and Society*, 76, 103557. https://doi.org/10.1016/j.scs.2021.103557. *(occupancy-forecasting-under-disruption exemplar; replaces the earlier unverified "Bielskus et al. 2021" row, matching Ch1 §1.3.)*
- Chen, J., Adhikari, R., Wilson, E., Robertson, J., Fontanini, A., Polly, B. and Olawale, O. (2022) Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model (ResStock). *Applied Energy*, 325, 119890. https://doi.org/10.1016/j.apenergy.2022.119890.
- Osman, M., Ouf, M., Azar, E. and Dong, B. (2023) Stochastic bottom-up load profile generator for Canadian households' electricity demand. *Building and Environment*, 241, 110490. https://doi.org/10.1016/j.buildenv.2023.110490.
- Yin, R., Yamaguchi, Y., Zajch, A.M., Uchida, H. and Shimoda, Y. (2024) Long-term changes in time use and impacts on residential energy demand. *Proc. ASim 2024, 5th Asia Conference of IBPSA*, Osaka, Japan, 8–10 December 2024, pp. 1321–1328 (paper E17_asim2024_1285). *(Statistical time-use analysis: logistic regression on Japanese time-use 2001–2021; no building-energy simulation, no future-year forecast — both named as future work. IBPSA proceedings DOI to confirm at typesetting.)*
- Jalilian, M. and Kamel, R. (2025) Urban-scale building energy modeling under future climate scenarios (Nassau County, NY; 346,827 buildings, static occupancy). *Frontiers in Energy Research*, 13, 1683787. https://doi.org/10.3389/fenrg.2025.1683787.

*Removed: "Ramírez-Aguilar et al. (2023)" — the June 2026 verification pass found no matching building-energy/occupancy paper under that author name; dropped rather than cite unverifiably.*
