#!/encs/bin/bash
#SBATCH --job-name=s9_warmup60
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_warmup60_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_warmup60_%j.err

# Warmup-60 recovery: re-run warmup-convergence Severe failures with
# Maximum Number of Warmup Days raised from 25 to 60.
# MidRise Calgary HH78358/2022 is EXCLUDED (HVAC blow-up), NOT included here.
# Authorized by STEP 1/2 of 2026-06-06 manager closeout task.
# Final list: 1 MidRise Toronto + 4 HighRise Toronto + 3 HighRise Vancouver + 1 HighRise Winnipeg = 9 total.
# MidRise Calgary (HVAC blow-up, 53k+ warnings) is EXCLUDED separately.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

ROOT=/speed-scratch/o_iseri/step9_run
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
SEXEC="singularity exec --bind /speed-scratch $SIF"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EXTRACT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/cluster_spike/extract_meters.py
EPW_TORONTO=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw
EPW_VANCOUVER=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_BC_Vancouver.Harbour.CS.712010_TMYx_5C.epw
EPW_WINNIPEG=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw

echo "=== Step 9 warmup-60 recovery | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

recover_run() {
    local IDF_PATH=$1
    local EPW_PATH=$2
    local OUT_DIR
    OUT_DIR=$(dirname "$IDF_PATH")
    local LABEL
    LABEL=$(echo "$OUT_DIR" | awk -F/ '{print $(NF-3)"/"$(NF-2)"/"$(NF-1)"/"$NF}')
    local IDF_NAME
    IDF_NAME=$(basename "$IDF_PATH")

    echo ""
    echo "=== RECOVER: $LABEL ==="

    # Archive original IDF before patching
    if [ ! -f "$OUT_DIR/${IDF_NAME}.bak_warmup60" ]; then
        cp "$IDF_PATH" "$OUT_DIR/${IDF_NAME}.bak_warmup60"
        echo "  Archived: ${IDF_NAME}.bak_warmup60"
    else
        echo "  Archive already exists, skipping cp"
    fi

    # Patch: Maximum Number of Warmup Days 25 -> 60 (do not touch tolerances)
    sed -i 's/25,.*!- Maximum Number of Warmup Days/60,                       !- Maximum Number of Warmup Days/' "$IDF_PATH"
    echo "  Patched: Maximum Number of Warmup Days 25->60"

    # Remove previous run's .end so the post-run check reflects this run only
    rm -f "$OUT_DIR/eplusout.end" "$OUT_DIR/hourly_meters.csv"

    # Stage IDF
    cp "$IDF_PATH" "$OUT_DIR/in.idf"
    $SEXEC cat ${EP_BIN}/Energy+.idd > "$OUT_DIR/Energy+.idd"

    cd "$OUT_DIR"
    $SEXEC "${EP_BIN}/ExpandObjects"
    if [ -f "$OUT_DIR/expanded.idf" ]; then IDF_RUN="$OUT_DIR/expanded.idf"
    else IDF_RUN="$OUT_DIR/in.idf"; fi

    $SEXEC "${EP_BIN}/energyplus" -d "$OUT_DIR" -w "$EPW_PATH" "$IDF_RUN"
    EP_RC=$?
    if [ $EP_RC -ne 0 ]; then echo "  E+ FAIL (exit $EP_RC): $LABEL"; return 1; fi
    if [ ! -f "$OUT_DIR/eplusout.end" ]; then echo "  FAIL (no .end): $LABEL"; return 1; fi

    SEVERE=$(grep -c "\*\* Severe" "$OUT_DIR/eplusout.err" 2>/dev/null || echo 0)
    echo "  Severe count after warmup-60 patch: $SEVERE"
    if [ "$SEVERE" -gt 0 ]; then echo "  FAIL ($SEVERE Severe remaining): $LABEL"; return 1; fi

    $PYTHON "$EXTRACT" "$OUT_DIR/eplusout.sql" "$OUT_DIR/hourly_meters.csv"
    if [ $? -ne 0 ]; then echo "  FAIL (extract): $LABEL"; return 1; fi

    echo "  DONE: $LABEL"
    return 0
}

DONE=0
FAIL=0

# 1. MidRise Toronto HH1865/2030 activity — manager-ruled RECOVER
recover_run "$ROOT/idfs/MidRise__Toronto_5A/activity/sample_003_HH1865/2030/Scenario_2030.idf" "$EPW_TORONTO"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# 2-5. HighRise Toronto — STEP 1->STEP 2 rule: warmup Severe -> RECOVER
recover_run "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_012_HH32974/2022/Scenario_2022.idf" "$EPW_TORONTO"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

recover_run "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_012_HH32974/2030/Scenario_2030.idf" "$EPW_TORONTO"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

recover_run "$ROOT/idfs/HighRise__Toronto_5A/activity/sample_017_HH90265/2030/Scenario_2030.idf" "$EPW_TORONTO"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

recover_run "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_026_HH47072/2030/Scenario_2030.idf" "$EPW_TORONTO"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# 6. HighRise Vancouver HH79793/2022 baseline — warmup Severe confirmed
recover_run "$ROOT/idfs/HighRise__Vancouver_5C/baseline/sample_005_HH79793/2022/Scenario_2022.idf" "$EPW_VANCOUVER"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# 7. HighRise Vancouver HH75563/2022 activity — warmup Severe confirmed
recover_run "$ROOT/idfs/HighRise__Vancouver_5C/activity/sample_012_HH75563/2022/Scenario_2022.idf" "$EPW_VANCOUVER"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# 8. HighRise Vancouver HH104153/2022 activity — warmup Severe confirmed
recover_run "$ROOT/idfs/HighRise__Vancouver_5C/activity/sample_032_HH104153/2022/Scenario_2022.idf" "$EPW_VANCOUVER"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# 9. HighRise Winnipeg HH44464/2030 baseline — warmup Severe confirmed
recover_run "$ROOT/idfs/HighRise__Winnipeg_7A/baseline/sample_013_HH44464/2030/Scenario_2030.idf" "$EPW_WINNIPEG"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

echo ""
echo "=== Warmup-60 recovery complete: succeeded=$DONE  failed=$FAIL ==="
echo "Date: $(date)"
