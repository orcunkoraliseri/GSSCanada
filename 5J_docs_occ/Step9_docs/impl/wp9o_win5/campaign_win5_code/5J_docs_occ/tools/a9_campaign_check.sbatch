#!/bin/bash
#SBATCH -J 5J_9l_check
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/modelA/campaign_win5/logs/check_%j.out
# 5J Step 9l check job (a9_campaign_check). MANIFEST = csv; SKIPTEST=1 adds the skip-rule test on a copy of a real result.
# Exit code: 0 = every section ran (verdicts are the text); 4 = written but a section crashed (NOT_EVALUABLE); other = the check crashed.
C=/speed-scratch/o_iseri/5J/modelA/campaign_win5
: ${MANIFEST:?MANIFEST not set}
cd $C/root/5J_docs_occ/tools || exit 2
if [ "$SKIPTEST" = "1" ]; then
  /speed-scratch/o_iseri/envs/step4/bin/python -u a9_campaign_task.py check $MANIFEST --skiptest
else
  /speed-scratch/o_iseri/envs/step4/bin/python -u a9_campaign_task.py check $MANIFEST
fi
RC=$?
echo "check exit=$RC"
exit $RC
