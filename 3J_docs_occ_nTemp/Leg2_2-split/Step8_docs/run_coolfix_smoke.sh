#!/bin/bash
# run_coolfix_smoke.sh — Step 8 apartment cooling-setpoint fix: Phase-4 smoke test (3J Leg-2)
#
# 4 E+ runs (2 MidRise + 2 HighRise, Winnipeg_7A, scenario 2022) against the patched
# Buildings_MTL_v242_3Jfix IDFs, ahead of committing to the full 4,200-run subset re-sim.
# See investigation/step8_coolfix_implementation_plan.md Phase 4 /
# investigation/step8_coolfix_employee_prompt.md Phase 4.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_coolfix_smoke.sh
#       (returns job ID instantly; NEVER run from login node interactively)

#SBATCH --job-name=3J_coolfix_smoke
#SBATCH -p ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/coolfix_smoke_%j.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"

# Fix 5: dep precheck — fail fast if python env is missing a required package
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

# ---- E+ wrapper: Speed cluster is AlmaLinux 9; the Ubuntu-compiled host binary
# won't run. Route energyplus + ExpandObjects calls through the Singularity SIF
# via thin wrapper scripts. simulation.py finds executables + Energy+.idd via
# ENERGYPLUS_DIR, so we point that to a temp dir with the wrappers.
EPWRAP=/speed-scratch/o_iseri/step8_2split/epwrap_$$
mkdir -p "$EPWRAP"
cat > "$EPWRAP/energyplus" << 'WEOF'
#!/bin/bash
singularity exec --bind /speed-scratch --bind /nfs/speed-scratch /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus "$@"
WEOF
cat > "$EPWRAP/ExpandObjects" << 'WEOF'
#!/bin/bash
singularity exec --bind /speed-scratch --bind /nfs/speed-scratch /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/ExpandObjects "$@"
WEOF
chmod +x "$EPWRAP/energyplus" "$EPWRAP/ExpandObjects"
cp /home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd "$EPWRAP/"
export ENERGYPLUS_DIR="$EPWRAP"
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg
export ESIM_WORKERS=8

echo "=== 3J coolfix smoke test (MidRise + HighRise, Winnipeg_7A, 2022, n=2) ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  PY: $PY  SIF: $SIF"

# ---- run --------------------------------------------------------------
cd "$STEP8_DIR"
$PY 3rdJ_08B_run_paired_mc.py \
    --arch MidRise --city Winnipeg_7A --scenario 2022 \
    --n 2 --seed 42 --mode standard \
    --out-dir "$SCRATCH/campaign_smoke"

$PY 3rdJ_08B_run_paired_mc.py \
    --arch HighRise --city Winnipeg_7A --scenario 2022 \
    --n 2 --seed 42 --mode standard \
    --out-dir "$SCRATCH/campaign_smoke"

echo "  Smoke test done: $(date)"
rm -rf "$EPWRAP"
