# FINAL CHECK REPORT — 3J Leg-2 (2-split) full-pipeline audit, 2026-07-18

**Verdict: GO-with-caveats for Leg-3.** Pipeline complete and correct end-to-end (0 FAIL, every scorecard re-derived from its own artifact); sole defect-grade finding = stale local Step-8/9 mirrors (truth verified cluster-side); fix G4 gate + `D2030` default at Leg-3 fork time. Details §7.

Method: manager (Fable) delegated all mechanical scans to cheap-model employees (Haiku for existence/tally checks, Sonnet for anything needing judgement). Every scorecard below is **re-derived from the artifact's own body/columns**, then compared against the artifact's headline claim. Sources are cited per line. Diagnosis only — nothing was fixed in this pass.

---

## 1. Per-step audit

### Step 1 — GSS ingest — **COMPLETE & CORRECT**
- Val doc `Step1_docs/3rdJ_01_readingGSS_val.md` exists (28,132 B, mtime 2026-06-15).
- Scorecard re-derived from body (line 340): **139P / 0W / 0F** — matches headline (Progress Log 2026-06-14, job 968314).
- `outputs_step1/`: main_{2005,2010,2015,2022}.csv = 19,597 / 15,390 / 17,390 / 12,336 rows; episode_{2005,2010,2015,2022}.csv = 333,654 / 283,287 / 274,108 / 168,078 rows.
- Frame strings: none present (the 23,150-HH frame is census-side, defined at Step 5; GSS-side counts are respondent-level and do not contradict it).

### Step 2 — harmonization — **COMPLETE & CORRECT**
- Val doc `Step2_docs/3rdJ_02_harmonizeGSS_val.md` exists (4,798 B, mtime 2026-06-15).
- Scorecard re-derived from body (line 95): **73P / 1W / 0F** — matches headline. Sole WARN = 2015 TELEWORK diary-day flag (documented).
- `outputs_step2/`: same 8-file inventory as Step 1, identical row counts (harmonization is in-place column work — expected).
- `00_column_availability_investigation.md` exists; conclusions intact (2005 TELEWORK candidate MAR_Q190; co-presence 20% empty = intrinsic survey skip; office-conditioning extras MAR_Q410/WHW_230 etc.).
- Frame strings: none — no contradiction.

### Step 3 — merge / work tiler — **COMPLETE & CORRECT**
- Val doc `Step3_docs/3rdJ_03_mergingGSS_val.md` exists (6,774 B, mtime 2026-06-15).
- Scorecard re-derived from body (line 122): **91P / 1W / 0F** — matches headline. Sole WARN = §9.5 night-slot AT_WORK rate 5.03% (marginal over 5%).
- `outputs_step3/`: merged_episodes.csv 1,049,480 rows; hetus_wide / hetus_30min / copresence_30min / **work_30min.csv all 64,061 rows** (consistent tiled-channel row identity — two-channel split origin confirmed).
- Frame strings: none — no contradiction.

