# Step 8 Validation Report — Improvement Doc (3J Leg-2, two-channel)

Compares `step8_validation_report.html` in **2J** (`2J_docs_occ_nTemp/outputs_step8/`) against the **3J Leg-2 two-channel** report in this folder, to identify figures/analyses that existed in 2J and did not carry over (or carried over thinner) into 3J, and to recommend what to add. Built by decoding both HTML reports' embedded charts and gate tables (2026-07-07).

## 0. Which report is the live/updated one — resolved

There were two `step8_validation_report.html` copies:

| File | Last written | Scorecard | Chart sections rendered |
|---|---|---|---|
| `Step8_docs/outputs_step8/step8_validation_report.html` (**this folder**) | 2026-07-02 21:13 | 46 PASS · 1 WARN · 13 INFO · 0 FAIL | all 9 (§0–§8) |
| `Step8_docs/step8_validation_report.html` | 2026-07-01 20:14 | 27 PASS · 0 WARN · 13 INFO · 0 FAIL | missing §4 and §5 charts |

The validator script itself (`Step8_docs/3rdJ_08_simulation_2split_val.py`, lines 43-46) hardcodes:
```python
OUT_DIR = HERE / "outputs_step8"
HTML_OUT = OUT_DIR / "step8_validation_report.html"
```
So **`outputs_step8/step8_validation_report.html` is the only path the pipeline still writes to.** The copy directly under `Step8_docs/` was a stray artifact from the 2026-07-01 run (pre the office-WFH-bug fix and pre the §7.2 gate reword — both landed 2026-07-02), left behind when the output path moved into the `outputs_step8/` subfolder.

**Action taken:** moved the stale copy to `Step8_docs/archive/step8_validation_report.20260701_preOutputsStep8Dir.html`, following this repo's existing predecessor-archiving convention (same pattern as `3rdJ_08_simulation_2split_val.20260701.py` etc. already in that folder). This is an **uncommitted working-tree change** — `git status` shows it as a delete + untracked add; review and commit/stage it yourself when ready. Nothing else in the folder references the old path, so no other file needed updating.

Going forward: only edit/regenerate `outputs_step8/step8_validation_report.html`. Don't let `run_validation.sh` or ad-hoc local runs write anywhere else.

## 1. Section map: 2J → 3J

2J was single-channel (residential only); 3J Leg-2 is two-channel (residential + office) and restructured the sections. Numbering doesn't line up 1:1:

| 2J section | 3J section | Status |
|---|---|---|
| *(none)* | §0 Historical Schedule Generation | 3J-only addition (reconstructed 2005/2010/2015 schedules) |
| §1 Run Integrity | §1 Run Integrity | Carried over, improved (per-channel split) |
| §2 Schedule Injection Fidelity | §2 Schedule Injection Fidelity | **Present but weaker — see §2.1 below** |
| §3 Monte-Carlo Convergence | §3 Monte-Carlo Convergence | Carried over, improved (CI histogram + normalized traces) |
| §4 Physical Plausibility (SHEU) | §4 Physical Plausibility (SHEU/NECB-PNNL) | **Partially carried over — see §2.2** |
| §5 Load-Shape / Time-Series Sanity | §5 Load-Shape / Time-Series Sanity | **Partially carried over — see §2.3** |
| §6 2022→2030 Shift Effect (headline, 4 charts) | §6 Longitudinal·COVID-break·WFH-band (1 chart) | **Largest regression — see §2.4** |
| §7 Longitudinal Trajectory 2005→2030 (4-panel) | §7 Scenario Plausibility (different, narrower analysis) | **No equivalent exists — see §2.5** |
| §8 Summary | §8 Summary | Carried over |

## 2. Gaps and recommendations, most important first

### 2.1 [P0] §6/§7 — the 2005→2030 multi-metric longitudinal trajectory figure has no 3J equivalent

