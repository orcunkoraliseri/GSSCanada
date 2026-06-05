#!/encs/bin/bash
#SBATCH --job-name=s9_gen
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_gen_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_gen_%j.err

# Phase 2 — Stage A: generate activity BEM_Schedules + all 240 IDFs.
#
# PRE-REQUISITES (done locally before sbatch):
#   (a) BEM_Schedules_2030.csv uploaded (13-col; 2022 already on cluster)
#   (b) Engine (Step8_docs/) + Step9 scripts uploaded
#   (c) activity_loads.py + 07_aug_to_bem.py uploaded
#   (d) Buildings_MTL_v242/ IDFs uploaded
#   (e) AUG CSV + 2030 diaries uploaded
#   (f) Dep check (step9_dep_check.sh) passed
#
# Sub-steps:
#   A1: run 07_aug_to_bem.py for 2022 + 2030 (backs up 13-col, writes 17-col activity)
#   A2: run step9_idf_gen.py to generate 240 IDFs + step9_manifest.csv

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
S2J=$GCMAIN/2J_docs_occ_nTemp
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64

mkdir -p $ROOT/logs $ROOT/idfs

echo "=== Step 9 Stage A: generate BEM_Schedules + IDFs ==="
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

# --- A1: Generate activity BEM_Schedules ---
# 07_aug_to_bem.py backs up the existing 13-col CSV as _CLASSIC_BAK_2026-05-31.csv
# then overwrites with the 17-col activity version.
echo ""
echo "--- A1: 07_aug_to_bem.py --year 2022 ---"
cd $S2J
$PYTHON 07_aug_to_bem.py --year 2022
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2022 failed"; exit 1; fi

echo ""
echo "--- A1: 07_aug_to_bem.py --year 2030 ---"
$PYTHON 07_aug_to_bem.py --year 2030
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2030 failed"; exit 1; fi

# Verify baseline backups + activity CSVs
for YR in 2022 2030; do
    BAK=$GCMAIN/BEM_Setup/BEM_Schedules_${YR}_CLASSIC_BAK_2026-05-31.csv
    ACT=$GCMAIN/BEM_Setup/BEM_Schedules_${YR}.csv
    if [ ! -f "$BAK" ]; then echo "ERROR: baseline backup missing: $BAK"; exit 1; fi
    NCOLS=$(head -1 "$BAK" | tr ',' '\n' | wc -l)
    ACOLS=$(head -1 "$ACT" | tr ',' '\n' | wc -l)
    echo "  Baseline $YR: $NCOLS cols (expect 13)   Activity $YR: $ACOLS cols (expect 17)"
    if [ "$ACOLS" -ne 17 ]; then echo "ERROR: activity CSV not 17-col"; exit 1; fi
done

# --- A2: Generate IDFs ---
echo ""
echo "--- A2: step9_idf_gen.py ---"
$PYTHON $S2J/Step9_docs/step9_cluster/step9_idf_gen.py --root $ROOT --n 20 --seed 42
if [ $? -ne 0 ]; then echo "ERROR: step9_idf_gen.py failed"; exit 1; fi

NIDFS=$(wc -l < $ROOT/step9_manifest.csv)
echo ""
echo "=== Stage A COMPLETE ==="
echo "  Manifest rows (incl. header): $NIDFS  (expect 241)"
echo "  Date: $(date)"
