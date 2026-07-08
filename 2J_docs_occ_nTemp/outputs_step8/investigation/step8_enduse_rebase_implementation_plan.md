# 2J Step 8 — End-Use Metric Re-Base Implementation Plan (Fix v3 port from 3J)

**Authored:** 2026-07-08 (manager) · **Status: READY FOR EXECUTION — local-first, NO cluster compute**
**Executes the revised fix from §7 of** `step8_resid_heating_cooling_dominance_investigation.md`
**(this folder). The 3,000-run re-sim originally planned there is CANCELLED — this plan is
re-aggregation + validator re-base only. No IDF, template, runner, or Step-9 change. All 6,000
existing 2J runs stay valid.**

**Reference implementations (3J, already executed & user-accepted 2026-07-08):**
- Plan: `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_coolfix_implementation_plan.md` (section "Fix v3")
- Extractors: `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/extract_enduse_annual.py`
  (sqlite path) and `extract_enduse_annual_from_tbl.py` (eplustbl.csv path) — **both already
  carry the kBtu/GJ unit fix; keep it** (house prototypes report End Uses in kBtu, apartment
  prototypes in GJ — same mix in 2J).
- Validator pattern (gate 4.9/4.10, `--section` arg, chart): `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py`
- Root-cause trace: 3J investigation §11 (metering artifact: thermostat-independent ERV
  ventilation air on `Cooling:EnergyTransfer`; Mechanism A retired).

## Aim

Re-base 2J's §4 heating-vs-cooling dominance evidence from the `:EnergyTransfer` metric (artifact-
affected for the ventilated apartment archetypes) to true end-use energy (ABUPS End Uses: Cooling
Electricity vs Heating fuel), add the dominance gate 2J's validator lacks, and produce a locally
verified §4 report + merged report — without waiting for the cluster (login-node file access
works; compute jobs are off-limits for ~2 weeks from 2026-07-08).

## Constraints (unchanged)

- 🔴 Cluster hard rules per CLAUDE.md. **This pass submits ZERO sbatch jobs.** Login node used
  only for: `ls` (layout/retention checks), one single-invocation `tar` (one-shot archive I/O —
  precedent: the 3J subset fetch, user-approved 2026-07-08; no loops, no recursion via shell,
  one command), and one `scp`. All single-line, each labeled "locally" / "on the cluster".
- Do NOT modify `BEM_setup/Buildings_MTL_v242/` templates (provenance record of submitted
  results), `eSim_bem_utils_2J/` runtime code, or anything in 3J.
- Do NOT overwrite the canonical `outputs_step8/step8_validation_report.html` (full-campaign,
  cluster-generated). Local runs write to a separate `--out-dir` AND rename their HTML.
- No git commits (user owns git).

## Steps (phases 2JV3-A … 2JV3-F)

### 2JV3-A — port the extractors locally + dry-run gate
1. Copy the two 3J extractor scripts into `2J_docs_occ_nTemp/outputs_step8/investigation/` and
   adapt only the path/cell-parsing bits to the 2J campaign layout (expected
   `<ARCH>__<City>_<CZ>/sample_*/<year>/…` — confirm actual naming in 2JV3-B before finalizing
   the regex; 2J "scenario" = calendar year 2005/2010/2015/2022/2030). Output schema identical
   to 3J: `cell, arch, city, cz, scenario, sample, hh_id, heating_gas_GJ, heating_elec_GJ,
   heating_district_GJ, cooling_elec_GJ, cooling_gas_GJ, cooling_district_GJ`. Stdlib only.
2. **Dry-run gate:** run the tbl-variant against the 3J smoke tree
   (`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/campaign_smoke_v2/`) — MidRise
   sample_001 2022 must return `heating_gas_GJ=78.34`, `cooling_elec_GJ=136.12` **exactly**.
   FAIL → fix before touching the cluster.

### 2JV3-B — subset fetch from cluster scratch (login node only, no compute)
3. Locate the 2J campaign root on `/speed-scratch/` from the local 2J Step8 run scripts /
   sbatch wrappers (`Step8_docs/run_bem.py`, `run_paired_mc.py`, `run_batch_hpc.py`, any `.sh`);
   confirm with a single `ls` on the cluster, then one more `ls` into one
   `sample_*/2022/` to verify **`eplustbl.csv` is present** per run (runner persists full E+
   output dirs by design — `eSim_bem_utils_2J/main.py:1994`). **If eplustbl.csv is absent:
   STOP and report** (fallback options are a manager decision — .sql files are ~41 MB each,
   a 600-file download is a different conversation).
