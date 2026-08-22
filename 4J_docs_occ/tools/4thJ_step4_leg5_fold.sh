#!/bin/bash
#SBATCH --job-name=4J_s4_leg5
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --mem=192G
#SBATCH --cpus-per-task=8
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_leg5_%j.out

# Step 4, work item 4.2 -- a LEG-5 fold. `D-S7-3` (a) directive 4.
#   usage: sbatch 4thJ_step4_leg5_fold.sh <fold>      # es | uk | it
#
# This is the REPORTED leg: `allenai/Olmo-3-1025-7B` @ a81bae42db3975be1671e27b9c9a56da1a9f980f,
# resolved by the trainer from `staged_weights.json`, never from this file. `--run-type
# primary`, so LoRA in bf16 -- NO quantisation, therefore NO `bitsandbytes`, therefore
# `envs/step4` stays exactly as it was. Only the `ceiling` run-type would need it.
#
# 🔴 `FINDING 9`: the GRES is NAMED. The FULL 7g.80gb instance and not a MIG slice --
# 13.6 GiB of bf16 weights plus optimiser state and 1280-token activations do not fit a
# 20 GB slice, and a bare `gpu:1` is how the pilot lost its memory footprint (`FINDING 2`).
#
# 🔴 Effective batch is held at 16 -- 2 x 8, the SAME as every Leg-4 fold. It is not a
# free parameter to re-tune because the GPU got bigger; holding it constant is what makes
# the Leg-4 rehearsal and the Leg-5 result the same experiment at two model sizes.
#
# Epochs come from `4thJ_step4_thresholds.py:EPOCHS_LEG5` (3), not from this file, and are
# left unset here so the threshold module stays the single source.

set -x
FOLD=${1:?usage: sbatch 4thJ_step4_leg5_fold.sh <es|uk|it>}

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
    RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_leg5
    DIAG=/speed-scratch/o_iseri/4J_step4/diagnostics_leg5
    ;;
  permuted)
    MANIFEST_ARG="--shard-manifest /speed-scratch/o_iseri/4J_step4/shard_manifest_permuted_control.json"
    RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_leg5_permuted_control
    DIAG=/speed-scratch/o_iseri/4J_step4/diagnostics_leg5_permuted_control
    echo "PERMUTED CONTROL RUN -- nothing this job produces is a result."
    ;;
  *)
    echo "run-type must be primary or permuted, got '$RUNTYPE'"
    exit 1
    ;;
esac
mkdir -p "$DIAG"
ADAPTER=$RUNDIR/leg5_${RUNTYPE}_fold_$FOLD/adapter

"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold "$FOLD" --leg 5 --run-type "$RUNTYPE" $MANIFEST_ARG \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 2 --grad-accum 8 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"

if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- diagnostics cannot run for fold $FOLD."
    exit 1
fi

# 🔴 `--out` is REDIRECTED. `4thJ_step4_diagnostics.py:413` names its output
# `generated_<run_type>_<fold>.jsonl` with NO leg in the filename, so a Leg-5 run
# left at the default would silently overwrite the Leg-4 fold's diagnostics --
# the cache-key-collision class of `FINDING 8`. Redirected here rather than
# renamed inside the script, so nothing Leg 4 already wrote is disturbed.
# (`$DIAG` and `$RUNDIR` are set from `$RUNTYPE` at the top of this file.)

"$ENVDIR/bin/python" -u 4thJ_step4_diagnostics.py \
    --fold "$FOLD" --leg 5 --run-type "$RUNTYPE" --adapter "$ADAPTER" \
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
