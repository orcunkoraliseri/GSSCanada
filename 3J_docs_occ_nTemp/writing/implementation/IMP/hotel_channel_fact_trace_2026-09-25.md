# Hotel channel fact trace (2026-09-25)

Read-only fact trace. No manuscript file was edited. Evidence file paths are absolute
under `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`.

## Evidence base

- `3J_docs_occ_nTemp\Leg3_4-split\Step6_docs\3rdJ_06_hotel_sarima_4split.py` lines 24-70
  (module docstring), 98-101 (window constants), 164-282 (order selection and freeze/borrow
  logic), 385-410 (2030 central path, anchors), 400-420 (build_lookup, raw values).
- `3J_docs_occ_nTemp\Leg3_4-split\Step6_docs\outputs_step6_hotel\section8_hotel_gate_scorecard.csv`
  (fitted order, backcast MAE, dip check, per-province gate results).
- `0_Occupancy\external\hotel_occupancy_monthly.csv` (raw input, real vs blank cells).
- `0_Occupancy\processed\hotel_multiplier_lookup.csv` (values fed to 2022 EnergyPlus build).
- `0_Occupancy\forecasts\hotel_multiplier_2030.csv` (values fed to 2030 EnergyPlus build).
- `3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\3rdJ_07_aug_to_bem_4split.py` lines 46-49,
  119-123, 1046-1262 (only `--year 2022` and `--year 2030` exist; lookup and forecast csv
  paths; AB Q4 2022 carry-forward).
- `3J_docs_occ_nTemp\Leg3_4-split\deepResearch_v2\manifest.json` (Alberta source list).
- `3J_docs_occ_nTemp\Leg3_4-split\deepResearch_v2\2022-province-mensuelle.txt` line 23
  (ISQ source line).

## Findings (a)-(e)

**(a) Real data span read by the fit.** `hotel_occupancy_monthly.csv`: AB rows are blank
2005-01 to 2010-12, real 2011-01 to 2022-09 (one internal gap, 2011-12), blank again
2022-10 to 2022-12. QC rows are blank 2005-01 to 2018-12, real 2019-01 to 2022-12.
Confirmed against `hotel_multiplier_lookup.csv`, whose AB rows start 2011-01 and end
2022-09, and whose QC rows start 2019-01 and end 2022-12. No 2005-2009 CBRE archive
values appear anywhere in the input file; script lines 33-40 state this splice never
happened.

**(b) SARIMA order and pandemic window.** Gate scorecard row 8.1: AB's own pre-COVID BIC
fit selected order `(p,d,q,P,D,Q) = (1,1,0,0,1,0)`, i.e. SARIMA(1,1,0)(0,1,0)_12, not
SARIMA(1,1,1)(1,1,1,12). QC's pre-COVID segment has only 12 observations (2019-01 to
2020-02), below the 24-observation floor the script sets to identify a seasonal term, so
QC's order was not independently fit; it was set equal to AB's order (`order_source =
"borrowed_from_AB"`), flagged as a gate 8.1 FAIL for QC. The pandemic indicator is two
regressors, not one: `covid_pulse` is a dummy for 2020-03 to 2022-06 exactly as the
manuscript states, but the code also carries a second, permanent `level_shift` dummy from
2020-03 onward that never turns off (script lines 99-101, 217-218). The manuscript
mentions only the pulse window.

**(c) What r value each simulation year used.** `build_lookup()` (script, the loop building
`hotel_multiplier_lookup.csv`) writes the raw input `occupancy_rate` values straight from
the source series, with no fitting step; `hotel_multiplier_lookup.csv` for 2022 matches
`hotel_occupancy_monthly.csv` for 2022 row for row (e.g. AB 2022-01 = 0.331 in both). Step 7
(`3rdJ_07_aug_to_bem_4split.py` line 121) reads this lookup file for `--year 2022`. So the
2022 EnergyPlus multiplier uses observed 2022 monthly occupancy, not a SARIMA fitted or
forecast value. One data gap: AB 2022 has no real Oct-Dec rows; Step 7 lines 46-49
carry-forward the September value into Q4. For 2030, `anchored_2019_central_path()`
(script lines 385-395) builds the central path as the normalised 2019 monthly shape times a
fixed 2023-2025 recovery anchor (QC 0.635, AB 0.615), then the three named bands
(0.92/1.00/1.05, with AB low=0.90 and QC high=1.07) multiply that central path. This is
written to `hotel_multiplier_2030.csv`, read by Step 7 for `--year 2030`. The raw SARIMA
96-step point forecast is also written to the same file for reference
(`sarima_raw_forecast_2030` column) but is not the value used for `occupancy_rate`; the
2030 file's own numbers confirm the raw SARIMA path drifts far above 1.0 (e.g. AB
2030-01 raw forecast 2.32) and is not physically usable.