4. One-shot `tar` on the cluster of the gate-4.9 subset: **year 2022 × CZ ∈ {6A, 6B, 7A} × all
   4 archetypes × 50 samples = 600 `eplustbl.csv` files** (~1–2 MB each → manageable single
   archive), then one `scp` down to
   `2J_docs_occ_nTemp/outputs_step8/campaign_subset_v3_enduse/`. Mirror the 3J tar/scp pattern
   (memory: single 600 MB archive beat 3,000 individual transfers).

### 2JV3-C — local extraction + ground-truth check
5. Run the tbl extractor over the subset → `2J_docs_occ_nTemp/outputs_step8/agg/agg_enduse_annual.csv`
   (expect 600 rows; tally line `dirs/parsed/skipped`).
6. **Hand-verify two files** (one apartment, one house): grep the End Uses Heating/Cooling rows
   straight from the `eplustbl.csv`, confirm the CSV row matches after unit conversion (house
   header will say `[kBtu]`, apartment `[GJ]` — the unit branch MUST be exercised by both
   families). Compute the per-arch × CZ ratio table (mean cooling-elec / mean heating-fuel) and
   include it in the report to the user.

### 2JV3-D — validator re-base (edit + local §4 run)
7. Archive `2J_docs_occ_nTemp/08_simulation_val.py` →
   `2J_docs_occ_nTemp/outputs_step8/archive/08_simulation_val.20260708_preEnduseMetric.py`.
8. Edits (mirror the 3J validator, incl. its post-acceptance cosmetic lessons):
   - **New gate 4.9-heat-dominance** — source `agg/agg_enduse_annual.csv`; ratio =
     `cooling_elec / (heating_gas + heating_elec + heating_district)` (site GJ), per archetype ×
     CZ ∈ {6A, 6B, 7A}. Thresholds: **FAIL > 2.0× in 7A; WARN > 1.25× in any of 6A/6B/7A.**
     Message must print the ratios for ALL THREE tested CZs (3J lesson: printing only 7A while
     6A/6B trip the WARN confuses readers) and state the data provenance ("2022 subset, n=50/cell").
   - **New gate 4.10-enduse-table** (INFO) — heating fuel vs cooling electricity per archetype ×
     CZ from the new csv, **explicitly labeled as n=50-sample sums** (3J lesson).
   - **New chart** `_plot_enduse_energy_split()` — true end-use energy bars (cite THIS one in
     the paper, never the ET chart).
   - **Relabel, don't remove**, the existing ET-based §4 material: chart title
     `Heating / Cooling / Other Split by CZ` (`08_simulation_val.py:694-711`) and gates 4.2/4.3
     wording (`:620-640`) → "air-system delivered sensible energy (incl. ventilation air)".
     Their PASS/WARN logic is unchanged.
   - **Add a `--section` argparse option** (copy the pattern from
     `3rdJ_08_simulation_2split_val.py`) so §4 can run standalone; 2J's validator currently has
     none (`08_simulation_val.py:1361-1381`) and hardcodes its HTML name (`:1342`).
   - `py -m py_compile` must pass.
9. Local §4 run: `--section 4` + `--agg-dir outputs_step8/agg` + **`--out-dir` pointed at a
   fresh directory** (e.g. `outputs_step8/v3_local/`), then rename the HTML to
   `outputs_step8/step8_validation_report_v3_section4_local.html`. The canonical HTML is not
   touched. Note: EUI bands + relabeled ET chart regenerate from the full local
   `agg_annual.csv` (all years/CZs); only 4.9/4.10 use the 2022 subset.

### 2JV3-E — merged report
10. Splice the re-based §4 (gate rows + charts) into a copy of the canonical
    `outputs_step8/step8_validation_report.html`, recompute the scorecard counts →
    `outputs_step8/step8_validation_report_v3_merged.html` (mirror the 3J merge; a small local
    python script is fine). Canonical file remains untouched.

### 2JV3-F — docs + STOP
11. Append Progress Log rows to the investigation doc and to this plan (subset fetched, dry-run
    result, hand-check result, gate 4.9 outcome with the full ratio table, files produced).
    Report to the user and STOP. **Do not** edit `readySubmission.md` or any paper text — the
    paper re-basing decision is the user's, made on these numbers.

### Later phase (cluster compute back — OUT OF SCOPE for this pass)
Full-campaign canonical regen: sqlite extractor over all 6,000 runs + full (no `--section`)
validator run, chained `sbatch --dependency=afterok:`, 7-day walltime — sequenced AFTER the 3J
canonical regen re-verifies the extractor at scale. Only then does the canonical
`step8_validation_report.html` get replaced.

