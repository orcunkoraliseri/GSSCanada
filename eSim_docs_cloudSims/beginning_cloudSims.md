# Cloud Simulations on Speed HPC — Implementation Plan

## Aim

Migrate the EnergyPlus Monte Carlo neighbourhood simulations (Option 10 in `main.py`) from the local desktop to Concordia's **Speed HPC cluster** (SLURM), enabling N=20 production runs across all 6 neighbourhoods × 5 scenario years in a fraction of the time.

---

## Context

| Item | Detail |
|------|--------|
| Cluster | `speed.encs.concordia.ca` (SLURM) |
| Username | `o_iseri` |
| EnergyPlus version | 24.2.0 (must match local) |
| Neighbourhoods | NUS_RC1–RC6 (6 IDFs) |
| Scenarios per neighbourhood | 5 years (2005/2010/2015/2022/2025) + Default = 6 |
| MC iterations (production) | N=20 |
| Total sims (production) | 6 neighbourhoods × (1 Default + 20 × 5 years) = **606 EnergyPlus runs** |
| Partition | `ps` (CPU serial, 7-day max walltime) |
| Scratch | `/speed-scratch/o_iseri/` (90-day auto-cleanup) |

---

## Task List

### Task 1: Cluster Access & Environment Setup

**What:** Verify SSH access, set up working directories, install EnergyPlus 24.2, create Python venv.

**How:**

```bash
# 1a. Connect (from campus or VPN)
ssh o_iseri@speed.encs.concordia.ca

# 1b. Create project directories on scratch
mkdir -p /speed-scratch/o_iseri/GSSCanada
mkdir -p /speed-scratch/o_iseri/EnergyPlus

# 1c. Check available modules
module avail 2>&1 | grep -i energy

# 1d. If EnergyPlus not available as module, install locally:
#     Download Linux tar.gz from https://github.com/NREL/EnergyPlus/releases/tag/v24.2.0
#     (EnergyPlus-24.2.0-dcd...-Linux-Ubuntu22.04-x86_64.tar.gz)
cd /speed-scratch/o_iseri/EnergyPlus
wget <energyplus-24.2.0-linux-url>
tar xzf EnergyPlus-24.2.0-*.tar.gz
# Note the extracted directory path for ENERGYPLUS_DIR

# 1e. Python virtual environment
module load python/3.9   # or whatever is available; check with: module avail python
python3 -m venv /speed-scratch/o_iseri/GSSCanada/venv
source /speed-scratch/o_iseri/GSSCanada/venv/bin/activate
pip install pandas numpy scipy matplotlib seaborn tqdm eppy scikit-learn
```

**Expected result:** Can SSH in, EnergyPlus 24.2 binary runs on a compute node, Python env has all deps.

**Test method:** `energyplus --version` returns 24.2; `python -c "import eppy"` succeeds.

---

### Task 2: Transfer Project Files to Cluster

**What:** Upload the repo, IDF files, EPW files, and schedule CSVs.

**How:**

```bash
# From local Windows machine (Git Bash / PowerShell with rsync or scp):
# Option A: rsync (preferred, incremental)
rsync -avz --exclude='.git' --exclude='SimResults*' --exclude='__pycache__' \
  /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/ \
  o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/

# Option B: scp (simpler)
scp -r "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main" \
  o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/GSSCanada/
```

**Key files to verify on cluster:**
- `BEM_Setup/Neighbourhoods/NUS_RC*.idf` (6 files)
- `BEM_Setup/WeatherFile/*.epw`
- `BEM_Setup/BEM_Schedules_*.csv` (5 year files)
- `eSim_bem_utils/` (all Python modules)

**Test method:** `ls` the directories on the cluster; file counts match local.

---

### Task 3: Create the Headless Batch Runner Script (Python)

**What:** Write a non-interactive Python script (`run_batch_hpc.py`) that replaces the menu-driven Option 10 with command-line arguments, so SLURM can invoke it without user input.

