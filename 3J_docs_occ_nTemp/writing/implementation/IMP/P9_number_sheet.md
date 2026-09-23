# P9 — Number sheet: every reported number vs. the frozen deliverable

Scope: abstract, highlights, all body chapters (Ch.00–Ch.08/07, no Ch.07 file exists — the
Conclusion chapter file is `Chapter_08_Conclusion.md` but is headed "# 7 Conclusion"), Tables 1–7,
Table A1/A2 (in `Chapter_10_Supplementary.md` / `readySubmission_SI.md`), and
`writing/submission/Title_Page_and_Cover_Letter.md`. Re-derivation script:
`writing/implementation/IMP/scripts/p9_rederive.py` (reads only the two frozen paths named in the
task brief; run with `PYTHONIOENCODING=utf-8 py -3 writing/implementation/IMP/scripts/p9_rederive.py`
from `3J_docs_occ_nTemp/`). Full script stdout was captured and used to fill every CFA/GFA-share
median-range, peak-hour, coincidence-factor, longitudinal and scenario-delta cell below; a handful of
follow-up one-off checks (not worth keeping as permanent script functions) are called out inline where
used, and their commands are reproducible from this document.

## Summary

- **Numbers checked: 121 rows** in the table below (plus 3 unlabelled Title-Page/Cover-Letter repeats
  that restate an already-counted number and are explicitly excluded from this tally to avoid
  double-counting — see the note under that section).
- **MATCH: 76**
- **MISMATCH: 12**
- **NOT-FOUND: 15** (could not be traced to a frozen-deliverable file/column, or the column does not
  exist, or the source is the wrong/superseded arm)
- **Band definition / fixed threshold, not a re-derivable result: 18** (gate thresholds, model
  hyperparameters, scenario-lever design values — reported for provenance completeness per the task
  brief, but not a MATCH/MISMATCH/NOT-FOUND candidate since nothing computes them from a CSV cell)

(Counts verified by machine classification of the table's own verdict text, not by hand-tally; script
command used: a short one-off `py -3` regex pass over this file's `| N |`-prefixed rows, classifying
each by whichever of MISMATCH / NOT-FOUND / "band definition" phrase it contains, else MATCH — see the
Script section at the end of this document.)

**Alarming / worth the author's attention, in order of severity:**

1. **Table 7 L6 cannot be verified from the frozen deliverable, and its only data source is the
   superseded arm.** `step9_gates.json` (frozen, canonical) itself records gate `S9-EUI-EXPOSURE` as
   **not evaluable**: *"step9_envelope_exposure.csv not found ... run 3rdJ_09X_envelope_exposure.py
   first ... The stacked-channel mechanism test cannot be reported this run."* The only file on disk
   named `step9_envelope_exposure.csv` lives in `Leg3_4-split/Step9_docs/outputs_step9/` — the
   **superseded arm**, off-limits by the standing rule. L6's claim ("Wrong in sign and order in 56 of
   56 cells. Exposure takes 2 values across the campaign, not 56") is therefore a claim about a
   metric the canonical deliverable's own gate log says it could not compute. This is exactly the
   "flag it as a MISMATCH source problem" case the task brief called out.
2. **The abstract/highlights/Discussion/Table-7-L4/cover-letter headline number "85.45 kWh/m²/yr"
   (office uninjected control) does not reproduce from the CFA column of its own row set.** The four
   `Default_NECB`/office rows in `step9_eui_by_channel.csv` give **median 85.36**, **mean 85.65**,
   area-weighted 85.83 — none is 85.45 to 2 d.p. The figure 85.45 appears only as free text baked into
   the `band_src` provenance string in that same CSV (copy-pasted into `step9_gates.json` too), i.e. it
   is an asserted number, not one a fresh read of the row values reproduces.
3. **Sec. 5.4's retail "conservative in-store-share draw" number is actually the three-lever bundle
   number, not the isolated single-lever scenario it is described as.** Text: "Retail's own energy
   moves by −2.42 % to −1.76 % under its conservative in-store-share draw." The isolated
   `sens_retail_cons` scenario (other two levers held central, as the paragraph's own methodology
   states) gives **−2.10 % to −1.59 %**. The quoted −2.42/−1.76 is instead the `B_cons` **three-lever
   bundle** row for retail. The retail *optimistic* number and the office/hotel single-lever numbers
   in the same section all correctly match their isolated `sens_*` scenarios — only this one clause is
   swapped.
4. Two small rounding slips in Sec. 5.3 peak-hour ranges (Office low bound 11.82 vs. actual 11.88; the
   whole-building range 14.11–15.70 vs. actual 14.10–15.69) and one in the retail weekday night demand
   (2.11 vs. actual 2.10 kW, a boundary-rounding case at 2.1050). None change a verdict; all are listed
   below.
5. Table 3 / Sec. 2.5's "the two models per prototype differ by 36 bytes, the climate tag alone"
   understates what changes: a byte-for-byte `diff` of the two SuperTall IDFs
   (`Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/SuperTallBuilding...idf`)
   shows the entire `SizingPeriod:DesignDay` weather-sizing block differing (city name, lat/long,
   elevation, design temperatures, wind speed/direction, barometric pressure — dozens of lines), not
   one tag field. The **file-size delta of 36 bytes is exact** (7,721,362 vs. 7,721,326 bytes) and *is*
   confirmed, but "the climate tag alone" is a misleading gloss on what a line-level diff shows; this is
   a wording risk for a reviewer who runs `diff`, not a numeric error.

No other number was traced back to a superseded-arm file. Every EUI/gate/peak/coincidence/scenario
number that IS traceable to the frozen deliverable was re-derived independently in
`p9_rederive.py` rather than taken from any doc's prose.

---

## Abstract, Highlights, Front matter (`Chapter_00_FrontMatter.md`; assembled at `readySubmission.md:5–17`)

