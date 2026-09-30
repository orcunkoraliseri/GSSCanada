#!/bin/tcsh
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH -J wp13
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp13_%j.out

set W = /speed-scratch/o_iseri/1J_rerun/wp13
set PY = /speed-scratch/o_iseri/GSSCanada/venv/bin/python
setenv PYTHONIOENCODING utf-8
setenv MPLBACKEND Agg
setenv MPLCONFIGDIR $W/mplcfg
setenv WP13_FIGS $W/out/figs
mkdir -p $W/out/figs $W/mplcfg
cd $W

echo "WP13 start `date`"
echo "--- input sizes (ls -l) ---"
set O = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy
ls -l $O/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv $O/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv $O/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv $O/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv
echo "--- STEP 1 metrics, Quebec, HHSIZE, tiers ---"
$PY wp13_metrics.py --outdir $W/out
echo "STEP1 exit $status"
echo "--- STEP 2 Fig 8 + C2 (temporal) ---"
cd $W/plot
$PY plot_temporal_comparison.py
echo "STEP2 exit $status"
echo "--- STEP 3 Fig C1 (non-temporal) ---"
$PY plot_nontemporal_comparison.py
echo "STEP3 exit $status"
echo "--- STEP 4 Fig 11 (presence evolution v2) ---"
$PY plot_presence_evolution_v2.py
echo "STEP4 exit $status"
cd $W
echo "--- STEP 5 Fig 13 ---"
$PY run_fig13.py
echo "STEP5 exit $status"
echo "--- STEP 6 Fig 14 ---"
cd $W/plot
$PY plot_hhsize_occupancy.py
echo "STEP6 exit $status"
cd $W
echo "--- STEP 7 Fig 12 (slow: reads the 5 aggregated activity files) ---"
$PY run_fig12.py
echo "STEP7 exit $status"
echo "--- STEP 8 old vs new table ---"
$PY build_old_vs_new.py --dir $W/out
echo "STEP8 exit $status"
ls -l $W/out $W/out/figs
echo "JOB DONE"
