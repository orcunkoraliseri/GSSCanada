# EMPLOYEE PROMPT — 2J Step 8 end-use metric re-base (Fix v3 port; NO re-sim, NO sbatch)

You are the **employee**. Execute the task below and append a Progress Log entry on completion.

**Task doc (authoritative, read first):**
`2J_docs_occ_nTemp/outputs_step8/investigation/step8_enduse_rebase_implementation_plan.md`
**Context (read §7):**
`2J_docs_occ_nTemp/outputs_step8/investigation/step8_resid_heating_cooling_dominance_investigation.md`

**TL;DR:** 2J's §4 report shows apartment cooling ≫ heating in cold CZs. This was traced (3J
investigation §11) to a METERING artifact, not a model bug: `Cooling:EnergyTransfer` counts
thermostat-independent ERV ventilation air as "cooling" at zero electricity. The templates were
never broken; **the planned 3,000-run re-sim is CANCELLED; all 6,000 runs stay valid.** Your job:
re-base §4 onto true end-use energy (ABUPS End Uses: Cooling Electricity vs Heating fuel) by
porting the already-verified 3J Fix v3 — extract a 600-run 2022 subset's `eplustbl.csv` from
cluster scratch, aggregate locally, add gate 4.9/4.10 + chart to `08_simulation_val.py`, produce
a local §4 report + merged report. The cluster's COMPUTE is unavailable (~2 weeks from
2026-07-08) but the login node is reachable for file operations.

---

## 🔴 Cluster hard rules (account-suspension risk — flagged 3×, one more = ban)

- **ZERO `sbatch` jobs this task.** Nothing runs on the cluster. NEVER a blocking `srun` or bare
  `python` on the login node (`speed-submit2`).
- Allowed on the login node, single-line only, each labeled "on the cluster": `ls`, `scp`,
  `cd`, plus **exactly one one-shot `tar` invocation** (archive I/O, precedent user-approved
  2026-07-08 for the 3J subset fetch — one command, no loops, then done).
- Everything else runs **locally** — label those commands "locally".

## Reference implementations (3J — executed, verified, user-accepted 2026-07-08)