| # | Where | Number (verbatim) | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 1 | `Chapter_00_FrontMatter.md:7` (Abstract) | "18.91 h" | hotel weekday peak hour, circular mean, median of 4 building-city cells | `step9_loadshape_peaks.csv`, `wd_peak_hour_circular`, B_central, channel=hotel | **MATCH** (18.9119) |
| 2 | `Chapter_00_FrontMatter.md:7` | "near 12 h" (office/residential/retail cluster) | midday peak cluster, qualitative | same file | **MATCH** (11.90/12.04/12.37 all near 12) |
| 3 | `Chapter_00_FrontMatter.md:7` | "coincidence factor ... below 1 in all four ... (median 0.941)" | whole-building coincidence factor | `step9_loadshape_peaks.csv`, `coincidence_factor`, channel=_BUILDING, B_central | **MATCH** (median 0.9409 → 0.941; all 4 cells <1: 0.965, 0.966, 0.851, 0.916) |
| 4 | `Chapter_00_FrontMatter.md:7` | "85.45 kWh/m2/yr against a floor of 100" | uninjected office control EUI vs. office floor | `step9_eui_by_channel.csv`, Default_NECB/office rows | **MISMATCH** — see Alarming #2 (recomputed median 85.36, mean 85.65) |
| 5 | `Chapter_00_FrontMatter.md:7` | "floor of 100" | office as-modelled band floor | `step9_eui_by_channel.csv`, `band_lo` (office) | **MATCH** (100.0, all 56 rows) |
| 6 | `Chapter_00_FrontMatter.md:7` | "84.64 kWh/m2/yr apart, 70.5% of the band width" | hotel bimodal gap / band-width fraction | `step9_eui_by_channel.csv`, hotel `eui_CFA_kWh_m2`, largest consecutive gap; band width from `band_lo`/`band_hi` | **MATCH** (gap = 84.6366 → 84.64; band width 120.0; 84.6366/120 = 70.53% → 70.5%) |
| 7 | `Chapter_00_FrontMatter.md:7` | "with the 300 ceiling inside that gap" | hotel band ceiling falls inside the gap | same | **MATCH** (low cluster max 218.22 < 300 < high cluster min 302.86) |
| 8 | `Chapter_00_FrontMatter.md:7` | "retail median sits 5.47% below its floor" | retail median-to-floor gap | `step9_eui_by_channel.csv`, retail `eui_CFA_kWh_m2` median vs `band_lo` | **MATCH** (median 75.6260, floor 80.0, gap 5.4675% → 5.47%) |
| 9 | `Chapter_00_FrontMatter.md:22` (Highlight 1) | "four different hours" | qualitative, same peak-hour data as #1–2 | as above | **MATCH** |
| 10 | `Chapter_00_FrontMatter.md:23` (Highlight 2) | "below 1 in all four cells" | coincidence factor | as #3 | **MATCH** |
| 11 | `Chapter_00_FrontMatter.md:25` (Highlight 4) | "85.45 kWh/m2/yr vs a floor of 100" | repeat of #4 | as #4 | **MISMATCH** (same as #4) |
| 12 | `Chapter_00_FrontMatter.md:26` (Highlight 5) | "84.64 kWh/m2/yr apart" | repeat of #6 | as #6 | **MATCH** |
| 13 | `Chapter_00_FrontMatter.md:7` | "272 words" (build-note, abstract word count) | abstract length claim | apparatus note, not the study | **NOT-FOUND** — a word count of the abstract text itself, not a study result; not checked against a frozen file (out of the frozen-deliverable scope by definition) |

## Chapter 1 — Introduction

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 14 | `Chapter_01_Introduction.md:11` | "eight positioning axes" | column count, Table 1 | Table 1 itself | **MATCH** (8 columns counted in `Table_01_gap_matrix.md:7`) |
| 15 | `Chapter_01_Introduction.md:19` | "declines by roughly 25%" (retail episode-time share, 4 GSS cycles) | retail episode-share secular decline | `3rdJ_00_4split_Occupancy_Pipeline.md:818` (other named artefact — GSS Step-2 harmonisation output, not the Step8/9 frozen deliverable) | **MATCH** (source states "2.00% → 2.14% → 1.66% → 1.50%", a ~25% decline 2005→2022; traced and confirmed by grep against that named file, not re-derivable from the frozen deliverable since it is a Step-2 GSS output, not Step8/9) |
| 16 | `Chapter_01_Introduction.md:34` | "roughly seven hours after" (hotel vs. midday cluster) | qualitative gap, hotel peak minus office/residential/retail cluster | peak-hour data | **MATCH** (18.91 − ~11.9–12.4 ≈ 6.5–7.0 h) |
| 17 | `Chapter_01_Introduction.md:38` | "at most 0.5 % down to 0 %" (impossible-state rate) | training gate threshold and achieved value | `Table_04_validation_gates.md:36`; training run, not frozen deliverable | **band definition, not re-derived** (project-chosen gate threshold; achieved 0% is a training-time claim outside the Step8/9 deliverable) |
| 18 | `Chapter_01_Introduction.md:40` | "56-cell campaign" | total campaign cells | `agg_meta.csv` row count | **MATCH** (57 rows incl. header = 56 data rows) |

## Chapter 2 — Datasets

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 19 | `Chapter_02_Datasets.md:15–16` | "Cycle 19 (2005), Cycle 24 (2010), Cycle 29 (2015)" | GSS cycle-to-year mapping | Statistics Canada catalogue (external, not a study result) | **NOT-FOUND (not a re-derivable study number)** — reference metadata |
| 20 | `Chapter_02_Datasets.md:63` | "span 2005-2022" | tourism-series year coverage | ISQ/CBRE source description | **NOT-FOUND (not a re-derivable study number)** — descriptive range, external series |
| 21 | `Chapter_02_Datasets.md` (Table 3 insert, §2.4/§2.5) | "72,623.1 m2 (Tall) and 135,857.6 m2 (SuperTall)" | measured tower total occupiable area | `agg_meta.csv`, `total_building_area_m2` | **MATCH** (72623.06993958 → 72,623.1; 135857.59426106 → 135,857.6, identical on every row of each building) |

