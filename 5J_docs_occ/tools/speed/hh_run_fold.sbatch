#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J hh_fold
# usage: sbatch --export=ALL,FOLD=es,YEAR=2010,OUTNAME=es_60,HIDS=hids_es60.csv hh_run_fold.sbatch
R=/speed-scratch/o_iseri/5J/households
PY=/speed-scratch/o_iseri/envs/step4/bin/python
$PY -u -c "import sys,numpy,pandas;print('python',sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__)"
cd $R/repo
$PY -u 5J_docs_occ/tools/5thJ_step9_trigger_act2.py --root $R/repo/4J_docs_occ --fold $FOLD --leg leg5 --year $YEAR --seed 1 --households 100 --timestep 60 --shipped-suffix _cal$YEAR --corpus $R/repo/4J_step3_corpus_es_it.jsonl --hids $R/repo/5J_docs_occ/Step2_docs/outputs_step2/$HIDS --out $R/$OUTNAME
echo "TRIGGER exit=$?"