**(d) Backcast and pandemic-dip checks.** Gate 8.3 (backcast): AB tested on the full
2015-01 to 2019-12 window (n=60), MAE=0.0174, PASS. QC has no ground truth before 2019-01,
so its "2015-2019" check is actually a 2019-only test (n=12), MAE=0.0990, which fails the
same MAE<0.05 threshold and is recorded as `FAIL (PARTIAL)`. Gate 8.4 (2020-04 dip):
both provinces reconstruct the April 2020 collapse without overshoot and PASS (AB
reconstructed 0.2767 vs actual 0.1250; QC reconstructed 0.3187 vs actual 0.1120 -- note
the reconstructed value is well above the actual low in both cases, i.e. the model
recovers the direction of the dip but not its depth).

**(e) 2005-2015 code schedule.** Confirmed. `3rdJ_07_aug_to_bem_4split.py` only implements
`--year 2022` and `--year 2030` (lines 1046-1262); there is no code path that builds a hotel
product for 2005, 2010 or 2015, and line 1027-1030 states historical-cycle products for
those years are "NOT PRESENT locally" and out of Step 7's scope. Guest rooms in those three
survey years therefore keep the NECB code schedule by omission, not by an explicit override.

## Manuscript claims

| # | Claim (file:line) | Verdict | Evidence | Proposed replacement |
|---|---|---|---|---|
| 1 | `02_Framework.md:15` "Quebec ... Institut de la statistique du Québec, ... Alberta ... from CBRE and Travel Alberta market reports. Both series cover 2005 to 2022." | FALSE | Alberta source tag in the data is ABMKTMONITOR (Government of Alberta tourism market monitor PDFs, manifest.json), not CBRE/Travel Alberta; no CBRE data appears in the input file. AB real values run 2011-01 to 2022-09 and QC 2019-01 to 2022-12, not 2005-2022 for either province (`hotel_occupancy_monthly.csv`; script lines 25-31). | "The Quebec series comes from the Institut de la statistique du Québec. The Alberta series comes from the Government of Alberta's tourism market monitor. The Alberta series covers 2011 to 2022 and the Quebec series covers 2019 to 2022." |
| 2 | `02_Framework.md:36` "SARIMA(1,1,1)(1,1,1,12) ... A pandemic indicator covers March 2020 to June 2022 ..." | PARTLY | Fitted order is SARIMA(1,1,0)(0,1,0)_12 for Alberta, borrowed by Quebec (gate scorecard 8.1). The March 2020 to June 2022 window matches the code's pulse dummy, but a second permanent level-shift dummy from March 2020 onward is not mentioned. | "Each provincial series is fitted with a seasonal ARIMA model, order (1,1,0)(0,1,0) with 12-month seasonality, selected by BIC on Alberta's pre-pandemic months and reused for Quebec. A pandemic pulse covers March 2020 to June 2022, together with a level shift from March 2020 onward." |
| 3 | Section 2.3 "Hotel uses a band of 0.92, 1.00 or 1.05 around the central seasonal projection." | TRUE | `BAND_DEFAULT` and `hotel_multiplier_2030.csv` confirm these three multipliers on the central path (script line 96; gate 8.7 PASS). Note the manuscript omits the two provincial tilts (AB low 0.90, QC high 1.07), also present in the same table (Table 1 / Eq. 1 area), but the sentence itself is accurate as a general statement. | No change needed; optionally add "with Alberta's low band at 0.90 and Quebec's high band at 1.07" if the tilts are meant to be stated here rather than only in the table. |
| 4 | `02_Framework.md:91` "The hotel model is fitted to the provincial series, and its 2015 to 2019 reconstruction and pandemic dip are checked against the same series." | PARTLY | True for Alberta (full 2015-2019 backcast, n=60, PASS). For Quebec there is no ground truth before 2019, so the check only covers 2019 (n=12) and that check fails its own MAE threshold (gate 8.3, `FAIL (PARTIAL)`). The pandemic-dip check passes for both provinces (gate 8.4). | "The hotel model is fitted to the provincial series. Its reconstruction is checked against the same series over 2015 to 2019 for Alberta and over 2019 only for Quebec, and the pandemic dip is checked for both provinces." |
| 5 | `11_References.md:11` CBRE Limited and Travel Alberta entry | FALSE | No CBRE or Travel Alberta values are in the ingested Alberta series; the manifest lists only Government of Alberta tourism market monitor PDFs from open.alberta.ca. | See proposed reference below. |
| 5b | `11_References.md:21` Institut de la statistique du Québec entry | TRUE (needs a fuller citation) | ISQ is confirmed as the QC source (`2022-province-mensuelle.txt` line 23). The entry has no table/catalogue identifier; the export gives one. | See proposed reference below. |
| 6a | `02_Framework.md:70` "In 2005, 2010 and 2015 the guest rooms stay on the code schedule, because the Quebec tourism series lacks matching coverage for those years." | PARTLY | True that no hotel product exists for those three years (Step 7 lines 1027-1030) and true that Quebec's gap alone would block all three years. But Alberta's own real data also excludes 2005 and 2010 (starts 2011-01), so the sentence credits the omission to Quebec only when Alberta lacks coverage for two of the same three years too. | "In 2005, 2010 and 2015 the guest rooms stay on the code schedule, because neither province's tourism series has usable coverage across all three years." |
| 6b | `Table_04_validation_gates.md:37` "Hotel backcast \| QC and AB monthly 2015-2019 vs reconstruction \| MAE < 0.05" | PARTLY | Describes the gate design, not the outcome. QC's actual tested window is 2019 only (n=12) and QC fails the MAE<0.05 threshold on that window (gate 8.3). Table gives no hint the two provinces were tested on different windows or that QC failed. | Add a note column or footnote: "QC tested on 2019 only (no ground truth before 2019); QC MAE 0.0990, FAIL. AB tested on the full 2015-2019 window; AB MAE 0.0174, PASS." |

