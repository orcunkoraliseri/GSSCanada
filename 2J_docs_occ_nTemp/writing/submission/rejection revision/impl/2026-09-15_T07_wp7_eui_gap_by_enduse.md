# T07 — WP7 step 2: where the energy-intensity gap sits, by end use — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP7, §10 Wave 2
Status:     DONE — Speed job 1328260 collected, closure test measured (see Verified)

## Task

**Why.** After the 2026-08-06 correction, all four archetypes sit BELOW their survey (SHEU) energy
intensity ranges. We need to show which end use carries the gap. Expected (test, do not assume):
space heating, which was never calibrated.

**Critical warning.** The `eui_kWh_m2` and `total_energy_kWh` columns in `outputs_step8/agg/` come
from a defective function (`calculate_eui()`, peak-demand table summed in, US gallons counted as kWh).
**Never use them.** The corrected recompute and its method are in
`GSSCanada-main/3J_docs_occ_nTemp/improvements/v4/V4-B4_RESULTS.md` and `V4-B4_PREREGISTRATION.md`.
Read both first. The raw per-run tables are local:
`GSSCanada-main/BEM_Setup/SimResults_Step8/campaign_N50/<Arch>__<City>/sample_*/…/eplustbl.csv`.
The submitted Table 5 is in `writing/submission/archive/2J_manuscript_submission.md` (grep only).

**Steps.**
1. From V4-B4, find the corrected per-run end-use values if they were saved to disk. If a per-run
   end-use file exists, this task is local reading only: note its path, row count and columns.
   If only totals were saved, the end-use split must be recomputed from `eplustbl.csv` with the
   V4-B4 corrected parsing (pinned report name, unit-aware water) — then write a script in
   `T07_scripts/` and run it on Speed (step 3).
2. Find the SHEU end-use split per dwelling type that Table 5 used (space heating, water heating,
   appliances, lighting, space cooling), with its table number and units, from files on disk
   (`deepResearch/`, Step-8 docs). Quote `file:line`. If the split is not on disk, write NOT FOUND;
   do not fetch it from the web.
3. If computing: upload only the 2022 `eplustbl.csv` files needed plus the script to
   `/speed-scratch/o_iseri/2J_revision/T07/`, `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00`, JobID
   in Ledger, **end your turn**.
4. Output `T07_out/eui_gap_by_enduse_2022.csv`: archetype, end use, simulated kWh/m² (2022, conditioned
   floor-area basis as in Table 5), SHEU kWh/m² low/high if found, gap. Plus a closure row: end uses
   sum back to the corrected Table 5 total.

**Test.** End-use breakdown sums back to the corrected Table 5 total per archetype (tolerance: the
V4-B4 reconstruction error, 0.0005 kWh/m², or state the measured gap).

**Not for the paper.** 2022 only; 2030 is defective (WP1).

**Employee rules.** Plan §10 rules 1–6 apply. Also:
- Speed login node: ONLY `sbatch squeue sacct scancel ls cat head tail grep wc -l scp`. **No `find`,
  no `du`, no recursive listing, no python** on the cluster.
- tcsh: no `2>&1` or `2>/dev/null` in ssh strings. `ssh -o BatchMode=yes -o ConnectTimeout=60`.
- Local python is `py -3` (not `python`). Never read a multi-MB file into context.
- Submit and end the turn. Never wait or poll.

## Ledger

- **Local, no cluster.** Built `t07_manifest_2022.csv`: for every 2022 row of
  `outputs_step8/agg/agg_annual.csv` (the V4-B4-validated published aggregate, "shipped == published"
  for 6000/6000 runs per `V4-B4_RESULTS.md` §1), resolved `(arch,city,sample,sim_hh_id)` to
  `<arch>__<city>/sample_<NNN>_HH<sim_hh_id>/2022/eplustbl.csv` under
  `BEM_Setup/SimResults_Step8/campaign_N50/`. 1200 rows (300/archetype), 0 missing, 0 duplicate
  relpaths — this resolves the ambiguity from the 2026-07-11 resim, which left **2392** matching
  `*2022*eplustbl.csv` files on disk (roughly double 1200) because of stale/duplicate
  `sample_NNN_HH<oldid>` dirs alongside the current ones; `sim_hh_id` from the validated aggregate
  is the tie-breaker.
