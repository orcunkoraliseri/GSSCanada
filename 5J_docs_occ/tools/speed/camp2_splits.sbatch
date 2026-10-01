#!/bin/bash
#SBATCH -J camp2D
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/splits_%j.out
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S=/speed-scratch/o_iseri/5J/splits
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -u $R/camp2_splits.py || { echo "SPLITS_SCRIPT_FAILED"; exit 1; }
echo "--- file modes and md5 (as written)"
ls -l $S
cat $S/splits.md5
echo "MD5_CHECK_NOT_OK_COUNT $(md5sum -c $S/splits.md5 | grep -vc ': OK')"
echo "--- a write to a sealed file must fail"
( echo x >> $S/development.txt ) 2>&1 | sed 's/^/WRITE_TEST /'
echo "--- gates_frozen.md5 must NOT exist"
ls /speed-scratch/o_iseri/5J/gates_frozen.md5 2>&1 | sed 's/^/GATE_FILE_LS /'
echo "--- loader tests"
PYTHONPATH=$R $PY -u $R/camp2_loader_test.py
echo "LOADER_TEST_EXIT $?"
echo "end=$(date -Iseconds)"
