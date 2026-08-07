# Task 34 — CVAE Validation Probe: Reconstruction-Error Sample Size

**Date:** 2026-04-09
**Analysis type:** Read-only probe (no pipeline code modified)
**Closes:** Task 34

---

## §1 CSVs Examined in `0_Occupancy/Outputs_CENSUS/`

| File | Row count (incl. header) | Columns (first 12) | Reconstruction-error candidate? |
|---|---|---|---|
| `2006_LINKED.csv` | 220,585 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `2016_LINKED.csv` | 273,962 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `BEM_Schedules_2025.csv` | 1,146,337 | SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, Occupancy_Schedule, Metabolic_Rate | No — BEM schedule outputs; no error column |
| `Full_Expanded_Schedules.csv` | 792,033 | EPINO, WGHT_EPI, end, occPRE, start, occACT, Alone, Spouse, Children, parents, otherHHs, others | No — GSS activity episodes |
| `Full_Expanded_Schedules_Refined.csv` | 792,033 | EPINO, WGHT_EPI, end, occPRE, start, occACT, Alone, Spouse, Children, parents, otherHHs, others | No — GSS activity episodes |
| `Full_data.csv` | 17,437,249 | Time_Slot, occPre, occDensity, occActivity, ind_occPRE, ind_occACT, ind_density, WGHT_EPI, Alone, PR, REGION, DDAY | No — aggregated occupancy data |
| `Generated/forecasted_population_2025.csv` | 250,001 | EMPIN, TOTINC, INCTAX, POWST, GENSTAT, CITIZEN, MARSTH, HRSWRK, KOL, CMA, YEAR, LFTAG | No — CVAE-generated demographic profiles; no error column |
| `Generated/forecasted_population_2030.csv` | 250,001 | EMPIN, TOTINC, INCTAX, POWST, GENSTAT, CITIZEN, MARSTH, HRSWRK, KOL, CMA, YEAR, LFTAG | No — CVAE-generated demographic profiles; no error column |
| `Validation_VAE_Reconstruction/validation_vae_reconstruction.csv` | 251 | Sample_ID, Feature, Type, Original, Predicted, Confidence/Diff, Status | **Only reconstruction file** — 10 samples × 25 features |
| `cen06_filtered.csv` | 309,842 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `cen06_filtered2.csv` | 220,580 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `cen11_filtered.csv` | 333,009 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP2011, NOCS, EMPIN | No — Census demographic file |
| `cen11_filtered2.csv` | 302,007 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `cen16_filtered.csv` | 343,331 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP2011, NOCS, EMPIN | No — Census demographic file |
| `cen16_filtered2.csv` | 273,952 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `cen21_filtered.csv` | 361,916 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, GENDER, KOL, ATTSCH, CIP2021, NOC21, EMPIN | No — Census demographic file |
| `cen21_filtered2.csv` | 278,842 | HH_ID, EF_ID, CF_ID, PP_ID, CMA, AGEGRP, SEX, KOL, ATTSCH, CIP, NOCS, EMPIN | No — Census demographic file |
| `forecasted_population_2025_LINKED.csv` | 248,529 | EMPIN, TOTINC, INCTAX, POWST, GENSTAT, CITIZEN, MARSTH, HRSWRK, KOL, CMA, YEAR, LFTAG | No — CVAE-linked demographic profiles; no error column |

**Total CSVs examined:** 18 (17 with > 1000 rows; 1 small diagnostic file)

---

## §2 Finding

**Not found.**

No per-household CVAE reconstruction-error file exists in `Outputs_CENSUS/`. The files with `HH_ID` or `SIM_HH_ID` columns are Census demographic inputs (`cen*_filtered*.csv`, `*_LINKED.csv`) and BEM schedule outputs (`BEM_Schedules_2025.csv`). None contain a numeric error, loss, MSE, or reconstruction-quality metric. The two CVAE forecast files (`Generated/forecasted_population_2025.csv`, `Generated/forecasted_population_2030.csv`, `forecasted_population_2025_LINKED.csv`) contain only demographic profile columns — no per-record reconstruction error is logged.

The only reconstruction-quality file is `Validation_VAE_Reconstruction/validation_vae_reconstruction.csv` (250 data rows = 10 test samples × 25 features), already documented in Task 33.

---

## §3 Impact on Paper Footnote

The 2025 CVAE footnote in `task33_tier4_rate_report.md` (§4 and §5) is based solely on the 10-sample diagnostic file. Because no population-level reconstruction-error file exists, the statistics (median continuous-feature error = 0.014 normalized units, P90 = 0.037, P99 = 0.107) **cannot be upgraded to population-level estimates**.

**Action taken:** Appended the following caveat note to `task33_tier4_rate_report.md` §4 (after the SIM_HH_ID join section):

> **Caveat (Task 34 probe, 2026-04-09):** No per-household reconstruction-error file was found in `Outputs_CENSUS/`. The n=30 continuous-feature rows from the 10-sample diagnostic are the only available reconstruction-quality metric for 2025. The paper footnote should cite this as a diagnostic estimate (n=10 test samples), not a population statistic.

The existing paper footnote draft (§5) already qualifies the statistics as coming from a "10-sample diagnostic validation set" — no change to §5 wording is needed. The caveat in §4 makes this limitation explicit for future readers of the report.

---

## §4 Sign-off

Task 34 ✅ — read-only probe complete; no production code modified; no pipeline re-run; no files in `25CEN22GSS_classification/` touched.
