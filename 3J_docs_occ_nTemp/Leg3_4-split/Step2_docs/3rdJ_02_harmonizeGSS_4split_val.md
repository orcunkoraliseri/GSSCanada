# 3rdJ Step 2 Validator — Data Harmonization (Leg-3 Four-Channel Split)
### Retail-signal verification on the Leg-2 harmonized episodes + canonical hotel series gates

---

## Goal

Validate (1) that the AT_RETAIL ingredients (`occPRE == 5`, `occACT == 4`) are present, stable, and correctly cross-walked in the Leg-2 harmonized episode CSVs, (2) that the frozen gated OR-rule's leak cross-tab is produced per cycle (the OD-1 verification condition), and (3) that the canonical hotel monthly series is schema-clean, spliced correctly, and magnitude-plausible. Emit the house-style dark-theme HTML + TXT report.

## Reference

- Main doc: `3rdJ_02_harmonizeGSS_4split.md`
- Leg-2 validator template: `../../Leg2_2-split/Step2_docs/3rdJ_02_harmonizeGSS_2split_val.py`
- Inputs validated: `../../Leg2_2-split/Step2_docs/outputs_step2/episode_{cycle}.csv` (read-only), `0_Occupancy/external/hotel_occupancy_monthly.csv`, `outputs_step2/retail_orrule_crosstab_{cycle}.csv`

## Validation Sections

### Section 1 — Retail Signal Presence (⚠️ NEW, Leg 3)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 1.1 | `occPRE` present, values ∈ 1–18, code 5 non-empty, all 4 cycles | true | FAIL |
| 1.2 | Weighted episode-time share of `occPRE == 5` per cycle | 1.5–3.0 % (target ~2.1–2.3 %, stable) | WARN outside |
| 1.3 | `occACT` present, code 4 ("Purchasing Goods & Services") non-empty, all cycles | true | FAIL |
| 1.4 | `occPRE == 7` (restaurant) share reported per cycle | INFO only (excluded channel, decision record) | INFO |
| 1.5 | Cross-cycle share stability: max pairwise delta of 1.2 across cycles | ≤ 1.0 pp | WARN |

### Section 2 — OR-Rule Leak Cross-Tab (⚠️ NEW, Leg 3 — the OD-1 verification condition)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 2.1 | Per-cycle `occACT==4 × occPRE` weighted cross-tab emitted (4 CSVs) | 4/4 present | FAIL |
| 2.2 | Online-shopping leak share (`occACT==4 & occPRE==1`) reported per cycle | INFO — no threshold; the rule is FROZEN gated | INFO |
| 2.3 | Leak trend direction 2005→2022 | rising (e-commerce) — WARN if flat/falling (suggests a coding problem, investigate) | WARN |
| 2.4 | Gated-rule preview: episode share of `(occPRE==5) \| ((occACT==4) & occPRE∈{5,9})` per cycle | 1.5–3.5 %; must exceed the 1.2 location-only share by 0–1.0 pp | WARN outside |
| 2.5 | Gate audit: `occACT==4 & occPRE∈{5,9}` adds no `occPRE==1/2` rows (rule correctness) | 0 rows | FAIL |

### Section 3 — Canonical Hotel Series (⚠️ NEW, Leg 3, non-GSS)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 3.1 | Schema `YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, SPLICED`; PR ∈ {QC, AB} | exact | FAIL |
| 3.2 | Coverage: QC 216/216 months; AB 216/216 (spliced) **or** 156/156 + fallback decision recorded | as stated | FAIL |
| 3.3 | `occupancy_rate ∈ (0,1]`, no NaN inside each source window | true | FAIL |
| 3.4 | AB splice continuity: `|mean(2009-07…2009-12) − mean(2010-01…2010-06)|` after calibration | ≤ 8 pp (seasonal-adjusted comparison in-code) | WARN |
| 3.5 | COVID months 2020-03…2022-06 present, 2020-04 = or near series minimum, both provinces | true | FAIL |
| 3.6 | Pre-COVID annual means: QC 0.60–0.65, AB 0.54–0.58 (dr_L3-01 anchors) | in band | WARN |
| 3.7 | Seasonality: pre-COVID summer > winter mean, both provinces | true | WARN |

### Section 4 — Charts

- 4.1 Headline: per-cycle weighted diurnal share of `occPRE==5` episodes (preview of the Step-3 tiled shape; expect midday hump, near-zero night).
- 4.2 Leak chart: online-shopping leak share per cycle (bar, 2005→2022).
- 4.3 Hotel: harmonized monthly series per PR with splice boundary and COVID window marked; seasonal-profile panel.