## Expected result

- `agg/agg_enduse_annual.csv` (600 rows, 2022, CZ 6A/6B/7A) + the two local HTMLs, canonical
  untouched.
- Gate 4.9 prediction (to confirm, not assume — the gate decides): 3J's end-use re-base flipped
  CZ7A apartments to heating-dominated (0.67–0.71×), and 2J's ET ratios (3.36×/1.86×) were milder
  than 3J's ET ratios (9.8×/5.3×) → 2J 7A plausibly ≤1×, 6A/6B possibly WARN (>1.25×,
  prototype characteristic). **A 4.9 FAIL (>2.0× in 7A on end-use energy) → STOP and report;
  that would be a real finding, not a metric artifact.**
- Paper stance unchanged from investigation §7: `readySubmission.md` EUI/site-energy numbers
  unaffected; only dominance-split claims need re-basing on the 4.10 table.

## Test method

Extractor: exact-match dry-run on the 3J smoke tree (78.34/136.12) + two-file hand-check on 2J
data with both unit families exercised. Validator: py_compile + §4-scoped local run into a
separate out-dir + visual check that 4.9/4.10/new chart render and ET material is relabeled.
Merge: scorecard arithmetic (old counts − replaced §4 gates + new §4 gates) checks out; spot-diff
a non-§4 section against the canonical to prove it's unchanged.

---

