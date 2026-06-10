#!/encs/bin/bash
#SBATCH --job-name=s8_aggval_v2
#SBATCH --partition=ps
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/aggval_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/aggval_%j.err

# Step 8 corrected-v2 FULL aggregate + validate (Sub-steps 8E + 8F on the v2 campaign).
#   Pass A: 08_simulation_plots.py --rebuild-agg --figs all  -> agg tables + 11 figures
#   Pass B: 08_simulation_val.py (8-section validator)       -> step8_validation_report.html
# Schedules read from the PRIVATE as-built dir (step8_run/sched), NOT BEM_Setup,
# so the Section-2 round-trip is a true as-built check for all 5 years.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
RES=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/campaign_N50
OUT=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/outputs_step8
SCHED=/speed-scratch/o_iseri/step8_run/sched
export MPLBACKEND=Agg

echo "=== step8_aggval_v2.sh  job=$SLURM_JOB_ID  node=$SLURMD_NODENAME  $(date) ==="

# --- Prechecks (fail fast, no partial outputs) ---
$PYTHON -c "import numpy, pandas, matplotlib, scipy; print('deps ok')" || { echo "FATAL: missing python dep (need numpy/pandas/matplotlib/scipy)"; exit 1; }
cd "$STEP8_DIR" || { echo "FATAL: no $STEP8_DIR"; exit 1; }
$PYTHON -c "from eSim_bem_utils_2J import plotting; print('engine plotting ok')" || { echo "FATAL: eSim_bem_utils_2J not importable from $STEP8_DIR"; exit 1; }
for yr in 2005 2010 2015 2022 2030; do
    [ -f "$SCHED/BEM_Schedules_${yr}.csv" ] || { echo "FATAL: missing $SCHED/BEM_Schedules_${yr}.csv"; exit 1; }
done
NCSV=$(find "$RES" -name "hourly_meters.csv" | wc -l)
NSQL=$(find "$RES" -name "eplusout.sql" | wc -l)
echo "hourly_meters.csv: $NCSV (expect 6000)   eplusout.sql: $NSQL (EUI/area source)"
if [ "$NSQL" -eq 0 ]; then echo "FATAL: no eplusout.sql under $RES -- EUI/area would be NaN and the validator would fail"; exit 1; fi

mkdir -p "$OUT"

# --- Pass A: aggregation + all figures (8E on v2) ---
echo "=== Pass A: 08_simulation_plots.py --rebuild-agg  $(date) ==="
$PYTHON 08_simulation_plots.py --results-dir "$RES" --out "$OUT" --schedules-dir "$SCHED" --rebuild-agg --figs all
EXIT_A=$?
echo "Pass A exit=$EXIT_A  $(date)"
[ $EXIT_A -ne 0 ] && exit $EXIT_A

# --- Pass B: full 8-section validation (8F on v2) ---
echo "=== Pass B: 08_simulation_val.py  $(date) ==="
$PYTHON 08_simulation_val.py --sim-dir "$RES" --sched-dir "$SCHED" --agg-dir "$OUT/agg" --out-dir "$OUT"
EXIT_B=$?
echo "Pass B exit=$EXIT_B  $(date)"
[ $EXIT_B -ne 0 ] && exit $EXIT_B

echo "=== DONE $(date) ==="
echo "Aggregates: $OUT/agg/"
echo "Figures   : $OUT/figures/"
echo "Report    : $OUT/step8_validation_report.html"
