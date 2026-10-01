#!/bin/bash
#SBATCH -J frz_misc2
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/misc2_%j.out
# fix 1 copy of frz_misc.sbatch. The last command ends with `|| true`: the old job showed FAILED 2:0 only because `ls` of the absent
# gates_frozen.md5 exits 2, although the output was complete; here that absence is expected and must not make the job fail.
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
echo "== refusal"; $PY -u $F/frz_refusal.py
echo "== sources check (gates 1.1, 1.2)"; $PY -u $F/5thJ_04_scorer.py --mode sources --sources $F/gates_frozen.md
echo "== md5 (inside a job)"; md5sum $F/gates_frozen.md $F/5thJ_04_scorer.py $F/split_loader.py $F/out/floors_PLANTED_HIGH.json
echo "== gate file absent"; ls -la /speed-scratch/o_iseri/5J/gates_frozen.md5 2>&1 || true
exit 0
