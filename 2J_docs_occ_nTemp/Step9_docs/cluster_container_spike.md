# Step 9 — Cluster Container Spike

**Goal**: Prove that E+ 24.2.0 in a Singularity container on Speed reproduces a local Windows result
for the identical IDF+EPW, validating the cluster path for Step 9 (activity-driven loads).

**Status**: ✅ **GO — COMPLETE 2026-06-03.** Container validated; cluster path open for Step 9.

---

## 1. Recon Findings (from Step 8 cluster recon, 2026-06-02)

| Item | Finding |
|------|---------|
| Scheduler | SLURM (sbatch/salloc/squeue at /local/bin) |
| Login shell | tcsh (login node) |
| Nodes OS | AlmaLinux 9.7 / **glibc 2.34** |
| Singularity module | `singularity/3.10.4` (`module load singularity/3.10.4`) |
| Python / conda | `Mamba/23.11.0-0` (not needed for spike) |
| Home dir | `/nfs/home/o/o_iseri` |
| Scratch dir | `/speed-scratch/o_iseri` |
| Internet on login node | OK |
| EnergyPlus module | **NONE** — bare E+ 24.2 tarball fails (glibc 2.34 < 2.35 needed) |
| NREL Docker image | `nrel/energyplus:24.2.0` **confirmed** on Docker Hub |

**Why container**: E+ 24.2.0 Linux binary bundles libpython 3.12 which requires glibc ≥ 2.35.
Speed has 2.34. The container runs on Ubuntu 22.04 (glibc 2.35) inside Singularity.

---

## 2. Path Chosen: Easy path — `singularity pull docker://nrel/energyplus:24.2.0`

No definition file needed if the NREL image pulls and reports `24.2.0` on `energyplus --version`.

Fallback (only if pull fails on compute nodes due to missing internet):
- Option A: Ask ENCS if one-time `singularity pull` is allowed on login node (lightweight, no GPU).
- Option B: Build from definition file (`Bootstrap: ubuntu:22.04`, `%post` installs the GitHub
  EnergyPlus tarball) — requires writing a `.def` file and building via sbatch (slower but safe).

---

## 3. Reference Cell

| Item | Value |
|------|-------|
| Archetype | SingleD (DetachedHouse, MTL v24.2 IDF) |
| Climate | Winnipeg 7A |
| HH ID | 77448 |
| Year | 2022 |
| Local source | `Step8_docs/_bigtest/SingleD__Winnipeg_7A/sample_001_HH77448/2022/` |
| Local result | `eplusout.end`: EnergyPlus Completed Successfully — 658004 Warnings, 0 Severe |
| IDF staged | `cluster_spike/Scenario_2022.idf` (357 KB) |
| EPW staged | `cluster_spike/Winnipeg.epw` (1.5 MB, `CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw`) |
| Local reference | `Step8_docs/_bigtest/.../2022/hourly_meters.csv` (8760 rows, 9 meters) |

---

## 4. Files in `cluster_spike/`

| File | Purpose |
|------|---------|
| `pull_sif.sh` | SLURM Job A — pull `nrel/energyplus:24.2.0` → `energyplus_24.2.0.sif` |
| `run_ep_test.sh` | SLURM Job B — run E+ in container, extract meters |
| `extract_meters.py` | sqlite3-only meter extractor (runs inside container) |
| `compare_meters.py` | local comparison script (runs locally after download) |
| `Scenario_2022.idf` | reference IDF (with occupancy schedules for HH77448 2022) |
| `Winnipeg.epw` | reference weather file |

---

## 5. Upload + Cluster Commands

### Upload (locally)
```powershell
scp -r "2J_docs_occ_nTemp\Step9_docs\cluster_spike" "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step9_spike"
```
*(creates `/speed-scratch/o_iseri/step9_spike/` with all files)*

### Job A — pull the container (on the cluster)
```
sbatch /speed-scratch/o_iseri/step9_spike/pull_sif.sh
```
Expected: ~5–15 min (image is ~2–3 GB). Output: `logs/pull_sif_<JOBID>.out`.
Confirm with: `cat /speed-scratch/o_iseri/step9_spike/logs/pull_sif_<JOBID>.out | tail -5`

