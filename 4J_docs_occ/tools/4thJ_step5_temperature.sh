#!/bin/bash
#SBATCH --job-name=4J_s5_temp
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step5_temp_%j.out

# Step 5, work item 5.4 -- the decoding temperature, calibrated on the fold's own
# held-in validation split.
#   usage: sbatch 4thJ_step5_temperature.sh <fold>      # es | uk | it
#
# The GRES is NAMED, not a bare `gpu:1` (FINDING 9): a bare request lets Slurm hand
# out any free slice, and the Step 4 pilot landed on one shared with three other
# processes. Same profile as the Step 4 folds, so the footprint is comparable.
#
# 🔴 THE ADAPTER IS THE D-S4-5 CHAIN (`runs_ds45`), ruled by the author 2026-08-21.
# D-S4-5 (b) is the registered basis for G4.1, so these are the runs whose gate
# verdicts the paper reports. Calibrating the older `runs/` weights would mean
# reporting one model's gates and shipping another model's diaries.

set -x
FOLD=${1:?usage: sbatch 4thJ_step5_temperature.sh <es|uk|it>}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step5_temperature.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- fold $FOLD not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_ds45/leg4_primary_fold_$FOLD/adapter
if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- item 5.4 cannot run for fold $FOLD."
    exit 1
fi

OUT=/speed-scratch/o_iseri/4J_step5
mkdir -p "$OUT"

"$ENVDIR/bin/python" -u 4thJ_step5_temperature.py \
    --fold "$FOLD" --adapter "$ADAPTER" --out "$OUT" \
    --gen-batch 8 --n-prompts 600

echo "--- artefact ---"
ls -l "$OUT"
md5sum "$OUT/temperature_calibration_$FOLD.json"
