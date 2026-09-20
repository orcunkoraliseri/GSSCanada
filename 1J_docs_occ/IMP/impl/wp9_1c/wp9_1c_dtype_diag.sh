#!/bin/tcsh
#SBATCH --job-name=wp9_1c_dtdiag
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_1c_dtype_diag_%j.out
set D = /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy
/speed-scratch/o_iseri/1J_rerun/venv2025/bin/python /speed-scratch/o_iseri/1J_rerun/occ2025/wp9_1c_dtype_diag.py $D/Outputs_CENSUS/BEM_Schedules_2025_original.csv $D/reference/BEM_Schedules_2025_APRIL.csv
