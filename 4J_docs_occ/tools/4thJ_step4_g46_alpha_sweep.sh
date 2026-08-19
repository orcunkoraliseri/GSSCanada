#!/bin/bash
#SBATCH --job-name=4J_s4_g46sweep
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_g46sweep_%j.out

# D-S4-3 -- the G4.6 alpha sweep. Reports a number, rules nothing.
#   usage: sbatch 4thJ_step4_g46_alpha_sweep.sh [adapter_dir]
#
# FINDING 9 / FINDING 2: named GRES, and ONE of our GPU jobs at a time. Do not submit
# this while a fold is training -- check `squeue -u $USER` first.
#
# WALLTIME. This asked for two hours on the argument that a short limit makes a hung job
# release the GPU by itself. That argument does not survive the standing rule: every job
# requests SEVEN DAYS unless the partition's MaxTime is lower, and `scontrol` reports
# MaxTime=7-00:00:00 on both `pg` and `ps`, so there is no lower cap to defer to. A hang is
# handled by `scancel`, which is a decision, not by a deadline that also truncates a slow
# but healthy run. Six forward-pass sweeps over 64 sequences still take minutes.

set -x
ADAPTER=${1:-/speed-scratch/o_iseri/4J_step4/runs_perturb/leg4_perturb_fold_es/adapter}
FOLD=${2:-es}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_g46_alpha_sweep.py 4thJ_step4_train.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- sweep not started"
    exit 1
fi

if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- the sweep has nothing to scale and is NOT run."
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

"$ENVDIR/bin/python" -u 4thJ_step4_g46_alpha_sweep.py \
    --fold "$FOLD" --adapter "$ADAPTER" \
    --out /speed-scratch/o_iseri/4J_step4/g46_alpha_sweep_$SLURM_JOB_ID.json
