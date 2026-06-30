#!/bin/bash
# 3rdJ_08C0_idf_transition.sh — Sub-step 8C.0: Office IDF v22.1 → v24.2 transition
#
# Transitions the 4 PNNL Tall/SuperTall office IDFs from EnergyPlus v22.1 to v24.2
# using the EnergyPlus IDFVersionUpdater transition chain inside the v24.2 SIF.
# The v22.1 IDFs have field-schema changes in HeatExchanger:AirToAir:SensibleAndLatent
# and Coil:Cooling:DX:SingleSpeed that cause fatal errors under v24.2.
#
# Transition chain: 22.1 → 22.2 → 23.1 → 23.2 → 24.1 → 24.2
# All utilities are present inside the SIF at /EnergyPlus/PreProcess/IDFVersionUpdater/
#
# Output: $SCRATCH/step8_2split/office_idfs_v242/{CAN_CLG,CAN_MTL}/*.idf
# Then scp back to local outputs_step8/office_idfs_v242/ before 8C runs.
#
# SLURM: 4 IDFs in one job (each transition takes < 5 min; 4 serial is fine).
# User: submit with  sbatch 3rdJ_08C0_idf_transition.sh

#SBATCH --job-name=3J_8C0_transition
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8C0_transition_%j.out

SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
SCRATCH=/speed-scratch/o_iseri/step8_2split
SRC_BASE=/speed-scratch/o_iseri/step8_2split/upload

# Fix 2: write to the mirrored tree path that office_runner.py reads from
STEP8_DOCS=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs
OUT_CLG=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_CLG
OUT_MTL=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_MTL

mkdir -p "$OUT_CLG" "$OUT_MTL" "$SCRATCH/logs"

echo "=== 8C.0: Office IDF v22.1 -> v24.2 transition ==="
date

# The EnergyPlus SIF contains the IDFVersionUpdater at:
#   /EnergyPlus/PreProcess/IDFVersionUpdater/
# The updater binary for each step is named:
#   Transition-V22-1-0-to-V22-2-0, Transition-V22-2-0-to-V23-1-0, etc.
# The auto-transition launcher is: /EnergyPlus/PreProcess/IDFVersionUpdater/Transition
# (which chains all steps from the source version to the target automatically).

# Helper: run transition chain on one IDF
transition_idf() {
    local SRC="$1"
    local OUTDIR="$2"
    local BASENAME=$(basename "$SRC")
    local STEM="${BASENAME%_v221.idf}"
    local TMP="$OUTDIR/tmp_${STEM}"
    mkdir -p "$TMP"
    cp "$SRC" "$TMP/${BASENAME}"

    echo "  Transitioning $BASENAME ..."
    # E+ 24.2 includes an auto-chain launcher. Use it:
    singularity exec \
        --bind "$TMP:$TMP" \
        "$SIF" \
        bash -c "cd '$TMP' && /EnergyPlus/PreProcess/IDFVersionUpdater/Transition '$BASENAME'"

    # After transition the file is renamed to the current version in-place.
    # Find the resulting IDF (will no longer be named _v221):
    RESULT=$(ls "$TMP"/*.idf 2>/dev/null | grep -v "NotConverted" | head -n1)
    if [ -z "$RESULT" ]; then
        echo "  ERROR: transition produced no IDF for $BASENAME"
        return 1
    fi

    # Rename to _v242 and copy out
    OUT_NAME="${STEM}_v242.idf"
    cp "$RESULT" "$OUTDIR/$OUT_NAME"
    echo "  -> $OUT_NAME"
    rm -rf "$TMP"
}

# 4 office IDFs
transition_idf "$SRC_BASE/BEM_Setup/Buildings/CAN_CLG/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf"      "$OUT_CLG"
transition_idf "$SRC_BASE/BEM_Setup/Buildings/CAN_CLG/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf" "$OUT_CLG"
transition_idf "$SRC_BASE/BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf"       "$OUT_MTL"
transition_idf "$SRC_BASE/BEM_Setup/Buildings/CAN_MTL/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf"  "$OUT_MTL"

echo ""
echo "=== Done. v24.2 IDFs at: ==="
ls -lh "$OUT_CLG"/*.idf 2>/dev/null
ls -lh "$OUT_MTL"/*.idf 2>/dev/null
date