**How:** Create `eSim_bem_utils/run_batch_hpc.py` that:

1. Accepts CLI args: `--idf`, `--epw`, `--region`, `--sim-mode`, `--iter-count`, `--output-dir`
2. Calls the same internal functions as Option 10 (`_run_mc_neighbourhood`, etc.)
3. Exits with code 0 on success, non-zero on failure
4. Writes results to the specified output directory

```python
# Skeleton:
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import neighbourhood, integration, simulation, plotting, config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--idf', required=True)
    parser.add_argument('--epw', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--sim-mode', default='weekly')
    parser.add_argument('--iter-count', type=int, default=20)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    # ... call _run_mc_neighbourhood logic ...

if __name__ == '__main__':
    main()
```

**Expected result:** Can run `python run_batch_hpc.py --idf ... --epw ... --region Quebec --iter-count 2 --output-dir /tmp/test` on the cluster without any interactive prompts.

**Test method:** Run with N=1 on a single IDF via `salloc` interactive session.

---

### Task 4: Create SLURM Job Scripts

**What:** Write SLURM submission scripts that run the batch across all neighbourhoods.

**How:** Two approaches (choose based on preference):

#### Option A: Job Array (one array task per neighbourhood)

```bash
#!/bin/bash
#SBATCH --job-name=eSim_MC
#SBATCH --account=speed1
#SBATCH -p ps
#SBATCH --mem=8G
#SBATCH -c 4
#SBATCH -t 1-00:00:00
#SBATCH --array=1-6
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/logs/eSim_%A_%a.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=orcunkoral.oseri@concordia.ca

# --- Setup ---
PROJECT=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24-2-0
VENV=/speed-scratch/o_iseri/GSSCanada/venv

source $VENV/bin/activate
export ENERGYPLUS_DIR=$EP_DIR

# --- Map array index to neighbourhood + EPW ---
# (Hardcoded mapping — 6 neighbourhoods × assigned EPW)
IDFS=(NUS_RC1 NUS_RC2 NUS_RC3 NUS_RC4 NUS_RC5 NUS_RC6)
# Adjust EPW assignments below to match your local setup:
EPWS=(CAN_QC_Montreal CAN_QC_Montreal CAN_QC_Montreal CAN_QC_Montreal CAN_QC_Montreal CAN_QC_Montreal)
REGIONS=(Quebec Quebec Quebec Quebec Quebec Quebec)

IDX=$((SLURM_ARRAY_TASK_ID - 1))
IDF_NAME=${IDFS[$IDX]}
EPW_PATTERN=${EPWS[$IDX]}
REGION=${REGIONS[$IDX]}

IDF_PATH=$PROJECT/BEM_Setup/Neighbourhoods/${IDF_NAME}.idf
EPW_PATH=$(ls $PROJECT/BEM_Setup/WeatherFile/*${EPW_PATTERN}*.epw | head -1)
OUTPUT_DIR=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20/${IDF_NAME}

mkdir -p $OUTPUT_DIR

# --- Run ---
cd $PROJECT
python eSim_bem_utils/run_batch_hpc.py \
    --idf "$IDF_PATH" \
    --epw "$EPW_PATH" \
    --region "$REGION" \
    --sim-mode weekly \
    --iter-count 20 \
    --output-dir "$OUTPUT_DIR"

echo "Done: $IDF_NAME (exit code: $?)"
```

#### Option B: One script per neighbourhood (simpler debugging)

Submit 6 separate scripts, each hardcoded to one IDF/EPW pair.

**Expected result:** `sbatch submit_array.sh` queues 6 jobs that each run N=20 MC for one neighbourhood.

**Test method:** Submit with `--iter-count 1` first; check logs and output directories.

---

### Task 5: Smoke Test — NUS_RC1 Option 7, N=2

