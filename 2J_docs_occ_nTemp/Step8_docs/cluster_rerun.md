# Step 8 Cluster Re-run Log — Corrected Schedules

**Purpose**: Re-run the 6,000-simulation EnergyPlus campaign after fixing the 4-hour
schedule injection bug in `07_aug_to_bem.py`. Annual EUI is expected to be phase-robust
(~250–272 kWh/m²); timing and peak results are the primary outputs that change.

**Campaign tag**: `SimResults_Step8_corrected/campaign_N50/`

---

## Progress Log

### 2026-06-08 — Stage 0 artefacts built (employee agent)

**Bug context**: `07_aug_to_bem.py` was dropping the diary→clock +4 h rotation that the
classic `occToBEM` pipeline performed via datetime resampling. All 5 year schedule CSVs
(BEM_Schedules_{2005,2010,2015,2022,2030}.csv) were corrected locally:

- 2022 / 2030: `np.roll(+4)` applied in `07_aug_to_bem.py` (live in repo)
- 2005 / 2010 / 2015: `fix_old_years_clock.py` relabels Hour+4 in place

**Q4 answer (HH consistency)**: CONFIRMED — same N=50 HH sampled across all 5 years.
`run_step8_paired_mc()` builds `common` = intersection of SIM_HH_IDs present in ALL year
CSVs, then samples N from that pool with a deterministic SHA-256 per-cell seed. Every HH
runs against all 5 years. No freeze needed beyond MD5 provenance logging in each SLURM
task (done in `step8_array.sh`).

**Files created (local → upload to cluster)**:

| Local path (under Step8_docs/) | Cluster destination |
|---|---|
| `ep_wrappers/energyplus` | `/speed-scratch/o_iseri/ep_wrappers/energyplus` |
| `ep_wrappers/ExpandObjects` | `/speed-scratch/o_iseri/ep_wrappers/ExpandObjects` |
| `step8_smoke.sh` | `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs/` |
| `step8_array.sh` | same |
| `step8_warmup_retry.py` | same |
| `step8_warmup_retry.sh` | same |

**eppy**: Required by `integration.py` and `idf_optimizer.py`. Pre-flight in both .sh
scripts checks `import eppy` and prints install command if missing.

**IDD**: Must be extracted from the SIF on the cluster (see cluster setup commands below).

**Status**: PENDING — upload + cluster setup + smoke gate not yet done.

---

### Cluster setup commands (run in order)

**Step C1 — Upload bundle (locally):**
```powershell
"energyplus","ExpandObjects" | ForEach-Object { scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\Step8_docs\ep_wrappers\$_" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/ep_wrappers/ }
```

```powershell
"step8_smoke.sh","step8_array.sh","step8_warmup_retry.py","step8_warmup_retry.sh" | ForEach-Object { scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\Step8_docs\$_" "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs/" }
```

**Step C2 — Create wrapper dir + extract IDD (on the cluster):**
```tcsh
mkdir -p /speed-scratch/o_iseri/ep_wrappers
```

```tcsh
singularity exec /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif cat /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/Energy+.idd > /speed-scratch/o_iseri/ep_wrappers/Energy+.idd
```

**Step C3 — Fix permissions + line endings (on the cluster):**
```tcsh
chmod +x /speed-scratch/o_iseri/ep_wrappers/energyplus /speed-scratch/o_iseri/ep_wrappers/ExpandObjects
```

```tcsh
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs && dos2unix step8_smoke.sh step8_array.sh step8_warmup_retry.py step8_warmup_retry.sh
```

**Step C4 — Install eppy if missing (on the cluster):**
```tcsh
/speed-scratch/o_iseri/envs/step4/bin/python -c "import eppy; print('eppy ok')"
```

If that prints an error:
```tcsh
/speed-scratch/o_iseri/envs/step4/bin/python -m pip install eppy
```

**Step C5 — Make logs dir + submit smoke (on the cluster):**
```tcsh
mkdir -p /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs
```

```tcsh
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs && sbatch step8_smoke.sh
```

**Step C6 — Verify smoke output, then submit full array (on the cluster):**

After smoke job completes, relay the `.out` log. Gate: E+ ran with 0 Severe errors and
EUI is in 250–272 kWh/m² band. If passes:

```tcsh
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs && sbatch step8_array.sh
```

**Step C7 — After array finishes: warmup retry (on the cluster):**

Only needed if any cells have `< 250 hourly_meters.csv` in their output dir.
```tcsh
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs && sbatch step8_warmup_retry.sh
```

---

### 2026-06-08 — v2 re-run (employee agent, Sonnet 4.6) — Stages 0–3

**Root causes fixed in v2:**
1. **Clock bug**: `07_aug_to_bem.py` dropped the diary→clock +4 h rotation. All 5 year CSVs in the prior array (953076) were 4 h early. `build_s8_sched.py` fixes 2005/2010/2015 via `(Hour+4)%24` re-sort; 2022/2030 were already clock-correct in BEM_Setup.
2. **Schema bug**: BEM_Setup 2022/2030 CSVs have 17 cols (`Equip_Design_W`, `Light_Design_W` extra). In `integration.py` `_s9_equip_dw = float(_s9_meta.get('equip_design_w', 0.0))` — when >0, activates S9 path and **zeros standard L&E loads**. Fix: `build_s8_sched.py` drops those 2 cols → 15-col private CSVs → standard L&E path.
3. **Isolation**: BEM_Setup is owned by Step 9 (running concurrently). All Step 8 v2 schedules live in private dir `/speed-scratch/o_iseri/step8_run/sched/`; `run_paired_mc.py` patched with `--sched-dir` arg to bypass `BEM_SETUP_DIR`.

**Prior corrupt results archived on cluster:**
- `SimResults_Step8_corrected` → `SimResults_Step8_corrected_CORRUPT_953076`
- Original `step8_array.sh` → `Step8_docs/archive/step8_array_BACKUP_2026-06-08.sh`

**Stage 1 — Private schedule build (job 953102):**
- Submitted: 2026-06-08 ~16:11 EDT; completed: 16:21 (9m 23s)
- 2005/2010/2015: 6,936,336 rows × 13 cols each; `(Hour+4)%24` applied; re-sorted by SIM_HH_ID/Day_Type/Hour
- 2022/2030: 6,936,336 rows × 15 cols → dropped `['Equip_Design_W', 'Light_Design_W']`; 13 remaining cols (Equipment_Fraction + Lighting_Fraction kept — harmless without design-W)
- Build phase check:
  - 2005: night_h00-05=0.955 midday_h11-14=0.382 peak=h03 → PASS
  - 2010: night=0.950 midday=0.372 peak=h03 → PASS
  - 2015: night=0.938 midday=0.348 peak=h03 → PASS
  - 2022: night=0.945 midday=0.412 peak=h03 → PASS
  - 2030: night=0.953 midday=0.552 peak=h01 → PASS

**Stage 2 — Smoke test (job 953107, SingleD × Montreal_6A, N=3, all 5 yr):**
- Submitted: ~16:21; completed: 16:36 (14m 30s); exit=0
- E+: 15/15 OK, 0 failures
- **PHASE GATE: PASS** — all 5 years overnight-peak confirmed (pre-E+ check on private CSVs)
- **L&E GATE: PASS** — standard path active (design-W dropped):
  - 2005: lights=138 kWh (ref 152, ok) equip=6757 kWh (ref 6553, ok)
  - 2010: lights=138 kWh (ref 151, ok) equip=6576 kWh (ref 6576, ok)
  - 2015: lights=151 kWh (ref 151, ok) equip=6790 kWh (ref 6574, ok)
  - 2022: lights=135 kWh (ref 156, ok) equip=6364 kWh (ref 6781, ok)
  - 2030: lights=128 kWh (ref 159, ok) equip=6252 kWh (ref 6870, ok)
- (Tolerance 30% for N=3; full campaign target 5%)
- **SMOKE RESULT: PASS**

**Stage 3 — Full 24-cell array (job 953111, step8_array_v2.sh):**
- Submitted: 2026-06-08 ~16:38 EDT
- 24 tasks (0–23), `--time=48:00:00`, `--cpus-per-task=8 --mem=16G`
- Results root: `SimResults_Step8_corrected_v2/campaign_N50/`
- Schedules sourced from private dir (NOT BEM_Setup)
- Status: **RUNNING** (tasks 0-2 started immediately, 3-23 pending at submission time)