## Progress Log

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-08 | Plan authored (manager); employee prompt at `step8_enduse_rebase_employee_prompt.md` (this folder) | READY FOR EXECUTION | Fresh Sonnet employee session; local-first, zero sbatch; mirrors 3J Fix v3 incl. kBtu/GJ unit fix and post-acceptance cosmetic lessons (4.9 message prints all tested CZs; 4.10 labeled as n=50 sums; canonical HTML never overwritten). |
| 2026-07-08 | Executed 2JV3-A…F (employee) | **DONE — 0 FAIL, gate 4.9 PASS clean** | **2JV3-A:** ported both 3J extractors to `outputs_step8/investigation/` (paths only adapted — 2J's `outputs_step8/` sits one level shallower than 3J's, no `Step8_docs/` layer; cell/sample regex unchanged, confirmed identical to `eSim_bem_utils_2J/main.py:2056`). Dry-run vs 3J smoke tree: exact match, MidRise sample_001 2022 → `heating_gas_GJ=78.34`, `cooling_elec_GJ=136.12`. **2JV3-B:** canonical campaign root confirmed as `/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/campaign_N50` (from `step8_aggval_v2.sh`); on-cluster `ls` confirmed cell naming (`<ARCH>__<City>_<CZ>`, CZ 6A=Montreal, 6B=Calgary, 7A=Winnipeg) and `eplustbl.csv` presence per run; one-shot `tar` (bash brace-expansion, single invocation, no shell loop) archived 600 files (571 MB) for 2022 × {Montreal_6A, Calgary_6B, Winnipeg_7A} × 4 archetypes × 50 samples; one `scp` down + local extract → 600 files confirmed on disk. **2JV3-C:** extractor ran 600/600 parsed, 0 skipped → `agg/agg_enduse_annual.csv`. Hand-verified 2 files against raw `eplustbl.csv` End Uses rows: MidRise__Montreal_6A sample_001 (GJ family) heating_gas=144.92, cooling_elec=80.30 — exact match; SingleD__Montreal_6A sample_001 (kBtu family) heating_gas=24655.30 kBtu→26.0127 GJ, cooling_elec=4917.68 kBtu→5.1884 GJ — exact match. Both unit branches exercised. **Full ratio table (mean cooling_elec/mean heating_fuel, n=50/cell):**<br>`HighRise 6A=0.341 6B=0.367 7A=0.256`<br>`MidRise  6A=0.400 6B=0.321 7A=0.259`<br>`OtherDwelling 6A=0.346 6B=0.202 7A=0.203`<br>`SingleD  6A=0.224 6B=0.143 7A=0.153`<br>All ratios ≤0.40× — far below the 1.25× WARN and 2.0× FAIL thresholds; end-use energy is heating-dominated everywhere, more decisively than the 3J precedent (0.67–0.71× in 7A) predicted. **2JV3-D:** archived pre-edit validator to `outputs_step8/archive/08_simulation_val.20260708_preEnduseMetric.py`; added gate 4.9 (heat-vs-cool dominance, FAIL>2.0× in 7A / WARN>1.25× in 6A/6B/7A, message prints ratios for all 3 CZs + "2022 subset, n=50/cell" provenance) and gate 4.10 (INFO end-use table, labeled n=50-sample sums) to `validate_physical_plausibility()`; added `_plot_enduse_energy_split()` chart; relabeled gate 4.2/4.3 messages and the `_plot_heat_cool_split` chart title to "air-system delivered sensible energy (incl. ventilation air)" (PASS/WARN logic unchanged); added `--section` argparse (1–7) + refactored `run_all(section=None)`. `py -m py_compile` passed. Local `--section 4` run (fresh `outputs_step8/v3_local/`) → gate 4.9 **PASS** (all ratios ≤0.40×, well under 1.25×), 3 charts rendered; HTML renamed to `step8_validation_report_v3_section4_local.html`; canonical untouched (verified by mtime/md5 before and after). **2JV3-E:** wrote `investigation/merge_v3_report.py`, spliced the re-based §4 block (gate rows + 3 charts) into a copy of the canonical HTML → `step8_validation_report_v3_merged.html`; scorecard recomputed 24→25 PASS, 3→4 INFO (net +1 gate: old 4.1–4.4 replaced 4-for-4, plus new 4.9 PASS + 4.10 INFO), 0 WARN/FAIL throughout; verified sections s1/s2/s3/s5/s6/s7 byte-identical between canonical and merged; canonical file mtime/md5 unchanged (Jun 11, `3599e088…`). **Files produced:** `outputs_step8/agg/agg_enduse_annual.csv` (600 rows), `outputs_step8/campaign_subset_v3_enduse/` (600 eplustbl.csv), `outputs_step8/step8_validation_report_v3_section4_local.html`, `outputs_step8/step8_validation_report_v3_merged.html`, `outputs_step8/investigation/{extract_enduse_annual.py, extract_enduse_annual_from_tbl.py, merge_v3_report.py}`. **Zero sbatch jobs. Zero cluster compute.** No FAIL anywhere — gate 4.9 confirms (does not merely predict) that 2J's apartment heating/cooling dominance anomaly is a metering artifact, not a physical or template defect. |
| 2026-07-08 (later still) | UX fix: user flagged that the retained ET-based §4 chart still visually shows cooling ≥ heating in cold CZs (correct per its own logic, but confusing without a clear pointer to the corrected chart) | **DONE — captions added, gate values unchanged** | Extracted and visually inspected the 3 §4 chart images from the merged report to confirm the read: the relabeled ET chart (`_plot_heat_cool_split`) shows cooling share 0.43–0.48 vs heating 0.13–0.42 across CZ 5C→7A (matches gate 4.3's `min CZ cooling share 0.426`) — this is the known ERV-ventilation-air metering artifact, correctly reproduced, not a new bug. The true end-use chart (`_plot_enduse_energy_split`) directly below it already showed heating >> cooling everywhere, but the two charts sat back-to-back with no visual callout distinguishing "known-artifact, don't cite" from "corrected, cite this one" — a reasonable source of confusion on a skim. Fix: extended `multi_chart()` in `08_simulation_val.py` to accept `(caption, b64)` tuples and render an inline note under a chart; added a ⚠ caption on the ET chart ("known metering artifact... do NOT cite... see the true end-use-energy chart below, which supersedes this one") and a ✓ caption on the end-use chart ("this is the chart to cite... supersedes the ET-based chart above"). Pure presentation change — gate 4.1–4.4/4.9/4.10 values, thresholds, and PASS/WARN/FAIL logic all unchanged (re-verified identical output on re-run). Re-ran `--section 4` + `merge_v3_report.py`; scorecard unchanged (25 PASS/4 INFO/0 WARN/0 FAIL); canonical `step8_validation_report.html` md5 unchanged (`3599e088…`). |
| 2026-07-08 (later still) | UX fix #2: user flagged a color-coding clash — chart 1 (EUI benchmark) colored HighRise=red/SingleD=blue, while charts 2/3 directly below use red=Heating/blue=Cooling, so scanning down the page reads as a false link between an archetype and a heating/cooling meaning | **DONE — chart 1 recolored, gate values unchanged** | `_plot_eui_benchmark()` in `08_simulation_val.py` (~line 762) changed its 4-archetype palette from `[accent(blue), green, yellow, red]` to `[green, yellow, peach, mauve]` — deliberately excludes accent/red so no chart in §4 reuses colors with two different meanings. Re-ran `--section 4` + `merge_v3_report.py`; gate 4.1–4.4/4.9/4.10 values and scorecard (25 PASS/4 INFO/0 WARN/0 FAIL) unchanged (pure presentation change); canonical `step8_validation_report.html` md5 unchanged (`3599e088…`). |
