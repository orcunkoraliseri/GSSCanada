# 3rdJ Step 3 Validator — Merge & Tiling (Leg-3 Four-Channel Split)
### Section 11 — AT_RETAIL channel gates · Section 12 — legacy bit-identity

---

## Goal

Validate the Leg-3 merger/tiler outputs: the new `retail_30min.csv` channel (shape, alignment, encoding, dr_L3-06 diurnal targets, exclusivity) and the **bit-identity of every legacy output** vs Leg-2 (the conservative-variant proof). Emit the house-style dark-theme HTML + TXT report.

## Reference

- Main doc: `3rdJ_03_mergingGSS_4split.md`
- Leg-2 validator (Sections 1–10 ported): `../../Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS_2split_val.py` + its val doc (Section-9 AT_WORK template)
- Gate sources: dr_L3-06 (diurnal targets), OD-1 freeze (leak cross-tab), pipeline VALIDATION PLAN table

## Validation Methods

| # | Method | Source | Notes |
|---|---|---|---|
| 1–10 | Row counts, merge keys, derived features, HETUS 144-slot integrity, cross-cycle, summary stats, 30-min downsampling, co-presence, AT_WORK channel, office conditioning | Leg 2 (ported) | run unchanged on the Leg-3 outputs |
| 11 | **AT_RETAIL 30-min channel** | ⚠️ NEW (Leg 3) | headline |
| 12 | **Legacy bit-identity vs Leg-2** | ⚠️ NEW (Leg 3) | the additive-safety proof |

## Section 11 — AT_RETAIL Channel Checks (⚠️ NEW, Leg 3)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 11.1 | `retail_30min.csv` shape | (N, 49) = occID + RETL30_001..048 | FAIL |
| 11.2 | occID alignment to `hetus_30min.csv` | exact row match | FAIL |
| 11.3 | Values ∈ {0, 1}; NaN count | binary only, 0 NaN | FAIL |
| 11.4 | Weekday 12:00–14:00 weighted rate, per cycle | **0.06–0.10** (dr_L3-06 CONFIRMED, central ≈ 0.079) | WARN outside |
| 11.5 | Saturday 13:00–16:00 weighted peak rate, per cycle | **0.09–0.12** (dr_L3-06, distinct Saturday gate) | WARN outside |
| 11.6 | Sunday peak rate, per province (respondent PR): QC 12:00–17:00 · AB 12:00–16:00 | **QC 0.04–0.07 · AB 0.06–0.10** (dr_L3-06, province-specific) | WARN outside |
| 11.7 | Night 00:00–05:00 mean rate, all day-types (slots 41–48 + 1–2 in the 4 AM-origin array) | **0.000–0.003** | WARN outside |
| 11.8 | All-day tiled daily-mean rate, per cycle | 2–8 % provisional project-chosen band; episode-time share ~2.1–2.3 % context reported | WARN outside |
| 11.9 | Exclusivity: cells with RETL30=1 ∧ hom30-source AT_HOME=1, and RETL30=1 ∧ WORK30=1 | ≈ 0 expected (gated rule + exclusive occPRE); WARN > 1 % of retail-positive cells | WARN |
| 11.10 | OR-rule leak verification: episode-level cross-tab `occACT==4 × occPRE` reproduced; gated rule adds no occPRE∈{1,2} rows | 0 violations | FAIL |
| 11.11 | Headline chart: mean diurnal AT_RETAIL curve per cycle × day-type (weekday/Sat/Sun, QC vs AB panels for Sunday) | qualitative: midday hump, Sat > weekday peak, compressed QC Sunday, ≈0 nights | visual |

> **Day-type/province subsetting.** 11.4–11.7 use `DDAY_STRATA` (1 = weekday, 2/3 = weekend split into Sat/Sun via the diary-day variable) and respondent `PR` — both already carried in `hetus_30min.csv`. Rates are `WGHT_PER`-weighted.

