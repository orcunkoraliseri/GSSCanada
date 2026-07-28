# Employee handoff — 3J Leg-3 Step 8 · PROBES P1–P4 (build + submit)

**You are the employee.** Execute the task below and append a Progress Log entry on completion.
Manager-authored 2026-07-28. Scope: build the probe harness, submit it, nothing else.

---

## 0. Non-negotiable environment rules

- 🔴 **`sbatch` only.** NEVER a blocking/interactive `srun`. NEVER any `python` — not even a
  one-liner — on the login node (`speed-submit2`). Account-suspension risk, flagged 3×.
  Allowed over ssh: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
- 🔴 **Every submission gets `-t 7-00:00:00`.** No exceptions, however short the job.
- Login shell is **tcsh**: no `2>/dev/null`, no `2>&1` (→ "Ambiguous output redirect"). Inside
  `.sh` wrappers it's bash, so bash syntax is fine there.
- Cluster commands: **one physical line, `cd`-first, paths double-quoted.**
- Wrapper scripts **never in `/tmp`** (noexec on compute nodes) — they live in the upload tree.
- Do **not** modify: `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`,
  `eSim_dynamicML_mHead_alignment.py`.
- Do **not** loosen a gate threshold to erase a FAIL. Relabel + document with evidence instead.

## 1. Aim

Build and run the four §P pre-campaign probes that gate the 56-run Step-8 campaign
(definitions: `3rdJ_08_simulation_4split_val.md` §P, L8–15):

| Probe | Requirement | Verdict rule |
|---|---|---|
| P1 | Scenario-differentiation per channel: probe pairs differ in that channel's hourly series (max abs delta > 0) | FAIL = campaign blocked |
| P2 | Byte-identity tripwire: no two *different* scenarios produce byte-identical output | FAIL |
| P3 | Stale-output guard: injector-hash output dirs work; header-only/partial `hourly_meters.csv` detected | FAIL |
| P4 | Fall-back loudness: a deliberately-missing channel product logs the baseline reversion in the manifest | FAIL |

**Scope boundary — residential is OUT.** The residential channel has no specified rule for
collapsing the per-household Step-7 product (`BEM_Schedules_4split_2022.csv`, keyed `SIM_HH_ID`)
into one deterministic tower run; this is an open manager/user decision. Residential Spaces
therefore stay at NECB baseline in every probe cell. Report P1's residential leg as
**NOT EXERCISED — blocked upstream**, never as PASS and never as FAIL. Do not invent a
collapse rule. Do not inject residential.

## 2. Known-good context (verified 2026-07-28, do not re-derive)

- **IDF stock** (v24.2, reuse, do not re-transition):
  `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/`
  - `CAN_MTL/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` (7 721 326 B) ← **probe building**
  - `CAN_MTL/TallBuilding_..._Z6_v242.idf` (5 142 928 B)
  - `CAN_CLG/…_Z7A_v242.idf` (SuperTall 7 721 362 B / Tall 5 142 964 B)
  The `6A_Buffalo` token is an upstream prototype artifact; the operative climate marker is the
  `Z6`/`Z7A` suffix.
- **This IDF *is* the mixed tower** (ARCH B, blocker lifted 2026-07-24): all four channels are
  native `Space` objects carrying `Tag_2`. Tall census = residential 30 / office 33 / retail 9 /
  hotel 25 / service_MEP 63 = 164 Spaces; SuperTall = 256. Ignore any docstring in
  `commercial_integration.py` claiming no mixed-use prototype exists — that text is stale, the
  census measured otherwise.
