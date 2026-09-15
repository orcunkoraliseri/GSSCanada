#!/bin/bash
#SBATCH --job-name=t20_hhid_check
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T20/logs/slurm_t20_hhid_check_%j.out

# T20 -- N2 household-ID literal set-equality check.
# Compares SIM_HH_ID sets of the two final 17-col BEM_Schedules_*.csv files
# (the files EnergyPlus reads): main 2030 vs Nb-f 2022 (the one unmeasured
# part of N2), and null 2030 vs Nb-f 2022 as a positive control that must
# give 0/0. Reads only the SIM_HH_ID column, chunked. Does not touch any
# other T20/T18c file.
#
# Task doc: 2026-09-15_T20_wp1_d1_2030_build.md, "Ledger (2026-09-15,
# re-point to Nb-f stock)" / "Collector (2026-09-15)" /
# "WHAT I DID NOT VERIFY (collector pass, 2026-09-15)".

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR=/speed-scratch/o_iseri/2J_revision/T20/T20_scripts

MAIN_2030=/speed-scratch/o_iseri/2J_revision/T20/out/main/BEM_Setup/BEM_Schedules_2030.csv
NULL_2030=/speed-scratch/o_iseri/2J_revision/T20/out/null/BEM_Setup/BEM_Schedules_2030.csv
NBF_2022=/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv

echo "[T20_HHID_CHECK] start $(date)"
echo "[T20_HHID_CHECK] main_2030=$MAIN_2030"
echo "[T20_HHID_CHECK] null_2030=$NULL_2030"
echo "[T20_HHID_CHECK] nbf_2022=$NBF_2022"

set +e
"$PYTHON" "$SCRIPT_DIR/t20_hhid_check.py" \
    --pair main_vs_nbf2022 "$MAIN_2030" "$NBF_2022" \
    --pair null_vs_nbf2022 "$NULL_2030" "$NBF_2022" \
    --expected-count 144465
RC=$?
set -e

echo "[T20_HHID_CHECK] python exit=$RC"
echo "[T20_HHID_CHECK] end $(date)"
exit $RC