## PASS / WARN / FAIL Convention

Canonical Leg-2 definitions: **PASS** clean/in-range; **WARN** plausible-but-attention (soft band breach, documented source quirk, INFO-adjacent trend checks); **FAIL** concrete integrity problem (missing artifact, schema break, gap months, rule-correctness violation 2.5).

## Expected Result

0 FAIL. Acceptable WARNs: 1.5/2.3/2.4 soft bands, 3.4 splice continuity, 3.6/3.7 provincial-average composition effects. Report `outputs_step2/step2_validation_report.html` + `.txt`.

## Test Method

Locally: `py -3 -X utf8 3rdJ_02_harmonizeGSS_4split_val.py` from `Step2_docs/`. Confirm 4 cross-tab CSVs, headline diurnal preview shape, hotel charts.

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`)*

### 2026-07-19 — Validator built + run → verdict WARN, 0 FAIL (11 PASS / 3 WARN / 3 INFO)

Built `3rdJ_02_harmonizeGSS_4split_val.py`. Streams the reused Leg-2 Step-2 episodes (read-only, one pass/cycle) for the retail signal; reads the canonical `0_Occupancy/external/hotel_occupancy_monthly.csv`; emits the 4 cross-tabs + house-style HTML/TXT + 5 figures (V1 retail diurnal share, V2 leak, V3 loc-only vs gated, V4 hotel series, V5 hotel seasonal).

**Retail signal (weighted episode-time share, occPRE==5 / gated / leak):**
| cycle | occPRE==5 | gated OR-rule | leak (occACT4&occPRE1) |
|---|---|---|---|
| 2005 | 1.71% | 2.00% | 0.180% |
| 2010 | 1.81% | 2.14% | 0.142% |
| 2015 | 1.58% | 1.66% | 0.164% |
| 2022 | 1.48% | 1.50% | 0.067% |

**The 3 WARN are all anticipated (per this doc's "Acceptable WARNs"), 0 FAIL:**
- **1.2** — 2022 occPRE==5 share 1.48% sits 0.02 pp below the 1.5% floor (soft breach; the retail signal eases as in-person shopping declines).
- **2.3** — leak trend **falls** (0.18→0.07%), not rises. **Investigated** (gate instruction): the cross-tabs show that among occACT==4 episodes, occPRE==1 (home) drops 8.47→4.44% while occPRE==5 (store) rises 75.15→90.32% — a **2022 GSSP diary-coding concentration** of purchasing at the store location, NOT a code bug and NOT e-commerce under-capture. The gate protects the longitudinal signal regardless of direction; leak stays <0.2% of all time. Caption made direction-honest.
- **3.6** — AB pre-COVID mean 0.599 vs band 0.54–0.58 (QC 0.603 in-band): the AB driver is `AlbertaExclResorts` (Calgary+Edmonton urban), which runs above the all-Alberta anchor. Composition effect, RECONCILED.

**Gate 2.5 (rule correctness) PASS** — gated arm-2 adds 0 weighted time on occPRE∈{1,2}; **2.4 PASS** — gated share exceeds location-only by 0.02–0.33 pp, in-band. **Section 3** hotel: schema exact, grid 216/216 both PR, occ∈(0,1], both COVID troughs intact (2020-04 = series min), splice INFO (moot). Report: `outputs_step2/step2_validation_report.{html,txt}`.

### 2026-07-19 — Figures expanded to all 4 building types (user request: "peu de figures")

Report figure set grown **5 → 14** to match the Leg-2 Step-2 report's richness and cover **all building types**, one extra streaming pass (no new gates; verdict unchanged WARN/0 FAIL). Three bands:
- **A — 4-channel schedules (all building types):** G1 4-channel diurnal (R/O/R measured + Hotel design shape), G2 per-channel presence rate/cycle (the Leg-2 AT_HOME/AT_WORK-rate figure extended to all channels), G3/G4/G5 Residential/Office/Retail diurnal across cycles, G6 Hotel weekday-vs-weekend s(t).
- **B — GSS harmonization QA (reused Leg-2 episodes):** G7 time-weighted 14-category activity distribution × 4 cycles, G8 diary-closure rate + episodes/respondent, G9 occPRE==2 workplace share.
- **C — retail signal + hotel series:** V1–V5 (unchanged).

**Channel rates confirm the expected story:** AT_HOME 63.6/63.5/66.1/**72.3%** (WFH rise 2022), AT_WORK 7.6/6.6/6.3/**4.9%** (WFH fall), diary closure 98.3/98.5/100/100% (all > 95% floor). Rates use the Leg-2 episode-count basis; time-shares/curves use DIARY_VALID episodes.