- **EPW:** `/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`
- **EnergyPlus:** SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`, exe inside at
  `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus`.
  Wrapper pattern (Leg-2 `run_residential_array.sh:37-44`, proven):
  ```bash
  singularity exec --bind /speed-scratch --bind /nfs/speed-scratch <SIF> <exe-in-sif> "$@"
  ```
  Both binds are mandatory — python resolves the `/nfs` symlink (Cycle-7 lesson).
- **IDD:** `/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd` (export as `EPLUS_IDD`).
- **Python:** `/speed-scratch/o_iseri/envs/step4/bin/python` (3.10; has eppy — proven by AUDIT-W).
- **Injector:** `eSim_bem_utils/commercial_integration.py`, md5 `5670f6026a91577126cd1329f60acb1a`.
  `inject_mixed_use(idf_path, output_path, channels, building_meta, verbose=True) -> dict`.
  `channels` values are **CSV paths + channel keys**, e.g.
  `{"office": {"csv": …, "archetype": "Office_Knowledge", "band": "hybrid"},
    "retail": {"csv": …, "pr": "QC"}, "hotel": {"csv": …, "pr": "QC"}}`.
  A missing channel key or missing CSV → that channel reverts to NECB baseline (W5 fall-back).
- **Step-7 products** on the cluster under
  `/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/`
  — currently **only the 2022 set is uploaded**. The 2030 sets exist locally and must be
  uploaded by you (§4). Office bands: the 2022 file carries `BAND=observed` **only**; the 2030
  file carries `conservative` / `hybrid` / `fullyhybrid`. Do not pass `band="hybrid"` against
  the 2022 CSV — it will not match.
- Reference for structure/style: `3rdJ_08W_audit_wiring.py` + `.sh` (same folder). Reuse its
  path constants and its `report(status, gate, detail)` scorecard idiom verbatim.

## 3. Deliverables (write these, locally, in `3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/`)

### 3.1 `3rdJ_08P_probe_driver.py` — runs ONE probe cell

CLI: `--cell <int>` (index into the cell table below) and `--force-inj-hash <hex>` (optional,
P3 only). Behaviour, in order:

1. **Injector fingerprint.** `INJ_HASH = md5(commercial_integration.py).hexdigest()[:8]`.
   Output root = `/speed-scratch/o_iseri/step8_4split/probes/campaign_<INJ_HASH>/<cell_tag>/`.
   This is the §6 structural stale-output guard: a wiring change changes the hash, which
   invalidates every completion check automatically. Never hard-code the hash.
2. **Inject.** Build the cell's `channels` dict, call `inject_mixed_use()` into
   `<outdir>/injected.idf`. Capture the returned result dict.
3. **Ensure outputs** (do this on the injected IDF, every path, no exceptions — the Leg-2
   office SQL-gap lesson):
   - `Output:SQLite` = `SimpleAndTabular` (add if absent).
   - Hourly `Output:Meter` covering **everything electric and gas**, explicitly including
     `WaterSystems:Electricity` (2J Bug B: 100 %-electric DHW was ~80 % of MidRise electricity
     and invisible to post-processing; hotel guest rooms are DHW-heavy so it matters doubly):
     `Electricity:Facility`, `Gas:Facility`, `InteriorLights:Electricity`,
     `InteriorEquipment:Electricity`, `InteriorEquipment:Gas`, `Fans:Electricity`,
     `Pumps:Electricity`, `Cooling:Electricity`, `Heating:Electricity`, `Heating:Gas`,
     `WaterSystems:Electricity`, `WaterSystems:Gas`.
   - Hourly `Output:Variable` with key `*` for: `Zone People Occupant Count`,
     `Zone Lights Electricity Energy`, `Zone Electric Equipment Electricity Energy`.
     These are the per-channel evidence that modulation reached the engine.
   - `RunPeriod` = full year, `Timestep` left as-is.
4. **Simulate.** Write the singularity wrapper into `<outdir>/epwrap/energyplus` (chmod +x),
   then `subprocess.run([wrapper, '-w', EPW, '-d', <outdir>/run, injected_idf])`.
   **No `capture_output=True`** — let EP's stdout/stderr land in the SLURM log (diagnostic mode).
   Record the return code.
5. **Post-process** `<outdir>/run/eplusout.sql` → two CSVs in `<outdir>`:
   - `hourly_meters.csv` — one column per requested meter, 8 760 rows. Query the SQL
     `ReportData`/`ReportDataDictionary` tables (Leg-2 equivalent:
     `eSim_bem_utils_3J/plotting.py::get_hourly_meter_data`, port or reimplement — your choice,
     but state which in the Progress Log).
   - `channel_hourly.csv` — the three zone variables aggregated **per channel**. Map each zone
     to a channel with `classify_tag2()` from `commercial_integration.py`, exactly as the
     AUDIT-W script does; emit columns `<channel>_people`, `<channel>_lights`, `<channel>_equip`
     for channels `office`, `retail`, `hotel`, `residential`, `service_MEP`. 8 760 rows.
6. **Manifest.** `<outdir>/manifest.json`, containing at minimum: cell index + tag, scenario
   label, per-channel `{csv_path, csv_md5, exists}`, the `inject_mixed_use()` result dict
   (including `fallback` and `ambiguous`), `INJ_HASH`, injected-IDF md5, EP return code,
   row counts of both CSVs, and their md5s. **If any channel fell back to baseline, the manifest
   must carry an explicit top-level `"FALLBACK_LOUD": ["<channel>", …]` key and the driver must
   print a banner line `!!! FALLBACK: <channel> reverted to NECB baseline !!!` to stdout.**
   That banner + key is exactly what P4 tests.
7. Exit non-zero on EP failure or on a CSV with ≠ 8 760 rows.

### 3.2 Probe cell table (SuperTall, MTL Z6, per §7 "one building")

| # | tag | office | retail | hotel |
|---|---|---|---|---|
| 0 | `baseline_necb` | — (absent) | — | — |
| 1 | `B_central` | 2030 / `hybrid` | 2030_central | 2030_central |
| 2 | `var_office` | 2030 / `fullyhybrid` | 2030_central | 2030_central |
| 3 | `var_retail` | 2030 / `hybrid` | 2030_opt | 2030_central |
| 4 | `var_hotel` | 2030 / `hybrid` | 2030_central | 2030_opt |
| 5 | `cycle_2022` | 2022 / `observed` | 2022 | 2022 |
| 6 | `fallback_retail` | 2030 / `hybrid` | **path to a nonexistent file** | 2030_central |

Cells 1–4 are the one-at-a-time design P1 asks for (each varies exactly one channel off
B-central). Cell 0 is the un-injected reference. Cell 6 exists only to trip P4.

### 3.3 `3rdJ_08P_probes.sh` — SLURM array launcher

`#SBATCH --array=0-6`, `-p ps`, `--cpus-per-task=4`, `--mem=16G`, **`-t 7-00:00:00`**,
`--output=/speed-scratch/o_iseri/step8_4split/logs/8P_probe_%A_%a.out`.
Exports `EPLUS_IDD` and `PYTHONPATH=/speed-scratch/o_iseri/step8_4split/upload`, `cd`s to the
Step8_docs dir in the upload tree, runs `python -u 3rdJ_08P_probe_driver.py --cell $SLURM_ARRAY_TASK_ID`,
echoes the exit code. (`-u` so partial output survives a kill.) Add a defensive
`python -c "import eppy, pandas, numpy"` precheck line **inside the wrapper** so a missing
dependency surfaces in the job log immediately, not 40 minutes in.