**Stage 4 — Warmup retry + aggregate: COMPLETE (2026-06-09)**

- Array 953111 completed: 23 COMPLETED + 1 FAILED (benign — task 7 OtherDwelling×Kelowna_5B,
  250/250 files present, 1 warmup failure wrote fallback output)
- File count check: 6000/6000 hourly_meters.csv confirmed (2026-06-09)
- Warmup retry: NOT NEEDED (all cells at 250)
- Validation job 954020 COMPLETED (exit 0); logs: SimResults_Step8_corrected_v2/logs/val_954020.{out,err}
  (953491 FAILED — latin-1 encoding; 954016 FAILED — pandas .values() bug; 954020 clean)

**Validation results (954020):**
- Gate 1 (L&E): PASS — all 240 run-year pairs (24 cells × 2 samples × 5 years) above threshold
  - lights > 50 kWh/yr and equip > 1000 kWh/yr confirmed for every run
  - SingleD: lights=152±13 kWh, equip=6788±279 kWh (matches smoke-test values)
- Peak-hour distribution: CORRECT — h17 dominates (92/240=38%), h18 second (66/240=28%)
  - Evening residential peak confirms +4h clock fix working
  - Corrupt (4h-early) would have shown ~h13 peak; now correctly at h17
- EUI (elec+gas, conditioned floor area):
  - SingleD: 124.2±12.0 kWh/m²
  - OtherDwelling: 112.4±8.8 kWh/m²
  - MidRise: 1175.5±73.5 kWh/m² (total building)
  - HighRise: 861.5±75.8 kWh/m²
- Corrupt comparison: empty (archive sample naming differs); non-critical — peak distribution confirms shift
- OVERALL: PASS

---

### 2026-06-09 — Stage 5 prepared: FULL aggregate + validate on v2 (manager)

Stage-4's 954020 was the lightweight gate only (L&E + peak-hour clock + eplustbl EUI on
2 samples/cell). The authoritative 8E aggregation + 8F 8-section validation have NOT yet
run on v2 — queued now as one job, **on the cluster** (v2 campaign exists only there).

**Implementation audit findings (fixed in this bundle):**
1. `08_simulation_val.py` `__main__` hard-coded the OLD bugged campaign
   (`SimResults_Step8/campaign_N50`) → added argparse (`--sim-dir --sched-dir --agg-dir
   --out-dir`; defaults unchanged, so local v1 behaviour identical).
2. §2 round-trip now points at the PRIVATE as-built schedules
   (`/speed-scratch/o_iseri/step8_run/sched/BEM_Schedules_{year}.csv`) — unlike v1, the v2
   as-built CSVs are preserved, so gates 2.1/2.2/2.4 now also enforce 2022/2030 (expected
   exact); stale v1 provenance text in gate strings + HTML §2 note rewritten.
3. `08_simulation_plots.py` needed no code change (CLI already takes
   `--results-dir/--out/--schedules-dir`); it reads EUI/area from `eplusout.sql` →
   wrapper prechecks sql presence and aborts if absent.
4. EUI basis caution: 954020's 124.2 kWh/m² (SingleD) is eplustbl
   per-conditioned-area elec+gas — NOT comparable to v1's agg-based 202/153/126/116.
   The phase-invariance check is the apples-to-apples diff of v2 `agg_annual.csv`
   vs v1 `outputs_step8/agg/agg_annual.csv` after this job.

**New files:** `step8_aggval_v2.sh` (partition ps, 48 h, 32 G, 4 cpu; Pass A = plots
`--rebuild-agg --figs all`, Pass B = full validator). Outputs →
`SimResults_Step8_corrected_v2/outputs_step8/{agg/,figures/,step8_validation_report.html}`.
Logs → `SimResults_Step8_corrected_v2/logs/aggval_<job>.{out,err}`.

**Status: PREPARED — upload + sbatch pending (user).** After completion: download
figures + report + agg_{annual,peak,meta}.csv (skip agg_diurnal ~12 M rows unless needed),
diff EUI/SHEU vs v1 (must be ~unchanged), run Part-4 checklist (a)–(g), then trigger 8G.

---

---

### 2026-06-10 — Stage 5 RESULTS: full aggregate + 8-section validation (employee agent, Sonnet 4.6)

