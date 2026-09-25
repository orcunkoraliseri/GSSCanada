# Item 2: hotel 2030 recovery levels (AB 0.615, QC 0.635)

Date: 2026-09-25. Read-only check. No manuscript or chapter file was edited.
Paths are relative to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`.

Manuscript sentence (`3J_docs_occ_nTemp/writing/chapters_v2/02_Framework.md:36`):
> "For 2030, r is the 2019 monthly pattern rescaled to a post-pandemic recovery level of 0.615 in
> Alberta and 0.635 in Quebec [REF NEEDED: source of the 2023 to 2025 hotel recovery levels]."

## 1. Where the numbers are hard-coded

- `3J_docs_occ_nTemp/Leg3_4-split/Step6_docs/3rdJ_06_hotel_sarima_4split.py:111`
  `ANCHORS_2023_2025 = {"QC": 0.635, "AB": 0.615}`
- The same file, lines 372-382 (`anchored_2019_central_path`): `shape = y2019 / y2019.mean()` then
  `shape * ANCHORS_2023_2025[pr]`.
- They are also repeated as a "sanity anchor" (gate 8.6, plus or minus 0.05, WARN) in
  `Step6_docs/3rdJ_06_trackB_hotel_builder_prompt.md:66-67,90`,
  `Step6_docs/3rdJ_06_longitudinalForecasting_4split.md:84` and `..._4split_val.md:54`.
  The runbook reports gate 8.6 as "PASS (by construction)" (`3rdJ_06_longitudinalForecasting_4split.md:242-243`),
  so the anchor check and the central path use the same number, and the check can never fail.

## 2. What the numbers mean: an occupancy RATE, not a ratio to 2019

The 2019 shape is divided by its own mean, so it averages 1.0. Multiplying by the anchor makes the
2030 central annual mean exactly 0.615 (AB) and 0.635 (QC). So each anchor is an **annual average
occupancy rate** (61.5 %, 63.5 %), not a fraction of 2019. The builder prompt says the same:
"2023-2025 actuals QC ~0.635 (Montreal ~0.666 in 2025), AB ~0.615 (Calgary ~0.63)" (line 66-67).

Compared with the repo's own 2019 means (simple mean of 12 months, `0_Occupancy/external/hotel_occupancy_monthly.csv`):
- AB 2019 = 0.5411, so the 2030 central path is 0.615 / 0.5411 = 1.137 times 2019.
- QC 2019 = 0.6033, so the 2030 central path is 0.635 / 0.6033 = 1.053 times 2019.

This matters because the deep-research report the anchors come from names the central scenario
"Full Recovery (Central/Default) ... returns to 100% of 2019 levels". Our central path sits 14 %
(AB) and 5 % (QC) above our own 2019 level.

## 3. Where they came from

Origin: `3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-09_hotel_2030_forecast_REPORT.md:48`
(AI-written deep-research report, Table 4 "Sanity anchors"):
> "Latest available (2023-2025) ... | Quebec (QC): ~63.5% (Montréal: ~66.6% in 2025)
> Alberta (AB): ~61.5% (Calgary: ~63.0% in 2024-2025) | CBRE Hotels Canada Outlook (late 2025/early 2026);
> Tourisme Québec monthly statistics (2025)"

The reference behind it (same file, line 107) is:
> "CBRE Hotels. (2025). Canada Hotel Outlook: late 2025/2026 updates. CBRE Hotels Research.
> [Link](https://www.cbre.ca/en/insights/reports)"

That link goes to a general reports landing page, not to a document. No page, table or edition is
given. The same Table 4 also cites "Statistics Canada Table 24-10-0048-01 ... Travel accommodation
survey", which the report itself calls "Discontinued" (line 116), so it cannot be a 2019-2025 source.
The script docstring (lines 61-62) calls the values "the real 2023-2025 CBRE/STR-reported recovery
anchor", but nothing in the repo shows that anyone ever opened a CBRE or STR document.

No other file in the tree gives an origin. Grep for `0.615` / `0.635` / `61.5 %` / `63.5 %` found only:
- the Step 6 files above;
- `deepResearch_v2/dr_L3v2-01B_alberta_ab_monthly_REPORT.DISCARDED_FABRICATED.md:83` (AB May 2011 = 0.6150,
  in a report already discarded as fabricated; not related);
- `deepResearch_v2/Hotel Market Occupancy Research.txt:440,1559` (Calgary May 2018 = 0.635; a coincidence).

## 4. Check against our own official data (Quebec)

The repo holds the official ISQ dashboard exports for 2019-2026
(`3J_docs_occ_nTemp/Leg3_4-split/deepResearch_v2/<year>-province-mensuelle.txt`, source line:
"Institut de la statistique du Québec, Enquête sur la fréquentation des établissements d'hébergement
(régions et MRC/villes)", update "Thursday, July 02, 2026"). The "Taux d'occupation, Province" row,
column "Total", reads:

| Year | ISQ annual rate (Total) |
|---|---|
| 2019 | 60.8 % |
| 2022 | 57.1 % |
| 2023 | 61.4 % |
| 2024 | 60.9 % |
| 2025 | 60.8 % |

- 2023-2025 mean = (61.4 + 60.9 + 60.8) / 3 = **61.0 %**, not 63.5 %. No year from 2023 to 2025 reaches 63.5 %.
- The 2023-2025 mean over 2019 is 61.0 / 60.8 = **1.004**: Quebec came back to its 2019 level, no higher.
- Other ratios also miss 0.635: 2022/2019 = 0.939; 2023/2019 = 1.010.
- The report's own 2019 figure for Quebec ("~65.0%", line 46) and 2022 figure ("~58.0%", line 47)
  do not match ISQ either (60.8 %, 57.1 %).

So the official source we already cite for Quebec contradicts the 0.635 anchor by about 2.5 points.

## 5. Check against our own data (Alberta)

The Alberta series in the repo (Government of Alberta tourism market monitor, `hotel_raw_AB/AB_MM_*.pdf`,
`deepResearch_v2/hotel_ab_monthly_2012_2022.csv`) ends at 2022-11 and the ingested series ends at 2022-09.
There is no 2023-2025 Alberta figure in the repo, so 0.615 cannot be derived from our data.
- 0.615 is not our AB 2022 mean (0.548, 9 months) or 2019 mean (0.541).
- 0.615 / 0.541 = 1.137, which is not a ratio that appears in any of our sources.
- The nearest real values in our AB series are the 2011-2014 annual means (0.633-0.682), which are
  before the 2015 oil downturn and are not "2023-2025".

## 6. Outside-world check: not done

The task asked for a web check of Travel Alberta, the Alberta tourism monitor, ISQ, CBRE, STR and the
Hotel Association of Canada. That check was **not run**. The project CLAUDE.md rule "Deep research is
EXTERNAL" says the assistant never verifies citations itself; the author runs that step in Gemini
using a prompt. So this file does not say whether a CBRE or STR document with 61.5 % / 63.5 % exists.
Given sections 4 and 5, this does not change the verdict. Even if a CBRE figure existed, it would
disagree with the ISQ series the paper already uses for Quebec.

If the author wants to keep an Alberta post-2022 level, the question for an external prompt would be:
"Government of Alberta Tourism Market Monitor (open.alberta.ca), annual Alberta-wide hotel occupancy
for 2023, 2024 and 2025; quote the exact figure, page and URL; NOT FOUND beats an invented number."

## 7. What a defensible replacement would look like (for the author to decide; nothing was changed)

- Quebec: the observed ISQ 2023-2025 mean, 0.610, is citable from the ISQ source already in the
  reference list. It is essentially equal to 2019 (ratio 1.004).
- Alberta: no observed post-2022 value exists in the repo. The simplest defensible choice is the
  "100 % of 2019" central value the scenario design already names (Alberta 2019 mean 0.541), or an
  Alberta tourism market monitor figure if the author finds one.
- Either change would alter the 2030 hotel inputs and therefore the published 2030 results; that is a
  modelling decision for the author, not something to fix in the text alone.

## VERDICT

VERDICT: UNSOURCED. The two values come only from an unvetted AI-written deep-research table
(`dr_L3-09_hotel_2030_forecast_REPORT.md:48`) that cites a generic CBRE landing page. They are annual
occupancy rates, not ratios to 2019. The Quebec value is contradicted by the official ISQ series in
the repo (2023-2025 mean 61.0 %), and no Alberta figure for 2023-2025 exists in the repo.
If the values are kept, state them as an assumption. Suggested manuscript wording:

> "For 2030, r is the 2019 monthly pattern rescaled to an assumed post-pandemic annual occupancy of
> 0.615 in Alberta and 0.635 in Quebec, chosen as scenario values rather than observed rates."

Preferred alternative for Quebec, if the author changes the input (this changes the 2030 results):

> "For 2030, r is the 2019 monthly pattern rescaled to the mean observed annual occupancy for
> 2023 to 2025, 0.610 in Quebec (Institut de la statistique du Québec)."

## 8. Addendum 2026-09-25 (manager, after the author allowed online checks)

Source: Government of Alberta Economic Dashboard, "Accommodation occupancy rate" (CBRE monthly averages),
API `https://api.economicdata.alberta.ca/data?table=CBRE_Occupancy_Percentage&GeoName=Alberta;Quebec&Indicator=Occupancy%20%`,
fetched 2026-09-25, saved as `item2_ab_qc_cbre_occupancy_api_2026-09-25.json` (258 monthly rows, 2015-11 to 2026-07).
Alberta = "Alberta (excluding resorts)".