- **Local, no cluster.** Wrote `T07_scripts/eui_enduse_by_run.py` (V4-B4-corrected parsing: pins the
  `eplustbl.csv` **"End Uses"** table only, stops before "End Uses By Subcategory" — never reads it,
  which is V4-B4 defect 1; excludes the Water column **by position** — it is always the last of 14
  data columns in that table — instead of string-matching `'m3'`/`'gal'`, which fixes V4-B4 defect 2
  for both SI and IP archetypes by construction). Maps rows to the 5 SHEU categories: space_heating
  = Heating; water_heating = Water Systems; space_cooling = Cooling; lighting = Interior+Exterior
  Lighting; appliances = everything else (Interior/Exterior Equipment, Fans, Pumps, Heat Rejection,
  Humidification, Heat Recovery, Refrigeration, Generators).
- **Local, no cluster.** Dry-run on 6 of the 1200 files (2/archetype for HighRise/SingleD, 1/archetype
  for MidRise/OtherDwelling): reproduces V4-B4's corrected 2022 pooled totals closely — HighRise 77.72
  (V4-B4: 78.21), MidRise 106.86 (V4-B4: 107.74), OtherDwelling 103.09 n=1 (V4-B4: 99.99), SingleD
  119.82 n=2 (V4-B4: 115.00). Confirms the parsing method before full deployment. Internal closure
  check (sum of 5 categories vs the table's own "Total End Uses" row, independently summed in the
  script) matched to 0.0 in all 6 — expected, since both numbers come from the same source rows, not
  an independent check.
- **Local, no cluster.** `tar czf t07_2022_eplustbl.tar.gz` of the 1200 canonical files (from
  `t07_manifest_2022.csv`), 156,682,002 bytes (vs ~2.1 GB uncompressed for 1200 × ~1.75 MB).
- `scp -r` to `/speed-scratch/o_iseri/2J_revision/T07/` (tar, manifest, `T07_scripts/`) — remote `ls -la`
  confirms byte-identical sizes for the tar (156682002) and manifest (115505).
- **Speed job 1328260** · `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 T07_scripts/run_eui_enduse.sh` ·
  submitted 2026-09-15. Wrapper script untars into `T07/campaign/`, runs `eui_enduse_by_run.py`
  against the 1200-file manifest, writes `T07/out/per_run_enduse_2022.csv` and
  `T07/out/eui_gap_by_enduse_2022.csv`. Slurm log: `/speed-scratch/o_iseri/2J_revision/T07/slurm_1328260.out`.
- **Collected 2026-09-15.** `sacct -j 1328260` → `COMPLETED`, exit `0:0`, elapsed `00:00:38`, 4 CPUs
  (all three sub-steps: job/batch/extern). `cat` of the slurm log on the login node:
  `n_ok=1200 n_fail=0` / `wrote .../out/per_run_enduse_2022.csv` / `wrote .../out/eui_gap_by_enduse_2022.csv`
  / `DONE` — **all 1,200 of 1,200 manifest runs parsed, zero skipped, zero failed.** 38 s for 1,200
  files (4 CPUs, ~300 files/CPU) is consistent with a single-pass regex/text-table parse of an
  already-local ~1.75 MB `eplustbl.csv` per run — no external I/O beyond the untar, no per-run process
  spawn.
- `scp -o BatchMode=yes -o ConnectTimeout=60` of `out/eui_gap_by_enduse_2022.csv`, `out/per_run_enduse_2022.csv`,
  `slurm_1328260.out` from `/speed-scratch/o_iseri/2J_revision/T07/` to local `T07_out/` — one attempt,
  no retry needed. Local file sizes match the remote `ls -la` exactly: 1784, 183425, 173 bytes.

## Verified

- `3J_docs_occ_nTemp/improvements/v4/V4-B4_RESULTS.md` and `V4-B4_PREREGISTRATION.md`: the defective
  function is `calculate_eui()` in
  `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/plotting.py:293-299,319,343-345` (queries
  `TabularDataWithStrings` for `'End Uses By Subcategory'` with no report-name pin — the
  peak-demand-table copy gets summed in — and the water guard only matches `'m3'`, missing IP `'gal'`
  runs). Corrected 2022 pooled EUI (`V4-B4_RESULTS.md:108-111`, §4.1): SingleDetached 115.00,
  OtherDwelling 99.99, MidRise 107.74, HighRise 78.21 kWh/m². **V4-B4 saved only totals** (verified
  via an independent `elec_facility_kWh` meter-sum cross-check, `V4-B4_RESULTS.md` §1.3) — **no
  per-run end-use file was written to disk by V4-B4.**
- `outputs_step8/agg/agg_enduse_annual.csv` (60,469 bytes, 601 rows incl. header) exists but is
  insufficient for this task: columns are only `heating_gas_GJ, heating_elec_GJ, heating_district_GJ,
  cooling_elec_GJ, cooling_gas_GJ, cooling_district_GJ` — no water heating, appliances or lighting —
  and it covers only `campaign_subset_v3_enduse` (600 runs, 2022, CZ 6A/6B/7A only), built by
  `outputs_step8/investigation/extract_enduse_annual_from_tbl.py`, not the corrected full campaign.
