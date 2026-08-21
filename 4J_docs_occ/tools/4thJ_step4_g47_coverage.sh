#!/bin/bash
#SBATCH --job-name=4J_s4_g47cov
#SBATCH --partition=pt
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_g47cov_%j.out

# G4.7 -- the one gate the coverage clause has never seen fall on a LOCO fold.
#   usage: sbatch 4thJ_step4_g47_coverage.sh            # all three folds
#          sbatch 4thJ_step4_g47_coverage.sh uk         # one fold
#
# 🔴 NO GPU, ON PURPOSE. This scores an already-persisted generated set, so it runs on the
# CPU partition and CANNOT contend with the D-S4-5 chain or any training job. That is the
# same reasoning that put FINDING 29's re-score on `pt` as job 1274945. It is safe to
# submit while the GPU is busy -- unlike 4thJ_step4_g41_seedfloor.sh, which is not.
#
# What it closes: the coverage clause FAILs on es, uk and it, all three because G4.7
# passes at baseline and no perturbation on those folds ever made it fall. What it does
# NOT close: whether TRAINING can break termination. See the header of the .py.

set -x
ONLY=${1:-}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_g47_coverage.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- G4.7 coverage demonstration not started"
    exit 1
fi

DIAGDIR=/speed-scratch/o_iseri/4J_step4/diagnostics
FOLDS=${ONLY:-"es uk it"}

for F in $FOLDS ; do
    GEN="$DIAGDIR/generated_primary_${F}.jsonl"
    if [ ! -s "$GEN" ]; then
        # 🔴 Named, not skipped. A fold silently absent from a coverage demonstration is
        # indistinguishable in the output from a fold that passed it.
        echo "🔴 FOLD $F HAS NO GENERATED SET AT $GEN -- coverage NOT demonstrated for"
        echo "   this fold, and that is a gap, not a pass. Check the diagnostics run."
        continue
    fi
    "$ENVDIR/bin/python" -u 4thJ_step4_g47_coverage.py --fold "$F" --generated "$GEN" --rate 0.01
done

md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