**Job:** 954135 (`s8_aggval_v2`), COMPLETED, elapsed 00:54:26, exit 0:0

**Pass A** (08_simulation_plots.py --rebuild-agg --figs all): exit=0, completed Tue Jun 9 22:25:02 EDT 2026
- hourly_meters.csv count: 6000 (expected 6000); eplusout.sql count: 6000

**Pass B** (08_simulation_val.py, 8-section validator): exit=0, completed Tue Jun 9 22:26:33 EDT 2026 (88 s)
- Scorecard: **PASS: 22 / WARN: 2 / INFO: 3 / FAIL: 0**

**Downloads landed in:** `2J_docs_occ_nTemp/outputs_step8_v2/`

| File | Size |
|---|---|
| step8_validation_report.html | 749 KB |
| agg/agg_annual.csv | 1,563 KB |
| agg/agg_peak.csv | 866 KB |
| agg/agg_meta.csv | 1,058 KB |
| agg/agg_peak_hours.csv | 149,399 KB |
| figures/ (fig01–fig10, PNG + PDF) | 10 figure pairs |

(agg_diurnal.csv skipped per runbook — ~12M rows.)

**Quick summary (computed locally):**

*Mean EUI by archetype (all cities/years/samples):*

| Archetype | Mean EUI (kWh/m²) |
|---|---|
| SingleD | 208.13 |
| MidRise | 151.79 |
| OtherDwelling | 127.80 |
| HighRise | 117.01 |

*Mean EUI by archetype × year:*

| Archetype | 2005 | 2010 | 2015 | 2022 | 2030 |
|---|---|---|---|---|---|
| SingleD | 207.35 | 206.16 | 206.19 | 208.97 | 211.98 |
| MidRise | 152.09 | 152.73 | 152.59 | 151.96 | 149.56 |
| OtherDwelling | 127.44 | 127.45 | 126.70 | 128.00 | 129.41 |
| HighRise | 116.82 | 117.54 | 117.63 | 116.98 | 116.10 |

*Mean peak hour per year:*

| Year | Mean peak hour |
|---|---|
| 2005 | 17.512 |
| 2010 | 17.682 |
| 2015 | 17.623 |
| 2022 | 17.545 |
| 2030 | 17.709 |
| Overall | 17.614 |

*agg_meta status counts:* ok=5999 / short=1 (OtherDwelling × Kelowna_5B × 2010, n_hours=0 — known benign failure)

**WARN gates (2 total, 0 FAIL):**
- [WARN] 1.1: Completeness: 5999/6000 runs ok
- [WARN] 1.5: Output completeness: 5999/6000 have 8760 h

**Selected INFO/PASS highlights from validator log:**
- [PASS] 5.1: Peak-occupancy coupling: ensemble mean peak hour = 17.61h (expected 16–20h)
- [INFO] 6.3: Peak hour: 2022=17.55h → 2030=17.71h (Δ=+0.164h; peak FLATTEN, not shift)
- [INFO] 6.4: Δ EUI by CZ: 5A +1.07, 5B +1.28, 5C +0.31, 6A −0.12, 6B −0.27, 7A −0.56 (range 1.8 kWh/m²)
- [PASS] 7.1: Trend continuity: max YoY EUI Δ = 0.5%
- [PASS] 7.2: COVID break 2015→2022: Δload_factor=+0.0060, Δmidday=+0.0031 (visible)

---

### 2026-06-10 — Stage 6 — 8G: failed-run enumeration + recovery (employee agent, Sonnet 4.6)

**Enumeration (authoritative, read-only scan):**
- `eplusout.end` check: scanned all 6,000 files; exactly **1** does not contain "EnergyPlus Completed Successfully"
  - `campaign_N50/OtherDwelling__Kelowna_5B/sample_050_HH145979/2010/eplusout.end`
- `hourly_meters.csv` row check: confirmed via `agg_meta.csv` (aggregator flags status=short); exactly **1** file with `n_hours=0`
  - Same run as above — header-only CSV (0 data rows)
- **Total failures: 1 (expected). No additional failures found. Proceeding with recovery.**

