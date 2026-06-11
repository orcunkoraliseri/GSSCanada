# Table 2 — GSS Time-Use Cycle Summary

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 3b (Steps 1–2); `00_GSS_Occupancy_Pipeline.md` §Step 2 validation summary; `02_harmonizationGSS_val.md` TUI_10_AVAIL flags

| Cycle year | n valid diaries | DIARY_VALID exclusion % | Weighted AT_HOME % | Collection mode | TUI_10 available |
|---|---|---|---|---|---|
| 2005 | 19,221 | 1.92 | 62.7 | CATI | No (0) |
| 2010 | 15,114 | 1.79 | 62.3 | CATI | No (0) |
| 2015 | 17,390 | 0.00 | 64.5 | CATI | Yes (1) |
| 2022 | 12,336 | 0.00 | 70.6 | EQ (electronic questionnaire) | Yes (1) |
| **Total** | **64,061** | — | — | — | — |

**Notes:**
- n valid diaries = post 1,440-min diary-closure filter.
- DIARY_VALID exclusion % = proportion of respondents excluded by the closure filter prior to the valid-diary count above.
- Weighted AT_HOME % = population-weighted fraction reporting being at home, diary basis (IS_SYN=0 observed-only rows). The 2022 spike (+6.1 pp vs 2015) is the COVID-19 behavioural signature.
- Collection mode: CATI = Computer-Assisted Telephone Interview; EQ = electronic questionnaire administered online. The CATI→EQ mode shift at 2022 is a potential measurement break; absorbed by harmonization and per-cycle calibration; COLLECT_MODE (0/1) is an explicit conditioning feature of the generator (see Table B1).
- TUI_10 (subjective well-being scale during episode): absent 2005/2010 (TUI_10_AVAIL = 0); available 2015/2022 (TUI_10_AVAIL = 1). Used as an auxiliary conditioning signal for 2015/2022 sub-analyses only; excluded from cross-cycle model inputs.
- SURVMNTH absent in 2005/2010 → DDAY_STRATA conditioning strata collapse from 84 to 7 for those cycles.
