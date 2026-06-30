#!/bin/bash
# 3rdJ_08C0_idf_transition.sh — Sub-step 8C.0: Office IDF v22.1 → v24.2 transition
#
# Transitions the 4 PNNL Tall/SuperTall office IDFs from EnergyPlus v22.1 to v24.2
# using the host-side IDFVersionUpdater Transition chain (NOT the SIF).
#
# The SIF's container root is /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/
# but that container does NOT include IDFVersionUpdater or the Transition binaries.
# The host-side ep_install DOES have the full chain:
#   /home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-.../PreProcess/IDFVersionUpdater/
#
# Transition chain applied: V22-1 → V22-2 → V23-1 → V23-2 → V24-1 → V24-2
# Each step overwrites the working IDF in place (saves .idfold backup).
# The Transition binaries look for their IDD files in their own directory (argv[0] dir).
#
# Output: mirrored tree outputs_step8/office_idfs_v242/{CAN_CLG,CAN_MTL}/*.idf
#
# SLURM: 4 IDFs in one job (each transition chain < 2 min; 4 serial is fine).

#SBATCH --job-name=3J_8C0_tr
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8C0_transition_%j.out

SRC_BASE=/speed-scratch/o_iseri/step8_2split/upload
SCRATCH=/speed-scratch/o_iseri/step8_2split

# Fix 2: write to the mirrored tree path that office_runner.py reads from
STEP8_DOCS=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs
OUT_CLG=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_CLG
OUT_MTL=$STEP8_DOCS/outputs_step8/office_idfs_v242/CAN_MTL

# Host-side IDFVersionUpdater (has full Transition chain + IDD files)
IDD_UPDATER=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/PreProcess/IDFVersionUpdater

mkdir -p "$OUT_CLG" "$OUT_MTL" "$SCRATCH/logs"

echo "=== 8C.0: Office IDF v22.1 -> v24.2 transition ==="
date
echo "  IDD_UPDATER: $IDD_UPDATER"

# Helper: run the full v22.1→v24.2 Transition chain on one IDF.
# The Transition binaries resolve their IDD files relative to argv[0] (their own dir).
# We create a temp dir, copy the IDF there as "working.idf", cd to the temp dir,
# then run each step. The binaries at $IDD_UPDATER find their IDDs in $IDD_UPDATER.
transition_idf() {
    local SRC="$1"
    local OUTDIR="$2"
    local BASENAME
    BASENAME=$(basename "$SRC")
    local STEM="${BASENAME%_v221.idf}"
    local TMP="$SCRATCH/tmp_transition_${STEM}_$$"
    mkdir -p "$TMP"
    cp "$SRC" "$TMP/working.idf"

    echo "  Transitioning $BASENAME ..."
    (
        cd "$TMP" || exit 1
        "$IDD_UPDATER/Transition-V22-1-0-to-V22-2-0" working.idf || { echo "  ERROR: V22-1->V22-2 failed"; exit 1; }
        "$IDD_UPDATER/Transition-V22-2-0-to-V23-1-0" working.idf || { echo "  ERROR: V22-2->V23-1 failed"; exit 1; }
        "$IDD_UPDATER/Transition-V23-1-0-to-V23-2-0" working.idf || { echo "  ERROR: V23-1->V23-2 failed"; exit 1; }
        "$IDD_UPDATER/Transition-V23-2-0-to-V24-1-0" working.idf || { echo "  ERROR: V23-2->V24-1 failed"; exit 1; }
        "$IDD_UPDATER/Transition-V24-1-0-to-V24-2-0" working.idf || { echo "  ERROR: V24-1->V24-2 failed"; exit 1; }
    ) || { echo "  ERROR: transition chain failed for $BASENAME"; rm -rf "$TMP"; return 1; }

    # Verify version string in output
    if ! grep -q "24\.2" "$TMP/working.idf"; then
        echo "  ERROR: output IDF does not contain version 24.2 — transition may have failed"
        rm -rf "$TMP"
        return 1
    fi

    OUT_NAME="${STEM}_v242.idf"
    cp "$TMP/working.idf" "$OUTDIR/$OUT_NAME"
    local VER
    VER=$(grep -m1 "Version Identifier" "$OUTDIR/$OUT_NAME" | tr -d ' ;' | sed 's/.*Identifier//')
    echo "  -> $OUT_NAME  (version: $VER)"
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
