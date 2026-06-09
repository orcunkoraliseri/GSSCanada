#!/encs/bin/bash
#SBATCH --job-name=s9_a1_csv
#SBATCH --partition=ps
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_a1_csv_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_a1_csv_%j.err

# Step 9 corrected re-run 2026-06-08: regenerate BEM_Schedules_2022.csv + _2030.csv
# using the fixed 07_aug_to_bem.py (np.roll +4h diary->clock correction).
# Run BEFORE Stage A (non-destructive) and occ_verify gate.
# Step 8 job 952987 FAILED/done; safe to overwrite BEM_Schedules.

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
S2J=$GCMAIN/2J_docs_occ_nTemp
BEM_DIR=$GCMAIN/BEM_Setup
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "=== Step 9 A1 CSV-gen: corrected BEM_Schedules (2026-06-08 +4h fix) | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

echo ""
echo "--- 07_aug_to_bem.py --year 2022 ---"
cd $S2J
$PYTHON 07_aug_to_bem.py --year 2022
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2022 failed"; exit 1; fi

echo ""
echo "--- 07_aug_to_bem.py --year 2030 ---"
$PYTHON 07_aug_to_bem.py --year 2030
if [ $? -ne 0 ]; then echo "ERROR: 07_aug_to_bem.py 2030 failed"; exit 1; fi

for YR in 2022 2030; do
    ACT=$BEM_DIR/BEM_Schedules_${YR}.csv
    ACOLS=$(head -1 "$ACT" | tr ',' '\n' | wc -l)
    echo "  Activity $YR: $ACOLS cols (expect 17)"
    if [ "$ACOLS" -ne 17 ]; then echo "ERROR: activity CSV not 17-col for $YR"; exit 1; fi
done

echo ""
echo "=== A1 CSV-gen COMPLETE: corrected BEM_Schedules_2022.csv + _2030.csv written ==="
echo "Date: $(date)"
