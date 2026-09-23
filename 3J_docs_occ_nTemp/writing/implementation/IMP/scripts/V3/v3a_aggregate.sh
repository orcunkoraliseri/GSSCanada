#!/bin/bash
# V3a aggregation, after v3a_array (afterok): one Step-8E aggregation per seed over the 8 cells of
# that seed, then the spread summary. !!! TODO: same input gate as v3a_array.sh.
#SBATCH --job-name=3J_V3aagg
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/v3aagg_%j.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
[ -f $ROOT/V3A_INPUTS_READY ] || { echo "FATAL: V3a inputs not marked ready"; exit 1; }
AGG=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py
for s in 42 101 202 303 404; do
  IN=$ROOT/agg_in/seed$s; mkdir -p $IN
  for d in $ROOT/runs/V3a/S__*__s$s; do
    tag=$(basename $d | sed -E 's/^S__(.*)__s[0-9]+$/\1/'); ln -sfn $d $IN/$tag
  done
  $PY -u $AGG --campaign-dir $IN --outdir $ROOT/agg_V3a/seed$s --eplus-idd $EPLUS_IDD --idf-name injected_resized.idf || exit 1
done
cd $CODE || exit 1
$PY -u v3_check.py v3a $ROOT/agg_V3a --frozen-agg $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable --out $ROOT/agg_V3a/_check
