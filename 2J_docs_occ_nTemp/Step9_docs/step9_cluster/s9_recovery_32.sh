#!/encs/bin/bash
#SBATCH --job-name=s9_recovery32
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_recovery32_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_recovery32_%j.err

# Recovery job: re-run all 32 IDFs missing hourly_meters.csv after the corrected array (952998).
# Task 47 (HighRise__Winnipeg_7A/activity) OOM'd (fork: Cannot allocate memory) — 15 miss.
# Other 17 are scattered straggler failures across 12 cells.
# Runs SEQUENTIALLY (not via joblib) to avoid memory accumulation.
# HighRise IDFs patched with warmup=120; MidRise run as-is.
# 2026-06-10: initial recovery after 952998_47 exit 126.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

ROOT=/speed-scratch/o_iseri/step9_run
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
SEXEC="singularity exec --bind /speed-scratch $SIF"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EXTRACT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/cluster_spike/extract_meters.py
WF=$GCMAIN/BEM_Setup/WeatherFile

EPW_KELOWNA=$WF/CAN_BC_Kelowna.Intl.AP.712030_TMYx_5B.epw
EPW_MONTREAL=$WF/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
EPW_TORONTO=$WF/CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw
EPW_VANCOUVER=$WF/CAN_BC_Vancouver.Harbour.CS.712010_TMYx_5C.epw
EPW_WINNIPEG=$WF/CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw

echo "=== Step 9 recovery-32 | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

recover_one() {
    local IDF_PATH=$1
    local EPW_PATH=$2
    local PATCH_WARMUP=$3   # "yes" for HighRise, "no" for MidRise
    local OUT_DIR
    OUT_DIR=$(dirname "$IDF_PATH")
    local IDF_NAME
    IDF_NAME=$(basename "$IDF_PATH")
    local LABEL
    LABEL=$(echo "$OUT_DIR" | awk -F/ '{print $(NF-3)"/"$(NF-2)"/"$(NF-1)"/"$NF}')

    echo ""
    echo "=== RECOVER: $LABEL ==="

    if [ ! -f "$IDF_PATH" ]; then
        echo "  ABORT: IDF not found at $IDF_PATH"
        return 1
    fi

    # Skip if already recovered
    if [ -f "$OUT_DIR/hourly_meters.csv" ]; then
        echo "  SKIP: hourly_meters.csv already present"
        return 0
    fi

    if [ "$PATCH_WARMUP" = "yes" ]; then
        # Backup original if not already done
        if [ ! -f "$OUT_DIR/${IDF_NAME}.bak_orig" ]; then
            cp "$IDF_PATH" "$OUT_DIR/${IDF_NAME}.bak_orig"
            echo "  Created .bak_orig backup"
        fi
        # Restore from backup (idempotent)
        cp "$OUT_DIR/${IDF_NAME}.bak_orig" "$IDF_PATH"
        # Patch warmup days 25 -> 120
        sed -i 's/25,.*!- Maximum Number of Warmup Days/120,                      !- Maximum Number of Warmup Days/' "$IDF_PATH"
        if ! grep -q "120,.*!- Maximum Number of Warmup Days" "$IDF_PATH"; then
            echo "  ABORT: warmup patch failed"
            return 1
        fi
        echo "  Patched: Maximum Number of Warmup Days 25->120"
    fi

    # Clear stale outputs
    rm -f "$OUT_DIR/eplusout.end" "$OUT_DIR/hourly_meters.csv"

    # Stage and run
    cp "$IDF_PATH" "$OUT_DIR/in.idf"
    $SEXEC cat ${EP_BIN}/Energy+.idd > "$OUT_DIR/Energy+.idd"

    cd "$OUT_DIR"
    $SEXEC "${EP_BIN}/ExpandObjects"
    if [ -f "$OUT_DIR/expanded.idf" ]; then IDF_RUN="$OUT_DIR/expanded.idf"
    else IDF_RUN="$OUT_DIR/in.idf"; fi

    $SEXEC "${EP_BIN}/energyplus" -d "$OUT_DIR" -w "$EPW_PATH" "$IDF_RUN"
    EP_RC=$?
    if [ $EP_RC -ne 0 ]; then echo "  FAIL E+(exit $EP_RC): $LABEL"; return 1; fi
    if [ ! -f "$OUT_DIR/eplusout.end" ]; then echo "  FAIL (no .end): $LABEL"; return 1; fi

    SEVERE=$(grep -c "\*\* Severe" "$OUT_DIR/eplusout.err" || echo 0)
    if [ "$SEVERE" -gt 0 ]; then echo "  FAIL ($SEVERE Severe): $LABEL"; return 1; fi

    $PYTHON "$EXTRACT" "$OUT_DIR/eplusout.sql" "$OUT_DIR/hourly_meters.csv"
    if [ $? -ne 0 ]; then echo "  FAIL (extract): $LABEL"; return 1; fi

    echo "  OK: $LABEL"
    return 0
}

