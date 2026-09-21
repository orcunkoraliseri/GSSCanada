#!/bin/bash
#SBATCH --job-name=wp10_stage4_default_RC4
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=24G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_default_RC4_%j.out

# WP10 Stage 4c: Default (--iter-count 1) task for NUS_RC4, on the RE-STAGED
# schedule files (Stage-1 rebuilt grid files, manager ruling (a)). Same job shape as
# Stage 3's Gate 3 test run (wp9_step3_rc1.sh), only --output-dir changed.
# Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

CODE=/speed-scratch/o_iseri/1J_rerun/code
VENV=/speed-scratch/o_iseri/GSSCanada/venv
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64

echo "=== Pre-flight: md5 dedupe check on staged schedule CSVs ==="
M2005=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2005.csv" | awk '{print $1}')
M2010=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2010.csv" | awk '{print $1}')
M2015=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2015.csv" | awk '{print $1}')
M2022=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2022.csv" | awk '{print $1}')
M2025=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2025.csv" | awk '{print $1}')
echo "2005=$M2005"
echo "2010=$M2010"
echo "2015=$M2015"
echo "2022=$M2022"
echo "2025=$M2025"

DUP=0
if [ "$M2005" = "$M2010" ] || [ "$M2005" = "$M2015" ] || [ "$M2005" = "$M2022" ] || [ "$M2005" = "$M2025" ] || \
   [ "$M2010" = "$M2015" ] || [ "$M2010" = "$M2022" ] || [ "$M2010" = "$M2025" ] || \
   [ "$M2015" = "$M2022" ] || [ "$M2015" = "$M2025" ] || \
   [ "$M2022" = "$M2025" ]; then
  DUP=1
fi

if [ "$DUP" -eq 1 ]; then
  echo "ERROR: two staged schedule CSVs share an md5 -- stopping before run."
  exit 3
fi
echo "Dedupe check OK: all five schedule CSV md5 distinct."

source "$VENV/bin/activate"
export ENERGYPLUS_DIR="$EP_DIR"

echo "=== Running run_batch_hpc.py NUS_RC4 (Default, --iter-count 1) ==="
python "$CODE/eSim_bem_utils/run_batch_hpc.py" \
    --idf        "$CODE/BEM_Setup/Neighbourhoods/NUS_RC4.idf" \
    --region     Quebec \
    --sim-mode   standard \
    --iter-count 1 \
    --output-dir /speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1 \
    --workers    1

EXIT_CODE=$?
echo "Done: NUS_RC4 Stage4 Default (exit code: $EXIT_CODE)"
exit $EXIT_CODE