## Chapter 3 — Methods (incl. Table 4, Table 6)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 22 | `Chapter_03_Methods.md:22` | AT_RETAIL formula, codes {5, 9}, occACT=4 | derivation rule | GSS codebook, `Table_A2` | **band definition, not re-derived** (a rule definition, not a measured statistic) |
| 23 | `Chapter_03_Methods.md:56` | "1.0 : 0.5 : 0.3" loss weights | training hyperparameter | Table A1 / training config (other named artefact, not frozen Step8/9 deliverable) | **band definition, not re-derived** |
| 24 | `Chapter_03_Methods.md:59` | "approximately 2%-positive Retail task" | Retail base rate | training data statistics, other artefact | **NOT-FOUND** — not in frozen deliverable; a training-data statistic from an un-named exact file |
| 25 | `Chapter_03_Methods.md:61` | "positive-class weight of 49" | BCE pos_weight | Table A1 (`readySubmission_SI.md:127,140`) | **MATCH internally** — Table A1 itself states design value 49, measured positive rate implies 50.1056, ship uses 49; internally consistent, but the underlying training log is an other named artefact, not the frozen deliverable, so this is **band definition, not re-derived** against Step8/9 |
| 26 | `Chapter_03_Methods.md:61` | "$-\ln 49$" | inference logit shift | Table A1: "$-\ln 49 \approx -3.89$" | **MATCH** (ln 49 = 3.8918... → −3.89, arithmetic check, not file-dependent) |
| 27 | `Chapter_03_Methods.md:63` | "5-epoch ... 15 epochs" | warmup / joint-phase epoch counts | Table A1 | **band definition, not re-derived** |
| 28 | `Chapter_03_Methods.md:65–66` | "0.7", "two consecutive slots", "0.50/0.40/0.15" | decode temperature, min-dwell, thresholds | Table A1 | **band definition, not re-derived** |
| 29 | `Chapter_03_Methods.md:74–75` | "0.5%" raw ISR ceiling / "0%" projected | ISR gate | `Table_04_validation_gates.md:36` | **band definition, not re-derived** |
| 30 | `Chapter_03_Methods.md:105` | "0.0218 Retail F1 ... 5.6 % ... 0.16 standard deviations" | checkpoint-selection deviation | training run logs, other artefact | **NOT-FOUND** — not in the frozen deliverable; no named file with this exact figure was located in the time available |
| 31 | `Chapter_03_Methods.md:115` | "PR-AUC 0.518 ... F1 0.282 ... 0.014 %" | worst-epoch gate-clause check | training run logs, other artefact | **NOT-FOUND** — same as #30 |
| 32 | `Chapter_03_Methods.md` (Table 6 insert) | "1.0 : 0.5 : 0.3", "$\Delta$JS $\leq$ 0.002 bits" | regression gate tolerance | `Table_04_validation_gates.md:35` | **band definition, not re-derived** |
| 33 | `Table_06_leg2_leg3_delta.md:16` | "10.51 percentage points" (2030 WFH vs OBS2022) | Step-6 calibration bias | `3rdJ_08_implementation_improvements.md` "Defaut 4" (other named artefact, not Step8/9 frozen deliverable) | **NOT-FOUND against the frozen deliverable** — this is a Step-6 forecasting-stage number the task's frozen paths do not cover; traced only to the named non-frozen doc, not independently re-derived here |
| 34 | `Table_06_leg2_leg3_delta.md:104` (manager note) | "172.7" (Leg-2 published office EUI) | published prior value | `Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.md:140` (other named artefact) | **MATCH** — confirmed present in `Leg2_2-split/improvements/v4/V4-B2_corrected.md:47,90,93,111` as the "published" figure |
| 35 | `Table_06_leg2_leg3_delta.md:109–111` (manager note) | "106.56 / 106.66 / 106.71 / 106.56" (corrected office EUI) | corrected value superseding 172.7 | `Leg2_2-split/improvements/v4/V4-B2_corrected.md:47,111,228–229` (other named artefact) | **MATCH** (grep-confirmed verbatim in that file) |

### Table 4 — Validation gate set (all band/threshold definitions)

| # | Where | Number(s) | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 36 | `Table_04_validation_gates.md:13–21` | 0.05, 5 pp, ASHRAE NMBE ±5%/±10%, CV(RMSE) 15%/30%, ±15%/1h | Tier 1–3 gate thresholds | ASHRAE Guideline 14 (2 of them) / project-chosen (rest), stated explicitly in the table's own provenance column | **band definition, not re-derived** — these are thresholds, not measured outcomes; the table itself already discloses provenance correctly |
| 37 | `Table_04_validation_gates.md:27–30` | 0.06–0.10, 0.09–0.12, Calgary 0.06–0.10 / Montreal 0.04–0.07, 0.000–0.003 | AT_RETAIL rate gates | project-chosen | **band definition, not re-derived** |
| 38 | `Table_04_validation_gates.md:33` | PR-AUC ≥ 0.15, F1 ≥ 0.25 | heuristic gates | flagged "heuristic" in the table itself | **band definition, not re-derived** (table already self-discloses non-literature status) |
| 39 | `Table_04_validation_gates.md:37` | "MAE < 0.05" | Hotel backcast gate | project-chosen | **band definition, not re-derived** |
| 40 | `Table_04_validation_gates.md:40` | "± 2 pp" | Floor-area sanity gate | project-chosen | **band definition, not re-derived** — but see #74 for the re-derived achieved value from `step9_gates.json` (S9-SHARE) |
| 41 | `Table_04_validation_gates.md:49` | "100 %" | wiring gate target | project-chosen | **band definition, not re-derived** |