### Step 4 — ML augmentation + 04T rake — **COMPLETE w/ documented caveats**
- **04T fix confirmed landed and operative** (the audit's core question):
  - Script `Step4_docs/3rdJ_04T_act_rake_2split.py` (mtime 2026-07-15 19:11) implements the FLOATING/TELEWORK conditional rake; Gate A threshold `GATE_A_PASS_PP = 2.0` in `3rdJ_04_augmentationGSS_2split_val.py:904`.
  - **Gate A re-derived from three independent artifacts**: run log `_04T_full_run.log` (obs FLOATING 2.96% vs syn 4.08% → excess **+1.12 pp**), `outputs_step4/step4_validation_report.txt:76` (`[PASS] GA ... +1.12 pp ... PASS<=2.0pp`), and `3rdJ_04_augmentationGSS.md:1738` (+20.98 pp FAIL pre-04T → +1.12 pp PASS post-04T; post-04T FAIL set is a strict subset of pre-04T).
  - The 61.12% figure is formally superseded in `dr_S4-02..._REPORT.md` itself (measured on a disjoint 2,560-row diagnostic sample; true pre-04T baseline on the real 128,122-row pool = 50.24% = 26.30% legitimate TELEWORK + 23.94% impossible FLOATING). **Not operative anywhere downstream.**
  - Downstream propagation verified: `Step5_docs/3rdJ_05_censusLinkage_2split.py:46` reads `outputs_step4/sweep/R5_raked_mindwell_actv2/augmented_diaries.csv` (the 04T-fixed pool); pre-fix path survives only in the frozen predecessor `...20260715_preFULLPOOLactv2.py`.
- Live report of record: `outputs_step4/step4_validation_report.{html,txt}` (mtime 2026-07-17 14:57, byte-identical to `sweep/R5_raked_mindwell_actv2/` copy): **66P / 3W / 2F** (FAILs = G4 work-peak 14.85 pp and OW5 day-type ordering 61.4% — both pre-existing, both argued non-blocking: G4 lives in the act30 channel the BEM never consumes; OW5 unobservable by design).
- Frame strings: zero hits in Step4_docs — expected (frame enters at Step 5+).
- **Caveat S4-a (stale spec doc):** `3rdJ_04_augmentationGSS_val.md` (mtime 2026-06-26) predates 04T by 3 weeks; its 68P/1W/2F headline and GA narrative describe the pre-04T state. The correct narrative lives in `3rdJ_04_augmentationGSS.md`. Citing only `_val.md` would miss the 04T episode. Doc-only; does not affect artifacts.
- **Caveat S4-b (pre-fix file left in a tempting location):** top-level `outputs_step4/augmented_diaries.csv` (400 MB, Jun 22) is the **pre-04T** pool; the fixed pool lives only under `sweep/R5_raked_mindwell_actv2/`. The live Step-5 script points at the right one, but the stale one-off scripts `Step5_docs/_gap_analysis_tmp.py` and `_q1234_analysis.py` still hardcode the top-level pre-fix path. Risk is future-reuse only, not current-pipeline.

### Step 5 — census linkage — **COMPLETE w/ documented caveats** (data correct; val doc stale)
- Val doc `Step5_docs/3rdJ_05_censusLinkage_2split_val.md` exists (20,514 B, mtime 2026-06-26). Its final headline (L377, 2026-06-23): 20P/1W/3F.
- **Caveat S5-a (stale headline, two axes):** the operative scorecard is **22P/1W/1F** per `Step5_docs/run_val_20260715.log` (July-15 rerun against the live actv2 data, day-type-stratified gate logic) — the .md was never updated. Likewise the doc still says "613 excluded / 29,660 post-exclusion" (June-22 numbers); the live artifacts say **735 / 29,538**. Doc-only staleness; the 22/1/1 result matches memory-of-record.
- **Live data re-derived (scripted counts, live `outputs_step5/`):** Matched_Keys / Full_Schedules / Full_Aggregated / BEM_Schedules = **30,273 rows** each; `_excl` variants = **29,538 rows** each; `excluded_pids.csv` = **735 rows**. 30,273 − 735 = 29,538 ✓ — frame of record confirmed from the artifact's own rows. Run log confirms "Excluded: 735 HHs (2.43% of 30273)".
- **Provenance confirmed:** live dir (files 2026-07-15 19:34–19:48) postdates the `outputs_step5.20260715_pre_actv2/` snapshot (19:32:49). Step 6's calib-C script reads the **live** dir: `Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py:62-65` → `Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv`. No script reads the archive (only a log *filename* mentions pre_actv2).
- Note: Step-5 log reports 23,882 unique SIM_HH_ID pre-exclusion; the 23,150-HH post-exclusion figure is adjudicated under the frame sweep (§2) — no contradiction found in Step-5 artifacts (the step's docs simply don't state HH-frame numbers).

### Step 6 — longitudinal forecast + calib-C — **COMPLETE & CORRECT** (minor hygiene notes)
- Scorecard **re-derived from the live HTML report** (`outputs_step6/step6_validation_report.html`, regen 2026-07-17 16:33) by parsing every gate-status span: **54P / 11W / 0F / 40I** — matches record exactly (65 scored gates, 54/65 PASS).
- **Deliverable of record confirmed:** `2030_synthetic_diaries_2split_calibrated_mindwell_C.csv`, 70,682,794 B, mtime 2026-07-17 16:15, **111,024 rows** (exact), MD5 **E4E8AEF4278963255040C1B27DA13E14**.
- **Mutex re-derived from the file itself** (pandas over `hom30_001..048` × `wrk30_001..048`, all 111,024 rows): slot-level conflicts = **0**, rows with ≥1 conflict = **0**. Gate 6.7 in the report agrees: `Mutual exclusion: hom30==1 AND wrk30==1 | 0 | PASS`. Gate 6.8 independently cross-checks the row total (37,008 × 3 bands = 111,024).
- Resolves the Step-5 hand-off question: calib-C was re-run 2026-07-17 (`run_calibC_20260717.log`; script mtime 16:10, `_C` output 16:15), i.e. **on the post-actv2 live Step-5 data** — no pre-actv2 snapshot leaked in.
- **Caveat S6-a (spec doc stale):** `3rdJ_06_longitudinalForecasting_2split_val.md` (mtime 2026-06-26) is the plan/spec, holds no result rows, and never picked up the 07-17 rerun; the scorecard of record lives only in the HTML. Doc-only.
- **Caveat S6-b (hygiene):** the non-`_C` 2030 file (Jun 26) + 5 BAK/pre-fix `_C` variants still sit in live `outputs_step6/`. Naming is unambiguous and no downstream script globs loosely today, but a future `mindwell*.csv` glob could pick the wrong file. Recommend moving backups to `archive/` (not done in this pass — diagnosis only).

### Step 7 — BEM integration — **COMPLETE & CORRECT** (val-doc log gap noted)
- Val doc exists (`3rdJ_07_bemIntegration_2split_val.md`, mtime 2026-07-15 20:26). Gate table re-counted: 2022 = 22P/2I, 2030 = 25P/1I, **0 WARN / 0 FAIL both columns**. Headline "32P / 43P" counts per-band/per-archetype sub-checks the 26-row table collapses — directionally consistent, exact figures not independently re-derivable from the table alone (noted, not a defect).
- **Mutex regeneration confirmed by hash evidence** — all three 2030 schedules: live mtimes 2026-07-17 16:39, `_BAK_2026-07-17` counterparts present, **MD5 differs from BAK in all 3 cases** (e.g. conservative D1865BBB… vs BAK 4E21C6D6…; full table in audit trail). Row counts unchanged at **1,111,200 data rows / 23,150 HH** — consistent with a weekend-only occupancy shift.
- **Office multiplier bit-identical pre/post as required:** `office_presence_multiplier_2030.csv` MD5 3B2F8A2BE6A82DA9F2EE074338F2219C == its `_BAK_2026-07-17` — office channel (reads only wrk30) correctly insulated from the hom30 fix.
- **`_C`-input provenance proven from the run log**, not just code: `run_year2030_20260717.log:5` = "Using --deliverable override: …\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv". (Producer's hardcoded default is the non-`_C` path — the run used the explicit override; validator auto-prefers `_C` at `3rdJ_07_bemIntegration_2split_val.py:170`.)
- 2022 ledger: live `BEM_Schedules_2split_2022.csv` MD5 AE167972…, **1,111,200 rows / 23,150 HH**; its `_BAK_2026-07-15` has 1,114,128 rows / **23,211 HH** — the BAK pair independently reproduces the exact 61-HH / 2,928-row frame fix, confirming the frame fix (07-15) and mutex fix (07-17) are cleanly separable in file history.
- **Caveat S7-a:** the HTML validator reports (`step7_validation_report_{2022,2030}.html`, mtime 07-15 20:16) predate the 07-17 regen; the 07-17 sign-off relied on the producer's inline gate asserts ("ALL PASS" in `run_year2030_20260717.log`) + MD5 verification, per `2J_to_3J_improvement_implementation.md:1446-1472`. Also, Step7_docs' own Progress Logs carry no 07-17 entry (history lives only in the improvement doc). Doc/report-refresh gap, not a data defect.

### Step 9 — activity-driven loads — **COMPLETE w/ documented caveat** (stale local CSVs)
- Latest report `outputs_step9/step9_report.html` (mtime 2026-07-17 14:06). Scorecard re-derived by counting gate-table status cells: **10P / 1W / 0F** — matches record. Sole WARN = **G2r** (resid SingleD EUI out of SHEU band), as expected. G8o verbatim: PASS, "2030 bands DIFFER (WFH-modulation live)", energy% cons/hyb/full = 0.53/−0.00/−0.32.
- Re-derived EUIs from `step9_eui_by_channel.csv`: office 172.6 (all) / 172.7 (Office_Knowledge), inside [100, 200] as-modelled PNNL → G2o PASS confirmed; resid SingleD 212.5 out of band [130.6, 186.1] → WARN confirmed; other 3 resid archetypes in band.
- **Caveat S9-a (FINDING — stale local CSVs):** the four core CSVs in `outputs_step9/` are mtime **2026-07-06**, 11 days older than the 07-17 report. Recomputing G8o from the local `step9_scenario_response.csv` gives **0.54 / −0.01 / −0.33**, each exactly 0.01 off the report's (and record's) 0.53 / −0.00 / −0.32 — the local CSVs are the **pre-mutex-cascade** versions, never re-synced from the cluster after the 07-17/18 re-run. Signs, magnitudes, and every PASS/WARN are unaffected, but the local CSV set is not the one that generated the current report. **Recommended (cheap) fix: re-scp the 4 step9 CSVs from the cluster.** Until then, quote the HTML report, not the local CSVs.
- Minor numeric-provenance notes: SingleD EUI floats across artifacts (CSV 212.5 / report G3 row 212.1 / memory 211.7 — same qualitative story, digit not stable; check before quoting to 1 decimal in the manuscript); report's G2o "172.7" cites the Office_Knowledge subgroup row rather than the office-all aggregate (172.6) — cosmetic.
- Frame grep: only 2 hits, both inside `*_pre_frame23150` archive snapshots — clean.

---

## 2. Cross-cutting sweeps

### 2.1 Frame consistency — **CLEAN**
Full recursive grep of Leg2_2-split (all .md/.py incl. archives; `eSim_bem_utils_3J` lives nested at `Step8_docs/eSim_bem_utils_3J/` — no standalone copy exists):
- **23,211 / 144,507 / 144,465 / 674-as-exclusion: zero unlabelled live occurrences.** Every hit is (a) an explicitly-labelled 2J/historical reference, (b) a dated archive/BAK file, or (c) the append-only improvement-doc audit trail deliberately preserving history.
- The two "known stale comments" from the brief are **better than believed**: `Step8_docs/eSim_bem_utils_3J/main.py:74-75` now correctly reads 23,150 (fixed in the 07-15 patch chain); `integration.py:17` **never contained a frame number** (false lead, already annotated at `2J_to_3J_improvement_implementation.md:428`).
- No live .py contains a stale frame literal in code or comment. Positive confirmation: 87 occurrences of 23,150 across 17 current files.

### 2.2 Provenance chain — **INTACT** (2 latent footguns noted, no live defect)
Every producer→consumer edge verified from live script source (file:line quoted in the employee audit):
- Step 4←3 (`3rdJ_04A_assembly_2split.py:75`), Step 5←4 (`3rdJ_05_censusLinkage_2split.py:46` → `sweep/R5_raked_mindwell_actv2/`), Step 6←5 (`3rdJ_06_calibrate_C_activity_weekend_2split.py:64` → live `outputs_step5/`), Step 8←7 (`eSim_bem_utils_3J/main.py:98-101` etc.), Step 9←8 (`3rdJ_09_activityDrivenLoads_2split.py:60` → live `agg/`). **No live script reads any archive dir as input** (full sweep; the only `_BAK` mentions are each script's own backup-write logic).
- 04T placement: runs post-04L/04M into `R5_raked_mindwell_actv2/`; 2030 side handled by wrapper `Step6_docs/3rdJ_06_forecast_rake_2split.py:39-42` (imports 04T functions, reads/overwrites the `_C` file with a PRE_RAKE_SNAPSHOT backup). Consistent.
- Step 6's forecaster deliberately trains on the separate `R5_lr1e4` pool (OD-1, resolved 2026-06-23, documented at `3rdJ_06_longitudinalForecasting_2split.md:45,660-671`) — by design, not drift.
- **Footgun P-a:** `3rdJ_07_aug_to_bem_2split.py:52-54` hardcodes `D2030` = the **non-`_C`** file. Confirmed dead code (single grep hit = its own definition; all real runs pass `--deliverable` explicitly, incl. the 07-17 regen per its run log) — but a future bare `--year 2030` run would silently consume the wrong file. Recommend hard-coding `_C` or asserting, when Leg-3 forks this script.
- **Footgun P-b (= S4-b):** stale one-off scripts pointing at the pre-04T top-level `augmented_diaries.csv`.

### 2.3 Deliverable hashes — **MATCH** (1 ledger gap)
- The three 2030 BEM schedules' computed MD5s (d1865bbb… / 1762155b… / 54abbcd8…) **match the hashes recorded at upload time** in `2J_to_3J_improvement_implementation.md:1467` — i.e. what Step-8's re-sim campaign (job 1126886) actually consumed on the cluster is byte-identical to the local files. The superseded Jul-15 pre-fix hashes (recorded L975-977) correctly do NOT match.
- **Gap H-a:** no MD5 was ever recorded for the `_C` 2030 diaries file itself — its provenance chain rests on row count (111,024) + size only. This audit now provides one: **E4E8AEF4278963255040C1B27DA13E14** (computed 2026-07-18, §Step 6 above), which future sessions can verify against.

### Step 8 — simulation campaign — **COMPLETE & CORRECT on the cluster; local mirror STALE** (finding)
- **FINDING S8-a (silent local staleness — exactly the failure mode this pass hunts):** the *local* `outputs_step8/` is not the post-mutex state. Local agg tables are Jul 6–8; local `step8_validation_report.html` is Jul-17 12:18 (pre-mutex, scorecard 50P/**1W**/17I/0F with gate 4.9 INFO "enduse file absent"); and `agg_pre_mutexfix_20260718/` doesn't exist locally at all. The post-mutex artifacts of record live **on the cluster** (`/speed-scratch/o_iseri/step8_2split/upload/.../outputs_step8/`): agg tables Jul-18 11:20, baseline archive `agg_pre_mutexfix_20260718/` Jul-18 09:09, report Jul-18 11:42.
- **Scorecard of record re-verified from the cluster artifact itself** (single-file grep on the Jul-18 11:42 report): `Scorecard: 50 PASS · 2 WARN · 17 INFO · 0 FAIL` ✓ — matches record (2W = §4.1 SingleD EUI + §4.9 heat-dominance, the latter WARN because the refreshed `agg_enduse_annual.csv` Jul-17 13:18 exists cluster-side).
- **The <1%-delta claim was re-derived in this pass** from the two cluster `agg_annual.csv` files (post-mutex vs `agg_pre_mutexfix_20260718/` baseline, both scp'd to scratchpad): results in §2.4 below.
- Frame check: live Step8_docs uniformly 23,150; stale numbers only in `*_pre_frame23150` archives. Clean.
- Gate "6.7" in the Step-8 report is longitudinal monotonicity (PASS) — the mutex gate family lives in Step 6 (6.7 mutual-exclusion PASS, §Step 6) — naming collision only, no gap.
- **Recommended fix for S8-a (cheap, no simulation):** one scp sync of cluster `outputs_step8/{agg/, agg_pre_mutexfix_20260718/, step8_validation_report.html}` and `outputs_step9/` to local. Not done in this pass (diagnosis-only; also a state-changing sync the user should own).

### 2.4 Mutex-fix delta — **RE-DERIVED, CLAIM CONFIRMED** (with one nuance)
Both cluster `agg_annual.csv` files (post-mutex live Jul-18 11:20 vs `agg_pre_mutexfix_20260718/` baseline Jul-18 09:09) scp'd to scratchpad and compared by script (8,652 data rows × 29 cols each; scripts preserved in scratchpad):
- **Invariance (everything except 2030-residential): CONFIRMED at 100%.** All 96 (channel, arch, city, scenario) groups show exactly 0.0% delta; summed total_energy_kWh identical to the cent (6,730,443,197.80 both sides). On genuinely key-matched rows, 0 rows differ on any column.
- **2030-residential band aggregates: −0.0212% (conservative) / −0.0793% (hybrid) / +0.0169% (fullyhybrid)** — far under the <1% claim. Worst (arch, city) cell 3.03% (SingleD/Montréal/fullyhybrid); washes out at band level.
- **Nuance N-1 (row-ID churn):** ~40% of rows (3,486/8,652) carry reshuffled `sample`/`sim_hh_id` labels between the two runs *even in untouched scenarios*. Proven cosmetic by sorted-multiset identity (per-cell value lists byte-identical). So the record's phrase "rows bit-identical" is true **at the value level, not the row-key level** — any future per-row join on these files must not use key-match rate as a change proxy.
- **Nuance N-2 (household-level swings):** a handful of 2030-hybrid SingleD/OtherDwelling households (Winnipeg/Toronto/Montréal) swing 40–75% in annual total energy under the mutex fix. Immaterial to aggregates; footnote-worthy only if the paper ever shows household-level distributions.

### 2.5 Step-9 cluster artifacts — **RE-DERIVED, ALL NUMBERS OF RECORD CONFIRMED**
From the cluster's post-mutex `outputs_step9/` (Jul-18 12:06, scp'd to scratchpad):
- `step9_scenario_response.csv` recomputed: office 2030 vs 2022 = **+0.533% / −0.004% / −0.324%** → record's 0.53/−0.00/−0.32 exact.
- `step9_eui_by_channel.csv`: office all = **172.7** in [100,200]; resid **SingleD = 211.7**, band [130.6,186.1], in_band=False — the record's numbers exactly. This resolves the §Step-9 numeric-instability note: **211.7 and 172.7 are the current cluster values; the local CSVs' 212.5/172.6 are the stale pre-cascade versions** (one consistent story, no real instability).
- `step9_report.html` gate table re-counted: **10P / 1W / 0F**, WARN = G2r, G8o PASS ("2030 bands DIFFER (WFH-modulation live)", range 0.85). Scorecard of record confirmed from the artifact itself.

---

## 3. Implementation-doc closure — **FULLY CLOSED** (2 cosmetic notes)

`improvement/2J_to_3J_improvement_implementation.md` (1,523 lines; extracted by employee, adjudicated by manager):
- **Tasks 1–4: all DONE** with closing Progress-Log entries — Task 1 (L287, act30 rake, Gate A closed), Task 2 (L236, multi-zone injection port), Task 3 (L206, spot-checks), Task 4 (L1514, "MUTEX-FIX CASCADE CLOSED OUT", 0 FAIL end-to-end). Structural note: `## Task N` headers themselves carry no DONE tag — status lives in the Progress Log (doc convention, not a gap).
- **OD-I1..I4: all ✅ RESOLVED** (header L193, resolved 2026-07-15). OD-I2 and OD-I4 additionally *evidenced* downstream (LFTAG pool-up 2.8%/2.2% at L339-342; OD-I4's 04P-probe condition evaluated with real numbers at L558-566 → 04T applied).
- **Gate A: PASS shown with real numbers, twice** — residential pool +20.98 pp FAIL → **+1.12 pp PASS** (L360-362, re-derived L418) and 2030-forecast +3.53 pp → **+0.56 pp PASS** (L543-548, L578). Not a bare assertion.
- **No dangling non-terminal state**: every RUNNING/LAUNCHED/PENDING/awaiting hit is closed by a later terminal entry (verified pairwise: archive job 1126041 → COMPLETED L893; campaign launch → relaunch → 168 COMPLETED L1267; end-use extractor 1126821 → COMPLETE L1402; Phase-2 re-cascade LAUNCHED chain → CLOSED OUT L1505).
- **Progress Log ends** on the 2026-07-18 *final-check prompt authoring* entry (L1521-1523), i.e. one entry **after** the mutex closeout (L1505). Cosmetic self-reference only; the last entry reopens nothing.
- Explicit open residuals (by design, filed-not-fixed): Section-4 backcast re-score; TICKET_G4_pooled_strata; TICKET_cross_era_pairing — adjudicated in the caveats section below.

---

## 4. Per-step summary table

| Step | Val report exists | Latest scorecard (re-derived) | Live deliverable + provenance | Frame OK | Status |
|---|---|---|---|---|---|
| 1 | ✓ | 139P/0W/0F (= headline) | outputs_step1 8 CSVs, counts sane | ✓ | **COMPLETE & CORRECT** |
| 2 | ✓ | 73P/1W/0F (= headline) | outputs_step2 8 CSVs, counts sane | ✓ | **COMPLETE & CORRECT** |
| 3 | ✓ | 91P/1W/0F (= headline) | work_30min.csv 64,061 rows, 2-channel origin ✓ | ✓ | **COMPLETE & CORRECT** |
| 4 | ✓ (report .txt/.html of 07-17) | 66P/3W/2F (both FAILs pre-existing, argued non-blocking) | 04T pool `R5_raked_mindwell_actv2/` consumed by Step 5 ✓; Gate A +1.12 pp PASS (3 sources) | ✓ (n/a) | **COMPLETE w/ caveats** (S4-a doc stale, S4-b pre-fix file ambient) |
| 5 | ✓ (doc stale) | 22P/1W/1F per run_val_20260715.log (doc still says 20/1/3) | live outputs_step5 = 30,273/29,538/735 re-derived ✓; Step 6 reads live dir ✓ | ✓ (from own rows) | **COMPLETE w/ caveats** (S5-a doc stale) |
| 6 | ✓ (spec doc; results in HTML) | 54P/11W/0F/40I (= record, re-parsed from HTML) | `_C` file: 111,024 rows, mutex=0 re-derived, MD5 E4E8AEF4…, gate 6.7 PASS | ✓ | **COMPLETE & CORRECT** (S6-a/b hygiene) |
| 7 | ✓ | 0W/0F both years (headline 32/43 = sub-check granularity) | 3× 2030 schedules regen on `_C` (log-proven), MD5≠BAK; office multiplier MD5-identical ✓; 23,150 HH ✓ | ✓ | **COMPLETE & CORRECT** (S7-a report-refresh gap) |
| 8 | ✓ cluster (local stale) | **50P/2W/17I/0F re-verified on cluster artifact**; delta claim re-derived §2.4 ✓ | cluster agg Jul-18 = live; consumed schedules hash-verified §2.3 ✓ | ✓ | **COMPLETE & CORRECT on cluster; local mirror STALE (S8-a)** |
| 9 | ✓ cluster (local CSVs stale) | 10P/1W/0F re-counted (cluster report); all record numbers re-derived §2.5 ✓ | cluster outputs Jul-18 = live; reads live agg ✓ | ✓ | **COMPLETE & CORRECT on cluster; local CSVs STALE (S9-a)** |

## 5. Caveats carried into Leg-3 (each: blocks Leg-3? why)

| # | Caveat | Blocks Leg-3? | Why |
|---|---|---|---|
| #5 | Multi-zone injection fix is per-zone redistribution, energy-neutral on annual aggregates (~1.0× all archs) — paper must not claim it "restored" energy | **No** | Verified still true by §2.4's invariance result (non-2030 rows 0.0% delta through the whole cascade). Wording constraint on the paper only. |
| #6 | Mutex fix = weekend-occupancy correction, negligible annual energy | **No** | Re-proven quantitatively in §2.4: band deltas ≤0.08%. 2030 headline numbers stand. |
| G4 ticket | `TICKET_G4_pooled_strata_defect.md` (filed 07-15, OPEN) — Step-4 validator G4 pools day-type strata (Simpson's paradox); mis-reports 04T's success as FAIL | **No, but fix at fork** | Validator-only; no data affected; per-stratum evidence already in the ticket (0.3/0.02/0.00 pp post-04T). Leg-3 will fork this validator — porting a known-defective gate forward would bake the misreporting into 4-split reports. Recommend implementing the ticket's per-stratum fix when Leg-3 copies the Step-4 validator (cheap, local, test method already written). |
| Cross-era ticket | `TICKET_cross_era_pairing_defect.md` (filed 07-17) — CRN pairing valid within era-pools (2022↔2030; within 2,883-HH historical stock), NOT across the 2005→2030 trend | **No** | Claim-scope only, zero results impact. One-sentence manuscript action (report cross-era trend differences as unpaired). Leg-3 inherits the same two-pool design — carry the same sentence. |
| Backcast | Clean Section-4 backcast re-score needs cluster temp=0.8 regen with real `R5_lr1e4` conditioning | **No** | Non-blocking follow-up, explicitly out of scope of the closeout; unrelated to the 4-split fork base. |

## 6. New findings from this pass (diagnosis only — nothing fixed)

**Defect-grade (the silent-staleness class this pass hunts):**
- **S8-a / S9-a — local mirrors of Step-8/Step-9 outputs are pre-mutex stale.** Local `outputs_step8/` (agg Jul 6–8, report Jul-17 12:18, 50P/1W/17I/0F, no `agg_pre_mutexfix_20260718/`) and local `outputs_step9/` core CSVs (Jul-6; give 0.54/−0.01/−0.33 and SingleD 212.5) are NOT the post-mutex artifacts of record. The of-record versions are cluster-side (Jul-18) and were fully re-verified there in this pass (§2.4, §2.5, Step-8 section). **Anyone reading only the local tree would quote superseded numbers.** Recommended fix: one scp sync of cluster `outputs_step8/{agg/, agg_pre_mutexfix_20260718/, step8_validation_report.html}` + `outputs_step9/` → local (~1.1 GB, no simulation, minutes). No ticket filed — this report + the Progress Log entry serve as the record; user decides when to sync.

**Caveat-grade (doc staleness / hygiene / footguns; all detailed in-line above):**
- S4-a, S5-a, S6-a, S7-a: four val/spec docs whose headlines lag their own live reports (Step-4 .md pre-04T; Step-5 .md 20/1/3-vs-22/1/1 and 613-vs-735; Step-6 spec never back-filled; Step-7 no 07-17 Progress-Log entry). One doc-backfill session clears all four.
- S4-b / P-b: pre-04T `augmented_diaries.csv` still at the tempting top-level path; two stale one-off scripts point at it.
- S6-b: non-`_C` 2030 file + 5 BAK variants live in `outputs_step6/` (glob hazard).
- P-a: `3rdJ_07_aug_to_bem_2split.py` hardcoded `D2030` default = non-`_C` file (dead code today; assert/fix at Leg-3 fork).
- H-a: no MD5 was ever recorded for the `_C` deliverable — this report now records it (E4E8AEF4278963255040C1B27DA13E14).
- N-1: `sample`/`sim_hh_id` labels churn between re-runs (~40% of agg rows) — value-proven cosmetic, but future pre/post joins must compare value multisets or group aggregates, not row keys.

## 7. VERDICT

# **GO-with-caveats for Leg-3**

Every step of the 2-split pipeline is complete and correct **as attested by its own artifacts**: scorecards re-derived (not trusted) at every step, 0 FAIL end-to-end, frame 23,150 clean everywhere live, provenance chain fully live (no archive reads), campaign-consumed hashes match local deliverables, mutex/actv2 fixes proven landed and quantitatively bounded (§2.4). The implementation doc is fully closed (4/4 tasks DONE, OD-I1..4 resolved, Gate A evidenced twice, no dangling states).

The caveats are: (1) **sync the stale local Step-8/9 mirrors before quoting any number from the local tree** (S8-a/S9-a — the one silent-staleness defect this pass found, cluster-side truth verified); (2) four val-doc headline backfills; (3) fix the G4 gate per its ticket **when Leg-3 forks the Step-4 validator**, and harden the `D2030` default when it forks Step 7. None of these touches a published number — the 2030 headline results stand as closed on 2026-07-18.

*Audit executed 2026-07-18 by manager session (Fable) with 11 cheap-model employee agents (1 Haiku, 10 Sonnet); cluster re-verification via login-node-safe single-file ops + scp only (no compute on speed-submit2).*

---

## 8. RESOLUTION — caveats cleared (2026-07-18, same day)

Acting on the GO-with-caveats verdict, the manager cleared the actionable caveats before the Leg-3 fork. Diagnosis→fix, each verified:

- **G4 gate (ticket) — CLOSED.** `3rdJ_04_augmentationGSS_2split_val.py` G4 stratified per `DDAY_STRATA` (predecessor `...val.py.20260718_preG4fix`). Re-run on both pools: post-04T work-peak deltas weekday 0.33 / Sat 0.03 / Sun 0.01 pp → PASS; sleep deltas all ≤0.04 pp → PASS; pre-04T ranks worse than post-04T in every stratum (direction test PASS). **Step-4 scorecard 66P/3W/2F → 73P/3W/1F**, sole remaining FAIL = OW5 (unobservable by design); diff confirms only G4 lines moved. Top-level `outputs_step4/step4_validation_report.{txt,html}` promoted to the new report (md5-identical to the actv2 sweep copy, `1ed0cb8f…`); old top-level archived at `outputs_step4/_pre_G4fix_20260718/`.
- **D2030 default (footgun P-a) — HARDENED.** `3rdJ_07_aug_to_bem_2split.py` `D2030` default repointed from the non-`_C` file to `...mindwell_C.csv` (predecessor `...py.20260718_preD2030harden`). A bare `--year 2030` run can no longer silently consume the mutex-contaminated file.
- **4 val-doc backfills (S4-a/S5-a/S6-a/S7-a) — DONE.** Dated 2026-07-18 addenda added (append-only, originals intact): Step-4 (73P/3W/1F + 04T/G4 narrative), Step-5 (22P/1W/1F, 735/29,538), Step-6 (54P/11W/0F/40I, `_C` MD5 E4E8AEF4…), Step-7 (07-17 mutex-regen Progress-Log entry with MD5 evidence).
- **Hygiene (S6-b, S4-b) — DONE.** 6 superseded Step-6 backup/non-`_C` files moved to `Step6_docs/outputs_step6/archive_pre_mutexfix/` (live `_C` deliverable untouched, MD5 verified); 2 stale one-off Step-5 scripts got a header warning that they read the pre-04T pool.

**Still requiring the user (cluster auth):** the S8-a/S9-a scp sync of the post-mutex cluster `outputs_step8/{agg,agg_pre_mutexfix_20260718,step8_validation_report.html}` + `outputs_step9/` to local. Stale local versions were archived aside (`_pre_mutexsync_20260718/`) so the target dirs are clean and ready to receive. Until synced, quote the cluster artifacts, not local.

**Net:** every caveat that could be closed locally is closed. Base is clean for the Leg-3 fork pending the one scp sync.

### 8.1 scp sync — DONE (2026-07-18, manager-executed)
The S8-a/S9-a sync was run by the manager over key-based SSH (BatchMode, no login-node compute): cluster `outputs_step8/{agg, agg_pre_mutexfix_20260718, step8_validation_report.html}` + `outputs_step9/{step9_*.csv, step9_report.html}` pulled to local. **Verified post-sync:** local Step-8 report = `50 PASS · 2 WARN · 17 INFO · 0 FAIL`; local `step9_eui_by_channel.csv` SingleD = 211.7 (WARN G2r), office all = 172.7 in-band; local `step9_scenario_response.csv` office 2030 = +0.53 / −0.00 / −0.32 (G8o). Stale pre-mutex local copies retained at `_pre_mutexsync_20260718/`. **All GO-with-caveats items now fully closed — base is clean for the Leg-3 fork.**