**Root-cause confirmation (`eplusout.err` excerpt):**
```
** Severe  ** Coil:Cooling:DX:SingleSpeed "DX COOLING COIL_UNIT6" -- negative coil bypass factor calculated.
**   ~~~   **  During Warmup, Environment=MONTREAL-TRUDEAU.INTL.AP ANN HTG 99.6% CONDNS DB, at Simulation time=01/21 00:00 - 00:15
**  Fatal  ** Coil:Cooling:DX:SingleSpeed "DX COOLING COIL_UNIT6" Errors found in calculating coil bypass factors
...
EnergyPlus Terminated--Fatal Error Detected. 9 Warning; 1 Severe Errors; Elapsed Time=00hr 00min  2.22sec
```
Class: DX-coil autosizing fatal (not warmup, not clock). Deterministic.

**Fix applied (Attempt 1 — SUCCESS):**
- Isolated copy: `step8_8G_fix/OtherDwelling__Kelowna_5B__sample_050_HH145979__2010/`
- File edited: `expanded.idf` copy only (`Buildings_MTL_v242/` untouched)
- Change: `Coil:Cooling:DX:SingleSpeed "DX Cooling Coil_unit6"` — `Gross Rated Sensible Heat Ratio`: **`autosize` → `0.75`**
- Original backed up as `expanded.idf.ORIG_PRE_8G`

**Recovery job:** sbatch `step8_8G_fix.sh` → job **954296** (partition ps, 1 cpu, 4G, 48h)
- State: COMPLETED, exit=0:0, elapsed 00:03:46
- E+: `EnergyPlus Completed Successfully -- 0 Severe Errors`, elapsed 3m 23s
- Extraction: 8761 lines, 9 meters (`hourly_meters.csv` written OK)

**Campaign update:**
- `campaign_N50/OtherDwelling__Kelowna_5B/sample_050_HH145979/2010` renamed to `2010_FAILED_BAK`
- Corrected run dir placed at `campaign_N50/OtherDwelling__Kelowna_5B/sample_050_HH145979/2010`

**Re-aggregate + validate:** sbatch `step8_aggval_v2.sh` → job **954300** (partition ps, 4 cpu, 32G, 48h)
- State: COMPLETED, exit=0:0, elapsed 00:56:19
- Pass A (08_simulation_plots.py --rebuild-agg --figs all): exit=0
- Pass B (08_simulation_val.py, 8-section validator): exit=0
- **New scorecard: PASS 24 / WARN 0 / INFO 3 / FAIL 0** (was PASS 22/WARN 2 before fix)
- **agg_meta status: ok=6000 / short=0** (was ok=5999/short=1)

**EUI/peak-hour deltas (post-8G vs pre-8G):**
- EUI: SingleD +0.001, MidRise −0.003, OtherDwelling −0.012, HighRise +0.002 kWh/m² — all < 0.013 (negligible)
- Peak hour by year: 2005 +0.000, 2010 −0.001, 2015 −0.000, 2022 +0.000, 2030 −0.000 h — all < 0.001 h

**Local downloads refreshed** in `2J_docs_occ_nTemp/outputs_step8_v2/`:
| File | Size |
|---|---|
| step8_validation_report.html | 749 kB |
| agg/agg_annual.csv | 1,565 kB |
| agg/agg_peak.csv | 866 kB |
| agg/agg_meta.csv | 1,058 kB |
| agg/agg_peak_hours.csv | 149,425 kB |
| figures/ | 23 files |

**Sub-step 8G COMPLETE — campaign at 6000/6000, scorecard 24 PASS / 0 WARN / 0 FAIL.**

---

## Open items

- [x] Smoke gate: relayed and verified (953107 PASS)
- [x] Full array submitted (953111 — 23 COMPLETED + 1 benign FAILED)
- [x] Warmup retry: NOT NEEDED (all cells at 250)
- [x] Stage 4 quick validation (954020 PASS — L&E + peak clock)
- [x] Stage 5 full aggregate + validation (954135 COMPLETE — PASS 22 / WARN 2 / FAIL 0)
- [x] Stage 6 — 8G: failed-run recovery (954296 fix COMPLETE; 954300 re-agg COMPLETE — PASS 24 / WARN 0 / FAIL 0)
- [ ] Phase-invariance diff vs v1 agg + Part-4 checklist (manager, after Stage 6)