## Proposed replacement reference entries

**Alberta**, built only from `manifest.json` (do not add anything not in that file):

> Government of Alberta (2022) *Alberta tourism market monitor: monthly update*. Edmonton:
> Government of Alberta. https://open.alberta.ca/dataset/1648658d-ec8e-4bf0-98d6-23bdf172ac4a
> [Accessed: [date]]

Note: the manifest lists one dataset page per year (each with its own `dataset_id`); the
URL above is the 2022 dataset page, matching the manifest excerpt read. If earlier years
are cited elsewhere, each year has its own `dataset_id`/URL in the same manifest and should
use its own dataset page rather than this one.

**Quebec**, built only from the export's source line:

> Institut de la statistique du Québec (2026) *Enquête sur la fréquentation des
> établissements d'hébergement*, données mensuelles par territoire. Québec: Institut de la
> statistique du Québec. [Accessed: [date]]

The export text gives the survey name and the update date (2026-07-02) but no stable table
or catalogue number; none could be derived without a web search, which is out of scope here.

## Proposed limitation sentence (Quebec short series)

One sentence, for `05_Limitations.md` or the hotel paragraph in `02_Framework.md`:

> The Quebec hotel series begins in 2019, so its seasonal order is borrowed from Alberta
> and its pre-pandemic reconstruction check covers 2019 only.

This states the limitation once, in plain terms, without process history (no mention of
gate numbers, BIC search internals, or the investigation that led to the anchored-2019-shape
central path).

## WHAT I DID NOT VERIFY

- Did not verify the exact wording, table number or catalogue identifier for the ISQ
  survey beyond what the export's on-screen text gives; a true catalogue number likely
  needs the ISQ website itself, which is a web lookup outside this read-only, no-web-search
  task.
- Did not verify whether earlier Alberta Tourism Market Monitor issues (pre-2022) use a
  different `dataset_id`/URL structure in `manifest.json`; only confirmed the 2022 entries
  used to build the reference above.
- Did not re-run the SARIMA fit or the BIC grid search; relied on the checked-in
  `section8_hotel_gate_scorecard.csv` and the script's own printed logic rather than
  re-executing `3rdJ_06_hotel_sarima_4split.py`.
- Did not check every other chapter file for hotel mentions beyond `00` through `07`,
  `09_AppendixB_Equations.md`, `10_Declarations.md`, `11_References.md` and
  `SI_additions.md`; archived pre-stage folders (`_archive_pre_*`) were excluded on
  purpose since they are not the live manuscript.
- Did not check `campaign_local_deliverable/`, `agg_deliverable/`, or
  `outputs_step9_deliverable/` beyond what was necessary, per the task's read-only
  restriction on those folders.
- Did not verify the AB 2022 Q4 carry-forward's effect on any downstream reported number
  in `03_Results.md`; only confirmed the carry-forward mechanism exists in Step 7.
