#!/bin/bash
#SBATCH --job-name=4J_s4_ds45
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_ds45_%j.out

# D-S4-5, RULED (b) BY THE AUTHOR 2026-08-19 -- the mid-epoch checkpoint basis for G4.1.
#   usage: sbatch 4thJ_step4_ds45_midepoch_fold.sh <fold>      # es | uk | it
#
# The basis is registered in Step4_docs/outputs_step4/proglog_step4_gates.md BEFORE this
# script existed and BEFORE any run reported under it. Read that entry before reading any
# number this job prints.
#
# 🔴 WHAT THIS RUN IS AND IS NOT. It re-trains one fold on the SAME shard with the SAME
# recipe and adds three G4.1 readings inside the final epoch, at the registered 0.25 /
# 0.50 / 0.75 points. The VERDICT comes from frac 0.50 ONLY, named in advance; 0.25 and
# 0.75 are descriptive and are not eligible to supply it. The grid and the verdict point
# are CONSTANTS in 4thJ_step4_train.py, deliberately not flags, so nothing here can move
# them.
#
# 🔴 IT WRITES TO A SEPARATE TREE. `runs_ds45`, never `runs`. The closed folds -- es
# (1274884) and uk (1274964) -- and their adapters are evidence and are not overwritten by
# a re-run. This is the same rule that put FINDING 29's re-score in `genperturb_f29/`.
#
# 🔴 IT RUNS THE TRAINER ONLY -- no diagnostics, no genperturb. D-S4-5 concerns G4.1's
# checkpoint basis and nothing else. Every other Step 4 gate stands on the closed runs, and
# producing a second set of G4.3 / G4.4 / G4.12 readings here would put two numbers for the
# same gate on the record with nothing to choose between them.
#
# Effective batch is held at 16 (2 x 8), the same as every other Step 4 run, because the
# whole value of this job is that its epoch-end readings are comparable with the closed
# fold's. Change nothing here that the closed run did not have.

set -x
FOLD=${1:?usage: sbatch 4thJ_step4_ds45_midepoch_fold.sh <es|uk|it>}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- D-S4-5 fold $FOLD not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_ds45
mkdir -p "$RUNDIR"

"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold "$FOLD" --leg 4 --run-type primary \
    --epochs 2 \
    --g41-midepoch \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 2 --grad-accum 8 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"

# G4.14's own check, printed at the end of every job in this project: the frozen
# pre-registration and its sidecar, both sides, so a run that quietly edited it cannot
# also quietly report a PASS.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