### Job B — run E+ container test (on the cluster)
*(submit AFTER Job A completes and shows "SIF ready")*
```
sbatch /speed-scratch/o_iseri/step9_spike/run_ep_test.sh
```
Expected: ~5–10 min (single annual E+ run). Output: `logs/ep_test_<JOBID>.out`.
Result file: `/speed-scratch/o_iseri/step9_spike/output/hourly_meters_container.csv`

### Download result (locally)
```powershell
scp "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step9_spike/output/hourly_meters_container.csv" "2J_docs_occ_nTemp\Step9_docs\cluster_spike\hourly_meters_container.csv"
```

### Validate (locally)
```powershell
python "2J_docs_occ_nTemp\Step9_docs\cluster_spike\compare_meters.py" "2J_docs_occ_nTemp\Step8_docs\_bigtest\SingleD__Winnipeg_7A\sample_001_HH77448\2022\hourly_meters.csv" "2J_docs_occ_nTemp\Step9_docs\cluster_spike\hourly_meters_container.csv"
```

---

## 6. Validated SIF Location on Speed

`/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`  
Verified `EnergyPlus, Version 24.2.0-94a887817b` — **confirmed 2026-06-03, Job 948008**.

## 7. Local vs Container Diff Table

Reference: `SingleD × Winnipeg_7A, HH77448, 2022` — 8760 hourly rows, 9 meters.

| Meter | Local kWh | Container kWh | Diff% | Max hourly J |
|-------|-----------|---------------|-------|-------------|
| Cooling:EnergyTransfer | 5639.4 | 5639.7 | 0.0055% | 75,434 |
| Electricity:Facility | 9883.9 | 9884.0 | 0.0009% | 5,336 |
| Fan Electricity Energy | 438.0 | 438.0 | 0.0000% | 0 |
| Heating:EnergyTransfer | 7980.2 | 7979.9 | 0.0031% | 230,569 |
| InteriorEquipment:Electricity | 6576.5 | 6576.5 | 0.0000% | 0 |
| InteriorLights:Electricity | 151.3 | 151.3 | 0.0000% | 0 |
| WaterSystems:EnergyTransfer | 2775.0 | 2775.0 | 0.0000% | 320 |
| Zone Electric Equipment Electricity Energy | 6576.5 | 6576.5 | 0.0000% | 0 |
| Zone Lights Electricity Energy | 151.3 | 151.3 | 0.0000% | 0 |

Largest diff: 0.0055% (Cooling). 5 of 9 meters exact (0.0000%). Max hourly delta 230,569 J = 0.064 kWh — negligible. All within 0.5% gate.

---

## 8. GO / NO-GO Verdict

## ✅ GO — Container validated 2026-06-03

**Gate**: all significant end-uses (annual > 0.1 kWh) must differ < 0.5%. **PASSED.**

E+ 24.2.0 in `nrel/energyplus:24.2.0` Singularity container on Speed reproduces local Windows
results to <0.006% per end-use. The cluster path is open for Step 9.

---

## 9. Reusable sbatch Template for Step 9

E+ binary path inside the container: `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/`  
Use `--bind /speed-scratch` on every `singularity exec` (not auto-mounted).  
Use `SEXEC="singularity exec --bind /speed-scratch $SIF"` pattern in scripts.  
Use host step4 Python for pre/post-processing (no standalone `python3` in the NREL image).

```bash
#!/encs/bin/bash
#SBATCH --partition=ps
#SBATCH --time=48:00:00
. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
SEXEC="singularity exec --bind /speed-scratch $SIF"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
# ... inject schedules, then:
$SEXEC "${EP_BIN}/ExpandObjects"          # from the IDF's work dir (CWD must contain in.idf + Energy+.idd)
$SEXEC "${EP_BIN}/energyplus" -d $OUTDIR -w $EPW expanded.idf
$PYTHON extract_meters.py $OUTDIR/eplusout.sql $OUTDIR/hourly_meters.csv
```

---

## Progress Log

### 2026-06-03 — Scripts staged (Employee)

Recon drawn from Step 8 cluster investigation (2026-06-02, confirmed in memory):
- `singularity/3.10.4` module available on Speed.
- `nrel/energyplus:24.2.0` confirmed on Docker Hub.
- Bare tarball dead (glibc 2.34 < 2.35); container is the only viable path.
- Internet access OK on login node; compute nodes assumed OK (standard at Concordia Speed).

