#!/bin/bash
#SBATCH --job-name=4J_s4_leg4
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_leg4_%j.out

# Step 4, work item 4.2 -- a full LEG-4 fold, plus its conditioning diagnostics.
#   usage: sbatch 4thJ_step4_leg4_fold.sh <fold>      # es | uk | it
#
# FINDING 9: the GRES is NAMED, not a bare `gpu:1`. A bare request lets Slurm hand out
# any free slice and the pilot landed on one shared with three other processes
# (FINDING 2). Naming the profile is what makes the memory footprint ours to reason about.
#
# Two epochs, not one. G4.9 is a forgetting gate and a single reading cannot regress from
# itself -- with one epoch it correctly reports NOT CHECKED, and NOT CHECKED is not a pass.
#
# Effective batch is held at 16 across EVERY run in Step 4 (2 x 8 here, 1 x 16 on the
# shared-slice pilot). Holding it constant is what makes the pilot and the folds
# comparable; it is not a free parameter to tune per job.

set -x
FOLD=${1:?usage: sbatch 4thJ_step4_leg4_fold.sh <es|uk|it>}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py 4thJ_step4_diagnostics.py \
    4thJ_step4_genperturb.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- fold $FOLD not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1


# ---------------------------------------------------------------------------
# 🔴 `D-S6-14`, author 2026-08-22 -- the OPTIONAL second argument.
#   usage: sbatch <this> <fold> [primary|permuted]     default primary
# `permuted` trains the RANDOM-LABEL-PERMUTATION CONTROL: the same fold, the same
# backbone, the same schedule, from shards whose prefix-to-body pairing was deranged
# by `4thJ_step4_shards.py --permute-labels`. It is the memorisation CEILING that
# `G6.10` and `G6.11` are read against, and it is not a model of anything.
# Nothing about the default path changes: with no second argument this file behaves
# exactly as it did before.
RUNTYPE=${2:-primary}
case "$RUNTYPE" in
  primary)
    MANIFEST_ARG=""
    RUNDIR=/speed-scratch/o_iseri/4J_step4/runs
    DIAG=/speed-scratch/o_iseri/4J_step4/diagnostics
    ;;
  permuted)
    MANIFEST_ARG="--shard-manifest /speed-scratch/o_iseri/4J_step4/shard_manifest_permuted_control.json"
    RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_permuted_control
    DIAG=/speed-scratch/o_iseri/4J_step4/diagnostics_permuted_control
    echo "PERMUTED CONTROL RUN -- nothing this job produces is a result."
    ;;
  *)
    echo "run-type must be primary or permuted, got '$RUNTYPE'"
    exit 1
    ;;
esac
mkdir -p "$DIAG"
ADAPTER=$RUNDIR/leg4_${RUNTYPE}_fold_$FOLD/adapter

"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold "$FOLD" --leg 4 --run-type "$RUNTYPE" $MANIFEST_ARG \
    --epochs 2 \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 2 --grad-accum 8 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"

if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- diagnostics cannot run for fold $FOLD."
    exit 1
fi

"$ENVDIR/bin/python" -u 4thJ_step4_diagnostics.py \
    --fold "$FOLD" --leg 4 --run-type "$RUNTYPE" --adapter "$ADAPTER" \
    --out "$DIAG" \
    --gen-stratified-k 6 --gen-batch 8 --ce-n 256 --max-len 1280

GEN=$DIAG/generated_${RUNTYPE}_$FOLD.jsonl
if [ "$RUNTYPE" = "permuted" ]; then
    echo "PERMUTED CONTROL: the generation-side perturbation battery is NOT run. Its"
    echo "gates ask whether a model of the population is right; this run is not one,"
    echo "and felling a gate on it would demonstrate nothing."
elif [ -s "$GEN" ]; then
    "$ENVDIR/bin/python" -u 4thJ_step4_genperturb.py \
        --fold "$FOLD" --generated "$GEN" --perturbation all
else
    echo "NO GENERATED FILE AT $GEN -- generation-side perturbations skipped for fold "
    echo "$FOLD, and that is recorded as a gap, not as a pass."
fi

md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