**What:** Before the full N=20 batch, run a minimal end-to-end test using only NUS_RC1 with N=2 MC iterations via `run_batch_hpc.py`. This exercises the same `_run_mc_neighbourhood` path as Option 10 but limits cost to ~12 EnergyPlus runs (2 scenarios × 6 buildings × 1 iteration + Default).

**How:**

```bash
# Step 1: Request an interactive node
salloc -p ps --mem=8G -c 4 -t 120

# Step 2: Activate environment and set EnergyPlus path
bash
source /speed-scratch/o_iseri/GSSCanada/venv/bin/activate
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64

# Step 3: Run NUS_RC1 only, N=2
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main
python eSim_bem_utils/run_batch_hpc.py \
    --idf BEM_Setup/Neighbourhoods/NUS_RC1.idf \
    --region Quebec \
    --sim-mode weekly \
    --iter-count 2 \
    --output-dir /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1
```

**Expected result:**
- No Python import errors or EnergyPlus crashes
- Output directory populated: `NUS_RC1/Default/`, `NUS_RC1/2005/`, …`NUS_RC1/2025/`
- Each scenario folder contains `eplusout.sql` + EUI summary CSV
- No `FATAL` lines in EnergyPlus output

**Test method:**

```bash
# Check outputs exist
ls /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1/

# Quick sanity: any fatal errors?
grep -r "FATAL" /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1/ | head -20

# Confirm CSV present
find /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1/ -name "*.csv" | head -10
```

**Pass criteria:** All 6 scenario folders present, no FATAL errors, at least one CSV with EUI values.

**Only proceed to Task 6 if this passes.**

---

### Task 6: Production Run (N=20)

**What:** Submit the full production batch.

**How:**

```bash
# Create log directory
mkdir -p /speed-scratch/o_iseri/GSSCanada/logs

# Submit
sbatch submit_array.sh

# Monitor
squeue -u o_iseri
sacct -j <JOBID> --format=JobID,State,Elapsed,MaxRSS
```

**Expected result:** 6 jobs complete (one per neighbourhood), each producing N=20 MC results.

**Test method:** Check `batch_summary.csv` in each output dir; compare EUI ranges with local N=5 sanity run.

---

### Task 7: Retrieve Results

**What:** Download completed results back to local machine.

**How:**

```bash
# From local machine:
rsync -avz o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/GSSCanada/results/ \
  "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/SimResults/"
```

**Test method:** Open results locally; verify plots and CSVs are intact.

---

## Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-04-16 | Plan created | Done | All 8 tasks defined |
| 2026-04-16 | Task 1: Cluster setup | Done | EnergyPlus CentOS7 build + venv installed |
| 2026-04-16 | Task 2: File transfer | In progress | IDFs + eSim_bem_utils transferred; EPWs/CSVs to confirm |
| | Task 3: Headless runner | Pending | |
| | Task 4: SLURM scripts | Pending | |
| | Task 5: Smoke test NUS_RC1 N=2 | Pending | New — added 2026-04-16 |
| | Task 6: Production run (N=20) | Pending | Only after Task 5 passes |
| | Task 7: Retrieve results | Pending | |

---

## Key Notes

- **EnergyPlus is CPU-only** — use partition `ps`, not GPU partitions.
- **`weekly` sim mode recommended** for HPC — ~2.5x faster than full-year, validated locally.
- **`config.py` auto-detects Linux** and sets `ENERGYPLUS_DIR` to `/usr/local/EnergyPlus-24-2-0` — override via `ENERGYPLUS_DIR` env var in the SLURM script.
- **Scratch cleanup**: `/speed-scratch` files auto-deleted after 90 days of no access. Copy results back promptly.
- **Calcul Quebec fallback**: If Speed capacity is insufficient, the same SLURM scripts work on Calcul Quebec clusters (same scheduler). You'd just need to transfer files and adjust account/partition names.
- **Request shell change**: Speed defaults to `tcsh`. Request bash from Service Desk if needed, or add `#!/bin/bash` to all scripts (which SLURM respects regardless of login shell).
