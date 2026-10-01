#!/bin/bash
#SBATCH -J mzpcompile
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -o /speed-scratch/o_iseri/5J/mz_pilot/logs/compile_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
R=/speed-scratch/o_iseri/5J/mz_pilot
for f in $R/repo/5J_docs_occ/tools/5thJ_idf_mz.py $R/mzp_build.py $R/mzp_extract.py $R/5thJ_mz_pilot_check.py; do
  $PY -c "import ast,sys; ast.parse(open(sys.argv[1]).read()); print('SYNTAX_OK', sys.argv[1])" $f || echo "SYNTAX_FAIL $f"
done
