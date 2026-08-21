#!/bin/bash
#SBATCH --job-name=4J_s5_rep
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step5_rep_%j.out

# Step 5, item 5.4 -- D-S5-13(a), RULED BY THE AUTHOR 2026-08-21.
#   usage: sbatch 4thJ_step5_temperature_replicates.sh <fold>     # es | uk | it
#
# WHAT THIS RUN IS FOR, AND WHAT IT MAY NOT DO
# ============================================
# `G5.8`'s registered sensitivity clause compares the STEP-TO-STEP difference
# along the temperature grid with the RE-RUN SPREAD at a fixed temperature. The
# primary sweep produced one realisation per grid point, so the spread term did
# not exist and the clause could not be evaluated (`FINDING 65`).
#
# 🔴 THIS RUN MEASURES THE SPREAD. IT DOES NOT CHOOSE A TEMPERATURE. The script
# refuses to recompute the choice in replicate mode; `T_chosen` stays exactly as
# the primary artefact recorded it (es 1.30, uk 1.10, it 1.20).
#
# THE WINDOW, PRE-REGISTERED HERE BEFORE THE RUN
# ==============================================
# D-S5-13(a): "a NARROW window of grid points around the chosen T (the argmin
# and its two neighbours)". Every point below is already on the pre-registered
# uniform grid -- no point is invented, and the grid is NOT extended.
#
#   es  T_chosen = 1.30  ->  1.10, 1.20, 1.30
#   uk  T_chosen = 1.10  ->  1.00, 1.10, 1.20
#   it  T_chosen = 1.20  ->  1.10, 1.20, 1.30
#
# 🔴 `es` is a GRID ENDPOINT, so it has no neighbour above. The window rule
# applied is stated rather than fudged: THREE points, the chosen one and the two
# nearest available on the grid. It is not extended past 1.30 -- the
# pre-registered rule forbids chasing an endpoint, and this run does not.
#
# WHY FIVE SEEDS AND NOT FOUR
# ===========================
# The decision text said "4 FURTHER replicates", on the reading that the primary
# realisation could serve as the fifth. 🔴 `FINDING 66` disqualifies it: the
# primary sweep never called `torch.manual_seed`, so its realisation carries no
# seed, cannot be reproduced, and cannot be labelled one of five. Five SEEDED
# passes are run instead. Cost is unchanged in practice -- the window is three
# points, not nine, and the high-T points are the fast ones.
#
# GENERATIONS ARE PERSISTED THIS TIME
# ===================================
# `--save-gen` writes one .jsonl per (T, seed). The first sweep discarded its
# text, which is why `at_home_mae_pp_covered` (D-S5-14) could not be re-derived
# for any of its 27 passes without a GPU. That does not happen twice.

set -x
FOLD=${1:?usage: sbatch 4thJ_step5_temperature_replicates.sh <es|uk|it>}

case "$FOLD" in
    es) WINDOW="1.10,1.20,1.30" ;;
    uk) WINDOW="1.00,1.10,1.20" ;;
    it) WINDOW="1.10,1.20,1.30" ;;
    *)  echo "unknown fold $FOLD"; exit 1 ;;
esac

SEEDS="101,102,103,104,105"

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
    echo "NO ADAPTER AT $ADAPTER -- D-S5-13 replicates cannot run for fold $FOLD."
    exit 1
fi

OUT=/speed-scratch/o_iseri/4J_step5
GENDIR=$OUT/generations_$FOLD
mkdir -p "$OUT"

"$ENVDIR/bin/python" -u 4thJ_step5_temperature.py \
    --fold "$FOLD" --adapter "$ADAPTER" --out "$OUT" \
    --gen-batch 8 --n-prompts 600 \
    --grid "$WINDOW" --gen-seeds "$SEEDS" \
    --save-gen "$GENDIR" --tag replicates

echo "--- artefact ---"
ls -l "$OUT"
md5sum "$OUT/temperature_calibration_${FOLD}_replicates.json"
ls -l "$GENDIR" | head -20
