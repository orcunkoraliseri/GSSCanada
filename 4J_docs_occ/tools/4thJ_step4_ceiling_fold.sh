#!/bin/bash
#SBATCH --job-name=4J_s4_ceiling
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --mem=192G
#SBATCH --cpus-per-task=8
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_ceiling_%j.out

# Step 4 -- THE CEILING RUN. Full fine-tune, 8-bit AdamW, ONE pre-named fold.
#   usage: sbatch 4thJ_step4_ceiling_fold.sh <fold> [control]
#
# `4thJ_04_finetuneLLM.md:61`: "Ceiling -- full fine-tune, 8-bit AdamW | Leg-5 |
# 1, on a pre-named fold | Answers 'does LoRA underfit a far-from-pretraining
# target'." It is a RECIPE COMPARISON reported in the methods. It is not a gate,
# it carries no G4.x id, and a number from it may never be written up as one.
#
# 🔴 SECOND ARGUMENT `control` RUNS THE REFUSAL, AND IT IS RUN FIRST.
# The trainer refuses `--run-type ceiling` when `bitsandbytes` is not importable
# rather than falling back to 32-bit AdamW. A refusal nobody has watched happen
# is an assumption, so `control` launches the identical job with PYTHONPATH unset
# and the log has to show it stopping at the optimiser. If the control does NOT
# stop, the guard is not guarding and the real run must not be trusted.
#
# 🔴 Effective batch stays 2 x 8 = 16, the same as every Leg-4 and Leg-5 LoRA
# fold. It is not re-tuned because the recipe changed: holding it constant is the
# only thing that makes "LoRA vs full fine-tune" a comparison of the recipe
# rather than of two different schedules.
#
# 🔴 No adapter is written (`save_this` excludes `ceiling`) and no diagnostics
# run: `4thJ_step4_diagnostics.py` takes `--adapter` and there is none. The
# reading this job exists for is the trainer's own loss curve beside the LoRA
# fold's, and that is what the methods section compares.

set -x
FOLD=${1:?usage: sbatch 4thJ_step4_ceiling_fold.sh <es|uk|it> [control]}
ARM=${2:-run}

ENVDIR=/speed-scratch/o_iseri/envs/step4
BNBDIR=/speed-scratch/o_iseri/envs/bnb_for_step4
RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_leg5_ceiling

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- ceiling run not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

case "$ARM" in
  control)
    echo "############ CONTROL ARM -- PYTHONPATH deliberately NOT set ############"
    echo "EXPECTED, written before the run: the trainer reaches the optimiser and"
    echo "FAILS with 'REFUSING rather than falling back to 32-bit AdamW'. A clean"
    echo "exit here would mean the guard does nothing."
    unset PYTHONPATH
    ;;
  run)
    if [ ! -d "$BNBDIR" ]; then
        echo "NO $BNBDIR -- run 4thJ_step4_ceiling_env.sh first."
        exit 1
    fi
    export PYTHONPATH="$BNBDIR"
    echo "PYTHONPATH=$PYTHONPATH  (envs/step4 itself is untouched)"
    ;;
  *)
    echo "second argument must be 'run' or 'control', got '$ARM'"
    exit 1
    ;;
esac

mkdir -p "$RUNDIR"

"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold "$FOLD" --leg 5 --run-type ceiling \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 2 --grad-accum 8 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"
RC=$?
echo "ceiling ($ARM) exit status: $RC"
if [ "$ARM" = "control" ]; then
    if [ "$RC" -eq 0 ]; then
        echo "🔴 CONTROL PASSED. The bitsandbytes guard is NOT guarding. Do not run"
        echo "   the real arm until this is understood."
    else
        echo "control failed as required."
    fi
fi

# The pre-registration is untouched by any of the above. Proving it, not assuming.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
ls -l "$RUNDIR"
