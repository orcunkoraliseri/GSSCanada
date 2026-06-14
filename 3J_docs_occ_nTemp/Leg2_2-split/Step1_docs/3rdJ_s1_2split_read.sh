#!/encs/bin/bash
#SBATCH --job-name=3rdJ_s1_read
#SBATCH --partition=ps
#SBATCH --mem=64G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step1_2split_run/logs/s1_read_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step1_2split_run/logs/s1_read_%j.err

# Leg-2 (Residential + Office) Step 1: read all 4 GSS cycles with office-gating
# columns, write 8 CSVs (main_/episode_ x 2005/2010/2015/2022) to outputs_step1/,
# then run the validation report.
#
# PRE-REQUISITES (done before sbatch):
#   (a) 3rdJ_01_readingGSS_2split.py + 3rdJ_01_readingGSS_2split_val.py uploaded to S1DIR.
#   (b) Raw GSS microdata present under $DATA (the data-file gate below verifies this;
#       if any MISS, the job exits and you upload the named files, then re-submit).
#   (c) step4 env has pandas/numpy; pyreadstat is auto-installed below if absent.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
S1DIR=$GCMAIN/3J_docs_occ_nTemp/Leg2_2-split/Step1_docs
DATA=$GCMAIN/0_Occupancy/DataSources_GSS
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
ROOT=/speed-scratch/o_iseri/step1_2split_run

mkdir -p $ROOT/logs

echo "=== 3rdJ Leg-2 Step 1 reader START ==="
echo "Node: $(hostname)  Date: $(date)"
echo "Python: $($PYTHON --version 2>&1)"

# --- Dependency precheck (auto-install pyreadstat into step4 env if missing) ---
echo ""
echo "--- Python imports ---"
$PYTHON -c "import pandas, numpy; print('  OK  pandas', pandas.__version__, '| numpy', numpy.__version__)"
if [ $? -ne 0 ]; then echo "ERROR: pandas/numpy missing in step4 env"; exit 1; fi

$PYTHON -c "import pyreadstat" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  pyreadstat absent -> installing into step4 env"
    $PYTHON -m pip install --quiet pyreadstat
    $PYTHON -c "import pyreadstat" 2>/dev/null
    if [ $? -ne 0 ]; then echo "ERROR: pyreadstat install failed (no network on node?)"; exit 1; fi
fi
echo "  OK  pyreadstat"

$PYTHON -c "import seaborn, matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  seaborn/matplotlib absent -> installing into step4 env"
    $PYTHON -m pip install --quiet seaborn matplotlib
    $PYTHON -c "import seaborn, matplotlib" 2>/dev/null
    if [ $? -ne 0 ]; then echo "ERROR: seaborn/matplotlib install failed (no network on node?)"; exit 1; fi
fi
echo "  OK  seaborn/matplotlib"

# --- Data-file gate (all 12 inputs the reader opens) ---
echo ""
echo "--- Data file check ---"
MISS=0
chk() { if [ -f "$1" ]; then echo "  OK   $(du -h "$1" | cut -f1)  $1"; else echo "  MISS $1"; MISS=1; fi; }

chk "$DATA/Main_files/GSSMain_2005.sas7bdat"
chk "$DATA/Episode_files/GSS_2005_episode/C19PUMFE_NUM.SAV"
chk "$DATA/Main_files/GSSMain_2010.DAT"
chk "$DATA/Main_files/GSSMain_2010_syntax.SPS"
chk "$DATA/Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT"
chk "$DATA/Episode_files/GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS"
chk "$DATA/Main_files/GSSMain_2015.txt"
chk "$DATA/Main_files/GSSMain_2015.sps"
chk "$DATA/Episode_files/GSS_2015_episode/GSS29PUMFE.txt"
chk "$DATA/Episode_files/GSS_2015_episode/c29pumfe_e.sps"
chk "$DATA/Main_files/GSSMain_2022.sas7bdat"
chk "$DATA/Episode_files/GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat"

if [ $MISS -ne 0 ]; then
    echo ""
    echo "=== ABORT: missing input files above — upload them under $DATA then re-submit ==="
    exit 1
fi

cd $S1DIR || { echo "ERROR: cannot cd $S1DIR"; exit 1; }

# --- Step 1a: read all cycles -> 8 CSVs in outputs_step1/ ---
echo ""
echo "--- Reader: 3rdJ_01_readingGSS_2split.py ---"
$PYTHON 3rdJ_01_readingGSS_2split.py
if [ $? -ne 0 ]; then echo "ERROR: reader failed"; exit 1; fi

NCSV=$(ls outputs_step1/main_*.csv outputs_step1/episode_*.csv 2>/dev/null | wc -l)
echo "  CSVs written: $NCSV  (expect 8)"

# --- Step 1b: validation report ---
echo ""
echo "--- Validator: 3rdJ_01_readingGSS_2split_val.py ---"
$PYTHON 3rdJ_01_readingGSS_2split_val.py
if [ $? -ne 0 ]; then echo "WARN: validator returned non-zero — inspect report"; fi

echo ""
echo "=== 3rdJ Leg-2 Step 1 COMPLETE ==="
echo "  Outputs: $S1DIR/outputs_step1/"
echo "  Date: $(date)"