## Section 12 — Legacy Bit-Identity (⚠️ NEW, Leg 3)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 12.1 | SHA-256 of `merged_episodes.csv`, `hetus_wide.csv`, `hetus_30min.csv`, `copresence_30min.csv`, `work_30min.csv` vs Leg-2 `outputs_step3/` | identical | **FAIL** — retail must be purely additive |
| 12.2 | `merged_episodes.parquet` hash, or column-wise value equality if hash is non-deterministic | identical / equal | FAIL (record which comparison was used) |

## PASS / WARN / FAIL Convention

Canonical Leg-2 definitions. FAIL = missing output, wrong shape, non-binary values, occID mismatch, rule-correctness violation (11.10), **any Section-12 mismatch**. WARN = rate-band breaches (11.4–11.9 — real data may sit at band edges; document, don't force).

> **Threshold provenance (keep the Leg-2 discipline).** 11.4 weekday 0.06–0.10 = project-chosen, externally CONFIRMED by dr_L3-06; 11.5/11.6 = dr_L3-06-derived (medium confidence); 11.7 night = dr_L3-06; 11.8 = project-chosen provisional. Do not cite project-chosen bars to the literature.

## Expected Result

0 FAIL. Acceptable WARNs: marginal band-edge breaches on 11.4–11.8 (cycle- or province-specific), tiny 11.9 majority-vote edge overlaps. 13+ charts; headline = 11.11.

## Test Method

Locally: `py -3 -X utf8 3rdJ_03_mergingGSS_4split_val.py` from `Step3_docs/` (or `3rdJ_s3_4split_valonly.sh` via sbatch on the cluster). Inspect Sections 11–12 first, then the ported Sections 1–10 for regressions.

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`)*

### 2026-07-19 — Validator run → 120 PASS / 13 WARN / 0 FAIL

`3rdJ_03_mergingGSS_4split_val.py` (Leg-2 Sections 1–10 ported + new Section 11 + Section 12) run locally. **Verdict 0 FAIL.** Sections 1–10 (ported) all clean → no regression from the retail delta.

- **Section 12 (bit-identity)** — 12.1 all 5 CSV legacy outputs SHA-256 identical to Leg-2; 12.2 parquet SHA-256 identical (method=sha256, deterministic here). PASS.
- **Section 11 (AT_RETAIL)** — 11.1 shape (64061,49), 11.2 occID aligned, 11.3 {0,1}/0-NaN, 11.9 exclusivity 0/0, **11.10 leak-rule 0 violations (occACT==4 episodes with occPRE∈{1,2} = 0)** — all PASS. 11.11 headline diurnal charts (day-type + QC/AB Sunday panels) generated.

**The 13 WARN are diurnal band-edge/below-band breaches on dr_L3-06 *validation targets* (not forced):**
- **11.4 weekday 12:00–14:00 = 3.31–4.89%**, BELOW the dr_L3-06 0.06–0.10 target, all cycles. The raw GSS-tiled "shopping-location present" rate is **~half** the dr_L3-06 literature target (which derives from retail-sector foot-traffic, structurally higher than time-use presence). **Not a bug — a genuine signal-strength gap; carry to Step 4 (the model learns from this) and Step 6/8 injection.** ⚠️
- **11.5 Saturday 13:00–16:00** — 2005/2010 in band (9.01/9.34%), 2015/2022 below (8.37/6.50%) as in-person retail eases.
- **11.6 Sunday** — QC all in band (5.16–5.79%); AB 2010/2015 just below its 0.06–0.10 band (5.78–5.88%); 2005 no Sunday-stratum data.
- **11.8 all-day daily-mean** — 1.51–2.14%, below the 2–8% provisional bar (short episodes; recorded).

Reports: `outputs_step3/step3_validation_report.{html,txt}` (dark-theme house style, 15 chart sections incl. 11a diurnal-by-day-type and 11b Sunday QC-vs-AB panels; validator class `GSSMergeValidator4Split`). **Step 3 COMPLETE — Step-4 inputs (`retail_30min.csv` + bit-identical legacy) ready.**
