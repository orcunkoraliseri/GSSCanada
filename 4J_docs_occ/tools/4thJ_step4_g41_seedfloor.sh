#!/bin/bash
#SBATCH --job-name=4J_s4_g41floor
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_g41floor_%j.out

# G4.1's SAMPLING-NOISE FLOOR -- the measurement Step 4 has been quoting resolutions
# without.
#   usage: sbatch 4thJ_step4_g41_seedfloor.sh <fold> [adapter_dir]   # fold = es | uk | it
#
# 🔴 WHY THIS IS OWED. FINDING 37 refused a G4.1 PASS at 0.61x "the spread". The D-S4-5
# entries refused both the FAIL and the PASS on fold `uk` against a spread of 0.131/0.391.
# Every one of those spreads came from a pair of TRAINING RUNS, which confounds the
# sampler's variance with the fact that two GPU training runs are not bit-identical. G4.6
# has a repeat-noise floor (0.000e+00). G4.1 has never had one, and it is the gate the
# whole D-S4-5 decision was about.
#
# 🔴 WHAT MAKES THIS THE RIGHT MEASUREMENT. It does NOT train. One adapter is loaded once
# and reused for every seed, so weight divergence is exactly zero by construction and the
# only thing left moving is model.generate's sampling. That is a LOWER BOUND on the
# run-to-run spread of two trained replicates -- quote it as a lower bound, never as "the"
# spread. This is the same correction already applied to G4.6's 3.81e-05.
#
# 🔴 IT PRODUCES NO VERDICT FOR ANY FOLD. Not a re-score, not a second G4.1 reading for
# the record. Its output is a RESOLUTION, to be printed beside G4.1 readings. The script
# writes `is_a_verdict_for_any_fold: false` into its own JSON so a later reader cannot
# mistake it for one.
#
# The seed set is fixed IN THE SOURCE (13,101,1009,7919,104729), written before any result
# existed, so it cannot be chosen to widen or narrow the spread. Overriding --seeds on a
# re-run is a basis change and must be declared as one.
#
# COST: generation only, ~600 diaries per seed x 5 seeds = the cost of five G4.1 probes.
# No training, no optimiser, no checkpoints. This is minutes-to-an-hour, not hours.
#
# 🔴 DO NOT SUBMIT THIS WHILE THE D-S4-5 CHAIN HOLDS THE GPU. It wants the same
# `nvidia_a100_2g.20gb` slice. Run `squeue -u $USER` first; if 1284912 or any successor is
# RUNNING, wait. FINDING 2 is about exactly this contention.

set -x
FOLD=${1:?usage: sbatch 4thJ_step4_g41_seedfloor.sh <es|uk|it> [adapter_dir]}
ADAPTER=${2:-/speed-scratch/o_iseri/4J_step4/runs_leg5/leg5_primary_fold_${FOLD}/adapter}

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

# 🔴 The adapter has to exist BEFORE the GPU is taken. A missing adapter dir would send
# PeftModel.from_pretrained down a path that can silently produce a base-model run, and a
# base-model sampling floor is not the quantity this job exists to measure.
if [ ! -d "$ADAPTER" ]; then
    echo "🔴 NO ADAPTER AT $ADAPTER -- refusing to run. A base-model floor is not G4.1's"
    echo "   floor. Pass the adapter dir explicitly as argument 2 if it lives elsewhere."
    exit 1
fi

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_g41_seedfloor.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- G4.1 seed floor not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

"$ENVDIR/bin/python" -u 4thJ_step4_g41_seedfloor.py \
    --fold "$FOLD" --leg 5 --run-type primary \
    --adapter "$ADAPTER" \
    --gen-n 600 --gen-stratified-k 6 --gen-batch 8 --max-len 1200 || exit 1

# G4.14's own check, printed at the end of every job in this project.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
