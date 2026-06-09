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

**Stage 4 — Warmup retry + aggregate: PENDING** (awaiting array completion)

---

### Stage 2 — Aggregate + validate (PENDING)

After array (+ optional retry) is done:
- Re-run `08_simulation_val.md` validation gates on `SimResults_Step8_corrected/`
- Compare corrected vs pre-bug: annual EUI expected ~same; peak-hour timing should shift
  by +4 h relative to old results
- Update SI figures / tables referencing peak timing

---

## Open items

- [ ] Smoke gate: relayed and verified
- [ ] Full array submitted
- [ ] Warmup retry (if needed)
- [ ] Stage 2 aggregate + validation