2J's `§7 Longitudinal Trajectory` was a 4-panel figure — EUI, Load Factor, Midday Share, Peak-to-Avg, all four **per archetype**, 2005→2030, with a COVID marker at 2022 (`_plot_longitudinal`, `2J_docs_occ_nTemp/08_simulation_val.py:1018`). It's the "headline story arc" figure for a paper about how occupancy/energy evolves over two decades.

3J's only historical-arc chart is §0's single line (WD AT_HOME occupancy, residential-only, 2005→2022, stops before the 2030 scenario fork). There is no multi-metric, per-archetype, two-channel, full 2005→2030 trajectory figure anywhere in the 3J report.

**Recommend:** add a longitudinal trajectory figure that extends `_plot_longitudinal`'s pattern to:
- both channels (resid archetypes + office archetypes/env),
- the 2030 scenario fork (3 lines/markers past 2022 — conservative/hybrid/fullyhybrid — instead of 2J's single 2030 point),
- the same COVID-break marker at 2022.

Metrics: EUI, load factor / coincidence factor, midday share, peak hour or peak-to-avg. Source data is already aggregated for §4/§5/§6/§7 ("Reads §8D agg" per the gate messages), so this is a plotting addition on top of existing aggregate tables, not a new data pipeline.

### 2.2 [P0] §6 headline shift-effect lost 3 of its 4 panels

2J's `§6 2022→2030 Shift Effect` had 4 figures (`08_simulation_val.py:878-975`):
1. `_plot_paired_delta` — 3-panel histogram of paired per-HH Δ (EUI, midday share, load factor), 2030−2022.
2. `_plot_2022_2030_diurnal` — 2022 vs 2030 diurnal envelope overlay.
3. `_plot_peak_hour_stability` — peak-hour by archetype, 2005→2030, errorbars.
4. `_plot_delta_by_cz` — 2022→2030 mean Δ (EUI, midday, load factor) broken out **by climate zone**.

3J's §6 has one chart (WFH-band ordering bars: resid WD occupancy + office WD peak AT_WORK, monotonic-ordering check only). The gate table shows the underlying paired-Δ numbers exist for residential midday (gate 6.1: "+4.223 ± 1.178 kW excludes 0, n=1200 HH") and peak-hour shift (gate 6.6, text-only) — they're just never visualized as a distribution, and never broken out by CZ.

**Recommend**, adapted to two channels and the 3-scenario 2030 fork:
- Paired-Δ histograms (resid: EUI/midday/peak-hour; office: energy/AT_WORK) — one panel set per 2030 scenario, or overlaid.
- Δ-by-climate-zone bars for both channels — currently **zero** CZ-disaggregated view of the 2030 effect exists; given the pipeline already stratifies everything else by CZ, this is a natural, low-effort addition from the same aggregate tables.
- Peak-hour-by-archetype-over-time chart (folds into the §2.1 longitudinal figure — no need to duplicate if that's built).

### 2.3 [P1] §4 — end-use split (heating/cooling/other) has no 3J equivalent

2J had a second §4 figure: `Heating / Cooling / Other Split by CZ` (stacked bar), backing two numeric gates — "heating share rises cold→warm" and "non-zero cooling present." 3J's §4 has neither the figure nor an equivalent gate for either channel — only the EUI-vs-benchmark-band bars survived.

**Recommend:** add the stacked end-use bar (heating/cooling/other-as-lights+equip) by CZ, for both residential and office, plus the two gates it backs (share ordering across CZ; nonzero cooling floor). This is a standard BEM plausibility check (verifies the model isn't e.g. all-heating in a warm CZ) and is currently silent in 3J.

### 2.4 [P1] §5 — no seasonal decomposition of the diurnal load shape

2J's §5 diurnal chart split by **season** (cooling / heating / shoulder / all). 3J's §5 diurnal chart splits by **weekday vs weekend** only (a different, valid dimension, but not a substitute). With two channels now, a seasonal split is arguably more informative than before (e.g., does office AC load peak differently in cooling vs heating season, does resid heating dominate the winter evening peak).

**Recommend:** add the season-conditioned diurnal overlay for both channels, on top of (not instead of) the existing WD/WE panels.

### 2.5 [P2] §2 — the injection-fidelity check is weaker than 2J's, and self-flags it

3J gate 2.6 says: *"Lights formula max(0.15, O) verified on 2022 CSV... **Full ±0.5% round-trip requires E+ SQL comparison.**"* Gate 2.1 similarly labels itself *"source gate, not E+ round-trip."* So the report itself documents that the actual injected-schedule-vs-source round-trip (what 2J's §2 did) is not currently being checked.

**Important:** the note that this "requires E+ SQL comparison" isn't quite right — 2J never ran EnergyPlus to get this check. It parsed the **input IDF text directly** with a small regex-based `Schedule:Compact` reader and diffed it against the source CSV, before/without simulation:
- `2J_docs_occ_nTemp/Step8_docs/roundtrip_analysis.py` — `parse_compact_schedule()` (line 30), `parse_people_count()` (line 74), `collect_samples()` (line 111).
- `2J_docs_occ_nTemp/08_simulation_val.py` — Section 2 driver (lines 265-470), figure at line ~468 (`Schedule Injection Round-trip: HH <id> (<arch>)`, weekday+weekend panels, per sampled HH).

3J's office IDFs already carry the same kind of injected `Schedule:Compact` objects (`office_integration.py:255-278`, `ppl_name`/`lgt_name`/`eq_name`). So this method ports directly to both channels: sample a few IDFs per channel, regex out the injected schedule text, diff against the source CSV (`BEM_Schedules_<year>.csv` for resid, `office_presence_multiplier_<year>.csv` for office), and produce the same weekday/weekend round-trip plot plus the daily-mean-%/hour-alignment/metabolic-rate gates 2J had.

**Recommend:** port `roundtrip_analysis.py` + the Section-2 driver into `3rdJ_08_simulation_2split_val.py`, one code path per channel. This resolves the self-flagged gap without needing an E+ SQL pass at all.

### 2.6 [P2] §3 — office channel is silently absent from Monte-Carlo convergence

All of §3's gates (3.1-3.2, 3.3, 3.4) are `Resid`-only. This is actually **correct** — the office campaign (3 arch × 2 env × 6 CZ × 7 scenarios = 252 runs) is full-factorial, not N=50 Monte-Carlo sampled, so a convergence check doesn't apply to it. But the report doesn't say that anywhere, so a reader has no way to distinguish "not applicable" from "forgotten."

**Recommend:** add a one-line INFO gate under §3, e.g. *"Office campaign is full-factorial (252/252 cells, no resampling) — MC convergence N/A."* Cheap, no new chart needed.

### 2.7 [P2] §0 — office channel has no historical chart, despite having its own gates

§0's gate table checks residential AND office schema/row-count/NaN for 2005/2010/2015, and gate 0.5 flags a real methodological discontinuity (office AT_WORK gating variable changes definition across GSS cycles: `PLACE=02` for 2005/2010 vs `LOCATION=301/3301` for 2015/2022) — but §0's only chart is the residential AT_HOME arc. The office-side discontinuity is currently text-only.

**Recommend:** add an office AT_WORK historical arc (2005→2022) alongside the existing resid panel, so the cycle-definition break in gate 0.5 is visible, not just described.

## 3. Priority summary

| # | Gap | Priority | New chart(s) | New gate(s) | Data already available? |
|---|---|---|---|---|---|
| 2.1 | 2005→2030 longitudinal trajectory, both channels | P0 | 1 (multi-panel) | none needed | Yes — §8D agg tables |
| 2.2 | §6 headline shift-effect (paired-Δ hist, Δ-by-CZ) | P0 | 2 | none needed | Yes — §8D agg tables |
| 2.3 | Heating/cooling/other split by CZ, both channels | P1 | 1 | 2 | Yes — same EUI agg source as §4 |
| 2.4 | Seasonal diurnal decomposition, both channels | P1 | 1 | none needed | Check: needs season tag in §8D agg (cooling/heating/shoulder) |
| 2.5 | IDF-text round-trip fidelity check, both channels | P2 | 1 | ~4 (mirrors 2J 2.1/2.2/2.3/2.4) | Needs new sampling step (port `roundtrip_analysis.py`) |
| 2.6 | "Office N/A for MC convergence" note | P2 | 0 | 1 | N/A (text only) |
| 2.7 | Office historical AT_WORK arc in §0 | P2 | 1 | none needed | Check: needs office 2005-2022 series alongside existing resid one |

P0 items reuse data the validator already aggregates for §4-§7 — they're plotting work, not new analysis. P1/P2 items are worth doing but lower-stakes for the paper's headline claims.

## Progress Log

### 2026-07-07 — all 7 items (2.1–2.7) implemented in `3rdJ_08_simulation_2split_val.py`

Script: `3rdJ_08_simulation_2split_val.py` (predecessor archived to
`archive/3rdJ_08_simulation_2split_val.20260707_preImprovements.py` before editing).
Diff: +453/−20 lines. Verified locally against the real `outputs_step8/agg/*.csv`
tables (8,652 annual rows, both channels, all 7 scenarios) — script runs clean,
`py -m py_compile` passes, no `[plot-skip]`/`[section-error]` in the log for any
new function. Report HTML was **not** regenerated/committed from this local test —
the local campaign/office run dirs only have `cell_manifest.csv` synced (raw
per-run outputs live on cluster scratch), so a local run reports "0/8400" /
"0/252" complete and would regress the real scorecard. A local test accidentally
overwrote `outputs_step8/step8_validation_report.html`; it was restored via
`git checkout --` immediately after (confirmed 0-diff against HEAD). **The real
report must be regenerated by re-running this script on the cluster** (via
`run_validation.sh`) where the full campaign/office outputs exist — only then
should the new charts land in the committed HTML.

Per item:
- **2.1 (P0)** `_plot_longitudinal()` — 2×4 grid (resid/office × EUI/load-factor/
  midday-share/peak-hour), 2005→2030 with the 3-band 2030 fork shaded. Added to §6.
- **2.2 (P0)** `_plot_paired_delta()` (5-panel histogram: resid EUI%/midday/peak-hour,
  office energy%/occupancy%) + `_plot_delta_by_cz()` (3-panel bar by CZ). Both reuse
  the existing 6.1-style pivot-by-(cell,sim_hh_id) pairing logic, generalized to 3
  metrics and to the office channel (paired by cell only, no HH sampling there).
- **2.3 (P1)** `_gate_enduse_split()` + `_plot_enduse_split()` — residential
  heating/cooling/other share by CZ from `agg_annual`'s existing
  `heating_ET_kWh`/`cooling_ET_kWh`/`lights_kWh`/`equip_kWh`/`fan_kWh`/`water_ET_kWh`
  columns; gates 4.6 (heating share rises mild→severe CZ) and 4.7 (nonzero cooling
  floor) both PASS on real local data. **Note:** cooling share came out surprisingly
  large (~45%) even in cold CZ (7A) vs. heating (~8%) — these are E+
  `:EnergyTransfer` zone thermal-load meters, not delivered fuel, so it isn't
  necessarily wrong, but worth a sanity look before citing in the paper. Office
  channel gets an INFO gate (4.8) instead of a chart: the office aggregator only
  sums Lights+Equipment electricity today, so heating/cooling isn't available
  without a regex addition + a re-run of the office aggregation pass (cluster job,
  not done here).
- **2.4 (P1)** `_plot_seasonal_loadshape()` — heating/cooling/all-season diurnal
  overlay, both channels, added to §5. No new gates (as scoped).
- **2.5 (P2)** `_gate_idf_roundtrip()` + `_parse_all_compact_schedules()` +
  `_best_match()` — IDF-text `Schedule:Compact` parser ported from 2J's
  `roundtrip_analysis.py`, generalized from 2J's exact-name lookup to a best-match
  search across all Schedule:Compact objects (3J's schedule-naming convention
  differs per channel/archetype — e.g. office uses `OFC_People_<arch>_<band>` — and
  guessing a name risked a silently-wrong or silently-missing match). Correctly
  falls back to INFO locally (no per-run `*.idf` synced); will populate real
  PASS/WARN values once run where campaign `*.idf` files exist (cluster).
- **2.6 (P2)** One-line INFO gate 3.5-office in `section3()` — no chart, no new logic.
- **2.7 (P2)** Extended `_check_longitudinal()` (§0) to also read
  `office_presence_multiplier_{2005,2010,2015,2022}.csv` and added `_plot_arc2()`
  (2-panel: resid AT_HOME + office AT_WORK) replacing the old single-panel
  `_plot_arc()` (removed, now dead code). Makes the gate-0.5 gating-variable break
  visible instead of text-only.

**Not done (flagged, not silently skipped):** re-running the office aggregator to
add heating/cooling meters (needed for a real 2.3-office chart) — this requires
editing `3rdJ_08_simulation_2split_agg.py`'s office wide-schema regex and a full
re-scan of the office campaign, which lives on cluster scratch; out of scope for a
local-only pass. Next step for whoever picks this up: re-run
`3rdJ_08_simulation_2split_val.py` via `run_validation.sh` on the cluster once
campaign/office runs are current, confirm the new gates/charts render against real
(not locally-partial) data, then commit the refreshed
`outputs_step8/step8_validation_report.html`.

### 2026-07-07 (later) — cluster re-run (job 1069196) confirms all 7 items against real data; report regenerated & synced

Ran `3rdJ_08_simulation_2split_val.py` for real via SLURM job **1069196**
(`3J_8E_val`) on Speed against the full campaign (8,400 residential + 252 office
runs) — the "next step" flagged in the entry above. **COMPLETED, ExitCode 0:0,
Elapsed 00:13:06.** No tracebacks/fatal errors in the log.

**Scorecard: 50 PASS / 1 WARN / 16 INFO / 0 FAIL** (up from the pre-improvements
baseline of 46/1/13/0; the 7 new gates split into 4 PASS + 3 INFO, arithmetic
checks out exactly, FAIL count unchanged at 0).

Per item, now confirmed against real cluster data (not the local partial run):
- **2.5 (P2) IDF-text round-trip** — gates `2.10-resid-roundtrip` and
  `2.11-office-roundtrip` both came back **PASS** (not the INFO fallback the local
  test produced, since real per-run `*.idf` files exist on cluster scratch):
  median/max daily-mean error **0.00%** for both channels (n=15 sampled HH/cells
  each). This closes out the gap this entry's predecessor flagged.
- **2.3 (P1) heating/cooling/other split by CZ** — gates 4.6/4.7 both PASS on
  real data (heating share by CZ: 5A=0.03 … 7A=0.09, rises mild→severe; cooling
  floor max 0.45). **Follow-up:** the surprisingly-large cooling share flagged in
  the local-run note above was investigated further (prompted by user review of
  this report's §4) and confirmed to be a real physical-plausibility issue, not a
  validator bug — root cause traced to two mechanisms in the static residential
  prototype IDFs (frozen 24.0°C year-round cooling setpoint in the MidRise/HighRise
  ASHRAE-90.1 apartment templates, and one Zone-6-localized envelope reused across
  all 6 climate zones with only the EPW weather file varying per CZ), both
  upstream of any numbered pipeline step. Full writeup, evidence tables, and
  ranked fix options:
  `Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`.
  No IDF or code changed — awaiting user decision on which fix to apply.
- **2.6 (P2)** gate `3.5-office` (INFO, full-factorial/no-MC-convergence note) —
  confirmed rendering as intended.
- **4.8-office-enduse** — still INFO as expected; office aggregator still lacks
  heating/cooling meters (unchanged from the "not done" note above).
- **2.1/2.2/2.4/2.7** — longitudinal trajectory, paired-Δ/Δ-by-CZ, seasonal
  diurnal, and office AT_WORK historical arc all rendered without
  `[plot-skip]`/`[section-error]` in the log.

`outputs_step8/step8_validation_report.html` was scp'd down from
`/speed-scratch/o_iseri/step8_2split/upload/.../outputs_step8/` and now shows as
a **modified, uncommitted** file in `git status` — left as-is for review, per
instruction not to auto-commit.

### 2026-07-08 — item 2.3's chart (`_plot_enduse_split`) is metering-artifact-affected; added a true end-use-energy companion chart (Fix v3)

The user flagged, while reviewing `step8_validation_report_v3_section4_local.html`,
that the §4 heating/cooling chart still showed cooling far exceeding heating even
in the coldest CZ — which is exactly the metering artifact traced in
`investigation/step8_resid_heating_cooling_dominance_investigation.md` §11/§12:
`_plot_enduse_split()` (added in the 2.3 item above, 2026-07-07) reads
`heating_ET_kWh`/`cooling_ET_kWh` from `agg_annual.csv`, i.e. E+'s
`:EnergyTransfer` zone thermal-load meters — for the two ventilated apartment
archetypes (MidRise/HighRise), cold ERV ventilation air gets counted as
"cooling" on that meter with zero compressor electricity behind it, so the chart
was never wrong about the *data it plots*, but that data isn't a fair
heating-vs-cooling comparison. This is the same root cause the 2026-07-07 (later)
entry above flagged as "worth a sanity look before citing in the paper" —
confirmed and fixed via Fix v3.

**Fix (this session, no re-simulation — see the coolfix investigation/plan docs
for the full Fix v3 writeup):**
- Relabeled `_plot_enduse_split()`'s axis/title to say "air-system delivered
  sensible energy (incl. ventilation air)" instead of "end-use energy transfer" —
  it's still a legitimate, useful chart, just not an end-use-energy comparison,
  and should never be captioned as one.
- Added a new companion chart, `_plot_enduse_energy_split()`, plotting the
  **true fuel/electricity end-use energy** (heating fuel vs cooling electricity,
  per archetype × CZ, from `agg_enduse_annual.csv`) that backs gates 4.9/4.10.
  This is the chart that should be cited for any heating-vs-cooling-dominance
  claim in the paper — it is not subject to the ERV-artifact.
- **Found and fixed a second, unrelated bug while building this**: the
  End-Uses extractors (`extract_enduse_annual.py` for the cluster/sqlite path,
  `extract_enduse_annual_from_tbl.py` for the local/csv path) assumed every
  archetype's EnergyPlus output reports energy in GJ. In fact `OutputControl:
  Table:Style`'s unit-conversion setting differs by archetype family: SingleD
  and OtherDwelling (house prototypes) report in **kBtu** (IP units), while
  MidRise and HighRise (apartment prototypes) report in **GJ** (SI units) —
  confirmed by diffing `eplustbl.csv` headers across archetypes. Treating kBtu
  values as GJ inflated SingleD/OtherDwelling's absolute heating/cooling GJ
  figures by ~950× (e.g. one house's true 18.1 GJ annual heating was misread as
  18,137 "GJ"). Both extractors now read the unit token (`Units` column in
  sqlite; the `[GJ]`/`[kBtu]` header suffix in the CSV) and convert to GJ.
  **The gate-4.9 ratio itself was never wrong** — heating and cooling for a
  given archetype/run share the same unit bug, so it canceled out of the ratio —
  only the absolute GJ figures shown in the new 4.10 table were affected before
  this fix. Re-ran the local 600-row extraction + `--section 4` validator after
  the fix; `step8_validation_report_v3_section4_local.html` regenerated with
  corrected 4.10 numbers and the new chart (3 images embedded total: EUI bands,
  the relabeled ET-based split, the new true end-use-energy split).

### 2026-07-08 (later) — v3 merged report independently verified by manager; ACCEPTED by user

The Fix-v3 outputs (`step8_validation_report_v3_section4_local.html` — §4-only,
from the local 600-run extraction — and `step8_validation_report_v3_merged.html`
— the full job-1069196-era baseline with the re-based §4 gates merged in) were
reviewed by the manager session and **accepted by the user (2026-07-08)** as the
standing validation record until the canonical cluster regen.

**Verification performed (independent, not a read-through):**
- Every §4 end-use figure was recomputed directly from
  `outputs_step8/agg/agg_enduse_annual.csv` (600 rows: 4 arch × 3 CZ × 50
  samples, 2022, no zero/missing rows) — **exact match** against both HTMLs
  (e.g. table 4.10 MidRise 7A heating 7,798.9 GJ = 50 × 156.0 GJ mean; cooling
  5,189.4 GJ = 50 × 103.8).
- Extractor ground truth re-confirmed: the dry-run CSVs in
  `outputs_step8/coolfix_verify/` reproduce the smoke run's known values to the
  cent (MidRise HH80741 2022: heating_gas 78.34 GJ, cooling_elec 136.12 GJ).
- §0–§3 and §5–§7 in the merged report are identical to the previously accepted
  baseline (the metric fix only touches §4), as expected.

**Outcome — merged scorecard 50 PASS / 2 WARN / 17 INFO / 0 FAIL.** The two
WARNs are both understood: 4.1-SingleD (pre-existing EUI-basis difference) and
4.9-heat-dominance. On the corrected end-use metric the physics is right:
**CZ 7A apartments are heating-dominated** (cooling-elec/heating ratios
MidRise 0.67×, HighRise 0.71×; houses 0.20–0.33×) — the old 9.8× "dominance"
is fully attributed to the ET metering artifact. The 4.9 WARN is triggered by
the 6A/6B apartments (MidRise/HighRise ≈1.4× in 6A, ≈1.7× in 6B), the known
prototype characteristic (dense ASHRAE internal gains + tight STD2022 envelope
+ ERV recovery) → **paper caveat, not a bug**. Heating rises monotonically
mild→severe CZ for every archetype; Calgary (6B) heating sitting below
Montreal (6A) despite higher HDD was queried and **confirmed by the user as a
real regional weather regime** (sunny/chinook winters), not an anomaly. The
smoke household's 1.74× ratio sits inside the campaign 7A tail (max 2.80×) —
smoke and campaign data are mutually consistent.

**Provenance caveat of the accepted report:** §4's re-based gates are backed by
the 2022-scenario-only 600-run subset (CZ coverage for gate 4.9 is complete —
it only tests 6A/6B/7A); the merged header still carries the baseline's
"Generated 2026-07-07" stamp.

**Remaining (owed at canonical full-campaign regen once Speed is back):**
1. Regenerate on the cluster against all 8,400 resid runs / 7 scenarios (the
   sqlite extractor + re-based validator path from the Fix-v3 plan).
2. Three cosmetic report tweaks: (a) gate 4.9's message should print the
   triggering 6A/6B ratios, not only the healthy 7A ones; (b) label table
   4.10's GJ values as n=50-sample **sums**, not per-building; (c) refresh the
   merged header's generation date.
3. Sequence the same re-aggregation fix for 2J, then refresh any paper numbers
   that cited ET-based cooling.