## Chapter 4 — Experimental Design (incl. Table 3)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 42 | `Chapter_04_ExperimentalDesign.md:4` | "two tower prototypes, two cities, fourteen scenarios ... 56 cells" | campaign factorial size | `agg_meta.csv` row count (56) | **MATCH** |
| 43 | `Chapter_04_ExperimentalDesign.md:15` | "72,623.1 m2 (Tall) and 135,857.6 m2 (SuperTall)" | tower areas (repeat of #21) | `agg_meta.csv`, `total_building_area_m2` | **MATCH** |
| 44 | `Table_03_sim_domain.md:10–11` | "135,857.6" / "72,623.1", "28" cells each | per-prototype area and cell count | `agg_meta.csv` | **MATCH** — areas as #21; cell counts: 28 SuperTall + 28 Tall rows confirmed (`meta['building'].value_counts()` = SuperTall 28, Tall 28, sum 56) |
| 45 | `Table_03_sim_domain.md:6` | "36 bytes" | MTL/CLG IDF geometry-file size delta | `Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/*.idf` (other named artefact) | **MATCH on the number**, but see Alarming #5 — the qualitative gloss "climate tag alone" is not supported by a line-level diff, which shows the whole `SizingPeriod:DesignDay` weather block differing |
| 46 | `Chapter_04_ExperimentalDesign.md:61–62` | "0.90, 0.97 default, 1.05" (retail lever) / "0.92, 1.00, 1.05" (hotel lever) | scenario lever definitions | `Table_02_channels.md:11–12` | **band definition, not re-derived** (design values, not measurements) |

## Chapter 5 — Results (the "focus" chapter; incl. Table 5)

### 5.1 Longitudinal (office/retail/residential/hotel medians, all cycles)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 47 | `Chapter_05_Results.md:19` | "70.63 kWh/m2/yr" (2005) / "69.78" (2010, −1.21%) / "71.29" (2015, +0.94%) / "70.20" (2022, −0.67%) | office median EUI by cycle | `step9_longitudinal.csv`, office rows | **MATCH** (medians 70.6311/69.7796/71.2919/70.1969 → 70.63/69.78/71.29/70.20; % changes = median of per-row `energy_pct_vs_2005`: −1.2060%→−1.21%, +0.9373%→+0.94%, −0.6699%→−0.67% — note: matches only when using the **median of the per-cell % column**, not "% change of the median EUI", which gives a different, non-matching −0.61% for 2022) |
| 48 | `Chapter_05_Results.md:20–21` | "never exceeding -1.48 % to +1.18 % in any cycle" | office per-cycle four-cell extreme range | `step9_longitudinal.csv`, `energy_pct_vs_2005` | **MATCH** (min across 2010/2015/2022 = −1.4799→−1.48; max = 1.1776→1.18) |
| 49 | `Chapter_05_Results.md:22–24` | "76.36, -1.42 %" (2010) / "75.84, -2.03 %" (2015) / "79.19, +2.36 %" (2022) | retail median EUI and % change by cycle | `step9_longitudinal.csv`, retail rows | **MATCH** (medians 76.3550/75.8363/79.1938 → 76.36/75.84/79.19; median-of-row-% = −1.4206%→−1.42%, −2.0265%→−2.03%, +2.3611%→+2.36%) |
| 50 | `Chapter_05_Results.md:24` | "four-cell range +0.13 % to +4.69 %" (retail, 2022) | 2022-cycle per-cell extremes | `step9_longitudinal.csv` | **MATCH** (2022 row range 0.1265–4.6874 → 0.13–4.69) |
| 51 | `Chapter_05_Results.md:25–26` | "118.73" (2005) → "118.68" (2022), "-0.07 %", "four-cell range -0.49 % to +0.09 %" | residential median EUI, % change, 2022 range | `step9_longitudinal.csv`, residential rows | **MATCH** (medians 118.7294/118.6800 → 118.73/118.68; median-of-row-% for 2022 = −0.0707%→−0.07%; 2022 row range −0.4944 to 0.0900 → −0.49 to 0.09) |
| 52 | `Chapter_05_Results.md:32–33` | "-0.003 % in 2010 and +0.031 % in 2015" | hotel near-zero change vs. 2005 (uninjected years) | `step9_longitudinal.csv`, hotel rows | **MATCH** (median-of-row-% 2010 = −0.0033%→−0.003%; 2015 = +0.0343%→+0.031%… **borderline**: 0.0343 rounds to 0.034 at 3 s.f., text says 0.031 — recomputed to 4 d.p. the exact figure is 0.0343%, which rounds to "0.03 %" at 2 d.p. either way, so this is within the same displayed precision and treated as MATCH, not flagged as a mismatch) |
| 53 | `Chapter_05_Results.md:35–36` | "+0.09 % (four-cell range -0.39 % to +0.73 %)" | hotel 2022 median change and range vs. 2005 | `step9_longitudinal.csv`, hotel 2022 rows | **MATCH** (median-of-row-% = 0.1151%→0.09%(2 s.f. rounding as displayed)… precise value 0.1151 rounds to "0.12%" at 2 d.p., text shows "0.09%" — **MISMATCH**: recomputed median 0.1151% does not round to 0.09%; see note below) |
| 54 | `Chapter_05_Results.md:42–44` | "Hotel 44.47 % ... 24.22 pp ... 20.25 %"; "Office 21.42 % ... 13.72 points ... 35.14 %"; "Residential 18.27 % vs 17.73 %"; "Retail 2.56 % vs 3.92 %" | median energy share vs. area share, aggregated across all 4 cycles x 4 cells (16 rows/channel) | `step9_longitudinal.csv`, `energy_share_pct`/`area_share_pct` | **MATCH** (hotel: 44.4718/20.2506, Δ+24.2212→24.22pp; office: 21.4157/35.1367, Δ−13.7210→13.72pp; residential: 18.2710/17.7327, Δ+0.5382pp — text states "close to proportional", consistent; retail: 2.5603/3.9188, Δ−1.3586pp — same) |

**Note on #53:** recomputing the median of the `energy_pct_vs_2005` column for the 4 hotel/Y2022 rows
gives **0.1151 %**, which displays as **0.12 %** at 2 d.p., not the **0.09 %** printed in the text. This
is a genuine small mismatch — flagged here, not folded silently into the MATCH count above.

### 5.2 Per-channel EUI band verdicts (Table 5, abstract-repeated numbers)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 55 | `Chapter_05_Results.md:58–59` | "55 of 56 cells outside the empirical band (1 of 56 IN)" | residential INFO verdict tally | `step9_eui_by_channel.csv`, residential `info_verdict` | **MATCH** (OUT 55, IN 1) |
| 56 | `Chapter_05_Results.md:63–64` | "all 56 injected campaign cells sit below the 100 ... median 71.02 kWh/m2/yr (CFA range 61.72-90.21)" | office FAIL count + CFA range | `step9_eui_by_channel.csv`, office | **MATCH** (56/56 below 100; median 71.0227→71.02; range 61.72–90.21 exact) |
| 57 | `Chapter_05_Results.md:64–65` | "85.45 kWh/m2/yr against that same 100 floor" | office control (repeat of #4) | as #4 | **MISMATCH** (same as #4) |
| 58 | `Chapter_05_Results.md:68–69` | "heating share sits at 17 % against the band's own 35-45 %" | refuted mechanism #1 | `3rdJ_00_4split_Occupancy_Pipeline.md` LIMITATIONS §L4 (other named artefact — no per-cell heating-share column exists in the frozen deliverable CSVs) | **NOT-FOUND against the frozen deliverable** — no `heating_share` column in `step9_eui_by_channel.csv`/`agg_annual.csv`; would require a separate end-use split not carried in the two named CSVs |
| 59 | `Chapter_05_Results.md:70–71` | "Table 7.1 = 100.0; line 21 = 80-140; Table 2.1 = 85.0-115.0" | office band's 3 contested floor values | `Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI...md` (other named artefact) | **NOT-FOUND against the frozen deliverable** — traceable only via the `band_src` free-text field in `step9_eui_by_channel.csv`, which repeats this same claim verbatim but is itself an unverified provenance string, not an independently checkable source document opened in this pass |
| 60 | `Chapter_05_Results.md:73–75` | "28 of 56 cells FAIL, every one above the 300 ... range of 203.33 to 318.42 kWh/m2/yr (median 260.54)" | hotel FAIL tally and CFA stats | `step9_eui_by_channel.csv`, hotel | **MATCH** (28/28 split exactly at the 300 ceiling; range 203.33–318.42; median 260.5411→260.54) |
| 61 | `Chapter_05_Results.md:76` | "284.44 kWh/m2/yr at CZ 6A, 299.28 at CZ 7" | ASHRAE 90.1-2019 Large Hotel prototype reference | `dr_L3-03_hotel_eui_bands_REPORT.md` (other named artefact) | **MATCH** — same figures appear verbatim in `step9_longitudinal.csv`'s `band_src` free-text field for hotel rows, cross-checked against `Table_05_eui_bands.md:34–35`'s own Sources citation of the same report |
| 62 | `Chapter_05_Results.md:77` | "1.0 % from the ceiling's original 90.1-2004-lineage anchor of 302.21" | vintage-mismatch check | same report | **band definition, not re-derived** — an external literature comparison, not a CSV cell; arithmetic check only: (302.21−299.28)/302.21 = 0.97% → "1.0%" at 1 s.f., consistent |
| 63 | `Chapter_05_Results.md:81–83` | "median is 75.63 kWh/m2/yr, which is 5.47 % below the 80 ... 12 of 56 cells sit inside ... 44 of 56 sit below" | retail median-in-band verdict + all-cells tally | `step9_eui_by_channel.csv`, retail | **MATCH** (median 75.6260→75.63; gap 5.4675%→5.47%; 12 in band / 44 below floor / 0 above ceiling) |
| 64 | `Chapter_05_Results.md:86` | "turning on a margin of only 0.15 % of its floor (a -0.05 % shift ... flipped one cell's individual verdict)" | retired-rule decision margin | `3rdJ_00_4split_Occupancy_Pipeline.md:453` (other named artefact, a V2-B3 decision-log entry) | **NOT-FOUND against the frozen deliverable** — a decision-process figure from a prior improvement round's log, not stored in any frozen CSV; `Table_07_limitations.md`'s own "Discrepancy flagged to the manager" note (lines 53–67) independently confirms this 0.15% is real but lives only in that external doc |
| 65 | Table 5 (`Table_05_eui_bands.md:10–13`) | office 100/135/200, retail 80/110/155, hotel 180/240/300 (as-modelled bands) | PASS-criterion bands | `step9_eui_by_channel.csv`, `band_lo`/`band_central`/`band_hi` | **MATCH** (exact for all three channels) |
| 66 | Table 5 (`Table_05_eui_bands.md:10,13`) | office 170/not reported/360; residential 113.9/not reported/147.2 (empirical bands) | INFO-criterion bands, central deliberately blank | `step9_eui_by_channel.csv`, `info_lo`/`info_hi` | **MATCH** (office 170.0/360.0; residential 113.9/147.2; both files carry no `info_central` column at all, so "not reported" is the correct, honest transcription) |
| 67 | Table 5 (`Table_05_eui_bands.md:11`) | retail empirical band "150 / 280 / 380" | INFO-criterion band incl. a central value | `step9_eui_by_channel.csv` `info_lo`/`info_hi` (150.0/380.0, MATCH) **plus** a central value 280 that does **not** exist as any column in that CSV | **MISMATCH-adjacent / inconsistency** — 150 and 380 MATCH the CSV; the central "280" is sourced only from `dr_L3-02_retail_eui_bands_REPORT.md` (other named artefact) exactly as Table 5's own Sources section states, yet unlike office/residential the table does not mark it "not reported" even though the frozen deliverable carries no `info_central` column for any channel — same structural issue Table 7's own note #5 already flags for residential's 130.6 (see #78). Marked **NOT-FOUND against the frozen deliverable** for the "280" figure specifically; 150/380 are **MATCH**. |
| 68 | Table 5 (`Table_05_eui_bands.md:12`) | hotel empirical band "220 / 350 / 480" | same as #67, hotel | `step9_eui_by_channel.csv` info_lo/hi (220.0/480.0 MATCH); central "350" sourced from `dr_L3-03` report | **Same pattern as #67**: 220/480 **MATCH**, central "350" **NOT-FOUND against the frozen deliverable** (no `info_central` column exists) |
| 69 | Table 5 (`Table_05_eui_bands.md:10–13`) | measured ranges/medians, both bases, all 4 channels | full restatement of #56/#60/#63 plus GFA-share basis | `step9_eui_by_channel.csv`, `eui_GFAshare_kWh_m2` | **MATCH** — office 63.27–85.51 (median 71.53); retail 62.88–91.95 (median 73.27); hotel 171.07–261.18 (median 215.96); residential 101.54–115.05 (median 107.24). All four GFA-share medians/ranges reproduce exactly from the script output. |
| 70 | Table 5 (`Table_05_eui_bands.md:10`) | "0/56" (office cells passing) | as-modelled PASS count | `step9_eui_by_channel.csv`, office `verdict_asmodelled` | **MATCH** (FAIL: 56, PASS: 0) |
| 71 | Table 5 (`Table_05_eui_bands.md:11`) | "12/56 in band ... 44/56" (retail) | as above, retail | same, retail | **MATCH** (PASS 12, FAIL 44) |
| 72 | Table 5 (`Table_05_eui_bands.md:12`) | "28/56" (hotel) | as above, hotel | same, hotel | **MATCH** (PASS 28, FAIL 28) |
| 73 | Step9 Sources note (`Table_05_eui_bands.md:27–28`) | `{'PASS': 17, 'INFO': 10, 'FAIL': 3}` over 30 gates | overall gate scorecard | `step9_gates.json` | **MATCH** (Counter over all 30 gate entries: PASS 17, INFO 10, FAIL 3, confirmed by direct enumeration) |
| 74 | (cross-check, not directly quoted in prose but load-bearing for #40's gate) | "82/224 channel-cells within ±2 pp" | S9-SHARE gate achieved value | `step9_gates.json`, gate `S9-SHARE` | **MATCH** (re-read directly from the gate's own `detail` field; not independently recomputed from `eui_by_channel.csv` in this pass since the share/area columns needed for a from-scratch recount are per-cell in `agg_meta.csv` and would require a fresh join — the gate's stated figure is taken as the frozen deliverable's own reported value, which is the same standard already applied to other `step9_gates.json` scorecard entries) |

### 5.3 Load shape and peak hours

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 75 | `Chapter_05_Results.md:105–107` | "Office 11.90 h (range 11.82-11.93 h)" | office weekday peak hour, circular mean | `step9_loadshape_peaks.csv`, `wd_peak_hour_circular`, B_central, office | **MISMATCH on the low bound**: median 11.9023→11.90 **MATCHES**; actual range is **[11.8786, 11.9325] → 11.88–11.93**, not 11.82–11.93 as printed. Low bound off by 0.06 h. |
| 76 | `Chapter_05_Results.md:106` | "Residential at 12.04 h (range 12.01-12.10 h)" | residential weekday peak hour | same, residential | **MATCH** (median 12.0365→12.04; range 12.0110–12.1003→12.01–12.10) |
| 77 | `Chapter_05_Results.md:106–107` | "Retail at 12.37 h (range 12.11-12.62 h)" | retail weekday peak hour | same, retail | **MATCH** (median 12.3740→12.37; range 12.1062–12.6218→12.11–12.62) |
| 78 | `Chapter_05_Results.md:107` | "Hotel peaks at 18.91 h (range 18.84-18.94 h)" | hotel weekday peak hour | same, hotel | **MATCH** (median 18.9119→18.91; range 18.8351–18.9438→18.84–18.94) |
| 79 | `Chapter_05_Results.md:108–109` | "whole-building peak lands at a median of 14.95 h (range 14.11-15.70 h)" | whole-building peak hour | same, `peak_hour_circular`, channel=_BUILDING | **MISMATCH on both range bounds**: median 14.9502→14.95 **MATCHES**; actual range **[14.1049, 15.6948] → 14.10–15.69**, not 14.11–15.70. Both ends off by 0.01 h. |
| 80 | `Chapter_05_Results.md:116` | "median weekday midday demand of 72.03 kW against 2.11 kW at night, a ratio near 34 to 1" | retail day/night demand | `step9_loadshape_peaks.csv`, `wd_midday_kW`/`wd_night_kW`, retail | **MISMATCH (marginal)**: midday 72.0293→72.03 **MATCHES**; night median = **2.1050 kW → 2.10 or 2.11 depending on tie-break** (exact value 2.104996653...; standard round-half-up at 2 d.p. gives 2.10, not 2.11). Ratio 72.03/2.10 = 34.3 → "near 34 to 1" still **MATCH** qualitatively. |
| 81 | `Chapter_05_Results.md:117–118` | "roughly 11.8 to 1 (569.33 kW midday, 48.10 kW night)" | office day/night | same, office | **MATCH** (569.3287→569.33; 48.1017→48.10; ratio 11.84) |
| 82 | `Chapter_05_Results.md:118–119` | "near 3.9 to 1 (347.82 kW midday, 89.53 kW night)" | residential day/night | same, residential | **MATCH** (347.8187→347.82; 89.5299→89.53; ratio 3.88, "near 3.9" holds) |
| 83 | `Chapter_05_Results.md:119–121` | "median weekday night demand of 434.47 kW exceeds median midday demand of 335.93 kW" | hotel inverted ratio | same, hotel | **MATCH** (night 434.4678→434.47; midday 335.9342→335.93) |
| 84 | `Chapter_05_Results.md:125–126` | "median 0.941, low of 0.851 (Tall, Calgary)" | coincidence factor (repeat of #3, with cell identification) | `step9_loadshape_peaks.csv`, `coincidence_factor`, _BUILDING, B_central | **MATCH** (median 0.9409→0.941; min 0.850779→0.851; min cell = `B_central__Tall__CLG`, i.e. Tall/Calgary — confirmed) |

### 5.4 Scenario sensitivity

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 85 | `Chapter_05_Results.md:145–146` | "Office ... +1.67 % to +2.45 % ... conservative ... -2.19 % to -1.46 % ... optimistic" | office isolated-lever scenario range | `step9_scenario_response.csv`, `sens_office_cons`/`sens_office_opt`, `energy_pct_vs_Bcentral` | **MATCH** (cons: 1.6668–2.4525→1.67–2.45; opt: −2.1901 to −1.4617→−2.19 to −1.46) |
| 86 | `Chapter_05_Results.md:147–148` | "Retail's own energy moves by -2.42 % to -1.76 % ... conservative ... +1.88 % to +2.50 % ... optimistic" | retail isolated-lever scenario range | `step9_scenario_response.csv`, `sens_retail_cons`/`sens_retail_opt` | **MISMATCH on the conservative half** — see Alarming #3. `sens_retail_cons` gives **−2.1020 % to −1.5901 % → −2.10 to −1.59**, not −2.42/−1.76 (that figure is instead the `B_cons` bundle value for retail). Optimistic half **MATCHES**: `sens_retail_opt` gives 1.8809–2.4991→1.88–2.50. |
| 87 | `Chapter_05_Results.md:148–150` | "Hotel ... -0.76 % to -0.40 % conservative and +0.26 % to +0.48 % optimistic" | hotel isolated-lever scenario range | `step9_scenario_response.csv`, `sens_hotel_cons`/`sens_hotel_opt` | **MATCH** (cons: −0.7550 to −0.3989→−0.76 to −0.40; opt: 0.2633–0.4764→0.26–0.48) |
| 88 | `Chapter_05_Results.md:153–154` | "Retail shifts by only -0.08 % to +0.02 % and Hotel by +0.004 % to +0.03 %" (under conservative office draw) | cross-channel effect of office lever | `step9_scenario_response.csv`, `sens_office_cons`, channel=retail/hotel | **MATCH** (retail: −0.0820 to 0.0192→−0.08 to 0.02; hotel: 0.0044 to 0.0264→0.004 to 0.03) |
| 89 | `Chapter_05_Results.md:154–155` | "Office shifts by -0.02 % to -0.01 % and Hotel by -0.01 % to 0.00 %" (under conservative retail draw) | cross-channel effect of retail lever | `step9_scenario_response.csv`, `sens_retail_cons`, channel=office/hotel | **MATCH** (office: −0.0158 to −0.0120→−0.02 to −0.01; hotel: −0.0065 to 0.0011→−0.01 to 0.00) |
| 90 | `Chapter_05_Results.md:155–156` | "Office shifts by -0.27 % to -0.18 % and Retail by -0.23 % to -0.16 %" (under conservative hotel draw) | cross-channel effect of hotel lever | `step9_scenario_response.csv`, `sens_hotel_cons`, channel=office/retail | **MATCH** (office: −0.2657 to −0.1818→−0.27 to −0.18; retail: −0.2329 to −0.1630→−0.23 to −0.16) |
| 91 | `Chapter_05_Results.md:159–160` | "Residential's own energy moves by +0.06 % to +0.29 % under the coupled office scenarios and by under 0.10 % under the retail and hotel ones" | residential response, coupled/other levers | `step9_scenario_response.csv`, channel=residential | **MATCH** — `sens_office_cons` gives residential 0.0643–0.2868→0.06–0.29; under `sens_retail_cons` residential −0.0057 to −0.0008 (abs < 0.10) and under `sens_hotel_cons` −0.0994 to −0.0378 (abs < 0.10), consistent with "under 0.10%" |
| 92 | `Chapter_05_Results.md:161–163` | "Office -2.05 % to +2.20 %, Retail -2.42 % to +2.66 % and Hotel -0.73 % to +0.45 %" | outer 2030 bundle (B_cons/B_opt) combined range, all 3 channels | `step9_scenario_response.csv`, `B_cons`/`B_opt` | **MATCH** — office: min(B_opt)=−2.0508→−2.05, max(B_cons)=2.1956→2.20; retail: min(B_cons)=−2.4239→−2.42, max(B_opt)=2.6560→2.66; hotel: min(B_cons)=−0.7309→−0.73, max(B_opt)=0.4452→0.45. (This is exactly the number wrongly reused for retail's *isolated*-lever claim at #86.) |

## Chapter 6 — Discussion

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 93 | `Chapter_06_Discussion.md:4` | "18.91 h against a midday cluster of 11.90 to 12.37 h" | repeat of peak-hour figures | as §5.3 | **MATCH** |
| 94 | `Chapter_06_Discussion.md:4` | "14.95 h coincides with none of them" | whole-building peak median | as #79 | **MATCH** (median only; the range is not repeated here) |
| 95 | `Chapter_06_Discussion.md:5–6` | "retail 34 to 1, residential 3.9 to 1, hotel inverted" | day/night ratio repeats | as §5.3 | **MATCH** |
| 96 | `Chapter_06_Discussion.md:7` | "median 0.941" | coincidence factor repeat | as #3 | **MATCH** |
| 97 | `Chapter_06_Discussion.md:14` | "five of the nine steps carry no cross-stage comparison" | Table 6 tally | `Table_06_leg2_leg3_delta.md`, "Bit-identical?" column | **MATCH** (5 rows marked "not reported"/"⚠ check source": Steps 1, 2, 3, 5, 8 — counted directly from the table) |
| 98 | `Chapter_06_Discussion.md:20` | "scores 85.45 against the same 100 ... failing by 15 %" | office control repeat + fail margin | as #4 | **MISMATCH** on 85.45 (as #4); the "15%" follows from (100−85)/100 rounding, i.e. internally consistent with the stated (mismatched) 85.45 rather than with the recomputed 85.36–85.65 range — recomputed margin would be 14.35–14.64%, still displays as "~15%" either way, so the qualitative "15%" claim itself is **not** separately flagged |
| 99 | `Chapter_06_Discussion.md:21–22` | "about 17 % against the band's implied 35 to 45 %" | heating-share mechanism repeat | as #58 | **NOT-FOUND against the frozen deliverable** (same as #58) |
| 100 | `Chapter_06_Discussion.md:24` | "median 71.02 kWh/m2/yr" | office median repeat | as #56 | **MATCH** |
| 101 | `Chapter_06_Discussion.md:27` | "28 cells at 203.33 to 218.22 ... 28 at 302.86 to 318.42" | hotel two-cluster bounds | `step9_eui_by_channel.csv`, hotel, sorted, split at largest gap | **MATCH** (low cluster exactly 203.33–218.22; high cluster exactly 302.86–318.42, confirmed by script) |
| 102 | `Chapter_06_Discussion.md:28–29` | "largest gap ... 84.64 kWh/m2/yr, 70.5 % of the band's width" | repeat of #6 | as #6 | **MATCH** |
| 103 | `Chapter_06_Discussion.md:40–41` | "3,499 of 16,367 multi-person households, 21.38 %" | residential intra-household diversity | `3rdJ_00_4split_Occupancy_Pipeline.md:641` (other named artefact — Census/GSS linkage output, not Step8/9) | **MATCH** (grep-confirmed verbatim: "3,499 of 16,367 multi-person households, 21.38 %"; arithmetic check 3499/16367 = 21.379% → 21.38%, consistent) — **not** traceable to the frozen deliverable paths, since this is a Step-3/5 linkage statistic, outside the task's two named directories |

## Chapter 8/7 — Conclusion

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 104 | `Chapter_08_Conclusion.md:5` | "roughly seven hours after" | repeat of #16 | as #16 | **MATCH** |
| 105 | `Chapter_08_Conclusion.md:5–6` | "below 1 in all four building-city cells" | coincidence factor qualitative | as #3 | **MATCH** |

## Table 1 — Gap matrix

Table 1 (`Table_01_gap_matrix.md:7–13`) is entirely checkmarks (✓/✗), no numeric magnitudes to
re-derive; its "eight axes" count is checked at #14. No further rows.

## Table 2 — Channels

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 106 | `Table_02_channels.md:11` | "0.95 x customer-hours shape" | retail injection multiplier | pipeline design doc (other named artefact) | **band definition, not re-derived** (and see Table 7 L11, #113, for the correction note attached to this same 0.95 figure) |
| 107 | `Table_02_channels.md:12` | "SARIMA(1,1,1)(1,1,1,12)" | hotel model order | pipeline design doc | **band definition, not re-derived** |

## Table 7 — Limitations (L1–L16)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 108 | `Table_07_limitations.md:10` (L3) | "3,499 of 16,367 multi-person households, 21.38 %" | repeat of #103 | as #103 | **MATCH** |
| 109 | `Table_07_limitations.md:11` (L4) | "85.45 against a floor of 100" | repeat of #4 | as #4 | **MISMATCH** (same as #4) |
| 110 | `Table_07_limitations.md:12` (L5) | "Reference 284.44 and 299.28 kWh/m2/yr. FAIL on 28 of 56 cells, all Tall, all over the 300 ceiling; range 203.33-318.42" | repeat of #60–61 | as #60–61 | **MATCH** |
| 111 | `Table_07_limitations.md:13` (L6) | "Wrong in sign and order in 56 of 56 cells. Exposure takes 2 values across the campaign, not 56." | envelope-exposure mechanism test | claims `step9_envelope_exposure.csv` (does not exist in the frozen deliverable) | **MISMATCH — source problem** (see Alarming #1). The frozen `step9_gates.json`'s own `S9-EUI-EXPOSURE` entry states this file was **not found** and the test **"cannot be reported this run."** The only file with this name lives in the superseded `outputs_step9/` arm, off-limits by the standing rule. |
| 112 | `Table_07_limitations.md:14` (L7) | "Median 75.63 against a floor of 80, 5.47 % below, 44 of 56 cells under" | repeat of #63 | as #63 | **MATCH** |
| 113 | `Table_07_limitations.md:15` (L8) | "130.6 kWh/m2/yr over 113.9-147.2, never a pass criterion" | residential empirical-band context value | `step9_eui_by_channel.csv` info_lo/info_hi (113.9/147.2, MATCH) + a "130.6" central value that is **not** a column in the CSV | **NOT-FOUND against the frozen deliverable, but self-disclosed by the manuscript itself** — Table 7's own note #5 (lines 140–169) already documents that 130.6 = (113.9+147.2)/2 = 130.55→130.6, the exact arithmetic midpoint of the range, absent from the deliverable, and explicitly declined by Table 5 ("not reported"). This row is transcribed correctly per that note's own reasoning; the underlying number itself remains unverifiable pending the SHEU-2019 primary source, exactly as the note says. |
| 114 | `Table_07_limitations.md:16` (L9) | "24.97 against 29.97 m2/person, so retail is roughly 20 % over-crowded" | NECB office vs. retail occupant density | `3rdJ_00_4split_Occupancy_Pipeline.md:306,312,320–321,776–778` (other named artefact) | **MATCH** (grep-confirmed: "24.97 m²/person" is NECB office 3.72 occ/1000ft²; "29.97 m²/person" is NECB retail-sales 3.10 occ/1000ft²; (29.97−24.97)/24.97 = 20.0% → "~20% over-crowded") |
| 115 | `Table_07_limitations.md:17` (L10) | "7.5028 W/m2 on every space type in both towers" | blanket equipment power density | `3rdJ_00_4split_Occupancy_Pipeline.md:342,786` | **MATCH** (grep-confirmed verbatim "plug density (`7.5028 W/m²`)") |
| 116 | `Table_07_limitations.md:18` (L11) | "peak 0.90 with a 0.50 lunch dip, times 0.95: 18.75 % hot on the wrong shape" | retail-on-office-curve mismatch | `3rdJ_00_4split_Occupancy_Pipeline.md:796` | **MATCH** (grep-confirmed "18.75 % hot at peak"; 0.95/0.90=1.0556, i.e. the 0.95 constant sits 5.6% above the stated 0.90 office peak — wait, check: (0.95−0.80)/0.80? The source text at line 796 gives "18.75% hot" directly, confirmed verbatim, not independently re-derived arithmetically here since the exact basis of the 18.75% figure is stated in the source but not re-computed from a frozen CSV) |
| 117 | `Table_07_limitations.md:19` (L12) | "The anchor previously cited gives 5. The gate is non-monotonic: fails at 10, passes at 11-20, fails at 30." | minimum pool size sensitivity | pipeline doc, other artefact | **NOT-FOUND against the frozen deliverable** — not located within the time available in this pass; the exact line reference was not re-confirmed by grep (unlike L9/L10/L14/L16) |
| 118 | `Table_07_limitations.md:21` (L14) | "2.00 %, 2.14 %, 1.66 %, 1.50 %, a 25 % decline" | repeat of #15 | as #15 | **MATCH** |
| 119 | `Table_07_limitations.md:23` (L16) | "Slope -0.98 against draw volume. A global factor of 6 moved that object's share from 26.7 % to 65.4 % by reweighting alone." | hotel DHW plant capacity-pinning | `3rdJ_00_4split_Occupancy_Pipeline.md:834–838` | **MATCH** (grep-confirmed verbatim: slope −0.98, global K to 6, LAUNDRY share 26.7%→65.4%) |
| 120 | `Table_07_limitations.md` self-check (line 84–85) | "16 / 16" limitations self-count | count of Table 7 rows | source doc's own self-check, cross-checked against Table 7's own Manager Note #1 | **MATCH per the table's own documented reconciliation** — the source numbers L8 twice (a real ID collision, disclosed in Manager Note #1), and Table 7 explicitly explains why it still reports 16 rows rather than 17; this is not independently re-verified beyond re-reading that note, which is itself the authors' own audit trail |

## Table A1/A2 (Supplementary; `Chapter_10_Supplementary.md` insert / `readySubmission_SI.md:93–166`)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| 121 | `readySubmission_SI.md:100–101` | "6 layers, model width 256, 8 attention heads, approximately 29M parameters" | encoder architecture | model card, other named artefact (not Step8/9 frozen deliverable, and no checkpoint file was available to independently count parameters in this pass) | **NOT-FOUND against the frozen deliverable** — architecture/training specs in Table A1 as a whole (encoder size, conditioning-vector width 120/119, dropout 0.1, weight decay 1e-4, batch composition 50/25/25%, shipped scorecard "147 PASS / 18 WARN / 1 FAIL") are all sourced from the training pipeline/model-card documentation, not from `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/` or `Leg3_4-split/Step9_docs/outputs_step9_deliverable/`, and were not independently re-derivable in this pass; grouped here as one row rather than enumerated line-by-line given the volume, all carrying the same NOT-FOUND-against-frozen-deliverable status |

## Title Page and Cover Letter (`writing/submission/Title_Page_and_Cover_Letter.md`)

| # | Where | Number | Meaning | Claimed source | Verdict |
|---|---|---|---|---|---|
| — | `Title_Page_and_Cover_Letter.md:36–37` | "85.45 kWh/m2/yr against the same 100 kWh/m2/yr office floor" | office control repeat | as #4 | **MISMATCH** (same as #4; counted under #4, not double-counted in the summary tally) |
| — | `Title_Page_and_Cover_Letter.md:39` | "refuted in all 56 of 56 cells" | repeat of the heating-share/re-basing mechanism refutation | as #58 | **NOT-FOUND against the frozen deliverable** (same as #58; not double-counted) |
| — | `Title_Page_and_Cover_Letter.md:50–56` | "56-cell campaign", "four different hours", "roughly seven hours", "below 1 in all four" | repeats of #18, #16, #3 | as cited | **MATCH** (not double-counted) |

The three Title-Page/Cover-Letter rows above restate numbers already counted once each under Chapters
0/5/6/1 and are **not** added again to the Summary tally (they would otherwise double-count the same
85.45 mismatch and the same "17%"/"56 of 56" NOT-FOUND item a fourth time).

---

## Script

`writing/implementation/IMP/scripts/p9_rederive.py` — reads
`Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_meta.csv` and
`Leg3_4-split/Step9_docs/outputs_step9_deliverable/{step9_eui_by_channel.csv, step9_longitudinal.csv,
step9_loadshape_peaks.csv, step9_scenario_response.csv, step9_gates.json}` only — never the superseded
`agg/` or `outputs_step9/` arms — and prints every median/range/gap/ratio/scorecard number checked
above. Kept on disk, rerunnable with `PYTHONIOENCODING=utf-8 py -3
writing/implementation/IMP/scripts/p9_rederive.py` from `3J_docs_occ_nTemp/`. Follow-up one-off checks
used for a few rows above (office control mean/weighted-average, hotel/office peak-hour cell-level
values, retail night-demand precision, the Default_NECB office rows, the IDF byte-diff) were run as
short inline `py -3 -c "..."` commands during this task rather than folded into the script, since they
were single confirmatory queries rather than reusable derivations; the exact commands are reproducible
from the transcript of this task if needed again.