### 3.4 `3rdJ_08P_probe_gates.py` — the scorecard (run AFTER the array lands)

Reads every `campaign_*/…/manifest.json` + the two CSVs and emits a PASS/WARN/FAIL line per gate
using the AUDIT-W `report()` idiom, then a scorecard, then `sys.exit(1)` iff any FAIL.

- **P1** — for each of office / retail / hotel: `max|Δ|` of that channel's `*_people`,
  `*_lights`, `*_equip` columns between its one-at-a-time cell and cell 1 (`B_central`), and
  between cell 1 and cell 0. Require **> 0** on at least the `people` column of the varied
  channel. Report the actual max|Δ| per comparison — a number, not just a verdict.
  Also emit `INFO` lines for the *unvaried* channels in each pair (they should be ~0; a large
  delta there means cross-channel leakage and is worth seeing).
  Residential → `report("INFO", "P1 residential", "NOT EXERCISED — collapse rule unspecified")`.
- **P2** — md5 every cell's `hourly_meters.csv`; any two cells among 0–5 sharing an md5 = FAIL,
  naming the pair. (Cell 6 excluded: it is a deliberate near-duplicate of cell 1 minus retail.)
- **P3** — two parts: (a) assert every output path contains `campaign_<INJ_HASH>` with the hash
  matching a freshly computed md5 of the injector on disk; (b) assert both CSVs in every cell
  have exactly 8 760 data rows and an mtime newer than the injected IDF. Completeness =
  row count **AND** mtime freshness, together (§6b.5).
- **P4** — cell 6's manifest must contain `"FALLBACK_LOUD": ["retail"]` and its SLURM log must
  contain the `!!! FALLBACK` banner; additionally cell 6's retail columns in
  `channel_hourly.csv` must be **identical** to cell 0's retail columns (proof it truly reverted
  to baseline rather than silently keeping the previous scenario).

## 4. Execution sequence

1. Write the three files locally. **Compile-check each**: `py -3 -m py_compile <file>` in
   PowerShell (plain `python` fails under Git Bash — Windows Store alias).
2. Upload: the three new files, the 2030 Step-7 products (office/retail/hotel), and re-verify the
   already-uploaded injector. Then **md5-verify at both ends** and write the comparison table
   into the Progress Log **before** submitting (§6b.1 — in Leg-2 this exact check caught an
   absent launcher and a stale injector, either of which would have poisoned the campaign).
   *Verify the artifact, not the assumption that it's there.*
3. Submit `3rdJ_08P_probes.sh`. Capture the job ID and confirm with `squeue -u o_iseri` —
   never claim a job is running without verifying.
4. **Stop there and report.** Do not run the gate script yet, do not poll in a loop. The array
   is 7 annual SuperTall simulations; check back at **≥30 min** spacing.
5. When the array lands, submit `3rdJ_08P_probe_gates.py` (also via `sbatch`, also 7-day
   walltime) and report the scorecard.
6. **P3 part (a) needs a second submission**: after the array completes, append one comment line
   to `commercial_integration.py`, re-upload, and rerun **cell 1 only** — the output must land
   in a *new* `campaign_<new-hash>/` dir. Do this only after step 5's scorecard is in hand.

## 5. Deliverable back to the manager

- The md5 both-ends table (§4.2).
- Job IDs.
- The P1–P4 scorecard with **numbers** (max|Δ| per channel, md5 pairs, row counts), not just
  verdicts.
- A Progress Log entry appended to `3rdJ_08_simulation_4split.md` under a dated heading.
- Any gate that FAILs: report it as FAIL with evidence. Do not tune a threshold to make it pass.

**Out of scope, do not start:** the 56-run campaign, sub-step 8A (historical 2005/2010/2015
products), the 6 one-at-a-time sensitivity product sets, `3rdJ_08_simulation_4split_agg.py`,
and anything touching the residential injector.