| Year | Alberta (12-month mean) | Quebec, CBRE series (12-month mean) |
|---|---|---|
| 2019 | 54.11 % | 68.47 % |
| 2022 | 54.17 % | 59.39 % |
| 2023 | 58.80 % | 66.59 % |
| 2024 | 59.99 % | 65.89 % |
| 2025 | 60.27 % | 65.13 % |

- The Alberta 2019 mean (54.11 %) equals the repo's own AB 2019 mean (0.5411), so this is the same series the paper
  already uses for Alberta, now extended past 2022.
- Alberta 2023-2025 mean = (58.80 + 59.99 + 60.27) / 3 = **59.7 %** (0.597), not 61.5 %. Ratio to 2019 = 1.103.
- Quebec: the CBRE series is hotels only and runs higher than ISQ (all establishments). Its 2023-2025 mean is 65.9 %;
  ISQ's is 61.0 %. Neither gives 63.5 %. The paper's Quebec series is ISQ, so ISQ is the consistent choice (0.610).
- Updated verdict: both anchors are UNSOURCED, and both now have an observed, citable replacement from the sources the
  paper already cites: **Alberta 0.597, Quebec 0.610** (2023-2025 means). Using them changes the 2030 hotel inputs
  (AB down 1.8 points, QC down 2.5 points) and so needs the hotel 2030 cells re-run; that is the author's call.
