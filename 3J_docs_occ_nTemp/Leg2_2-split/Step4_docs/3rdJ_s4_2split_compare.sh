#!/encs/bin/bash
#SBATCH --job-name=3J_s4_cmp
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_cmp_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_cmp_%j.err

# ── 3rdJ Step 4N: Pareto comparison of raked bases (R7/R8/R10) ────────────────
# Fires last in the auto-chain (afterok on both _raked validators). Reads each
# variant's step4_validation_report.txt + runs the home-gated act30 probe, then
# prints the Pareto table. Writes compare_raked.txt next to the script outputs.
# Submit:  sbatch --dependency=afterok:<R8val>:<R10val> 3rdJ_s4_2split_compare.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4N — Raked-base Pareto comparison ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID  Node: $SLURMD_NODENAME"

cd "$SDIR"
$PYTHON 3rdJ_04N_compare_raked.py outputs_step4/sweep R7_cap_raked R8_deep_raked R10_fast_raked | tee outputs_step4/sweep/compare_raked.txt
EXIT_CMP=${PIPESTATUS[0]}
echo "[DONE] Compare exit code: $EXIT_CMP"
date
exit $EXIT_CMP
