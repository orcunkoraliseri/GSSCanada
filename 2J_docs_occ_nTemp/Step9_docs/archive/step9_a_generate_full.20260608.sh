#!/encs/bin/bash
#SBATCH --job-name=s9_gen_full
#SBATCH --partition=ps
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_gen_full_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_gen_full_%j.err

# Stage A (FULL GRID): generate 17-col activity BEM_Schedules + 13-col baselines + 9,600 IDFs.
#
# Sub-steps:
#   A1: 07_aug_to_bem.py for 2022 + 2030  -> 17-col activity CSVs
#   A2-1: step9_a2_baseline_extract.py    -> 13-col baseline CSVs (same HH IDs as activity)
#   A2-2: step9_idf_gen_full.py --n 50    -> 9,600 IDFs + step9_manifest.csv
#
# PRE-REQUISITES (done locally before sbatch):
#   (a) New cluster scripts uploaded (step9_idf_gen_full.py, this script, etc.)
#   (b) activity_loads.py + 07_aug_to_bem.py already on cluster (from 3-cell run)
#   (c) Buildings_MTL_v242/ IDFs + EPW files already on cluster
#   (d) AUG CSV + 2030 diaries already on cluster
#   (e) step9_dep_check.sh passed (step4 env has eppy/pandas/numpy/yaml/joblib)
#
# Expected output: 9,601-row manifest (header + 9,600 IDFs), ~64 GB IDF tree.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
S2J=$GCMAIN/2J_docs_occ_nTemp
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
BEM_DIR=$GCMAIN/BEM_Setup

mkdir -p $ROOT/logs $ROOT/idfs

echo "=== Step 9 Stage A FULL: generate BEM_Schedules + IDFs ==="
echo "Node: $(hostname)  Date: $(date)"

# --- Extract Energy+.idd from container (needed by eppy for IDF generation) ---
echo ""
echo "--- Extracting Energy+.idd ---"
singularity exec --bind /speed-scratch $SIF cat ${EP_BIN}/Energy+.idd > $ROOT/Energy+.idd
if [ $? -ne 0 ] || [ ! -s "$ROOT/Energy+.idd" ]; then
    echo "ERROR: IDD extraction failed"
    exit 1
fi
echo "IDD extracted: $(wc -c < $ROOT/Energy+.idd) bytes"
export ENERGYPLUS_DIR=$ROOT
export IDD_FILE=$ROOT/Energy+.idd

# --- A1: Generate 17-col activity BEM_Schedules ---
echo ""
echo "--- A1: 07_aug_to_bem.py --year 2022 ---"
cd $S2J
$PYTHON 07_aug_to_bem.py --year 2022
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2022 failed"; exit 1; fi

echo ""
echo "--- A1: 07_aug_to_bem.py --year 2030 ---"
$PYTHON 07_aug_to_bem.py --year 2030
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2030 failed"; exit 1; fi

for YR in 2022 2030; do
    ACT=$BEM_DIR/BEM_Schedules_${YR}.csv
    ACOLS=$(head -1 "$ACT" | tr ',' '\n' | wc -l)
    echo "  Activity $YR: $ACOLS cols (expect 17)"
    if [ "$ACOLS" -ne 17 ]; then echo "ERROR: activity CSV not 17-col"; exit 1; fi
done

# --- A2-1: Extract 13-col baseline CSVs from activity CSVs ---
echo ""
echo "--- A2-1: step9_a2_baseline_extract.py ---"
$PYTHON $S2J/Step9_docs/step9_cluster/step9_a2_baseline_extract.py --bem_dir "$BEM_DIR"
if [ $? -ne 0 ]; then echo "ERROR: baseline extract failed"; exit 1; fi

for YR in 2022 2030; do
    BL=$BEM_DIR/BEM_Schedules_${YR}_baseline.csv
    if [ ! -f "$BL" ]; then echo "ERROR: baseline missing $BL"; exit 1; fi
    BCOLS=$(head -1 "$BL" | tr ',' '\n' | wc -l)
    echo "  Baseline $YR: $BCOLS cols (expect 13)"
    if [ "$BCOLS" -ne 13 ]; then echo "ERROR: baseline CSV not 13-col"; exit 1; fi
done

# --- A2-2: Generate 9,600 IDFs (full 24-cell grid, n=50) ---
echo ""
echo "--- A2-2: step9_idf_gen_full.py --n 50 ---"
$PYTHON $S2J/Step9_docs/step9_cluster/step9_idf_gen_full.py --root $ROOT --n 50 --seed 42
if [ $? -ne 0 ]; then echo "ERROR: step9_idf_gen_full.py failed"; exit 1; fi

NIDFS=$(wc -l < $ROOT/step9_manifest.csv)
echo ""
echo "=== Stage A FULL COMPLETE ==="
echo "  Manifest rows (incl. header): $NIDFS  (expect 9601)"
if [ "$NIDFS" -ne 9601 ]; then
    echo "  WARN: expected 9601 rows, got $NIDFS — check log for skipped IDFs"
fi
echo "  Date: $(date)"
