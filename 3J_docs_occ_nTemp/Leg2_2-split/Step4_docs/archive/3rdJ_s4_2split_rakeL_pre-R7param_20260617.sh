#!/encs/bin/bash
#SBATCH --job-name=3J_s4_rakeL
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_rakeL_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_rakeL_%x_%j.err

# 3rdJ Step 4L — Joint AT_HOME + AT_WORK post-hoc raking (GPU needed for model.generate)
. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4L — Joint Rake =====" ; date
echo "SLURM_JOB_ID: $SLURM_JOB_ID  Node: $SLURMD_NODENAME"

$PYTHON -c "import pandas, numpy, torch" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages..."
    $PYTHON -m pip install --quiet pandas numpy torch 2>&1 | tail -5
}

cd "$SDIR"
$PYTHON 3rdJ_04L_joint_rake_2split.py
EXIT_RAKE=$?
echo "[DONE] Rake exit code: $EXIT_RAKE" ; date
exit $EXIT_RAKE