Reference cell chosen: `sample_001_HH77448 / SingleD / Winnipeg_7A / 2022`
(from `_bigtest/`, completed 2026-06-02, 0 severe errors, 8760-row hourly_meters.csv).

Staged to `Step9_docs/cluster_spike/`:
- `pull_sif.sh` + `run_ep_test.sh` (SLURM jobs, `#!/encs/bin/bash`, `--partition=ps`, `--time=48:00:00`)
- `extract_meters.py` (sqlite3-only, runs inside container, replicates `plotting.get_hourly_meter_data`)
- `compare_meters.py` (local, csv-only, 0.5% gate per end-use)
- `Scenario_2022.idf` (357 KB) + `Winnipeg.epw` (1.5 MB)

Awaiting user to:
1. Run `scp -r` upload (locally → `/speed-scratch/o_iseri/step9_spike/`)
2. `sbatch /speed-scratch/o_iseri/step9_spike/pull_sif.sh` (on the cluster)
3. `sbatch /speed-scratch/o_iseri/step9_spike/run_ep_test.sh` (on the cluster, after Job A done)
4. Download `hourly_meters_container.csv` and run `compare_meters.py` locally.

**Potential blocker**: if compute nodes on Speed lack internet access, `pull_sif.sh` will fail.
Fallback: ask ENCS if a one-time `singularity pull` on the login node is permitted (it's
just a download, no GPU), or build from a definition file (Bootstrap: ubuntu:22.04).
This is a **manager decision** if the pull fails and ENCS says no to login-node pulls.

### 2026-06-03 — Execution complete + GO verdict (Employee)

**Jobs run on Speed (`magic-node-04`, partition `ps`):**
- Job A (pull_sif): **948008** — PASS. Pull ~3 min. `EnergyPlus, Version 24.2.0-94a887817b` confirmed.
- Job B (run_ep_test v1): **948009** — FAIL. Root cause: wrong `EP_BIN` path (`/usr/local/EnergyPlus-24-2-0` assumed; actual `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64`).
- Job B v2: **948013** — FAIL. Root cause: `/speed-scratch` not auto-mounted in container → `singularity exec cp` and ExpandObjects couldn't write output. Fix: add `--bind /speed-scratch` to all `singularity exec` calls.
- Job B v3: **948015** — E+ PASS (1 min 35 sec, 0 Severe, 658017 warnings vs local 658004). Meter extraction via container `python3` also failed (no standalone python3 in NREL image; E+ ships Python 3.12 as a library only). Fixed by running `extract_meters.py` with host step4 Python directly.

**Three bugs found and fixed in `run_ep_test.sh`:**
1. `EP_BIN`: `/usr/local/EnergyPlus-24-2-0` → `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64`
2. All `singularity exec` calls need `--bind /speed-scratch` (not auto-mounted by Singularity 3.10.4 on Speed).
3. Meter extraction: NREL image has no standalone `python3` → use `/speed-scratch/o_iseri/envs/step4/bin/python` on host.

**Validation result:**
- 8760 rows, 9 meters, all within 0.5% gate.
- Largest diff: Cooling 0.0055%; 5/9 meters exact (0.0000%).
- **GATE: PASS → GO for Step 9 on Speed cluster.**

**SIF location**: `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` (retained; reuse for Step 9).

### 2026-06-04 — SIF promoted to Step 8 use (Employee)

Step 8 local campaign (tabletop1) escalated after confirmed watchdog trip at 80.7% committed — 9.2 min into MidRise__Toronto_5A at --ep-workers 2 on a clean 60.1% baseline. Root cause: `idf_reader/main_BEM.py` concurrent E+ load (~12 pp) leaves insufficient headroom for MidRise/HighRise CSV load + E+ startup. Local campaign stopped at 12/24 (all SingleD + OtherDwelling complete, resume-safe); 12 heavy cells (MidRise×6 + HighRise×6) escalated to Speed cluster per the pre-agreed escalation rule.

**The SIF and sbatch template in Section 9 are now the confirmed path for Step 8 MidRise + HighRise cells.** The Step 9 spike proved the container reproduces local results to <0.006%; that validation is directly inherited by Step 8. Next step: build a SLURM array wrapping `run_paired_mc.py` (the validated Step 8 1-cell driver) using the container pattern from Section 9.