DONE=0; FAIL=0

# --- HighRise__Kelowna_5B/activity (1) ---
recover_one "$ROOT/idfs/HighRise__Kelowna_5B/activity/sample_043_HH75840/2022/Scenario_2022.idf" "$EPW_KELOWNA" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Kelowna_5B/baseline (1) ---
recover_one "$ROOT/idfs/HighRise__Kelowna_5B/baseline/sample_006_HH119046/2030/Scenario_2030.idf" "$EPW_KELOWNA" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Montreal_6A/baseline (1) ---
recover_one "$ROOT/idfs/HighRise__Montreal_6A/baseline/sample_037_HH79579/2030/Scenario_2030.idf" "$EPW_MONTREAL" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Toronto_5A/activity (1) ---
recover_one "$ROOT/idfs/HighRise__Toronto_5A/activity/sample_019_HH56752/2022/Scenario_2022.idf" "$EPW_TORONTO" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Toronto_5A/baseline (3) ---
recover_one "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_017_HH90265/2022/Scenario_2022.idf" "$EPW_TORONTO" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_026_HH47072/2022/Scenario_2022.idf" "$EPW_TORONTO" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Toronto_5A/baseline/sample_040_HH7077/2022/Scenario_2022.idf" "$EPW_TORONTO" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Vancouver_5C/activity (2) ---
recover_one "$ROOT/idfs/HighRise__Vancouver_5C/activity/sample_032_HH104153/2022/Scenario_2022.idf" "$EPW_VANCOUVER" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Vancouver_5C/activity/sample_038_HH59576/2030/Scenario_2030.idf" "$EPW_VANCOUVER" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Vancouver_5C/baseline (3) ---
recover_one "$ROOT/idfs/HighRise__Vancouver_5C/baseline/sample_006_HH64721/2030/Scenario_2030.idf" "$EPW_VANCOUVER" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Vancouver_5C/baseline/sample_031_HH101651/2030/Scenario_2030.idf" "$EPW_VANCOUVER" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Vancouver_5C/baseline/sample_038_HH59576/2022/Scenario_2022.idf" "$EPW_VANCOUVER" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Winnipeg_7A/activity (15) ---
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_043_HH41235/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_044_HH123367/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_044_HH123367/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_045_HH114814/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_045_HH114814/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_046_HH30949/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_046_HH30949/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_047_HH115172/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_047_HH115172/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_048_HH44412/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_048_HH44412/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_049_HH8505/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_049_HH8505/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_050_HH69669/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_050_HH69669/2030/Scenario_2030.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- HighRise__Winnipeg_7A/baseline (1) ---
recover_one "$ROOT/idfs/HighRise__Winnipeg_7A/baseline/sample_050_HH69669/2022/Scenario_2022.idf" "$EPW_WINNIPEG" "yes"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- MidRise__Kelowna_5B/activity (1) ---
recover_one "$ROOT/idfs/MidRise__Kelowna_5B/activity/sample_008_HH143171/2022/Scenario_2022.idf" "$EPW_KELOWNA" "no"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- MidRise__Montreal_6A/activity (1) ---
recover_one "$ROOT/idfs/MidRise__Montreal_6A/activity/sample_010_HH27699/2030/Scenario_2030.idf" "$EPW_MONTREAL" "no"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- MidRise__Toronto_5A/baseline (1) ---
recover_one "$ROOT/idfs/MidRise__Toronto_5A/baseline/sample_035_HH22375/2022/Scenario_2022.idf" "$EPW_TORONTO" "no"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

# --- MidRise__Vancouver_5C/baseline (1) ---
recover_one "$ROOT/idfs/MidRise__Vancouver_5C/baseline/sample_007_HH133575/2022/Scenario_2022.idf" "$EPW_VANCOUVER" "no"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

echo ""
echo "=== Recovery-32 complete: succeeded=$DONE  failed=$FAIL ==="
echo "Date: $(date)"
[ $FAIL -gt 0 ] && exit 1 || exit 0
