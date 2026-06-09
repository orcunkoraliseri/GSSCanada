#!/encs/bin/bash
#SBATCH --job-name=s9_occ_gate
#SBATCH --partition=ps
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_occ_gate_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_occ_gate_%j.err

# GATE: verify BEM_Schedules_2022.csv has the +4h diary->clock fix applied.
# Exits 1 on FAIL (occupancy not overnight-peaked) -> afterok chain aborts downstream.
# Must run after step9_a1_csv_gen.sh completes.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
S9=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step9_docs/step9_cluster

echo "=== Step 9 occupancy-clock gate | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

$PYTHON $S9/step9_occ_verify.py
RC=$?
echo "occ_verify exit code: $RC"
exit $RC
