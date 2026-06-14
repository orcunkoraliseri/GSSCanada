#!/encs/bin/bash
#SBATCH --job-name=3rdJ_s1_val
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step1_2split_run/logs/s1_val_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step1_2split_run/logs/s1_val_%j.err

# Validator-only re-run: the reader (job 967942) already wrote the 8 CSVs to
# outputs_step1/. This job just installs the plotting deps (seaborn/matplotlib)
# that were missing in the step4 env, then runs the validation report.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
S1DIR=$GCMAIN/3J_docs_occ_nTemp/Leg2_2-split/Step1_docs
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

mkdir -p /speed-scratch/o_iseri/step1_2split_run/logs

echo "=== 3rdJ Leg-2 Step 1 VALIDATOR-ONLY START ==="
echo "Node: $(hostname)  Date: $(date)"

echo ""
echo "--- Plotting deps ---"
$PYTHON -c "import seaborn, matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  seaborn/matplotlib absent -> installing into step4 env"
    $PYTHON -m pip install --quiet seaborn matplotlib
    $PYTHON -c "import seaborn, matplotlib" 2>/dev/null
    if [ $? -ne 0 ]; then echo "ERROR: seaborn/matplotlib install failed (no network on node?)"; exit 1; fi
fi
echo "  OK  seaborn/matplotlib"

NCSV=$(ls $S1DIR/outputs_step1/main_*.csv $S1DIR/outputs_step1/episode_*.csv 2>/dev/null | wc -l)
echo "  CSVs present: $NCSV  (expect 8)"
if [ "$NCSV" -ne 8 ]; then echo "ERROR: expected 8 CSVs in outputs_step1/ — run the reader first"; exit 1; fi

cd $S1DIR || { echo "ERROR: cannot cd $S1DIR"; exit 1; }

echo ""
echo "--- Validator: 3rdJ_01_readingGSS_2split_val.py ---"
$PYTHON 3rdJ_01_readingGSS_2split_val.py
RC=$?
if [ $RC -ne 0 ]; then echo "WARN: validator returned non-zero ($RC) — inspect report"; fi

echo ""
echo "=== 3rdJ Leg-2 Step 1 VALIDATOR-ONLY COMPLETE (rc=$RC) ==="
echo "  Date: $(date)"