- Extractors (copy + adapt; **both already handle the kBtu/GJ unit split — KEEP that logic**,
  house prototypes report End Uses in kBtu, apartments in GJ):
  `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/extract_enduse_annual.py` (sqlite)
  `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/extract_enduse_annual_from_tbl.py` (tbl.csv — the one you'll run)
- Validator gate/chart/`--section` pattern:
  `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py` (gate
  4.9-heat-dominance, gate 4.10 table, `_plot_enduse_energy_split`, ET relabeling)
- Dry-run ground truth: `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/campaign_smoke_v2/`
  (MidRise sample_001 2022: `heating_gas_GJ=78.34`, `cooling_elec_GJ=136.12`)

## Phase 2JV3-A — port extractors + dry-run gate (local)

1. Locally: copy both 3J extractor scripts into
   `2J_docs_occ_nTemp/outputs_step8/investigation/` and adapt ONLY paths + cell-name parsing to
   the 2J campaign layout (expected `<ARCH>__<City>_<CZ>/sample_*/<year>/…`, years
   2005/2010/2015/2022/2030 — finalize the regex after you see the real `ls` output in
   2JV3-B). Output schema unchanged: `cell, arch, city, cz, scenario, sample, hh_id,
   heating_gas_GJ, heating_elec_GJ, heating_district_GJ, cooling_elec_GJ, cooling_gas_GJ,
   cooling_district_GJ` (scenario = year). Stdlib only. Skip-and-log; final tally line.
2. Locally: dry-run the tbl extractor against the 3J smoke tree (point its campaign-dir env/arg
   at `.../outputs_step8/campaign_smoke_v2`) — **gate: exact match** on 78.34 / 136.12 for
   MidRise sample_001 2022. FAIL → fix before touching the cluster.

## Phase 2JV3-B — subset fetch (cluster login node, file ops only)

3. Locally: find the 2J campaign root on `/speed-scratch/` from the 2J run scripts
   (`2J_docs_occ_nTemp/Step8_docs/run_bem.py`, `run_paired_mc.py`, `run_batch_hpc.py`, any
   `.sh`/sbatch wrappers or prior scp notes).
4. On the cluster: one single-line `ls` of the campaign root (confirm cell dir naming), then one
   `ls` into one `sample_*/2022/` — confirm **`eplustbl.csv` exists** (runner persists full E+
   run dirs by design, `eSim_bem_utils_2J/main.py:1994`). **If eplustbl.csv is missing → STOP
   and report; do not improvise a fallback** (.sql files are ~41 MB each — manager decision).
5. On the cluster: ONE single-line `tar` bundling the subset — **year 2022 × the three cell
   groups whose names end `_6A` / `_6B` / `_7A` × all 4 archetypes = 600 `eplustbl.csv` files**
   (use tar's own include patterns / a generated file list via `ls`, not a shell loop) — then
   locally: ONE `scp` of the archive down to
   `2J_docs_occ_nTemp/outputs_step8/campaign_subset_v3_enduse/` and extract it there.

## Phase 2JV3-C — extract + ground-truth check (local)

6. Locally: run the tbl extractor over the subset →
   `2J_docs_occ_nTemp/outputs_step8/agg/agg_enduse_annual.csv`. Expect 600 rows (4 arch × 3 CZ ×
   50 samples, 2022). Report the tally.
7. Locally: hand-verify TWO files — one apartment (`[GJ]` header) and one house (`[kBtu]`
   header): grep the End Uses Heating/Cooling rows from the raw `eplustbl.csv` and confirm the
   CSV row matches after unit conversion. **Both unit families must be exercised.** Then compute
   and report the ratio table: per archetype × CZ, mean cooling_elec / mean heating fuel
   (gas+elec+district).

## Phase 2JV3-D — validator re-base + local §4 run (local)

8. Locally: archive `2J_docs_occ_nTemp/08_simulation_val.py` →
   `2J_docs_occ_nTemp/outputs_step8/archive/08_simulation_val.20260708_preEnduseMetric.py`, then
   edit the validator (mirror the 3J validator's implementations):
   - **Gate 4.9-heat-dominance**: reads `agg/agg_enduse_annual.csv`; ratio =
     `cooling_elec / (heating_gas + heating_elec + heating_district)` per archetype ×
     CZ ∈ {6A,6B,7A}; **FAIL > 2.0× in 7A, WARN > 1.25× in any of 6A/6B/7A**. The message MUST
     print the ratios for all three CZs and state "2022 subset, n=50/cell" (3J cosmetic lesson —
     don't print only 7A).
   - **Gate 4.10-enduse-table** (INFO): heating fuel vs cooling electricity per archetype × CZ,
     values **labeled as n=50-sample sums** (3J lesson).
   - **`_plot_enduse_energy_split()`**: end-use energy bar chart (this is the paper-citable one).
   - **Relabel (do not remove)** the ET-based material: chart title at
     `08_simulation_val.py:694-711` and gate 4.2/4.3 wording at `:620-640` → "air-system
     delivered sensible energy (incl. ventilation air)". Logic unchanged.
   - **Add a `--section` argparse option** (pattern from the 3J validator) — 2J currently has
     none and hardcodes its HTML filename at `:1342`.
   - `py -m py_compile` must pass.
9. Locally: run `--section 4` with `--agg-dir` at `outputs_step8/agg` and **`--out-dir` at a
   FRESH directory** (`outputs_step8/v3_local/`) — 🔴 NEVER let this run write
   `outputs_step8/step8_validation_report.html` (the canonical full-campaign report; the 3J
   session overwrote theirs by accident and had to restore it). Rename the produced HTML to
   `outputs_step8/step8_validation_report_v3_section4_local.html`. Check: 4.9/4.10 + new chart
   render; EUI + relabeled ET charts regenerate from the full local `agg_annual.csv`.

## Phase 2JV3-E — merged report (local)

10. Locally: splice the re-based §4 (gate rows + charts) into a COPY of the canonical
    `outputs_step8/step8_validation_report.html`, recompute the scorecard counts →
    `outputs_step8/step8_validation_report_v3_merged.html`. Verify one non-§4 section is
    byte-identical to the canonical. Canonical file untouched.

## STOP + report (Phase 2JV3-F)

11. Append Progress Log rows to BOTH the investigation doc and the implementation plan (dry-run
    result, subset fetch details, hand-check result, **full 4.9 ratio table**, gate outcome,
    files produced). Report the same to the user. **STOP conditions along the way:**
    eplustbl.csv absent on scratch (step 4); extractor dry-run mismatch (step 2); **gate 4.9
    FAIL** (>2.0× in 7A on end-use energy — that would be a real physical finding, not the
    artifact; report, don't fix). Do NOT touch `readySubmission.md`, the
    `BEM_setup/Buildings_MTL_v242/` templates, `eSim_bem_utils_2J/` runtime code, Step 9, or
    anything under `3J_docs_occ_nTemp/`. No git commits. No sbatch.

**Expected end state:** `agg_enduse_annual.csv` (600 rows) + `step8_validation_report_v3_section4_local.html`
+ `step8_validation_report_v3_merged.html`; canonical HTML untouched; zero cluster compute;
expected (to confirm, not assume) 7A apartments ≤1× on end-use energy with possible 6A/6B WARN.
The later full-campaign canonical regen (sqlite extractor + full validator via chained sbatch)
happens in a separate session once cluster compute is back, after the 3J canonical regen.
