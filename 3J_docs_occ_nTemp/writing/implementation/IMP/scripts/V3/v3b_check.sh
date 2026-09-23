#!/bin/bash
# V3b scorer, run after the array (afterany). Writes runs/V3b/_check/{v3b_summary.txt,
# v3b_scorecard.json, v3b_effects.csv}. Exit: 0 PASS, 1 FAIL, 2 NOT_EVALUABLE, 3 checker crash.
#SBATCH --job-name=3J_V3bchk
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/v3bchk_%j.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
cd $CODE || exit 1
$PY -u v3_check.py selftest --frozen $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/campaign_local_deliverable --out $ROOT/runs/V3b/_check
$PY -u v3_check.py v3b $ROOT/runs/V3b --frozen $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/campaign_local_deliverable --out $ROOT/runs/V3b/_check
RC=$?
echo "V3b checker exit=$RC (0 PASS, 1 FAIL, 2 NOT_EVALUABLE, 3 crash) $(date)"
exit $RC
