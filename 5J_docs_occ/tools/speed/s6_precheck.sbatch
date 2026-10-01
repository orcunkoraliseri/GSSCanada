#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -J s6_precheck
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_precheck_%j.out
# syntax checks of the part B scripts + the collect parser on a REAL capture of the validation scoring (no test file, no test truth)
C=/speed-scratch/o_iseri/5J/test/code
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export PYTHONDONTWRITEBYTECODE=1
for f in s6_startup.sh s6_seenfail.sh s6_seenfail.sbatch s6_score.sbatch s6_collect.sbatch; do bash -n $C/$f && echo "BASH_SYNTAX_OK $f $(md5sum < $C/$f | cut -d' ' -f1)" || echo "BASH_SYNTAX_FAIL $f"; done
$PY -c "import sys; compile(open('$C/s6_collect.py').read(),'s6_collect.py','exec'); print('PY_SYNTAX_OK s6_collect.py')" || echo PY_SYNTAX_FAIL
cd $C
for t in S3 B0; do
$PY -c "
import sys; sys.path.insert(0,'$C')
import s6_collect as c
p = c.parse_call(c.read_text('/speed-scratch/o_iseri/5J/train/score/score_$t.txt'))
print('REAL_CAPTURE $t gates', len(p['gates']), 'counts', c.check_counts(p), 'verdicts', c.check_verdicts(p), 'exit', c.check_exit(p, 0), 'runs_printed', p['runs_printed'])
r = [g for g in p['gates'] if g['gate']=='G5J.3'][0]; print('SAMPLE_G3', {k: r[k] for k in ('country','class','target','verdict','r2','sign','skill_over_B1','ci_lo','ci_hi','buildings','households')})
r = [g for g in p['gates'] if g['gate']=='G5J.4'][0]; print('SAMPLE_G4', {k: r[k] for k in ('verdict','ctrl_r2','ctrl_sign','ctrl_skill_ci_lo','flagged')})
print('CLAIM_RULE', c.claim_word(8,4,4,0), c.claim_word(6,4,2,0), c.claim_word(2,1,1,0), c.claim_word(8,4,4,2))
"
done
echo PRECHECK_DONE