- `outputs_step8/agg/agg_annual.csv` (6001 rows incl. header = 6000 runs, matches the published
  campaign) **has per-run columns** `lights_kWh, equip_kWh, fan_kWh, heating_ET_kWh, cooling_ET_kWh,
  water_ET_kWh` — but these are `*:EnergyTransfer` **meter** values (thermal load reaching the HVAC
  system), defined at `2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py:84-86,397-399`, a
  **different physical basis** than the site/fuel energy SHEU and Table 5 use. Locally aggregated the
  2022 rows (sum of the 6 columns ÷ summed conditioned floor area, by archetype): HighRise 73.7,
  MidRise 79.4 (⚠ `water_ET_kWh` is blank for all 300 MidRise 2022 rows — a separate, unexplained data
  gap), OtherDwelling 64.2, SingleD 85.6 kWh/m² — none reproduce V4-B4's corrected totals
  (78.21/107.74/99.99/115.00), confirming this file is on the wrong basis and not usable here.
- SHEU end-use split by dwelling type (space heating / water heating / appliances / lighting /
  cooling, as opposed to the total-only intensity Table 5 already uses): **NOT FOUND on disk.**
  Checked `writing/deepResearch/Canadian Residential Energy-Use Intensity by Dwelling Type (NRCan) —
  Plausibility Bands for Building-Energy Simulation.md` (has only SHEU-2019 Table 3.3b total-all-fuels
  and Table 3.6b electricity-only intensities per dwelling type, `:4-5,21-29` — no end-use split) and
  `writing/submission/tables/Table_05_eui_sheu.md` (same total-only figures). Per the task rule, not
  fetched from the web. Re-verified this turn (grep for `space heating|water heating|appliance|
  lighting|space cooling` in the deepResearch file returns nothing; `Table_05_eui_sheu.md` carries
  only SHEU national-central and regional-band totals, no per-end-use rows) — confirms the prior
  employee's NOT FOUND.
- **Closure test (job 1328260 output, `T07_out/eui_gap_by_enduse_2022.csv`, n=300/archetype, 1200/1200
  total).** Reconstructed 2022 totals (sum of 5 end uses) vs V4-B4's published corrected totals
  (`V4-B4_RESULTS.md:108-111`): HighRise 78.2111 vs 78.21 (Δ 0.0011), MidRise 107.7432 vs 107.74
  (Δ 0.0032), OtherDwelling 99.9857 vs 99.99 (Δ −0.0043), SingleD 114.9986 vs 115.00 (Δ −0.0014).
  **Measured gap: up to 0.0043 kWh/m² (OtherDwelling), exceeding the task's stated 0.0005 kWh/m²
  tolerance.** But all four reconstructed values round to their published counterpart at the 2-decimal
  precision V4-B4 itself published — the 0.0005 tolerance is tighter than V4-B4's own published
  precision allows to check against, so this is the measured gap, not a failed reconciliation; no
  independent higher-precision V4-B4 total exists on disk to test against instead. The in-script
  internal check (5-category sum vs the table's own "Total End Uses" row) also matched to 0.0/−0.0 in
  all four archetypes' `TOTAL_direct_sum_check` rows — as before, not an independent check, same source
  rows.
- **End-use breakdown, 2022, kWh/m² and share of archetype total** (`T07_out/eui_gap_by_enduse_2022.csv`):
  HighRise — appliances 31.90 (40.8%), space_heating 13.53 (17.3%), water_heating 13.29 (17.0%),
  lighting 13.16 (16.8%), space_cooling 6.34 (8.1%). MidRise — water_heating 43.53 (40.4%), appliances
  32.87 (30.5%), space_heating 12.59 (11.7%), lighting 11.66 (10.8%), space_cooling 7.10 (6.6%).
  OtherDwelling — appliances 54.59 (54.6%), space_heating 19.14 (19.1%), water_heating 13.69 (13.7%),
  lighting 7.17 (7.2%), space_cooling 5.41 (5.4%). SingleD — appliances 48.02 (41.8%), space_heating
  29.55 (25.7%), water_heating 24.44 (21.3%), lighting 6.58 (5.7%), space_cooling 6.41 (5.6%).
  **The task's stated expectation (space heating carries the gap) does not hold as "largest end use":
  appliances is largest in 3 of 4 archetypes, water heating in MidRise; space heating is largest in
  none.** SHEU columns are all `NOT FOUND` (see above), so no per-end-use gap vs SHEU could be computed
  — only the simulated split is reported.

## Decisions

- Recomputed the end-use split myself (no adequate file existed) from `eplustbl.csv`'s "End Uses"
  table with the V4-B4-style fix, per task step 1's instruction for this case.
- Chose **position-based** water-column exclusion (always the last of 14 data columns) instead of
  string-matching units — this is unit-system agnostic by construction, so it fixes V4-B4 defect 2
  for IP archetypes (`gal`) the same way it does for SI (`m3`), without needing a unit-string check.
- "Appliances" bucket = everything besides Heating/Cooling/Water Systems/Lighting (i.e. includes fans,
  pumps, heat rejection, etc.) because the SHEU end-use split itself is NOT FOUND on disk to check
  against a finer definition — flagged, not asserted as SHEU's own definition.
- Used `agg_annual.csv`'s `sim_hh_id` (already V4-B4-validated as matching the published 6000 runs) to
  pick the canonical file out of the duplicate `sample_NNN_HH<id>` directories left by the 2026-07-11
  resim, rather than guessing from directory mtimes.
- Followed Plan §10 rule 1 literally (submit via Speed `sbatch`) even though the raw `eplustbl.csv`
  files are already present on this machine and the parse itself is fast locally — per the task doc's
  explicit step 3 instruction, and for consistency with T01–T06.

## Next
Task closed. `T07_out/eui_gap_by_enduse_2022.csv` (final, from job 1328260) and
`T07_out/per_run_enduse_2022.csv` (1200 runs) are installed next to this doc, with `slurm_1328260.out`
alongside. Nothing further owed unless the author wants the SHEU end-use split supplied (currently
NOT FOUND on disk) or wants the tolerance re-stated/relaxed given V4-B4 only published 2 decimals.

**Manager note (2026-09-15, after collection).**
1. The "space heating is largest nowhere" reading does not test the task's expectation. The expectation
   was about which end use carries the **gap to SHEU**, not which end use is largest in the simulation.
   That question stays open until the SHEU end-use split exists; do not quote the share ranking as a
   rebuttal of it.
2. Simulated space heating is 12.6 to 29.5 kWh/m² (all fuels, End Uses table) across the four
   archetypes, pooled over six cities. That is small for Canadian homes and is the first place WP7
   must look once SHEU is supplied. Recorded as a check, not a finding.
3. The in-CSV `TOTAL_direct_sum_check` gap of 0.0 is a sum compared with itself; it is not a closure
   test. The only closure evidence is the 2-decimal round-match to V4-B4 in Verified.
4. SHEU end-use split per dwelling type: author supplies it (external, never fetched by an agent).
   T10 CSV repair verified by manager: 59 rows load; 5 recomputed matches, 3 recomputed mismatches.

## WHAT I DID NOT VERIFY

- Whether the full 1200-run archetype totals match V4-B4's corrected totals within the task's stated
  0.0005 kWh/m² tolerance — they do **not**; measured gap up to 0.0043 kWh/m² (OtherDwelling), though
  all four round-match V4-B4's own published 2-decimal figures (see Verified). Did not attempt to
  locate a higher-precision V4-B4 total to test against a tighter basis.
- Did not re-derive `eui_enduse_by_run.py`'s per-run parsing logic myself (e.g. did not open the
  script or re-parse a raw `eplustbl.csv` independently this turn) — relied on (a) the prior
  employee's 6-file dry-run cross-check already in the Ledger and (b) this turn's own check that the
  full 1200-run reconstructed totals round-match V4-B4's published totals, as corroborating but not
  independent evidence the parser is correct end-to-end.
- Could not find `T07_scripts/` or `t07_manifest_2022.csv` on this local machine when starting this
  turn (only the task doc and no output dirs existed under `impl/`) — the remote `ls -la` on Speed
  confirms `T07_scripts/`, the tar, and the manifest are present there with the byte sizes the prior
  Ledger entries reported, and the job ran successfully against them, so the artifacts existed as
  claimed; only their local copies are unaccounted for. Not investigated further (not blocking; did
  not need local script access to collect and check job 1328260's output).
- Whether "appliances" as bucketed (everything but heating/cooling/water/lighting) is the grouping a
  reviewer or SHEU comparison would expect — cannot check without the SHEU end-use split, which is
  NOT FOUND on disk (re-confirmed this turn).
- The MidRise `water_ET_kWh` gap in `agg_annual.csv` (300/300 rows blank) remains not root-caused;
  does not affect this task's chosen path.
